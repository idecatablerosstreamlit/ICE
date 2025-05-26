"""
Sistema de filtros para el Dashboard ICE
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
    """Filtros específicos para la pestaña de evolución"""
    
    @staticmethod
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

class PivotTableFilters:
    """Filtros para la tabla dinámica"""
    
    @staticmethod
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
