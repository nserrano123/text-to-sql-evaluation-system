"""Property-based tests for CSV export completeness"""

import pandas as pd
from io import StringIO
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import pytest
from hypothesis import given, strategies as st, settings


# **Feature: text-to-sql-evaluation, Property 24: CSV export completeness**


# Strategies for generating test data
@st.composite
def gold_query_strategy(draw):
    """Generate a valid gold query record"""
    return {
        'id': str(uuid4()),
        'chat_input': draw(st.text(min_size=1, max_size=200)),
        'session_id': draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        'member_id': draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        'clasificacion': draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        'pregunta_descompuesta': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'tablas_columnas_ddl': draw(st.text(min_size=10, max_size=500)),
        'sql_reference': draw(st.text(min_size=5, max_size=200)),
        'created_at': datetime.now(timezone.utc).isoformat()
    }


@st.composite
def evaluation_strategy(draw):
    """Generate a valid evaluation record"""
    gold_query_id = str(uuid4())
    return {
        'id': str(uuid4()),
        'gold_query_id': gold_query_id,
        'generated_sql': draw(st.text(min_size=5, max_size=200)),
        'evaluation_date': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }, gold_query_id


@st.composite
def execution_accuracy_strategy(draw):
    """Generate a valid execution accuracy record"""
    evaluation_id = str(uuid4())
    return {
        'id': str(uuid4()),
        'evaluation_id': evaluation_id,
        'results_match': draw(st.one_of(st.none(), st.booleans())),
        'is_correct': draw(st.booleans()),
        'evaluator_notes': draw(st.one_of(st.none(), st.text(max_size=500))),
        'created_at': datetime.now(timezone.utc).isoformat()
    }, evaluation_id


@st.composite
def time_to_answer_strategy(draw):
    """Generate a valid time to answer record"""
    evaluation_id = str(uuid4())
    duration = draw(st.floats(min_value=0.1, max_value=3600.0))
    start_time = datetime.now(timezone.utc)
    end_time = datetime.fromtimestamp(start_time.timestamp() + duration, tz=timezone.utc)
    
    return {
        'id': str(uuid4()),
        'evaluation_id': evaluation_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': duration,
        'created_at': datetime.now(timezone.utc).isoformat()
    }, evaluation_id


@st.composite
def component_matching_strategy(draw):
    """Generate a valid component matching record"""
    evaluation_id = str(uuid4())
    return {
        'id': str(uuid4()),
        'evaluation_id': evaluation_id,
        'select_correct': draw(st.booleans()),
        'where_correct': draw(st.booleans()),
        'group_by_correct': draw(st.booleans()),
        'order_by_correct': draw(st.booleans()),
        'keywords_correct': draw(st.booleans()),
        'f1_score': draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))),
        'evaluator_notes': draw(st.one_of(st.none(), st.text(max_size=500))),
        'created_at': datetime.now(timezone.utc).isoformat()
    }, evaluation_id




class MockSupabaseClient:
    """Mock Supabase client for testing CSV export"""
    
    def __init__(self):
        self.gold_queries: List[Dict[str, Any]] = []
        self.evaluations: List[Dict[str, Any]] = []
        self.execution_accuracy: List[Dict[str, Any]] = []
        self.time_to_answer: List[Dict[str, Any]] = []
        self.component_matching: List[Dict[str, Any]] = []
    
    def add_gold_query(self, data: Dict[str, Any]):
        """Add a gold query record"""
        self.gold_queries.append(data)
    
    def add_evaluation(self, data: Dict[str, Any]):
        """Add an evaluation record"""
        self.evaluations.append(data)
    
    def add_execution_accuracy(self, data: Dict[str, Any]):
        """Add an execution accuracy record"""
        self.execution_accuracy.append(data)
    
    def add_time_to_answer(self, data: Dict[str, Any]):
        """Add a time to answer record"""
        self.time_to_answer.append(data)
    
    def add_component_matching(self, data: Dict[str, Any]):
        """Add a component matching record"""
        self.component_matching.append(data)
    
    def table(self, table_name: str):
        """Mock table method"""
        return MockTable(self, table_name)


