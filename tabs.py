"""
Interfaces de usuario para las pestañas del Dashboard ICE - VERSIÓN CON FICHAS DESDE GOOGLE SHEETS
ACTUALIZACIÓN: Ya no usa Excel, ahora usa fichas desde la pestaña "Fichas" de Google Sheets
"""

import streamlit as st
import pandas as pd
import time
from charts import ChartGenerator, MetricsDisplay
from data_utils import DataProcessor, DataEditor
from filters import EvolutionFilters
from datetime import datetime

# Importar el sistema de autenticación
try:
    from auth import auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    # Crear un mock del auth_manager si no está disponible
    class MockAuthManager:
        def is_authenticated(self): return False
        def show_auth_status(self): st.info("🔒 Sistema de autenticación no disponible")
        def login_form(self): st.error("Sistema de autenticación no configurado")
        def require_auth_for_action(self, action): 
            st.error(f"Autenticación requerida para: {action}")
            return False
    
    auth_manager = MockAuthManager()
    AUTH_AVAILABLE = False

class GeneralSummaryTab:
    """Pestaña de resumen general"""
    
    @staticmethod
    def render(df, fecha_seleccionada=None):
        """Renderizar la pestaña de resumen general"""
        st.header("Resumen General")
        
        try:
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
                st.error(f"Faltan columnas esenciales: {missing_cols}")
                return
            
            datos_validos = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            if datos_validos.empty:
                st.info("Los datos están vacíos o incompletos")
                return
            
            # Obtener fecha de última actualización
            ultima_actualizacion = GeneralSummaryTab._get_last_update_info(df)
            
            # Calcular puntajes
            puntajes_componente, puntajes_categoria, puntaje_general = DataProcessor.calculate_scores(df)
            
            if puntajes_componente.empty and puntaje_general == 0:
                st.info("Agregando más datos podrás ver los puntajes y análisis")
                return
            
            st.info("**Puntajes calculados usando valores más recientes**")
            
            # Mostrar métricas generales
            MetricsDisplay.show_general_metrics(puntaje_general, puntajes_componente, ultima_actualizacion)
            
            # Layout con velocímetro y radar
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
                    st.error(f"Error en radar: {e}")
            
            # Puntajes por componente
            st.subheader("Puntajes por Componente")
            if not puntajes_componente.empty:
                try:
                    fig_comp = ChartGenerator.component_bar_chart(puntajes_componente)
                    st.plotly_chart(fig_comp, use_container_width=True)
                except Exception as e:
                    st.error(f"Error en gráfico: {e}")
                    st.dataframe(puntajes_componente, use_container_width=True)
            
            # Tabla de datos recientes
            with st.expander("Ver datos más recientes por indicador"):
                try:
                    df_latest = DataProcessor._get_latest_values_by_indicator(df)
                    if not df_latest.empty:
                        columns_to_show = ['Codigo', 'Indicador', 'Componente', 'Categoria', 'Valor', 'Tipo', 'Valor_Normalizado', 'Fecha']
                        available_columns = [col for col in columns_to_show if col in df_latest.columns]
                        st.dataframe(df_latest[available_columns], use_container_width=True)
                except Exception as e:
                    st.error(f"Error al mostrar datos: {e}")
        
        except Exception as e:
            st.error(f"Error en resumen general: {e}")
    
    @staticmethod
    def _get_last_update_info(df):
        """Obtener información de la última actualización"""
        try:
            if df.empty or 'Fecha' not in df.columns:
                return None
            
            fechas_validas = df['Fecha'].dropna()
            if fechas_validas.empty:
                return None
            
            if not pd.api.types.is_datetime64_any_dtype(fechas_validas):
                fechas_validas = pd.to_datetime(fechas_validas, errors='coerce').dropna()
            
            if fechas_validas.empty:
                return None
            
            ultima_fecha = fechas_validas.max()
            registro_mas_reciente = df[df['Fecha'] == ultima_fecha].iloc[0]
            
            return {
                'fecha': ultima_fecha,
                'indicador': registro_mas_reciente.get('Indicador', 'N/A'),
                'codigo': registro_mas_reciente.get('Codigo', 'N/A'),
                'componente': registro_mas_reciente.get('Componente', 'N/A')
            }
        except:
            return None

