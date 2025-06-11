"""
Utilidades para el manejo de datos del Dashboard ICE - CORREGIDO PARA GOOGLE SHEETS
"""

import pandas as pd
import os
import streamlit as st
from config import COLUMN_MAPPING, DEFAULT_META, CSV_SEPARATOR, CSV_FILENAME, EXCEL_FILENAME
import openpyxl  # Para leer archivos Excel
from google_sheets_manager import GoogleSheetsManager

class DataLoader:
    """Clase para cargar y procesar datos - CORREGIDO GOOGLE SHEETS"""
    
    def __init__(self, use_google_sheets=True):
        self.df = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.script_dir, CSV_FILENAME)
        self.use_google_sheets = use_google_sheets
        self.sheets_manager = GoogleSheetsManager() if use_google_sheets else None
    
    def load_data(self):
        """Cargar datos desde Google Sheets o CSV como fallback"""
        try:
            # Intentar cargar desde Google Sheets primero
            if self.use_google_sheets and self.sheets_manager:
                st.info("🔄 Cargando desde Google Sheets...")
                df_sheets = self._load_from_google_sheets()
                
                if df_sheets is not None:
                    self.df = df_sheets
                    return self.df
                else:
                    st.warning("⚠️ Google Sheets no disponible, usando CSV como fallback")
            
            # Fallback a CSV
            st.info("🔄 Cargando desde archivo CSV...")
            df_csv = self._load_from_csv()
            
            if df_csv is not None:
                self.df = df_csv
                return self.df
            else:
                st.error("❌ No se pudieron cargar datos desde ninguna fuente")
                return None
                
        except Exception as e:
            st.error(f"❌ Error crítico en load_data: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def _load_from_google_sheets(self):
        """Cargar datos desde Google Sheets"""
        try:
            df = self.sheets_manager.load_data()
            
            if df is None:
                return None
            
            if df.empty:
                # Crear DataFrame vacío con estructura correcta
                empty_df = pd.DataFrame(columns=[
                    "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha"
                ])
                self._process_dataframe(empty_df)
                st.warning("📋 Google Sheets conectado pero vacío")
                return empty_df
            
            # Procesar datos igual que CSV
            self._process_dataframe(df)
            
            # Verificar y limpiar
            if self._verify_and_clean_dataframe(df):
                st.success(f"✅ Datos cargados desde Google Sheets: {len(df)} registros")
                return df
            else:
                return None
                
        except Exception as e:
            st.warning(f"⚠️ Error al cargar desde Google Sheets: {e}")
            import traceback
            with st.expander("🔧 Debug: Error Google Sheets", expanded=False):
                st.code(traceback.format_exc())
            return None
    
    def _load_from_csv(self):
        """Cargar datos desde CSV (método original mantenido)"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.csv_path):
                st.error(f"❌ Archivo CSV no encontrado: {self.csv_path}")
                return None
            
            # Código original del CSV
            self.df = pd.read_csv(self.csv_path, sep=CSV_SEPARATOR, encoding='utf-8')
            
            # Debug info
            with st.expander("🔧 Debug: CSV cargado", expanded=False):
                st.write(f"**Archivo:** {self.csv_path}")
                st.write(f"**Shape:** {self.df.shape}")
                st.write(f"**Columnas:** {list(self.df.columns)}")
                if not self.df.empty:
                    st.dataframe(self.df.head(3))
            
            # Procesar datos
            self._process_dataframe(self.df)
            
            # Verificar y limpiar
            if self._verify_and_clean_dataframe(self.df):
                st.success(f"✅ Datos cargados desde CSV: {len(self.df)} registros")
                return self.df
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ Error al cargar CSV: {e}")
            return None
    
    def _process_dataframe(self, df):
        """Procesar DataFrame (común para Google Sheets y CSV)"""
        try:
            if df.empty:
                return
            
            # Renombrar columnas
            for original, nuevo in COLUMN_MAPPING.items():
                if original in df.columns:
                    df.rename(columns={original: nuevo}, inplace=True)
            
            # Procesar fechas
            self._process_dates(df)
            
            # Procesar valores
            self._process_values(df)
            
            # Añadir columnas por defecto
            self._add_default_columns(df)
            
        except Exception as e:
            st.error(f"Error al procesar DataFrame: {e}")
    
    def _verify_and_clean_dataframe(self, df):
        """Verificar y limpiar DataFrame"""
        try:
            if df.empty:
                # Si está vacío pero tiene la estructura correcta, está bien
                required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
                if all(col in df.columns for col in required_columns):
                    return True
                return False
            
            # Verificar columnas esenciales
            required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Faltan columnas: {missing_columns}")
                st.write("**Columnas disponibles:**", list(df.columns))
                return False
            
            # Limpiar datos problemáticos
            initial_count = len(df)
            df.dropna(subset=['Codigo', 'Fecha', 'Valor'], inplace=True)
            final_count = len(df)
            
            if initial_count != final_count:
                st.info(f"🧹 Limpiados {initial_count - final_count} registros con datos faltantes")
            
            if df.empty:
                st.warning("⚠️ No hay datos válidos después de la limpieza")
                return True  # Permitir DataFrames vacíos pero con estructura correcta
            
            return True
            
        except Exception as e:
            st.error(f"Error en verificación: {e}")
            return False
    
    def _process_dates(self, df):
        """Procesar fechas (método mejorado)"""
        try:
            if df.empty or 'Fecha' not in df.columns:
                return
            
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', 
                '%Y/%m/%d', '%m/%d/%Y', '%d.%m.%Y'
            ]
            
            fechas_convertidas = None
            
            for formato in date_formats:
                try:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], format=formato, errors='coerce')
                    porcentaje_validas = (fechas_convertidas.notna().sum() / len(fechas_convertidas)) * 100
                    
                    if porcentaje_validas >= 50:
                        break
                except ValueError:
                    continue
            
            if fechas_convertidas is None:
                fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
            
            df['Fecha'] = fechas_convertidas
            
            # Contar fechas inválidas
            fechas_invalidas = df['Fecha'].isna().sum()
            if fechas_invalidas > 0:
                st.warning(f"⚠️ {fechas_invalidas} fechas no se pudieron convertir")
                
        except Exception as e:
            st.warning(f"Error al procesar fechas: {e}")
    
    def _process_values(self, df):
        """Procesar valores numéricos"""
        try:
            if df.empty or 'Valor' not in df.columns:
                return
            
            if df['Valor'].dtype == 'object':
                # Limpiar y convertir valores
                df['Valor'] = df['Valor'].astype(str).str.replace(',', '.').str.strip()
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
                
        except Exception as e:
            st.warning(f"Error al procesar valores: {e}")
    
    def _add_default_columns(self, df):
        """Añadir columnas por defecto"""
        if 'Meta' not in df.columns:
            df['Meta'] = DEFAULT_META
        if 'Peso' not in df.columns:
            df['Peso'] = 1.0
    
    def get_data_source_info(self):
        """Obtener información sobre la fuente de datos"""
        if self.use_google_sheets and self.sheets_manager:
            return {
                'source': 'Google Sheets',
                'connection_info': self.sheets_manager.get_connection_info()
            }
        else:
            return {
                'source': 'CSV',
                'csv_path': self.csv_path
            }

# MANTENER TODAS LAS CLASES ORIGINALES SIN CAMBIOS
class DataProcessor:
    """Clase para procesar y calcular métricas de los datos"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes usando SIEMPRE el valor más reciente de cada indicador."""
        try:
            if df.empty:
                st.info("📋 No hay datos disponibles para calcular puntajes")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # SIEMPRE usar el valor más reciente de cada indicador
            df_filtrado = DataProcessor._get_latest_values_by_indicator(df)

            if len(df_filtrado) == 0:
                st.info("📋 No hay datos para calcular puntajes")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # Verificar columnas esenciales
            required_columns = ['Valor', 'Peso', 'Componente', 'Categoria']
            missing_columns = [col for col in required_columns if col not in df_filtrado.columns]
            if missing_columns:
                st.error(f"Faltan columnas esenciales: {missing_columns}")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # Normalizar valores (0-1)
            df_filtrado['Valor_Normalizado'] = df_filtrado['Valor'].clip(0, 1)
            
            # Verificar que tenemos datos después de la normalización
            if df_filtrado['Valor_Normalizado'].isna().all():
                st.error("Todos los valores normalizados son NaN")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Calcular puntajes por componente
            try:
                puntajes_componente = DataProcessor._calculate_weighted_average_by_group(
                    df_filtrado, 'Componente'
                )
            except Exception as e:
                st.error(f"Error al calcular puntajes por componente: {e}")
                puntajes_componente = pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []})
            
            # Calcular puntajes por categoría
            try:
                puntajes_categoria = DataProcessor._calculate_weighted_average_by_group(
                    df_filtrado, 'Categoria'
                )
            except Exception as e:
                st.error(f"Error al calcular puntajes por categoría: {e}")
                puntajes_categoria = pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []})
            
            # Calcular puntaje general
            try:
                peso_total = df_filtrado['Peso'].sum()
                if peso_total > 0:
                    puntaje_general = (df_filtrado['Valor_Normalizado'] * df_filtrado['Peso']).sum() / peso_total
                else:
                    puntaje_general = df_filtrado['Valor_Normalizado'].mean()
                
                # Verificar que el puntaje general es válido
                if pd.isna(puntaje_general):
                    puntaje_general = 0.0
                    
            except Exception as e:
                st.error(f"Error al calcular puntaje general: {e}")
                puntaje_general = 0.0

            return puntajes_componente, puntajes_categoria, puntaje_general
            
        except Exception as e:
            st.error(f"Error crítico en calculate_scores: {e}")
            import traceback
            st.code(traceback.format_exc())
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
    
    @staticmethod
    def _get_latest_values_by_indicator(df):
        """Obtener el valor más reciente de cada indicador."""
        try:
            if df.empty:
                return df
            
            # Verificar que tenemos las columnas necesarias
            required_columns = ['Codigo', 'Fecha', 'Valor']
            if not all(col in df.columns for col in required_columns):
                st.error(f"Faltan columnas requeridas: {required_columns}")
                return df
            
            # Remover filas con valores NaN en columnas críticas
            df_clean = df.dropna(subset=['Codigo', 'Fecha', 'Valor']).copy()
            
            if df_clean.empty:
                return df
            
            # Usar sort_values y groupby para obtener valores más recientes
            df_latest = (df_clean
                        .sort_values(['Codigo', 'Fecha'])
                        .groupby('Codigo', as_index=False)
                        .last()
                        .reset_index(drop=True))
            
            return df_latest
            
        except Exception as e:
            st.error(f"Error al obtener valores más recientes: {e}")
            return df
    
    @staticmethod
    def _calculate_weighted_average_by_group(df, group_column):
        """Calcular promedio ponderado por grupo"""
        try:
            if df.empty:
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            if group_column not in df.columns:
                st.error(f"La columna '{group_column}' no existe en los datos")
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            # Verificar que tenemos las columnas necesarias
            required_cols = ['Valor_Normalizado', 'Peso']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Faltan columnas necesarias: {missing_cols}")
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            # Función para calcular promedio ponderado
            def weighted_avg(valores, pesos):
                mask = pd.notna(valores) & pd.notna(pesos)
                if not mask.any():
                    return 0.0
                
                valores_clean = valores[mask]
                pesos_clean = pesos[mask]
                peso_total = pesos_clean.sum()
                
                if peso_total > 0:
                    return (valores_clean * pesos_clean).sum() / peso_total
                else:
                    return valores_clean.mean() if len(valores_clean) > 0 else 0.0
            
            # Calcular promedio ponderado por grupo
            result = df.groupby(group_column).agg({
                'Valor_Normalizado': list,
                'Peso': list
            }).reset_index()
            
            result['Puntaje_Ponderado'] = result.apply(
                lambda row: weighted_avg(
                    pd.Series(row['Valor_Normalizado']), 
                    pd.Series(row['Peso'])
                ), axis=1
            )
            
            return result[[group_column, 'Puntaje_Ponderado']]
            
        except Exception as e:
            st.error(f"Error en cálculo ponderado por {group_column}: {e}")
            return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
    
    @staticmethod
    def create_pivot_table(df, fecha=None, filas='Categoria', columnas='Componente', valores='Valor'):
        """Crear tabla dinámica (función legacy)"""
        return pd.DataFrame()

