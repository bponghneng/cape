"""Tests for state_watcher module."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from cape_cli.state_watcher import StateWatcher


class TestStateWatcher:
    """Test StateWatcher class."""

    @pytest.fixture
    def temp_state_dir(self):
        """Create temporary state directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def watcher(self, temp_state_dir):
        """Create StateWatcher instance with temporary directory."""
        with patch('cape_cli.state_watcher.CapePaths.get_state_dir', return_value=temp_state_dir):
            with patch('cape_cli.state_watcher.CapePaths.ensure_directories'):
                watcher = StateWatcher()
                watcher.start()
                yield watcher
                watcher.stop()

    def test_watcher_starts_and_stops(self, temp_state_dir):
        """Test watcher lifecycle."""
        with patch('cape_cli.state_watcher.CapePaths.get_state_dir', return_value=temp_state_dir):
            with patch('cape_cli.state_watcher.CapePaths.ensure_directories'):
                watcher = StateWatcher()
                assert not watcher.is_running()

                watcher.start()
                assert watcher.is_running()

                watcher.stop()
                assert not watcher.is_running()

    def test_callback_triggered_on_file_change(self, watcher, temp_state_dir):
        """Test callback is triggered when state file is modified."""
        workflow_id = "test-workflow"
        callback_triggered = []

        def callback(wf_id):
            callback_triggered.append(wf_id)

        watcher.register_callback(workflow_id, callback)

        # Create and modify state file
        state_file = temp_state_dir / f"{workflow_id}.json"
        state_file.write_text('{"status": "running"}')

        # Wait for event to be processed
        time.sleep(0.5)

        # Modify file
        state_file.write_text('{"status": "completed"}')

        # Wait for event to be processed
        time.sleep(0.5)

        # Check callback was triggered
        assert workflow_id in callback_triggered

    def test_debouncing_prevents_duplicate_events(self, watcher, temp_state_dir):
        """Test debouncing prevents duplicate events from rapid changes."""
        workflow_id = "test-workflow"
        callback_count = []

        def callback(wf_id):
            callback_count.append(1)

        watcher.register_callback(workflow_id, callback)

        # Create state file
        state_file = temp_state_dir / f"{workflow_id}.json"

        # Rapidly modify file multiple times
        for i in range(5):
            state_file.write_text(f'{{"status": "running", "step": {i}}}')
            time.sleep(0.02)  # 20ms between writes (faster than debounce)

        # Wait for events to be processed
        time.sleep(0.5)

        # Should have fewer callbacks than modifications due to debouncing
        assert len(callback_count) < 5

    def test_unregister_callback(self, watcher, temp_state_dir):
        """Test unregistering a callback."""
        workflow_id = "test-workflow"
        callback_triggered = []

        def callback(wf_id):
            callback_triggered.append(wf_id)

        watcher.register_callback(workflow_id, callback)

        # Trigger event
        state_file = temp_state_dir / f"{workflow_id}.json"
        state_file.write_text('{"status": "running"}')
        time.sleep(0.5)

        # Unregister
        watcher.unregister_callback(workflow_id)
        callback_triggered.clear()

        # Trigger event again
        state_file.write_text('{"status": "completed"}')
        time.sleep(0.5)

        # Callback should not be triggered
        assert len(callback_triggered) == 0

    def test_callback_error_does_not_stop_observer(self, watcher, temp_state_dir):
        """Test that callback errors don't stop the observer."""
        workflow_id = "test-workflow"

        def bad_callback(wf_id):
            raise RuntimeError("Callback error")

        watcher.register_callback(workflow_id, bad_callback)

        # Modify file - should not crash observer
        state_file = temp_state_dir / f"{workflow_id}.json"
        state_file.write_text('{"status": "running"}')
        time.sleep(0.5)

        # Observer should still be running
        assert watcher.is_running()

    def test_context_manager(self, temp_state_dir):
        """Test using StateWatcher as context manager."""
        with patch('cape_cli.state_watcher.CapePaths.get_state_dir', return_value=temp_state_dir):
            with patch('cape_cli.state_watcher.CapePaths.ensure_directories'):
                with StateWatcher() as watcher:
                    assert watcher.is_running()

                # Should be stopped after context exit
                assert not watcher.is_running()

    def test_ignores_non_json_files(self, watcher, temp_state_dir):
        """Test that non-JSON files are ignored."""
        workflow_id = "test-workflow"
        callback_triggered = []

        def callback(wf_id):
            callback_triggered.append(wf_id)

        watcher.register_callback(workflow_id, callback)

        # Create non-JSON file
        txt_file = temp_state_dir / f"{workflow_id}.txt"
        txt_file.write_text('not json')
        time.sleep(0.5)

        # Callback should not be triggered
        assert len(callback_triggered) == 0

    def test_multiple_workflows(self, watcher, temp_state_dir):
        """Test monitoring multiple workflows."""
        workflow1 = "workflow-1"
        workflow2 = "workflow-2"
        callbacks = {workflow1: [], workflow2: []}

        def make_callback(wf_id):
            def callback(received_id):
                callbacks[wf_id].append(received_id)
            return callback

        watcher.register_callback(workflow1, make_callback(workflow1))
        watcher.register_callback(workflow2, make_callback(workflow2))

        # Modify both files
        (temp_state_dir / f"{workflow1}.json").write_text('{"status": "running"}')
        (temp_state_dir / f"{workflow2}.json").write_text('{"status": "completed"}')
        time.sleep(0.5)

        # Both callbacks should be triggered
        assert workflow1 in callbacks[workflow1]
        assert workflow2 in callbacks[workflow2]
