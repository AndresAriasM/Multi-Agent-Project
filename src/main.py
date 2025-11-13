"""
Script principal que ejecuta el análisis completo
Ubicación: src/main.py
VERSIÓN CORREGIDA - Con generación de datos enriquecidos
"""

import sys
import argparse
from pathlib import Path
import os
import numpy as np

# Asegurar que PYTHONPATH incluye el directorio actual
sys.path.insert(0, os.path.dirname(__file__))

from lector_tablas_snies import LectorSNIES
from lector_datos_enriquecidos import LectorDatosEnriquecidos
from agentes.coordinador import CoordinadorAgentes
from presentacion.generador_powerpoint import GeneradorPowerPoint
from config import OUTPUT_DIR, validar_config


def _buscar_programa_mejorado(lector, programa_buscar: str) -> dict:
    """
    Busca programas usando similitud Jaccard y enriquece con datos SNIES
    VERSIÓN CORREGIDA - Maneja numpy arrays correctamente
    """
    import pandas as pd

    print(f"\n🔍 Búsqueda mejorada de: '{programa_buscar}'")

    # PASO 0: Obtener datos del lector
    programas_list = None

    # Acceder a los datos YA CARGADOS en el lector
    if hasattr(lector, 'datos') and 'programas' in lector.datos:
        p = lector.datos['programas']
        if isinstance(p, pd.DataFrame):
            programas_list = p['PROGRAMA_ACADEMICO'].unique().tolist()

    if programas_list is None or len(programas_list) == 0:
        print("⚠️  No se encontraron programas en el lector")
        return lector.buscar_programa(programa_buscar)

    print(f"📌 Programas disponibles: {len(programas_list)}")

    # PASO 1: Preparar palabras de búsqueda
    palabras_comunes = {'de', 'la', 'el', 'y', 'en', 'a', 'o', 'los', 'las', 'un', 'una', 'del', 'con'}
    programa_palabras = set(p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes)

    # Palabras OBLIGATORIAS
    palabras_ordenadas = [p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes]
    requerido = set(palabras_ordenadas[:2]) if len(palabras_ordenadas) >= 2 else set(palabras_ordenadas)

    print(f"📌 Palabras búsqueda: {programa_palabras}")
    print(f"📌 Palabras obligatorias: {requerido}")

    n = len(programa_palabras) if len(programa_palabras) > 0 else 1
    umbral_jaccard = (n - 1) / n if n > 1 else 1.0

    # PASO 2: Filtrar programas
    coincidencias = []

    for prg in programas_list:
        prg_palabras = set(p.lower() for p in str(prg).split() if p.lower() not in palabras_comunes)

        if len(programa_palabras) > 0:
            interseccion = len(programa_palabras.intersection(prg_palabras))
            jaccard = interseccion / len(programa_palabras)
        else:
            jaccard = 1.0

        tiene_requeridas = requerido.issubset(prg_palabras)

        if jaccard >= umbral_jaccard and tiene_requeridas:
            coincidencias.append(prg)

    coincidencias = sorted(list(set(coincidencias)))

    print(f"✅ Encontrados {len(coincidencias)} programas equivalentes")
    for i, prog in enumerate(coincidencias[:15], 1):
        print(f"   {i}. {prog}")
    if len(coincidencias) > 15:
        print(f"   ... y {len(coincidencias) - 15} más")

    # PASO 3: Enriquecer datos CON LOS PROGRAMAS ENCONTRADOS
    print("\n📊 Enriqueciendo datos...")

    programas_df = lector.datos.get('programas', pd.DataFrame())
    maestro_df = lector.datos.get('maestro', pd.DataFrame())
    oferta_df = lector.datos.get('oferta', pd.DataFrame())

    # FILTRAR por los coincidencias REALES encontradas
    programas_filtrados = programas_df[programas_df['PROGRAMA_ACADEMICO'].isin(coincidencias)]
    snies_codes = programas_filtrados['CODIGO_SNIES'].unique()

    maestro_filtrado = maestro_df[maestro_df['CODIGO_SNIES'].isin(snies_codes)]
    maestro_merged = maestro_filtrado.merge(programas_filtrados, on='CODIGO_SNIES', how='left')

    if not oferta_df.empty:
        maestro_merged = maestro_merged.merge(oferta_df, on=['CODIGO_SNIES', 'PERIODO'], how='left')

    datos = {
        'nombre': programa_buscar,
        'maestro': maestro_merged,
        'maestro_enriquecido': maestro_merged,
        'programas': programas_filtrados,
        'equivalentes': coincidencias,
        'snies_codes': list(snies_codes),  # ✅ CONVERTIR A LISTA
        'palabras_clave': programa_palabras,
        'estadisticas': {
            'total_programas_equivalentes': len(coincidencias),
            'total_registros_snies': len(maestro_merged),
            'instituciones_unicas': maestro_merged['CODIGO_INSTITUCION_x'].nunique() if 'CODIGO_INSTITUCION_x' in maestro_merged.columns else 0,
            'departamentos_unicos': maestro_merged['DEPARTAMENTO_PROGRAMA'].nunique() if 'DEPARTAMENTO_PROGRAMA' in maestro_merged.columns else 0,
        },
        'datos_enriquecidos': {}  # ✅ INICIALIZAR PARA GENERAR
    }

    print(f"📊 Datos básicos:")
    print(f"   - Programas equivalentes: {len(coincidencias)}")
    print(f"   - Registros SNIES: {datos['estadisticas']['total_registros_snies']}")
    print(f"   - Instituciones: {datos['estadisticas']['instituciones_unicas']}")
    print(f"   - Departamentos: {datos['estadisticas']['departamentos_unicos']}")

    # ============ ✅ GENERAR DATOS ENRIQUECIDOS ============
    print("\n📊 Generando datos enriquecidos...")

    try:
        # ✅ CONVERTIR snies_codes a lista si es numpy array
        snies_codes_lista = list(snies_codes) if isinstance(snies_codes, np.ndarray) else snies_codes
        
        if len(snies_codes_lista) == 0:
            print("⚠️  No hay códigos SNIES para enriquecer")
            return datos

        # ✅ Obtener DataFrames originales para enriquecimiento
        ies_df = lector.datos.get('ies', pd.DataFrame())

        lector_enriquecido = LectorDatosEnriquecidos(
            maestro_df,
            oferta_df,
            programas_df,
            ies_df,
            verbose=True
        )

        # ✅ Llamar con listas, no numpy arrays
        datos_enriquecidos = lector_enriquecido.extraer_datos_enriquecidos(
            snies_codes=snies_codes_lista,
            denominaciones=coincidencias
        )

        datos['datos_enriquecidos'] = datos_enriquecidos

        print(f"✅ Datos enriquecidos generados correctamente\n")

    except Exception as e:
        print(f"⚠️  Error generando datos enriquecidos: {e}")
        import traceback
        traceback.print_exc()
        # Continuar sin datos enriquecidos
        datos['datos_enriquecidos'] = {}

    return datos


