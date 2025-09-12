# Agent Coordination Protocol

*Standards for coordinated execution of feature specifications using integrated agents with cohesive tagging and documentation*  

## Overview

Ensures agents maintain context across phases and handoffs with complete audit trail and quality gates.

## Document Naming Convention

### Structure
`[feature]-[phase]-[agent]-[document-type].md`

### Examples
- `work-item-1-phase-1_5-architect-decisions.md`
- `work-item-1-phase-1_5-tasks-breakdown.md`
- `work-item-1-phase-1_5-reviewer-report.md`
- `work-item-1-phase-1_5-validator-acceptance.md`

### Components

**feature:** Short feature name (e.g., work-item-1, user-profiles, chat-system)  
**phase:** Phase number (e.g., phase-1, phase-1_5)  
**agent:** Agent role identifier (architect, tasks, reviewer, validator)  
**document-type:** Output type (decisions, breakdown, report, acceptance)

## Universal Tagging System

### Required Tags (Every Document)
`#feature-[name] #phase-[number] #agent-[role] #status-[current] #timestamp-[YYYYMMDD-HHMM]`

### Workflow Status Tags
- `#status-planning` - Phase specification and preparation
- `#status-architecture` - Architectural review in progress  
- `#status-checkpoint` - Waiting for user architecture approval
- `#status-implementation` - Active development work
- `#status-review` - Code review in progress
- `#status-validation` - QA acceptance testing
- `#status-complete` - Phase fully completed

### Agent Role Tags
- `#agent-architect` - elixir-otp-architect outputs
- `#agent-task-planner` - feature-task-architect outputs  
- `#agent-reviewer` - elixir-code-reviewer outputs
- `#agent-validator` - elixir-qa-validator outputs
- `#agent-general` - General agent coordination

### Document Type Tags
- `#docs-architectural-decisions` - Technical approach and decisions
- `#docs-task-breakdown` - Archon task structure and criteria
- `#docs-quality-report` - Code review findings and assessment
- `#docs-acceptance-report` - QA validation and testing results
- `#docs-user-checkpoint` - User decision documentation
- `#docs-handoff` - Agent-to-agent context transfer

### Action Required Tags
- `#checkpoint-pending` - User architecture decision needed
- `#approval-required` - User approval needed to proceed
- `#quality-gate` - Code review PASS required
- `#validation-needed` - QA acceptance required
- `#blocked` - Cannot proceed due to external dependency

## Execution Phase Protocol

### Context Requirements
- Feature specification: `@ai_docs/[feature]-plan.md`
- Phase specification: `@ai_docs/[feature]-phase-[x].md`  
- Previous phase outcomes: `@ai_docs/[feature]-phase-[x-1]-*-*.md`
- Current Archon project: `[project_id]` | Tasks: `[task_status_summary]`
- Repository state: `[branch_name]` | Last commit: `[commit_hash]`

### Coordination Requirements
1. **Universal Tagging:** Apply full tag system to all documents and task updates
2. **Document Creation:** Generate `[agent]-[type].md` following naming convention
3. **Archon Integration:** Update task status and cross-reference documents
4. **Context Preservation:** Include coordination metadata in all outputs
5. **User Checkpoints:** Pause at architecture checkpoint for user decision
6. **Quality Gates:** Enforce code review PASS before proceeding to next phase
7. **Handoff Documentation:** Create explicit context transfer for next agent

### Expected Outputs
- Agent-specific documentation with full coordination metadata
- Archon task updates with current status and document references
- User checkpoint decision documentation (if applicable)  
- Handoff document preparing context for next workflow step
- Updated feature execution log with decision history

## Document Templates

### Architectural Decision Document Template

```markdown
# [Feature] Phase [X] - Architectural Decisions

## Coordination Metadata
**Feature:** [name] | **Phase:** [x] | **Agent:** architect | **Status:** [current]  
**Created:** [timestamp] | **Author:** elixir-otp-architect  
**Tags:** #feature-[name] #phase-[x] #agent-architect #docs-architectural-decisions #timestamp-[YYYYMMDD-HHMM]

**Previous Context:** [link to previous phase or relevant decisions]  
**Next Expected:** [feature]-[phase]-tasks-breakdown.md  
**Archon Tasks:** [links to related Archon tasks]  
**User Checkpoint Status:** [pending|approved|revised]

## Phase Context Review
**Phase Specification:** @ai_docs/[feature]-phase-[x].md  
**Legacy Constraints Applied:** [specific constraints that guided decisions]  
**Performance Requirements:** [requirements considered in approach]  
**Security Model:** [authorization patterns integrated]

## Technical Approach
[Detailed technical approach and architectural decisions]

## Key Architectural Decisions  
1. **[Decision Category]:** [Specific choice made]
   - **Rationale:** [Why this choice was made]
   - **Alternatives Considered:** [Other options evaluated]
   - **Trade-offs:** [Benefits and costs]

## Legacy System Integration
**Existing Patterns Reused:** [Specific modules/patterns leveraged]  
**New Abstractions:** [Any new patterns introduced and justification]  
**Complexity Assessment:** [Evaluation against phase complexity budget]

## User Checkpoint Decision
**Decision Required:** [Specific question for user]  
**Complexity Indicators:** [Signs this might be too complex]  
**Simplification Alternatives:** [Simpler approaches if user challenges]

**User Decision:** [Approved|Challenged|Refined] - [User feedback/constraints added]  

## Handoff to Task Planning
**Context for feature-task-architect:** [Key points for task breakdown]  
**Acceptance Criteria:** [How to validate successful implementation]  
**Resource References:** [Documentation, code examples, patterns to reference]
```

