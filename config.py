""""
Configuración y estilos para el Dashboard ICE - SIN TEMA OSCURO
"""
import streamlit as st
import base64
import os

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE - Google Sheets",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )



def create_banner():
    """Crear banner superior del dashboard - ARREGLADO Y FUNCIONAL"""
    
    # Función auxiliar para convertir imagen a base64
    def img_to_base64(img_path):
        try:
            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode()
        except:
            pass
        return None

    # Intentar cargar las imágenes
    logo_gov = img_to_base64("images/logo_gov.png")
    logo_bogota = img_to_base64("images/logo_bogota.png") 
    logo_alcaldia = img_to_base64("images/logo_alcaldia.png")
    
    # Sección azul GOV.CO (sin cambios)
    if logo_gov:
        gov_logo_html = f'<img src="data:image/png;base64,{logo_gov}" style="width: 140px; height: 32px; margin-right: 12px;" alt="GOV.CO">'
    else:
        gov_logo_html = '''<div style="
            width: 32px; height: 32px; background: white; border-radius: 6px; margin-right: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; color: #4169E1; font-weight: bold;">🏛️</div>'''
    
    st.markdown(f"""
    <div style="
        background: #4169E1;
        padding: 15px 20px;
        margin: -1rem -1rem 0 -1rem;
        color: white;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        ">
            <div style="display: flex; align-items: center;">
                {gov_logo_html}
                <span style="
                    color: white;
                    font-size: 22px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                "></span>
            </div>
            <a href="https://www.gov.co/" target="_blank" style="
                color: white;
                text-decoration: underline;
                font-size: 14px;
            ">Ir a Gov.co</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # SECCIÓN BLANCA - USANDO COLUMNAS DE STREAMLIT
    # Nueva distribución: Alcaldía + Bogotá a la izquierda, Título a la derecha
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Logos en una fila horizontal
        logo_col1, logo_col2 = st.columns([1, 1])
        
        with logo_col1:
            # Logo Alcaldía PRIMERO
            if logo_alcaldia:
                st.markdown(f'''
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{logo_alcaldia}" 
                         style="width: 60px; height: auto;" 
                         alt="Alcaldía Mayor">
                    <div style="font-size: 10px; font-weight: 500; margin-top: 5px;">ALCALDÍA</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown("### 🏛️")
                st.caption("ALCALDÍA")
        
        with logo_col2:
            # Logo Bogotá SEGUNDO
            if logo_bogota:
                st.markdown(f'''
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{logo_bogota}" 
                         style="width: 80px; height: auto;" 
                         alt="Datos Abiertos Bogotá">
                    <div style="font-size: 10px; font-weight: 500; margin-top: 5px;">BOGOTÁ</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown("### 🏢")
                st.caption("BOGOTÁ")
    
    with col2:
        # Título y subtítulo a la DERECHA
        st.markdown("# Dashboard ICE")
        st.markdown("""
        <p style="
            color: #1e3a8a; 
            font-size: 0.9rem; 
            font-weight: 500;
            margin-top: -10px;
        ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

def apply_dark_theme():
    """Aplicar estilos - PESTAÑAS GRISES CON ACTIVA EN AZUL #4169E1"""
    st.markdown("""
    <style>
        /* PESTAÑAS - FORZAR COLORES ESPECÍFICOS */
        .stTabs [data-baseweb="tab-list"] {
            background: #f5f5f5 !important;
            border-radius: 10px 10px 0 0 !important;
            padding: 10px !important;
            border-bottom: 2px solid #ddd !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #e8e8e8 !important;
            color: #666666 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            margin: 0 5px !important;
            padding: 12px 20px !important;
            border: 1px solid #cccccc !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #d5d5d5 !important;
            color: #333333 !important;
            border-color: #999999 !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #4169E1 !important;
            color: white !important;
            border-color: #4169E1 !important;
            font-weight: 700 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(65, 105, 225, 0.4) !important;
        }
        
        /* BOTONES */
        div.stButton > button:first-child {
            background-color: #4169E1 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:first-child:hover {
            background-color: #365cc0 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* MÉTRICAS */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.1) !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            border-left: 4px solid #4169E1 !important;
        }
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4169E1 0%, #365cc0 100%) !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stMultiselect label {
            color: white !important;
            font-weight: 500 !important;
        }
        
        /* SELECTBOX */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Configuración de columnas para Google Sheets - ACTUALIZADO CON TIPO
COLUMN_MAPPING = {
    'LINEA DE ACCIÓN': 'Linea_Accion',
    'COMPONENTE PROPUESTO': 'Componente',
    'CATEGORÍA': 'Categoria',
    'COD': 'Codigo',
    'Nombre de indicador': 'Indicador',
    'Valor': 'Valor',
    'Fecha': 'Fecha',
    'Tipo': 'Tipo'
}

# Configuración por defecto
DEFAULT_META = 1.0
EXCEL_FILENAME = "Batería de indicadores.xlsx"

# Configuración Google Sheets - ACTUALIZADA
GOOGLE_SHEETS_CONFIG = {
    'worksheet_name': 'IndicadoresICE',
    'required_columns': [
        'LINEA DE ACCIÓN', 'COMPONENTE PROPUESTO', 'CATEGORÍA', 
        'COD', 'Nombre de indicador', 'Valor', 'Fecha', 'Tipo'
    ],
    'cache_ttl_seconds': 30,
    'max_retries': 3
}

# Tipos de indicadores soportados
INDICATOR_TYPES = {
    'porcentaje': {
        'description': 'Valores entre 0-1 o 0-100%',
        'examples': ['0.75', '75%'],
        'normalization': 'direct'
    },
    'numero': {
        'description': 'Cantidades numéricas',
        'examples': ['150', '1250'],
        'normalization': 'by_max'
    },
    'moneda': {
        'description': 'Valores monetarios',
        'examples': ['$50000', '2500000'],
        'normalization': 'by_max'
    },
    'indice': {
        'description': 'Índices y ratios',
        'examples': ['1.5', '0.85'],
        'normalization': 'by_max'
    }
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
- `Tipo`

### 5. Tipos de indicadores soportados:
- **porcentaje**: Valores entre 0-1 o 0-100%
- **numero**: Cantidades numéricas (se normaliza por el máximo)
- **moneda**: Valores monetarios (se normaliza por el máximo)
- **indice**: Índices y ratios (se normaliza por el máximo)

### 6. Instalar dependencias:
```bash
pip install gspread google-auth
```

### ⚠️ Notas importantes:
- El `private_key` debe incluir los `\\n` para los saltos de línea
- El Service Account debe tener permisos de Editor en la hoja
- La URL debe ser la completa de Google Sheets (incluye `/edit` al final)
- Los nombres de las columnas deben coincidir exactamente
- La columna **Tipo** es obligatoria para la normalización correcta
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
            'Incremento ingresos propios anuales (millones COP)'
        ],
        'Valor': [0.5, 0.75, 1250],
        'Fecha': ['1/01/2025', '1/01/2025', '1/01/2025'],
        'Tipo': ['porcentaje', 'porcentaje', 'moneda']
    }
    
    import pandas as pd
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    st.info("💡 **Tip:** Nota la columna 'Tipo' que define cómo normalizar cada indicador.")

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
