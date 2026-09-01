#!/usr/bin/env python3
"""
MIDDLEWARE SAAS - Detección de Tenant y Conexión Dinámica
"""

import sqlite3
import os
import shutil
from pathlib import Path
from flask import request, g, current_app
import re

class GestorTenants:
    def __init__(self, app=None):
        self.app = app
        self.tenant_master_db = 'tenant_master.db'
        self.databases_dir = 'databases_tenants'
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar la aplicación con el middleware SaaS"""
        self.app = app
        
    def detectar_y_configurar_tenant(self):
        """Detectar el tenant y configurar la conexión a BD"""
        print(f"\n🔍 MIDDLEWARE DEBUG - INICIANDO DETECCIÓN:")
        print(f"   Request URL: {request.url if request else 'No request'}")
        print(f"   Request Host: {request.host if request else 'No request'}")
        print(f"   Request Args: {dict(request.args) if request else 'No request'}")
        
        # Obtener información del tenant desde el subdominio o parámetros
        tenant_info = self.obtener_tenant_desde_request()
        
        print(f"🔍 MIDDLEWARE DEBUG - Tenant info: {tenant_info}")
        
        if not tenant_info:
            # Si no se detecta tenant, usar el principal por defecto
            tenant_info = {
                'id': 1,
                'nombre': 'Panadería Principal',
                'subdominio': 'principal',
                'base_datos': 'panaderia_principal.db'
            }
            print(f"🔍 MIDDLEWARE DEBUG - Usando tenant por defecto: {tenant_info}")
        
        # Configurar la conexión a la BD del tenant en el contexto global
        g.tenant = tenant_info
        g.db_path = os.path.join(self.databases_dir, tenant_info['base_datos'])
        
        print(f"🔍 MIDDLEWARE DEBUG - Configurado:")
        print(f"   Tenant: {tenant_info['nombre']}")
        print(f"   BD Path: {g.db_path}")
        print(f"   Tenant ID: {tenant_info['id']}")
    
    def obtener_tenant_desde_request(self):
        """Obtener información del tenant basado en la request"""
        # 🆕 ESTRATEGIA 1: Por sesión (si usuario ya logueado)
        from flask import session
        if session.get('tenant_subdominio'):
            tenant_subdominio = session['tenant_subdominio']
            print(f"🔍 MIDDLEWARE: Usando tenant de sesión: {tenant_subdominio}")
            return self.obtener_tenant_desde_bd(tenant_subdominio)
        
        # Estrategia 2: Por subdominio (para producción)
        subdominio = self.extraer_subdominio(request.host)
        
        # Estrategia 3: Por parámetro de consulta (para desarrollo)
        tenant_param = request.args.get('tenant', None)
        
        # Estrategia 4: Por header HTTP (para APIs)
        tenant_header = request.headers.get('X-Tenant-ID', None)
        
        tenant_identificador = subdominio or tenant_param or tenant_header
        
        if tenant_identificador:
            return self.obtener_tenant_desde_bd(tenant_identificador)
        
        return None
    
    def extraer_subdominio(self, host):
        """Extraer subdominio del host"""
        # Para desarrollo local: localhost:5000 -> no hay subdominio
        if 'localhost' in host or '127.0.0.1' in host:
            return None
        
        # Para producción: panaderia.midominio.com -> "panaderia"
        partes = host.split('.')
        if len(partes) > 2:
            return partes[0]
        
        return None
    
    def obtener_tenant_desde_bd(self, identificador):
        """Obtener información del tenant desde la BD maestra"""
        try:
            conn = sqlite3.connect(self.tenant_master_db)
            cursor = conn.cursor()
            
            # Buscar por subdominio o ID
            cursor.execute('''
                SELECT id, nombre, subdominio, base_datos, activo, plan
                FROM tenants 
                WHERE (subdominio = ? OR id = ?) AND activo = 1
            ''', (identificador, identificador))
            
            tenant_data = cursor.fetchone()
            conn.close()
            
            if tenant_data:
                return {
                    'id': tenant_data[0],
                    'nombre': tenant_data[1],
                    'subdominio': tenant_data[2],
                    'base_datos': tenant_data[3],
                    'activo': bool(tenant_data[4]),
                    'plan': tenant_data[5]
                }
            
        except Exception as e:
            print(f"❌ Error obteniendo tenant desde BD: {e}")
        
        # ⬇⬇⬇ NUEVO: SI NO EXISTE, CREAR AUTOMÁTICAMENTE ⬇⬇⬇
        print(f"⚠️  Tenant no encontrado: {identificador}. Creando automáticamente...")
        return self.crear_tenant_automatico(identificador)
    
    def obtener_conexion_tenant(self):
        """Obtener conexión a la BD del tenant actual"""
        if not hasattr(g, 'db_path'):
            self.detectar_y_configurar_tenant()
        
        try:
            conn = sqlite3.connect(g.db_path)
            conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
            return conn
        except Exception as e:
            print(f"❌ Error conectando a BD tenant: {e}")
            return None

    def obtener_uri_bd_tenant(self):
        """Obtener URI de base de datos para SQLAlchemy"""
        if not hasattr(g, 'db_path'):
            self.detectar_y_configurar_tenant()
        
        # Para SQLite
        if hasattr(g, 'db_path'):
            return f"sqlite:///{g.db_path}"
        else:
            # Fallback a BD principal
            return "sqlite:///panaderia.db"
    
    def obtener_siguiente_panaderia_id(self):
        """Obtiene el siguiente ID disponible para nueva panadería"""
        try:
            conn = sqlite3.connect(self.tenant_master_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT MAX(id) FROM tenants")
            max_id = cursor.fetchone()[0]
            
            siguiente_id = (max_id or 1) + 1
            
            conn.close()
            return siguiente_id
            
        except Exception as e:
            print(f"⚠️  Error obteniendo siguiente ID: {e}")
            return 1000  # ID alto para evitar conflictos
    
    def crear_tenant_automatico(self, identificador):
        """Crear un nuevo tenant automáticamente usando PostgreSQL"""
        try:
            from models import Tenant, ConfiguracionPanaderia, db
            from sqlalchemy import text
            from werkzeug.security import generate_password_hash
            import secrets
            import string
            
            print(f"🚀 Creando tenant automáticamente: {identificador}")
            
            # 1. Verificar si ya existe
            tenant_existente = Tenant.query.filter_by(subdominio=identificador).first()
            if tenant_existente:
                print(f"✅ Tenant ya existe: {tenant_existente.nombre} (ID: {tenant_existente.id})")
                return {
                    'id': tenant_existente.id,
                    'nombre': tenant_existente.nombre,
                    'subdominio': tenant_existente.subdominio,
                    'base_datos': tenant_existente.base_datos,
                    'activo': tenant_existente.activo,
                    'plan': tenant_existente.plan
                }
            
            # 2. Crear tenant en PostgreSQL
            nuevo_tenant = Tenant(
                nombre=f"Panadería {identificador}",
                subdominio=identificador,
                base_datos=f"tenant_{identificador}",
                plan='basico',
                activo=True
            )
            db.session.add(nuevo_tenant)
            db.session.commit()
            
            tenant_id = nuevo_tenant.id
            
            # 3. Crear schema en PostgreSQL
            schema_name = f"tenant_{tenant_id}"
            db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            db.session.commit()
            
            # 4. Crear las tablas dentro del schema
            from models import db
            from sqlalchemy import MetaData
            
            metadata = MetaData(schema=schema_name)
            for table in db.metadata.tables.values():
                if table.schema is None or table.schema == 'public':
                    try:
                        new_table = table.to_metadata(metadata, schema=schema_name)
                    except AttributeError:
                        new_table = table.tometadata(metadata, schema=schema_name)
            
            metadata.create_all(db.engine)
            print(f"   ✅ Tablas creadas en schema {schema_name}")
            
            # 5. Generar contraseña temporal
            caracteres = string.ascii_letters + string.digits + "!@#$%"
            contrasena_temp = ''.join(secrets.choice(caracteres) for _ in range(10))
            
            # 6. Configurar panadería en el schema (SIN ID)
            db.session.execute(
                text(f"""
                    INSERT INTO {schema_name}.configuracion_panaderia 
                    (panaderia_id, nombre_panaderia, fecha_creacion, activo)
                    VALUES (:panaderia_id, :nombre_panaderia, NOW(), true)
                """),
                {
                    'panaderia_id': tenant_id,
                    'nombre_panaderia': f"Panadería {identificador}"
                }
            )
            print(f"   ✅ Configuración creada")
            
            # 7. Obtener el ID generado
            result = db.session.execute(
                text(f"SELECT id FROM {schema_name}.configuracion_panaderia WHERE panaderia_id = :panaderia_id"),
                {'panaderia_id': tenant_id}
            )
            config_id = result.fetchone()[0]
            print(f"   ✅ Config ID: {config_id}")
            
            # 8. Configurar consecutivo POS
            db.session.execute(
                text(f"""
                    INSERT INTO {schema_name}.consecutivos_pos 
                    (panaderia_id, numero_actual)
                    VALUES (:panaderia_id, :numero_actual)
                """),
                {
                    'panaderia_id': config_id,
                    'numero_actual': 0
                }
            )
            
            # 9. Crear usuario admin
            db.session.execute(
                text(f"""
                    INSERT INTO {schema_name}.usuarios 
                    (username, password_hash, nombre_completo, rol, activo, panaderia_id)
                    VALUES 
                    (:username, :password_hash, :nombre_completo, :rol, :activo, :panaderia_id)
                """),
                {
                    'username': f'admin_{tenant_id}',
                    'password_hash': generate_password_hash(contrasena_temp),
                    'nombre_completo': f'Administrador Panadería {identificador}',
                    'rol': 'admin_cliente',
                    'activo': True,
                    'panaderia_id': config_id
                }
            )
            
            db.session.commit()
            
            print(f"✅ Tenant creado: {identificador} (ID: {tenant_id})")
            print(f"   🔑 Contraseña temporal: {contrasena_temp}")
            
            return {
                'id': tenant_id,
                'nombre': f"Panadería {identificador}",
                'subdominio': identificador,
                'base_datos': f"tenant_{identificador}",
                'activo': True,
                'plan': 'basico'
            }
            
        except Exception as e:
            print(f"❌ Error creando tenant automático: {e}")
            db.session.rollback()
            return None

# Instancia global del gestor de tenants
gestor_tenants = GestorTenants()

def init_tenants_app(app):
    """Inicializar la aplicación con el sistema de tenants"""
    gestor_tenants.init_app(app)
    return gestor_tenants
    
    # =============================================
    # 🆕 CREAR SCHEMAS PARA TENANTS EXISTENTES
    # =============================================
    try:
        from sqlalchemy import text
        with app.app_context():
            # Obtener tenants de la base de datos
            from models import Tenant
            tenants = Tenant.query.all()
            for tenant in tenants:
                schema_name = f"tenant_{tenant.id}"
                db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                db.session.commit()
                print(f"✅ Schema {schema_name} creado/verificado para tenant {tenant.id}")
    except Exception as e:
        print(f"⚠️ Error creando schemas: {e}")
