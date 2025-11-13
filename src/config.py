"""
Configuración centralizada del proyecto
Ubicación: src/config.py
"""

import os
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except:
    pass

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Rutas de salida
SNIES_MAESTRO_URL = os.getenv("SNIES_MAESTRO_URL", "https://robertohincapie.com/data/snies/MAESTRO.parquet")
SNIES_OFERTA_URL = os.getenv("SNIES_OFERTA_URL", "https://robertohincapie.com/data/snies/OFERTA.parquet")
SNIES_PROGRAMAS_URL = os.getenv("SNIES_PROGRAMAS_URL", "https://robertohincapie.com/data/snies/PROGRAMAS.parquet")
SNIES_IES_URL = os.getenv("SNIES_IES_URL", "https://robertohincapie.com/data/snies/IES.parquet")

# Configuración de agentes
AGENTES_ENABLED = os.getenv("AGENTES_ENABLED", "true").lower() == "true"
AGENTES_TIMEOUT = int(os.getenv("AGENTES_TIMEOUT", "300"))

# Rutas de salida
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "pptx")

# Crear carpeta de output si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validar_config():
    """Valida que la configuración esté completa"""
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY no está configurada en .env")


def get_openai_client():
    """Obtiene el cliente OpenAI configurado para Azure"""
    from openai import AzureOpenAI
    
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY no está configurada")
    
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-02-15-preview",
        azure_endpoint="https://pnl-maestria.openai.azure.com"
    )
    return client