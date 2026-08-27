# Informatica Mapping Researcher for Microsoft Copilot

A researcher agent that answers "what is the source and target of this mapping?",
"which columns does it load?" and "where does this column come from?" against our
Informatica repository — without anyone opening Designer.

The short version of how it works: **do not hand Copilot the raw XML.** Convert the
XML exports into one plain-Markdown page per mapping and per table, put those pages
in a SharePoint document library, and point a Copilot agent at that library as its
knowledge source. The conversion is what makes the answers accurate; the Copilot
part is mostly configuration.

```
PowerCenter repo ──export──► *.xml ──parse──► Markdown pages ──sync──► SharePoint
                                                                          │
                                                                    knowledge source
                                                                          ▼
                                                        Copilot agent + instructions.md
```

## Why the XML has to be converted first

Informatica export XML is machine-readable, not *retrieval*-readable, and Copilot
grounds answers on retrieved text chunks:

- One export file is often megabytes; retrieval returns a few chunks, so most of a
  mapping never reaches the model.
- The interesting facts are attribute values (`FROMINSTANCE`, `TOFIELD`,
  `EXPRESSION`) that carry no surrounding sentence for the retriever to match on.
- Column lineage is not stored anywhere in the file. It only exists as a chain of
  `<CONNECTOR>` elements that has to be walked. A language model asked to walk that
  chain across truncated chunks will guess, and the guesses look right.
- A chunk of XML that lands in context without its `<MAPPING NAME=...>` ancestor
  cannot be attributed to any mapping.

The generator in `extract/` resolves all of that once, deterministically, and
writes it down as prose and tables. Copilot then only has to find and quote it.

## Quick start

```bash
# 1. Export mappings/workflows from Repository Manager (or pmrep ObjectExport) to XML
mkdir -p exports && cp /path/to/*.xml exports/

# 2. Generate the knowledge base
python3 extract/build_kb.py --xml-dir exports --out-dir knowledge

# 3. Look at knowledge/mappings/*.md and confirm the facts against Designer
#    for two or three mappings you know well

# 4. Upload knowledge/ to the SharePoint library, then build the agent
```

Try it against the bundled sample first:

```bash
python3 extract/build_kb.py --xml-dir samples --out-dir /tmp/kb
```

Python 3.11, standard library only — no packages to install and nothing leaves the
machine.

## What gets generated

| Output | Contents |
|--------|----------|
| `knowledge/00-mapping-catalogue.md` | One row per mapping: folder, sources, targets, workflows |
| `knowledge/mappings/<FOLDER>__<MAPPING>.md` | Sources, targets, lookups, transformation config, port expressions, column-level lineage, full column lists, sessions and connections |
| `knowledge/tables/<FOLDER>__<KIND>__<TABLE>.md` | Column list plus every mapping that reads or writes the table |
| `knowledge/mappings.json` | The same model as JSON, if you later want an API-backed action |

## What is in this folder

| Path | Purpose |
|------|---------|
| `extract/parse_powercenter.py` | Parses PowerCenter XML into sources, targets, mappings, connectors, sessions |
| `extract/build_kb.py` | Renders the parsed model as Copilot-ready Markdown + JSON |
| `agent/instructions.md` | The agent's system instructions — the "skill file" |
| `agent/declarativeAgent.json` | Declarative-agent manifest for the source-controlled build route |
| `samples/sample_export.xml` | A small but realistic export to test the pipeline |
| `docs/01-architecture.md` | Which Copilot surface to use, and the file model behind the agent |
| `docs/02-build-the-agent.md` | Step-by-step build, both the no-code and the manifest route |
| `docs/03-operations.md` | Refresh, permissions, rollout, what to do when an answer is wrong |
| `docs/04-evaluation.md` | The question bank the agent must pass before anyone trusts it |

Read `docs/01-architecture.md` first.
