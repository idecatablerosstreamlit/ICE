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

        return self.filters
    
    def _create_date_filter(self):
        """Crear filtro de fechas"""
        try:
            fechas = sorted(self.df['Fecha'].dropna().unique())
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
            componentes = sorted(self.df['Componente'].dropna().unique())
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
                    self.df[self.df['Componente'] == self.filters['componente']]['Categoria'].dropna().unique()
                )
            else:
                categorias = sorted(self.df['Categoria'].dropna().unique())
            
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
    
    def apply_filters(self, df):
        """Aplicar filtros al DataFrame"""
        df_filtrado = df.copy()
        
        if self.filters.get('fecha'):
            df_filtrado = df_filtrado[df_filtrado['Fecha'] == self.filters['fecha']]
        
        if self.filters.get('componente'):
            df_filtrado = df_filtrado[df_filtrado['Componente'] == self.filters['componente']]
        
        if self.filters.get('categoria'):
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == self.filters['categoria']]

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
        st.markdown("### Configuración de Visualización")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Selección de Indicador**")
            
            try:
                # ✅ INICIALIZAR estado si no existe
                if 'evolution_selected_codigo' not in st.session_state:
                    st.session_state.evolution_selected_codigo = None
                if 'evolution_selected_indicador' not in st.session_state:
                    st.session_state.evolution_selected_indicador = None
                
                # Obtener códigos únicos disponibles
                if 'COD' in df.columns:
                    codigos_disponibles = sorted([c for c in df['COD'].dropna().unique() if str(c).strip()])
                else:
                    st.error("No se encontró la columna 'COD' en los datos")
                    return {'codigo': None, 'indicador': None, 'mostrar_meta': True, 'tipo_grafico': "Línea"}
                
                if not codigos_disponibles:
                    st.warning("No hay códigos de indicadores disponibles")
                    return {'codigo': None, 'indicador': None, 'mostrar_meta': True, 'tipo_grafico': "Línea"}
                
                # Crear opciones con información adicional
                opciones_display = []
                codigo_map = {}

                for codigo in codigos_disponibles:
                    try:
                        indicador_info = df[df['COD'] == codigo].iloc[0]
                        nombre = indicador_info['Indicador'] if 'Indicador' in indicador_info else 'Sin nombre'
                        componente = indicador_info['Componente'] if 'Componente' in indicador_info else 'Sin componente'

                        # Celdas vacías llegan como NaN (float); usar texto por defecto
                        if pd.isna(nombre):
                            nombre = 'Sin nombre'
                        if pd.isna(componente):
                            componente = 'Sin componente'


                        # Limitar longitud para mejor visualización
                        nombre_corto = nombre[:50] + "..." if len(nombre) > 50 else nombre
                        display_text = f"{codigo} - {nombre_corto}"

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
                    help="Selecciona un indicador para ver su evolución histórica"
                )
                
                codigo_seleccionado = codigo_map.get(seleccion)
                
                # ✅ ACTUALIZAR session_state
                st.session_state.evolution_selected_codigo = codigo_seleccionado
                
                # Obtener nombre del indicador si se seleccionó uno específico
                if codigo_seleccionado:
                    try:
                        indicador_data = df[df['COD'] == codigo_seleccionado].iloc[0]
                        indicador_seleccionado = indicador_data['Indicador']
                        st.session_state.evolution_selected_indicador = indicador_seleccionado
                        
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
            st.markdown("**Opciones de Visualización**")
            
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
                datos_indicador = df[df['COD'] == codigo_seleccionado]
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
