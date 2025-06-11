# Botón para descargar PDF metodológico y ver ficha
            if excel_data is not None and not excel_data.empty:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col2:
                    if st.button("📋 Ver Ficha", key="view_sheet"):
                        # Buscar datos del indicador en Excel
                        indicador_metodologico = excel_data[excel_data['Codigo'] == codigo_editar]
                        
                        if not indicador_metodologico.empty:
                            st.subheader(f"📋 Ficha Metodológica: {codigo_editar}")
                            
                            metodologia = indicador_metodologico.iloc[0]
                            
                            # Mostrar información metodológica en pestañas
                            tab1, tab2, tab3 = st.tabs(["📊 Básica", "🔬 Metodología", "📞 Contacto"])
                            
                            with tab1:
                                st.write(f"**Nombre:** {metodologia.get('Nombre_Indicador', 'N/A')}")
                                st.write(f"**Definición:** {metodologia.get('Definicion', 'N/A')}")
                                st.write(f"**Objetivo:** {metodologia.get('Objetivo', 'N/A')}")
                                st.write(f"**Área Temática:** {metodologia.get('Area_Tematica', 'N/A')}")
                                st.write(f"**Sector:** {metodologia.get('Sector', 'N/A')}")
                                st.write(f"**Entidad:** {metodologia.get('Entidad', 'N/A')}")
                            
                            with tab2:
                                st.write(f"**Fórmula:** {metodologia.get('Formula_Calculo', 'N/A')}")
                                st.write(f"**Variables:** {metodologia.get('Variables', 'N/A')}")
                                st.write(f"**Unidad de medida:** {metodologia.get('Unidad_Medida', 'N/A')}")
                                st.write(f"**Periodicidad:** {metodologia.get('Periodicidad', 'N/A')}")
                                st.write(f"**Fuente:** {metodologia.get('Fuente_Informacion', 'N/A')}")
                                st.write(f"**Tipo:** {metodologia.get('Tipo_Indicador', 'N/A')}")
                            
                            with tab3:
                                st.write(f"**Directivo Responsable:** {metodologia.get('Directivo_Responsable', 'N/A')}")
                                st.write(f"**Correo:** {metodologia.get('Correo_Directivo', 'N/A')}")
                                st.write(f"**Teléfono:** {metodologia.get('Telefono_Contacto', 'N/A')}")
                                if metodologia.get('Enlaces_Web'):
                                    st.write(f"**Enlaces:** {metodologia.get('Enlaces_Web', 'N/A')}")
                        else:
                            st.warning(f"No se encontró información metodológica para {codigo_editar}")
                
                with col3:
                    if st.button("📄 PDF", key="download_pdf"):
                        try:
                            from pdf_generator import PDFGenerator
                            pdf_generator = PDFGenerator()
                            
                            if not pdf_generator.is_available():
                                st.error("📦 **Instalar reportlab:** `pip install reportlab`")
                            else:
                                pdf_bytes = pdf_generator.generate_metodological_sheet(codigo_editar, excel_data)
                                
                                if pdf_bytes and len(pdf_bytes) > 0:
                                    st.download_button(
                                        label="📄 Descargar PDF",
                                        data=pdf_bytes,
                                        file_name=f"Hoja_Metodologica_{codigo_editar}.pdf",
                                        mime="application/pdf",
                                        key="download_pdf_button"
                                    )
                                    st.success("✅ PDF generado correctamente")
                                else:
                                    st.error("❌ Error: No se pudo generar el PDF")
                        except ImportError:
                            st.error("❌ Módulo PDF Generator no disponible. Instalar: `pip install reportlab`")
                        except Exception as e:
                            st.error(f"❌ Error al generar PDF: {e}")
                            import traceback
                            with st.expander("🔧 Detalles del error"):
                                st.code(traceback.format_exc())
            else:
                st.info("💡 Para habilitar fichas metodológicas, verifica que el archivo 'Batería de indicadores.xlsx' esté en el directorio.")"""
Interfaces de usuario para las pestañas del Dashboard ICE - SOLO GOOGLE SHEETS
"""

