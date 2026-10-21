# Hospital Decision-Maker Pipeline

A four-stage research pipeline that finds, validates and ranks decision-makers at US hospitals.

| Stage | Purpose |
|---|---|
| SOP 1 | Qualify hospital accounts against the monitoring-workflow signal gates |
| SOP 2 | Discover candidate decision-makers at qualified accounts |
| SOP 3 | Independently validate each person (employment, role, location, activity) |
| SOP 4 | Score and select the Golden list |

- `SOPs/` holds the written procedures, which are the source of truth.
- `pipeline/` holds the implementation. See [pipeline/README.md](pipeline/README.md) for setup and usage.

API keys, credentials, databases and run output are not stored in this repository.
Provide credentials through environment variables as described in the pipeline README.
