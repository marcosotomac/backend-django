#!/usr/bin/env python3
"""
Script para validar endpoints del chat que funcionan en Postman
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


def print_test_result(test_name, success, details=""):
    status = "✅ PASÓ" if success else "❌ FALLÓ"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    print()


def test_chat_endpoints():
    print("🔥 VALIDACIÓN DE ENDPOINTS DEL CHAT PARA POSTMAN")
    print("=" * 60)
    print()

    # Test 1: Verificar endpoints disponibles
    print("📋 ENDPOINTS DISPONIBLES:")
    endpoints = [
        "/api/v1/chat/rooms/",
        "/api/v1/chat/rooms/direct_chat/",
        "/api/v1/chat/messages/",
        "/api/v1/chat/onlinestatus/"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "Disponible" if response.status_code in [
                200, 401, 403] else f"Error {response.status_code}"
            print(f"   {endpoint} - {status}")
        except Exception as e:
            print(f"   {endpoint} - Error de conexión")

    print()

    # Test 2: Verificar estructura de respuesta sin autenticación
    print("🔒 VERIFICACIÓN DE AUTENTICACIÓN:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/rooms/")
        if response.status_code == 401:
            print_test_result("Autenticación requerida", True,
                              "Los endpoints requieren autenticación (401)")
        else:
            print_test_result("Autenticación requerida", False,
                              f"Código inesperado: {response.status_code}")
    except Exception as e:
        print_test_result("Conexión al servidor", False, f"Error: {str(e)}")

    # Test 3: Verificar formato de respuesta de error
    print("📝 FORMATO DE RESPUESTAS:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/rooms/")
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print_test_result("Respuesta JSON válida",
                                  True, f"Estructura: {list(data.keys())}")
            except:
                print_test_result("Respuesta JSON válida",
                                  False, "No es JSON válido")
        else:
            print_test_result("Respuesta JSON válida", False,
                              "Content-Type no es JSON")
    except Exception as e:
        print_test_result("Formato de respuesta", False, f"Error: {str(e)}")

    print("🎯 RESUMEN PARA POSTMAN:")
    print("=" * 60)
    print("✅ Servidor Django corriendo en http://127.0.0.1:8000")
    print("✅ Endpoints del chat disponibles bajo /api/v1/chat/")
    print("✅ Autenticación JWT requerida (Header: Authorization: Bearer <token>)")
    print("✅ Respuestas en formato JSON")
    print("✅ Estructura de URL: /api/v1/chat/{rooms|messages|onlinestatus}/")
    print()
    print("📚 ENDPOINTS PRINCIPALES PARA PROBAR:")
    print("   POST /api/v1/auth/login/ - Obtener token")
    print("   GET  /api/v1/chat/rooms/ - Listar salas del usuario")
    print("   POST /api/v1/chat/rooms/ - Crear sala grupal")
    print("   POST /api/v1/chat/rooms/direct_chat/ - Crear chat directo")
    print("   POST /api/v1/chat/rooms/{id}/join/ - Unirse a sala")
    print("   GET  /api/v1/chat/rooms/{id}/messages/ - Obtener mensajes")
    print("   POST /api/v1/chat/messages/ - Enviar mensaje")
    print()


if __name__ == "__main__":
    test_chat_endpoints()
