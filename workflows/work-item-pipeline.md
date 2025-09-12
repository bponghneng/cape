# Work Item Pipeline

*Complete workflow for moving from work items through strategic planning to detailed phase implementation*  

## Overview

Three-stage process that bridges high-level work items with technical implementation through strategic planning, agent coordination, and human checkpoints.

## Stage 1: Strategic Planning (Work Item → Intermediate Strategy)

### Input
Work item with basic description, priority, and scope

### Process

#### Context Gathering
- Read work item details
- Research existing codebase patterns related to work using search tools
- Identify technical dependencies and constraints
- Assess business impact and user value

#### Strategic Discussion (Human + General Agent)
- Analyze core challenges and complexity risks
- Define success criteria and acceptance boundaries  
- Identify non-goals and scope boundaries
- Assess technical approach options and trade-offs
- Determine high-level phase strategy

#### Strategy Document Creation
- Use Strategic Plan Template
- Capture strategic thinking and decision rationale
- Define phase-level objectives and success criteria
- Document architecture principles and quality requirements
- Set up framework for phase-by-phase implementation

### Output
Feature Implementation Strategy document with objectives, phase breakdown, principles, and risk assessment

---

## Stage 2: Iterative Phase Implementation

### Phase Planning Cycle

#### Pre-Phase Review
**Trigger:** Ready to start next phase  
**Participants:** User + General Agent

**Process:**
1. Review current strategy document for context
2. Assess outcomes and lessons from previous phase (if applicable)  
3. Identify any needed strategy adjustments
4. Confirm next phase objectives align with strategic goals

**Review Questions:**
- Does the next phase objective still align with overall strategy?
- Have previous phase outcomes changed our understanding of the problem?
- Do we need to adjust complexity budgets or technical approach?
- Are there new risks or dependencies to consider?

**Outputs:**
- Go/No-Go decision for phase as originally planned
- Strategy document updates (if needed)
- Modified phase objectives or scope (if needed)

#### Phase Specification Creation
**Input:** Strategy document + previous phase outcomes

**Process:**
1. Use Phase Spec Template
2. Apply strategic guidance and constraints from strategy document
3. Incorporate lessons learned from previous phases
4. Define specific legacy constraints and complexity budgets
5. Create detailed phase specification ready for agent execution

**Template Structure:**
```markdown
## Phase X: [Goal Statement]
### Goal, Legacy Context & Constraints, Requirements
### 1. Architectural Review (elixir-otp-architect)
### 2. User Architecture Checkpoint ← HUMAN CONTROL POINT
### 3. Task Planning (feature-task-architect)
### 4. User Feature Task Checkpoint ← HUMAN CONTROL POINT
### 5. Implementation (General Agent)
### 6. Quality Review (elixir-code-reviewer)
### 7. Acceptance Validation (elixir-qa-validator)
```

#### Phase Execution
**Process:** Follow Agent-Integrated Methodology with Human Checkpoints

1. **Architectural Review** (architect agent)
   - Input: Phase requirements + legacy constraints
   - Output: Technical approach document
   - Tags: #agent-architect #phase-X #docs-architectural-decisions

2. **Human Architecture Checkpoint** ← **HUMAN CONTROL POINT**
   - User Options: Approve / Challenge / Refine / Document
   - Prevents over-engineering before implementation
   - Decision required before proceeding

3. **Task Planning** (feature task architect)
   - Input: Approved architectural approach
   - Output: Archon tasks with acceptance criteria
   - Tags: #agent-task-planner #phase-X #docs-task-breakdown

4. **Human Feature Task Checkpoint** ← **HUMAN CONTROL POINT**
   - User Options: Approve / Refine
   - Validates task breakdown and acceptance criteria
   - Decision required before proceeding to implementation

5. **Implementation** (engineer agent)
   - Execute Archon tasks following architectural guidance
   - Update task status throughout implementation
   - Tags: #phase-X #status-implementation

6. **Quality Review** (code review agent)
   - Focus: Code quality, security, patterns, performance
   - Output: PASS/FAIL assessment
   - Tags: #agent-reviewer #phase-X #quality-gate

7. **Acceptance Validation** (qa validator agent)
   - Focus: Feature acceptance and task completion
   - Output: Phase completion confirmation
   - Tags: #agent-validator #phase-X #docs-acceptance-report

#### Post-Phase Review
**Trigger:** Phase completion and QA validation  
**Participants:** User + Code Review Agent + QA Validator Agent

**Process:**
1. **Outcome Assessment**
   - Validate phase deliverables against strategic objectives
   - Assess quality and completeness of implementation
   - Document lessons learned and unexpected discoveries

2. **Strategy Impact Analysis**
   - Determine if strategic approach remains valid
   - Identify needed adjustments to upcoming phases
   - Assess if new phases need to be created or existing ones modified

