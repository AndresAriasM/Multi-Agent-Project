# 📚 Análisis SNIES - Sistema Multi-Agente

Aplicación inteligente para analizar programas académicos colombianos usando inteligencia artificial y datos del SNIES (Sistema Nacional de Información de Educación Superior).

## 🎯 ¿Qué hace?

Busca un programa académico y proporciona:

- **Denominaciones normalizadas** - Estandariza el nombre del programa
- **Tendencias del mercado** - Detecta palabras emergentes y en declive
- **Análisis de instituciones** - Identifica dónde se ofrece y quiénes lo ofertan
- **Oportunidades geográficas** - Hubs de concentración y zonas sin cobertura
- **Recomendaciones** - Basadas en datos del mercado

Todo con resultados descargables en **Excel** y **PowerPoint**.

---

## 🚀 Instalación Rápida

### 1. Clonar/Descargar el proyecto
```bash
git clone https://github.com/AndresAriasM/Multi-Agent-Project.git
cd Multi-Agent-Project
```

### 2. Crear ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
pip install streamlit openpyxl
```

### 4. Configurar credenciales
Crea archivo `.env` en la raíz del proyecto:
```
AZURE_OPENAI_API_KEY=tu_clave_aqui
```

### 5. Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

---

## 📖 Cómo Usar

1. **Ingresa un programa** - Escribe en el cuadro de búsqueda
   - Ej: "Ingeniería de Datos", "Maestría Administración"

2. **Haz clic en Buscar** - El sistema analiza automáticamente

3. **Ver resultados** en 4 pestañas:
   - 📊 **Resumen** - Métricas y hallazgos principales
   - 🏫 **Instituciones** - Análisis de oferentes
   - 📈 **Tendencias** - Palabras emergentes
   - 💾 **Descargar** - Excel y PowerPoint

4. **Descarga los resultados** en los formatos que necesites

---

## 🤖 Cómo Funciona

```
1. BÚSQUEDA
   └─ Encuentra programas equivalentes por similitud

2. ENRIQUECIMIENTO
   └─ Carga datos completos de SNIES

3. AGENTES IA
   ├─ Agente Denominación → Normaliza nombres
   ├─ Agente Tendencias → Detecta patrones del mercado
   └─ Agente Geografía → Analiza ubicación e instituciones

4. RESULTADOS
   └─ Presentación interactiva + Descarga (Excel, PowerPoint)
```

---

## 📊 Resultados Disponibles

### En la Aplicación (Streamlit)
- Métricas interactivas
- Tablas y gráficos
- Hallazgos y recomendaciones

### Excel
6 hojas con datos completos:
- Resumen general
- Denominaciones encontradas
- Tendencias nacionales e internacionales
- Análisis de instituciones
- Hubs geográficos
- Recomendaciones

### PowerPoint
Presentación profesional con:
- Portada y tabla de contenidos
- Análisis completo
- Gráficas y tablas
- Conclusiones y recomendaciones

---

## 🔧 Requisitos

- Python 3.11+
- Azure OpenAI API key
- 10GB de RAM disponible
- Conexión a internet (primera ejecución)

---

## ⚡ Quick Start

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install streamlit openpyxl

# 2. Configurar .env
echo "AZURE_OPENAI_API_KEY=tu_clave" > .env

# 3. Ejecutar
streamlit run app.py

# 4. Abrir navegador
# http://localhost:8501
```

---

## 📁 Estructura del Proyecto

```
Multi-Agent-Project/
├── app.py                          # App Streamlit
├── src/
│   ├── main.py                    # Script principal
│   ├── lector_tablas_snies.py     # Carga datos SNIES
│   ├── lector_datos_enriquecidos.py
│   ├── agentes/
│   │   ├── coordinador.py         # Orquesta agentes
│   │   ├── agente_denominacion.py
│   │   ├── agente_tendencias.py
│   │   ├── agente_instituciones_geografia.py
│   │   └── llm_handler.py         # Azure OpenAI
│   └── presentacion/
│       └── generador_powerpoint.py
├── requirements.txt
├── .env                           # Credenciales
└── output/                        # Resultados generados
```

---
