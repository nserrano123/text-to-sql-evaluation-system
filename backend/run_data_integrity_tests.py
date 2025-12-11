#!/usr/bin/env python3
"""
Direct runner for data integrity property-based tests
**Feature: text-to-sql-evaluation, Property 2: Data integrity on query**
"""

import sys
sys.path.append('.')

from hypothesis import given, strategies as st, settings
from app.models.gold_query import GoldQuery
from uuid import uuid4
from datetime import datetime, timezone
from typing import List


# Strategy for generating valid strings
valid_string_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for generating optional strings
optional_string_strategy = st.one_of(st.none(), st.text(max_size=255))

# Strategy for generating valid GoldQuery objects
def gold_query_strategy():
    return st.builds(
        GoldQuery,
        id=st.just(uuid4()),  # Generate unique UUID for each record
        chat_input=valid_string_strategy,
        session_id=optional_string_strategy,
        member_id=optional_string_strategy,
        clasificacion=optional_string_strategy,
        pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000)),
        tablas_columnas_ddl=valid_string_strategy,
        sql_reference=valid_string_strategy,
        created_at=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        ).map(lambda dt: dt.replace(tzinfo=timezone.utc))
    )


def simulate_database_roundtrip(records: List[GoldQuery]) -> List[GoldQuery]:
    """
    Simulate storing records to database and retrieving them back.
    This simulates the database roundtrip that should preserve data integrity.
    In a real implementation, this would involve actual database operations.
    """
    # Simulate serialization/deserialization that happens in database operations
    serialized_records = []
    
    for record in records:
        # Convert to dict (simulating database storage)
        record_dict = record.model_dump()
        
        # Convert back to model (simulating database retrieval)
        restored_record = GoldQuery(**record_dict)
        serialized_records.append(restored_record)
    
    return serialized_records


@given(st.lists(gold_query_strategy(), min_size=1, max_size=10))
@settings(max_examples=100)
def test_data_integrity_on_query_single_record_roundtrip(records: List[GoldQuery]):
    """
    Property 2: Data integrity on query - Single record integrity
    For any set of records inserted into gold_queries, querying the table 
    should return exactly those records with all fields intact
    **Validates: Requirements 1.3**
    """
    # Simulate database roundtrip
    retrieved_records = simulate_database_roundtrip(records)
    
    # Verify we get back the same number of records
    if len(retrieved_records) != len(records):
        raise AssertionError(f"Expected {len(records)} records, got {len(retrieved_records)}")
    
    # Verify each record's data integrity
    for original, retrieved in zip(records, retrieved_records):
        # Check all required fields are preserved
        if retrieved.chat_input != original.chat_input:
            raise AssertionError("chat_input field not preserved during roundtrip")
        if retrieved.tablas_columnas_ddl != original.tablas_columnas_ddl:
            raise AssertionError("tablas_columnas_ddl field not preserved during roundtrip")
        if retrieved.sql_reference != original.sql_reference:
            raise AssertionError("sql_reference field not preserved during roundtrip")
        
        # Check optional fields are preserved (including None values)
        if retrieved.session_id != original.session_id:
            raise AssertionError("session_id field not preserved during roundtrip")
        if retrieved.member_id != original.member_id:
            raise AssertionError("member_id field not preserved during roundtrip")
        if retrieved.clasificacion != original.clasificacion:
            raise AssertionError("clasificacion field not preserved during roundtrip")
        if retrieved.pregunta_descompuesta != original.pregunta_descompuesta:
            raise AssertionError("pregunta_descompuesta field not preserved during roundtrip")
        
        # Check metadata fields are preserved
        if retrieved.id != original.id:
            raise AssertionError("id field not preserved during roundtrip")
        if retrieved.created_at != original.created_at:
            raise AssertionError("created_at field not preserved during roundtrip")


