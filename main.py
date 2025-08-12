"""
Dashboard ICE - Archivo Principal - VERSIÓN CORREGIDA CON FILTROS DE FECHA
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
    
    # Aplicar estilos (comentado porque el original no lo usa)
    # apply_dark_theme()
    
    # Inicializar session state - COMPLETO
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    if 'last_load_time' not in st.session_state:
        st.session_state.last_load_time = 0
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = 0
    if 'selected_fecha' not in st.session_state:
        st.session_state.selected_fecha = None
    
    # Verificar configuración de Google Sheets
    config_valid, config_message = validate_google_sheets_config()
    
    if not config_valid:
        st.error(f"❌ **Error en configuración de Google Sheets:** {config_message}")
        
        with st.expander("📋 Ver instrucciones de configuración", expanded=True):
            show_setup_instructions()
        
        st.stop()
    
    # CARGA DE DATOS CON MANEJO DE ERRORES COMPLETO
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
        
        # Crear filtros mejorados con información de estado
        filters = create_enhanced_filters(df)
        
        # Mostrar información de filtros aplicados (opcional)
        show_filter_status(df, filters)
        
        # Renderizar pestañas con datos y filtros
        tab_manager = TabManager(df, None, excel_data)
        tab_manager.render_tabs(df, filters)
        
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
        if df_loaded is not None and not df_loaded.empty:
            st.success(f"✅ Datos cargados: {len(df_loaded)} registros de Google Sheets")
        else:
            st.info("📋 Google Sheets está vacío o no se pudo conectar")
        
        if excel_data is not None and not excel_data.empty:
            st.success(f"✅ Datos metodológicos: {len(excel_data)} indicadores")
        else:
            st.warning("⚠️ No se encontró archivo Excel metodológico")
        
        return df_loaded, source_info, excel_data
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        # Retornar datos vacíos para mantener funcionalidad
        empty_df = pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
        ])
        return empty_df, {'source': 'Google Sheets (Error)', 'connection_info': {'connected': False}}, None

def load_data_simple():
    """Cargar datos silenciosamente para evitar información en encabezado - MANTENER COMPATIBILIDAD"""
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

def verify_data_structure(df):
    """Verificar estructura de datos - VERSIÓN SIMPLE PARA COMPATIBILIDAD"""
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

def create_enhanced_filters(df):
    """Crear filtros mejorados con información de estado - VERSIÓN PRINCIPAL"""
    
    try:
        if df.empty or 'Fecha' not in df.columns:
            st.warning("⚠️ No hay fechas disponibles para filtrar")
            return {'fecha': None}
        
        # ✅ OBTENER Y PROCESAR FECHAS
        fechas_validas = df['Fecha'].dropna().unique()
        if len(fechas_validas) == 0:
            st.warning("⚠️ No hay fechas válidas en los datos")
            return {'fecha': None}
        
        # Asegurar que las fechas son datetime
        fechas_dt = pd.to_datetime(fechas_validas, errors='coerce')
        fechas_dt = fechas_dt.dropna()
        
        if len(fechas_dt) == 0:
            st.warning("⚠️ Las fechas en Google Sheets no tienen formato válido")
            return {'fecha': None}
        
        # Ordenar fechas
        fechas_ordenadas = sorted(fechas_dt)
        
        # ✅ CREAR OPCIONES PARA EL SELECTBOX
        fecha_options = []
        fecha_map = {}
        
        for fecha in fechas_ordenadas:
            # Contar registros para cada fecha
            registros_fecha = len(df[df['Fecha'] == fecha])
            
            # Formato: "DD/MM/YYYY (N registros)"
            display_text = f"{fecha.strftime('%d/%m/%Y')} ({registros_fecha} registros)"
            fecha_options.append(display_text)
            fecha_map[display_text] = fecha
        
        # ✅ DETERMINAR ÍNDICE INICIAL
        index_inicial = len(fecha_options) - 1  # Por defecto la más reciente
        
        # Si hay una fecha previamente seleccionada, mantenerla
        if st.session_state.selected_fecha is not None:
            try:
                fecha_anterior = st.session_state.selected_fecha
                for i, (display, fecha_real) in enumerate(fecha_map.items()):
                    if fecha_real == fecha_anterior:
                        index_inicial = i
                        break
            except:
                pass  # Usar default si hay error
        
        # ✅ SELECTBOX PRINCIPAL
        st.markdown("### 📅 Filtros de Análisis")
        
        fecha_seleccionada_str = st.selectbox(
            "Fecha de referencia para análisis", 
            fecha_options, 
            index=index_inicial,
            help="Selecciona la fecha específica para el análisis. Los indicadores se filtrarán por esta fecha exacta.",
            key="fecha_filter_main"
        )
        
        # ✅ OBTENER FECHA REAL SELECCIONADA
        fecha_seleccionada = fecha_map[fecha_seleccionada_str]
        
        # Actualizar session state
        st.session_state.selected_fecha = fecha_seleccionada
        
        # ✅ MOSTRAR INFORMACIÓN DE LA SELECCIÓN
        col1, col2, col3 = st.columns(3)
        
        with col1:
            registros_fecha = len(df[df['Fecha'] == fecha_seleccionada])
            st.metric("Registros en fecha", registros_fecha)
        
        with col2:
            indicadores_fecha = df[df['Fecha'] == fecha_seleccionada]['Codigo'].nunique()
            st.metric("Indicadores únicos", indicadores_fecha)
        
        with col3:
            componentes_fecha = df[df['Fecha'] == fecha_seleccionada]['Componente'].nunique()
            st.metric("Componentes", componentes_fecha)
        
        # ✅ INFORMACIÓN ADICIONAL
        if registros_fecha == 0:
            st.warning(f"⚠️ No hay registros exactos para {fecha_seleccionada.strftime('%d/%m/%Y')}. Se usará la fecha más cercana anterior.")
        else:
            st.success(f"✅ Análisis para {fecha_seleccionada.strftime('%d/%m/%Y')} - {registros_fecha} registros encontrados")
        
        return {'fecha': fecha_seleccionada}
        
    except Exception as e:
        st.error(f"❌ Error al crear filtros: {e}")
        
        # Información de debug
        with st.expander("🔧 Debug de filtros"):
            st.write("**Error:**", str(e))
            if not df.empty:
                st.write("**Columnas disponibles:**", list(df.columns))
                if 'Fecha' in df.columns:
                    st.write("**Muestra de fechas:**", df['Fecha'].head().tolist())
        
        return {'fecha': None}

def create_simple_filters(df):
    """Crear filtros simples - VERSIÓN DE COMPATIBILIDAD"""
    
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

def show_filter_status(df, filters):
    """Mostrar estado de filtros aplicados - OPCIONAL"""
    if st.checkbox("🔧 Mostrar información detallada de filtros", value=False):
        st.markdown("#### 🎛️ Estado de Filtros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Filtros actuales:**")
            for key, value in filters.items():
                if value is not None:
                    if key == 'fecha':
                        valor_str = pd.to_datetime(value).strftime('%d/%m/%Y')
                    else:
                        valor_str = str(value)
                    st.write(f"- **{key.title()}:** {valor_str}")
                else:
                    st.write(f"- **{key.title()}:** Sin filtro")
        
        with col2:
            if filters.get('fecha'):
                fecha_filtro = filters['fecha']
                df_filtrado = df[df['Fecha'] == fecha_filtro]
                
                st.write("**Impacto del filtro:**")
                st.write(f"- **Registros totales:** {len(df)}")
                st.write(f"- **Registros filtrados:** {len(df_filtrado)}")
                
                if not df_filtrado.empty:
                    st.write(f"- **Indicadores únicos:** {df_filtrado['Codigo'].nunique()}")
                    st.write(f"- **Componentes únicos:** {df_filtrado['Componente'].nunique()}")

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

def show_system_info_footer(df, source_info):
    """Mostrar información del sistema - VERSIÓN SIMPLE PARA COMPATIBILIDAD"""
    
    # Mostrar información que antes estaba en encabezado
    if not df.empty:
        st.success(f"Cargados {len(df)} registros")
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
            st.success("Conectado")
        else:
            st.error("Desconectado")
        
        # Botón de actualización
        if st.button("Actualizar", 
                    help="Recarga los datos",
                   key="footer_refresh"):
            current_tab = st.session_state.get('active_tab_index', 0)
            st.session_state.last_load_time = time.time()
            st.session_state.active_tab_index = current_tab
            st.rerun()

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
