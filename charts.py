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
            fig = px.line(df_evolucion, x='Fecha', y='Valor', title=title)
            fig.update_traces(line_color='#3498DB', line_width=3)
        else:  # Barras
            fig = px.bar(df_evolucion, x='Fecha', y='Valor', title=title)
            fig.update_traces(marker_color='#3498DB')

        # Añadir línea de meta si se seleccionó
        if mostrar_meta:
            fig.add_hline(
                y=1.0,
                line_dash="dash",
                line_color="#E74C3C",
                line_width=2,
                annotation_text="Meta (100%)",
                annotation_font_color="#E74C3C"
            )

        fig.update_layout(
            plot_bgcolor='rgba(248,249,250,0.9)',
            paper_bgcolor='rgba(248,249,250,0.9)',
            font_color='#2C3E50',
            xaxis_title="Fecha",
            yaxis_title="Valor",
            legend_title_text="",
            height=400,
            title_font_size=16,
            title_font_color='#2C3E50',
            xaxis=dict(gridcolor='#BDC3C7'),
            yaxis=dict(gridcolor='#BDC3C7')
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
            line_color='#3498DB',
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='#2C3E50', size=10),
                    gridcolor='#BDC3C7'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#2C3E50', size=11),
                    gridcolor='#BDC3C7'
                ),
                bgcolor='rgba(248,249,250,0.8)'
            ),
            paper_bgcolor='rgba(248,249,250,0.9)',
            font_color='#2C3E50',
            title="Radar: Promedio por Componente",
            title_font_size=16,
            title_font_color='#2C3E50',
            height=350
        )

        return fig

    @staticmethod
    def radar_chart_categories(df, componente, fecha=None):
        """Generar gráfico de radar por categorías de un componente específico"""
        if fecha:
            df_filtrado = df[(df['Fecha'] == fecha) & (df['Componente'] == componente)].copy()
        else:
            ultima_fecha = df['Fecha'].max()
            df_filtrado = df[(df['Fecha'] == ultima_fecha) & (df['Componente'] == componente)].copy()

        if len(df_filtrado) == 0:
            return ChartGenerator._empty_chart(f"No hay datos disponibles para el componente {componente}")

        # Calcular promedio ponderado por categoría dentro del componente
        def weighted_avg_category(group):
            valores = group['Valor'].clip(0, 1)
            pesos = group.get('Peso', pd.Series([1.0] * len(group)))
            peso_total = pesos.sum()
            
            if peso_total > 0:
                return (valores * pesos).sum() / peso_total * 100
            else:
                return valores.mean() * 100

        # Calcular datos para el radar por categoría
        datos_radar = df_filtrado.groupby('Categoria').apply(weighted_avg_category).reset_index()
        datos_radar.columns = ['Categoria', 'Cumplimiento']

        if len(datos_radar) < 3:
            return ChartGenerator._empty_chart(f"Se requieren al menos 3 categorías para el radar de {componente}")

        # Crear gráfico de radar
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=datos_radar['Cumplimiento'],
            theta=datos_radar['Categoria'],
            fill='toself',
            name='Cumplimiento por Categoría',
            line_color='#E67E22',
            fillcolor='rgba(230, 126, 34, 0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='#2C3E50', size=10),
                    gridcolor='#BDC3C7'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#2C3E50', size=11),
                    gridcolor='#BDC3C7'
                ),
                bgcolor='rgba(248,249,250,0.8)'
            ),
            paper_bgcolor='rgba(248,249,250,0.9)',
            font_color='#2C3E50',
            title=f"Radar: Categorías de {componente}",
            title_font_size=16,
            title_font_color='#2C3E50',
            height=350
        )

        return fig

    @staticmethod
    def component_bar_chart(puntajes_componente):
        """Generar gráfico de barras por componente con colores específicos"""
        if puntajes_componente.empty:
            return ChartGenerator._empty_chart("No hay datos de componentes")

        # Ordenar de mayor a menor
        puntajes_componente = puntajes_componente.sort_values('Puntaje_Ponderado', ascending=True)
        
        # Asignar colores: verde al mejor, rojo al peor, amarillo al resto
        colores = []
        for i, valor in enumerate(puntajes_componente['Puntaje_Ponderado']):
            if i == len(puntajes_componente) - 1:  # El último (mayor valor)
                colores.append('#2E8B57')  # Verde corporativo
            elif i == 0:  # El primero (menor valor)
                colores.append('#DC143C')  # Rojo corporativo
            else:
                colores.append('#DAA520')  # Dorado/amarillo corporativo

        fig = go.Figure(go.Bar(
            y=puntajes_componente['Componente'],
            x=puntajes_componente['Puntaje_Ponderado'],
            orientation='h',
            marker=dict(color=colores),
            text=[f'{val:.3f}' for val in puntajes_componente['Puntaje_Ponderado']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Puntaje por Componente",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2C3E50',
            yaxis_title="",
            xaxis_title="Puntaje (0-1)",
            height=400,
            title_font_size=18,
            title_font_color='#2C3E50'
        )
        
        return fig

    @staticmethod
    def gauge_chart(puntaje_general):
        """Generar gráfico de velocímetro para el puntaje general"""
        # Convertir a porcentaje para mejor visualización
        valor_porcentaje = puntaje_general * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor_porcentaje,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Puntaje General ICE", 'font': {'color': '#2C3E50', 'size': 16}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "#34495E", 'tickfont': {'color': '#2C3E50', 'size': 12}},
                'bar': {'color': "#3498DB"},
                'bgcolor': "rgba(248,249,250,0.8)",
                'borderwidth': 2,
                'bordercolor': "#BDC3C7",
                'steps': [
                    {'range': [0, 30], 'color': '#FFE5E5'},
                    {'range': [30, 60], 'color': '#FFF4E5'},
                    {'range': [60, 80], 'color': '#FFFDE5'},
                    {'range': [80, 100], 'color': '#E8F5E8'}
                ],
                'threshold': {
                    'line': {'color': "#E74C3C", 'width': 3},
                    'thickness': 0.75,
                    'value': 85
                }
            },
            number = {'font': {'color': '#2C3E50', 'size': 24}, 'suffix': '%'}
        ))

        fig.update_layout(
            paper_bgcolor='rgba(248,249,250,0.9)',
            plot_bgcolor='rgba(248,249,250,0.9)',
            font_color='#2C3E50',
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig

    @staticmethod
    def _empty_chart(message):
        """Crear gráfico vacío con mensaje"""
        fig = go.Figure()
        fig.update_layout(
            title=message,
            plot_bgcolor='rgba(248,249,250,0.9)',
            paper_bgcolor='rgba(248,249,250,0.9)',
            font_color='#2C3E50',
            title_font_color='#2C3E50'
        )
        return fig

class MetricsDisplay:
    """Clase para mostrar métricas en el dashboard"""
    
    @staticmethod
    def show_general_metrics(puntaje_general, puntajes_componente):
        """Mostrar métricas generales"""
        import streamlit as st
        
        # Crear una tarjeta corporativa para la métrica principal
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; box-shadow: 0 8px 16px rgba(0,0,0,0.15);
                        margin-bottom: 1.5rem;">
                <h3 style="color: white; margin: 0 0 0.5rem 0;">Puntaje General ICE</h3>
                <h1 style="color: white; margin: 0; font-size: 3rem; font-weight: 700;">
                    {puntaje_general:.3f}
                </h1>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                    {(puntaje_general * 100):.1f}% de cumplimiento
                </p>
            </div>
            """, unsafe_allow_html=True)
