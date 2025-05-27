"""
Dashboard ICE - Archivo Principal - Versión corregida
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
"""

import streamlit as st
import os
import pandas as pd
from config import configure_page, apply_dark_theme, CSV_FILENAME
from data_utils import DataLoader
from filters import FilterManager
from tabs import TabManager

def main():
    """Función principal del dashboard"""
    
    # Configurar página
    configure_page()
    apply_dark_theme()
    
    # Título principal
    st.title("📊 Dashboard de Indicadores ICE")
    st.markdown("Sistema de monitoreo y seguimiento de indicadores")
    
    # Añadir opción de debug
    debug_mode = st.sidebar.checkbox("Modo Debug", value=True)
    
    # Cargar datos
    data_loader = DataLoader()
    
    if debug_mode:
        st.sidebar.header("🔧 Información de Debug")
    
    df = data_loader.load_data()
    
    if df is not None and len(df) > 0:
        try:
            # Mostrar información básica de los datos
            if debug_mode:
                with st.expander("📋 Información de los datos cargados"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total registros", len(df))
                    with col2:
                        st.metric("Indicadores únicos", df['Indicador'].nunique())
                    with col3:
                        st.metric("Fechas únicas", df['Fecha'].nunique())
                    
                    st.subheader("Primeros 5 registros:")
                    st.dataframe(df.head())
                    
                    st.subheader("Información por columna:")
                    st.write(df.dtypes)
            
            # Crear sistema de filtros
            filter_manager = FilterManager(df)
            filters = filter_manager.create_sidebar_filters()
            
            # Aplicar filtros
            df_filtrado = filter_manager.apply_filters(df)
            
            if debug_mode:
                st.sidebar.write(f"Registros después del filtro: {len(df_filtrado)}")
            
            # Mostrar información de filtros activos
            active_filters = filter_manager.get_filter_info()
            if active_filters:
                st.sidebar.markdown("**🔍 Filtros activos:**")
                for filter_info in active_filters:
                    st.sidebar.markdown(f"- {filter_info}")
            
            # Verificar que hay datos después del filtro
            if len(df_filtrado) == 0:
                st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados. Intenta cambiar los filtros.")
                st.info("💡 Sugerencia: Selecciona 'Todos' en los filtros para ver todos los datos disponibles.")
                
                # Mostrar datos sin filtrar como referencia
                with st.expander("Ver todos los datos disponibles"):
                    st.dataframe(df)
            else:
                # Renderizar pestañas
                tab_manager = TabManager(df, data_loader.csv_path)
                tab_manager.render_tabs(df_filtrado, filters)
            
            # Información adicional en sidebar
            render_sidebar_info(debug_mode)
            
        except Exception as e:
            st.error(f"❌ Error al procesar datos: {e}")
            st.info("🔧 Activa el modo debug para ver más información.")
            
            if debug_mode:
                st.exception(e)
    
    else:
        show_error_message()

def render_sidebar_info(debug_mode=False):
    """Renderizar información adicional en la barra lateral"""
    st.sidebar.markdown("---")
    
    if debug_mode:
        st.sidebar.header("🎯 Estado del Sistema")
        try:
            # Información del entorno
            st.sidebar.write(f"Python: {os.sys.version.split()[0]}")
            st.sidebar.write(f"Pandas: {pd.__version__}")
            st.sidebar.write(f"Streamlit: {st.__version__}")
            
            # Información del directorio
            current_dir = os.getcwd()
            st.sidebar.write(f"Directorio actual: {os.path.basename(current_dir)}")
            
        except Exception as e:
            st.sidebar.error(f"Error obteniendo info del sistema: {e}")
    
    st.sidebar.info("""
    📊 **Dashboard ICE**
    
    Este dashboard permite monitorear y analizar los indicadores clave de desempeño de la Infraestructura de Conocimiento Espacial, con visualizaciones interactivas y cálculos automáticos de puntajes.
    
    **Navegación:**
    - 📈 **Resumen General**: Vista global de indicadores
    - 🏗️ **Por Componente**: Análisis detallado por área
    - 📊 **Evolución**: Tendencias temporales
    - 📋 **Tabla Dinámica**: Análisis cruzado
    - ✏️ **Edición**: Actualizar valores
    """)
    
    # Créditos
    st.sidebar.markdown("---")
    st.sidebar.markdown("**© 2025 Dashboard ICE**")
    st.sidebar.markdown("**IDECA - Bogotá D.C.**")

def show_error_message():
    """Mostrar mensaje de error cuando no se puede cargar el archivo"""
    st.error(f"""
    ### ❌ Error al cargar el archivo de indicadores

    No se pudo encontrar o abrir el archivo `{CSV_FILENAME}`. 

    **🛠️ Posibles soluciones:**
    
    1. **Verificar archivo**: Asegúrate de que el archivo `{CSV_FILENAME}` existe
    2. **Ubicación**: El archivo debe estar en el mismo directorio que este script
    3. **Formato**: Verifica que usa punto y coma (;) como separador
    4. **Encoding**: Asegúrate de que está guardado en UTF-8
    5. **Permisos**: Comprueba que tienes permisos de lectura
    """)

    # Mostrar información de diagnóstico
    try:
        current_dir = os.getcwd()
        files_in_dir = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
        
        st.info(f"""
        **🔍 Información de diagnóstico:**
        - **Directorio actual**: `{current_dir}`
        - **Archivos CSV encontrados**: {', '.join(files_in_dir) if files_in_dir else 'Ninguno'}
        - **Archivo buscado**: `{CSV_FILENAME}`
        """)
        
        if files_in_dir:
            st.success("💡 Se encontraron archivos CSV. Verifica que el nombre coincida exactamente.")
        
    except Exception as e:
        st.warning(f"⚠️ No se pudo obtener información del directorio: {e}")

def check_streamlit_issues():
    """Verificar problemas comunes de Streamlit"""
    try:
        # Verificar versión de Streamlit
        import streamlit as st
        version = st.__version__
        
        # Sugerir actualización si es necesario
        if version < "1.28.0":
            st.sidebar.warning(f"⚠️ Streamlit {version} detectado. Considera actualizar a la versión más reciente.")
            
    except Exception as e:
        st.sidebar.error(f"Error verificando Streamlit: {e}")

if __name__ == "__main__":
    # Verificar problemas de Streamlit
    check_streamlit_issues()
    
    # Ejecutar aplicación principal
    main()
