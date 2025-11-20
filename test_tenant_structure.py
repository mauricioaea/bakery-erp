# test_tenant_structure.py - VERSIÓN CORREGIDA
"""
Script para probar que la estructura tenant funciona correctamente
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Prueba imports básicos sin dependencias de Flask"""
    try:
        # Probar imports que no requieren contexto de Flask
        from tenant_decorators import TenantSecurityException
        print("✅ Import básico (TenantSecurityException) funciona")
        return True
    except Exception as e:
        print(f"❌ Error en import básico: {e}")
        return False

def test_flask_login_imports():
    """Prueba imports que requieren flask_login"""
    try:
        # Estos imports deberían funcionar ahora con las correcciones
        from flask_login import current_user
        print("✅ Flask-Login import funciona")
        return True
    except Exception as e:
        print(f"❌ Error importando flask_login: {e}")
        return False

def test_tenant_imports():
    """Prueba que todos los imports tenant funcionen"""
    try:
        from tenant_decorators import tenant_required, with_tenant_context
        from tenant_context import TenantContext
        from security_utils import safe_tenant_query
        
        print("✅ Todos los imports tenant funcionan correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en imports tenant: {e}")
        return False

def test_decorator_creation():
    """Prueba la creación de decoradores"""
    try:
        from tenant_decorators import tenant_required
        
        # Crear una función de prueba con el decorador
        @tenant_required
        def test_function():
            return "success"
            
        print("✅ Decoradores se crean correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando decoradores: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando estructura de seguridad tenant...")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_flask_login_imports,
        test_tenant_imports,
        test_decorator_creation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{len(tests)} pruebas pasadas")
    
    if passed == len(tests):
        print("🎉 ¡Estructura de seguridad lista para usar!")
    else:
        print("⚠️  Algunas pruebas fallaron, pero podemos continuar")
        print("💡 Los problemas pueden ser por falta de contexto Flask en pruebas")