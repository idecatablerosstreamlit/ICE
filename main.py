"""
Dashboard ICE - Archivo Principal
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
VERSION CON SOPORTE GOOGLE SHEETS
"""

import streamlit as st
import pandas as pd
import os
from config import (
    configure_page, apply_dark_theme, get_data_source_preference, 
    show_data_source_indicator, validate_google_sheets_config,
    show_setup_instructions
)
from data_utils import DataLoader, ExcelDataLoader
from tabs import TabManager

def main():
    """Función principal del dashboard"""
    
    # Configurar página
    configure_page()
    apply_dark_theme()
    
    # Determinar fuente de datos
    data_source = get_data_source_preference()
    
    # Título principal con indicador de fuente de datos
    source_indicator = show_data_source_indicator(data_source)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="color: white; margin: 0;">🏢 Dashboard ICE</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Sistema de Monitoreo - Infraestructura de Conocimiento Espacial
        </p>
        <p style="margin: 0.5rem 0 0 0;">
            {source_indicator}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar configuración si es necesario
    if data_source == "google_sheets":
        config_valid, config_message = validate_google_sheets_config()
        if not config_valid:
            st.error(f"❌ **Error en configuración de Google Sheets:** {config_message}")
            
            with st.expander("📋 Ver instrucciones de configuración", expanded=True):
                show_setup_instructions()
            
            st.info("💡 El sistema usará CSV como fallback hasta que Google Sheets esté configurado")
            data_source = "csv"  # Fallback a CSV
    
    # Sistema de recarga automática de datos
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = 0
    
    # Función de carga adaptable
    @st.cache_data(ttl=30 if data_source == "google_sheets" else 5, show_spinner=True)
    def load_data_cached(timestamp, source_type):
        """Cargar datos según el tipo de fuente"""
        # Configurar DataLoader según la fuente
        use_google_sheets = (source_type == "google_sheets")
        data_loader = DataLoader(use_google_sheets=use_google_sheets)
        
        df_loaded = data_loader.load_data()
        
        # Cargar datos del Excel para hojas metodológicas
        excel_loader = ExcelDataLoader()
        excel_data = excel_loader.load_excel_data()
        
        # Obtener información de la fuente de datos
        source_info = data_loader.get_data_source_info()
        
        return df_loaded, source_info, excel_data
    
    try:
        # Cargar datos
        df, source_info, excel_data = load_data_cached(st.session_state.data_timestamp, data_source)
        
        # Debug: Mostrar información de la fuente
        with st.expander("🔧 Debug: Información de la fuente de datos", expanded=False):
            st.write(f"**Tipo de fuente:** {source_info['source']}")
            st.write(f"**Session timestamp:** {st.session_state.data_timestamp}")
            st.write(f"**Datos cargados:** {len(df) if df is not None else 0} registros")
            
            if source_info['source'] == 'Google Sheets':
                connection_info = source_info.get('connection_info', {})
                st.write(f"**Conectado:** {connection_info.get('connected', False)}")
                if connection_info.get('spreadsheet_url'):
                    st.write(f"**URL:** {connection_info['spreadsheet_url']}")
            elif source_info['source'] == 'CSV':
                st.write(f"**Archivo CSV:** {source_info.get('csv_path', 'N/A')}")
        
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
                st.error("❌ **Error crítico:** No hay datos válidos")
                health_check_passed = False
            
            if not health_check_passed:
                st.stop()
            
            # Botón de recarga manual adaptado
            col_reload1, col_reload2, col_reload3 = st.columns([2, 1, 2])
            with col_reload2:
                button_text = "🔄 Actualizar desde Google Sheets" if data_source == "google_sheets" else "🔄 Actualizar Datos"
                if st.button(button_text, help=f"Recarga los datos desde {source_info['source']}"):
                    st.cache_data.clear()
                    st.session_state.data_timestamp += 1
                    st.rerun()
            
            # Mostrar información de estado
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"📊 **{len(df)}** registros")
            with col2:
                st.info(f"🔢 **{df['Codigo'].nunique()}** indicadores")
            with col3:
                fechas_disponibles = df['Fecha'].nunique()
                st.info(f"📅 **{fechas_disponibles}** fechas")
            with col4:
                # Mostrar fuente de datos
                if source_info['source'] == 'Google Sheets':
                    st.success("🌐 **Google Sheets**")
                else:
                    st.warning("📁 **CSV Local**")
            
            # Mostrar enlace a Google Sheets si aplica
            if (source_info['source'] == 'Google Sheets' and 
                source_info.get('connection_info', {}).get('spreadsheet_url')):
                
                spreadsheet_url = source_info['connection_info']['spreadsheet_url']
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #0F9D58 0%, #34A853 100%); 
                           padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center;">
                    <p style="color: white; margin: 0; font-weight: 500;">
                        📊 Datos sincronizados con Google Sheets
                        <a href="{spreadsheet_url}" target="_blank" style="color: #E8F5E8; text-decoration: underline; margin-left: 10px;">
                            🔗 Abrir hoja de cálculo
                        </a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Datos completos para pestañas
            df_completo = df.copy()
            
            # Crear filtros simples
            filters = create_simple_filters(df)
            
            # Renderizar pestañas con información de fuente
            csv_path = source_info.get('csv_path', '') if source_info['source'] == 'CSV' else None
            tab_manager = TabManager(df_completo, csv_path, excel_data)
            tab_manager.render_tabs(df_completo, filters)
            
        else:
            show_error_message(data_source)
            
    except Exception as e:
        st.error(f"Error crítico al procesar datos: {e}")
        st.info("Verifica la configuración de tu fuente de datos")
        
        # Mostrar traceback para debug
        import traceback
        with st.expander("🔧 Detalles del error (para desarrolladores)"):
            st.code(traceback.format_exc())
            
        # Botón para intentar recargar
        if st.button("🔄 Intentar Recargar"):
            st.cache_data.clear()
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
                st.warning("No se encontraron fechas válidas")
                return {'fecha': None}
        except Exception as e:
            st.warning(f"Error al procesar fechas: {e}")
            return {'fecha': None}

def show_error_message(data_source):
    """Mostrar mensaje de error adaptado a la fuente de datos"""
    if data_source == "google_sheets":
        st.error("""
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
        
        with st.expander("🔧 Diagnóstico de Google Sheets"):
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
    else:
        # Mensaje original para CSV
        from config import CSV_FILENAME
        st.error(f"""
        ### ❌ Error al cargar archivo CSV

        No se pudo encontrar o abrir el archivo "{CSV_FILENAME}".

        **Solución:**
        1. Asegúrate de que el archivo "{CSV_FILENAME}" existe
        2. Verifica el formato (punto y coma como separador)
        3. Comprueba los permisos de lectura
        """)
        
        # Mostrar información de diagnóstico
        try:
            current_dir = os.getcwd()
            files_in_dir = os.listdir(current_dir)
            st.info(f"""
            **Diagnóstico:**
            - Directorio actual: {current_dir}
            - Archivos encontrados: {', '.join(files_in_dir)}
            """)
        except Exception as e:
            st.warning(f"Error al obtener información del directorio: {e}")

if __name__ == "__main__":
    main()
