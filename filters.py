"""
Sistema de filtros para el Dashboard ICE - Versión corregida
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
        st.sidebar.header("🔍 Filtros")
        
        try:
            # Filtro de fechas
            self._create_date_filter()
            
            # Filtro de componentes
            self._create_component_filter()
            
            # Filtro de categorías (dependiente del componente)
            self._create_category_filter()
            
            # Filtro de línea de acción
            self._create_action_line_filter()
            
            return self.filters
            
        except Exception as e:
            st.sidebar.error(f"Error creando filtros: {e}")
            return {}
    
    def _create_date_filter(self):
        """Crear filtro de fechas"""
        try:
            if 'Fecha' in self.df.columns:
                fechas = sorted(self.df['Fecha'].dropna().unique())
                if len(fechas) > 0:
                    fecha_seleccionada = st.sidebar.selectbox(
                        "📅 Fecha", 
                        fechas, 
                        index=len(fechas) - 1,
                        format_func=lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else 'Sin fecha'
                    )
                    self.filters['fecha'] = fecha_seleccionada
                else:
                    st.sidebar.warning("No hay fechas válidas")
                    self.filters['fecha'] = None
            else:
                st.sidebar.warning("Columna 'Fecha' no encontrada")
                self.filters['fecha'] = None
        except Exception as e:
            st.sidebar.error(f"Error con filtro de fechas: {e}")
            self.filters['fecha'] = None
    
    def _create_component_filter(self):
        """Crear filtro de componentes"""
        try:
            if 'Componente' in self.df.columns:
                componentes = sorted(self.df['Componente'].dropna().unique())
                componente_seleccionado = st.sidebar.selectbox(
                    "🏗️ Componente", 
                    ["Todos"] + list(componentes)
                )
                
                if componente_seleccionado == "Todos":
                    self.filters['componente'] = None
                else:
                    self.filters['componente'] = componente_seleccionado
            else:
                st.sidebar.warning("Columna 'Componente' no encontrada")
                self.filters['componente'] = None
        except Exception as e:
            st.sidebar.error(f"Error con filtro de componentes: {e}")
            self.filters['componente'] = None
    
    def _create_category_filter(self):
        """Crear filtro de categorías"""
        try:
            if 'Categoria' in self.df.columns:
                if self.filters.get('componente'):
                    categorias = sorted(
                        self.df[self.df['Componente'] == self.filters['componente']]['Categoria'].dropna().unique()
                    )
                else:
                    categorias = sorted(self.df['Categoria'].dropna().unique())
                
                categoria_seleccionada = st.sidebar.selectbox(
                    "📂 Categoría", 
                    ["Todas"] + list(categorias)
                )
                
                if categoria_seleccionada == "Todas":
                    self.filters['categoria'] = None
                else:
                    self.filters['categoria'] = categoria_seleccionada
            else:
                st.sidebar.warning("Columna 'Categoria' no encontrada")
                self.filters['categoria'] = None
        except Exception as e:
            st.sidebar.error(f"Error con filtro de categorías: {e}")
            self.filters['categoria'] = None
    
    def _create_action_line_filter(self):
        """Crear filtro de línea de acción"""
        try:
            if 'Linea_Accion' in self.df.columns:
                # Filtrar líneas de acción basado en selecciones previas
                df_temp = self.df.copy()
                
                if self.filters.get('componente'):
                    df_temp = df_temp[df_temp['Componente'] == self.filters['componente']]
                
                if self.filters.get('categoria'):
                    df_temp = df_temp[df_temp['Categoria'] == self.filters['categoria']]
                
                lineas_accion = sorted(df_temp['Linea_Accion'].dropna().unique())
                
                linea_accion_seleccionada = st.sidebar.selectbox(
                    "📋 Línea de Acción", 
                    ["Todas"] + list(lineas_accion)
                )
                
                if linea_accion_seleccionada == "Todas":
                    self.filters['linea_accion'] = None
                else:
                    self.filters['linea_accion'] = linea_accion_seleccionada
            else:
                st.sidebar.warning("Columna 'Linea_Accion' no encontrada")
                self.filters['linea_accion'] = None
        except Exception as e:
            st.sidebar.error(f"Error con filtro de líneas de acción: {e}")
            self.filters['linea_accion'] = None
    
    def apply_filters(self, df):
        """Aplicar filtros al DataFrame"""
        try:
            df_filtrado = df.copy()
            
            if self.filters.get('fecha') is not None:
                df_filtrado = df_filtrado[df_filtrado['Fecha'] == self.filters['fecha']]
            
            if self.filters.get('componente'):
                df_filtrado = df_filtrado[df_filtrado['Componente'] == self.filters['componente']]
            
            if self.filters.get('categoria'):
                df_filtrado = df_filtrado[df_filtrado['Categoria'] == self.filters['categoria']]
            
            if self.filters.get('linea_accion'):
                df_filtrado = df_filtrado[df_filtrado['Linea_Accion'] == self.filters['linea_accion']]
            
            return df_filtrado
            
        except Exception as e:
            st.error(f"Error aplicando filtros: {e}")
            return df
    
    def get_filter_info(self):
        """Obtener información de los filtros aplicados"""
        active_filters = []
        
        try:
            for key, value in self.filters.items():
                if value:
                    if key == 'fecha' and pd.notna(value):
                        active_filters.append(f"📅 {key.title()}: {value.strftime('%d/%m/%Y')}")
                    elif value:
                        active_filters.append(f"🔍 {key.title()}: {value}")
        except Exception as e:
            st.sidebar.error(f"Error obteniendo info de filtros: {e}")
        
        return active_filters

class EvolutionFilters:
    """Filtros específicos para la pestaña de evolución"""
    
    @staticmethod
    def create_evolution_filters(df):
        """Crear filtros para la pestaña de evolución"""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Por código de indicador
                if 'Codigo' in df.columns:
                    codigos = sorted(df['Codigo'].dropna().unique())
                    codigo_seleccionado = st.selectbox(
                        "🎯 Código de Indicador", 
                        ["Todos"] + list(codigos)
                    )
                    
                    if codigo_seleccionado == "Todos":
                        codigo_seleccionado = None
                        indicador_seleccionado = None
                    else:
                        # Buscar el indicador correspondiente
                        indicador_data = df[df['Codigo'] == codigo_seleccionado]
                        if not indicador_data.empty and 'Indicador' in df.columns:
                            indicador_seleccionado = indicador_data['Indicador'].iloc[0]
                        else:
                            indicador_seleccionado = None
                else:
                    codigo_seleccionado = None
                    indicador_seleccionado = None
                    st.warning("Columna 'Codigo' no encontrada")
            
            with col2:
                # Opción para mostrar línea de meta
                mostrar_meta = st.checkbox("📊 Mostrar línea de referencia (Meta = 1.0)", value=True)
                
                # Seleccionar tipo de gráfico
                tipo_grafico = st.radio(
                    "📈 Tipo de gráfico",
                    options=["Línea", "Barras"],
                    horizontal=True
                )
            
            return {
                'codigo': codigo_seleccionado,
                'indicador': indicador_seleccionado,
                'mostrar_meta': mostrar_meta,
                'tipo_grafico': tipo_grafico
            }
            
        except Exception as e:
            st.error(f"Error creando filtros de evolución: {e}")
            return {
                'codigo': None,
                'indicador': None,
                'mostrar_meta': True,
                'tipo_grafico': "Línea"
            }

class PivotTableFilters:
    """Filtros para la tabla dinámica"""
    
    @staticmethod
    def create_pivot_filters():
        """Crear filtros para la tabla dinámica"""
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filas = st.selectbox(
                    "📊 Filas",
                    options=["Categoria", "Componente", "Linea_Accion", "Codigo"],
                    index=0
                )
            
            with col2:
                columnas = st.selectbox(
                    "📋 Columnas",
                    options=["Componente", "Categoria", "Linea_Accion", "Codigo"],
                    index=0
                )
            
            with col3:
                valores = st.selectbox(
                    "🎯 Valores",
                    options=["Valor", "Cumplimiento", "Puntaje_Ponderado"],
                    index=0
                )
            
            return {
                'filas': filas,
                'columnas': columnas,
                'valores': valores
            }
            
        except Exception as e:
            st.error(f"Error creando filtros de tabla dinámica: {e}")
            return {
                'filas': "Categoria",
                'columnas': "Componente", 
                'valores': "Valor"
            }
