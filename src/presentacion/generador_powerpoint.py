"""
Generador de presentaciones PowerPoint
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from typing import Dict

class GeneradorPowerPoint:
    """Genera presentaciones PowerPoint profesionales"""
    
    def __init__(self, datos: Dict, resultados_agentes: Dict):
        self.datos = datos
        self.resultados = resultados_agentes
        self.prs = Presentation()
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)
    
    def crear_presentacion(self, filepath: str) -> None:
        """Crea la presentación completa"""
        self._agregar_portada()
        self._agregar_tabla_contenidos()
        self._agregar_seccion_datos()
        self._agregar_seccion_agentes()
        self._agregar_conclusiones()
        
        self.prs.save(filepath)
        print(f"Presentación guardada en: {filepath}")
    
    def _agregar_portada(self) -> None:
        """Agrega diapositiva de portada"""
        slide_layout = self.prs.slide_layouts[6]  # Blank layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Agregar fondo
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = (31, 78, 121)  # Azul profesional
        
        # Título
        title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = "Análisis de Oportunidad"
        title_frame.paragraphs[0].font.size = Pt(54)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = (255, 255, 255)
        
        # Subtítulo
        subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(8), Inches(1))
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = "Programas Académicos SNIES"
        subtitle_frame.paragraphs[0].font.size = Pt(28)
        subtitle_frame.paragraphs[0].font.color.rgb = (200, 200, 200)
    
    def _agregar_tabla_contenidos(self) -> None:
        """Agrega tabla de contenidos"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Contenido"
        
        content = slide.placeholders[1]
        tf = content.text_frame
        tf.text = "1. Datos SNIES"
        tf.add_paragraph().text = "2. Análisis de Denominación"
        tf.add_paragraph().text = "3. Tendencias de Palabras Clave"
        tf.add_paragraph().text = "4. Análisis Comparativo"
        tf.add_paragraph().text = "5. Conclusiones y Recomendaciones"
    
    def _agregar_seccion_datos(self) -> None:
        """Agrega sección de datos"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Datos SNIES"
        
        content = slide.placeholders[1]
        tf = content.text_frame
        tf.text = f"Total de programas equivalentes: {len(self.datos.get('equivalentes', []))}"
    
    def _agregar_seccion_agentes(self) -> None:
        """Agrega sección de análisis de agentes"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Análisis de Agentes"
        
        content = slide.placeholders[1]
        tf = content.text_frame
        tf.text = "Resultados del análisis multi-agente"
    
    def _agregar_conclusiones(self) -> None:
        """Agrega diapositiva de conclusiones"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Conclusiones"
        
        content = slide.placeholders[1]
        tf = content.text_frame
        tf.text = "Hallazgos principales del análisis"

