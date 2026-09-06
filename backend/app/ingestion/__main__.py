"""
SuperScout Ingestion Module Entry Point

Enables executing CLI via `python -m app.ingestion ...`
"""
from app.services.ingestion.cli import main

if __name__ == "__main__":
    main()
