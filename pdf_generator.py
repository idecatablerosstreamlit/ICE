"""
Generador de PDFs para fichas metodológicas del Dashboard ICE
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
    """Generador de fichas metodológicas en PDF"""
    
    def __init__(self):
        self.pdf_available = PDF_AVAILABLE
    
    def generate_metodological_sheet(self, codigo, excel_data):
        """Generar ficha metodológica en PDF"""
        try:
            if not self.pdf_available:
                st.error("📦 **Falta instalar reportlab:** `pip install reportlab`")
                return None
            
            # Buscar datos del indicador
            indicador_data = excel_data[excel_data['Codigo'] == codigo]
            
            if indicador_data.empty:
                st.error(f"❌ No se encontraron datos metodológicos para {codigo}")
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
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#4472C4')
            )
            
            # Estilo para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#4472C4')
            )
            
            # Estilo para texto normal
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
            story.append(Spacer(1, 12))
            
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
            
            # Información básica del indicador
            story.append(Paragraph("1. INFORMACIÓN BÁSICA", subtitle_style))
            
            basic_data = [
                ['Nombre del indicador:', datos.get('Nombre_Indicador', 'N/A')],
                ['Código:', codigo],
                ['Área temática:', datos.get('Area_Tematica', 'N/A')],
                ['Tema:', datos.get('Tema', 'N/A')],
                ['Sector:', datos.get('Sector', 'N/A')],
                ['Entidad responsable:', datos.get('Entidad', 'N/A')],
                ['Dependencia:', datos.get('Dependencia', 'N/A')]
            ]
            
            basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7F3FF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(basic_table)
            story.append(Spacer(1, 15))
            
            # Definición y objetivo
            story.append(Paragraph("2. DEFINICIÓN Y OBJETIVO", subtitle_style))
            
            story.append(Paragraph("<b>Definición:</b>", normal_style))
            story.append(Paragraph(datos.get('Definicion', 'No disponible'), normal_style))
            story.append(Spacer(1, 8))
            
            story.append(Paragraph("<b>Objetivo:</b>", normal_style))
            story.append(Paragraph(datos.get('Objetivo', 'No disponible'), normal_style))
            story.append(Spacer(1, 15))
            
            # Metodología de cálculo
            story.append(Paragraph("3. METODOLOGÍA DE CÁLCULO", subtitle_style))
            
            methodology_data = [
                ['Fórmula de cálculo:', datos.get('Formula_Calculo', 'N/A')],
                ['Variables:', datos.get('Variables', 'N/A')],
                ['Unidad de medida:', datos.get('Unidad_Medida', 'N/A')],
                ['Metodología de cálculo:', datos.get('Metodologia_Calculo', 'N/A')],
                ['Tipo de acumulación:', datos.get('Tipo_Acumulacion', 'N/A')]
            ]
            
            methodology_table = Table(methodology_data, colWidths=[2*inch, 4*inch])
            methodology_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7F3FF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(methodology_table)
            story.append(Spacer(1, 15))
            
            # Información técnica
            story.append(Paragraph("4. INFORMACIÓN TÉCNICA", subtitle_style))
            
            technical_data = [
                ['Fuente de información:', datos.get('Fuente_Informacion', 'N/A')],
                ['Tipo de indicador:', datos.get('Tipo_Indicador', 'N/A')],
                ['Periodicidad:', datos.get('Periodicidad', 'N/A')],
                ['Desagregación geográfica:', datos.get('Desagregacion_Geografica', 'N/A')],
                ['Desagregación poblacional:', datos.get('Desagregacion_Poblacional', 'N/A')],
                ['Clasificación según calidad:', datos.get('Clasificacion_Calidad', 'N/A')],
                ['Clasificación según intervención:', datos.get('Clasificacion_Intervencion', 'N/A')]
            ]
            
            technical_table = Table(technical_data, colWidths=[2*inch, 4*inch])
            technical_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7F3FF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(technical_table)
            story.append(Spacer(1, 15))
            
            # Observaciones y limitaciones
            if datos.get('Observaciones') or datos.get('Limitaciones'):
                story.append(Paragraph("5. OBSERVACIONES Y LIMITACIONES", subtitle_style))
                
                if datos.get('Observaciones'):
                    story.append(Paragraph("<b>Observaciones:</b>", normal_style))
                    story.append(Paragraph(datos.get('Observaciones', 'N/A'), normal_style))
                    story.append(Spacer(1, 8))
                
                if datos.get('Limitaciones'):
                    story.append(Paragraph("<b>Limitaciones:</b>", normal_style))
                    story.append(Paragraph(datos.get('Limitaciones', 'N/A'), normal_style))
                    story.append(Spacer(1, 8))
                
                if datos.get('Interpretacion'):
                    story.append(Paragraph("<b>Interpretación:</b>", normal_style))
                    story.append(Paragraph(datos.get('Interpretacion', 'N/A'), normal_style))
                    story.append(Spacer(1, 15))
            
            # Información de contacto
            story.append(Paragraph("6. INFORMACIÓN DE CONTACTO", subtitle_style))
            
            contact_data = [
                ['Directivo responsable:', datos.get('Directivo_Responsable', 'N/A')],
                ['Correo electrónico:', datos.get('Correo_Directivo', 'N/A')],
                ['Teléfono de contacto:', datos.get('Telefono_Contacto', 'N/A')]
            ]
            
            contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
            contact_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7F3FF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(contact_table)
            
            # Enlaces web
            if datos.get('Enlaces_Web'):
                story.append(Spacer(1, 15))
                story.append(Paragraph("7. ENLACES RELACIONADOS", subtitle_style))
                story.append(Paragraph(datos.get('Enlaces_Web', 'N/A'), normal_style))
            
            # Soporte legal
            if datos.get('Soporte_Legal'):
                story.append(Spacer(1, 15))
                story.append(Paragraph("8. SOPORTE LEGAL", subtitle_style))
                story.append(Paragraph(datos.get('Soporte_Legal', 'N/A'), normal_style))
            
            # Generar PDF
            doc.build(story)
            
            # Obtener datos del buffer
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            st.error(f"❌ Error al generar PDF: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def is_available(self):
        """Verificar si PDF está disponible"""
        return self.pdf_available
