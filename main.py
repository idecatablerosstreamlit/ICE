"""
Dashboard ICE - Archivo Principal - SOLO GOOGLE SHEETS
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
"""

import streamlit as st
import pandas as pd
import os
from config import (
    configure_page, apply_dark_theme, validate_google_sheets_config,
    show_setup_instructions
)
from data_utils import DataLoader, ExcelDataLoader
from tabs import TabManager

def main():
    """Función principal del dashboard"""
    
    # Configurar página
    configure_page()
    apply_dark_theme()
    
    # Título principal
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #4472C4 0%, #5B9BD5 100%);
                  border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="color: white; margin: 0;">🏢 Dashboard ICE</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Sistema de Monitoreo - Infraestructura de Conocimiento Espacial
        </p>
        <p style="margin: 0.5rem 0 0 0;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 500;">
                📊 Powered by Google Sheets
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar configuración de Google Sheets
    config_valid, config_message = validate_google_sheets_config()
    
    if not config_valid:
        st.error(f"❌ **Error en configuración de Google Sheets:** {config_message}")
        
        with st.expander("📋 Ver instrucciones de configuración", expanded=True):
            show_setup_instructions()
        
        st.stop()
    
    # Sistema de recarga automática de datos
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = 0
    
    # Función de carga desde Google Sheets
    @st.cache_data(ttl=30, show_spinner=True)
    def load_data_cached(timestamp):
        """Cargar datos únicamente desde Google Sheets"""
        try:
            # Cargar desde Google Sheets
            data_loader = DataLoader()
            df_loaded = data_loader.load_data()
            
            # Cargar datos del Excel para hojas metodológicas
            excel_loader = ExcelDataLoader()
            excel_data = excel_loader.load_excel_data()
            
            # Obtener información de la fuente
            source_info = data_loader.get_data_source_info()
            
            return df_loaded, source_info, excel_data
            
        except Exception as e:
            st.error(f"Error al cargar datos desde Google Sheets: {e}")
            # Retornar datos vacíos pero válidos
            empty_df = pd.DataFrame(columns=[
                'Linea_Accion', 'Componente', 'Categoria', 
                'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso'
            ])
            return empty_df, {'source': 'Google Sheets (Error)', 'connection_info': {'connected': False}}, None
    
    try:
        # Cargar datos
        df, source_info, excel_data = load_data_cached(st.session_state.data_timestamp)
        
        # Debug: Mostrar información de la fuente
        with st.expander("🔧 Debug: Información de Google Sheets", expanded=False):
            st.write(f"**Tipo de fuente:** {source_info['source']}")
            st.write(f"**Session timestamp:** {st.session_state.data_timestamp}")
            st.write(f"**Datos cargados:** {len(df) if df is not None else 0} registros")
            st.write(f"**Columnas disponibles:** {list(df.columns) if df is not None else 'N/A'}")
            
            connection_info = source_info.get('connection_info', {})
            st.write(f"**Conectado:** {connection_info.get('connected', False)}")
            if connection_info.get('spreadsheet_url'):
                st.write(f"**URL:** {connection_info['spreadsheet_url']}")
        
        if df is not None:
            # Verificación básica de datos
            if df.empty:
                st.info("📋 Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
                
                # Mostrar instrucciones para empezar
                with st.expander("📚 Cómo empezar con Google Sheets", expanded=True):
                    st.markdown("""
                    ### 🚀 Primeros pasos para usar el Dashboard ICE con Google Sheets:
                    
                    1. **Ve a la pestaña "Gestión de Datos"**
                    2. **Selecciona "➕ Crear nuevo código"** para crear tu primer indicador
                    3. **Llena la información básica** del indicador
                    4. **Agrega algunos registros** con fechas y valores
                    5. **Los datos se guardarán automáticamente** en Google Sheets
                    6. **Regresa a las otras pestañas** para ver los análisis
                    
                    ### 📊 Estructura de Google Sheets:
                    Tu hoja debe tener estas columnas en la primera fila:
                    - `LINEA DE ACCIÓN`
                    - `COMPONENTE PROPUESTO`
                    - `CATEGORÍA`
                    - `COD`
                    - `Nombre de indicador`
                    - `Valor`
                    - `Fecha`
                    """)
            else:
                # Verificación de columnas esenciales
                required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ **Error:** Faltan columnas esenciales en Google Sheets: {missing_columns}")
                    st.error("**Verifica que tu Google Sheets tenga las columnas correctas**")
                    st.write("**Columnas disponibles:**", list(df.columns))
                    st.stop()
            
            # Botón de recarga manual
            col_reload1, col_reload2, col_reload3 = st.columns([2, 1, 2])
            with col_reload2:
                if st.button("🔄 Actualizar desde Google Sheets", help="Recarga los datos desde Google Sheets"):
                    # Guardar pestaña activa antes de recargar
                    current_tab = st.session_state.get('active_tab', 0)
                    
                    st.cache_data.clear()
                    st.session_state.data_timestamp += 1
                    
                    # Restaurar pestaña activa
                    st.session_state.active_tab = current_tab
                    
                    st.rerun()
            
            # Mostrar información de estado
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"📊 **{len(df)}** registros")
            with col2:
                indicadores_unicos = df['Codigo'].nunique() if not df.empty else 0
                st.info(f"🔢 **{indicadores_unicos}** indicadores")
            with col3:
                if not df.empty and 'Fecha' in df.columns:
                    fechas_disponibles = df['Fecha'].nunique()
                    st.info(f"📅 **{fechas_disponibles}** fechas")
                else:
                    st.info("📅 **0** fechas")
            with col4:
                # Mostrar estado de conexión
                connection_info = source_info.get('connection_info', {})
                if connection_info.get('connected', False):
                    st.success("🌐 **Conectado**")
                else:
                    st.error("❌ **Desconectado**")
            
            # Mostrar enlace a Google Sheets
            connection_info = source_info.get('connection_info', {})
            if connection_info.get('spreadsheet_url'):
                spreadsheet_url = connection_info['spreadsheet_url']
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #0F9D58 0%, #34A853 100%); 
                           padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center;">
                    <p style="color: white; margin: 0; font-weight: 500;">
                        📊 Datos sincronizados con Google Sheets
                        <a href="{spreadsheet_url}" target="_blank" style="color: #4472C4; text-decoration: underline; margin-left: 10px;">
                            🔗 Abrir hoja de cálculo
                        </a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Crear filtros simples
            filters = create_simple_filters(df)
            
            # Renderizar pestañas (sin CSV path ya que solo usamos Google Sheets)
            tab_manager = TabManager(df, None, excel_data)
            tab_manager.render_tabs(df, filters)
            
        else:
            st.error("❌ No se pudieron cargar los datos desde Google Sheets")
            show_error_message()
            
    except Exception as e:
        st.error(f"Error crítico: {e}")
        
        # Mostrar traceback para debug
        import traceback
        with st.expander("🔧 Detalles del error (para desarrolladores)"):
            st.code(traceback.format_exc())
            
        # Botón para intentar recargar
        if st.button("🔄 Intentar Recargar"):
            # Guardar pestaña activa antes de recargar
            current_tab = st.session_state.get('active_tab', 0)
            
            st.cache_data.clear()
            
            # Restaurar pestaña activa
            st.session_state.active_tab = current_tab
            
            st.rerun()

