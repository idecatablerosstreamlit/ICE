"""
Banner superior para Dashboard ICE - VERSIÓN SIMPLIFICADA QUE FUNCIONA
"""

import streamlit as st

def create_government_banner_with_real_logos():
    """Banner simplificado y funcional para Dashboard ICE"""
    
    # Sección azul GOV.CO
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #4A6CF7 0%, #667eea 100%);
        padding: 15px;
        margin: -1rem -1rem 0 -1rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    ">
        <div style="display: flex; align-items: center;">
            <div style="
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
            ">🏛️</div>
            <span style="
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 0.5px;
            ">GOV.CO</span>
        </div>
        <a href="https://www.gov.co/" target="_blank" style="
            color: white;
            text-decoration: underline;
            font-size: 14px;
        ">Ir a Gov.co</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección blanca Dashboard
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 25px 15px;
        margin: 0 -1rem 2rem -1rem;
        border-bottom: 4px solid #4472C4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    ">
        <div style="
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
        ">🏢</div>
        
        <div style="flex: 1; min-width: 300px;">
            <h1 style="
                color: #2C3E50;
                font-size: 32px;
                font-weight: 700;
                margin: 0 0 8px 0;
                background: linear-gradient(135deg, #4472C4 0%, #5B9BD5 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">Dashboard ICE</h1>
            <p style="
                color: #6C757D;
                font-size: 16px;
                margin: 0;
                font-weight: 500;
            ">Sistema de Monitoreo - Infraestructura de Conocimiento Espacial - IDECA</p>
        </div>

        <div style="
            display: flex;
            align-items: center;
            gap: 20px;
            flex-shrink: 0;
        ">
            <div style="
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
            ">ALCALDÍA<br>MAYOR<br>DE BOGOTÁ<br>D.C.</div>
            
            <div style="
                background: linear-gradient(45deg, #E31E24 0%, #FF6B35 100%);
                padding: 12px 20px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                font-size: 18px;
                letter-spacing: 1.5px;
                box-shadow: 0 4px 15px rgba(227, 30, 36, 0.4);
            ">BOGOTÁ</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Funciones de compatibilidad
def create_dashboard_banner():
    create_government_banner_with_real_logos()

def create_dashboard_banner_with_images():
    create_government_banner_with_real_logos()
