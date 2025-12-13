#!/usr/bin/env python3
"""
Script para cargar dataset usando SQLite local (sin Supabase)
"""

import pandas as pd
import sqlite3
import json
import sys
from pathlib import Path
import uuid
from datetime import datetime

def create_local_database():
    """
    Crea base de datos SQLite local con el esquema necesario
    """
    conn = sqlite3.connect('evaluation_system.db')
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_queries (
            id TEXT PRIMARY KEY,
            chat_input TEXT NOT NULL,
            session_id TEXT,
            member_id TEXT,
            clasificacion TEXT,
            pregunta_descompuesta TEXT,
            tablas_columnas_ddl TEXT NOT NULL,
            sql_reference TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id TEXT PRIMARY KEY,
            gold_query_id TEXT NOT NULL,
            generated_sql TEXT NOT NULL,
            evaluation_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gold_query_id) REFERENCES gold_queries(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_accuracy (
            id TEXT PRIMARY KEY,
            evaluation_id TEXT NOT NULL,
            results_match BOOLEAN,
            is_correct BOOLEAN NOT NULL,
            evaluator_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_to_answer (
            id TEXT PRIMARY KEY,
            evaluation_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS component_matching (
            id TEXT PRIMARY KEY,
            evaluation_id TEXT NOT NULL,
            select_correct BOOLEAN NOT NULL,
            where_correct BOOLEAN NOT NULL,
            group_by_correct BOOLEAN NOT NULL,
            order_by_correct BOOLEAN NOT NULL,
            keywords_correct BOOLEAN NOT NULL,
            f1_score REAL,
            evaluator_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        )
    ''')
    
    conn.commit()
    return conn

def load_dataset_to_sqlite(excel_file_path):
    """
    Carga dataset completo a SQLite local
    """
    
    if not Path(excel_file_path).exists():
        print(f"❌ Error: No se encuentra el archivo {excel_file_path}")
        return False
    
    try:
        # Crear base de datos local
        print("🗄️  Creando base de datos SQLite local...")
        conn = create_local_database()
        cursor = conn.cursor()
        
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
                
                # Verificar campos requeridos
                if pd.isna(row['chatInput']) or pd.isna(row['SQL']) or pd.isna(row['Tablas y columnas (DDL)']):
                    print(f"⚠️  Fila {index + 1}: Faltan campos requeridos, saltando...")
                    error_count += 1
                    continue
                
                # 1. Crear gold query
                gold_query_id = str(uuid.uuid4())
                
                cursor.execute('''
                    INSERT INTO gold_queries 
                    (id, chat_input, session_id, member_id, clasificacion, pregunta_descompuesta, tablas_columnas_ddl, sql_reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    gold_query_id,
                    str(row['chatInput']).strip(),
                    str(row['sessionId']).strip() if pd.notna(row['sessionId']) else None,
                    str(row['member_id']).strip() if pd.notna(row['member_id']) else None,
                    str(row['Clasificacion']).strip() if pd.notna(row['Clasificacion']) else None,
                    str(row['Pregunta Descompuesta']).strip() if pd.notna(row['Pregunta Descompuesta']) else None,
                    str(row['Tablas y columnas (DDL)']).strip(),
                    str(row['SQL']).strip()
                ))
                
                print(f"✅ Gold query creada con ID: {gold_query_id}")
                
                # 2. Crear evaluaciones para cada modelo
                models_to_evaluate = [
                    {
                        'name': 'N8n',
                        'sql_column': 'N8nSqlGenerated',
                        'notes': 'Modelo N8n'
                    },
                    {
                        'name': 'Metric',
                        'sql_column': 'MetricSqlGenerated', 
                        'notes': 'Modelo Metric'
                    }
                ]
                
                for model in models_to_evaluate:
                    if model['sql_column'] in df.columns and pd.notna(row[model['sql_column']]):
                        generated_sql = str(row[model['sql_column']]).strip()
                        
                        if generated_sql:
                            print(f"🤖 Creando evaluación para modelo {model['name']}...")
                            
                            # Crear evaluación
                            evaluation_id = str(uuid.uuid4())
                            cursor.execute('''
                                INSERT INTO evaluations (id, gold_query_id, generated_sql)
                                VALUES (?, ?, ?)
                            ''', (evaluation_id, gold_query_id, generated_sql))
                            
                            # Execution accuracy
                            execution_accuracy = False
                            if 'ExecutionAccuracy' in df.columns and pd.notna(row['ExecutionAccuracy']):
                                ea_value = str(row['ExecutionAccuracy']).strip().lower()
                                execution_accuracy = ea_value in ['1', 'true', 'yes', 'correct', 'correcto']
                            
                            cursor.execute('''
                                INSERT INTO execution_accuracy (id, evaluation_id, is_correct, evaluator_notes)
                                VALUES (?, ?, ?, ?)
                            ''', (str(uuid.uuid4()), evaluation_id, execution_accuracy, f"Cargado desde Excel - {model['notes']}"))
                            
                            # Time to answer (placeholder)
                            cursor.execute('''
                                INSERT INTO time_to_answer (id, evaluation_id, start_time, end_time, duration_seconds)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (str(uuid.uuid4()), evaluation_id, '2024-01-01T00:00:00Z', '2024-01-01T00:00:01Z', 1.0))
                            
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
                            
                            cursor.execute('''
                                INSERT INTO component_matching 
                                (id, evaluation_id, select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct, f1_score, evaluator_notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (str(uuid.uuid4()), evaluation_id, select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct, f1_score, f"Cargado desde Excel - {model['notes']}"))
                            
                            print(f"✅ Evaluación creada para modelo {model['name']}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"❌ Fila {index + 1}: Error - {str(e)}")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 Resumen:")
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📈 Total procesadas: {success_count + error_count}")
        
        if success_count > 0:
            print(f"\n🎉 ¡Dataset cargado exitosamente en SQLite!")
            print(f"🗄️  Base de datos creada: evaluation_system.db")
            print(f"📊 Ahora puedes usar el sistema con datos locales")
            
            # Mostrar estadísticas
            conn = sqlite3.connect('evaluation_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM gold_queries")
            gold_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM evaluations")
            eval_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM execution_accuracy WHERE is_correct = 1")
            correct_count = cursor.fetchone()[0]
            
            print(f"\n📈 Estadísticas:")
            print(f"📝 Gold queries: {gold_count}")
            print(f"🤖 Evaluaciones: {eval_count}")
            print(f"✅ Consultas correctas: {correct_count}")
            print(f"📊 Accuracy promedio: {(correct_count/eval_count*100):.1f}%" if eval_count > 0 else "📊 Accuracy promedio: 0%")
            
            conn.close()
        
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
    
    # Cargar datos
    success = load_dataset_to_sqlite(excel_file)
    if not success:
        sys.exit(1)