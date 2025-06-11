"""
Generador de PDFs para Hojas Metodológicas del Dashboard ICE - SOLO PDF
"""

import streamlit as st
from datetime import datetime
import io

# Importar ReportLab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class PDFGenerator:
    """Clase para generar SOLO PDFs de hojas metodológicas"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado. Ejecuta: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.HexColor('#4472c4'),
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        self.label_style = ParagraphStyle(
            'CustomLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
    
    def generate_metodological_sheet(self, codigo, excel_data):
        """Generar hoja metodológica SOLO en PDF"""
        
        if not REPORTLAB_AVAILABLE:
            st.error("❌ ReportLab no está instalado. No se puede generar PDF.")
            st.info("Instala con: pip install reportlab")
            return None
        
        try:
            # Buscar datos del indicador
            from data_utils import ExcelDataLoader
            excel_loader = ExcelDataLoader()
            indicator_data = excel_loader.get_indicator_data(codigo)
            
            if not indicator_data:
                st.error(f"No se encontraron datos para el indicador {codigo}")
                return None
            
            # Crear PDF en memoria
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.75*inch, leftMargin=0.75*inch, 
                                  topMargin=0.75*inch, bottomMargin=0.75*inch)
            
            story = []
            
            # Título principal
            story.append(Paragraph("SISTEMA DE SEGUIMIENTO Y EVALUACION IDECA - ICE", self.title_style))
            story.append(Paragraph("FICHA METODOLÓGICA DEL INDICADOR", self.title_style))
            story.append(Spacer(1, 20))
            
            # Crear las secciones
            story.extend(self._create_section_i(indicator_data))
            story.append(Spacer(1, 20))
            story.extend(self._create_section_ii(indicator_data))
            story.append(Spacer(1, 20))
            story.extend(self._create_section_iii(indicator_data))
            story.append(Spacer(1, 20))
            story.extend(self._create_section_iv())
            
            # Generar PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            st.success("✅ PDF generado correctamente")
            return pdf_bytes
            
        except Exception as e:
            st.error(f"❌ Error al generar PDF: {e}")
            return None
    
    def _create_section_i(self, data):
        """Sección I: Descripción del indicador"""
        story = []
        story.append(Paragraph("I. DESCRIPCIÓN DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        section_data = [
            ['I.1. Código del indicador', self._safe_get(data, 'Codigo', '')],
            ['I.2. Nombre del indicador', self._safe_get(data, 'Nombre_Indicador', '')],
            ['I.3. Definición', self._safe_get(data, 'Definicion', '')],
            ['I.4. Objetivo', self._safe_get(data, 'Objetivo', '')],
            ['I.5. Área temática', self._safe_get(data, 'Area_Tematica', '')],
            ['I.6. Tema', self._safe_get(data, 'Tema', '')],
            ['I.7. Soporte Legal', self._safe_get(data, 'Soporte_Legal', '')]
        ]
        
        table_data = [[Paragraph(label, self.label_style), Paragraph(str(value), self.normal_style)] for label, value in section_data]
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        return story
    
    def _create_section_ii(self, data):
        """Sección II: Características del indicador"""
        story = []
        story.append(Paragraph("II. CARACTERÍSTICAS DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        section_data = [
            ['II.1. Fórmula de cálculo', self._safe_get(data, 'Formula_Calculo', '')],
            ['II.2. Variables', self._safe_get(data, 'Variables', '')],
            ['II.3. Unidad de medida', self._safe_get(data, 'Unidad_Medida', '')],
            ['II.4. Metodología de cálculo', self._safe_get(data, 'Metodologia_Calculo', '')],
            ['II.5. Fuente de Información', self._safe_get(data, 'Fuente_Informacion', '')],
            ['II.6. Tipo de indicador', self._safe_get(data, 'Tipo_Indicador', '')],
            ['II.7. Periodicidad', self._safe_get(data, 'Periodicidad', '')],
            ['II.8. Interpretación', self._safe_get(data, 'Interpretacion', '')],
            ['II.9. Limitaciones', self._safe_get(data, 'Limitaciones', '')]
        ]
        
        table_data = [[Paragraph(label, self.label_style), Paragraph(str(value), self.normal_style)] for label, value in section_data]
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        return story
    
    def _create_section_iii(self, data):
        """Sección III: Datos del responsable"""
        story = []
        story.append(Paragraph("III. DATOS DEL RESPONSABLE QUE REPORTA LA INFORMACIÓN", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        section_data = [
            ['III.1. Sector', self._safe_get(data, 'Sector', '')],
            ['III.2. Entidad', self._safe_get(data, 'Entidad', '')],
            ['III.3. Dependencia', self._safe_get(data, 'Dependencia', '')],
            ['III.4. Directivo/a Responsable', self._safe_get(data, 'Directivo_Responsable', '')],
            ['III.5. Correo electrónico', self._safe_get(data, 'Correo_Directivo', '')],
            ['III.6. Teléfono de contacto', self._safe_get(data, 'Telefono_Contacto', '')]
        ]
        
        table_data = [[Paragraph(label, self.label_style), Paragraph(str(value), self.normal_style)] for label, value in section_data]
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        return story
    
    def _create_section_iv(self):
        """Sección IV: Otras consideraciones"""
        story = []
        story.append(Paragraph("IV. OTRAS CONSIDERACIONES", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        section_data = [['IV.1. Fecha de elaboración de la ficha', fecha_actual]]
        
        table_data = [[Paragraph(label, self.label_style), Paragraph(str(value), self.normal_style)] for label, value in section_data]
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        return story
    
    def _safe_get(self, data, key, default=''):
        """Obtener valor de forma segura"""
        try:
            value = data.get(key, default)
            if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
                return default
            return str(value)
        except:
            return default
