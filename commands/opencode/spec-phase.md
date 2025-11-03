---
description: Create phase specification with agent workflow and human checkpoint
template: |
  # spec:phase

  Create phase specification with agent workflow and human checkpoint

  ## Usage

  ```
  /spec:phase
  ```

  ## Examples

  ```
  /spec:phase
  ```

  ## Implementation

  This command will:

  1. **List available strategy documents** with project names from `ai_docs/features/active/*/strategy.md`
  2. **Ask user to select** which strategy document to work with
  3. **Analyze selected strategy** to identify phases without existing phase documents
  4. **Ask user to select** which phase to create specification for
  5. **Create phase spec** at `ai_docs/features/active/{project-name}/phase-{number}.md`
  6. **Generate phase specification** with:
     - Phase header with goal and methodology from strategy
     - Legacy context and constraints template with TODO sections
     - Requirements and success criteria template
     - Agent workflow guidance for implementation

  After creation, use conversational workflow to complete the phase specification sections. 

  ### Conversational Workflow
  1. **Goal Definition** - What specific outcome this phase achieves
  2. **Legacy Context** - Existing patterns, constraints, and pragmatic rules  
  3. **Requirements** - Functional requirements and success criteria
  4. **Implementation Planning** - Approach and quality assurance strategy

  ### Supportive Agents (Optional)
  - **`[architect agent name]`** - Architectural guidance and technical approach review
  - **`[feature task architect agent name]`** - Task breakdown and Archon task creation
  - **`[code review agent name]`** - Code quality review during implementation  
  - **`[qa validator agent name]`** - Acceptance validation and testing

  ### Success Criteria for Command
  - All TODO sections completed with specific details
  - Legacy constraints properly addressed
  - Success criteria clearly defined and measurable
  - Implementation approach documented

  ## Output

  Creates `ai_docs/features/active/{project-name}/phase-{number}.md` with embedded phase specification template.

  ## Phase Specification Template

  The phase-{number}.md will be created with this embedded template:

  ```markdown
  # Phase {PHASE_NUMBER}: {PHASE_GOAL}

  *Phase specification for {PROJECT-NAME}*  
  **Created:** {DATE}  
  **Methodology:** Agent-Integrated Feature Specification with Human Architecture Checkpoint  
  **Tags:** #feature-{PROJECT-NAME} #phase-{PHASE_NUMBER} #status-planning #docs-phase-specification

  ## Goal
  {TODO: Clear, concise objective - what business/technical outcome this achieves}

  ## Legacy Context & Constraints

  - **Existing Patterns:** {TODO: Specific patterns/modules to reuse}
  - **Complexity Budget:** {TODO: Maximum new abstractions allowed}
  - **Performance Priority:** {TODO: Specific performance requirements}
  - **Compatibility Requirements:** {TODO: Backward compatibility constraints}
  - **Schema Reality:** {TODO: Work with existing schema constraints}
  - **Pragmatic Rules:** {TODO: Prefer proven patterns over elegant solutions}

  ## Requirements & Success Criteria

  **Functional Requirements:** {TODO: API contracts, security needs, specific behaviors}

  **Success Criteria:** {TODO: Measurable outcomes and acceptance criteria}

  ## Implementation Approach

  {TODO: Define implementation approach, testing strategy, and quality assurance}

  ## Quality Gates

  {TODO: Define review checkpoints and validation requirements}

  ---

  *This phase specification ensures systematic implementation with human oversight, agent coordination, and quality assurance throughout the development process.*
  ```
---