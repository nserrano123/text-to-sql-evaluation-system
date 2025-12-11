"""Property-based tests for required field validation"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError
from backend.app.models.gold_query import GoldQueryCreate
from uuid import uuid4
from datetime import datetime


# **Feature: text-to-sql-evaluation, Property 1: Required field validation**

# Strategy for generating valid strings
valid_string_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())

# Strategy for generating optional strings
optional_string_strategy = st.one_of(st.none(), st.text(max_size=255))

# Strategy for generating invalid (empty/whitespace) strings
invalid_string_strategy = st.one_of(
    st.just(""),  # Empty string
    st.text(alphabet=" \t\n\r\f\v", min_size=1, max_size=50)  # Whitespace-only strings
)


@given(
    chat_input=invalid_string_strategy,
    tablas_columnas_ddl=valid_string_strategy,
    sql_reference=valid_string_strategy,
    session_id=optional_string_strategy,
    member_id=optional_string_strategy,
    clasificacion=optional_string_strategy,
    pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000))
)
@settings(max_examples=100)
def test_missing_chat_input_rejected(
    chat_input, tablas_columnas_ddl, sql_reference, 
    session_id, member_id, clasificacion, pregunta_descompuesta
):
    """
    Property 1: Required field validation - chat_input
    For any attempt to create a GoldQuery with missing/empty chat_input, 
    the creation should be rejected with ValidationError
    **Validates: Requirements 1.2**
    """
    with pytest.raises(ValidationError) as exc_info:
        GoldQueryCreate(
            chat_input=chat_input,
            session_id=session_id,
            member_id=member_id,
            clasificacion=clasificacion,
            pregunta_descompuesta=pregunta_descompuesta,
            tablas_columnas_ddl=tablas_columnas_ddl,
            sql_reference=sql_reference
        )
    
    # Verify that the error is related to chat_input field
    errors = exc_info.value.errors()
    chat_input_errors = [error for error in errors if 'chat_input' in str(error.get('loc', []))]
    assert len(chat_input_errors) > 0, "Expected validation error for chat_input field"


@given(
    chat_input=valid_string_strategy,
    tablas_columnas_ddl=invalid_string_strategy,
    sql_reference=valid_string_strategy,
    session_id=optional_string_strategy,
    member_id=optional_string_strategy,
    clasificacion=optional_string_strategy,
    pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000))
)
@settings(max_examples=100)
def test_missing_tablas_columnas_ddl_rejected(
    chat_input, tablas_columnas_ddl, sql_reference,
    session_id, member_id, clasificacion, pregunta_descompuesta
):
    """
    Property 1: Required field validation - tablas_columnas_ddl
    For any attempt to create a GoldQuery with missing/empty tablas_columnas_ddl,
    the creation should be rejected with ValidationError
    **Validates: Requirements 1.2**
    """
    with pytest.raises(ValidationError) as exc_info:
        GoldQueryCreate(
            chat_input=chat_input,
            session_id=session_id,
            member_id=member_id,
            clasificacion=clasificacion,
            pregunta_descompuesta=pregunta_descompuesta,
            tablas_columnas_ddl=tablas_columnas_ddl,
            sql_reference=sql_reference
        )
    
    # Verify that the error is related to tablas_columnas_ddl field
    errors = exc_info.value.errors()
    ddl_errors = [error for error in errors if 'tablas_columnas_ddl' in str(error.get('loc', []))]
    assert len(ddl_errors) > 0, "Expected validation error for tablas_columnas_ddl field"


@given(
    chat_input=valid_string_strategy,
    tablas_columnas_ddl=valid_string_strategy,
    sql_reference=invalid_string_strategy,
    session_id=optional_string_strategy,
    member_id=optional_string_strategy,
    clasificacion=optional_string_strategy,
    pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000))
)
@settings(max_examples=100)
def test_missing_sql_reference_rejected(
    chat_input, tablas_columnas_ddl, sql_reference,
    session_id, member_id, clasificacion, pregunta_descompuesta
):
    """
    Property 1: Required field validation - sql_reference
    For any attempt to create a GoldQuery with missing/empty sql_reference,
    the creation should be rejected with ValidationError
    **Validates: Requirements 1.2**
    """
    with pytest.raises(ValidationError) as exc_info:
        GoldQueryCreate(
            chat_input=chat_input,
            session_id=session_id,
            member_id=member_id,
            clasificacion=clasificacion,
            pregunta_descompuesta=pregunta_descompuesta,
            tablas_columnas_ddl=tablas_columnas_ddl,
            sql_reference=sql_reference
        )
    
    # Verify that the error is related to sql_reference field
    errors = exc_info.value.errors()
    sql_errors = [error for error in errors if 'sql_reference' in str(error.get('loc', []))]
    assert len(sql_errors) > 0, "Expected validation error for sql_reference field"


@given(
    chat_input=valid_string_strategy,
    tablas_columnas_ddl=valid_string_strategy,
    sql_reference=valid_string_strategy,
    session_id=optional_string_strategy,
    member_id=optional_string_strategy,
    clasificacion=optional_string_strategy,
    pregunta_descompuesta=st.one_of(st.none(), st.text(max_size=1000))
)
@settings(max_examples=100)
def test_valid_required_fields_accepted(
    chat_input, tablas_columnas_ddl, sql_reference,
    session_id, member_id, clasificacion, pregunta_descompuesta
):
    """
    Property 1: Required field validation - positive case
    For any attempt to create a GoldQuery with all required fields present and valid,
    the creation should succeed
    **Validates: Requirements 1.2**
    """
    # This should not raise any exception
    gold_query = GoldQueryCreate(
        chat_input=chat_input,
        session_id=session_id,
        member_id=member_id,
        clasificacion=clasificacion,
        pregunta_descompuesta=pregunta_descompuesta,
        tablas_columnas_ddl=tablas_columnas_ddl,
        sql_reference=sql_reference
    )
    
    # Verify the fields are set correctly
    assert gold_query.chat_input == chat_input
    assert gold_query.tablas_columnas_ddl == tablas_columnas_ddl
    assert gold_query.sql_reference == sql_reference
    assert gold_query.session_id == session_id
    assert gold_query.member_id == member_id
    assert gold_query.clasificacion == clasificacion
    assert gold_query.pregunta_descompuesta == pregunta_descompuesta