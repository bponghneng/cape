"""Workflow orchestration for adw_plan_build process."""

from typing import Optional, Tuple
from logging import Logger

from cape_cli.models import (
    AgentPromptResponse,
    AgentTemplateRequest,
    CapeIssue,
)
from cape_cli.agent import execute_template
from cape_cli.database import fetch_issue, create_comment

# Agent names
AGENT_IMPLEMENTOR = "sdlc_implementor"
AGENT_PLANNER = "sdlc_planner"
AGENT_CLASSIFIER = "issue_classifier"
AGENT_PLAN_FINDER = "plan_finder"


def insert_progress_comment(issue_id: int, comment_text: str, logger: Logger) -> None:
    """Insert a progress comment for the issue.

    This is a best-effort operation - database failures are logged but never halt
    workflow execution. Successful insertions are logged at DEBUG level, failures
    at ERROR level.

    Args:
        issue_id: The Cape issue ID
        comment_text: The comment text to insert
        logger: Logger instance for recording outcomes
    """
    try:
        comment = create_comment(issue_id, comment_text)
        logger.debug(f"Comment inserted: ID={comment.id}, Text='{comment_text}'")
    except Exception as e:
        logger.error(f"Failed to insert comment on issue {issue_id}: {e}")


def classify_issue(
    issue: CapeIssue, adw_id: str, logger: Logger
) -> Tuple[Optional[str], Optional[str]]:
    """Classify issue and return appropriate slash command.

    Returns:
        Tuple of (command, error_message) where one will be None
    """
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
    issue: CapeIssue, command: str, adw_id: str, logger: Logger
) -> AgentPromptResponse:
    """Build implementation plan for the issue using the specified command.

    Args:
        issue: The Cape issue to plan for
        command: The triage command to use (e.g., /triage:feature)
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        Agent response with plan output
    """
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
    plan_output: str, adw_id: str, logger: Logger
) -> Tuple[Optional[str], Optional[str]]:
    """Get the path to the plan file that was just created.

    Args:
        plan_output: The output from the build_plan step
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        Tuple of (file_path, error_message) where one will be None
    """
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
    plan_file: str, adw_id: str, logger: Logger
) -> AgentPromptResponse:
    """Implement the plan using the /implement command.

    Args:
        plan_file: Path to the plan file to implement
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        Agent response with implementation results
    """
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


def execute_workflow(issue_id: int, adw_id: str, logger: Logger) -> bool:
    """Execute complete workflow for an issue.

    This is the main orchestration function that runs all workflow steps:
    1. Fetch issue from database
    2. Classify the issue
    3. Build implementation plan
    4. Find plan file
    5. Implement the plan

    Progress comments are inserted at 4 key points (best-effort, non-blocking).

    Args:
        issue_id: The Cape issue ID to process
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        True if workflow completed successfully, False otherwise
    """
    logger.info(f"ADW ID: {adw_id}")
    logger.info(f"Processing issue ID: {issue_id}")

    # Fetch issue from Supabase
    logger.info("\n=== Fetching issue from Supabase ===")
    try:
        issue = fetch_issue(issue_id)
        logger.info(f"Issue fetched: ID={issue.id}, Status={issue.status}")
    except ValueError as e:
        logger.error(f"Error fetching issue: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error fetching issue: {e}")
        return False

    # Insert progress comment - best-effort, non-blocking
    insert_progress_comment(issue_id, "Workflow started - Issue fetched and validated", logger)

    # Classify the issue
    logger.info("\n=== Classifying issue ===")
    issue_command, error = classify_issue(issue, adw_id, logger)
    if error:
        logger.error(f"Error classifying issue: {error}")
        return False
    logger.info(f"Issue classified as: {issue_command}")

    # Insert progress comment - best-effort, non-blocking
    insert_progress_comment(issue_id, f"Issue classified as {issue_command}", logger)

    # Build the implementation plan
    logger.info("\n=== Building implementation plan ===")
    plan_response = build_plan(issue, issue_command, adw_id, logger)
    if not plan_response.success:
        logger.error(f"Error building plan: {plan_response.output}")
        return False
    logger.info(" Implementation plan created")

    # Insert progress comment - best-effort, non-blocking
    insert_progress_comment(issue_id, "Implementation plan created successfully", logger)

    # Get the path to the plan file that was created
    logger.info("\n=== Finding plan file ===")
    plan_file_path, error = get_plan_file(plan_response.output, adw_id, logger)
    if error:
        logger.error(f"Error finding plan file: {error}")
        return False
    logger.info(f"Plan file created: {plan_file_path}")

    # Implement the plan
    logger.info("\n=== Implementing solution ===")
    implement_response = implement_plan(plan_file_path, adw_id, logger)
    if not implement_response.success:
        logger.error(f"Error implementing solution: {implement_response.output}")
        return False
    logger.info(" Solution implemented")

    # Insert progress comment - best-effort, non-blocking
    insert_progress_comment(issue_id, "Solution implemented successfully", logger)

    logger.info("\n=== Workflow completed successfully ===")
    return True
