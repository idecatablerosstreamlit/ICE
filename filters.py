"""
Sistema de filtros para el Dashboard ICE - VERSIÓN ESTABLE
"""

import streamlit as st
import pandas as pd

class FilterManager:
    """Clase para manejar todos los filtros del dashboard"""
    
    def __init__(self, df):
        self.df = df
        self.filters = {}
    
    def create_sidebar_filters(self):
        """Crear filtros en la barra lateral"""
        st.sidebar.header("Filtros")
        
        # Filtro de fechas
        self._create_date_filter()
        
        # Filtro de componentes
        self._create_component_filter()
        
        # Filtro de categorías (dependiente del componente)
        self._create_category_filter()
        
        # Filtro de línea de acción
        self._create_action_line_filter()
        
        return self.filters
    
    def _create_date_filter(self):
        """Crear filtro de fechas"""
        try:
            fechas = sorted(self.df['Fecha'].unique())
            fecha_seleccionada = st.sidebar.selectbox(
                "Fecha", 
                fechas, 
                index=len(fechas) - 1
            )
            self.filters['fecha'] = fecha_seleccionada
        except Exception as e:
            st.sidebar.warning(f"No se encontraron fechas válidas: {e}")
            self.filters['fecha'] = None
    
    def _create_component_filter(self):
        """Crear filtro de componentes"""
        try:
            componentes = sorted(self.df['Componente'].unique())
            componente_seleccionado = st.sidebar.selectbox(
                "Componente", 
                ["Todos"] + list(componentes)
            )
            
            if componente_seleccionado == "Todos":
                self.filters['componente'] = None
            else:
                self.filters['componente'] = componente_seleccionado
        except Exception as e:
            st.sidebar.warning(f"Error al cargar componentes: {e}")
            self.filters['componente'] = None
    
    def _create_category_filter(self):
        """Crear filtro de categorías"""
        try:
            if self.filters.get('componente'):
                categorias = sorted(
                    self.df[self.df['Componente'] == self.filters['componente']]['Categoria'].unique()
                )
            else:
                categorias = sorted(self.df['Categoria'].unique())
            
            categoria_seleccionada = st.sidebar.selectbox(
                "Categoría", 
                ["Todas"] + list(categorias)
            )
            
            if categoria_seleccionada == "Todas":
                self.filters['categoria'] = None
            else:
                self.filters['categoria'] = categoria_seleccionada
        except Exception as e:
            st.sidebar.warning(f"Error al cargar categorías: {e}")
            self.filters['categoria'] = None
    
    def _create_action_line_filter(self):
        """Crear filtro de línea de acción"""
        try:
            # Filtrar líneas de acción basado en selecciones previas
            df_temp = self.df.copy()
            
            if self.filters.get('componente'):
                df_temp = df_temp[df_temp['Componente'] == self.filters['componente']]
            
            if self.filters.get('categoria'):
                df_temp = df_temp[df_temp['Categoria'] == self.filters['categoria']]
            
            # Filtrar valores NaN y vacíos antes de ordenar
            lineas_accion_series = df_temp['Linea_Accion'].dropna()
            lineas_accion_filtradas = lineas_accion_series[lineas_accion_series != ''].unique()
            
            # Convertir a lista y ordenar solo si hay elementos válidos
            if len(lineas_accion_filtradas) > 0:
                lineas_accion = sorted([str(x) for x in lineas_accion_filtradas if pd.notna(x)])
            else:
                lineas_accion = []
            
            linea_accion_seleccionada = st.sidebar.selectbox(
                "Línea de Acción", 
                ["Todas"] + list(lineas_accion)
            )
            
            if linea_accion_seleccionada == "Todas":
                self.filters['linea_accion'] = None
            else:
                self.filters['linea_accion'] = linea_accion_seleccionada
        except Exception as e:
            st.sidebar.warning(f"Error al cargar líneas de acción: {e}")
            self.filters['linea_accion'] = None
    
    def apply_filters(self, df):
        """Aplicar filtros al DataFrame"""
        df_filtrado = df.copy()
        
        if self.filters.get('fecha'):
            df_filtrado = df_filtrado[df_filtrado['Fecha'] == self.filters['fecha']]
        
        if self.filters.get('componente'):
            df_filtrado = df_filtrado[df_filtrado['Componente'] == self.filters['componente']]
        
        if self.filters.get('categoria'):
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == self.filters['categoria']]
        
        if self.filters.get('linea_accion'):
            # Manejo seguro de la comparación incluyendo valores NaN
            df_filtrado = df_filtrado[
                (df_filtrado['Linea_Accion'] == self.filters['linea_accion']) |
                (df_filtrado['Linea_Accion'].fillna('') == self.filters['linea_accion'])
            ]
        
        return df_filtrado
    
    def get_filter_info(self):
        """Obtener información de los filtros aplicados"""
        active_filters = []
        
        for key, value in self.filters.items():
            if value:
                active_filters.append(f"{key.title()}: {value}")
        
        return active_filters

