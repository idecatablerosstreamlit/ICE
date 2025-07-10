"""
Utilidades para el manejo de datos del Dashboard ICE - VERSIÓN CORREGIDA
CORRECCIÓN: Normalización simplificada y eliminación de bucles infinitos
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import COLUMN_MAPPING, DEFAULT_META, EXCEL_FILENAME
import openpyxl

# Importación de Google Sheets
try:
    from google_sheets_manager import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

class DataLoader:
    """Clase para cargar datos - VERSIÓN SIMPLIFICADA"""
    
    def __init__(self):
        self.df = None
        self.sheets_manager = None
        
        if not GOOGLE_SHEETS_AVAILABLE:
            st.error("❌ **Google Sheets no disponible.** Instala: `pip install gspread google-auth`")
            return
        
        try:
            self.sheets_manager = GoogleSheetsManager()
        except Exception as e:
            st.error(f"❌ Error al inicializar Google Sheets: {e}")
            self.sheets_manager = None
    
    def load_data(self):
        """Cargar datos desde Google Sheets - SIMPLIFICADO"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                st.error("❌ Google Sheets no disponible")
                return self._create_empty_dataframe()
            
            # Cargar datos básicos
            st.write("📥 Conectando con Google Sheets...")
            df = self.sheets_manager.load_data()
            
            if df is None:
                st.error("❌ Error al conectar con Google Sheets")
                return self._create_empty_dataframe()
            
            if df.empty:
                st.warning("📋 Google Sheets está vacío")
                return self._create_empty_dataframe()
            
            st.write(f"📊 Cargados {len(df)} registros")
            
            # Procesar datos
            st.write("🔧 Procesando datos...")
            self._process_dataframe_simple(df)
            
            # Verificar y limpiar
            if self._verify_dataframe_simple(df):
                st.success("✅ Datos cargados correctamente")
                return df
            else:
                st.error("❌ Datos inválidos")
                return self._create_empty_dataframe()
                
        except Exception as e:
            st.error(f"❌ Error crítico: {e}")
            return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """Crear DataFrame vacío"""
        return pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
        ])
    
    def _process_dataframe_simple(self, df):
        """Procesar DataFrame - VERSIÓN SIMPLIFICADA"""
        try:
            # Renombrar columnas
            for original, nuevo in COLUMN_MAPPING.items():
                if original in df.columns:
                    df.rename(columns={original: nuevo}, inplace=True)
            
            # Procesar fechas
            self._process_dates_simple(df)
            
            # Procesar valores
            self._process_values_simple(df)
            
            # Añadir columnas por defecto
            self._add_default_columns(df)
            
            # Normalización SIMPLIFICADA
            self._normalize_values_simple(df)
            
        except Exception as e:
            st.error(f"Error en procesamiento: {e}")
    
    def _process_dates_simple(self, df):
        """Procesar fechas - SIMPLIFICADO"""
        try:
            if 'Fecha' not in df.columns:
                return
            
            # Convertir fechas con formato más común
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
            
            fechas_invalidas = df['Fecha'].isna().sum()
            if fechas_invalidas > 0:
                st.warning(f"⚠️ {fechas_invalidas} fechas no válidas")
                
        except Exception as e:
            st.warning(f"Error al procesar fechas: {e}")
    
    def _process_values_simple(self, df):
        """Procesar valores - SIMPLIFICADO"""
        try:
            if 'Valor' not in df.columns:
                return
            
            # Convertir valores a numérico
            if df['Valor'].dtype == 'object':
                df['Valor'] = (df['Valor']
                              .astype(str)
                              .str.replace(',', '.')
                              .str.strip())
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            valores_invalidos = df['Valor'].isna().sum()
            if valores_invalidos > 0:
                st.warning(f"⚠️ {valores_invalidos} valores no válidos")
                
        except Exception as e:
            st.warning(f"Error al procesar valores: {e}")
    
    def _add_default_columns(self, df):
        """Añadir columnas por defecto"""
        if 'Meta' not in df.columns:
            df['Meta'] = DEFAULT_META
        if 'Peso' not in df.columns:
            df['Peso'] = 1.0
        if 'Tipo' not in df.columns:
            df['Tipo'] = 'porcentaje'
        
        # Convertir tipos
        df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce').fillna(DEFAULT_META)
        df['Peso'] = pd.to_numeric(df['Peso'], errors='coerce').fillna(1.0)
    
    def _normalize_values_simple(self, df):
        """Normalización SIMPLIFICADA - Sin bucles complejos"""
        try:
            if df.empty or 'Valor' not in df.columns:
                return
            
            # Inicializar valores normalizados
            df['Valor_Normalizado'] = 0.5
            
            # Normalización por tipo - SIMPLIFICADA
            for tipo in df['Tipo'].unique():
                if pd.isna(tipo):
                    continue
                    
                mask = df['Tipo'] == tipo
                valores = df.loc[mask, 'Valor']
                
                if tipo.lower() in ['porcentaje', 'percentage']:
                    # Porcentajes: convertir a 0-1 si están en 0-100
                    valores_norm = valores.apply(lambda x: x if x <= 1 else x / 100)
                    df.loc[mask, 'Valor_Normalizado'] = valores_norm.clip(0, 1)
                else:
                    # Otros tipos: normalización simple por máximo
                    if valores.max() > 0:
                        df.loc[mask, 'Valor_Normalizado'] = (valores / valores.max()).clip(0, 1)
                    else:
                        df.loc[mask, 'Valor_Normalizado'] = 0.5
            
            # Asegurar que todos los valores están entre 0 y 1
            df['Valor_Normalizado'] = df['Valor_Normalizado'].clip(0, 1)
            
        except Exception as e:
            st.error(f"Error en normalización: {e}")
            # Fallback
            if 'Valor' in df.columns:
                df['Valor_Normalizado'] = df['Valor'].clip(0, 1)
    
    def _verify_dataframe_simple(self, df):
        """Verificar DataFrame - SIMPLIFICADO"""
        try:
            if df.empty:
                return True
            
            # Verificar columnas esenciales
            required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Faltan columnas: {missing_columns}")
                return False
            
            # Limpiar registros vacíos
            initial_count = len(df)
            df.dropna(subset=['Codigo'], inplace=True)
            final_count = len(df)
            
            if initial_count != final_count:
                st.info(f"🧹 Limpiados {initial_count - final_count} registros vacíos")
            
            return True
            
        except Exception as e:
            st.error(f"Error en verificación: {e}")
            return False
    
    def get_data_source_info(self):
        """Obtener información de la fuente"""
        if self.sheets_manager:
            return {
                'source': 'Google Sheets',
                'connection_info': self.sheets_manager.get_connection_info()
            }
        else:
            return {
                'source': 'Google Sheets (No conectado)',
                'connection_info': {'connected': False}
            }

