"""
Utilidades para el manejo de datos del Dashboard ICE
"""

import pandas as pd
import os
import streamlit as st
from config import COLUMN_MAPPING, DEFAULT_META, CSV_SEPARATOR, CSV_FILENAME

class DataLoader:
    """Clase para cargar y procesar datos del CSV"""
    
    def __init__(self):
        self.df = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.script_dir, CSV_FILENAME)
    
    def load_data(self):
        """Cargar datos desde el archivo CSV"""
        try:
            # Cargar el archivo CSV con punto y coma como separador
            self.df = pd.read_csv(self.csv_path, sep=CSV_SEPARATOR)
            
            # Renombrar columnas
            self._rename_columns()
            
            # Procesar fechas y valores
            self._process_dates()
            self._process_values()
            
            # Añadir columnas por defecto
            self._add_default_columns()
            
            return self.df
            
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return None
    
    def _rename_columns(self):
        """Renombrar columnas según el mapeo"""
        for original, nuevo in COLUMN_MAPPING.items():
            if original in self.df.columns:
                self.df = self.df.rename(columns={original: nuevo})
    
    def _process_dates(self):
        """Procesar columna de fechas"""
        try:
            self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], format='%d/%m/%Y', errors='coerce')
        except:
            try:
                self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], errors='coerce')
            except Exception as e:
                st.warning(f"Error al convertir fechas: {e}")
    
    def _process_values(self):
        """Procesar valores numéricos"""
        if self.df['Valor'].dtype == 'object':
            self.df['Valor'] = self.df['Valor'].str.replace(',', '.').astype(float)
    
    def _add_default_columns(self):
        """Añadir columnas por defecto si no existen"""
        if 'Meta' not in self.df.columns:
            self.df['Meta'] = DEFAULT_META
        
        if 'Peso' not in self.df.columns:
            self.df['Peso'] = 100 / len(self.df['Indicador'].unique() if 'Indicador' in self.df.columns else self.df.index)

class DataProcessor:
    """Clase para procesar y calcular métricas de los datos"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes por componente y categoría"""
        if fecha_filtro:
            df_filtrado = df[df['Fecha'] == fecha_filtro]
        else:
            df_filtrado = df

        if len(df_filtrado) == 0:
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

        # Calcular cumplimiento
        if df_filtrado['Valor'].max() <= 1:
            df_filtrado['Cumplimiento'] = df_filtrado['Valor'] * 100
        else:
            df_filtrado['Cumplimiento'] = df_filtrado['Valor']

        df_filtrado['Cumplimiento'] = df_filtrado['Cumplimiento'].clip(upper=100)
        df_filtrado['Puntaje_Ponderado'] = df_filtrado['Cumplimiento'] * df_filtrado['Peso'] / 100

        # Agrupar por componente y categoría
        puntajes_componente = df_filtrado.groupby('Componente')['Puntaje_Ponderado'].sum().reset_index()
        puntajes_categoria = df_filtrado.groupby('Categoria')['Puntaje_Ponderado'].sum().reset_index()
        puntaje_general = df_filtrado['Puntaje_Ponderado'].sum()

        return puntajes_componente, puntajes_categoria, puntaje_general
    
    @staticmethod
    def create_pivot_table(df, fecha=None, filas='Categoria', columnas='Componente', valores='Valor'):
        """Crear tabla dinámica"""
        if fecha:
            df_filtrado = df[df['Fecha'] == fecha]
        else:
            ultima_fecha = df['Fecha'].max()
            df_filtrado = df[df['Fecha'] == ultima_fecha]

        if valores in ["Cumplimiento", "Puntaje_Ponderado"] and "Cumplimiento" not in df_filtrado.columns:
            if df_filtrado['Valor'].max() <= 1:
                df_filtrado['Cumplimiento'] = df_filtrado['Valor'] * 100
            else:
                df_filtrado['Cumplimiento'] = df_filtrado['Valor']
            
            df_filtrado['Puntaje_Ponderado'] = df_filtrado['Cumplimiento'] * df_filtrado['Peso'] / 100

        tabla = pd.pivot_table(
            df_filtrado,
            values=valores,
            index=[filas],
            columns=[columnas],
            aggfunc='mean',
            fill_value=0
        )

        return tabla

class DataEditor:
    """Clase para editar datos"""
    
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Guardar edición de un indicador"""
        try:
            idx = df[(df['Codigo'] == codigo) & (df['Fecha'] == fecha)].index

            if len(idx) > 0:
                df.loc[idx, 'Valor'] = nuevo_valor
                df.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                return True
            else:
                nueva_fila = df[df['Codigo'] == codigo].iloc[0].copy()
                nueva_fila['Fecha'] = fecha
                nueva_fila['Valor'] = nuevo_valor
                df_nuevo = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                return True
        except Exception as e:
            st.error(f"Error al guardar edición: {e}")
            return False
