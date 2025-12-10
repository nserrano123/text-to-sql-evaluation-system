"""GoldQuery model for storing reference SQL queries"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class GoldQuery(BaseModel):
    """Model for gold standard SQL queries used as evaluation reference"""
    
    id: UUID
    chat_input: str = Field(..., min_length=1, description="Natural language input from user")
    session_id: Optional[str] = Field(None, max_length=255)
    member_id: Optional[str] = Field(None, max_length=255)
    clasificacion: Optional[str] = Field(None, max_length=100)
    pregunta_descompuesta: Optional[str] = None
    tablas_columnas_ddl: str = Field(..., min_length=1, description="DDL schema information for database context")
    sql_reference: str = Field(..., min_length=1, description="Correct SQL query (gold standard)")
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class GoldQueryCreate(BaseModel):
    """Model for creating new gold queries"""
    
    chat_input: str = Field(..., min_length=1, description="Natural language input from user")
    session_id: Optional[str] = Field(None, max_length=255)
    member_id: Optional[str] = Field(None, max_length=255)
    clasificacion: Optional[str] = Field(None, max_length=100)
    pregunta_descompuesta: Optional[str] = None
    tablas_columnas_ddl: str = Field(..., min_length=1, description="DDL schema information for database context")
    sql_reference: str = Field(..., min_length=1, description="Correct SQL query (gold standard)")

    class Config:
        from_attributes = True