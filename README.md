# Análisis de Oportunidad de Programas Académicos SNIES

Proyecto de análisis de programas académicos colombianos utilizando datos SNIES, con un sistema multi-agente para análisis de tendencias y denominaciones.

## 👥 Equipo

- **Estudiante 1**
- **Estudiante 2**

## 📋 Descripción

Este proyecto reproduce un reporte profesional de "Análisis de Oportunidad" para un programa académico universitario colombiano. Utiliza:

1. **Análisis de datos SNIES** - Procesamiento de tablas de programas, instituciones y estudiantes
2. **Sistema de agentes** - Análisis inteligente de denominación y tendencias de palabras
3. **Generación automática** - Creación de presentación PowerPoint profesional

## 🏗️ Estructura del Proyecto

```
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
```

## 🚀 Instalación

1. **Clonar repositorio**
```bash
git clone <tu-repositorio>
cd trabajo-final-snies
```

2. **Crear ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## 📊 Uso

### Ejecutar análisis completo

```bash
python src/main.py --programa "DOCTORADO CIENCIAS SOCIALES"
```

### Ejecutar solo agentes

```bash
python src/agentes/coordinador.py
```

### Generar presentación

```bash
python src/presentacion/generador_powerpoint.py
```

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

