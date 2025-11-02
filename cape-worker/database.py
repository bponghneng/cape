"""Database operations for the Cape Worker."""

import sys
from pathlib import Path
from typing import Optional, Tuple
import logging

# Add cape-cli to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent / "cape-cli" / "src"))

from cape_cli.database import get_client as _get_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_client():
    """Get a Supabase client instance.

    Returns:
        Supabase client configured with environment credentials
    """
    return _get_client()


def get_next_issue(worker_id: str, logger: Optional[logging.Logger] = None) -> Optional[Tuple[int, str]]:
    """
    Retrieve and lock the next pending issue from the database.

    Uses the PostgreSQL function get_and_lock_next_issue to atomically
    retrieve and lock an issue, preventing race conditions.

    Args:
        worker_id: Unique identifier for the worker requesting the issue
        logger: Optional logger for logging operations

    Returns:
        Tuple of (issue_id, description) if an issue is available, None otherwise
    """
    try:
        client = get_client()

        # Call the PostgreSQL function to get and lock the next issue
        response = client.rpc(
            "get_and_lock_next_issue",
            {"p_worker_id": worker_id}
        ).execute()

        if response.data and len(response.data) > 0:
            issue = response.data[0]
            issue_id = issue["id"]
            description = issue["description"]
            if logger:
                logger.info(f"Locked issue {issue_id} for processing")
            return (issue_id, description)

        return None

    except Exception as e:
        if logger:
            logger.error(f"Error retrieving next issue: {e}")
        return None


def update_issue_status(issue_id: int, status: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Update the status of an issue in the database.

    Args:
        issue_id: The ID of the issue to update
        status: The new status ('pending', 'started', or 'completed')
        logger: Optional logger for logging operations
    """
    try:
        client = get_client()

        client.table("cape_issues").update(
            {"status": status}
        ).eq("id", issue_id).execute()

        if logger:
            logger.debug(f"Updated issue {issue_id} status to {status}")

    except Exception as e:
        if logger:
            logger.error(f"Error updating issue {issue_id} status: {e}")
