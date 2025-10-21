# Feature Request: Supabase-Sourced Cape Issue Workflow

## Objective
- Refactor `adw_plan_build` so `main` loads Cape issues from Supabase, passing a strongly typed `CapeIssue` through the workflow instead of relying on local markdown files.
- Introduce a Supabase helper capable of fetching issues and posting comments to support future workflow automation.

## High Level Tasks
- Update CLI argument parsing and logging to work with Supabase-backed issue IDs.
- Implement Supabase connectivity with `supabase-py`, including environment configuration.
- Define new Pydantic data models (`CapeIssue`, `CapeComment`) and integrate them into the workflow.
- Rewrite workflow functions to operate on `CapeIssue` instances instead of file paths.
- Add a basic comment creation API for future status updates.

## Technical Constraints
- **Data requirements**: `CapeIssue` must capture `id`, `description`, and `status` (default `pending`, limited to `pending|started|completed`). Include optional `created_at`/`updated_at` timestamps parsed from Supabase but unused initially. `CapeComment` stores `id`, `issue_id`, `comment`, and optional timestamps for write operations. Supabase schema:  
  - `cape_issues(id SERIAL PRIMARY KEY, description TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now())`  
  - `cape_comments(id SERIAL PRIMARY KEY, issue_id INT NOT NULL REFERENCES cape_issues(id), comment TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now())`
- **Supabase access**: Use `supabase-py`; embed a helper module at `workflows/supabase.py` exposing `fetch_issue(issue_id: int) -> CapeIssue` and `create_comment(issue_id: int, text: str) -> CapeComment`. Load `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (documented in `.env` templates) after `load_dotenv()`.
- **CapeIssue model**: Add Pydantic types in `workflows/data_types.py` with validation that trims text, enforces status literals, and defaults missing status to `pending`. Provide `CapeIssue.from_supabase(row: dict)` factory. Defer comment parsing until reads are needed.
- **Workflow refactor**: Update `classify_issue`, `build_plan`, and related helpers to accept `CapeIssue` instead of a file path, removing filesystem reads. Log using issue ID/status. Keep plan/implement functions ready for future context, passing `issue` if needed.
- **CLI flow & fallback**: Change usage to `uv run workflows/adw_plan_build.py <issue-id> [adw-id]`. Optionally allow a temporary `--issue-path` fallback, but default path must be Supabase. Ensure clear error handling for missing env vars or issue records. Comments are not fetched during workflow; the helper’s comment API remains unused until automation requires it.

## Acceptance Criteria
- `main` fetches a `CapeIssue` from Supabase using an integer issue ID and drives the workflow without reading local files.
- New data models and Supabase helper handle validation, defaults, and environment loading as specified.
- Command-line usage and logging reflect issue IDs and statuses; file-based usage is deprecated with no CLI flag for legacy support.
- Unit/integration coverage:
  - Tests for `main` (or a refactored orchestrator) verifying Supabase fetch integration, argument parsing, and error pathways.
  - Tests for `CapeIssue` (status defaulting, value trimming, timestamp parsing).
  - Tests for Supabase helper functions (mocked client verifying query shapes and env var handling).
- Documentation updates include environment variable expectations and revised workflow invocation instructions.
- Supabase migration scripts (SQL or `supabase` CLI) exist to create `cape_issues` and `cape_comments` with the specified schema.
