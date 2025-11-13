"""
Lector de Datos Enriquecidos SNIES
Extrae información completa: programas, instituciones, duración, matrículas, geografía, etc.
Ubicación: src/lector_datos_enriquecidos.py
"""

import pandas as pd
from typing import Dict, List
from collections import Counter


class LectorDatosEnriquecidos:
    """Extrae datos enriquecidos de programas académicos SNIES"""
    
    def __init__(self, maestro_df: pd.DataFrame, oferta_df: pd.DataFrame, 
                 programas_df: pd.DataFrame, ies_df: pd.DataFrame, verbose=True):
        """
        Inicializa el lector con dataframes cargados
        
        Args:
            maestro_df: DataFrame MAESTRO
            oferta_df: DataFrame OFERTA
            programas_df: DataFrame PROGRAMAS
            ies_df: DataFrame IES
            verbose: Mostrar mensajes de progreso
        """
        self.maestro = maestro_df
        self.oferta = oferta_df
        self.programas = programas_df
        self.ies = ies_df
        self.verbose = verbose
    
    def log(self, mensaje):
        """Imprime mensaje si verbose está activo"""
        if self.verbose:
            print(f"   {mensaje}")
    
    def extraer_datos_enriquecidos(self, snies_codes: List[str], 
                                   denominaciones: List[str]) -> Dict:
        """
        Extrae TODOS los datos disponibles para un conjunto de programas
        
        Args:
            snies_codes: Lista de códigos SNIES
            denominaciones: Lista de denominaciones de programas
            
        Returns:
            Dict con datos enriquecidos completos
        """
        self.log("📊 Extrayendo datos enriquecidos...")
        
        # Filtrar datos por códigos SNIES
        maestro_f = self.maestro[self.maestro['CODIGO_SNIES'].isin(snies_codes)].copy()
        oferta_f = self.oferta[self.oferta['CODIGO_SNIES'].isin(snies_codes)].copy()
        programas_f = self.programas[self.programas['CODIGO_SNIES'].isin(snies_codes)].copy()
        
        datos = {
            'programas_equivalentes': denominaciones,
            'cantidad_equivalentes': len(denominaciones),
            'snies_codes': list(snies_codes),
            'registros_maestro': len(maestro_f),
            'registros_oferta': len(oferta_f),
        }
        
        # 1. INFORMACIÓN BÁSICA
        self.log("1️⃣  Extrayendo información básica...")
        datos['informacion_basica'] = self._extraer_informacion_basica(programas_f)
        
        # 2. MODALIDADES
        self.log("2️⃣  Extrayendo modalidades...")
        datos['modalidades'] = self._extraer_modalidades(programas_f)
        
        # 3. INSTITUCIONES
        self.log("3️⃣  Extrayendo instituciones...")
        inst_codes = set(programas_f['CODIGO_INSTITUCION'].unique())
        ies_f = self.ies[self.ies['CODIGO_INSTITUCION'].isin(inst_codes)].copy()
        datos['instituciones'] = self._extraer_instituciones(ies_f, programas_f)
        
        # 4. DURACIÓN Y ESTRUCTURA
        self.log("4️⃣  Extrayendo duración y estructura...")
        datos['duracion'] = self._extraer_duracion(oferta_f)
        
        # 5. MATRÍCULAS Y COSTOS
        self.log("5️⃣  Extrayendo matrículas...")
        datos['matriculas'] = self._extraer_matriculas(oferta_f)
        
        # 6. ESTADO
        self.log("6️⃣  Extrayendo estado...")
        datos['estado'] = self._extraer_estado(oferta_f, programas_f)
        
        # 7. COBERTURA GEOGRÁFICA
        self.log("7️⃣  Extrayendo cobertura geográfica...")
        datos['cobertura_geografica'] = self._extraer_cobertura_geografica(programas_f)
        
        # 8. EVOLUCIÓN TEMPORAL
        self.log("8️⃣  Extrayendo evolución temporal...")
        datos['evolucion_temporal'] = self._extraer_evolucion_temporal(maestro_f)
        
        # 9. PROCESOS ACADÉMICOS
        self.log("9️⃣  Extrayendo procesos académicos...")
        datos['procesos'] = self._extraer_procesos(maestro_f)
        
        # 10. GÉNERO
        self.log("🔟 Extrayendo distribución de género...")
        datos['genero'] = self._extraer_genero(maestro_f)
        
        # 11. CONTEXTO GENERAL DEL MERCADO
        self.log("1️⃣1️⃣  Extrayendo contexto del mercado...")
        datos['contexto_mercado'] = self._extraer_contexto_mercado(
            denominaciones, ies_f, programas_f, maestro_f, oferta_f
        )
        
        self.log("✅ Datos enriquecidos extraídos")
        return datos
    
    def _extraer_informacion_basica(self, programas_f: pd.DataFrame) -> Dict:
        """Extrae información básica de programas"""
        return {
            'denominaciones': programas_f['PROGRAMA_ACADEMICO'].unique().tolist()[:10],
            'niveles_academicos': programas_f['NIVEL_ACADEMICO'].unique().tolist() 
                if 'NIVEL_ACADEMICO' in programas_f.columns else [],
            'niveles_formacion': programas_f['NIVEL_FORMACION'].unique().tolist() 
                if 'NIVEL_FORMACION' in programas_f.columns else [],
            'areas_conocimiento': programas_f['AREA_CONOCIMIENTO'].unique().tolist() 
                if 'AREA_CONOCIMIENTO' in programas_f.columns else [],
            'nbc': programas_f['NBC'].unique().tolist() 
                if 'NBC' in programas_f.columns else [],
            'cine_campo_amplio': programas_f['CINE_CAMPO_AMPLIO'].unique().tolist() 
                if 'CINE_CAMPO_AMPLIO' in programas_f.columns else [],
        }
    
    def _extraer_modalidades(self, programas_f: pd.DataFrame) -> Dict:
        """Extrae información de modalidades"""
        modalidades_count = programas_f['MODALIDAD'].value_counts().to_dict() \
            if 'MODALIDAD' in programas_f.columns else {}
        
        return {
            'disponibles': list(modalidades_count.keys()),
            'distribucion': modalidades_count,
            'total_tipos': len(modalidades_count)
        }
    
    def _extraer_instituciones(self, ies_f: pd.DataFrame, programas_f: pd.DataFrame) -> Dict:
        """Extrae información de instituciones oferentes"""
        instituciones_data = []
        
        for _, row in ies_f.iterrows():
            inst_info = {
                'codigo': str(row.get('CODIGO_INSTITUCION', '')),
                'nombre': str(row.get('INSTITUCION', '')),
                'tipo': str(row.get('CARACTER_IES', '')),
                'sector': str(row.get('SECTOR_IES', '')),
                'naturaleza': str(row.get('NATURALEZA_JURIDICA', '')),
                'departamento': str(row.get('DEPARTAMENTO_IES', '')),
                'municipio': str(row.get('MUNICIPIO_IES', '')),
                'acreditacion_alta_calidad': str(row.get('ACREDITACION_ALTA_CALIDAD', '')),
                'vigencia_acreditacion': str(row.get('VIGENCIA_ACREDITACION', '')),
                'telefono': str(row.get('TELEFONO_IES', '')),
                'web': str(row.get('PAGINA_WEB', '')),
                'programas_vigentes': row.get('PROGRAMAS_VIGENTES'),
            }
            instituciones_data.append(inst_info)
        
        return {
            'total': len(instituciones_data),
            'lista': instituciones_data,
            'por_tipo': ies_f['CARACTER_IES'].value_counts().to_dict() 
                if 'CARACTER_IES' in ies_f.columns else {},
            'por_sector': ies_f['SECTOR_IES'].value_counts().to_dict() 
                if 'SECTOR_IES' in ies_f.columns else {},
            'por_departamento': ies_f['DEPARTAMENTO_IES'].value_counts().to_dict() 
                if 'DEPARTAMENTO_IES' in ies_f.columns else {},
            'acreditadas_alta_calidad': len(ies_f[ies_f['ACREDITACION_ALTA_CALIDAD'] == 'Si']) 
                if 'ACREDITACION_ALTA_CALIDAD' in ies_f.columns else 0,
        }
    
    def _extraer_duracion(self, oferta_f: pd.DataFrame) -> Dict:
        """Extrae información de duración y estructura"""
        periodos_disponibles = []
        if 'NUMERO_PERIODO' in oferta_f.columns:
            periodos = pd.to_numeric(oferta_f['NUMERO_PERIODO'], errors='coerce').dropna().unique()
            periodos_disponibles = sorted([int(p) for p in periodos if p > 0])
        
        creditos_disponibles = []
        if 'NUMERO_CREDITOS' in oferta_f.columns:
            creditos = pd.to_numeric(oferta_f['NUMERO_CREDITOS'], errors='coerce').dropna().unique()
            creditos_disponibles = sorted([int(c) for c in creditos if c > 0])
        
        return {
            'periodos_disponibles': periodos_disponibles,
            'creditos_disponibles': creditos_disponibles,
            'periodicidad': oferta_f['PERIODICIDAD'].unique().tolist() 
                if 'PERIODICIDAD' in oferta_f.columns else [],
            'periodicidad_admisiones': oferta_f['PERIODICIDAD_ADMISIONES'].unique().tolist() 
                if 'PERIODICIDAD_ADMISIONES' in oferta_f.columns else [],
        }
    
    def _extraer_matriculas(self, oferta_f: pd.DataFrame) -> Dict:
        """Extrae información de matrículas y costos"""
        oferta_f_copy = oferta_f.copy()
        oferta_f_copy['MATRICULA_NUM'] = pd.to_numeric(oferta_f_copy['MATRICULA'], errors='coerce')
        matriculas_validas = oferta_f_copy[oferta_f_copy['MATRICULA_NUM'].notna()]['MATRICULA_NUM']
        
        if len(matriculas_validas) > 0:
            return {
                'minima': float(matriculas_validas.min()),
                'maxima': float(matriculas_validas.max()),
                'promedio': float(matriculas_validas.mean()),
                'mediana': float(matriculas_validas.median()),
                'desv_estandar': float(matriculas_validas.std()),
                'registros_con_matricula': len(matriculas_validas),
            }
        else:
            return {
                'minima': None,
                'maxima': None,
                'promedio': None,
                'mediana': None,
                'desv_estandar': None,
                'registros_con_matricula': 0,
            }
    
    def _extraer_estado(self, oferta_f: pd.DataFrame, programas_f: pd.DataFrame) -> Dict:
        """Extrae información de estado de programas"""
        return {
            'estado_programa': oferta_f['ESTADO_PROGRAMA'].value_counts().to_dict() 
                if 'ESTADO_PROGRAMA' in oferta_f.columns else {},
            'estado_institucion': oferta_f['ESTADO_INSTITUCION'].value_counts().to_dict() 
                if 'ESTADO_INSTITUCION' in oferta_f.columns else {},
            'reconocimiento': oferta_f['RECONOCIMIENTO'].unique().tolist() 
                if 'RECONOCIMIENTO' in oferta_f.columns else [],
        }
    
    def _extraer_cobertura_geografica(self, programas_f: pd.DataFrame) -> Dict:
        """Extrae información de cobertura geográfica"""
        departamentos = programas_f['DEPARTAMENTO_PROGRAMA'].value_counts().to_dict() \
            if 'DEPARTAMENTO_PROGRAMA' in programas_f.columns else {}
        municipios = programas_f['MUNICIPIO_PROGRAMA'].value_counts().to_dict() \
            if 'MUNICIPIO_PROGRAMA' in programas_f.columns else {}
        
        return {
            'departamentos': departamentos,
            'total_departamentos': len(departamentos),
            'municipios_top': dict(list(municipios.items())[:20]),
            'total_municipios': len(municipios),
        }
    
    def _extraer_evolucion_temporal(self, maestro_f: pd.DataFrame) -> Dict:
        """Extrae información de evolución temporal"""
        periodos_maestro = maestro_f['PERIODO'].unique()
        periodos_maestro = sorted([p for p in periodos_maestro if str(p) != 'nan'])
        
        maestro_f_copy = maestro_f.copy()
        maestro_f_copy['CANTIDAD_NUM'] = pd.to_numeric(maestro_f_copy['CANTIDAD'], errors='coerce')
        
        evolucion_matriculas = maestro_f_copy[maestro_f_copy['PROCESO'] == 'MATRICULADOS'] \
            .groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
        evolucion_inscritos = maestro_f_copy[maestro_f_copy['PROCESO'] == 'INSCRITOS'] \
            .groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
        evolucion_graduados = maestro_f_copy[maestro_f_copy['PROCESO'] == 'GRADUADOS'] \
            .groupby('PERIODO')['CANTIDAD_NUM'].sum().to_dict()
        
        return {
            'periodos_disponibles': periodos_maestro,
            'rango_temporal': f"{periodos_maestro[0] if periodos_maestro else 'N/A'} a {periodos_maestro[-1] if periodos_maestro else 'N/A'}",
            'matriculados_por_periodo': {str(k): v for k, v in evolucion_matriculas.items()},
            'inscritos_por_periodo': {str(k): v for k, v in evolucion_inscritos.items()},
            'graduados_por_periodo': {str(k): v for k, v in evolucion_graduados.items()},
        }
    
    def _extraer_procesos(self, maestro_f: pd.DataFrame) -> Dict:
        """Extrae información de procesos académicos"""
        procesos = maestro_f['PROCESO'].value_counts().to_dict()
        
        # Calcular tasas
        matriculados = procesos.get('MATRICULADOS', 0)
        graduados = procesos.get('GRADUADOS', 0)
        tasa_graduacion = (graduados / matriculados * 100) if matriculados > 0 else 0
        
        return {
            'distribucion': procesos,
            'tasa_graduacion_estimada': round(tasa_graduacion, 2),
        }
    
    def _extraer_genero(self, maestro_f: pd.DataFrame) -> Dict:
        """Extrae distribución de género"""
        genero_dist = maestro_f['GENERO'].value_counts().to_dict() \
            if 'GENERO' in maestro_f.columns else {}
        
        total = sum(genero_dist.values()) if genero_dist else 0
        
        return {
            'distribucion': genero_dist,
            'porcentajes': {k: round(v/total*100, 2) for k, v in genero_dist.items()} if total > 0 else {},
        }
    
    def _extraer_contexto_mercado(self, denominaciones: List[str], ies_f: pd.DataFrame,
                                  programas_f: pd.DataFrame, maestro_f: pd.DataFrame,
                                  oferta_f: pd.DataFrame) -> Dict:
        """
        Extrae contexto general del mercado académico para este tipo de programa
        Información valiosa para estudiantes que estudian la oferta académica
        """
        
        # Análisis de competencia
        total_institutos = len(ies_f)
        universidades = len(ies_f[ies_f['CARACTER_IES'] == 'Universidad']) if 'CARACTER_IES' in ies_f.columns else 0
        tecnologicas = len(ies_f[ies_f['CARACTER_IES'] == 'Tecnologica']) if 'CARACTER_IES' in ies_f.columns else 0
        instituciones_tecnicas = len(ies_f[ies_f['CARACTER_IES'] == 'Institucion Tecnica']) if 'CARACTER_IES' in ies_f.columns else 0
        
        # Análisis por sector
        sector_oficial = len(ies_f[ies_f['SECTOR_IES'] == 'Oficial']) if 'SECTOR_IES' in ies_f.columns else 0
        sector_privado = len(ies_f[ies_f['SECTOR_IES'] == 'Privado']) if 'SECTOR_IES' in ies_f.columns else 0
        
        # Análisis de acreditación
        acreditadas = len(ies_f[ies_f['ACREDITACION_ALTA_CALIDAD'] == 'Si']) if 'ACREDITACION_ALTA_CALIDAD' in ies_f.columns else 0
        porcentaje_acreditacion = (acreditadas / total_institutos * 100) if total_institutos > 0 else 0
        
        # Concentración geográfica
        top_departamentos = programas_f['DEPARTAMENTO_PROGRAMA'].value_counts().head(3).to_dict() \
            if 'DEPARTAMENTO_PROGRAMA' in programas_f.columns else {}
        
        # Demanda (basada en matrículas)
        maestro_f_copy = maestro_f.copy()
        maestro_f_copy['CANTIDAD_NUM'] = pd.to_numeric(maestro_f_copy['CANTIDAD'], errors='coerce')
        
        total_matriculados_reciente = maestro_f_copy[maestro_f_copy['PROCESO'] == 'MATRICULADOS']['CANTIDAD_NUM'].sum()
        total_nuevos_reciente = maestro_f_copy[maestro_f_copy['PROCESO'] == 'NUEVOS']['CANTIDAD_NUM'].sum()
        
        # Elasticidad de precio
        oferta_f_copy = oferta_f.copy()
        oferta_f_copy['MATRICULA_NUM'] = pd.to_numeric(oferta_f_copy['MATRICULA'], errors='coerce')
        matriculas_por_inst = oferta_f_copy.groupby('IES_PADRE')['MATRICULA_NUM'].mean()
        variabilidad_precios = float(matriculas_por_inst.std()) if len(matriculas_por_inst) > 0 else 0
        
        return {
            'competencia': {
                'total_instituciones': total_institutos,
                'universidades': universidades,
                'tecnologicas': tecnologicas,
                'instituciones_tecnicas': instituciones_tecnicas,
            },
            'sector': {
                'oficial': sector_oficial,
                'privado': sector_privado,
                'porcentaje_privado': round(sector_privado / total_institutos * 100, 2) if total_institutos > 0 else 0,
            },
            'acreditacion': {
                'total_acreditadas': acreditadas,
                'porcentaje_acreditacion': round(porcentaje_acreditacion, 2),
            },
            'concentracion_geografica': {
                'top_departamentos': top_departamentos,
                'es_concentrado': len(top_departamentos) <= 3 and sum(top_departamentos.values()) >= total_institutos * 0.5,
            },
            'demanda': {
                'total_matriculados_reciente': int(total_matriculados_reciente) if total_matriculados_reciente else 0,
                'total_nuevos_reciente': int(total_nuevos_reciente) if total_nuevos_reciente else 0,
                'nivel_demanda': 'Alto' if total_nuevos_reciente > 500 else 'Medio' if total_nuevos_reciente > 100 else 'Bajo',
            },
            'precios': {
                'variabilidad_precios': round(variabilidad_precios, 0),
                'mercado_homogeneo': variabilidad_precios < 1000000,  # Menos de 1M de variación
            },
            'tendencias': {
                'programas_crecientes': True,  # Se asume creciente si hay múltiples equivalentes
                'modalidades_modernas': len(programas_f['MODALIDAD'].unique()) > 1 if 'MODALIDAD' in programas_f.columns else False,
            }
        }