"""
Interfaces de usuario para las pestañas del Dashboard ICE
"""

import streamlit as st
import pandas as pd
import time
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor
from filters import EvolutionFilters
from pdf_generator import PDFGenerator

class GeneralSummaryTab:
    """Pestaña de resumen general"""
    
    @staticmethod
    def render(df, fecha_seleccionada):
        """Renderizar la pestaña de resumen general"""
        st.header("Resumen General")
        
        try:
            # Verificación previa de datos
            if df.empty:
                st.error("❌ No hay datos disponibles para el análisis")
                return
                
            required_cols = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"❌ Faltan columnas esenciales: {missing_cols}")
                st.write("**Columnas disponibles:**", list(df.columns))
                return
            
            # Intentar cálculo de puntajes
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(df)
            
            # Mostrar métricas generales
            MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente)
            
            # Crear layout con gráficos
            col1, col2 = st.columns([1, 2])
            
            with col1:
                try:
                    st.plotly_chart(
                        ChartGenerator.gauge_chart(puntaje_general), 
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error en velocímetro: {e}")
            
            with col2:
                try:
                    st.plotly_chart(
                        ChartGenerator.radar_chart(df, None),
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error en gráfico radar: {e}")
            
            # Puntajes por componente
            st.subheader("Puntajes por Componente")
            if not puntajes_componente.empty:
                try:
                    fig_comp = ChartGenerator.component_bar_chart(puntajes_componente)
                    st.plotly_chart(fig_comp, use_container_width=True)
                except Exception as e:
                    st.error(f"Error en gráfico de componentes: {e}")
                    st.dataframe(puntajes_componente, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar puntajes por componente")
            
        except Exception as e:
            st.error(f"❌ Error crítico al calcular puntajes: {e}")

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de resumen por componente"""
        st.header("Resumen por Componente")
        
        # Selector de componente
        componentes = sorted(df['Componente'].unique())
        componente_analisis = st.selectbox(
            "Seleccionar componente para análisis detallado", 
            componentes,
            key="comp_analysis"
        )
        
        # Análisis del componente seleccionado
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        df_componente = df_latest[df_latest['Componente'] == componente_analisis]
        
        if not df_componente.empty:
            st.dataframe(
                df_componente[['Indicador', 'Categoria', 'Valor', 'Fecha']].sort_values('Valor', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("No hay datos para el componente seleccionado")

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de evolución"""
        st.subheader("📈 Evolución Temporal de Indicadores")
        
        try:
            if df.empty:
                st.warning("No hay datos disponibles para mostrar evolución")
                return
            
            # Crear filtros específicos de evolución
            evolution_filters = EvolutionFilters.create_evolution_filters(df)
            
            # Generar gráfico de evolución
            try:
                fig = ChartGenerator.evolution_chart(
                    df,
                    indicador=evolution_filters['indicador'],
                    componente=None,
                    tipo_grafico=evolution_filters['tipo_grafico'],
                    mostrar_meta=evolution_filters['mostrar_meta']
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error al generar gráfico: {e}")
            
        except Exception as e:
            st.error(f"Error crítico en pestaña de evolución: {e}")

class EditTab:
    """Pestaña de edición"""
    
    @staticmethod
    def render(df, csv_path, excel_data=None):
        """Renderizar la pestaña de edición"""
        st.subheader("Gestión de Indicadores")
        
        try:
            if df.empty:
                st.error("No hay datos disponibles")
                return
            
            # Seleccionar indicador
            codigos_disponibles = sorted(df['Codigo'].dropna().unique())
            if not codigos_disponibles:
                st.error("No hay códigos de indicadores disponibles")
                return
                
            codigo_editar = st.selectbox("Seleccionar Código de Indicador", codigos_disponibles, key="codigo_editar")
            
            # Mostrar información del indicador
            datos_indicador = df[df['Codigo'] == codigo_editar]
            if not datos_indicador.empty:
                nombre_indicador = datos_indicador['Indicador'].iloc[0]
                st.write(f"**Indicador seleccionado:** {nombre_indicador}")
                
                # Botón para descargar hoja metodológica (solo si hay datos del Excel)
                if excel_data is not None and not excel_data.empty:
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("📄 Descargar Hoja Metodológica", key="download_pdf"):
                            try:
                                pdf_generator = PDFGenerator()
                                file_bytes = pdf_generator.generate_metodological_sheet(codigo_editar, excel_data)
                                
                                if file_bytes:
                                    st.download_button(
                                        label="📊 Descargar CSV",
                                        data=file_bytes,
                                        file_name=f"Hoja_Metodologica_{codigo_editar}.csv",
                                        mime="text/csv",
                                        key="download_file_button"
                                    )
                                else:
                                    st.error("No se pudo generar el archivo metodológico")
                            except Exception as e:
                                st.error(f"Error al generar archivo: {e}")
                else:
                    st.info("💡 Para habilitar la descarga de hojas metodológicas, coloca el archivo Excel en el directorio.")
                
                # Mostrar datos del indicador
                st.dataframe(
                    datos_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"Error en la gestión de indicadores: {e}")

class TabManager:
    """Gestor de pestañas del dashboard"""
    
    def __init__(self, df, csv_path, excel_data=None):
        self.df = df
        self.csv_path = csv_path
        self.excel_data = excel_data
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resumen General", 
            "Resumen por Componente", 
            "Evolución", 
            "Gestión de Datos"
        ])
        
        with tab1:
            GeneralSummaryTab.render(df_filtrado, filters.get('fecha'))
        
        with tab2:
            ComponentSummaryTab.render(df_filtrado, filters)
        
        with tab3:
            EvolutionTab.render(self.df, filters)
        
        with tab4:
            EditTab.render(self.df, self.csv_path, self.excel_data)
