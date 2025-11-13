"""
Generador de presentaciones PowerPoint profesionales
Ubicación: src/presentacion/generador_powerpoint.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from typing import Dict, List
import pandas as pd
import os
from pathlib import Path
import pandas as pd

class GeneradorPowerPoint:
    """Genera presentaciones PowerPoint profesionales"""
    
    def __init__(self, datos: Dict, resultados_agentes: Dict, graficas_dir: str = 'output'):
        """
        Inicializa el generador
        
        Args:
            datos: Datos SNIES procesados
            resultados_agentes: Resultados del análisis multi-agente
            graficas_dir: Directorio con las gráficas generadas
        """
        self.datos = datos
        self.resultados = resultados_agentes
        self.graficas_dir = graficas_dir
        
        self.prs = Presentation()
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)
        
        # Colores corporativos
        self.color_primario = RGBColor(31, 78, 121)      # Azul oscuro
        self.color_secundario = RGBColor(79, 129, 189)   # Azul claro
        self.color_acento = RGBColor(192, 0, 0)          # Rojo
        self.color_texto = RGBColor(0, 0, 0)
        self.color_blanco = RGBColor(255, 255, 255)
    
    def crear_presentacion(self, filepath: str) -> None:
        """Crea la presentación completa"""
        print("📊 Generando presentación PowerPoint...")
        
        self._agregar_portada()
        self._agregar_tabla_contenidos()
        self._agregar_resumen_ejecutivo()
        self._agregar_datos_snies_enriquecidos()
        self._agregar_variantes_programa()
        self._agregar_comparacion_variantes()
        self._agregar_universidades_oferta()
        self._agregar_detalle_instituciones()
        self._agregar_informacion_detallada()
        self._agregar_duracion_programas()
        self._agregar_modalidades()
        self._agregar_acreditacion()
        self._agregar_contexto_snies()
        self._agregar_analisis_denominacion()
        self._agregar_analisis_tendencias()
        self._agregar_graficas()
        self._agregar_conclusiones()
        self._agregar_recomendaciones()
        
        # Crear carpeta si no existe
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        self.prs.save(filepath)
        print(f"✅ Presentación guardada en: {filepath}")
    
    def _agregar_portada(self) -> None:
        """Agrega diapositiva de portada"""
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Fondo
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.color_primario
        
        # Título principal
        titulo_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1.5))
        titulo_frame = titulo_box.text_frame
        titulo_frame.word_wrap = True
        p = titulo_frame.paragraphs[0]
        p.text = "Análisis de Oportunidad"
        p.font.size = Pt(54)
        p.font.bold = True
        p.font.color.rgb = self.color_blanco
        p.alignment = PP_ALIGN.CENTER
        
        # Subtítulo
        subtit_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.8), Inches(9), Inches(1))
        subtit_frame = subtit_box.text_frame
        p = subtit_frame.paragraphs[0]
        p.text = "Programas Académicos SNIES"
        p.font.size = Pt(32)
        p.font.color.rgb = self.color_blanco
        p.alignment = PP_ALIGN.CENTER
        
        # Programa
        prog_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(9), Inches(1))
        prog_frame = prog_box.text_frame
        p = prog_frame.paragraphs[0]
        programa = self.resultados.get('programa', 'Programa Académico')
        p.text = f"Programa: {programa}"
        p.font.size = Pt(18)
        p.font.color.rgb = self.color_blanco
        p.alignment = PP_ALIGN.CENTER
        
        # Fecha
        fecha_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.8), Inches(9), Inches(0.5))
        fecha_frame = fecha_box.text_frame
        p = fecha_frame.paragraphs[0]
        timestamp = self.resultados.get('timestamp', 'Noviembre 2025')
        p.text = timestamp
        p.font.size = Pt(14)
        p.font.color.rgb = self.color_blanco
        p.alignment = PP_ALIGN.CENTER
    
    def _agregar_tabla_contenidos(self) -> None:
        """Agrega tabla de contenidos"""
        slide = self._crear_slide_titulo("Contenido")
        
        contenidos = [
            "1. Resumen Ejecutivo",
            "2. Contexto SNIES",
            "3. Análisis de Denominación",
            "4. Análisis de Tendencias",
            "5. Gráficas y Visualizaciones",
            "6. Conclusiones",
            "7. Recomendaciones"
        ]
        
        left = Inches(1.5)
        top = Inches(2)
        
        for i, contenido in enumerate(contenidos):
            text_box = slide.shapes.add_textbox(left, top + Inches(i * 0.7), Inches(7), Inches(0.6))
            text_frame = text_box.text_frame
            p = text_frame.paragraphs[0]
            p.text = contenido
            p.font.size = Pt(18)
            p.font.color.rgb = self.color_texto
            p.level = 0
    
    def _agregar_resumen_ejecutivo(self) -> None:
        """Agrega resumen ejecutivo"""
        slide = self._crear_slide_titulo("Resumen Ejecutivo")
        
        sintesis = self.resultados.get('sintesis', {})
        resumen = sintesis.get('resumen_ejecutivo', 'No disponible')
        
        # Limitar a primeras líneas
        lineas = resumen.split('\n')[:8]
        
        text_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        for i, linea in enumerate(lineas):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            p.text = linea.strip()
            p.font.size = Pt(12)
            p.font.color.rgb = self.color_texto
            p.space_after = Pt(6)
    
    def _agregar_datos_snies_enriquecidos(self) -> None:
        """Agrega diapositiva con datos enriquecidos del SNIES"""
        import pandas as pd
        slide = self._crear_slide_titulo("Datos del SNIES Enriquecidos")
        
        maestro_enriquecido = self.datos.get('maestro_enriquecido', pd.DataFrame())
        estadisticas = self.datos.get('estadisticas', {})
        
        if maestro_enriquecido.empty:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Datos enriquecidos no disponibles"
            p.font.size = Pt(14)
            return
        
        # Crear tabla con información general
        rows = 6
        cols = 2
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(8)
        height = Inches(3)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        # Encabezados
        for col_idx, titulo in enumerate(['Métrica', 'Valor']):
            celda = table_shape.cell(0, col_idx)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_primario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(11)
        
        # Datos
        datos_table = [
            ('Programas Equivalentes', str(estadisticas.get('total_programas_equivalentes', 0))),
            ('Registros SNIES Totales', str(estadisticas.get('total_registros_snies', 0))),
            ('Instituciones Únicas', str(estadisticas.get('instituciones_unicas', 0))),
            ('Departamentos Cubiertos', str(estadisticas.get('departamentos_unicos', 0))),
            ('Períodos Analizados', str(maestro_enriquecido['PERIODO'].nunique()) if 'PERIODO' in maestro_enriquecido.columns else '0'),
        ]
        
        for row_idx, (metrica, valor) in enumerate(datos_table, 1):
            # Métrica
            celda = table_shape.cell(row_idx, 0)
            celda.text = metrica
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            celda.text_frame.paragraphs[0].font.bold = True
            
            # Valor
            celda = table_shape.cell(row_idx, 1)
            celda.text = valor
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            celda.fill.solid()
            celda.fill.fore_color.rgb = RGBColor(230, 240, 250)
    
    def _agregar_variantes_programa(self) -> None:
        """Agrega diapositiva con variantes del programa"""
        import pandas as pd
        slide = self._crear_slide_titulo("Variantes del Programa")
        
        denominaciones = self.resultados.get('denominacion', {}).get('denominaciones_totales', [])
        
        if not denominaciones:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay variantes disponibles"
            p.font.size = Pt(14)
            return
        
        rows = len(denominaciones) + 1
        cols = 3
        left = Inches(0.8)
        top = Inches(1.8)
        width = Inches(8.4)
        height = Inches(0.5 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['No.', 'Variante del Programa', 'Frecuencia']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_primario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(11)
        
        for idx, denominacion in enumerate(denominaciones, 1):
            celda = table_shape.cell(idx, 0)
            celda.text = str(idx)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            
            celda = table_shape.cell(idx, 1)
            celda.text = str(denominacion)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            celda.text_frame.word_wrap = True
            
            celda = table_shape.cell(idx, 2)
            celda.text = "1"
            celda.text_frame.paragraphs[0].font.size = Pt(10)
        
        info_box = slide.shapes.add_textbox(Inches(0.8), Inches(top + height + Inches(0.5)), Inches(8.4), Inches(2))
        info_frame = info_box.text_frame
        info_frame.word_wrap = True
        
        p = info_frame.paragraphs[0]
        p.text = f"Total de variantes identificadas: {len(denominaciones)}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.color_primario
    
    def _agregar_universidades_oferta(self) -> None:
        """Agrega diapositiva con universidades que ofrecen el programa"""
        import pandas as pd
        slide = self._crear_slide_titulo("Universidades que Ofrecen el Programa")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Información de universidades no disponible"
            p.font.size = Pt(14)
            return
        
        if 'CODIGO_INSTITUCION_x' not in maestro_df.columns:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay datos de instituciones disponibles"
            p.font.size = Pt(14)
            return
        
        universidades = maestro_df.drop_duplicates(subset=['CODIGO_INSTITUCION_x']).head(8)
        
        if len(universidades) == 0:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay universidades registradas"
            p.font.size = Pt(14)
            return
        
        rows = len(universidades) + 1
        cols = 2
        left = Inches(0.8)
        top = Inches(1.8)
        width = Inches(8.4)
        height = Inches(0.5 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['No.', 'Universidad']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_primario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(10)
        
        for idx, (_, row) in enumerate(universidades.iterrows(), 1):
            celda = table_shape.cell(idx, 0)
            celda.text = str(idx)
            celda.text_frame.paragraphs[0].font.size = Pt(9)
            
            celda = table_shape.cell(idx, 1)
            nombre = row.get('NOMBRE_INSTITUCION', 'N/A')
            celda.text = str(nombre)[:50]
            celda.text_frame.paragraphs[0].font.size = Pt(9)
            celda.text_frame.word_wrap = True
        
        resumen_box = slide.shapes.add_textbox(Inches(0.8), Inches(top + height + Inches(0.3)), Inches(8.4), Inches(1))
        resumen_frame = resumen_box.text_frame
        resumen_frame.word_wrap = True
        
        p = resumen_frame.paragraphs[0]
        total_inst = maestro_df['CODIGO_INSTITUCION_x'].nunique()
        p.text = f"✓ Total de instituciones: {total_inst}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.color_primario
    
    def _agregar_comparacion_variantes(self) -> None:
        """Compara las variantes del programa encontradas"""
        import pandas as pd
        slide = self._crear_slide_titulo("Análisis Comparativo de Variantes")
        
        denominaciones = self.resultados.get('denominacion', {}).get('denominaciones_totales', [])
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty or not denominaciones:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Datos insuficientes para análisis comparativo"
            p.font.size = Pt(14)
            return
        
        # Crear tabla con comparación
        rows = min(len(denominaciones) + 1, 6)  # Máximo 5 filas
        cols = 4
        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(0.5 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['Variante', 'Oferentes', 'Dtos', 'Estado']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_secundario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(9)
        
        for idx, denom in enumerate(denominaciones[:rows-1], 1):
            # Variante
            celda = table_shape.cell(idx, 0)
            celda.text = str(denom)[:30]
            celda.text_frame.paragraphs[0].font.size = Pt(8)
            
            # Oferentes
            oferentes = 1 if idx <= len(denominaciones) else 0
            celda = table_shape.cell(idx, 1)
            celda.text = str(oferentes)
            celda.text_frame.paragraphs[0].font.size = Pt(8)
            
            # Departamentos
            depts = maestro_df['DEPARTAMENTO_PROGRAMA'].nunique() if not maestro_df.empty else 0
            celda = table_shape.cell(idx, 2)
            celda.text = str(depts)
            celda.text_frame.paragraphs[0].font.size = Pt(8)
            
            # Estado
            celda = table_shape.cell(idx, 3)
            celda.text = "Activo"
            celda.text_frame.paragraphs[0].font.size = Pt(8)
    
    def _agregar_detalle_instituciones(self) -> None:
        """Detalle ampliado de instituciones que ofrecen el programa"""
        import pandas as pd
        slide = self._crear_slide_titulo("Detalle de Instituciones Oferentes")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay datos de instituciones"
            p.font.size = Pt(14)
            return
        
        # Filtrar universidades únicas
        universidades = maestro_df.drop_duplicates(subset=['CODIGO_INSTITUCION_x']).head(10)
        
        if len(universidades) == 0:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay universidades registradas"
            p.font.size = Pt(14)
            return
        
        rows = min(len(universidades) + 1, 11)
        cols = 3
        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(0.4 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['Institución', 'Ciudad', 'Programas']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_primario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(9)
        
        for idx, (_, row) in enumerate(universidades.iterrows(), 1):
            if idx >= rows:
                break
            
            # Institución
            celda = table_shape.cell(idx, 0)
            nombre = row.get('NOMBRE_INSTITUCION', 'N/A')
            celda.text = str(nombre)[:35]
            celda.text_frame.paragraphs[0].font.size = Pt(8)
            celda.text_frame.word_wrap = True
            
            # Ciudad
            celda = table_shape.cell(idx, 1)
            ciudad = row.get('CIUDAD', 'N/A')
            celda.text = str(ciudad)[:15]
            celda.text_frame.paragraphs[0].font.size = Pt(8)
            
            # Programas
            celda = table_shape.cell(idx, 2)
            celda.text = "1"
            celda.text_frame.paragraphs[0].font.size = Pt(8)
    
    def _agregar_duracion_programas(self) -> None:
        """Agrega información sobre duraciones de los programas"""
        import pandas as pd
        slide = self._crear_slide_titulo("Duración de Programas")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty or 'NUMERO_SEMESTRES' not in maestro_df.columns:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Información de duraciones no disponible"
            p.font.size = Pt(14)
            return
        
        # Obtener semestres únicos
        semestres_data = maestro_df['NUMERO_SEMESTRES'].dropna()
        if len(semestres_data) == 0:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay información de duraciones"
            p.font.size = Pt(14)
            return
        
        # Crear tabla de duraciones
        from collections import Counter
        duraciones = Counter(int(float(str(s).split('.')[0])) for s in semestres_data if str(s) != 'nan')
        
        rows = min(len(duraciones) + 1, 8)
        cols = 3
        left = Inches(2)
        top = Inches(1.8)
        width = Inches(6)
        height = Inches(0.5 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['Semestres', 'Programas', 'Porcentaje']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_secundario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(10)
        
        total = sum(duraciones.values())
        for idx, (semestres, cantidad) in enumerate(sorted(duraciones.items())[:rows-1], 1):
            # Semestres
            celda = table_shape.cell(idx, 0)
            celda.text = str(semestres)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            
            # Cantidad
            celda = table_shape.cell(idx, 1)
            celda.text = str(cantidad)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            
            # Porcentaje
            celda = table_shape.cell(idx, 2)
            porcentaje = (cantidad / total * 100) if total > 0 else 0
            celda.text = f"{porcentaje:.1f}%"
            celda.text_frame.paragraphs[0].font.size = Pt(10)
    
    def _agregar_modalidades(self) -> None:
        """Agrega información sobre modalidades de estudio"""
        import pandas as pd
        slide = self._crear_slide_titulo("Modalidades de Estudio")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty or 'MODALIDAD' not in maestro_df.columns:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Información de modalidades no disponible"
            p.font.size = Pt(14)
            return
        
        from collections import Counter
        modalidades = maestro_df['MODALIDAD'].value_counts()
        
        if len(modalidades) == 0:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "No hay información de modalidades"
            p.font.size = Pt(14)
            return
        
        rows = min(len(modalidades) + 1, 7)
        cols = 3
        left = Inches(1.5)
        top = Inches(1.8)
        width = Inches(7)
        height = Inches(0.5 * rows)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['Modalidad', 'Cantidad', 'Porcentaje']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_acento
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(10)
        
        total = modalidades.sum()
        for idx, (modalidad, cantidad) in enumerate(modalidades.head(rows-1).items(), 1):
            # Modalidad
            celda = table_shape.cell(idx, 0)
            celda.text = str(modalidad)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            
            # Cantidad
            celda = table_shape.cell(idx, 1)
            celda.text = str(cantidad)
            celda.text_frame.paragraphs[0].font.size = Pt(10)
            
            # Porcentaje
            celda = table_shape.cell(idx, 2)
            porcentaje = (cantidad / total * 100) if total > 0 else 0
            celda.text = f"{porcentaje:.1f}%"
            celda.text_frame.paragraphs[0].font.size = Pt(10)
    
    def _agregar_acreditacion(self) -> None:
        """Agrega información sobre acreditación de programas"""
        import pandas as pd
        slide = self._crear_slide_titulo("Estado de Acreditación")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Información de acreditación no disponible"
            p.font.size = Pt(14)
            return
        
        # Analizar acreditación
        if 'ACREDITACION' in maestro_df.columns:
            acreditados = len(maestro_df[maestro_df['ACREDITACION'].astype(str).str.contains('Si', case=False, na=False)])
            no_acreditados = len(maestro_df) - acreditados
        else:
            acreditados = 0
            no_acreditados = len(maestro_df)
        
        total = len(maestro_df)
        
        # Crear tabla
        rows = 3
        cols = 2
        left = Inches(2.5)
        top = Inches(2)
        width = Inches(5)
        height = Inches(1.2)
        
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        encabezados = ['Estado', 'Programas']
        for col, titulo in enumerate(encabezados):
            celda = table_shape.cell(0, col)
            celda.text = titulo
            celda.fill.solid()
            celda.fill.fore_color.rgb = self.color_primario
            para = celda.text_frame.paragraphs[0]
            para.font.bold = True
            para.font.color.rgb = self.color_blanco
            para.font.size = Pt(11)
        
        # Fila acreditados
        celda = table_shape.cell(1, 0)
        celda.text = "Acreditados"
        celda.text_frame.paragraphs[0].font.size = Pt(11)
        celda.text_frame.paragraphs[0].font.bold = True
        
        celda = table_shape.cell(1, 1)
        celda.text = f"{acreditados} ({acreditados/total*100:.1f}%)" if total > 0 else "0"
        celda.text_frame.paragraphs[0].font.size = Pt(11)
        celda.fill.solid()
        celda.fill.fore_color.rgb = RGBColor(200, 240, 200)
        
        # Fila no acreditados
        celda = table_shape.cell(2, 0)
        celda.text = "No Acreditados"
        celda.text_frame.paragraphs[0].font.size = Pt(11)
        
        celda = table_shape.cell(2, 1)
        celda.text = f"{no_acreditados} ({no_acreditados/total*100:.1f}%)" if total > 0 else "0"
        celda.text_frame.paragraphs[0].font.size = Pt(11)
        celda.fill.solid()
        celda.fill.fore_color.rgb = RGBColor(255, 200, 200)
    
    def _agregar_informacion_detallada(self) -> None:
        """Agrega diapositiva con información detallada del programa"""
        import pandas as pd
        slide = self._crear_slide_titulo("Información Detallada del Programa")
        
        maestro_df = self.datos.get('maestro', pd.DataFrame())
        
        if maestro_df.empty:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(3))
            frame = box.text_frame
            p = frame.paragraphs[0]
            p.text = "Información detallada no disponible"
            p.font.size = Pt(14)
            return
        
        info_items = []
        
        if 'NIVEL_ESTUDIO' in maestro_df.columns:
            niveles = maestro_df['NIVEL_ESTUDIO'].unique()
            info_items.append(('Niveles de Estudio', ', '.join(str(n) for n in niveles[:5])))
        
        if 'NUMERO_SEMESTRES' in maestro_df.columns:
            semestres_str = maestro_df['NUMERO_SEMESTRES'].dropna().unique()
            semestres_unicos = sorted(set(str(s).split('.')[0] for s in semestres_str))[:5]
            info_items.append(('Duraciones (Semestres)', ', '.join(semestres_unicos)))
        
        if 'MODALIDAD' in maestro_df.columns:
            modalidades = maestro_df['MODALIDAD'].unique()
            info_items.append(('Modalidades', ', '.join(str(m) for m in modalidades[:5])))
        
        if 'ACREDITACION' in maestro_df.columns:
            acreditados = len(maestro_df[maestro_df['ACREDITACION'].astype(str).str.contains('Si', case=False, na=False)])
            total = len(maestro_df)
            info_items.append(('Programas Acreditados', f'{acreditados} de {total}'))
        
        info_items.append(('Total de Registros', str(len(maestro_df))))
        
        if 'DEPARTAMENTO_PROGRAMA' in maestro_df.columns:
            depts = maestro_df['DEPARTAMENTO_PROGRAMA'].unique()
            info_items.append(('Departamentos Cubiertos', f'{len(depts)} departamentos'))
        
        y_pos = 1.8
        for label, valor in info_items:
            label_box = slide.shapes.add_textbox(Inches(0.8), Inches(y_pos), Inches(3), Inches(0.4))
            label_frame = label_box.text_frame
            p = label_frame.paragraphs[0]
            p.text = label
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = self.color_primario
            
            valor_box = slide.shapes.add_textbox(Inches(4), Inches(y_pos), Inches(5.2), Inches(0.4))
            valor_frame = valor_box.text_frame
            valor_frame.word_wrap = True
            p = valor_frame.paragraphs[0]
            p.text = str(valor)
            p.font.size = Pt(11)
            p.font.color.rgb = self.color_texto
            
            y_pos += 0.6
    
    def _agregar_contexto_snies(self) -> None:
        """Agrega contexto de datos SNIES"""
        slide = self._crear_slide_titulo("Contexto SNIES")
        
        stats = {
            'Total de Programas Equivalentes': self.datos.get('programas', pd.DataFrame()).shape[0] if hasattr(self.datos.get('programas'), 'shape') else len(self.datos.get('equivalentes', [])),
            'Instituciones': self.datos.get('maestro', pd.DataFrame())['CODIGO_INSTITUCION_x'].nunique() if not self.datos.get('maestro', pd.DataFrame()).empty else 0,
            'Departamentos': self.datos.get('maestro', pd.DataFrame())['DEPARTAMENTO_PROGRAMA'].nunique() if not self.datos.get('maestro', pd.DataFrame()).empty else 0,
            'Códigos SNIES': len(self.datos.get('snies_codes', []))
        }
        
        top = Inches(2)
        for i, (clave, valor) in enumerate(stats.items()):
            # Clave
            key_box = slide.shapes.add_textbox(Inches(1.5), top + Inches(i * 0.9), Inches(4), Inches(0.5))
            key_frame = key_box.text_frame
            p = key_frame.paragraphs[0]
            p.text = clave + ":"
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = self.color_secundario
            
            # Valor
            val_box = slide.shapes.add_textbox(Inches(5.5), top + Inches(i * 0.9), Inches(3), Inches(0.5))
            val_frame = val_box.text_frame
            p = val_frame.paragraphs[0]
            p.text = str(valor)
            p.font.size = Pt(14)
            p.font.color.rgb = self.color_texto
    
    def _agregar_analisis_denominacion(self) -> None:
        """Agrega análisis de denominación"""
        slide = self._crear_slide_titulo("Análisis de Denominación")
        
        denom = self.resultados.get('denominacion', {})
        analisis_ia = denom.get('analisis_ia', {})
        
        # Denominación oficial
        prog_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(0.6))
        prog_frame = prog_box.text_frame
        p = prog_frame.paragraphs[0]
        denominacion = analisis_ia.get('denominacion_oficial', 'No disponible')
        p.text = f"Denominación oficial: {denominacion}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = self.color_primario
        
        # Palabras clave
        palabras = analisis_ia.get('palabras_clave', [])
        palabras_text = ", ".join(palabras) if palabras else "No disponible"
        
        pal_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(8.4), Inches(1))
        pal_frame = pal_box.text_frame
        pal_frame.word_wrap = True
        p = pal_frame.paragraphs[0]
        p.text = f"Palabras clave: {palabras_text}"
        p.font.size = Pt(12)
        p.font.color.rgb = self.color_texto
        
        # Clasificación
        clasificacion = analisis_ia.get('clasificacion', 'No disponible')
        clase_box = slide.shapes.add_textbox(Inches(0.8), Inches(4), Inches(8.4), Inches(0.6))
        clase_frame = clase_box.text_frame
        p = clase_frame.paragraphs[0]
        p.text = f"Clasificación: {clasificacion}"
        p.font.size = Pt(12)
        p.font.color.rgb = self.color_texto
        
        # Hallazgos
        hallazgos = denom.get('estadisticas', {}).get('total_variaciones', 0)
        hall_box = slide.shapes.add_textbox(Inches(0.8), Inches(5), Inches(8.4), Inches(1.5))
        hall_frame = hall_box.text_frame
        hall_frame.word_wrap = True
        p = hall_frame.paragraphs[0]
        p.text = f"Se encontraron {hallazgos} variaciones diferentes de la denominación en el sistema SNIES."
        p.font.size = Pt(12)
        p.font.color.rgb = self.color_texto
    
    def _agregar_analisis_tendencias(self) -> None:
        """Agrega análisis de tendencias"""
        slide = self._crear_slide_titulo("Análisis de Tendencias")
        
        tend = self.resultados.get('tendencias', {})
        emergentes = tend.get('palabras_emergentes', [])
        
        # Palabras emergentes
        emerg_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(0.6))
        emerg_frame = emerg_box.text_frame
        p = emerg_frame.paragraphs[0]
        p.text = "Palabras Emergentes:"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = self.color_primario
        
        # Lista de emergentes
        emerg_list = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(7.7), Inches(2))
        emerg_frame = emerg_list.text_frame
        emerg_frame.word_wrap = True
        
        for i, palabra in enumerate(emergentes[:5]):
            if i == 0:
                p = emerg_frame.paragraphs[0]
            else:
                p = emerg_frame.add_paragraph()
            p.text = f"• {palabra}"
            p.font.size = Pt(12)
            p.font.color.rgb = self.color_texto
            p.level = 0
        
        # Tendencias nacionales
        tend_box = slide.shapes.add_textbox(Inches(0.8), Inches(5), Inches(8.4), Inches(1.5))
        tend_frame = tend_box.text_frame
        tend_frame.word_wrap = True
        p = tend_frame.paragraphs[0]
        p.text = "Tendencias a nivel nacional: Crecimiento sostenido en programas con denominación moderna y orientada a transformación digital."
        p.font.size = Pt(12)
        p.font.color.rgb = self.color_texto
    
    def _agregar_graficas(self) -> None:
        """Agrega diapositivas con gráficas generadas dinámicamente"""
        print("  Generando gráficas dinámicamente...")
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Backend sin GUI
            
            # Crear gráficas si no existen PNG
            graficas_generadas = self._generar_graficas_dinamicas()
            
            if not graficas_generadas:
                print("  ⚠️  No se pudieron generar gráficas")
                return
            
            print(f"  ✅ Generadas {len(graficas_generadas)} gráficas dinámicamente")
            
            # Agregar máximo 4 gráficas por presentación (2 por slide)
            for i in range(0, len(graficas_generadas[:4]), 2):
                slide = self._crear_slide_vacio()
                
                # Primera gráfica
                if i < len(graficas_generadas):
                    img_path = graficas_generadas[i]
                    try:
                        slide.shapes.add_picture(img_path, Inches(0.5), Inches(1), width=Inches(4.5))
                    except Exception as e:
                        print(f"  ⚠️  Error agregando gráfica {i}: {e}")
                
                # Segunda gráfica
                if i + 1 < len(graficas_generadas):
                    img_path = graficas_generadas[i + 1]
                    try:
                        slide.shapes.add_picture(img_path, Inches(5), Inches(1), width=Inches(4.5))
                    except Exception as e:
                        print(f"  ⚠️  Error agregando gráfica {i+1}: {e}")
        
        except ImportError:
            print("  ⚠️  matplotlib no disponible, saltando gráficas")
    
    def _generar_graficas_dinamicas(self) -> List[str]:
        """Genera gráficas de forma dinámica usando matplotlib"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            graficas_paths = []
            
            # Gráfica 1: Distribución de programas equivalentes
            fig, ax = plt.subplots(figsize=(6, 4))
            programas = self.datos.get('equivalentes', [])
            if programas:
                from collections import Counter
                conteos = Counter(programas)
                nombres = list(conteos.keys())
                valores = list(conteos.values())
                
                ax.barh(nombres, valores, color='#1F4E79')
                ax.set_xlabel('Cantidad', fontsize=10, fontweight='bold')
                ax.set_title('Programas Equivalentes Encontrados', fontsize=12, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)
                
                path = os.path.join(self.graficas_dir, 'grafica_1_programas.png')
                os.makedirs(self.graficas_dir, exist_ok=True)
                plt.tight_layout()
                plt.savefig(path, dpi=150, bbox_inches='tight')
                plt.close()
                graficas_paths.append(path)
            
            # Gráfica 2: Palabras clave frecuentes
            palabras_clave = self.resultados.get('denominacion', {}).get('estadisticas', {}).get('palabras_mas_frecuentes', {})
            if palabras_clave:
                fig, ax = plt.subplots(figsize=(6, 4))
                palabras = list(palabras_clave.keys())[:6]
                frecuencias = [int(palabras_clave[p]) for p in palabras]
                
                colores = ['#1F4E79', '#4F81BD', '#FF6B6B', '#FFB6C1', '#87CEEB', '#90EE90']
                ax.bar(palabras, frecuencias, color=colores[:len(palabras)])
                ax.set_ylabel('Frecuencia', fontsize=10, fontweight='bold')
                ax.set_title('Palabras Clave Más Frecuentes', fontsize=12, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45, ha='right')
                
                path = os.path.join(self.graficas_dir, 'grafica_2_palabras_clave.png')
                plt.tight_layout()
                plt.savefig(path, dpi=150, bbox_inches='tight')
                plt.close()
                graficas_paths.append(path)
            
            # Gráfica 3: Tendencias emergentes vs decadentes
            tendencias = self.resultados.get('tendencias', {})
            emergentes = tendencias.get('palabras_emergentes', [])
            decadentes = tendencias.get('palabras_decadentes', [])
            
            if emergentes or decadentes:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
                
                if emergentes:
                    ax1.barh(range(len(emergentes)), [1]*len(emergentes), color='#2ECC71')
                    ax1.set_yticks(range(len(emergentes)))
                    ax1.set_yticklabels(emergentes, fontsize=9)
                    ax1.set_xlim(0, 1.5)
                    ax1.set_xticks([])
                    ax1.set_title('Palabras Emergentes', fontsize=12, fontweight='bold', color='#27AE60')
                
                if decadentes:
                    ax2.barh(range(len(decadentes)), [1]*len(decadentes), color='#E74C3C')
                    ax2.set_yticks(range(len(decadentes)))
                    ax2.set_yticklabels(decadentes, fontsize=9)
                    ax2.set_xlim(0, 1.5)
                    ax2.set_xticks([])
                    ax2.set_title('Palabras Decadentes', fontsize=12, fontweight='bold', color='#C0392B')
                
                path = os.path.join(self.graficas_dir, 'grafica_3_tendencias.png')
                plt.tight_layout()
                plt.savefig(path, dpi=150, bbox_inches='tight')
                plt.close()
                graficas_paths.append(path)
            
            # Gráfica 4: Estadísticas generales
            estadisticas = self.datos.get('estadisticas', {})
            if estadisticas:
                fig, ax = plt.subplots(figsize=(6, 4))
                
                labels = ['Registros\nProcesados']
                valores = [estadisticas.get('total_registros', 0)]
                
                ax.bar(labels, valores, color='#3498DB', width=0.5)
                ax.set_ylabel('Cantidad', fontsize=10, fontweight='bold')
                ax.set_title('Registros Analizados', fontsize=12, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                
                # Agregar valores en las barras
                for i, v in enumerate(valores):
                    ax.text(i, v + 50, str(v), ha='center', va='bottom', fontweight='bold', fontsize=11)
                
                path = os.path.join(self.graficas_dir, 'grafica_4_estadisticas.png')
                plt.tight_layout()
                plt.savefig(path, dpi=150, bbox_inches='tight')
                plt.close()
                graficas_paths.append(path)
            
            return graficas_paths
        
        except Exception as e:
            print(f"  ⚠️  Error generando gráficas dinámicas: {e}")
            return []
    
    
    def _agregar_conclusiones(self) -> None:
        """Agrega diapositiva de conclusiones"""
        slide = self._crear_slide_titulo("Conclusiones")
        
        sintesis = self.resultados.get('sintesis', {})
        hallazgos = sintesis.get('hallazgos_principales', [])
        
        # Hallazgos principales
        hall_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5))
        hall_frame = hall_box.text_frame
        hall_frame.word_wrap = True
        
        for i, hallazgo in enumerate(hallazgos[:5]):
            if i == 0:
                p = hall_frame.paragraphs[0]
            else:
                p = hall_frame.add_paragraph()
            p.text = f"• {hallazgo}"
            p.font.size = Pt(12)
            p.font.color.rgb = self.color_texto
            p.space_after = Pt(8)
            p.level = 0
    
    def _agregar_recomendaciones(self) -> None:
        """Agrega diapositiva de recomendaciones"""
        slide = self._crear_slide_titulo("Recomendaciones")
        
        sintesis = self.resultados.get('sintesis', {})
        recomendaciones = sintesis.get('recomendaciones', [])
        
        # Recomendaciones
        rec_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(5))
        rec_frame = rec_box.text_frame
        rec_frame.word_wrap = True
        
        for i, recom in enumerate(recomendaciones[:6]):
            if i == 0:
                p = rec_frame.paragraphs[0]
            else:
                p = rec_frame.add_paragraph()
            p.text = f"• {recom}"
            p.font.size = Pt(12)
            p.font.color.rgb = self.color_texto
            p.space_after = Pt(8)
            p.level = 0
    
    def _crear_slide_titulo(self, titulo: str):
        """Crea un slide con título y fondo"""
        slide_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Fondo blanco
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.color_blanco
        
        # Línea superior
        linea = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.1))
        linea.fill.solid()
        linea.fill.fore_color.rgb = self.color_primario
        linea.line.color.rgb = self.color_primario
        
        # Título
        titulo_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(8.4), Inches(0.7))
        titulo_frame = titulo_box.text_frame
        p = titulo_frame.paragraphs[0]
        p.text = titulo
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = self.color_primario
        
        return slide
    
    def _crear_slide_vacio(self):
        """Crea un slide en blanco"""
        slide_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(slide_layout)
        
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.color_blanco
        
        return slide


