"""
Cliente de Azure OpenAI para análisis de programas académicos
Ubicación: src/agentes/llm_handler.py
VERSIÓN CORREGIDA - Con manejo robusto de JSON
"""

from typing import Dict, List
import json
import re
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class LLMHandler:
    """Maneja las llamadas a Azure OpenAI para análisis de SNIES"""

    def __init__(self):
        """Inicializa el cliente de Azure OpenAI"""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY no está configurada en .env")

        self.client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-15-preview",
            azure_endpoint="https://pnl-maestria.openai.azure.com"
        )
        self.model = "gpt-4.1-nano"

    def _limpiar_respuesta_json(self, texto: str) -> str:
        """
        Limpia la respuesta para asegurar que sea JSON válido
        Remueve markdown, espacios extras, etc.
        """
        # Remover bloques de código markdown
        texto = re.sub(r'```json\s*\n', '', texto)
        texto = re.sub(r'```\s*\n', '', texto)
        texto = re.sub(r'```', '', texto)

        # Remover espacios y saltos al inicio/final
        texto = texto.strip()

        return texto

    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """
        Realiza una llamada a Azure OpenAI

        Args:
            system_prompt: Instrucción del sistema
            user_prompt: Prompt del usuario
            max_tokens: Máximo de tokens en la respuesta

        Returns:
            Contenido de la respuesta
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error en llamada a OpenAI: {e}")
            raise

    def analizar_denominacion(self, programas: List[str], programa_objetivo: str) -> Dict:
        """
        Analiza la denominación de un programa académico

        Args:
            programas: Lista de programas encontrados
            programa_objetivo: El programa a analizar

        Returns:
            Dict con análisis en JSON
        """
        programas_str = "\n".join(f"- {p}" for p in programas[:15])

        system_prompt = "Eres experto en educación superior colombiana. Responde SOLO con JSON válido."

        user_prompt = f"""Analiza la denominación del programa académico:

Programa objetivo: {programa_objetivo}

Programas equivalentes encontrados:
{programas_str}

Responde SOLO con este JSON (sin texto adicional, sin markdown):
{{
    "denominacion_oficial": "nombre estandarizado",
    "variaciones_encontradas": ["var1", "var2"],
    "patrones": {{"con_nivel": 5}},
    "palabras_clave": ["palabra1", "palabra2"],
    "clasificacion": "Doctorado",
    "internacionales": ["PhD"],
    "hallazgos": ["hallazgo1"]
}}"""

        try:
            response = self.call(system_prompt, user_prompt, max_tokens=1000)
            # ✅ Limpiar respuesta
            response_limpio = self._limpiar_respuesta_json(response)
            return json.loads(response_limpio)
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            print(f"    Respuesta original: {response[:200]}")
            # ✅ Retornar estructura básica válida
            return {
                "denominacion_oficial": programa_objetivo,
                "variaciones_encontradas": programas[:5],
                "patrones": {"con_nivel": len(programas)},
                "palabras_clave": programa_objetivo.lower().split(),
                "clasificacion": "No disponible",
                "internacionales": [],
                "hallazgos": ["Análisis con limitaciones de IA"]
            }
        except Exception as e:
            print(f"Error en análisis: {e}")
            return {
                "denominacion_oficial": programa_objetivo,
                "error": str(e)
            }

    def analizar_denominacion_con_contexto(self, programas: List[str], programa_objetivo: str,
                                          contexto_mercado: Dict, instituciones: Dict,
                                          modalidades: Dict, duracion: Dict = None,
                                          matriculas: Dict = None) -> Dict:
        """
        Analiza denominación con contexto completo del mercado

        Args:
            programas: Lista de denominaciones
            programa_objetivo: Programa a analizar
            contexto_mercado: Contexto del mercado
            instituciones: Información de instituciones
            modalidades: Modalidades disponibles
            duracion: Información de duración
            matriculas: Información de matrículas

        Returns:
            Dict con análisis enriquecido
        """
        programas_str = "\n".join(f"- {p}" for p in programas[:15])

        contexto_str = f"""
