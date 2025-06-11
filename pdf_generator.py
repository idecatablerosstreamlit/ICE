"""
Generador de PDFs para Hojas Metodológicas del Dashboard ICE
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import io

# Intentar importar ReportLab para PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class PDFGenerator:
    """Clase para generar PDFs de hojas metodológicas"""
    
    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para PDF"""
        # Estilo para título principal
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulos de sección
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
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Estilo para etiquetas
        self.label_style = ParagraphStyle(
            'CustomLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
    
    def generate_metodological_sheet(self, codigo, excel_data):
        """Generar hoja metodológica en PDF o CSV como fallback"""
        
        if not REPORTLAB_AVAILABLE:
            st.warning("ReportLab no está instalado. Generando CSV como alternativa.")
            st.info("Para generar PDFs, instala: pip install reportlab")
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
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Construir contenido
            story = []
            
            # Encabezado principal
            story.append(Paragraph("SISTEMA DE SEGUIMIENTO Y EVALUACION IDECA - ICE", self.title_style))
            story.append(Paragraph("FICHA METODOLÓGICA DEL INDICADOR", self.title_style))
            story.append(Spacer(1, 20))
            
            # Sección I: Descripción del indicador
            story.extend(self._create_section_i(indicator_data))
            story.append(Spacer(1, 20))
            
            # Sección II: Características del indicador
            story.extend(self._create_section_ii(indicator_data))
            story.append(PageBreak())
            
            # Sección III: Datos del responsable
            story.extend(self._create_section_iii(indicator_data))
            story.append(Spacer(1, 20))
            
            # Sección IV: Otras consideraciones
            story.extend(self._create_section_iv())
            
            # Construir PDF
            doc.build(story)
            
            # Obtener bytes del PDF
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            st.success("✅ PDF generado correctamente")
            return pdf_bytes
            
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")
            st.info("Generando CSV como alternativa...")
            return self._generate_csv_alternative(codigo, excel_data)
    
    def _create_section_i(self, data):
        """Crear sección I: Descripción del indicador"""
        story = []
        
        # Título de sección
        story.append(Paragraph("I. DESCRIPCIÓN DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        # Datos de la sección I
        section_data = [
            ['I.1. Código del indicador', self._safe_get(data, 'Codigo', '')],
            ['I.2. Nombre del indicador', self._safe_get(data, 'Nombre_Indicador', '')],
            ['I.3. Definición', self._safe_get(data, 'Definicion', '')],
            ['I.4. Objetivo', self._safe_get(data, 'Objetivo', '')],
            ['I.5. Área temática', self._safe_get(data, 'Area_Tematica', '')],
            ['I.6. Tema', self._safe_get(data, 'Tema', '')],
            ['I.7. Soporte Legal', self._safe_get(data, 'Soporte_Legal', '')]
        ]
        
        # Crear tabla
        table_data = []
        for label, value in section_data:
            table_data.append([
                Paragraph(label, self.label_style),
                Paragraph(self._wrap_text(str(value)), self.normal_style)
            ])
        
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(table)
        return story
    
    def _create_section_ii(self, data):
        """Crear sección II: Características del indicador"""
        story = []
        
        # Título de sección
        story.append(Paragraph("II. CARACTERÍSTICAS DEL INDICADOR", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        # Primera parte de características
        section_data_1 = [
            ['II.1. Fórmula de cálculo', self._safe_get(data, 'Formula_Calculo', '')],
            ['II.2. Variables', self._safe_get(data, 'Variables', '')],
            ['II.3. Unidad de medida', self._safe_get(data, 'Unidad_Medida', '')],
            ['II.4. Metodología de cálculo', self._safe_get(data, 'Metodologia_Calculo', '')],
            ['II.5. Fuente de Información', self._safe_get(data, 'Fuente_Informacion', '')],
            ['II.6. Tipo de indicador', self._safe_get(data, 'Tipo_Indicador', '')],
            ['II.7. Periodicidad', self._safe_get(data, 'Periodicidad', '')]
        ]
        
        table_data_1 = []
        for label, value in section_data_1:
            table_data_1.append([
                Paragraph(label, self.label_style),
                Paragraph(self._wrap_text(str(value)), self.normal_style)
            ])
        
        table1 = Table(table_data_1, colWidths=[2.2*inch, 4*inch])
        table1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(table1)
        story.append(Spacer(1, 15))
        
        # Niveles de desagregación
        story.append(Paragraph("II.8. Niveles de desagregación", self.label_style))
        story.append(Spacer(1, 5))
        
        desag_data = [
            [Paragraph("II.8.a. Geográfica", self.label_style), 
             Paragraph("II.8.b. Poblacional-diferencial", self.label_style)],
            [Paragraph(self._wrap_text(self._safe_get(data, 'Desagregacion_Geografica', '')), self.normal_style),
             Paragraph(self._wrap_text(self._safe_get(data, 'Desagregacion_Poblacional', '')), self.normal_style)]
        ]
        
        desag_table = Table(desag_data, colWidths=[3.1*inch, 3.1*inch])
        desag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(desag_table)
        story.append(Spacer(1, 15))
        
        # Clasificación
        story.append(Paragraph("II.9. Clasificación", self.label_style))
        story.append(Spacer(1, 5))
        
        clas_data = [
            [Paragraph("II.9.a. Según calidad", self.label_style),
             Paragraph("II.9.b. Según nivel de intervención", self.label_style)],
            [Paragraph(self._wrap_text(self._safe_get(data, 'Clasificacion_Calidad', '')), self.normal_style),
             Paragraph(self._wrap_text(self._safe_get(data, 'Clasificacion_Intervencion', '')), self.normal_style)]
        ]
        
        clas_table = Table(clas_data, colWidths=[3.1*inch, 3.1*inch])
        clas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(clas_table)
        story.append(Spacer(1, 15))
        
        # Resto de características
        section_data_2 = [
            ['II.10. Tipo de acumulación', self._safe_get(data, 'Tipo_Acumulacion', '')],
            ['II.11. Enlaces web relacionados', self._safe_get(data, 'Enlaces_Web', '')],
            ['II.12. Interpretación', self._safe_get(data, 'Interpretacion', '')],
            ['II.13. Limitaciones', self._safe_get(data, 'Limitaciones', '')]
        ]
        
        table_data_2 = []
        for label, value in section_data_2:
            table_data_2.append([
                Paragraph(label, self.label_style),
                Paragraph(self._wrap_text(str(value)), self.normal_style)
            ])
        
        table2 = Table(table_data_2, colWidths=[2.2*inch, 4*inch])
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(table2)
        return story
    
    def _create_section_iii(self, data):
        """Crear sección III: Datos del responsable"""
        story = []
        
        # Título de sección
        story.append(Paragraph("III. DATOS DEL RESPONSABLE QUE REPORTA LA INFORMACIÓN", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        section_data = [
            ['III.1. Sector', self._safe_get(data, 'Sector', '')],
            ['III.2. Entidad', self._safe_get(data, 'Entidad', '')],
            ['III.3. Dependencia', self._safe_get(data, 'Dependencia', '')],
            ['III.4. Directivo/a Responsable', self._safe_get(data, 'Directivo_Responsable', '')],
            ['III.5. Correo electrónico del directivo', self._safe_get(data, 'Correo_Directivo', '')],
            ['III.6. Teléfono de contacto', self._safe_get(data, 'Telefono_Contacto', '')]
        ]
        
        table_data = []
        for label, value in section_data:
            table_data.append([
                Paragraph(label, self.label_style),
                Paragraph(self._wrap_text(str(value)), self.normal_style)
            ])
        
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(table)
        return story
    
    def _create_section_iv(self):
        """Crear sección IV: Otras consideraciones"""
        story = []
        
        # Título de sección
        story.append(Paragraph("IV. OTRAS CONSIDERACIONES", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        section_data = [
            ['IV.1. Fecha de elaboración de la ficha', fecha_actual]
        ]
        
        table_data = []
        for label, value in section_data:
            table_data.append([
                Paragraph(label, self.label_style),
                Paragraph(str(value), self.normal_style)
            ])
        
        table = Table(table_data, colWidths=[2.2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472c4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Pie de página
        footer_text = "Este documento ha sido generado automáticamente por el Sistema ICE - IDECA."
        story.append(Paragraph(footer_text, self.normal_style))
        
        return story
    
    def _generate_csv_alternative(self, codigo, excel_data):
        """Generar archivo CSV como alternativa al PDF"""
        try:
            from data_utils import ExcelDataLoader
            excel_loader = ExcelDataLoader()
            indicator_data = excel_loader.get_indicator_data(codigo)
            
            if not indicator_data:
                return None
            
            # Crear DataFrame con los datos estructurados
            data_rows = [
                ['I. DESCRIPCIÓN DEL INDICADOR', ''],
                ['I.1. Código del indicador', self._safe_get(indicator_data, 'Codigo', '')],
                ['I.2. Nombre del indicador', self._safe_get(indicator_data, 'Nombre_Indicador', '')],
                ['I.3. Definición', self._safe_get(indicator_data, 'Definicion', '')],
                ['I.4. Objetivo', self._safe_get(indicator_data, 'Objetivo', '')],
                ['I.5. Área temática', self._safe_get(indicator_data, 'Area_Tematica', '')],
                ['I.6. Tema', self._safe_get(indicator_data, 'Tema', '')],
                ['I.7. Soporte Legal', self._safe_get(indicator_data, 'Soporte_Legal', '')],
                ['', ''],
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
                ['', ''],
                ['III. DATOS DEL RESPONSABLE QUE REPORTA LA INFORMACIÓN', ''],
                ['III.1. Sector', self._safe_get(indicator_data, 'Sector', '')],
                ['III.2. Entidad', self._safe_get(indicator_data, 'Entidad', '')],
                ['III.3. Dependencia', self._safe_get(indicator_data, 'Dependencia', '')],
                ['III.4. Directivo/a Responsable', self._safe_get(indicator_data, 'Directivo_Responsable', '')],
                ['III.5. Correo electrónico del directivo', self._safe_get(indicator_data, 'Correo_Directivo', '')],
                ['III.6. Teléfono de contacto', self._safe_get(indicator_data, 'Telefono_Contacto', '')],
                ['', ''],
                ['IV. OTRAS CONSIDERACIONES', ''],
                ['IV.1. Fecha de elaboración de la ficha', datetime.now().strftime("%d/%m/%Y")]
            ]
            
            # Crear DataFrame y convertir a CSV
            df_export = pd.DataFrame(data_rows, columns=['Campo', 'Valor'])
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            
            return csv_data.encode('utf-8-sig')
            
        except Exception as e:
            st.error(f"Error al generar archivo alternativo: {e}")
            return None
    
    def _safe_get(self, data, key, default=''):
        """Obtener valor de forma segura del diccionario"""
        try:
            value = data.get(key, default)
            if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
                return default
            return str(value)
        except:
            return default
    
    def _wrap_text(self, text):
        """Ajustar texto para que no se desborde en las celdas"""
        if len(str(text)) > 100:
            # Insertar saltos de línea cada 100 caracteres aproximadamente
            words = str(text).split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 100:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return '<br/>'.join(lines)
        return str(text)