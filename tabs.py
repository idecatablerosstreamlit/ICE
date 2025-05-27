"""
Interfaces de usuario para las pestañas del Dashboard ICE
"""

import streamlit as st
import pandas as pd
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor

# Funciones de filtros integradas directamente
def create_evolution_filters(df):
    """Crear filtros para la pestaña de evolución"""
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
    
    return {
        'codigo': codigo_seleccionado,
        'indicador': indicador_seleccionado,
        'mostrar_meta': mostrar_meta,
        'tipo_grafico': tipo_grafico
    }

def create_pivot_filters():
    """Crear filtros para la tabla dinámica"""
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
    
    return {
        'filas': filas,
        'columnas': columnas,
        'valores': valores
    }

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
            
            # Gráfico de radar
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
            # Métricas del componente con HTML personalizado para mejor visibilidad
            col1, col2, col3 = st.columns(3)
            
            with col1:
                valor_promedio = df_componente['Valor'].mean()
                st.markdown(f"""
                <div style="background-color: #404040; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #E0E0E0; margin: 0 0 0.5rem 0;">Valor Promedio</h4>
                    <h2 style="color: #FFFFFF; margin: 0; font-size: 2rem;">{valor_promedio:.2f}</h2>
                    <p style="color: #B0B0B0; margin: 0.5rem 0 0 0;">{valor_promedio*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_indicadores = df_componente['Indicador'].nunique()
                st.markdown(f"""
                <div style="background-color: #404040; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #E0E0E0; margin: 0 0 0.5rem 0;">Total Indicadores</h4>
                    <h2 style="color: #FFFFFF; margin: 0; font-size: 2rem;">{total_indicadores}</h2>
                    <p style="color: #B0B0B0; margin: 0.5rem 0 0 0;">indicadores</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                ultima_medicion = df_componente['Fecha'].max()
                st.markdown(f"""
                <div style="background-color: #404040; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #E0E0E0; margin: 0 0 0.5rem 0;">Última Medición</h4>
                    <h2 style="color: #FFFFFF; margin: 0; font-size: 1.5rem;">{ultima_medicion.strftime('%d/%m/%Y')}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico de evolución del componente
            fig_evol = ChartGenerator.evolution_chart(df_componente, componente=componente_analisis)
            st.plotly_chart(fig_evol, use_container_width=True)
            
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
            evolution_filters = create_evolution_filters(df)
            
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
            pivot_filters = create_pivot_filters()
            
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
