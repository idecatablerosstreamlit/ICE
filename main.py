"""
Dashboard ICE - Archivo Principal - VERSIÓN SIMPLIFICADA SIN FILTROS
"""

import streamlit as st
import pandas as pd
import os
import time
from config import (
    configure_page, create_banner, apply_dark_theme, validate_google_sheets_config,
    show_setup_instructions
)
from data_utils import DataLoader, ExcelDataLoader
from tabs import TabManager

def main():
    configure_page()
    
    # Crear banner superior
    create_banner()
    
    # Inicializar session state - SIMPLIFICADO
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    if 'last_load_time' not in st.session_state:
        st.session_state.last_load_time = 0
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = 0
    
    # Verificar configuración de Google Sheets
    config_valid, config_message = validate_google_sheets_config()
    
    if not config_valid:
        st.error(f"❌ **Error en configuración de Google Sheets:** {config_message}")
        
        with st.expander("📋 Ver instrucciones de configuración", expanded=True):
            show_setup_instructions()
        
        st.stop()
    
    # CARGA DE DATOS SIMPLIFICADA
    try:
        # Cargar datos con información de estado
        df, source_info, excel_data = load_data_with_status()
        
        # Verificar si la carga fue exitosa
        if df is None:
            st.error("❌ Error al cargar datos desde Google Sheets")
            show_error_message()
            return
        
        # Verificar estructura de datos
        if not verify_data_structure_complete(df):
            return
        
        # ✅ SIN FILTROS - Solo pasar datos directamente
        # Las pestañas siempre usarán los valores más recientes
        
        # Renderizar pestañas sin filtros
        tab_manager = TabManager(df, None, excel_data)
        tab_manager.render_tabs(df, {})  # Pasar diccionario vacío como filtros
        
        # INFORMACIÓN DE ESTADO AL FINAL
        st.markdown("---")
        
        # Información del sistema en expander
        with st.expander("Información del Sistema", expanded=False):
            show_system_info_complete(df, source_info, excel_data)
        
    except Exception as e:
        st.error(f"❌ Error crítico en la aplicación: {e}")
        
        # Mostrar detalles para debug
        with st.expander("🔧 Detalles del error"):
            import traceback
            st.code(traceback.format_exc())
        
        # Opciones de recuperación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reintentar", use_container_width=True):
                current_tab = st.session_state.get('active_tab_index', 0)
                st.session_state.last_load_time = time.time()
                st.session_state.active_tab_index = current_tab
                st.rerun()
        
        with col2:
            if st.button("🧹 Limpiar Cache", use_container_width=True):
                st.cache_data.clear()
                st.session_state.data_timestamp = time.time()
                st.rerun()

def load_data_with_status():
    """Cargar datos con información de estado mejorada"""
    try:
        # Mostrar estado de carga
        with st.spinner("🔄 Conectando con Google Sheets..."):
            # Cargar desde Google Sheets
            data_loader = DataLoader()
            df_loaded = data_loader.load_data()
        
        # Cargar datos del Excel
        with st.spinner("📋 Cargando datos metodológicos..."):
            excel_loader = ExcelDataLoader()
            excel_data = excel_loader.load_excel_data()
        
        # Obtener información de la fuente
        source_info = data_loader.get_data_source_info()
        
        # Mostrar resultados de carga
        # if df_loaded is not None and not df_loaded.empty:
        #     st.success(f"✅ Datos cargados: {len(df_loaded)} registros de Google Sheets")
        # else:
         #    st.info("📋 Google Sheets está vacío o no se pudo conectar")
        
        # if excel_data is not None and not excel_data.empty:
        #     st.success(f"✅ Datos metodológicos: {len(excel_data)} indicadores")
        # else:
         #    st.warning("⚠️ No se encontró archivo Excel metodológico")
        
        return df_loaded, source_info, excel_data
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        # Retornar datos vacíos para mantener funcionalidad
        empty_df = pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
        ])
        return empty_df, {'source': 'Google Sheets (Error)', 'connection_info': {'connected': False}}, None

def get_last_update_date(df):
    """Obtener la fecha de la última actualización (el indicador más recientemente actualizado)"""
    try:
        if df.empty or 'Fecha' not in df.columns:
            return None
        
        # Obtener la fecha más reciente de todos los registros
        fechas_validas = df['Fecha'].dropna()
        if fechas_validas.empty:
            return None
        
        # Convertir a datetime si es necesario
        if not pd.api.types.is_datetime64_any_dtype(fechas_validas):
            fechas_validas = pd.to_datetime(fechas_validas, errors='coerce').dropna()
        
        if fechas_validas.empty:
            return None
        
        # Obtener la fecha más reciente
        ultima_fecha = fechas_validas.max()
        
        # Obtener información del indicador que se actualizó más recientemente
        registro_mas_reciente = df[df['Fecha'] == ultima_fecha].iloc[0]
        
        return {
            'fecha': ultima_fecha,
            'indicador': registro_mas_reciente.get('Indicador', 'N/A'),
            'codigo': registro_mas_reciente.get('Codigo', 'N/A'),
            'componente': registro_mas_reciente.get('Componente', 'N/A')
        }
        
    except Exception as e:
        return None

