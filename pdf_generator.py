"""
Generador de PDFs para Hojas Metodológicas del Dashboard ICE
"""

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import io
import streamlit as st
from datetime import datetime
import pandas as pd

class PDFGenerator:
    """Clase para generar PDFs de hojas metodológicas"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            st.error("La librería ReportLab no está disponible. Por favor, instala: pip install reportlab")
            return
            
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Estilo para título principal
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79')
        )
        
        # Estilo para subtítulos
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=8,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.HexColor('#4472c4')
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_JUSTIFY
        )
        
        # Estilo para etiquetas
        self.label_style = ParagraphStyle(
            'CustomLabel',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
    
    def generate_metodological_sheet(self, codigo, excel_data):
        """Generar hoja metodológica en PDF"""
        if not REPORTLAB_AVAILABLE:
            # Generar CSV como alternativa
            return self._generate_csv_alternative(codigo, excel_data)
        
        try:
            # Buscar datos del indicador
            from data_utils import ExcelDataLoader
            excel_loader = ExcelDataLoader()
            indicator_data = excel_loader.get_indicator_data(codigo)
            
            if not indicator_data:
                st.error(f"No se encontraron datos para el indicador {codigo}")
                return None
            
            # Crear buffer de memoria para el PDF
            buffer = io.BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Construir contenido
            story = []
            
            # Título principal
            story.append(Paragraph("SISTEMA DE SEGUIMIENTO Y EVALUACION IDECA - ICE", self.title_style))
            story.append(Paragraph("FICHA METODOLÓGICA DEL INDICADOR", self.title_style))
            story.append(Spacer(1, 12))
            
            # Sección I: Descripción del indicador
            story.extend(self._create_section_i(indicator_data))
            story.append(PageBreak())
            
            # Sección II: Características del indicador
            story.extend(self._create_section_ii(indicator_data))
            story.append(PageBreak())
            
            # Sección III: Datos del responsable
            story.extend(self._create_section_iii(indicator_data))
            
            # Sección IV: Otras consideraciones
            story.extend(self._create_section_iv())
            
            # Construir PDF
            doc.build(story)
            
            # Obtener bytes del PDF
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")
            # Intentar generar CSV como alternativa
            return self._generate_csv_alternative(codigo, excel_data)
    
    def _generate_csv_alternative(self, codigo, excel_data):
        """Generar archivo CSV como alternativa al PDF"""
        try:
            from data_utils import ExcelDataLoader
            excel_loader = ExcelDataLoader()
            indicator_data = excel_loader.get_indicator_data(codigo)
            
            if not indicator_data:
                return None
            
            # Crear DataFrame con los datos estructurados
            data_rows = []
            
            # Sección I
            seccion_i = [
                ['I. DESCRIPCIÓN DEL INDICADOR', ''],
                ['I.1. Código del indicador', self._safe_get(indicator_data, 'Codigo', '')],
                ['I.2. Nombre del indicador', self._safe_get(indicator_data, 'Nombre_Indicador', '')],
                ['I.3. Definición', self._safe_get(indicator_data, 'Definicion', '')],
                ['I.4. Objetivo', self._safe_get(indicator_data, 'Objetivo', '')],
                ['I.5. Área temática', self._safe_get(indicator_data, 'Area_Tematica', '')],
                ['I.6. Tema', self._safe_get(indicator_data, 'Tema', '')],
                ['I.7. Soporte Legal', self._safe_get(indicator_data, 'Soporte_Legal', '')],
                ['', '']
            ]
            
            # Sección II
            seccion_ii = [
                ['II. CARACTERÍSTICAS DEL INDICADOR', ''],
                ['II.1. Fórmula de cálculo', self._safe_get(indicator_data, 'Formula_Calculo', '')],
                ['II.2. Variables', self._safe_get(indicator_data, 'Variables', '')],
                ['II.3. Unidad de medida', self._safe_get(indicator_data, 'Unidad_Medida', '')],
                ['II.4. Metodología de cálculo', self._safe_get(indicator_data, 'Metodologia_Calculo', '')],
                ['II.5. Fuente de Información', self._safe_get(indicator_data, 'Fuente_Informacion', '')],
                ['II.6. Tipo de indicador', self._safe_get(indicator_data, 'Tipo_Indicador', '')],
                ['II.7. Periodicidad', self._safe_get(indicator_data, 'Periodicidad', '')],
                ['II.8.a. Geográfica', self._safe_get(indicator_data, 'Desagregacion_Geografica', '')],
                ['II.8.b. Poblacional-diferencial', self._safe_get(indicator_data, 'Desagregacion_Poblacional', '')],
                ['II.9.a. Según calidad', self._safe_get(indicator_data, 'Clasificacion_Calidad', '')],
                ['II.9.b. Según nivel de intervención', self._safe_get(indicator_data, 'Clasificacion_Intervencion', '')],
                ['II.10. Tipo de acumulación', self._safe_get(indicator_data, 'Tipo_Acumulacion', '')],
                ['II.11. Enlaces web relacionados', self._safe_get(indicator_data, 'Enlaces_Web', '')],
                ['II.12. Interpretación', self._safe_get(indicator_data, 'Interpretacion', '')],
                ['II.13. Limitaciones', self._safe_get(indicator_data, 'Limitaciones', '')],
                ['', '']
            ]
            
            # Sección III
            seccion_iii = [
                ['III. DATOS DEL RESPONSABLE QUE REPORTA LA INFORMACIÓN', ''],
                ['III.1. Sector', self._safe_get(indicator_data, 'Sector', '')],
                ['III.2. Entidad', self._safe_get(indicator_data, 'Entidad', '')],
                ['III.3. Dependencia', self._safe_get(indicator_data, 'Dependencia', '')],
                ['III.4. Directivo/a Responsable', self._safe_get(indicator_data, 'Directivo_Responsable', '')],
                ['III.5. Correo electrónico del directivo', self._safe_get(indicator_data, 'Correo_Directivo', '')],
                ['III.6. Teléfono de contacto', self._safe_get(indicator_data, 'Telefono_Contacto', '')],
                ['', '']
            ]
            
            # Sección IV
            seccion_iv = [
                ['IV. OTRAS CONSIDERACIONES', ''],
                ['IV.1. Fecha de elaboración de la ficha', datetime.now().strftime("%d/%m/%Y")]
            ]
            
            # Combinar todas las secciones
            data_rows = seccion_i + seccion_ii + seccion_iii + seccion_iv
            
            # Crear DataFrame
            df_export = pd.DataFrame(data_rows, columns=['Campo', 'Valor'])
            
            # Convertir a CSV
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            
            st.info("PDF no disponible. Se generó archivo CSV con la información metodológica.")
            return csv_data.encode('utf-8-sig')
            
        except Exception as e:
            st.error(f"Error al generar archivo alternativo: {e}")
            return None
    
    def _create_section_i(self, data):
        """Crear sección I: Descripción del indicador"""
        story = []
        
        # Título de sección
        story.append(Paragraph("I. DESCRIPCIÓN DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Crear tabla con los datos
        table_data = [
            ['I.1. Código del indicador', self._safe_get(data, 'Codigo', '')],
            ['I.2. Nombre del indicador', self._safe_get(data, 'Nombre_Indicador', '')],
            ['I.3. Definición', self._safe_get(data, 'Definicion', '')],
            ['I.4. Objetivo', self._safe_get(data, 'Objetivo', '')],
            ['I.5. Área temática', self._safe_get(data, 'Area_Tematica', '')],
            ['I.6. Tema', self._safe_get(data, 'Tema', '')],
            ['I.7. Soporte Legal', self._safe_get(data, 'Soporte_Legal', '')]
        ]
        
        # Convertir datos a párrafos para mejor formato
        formatted_data = []
        for row in table_data:
            formatted_row = [
                Paragraph(row[0], self.label_style),
                Paragraph(str(row[1]), self.normal_style)
            ]
            formatted_data.append(formatted_row)
        
        table = Table(formatted_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
        ]))
        
        story.append(table)
        return story
    
    def _create_section_ii(self, data):
        """Crear sección II: Características del indicador"""
        story = []
        
        # Título de sección
        story.append(Paragraph("II. CARACTERÍSTICAS DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Primera parte de la tabla
        table_data_1 = [
            ['II.1. Fórmula de cálculo', self._safe_get(data, 'Formula_Calculo', '')],
            ['II.2. Variables', self._safe_get(data, 'Variables', '')],
            ['II.3. Unidad de medida', self._safe_get(data, 'Unidad_Medida', '')],
            ['II.4. Metodología de cálculo', self._safe_get(data, 'Metodologia_Calculo', '')],
            ['II.5. Fuente de Información', self._safe_get(data, 'Fuente_Informacion', '')],
            ['II.6. Tipo de indicador', self._safe_get(data, 'Tipo_Indicador', '')],
            ['II.7. Periodicidad', self._safe_get(data, 'Periodicidad', '')]
        ]
        
        formatted_data_1 = []
        for row in table_data_1:
            formatted_row = [
                Paragraph(row[0], self.label_style),
                Paragraph(str(row[1]), self.normal_style)
            ]
            formatted_data_1.append(formatted_row)
        
        table1 = Table(formatted_data_1, colWidths=[2.5*inch, 4*inch])
        table1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
        ]))
        
        story.append(table1)
        story.append(Spacer(1, 12))
        
        # Subtítulo para niveles de desagregación
        story.append(Paragraph("II.8. Niveles de desagregación", self.label_style))
        story.append(Spacer(1, 6))
        
        # Tabla de desagregaciones
        desag_data = [
            ['II.8.a. Geográfica', 'II.8.b. Poblacional-diferencial'],
            [self._safe_get(data, 'Desagregacion_Geografica', ''), 
             self._safe_get(data, 'Desagregacion_Poblacional', '')]
        ]
        
        formatted_desag = []
        for i, row in enumerate(desag_data):
            if i == 0:  # Header row
                formatted_row = [Paragraph(cell, self.label_style) for cell in row]
            else:
                formatted_row = [Paragraph(str(cell), self.normal_style) for cell in row]
            formatted_desag.append(formatted_row)
        
        desag_table = Table(formatted_desag, colWidths=[3.25*inch, 3.25*inch])
        desag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white])
        ]))
        
        story.append(desag_table)
        story.append(Spacer(1, 12))
        
        # Subtítulo para clasificación
        story.append(Paragraph("II.9. Clasificación", self.label_style))
        story.append(Spacer(1, 6))
        
        # Tabla de clasificación
        clas_data = [
            ['II.9.a. Según calidad', 'II.9.b. Según nivel de intervención'],
            [self._safe_get(data, 'Clasificacion_Calidad', ''), 
             self._safe_get(data, 'Clasificacion_Intervencion', '')]
        ]
        
        formatted_clas = []
        for i, row in enumerate(clas_data):
            if i == 0:  # Header row
                formatted_row = [Paragraph(cell, self.label_style) for cell in row]
            else:
                formatted_row = [Paragraph(str(cell), self.normal_style) for cell in row]
            formatted_clas.append(formatted_row)
        
        clas_table = Table(formatted_clas, colWidths=[3.25*inch, 3.25*inch])
        clas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white])
        ]))
        
        story.append(clas_table)
        story.append(Spacer(1, 12))
        
        # Tabla final de características
        table_data_2 = [
            ['II.10. Tipo de acumulación', self._safe_get(data, 'Tipo_Acumulacion', '')],
            ['II.11. Enlaces web relacionados', self._safe_get(data, 'Enlaces_Web', '')],
            ['II.12. Interpretación', self._safe_get(data, 'Interpretacion', '')],
            ['II.13. Limitaciones', self._safe_get(data, 'Limitaciones', '')]
        ]
        
        formatted_data_2 = []
        for row in table_data_2:
            formatted_row = [
                Paragraph(row[0], self.label_style),
                Paragraph(str(row[1]), self.normal_style)
            ]
            formatted_data_2.append(formatted_row)
        
        table2 = Table(formatted_data_2, colWidths=[2.5*inch, 4*inch])
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
        ]))
        
        story.append(table2)
        return story
    
    def _create_section_iii(self, data):
        """Crear sección III: Datos del responsable"""
        story = []
        
        # Título de sección
        story.append(Paragraph("III. DATOS DEL RESPONSABLE QUE REPORTA LA INFORMACIÓN", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Crear tabla con los datos del responsable
        table_data = [
            ['III.1. Sector', self._safe_get(data, 'Sector', '')],
            ['III.2. Entidad', self._safe_get(data, 'Entidad', '')],
            ['III.3. Dependencia', self._safe_get(data, 'Dependencia', '')],
            ['III.4. Directivo/a Responsable', self._safe_get(data, 'Directivo_Responsable', '')],
            ['III.5. Correo electrónico del directivo', self._safe_get(data, 'Correo_Directivo', '')],
            ['III.6. Teléfono de contacto', self._safe_get(data, 'Telefono_Contacto', '')]
        ]
        
        formatted_data = []
        for row in table_data:
            formatted_row = [
                Paragraph(row[0], self.label_style),
                Paragraph(str(row[1]), self.normal_style)
            ]
            formatted_data.append(formatted_row)
        
        table = Table(formatted_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
        ]))
        
        story.append(table)
        return story
    
    def _create_section_iv(self):
        """Crear sección IV: Otras consideraciones"""
        story = []
        
        # Título de sección
        story.append(Paragraph("IV. OTRAS CONSIDERACIONES", self.subtitle_style))
        story.append(Spacer(1, 12))
        
        # Fecha de elaboración
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        table_data = [
            ['IV.1. Fecha de elaboración de la ficha', fecha_actual]
        ]
        
        formatted_data = []
        for row in table_data:
            formatted_row = [
                Paragraph(row[0], self.label_style),
                Paragraph(str(row[1]), self.normal_style)
            ]
            formatted_data.append(formatted_row)
        
        table = Table(formatted_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white])
        ]))
        
        story.append(table)
        
        # Agregar información adicional
        story.append(Spacer(1, 20))
        footer_text = """
        Este documento ha sido generado automáticamente por el Sistema de Seguimiento y Evaluación IDECA - ICE.
        Para más información, contacte con la dependencia responsable del indicador.
        """
        story.append(Paragraph(footer_text, self.normal_style))
        
        return story
    
    def _safe_get(self, data, key, default=''):
        """Obtener valor de forma segura del diccionario"""
        try:
            value = data.get(key, default)
            if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
                return default
            return str(value)
        except:
            return default