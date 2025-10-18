---
description: Triage a chore into an implementation plan.
template: |
  # Triage a Chore into an Implementation Plan

  Create a new research report and implementation plan for a codebase chore using the exact specified markdown `Plan Format`. Follow the `Instructions` to conduct the research and create the plan, and use the `Relevant Files` to focus on the right files.

  ## Instructions

  - You're writing documents to research and plan a codebase chore that will add value to the application.
  - Research the codebase to determine the problem specified in the `Chore`. Identify the root cause and determine the best solution.
  - Use the `react-native-architect` agenrt to create the research report in the `./specs/` directory using the following format: `./specs/chore-<chore name>-research.md`.
  - Use the `Research Report Format` below to create the research report.
  - Use the `taskmaster` agent to read the research report and break down the solution into a plan with actionable work increments that can be completed in 1-2 days by a single engineer. Create the plan in the `./specs/` directory using the following format: `./specs/chore-<chore name>-plan.md`.
  - Use the `Plan Format` below to create the plan.
  - IMPORTANT: Replace every <placeholder> in the `Research Report Format` and `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
  - Instructions for subagents:
      - Use your reasoning model: THINK HARD about the feature requirements, design and implementation approach.
      - Start your research by reading the `./CLAUDE.md` and `./ws2-mobile/README.md` files.
      - Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
      - Design for extensibility and maintainability, but remember the simplicity mindset.
      - Respect requested files in the `Relevant Files` section.

  ## Relevant Files

  Focus on the following files:
  - `./ws2-mobile/package.json` - Contains the project configuration and dependencies.
  - `./ws2-mobile/README.md` - Contains the project overview and instructions.
  - `./ws2-mobile/src/**` - Contains the source code for the application.

  Ignore all other files in the codebase.

  ## Research Method

  Use the `react-native-architect` subagent to understand the architecture of the codebase, to detail existing implementations, and to determine the best solution.

  ## Research Report Format

  ```md
  # Chore: <chore name>

  ## Problem Statement
  <clearly define the specific problem or opportunity the feature addresses>

  ## Solution Statement
  <describe the proposed solution approach and how it solves the problem>

  ## Relevant Files
  <find and list the files that are relevant to the feature implementation and describe why they are relevant in bullet points>

  ## Test Coverage
  <describe the proposed test coverage for the feature implementation with bullet points listing the scenarios and test cases covered>

  ## Notes
  <optionally list any additional critical analysis. Some examples are legacy patterns that may need to be refactored, alternate approaches or design patterns that may be more appropriate, or context that are relevant to the feature that will be helpful to lead engineers planning work increments specific to this feature>
  ```

  ## Plan Format

  ```md
  # Chore: <chore name>

  ## Chore Description

  <describe the chore in detail, including its purpose and value to users>

  ## User Story

  As a <type of user>
  I want to <action/goal>
  So that <benefit/value>=

  ## Technical Specification

  <snippets for database migrations and schema, context modules and functions, controller methods, view modules and functions, API endpoint routes and other relevant code>

  ## Implementation Increments

  <list step by step increments as h3 headers plus bullet points. use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Each increment should be a complete unit of work that can be completed in 1-2 days by a single engineer. Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

  ### Increment 1: <title of the increment>

  <describe the increment in detail, including its purpose and value to users>

  #### Implementation Details

  <reference sections in `Technical Specification` and `Relevant Files` related to the increment>

  #### Relevant Files

  <find and list the files that are relevant to the increment. Describe why they are relevant in bullet points. If there are new files that need to be created for the increment, list them in an h4 'New Files' section.>

  #### Key Test Cases

  <list key test cases for the increment. Include unit tests, integration tests and API tests as appropriate. Testing strategy should be clear, concise and lean. Focus on core functionality and minimize testing of edge cases.>

  #### Acceptance Criteria
  <list specific, measurable criteria that must be met for the increment to be considered complete>

  #### Dependencies
  <list any work increment dependencies that must be completed before this increment can be implemented>

  ## Notes
  <optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the tech lead planning work increments>
  ```

  ## Chore

  $ARGUMENTS
---