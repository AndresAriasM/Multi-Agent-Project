"""
Cliente de Azure OpenAI para análisis de programas académicos
Ubicación: src/agentes/llm_handler.py
"""

from typing import Dict, List
import json
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

Responde SOLO con este JSON (sin texto adicional):
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
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Respuesta no es JSON válido")
            return {"denominacion_oficial": programa_objetivo}
        except Exception as e:
            print(f"Error en análisis: {e}")
            return {"error": str(e)}
    
    def analizar_tendencias(self, programa: str) -> Dict:
        """
        Analiza tendencias de palabras clave
        
        Args:
            programa: Nombre del programa
            
        Returns:
            Dict con tendencias en JSON
        """
        system_prompt = "Eres analista de tendencias en educación superior. Responde SOLO con JSON válido."
        
        user_prompt = f"""Analiza tendencias para: {programa}

Responde SOLO con este JSON (sin texto adicional):
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
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Respuesta no es JSON válido")
            return {"emergentes": []}
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
            return f"Error: {e}"
    
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

Responde SOLO con este JSON:
{{"insights": ["i1", "i2", "i3", "i4", "i5"]}}"""
        
        try:
            response = self.call(system_prompt, user_prompt, max_tokens=500)
            data = json.loads(response)
            return data.get("insights", [])
        except json.JSONDecodeError:
            print(f"Respuesta no es JSON válido")
            return []
        except Exception as e:
            print(f"Error extrayendo insights: {e}")
            return []