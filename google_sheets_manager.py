"""
Gestor de Google Sheets para el Dashboard ICE - CORREGIDO
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import json

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

class GoogleSheetsManager:
    """Clase para gestionar la conexión y operaciones con Google Sheets - CORREGIDA"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.spreadsheet_url = None
        self.worksheet_name = "IndicadoresICE"
        self.connected = False
        
    def setup_credentials(self):
        """Configurar credenciales de Google Sheets"""
        try:
            if not GSPREAD_AVAILABLE:
                st.error("📦 **Instalar dependencias:** `pip install gspread google-auth`")
                return False
            
            # Verificar configuración en secrets
            if "google_sheets" not in st.secrets:
                st.error("""
                ❌ **Configuración requerida en `.streamlit/secrets.toml`:**
                
                ```toml
                [google_sheets]
                type = "service_account"
                project_id = "tu-proyecto-id"
                private_key_id = "tu-private-key-id"
                private_key = "-----BEGIN PRIVATE KEY-----\\ntu-private-key\\n-----END PRIVATE KEY-----\\n"
                client_email = "tu-service-account@proyecto.iam.gserviceaccount.com"
                client_id = "tu-client-id"
                auth_uri = "https://accounts.google.com/o/oauth2/auth"
                token_uri = "https://oauth2.googleapis.com/token"
                spreadsheet_url = "https://docs.google.com/spreadsheets/d/TU_SPREADSHEET_ID/edit"
                ```
                """)
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
            
            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=scope
            )
            
            self.gc = gspread.authorize(credentials)
            return True
            
        except Exception as e:
            st.error(f"❌ Error en credenciales: {e}")
            return False
    
    def connect_to_sheet(self):
        """Conectar a la hoja de Google Sheets"""
        try:
            if not self.gc and not self.setup_credentials():
                return False
            
            # Abrir hoja de cálculo
            self.sheet = self.gc.open_by_url(self.spreadsheet_url)
            
            # Obtener o crear worksheet
            try:
                self.worksheet = self.sheet.worksheet(self.worksheet_name)
                # st.success(f"✅ Conectado a '{self.worksheet_name}'")
            except gspread.WorksheetNotFound:
                # Crear worksheet si no existe
                self.worksheet = self.sheet.add_worksheet(
                    title=self.worksheet_name, rows=1000, cols=10
                )
                # Agregar headers
                headers = [
                    "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha"
                ]
                self.worksheet.append_row(headers)
                st.success(f"✅ Creada hoja '{self.worksheet_name}'")
            
            self.connected = True
            return True
            
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
            self.connected = False
            return False
    
    def load_data(self):
        """Cargar datos desde Google Sheets"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return None
            
            # Obtener todos los datos
            data = self.worksheet.get_all_records()
            
            if not data:
                st.warning("⚠️ Hoja de Google Sheets vacía")
                # Crear DataFrame vacío con columnas correctas
                return pd.DataFrame(columns=[
                    "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
                    "COD", "Nombre de indicador", "Valor", "Fecha"
                ])
            
            df = pd.DataFrame(data)
            
            # Debug info
            
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al cargar desde Google Sheets: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def add_record(self, data_dict):
        """Agregar un registro a Google Sheets - CORREGIDO"""
        try:
            if not self.connected and not self.connect_to_sheet():
                st.error("❌ No se pudo conectar a Google Sheets")
                return False
            
            # Verificar que tenemos datos
            if not data_dict:
                st.error("❌ No hay datos para agregar")
                return False
            
            # Obtener headers de la hoja para mantener orden correcto
            try:
                headers = self.worksheet.row_values(1)
                if not headers:
                    # Si no hay headers, agregarlos
                    headers = [
                        "LINEA DE ACCIÓN", "COMPONENTE PROPUESTO", "CATEGORÍA", 
                        "COD", "Nombre de indicador", "Valor", "Fecha"
                    ]
                    self.worksheet.append_row(headers)
            except Exception as e:
                st.error(f"❌ Error al obtener headers: {e}")
                return False
            
            # Mapeo de nombres internos a nombres de Google Sheets
            header_map = {
                'Linea_Accion': 'LINEA DE ACCIÓN',
                'Componente': 'COMPONENTE PROPUESTO', 
                'Categoria': 'CATEGORÍA',
                'Codigo': 'COD',
                'Indicador': 'Nombre de indicador',
                'Valor': 'Valor',
                'Fecha': 'Fecha'
            }
            
            # Crear fila con el orden correcto de los headers
            nueva_fila = []
            for header in headers:
                # Buscar el valor correspondiente
                valor_encontrado = ""
                
                # Buscar por mapeo directo
                for key_interno, header_sheets in header_map.items():
                    if header == header_sheets and key_interno in data_dict:
                        valor_encontrado = str(data_dict[key_interno])
                        break
                
                # Si no se encontró por mapeo, buscar directamente
                if not valor_encontrado and header in data_dict:
                    valor_encontrado = str(data_dict[header])
                
                nueva_fila.append(valor_encontrado)
            
            # Debug: mostrar lo que se va a agregar
            with st.expander("🔧 Debug: Datos a agregar", expanded=False):
                st.write("**Headers de Google Sheets:**", headers)
                st.write("**Datos recibidos:**", data_dict)
                st.write("**Fila a agregar:**", nueva_fila)
            
            # Agregar fila a Google Sheets
            self.worksheet.append_row(nueva_fila)
            st.success("✅ Registro agregado a Google Sheets")
            
            # Pequeña pausa para asegurar que se guarde
            import time
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    def update_record(self, codigo, fecha, nuevo_valor):
        """Actualizar un registro en Google Sheets - CORREGIDO"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # Obtener todos los datos para buscar el registro
            try:
                data = self.worksheet.get_all_records()
            except Exception as e:
                st.error(f"❌ Error al obtener datos: {e}")
                return False
            
            # Buscar registro a actualizar
            row_to_update = None
            for i, row in enumerate(data, start=2):  # start=2 (headers en fila 1)
                row_codigo = str(row.get('COD', '')).strip()
                
                if row_codigo == str(codigo).strip():
                    # Comparar fechas
                    if self._compare_dates(row.get('Fecha', ''), fecha):
                        row_to_update = i
                        break
            
            if row_to_update is None:
                st.error("❌ Registro no encontrado para actualizar")
                return False
            
            # Encontrar columna de Valor
            try:
                headers = self.worksheet.row_values(1)
                valor_col = None
                for j, header in enumerate(headers, start=1):
                    if header in ['Valor', 'valor']:
                        valor_col = j
                        break
                
                if valor_col is None:
                    st.error("❌ No se encontró columna 'Valor'")
                    return False
                
                # Actualizar celda
                self.worksheet.update_cell(row_to_update, valor_col, nuevo_valor)
                st.success("✅ Registro actualizado en Google Sheets")
                
                # Pausa para asegurar guardado
                import time
                time.sleep(0.5)
                
                return True
                
            except Exception as e:
                st.error(f"❌ Error al actualizar celda: {e}")
                return False
            
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
            return False
    
    def delete_record(self, codigo, fecha):
        """Eliminar un registro de Google Sheets - CORREGIDO"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # Obtener todos los datos
            try:
                data = self.worksheet.get_all_records()
            except Exception as e:
                st.error(f"❌ Error al obtener datos: {e}")
                return False
            
            # Buscar registro a eliminar
            row_to_delete = None
            for i, row in enumerate(data, start=2):  # start=2 (headers en fila 1)
                row_codigo = str(row.get('COD', '')).strip()
                
                if row_codigo == str(codigo).strip():
                    if self._compare_dates(row.get('Fecha', ''), fecha):
                        row_to_delete = i
                        break
            
            if row_to_delete is None:
                st.error("❌ Registro no encontrado para eliminar")
                return False
            
            try:
                # Eliminar fila
                self.worksheet.delete_rows(row_to_delete)
                st.success("✅ Registro eliminado de Google Sheets")
                
                # Pausa para asegurar guardado
                import time
                time.sleep(0.5)
                
                return True
                
            except Exception as e:
                st.error(f"❌ Error al eliminar fila: {e}")
                return False
            
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            return False
    
    def _compare_dates(self, sheet_date_str, target_date):
        """Comparar fechas de forma segura - MEJORADO"""
        try:
            if not sheet_date_str:
                return False
            
            # Limpiar string de fecha
            sheet_date_str = str(sheet_date_str).strip()
            
            # Convertir fecha de sheets a datetime
            sheet_date = pd.to_datetime(sheet_date_str, dayfirst=True, errors='coerce')
            
            # Convertir fecha objetivo a datetime si es necesario
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date, dayfirst=True, errors='coerce')
            elif hasattr(target_date, 'date'):
                # Si es datetime, extraer solo la fecha
                target_date = pd.to_datetime(target_date.date())
            
            # Comparar solo las fechas (sin tiempo)
            if pd.notna(sheet_date) and pd.notna(target_date):
                return sheet_date.date() == target_date.date()
            
            return False
            
        except Exception as e:
            st.warning(f"Error al comparar fechas: {e}")
            return False
    
    def get_connection_info(self):
        """Obtener información de la conexión"""
        return {
            'connected': self.connected,
            'spreadsheet_url': self.spreadsheet_url,
            'worksheet_name': self.worksheet_name,
            'gspread_available': GSPREAD_AVAILABLE
        }
