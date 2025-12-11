"""Unit tests for Pydantic model validators"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import ValidationError

from app.models.gold_query import GoldQuery, GoldQueryCreate
from app.models.time_to_answer import TimeToAnswer, TimeToAnswerCreate


class TestGoldQueryValidators:
    """Test validators for GoldQuery models"""
    
    def test_rejects_missing_required_fields(self):
        """Test that verifies rejection of missing required fields"""
        # Test missing chat_input
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                tablas_columnas_ddl="CREATE TABLE test (id INT);",
                sql_reference="SELECT * FROM test;"
            )
        assert "chat_input" in str(exc_info.value)
        
        # Test missing tablas_columnas_ddl
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                sql_reference="SELECT * FROM test;"
            )
        assert "tablas_columnas_ddl" in str(exc_info.value)
        
        # Test missing sql_reference
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                tablas_columnas_ddl="CREATE TABLE test (id INT);"
            )
        assert "sql_reference" in str(exc_info.value)
    
    def test_rejects_empty_required_fields(self):
        """Test that verifies rejection of empty required fields"""
        # Test empty chat_input (min_length constraint triggers first)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="",
                tablas_columnas_ddl="CREATE TABLE test (id INT);",
                sql_reference="SELECT * FROM test;"
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Test whitespace-only chat_input (custom validator triggers)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="   \n\t  ",
                tablas_columnas_ddl="CREATE TABLE test (id INT);",
                sql_reference="SELECT * FROM test;"
            )
        assert "Field cannot be empty or contain only whitespace" in str(exc_info.value)
        
        # Test empty tablas_columnas_ddl (min_length constraint triggers first)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                tablas_columnas_ddl="",
                sql_reference="SELECT * FROM test;"
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Test whitespace-only tablas_columnas_ddl (custom validator triggers)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                tablas_columnas_ddl="   \t   ",
                sql_reference="SELECT * FROM test;"
            )
        assert "Field cannot be empty or contain only whitespace" in str(exc_info.value)
        
        # Test empty sql_reference (min_length constraint triggers first)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                tablas_columnas_ddl="CREATE TABLE test (id INT);",
                sql_reference=""
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Test whitespace-only sql_reference (custom validator triggers)
        with pytest.raises(ValidationError) as exc_info:
            GoldQueryCreate(
                chat_input="Show me all records",
                tablas_columnas_ddl="CREATE TABLE test (id INT);",
                sql_reference="  \n  "
            )
        assert "Field cannot be empty or contain only whitespace" in str(exc_info.value)
    
    def test_accepts_valid_required_fields(self):
        """Test that valid required fields are accepted"""
        valid_data = GoldQueryCreate(
            chat_input="Show me all records",
            tablas_columnas_ddl="CREATE TABLE test (id INT);",
            sql_reference="SELECT * FROM test;"
        )
        assert valid_data.chat_input == "Show me all records"
        assert valid_data.tablas_columnas_ddl == "CREATE TABLE test (id INT);"
        assert valid_data.sql_reference == "SELECT * FROM test;"


class TestTimeToAnswerValidators:
    """Test validators for TimeToAnswer models"""
    
    def test_validates_timestamp_order(self):
        """Test that verifies validation of timestamp order (end_time > start_time)"""
        evaluation_id = uuid4()
        start_time = datetime.now()
        end_time = start_time - timedelta(seconds=10)  # Invalid: end before start
        duration = 10.0
        
        # Test with TimeToAnswerCreate
        with pytest.raises(ValidationError) as exc_info:
            TimeToAnswerCreate(
                evaluation_id=evaluation_id,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration
            )
        assert "end_time must be after start_time" in str(exc_info.value)
        
        # Test with TimeToAnswer (full model)
        with pytest.raises(ValidationError) as exc_info:
            TimeToAnswer(
                id=uuid4(),
                evaluation_id=evaluation_id,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                created_at=datetime.now()
            )
        assert "end_time must be after start_time" in str(exc_info.value)
    
    def test_validates_duration_calculation(self):
        """Test that verifies validation of duration calculation"""
        evaluation_id = uuid4()
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)
        incorrect_duration = 50.0  # Should be 30.0
        
        # Test with TimeToAnswerCreate
        with pytest.raises(ValidationError) as exc_info:
            TimeToAnswerCreate(
                evaluation_id=evaluation_id,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=incorrect_duration
            )
        assert "duration_seconds must match end_time - start_time" in str(exc_info.value)
        
        # Test with TimeToAnswer (full model)
        with pytest.raises(ValidationError) as exc_info:
            TimeToAnswer(
                id=uuid4(),
                evaluation_id=evaluation_id,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=incorrect_duration,
                created_at=datetime.now()
            )
        assert "duration_seconds must match end_time - start_time" in str(exc_info.value)
    
    def test_accepts_valid_timestamps_and_duration(self):
        """Test that valid timestamps and duration are accepted"""
        evaluation_id = uuid4()
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=45)
        correct_duration = 45.0
        
        # Test TimeToAnswerCreate
        valid_create = TimeToAnswerCreate(
            evaluation_id=evaluation_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=correct_duration
        )
        assert valid_create.evaluation_id == evaluation_id
        assert valid_create.start_time == start_time
        assert valid_create.end_time == end_time
        assert valid_create.duration_seconds == correct_duration
        
        # Test TimeToAnswer (full model)
        valid_full = TimeToAnswer(
            id=uuid4(),
            evaluation_id=evaluation_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=correct_duration,
            created_at=datetime.now()
        )
        assert valid_full.evaluation_id == evaluation_id
        assert valid_full.start_time == start_time
        assert valid_full.end_time == end_time
        assert valid_full.duration_seconds == correct_duration
    
    def test_allows_small_duration_tolerance(self):
        """Test that small differences in duration calculation are tolerated"""
        evaluation_id = uuid4()
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)
        # Duration with small tolerance (within 0.01 seconds)
        duration_with_tolerance = 30.005
        
        # This should be accepted (within tolerance)
        valid_data = TimeToAnswerCreate(
            evaluation_id=evaluation_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_with_tolerance
        )
        assert valid_data.duration_seconds == duration_with_tolerance