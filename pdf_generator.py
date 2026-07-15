# Archivo: pdf_generator.py - VERSIÓN ACTUALIZADA PARA FICHAS DESDE GOOGLE SHEETS

"""
Generador de PDFs para fichas metodológicas del Dashboard ICE - ACTUALIZADO PARA GOOGLE SHEETS
ACTUALIZACIÓN: Ya no usa Excel, ahora usa datos de la pestaña "Fichas" de Google Sheets
CORRECCIÓN: Ahora usa la fecha y hora de Colombia correctamente
"""

import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime
import pytz

def get_colombia_time():
    """Obtener fecha y hora actual de Colombia"""
    colombia_tz = pytz.timezone('America/Bogota')
    return datetime.now(colombia_tz)

# Importación condicional de reportlab
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Fuente institucional Nunito Sans (TTF en carpeta fonts/); si falta, se usa Helvetica
PDF_FONT = 'Helvetica'
PDF_FONT_BOLD = 'Helvetica-Bold'
if PDF_AVAILABLE:
    try:
        _FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        pdfmetrics.registerFont(TTFont('NunitoSans', os.path.join(_FONTS_DIR, 'NunitoSans-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('NunitoSans-Bold', os.path.join(_FONTS_DIR, 'NunitoSans-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('NunitoSans-Italic', os.path.join(_FONTS_DIR, 'NunitoSans-Italic.ttf')))
        pdfmetrics.registerFont(TTFont('NunitoSans-BoldItalic', os.path.join(_FONTS_DIR, 'NunitoSans-BoldItalic.ttf')))
        pdfmetrics.registerFontFamily(
            'NunitoSans',
            normal='NunitoSans',
            bold='NunitoSans-Bold',
            italic='NunitoSans-Italic',
            boldItalic='NunitoSans-BoldItalic'
        )
        PDF_FONT = 'NunitoSans'
        PDF_FONT_BOLD = 'NunitoSans-Bold'
    except Exception:
        pass

class PDFGenerator:
    """Generador de fichas metodológicas en PDF - ACTUALIZADO PARA GOOGLE SHEETS"""
    
    def __init__(self):
        self.pdf_available = PDF_AVAILABLE
    
    def generate_metodological_sheet(self, codigo, fichas_data):
        """Generar ficha metodológica en PDF - USANDO DATOS DE GOOGLE SHEETS"""
        try:
            if not self.pdf_available:
                st.error("📦 **Para descargar PDFs instala:** `pip install reportlab`")
                return None
            
            if fichas_data is None or fichas_data.empty:
                st.error("❌ No hay datos metodológicos disponibles. Verifica la pestaña 'Fichas' en Google Sheets.")
                return None
            
            # Buscar datos del indicador en las fichas de Google Sheets
            indicador_data = fichas_data[fichas_data['COD'] == codigo]
            
            if indicador_data.empty:
                st.error(f"❌ No se encontraron datos metodológicos para el código {codigo}")
                
                # Mostrar códigos disponibles
                if 'COD' in fichas_data.columns:
                    codigos_disponibles = fichas_data['COD'].dropna().unique().tolist()
                    if codigos_disponibles:
                        st.info(f"💡 Códigos disponibles en pestaña 'Fichas': {', '.join(map(str, codigos_disponibles[:10]))}")
                        if len(codigos_disponibles) > 10:
                            st.info(f"... y {len(codigos_disponibles) - 10} más")
                else:
                    st.warning("⚠️ La pestaña 'Fichas' no tiene la columna 'COD'")
                
                return None
            
            # Obtener datos del indicador
            datos = indicador_data.iloc[0]
            
            # Crear documento PDF con márgenes ajustados
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=60
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
        """Construir contenido del PDF con mejor manejo de texto largo"""
        # Crear estilos mejorados
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#003A5B'),
            fontName=PDF_FONT_BOLD
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#003A5B'),
            borderWidth=1,
            borderColor=colors.HexColor('#003A5B'),
            borderPadding=8,
            backColor=colors.HexColor('#F8F9FA'),
            fontName=PDF_FONT_BOLD
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=12,
            fontName=PDF_FONT
        )
        
        label_style = ParagraphStyle(
            'CustomLabel',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#444444'),
            fontName=PDF_FONT_BOLD
        )
        
        # Construir contenido del documento
        story = []
        
        # Título principal
        story.append(Paragraph("FICHA METODOLÓGICA DE INDICADOR", title_style))
        story.append(Paragraph("Dashboard ICE - Infraestructura de Conocimiento Espacial", normal_style))
        story.append(Spacer(1, 20))
        
        # ✅ CORRECCIÓN: Usar get_colombia_time() en lugar de datetime.now()
        colombia_time = get_colombia_time()
        fecha_generacion = colombia_time.strftime('%d/%m/%Y %H:%M:%S COT')
        
        # Información institucional
        story.append(Paragraph("INFORMACIÓN DEL DOCUMENTO", subtitle_style))
        
        institucion_data = [
            ['Sistema:', 'Dashboard ICE - Infraestructura de Conocimiento Espacial'],
            ['Fuente de datos:', 'Google Sheets - Pestaña "Fichas"'],
            ['Fecha de generación:', fecha_generacion],  # ✅ CORREGIDO
            ['Código del indicador:', codigo]
        ]
        
        institucion_table = self._create_simple_table(institucion_data)
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
        
        basic_table = self._create_flexible_table(basic_data)
        story.append(basic_table)
        story.append(Spacer(1, 15))
        
        # 2. DEFINICIÓN Y OBJETIVO
        story.append(Paragraph("2. DEFINICIÓN Y OBJETIVO", subtitle_style))
        
        definicion = self._safe_get(datos, 'Definicion', 'No disponible')
        objetivo = self._safe_get(datos, 'Objetivo', 'No disponible')
        
        if definicion != 'No disponible':
            story.append(Paragraph("<b>Definición:</b>", label_style))
            story.append(Paragraph(definicion, normal_style))
            story.append(Spacer(1, 10))
        
        if objetivo != 'No disponible':
            story.append(Paragraph("<b>Objetivo:</b>", label_style))
            story.append(Paragraph(objetivo, normal_style))
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
        
        methodology_table = self._create_flexible_table(methodology_data)
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
        
        technical_table = self._create_flexible_table(technical_data)
        story.append(technical_table)
        story.append(Spacer(1, 15))
        
        # 5. OBSERVACIONES Y LIMITACIONES
        observaciones = self._safe_get(datos, 'Observaciones', '')
        limitaciones = self._safe_get(datos, 'Limitaciones', '')
        interpretacion = self._safe_get(datos, 'Interpretacion', '')
        
        if observaciones != 'N/A' or limitaciones != 'N/A' or interpretacion != 'N/A':
            story.append(Paragraph("5. OBSERVACIONES Y LIMITACIONES", subtitle_style))
            
            if observaciones != 'N/A':
                story.append(Paragraph("<b>Observaciones:</b>", label_style))
                story.append(Paragraph(observaciones, normal_style))
                story.append(Spacer(1, 10))
            
            if limitaciones != 'N/A':
                story.append(Paragraph("<b>Limitaciones:</b>", label_style))
                story.append(Paragraph(limitaciones, normal_style))
                story.append(Spacer(1, 10))
            
            if interpretacion != 'N/A':
                story.append(Paragraph("<b>Interpretación:</b>", label_style))
                story.append(Paragraph(interpretacion, normal_style))
                story.append(Spacer(1, 15))
        
        # 6. INFORMACIÓN DE CONTACTO
        story.append(Paragraph("6. INFORMACIÓN DE CONTACTO", subtitle_style))
        
        contact_data = [
            ['Directivo responsable:', self._safe_get(datos, 'Directivo_Responsable', 'N/A')],
            ['Correo electrónico:', self._safe_get(datos, 'Correo_Directivo', 'N/A')],
            ['Teléfono de contacto:', self._safe_get(datos, 'Telefono_Contacto', 'N/A')]
        ]
        
        contact_table = self._create_flexible_table(contact_data)
        story.append(contact_table)
        
        # 7. ENLACES Y SOPORTE LEGAL
        enlaces = self._safe_get(datos, 'Enlaces_Web', '')
        soporte = self._safe_get(datos, 'Soporte_Legal', '')
        
        if enlaces != 'N/A':
            story.append(Spacer(1, 15))
            story.append(Paragraph("7. ENLACES RELACIONADOS", subtitle_style))
            story.append(Paragraph(enlaces, normal_style))
        
        if soporte != 'N/A':
            story.append(Spacer(1, 15))
            story.append(Paragraph("8. SOPORTE LEGAL", subtitle_style))
            story.append(Paragraph(soporte, normal_style))
        
        # ✅ CORRECCIÓN: Usar get_colombia_time() en el pie de página también
        fecha_pie = colombia_time.strftime('%d/%m/%Y a las %H:%M:%S COT')
        
        # Pie de página con información del sistema
        story.append(Spacer(1, 30))
        story.append(Paragraph("―――――――――――――――――――――――――――――――――――", normal_style))
        story.append(Paragraph("<i>Documento generado automáticamente desde Google Sheets por el Dashboard ICE</i>", normal_style))
        story.append(Paragraph(f"<i>Fecha y hora de generación: {fecha_pie}</i>", normal_style))  # ✅ CORREGIDO
        
        return story
    
    def _safe_get(self, datos, campo, default='N/A'):
        """Obtener valor de forma segura manejando NaN y preservando texto completo"""
        try:
            valor = datos.get(campo, default)
            if pd.isna(valor) or valor == '' or str(valor).strip() == '':
                return default
            
            texto = str(valor).strip()
            
            # Limpiar el texto pero preservarlo completo
            # Reemplazar caracteres problemáticos
            texto = texto.replace('\r\n', '\n').replace('\r', '\n')
            
            # Escapar caracteres especiales de HTML/XML
            texto = texto.replace('&', '&amp;')
            texto = texto.replace('<', '&lt;')
            texto = texto.replace('>', '&gt;')
            
            return texto if texto else default
            
        except Exception as e:
            return default
    
    def _create_simple_table(self, data):
        """Crear tabla simple para información institucional"""
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#003A5B')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), PDF_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        return table
    
    def _create_flexible_table(self, data):
        """Crear tabla flexible que se adapta al contenido largo"""
        # Preparar datos con Paragraphs para texto largo
        processed_data = []
        
        for row in data:
            if len(row) >= 2:
                label = row[0]
                content = row[1]
                
                # Crear paragraph para contenido largo
                if len(str(content)) > 80:
                    # Usar Paragraph para texto largo
                    cell_style = ParagraphStyle('CellNormal', parent=getSampleStyleSheet()['Normal'], fontName=PDF_FONT)
                    content_paragraph = Paragraph(str(content), cell_style)
                    processed_data.append([label, content_paragraph])
                else:
                    processed_data.append([label, str(content)])
            else:
                processed_data.append(row)
        
        # Determinar anchos de columna dinámicamente
        max_content_length = max([len(str(row[1])) for row in data if len(row) >= 2] + [0])
        
        if max_content_length > 200:
            col_widths = [2*inch, 4.5*inch]
        elif max_content_length > 100:
            col_widths = [2.2*inch, 4.3*inch]
        else:
            col_widths = [2.5*inch, 4*inch]
        
        table = Table(processed_data, colWidths=col_widths, repeatRows=0)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E5EBEF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), PDF_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        return table
    
    def is_available(self):
        """Verificar si PDF está disponible"""
        return self.pdf_available

    @staticmethod
    def generate_ficha_pdf(ficha_row):
        """
        Generar PDF de ficha metodológica desde una fila de datos
        Args:
            ficha_row: Serie de pandas con los datos de la ficha
        Returns:
            BytesIO con el contenido del PDF
        """
        if not PDF_AVAILABLE:
            raise ImportError("reportlab no está disponible. Instala con: pip install reportlab")

        # Crear DataFrame temporal con la fila
        import pandas as pd
        fichas_df_temp = pd.DataFrame([ficha_row])

        # Usar el método existente
        generator = PDFGenerator()
        codigo = ficha_row.get('COD', 'UNKNOWN')
        return generator.generate_metodological_sheet(codigo, fichas_df_temp)
