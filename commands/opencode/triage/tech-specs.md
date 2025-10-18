---
description: Triage an implementation plan into technical specification documents.
template: |
  # Create Technical Specifications from a Implementation Plan

  Parse the implementation increments in the `Implementation Plan` and create technical specifications documents using the exact specified markdown `Technical Specification Format`. Follow the `Instructions` to parse the `Implementation Plan` and create the work items as directed. Report the created work items as outlined in `Report`.

  ## Instructions

  - You're parsing a feature implementation plan and technical specifications documents.
  - Read the `Implementation Plan`
  - Identify the `Technical Specification` section in the implementation plan..
  - For each h3 in the `Technical Specification` section, create a technical specification document using the exact specified markdown `Technical Specification Format`.
  - Create the documents in the `specs/*.md` file. Name it appropriately based on `Technical Specification` h3 title.

  ## Implementation Plan

  $ARGUMENTS
---