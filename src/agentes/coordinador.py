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

