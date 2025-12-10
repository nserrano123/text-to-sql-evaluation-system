"""TimeToAnswer model for TTA metric data"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID


class TimeToAnswer(BaseModel):
    """Model for Time-to-Answer (TTA) metric data"""
    
    id: UUID
    evaluation_id: UUID = Field(..., description="Reference to the evaluation")
    start_time: datetime = Field(..., description="Timestamp when evaluation started")
    end_time: datetime = Field(..., description="Timestamp when evaluation completed")
    duration_seconds: float = Field(..., ge=0, description="Time in seconds from start to completion")
    created_at: datetime

    @field_validator('duration_seconds')
    @classmethod
    def validate_duration(cls, v: float, info) -> float:
        """Validate that duration_seconds matches the difference between end_time and start_time"""
        if 'start_time' in info.data and 'end_time' in info.data:
            expected = (info.data['end_time'] - info.data['start_time']).total_seconds()
            if abs(v - expected) > 0.01:
                raise ValueError('duration_seconds must match end_time - start_time')
        return v
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v: datetime, info) -> datetime:
        """Validate that end_time is after start_time"""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }