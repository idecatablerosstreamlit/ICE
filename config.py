"""
Configuración y estilos para el Dashboard ICE - Versión corregida
"""

import streamlit as st

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE - IDECA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.ideca.gov.co',
            'Report a bug': None,
            'About': "Dashboard ICE - Sistema de monitoreo de indicadores de la Infraestructura de Conocimiento Espacial"
        }
    )

def apply_dark_theme():
    """Aplicar tema oscuro personalizado con mejor compatibilidad"""
    try:
        st.markdown("""
        <style>
            /* Tema principal */
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            /* Sidebar styling */
            .css-1d391kg, [data-testid="stSidebar"] {
                background-color: #262730;
            }
            
            /* Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
                background-color: #262730;
                border-radius: 8px;
                padding: 4px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 6px;
                color: #fafafa;
                font-weight: 500;
                padding: 8px 16px;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            
            /* DataFrames and tables */
            .stDataFrame, .stTable {
                background-color: #1e1e1e;
                color: #fafafa;
            }
            
            /* Metrics styling */
            [data-testid="metric-container"] {
                background: linear-gradient(135deg, #262730 0%, #1e1e1e 100%);
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            [data-testid="metric-container"] > div {
                color: #fafafa;
            }
            
            /* Buttons */
            .stButton > button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                background: linear-gradient(45deg, #45a049, #3d8b3d);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
            }
            
            /* Form styling */
            .stForm {
                background-color: #262730;
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
            
            /* Input fields */
            .stSelectbox label, .stMultiselect label, .stDateInput label, 
            .stNumberInput label, .stTextInput label {
                color: #fafafa !important;
                font-weight: 500;
            }
            
            /* Container padding */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* Headers */
            h1, h2, h3 {
                color: #fafafa;
                font-weight: 600;
            }
            
            /* Success/Error/Warning messages */
            .stSuccess {
                background-color: rgba(76, 175, 80, 0.1);
                border: 1px solid #4CAF50;
                border-radius: 8px;
            }
            
            .stError {
                background-color: rgba(244, 67, 54, 0.1);
                border: 1px solid #f44336;
                border-radius: 8px;
            }
            
            .stWarning {
                background-color: rgba(255, 193, 7, 0.1);
                border: 1px solid #ffc107;
                border-radius: 8px;
            }
            
            .stInfo {
                background-color: rgba(33, 150, 243, 0.1);
                border: 1px solid #2196f3;
                border-radius: 8px;
            }
            
            /* Plotly charts background */
            .js-plotly-plot {
                background-color: transparent !important;
            }
            
            /* Hide Streamlit branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #262730;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #4CAF50;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #45a049;
            }
            
            /* Loading spinner */
            .stSpinner > div {
                border-top-color: #4CAF50 !important;
            }
            
            /* Expandable sections */
            .streamlit-expanderHeader {
                background-color: #262730;
                color: #fafafa;
                border-radius: 8px;
            }
            
            .streamlit-expanderContent {
                background-color: #1e1e1e;
                border: 1px solid #4CAF50;
                border-radius: 0 0 8px 8px;
            }
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error aplicando tema: {e}")

def add_custom_css_fix():
    """Añadir fixes para problemas CSS comunes"""
    try:
        st.markdown("""
        <style>
            /* Fix for CSS loading issues */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            }
            
            /* Fallback styles in case of CSS loading failures */
            .stApp {
                background-color: #0e1117 !important;
                color: #fafafa !important;
            }
            
            /* Ensure visibility of key elements */
            .main > div {
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Prevent CSS loading errors from breaking layout */
            [data-testid="stSidebar"] {
                background-color: #262730 !important;
                visibility: visible !important;
            }
            
            /* Ensure metrics are always visible */
            [data-testid="metric-container"] {
                background-color: #262730 !important;
                color: #fafafa !important;
                visibility: visible !important;
            }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        # Si falla, usar estilos básicos
        st.markdown("""
        <style>
            .stApp { background-color: #0e1117; color: white; }
            [data-testid="stSidebar"] { background-color: #262730; }
        </style>
        """, unsafe_allow_html=True)

# Configuración de columnas CSV
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

# Configuración de colores
COLORS = {
    'primary': '#4CAF50',
    'secondary': '#45a049',
    'background': '#0e1117',
    'sidebar': '#262730',
    'success': '#4CAF50',
    'error': '#f44336',
    'warning': '#ffc107',
    'info': '#2196f3'
}
