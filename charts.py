"""
Funciones de visualización para el Dashboard ICE
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class ChartGenerator:
    """Clase para generar diferentes tipos de gráficos"""
    
    @staticmethod
    def show_category_table_simple(df, componente):
        """Mostrar tabla de categorías usando componentes nativos de Streamlit"""
        import streamlit as st
        
        try:
            # Obtener valores más recientes del componente
            df_latest = ChartGenerator._get_latest_values_by_indicator(df)
            df_filtrado = df_latest[df_latest['Componente'] == componente].copy()

            if len(df_filtrado) == 0:
                st.warning(f"No hay datos disponibles para el componente {componente}")
                return

            # Calcular promedio ponderado por categoría
            def weighted_avg_category(group):
                valores = group['Valor'].clip(0, 1)
                pesos = group.get('Peso', pd.Series([1.0] * len(group)))
                peso_total = pesos.sum()
                
                if peso_total > 0:
                    return (valores * pesos).sum() / peso_total
                else:
                    return valores.mean()

            # Calcular datos por categoría
            datos_categorias = df_filtrado.groupby('Categoria').apply(weighted_avg_category).reset_index()
            datos_categorias.columns = ['Categoria', 'Puntaje']
            
            # Ordenar por puntaje descendente
            datos_categorias = datos_categorias.sort_values('Puntaje', ascending=False)
            
            st.subheader("📊 Puntajes por Categoría")
            
            # Mostrar cada categoría con métricas coloridas
            for _, row in datos_categorias.iterrows():
                porcentaje = row['Puntaje'] * 100
                
                # Determinar color y emoji según puntaje
                if row['Puntaje'] >= 0.8:
                    emoji = "🟢"
                    estado = "Excelente"
                elif row['Puntaje'] >= 0.6:
                    emoji = "🟡"
                    estado = "Bueno"
                elif row['Puntaje'] >= 0.4:
                    emoji = "🟠"
                    estado = "Regular"
                else:
                    emoji = "🔴"
                    estado = "Crítico"
                
                # Crear columnas para cada categoría
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['Categoria']}**")
                
                with col2:
                    st.metric("Puntaje", f"{row['Puntaje']:.3f}")
                
                with col3:
                    st.metric("Porcentaje", f"{porcentaje:.1f}%")
                
                with col4:
                    st.write(f"{emoji} **{estado}**")
                
                # Agregar una barra de progreso visual
                st.progress(row['Puntaje'])
                st.write("---")  # Separador
                
        except Exception as e:
            st.error(f"Error al mostrar tabla de categorías: {e}")
            import traceback
            st.code(traceback.format_exc())

    @staticmethod
    def _get_latest_values_by_indicator(df):
        """Obtener el valor más reciente de cada indicador"""
        try:
            # Agrupar por código de indicador y tomar el registro con fecha más reciente
            def get_latest_record(group):
                return group.loc[group['Fecha'].idxmax()]
            
            df_latest = df.groupby('Codigo').apply(get_latest_record).reset_index(drop=True)
            return df_latest
            
        except Exception as e:
            import streamlit as st
            st.warning(f"Error al obtener valores más recientes en gráficos: {e}")
            # Fallback: retornar el DataFrame original
            return df
    
    @staticmethod
    def category_summary_table(df, componente, fecha=None):
        """Generar tabla de resumen de categorías con colores por puntaje usando valores más recientes"""
        try:
            if fecha:
                df_filtrado = df[(df['Fecha'] == fecha) & (df['Componente'] == componente)].copy()
                # Si no hay datos para esa fecha, usar valores más recientes del componente
                if df_filtrado.empty:
                    df_latest = ChartGenerator._get_latest_values_by_indicator(df)
                    df_filtrado = df_latest[df_latest['Componente'] == componente].copy()
            else:
                # Usar valores más recientes de cada indicador del componente
                df_latest = ChartGenerator._get_latest_values_by_indicator(df)
                df_filtrado = df_latest[df_latest['Componente'] == componente].copy()

            if len(df_filtrado) == 0:
                return None, f"No hay datos disponibles para el componente {componente}"

            # Calcular promedio ponderado por categoría dentro del componente
            def weighted_avg_category(group):
                valores = group['Valor'].clip(0, 1)
                pesos = group.get('Peso', pd.Series([1.0] * len(group)))
                peso_total = pesos.sum()
                
                if peso_total > 0:
                    return (valores * pesos).sum() / peso_total
                else:
                    return valores.mean()

            # Calcular datos por categoría
            datos_categorias = df_filtrado.groupby('Categoria').apply(weighted_avg_category).reset_index()
            datos_categorias.columns = ['Categoria', 'Puntaje']
            
            # Función para asignar colores según el puntaje
            def get_color_by_score(score):
                if score >= 0.8:
                    return '#2E8B57'  # Verde - Excelente
                elif score >= 0.6:
                    return '#DAA520'  # Dorado - Bueno
                elif score >= 0.4:
                    return '#FF8C00'  # Naranja - Regular
                else:
                    return '#DC143C'  # Rojo - Crítico

            # Crear DataFrame para mostrar con Streamlit (más confiable que HTML)
            tabla_data = []
            for _, row in datos_categorias.iterrows():
                porcentaje = row['Puntaje'] * 100
                
                if row['Puntaje'] >= 0.8:
                    estado = "🟢 Excelente"
                elif row['Puntaje'] >= 0.6:
                    estado = "🟡 Bueno"
                elif row['Puntaje'] >= 0.4:
                    estado = "🟠 Regular"
                else:
                    estado = "🔴 Crítico"
                
                tabla_data.append({
                    'Categoría': row['Categoria'],
                    'Puntaje': f"{row['Puntaje']:.3f}",
                    'Porcentaje': f"{porcentaje:.1f}%",
                    'Estado': estado
                })
            
            tabla_df = pd.DataFrame(tabla_data)
            
            return tabla_df, None
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error en tabla de categorías: {e}")
            return None, f"Error al generar tabla para {componente}"

    @staticmethod
    def evolution_chart(df, indicador=None, componente=None, tipo_grafico="Línea", mostrar_meta=True):
        """Generar gráfico de evolución temporal - CORREGIDO para mostrar datos históricos"""
        try:
            # Debug: Mostrar información de entrada
            import streamlit as st
            
            # Filtrar datos según los parámetros
            if indicador:
                df_filtrado = df[df['Indicador'] == indicador].copy()
                titulo = f"Evolución de {indicador}"
            elif componente:
                df_filtrado = df[df['Componente'] == componente].copy()
                titulo = f"Evolución del componente {componente}"
            else:
                df_filtrado = df.copy()
                titulo = "Evolución General"

            if len(df_filtrado) == 0:
                return ChartGenerator._empty_chart("No hay datos disponibles para el filtro seleccionado")

            # Debug: Mostrar datos filtrados
            with st.expander("🔍 Debug: Datos para evolución", expanded=False):
                st.write(f"**Filtro aplicado:** {indicador or componente or 'General'}")
                st.write(f"**Registros encontrados:** {len(df_filtrado)}")
                st.dataframe(df_filtrado[['Fecha', 'Valor', 'Indicador', 'Componente']].sort_values('Fecha'))

            # Preparar datos para gráfico
            if indicador:
                # Para indicador específico: mostrar todos sus valores históricos
                df_evolucion = df_filtrado[['Fecha', 'Valor']].sort_values('Fecha')
                df_evolucion = df_evolucion.dropna(subset=['Fecha', 'Valor'])
            elif componente:
                # Para componente: promedio ponderado por fecha
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
                # Para vista general: promedio simple por fecha
                df_evolucion = df_filtrado.groupby('Fecha')['Valor'].mean().reset_index()

            # Verificar que tenemos datos para graficar
            if len(df_evolucion) == 0:
                return ChartGenerator._empty_chart("No hay datos válidos para graficar")

            # Crear gráfico según tipo
            if tipo_grafico == "Línea":
                fig = px.line(
                    df_evolucion, 
                    x='Fecha', 
                    y='Valor', 
                    title=titulo,
                    markers=True  # Agregar marcadores para ver puntos individuales
                )
                fig.update_traces(line_color='#3498DB', line_width=3, marker_size=8)
            else:  # Barras
                fig = px.bar(df_evolucion, x='Fecha', y='Valor', title=titulo)
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

            # Configurar layout
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
                yaxis=dict(gridcolor='#BDC3C7', range=[0, 1.1])  # Fijar rango Y
            )

            # Mejorar formato de fechas en eje X
            fig.update_xaxes(
                tickformat="%d/%m/%Y",
                tickangle=45
            )

            return fig
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error crítico en evolution_chart: {e}")
            import traceback
            st.code(traceback.format_exc())
            return ChartGenerator._empty_chart("Error al generar gráfico de evolución")

    @staticmethod
    def radar_chart(df, fecha=None):
        """Generar gráfico de radar por componente usando valores más recientes"""
        try:
            if fecha:
                df_filtrado = df[df['Fecha'] == fecha].copy()
                # Si no hay datos para esa fecha, usar valores más recientes
                if df_filtrado.empty:
                    df_filtrado = ChartGenerator._get_latest_values_by_indicator(df)
            else:
                # Usar valores más recientes de cada indicador
                df_filtrado = ChartGenerator._get_latest_values_by_indicator(df)

            if len(df_filtrado) == 0:
                return ChartGenerator._empty_chart("No hay datos disponibles")

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
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error en radar chart: {e}")
            return ChartGenerator._empty_chart("Error al generar gráfico de radar")

    @staticmethod
    def radar_chart_categories(df, componente, fecha=None):
        """Generar gráfico de radar por categorías de un componente específico usando valores más recientes"""
        try:
            if fecha:
                df_filtrado = df[(df['Fecha'] == fecha) & (df['Componente'] == componente)].copy()
                # Si no hay datos para esa fecha, usar valores más recientes del componente
                if df_filtrado.empty:
                    df_latest = ChartGenerator._get_latest_values_by_indicator(df)
                    df_filtrado = df_latest[df_latest['Componente'] == componente].copy()
            else:
                # Usar valores más recientes de cada indicador del componente
                df_latest = ChartGenerator._get_latest_values_by_indicator(df)
                df_filtrado = df_latest[df_latest['Componente'] == componente].copy()

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
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error en radar de categorías: {e}")
            return ChartGenerator._empty_chart("Error al generar gráfico de radar por categorías")

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
