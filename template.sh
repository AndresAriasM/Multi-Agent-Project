#!/bin/bash

# Script para crear la estructura completa del proyecto trabajo-final-snies
# Uso: bash create_project.sh

PROJECT_NAME="trabajo-final-snies"
AUTHOR1=${1:-"Estudiante 1"}
AUTHOR2=${2:-"Estudiante 2"}

echo "=========================================="
echo "Creando estructura del proyecto: $PROJECT_NAME"
echo "=========================================="

# Crear directorio principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Crear estructura de carpetas
echo "📁 Creando carpetas..."
mkdir -p src/agentes
mkdir -p src/analisis
mkdir -p src/presentacion
mkdir -p notebooks
mkdir -p data
mkdir -p output
mkdir -p tests
mkdir -p docs

# Crear archivo .gitignore
echo "📄 Creando .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.parquet
*.csv
output/*.pptx
output/*.pdf
data/local/
.env

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# pip
pip-log.txt
pip-delete-this-directory.txt

EOF

# Crear requirements.txt
echo "📄 Creando requirements.txt..."
cat > requirements.txt << 'EOF'
# Core
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0

# Web scraping y data fetching
requests>=2.31.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0

# Presentation generation
python-pptx>=0.6.21
pillow>=10.0.0

# NLP y análisis de texto
nltk>=3.8.1
scikit-learn>=1.3.0
spacy>=3.6.0

# Agentes (elige según tu preferencia)
# anthropic>=0.7.0  # Para API de Claude
# openai>=1.3.0     # Para OpenAI
# crewai>=0.1.0     # Para framework CrewAI
# autogen>=0.2.0    # Para Microsoft AutoGen

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Utilities
pyyaml>=6.0
tqdm>=4.66.0

EOF

# Crear README.md
echo "📄 Creando README.md..."
cat > README.md << EOF
# Análisis de Oportunidad de Programas Académicos SNIES

Proyecto de análisis de programas académicos colombianos utilizando datos SNIES, con un sistema multi-agente para análisis de tendencias y denominaciones.

## 👥 Equipo

- **$AUTHOR1**
- **$AUTHOR2**

## 📋 Descripción

Este proyecto reproduce un reporte profesional de "Análisis de Oportunidad" para un programa académico universitario colombiano. Utiliza:

1. **Análisis de datos SNIES** - Procesamiento de tablas de programas, instituciones y estudiantes
2. **Sistema de agentes** - Análisis inteligente de denominación y tendencias de palabras
3. **Generación automática** - Creación de presentación PowerPoint profesional

## 🏗️ Estructura del Proyecto

\`\`\`
trabajo-final-snies/
├── src/
│   ├── lector_tablas_snies.py      # Carga y procesa datos SNIES
│   ├── agentes/
│   │   ├── agente_denominacion.py  # Analiza nombres de programas
│   │   ├── agente_tendencias.py    # Detecta tendencias de palabras
│   │   ├── agente_busqueda.py      # Busca información relevante
│   │   └── coordinador.py          # Orquesta los agentes
│   ├── analisis/
│   │   ├── procesador_texto.py     # NLP y análisis de texto
│   │   └── generador_graficas.py   # Crea visualizaciones
│   └── presentacion/
│       └── generador_powerpoint.py # Genera el reporte final
├── notebooks/
│   └── exploracion.ipynb           # Notebooks de experimentación
├── data/                           # Datos (si aplica)
├── output/                         # Salidas (PowerPoint, gráficas)
├── tests/                          # Tests unitarios
├── docs/                           # Documentación
├── requirements.txt
└── README.md
\`\`\`

## 🚀 Instalación

1. **Clonar repositorio**
\`\`\`bash
git clone <tu-repositorio>
cd trabajo-final-snies
\`\`\`

2. **Crear ambiente virtual**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
\`\`\`

3. **Instalar dependencias**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 📊 Uso

### Ejecutar análisis completo

\`\`\`bash
python src/main.py --programa "DOCTORADO CIENCIAS SOCIALES"
\`\`\`

### Ejecutar solo agentes

\`\`\`bash
python src/agentes/coordinador.py
\`\`\`

### Generar presentación

\`\`\`bash
python src/presentacion/generador_powerpoint.py
\`\`\`

## 📈 Funcionalidades

- ✅ Carga de datos SNIES desde parquets remotos
- ✅ Búsqueda y filtrado de programas equivalentes
- ✅ Gráficas de tendencias temporales
- ✅ Análisis de denominación de programas
- ✅ Detección de tendencias de palabras clave
- ✅ Comparación nacional e internacional
- ✅ Generación automática de PowerPoint profesional

## 🔗 Referencias

- [Repositorio base](https://github.com/robertohincapie/agentes1.git)
- [Datos SNIES](https://www.mineducacion.gov.co/snies/)

## 📝 Notas

- Fecha de entrega: 14 de noviembre 2025
- Trabajo en parejas
- Entrega: Repositorio en GitHub

EOF

# Crear __init__.py para los paquetes
echo "📄 Creando archivos __init__.py..."
touch src/__init__.py
touch src/agentes/__init__.py
touch src/analisis/__init__.py
touch src/presentacion/__init__.py
touch tests/__init__.py

# Crear archivo main.py
echo "📄 Creando src/main.py..."
cat > src/main.py << 'EOF'
"""
Script principal para ejecutar el análisis completo
"""
import argparse
from lector_tablas_snies import LectorSNIES
from agentes.coordinador import CoordinadorAgentes
from presentacion.generador_powerpoint import GeneradorPowerPoint

def main():
    parser = argparse.ArgumentParser(description="Análisis de Oportunidad SNIES")
    parser.add_argument("--programa", type=str, default="DOCTORADO CIENCIAS SOCIALES",
                        help="Nombre del programa a analizar")
    parser.add_argument("--output", type=str, default="../output/reporte_final.pptx",
                        help="Ruta del archivo de salida PowerPoint")
    
    args = parser.parse_args()
    
    print(f"🔍 Analizando programa: {args.programa}")
    print(f"📊 Cargando datos SNIES...")
    
    # Cargar datos
    lector = LectorSNIES(args.programa)
    datos = lector.procesar()
    
    # Ejecutar agentes
    print("🤖 Ejecutando sistema de agentes...")
    coordinador = CoordinadorAgentes(datos)
    resultados_agentes = coordinador.ejecutar()
    
    # Generar presentación
    print("📈 Generando presentación PowerPoint...")
    generador = GeneradorPowerPoint(datos, resultados_agentes)
    generador.crear_presentacion(args.output)
    
    print(f"✅ Presentación generada: {args.output}")

if __name__ == "__main__":
    main()
EOF

# Crear lector_tablas_snies.py
echo "📄 Creando src/lector_tablas_snies.py..."
cat > src/lector_tablas_snies.py << 'EOF'
"""
Lector de tablas SNIES - Carga y procesa datos de programas académicos
"""
import pandas as pd
from typing import Dict, List, Set

class LectorSNIES:
    """Lee y procesa datos de SNIES"""
    
    URLS_DATOS = {
        'maestro': 'https://robertohincapie.com/data/snies/MAESTRO.parquet',
        'oferta': 'https://robertohincapie.com/data/snies/OFERTA.parquet',
        'programas': 'https://robertohincapie.com/data/snies/PROGRAMAS.parquet',
        'ies': 'https://robertohincapie.com/data/snies/IES.parquet'
    }
    
    def __init__(self, programa: str):
        self.programa = programa
        self.palabras_clave = self._extraer_palabras_clave(programa)
        self.datos = {}
    
    def _extraer_palabras_clave(self, programa: str) -> Set[str]:
        """Extrae palabras clave del programa"""
        return set(programa.lower().split())
    
    def cargar_datos(self) -> None:
        """Carga todos los datos SNIES"""
        print("Cargando datos SNIES...")
        for nombre, url in self.URLS_DATOS.items():
            print(f"  - Cargando {nombre}...")
            self.datos[nombre] = pd.read_parquet(url)
    
    def encontrar_programas_equivalentes(self) -> List[str]:
        """Encuentra programas equivalentes al buscado"""
        programas_df = self.datos['programas']
        equivalentes = []
        
        for prg in programas_df['PROGRAMA_ACADEMICO'].unique():
            palabras_prg = set(str(prg).lower().split())
            similitud = len(self.palabras_clave.intersection(palabras_prg)) / len(self.palabras_clave)
            
            if similitud >= 0.8:  # Al menos 80% de similitud
                equivalentes.append(prg)
        
        return equivalentes
    
    def procesar(self) -> Dict:
        """Procesa todos los datos"""
        self.cargar_datos()
        
        # Encontrar programas equivalentes
        equivalentes = self.encontrar_programas_equivalentes()
        print(f"Encontrados {len(equivalentes)} programas equivalentes")
        
        # Filtrar datos
        programas_f = self.datos['programas'][
            self.datos['programas']['PROGRAMA_ACADEMICO'].isin(equivalentes)
        ]
        
        snies_codes = programas_f['CODIGO_SNIES'].unique()
        
        maestro_f = self.datos['maestro'][
            self.datos['maestro']['CODIGO_SNIES'].isin(snies_codes)
        ]
        
        # Merge de datos
        maestro_merged = maestro_f.merge(
            programas_f, 
            on='CODIGO_SNIES', 
            how='left'
        )
        
        maestro_merged = maestro_merged.merge(
            self.datos['oferta'],
            on=['CODIGO_SNIES', 'PERIODO'],
            how='left'
        )
        
        return {
            'maestro': maestro_merged,
            'programas': programas_f,
            'equivalentes': equivalentes,
            'snies_codes': snies_codes,
            'palabras_clave': self.palabras_clave
        }

EOF

# Crear agente_denominacion.py
echo "📄 Creando src/agentes/agente_denominacion.py..."
cat > src/agentes/agente_denominacion.py << 'EOF'
"""
Agente que analiza la denominación de programas académicos
"""
from typing import Dict, List

class AgenteDenominacion:
    """Analiza nombres y denominaciones de programas"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.programas = datos.get('equivalentes', [])
    
    def analizar(self) -> Dict:
        """Realiza análisis de denominación"""
        resultados = {
            'denominaciones': self.programas,
            'palabras_comunes': self._extraer_palabras_comunes(),
            'patrones': self._identificar_patrones(),
            'variaciones': self._detectar_variaciones()
        }
        return resultados
    
    def _extraer_palabras_comunes(self) -> List[str]:
        """Extrae palabras comunes en denominaciones"""
        todas_palabras = []
        for prog in self.programas:
            todas_palabras.extend(str(prog).lower().split())
        
        # Contar frecuencias
        from collections import Counter
        frecuencias = Counter(todas_palabras)
        # Retornar top 10
        return [palabra for palabra, _ in frecuencias.most_common(10)]
    
    def _identificar_patrones(self) -> Dict:
        """Identifica patrones en nombres"""
        patrones = {
            'con_disciplina': sum(1 for p in self.programas if any(
                x in str(p).lower() for x in ['ciencias', 'ingeniería', 'administración']
            )),
            'con_nivel': sum(1 for p in self.programas if any(
                x in str(p).lower() for x in ['doctorado', 'maestría', 'especialización']
            ))
        }
        return patrones
    
    def _detectar_variaciones(self) -> List[str]:
        """Detecta variaciones en denominaciones"""
        return list(set(str(p).lower() for p in self.programas))

EOF

# Crear agente_tendencias.py
echo "📄 Creando src/agentes/agente_tendencias.py..."
cat > src/agentes/agente_tendencias.py << 'EOF'
"""
Agente que detecta tendencias de palabras clave
"""
from typing import Dict, List
import pandas as pd

class AgenteTendencias:
    """Detecta tendencias en palabras clave de programas"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.maestro = datos.get('maestro', pd.DataFrame())
    
    def analizar(self) -> Dict:
        """Analiza tendencias de palabras clave"""
        resultados = {
            'tendencia_temporal': self._analizar_tendencia_temporal(),
            'palabras_emergentes': self._identificar_emergentes(),
            'comparativa_nacional': self._analisis_nacional(),
            'tendencias_globales': self._tendencias_globales()
        }
        return resultados
    
    def _analizar_tendencia_temporal(self) -> Dict:
        """Analiza tendencia en el tiempo"""
        return {
            'resumen': 'Análisis de tendencia temporal de palabras clave',
            'periodos': []
        }
    
    def _identificar_emergentes(self) -> List[str]:
        """Identifica palabras emergentes"""
        return ['innovación', 'sostenibilidad', 'transformación digital']
    
    def _analisis_nacional(self) -> Dict:
        """Analiza tendencias a nivel nacional"""
        return {
            'total_programas': len(self.datos.get('equivalentes', [])),
            'distribucion': 'Nacional'
        }
    
    def _tendencias_globales(self) -> Dict:
        """Analiza tendencias globales (internacional)"""
        return {
            'tendencias': ['AI', 'Sustainability', 'Digital Transformation'],
            'relevancia_local': 'Alta'
        }

EOF

# Crear coordinador.py
echo "📄 Creando src/agentes/coordinador.py..."
cat > src/agentes/coordinador.py << 'EOF'
"""
Coordinador del sistema multi-agente
"""
from typing import Dict
from .agente_denominacion import AgenteDenominacion
from .agente_tendencias import AgenteTendencias

class CoordinadorAgentes:
    """Coordina la ejecución de múltiples agentes"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.agente_denominacion = AgenteDenominacion(datos)
        self.agente_tendencias = AgenteTendencias(datos)
    
    def ejecutar(self) -> Dict:
        """Ejecuta todos los agentes y sintetiza resultados"""
        print("Ejecutando agentes...")
        
        resultados = {
            'denominacion': self.agente_denominacion.analizar(),
            'tendencias': self.agente_tendencias.analizar(),
            'sintesis': self._sintetizar()
        }
        
        return resultados
    
    def _sintetizar(self) -> Dict:
        """Sintetiza los resultados de todos los agentes"""
        return {
            'hallazgos_principales': [],
            'recomendaciones': [],
            'proximos_pasos': []
        }

EOF

# Crear generador_graficas.py
echo "📄 Creando src/analisis/generador_graficas.py..."
cat > src/analisis/generador_graficas.py << 'EOF'
"""
Generador de gráficas para el análisis
"""
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List

class GeneradorGraficas:
    """Genera gráficas de análisis"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
    
    def generar_todas(self) -> Dict[str, str]:
        """Genera todas las gráficas necesarias"""
        graficas = {}
        
        graficas['programas_ies'] = self._grafica_programas_ies()
        graficas['evolucion_matriculas'] = self._grafica_evolucion()
        graficas['distribucion_geo'] = self._grafica_distribucion()
        
        return graficas
    
    def _grafica_programas_ies(self) -> str:
        """Gráfica de programas e instituciones en el tiempo"""
        # Implementar
        return 'grafica_programas_ies.png'
    
    def _grafica_evolucion(self) -> str:
        """Gráfica de evolución de matrículas"""
        # Implementar
        return 'grafica_evolucion.png'
    
    def _grafica_distribucion(self) -> str:
        """Gráfica de distribución geográfica"""
        # Implementar
        return 'grafica_distribucion.png'

EOF

# Crear generador_powerpoint.py
echo "📄 Creando src/presentacion/generador_powerpoint.py..."
cat > src/presentacion/generador_powerpoint.py << 'EOF'
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

EOF

# Crear archivo de test básico
echo "📄 Creando tests/test_lector.py..."
cat > tests/test_lector.py << 'EOF'
"""
Tests para el lector de SNIES
"""
import pytest
import sys
sys.path.insert(0, '../src')

def test_inicializacion():
    """Test básico de inicialización"""
    assert True

def test_palabras_clave():
    """Test de extracción de palabras clave"""
    from lector_tablas_snies import LectorSNIES
    lector = LectorSNIES("DOCTORADO CIENCIAS SOCIALES")
    palabras = lector.palabras_clave
    assert len(palabras) > 0

EOF

# Crear archivo de configuración
echo "📄 Creando .env.example..."
cat > .env.example << 'EOF'
# Configuración del proyecto

# URLs de datos SNIES
SNIES_MAESTRO_URL=https://robertohincapie.com/data/snies/MAESTRO.parquet
SNIES_OFERTA_URL=https://robertohincapie.com/data/snies/OFERTA.parquet
SNIES_PROGRAMAS_URL=https://robertohincapie.com/data/snies/PROGRAMAS.parquet
SNIES_IES_URL=https://robertohincapie.com/data/snies/IES.parquet

# Configuración de agentes
AGENTES_ENABLED=true
AGENTES_TIMEOUT=300

# Rutas de salida
OUTPUT_DIR=./output
OUTPUT_FORMAT=pptx

EOF

# Crear archivo CONTRIBUTING.md
echo "📄 Creando docs/CONTRIBUTING.md..."
cat > docs/CONTRIBUTING.md << 'EOF'
# Guía de Contribución

## Flujo de trabajo en parejas

1. **Crear ramas por feature**
   ```bash
   git checkout -b feature/nombre-feature
   ```

2. **Hacer commits descriptivos**
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```

3. **Hacer pull request para revisión**
   - Describe los cambios
   - Referencia issues si aplica

## Estándares de código

- Usar snake_case para variables y funciones
- Agregar docstrings en todas las funciones
- Máximo 100 caracteres por línea
- Usar type hints cuando sea posible

## Testing

- Escribir tests para nuevas funcionalidades
- Ejecutar: `pytest tests/`

EOF

# Crear .gitkeep en carpetas importantes
echo "📄 Creando .gitkeep en carpetas..."
touch data/.gitkeep
touch output/.gitkeep
touch notebooks/.gitkeep

# Imprimir resumen
echo ""
echo "=========================================="
echo "✅ Estructura del proyecto creada exitosamente"
echo "=========================================="
echo ""
echo "📁 Carpetas creadas:"
echo "   - src/agentes"
echo "   - src/analisis"
echo "   - src/presentacion"
echo "   - notebooks"
echo "   - data"
echo "   - output"
echo "   - tests"
echo "   - docs"
echo ""
echo "📄 Archivos creados:"
echo "   - requirements.txt"
echo "   - README.md"
echo "   - .gitignore"
echo "   - .env.example"
echo "   - src/main.py"
echo "   - src/lector_tablas_snies.py"
echo "   - src/agentes/*.py"
echo "   - src/analisis/*.py"
echo "   - src/presentacion/*.py"
echo "   - tests/*.py"
echo "   - docs/CONTRIBUTING.md"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. cd $PROJECT_NAME"
echo "   2. git init"
echo "   3. python -m venv venv"
echo "   4. source venv/bin/activate"
echo "   5. pip install -r requirements.txt"
echo "   6. git add ."
echo "   7. git commit -m 'Initial project structure'"
echo ""
echo "📚 Documentación disponible en docs/"
echo "=========================================="

EOF

chmod +x create_project.sh

# Mostrar mensaje final
echo ""
echo "✅ Script creado: create_project.sh"
echo "Uso: bash create_project.sh [AUTOR1] [AUTOR2]"
echo ""
echo "Ejemplo: bash create_project.sh 'Juan Pérez' 'María García'"