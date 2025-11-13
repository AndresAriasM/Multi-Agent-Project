"""
Aplicación Streamlit - Análisis de Programas SNIES
Ubicación: app.py
Ejecución: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path
from io import BytesIO

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from src.lector_tablas_snies import LectorSNIES
from src.lector_datos_enriquecidos import LectorDatosEnriquecidos
from src.agentes.coordinador import CoordinadorAgentes
import numpy as np


# ========== CONFIGURACIÓN STREAMLIT ==========
st.set_page_config(
    page_title="Análisis SNIES",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTitle {
        color: #1f4e79;
        font-size: 2.5rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# ========== INICIALIZAR SESIÓN ==========
if 'datos_cargados' not in st.session_state:
    st.session_state.datos_cargados = False
    st.session_state.programa_actual = None
    st.session_state.resultados_agentes = None
    st.session_state.datos_json = None


# ========== FUNCIONES AUXILIARES ==========
@st.cache_resource
def cargar_snies():
    """Carga datos SNIES (una sola vez)"""
    with st.spinner("⏳ Cargando datos SNIES..."):
        lector = LectorSNIES(["temp"], verbose=False)
        lector.cargar_datos()
    return lector


def buscar_programa_snies(lector, programa_buscar: str):
    """Busca el programa y genera análisis"""
    import numpy as np
    
    print(f"\n🔍 Buscando: {programa_buscar}")
    
    # Paso 1: Buscar programa
    with st.spinner("🔍 Buscando programa..."):
        programas_list = lector.datos['programas']['PROGRAMA_ACADEMICO'].unique().tolist()
        
        # Búsqueda con Jaccard
        palabras_comunes = {'de', 'la', 'el', 'y', 'en', 'a', 'o', 'los', 'las', 'un', 'una', 'del', 'con'}
        programa_palabras = set(p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes)
        palabras_ordenadas = [p.lower() for p in programa_buscar.split() if p.lower() not in palabras_comunes]
        requerido = set(palabras_ordenadas[:2]) if len(palabras_ordenadas) >= 2 else set(palabras_ordenadas)
        
        n = len(programa_palabras) if len(programa_palabras) > 0 else 1
        umbral_jaccard = (n - 1) / n if n > 1 else 1.0
        
        coincidencias = []
        for prg in programas_list:
            prg_palabras = set(p.lower() for p in str(prg).split() if p.lower() not in palabras_comunes)
            interseccion = len(programa_palabras.intersection(prg_palabras))
            jaccard = interseccion / len(programa_palabras) if len(programa_palabras) > 0 else 1.0
            tiene_requeridas = requerido.issubset(prg_palabras)
            
            if jaccard >= umbral_jaccard and tiene_requeridas:
                coincidencias.append(prg)
        
        coincidencias = sorted(list(set(coincidencias)))
        
        if not coincidencias:
            st.error(f"❌ No se encontraron programas similares a '{programa_buscar}'")
            return None
        
        st.success(f"✅ Encontrados {len(coincidencias)} programas equivalentes")

    # Paso 2: Enriquecer datos
    with st.spinner("📊 Enriqueciendo datos..."):
        programas_df = lector.datos['programas']
        maestro_df = lector.datos['maestro']
        oferta_df = lector.datos['oferta']
        ies_df = lector.datos['ies']
        
        programas_filtrados = programas_df[programas_df['PROGRAMA_ACADEMICO'].isin(coincidencias)]
        snies_codes = list(programas_filtrados['CODIGO_SNIES'].unique())
        
        maestro_filtrado = maestro_df[maestro_df['CODIGO_SNIES'].isin(snies_codes)]
        maestro_merged = maestro_filtrado.merge(programas_filtrados, on='CODIGO_SNIES', how='left')
        
        if not oferta_df.empty:
            maestro_merged = maestro_merged.merge(oferta_df, on=['CODIGO_SNIES', 'PERIODO'], how='left')
        
        datos = {
            'nombre': programa_buscar,
            'maestro': maestro_merged,
            'programas': programas_filtrados,
            'equivalentes': coincidencias,
            'snies_codes': snies_codes,
            'datos_enriquecidos': {}
        }
        
        # Generar datos enriquecidos
        try:
            lector_enriquecido = LectorDatosEnriquecidos(
                maestro_df, oferta_df, programas_df, ies_df, verbose=False
            )
            datos['datos_enriquecidos'] = lector_enriquecido.extraer_datos_enriquecidos(
                snies_codes=snies_codes,
                denominaciones=coincidencias
            )
        except Exception as e:
            st.warning(f"⚠️ Error enriqueciendo datos: {e}")
            datos['datos_enriquecidos'] = {}

    # Paso 3: Ejecutar agentes
    with st.spinner("🤖 Ejecutando análisis con agentes..."):
        try:
            coordinador = CoordinadorAgentes(datos)
            resultados = coordinador.ejecutar()
            return datos, resultados
        except Exception as e:
            st.error(f"❌ Error ejecutando agentes: {e}")
            return None, None


def crear_excel_resultados(datos, resultados):
    """Crea archivo Excel con resultados"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Resumen
        resumen_df = pd.DataFrame({
            'Métrica': [
                'Programa Analizado',
                'Denominación Oficial',
                'Programas Equivalentes',
                'Registros SNIES',
                'Instituciones',
                'Departamentos',
            ],
            'Valor': [
                datos.get('nombre', 'N/A'),
                resultados.get('sintesis', {}).get('denominacion_oficial', 'N/A'),
                len(datos.get('equivalentes', [])),
                len(datos.get('maestro', pd.DataFrame())),
                datos.get('maestro', pd.DataFrame()).get('CODIGO_INSTITUCION_x', pd.Series()).nunique() if 'CODIGO_INSTITUCION_x' in datos.get('maestro', pd.DataFrame()).columns else 'N/A',
                datos.get('maestro', pd.DataFrame()).get('DEPARTAMENTO_PROGRAMA', pd.Series()).nunique() if 'DEPARTAMENTO_PROGRAMA' in datos.get('maestro', pd.DataFrame()).columns else 'N/A',
            ]
        })
        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja 2: Denominaciones
        denom = resultados.get('denominacion', {})
        denom_df = pd.DataFrame({
            'Denominación': denom.get('denominaciones_totales', []),
            'Variación': range(1, len(denom.get('denominaciones_totales', [])) + 1)
        })
        denom_df.to_excel(writer, sheet_name='Denominaciones', index=False)
        
        # Hoja 3: Tendencias
        tend = resultados.get('tendencias', {})
        tendencias_data = {
            'Emergentes': tend.get('palabras_emergentes', []),
            'Decadentes': tend.get('palabras_decadentes', []),
        }
        max_len = max(len(tendencias_data['Emergentes']), len(tendencias_data['Decadentes']))
        tendencias_data['Emergentes'] += [''] * (max_len - len(tendencias_data['Emergentes']))
        tendencias_data['Decadentes'] += [''] * (max_len - len(tendencias_data['Decadentes']))
        tend_df = pd.DataFrame(tendencias_data)
        tend_df.to_excel(writer, sheet_name='Tendencias', index=False)
        
        # Hoja 4: Instituciones
        inst_geo = resultados.get('instituciones_geografia', {})
        if inst_geo.get('segmentacion_institucional'):
            seg = inst_geo['segmentacion_institucional']
            inst_data = {
                'Tipo de Análisis': [],
                'Categoría': [],
                'Valor': []
            }
            
            for tipo, dist in seg.get('por_tipo', {}).get('distribucion', {}).items():
                inst_data['Tipo de Análisis'].append('Por Tipo')
                inst_data['Categoría'].append(tipo)
                inst_data['Valor'].append(dist)
            
            for sector, dist in seg.get('por_sector', {}).get('distribucion', {}).items():
                inst_data['Tipo de Análisis'].append('Por Sector')
                inst_data['Categoría'].append(sector)
                inst_data['Valor'].append(dist)
            
            inst_df = pd.DataFrame(inst_data)
            inst_df.to_excel(writer, sheet_name='Instituciones', index=False)
        
        # Hoja 5: Hubs Geográficos
        if inst_geo.get('hub_geograficos', {}).get('hubs_principales'):
            hubs_data = []
            for hub in inst_geo['hub_geograficos']['hubs_principales']:
                hubs_data.append({
                    'Departamento': hub.get('departamento'),
                    'Programas': hub.get('cantidad_programas'),
                    'Porcentaje': hub.get('porcentaje'),
                    'Nivel': hub.get('nivel')
                })
            hubs_df = pd.DataFrame(hubs_data)
            hubs_df.to_excel(writer, sheet_name='Hubs Geográficos', index=False)
        
        # Hoja 6: Recomendaciones
        sint = resultados.get('sintesis', {})
        recom_data = {
            'Tipo': [],
            'Recomendación': []
        }
        
        for h in sint.get('hallazgos_principales', []):
            recom_data['Tipo'].append('Hallazgo')
            recom_data['Recomendación'].append(h)
        
        for r in sint.get('recomendaciones', []):
            recom_data['Tipo'].append('Recomendación')
            recom_data['Recomendación'].append(r)
        
        recom_df = pd.DataFrame(recom_data)
        recom_df.to_excel(writer, sheet_name='Recomendaciones', index=False)
    
    output.seek(0)
    return output


