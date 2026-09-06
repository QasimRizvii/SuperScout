"""
SuperScout Backend — JSON Data Source Reader
"""
import json
import io
from pathlib import Path
from typing import Any, Dict, List, Union

from app.services.ingestion.exceptions import SourceFormatError


class JSONDataSource:
    """
    Reads structured JSON data files or streams and yields dict records.
    """

    def __init__(self, source_path_or_stream_or_data: Union[str, Path, io.TextIOBase, List[Dict[str, Any]]]):
        self.source = source_path_or_stream_or_data

    def read_records(self) -> List[Dict[str, Any]]:
        """Parse JSON content into list of dictionary records."""
        try:
            if isinstance(self.source, list):
                return self.source

            if isinstance(self.source, (str, Path)):
                file_path = Path(self.source)
                if not file_path.exists():
                    raise SourceFormatError(f"File not found: {file_path}")
                with open(file_path, mode="r", encoding="utf-8") as f:
                    data = json.load(f)
            elif isinstance(self.source, io.TextIOBase):
                data = json.load(self.source)
            else:
                raise SourceFormatError("Unsupported JSON source type")

            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # If wrapped in a container object e.g. {"players": [...]} or single record
                if "records" in data and isinstance(data["records"], list):
                    return data["records"]
                if "items" in data and isinstance(data["items"], list):
                    return data["items"]
                return [data]
            else:
                raise SourceFormatError("JSON content must be a list of records or a dictionary container")
        except SourceFormatError:
            raise
        except Exception as exc:
            raise SourceFormatError(f"Failed to parse JSON source: {str(exc)}") from exc
