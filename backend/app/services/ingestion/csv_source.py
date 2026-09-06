"""
SuperScout Backend — CSV Data Source Reader
"""
import csv
import io
from pathlib import Path
from typing import Any, Dict, List, Union

from app.services.ingestion.exceptions import SourceFormatError


class CSVDataSource:
    """
    Reads structured CSV data files or streams and yields dict records.
    """

    def __init__(self, source_path_or_stream: Union[str, Path, io.TextIOBase, io.BytesIO]):
        self.source = source_path_or_stream

    def read_records(self) -> List[Dict[str, Any]]:
        """Parse CSV content into list of string-keyed dictionaries."""
        try:
            if isinstance(self.source, (str, Path)):
                file_path = Path(self.source)
                if not file_path.exists():
                    raise SourceFormatError(f"File not found: {file_path}")
                with open(file_path, mode="r", encoding="utf-8-sig") as f:
                    return self._parse_csv_stream(f)
            elif isinstance(self.source, io.BytesIO):
                stream = io.TextIOWrapper(self.source, encoding="utf-8-sig")
                return self._parse_csv_stream(stream)
            elif isinstance(self.source, io.TextIOBase):
                return self._parse_csv_stream(self.source)
            else:
                raise SourceFormatError("Unsupported CSV source type")
        except SourceFormatError:
            raise
        except Exception as exc:
            raise SourceFormatError(f"Failed to parse CSV source: {str(exc)}") from exc

    def _parse_csv_stream(self, stream: io.TextIOBase) -> List[Dict[str, Any]]:
        reader = csv.DictReader(stream)
        records: List[Dict[str, Any]] = []
        for row in reader:
            # Strip key and value whitespace
            clean_row = {
                k.strip(): v.strip() if isinstance(v, str) else v
                for k, v in row.items()
                if k is not None
            }
            records.append(clean_row)
        return records