CONTEXTO DEL MERCADO:
- Total de instituciones oferentes: {contexto_mercado.get('competencia', {}).get('total_instituciones', 'N/A')}
- Universidades: {contexto_mercado.get('competencia', {}).get('universidades', 'N/A')}
- Tecnológicas: {contexto_mercado.get('competencia', {}).get('tecnologicas', 'N/A')}
- Sector privado: {contexto_mercado.get('sector', {}).get('porcentaje_privado', 'N/A')}%
- Acreditadas alta calidad: {contexto_mercado.get('acreditacion', {}).get('porcentaje_acreditacion', 'N/A')}%
- Nivel de demanda: {contexto_mercado.get('demanda', {}).get('nivel_demanda', 'N/A')}
- Nuevos inscritos recientes: {contexto_mercado.get('demanda', {}).get('total_nuevos_reciente', 'N/A')}
- Mercado homogéneo: {contexto_mercado.get('precios', {}).get('mercado_homogeneo', 'N/A')}

MODALIDADES DISPONIBLES: {', '.join(modalidades.get('disponibles', []))}
NÚMERO DE INSTITUCIONES: {instituciones.get('total', 'N/A')}
"""

        if duracion:
            contexto_str += f"\nDURACIÓN: {duracion.get('periodos_disponibles', [])} periodos"

        if matriculas and matriculas.get('promedio'):
            contexto_str += f"\nRANGO DE MATRÍCULAS: ${matriculas.get('minima', 0):,.0f} - ${matriculas.get('maxima', 0):,.0f}"

        system_prompt = """Eres experto en educación superior colombiana y análisis de mercado académico.
Debes proporcionar un análisis de denominación considerando el CONTEXTO COMPLETO del mercado.
Responde SOLO con JSON válido, SIN markdown, SIN explicaciones adicionales."""

        user_prompt = f"""Analiza la denominación y posicionamiento en el mercado del programa:

Programa objetivo: {programa_objetivo}

Denominaciones encontradas:
{programas_str}

{contexto_str}

PROPORCIONA ANÁLISIS que incluya:
1. Denominación oficial estandarizada
2. Variaciones encontradas
3. Posicionamiento en el mercado
4. Recomendaciones competitivas
5. Oportunidades de diferenciación
6. Recomendaciones para estudiantes

Responde SOLO con JSON (sin markdown):
{{
    "denominacion_oficial": "nombre estandarizado",
    "variaciones_encontradas": ["var1", "var2"],
    "patrones": {{"con_nivel": 5}},
    "palabras_clave": ["palabra1"],
    "clasificacion": "Doctorado",
    "internacionales": ["PhD"],
    "posicionamiento_mercado": {{
        "competencia_nivel": "Alto/Medio/Bajo",
        "saturacion": "Alta/Media/Baja",
        "diferenciadores": ["diferenciador1"],
        "tendencia": "creciente/estable/decreciente"
    }},
    "recomendaciones_competitivas": ["rec1", "rec2"],
    "oportunidades_diferenciacion": ["oport1"],
    "valor_para_estudiante": "Por qué este programa es valioso",
    "hallazgos": ["hallazgo1"]
}}"""

        try:
            response = self.call(system_prompt, user_prompt, max_tokens=1500)
            # ✅ Limpiar respuesta
            response_limpio = self._limpiar_respuesta_json(response)
            return json.loads(response_limpio)
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            print(f"    Respuesta original: {response[:200]}")
            # ✅ Retornar estructura básica válida
            return {
                "denominacion_oficial": programa_objetivo,
                "variaciones_encontradas": programas[:5],
                "patrones": {"con_nivel": len(programas)},
                "palabras_clave": programa_objetivo.lower().split(),
                "clasificacion": "No disponible",
                "internacionales": [],
                "posicionamiento_mercado": {
                    "competencia_nivel": contexto_mercado.get('competencia', {}).get('total_instituciones', 0) > 5 and "Alto" or "Bajo",
                    "saturacion": "No disponible",
                    "diferenciadores": [],
                    "tendencia": "estable"
                },
                "recomendaciones_competitivas": ["Análisis con limitaciones de IA"],
                "oportunidades_diferenciacion": [],
                "valor_para_estudiante": "Profesionales formados según demanda del mercado",
                "hallazgos": ["Análisis con limitaciones de IA"]
            }
        except Exception as e:
            print(f"Error en análisis: {e}")
            return {"denominacion_oficial": programa_objetivo, "error": str(e)}

    def analizar_tendencias(self, programa: str) -> Dict:
        """
        Analiza tendencias de palabras clave

        Args:
            programa: Nombre del programa

        Returns:
            Dict con tendencias en JSON
        """
        system_prompt = "Eres analista de tendencias en educación superior. Responde SOLO con JSON válido, sin markdown."

        user_prompt = f"""Analiza tendencias para: {programa}

