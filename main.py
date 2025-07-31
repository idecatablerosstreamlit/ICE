"""
Dashboard ICE - Archivo Principal - VERSIÓN CORREGIDA CON BANNER
"""

import streamlit as st
import pandas as pd
import os
import time
from config import (
    configure_page, apply_dark_theme, validate_google_sheets_config,
    show_setup_instructions
)
from data_utils import DataLoader, ExcelDataLoader
from tabs import TabManager

def main():
    # Configurar página
    configure_page()
    
    # BANNER DEBE IR ANTES DEL TEMA - VERSIÓN CORREGIDA
    try:
        from banner import create_government_banner_with_real_logos
        create_government_banner_with_real_logos()
    except Exception as e:
        # Fallback en caso de error
        st.markdown("""
        <div style='background: #4A6CF7; color: white; padding: 15px; text-align: center; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🏛️ GOV.CO - Dashboard ICE 🏢</h2>
            <p style='color: white; margin: 5px 0 0 0;'>Sistema de Monitoreo - IDECA</p>
        </div>
        """, unsafe_allow_html=True)
        st.error(f"Error cargando banner: {e}")
    
    apply_dark_theme()
    
    # Inicializar session state - SIMPLIFICADO
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    if 'last_load_time' not in st.session_state:
        st.session_state.last_load_time = 0
    
    # NO AGREGAR MÁS TÍTULOS AQUÍ - EL BANNER YA LOS INCLUYE
    
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
    
    # Información detallada en expandible (lo que antes se mostraba en "Detalles del procesamiento")
    with st.expander("Detalles del procesamiento de datos", expanded=False):
        if not df.empty:
            st.write("**Procesamiento completado:**")
            st.success("Columnas renombradas correctamente")
            
            # Información de fechas
            if 'Fecha' in df.columns:
                fechas_validas = df['Fecha'].notna().sum()
                fechas_invalidas = df['Fecha'].isna().sum()
                if fechas_validas > 0:
                    st.success(f"{fechas_validas} fechas procesadas correctamente")
                if fechas_invalidas > 0:
                    st.warning(f"{fechas_invalidas} fechas no convertidas")
            
            # Información de valores
            if 'Valor' in df.columns:
                valores_validos = df['Valor'].notna().sum()
                valores_invalidos = df['Valor'].isna().sum()
                if valores_validos > 0:
                    st.success(f"{valores_validos} valores procesados")
                if valores_invalidos > 0:
                    st.warning(f"{valores_invalidos} valores no válidos")
            
            # Información de normalización
            if 'Valor_Normalizado' in df.columns:
                # Contar indicadores con y sin historial
                indicadores_sin_historico = 0
                indicadores_con_historico = 0
                
                for codigo in df['Codigo'].unique():
                    if pd.isna(codigo):
                        continue
                    valores = df[df['Codigo'] == codigo]['Valor'].dropna()
                    if len(valores) == 1:
                        indicadores_sin_historico += 1
                    elif len(valores) > 1:
                        indicadores_con_historico += 1
                
                norm_min = df['Valor_Normalizado'].min()
                norm_max = df['Valor_Normalizado'].max()
                norm_promedio = df['Valor_Normalizado'].mean()
                
                st.success("Normalización completada")
                st.info(f"Rango normalizado: {norm_min:.3f} - {norm_max:.3f}")
                st.info(f"Promedio normalizado: {norm_promedio:.3f}")
                
                if indicadores_sin_historico > 0:
                    st.info(f"{indicadores_sin_historico} indicadores sin historial: valores numéricos = 0.7, porcentajes = valor original")
                
                if indicadores_con_historico > 0:
                    st.info(f"{indicadores_con_historico} indicadores con historial: normalizados por máximo")
        else:
            st.info("Google Sheets está vacío")
    
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
        
        # Información técnica
        with st.expander("Información Técnica", expanded=False):
            st.write("**Fuente de datos:**", source_info.get('source', 'Desconocida'))
            if connection_info and 'timeout' in connection_info:
                st.write("**Timeout configurado:**", f"{connection_info['timeout']}s")
            
            # Timestamp de última carga
            if 'last_load_time' in st.session_state and st.session_state.last_load_time > 0:
                import datetime
                last_time = datetime.datetime.fromtimestamp(st.session_state.last_load_time)
                st.write("**Última actualización:**", last_time.strftime('%H:%M:%S'))
            
            # Información sobre normalización
            st.markdown("**Reglas de normalización:**")
            st.write("• Porcentajes: valor original")
            st.write("• Números sin historial: 0.7 (70%)")
            st.write("• Números con historial: normalizado por máximo")

def verify_data_structure(df):
    """Verificar estructura de datos"""
    if df.empty:
        st.info("📋 Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
        
        # Mostrar instrucciones
        with st.expander("🚀 Cómo empezar", expanded=True):
            st.markdown("""
            ### Primeros pasos:
            
            1. **Ve a la pestaña "Gestión de Datos"**
            2. **Selecciona "➕ Crear nuevo código"**
            3. **Llena la información del indicador**
            4. **Agrega registros con fechas y valores**
            5. **Los datos se guardan automáticamente en Google Sheets**
            
            ### Columnas requeridas en Google Sheets:
            - `LINEA DE ACCIÓN`
            - `COMPONENTE PROPUESTO`
            - `CATEGORÍA`
            - `COD`
            - `Nombre de indicador`
            - `Valor`
            - `Fecha`
            - `Tipo`
            """)
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
