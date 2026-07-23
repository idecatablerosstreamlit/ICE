""""
Configuración y estilos para el Dashboard ICE - SIN TEMA OSCURO
"""
import streamlit as st
import base64
import os

# ============================================================
# PALETA DE COLOR IDECA (manual de marca)
# ============================================================
IDECA_COLORS = {
    'azul': '#003A5B',        # Azul Ideca - primario
    'azul_claro': '#7A97A8',  # Azul Ideca claro - primario
    'rojo': '#E3192F',        # Rojo impacto - acciones puntuales
    'amarillo': '#FEB400',    # Amarillo - destacar elementos clave
    'gris_fondos': '#EAEAEA', # Gris neutro - fondos
    'negro_textos': '#444444' # Negro - textos
}

# Derivados para hover/degradados (tintes del azul Ideca)
IDECA_AZUL_HOVER = '#002A42'   # azul más oscuro para hover
IDECA_AZUL_TINTE = '#E5EBEF'   # tinte muy claro del azul para fondos suaves

# Escala de desempeño (semáforo alineado a la paleta IDECA)
# alto → azul Ideca, medio-alto → azul claro, medio-bajo → amarillo, crítico → rojo
IDECA_PERFORMANCE_SCALE = {
    'alto': IDECA_COLORS['azul'],
    'medio_alto': IDECA_COLORS['azul_claro'],
    'medio_bajo': IDECA_COLORS['amarillo'],
    'critico': IDECA_COLORS['rojo']
}

# Tipografía institucional
IDECA_FONT = "Nunito Sans"
IDECA_FONT_CSS = f"'{IDECA_FONT}', 'Source Sans Pro', sans-serif"

# ============================================================
# CONTENIDO DE REFERENCIA: ¿QUÉ ES LA ICE? COMPONENTES Y CATEGORÍAS
# Basado en el documento "ICE — Infraestructura de Conocimiento Espacial:
# Definiciones, componentes, categorías y marco normativo" (Resumen.pdf, IDECA 2025)
# ============================================================
ICE_QUE_ES = """
La **Infraestructura de Conocimiento Espacial (ICE)** es la evolución de la tradicional Infraestructura
de Datos Espaciales (IDE): no se limita a gestionar técnicamente los datos geográficos, sino que busca
convertirlos en conocimiento útil para tomar decisiones, innovar, planear el territorio y facilitar la
participación ciudadana.

En otras palabras: la IDE se encarga de que los datos existan, estén disponibles y sean de calidad. La
ICE va un paso más allá y pregunta qué tanto esos datos se están usando realmente para generar valor
público en la ciudad.

Esta evolución responde a la misión de IDECA (facilitar el descubrimiento, acceso, interoperabilidad y
reutilización de la información geoespacial de forma colaborativa) y a su visión 2033: ser una
infraestructura de conocimiento geoespacial que soporte la transformación de Bogotá hacia un territorio
inteligente y sostenible.
"""

ICE_COMO_SE_MIDE = """
El modelo ICE organiza el seguimiento en tres niveles, de lo más general a lo más específico:

- **Componentes:** las 8 grandes dimensiones de la infraestructura (gobernanza, datos, interoperabilidad, etc.).
- **Categorías:** subtemas dentro de cada componente (por ejemplo, dentro de "Datos": disponibilidad, datos básicos y calidad).
- **Indicadores:** las métricas específicas que se calculan y consolidan hacia arriba, hasta llegar a un puntaje único (Índice General ICE) entre 0 y 1.

Cada indicador tiene su propia ficha metodológica (definición, fórmula, fuente y responsable), y los
puntajes se calculan como un promedio ponderado que sube desde los indicadores hasta las categorías,
los componentes y finalmente el índice general.

De acuerdo con el Decreto Nacional 1389 de 2022 y el Decreto Distrital 575 de 2023, la infraestructura
de datos del Distrito (y por tanto la ICE) se organiza en los siguientes 8 componentes.
"""

