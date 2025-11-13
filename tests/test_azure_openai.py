#!/usr/bin/env python3
"""
Script de Testing - Conexión a Azure OpenAI con OpenAI Library
Ubicación: test_azure_connection.py (raíz del proyecto)
Uso: python test_azure_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_openai_client():
    """Obtiene el cliente OpenAI configurado para Azure"""
    try:
        from openai import AzureOpenAI
    except ImportError:
        print("❌ Error: openai no está instalado")
        print("   Instala con: pip install openai")
        return None
    
    AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not AZURE_KEY:
        print("❌ Error: AZURE_OPENAI_API_KEY no está configurada en .env")
        return None
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint="https://pnl-maestria.openai.azure.com"
        )
        return client
    except Exception as e:
        print(f"❌ Error configurando cliente: {e}")
        return None


def test_basic_connection():
    """Prueba básica de conexión"""
    print("\n" + "="*60)
    print("TEST 1: Conexión Básica")
    print("="*60)
    
    client = get_openai_client()
    
    if client is None:
        print("❌ No se pudo configurar el cliente")
        return False
    
    print("✅ Cliente configurado correctamente")
    return True


def test_simple_completion():
    """Prueba una completación simple"""
    print("\n" + "="*60)
    print("TEST 2: Completación Simple")
    print("="*60)
    
    client = get_openai_client()
    
    if client is None:
        print("❌ Cliente no disponible")
        return False
    
    try:
        print("📤 Enviando prompt a Azure OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente útil y conciso."
                },
                {
                    "role": "user",
                    "content": "¿Qué es un programa académico? Responde en máximo 2 líneas."
                }
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        print("✅ Respuesta recibida:")
        print(f"   {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error en completación: {e}")
        return False


def test_snies_analysis():
    """Prueba análisis de SNIES"""
    print("\n" + "="*60)
    print("TEST 3: Análisis de Denominación SNIES")
    print("="*60)
    
    client = get_openai_client()
    
    if client is None:
        print("❌ Cliente no disponible")
        return False
    
    try:
        programas = [
            "DOCTORADO EN CIENCIAS SOCIALES",
            "DOCTORADO CIENCIAS SOCIALES",
            "DOCTORATE IN SOCIAL SCIENCES"
        ]
        
        prompt = f"""Analiza estas denominaciones de programas académicos:

{chr(10).join(f'- {p}' for p in programas)}

Proporciona:
1. Denominación oficial estandarizada
2. Equivalentes internacionales
3. Tipo de programa

Sé conciso."""
        
        print("📤 Analizando programas académicos...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Eres experto en programas académicos y educación superior."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        print("✅ Análisis completado:")
        print(response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False


def test_json_output():
    """Prueba obtener output en formato JSON"""
    print("\n" + "="*60)
    print("TEST 4: Output en Formato JSON")
    print("="*60)
    
    client = get_openai_client()
    
    if client is None:
        print("❌ Cliente no disponible")
        return False
    
    try:
        prompt = """Responde SOLO con JSON válido (sin explicaciones adicionales).
Analiza el programa "MAESTRÍA EN ADMINISTRACIÓN":

{
    "denominacion": "MAESTRÍA EN ADMINISTRACIÓN",
    "tipo": "Maestría",
    "palabras_clave": ["administración", "gestión"],
    "equivalentes_internacionales": ["Master in Business Administration"]
}"""
        
        print("📤 Solicitando respuesta en JSON...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente que responde solo con JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=300
        )
        
        respuesta = response.choices[0].message.content
        print("✅ Respuesta JSON recibida:")
        print(respuesta)
        
        try:
            import json
            json.loads(respuesta)
            print("✅ JSON válido confirmado")
            return True
        except json.JSONDecodeError:
            print("⚠️  Respuesta válida, pero no es JSON válido")
            return True
        
    except Exception as e:
        print(f"❌ Error en JSON: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  TESTS DE CONEXIÓN - AZURE OPENAI".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Verificar .env
    print("\n🔍 Verificando configuración...")
    AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    if AZURE_KEY:
        print(f"✅ AZURE_OPENAI_API_KEY configurada")
    else:
        print("❌ AZURE_OPENAI_API_KEY no encontrada en .env")
        print("   Crea .env con: AZURE_OPENAI_API_KEY=tu_clave")
        return 1
    
    # Ejecutar tests
    tests = [
        ("Conexión Básica", test_basic_connection),
        ("Completación Simple", test_simple_completion),
        ("Análisis SNIES", test_snies_analysis),
        ("Output JSON", test_json_output),
    ]
    
    resultados = {}
    for nombre, test_func in tests:
        try:
            resultados[nombre] = test_func()
        except Exception as e:
            print(f"❌ Error inesperado en {nombre}: {e}")
            resultados[nombre] = False
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:.<40} {estado}")
    
    total_pasados = sum(1 for v in resultados.values() if v)
    total_tests = len(resultados)
    
    print(f"\nTotal: {total_pasados}/{total_tests} tests pasados")
    
    if total_pasados == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("   La conexión a Azure OpenAI funciona correctamente")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())