"""
Utilidades para el manejo de datos del Dashboard ICE - VERSIÓN CON SHEETS FICHAS
CORRECCIÓN: Cargar fichas metodológicas desde Google Sheets en lugar de Excel
"""

import pandas as pd
import numpy as np
import streamlit as st
import os
from config import COLUMN_MAPPING, DEFAULT_META, INDICATOR_TYPES

# Importación de Google Sheets
try:
    from google_sheets_manager import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

class DataLoader:
    """Clase para cargar datos - VERSIÓN CON FICHAS DESDE SHEETS"""
    
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
        """Cargar datos desde Google Sheets - SILENCIOSO PARA ENCABEZADO"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                return self._create_empty_dataframe()
            
            # Cargar datos silenciosamente
            df = self.sheets_manager.load_data()
            
            if df is None or df.empty:
                return self._create_empty_dataframe()
            
            # Procesar datos silenciosamente
            self._process_dataframe_silent(df)
            
            # Verificar y limpiar silenciosamente
            if self._verify_dataframe_simple(df):
                return df
            else:
                return self._create_empty_dataframe()
                
        except Exception as e:
            return self._create_empty_dataframe()
    
    def load_fichas_data(self):
        """NUEVO: Cargar fichas metodológicas desde Google Sheets"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                return None
            
            # Cargar fichas desde Google Sheets
            fichas_df = self.sheets_manager.load_fichas_data()
            
            if fichas_df is None:
                return None
            
            if fichas_df.empty:
                return pd.DataFrame()
            
            # Limpiar datos de fichas
            fichas_df = fichas_df.dropna(subset=['Codigo'], how='all')
            
            return fichas_df
            
        except Exception as e:
            st.error(f"❌ Error al cargar fichas: {e}")
            return None
    
    def _create_empty_dataframe(self):
        """Crear DataFrame vacío"""
        return pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado'
        ])
    
    def _process_dataframe_silent(self, df):
        """Procesar DataFrame silenciosamente (sin mostrar información en pantalla)"""
        try:
            # Renombrar columnas
            for original, nuevo in COLUMN_MAPPING.items():
                if original in df.columns:
                    df.rename(columns={original: nuevo}, inplace=True)
            
            # Procesar fechas silenciosamente
            self._process_dates_silent(df)
            
            # Procesar valores silenciosamente
            self._process_values_silent(df)
            
            # Añadir columnas por defecto
            self._add_default_columns_corrected(df)
            
            # Normalización silenciosa
            self._normalize_values_silent(df)
            
        except Exception as e:
            pass  # Silencioso
    
    def _process_dates_silent(self, df):
        """Procesar fechas silenciosamente"""
        try:
            if 'Fecha' not in df.columns:
                return
            
            # Formatos de fecha comunes
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', 
                '%Y/%m/%d', '%m/%d/%Y', '%d.%m.%Y'
            ]
            
            fechas_convertidas = None
            
            for formato in date_formats:
                try:
                    temp_fechas = pd.to_datetime(df['Fecha'], format=formato, errors='coerce')
                    validas = temp_fechas.notna().sum()
                    
                    if validas > 0:
                        if fechas_convertidas is None or validas > fechas_convertidas.notna().sum():
                            fechas_convertidas = temp_fechas
                except:
                    continue
            
            if fechas_convertidas is None or fechas_convertidas.notna().sum() == 0:
                try:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
                except:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce')
            
            df['Fecha'] = fechas_convertidas
                
        except Exception as e:
            pass  # Silencioso
    
    def _process_values_silent(self, df):
        """Procesar valores silenciosamente"""
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
                
        except Exception as e:
            pass  # Silencioso
    
    def _normalize_values_silent(self, df):
        """Normalización silenciosa (sin mostrar información en pantalla)"""
        try:
            if df.empty or 'Valor' not in df.columns:
                return
            
            # Inicializar valores normalizados
            df['Valor_Normalizado'] = 0.0
            
            # Verificar que tenemos datos válidos
            valores_validos = df['Valor'].notna()
            if not valores_validos.any():
                return
            
            # Agrupar por indicador para detectar si tiene historial
            for codigo in df['Codigo'].unique():
                if pd.isna(codigo):
                    continue
                    
                mask = df['Codigo'] == codigo
                datos_indicador = df[mask]
                valores = datos_indicador['Valor'].dropna()
                
                if valores.empty:
                    continue
                
                # Obtener información del indicador
                indicador_info = datos_indicador.iloc[0]
                tipo = str(indicador_info.get('Tipo', 'porcentaje')).lower()
                
                # Verificar si tiene historial (más de un registro)
                tiene_historico = len(valores) > 1
                
                if not tiene_historico:
                    # SIN HISTORIAL: Asignar valores fijos según tipo
                    if tipo in ['porcentaje', 'percentage', '%']:
                        # Porcentajes: usar valor original normalizado
                        for index in datos_indicador.index:
                            valor = datos_indicador.loc[index, 'Valor']
                            if pd.notna(valor):
                                if valor <= 1:
                                    valor_norm = valor  # Ya está en 0-1
                                else:
                                    valor_norm = valor / 100  # Convertir de 0-100 a 0-1
                                df.at[index, 'Valor_Normalizado'] = max(0, min(1, valor_norm))
                    else:
                        # VALORES NUMÉRICOS SIN HISTORIAL: Asignar 0.7 (70%)
                        for index in datos_indicador.index:
                            df.at[index, 'Valor_Normalizado'] = 0.7
                    
                else:
                    # CON HISTORIAL: Normalizar por el máximo del indicador
                    if tipo in ['porcentaje', 'percentage', '%']:
                        # Porcentajes: convertir a 0-1 si es necesario
                        for index in datos_indicador.index:
                            valor = datos_indicador.loc[index, 'Valor']
                            if pd.notna(valor):
                                if valor <= 1:
                                    valor_norm = valor
                                else:
                                    valor_norm = valor / 100
                                df.at[index, 'Valor_Normalizado'] = max(0, min(1, valor_norm))
                    else:
                        # Valores numéricos: normalizar por el máximo del indicador
                        max_valor = valores.max()
                        if max_valor > 0:
                            for index in datos_indicador.index:
                                valor = datos_indicador.loc[index, 'Valor']
                                if pd.notna(valor):
                                    valor_norm = valor / max_valor
                                    df.at[index, 'Valor_Normalizado'] = max(0, valor_norm)
                        else:
                            # Si todos los valores son 0, asignar 0.7
                            for index in datos_indicador.index:
                                df.at[index, 'Valor_Normalizado'] = 0.7
                
        except Exception as e:
            # Fallback seguro silencioso
            try:
                df['Valor_Normalizado'] = 0.7
            except:
                pass
    
    def _add_default_columns_corrected(self, df):
        """Añadir columnas por defecto - VERSIÓN SILENCIOSA"""
        try:
            # Meta por defecto
            if 'Meta' not in df.columns:
                df['Meta'] = DEFAULT_META
            
            # Peso por defecto
            if 'Peso' not in df.columns:
                df['Peso'] = 1.0
            
            # Tipo por defecto
            if 'Tipo' not in df.columns:
                df['Tipo'] = 'porcentaje'
            
            # Convertir tipos
            df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce').fillna(DEFAULT_META)
            df['Peso'] = pd.to_numeric(df['Peso'], errors='coerce').fillna(1.0)
            
        except Exception as e:
            pass  # Silencioso
    
    def _verify_dataframe_simple(self, df):
        """Verificar DataFrame"""
        try:
            if df.empty:
                return True
            
            # Verificar columnas esenciales
            required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False
            
            # Limpiar registros vacíos
            initial_count = len(df)
            df.dropna(subset=['Codigo'], inplace=True)
            
            return True
            
        except Exception as e:
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
    """Clase para procesar datos - VERSIÓN CORREGIDA"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes usando normalización simple - APLICANDO FILTRO DE FECHA"""
        try:
            if df.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # ✅ APLICAR FILTRO DE FECHA SI SE PROPORCIONA
            if fecha_filtro is not None:
                # Convertir fecha_filtro a datetime si es necesario
                if not pd.api.types.is_datetime64_any_dtype(pd.Series([fecha_filtro])):
                    fecha_filtro = pd.to_datetime(fecha_filtro)
                
                # Filtrar por la fecha específica
                df_filtrado = df[df['Fecha'] == fecha_filtro].copy()
                
                if df_filtrado.empty:
                    # Si no hay datos para esa fecha exacta, usar los más cercanos
                    fechas_disponibles = df['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= fecha_filtro]
                    
                    if not fecha_mas_cercana.empty:
                        fecha_usar = fecha_mas_cercana.iloc[-1]  # La más reciente antes o igual
                        df_filtrado = df[df['Fecha'] == fecha_usar].copy()
                    else:
                        # Si no hay fechas anteriores, usar la primera disponible
                        fecha_usar = fechas_disponibles.iloc[0]
                        df_filtrado = df[df['Fecha'] == fecha_usar].copy()
            else:
                # Sin filtro de fecha, usar valores más recientes por indicador
                df_filtrado = DataProcessor._get_latest_values_by_indicator(df)
            
            if df_filtrado.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Resto del método permanece igual...
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
        """Obtener valores más recientes por indicador"""
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
    """Clase para editar datos - VERSIÓN CORREGIDA"""
    
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

class SheetsDataLoader:
    """NUEVA CLASE: Cargador de datos metodológicos desde Google Sheets"""
    
    def __init__(self):
        self.sheets_manager = None
        
        if GOOGLE_SHEETS_AVAILABLE:
            try:
                self.sheets_manager = GoogleSheetsManager()
            except Exception as e:
                st.error(f"❌ Error al inicializar Google Sheets para fichas: {e}")
    
    def load_fichas_data(self):
        """Cargar datos de fichas metodológicas desde Google Sheets"""
        try:
            if not self.sheets_manager:
                return None
            
            fichas_df = self.sheets_manager.load_fichas_data()
            
            if fichas_df is None:
                return None
            
            if fichas_df.empty:
                return pd.DataFrame()
            
            # Limpiar y procesar fichas
            fichas_df = fichas_df.dropna(subset=['Codigo'], how='all')
            
            return fichas_df
            
        except Exception as e:
            st.error(f"❌ Error al cargar fichas desde Sheets: {e}")
            return None
    
    def add_ficha(self, ficha_data):
        """Agregar nueva ficha metodológica"""
        try:
            if not self.sheets_manager:
                return False
            
            return self.sheets_manager.add_ficha_record(ficha_data)
            
        except Exception as e:
            st.error(f"❌ Error al agregar ficha: {e}")
            return False
    
    def update_ficha(self, codigo, campo, nuevo_valor):
        """Actualizar campo de ficha metodológica"""
        try:
            if not self.sheets_manager:
                return False
            
            return self.sheets_manager.update_ficha_record(codigo, campo, nuevo_valor)
            
        except Exception as e:
            st.error(f"❌ Error al actualizar ficha: {e}")
            return False

# Mantener compatibilidad con ExcelDataLoader para transición gradual
class ExcelDataLoader:
    """CLASE OBSOLETA: Mantenida para compatibilidad pero ya no se usa"""
    
    def __init__(self):
        st.warning("⚠️ ExcelDataLoader obsoleto. Ahora se usan fichas de Google Sheets.")
    
    def load_excel_data(self):
        """Método obsoleto"""
        st.info("📋 Cargando fichas desde Google Sheets en lugar de Excel...")
        
        # Redirigir a SheetsDataLoader
        sheets_loader = SheetsDataLoader()
        return sheets_loader.load_fichas_data()
