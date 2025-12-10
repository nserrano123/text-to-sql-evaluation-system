"""MetricsSummary model for aggregated metrics"""

from pydantic import BaseModel, Field
from typing import Dict


class MetricsSummary(BaseModel):
    """Model for aggregated evaluation metrics summary"""
    
    execution_accuracy: float = Field(..., ge=0.0, le=100.0, description="Execution accuracy percentage")
    average_time_to_answer: float = Field(..., ge=0.0, description="Average time to answer in seconds")
    component_scores: Dict[str, float] = Field(..., description="F1 scores per component")
    total_evaluations: int = Field(..., ge=0, description="Total number of evaluations")
    completed_evaluations: int = Field(..., ge=0, description="Number of completed evaluations")

    class Config:
        from_attributes = True