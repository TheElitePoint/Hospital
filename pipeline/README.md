# Hospital Decision-Maker Pipeline

Implements SOP 1-4 (v1.0). **The SOPs are the source of truth.** Where this code and an
SOP disagree, the SOP wins and the code is the bug.

## Design in one paragraph

SQLite is the system of record because the SOPs specify an evidence graph (one-to-many
evidence per claim, correction logs, one canonical person across many accounts) that a
spreadsheet cannot hold. Google Sheets is the shareable layer: `07_Golden` is the
contact-ready deliverable your team works from. Expensive calls sit behind free gates —
CMS data settles Gates A0-A3 at zero cost, and the Apify LinkedIn check runs last, only on
accounts that already passed A0-A10, exactly as SOP 1 orders it.

## Install

```bash
pip install -r requirements.txt
export $(grep -v '^#' ../env-keys/.env | xargs)   # APIFY_TOKENS, GROQ_API_KEYS, TAVILY_API_KEYS
python -m hp.cli init            # creates data/hospitals.db, seeds key pools from env
```

## Run

```bash
python -m hp.cli universe                     # CMS load, IN/OH/KY/TX/AL, free gates A0-A3
python -m hp.cli sop1 --state IN --limit 25   # calibration batch - DO THIS FIRST
python -m hp.cli status
python -m hp.cli golden --target 1000
python -m hp.cli sync --sheet-id <ID> --credentials sa.json
python -m hp.cli pull --sheet-id <ID>         # human QA edits back into the DB
```

## Web dashboard

Install once, then start the local control plane:

```bash
pip install -r requirements.txt
./start_dashboard.command
```

Open `http://127.0.0.1:8765`. Enter the required number of new Golden people and select **Start
pipeline**. The dashboard uses CMS for the free five-state universe, shows live SOP-stage
counts and provider health, and pauses with a masked key-entry dialog if every usable key
for Tavily, Groq or Apify is exhausted. Adding the requested key resumes the same durable
job. Work is committed to SQLite before every pause.

The downloadable workbook contains exactly two tabs: `People` for every unique researched
person and `Golden` for SOP4-selected records with all eight component scores visible.
Generate it directly with:

```bash
python -m hp.cli universe
python -m hp.cli sop1 --limit 5
python -m hp.cli a11 --limit 5
python -m hp.cli sop2 --limit-accounts 5 --max-employees 60
python -m hp.cli sop3 --limit 100
python -m hp.cli golden --target 300
python -m hp.cli export-excel
```

Every stage is resumable. Kill it mid-run and re-run: completed subjects are skipped and
every external response is cached, so a prompt change costs zero scraping credit.

## API keys

Tokens are pooled per provider and rotated automatically.

```bash
python -m hp.cli keys list apify
python -m hp.cli keys add apify apify_api_xxx --label "account 4"
python -m hp.cli keys add apify apify_api_old      # re-adding revives a topped-up token
```

Behaviour when a token dies mid-run:
- **out of credit** -> marked `EXHAUSTED`, the same request retries on the next token
- **revoked/invalid** -> marked `INVALID`, never retried
- **rate limited** -> timed cooldown, stays `ACTIVE`
- **all tokens dead** -> the stage halts cleanly with work committed; add a token and re-run

## The quality guarantee

`hp/llm/validator.py` is the reason to trust the output. Every model claim is dropped
unless it cites evidence that exists, the excerpt is a **verbatim substring of the fetched
page**, and the source tier is derived from the domain rather than self-reported. Dropped
claims are never repaired — the record routes to REVIEW with a specific missing fact.
`tests/test_sop1.py` case 2 proves a model that invents an excerpt cannot produce a PASS.

## The 30% review queue

SOP 4 s01.1 bars a REVIEW record from Golden, so `08_Review_Queue` is a human work queue,
not a side door into the deliverable. It is capped at 30% of PASS volume and ranked by
resolution value (account priority x validated priority x commercial role, weighted up for
accounts because clearing one unlocks a whole buying group, and down for records with no
concrete next action). Cleared records compete normally on the next `golden` run.

## Status

Built: schema, durable key pool, cache, citation validator, CMS universe loader, SOP 1
research and A11 sector gate, bulk SOP 2 employee discovery, independent SOP 3 profile
validation and disproof search, SOP 4 selection, Google Sheets sync, two-sheet Excel export,
CLI, and local web control plane. Apify submissions are journaled before polling so a
restart resumes the paid run instead of submitting it twice.

## Tests

```bash
for t in tests/test_*.py; do python3 "$t"; done
```
