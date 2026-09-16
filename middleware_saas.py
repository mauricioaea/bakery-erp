#!/usr/bin/env python3
"""
MIDDLEWARE SAAS - Detección de Tenant y Conexión Dinámica
(100% PostgreSQL - SQLite eliminado 2026-09-16)
"""

import os
from pathlib import Path
from flask import request, g, current_app
import re


class GestorTenants:
    def __init__(self, app=None):
        self.app = app
        
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
                'base_datos': 'tenant_1'
            }
            print(f"🔍 MIDDLEWARE DEBUG - Usando tenant por defecto: {tenant_info}")
        
        # Configurar el tenant en el contexto global
        g.tenant = tenant_info
        
        print(f"🔍 MIDDLEWARE DEBUG - Configurado:")
        print(f"   Tenant: {tenant_info['nombre']}")
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
        """
        Obtener información del tenant desde PostgreSQL (public.tenants).
        100% PostgreSQL - sin SQLite.
        """
        try:
            from models import Tenant
            
            # 1. Buscar por subdominio
            tenant = Tenant.query.filter_by(subdominio=str(identificador), activo=True).first()
            
            # 2. Si no se encuentra y es numérico, buscar por ID
            if not tenant and str(identificador).isdigit():
                tenant = Tenant.query.filter_by(id=int(identificador), activo=True).first()
            
            if tenant:
                return {
                    'id': tenant.id,
                    'nombre': tenant.nombre,
                    'subdominio': tenant.subdominio,
                    'base_datos': tenant.base_datos,
                    'activo': bool(tenant.activo),
                    'plan': tenant.plan
                }
            
            # 3. Si no existe, crear automáticamente (usa PostgreSQL)
            print(f"⚠️ Tenant no encontrado: {identificador}. Creando automáticamente...")
            return self.crear_tenant_automatico(identificador)
        
        except Exception as e:
            print(f"❌ Error obteniendo tenant desde PostgreSQL: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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