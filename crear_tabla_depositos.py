#!/usr/bin/env python
"""
📋 SCRIPT PARA CREAR TABLA DEPÓSITOS BANCARIOS
Autor: Sistema Panadería SaaS
"""

import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar después de configurar path
from models import db, DepositoBancario

def crear_tabla_depositos():
    """Crea la tabla depositos_bancarios en todas las bases de datos necesarias"""
    
    print("🚀 INICIANDO CREACIÓN DE TABLA DEPÓSITOS BANCARIOS")
    print("="*60)
    
    # Configurar aplicación Flask temporal
    app = Flask(__name__)
    
    # 1. Primero crear en base de datos principal
    print("\n1. 📊 Creando tabla en base de datos PRINCIPAL...")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///panaderia.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'principal': 'sqlite:///panaderia.db'
    }
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Crear todas las tablas definidas en models
            db.create_all()
            print("✅ Tablas creadas en base de datos principal")
            
            # Verificar si la tabla existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            
            print(f"📋 Tablas en base de datos principal: {len(tablas)}")
            for tabla in tablas:
                print(f"   - {tabla}")
                
        except Exception as e:
            print(f"❌ Error al crear tablas en principal: {e}")
    
    # 2. Crear en base de datos del tenant (panaderia_principal.db)
    print("\n2. 🏪 Creando tabla en base de datos TENANT (panaderia_principal.db)...")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases_tenants/panaderia_principal.db'
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas en base de datos tenant")
            
            # Verificar específicamente la tabla depositos_bancarios
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            
            print(f"📋 Tablas en base de datos tenant: {len(tablas)}")
            for tabla in tablas:
                print(f"   - {tabla}")
                
            if 'depositos_bancarios' in tablas:
                print("🎉 ¡TABLA 'depositos_bancarios' CREADA EXITOSAMENTE!")
                
                # Mostrar estructura de la tabla
                print("\n📐 Estructura de la tabla 'depositos_bancarios':")
                with db.engine.connect() as conn:
                    result = conn.execute(text("PRAGMA table_info(depositos_bancarios);"))
                    for row in result:
                        print(f"   - {row[1]} ({row[2]}) {'NOT NULL' if row[3] else ''}")
                        
            else:
                print("❌ La tabla 'depositos_bancarios' no se creó automáticamente")
                print("   Creando manualmente...")
                
                # Crear tabla manualmente
                crear_tabla_manual()
                
        except Exception as e:
            print(f"❌ Error al crear tablas en tenant: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("📋 RESUMEN DE LA OPERACIÓN:")
    print("="*60)
    
    # Verificar nuevamente ambas bases de datos
    verificar_tablas_final()

def crear_tabla_manual():
    """Crea la tabla manualmente si SQLAlchemy no lo hace"""
    try:
        import sqlite3
        
        # Conexión a la base de datos tenant
        conn = sqlite3.connect('databases_tenants/panaderia_principal.db')
        cursor = conn.cursor()
        
        # SQL para crear la tabla depositos_bancarios
        sql = """
        CREATE TABLE IF NOT EXISTS depositos_bancarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panaderia_id INTEGER NOT NULL,
            fecha_deposito DATE NOT NULL,
            monto FLOAT NOT NULL,
            descripcion VARCHAR(200),
            referencia VARCHAR(50),
            cuenta_bancaria VARCHAR(100),
            metodo_deposito VARCHAR(50),
            estado VARCHAR(20) DEFAULT 'REGISTRADO',
            fecha_conciliacion DATE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (panaderia_id) REFERENCES panaderias (id)
        );
        """
        
        cursor.execute(sql)
        
        # Crear índices para mejor performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_depositos_panaderia ON depositos_bancarios(panaderia_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_depositos_fecha ON depositos_bancarios(fecha_deposito);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_depositos_estado ON depositos_bancarios(estado);")
        
        conn.commit()
        conn.close()
        
        print("✅ Tabla 'depositos_bancarios' creada manualmente")
        
    except Exception as e:
        print(f"❌ Error al crear tabla manualmente: {e}")

def verificar_tablas_final():
    """Verifica que las tablas existan en ambas bases de datos"""
    print("\n🔍 VERIFICACIÓN FINAL DE TABLAS:")
    
    bases_datos = [
        ('Principal', 'panaderia.db'),
        ('Tenant', 'databases_tenants/panaderia_principal.db')
    ]
    
    for nombre, ruta in bases_datos:
        if os.path.exists(ruta):
            try:
                import sqlite3
                conn = sqlite3.connect(ruta)
                cursor = conn.cursor()
                
                # Verificar si existe la tabla
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='depositos_bancarios';")
                existe = cursor.fetchone()
                
                if existe:
                    print(f"✅ {nombre}: Tabla 'depositos_bancarios' EXISTE")
                    
                    # Contar registros si hay
                    cursor.execute("SELECT COUNT(*) FROM depositos_bancarios;")
                    count = cursor.fetchone()[0]
                    print(f"   📊 Registros: {count}")
                    
                else:
                    print(f"❌ {nombre}: Tabla 'depositos_bancarios' NO EXISTE")
                    
                conn.close()
                
            except Exception as e:
                print(f"❌ {nombre}: Error al verificar: {e}")
        else:
            print(f"❌ {nombre}: Base de datos '{ruta}' no encontrada")

def insertar_deposito_prueba():
    """Inserta un depósito de prueba para verificar que funciona"""
    print("\n🧪 INSERTANDO DEPÓSITO DE PRUEBA:")
    
    try:
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect('databases_tenants/panaderia_principal.db')
        cursor = conn.cursor()
        
        # Insertar un depósito de prueba
        sql = """
        INSERT INTO depositos_bancarios 
        (panaderia_id, fecha_deposito, monto, descripcion, referencia, 
         cuenta_bancaria, metodo_deposito, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        valores = (
            3,  # panaderia_id (debe coincidir con tu usuario admin_3)
            '2025-12-01',
            1000.50,
            'Depósito de prueba diagnóstico',
            'TEST-001',
            'Cuenta Principal',
            'efectivo',
            'REGISTRADO'
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        
        # Obtener el ID insertado
        deposito_id = cursor.lastrowid
        
        print(f"✅ Depósito de prueba insertado exitosamente")
        print(f"   ID: {deposito_id}")
        print(f"   Monto: $1000.50")
        print(f"   Fecha: 2025-12-01")
        
        # Verificar que se insertó
        cursor.execute("SELECT COUNT(*) FROM depositos_bancarios;")
        count = cursor.fetchone()[0]
        print(f"   Total depósitos en tabla: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al insertar depósito de prueba: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🔧 CREADOR DE TABLA DEPÓSITOS BANCARIOS - SISTEMA PANADERÍA")
    print("="*60)
    
    # Preguntar qué acciones realizar
    print("\nSelecciona las acciones a realizar:")
    print("1. Solo crear la tabla")
    print("2. Crear tabla + insertar depósito de prueba")
    print("3. Solo verificar estado actual")
    
    opcion = input("\nOpción (1-3): ").strip()
    
    if opcion == '1':
        crear_tabla_depositos()
    elif opcion == '2':
        crear_tabla_depositos()
        insertar_deposito_prueba()
    elif opcion == '3':
        verificar_tablas_final()
    else:
        print("❌ Opción no válida")