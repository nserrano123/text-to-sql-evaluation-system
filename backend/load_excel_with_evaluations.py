#!/usr/bin/env python3
"""
Script para cargar datos de gold queries Y crear evaluaciones automáticamente
desde un archivo Excel que ya tiene consultas generadas por IA
"""

import pandas as pd
import requests
import json
import sys
from pathlib import Path
import time

# Configuración
API_BASE_URL = "http://localhost:8001"

def load_excel_with_evaluations(excel_file_path):
    """
    Carga gold queries y crea evaluaciones automáticamente desde Excel
    """
    
    if not Path(excel_file_path).exists():
        print(f"❌ Error: No se encuentra el archivo {excel_file_path}")
        return False
    
    try:
        # Leer Excel
        print(f"📖 Leyendo archivo Excel: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        print(f"📊 Encontradas {len(df)} filas")
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        
        # Mapeo de columnas específico para tu Excel
        column_mapping = {
            # Para gold queries
            'chatInput': 'chat_input',
            'SQL': 'sql_reference', 
            'Tablas y columnas (DDL)': 'tablas_columnas_ddl',
            'sessionId': 'session_id',
            'member_id': 'member_id',
            'Clasificacion': 'clasificacion',
            'Pregunta Descompuesta': 'pregunta_descompuesta',
            
            # Para evaluaciones
            'N8nSqlGenerated': 'generated_sql'  # La consulta generada por IA
        }
        
        # Verificar columnas requeridas
        required_fields = ['chatInput', 'SQL', 'Tablas y columnas (DDL)']
        missing_required = [field for field in required_fields if field not in df.columns]
        if missing_required:
            print(f"❌ Error: Faltan columnas requeridas: {missing_required}")
            return False
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 1. Preparar datos para gold query
                gold_query_data = {}
                
                for excel_col, api_field in column_mapping.items():
                    if excel_col in df.columns and api_field != 'generated_sql':
                        value = row[excel_col]
                        if pd.notna(value):
                            gold_query_data[api_field] = str(value).strip()
                
                # Verificar campos requeridos para gold query
                required_api_fields = ['chat_input', 'sql_reference', 'tablas_columnas_ddl']
                if not all(gold_query_data.get(field) for field in required_api_fields):
                    print(f"⚠️  Fila {index + 1}: Faltan campos requeridos para gold query, saltando...")
                    error_count += 1
                    continue
                
                # 2. Crear gold query
                print(f"📝 Fila {index + 1}: Creando gold query...")
                response = requests.post(
                    f"{API_BASE_URL}/api/gold-queries",
                    json=gold_query_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"❌ Fila {index + 1}: Error creando gold query - {response.status_code}: {response.text}")
                    error_count += 1
                    continue
                
                gold_query_response = response.json()
                gold_query_id = gold_query_response['id']
                print(f"✅ Fila {index + 1}: Gold query creada con ID: {gold_query_id}")
                
                # 3. Crear evaluación si hay consulta generada
                if 'N8nSqlGenerated' in df.columns and pd.notna(row['N8nSqlGenerated']):
                    generated_sql = str(row['N8nSqlGenerated']).strip()
                    
                    if generated_sql:
                        print(f"🤖 Fila {index + 1}: Creando evaluación con consulta generada...")
                        
                        # Datos para la evaluación
                        evaluation_data = {
                            "gold_query_id": gold_query_id,
                            "generated_sql": generated_sql,
                            "execution_accuracy": {
                                "isCorrect": False,  # Por defecto, necesitará evaluación manual
                                "evaluatorNotes": "Cargado desde Excel - Requiere evaluación manual"
                            },
                            "time_to_answer": {
                                "startTime": "2024-01-01T00:00:00Z",  # Placeholder
                                "endTime": "2024-01-01T00:00:01Z",    # Placeholder
                                "durationSeconds": 1.0
                            },
                            "component_matching": {
                                "selectCorrect": False,
                                "whereCorrect": False,
                                "groupByCorrect": False,
                                "orderByCorrect": False,
                                "keywordsCorrect": False,
                                "f1Score": 0.0,
                                "evaluatorNotes": "Cargado desde Excel - Requiere evaluación manual"
                            }
                        }
                        
                        eval_response = requests.post(
                            f"{API_BASE_URL}/api/evaluations",
                            json=evaluation_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if eval_response.status_code == 200:
                            print(f"✅ Fila {index + 1}: Evaluación creada (requiere evaluación manual)")
                        else:
                            print(f"⚠️  Fila {index + 1}: Error creando evaluación - {eval_response.status_code}: {eval_response.text}")
                
                success_count += 1
                time.sleep(0.1)  # Pequeña pausa para no sobrecargar la API
                
            except Exception as e:
                error_count += 1
                print(f"❌ Fila {index + 1}: Error - {str(e)}")
        
        print(f"\n📊 Resumen:")
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📈 Total procesadas: {success_count + error_count}")
        
        if success_count > 0:
            print(f"\n🎉 ¡Datos cargados exitosamente!")
            print(f"🌐 Ve a http://localhost:3000/evaluation para evaluar las consultas")
            print(f"📊 Ve a http://localhost:3000/dashboard para ver el progreso")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📖 Uso:")
        print(f"   python {sys.argv[0]} <archivo.xlsx>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    # Verificar que el backend esté ejecutándose
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ El backend no está respondiendo. Asegúrate de que esté ejecutándose en puerto 8001")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend. Asegúrate de que esté ejecutándose en puerto 8001")
        sys.exit(1)
    
    # Cargar datos
    success = load_excel_with_evaluations(excel_file)
    if not success:
        sys.exit(1)