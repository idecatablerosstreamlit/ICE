"""
Utilidades para el manejo de datos del Dashboard ICE - Versión corregida
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
            # Debug: mostrar información del archivo
            st.sidebar.write(f"Buscando archivo: {self.csv_path}")
            st.sidebar.write(f"Archivo existe: {os.path.exists(self.csv_path)}")
            
            # Cargar el archivo CSV con punto y coma como separador y encoding UTF-8
            self.df = pd.read_csv(self.csv_path, sep=CSV_SEPARATOR, encoding='utf-8-sig')
            
            st.sidebar.write(f"Filas cargadas: {len(self.df)}")
            st.sidebar.write(f"Columnas: {list(self.df.columns)}")
            
            # Renombrar columnas
            self._rename_columns()
            
            # Procesar fechas y valores
            self._process_dates()
            self._process_values()
            
            # Añadir columnas por defecto
            self._add_default_columns()
            
            # Validar datos
            if self._validate_data():
                st.sidebar.success(f"Datos cargados correctamente: {len(self.df)} registros")
                return self.df
            else:
                st.error("Error en la validación de datos")
                return None
            
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            st.error(f"Archivo buscado: {self.csv_path}")
            return None
    
    def _rename_columns(self):
        """Renombrar columnas según el mapeo"""
        original_columns = self.df.columns.tolist()
        for original, nuevo in COLUMN_MAPPING.items():
            if original in self.df.columns:
                self.df = self.df.rename(columns={original: nuevo})
        
        # Debug: mostrar cambios
        new_columns = self.df.columns.tolist()
        st.sidebar.write(f"Columnas renombradas: {len([c for c in original_columns if c not in new_columns])}")
    
    def _process_dates(self):
        """Procesar columna de fechas"""
        try:
            # Mostrar algunos valores originales
            st.sidebar.write(f"Fechas originales (primeras 3): {self.df['Fecha'].head(3).tolist()}")
            
            # Intentar múltiples formatos de fecha
            if self.df['Fecha'].dtype == 'object':
                # Primero intentar con formato dd/mm/yyyy
                try:
                    self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], format='%d/%m/%Y', errors='coerce')
                except:
                    # Si falla, intentar detección automática
                    self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], errors='coerce')
            
            # Verificar si hay fechas NaT (Not a Time)
            fechas_invalidas = self.df['Fecha'].isna().sum()
            if fechas_invalidas > 0:
                st.sidebar.warning(f"Fechas inválidas encontradas: {fechas_invalidas}")
            
            # Mostrar fechas procesadas
            fechas_unicas = self.df['Fecha'].dropna().unique()
            st.sidebar.write(f"Fechas únicas: {len(fechas_unicas)}")
            
        except Exception as e:
            st.sidebar.error(f"Error al procesar fechas: {e}")
    
    def _process_values(self):
        """Procesar valores numéricos"""
        try:
            # Mostrar algunos valores originales
            st.sidebar.write(f"Valores originales (primeros 3): {self.df['Valor'].head(3).tolist()}")
            
            # Si los valores son texto (con coma decimal)
            if self.df['Valor'].dtype == 'object':
                # Reemplazar coma por punto y convertir a float
                self.df['Valor'] = self.df['Valor'].astype(str).str.replace(',', '.').astype(float)
            
            # Verificar valores inválidos
            valores_invalidos = self.df['Valor'].isna().sum()
            if valores_invalidos > 0:
                st.sidebar.warning(f"Valores inválidos encontrados: {valores_invalidos}")
            
            # Mostrar estadísticas básicas
            st.sidebar.write(f"Rango de valores: {self.df['Valor'].min():.2f} - {self.df['Valor'].max():.2f}")
            
        except Exception as e:
            st.sidebar.error(f"Error al procesar valores: {e}")
    
    def _add_default_columns(self):
        """Añadir columnas por defecto si no existen"""
        try:
            if 'Meta' not in self.df.columns:
                self.df['Meta'] = DEFAULT_META
            
            if 'Peso' not in self.df.columns:
                # Calcular peso uniforme basado en número de indicadores únicos
                num_indicadores = self.df['Indicador'].nunique() if 'Indicador' in self.df.columns else len(self.df)
                self.df['Peso'] = 100 / num_indicadores if num_indicadores > 0 else 1
            
            st.sidebar.write("Columnas por defecto añadidas: Meta, Peso")
            
        except Exception as e:
            st.sidebar.error(f"Error al añadir columnas por defecto: {e}")
    
    def _validate_data(self):
        """Validar que los datos estén correctamente cargados"""
        try:
            required_columns = ['Indicador', 'Componente', 'Categoria', 'Valor', 'Fecha']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            
            if missing_columns:
                st.error(f"Columnas faltantes: {missing_columns}")
                return False
            
            # Verificar que hay datos válidos
            if len(self.df) == 0:
                st.error("No hay datos en el DataFrame")
                return False
            
            # Verificar que hay fechas válidas
            if self.df['Fecha'].isna().all():
                st.error("No hay fechas válidas")
                return False
            
            # Verificar que hay valores válidos
            if self.df['Valor'].isna().all():
                st.error("No hay valores válidos")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Error en validación: {e}")
            return False

class DataProcessor:
    """Clase para procesar y calcular métricas de los datos"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes por componente y categoría"""
        try:
            if fecha_filtro:
                df_filtrado = df[df['Fecha'] == fecha_filtro].copy()
            else:
                # Si no hay filtro de fecha, usar la fecha más reciente
                ultima_fecha = df['Fecha'].max()
                df_filtrado = df[df['Fecha'] == ultima_fecha].copy()

            if len(df_filtrado) == 0:
                st.warning("No hay datos para la fecha seleccionada")
                return pd.DataFrame(), pd.DataFrame(), 0

            # Calcular cumplimiento
            df_filtrado['Cumplimiento'] = df_filtrado['Valor'] * 100
            df_filtrado['Cumplimiento'] = df_filtrado['Cumplimiento'].clip(upper=100)
            
            # Calcular puntaje ponderado
            df_filtrado['Puntaje_Ponderado'] = df_filtrado['Cumplimiento'] * df_filtrado['Peso'] / 100

            # Agrupar por componente y categoría
            puntajes_componente = df_filtrado.groupby('Componente')['Puntaje_Ponderado'].sum().reset_index()
            puntajes_categoria = df_filtrado.groupby('Categoria')['Puntaje_Ponderado'].sum().reset_index()
            puntaje_general = df_filtrado['Puntaje_Ponderado'].sum()

            return puntajes_componente, puntajes_categoria, puntaje_general
            
        except Exception as e:
            st.error(f"Error al calcular puntajes: {e}")
            return pd.DataFrame(), pd.DataFrame(), 0
    
    @staticmethod
    def create_pivot_table(df, fecha=None, filas='Categoria', columnas='Componente', valores='Valor'):
        """Crear tabla dinámica"""
        try:
            if fecha:
                df_filtrado = df[df['Fecha'] == fecha].copy()
            else:
                ultima_fecha = df['Fecha'].max()
                df_filtrado = df[df['Fecha'] == ultima_fecha].copy()

            if len(df_filtrado) == 0:
                st.warning("No hay datos para crear la tabla dinámica")
                return pd.DataFrame()

            # Añadir columnas calculadas si son necesarias
            if valores in ["Cumplimiento", "Puntaje_Ponderado"]:
                df_filtrado['Cumplimiento'] = df_filtrado['Valor'] * 100
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
            
        except Exception as e:
            st.error(f"Error al crear tabla dinámica: {e}")
            return pd.DataFrame()

