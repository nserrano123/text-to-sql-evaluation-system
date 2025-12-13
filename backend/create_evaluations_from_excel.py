#!/usr/bin/env python3
"""
Script simple para crear evaluaciones desde Excel
"""

import pandas as pd
import requests
import json
import sys
from pathlib import Path
import time

API_BASE_URL = "http://localhost:8001"

def create_evaluations_from_excel(excel_file_path):
    """
    Crea evaluaciones desde Excel usando las gold queries existentes
    """
    
    if not Path(excel_file_path).exists():
        print(f"❌ Error: No se encuentra el archivo {excel_file_path}")
        return False
    
    try:
        # Leer Excel
        print(f"📖 Leyendo archivo Excel: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Obtener gold queries existentes
        print("📋 Obteniendo gold queries existentes...")
        response = requests.get(f"{API_BASE_URL}/api/gold-queries/")
        gold_queries = response.json()
        
        print(f"📊 Encontradas {len(gold_queries)} gold queries")
        print(f"📊 Encontradas {len(df)} filas en Excel")
        
        success_count = 0
        error_count = 0
        
        # Crear un mapa de gold queries por chat_input para hacer matching
        gold_query_map = {gq['chat_input']: gq for gq in gold_queries}
        
        for index, row in df.iterrows():
            try:
                print(f"\n🔄 Procesando fila {index + 1}...")
                
                # Buscar la gold query correspondiente
                chat_input = str(row['chatInput']).strip()
                
                if chat_input not in gold_query_map:
                    print(f"⚠️  Fila {index + 1}: No se encontró gold query para '{chat_input[:50]}...', saltando...")
                    error_count += 1
                    continue
                
                gold_query = gold_query_map[chat_input]
                gold_query_id = gold_query['id']
                
                # Crear evaluaciones para cada modelo que tenga datos
                models_to_evaluate = [
                    {
                        'name': 'N8n',
                        'sql_column': 'N8nSqlGenerated'
                    },
                    {
                        'name': 'Metric',
                        'sql_column': 'MetricSqlGenerated'
                    }
                ]
                
                for model in models_to_evaluate:
                    if model['sql_column'] in df.columns and pd.notna(row[model['sql_column']]):
                        generated_sql = str(row[model['sql_column']]).strip()
                        
                        if generated_sql:
                            print(f"🤖 Creando evaluación para modelo {model['name']}...")
                            
                            # Determinar execution accuracy
                            execution_accuracy = False
                            if 'ExecutionAccuracy' in df.columns and pd.notna(row['ExecutionAccuracy']):
                                ea_value = str(row['ExecutionAccuracy']).strip().lower()
                                execution_accuracy = ea_value in ['1', 'true', 'yes', 'correct', 'correcto']
                            
                            # Component matching
                            select_correct = str(row.get('CM_select', '')).strip().lower() in ['1', 'true', 'yes', 'correct'] if pd.notna(row.get('CM_select')) else False
                            where_correct = str(row.get('CM_where', '')).strip().lower() in ['1', 'true', 'yes', 'correct'] if pd.notna(row.get('CM_where')) else False
                            group_by_correct = str(row.get('CM_group_by', '')).strip().lower() in ['1', 'true', 'yes', 'correct'] if pd.notna(row.get('CM_group_by')) else False
                            order_by_correct = str(row.get('CM_order_by', '')).strip().lower() in ['1', 'true', 'yes', 'correct'] if pd.notna(row.get('CM_order_by')) else False
                            keywords_correct = str(row.get('CM_keywords', '')).strip().lower() in ['1', 'true', 'yes', 'correct'] if pd.notna(row.get('CM_keywords')) else False
                            
                            # Calcular F1 score
                            correct_components = sum([select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct])
                            total_components = 5
                            precision = correct_components / total_components if total_components > 0 else 0
                            recall = precision
                            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                            
                            # Datos para la evaluación
                            evaluation_data = {
                                "gold_query_id": gold_query_id,
                                "generated_sql": generated_sql,
                                "execution_accuracy": {
                                    "isCorrect": execution_accuracy,
                                    "evaluatorNotes": f"Cargado desde Excel - Modelo {model['name']}"
                                },
                                "time_to_answer": {
                                    "startTime": "2024-01-01T00:00:00Z",
                                    "endTime": "2024-01-01T00:00:01Z",
                                    "durationSeconds": 1.0
                                },
                                "component_matching": {
                                    "selectCorrect": select_correct,
                                    "whereCorrect": where_correct,
                                    "groupByCorrect": group_by_correct,
                                    "orderByCorrect": order_by_correct,
                                    "keywordsCorrect": keywords_correct,
                                    "f1Score": f1_score,
                                    "evaluatorNotes": f"Cargado desde Excel - Modelo {model['name']}"
                                }
                            }
                            
                            eval_response = requests.post(
                                f"{API_BASE_URL}/api/evaluations",
                                json=evaluation_data,
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if eval_response.status_code == 200:
                                print(f"✅ Evaluación creada para modelo {model['name']}")
                            else:
                                print(f"⚠️  Error creando evaluación para {model['name']} - {eval_response.status_code}: {eval_response.text}")
                
                success_count += 1
                time.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Fila {index + 1}: Error - {str(e)}")
        
        print(f"\n📊 Resumen:")
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores: {error_count}")
        
        if success_count > 0:
            print(f"\n🎉 ¡Evaluaciones creadas exitosamente!")
            print(f"🌐 Ve a http://localhost:3000 para ver el sistema funcionando")
        
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
    
    # Crear evaluaciones
    success = create_evaluations_from_excel(excel_file)
    if not success:
        sys.exit(1)