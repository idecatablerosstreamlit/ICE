"""
Dashboard ICE - Archivo Principal - VERSIÓN CORREGIDA CON BANNER
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
    
    # AGREGAR SOLO ESTA LÍNEA:
    create_banner()
    
    # BANNER USANDO SOLO STREAMLIT NATIVO - GARANTIZADO QUE FUNCIONA
    
    # Sección azul GOV.CO
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
        padding: 15px 20px;
        margin: -1rem -1rem 0 -1rem;
        color: white;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        ">
            <div style="display: flex; align-items: center;">
                <div style="
                    width: 32px;
                    height: 32px;
                    background: white;
                    border-radius: 6px;
                    margin-right: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    color: #4A6CF7;
                    font-weight: bold;
                ">🏛️</div>
                <span style="
                    color: white;
                    font-size: 22px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                ">GOV.CO</span>
            </div>
            <a href="https://www.gov.co/" target="_blank" style="
                color: white;
                text-decoration: underline;
                font-size: 14px;
            ">Ir a Gov.co</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección blanca Dashboard
    st.markdown("""
    <div style="
        background: white;
        padding: 25px 20px;
        margin: 0 -1rem 20px -1rem;
        border-bottom: 3px solid #4472C4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            max-width: 1200px;
            margin: 0 auto;
            flex-wrap: wrap;
            gap: 20px;
        ">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    box-shadow: 0 6px 20px rgba(68, 114, 196, 0.3);
                ">🏢</div>
                <div>
                    <h1 style="
                        color: #2C3E50;
                        font-size: 32px;
                        font-weight: 700;
                        margin: 0 0 6px 0;
                        background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    ">Dashboard ICE</h1>
                    <p style="
                        color: #6C757D;
                        font-size: 16px;
                        margin: 0;
                        font-weight: 400;
                    ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    width: 55px;
                    height: 55px;
                    background: linear-gradient(135deg, #003366 0%, #004080 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 8px;
                    font-weight: bold;
                    text-align: center;
                    line-height: 1.1;
                    box-shadow: 0 4px 12px rgba(0, 51, 102, 0.3);
                ">ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.</div>
                
                <div style="
                    background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                    padding: 12px 20px;
                    border-radius: 25px;
                    color: white;
                    font-weight: bold;
                    font-size: 18px;
                    letter-spacing: 1.5px;
                    box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
                ">BOGOTÁ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    apply_dark_theme()
    
    # Inicializar session state - SIMPLIFICADO
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    if 'last_load_time' not in st.session_state:
        st.session_state.last_load_time = 0
    
    # Verificar configuración de Google Sheets
    config_valid, config_message = validate_google_sheets_config()
    
    if not config_valid:
        st.error(f"❌ **Error en configuración de Google Sheets:** {config_message}")
        
        with st.expander("📋 Ver instrucciones de configuración", expanded=True):
            show_setup_instructions()
        
        st.stop()
    
    # CARGA DE DATOS SIMPLIFICADA - SIN INFORMACIÓN EN ENCABEZADO
    try:
        # Cargar datos sin mostrar información en el encabezado
        df, source_info, excel_data = load_data_simple()
        
        # Verificar si la carga fue exitosa
        if df is None:
            st.error("❌ Error al cargar datos desde Google Sheets")
            show_error_message()
            return
        
        # Verificar estructura de datos (sin mostrar información técnica)
        if not verify_data_structure(df):
            return
        
        # Crear filtros simples (sin información técnica)
        filters = create_simple_filters(df)
        
        # Renderizar pestañas
        tab_manager = TabManager(df, None, excel_data)
        tab_manager.render_tabs(df, filters)
        
        # INFORMACIÓN DE ESTADO AL FINAL - EN EXPANDER
        st.markdown("---")
        
        # Información del sistema en expander (colapsado por defecto)
        with st.expander("Información del Sistema", expanded=False):
            show_system_info_footer(df, source_info)
        
    except Exception as e:
        st.error(f"❌ Error crítico: {e}")
        
        # Mostrar detalles para debug
        with st.expander("🔧 Detalles del error"):
            import traceback
            st.code(traceback.format_exc())
        
        # Botón para reintentar
        if st.button("🔄 Reintentar"):
            current_tab = st.session_state.get('active_tab_index', 0)
            st.session_state.last_load_time = time.time()
            st.session_state.active_tab_index = current_tab
            st.rerun()

def load_data_simple():
    """Cargar datos silenciosamente para evitar información en encabezado"""
    try:
        # Cargar desde Google Sheets sin mostrar información
        data_loader = DataLoader()
        df_loaded = data_loader.load_data()
        
        # Cargar datos del Excel silenciosamente
        excel_loader = ExcelDataLoader()
        excel_data = excel_loader.load_excel_data()
        
        # Obtener información de la fuente
        source_info = data_loader.get_data_source_info()
        
        return df_loaded, source_info, excel_data
        
    except Exception as e:
        # Error silencioso, se mostrará en el footer
        empty_df = pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
        ])
        return empty_df, {'source': 'Google Sheets (Error)', 'connection_info': {'connected': False}}, None

