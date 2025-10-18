---
description: Execute phase implementation using integrated agents workflow with human architecture checkpoints
template: |
  # spec:execute

  Execute phase implementation using integrated agents workflow with human architecture checkpoints

  ## Usage

  ```
  /spec:execute <feature> <phase>
  ```

  ## Examples

  ```
  /spec:execute work-item-1 phase-1
  /spec:execute work-item-2 phase-2
  ```

  ## Implementation

  This command orchestrates the complete integrated agents workflow for a specific phase:

  ### 1. Simple Context Check

  ```
  Verify required files exist and are not empty:
  - Strategy: `ai_docs/features/active/{feature}/strategy.md`
  - Phase Spec: `ai_docs/features/active/{feature}/{phase}.md`

  If missing → Exit with error: "Run /spec:strategy first" or "Create phase spec"
  If present → Proceed to execution
  ```

  ### 2. Agent Execution

  **[architect agent name]:**
  ```
  Execute architectural review for {FEATURE} {PHASE}.

  Context Files:
  - Strategic Plan: @ai_docs/features/active/{feature}/strategy.md
  - Phase Specification: @ai_docs/features/active/{feature}/{phase}.md

  Create complete architectural decisions document content including:
  - Technical approach and key architectural decisions
  - User checkpoint with decision options (Approve/Challenge/Refine)
  - Legacy system integration analysis
  - Handoff context for task planning

  SIMPLE OUTPUT FORMAT (JSON):
  {
    "status": "pass|fail|partial",
    "confidence": "high|medium|low",
    "content": "Complete architectural decisions document as markdown",
    "issues": ["List any problems or concerns"]
  }

  If you cannot complete the analysis → status: "fail" and explain in issues
  If context is unclear → status: "partial" and list gaps in issues
  ```

  **User Architecture Checkpoint:**
  ```
  Review architectural decisions and choose: Approve / Challenge / Refine
  Decision will be recorded in architect decisions file.
  ```

  **[feature task architect agent name]:**
  ```
  Create task breakdown for {FEATURE} {PHASE}.

  Context Files:
  - Architectural Context: ai_docs/features/active/{feature}/{feature}-{phase}-architect-decisions.md
  - Phase Specification: @ai_docs/features/active/{feature}/{phase}.md
  - Strategic Plan: @ai_docs/features/active/{feature}/strategy.md

  Create complete task breakdown document including:
  - Archon tasks with clear acceptance criteria
  - Implementation guidance and resource references
  - Quality assurance integration approach
  - Implementation handoff instructions

  SIMPLE OUTPUT FORMAT (JSON):
  {
    "status": "pass|fail|partial", 
    "confidence": "high|medium|low",
    "content": ["List of task titles created in Archon"],
    "issues": ["List any problems or concerns"]
  }

  If task breakdown cannot be completed → status: "fail" and explain in issues
  ```

  **[implementation agent name]:**
  ```
  Create Archon tasks per task breakdown document.
  Execute Archon tasks.
  Update Archon task status throughout implementation.
  ```

  **Quality Assurance (Parallel):**

  **[code review agent name]:**
  ```
  Review code changes for {FEATURE} {PHASE}.

  Context Files:
  - Task breakdown, architectural decisions, and phase specification

  Create complete code review report including:
  - PASS/FAIL assessment with reasoning
  - Code quality, security, and performance analysis
  - Architectural compliance evaluation
  - Testing coverage assessment
  - Specific findings and recommendations

  SIMPLE OUTPUT FORMAT (JSON):
  {
    "status": "pass|fail|partial",
    "confidence": "high|medium|low", 
    "content": "Complete code review report as markdown",
    "issues": ["List any problems or concerns"]
  }

  If code cannot be reviewed → status: "fail" and explain in issues
  If critical issues found → status: "fail" with detailed findings
  ```

  **[qa validator agent name] (parallel):**
  ```
  Validate {FEATURE} {PHASE} completion.

  Context Files:
  - Task breakdown, architectural decisions, and phase specification

  Create complete validation report including:
  - Acceptance criteria verification results
  - Archon task completion assessment  
  - Testing results and coverage analysis
  - Final phase completion assessment

  SIMPLE OUTPUT FORMAT (JSON):
  {
    "status": "pass|fail|partial",
    "confidence": "high|medium|low",
    "content": "Complete validation report as markdown", 
    "issues": ["List any problems or concerns"]
  }

  Mark Archon tasks as "done" after successful validation.
  If validation fails → status: "fail" with blocking issues listed
  If phase incomplete → status: "partial" with remaining work described

  Note: Runs in parallel with code reviewer. Both must complete successfully.
  ```

  ### 3. File Creation

  ```
  For each agent JSON output:

  1. Check status is not "fail" (if fail → escalate with agent issues)
  2. Extract content from JSON
  3. Create appropriately named files:
     - `{feature}-{phase}-architect-decisions.md` 
     - `{feature}-{phase}-tasks-breakdown.md`
     - `{feature}-{phase}-reviewer-report.md` 
     - `{feature}-{phase}-validator-acceptance.md`

  4. Add basic tags:
     - #feature-{feature} #phase-{phase} #agent-{agent} #timestamp-{YYYYMMDD-HHMM}

  Simple file creation with consistent naming and minimal tagging.
  ```

  ### 4. Completion

  Phase execution complete with all documents created.

  ## Output

  Creates agent coordination documents:
  - `{feature}-{phase}-architect-decisions.md` - Technical approach and user checkpoint
  - `{feature}-{phase}-tasks-breakdown.md` - Archon tasks with acceptance criteria  
  - `{feature}-{phase}-reviewer-report.md` - Code quality assessment with PASS/FAIL
  - `{feature}-{phase}-validator-acceptance.md` - Feature completion validation

  ## Workflow Integration

  Streamlined workflow with:
  - Consistent document naming and tagging
  - Human architecture checkpoints to prevent over-engineering
  - Quality gates requiring code review PASS before proceeding
  - Complete audit trail through document handoffs
  - Archon integration for task management throughout execution
---