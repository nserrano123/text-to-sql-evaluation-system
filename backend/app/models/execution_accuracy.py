"""ExecutionAccuracy model for EX metric data"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ExecutionAccuracy(BaseModel):
    """Model for Execution Accuracy (EX) metric data"""
    
    id: UUID
    evaluation_id: UUID = Field(..., description="Reference to the evaluation")
    results_match: Optional[bool] = Field(None, description="Whether query results match")
    is_correct: bool = Field(..., description="Whether the generated query produces correct results")
    evaluator_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ExecutionAccuracyCreate(BaseModel):
    """Model for creating new execution accuracy records"""
    
    evaluation_id: UUID = Field(..., description="Reference to the evaluation")
    results_match: Optional[bool] = Field(None, description="Whether query results match")
    is_correct: bool = Field(..., description="Whether the generated query produces correct results")
    evaluator_notes: Optional[str] = None

    class Config:
        from_attributes = True