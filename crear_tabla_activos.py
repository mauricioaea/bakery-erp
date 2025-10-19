#!/usr/bin/env python3
"""
📋 SCRIPT: CREAR TABLA DE ACTIVOS FIJOS
🎯 OBJETIVO: Agregar la nueva tabla 'activos_fijos' a la base de datos existente
⚠️ IMPORTANTE: Esto NO borra tus datos existentes, solo agrega una tabla nueva
"""

import sys
import os

# 🔧 CONFIGURACIÓN: Agregar el directorio actual al path para encontrar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 📦 IMPORTAR: Traemos la aplicación y la base de datos de tus archivos existentes
from app import app, db
from models import ActivoFijo

def crear_tabla_activos():
    """
    🚀 FUNCIÓN PRINCIPAL: Crea la tabla de activos fijos
    """
    print("=" * 50)
    print("🚀 INICIANDO CREACIÓN DE TABLA DE ACTIVOS FIJOS")
    print("=" * 50)
    
    try:
        # 🔐 ABRIR CONTEXTO: Necesario para trabajar con la base de datos
        with app.app_context():
            print("📊 Conectando a la base de datos...")
            
            # 🛠️ CREAR TABLAS: Esto crea SOLO las tablas que no existen
            db.create_all()
            
            print("✅ ¡ÉXITO! Tabla de activos fijos creada correctamente")
            print("")
            print("📋 ESTRUCTURA DE LA NUEVA TABLA:")
            print("   ┌─────────────────────────────────────────")
            print("   │ 📦 activos_fijos")
            print("   ├─────────────────────────────────────────")
            print("   │ • id (Llave primaria)")
            print("   │ • nombre (Nombre del activo)")
            print("   │ • categoria (Tipo: maquinaria, mobiliario, etc.)")
            print("   │ • descripcion (Descripción detallada)")
            print("   │ • numero_serie (Número de serie/placa)")
            print("   │ • fecha_compra (Fecha de adquisición)")
            print("   │ • proveedor (Quién lo vendió)")
            print("   │ • valor_compra (Precio de compra)")
            print("   │ • metodo_pago (Forma de pago)")
            print("   │ • vida_util (Años de vida útil)")
            print("   │ • valor_residual (Valor al final de vida útil)")
            print("   │ • metodo_depreciacion (Método de depreciación)")
            print("   │ • ubicacion (Dónde está ubicado)")
            print("   │ • estado (ACTIVO/MANTENIMIENTO/BAJA)")
            print("   │ • responsable (Quién lo usa)")
            print("   │ • fecha_registro (Fecha de registro en sistema)")
            print("   │ • fecha_baja (Fecha de baja)")
            print("   └─────────────────────────────────────────")
            print("")
            print("💡 La tabla está lista para usar. Puedes registrar activos.")
            
    except Exception as e:
        print("❌ ERROR: No se pudo crear la tabla")
        print(f"   Detalles: {e}")
        print("")
        print("🔧 SOLUCIÓN: Verifica que:")
        print("   • El archivo models.py esté correcto")
        print("   • La base de datos panaderia.db exista")
        print("   • No haya errores de sintaxis en los modelos")

# 🎯 EJECUCIÓN: Esto se ejecuta solo cuando corres el script directamente
if __name__ == "__main__":
    print("")
    crear_tabla_activos()
    print("")
    print("=" * 50)
    print("🎉 PROCESO COMPLETADO")
    print("=" * 50)