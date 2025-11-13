"""
Agente de Análisis Institucional y Segmentación Geográfica - VERSIÓN CORREGIDA
Ubicación: src/agentes/agente_instituciones_geografia.py
CAMBIOS: Validación de datos enriquecidos y manejo de casos vacíos
"""

from typing import Dict, List
import json
import pandas as pd
from collections import Counter


class AgenteInstitucionesGeografia:
    """Analiza instituciones y segmentación geográfica con insights valiosos"""

    def __init__(self, datos: Dict):
        self.datos = datos
        self.datos_enriquecidos = datos.get('datos_enriquecidos', {})
        self.maestro = datos.get('maestro', pd.DataFrame())

        try:
            from .llm_handler import LLMHandler
            self.llm = LLMHandler()
        except Exception as e:
            print(f"⚠️  Error inicializando LLMHandler: {e}")
            self.llm = None

    def analizar(self) -> Dict:
        """Realiza análisis institucional y geográfico completo"""
        print("🏫 Analizando instituciones y geografía...")

        # ✅ VALIDAR que hay datos enriquecidos
        if not self.datos_enriquecidos:
            print("⚠️  Sin datos enriquecidos - retornando análisis vacío")
            return self._retornar_analisis_vacio()

        resultados = {
            'segmentacion_institucional': self._analizar_segmentacion_institucional(),
            'hub_geograficos': self._identificar_hub_geograficos(),
            'oportunidades_por_ubicacion': self._oportunidades_ubicacion(),
            'competencia_regional': self._analizar_competencia_regional(),
            'institucion_referente': self._identificar_institucion_referente(),
            'gaps_geograficos': self._identificar_gaps_geograficos(),
            'analisis_ia': self._generar_analisis_ia(),
            'recomendaciones_institucion': self._generar_recomendaciones_institucion(),
        }

        return resultados

    def _retornar_analisis_vacio(self) -> Dict:
        """Retorna estructura vacía pero válida"""
        return {
            'segmentacion_institucional': {
                'por_tipo': {'distribucion': {}, 'detalles_por_tipo': {}},
                'por_sector': {'distribucion': {}, 'detalles_por_sector': {}},
                'acreditadas_vs_no_acreditadas': {'acreditadas': {'lista': []}, 'no_acreditadas': {'lista': []}},
                'por_departamento': {'distribucion': {}, 'detalles': {}},
            },
            'hub_geograficos': {'hubs_principales': [], 'hubs_secundarios': []},
            'oportunidades_por_ubicacion': {'departamentos_con_alta_demanda': [], 'departamentos_con_baja_cobertura': []},
            'competencia_regional': {'detalles_por_departamento': {}, 'regiones_mas_competitivas': []},
            'institucion_referente': {'institucion_referente_top1': None, 'institucion_referente_top3': []},
            'gaps_geograficos': {'departamentos_sin_cobertura': [], 'cantidad_gaps': 0},
            'analisis_ia': {'analisis': 'Datos insuficientes', 'insights_clave': []},
            'recomendaciones_institucion': []
        }

    # ========== SEGMENTACIÓN INSTITUCIONAL ==========

    def _analizar_segmentacion_institucional(self) -> Dict:
        """Segmenta instituciones por tipo, sector y características"""
        instituciones = self.datos_enriquecidos.get('instituciones', {})
        inst_lista = instituciones.get('lista', [])

        # ✅ VALIDAR que hay instituciones
        if not inst_lista:
            print("⚠️  Sin instituciones en datos enriquecidos")
            return {
                'por_tipo': {'distribucion': {}, 'detalles_por_tipo': {}, 'total_tipos': 0},
                'por_sector': {'distribucion': {}, 'detalles_por_sector': {}, 'porcentajes': {}},
                'acreditadas_vs_no_acreditadas': {'acreditadas': {'lista': []}, 'no_acreditadas': {'lista': []}},
                'por_departamento': {'distribucion': {}, 'detalles': {}},
            }

        segmentacion = {
            'por_tipo': self._segmentar_por_tipo(inst_lista),
            'por_sector': self._segmentar_por_sector(inst_lista),
            'acreditadas_vs_no_acreditadas': self._segmentar_por_acreditacion(inst_lista),
            'por_departamento': self._segmentar_por_departamento(inst_lista),
            'distribucion_geografica': self._distribucion_geografica_instituciones(inst_lista),
        }

        return segmentacion

    def _segmentar_por_tipo(self, instituciones: List[Dict]) -> Dict:
        """Segmenta instituciones por tipo"""
        tipos = {}
        para_cada_tipo = {}

        for inst in instituciones:
            tipo = inst.get('tipo', 'Otros')
            if tipo not in tipos:
                tipos[tipo] = 0
                para_cada_tipo[tipo] = []
            tipos[tipo] += 1
            para_cada_tipo[tipo].append({
                'nombre': inst.get('nombre'),
                'municipio': inst.get('municipio'),
            })

        return {
            'distribucion': tipos,
            'total_tipos': len(tipos),
            'detalles_por_tipo': para_cada_tipo,
            'tipo_dominante': max(tipos.items(), key=lambda x: x[1])[0] if tipos else 'N/A',
        }

    def _segmentar_por_sector(self, instituciones: List[Dict]) -> Dict:
        """Segmenta por sector"""
        sectores = {}
        para_cada_sector = {}

        for inst in instituciones:
            sector = inst.get('sector', 'Desconocido')
            if sector not in sectores:
                sectores[sector] = 0
                para_cada_sector[sector] = []
            sectores[sector] += 1
            para_cada_sector[sector].append(inst.get('nombre'))

        total = sum(sectores.values())
        porcentajes = {s: round(c / total * 100, 2) for s, c in sectores.items()} if total > 0 else {}

        return {
            'distribucion': sectores,
            'porcentajes': porcentajes,
            'sector_dominante': max(sectores.items(), key=lambda x: x[1])[0] if sectores else 'N/A',
            'detalle_por_sector': para_cada_sector,
        }

    def _segmentar_por_acreditacion(self, instituciones: List[Dict]) -> Dict:
        """Segmenta acreditadas vs no acreditadas"""
        acreditadas = [i for i in instituciones if i.get('acreditacion_alta_calidad') == 'Si']
        no_acreditadas = [i for i in instituciones if i.get('acreditacion_alta_calidad') != 'Si']

        total = len(instituciones)

        return {
            'acreditadas': {
                'cantidad': len(acreditadas),
                'porcentaje': round(len(acreditadas) / total * 100, 2) if total > 0 else 0,
                'lista': [i.get('nombre') for i in acreditadas][:10]
            },
            'no_acreditadas': {
                'cantidad': len(no_acreditadas),
                'porcentaje': round(len(no_acreditadas) / total * 100, 2) if total > 0 else 0,
                'lista': [i.get('nombre') for i in no_acreditadas][:10]
            },
        }

    def _segmentar_por_departamento(self, instituciones: List[Dict]) -> Dict:
        """Segmenta por departamento"""
        departamentos = {}

        for inst in instituciones:
            dept = inst.get('departamento', 'Desconocido')
            if dept not in departamentos:
                departamentos[dept] = {'cantidad': 0, 'instituciones': []}
            departamentos[dept]['cantidad'] += 1
            departamentos[dept]['instituciones'].append(inst.get('nombre'))

        return {
            'total_departamentos': len(departamentos),
            'distribucion': {d: v['cantidad'] for d, v in departamentos.items()},
            'departamento_con_mas_oferta': max(departamentos.items(), 
                                               key=lambda x: x[1]['cantidad'])[0] if departamentos else 'N/A',
            'detalles': departamentos,
        }

    def _distribucion_geografica_instituciones(self, instituciones: List[Dict]) -> Dict:
        """Análisis de distribución geográfica"""
        municipios = {}

        for inst in instituciones:
            mpio = inst.get('municipio', 'Desconocido')
            municipios[mpio] = municipios.get(mpio, 0) + 1

        top_municipios = sorted(municipios.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'total_municipios': len(municipios),
            'top_10_municipios': dict(top_municipios),
            'concentracion_geogratica': round(sum(dict(top_municipios).values()) / len(instituciones) * 100, 2) if instituciones else 0
        }

    # ========== HUBS GEOGRÁFICOS ==========

    def _identificar_hub_geograficos(self) -> Dict:
        """Identifica zonas geográficas con alta concentración"""
        cobertura = self.datos_enriquecidos.get('cobertura_geografica', {})
        departamentos = cobertura.get('departamentos', {})

        # ✅ VALIDAR que hay departamentos
        if not departamentos:
            print("⚠️  Sin cobertura geográfica en datos enriquecidos")
            return {
                'hubs_principales': [],
                'hubs_secundarios': [],
                'concentracion_top_3_departamentos': 0.0,
                'total_departamentos': 0,
                'dispersion_geografica': 'Sin datos'
            }

        total = sum(departamentos.values()) if departamentos else 1

        hubs_principales = []
        hubs_secundarios = []

        for dept, cantidad in sorted(departamentos.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (cantidad / total * 100) if total > 0 else 0

            hub_info = {
                'departamento': dept,
                'cantidad_programas': cantidad,
                'porcentaje': round(porcentaje, 2),
                'nivel': 'Alto' if porcentaje >= 20 else 'Medio' if porcentaje >= 10 else 'Bajo'
            }

            if porcentaje >= 20:
                hubs_principales.append(hub_info)
            elif porcentaje >= 10:
                hubs_secundarios.append(hub_info)

        concentracion_top_3 = sum([h['cantidad_programas'] for h in (hubs_principales + hubs_secundarios)[:3]]) / total * 100 if total > 0 else 0

        return {
            'hubs_principales': hubs_principales,
            'hubs_secundarios': hubs_secundarios,
            'concentracion_top_3_departamentos': round(concentracion_top_3, 2),
            'total_departamentos': len(departamentos),
            'dispersion_geografica': 'Baja' if concentracion_top_3 > 60 else 'Media' if concentracion_top_3 > 40 else 'Alta',
        }

    # ========== OPORTUNIDADES POR UBICACIÓN ==========

    def _oportunidades_ubicacion(self) -> Dict:
        """Identifica oportunidades según ubicación"""
        cobertura = self.datos_enriquecidos.get('cobertura_geografica', {})
        departamentos = cobertura.get('departamentos', {})

        if not departamentos:
            return {
                'departamentos_con_alta_demanda': [],
                'departamentos_con_baja_cobertura': [],
            }

        oportunidades = {
            'departamentos_con_alta_demanda': [],
            'departamentos_con_baja_cobertura': [],
        }

        total_programas = sum(departamentos.values())
        promedio = total_programas / len(departamentos) if departamentos else 0

        for dept, cantidad in departamentos.items():
            if cantidad > promedio * 1.5:
                oportunidades['departamentos_con_alta_demanda'].append({
                    'departamento': dept,
                    'programas': cantidad,
                    'potencial': 'Alto - demanda comprobada'
                })
            elif cantidad < promedio * 0.5:
                oportunidades['departamentos_con_baja_cobertura'].append({
                    'departamento': dept,
                    'programas': cantidad,
                    'potencial': 'Oportunidad de expansión'
                })

        return oportunidades

    # ========== COMPETENCIA REGIONAL ==========

    def _analizar_competencia_regional(self) -> Dict:
        """Analiza competencia por región"""
        instituciones = self.datos_enriquecidos.get('instituciones', {})
        inst_lista = instituciones.get('lista', [])

        if not inst_lista:
            return {
                'detalles_por_departamento': {},
                'regiones_mas_competitivas': []
            }

        competencia_por_depto = {}

        for inst in inst_lista:
            depto = inst.get('departamento', 'Desconocido')
            if depto not in competencia_por_depto:
                competencia_por_depto[depto] = {
                    'total': 0,
                    'universidades': 0,
                    'tecnologicas': 0,
                    'acreditadas': 0,
                }

            competencia_por_depto[depto]['total'] += 1

            if inst.get('tipo') == 'Universidad':
                competencia_por_depto[depto]['universidades'] += 1
            elif inst.get('tipo') == 'Tecnologica':
                competencia_por_depto[depto]['tecnologicas'] += 1

            if inst.get('acreditacion_alta_calidad') == 'Si':
                competencia_por_depto[depto]['acreditadas'] += 1

        return {
            'detalles_por_departamento': competencia_por_depto,
            'regiones_mas_competitivas': sorted(
                competencia_por_depto.items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )[:5]
        }

    # ========== INSTITUCIÓN REFERENTE ==========

    def _identificar_institucion_referente(self) -> Dict:
        """Identifica la institución referente"""
        instituciones = self.datos_enriquecidos.get('instituciones', {})
        inst_lista = instituciones.get('lista', [])

        if not inst_lista:
            return {
                'institucion_referente_top1': None,
                'institucion_referente_top3': [],
            }

        mejores = []

        for inst in inst_lista:
            score = 0

            if inst.get('acreditacion_alta_calidad') == 'Si':
                score += 3

            if inst.get('tipo') == 'Universidad':
                score += 2
            elif inst.get('tipo') == 'Tecnologica':
                score += 1

            mejores.append({
                'nombre': inst.get('nombre'),
                'tipo': inst.get('tipo'),
                'sector': inst.get('sector'),
                'acreditada': inst.get('acreditacion_alta_calidad') == 'Si',
                'municipio': inst.get('municipio'),
                'departamento': inst.get('departamento'),
                'score': score
            })

        mejores.sort(key=lambda x: x['score'], reverse=True)

        return {
            'institucion_referente_top1': mejores[0] if mejores else None,
            'institucion_referente_top3': mejores[:3] if mejores else [],
        }

    # ========== GAPS GEOGRÁFICOS ==========

    def _identificar_gaps_geograficos(self) -> Dict:
        """Identifica regiones sin cobertura"""
        cobertura = self.datos_enriquecidos.get('cobertura_geografica', {})
        departamentos = cobertura.get('departamentos', {})

        # ✅ VALIDAR que hay datos
        if not departamentos:
            return {
                'departamentos_sin_cobertura': [],
                'cantidad_gaps': 0,
                'oportunidad_expansion': 'Sin datos de cobertura'
            }

        depts_principales = [
            'Bogotá D.C.', 'Antioquia', 'Valle del Cauca', 'Cundinamarca',
            'Atlántico', 'Santander', 'Meta', 'Nariño', 'Cauca', 'Córdoba',
            'Bolívar', 'Magdalena', 'Cesar', 'Sucre', 'Huila', 'Tolima',
            'Putumayo', 'Caquetá', 'Guaviare', 'Chocó', 'Guainía', 'Vichada',
            'Amazonas', 'Arauca', 'Casanare', 'Quindío', 'Risaralda',
            'Caldas', 'La Guajira', 'Boyacá'
        ]

        gaps = [dept for dept in depts_principales if dept not in departamentos or departamentos[dept] == 0]

        return {
            'departamentos_sin_cobertura': gaps,
            'cantidad_gaps': len(gaps),
            'oportunidad_expansion': f"{len(gaps)} departamentos sin oferta" if gaps else "Buena cobertura nacional"
        }

    # ========== ANÁLISIS CON IA ==========

    def _generar_analisis_ia(self) -> Dict:
        """Genera análisis enriquecido con IA"""
        if not self.llm or not self.datos_enriquecidos:
            return self._analisis_basico_ia()

        try:
            segmentacion = self._analizar_segmentacion_institucional()
            hubs = self._identificar_hub_geograficos()

            prompt = f"""
Analiza esta información sobre distribución institucional:

SEGMENTACIÓN:
- Tipos: {json.dumps(segmentacion['por_tipo']['distribucion'])}
- Sector: {json.dumps(segmentacion['por_sector']['distribucion'])}

HUBS: {json.dumps(hubs)}

Proporciona análisis en máximo 100 palabras."""

            respuesta = self.llm.call(
                "Eres experto en educación superior.",
                prompt,
                max_tokens=500
            )

            return {
                'analisis': respuesta,
                'insights_clave': self._extraer_insights_ia(respuesta)
            }

        except Exception as e:
            print(f"⚠️  Error en IA: {e}")
            return self._analisis_basico_ia()

    def _analisis_basico_ia(self) -> Dict:
        """Análisis básico sin IA"""
        return {
            'analisis': 'Análisis basado en datos estadísticos',
            'insights_clave': []
        }

    def _extraer_insights_ia(self, texto: str) -> List[str]:
        """Extrae insights del texto"""
        return [linea.strip() for linea in texto.split('\n') if linea.strip()][:5]

    # ========== RECOMENDACIONES ==========

    def _generar_recomendaciones_institucion(self) -> List[str]:
        """Genera recomendaciones prácticas"""
        segmentacion = self._analizar_segmentacion_institucional()
        gaps = self._identificar_gaps_geograficos()

        recomendaciones = []

        acred = segmentacion.get('acreditadas_vs_no_acreditadas', {})
        if acred and acred.get('acreditadas', {}).get('porcentaje', 0) < 50:
            recomendaciones.append(
                f"Solo {acred.get('acreditadas', {}).get('porcentaje', 0)}% acreditadas. Priorizar con acreditadas."
            )

        if gaps.get('cantidad_gaps', 0) > 10:
            recomendaciones.append(
                f"{gaps.get('cantidad_gaps', 0)} departamentos sin cobertura. Oportunidad de expansión."
            )

        if not recomendaciones:
            recomendaciones.append("Consolidar presencia en mercado actual")

        return recomendaciones