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
            # IMPORTANTE: NO usar fecha_seleccionada para cálculos principales
            # Siempre calcular con valores más recientes para consistencia
            
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
            
            # Verificar que los cálculos fueron exitosos
            if puntajes_componente.empty and puntajes_categoria.empty and puntaje_general == 0:
                st.error("❌ No se pudieron calcular los puntajes. Revisar la estructura de los datos.")
                return
            
            # Mostrar información sobre qué datos se están usando
            st.info("""
            📊 **Cálculos basados en valores más recientes:** Los puntajes se calculan 
            usando el valor más reciente de cada indicador, asegurando consistencia 
            independientemente de cuándo se agregaron los datos.
            """)
            
            # Mostrar métricas generales
            MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente)
            
            # Crear layout con velocímetro más pequeño
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Gráfico de velocímetro (más pequeño)
                try:
                    st.plotly_chart(
                        ChartGenerator.gauge_chart(puntaje_general), 
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error en velocímetro: {e}")
            
            with col2:
                # Gráfico de radar (más grande) - también usando valores más recientes
                try:
                    st.plotly_chart(
                        ChartGenerator.radar_chart(df, None),  # None = usar valores más recientes
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
                    # Fallback: mostrar como tabla
                    st.dataframe(puntajes_componente, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar puntajes por componente")
            
        except Exception as e:
            st.error(f"❌ Error crítico al calcular puntajes: {e}")
            import traceback
            with st.expander("🔧 Detalles técnicos del error"):
                st.code(traceback.format_exc())
                st.write("**Información de debug:**")
                st.write(f"- Shape del DataFrame: {df.shape if df is not None else 'None'}")
                st.write(f"- Columnas: {list(df.columns) if df is not None else 'None'}")
                if df is not None and not df.empty:
                    st.write(f"- Códigos únicos: {df['Codigo'].nunique()}")
                    st.write(f"- Fechas únicas: {df['Fecha'].nunique()}")
            st.info("💡 Intenta recargar los datos usando el botón '🔄 Actualizar Datos'")
        
        # Mostrar tabla de datos más recientes
        with st.expander("📋 Ver datos más recientes por indicador"):
            try:
                df_latest = DataProcessor._get_latest_values_by_indicator(df)
                if not df_latest.empty:
                    st.dataframe(df_latest[['Codigo', 'Indicador', 'Componente', 'Categoria', 'Valor', 'Fecha']], use_container_width=True)
                else:
                    st.warning("No se pudieron obtener datos más recientes")
            except Exception as e:
                st.error(f"Error al mostrar datos: {e}")

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
        
        # Obtener valores más recientes y filtrar por componente
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        df_componente = df_latest[df_latest['Componente'] == componente_analisis]
        
        if not df_componente.empty:
            # Información sobre los datos que se están usando
            st.info(f"""
            📊 **Análisis de {componente_analisis}:** Basado en los valores más recientes 
            de cada indicador de este componente.
            """)
            
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
            
            # Tabla de categorías con colores - usando valores más recientes
            try:
                ChartGenerator.show_category_table_simple(df, componente_analisis)
            except Exception as e:
                st.error(f"Error al mostrar categorías: {e}")
                
                # Fallback: mostrar datos básicos
                st.subheader("📊 Datos por Categoría (Fallback)")
                try:
                    df_latest = DataProcessor._get_latest_values_by_indicator(df)
                    df_comp = df_latest[df_latest['Componente'] == componente_analisis]
                    
                    if not df_comp.empty:
                        categoria_stats = df_comp.groupby('Categoria')['Valor'].agg(['mean', 'count']).reset_index()
                        categoria_stats.columns = ['Categoría', 'Puntaje Promedio', 'Num. Indicadores']
                        st.dataframe(categoria_stats, use_container_width=True)
                    else:
                        st.warning("No hay datos del componente disponibles")
                except Exception as e2:
                    st.error(f"Error en fallback: {e2}")
            
            # Layout con gráficos lado a lado
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                # Gráfico de evolución del componente - usar datos históricos completos
                df_componente_historico = df[df['Componente'] == componente_analisis]
                fig_evol = ChartGenerator.evolution_chart(df_componente_historico, componente=componente_analisis)
                st.plotly_chart(fig_evol, use_container_width=True)
            
            with col_der:
                # Gráfico de radar por categorías - usar valores más recientes
                fig_radar_cat = ChartGenerator.radar_chart_categories(
                    df, componente_analisis, None  # None = usar valores más recientes
                )
                st.plotly_chart(fig_radar_cat, use_container_width=True)
            
            # Tabla de indicadores del componente - mostrar valores más recientes
            st.subheader(f"Indicadores Más Recientes de {componente_analisis}")
            st.dataframe(
                df_componente[['Indicador', 'Categoria', 'Valor', 'Fecha']].sort_values('Valor', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("No hay datos para el componente seleccionado")

class EvolutionTab:
    """Pestaña de evolución - CORREGIDA"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de evolución"""
        st.subheader("📈 Evolución Temporal de Indicadores")
        
        try:
            # Verificar que tenemos datos
            if df.empty:
                st.warning("No hay datos disponibles para mostrar evolución")
                return
            
            # Información sobre los datos disponibles
            st.info(f"""
            📊 **Datos disponibles:** {len(df)} registros de {df['Codigo'].nunique()} indicadores únicos
            📅 **Rango de fechas:** {df['Fecha'].min().strftime('%d/%m/%Y')} - {df['Fecha'].max().strftime('%d/%m/%Y')}
            """)
            
            # Crear filtros específicos de evolución
            evolution_filters = EvolutionFilters.create_evolution_filters(df)
            
            # Mostrar información del filtro seleccionado
            if evolution_filters['indicador']:
                st.success(f"**📊 Indicador seleccionado:** {evolution_filters['indicador']}")
                
                # Mostrar datos específicos del indicador
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if not datos_indicador.empty:
                    st.write(f"**Registros históricos encontrados:** {len(datos_indicador)}")
                    
                    # Mostrar tabla de datos del indicador
                    with st.expander("📋 Ver datos históricos del indicador"):
                        st.dataframe(
                            datos_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                            use_container_width=True
                        )
                else:
                    st.warning("No se encontraron datos históricos para este indicador")
                    return
            else:
                st.info("**📊 Vista general:** Mostrando evolución promedio de todos los indicadores")
            
            # Generar gráfico de evolución
            try:
                fig = ChartGenerator.evolution_chart(
                    df,
                    indicador=evolution_filters['indicador'],
                    componente=None,  # No filtrar por componente aquí
                    tipo_grafico=evolution_filters['tipo_grafico'],
                    mostrar_meta=evolution_filters['mostrar_meta']
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error al generar gráfico: {e}")
                import traceback
                with st.expander("Detalles del error"):
                    st.code(traceback.format_exc())
            
            # Mostrar análisis adicional si hay un indicador seleccionado
            if evolution_filters['codigo'] and evolution_filters['indicador']:
                st.subheader(f"📊 Análisis Detallado: {evolution_filters['indicador']}")
                
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if len(datos_indicador) > 1:
                    # Métricas de evolución
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        valor_inicial = datos_indicador.iloc[0]['Valor']
                        st.metric("Valor Inicial", f"{valor_inicial:.3f}")
                    
                    with col2:
                        valor_actual = datos_indicador.iloc[-1]['Valor']
                        st.metric("Valor Actual", f"{valor_actual:.3f}")
                    
                    with col3:
                        cambio = valor_actual - valor_inicial
                        st.metric("Cambio Total", f"{cambio:+.3f}")
                    
                    with col4:
                        if valor_inicial != 0:
                            cambio_pct = (cambio / valor_inicial) * 100
                            st.metric("Cambio %", f"{cambio_pct:+.1f}%")
                        else:
                            st.metric("Cambio %", "N/A")
                
                # Tabla de datos históricos
                st.dataframe(
                    datos_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"Error crítico en pestaña de evolución: {e}")
            import traceback
            with st.expander("🔧 Debug: Detalles del error"):
                st.code(traceback.format_exc())
                st.write("**Datos de entrada:**")
                st.write(f"- DataFrame shape: {df.shape if df is not None else 'None'}")
                st.write(f"- Filtros: {filters}")
                if df is not None and not df.empty:
                    st.write(f"- Columnas: {list(df.columns)}")
                    st.write(f"- Códigos únicos: {df['Codigo'].nunique() if 'Codigo' in df.columns else 'N/A'}")

class EditTab:
    """Pestaña de edición mejorada"""
    
    @staticmethod
    def render(df, csv_path):
        """Renderizar la pestaña de edición con capacidades completas"""
        st.subheader("Gestión de Indicadores")
        
        try:
            # Validar que hay datos
            if df.empty:
                st.error("No hay datos disponibles")
                return
            
            # Seleccionar indicador por código
            codigos_disponibles = sorted(df['Codigo'].dropna().unique())
            if not codigos_disponibles:
                st.error("No hay códigos de indicadores disponibles")
                return
                
            codigo_editar = st.selectbox("Seleccionar Código de Indicador", codigos_disponibles, key="codigo_editar")
            
            # Validar que el código seleccionado existe en los datos
            datos_indicador = df[df['Codigo'] == codigo_editar]
            if datos_indicador.empty:
                st.error(f"No se encontraron datos para el código {codigo_editar}")
                return
            
            # Mostrar información del indicador
            try:
                nombre_indicador = datos_indicador['Indicador'].iloc[0]
                componente_indicador = datos_indicador['Componente'].iloc[0]
                categoria_indicador = datos_indicador['Categoria'].iloc[0]
            except IndexError:
                st.error(f"Error al obtener información del indicador {codigo_editar}")
                return
            
            st.markdown(f"""
            **Indicador seleccionado:** {nombre_indicador}  
            **Componente:** {componente_indicador}  
            **Categoría:** {categoria_indicador}
            """)
            
            # Obtener registros existentes del indicador
            registros_indicador = datos_indicador.sort_values('Fecha', ascending=False)
            
            # Crear pestañas para diferentes acciones
            tab_ver, tab_agregar, tab_editar, tab_eliminar = st.tabs([
                "📋 Ver Registros", 
                "➕ Agregar Nuevo", 
                "✏️ Editar Existente", 
                "🗑️ Eliminar Registro"
            ])
            
            with tab_ver:
                st.subheader("Registros Existentes")
                if not registros_indicador.empty:
                    st.dataframe(
                        registros_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                        use_container_width=True
                    )
                else:
                    st.info("No hay registros para este indicador")
            
            with tab_agregar:
                EditTab._render_add_form(df, codigo_editar, nombre_indicador, csv_path)
            
            with tab_editar:
                EditTab._render_edit_form(df, codigo_editar, registros_indicador, csv_path)
            
            with tab_eliminar:
                EditTab._render_delete_form(df, codigo_editar, registros_indicador, csv_path)
        
        except Exception as e:
            st.error(f"Error en la gestión de indicadores: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.info("Verifica que el archivo CSV contenga todas las columnas necesarias")
    
    @staticmethod
    def _render_add_form(df, codigo_editar, nombre_indicador, csv_path):
        """Formulario para agregar nuevo registro"""
        st.subheader("Agregar Nuevo Registro")
        
        with st.form("form_agregar"):
            col1, col2 = st.columns(2)
            
            with col1:
                nueva_fecha = st.date_input(
                    "Nueva Fecha",
                    help="Selecciona la fecha para el nuevo registro"
                )
            
            with col2:
                nuevo_valor = st.number_input(
                    "Nuevo Valor",
                    value=0.5,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    help="Valor entre 0 y 1, donde 1 = 100% de cumplimiento"
                )
            
            submitted = st.form_submit_button("➕ Agregar Registro", use_container_width=True)
            
            if submitted:
                # Verificar si ya existe un registro para esa fecha
                fecha_dt = pd.to_datetime(nueva_fecha)
                registro_existente = df[(df['Codigo'] == codigo_editar) & (df['Fecha'] == fecha_dt)]
                
                if not registro_existente.empty:
                    st.warning(f"Ya existe un registro para la fecha {nueva_fecha.strftime('%d/%m/%Y')}. Usa la pestaña 'Editar' para modificarlo.")
                else:
                    if DataEditor.add_new_record(df, codigo_editar, fecha_dt, nuevo_valor, csv_path):
                        st.success("✅ Nuevo registro agregado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al agregar el nuevo registro")
    
    @staticmethod
    def _render_edit_form(df, codigo_editar, registros_indicador, csv_path):
        """Formulario para editar registro existente"""
        st.subheader("Editar Registro Existente")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para editar")
            return
        
        # Seleccionar registro a editar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a editar",
            fechas_disponibles,
            help="Selecciona el registro que deseas modificar"
        )
        
        if fecha_seleccionada_str:
            # Obtener la fecha real
            idx_seleccionado = fechas_disponibles.index(fecha_seleccionada_str)
            fecha_real = registros_indicador.iloc[idx_seleccionado]['Fecha']
            valor_actual = registros_indicador.iloc[idx_seleccionado]['Valor']
            
            with st.form("form_editar"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📅 Fecha: {fecha_real.strftime('%d/%m/%Y')}")
                    st.info(f"📊 Valor actual: {valor_actual:.3f}")
                
                with col2:
                    nuevo_valor = st.number_input(
                        "Nuevo Valor",
                        value=float(valor_actual),
                        min_value=0.0,
                        max_value=1.0,
                        step=0.01,
                        help="Nuevo valor para este registro"
                    )
                
                submitted = st.form_submit_button("✏️ Actualizar Registro", use_container_width=True)
                
                if submitted:
                    if DataEditor.update_record(df, codigo_editar, fecha_real, nuevo_valor, csv_path):
                        st.success(f"✅ Registro del {fecha_real.strftime('%d/%m/%Y')} actualizado correctamente")
                        st.balloons()
                        # Forzar recarga inmediata
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar el registro")
    
    @staticmethod
    def _render_delete_form(df, codigo_editar, registros_indicador, csv_path):
        """Formulario para eliminar registro"""
        st.subheader("Eliminar Registro")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para eliminar")
            return
        
        # Seleccionar registro a eliminar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a eliminar",
            fechas_disponibles,
            help="⚠️ CUIDADO: Esta acción no se puede deshacer"
        )
        
        if fecha_seleccionada_str:
            # Obtener la fecha real
            idx_seleccionado = fechas_disponibles.index(fecha_seleccionada_str)
            fecha_real = registros_indicador.iloc[idx_seleccionado]['Fecha']
            valor_actual = registros_indicador.iloc[idx_seleccionado]['Valor']
            
            st.warning(f"""
            ⚠️ **ATENCIÓN**: Estás a punto de eliminar el registro:
            - **Fecha**: {fecha_real.strftime('%d/%m/%Y')}
            - **Valor**: {valor_actual:.3f}
            
            Esta acción **NO SE PUEDE DESHACER**.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                confirmar = st.checkbox("Confirmo que quiero eliminar este registro", key="confirm_delete")
            
            with col2:
                if confirmar:
                    if st.button("🗑️ ELIMINAR REGISTRO", type="primary", use_container_width=True):
                        if DataEditor.delete_record(df, codigo_editar, fecha_real, csv_path):
                            st.success(f"✅ Registro del {fecha_real.strftime('%d/%m/%Y')} eliminado correctamente")
                            st.balloons()
                            # Forzar recarga inmediata
                            st.cache_data.clear()
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el registro")

class TabManager:
    """Gestor de pestañas del dashboard"""
    
    def __init__(self, df, csv_path, excel_data=None):
    self.df = df
    self.csv_path = csv_path
    self.excel_data = excel_data
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas (sin tabla dinámica)"""
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
            EditTab.render(self.df, self.csv_path)