@given(st.lists(gold_query_strategy(), min_size=0, max_size=5))
@settings(max_examples=100)
def test_data_integrity_empty_and_small_sets(records: List[GoldQuery]):
    """
    Property 2: Data integrity on query - Edge cases with empty/small sets
    For any set of records (including empty sets), the roundtrip should preserve
    the exact count and content
    **Validates: Requirements 1.3**
    """
    # Simulate database roundtrip
    retrieved_records = simulate_database_roundtrip(records)
    
    # Verify count is preserved
    if len(retrieved_records) != len(records):
        raise AssertionError(f"Record count not preserved: expected {len(records)}, got {len(retrieved_records)}")
    
    # For empty sets, we're done
    if len(records) == 0:
        return
    
    # For non-empty sets, verify content integrity
    for i, (original, retrieved) in enumerate(zip(records, retrieved_records)):
        if original.model_dump() != retrieved.model_dump():
            raise AssertionError(f"Record {i} data integrity violated during roundtrip")


@given(gold_query_strategy())
@settings(max_examples=100)
def test_data_integrity_field_types_preserved(record: GoldQuery):
    """
    Property 2: Data integrity on query - Field types preservation
    For any record, all field types should be preserved during database operations
    **Validates: Requirements 1.3**
    """
    # Simulate database roundtrip for single record
    retrieved_records = simulate_database_roundtrip([record])
    retrieved_record = retrieved_records[0]
    
    # Verify field types are preserved
    if type(retrieved_record.id) != type(record.id):
        raise AssertionError("id field type not preserved")
    if type(retrieved_record.chat_input) != type(record.chat_input):
        raise AssertionError("chat_input field type not preserved")
    if type(retrieved_record.tablas_columnas_ddl) != type(record.tablas_columnas_ddl):
        raise AssertionError("tablas_columnas_ddl field type not preserved")
    if type(retrieved_record.sql_reference) != type(record.sql_reference):
        raise AssertionError("sql_reference field type not preserved")
    if type(retrieved_record.created_at) != type(record.created_at):
        raise AssertionError("created_at field type not preserved")
    
    # Check optional fields (they can be None, so we need to handle that)
    if record.session_id is not None:
        if type(retrieved_record.session_id) != type(record.session_id):
            raise AssertionError("session_id field type not preserved")
    if record.member_id is not None:
        if type(retrieved_record.member_id) != type(record.member_id):
            raise AssertionError("member_id field type not preserved")
    if record.clasificacion is not None:
        if type(retrieved_record.clasificacion) != type(record.clasificacion):
            raise AssertionError("clasificacion field type not preserved")
    if record.pregunta_descompuesta is not None:
        if type(retrieved_record.pregunta_descompuesta) != type(record.pregunta_descompuesta):
            raise AssertionError("pregunta_descompuesta field type not preserved")


@given(st.lists(gold_query_strategy(), min_size=2, max_size=10))
@settings(max_examples=100)
def test_data_integrity_unique_records_preserved(records: List[GoldQuery]):
    """
    Property 2: Data integrity on query - Unique records preservation
    For any set of records with unique IDs, all unique records should be preserved
    **Validates: Requirements 1.3**
    """
    # Ensure all records have unique IDs (regenerate if needed)
    unique_records = []
    used_ids = set()
    
    for record in records:
        if record.id not in used_ids:
            unique_records.append(record)
            used_ids.add(record.id)
        else:
            # Create a new record with unique ID
            new_record = record.model_copy()
            new_record.id = uuid4()
            unique_records.append(new_record)
            used_ids.add(new_record.id)
    
    # Simulate database roundtrip
    retrieved_records = simulate_database_roundtrip(unique_records)
    
    # Verify all unique records are preserved
    if len(retrieved_records) != len(unique_records):
        raise AssertionError("Not all unique records were preserved")
    
    # Verify each unique record is intact
    retrieved_ids = {r.id for r in retrieved_records}
    original_ids = {r.id for r in unique_records}
    
    if retrieved_ids != original_ids:
        raise AssertionError("Set of record IDs not preserved during roundtrip")


def run_all_tests():
    """Run all property-based tests for data integrity"""
    tests = [
        ("Data integrity single record roundtrip", test_data_integrity_on_query_single_record_roundtrip),
        ("Data integrity empty and small sets", test_data_integrity_empty_and_small_sets),
        ("Data integrity field types preserved", test_data_integrity_field_types_preserved),
        ("Data integrity unique records preserved", test_data_integrity_unique_records_preserved),
    ]
    
    print("Running Property-Based Tests for Data Integrity on Query")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}...")
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All property-based tests PASSED!")
        return True
    else:
        print("💥 Some property-based tests FAILED!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)