def main():
    parser = argparse.ArgumentParser(
        description="Análisis de Oportunidad SNIES con Sistema Multi-Agente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --programa "DOCTORADO CIENCIAS SOCIALES"
  python main.py --programa "MAESTRÍA ADMINISTRACIÓN" --output analisis_maestria.pptx
        """
    )

    parser.add_argument(
        "--programa",
        type=str,
        default="DOCTORADO CIENCIAS SOCIALES",
        help="Nombre del programa a analizar"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reporte_analisis_oportunidad.pptx",
        help="Archivo de salida PowerPoint"
    )
    parser.add_argument(
        "--generar-graficas",
        action="store_true",
        default=True,
        help="Generar gráficas SNIES"
    )
    parser.add_argument(
        "--sin-agentes",
        action="store_true",
        help="Ejecutar sin sistema de agentes (solo SNIES)"
    )

    args = parser.parse_args()

    try:
        # Validar configuración
        print("🔧 Validando configuración...")
        validar_config()
        print("✅ Configuración válida\n")

    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        print("   Asegúrate de tener un archivo .env con las credenciales de Azure OpenAI")
        sys.exit(1)

    try:
        # PASO 1: Cargar y procesar datos SNIES
        print("="*60)
        print("PASO 1: CARGANDO DATOS SNIES")
        print("="*60)
        print(f"📚 Analizando programa: {args.programa}\n")

        lector = LectorSNIES([args.programa], verbose=True)
        lector.cargar_datos()

        # Búsqueda mejorada con fuzzy matching
        datos = _buscar_programa_mejorado(lector, args.programa)

        # Generar gráficas
        if args.generar_graficas:
            print("\n📊 Generando gráficas SNIES...")
            try:
                lector.generar_graficas(args.programa, OUTPUT_DIR)
            except Exception as e:
                print(f"⚠️  Error generando gráficas: {e}")

        print("\n✅ Datos SNIES procesados\n")

        # PASO 2: Ejecutar sistema multi-agente
        if not args.sin_agentes:
            print("="*60)
            print("PASO 2: EJECUTANDO SISTEMA MULTI-AGENTE")
            print("="*60)

            coordinador = CoordinadorAgentes(datos)
            resultados_agentes = coordinador.ejecutar()

            # Guardar resultados de agentes
            resultados_json = f"{OUTPUT_DIR}/resultados_agentes.json"
            coordinador.guardar_resultados(resultados_json)

            print("\n✅ Análisis de agentes completado\n")
        else:
            print("⏭️  Saltando sistema de agentes\n")
            resultados_agentes = {
                'programa': args.programa,
                'sintesis': {'hallazgos_principales': [], 'recomendaciones': []},
                'denominacion': {'analisis_ia': {}},
                'tendencias': {'palabras_emergentes': []},
                'instituciones_geografia': {}
            }

        # PASO 3: Generar presentación
        print("="*60)
        print("PASO 3: GENERANDO PRESENTACIÓN POWERPOINT")
        print("="*60 + "\n")

        output_path = f"{OUTPUT_DIR}/{args.output}"
        generador = GeneradorPowerPoint(datos, resultados_agentes, OUTPUT_DIR)
        generador.crear_presentacion(output_path)

        print("\n" + "="*60)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"\n📊 Archivos generados en: {OUTPUT_DIR}/")
        print(f"  - {args.output} (Presentación principal)")
        if args.generar_graficas:
            print(f"  - Gráficas SNIES")
        if not args.sin_agentes:
            print(f"  - resultados_agentes.json (Datos de análisis)")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())