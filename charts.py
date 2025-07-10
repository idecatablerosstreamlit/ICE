# Agregar esta función corregida al archivo charts.py

@staticmethod
def _get_latest_values_by_indicator(df):
    """Obtener el valor más reciente de cada indicador - VERSIÓN CORREGIDA"""
    try:
        if df.empty:
            return df
        
        # Verificar columnas esenciales
        required_columns = ['Codigo', 'Fecha', 'Valor']
        if not all(col in df.columns for col in required_columns):
            import streamlit as st
            st.error(f"Faltan columnas esenciales: {required_columns}")
            return df
        
        # Limpiar datos
        df_clean = df.dropna(subset=['Codigo', 'Fecha', 'Valor']).copy()
        
        if df_clean.empty:
            import streamlit as st
            st.warning("No hay datos válidos para procesar")
            return df
        
        # Asegurar que las fechas son datetime
        if not pd.api.types.is_datetime64_any_dtype(df_clean['Fecha']):
            df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'], errors='coerce')
            df_clean = df_clean.dropna(subset=['Fecha'])
        
        if df_clean.empty:
            import streamlit as st
            st.warning("No hay fechas válidas")
            return df
        
        # Obtener valores más recientes de forma segura
        result_rows = []
        
        for codigo in df_clean['Codigo'].unique():
            if pd.isna(codigo):
                continue
                
            # Filtrar datos para este código
            codigo_data = df_clean[df_clean['Codigo'] == codigo].copy()
            
            if codigo_data.empty:
                continue
            
            # Ordenar por fecha y tomar el más reciente
            codigo_data_sorted = codigo_data.sort_values('Fecha')
            latest_row = codigo_data_sorted.iloc[-1]
            
            result_rows.append(latest_row)
        
        if not result_rows:
            import streamlit as st
            st.warning("No se pudieron procesar los datos")
            return df
        
        # Crear DataFrame resultado
        result_df = pd.DataFrame(result_rows).reset_index(drop=True)
        
        return result_df
        
    except Exception as e:
        import streamlit as st
        st.error(f"Error al obtener valores más recientes en gráficos: {e}")
        return df
