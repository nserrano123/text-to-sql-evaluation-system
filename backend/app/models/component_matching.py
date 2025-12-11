"""ComponentMatching model for component evaluation data"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ComponentMatching(BaseModel):
    """Model for Component Matching metric data"""
    
    id: UUID
    evaluation_id: UUID = Field(..., description="Reference to the evaluation")
    select_correct: bool = Field(..., description="Whether SELECT component is correct")
    where_correct: bool = Field(..., description="Whether WHERE component is correct")
    group_by_correct: bool = Field(..., description="Whether GROUP BY component is correct")
    order_by_correct: bool = Field(..., description="Whether ORDER BY component is correct")
    keywords_correct: bool = Field(..., description="Whether KEYWORDS component is correct")
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="F1 score calculated from component matching")
    evaluator_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ComponentMatchingCreate(BaseModel):
    """Model for creating new component matching records"""
    
    evaluation_id: UUID = Field(..., description="Reference to the evaluation")
    select_correct: bool = Field(..., description="Whether SELECT component is correct")
    where_correct: bool = Field(..., description="Whether WHERE component is correct")
    group_by_correct: bool = Field(..., description="Whether GROUP BY component is correct")
    order_by_correct: bool = Field(..., description="Whether ORDER BY component is correct")
    keywords_correct: bool = Field(..., description="Whether KEYWORDS component is correct")
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="F1 score calculated from component matching")
    evaluator_notes: Optional[str] = None

    class Config:
        from_attributes = True