class ComponentSummaryTab:
    """Pestaña de resumen por componente"""
    
    @staticmethod
    def render(df, filters=None):
        """Renderizar resumen por componente"""
        st.header("Resumen por Componente")
        
        if df.empty:
            st.info("No hay datos disponibles")
            return
        
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        componentes = sorted(df_latest['Componente'].unique()) if not df_latest.empty else []
        
        if not componentes:
            st.info("No hay componentes disponibles")
            return
            
        componente_analisis = st.selectbox(
            "Seleccionar componente para análisis detallado", 
            componentes,
            key="comp_analysis_main"
        )
        
        df_componente = df_latest[df_latest['Componente'] == componente_analisis]
        
        if not df_componente.empty:
            st.info(f"**Análisis de {componente_analisis}:** Valores más recientes")
            
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
            
            # Gráficos
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                df_componente_historico = df[df['Componente'] == componente_analisis]
                fig_evol = ChartGenerator.evolution_chart(df_componente_historico, componente=componente_analisis)
                st.plotly_chart(fig_evol, use_container_width=True)
            
            with col_der:
                ComponentSummaryTab._render_category_visualization(df, componente_analisis)
            
            # Tabla de indicadores
            st.subheader(f"Indicadores de {componente_analisis}")
            columns_to_show = ['Indicador', 'Categoria', 'Valor', 'Tipo', 'Valor_Normalizado', 'Fecha']
            available_columns = [col for col in columns_to_show if col in df_componente.columns]
            
            st.dataframe(
                df_componente[available_columns].sort_values(
                    'Valor_Normalizado' if 'Valor_Normalizado' in df_componente.columns else 'Valor', 
                    ascending=False
                ),
                use_container_width=True
            )
    
    @staticmethod
    def _render_category_visualization(df, componente):
        """Renderizar visualización de categorías"""
        df_latest = DataProcessor._get_latest_values_by_indicator(df)
        df_componente = df_latest[df_latest['Componente'] == componente]
        
        num_categorias = df_componente['Categoria'].nunique()
        
        if num_categorias < 3:
            opciones = ["Barras Horizontales", "Radar (requiere 3+ categorías)"]
            default_viz = "Barras Horizontales"
        else:
            opciones = ["Barras Horizontales", "Radar de Categorías"]
            default_viz = "Radar de Categorías"
        
        tipo_viz = st.selectbox(
            f"Visualización ({num_categorias} categorías):",
            opciones,
            index=0 if "Barras" in default_viz else 1,
            key=f"viz_selector_{componente}"
        )
        
        if "Barras" in tipo_viz:
            fig_bar = ChartGenerator.horizontal_bar_chart(df, componente, None)
            st.plotly_chart(fig_bar, use_container_width=True)
        elif "Radar" in tipo_viz and num_categorias >= 3:
            fig_radar_cat = ChartGenerator.radar_chart_categories(df, componente, None)
            st.plotly_chart(fig_radar_cat, use_container_width=True)
        else:
            st.warning(f"Se requieren 3+ categorías para radar. {componente} tiene {num_categorias}.")

class EvolutionTab:
    """Pestaña de evolución"""
    
    @staticmethod
    def render(df, filters=None):
        """Renderizar evolución temporal"""
        st.header("Evolución Temporal de Indicadores")
        
        try:
            if df.empty:
                st.info("No hay datos para mostrar evolución")
                return
            
            st.info(f"**Datos:** {len(df)} registros de {df['Codigo'].nunique()} indicadores")
            
            # Crear filtros
            evolution_filters = EvolutionFilters.create_evolution_filters_stable(df)
            
            if evolution_filters['indicador']:
                st.success(f"**Indicador:** {evolution_filters['indicador']}")
                
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if not datos_indicador.empty:
                    st.write(f"**Registros históricos:** {len(datos_indicador)}")
                    
                    with st.expander("Ver datos históricos"):
                        columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
                        available_columns = [col for col in columns_to_show if col in datos_indicador.columns]
                        st.dataframe(datos_indicador[available_columns], use_container_width=True)
                else:
                    st.warning("No hay datos históricos")
                    return
            else:
                st.info("**Vista general:** Evolución promedio")
            
            # Generar gráfico
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
                st.error(f"Error en gráfico: {e}")
            
            # Análisis detallado si hay indicador seleccionado
            if evolution_filters['codigo'] and evolution_filters['indicador']:
                st.subheader(f"Análisis: {evolution_filters['indicador']}")
                
                datos_indicador = df[df['Codigo'] == evolution_filters['codigo']].sort_values('Fecha')
                
                if len(datos_indicador) > 1:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    valor_col = 'Valor_Normalizado' if 'Valor_Normalizado' in datos_indicador.columns else 'Valor'
                    
                    with col1:
                        valor_inicial = datos_indicador.iloc[0][valor_col]
                        st.metric("Valor Inicial", f"{valor_inicial:.3f}")
                    
                    with col2:
                        valor_actual = datos_indicador.iloc[-1][valor_col]
                        st.metric("Valor Actual", f"{valor_actual:.3f}")
                    
                    with col3:
                        cambio = valor_actual - valor_inicial
                        st.metric("Cambio Total", f"{cambio:+.3f}")
                    
                    with col4:
                        if valor_inicial != 0:
                            cambio_pct = (cambio / valor_inicial) * 100
                            st.metric("Cambio %", f"{cambio_pct:+.1f}%")
                
                # Tabla histórica
                columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
                available_columns = [col for col in columns_to_show if col in datos_indicador.columns]
                st.dataframe(datos_indicador[available_columns], use_container_width=True)
        
        except Exception as e:
            st.error(f"Error en evolución: {e}")

