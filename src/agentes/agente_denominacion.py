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

