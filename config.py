"""
Configuración y estilos para el Dashboard ICE
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
EXCEL_FILENAME = "Batería de indicadores.xlsx"
