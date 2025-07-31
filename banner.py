"""
Banner superior para Dashboard ICE - Integración con Streamlit CORREGIDO
"""

import streamlit as st

def create_government_banner_with_real_logos():
    """Banner estilo GOV.CO para Dashboard ICE - VERSIÓN CORREGIDA"""
    
    banner_html = """
    <style>
        /* Reset Streamlit */
        .stApp > header {
            display: none !important;
        }
        
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem;
            max-width: 100% !important;
        }
        
        /* Sección azul GOV.CO */
        .gov-header {
            background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
            padding: 15px 0;
            width: 100vw;
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            margin-top: -1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 1000;
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
            cursor: pointer;
        }

        .gov-logo-link:hover {
            opacity: 0.85;
            transform: translateY(-1px);
        }

        .gov-escudo {
            width: 36px;
            height: 36px;
            background: white;
            border-radius: 8px;
            margin-right: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #4A6CF7;
            font-size: 14px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
            border: 2px solid rgba(255,255,255,0.3);
        }

        .gov-text {
            color: white;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .gov-link {
            color: white;
            text-decoration: underline;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .gov-link:hover {
            color: #E8F4FD;
            text-decoration: none;
            transform: translateY(-1px);
        }

        /* Sección blanca Dashboard */
        .dashboard-header {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
            padding: 25px 0;
            width: 100vw;
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            margin-bottom: 2rem;
            border-bottom: 4px solid #4472C4;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        }

        .dashboard-content {
            display: flex;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            gap: 25px;
        }

        .ice-logo {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 8px 25px rgba(68, 114, 196, 0.35);
            border: 3px solid rgba(255,255,255,0.3);
            flex-shrink: 0;
        }

        .dashboard-info {
            flex: 1;
            min-width: 0;
        }

        .dashboard-title {
            color: #2C3E50;
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }

        .dashboard-subtitle {
            color: #6C757D;
            font-size: 18px;
            font-weight: 500;
            line-height: 1.4;
        }

        .bogota-section {
            display: flex;
            align-items: center;
            gap: 25px;
            flex-shrink: 0;
        }

        .alcaldia-shield {
            width: 65px;
            height: 65px;
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
            box-shadow: 0 6px 20px rgba(0, 51, 102, 0.4);
            border: 3px solid rgba(255,255,255,0.2);
        }

        .bogota-brand {
            background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
            padding: 15px 25px;
            border-radius: 30px;
            color: white;
            font-weight: bold;
            font-size: 22px;
            letter-spacing: 2px;
            box-shadow: 0 6px 20px rgba(227, 30, 36, 0.4);
            border: 3px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }

        .bogota-brand:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(227, 30, 36, 0.5);
        }

        /* Responsivo */
        @media (max-width: 992px) {
            .dashboard-title {
                font-size: 30px;
            }
            
            .dashboard-subtitle {
                font-size: 16px;
            }
            
            .bogota-section {
                gap: 20px;
            }
        }

        @media (max-width: 768px) {
            .gov-content,
            .dashboard-content {
                flex-direction: column;
                text-align: center;
                gap: 20px;
                padding: 0 1rem;
            }
            
            .dashboard-title {
                font-size: 26px;
            }
            
            .dashboard-subtitle {
                font-size: 15px;
            }
            
            .ice-logo {
                width: 60px;
                height: 60px;
                font-size: 24px;
            }
            
            .bogota-section {
                justify-content: center;
                margin-top: 10px;
            }
        }

        @media (max-width: 480px) {
            .gov-text {
                font-size: 20px;
            }
            
            .dashboard-title {
                font-size: 22px;
            }
            
            .dashboard-subtitle {
                font-size: 14px;
            }
            
            .bogota-brand {
                font-size: 18px;
                padding: 12px 20px;
            }
            
            .alcaldia-shield {
                width: 55px;
                height: 55px;
                font-size: 7px;
            }
        }
    </style>

    <!-- Sección azul GOV.CO -->
    <div class="gov-header">
        <div class="gov-content">
            <div class="gov-left">
                <a href="https://www.gov.co/" class="gov-logo-link" target="_blank">
                    <div class="gov-escudo">🏛️</div>
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
                <div class="alcaldia-shield">
                    ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.
                </div>
                <div class="bogota-brand">BOGOTÁ</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

# Funciones de compatibilidad
def create_dashboard_banner():
    """Función de compatibilidad"""
    create_government_banner_with_real_logos()

def create_dashboard_banner_with_images():
    """Función de compatibilidad"""
    create_government_banner_with_real_logos()
