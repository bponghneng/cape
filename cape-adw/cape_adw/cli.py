"""CLI interface for CAPE ADW."""

import sys
import typer
from cape_adw.adw import execute_adw_workflow

app = typer.Typer(help="CAPE ADW - Agent Development Workflow", invoke_without_command=True)


@app.callback()
def main(
    ctx: typer.Context,
    issue_id: str = typer.Argument(None, help="The ID of the issue to process"),
    description: str = typer.Argument(None, help="The description of the issue")
):
    """
    CAPE ADW - Agent Development Workflow
    
    Execute the Agent Development Workflow for a given issue.
    """
    if issue_id is None or description is None:
        typer.echo("Usage: cape-adw <issue_id> <description>")
        typer.echo("Use 'cape-adw --help' for more information")
        raise typer.Exit()
    
    try:
        result = execute_adw_workflow(issue_id, description)
        typer.echo(result)
        sys.exit(0)
    except Exception as e:
        typer.echo(f"Error executing ADW workflow: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
