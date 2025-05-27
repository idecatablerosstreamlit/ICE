"""
Interfaces de usuario para las pestañas del Dashboard ICE
"""

import streamlit as st
import pandas as pd
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor

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
            
            # Gráfico de radar (spider)
            st.plotly_chart(
                ChartGenerator.radar_chart(df, fecha_seleccionada), 
                use_container_width=True
            )
            
            # Gráfico de score general - evolución temporal del puntaje general
            st.subheader("Evolución del Score General")
            fig_score = ChartGenerator.evolution_chart(df, tipo_grafico="Línea", mostrar_meta=True)
            st.plotly_chart(fig_score, use_container_width=True)
            
            # Puntajes por componente
            st.subheader("Puntajes por Componente")
            if not puntajes_componente.empty:
                fig_comp = ChartGenerator.component_bar_chart(puntajes_componente)
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Tabla de puntajes por componente
                st.dataframe(puntajes_componente, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar puntajes por componente")
            
            # Tabla de puntajes por categoría
            st.subheader("Puntajes por Categoría")
            if not puntajes_categoria.empty:
                st.dataframe(puntajes_categoria, use_container_width=True)
            
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
            # Métricas del componente
            col1, col2, col3 = st.columns(3)
            
            with col1:
                valor_promedio = df_componente['Valor'].mean()
                st.metric("Valor Promedio", f"{valor_promedio:.2f}")
            
            with col2:
                total_indicadores = df_componente['Indicador'].nunique()
                st.metric("Total Indicadores", total_indicadores)
            
            with col3:
                ultima_medicion = df_componente['Fecha'].max()
                st.metric("Última Medición", ultima_medicion.strftime('%d/%m/%Y'))
            
            # Gráfico spider/radar para el componente seleccionado
            st.subheader(f"Diagrama Spider - {componente_analisis}")
            fig_spider = ChartGenerator.radar_chart(df_componente, filters.get('fecha'))
            st.plotly_chart(fig_spider, use_container_width=True)
            
            # Gráfico de evolución del componente
            st.subheader(f"Evolución Temporal - {componente_analisis}")
            fig_evol = ChartGenerator.evolution_chart(df_componente, componente=componente_analisis)
            st.plotly_chart(fig_evol, use_container_width=True)
            
            # Tabla de métricas y avances por categoría dentro del componente
            st.subheader(f"Métricas por Categoría - {componente_analisis}")
            try:
                puntajes_componente, puntajes_categoria_comp, puntaje_general_comp = DataProcessor.calculate_scores(
                    df_componente, filters.get('fecha')
                )
                
                # Mostrar tabla de avances por categoría
                categorias_componente = df_componente.groupby('Categoria').agg({
                    'Valor': ['mean', 'count', 'min', 'max'],
                    'Indicador': 'nunique'
                }).round(3)
                
                categorias_componente.columns = ['Promedio', 'Total_Mediciones', 'Mínimo', 'Máximo', 'Num_Indicadores']
                categorias_componente['Cumplimiento_%'] = (categorias_componente['Promedio'] * 100).round(1)
                
                st.dataframe(categorias_componente, use_container_width=True)
                
            except Exception as e:
                st.warning(f"No se pudieron calcular métricas por categoría: {e}")
            
            # Tabla detallada de indicadores del componente
            st.subheader(f"Detalle de Indicadores - {componente_analisis}")
            tabla_detalle = df_componente[['Codigo', 'Indicador', 'Categoria', 'Valor', 'Fecha']].sort_values(['Categoria', 'Fecha'], ascending=[True, False])
            st.dataframe(tabla_detalle, use_container_width=True)
            
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
            col1, col2 = st.columns(2)
            
            with col1:
                # Por código de indicador
                codigos = sorted(df['Codigo'].unique())
                codigo_seleccionado = st.selectbox("Código de Indicador", ["Todos"] + list(codigos))
                
                if codigo_seleccionado == "Todos":
                    codigo_seleccionado = None
                    indicador_seleccionado = None
                else:
                    indicador_seleccionado = df[df['Codigo'] == codigo_seleccionado]['Indicador'].iloc[0]
            
            with col2:
                # Opción para mostrar línea de meta
                mostrar_meta = st.checkbox("Mostrar línea de referencia (Meta = 1.0)", value=True)
                
                # Seleccionar tipo de gráfico
                tipo_grafico = st.radio(
                    "Tipo de gráfico",
                    options=["Línea", "Barras"],
                    horizontal=True
                )
            
            # Mostrar nombre del indicador seleccionado
            if indicador_seleccionado:
                st.write(f"**Indicador seleccionado:** {indicador_seleccionado}")
            
            # Generar gráfico de evolución
            fig = ChartGenerator.evolution_chart(
                df,
                indicador=indicador_seleccionado,
                componente=filters.get('componente'),
                tipo_grafico=tipo_grafico,
                mostrar_meta=mostrar_meta
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabla de datos del indicador seleccionado
            if codigo_seleccionado:
                st.subheader(f"Datos del indicador: {indicador_seleccionado}")
                datos_indicador = df[df['Codigo'] == codigo_seleccionado].sort_values('Fecha')
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
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filas = st.selectbox(
                    "Filas",
                    options=["Categoria", "Componente", "Linea_Accion", "Codigo"],
                    index=0
                )
            
            with col2:
                columnas = st.selectbox(
                    "Columnas",
                    options=["Componente", "Categoria", "Linea_Accion", "Codigo"],
                    index=0
                )
            
            with col3:
                valores = st.selectbox(
                    "Valores",
                    options=["Valor", "Cumplimiento", "Puntaje_Ponderado"],
                    index=0
                )
            
            # Validar que filas y columnas sean diferentes
            if filas == columnas:
                st.warning("Las filas y columnas deben ser diferentes.")
            else:
                # Crear tabla dinámica
                tabla = DataProcessor.create_pivot_table(
                    df,
                    fecha=fecha_seleccionada,
                    filas=filas,
                    columnas=columnas,
                    valores=valores
                )
                
                # Mostrar tabla con formato condicional
                st.dataframe(
                    tabla.style.background_gradient(cmap='YlGn'), 
                    use_container_width=True
                )
                
                # Opción para descargar
                csv = tabla.to_csv(index=True)
                st.download_button(
                    label="Descargar tabla como CSV",
                    data=csv,
                    file_name=f"tabla_dinamica_{fecha_seleccionada.strftime('%Y%m%d')}.csv",
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
                        fechas_options = sorted(df['Fecha'].unique())
                        fecha_editar = st.date_input(
                            "Fecha",
                            value=pd.to_datetime(fechas_options[-1]).date() if fechas_options else None
                        )
                    except:
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
