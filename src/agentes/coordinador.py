"""
Coordinador del sistema multi-agente - ACTUALIZADO
Ubicación: src/agentes/coordinador.py
INTEGRA: Agente de Instituciones y Geografía
"""

from typing import Dict, List
import json
from datetime import datetime
from .agente_denominacion import AgenteDenominacion
from .agente_tendencias import AgenteTendencias
from .agente_instituciones_geografia import AgenteInstitucionesGeografia
from .llm_handler import LLMHandler


class CoordinadorAgentes:
    """Coordina la ejecución de múltiples agentes incluyendo análisis institucional"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.agente_denominacion = AgenteDenominacion(datos)
        self.agente_tendencias = AgenteTendencias(datos)
        self.agente_instituciones = AgenteInstitucionesGeografia(datos)
        try:
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None
        self.resultados = {}
    
    def ejecutar(self) -> Dict:
        """Ejecuta todos los agentes"""
        print("\n" + "="*60)
        print("🤖 SISTEMA MULTI-AGENTE - INICIANDO ANÁLISIS COMPLETO")
        print("="*60 + "\n")
        
        # Ejecutar agentes
        print("1️⃣  Ejecutando Agente de Denominación...")
        denominacion = self.agente_denominacion.analizar()
        
        print("2️⃣  Ejecutando Agente de Tendencias...")
        tendencias = self.agente_tendencias.analizar()
        
        print("3️⃣  Ejecutando Agente de Instituciones y Geografía...")
        instituciones_geo = self.agente_instituciones.analizar()
        
        print("4️⃣  Sintetizando resultados...")
        sintesis = self._sintetizar(denominacion, tendencias, instituciones_geo)
        
        self.resultados = {
            'denominacion': denominacion,
            'tendencias': tendencias,
            'instituciones_geografia': instituciones_geo,
            'sintesis': sintesis,
            'programa': self.datos.get('nombre', 'No especificado'),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\n✅ Análisis completado\n")
        return self.resultados
    
    def _sintetizar(self, denominacion: Dict, tendencias: Dict, 
                   instituciones: Dict) -> Dict:
        """Sintetiza resultados de TODOS los agentes"""
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
            'hallazgos_principales': self._extraer_hallazgos(denominacion, tendencias, instituciones),
            'hallazgos_institucionales': instituciones.get('analisis_ia', {}).get('insights_clave', []),
            'recomendaciones': self._generar_recomendaciones(denominacion, tendencias, instituciones),
            'recomendaciones_institucionales': instituciones.get('recomendaciones_institucion', []),
            'hub_geograficos_principales': instituciones.get('hub_geograficos', {}).get('hubs_principales', []),
            'institucion_referente': instituciones.get('institucion_referente', {}).get('institucion_referente_top1'),
            'oportunidades_expansion': self._generar_oportunidades_expansion(instituciones),
            'proximos_pasos': [
                'Validar denominación con expertos',
                'Realizar visitas a instituciones referentes',
                'Evaluar oportunidades de expansión en regiones identificadas',
                'Monitorear tendencias periódicamente'
            ]
        }
    
    def _extraer_hallazgos(self, denominacion: Dict, tendencias: Dict, 
                          instituciones: Dict) -> List[str]:
        """Extrae hallazgos de TODOS los agentes"""
        hallazgos = []
        
        # Denominación
        den_hallazgos = denominacion.get('analisis_ia', {}).get('hallazgos', [])
        if isinstance(den_hallazgos, list):
            hallazgos.extend(den_hallazgos[:2])
        
        # Tendencias
        ten_emergentes = tendencias.get('palabras_emergentes', [])
        if ten_emergentes:
            hallazgos.append(f"Tendencias emergentes: {', '.join(ten_emergentes[:3])}")
        
        # Instituciones
        hubs = instituciones.get('hub_geograficos', {})
        if hubs.get('hubs_principales'):
            top_hub = hubs['hubs_principales'][0]
            hallazgos.append(f"Hub geográfico principal: {top_hub.get('departamento')} "
                           f"({top_hub.get('porcentaje')}% de la oferta)")
        
        cantidad_var = denominacion.get('cantidad_variaciones', 0)
        hallazgos.append(f"Se encontraron {cantidad_var} variaciones del programa")
        
        seg = instituciones.get('segmentacion_institucional', {})
        if seg.get('acreditadas_vs_no_acreditadas'):
            acred = seg['acreditadas_vs_no_acreditadas']['acreditadas']['porcentaje']
            hallazgos.append(f"{acred}% de instituciones oferentes están acreditadas")
        
        return hallazgos
    
    def _generar_recomendaciones(self, denominacion: Dict, tendencias: Dict, 
                                instituciones: Dict) -> List[str]:
        """Genera recomendaciones integradas de todos los agentes"""
        recomendaciones = []
        
        clasificacion = denominacion.get('analisis_ia', {}).get('clasificacion', '')
        if clasificacion:
            recomendaciones.append(f"Clasificar programa como: {clasificacion}")
        
        palabras_emergentes = tendencias.get('palabras_emergentes', [])
        if palabras_emergentes:
            recomendaciones.append(f"Alinear curricula con tendencias emergentes: "
                                 f"{', '.join(palabras_emergentes[:2])}")
        
        recomendaciones.append("Actualizar denominación en sistemas académicos")
        recomendaciones.append("Revisar equivalencias internacionales")
        
        return recomendaciones
    
    def _generar_oportunidades_expansion(self, instituciones: Dict) -> List[Dict]:
        """Genera oportunidades de expansión geográfica"""
        oportunidades = instituciones.get('oportunidades_por_ubicacion', {})
        gaps = instituciones.get('gaps_geograficos', {})
        
        resultado = []
        
        # Departamentos con baja cobertura = oportunidades
        for dept_info in oportunidades.get('departamentos_con_baja_cobertura', [])[:5]:
            resultado.append({
                'tipo': 'Expansión',
                'departamento': dept_info.get('departamento'),
                'potencial': dept_info.get('potencial'),
                'programas_actuales': dept_info.get('programas')
            })
        
        return resultado
    
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