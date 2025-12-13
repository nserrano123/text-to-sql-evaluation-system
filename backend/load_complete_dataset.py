#!/usr/bin/env python3
"""
Script para cargar dataset completo con gold queries y evaluaciones ya realizadas
"""

import pandas as pd
import requests
import json
import sys
from pathlib import Path
import time

# Configuración
API_BASE_URL = "http://localhost:8001"

def load_complete_dataset(excel_file_path):
    """
    Carga gold queries y evaluaciones completas desde Excel
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
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                print(f"\n🔄 Procesando fila {index + 1}...")
                
                # 1. Preparar datos para gold query
                gold_query_data = {
                    "chat_input": str(row['chatInput']).strip() if pd.notna(row['chatInput']) else "",
                    "sql_reference": str(row['SQL']).strip() if pd.notna(row['SQL']) else "",
                    "tablas_columnas_ddl": str(row['Tablas y columnas (DDL)']).strip() if pd.notna(row['Tablas y columnas (DDL)']) else ""
                }
                
                # Campos opcionales
                if pd.notna(row['sessionId']):
                    gold_query_data["session_id"] = str(row['sessionId']).strip()
                if pd.notna(row['member_id']):
                    gold_query_data["member_id"] = str(row['member_id']).strip()
                if pd.notna(row['Clasificacion']):
                    gold_query_data["clasificacion"] = str(row['Clasificacion']).strip()
                if pd.notna(row['Pregunta Descompuesta']):
                    gold_query_data["pregunta_descompuesta"] = str(row['Pregunta Descompuesta']).strip()
                
                # Verificar campos requeridos
                if not all([gold_query_data["chat_input"], gold_query_data["sql_reference"], gold_query_data["tablas_columnas_ddl"]]):
                    print(f"⚠️  Fila {index + 1}: Faltan campos requeridos, saltando...")
                    error_count += 1
                    continue
                
                # 2. Crear gold query
                print(f"📝 Creando gold query...")
                response = requests.post(
                    f"{API_BASE_URL}/api/gold-queries",
                    json=gold_query_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"❌ Error creando gold query - {response.status_code}: {response.text}")
                    error_count += 1
                    continue
                
                gold_query_response = response.json()
                gold_query_id = gold_query_response['id']
                print(f"✅ Gold query creada con ID: {gold_query_id}")
                
                # 3. Crear evaluaciones para cada modelo que tenga datos
                models_to_evaluate = [
                    {
                        'name': 'N8n',
                        'sql_column': 'N8nSqlGenerated',
                        'notes': 'Evaluación cargada desde Excel - Modelo N8n'
                    },
                    {
                        'name': 'Metric',
                        'sql_column': 'MetricSqlGenerated', 
                        'notes': 'Evaluación cargada desde Excel - Modelo Metric'
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
                                # Asumir que valores > 0 o "True" o "1" significan correcto
                                ea_value = str(row['ExecutionAccuracy']).strip().lower()
                                execution_accuracy = ea_value in ['1', 'true', 'yes', 'correct', 'correcto']
                            
                            # Component matching desde las columnas CM_*
                            select_correct = False
                            where_correct = False
                            group_by_correct = False
                            order_by_correct = False
                            keywords_correct = False
                            
                            if 'CM_select' in df.columns and pd.notna(row['CM_select']):
                                select_correct = str(row['CM_select']).strip().lower() in ['1', 'true', 'yes', 'correct']
                            if 'CM_where' in df.columns and pd.notna(row['CM_where']):
                                where_correct = str(row['CM_where']).strip().lower() in ['1', 'true', 'yes', 'correct']
                            if 'CM_group_by' in df.columns and pd.notna(row['CM_group_by']):
                                group_by_correct = str(row['CM_group_by']).strip().lower() in ['1', 'true', 'yes', 'correct']
                            if 'CM_order_by' in df.columns and pd.notna(row['CM_order_by']):
                                order_by_correct = str(row['CM_order_by']).strip().lower() in ['1', 'true', 'yes', 'correct']
                            if 'CM_keywords' in df.columns and pd.notna(row['CM_keywords']):
                                keywords_correct = str(row['CM_keywords']).strip().lower() in ['1', 'true', 'yes', 'correct']
                            
                            # Calcular F1 score
                            correct_components = sum([select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct])
                            total_components = 5
                            precision = correct_components / total_components if total_components > 0 else 0
                            recall = precision  # En este contexto, precision = recall
                            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                            
                            # Datos para la evaluación
                            evaluation_data = {
                                "gold_query_id": gold_query_id,
                                "generated_sql": generated_sql,
                                "execution_accuracy": {
                                    "isCorrect": execution_accuracy,
                                    "evaluatorNotes": f"{model['notes']} - Execution Accuracy: {execution_accuracy}"
                                },
                                "time_to_answer": {
                                    "startTime": "2024-01-01T00:00:00Z",  # Placeholder
                                    "endTime": "2024-01-01T00:00:01Z",    # Placeholder
                                    "durationSeconds": 1.0
                                },
                                "component_matching": {
                                    "selectCorrect": select_correct,
                                    "whereCorrect": where_correct,
                                    "groupByCorrect": group_by_correct,
                                    "orderByCorrect": order_by_correct,
                                    "keywordsCorrect": keywords_correct,
                                    "f1Score": f1_score,
                                    "evaluatorNotes": f"{model['notes']} - Component Matching completado"
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
                time.sleep(0.1)  # Pequeña pausa para no sobrecargar la API
                
            except Exception as e:
                error_count += 1
                print(f"❌ Fila {index + 1}: Error - {str(e)}")
        
        print(f"\n📊 Resumen:")
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📈 Total procesadas: {success_count + error_count}")
        
        if success_count > 0:
            print(f"\n🎉 ¡Dataset completo cargado exitosamente!")
            print(f"📊 Ve a http://localhost:3000/dashboard para ver las métricas")
            print(f"📈 Ve a http://localhost:3000/results para ver las gráficas")
            print(f"📤 Ve a http://localhost:3000/export para exportar resultados")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False

def show_dataset_preview(excel_file_path):
    """
    Muestra una vista previa del dataset completo
    """
    try:
        df = pd.read_excel(excel_file_path)
        print(f"\n📋 Vista previa del dataset:")
        print(f"📊 Filas: {len(df)}")
        print(f"📋 Columnas: {len(df.columns)}")
        
        # Mostrar estadísticas por modelo
        if 'N8nSqlGenerated' in df.columns:
            n8n_count = df['N8nSqlGenerated'].notna().sum()
            print(f"🤖 Consultas N8n: {n8n_count}")
        
        if 'MetricSqlGenerated' in df.columns:
            metric_count = df['MetricSqlGenerated'].notna().sum()
            print(f"📊 Consultas Metric: {metric_count}")
        
        if 'ExecutionAccuracy' in df.columns:
            ea_count = df['ExecutionAccuracy'].notna().sum()
            print(f"✅ Con Execution Accuracy: {ea_count}")
        
        # Mostrar component matching
        cm_columns = [col for col in df.columns if col.startswith('CM_')]
        if cm_columns:
            print(f"🔧 Component Matching columnas: {len(cm_columns)}")
        
        print(f"\n🔍 Primeras 2 filas (campos principales):")
        main_cols = ['chatInput', 'SQL', 'N8nSqlGenerated', 'ExecutionAccuracy']
        available_cols = [col for col in main_cols if col in df.columns]
        if available_cols:
            print(df[available_cols].head(2).to_string())
            
    except Exception as e:
        print(f"❌ Error al leer el archivo: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📖 Uso:")
        print(f"   python {sys.argv[0]} <archivo.xlsx>")
        print(f"   python {sys.argv[0]} preview <archivo.xlsx>  # Para ver vista previa")
        sys.exit(1)
    
    if sys.argv[1] == "preview":
        if len(sys.argv) < 3:
            print("❌ Especifica el archivo para la vista previa")
            sys.exit(1)
        show_dataset_preview(sys.argv[2])
    else:
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
        success = load_complete_dataset(excel_file)
        if not success:
            sys.exit(1)