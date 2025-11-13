"""
Agente que detecta tendencias de palabras clave
Ubicación: src/agentes/agente_tendencias.py
"""

from typing import Dict, List
import pandas as pd
import json
from .llm_handler import LLMHandler


class AgenteTendencias:
    """Detecta tendencias en palabras clave de programas"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.maestro = datos.get('maestro', pd.DataFrame())
        try:
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None
    
    def analizar(self) -> Dict:
        """Analiza tendencias de palabras clave"""
        print("📈 Analizando tendencias...")
        
        programa = self.datos.get('nombre', 'Programa')
        
        if not self.llm:
            print("⚠️  LLMHandler no disponible, usando análisis básico")
            return self._analisis_basico()
        
        try:
            # Llamar a Azure OpenAI
            respuesta_ia = self.llm.analizar_tendencias(programa)
            
            # Si es dict, es JSON parseado
            if isinstance(respuesta_ia, dict):
                analisis_ia = respuesta_ia
            else:
                # Si es string, intentar parsear
                try:
                    analisis_ia = json.loads(respuesta_ia)
                except:
                    analisis_ia = self._analisis_basico()
                    
        except Exception as e:
            print(f"⚠️  Error en IA: {e}, usando análisis básico")
            analisis_ia = self._analisis_basico()
        
        resultados = {
            'palabras_emergentes': analisis_ia.get('emergentes', []),
            'palabras_decadentes': analisis_ia.get('decadentes', []),
            'tendencias_nacionales': analisis_ia.get('nacionales', {}),
            'tendencias_globales': analisis_ia.get('globales', {}),
            'analisis_ia': analisis_ia,
            'estadisticas': self._calcular_estadisticas()
        }
        
        return resultados
    
    def _analisis_basico(self) -> Dict:
        """Análisis básico sin IA"""
        return {
            'emergentes': ['Transformación digital', 'Sostenibilidad', 'Innovación'],
            'decadentes': [],
            'nacionales': {'tendencia': 'Crecimiento en programas STEM'},
            'globales': {'tendencia': 'Énfasis en competencias digitales'},
            'innovacion': ['Metodologías híbridas'],
            'recomendaciones': ['Análisis básico']
        }
    
    def _calcular_estadisticas(self) -> Dict:
        """Calcula estadísticas"""
        if self.maestro.empty:
            return {
                'total_periodos': 0,
                'instituciones': 0,
                'programas': 0,
                'departamentos': 0
            }
        
        stats = {
            'total_periodos': self.maestro['PERIODO'].nunique() if 'PERIODO' in self.maestro.columns else 0,
            'instituciones': self.maestro['CODIGO_INSTITUCION_x'].nunique() if 'CODIGO_INSTITUCION_x' in self.maestro.columns else 0,
            'programas': self.maestro['CODIGO_SNIES'].nunique() if 'CODIGO_SNIES' in self.maestro.columns else 0,
            'departamentos': self.maestro['DEPARTAMENTO_PROGRAMA'].nunique() if 'DEPARTAMENTO_PROGRAMA' in self.maestro.columns else 0
        }
        
        return stats