Responde SOLO con JSON (sin markdown):
{{
    "emergentes": ["transformación digital", "sostenibilidad"],
    "decadentes": [],
    "nacionales": {{"tendencia": "Crecimiento STEM"}},
    "globales": {{"tendencia": "Competencias digitales"}},
    "innovacion": ["metodologías híbridas"],
    "recomendaciones": ["Actualizar"]
}}"""

        try:
            response = self.call(system_prompt, user_prompt, max_tokens=1000)
            # ✅ Limpiar respuesta
            response_limpio = self._limpiar_respuesta_json(response)
            return json.loads(response_limpio)
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            # ✅ Retornar estructura básica válida
            return {
                "emergentes": ["Transformación digital", "Inteligencia artificial"],
                "decadentes": [],
                "nacionales": {"tendencia": "Crecimiento en demanda"},
                "globales": {"tendencia": "Competencias digitales"},
                "innovacion": ["Metodologías híbridas"],
                "recomendaciones": ["Análisis con limitaciones de IA"]
            }
        except Exception as e:
            print(f"Error en tendencias: {e}")
            return {"error": str(e)}

    def generar_resumen(self, contexto: str, programa: str) -> str:
        """
        Genera resumen ejecutivo

        Args:
            contexto: Contexto del análisis
            programa: Nombre del programa

        Returns:
            String con resumen
        """
        system_prompt = "Eres redactor profesional especializado en educación superior."

        user_prompt = f"""Genera resumen ejecutivo para:

Programa: {programa}
Contexto: {contexto[:500]}

Máximo 250 palabras."""

        try:
            return self.call(system_prompt, user_prompt, max_tokens=800)
        except Exception as e:
            print(f"Error generando resumen: {e}")
            return f"El programa de {programa} es un programa académico de educación superior."

    def extraer_insights(self, texto: str) -> List[str]:
        """
        Extrae insights clave

        Args:
            texto: Texto a analizar

        Returns:
            Lista de insights
        """
        system_prompt = "Eres experto extrayendo insights. Responde SOLO con JSON válido."

        user_prompt = f"""Extrae los 5 insights más importantes:

{texto[:1500]}

Responde SOLO con JSON:
{{"insights": ["i1", "i2", "i3", "i4", "i5"]}}"""

        try:
            response = self.call(system_prompt, user_prompt, max_tokens=500)
            # ✅ Limpiar respuesta
            response_limpio = self._limpiar_respuesta_json(response)
            data = json.loads(response_limpio)
            return data.get("insights", [])
        except json.JSONDecodeError:
            print(f"⚠️  Respuesta no es JSON válido")
            return []
        except Exception as e:
            print(f"Error extrayendo insights: {e}")
            return []