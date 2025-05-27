"""
Configuración y estilos para el Dashboard ICE
"""

import streamlit as st

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_dark_theme():
    """Aplicar tema oscuro personalizado"""
    st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1E1E1E;
        }
        .stTabs [data-baseweb="tab"] {
            color: white;
        }
        .stDataFrame {
            background-color: #1E1E1E;
        }
        .stTable {
            background-color: #1E1E1E;
        }
        div.block-container {
            padding-top: 2rem;
        }
        div.stButton > button {
            background-color: #4CAF50;
            color: white !important;
            border: 1px solid #4CAF50;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #45a049;
            color: white !important;
            border: 1px solid #45a049;
        }
        [data-testid="stSidebar"] {
            background-color: #1E1E1E;
        }
        .stSelectbox label, .stMultiselect label {
            color: white;
        }
        .stDateInput label {
            color: white;
        }
        .css-1d0tddh {
            color: white;
        }
        /* Mejorar visibilidad de métricas */
        [data-testid="metric-container"] {
            background-color: #2D2D2D !important;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        [data-testid="metric-container"] > div {
            color: white !important;
        }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #E0E0E0 !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }
        [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #B0B0B0 !important;
            font-size: 0.9rem !important;
        }
        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            color: #90CAF9 !important;
        }
        /* Mejorar selectboxes */
        .stSelectbox > div > div {
            background-color: #2D2D2D;
            color: white;
        }
        /* Mejorar radio buttons */
        .stRadio label {
            color: white !important;
        }
        /* Mejorar checkboxes */
        .stCheckbox label {
            color: white !important;
        }
        /* Mejorar form labels */
        .stFormSubmitButton > button {
            background-color: #2196F3 !important;
            color: white !important;
            border: 1px solid #2196F3 !important;
            font-weight: 600 !important;
        }
        .stFormSubmitButton > button:hover {
            background-color: #1976D2 !important;
            color: white !important;
            border: 1px solid #1976D2 !important;
        }
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
