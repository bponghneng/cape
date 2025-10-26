"""Supabase client and helper functions for Cape issue workflow."""

import os
import logging
from typing import Optional, List
from functools import lru_cache

from supabase import create_client, Client
from postgrest.exceptions import APIError
from dotenv import load_dotenv

from cape_cli.models import CapeIssue, CapeComment

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================


class SupabaseConfig:
    """Configuration for Supabase connection."""

    def __init__(self):
        self.url: Optional[str] = os.environ.get("SUPABASE_URL")
        self.service_role_key: Optional[str] = os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY"
        )

    def validate(self) -> None:
        """Validate required environment variables are set."""
        missing = []

        if not self.url:
            missing.append("SUPABASE_URL")
        if not self.service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")

        if missing:
            raise ValueError(
                f"Missing required Supabase environment variables: "
                f"{', '.join(missing)}. "
                f"Please set these in your environment or .env file."
            )


# ============================================================================
# Client Singleton
# ============================================================================

_client: Optional[Client] = None


@lru_cache()
def get_client() -> Client:
    """Get or create the global Supabase client instance."""
    global _client

    if _client is None:
        config = SupabaseConfig()
        config.validate()

        _client = create_client(config.url, config.service_role_key)
        logger.info("Supabase client initialized")

    return _client


# ============================================================================
# Issue Operations
# ============================================================================


