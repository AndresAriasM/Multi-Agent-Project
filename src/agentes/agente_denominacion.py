"""
Agente que analiza denominación de programas académicos
Ubicación: src/agentes/agente_denominacion.py
"""

from typing import Dict, List
import json
from .llm_handler import LLMHandler


class AgenteDenominacion:
    """Analiza nombres y denominaciones de programas"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.programas = datos.get('equivalentes', [])
        try:
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None
    
    def analizar(self) -> Dict:
        """Realiza análisis de denominación"""
        print("🔍 Analizando denominación de programas...")
        
        denominaciones_unicas = list(set(self.programas))
        
        if not self.llm:
            print("⚠️  LLMHandler no disponible, usando análisis básico")
            return self._analisis_basico()
        
        try:
            # Llamar a Azure OpenAI
            respuesta_ia = self.llm.analizar_denominacion(
                denominaciones_unicas,
                self.datos.get('nombre', 'Programa Académico')
            )
            
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
            'denominaciones_totales': denominaciones_unicas,
            'cantidad_variaciones': len(denominaciones_unicas),
            'analisis_ia': analisis_ia,
            'estadisticas': self._calcular_estadisticas()
        }
        
        return resultados
    
    def _analisis_basico(self) -> Dict:
        """Análisis básico sin IA"""
        return {
            'denominacion_oficial': self.programas[0] if self.programas else 'No disponible',
            'variaciones_encontradas': self.programas[:10],
            'patrones_nombres': self._identificar_patrones(),
            'palabras_clave': self._extraer_palabras_comunes(),
            'clasificacion': self._clasificar_programa(),
            'equivalentes_internacionales': ['PhD', 'Master'],
            'hallazgos': ['Análisis básico']
        }
    
    def _calcular_estadisticas(self) -> Dict:
        """Calcula estadísticas"""
        todas_palabras = []
        for prog in self.programas:
            todas_palabras.extend(str(prog).lower().split())
        
        from collections import Counter
        frecuencias = Counter(todas_palabras)
        
        return {
            'total_variaciones': len(self.programas),
            'palabras_unicas': len(set(todas_palabras)),
            'longitud_promedio': sum(len(p.split()) for p in self.programas) / len(self.programas) if self.programas else 0,
            'palabras_mas_frecuentes': dict(frecuencias.most_common(5))
        }
    
    def _identificar_patrones(self) -> Dict:
        """Identifica patrones"""
        patrones = {
            'con_disciplina': sum(1 for p in self.programas if any(
                x in str(p).lower() for x in ['ciencias', 'ingeniería', 'administración']
            )),
            'con_nivel': sum(1 for p in self.programas if any(
                x in str(p).lower() for x in ['doctorado', 'maestría', 'especialización']
            ))
        }
        return patrones
    
    def _extraer_palabras_comunes(self) -> List[str]:
        """Extrae palabras comunes"""
        todas_palabras = []
        for prog in self.programas:
            todas_palabras.extend(str(prog).lower().split())
        
        from collections import Counter
        frecuencias = Counter(todas_palabras)
        return [palabra for palabra, _ in frecuencias.most_common(10)]
    
    def _clasificar_programa(self) -> str:
        """Clasifica tipo de programa"""
        programas_texto = ' '.join(self.programas).lower()
        
        if 'doctorado' in programas_texto:
            return 'Doctorado'
        elif 'maestría' in programas_texto or 'maestria' in programas_texto:
            return 'Maestría'
        elif 'especialización' in programas_texto or 'especializacion' in programas_texto:
            return 'Especialización'
        else:
            return 'Otro'