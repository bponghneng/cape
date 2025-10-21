#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["python-dotenv", "pydantic>=2.0", "supabase>=2.0"]
# ///
"""Create a Cape issue from a description string."""

import sys
import argparse
from dotenv import load_dotenv

from supabase_client import create_issue
from utils import make_adw_id, setup_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with description attribute.
    """
    parser = argparse.ArgumentParser(
        description="Create a Cape issue from description string",
        epilog="""
Examples:
  uv run create_issue_from_string.py "Fix login bug"
  uv run create_issue_from_string.py "Add user authentication feature"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "description",
        type=str,
        help="Issue description text",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for create_issue_from_string script."""
    load_dotenv()

    args = parse_args()
    adw_id = make_adw_id()
    logger = setup_logger(adw_id, "create_issue_from_string")

    logger.info(f"ADW ID: {adw_id}")
    logger.info("Creating issue from string description")

    try:
        issue = create_issue(args.description)
        logger.info(f"✅ Issue created with ID: {issue.id}")
        print(issue.id)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