class EditTab:
    """Pestaña de gestión con autenticación - ACTUALIZADA PARA FICHAS DESDE GOOGLE SHEETS"""
    
    @staticmethod
    def render(df, csv_path, fichas_data=None):
        """Renderizar gestión de indicadores - ACTUALIZADO PARA FICHAS DESDE SHEETS"""
        st.header("Gestión de Indicadores")
        
        try:
            # Verificar Google Sheets
            from data_utils import GOOGLE_SHEETS_AVAILABLE
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("Google Sheets no disponible. Instala: `pip install gspread google-auth`")
                return
            
            # Mostrar estado de autenticación
            auth_manager.show_auth_status()
            
            # Inicializar session state
            if 'selected_codigo_edit' not in st.session_state:
                st.session_state.selected_codigo_edit = None
            
            # Selector de código
            codigo_editar = EditTab._render_codigo_selector(df)
            
            # MODO CONSULTA
            st.markdown("### 📖 Modo Consulta")
            
            if codigo_editar and codigo_editar != "CREAR_NUEVO":
                datos_indicador = df[df['Codigo'] == codigo_editar] if not df.empty else pd.DataFrame()
                
                if not datos_indicador.empty:
                    EditTab._render_indicator_info_card(datos_indicador, codigo_editar)
                    EditTab._render_metodological_expander(codigo_editar, fichas_data)
                    
                    registros_indicador = datos_indicador.sort_values('Fecha', ascending=False)
                    EditTab._render_view_records_public(registros_indicador)
                elif not df.empty:
                    st.error(f"No se encontraron datos para {codigo_editar}")
            
            # SEPARADOR
            st.markdown("---")
            
            # MODO ADMINISTRADOR
            st.markdown("### 🔐 Modo Administrador")
            
            if not auth_manager.is_authenticated():
                auth_manager.login_form()
                
                with st.expander("¿Qué puedes hacer como administrador?"):
                    st.markdown("""
                    **Con acceso de administrador podrás:**
                    - Crear nuevos indicadores
                    - Agregar registros a indicadores existentes  
                    - Editar valores de registros
                    - Eliminar registros (irreversible)
                    - Crear y editar fichas metodológicas
                    - Generar PDFs desde Google Sheets
                    
                    **Credenciales:** admin / qwerty
                    """)
            else:
                st.success("✅ Modo Administrador Activo")
                
                if codigo_editar == "CREAR_NUEVO":
                    EditTab._render_new_indicator_form_auth(df)
                elif codigo_editar and not df.empty:
                    datos_indicador = df[df['Codigo'] == codigo_editar]
                    if not datos_indicador.empty:
                        registros_indicador = datos_indicador.sort_values('Fecha', ascending=False)
                        EditTab._render_admin_management_tabs(df, codigo_editar, registros_indicador, fichas_data)
                    else:
                        st.warning("Selecciona un indicador válido")
                else:
                    st.info("Selecciona '[Crear nuevo código]' o elige un indicador existente")
        
        except Exception as e:
            st.error(f"Error en gestión: {e}")
    
    @staticmethod
    def _render_codigo_selector(df):
        """Selector de código"""
        if df.empty:
            st.info("Base de datos vacía")
            return "CREAR_NUEVO" if auth_manager.is_authenticated() else None
        
        codigos_disponibles = sorted(df['Codigo'].dropna().unique())
        
        if auth_manager.is_authenticated():
            opciones_codigo = ["[Crear nuevo código]"] + list(codigos_disponibles)
        else:
            opciones_codigo = list(codigos_disponibles)
        
        if not opciones_codigo:
            st.warning("No hay indicadores disponibles")
            return None
        
        index_actual = 0
        if st.session_state.selected_codigo_edit in codigos_disponibles:
            try:
                if auth_manager.is_authenticated():
                    index_actual = opciones_codigo.index(st.session_state.selected_codigo_edit)
                else:
                    index_actual = codigos_disponibles.index(st.session_state.selected_codigo_edit)
            except ValueError:
                index_actual = 0
        
        codigo_seleccionado = st.selectbox(
            "Seleccionar Indicador", 
            opciones_codigo,
            index=index_actual,
            key="codigo_consulta_selector"
        )
        
        if codigo_seleccionado == "[Crear nuevo código]":
            return "CREAR_NUEVO"
        else:
            st.session_state.selected_codigo_edit = codigo_seleccionado
            return codigo_seleccionado
    
    @staticmethod
    def _render_view_records_public(registros_indicador):
        """Ver registros - modo público"""
        st.subheader("📊 Registros del Indicador")
        if not registros_indicador.empty:
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Registros", len(registros_indicador))
            with col2:
                if 'Valor' in registros_indicador.columns:
                    valor_promedio = registros_indicador['Valor'].mean()
                    st.metric("Valor Promedio", f"{valor_promedio:.3f}")
            with col3:
                fecha_mas_reciente = registros_indicador['Fecha'].max()
                if pd.notna(fecha_mas_reciente):
                    fecha_str = pd.to_datetime(fecha_mas_reciente).strftime('%d/%m/%Y')
                    st.metric("Última Medición", fecha_str)
            
            # Tabla de datos
            columns_to_show = ['Fecha', 'Valor', 'Tipo', 'Valor_Normalizado', 'Componente', 'Categoria']
            available_columns = [col for col in columns_to_show if col in registros_indicador.columns]
            st.dataframe(registros_indicador[available_columns], use_container_width=True)
        else:
            st.info("No hay registros para este indicador")
    
    @staticmethod
    def _render_indicator_info_card(datos_indicador, codigo_editar):
        """Card con información del indicador"""
        try:
            nombre_indicador = datos_indicador['Indicador'].iloc[0]
            componente_indicador = datos_indicador['Componente'].iloc[0]
            categoria_indicador = datos_indicador['Categoria'].iloc[0]
            tipo_indicador = datos_indicador.get('Tipo', pd.Series(['porcentaje'])).iloc[0]
            
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
    def _render_metodological_expander(codigo_editar, fichas_data):
        """Información metodológica - ACTUALIZADA PARA USAR FICHAS DE GOOGLE SHEETS"""
        with st.expander("📋 Información Metodológica"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Ficha Metodológica")
                if fichas_data is not None and not fichas_data.empty:
                    indicador_metodologico = fichas_data[fichas_data['Codigo'] == codigo_editar]
                    
                    if not indicador_metodologico.empty:
                        metodologia = indicador_metodologico.iloc[0]
                        
                        def safe_get(campo, default='N/A'):
                            try:
                                valor = metodologia.get(campo, default)
                                if pd.isna(valor) or valor == '':
                                    return default
                                return str(valor).strip()
                            except:
                                return default
                        
                        st.write(f"**Nombre:** {safe_get('Nombre_Indicador')}")
                        st.write(f"**Área Temática:** {safe_get('Area_Tematica')}")
                        st.write(f"**Sector:** {safe_get('Sector')}")
                        st.write(f"**Entidad:** {safe_get('Entidad')}")
                        st.write("**Definición:**")
                        st.write(safe_get('Definicion'))
                        
                        # Mostrar más campos si están disponibles
                        objetivo = safe_get('Objetivo')
                        if objetivo != 'N/A':
                            st.write("**Objetivo:**")
                            st.write(objetivo)
                    else:
                        st.warning(f"No se encontró ficha metodológica para {codigo_editar} en Google Sheets")
                        
                        # Mostrar códigos disponibles
                        if 'Codigo' in fichas_data.columns:
                            codigos_disponibles = fichas_data['Codigo'].dropna().unique().tolist()
                            if codigos_disponibles:
                                st.info(f"💡 Códigos disponibles: {', '.join(map(str, codigos_disponibles[:5]))}")
                else:
                    st.warning("No hay datos de fichas disponibles. Verifica la pestaña 'Fichas' en Google Sheets.")
                    
                    # Opción para crear nueva ficha
                    if st.button("➕ Crear ficha metodológica", key=f"crear_ficha_{codigo_editar}"):
                        EditTab._render_create_ficha_form(codigo_editar)
            
            with col2:
                st.markdown("#### 📄 Generar PDF")
                EditTab._render_pdf_section(codigo_editar, fichas_data)
    
    @staticmethod
    def _render_create_ficha_form(codigo_editar):
        """Formulario para crear nueva ficha metodológica"""
        st.subheader(f"📋 Crear Ficha para {codigo_editar}")
        
        with st.form("form_crear_ficha"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_indicador = st.text_input("Nombre del Indicador", key="ficha_nombre")
                definicion = st.text_area("Definición", key="ficha_definicion")
                objetivo = st.text_area("Objetivo", key="ficha_objetivo")
                area_tematica = st.text_input("Área Temática", key="ficha_area")
                
            with col2:
                sector = st.text_input("Sector", key="ficha_sector")
                entidad = st.text_input("Entidad", key="ficha_entidad")
                dependencia = st.text_input("Dependencia", key="ficha_dependencia")
                tema = st.text_input("Tema", key="ficha_tema")
            
            submitted = st.form_submit_button("💾 Guardar Ficha")
            
            if submitted:
                # Crear ficha
                ficha_data = {
                    'Codigo': codigo_editar,
                    'Nombre_Indicador': nombre_indicador,
                    'Definicion': definicion,
                    'Objetivo': objetivo,
                    'Area_Tematica': area_tematica,
                    'Tema': tema,
                    'Sector': sector,
                    'Entidad': entidad,
                    'Dependencia': dependencia,
                    'Formula_Calculo': '',
                    'Variables': '',
                    'Unidad_Medida': '',
                    'Metodologia_Calculo': '',
                    'Tipo_Acumulacion': '',
                    'Fuente_Informacion': '',
                    'Tipo_Indicador': '',
                    'Periodicidad': '',
                    'Desagregacion_Geografica': '',
                    'Desagregacion_Poblacional': '',
                    'Clasificacion_Calidad': '',
                    'Clasificacion_Intervencion': '',
                    'Observaciones': '',
                    'Limitaciones': '',
                    'Interpretacion': '',
                    'Directivo_Responsable': '',
                    'Correo_Directivo': '',
                    'Telefono_Contacto': '',
                    'Enlaces_Web': '',
                    'Soporte_Legal': ''
                }
                
                try:
                    from data_utils import SheetsDataLoader
                    fichas_loader = SheetsDataLoader()
                    success = fichas_loader.add_ficha(ficha_data)
                    
                    if success:
                        st.success("✅ Ficha metodológica creada correctamente")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al crear la ficha")
                        
                except Exception as e:
                    st.error(f"❌ Error al guardar ficha: {e}")
    
    @staticmethod
    def _render_pdf_section(codigo_editar, fichas_data):
        """Sección de PDF - ACTUALIZADA PARA FICHAS DE GOOGLE SHEETS"""
        try:
            import reportlab
            reportlab_available = True
        except ImportError:
            reportlab_available = False
        
        if reportlab_available and fichas_data is not None and not fichas_data.empty:
            if codigo_editar in fichas_data['Codigo'].values:
                if st.button("📄 Generar PDF", key=f"generate_pdf_{codigo_editar}"):
                    EditTab._generate_and_download_pdf(codigo_editar, fichas_data)
            else:
                st.warning(f"No hay ficha metodológica para {codigo_editar} en Google Sheets")
                if st.button("➕ Crear ficha primero", key=f"crear_ficha_pdf_{codigo_editar}"):
                    EditTab._render_create_ficha_form(codigo_editar)
        elif not reportlab_available:
            st.error("Para PDFs instala: `pip install reportlab`")
        else:
            st.warning("No hay fichas metodológicas disponibles en Google Sheets")
            st.info("💡 Asegúrate de tener la pestaña 'Fichas' en tu Google Sheets")
    
    @staticmethod
    def _render_new_indicator_form_auth(df):
        """Formulario para crear nuevo indicador"""
        st.subheader("➕ Crear Nuevo Indicador")
        
        if not auth_manager.require_auth_for_action("Crear nuevo indicador"):
            return
        
        from config import INDICATOR_TYPES
        
        with st.form("form_nuevo_indicador_auth"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_codigo = st.text_input(
                    "Código del Indicador",
                    placeholder="Ej: D01-3",
                    help="Código único"
                )
                
                nuevo_indicador = st.text_input(
                    "Nombre del Indicador",
                    placeholder="Ej: Porcentaje de datos actualizados",
                    help="Nombre descriptivo"
                )
                
                nuevo_componente = st.selectbox(
                    "Componente",
                    ["Datos", "Seguridad e interoperabilidad", "Gobernanza y estratégia", 
                     "Herramientas técnicas y tecnológicas", "Aprovechamiento de datos"]
                )
                
                nuevo_tipo = st.selectbox(
                    "Tipo de Indicador",
                    list(INDICATOR_TYPES.keys())
                )
            
            with col2:
                nueva_categoria = st.text_input(
                    "Categoría",
                    placeholder="Ej: 01. Disponibilidad"
                )
                
                nueva_linea = st.text_input(
                    "Línea de Acción",
                    placeholder="Ej: LA.2.3."
                )
                
                if nuevo_tipo in INDICATOR_TYPES:
                    tipo_info = INDICATOR_TYPES[nuevo_tipo]
                    st.info(f"**{nuevo_tipo.title()}:** {tipo_info['description']}")
                
                primer_valor = st.number_input(
                    "Valor Inicial",
                    value=0.5 if nuevo_tipo == 'porcentaje' else 100.0
                )
                
                primera_fecha = st.date_input("Fecha Inicial")
            
            submitted = st.form_submit_button("✅ Crear Indicador", use_container_width=True)
            
            if submitted:
                if EditTab._validate_and_create_indicator(
                    df, nuevo_codigo, nuevo_indicador, nueva_categoria, nueva_linea,
                    nuevo_componente, nuevo_tipo, primer_valor, primera_fecha
                ):
                    st.success("✅ Indicador creado exitosamente")
                    time.sleep(1)
                    st.rerun()
    
    @staticmethod
    def _validate_and_create_indicator(df, codigo, indicador, categoria, linea, componente, tipo, valor, fecha):
        """Validar y crear indicador"""
        if not codigo.strip():
            st.error("El código es obligatorio")
            return False
        
        if not indicador.strip():
            st.error("El nombre es obligatorio")
            return False
        
        if not categoria.strip():
            st.error("La categoría es obligatoria")
            return False
        
        if not df.empty and codigo in df['Codigo'].values:
            st.error(f"El código '{codigo}' ya existe")
            return False
        
        try:
            from google_sheets_manager import GoogleSheetsManager
            sheets_manager = GoogleSheetsManager()
            
            data_dict = {
                'LINEA DE ACCIÓN': linea.strip(),
                'COMPONENTE PROPUESTO': componente,
                'CATEGORÍA': categoria.strip(),
                'COD': codigo.strip(),
                'Nombre de indicador': indicador.strip(),
                'Valor': valor,
                'Fecha': fecha.strftime('%d/%m/%Y'),
                'Tipo': tipo
            }
            
            success = sheets_manager.add_record(data_dict)
            
            if success:
                st.session_state.selected_codigo_edit = codigo
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                return True
            else:
                st.error("Error al crear el indicador")
                return False
                
        except Exception as e:
            st.error(f"Error al crear indicador: {e}")
            return False
    
    @staticmethod
    def _render_admin_management_tabs(df, codigo_editar, registros_indicador, fichas_data):
        """Pestañas de gestión para administradores - ACTUALIZADO PARA FICHAS SHEETS"""
        st.subheader("🛠️ Herramientas de Administración")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Vista Detallada",
            "➕ Agregar Registro", 
            "✏️ Editar Registro",
            "🗑️ Eliminar Registro"
        ])
        
        with tab1:
            EditTab._render_detailed_view(registros_indicador, fichas_data, codigo_editar)
        
        with tab2:
            EditTab._render_add_form_auth(df, codigo_editar)
        
        with tab3:
            EditTab._render_edit_form_auth(df, codigo_editar, registros_indicador)
        
        with tab4:
            EditTab._render_delete_form_auth(df, codigo_editar, registros_indicador)
    
    @staticmethod
    def _render_detailed_view(registros_indicador, fichas_data, codigo_editar):
        """Vista detallada para administradores - ACTUALIZADA PARA FICHAS SHEETS"""
        st.write("**Vista completa de registros con herramientas de análisis**")
        
        if not registros_indicador.empty:
            # Estadísticas avanzadas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Registros", len(registros_indicador))
            
            with col2:
                if 'Valor' in registros_indicador.columns:
                    valor_min = registros_indicador['Valor'].min()
                    valor_max = registros_indicador['Valor'].max()
                    st.metric("Rango", f"{valor_min:.2f} - {valor_max:.2f}")
            
            with col3:
                if 'Valor_Normalizado' in registros_indicador.columns:
                    norm_promedio = registros_indicador['Valor_Normalizado'].mean()
                    st.metric("Promedio Norm.", f"{norm_promedio:.3f}")
            
            with col4:
                if len(registros_indicador) > 1:
                    periodo_dias = (registros_indicador['Fecha'].max() - registros_indicador['Fecha'].min()).days
                    st.metric("Período (días)", periodo_dias)
                else:
                    st.metric("Período", "1 registro")
            
            # Tabla completa
            st.dataframe(registros_indicador, use_container_width=True)
            
            # Información metodológica expandida
            if fichas_data is not None and not fichas_data.empty:
                with st.expander("📋 Información Metodológica Completa"):
                    indicador_metodologico = fichas_data[fichas_data['Codigo'] == codigo_editar]
                    if not indicador_metodologico.empty:
                        metodologia = indicador_metodologico.iloc[0]
                        st.dataframe(metodologia.to_frame().T, use_container_width=True)
                    else:
                        st.info("No hay información metodológica para este código en Google Sheets")
                        if st.button("➕ Crear ficha metodológica", key=f"crear_ficha_detailed_{codigo_editar}"):
                            EditTab._render_create_ficha_form(codigo_editar)
            else:
                st.warning("⚠️ No hay fichas metodológicas disponibles en Google Sheets")
        else:
            st.info("No hay registros para mostrar")
    
    @staticmethod
    def _render_add_form_auth(df, codigo_editar):
        """Formulario para agregar registros"""
        st.write("**Agregar nuevo registro al indicador**")
        
        if not auth_manager.require_auth_for_action("Agregar registro"):
            return
        
        # Obtener tipo del indicador
        if not df.empty:
            datos_indicador = df[df['Codigo'] == codigo_editar]
            if not datos_indicador.empty:
                tipo_indicador = datos_indicador.get('Tipo', pd.Series(['porcentaje'])).iloc[0]
                st.info(f"**Tipo de indicador:** {tipo_indicador}")
        
        with st.form("form_agregar_auth"):
            col1, col2 = st.columns(2)
            
            with col1:
                nueva_fecha = st.date_input("Nueva Fecha")
            
            with col2:
                nuevo_valor = st.number_input("Nuevo Valor", value=0.5)
            
            submitted = st.form_submit_button("➕ Agregar Registro", use_container_width=True)
            
            if submitted:
                fecha_dt = pd.to_datetime(nueva_fecha)
                
                # Verificar duplicados
                if not df.empty:
                    registro_existente = df[(df['Codigo'] == codigo_editar) & (df['Fecha'] == fecha_dt)]
                    if not registro_existente.empty:
                        st.warning(f"Ya existe un registro para {nueva_fecha.strftime('%d/%m/%Y')}")
                        return
                
                # Agregar registro
                success = DataEditor.add_new_record(df, codigo_editar, fecha_dt, nuevo_valor, None)
                
                if success:
                    st.success("✅ Registro agregado correctamente")
                    st.cache_data.clear()
                    st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error al agregar el registro")
    
    @staticmethod
    def _render_edit_form_auth(df, codigo_editar, registros_indicador):
        """Formulario para editar registros - COMPLETAMENTE CORREGIDO"""
        st.write("**Modificar registro existente**")
        
        if not auth_manager.require_auth_for_action("Editar registro"):
            return
        
        if registros_indicador.empty:
            st.info("No hay registros para editar")
            return
        
        try:
            # FECHAS DISPONIBLES PARA EDITAR (variable única)
            fechas_edit_list = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
            
            fecha_edit_selected = st.selectbox(
                "Seleccionar registro a editar:",
                fechas_edit_list,
                key="edit_fecha_selector_unique",
                help="Elige el registro que quieres modificar"
            )
            
            if fecha_edit_selected:
                idx_edit = fechas_edit_list.index(fecha_edit_selected)
                fecha_edit_real = registros_indicador.iloc[idx_edit]['Fecha']
                valor_edit_actual = registros_indicador.iloc[idx_edit]['Valor']
                
                st.info(f"**Editando registro del {fecha_edit_real.strftime('%d/%m/%Y')}**")
                
                with st.form("form_editar_unico_auth"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Información actual:**")
                        st.write(f"📅 **Fecha:** {fecha_edit_real.strftime('%d/%m/%Y')}")
                        st.write(f"📊 **Valor actual:** {valor_edit_actual:.3f}")
                    
                    with col2:
                        st.markdown("**Nuevo valor:**")
                        nuevo_valor_edit = st.number_input(
                            "Nuevo Valor", 
                            value=float(valor_edit_actual),
                            help="Introduce el nuevo valor para este registro"
                        )
                    
                    submitted_edit_form = st.form_submit_button("✏️ Actualizar Registro", use_container_width=True)
                    
                    if submitted_edit_form:
                        if nuevo_valor_edit != valor_edit_actual:
                            success = DataEditor.update_record(df, codigo_editar, fecha_edit_real, nuevo_valor_edit, None)
                            
                            if success:
                                st.success(f"✅ Registro actualizado: {valor_edit_actual:.3f} → {nuevo_valor_edit:.3f}")
                                st.cache_data.clear()
                                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar el registro")
                        else:
                            st.warning("⚠️ El valor no ha cambiado")
        
        except Exception as e:
            st.error(f"Error en formulario de edición: {e}")
    
    @staticmethod
    def _render_delete_form_auth(df, codigo_editar, registros_indicador):
        """Formulario para eliminar registros - COMPLETAMENTE CORREGIDO"""
        st.write("**Eliminar registro permanentemente**")
        
        if not auth_manager.require_auth_for_action("Eliminar registro"):
            return
        
        if registros_indicador.empty:
            st.info("No hay registros para eliminar")
            return
        
        try:
            # FECHAS DISPONIBLES PARA ELIMINAR (variable única)
            fechas_delete_list = registros_indicador['Fecha'].dt.strftime('%d/%m/%Y (%A)').tolist()
            
            fecha_delete_selected = st.selectbox(
                "⚠️ Seleccionar registro a eliminar:",
                fechas_delete_list,
                key="delete_fecha_selector_unique",
                help="CUIDADO: Esta acción es irreversible"
            )
            
            if fecha_delete_selected:
                idx_delete = fechas_delete_list.index(fecha_delete_selected)
                fecha_delete_real = registros_indicador.iloc[idx_delete]['Fecha']
                valor_delete_actual = registros_indicador.iloc[idx_delete]['Valor']
                
                # ADVERTENCIA DE ELIMINACIÓN
                st.error(f"""
                🚨 **ATENCIÓN - ACCIÓN IRREVERSIBLE**
                
                Vas a eliminar permanentemente:
                - **📅 Fecha:** {fecha_delete_real.strftime('%d/%m/%Y')}
                - **📊 Valor:** {valor_delete_actual:.3f}
                - **🏷️ Indicador:** {codigo_editar}
                
                ⚠️ **Esta acción NO SE PUEDE DESHACER**
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    confirmar_delete_checkbox = st.checkbox(
                        "✅ Confirmo que quiero eliminar este registro",
                        key="confirm_delete_checkbox_unique",
                        help="Marca esta casilla para habilitar el botón de eliminación"
                    )
                
                with col2:
                    if confirmar_delete_checkbox:
                        if st.button(
                            "🗑️ ELIMINAR PERMANENTEMENTE",
                            type="primary",
                            use_container_width=True,
                            key="delete_button_final_unique"
                        ):
                            with st.spinner("Eliminando registro..."):
                                success = DataEditor.delete_record(df, codigo_editar, fecha_delete_real, None)
                                
                                if success:
                                    st.success("✅ Registro eliminado correctamente")
                                    st.cache_data.clear()
                                    st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar el registro")
                    else:
                        st.button(
                            "🔒 Confirma primero para eliminar",
                            disabled=True,
                            use_container_width=True
                        )
        
        except Exception as e:
            st.error(f"Error en formulario de eliminación: {e}")
    
    @staticmethod
    def _generate_and_download_pdf(codigo_editar, fichas_data):
        """Generar y descargar PDF - ACTUALIZADO PARA FICHAS DE GOOGLE SHEETS"""
        try:
            from pdf_generator import PDFGenerator
            
            pdf_generator = PDFGenerator()
            
            if not pdf_generator.is_available():
                st.error("PDF no disponible. Instala: `pip install reportlab`")
                return
            
            with st.spinner("Generando ficha metodológica desde Google Sheets..."):
                pdf_bytes = pdf_generator.generate_metodological_sheet(codigo_editar, fichas_data)
                
                if pdf_bytes and len(pdf_bytes) > 0:
                    st.success("✅ PDF generado correctamente desde Google Sheets")
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Ficha_Metodologica_{codigo_editar}_{timestamp}.pdf"
                    
                    st.download_button(
                        label="📄 Descargar Ficha Metodológica PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_pdf_{codigo_editar}_{timestamp}",
                        use_container_width=True
                    )
                else:
                    st.error("No se pudo generar el PDF")
                    
        except ImportError:
            st.error("Archivo pdf_generator.py no encontrado")
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

class TabManager:
    """Gestor de pestañas del dashboard - ACTUALIZADO PARA FICHAS DESDE GOOGLE SHEETS"""
    
    def __init__(self, df, csv_path, fichas_data=None):
        self.df = df
        self.csv_path = None
        self.fichas_data = fichas_data
    
    def render_tabs(self, df_filtrado, filters):
        """Renderizar todas las pestañas"""
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Resumen General", 
            "🏢 Resumen por Componente", 
            "📈 Evolución", 
            "⚙️ Gestión de Datos"
        ])
        
        with tab1:
            GeneralSummaryTab.render(self.df)
        
        with tab2:
            ComponentSummaryTab.render(self.df)
        
        with tab3:
            EvolutionTab.render(self.df)
        
        with tab4:
            EditTab.render(self.df, None, self.fichas_data)
        
        # Sidebar con información del sistema
        with st.sidebar:
            st.markdown("### 📊 Estado del Sistema")
            
            if not self.df.empty:
                st.success(f"**{len(self.df)}** registros cargados")
                st.success(f"**{self.df['Codigo'].nunique()}** indicadores únicos")
                
                if 'Tipo' in self.df.columns:
                    tipos_count = self.df['Tipo'].value_counts()
                    st.info(f"**Tipos:** {dict(tipos_count)}")
                
                if 'Fecha' in self.df.columns:
                    fechas_count = self.df['Fecha'].nunique()
                    fecha_min = self.df['Fecha'].min()
                    fecha_max = self.df['Fecha'].max()
                    st.info(f"**Fechas:** {fechas_count} diferentes")
                    st.info(f"**Rango:** {pd.to_datetime(fecha_min).strftime('%d/%m/%Y')} - {pd.to_datetime(fecha_max).strftime('%d/%m/%Y')}")
                
                if 'Componente' in self.df.columns:
                    componentes_count = self.df['Componente'].nunique()
                    st.info(f"**Componentes:** {componentes_count}")
                    
                    with st.expander("Ver componentes"):
                        componentes_list = sorted(self.df['Componente'].unique())
                        for comp in componentes_list:
                            count = len(self.df[self.df['Componente'] == comp])
                            st.write(f"• **{comp}:** {count} registros")
            else:
                st.warning("📋 Google Sheets vacío")
            
            # Estado de servicios - ACTUALIZADO PARA FICHAS
            with st.expander("🔧 Estado de Servicios", expanded=False):
                # PDF
                try:
                    import reportlab
                    st.success("📄 PDF: Disponible")
                    pdf_ok = True
                except ImportError:
                    st.error("📄 PDF: No instalado")
                    pdf_ok = False
                
                # Fichas metodológicas desde Google Sheets
                if self.fichas_data is not None and not self.fichas_data.empty:
                    st.success(f"📊 Fichas: {len(self.fichas_data)} disponibles")
                    fichas_ok = True
                elif self.fichas_data is not None and self.fichas_data.empty:
                    st.warning("📊 Fichas: Pestaña vacía")
                    fichas_ok = False
                else:
                    st.error("📊 Fichas: No disponibles")
                    fichas_ok = False
                
                # Google Sheets
                try:
                    from google_sheets_manager import GoogleSheetsManager
                    sheets_manager = GoogleSheetsManager()
                    connection_info = sheets_manager.get_connection_info()
                    
                    if connection_info.get('connected', False):
                        st.success("📝 Google Sheets: Conectado")
                        if connection_info.get('fichas_available', False):
                            st.success("📋 Pestaña 'Fichas': Disponible")
                        else:
                            st.warning("📋 Pestaña 'Fichas': No disponible")
                    else:
                        st.error("📝 Google Sheets: Desconectado")
                        
                except Exception:
                    st.error("📝 Google Sheets: Error")
            
            # Controles
            st.markdown("### 🎛️ Controles")
            
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
