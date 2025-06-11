"""
Gestor de Google Sheets para el Dashboard ICE
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
    """Clase para gestionar la conexión y operaciones con Google Sheets"""
    
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
                st.success(f"✅ Conectado a '{self.worksheet_name}'")
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
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            # Debug info
            with st.expander("🔧 Debug: Google Sheets", expanded=False):
                st.write(f"**URL:** {self.spreadsheet_url}")
                st.write(f"**Worksheet:** {self.worksheet_name}")
                st.write(f"**Registros:** {len(df)}")
                st.write(f"**Columnas:** {list(df.columns)}")
                if not df.empty:
                    st.dataframe(df.head(3))
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al cargar desde Google Sheets: {e}")
            return None
    
    def add_record(self, data_dict):
        """Agregar un registro a Google Sheets"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # Obtener headers para mantener orden
            headers = self.worksheet.row_values(1)
            
            # Crear fila con el orden correcto
            nueva_fila = []
            for header in headers:
                # Mapear nombres de columnas
                header_map = {
                    'LINEA DE ACCIÓN': 'Linea_Accion',
                    'COMPONENTE PROPUESTO': 'Componente', 
                    'CATEGORÍA': 'Categoria',
                    'COD': 'Codigo',
                    'Nombre de indicador': 'Indicador',
                    'Valor': 'Valor',
                    'Fecha': 'Fecha'
                }
                
                mapped_key = header_map.get(header, header)
                nueva_fila.append(data_dict.get(mapped_key, ''))
            
            # Agregar fila
            self.worksheet.append_row(nueva_fila)
            st.success("✅ Registro agregado a Google Sheets")
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar: {e}")
            return False
    
    def update_record(self, codigo, fecha, nuevo_valor):
        """Actualizar un registro en Google Sheets"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # Obtener todos los datos
            data = self.worksheet.get_all_records()
            
            # Buscar registro a actualizar
            for i, row in enumerate(data, start=2):  # start=2 (headers en fila 1)
                if (str(row.get('COD', '')).strip() == str(codigo).strip() and 
                    self._compare_dates(row.get('Fecha', ''), fecha)):
                    
                    # Encontrar columna de Valor
                    headers = self.worksheet.row_values(1)
                    valor_col = None
                    for j, header in enumerate(headers, start=1):
                        if header == 'Valor':
                            valor_col = j
                            break
                    
                    if valor_col:
                        self.worksheet.update_cell(i, valor_col, nuevo_valor)
                        st.success("✅ Registro actualizado en Google Sheets")
                        return True
            
            st.error("❌ Registro no encontrado")
            return False
            
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
            return False
    
    def delete_record(self, codigo, fecha):
        """Eliminar un registro de Google Sheets"""
        try:
            if not self.connected and not self.connect_to_sheet():
                return False
            
            # Obtener todos los datos
            data = self.worksheet.get_all_records()
            
            # Buscar registro a eliminar
            for i, row in enumerate(data, start=2):  # start=2 (headers en fila 1)
                if (str(row.get('COD', '')).strip() == str(codigo).strip() and 
                    self._compare_dates(row.get('Fecha', ''), fecha)):
                    
                    # Eliminar fila
                    self.worksheet.delete_rows(i)
                    st.success("✅ Registro eliminado de Google Sheets")
                    return True
            
            st.error("❌ Registro no encontrado")
            return False
            
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            return False
    
    def _compare_dates(self, sheet_date_str, target_date):
        """Comparar fechas de forma segura"""
        try:
            if not sheet_date_str:
                return False
            
            # Convertir fecha de sheets a datetime
            sheet_date = pd.to_datetime(sheet_date_str, dayfirst=True, errors='coerce')
            
            # Convertir fecha objetivo a datetime si es necesario
            if isinstance(target_date, str):
                target_date = pd.to_datetime(target_date, dayfirst=True, errors='coerce')
            
            # Comparar solo las fechas (sin tiempo)
            if pd.notna(sheet_date) and pd.notna(target_date):
                return sheet_date.date() == target_date.date()
            
            return False
            
        except Exception:
            return False
    
    def get_connection_info(self):
        """Obtener información de la conexión"""
        return {
            'connected': self.connected,
            'spreadsheet_url': self.spreadsheet_url,
            'worksheet_name': self.worksheet_name,
            'gspread_available': GSPREAD_AVAILABLE
        }