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

        # Agrupar por fecha y calcular promedio ponderado
        if componente or not indicador:
            # Para componente o vista general, usar promedio ponderado
            def weighted_avg_by_date(group):
                valores = group['Valor'].clip(0, 1)
                pesos = group.get('Peso', pd.Series([1.0] * len(group)))
                peso_total = pesos.sum()
                
                if peso_total > 0:
                    return (valores * pesos).sum() / peso_total
                else:
                    return valores.mean()
            
            df_evolucion = df_filtrado.groupby('Fecha').apply(weighted_avg_by_date).reset_index()
            df_evolucion.columns = ['Fecha', 'Valor']
        else:
            # Para indicador específico, usar valor directo
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
            df_filtrado = df[df['Fecha'] == fecha].copy()
        else:
            ultima_fecha = df['Fecha'].max()
            df_filtrado = df[df['Fecha'] == ultima_fecha].copy()

        if len(df_filtrado) == 0:
            return ChartGenerator._empty_chart("No hay datos disponibles para la fecha seleccionada")

        # Calcular promedio ponderado por componente (0-100 para visualización)
        def weighted_avg_component(group):
            valores = group['Valor'].clip(0, 1)
            pesos = group.get('Peso', pd.Series([1.0] * len(group)))
            peso_total = pesos.sum()
            
            if peso_total > 0:
                return (valores * pesos).sum() / peso_total * 100
            else:
                return valores.mean() * 100

        # Calcular datos para el radar
        datos_radar = df_filtrado.groupby('Componente').apply(weighted_avg_component).reset_index()
        datos_radar.columns = ['Componente', 'Cumplimiento']

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
            title="Diagrama de Radar: Promedio Ponderado por Componente",
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
            title="Promedio Ponderado por Componente",
            template="plotly_dark",
            orientation='h'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            yaxis_title="",
            xaxis_title="Puntaje (0-1)",
            height=400
        )
        
        return fig

    @staticmethod
    def gauge_chart(puntaje_general):
        """Generar gráfico de velocímetro para el puntaje general"""
        # Convertir a porcentaje para mejor visualización
        valor_porcentaje = puntaje_general * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = valor_porcentaje,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Puntaje General ICE", 'font': {'color': 'white', 'size': 20}},
            delta = {'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
                'bar': {'color': "#4CAF50"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "white",
                'steps': [
                    {'range': [0, 30], 'color': '#FF4444'},
                    {'range': [30, 60], 'color': '#FFAA00'},
                    {'range': [60, 80], 'color': '#FFDD00'},
                    {'range': [80, 100], 'color': '#44FF44'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            },
            number = {'font': {'color': 'white', 'size': 30}}
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            margin=dict(l=20, r=20, t=60, b=20)
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
        
        # Solo mostrar el puntaje general como métrica numérica
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.metric(
                label="Puntaje General ICE", 
                value=f"{puntaje_general:.3f}",
                delta=f"{(puntaje_general * 100):.1f}%"
            )