import streamlit as st
import pandas as pd
import time
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor
from filters import EvolutionFilters

class GeneralSummaryTab:
    """Pestaña de resumen general"""
    
    @staticmethod
    def render(df, fecha_seleccionada):
        """Renderizar la pestaña de resumen general"""
        st.header("Resumen General")
        
        try:
            # Verificación previa de datos
            if df.empty:
                st.info("📋 Google Sheets está vacío. Puedes agregar datos en la pestaña 'Gestión de Datos'")
                st.markdown("""
                ### 🚀 Primeros pasos:
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
                st.error(f"❌ Faltan columnas esenciales en Google Sheets: {missing_cols}")
                st.write("**Columnas disponibles:**", list(df.columns))
                return
            
            # Verificar que hay datos válidos
            datos_validos = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            if datos_validos.empty:
                st.info("📋 Los datos en Google Sheets están vacíos o incompletos")
                return
            
            # Intentar cálculo de puntajes
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(df)
            
            # Verificar que los cálculos fueron exitosos
            if puntajes_componente.empty and puntajes_categoria.empty and puntaje_general == 0:
                st.info("📊 Agregando más datos podrás ver los puntajes y análisis")
                return
            
            # Mostrar información sobre qué datos se están usando
            st.info("""
            📊 **Cálculos basados en valores más recientes desde Google Sheets:** Los puntajes se calculan 
            usando el valor más reciente de cada indicador, asegurando consistencia.
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
                # Gráfico de radar (más grande)
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
                st.info("Agrega más datos a Google Sheets para ver puntajes por componente")
            
        except Exception as e:
            st.error(f"❌ Error al calcular puntajes desde Google Sheets: {e}")
            import traceback
            with st.expander("🔧 Detalles del error"):
                st.code(traceback.format_exc())
        
        # Mostrar tabla de datos más recientes
        with st.expander("📋 Ver datos más recientes por indicador (desde Google Sheets)"):
            try:
                df_latest = DataProcessor._get_latest_values_by_indicator(df)
                if not df_latest.empty:
                    st.dataframe(df_latest[['Codigo', 'Indicador', 'Componente', 'Categoria', 'Valor', 'Fecha']], use_container_width=True)
                else:
                    st.info("No hay datos para mostrar")
            except Exception as e:
                st.error(f"Error al mostrar datos: {e}")

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de resumen por componente"""
        st.header("Resumen por Componente")
        
        if df.empty:
            st.info("📋 No hay datos disponibles en Google Sheets para análisis por componente")
            return
        
        # Selector de componente específico para esta vista
        componentes = sorted(df['Componente'].unique())
        if not componentes:
            st.info("📋 No hay componentes disponibles en Google Sheets")
            return
            
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
            de cada indicador de este componente desde Google Sheets.
            """)
            
            # Métricas del componente
            col1, col2, col3 = st.columns(3)
            
            with col1:
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
            
            # Tabla de categorías
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
                # Gráfico de radar por categorías
                fig_radar_cat = ChartGenerator.radar_chart_categories(
                    df, componente_analisis, None
                )
                st.plotly_chart(fig_radar_cat, use_container_width=True)
            
            # Tabla de indicadores del componente
            st.subheader(f"Indicadores Más Recientes de {componente_analisis}")
            st.dataframe(
                df_componente[['Indicador', 'Categoria', 'Valor', 'Fecha']].sort_values('Valor', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("No hay datos para el componente seleccionado en Google Sheets")

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters):
        """Renderizar la pestaña de evolución"""
        st.subheader("📈 Evolución Temporal de Indicadores")
        
        try:
            if df.empty:
                st.info("📋 No hay datos disponibles en Google Sheets para mostrar evolución")
                return
            
            # Información sobre los datos disponibles
            st.info(f"""
            📊 **Datos desde Google Sheets:** {len(df)} registros de {df['Codigo'].nunique()} indicadores únicos
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
                    st.warning("No se encontraron datos históricos para este indicador en Google Sheets")
                    return
            else:
                st.info("**📊 Vista general:** Mostrando evolución promedio de todos los indicadores")
            
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

class EditTab:
    """Pestaña de edición - SOLO GOOGLE SHEETS"""
    
    @staticmethod
    def render(df, csv_path, excel_data=None):
        """Renderizar la pestaña de edición con Google Sheets"""
        st.subheader("Gestión de Indicadores (Google Sheets)")
        
        try:
            # Verificar que Google Sheets esté disponible
            from data_utils import GOOGLE_SHEETS_AVAILABLE
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ **Google Sheets no disponible.** Instala las dependencias: `pip install gspread google-auth`")
                return
            
            # Inicializar session state para preservar selecciones
            if 'selected_codigo' not in st.session_state:
                st.session_state.selected_codigo = None
            if 'last_action' not in st.session_state:
                st.session_state.last_action = None
            
            # Obtener códigos disponibles
            if df.empty:
                st.info("📋 Google Sheets está vacío. Puedes crear un nuevo indicador.")
                codigos_disponibles = []
            else:
                codigos_disponibles = sorted(df['Codigo'].dropna().unique())
            
            # Agregar opción para crear nuevo código
            opciones_codigo = ["➕ Crear nuevo código"] + list(codigos_disponibles)
            
            # Seleccionar código (mantener selección si es posible)
            index_actual = 0
            if st.session_state.selected_codigo and st.session_state.selected_codigo in codigos_disponibles:
                try:
                    index_actual = opciones_codigo.index(st.session_state.selected_codigo)
                except ValueError:
                    index_actual = 0
            
            codigo_editar = st.selectbox(
                "Seleccionar Código de Indicador", 
                opciones_codigo,
                index=index_actual,
                key="codigo_editar",
                help="Los datos se guardan automáticamente en Google Sheets"
            )
            
            # Actualizar session state
            if codigo_editar != "➕ Crear nuevo código":
                st.session_state.selected_codigo = codigo_editar
            
            # Manejar creación de nuevo código
            if codigo_editar == "➕ Crear nuevo código":
                EditTab._render_new_indicator_form(df)
                return
            
            # Validar que el código seleccionado existe en los datos
            datos_indicador = df[df['Codigo'] == codigo_editar] if not df.empty else pd.DataFrame()
            
            if datos_indicador.empty and not df.empty:
                st.error(f"No se encontraron datos para el código {codigo_editar} en Google Sheets")
                return
            elif not df.empty:
                # Mostrar información del indicador
                try:
                    nombre_indicador = datos_indicador['Indicador'].iloc[0]
                    componente_indicador = datos_indicador['Componente'].iloc[0]
                    categoria_indicador = datos_indicador['Categoria'].iloc[0]
                    
                    st.markdown(f"""
                    **Indicador seleccionado:** {nombre_indicador}  
                    **Componente:** {componente_indicador}  
                    **Categoría:** {categoria_indicador}  
                    📊 **Fuente:** Google Sheets
                    """)
                    
                except IndexError:
                    st.error(f"Error al obtener información del indicador {codigo_editar}")
                    return
            
            # Botón para descargar PDF metodológico
            if excel_data is not None and not excel_data.empty:
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("📄 Descargar PDF Metodológico", key="download_pdf"):
                        try:
                            from pdf_generator import PDFGenerator
                            pdf_generator = PDFGenerator()
                            pdf_bytes = pdf_generator.generate_metodological_sheet(codigo_editar, excel_data)
                            
                            if pdf_bytes and pdf_bytes.startswith(b'%PDF'):
                                st.download_button(
                                    label="📄 Descargar PDF",
                                    data=pdf_bytes,
                                    file_name=f"Hoja_Metodologica_{codigo_editar}.pdf",
                                    mime="application/pdf",
                                    key="download_pdf_button"
                                )
                            else:
                                st.error("Error: No se pudo generar el PDF")
                        except ImportError:
                            st.error("Módulo PDF Generator no disponible")
                        except Exception as e:
                            st.error(f"Error al generar PDF: {e}")
            else:
                st.info("💡 Para habilitar la descarga en PDF, coloca el archivo Excel en el directorio.")
            
            # Obtener registros existentes del indicador
            if not df.empty and not datos_indicador.empty:
                registros_indicador = datos_indicador.sort_values('Fecha', ascending=False)
            else:
                registros_indicador = pd.DataFrame()
            
            # Crear pestañas para diferentes acciones
            tab_ver, tab_agregar, tab_editar, tab_eliminar = st.tabs([
                "📋 Ver Registros", 
                "➕ Agregar Nuevo", 
                "✏️ Editar Existente", 
                "🗑️ Eliminar Registro"
            ])
            
            with tab_ver:
                st.subheader("Registros Existentes en Google Sheets")
                if not registros_indicador.empty:
                    st.dataframe(
                        registros_indicador[['Fecha', 'Valor', 'Componente', 'Categoria']], 
                        use_container_width=True
                    )
                else:
                    st.info("No hay registros para este indicador en Google Sheets")
            
            with tab_agregar:
                EditTab._render_add_form(df, codigo_editar)
            
            with tab_editar:
                EditTab._render_edit_form(df, codigo_editar, registros_indicador)
            
            with tab_eliminar:
                EditTab._render_delete_form(df, codigo_editar, registros_indicador)
        
        except Exception as e:
            st.error(f"Error en la gestión de indicadores: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    @staticmethod
    def _render_new_indicator_form(df):
        """Formulario para crear nuevo indicador en Google Sheets"""
        st.subheader("Crear Nuevo Indicador en Google Sheets")
        
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
                
                primer_valor = st.number_input(
                    "Valor Inicial",
                    value=0.5,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    help="Primer valor del indicador"
                )
                
                primera_fecha = st.date_input(
                    "Fecha Inicial",
                    help="Fecha del primer registro"
                )
            
            submitted = st.form_submit_button("➕ Crear Indicador en Google Sheets", use_container_width=True)
            
            if submitted:
                # Validaciones
                if not nuevo_codigo.strip():
                    st.error("❌ El código es obligatorio")
                    return
                
                if not nuevo_indicador.strip():
                    st.error("❌ El nombre del indicador es obligatorio")
                    return
                
                if not nueva_categoria.strip():
                    st.error("❌ La categoría es obligatoria")
                    return
                
                # Verificar que el código no exista
                if not df.empty and nuevo_codigo in df['Codigo'].values:
                    st.error(f"❌ El código '{nuevo_codigo}' ya existe en Google Sheets")
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
                        'Fecha': primera_fecha.strftime('%d/%m/%Y')
                    }
                    
                    success = sheets_manager.add_record(data_dict)
                    
                    if success:
                        st.success(f"✅ Indicador '{nuevo_codigo}' creado correctamente en Google Sheets")
                        # Actualizar session state para seleccionar el nuevo código
                        st.session_state.selected_codigo = nuevo_codigo
                        # Forzar recarga SIN cambiar pestaña
                        st.cache_data.clear()
                        st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                        # NO usar st.rerun() para evitar reseteo de pestaña
                        st.info("🔄 Los datos se actualizarán automáticamente desde Google Sheets en unos segundos")
                        
                        # Mostrar botón manual de actualización
                        if st.button("🔄 Actualizar ahora", key="refresh_after_create"):
                            st.rerun()
                    else:
                        st.error("❌ Error al crear el indicador en Google Sheets")
                        
                except Exception as e:
                    st.error(f"❌ Error al crear indicador en Google Sheets: {e}")
    
    @staticmethod
    def _render_add_form(df, codigo_editar):
        """Formulario para agregar nuevo registro a Google Sheets"""
        st.subheader("Agregar Nuevo Registro a Google Sheets")
        
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
            
            submitted = st.form_submit_button("➕ Agregar Registro a Google Sheets", use_container_width=True)
            
            if submitted:
                # Verificar si ya existe un registro para esa fecha
                fecha_dt = pd.to_datetime(nueva_fecha)
                
                if not df.empty:
                    registro_existente = df[(df['Codigo'] == codigo_editar) & (df['Fecha'] == fecha_dt)]
                    
                    if not registro_existente.empty:
                        st.warning(f"Ya existe un registro para la fecha {nueva_fecha.strftime('%d/%m/%Y')} en Google Sheets. Usa la pestaña 'Editar' para modificarlo.")
                        return
                
                # Agregar registro a Google Sheets
                success = DataEditor.add_new_record(df, codigo_editar, fecha_dt, nuevo_valor, None)
                
                if success:
                    st.success("✅ Nuevo registro agregado correctamente a Google Sheets")
                    # NO usar st.rerun() para evitar reseteo de pestaña
                    st.info("🔄 Los datos se actualizarán automáticamente en unos segundos")
                    
                    # Limpiar cache para próxima carga
                    st.cache_data.clear()
                    st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                    
                    # Botón manual de actualización
                    if st.button("🔄 Ver cambios ahora", key="refresh_after_add"):
                        st.rerun()
                else:
                    st.error("❌ Error al agregar el nuevo registro a Google Sheets")
    
    @staticmethod
    def _render_edit_form(df, codigo_editar, registros_indicador):
        """Formulario para editar registro existente en Google Sheets"""
        st.subheader("Editar Registro Existente en Google Sheets")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para editar en Google Sheets")
            return
        
        # Seleccionar registro a editar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a editar",
            fechas_disponibles,
            help="Selecciona el registro que deseas modificar en Google Sheets"
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
                        help="Nuevo valor para este registro en Google Sheets"
                    )
                
                submitted = st.form_submit_button("✏️ Actualizar Registro en Google Sheets", use_container_width=True)
                
                if submitted:
                    success = DataEditor.update_record(df, codigo_editar, fecha_real, nuevo_valor, None)
                    
                    if success:
                        st.success(f"✅ Registro del {fecha_real.strftime('%d/%m/%Y')} actualizado correctamente en Google Sheets")
                        st.balloons()
                        # NO usar st.rerun() para evitar reseteo de pestaña
                        st.info("🔄 Los datos se actualizarán automáticamente desde Google Sheets en unos segundos")
                        
                        # Limpiar cache para próxima carga
                        st.cache_data.clear()
                        st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                        
                        # Botón manual de actualización
                        if st.button("🔄 Ver cambios ahora", key="refresh_after_edit"):
                            st.rerun()
                    else:
                        st.error("❌ Error al actualizar el registro en Google Sheets")
    
    @staticmethod
    def _render_delete_form(df, codigo_editar, registros_indicador):
        """Formulario para eliminar registro de Google Sheets"""
        st.subheader("Eliminar Registro de Google Sheets")
        
        if registros_indicador.empty:
            st.info("No hay registros existentes para eliminar en Google Sheets")
            return
        
        # Seleccionar registro a eliminar
        fechas_disponibles = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
        fecha_seleccionada_str = st.selectbox(
            "Seleccionar fecha a eliminar",
            fechas_disponibles,
            help="⚠️ CUIDADO: Esta acción eliminará el registro de Google Sheets y no se puede deshacer"
        )
        
        if fecha_seleccionada_str:
            # Obtener la fecha real
            idx_seleccionado = fechas_disponibles.index(fecha_seleccionada_str)
            fecha_real = registros_indicador.iloc[idx_seleccionado]['Fecha']
            valor_actual = registros_indicador.iloc[idx_seleccionado]['Valor']
            
            st.warning(f"""
            ⚠️ **ATENCIÓN**: Estás a punto de eliminar el registro de Google Sheets:
            - **Fecha**: {fecha_real.strftime('%d/%m/%Y')}
            - **Valor**: {valor_actual:.3f}
            
            Esta acción **NO SE PUEDE DESHACER** y eliminará el registro permanentemente de Google Sheets.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                confirmar = st.checkbox("Confirmo que quiero eliminar este registro de Google Sheets", key="confirm_delete")
            
            with col2:
                if confirmar:
                    if st.button("🗑️ ELIMINAR REGISTRO DE GOOGLE SHEETS", type="primary", use_container_width=True):
                        success = DataEditor.delete_record(df, codigo_editar, fecha_real, None)
                        
                        if success:
                            st.success(f"✅ Registro del {fecha_real.strftime('%d/%m/%Y')} eliminado correctamente de Google Sheets")
                            st.balloons()
                            # NO usar st.rerun() para evitar reseteo de pestaña
                            st.info("🔄 Los datos se actualizarán automáticamente desde Google Sheets en unos segundos")
                            
                            # Limpiar cache para próxima carga
                            st.cache_data.clear()
                            st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                            
                            # Botón manual de actualización
                            if st.button("🔄 Ver cambios ahora", key="refresh_after_delete"):
                                st.rerun()
                        else:
                            st.error("❌ Error al eliminar el registro de Google Sheets")

class TabManager:
    """Gestor de pestañas del dashboard - SOLO GOOGLE SHEETS CON PERSISTENCIA"""
    
    def __init__(self, df, csv_path, excel_data=None):
        self.df = df
        self.csv_path = None  # No usamos CSV
        self.excel_data = excel_data
        
        # Inicializar pestaña activa en session_state
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = 0
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas manteniendo el estado activo"""
        
        # Nombres de las pestañas
        tab_names = [
            "📊 Resumen General", 
            "🏗️ Resumen por Componente", 
            "📈 Evolución", 
            "⚙️ Gestión de Datos"
        ]
        
        # Crear pestañas con índice persistente
        tabs = st.tabs(tab_names)
        
        # Detectar cambio de pestaña usando un callback
        # Usamos un selectbox oculto para mantener el estado
        with st.sidebar:
            with st.expander("🎛️ Navegación", expanded=False):
                current_tab = st.radio(
                    "Pestaña activa:",
                    options=range(len(tab_names)),
                    format_func=lambda x: tab_names[x],
                    index=st.session_state.active_tab,
                    key="tab_selector"
                )
                
                # Actualizar session state si cambió
                if current_tab != st.session_state.active_tab:
                    st.session_state.active_tab = current_tab
                    st.rerun()
        
        # Renderizar contenido de cada pestaña
        with tabs[0]:  # Resumen General
            if st.session_state.active_tab == 0 or True:  # Siempre renderizar para que funcione
                GeneralSummaryTab.render(df_filtrado, filters.get('fecha'))
        
        with tabs[1]:  # Resumen por Componente
            if st.session_state.active_tab == 1 or True:
                ComponentSummaryTab.render(df_filtrado, filters)
        
        with tabs[2]:  # Evolución
            if st.session_state.active_tab == 2 or True:
                EvolutionTab.render(self.df, filters)
        
        with tabs[3]:  # Gestión de Datos
            if st.session_state.active_tab == 3 or True:
                EditTab.render(self.df, None, self.excel_data)
        
        # Mostrar información de la pestaña activa
        st.sidebar.info(f"📍 **Pestaña activa:** {tab_names[st.session_state.active_tab]}")
        
        # Botón para resetear pestaña (útil para debugging)
        if st.sidebar.button("🔄 Resetear navegación"):
            st.session_state.active_tab = 0
            st.rerun()
