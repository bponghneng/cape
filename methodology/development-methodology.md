# CAPE Development Methodology

*Coordinated Agent Planning & Execution*  

## Overview

Coordinated Agent Planning & Execution (CAPE) is a development methodology that bridges high-level work items with detailed technical implementation through strategic planning, agent coordination, and human checkpoints to prevent over-engineering.

## Core Principles

### Strategic Planning
Start with intermediate strategy documents that capture thinking process before diving into technical implementation

### Human Checkpoints  
Human architecture checkpoints prevent over-engineering while preserving agent expertise

### Agent Coordination
Specialized agents work together through defined handoff patterns with full documentation

### Iterative Refinement
Strategy can evolve based on phase outcomes and learning

### Quality Assurance
Built-in review and validation cycles ensure quality throughout

## Workflow Stages

### Stage 1: Strategic Planning
- **Input:** Plane work item with basic requirements
- **Process:** Create intermediate strategy document capturing goals, constraints, and high-level phases using `/cape-strategy` command
- **Output:** Feature Implementation Strategy document

### Stage 2: Iterative Phase Implementation
- **Input:** Strategy document and phase specifications
- **Process:** Phase Planning (using `/cape-phase` command) → Agent Execution (using `/cape-execute` command) with Human Checkpoints → Post-Phase Review
- **Output:** Implemented phases with quality validation

### Stage 3: Completion and Handoff
- **Input:** All phases complete and validated
- **Process:** Full feature validation and documentation finalization
- **Output:** Complete feature ready for production

## Agent Integration

### elixir-otp-architect
High-level technical architecture and approach with simplicity-first mindset for Elixir/Phoenix applications

### feature-task-architect  
Breaks down specifications into actionable Archon tasks with clear acceptance criteria

### elixir-code-reviewer
Code quality, style, security, and testing patterns validation for Elixir/Phoenix code

### elixir-qa-validator
Feature acceptance and task completion validation with Archon task management

### react-native-architect
High-level technical architecture and design planning for React Native/Expo applications

### react-native-code-reviewer
Code quality, style, security, and testing patterns validation for React Native/TypeScript code

### react-native-engineer
Expert guidance on React Native/Expo development with simplicity-first approach

### react-native-test-expert
Comprehensive testing strategies for React Native projects using Jest and testing libraries

## Human Checkpoint

### Purpose
Prevent over-engineering in legacy systems while leveraging agent expertise

### Timing
Two critical checkpoints are required:
1. **After architectural review, before feature task review**
2. **After feature task review, before implementation**

### Checkpoint 1: Architectural Review Checkpoint
**Options:**
- **Approve:** Proceed to feature task review
- **Challenge:** Request simpler alternative (requires re-running architectural review)
- **Refine:** Add constraints and request revision (requires re-running architectural review)

### Checkpoint 2: Feature Task Review Checkpoint  
**Options:**
- **Approve:** Proceed with implementation
- **Refine:** Add constraints and request revision (requires re-running feature task review)

### Review Cycle Requirements
- Human checkpoint must run after every architectural review
- Human checkpoint must run after every feature task review
- If result is **Refine** (either checkpoint) or **Challenge** (architectural only), the respective review must be run again
- Process continues until **Approve** is received at both checkpoints

## Coordination Standards

### Document Naming
`[feature]-[phase]-[agent]-[type].md` format for consistent organization

### Tagging System
Universal tags for feature, phase, agent, status, and document type tracking

### Quality Gates
Code review PASS and QA validation required before phase completion

### Archon Integration
All tasks managed through Archon MCP server with document cross-references

## Benefits

### Prevents Over-Engineering
Human checkpoints catch complexity before implementation

### Leverages Expertise
Specialized agents provide technical knowledge within controlled bounds

### Maintains Flexibility
Strategy can adapt based on learning without full restart

### Ensures Quality
Built-in review cycles and validation throughout development

### Provides Audit Trail
Complete documentation of decisions and evolution

---

*This methodology ensures systematic, coordinated development while maintaining human control over complexity and strategic direction.*