"""Supabase client and helper functions for Cape issue workflow."""

import os
import logging
from typing import Optional, List
from functools import lru_cache

from supabase import create_client, Client
from postgrest.exceptions import APIError
from dotenv import load_dotenv

from data_types import CapeIssue, CapeComment

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
