# Funciones de compatibilidad
def create_dashboard_banner():
    create_government_banner_with_real_logos()

def create_dashboard_banner_with_images():
    create_banner_with_local_images()  # Usa la versión con imágenes locales"""
Banner superior para Dashboard ICE - COMPONENTE HTML COMPLETO
Esta versión usa st.components.v1.html() para control total del diseño
"""

import streamlit as st
import streamlit.components.v1 as components

def create_government_banner_with_real_logos():
    """Banner completo usando componente HTML"""
    
    banner_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Source Sans Pro', sans-serif;
                background: white;
            }

            /* Sección azul GOV.CO */
            .gov-header {
                background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
                padding: 15px 0;
                width: 100%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .gov-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }

            .gov-left {
                display: flex;
                align-items: center;
            }

            .gov-logo-link {
                display: flex;
                align-items: center;
                text-decoration: none;
                transition: opacity 0.3s ease;
                cursor: pointer;
            }

            .gov-logo-link:hover {
                opacity: 0.85;
            }

            .gov-logo {
                height: 32px;
                width: auto;
                margin-right: 12px;
            }

            .gov-escudo {
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
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
                transition: color 0.3s ease;
                cursor: pointer;
            }

            .gov-link:hover {
                color: #E8F4FD;
                text-decoration: none;
            }

            /* Sección blanca Dashboard */
            .dashboard-header {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
                padding: 25px 0;
                border-bottom: 3px solid #4472C4;
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            }

            .dashboard-content {
                display: flex;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                gap: 25px;
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
                flex-shrink: 0;
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
                flex-shrink: 0;
            }

            .bogota-logo {
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
                font-size: 18px;
                letter-spacing: 1.5px;
                box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
            }

            .alcaldia-shield {
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
                    padding: 0 15px;
                }
                
                .dashboard-title {
                    font-size: 24px;
                }
                
                .dashboard-subtitle {
                    font-size: 14px;
                }
            }
        </style>
        <script>
            function openGovCo() {
                window.open('https://www.gov.co/', '_blank');
            }
        </script>
    </head>
    <body>
        <!-- Sección azul GOV.CO -->
        <div class="gov-header">
            <div class="gov-content">
                <div class="gov-left">
                    <div class="gov-logo-link" onclick="openGovCo()">
                        <div class="gov-escudo">🏛️</div>
                        <span class="gov-text">GOV.CO</span>
                    </div>
                </div>
                <div class="gov-link" onclick="openGovCo()">Ir a Gov.co</div>
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
                    <div class="bogota-placeholder">BOGOTÁ</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Renderizar como componente HTML completo
    components.html(banner_html, height=200, scrolling=False)

# Función alternativa más simple si la anterior no funciona
def create_simple_banner():
    """Banner simplificado usando componente HTML"""
    
    simple_html = """
    <div style="
        background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 15px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="
                    width: 28px;
                    height: 28px;
                    background: white;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #4A6CF7;
                    font-weight: bold;
                    font-size: 12px;
                ">🏛️</div>
                <span style="font-size: 20px; font-weight: 600;">GOV.CO</span>
            </div>
            <a href="https://www.gov.co/" target="_blank" style="color: white; text-decoration: underline; font-size: 13px;">Ir a Gov.co</a>
        </div>
    </div>
    
    <div style="
        background: white;
        padding: 25px;
        border: 3px solid #4472C4;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    box-shadow: 0 4px 12px rgba(68, 114, 196, 0.3);
                ">🏢</div>
                <div>
                    <h1 style="
                        color: #2C3E50;
                        font-size: 28px;
                        font-weight: 700;
                        margin: 0 0 5px 0;
                        background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    ">Dashboard ICE</h1>
                    <p style="color: #6C757D; font-size: 14px; margin: 0;">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
                </div>
            </div>
            <div style="
                background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                padding: 10px 18px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                font-size: 16px;
                letter-spacing: 1px;
                box-shadow: 0 3px 10px rgba(227, 30, 36, 0.4);
            ">BOGOTÁ</div>
        </div>
    </div>
    """
    
    components.html(simple_html, height=180, scrolling=False)

# Función que usa imágenes locales
def create_banner_with_local_images():
    """Banner que usa las imágenes locales gov.png y Bogota.png"""
    
    # Primero intentamos cargar las imágenes como base64
    import base64
    import os
    
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return None
    
    gov_img_b64 = get_base64_image("gov.png")
    bogota_img_b64 = get_base64_image("Bogota.png")
    
    banner_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
            
            .gov-header {{
                background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
                padding: 15px 0;
                width: 100%;
            }}
            
            .gov-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            
            .gov-left {{ display: flex; align-items: center; cursor: pointer; }}
            .gov-text {{ color: white; font-size: 22px; font-weight: 600; margin-left: 12px; }}
            .gov-link {{ color: white; text-decoration: underline; font-size: 14px; cursor: pointer; }}
            .gov-logo {{ height: 32px; width: auto; }}
            .gov-escudo {{ width: 32px; height: 32px; background: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #4A6CF7; font-weight: bold; }}
            
            .dashboard-header {{
                background: white;
                padding: 25px 0;
                border-bottom: 3px solid #4472C4;
            }}
            
            .dashboard-content {{
                display: flex;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                gap: 25px;
            }}
            
            .ice-logo {{
                width: 60px; height: 60px;
                background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                border-radius: 12px; display: flex; align-items: center; justify-content: center;
                color: white; font-size: 24px; font-weight: bold;
            }}
            
            .dashboard-info {{ flex: 1; }}
            .dashboard-title {{ color: #2C3E50; font-size: 32px; font-weight: 700; margin-bottom: 6px; }}
            .dashboard-subtitle {{ color: #6C757D; font-size: 16px; }}
            
            .bogota-section {{ display: flex; align-items: center; gap: 20px; }}
            .alcaldia-shield {{
                width: 55px; height: 55px; background: linear-gradient(135deg, #003366 0%, #004080 100%);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                color: white; font-size: 8px; font-weight: bold; text-align: center; line-height: 1.1;
            }}
            .bogota-logo {{ height: 70px; width: auto; }}
            .bogota-placeholder {{ 
                background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                padding: 12px 20px; border-radius: 25px; color: white; font-weight: bold; font-size: 18px;
            }}
        </style>
        <script>
            function openGovCo() {{
                window.open('https://www.gov.co/', '_blank');
            }}
        </script>
    </head>
    <body>
        <div class="gov-header">
            <div class="gov-content">
                <div class="gov-left" onclick="openGovCo()">
                    {"<img src='data:image/png;base64," + gov_img_b64 + "' alt='GOV.CO' class='gov-logo'>" if gov_img_b64 else "<div class='gov-escudo'>🏛️</div>"}
                    <span class="gov-text">GOV.CO</span>
                </div>
                <div class="gov-link" onclick="openGovCo()">Ir a Gov.co</div>
            </div>
        </div>
        
        <div class="dashboard-header">
            <div class="dashboard-content">
                <div class="ice-logo">🏢</div>
                <div class="dashboard-info">
                    <div class="dashboard-title">Dashboard ICE</div>
                    <div class="dashboard-subtitle">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</div>
                </div>
                <div class="bogota-section">
                    <div class="alcaldia-shield">ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.</div>
                    {"<img src='data:image/png;base64," + bogota_img_b64 + "' alt='Bogotá' class='bogota-logo'>" if bogota_img_b64 else "<div class='bogota-placeholder'>BOGOTÁ</div>"}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    components.html(banner_html, height=200, scrolling=False)
