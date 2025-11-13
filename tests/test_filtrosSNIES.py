#!/usr/bin/env python3
"""
Script completo para extraer TODOS los datos disponibles de un programa SNIES
Incluye: universidades, duración, modalidades, acreditación, matrículas, evolución, etc.
"""

import pandas as pd
import json
from collections import Counter
from datetime import datetime

def buscar_y_extraer_programa(programa_buscar: str):
    """Busca un programa y extrae TODOS los datos disponibles"""
    
    print("\n" + "="*80)
    print(f"🔍 EXTRAYENDO DATOS COMPLETOS: '{programa_buscar}'")
    print("="*80)
    
    # PASO 1: Cargar datos
    print("\n1️⃣  CARGANDO DATOS...")
    try:
        maestro = pd.read_parquet('https://robertohincapie.com/data/snies/MAESTRO.parquet')
        oferta = pd.read_parquet('https://robertohincapie.com/data/snies/OFERTA.parquet')
        programas = pd.read_parquet('https://robertohincapie.com/data/snies/PROGRAMAS.parquet')
        ies = pd.read_parquet('https://robertohincapie.com/data/snies/IES.parquet')
        print("   ✅ Datos cargados")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None
    
    # PASO 2: Buscar programas equivalentes
    print("\n2️⃣  BUSCANDO PROGRAMAS EQUIVALENTES...")
    palabras_comunes = {'de', 'la', 'el', 'y', 'en', 'a', 'o', 'los', 'las', 'un', 'una', 'del', 'con'}
    programa_palabras = set(p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes)
    
    palabras_ordenadas = [p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes]
    requerido = set(palabras_ordenadas[:2]) if len(palabras_ordenadas) >= 2 else set(palabras_ordenadas)
    
    n = len(programa_palabras) if len(programa_palabras) > 0 else 1
    umbral_jaccard = (n - 1) / n if n > 1 else 1.0
    
    coincidencias = []
    for prg in programas['PROGRAMA_ACADEMICO'].unique():
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
    print(f"   ✅ Encontrados {len(coincidencias)} programas equivalentes")
    
    if len(coincidencias) == 0:
        print("   ⚠️  No hay coincidencias")
        return None
    
    # PASO 3: Filtrar datos
    print("\n3️⃣  FILTRANDO DATOS...")
    programas_f = programas[programas['PROGRAMA_ACADEMICO'].isin(coincidencias)]
    snies_codes = set(programas_f['CODIGO_SNIES'].unique())
    
    maestro_f = maestro[maestro['CODIGO_SNIES'].isin(snies_codes)].copy()
    oferta_f = oferta[oferta['CODIGO_SNIES'].isin(snies_codes)].copy()
    
    print(f"   ✅ Códigos SNIES: {len(snies_codes)}")
    print(f"   ✅ Registros MAESTRO: {len(maestro_f):,}")
    print(f"   ✅ Registros OFERTA: {len(oferta_f):,}")
    
    # CREAR DICCIONARIO DE DATOS ENRIQUECIDOS
    datos_enriquecidos = {
        'programa_buscado': programa_buscar,
        'timestamp': datetime.now().isoformat(),
        'programas_equivalentes': coincidencias,
        'cantidad_equivalentes': len(coincidencias),
        'snies_codes': list(snies_codes),
        'total_snies_codes': len(snies_codes),
    }
    
    # ========== INFORMACIÓN BÁSICA DEL PROGRAMA ==========
    print("\n4️⃣  EXTRAYENDO INFORMACIÓN BÁSICA...")
    
    datos_enriquecidos['informacion_basica'] = {
        'denominaciones': coincidencias[:10],
        'niveles_academicos': programas_f['NIVEL_ACADEMICO'].unique().tolist() if 'NIVEL_ACADEMICO' in programas_f.columns else [],
        'niveles_formacion': programas_f['NIVEL_FORMACION'].unique().tolist() if 'NIVEL_FORMACION' in programas_f.columns else [],
        'areas_conocimiento': programas_f['AREA_CONOCIMIENTO'].unique().tolist() if 'AREA_CONOCIMIENTO' in programas_f.columns else [],
        'nbc': programas_f['NBC'].unique().tolist() if 'NBC' in programas_f.columns else [],
        'cine_campo_amplio': programas_f['CINE_CAMPO_AMPLIO'].unique().tolist() if 'CINE_CAMPO_AMPLIO' in programas_f.columns else [],
        'cine_campo_especifico': programas_f['CINE_CAMPO_ESPECIFICO'].unique().tolist() if 'CINE_CAMPO_ESPECIFICO' in programas_f.columns else [],
        'cine_campo_detallado': programas_f['CINE_CAMPO_DETALLADO'].unique().tolist() if 'CINE_CAMPO_DETALLADO' in programas_f.columns else [],
    }
    
    # ========== MODALIDADES ==========
    print("\n5️⃣  EXTRAYENDO MODALIDADES...")
    
    modalidades_count = programas_f['MODALIDAD'].value_counts().to_dict() if 'MODALIDAD' in programas_f.columns else {}
    datos_enriquecidos['modalidades'] = {
        'disponibles': list(modalidades_count.keys()),
        'distribucion': modalidades_count,
        'total_tipos': len(modalidades_count)
    }
    
    # ========== INSTITUCIONES ==========
    print("\n6️⃣  EXTRAYENDO INFORMACIÓN DE INSTITUCIONES...")
    
    inst_codes = set(programas_f['CODIGO_INSTITUCION'].unique())
    ies_f = ies[ies['CODIGO_INSTITUCION'].isin(inst_codes)].copy()
    
    instituciones_data = []
    for _, row in ies_f.iterrows():
        inst_info = {
            'codigo': row.get('CODIGO_INSTITUCION'),
            'nombre': row.get('INSTITUCION'),
            'tipo': row.get('CARACTER_IES'),
            'sector': row.get('SECTOR_IES'),
            'naturaleza': row.get('NATURALEZA_JURIDICA'),
            'departamento': row.get('DEPARTAMENTO_IES'),
            'municipio': row.get('MUNICIPIO_IES'),
            'acreditacion_alta_calidad': row.get('ACREDITACION_ALTA_CALIDAD'),
            'vigencia_acreditacion': row.get('VIGENCIA_ACREDITACION'),
            'telefono': row.get('TELEFONO_IES'),
            'web': row.get('PAGINA_WEB'),
            'programas_vigentes': row.get('PROGRAMAS_VIGENTES'),
        }
        instituciones_data.append(inst_info)
    
    datos_enriquecidos['instituciones'] = {
        'total': len(instituciones_data),
        'lista': instituciones_data,
        'por_tipo': ies_f['CARACTER_IES'].value_counts().to_dict() if 'CARACTER_IES' in ies_f.columns else {},
        'por_sector': ies_f['SECTOR_IES'].value_counts().to_dict() if 'SECTOR_IES' in ies_f.columns else {},
        'por_departamento': ies_f['DEPARTAMENTO_IES'].value_counts().to_dict() if 'DEPARTAMENTO_IES' in ies_f.columns else {},
        'acreditadas_alta_calidad': len(ies_f[ies_f['ACREDITACION_ALTA_CALIDAD'] == 'Si']) if 'ACREDITACION_ALTA_CALIDAD' in ies_f.columns else 0,
    }
    
    # ========== DURACIÓN (SEMESTRES/PERÍODOS) ==========
    print("\n7️⃣  EXTRAYENDO DURACIÓN DE PROGRAMAS...")
    
    # De OFERTA - NUMERO_PERIODO
    if 'NUMERO_PERIODO' in oferta_f.columns:
        periodos_disponibles = pd.to_numeric(oferta_f['NUMERO_PERIODO'], errors='coerce').dropna().unique()
        periodos_disponibles = sorted([int(p) for p in periodos_disponibles if p > 0])
    else:
        periodos_disponibles = []
    
    # De OFERTA - NUMERO_CREDITOS
    if 'NUMERO_CREDITOS' in oferta_f.columns:
        creditos_disponibles = pd.to_numeric(oferta_f['NUMERO_CREDITOS'], errors='coerce').dropna().unique()
        creditos_disponibles = sorted([int(c) for c in creditos_disponibles if c > 0])
    else:
        creditos_disponibles = []
    
    datos_enriquecidos['duracion'] = {
        'periodos_disponibles': periodos_disponibles,
        'creditos_disponibles': creditos_disponibles,
        'periodicidad': oferta_f['PERIODICIDAD'].unique().tolist() if 'PERIODICIDAD' in oferta_f.columns else [],
        'periodicidad_admisiones': oferta_f['PERIODICIDAD_ADMISIONES'].unique().tolist() if 'PERIODICIDAD_ADMISIONES' in oferta_f.columns else [],
    }
    
    # ========== MATRÍCULAS Y COSTOS ==========
    print("\n8️⃣  EXTRAYENDO INFORMACIÓN DE MATRÍCULAS...")
    
    oferta_f['MATRICULA_NUM'] = pd.to_numeric(oferta_f['MATRICULA'], errors='coerce')
    matriculas_validas = oferta_f[oferta_f['MATRICULA_NUM'].notna()]['MATRICULA_NUM']
    
    if len(matriculas_validas) > 0:
        matricula_stats = {
            'minima': float(matriculas_validas.min()),
            'maxima': float(matriculas_validas.max()),
            'promedio': float(matriculas_validas.mean()),
            'mediana': float(matriculas_validas.median()),
            'desv_estandar': float(matriculas_validas.std()),
            'registros_con_matricula': len(matriculas_validas),
        }
    else:
        matricula_stats = {
            'minima': None,
            'maxima': None,
            'promedio': None,
            'mediana': None,
            'desv_estandar': None,
            'registros_con_matricula': 0,
        }
    
    datos_enriquecidos['matriculas'] = matricula_stats
    
    # ========== ESTADO DE PROGRAMAS ==========
    print("\n9️⃣  EXTRAYENDO ESTADO DE PROGRAMAS...")
    
    estado_programa = oferta_f['ESTADO_PROGRAMA'].value_counts().to_dict() if 'ESTADO_PROGRAMA' in oferta_f.columns else {}
    estado_institucion = oferta_f['ESTADO_INSTITUCION'].value_counts().to_dict() if 'ESTADO_INSTITUCION' in oferta_f.columns else {}
    
    datos_enriquecidos['estado'] = {
        'estado_programa': estado_programa,
        'estado_institucion': estado_institucion,
        'reconocimiento': oferta_f['RECONOCIMIENTO'].unique().tolist() if 'RECONOCIMIENTO' in oferta_f.columns else [],
        'acreditacion': programas_f['PROGRAMA_ACREDITADO'].unique().tolist() if 'PROGRAMA_ACREDITADO' in programas_f.columns else [],
    }
    
    # ========== COBERTURA GEOGRÁFICA ==========
    print("\n🔟 EXTRAYENDO COBERTURA GEOGRÁFICA...")
    
    departamentos = programas_f['DEPARTAMENTO_PROGRAMA'].value_counts().to_dict() if 'DEPARTAMENTO_PROGRAMA' in programas_f.columns else {}
    municipios = programas_f['MUNICIPIO_PROGRAMA'].value_counts().to_dict() if 'MUNICIPIO_PROGRAMA' in programas_f.columns else {}
    
    datos_enriquecidos['cobertura_geografica'] = {
        'departamentos': departamentos,
        'total_departamentos': len(departamentos),
        'municipios': {k: v for k, v in list(municipios.items())[:20]},  # Top 20
        'total_municipios': len(municipios),
    }
    
    # ========== EVOLUCIÓN TEMPORAL ==========
    print("\n1️⃣1️⃣  EXTRAYENDO EVOLUCIÓN TEMPORAL...")
    
    # Períodos disponibles
    periodos_maestro = maestro_f['PERIODO'].unique()
    periodos_maestro = sorted([p for p in periodos_maestro if str(p) != 'nan'])
    
    # Evolución de matrículas por período
    maestro_f['CANTIDAD_NUM'] = pd.to_numeric(maestro_f['CANTIDAD'], errors='coerce')
    evolucion_matriculas = maestro_f[maestro_f['PROCESO'] == 'MATRICULADOS'].groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
    
    # Evolución de inscritos
    evolucion_inscritos = maestro_f[maestro_f['PROCESO'] == 'INSCRITOS'].groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
    
    # Evolución de graduados
    evolucion_graduados = maestro_f[maestro_f['PROCESO'] == 'GRADUADOS'].groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
    
    datos_enriquecidos['evolucion_temporal'] = {
        'periodos_disponibles': periodos_maestro,
        'rango_temporal': f"{periodos_maestro[0] if periodos_maestro else 'N/A'} a {periodos_maestro[-1] if periodos_maestro else 'N/A'}",
        'matriculados_por_periodo': evolucion_matriculas,
        'inscritos_por_periodo': evolucion_inscritos,
        'graduados_por_periodo': evolucion_graduados,
    }
    
    # ========== PROCESOS ACADÉMICOS ==========
    print("\n1️⃣2️⃣  EXTRAYENDO PROCESOS ACADÉMICOS...")
    
    procesos = maestro_f['PROCESO'].value_counts().to_dict()
    datos_enriquecidos['procesos'] = procesos
    
    # ========== PERSPECTIVA DE GÉNERO ==========
    print("\n1️⃣3️⃣  EXTRAYENDO INFORMACIÓN DE GÉNERO...")
    
    genero_dist = maestro_f['GENERO'].value_counts().to_dict() if 'GENERO' in maestro_f.columns else {}
    datos_enriquecidos['genero'] = genero_dist
    
    # ========== RESUMEN EJECUTIVO ==========
    print("\n1️⃣4️⃣  GENERANDO RESUMEN...")
    
    datos_enriquecidos['resumen'] = {
        'total_programas_equivalentes': len(coincidencias),
        'total_instituciones': len(instituciones_data),
        'total_departamentos': len(departamentos),
        'total_registros_maestro': len(maestro_f),
        'total_registros_oferta': len(oferta_f),
        'rango_matricula_promedio': f"${matricula_stats['minima']:,.0f} - ${matricula_stats['maxima']:,.0f}" if matricula_stats['minima'] else "N/A",
        'modalidades_disponibles': list(modalidades_count.keys()),
        'acreditadas_alta_calidad': datos_enriquecidos['instituciones']['acreditadas_alta_calidad'],
    }
    
    return datos_enriquecidos


