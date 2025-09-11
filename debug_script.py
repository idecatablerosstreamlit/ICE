"""
Script de diagnóstico para el Dashboard ICE
Ejecutar este script para verificar que todo esté configurado correctamente
"""

import os
import pandas as pd
import sys
from datetime import datetime

def check_file_existence():
    """Verificar que el archivo CSV existe"""
    print("🔍 Verificando archivo CSV...")
    
    csv_file = "IndicadoresICE.csv"
    current_dir = os.getcwd()
    csv_path = os.path.join(current_dir, csv_file)
    
    print(f"📁 Directorio actual: {current_dir}")
    print(f"📄 Buscando archivo: {csv_path}")
    
    if os.path.exists(csv_path):
        print("✅ Archivo CSV encontrado")
        return csv_path
    else:
        print("❌ Archivo CSV NO encontrado")
        
        # Buscar archivos CSV alternativos
        csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
        if csv_files:
            print(f"📋 Archivos CSV encontrados: {csv_files}")
        else:
            print("📭 No se encontraron archivos CSV en el directorio")
        
        return None

def check_file_content(csv_path):
    """Verificar el contenido del archivo CSV"""
    print("\n📊 Verificando contenido del CSV...")
    
    try:
        # Leer el archivo
        df = pd.read_csv(csv_path, sep=";", encoding='utf-8-sig')
        print(f"✅ Archivo leído correctamente")
        print(f"📏 Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
        
        # Verificar columnas
        print(f"📋 Columnas encontradas: {list(df.columns)}")
        
        required_columns = ['LINEA DE ACCIÓN', 'COMPONENTE PROPUESTO', 'CATEGORÍA', 'COD', 'Nombre de indicador', 'Valor', 'Fecha']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Columnas faltantes: {missing_columns}")
        else:
            print("✅ Todas las columnas requeridas están presentes")
        
        # Verificar datos
        print(f"\n📈 Estadísticas básicas:")
        print(f"   - Total registros: {len(df)}")
        print(f"   - Indicadores únicos: {df['Nombre de indicador'].nunique()}")
        print(f"   - Componentes únicos: {df['COMPONENTE PROPUESTO'].nunique()}")
        
        # Verificar fechas
        print(f"\n📅 Verificando fechas...")
        fechas_sample = df['Fecha'].head(5).tolist()
        print(f"   - Muestra de fechas: {fechas_sample}")
        
        try:
            fechas_convertidas = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            fechas_validas = fechas_convertidas.notna().sum()
            print(f"   - Fechas válidas: {fechas_validas}/{len(df)}")
        except Exception as e:
            print(f"   - ⚠️ Error procesando fechas: {e}")
        
        # Verificar valores
        print(f"\n🎯 Verificando valores...")
        valores_sample = df['Valor'].head(5).tolist()
        print(f"   - Muestra de valores: {valores_sample}")
        
        try:
            if df['Valor'].dtype == 'object':
                valores_convertidos = df['Valor'].str.replace(',', '.').astype(float)
            else:
                valores_convertidos = df['Valor']
            
            valores_validos = valores_convertidos.notna().sum()
            print(f"   - Valores válidos: {valores_validos}/{len(df)}")
            print(f"   - Rango: {valores_convertidos.min():.2f} - {valores_convertidos.max():.2f}")
        except Exception as e:
            print(f"   - ⚠️ Error procesando valores: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def check_dependencies():
    """Verificar dependencias de Python"""
    print("\n🐍 Verificando dependencias de Python...")
    
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'plotly': 'plotly'
    }
    
    for package_name, import_name in required_packages.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'Desconocida')
            print(f"✅ {package_name}: {version}")
        except ImportError:
            print(f"❌ {package_name}: NO INSTALADO")
    
    print(f"🐍 Python: {sys.version}")

def check_streamlit_config():
    """Verificar configuración de Streamlit"""
    print("\n⚙️ Verificando configuración de Streamlit...")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit importado correctamente: {st.__version__}")
        
        # Verificar si estamos en Streamlit Cloud
        if 'STREAMLIT_SERVER_PORT' in os.environ:
            print("☁️ Ejecutándose en Streamlit Cloud")
        else:
            print("💻 Ejecutándose localmente")
            
    except Exception as e:
        print(f"❌ Error con Streamlit: {e}")

def generate_test_data():
    """Generar datos de prueba si el archivo no existe"""
    print("\n🛠️ Generando archivo de datos de prueba...")
    
    test_data = {
        'LINEA DE ACCIÓN': ['LA.2.3.', 'N.A.', 'L.A.5.1.'] * 5,
        'COMPONENTE PROPUESTO': ['Datos', 'Seguridad e interoperabilidad', 'Gobernanza y estratégia'] * 5,
        'CATEGORÍA': ['01. Disponibilidad', '01. Interoperabilidad', '02. Financiación'] * 5,
        'COD': [f'D0{i}-{j}' for i in range(1, 4) for j in range(1, 6)],
        'Nombre de indicador': [f'Indicador de prueba {i}' for i in range(1, 16)],
        'Valor': [0.5] * 15,
        'Fecha': ['1/01/2025'] * 15
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv('IndicadoresICE_test.csv', sep=';', index=False, encoding='utf-8-sig')
    print("✅ Archivo de prueba generado: IndicadoresICE_test.csv")

def main():
    """Función principal de diagnóstico"""
    print("🚀 Iniciando diagnóstico del Dashboard ICE")
    print("=" * 50)
    
    # Verificar archivo
    csv_path = check_file_existence()
    
    if csv_path:
        check_file_content(csv_path)
    else:
        print("\n💡 ¿Quieres generar un archivo de datos de prueba? (s/n)")
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            generate_test_data()
    
    # Verificar dependencias
    check_dependencies()
    
    # Verificar Streamlit
    check_streamlit_config()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnóstico completado")
    print("\n💡 Para ejecutar el dashboard, usa:")
    print("   streamlit run main.py")

if __name__ == "__main__":
    main()