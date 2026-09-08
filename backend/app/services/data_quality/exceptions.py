"""
SuperScout Backend — Data Quality Exceptions
"""

class DataQualityError(Exception):
    """Base exception for data quality domain."""
    pass

class DataValidationError(DataQualityError):
    def __init__(self, message: str):
        super().__init__(f"Data validation failed: {message}")

class EntityNotFoundError(DataQualityError):
    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} not found.")

class ProvenanceNotFoundError(DataQualityError):
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        super().__init__(f"Data provenance batch '{batch_id}' not found.")