class DataProcessor:
    """Clase para procesar datos - SIMPLIFICADA"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes - SIMPLIFICADO"""
        try:
            if df.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Usar valores más recientes
            df_filtrado = DataProcessor._get_latest_values_by_indicator(df)
            
            if df_filtrado.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Verificar columnas necesarias
            required_columns = ['Valor_Normalizado', 'Peso', 'Componente', 'Categoria']
            if not all(col in df_filtrado.columns for col in required_columns):
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Calcular puntajes por componente
            puntajes_componente = df_filtrado.groupby('Componente').apply(
                lambda x: (x['Valor_Normalizado'] * x['Peso']).sum() / x['Peso'].sum()
            ).reset_index()
            puntajes_componente.columns = ['Componente', 'Puntaje_Ponderado']
            
            # Calcular puntajes por categoría
            puntajes_categoria = df_filtrado.groupby('Categoria').apply(
                lambda x: (x['Valor_Normalizado'] * x['Peso']).sum() / x['Peso'].sum()
            ).reset_index()
            puntajes_categoria.columns = ['Categoria', 'Puntaje_Ponderado']
            
            # Calcular puntaje general
            peso_total = df_filtrado['Peso'].sum()
            if peso_total > 0:
                puntaje_general = (df_filtrado['Valor_Normalizado'] * df_filtrado['Peso']).sum() / peso_total
            else:
                puntaje_general = df_filtrado['Valor_Normalizado'].mean()
            
            return puntajes_componente, puntajes_categoria, puntaje_general
            
        except Exception as e:
            st.error(f"Error en cálculo de puntajes: {e}")
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
    
    @staticmethod
    def _get_latest_values_by_indicator(df):
        """Obtener valores más recientes - SIMPLIFICADO"""
        try:
            if df.empty:
                return df
            
            # Verificar columnas necesarias
            if not all(col in df.columns for col in ['Codigo', 'Fecha', 'Valor']):
                return df
            
            # Limpiar datos
            df_clean = df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            
            if df_clean.empty:
                return df
            
            # Obtener valores más recientes
            df_latest = (df_clean
                        .sort_values(['Codigo', 'Fecha'])
                        .groupby('Codigo')
                        .last()
                        .reset_index())
            
            return df_latest
            
        except Exception as e:
            st.error(f"Error al obtener valores recientes: {e}")
            return df

