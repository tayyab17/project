# 2. Build the agent, step by step

Budget roughly a day for a first working version covering one folder, then a few
days of correcting instructions against real questions.

## Step 1 — Export the metadata

Repository Manager: select the folder (or the mappings and their workflows),
**Repository → Export Objects**, tick *Export dependent objects* so sources, targets
and reusable transformations come with the mappings, and save the XML.

Scripted, if you have `pmrep` access:

```bash
pmrep objectexport -n m_LND_TO_DIM_CUSTOMER -o mapping -f EDW_CUSTOMER \
    -m -s -b -r -u exports/m_LND_TO_DIM_CUSTOMER.xml
```

Export one folder per file. Put the files in `exports/` — one flat folder is fine,
the generator recurses.

> On IDMC / Cloud Data Integration there is no PowerCenter XML. Pull the equivalent
> JSON from the asset export API or the metadata REST API, and write a sibling
> parser that produces the same dataclasses in `extract/parse_powercenter.py`.
> Everything downstream — the Markdown, the instructions, the agent — is unchanged.

## Step 2 — Generate the knowledge base

```bash
python3 extract/build_kb.py --xml-dir exports --out-dir knowledge
```

It prints how many mappings, tables and workflows it parsed. If that count is lower
than you expect, the export was missing dependent objects — go back to step 1.

## Step 3 — Verify before anyone sees it

This is the step teams skip and then regret. Take **three mappings you know by
heart** and check their generated page line by line against Designer:

- Are all sources and targets listed, including the ones behind a lookup?
- Does every target column appear, and is anything marked `NOT CONNECTED` genuinely
  unconnected?
- Are the filter and lookup conditions and the port expressions character-identical?
- Does the lineage path for a derived column match what you see on the canvas?

Fix the generator until those three are perfect. A researcher that is right about
90% of columns is worse than no researcher, because nobody can tell which 90%.

## Step 4 — Put the knowledge in SharePoint

1. In the data engineering SharePoint site, create a document library named
   `InformaticaKB`.
2. Upload the contents of `knowledge/` — keep the `mappings/` and `tables/`
   subfolders.
3. Set permissions now, not later: whoever can read this library can read every
   table name, column name and SQL override in the repository. Restrict it to the
   data team plus the analysts who need it.
4. Do **not** upload the raw XML exports into this library.
5. Wait for SharePoint to index the files. Search for a distinctive string such as
   `Column level lineage for mapping` in SharePoint search — when it comes back,
   Copilot can retrieve it too.

## Step 5a — Build it in the M365 Copilot agent builder (recommended first)

1. Microsoft 365 Copilot → **Create agent**.
2. **Name:** `Informatica Mapping Researcher`.
3. **Description:** copy the `description` from `agent/declarativeAgent.json` —
   this is what tells Copilot when to route a question to this agent, so keep the
   words people actually use: mapping, source, target, column, lineage, ETL.
4. **Instructions:** paste the whole of `agent/instructions.md`.
5. **Knowledge:** add the `InformaticaKB` document library as a SharePoint source.
   Add the library URL, not individual files.
6. **Starter prompts:** add the five from `conversation_starters` in the manifest.
7. Turn off web search and any capability you did not ask for. This agent answers
   from the repository export or it says it does not know.
8. Test in the agent's own chat pane, then **Share** with the team.

## Step 5b — Build it from the manifest instead

Use this once the instructions have settled and you want them reviewed in Git.

1. Install the Microsoft 365 Agents Toolkit (formerly Teams Toolkit) in VS Code and
   create a declarative agent project.
2. Replace the generated `declarativeAgent.json` with `agent/declarativeAgent.json`
   and put `agent/instructions.md` next to it — the manifest already loads it with
   `$[file('instructions.md')]`.
3. In `declarativeAgent.json`, replace the placeholder SharePoint URL under the
   `OneDriveAndSharePoint` capability with the real `InformaticaKB` library URL.
4. Supply the app manifest fields the toolkit requires — publisher, colour and
   outline icons, and a unique app id.
5. Provision and preview from VS Code, then publish to the org catalogue for admin
   approval.

Version the whole `agent/` folder. When someone reports a bad answer, the fix is a
pull request against `instructions.md` — reviewable, revertible, attributable.

## Step 6 — Build it in Copilot Studio instead (only if you need actions)

Same knowledge and instructions; the differences are:

- **Knowledge:** add the SharePoint library as a knowledge source; leave general
  knowledge off so the agent cannot answer from the model's own priors.
- **Instructions:** paste `agent/instructions.md` into the agent's instructions.
- **Tools/actions:** add these only when retrieval genuinely cannot answer the
  question — run status, last load date, row counts.
- **Publish:** to Microsoft 365 Copilot and/or Teams, then have an admin approve it.

## Step 7 — Test against the question bank

Run every question in `04-evaluation.md` before you announce the agent. Each wrong
answer is either a knowledge gap (fix the generator, regenerate, re-upload) or a
behaviour gap (fix `instructions.md`). Note which one it was — if you keep patching
instructions to work around missing data, the data is the problem.
