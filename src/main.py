"""
Script principal que ejecuta el análisis completo
Ubicación: src/main.py
"""

import sys
import argparse
from pathlib import Path
import os

# Asegurar que PYTHONPATH incluye el directorio actual
sys.path.insert(0, os.path.dirname(__file__))

from lector_tablas_snies import LectorSNIES
from agentes.coordinador import CoordinadorAgentes
from presentacion.generador_powerpoint import GeneradorPowerPoint
from config import OUTPUT_DIR, validar_config


def _buscar_programa_mejorado(lector, programa_buscar: str) -> dict:
    """
    Busca programas usando similitud Jaccard y enriquece con datos SNIES
    
    Lógica:
    1. Calcula similitud Jaccard entre palabras
    2. Valida palabras clave obligatorias
    3. Enriquece con datos del SNIES
    """
    import pandas as pd
    
    print(f"\n🔍 Búsqueda mejorada de: '{programa_buscar}'")
    
    # PASO 0: Obtener datos disponibles del lector
    programas_list = None
    maestro_df = None
    oferta_df = None
    
    # Intentar obtener programas
    if hasattr(lector, 'programas'):
        p = lector.programas
        if isinstance(p, list):
            programas_list = p
        elif isinstance(p, pd.DataFrame):
            programas_list = p['PROGRAMA_ACADEMICO'].unique().tolist() if 'PROGRAMA_ACADEMICO' in p.columns else p.values.tolist()
    
    if programas_list is None or len(programas_list) == 0:
        print("⚠️  No se encontraron programas en el lector")
        return lector.buscar_programa(programa_buscar)
    
    print(f"📌 Programas disponibles: {len(programas_list)}")
    
    # PASO 1: Preparar palabras de búsqueda
    palabras_comunes = {'de', 'la', 'el', 'y', 'en', 'a', 'o', 'los', 'las', 'un', 'una'}
    programa_palabras = set(p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes)
    
    # Palabras OBLIGATORIAS (primeras 2 palabras significativas)
    palabras_ordenadas = [p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes]
    requerido = set(palabras_ordenadas[:2]) if len(palabras_ordenadas) >= 2 else set(palabras_ordenadas)
    
    print(f"📌 Palabras búsqueda: {programa_palabras}")
    print(f"📌 Palabras obligatorias: {requerido}")
    
    n = len(programa_palabras) if len(programa_palabras) > 0 else 1
    umbral_jaccard = (n - 1) / n if n > 1 else 1.0
    
    # PASO 2: Filtrar programas usando Jaccard + palabras clave
    coincidencias = []
    
    for prg in programas_list:
        # Convertir a palabras
        prg_palabras = set(p.lower() for p in str(prg).split() if p.lower() not in palabras_comunes)
        
        # Calcular similitud Jaccard
        if len(programa_palabras) > 0:
            interseccion = len(programa_palabras.intersection(prg_palabras))
            jaccard = interseccion / len(programa_palabras)
        else:
            jaccard = 1.0
        
        # Validar: Jaccard >= umbral AND todas las palabras requeridas presentes
        tiene_requeridas = requerido.issubset(prg_palabras)
        
        if jaccard >= umbral_jaccard and tiene_requeridas:
            coincidencias.append(prg)
    
    coincidencias = sorted(list(set(coincidencias)))
    
    print(f"✅ Encontrados {len(coincidencias)} programas equivalentes")
    for i, prog in enumerate(coincidencias[:15], 1):
        print(f"   {i}. {prog}")
    if len(coincidencias) > 15:
        print(f"   ... y {len(coincidencias) - 15} más")
    
    # PASO 3: Enriquecer datos llamando al lector original
    print("\n📊 Enriqueciendo datos...")
    datos = lector.buscar_programa(programa_buscar)
    
    # Guardar datos enriquecidos
    datos['equivalentes'] = coincidencias if coincidencias else [programa_buscar]
    
    # Calcular estadísticas básicas
    if 'maestro' in datos and isinstance(datos['maestro'], pd.DataFrame) and not datos['maestro'].empty:
        maestro_df = datos['maestro']
        datos['estadisticas'] = {
            'total_programas_equivalentes': len(coincidencias),
            'total_registros_snies': len(maestro_df),
            'instituciones_unicas': maestro_df['CODIGO_INSTITUCION_x'].nunique() if 'CODIGO_INSTITUCION_x' in maestro_df.columns else 0,
            'departamentos_unicos': maestro_df['DEPARTAMENTO_PROGRAMA'].nunique() if 'DEPARTAMENTO_PROGRAMA' in maestro_df.columns else 0,
        }
    else:
        datos['estadisticas'] = {
            'total_programas_equivalentes': len(coincidencias),
            'total_registros_snies': 0,
            'instituciones_unicas': 0,
            'departamentos_unicos': 0,
        }
    
    print(f"📊 Datos enriquecidos:")
    print(f"   - Programas equivalentes: {len(coincidencias)}")
    print(f"   - Registros SNIES: {datos['estadisticas']['total_registros_snies']}")
    print(f"   - Instituciones: {datos['estadisticas']['instituciones_unicas']}")
    print(f"   - Departamentos: {datos['estadisticas']['departamentos_unicos']}")
    
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
                'tendencias': {'palabras_emergentes': []}
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