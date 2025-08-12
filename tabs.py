"""
Interfaces de usuario para las pestañas del Dashboard ICE - VERSIÓN SIMPLIFICADA SIN FILTROS
SOLO FECHA DE ÚLTIMA ACTUALIZACIÓN EN RESUMEN GENERAL
"""

import streamlit as st
import pandas as pd
import time
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor
from filters import EvolutionFilters
from datetime import datetime

class GeneralSummaryTab:
    """Pestaña de resumen general"""
    
    @staticmethod
    def render(df, fecha_seleccionada=None):
        """Renderizar la pestaña de resumen general - SIN FILTROS"""
        st.header("Resumen General")
        
        try:
            # Verificación previa de datos
            if df.empty:
                st.info("Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
                st.markdown("""
                ### Primeros pasos:
                1. Ve a la pestaña **"Gestión de Datos"**
                2. Selecciona un código de indicador (o crea uno nuevo)
                3. Agrega algunos registros con valores y fechas
                4. Los datos se guardarán automáticamente en Google Sheets
                5. Regresa aquí para ver los análisis
                """)
                return
                
            required_cols = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Faltan columnas esenciales en Google Sheets: {missing_cols}")
                st.write("**Columnas disponibles:**", list(df.columns))
                return
            
            # Verificar que hay datos válidos
            datos_validos = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            if datos_validos.empty:
                st.info("Los datos en Google Sheets están vacíos o incompletos")
                return
            
            # ✅ OBTENER FECHA DE ÚLTIMA ACTUALIZACIÓN
            ultima_actualizacion = GeneralSummaryTab._get_last_update_info(df)
            
            # ✅ MOSTRAR FECHA DE ÚLTIMA ACTUALIZACIÓN
            if ultima_actualizacion:
                fecha_str = ultima_actualizacion['fecha'].strftime('%d/%m/%Y')
                
                
                # Card de última actualización
                # Tarjeta de última actualización - MEJORADA
                st.markdown(f"""
                <div style="
                    background: #272f7a; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    margin: 1.5rem 0; 
                    color: white;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 4px solid #4a90e2;
                ">
                    <div style="
                        display: flex; 
                        justify-content: space-between; 
                        align-items: flex-start;
                        margin-bottom: 1rem;
                    ">
                        <h3 style="
                            color: white; 
                            margin: 0; 
                            font-size: 1.2rem; 
                            font-weight: 600;
                        ">Última Actualización</h3>
                        <span style="
                            background: rgba(255, 255, 255, 0.2); 
                            padding: 0.25rem 0.75rem; 
                            border-radius: 20px; 
                            font-size: 0.9rem; 
                            font-weight: 500;
                        ">{fecha_str}</span>
                    </div>
                    
                    <div style="
                        display: grid; 
                        grid-template-columns: 1fr 1fr; 
                        gap: 1rem; 
                        margin-top: 1rem;
                    ">
                        <div>
                            <div style="
                                font-size: 0.85rem; 
                                opacity: 0.8; 
                                margin-bottom: 0.25rem;
                            ">Indicador</div>
                            <div style="
                                font-weight: 500; 
                                line-height: 1.3;
                                font-size: 0.9rem;
                            ">{ultima_actualizacion['indicador']}</div>
                        </div>
                        
                        <div>
                            <div style="
                                font-size: 0.85rem; 
                                opacity: 0.8; 
                                margin-bottom: 0.25rem;
                            ">Código</div>
                            <div style="
                                font-weight: 500; 
                                font-family: monospace; 
                                background: rgba(255, 255, 255, 0.1); 
                                padding: 0.25rem 0.5rem; 
                                border-radius: 4px; 
                                display: inline-block;
                                font-size: 0.9rem;
                            ">{ultima_actualizacion['codigo']}</div>
                        </div>
                        
                        <div style="grid-column: 1 / -1;">
                            <div style="
                                font-size: 0.85rem; 
                                opacity: 0.8; 
                                margin-bottom: 0.25rem;
                            ">Componente</div>
                            <div style="
                                font-weight: 500;
                                font-size: 0.9rem;
                            ">{ultima_actualizacion['componente']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                
            
            # ✅ CALCULAR PUNTAJES SIN FILTROS (siempre valores más recientes)
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(df)
            
            # Verificar que los cálculos fueron exitosos
            if puntajes_componente.empty and puntajes_categoria.empty and puntaje_general == 0:
                st.info("Agregando más datos podrás ver los puntajes y análisis")
                return
            
            # Mostrar información sobre qué datos se están usando
            st.info("**Puntajes calculados usando valores más recientes:** Los indicadores se normalizan según su tipo antes del cálculo.")
            
            # Mostrar métricas generales
            MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente)
            
            # Crear layout con velocímetro y radar
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Gráfico de velocímetro
                try:
                    st.plotly_chart(
                        ChartGenerator.gauge_chart(puntaje_general), 
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error en velocímetro: {e}")
            
            with col2:
                # Gráfico de radar (sin filtros)
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
                st.info("Agrega más datos para ver puntajes por componente")
        
        except ValueError as e:
            st.error(f"Error de valor en cálculos: {e}")
        except KeyError as e:
            st.error(f"Columna faltante: {e}")
        except Exception as e:
            st.error(f"Error inesperado al calcular puntajes: {e}")
            with st.expander("Detalles del error"):
                st.code(str(e))
        
        # Mostrar tabla de datos más recientes
        with st.expander("Ver datos más recientes por indicador"):
            try:
                df_latest = DataProcessor._get_latest_values_by_indicator(df)
                
                if not df_latest.empty:
                    columns_to_show = ['Codigo', 'Indicador', 'Componente', 'Categoria', 'Valor', 'Tipo', 'Valor_Normalizado', 'Fecha']
                    available_columns = [col for col in columns_to_show if col in df_latest.columns]
                    st.dataframe(df_latest[available_columns], use_container_width=True)
                else:
                    st.info("No hay datos para mostrar")
            except Exception as e:
                st.error(f"Error al mostrar datos: {e}")
    
    @staticmethod
    def _get_last_update_info(df):
        """Obtener información de la última actualización"""
        try:
            if df.empty or 'Fecha' not in df.columns:
                return None
            
            # Obtener la fecha más reciente de todos los registros
            fechas_validas = df['Fecha'].dropna()
            if fechas_validas.empty:
                return None
            
            # Convertir a datetime si es necesario
            if not pd.api.types.is_datetime64_any_dtype(fechas_validas):
                fechas_validas = pd.to_datetime(fechas_validas, errors='coerce').dropna()
            
            if fechas_validas.empty:
                return None
            
            # Obtener la fecha más reciente
            ultima_fecha = fechas_validas.max()
            
            # Obtener información del indicador que se actualizó más recientemente
            registro_mas_reciente = df[df['Fecha'] == ultima_fecha].iloc[0]
            
            return {
                'fecha': ultima_fecha,
                'indicador': registro_mas_reciente.get('Indicador', 'N/A'),
                'codigo': registro_mas_reciente.get('Codigo', 'N/A'),
                'componente': registro_mas_reciente.get('Componente', 'N/A')
            }
            
        except Exception as e:
            return None

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters=None):
        """Renderizar la pestaña de resumen por componente - SIN FILTROS"""
        st.header("Resumen por Componente")
        
        if df.empty:
            st.info("No hay datos disponibles para análisis por componente")
            return
        
        # ✅ SIEMPRE USAR VALORES MÁS RECIENTES (sin filtros)
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        
        # Selector de componente específico para esta vista
        componentes = sorted(df_latest['Componente'].unique()) if not df_latest.empty else []
        if not componentes:
            st.info("No hay componentes disponibles")
            return
            
        componente_analisis = st.selectbox(
            "Seleccionar componente para análisis detallado", 
            componentes,
            key="comp_analysis_main"
        )
        
        # Filtrar por componente seleccionado
        df_componente = df_latest[df_latest['Componente'] == componente_analisis]
        
        if not df_componente.empty:
            # Información sobre los datos que se están usando
            st.info(f"**Análisis de {componente_analisis}:** Basado en valores más recientes de cada indicador.")
            
            # Métricas del componente
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Valor_Normalizado' in df_componente.columns:
                    valor_promedio = df_componente['Valor_Normalizado'].mean()
                else:
                    valor_promedio = df_componente['Valor'].mean()
                st.metric("Valor Promedio", f"{valor_promedio:.3f}")
            
            with col2:
                total_indicadores = df_componente['Indicador'].nunique()
                st.metric("Total Indicadores", total_indicadores)
            
            with col3:
                ultima_medicion = df_componente['Fecha'].max()
                if pd.notna(ultima_medicion):
                    try:
                        fecha_str = pd.to_datetime(ultima_medicion).strftime('%d/%m/%Y')
                        st.metric("Última Medición", fecha_str)
                    except:
                        st.metric("Última Medición", "No disponible")
                else:
                    st.metric("Última Medición", "No disponible")
            
            # Tabla de categorías (sin filtros)
            try:
                ChartGenerator.show_category_table_simple(df, componente_analisis)
            except Exception as e:
                st.error(f"Error al mostrar categorías: {e}")
            
            # Layout con gráficos lado a lado
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                # Gráfico de evolución del componente
                df_componente_historico = df[df['Componente'] == componente_analisis]
                fig_evol = ChartGenerator.evolution_chart(df_componente_historico, componente=componente_analisis)
                st.plotly_chart(fig_evol, use_container_width=True)
            
            with col_der:
                # Selector de tipo de visualización (sin filtros)
                ComponentSummaryTab._render_category_visualization(df, componente_analisis)
            
            # Tabla de indicadores del componente
            st.subheader(f"Indicadores Más Recientes de {componente_analisis}")
            columns_to_show = ['Indicador', 'Categoria', 'Valor', 'Tipo', 'Valor_Normalizado', 'Fecha']
            available_columns = [col for col in columns_to_show if col in df_componente.columns]
            
            st.dataframe(
                df_componente[available_columns].sort_values('Valor_Normalizado' if 'Valor_Normalizado' in df_componente.columns else 'Valor', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("No hay datos para el componente seleccionado")
    
    @staticmethod
    def _render_category_visualization(df, componente):
        """Renderizar visualización de categorías - SIN FILTROS"""
        
        # Usar valores más recientes
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        df_componente = df_latest[df_latest['Componente'] == componente]
        
        # Contar categorías para determinar mejor visualización
        num_categorias = df_componente['Categoria'].nunique()
        
        # Selector de tipo de visualización
        if num_categorias < 3:
            opciones = [
                "Barras Horizontales",
                "Radar (requiere 3+ categorías)"
            ]
            default_viz = "Barras Horizontales"
        else:
            opciones = [
                "Barras Horizontales", 
                "Radar de Categorías"
            ]
            default_viz = "Radar de Categorías"
        
        tipo_viz = st.selectbox(
            f"Visualización para {componente} ({num_categorias} categorías):",
            opciones,
            index=0 if "Barras" in default_viz else 1,
            key=f"viz_selector_{componente}"
        )
        
        # Renderizar la visualización seleccionada (sin filtros)
        if "Barras" in tipo_viz:
            # Usar barras horizontales
            fig_bar = ChartGenerator.horizontal_bar_chart(df, componente, None)
            st.plotly_chart(fig_bar, use_container_width=True)
        elif "Radar" in tipo_viz:
            if num_categorias >= 3:
                # Usar radar de categorías
                fig_radar_cat = ChartGenerator.radar_chart_categories(df, componente, None)
                st.plotly_chart(fig_radar_cat, use_container_width=True)
            else:
                st.warning(f"Se requieren al menos 3 categorías para el radar. {componente} tiene {num_categorias}.")
                # Fallback a barras horizontales
                fig_bar = ChartGenerator.horizontal_bar_chart(df, componente, None)
                st.plotly_chart(fig_bar, use_container_width=True)

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters=None):
        """Renderizar la pestaña de evolución - FUNCIONALIDAD COMPLETA PRESERVADA"""
        st.header("Evolución Temporal de Indicadores")
        
        try:
            if df.empty:
                st.info("No hay datos suficientes para mostrar evolución")
                return
            
            # Información sobre los datos disponibles
            st.info(f"**Datos:** {len(df)} registros de {df['Codigo'].nunique()} indicadores únicos")
            
            # Crear filtros sin causar rerun
            evolution_filters = EvolutionFilters.create_evolution_filters_stable(df)
            
            # Mostrar información del filtro seleccionado
            if evolution_filters['indicador']:
                st.success(f"**Indicador seleccionado:** {evolution_filters['indicador']}")
                
                # Mostrar datos específicos del indicador
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if not datos_indicador.empty:
                    st.write(f"**Registros históricos encontrados:** {len(datos_indicador)}")
                    
                    # Mostrar tabla de datos del indicador
                    with st.expander("Ver datos históricos del indicador"):
                        columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
                        available_columns = [col for col in columns_to_show if col in datos_indicador.columns]
                        st.dataframe(datos_indicador[available_columns], use_container_width=True)
                else:
                    st.warning("No se encontraron datos históricos para este indicador")
                    return
            else:
                st.info("**Vista general:** Mostrando evolución promedio de todos los indicadores")
            
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
            
            # Mostrar análisis adicional si hay un indicador seleccionado
            if evolution_filters['codigo'] and evolution_filters['indicador']:
                st.subheader(f"Análisis Detallado: {evolution_filters['indicador']}")
                
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if len(datos_indicador) > 1:
                    # Métricas de evolución usando valores normalizados
                    col1, col2, col3, col4 = st.columns(4)
                    
                    valor_col = 'Valor_Normalizado' if 'Valor_Normalizado' in datos_indicador.columns else 'Valor'
                    
                    with col1:
                        valor_inicial = datos_indicador.iloc[0][valor_col]
                        st.metric("Valor Inicial (Norm.)", f"{valor_inicial:.3f}")
                    
                    with col2:
                        valor_actual = datos_indicador.iloc[-1][valor_col]
                        st.metric("Valor Actual (Norm.)", f"{valor_actual:.3f}")
                    
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
                columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
                available_columns = [col for col in columns_to_show if col in datos_indicador.columns]
                st.dataframe(datos_indicador[available_columns], use_container_width=True)
        
        except ValueError as e:
            st.error(f"Error de valor en evolución: {e}")
        except KeyError as e:
            st.error(f"Columna faltante en evolución: {e}")
        except Exception as e:
            st.error(f"Error crítico en pestaña de evolución: {e}")
            with st.expander("Detalles del error"):
                st.code(str(e))

class EditTab:
    """Pestaña de edición - FUNCIONALIDAD COMPLETA PRESERVADA"""
    
    @staticmethod
    def render(df, csv_path, excel_data=None):
        """Renderizar la pestaña de edición con Google Sheets - TODAS LAS FUNCIONALIDADES"""
        st.header("Gestión de Indicadores")
        
        try:
            # Verificar que Google Sheets esté disponible
            from data_utils import GOOGLE_SHEETS_AVAILABLE
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("Servicio no disponible. Instala las dependencias: `pip install gspread google-auth`")
                return
            
            # Inicializar session state para preservar selecciones
            if 'selected_codigo_edit' not in st.session_state:
                st.session_state.selected_codigo_edit = None
            
            # Selector de código persistente
            codigo_editar = EditTab._render_codigo_selector(df)
            
            if codigo_editar == "CREAR_NUEVO":
                EditTab._render_new_indicator_form(df)
                return
            
            # Validar que el código seleccionado existe en los datos
            datos_indicador = df[df['Codigo'] == codigo_editar] if not df.empty else pd.DataFrame()
            
            if datos_indicador.empty and not df.empty:
                st.error(f"No se encontraron datos para el código {codigo_editar}")
                return
            elif not df.empty:
                # Mostrar información del indicador
                EditTab._render_indicator_info_card(datos_indicador, codigo_editar)
            
            # Información metodológica en expander (ESTABLE)
            EditTab._render_metodological_expander(codigo_editar, excel_data)
            
            # Obtener registros existentes del indicador
            if not df.empty and not datos_indicador.empty:
                registros_indicador = datos_indicador.sort_values('Fecha', ascending=False)
            else:
                registros_indicador = pd.DataFrame()
            
            # SUB-PESTAÑAS NATIVAS - SIN ST.RERUN
            EditTab._render_management_tabs(df, codigo_editar, registros_indicador)
        
        except ImportError as e:
            st.error(f"Error de importación: {e}")
        except Exception as e:
            st.error(f"Error en la gestión de indicadores: {e}")
            with st.expander("Detalles del error"):
                st.code(str(e))
    
    @staticmethod
    def _render_codigo_selector(df):
        """Selector de código persistente y estable"""
        # Obtener códigos disponibles
        if df.empty:
            st.info("Base de datos vacía. Puedes crear un nuevo indicador.")
            return "CREAR_NUEVO"
        
        codigos_disponibles = sorted(df['Codigo'].dropna().unique())
        opciones_codigo = ["[Crear nuevo código]"] + list(codigos_disponibles)
        
        # Determinar índice actual basado en session state
        index_actual = 0
        if st.session_state.selected_codigo_edit and st.session_state.selected_codigo_edit in codigos_disponibles:
            try:
                index_actual = opciones_codigo.index(st.session_state.selected_codigo_edit)
            except ValueError:
                index_actual = 0
        
        codigo_seleccionado = st.selectbox(
            "Seleccionar Código de Indicador", 
            opciones_codigo,
            index=index_actual,
            key="codigo_editar_selector",
            help="Los datos se guardan automáticamente"
        )
        
        # Actualizar session state
        if codigo_seleccionado == "[Crear nuevo código]":
            return "CREAR_NUEVO"
        else:
            st.session_state.selected_codigo_edit = codigo_seleccionado
            return codigo_seleccionado
    
    @staticmethod
    def _render_indicator_info_card(datos_indicador, codigo_editar):
        """Mostrar información del indicador en card"""
        try:
            nombre_indicador = datos_indicador['Indicador'].iloc[0]
            componente_indicador = datos_indicador['Componente'].iloc[0]
            categoria_indicador = datos_indicador['Categoria'].iloc[0]
            tipo_indicador = datos_indicador.get('Tipo', pd.Series(['porcentaje'])).iloc[0]
            
            # Card con información del indicador
            st.markdown(f"""
            <div style="background: linear-gradient(45deg, #4472C4 0%, #5B9BD5 100%); 
                       padding: 1rem; border-radius: 10px; margin: 1rem 0; color: white;">
                <h4 style="color: white; margin: 0;">{nombre_indicador}</h4>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    <strong>Componente:</strong> {componente_indicador}<br>
                    <strong>Categoría:</strong> {categoria_indicador}<br>
                    <strong>Código:</strong> {codigo_editar}<br>
                    <strong>Tipo:</strong> {tipo_indicador}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        except IndexError:
            st.error(f"Error al obtener información del indicador {codigo_editar}")
    
    @staticmethod
    def _render_metodological_expander(codigo_editar, excel_data):
        """Renderizar información metodológica en expander estable"""
        with st.expander("Información Metodológica"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Ficha Metodológica")
                if excel_data is not None and not excel_data.empty:
                    indicador_metodologico = excel_data[excel_data['Codigo'] == codigo_editar]
                    
                    if not indicador_metodologico.empty:
                        metodologia = indicador_metodologico.iloc[0]
                        
                        # Función auxiliar para obtener valores seguros
                        def safe_get(campo, default='N/A'):
                            try:
                                valor = metodologia.get(campo, default)
                                if pd.isna(valor) or valor == '' or str(valor).strip() == '':
                                    return default
                                return str(valor).strip()
                            except:
                                return default
                        
                        # Mostrar información básica
                        st.write(f"**Nombre:** {safe_get('Nombre_Indicador')}")
                        st.write(f"**Área Temática:** {safe_get('Area_Tematica')}")
                        st.write(f"**Sector:** {safe_get('Sector')}")
                        st.write(f"**Entidad:** {safe_get('Entidad')}")
                        
                        st.write("**Definición:**")
                        st.write(safe_get('Definicion'))
                    else:
                        st.warning(f"No se encontró información metodológica para {codigo_editar}")
                else:
                    st.warning("No hay datos metodológicos disponibles (falta archivo Excel)")
            
            with col2:
                st.subheader("Generar PDF")
                # Verificar disponibilidad de PDF
                try:
                    import reportlab
                    reportlab_available = True
                except ImportError:
                    reportlab_available = False
                
                if reportlab_available and excel_data is not None and not excel_data.empty:
                    codigo_existe = codigo_editar in excel_data['Codigo'].values
                    
                    if codigo_existe:
                        if st.button("Generar PDF", key=f"generate_pdf_{codigo_editar}"):
                            EditTab._generate_and_download_pdf(codigo_editar, excel_data)
                    else:
                        st.warning(f"No hay datos metodológicos para {codigo_editar}")
                        
                elif not reportlab_available:
                    st.error("Para generar PDFs instala: `pip install reportlab`")
                else:
                    st.warning("Necesitas el archivo 'Batería de indicadores.xlsx'")
    
    @staticmethod
    def _render_management_tabs(df, codigo_editar, registros_indicador):
        """Renderizar sub-pestañas de gestión usando st.tabs nativo"""
        
        # SUB-PESTAÑAS NATIVAS - SIN PROBLEMAS DE ESTADO
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
            "Ver Registros",
            "Agregar Nuevo", 
            "Editar Existente",
            "Eliminar Registro"
        ])
        
        with sub_tab1:
            EditTab._render_view_records(registros_indicador)
        
        with sub_tab2:
            EditTab._render_add_form(df, codigo_editar)
        
        with sub_tab3:
            EditTab._render_edit_form(df, codigo_editar, registros_indicador)
        
        with sub_tab4:
            EditTab._render_delete_form(df, codigo_editar, registros_indicador)
    
    @staticmethod
    def _render_view_records(registros_indicador):
        """Renderizar tabla de registros existentes"""
        st.subheader("Registros Existentes")
        if not registros_indicador.empty:
            columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
            available_columns = [col for col in columns_to_show if col in registros_indicador.columns]
            st.dataframe(registros_indicador[available_columns], use_container_width=True)
        else:
            st.info("No hay registros para este indicador")
    
    @staticmethod
    def _render_new_indicator_form(df):
        """Formulario para crear nuevo indicador en Google Sheets"""
        st.subheader("Crear Nuevo Indicador")
        
        from config import INDICATOR_TYPES
        
        with st.form("form_nuevo_indicador"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_codigo = st.text_input(
                    "Código del Indicador",
                    placeholder="Ej: D01-3",
                    help="Código único para identificar el indicador"
                )
                
                nuevo_indicador = st.text_input(
                    "Nombre del Indicador",
                    placeholder="Ej: Porcentaje de datos actualizados",
                    help="Nombre descriptivo del indicador"
                )
                
                nuevo_componente = st.selectbox(
                    "Componente",
                    ["Datos", "Seguridad e interoperabilidad", "Gobernanza y estratégia", 
                     "Herramientas técnicas y tecnológicas", "Aprovechamiento de datos"],
                    help="Componente al que pertenece el indicador"
                )
                
                # Selector de tipo
                nuevo_tipo = st.selectbox(
                    "Tipo de Indicador",
                    list(INDICATOR_TYPES.keys()),
                    help="Tipo de indicador para normalización correcta"
                )
            
            with col2:
                nueva_categoria = st.text_input(
                    "Categoría",
                    placeholder="Ej: 01. Disponibilidad",
                    help="Categoría específica dentro del componente"
                )
                
                nueva_linea = st.text_input(
                    "Línea de Acción",
                    placeholder="Ej: LA.2.3.",
                    help="Línea de acción correspondiente (opcional)"
                )
                
                # Mostrar información del tipo seleccionado
                if nuevo_tipo in INDICATOR_TYPES:
                    tipo_info = INDICATOR_TYPES[nuevo_tipo]
                    st.info(f"**{nuevo_tipo.title()}:** {tipo_info['description']}")
                    st.caption(f"Ejemplos: {', '.join(tipo_info['examples'])}")
                
                primer_valor = st.number_input(
                    "Valor Inicial",
                    value=0.5 if nuevo_tipo == 'porcentaje' else 100.0,
                    help=f"Primer valor del indicador (tipo: {nuevo_tipo})"
                )
                
                primera_fecha = st.date_input(
                    "Fecha Inicial",
                    help="Fecha del primer registro"
                )
            
            submitted = st.form_submit_button("Crear Indicador", use_container_width=True)
            
            if submitted:
                # Validaciones
                if not nuevo_codigo.strip():
                    st.error("El código es obligatorio")
                    return
                
                if not nuevo_indicador.strip():
                    st.error("El nombre del indicador es obligatorio")
                    return
                
                if not nueva_categoria.strip():
                    st.error("La categoría es obligatoria")
                    return
                
                # Verificar que el código no exista
                if not df.empty and nuevo_codigo in df['Codigo'].values:
                    st.error(f"El código '{nuevo_codigo}' ya existe")
                    return
                
                # Crear el nuevo registro en Google Sheets
                try:
                    from google_sheets_manager import GoogleSheetsManager
                    sheets_manager = GoogleSheetsManager()
                    
                    # Preparar datos para Google Sheets
                    data_dict = {
                        'LINEA DE ACCIÓN': nueva_linea.strip(),
                        'COMPONENTE PROPUESTO': nuevo_componente,
                        'CATEGORÍA': nueva_categoria.strip(),
                        'COD': nuevo_codigo.strip(),
                        'Nombre de indicador': nuevo_indicador.strip(),
                        'Valor': primer_valor,
                        'Fecha': primera_fecha.strftime('%d/%m/%Y'),
                        'Tipo': nuevo_tipo
                    }
                    
                    success = sheets_manager.add_record(data_dict)
                    
                    if success:
                        st.success(f"Indicador '{nuevo_codigo}' creado correctamente")
                        # Actualizar session state para seleccionar el nuevo código
                        st.session_state.selected_codigo_edit = nuevo_codigo
                        # Limpiar cache
                        st.cache_data.clear()
                        st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                        st.info("Los datos se actualizarán automáticamente")
                        
                        # Opción manual de actualización
                        if st.button("Actualizar datos ahora", key="refresh_after_create"):
                            st.rerun()
                    else:
                        st.error("Error al crear el indicador")
                        
                except Exception as e:
                    st.error(f"Error al crear indicador: {e}")
    
    @staticmethod
    def _render_add_form(df, codigo_editar):
        """Formulario para agregar nuevo registro a Google Sheets - ESTABLE"""
        st.subheader("Agregar Nuevo Registro")
        
        # Obtener tipo del indicador si existe
        if not df.empty:
            datos_indicador = df[df['Codigo'] == codigo_editar]
            if not datos_indicador.empty:
                tipo_indicador = datos_indicador.get('Tipo', pd.Series(['porcentaje'])).iloc[0]
                st.info(f"Tipo de indicador: **{tipo_indicador}**")
        
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
                    help="Valor según el tipo del indicador (se normalizará automáticamente)"
                )
            
            submitted = st.form_submit_button("Agregar", use_container_width=True)
            
            if submitted:
                # Verificar si ya existe un registro para esa fecha
                fecha_dt = pd.to_datetime(nueva_fecha)
                
                if not df.empty:
                    registro_existente = df[(df['Codigo'] == codigo_editar) & (df['Fecha'] == fecha_dt)]
                    
                    if not registro_existente.empty:
                        st.warning(f"Ya existe un registro para la fecha {nueva_fecha.strftime('%d/%m/%Y')}. Usa la pestaña 'Editar' para modificarlo.")
                        return
                
                # Agregar registro a Google Sheets
                success = DataEditor.add_new_record(df, codigo_editar, fecha_dt, nuevo_valor, None)
                
                if success:
                    st.success("Nuevo registro agregado correctamente")
                    st.info("Los datos se actualizarán automáticamente")
                    
                    # Limpiar cache
                    st.cache_data.clear()
                    st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                    
                    # Opción manual de actualización
                    if st.button("Ver cambios ahora", key="refresh_after_add"):
                        st.rerun()
                else:
                    st.error("Error al agregar el nuevo registro")
    
    @staticmethod
    def _render_edit_form(df, codigo_editar, registros_indicador):
        """Formulario para editar registro existente en Google Sheets - ESTABLE"""
        st.subheader("Editar Registro Existente")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para editar")
            return
        
        # Seleccionar registro a editar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a editar",
            fechas_disponibles,
            key="fecha_editar",
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
                    st.info(f"Fecha: {fecha_real.strftime('%d/%m/%Y')}")
                    st.info(f"Valor actual: {valor_actual:.3f}")
                
                with col2:
                    nuevo_valor = st.number_input(
                        "Nuevo Valor",
                        value=float(valor_actual),
                        help="Nuevo valor para este registro"
                    )
                
                submitted = st.form_submit_button("Actualizar", use_container_width=True)
                
                if submitted:
                    success = DataEditor.update_record(df, codigo_editar, fecha_real, nuevo_valor, None)
                    
                    if success:
                        st.success(f"Registro del {fecha_real.strftime('%d/%m/%Y')} actualizado correctamente")
                        st.balloons()
                        st.info("Los datos se actualizarán automáticamente")
                        
                        # Limpiar cache
                        st.cache_data.clear()
                        st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                        
                        # Opción manual de actualización
                        if st.button("Ver cambios ahora", key="refresh_after_edit"):
                            st.rerun()
                    else:
                        st.error("Error al actualizar el registro")
    
    @staticmethod
    def _render_delete_form(df, codigo_editar, registros_indicador):
        """Formulario para eliminar registro de Google Sheets - ESTABLE"""
        st.subheader("Eliminar Registro")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para eliminar")
            return
        
        # Seleccionar registro a eliminar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a eliminar",
            fechas_disponibles,
            key="fecha_eliminar",
            help="CUIDADO: Esta acción eliminará el registro y no se puede deshacer"
        )
        
        if fecha_seleccionada_str:
            # Obtener la fecha real
            idx_seleccionado = fechas_disponibles.index(fecha_seleccionada_str)
            fecha_real = registros_indicador.iloc[idx_seleccionado]['Fecha']
            valor_actual = registros_indicador.iloc[idx_seleccionado]['Valor']
            
            st.warning(f"""
            **ATENCIÓN**: Estás a punto de eliminar el registro:
            - **Fecha**: {fecha_real.strftime('%d/%m/%Y')}
            - **Valor**: {valor_actual:.3f}
            
            Esta acción **NO SE PUEDE DESHACER** y eliminará el registro permanentemente
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                confirmar = st.checkbox("Confirmo que quiero eliminar este registro", key="confirm_delete")
            
            with col2:
                if confirmar:
                    if st.button("ELIMINAR DE GOOGLE SHEETS", type="primary", use_container_width=True, key="delete_button"):
                        success = DataEditor.delete_record(df, codigo_editar, fecha_real, None)
                        
                        if success:
                            st.success(f"Registro del {fecha_real.strftime('%d/%m/%Y')} eliminado correctamente")
                            st.balloons()
                            st.info("Los datos se actualizarán automáticamente")
                            
                            # Limpiar cache
                            st.cache_data.clear()
                            st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                            
                            # Opción manual de actualización
                            if st.button("Ver cambios ahora", key="refresh_after_delete"):
                                st.rerun()
                        else:
                            st.error("Error al eliminar el registro")
    
    @staticmethod
    def _generate_and_download_pdf(codigo_editar, excel_data):
        """Generar y mostrar botón de descarga de PDF - SIMPLIFICADO"""
        try:
            from pdf_generator import PDFGenerator
            
            pdf_generator = PDFGenerator()
            
            if not pdf_generator.is_available():
                st.error("PDF no disponible. Instala: `pip install reportlab`")
                return
            
            with st.spinner("Generando ficha metodológica en PDF..."):
                pdf_bytes = pdf_generator.generate_metodological_sheet(codigo_editar, excel_data)
                
                if pdf_bytes and len(pdf_bytes) > 0:
                    st.success("PDF generado correctamente")
                    st.balloons()
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Ficha_Metodologica_{codigo_editar}_{timestamp}.pdf"
                    
                    st.download_button(
                        label="Descargar Ficha Metodológica PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_pdf_{codigo_editar}_{timestamp}",
                        use_container_width=True,
                        help=f"Descargar ficha metodológica de {codigo_editar}"
                    )
                else:
                    st.error("No se pudo generar el PDF. Verifica los datos metodológicos.")
                    
        except ImportError:
            st.error("Archivo pdf_generator.py no encontrado")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

class TabManager:
    """Gestor de pestañas del dashboard - SIN FILTROS DE FECHA"""
    
    def __init__(self, df, csv_path, excel_data=None):
        self.df = df
        self.csv_path = None  # No usamos CSV
        self.excel_data = excel_data
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar pestañas - SIN FILTROS DE FECHA"""
        
        # PESTAÑAS NATIVAS DE STREAMLIT - ESTABLES Y SIN FILTROS
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resumen General", 
            "Resumen por Componente", 
            "Evolución", 
            "Gestión de Datos"
        ])
        
        # ✅ PASAR DATOS SIN FILTROS A CADA PESTAÑA
        with tab1:
            GeneralSummaryTab.render(self.df)  # Sin filtros de fecha
        
        with tab2:
            ComponentSummaryTab.render(self.df)  # Sin filtros de fecha
        
        with tab3:
            EvolutionTab.render(self.df)  # Mantiene sus propios filtros de indicador
        
        with tab4:
            EditTab.render(self.df, None, self.excel_data)
        
        # Información de estado en sidebar - SIMPLIFICADA
        with st.sidebar:
            st.markdown("### Estado del Sistema")
            
            # Información de datos
            if not self.df.empty:
                st.success(f"**{len(self.df)}** registros cargados")
                st.success(f"**{self.df['Codigo'].nunique()}** indicadores únicos")
                
                # Mostrar información de tipos si existe la columna
                if 'Tipo' in self.df.columns:
                    tipos_count = self.df['Tipo'].value_counts()
                    st.info(f"**Tipos:** {dict(tipos_count)}")
                
                # Información de fechas
                if 'Fecha' in self.df.columns:
                    fechas_count = self.df['Fecha'].nunique()
                    fecha_min = self.df['Fecha'].min()
                    fecha_max = self.df['Fecha'].max()
                    st.info(f"**Fechas:** {fechas_count} diferentes")
                    st.info(f"**Rango:** {pd.to_datetime(fecha_min).strftime('%d/%m/%Y')} - {pd.to_datetime(fecha_max).strftime('%d/%m/%Y')}")
                
                # Información de componentes
                if 'Componente' in self.df.columns:
                    componentes_count = self.df['Componente'].nunique()
                    st.info(f"**Componentes:** {componentes_count}")
                    
                    # Lista de componentes
                    with st.expander("Ver componentes"):
                        componentes_list = sorted(self.df['Componente'].unique())
                        for comp in componentes_list:
                            count = len(self.df[self.df['Componente'] == comp])
                            st.write(f"• **{comp}:** {count} registros")
            else:
                st.warning("Google Sheets vacío")
            
            # Estado PDF - COMPLETO
            with st.expander("Estado PDF", expanded=False):
                try:
                    import reportlab
                    st.success("reportlab: Disponible")
                    reportlab_ok = True
                except ImportError:
                    st.error("reportlab: No instalado")
                    st.code("pip install reportlab")
                    reportlab_ok = False
                
                if self.excel_data is not None and not self.excel_data.empty:
                    st.success(f"Excel: {len(self.excel_data)} fichas")
                    excel_ok = True
                else:
                    st.warning("Excel: No disponible")
                    st.caption("Coloca 'Batería de indicadores.xlsx' en el directorio")
                    excel_ok = False
                
                if reportlab_ok and excel_ok:
                    st.success("**PDF completamente funcional**")
                elif reportlab_ok:
                    st.warning("**PDF parcial** (falta Excel)")
                elif excel_ok:
                    st.warning("**PDF parcial** (falta reportlab)")
                else:
                    st.error("**PDF no disponible**")
            
            # Estado Google Sheets - COMPLETO
            with st.expander("Estado Google Sheets", expanded=False):
                try:
                    from google_sheets_manager import GoogleSheetsManager
                    sheets_manager = GoogleSheetsManager()
                    connection_info = sheets_manager.get_connection_info()
                    
                    if connection_info.get('connected', False):
                        st.success("Conexión: Activa")
                        st.info(f"Hoja: {connection_info.get('worksheet_name', 'N/A')}")
                        if 'timeout' in connection_info:
                            st.info(f"Timeout: {connection_info['timeout']}s")
                    else:
                        st.error("Conexión: Inactiva")
                    
                    # Test de conexión
                    if st.button("🔧 Test Conexión", key="sidebar_test"):
                        success, message = sheets_manager.test_connection()
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                            
                except Exception as e:
                    st.error(f"Error: {e}")
            
            # Controles de actualización
            st.markdown("### Controles")
            
            if st.button("🔄 Actualizar Datos", key="sidebar_refresh", use_container_width=True):
                st.cache_data.clear()
                st.session_state.data_timestamp = time.time()
                st.rerun()
            
            if st.button("🧹 Limpiar Cache", key="sidebar_cache", use_container_width=True):
                st.cache_data.clear()
                st.session_state.clear()
                st.success("Cache limpiado")
                time.sleep(1)
                st.rerun()
