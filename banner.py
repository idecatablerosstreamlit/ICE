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

# Para usar en tu main.py, simplemente importa y llama la función:
# from banner import create_dashboard_banner
# create_dashboard_banner()

# O si tienes las imágenes:
# create_dashboard_banner_with_images()