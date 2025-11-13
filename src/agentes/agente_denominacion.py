"""
Agente que analiza denominación de programas académicos CON CONTEXTO ENRIQUECIDO
Ubicación: src/agentes/agente_denominacion.py
REEMPLAZA completamente el archivo anterior
"""

from typing import Dict, List
import json
from .llm_handler import LLMHandler


class AgenteDenominacion:
    """Analiza nombres y denominaciones de programas con contexto del mercado"""
    
    def __init__(self, datos: Dict):
        self.datos = datos
        self.programas = datos.get('equivalentes', [])
        self.datos_enriquecidos = datos.get('datos_enriquecidos', {})
        try:
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None
    
    def analizar(self) -> Dict:
        """Realiza análisis de denominación con contexto enriquecido"""
        print("🔍 Analizando denominación de programas...")
        
        denominaciones_unicas = list(set(self.programas))
        
        # Obtener contexto enriquecido si está disponible
        contexto_mercado = self.datos_enriquecidos.get('contexto_mercado', {})
        instituciones = self.datos_enriquecidos.get('instituciones', {})
        modalidades = self.datos_enriquecidos.get('modalidades', {})
        duracion = self.datos_enriquecidos.get('duracion', {})
        matriculas = self.datos_enriquecidos.get('matriculas', {})
        
        if not self.llm:
            print("⚠️  LLMHandler no disponible, usando análisis básico")
            return self._analisis_basico()
        
        try:
            # Llamar a Azure OpenAI CON CONTEXTO ENRIQUECIDO
            respuesta_ia = self.llm.analizar_denominacion_con_contexto(
                denominaciones_unicas,
                self.datos.get('nombre', 'Programa Académico'),
                contexto_mercado,
                instituciones,
                modalidades,
                duracion,
                matriculas
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
            'estadisticas': self._calcular_estadisticas(),
            'contexto_mercado_resumido': {
                'competencia': contexto_mercado.get('competencia', {}),
                'acreditacion': contexto_mercado.get('acreditacion', {}),
                'demanda': contexto_mercado.get('demanda', {}),
                'sector': contexto_mercado.get('sector', {}),
            }
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
            'hallazgos': ['Análisis básico sin contexto de IA'],
            'contexto_del_mercado': self._generar_contexto_basico()
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
    
    def _generar_contexto_basico(self) -> Dict:
        """Genera contexto básico sin IA"""
        contexto_mercado = self.datos_enriquecidos.get('contexto_mercado', {})
        
        return {
            'competencia_total': contexto_mercado.get('competencia', {}).get('total_instituciones', 'N/A'),
            'tipo_institucion_dominante': 'Universidades' if contexto_mercado.get('competencia', {}).get('universidades', 0) > 5 else 'Variado',
            'sector_dominante': 'Privado' if contexto_mercado.get('sector', {}).get('porcentaje_privado', 0) > 50 else 'Oficial',
            'nivel_demanda': contexto_mercado.get('demanda', {}).get('nivel_demanda', 'Desconocido'),
            'mercado_homogeneo': contexto_mercado.get('precios', {}).get('mercado_homogeneo', False),
        }