"""
Utilidades para el manejo de datos del Dashboard ICE - SOLO GOOGLE SHEETS
"""

import pandas as pd
import streamlit as st
from config import COLUMN_MAPPING, DEFAULT_META, EXCEL_FILENAME
import openpyxl  # Para leer archivos Excel

# Importación de Google Sheets (OBLIGATORIO)
try:
    from google_sheets_manager import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    st.error("❌ **ERROR CRÍTICO:** No se puede importar GoogleSheetsManager. Instala las dependencias: `pip install gspread google-auth`")

class DataLoader:
    """Clase para cargar y procesar datos - SOLO GOOGLE SHEETS"""
    
    def __init__(self):
        self.df = None
        self.sheets_manager = None
        
        # Verificar que Google Sheets esté disponible
        if not GOOGLE_SHEETS_AVAILABLE:
            st.error("❌ **Google Sheets no disponible.** Instala dependencias: `pip install gspread google-auth`")
            return
        
        # Inicializar Google Sheets manager
        try:
            self.sheets_manager = GoogleSheetsManager()
        except Exception as e:
            st.error(f"❌ Error al inicializar Google Sheets: {e}")
            self.sheets_manager = None
    
    def load_data(self):
        """Cargar datos ÚNICAMENTE desde Google Sheets"""
        try:
            # Verificar que Google Sheets esté disponible
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ **Google Sheets no está disponible.** Instala las dependencias necesarias.")
                return self._create_empty_dataframe()
            
            if not self.sheets_manager:
                st.error("❌ **Google Sheets Manager no inicializado.** Verifica la configuración.")
                return self._create_empty_dataframe()
            
            st.info("🔄 Cargando datos desde Google Sheets...")
            
            # Cargar desde Google Sheets
            df = self.sheets_manager.load_data()
            
            if df is None:
                st.error("❌ **Error al conectar con Google Sheets.** Verifica tu configuración.")
                return self._create_empty_dataframe()
            
            if df.empty:
                st.warning("📋 **Google Sheets está vacío.** Puedes agregar datos desde la pestaña 'Gestión de Datos'.")
                return self._create_empty_dataframe()
            
            # Procesar datos
            self._process_dataframe(df)
            
            # Verificar y limpiar
            if self._verify_and_clean_dataframe(df):
                self.df = df
                st.success(f"✅ **Datos cargados desde Google Sheets:** {len(df)} registros")
                return df
            else:
                st.error("❌ **Datos inválidos en Google Sheets.** Verifica la estructura.")
                return self._create_empty_dataframe()
                
        except Exception as e:
            st.error(f"❌ **Error crítico al cargar desde Google Sheets:** {e}")
            import traceback
            with st.expander("🔧 Detalles del error"):
                st.code(traceback.format_exc())
            
            return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """Crear DataFrame vacío con estructura correcta"""
        empty_df = pd.DataFrame(columns=[
            'Linea_Accion', 'Componente', 'Categoria', 
            'Codigo', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso'
        ])
        
        # Asegurar tipos correctos
        empty_df['Valor'] = empty_df['Valor'].astype(float)
        empty_df['Meta'] = empty_df['Meta'].astype(float)
        empty_df['Peso'] = empty_df['Peso'].astype(float)
        
        return empty_df
    
    def _process_dataframe(self, df):
        """Procesar DataFrame de Google Sheets"""
        try:
            if df.empty:
                return
            
            # Renombrar columnas de Google Sheets a formato interno
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
            st.error(f"Error al procesar datos de Google Sheets: {e}")
    
    def _process_dates(self, df):
        """Procesar fechas de Google Sheets"""
        try:
            if df.empty or 'Fecha' not in df.columns:
                return
            
            # Google Sheets puede devolver fechas en diferentes formatos
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', 
                '%Y/%m/%d', '%m/%d/%Y', '%d.%m.%Y'
            ]
            
            fechas_convertidas = None
            
            for formato in date_formats:
                try:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], format=formato, errors='coerce')
                    # Si se convirtieron más del 50% de las fechas, usar este formato
                    if fechas_convertidas.notna().sum() / len(fechas_convertidas) >= 0.5:
                        break
                except:
                    continue
            
            # Si ningún formato específico funcionó, usar conversión automática
            if fechas_convertidas is None or fechas_convertidas.notna().sum() == 0:
                fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
            
            df['Fecha'] = fechas_convertidas
            
            # Reportar fechas inválidas
            fechas_invalidas = df['Fecha'].isna().sum()
            if fechas_invalidas > 0:
                st.warning(f"⚠️ {fechas_invalidas} fechas no se pudieron convertir en Google Sheets")
                
        except Exception as e:
            st.warning(f"Error al procesar fechas desde Google Sheets: {e}")
    
    def _process_values(self, df):
        """Procesar valores numéricos de Google Sheets"""
        try:
            if df.empty or 'Valor' not in df.columns:
                return
            
            # Google Sheets puede devolver valores como strings
            if df['Valor'].dtype == 'object':
                # Reemplazar comas por puntos y limpiar espacios
                df['Valor'] = (df['Valor']
                              .astype(str)
                              .str.replace(',', '.')
                              .str.replace(' ', '')
                              .str.strip())
                
                # Convertir a numérico
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            
            # Reportar valores inválidos
            valores_invalidos = df['Valor'].isna().sum()
            if valores_invalidos > 0:
                st.warning(f"⚠️ {valores_invalidos} valores no se pudieron convertir desde Google Sheets")
                
        except Exception as e:
            st.warning(f"Error al procesar valores desde Google Sheets: {e}")
    
    def _add_default_columns(self, df):
        """Añadir columnas por defecto si no existen"""
        if 'Meta' not in df.columns:
            df['Meta'] = DEFAULT_META
        if 'Peso' not in df.columns:
            df['Peso'] = 1.0
        
        # Asegurar tipos correctos
        df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce').fillna(DEFAULT_META)
        df['Peso'] = pd.to_numeric(df['Peso'], errors='coerce').fillna(1.0)
    
    def _verify_and_clean_dataframe(self, df):
        """Verificar y limpiar DataFrame de Google Sheets"""
        try:
            if df.empty:
                return True  # DataFrame vacío pero válido
            
            # Verificar columnas esenciales
            required_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ **Faltan columnas en Google Sheets:** {missing_columns}")
                st.error("**Columnas requeridas:** LINEA DE ACCIÓN, COMPONENTE PROPUESTO, CATEGORÍA, COD, Nombre de indicador, Valor, Fecha")
                st.write("**Columnas encontradas:**", list(df.columns))
                return False
            
            # Limpiar registros con datos faltantes solo en columnas críticas
            initial_count = len(df)
            df.dropna(subset=['Codigo'], inplace=True)  # Solo código es obligatorio
            final_count = len(df)
            
            if initial_count != final_count:
                st.info(f"🧹 Limpiados {initial_count - final_count} registros sin código desde Google Sheets")
            
            return True
            
        except Exception as e:
            st.error(f"Error en verificación de datos de Google Sheets: {e}")
            return False
    
    def get_data_source_info(self):
        """Obtener información sobre la fuente de datos"""
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