### Task Breakdown Document Template

```markdown  
# [Feature] Phase [X] - Task Breakdown

## Coordination Metadata
**Feature:** [name] | **Phase:** [x] | **Agent:** task-planner | **Status:** [current]  
**Created:** [timestamp] | **Author:** feature-task-architect  
**Tags:** #feature-[name] #phase-[x] #agent-task-planner #docs-task-breakdown #timestamp-[YYYYMMDD-HHMM]

**Input Context:** [feature]-[phase]-architect-decisions.md  
**Next Expected:** Implementation begins with first Archon task  
**Archon Project:** [project_id] | **Tasks Created:** [count]

## Archon Task Structure

### Task 1: [Task Title]
**Archon Task ID:** [task-id]  
**Status:** todo  
**Priority:** [high|medium|low]  

**Acceptance Criteria:**
- [ ] [Specific measurable outcome]
- [ ] [Next specific outcome]

**Implementation Guidance:**
- **Technical Approach:** [Specific implementation direction from architect]
- **Code Examples:** [References to existing patterns to follow]
- **Testing Requirements:** [Specific tests to write]

**Resources:**
- **Documentation:** [Links to relevant docs]
- **Code References:** [Existing code to reference or extend]

## Quality Assurance Integration
**Code Review Focus:** [Areas for elixir-code-reviewer to emphasize]  
**Testing Strategy:** [Overall testing approach across tasks]  
**Acceptance Validation:** [How elixir-qa-validator will verify completion]

## Handoff to Implementation
**First Task:** [Which task to start with and why]  
**Context Documents:** [All documents developer should reference]  
```

## Cross-Reference System

### Feature Execution Log Template
```markdown
# [Feature] Execution Log

**Feature:** [name] | **Status:** [current_phase]  
**Created:** [start_date] | **Last Updated:** [timestamp]  
**Tags:** #feature-[name] #execution-log #status-[current]

## Execution Timeline
- **[Date]** Phase [X] Started - [brief description]
- **[Date]** Architecture Review Completed - [architect decision status]  
- **[Date]** User Checkpoint - [user decision and any new constraints]
- **[Date]** Implementation [Status] - [progress summary]

## Phase Documentation Index
### Phase [X]: [Phase Name]
- **Specification:** @ai_docs/[feature]-phase-[x].md
- **Architectural Decisions:** @ai_docs/[feature]-phase-[x]-architect-decisions.md
- **Task Breakdown:** @ai_docs/[feature]-phase-[x]-tasks-breakdown.md  

## Current Status
**Active Phase:** [X] - [Phase Name]  
**Current Agent:** [agent handling current work]  
**Next Milestone:** [what needs to happen next]  
```

## Quality Assurance Workflow

### For Every Phase Execution

1. **Agent Output Creation**
   - Document created with full coordination metadata
   - All required tags applied consistently
   - Cross-references to previous context included
   - Archon task references updated

2. **Context Handoff Verification**  
   - Next agent has all required input documents
   - Dependencies clearly documented and available
   - Success criteria defined and measurable
   - Escalation path defined if issues arise

3. **Archon Integration Update**
   - Task status updated with document references
   - Progress notes include coordination metadata  
   - Dependencies and blockers clearly marked
   - Success criteria linked to acceptance testing

4. **User Checkpoint Management** (Architecture phases)
   - Checkpoint decision clearly documented
   - Any new constraints captured and propagated
   - Approval/revision/challenge responses recorded
   - Impact on subsequent phases assessed

5. **Quality Gate Enforcement**
   - Code review PASS required before next phase
   - QA acceptance required for phase completion
   - All quality findings addressed and verified
   - Documentation updated with final outcomes

6. **Feature Execution Log Update**
   - Timeline updated with phase completion
   - Key decisions recorded for future reference
   - Document index updated with new outputs
   - Status and next steps clearly documented

## Revision Communication Protocol

### Internal Documentation

**Strategy Document Updates:**
```markdown
## Strategy Revision Log

**[Date] - Revision [Number]: [Brief Title]**
- **Trigger:** [What caused the need for revision]
- **Changes Made:** [Specific strategy modifications]
- **Phase Impact:** [Which phases need modification]
- **Timeline Impact:** [Effect on overall delivery]
```

**Phase Specification Updates:**
```markdown
## Phase Revision History

**Revision [Number] - [Date]:**
- **Reason:** [Why revision was needed]
- **Changes:** [Specific modifications made]
- **Architectural Impact:** [Changes to technical approach]
```

### Stakeholder Communication

**For Strategy-Level Changes:**
- Update Plane work item with revised timeline/scope
- Communicate changes to dependent teams or features
- Revise business stakeholder expectations if necessary

**For Phase-Level Changes:**
- Internal team communication only unless timeline affected
- Update development team on revised approach
- Document lessons learned for future similar work

---

*This protocol ensures complete coordination and context preservation throughout complex multi-phase feature development using specialized agents.*