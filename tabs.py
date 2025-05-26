"""
Interfaces de usuario para las pestañas del Dashboard ICE
"""

import streamlit as st
import pandas as pd
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor
from filters import EvolutionFilters, PivotTableFilters

class GeneralSummaryTab:
    """Pestaña de resumen general"""
    
    @staticmethod
    def render(df, fecha_seleccionada):
        """Renderizar la pestaña de resumen general"""
        st.header("Resumen General")
        
        try:
            # Calcular puntajes
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(
                df, fecha_seleccionada
            )
            
            # Mostrar métricas generales
            MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente)
            
            # Crear layout con velocímetro más pequeño
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Gráfico de velocímetro (más pequeño)
                st.plotly_chart(
                    ChartGenerator.gauge_chart(puntaje_general), 
                    use_container_width=True
                )
            
            with col2:
                # Gráfico de radar (más grande)
                st.plotly_chart(
                    ChartGenerator.radar_chart(df, fecha_seleccionada), 
                    use_container_width=True
                )
            
            # Puntajes por componente
            st.subheader("Puntajes por Componente")
            if not puntajes_componente.empty:
                fig_comp = ChartGenerator.component_bar_chart(puntajes_componente)
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar puntajes por componente")
            
        except Exception as e:
            st.error(f"Error al calcular puntajes: {e}")
            st.info("Comprueba que los datos contengan las columnas requeridas")
        
        # Mostrar tabla de datos filtrados
        with st.expander("Ver datos generales"):
            st.dataframe(df, use_container_width=True)

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de resumen por componente"""
        st.header("Resumen por Componente")
        
        # Selector de componente específico para esta vista
        componentes = sorted(df['Componente'].unique())
        componente_analisis = st.selectbox(
            "Seleccionar componente para análisis detallado", 
            componentes,
            key="comp_analysis"
        )
        
        # Filtrar datos por componente
        df_componente = df[df['Componente'] == componente_analisis]
        
        if not df_componente.empty:
            # Métricas del componente con estilo personalizado (gris más claro)
            st.markdown("""
            <style>
            .metric-gray {
                background-color: rgba(248, 249, 250, 0.9);
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #95A5A6;
                margin-bottom: 1rem;
            }
            .metric-gray .metric-label {
                color: #7F8C8D !important;
                font-size: 0.875rem;
                font-weight: 500;
                margin-bottom: 0.25rem;
            }
            .metric-gray .metric-value {
                color: #5D6D7E !important;
                font-size: 1.5rem;
                font-weight: 600;
                margin: 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                valor_promedio = df_componente['Valor'].mean()
                st.markdown(f"""
                <div class="metric-gray">
                    <div class="metric-label">Valor Promedio</div>
                    <div class="metric-value">{valor_promedio:.3f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_indicadores = df_componente['Indicador'].nunique()
                st.markdown(f"""
                <div class="metric-gray">
                    <div class="metric-label">Total Indicadores</div>
                    <div class="metric-value">{total_indicadores}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                ultima_medicion = df_componente['Fecha'].max()
                # Manejar fechas NaT de forma segura
                if pd.notna(ultima_medicion):
                    try:
                        fecha_str = pd.to_datetime(ultima_medicion).strftime('%d/%m/%Y')
                        fecha_display = fecha_str
                    except:
                        fecha_display = "No disponible"
                else:
                    fecha_display = "No disponible"
                
                st.markdown(f"""
                <div class="metric-gray">
                    <div class="metric-label">Última Medición</div>
                    <div class="metric-value">{fecha_display}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Layout con gráficos lado a lado
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                # Gráfico de evolución del componente
                fig_evol = ChartGenerator.evolution_chart(df_componente, componente=componente_analisis)
                st.plotly_chart(fig_evol, use_container_width=True)
            
            with col_der:
                # Gráfico de radar por categorías del componente
                fig_radar_cat = ChartGenerator.radar_chart_categories(
                    df, componente_analisis, filters.get('fecha')
                )
                st.plotly_chart(fig_radar_cat, use_container_width=True)
            
            # Tabla de indicadores del componente
            st.subheader(f"Indicadores de {componente_analisis}")
            st.dataframe(
                df_componente[['Indicador', 'Categoria', 'Valor', 'Fecha']].sort_values('Fecha', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("No hay datos para el componente seleccionado")

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de evolución"""
        st.subheader("Evolución de Indicadores")
        
        try:
            # Crear filtros específicos de evolución
            evolution_filters = EvolutionFilters.create_evolution_filters(df)
            
            # Mostrar nombre del indicador seleccionado
            if evolution_filters['indicador']:
                st.write(f"**Indicador seleccionado:** {evolution_filters['indicador']}")
            
            # Generar gráfico de evolución
            fig = ChartGenerator.evolution_chart(
                df,
                indicador=evolution_filters['indicador'],
                componente=filters.get('componente'),
                tipo_grafico=evolution_filters['tipo_grafico'],
                mostrar_meta=evolution_filters['mostrar_meta']
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabla de datos del indicador seleccionado
            if evolution_filters['codigo']:
                st.subheader(f"Datos del indicador: {evolution_filters['indicador']}")
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                st.dataframe(
                    datos_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"Error al generar gráfico de evolución: {e}")

class PivotTableTab:
    """Pestaña de tabla dinámica"""
    
    @staticmethod
    def render(df, fecha_seleccionada):
        """Renderizar la pestaña de tabla dinámica"""
        st.subheader("Tabla Dinámica de Indicadores")
        
        try:
            # Crear filtros para tabla dinámica
            pivot_filters = PivotTableFilters.create_pivot_filters()
            
            # Validar que filas y columnas sean diferentes
            if pivot_filters['filas'] == pivot_filters['columnas']:
                st.warning("Las filas y columnas deben ser diferentes.")
            else:
                # Crear tabla dinámica
                tabla = DataProcessor.create_pivot_table(
                    df,
                    fecha=fecha_seleccionada,
                    filas=pivot_filters['filas'],
                    columnas=pivot_filters['columnas'],
                    valores=pivot_filters['valores']
                )
                
                # Mostrar tabla con formato condicional
                st.dataframe(
                    tabla.style.background_gradient(cmap='YlGn'), 
                    use_container_width=True
                )
                
                # Opción para descargar - manejar fechas NaT
                csv = tabla.to_csv(index=True)
                
                # Crear nombre de archivo seguro
                if fecha_seleccionada is not None and pd.notna(fecha_seleccionada):
                    try:
                        fecha_str = pd.to_datetime(fecha_seleccionada).strftime('%Y%m%d')
                        filename = f"tabla_dinamica_{fecha_str}.csv"
                    except:
                        filename = "tabla_dinamica.csv"
                else:
                    filename = "tabla_dinamica.csv"
                
                st.download_button(
                    label="Descargar tabla como CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
        
        except Exception as e:
            st.error(f"Error al generar tabla dinámica: {e}")
            st.info("Comprueba que los datos contengan las columnas seleccionadas")

class EditTab:
    """Pestaña de edición"""
    
    @staticmethod
    def render(df, csv_path):
        """Renderizar la pestaña de edición"""
        st.subheader("Edición de Indicadores")
        
        try:
            # Seleccionar indicador por código
            codigos = sorted(df['Codigo'].unique())
            codigo_editar = st.selectbox("Seleccionar Código de Indicador", codigos, key="codigo_editar")
            
            # Mostrar información del indicador
            nombre_indicador = df[df['Codigo'] == codigo_editar]['Indicador'].iloc[0]
            st.write(f"**Indicador seleccionado:** {nombre_indicador}")
            
            # Mostrar información actual
            info_indicador = df[df['Codigo'] == codigo_editar]
            st.dataframe(
                info_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                use_container_width=True
            )
            
            # Formulario de edición
            with st.form("form_edicion"):
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        # Filtrar fechas válidas (no NaT)
                        fechas_validas = df['Fecha'].dropna().unique()
                        if len(fechas_validas) > 0:
                            fechas_options = sorted(fechas_validas)
                            ultima_fecha_valida = pd.to_datetime(fechas_options[-1])
                            fecha_editar = st.date_input(
                                "Fecha",
                                value=ultima_fecha_valida.date() if pd.notna(ultima_fecha_valida) else None
                            )
                        else:
                            fecha_editar = st.date_input("Fecha")
                    except Exception as e:
                        st.warning(f"Error al cargar fechas: {e}")
                        fecha_editar = st.date_input("Fecha")
                
                with col2:
                    valor_actual = info_indicador[
                        info_indicador['Fecha'] == pd.to_datetime(fecha_editar)
                    ]['Valor'].values
                    
                    valor_editar = st.number_input(
                        "Nuevo valor",
                        value=float(valor_actual[0]) if len(valor_actual) > 0 else 0.5,
                        min_value=0.0,
                        max_value=1.0,
                        step=0.1
                    )
                    st.caption("Los valores deben estar entre 0 y 1, donde 1 representa el 100%")
                
                # Botón para guardar
                submitted = st.form_submit_button("Guardar cambios")
                
                if submitted:
                    fecha_dt = pd.to_datetime(fecha_editar)
                    if DataEditor.save_edit(df, codigo_editar, fecha_dt, valor_editar, csv_path):
                        st.success("Datos actualizados correctamente")
                        st.rerun()
                    else:
                        st.error("Error al actualizar datos")
        
        except Exception as e:
            st.error(f"Error en la edición de indicadores: {e}")
            st.info("Asegúrate de que los datos contengan las columnas necesarias")

class TabManager:
    """Gestor de pestañas del dashboard"""
    
    def __init__(self, df, csv_path):
        self.df = df
        self.csv_path = csv_path
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Resumen General", 
            "Resumen por Componente", 
            "Evolución", 
            "Tabla Dinámica", 
            "Edición"
        ])
        
        with tab1:
            GeneralSummaryTab.render(df_filtrado, filters.get('fecha'))
        
        with tab2:
            ComponentSummaryTab.render(df_filtrado, filters)
        
        with tab3:
            EvolutionTab.render(self.df, filters)
        
        with tab4:
            PivotTableTab.render(self.df, filters.get('fecha'))
        
        with tab5:
            EditTab.render(self.df, self.csv_path)
