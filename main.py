"""
Dashboard ICE - Archivo Principal
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
"""

import streamlit as st
import pandas as pd
import os
from config import configure_page, apply_dark_theme, CSV_FILENAME
from data_utils import DataLoader, ExcelDataLoader
from tabs import TabManager

def main():
    """Función principal del dashboard"""
    
    # Configurar página
    configure_page()
    apply_dark_theme()
    
    # Título principal con estilo corporativo
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="color: white; margin: 0;">🏢 Dashboard ICE</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Sistema de Monitoreo - Infraestructura de Conocimiento Espacial
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sistema de recarga automática de datos - MEJORADO
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = 0
    
    # Verificar si hay cambios en el archivo CSV
    def get_file_timestamp(csv_path):
        try:
            return os.path.getmtime(csv_path)
        except:
            return 0
    
    # Cargar datos con cache más inteligente
    @st.cache_data(ttl=5, show_spinner=True)  # Cache por 5 segundos para permitir recargas
    def load_data_cached(timestamp, file_timestamp):
        data_loader = DataLoader()
        df_loaded = data_loader.load_data()
        return df_loaded, data_loader.csv_path
        # Cargar datos del Excel para hojas metodológicas
        excel_loader = ExcelDataLoader()
        excel_data = excel_loader.load_excel_data()
    try:
        # Obtener timestamp del archivo
        data_loader_temp = DataLoader()
        file_timestamp = get_file_timestamp(data_loader_temp.csv_path)
        
        # Cargar datos con ambos timestamps
        df, csv_path = load_data_cached(st.session_state.data_timestamp, file_timestamp)
        
        # Debug: Mostrar información de cache
        with st.expander("🔧 Debug: Sistema de cache", expanded=False):
            st.write(f"**Session timestamp:** {st.session_state.data_timestamp}")
            st.write(f"**File timestamp:** {file_timestamp}")
            st.write(f"**Datos cargados:** {len(df) if df is not None else 0} registros")
        
        if df is not None and not df.empty:
            # Verificación de salud de los datos
            health_check_passed = True
            
            # Verificar columnas esenciales
            required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ **Error crítico:** Faltan columnas esenciales: {missing_columns}")
                st.write("**Columnas disponibles:**", list(df.columns))
                health_check_passed = False
            
            # Verificar datos válidos
            datos_validos = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            if len(datos_validos) == 0:
                st.error("❌ **Error crítico:** No hay datos válidos (todos los registros tienen valores nulos)")
                health_check_passed = False
            
            if not health_check_passed:
                st.stop()
            
            # Botón de recarga manual
            col_reload1, col_reload2, col_reload3 = st.columns([2, 1, 2])
            with col_reload2:
                if st.button("🔄 Actualizar Datos", help="Recarga los datos desde el archivo CSV"):
                    st.cache_data.clear()
                    st.session_state.data_timestamp += 1
                    st.rerun()
            
            # Mostrar información de estado de los datos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📊 **{len(df)}** registros cargados")
            with col2:
                st.info(f"🔢 **{df['Codigo'].nunique()}** indicadores únicos")
            with col3:
                fechas_disponibles = df['Fecha'].nunique()
                st.info(f"📅 **{fechas_disponibles}** fechas diferentes")
            
            # IMPORTANTE: No filtrar por fecha aquí - dejar que cada función maneje sus propios filtros
            # El cálculo de componentes y general siempre usa valores más recientes
            df_completo = df.copy()
            
            # Crear filtros simples (solo para referencia, no para filtrado directo)
            filters = create_simple_filters(df)
            
            # Renderizar pestañas - pasar datos completos
            tab_manager = TabManager(df_completo, csv_path, excel_data)
            tab_manager.render_tabs(df_completo, filters) 
        else:
            show_error_message()
            
    except Exception as e:
        st.error(f"Error crítico al procesar datos: {e}")
        st.info("Verifica que el archivo CSV contenga todas las columnas requeridas")
        # Mostrar traceback para debug
        import traceback
        with st.expander("🔧 Detalles del error (para desarrolladores)"):
            st.code(traceback.format_exc())
            
        # Botón para intentar recargar
        if st.button("🔄 Intentar Recargar Datos"):
            st.cache_data.clear()
            st.rerun()

def create_simple_filters(df):
    """Crear selector de fecha para referencia (no afecta cálculos principales)"""
    st.markdown("### 📅 Fecha de Referencia")
    
    # Mostrar información explicativa
    st.info("""
    ℹ️ **Nota importante:** Los cálculos de componentes y puntaje general siempre usan 
    el **valor más reciente** de cada indicador. Esta fecha es solo para visualizaciones específicas.
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            # Filtrar solo fechas válidas (no NaT)
            fechas_validas = df['Fecha'].dropna().unique()
            if len(fechas_validas) > 0:
                fechas = sorted(fechas_validas)
                fecha_seleccionada = st.selectbox(
                    "Seleccionar fecha (solo para visualizaciones específicas)", 
                    fechas, 
                    index=len(fechas) - 1,
                    help="Esta fecha se usa solo en algunas visualizaciones. Los cálculos principales usan valores más recientes."
                )
                return {'fecha': fecha_seleccionada}
            else:
                st.warning("No se encontraron fechas válidas en los datos")
                return {'fecha': None}
        except Exception as e:
            st.warning(f"Error al procesar fechas: {e}")
            return {'fecha': None}

def show_error_message():
    """Mostrar mensaje de error cuando no se puede cargar el archivo"""
    st.error(f"""
    ### ❌ Error al cargar el archivo de indicadores

    No se pudo encontrar o abrir el archivo "{CSV_FILENAME}". 

    **Solución:**
    1. Asegúrate de que el archivo "{CSV_FILENAME}" existe en el mismo directorio donde estás ejecutando esta aplicación.
    2. Verifica que el nombre del archivo sea exactamente "{CSV_FILENAME}" (respetando mayúsculas y minúsculas).
    3. Comprueba que el archivo utiliza punto y coma (;) como separador de columnas.
    4. Asegúrate de que tienes permisos de lectura para el archivo.

    Si sigues teniendo problemas, intenta crear una copia del archivo CSV y guárdala con el nombre "{CSV_FILENAME}" en el mismo directorio que este script.
    """)

    # Mostrar información de diagnóstico
    try:
        current_dir = os.getcwd()
        files_in_dir = os.listdir(current_dir)
        st.info(f"""
        **Información de diagnóstico:**
        - Directorio de trabajo actual: {current_dir}
        - Archivos en el directorio actual: {', '.join(files_in_dir)}
        """)
    except Exception as e:
        st.warning(f"No se pudo obtener información del directorio: {e}")

if __name__ == "__main__":
    main()
