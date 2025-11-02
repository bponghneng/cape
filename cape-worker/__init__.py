"""Cape Worker Package

This package provides the issue worker functionality for the Cape system.
"""

from .worker import IssueWorker
from .database import get_client, get_next_issue, update_issue_status
from .config import WorkerConfig
from .cli import main

__all__ = [
    'IssueWorker',
    'get_client',
    'get_next_issue',
    'update_issue_status',
    'WorkerConfig',
    'main'
]
