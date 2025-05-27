"""
Dashboard ICE - Archivo Principal Simplificado
Sistema de monitoreo y seguimiento de indicadores de la Infraestructura de Conocimiento Espacial
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard ICE - IDECA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #262730 0%, #1e1e1e 100%);
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
    }
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Cargar datos desde el archivo CSV"""
    try:
        csv_filename = "IndicadoresICE.csv"
        
        # Verificar si el archivo existe
        if not os.path.exists(csv_filename):
            st.error(f"❌ No se encontró el archivo {csv_filename}")
            return None
        
        # Cargar el archivo
        df = pd.read_csv(csv_filename, sep=";", encoding='utf-8-sig')
        
        # Renombrar columnas
        column_mapping = {
            'LINEA DE ACCIÓN': 'Linea_Accion',
            'COMPONENTE PROPUESTO': 'Componente',
            'CATEGORÍA': 'Categoria',
            'COD': 'Codigo',
            'Nombre de indicador': 'Indicador',
            'Valor': 'Valor',
            'Fecha': 'Fecha'
        }
        
        for original, nuevo in column_mapping.items():
            if original in df.columns:
                df = df.rename(columns={original: nuevo})
        
        # Procesar fechas
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
        
        # Procesar valores
        if df['Valor'].dtype == 'object':
            df['Valor'] = df['Valor'].astype(str).str.replace(',', '.').astype(float)
        
        # Añadir columnas calculadas
        df['Meta'] = 1.0
        df['Peso'] = 100 / df['Indicador'].nunique()
        df['Cumplimiento'] = df['Valor'] * 100
        df['Puntaje_Ponderado'] = df['Cumplimiento'] * df['Peso'] / 100
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return None

def create_filters(df):
    """Crear filtros en la sidebar"""
    st.sidebar.header("🔍 Filtros")
    
    filters = {}
    
    # Filtro de fecha
    if 'Fecha' in df.columns:
        fechas = sorted(df['Fecha'].dropna().unique())
        if fechas:
            filters['fecha'] = st.sidebar.selectbox(
                "📅 Fecha",
                fechas,
                index=len(fechas)-1,
                format_func=lambda x: x.strftime('%d/%m/%Y')
            )
    
    # Filtro de componente
    if 'Componente' in df.columns:
        componentes = ["Todos"] + sorted(df['Componente'].dropna().unique().tolist())
        comp_selected = st.sidebar.selectbox("🏗️ Componente", componentes)
        filters['componente'] = None if comp_selected == "Todos" else comp_selected
    
    # Filtro de categoría
    if 'Categoria' in df.columns:
        if filters.get('componente'):
            categorias = df[df['Componente'] == filters['componente']]['Categoria'].dropna().unique()
        else:
            categorias = df['Categoria'].dropna().unique()
        
        categorias = ["Todas"] + sorted(categorias.tolist())
        cat_selected = st.sidebar.selectbox("📂 Categoría", categorias)
        filters['categoria'] = None if cat_selected == "Todas" else cat_selected
    
    return filters

def apply_filters(df, filters):
    """Aplicar filtros al DataFrame"""
    df_filtered = df.copy()
    
    if filters.get('fecha') is not None:
        df_filtered = df_filtered[df_filtered['Fecha'] == filters['fecha']]
    
    if filters.get('componente'):
        df_filtered = df_filtered[df_filtered['Componente'] == filters['componente']]
    
    if filters.get('categoria'):
        df_filtered = df_filtered[df_filtered['Categoria'] == filters['categoria']]
    
    return df_filtered

def create_radar_chart(df):
    """Crear gráfico de radar"""
    try:
        if len(df) == 0:
            return go.Figure().add_annotation(text="No hay datos disponibles")
        
        # Agrupar por componente
        radar_data = df.groupby('Componente')['Cumplimiento'].mean().reset_index()
        
        if len(radar_data) < 3:
            return go.Figure().add_annotation(text="Se requieren al menos 3 componentes")
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_data['Cumplimiento'],
            theta=radar_data['Componente'],
            fill='toself',
            name='Cumplimiento',
            line_color='#4CAF50'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title="Diagrama de Radar por Componente",
            template="plotly_dark"
        )
        
        return fig
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {e}")

def create_evolution_chart(df, indicador=None):
    """Crear gráfico de evolución"""
    try:
        if indicador:
            df_plot = df[df['Indicador'] == indicador]
            title = f"Evolución: {indicador}"
        else:
            df_plot = df.groupby('Fecha')['Valor'].mean().reset_index()
            title = "Evolución General"
        
        if len(df_plot) == 0:
            return go.Figure().add_annotation(text="No hay datos disponibles")
        
        fig = px.line(df_plot, x='Fecha', y='Valor', title=title, template="plotly_dark")
        fig.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Meta")
        
        return fig
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {e}")

