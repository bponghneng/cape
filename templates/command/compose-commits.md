---
description: Compose conventional commits from unstaged changes
tools: mcp__archon__rag_search_knowledge_base,  mcp__firecrawl-mcp__firecrawl_scrape, mcp__firecrawl-mcp__firecrawl_search, Bash, Read, Grep, Glob, WebSearch
---

# /compose-commits - Compose conventional commits

Execute the `Learn`, `Analyze`, and `Compose` sections.

## Learn Conventional Commits Standard

- Use `mcp__archon__rag_search_knowledge_base` to search for conventional commits standard
- Scrape the Conventional Commits specification `https://www.conventionalcommits.org/en/v1.0.0/` if knowledge base search insufficient

## Analyze

1. Run `git status` to see all unstaged changes
2. Run `git diff` to understand what changed
3. Read modified files to understand the purpose of changes
4. Group related changes logically

## Compose

Create conventional commits following the standard:

- `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Include breaking changes notation if applicable
- Commit the changes

## Report

List of commits with complete conventional commit messages, including commit sha.