class EvolutionFilters:
    """Filtros específicos para la pestaña de evolución - VERSIÓN ESTABLE"""
    
    @staticmethod
    def create_evolution_filters_stable(df):
        """Crear filtros para la pestaña de evolución SIN causar rerun"""
        st.markdown("### 🎛️ Configuración de Visualización")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Selección de Indicador**")
            
            try:
                # ✅ INICIALIZAR estado si no existe
                if 'evolution_selected_codigo' not in st.session_state:
                    st.session_state.evolution_selected_codigo = None
                if 'evolution_selected_indicador' not in st.session_state:
                    st.session_state.evolution_selected_indicador = None
                
                # Obtener códigos únicos disponibles
                if 'Codigo' in df.columns:
                    codigos_disponibles = sorted([c for c in df['Codigo'].dropna().unique() if str(c).strip()])
                else:
                    st.error("No se encontró la columna 'Codigo' en los datos")
                    return {'codigo': None, 'indicador': None, 'mostrar_meta': True, 'tipo_grafico': "Línea"}
                
                if not codigos_disponibles:
                    st.warning("No hay códigos de indicadores disponibles")
                    return {'codigo': None, 'indicador': None, 'mostrar_meta': True, 'tipo_grafico': "Línea"}
                
                # Crear opciones con información adicional
                opciones_display = ["🌍 Todos los indicadores (Vista General)"]
                codigo_map = {opciones_display[0]: None}
                
                for codigo in codigos_disponibles:
                    try:
                        indicador_info = df[df['Codigo'] == codigo].iloc[0]
                        nombre = indicador_info['Indicador'] if 'Indicador' in indicador_info else 'Sin nombre'
                        componente = indicador_info['Componente'] if 'Componente' in indicador_info else 'Sin componente'
                        
                        # Limitar longitud para mejor visualización
                        nombre_corto = nombre[:50] + "..." if len(nombre) > 50 else nombre
                        display_text = f"📈 {codigo} - {nombre_corto}"
                        
                        opciones_display.append(display_text)
                        codigo_map[display_text] = codigo
                        
                    except Exception as e:
                        st.warning(f"Error procesando código {codigo}: {e}")
                        continue
                
                # ✅ DETERMINAR índice actual basado en session_state
                index_actual = 0
                if st.session_state.evolution_selected_codigo:
                    for i, opcion in enumerate(opciones_display):
                        if codigo_map.get(opcion) == st.session_state.evolution_selected_codigo:
                            index_actual = i
                            break
                
                # ✅ Selector principal con KEY ÚNICO
                seleccion = st.selectbox(
                    "Indicador a analizar:",
                    opciones_display,
                    index=index_actual,
                    key="evolution_indicador_selector_stable",
                    help="Selecciona un indicador específico o la vista general"
                )
                
                codigo_seleccionado = codigo_map.get(seleccion)
                
                # ✅ ACTUALIZAR session_state
                st.session_state.evolution_selected_codigo = codigo_seleccionado
                
                # Obtener nombre del indicador si se seleccionó uno específico
                if codigo_seleccionado:
                    try:
                        indicador_data = df[df['Codigo'] == codigo_seleccionado].iloc[0]
                        indicador_seleccionado = indicador_data['Indicador']
                        st.session_state.evolution_selected_indicador = indicador_seleccionado
                        
                        # Mostrar información adicional del indicador seleccionado
                        st.info(f"""
                        **Componente:** {indicador_data.get('Componente', 'N/A')}  
                        **Categoría:** {indicador_data.get('Categoria', 'N/A')}
                        """)
                        
                    except Exception as e:
                        st.error(f"Error al obtener datos del indicador: {e}")
                        indicador_seleccionado = None
                        st.session_state.evolution_selected_indicador = None
                else:
                    indicador_seleccionado = None
                    st.session_state.evolution_selected_indicador = None
                    
            except Exception as e:
                st.error(f"Error crítico al crear filtros: {e}")
                import traceback
                st.code(traceback.format_exc())
                return {'codigo': None, 'indicador': None, 'mostrar_meta': True, 'tipo_grafico': "Línea"}
        
        with col2:
            st.markdown("**🎨 Opciones de Visualización**")
            
            # ✅ INICIALIZAR estado para opciones de visualización
            if 'evolution_mostrar_meta' not in st.session_state:
                st.session_state.evolution_mostrar_meta = True
            if 'evolution_tipo_grafico' not in st.session_state:
                st.session_state.evolution_tipo_grafico = "Línea"
            
            # Opción para mostrar línea de meta con KEY ÚNICO
            mostrar_meta = st.checkbox(
                "📏 Mostrar línea de referencia (Meta = 1.0)", 
                value=st.session_state.evolution_mostrar_meta,
                key="evolution_mostrar_meta_stable",
                help="Muestra una línea horizontal en 100% como referencia"
            )
            st.session_state.evolution_mostrar_meta = mostrar_meta
            
            # Seleccionar tipo de gráfico con KEY ÚNICO
            tipo_grafico = st.radio(
                "📊 Tipo de gráfico:",
                options=["Línea", "Barras"],
                index=0 if st.session_state.evolution_tipo_grafico == "Línea" else 1,
                horizontal=True,
                key="evolution_tipo_grafico_stable",
                help="Línea: mejor para ver tendencias / Barras: mejor para comparar valores puntuales"
            )
            st.session_state.evolution_tipo_grafico = tipo_grafico
            
            # Mostrar estadísticas si hay un indicador seleccionado
            if codigo_seleccionado:
                datos_indicador = df[df['Codigo'] == codigo_seleccionado]
                if not datos_indicador.empty:
                    st.markdown("**📊 Estadísticas:**")
                    st.write(f"• **Registros:** {len(datos_indicador)}")
                    st.write(f"• **Rango:** {datos_indicador['Valor'].min():.3f} - {datos_indicador['Valor'].max():.3f}")
                    st.write(f"• **Promedio:** {datos_indicador['Valor'].mean():.3f}")
        
        return {
            'codigo': codigo_seleccionado,
            'indicador': indicador_seleccionado,
            'mostrar_meta': mostrar_meta,
            'tipo_grafico': tipo_grafico
        }
    
    @staticmethod
    def create_evolution_filters(df):
        """Método de compatibilidad - redirige a la versión estable"""
        return EvolutionFilters.create_evolution_filters_stable(df)