def mostrar_resultados(datos):
    """Muestra resultados de forma legible"""
    if not datos:
        print("\n❌ No hay datos para mostrar")
        return
    
    print("\n" + "="*80)
    print("📊 RESULTADOS COMPLETOS")
    print("="*80)
    
    # Resumen
    print("\n📋 RESUMEN EJECUTIVO:")
    resumen = datos.get('resumen', {})
    for clave, valor in resumen.items():
        print(f"   • {clave}: {valor}")
    
    # Programas equivalentes
    print("\n📚 PROGRAMAS EQUIVALENTES:")
    for i, prog in enumerate(datos['programas_equivalentes'][:10], 1):
        print(f"   {i}. {prog}")
    if len(datos['programas_equivalentes']) > 10:
        print(f"   ... y {len(datos['programas_equivalentes']) - 10} más")
    
    # Instituciones
    print("\n🏫 INSTITUCIONES ({})".format(datos['instituciones']['total']))
    for inst in datos['instituciones']['lista'][:5]:
        print(f"   • {inst['nombre']} ({inst['municipio']}) - {inst['tipo']}")
    if len(datos['instituciones']['lista']) > 5:
        print(f"   ... y {len(datos['instituciones']['lista']) - 5} más")
    
    # Modalidades
    print("\n🎯 MODALIDADES:")
    for modalidad, count in datos['modalidades']['distribucion'].items():
        print(f"   • {modalidad}: {count} programas")
    
    # Duración
    print("\n⏱️  DURACIÓN:")
    print(f"   • Períodos: {datos['duracion']['periodos_disponibles']}")
    print(f"   • Créditos: {datos['duracion']['creditos_disponibles']}")
    
    # Matrículas
    print("\n💰 MATRÍCULAS:")
    mat = datos['matriculas']
    print(f"   • Mínima: ${mat['minima']:,.0f}" if mat['minima'] else "   • Mínima: N/A")
    print(f"   • Máxima: ${mat['maxima']:,.0f}" if mat['maxima'] else "   • Máxima: N/A")
    print(f"   • Promedio: ${mat['promedio']:,.0f}" if mat['promedio'] else "   • Promedio: N/A")
    
    # Geografía
    print("\n🗺️  COBERTURA GEOGRÁFICA:")
    print(f"   • Departamentos: {datos['cobertura_geografica']['total_departamentos']}")
    print(f"   • Municipios: {datos['cobertura_geografica']['total_municipios']}")
    
    # Acreditación
    print("\n✅ ACREDITACIÓN:")
    print(f"   • Instituciones con alta calidad: {datos['instituciones']['acreditadas_alta_calidad']}")
    
    print("\n" + "="*80 + "\n")


def guardar_json(datos, filename=None):
    """Guarda datos en JSON"""
    if not filename:
        programa_limpio = datos['programa_buscado'].replace(' ', '_').lower()
        filename = f"datos_snies_{programa_limpio}.json"
    
    # Convertir objetos no serializables
    def convertir(obj):
        if pd.isna(obj):
            return None
        if isinstance(obj, (int, float)):
            return obj if not pd.isna(obj) else None
        if isinstance(obj, dict):
            return {k: convertir(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convertir(item) for item in obj]
        return str(obj)
    
    datos_json = convertir(datos)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Datos guardados en: {filename}\n")


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🎓 EXTRACTOR COMPLETO DE DATOS SNIES")
    print("="*80)
    
    while True:
        programa = input("\n🔍 Ingresa programa (o 'salir'): ").strip()
        
        if programa.lower() == 'salir':
            break
        
        if not programa:
            continue
        
        datos = buscar_y_extraer_programa(programa)
        
        if datos:
            mostrar_resultados(datos)
            guardar = input("💾 ¿Guardar en JSON? (s/n): ").strip().lower()
            if guardar == 's':
                guardar_json(datos)


if __name__ == "__main__":
    main()