"""
Interfaces de usuario para las pestañas del Dashboard ICE - Versión corregida
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
        st.header("📈 Resumen General")
        
        if len(df) == 0:
            st.warning("⚠️ No hay datos disponibles para mostrar")
            return
        
        try:
            # Calcular puntajes
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(
                df, fecha_seleccionada
            )
            
            # Mostrar métricas generales
            if puntaje_general > 0:
                MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente)
                
                # Gráfico de radar
                st.subheader("🎯 Diagrama de Radar por Componente")
                radar_fig = ChartGenerator.radar_chart(df, fecha_seleccionada)
                st.plotly_chart(radar_fig, use_container_width=True)
                
                # Puntajes por componente
                st.subheader("🏗️ Puntajes por Componente")
                if not puntajes_componente.empty:
                    fig_comp = ChartGenerator.component_bar_chart(puntajes_componente)
                    st.plotly_chart(fig_comp, use_container_width=True)
                    
                    # Mostrar tabla de puntajes
                    st.dataframe(
                        puntajes_componente.sort_values('Puntaje_Ponderado', ascending=False),
                        use_container_width=True
                    )
                else:
                    st.info("📊 No hay datos suficientes para mostrar puntajes por componente")
            else:
                st.warning("⚠️ No se pudieron calcular los puntajes")
            
        except Exception as e:
            st.error(f"❌ Error al calcular puntajes: {e}")
            st.info("🔧 Comprueba que los datos contengan las columnas requeridas")
        
        # Mostrar tabla de datos filtrados
        st.subheader("📋 Datos Generales")
        try:
            if len(df) > 0:
                # Mostrar información básica
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total registros", len(df))
                with col2:
                    st.metric("🎯 Indicadores únicos", df['Indicador'].nunique())
                with col3:
                    st.metric("📅 Fechas disponibles", df['Fecha'].nunique())
                
                # Tabla con datos
                df_display = df[['Indicador', 'Componente', 'Categoria', 'Valor', 'Fecha']].copy()
                df_display['Fecha'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("📭 No hay datos para mostrar")
        except Exception as e:
            st.error(f"Error al mostrar tabla: {e}")

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de resumen por componente"""
        st.header("🏗️ Resumen por Componente")
        
        if len(df) == 0:
            st.warning("⚠️ No hay datos disponibles")
            return
        
        try:
            # Selector de componente específico para esta vista
            componentes = sorted(df['Componente'].unique())
            componente_analisis = st.selectbox(
                "🔍 Seleccionar componente para análisis detallado", 
                componentes,
                key="comp_analysis"
            )
            
            # Filtrar datos por componente
            df_componente = df[df['Componente'] == componente_analisis]
            
            if not df_componente.empty:
                # Métricas del componente
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    valor_promedio = df_componente['Valor'].mean()
                    st.metric("📊 Valor Promedio", f"{valor_promedio:.2f}")
                
                with col2:
                    total_indicadores = df_componente['Indicador'].nunique()
                    st.metric("🎯 Total Indicadores", total_indicadores)
                
                with col3:
                    if len(df_componente) > 0:
                        ultima_medicion = df_componente['Fecha'].max()
                        st.metric("📅 Última Medición", ultima_medicion.strftime('%d/%m/%Y'))
                
                # Gráfico de evolución del componente
                st.subheader(f"📈 Evolución de {componente_analisis}")
                fig_evol = ChartGenerator.evolution_chart(df_componente, componente=componente_analisis)
                st.plotly_chart(fig_evol, use_container_width=True)
                
                # Tabla de indicadores del componente
                st.subheader(f"📋 Indicadores de {componente_analisis}")
                df_display = df_componente[['Indicador', 'Categoria', 'Valor', 'Fecha']].copy()
                df_display['Fecha'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
                df_display = df_display.sort_values('Fecha', ascending=False)
                st.dataframe(df_display, use_container_width=True)
                
            else:
                st.warning("⚠️ No hay datos para el componente seleccionado")
                
        except Exception as e:
            st.error(f"❌ Error en resumen por componente: {e}")

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de evolución"""
        st.header("📊 Evolución de Indicadores")
        
        if len(df) == 0:
            st.warning("⚠️ No hay datos disponibles")
            return
        
        try:
            # Crear filtros específicos de evolución
            evolution_filters = EvolutionFilters.create_evolution_filters(df)
            
            # Mostrar nombre del indicador seleccionado
            if evolution_filters['indicador']:
                st.info(f"**🎯 Indicador seleccionado:** {evolution_filters['indicador']}")
            
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
                st.subheader(f"📋 Datos del indicador: {evolution_filters['indicador']}")
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if not datos_indicador.empty:
                    df_display = datos_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']].copy()
                    df_display['Fecha'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
                    st.dataframe(df_display, use_container_width=True)
                else:
                    st.info("📭 No hay datos históricos para este indicador")
            
        except Exception as e:
            st.error(f"❌ Error al generar gráfico de evolución: {e}")
            if st.checkbox("🔧 Mostrar detalles del error"):
                st.exception(e)

class PivotTableTab:
    """Pestaña de tabla dinámica"""
    
    @staticmethod
    def render(df, fecha_seleccionada):
        """Renderizar la pestaña de tabla dinámica"""
        st.header("📋 Tabla Dinámica de Indicadores")
        
        if len(df) == 0:
            st.warning("⚠️ No hay datos disponibles")
            return
        
        try:
            # Crear filtros para tabla dinámica
            pivot_filters = PivotTableFilters.create_pivot_filters()
            
            # Validar que filas y columnas sean diferentes
            if pivot_filters['filas'] == pivot_filters['columnas']:
                st.warning("⚠️ Las filas y columnas deben ser diferentes.")
                return
            
            # Crear tabla dinámica
            tabla = DataProcessor.create_pivot_table(
                df,
                fecha=fecha_seleccionada,
                filas=pivot_filters['filas'],
                columnas=pivot_filters['columnas'],
                valores=pivot_filters['valores']
            )
            
            if not tabla.empty:
                # Mostrar información de la tabla
                st.info(f"📊 Tabla dinámica: {tabla.shape[0]} filas × {tabla.shape[1]} columnas")
                
                # Mostrar tabla con formato condicional
                st.dataframe(
                    tabla.style.background_gradient(cmap='YlGn').format("{:.2f}"), 
                    use_container_width=True
                )
                
                # Opción para descargar
                csv = tabla.to_csv(index=True)
                st.download_button(
                    label="📥 Descargar tabla como CSV",
                    data=csv,
                    file_name=f"tabla_dinamica_{fecha_seleccionada.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No se pudo generar la tabla dinámica con los filtros seleccionados")
            
        except Exception as e:
            st.error(f"❌ Error al generar tabla dinámica: {e}")
            st.info("🔧 Comprueba que los datos contengan las columnas seleccionadas")

class EditTab:
    """Pestaña de edición"""
    
    @staticmethod
    def render(df, csv_path):
        """Renderizar la pestaña de edición"""
        st.header("✏️ Edición de Indicadores")
        
        if len(df) == 0:
            st.warning("⚠️ No hay datos disponibles para editar")
            return
        
        try:
            # Seleccionar indicador por código
            codigos = sorted(df['Codigo'].unique())
            codigo_editar = st.selectbox(
                "🔍 Seleccionar Código de Indicador", 
                codigos, 
                key="codigo_editar"
            )
            
            if codigo_editar:
                # Mostrar información del indicador
                info_indicador = df[df['Codigo'] == codigo_editar]
                if not info_indicador.empty:
                    nombre_indicador = info_indicador['Indicador'].iloc[0]
                    st.info(f"**🎯 Indicador seleccionado:** {nombre_indicador}")
                    
                    # Mostrar información actual
                    st.subheader("📊 Valores actuales")
                    df_display = info_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']].copy()
                    df_display['Fecha'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
                    st.dataframe(df_display, use_container_width=True)
                    
                    # Formulario de edición
                    with st.form("form_edicion"):
                        st.subheader("✏️ Editar valor")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            try:
                                fechas_options = sorted(df['Fecha'].unique())
                                fecha_editar = st.date_input(
                                    "📅 Fecha",
                                    value=pd.to_datetime(fechas_options[-1]).date() if fechas_options else None
                                )
                            except:
                                fecha_editar = st.date_input("📅 Fecha")
                        
                        with col2:
                            # Buscar valor actual para esa fecha
                            fecha_dt = pd.to_datetime(fecha_editar)
                            valor_actual = info_indicador[
                                info_indicador['Fecha'] == fecha_dt
                            ]['Valor'].values
                            
                            valor_editar = st.number_input(
                                "🎯 Nuevo valor",
                                value=float(valor_actual[0]) if len(valor_actual) > 0 else 0.5,
                                min_value=0.0,
                                max_value=1.0,
                                step=0.1,
                                help="Los valores deben estar entre 0 y 1, donde 1 representa el 100%"
                            )
                        
                        # Botón para guardar
                        submitted = st.form_submit_button("💾 Guardar cambios", type="primary")
                        
                        if submitted:
                            fecha_dt = pd.to_datetime(fecha_editar)
                            if DataEditor.save_edit(df, codigo_editar, fecha_dt, valor_editar, csv_path):
                                st.success("✅ Datos actualizados correctamente")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar datos")
                else:
                    st.error("❌ No se encontró información para el código seleccionado")
        
        except Exception as e:
            st.error(f"❌ Error en la edición de indicadores: {e}")
            st.info("🔧 Asegúrate de que los datos contengan las columnas necesarias")

class TabManager:
    """Gestor de pestañas del dashboard"""
    
    def __init__(self, df, csv_path):
        self.df = df
        self.csv_path = csv_path
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas"""
        try:
            # Crear pestañas con iconos
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Resumen General", 
                "🏗️ Por Componente", 
                "📊 Evolución", 
                "📋 Tabla Dinámica", 
                "✏️ Edición"
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
                
        except Exception as e:
            st.error(f"❌ Error al renderizar pestañas: {e}")
            st.info("🔧 Intenta recargar la página o revisa los datos")
