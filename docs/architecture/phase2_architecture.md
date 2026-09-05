# SuperScout Architecture — Phase 2: Cricket Data Foundation

## Overview

Phase 2 establishes the relational data layer and data ingestion framework for SuperScout. This foundation serves all future intelligence modules:
1. Player Intelligence
2. Auction Intelligence
3. Squad Intelligence
4. Match Intelligence
5. Playing XI Recommendation
6. Batter/Bowler Matchup Analysis
7. Super Over Intelligence

---

## Architectural Stack

- **ORM Layer**: SQLAlchemy 2.x declarative mapped models (`app/models/`).
- **Data Validation & Contracts**: Pydantic v2 schemas (`app/schemas/`).
- **Database Migration**: Alembic (`alembic.ini`, `database/migrations/`).
- **Service Layer**: Decoupled query & mutation logic (`app/services/`).
- **API Framework**: FastAPI REST routers (`app/api/v1/endpoints/`).
- **Data Ingestion**: Abstract 5-stage pipeline (`BaseIngestor` in `app/services/ingestion/`).

---

## Data Ingestion Philosophy

The data ingestion pipeline adheres to strict data integrity principles:

```
[ Raw Data Source ]
        │
        ▼
   1. load_raw()
        │
        ▼
 2. validate_record()  ──(Fail)──► [ Ingestion Error Log ]
        │
        ▼
3. normalize_record()
        │
        ▼
 4. is_duplicate()     ──(True)──► [ Skip Duplicate Record ]
        │
        ▼
  5. save_record()     ──(Fail)──► [ Rollback DB Session ]
```

1. **Non-Destructive**: Never mutates or overwrites raw data files in `data/raw/`.
2. **Atomic Transactions**: Rolling back failed database insertions guarantees zero database corruption.
3. **Audit Reports**: Every execution yields a structured `IngestionReport` containing counts and exact error tracebacks.
