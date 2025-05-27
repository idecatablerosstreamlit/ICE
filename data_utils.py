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
            # Intentar conversión con formato específico
            self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], format='%d/%m/%Y', errors='coerce')
        except:
            try:
                # Intentar conversión automática
                self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], errors='coerce')
            except Exception as e:
                st.warning(f"Error al convertir fechas: {e}")
        
        # Filtrar filas con fechas NaT si existen
        if self.df['Fecha'].isna().any():
            filas_con_nat = self.df['Fecha'].isna().sum()
            st.warning(f"Se encontraron {filas_con_nat} filas con fechas inválidas que serán excluidas del análisis.")
            self.df = self.df.dropna(subset=['Fecha'])
    
    def _process_values(self):
        """Procesar valores numéricos"""
        if self.df['Valor'].dtype == 'object':
            self.df['Valor'] = self.df['Valor'].str.replace(',', '.').astype(float)
    
    def _add_default_columns(self):
        """Añadir columnas por defecto si no existen"""
        if 'Meta' not in self.df.columns:
            self.df['Meta'] = DEFAULT_META
        
        # Asignar peso igual a todos los indicadores (será normalizado por componente)
        if 'Peso' not in self.df.columns:
            self.df['Peso'] = 1.0

class DataProcessor:
    """Clase para procesar y calcular métricas de los datos"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes por componente y categoría usando promedio ponderado"""
        if fecha_filtro:
            df_filtrado = df[df['Fecha'] == fecha_filtro].copy()
        else:
            df_filtrado = df.copy()

        if len(df_filtrado) == 0:
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

        # Normalizar valores (0-1 o convertir a 0-100 si es necesario para visualización)
        df_filtrado['Valor_Normalizado'] = df_filtrado['Valor'].clip(0, 1)
        
        # Calcular puntajes por componente (promedio ponderado)
        puntajes_componente = DataProcessor._calculate_weighted_average_by_group(
            df_filtrado, 'Componente'
        )
        
        # Calcular puntajes por categoría (promedio ponderado)
        puntajes_categoria = DataProcessor._calculate_weighted_average_by_group(
            df_filtrado, 'Categoria'
        )
        
        # Calcular puntaje general (promedio ponderado de todos los indicadores)
        peso_total = df_filtrado['Peso'].sum()
        if peso_total > 0:
            puntaje_general = (df_filtrado['Valor_Normalizado'] * df_filtrado['Peso']).sum() / peso_total
        else:
            puntaje_general = df_filtrado['Valor_Normalizado'].mean()

        return puntajes_componente, puntajes_categoria, puntaje_general
    
    @staticmethod
    def _calculate_weighted_average_by_group(df, group_column):
        """Calcular promedio ponderado por grupo"""
        def weighted_avg(group):
            valores = group['Valor_Normalizado']
            pesos = group['Peso']
            peso_total = pesos.sum()
            
            if peso_total > 0:
                return (valores * pesos).sum() / peso_total
            else:
                return valores.mean()
        
        # Calcular promedio ponderado por grupo
        puntajes = df.groupby(group_column).apply(weighted_avg).reset_index()
        puntajes.columns = [group_column, 'Puntaje_Ponderado']
        
        return puntajes
    
    @staticmethod
    def create_pivot_table(df, fecha=None, filas='Categoria', columnas='Componente', valores='Valor'):
        """Crear tabla dinámica"""
        if fecha:
            df_filtrado = df[df['Fecha'] == fecha].copy()
        else:
            ultima_fecha = df['Fecha'].max()
            df_filtrado = df[df['Fecha'] == ultima_fecha].copy()

        # Calcular columnas adicionales si es necesario
        if valores in ["Cumplimiento", "Puntaje_Ponderado"]:
            df_filtrado['Valor_Normalizado'] = df_filtrado['Valor'].clip(0, 1)
            
            if valores == "Cumplimiento":
                df_filtrado['Cumplimiento'] = df_filtrado['Valor_Normalizado'] * 100
            elif valores == "Puntaje_Ponderado":
                # Para la tabla pivote, usamos el valor ponderado individual
                df_filtrado['Puntaje_Ponderado'] = df_filtrado['Valor_Normalizado'] * df_filtrado.get('Peso', 1.0)

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
    """Clase para editar datos con operaciones CRUD completas"""
    
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Guardar edición de un indicador (función heredada para compatibilidad)"""
        return DataEditor.update_record(df, codigo, fecha, nuevo_valor, csv_path)
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path):
        """Agregar un nuevo registro para un indicador"""
        try:
            # Obtener información base del indicador
            indicador_base = df[df['Codigo'] == codigo].iloc[0]
            
            # Crear nueva fila
            nueva_fila = {
                'Linea_Accion': indicador_base['Linea_Accion'],
                'Componente': indicador_base['Componente'],
                'Categoria': indicador_base['Categoria'],
                'Codigo': codigo,
                'Indicador': indicador_base['Indicador'],
                'Valor': valor,
                'Fecha': fecha,
                'Meta': indicador_base.get('Meta', 1.0),
                'Peso': indicador_base.get('Peso', 1.0)
            }
            
            # Agregar al DataFrame
            df_nuevo = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            
            # Guardar al CSV
            df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
            return True
            
        except Exception as e:
            st.error(f"Error al agregar nuevo registro: {e}")
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path):
        """Actualizar un registro existente"""
        try:
            # Encontrar el índice del registro a actualizar
            idx = df[(df['Codigo'] == codigo) & (df['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                # Actualizar el valor
                df.loc[idx, 'Valor'] = nuevo_valor
                # Guardar al CSV
                df.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                return True
            else:
                st.error(f"No se encontró un registro para la fecha {fecha.strftime('%d/%m/%Y')}")
                return False
                
        except Exception as e:
            st.error(f"Error al actualizar el registro: {e}")
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path):
        """Eliminar un registro existente"""
        try:
            # Encontrar el índice del registro a eliminar
            idx = df[(df['Codigo'] == codigo) & (df['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                # Eliminar la fila
                df_nuevo = df.drop(idx).reset_index(drop=True)
                # Guardar al CSV
                df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                return True
            else:
                st.error(f"No se encontró un registro para la fecha {fecha.strftime('%d/%m/%Y')}")
                return False
                
        except Exception as e:
            st.error(f"Error al eliminar el registro: {e}")
            return False
