#!/usr/bin/env python3
"""Script para agregar datos de prueba N8n a una consulta existente"""

import asyncio
import os
from app.database import get_database
from app.repositories.gold_query_repository import GoldQueryRepository

async def add_n8n_test_data():
    """Agregar datos N8n de prueba a la primera consulta disponible"""
    
    # Obtener conexión a la base de datos
    db = await get_database()
    repo = GoldQueryRepository(db)
    
    try:
        # Obtener todas las consultas
        queries = await repo.get_all()
        
        if not queries:
            print("❌ No hay consultas disponibles")
            return
            
        # Tomar la primera consulta
        query = queries[0]
        print(f"📝 Actualizando consulta: {query.id}")
        print(f"   Consulta: {query.chat_input[:50]}...")
        
        # Datos N8n de ejemplo
        n8n_sql_generated = """
SELECT 
    t.geographic_location_id,
    SUM(i.total_amount) as total_amount_sum,
    COUNT(*) as record_count
FROM tax.directive t
JOIN account_payable.invoice_detail i 
    ON t.member_id = i.member_id 
    AND t.geographic_location_id = i.geographic_location_id
WHERE t.member_id = $1
GROUP BY t.geographic_location_id
ORDER BY total_amount_sum DESC
LIMIT 50;
        """.strip()
        
        n8n_din_sql = """
WITH base_data AS (
    SELECT 
        td.member_id,
        td.geographic_location_id,
        aid.total_amount
    FROM tax.directive td
    INNER JOIN account_payable.invoice_detail aid
        ON td.member_id = aid.member_id
        AND td.geographic_location_id = aid.geographic_location_id
    WHERE td.member_id = $1
)
SELECT 
    geographic_location_id,
    SUM(total_amount) AS suma_total_amount,
    COUNT(*) AS numero_registros
FROM base_data
GROUP BY geographic_location_id
ORDER BY suma_total_amount DESC
LIMIT 50;
        """.strip()
        
        n8n_llm_response = """
Análisis de la consulta:

1. **Objetivo**: Combinar las tablas tax.directive y account_payable.invoice_detail para obtener estadísticas por geographic_location_id.

2. **Estrategia**: 
   - Usar JOIN entre las tablas basado en member_id y geographic_location_id
   - Filtrar por member_id específico
   - Agrupar por geographic_location_id
   - Calcular SUM del campo total_amount y COUNT de registros

3. **Consideraciones**:
   - Se usa LIMIT 50 para evitar resultados muy grandes
   - ORDER BY descendente para mostrar los valores más altos primero
   - El parámetro $1 representa el member_id del usuario actual

4. **Resultado esperado**: Lista de ubicaciones geográficas con sus totales y conteos correspondientes.
        """.strip()
        
        # Actualizar la consulta con datos N8n
        await db.execute("""
            UPDATE gold_queries 
            SET 
                n8n_sql_generated = $1,
                n8n_din_sql = $2,
                n8n_llm_response = $3
            WHERE id = $4
        """, n8n_sql_generated, n8n_din_sql, n8n_llm_response, query.id)
        
        print("✅ Datos N8n agregados exitosamente")
        print(f"   - N8n SQL Generated: {len(n8n_sql_generated)} caracteres")
        print(f"   - N8n DIN SQL: {len(n8n_din_sql)} caracteres") 
        print(f"   - N8n LLM Response: {len(n8n_llm_response)} caracteres")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(add_n8n_test_data())