def create_component_chart(df):
    """Crear gráfico por componente"""
    try:
        if len(df) == 0:
            return go.Figure().add_annotation(text="No hay datos disponibles")
        
        comp_data = df.groupby('Componente')['Puntaje_Ponderado'].sum().reset_index()
        comp_data = comp_data.sort_values('Puntaje_Ponderado', ascending=True)
        
        fig = px.bar(
            comp_data,
            y='Componente',
            x='Puntaje_Ponderado',
            title="Puntaje por Componente",
            template="plotly_dark",
            orientation='h'
        )
        
        return fig
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {e}")

def main():
    """Función principal"""
    st.title("📊 Dashboard de Indicadores ICE")
    st.markdown("Sistema de monitoreo y seguimiento de indicadores")
    
    # Cargar datos
    df = load_data()
    
    if df is None:
        st.stop()
    
    # Mostrar información básica
    with st.expander("ℹ️ Información de los datos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total registros", len(df))
        with col2:
            st.metric("Indicadores únicos", df['Indicador'].nunique())
        with col3:
            st.metric("Fechas únicas", df['Fecha'].nunique())
    
    # Crear filtros
    filters = create_filters(df)
    df_filtered = apply_filters(df, filters)
    
    # Mostrar filtros aplicados
    if any(filters.values()):
        st.sidebar.markdown("**🎯 Filtros activos:**")
        for key, value in filters.items():
            if value:
                if key == 'fecha':
                    st.sidebar.markdown(f"- 📅 {key.title()}: {value.strftime('%d/%m/%Y')}")
                else:
                    st.sidebar.markdown(f"- 🔍 {key.title()}: {value}")
    
    # Verificar que hay datos después del filtro
    if len(df_filtered) == 0:
        st.warning("⚠️ No hay datos para los filtros seleccionados")
        st.stop()
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Resumen General", 
        "🏗️ Por Componente", 
        "📊 Evolución", 
        "📋 Datos"
    ])
    
    with tab1:
        st.header("📈 Resumen General")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            puntaje_general = df_filtered['Puntaje_Ponderado'].sum()
            st.metric("Puntaje General", f"{puntaje_general:.1f}")
        with col2:
            valor_promedio = df_filtered['Valor'].mean()
            st.metric("Valor Promedio", f"{valor_promedio:.2f}")
        with col3:
            cumplimiento_promedio = df_filtered['Cumplimiento'].mean()
            st.metric("Cumplimiento %", f"{cumplimiento_promedio:.1f}%")
        
        # Gráfico de radar
        radar_fig = create_radar_chart(df_filtered)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Gráfico por componente
        comp_fig = create_component_chart(df_filtered)
        st.plotly_chart(comp_fig, use_container_width=True)
    
    with tab2:
        st.header("🏗️ Análisis por Componente")
        
        if 'Componente' in df.columns:
            componentes = df['Componente'].unique()
            componente_selected = st.selectbox("Seleccionar componente:", componentes)
            
            df_comp = df[df['Componente'] == componente_selected]
            
            # Métricas del componente
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Indicadores", df_comp['Indicador'].nunique())
            with col2:
                st.metric("Valor promedio", f"{df_comp['Valor'].mean():.2f}")
            
            # Gráfico de evolución del componente
            evol_fig = create_evolution_chart(df_comp)
            st.plotly_chart(evol_fig, use_container_width=True)
            
            # Tabla de indicadores
            st.subheader("Indicadores del componente")
            display_df = df_comp[['Indicador', 'Categoria', 'Valor', 'Fecha']].copy()
            display_df['Fecha'] = display_df['Fecha'].dt.strftime('%d/%m/%Y')
            st.dataframe(display_df, use_container_width=True)
    
    with tab3:
        st.header("📊 Evolución de Indicadores")
        
        # Selector de indicador
        if 'Indicador' in df.columns:
            indicadores = ["Todos"] + df['Indicador'].unique().tolist()
            indicador_selected = st.selectbox("Seleccionar indicador:", indicadores)
            
            if indicador_selected == "Todos":
                evol_fig = create_evolution_chart(df)
            else:
                evol_fig = create_evolution_chart(df, indicador_selected)
            
            st.plotly_chart(evol_fig, use_container_width=True)
    
    with tab4:
        st.header("📋 Datos")
        
        # Mostrar datos filtrados
        display_df = df_filtered.copy()
        if 'Fecha' in display_df.columns:
            display_df['Fecha'] = display_df['Fecha'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Opción de descarga
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos como CSV",
            data=csv,
            file_name=f"datos_ice_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
