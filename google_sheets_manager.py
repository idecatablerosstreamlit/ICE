"""
Gestor de Google Sheets - VERSIÓN CORREGIDA CON TIMEOUT
CORRECCIÓN: Timeout en conexiones y manejo de errores mejorado
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
    """Gestor de Google Sheets - VERSIÓN CORREGIDA"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.spreadsheet_url = None
        self.worksheet_name = "IndicadoresICE"
        self.connected = False
        self.timeout = 30  # NUEVO: Timeout de 30 segundos
        
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
        """Conectar a Google Sheets - CON TIMEOUT"""
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
            
            # Obtener o crear worksheet
            try:
                self.worksheet = self.sheet.worksheet(self.worksheet_name)
            except gspread.WorksheetNotFound:
                # Crear worksheet si no existe
                self.worksheet = self.sheet.add_worksheet(
                    title=self.worksheet_name, rows=1000, cols=10
                )
                # Agregar headers
                headers = [
                    "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha", "Tipo"
                ]
                self.worksheet.append_row(headers)
            
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
                        "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
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
                    "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
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
            'gspread_available': GSPREAD_AVAILABLE,
            'timeout': self.timeout
        }
    
    def test_connection(self):
        """Probar conexión - NUEVO MÉTODO"""
        try:
            start_time = time.time()
            
            if not self.connect_to_sheet():
                return False, "No se pudo conectar"
            
            # Probar lectura rápida
            try:
                headers = self.worksheet.row_values(1)
                connection_time = time.time() - start_time
                
                if connection_time > self.timeout:
                    return False, f"Timeout ({connection_time:.1f}s > {self.timeout}s)"
                
                return True, f"Conexión exitosa ({connection_time:.1f}s)"
                
            except Exception as e:
                return False, f"Error al leer: {e}"
                
        except Exception as e:
            return False, f"Error de conexión: {e}"
