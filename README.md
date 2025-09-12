# CAPE: Coordinated Agent Planning & Execution

## What is CAPE?

CAPE started as an extensive conversation with Claude Code about developing multi-agent workflows for complex brownfield codebases. Claude Code suggested the backronym name, which is laughably overblown for my actual intentions—but as someone who counts himself as attitudinally Generation X, I kept the name out of amusement at the irony I detected in this corporate-speak backronym.

*A comprehensive development methodology for complex feature implementation with agent coordination and human oversight.* Despite the highly over-engineered process language, I've found the methodology and workflow documents genuinely handy as context when working with Claude Code to build agents and commands.

The repo has evolved sensibly to satisfy smaller-scale ambitions: a collection of subagent and command templates I can source for my AI coder tools. CAPE bridges the gap between high-level work items and detailed technical implementation through strategic planning, specialized agent coordination, and human checkpoints that prevent over-engineering while leveraging agent expertise. As Claude says.

## Quick Start

1. **Read:** [CAPE Quick Reference](./methodology/quick-reference.md) for daily usage
2. **Study:** [Development Methodology](./methodology/development-methodology.md) for complete system
3. **Follow:** [Work Item Pipeline](./workflows/work-item-pipeline.md) for complete process
4. **Coordinate:** [Agent Coordination Protocol](./workflows/agent-coordination-protocol.md) for agent workflows

## Directory Structure

```
CAPE/
├── methodology/
│   ├── development-methodology.md         # Complete system overview
│   └── quick-reference.md                 # Daily usage cheat sheet
├── workflows/
│   ├── work-item-pipeline.md              # Work item to implementation pipeline
│   └── agent-coordination-protocol.md     # Execution coordination standards
├── templates/
│   └── command/                           # Command templates for AI tools
│       └── spec/                         # Specification generation commands
│           ├── strategy.md               # Strategic planning command
│           └── phase.md                  # Phase specification command
└── agents/
    ├── claude-code/                       # Claude Code agent definitions
    │   ├── elixir-otp-architect.md        # Elixir/Phoenix architecture
    │   ├── elixir-code-reviewer.md        # Elixir code quality
    │   ├── elixir-qa-validator.md         # Elixir feature validation
    │   ├── feature-task-architect.md      # Task planning & breakdown
    │   ├── react-native-architect.md      # React Native architecture
    │   ├── react-native-code-reviewer.md  # React Native code quality
    │   ├── react-native-engineer.md       # React Native development
    │   └── react-native-test-expert.md    # React Native testing
    └── opencode/                          # OpenCode agent definitions
        ├── react-native-engineer.md       # React Native development
        └── react-native-code-reviewer.md  # React Native code quality
```

## Core Workflow

### 1. Strategic Planning
**Input:** Work item description  
**Process:** Create intermediate strategy document  
**Output:** Strategic plan with phases, constraints, and success criteria

### 2. Phase Implementation  
**Input:** Strategic plan + phase specification  
**Process:** Agent workflow with human checkpoints  
**Output:** Implemented phase with quality validation

### 3. Iterative Refinement
**Input:** Phase outcomes and lessons learned  
**Process:** Update strategy and plan next phase  
**Output:** Evolved strategy and next phase specification

## Key Innovations

### Human Architecture Checkpoint
- **Problem:** Agents can over-engineer solutions in legacy systems
- **Solution:** Human checkpoint after architecture review, before implementation
- **Options:** Approve / Challenge / Refine / Document architectural approach

### Strategic Planning Layer  
- **Problem:** Gap between work items and detailed phase specifications
- **Solution:** Intermediate strategy document capturing thinking process
- **Benefits:** Flexibility, context preservation, strategic alignment

### Agent Coordination Protocol
- **Problem:** Context loss and coordination issues in multi-agent workflows  
- **Solution:** Universal tagging, document naming, and handoff standards
- **Benefits:** Complete audit trail, seamless handoffs, quality assurance

### Quality Gate Integration
- **Problem:** Quality issues discovered too late in development process
- **Solution:** Built-in code review and validation at each phase boundary
- **Benefits:** Early issue detection, consistent quality, reduced rework

## When to Use CAPE

### Ideal for:
- **Complex Features:** Multi-phase development with architectural decisions
- **Legacy System Work:** High over-engineering risk, existing pattern constraints  
- **Strategic Projects:** Clear business value, multiple stakeholder coordination
- **Quality-Critical Development:** High reliability, security, or performance requirements

### Simple Alternative:
- **Basic Features:** 1-2 phase implementation, well-understood patterns
- **Quick Fixes:** Bug fixes, minor enhancements, no architectural impact
- **Experimental Work:** Proof of concepts, spike investigations, throwaway prototypes

## Success Indicators

### Good Strategic Planning
- Clear objectives and realistic phase breakdown
- Appropriate complexity constraints for target system
- Confident approach with identified risks and mitigation

### Effective Human Checkpoints  
- Architecture is pragmatic and reuses existing patterns
- Approach fits within complexity budget
- User confident in technical direction

### Quality Execution
- All quality gates passed consistently  
- Documentation complete and cross-referenced
- Strategic objectives met and work item criteria satisfied
- Team confident in maintainability and extensibility

## Common Usage Patterns

### Simple Feature (2-3 phases)
```
Strategy: Reuse existing patterns, focus on specific quality aspect
Phases: Setup → Implementation → Integration  
Checkpoints: Security/performance validation
Example: Add user profile image upload
```

### Complex Feature (4-5 phases)
```
Strategy: Some new patterns needed, multiple architectural decisions
Phases: Architecture → Backend → Frontend → Testing → Integration
Checkpoints: Architecture approach, scalability decisions, UX validation  
Example: Implement real-time notifications system
```

### Legacy Migration (6+ phases)
```
Strategy: Extensive changes, backward compatibility critical
Phases: Planning → Migration → Refactoring → Security → New Features → Validation
Checkpoints: Every major architectural decision, rollback planning, user impact
Example: Migrate chat system to conversation-centric schema
```

## Getting Help

### Documentation References
- **Daily Usage:** [CAPE Quick Reference](./methodology/quick-reference.md)
- **Complete System:** [CAPE Development Methodology](./methodology/development-methodology.md)
- **Troubleshooting:** Check Quick Reference troubleshooting section
- **Agent Integration:** [Agent Coordination Protocol](./workflows/agent-coordination-protocol.md)

### Common Issues  
- **Over-Engineering:** Use human checkpoint to challenge architectural complexity
- **Scope Creep:** Review and update strategy document with new understanding
- **Quality Failures:** Address issues before proceeding, update strategy if pattern emerges
- **Agent Coordination:** Verify tagging and document cross-references are complete

---

## Version History

- **v1.1** (2025-09-12): Updated for standalone operation
  - Removed task management dependency from workflows and templates
  - Added React Native agent definitions for mobile development
  - Updated agent integration section with complete agent ecosystem
  - Added command templates for strategy and phase specification
  - Enhanced human checkpoint workflow with two-stage validation
- **v1.0** (2025-09-07): Initial CAPE methodology with human checkpoint innovation
  - Enhanced agent specifications with full coordination integration  
  - Complete workflow from task management platform work items to production deployment
  - Universal coordination protocol for multi-agent development

---

*CAPE enables systematic, coordinated development while maintaining human control over complexity and strategic direction.*