"""
Dashboard ICE - Archivo Principal
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
"""

import streamlit as st
import os
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
    st.title("Dashboard de Indicadores ICE")
    st.markdown("Sistema de monitoreo y seguimiento de indicadores")
    
    # Cargar datos
    data_loader = DataLoader()
    df = data_loader.load_data()
    
    if df is not None:
        try:
            # Crear sistema de filtros
            filter_manager = FilterManager(df)
            filters = filter_manager.create_sidebar_filters()
            
            # Aplicar filtros
            df_filtrado = filter_manager.apply_filters(df)
            
            # Mostrar información de filtros activos
            active_filters = filter_manager.get_filter_info()
            if active_filters:
                st.sidebar.markdown("**Filtros activos:**")
                for filter_info in active_filters:
                    st.sidebar.markdown(f"- {filter_info}")
            
            # Renderizar pestañas
            tab_manager = TabManager(df, data_loader.csv_path)
            tab_manager.render_tabs(df_filtrado, filters)
            
            # Información adicional en sidebar
            render_sidebar_info()
            
        except Exception as e:
            st.error(f"Error al procesar datos: {e}")
            st.info("Verifica que el archivo CSV contenga todas las columnas requeridas")
    
    else:
        show_error_message()

def render_sidebar_info():
    """Renderizar información adicional en la barra lateral"""
    st.sidebar.markdown("---")
    st.sidebar.info("""
    Este dashboard permite monitorear y analizar los indicadores clave de desempeño,
    con visualizaciones interactivas y cálculos automáticos de puntajes.
    """)
    
    # Créditos
    st.sidebar.markdown("---")
    st.sidebar.text("© 2025 Dashboard ICE")
    st.sidebar.text("IDECA - Bogotá D.C.")

def show_error_message():
    """Mostrar mensaje de error cuando no se puede cargar el archivo"""
    st.error(f"""
    ### Error al cargar el archivo de indicadores

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
