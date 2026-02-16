"""
Dashboard ICE - Archivo Principal - VERSIÓN CON FICHAS DESDE GOOGLE SHEETS
ACTUALIZACIÓN: Ya no usa Excel, ahora carga fichas desde pestaña "Fichas" en Google Sheets
"""

import streamlit as st
import pandas as pd
import os
import time
from config import (
    configure_page, create_banner, apply_dark_theme, validate_google_sheets_config,
    show_setup_instructions
)
from data_utils import DataLoader, SheetsDataLoader
from tabs import TabManager
from datetime import datetime, timezone, timedelta

# Configurar zona horaria de Colombia (UTC-5)
COLOMBIA_TZ = timezone(timedelta(hours=-5))

def get_colombia_time():
    """Obtener fecha y hora actual de Colombia"""
    return datetime.now(COLOMBIA_TZ)
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
            # ACTUALIZAR INSTRUCCIONES PARA INCLUIR PESTAÑA FICHAS
            st.markdown("""
            ---
            ### 📋 **NUEVO: Pestaña "Fichas" para información metodológica**
            
            El sistema ahora carga la información metodológica desde una pestaña llamada **"Fichas"** en tu Google Sheets:
            
            1. **Crea una pestaña llamada "Fichas"** en tu Google Sheets
            2. **Estructura requerida de la pestaña "Fichas":**
               - **Primera fila (headers):** `Codigo`, `Nombre_Indicador`, `Definicion`, `Objetivo`, `Area_Tematica`, `Tema`, `Sector`, `Entidad`, `Dependencia`, `Formula_Calculo`, `Variables`, `Unidad_Medida`, `Metodologia_Calculo`, `Tipo_Acumulacion`, `Fuente_Informacion`, `Tipo_Indicador`, `Periodicidad`, `Desagregacion_Geografica`, `Desagregacion_Poblacional`, `Clasificacion_Calidad`, `Clasificacion_Intervencion`, `Observaciones`, `Limitaciones`, `Interpretacion`, `Directivo_Responsable`, `Correo_Directivo`, `Telefono_Contacto`, `Enlaces_Web`, `Soporte_Legal`
            3. **Ejemplo de registro:**
               - **Codigo:** D01-1
               - **Nombre_Indicador:** Porcentaje de datos actualizados
               - **Definicion:** Indica el porcentaje de conjuntos de datos que han sido actualizados...
               - **Objetivo:** Medir la actualización de los datos...
               - *...y así sucesivamente*
            
            ✅ **Ventajas del nuevo sistema:**
            - ✅ Todo en Google Sheets (no más archivos Excel)
            - ✅ Edición colaborativa en tiempo real
            - ✅ Sincronización automática
            - ✅ Acceso desde cualquier lugar
            """)
        
        st.stop()
    
    # CARGA DE DATOS ACTUALIZADA
    try:
        # Cargar datos con información de estado
        df, source_info, fichas_data = load_data_with_status_sheets()
        
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
        
        # Renderizar pestañas CON FICHAS DESDE SHEETS
        tab_manager = TabManager(df, None, fichas_data)
        tab_manager.render_tabs(df, {})  # Pasar diccionario vacío como filtros
        
        # INFORMACIÓN DE ESTADO AL FINAL
        st.markdown("---")
        
        # Información del sistema en expander
        with st.expander("Información del Sistema", expanded=False):
            show_system_info_complete_sheets(df, source_info, fichas_data)
        
    except Exception as e:
        st.error(f"❌ Error crítico en la aplicación: {e}")
        
        # Mostrar detalles para debug
        with st.expander("🔧 Detalles del error"):
            import traceback
            st.code(traceback.format_exc())
        
        # Opciones de recuperación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reintentar", width='stretch'):
                current_tab = st.session_state.get('active_tab_index', 0)
                st.session_state.last_load_time = time.time()
                st.session_state.active_tab_index = current_tab
                st.rerun()
        
        with col2:
            if st.button("🧹 Limpiar Cache", width='stretch'):
                st.cache_data.clear()
                st.session_state.data_timestamp = time.time()
                st.rerun()

