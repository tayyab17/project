# CLAUDE.md

This file provides guidance for AI assistants (Claude, Copilot, etc.) working in this repository.
Keep it updated as the project evolves.

---

## Project Overview

> **TODO:** Replace this section with a description of what this project does, who its users are,
> and what problem it solves.

**Status:** Repository initialized; codebase not yet added.

---

## Repository Structure

```
project/
├── CLAUDE.md          # This file — AI assistant guidance
└── .git/
```

> **TODO:** Update this tree once source code is committed.

---

## Tech Stack

> **TODO:** Fill in the languages, frameworks, libraries, and tools this project uses.

| Layer | Technology |
|-------|-----------|
| Language | — |
| Framework | — |
| Database | — |
| Testing | — |
| CI/CD | — |

---

## Development Setup

### Prerequisites

> **TODO:** List required tools and versions (Node, Python, Go, Docker, etc.).

### First-time Setup

```bash
# Clone the repository
git clone <repo-url>
cd project

# Install dependencies (update command for your stack)
# npm install       # Node.js
# pip install -r requirements.txt  # Python
# go mod download   # Go
```

### Environment Variables

> **TODO:** Document required environment variables. Never commit secrets.
> Provide a `.env.example` file in the repo with placeholder values.

```bash
# Copy the example and fill in real values
cp .env.example .env
```

---

## Common Commands

> **TODO:** Replace placeholders with real commands for this project.

| Task | Command |
|------|---------|
| Install dependencies | `<install-command>` |
| Start dev server | `<dev-command>` |
| Run all tests | `<test-command>` |
| Run linter | `<lint-command>` |
| Type check | `<typecheck-command>` |
| Build for production | `<build-command>` |
| Format code | `<format-command>` |

### Running Tests

> **TODO:** Describe the test structure and how to run subsets.

```bash
# Run all tests
<test-command>

# Run a single test file
<test-command> path/to/test

# Run tests matching a pattern
<test-command> --grep "pattern"
```

---

## Git Workflow

### Branch Naming

```
feature/<short-description>     # new functionality
fix/<short-description>         # bug fixes
chore/<short-description>       # maintenance, dependency updates
docs/<short-description>        # documentation only
refactor/<short-description>    # code restructuring without behavior change
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional-scope>): <short summary>

<optional body — explain WHY, not what>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `perf`

Examples:
```
feat(auth): add OAuth2 login flow
fix(api): handle null response from external service
chore: upgrade dependencies to latest versions
```

### Pull Requests

- Keep PRs focused — one concern per PR.
- Link related issues in the PR description.
- All CI checks must pass before merging.
- Require at least one review before merging to `main`.

---

## Code Conventions

### General

- Prefer clarity over cleverness — code is read far more than it is written.
- Keep functions small and single-purpose.
- No commented-out code — delete it; git history preserves it.
- No `TODO`/`FIXME` in committed code — open an issue instead.

### Naming

| Element | Convention |
|---------|-----------|
| Variables / functions | `camelCase` (JS/TS) or `snake_case` (Python/Go) |
| Classes / types | `PascalCase` |
| Constants | `UPPER_SNAKE_CASE` |
| Files | `kebab-case` (web) or `snake_case` (backend) |
| Database columns | `snake_case` |

> **TODO:** Adjust conventions to match the actual language(s) used.

### Comments

Write comments only when the **why** is non-obvious — a hidden constraint, a subtle invariant,
or a workaround for a specific external bug. Never describe what the code does (well-named
identifiers already do that).

### Error Handling

- Validate at system boundaries (user input, external APIs, environment variables).
- Do not add defensive checks for scenarios that cannot happen inside well-typed internal code.
- Propagate errors with enough context to diagnose without a debugger.

### Security

- Never hardcode secrets, API keys, or passwords.
- Sanitize and validate all external input before use.
- Follow OWASP Top 10 guidelines.
- Keep dependencies up to date; review security advisories.

---

## Testing Conventions

- Write tests alongside the code they cover.
- Test behavior, not implementation — if refactoring doesn't break tests, the tests are useful.
- Aim for fast unit tests; keep integration/e2e tests in a separate suite.
- Use descriptive test names: `describe("UserService") > it("returns 404 when user not found")`.

---

## Architecture Decisions

> **TODO:** Record significant architecture decisions here, or link to an `docs/adr/` directory
> using the [ADR format](https://adr.github.io/).

| Date | Decision | Rationale |
|------|----------|-----------|
| — | — | — |

---

## AI Assistant Instructions

These rules apply specifically when an AI assistant (Claude, Copilot, etc.) is working in
this repository.

### Do

- Read `CLAUDE.md` at the start of every session to orient yourself.
- Prefer editing existing files over creating new ones.
- Run the project's linter and tests after making changes, and fix any failures before stopping.
- Commit with clear, conventional commit messages (see above).
- Push to the correct feature branch (never to `main` directly).
- Ask before taking irreversible actions (force-push, deleting files, dropping data).

### Do Not

- Do not invent API endpoints, environment variables, or configuration keys that aren't documented here or in the source.
- Do not add features, refactors, or abstractions beyond what was asked.
- Do not add comments that describe what code does — only comments for non-obvious *why*.
- Do not commit `.env` files, secrets, or credentials.
- Do not leave `console.log`/`print` debug statements in committed code.
- Do not use `any` types or skip type checking to make errors disappear.
- Do not suppress linter warnings with inline disable comments unless absolutely necessary (and if you do, add a comment explaining why).

### Working Style

- Prefer small, focused changes that are easy to review.
- When uncertain about intent, ask rather than guess.
- If a requested change would require a large-scale refactor, flag that upfront before proceeding.
- After completing a task, run the full test suite and confirm it passes.

---

## CI/CD

> **TODO:** Describe the CI pipeline (GitHub Actions, CircleCI, etc.) and what it runs.

All CI checks must be green before a PR can be merged. If a check fails on your branch:
1. Read the failure log carefully.
2. Reproduce locally using the commands in the **Common Commands** table.
3. Fix the underlying issue — do not use `--no-verify` or skip hooks to bypass checks.

---

## Deployment

> **TODO:** Describe how the application is deployed (environments, commands, access required).

| Environment | Branch | URL |
|-------------|--------|-----|
| Development | `main` | — |
| Staging | — | — |
| Production | — | — |

---

## Useful References

> **TODO:** Add links to design docs, runbooks, internal wikis, or API specs.

- Project board / issue tracker: —
- Design documents: —
- API documentation: —
