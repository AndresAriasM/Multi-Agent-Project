#!/usr/bin/env python3
"""
Lector de Tablas SNIES - Versión Mejorada
Carga y procesa datos de programas académicos colombianos
Permite buscar múltiples programas y compararlos

Uso:
    # Un programa
    python lector_tablas_snies.py "DOCTORADO CIENCIAS SOCIALES"
    
    # Múltiples programas
    python lector_tablas_snies.py "DOCTORADO CIENCIAS SOCIALES" "MAESTRIA ADMINISTRACION" "ESPECIALIZACIÓN FINANZAS"
    
    # Desde archivo
    python lector_tablas_snies.py --file programas.txt
    
    # Modo interactivo
    python lector_tablas_snies.py --interactive
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from typing import List, Dict


class LectorSNIES:
    """Carga y procesa datos de SNIES"""
    
    URLS = {
        'maestro': 'https://robertohincapie.com/data/snies/MAESTRO.parquet',
        'oferta': 'https://robertohincapie.com/data/snies/OFERTA.parquet',
        'programas': 'https://robertohincapie.com/data/snies/PROGRAMAS.parquet',
        'ies': 'https://robertohincapie.com/data/snies/IES.parquet'
    }
    
    def __init__(self, programas: List[str] = None, verbose=True):
        """
        Inicializa el lector
        
        Args:
            programas: Lista de programas a buscar
            verbose: Mostrar mensajes de progreso
        """
        self.programas = programas if programas else ['DOCTORADO CIENCIAS SOCIALES']
        self.verbose = verbose
        self.datos = {}
        self.resultados = {}  # {nombre_programa: datos_procesados}
        
    def log(self, mensaje, nivel="INFO"):
        """Imprime mensajes si verbose está activo"""
        if self.verbose:
            prefijos = {"INFO": "ℹ️ ", "OK": "✅ ", "ERROR": "❌ ", "WARNING": "⚠️ "}
            print(f"{prefijos.get(nivel, '')} {mensaje}")
    
    def cargar_datos(self):
        """Carga todos los datos SNIES desde URLs remotas (una sola vez)"""
        if self.datos:
            self.log("Datos ya están cargados, usando caché", "INFO")
            return
        
        self.log("Cargando datos SNIES desde repositorio remoto...", "INFO")
        
        try:
            for nombre, url in self.URLS.items():
                self.log(f"Descargando {nombre}...", "INFO")
                self.datos[nombre] = pd.read_parquet(url)
                self.log(f"{nombre}: {len(self.datos[nombre])} registros", "OK")
        except Exception as e:
            self.log(f"Error cargando datos: {e}", "ERROR")
            raise
    
    def buscar_programa(self, programa: str) -> Dict:
        """
        Busca un programa específico y procesa sus datos
        
        Args:
            programa: Nombre del programa a buscar
            
        Returns:
            Diccionario con datos procesados
        """
        self.log(f"\n{'='*60}", "INFO")
        self.log(f"Buscando programa: '{programa}'", "INFO")
        self.log(f"{'='*60}", "INFO")
        
        # Paso 1: Buscar equivalentes
        programa_palabras = set(programa.lower().split())
        programas_df = self.datos['programas']
        
        equivalentes = []
        for prg in programas_df['PROGRAMA_ACADEMICO'].unique():
            palabras_prg = set(str(prg).lower().split())
            # Calcular similitud: cuántas palabras clave coinciden
            similitud = len(programa_palabras.intersection(palabras_prg)) / len(programa_palabras)
            
            if similitud >= 0.8:
                equivalentes.append(prg)
        
        self.log(f"Encontrados {len(equivalentes)} programas equivalentes:", "OK")
        for i, prog in enumerate(equivalentes[:5], 1):
            self.log(f"  {i}. {prog}", "INFO")
        if len(equivalentes) > 5:
            self.log(f"  ... y {len(equivalentes) - 5} más", "INFO")
        
        # Paso 2: Filtrar datos para este programa
        programas_f = self.datos['programas'][
            self.datos['programas']['PROGRAMA_ACADEMICO'].isin(equivalentes)
        ]
        
        snies_codes = programas_f['CODIGO_SNIES'].unique()
        
        maestro_f = self.datos['maestro'][
            self.datos['maestro']['CODIGO_SNIES'].isin(snies_codes)
        ]
        
        # Paso 3: Mergear datos
        maestro_merged = maestro_f.merge(
            programas_f,
            on='CODIGO_SNIES',
            how='left'
        )
        
        maestro_merged = maestro_merged.merge(
            self.datos['oferta'],
            on=['CODIGO_SNIES', 'PERIODO'],
            how='left'
        )
        
        self.log(f"Datos procesados: {len(maestro_merged)} registros", "OK")
        
        return {
            'nombre': programa,
            'maestro': maestro_merged,
            'programas': programas_f,
            'equivalentes': equivalentes,
            'snies_codes': snies_codes,
            'palabras_clave': programa_palabras
        }
    
    def procesar_todos(self):
        """Procesa todos los programas especificados"""
        self.cargar_datos()
        
        for programa in self.programas:
            try:
                self.resultados[programa] = self.buscar_programa(programa)
            except Exception as e:
                self.log(f"Error procesando '{programa}': {e}", "ERROR")
    
    def generar_graficas(self, programa: str, output_dir='output'):
        """Genera gráficas para un programa específico"""
        if programa not in self.resultados:
            self.log(f"Programa '{programa}' no encontrado", "ERROR")
            return
        
        datos_prog = self.resultados[programa]
        maestro_procesado = datos_prog['maestro']
        
        # Crear carpeta específica para este programa
        prog_dir = Path(output_dir) / programa.replace(' ', '_')
        prog_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"Generando gráficas en '{prog_dir}'...", "INFO")
        
        try:
            self._grafica_programas_instituciones(maestro_procesado, prog_dir)
            self._grafica_costo_vs_matriculados(maestro_procesado, prog_dir)
            self._grafica_evolucion_matriculas(maestro_procesado, prog_dir)
            self._grafica_distribucion_geografica(maestro_procesado, prog_dir)
            self._grafica_estudiantes_tiempo(maestro_procesado, prog_dir)
            
            self.log(f"✅ Gráficas guardadas en '{prog_dir}'", "OK")
        except Exception as e:
            self.log(f"Error generando gráficas: {e}", "ERROR")
    
    def generar_todas_graficas(self, output_dir='output'):
        """Genera gráficas para todos los programas"""
        for programa in self.programas:
            self.generar_graficas(programa, output_dir)
    
    def _grafica_programas_instituciones(self, maestro_procesado, output_dir):
        """Gráfica 1: Número de programas e instituciones"""
        try:
            NprogNies = maestro_procesado.groupby(by='PERIODO').agg({
                'CODIGO_INSTITUCION_x': 'nunique',
                'CODIGO_SNIES': 'nunique'
            })
            
            fig, ax = plt.subplots(figsize=(12, 6))
            NprogNies.plot(ax=ax, marker='o')
            ax.set_title('Número de Programas e Instituciones en el Tiempo')
            ax.set_xlabel('Período')
            ax.set_ylabel('Cantidad')
            ax.grid(True, alpha=0.3)
            ax.legend(['Instituciones', 'Programas'])
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/01_programas_instituciones.png', dpi=300)
            plt.close()
            self.log("✅ Gráfica 1 guardada", "OK")
        except Exception as e:
            self.log(f"Error en gráfica 1: {e}", "ERROR")
    
    def _grafica_costo_vs_matriculados(self, maestro_procesado, output_dir):
        """Gráfica 2: Costo vs Promedio de matriculados"""
        try:
            maestro_copia = maestro_procesado.copy()
            maestro_copia['PROXY_PER'] = maestro_copia['PROXY_PER'].astype(int)
            
            df = maestro_copia[
                (maestro_copia['PROXY_PER'] >= 20211) & 
                (maestro_copia['PROXY_PER'] <= 20242)
            ].copy()
            
            df.loc[:, 'Nombre_ies'] = df['INSTITUCION'] + ' - ' + df['PROGRAMA_ACADEMICO']
            df = df[df['PROCESO'] == 'MATRICULADOS'].copy()
            df['CANTIDAD'] = df['CANTIDAD'].astype(int)
            df = df[['MATRICULA', 'CANTIDAD', 'Nombre_ies', 'PERIODO']]
            df = df.dropna()
            df = df[df['MATRICULA'] != 'null'].copy()
            
            if df.empty:
                self.log("Sin datos para gráfica 2", "WARNING")
                return
            
            df['MATRICULA'] = df['MATRICULA'].astype(float)
            df2 = df.groupby(by='Nombre_ies').agg({'MATRICULA': 'last', 'CANTIDAD': 'mean'})
            
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.scatter(df2['CANTIDAD'], df2['MATRICULA'], s=100, alpha=0.6)
            
            for i, txt in enumerate(df2.index):
                ax.annotate(
                    txt,
                    (df2['CANTIDAD'].iloc[i], df2['MATRICULA'].iloc[i]),
                    fontsize=7,
                    ha='center',
                    va='center',
                    alpha=0.7
                )
            
            ax.set_xlabel('Promedio de Estudiantes Matriculados')
            ax.set_ylabel('Valor Matrícula (última registrada)')
            ax.set_title('Costo vs Promedio de Matriculados')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/02_costo_vs_matriculados.png', dpi=300, bbox_inches='tight')
            plt.close()
            self.log("✅ Gráfica 2 guardada", "OK")
        except Exception as e:
            self.log(f"Error en gráfica 2: {e}", "ERROR")
    
    def _grafica_evolucion_matriculas(self, maestro_procesado, output_dir):
        """Gráfica 3: Evolución de valor de matrículas"""
        try:
            maestro_copia = maestro_procesado.copy()
            maestro_copia['PROXY_PER'] = maestro_copia['PROXY_PER'].astype(int)
            
            df = maestro_copia[
                (maestro_copia['PROXY_PER'] >= 20211) & 
                (maestro_copia['PROXY_PER'] <= 20242)
            ].copy()
            
            df.loc[:, 'Nombre_ies'] = df['INSTITUCION'] + ' - ' + df['PROGRAMA_ACADEMICO']
            df = df[df['PROCESO'] == 'MATRICULADOS'].copy()
            df['CANTIDAD'] = df['CANTIDAD'].astype(int)
            df = df[['MATRICULA', 'CANTIDAD', 'Nombre_ies', 'PERIODO']]
            df = df.dropna()
            df = df[df['MATRICULA'] != 'null'].copy()
            
            if df.empty:
                self.log("Sin datos para gráfica 3", "WARNING")
                return
            
            df['MATRICULA'] = df['MATRICULA'].astype(float)
            
            valor = pd.pivot_table(
                df,
                index='Nombre_ies',
                columns='PERIODO',
                values='MATRICULA',
                aggfunc='mean',
                fill_value=0
            )
            
            fig, ax = plt.subplots(figsize=(14, 8))
            valor.T.plot(ax=ax, alpha=0.7)
            ax.set_title('Evolución del Valor de Matrículas')
            ax.set_xlabel('Período')
            ax.set_ylabel('Valor Matrícula')
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/03_evolucion_matriculas.png', dpi=300, bbox_inches='tight')
            plt.close()
            self.log("✅ Gráfica 3 guardada", "OK")
        except Exception as e:
            self.log(f"Error en gráfica 3: {e}", "ERROR")
    
    def _grafica_distribucion_geografica(self, maestro_procesado, output_dir):
        """Gráfica 4: Distribución por departamento y municipio"""
        try:
            maestro_copia = maestro_procesado.copy()
            maestro_copia['PROXY_PER'] = maestro_copia['PROXY_PER'].astype(int)
            
            df = maestro_copia[
                (maestro_copia['PROXY_PER'] >= 20211) & 
                (maestro_copia['PROXY_PER'] <= 20242)
            ].copy()
            
            df = df[df['PROCESO'] == 'MATRICULADOS'].copy()
            df['CANTIDAD'] = df['CANTIDAD'].astype(int)
            
            porDpto = df.groupby('DEPARTAMENTO_PROGRAMA').agg({
                'CODIGO_SNIES': 'nunique'
            }).sort_values(by='CODIGO_SNIES', ascending=False)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            porDpto.plot(kind='bar', ax=ax1, color='steelblue')
            ax1.set_title('Número de Programas por Departamento')
            ax1.set_xlabel('Departamento')
            ax1.set_ylabel('Cantidad de Programas')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3, axis='y')
            
            porMpio = df.groupby('MUNICIPIO_PROGRAMA').agg({
                'CODIGO_SNIES': 'nunique'
            }).sort_values(by='CODIGO_SNIES', ascending=False).head(15)
            
            porMpio.plot(kind='bar', ax=ax2, color='coral')
            ax2.set_title('Top 15 Municipios con más Programas')
            ax2.set_xlabel('Municipio')
            ax2.set_ylabel('Cantidad de Programas')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/04_distribucion_geografica.png', dpi=300, bbox_inches='tight')
            plt.close()
            self.log("✅ Gráfica 4 guardada", "OK")
        except Exception as e:
            self.log(f"Error en gráfica 4: {e}", "ERROR")
    
    def _grafica_estudiantes_tiempo(self, maestro_procesado, output_dir):
        """Gráfica 5: Número de estudiantes en el tiempo"""
        try:
            maestro_copia = maestro_procesado.copy()
            maestro_copia = maestro_copia[maestro_copia['CANTIDAD'] != 'null']
            maestro_copia['CANTIDAD'] = maestro_copia['CANTIDAD'].astype(int)
            
            num = pd.pivot_table(
                maestro_copia,
                index='PERIODO',
                columns='PROCESO',
                values='CANTIDAD',
                fill_value=0,
                aggfunc='sum'
            )
            
            fig, axes = plt.subplots(len(num.columns), 1, figsize=(12, 10), sharex=True)
            
            if len(num.columns) == 1:
                axes = [axes]
            
            for i, col in enumerate(num.columns):
                axes[i].plot(num[col], marker='o', linewidth=2, markersize=6, color='steelblue')
                axes[i].set_title(f'Estudiantes: {col}', fontsize=12, fontweight='bold')
                axes[i].grid(True, alpha=0.3)
                axes[i].set_ylabel('Cantidad')
                
                if i < len(num.columns) - 1:
                    axes[i].label_outer()
                else:
                    axes[i].set_xlabel('Período')
                    plt.setp(axes[i].xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/05_estudiantes_tiempo.png', dpi=300, bbox_inches='tight')
            plt.close()
            self.log("✅ Gráfica 5 guardada", "OK")
        except Exception as e:
            self.log(f"Error en gráfica 5: {e}", "ERROR")
    
    def mostrar_resumen(self):
        """Muestra un resumen de todos los programas procesados"""
        print("\n" + "="*80)
        print("📊 RESUMEN DEL ANÁLISIS")
        print("="*80)
        
        for programa, datos in self.resultados.items():
            print(f"\n✅ {programa.upper()}")
            print(f"   - Programas encontrados: {len(datos['equivalentes'])}")
            print(f"   - Registros procesados: {len(datos['maestro'])}")
            print(f"   - Códigos SNIES: {len(datos['snies_codes'])}")
            print(f"   - Instituciones: {datos['maestro']['CODIGO_INSTITUCION_x'].nunique()}")
        
        print("\n" + "="*80 + "\n")
    
    def comparar_programas(self) -> pd.DataFrame:
        """
        Compara múltiples programas
        
        Returns:
            DataFrame con comparativa
        """
        if len(self.resultados) < 2:
            self.log("Se necesitan al menos 2 programas para comparar", "WARNING")
            return None
        
        comparativa = []
        for programa, datos in self.resultados.items():
            maestro = datos['maestro']
            comparativa.append({
                'Programa': programa,
                'Programas Equivalentes': len(datos['equivalentes']),
                'Registros': len(maestro),
                'Instituciones': maestro['CODIGO_INSTITUCION_x'].nunique(),
                'Códigos SNIES': len(datos['snies_codes']),
                'Períodos': maestro['PERIODO'].nunique(),
                'Departamentos': maestro['DEPARTAMENTO_PROGRAMA'].nunique()
            })
        
        df_comparativa = pd.DataFrame(comparativa)
        return df_comparativa
    
    def generar_grafica_comparativa(self, output_dir='output'):
        """Genera gráfica comparativa de múltiples programas"""
        if len(self.resultados) < 2:
            self.log("Se necesitan al menos 2 programas para generar comparativa", "WARNING")
            return
        
        df_comp = self.comparar_programas()
        
        # Graficar comparativa
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Gráfica 1: Programas equivalentes
        axes[0, 0].bar(df_comp['Programa'], df_comp['Programas Equivalentes'], color='steelblue')
        axes[0, 0].set_title('Programas Equivalentes Encontrados')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Gráfica 2: Registros
        axes[0, 1].bar(df_comp['Programa'], df_comp['Registros'], color='coral')
        axes[0, 1].set_title('Total de Registros Procesados')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Gráfica 3: Instituciones
        axes[1, 0].bar(df_comp['Programa'], df_comp['Instituciones'], color='seagreen')
        axes[1, 0].set_title('Instituciones que Ofrecen el Programa')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Gráfica 4: Cobertura geográfica
        axes[1, 1].bar(df_comp['Programa'], df_comp['Departamentos'], color='orange')
        axes[1, 1].set_title('Departamentos con Oferta')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        Path(output_dir).mkdir(exist_ok=True)
        plt.savefig(f'{output_dir}/00_comparativa_programas.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"✅ Gráfica comparativa guardada en '{output_dir}/00_comparativa_programas.png'", "OK")
        
        # Guardar tabla comparativa en CSV
        df_comp.to_csv(f'{output_dir}/comparativa_programas.csv', index=False)
        self.log(f"✅ Tabla comparativa guardada en '{output_dir}/comparativa_programas.csv'", "OK")
        
        print("\n📊 TABLA COMPARATIVA:")
        print(df_comp.to_string(index=False))
    
    def ejecutar(self, output_dir='output', generar_comparativa=True):
        """Ejecuta todo el pipeline completo"""
        try:
            self.procesar_todos()
            self.generar_todas_graficas(output_dir)
            
            if generar_comparativa and len(self.programas) > 1:
                self.generar_grafica_comparativa(output_dir)
            
            self.mostrar_resumen()
            self.log("¡Procesamiento completado exitosamente!", "OK")
            return self.resultados
        except Exception as e:
            self.log(f"Error durante la ejecución: {e}", "ERROR")
            raise


def main():
    """Función principal con manejo de argumentos"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Análisis de Programas Académicos SNIES',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Un programa
  python lector_tablas_snies.py "DOCTORADO CIENCIAS SOCIALES"
  
  # Múltiples programas
  python lector_tablas_snies.py "DOCTORADO CIENCIAS SOCIALES" "MAESTRIA ADMINISTRACION"
  
  # Desde archivo
  python lector_tablas_snies.py --file programas.txt
  
  # Modo interactivo
  python lector_tablas_snies.py --interactive
        """
    )
    
    parser.add_argument(
        'programas',
        nargs='*',
        help='Nombres de programas a buscar'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Archivo con lista de programas (uno por línea)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Modo interactivo'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='Carpeta de salida (default: output)'
    )
    parser.add_argument(
        '--no-comparativa',
        action='store_true',
        help='No generar gráfica comparativa'
    )
    
    args = parser.parse_args()
    
    # Determinar qué programas procesar
    programas_a_procesar = []
    
    if args.interactive:
        print("\n" + "="*60)
        print("🔍 MODO INTERACTIVO")
        print("="*60)
        print("Ingresa los programas a buscar (uno por línea)")
        print("Escribe 'listo' cuando termines\n")
        
        while True:
            prog = input("Programa: ").strip()
            if prog.lower() == 'listo':
                break
            if prog:
                programas_a_procesar.append(prog)
    
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                programas_a_procesar = [line.strip() for line in f if line.strip()]
            print(f"✅ Cargados {len(programas_a_procesar)} programas desde '{args.file}'")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {args.file}")
            sys.exit(1)
    
    elif args.programas:
        programas_a_procesar = args.programas
    
    else:
        programas_a_procesar = ['DOCTORADO CIENCIAS SOCIALES']
        print("ℹ️  Usando programa por defecto: DOCTORADO CIENCIAS SOCIALES")
    
    # Crear lector y ejecutar
    lector = LectorSNIES(
        programas=programas_a_procesar,
        verbose=True
    )
    
    lector.ejecutar(
        output_dir=args.output,
        generar_comparativa=not args.no_comparativa
    )


if __name__ == '__main__':
    main()