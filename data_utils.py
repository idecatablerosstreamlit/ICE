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
        """
        Calcular puntajes usando SIEMPRE el valor más reciente de cada indicador.
        El parámetro fecha_filtro se ignora para mantener consistencia.
        """
        if df.empty:
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

        # SIEMPRE usar el valor más reciente de cada indicador
        # Esto garantiza que el dashboard funcione correctamente sin importar las fechas
        df_filtrado = DataProcessor._get_latest_values_by_indicator(df)

        if len(df_filtrado) == 0:
            import streamlit as st
            st.error("No se pudieron obtener valores más recientes de los indicadores")
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

        # Normalizar valores (0-1)
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
    def _get_latest_values_by_indicator(df):
        """
        Obtener el valor más reciente de cada indicador.
        Esta es la función CLAVE para el correcto funcionamiento del dashboard.
        """
        try:
            if df.empty:
                return df
            
            # Verificar que tenemos las columnas necesarias
            required_columns = ['Codigo', 'Fecha', 'Valor']
            if not all(col in df.columns for col in required_columns):
                import streamlit as st
                st.error(f"Faltan columnas requeridas: {required_columns}")
                return df
            
            # Remover filas con valores NaN en columnas críticas
            df_clean = df.dropna(subset=['Codigo', 'Fecha', 'Valor']).copy()
            
            if df_clean.empty:
                import streamlit as st
                st.warning("No hay datos válidos después de limpiar valores NaN")
                return df
            
            # Agrupar por código de indicador y tomar el registro con fecha más reciente
            def get_latest_record(group):
                # Ordenar por fecha y tomar el último registro
                latest_idx = group['Fecha'].idxmax()
                return group.loc[latest_idx]
            
            # Aplicar la función a cada grupo de indicadores
            df_latest = df_clean.groupby('Codigo', as_index=False).apply(
                lambda x: get_latest_record(x)
            ).reset_index(drop=True)
            
            import streamlit as st
            # Mostrar información de debug
            with st.expander("🔍 Debug: Valores más recientes por indicador", expanded=False):
                st.write(f"**Total indicadores únicos:** {df_clean['Codigo'].nunique()}")
                st.write(f"**Registros después de filtrar:** {len(df_latest)}")
                st.dataframe(df_latest[['Codigo', 'Indicador', 'Valor', 'Fecha', 'Componente']].sort_values('Fecha'))
            
            return df_latest
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error crítico al obtener valores más recientes: {e}")
            import traceback
            st.code(traceback.format_exc())
            # En caso de error, retornar DataFrame original como fallback
            return df
    
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
        """Crear tabla dinámica (función legacy - ya no se usa)"""
        return pd.DataFrame()  # Función deshabilitada

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
