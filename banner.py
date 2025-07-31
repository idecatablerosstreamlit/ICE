"""
Banner superior para Dashboard ICE - Integración con Streamlit
"""

import streamlit as st

def create_dashboard_banner():
    """Crear banner superior del Dashboard ICE estilo Datos Abiertos Bogotá"""
    
    banner_html = """
    <style>
        .header-blue {
            background: linear-gradient(90deg, #4472C4 0%, #3B5998 100%);
            padding: 10px 0;
            width: 100%;
            margin: -1rem -1rem 0 -1rem;
        }

        .header-blue-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
            max-width: 100%;
        }

        .gov-section {
            display: flex;
            align-items: center;
        }

        .gov-logo-link {
            display: flex;
            align-items: center;
            text-decoration: none;
            transition: opacity 0.3s ease;
        }

        .gov-logo-link:hover {
            opacity: 0.85;
        }

        .gov-logo {
            height: 28px;
            width: 28px;
            background: white;
            border-radius: 4px;
            margin-right: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #4472C4;
            font-size: 14px;
        }

        .gov-text {
            color: white;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .ir-govco {
            color: white;
            text-decoration: underline;
            font-size: 13px;
            font-weight: 400;
            transition: color 0.3s ease;
        }

        .ir-govco:hover {
            color: #E8F4FD;
        }

        .header-white {
            background: white;
            padding: 1rem 0;
            border-bottom: 3px solid #4472C4;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 0 -1rem 2rem -1rem;
        }

        .header-white-content {
            display: flex;
            align-items: center;
            padding: 0 2rem;
            gap: 1.5rem;
        }

        .ice-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(68, 114, 196, 0.25);
        }

        .dashboard-info {
            flex: 1;
        }

        .dashboard-title {
            color: #2C3E50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .dashboard-subtitle {
            color: #7F8C8D;
            font-size: 14px;
            font-weight: 400;
        }

        .bogota-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .alcaldia-logo {
            height: 45px;
            width: 45px;
            background: #003366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 8px;
            text-align: center;
            line-height: 1.1;
        }

        .bogota-logo {
            height: 40px;
            background: linear-gradient(45deg, #E31E24, #FFA500);
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 18px;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(227, 30, 36, 0.3);
        }

        @media (max-width: 768px) {
            .header-blue-content,
            .header-white-content {
                padding: 0 1rem;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .dashboard-title {
                font-size: 20px;
            }

            .gov-text {
                font-size: 18px;
            }
        }
    </style>

    <!-- Sección azul superior -->
    <div class="header-blue">
        <div class="header-blue-content">
            <div class="gov-section">
                <a href="https://www.gov.co/" class="gov-logo-link" target="_blank">
                    <div class="gov-logo">GOV</div>
                    <span class="gov-text">GOV.CO</span>
                </a>
            </div>
            <a href="https://www.gov.co/" class="ir-govco" target="_blank">Ir a Gov.co</a>
        </div>
    </div>

    <!-- Sección blanca con información del dashboard -->
    <div class="header-white">
        <div class="header-white-content">
            <div class="ice-icon">🏢</div>
            
            <div class="dashboard-info">
                <div class="dashboard-title">Dashboard ICE</div>
                <div class="dashboard-subtitle">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</div>
            </div>

            <div class="bogota-section">
                <div class="alcaldia-logo">
                    ALCALDÍA<br>MAYOR<br>DE BOGOTÁ D.C.
                </div>
                <div class="bogota-logo">BOGOTÁ</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

def create_dashboard_banner_with_images():
    """Versión del banner que usa imágenes reales (gov.png y Bogota.png)"""
    
    banner_html = """
    <style>
        .header-blue {
            background: linear-gradient(90deg, #4472C4 0%, #3B5998 100%);
            padding: 10px 0;
            width: 100%;
            margin: -1rem -1rem 0 -1rem;
        }

        .header-blue-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
            max-width: 100%;
        }

        .gov-section {
            display: flex;
            align-items: center;
        }

        .gov-logo-link {
            display: flex;
            align-items: center;
            text-decoration: none;
            transition: opacity 0.3s ease;
        }

        .gov-logo-link:hover {
            opacity: 0.85;
        }

        .gov-logo-img {
            height: 28px;
            width: auto;
            margin-right: 10px;
        }

        .gov-text {
            color: white;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .ir-govco {
            color: white;
            text-decoration: underline;
            font-size: 13px;
            font-weight: 400;
            transition: color 0.3s ease;
        }

        .ir-govco:hover {
            color: #E8F4FD;
        }

        .header-white {
            background: white;
            padding: 1rem 0;
            border-bottom: 3px solid #4472C4;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 0 -1rem 2rem -1rem;
        }

        .header-white-content {
            display: flex;
            align-items: center;
            padding: 0 2rem;
            gap: 1.5rem;
        }

        .ice-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(68, 114, 196, 0.25);
        }

        .dashboard-info {
            flex: 1;
        }

        .dashboard-title {
            color: #2C3E50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .dashboard-subtitle {
            color: #7F8C8D;
            font-size: 14px;
            font-weight: 400;
        }

        .bogota-logo-img {
            height: 60px;
            width: auto;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        @media (max-width: 768px) {
            .header-blue-content,
            .header-white-content {
                padding: 0 1rem;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .dashboard-title {
                font-size: 20px;
            }

            .gov-text {
                font-size: 18px;
            }
        }
    </style>

    <!-- Sección azul superior -->
    <div class="header-blue">
        <div class="header-blue-content">
            <div class="gov-section">
                <a href="https://www.gov.co/" class="gov-logo-link" target="_blank">
                    <img src="gov.png" alt="GOV.CO" class="gov-logo-img">
                    <span class="gov-text">GOV.CO</span>
                </a>
            </div>
            <a href="https://www.gov.co/" class="ir-govco" target="_blank">Ir a Gov.co</a>
        </div>
    </div>

    <!-- Sección blanca con información del dashboard -->
    <div class="header-white">
        <div class="header-white-content">
            <div class="ice-icon">🏢</div>
            
            <div class="dashboard-info">
                <div class="dashboard-title">Dashboard ICE</div>
                <div class="dashboard-subtitle">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</div>
            </div>

            <img src="Bogota.png" alt="Bogotá" class="bogota-logo-img">
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

def create_government_banner_with_real_logos():
    """Versión del banner estilo GOV.CO para Dashboard ICE"""
    
    banner_html = """
    <style>
        /* Reset para eliminar espacios de Streamlit */
        .main > div {
            padding-top: 0rem !important;
        }
        
        /* Sección azul GOV.CO */
        .gov-header {
            background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
            padding: 12px 0;
            width: 100%;
            margin: -1rem -1rem 0 -1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .gov-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .gov-left {
            display: flex;
            align-items: center;
        }

        .gov-logo-link {
            display: flex;
            align-items: center;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .gov-logo-link:hover {
            opacity: 0.85;
        }

        .gov-logo-img {
            height: 32px;
            width: auto;
            margin-right: 12px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        .gov-escudo-placeholder {
            width: 32px;
            height: 32px;
            background: white;
            border-radius: 6px;
            margin-right: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #4A6CF7;
            font-size: 12px;
        }

        .gov-text {
            color: white;
            font-size: 22px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .gov-link {
            color: white;
            text-decoration: underline;
            font-size: 14px;
            font-weight: 400;
            transition: all 0.3s ease;
        }

        .gov-link:hover {
            color: #E8F4FD;
            text-decoration: none;
        }

        /* Sección blanca Dashboard */
        .dashboard-header {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
            padding: 20px 0;
            border-bottom: 3px solid #4472C4;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            margin: 0 -1rem 2rem -1rem;
        }

        .dashboard-content {
            display: flex;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            gap: 20px;
        }

        .ice-logo {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
            box-shadow: 0 6px 20px rgba(68, 114, 196, 0.3);
        }

        .dashboard-info {
            flex: 1;
        }

        .dashboard-title {
            color: #2C3E50;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .dashboard-subtitle {
            color: #6C757D;
            font-size: 16px;
            font-weight: 400;
            line-height: 1.4;
        }

        .bogota-section {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .bogota-logo-img {
            height: 70px;
            width: auto;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));
        }

        .bogota-placeholder {
            background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
            padding: 12px 20px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            font-size: 20px;
            letter-spacing: 1.5px;
            box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
        }

        .alcaldia-placeholder {
            width: 55px;
            height: 55px;
            background: linear-gradient(135deg, #003366 0%, #004080 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 8px;
            font-weight: bold;
            text-align: center;
            line-height: 1.1;
            box-shadow: 0 4px 12px rgba(0, 51, 102, 0.3);
        }

        /* Responsivo */
        @media (max-width: 768px) {
            .gov-content,
            .dashboard-content {
                flex-direction: column;
                text-align: center;
                gap: 15px;
                padding: 0 1rem;
            }
            
            .dashboard-title {
                font-size: 24px;
            }
            
            .dashboard-subtitle {
                font-size: 14px;
            }
        }
    </style>

    <!-- Sección azul GOV.CO -->
    <div class="gov-header">
        <div class="gov-content">
            <div class="gov-left">
                <a href="https://www.gov.co/" class="gov-logo-link" target="_blank">
                    <img src="gov.png" alt="GOV.CO" class="gov-logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="gov-escudo-placeholder" style="display: none;">🏛️</div>
                    <span class="gov-text">GOV.CO</span>
                </a>
            </div>
            <a href="https://www.gov.co/" class="gov-link" target="_blank">Ir a Gov.co</a>
        </div>
    </div>

    <!-- Sección blanca Dashboard -->
    <div class="dashboard-header">
        <div class="dashboard-content">
            <div class="ice-logo">🏢</div>
            
            <div class="dashboard-info">
                <div class="dashboard-title">Dashboard ICE</div>
                <div class="dashboard-subtitle">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</div>
            </div>

            <div class="bogota-section">
                <div class="alcaldia-placeholder">
                    ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.
                </div>
                <img src="Bogota.png" alt="Bogotá" class="bogota-logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div class="bogota-placeholder" style="display: none;">BOGOTÁ</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

# Para usar en tu main.py, simplemente importa y llama la función:
# from banner import create_dashboard_banner
# create_dashboard_banner()

# O si tienes las imágenes:
# create_dashboard_banner_with_images()