class DataEditor:
    """Clase para editar datos - SIMPLIFICADA"""
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path=None):
        """Agregar nuevo registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ Google Sheets no disponible")
                return False
            
            sheets_manager = GoogleSheetsManager()
            
            # Buscar información base
            if df.empty:
                st.error("❌ No hay datos base disponibles")
                return False
            
            indicador_existente = df[df['Codigo'] == codigo]
            if indicador_existente.empty:
                st.error(f"❌ No se encontró el código {codigo}")
                return False
            
            indicador_base = indicador_existente.iloc[0]
            
            # Preparar datos
            data_dict = {
                'LINEA DE ACCIÓN': indicador_base.get('Linea_Accion', ''),
                'COMPONENTE PROPUESTO': indicador_base.get('Componente', ''),
                'CATEGORÍA': indicador_base.get('Categoria', ''),
                'COD': codigo,
                'Nombre de indicador': indicador_base.get('Indicador', ''),
                'Valor': valor,
                'Fecha': fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else str(fecha),
                'Tipo': indicador_base.get('Tipo', 'porcentaje')
            }
            
            # Agregar a Google Sheets
            return sheets_manager.add_record(data_dict)
            
        except Exception as e:
            st.error(f"❌ Error al agregar: {e}")
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path=None):
        """Actualizar registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                return False
            
            sheets_manager = GoogleSheetsManager()
            return sheets_manager.update_record(codigo, fecha, nuevo_valor)
            
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path=None):
        """Eliminar registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                return False
            
            sheets_manager = GoogleSheetsManager()
            return sheets_manager.delete_record(codigo, fecha)
            
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            return False

class ExcelDataLoader:
    """Clase para cargar datos del Excel"""
    
    def __init__(self):
        self.excel_path = os.path.join(os.path.dirname(__file__), EXCEL_FILENAME)
    
    def load_excel_data(self):
        """Cargar datos del Excel"""
        try:
            if not os.path.exists(self.excel_path):
                return None
            
            df = pd.read_excel(
                self.excel_path, 
                sheet_name="Hoja metodológica indicadores",
                header=1
            )
            
            # Mapeo básico de columnas
            column_mapping = {
                'C1_ID': 'Codigo',
                'C2_Nombre indicador': 'Nombre_Indicador',
                'C3_Definición': 'Definicion',
                'C4_Objetivo': 'Objetivo',
                'C5_Área temática': 'Area_Tematica',
                'C6_Tema': 'Tema',
                'C18_Sector': 'Sector',
                'C19_Entidad': 'Entidad',
                'C20_Dependencia': 'Dependencia'
            }
            
            # Renombrar columnas existentes
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})
            
            # Limpiar datos
            df = df.dropna(subset=['Codigo'])
            
            return df
            
        except Exception as e:
            st.error(f"Error al cargar Excel: {e}")
            return None