# Lista de los 8 componentes: nombre, descripción, categorías (nombre + qué mide) y fuente normativa
ICE_COMPONENTS_INFO = [
    {
        "nombre": "1. Gobernanza de la Infraestructura de Datos",
        "descripcion": "Es el conjunto de reglas, roles y espacios de coordinación que permiten que las "
                        "entidades del Distrito trabajen juntas para gestionar los datos geográficos de "
                        "forma ordenada, confiable y con responsabilidades claras. Define quién decide, "
                        "quién ejecuta y quién es responsable de cada dato.",
        "categorias": [
            {"Categoría": "Condiciones iniciales y normativa", "Qué mide": "Marco jurídico e institucional que habilita la operación de la infraestructura de datos."},
            {"Categoría": "Financiación", "Qué mide": "Recursos presupuestales que garantizan la sostenibilidad de la infraestructura en el tiempo."},
            {"Categoría": "Planeación y participación", "Qué mide": "Formulación estratégica y articulación con entidades públicas, privadas y ciudadanía."},
            {"Categoría": "Comunicaciones", "Qué mide": "Divulgación y posicionamiento de la infraestructura de datos como un bien público."},
            {"Categoría": "Seguimiento y evaluación", "Qué mide": "Monitoreo del desempeño, impacto y cumplimiento de metas."},
        ],
        "fuente": "Decreto Nacional 1389 de 2022 (MinTIC), Decreto Distrital 575 de 2023 y Decreto 608 de 2022 (IDECA)."
    },
    {
        "nombre": "2. Generación de capacidades",
        "descripcion": "Se refiere a fortalecer las habilidades de las personas y las entidades para que "
                        "puedan implementar, operar y sostener la infraestructura de datos por sí mismas: "
                        "formación, transferencia de conocimiento e investigación aplicada.",
        "categorias": [
            {"Categoría": "Fortalecimiento de capacidades", "Qué mide": "Desarrollo de competencias técnicas e institucionales para gestionar y usar datos geoespaciales."},
            {"Categoría": "Educación", "Qué mide": "Inclusión de contenidos sobre datos abiertos y geografía digital en procesos formativos."},
            {"Categoría": "I+D+i", "Qué mide": "Investigación, desarrollo e innovación aplicados a datos geoespaciales."},
        ],
        "fuente": "Plan Nacional de Infraestructura de Datos (PNID, Resolución MinTIC 460 de 2022) y Plan Estratégico IDECA 2024–2033."
    },
    {
        "nombre": "3. Datos",
        "descripcion": "Es el núcleo de todo el sistema: la información geográfica que producen las "
                        "entidades del Distrito (mapas, catastro, límites administrativos, etc.), que debe "
                        "estar disponible, actualizada y ser confiable para poder usarse con seguridad.",
        "categorias": [
            {"Categoría": "Disponibilidad", "Qué mide": "Acceso oportuno y abierto a los datos, conforme a principios internacionales (FAIR)."},
            {"Categoría": "Datos básicos", "Qué mide": "Conjuntos de datos esenciales para el funcionamiento del Distrito, como el mapa de referencia o el catastro."},
            {"Categoría": "Calidad", "Qué mide": "Precisión, completitud, coherencia y actualidad de los datos geográficos."},
        ],
        "fuente": "Decreto Distrital 575 de 2023 y principios internacionales de datos abiertos FAIR."
    },
    {
        "nombre": "4. Interoperabilidad",
        "descripcion": "Es la capacidad de que los sistemas de distintas entidades se 'entiendan entre sí' "
                        "e intercambien información de forma automática, segura y estandarizada, sin "
                        "importar qué tecnología use cada una.",
        "categorias": [
            {"Categoría": "Interoperabilidad", "Qué mide": "Capacidad de los sistemas para intercambiar, procesar y reutilizar datos entre plataformas de forma estandarizada."},
        ],
        "fuente": "Marco de Interoperabilidad del MinTIC (dominios político-legal, organizacional, semántico y técnico)."
    },
    {
        "nombre": "5. Aprovechamiento de datos",
        "descripcion": "Es convertir los datos en decisiones: usar la información geográfica para planear "
                        "mejor la ciudad, identificar patrones y brechas en el territorio, y crear "
                        "soluciones e innovación pública, no solo publicar datos.",
        "categorias": [
            {"Categoría": "Analítica de datos", "Qué mide": "Uso de estadística, geografía e inteligencia artificial para generar conocimiento a partir de los datos."},
            {"Categoría": "Uso de información de las plataformas", "Qué mide": "Medición del acceso, consulta y reutilización de datos desde los geoportales y servicios web."},
        ],
        "fuente": "Marco de Referencia de Arquitectura Empresarial del MinTIC y Política Pública Bogotá Territorio Inteligente 2023–2032 (CONPES Distrital 29 de 2023)."
    },
    {
        "nombre": "6. Seguridad y privacidad",
        "descripcion": "Es proteger los datos geográficos frente a accesos indebidos, alteraciones o "
                        "pérdidas, y cuidar los datos personales de las personas, cumpliendo la ley y "
                        "generando confianza institucional y ciudadana.",
        "categorias": [
            {"Categoría": "Seguridad", "Qué mide": "Protocolos de protección, control de acceso y gestión de riesgos sobre los datos y las plataformas."},
        ],
        "fuente": "Modelo de Seguridad y Privacidad de la Información (MSPI) del MinTIC, Ley 1581 de 2012 y Ley 1712 de 2014."
    },
    {
        "nombre": "7. Insumos técnicos y tecnológicos",
        "descripcion": "Son las herramientas, plataformas y estándares tecnológicos (como Mapas Bogotá o "
                        "el portal de Datos Abiertos) que hacen posible producir, administrar, intercambiar "
                        "y visualizar la información geográfica.",
        "categorias": [
            {"Categoría": "Geoportales y servicios web geoespaciales", "Qué mide": "Plataformas para visualizar, consultar y descargar datos geográficos."},
            {"Categoría": "Desempeño tecnológico", "Qué mide": "Eficiencia, escalabilidad y disponibilidad de los sistemas que soportan la infraestructura."},
        ],
        "fuente": "Plan Nacional de Infraestructura de Datos (PNID), Marco de Referencia de Arquitectura Empresarial del MinTIC y estándares OGC."
    },
    {
        "nombre": "8. Uso y apropiación",
        "descripcion": "Mide qué tanto las entidades, la ciudadanía, la academia y el sector privado "
                        "realmente consultan, entienden y se apropian de los datos geográficos que ofrece "
                        "IDECA, más allá de que estén simplemente disponibles.",
        "categorias": [
            {"Categoría": "Interacción con los geoportales IDECA", "Qué mide": "Nivel de participación y aprovechamiento de los datos geográficos por parte de los usuarios."},
        ],
        "fuente": "Guía de Uso y Apropiación de TI del MinTIC y principios del Plan Nacional de Infraestructura de Datos (PNID)."
    },
]