class DataEditor:
    """Clase para editar datos"""
    
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Guardar edición de un indicador"""
        try:
            # Convertir fecha a datetime si no lo es
            if not isinstance(fecha, pd.Timestamp):
                fecha = pd.to_datetime(fecha)
            
            # Buscar el registro existente
            mask = (df['Codigo'] == codigo) & (df['Fecha'] == fecha)
            idx = df[mask].index

            if len(idx) > 0:
                # Actualizar registro existente
                df.loc[idx, 'Valor'] = nuevo_valor
            else:
                # Crear nuevo registro basado en uno existente del mismo código
                registro_base = df[df['Codigo'] == codigo].iloc[0].copy()
                registro_base['Fecha'] = fecha
                registro_base['Valor'] = nuevo_valor
                
                # Añadir el nuevo registro
                df = pd.concat([df, pd.DataFrame([registro_base])], ignore_index=True)
            
            # Guardar el archivo
            # Convertir fechas de vuelta al formato original para guardar
            df_to_save = df.copy()
            df_to_save['Fecha'] = df_to_save['Fecha'].dt.strftime('%d/%m/%Y')
            df_to_save['Valor'] = df_to_save['Valor'].astype(str).str.replace('.', ',')
            
            # Aplicar mapeo inverso de columnas
            reverse_mapping = {v: k for k, v in COLUMN_MAPPING.items()}
            for nuevo, original in reverse_mapping.items():
                if nuevo in df_to_save.columns:
                    df_to_save = df_to_save.rename(columns={nuevo: original})
            
            df_to_save.to_csv(csv_path, sep=CSV_SEPARATOR, index=False, encoding='utf-8-sig')
            return True
            
        except Exception as e:
            st.error(f"Error al guardar edición: {e}")
            return False
