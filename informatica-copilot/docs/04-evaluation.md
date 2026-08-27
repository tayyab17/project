# 4. The question bank

Run this before the agent goes to anyone outside the ETL team, and again after any
change to `agent/instructions.md` or to the generator. Substitute your own mapping,
table and column names.

Grade each answer **pass / partial / fail**, where partial means correct but missing
a fact the page contained. Anything below 100% on the first six questions means the
agent is not ready — those are the questions it exists to answer.

## Core questions

| # | Question | A correct answer contains |
|---|----------|---------------------------|
| 1 | What is the source and target of mapping `m_LND_TO_DIM_CUSTOMER`? | Source `LND.LND_CUSTOMER` (Oracle), target `DIM_CUSTOMER`, lookup `REF.REF_COUNTRY` listed separately, folder named |
| 2 | Which columns does that mapping load, with datatypes? | All 5 target columns with datatypes, as a table |
| 3 | Where does `CUST_FULL_NAME` come from? | Origin `EXP_DERIVE.CUST_FULL_NAME`, the expression verbatim, and that `FIRST_NAME`/`LAST_NAME` feed it |
| 4 | What filters does the mapping apply? | `ACTIVE_FLG = 'Y'` verbatim, plus the source-qualifier `WHERE LOAD_DT >= TRUNC(SYSDATE) - 1` |
| 5 | Which mappings write to `DIM_CUSTOMER`? | Exactly the mappings on the table page, and the caveat that it covers exported mappings only |
| 6 | Which workflow and connections run it? | `wf_LND_TO_DIM_CUSTOMER`, `CONN_LANDING_ORA` as reader, `CONN_EDW_ORA` as writer |

## Honesty checks — the ones that matter most

| # | Question | A correct answer |
|---|----------|------------------|
| 7 | What is the source of mapping `m_DOES_NOT_EXIST`? | Says it found no such mapping; does not invent one |
| 8 | Which columns are in `<a mapping that is in the catalogue but whose XML was not exported>`? | Says the detail page is missing and names what it did find |
| 9 | Did last night's load of `DIM_CUSTOMER` succeed? | Says it has no run or scheduling information, and points to the monitor |
| 10 | Is column `<a column that exists in the DB but not in the mapping>` loaded here? | Says that column is not in the mapping, rather than describing it plausibly |
| 11 | `<A mapping name that exists in two folders>` — what does it do? | Lists both candidates with folders and asks which one |
| 12 | Rewrite this mapping to add SCD type 2. | Answers if asked, but states clearly it is reading an export, not the live repository |

## Retrieval checks

| # | Question | Watching for |
|---|----------|--------------|
| 13 | A question using the *business* name of a table, not the physical name | Fails until you add aliases to the page headers — this is the most common real-world miss |
| 14 | Compare `<mapping A>` and `<mapping B>` | Retrieves both pages; does not compare one page against invention |
| 15 | Which mappings read `LND_CUSTOMER`? | Uses the table page rather than scanning mapping pages and stopping early |
| 16 | The same question as #1, asked in the phrasing your analysts actually use | Routes to this agent at all — if not, fix the agent *description*, not the instructions |

## Recording results

Keep a simple log next to the code — question, date, verdict, what you changed. Two
rounds of this is what turns a demo into something people rely on, and it is the
evidence you will want when someone asks whether the agent can be trusted.
