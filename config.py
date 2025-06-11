"""
Configuración y estilos para el Dashboard ICE - CON SOPORTE GOOGLE SHEETS
"""

import streamlit as st

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def apply_dark_theme():
    """Aplicar tema corporativo moderno"""
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2C3E50;
        }
        
        .main > div {
            padding-top: 2rem;
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px 10px 0 0;
            padding: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: white;
            font-weight: 500;
            border-radius: 5px;
            margin: 0 5px;
            padding: 8px 16px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.3) !important;
        }
        
        .stDataFrame, .stTable {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        div.block-container {
            padding-top: 1rem;
        }
        
        div.stButton > button {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-right: 3px solid #BDC3C7;
        }
        
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stMultiselect label,
        [data-testid="stSidebar"] .stDateInput label {
            color: white;
            font-weight: 500;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stMetric {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3498DB;
        }
        
        .stMetric label {
            color: #2C3E50 !important;
            font-weight: 600;
        }
        
        .stMetric [data-testid="metric-value"] {
            color: #2C3E50 !important;
            font-size: 1.8rem !important;
            font-weight: 700;
        }
        
        h1, h2, h3 {
            color: #2C3E50;
            font-weight: 600;
        }
        
        .stExpander {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            border: 1px solid #BDC3C7;
        }
        
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid #3498DB;
        }
        
        .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            border: 1px solid #BDC3C7;
        }
        
        /* Estilos específicos para indicadores de Google Sheets */
        .sheets-indicator {
            background: linear-gradient(45deg, #0F9D58 0%, #34A853 100%);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-block;
            margin-left: 0.5rem;
        }
        
        .csv-indicator {
            background: linear-gradient(45deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-block;
            margin-left: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def get_data_source_preference():
    """Obtener preferencia de fuente de datos desde configuración"""
    try:
        # Verificar si Google Sheets está configurado
        if ("google_sheets" in st.secrets and 
            "spreadsheet_url" in st.secrets["google_sheets"]):
            return "google_sheets"
        else:
            return "csv"
    except:
        return "csv"

def show_data_source_indicator(source_type):
    """Mostrar indicador visual del tipo de fuente de datos"""
    if source_type == "google_sheets":
        return '<span class="sheets-indicator">📊 Google Sheets</span>'
    else:
        return '<span class="csv-indicator">📁 CSV Local</span>'

# Configuración de columnas CSV/Google Sheets
COLUMN_MAPPING = {
    'LINEA DE ACCIÓN': 'Linea_Accion',
    'COMPONENTE PROPUESTO': 'Componente',
    'CATEGORÍA': 'Categoria',
    'COD': 'Codigo',
    'Nombre de indicador': 'Indicador',
    'Valor': 'Valor',
    'Fecha': 'Fecha'
}

# Configuración por defecto
DEFAULT_META = 1.0
CSV_SEPARATOR = ";"
CSV_FILENAME = "IndicadoresICE.csv"
EXCEL_FILENAME = "Batería de indicadores.xlsx"

# Configuración Google Sheets
GOOGLE_SHEETS_CONFIG = {
    'worksheet_name': 'IndicadoresICE',
    'required_columns': [
        'LINEA DE ACCIÓN', 'COMPONENTE PROPUESTO', 'CATEGORÍA', 
        'COD', 'Nombre de indicador', 'Valor', 'Fecha'
    ],
    'cache_ttl_seconds': 30,  # Cache más frecuente para Google Sheets
    'max_retries': 3
}

# Mensajes de ayuda para configuración
GOOGLE_SHEETS_SETUP_GUIDE = """
## 🔧 Configuración de Google Sheets

Para usar Google Sheets como base de datos:

### 1. Crear Service Account:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets y Google Drive
4. Crea un Service Account
5. Descarga las credenciales como JSON

### 2. Configurar Streamlit Secrets:
Crea `.streamlit/secrets.toml`:

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

### 3. Compartir Google Sheets:
- Comparte tu hoja de Google Sheets con el email del Service Account
- Dale permisos de Editor

### 4. Estructura de la hoja:
La hoja debe tener estas columnas en la primera fila:
- LINEA DE ACCIÓN
- COMPONENTE PROPUESTO  
- CATEGORÍA
- COD
- Nombre de indicador
- Valor
- Fecha
"""

def show_setup_instructions():
    """Mostrar instrucciones de configuración"""
    st.markdown(GOOGLE_SHEETS_SETUP_GUIDE)

def validate_google_sheets_config():
    """Validar configuración de Google Sheets"""
    try:
        if "google_sheets" not in st.secrets:
            return False, "Sección 'google_sheets' no encontrada en secrets.toml"
        
        required_keys = [
            'type', 'project_id', 'private_key', 'client_email', 
            'spreadsheet_url'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in st.secrets["google_sheets"]:
                missing_keys.append(key)
        
        if missing_keys:
            return False, f"Faltan claves en configuración: {missing_keys}"
        
        return True, "Configuración válida"
        
    except Exception as e:
        return False, f"Error al validar configuración: {e}"
