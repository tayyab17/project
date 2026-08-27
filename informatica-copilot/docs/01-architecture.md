# 1. Architecture — what to build and where

## Vocabulary: your "skill files" and "plan files" in Microsoft terms

Microsoft Copilot has no `SKILL.md` or plan file. The same jobs are done by
differently-named pieces, and knowing the mapping saves a lot of searching:

| What you want | Microsoft name | In this repo |
|---------------|----------------|--------------|
| The skill file that tells the agent what it is and how to answer | **Instructions** (a single instruction block, `instructions` in the manifest) | `agent/instructions.md` |
| The plan file / the recipes it follows | There is no separate plan file — recipes go in the instructions as named procedures, and the visible entry points are **conversation starters** | the "Standard answers" section, plus `conversation_starters` in `agent/declarativeAgent.json` |
| The knowledge the agent reads | **Knowledge sources** — a SharePoint/OneDrive location, uploaded files, a Graph connector, or Dataverse | `knowledge/` uploaded to SharePoint |
| The whole agent, as a file you can review and version | **Declarative agent manifest** (`declarativeAgent.json`) inside an app package | `agent/declarativeAgent.json` |
| Calling out to a system for a live answer | **Actions** — an API plugin (OpenAPI) or a Power Automate flow | not used in v1; see below |

So "creating skill files, plan files and md files" becomes: **write one instructions
file, generate many knowledge Markdown files, and optionally keep a manifest under
source control.**

## Which Copilot surface

There are three ways to build this. Pick one — do not start with the hardest.

### A. Agent builder in Microsoft 365 Copilot — start here

Create the agent from inside the Copilot app (**Create agent**): give it a name, a
description, paste the instructions, add the SharePoint library as knowledge, share
it with your team. No code, no deployment, minutes to build.

- **Use it when** the knowledge is Markdown files in SharePoint and the answers are
  retrieval-only — which is exactly our case.
- **Limits to expect:** an instructions box with a character cap (about 8,000
  characters at time of writing — `agent/instructions.md` fits comfortably), and a
  cap on how many distinct SharePoint URLs you can attach. Point it at **one
  document library**, not at dozens of individual files, and neither cap bites.
  Verify both caps against current Microsoft docs before you design around them.
- Everyone who uses the agent needs a Microsoft 365 Copilot licence.

### B. Copilot Studio

A full agent-authoring product: the same knowledge sources plus topics, triggers,
tools/actions, connectors, analytics, environment-level governance and publishing to
Teams, a website or M365 Copilot.

- **Move here when** you need one of: a live call into an Informatica or metadata
  REST API, publishing outside M365 Copilot, per-environment DLP and ALM, or usage
  analytics your team can review.
- It runs on Copilot Studio capacity/licensing that is separate from M365 Copilot —
  get that confirmed before you promise a rollout date.

### C. Declarative agent manifest + Teams Toolkit

Author `declarativeAgent.json`, an app manifest and icons in VS Code, package it and
publish to the org's app catalogue.

- **Move here when** the agent itself should live in Git with pull requests and
  review — the same discipline you already apply to the mappings.
- `agent/declarativeAgent.json` is that file, ready to fill in. It references
  `instructions.md` via `$[file('instructions.md')]`, so the instructions stay a
  reviewable Markdown file rather than a JSON string.

Route A and route C produce the *same* kind of agent. You can prototype in A and
move the working instructions into C later without rebuilding anything.

### Where a Graph connector fits

If the repository is very large (thousands of mappings), or the metadata has to
follow per-team permissions, index it with a **Microsoft Graph connector** instead of
a document library. That is a bigger build — a connector, a schema, a crawl
schedule — so do it only after route A has proven the answers are useful.

## Knowledge design — the part that decides answer quality

The generator already follows these rules; keep them if you change it.

1. **One mapping per file.** A file is the unit people cite, review and correct.
2. **Repeat the mapping name in every heading.** Retrieval returns chunks, not
   files. `## Column level lineage for mapping m_LND_TO_DIM_CUSTOMER` survives being
   ripped out of its document; `## Lineage` does not.
3. **Put the answer in the first ten lines.** The header block —
   name, folder, sources, targets, lookups, one-line summary — answers the most
   common question on its own.
4. **Facts as tables, one fact per row.** A lineage row that names the target
   column, the origin port and the full path is quotable verbatim.
5. **Verbatim logic.** Filter conditions, join conditions, lookup overrides and port
   expressions are copied exactly. A paraphrased expression is a wrong answer with
   good grammar.
6. **A separate page per table** so impact questions ("who writes DIM_CUSTOMER?")
   retrieve a page that literally contains the answer.
7. **No raw XML in the library.** Keep the exports in Git or a separate folder that
   is *not* a knowledge source. Indexing both means the retriever sometimes returns
   XML chunks, and answer quality drops.

## When to add an action instead

Retrieval answers "what does this mapping do". It cannot answer "did last night's
run succeed" or "what changed since Tuesday" — that is live state. When you need
those, keep this knowledge base as-is and add a Copilot Studio action calling your
own small API over `mappings.json` plus the operational metadata. Do not try to make
retrieval do it; stale numbers stated confidently are how a tool like this loses its
users.