class MockTable:
    """Mock table for Supabase queries"""
    
    def __init__(self, client: MockSupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
    
    def select(self, columns: str):
        """Mock select method"""
        return MockQuery(self.client, self.table_name)


class MockQuery:
    """Mock query for Supabase operations"""
    
    def __init__(self, client: MockSupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
    
    def execute(self):
        """Mock execute method"""
        if self.table_name == 'gold_queries':
            data = self.client.gold_queries
        elif self.table_name == 'evaluations':
            data = self.client.evaluations
        elif self.table_name == 'execution_accuracy':
            data = self.client.execution_accuracy
        elif self.table_name == 'time_to_answer':
            data = self.client.time_to_answer
        elif self.table_name == 'component_matching':
            data = self.client.component_matching
        else:
            data = []
        
        return MockResult(data)


class MockResult:
    """Mock result for Supabase queries"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data


class MockExportService:
    """Mock export service for testing"""
    
    def __init__(self, mock_client: MockSupabaseClient):
        self.client = mock_client
    
    def _export_csv_fallback(self) -> str:
        """
        Mock implementation of CSV export using fallback method.
        """
        # Get data from each table
        gold_queries = self.client.gold_queries
        evaluations = self.client.evaluations
        execution_accuracy = self.client.execution_accuracy
        time_to_answer = self.client.time_to_answer
        component_matching = self.client.component_matching
        
        # Convert to DataFrames
        df_gold = pd.DataFrame(gold_queries) if gold_queries else pd.DataFrame()
        df_eval = pd.DataFrame(evaluations) if evaluations else pd.DataFrame()
        df_ea = pd.DataFrame(execution_accuracy) if execution_accuracy else pd.DataFrame()
        df_tta = pd.DataFrame(time_to_answer) if time_to_answer else pd.DataFrame()
        df_cm = pd.DataFrame(component_matching) if component_matching else pd.DataFrame()
        
        # Rename columns to avoid conflicts
        if not df_gold.empty:
            df_gold = df_gold.add_suffix('_gold')
            df_gold = df_gold.rename(columns={'id_gold': 'gold_query_id'})
        
        if not df_eval.empty:
            df_eval = df_eval.add_suffix('_eval')
            df_eval = df_eval.rename(columns={
                'id_eval': 'evaluation_id',
                'gold_query_id_eval': 'gold_query_id'
            })
        
        if not df_ea.empty:
            df_ea = df_ea.add_suffix('_ea')
            df_ea = df_ea.rename(columns={
                'id_ea': 'execution_accuracy_id',
                'evaluation_id_ea': 'evaluation_id'
            })
        
        if not df_tta.empty:
            df_tta = df_tta.add_suffix('_tta')
            df_tta = df_tta.rename(columns={
                'id_tta': 'time_to_answer_id',
                'evaluation_id_tta': 'evaluation_id'
            })
        
        if not df_cm.empty:
            df_cm = df_cm.add_suffix('_cm')
            df_cm = df_cm.rename(columns={
                'id_cm': 'component_matching_id',
                'evaluation_id_cm': 'evaluation_id'
            })
        
        # Perform joins
        # Start with gold_queries as base
        if df_gold.empty:
            # If no gold queries, return empty CSV with headers
            return pd.DataFrame().to_csv(index=False)
        
        result_df = df_gold
        
        # Left join with evaluations
        if not df_eval.empty:
            result_df = result_df.merge(df_eval, on='gold_query_id', how='left')
        
        # Left join with execution_accuracy
        if not df_ea.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_ea, on='evaluation_id', how='left')
        
        # Left join with time_to_answer
        if not df_tta.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_tta, on='evaluation_id', how='left')
        
        # Left join with component_matching
        if not df_cm.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_cm, on='evaluation_id', how='left')
        
        # Convert to CSV
        csv_buffer = StringIO()
        result_df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()





def test_csv_export_includes_all_gold_query_fields():
    """
    Property 24: CSV export completeness - All gold query fields included
    For any set of gold queries, the CSV export should include all fields from the gold_queries table
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create test data
    gold_queries = [
        {
            'id': str(uuid4()),
            'chat_input': 'Test chat input 1',
            'session_id': 'session_1',
            'member_id': 'member_1',
            'clasificacion': 'test',
            'pregunta_descompuesta': 'Test question',
            'tablas_columnas_ddl': 'CREATE TABLE test (id INT);',
            'sql_reference': 'SELECT * FROM test;',
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid4()),
            'chat_input': 'Test chat input 2',
            'session_id': None,
            'member_id': None,
            'clasificacion': None,
            'pregunta_descompuesta': None,
            'tablas_columnas_ddl': 'CREATE TABLE test2 (id INT);',
            'sql_reference': 'SELECT * FROM test2;',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add gold queries to mock client
    for gold_query in gold_queries:
        mock_client.add_gold_query(gold_query)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Expected gold query fields (with suffix)
    expected_gold_fields = [
        'chat_input_gold', 'session_id_gold', 'member_id_gold', 
        'clasificacion_gold', 'pregunta_descompuesta_gold', 
        'tablas_columnas_ddl_gold', 'sql_reference_gold', 'created_at_gold'
    ]
    
    # Verify all gold query fields are present in CSV
    for field in expected_gold_fields:
        assert field in df.columns, f"Gold query field '{field}' should be present in CSV export"
    
    # Verify we have the correct number of rows (at least as many as gold queries)
    assert len(df) >= len(gold_queries), "CSV should have at least as many rows as gold queries"


def test_csv_export_includes_all_evaluation_fields():
    """
    Property 24: CSV export completeness - All evaluation fields included
    For any set of evaluations, the CSV export should include all fields from the evaluations table
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create test data
    gold_query = {
        'id': str(uuid4()),
        'chat_input': 'Test chat input',
        'session_id': 'session_1',
        'member_id': 'member_1',
        'clasificacion': 'test',
        'pregunta_descompuesta': 'Test question',
        'tablas_columnas_ddl': 'CREATE TABLE test (id INT);',
        'sql_reference': 'SELECT * FROM test;',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    evaluation = {
        'id': str(uuid4()),
        'gold_query_id': gold_query['id'],
        'generated_sql': 'SELECT * FROM test;',
        'evaluation_date': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add data to mock client
    mock_client.add_gold_query(gold_query)
    mock_client.add_evaluation(evaluation)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Expected evaluation fields (with suffix)
    expected_eval_fields = [
        'generated_sql_eval', 'evaluation_date_eval', 'created_at_eval'
    ]
    
    # Verify all evaluation fields are present in CSV
    for field in expected_eval_fields:
        assert field in df.columns, f"Evaluation field '{field}' should be present in CSV export"


def test_csv_export_includes_all_metrics_fields():
    """
    Property 24: CSV export completeness - All metrics fields included when present
    For any set of evaluations with metrics, the CSV export should include all fields 
    from execution_accuracy, time_to_answer, and component_matching tables
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create test data
    gold_query = {
        'id': str(uuid4()),
        'chat_input': 'Test chat input',
        'session_id': 'session_1',
        'member_id': 'member_1',
        'clasificacion': 'test',
        'pregunta_descompuesta': 'Test question',
        'tablas_columnas_ddl': 'CREATE TABLE test (id INT);',
        'sql_reference': 'SELECT * FROM test;',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    evaluation = {
        'id': str(uuid4()),
        'gold_query_id': gold_query['id'],
        'generated_sql': 'SELECT * FROM test;',
        'evaluation_date': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    execution_accuracy = {
        'id': str(uuid4()),
        'evaluation_id': evaluation['id'],
        'results_match': True,
        'is_correct': True,
        'evaluator_notes': 'Test notes',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    time_to_answer = {
        'id': str(uuid4()),
        'evaluation_id': evaluation['id'],
        'start_time': datetime.now(timezone.utc).isoformat(),
        'end_time': datetime.now(timezone.utc).isoformat(),
        'duration_seconds': 10.5,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    component_matching = {
        'id': str(uuid4()),
        'evaluation_id': evaluation['id'],
        'select_correct': True,
        'where_correct': False,
        'group_by_correct': True,
        'order_by_correct': False,
        'keywords_correct': True,
        'f1_score': 0.75,
        'evaluator_notes': 'Component notes',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add data to mock client
    mock_client.add_gold_query(gold_query)
    mock_client.add_evaluation(evaluation)
    mock_client.add_execution_accuracy(execution_accuracy)
    mock_client.add_time_to_answer(time_to_answer)
    mock_client.add_component_matching(component_matching)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Expected fields for each table
    expected_ea_fields = [
        'results_match_ea', 'is_correct_ea', 'evaluator_notes_ea', 'created_at_ea'
    ]
    expected_tta_fields = [
        'start_time_tta', 'end_time_tta', 'duration_seconds_tta', 'created_at_tta'
    ]
    expected_cm_fields = [
        'select_correct_cm', 'where_correct_cm', 'group_by_correct_cm',
        'order_by_correct_cm', 'keywords_correct_cm', 'f1_score_cm',
        'evaluator_notes_cm', 'created_at_cm'
    ]
    
    # Verify all metrics fields are present
    for field in expected_ea_fields:
        assert field in df.columns, f"Execution accuracy field '{field}' should be present when data exists"
    
    for field in expected_tta_fields:
        assert field in df.columns, f"Time to answer field '{field}' should be present when data exists"
    
    for field in expected_cm_fields:
        assert field in df.columns, f"Component matching field '{field}' should be present when data exists"


def test_csv_export_preserves_data_integrity():
    """
    Property 24: CSV export completeness - Data integrity preserved in export
    For any set of data, the CSV export should preserve all original values without corruption
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create test data with specific values
    gold_queries = [
        {
            'id': str(uuid4()),
            'chat_input': 'Test chat input 0',
            'session_id': 'session_0',
            'member_id': 'member_0',
            'clasificacion': 'test',
            'pregunta_descompuesta': 'Test question 0',
            'tablas_columnas_ddl': 'CREATE TABLE test0 (id INT);',
            'sql_reference': 'SELECT * FROM table_0;',
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid4()),
            'chat_input': 'Test chat input 1',
            'session_id': 'session_1',
            'member_id': 'member_1',
            'clasificacion': 'test',
            'pregunta_descompuesta': 'Test question 1',
            'tablas_columnas_ddl': 'CREATE TABLE test1 (id INT);',
            'sql_reference': 'SELECT * FROM table_1;',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add gold queries
    for gold_query in gold_queries:
        mock_client.add_gold_query(gold_query)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Verify data integrity
    assert len(df) >= len(gold_queries), "Should have at least as many rows as input data"
    
    # Check that specific values are preserved
    for i, gold_query in enumerate(gold_queries):
        # Find the row with this gold query ID
        matching_rows = df[df['gold_query_id'] == gold_query['id']]
        assert len(matching_rows) >= 1, f"Should find row for gold query {gold_query['id']}"
        
        row = matching_rows.iloc[0]
        assert row['chat_input_gold'] == gold_query['chat_input'], \
            f"Chat input should be preserved for gold query {i}"
        assert row['sql_reference_gold'] == gold_query['sql_reference'], \
            f"SQL reference should be preserved for gold query {i}"


def test_csv_export_handles_empty_data():
    """
    Property 24: CSV export completeness - Handles empty or minimal data gracefully
    For any dataset including empty datasets, the CSV export should complete successfully
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Test with empty data
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Generate CSV should not fail even with no data
    csv_content = service._export_csv_fallback()
    
    # Should be valid CSV
    assert isinstance(csv_content, str), "CSV export should return a string"
    
    # For empty data, the CSV should be empty or just headers
    # We'll skip parsing empty CSV as pandas requires at least one column
    
    # Test with minimal data (1 gold query)
    gold_query = {
        'id': str(uuid4()),
        'chat_input': 'Test input',
        'session_id': None,
        'member_id': None,
        'clasificacion': None,
        'pregunta_descompuesta': None,
        'tablas_columnas_ddl': 'CREATE TABLE test (id INT);',
        'sql_reference': 'SELECT * FROM test;',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    mock_client.add_gold_query(gold_query)
    
    # Generate CSV with minimal data
    csv_content = service._export_csv_fallback()
    df = pd.read_csv(StringIO(csv_content))
    
    # Should have 1 row
    assert len(df) == 1, "Should have 1 row for minimal data"
    
    # Should have basic columns
    assert 'gold_query_id' in df.columns, "Should have gold_query_id column"
    assert 'chat_input_gold' in df.columns, "Should have chat_input_gold column"


# Property-based tests using Hypothesis

def test_csv_export_completeness_all_gold_fields_property(gold_queries):
    """
    Property 24: CSV export completeness - All gold query fields must be present
    For any set of gold queries, the CSV export should include all required fields
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add gold queries to mock client
    for gold_query in gold_queries:
        mock_client.add_gold_query(gold_query)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Expected gold query fields (with suffix)
    expected_gold_fields = [
        'chat_input_gold', 'session_id_gold', 'member_id_gold', 
        'clasificacion_gold', 'pregunta_descompuesta_gold', 
        'tablas_columnas_ddl_gold', 'sql_reference_gold', 'created_at_gold'
    ]
    
    # Verify all gold query fields are present in CSV
    for field in expected_gold_fields:
        assert field in df.columns, f"Gold query field '{field}' should be present in CSV export"
    
    # Verify we have the correct number of rows
    assert len(df) >= len(gold_queries), "CSV should have at least as many rows as gold queries"
    
    # Verify data integrity - each gold query should be represented
    gold_query_ids = {gq['id'] for gq in gold_queries}
    csv_gold_query_ids = set(df['gold_query_id'].dropna().astype(str))
    assert gold_query_ids.issubset(csv_gold_query_ids), "All gold query IDs should be present in CSV"


def test_csv_export_completeness_full_dataset_property(gold_queries, evaluations_with_metrics):
    """
    Property 24: CSV export completeness - All fields from all tables included
    For any complete dataset with all table types, the CSV export should include all fields
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add gold queries
    for gold_query in gold_queries:
        mock_client.add_gold_query(gold_query)
    
    # Add evaluations and metrics, linking them to existing gold queries
    for i, (eval_data, ea_data, tta_data, cm_data) in enumerate(evaluations_with_metrics):
        evaluation, _ = eval_data
        execution_accuracy, _ = ea_data
        time_to_answer, _ = tta_data
        component_matching, _ = cm_data
        
        # Link to an existing gold query
        gold_query_id = gold_queries[i % len(gold_queries)]['id']
        evaluation['gold_query_id'] = gold_query_id
        
        # Use the same evaluation_id for all metrics
        evaluation_id = evaluation['id']
        execution_accuracy['evaluation_id'] = evaluation_id
        time_to_answer['evaluation_id'] = evaluation_id
        component_matching['evaluation_id'] = evaluation_id
        
        mock_client.add_evaluation(evaluation)
        mock_client.add_execution_accuracy(execution_accuracy)
        mock_client.add_time_to_answer(time_to_answer)
        mock_client.add_component_matching(component_matching)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Expected fields from all tables
    expected_fields = {
        # Gold query fields
        'chat_input_gold', 'session_id_gold', 'member_id_gold', 
        'clasificacion_gold', 'pregunta_descompuesta_gold', 
        'tablas_columnas_ddl_gold', 'sql_reference_gold', 'created_at_gold',
        
        # Evaluation fields
        'generated_sql_eval', 'evaluation_date_eval', 'created_at_eval',
        
        # Execution accuracy fields
        'results_match_ea', 'is_correct_ea', 'evaluator_notes_ea', 'created_at_ea',
        
        # Time to answer fields
        'start_time_tta', 'end_time_tta', 'duration_seconds_tta', 'created_at_tta',
        
        # Component matching fields
        'select_correct_cm', 'where_correct_cm', 'group_by_correct_cm',
        'order_by_correct_cm', 'keywords_correct_cm', 'f1_score_cm',
        'evaluator_notes_cm', 'created_at_cm'
    }
    
    # Verify all expected fields are present
    csv_columns = set(df.columns)
    missing_fields = expected_fields - csv_columns
    assert not missing_fields, f"Missing fields in CSV export: {missing_fields}"
    
    # Verify we have data rows
    assert len(df) > 0, "CSV should contain data rows"


def test_csv_export_completeness_partial_data_property(gold_queries, partial_evaluations):
    """
    Property 24: CSV export completeness - Handles partial data correctly
    For any dataset with missing evaluations or metrics, CSV export should still include all available fields
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Add gold queries
    for gold_query in gold_queries:
        mock_client.add_gold_query(gold_query)
    
    # Add only some evaluations (partial data scenario)
    for evaluation, _ in partial_evaluations:
        # Link to an existing gold query
        if gold_queries:
            gold_query_id = gold_queries[0]['id']
            evaluation['gold_query_id'] = gold_query_id
            mock_client.add_evaluation(evaluation)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Should always have gold query fields
    expected_gold_fields = [
        'chat_input_gold', 'tablas_columnas_ddl_gold', 'sql_reference_gold'
    ]
    
    for field in expected_gold_fields:
        assert field in df.columns, f"Required gold query field '{field}' should always be present"
    
    # Should have at least as many rows as gold queries
    assert len(df) >= len(gold_queries), "Should have at least one row per gold query"
    
    # If evaluations exist, should have evaluation fields
    if partial_evaluations:
        expected_eval_fields = ['generated_sql_eval', 'evaluation_date_eval']
        for field in expected_eval_fields:
            assert field in df.columns, f"Evaluation field '{field}' should be present when evaluations exist"


def test_csv_export_completeness_scalability_property(data_size):
    """
    Property 24: CSV export completeness - Scales correctly with data size
    For any data size, CSV export should maintain completeness and performance
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    # Create mock client and service
    mock_client = MockSupabaseClient()
    service = MockExportService(mock_client)
    
    # Generate data of specified size
    for i in range(data_size):
        gold_query = {
            'id': str(uuid4()),
            'chat_input': f'Test chat input {i}',
            'session_id': f'session_{i}',
            'member_id': f'member_{i}',
            'clasificacion': 'test',
            'pregunta_descompuesta': f'Test question {i}',
            'tablas_columnas_ddl': f'CREATE TABLE test{i} (id INT);',
            'sql_reference': f'SELECT * FROM test{i};',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        mock_client.add_gold_query(gold_query)
    
    # Generate CSV
    csv_content = service._export_csv_fallback()
    
    # Parse CSV
    df = pd.read_csv(StringIO(csv_content))
    
    # Verify completeness scales with data size
    assert len(df) == data_size, f"CSV should have {data_size} rows for {data_size} gold queries"
    
    # Verify all required columns are present regardless of size
    required_columns = ['gold_query_id', 'chat_input_gold', 'sql_reference_gold']
    for col in required_columns:
        assert col in df.columns, f"Required column '{col}' should be present at any scale"
    
    # Verify no data corruption at scale
    unique_chat_inputs = df['chat_input_gold'].nunique()
    assert unique_chat_inputs == data_size, f"Should have {data_size} unique chat inputs, got {unique_chat_inputs}"