def fetch_issue(issue_id: int) -> CapeIssue:
    """Fetch issue from Supabase by ID."""
    client = get_client()

    try:
        response = (
            client.table("cape_issues")
            .select("*")
            .eq("id", issue_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            raise ValueError(f"Issue with id {issue_id} not found")

        return CapeIssue.from_supabase(response.data)

    except APIError as e:
        logger.error(f"Database error fetching issue {issue_id}: {e}")
        raise ValueError(f"Failed to fetch issue {issue_id}: {e}") from e


def fetch_all_issues() -> List[CapeIssue]:
    """Fetch all issues ordered by creation date (newest first).

    Returns:
        List of CapeIssue objects. Returns empty list if no issues exist.

    Raises:
        ValueError: If database operation fails.
    """
    client = get_client()

    try:
        response = (
            client.table("cape_issues")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            return []

        return [CapeIssue.from_supabase(row) for row in response.data]

    except APIError as e:
        logger.error(f"Database error fetching all issues: {e}")
        raise ValueError(f"Failed to fetch issues: {e}") from e


# ============================================================================
# Comment Operations
# ============================================================================


def create_comment(issue_id: int, text: str) -> CapeComment:
    """Create a comment on an issue."""
    client = get_client()

    comment_data = {
        "issue_id": issue_id,
        "comment": text.strip(),
    }

    try:
        response = (
            client.table("cape_comments").insert(comment_data).execute()
        )

        if not response.data:
            raise ValueError("Comment creation returned no data")

        return CapeComment(**response.data[0])

    except APIError as e:
        logger.error(f"Database error creating comment on issue {issue_id}: {e}")
        raise ValueError(
            f"Failed to create comment on issue {issue_id}: {e}"
        ) from e


def fetch_comments(issue_id: int) -> List[CapeComment]:
    """Fetch all comments for an issue in chronological order.

    Args:
        issue_id: The ID of the issue to fetch comments for.

    Returns:
        List of CapeComment objects. Returns empty list if no comments exist.

    Raises:
        ValueError: If database operation fails.
    """
    client = get_client()

    try:
        response = (
            client.table("cape_comments")
            .select("*")
            .eq("issue_id", issue_id)
            .order("created_at", desc=False)
            .execute()
        )

        if not response.data:
            return []

        return [CapeComment(**row) for row in response.data]

    except APIError as e:
        logger.error(f"Database error fetching comments for issue {issue_id}: {e}")
        raise ValueError(f"Failed to fetch comments for issue {issue_id}: {e}") from e


def create_issue(description: str) -> CapeIssue:
    """Create a new Cape issue with the given description.

    Args:
        description: The issue description text. Will be trimmed of leading/trailing whitespace.
                    Must not be empty after trimming.

    Returns:
        CapeIssue: The created issue with database-generated id and timestamps.

    Raises:
        ValueError: If description is empty after trimming, or if database operation fails.
    """
    description_clean = description.strip()

    if not description_clean:
        raise ValueError("Issue description cannot be empty")

    client = get_client()

    issue_data = {
        "description": description_clean,
        "status": "pending",
    }

    try:
        response = (
            client.table("cape_issues").insert(issue_data).execute()
        )

        if not response.data:
            raise ValueError("Issue creation returned no data")

        return CapeIssue(**response.data[0])

    except APIError as e:
        logger.error(f"Database error creating issue: {e}")
        raise ValueError(f"Failed to create issue: {e}") from e


def update_issue_status(issue_id: int, status: str) -> CapeIssue:
    """Update the status of an existing issue.

    Args:
        issue_id: The ID of the issue to update.
        status: The new status value. Must be one of: "pending", "started", "completed".

    Returns:
        CapeIssue: The updated issue with new status and updated timestamp.

    Raises:
        ValueError: If status is invalid, issue not found, or database operation fails.
    """
    valid_statuses = ["pending", "started", "completed"]
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
        )

    client = get_client()

    update_data = {
        "status": status,
    }

    try:
        response = (
            client.table("cape_issues")
            .update(update_data)
            .eq("id", issue_id)
            .execute()
        )

        if not response.data:
            raise ValueError(f"Issue with id {issue_id} not found")

        return CapeIssue(**response.data[0])

    except APIError as e:
        logger.error(f"Database error updating issue {issue_id} status: {e}")
        raise ValueError(f"Failed to update issue {issue_id} status: {e}") from e


def update_issue_description(issue_id: int, description: str) -> CapeIssue:
    """Update the description of an existing issue.

    Args:
        issue_id: The ID of the issue to update.
        description: The new description text. Will be trimmed of leading/trailing whitespace.
                    Must be between 10 and 10000 characters after trimming.

    Returns:
        CapeIssue: The updated issue with new description and updated timestamp.

    Raises:
        ValueError: If description is invalid, issue not found, or database operation fails.
    """
    description_clean = description.strip()

    if not description_clean:
        raise ValueError("Issue description cannot be empty")

    if len(description_clean) < 10:
        raise ValueError("Issue description must be at least 10 characters")

    if len(description_clean) > 10000:
        raise ValueError("Issue description cannot exceed 10000 characters")

    client = get_client()

    update_data = {
        "description": description_clean,
    }

    try:
        response = (
            client.table("cape_issues")
            .update(update_data)
            .eq("id", issue_id)
            .execute()
        )

        if not response.data:
            raise ValueError(f"Issue with id {issue_id} not found")

        return CapeIssue(**response.data[0])

    except APIError as e:
        logger.error(f"Database error updating issue {issue_id} description: {e}")
        raise ValueError(f"Failed to update issue {issue_id} description: {e}") from e


def delete_issue(issue_id: int) -> bool:
    """Delete an issue and its associated comments from the database.

    This operation will cascade delete all comments associated with the issue
    if the database foreign key constraint is configured with ON DELETE CASCADE.

    Args:
        issue_id: The ID of the issue to delete.

    Returns:
        bool: True if the issue was successfully deleted.

    Raises:
        ValueError: If issue not found or database operation fails.
    """
    client = get_client()

    try:
        response = (
            client.table("cape_issues")
            .delete()
            .eq("id", issue_id)
            .execute()
        )

        if not response.data:
            raise ValueError(f"Issue with id {issue_id} not found")

        logger.info(f"Successfully deleted issue {issue_id}")
        return True

    except APIError as e:
        logger.error(f"Database error deleting issue {issue_id}: {e}")
        raise ValueError(f"Failed to delete issue {issue_id}: {e}") from e
