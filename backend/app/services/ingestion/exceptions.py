"""
SuperScout Backend — Ingestion Exceptions
"""

class IngestionPipelineError(Exception):
    """Base exception for all ingestion pipeline errors."""
    pass


class SourceFormatError(IngestionPipelineError):
    """Raised when source file format is malformed or unparseable."""
    pass


class RecordValidationError(IngestionPipelineError):
    """Raised when a data record violates domain validation rules."""
    pass


class ResolutionError(IngestionPipelineError):
    """Raised when an entity cannot be resolved unambiguously."""
    pass


class DuplicateRecordError(IngestionPipelineError):
    """Raised when a duplicate record is detected."""
    pass