def create_simple_filters(df):
    """Crear selector de fecha para referencia"""
    st.markdown("### 📅 Fecha de Referencia")
    
    st.info("""
    ℹ️ **Nota:** Los cálculos principales siempre usan el **valor más reciente** 
    de cada indicador. Esta fecha es solo para visualizaciones específicas.
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            if df.empty or 'Fecha' not in df.columns:
                st.warning("No hay fechas disponibles en Google Sheets")
                return {'fecha': None}
                
            fechas_validas = df['Fecha'].dropna().unique()
            if len(fechas_validas) > 0:
                fechas = sorted(fechas_validas)
                fecha_seleccionada = st.selectbox(
                    "Seleccionar fecha (solo para visualizaciones específicas)", 
                    fechas, 
                    index=len(fechas) - 1,
                    help="Esta fecha se usa solo en algunas visualizaciones específicas"
                )
                return {'fecha': fecha_seleccionada}
            else:
                st.warning("No se encontraron fechas válidas en Google Sheets")
                return {'fecha': None}
        except Exception as e:
            st.warning(f"Error al procesar fechas: {e}")
            return {'fecha': None}

def show_error_message():
    """Mostrar mensaje de error específico para Google Sheets"""
    st.error(f"""
    ### ❌ Error al cargar datos desde Google Sheets

    **Posibles causas:**
    1. **Configuración incorrecta:** Verifica `secrets.toml`
    2. **Permisos:** El Service Account debe tener acceso a la hoja
    3. **Estructura de datos:** La hoja debe tener las columnas correctas
    4. **Conectividad:** Verifica tu conexión a internet
    
    **Solución:**
    - Revisa la configuración en el expander de arriba
    - Asegúrate de que la hoja esté compartida con el Service Account
    - Verifica que las columnas coincidan con el formato esperado
    """)
    
    with st.expander("🔧 Diagnóstico de Google Sheets", expanded=True):
        config_valid, config_message = validate_google_sheets_config()
        if config_valid:
            st.success("✅ Configuración de secrets.toml válida")
        else:
            st.error(f"❌ {config_message}")
        
        # Mostrar configuración actual (sin datos sensibles)
        if "google_sheets" in st.secrets:
            st.write("**Configuración encontrada:**")
            config_keys = list(st.secrets["google_sheets"].keys())
            # Ocultar private_key por seguridad
            safe_keys = [k for k in config_keys if k != 'private_key']
            st.write(f"- Claves configuradas: {safe_keys}")
            if 'spreadsheet_url' in st.secrets["google_sheets"]:
                url = st.secrets["google_sheets"]["spreadsheet_url"]
                st.write(f"- URL de hoja: {url}")

if __name__ == "__main__":
    main()
