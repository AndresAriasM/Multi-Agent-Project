"""
Script principal para ejecutar el análisis completo
"""
import argparse
from lector_tablas_snies import LectorSNIES
from agentes.coordinador import CoordinadorAgentes
from presentacion.generador_powerpoint import GeneradorPowerPoint

def main():
    parser = argparse.ArgumentParser(description="Análisis de Oportunidad SNIES")
    parser.add_argument("--programa", type=str, default="DOCTORADO CIENCIAS SOCIALES",
                        help="Nombre del programa a analizar")
    parser.add_argument("--output", type=str, default="../output/reporte_final.pptx",
                        help="Ruta del archivo de salida PowerPoint")
    
    args = parser.parse_args()
    
    print(f"🔍 Analizando programa: {args.programa}")
    print(f"📊 Cargando datos SNIES...")
    
    # Cargar datos
    lector = LectorSNIES(args.programa)
    datos = lector.procesar()
    
    # Ejecutar agentes
    print("🤖 Ejecutando sistema de agentes...")
    coordinador = CoordinadorAgentes(datos)
    resultados_agentes = coordinador.ejecutar()
    
    # Generar presentación
    print("📈 Generando presentación PowerPoint...")
    generador = GeneradorPowerPoint(datos, resultados_agentes)
    generador.crear_presentacion(args.output)
    
    print(f"✅ Presentación generada: {args.output}")

if __name__ == "__main__":
    main()
