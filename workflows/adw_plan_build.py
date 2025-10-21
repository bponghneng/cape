#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "supabase"]
# ///
"""Task increment workflow driver."""

import sys
from typing import Optional, Tuple, Union

from dotenv import load_dotenv

from data_types import (
    AgentPromptResponse,
    AgentTemplateRequest,
    CapeIssue,
)
from agent import execute_template
from utils import make_adw_id, setup_logger
from supabase_client import fetch_issue

AGENT_IMPLEMENTOR = "sdlc_implementor"
AGENT_PLANNER = "sdlc_planner"
AGENT_CLASSIFIER = "issue_classifier"
AGENT_PLAN_FINDER = "plan_finder"


def parse_args(logger: Optional[object] = None) -> Tuple[int, Optional[str]]:
    """Parse command line arguments.

    Returns (issue_id, adw_id) where adw_id may be None."""
    if len(sys.argv) < 2:
        usage_msg = [
            "Usage: uv run adw_plan_build.py <issue-id> [adw-id]",
            "Example: uv run adw_plan_build.py 123",
            "Example: uv run adw_plan_build.py 123 abc12345",
        ]
        if logger:
            for msg in usage_msg:
                logger.error(msg)
        else:
            for msg in usage_msg:
                print(msg)
        sys.exit(1)

    try:
        issue_id = int(sys.argv[1])
    except ValueError:
        error_msg = f"Error: issue-id must be an integer, got: {sys.argv[1]}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        sys.exit(1)

    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    return issue_id, adw_id


def classify_issue(
    issue: CapeIssue, adw_id: str, logger: object
) -> Tuple[Optional[str], Optional[str]]:
    """Classify issue and return appropriate slash command.
    Returns (command, error_message) tuple."""
    request = AgentTemplateRequest(
        agent_name=AGENT_CLASSIFIER,
        slash_command="/triage:classify",
        args=[issue.description],
        adw_id=adw_id,
        model="sonnet",
    )
    logger.debug(
        "classify request: %s",
        request.model_dump_json(indent=2, by_alias=True),
    )
    response = execute_template(request)
    logger.debug(
        "classify response: %s",
        response.model_dump_json(indent=2, by_alias=True),
    )

    if not response.success:
        return None, response.output

    issue_command = response.output.strip()

    if issue_command == "0":
        return None, f"No command selected: {response.output}"

    if issue_command not in ["/chore", "/bug", "/feature"]:
        return None, f"Invalid command selected: {response.output}"

    # Convert to triage: prefixed command
    issue_command = f"/triage:{issue_command.lstrip('/')}"

    return issue_command, None


def build_plan(
    issue: CapeIssue, command: str, adw_id: str, logger: object
) -> AgentPromptResponse:
    """Build implementation plan for the issue using the specified command."""
    request = AgentTemplateRequest(
        agent_name=AGENT_PLANNER,
        slash_command=command,
        args=[issue.description],
        adw_id=adw_id,
        model="sonnet",
    )
    logger.debug(
        "build_plan request: %s",
        request.model_dump_json(indent=2, by_alias=True),
    )
    response = execute_template(request)
    logger.debug(
        "build_plan response: %s",
        response.model_dump_json(indent=2, by_alias=True),
    )
    return response


def get_plan_file(
    plan_output: str, adw_id: str, logger: object
) -> Tuple[Optional[str], Optional[str]]:
    """Get the path to the plan file that was just created.
    Returns (file_path, error_message) tuple."""
    request = AgentTemplateRequest(
        agent_name=AGENT_PLAN_FINDER,
        slash_command="/triage:find-plan-file",
        args=[plan_output],
        adw_id=adw_id,
        model="sonnet",
    )
    logger.debug(
        "get_plan_file request: %s",
        request.model_dump_json(indent=2, by_alias=True),
    )
    response = execute_template(request)
    logger.debug(
        "get_plan_file response: %s",
        response.model_dump_json(indent=2, by_alias=True),
    )

    if not response.success:
        return None, response.output

    # Clean up the response - get just the file path
    file_path = response.output.strip()

    # Validate it looks like a file path
    if file_path and file_path != "0" and "/" in file_path:
        return file_path, None
    elif file_path == "0":
        return None, "No plan file found in output"
    else:
        # If response doesn't look like a path, return error
        return None, f"Invalid file path response: {file_path}"


def implement_plan(
    plan_file: str, adw_id: str, logger: object
) -> AgentPromptResponse:
    """Implement the plan using the /implement command."""
    request = AgentTemplateRequest(
        agent_name=AGENT_IMPLEMENTOR,
        slash_command="/implement",
        args=[plan_file],
        adw_id=adw_id,
        model="sonnet",
    )
    logger.debug(
        "implement request: %s",
        request.model_dump_json(indent=2, by_alias=True),
    )
    response = execute_template(request)
    logger.debug(
        "implement response: %s",
        response.model_dump_json(indent=2, by_alias=True),
    )
    return response


def check_error(
    error_or_response: Union[Optional[str], AgentPromptResponse],
    logger: object,
    error_prefix: str,
) -> None:
    error: Optional[str] = None
    if isinstance(error_or_response, AgentPromptResponse):
        if not error_or_response.success:
            error = error_or_response.output
    else:
        error = error_or_response
    if error:
        logger.error(f"{error_prefix}: {error}")
        sys.exit(1)


def main() -> None:
    load_dotenv()

    issue_id, adw_id = parse_args()
    if not adw_id:
        adw_id = make_adw_id()

    logger = setup_logger(adw_id, "adw_plan_build")
    logger.info(f"ADW ID: {adw_id}")
    logger.info(f"Processing issue ID: {issue_id}")

    # Fetch issue from Supabase
    logger.info("\n=== Fetching issue from Supabase ===")
    try:
        issue = fetch_issue(issue_id)
        logger.info(f"Issue fetched: ID={issue.id}, Status={issue.status}")
    except ValueError as e:
        logger.error(f"Error fetching issue: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error fetching issue: {e}")
        sys.exit(1)

    # Classify the issue
    logger.info("\n=== Classifying issue ===")
    issue_command, error = classify_issue(issue, adw_id, logger)
    check_error(error, logger, "Error classifying issue")
    logger.info(f"Issue classified as: {issue_command}")

    # Build the implementation plan
    logger.info("\n=== Building implementation plan ===")
    plan_response = build_plan(issue, issue_command, adw_id, logger)
    check_error(plan_response, logger, "Error building plan")
    logger.info("✅ Implementation plan created")

    # Get the path to the plan file that was created
    logger.info("\n=== Finding plan file ===")
    plan_file_path, error = get_plan_file(plan_response.output, adw_id, logger)
    check_error(error, logger, "Error finding plan file")
    logger.info(f"Plan file created: {plan_file_path}")

    # Implement the plan
    logger.info("\n=== Implementing solution ===")
    implement_response = implement_plan(plan_file_path, adw_id, logger)
    check_error(implement_response, logger, "Error implementing solution")
    logger.info("✅ Solution implemented")

    logger.info("\n=== Workflow completed successfully ===")


if __name__ == "__main__":
    main()
