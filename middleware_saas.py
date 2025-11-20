#!/usr/bin/env python3
"""
MIDDLEWARE SAAS - Detección de Tenant y Conexión Dinámica
"""

import sqlite3
import os
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
        # Obtener información del tenant desde el subdominio o parámetros
        tenant_info = self.obtener_tenant_desde_request()
        
        if not tenant_info:
            # Si no se detecta tenant, usar el principal por defecto
            tenant_info = {
                'id': 1,
                'nombre': 'Panadería Principal',
                'subdominio': 'principal',
                'base_datos': 'panaderia_principal.db'
            }
        
        # Configurar la conexión a la BD del tenant en el contexto global
        g.tenant = tenant_info
        g.db_path = os.path.join(self.databases_dir, tenant_info['base_datos'])
        
        print(f"🔍 Tenant detectado: {tenant_info['nombre']} (BD: {g.db_path})")
    
    def obtener_tenant_desde_request(self):
        """Obtener información del tenant basado en la request"""
        # Estrategia 1: Por subdominio (para producción)
        subdominio = self.extraer_subdominio(request.host)
        
        # Estrategia 2: Por parámetro de consulta (para desarrollo)
        tenant_param = request.args.get('tenant', None)
        
        # Estrategia 3: Por header HTTP (para APIs)
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
        
        return None
    
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

# Instancia global del gestor de tenants
gestor_tenants = GestorTenants()

def init_tenants_app(app):
    """Inicializar la aplicación con el sistema de tenants"""
    gestor_tenants.init_app(app)
    return gestor_tenants