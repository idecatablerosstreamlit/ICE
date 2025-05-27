"""
Funciones de visualización para el Dashboard ICE
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class ChartGenerator:
    """Clase para generar diferentes tipos de gráficos"""
    
    @staticmethod
    def evolution_chart(df, indicador=None, componente=None, tipo_grafico="Línea", mostrar_meta=True):
        """Generar gráfico de evolución temporal"""
        # Filtrar datos
        if indicador:
            df_filtrado = df[df['Indicador'] == indicador]
        elif componente:
            df_filtrado = df[df['Componente'] == componente]
        else:
            df_filtrado = df

        if len(df_filtrado) == 0:
            return ChartGenerator._empty_chart("No hay datos disponibles para el filtro seleccionado")

        # Agrupar por fecha
        df_evolucion = df_filtrado.groupby('Fecha')['Valor'].mean().reset_index()

        # Crear gráfico según tipo
        title = f"Evolución de {indicador if indicador else componente if componente else 'Indicadores'}"
        
        if tipo_grafico == "Línea":
            fig = px.line(df_evolucion, x='Fecha', y='Valor', title=title, template="plotly_dark")
        else:  # Barras
            fig = px.bar(df_evolucion, x='Fecha', y='Valor', title=title, template="plotly_dark")

        # Añadir línea de meta si se seleccionó
        if mostrar_meta:
            fig.add_hline(
                y=1.0,
                line_dash="dash",
                line_color="green",
                annotation_text="Meta",
                annotation_font_color="green"
            )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Fecha",
            yaxis_title="Valor",
            legend_title_text="",
            height=400
        )

        return fig

    @staticmethod
    def radar_chart(df, fecha=None):
        """Generar gráfico de radar por componente"""
        if fecha:
            df_filtrado = df[df['Fecha'] == fecha]
        else:
            ultima_fecha = df['Fecha'].max()
            df_filtrado = df[df['Fecha'] == ultima_fecha]

        if len(df_filtrado) == 0:
            return ChartGenerator._empty_chart("No hay datos disponibles para la fecha seleccionada")

        # Calcular cumplimiento
        if 'Cumplimiento' not in df_filtrado.columns:
            if df_filtrado['Valor'].max() <= 1:
                df_filtrado['Cumplimiento'] = df_filtrado['Valor'] * 100
            else:
                df_filtrado['Cumplimiento'] = df_filtrado['Valor']

        # Agrupar por componente
        datos_radar = df_filtrado.groupby('Componente')['Cumplimiento'].mean().reset_index()

        if len(datos_radar) < 3:
            return ChartGenerator._empty_chart("Se requieren al menos 3 componentes para el gráfico de radar")

        # Crear gráfico de radar
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=datos_radar['Cumplimiento'],
            theta=datos_radar['Componente'],
            fill='toself',
            name='Cumplimiento',
            line_color='#4CAF50'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='white')
                ),
                angularaxis=dict(
                    tickfont=dict(color='white')
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title="Diagrama de Radar: Cumplimiento por Componente",
            height=450
        )

        return fig

    @staticmethod
    def component_bar_chart(puntajes_componente):
        """Generar gráfico de barras por componente"""
        if puntajes_componente.empty:
            return ChartGenerator._empty_chart("No hay datos de componentes")

        # Ordenar de mayor a menor
        puntajes_componente = puntajes_componente.sort_values('Puntaje_Ponderado', ascending=True)

        fig = px.bar(
            puntajes_componente,
            y='Componente',
            x='Puntaje_Ponderado',
            title="Puntaje por Componente",
            template="plotly_dark",
            orientation='h'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            yaxis_title="",
            xaxis_title="Puntaje",
            height=400
        )
        
        return fig

    @staticmethod
    def _empty_chart(message):
        """Crear gráfico vacío con mensaje"""
        fig = go.Figure()
        fig.update_layout(
            title=message,
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        return fig

class MetricsDisplay:
    """Clase para mostrar métricas en el dashboard"""
    
    @staticmethod
    def show_general_metrics(puntaje_general, puntajes_componente):
        """Mostrar métricas generales"""
        import streamlit as st
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Puntaje General", value=f"{puntaje_general:.1f}")

        if not puntajes_componente.empty:
            with col2:
                mejor_componente = puntajes_componente.sort_values('Puntaje_Ponderado', ascending=False).iloc[0]
                st.metric(
                    label="Mejor Componente",
                    value=mejor_componente['Componente'],
                    delta=f"{mejor_componente['Puntaje_Ponderado']:.1f}"
                )

            with col3:
                peor_componente = puntajes_componente.sort_values('Puntaje_Ponderado').iloc[0]
                st.metric(
                    label="Componente a Mejorar",
                    value=peor_componente['Componente'],
                    delta=f"{peor_componente['Puntaje_Ponderado']:.1f}"
                )
