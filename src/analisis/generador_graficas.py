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

