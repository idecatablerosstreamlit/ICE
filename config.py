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
            color: white;
        }
        div.stButton > button:hover {
            background-color: #45a049;
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