def verify_data_structure_complete(df):
    """Verificar estructura de datos con información detallada"""
    if df.empty:
        st.info("📋 Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
        st.markdown("""
        ### 🚀 Primeros pasos:
        1. Ve a la pestaña **"Gestión de Datos"**
        2. Haz clic en **"[Crear nuevo código]"**
        3. Completa la información del nuevo indicador
        4. Agrega algunos registros con valores y fechas
        5. Los datos se guardarán automáticamente en Google Sheets
        6. Regresa a las otras pestañas para ver los análisis
        """)
        return True
    
    # Verificar columnas esenciales
    required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ **Error:** Faltan columnas esenciales en Google Sheets: {missing_columns}")
        st.error("**Verifica que tu Google Sheets tenga las columnas correctas**")
        
        # Mostrar información de diagnóstico
        with st.expander("🔧 Información de diagnóstico"):
            st.write("**Columnas disponibles en Google Sheets:**", list(df.columns))
            st.write("**Columnas requeridas:**", required_columns)
            st.write("**Total registros:**", len(df))
            
            # Mostrar muestra de datos si existe
            if not df.empty:
                st.write("**Muestra de datos:**")
                st.dataframe(df.head(3), use_container_width=True)
        
        return False
    
    # Verificar datos válidos
    datos_validos = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
    if datos_validos.empty:
        st.warning("⚠️ Los datos en Google Sheets están incompletos")
        st.info("Hay registros pero faltan valores en campos esenciales")
        return True
    
    # Información positiva sobre la estructura
    registros_invalidos = len(df) - len(datos_validos)
    if registros_invalidos > 0:
        st.info(f"📊 {len(datos_validos)} registros válidos de {len(df)} totales")
    
    return True

def show_system_info_complete(df, source_info, excel_data):
    """Mostrar información completa del sistema"""
    
    # Información de datos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Estadísticas de Datos")
        
        if not df.empty:
            st.success(f"**Total registros:** {len(df)}")
            
            indicadores_unicos = df['Codigo'].nunique()
            st.success(f"**Indicadores únicos:** {indicadores_unicos}")
            
            if 'Fecha' in df.columns:
                fechas_disponibles = df['Fecha'].nunique()
                fecha_min = df['Fecha'].min()
                fecha_max = df['Fecha'].max()
                st.info(f"**Fechas diferentes:** {fechas_disponibles}")
                st.info(f"**Rango:** {pd.to_datetime(fecha_min).strftime('%d/%m/%Y')} - {pd.to_datetime(fecha_max).strftime('%d/%m/%Y')}")
            
            # Información de tipos si existe la columna
            if 'Tipo' in df.columns:
                tipos_count = df['Tipo'].value_counts()
                st.info(f"**Tipos de indicadores:** {dict(tipos_count)}")
            
            # Información de componentes
            if 'Componente' in df.columns:
                componentes_count = df['Componente'].nunique()
                st.info(f"**Componentes únicos:** {componentes_count}")
        else:
            st.warning("**Google Sheets vacío**")
    
    with col2:
        st.markdown("#### 🔗 Estado de Conexiones")
        
        # Estado Google Sheets
        connection_info = source_info.get('connection_info', {})
        if connection_info.get('connected', False):
            st.success("**Google Sheets:** Conectado")
        else:
            st.error("**Google Sheets:** Desconectado")
        
        # Estado Excel metodológico
        if excel_data is not None and not excel_data.empty:
            st.success(f"**Excel metodológico:** {len(excel_data)} fichas")
        else:
            st.warning("**Excel metodológico:** No disponible")
        
        # Estado PDF
        try:
            import reportlab
            pdf_status = "Disponible"
            pdf_color = "success"
        except ImportError:
            pdf_status = "No instalado (pip install reportlab)"
            pdf_color = "error"
        
        if pdf_color == "success":
            st.success(f"**Generación PDF:** {pdf_status}")
        else:
            st.error(f"**Generación PDF:** {pdf_status}")
        
        # Información de cache
        st.info(f"**Cache timestamp:** {st.session_state.get('data_timestamp', 'No inicializado')}")
    
    # Controles de gestión
    st.markdown("#### ⚙️ Controles de Sistema")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🔄 Actualizar Datos", 
                    help="Recarga los datos desde Google Sheets",
                    use_container_width=True):
            current_tab = st.session_state.get('active_tab_index', 0)
            st.session_state.last_load_time = time.time()
            st.session_state.active_tab_index = current_tab
            st.rerun()
    
    with col4:
        if st.button("🧹 Limpiar Cache", 
                    help="Limpia el cache de Streamlit",
                    use_container_width=True):
            st.cache_data.clear()
            st.session_state.data_timestamp = time.time()
            st.success("Cache limpiado")
            time.sleep(1)
            st.rerun()
    
    with col5:
        if st.button("🔧 Test Conexión", 
                    help="Probar conexión con Google Sheets",
                    use_container_width=True):
            try:
                from google_sheets_manager import GoogleSheetsManager
                sheets_manager = GoogleSheetsManager()
                success, message = sheets_manager.test_connection()
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")

def show_error_message():
    """Mostrar mensaje de error detallado"""
    st.error("""
    ### ❌ Error al cargar datos desde Google Sheets

    **Posibles causas y soluciones:**
    1. **Configuración incorrecta:** Verifica el archivo `secrets.toml`
    2. **Permisos:** El Service Account debe tener acceso de "Editor" a la hoja
    3. **Estructura de datos:** La hoja debe tener las columnas correctas
    4. **Conectividad:** Verifica tu conexión a internet
    5. **URL incorrecta:** Verifica que la URL de Google Sheets sea correcta
    """)
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Ver instrucciones de configuración", use_container_width=True):
            show_setup_instructions()
    
    with col2:
        if st.button("🔄 Intentar reconectar", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()
