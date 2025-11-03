---
argument-hint: "[project-name] [work-description...]"
description: Create strategic plan document with template and checklist
allowed-tools: Write, Read
template: |
  ## Usage

  ```bash
  /spec:strategy user-authentication "Implement OAuth 2.0 user authentication"
  /spec:strategy payment-flow "Add Stripe payment integration"
  ```

  ## Arguments

  - `project-name`: Kebab-case project identifier (e.g., user-auth, payment-flow)
  - `work-description`: Brief description of the work (rest of arguments)

  ## Implementation

  1. **Parse arguments**: Extract project name and work description from `$ARGUMENTS`
  2. **Prompt if missing**: If no arguments provided, ask user for:
     - Project name (kebab-case)
     - Work description (brief summary)
  3. **Generate strategy.md** in `ai_docs/` directory with:
     - Work item details from user input
     - Strategic plan template with TODO sections
     - Completion checklist at the top

  After creation, use conversational workflow to complete the strategic plan sections.

  ## Output

  Creates `ai_docs/strategy-{project-name}.md` with embedded strategic plan template.

  ## Your Task

  1. **Extract or prompt for inputs**:
     - If `$ARGUMENTS` is provided, parse it as: `project-name work-description...`
     - If `$ARGUMENTS` is empty, prompt the user:
       ```
       Please provide:
       1. Project name (kebab-case, e.g., user-authentication)
       2. Work description (brief summary of the work)
       ```
     - Wait for user response before proceeding

  2. **Generate the strategy document**:
     - Use the template below
     - Replace `{PROJECT-NAME}` with the project name
     - Replace `{PROJECT-DESCRIPTION}` with the work description
     - Replace `{DATE}` with current date in YYYY-MM-DD format
     - Create file at `ai_docs/strategy-{project-name}.md`

  3. **Confirm creation**:
     - Display the file path
     - Show a brief summary of next steps

  ## Strategic Plan Template

  Create the strategy document with this template:

  ```markdown
  # Strategic Plan: {PROJECT-NAME}

  *Strategic plan for {PROJECT-DESCRIPTION}*  
  *Created: {DATE}*

  ## ✅ Completion Checklist

  - [ ] **Work Item Context** - Business context and requirements
  - [ ] **Core Challenge** - Fundamental problem definition  
  - [ ] **Success Definition** - Objectives and acceptance criteria
  - [ ] **Technical Context** - Current system state and dependencies
  - [ ] **Strategic Phases** - High-level implementation approach
  - [ ] **Architecture Principles** - Technical guidance for phases

  ---

  ## Work Item Context

  **Project Name:** {PROJECT-NAME}  
  **Priority:** {TODO: Set priority} | **Assignee:** {TODO: Set assignee}  
  **Target Date:** {TODO: Set target date} | **Epic/Category:** {TODO: Set category}

  **Original Description:**
  > {PROJECT-DESCRIPTION}

  **Business Context:**  
  {TODO: Why this work matters - business value, user impact, strategic importance}

  ## Strategic Analysis

  #### Core Challenge
  {TODO: What is the fundamental problem we're solving? Why is it complex?}

  #### Success Definition

  **Primary Objectives:**
  - [ ] {TODO: Measurable outcome 1}
  - [ ] {TODO: Measurable outcome 2}  
  - [ ] {TODO: Measurable outcome 3}

  **Acceptance Criteria:**
  - [ ] {TODO: Specific, testable criteria}
  - [ ] {TODO: Next criteria}
  - [ ] {TODO: Final criteria}

  **Non-Goals (Explicitly Out of Scope):**
  - {TODO: What we're NOT doing in this iteration}
  - {TODO: Deferred features or optimizations}

  #### Technical Context

  **Existing System State:**
  {TODO: Current architecture, legacy patterns, performance constraints, security considerations}

  **Key Dependencies:**
  {TODO: External systems, database changes, other work items}

  **Risk Assessment:**
  - **High Risk:** {TODO: Major technical or business risks}
  - **Medium Risk:** {TODO: Moderate risks with mitigation strategies}  
  - **Low Risk:** {TODO: Minor risks to monitor}

  ## Implementation Approach

  #### Strategic Phases

  **Phase 1: {TODO: Foundation/Preparation}**
  - **Goal:** {TODO: What this phase establishes}
  - **Key Deliverables:** {TODO: Major outputs}
  - **Success Criteria:** {TODO: How we know it worked}

  **Phase 2: {TODO: Core Implementation}**  
  - **Goal:** {TODO: Primary work objective}
  - **Key Deliverables:** {TODO: Major outputs}
  - **Success Criteria:** {TODO: Measurable outcomes}

  **Phase 3: {TODO: Integration/Completion}**
  - **Goal:** {TODO: Final integration and validation}
  - **Key Deliverables:** {TODO: Final outputs}
  - **Success Criteria:** {TODO: Final acceptance criteria}

  #### Architecture Principles
  - **Backward Compatibility:** {TODO: Specific compatibility requirements}
  - **Performance:** {TODO: Performance goals and constraints}
  - **Security:** {TODO: Security model and requirements}
  - **Maintainability:** {TODO: Code quality and pattern requirements}

  #### Quality Assurance Strategy
  - **Testing Approach:** {TODO: Overall testing strategy}
  - **Review Process:** {TODO: Code review and validation approach}
  - **Rollback Plan:** {TODO: How to revert if things go wrong}

  ## Current Status

  **Active Phase:** Planning (Strategic Plan Creation)  
  **Created:** {DATE}  
  **Next Milestone:** Complete strategic plan sections  
  **Blockers:** None currently

  **Strategy Confidence:** [To be determined]
  - High: Well-understood problem, clear approach
  - Medium: Some unknowns, likely good approach  
  - Low: Significant unknowns, experimental approach

  ## Decision Log

  <!-- Decisions will be added as strategic planning progresses -->

  ---

  *This strategic plan will guide the detailed phase implementation for {PROJECT-NAME}. Complete the TODO sections using conversational workflow as outlined in the strategic plan user guide.*
  ```
---