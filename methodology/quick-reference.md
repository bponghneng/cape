# CAPE Quick Reference

*Daily usage guide for Coordinated Agent Planning & Execution* 

## CAPE at a Glance

**What:** Coordinated Agent Planning & Execution - methodology bridging work items to implementation  
**Why:** Prevents over-engineering while leveraging agent expertise through strategic planning and human checkpoints  
**When:** Use for complex features, legacy system work, or multi-phase development projects

## Quick Workflow

1. **Work Item → Strategic Plan** (capture thinking, define phases, set constraints)
2. **Phase Spec → Agent Execution** (architect → human checkpoint → tasks → implement → review → validate)  
3. **Post-Phase Review → Next Phase** (assess outcomes, update strategy, prepare next phase)

## Human Checkpoint Cheat Sheet

**When:** After architectural review, before implementation starts

**Options:**
- ✅ **Approve:** Proceed with architectural approach
- 🔄 **Challenge:** Too complex - provide simpler alternative
- 🎯 **Refine:** Add constraints and request revision  
- 📝 **Document:** Capture decisions for future phases

**Red Flags:**
- Too many new abstractions
- Doesn't reuse existing patterns  
- Over-engineered for MVP
- Conflicts with strategic principles

## Agent Roles Quick Reference

- 📐 **elixir-otp-architect:** Technical architecture & approach (simplicity-first)
- 📋 **feature-task-architect:** Breaks specs into Archon tasks
- 🔍 **elixir-code-reviewer:** Code quality, style, security, testing
- ✅ **elixir-qa-validator:** Feature acceptance & task completion

## Document Naming Quick Reference

- **Strategy:** `[feature]-strategy.md`
- **Phase Spec:** `[feature]-phase-[x].md`  
- **Agent Outputs:** `[feature]-phase-[x]-[agent]-[type].md`

**Examples:**
- `workitem-1-strategy.md`
- `workitem-1-phase-1_5.md`
- `workitem-1-phase-1_5-architect-decisions.md`

## Tagging Quick Reference

**Always Include:** `#feature-[name] #phase-[x] #agent-[role] #status-[current]`

**Status Values:** planning, architecture, checkpoint, implementation, review, validation, complete

**Action Tags:** #checkpoint-pending #approval-required #quality-gate #validation-needed

## Quality Gates Checklist

- ✅ **Before Implementation:** Human checkpoint approved architectural approach
- ✅ **Before Next Phase:** Code review PASS + QA validation complete  
- ✅ **Before Feature Complete:** All strategic objectives met + original work item criteria satisfied

## Common Use Cases

**Simple Feature:** 2-3 phases, reuse existing patterns, focus on specific quality aspects

**Complex Feature:** 4-5 phases, some new patterns needed, multiple architectural decisions

**Legacy Migration:** 6+ phases, extensive changes, backward compatibility critical, high complexity checkpoints

## Troubleshooting

**Agent Over-Engineering:** Use human checkpoint to challenge and request simpler alternatives

**Scope Creep:** Review strategy document, update with new understanding, assess phase impact

**Quality Gate Failures:** Address issues before proceeding, update strategy if pattern emerges

**Phase Complexity Exceeded:** Revise phase specification, re-run agent workflow, document lessons learned

## Success Indicators

**Good Strategic Plan:** Clear objectives, realistic phases, appropriate constraints, confident approach

**Effective Checkpoint:** Architecture is pragmatic, reuses patterns, fits complexity budget, user confident in approach

**Quality Execution:** All gates passed, documentation complete, strategic objectives met, work item criteria satisfied

---