def load_data_with_status_sheets():
    """ACTUALIZADO: Cargar datos combinados desde Google Sheets"""
    try:
        # Mostrar estado de carga
        with st.spinner("🔄 Conectando con Google Sheets y combinando datos..."):
            # Cargar datos combinados desde Google Sheets
            data_loader = DataLoader()
            df_loaded = data_loader.load_combined_data()

        # NUEVO: Cargar fichas desde Google Sheets (para la pestaña de fichas)
        with st.spinner("📋 Cargando fichas metodológicas desde Google Sheets..."):
            fichas_loader = SheetsDataLoader()
            fichas_data = fichas_loader.load_fichas_data()

        # Obtener información de la fuente
        source_info = data_loader.get_data_source_info()

        # Mostrar resultados de carga solo si hay problemas
        if df_loaded is None or df_loaded.empty:
            st.info("📋 Google Sheets está vacío o no se pudo conectar")

        if fichas_data is None:
            st.warning("⚠️ No se pudieron cargar las fichas metodológicas desde Google Sheets")
            st.info("💡 Verifica que existe la pestaña 'Fichas' en tu Google Sheets")
        elif fichas_data.empty:
            st.info("📋 La pestaña 'Fichas' está vacía")
        else:
            # Solo mostrar éxito si hay datos
            pass
        
        return df_loaded, source_info, fichas_data
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        # Retornar datos vacíos para mantener funcionalidad
        empty_df = pd.DataFrame(columns=[
            'LINEA DE ACCIÓN', 'COMPONENTE PROPUESTO', 'CATEGORÍA',
            'COD', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
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
            'codigo': registro_mas_reciente.get('COD', 'N/A'),
            'componente': registro_mas_reciente.get('COMPONENTE PROPUESTO', registro_mas_reciente.get('Componente', 'N/A'))
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
        
        ### 📋 Para fichas metodológicas:
        1. Crea una pestaña llamada **"Fichas"** en tu Google Sheets
        2. Agrega las fichas metodológicas de tus indicadores
        3. Podrás generar PDFs con información completa
        """)
        return True
    
    # Verificar columnas esenciales (nombres actualizados)
    required_columns = ['COD', 'Fecha', 'Valor']
    # Verificar columnas con nombres flexibles (ahora estandarizados)
    has_componente = 'Componente' in df.columns
    has_categoria = 'Categoria' in df.columns
    has_indicador = 'Indicador' in df.columns

    missing_columns = [col for col in required_columns if col not in df.columns]
    if not has_componente:
        missing_columns.append('COMPONENTE PROPUESTO')
    if not has_categoria:
        missing_columns.append('CATEGORÍA')
    if not has_indicador:
        missing_columns.append('Indicador')
    
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
                st.dataframe(df.head(3), width='stretch')
        
        return False
    
    # Verificar datos válidos
    datos_validos = df.dropna(subset=['COD', 'Fecha', 'Valor'])
    if datos_validos.empty:
        st.warning("⚠️ Los datos en Google Sheets están incompletos")
        st.info("Hay registros pero faltan valores en campos esenciales")
        return True
    
    # Información positiva sobre la estructura
    registros_invalidos = len(df) - len(datos_validos)
    if registros_invalidos > 0:
        st.info(f"📊 {len(datos_validos)} registros válidos de {len(df)} totales")
    
    return True

def show_system_info_complete_sheets(df, source_info, fichas_data):
    """ACTUALIZADO: Mostrar información completa del sistema con fichas de Sheets"""
    
    # Información de datos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Estadísticas de Datos")
        
        if not df.empty:
            st.success(f"**Total registros:** {len(df)}")
            
            indicadores_unicos = df['COD'].nunique()
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
            
            # NUEVO: Estado de pestaña Fichas
            if connection_info.get('fichas_available', False):
                st.success("**Pestaña 'Fichas':** Disponible")
            else:
                st.warning("**Pestaña 'Fichas':** No disponible")
        else:
            st.error("**Google Sheets:** Desconectado")
        
        # Estado Fichas metodológicas
        if fichas_data is not None and not fichas_data.empty:
            st.success(f"**Fichas metodológicas:** {len(fichas_data)} fichas")
        elif fichas_data is not None and fichas_data.empty:
            st.warning("**Fichas metodológicas:** Pestaña vacía")
        else:
            st.error("**Fichas metodológicas:** No disponibles")
        
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
        st.info(f"**Cache timestamp:** {get_colombia_time().strftime('%d/%m/%Y %H:%M:%S COT')}")
    
    # Controles de gestión
    st.markdown("#### ⚙️ Controles de Sistema")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🔄 Actualizar Datos", 
                    help="Recarga los datos desde Google Sheets",
                    width='stretch'):
            current_tab = st.session_state.get('active_tab_index', 0)
            st.session_state.last_load_time = time.time()
            st.session_state.active_tab_index = current_tab
            st.rerun()
    
    with col4:
        if st.button("🧹 Limpiar Cache", 
                    help="Limpia el cache de Streamlit",
                    width='stretch'):
            st.cache_data.clear()
            st.session_state.data_timestamp = time.time()
            st.success("Cache limpiado")
            time.sleep(1)
            st.rerun()
    
    with col5:
        if st.button("🔧 Test Conexión", 
                    help="Probar conexión con Google Sheets",
                    width='stretch'):
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
    
    # NUEVA SECCIÓN: Información de Fichas Metodológicas
    if fichas_data is not None:
        st.markdown("#### 📋 Detalles de Fichas Metodológicas")
        
        if not fichas_data.empty:
            # Estadísticas de fichas
            col6, col7, col8 = st.columns(3)
            
            with col6:
                total_fichas = len(fichas_data)
                st.metric("Total Fichas", total_fichas)
            
            with col7:
                if 'COD' in fichas_data.columns:
                    fichas_con_codigo = fichas_data['COD'].notna().sum()
                    st.metric("Fichas Válidas", fichas_con_codigo)
                else:
                    st.metric("Fichas Válidas", "N/A")
            
            with col8:
                if 'Definicion' in fichas_data.columns:
                    fichas_con_definicion = fichas_data['Definicion'].notna().sum()
                    st.metric("Con Definición", fichas_con_definicion)
                else:
                    st.metric("Con Definición", "N/A")
            
            # Mostrar muestra de fichas
            with st.expander("Ver muestra de fichas metodológicas"):
                # Seleccionar columnas más importantes para mostrar
                columnas_importantes = ['Codigo', 'Nombre_Indicador', 'Definicion', 'Objetivo', 'Area_Tematica', 'Entidad']
                columnas_disponibles = [col for col in columnas_importantes if col in fichas_data.columns]
                
                if columnas_disponibles:
                    st.dataframe(
                        fichas_data[columnas_disponibles].head(5), 
                        width='stretch'
                    )
                else:
                    st.dataframe(fichas_data.head(5), width='stretch')
        else:
            st.info("La pestaña 'Fichas' existe pero está vacía")
            
            # Botón para crear ficha de ejemplo
            if st.button("➕ Crear ficha de ejemplo", help="Crea una ficha metodológica de ejemplo"):
                try:
                    from google_sheets_manager import GoogleSheetsManager
                    sheets_manager = GoogleSheetsManager()
                    
                    # Crear ficha de ejemplo
                    ficha_ejemplo = {
                        'Codigo': 'D01-1',
                        'Nombre_Indicador': 'Porcentaje de datos actualizados',
                        'Definicion': 'Indica el porcentaje de conjuntos de datos que han sido actualizados en los últimos 30 días',
                        'Objetivo': 'Medir la actualización constante de los datos publicados',
                        'Area_Tematica': 'Datos Abiertos',
                        'Tema': 'Calidad de Datos',
                        'Sector': 'Tecnología',
                        'Entidad': 'IDECA',
                        'Dependencia': 'Subdirección de Información',
                        'Formula_Calculo': '(Datasets actualizados últimos 30 días / Total datasets) * 100',
                        'Variables': 'Datasets actualizados, Total datasets',
                        'Unidad_Medida': 'Porcentaje',
                        'Metodologia_Calculo': 'Conteo directo de datasets con fecha de actualización en los últimos 30 días',
                        'Tipo_Acumulacion': 'Promedio',
                        'Fuente_Informacion': 'Sistema de gestión de datos IDECA',
                        'Tipo_Indicador': 'Eficiencia',
                        'Periodicidad': 'Mensual',
                        'Desagregacion_Geografica': 'Distrital',
                        'Desagregacion_Poblacional': 'No aplica',
                        'Clasificacion_Calidad': 'Registro administrativo',
                        'Clasificacion_Intervencion': 'Gestión',
                        'Observaciones': 'Se considera actualizado si la fecha de modificación es menor a 30 días',
                        'Limitaciones': 'Depende de la configuración de actualización automática de cada dataset',
                        'Interpretacion': 'Mayor porcentaje indica mejor gestión de actualización de datos',
                        'Directivo_Responsable': 'Director IDECA',
                        'Correo_Directivo': 'director@ideca.gov.co',
                        'Telefono_Contacto': '3443000',
                        'Enlaces_Web': 'https://www.ideca.gov.co',
                        'Soporte_Legal': 'Decreto de Datos Abiertos de Bogotá'
                    }
                    
                    success = sheets_manager.add_ficha_record(ficha_ejemplo)
                    
                    if success:
                        st.success("✅ Ficha de ejemplo creada correctamente")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al crear ficha de ejemplo")
                        
                except Exception as e:
                    st.error(f"❌ Error al crear ficha de ejemplo: {e}")
    else:
        st.warning("⚠️ No se encontró información de fichas metodológicas")

def show_error_message():
    """Mostrar mensaje de error detallado - ACTUALIZADO PARA FICHAS"""
    st.error("""
    ### ❌ Error al cargar datos desde Google Sheets

    **Posibles causas y soluciones:**
    1. **Configuración incorrecta:** Verifica el archivo `secrets.toml`
    2. **Permisos:** El Service Account debe tener acceso de "Editor" a la hoja
    3. **Estructura de datos:** La hoja debe tener las columnas correctas
    4. **Pestaña 'Fichas':** Verifica que existe para las fichas metodológicas
    5. **Conectividad:** Verifica tu conexión a internet
    6. **URL incorrecta:** Verifica que la URL de Google Sheets sea correcta
    """)
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Ver instrucciones de configuración", width='stretch'):
            show_setup_instructions()
    
    with col2:
        if st.button("🔄 Intentar reconectar", width='stretch'):
            st.rerun()

if __name__ == "__main__":
    main()
