"""
Banner superior para Dashboard ICE - VERSIÓN DEFINITIVA FUNCIONAL
Compatible con el tema existente del dashboard
"""

import streamlit as st

def create_government_banner_with_real_logos():
    """
    Banner estilo GOV.CO integrado con el Dashboard ICE
    Esta versión es compatible con apply_dark_theme()
    """
    
    # Sección azul GOV.CO usando columnas de Streamlit
    gov_col1, gov_col2 = st.columns([3, 1])
    
    with gov_col1:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
            padding: 15px 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            margin-bottom: 0;
        ">
            <div style="
                width: 32px;
                height: 32px;
                background: white;
                border-radius: 6px;
                margin-right: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: #4A6CF7;
                font-size: 14px;
            ">🏛️</div>
            <span style="
                color: white;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-shadow: 0 1px 3px rgba(0,0,0,0.2);
            ">GOV.CO</span>
        </div>
        """, unsafe_allow_html=True)
    
    with gov_col2:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
            padding: 15px 20px;
            border-radius: 8px;
            text-align: right;
            margin-bottom: 0;
        ">
            <a href="https://www.gov.co/" target="_blank" style="
                color: white;
                text-decoration: underline;
                font-size: 14px;
                font-weight: 500;
            ">Ir a Gov.co</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Espacio pequeño
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sección principal del Dashboard usando columnas
    dash_col1, dash_col2, dash_col3 = st.columns([1, 4, 2])
    
    with dash_col1:
        st.markdown("""
        <div style="
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 6px 20px rgba(68, 114, 196, 0.3);
            margin: 0 auto;
        ">🏢</div>
        """, unsafe_allow_html=True)
    
    with dash_col2:
        st.markdown("""
        <div style="text-align: left; padding: 10px 0;">
            <h1 style="
                color: #2C3E50;
                font-size: 36px;
                font-weight: 700;
                margin: 0 0 8px 0;
                background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.2;
            ">Dashboard ICE</h1>
            <p style="
                color: #6C757D;
                font-size: 18px;
                margin: 0;
                font-weight: 500;
                line-height: 1.4;
            ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dash_col3:
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            padding: 10px 0;
        ">
            <div style="
                width: 60px;
                height: 60px;
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
            ">ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.</div>
            
            <div style="
                background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                padding: 12px 18px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                font-size: 18px;
                letter-spacing: 1.5px;
                box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
            ">BOGOTÁ</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Línea separadora con estilo
    st.markdown("""
    <hr style="
        margin: 20px 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #4472C4 0%, #5B9BD5 100%);
        border-radius: 2px;
    ">
    """, unsafe_allow_html=True)

def create_simple_government_banner():
    """Versión simplificada del banner para pruebas"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: white;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                ">🏛️</div>
                <span style="font-size: 28px; font-weight: 700;">GOV.CO</span>
            </div>
            <a href="https://www.gov.co/" target="_blank" style="
                color: white;
                text-decoration: underline;
                font-size: 16px;
            ">Ir a Gov.co</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 30px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        border: 3px solid #4472C4;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; gap: 25px; flex-wrap: wrap; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    width: 70px;
                    height: 70px;
                    background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                    border-radius: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 30px;
                    font-weight: bold;
                    box-shadow: 0 6px 20px rgba(68, 114, 196, 0.4);
                ">🏢</div>
                
                <div>
                    <h1 style="
                        color: #2C3E50;
                        font-size: 36px;
                        font-weight: 700;
                        margin: 0 0 8px 0;
                        background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    ">Dashboard ICE</h1>
                    <p style="
                        color: #6C757D;
                        font-size: 18px;
                        margin: 0;
                        font-weight: 500;
                    ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    width: 65px;
                    height: 65px;
                    background: linear-gradient(135deg, #003366 0%, #004080 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 9px;
                    font-weight: bold;
                    text-align: center;
                    line-height: 1.1;
                    box-shadow: 0 6px 20px rgba(0, 51, 102, 0.4);
                ">ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.</div>
                
                <div style="
                    background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                    padding: 15px 25px;
                    border-radius: 30px;
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    letter-spacing: 2px;
                    box-shadow: 0 6px 20px rgba(227, 30, 36, 0.4);
                ">BOGOTÁ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Funciones de compatibilidad
def create_dashboard_banner():
    create_government_banner_with_real_logos()

def create_dashboard_banner_with_images():
    create_government_banner_with_real_logos()
