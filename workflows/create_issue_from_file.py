#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["python-dotenv", "pydantic>=2.0", "supabase>=2.0"]
# ///
"""Create a Cape issue from a description file."""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from supabase_client import create_issue
from utils import make_adw_id, setup_logger


def read_file_description(file_path: str) -> str:
    """Read issue description from file.

    Args:
        file_path: Path to file containing issue description.

    Returns:
        str: File contents with leading/trailing whitespace removed.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If path is not a regular file or file cannot be decoded as UTF-8.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {file_path}")

    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        return content.strip()

    except UnicodeDecodeError as e:
        raise ValueError(f"Failed to decode file {file_path} as UTF-8: {e}") from e


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with file_path attribute.
    """
    parser = argparse.ArgumentParser(
        description="Create a Cape issue from description file",
        epilog="""
Examples:
  uv run create_issue_from_file.py issue.txt
  uv run create_issue_from_file.py /tmp/feature_request.txt
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "file_path",
        type=str,
        help="Path to file containing issue description",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for create_issue_from_file script."""
    load_dotenv()

    args = parse_args()
    adw_id = make_adw_id()
    logger = setup_logger(adw_id, "create_issue_from_file")

    logger.info(f"ADW ID: {adw_id}")
    logger.info(f"Reading issue description from: {args.file_path}")

    try:
        description = read_file_description(args.file_path)
        logger.info(f"Description length: {len(description)} characters")

        issue = create_issue(description)
        logger.info(f"✅ Issue created with ID: {issue.id}")
        print(issue.id)

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
