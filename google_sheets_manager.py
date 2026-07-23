"""
Gestor de Google Sheets - VERSIÓN CON PESTAÑA FICHAS METODOLÓGICAS
NUEVA FUNCIONALIDAD: Cargar fichas metodológicas desde Google Sheets
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import time

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

class GoogleSheetsManager:
    """Gestor de Google Sheets - CON PESTAÑA FICHAS"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.fichas_worksheet = None  # NUEVA: Worksheet para fichas metodológicas
        self.spreadsheet_url = None
        self.worksheet_name = "IndicadoresICE"
        self.fichas_worksheet_name = "Fichas"  # NUEVA: Nombre de la pestaña de fichas
        self.connected = False
        self.timeout = 30
        
    def setup_credentials(self):
        """Configurar credenciales - CON TIMEOUT"""
        try:
            if not GSPREAD_AVAILABLE:
                st.error("📦 **Instalar:** `pip install gspread google-auth`")
                return False
            
            # Verificar configuración
            if "google_sheets" not in st.secrets:
                st.error("❌ Configuración de Google Sheets no encontrada en secrets.toml")
                return False
            
            # Crear credenciales
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials_info = dict(st.secrets["google_sheets"])
            self.spreadsheet_url = credentials_info.pop("spreadsheet_url", None)
            
            if not self.spreadsheet_url:
                st.error("❌ Falta 'spreadsheet_url' en la configuración")
                return False
            
            # NUEVO: Timeout en creación de credenciales
            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=scope
            )
            
            # NUEVO: Timeout en autorización
            self.gc = gspread.authorize(credentials)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error en credenciales: {e}")
            return False
    
    def connect_to_sheet(self):
        """Conectar a Google Sheets - CON TIMEOUT Y FICHAS"""
        try:
            if not self.gc and not self.setup_credentials():
                return False
            
            # NUEVO: Timeout en conexión
            start_time = time.time()
            
            # Abrir hoja con timeout
            self.sheet = self.gc.open_by_url(self.spreadsheet_url)
            
            # Verificar timeout
            if time.time() - start_time > self.timeout:
                st.error("❌ Timeout al conectar con Google Sheets")
                return False
            
            # Obtener o crear worksheet principal
            try:
                self.worksheet = self.sheet.worksheet(self.worksheet_name)
            except gspread.WorksheetNotFound:
                # Crear worksheet si no existe
                self.worksheet = self.sheet.add_worksheet(
                    title=self.worksheet_name, rows=1000, cols=10
                )
                # Agregar headers
                headers = [
                    "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha", "Tipo"
                ]
                self.worksheet.append_row(headers)
            
            # NUEVO: Obtener o crear worksheet de fichas metodológicas
            try:
                self.fichas_worksheet = self.sheet.worksheet(self.fichas_worksheet_name)
                
            except gspread.WorksheetNotFound:
                st.warning("⚠️ Pestaña 'Fichas' no encontrada. Creando...")
                # Crear worksheet de fichas
                self.fichas_worksheet = self.sheet.add_worksheet(
                    title=self.fichas_worksheet_name, rows=1000, cols=50
                )
                # Agregar headers de fichas metodológicas
                fichas_headers = [
                    'Codigo', 'Nombre_Indicador', 'Definicion', 'Objetivo', 'Area_Tematica', 
                    'Tema', 'Sector', 'Entidad', 'Dependencia', 'Formula_Calculo', 
                    'Variables', 'Unidad_Medida', 'Metodologia_Calculo', 'Tipo_Acumulacion',
                    'Fuente_Informacion', 'Tipo_Indicador', 'Periodicidad', 'Desagregacion_Geografica',
                    'Desagregacion_Poblacional', 'Clasificacion_Calidad', 'Clasificacion_Intervencion',
                    'Observaciones', 'Limitaciones', 'Interpretacion', 'Directivo_Responsable',
                    'Correo_Directivo', 'Telefono_Contacto', 'Enlaces_Web', 'Soporte_Legal'
                ]
                self.fichas_worksheet.append_row(fichas_headers)
                st.info("✅ Pestaña 'Fichas' creada con estructura metodológica")
            
            self.connected = True
            return True
            
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
            # NUEVO: Información adicional sobre el error
            if "timeout" in str(e).lower():
                st.error("⏰ **Timeout:** Conexión muy lenta. Verifica tu internet.")
            elif "permission" in str(e).lower():
                st.error("🔒 **Permisos:** Verifica que el Service Account tenga acceso.")
            elif "not found" in str(e).lower():
                st.error("📋 **Hoja no encontrada:** Verifica la URL de Google Sheets.")
            
            self.connected = False
            return False
    
    def load_data(self):
        """Cargar datos - CON TIMEOUT Y RETRY"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if not self.connected and not self.connect_to_sheet():
                    if attempt < max_retries - 1:
                        st.warning(f"⏳ Intento {attempt + 1}/{max_retries} fallido, reintentando...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return None
                
                # NUEVO: Timeout en lectura de datos
                start_time = time.time()
                
                # Obtener datos con timeout
                data = self.worksheet.get_all_records()
                
                # Verificar timeout
                if time.time() - start_time > self.timeout:
                    st.error("❌ Timeout al leer datos de Google Sheets")
                    return None
                
                if not data:
                    st.info("📋 Google Sheets está vacío")
                    return pd.DataFrame(columns=[
                        "COMPONENTE PROPUESTO", "CATEGORÍA", 
                        "COD", "Nombre de indicador", "Valor", "Fecha", "Tipo"
                    ])
                
                df = pd.DataFrame(data)
                return df
                
            except Exception as e:
                st.error(f"❌ Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    st.error("❌ Se agotaron todos los intentos")
                    return None
        
        return None
    
    def load_fichas_data(self):
        """NUEVO: Cargar datos de fichas metodológicas desde Google Sheets"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if not self.connected and not self.connect_to_sheet():
                    if attempt < max_retries - 1:
                        st.warning(f"⏳ Intento {attempt + 1}/{max_retries} para fichas, reintentando...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return None
                
                if not self.fichas_worksheet:
                    st.warning("⚠️ No hay pestaña 'Fichas' disponible")
                    return pd.DataFrame()
                
                # Timeout en lectura de fichas
                start_time = time.time()
                
                # Obtener datos de fichas
                fichas_data = self.fichas_worksheet.get_all_records()
                
                # Verificar timeout
                if time.time() - start_time > self.timeout:
                    st.error("❌ Timeout al leer fichas metodológicas")
                    return None
                
                if not fichas_data:
                    st.info("📋 Pestaña 'Fichas' está vacía")
                    return pd.DataFrame()
                
                fichas_df = pd.DataFrame(fichas_data)

                # Limpiar datos vacíos usando COD
                if not fichas_df.empty and 'COD' in fichas_df.columns:
                    fichas_df = fichas_df.dropna(subset=['COD'], how='all')

                return fichas_df
                
            except Exception as e:
                st.error(f"❌ Error al cargar fichas en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Reintentando fichas en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    st.error("❌ Se agotaron todos los intentos para fichas")
                    return None
        
        return None

    def load_combined_data(self):
        """
        NUEVO: Cargar datos combinados de IndicadoresICE y Fichas
        Hace JOIN entre ambas tablas usando COD/Codigo
        Los metadatos (componente, categoría, tipo) vienen de Fichas
        Los valores y fechas vienen de IndicadoresICE
        """
        try:
            # Cargar ambas tablas
            df_indicadores = self.load_data()
            df_fichas = self.load_fichas_data()

            if df_indicadores is None:
                st.error("❌ No se pudieron cargar los datos de IndicadoresICE")
                return None

            if df_fichas is None or df_fichas.empty:
                st.warning("⚠️ No hay datos en Fichas. Usando datos de IndicadoresICE tal cual.")
                return df_indicadores

            # Limpiar nombres de columnas
            df_indicadores.columns = df_indicadores.columns.str.strip()
            df_fichas.columns = df_fichas.columns.str.strip()


            # Verificar que existen las columnas necesarias
            if 'COD' not in df_indicadores.columns:
                st.error("❌ Columna 'COD' no encontrada en IndicadoresICE")
                return df_indicadores

            if 'COD' not in df_fichas.columns:
                st.error("❌ Columna 'COD' no encontrada en Fichas")
                return df_indicadores

            # Limpiar códigos para el JOIN (ambas tablas usan COD)
            df_indicadores['COD_clean'] = df_indicadores['COD'].astype(str).str.strip()
            df_fichas['COD_clean'] = df_fichas['COD'].astype(str).str.strip()

            # Seleccionar columnas relevantes de Fichas
            fichas_cols = ['COD_clean', 'Componente', 'Categoría',
                          'Tipo_Indicador', 'Nombre_Indicador', 'Meta', 'Peso', 'VPN',
                          'Definicion', 'Unidad_Medida', 'Metodologia_Calculo', 'Calculo']

            # Verificar qué columnas existen en Fichas
            available_fichas_cols = ['COD_clean']
            for col in fichas_cols[1:]:
                if col in df_fichas.columns:
                    available_fichas_cols.append(col)

            df_fichas_subset = df_fichas[available_fichas_cols].copy()

            # Renombrar columnas de Fichas para que coincidan con el formato esperado
            rename_dict = {
                'Componente': 'COMPONENTE PROPUESTO',
                'Categoría': 'CATEGORÍA',
                'Tipo_Indicador': 'Tipo',
                'Nombre_Indicador': 'Nombre_Indicador_Ficha'
            }
            df_fichas_subset = df_fichas_subset.rename(columns=rename_dict)

            # Hacer LEFT JOIN usando COD en ambas tablas
            df_combined = df_indicadores.merge(
                df_fichas_subset,
                left_on='COD_clean',
                right_on='COD_clean',
                how='left',
                suffixes=('_ind', '_ficha')
            )

            # Normalizar nombres de columnas después del merge
            rename_map = {
                'Componente': 'COMPONENTE PROPUESTO',
                'Categoria': 'Categoría',
                'Código': 'COD',
                'Codigo': 'COD'  # También sin acento
            }
            for old_name, new_name in rename_map.items():
                if old_name in df_combined.columns:
                    df_combined = df_combined.rename(columns={old_name: new_name})

            # Priorizar metadatos de Fichas sobre IndicadoresICE
            # Si existe el valor en Fichas, usarlo; si no, mantener el de IndicadoresICE

            for col in ['COMPONENTE PROPUESTO', 'Categoría', 'Tipo']:
                if col in df_combined.columns:
                    # Si tenemos columna duplicada (_ind y _ficha), usar _ficha cuando esté disponible
                    col_ind = f"{col}_ind"
                    col_ficha = f"{col}_ficha"

                    if col_ind in df_combined.columns and col_ficha in df_combined.columns:
                        # Usar valor de Fichas si está disponible, sino usar el de Indicadores
                        df_combined[col] = df_combined[col_ficha].fillna(df_combined[col_ind])
                        # Eliminar columnas duplicadas
                        df_combined = df_combined.drop(columns=[col_ind, col_ficha])
                    elif col_ficha in df_combined.columns:
                        # Solo existe _ficha (no había en indicadores)
                        df_combined[col] = df_combined[col_ficha]
                        df_combined = df_combined.drop(columns=[col_ficha])

            # Renombrar Nombre_Indicador_Ficha a "Nombre de indicador" y luego a "Indicador"
            if 'Nombre_Indicador_Ficha' in df_combined.columns:
                df_combined = df_combined.rename(columns={'Nombre_Indicador_Ficha': 'Indicador'})
            elif 'Nombre_Indicador' in df_combined.columns:
                df_combined = df_combined.rename(columns={'Nombre_Indicador': 'Indicador'})

            # Eliminar COD_clean si existe COD
            if 'COD_clean' in df_combined.columns:
                df_combined = df_combined.drop(columns=['COD_clean'], errors='ignore')

            # Verificar que no haya duplicados en los nombres de columnas
            if df_combined.columns.duplicated().any():
                df_combined = df_combined.loc[:, ~df_combined.columns.duplicated(keep='first')]

            # Asegurar que CATEGORÍA tiene el nombre correcto
            if 'Categoría' in df_combined.columns and 'CATEGORÍA' not in df_combined.columns:
                df_combined = df_combined.rename(columns={'Categoría': 'CATEGORÍA'})

            # Reordenar columnas al formato esperado
            expected_cols = ['COMPONENTE PROPUESTO', 'CATEGORÍA',
                           'COD', 'Indicador', 'Tipo', 'Valor', 'Fecha']

            # Mantener solo las columnas que existen
            final_cols = [col for col in expected_cols if col in df_combined.columns]

            # Agregar columnas adicionales que no estén en expected_cols
            extra_cols = [col for col in df_combined.columns if col not in final_cols]
            final_cols.extend(extra_cols)

            df_combined = df_combined[final_cols]

            # ✅ NORMALIZAR nombres de columnas para compatibilidad con calculate_scores
            column_standardization = {
                'COMPONENTE PROPUESTO': 'Componente',
                'CATEGORÍA': 'Categoria'
            }

            for original, standard in column_standardization.items():
                if original in df_combined.columns:
                    df_combined = df_combined.rename(columns={original: standard})

            st.success(f"✅ Datos combinados: {len(df_combined)} registros de IndicadoresICE con metadatos de Fichas")

            return df_combined

        except Exception as e:
            st.error(f"❌ Error al combinar datos: {e}")
            import traceback
            st.error(traceback.format_exc())
            # En caso de error, devolver datos de IndicadoresICE sin combinar
            return self.load_data()

    def add_ficha_record(self, ficha_data_dict):
        """NUEVO: Agregar ficha metodológica"""
        try:
            if not self.connected and not self.connect_to_sheet():
                st.error("❌ No se pudo conectar a Google Sheets")
                return False
            
            if not self.fichas_worksheet:
                st.error("❌ No hay pestaña 'Fichas' disponible")
                return False
            
            if not ficha_data_dict:
                st.error("❌ No hay datos de ficha para agregar")
                return False
            
            # Timeout en operación
            start_time = time.time()
            
            # Obtener headers de fichas
            fichas_headers = self.fichas_worksheet.row_values(1)
            if not fichas_headers:
                st.error("❌ No hay headers en la pestaña 'Fichas'")
                return False
            
            # Crear fila con orden correcto
            nueva_fila_ficha = []
            for header in fichas_headers:
                valor = ""
                if header in ficha_data_dict:
                    valor = str(ficha_data_dict[header])
                nueva_fila_ficha.append(valor)
            
            # Verificar timeout antes de agregar
            if time.time() - start_time > self.timeout:
                st.error("❌ Timeout al preparar datos de ficha")
                return False
            
            # Agregar fila
            self.fichas_worksheet.append_row(nueva_fila_ficha)
            
            # Verificar que se completó en tiempo
            if time.time() - start_time > self.timeout:
                st.warning("⚠️ Operación lenta, pero posiblemente exitosa")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar ficha: {e}")
            return False
    
    def update_ficha_record(self, codigo, campo, nuevo_valor):
        """NUEVO: Actualizar campo de ficha metodológica"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            if not self.fichas_worksheet:
                st.error("❌ No hay pestaña 'Fichas' disponible")
                return False
            
            # Timeout en operación
            start_time = time.time()
            
            # Obtener datos de fichas
            fichas_data = self.fichas_worksheet.get_all_records()
            
            # Verificar timeout
            if time.time() - start_time > self.timeout / 2:
                st.warning("⚠️ Operación lenta...")
            
            # Buscar ficha por código
            row_to_update = None
            for i, row in enumerate(fichas_data, start=2):
                if str(row.get('Codigo', '')).strip() == str(codigo).strip():
                    row_to_update = i
                    break
            
            if row_to_update is None:
                st.error("❌ Ficha no encontrada")
                return False
            
            # Encontrar columna del campo
            headers = self.fichas_worksheet.row_values(1)
            campo_col = None
            for j, header in enumerate(headers, start=1):
                if header.lower() == campo.lower():
                    campo_col = j
                    break
            
            if campo_col is None:
                st.error(f"❌ Campo '{campo}' no encontrado")
                return False
            
            # Actualizar
            self.fichas_worksheet.update_cell(row_to_update, campo_col, nuevo_valor)
            
            # Verificar timeout final
            if time.time() - start_time > self.timeout:
                st.warning("⚠️ Operación completada pero lenta")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            st.error(f"❌ Error al actualizar ficha: {e}")
            return False
    
    def add_record(self, data_dict):
        """Agregar registro - CON TIMEOUT"""
        try:
            if not self.connected and not self.connect_to_sheet():
                st.error("❌ No se pudo conectar a Google Sheets")
                return False
            
            if not data_dict:
                st.error("❌ No hay datos para agregar")
                return False
            
            # NUEVO: Timeout en operación
            start_time = time.time()
            
            # Obtener headers
            headers = self.worksheet.row_values(1)
            if not headers:
                headers = [
                    "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha", "Tipo"
                ]
                self.worksheet.append_row(headers)
            
            # Crear fila con orden correcto
            nueva_fila = []
            for header in headers:
                valor = ""
                if header in data_dict:
                    valor = str(data_dict[header])
                nueva_fila.append(valor)
            
            # Verificar timeout antes de agregar
            if time.time() - start_time > self.timeout:
                st.error("❌ Timeout al preparar datos")
                return False
            
            # Agregar fila
            self.worksheet.append_row(nueva_fila)
            
            # Verificar que se completó en tiempo
            if time.time() - start_time > self.timeout:
                st.warning("⚠️ Operación lenta, pero posiblemente exitosa")
            
            # Pausa breve
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar: {e}")
            return False
    
    def update_record(self, codigo, fecha, nuevo_valor):
        """Actualizar registro - CON TIMEOUT"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # NUEVO: Timeout en operación
            start_time = time.time()
            
            # Obtener datos
            data = self.worksheet.get_all_records()
            
            # Verificar timeout
            if time.time() - start_time > self.timeout / 2:
                st.warning("⚠️ Operación lenta...")
            
            # Buscar registro
            row_to_update = None
            for i, row in enumerate(data, start=2):
                if str(row.get('COD', '')).strip() == str(codigo).strip():
                    if self._compare_dates(row.get('Fecha', ''), fecha):
                        row_to_update = i
                        break
            
            if row_to_update is None:
                st.error("❌ Registro no encontrado")
                return False
            
            # Encontrar columna de valor
            headers = self.worksheet.row_values(1)
            valor_col = None
            for j, header in enumerate(headers, start=1):
                if header.lower() in ['valor', 'value']:
                    valor_col = j
                    break
            
            if valor_col is None:
                st.error("❌ Columna 'Valor' no encontrada")
                return False
            
            # Actualizar
            self.worksheet.update_cell(row_to_update, valor_col, nuevo_valor)
            
            # Verificar timeout final
            if time.time() - start_time > self.timeout:
                st.warning("⚠️ Operación lenta, verificar resultado")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
            return False
    
    def delete_record(self, codigo, fecha):
        """Eliminar registro - CON TIMEOUT"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # NUEVO: Timeout en operación
            start_time = time.time()
            
            # Obtener datos
            data = self.worksheet.get_all_records()
            
            # Buscar registro
            row_to_delete = None
            for i, row in enumerate(data, start=2):
                if str(row.get('COD', '')).strip() == str(codigo).strip():
                    if self._compare_dates(row.get('Fecha', ''), fecha):
                        row_to_delete = i
                        break
            
            if row_to_delete is None:
                st.error("❌ Registro no encontrado")
                return False
            
            # Verificar timeout
            if time.time() - start_time > self.timeout / 2:
                st.warning("⚠️ Buscando registro...")
            
            # Eliminar fila
            self.worksheet.delete_rows(row_to_delete)
            
            # Verificar timeout final
            if time.time() - start_time > self.timeout:
                st.warning("⚠️ Operación completada pero lenta")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            return False
    
    def _compare_dates(self, sheet_date_str, target_date):
        """Comparar fechas de forma segura"""
        try:
            if not sheet_date_str:
                return False
            
            # Convertir fecha de sheets
            sheet_date = pd.to_datetime(str(sheet_date_str).strip(), dayfirst=True, errors='coerce')
            
            # Convertir fecha objetivo
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date, dayfirst=True, errors='coerce')
            elif hasattr(target_date, 'date'):
                target_date = pd.to_datetime(target_date.date())
            
            # Comparar fechas
            if pd.notna(sheet_date) and pd.notna(target_date):
                return sheet_date.date() == target_date.date()
            
            return False
            
        except Exception:
            return False
    
    def get_connection_info(self):
        """Obtener información de conexión"""
        return {
            'connected': self.connected,
            'spreadsheet_url': self.spreadsheet_url,
            'worksheet_name': self.worksheet_name,
            'fichas_worksheet_name': self.fichas_worksheet_name,  # NUEVO
            'gspread_available': GSPREAD_AVAILABLE,
            'timeout': self.timeout,
            'fichas_available': self.fichas_worksheet is not None  # NUEVO
        }
    
    def test_connection(self):
        """Probar conexión - MÉTODO MEJORADO"""
        try:
            start_time = time.time()
            
            if not self.connect_to_sheet():
                return False, "No se pudo conectar"
            
            # Probar lectura rápida de datos principales
            try:
                headers = self.worksheet.row_values(1)
                connection_time = time.time() - start_time
                
                if connection_time > self.timeout:
                    return False, f"Timeout ({connection_time:.1f}s > {self.timeout}s)"
                
                # Probar lectura de fichas también
                fichas_status = ""
                if self.fichas_worksheet:
                    try:
                        fichas_headers = self.fichas_worksheet.row_values(1)
                        fichas_status = f" + Fichas OK"
                    except:
                        fichas_status = f" + Fichas ERROR"
                else:
                    fichas_status = f" + Sin Fichas"
                
                return True, f"Conexión exitosa ({connection_time:.1f}s){fichas_status}"

            except Exception as e:
                return False, f"Error al leer: {e}"

        except Exception as e:
            return False, f"Error de conexión: {e}"

    def update_valores_recalculados(self, df_with_recalculated):
        """
        Actualizar la columna Valor_Recalculado en Google Sheets
        Args:
            df_with_recalculated: DataFrame con columnas COD, Fecha, Valor_Recalculado
        """
        try:
            if not self.connected and not self.connect_to_sheet():
                return False

            # Verificar que el DataFrame tiene las columnas necesarias
            if 'Codigo' not in df_with_recalculated.columns or 'Valor_Recalculado' not in df_with_recalculated.columns:
                return False

            # Obtener headers actuales
            headers = self.worksheet.row_values(1)

            # Verificar si existe columna Valor_Recalculado
            if 'Valor_Recalculado' not in headers:
                # Agregar columna Valor_Recalculado
                headers.append('Valor_Recalculado')
                col_recalc = len(headers)
                # Actualizar header
                self.worksheet.update_cell(1, col_recalc, 'Valor_Recalculado')
            else:
                col_recalc = headers.index('Valor_Recalculado') + 1

            # Obtener todos los datos
            all_data = self.worksheet.get_all_records()

            # Actualizar valores recalculados fila por fila
            for i, row in enumerate(all_data, start=2):
                try:
                    codigo = str(row.get('COD', '')).strip()
                    fecha = row.get('Fecha', '')

                    # Buscar el valor recalculado correspondiente en el DataFrame
                    matching_rows = df_with_recalculated[
                        (df_with_recalculated['Codigo'].astype(str).str.strip() == codigo)
                    ]

                    if not matching_rows.empty:
                        # Si hay fecha, intentar hacer match más preciso
                        if fecha and 'Fecha' in df_with_recalculated.columns:
                            import pandas as pd
                            fecha_row = pd.to_datetime(fecha, errors='coerce')
                            matching_with_date = matching_rows[
                                pd.to_datetime(matching_rows['Fecha'], errors='coerce') == fecha_row
                            ]
                            if not matching_with_date.empty:
                                valor_recalc = matching_with_date.iloc[0]['Valor_Recalculado']
                            else:
                                valor_recalc = matching_rows.iloc[0]['Valor_Recalculado']
                        else:
                            valor_recalc = matching_rows.iloc[0]['Valor_Recalculado']

                        # Actualizar celda
                        self.worksheet.update_cell(i, col_recalc, float(valor_recalc))
                except Exception as e:
                    # Si falla una fila, continuar con la siguiente
                    continue

            return True

        except Exception as e:
            st.error(f"Error al actualizar valores recalculados: {e}")
            return False
