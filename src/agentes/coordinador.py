"""
Coordinador del sistema multi-agente
Ubicación: src/agentes/coordinador.py
"""

from typing import Dict, List
import json
from datetime import datetime
from .agente_denominacion import AgenteDenominacion
from .agente_tendencias import AgenteTendencias
from .llm_handler import LLMHandler


class CoordinadorAgentes:
    """Coordina la ejecución de múltiples agentes"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.agente_denominacion = AgenteDenominacion(datos)
        self.agente_tendencias = AgenteTendencias(datos)
        try:
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None
        self.resultados = {}
    
    def ejecutar(self) -> Dict:
        """Ejecuta todos los agentes"""
        print("\n" + "="*60)
        print("🤖 SISTEMA MULTI-AGENTE - INICIANDO ANÁLISIS")
        print("="*60 + "\n")
        
        # Ejecutar agentes
        print("1️⃣  Ejecutando Agente de Denominación...")
        denominacion = self.agente_denominacion.analizar()
        
        print("2️⃣  Ejecutando Agente de Tendencias...")
        tendencias = self.agente_tendencias.analizar()
        
        print("3️⃣  Sintetizando resultados...")
        sintesis = self._sintetizar(denominacion, tendencias)
        
        self.resultados = {
            'denominacion': denominacion,
            'tendencias': tendencias,
            'sintesis': sintesis,
            'programa': self.datos.get('nombre', 'No especificado'),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\n✅ Análisis completado\n")
        return self.resultados
    
    def _sintetizar(self, denominacion: Dict, tendencias: Dict) -> Dict:
        """Sintetiza resultados de agentes"""
        programa = self.datos.get('nombre', 'Programa Académico')
        
        denominacion_oficial = denominacion.get('analisis_ia', {}).get('denominacion_oficial', 'No disponible')
        palabras_clave = denominacion.get('analisis_ia', {}).get('palabras_clave', [])
        palabras_emergentes = tendencias.get('palabras_emergentes', [])
        
        # Generar resumen si LLM disponible
        resumen = ""
        if self.llm:
            try:
                contexto = f"Programa: {programa}, Denominación: {denominacion_oficial}"
                resumen = self.llm.generar_resumen(contexto, programa)
            except Exception as e:
                print(f"⚠️  Error generando resumen: {e}")
                resumen = "Resumen no disponible"
        else:
            resumen = f"Análisis del programa {programa}"
        
        return {
            'programa': programa,
            'denominacion_oficial': denominacion_oficial,
            'resumen_ejecutivo': resumen,
            'hallazgos_principales': self._extraer_hallazgos(denominacion, tendencias),
            'recomendaciones': self._generar_recomendaciones(denominacion, tendencias),
            'proximos_pasos': [
                'Validar denominación con expertos',
                'Implementar cambios sugeridos',
                'Monitorear tendencias periódicamente'
            ]
        }
    
    def _extraer_hallazgos(self, denominacion: Dict, tendencias: Dict) -> List[str]:
        """Extrae hallazgos"""
        hallazgos = []
        
        den_hallazgos = denominacion.get('analisis_ia', {}).get('hallazgos', [])
        if isinstance(den_hallazgos, list):
            hallazgos.extend(den_hallazgos[:2])
        
        ten_emergentes = tendencias.get('palabras_emergentes', [])
        if ten_emergentes:
            hallazgos.append(f"Palabras emergentes: {', '.join(ten_emergentes[:3])}")
        
        cantidad_var = denominacion.get('cantidad_variaciones', 0)
        hallazgos.append(f"Se encontraron {cantidad_var} variaciones del programa")
        
        return hallazgos
    
    def _generar_recomendaciones(self, denominacion: Dict, tendencias: Dict) -> List[str]:
        """Genera recomendaciones"""
        recomendaciones = []
        
        clasificacion = denominacion.get('analisis_ia', {}).get('clasificacion', '')
        if clasificacion:
            recomendaciones.append(f"Clasificar como: {clasificacion}")
        
        palabras_emergentes = tendencias.get('palabras_emergentes', [])
        if palabras_emergentes:
            recomendaciones.append(f"Incorporar términos: {', '.join(palabras_emergentes[:2])}")
        
        recomendaciones.append("Actualizar denominación en sistemas académicos")
        recomendaciones.append("Revisar equivalencias internacionales")
        
        return recomendaciones
    
    def guardar_resultados(self, filepath: str) -> None:
        """Guarda resultados en JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            resultados_str = self._convertir_para_json(self.resultados)
            json.dump(resultados_str, f, ensure_ascii=False, indent=2)
        print(f"✅ Resultados guardados en {filepath}")
    
    def _convertir_para_json(self, obj):
        """Convierte objetos para serialización JSON"""
        if isinstance(obj, dict):
            return {k: self._convertir_para_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convertir_para_json(item) for item in obj]
        else:
            return str(obj)