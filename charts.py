"""
Módulo de gráficos para el Dashboard ICE - VERSIÓN COMPLETA CON FILTROS CORREGIDOS
Generación de visualizaciones y métricas para el sistema de monitoreo
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc
from datetime import datetime, timedelta

class ChartGenerator:
    """Generador de gráficos para el Dashboard ICE"""
    
    @staticmethod
    def gauge_chart(value, title="Puntaje General ICE", max_value=1.0):
        """Crear gráfico de velocímetro"""
        try:
            # Normalizar valor
            normalized_value = min(max(value, 0), max_value)
            percentage = (normalized_value / max_value) * 100
            
            # Determinar color basado en el valor
            if percentage >= 80:
                color = "#2E8B57"  # Verde
            elif percentage >= 60:
                color = "#FFD700"  # Amarillo
            elif percentage >= 40:
                color = "#FFA500"  # Naranja
            else:
                color = "#DC143C"  # Rojo
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': title, 'font': {'size': 16}},
                delta={'reference': 70, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': '#ffcccc'},
                        {'range': [40, 60], 'color': '#ffffcc'},
                        {'range': [60, 80], 'color': '#ccffcc'},
                        {'range': [80, 100], 'color': '#ccffff'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en gráfico de velocímetro: {e}")
            return ChartGenerator._create_error_chart("Error en velocímetro")
    
    @staticmethod
    def radar_chart(df, filters=None):
        """Crear gráfico de radar por componentes - CORREGIDO PARA USAR DATOS FILTRADOS"""
        try:
            if df.empty:
                return ChartGenerator._create_empty_chart("No hay datos disponibles")
            
            # ✅ DETERMINAR SI USAR DATOS YA FILTRADOS O OBTENER MÁS RECIENTES
            # Si el DataFrame viene con pocos registros, probablemente ya está filtrado por fecha
            total_indicadores = df['COD'].nunique() if 'COD' in df.columns else 0
            
            # Si hay filtros de fecha aplicados, usar los datos tal como vienen
            if filters and filters.get('fecha') is not None:
                # Los datos ya vienen filtrados por fecha, usarlos directamente
                df_latest = df
            else:
                # No hay filtro de fecha, obtener valores más recientes por indicador
                df_latest = ChartGenerator._get_latest_values_by_indicator(df)
            
            if df_latest.empty:
                return ChartGenerator._create_empty_chart("No hay datos para mostrar")
            
            # Verificar columnas necesarias
            if 'Componente' not in df_latest.columns or 'Valor_Normalizado' not in df_latest.columns:
                return ChartGenerator._create_empty_chart("Faltan columnas necesarias")
            
            # Agrupar por componente
            componentes = df_latest.groupby('Componente')['Valor_Normalizado'].mean().reset_index()
            
            if componentes.empty:
                return ChartGenerator._create_empty_chart("No hay componentes para mostrar")
            
            # Crear gráfico de radar
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=componentes['Valor_Normalizado'],
                theta=componentes['Componente'],
                fill='toself',
                name='Puntaje por Componente',
                line=dict(color='#4472C4'),
                fillcolor='rgba(68, 114, 196, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickformat='.2%'
                    )
                ),
                showlegend=True,
                title="Radar de Componentes ICE",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en gráfico de radar: {e}")
            return ChartGenerator._create_error_chart("Error en radar")
    
    @staticmethod
    def component_bar_chart(puntajes_componente):
        """Crear gráfico de barras por componente"""
        try:
            if puntajes_componente.empty:
                return ChartGenerator._create_empty_chart("No hay datos de componentes")
            
            # Ordenar por puntaje
            puntajes_sorted = puntajes_componente.sort_values('Puntaje_Ponderado', ascending=True)
            
            # Crear colores basados en puntajes
            colors = []
            for score in puntajes_sorted['Puntaje_Ponderado']:
                if score >= 0.8:
                    colors.append('#2E8B57')  # Verde
                elif score >= 0.6:
                    colors.append('#FFD700')  # Amarillo
                elif score >= 0.4:
                    colors.append('#FFA500')  # Naranja
                else:
                    colors.append('#DC143C')  # Rojo
            
            fig = go.Figure(data=[
                go.Bar(
                    y=puntajes_sorted['Componente'],
                    x=puntajes_sorted['Puntaje_Ponderado'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{score:.1%}" for score in puntajes_sorted['Puntaje_Ponderado']],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Puntajes por Componente",
                xaxis_title="Puntaje Normalizado",
                yaxis_title="Componente",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(tickformat='.0%', range=[0, 1])
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en gráfico de barras: {e}")
            return ChartGenerator._create_error_chart("Error en barras")
    
    @staticmethod
    def evolution_chart(df, indicador=None, componente=None, tipo_grafico="Línea", mostrar_meta=True):
        """Crear gráfico de evolución temporal"""
        try:
            if df.empty:
                return ChartGenerator._create_empty_chart("No hay datos de evolución")
            
            # Filtrar datos
            df_filtered = df.copy()
            
            if indicador:
                df_filtered = df_filtered[df_filtered['Indicador'] == indicador]
            elif componente:
                df_filtered = df_filtered[df_filtered['Componente'] == componente]
            
            if df_filtered.empty:
                return ChartGenerator._create_empty_chart("No hay datos para el filtro seleccionado")
            
            # Preparar datos para el gráfico
            if indicador:
                # Gráfico de un indicador específico
                df_plot = df_filtered.sort_values('Fecha')
                
                if tipo_grafico == "Línea":
                    fig = px.line(
                        df_plot, 
                        x='Fecha', 
                        y='Valor_Normalizado',
                        title=f"Evolución: {indicador}",
                        markers=True
                    )
                else:  # Barras
                    fig = px.bar(
                        df_plot, 
                        x='Fecha', 
                        y='Valor_Normalizado',
                        title=f"Evolución: {indicador}"
                    )
                
                fig.update_traces(line=dict(color='#4472C4'), marker=dict(color='#4472C4'))
                
            else:
                # Gráfico de evolución general (promedio)
                df_grouped = df_filtered.groupby('Fecha')['Valor_Normalizado'].mean().reset_index()
                
                if tipo_grafico == "Línea":
                    fig = px.line(
                        df_grouped, 
                        x='Fecha', 
                        y='Valor_Normalizado',
                        title="Evolución General (Promedio)",
                        markers=True
                    )
                else:  # Barras
                    fig = px.bar(
                        df_grouped, 
                        x='Fecha', 
                        y='Valor_Normalizado',
                        title="Evolución General (Promedio)"
                    )
                
                fig.update_traces(line=dict(color='#5B9BD5'), marker=dict(color='#5B9BD5'))
            
            # Añadir línea de meta si se solicita
            if mostrar_meta:
                fig.add_hline(
                    y=1.0, 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text="Meta (100%)"
                )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis=dict(tickformat='.0%', range=[0, 1.1]),
                xaxis_title="Fecha",
                yaxis_title="Valor Normalizado"
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en gráfico de evolución: {e}")
            return ChartGenerator._create_error_chart("Error en evolución")
    
    @staticmethod
    def horizontal_bar_chart(df, componente=None, categoria=None, fecha_filtro=None):
        """Crear gráfico de barras horizontales para categorías - CORREGIDO"""
        try:
            if df.empty:
                return ChartGenerator._create_empty_chart("No hay datos disponibles")
            
            # Filtrar por componente si se especifica
            df_filtered = df.copy()
            if componente:
                df_filtered = df_filtered[df_filtered['Componente'] == componente]
            
            if df_filtered.empty:
                return ChartGenerator._create_empty_chart("No hay datos para el componente seleccionado")
            
            # ✅ APLICAR FILTRO DE FECHA SI SE ESPECIFICA
            if fecha_filtro is not None:
                df_fecha = df_filtered[df_filtered['Fecha'] == fecha_filtro]
                if not df_fecha.empty:
                    df_filtered = df_fecha
                else:
                    # Usar fecha más cercana
                    fechas_disponibles = df_filtered['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= pd.to_datetime(fecha_filtro)]
                    if not fecha_mas_cercana.empty:
                        df_filtered = df_filtered[df_filtered['Fecha'] == fecha_mas_cercana.iloc[-1]]
                    else:
                        df_filtered = df_filtered[df_filtered['Fecha'] == fechas_disponibles.iloc[0]]
            else:
                # Obtener valores más recientes
                df_filtered = ChartGenerator._get_latest_values_by_indicator(df_filtered)
            
            # Agrupar por categoría
            if 'Categoria' not in df_filtered.columns:
                return ChartGenerator._create_empty_chart("No hay información de categorías")
            
            puntajes_categoria = df_filtered.groupby('Categoria')['Valor_Normalizado'].mean().reset_index()
            puntajes_categoria = puntajes_categoria.sort_values('Valor_Normalizado', ascending=True)
            
            # Crear colores
            colors = []
            for score in puntajes_categoria['Valor_Normalizado']:
                if score >= 0.8:
                    colors.append('#2E8B57')
                elif score >= 0.6:
                    colors.append('#FFD700')
                elif score >= 0.4:
                    colors.append('#FFA500')
                else:
                    colors.append('#DC143C')
            
            fig = go.Figure(data=[
                go.Bar(
                    y=puntajes_categoria['Categoria'],
                    x=puntajes_categoria['Valor_Normalizado'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{score:.1%}" for score in puntajes_categoria['Valor_Normalizado']],
                    textposition='auto'
                )
            ])
            
            titulo = f"Puntajes por Categoría - {componente}" if componente else "Puntajes por Categoría"
            
            fig.update_layout(
                title=titulo,
                xaxis_title="Puntaje Normalizado",
                yaxis_title="Categoría",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(tickformat='.0%', range=[0, 1])
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en gráfico horizontal: {e}")
            return ChartGenerator._create_error_chart("Error en barras horizontales")
    
    @staticmethod
    def radar_chart_categories(df, componente=None, categoria=None, fecha_filtro=None):
        """Crear gráfico de radar por categorías - CORREGIDO"""
        try:
            if df.empty:
                return ChartGenerator._create_empty_chart("No hay datos disponibles")
            
            # Filtrar por componente si se especifica
            df_filtered = df.copy()
            if componente:
                df_filtered = df_filtered[df_filtered['Componente'] == componente]
            
            if df_filtered.empty:
                return ChartGenerator._create_empty_chart("No hay datos para el componente")
            
            # ✅ APLICAR FILTRO DE FECHA SI SE ESPECIFICA
            if fecha_filtro is not None:
                df_fecha = df_filtered[df_filtered['Fecha'] == fecha_filtro]
                if not df_fecha.empty:
                    df_filtered = df_fecha
                else:
                    # Usar fecha más cercana
                    fechas_disponibles = df_filtered['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= pd.to_datetime(fecha_filtro)]
                    if not fecha_mas_cercana.empty:
                        df_filtered = df_filtered[df_filtered['Fecha'] == fecha_mas_cercana.iloc[-1]]
                    else:
                        df_filtered = df_filtered[df_filtered['Fecha'] == fechas_disponibles.iloc[0]]
            else:
                # Obtener valores más recientes
                df_filtered = ChartGenerator._get_latest_values_by_indicator(df_filtered)
            
            # Agrupar por categoría
            if 'Categoria' not in df_filtered.columns:
                return ChartGenerator._create_empty_chart("No hay información de categorías")
            
            categorias = df_filtered.groupby('Categoria')['Valor_Normalizado'].mean().reset_index()
            
            if len(categorias) < 3:
                return ChartGenerator._create_empty_chart("Se requieren al menos 3 categorías para el radar")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=categorias['Valor_Normalizado'],
                theta=categorias['Categoria'],
                fill='toself',
                name='Puntaje por Categoría',
                line=dict(color='#5B9BD5'),
                fillcolor='rgba(91, 155, 213, 0.3)'
            ))
            
            titulo = f"Radar de Categorías - {componente}" if componente else "Radar de Categorías"
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickformat='.0%'
                    )
                ),
                showlegend=True,
                title=titulo,
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error en radar de categorías: {e}")
            return ChartGenerator._create_error_chart("Error en radar de categorías")
    
    @staticmethod
    def show_category_table_simple(df, componente, fecha_filtro=None):
        """Mostrar tabla simple de categorías - CORREGIDO"""
        try:
            if df.empty:
                st.info("No hay datos disponibles")
                return
            
            # Filtrar por componente
            df_componente = df[df['Componente'] == componente]
            
            if df_componente.empty:
                st.info(f"No hay datos para el componente {componente}")
                return
            
            # ✅ APLICAR FILTRO DE FECHA SI SE ESPECIFICA
            if fecha_filtro is not None:
                df_fecha = df_componente[df_componente['Fecha'] == fecha_filtro]
                if not df_fecha.empty:
                    df_componente = df_fecha
                else:
                    # Usar fecha más cercana
                    fechas_disponibles = df_componente['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= pd.to_datetime(fecha_filtro)]
                    if not fecha_mas_cercana.empty:
                        df_componente = df_componente[df_componente['Fecha'] == fecha_mas_cercana.iloc[-1]]
                    else:
                        df_componente = df_componente[df_componente['Fecha'] == fechas_disponibles.iloc[0]]
            else:
                # Obtener valores más recientes
                df_componente = ChartGenerator._get_latest_values_by_indicator(df_componente)
            
            # Agrupar por categoría
            if 'Categoria' not in df_componente.columns:
                st.info("No hay información de categorías")
                return
            
            categorias_stats = df_componente.groupby('Categoria').agg({
                'Valor_Normalizado': ['mean', 'count'],
                'Indicador': 'count'
            }).round(3)
            
            categorias_stats.columns = ['Puntaje Promedio', 'Registros', 'Indicadores']
            categorias_stats = categorias_stats.sort_values('Puntaje Promedio', ascending=False)
            
            st.subheader(f"Resumen por Categoría - {componente}")
            st.dataframe(categorias_stats, width='stretch')
            
        except Exception as e:
            st.error(f"Error en tabla de categorías: {e}")
    
    @staticmethod
    def _get_latest_values_by_indicator(df):
        """Obtener valores más recientes por indicador"""
        try:
            if df.empty:
                return df
            
            # Verificar columnas esenciales
            required_columns = ['COD', 'Fecha', 'Valor']
            if not all(col in df.columns for col in required_columns):
                st.error(f"Faltan columnas esenciales: {required_columns}")
                return df

            # Limpiar datos
            df_clean = df.dropna(subset=['COD', 'Fecha', 'Valor']).copy()
            
            if df_clean.empty:
                st.warning("No hay datos válidos para procesar")
                return df
            
            # Asegurar que las fechas son datetime
            if not pd.api.types.is_datetime64_any_dtype(df_clean['Fecha']):
                df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'], errors='coerce')
                df_clean = df_clean.dropna(subset=['Fecha'])
            
            if df_clean.empty:
                st.warning("No hay fechas válidas")
                return df
            
            # Obtener valores más recientes de forma segura
            result_rows = []
            
            for codigo in df_clean['COD'].unique():
                if pd.isna(codigo):
                    continue
                    
                # Filtrar datos para este código
                codigo_data = df_clean[df_clean['COD'] == codigo].copy()
                
                if codigo_data.empty:
                    continue
                
                # Ordenar por fecha y tomar el más reciente
                codigo_data_sorted = codigo_data.sort_values('Fecha')
                latest_row = codigo_data_sorted.iloc[-1]
                
                result_rows.append(latest_row)
            
            if not result_rows:
                st.warning("No se pudieron procesar los datos")
                return df
            
            # Crear DataFrame resultado
            result_df = pd.DataFrame(result_rows).reset_index(drop=True)
            
            return result_df
            
        except Exception as e:
            st.error(f"Error al obtener valores más recientes en gráficos: {e}")
            return df
    
    @staticmethod
    def _create_empty_chart(message):
        """Crear gráfico vacío con mensaje"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig
    
    @staticmethod
    def _create_error_chart(error_message):
        """Crear gráfico de error"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"❌ {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig

class MetricsDisplay:
    """Clase para mostrar métricas del dashboard"""
    @staticmethod
    def show_general_metrics(puntaje_general, puntajes_componente, ultima_actualizacion=None):
        """Mostrar métricas generales"""
        try:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "Puntaje General ICE",
                    f"{puntaje_general:.1%}",
                    help="Puntaje promedio ponderado de todos los indicadores"
                )
            
            with col2:
                if not puntajes_componente.empty:
                    mejor_componente = puntajes_componente.loc[puntajes_componente['Puntaje_Ponderado'].idxmax()]
                    st.metric(
                        "Mejor Componente",
                        f"{mejor_componente['Puntaje_Ponderado']:.1%}",
                        delta=mejor_componente['Componente'],
                        help="Componente con mayor puntaje"
                    )
                else:
                    st.metric("Mejor Componente", "N/A")
            
            with col3:
                if not puntajes_componente.empty:
                    total_componentes = len(puntajes_componente)
                    st.metric(
                        "Total Componentes",
                        str(total_componentes),
                        help="Número total de componentes evaluados"
                    )
                else:
                    st.metric("Total Componentes", "0")
            
            with col4:
                if not puntajes_componente.empty:
                    componentes_buenos = len(puntajes_componente[puntajes_componente['Puntaje_Ponderado'] >= 0.7])
                    st.metric(
                        "Componentes ≥70%",
                        str(componentes_buenos),
                        help="Componentes con puntaje igual o superior al 70%"
                    )
                else:
                    st.metric("Componentes ≥70%", "0")
            
            with col5:
                if ultima_actualizacion:
                    fecha_str = ultima_actualizacion['fecha'].strftime('%d/%m/%Y')
                    st.metric(
                        "Última Actualización",
                        fecha_str,
                        help=f"Indicador: {ultima_actualizacion['indicador']}"
                    )
                else:
                    st.metric("Última Actualización", "N/A")
                    
        except Exception as e:
            st.error(f"Error al mostrar métricas: {e}")
    
    
    @staticmethod
    def show_component_metrics(df, componente, fecha_filtro=None):
        """Mostrar métricas específicas de un componente - CORREGIDO"""
        try:
            if df.empty:
                st.info("No hay datos disponibles")
                return
            
            # Filtrar por componente
            df_componente = df[df['Componente'] == componente]
            
            if df_componente.empty:
                st.info(f"No hay datos para el componente {componente}")
                return
            
            # ✅ APLICAR FILTRO DE FECHA SI SE ESPECIFICA
            if fecha_filtro is not None:
                df_fecha = df_componente[df_componente['Fecha'] == fecha_filtro]
                if not df_fecha.empty:
                    df_componente = df_fecha
                else:
                    # Usar fecha más cercana
                    fechas_disponibles = df_componente['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= pd.to_datetime(fecha_filtro)]
                    if not fecha_mas_cercana.empty:
                        df_componente = df_componente[df_componente['Fecha'] == fecha_mas_cercana.iloc[-1]]
                    else:
                        df_componente = df_componente[df_componente['Fecha'] == fechas_disponibles.iloc[0]]
            else:
                # Obtener valores más recientes
                df_componente = ChartGenerator._get_latest_values_by_indicator(df_componente)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Valor_Normalizado' in df_componente.columns:
                    valor_promedio = df_componente['Valor_Normalizado'].mean()
                    st.metric("Valor Promedio", f"{valor_promedio:.1%}")
                else:
                    st.metric("Valor Promedio", "N/A")
            
            with col2:
                total_indicadores = df_componente['Indicador'].nunique()
                st.metric("Total Indicadores", str(total_indicadores))
            
            with col3:
                if 'Fecha' in df_componente.columns:
                    ultima_fecha = df_componente['Fecha'].max()
                    if pd.notna(ultima_fecha):
                        fecha_str = pd.to_datetime(ultima_fecha).strftime('%d/%m/%Y')
                        st.metric("Última Actualización", fecha_str)
                    else:
                        st.metric("Última Actualización", "N/A")
                else:
                    st.metric("Última Actualización", "N/A")
                    
        except Exception as e:
            st.error(f"Error al mostrar métricas del componente: {e}")