class DataEditor:
    """Clase para editar datos - CORREGIDO PARA GOOGLE SHEETS"""
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path=None):
        """Agregar un nuevo registro - CORREGIDO"""
        try:
            # Determinar si usar Google Sheets o CSV
            use_sheets = DataEditor._should_use_google_sheets()
            
            if use_sheets:
                return DataEditor._add_record_google_sheets(df, codigo, fecha, valor)
            else:
                return DataEditor._add_record_csv(df, codigo, fecha, valor, csv_path)
                
        except Exception as e:
            st.error(f"❌ Error al agregar registro: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path=None):
        """Actualizar un registro existente - CORREGIDO"""
        try:
            use_sheets = DataEditor._should_use_google_sheets()
            
            if use_sheets:
                return DataEditor._update_record_google_sheets(codigo, fecha, nuevo_valor)
            else:
                return DataEditor._update_record_csv(df, codigo, fecha, nuevo_valor, csv_path)
                
        except Exception as e:
            st.error(f"❌ Error al actualizar registro: {e}")
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path=None):
        """Eliminar un registro existente - CORREGIDO"""
        try:
            use_sheets = DataEditor._should_use_google_sheets()
            
            if use_sheets:
                return DataEditor._delete_record_google_sheets(codigo, fecha)
            else:
                return DataEditor._delete_record_csv(df, codigo, fecha, csv_path)
                
        except Exception as e:
            st.error(f"❌ Error al eliminar registro: {e}")
            return False
    
    @staticmethod
    def _should_use_google_sheets():
        """Determinar si debe usar Google Sheets"""
        try:
            return ("google_sheets" in st.secrets and 
                    "spreadsheet_url" in st.secrets["google_sheets"])
        except:
            return False
    
    @staticmethod
    def _add_record_google_sheets(df, codigo, fecha, valor):
        """Agregar registro a Google Sheets"""
        try:
            sheets_manager = GoogleSheetsManager()
            
            # Buscar información base del indicador
            if df.empty:
                st.error(f"❌ No hay datos base disponibles para crear el registro")
                return False
            
            indicador_existente = df[df['Codigo'] == codigo]
            if indicador_existente.empty:
                st.error(f"❌ No se encontró información base para el código {codigo}")
                st.info("💡 Asegúrate de que el código existe en los datos actuales")
                return False
            
            indicador_base = indicador_existente.iloc[0]
            
            # Formatear fecha
            if hasattr(fecha, 'strftime'):
                fecha_formateada = fecha.strftime('%d/%m/%Y')
            else:
                fecha_formateada = pd.to_datetime(fecha).strftime('%d/%m/%Y')
            
            # Crear diccionario de datos con los nombres correctos para Google Sheets
            data_dict = {
                'LINEA DE ACCIÓN': indicador_base.get('Linea_Accion', ''),
                'COMPONENTE PROPUESTO': indicador_base.get('Componente', ''),
                'CATEGORÍA': indicador_base.get('Categoria', ''),
                'COD': codigo,
                'Nombre de indicador': indicador_base.get('Indicador', ''),
                'Valor': valor,
                'Fecha': fecha_formateada
            }
            
            # Agregar a Google Sheets
            success = sheets_manager.add_record(data_dict)
            
            if success:
                # Forzar recarga de cache SIN cambiar pestaña
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
            
            return success
            
        except Exception as e:
            st.error(f"❌ Error en Google Sheets: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    @staticmethod
    def _update_record_google_sheets(codigo, fecha, nuevo_valor):
        """Actualizar registro en Google Sheets"""
        try:
            sheets_manager = GoogleSheetsManager()
            success = sheets_manager.update_record(codigo, fecha, nuevo_valor)
            
            if success:
                # Forzar recarga de cache SIN cambiar pestaña
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
            
            return success
            
        except Exception as e:
            st.error(f"❌ Error en Google Sheets: {e}")
            return False
    
    @staticmethod
    def _delete_record_google_sheets(codigo, fecha):
        """Eliminar registro de Google Sheets"""
        try:
            sheets_manager = GoogleSheetsManager()
            success = sheets_manager.delete_record(codigo, fecha)
            
            if success:
                # Forzar recarga de cache SIN cambiar pestaña
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
            
            return success
            
        except Exception as e:
            st.error(f"❌ Error en Google Sheets: {e}")
            return False
    
    # Métodos CSV originales mantenidos...
    @staticmethod
    def _add_record_csv(df, codigo, fecha, valor, csv_path):
        """Agregar registro a CSV (método original)"""
        try:
            if not csv_path:
                st.error("❌ No se especificó ruta del archivo CSV")
                return False
            
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            
            codigo_col = 'COD' if 'COD' in df_actual.columns else 'Codigo'
            if codigo_col not in df_actual.columns:
                st.error("❌ No se encontró columna de código")
                return False
            
            indicadores_existentes = df_actual[df_actual[codigo_col] == codigo]
            if len(indicadores_existentes) == 0:
                st.error(f"❌ No se encontró información base para {codigo}")
                return False
                
            indicador_base = indicadores_existentes.iloc[0]
            
            fecha_formateada = fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else pd.to_datetime(fecha).strftime('%d/%m/%Y')
            
            nueva_fila = {}
            for col in df_actual.columns:
                if col == 'Fecha':
                    nueva_fila[col] = fecha_formateada
                elif col == 'Valor':
                    nueva_fila[col] = valor
                else:
                    nueva_fila[col] = indicador_base[col]
            
            df_nuevo = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
            
            st.cache_data.clear()
            st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar a CSV: {e}")
            return False
    
    @staticmethod
    def _update_record_csv(df, codigo, fecha, nuevo_valor, csv_path):
        """Actualizar registro en CSV (método original)"""
        try:
            if not csv_path:
                return False
            
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')
            
            codigo_col = 'COD' if 'COD' in df_actual.columns else 'Codigo'
            idx = df_actual[(df_actual[codigo_col] == codigo) & (df_actual['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                df_actual.loc[idx, 'Valor'] = nuevo_valor
                df_actual.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                return True
            else:
                st.error(f"❌ No se encontró registro para actualizar")
                return False
                
        except Exception as e:
            st.error(f"❌ Error al actualizar CSV: {e}")
            return False
    
    @staticmethod
    def _delete_record_csv(df, codigo, fecha, csv_path):
        """Eliminar registro de CSV (método original)"""
        try:
            if not csv_path:
                return False
            
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')
            
            codigo_col = 'COD' if 'COD' in df_actual.columns else 'Codigo'
            idx = df_actual[(df_actual[codigo_col] == codigo) & (df_actual['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                df_nuevo = df_actual.drop(idx).reset_index(drop=True)
                df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
                return True
            else:
                st.error(f"❌ No se encontró registro para eliminar")
                return False
                
        except Exception as e:
            st.error(f"❌ Error al eliminar de CSV: {e}")
            return False

    # Función de compatibilidad
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Función de compatibilidad"""
        return DataEditor.update_record(df, codigo, fecha, nuevo_valor, csv_path)

# MANTENER CLASE EXCEL ORIGINAL
class ExcelDataLoader:
    """Clase para cargar datos del archivo Excel con hojas metodológicas"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.excel_path = os.path.join(self.script_dir, "Batería de indicadores.xlsx")
        self.metodologicas_data = None
    
    def load_excel_data(self):
        """Cargar datos del Excel"""
        try:
            if not os.path.exists(self.excel_path):
                return None
            
            df_metodologicas = pd.read_excel(
                self.excel_path, 
                sheet_name="Hoja metodológica indicadores",
                header=1
            )
            
            column_mapping = {
                'C1_ID': 'Codigo',
                'C2_Nombre indicador': 'Nombre_Indicador',
                'C3_Definición': 'Definicion',
                'C4_Objetivo': 'Objetivo',
                'C5_Área temática': 'Area_Tematica',
                'C6_Tema': 'Tema',
                'C7_Soporte Legal': 'Soporte_Legal',
                'C8_Fórmula de cálculo': 'Formula_Calculo',
                'C9_Variables': 'Variables',
                'C10_Unidad de medida': 'Unidad_Medida',
                'C11_Fuente de Información': 'Fuente_Informacion',
                'C12_Tipo de indicador': 'Tipo_Indicador',
                'C13_Periodicidad ': 'Periodicidad',
                'C14_Desagregación Geográfica': 'Desagregacion_Geografica',
                'Metodología de cálculo': 'Metodologia_Calculo',
                'C15_Desagregación poblacional-diferencial': 'Desagregacion_Poblacional',
                'C16_Observaciones / Notas Técnicas': 'Observaciones',
                'Clasificación según calidad': 'Clasificacion_Calidad',
                'Clasificación según nivel de intervención': 'Clasificacion_Intervencion',
                'Tipo de acumulación': 'Tipo_Acumulacion',
                'C17_Enlaces web relacionados': 'Enlaces_Web',
                'Interpretación': 'Interpretacion',
                'Limitaciones': 'Limitaciones',
                'C18_Sector': 'Sector',
                'C19_Entidad': 'Entidad',
                'C20_Dependencia': 'Dependencia',
                'C21_Directivo/a Responsable': 'Directivo_Responsable',
                'C22_Correo electrónico del directivo': 'Correo_Directivo',
                'C23_Teléfono de contacto': 'Telefono_Contacto'
            }
            
            # Renombrar columnas existentes
            for old_name, new_name in column_mapping.items():
                if old_name in df_metodologicas.columns:
                    df_metodologicas = df_metodologicas.rename(columns={old_name: new_name})
            
            # Limpiar datos vacíos
            df_metodologicas = df_metodologicas.dropna(subset=['Codigo'])
            
            self.metodologicas_data = df_metodologicas
            st.success(f"✅ Datos del Excel cargados: {len(df_metodologicas)} indicadores metodológicos")
            return df_metodologicas
            
        except Exception as e:
            st.error(f"Error al cargar datos del Excel: {e}")
            return None
    
    def get_indicator_data(self, codigo):
        """Obtener datos de un indicador específico por código"""
        if self.metodologicas_data is None:
            self.load_excel_data()
        
        if self.metodologicas_data is None:
            return None
        
        try:
            # Buscar el indicador por código
            indicator_data = self.metodologicas_data[
                self.metodologicas_data['Codigo'] == codigo
            ]
            
            if len(indicator_data) > 0:
                return indicator_data.iloc[0].to_dict()
            else:
                return None
                
        except Exception as e:
            st.error(f"Error al obtener datos del indicador {codigo}: {e}")
            return None
                
        except Exception as e:
            st.error(f"Error al obtener datos del indicador {codigo}: {e}")
            return None
