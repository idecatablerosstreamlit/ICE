"""
Configuración y estilos para el Dashboard ICE - SOLO GOOGLE SHEETS
"""

import streamlit as st

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE - Ideca",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def apply_dark_theme():
    """Aplicar tema corporativo moderno con colores de Google Sheets"""
    st.markdown("""
    <style>
        .stApp {
            background: white;
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
            background: linear-gradient(90deg, #0F9D58 0%, #34A853 100%);
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
            background: linear-gradient(45deg, #0F9D58 0%, #34A853 100%);
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
            background: linear-gradient(180deg, #0F9D58 0%, #34A853 100%);
            border-right: 3px solid #BDC3C7;
        }
        
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stMultiselect label,
        [data-testid="stSidebar"] .stDateInput label {
            color: white;
            font-weight: 500;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #0F9D58 0%, #34A853 100%);
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
            border-left: 4px solid #0F9D58;
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
            border-left: 4px solid #0F9D58;
        }
        
        .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            border: 1px solid #BDC3C7;
        }
        
        /* Indicadores específicos de Google Sheets */
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
        
        .sheets-connected {
            background: linear-gradient(45deg, #4CAF50 0%, #66BB6A 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .sheets-error {
            background: linear-gradient(45deg, #F44336 0%, #E57373 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

# Configuración de columnas para Google Sheets
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
EXCEL_FILENAME = "Batería de indicadores.xlsx"

# Configuración Google Sheets
GOOGLE_SHEETS_CONFIG = {
    'worksheet_name': 'IndicadoresICE',
    'required_columns': [
        'LINEA DE ACCIÓN', 'COMPONENTE PROPUESTO', 'CATEGORÍA', 
        'COD', 'Nombre de indicador', 'Valor', 'Fecha'
    ],
    'cache_ttl_seconds': 30,
    'max_retries': 3
}

# Mensajes de ayuda para configuración
GOOGLE_SHEETS_SETUP_GUIDE = """
## 🔧 Configuración de Google Sheets para Dashboard ICE

Para usar Google Sheets como base de datos del Dashboard ICE:

### 1. Crear Service Account:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **API de Google Sheets** y **Google Drive API**
4. Ve a **"Credenciales"** → **"Crear credenciales"** → **"Cuenta de servicio"**
5. Crea una cuenta de servicio con un nombre descriptivo
6. Descarga las credenciales como archivo JSON

### 2. Configurar Streamlit Secrets:
Crea el archivo `.streamlit/secrets.toml` con el contenido del JSON:

```toml
[google_sheets]
type = "service_account"
project_id = "tu-proyecto-id"
private_key_id = "tu-private-key-id"  
private_key = "-----BEGIN PRIVATE KEY-----\\ntu-private-key-completa\\n-----END PRIVATE KEY-----\\n"
client_email = "tu-service-account@proyecto.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40proyecto.iam.gserviceaccount.com"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/TU_SPREADSHEET_ID/edit"
```

### 3. Compartir Google Sheets:
1. Abre tu hoja de Google Sheets
2. Haz clic en **"Compartir"**
3. Comparte con el email del Service Account (`tu-service-account@proyecto.iam.gserviceaccount.com`)
4. Dale permisos de **"Editor"**

### 4. Estructura de la hoja:
La hoja debe tener estas columnas en la **primera fila**:
- `LINEA DE ACCIÓN`
- `COMPONENTE PROPUESTO`  
- `CATEGORÍA`
- `COD`
- `Nombre de indicador`
- `Valor`
- `Fecha`

### 5. Installar dependencias:
```bash
pip install gspread google-auth
```

### ⚠️ Notas importantes:
- El `private_key` debe incluir los `\\n` para los saltos de línea
- El Service Account debe tener permisos de Editor en la hoja
- La URL debe ser la completa de Google Sheets (incluye `/edit` al final)
- Los nombres de las columnas deben coincidir exactamente
"""

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
        
        # Verificar que la URL sea válida
        spreadsheet_url = st.secrets["google_sheets"]["spreadsheet_url"]
        if not spreadsheet_url.startswith("https://docs.google.com/spreadsheets/"):
            return False, "URL de Google Sheets inválida"
        
        return True, "Configuración válida"
        
    except Exception as e:
        return False, f"Error al validar configuración: {e}"

def show_setup_instructions():
    """Mostrar instrucciones de configuración"""
    st.markdown(GOOGLE_SHEETS_SETUP_GUIDE)
    
    # Mostrar ejemplo de estructura
    st.subheader("📊 Ejemplo de estructura de Google Sheets:")
    
    example_data = {
        'LINEA DE ACCIÓN': ['LA.2.3.', 'N.A.', 'L.A.4.3'],
        'COMPONENTE PROPUESTO': ['Datos', 'Seguridad e interoperabilidad', 'Gobernanza y estratégia'],
        'CATEGORÍA': ['01. Disponibilidad', '01. Interoperabilidad', '02. Financiación'],
        'COD': ['D01-1', 'S01-1', 'G02-3'],
        'Nombre de indicador': [
            'Porcentaje de datos de licencia abierta',
            'Porcentaje de datos que se consumen como servicios',
            'Porcentaje de incremento ingresos propios anuales'
        ],
        'Valor': [0.5, 0.75, 0.3],
        'Fecha': ['1/01/2025', '1/01/2025', '1/01/2025']
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    st.info("💡 **Tip:** Puedes copiar esta estructura a tu Google Sheets como punto de partida.")

def get_connection_status():
    """Obtener estado de conexión de Google Sheets"""
    try:
        config_valid, _ = validate_google_sheets_config()
        if config_valid:
            return "connected"
        else:
            return "config_error"
    except:
        return "error"