class DataEditor:
    """Clase para editar datos - SOLO GOOGLE SHEETS"""
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path=None):
        """Agregar un nuevo registro a Google Sheets"""
        try:
            return DataEditor._add_record_google_sheets(df, codigo, fecha, valor)
                
        except Exception as e:
            st.error(f"❌ Error al agregar registro a Google Sheets: {e}")
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path=None):
        """Actualizar un registro existente en Google Sheets"""
        try:
            return DataEditor._update_record_google_sheets(codigo, fecha, nuevo_valor)
                
        except Exception as e:
            st.error(f"❌ Error al actualizar registro en Google Sheets: {e}")
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path=None):
        """Eliminar un registro existente de Google Sheets"""
        try:
            return DataEditor._delete_record_google_sheets(codigo, fecha)
                
        except Exception as e:
            st.error(f"❌ Error al eliminar registro de Google Sheets: {e}")
            return False
    
    @staticmethod
    def _add_record_google_sheets(df, codigo, fecha, valor):
        """Agregar registro a Google Sheets"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ Google Sheets no disponible")
                return False
            
            sheets_manager = GoogleSheetsManager()
            
            # Buscar información base del indicador
            if df.empty:
                st.error(f"❌ No hay datos base disponibles para crear el registro")
                return False
            
            indicador_existente = df[df['Codigo'] == codigo]
            if indicador_existente.empty:
                st.error(f"❌ No se encontró información base para el código {codigo}")
                st.info("💡 Asegúrate de que el código existe en Google Sheets")
                return False
            
            indicador_base = indicador_existente.iloc[0]
            
            # Formatear fecha
            if hasattr(fecha, 'strftime'):
                fecha_formateada = fecha.strftime('%d/%m/%Y')
            else:
                fecha_formateada = pd.to_datetime(fecha).strftime('%d/%m/%Y')
            
            # Crear diccionario de datos para Google Sheets
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
                # Forzar recarga de cache
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
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ Google Sheets no disponible")
                return False
            
            sheets_manager = GoogleSheetsManager()
            success = sheets_manager.update_record(codigo, fecha, nuevo_valor)
            
            if success:
                # Forzar recarga de cache
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
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ Google Sheets no disponible")
                return False
            
            sheets_manager = GoogleSheetsManager()
            success = sheets_manager.delete_record(codigo, fecha)
            
            if success:
                # Forzar recarga de cache
                st.cache_data.clear()
                st.session_state.data_timestamp = st.session_state.get('data_timestamp', 0) + 1
            
            return success
            
        except Exception as e:
            st.error(f"❌ Error en Google Sheets: {e}")
            return False

    # Función de compatibilidad
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Función de compatibilidad"""
        return DataEditor.update_record(df, codigo, fecha, nuevo_valor, None)

class ExcelDataLoader:
    """Clase para cargar datos del archivo Excel con hojas metodológicas"""
    
    def __init__(self):
        import os
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.excel_path = os.path.join(self.script_dir, EXCEL_FILENAME)
        self.metodologicas_data = None
    
    def load_excel_data(self):
        """Cargar datos del Excel"""
        try:
            import os
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
