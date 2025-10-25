#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "supabase"]
# ///
"""Manual validation script for ADW progress comments.

Usage:
    uv run workflows/validate_comments.py <issue-id>

Example:
    uv run workflows/validate_comments.py 123
"""

import sys
from dotenv import load_dotenv
from supabase_client import get_client


def validate_comments_exist(issue_id: int) -> bool:
    """Query database for comments on the specified issue.

    Args:
        issue_id: The Cape issue ID to query

    Returns:
        True if expected number of comments (4) exist, False otherwise
    """
    client = get_client()

    # Query comments for this issue
    response = (
        client.table("cape_comments")
        .select("*")
        .eq("issue_id", issue_id)
        .order("created_at")
        .execute()
    )

    comments = response.data
    comment_count = len(comments)

    print(f"\n=== Comments for Issue {issue_id} ===")
    print(f"Total comments found: {comment_count}")
    print(f"Expected comments: 4\n")

    if comment_count == 0:
        print("❌ No comments found for this issue")
        return False

    # Display all comments
    for i, comment in enumerate(comments, 1):
        print(f"{i}. ID={comment['id']}, Created={comment['created_at']}")
        print(f"   Text: {comment['comment']}\n")

    # Check if we have the expected count
    if comment_count == 4:
        print("✅ All expected comments present")
        return True
    else:
        print(f"⚠️  Expected 4 comments, found {comment_count}")
        return False


def main() -> None:
    """Main entry point for validation script."""
    if len(sys.argv) < 2:
        print("Usage: uv run workflows/validate_comments.py <issue-id>")
        print("Example: uv run workflows/validate_comments.py 123")
        sys.exit(1)

    try:
        issue_id = int(sys.argv[1])
    except ValueError:
        print(f"Error: issue-id must be an integer, got: {sys.argv[1]}")
        sys.exit(1)

    load_dotenv()

    try:
        success = validate_comments_exist(issue_id)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error querying comments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