def configure_page():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Dashboard ICE - Google Sheets",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )



def create_banner():
    """Crear banner superior + título centrado fuera"""
    
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
        gov_logo_html = f'<img src="data:image/png;base64,{logo_gov}" style="width: 140px; height: 32px; margin-right: 12px;" alt="">'
    else:
        gov_logo_html = '''<div style="
            width: 32px; height: 32px; background: white; border-radius: 6px; margin-right: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; color: #003A5B; font-weight: bold;">🏛️</div>'''

    st.markdown(f"""
    <div style="
        background: #003A5B;
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
    
    # SECCIÓN BLANCA - SOLO LOGOS (SIN TÍTULO)
 # SECCIÓN BLANCA - LOGOS JUNTOS A LA IZQUIERDA CON STREAMLIT
    col1, col2, col3 = st.columns([2, 3, 5])  # Ajustar proporciones para juntar logos
    
    with col1:
        # Logo Alcaldía CLICKEABLE
        if logo_alcaldia:
            st.markdown(f'''
            <div style="text-align: left; padding-right: 10px;">
                <a href="https://www.ideca.gov.co/" target="_blank" style="text-decoration: none;">
                    <img src="data:image/png;base64,{logo_alcaldia}" 
                         style="width: 150px; height: auto; transition: opacity 0.3s ease;" 
                         alt="Alcaldía Mayor - IDECA"
                         onmouseover="this.style.opacity='0.8'"
                         onmouseout="this.style.opacity='1'">
                </a>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="text-align: right; padding-right: 10px;">
                <a href="https://www.ideca.gov.co/" target="_blank" style="text-decoration: none;">
                    <div style="
                        width: 150px; height: 80px; background: #f0f0f0; border-radius: 8px;
                        display: inline-flex; align-items: center; justify-content: center;
                        font-size: 24px; color: #666; transition: opacity 0.3s ease;
                    " onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">🏛️</div>
                </a>
            </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        # Logo Bogotá (no clickeable, pegado al de Alcaldía)
        if logo_bogota:
            st.markdown(f'''
            <div style="text-align: left; padding-left: 0px;">
                <img src="data:image/png;base64,{logo_bogota}" 
                     style="width: 300px; height: auto;" 
                     alt="Datos Abiertos Bogotá">
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="text-align: left; padding-left: 0px;">
                <div style="
                    width: 300px; height: 80px; background: #f0f0f0; border-radius: 8px;
                    display: inline-flex; align-items: center; justify-content: center;
                    font-size: 24px; color: #666;
                ">🏢</div>
            </div>
            ''', unsafe_allow_html=True)
    
    with col3:
        # Columna vacía para el resto del espacio
        st.write("")
    
    # TÍTULO CENTRADO FUERA DEL BANNER EN AZUL OSCURO
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="
            color: #003A5B;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        ">Dashboard ICE</h1>
        <p style="
            color: #003A5B;
            font-size: 1rem;
            font-weight: 500;
            margin: 10px 0 0 0;
        ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

def apply_dark_theme():
    """Aplicar estilos - PALETA IDECA (azul #003A5B) Y FUENTE NUNITO SANS"""
    st.markdown("""
    <style>
        /* FUENTE INSTITUCIONAL - NUNITO SANS */
        @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        html, body, [class*="css"], .stApp, .stMarkdown,
        button, input, select, textarea,
        h1, h2, h3, h4, h5, h6, p, span, div, label {
            font-family: 'Nunito Sans', 'Source Sans Pro', sans-serif !important;
        }

        /* EXCEPCIÓN: los íconos de Streamlit usan la fuente Material Symbols;
           sin esto se muestran como texto (p.ej. "keyboard_double_arrow_right") */
        [data-testid="stIconMaterial"],
        [data-testid="stExpanderIcon"],
        .material-symbols-rounded,
        .material-symbols-outlined {
            font-family: 'Material Symbols Rounded' !important;
        }

        /* NAVEGACIÓN PRINCIPAL (st.radio "tab_selector") - ESTILO PESTAÑAS A TODO EL ANCHO */
        .st-key-tab_selector,
        .st-key-tab_selector > div,
        .st-key-tab_selector [data-testid="stRadio"],
        .st-key-tab_selector [data-testid="stRadio"] > div {
            width: 100% !important;
        }

        .st-key-tab_selector [role="radiogroup"] {
            display: flex !important;
            width: 100% !important;
            gap: 10px !important;
            background: #EAEAEA !important;
            padding: 10px !important;
            border-radius: 10px !important;
        }

        .st-key-tab_selector [role="radiogroup"] > label {
            flex: 1 1 0 !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 12px 8px !important;
            background: #e8e8e8 !important;
            border: 1px solid #cccccc !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
        }

        /* Ocultar el círculo del radio (todo hijo directo que no contenga el texto,
           robusto ante cambios de estructura entre versiones de Streamlit) */
        .st-key-tab_selector [role="radiogroup"] > label > div:not(:has([data-testid="stMarkdownContainer"])) {
            display: none !important;
        }

        .st-key-tab_selector [role="radiogroup"] > label p {
            font-weight: 600 !important;
            color: #666666 !important;
            font-size: 1rem !important;
        }

        .st-key-tab_selector [role="radiogroup"] > label:hover {
            background: #d5d5d5 !important;
            border-color: #999999 !important;
        }

        /* Pestaña activa en azul Ideca */
        .st-key-tab_selector [role="radiogroup"] > label:has(input:checked) {
            background: #003A5B !important;
            border-color: #003A5B !important;
            box-shadow: 0 4px 12px rgba(0, 58, 91, 0.4) !important;
        }

        .st-key-tab_selector [role="radiogroup"] > label:has(input:checked) p {
            color: white !important;
        }

        /* PESTAÑAS st.tabs (vista de administración) - DISTRIBUIDAS EN TODO EL ANCHO */
        .stTabs [data-baseweb="tab-list"] {
            background: #EAEAEA !important;
            border-radius: 10px 10px 0 0 !important;
            padding: 10px !important;
            border-bottom: 2px solid #ddd !important;
            display: flex !important;
            width: 100% !important;
            gap: 10px !important;
        }

        .stTabs [data-baseweb="tab"],
        .stTabs [data-baseweb="tab-list"] button[role="tab"] {
            flex: 1 1 0 !important;
            flex-grow: 1 !important;
            width: 100% !important;
            justify-content: center !important;
            text-align: center !important;
            background-color: #e8e8e8 !important;
            color: #666666 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            margin: 0 !important;
            padding: 12px 20px !important;
            border: 1px solid #cccccc !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #d5d5d5 !important;
            color: #444444 !important;
            border-color: #999999 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #003A5B !important;
            color: white !important;
            border-color: #003A5B !important;
            font-weight: 700 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0, 58, 91, 0.4) !important;
        }

        /* BOTONES */
        div.stButton > button:first-child {
            background-color: #003A5B !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:first-child:hover {
            background-color: #002A42 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        }

        /* MÉTRICAS */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.1) !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            border-left: 4px solid #003A5B !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #003A5B 0%, #002A42 100%) !important;
        }

        /* Todo el texto del sidebar en blanco para contraste sobre el azul */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            color: white !important;
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

# Configuración de columnas para Google Sheets - ACTUALIZADO
# NO renombrar columnas - mantener nombres originales
COLUMN_MAPPING = {
    # No hacemos renombres - las columnas mantienen sus nombres originales
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
    st.dataframe(example_df, width='stretch')
    
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