# ========== INTERFAZ STREAMLIT ==========

st.title("📚 Análisis SNIES - Sistema Multi-Agente")

# Información sobre qué hace
with st.expander("ℹ️ ¿Cómo funciona?", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Búsqueda**
        - Buscas un programa académico
        - Se encuentran programas equivalentes por similitud
        - Se extraen datos de la base SNIES
        """)
    
    with col2:
        st.markdown("""
        **🤖 Agentes (IA)**
        - **Denominación:** Normaliza nombres del programa
        - **Tendencias:** Detecta palabras emergentes/en declive
        - **Geografía:** Analiza dónde se ofrece el programa
        """)
    
    with col3:
        st.markdown("""
        **📊 Resultados**
        - Análisis completo del programa
        - Datos de instituciones oferentes
        - Oportunidades y recomendaciones
        """)

st.divider()

# Input del usuario
st.subheader("🔎 Buscar Programa")

programa_input = st.text_input(
    "Ingresa el nombre del programa",
    placeholder="Ej: Ingeniería de Datos, Maestría en Administración",
    help="Escribe parte o el nombre completo del programa"
)

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)

with col3:
    st.caption("💡 Ejemplos: Doctorado Ciencias Sociales, Ingeniería Software, Maestría Finanzas")

# Ejecutar búsqueda
if buscar_btn and programa_input:
    st.session_state.programa_actual = programa_input
    
    # Cargar SNIES
    lector = cargar_snies()
    
    # Buscar y analizar
    datos, resultados = buscar_programa_snies(lector, programa_input)
    
    if datos and resultados:
        st.session_state.datos_cargados = True
        st.session_state.resultados_agentes = resultados
        st.session_state.datos_json = datos
        st.success("✅ Análisis completado exitosamente")
    else:
        st.session_state.datos_cargados = False

# Mostrar resultados
if st.session_state.datos_cargados and st.session_state.resultados_agentes:
    resultados = st.session_state.resultados_agentes
    datos = st.session_state.datos_json
    
    st.divider()
    st.subheader("📋 Resultados del Análisis")
    
    # Tabs con resultados
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen",
        "🏫 Instituciones",
        "📈 Tendencias",
        "💾 Descargar"
    ])
    
    # TAB 1: Resumen
    with tab1:
        sint = resultados.get('sintesis', {})
        denom = resultados.get('denominacion', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Programas Equivalentes",
                len(datos.get('equivalentes', []))
            )
        
        with col2:
            st.metric(
                "Registros SNIES",
                len(datos.get('maestro', pd.DataFrame()))
            )
        
        with col3:
            inst_count = datos.get('maestro', pd.DataFrame()).get('CODIGO_INSTITUCION_x', pd.Series()).nunique() if 'CODIGO_INSTITUCION_x' in datos.get('maestro', pd.DataFrame()).columns else 0
            st.metric("Instituciones", inst_count)
        
        with col4:
            depts = datos.get('maestro', pd.DataFrame()).get('DEPARTAMENTO_PROGRAMA', pd.Series()).nunique() if 'DEPARTAMENTO_PROGRAMA' in datos.get('maestro', pd.DataFrame()).columns else 0
            st.metric("Departamentos", depts)
        
        st.markdown("**Denominación Oficial:**")
        st.info(sint.get('denominacion_oficial', 'N/A'))
        
        st.markdown("**Hallazgos Principales:**")
        for hallazgo in sint.get('hallazgos_principales', []):
            st.write(f"• {hallazgo}")
        
        st.markdown("**Recomendaciones:**")
        for rec in sint.get('recomendaciones', []):
            st.write(f"• {rec}")
    
    # TAB 2: Instituciones
    with tab2:
        inst_geo = resultados.get('instituciones_geografia', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Segmentación por Tipo:**")
            seg_tipo = inst_geo.get('segmentacion_institucional', {}).get('por_tipo', {}).get('distribucion', {})
            if seg_tipo:
                for tipo, count in seg_tipo.items():
                    st.write(f"• {tipo}: {count}")
            else:
                st.write("Sin datos")
        
        with col2:
            st.markdown("**Segmentación por Sector:**")
            seg_sector = inst_geo.get('segmentacion_institucional', {}).get('por_sector', {}).get('distribucion', {})
            if seg_sector:
                for sector, count in seg_sector.items():
                    st.write(f"• {sector}: {count}")
            else:
                st.write("Sin datos")
        
        st.markdown("**Hubs Geográficos (mayor concentración):**")
        hubs = inst_geo.get('hub_geograficos', {}).get('hubs_principales', [])
        if hubs:
            for hub in hubs[:5]:
                st.write(f"• {hub.get('departamento')}: {hub.get('cantidad_programas')} programas ({hub.get('porcentaje')}%)")
        else:
            st.write("Sin datos de concentración geográfica")
        
        st.markdown("**Oportunidades de Expansión:**")
        gaps = inst_geo.get('gaps_geograficos', {}).get('departamentos_sin_cobertura', [])
        if gaps:
            st.write(f"{len(gaps)} departamentos sin cobertura: {', '.join(gaps[:5])}{'...' if len(gaps) > 5 else ''}")
        else:
            st.write("Buena cobertura nacional")
    
    # TAB 3: Tendencias
    with tab3:
        tend = resultados.get('tendencias', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Palabras Emergentes:**")
            for palabra in tend.get('palabras_emergentes', []):
                st.write(f"🆙 {palabra}")
        
        with col2:
            st.markdown("**Palabras en Declive:**")
            decadentes = tend.get('palabras_decadentes', [])
            if decadentes:
                for palabra in decadentes:
                    st.write(f"📉 {palabra}")
            else:
                st.write("Ninguna identificada")
        
        st.markdown("**Tendencias del Mercado:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Nacional:**")
            st.write(tend.get('tendencias_nacionales', {}).get('tendencia', 'N/A'))
        
        with col2:
            st.write("**Global:**")
            st.write(tend.get('tendencias_globales', {}).get('tendencia', 'N/A'))
    
    # TAB 4: Descargar
    with tab4:
        st.markdown("**Descargar Resultados**")
        
        col1, col2 = st.columns(2)
        
        # Descargar Excel
        with col1:
            excel_file = crear_excel_resultados(datos, resultados)
            
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_file,
                file_name=f"analisis_snies_{datos.get('nombre', 'programa').replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
            
            st.caption("Excel con 6 hojas:")
            st.write("- Resumen")
            st.write("- Denominaciones")
            st.write("- Tendencias")
            st.write("- Instituciones")
            st.write("- Hubs Geográficos")
            st.write("- Recomendaciones")
        
        # Descargar PowerPoint
        with col2:
            from src.presentacion.generador_powerpoint import GeneradorPowerPoint
            
            try:
                with st.spinner("📊 Generando PowerPoint..."):
                    gen_ppt = GeneradorPowerPoint(datos, resultados, "")
                    ppt_bytes = BytesIO()
                    gen_ppt.prs.save(ppt_bytes)
                    ppt_bytes.seek(0)
                    
                    st.download_button(
                        label="📈 Descargar PowerPoint",
                        data=ppt_bytes,
                        file_name=f"analisis_snies_{datos.get('nombre', 'programa').replace(' ', '_')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.caption("PowerPoint con:")
                    st.write("- Portada y contenido")
                    st.write("- Análisis completo")
                    st.write("- Gráficas y tablas")
                    st.write("- Conclusiones")
            except Exception as e:
                st.error(f"Error generando PowerPoint: {e}")
                st.info("💡 Puedes usar el Excel como alternativa")

elif not st.session_state.datos_cargados and programa_input and not buscar_btn:
    st.info("👈 Haz clic en 'Buscar' para analizar el programa")