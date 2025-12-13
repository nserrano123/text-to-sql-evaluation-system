#!/usr/bin/env python3
"""
Script para cargar datos de gold queries desde un archivo Excel
"""

import pandas as pd
import requests
import json
import sys
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8001"
EXCEL_FILE = "gold_queries.xlsx"  # Cambia por el nombre de tu archivo

def load_excel_to_system(excel_file_path):
    """
    Carga datos desde Excel al sistema de evaluación
    """
    
    # Verificar que el archivo existe
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
            # Campos requeridos
            'chatInput': 'chat_input',                           # La pregunta en lenguaje natural
            'SQL': 'sql_reference',                              # La consulta SQL correcta (gold standard)
            'Tablas y columnas (DDL)': 'tablas_columnas_ddl',   # El esquema de la base de datos
            
            # Campos opcionales
            'sessionId': 'session_id',                          # ID de sesión
            'member_id': 'member_id',                           # ID del miembro
            'Clasificacion': 'clasificacion',                   # Categoría de la consulta
            'Pregunta Descompuesta': 'pregunta_descompuesta'    # Pregunta descompuesta
            
            # Nota: 'N8nSqlGenerated' no se mapea porque es la consulta generada por IA,
            # no la consulta de referencia (gold standard)
        }
        
        # Verificar columnas requeridas
        required_fields = ['chat_input', 'sql_reference', 'tablas_columnas_ddl']
        mapped_columns = {v: k for k, v in column_mapping.items() if k in df.columns}
        
        missing_required = [field for field in required_fields if field not in mapped_columns]
        if missing_required:
            print(f"❌ Error: Faltan campos requeridos: {missing_required}")
            print(f"💡 Ajusta el column_mapping en el script")
            return False
        
        # Cargar datos
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Preparar datos para la API
                gold_query_data = {}
                
                for api_field, excel_column in mapped_columns.items():
                    value = row[excel_column]
                    if pd.notna(value):  # Solo incluir valores no nulos
                        gold_query_data[api_field] = str(value).strip()
                
                # Verificar campos requeridos
                if not all(gold_query_data.get(field) for field in required_fields):
                    print(f"⚠️  Fila {index + 1}: Faltan campos requeridos, saltando...")
                    error_count += 1
                    continue
                
                # Enviar a la API
                response = requests.post(
                    f"{API_BASE_URL}/api/gold-queries",
                    json=gold_query_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ Fila {index + 1}: Cargada exitosamente")
                else:
                    error_count += 1
                    print(f"❌ Fila {index + 1}: Error {response.status_code} - {response.text}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Fila {index + 1}: Error - {str(e)}")
        
        print(f"\n📊 Resumen:")
        print(f"✅ Exitosas: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📈 Total procesadas: {success_count + error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False

def show_excel_preview(excel_file_path):
    """
    Muestra una vista previa del Excel para ayudar con el mapeo
    """
    try:
        df = pd.read_excel(excel_file_path)
        print(f"\n📋 Vista previa de {excel_file_path}:")
        print(f"📊 Filas: {len(df)}")
        print(f"📋 Columnas: {list(df.columns)}")
        print(f"\n🔍 Primeras 3 filas:")
        print(df.head(3).to_string())
        
        print(f"\n💡 Ajusta el column_mapping en el script según tus columnas:")
        for col in df.columns:
            print(f"   '{col}': 'campo_del_sistema',")
            
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
        show_excel_preview(sys.argv[2])
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
        success = load_excel_to_system(excel_file)
        if success:
            print("\n🎉 ¡Datos cargados exitosamente!")
            print("🌐 Ahora puedes ir a http://localhost:3000 para usar el sistema")
        else:
            print("\n❌ Hubo errores al cargar los datos")
            sys.exit(1)