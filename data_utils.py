"""
Utilidades para el manejo de datos del Dashboard ICE - VERSIÓN CORREGIDA
CORRECCIÓN: Normalización que preserva valores originales cuando no hay histórico
"""

import pandas as pd
import numpy as np
import streamlit as st
import os
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
        """Cargar datos desde Google Sheets - CON MENSAJES ORGANIZADOS"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                st.error("❌ Google Sheets no disponible")
                return self._create_empty_dataframe()
            
            # Usar un spinner para la conexión
            with st.spinner("🔄 Conectando con Google Sheets..."):
                df = self.sheets_manager.load_data()
            
            if df is None:
                st.error("❌ Error al conectar con Google Sheets")
                return self._create_empty_dataframe()
            
            if df.empty:
                st.warning("📋 Google Sheets está vacío")
                return self._create_empty_dataframe()
            
            # Mostrar resumen de carga
            st.success(f"📊 Cargados {len(df)} registros desde Google Sheets")
            
            # Procesar datos (esto incluye el expander con detalles)
            self._process_dataframe_simple(df)
            
            # Verificar y limpiar
            if self._verify_dataframe_simple(df):
                st.success("✅ Datos procesados y listos para usar")
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
        """Procesar DataFrame - VERSIÓN SIMPLIFICADA CON EXPANDER"""
        try:
            with st.expander("🔧 Detalles del procesamiento de datos", expanded=False):
                st.write("📝 **Procesando datos desde Google Sheets...**")
                
                # Renombrar columnas
                st.write("1️⃣ Renombrando columnas...")
                for original, nuevo in COLUMN_MAPPING.items():
                    if original in df.columns:
                        df.rename(columns={original: nuevo}, inplace=True)
                st.success("✅ Columnas renombradas correctamente")
                
                # Procesar fechas
                st.write("2️⃣ Procesando fechas...")
                self._process_dates_simple(df)
                
                # Procesar valores
                st.write("3️⃣ Procesando valores...")
                self._process_values_simple(df)
                
                # Añadir columnas por defecto
                st.write("4️⃣ Añadiendo columnas por defecto...")
                self._add_default_columns(df)
                st.success("✅ Columnas por defecto añadidas")
                
                # Normalización CORREGIDA
                st.write("5️⃣ Aplicando normalización inteligente...")
                self._normalize_values_fixed(df)
                
                st.success("🎉 **Procesamiento completado exitosamente**")
            
        except Exception as e:
            st.error(f"Error en procesamiento: {e}")
    
    def _process_dates_simple(self, df):
        """Procesar fechas - MEJORADO CON MENSAJES ORGANIZADOS"""
        try:
            if 'Fecha' not in df.columns:
                st.info("No hay columna 'Fecha' para procesar")
                return
            
            # Formatos de fecha comunes de Google Sheets
            date_formats = [
                '%d/%m/%Y',   # 01/12/2025
                '%d-%m-%Y',   # 01-12-2025
                '%Y-%m-%d',   # 2025-12-01
                '%Y/%m/%d',   # 2025/12/01
                '%m/%d/%Y',   # 12/01/2025
                '%d.%m.%Y'    # 01.12.2025
            ]
            
            fechas_convertidas = None
            mejor_formato = None
            
            # Probar cada formato
            for formato in date_formats:
                try:
                    temp_fechas = pd.to_datetime(df['Fecha'], format=formato, errors='coerce')
                    validas = temp_fechas.notna().sum()
                    
                    if validas > 0:
                        if fechas_convertidas is None or validas > fechas_convertidas.notna().sum():
                            fechas_convertidas = temp_fechas
                            mejor_formato = formato
                except:
                    continue
            
            # Si ningún formato específico funcionó, usar conversión automática
            if fechas_convertidas is None or fechas_convertidas.notna().sum() == 0:
                try:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
                    mejor_formato = "automático"
                except:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce')
                    mejor_formato = "automático (US)"
            
            # Asignar fechas convertidas
            df['Fecha'] = fechas_convertidas
            
            # Reportar resultados
            fechas_validas = df['Fecha'].notna().sum()
            fechas_invalidas = df['Fecha'].isna().sum()
            
            if fechas_validas > 0:
                st.success(f"✅ {fechas_validas} fechas procesadas correctamente (formato: {mejor_formato})")
            
            if fechas_invalidas > 0:
                st.warning(f"⚠️ {fechas_invalidas} fechas no se pudieron convertir")
                
        except Exception as e:
            st.error(f"Error al procesar fechas: {e}")
            # Intentar conversión básica como fallback
            try:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
                st.info("Usando conversión de fechas básica como fallback")
            except:
                st.error("No se pudieron procesar las fechas")
    
    def _process_values_simple(self, df):
        """Procesar valores - SIMPLIFICADO CON MENSAJES ORGANIZADOS"""
        try:
            if 'Valor' not in df.columns:
                st.info("No hay columna 'Valor' para procesar")
                return
            
            # Convertir valores a numérico
            if df['Valor'].dtype == 'object':
                df['Valor'] = (df['Valor']
                              .astype(str)
                              .str.replace(',', '.')
                              .str.strip())
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            valores_invalidos = df['Valor'].isna().sum()
            valores_validos = df['Valor'].notna().sum()
            
            if valores_validos > 0:
                st.success(f"✅ {valores_validos} valores procesados correctamente")
            
            if valores_invalidos > 0:
                st.warning(f"⚠️ {valores_invalidos} valores no válidos encontrados")
                
        except Exception as e:
            st.error(f"Error al procesar valores: {e}")
    
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
    
    def _normalize_values_fixed(self, df):
        """Normalización CORREGIDA - Preservar valores originales cuando no hay histórico"""
        try:
            if df.empty or 'Valor' not in df.columns:
                st.info("No hay valores para normalizar")
                return
            
            # Inicializar valores normalizados copiando valores originales
            df['Valor_Normalizado'] = df['Valor'].copy()
            
            # Verificar que tenemos datos válidos
            valores_validos = df['Valor'].notna()
            if not valores_validos.any():
                st.warning("⚠️ No hay valores válidos para normalizar")
                return
            
            # Contar indicadores con un solo valor ANTES del procesamiento
            indicadores_sin_historico = 0
            indicadores_con_historico = 0
            
            # Procesar cada INDICADOR individualmente (no por tipo)
            for codigo in df['Codigo'].unique():
                if pd.isna(codigo):
                    continue
                    
                mask = df['Codigo'] == codigo
                valores = df.loc[mask, 'Valor'].dropna()
                
                if valores.empty:
                    continue
                
                # Obtener información del indicador
                indicador_info = df[mask].iloc[0]
                tipo = indicador_info.get('Tipo', 'porcentaje')
                
                # REGLA PRINCIPAL: Si solo hay UN valor por indicador, NO normalizar
                # Solo usar el valor original ajustado por tipo
                if len(valores) == 1:
                    indicadores_sin_historico += 1
                    valor_original = valores.iloc[0]
                    
                    if str(tipo).lower() in ['porcentaje', 'percentage', '%']:
                        # Porcentajes: convertir a 0-1 si están en 0-100
                        if valor_original <= 1:
                            valor_norm = valor_original  # Ya está en 0-1
                        else:
                            valor_norm = valor_original / 100  # Convertir de 0-100 a 0-1
                        valor_norm = max(0, min(1, valor_norm))
                    else:
                        # Para otros tipos: MANTENER el valor original sin normalizar
                        if valor_original < 0:
                            valor_norm = 0
                        elif valor_original > 1 and str(tipo).lower() not in ['moneda', 'numero', 'cantidad']:
                            valor_norm = 1
                        else:
                            valor_norm = valor_original
                    
                    df.loc[mask, 'Valor_Normalizado'] = valor_norm
                    continue
                
                # Si hay MÚLTIPLES valores para el mismo indicador, sí normalizar
                indicadores_con_historico += 1
                
                if str(tipo).lower() in ['porcentaje', 'percentage', '%']:
                    # Porcentajes: convertir a 0-1 si están en 0-100
                    valores_norm = valores.apply(lambda x: x/100 if x > 1 else x)
                    valores_norm = valores_norm.clip(0, 1)
                    
                elif str(tipo).lower() in ['moneda', 'currency', 'dinero', 'pesos']:
                    # Valores monetarios: normalizar por máximo del indicador
                    max_val = valores.max()
                    if max_val > 0:
                        valores_norm = valores / max_val
                    else:
                        valores_norm = valores  # Mantener originales si max es 0
                    
                elif str(tipo).lower() in ['numero', 'number', 'cantidad', 'count']:
                    # Números: normalizar por máximo del indicador
                    max_val = valores.max()
                    if max_val > 0:
                        valores_norm = valores / max_val
                    else:
                        valores_norm = valores  # Mantener originales si max es 0
                    
                elif str(tipo).lower() in ['indice', 'index', 'ratio']:
                    # Índices: manejo especial
                    max_val = valores.max()
                    if max_val > 2:  # Valores grandes, normalizar
                        valores_norm = valores / max_val
                    else:  # Valores pequeños, mantener como están
                        valores_norm = valores.clip(0, 1)
                        
                else:
                    # Tipo desconocido: normalización conservadora
                    max_val = valores.max()
                    if max_val > 1:
                        valores_norm = valores / max_val
                    else:
                        valores_norm = valores.clip(0, 1)
                
                # Asignar valores normalizados
                df.loc[mask & valores_validos, 'Valor_Normalizado'] = valores_norm.clip(0, 1)
            
            # Verificar resultados
            norm_validos = df['Valor_Normalizado'].notna().sum()
            norm_min = df['Valor_Normalizado'].min()
            norm_max = df['Valor_Normalizado'].max()
            norm_promedio = df['Valor_Normalizado'].mean()
            
            # Mostrar resultados organizados
            st.success(f"✅ Normalización completada: {norm_validos} valores")
            st.info(f"Rango normalizado: {norm_min:.3f} - {norm_max:.3f}, Promedio: {norm_promedio:.3f}")
            
            if indicadores_sin_historico > 0:
                st.info(f"📊 {indicadores_sin_historico} indicadores sin histórico mantuvieron sus valores originales")
            
            if indicadores_con_historico > 0:
                st.info(f"📈 {indicadores_con_historico} indicadores con histórico fueron normalizados")
            
        except Exception as e:
            st.error(f"Error en normalización: {e}")
            # Fallback seguro: usar valores originales
            try:
                df['Valor_Normalizado'] = df['Valor'].copy()
                st.warning("⚠️ Usando valores originales como fallback")
            except:
                df['Valor_Normalizado'] = 0.5
                st.warning("⚠️ Usando valores por defecto (0.5) como fallback")
    
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
