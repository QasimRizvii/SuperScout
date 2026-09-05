# SuperScout — Data Directory Architecture

This directory houses cricket datasets and data processing artifacts for SuperScout.

## Subdirectories

- **`raw/`**: Unmodified raw source data files (JSON, CSV, YAML).
- **`processed/`**: Cleaned, validated, and normalized dataset artifacts ready for database ingestion.
- **`external/`**: Reference data, external mappings, dictionary files, and static assets.

## Ingestion Guidelines

1. **Non-Destructive Operations**: Never overwrite raw data files in `raw/`.
2. **Schema Integrity**: All records must pass through the `BaseIngestor` pipeline (`validate`, `normalize`, `detect_duplicates`).
3. **Audit Trail**: Any ingestion failure or anomaly must log clear errors without corrupting database state.
