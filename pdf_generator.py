# Archivo: pdf_generator.py - VERSIÓN CORREGIDA

"""
Generador de PDFs para fichas metodológicas del Dashboard ICE - CORREGIDO
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Importación condicional de reportlab
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class PDFGenerator:
    """Generador de fichas metodológicas en PDF - CORREGIDO"""
    
    def __init__(self):
        self.pdf_available = PDF_AVAILABLE
    
    def generate_metodological_sheet(self, codigo, excel_data):
        """Generar ficha metodológica en PDF - MÉTODO PRINCIPAL CORREGIDO"""
        try:
            if not self.pdf_available:
                st.error("📦 **Para descargar PDFs instala:** `pip install reportlab`")
                return None
            
            if excel_data is None or excel_data.empty:
                st.error("❌ No hay datos metodológicos disponibles. Asegúrate de que 'Batería de indicadores.xlsx' esté en el directorio.")
                return None
            
            # Buscar datos del indicador
            indicador_data = excel_data[excel_data['Codigo'] == codigo]
            
            if indicador_data.empty:
                st.error(f"❌ No se encontraron datos metodológicos para el código {codigo}")
                
                # Mostrar códigos disponibles
                codigos_disponibles = excel_data['Codigo'].dropna().unique().tolist()
                if codigos_disponibles:
                    st.info(f"💡 Códigos disponibles en Excel: {', '.join(map(str, codigos_disponibles[:10]))}")
                    if len(codigos_disponibles) > 10:
                        st.info(f"... y {len(codigos_disponibles) - 10} más")
                
                return None
            
            # Obtener datos del indicador
            datos = indicador_data.iloc[0]
            
            # Crear documento PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Crear estilos
            story = self._build_pdf_content(datos, codigo)
            
            # Generar PDF
            doc.build(story)
            
            # Obtener datos del buffer
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            st.error(f"❌ Error al generar PDF: {e}")
            import traceback
            with st.expander("🔧 Detalles del error"):
                st.code(traceback.format_exc())
            return None
    
    def _build_pdf_content(self, datos, codigo):
        """Construir contenido del PDF"""
        # Crear estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4472C4')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#4472C4')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        )
        
        # Construir contenido del documento
        story = []
        
        # Título principal
        story.append(Paragraph("FICHA METODOLÓGICA DE INDICADOR", title_style))
        story.append(Paragraph("Dashboard ICE - Infraestructura de Conocimiento Espacial", normal_style))
        story.append(Spacer(1, 20))
        
        # Información institucional
        institucion_data = [
            ['Sistema:', 'Dashboard ICE - Infraestructura de Conocimiento Espacial'],
            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Código del indicador:', codigo]
        ]
        
        institucion_table = Table(institucion_data, colWidths=[2*inch, 4*inch])
        institucion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(institucion_table)
        story.append(Spacer(1, 20))
        
        # 1. INFORMACIÓN BÁSICA
        story.append(Paragraph("1. INFORMACIÓN BÁSICA", subtitle_style))
        
        basic_data = [
            ['Nombre del indicador:', self._safe_get(datos, 'Nombre_Indicador', 'N/A')],
            ['Código:', codigo],
            ['Área temática:', self._safe_get(datos, 'Area_Tematica', 'N/A')],
            ['Tema:', self._safe_get(datos, 'Tema', 'N/A')],
            ['Sector:', self._safe_get(datos, 'Sector', 'N/A')],
            ['Entidad responsable:', self._safe_get(datos, 'Entidad', 'N/A')],
            ['Dependencia:', self._safe_get(datos, 'Dependencia', 'N/A')]
        ]
        
        basic_table = self._create_table(basic_data)
        story.append(basic_table)
        story.append(Spacer(1, 15))
        
        # 2. DEFINICIÓN Y OBJETIVO
        story.append(Paragraph("2. DEFINICIÓN Y OBJETIVO", subtitle_style))
        
        story.append(Paragraph("<b>Definición:</b>", normal_style))
        story.append(Paragraph(self._safe_get(datos, 'Definicion', 'No disponible'), normal_style))
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("<b>Objetivo:</b>", normal_style))
        story.append(Paragraph(self._safe_get(datos, 'Objetivo', 'No disponible'), normal_style))
        story.append(Spacer(1, 15))
        
        # 3. METODOLOGÍA DE CÁLCULO
        story.append(Paragraph("3. METODOLOGÍA DE CÁLCULO", subtitle_style))
        
        methodology_data = [
            ['Fórmula de cálculo:', self._safe_get(datos, 'Formula_Calculo', 'N/A')],
            ['Variables:', self._safe_get(datos, 'Variables', 'N/A')],
            ['Unidad de medida:', self._safe_get(datos, 'Unidad_Medida', 'N/A')],
            ['Metodología de cálculo:', self._safe_get(datos, 'Metodologia_Calculo', 'N/A')],
            ['Tipo de acumulación:', self._safe_get(datos, 'Tipo_Acumulacion', 'N/A')]
        ]
        
        methodology_table = self._create_table(methodology_data)
        story.append(methodology_table)
        story.append(Spacer(1, 15))
        
        # 4. INFORMACIÓN TÉCNICA
        story.append(Paragraph("4. INFORMACIÓN TÉCNICA", subtitle_style))
        
        technical_data = [
            ['Fuente de información:', self._safe_get(datos, 'Fuente_Informacion', 'N/A')],
            ['Tipo de indicador:', self._safe_get(datos, 'Tipo_Indicador', 'N/A')],
            ['Periodicidad:', self._safe_get(datos, 'Periodicidad', 'N/A')],
            ['Desagregación geográfica:', self._safe_get(datos, 'Desagregacion_Geografica', 'N/A')],
            ['Desagregación poblacional:', self._safe_get(datos, 'Desagregacion_Poblacional', 'N/A')],
            ['Clasificación según calidad:', self._safe_get(datos, 'Clasificacion_Calidad', 'N/A')],
            ['Clasificación según intervención:', self._safe_get(datos, 'Clasificacion_Intervencion', 'N/A')]
        ]
        
        technical_table = self._create_table(technical_data)
        story.append(technical_table)
        story.append(Spacer(1, 15))
        
        # 5. OBSERVACIONES Y LIMITACIONES
        observaciones = self._safe_get(datos, 'Observaciones', '')
        limitaciones = self._safe_get(datos, 'Limitaciones', '')
        interpretacion = self._safe_get(datos, 'Interpretacion', '')
        
        if observaciones or limitaciones or interpretacion:
            story.append(Paragraph("5. OBSERVACIONES Y LIMITACIONES", subtitle_style))
            
            if observaciones:
                story.append(Paragraph("<b>Observaciones:</b>", normal_style))
                story.append(Paragraph(observaciones, normal_style))
                story.append(Spacer(1, 8))
            
            if limitaciones:
                story.append(Paragraph("<b>Limitaciones:</b>", normal_style))
                story.append(Paragraph(limitaciones, normal_style))
                story.append(Spacer(1, 8))
            
            if interpretacion:
                story.append(Paragraph("<b>Interpretación:</b>", normal_style))
                story.append(Paragraph(interpretacion, normal_style))
                story.append(Spacer(1, 15))
        
        # 6. INFORMACIÓN DE CONTACTO
        story.append(Paragraph("6. INFORMACIÓN DE CONTACTO", subtitle_style))
        
        contact_data = [
            ['Directivo responsable:', self._safe_get(datos, 'Directivo_Responsable', 'N/A')],
            ['Correo electrónico:', self._safe_get(datos, 'Correo_Directivo', 'N/A')],
            ['Teléfono de contacto:', self._safe_get(datos, 'Telefono_Contacto', 'N/A')]
        ]
        
        contact_table = self._create_table(contact_data)
        story.append(contact_table)
        
        # 7. ENLACES Y SOPORTE LEGAL
        enlaces = self._safe_get(datos, 'Enlaces_Web', '')
        soporte = self._safe_get(datos, 'Soporte_Legal', '')
        
        if enlaces:
            story.append(Spacer(1, 15))
            story.append(Paragraph("7. ENLACES RELACIONADOS", subtitle_style))
            story.append(Paragraph(enlaces, normal_style))
        
        if soporte:
            story.append(Spacer(1, 15))
            story.append(Paragraph("8. SOPORTE LEGAL", subtitle_style))
            story.append(Paragraph(soporte, normal_style))
        
        return story
    
    def _safe_get(self, datos, campo, default='N/A'):
        """Obtener valor de forma segura manejando NaN"""
        try:
            valor = datos.get(campo, default)
            if pd.isna(valor) or valor == '' or str(valor).strip() == '':
                return default
            return str(valor).strip()
        except:
            return default
    
    def _create_table(self, data):
        """Crear tabla con estilo consistente"""
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7F3FF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        return table
    
    def is_available(self):
        """Verificar si PDF está disponible"""
        return self.pdf_available
