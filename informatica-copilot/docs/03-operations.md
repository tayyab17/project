# 3. Running it — refresh, permissions, rollout

## Keeping the knowledge current

The knowledge base is a snapshot. A stale snapshot answering confidently is the main
way this project fails, so decide the refresh cadence before go-live and put it in
the agent's own description so users see it.

**Weekly is enough for most repositories.** Re-export, regenerate, re-upload:

```bash
python3 extract/build_kb.py --xml-dir exports --out-dir knowledge
```

Regenerating overwrites the pages; upload the whole `knowledge/` folder over the
library so deleted mappings disappear rather than lingering as ghosts.

Two things make the refresh trustworthy:

- **Diff before upload.** Keep `knowledge/` in Git. `git diff` after regenerating
  shows exactly which mappings changed since last week — useful on its own, and it
  catches an export that silently lost half its objects.
- **Stamp the date.** Add a line to `00-mapping-catalogue.md` saying when the export
  was taken, and mention in the agent instructions that answers reflect that export.

Automate it only after two or three manual cycles have gone cleanly.

## Permissions

Copilot honours SharePoint permissions: a user only gets answers from files they can
already open. That is the whole access-control story, and it means the library's
permissions *are* the agent's permissions.

- Restrict `InformaticaKB` to the data team and the analysts who need it.
- Treat the content as sensitive. SQL overrides and lookup conditions expose schema
  names, filter logic and occasionally business rules that are not public internally.
- Never put credentials, connection strings or passwords in the knowledge base. The
  generator emits connection *names* (`CONN_EDW_ORA`) only — keep it that way.

## Rolling it out

1. **Two weeks with the ETL team only.** They can spot a wrong answer instantly;
   an analyst cannot. Collect every wrong answer.
2. **Fix in the right place.** Missing or wrong fact → generator. Right fact,
   badly used → instructions. Keep a running note of which, because a pile of
   instruction patches usually means a data gap you have not admitted yet.
3. **Then open it to analysts**, with one sentence of framing: this reads an export
   of the repository, it is refreshed weekly, and it will tell you when it does not
   know.

## When an answer is wrong

Ask the agent to cite its source page, then open that page.

- **The page is wrong** → the generator or the export is wrong. Fix, regenerate,
  re-upload. Add the case to the question bank.
- **The page is right, the answer is not** → an instructions problem. Add the case
  to the "Standard answers" section of `agent/instructions.md` with the shape of
  answer you wanted.
- **No page was cited, or the cited page is unrelated** → retrieval missed. Usually
  the question used a name that appears nowhere in the knowledge base — a business
  term, a job name, a workflow alias. Add those aliases to the mapping pages (a
  "known as" line in the header block) rather than trying to fix it with prompting.

## What this agent will not do, and should not pretend to

Say these out loud when you announce it, so nobody discovers them the hard way:

- It does not see the live repository — only the last export.
- It does not know run status, load dates, row counts or failures.
- It does not know anything not in the export: shell scripts, stored procedures,
  scheduler dependencies, downstream reports.
- Its impact analysis covers only mappings that were exported. Views, hand-written
  SQL and BI models are outside its world.