def show_system_info_footer(df, source_info):
    """Mostrar información del sistema sin iconos en expander"""
    
    # Mostrar información que antes estaba en encabezado
    if not df.empty:
        st.success(f"Cargados {len(df)} registros desde Google Sheets")
        st.success("Datos procesados y listos para usar")
    
    # Estadísticas principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Estadísticas de Datos")
        
        # Información básica sin iconos
        st.info(f"**Total registros:** {len(df)}")
        
        indicadores_unicos = df['Codigo'].nunique() if not df.empty else 0
        st.info(f"**Indicadores únicos:** {indicadores_unicos}")
        
        if not df.empty and 'Fecha' in df.columns:
            fechas_disponibles = df['Fecha'].nunique()
            st.info(f"**Fechas diferentes:** {fechas_disponibles}")
        else:
            st.info("**Fechas diferentes:** 0")
        
        # Información de tipos si existe la columna
        if not df.empty and 'Tipo' in df.columns:
            tipos_count = df['Tipo'].value_counts()
            st.info(f"**Tipos de indicadores:** {dict(tipos_count)}")
    
    with col2:
        st.markdown("#### Estado de Conexión")
        
        # Estado de conexión sin iconos
        connection_info = source_info.get('connection_info', {})
        if connection_info.get('connected', False):
            st.success("**Google Sheets:** Conectado")
        else:
            st.error("**Google Sheets:** Desconectado")
        
        # Botón de actualización
        if st.button("Actualizar desde Google Sheets", 
                    help="Recarga los datos desde Google Sheets",
                    key="footer_refresh"):
            current_tab = st.session_state.get('active_tab_index', 0)
            st.session_state.last_load_time = time.time()
            st.session_state.active_tab_index = current_tab
            st.rerun()

def verify_data_structure(df):
    """Verificar estructura de datos"""
    if df.empty:
        st.info("📋 Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
        return True
    
    # Verificar columnas esenciales
    required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ **Error:** Faltan columnas esenciales en Google Sheets: {missing_columns}")
        st.error("**Verifica que tu Google Sheets tenga las columnas correctas**")
        st.write("**Columnas disponibles:**", list(df.columns))
        return False
    
    return True

def create_simple_filters(df):
    """Crear filtros simples SIN información técnica en encabezado"""
    
    try:
        if df.empty or 'Fecha' not in df.columns:
            return {'fecha': None}
            
        fechas_validas = df['Fecha'].dropna().unique()
        if len(fechas_validas) > 0:
            fechas = sorted(fechas_validas)
            fecha_seleccionada = st.selectbox(
                "Fecha de referencia", 
                fechas, 
                index=len(fechas) - 1,
                help="Los cálculos usan siempre el valor más reciente de cada indicador"
            )
            return {'fecha': fecha_seleccionada}
        else:
            return {'fecha': None}
    except Exception as e:
        return {'fecha': None}

def show_error_message():
    """Mostrar mensaje de error"""
    st.error("""
    ### ❌ Error al cargar datos desde Google Sheets

    **Posibles causas:**
    1. **Configuración incorrecta:** Verifica `secrets.toml`
    2. **Permisos:** El Service Account debe tener acceso a la hoja
    3. **Estructura de datos:** La hoja debe tener las columnas correctas
    4. **Conectividad:** Verifica tu conexión a internet
    """)

if __name__ == "__main__":
    main()
