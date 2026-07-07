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
        """Crear un nuevo tenant automáticamente"""
        try:
            print(f"🆕 Creando tenant automáticamente: {identificador}")
            
            # 1. Obtener siguiente ID disponible
            siguiente_id = self.obtener_siguiente_panaderia_id()
            
            # 2. Crear base de datos
            destino = os.path.join(self.databases_dir, f"{identificador}.db")
            plantilla = os.path.join(self.databases_dir, "tenant_plantilla.db")
            
            if not Path(plantilla).exists():
                print(f"❌ Plantilla no encontrada: {plantilla}")
                return None
            
            # Copiar plantilla
            shutil.copy2(plantilla, destino)
            
            # Configurar tenant
            conn = sqlite3.connect(destino)
            cursor = conn.cursor()
            
            # Configurar panadería según columnas reales
            cursor.execute("PRAGMA table_info(configuracion_panaderia)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            cursor.execute("DELETE FROM configuracion_panaderia")
            
            if 'panaderia_id' in columnas and 'nombre_panaderia' in columnas:
                columnas_disponibles = ['panaderia_id', 'nombre_panaderia']
                valores = [siguiente_id, f"Panadería {identificador}"]
                
                # CORRECCIÓN: Para fecha_creacion, usar SQLite directamente
                sql_extra = ""
                if 'fecha_creacion' in columnas:
                    columnas_disponibles.append('fecha_creacion')
                    sql_extra = ", datetime('now')"
                
                columnas_sql = ', '.join(columnas_disponibles)
                
                # Construir SQL correctamente
                if sql_extra:
                    sql = f"INSERT INTO configuracion_panaderia ({columnas_sql}) VALUES (?, ?{sql_extra})"
                else:
                    sql = f"INSERT INTO configuracion_panaderia ({columnas_sql}) VALUES (?, ?)"
                
                cursor.execute(sql, (siguiente_id, f"Panadería {identificador}"))
                print(f"   ✅ configuracion_panaderia: ID {siguiente_id}")
            
            # Configurar consecutivo POS
            cursor.execute("DELETE FROM consecutivos_pos")
            cursor.execute("INSERT INTO consecutivos_pos (panaderia_id, numero_actual) VALUES (?, 0)", (siguiente_id,))
            print(f"   ✅ consecutivos_pos: ID {siguiente_id}")
            
            # Configurar tabla panaderias si existe (opcional)
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='panaderias'")
                if cursor.fetchone():
                    cursor.execute("DELETE FROM panaderias")
                    cursor.execute("INSERT INTO panaderias (id, nombre) VALUES (?, ?)", (siguiente_id, f"Panadería {identificador}"))
                    print(f"   ✅ panaderias: ID {siguiente_id}")
            except Exception as e:
                print(f"   ⚠️  panaderias: {e}")
            
            conn.commit()
            conn.close()
            
            # 3. Registrar en tenant_master.db
            conn_master = sqlite3.connect(self.tenant_master_db)
            cursor_master = conn_master.cursor()
            
            cursor_master.execute('''
                INSERT INTO tenants (id, nombre, subdominio, base_datos, activo, plan)
                VALUES (?, ?, ?, ?, 1, 'basico')
            ''', (siguiente_id, f"Panadería {identificador}", identificador, f"{identificador}.db"))
            
            conn_master.commit()
            conn_master.close()
            
            print(f"✅ Tenant creado automáticamente: {identificador} (ID: {siguiente_id})")
            
            return {
                'id': siguiente_id,
                'nombre': f"Panadería {identificador}",
                'subdominio': identificador,
                'base_datos': f"{identificador}.db",
                'activo': True,
                'plan': 'basico'
            }
            
        except Exception as e:
            print(f"❌ Error creando tenant automático: {e}")
            # Intentar limpiar archivo corrupto
            try:
                if os.path.exists(destino):
                    os.remove(destino)
                    print(f"🗑️  Limpiado archivo corrupto: {destino}")
            except:
                pass
            return None

# Instancia global del gestor de tenants
gestor_tenants = GestorTenants()

def init_tenants_app(app):
    """Inicializar la aplicación con el sistema de tenants"""
    gestor_tenants.init_app(app)
    return gestor_tenants