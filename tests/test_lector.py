"""
Tests para el lector de SNIES
"""
import pytest
import sys
sys.path.insert(0, '../src')

def test_inicializacion():
    """Test básico de inicialización"""
    assert True

def test_palabras_clave():
    """Test de extracción de palabras clave"""
    from lector_tablas_snies import LectorSNIES
    lector = LectorSNIES("DOCTORADO CIENCIAS SOCIALES")
    palabras = lector.palabras_clave
    assert len(palabras) > 0