3. **Next Phase Preparation**
   - Update strategy document with new learnings
   - Modify upcoming phase objectives if necessary
   - Prepare context for next phase planning cycle

### Revision Decision Matrix

#### Strategy-Level Revisions (Update Strategy Document)
**Triggers:**
- Business requirements change significantly
- Technical approach proves fundamentally flawed
- Major dependencies discovered that change timeline/scope
- Risk assessment was significantly wrong

**Process:**
1. Pause implementation
2. Revise strategy document with new understanding
3. Reassess all remaining phases for impact
4. Update phase specifications as needed
5. Communicate changes to stakeholders

#### Phase-Level Revisions (Modify Single Phase)
**Triggers:**
- Phase complexity exceeded budget but strategy remains sound
- Implementation discovered simpler approach than architectural plan
- Integration issues with previous phases require adjustment
- Quality gate failures require significant rework

**Process:**
1. Complete current phase or pause at safe checkpoint
2. Revise affected phase specification
3. Re-run agent workflow for revised phase (architecture → checkpoint → implementation)
4. Update strategy document with lessons learned

#### Tactical Revisions (Minor Implementation Adjustments)
**Triggers:**
- Code review suggests better patterns within same approach
- QA validation reveals edge cases requiring minor additions
- Performance testing suggests specific optimizations
- Integration testing reveals minor interface adjustments needed

**Process:**
1. Continue within current phase framework
2. Make adjustments through normal agent workflow
3. Document decisions in phase execution log
4. No strategy document update needed unless pattern emerges

---

## Stage 3: Completion and Handoff

### Feature Completion Review
**Trigger:** All phases complete and validated

**Process:**
1. **Full Feature Validation**
   - Validate against original work item acceptance criteria
   - Perform end-to-end testing and integration validation
   - Confirm all strategic objectives achieved

2. **Documentation Finalization**
   - Update strategy document with final outcomes
   - Document architectural decisions and lessons learned
   - Create handoff documentation for maintenance team

3. **Work Item Closure**
   - Update work item with completion details
   - Archive phase documentation with proper cross-references
   - Communicate completion to stakeholders

### Lessons Learned Capture
**For Future Feature Planning:**
- What strategic planning approaches worked well?
- Which phase breakdown strategies were most effective?
- What complexity risks were underestimated or overestimated?
- How can the intermediate planning process be improved?

---

## Coordination Standards

### Document Naming Convention
```
[feature]-strategy.md                    # Intermediate strategy document
[feature]-phase-[x].md                   # Phase specifications
[feature]-phase-[x]-architect-decisions.md    # Architectural decisions
[feature]-phase-[x]-tasks-breakdown.md        # Task planning
[feature]-phase-[x]-reviewer-report.md        # Code review
[feature]-phase-[x]-validator-acceptance.md   # QA validation
[feature]-execution-log.md               # Overall execution tracking
```

### Universal Tagging System
```markdown
**Required Tags:**
#feature-[name] #phase-[number] #agent-[role] #status-[current] #timestamp-[YYYYMMDD-HHMM]

**Workflow Status:**
#status-planning #status-architecture #status-checkpoint #status-implementation 
#status-review #status-validation #status-complete

**Document Types:**
#docs-strategy #docs-architectural-decisions #docs-task-breakdown 
#docs-quality-report #docs-acceptance-report #docs-user-checkpoint
```

### Quality Assurance Integration
**Throughout All Stages:**
- Strategy document guides all phase planning
- Human checkpoints prevent over-engineering
- Quality gates enforce standards before phase completion
- Continuous validation against original work item acceptance criteria
- Regular assessment of scope creep and timeline impact

---

## Usage Examples

### Simple Feature (Low Complexity)
```
Work Item: "Add user profile image upload"
Strategy: 2-3 phases, reuse existing patterns, focus on security
Phases: Setup → Implementation → Integration
Checkpoints: Security validation, performance testing
```

### Complex Feature (Medium Complexity)
```  
Work Item: "Implement real-time notifications"
Strategy: 4-5 phases, some new patterns, architectural decisions needed
Phases: Architecture → Backend → Frontend → Testing → Integration
Checkpoints: Architecture approach, scalability decisions, user experience
```

### Legacy Migration (High Complexity)
```
Work Item: "Migrate chat system to conversation-centric schema"
Strategy: 6+ phases, extensive migration, backward compatibility critical
Phases: Planning → Migration → Refactoring → Security → New Features → Validation
Checkpoints: Every major architectural decision, rollback planning, user impact
```

---

*This workflow provides a complete bridge from work items to implemented features using strategic planning, agent coordination, and quality assurance throughout the development process.*