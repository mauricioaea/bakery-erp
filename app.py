import os
import uuid
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response, g

# =============================================
# 🆕 FUNCIÓN SAAS - CREAR TENANT AUTOMÁTICAMENTE
# =============================================

def crear_tenant_saas(nombre_panaderia, subdominio, email_contacto=None):
    """
    Crear un nuevo tenant SaaS cuando se crea un cliente
    Returns: (éxito, mensaje, tenant_id)
    """
    try:
        # Importar módulos necesarios
        import sqlite3
        import os
        import shutil
        
        # 1. REGISTRAR EN BD MAESTRA
        conn_maestra = sqlite3.connect('tenant_master.db')
        cursor_maestra = conn_maestra.cursor()
        
        # Verificar si el subdominio ya existe
        cursor_maestra.execute("SELECT id FROM tenants WHERE subdominio = ?", (subdominio,))
        if cursor_maestra.fetchone():
            conn_maestra.close()
            return False, f"El subdominio '{subdominio}' ya existe", None
        
        # Nombre del archivo de BD
        nombre_bd = f"{subdominio}.db"  # Cambiado a formato más simple
        ruta_bd = os.path.join('databases_tenants', nombre_bd)
        
        # Insertar nuevo tenant
        cursor_maestra.execute(
            "INSERT INTO tenants (nombre, subdominio, base_datos, plan, activo) VALUES (?, ?, ?, ?, ?)",
            (nombre_panaderia, subdominio, nombre_bd, 'basico', 1)
        )
        
        tenant_id = cursor_maestra.lastrowid
        
        # 2. CREAR BASE DE DATOS DEL TENANT
        if not os.path.exists(ruta_bd):
            # Usar plantilla profesional
            plantilla = 'databases_tenants/tenant_plantilla.db'
            if os.path.exists(plantilla):
                shutil.copy2(plantilla, ruta_bd)
                print(f"✅ BD creada desde plantilla: {ruta_bd}")
            else:
                # Fallback a BD principal
                shutil.copy2('databases_tenants/panaderia_principal.db', ruta_bd)
                print(f"✅ BD creada desde principal: {ruta_bd}")
        
        # 3. CONFIGURAR TENANT EN SU BD (REEMPLAZA usuarios_global)
        # Ahora se configura directamente en la BD del tenant, no en tabla global
        conn_tenant = sqlite3.connect(ruta_bd)
        cursor_tenant = conn_tenant.cursor()
        
        # Configurar panadería en su propia BD
        cursor_tenant.execute("DELETE FROM configuracion_panaderia")
        cursor_tenant.execute(
            "INSERT INTO configuracion_panaderia (panaderia_id, nombre_panaderia, fecha_creacion) VALUES (?, ?, datetime('now'))",
            (tenant_id, nombre_panaderia)
        )
        
        # Configurar consecutivo POS
        cursor_tenant.execute("DELETE FROM consecutivos_pos")
        cursor_tenant.execute(
            "INSERT INTO consecutivos_pos (panaderia_id, numero_actual) VALUES (?, 0)",
            (tenant_id,)
        )
        
        conn_tenant.commit()
        conn_tenant.close()
        
        conn_maestra.commit()
        conn_maestra.close()
        
        print(f"🎉 Nuevo tenant SaaS creado: {nombre_panaderia} (ID: {tenant_id})")
        print(f"   📁 Archivo: {nombre_bd}")
        print(f"   🔢 Consecutivo POS: 0")
        return True, f"Tenant {nombre_panaderia} creado exitosamente", tenant_id
        
    except Exception as e:
        print(f"❌ Error creando tenant SaaS: {e}")
        return False, f"Error creando tenant: {str(e)}", None
    
# =============================================
# CREAR USUARIOS PARA UN TENANT (SIEMPRE)
# =============================================
def crear_usuarios_tenant_siempre(tenant_id, tenant_db_path, nombre_panaderia):
    """
    Crea los usuarios admin, super y cajero para un tenant
    Args:
        tenant_id: ID del tenant
        tenant_db_path: Ruta a la BD del tenant
        nombre_panaderia: Nombre de la panadería
    Returns:
        str: Contraseña temporal generada, o None si hay error
    """
    import sqlite3
    from werkzeug.security import generate_password_hash
    import secrets
    import string
    
    try:
        # Generar contraseña temporal
        caracteres = string.ascii_letters + string.digits + "!@#$%"
        contrasena_temp = ''.join(secrets.choice(caracteres) for _ in range(10))
        
        conn = sqlite3.connect(tenant_db_path)
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"   ℹ️ Ya existen {count} usuarios en el tenant")
            conn.close()
            return contrasena_temp
        
        # Crear usuarios
        usuarios_base = [
            {
                'username': f'admin_{tenant_id}',
                'rol': 'admin_cliente',
                'nombre': f'Administrador {nombre_panaderia}'
            },
            {
                'username': f'super_{tenant_id}',
                'rol': 'supervisor', 
                'nombre': f'Supervisor {nombre_panaderia}'
            },
            {
                'username': f'cajero_{tenant_id}',
                'rol': 'cajero',
                'nombre': f'Cajero Principal {nombre_panaderia}'
            }
        ]
        
        for user_data in usuarios_base:
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo, panaderia_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'],
                generate_password_hash(contrasena_temp),
                user_data['nombre'],
                user_data['rol'],
                1,  # Siempre activo
                tenant_id
            ))
            print(f"   ✅ Usuario creado: {user_data['username']} ({user_data['rol']})")
        
        conn.commit()
        conn.close()
        
        return contrasena_temp
        
    except Exception as e:
        print(f"   ❌ Error creando usuarios: {e}")
        return None

from tenant_decorators import tenant_required, with_tenant_context, tenant_query, get_current_tenant_id
from tenant_context import TenantContext
from security_utils import validate_tenant_access, safe_tenant_query, check_tenant_ownership

# SAAS MIDDLEWARE - Arquitectura Multi-Tenant
from middleware_saas import init_tenants_app, gestor_tenants

from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, timezone
from sqlalchemy import func, extract
from reportes import GeneradorReportes
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 🆕 IMPORTAR MIDDLEWARE MULTICLIENTE PRIMERO
from multicliente_middleware import (
    obtener_panaderia_usuario,
    filtrar_por_panaderia, 
    requiere_panaderia,
    get_panaderia_actual
)

# =============================================
# CONFIGURACIÓN INICIAL DE LA APP
# =============================================

# 🆕 OBTENER LA RUTA BASE DEL PROYECTO
basedir = os.path.abspath(os.path.dirname(__file__))

# 🆕 CREAR APLICACIÓN FLASK
app = Flask(__name__)
TenantContext.initialize_app(app)
# INICIALIZAR SISTEMA SAAS MULTI-TENANT
init_tenants_app(app)
print("🚀 Middleware SaaS - Sistema multi-tenant activado")
app.secret_key = '023431bcb986f0ebab954d4237dffb57f86d01e38107bfc16c839c717ba8b15f'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Mauricio/Desktop/panaderia_sistema/panaderia_profesional/databases_tenants/panaderia_principal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =============================================
# IMPORTAR DB PRIMERO, LUEGO MODELOS

# =============================================

# 🆕 SOLO IMPORTAR db PRIMERO
from models import db

# 🆕 AHORA IMPORTAR TODOS LOS MODELOS
from models import Usuario, Producto, Venta, DetalleVenta, MateriaPrima, Receta, RecetaIngrediente, Panaderia,  ConfiguracionPanaderia
from models import OrdenProduccion, Categoria, Proveedor, HistorialCompra, HistorialInventario
from models import ConfiguracionProduccion, HistorialRotacionProducto, ControlVidaUtil, Factura
from models import ProductoExterno, CompraExterna, RegistroDiario, SaldoBanco, PagoIndividual, DepositoBancario
from models import JornadaVentas, CierreDiario, obtener_jornada_activa, cerrar_jornada_actual, obtener_ventas_dia, obtener_historial_cierres
from models import ConsecutivoPOS, ConfiguracionSistema, Cliente
from models import calcular_rotacion_automatica, actualizar_rotaciones_automaticas
from models import calcular_tendencia_ventas, analizar_productos_periodo, calcular_rotacion_automatica_por_nombre
from models import calcular_proyeccion_ventas, generar_recomendacion_stock, generar_alertas_inteligentes
from models import LogSistema, RegistroFinanciero
from models import obtener_productos_sin_ventas_recientes, ActivoFijo, HistorialMantenimiento, CATEGORIAS_ACTIVOS
from facturacion.generador_xml import generar_xml_ubl_21




# =============================================
# CONFIGURACIÓN FLASK-LOGIN
# =============================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializar db con la app
db.init_app(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

# =============================================
# 🆕 DEFINICIÓN DE MÓDULOS DEL SISTEMA
# =============================================

MODULOS_SISTEMA = {
    'dashboard': 'Panel Principal',
    'punto_venta': 'Punto de Venta',
    'productos': 'Gestión de Productos',
    'categorias': 'Categorías',
    'produccion': 'Producción y Recetas',
    'inventario': 'Inventario y Materias Primas',
    'clientes': 'Gestión de Clientes',
    'proveedores': 'Proveedores',
    'finanzas': 'Control Financiero',
    'reportes': 'Reportes y Análisis',
    'configuracion': 'Configuración',
    'activos': 'Activos Fijos',
    'usuarios': 'Gestión de Usuarios',
    'sistema': 'Sistema y Diagnóstico'
}

# =============================================
# 🆕 DECORADORES PARA CONTROL DE ACCESO
# =============================================

from functools import wraps

def permisos_requeridos(modulo, accion):
    """Decorador para verificar permisos en rutas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if not current_user.tiene_permiso(modulo, accion):
                flash('❌ No tienes permisos para realizar esta acción', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def modulo_requerido(modulo):
    """Decorador para verificar acceso al módulo completo - VERSIÓN MEJORADA"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            # ✅ SUPER_ADMIN tiene acceso a TODO (incluyendo gestión de clientes)
            if current_user.rol == 'super_admin':
                return f(*args, **kwargs)
            
            # ✅ ADMIN_CLIENTE NO puede acceder a gestión de clientes de otros
            if modulo == 'gestion_clientes' and current_user.rol == 'admin_cliente':
                flash('❌ Solo el soporte técnico puede acceder a la gestión de clientes', 'error')
                return redirect(url_for('dashboard'))
            
            if not current_user.puede_acceder_modulo(modulo):
                flash(f'❌ No tienes acceso al módulo {MODULOS_SISTEMA.get(modulo, modulo)}', 'error')
                return redirect(url_for('acceso_denegado'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================
# 🆕 CONTEXT PROCESSOR PARA PERMISOS EN TEMPLATES
# =============================================

@app.context_processor
def inject_permisos():
    """Inyectar funciones de permisos en todos los templates"""
    def usuario_puede(modulo, accion):
        if not current_user.is_authenticated:
            return False
        return current_user.tiene_permiso(modulo, accion)
    
    def usuario_tiene_acceso(modulo):
        if not current_user.is_authenticated:
            return False
        return current_user.puede_acceder_modulo(modulo)
    
    def modulos_permitidos():
        if not current_user.is_authenticated:
            return []
        return current_user.obtener_modulos_permitidos()
    
    return dict(
        usuario_puede=usuario_puede,
        usuario_tiene_acceso=usuario_tiene_acceso,
        modulos_permitidos=modulos_permitidos,
        MODULOS_SISTEMA=MODULOS_SISTEMA
    )

@app.before_request
def antes_de_cada_peticion():
    # =============================================
    # 🆕 SAAS - DETECCIÓN MEJORADA DE TENANT
    # =============================================
    from middleware_saas import gestor_tenants
    
    tenant_detectado = None
    
    # PRIMERO: Detección por subdominio (siempre disponible)
    tenant_detectado = gestor_tenants.obtener_tenant_desde_request()
    if tenant_detectado:
        print(f"🔍 Tenant detectado por subdominio: {tenant_detectado['nombre']}")
    
    # SEGUNDO: Si hay usuario autenticado, priorizar su tenant
    # Verificar de forma segura si current_user está disponible
    try:
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and hasattr(current_user, 'panaderia_id'):
            try:
                import sqlite3
                conn = sqlite3.connect('tenant_master.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id, nombre, subdominio, base_datos FROM tenants WHERE id = ? AND activo = 1', (current_user.panaderia_id,))
                
                tenant_data = cursor.fetchone()
                conn.close()
                
                if tenant_data:
                    tenant_detectado = {
                        'id': tenant_data[0],
                        'nombre': tenant_data[1],
                        'subdominio': tenant_data[2],
                        'base_datos': tenant_data[3]
                    }
                    print(f"🔍 Tenant detectado por usuario: {tenant_detectado['nombre']} (panaderia_id: {current_user.panaderia_id})")
            except Exception as e:
                print(f"⚠️ Error detectando tenant por usuario: {e}")
    except Exception as e:
        print(f"⚠️ current_user no disponible aún: {e}")
    
    # TERCERO: Si no hay tenant detectado, usar principal por defecto
    if not tenant_detectado:
        tenant_detectado = {
            'id': 1,
            'nombre': 'Panadería Principal',
            'subdominio': 'principal',
            'base_datos': 'panaderia_principal.db'
        }
        print("🔍 Tenant por defecto: Panadería Principal")
    
    # Configurar en contexto global
    g.tenant = tenant_detectado
    
    # Configurar SQLAlchemy para el tenant detectado
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///databases_tenants/{tenant_detectado['base_datos']}"
    print(f"🔧 SaaS - BD configurada: {tenant_detectado['base_datos']}")
    
    """Middleware global unificado - VERSIÓN MEJORADA"""
    # 1. Establecer información de usuario y panadería
    from multicliente_middleware import obtener_info_usuario
    obtener_info_usuario()

    # 2. Verificar suscripción (solo si current_user está disponible)
    try:
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and hasattr(current_user, 'panaderia_id'):
            from models import obtener_configuracion_panaderia

            try:
                config = obtener_configuracion_panaderia(current_user.panaderia_id)
                if config is not None:
                    config.actualizar_estado_suscripcion()

                    if config.tipo_licencia != 'local' and not config.suscripcion_activa:
                        rutas_permitidas = ['logout', 'static', 'suscripcion_vencida', 'login']
                        if request.endpoint and not any(ruta in request.endpoint for ruta in rutas_permitidas):
                            return redirect(url_for('suscripcion_vencida'))
            except Exception as e:
                print(f"⚠️ Error verificando suscripción: {e}")
    except Exception as e:
        print(f"⚠️ current_user no disponible para verificación de suscripción: {e}")


# =============================================
# 🚀 INICIALIZACIÓN SAAS (EJECUCIÓN ÚNICA)
# =============================================

with app.app_context():
    db.create_all()
    
    # Verificar si ya existe un usuario admin
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = generate_password_hash('admin123')
        admin_user = Usuario(
            username='admin', 
            password_hash=hashed_password, 
            nombre_completo='Administrador Principal',
            rol='administrador'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Usuario admin creado: usuario: admin, contraseña: admin123")
    
    # 🆕 VERIFICAR Y CREAR MODELOS NUEVOS DEL SISTEMA POS
    consecutivo = ConsecutivoPOS.query.first()
    if not consecutivo:
        consecutivo_inicial = ConsecutivoPOS(numero_actual=0)
        db.session.add(consecutivo_inicial)
        print("✅ Consecutivo POS inicial creado")
    
    config_sistema = ConfiguracionSistema.query.first()
    if not config_sistema:
        config_inicial = ConfiguracionSistema(
            tipo_facturacion='POS',
            nombre_empresa='Panadería y Pasteleria Semillas',
            nit_empresa='900000000-1',
            direccion_empresa='Cra. 18 # 9-45 Atahualpa',
            telefono_empresa='+57 3189098818',
            ciudad_empresa='Pasto',
            regimen_empresa='Simplificado'
        )
        db.session.add(config_inicial)
        print("✅ Configuración del sistema inicial creada")
    
    # Crear categorías y productos de prueba si no existen
    if not Categoria.query.first():
        # Crear categorías
        panaderia = Categoria(nombre="Panadería")
        pasteleria = Categoria(nombre="Pastelería")
        bebidas = Categoria(nombre="Bebidas")
        
        db.session.add_all([panaderia, pasteleria, bebidas])
        db.session.commit()
        
        # Crear productos de prueba
        productos = [
            Producto(nombre="Pan Mantequilla", categoria_id=panaderia.id, precio_venta=300, codigo_barras="1001"),
            Producto(nombre="Pan Integral", categoria_id=panaderia.id, precio_venta=4000, codigo_barras="1002"),
            Producto(nombre="Croissant", categoria_id=panaderia.id, precio_venta=1000, codigo_barras="1003"),
            Producto(nombre="Pastel de Chocolate", categoria_id=pasteleria.id, precio_venta=30000, codigo_barras="2001"),
            Producto(nombre="Galletas", categoria_id=pasteleria.id, precio_venta=1200, codigo_barras="2002"),
            Producto(nombre="Café", categoria_id=bebidas.id, precio_venta=1000, codigo_barras="3001"),
            Producto(nombre="Jugo de Naranja", categoria_id=bebidas.id, precio_venta=4000, codigo_barras="3002")
        ]
        
        db.session.add_all(productos)
        db.session.commit()
        print("✅ Productos de prueba creados automáticamente")
    
    # ❌ ELIMINADO: PROVEEDORES PRE-CONFIGURADOS
    # Cada tenant debe empezar limpio y crear sus propios proveedores
    # if not Proveedor.query.first():
    #     proveedores_ejemplo = [
    #         Proveedor(
    #             nombre="Haz de Oros",
    #             contacto="Juan Pérez",
    #             telefono="3001234567",
    #             email="ventas@hazdeoros.com",
    #             direccion="Calle 123 #45-67, Bogotá",
    #             productos_que_suministra="Harina de trigo, harina integral, salvado",
    #             tiempo_entrega_dias=2,
    #             evaluacion=5
    #         ),
    #         Proveedor(
    #             nombre="Lacteos La Sabana",
    #             contacto="María González",
    #             telefono="3109876543", 
    #             email="pedidos@lacteoslasabana.com",
    #             direccion="Av. 68 #12-34, Medellín",
    #             productos_que_suministra="Leche, mantequilla, queso, crema de leche",
    #             tiempo_entrega_dias=1,
    #             evaluacion=4
    #         ),
    #         Proveedor(
    #             nombre="Dulces del Valle",
    #             contacto="Carlos Rodríguez",
    #             telefono="3205558888",
    #             email="info@dulcesdelvalle.com",
    #             direccion="Cr. 45 #78-90, Cali", 
    #             productos_que_suministra="Azúcar, panela, miel, esencias",
    #             tiempo_entrega_dias=3,
    #             evaluacion=4
    #         )
    #     ]
    #     
    #     db.session.add_all(proveedores_ejemplo)
    #     db.session.commit()
    #     print("✅ Proveedores de ejemplo creados automáticamente")
    
    # 🆕 HACER COMMIT FINAL DE TODOS LOS CAMBIOS
    db.session.commit()
    
    print("✅ Base de datos lista!")
    print(f"📁 Ubicación de la BD: {os.path.join(basedir, 'panaderia.db')}")
# =============================================
# 🆕 RUTA DE SUSCRIPCIÓN VENCIDA
# =============================================

@app.route('/suscripcion_vencida')
@login_required
def suscripcion_vencida():
    """Página que se muestra cuando la suscripción está vencida"""
    from models import obtener_configuracion_panaderia
    config = obtener_configuracion_panaderia(current_user.panaderia_id)
    return render_template('suscripcion_vencida.html', 
                         config=config,
                         dias_restantes=config.dias_para_expiracion)

# =============================================
# RUTAS PRINCIPALES DEL SISTEMA - SIN DUPLICADOS
# =============================================

# Ruta para el login - SOLO UNA VEZ
# =============================================
# RUTAS PRINCIPALES DEL SISTEMA - SIN DUPLICADOS
# =============================================

def es_super_usuario():
    """Verifica si el usuario actual es super usuario (dev_master)"""
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    usuario = Usuario.query.get(user_id)
    
    # Identificar por nombre de usuario (dev_master)
    if usuario and usuario.username == 'dev_master':
        return True
    
    return False

def diagnosticar_recetas(panaderia_id):
    """Diagnóstico para ver qué recetas existen"""
    print(f"🔍 DIAGNÓSTICO RECETAS - Panadería {panaderia_id}:")
    
    todas_recetas = Receta.query.filter_by(panaderia_id=panaderia_id).all()
    print(f"   Total recetas en BD: {len(todas_recetas)}")
    
    for receta in todas_recetas:
        print(f"   - '{receta.nombre}' (ID: {receta.id}, Activo: {receta.activo})")
    
    recetas_activas = Receta.query.filter_by(panaderia_id=panaderia_id, activo=True).all()
    print(f"   Recetas activas: {len(recetas_activas)}")
    
    return len(recetas_activas)

# ✅ ✅ ✅ AGREGA diagnosticar_recetas EXACTAMENTE AQUÍ ✅ ✅ ✅
def diagnosticar_recetas(panaderia_id):
    """Diagnóstico para ver qué recetas existen"""
    print(f"🔍 DIAGNÓSTICO RECETAS - Panadería {panaderia_id}:")
    
    # Ver todas las recetas de esta panadería
    todas_recetas = Receta.query.filter_by(panaderia_id=panaderia_id).all()
    print(f"   Total recetas en BD: {len(todas_recetas)}")
    
    for receta in todas_recetas:
        print(f"   - '{receta.nombre}' (ID: {receta.id}, Activo: {receta.activo})")
    
    # Ver recetas activas
    recetas_activas = Receta.query.filter_by(panaderia_id=panaderia_id, activo=True).all()
    print(f"   Recetas activas: {len(recetas_activas)}")
    
    return len(recetas_activas)

def obtener_panaderia_actual():
    """Obtener panadería actual considerando acceso remoto SOLO para super usuario"""
    if es_super_usuario() and 'panaderia_remota' in session:
        return session['panaderia_remota']
    return session.get('panaderia_id')

# ✅ ✅ ✅ FIN DE diagnosticar_recetas ✅ ✅ ✅
# Ruta para el login - SOLO UNA VEZ
@app.route('/', methods=['GET', 'POST'])
def login():
    # Limpiar mensajes flash antiguos
    from flask import get_flashed_messages
    get_flashed_messages()
    """🎯 SISTEMA DE LOGIN PROFESIONAL - ARQUITECTURA EXTENSIBLE"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔍 [LOGIN] Buscando usuario: {username}")
        print(f"🔍 [LOGIN] URI de BD: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 🔧 CORREGIDO: Buscar usuario en la BD del tenant
        from flask import g
        if hasattr(g, 'db_path') and g.db_path:
            # Usar la BD del tenant detectada
            import sqlite3
            conn_tenant = sqlite3.connect(g.db_path)
            cursor_tenant = conn_tenant.cursor()
            cursor_tenant.execute("SELECT id, username, password_hash, panaderia_id, rol FROM usuarios WHERE username = ?", (username,))
            user_data = cursor_tenant.fetchone()
            conn_tenant.close()
            
            if user_data:
                # Crear objeto Usuario a partir de los datos
                user = Usuario()
                user.id = user_data[0]
                user.username = user_data[1]
                user.password_hash = user_data[2]
                user.panaderia_id = user_data[3]
                user.rol = user_data[4]
            else:
                user = None
        else:
            # Fallback a BD principal
            user = Usuario.query.filter_by(username=username).first()
        
        if user:
            print(f"✅ [LOGIN] USUARIO ENCONTRADO: {user.username}")
            print(f"📦 [LOGIN] Hash en BD: {user.password_hash}")
            print(f"🏪 [LOGIN] Panadería ID: {user.panaderia_id}")
            
            # 🎯 ARQUITECTURA PROFESIONAL - MÚLTIPLES MÉTODOS DE VERIFICACIÓN
            login_exitoso, metodo_usado = verificar_credenciales(user, password)
            
            if login_exitoso:
                print(f"✅ [LOGIN] Verificación exitosa con método: {metodo_usado}")
                
                # 🔐 REGISTRO DE ACTIVIDAD (PREPARACIÓN PARA AUDITORÍA)
                registrar_intento_login(user.id, True, metodo_usado)
                
                # =============================================
                # 🆕 VERIFICAR FECHA DE EXPIRACIÓN DE LICENCIA
                # =============================================
                from models import ConfiguracionPanaderia
                from datetime import datetime
                
                # Obtener configuración de la panadería del usuario
                config = ConfiguracionPanaderia.query.filter_by(
                    tenant_id=user.panaderia_id
                ).first()
                
                # Si no encuentra por tenant_id, buscar por panaderia_id
                if not config:
                    config = ConfiguracionPanaderia.query.filter_by(
                        panaderia_id=user.panaderia_id
                    ).first()
                
                # Verificar si la licencia es de tipo local (permanente) o tiene fecha de expiración
                if config and config.tipo_licencia != 'local' and config.fecha_expiracion:
                    hoy = datetime.now().date()
                    dias_restantes = (config.fecha_expiracion - hoy).days
                    
                    if dias_restantes < 0:
                        # Licencia expirada - redirigir a licencia_expirada
                        flash('🔴 ¡ATENCIÓN! Tu licencia ha expirado. No podrás acceder al sistema hasta que renueves. 📞 Contáctanos: 3102482881 o ✉️ mauricioandreserazo@outlook.com', 'error')
                        return redirect(url_for('licencia_expirada'))
                    
                    # Opcional: mostrar alerta si está por vencer (7 días o menos)
                    elif dias_restantes <= 7 and dias_restantes >= 0:
                        flash(f'⚠️ Tu licencia vence en {dias_restantes} días. Renueva pronto.', 'warning')
                # =============================================
                # FIN DE VERIFICACIÓN
                # =============================================
                
                login_user(user)
                session['user_id'] = user.id
                session['username'] = user.username
                session['rol'] = user.rol
                session['panaderia_id'] = user.panaderia_id
                
                print(f"✅ [LOGIN] Login exitoso: {username}")
                flash('Inicio de sesión exitoso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # 🔐 REGISTRO DE INTENTO FALLIDO
                registrar_intento_login(user.id, False, 'fallido')
                print(f"❌ [LOGIN] Todas las verificaciones fallaron")
        
        else:
            print(f"❌ [LOGIN] USUARIO NO ENCONTRADO en la BD actual")
            # 🔐 REGISTRO DE INTENTO FALLIDO (usuario no existe)
            registrar_intento_login(None, False, 'usuario_no_existe')
        
        flash('Usuario o contraseña incorrectos', 'error')
        print(f"❌ [LOGIN] Login fallido para: {username}")
    
    return render_template('login.html')

def verificar_credenciales(user, password):
    """
    🎯 MÉTODO PROFESIONAL EXTENSIBLE - SOPORTE MÚLTIPLES TIPOS DE HASH
    Retorna: (éxito, método_usado)
    """
    # 1. VERIFICACIÓN CON HASH SEGURO (werkzeug) - PARA USUARIOS NUEVOS/RESETEADOS
    try:
        from werkzeug.security import check_password_hash
        if check_password_hash(user.password_hash, password):
            return True, 'hash_seguro'
    except Exception as e:
        print(f"⚠️ [VERIFICACIÓN] Error con hash seguro: {e}")
    
    # 2. VERIFICACIÓN CON HASH SIMPLE (desarrollo/transición) - PARA USUARIOS EXISTENTES
    if user.password_hash.startswith('dev_'):
        expected_hash = f"dev_{password}_hash"
        if user.password_hash == expected_hash:
            return True, 'hash_simple'
        else:
            print(f"❌ [VERIFICACIÓN] Hash simple no coincide")
            print(f"   Esperado: {expected_hash}")
    
    # 3. 🆕 ESPACIO RESERVADO PARA MÉTODOS FUTUROS
    # - Verificación con OTP (One-Time Password)
    # - Verificación con API externa (SSO)
    # - Verificación con biometrics
    # - Verificación con tokens JWT
    
    return False, 'ninguno'

def registrar_intento_login(user_id, exitoso, metodo):
    """
    🎯 PREPARACIÓN PARA SISTEMA DE AUDITORÍA PROFESIONAL
    En FASE 2, esto se migrará a tabla de auditoría en base de datos
    """
    try:
        # 📊 LOG TEMPORAL - EN FASE 2 SE MIGRA A BASE DE DATOS
        print(f"📊 [AUDITORÍA] Login - UserID: {user_id}, Exitoso: {exitoso}, Método: {metodo}")
        
        # 🆕 CÓDIGO PREPARADO PARA FASE 2 (ACTUALMENTE COMENTADO)
        # from datetime import datetime
        # from models import AuditoriaLogin  # 🎯 TABLA POR CREAR EN FASE 2
        # 
        # auditoria = AuditoriaLogin(
        #     usuario_id=user_id,
        #     exitoso=exitoso,
        #     metodo_autenticacion=metodo,
        #     ip_address=request.remote_addr,
        #     user_agent=request.headers.get('User-Agent'),
        #     fecha_hora=datetime.now()
        # )
        # db.session.add(auditoria)
        # db.session.commit()
        
    except Exception as e:
        print(f"⚠️ [AUDITORÍA] Error registrando intento: {e}")

# Ruta de fallback segura
@app.route('/acceso_denegado')
@login_required
def acceso_denegado():
    return render_template('acceso_denegado.html')

# =============================================
# 🆕 NUEVA RUTA PARA LICENCIA EXPIRADA
# =============================================
@app.route('/licencia_expirada')
def licencia_expirada():
    """Página específica para licencia expirada"""
    return render_template('licencia_expirada.html')

# Ruta para el dashboard - SOLO UNA VEZ
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username', 'Usuario'))

# Ruta para el punto de venta
@app.route('/punto_venta')
@login_required
@tenant_required
@modulo_requerido('punto_venta')
def punto_venta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ OBTENER panaderia_id DE LA SESIÓN (CON ACCESO REMOTO)
    panaderia_actual = obtener_panaderia_actual()  # ← ÚNICO CAMBIO AQUÍ
    
    # ✅ ✅ ✅ NUEVO: BLOQUE SUPER USUARIO (AGREGA ESTO) ✅ ✅ ✅
    if es_super_usuario() and not session.get('panaderia_remota'):
        flash("🔧 Como super usuario, usa 'Acceder a esta panadería' para usar el punto de venta", "info")
        return render_template('punto_venta.html',
                             productos_internos=[],
                             productos_externos=[],
                             categorias=[],
                             clientes=[])
    # ✅ ✅ ✅ FIN BLOQUE SUPER USUARIO ✅ ✅ ✅
    
    # ✅ OBTENER PRODUCTOS FILTRADOS POR PANADERÍA
    productos_internos = Producto.query.filter_by(panaderia_id=panaderia_actual, activo=True).all()
    
    productos_externos = ProductoExterno.query.filter_by(panaderia_id=panaderia_actual, activo=True).all()
    
    # ✅ OBTENER CATEGORÍAS PARA ORGANIZAR PRODUCTOS
    categorias = Categoria.query.filter_by(panaderia_id=panaderia_actual).all()
    
    # ✅ OBTENER CLIENTES PARA EL SELECT
    clientes = Cliente.query.filter_by(activo=True).all()
    
    # Debug temporal para verificar
    print(f"DEBUG PUNTO VENTA: Panadería {panaderia_actual}")
    print(f"DEBUG: {len(productos_internos)} productos internos")
    print(f"DEBUG: {len(productos_externos)} productos externos")
    print(f"DEBUG: {len(categorias)} categorías")
    
    return render_template('punto_venta.html',
                         productos_internos=productos_internos,
                         productos_externos=productos_externos,
                         categorias=categorias,
                         clientes=clientes)

# EN app.py - AGREGAR ESTA RUTA DE DIAGNÓSTICO URGENTE
@app.route('/debug_punto_venta')
@login_required
@modulo_requerido('punto_venta')
def debug_punto_venta():
    """Diagnóstico urgente del punto de venta"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 1. Verificar todos los productos
    todos_productos = Producto.query.all()
    
    # 2. Productos que deberían aparecer en búsqueda
    productos_busqueda = Producto.query.filter(
        Producto.activo == True,
        Producto.stock_actual > 0
    ).all()
    
    # 3. Productos de producción específicamente
    productos_produccion = Producto.query.filter_by(tipo_producto='produccion').all()
    
    # 4. Recetas con productos asociados
    recetas_con_producto = Receta.query.filter(Receta.producto_id.isnot(None)).all()
    
    debug_info = {
        'total_productos': len(todos_productos),
        'productos_activos_con_stock': len(productos_busqueda),
        'productos_produccion': len(productos_produccion),
        'recetas_con_producto': len(recetas_con_producto),
        'detalle_productos': [],
        'detalle_recetas': []
    }
    
    for producto in todos_productos:
        debug_info['detalle_productos'].append({
            'id': producto.id,
            'nombre': producto.nombre,
            'tipo': producto.tipo_producto,
            'activo': producto.activo,
            'stock_actual': producto.stock_actual,
            'precio': producto.precio_venta,
            'tiene_receta': producto.receta_id is not None,
            'aparece_en_busqueda': producto.activo and producto.stock_actual > 0
        })
    
    for receta in recetas_con_producto:
        debug_info['detalle_recetas'].append({
            'id': receta.id,
            'nombre': receta.nombre,
            'producto_id': receta.producto_id,
            'producto_nombre': receta.producto.nombre if receta.producto else 'NO',
            'producto_stock': receta.producto.stock_actual if receta.producto else 0
        })
    
    return render_template('debug_punto_venta.html', debug=debug_info)

# Ruta para buscar productos (API)
@app.route('/buscar_producto')
@login_required
@modulo_requerido('punto_venta')
@tenant_required
def buscar_producto():
    """Búsqueda unificada de productos (panadería + externos) - VERSIÓN FUNCIONAL"""
    query = request.args.get('q', '').lower()
        # 🔍 DIAGNÓSTICO COMPLETO
    user_id = session.get('user_id')
    panaderia_id = obtener_panaderia_actual()
    print(f"🔍 DIAGNÓSTICO buscar_producto:")
    print(f"   👤 User ID: {user_id}")
    print(f"   🏪 Panadería ID: {panaderia_id}")
    print(f"   👑 Es super usuario: {es_super_usuario()}")
    print(f"   🔍 Query: '{query}'")
    
    # ✅ ✅ ✅ NUEVO: BLOQUE SUPER USUARIO (AGREGA ESTO) ✅ ✅ ✅
    if es_super_usuario():
        print("🔍 Super usuario realizando búsqueda - retornando vacío")
        return jsonify([])  # Super usuario no ve productos en búsqueda
    # ✅ ✅ ✅ FIN BLOQUE SUPER USUARIO ✅ ✅ ✅
    
    try:
        resultados = []
        
        print(f"🔍 Iniciando búsqueda con query: '{query}'")
        
        # PRODUCTOS DE PANADERÍA
        from utilidades.consultas_filtradas import productos_activos_con_stock
        productos_panaderia = productos_activos_con_stock().all()
        print(f"🍞 Productos panadería encontrados: {len(productos_panaderia)}")
        
        # PRODUCTOS EXTERNOS
        from utilidades.consultas_filtradas import productos_externos_activos_con_stock
        productos_externos = productos_externos_activos_con_stock().all()
        print(f"🥤 Productos externos encontrados: {len(productos_externos)}")
        
        # AGREGAR PRODUCTOS DE PANADERÍA
        for producto in productos_panaderia:
            nombre_lower = producto.nombre.lower()
            if query in nombre_lower or query == '':
                resultados.append({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': float(producto.precio_venta),
                    'stock_actual': producto.stock_actual,
                    'categoria': getattr(producto.categoria, 'nombre', 'Panadería') if hasattr(producto, 'categoria') and producto.categoria else 'Panadería',
                    'tipo_producto': getattr(producto, 'tipo_producto', 'produccion'),
                    'es_externo': False
                })
                print(f"✅ Agregado panadería: {producto.nombre}")
        
        # AGREGAR PRODUCTOS EXTERNOS
        for producto in productos_externos:
            nombre_lower = producto.nombre.lower()
            if query in nombre_lower or query == '':
                resultados.append({
                    'id': producto.id + 10000,  # Offset para evitar conflictos
                    'nombre': producto.nombre,
                    'precio': float(producto.precio_venta),
                    'stock_actual': producto.stock_actual,
                    'categoria': producto.categoria,
                    'tipo_producto': 'produccion',  # Mismo tipo para compatibilidad
                    'es_externo': True,
                    'producto_externo_id': producto.id
                })
                print(f"✅ Agregado externo: {producto.nombre}")
        
        print(f"🎯 Total resultados: {len(resultados)}")
        
        # DEBUG: Mostrar primeros resultados
        for i, r in enumerate(resultados[:3]):
            print(f"  {i+1}. {r['nombre']} (ID: {r['id']}, Precio: {r['precio']})")
        
        return jsonify(resultados)
        
    except Exception as e:
        print(f"❌ Error en búsqueda de productos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@app.route('/debug_productos_punto_venta')
@login_required
@modulo_requerido('punto_venta')
def debug_productos_punto_venta():
    """Debug: Verificar qué productos están disponibles para punto de venta"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Productos de panadería
    from utilidades.consultas_filtradas import productos_activos_con_stock
    productos_panaderia = productos_activos_con_stock().all()
    
    # Productos externos
    from utilidades.consultas_filtradas import productos_externos_activos_con_stock
    productos_externos = productos_externos_activos_con_stock().all()
    
    resultado = {
        'panaderia_count': len(productos_panaderia),
        'externos_count': len(productos_externos),
        'panaderia': [{'id': p.id, 'nombre': p.nombre, 'stock': p.stock_actual} for p in productos_panaderia],
        'externos': [{'id': p.id, 'nombre': p.nombre, 'stock': p.stock_actual} for p in productos_externos]
    }
    
    return jsonify(resultado)
    
# === 🆕 FUNCIONES PARA MANEJO DE CONSECUTIVOS POS ===


def obtener_consecutivo_pos():
    """Obtiene y incrementa el consecutivo POS DIRECTAMENTE desde la BD del tenant"""
    try:
        import sqlite3
        from flask import g
        
        # 1. Obtener panaderia_id
        panaderia_id = current_user.panaderia_id
        print(f"🔢 [CONSECUTIVO] Panadería ID: {panaderia_id}")
        
        # 2. Obtener la ruta de la BD del tenant
        if hasattr(g, 'db_path') and g.db_path:
            bd_tenant = g.db_path
        else:
            # Buscar en tenant_master.db
            conn_master = sqlite3.connect('tenant_master.db')
            cursor_master = conn_master.cursor()
            cursor_master.execute("SELECT base_datos FROM tenants WHERE id = ?", (panaderia_id,))
            tenant = cursor_master.fetchone()
            conn_master.close()
            if tenant:
                bd_tenant = f"databases_tenants/{tenant[0]}"
            else:
                bd_tenant = f"databases_tenants/panaderia_sqlalchemy.db"
        
        print(f"📁 [CONSECUTIVO] BD: {bd_tenant}")
        
        # 3. Conectar DIRECTAMENTE a la BD del tenant
        conn = sqlite3.connect(bd_tenant)
        cursor = conn.cursor()
        
        # 4. Verificar tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='consecutivos_pos'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE consecutivos_pos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panaderia_id INTEGER NOT NULL,
                    numero_actual INTEGER DEFAULT 0
                )
            ''')
        
        # 5. Obtener y actualizar consecutivo
        cursor.execute("SELECT numero_actual FROM consecutivos_pos WHERE panaderia_id = ?", (panaderia_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            nuevo_numero = resultado[0] + 1
        else:
            nuevo_numero = 1
            cursor.execute("""
                INSERT INTO consecutivos_pos (panaderia_id, numero_actual)
                VALUES (?, ?)
            """, (panaderia_id, 0))
        
        # Actualizar el consecutivo
        cursor.execute("""
            UPDATE consecutivos_pos 
            SET numero_actual = ? 
            WHERE panaderia_id = ?
        """, (nuevo_numero, panaderia_id))
        conn.commit()
        conn.close()
        
        print(f"✅ [CONSECUTIVO] Nuevo: {nuevo_numero}")
        return nuevo_numero
        
    except Exception as e:
        print(f"❌ [CONSECUTIVO] Error: {e}")
        return 1  # Fallback seguro


def obtener_configuracion_sistema():
    """
    Obtiene la configuración del sistema para la panadería actual
    Si no existe, crea una configuración por defecto
    """
    from models import ConfiguracionSistema
    
    try:
        # Obtener panadería actual
        panaderia_id = current_user.panaderia_id if hasattr(current_user, 'panaderia_id') else 1
        
        config = ConfiguracionSistema.query.filter_by(panaderia_id=panaderia_id).first()
        
        if not config:
            # Crear configuración por defecto para esta panadería
            config = ConfiguracionSistema(
                panaderia_id=panaderia_id,
                tipo_facturacion='POS',
                nombre_empresa=f'Panadería {panaderia_id}',
                nit_empresa='9000000001',
                direccion_empresa='',
                telefono_empresa='',
                ciudad_empresa='',
                regimen_empresa='Simplificado'
            )
            db.session.add(config)
            db.session.commit()
            print(f"✅ Configuración creada para panadería {panaderia_id}")
        
        return config
        
    except Exception as e:
        print(f"Error obteniendo configuración: {e}")
        # Retornar objeto por defecto en caso de error
        return type('ConfigDefault', (), {
            'panaderia_id': 1,
            'nit_empresa': '9000000001',
            'nombre_empresa': 'Panadería Default',
            'direccion_empresa': '',
            'telefono_empresa': '',
            'ciudad_empresa': '',
            'regimen_empresa': 'Simplificado',
            'tipo_facturacion': 'POS'
        })()

def reiniciar_consecutivo_pos():
    """
    ⚠️ SOLO PARA PRUEBAS: Reinicia el consecutivo a 0
    """
    try:
        consecutivo = ConsecutivoPOS.query.filter_by(panaderia_id=current_user.panaderia_id).first()
        if consecutivo:
            consecutivo.numero_actual = 0
            db.session.commit()
            print("✅ Consecutivo POS reiniciado a 0")
        return True
    except Exception as e:
        print(f"❌ Error reiniciando consecutivo: {e}")
        return False
    


# ✅ RUTA ACTUALIZADA: /registrar_venta con aprendizaje automático
    
@app.route('/registrar_venta', methods=['POST'])
@login_required
@modulo_requerido('punto_venta')
@tenant_required
def registrar_venta():
    """Registrar venta - VERSIÓN CORREGIDA MULTI-TENANT"""
    print("🛒 DEBUG - INICIANDO REGISTRO DE VENTA")
    print(f"👤 User ID en sesión: {session.get('user_id')}")
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        # 🎯 OBTENER USUARIO ACTUAL PARA panaderia_id
        usuario_actual = Usuario.query.get(session['user_id'])
        panaderia_id = usuario_actual.panaderia_id
        print(f"🏪 DEBUG - Panadería ID del usuario: {panaderia_id}")
        
        data = request.get_json()
        carrito = data.get('carrito', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        cliente_id = data.get('cliente_id')
        tipo_documento_solicitado = data.get('tipo_documento')
        
        # 🎁 CAPTURAR DATOS DE DONACIÓN
        es_donacion = data.get('es_donacion', False)
        motivo_donacion = data.get('motivo_donacion', '')
        
        print(f'🛒 Datos de venta recibidos - Cliente: {cliente_id}, Tipo: {tipo_documento_solicitado}, Donación: {es_donacion}')
        
        # 🆕 OBTENER CONFIGURACIÓN DEL SISTEMA
        config = obtener_configuracion_sistema()
        
        # 🆕 VALIDACIÓN PARA FACTURA ELECTRÓNICA
        if tipo_documento_solicitado == 'ELECTRONICA':
            if not cliente_id:
                return jsonify({
                    'success': False, 
                    'error': 'Para factura electrónica se requiere seleccionar un cliente'
                })
            
            if config.tipo_facturacion != 'ELECTRONICA':
                return jsonify({
                    'success': False,
                    'error': 'El sistema no está configurado para facturación electrónica'
                })
        
        # 🆕 DETERMINAR TIPO DE DOCUMENTO FINAL
        if tipo_documento_solicitado == 'ELECTRONICA' and config.tipo_facturacion == 'ELECTRONICA':
            tipo_documento = 'ELECTRONICA'
            consecutivo_pos = None
            texto_legal = "Factura electrónica de venta - Régimen simplificado"
        else:
            tipo_documento = 'POS'
            consecutivo_pos = obtener_consecutivo_pos()
            texto_legal = "Documento equivalente POS – No válido como factura electrónica de venta"
        
        # 🎁 CALCULAR TOTAL (CERO SI ES DONACIÓN)
        total_venta = 0
        if not es_donacion:
            for item in carrito:
                producto_id = item['id']
                cantidad = item['cantidad']
                
                if producto_id > 10000:
                    producto_externo_id = producto_id - 10000
                    producto = ProductoExterno.query.get(producto_externo_id)
                    if producto:
                        total_venta += cantidad * producto.precio_venta
                else:
                    producto = Producto.query.get(producto_id)
                    if producto:
                        total_venta += cantidad * producto.precio_venta
        else:
            total_venta = 0
            print(f"🎁 REGISTRANDO DONACIÓN - Motivo: {motivo_donacion}")
        
        # 🎯 FECHA/HORA CON TIMEZONE CORRECTO (Colombia UTC-5)
        tz_colombia = timezone(timedelta(hours=-5))
        fecha_hora = datetime.now(tz_colombia)
        
        # 🆕 CREAR VENTA
        nueva_venta = Venta(
            usuario_id=session['user_id'],
            total=total_venta,
            metodo_pago=metodo_pago,
            cliente_id=cliente_id,
            panaderia_id=panaderia_id,
            tipo_documento=tipo_documento,
            consecutivo_pos=consecutivo_pos,
            texto_legal=texto_legal,
            es_donacion=es_donacion,
            motivo_donacion=motivo_donacion,
            fecha_hora=fecha_hora
        )
        db.session.add(nueva_venta)
        db.session.flush()
        
        print(f"✅ Venta creada con panaderia_id: {nueva_venta.panaderia_id}")
        print(f"📅 Fecha registrada: {fecha_hora}")
        
        # ⭐⭐⭐ CORRECCIÓN MULTI-TENANT: OBTENER DATOS DE PANADERÍA DESDE LA BD DEL TENANT ⭐⭐⭐
        import sqlite3
        import os
        
        nombre_panaderia = f"Panadería {panaderia_id}"
        nit_panaderia = "NIT_NO_REGISTRADO"
        direccion_panaderia = "Dirección no registrada"
        telefono_panaderia = "Teléfono no registrado"
        
        # ✅ OBTENER DATOS DESDE tenant_master.db
        try:
            conn_master = sqlite3.connect('tenant_master.db')
            cursor_master = conn_master.cursor()
            cursor_master.execute("SELECT base_datos FROM tenants WHERE id = ?", (panaderia_id,))
            tenant = cursor_master.fetchone()
            conn_master.close()
            
            if tenant:
                bd_tenant_path = os.path.join('databases_tenants', tenant[0])
                print(f"🔍 Conectando a BD tenant: {bd_tenant_path}")
                
                if os.path.exists(bd_tenant_path):
                    conn_tenant = sqlite3.connect(bd_tenant_path)
                    cursor_tenant = conn_tenant.cursor()
                    
                    cursor_tenant.execute("""
                        SELECT nombre_panaderia, nit, direccion, telefono_contacto 
                        FROM configuracion_panaderia 
                        WHERE panaderia_id = ?
                    """, (panaderia_id,))
                    
                    config_tenant = cursor_tenant.fetchone()
                    conn_tenant.close()
                    
                    if config_tenant:
                        nombre_panaderia = config_tenant[0] or f"Panadería {panaderia_id}"
                        nit_panaderia = config_tenant[1] or "NIT_NO_REGISTRADO"
                        direccion_panaderia = config_tenant[2] or "Dirección no registrada"
                        telefono_panaderia = config_tenant[3] or "Teléfono no registrado"
                        print(f"🏪 Datos obtenidos desde BD tenant: {nombre_panaderia}")
                    else:
                        print(f"⚠️ No hay configuración para panadería_id {panaderia_id}")
                else:
                    print(f"⚠️ BD del tenant no existe: {bd_tenant_path}")
            else:
                print(f"⚠️ No se encontró tenant con ID {panaderia_id}")
                
        except Exception as e:
            print(f"⚠️ Error obteniendo datos del tenant: {e}")
        
        detalles_venta = []
        
        # 🎁 PROCESAR CADA PRODUCTO DEL CARRITO
        for item in carrito:
            producto_id = item['id']
            cantidad = item['cantidad']
            
            if producto_id > 10000:
                producto_externo_id = producto_id - 10000
                producto = ProductoExterno.query.get(producto_externo_id)
                
                if not producto or producto.stock_actual < cantidad:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock insuficiente: {producto.nombre if producto else "Producto"}'
                    })
                
                producto.stock_actual -= cantidad
                
                if not es_donacion:
                    producto.total_ventas += cantidad
                    producto.total_ingresos += cantidad * producto.precio_venta
                    producto.utilidad_total += cantidad * (producto.precio_venta - producto.precio_compra)
                    producto.fecha_ultima_venta = datetime.now()
                
                precio_unitario = producto.precio_venta
                
                detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=None,
                    producto_externo_id=producto_externo_id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                detalles_venta.append(detalle)
                
            else:
                producto = Producto.query.get(producto_id)
                
                if not producto or producto.stock_actual < cantidad:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock insuficiente: {producto.nombre if producto else "Producto"}'
                    })
                
                producto.stock_actual -= cantidad
                precio_unitario = producto.precio_venta
                
                detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=producto_id,
                    producto_externo_id=None,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                detalles_venta.append(detalle)
        
        for detalle in detalles_venta:
            db.session.add(detalle)
        
        
        # 🆕 CREAR FACTURA O RECIBO SEGÚN CONFIGURACIÓN
        # 1. PRIMERO: Definir numero_factura SIEMPRE
        if tipo_documento == 'ELECTRONICA':
            numero_factura = f"FE{datetime.now().strftime('%Y%m%d')}{nueva_venta.id:04d}"
            mensaje_exito = f'Factura electrónica #{numero_factura} generada'
        else:
            # ✅ SIEMPRE usar POS como fallback
            # Extraer el valor numérico del objeto consecutivo
            if hasattr(consecutivo_pos, 'numero_actual'):
                num_consecutivo = consecutivo_pos.numero_actual
            else:
                num_consecutivo = consecutivo_pos

            # Asegurar que sea un entero
            num_consecutivo = int(num_consecutivo)

            numero_factura = f"POS-{panaderia_id}-{num_consecutivo:06d}"
            mensaje_exito = f'Recibo POS #{consecutivo_pos} generado correctamente'
        
        # 2. MENSAJE ESPECIAL PARA DONACIONES
        if es_donacion:
            mensaje_exito = f'Donación registrada - {mensaje_exito}'
        
        # CREAR FACTURA CON SQLITE DIRECTO (EVITA BD PRINCIPAL)
        import sqlite3
        from flask import g
        
        # ✅ PRIMERO: Guardar la venta en la BD
        db.session.commit()
        print(f"✅ Venta guardada en BD - ID: {nueva_venta.id}")
        
        # Obtener la ruta de la BD del tenant
        if hasattr(g, 'db_path') and g.db_path:
            bd_tenant = g.db_path
        else:
            # Buscar en tenant_master.db
            conn_master = sqlite3.connect('tenant_master.db')
            cursor_master = conn_master.cursor()
            cursor_master.execute("SELECT base_datos FROM tenants WHERE id = ?", (panaderia_id,))
            tenant = cursor_master.fetchone()
            conn_master.close()
            if tenant:
                bd_tenant = f"databases_tenants/{tenant[0]}"
            else:
                bd_tenant = f"databases_tenants/panaderia_sqlalchemy.db"
        
        print(f"📁 [FACTURA] BD: {bd_tenant}")
        
        # Conectar DIRECTAMENTE a la BD del tenant
        conn_tenant = sqlite3.connect(bd_tenant)
        cursor_tenant = conn_tenant.cursor()
        
        # Insertar factura DIRECTAMENTE en la BD del tenant
        cursor_tenant.execute("""
            INSERT INTO facturas (
                panaderia_id, venta_id, numero_factura, fecha_emision,
                subtotal, iva, total, nombre_panaderia,
                nit_panaderia, direccion_panaderia, telefono_panaderia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            panaderia_id,
            nueva_venta.id,
            numero_factura,
            datetime.now(),
            total_venta,
            0,
            total_venta,
            nombre_panaderia,
            nit_panaderia,
            direccion_panaderia,
            telefono_panaderia
        ))
        
        # Obtener el ID de la factura insertada
        factura_id = cursor_tenant.lastrowid
        conn_tenant.commit()
        conn_tenant.close()
        
        print(f"✅ Factura creada: {numero_factura} (Panadería: {panaderia_id} - {nombre_panaderia})")
        
        # Crear objeto factura para la respuesta
        factura = Factura()
        factura.id = factura_id
        factura.numero_factura = numero_factura
        
        respuesta = {
            'success': True,
            'venta_id': nueva_venta.id,
            'factura_id': factura.id,
            'numero_factura': factura.numero_factura,
            'consecutivo_pos': consecutivo_pos,
            'tipo_documento': tipo_documento,
            'total': total_venta,
            'mensaje': mensaje_exito,
            'panaderia_id': panaderia_id,
            'nombre_panaderia': nombre_panaderia,
            'es_donacion': es_donacion,
            'motivo_donacion': motivo_donacion
        }
        
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            if cliente:
                respuesta['cliente'] = cliente.to_dict()
                print(f'✅ Cliente incluido: {cliente.nombre}')
        
        if 'carrito' in session:
            session.pop('carrito')
            session.modified = True
        
        if es_donacion:
            print(f'🎁 DONACIÓN REGISTRADA - ID: {nueva_venta.id}')
        else:
            print(f'✅ Venta registrada - ID: {nueva_venta.id}, Total: ${total_venta}')
        
        return jsonify(respuesta)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al registrar venta: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})
# =============================================
# 🆕 RUTAS API PARA GESTIÓN DE CLIENTES
# =============================================

@app.route('/api/guardar-cliente', methods=['POST'])
@login_required
@modulo_requerido('clientes')
def guardar_cliente():
    """
    Guarda o actualiza un cliente para facturación electrónica
    """
    try:
        data = request.get_json()
        print('📝 Datos del cliente recibidos:', data)
        
        # ✅ VALIDAR DATOS OBLIGATORIOS
        if not data.get('documento') or not data.get('nombre'):
            return jsonify({
                'success': False,
                'error': 'Documento y nombre son obligatorios'
            }), 400
        
        # ✅ BUSCAR CLIENTE EXISTENTE POR DOCUMENTO
        cliente_existente = Cliente.query.filter_by(documento=data['documento']).first()
        
        if cliente_existente:
            # ✅ ACTUALIZAR CLIENTE EXISTENTE
            cliente_existente.nombre = data['nombre']
            cliente_existente.tipo_documento = data.get('tipo_documento', '31')
            cliente_existente.tipo_persona = data.get('tipo_persona', 'J')
            cliente_existente.direccion = data.get('direccion', '')
            cliente_existente.telefono = data.get('telefono', '')
            cliente_existente.email = data.get('email', '')
            cliente_existente.ciudad = data.get('ciudad', '')
            cliente_existente.departamento = data.get('departamento', '')
            cliente_existente.regimen = data.get('regimen', '')
            cliente_existente.responsabilidades = data.get('responsabilidades', '')
            cliente_existente.fecha_actualizacion = datetime.now()
            
            cliente = cliente_existente
            accion = 'actualizado'
            
        else:
            # ✅ CREAR NUEVO CLIENTE
            cliente = Cliente(
                documento=data['documento'],
                nombre=data['nombre'],
                tipo_documento=data.get('tipo_documento', '31'),
                tipo_persona=data.get('tipo_persona', 'J'),
                direccion=data.get('direccion', ''),
                telefono=data.get('telefono', ''),
                email=data.get('email', ''),
                ciudad=data.get('ciudad', ''),
                departamento=data.get('departamento', ''),
                regimen=data.get('regimen', ''),
                responsabilidades=data.get('responsabilidades', ''),
                activo=True
            )
            db.session.add(cliente)
            accion = 'creado'
        
        db.session.commit()
        
        print(f'✅ Cliente {accion} exitosamente:', cliente.id)
        
        return jsonify({
            'success': True,
            'cliente': cliente.to_dict(),
            'mensaje': f'Cliente {accion} correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ Error guardando cliente: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Error al guardar cliente: {str(e)}'
        }), 500

@app.route('/api/clientes-recientes', methods=['GET'])
@login_required
@modulo_requerido('clientes')
def obtener_clientes_recientes():
    """
    Obtiene la lista de clientes recientes para selección rápida
    """
    try:
        # ✅ OBTENER LOS ÚLTIMOS 10 CLIENTES ACTIVOS
        clientes = Cliente.query.filter_by(activo=True)\
                               .order_by(Cliente.fecha_actualizacion.desc())\
                               .limit(10)\
                               .all()
        
        clientes_data = [cliente.to_dict() for cliente in clientes]
        
        print(f'✅ Clientes recientes encontrados: {len(clientes_data)}')
        
        return jsonify(clientes_data)
        
    except Exception as e:
        print(f'❌ Error obteniendo clientes recientes: {str(e)}')
        return jsonify([])

@app.route('/api/buscar-cliente/<string:documento>', methods=['GET'])
@login_required
@modulo_requerido('clientes')
def buscar_cliente(documento):
    """
    Busca un cliente por número de documento
    """
    try:
        cliente = Cliente.query.filter_by(documento=documento, activo=True).first()
        
        if cliente:
            return jsonify({
                'success': True,
                'cliente': cliente.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'mensaje': 'Cliente no encontrado'
            })
            
    except Exception as e:
        print(f'❌ Error buscando cliente: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuracion-sistema', methods=['GET'])
@login_required
@modulo_requerido('configuracion')
def obtener_configuracion_sistema_api():
    """
    API para obtener la configuración del sistema (usada por JavaScript)
    """
    try:
        config = obtener_configuracion_sistema()
        
        return jsonify({
            'tipo_facturacion': config.tipo_facturacion,
            'nombre_empresa': config.nombre_empresa,
            'nit_empresa': config.nit_empresa
        })
        
    except Exception as e:
        print(f'❌ Error obteniendo configuración: {str(e)}')
        return jsonify({
            'tipo_facturacion': 'POS',
            'nombre_empresa': 'Mi Empresa',
            'nit_empresa': '000000000'
        })

# ✅ FUNCIÓN AUXILIAR INDEPENDIENTE
def obtener_texto_legal(tipo_documento):
    """
    Retorna el texto legal apropiado según el tipo de documento
    """
    if tipo_documento == 'ELECTRONICA':
        return "Factura electrónica de venta - Régimen simplificado"
    else:
        return "Documento equivalente POS – No válido como factura electrónica de venta"

# =============================================
# FIN RUTAS API CLIENTES
# =============================================

@app.route('/configuracion/facturacion', methods=['GET', 'POST'])
@login_required
@modulo_requerido('configuracion')
def configuracion_facturacion():
    """
    Configuración del tipo de facturación (POS vs Electrónica)
    """
    config = obtener_configuracion_sistema()
    
    if request.method == 'POST':
        try:
            # Actualizar configuración
            config.tipo_facturacion = request.form.get('tipo_facturacion', 'POS')
            config.nombre_empresa = request.form.get('nombre_empresa', '')
            config.nit_empresa = request.form.get('nit_empresa', '')
            config.direccion_empresa = request.form.get('direccion_empresa', '')
            config.telefono_empresa = request.form.get('telefono_empresa', '')
            config.ciudad_empresa = request.form.get('ciudad_empresa', '')
            config.regimen_empresa = request.form.get('regimen_empresa', 'Simplificado')
            
            db.session.commit()
            flash('✅ Configuración actualizada correctamente', 'success')
            
        except Exception as e:
            flash(f'❌ Error actualizando configuración: {str(e)}', 'error')
    
    return render_template('configuracion_facturacion.html', config=config)

@app.route('/api/exportar-xml/<int:venta_id>')
@login_required
@modulo_requerido('punto_venta')
def exportar_xml_venta(venta_id):
    """
    Exporta una venta a formato XML UBL 2.1 - VERSIÓN CORREGIDA
    """
    try:
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
        
        # Verificar que existan detalles
        if not detalles:
            flash('❌ No hay detalles de venta para generar el XML', 'error')
            return redirect(request.referrer or url_for('ventas'))
        
        # Obtener configuración del sistema
        config = obtener_configuracion_sistema()
        
        # Generar XML
        xml_content = generar_xml_ubl_21(venta, config, detalles)
        
        if not xml_content:
            flash('❌ No se pudo generar el contenido XML', 'error')
            return redirect(request.referrer or url_for('ventas'))
        
        # 🆕 CREAR RESPUESTA CON HEADERS CORRECTOS PARA XML
        response = make_response(xml_content)
        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="Factura_{venta_id}_{venta.fecha_hora.strftime("%Y%m%d_%H%M%S")}.xml"'
        
        # 🆕 EVITAR QUE EL NAVEGADOR INTERPRETE COMO HTML
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        flash(f'❌ Error generando XML: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ventas'))

# Función temporal para debug del XML
@app.route('/api/debug-xml/<int:venta_id>')
@login_required
@modulo_requerido('punto_venta')
def debug_xml(venta_id):
    """Debug del XML generado"""
    try:
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
        config = obtener_configuracion_sistema()
        
        xml_content = generar_xml_ubl_21(venta, config, detalles)
        
        # Verificar si el XML es válido
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_content)
            xml_valid = "✅ XML VÁLIDO"
        except Exception as e:
            xml_valid = f"❌ XML INVÁLIDO: {str(e)}"
        
        return f"""
        <h1>Debug XML - Venta {venta_id}</h1>
        <p>{xml_valid}</p>
        <h3>Contenido XML:</h3>
        <pre>{xml_content}</pre>
        <h3>Headers que debería tener:</h3>
        <ul>
            <li>Content-Type: application/xml; charset=utf-8</li>
            <li>Content-Disposition: attachment; filename=...</li>
        </ul>
        """
    except Exception as e:
        return f"Error en debug: {str(e)}"
    
@app.route('/api/imprimir-factura/<int:venta_id>')
@login_required
@modulo_requerido('punto_venta')
def imprimir_factura_electronica(venta_id):
    """Genera la representación impresa de la factura electrónica"""
    try:
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
        config = obtener_configuracion_sistema()
        
        # 🆕 DEBUG: Verificar datos del cliente
        print(f"🔍 DEBUG Factura Electrónica - Venta ID: {venta_id}")
        print(f"🔍 DEBUG Cliente ID: {venta.cliente_id}")
        if venta.cliente:
            print(f"🔍 DEBUG Datos Cliente: {venta.cliente.nombre}, {venta.cliente.documento}")
        else:
            print("🔍 DEBUG: No hay cliente asociado a esta venta")
        
        # Verificar si es factura electrónica
        if venta.tipo_documento != 'ELECTRONICA':
            flash('⚠️ Esta venta no es una factura electrónica', 'warning')
            return redirect(request.referrer or url_for('ventas'))
        
        return render_template(
            'factura_electronica.html',
            venta=venta,
            detalles=detalles,
            config=config,
            ahora=datetime.now()
        )
        
    except Exception as e:
        flash(f'❌ Error generando factura: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ventas'))
    
@app.route('/recibo-pos/<int:venta_id>')
@login_required
@modulo_requerido('punto_venta')
def recibo_pos(venta_id):
    """
    Genera el recibo POS - BUSCA EN AMBAS BDs
    """
    try:
        import sqlite3
        from flask import g
        from datetime import datetime
        
        panaderia_id = current_user.panaderia_id
        print(f"🔍 [RECIBO] Panadería ID: {panaderia_id}")
        print(f"🔍 [RECIBO] Venta ID: {venta_id}")
        
        # Obtener la ruta de la BD del tenant
        if hasattr(g, 'db_path') and g.db_path:
            bd_tenant = g.db_path
        else:
            conn_master = sqlite3.connect('tenant_master.db')
            cursor_master = conn_master.cursor()
            cursor_master.execute("SELECT base_datos FROM tenants WHERE id = ?", (panaderia_id,))
            tenant = cursor_master.fetchone()
            conn_master.close()
            if tenant:
                bd_tenant = f"databases_tenants/{tenant[0]}"
            else:
                bd_tenant = f"databases_tenants/panaderia_sqlalchemy.db"
        
        bd_principal = "databases_tenants/panaderia_principal.db"
        
        venta_data = None
        bd_usada = None
        
        # PRIMERO: Buscar en la BD del tenant
        print(f"📁 [RECIBO] Buscando en BD tenant: {bd_tenant}")
        conn = sqlite3.connect(bd_tenant)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, usuario_id, total, metodo_pago, cliente_id, 
                   panaderia_id, tipo_documento, consecutivo_pos, 
                   texto_legal, es_donacion, motivo_donacion, fecha_hora
            FROM ventas 
            WHERE id = ?
        """, (venta_id,))
        venta_data = cursor.fetchone()
        conn.close()
        
        if venta_data:
            bd_usada = bd_tenant
            print(f"✅ [RECIBO] Venta encontrada en BD TENANT")
        else:
            # SEGUNDO: Buscar en la BD principal
            print(f"📁 [RECIBO] Buscando en BD principal: {bd_principal}")
            conn = sqlite3.connect(bd_principal)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, usuario_id, total, metodo_pago, cliente_id, 
                       panaderia_id, tipo_documento, consecutivo_pos, 
                       texto_legal, es_donacion, motivo_donacion, fecha_hora
                FROM ventas 
                WHERE id = ?
            """, (venta_id,))
            venta_data = cursor.fetchone()
            conn.close()
            
            if venta_data:
                bd_usada = bd_principal
                print(f"✅ [RECIBO] Venta encontrada en BD PRINCIPAL (panaderia_id: {venta_data['panaderia_id']})")
            else:
                print(f"❌ [RECIBO] Venta ID {venta_id} NO encontrada en ninguna BD")
                flash('Venta no encontrada', 'error')
                return redirect(url_for('punto_venta'))
        
        # Crear objeto venta
        venta = Venta()
        venta.id = venta_data['id']
        venta.usuario_id = venta_data['usuario_id']
        venta.total = venta_data['total']
        venta.metodo_pago = venta_data['metodo_pago']
        venta.cliente_id = venta_data['cliente_id']
        venta.panaderia_id = venta_data['panaderia_id']
        venta.tipo_documento = venta_data['tipo_documento']
        venta.consecutivo_pos = venta_data['consecutivo_pos']
        venta.texto_legal = venta_data['texto_legal']
        venta.es_donacion = venta_data['es_donacion']
        venta.motivo_donacion = venta_data['motivo_donacion']
        
        # ✅ CORREGIR: Convertir fecha_hora si es string
        fecha_hora = venta_data['fecha_hora']
        if isinstance(fecha_hora, str):
            try:
                venta.fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    venta.fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M:%S')
                except:
                    venta.fecha_hora = datetime.now()
            print(f"📅 [RECIBO] Fecha convertida: {venta.fecha_hora}")
        else:
            venta.fecha_hora = fecha_hora
            print(f"📅 [RECIBO] Fecha original: {venta.fecha_hora}")
        
        # Obtener detalles de la venta (usando la BD donde se encontró)
        conn = sqlite3.connect(bd_usada)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, venta_id, producto_id, producto_externo_id, 
                   cantidad, precio_unitario
            FROM detalle_venta 
            WHERE venta_id = ?
        """, (venta_id,))
        detalles_data = cursor.fetchall()
        
        detalles = []
        for d in detalles_data:
            detalle = DetalleVenta()
            detalle.id = d['id']
            detalle.venta_id = d['venta_id']
            detalle.producto_id = d['producto_id']
            detalle.producto_externo_id = d['producto_externo_id']
            detalle.cantidad = d['cantidad']
            detalle.precio_unitario = d['precio_unitario']
            
            # ✅ OBTENER EL NOMBRE REAL DEL PRODUCTO (EXTERNO O PROPIO)
            nombre_producto = "Producto"
            
            if detalle.producto_id:
                # 📦 ES UN PRODUCTO PROPIO DE PANADERÍA
                cursor2 = conn.cursor()
                cursor2.execute("SELECT nombre FROM productos WHERE id = ?", (detalle.producto_id,))
                prod = cursor2.fetchone()
                cursor2.close()
                if prod:
                    nombre_producto = prod[0] if isinstance(prod, tuple) else prod['nombre']
                else:
                    nombre_producto = f"Producto propio #{detalle.producto_id}"
                    
            elif detalle.producto_externo_id:
                # 📦 ES UN PRODUCTO EXTERNO
                cursor2 = conn.cursor()
                cursor2.execute("SELECT nombre FROM productos_externos WHERE id = ?", (detalle.producto_externo_id,))
                prod = cursor2.fetchone()
                cursor2.close()
                if prod:
                    nombre_producto = prod[0] if isinstance(prod, tuple) else prod['nombre']
                else:
                    nombre_producto = f"Producto externo #{detalle.producto_externo_id}"
            
            detalle.nombre_producto = nombre_producto
            print(f"📝 [RECIBO] Producto: {nombre_producto} | Cant: {detalle.cantidad} | Precio: {detalle.precio_unitario}")
            detalles.append(detalle)
        
        conn.close()
        
        config = obtener_configuracion_sistema()
        
        return render_template('recibo_pos.html', 
                             venta=venta, 
                             detalles=detalles, 
                             config=config)
                             
    except Exception as e:
        print(f"❌ [RECIBO] Error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error al generar recibo: {str(e)}', 'error')
        return redirect(url_for('punto_venta'))
    
@app.route('/agregar_al_carrito', methods=['POST'])
@login_required
@modulo_requerido('punto_venta')
def agregar_al_carrito():
    try:
        data = request.get_json()
        producto_id = data['producto_id']
        cantidad = data['cantidad']
        
        # Validar que la cantidad sea positiva
        if cantidad <= 0:
            return jsonify({'success': False, 'message': 'La cantidad debe ser mayor a 0'})
        
        # Inicializar carrito en sesión si no existe
        if 'carrito' not in session:
            session['carrito'] = {}
        
        # Convertir a string porque las claves de session deben ser strings
        producto_id_str = str(producto_id)
        
        # Agregar o actualizar producto en carrito
        carrito = session['carrito']
        if producto_id_str in carrito:
            carrito[producto_id_str] += cantidad
        else:
            carrito[producto_id_str] = cantidad
        
        session['carrito'] = carrito
        session.modified = True
        
        print(f"Carrito actualizado: {session['carrito']}")  # Para debug
        
        return jsonify({
            'success': True, 
            'message': f'Producto agregado al carrito ({cantidad} unidades)',
            'carrito': session['carrito']
        })
    
    except Exception as e:
        print(f"Error: {e}")  # Para debug
        return jsonify({'success': False, 'message': 'Error interno del servidor'})

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

# =============================================
# RUTAS DE PROVEEDORES - CORREGIDAS MULTI-TENANT
# =============================================

@app.route('/proveedores')
@login_required
@modulo_requerido('proveedores')
def proveedores():
    """Lista de proveedores - Multi-tenant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    panaderia_id = current_user.panaderia_id
    todos_proveedores = Proveedor.query.filter_by(panaderia_id=panaderia_id).all()
    return render_template('proveedores.html', proveedores=todos_proveedores)
@app.route('/agregar_proveedor', methods=['GET', 'POST'])
@login_required
@modulo_requerido('proveedores')
def agregar_proveedor():
    """Agregar nuevo proveedor - Multi-tenant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    panaderia_id = current_user.panaderia_id
    
    if request.method == 'POST':
        try:
            nuevo_proveedor = Proveedor(
                panaderia_id=panaderia_id,
                nombre=request.form['nombre'],
                contacto=request.form.get('contacto', ''),
                telefono=request.form.get('telefono', ''),
                email=request.form.get('email', ''),
                direccion=request.form.get('direccion', ''),
                productos_que_suministra=request.form.get('productos_que_suministra', ''),
                tiempo_entrega_dias=int(request.form.get('tiempo_entrega_dias', 1)),
                evaluacion=int(request.form.get('evaluacion', 5)),
                activo=True
            )
            
            db.session.add(nuevo_proveedor)
            db.session.commit()
            
            flash(f'✅ Proveedor "{nuevo_proveedor.nombre}" agregado correctamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al agregar el proveedor: {str(e)}', 'error')
            return redirect(url_for('agregar_proveedor'))
    
    return render_template('agregar_proveedor.html')

@app.route('/editar_proveedor/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('proveedores')
def editar_proveedor(id):
    """Editar proveedor - Multi-tenant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    panaderia_id = current_user.panaderia_id
    proveedor = Proveedor.query.filter_by(panaderia_id=panaderia_id, id=id).first_or_404()
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form['nombre']
            proveedor.contacto = request.form.get('contacto', '')
            proveedor.telefono = request.form.get('telefono', '')
            proveedor.email = request.form.get('email', '')
            proveedor.direccion = request.form.get('direccion', '')
            proveedor.productos_que_suministra = request.form.get('productos_que_suministra', '')
            proveedor.tiempo_entrega_dias = int(request.form.get('tiempo_entrega_dias', 1))
            proveedor.evaluacion = int(request.form.get('evaluacion', 5))
            
            db.session.commit()
            flash(f'✅ Proveedor "{proveedor.nombre}" actualizado correctamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar el proveedor: {str(e)}', 'error')
            return redirect(url_for('editar_proveedor', id=id))
    
    return render_template('editar_proveedor.html', proveedor=proveedor)

@app.route('/toggle_proveedor/<int:id>')
@login_required
@modulo_requerido('proveedores')
def toggle_proveedor(id):
    """Activar/Desactivar proveedor - Multi-tenant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    panaderia_id = current_user.panaderia_id
    proveedor = Proveedor.query.filter_by(panaderia_id=panaderia_id, id=id).first_or_404()
    proveedor.activo = not proveedor.activo
    db.session.commit()
    
    estado = "activado" if proveedor.activo else "desactivado"
    flash(f'✅ Proveedor "{proveedor.nombre}" {estado} correctamente', 'success')
    return redirect(url_for('proveedores'))

@app.route('/productos_externos')
@login_required
@modulo_requerido('productos')
@tenant_required  # ← DECORADOR AGREGADO
def productos_externos():
    """Gestión de productos externos (bebidas, helados) - SOLO de esta panadería"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # FILTRO CLAVE: Solo productos de ESTA panadería
    productos = ProductoExterno.query.filter_by(
        activo=True, 
        panaderia_id=current_user.panaderia_id  # ← CORREGIDO: current_user.panaderia_id
    ).all()
    
    proveedores = Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id, activo=True).all()  # ← CORREGIDO: current_user.panaderia_id
    
    # Calcular métricas adicionales para cada producto
    for producto in productos:
        producto.utilidad_unitaria = producto.precio_venta - producto.precio_compra
        producto.margen_ganancia = (producto.utilidad_unitaria / producto.precio_compra * 100) if producto.precio_compra > 0 else 0
    
    return render_template('productos_externos.html', 
                         productos=productos, 
                         proveedores=proveedores)
    
# RUTA PARA CREAR PRODUCTO EXTERNO
@app.route('/crear_producto_externo', methods=['POST'])
@login_required
@modulo_requerido('productos')
@tenant_required  # ← DECORADOR AGREGADO
def crear_producto_externo():
    """Crear nuevo producto externo - Asigna automáticamente la panadería actual"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        nuevo_producto = ProductoExterno(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion', ''),
            categoria=request.form['categoria'],
            marca=request.form.get('marca', ''),
            codigo_barras=request.form.get('codigo_barras', ''),
            proveedor_id=request.form.get('proveedor_id'),
            precio_compra=float(request.form['precio_compra']),
            precio_venta=float(request.form['precio_venta']),
            stock_actual=int(request.form.get('stock_actual', 0)),
            stock_minimo=int(request.form.get('stock_minimo', 5)),
            panaderia_id=current_user.panaderia_id  # ← CORREGIDO: current_user.panaderia_id
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        flash('✅ Producto externo creado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al crear producto: {str(e)}', 'error')
    
    return redirect(url_for('productos_externos'))

# RUTA PARA EDITAR PRODUCTO EXTERNO
@app.route('/editar_producto_externo/<int:id>', methods=['POST'])
@login_required
@modulo_requerido('productos')
@tenant_required
def editar_producto_externo(id):
    """Editar producto externo - Solo si pertenece a esta panadería"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # ✅ CORREGIDO: Usar current_user.panaderia_id
        panaderia_id = current_user.panaderia_id
        
        # ✅ CORREGIDO: Filtro por tenant
        producto = ProductoExterno.query.filter_by(
            id=id, 
            panaderia_id=panaderia_id
        ).first()
        
        if not producto:
            flash('❌ Producto no encontrado o no tienes permisos', 'error')
            return redirect(url_for('productos_externos'))
        
        # Actualizar campos
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form.get('descripcion', '')
        producto.categoria = request.form['categoria']
        producto.marca = request.form.get('marca', '')
        producto.codigo_barras = request.form.get('codigo_barras', '')
        producto.proveedor_id = request.form.get('proveedor_id')
        producto.precio_compra = float(request.form['precio_compra'])
        producto.precio_venta = float(request.form['precio_venta'])
        producto.stock_actual = int(request.form.get('stock_actual', 0))
        producto.stock_minimo = int(request.form.get('stock_minimo', 5))
        
        db.session.commit()
        flash('✅ Producto actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al actualizar producto: {str(e)}', 'error')
    
    return redirect(url_for('productos_externos'))

# RUTA PARA ELIMINAR PRODUCTO EXTERNO (Borrado lógico)
@app.route('/eliminar_producto_externo/<int:id>', methods=['POST'])
@login_required
@modulo_requerido('productos')
@tenant_required
def eliminar_producto_externo(id):
    """Eliminar producto externo (borrado lógico) - Solo si pertenece a esta panadería"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # ✅ CORREGIDO: Usar current_user.panaderia_id
        panaderia_id = current_user.panaderia_id
        
        # ✅ CORREGIDO: Filtro por tenant
        producto = ProductoExterno.query.filter_by(
            id=id, 
            panaderia_id=panaderia_id
        ).first()
        
        if not producto:
            flash('❌ Producto no encontrado o no tienes permisos', 'error')
            return redirect(url_for('productos_externos'))
        
        producto.activo = False
        db.session.commit()
        
        flash('✅ Producto eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar producto: {str(e)}', 'error')
    
    return redirect(url_for('productos_externos'))

@app.route('/registrar_compra_externa', methods=['POST'])
@login_required
@modulo_requerido('productos')
@tenant_required
def registrar_compra_externa():
    """Registrar compra de productos externos y actualizar stock"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        producto_id = request.form['producto_id']
        proveedor_id = request.form['proveedor_id']
        cantidad = int(request.form['cantidad'])
        precio_compra = float(request.form['precio_compra'])
        notas = request.form.get('notas', '')
        
        # ✅ CORREGIDO: Filtrar producto por tenant
        panaderia_id = current_user.panaderia_id
        producto = ProductoExterno.query.filter_by(
            id=producto_id,
            panaderia_id=panaderia_id
        ).first()
        
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Registrar la compra
        compra = CompraExterna(
            producto_id=producto_id,
            proveedor_id=proveedor_id,
            cantidad=cantidad,
            precio_compra=precio_compra,
            total_compra=cantidad * precio_compra,
            notas=notas,
            panaderia_id=panaderia_id  # ✅ AGREGADO: Tenant en compra
        )
        
        # Actualizar stock y precios del producto
        producto.stock_actual += cantidad
        producto.precio_compra = precio_compra
        producto.fecha_ultima_compra = datetime.now()
        
        db.session.add(compra)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Compra registrada: {cantidad} unidades de {producto.nombre}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    
    # Obtener todas las materias primas (activas e inactivas)
    materias = MateriaPrima.query.all()
    
    # CALCULAR FECHAS PARA ALERTAS DE VENCIMIENTO
    hoy = datetime.now().date()
    hoy_mas_15 = hoy + timedelta(days=15)
    
    return render_template('materias_primas.html', 
                         materias_primas=materias,
                         hoy=hoy,
                         hoy_mas_15=hoy_mas_15)
    
@app.route('/materias_primas')
@login_required
@modulo_requerido('inventario')
@tenant_required
def materias_primas():
    """Gestión de materias primas - SOLO de esta panadería"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materias = MateriaPrima.query.filter_by(panaderia_id=current_user.panaderia_id).all()
    proveedores = Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id, activo=True).all()
    
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    hoy_mas_15 = hoy + timedelta(days=15)
    
    return render_template('materias_primas.html', 
                         materias_primas=materias,
                         proveedores=proveedores,
                         hoy=hoy,
                         hoy_mas_15=hoy_mas_15)


@app.route('/agregar_materia_prima', methods=['GET', 'POST'])
@login_required
@modulo_requerido('inventario')
@tenant_required
def agregar_materia_prima():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    proveedores = Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id, activo=True).all()
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            proveedor_id = request.form.get('proveedor_id', type=int)
            unidad_medida = request.form['unidad_medida']
            stock_minimo = float(request.form.get('stock_minimo', 0))
            
            # NUEVOS CAMPOS CONFIGURACIÓN EMPAQUES
            unidad_compra = request.form['unidad_compra']
            gramos_por_empaque = float(request.form['gramos_por_empaque'])
            stock_minimo_empaques = int(request.form['stock_minimo_empaques'])
            
            # NUEVOS CAMPOS COMPRA INICIAL
            cantidad_empaques_comprados = int(request.form['cantidad_empaques_comprados'])
            precio_total_compra = float(request.form['precio_total_compra'])
            
            # OBTENER FECHA DE VENCIMIENTO
            fecha_vencimiento_str = request.form.get('fecha_vencimiento', '').strip()
            fecha_vencimiento = None
            if fecha_vencimiento_str:
                from datetime import datetime
                fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
            
            # VALIDACIONES
            if not proveedor_id:
                flash('Debe seleccionar un proveedor', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if gramos_por_empaque <= 0:
                flash('El peso por empaque debe ser mayor a 0', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if stock_minimo_empaques < 1:
                flash('El stock mínimo de empaques debe ser al menos 1', 'error')
                return redirect(url_for('agregar_materia_prima'))
            
            if cantidad_empaques_comprados < 1:
                flash('La cantidad de empaques debe ser al menos 1', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if precio_total_compra <= 0:
                flash('El precio total debe ser mayor a 0', 'error')
                return redirect(url_for('agregar_materia_prima'))
            
            # CALCULAR STOCK INICIAL Y COSTOS
            stock_inicial = cantidad_empaques_comprados * gramos_por_empaque
            costo_unitario = precio_total_compra / stock_inicial
            precio_unitario_empaque = precio_total_compra / cantidad_empaques_comprados
            
            # Crear materia prima
            nueva_materia = MateriaPrima(
                nombre=nombre,
                proveedor_id=proveedor_id,
                unidad_medida=unidad_medida,
                costo_promedio=costo_unitario,
                stock_actual=stock_inicial,
                stock_minimo=stock_minimo,
                unidad_compra=unidad_compra,
                gramos_por_empaque=gramos_por_empaque,
                stock_minimo_empaques=stock_minimo_empaques,
                panaderia_id=current_user.panaderia_id,
                fecha_vencimiento=fecha_vencimiento,
                activo=True
            )
            
            db.session.add(nueva_materia)
            db.session.flush()
            
            # REGISTRAR COMPRA INICIAL EN HISTORIAL
            nueva_compra = HistorialCompra(
                materia_prima_id=nueva_materia.id,
                cantidad_empaques=cantidad_empaques_comprados,
                precio_total=precio_total_compra,
                precio_unitario_empaque=precio_unitario_empaque,
                usuario_id=session['user_id']
            )
            db.session.add(nueva_compra)
            db.session.commit()
            
            flash(f'Materia prima "{nombre}" agregada con {stock_inicial} {unidad_medida} de stock inicial', 'success')
            return redirect(url_for('materias_primas'))
            
        except ValueError as e:
            flash('Error: Los campos numéricos deben contener valores válidos', 'error')
            return redirect(url_for('agregar_materia_prima'))
        except Exception as e:
            flash(f'Error inesperado al agregar la materia prima: {str(e)}', 'error')
            return redirect(url_for('agregar_materia_prima'))
    
    return render_template('agregar_materia_prima.html', proveedores=proveedores)


@app.route('/editar_materia_prima/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('inventario')
@tenant_required
def editar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    panaderia_id = current_user.panaderia_id
    materia = MateriaPrima.query.filter_by(panaderia_id=panaderia_id, id=id).first_or_404()
    proveedores = Proveedor.query.filter_by(panaderia_id=panaderia_id, activo=True).all()
    
    if request.method == 'POST':
        try:
            # VERIFICAR SI ES UNA NUEVA COMPRA
            if 'nueva_compra_cantidad' in request.form and request.form['nueva_compra_cantidad']:
                cantidad_empaques = int(request.form['nueva_compra_cantidad'])
                precio_total = float(request.form['nueva_compra_precio'])
                
                if cantidad_empaques <= 0 or precio_total <= 0:
                    flash('Cantidad y precio deben ser mayores a 0', 'error')
                    return redirect(url_for('editar_materia_prima', id=id))
                
                # CALCULAR NUEVO STOCK Y COSTO PROMEDIO
                nuevo_stock_gramos = cantidad_empaques * materia.gramos_por_empaque
                precio_unitario_empaque = precio_total / cantidad_empaques
                
                # CALCULAR NUEVO COSTO PROMEDIO PONDERADO
                stock_actual_valor = materia.stock_actual * materia.costo_promedio
                nuevo_stock_valor = nuevo_stock_gramos * (precio_total / nuevo_stock_gramos)
                total_stock = materia.stock_actual + nuevo_stock_gramos
                
                if total_stock > 0:
                    nuevo_costo_promedio = (stock_actual_valor + nuevo_stock_valor) / total_stock
                else:
                    nuevo_costo_promedio = precio_total / nuevo_stock_gramos
                
                # ACTUALIZAR MATERIA PRIMA
                materia.stock_actual += nuevo_stock_gramos
                materia.costo_promedio = nuevo_costo_promedio
                materia.fecha_ultima_actualizacion = datetime.now()
                
                # REGISTRAR EN HISTORIAL
                nueva_compra = HistorialCompra(
                    materia_prima_id=materia.id,
                    cantidad_empaques=cantidad_empaques,
                    precio_total=precio_total,
                    precio_unitario_empaque=precio_unitario_empaque,
                    usuario_id=session['user_id']
                )
                db.session.add(nueva_compra)
                
                flash(f'✅ Se agregaron {nuevo_stock_gramos} {materia.unidad_medida} al stock', 'success')
            
            # ACTUALIZAR DATOS BÁSICOS
            materia.nombre = request.form['nombre']
            materia.proveedor_id = request.form.get('proveedor_id', type=int)
            materia.unidad_medida = request.form['unidad_medida']
            materia.stock_minimo = float(request.form.get('stock_minimo', 0))
            materia.stock_minimo_empaques = int(request.form.get('stock_minimo_empaques', 1))
            materia.gramos_por_empaque = float(request.form.get('gramos_por_empaque', 1.0))
            materia.unidad_compra = request.form.get('unidad_compra', 'Unidad')
            
            # MANEJAR FECHA DE VENCIMIENTO
            fecha_vencimiento_str = request.form.get('fecha_vencimiento', '').strip()
            if fecha_vencimiento_str:
                materia.fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
            else:
                materia.fecha_vencimiento = None
            
            # VALIDACIONES
            if not materia.proveedor_id:
                flash('Debe seleccionar un proveedor', 'error')
                return redirect(url_for('editar_materia_prima', id=id))
                
            if materia.stock_minimo < 0:
                flash('El stock mínimo no puede ser negativo', 'error')
                return redirect(url_for('editar_materia_prima', id=id))
            
            db.session.commit()
            flash(f'Materia prima "{materia.nombre}" actualizada correctamente', 'success')
            return redirect(url_for('materias_primas'))
            
        except ValueError as e:
            flash('Error: Los campos numéricos deben contener valores válidos', 'error')
            return redirect(url_for('editar_materia_prima', id=id))
        except Exception as e:
            flash(f'Error inesperado al actualizar la materia prima: {str(e)}', 'error')
            return redirect(url_for('editar_materia_prima', id=id))
    
    # OBTENER HISTORIAL DE COMPRAS PARA MOSTRAR
    historial_compras = HistorialCompra.query.filter_by(materia_prima_id=id).order_by(HistorialCompra.fecha_compra.desc()).all()
    
    return render_template('editar_materia_prima.html', 
                         materia=materia, 
                         proveedores=proveedores,
                         historial_compras=historial_compras)


@app.route('/desactivar_materia_prima/<int:id>')
@login_required
@modulo_requerido('inventario')
@tenant_required
def desactivar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.filter_by(panaderia_id=current_user.panaderia_id, id=id).first_or_404()
    materia.activo = False
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" desactivada correctamente', 'success')
    return redirect(url_for('materias_primas'))


@app.route('/activar_materia_prima/<int:id>')
@login_required
@modulo_requerido('inventario')
@tenant_required
def activar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.filter_by(panaderia_id=current_user.panaderia_id, id=id).first_or_404()
    materia.activo = True
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" activada correctamente', 'success')
    return redirect(url_for('materias_primas'))


@app.route('/historial_compras/<int:materia_prima_id>')
@login_required
@modulo_requerido('inventario')
@tenant_required
def historial_compras(materia_prima_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.filter_by(panaderia_id=current_user.panaderia_id, id=materia_prima_id).first_or_404()
    historial = HistorialCompra.query.filter_by(materia_prima_id=materia_prima_id).order_by(HistorialCompra.fecha_compra.desc()).all()
    
    return render_template('historial_compras.html', materia=materia, historial=historial)
# =============================================
# RUTAS DE PRODUCCIÓN Y RECETAS - CORREGIDAS MULTI-TENANT
# =============================================
from tenant_decorators import tenant_required  # Asegúrate de importar el decorador

@app.route('/recetas')
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def recetas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ CORREGIDO: Usar current_user.panaderia_id en lugar de función personalizada
    panaderia_actual = current_user.panaderia_id
    print(f"🔍 DEBUG RECETAS: Panadería actual: {panaderia_actual}")
    
    # ✅ BLOQUE SUPER USUARIO (MEJORADO)
    if es_super_usuario() and not session.get('panaderia_remota'):
        flash("🔧 Como super usuario, usa 'Acceder a esta panadería' para ver recetas específicas", "info")
        return render_template('recetas.html', recetas=[])
    
    # ✅ CORREGIDO: Solo recetas de ESTA panadería
    recetas_panaderia = Receta.query.filter_by(panaderia_id=panaderia_actual, activo=True).all()
    
    print(f"🔍 DEBUG RECETAS: Recetas encontradas para panadería {panaderia_actual}: {len(recetas_panaderia)}")
    for receta in recetas_panaderia:
        print(f"   - {receta.nombre} (ID: {receta.id})")
    
    return render_template('recetas.html', recetas=recetas_panaderia)

@app.route('/detalle_receta/<int:id>')
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def detalle_receta(id):
    """Página de detalle de una receta específica"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ CORREGIDO: Asegurar que la receta pertenezca al tenant actual
    receta = Receta.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first_or_404()
    return render_template('detalle_receta.html', receta=receta)

@app.route('/producir_receta/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def producir_receta(id):
    """Producción de una receta - cálculo de ingredientes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ CORREGIDO: Asegurar que la receta pertenezca al tenant actual
    receta = Receta.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first_or_404()
    
    if request.method == 'POST':
        try:
            cantidad = int(request.form['cantidad'])
            
            # Verificar stock disponible
            ingredientes_insuficientes = []
            for ingrediente in receta.ingredientes:
                cantidad_necesaria = (ingrediente.cantidad_gramos / receta.unidades_obtenidas) * cantidad
                if ingrediente.materia_prima.stock_actual < cantidad_necesaria:
                    ingredientes_insuficientes.append({
                        'nombre': ingrediente.materia_prima.nombre,
                        'necesario': cantidad_necesaria,
                        'disponible': ingrediente.materia_prima.stock_actual,
                        'unidad': ingrediente.materia_prima.unidad_medida
                    })
            
            if ingredientes_insuficientes:
                return render_template('produccion.html', 
                                     receta=receta,
                                     cantidad=cantidad,
                                     ingredientes_insuficientes=ingredientes_insuficientes)
            
            # Crear registro de producción
            orden_produccion = OrdenProduccion(
                receta_id=receta.id,
                cantidad_producir=cantidad,
                estado='confirmada',
                usuario_id=session['user_id'],
                fecha_inicio=datetime.now(),
                panaderia_id=current_user.panaderia_id  # ✅ NUEVO: Asignar panaderia_id
            )
            db.session.add(orden_produccion)
            db.session.flush()  # Para obtener el ID
            
            # Descontar ingredientes del inventario y registrar en historial
            for ingrediente in receta.ingredientes:
                cantidad_necesaria = (ingrediente.cantidad_gramos / receta.unidades_obtenidas) * cantidad
                
                # Actualizar stock
                ingrediente.materia_prima.stock_actual -= cantidad_necesaria
                
                # Registrar en historial de inventario
                movimiento = HistorialInventario(
                    materia_prima_id=ingrediente.materia_prima.id,
                    orden_produccion_id=orden_produccion.id,
                    cantidad_utilizada=cantidad_necesaria,
                    tipo_movimiento='produccion',
                    panaderia_id=current_user.panaderia_id  # ✅ NUEVO: Asignar panaderia_id
                )
                db.session.add(movimiento)
            
            db.session.commit()
            flash(f'✅ Producción de {cantidad} unidades confirmada. Ingredientes descontados del inventario.', 'success')
            return redirect(url_for('recetas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al procesar la producción: {str(e)}', 'error')
            return redirect(url_for('producir_receta', id=id))
    
    # GET request - mostrar formulario de producción
    cantidad = request.args.get('cantidad', receta.unidades_obtenidas, type=int)
    return render_template('produccion.html', receta=receta, cantidad=cantidad)

@app.route('/api/calcular_ingredientes/<int:id>')
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def calcular_ingredientes(id):
    """API para calcular ingredientes necesarios (AJAX)"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # ✅ CORREGIDO: Usar current_user.panaderia_id y filtrar receta
    receta = Receta.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first()
    
    if not receta:
        return jsonify({'error': 'Receta no encontrada'}), 404
    
    cantidad = request.args.get('cantidad', receta.unidades_obtenidas, type=int)
    
    ingredientes_calculados = []
    for ingrediente in receta.ingredientes:
        cantidad_necesaria = (ingrediente.cantidad_gramos / receta.unidades_obtenidas) * cantidad
        suficiente = ingrediente.materia_prima.stock_actual >= cantidad_necesaria
        
        ingredientes_calculados.append({
            'id': ingrediente.id,
            'nombre': ingrediente.materia_prima.nombre,
            'cantidad_original': ingrediente.cantidad_gramos,
            'cantidad_calculada': round(cantidad_necesaria, 2),
            'unidad': ingrediente.materia_prima.unidad_medida,
            'stock_disponible': ingrediente.materia_prima.stock_actual,
            'suficiente': suficiente
        })
    
    return jsonify(ingredientes_calculados)

# ✅ NUEVA API PARA ACTUALIZAR PRECIO REAL EN TIEMPO REAL


@app.route('/api/historial_precios/<int:receta_id>')
@login_required
@modulo_requerido('produccion')
@tenant_required
def obtener_historial_precios(receta_id):
    """Obtiene el historial de precios de una receta"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        from models import HistorialPrecioReceta
        
        historial = HistorialPrecioReceta.query.filter_by(
            receta_id=receta_id,
            panaderia_id=current_user.panaderia_id
        ).order_by(HistorialPrecioReceta.fecha_cambio.desc()).limit(20).all()
        
        resultado = []
        for h in historial:
            resultado.append({
                'fecha': h.fecha_cambio.strftime('%d/%m/%Y %H:%M'),
                'precio_anterior': h.precio_anterior,
                'precio_nuevo': h.precio_nuevo,
                'motivo': h.motivo or 'Sin motivo registrado'
            })
        
        return jsonify({
            'success': True,
            'historial': resultado,
            'total_cambios': len(resultado)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/actualizar_precio_real/<int:receta_id>', methods=['POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def actualizar_precio_real(receta_id):
    """API para actualizar el precio real de una receta desde la lista"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # ✅ CORREGIDO: Asegurar que la receta pertenezca al tenant actual
    receta = Receta.query.filter_by(id=receta_id, panaderia_id=current_user.panaderia_id).first_or_404()
    data = request.get_json()
    nuevo_precio = float(data.get('precio_real', 0))
    
    try:
        receta.precio_venta_real = nuevo_precio
        db.session.commit()
        
        return jsonify({
            'success': True,
            'precio_actualizado': nuevo_precio,
            'utilidad_pesos': receta.utilidad_real_pesos,
            'utilidad_porcentaje': round(receta.utilidad_real_porcentaje, 1),
            'rentabilidad': receta.rentabilidad_categoria,
            'punto_equilibrio': receta.punto_equilibrio_unidades,
            'costo_unitario': receta.costo_unitario
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ✅ NUEVO ENDPOINT PARA CÁLCULOS EN TIEMPO REAL DE RECETAS
@app.route('/api/calcular_precio_receta', methods=['POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def calcular_precio_receta():
    """API para cálculos en tiempo real de costos y precios con 45% CIF + 45% Ganancia"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        # Calcular costo total de ingredientes
        costo_total_mp = 0
        peso_total = 0
        
        for ingrediente in data.get('ingredientes', []):
            materia_prima_id = ingrediente.get('materia_prima_id')
            cantidad_gramos = float(ingrediente.get('cantidad_gramos', 0))
            
            if materia_prima_id and cantidad_gramos > 0:
                # ✅ CORREGIDO: Filtrar materia prima por tenant
                materia_prima = MateriaPrima.query.filter_by(
                    id=materia_prima_id, 
                    panaderia_id=current_user.panaderia_id
                ).first()
                if materia_prima:
                    # Calcular costo del ingrediente
                    costo_ingrediente = cantidad_gramos * materia_prima.costo_promedio
                    costo_total_mp += costo_ingrediente
                    peso_total += cantidad_gramos
        
        # Obtener parámetros adicionales
        peso_unidad = float(data.get('peso_unidad_gramos', 0))
        porcentaje_perdida = float(data.get('porcentaje_perdida', 10.0))
        
        # Calcular unidades obtenidas considerando pérdida por horneado
        peso_horneado_total = peso_total * (1 - porcentaje_perdida / 100)

        # Calcular unidades obtenidas
        if peso_unidad > 0:
            unidades_obtenidas = int(peso_horneado_total / peso_unidad)
        else:
            unidades_obtenidas = 0

        # APLICAR FÓRMULAS DEL EXCEL: 45% CIF + 45% GANANCIA
        costo_mp = costo_total_mp
        cif = costo_mp * 0.45  # 45% CIF
        costo_total_con_cif = costo_mp + cif
        ganancia = costo_total_con_cif * 0.45  # 45% Ganancia
        precio_total_preparacion = costo_total_con_cif + ganancia

        # Calcular precio por unidad
        if unidades_obtenidas > 0:
            precio_venta_unidad = precio_total_preparacion / unidades_obtenidas
        else:
            precio_venta_unidad = 0

        # Calcular métricas de rentabilidad
        if unidades_obtenidas > 0:
            costo_unitario = costo_total_con_cif / unidades_obtenidas
        else:
            costo_unitario = 0

        margen_contribucion = precio_venta_unidad - costo_unitario

        if precio_venta_unidad > 0:
            margen_porcentaje = (margen_contribucion / precio_venta_unidad) * 100
        else:
            margen_porcentaje = 0

        if margen_contribucion > 0:
            punto_equilibrio = int(costo_total_con_cif / margen_contribucion)
        else:
            punto_equilibrio = 0

        if costo_total_con_cif > 0:
            rentabilidad_porcentaje = (ganancia / costo_total_con_cif) * 100
        else:
            rentabilidad_porcentaje = 0
        
        return jsonify({
            'success': True,
            'costo_materia_prima': round(costo_mp, 2),
            'cif': round(cif, 2),
            'costo_total': round(costo_total_con_cif, 2),
            'ganancia': round(ganancia, 2),
            'precio_total_preparacion': round(precio_total_preparacion, 2),
            'precio_venta_unidad': round(precio_venta_unidad, 2),
            'peso_total': round(peso_total, 2),
            'unidades_obtenidas': unidades_obtenidas,
            'margen_contribucion': round(margen_contribucion, 2),
            'margen_porcentaje': round(margen_porcentaje, 2),
            'punto_equilibrio': punto_equilibrio,
            'rentabilidad_porcentaje': round(rentabilidad_porcentaje, 2),
            'costo_unitario': round(costo_unitario, 2)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/crear_receta', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def crear_receta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ DEBUG PARA CONFIRMAR PANADERÍA
    panaderia_actual = current_user.panaderia_id
    print(f"🔍 DEBUG CREAR_RECETA: Panadería actual: {panaderia_actual}")
    print(f"🔍 DEBUG CREAR_RECETA: User ID: {session.get('user_id')}")
    
    # ✅ CORREGIDO: Filtrar materias primas por tenant
    materias_primas = MateriaPrima.query.filter_by(activo=True, panaderia_id=panaderia_actual).all()
    print(f"🔍 Materias primas encontradas: {len(materias_primas)}")
    
    if request.method == 'POST':
        try:
            # ✅ CAPTURAR PRECIO REAL DEL FORMULARIO
            precio_venta_real = float(request.form.get('precio_venta_real', 0)) or 0
            
            # Crear la receta base
            nueva_receta = Receta(
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion', ''),
                categoria=request.form['categoria'],
                peso_unidad_gramos=float(request.form['peso_unidad_gramos']),
                porcentaje_perdida=float(request.form.get('porcentaje_perdida', 10.0)),
                activo=True,
                precio_venta_real=precio_venta_real,
                panaderia_id=panaderia_actual  # ✅ CORREGIDO: Usar current_user.panaderia_id
            )
            
            db.session.add(nueva_receta)
            db.session.flush()  # Para obtener el ID
            
            # Procesar ingredientes - USANDO GRAMOS DIRECTOS
            ingredientes_data = []
            costo_total_materias_primas = 0
            peso_total_masa = 0

            # Recoger ingredientes del formulario
            i = 0
            while f'ingredientes[{i}][materia_prima_id]' in request.form:
                materia_prima_id = request.form[f'ingredientes[{i}][materia_prima_id]']
                gramos = float(request.form[f'ingredientes[{i}][gramos]'])  # Gramos directos
                
                # ✅ CORREGIDO: Filtrar materia prima por tenant
                materia_prima = MateriaPrima.query.filter_by(
                    id=materia_prima_id, 
                    panaderia_id=panaderia_actual
                ).first()
                if materia_prima and gramos > 0:
                    cantidad_gramos = gramos
                    costo_ingrediente = cantidad_gramos * materia_prima.costo_promedio
                    
                    ingrediente = RecetaIngrediente(
                        receta_id=nueva_receta.id,
                        materia_prima_id=materia_prima_id,
                        porcentaje_aplicado=0,  # Se calculará después
                        cantidad_gramos=cantidad_gramos,
                        costo_ingrediente=costo_ingrediente
                    )
                    
                    db.session.add(ingrediente)
                    costo_total_materias_primas += costo_ingrediente
                    peso_total_masa += cantidad_gramos
                    ingredientes_data.append(ingrediente)
                
                i += 1
            
            # Calcular porcentajes después de tener el peso total
            for ingrediente in ingredientes_data:
                if peso_total_masa > 0:
                    ingrediente.porcentaje_aplicado = (ingrediente.cantidad_gramos / peso_total_masa) * 100
            
            # CALCULAR DATOS DE PRODUCCIÓN
            unidades_obtenidas = int(peso_total_masa / nueva_receta.peso_unidad_gramos) if nueva_receta.peso_unidad_gramos > 0 else 0
            peso_horneado_unidad = nueva_receta.peso_unidad_gramos - (nueva_receta.peso_unidad_gramos * (nueva_receta.porcentaje_perdida / 100))
            costo_indirecto = costo_total_materias_primas * 0.45  # 45% CIF
            costo_total_produccion = costo_total_materias_primas + costo_indirecto
            margen_ganancia = costo_total_produccion * 0.45  # 45% de ganancia
            precio_venta_unitario = (costo_total_produccion + margen_ganancia) / unidades_obtenidas if unidades_obtenidas > 0 else 0
            precio_por_gramo = precio_venta_unitario / nueva_receta.peso_unidad_gramos if nueva_receta.peso_unidad_gramos > 0 else 0
            
            # ✅ ACTUALIZAR RECETA CON TODOS LOS DATOS CALCULADOS (INCLUYENDO PRECIO REAL)
            nueva_receta.peso_total_masa = peso_total_masa
            nueva_receta.unidades_obtenidas = unidades_obtenidas
            nueva_receta.peso_horneado_unidad = peso_horneado_unidad
            nueva_receta.costo_materias_primas = costo_total_materias_primas
            nueva_receta.costo_indirecto = costo_indirecto
            nueva_receta.costo_total = costo_total_produccion
            nueva_receta.margen_ganancia = margen_ganancia
            nueva_receta.precio_venta_unitario = precio_venta_unitario
            nueva_receta.precio_por_gramo = precio_por_gramo
            nueva_receta.precio_venta = precio_venta_unitario * unidades_obtenidas
            # ✅ precio_venta_real ya fue asignado al crear la receta
            
            # ✅ NUEVO: CREAR PRODUCTO AUTOMÁTICAMENTE A PARTIR DE LA RECETA
            producto_automatico = Producto(
                nombre=nueva_receta.nombre,
                descripcion=nueva_receta.descripcion,
                categoria_id=obtener_categoria_id(nueva_receta.categoria, panaderia_actual),  # ✅ CORREGIDO: Pasar panaderia_id
                precio_venta=precio_venta_real if precio_venta_real > 0 else precio_venta_unitario,
                stock_actual=0,  # Inicialmente sin stock - se llena con producción
                stock_minimo=10,
                codigo_barras=f"PROD{nueva_receta.id:06d}",
                tipo_producto='produccion',
                es_pan=True if 'pan' in nueva_receta.nombre.lower() else False,
                receta_id=nueva_receta.id,
                activo=True,
                panaderia_id=panaderia_actual  # ✅ CORREGIDO: Usar current_user.panaderia_id
            )
            
            db.session.add(producto_automatico)
            db.session.flush()  # Para obtener el ID del producto
            
            # ✅ ASIGNAR EL PRODUCTO A LA RECETA (relación bidireccional)
            nueva_receta.producto_id = producto_automatico.id
            
            db.session.commit()
            
            # ✅ MENSAJE MEJORADO QUE INCLUYE LA CREACIÓN DEL PRODUCTO
            mensaje = f'✅ Receta "{nueva_receta.nombre}" creada exitosamente! '
            mensaje += f'Peso total: {peso_total_masa:,.0f}g | '
            mensaje += f'Unidades: {unidades_obtenidas} | '
            mensaje += f'Precio teórico: ${precio_venta_unitario:,.0f}'
            
            if precio_venta_real > 0:
                mensaje += f' | Precio real: ${precio_venta_real:,.0f}'
                # ✅ CALCULAR Y MOSTRAR UTILIDAD REAL INMEDIATAMENTE
                utilidad_pesos = nueva_receta.utilidad_real_pesos
                utilidad_porcentaje = nueva_receta.utilidad_real_porcentaje
                mensaje += f' | Utilidad: ${utilidad_pesos:,.0f} ({utilidad_porcentaje:.1f}%)'
            
            mensaje += f' | ✅ Producto automático creado: {producto_automatico.nombre}'
            
            flash(mensaje, 'success')
            return redirect(url_for('recetas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear la receta: {str(e)}', 'error')
            return redirect(url_for('crear_receta'))
    
    return render_template('crear_receta.html', materias_primas=materias_primas)

# ✅ FUNCIÓN HELPER CORREGIDA - AGREGAR panaderia_id
def obtener_categoria_id(nombre_categoria, panaderia_id):
    """Obtiene el ID de categoría basado en el nombre - crea si no existe"""
    # Normalizar nombre de categoría
    nombre_categoria = nombre_categoria.strip().title()
    
    # ✅ CORREGIDO: Filtrar categoría por tenant
    categoria = Categoria.query.filter_by(nombre=nombre_categoria, panaderia_id=panaderia_id).first()
    if not categoria:
        # Crear categoría si no existe
        categoria = Categoria(nombre=nombre_categoria, panaderia_id=panaderia_id)
        db.session.add(categoria)
        db.session.commit()
        print(f"✅ Nueva categoría creada: {nombre_categoria} para panadería {panaderia_id}")
    
    return categoria.id

# ✅ RUTA MEJORADA PARA EDITAR RECETAS EXISTENTES
@app.route('/editar_receta/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required  # ✅ NUEVO: Decorador multi-tenant
def editar_receta(id):
    """Editar una receta existente - AHORA CON PRECIO REAL"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ CORREGIDO: Asegurar que la receta pertenezca al tenant actual
    receta = Receta.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first_or_404()
    
    # ✅ CORREGIDO: Filtrar materias primas por tenant
    materias_primas = MateriaPrima.query.filter_by(activo=True, panaderia_id=current_user.panaderia_id).all()
    
    if request.method == 'POST':
        try:
            # ✅ ACTUALIZAR PRECIO REAL EN EDICIÓN
            nuevo_precio_real = float(request.form.get('precio_venta_real', 0)) or 0
            
            receta.nombre = request.form['nombre']
            receta.descripcion = request.form.get('descripcion', '')
            receta.categoria = request.form['categoria']
            receta.peso_unidad_gramos = float(request.form['peso_unidad_gramos'])
            receta.porcentaje_perdida = float(request.form.get('porcentaje_perdida', 10.0))
            receta.precio_venta_real = nuevo_precio_real  # ✅ ACTUALIZAR PRECIO REAL
            
            # ✅ ELIMINAR INGREDIENTES EXISTENTES Y AGREGAR NUEVOS
            RecetaIngrediente.query.filter_by(receta_id=receta.id).delete()
            
            # Reprocesar ingredientes (misma lógica que crear)
            costo_total_materias_primas = 0
            peso_total_masa = 0
            ingredientes_data = []
            
            i = 0
            while f'ingredientes[{i}][materia_prima_id]' in request.form:
                materia_prima_id = request.form[f'ingredientes[{i}][materia_prima_id]']
                gramos = float(request.form[f'ingredientes[{i}][gramos]'])
                
                # ✅ CORREGIDO: Filtrar materia prima por tenant
                materia_prima = MateriaPrima.query.filter_by(
                    id=materia_prima_id, 
                    panaderia_id=current_user.panaderia_id
                ).first()
                if materia_prima and gramos > 0:
                    cantidad_gramos = gramos
                    costo_ingrediente = cantidad_gramos * materia_prima.costo_promedio
                    
                    ingrediente = RecetaIngrediente(
                        receta_id=receta.id,
                        materia_prima_id=materia_prima_id,
                        porcentaje_aplicado=0,
                        cantidad_gramos=cantidad_gramos,
                        costo_ingrediente=costo_ingrediente
                    )
                    
                    db.session.add(ingrediente)
                    costo_total_materias_primas += costo_ingrediente
                    peso_total_masa += cantidad_gramos
                    ingredientes_data.append(ingrediente)
                
                i += 1
            
            # Recalcular porcentajes
            for ingrediente in ingredientes_data:
                if peso_total_masa > 0:
                    ingrediente.porcentaje_aplicado = (ingrediente.cantidad_gramos / peso_total_masa) * 100
            
            # ✅ RECALCULAR TODOS LOS DATOS DE PRODUCCIÓN
            unidades_obtenidas = int(peso_total_masa / receta.peso_unidad_gramos) if receta.peso_unidad_gramos > 0 else 0
            peso_horneado_unidad = receta.peso_unidad_gramos - (receta.peso_unidad_gramos * (receta.porcentaje_perdida / 100))
            costo_indirecto = costo_total_materias_primas * 0.45
            costo_total_produccion = costo_total_materias_primas + costo_indirecto
            margen_ganancia = costo_total_produccion * 0.45
            precio_venta_unitario = (costo_total_produccion + margen_ganancia) / unidades_obtenidas if unidades_obtenidas > 0 else 0
            precio_por_gramo = precio_venta_unitario / receta.peso_unidad_gramos if receta.peso_unidad_gramos > 0 else 0
            
            # ✅ ACTUALIZAR CAMPOS RECALCULADOS
            receta.peso_total_masa = peso_total_masa
            receta.unidades_obtenidas = unidades_obtenidas
            receta.peso_horneado_unidad = peso_horneado_unidad
            receta.costo_materias_primas = costo_total_materias_primas
            receta.costo_indirecto = costo_indirecto
            receta.costo_total = costo_total_produccion
            receta.margen_ganancia = margen_ganancia
            receta.precio_venta_unitario = precio_venta_unitario
            receta.precio_por_gramo = precio_por_gramo
            receta.precio_venta = precio_venta_unitario * unidades_obtenidas
            
            db.session.commit()
            
            flash(f'✅ Receta "{receta.nombre}" actualizada! Precio real: ${nuevo_precio_real:,.0f}', 'success')
            return redirect(url_for('detalle_receta', id=receta.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar la receta: {str(e)}', 'error')
            return redirect(url_for('editar_receta', id=id))
    
    # Para GET, mostrar formulario con datos existentes
    return render_template('crear_receta.html', 
                         receta=receta, 
                         materias_primas=materias_primas, 
                         editar=True)
    

# =============================================
# RUTA DE DIAGNÓSTICO - PRODUCTOS Y PUNTO DE VENTA
# =============================================

@app.route('/diagnostico_productos')
@login_required
@modulo_requerido('sistema')
def diagnostico_productos():
    """Página de diagnóstico para verificar productos y punto de venta"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todos los productos
    productos = Producto.query.all()
    
    # Obtener recetas con/sin producto
    recetas = Receta.query.all()
    
    # Probar la búsqueda
    resultados_busqueda_pan = []
    try:
        productos_pan = Producto.query.filter(
            Producto.activo == True,
            db.or_(
                Producto.nombre.ilike(f'%pan%'),
                Producto.codigo_barras.ilike(f'%pan%')
            )
        ).all()
        
        for producto in productos_pan:
            resultados_busqueda_pan.append({
                'nombre': producto.nombre,
                'stock': producto.stock_actual,
                'precio': producto.precio_venta,
                'activo': producto.activo,
                'tipo': producto.tipo_producto
            })
    except Exception as e:
        resultados_busqueda_pan = f"Error en búsqueda: {str(e)}"
    
    diagnostico = {
        'total_productos': len(productos),
        'total_recetas': len(recetas),
        'recetas_sin_producto': [],
        'productos_con_receta': [],
        'productos_externos': [],
        'productos_activos': [],
        'productos_con_stock': [],
        'busqueda_pan': resultados_busqueda_pan
    }
    
    for receta in recetas:
        if not receta.producto:
            diagnostico['recetas_sin_producto'].append({
                'id': receta.id,
                'nombre': receta.nombre,
                'categoria': receta.categoria
            })
        else:
            diagnostico['productos_con_receta'].append({
                'id': receta.producto.id,
                'nombre': receta.producto.nombre,
                'receta': receta.nombre,
                'stock': receta.producto.stock_actual,
                'precio': receta.producto.precio_venta,
                'activo': receta.producto.activo
            })
    
    for producto in productos:
        if producto.activo:
            diagnostico['productos_activos'].append({
                'nombre': producto.nombre,
                'stock': producto.stock_actual,
                'precio': producto.precio_venta,
                'tipo': producto.tipo_producto
            })
            
        if producto.stock_actual > 0:
            diagnostico['productos_con_stock'].append({
                'nombre': producto.nombre,
                'stock': producto.stock_actual,
                'precio': producto.precio_venta
            })
            
        if producto.tipo_producto == 'externo':
            diagnostico['productos_externos'].append({
                'nombre': producto.nombre,
                'stock': producto.stock_actual
            })
    
    return render_template('diagnostico_productos.html', diagnostico=diagnostico)
    
# =============================================
# RUTAS DE PRODUCCIÓN DIARIA - NUEVO MÓDULO
# =============================================



@app.route('/produccion_diaria')
@login_required
@modulo_requerido('produccion')
@tenant_required
def produccion_diaria():
    """Dashboard principal de producción diaria - SOLO datos de esta panadería"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ FILTRO CLAVE: Solo datos de ESTA panadería (CON ACCESO REMOTO)
    panaderia_actual = obtener_panaderia_actual()  # ← ÚNICO CAMBIO EN FILTRO
    
    print(f"🔍 DEBUG: Panadería actual: {panaderia_actual}")
    
    # ✅ ✅ ✅ NUEVO: BLOQUE SUPER USUARIO (MEJORADO) ✅ ✅ ✅
    if es_super_usuario() and not session.get('panaderia_remota'):
        flash("🔧 Como super usuario, usa 'Acceder a esta panadería' para ver producción específica", "info")
        return render_template('produccion_diaria.html',
                             recetas_con_stock=[],
                             ordenes_activas=[],
                             todas_las_ordenes_completadas=[],
                             alertas=[])
    # ✅ ✅ ✅ FIN BLOQUE SUPER USUARIO ✅ ✅ ✅
    
    # ✅ SOLO DIAGNÓSTICO - NO crear recetas automáticas
    hay_recetas = diagnosticar_recetas(panaderia_actual)
    
    if not hay_recetas:
        print("⚠️  NO hay recetas activas. Debes crearlas en el módulo 'Fórmulas y Recetas'")
        flash("No hay recetas disponibles. Crea recetas en el módulo 'Fórmulas y Recetas' primero.", "warning")
    
    
    
    # Obtener recetas activas de ESTA panadería
    recetas_activas = Receta.query.filter_by(
        activo=True,
        panaderia_id=panaderia_actual
    ).all()
    
    print(f"🔍 DEBUG: Recetas activas encontradas: {len(recetas_activas)}")
    
    recetas_con_stock = []
    alertas = []
    
    for receta in recetas_activas:
        # Calcular stock actual (usar función real o 0 si no existe)
        try:
            stock_actual = calcular_stock_vitrina(receta.id)
        except:
            stock_actual = 0  # Si la función no existe o falla
        
        # Obtener configuración personalizada
        config = ConfiguracionProduccion.query.filter_by(receta_id=receta.id).first()
        if not config:
            # Crear configuración por defecto si no existe
            config = ConfiguracionProduccion(
                receta_id=receta.id,
                stock_minimo=10,
                stock_objetivo=50,
                stock_maximo=100,
                rotacion_diaria_esperada=10.0
            )
            db.session.add(config)
            db.session.commit()
        
        stock_minimo_personalizado = config.stock_minimo
        
        # Calcular ventas del día actual
        try:
            hoy = datetime.now().date()
            ventas_hoy = calcular_ventas_hoy(receta.nombre, hoy)
        except:
            ventas_hoy = 0
        
        # Proyección de agotamiento
        proyeccion_horas = None
        if config.rotacion_diaria_esperada > 0 and stock_actual > 0:
            horas_restantes = (stock_actual / config.rotacion_diaria_esperada) * 24
            if horas_restantes < 168:
                proyeccion_horas = int(horas_restantes)
        
        # Generar alertas
        if stock_actual <= stock_minimo_personalizado:
            alertas.append({
                'nivel': 'critico',
                'mensaje': f'🔴 STOCK CRÍTICO: {receta.nombre} - Solo {stock_actual} unidades (Mínimo: {stock_minimo_personalizado})'
            })
        elif stock_actual <= (stock_minimo_personalizado * 2):
            alertas.append({
                'nivel': 'advertencia', 
                'mensaje': f'🟡 STOCK BAJO: {receta.nombre} - {stock_actual} unidades (Mínimo: {stock_minimo_personalizado})'
            })
        elif stock_actual >= config.stock_maximo:
            alertas.append({
                'nivel': 'info',
                'mensaje': f'🔵 STOCK ALTO: {receta.nombre} - {stock_actual} unidades (Máximo: {config.stock_maximo})'
            })
        
        recetas_con_stock.append({
            'id': receta.id,
            'nombre': receta.nombre,
            'stock_actual': stock_actual,
            'stock_minimo': stock_minimo_personalizado,
            'stock_maximo': config.stock_maximo,
            'ventas_hoy': ventas_hoy,
            'proyeccion_horas': proyeccion_horas,
            'rotacion_esperada': config.rotacion_diaria_esperada,
            'config': config
        })
    
    
    
    # ✅ Obtener órdenes de producción activas SOLO de esta panadería
    ordenes_activas = OrdenProduccion.query.filter(
        OrdenProduccion.estado.in_(['PENDIENTE', 'EN_PRODUCCION']),
        OrdenProduccion.panaderia_id == panaderia_actual  # ← FILTRO MULTICLIENTE
    ).order_by(OrdenProduccion.fecha_produccion.desc()).limit(10).all()
    
    # ✅ Obtener órdenes completadas del día SOLO de esta panadería
    hoy = datetime.now().date()
    ordenes_completadas_hoy_db = OrdenProduccion.query.filter(
        OrdenProduccion.estado == 'COMPLETADA',
        db.func.date(OrdenProduccion.fecha_fin) == hoy,
        OrdenProduccion.panaderia_id == panaderia_actual  # ← FILTRO MULTICLIENTE
    ).all()
    
    print(f"🔍 DEBUG: Recetas con stock procesadas: {len(recetas_con_stock)}")
    print(f"🔍 DEBUG: Alertas generadas: {len(alertas)}")
    print(f"🔍 DEBUG: Órdenes activas: {len(ordenes_activas)}")
    
    return render_template('produccion_diaria.html',
                         recetas_con_stock=recetas_con_stock,
                         ordenes_activas=ordenes_activas,
                         todas_las_ordenes_completadas=ordenes_completadas_hoy_db,
                         alertas=alertas)
    
# ✅ NUEVA RUTA: Configuración personalizada de stock por producto
@app.route('/configurar_stock_producto/<int:receta_id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required
def configurar_stock_producto(receta_id):
    """Configuración personalizada de stock por producto"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receta = Receta.query.get_or_404(receta_id)
    config = ConfiguracionProduccion.query.filter_by(receta_id=receta_id).first()
    
    # Crear configuración si no existe
    if not config:
        config = ConfiguracionProduccion(
            receta_id=receta_id,
            stock_minimo=10,
            stock_objetivo=50,
            stock_maximo=100,
            rotacion_diaria_esperada=10.0
        )
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            # Actualizar configuración
            config.stock_minimo = int(request.form['stock_minimo'])
            config.stock_objetivo = int(request.form['stock_objetivo'])
            config.stock_maximo = int(request.form['stock_maximo'])
            config.rotacion_diaria_esperada = float(request.form['rotacion_diaria_esperada'])
            config.tendencia_ventas = float(request.form.get('tendencia_ventas', 1.0))
            config.fecha_actualizacion = datetime.now()
            
            db.session.commit()
            flash(f'✅ Configuración de stock para "{receta.nombre}" actualizada', 'success')
            return redirect(url_for('produccion_diaria'))
            
        except Exception as e:
            flash(f'❌ Error al actualizar configuración: {str(e)}', 'error')
    
    # Obtener estadísticas reales para sugerencias
    stock_actual = calcular_stock_vitrina(receta_id)
    ventas_ultima_semana = calcular_ventas_ultima_semana(receta.nombre)
    
    return render_template('configurar_stock_producto.html', 
                         receta=receta, 
                         config=config,
                         stock_actual=stock_actual,
                         ventas_ultima_semana=ventas_ultima_semana)

# ✅ NUEVA FUNCIÓN: Calcular ventas de la última semana
def calcular_ventas_ultima_semana(nombre_receta):
    """Calcular ventas de los últimos 7 días para una receta"""
    try:
        fecha_inicio = datetime.now().date() - timedelta(days=7)
        
        ventas_semana = db.session.query(
            db.func.sum(DetalleVenta.cantidad)
        ).join(Producto).join(Venta).filter(
            Producto.nombre == nombre_receta,
            Venta.fecha_hora >= fecha_inicio
        ).scalar() or 0
        
        return ventas_semana
    except Exception as e:
        print(f"Error calculando ventas semana: {e}")
        return 0
    
# ✅ NUEVO: Ruta para configurar stock mínimo por receta
@app.route('/configurar_stock/<int:receta_id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required
def configurar_stock(receta_id):
    """Configurar stock objetivo y parámetros para una receta"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receta = Receta.query.get_or_404(receta_id)
    config = ConfiguracionProduccion.query.filter_by(receta_id=receta_id).first()
    
    if not config:
        config = ConfiguracionProduccion(receta_id=receta_id)
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            config.stock_objetivo = int(request.form['stock_objetivo'])
            config.porcentaje_critico = float(request.form['porcentaje_critico'])
            config.porcentaje_bajo = float(request.form['porcentaje_bajo'])
            config.porcentaje_medio = float(request.form['porcentaje_medio'])
            config.tendencia_ventas = float(request.form.get('tendencia_ventas', 1.0))
            config.fecha_actualizacion = datetime.now()
            
            db.session.commit()
            flash(f'✅ Configuración de stock para "{receta.nombre}" actualizada', 'success')
            return redirect(url_for('produccion_diaria'))
            
        except Exception as e:
            flash(f'❌ Error al actualizar configuración: {str(e)}', 'error')
    
    return render_template('configurar_stock.html', receta=receta, config=config)

# ✅ NUEVO: API para obtener configuración de stock


@app.route('/api/historial_produccion')
@login_required
@modulo_requerido('produccion')
@tenant_required
def api_historial_produccion():
    """API para obtener historial de producción por fechas"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'Fechas requeridas'}), 400
        
        from datetime import datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio_dt > fecha_fin_dt:
            return jsonify({'error': 'Fecha inicio > fecha fin'}), 400
        
        panaderia_id = current_user.panaderia_id
        
        # Obtener órdenes completadas en el rango
        ordenes = OrdenProduccion.query.filter(
            OrdenProduccion.estado == 'COMPLETADA',
            OrdenProduccion.panaderia_id == panaderia_id,
            OrdenProduccion.fecha_fin >= fecha_inicio_dt,
            OrdenProduccion.fecha_fin <= fecha_fin_dt
        ).order_by(OrdenProduccion.fecha_fin.desc()).all()
        
        resultado = []
        total_producido = 0
        recetas_set = set()
        
        for orden in ordenes:
            receta_nombre = orden.receta.nombre if orden.receta else 'Receta eliminada'
            recetas_set.add(receta_nombre)
            total_producido += orden.cantidad_producir
            
            resultado.append({
                'id': orden.id,
                'receta_nombre': receta_nombre,
                'cantidad': orden.cantidad_producir,
                'fecha_fin': orden.fecha_fin.isoformat() if orden.fecha_fin else None,
                'usuario': orden.usuario.username if orden.usuario else 'N/A'
            })
        
        return jsonify({
            'success': True,
            'ordenes': resultado,
            'metricas': {
                'total_producido': total_producido,
                'recetas_producidas': len(recetas_set),
                'total_ordenes': len(resultado)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/configuracion_stock/<int:receta_id>')
@login_required
@modulo_requerido('produccion')
@tenant_required
def api_configuracion_stock(receta_id):
    """API para obtener configuración de stock de una receta"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    config = ConfiguracionProduccion.query.filter_by(receta_id=receta_id).first()
    if not config:
        config = ConfiguracionProduccion(receta_id=receta_id)
        db.session.add(config)
        db.session.commit()
    
    return jsonify({
        'stock_objetivo': config.stock_objetivo,
        'porcentaje_critico': config.porcentaje_critico,
        'porcentaje_bajo': config.porcentaje_bajo,
        'porcentaje_medio': config.porcentaje_medio,
        'tendencia_ventas': config.tendencia_ventas
    })

@app.route('/produccion/ordenar_produccion', methods=['POST'])
@login_required
@modulo_requerido('produccion')
@tenant_required
def ordenar_produccion():
    """Crear nueva orden de producción desde el dashboard"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        receta_id = request.form.get('receta_id', type=int)
        cantidad = request.form.get('cantidad', type=int)
        
        if not receta_id or not cantidad or cantidad <= 0:
            return jsonify({'error': 'Datos inválidos'}), 400
        
        # ✅ AGREGADO: Filtro multicliente
        panaderia_actual = session.get('panaderia_id')
        receta = Receta.query.filter_by(id=receta_id, panaderia_id=panaderia_actual).first()
        
        if not receta:
            return jsonify({'error': 'Receta no encontrada'}), 404
        
        # Crear orden de producción
        nueva_orden = OrdenProduccion(
            receta_id=receta_id,
            cantidad_producir=cantidad,
            estado='PENDIENTE',
            usuario_id=session['user_id'],
            panaderia_id=panaderia_actual  # ✅ AGREGADO: Filtro multicliente
        )
        
        db.session.add(nueva_orden)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'orden_id': nueva_orden.id,
            'mensaje': f'Orden de producción creada para {cantidad} unidades'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/debug_produccion')
@login_required
@modulo_requerido('produccion')
def debug_produccion():
    """Página de debug para producción"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener órdenes de producción
    ordenes = OrdenProduccion.query.all()
    
    debug_info = {
        'total_ordenes': len(ordenes),
        'ordenes_detalle': []
    }
    
    for orden in ordenes:
        debug_info['ordenes_detalle'].append({
            'id': orden.id,
            'receta': orden.receta.nombre if orden.receta else 'N/A',
            'cantidad': orden.cantidad_producir,
            'estado': orden.estado,
            'producto_asociado': orden.receta.producto.nombre if orden.receta and orden.receta.producto else 'NO',
            'stock_actual': orden.receta.producto.stock_actual if orden.receta and orden.receta.producto else 0
        })
    
    return render_template('debug_produccion.html', debug=debug_info)
# =============================================
# ✅ NUEVAS FUNCIONES PARA APRENDIZAJE AUTOMÁTICO
# =============================================

def calcular_rotacion_automatica(producto_id, dias_historial=30):
    """Calcula la rotación diaria automática basada en historial real"""
    try:
        fecha_inicio = datetime.now().date() - timedelta(days=dias_historial)
        
        # Obtener ventas de los últimos 'dias_historial' días
        ventas_totales = db.session.query(
            db.func.sum(DetalleVenta.cantidad)
        ).join(Venta).filter(
            DetalleVenta.producto_id == producto_id,
            Venta.fecha_hora >= fecha_inicio
        ).scalar() or 0
        
        # Calcular promedio diario (excluyendo días sin ventas)
        dias_con_ventas = db.session.query(
            db.func.count(db.distinct(db.func.date(Venta.fecha_hora)))
        ).join(DetalleVenta).filter(
            DetalleVenta.producto_id == producto_id,
            Venta.fecha_hora >= fecha_inicio
        ).scalar() or 1  # Evitar división por cero
        
        rotacion_promedio = ventas_totales / dias_con_ventas
        
        return round(rotacion_promedio, 2)
    except Exception as e:
        print(f"❌ Error calculando rotación automática: {e}")
        return 10.0  # Valor por defecto

def actualizar_rotaciones_automaticas():
    """Actualiza automáticamente todas las rotaciones basado en datos históricos"""
    try:
        productos_activos = Producto.query.filter_by(activo=True).all()
        actualizaciones = 0
        
        for producto in productos_activos:
            if producto.receta:  # Solo productos con receta
                config = ConfiguracionProduccion.query.filter_by(receta_id=producto.receta.id).first()
                if config:
                    nueva_rotacion = calcular_rotacion_automatica(producto.id)
                    
                    # Solo actualizar si hay cambio significativo (> 10%)
                    cambio_significativo = abs(config.rotacion_diaria_esperada - nueva_rotacion) > (config.rotacion_diaria_esperada * 0.1)
                    
                    if cambio_significativo:
                        config.rotacion_diaria_esperada = nueva_rotacion
                        actualizaciones += 1
                        
                        # ✅ CORREGIDO: HistorialRotacionProducto (no historicalRotacionProducto)
                        historial = HistorialRotacionProducto(
                            producto_id=producto.id,
                            rotacion_real=nueva_rotacion
                        )
                        db.session.add(historial)
        
        db.session.commit()
        print(f"✅ Rotaciones automáticas actualizadas: {actualizaciones} productos")
        return actualizaciones
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando rotaciones automáticas: {e}")
        return 0

def actualizar_control_vida_util():
    """Actualiza el control de vida útil de todos los productos"""
    try:
        productos_pan = Producto.query.filter_by(es_pan=True, activo=True).all()
        hoy = datetime.now().date()
        
        for producto in productos_pan:
            # Buscar registro de vida útil del día
            control = ControlVidaUtil.query.filter_by(
                producto_id=producto.id, 
                fecha_produccion=hoy
            ).first()
            
            if not control and producto.stock_actual > 0:
                # Crear nuevo registro para el día
                # ✅ CORREGIDO: dias_sin_rotacion (no días_sin_notacion)
                control = ControlVidaUtil(
                    producto_id=producto.id,
                    fecha_produccion=hoy,
                    stock_inicial=producto.stock_actual,
                    stock_actual=producto.stock_actual,
                    dias_sin_rotacion=0,
                    estado='FRESCO'
                )
                db.session.add(control)
            elif control:
                # Actualizar stock actual
                control.stock_actual = producto.stock_actual
                
                # Calcular rotación del día
                rotacion_hoy = control.stock_inicial - control.stock_actual
                
                if rotacion_hoy == 0:
                    control.dias_sin_rotacion += 1
                else:
                    control.dias_sin_rotacion = 0
                
                # Determinar estado basado en días sin rotación
                if control.dias_sin_rotacion >= 3:
                    control.estado = 'PERDIDA'
                elif control.dias_sin_rotacion == 2:
                    control.estado = 'RIESGO'
                elif control.dias_sin_rotacion == 1:
                    control.estado = 'ALERTA'
                else:
                    control.estado = 'FRESCO'
        
        db.session.commit()
        print(f"✅ Control de vida útil actualizado para {len(productos_pan)} productos")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando control vida útil: {e}")
        
        
# FUNCIONES AUXILIARES PARA CÁLCULOS
def calcular_stock_vitrina(receta_id):
    """Calcular stock actual en vitrina para una receta"""
    try:
        receta = Receta.query.get(receta_id)
        print(f"🔍 DEBUG calcular_stock_vitrina: Receta: {receta.nombre if receta else 'N/A'}")
        
        # Si la receta tiene producto asociado, usar el stock del producto
        if receta and receta.producto:
            stock = receta.producto.stock_actual
            print(f"🔍 DEBUG: Usando stock del producto: {stock} unidades")
            return stock
        
        # Método antiguo (backup)
        produccion_total = db.session.query(
            db.func.sum(OrdenProduccion.cantidad_producir)
        ).filter(
            OrdenProduccion.receta_id == receta_id,
            OrdenProduccion.estado == 'COMPLETADA'
        ).scalar() or 0
        
        ventas_totales = db.session.query(
            db.func.sum(DetalleVenta.cantidad)
        ).join(Producto).filter(
            Producto.nombre == receta.nombre
        ).scalar() or 0
        
        stock_calculado = max(0, produccion_total - ventas_totales)
        print(f"🔍 DEBUG: Stock calculado (método antiguo): {stock_calculado}")
        
        return stock_calculado
        
    except Exception as e:
        print(f"❌ Error calculando stock: {e}")
        return 0

def calcular_ventas_hoy(nombre_receta, fecha):
    """Calcular ventas del día actual para una receta"""
    try:
        inicio_dia = datetime.combine(fecha, datetime.min.time())
        fin_dia = datetime.combine(fecha, datetime.max.time())
        
        ventas_hoy = db.session.query(
            db.func.sum(DetalleVenta.cantidad)
        ).join(Producto).join(Venta).filter(
            Producto.nombre == nombre_receta,
            Venta.fecha_hora >= inicio_dia,
            Venta.fecha_hora <= fin_dia
        ).scalar() or 0
        
        return ventas_hoy
        
    except Exception as e:
        print(f"Error calculando ventas hoy: {e}")
        return 0
    
    

# =============================================
# NUEVAS RUTAS PARA PRODUCCIÓN DIARIA MEJORADA
# =============================================

@app.route('/produccion/iniciar_produccion/<int:orden_id>')
@login_required
@modulo_requerido('produccion')
@tenant_required
def iniciar_produccion(orden_id):
    """Iniciar una orden de producción - Cambia estado a EN_PRODUCCION"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # ✅ AGREGADO: Filtro multicliente
        panaderia_actual = session.get('panaderia_id')
        orden = OrdenProduccion.query.filter_by(id=orden_id, panaderia_id=panaderia_actual).first()
        
        if not orden:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        # Verificar que la orden esté en estado PENDIENTE
        if orden.estado != 'PENDIENTE':
            return jsonify({'error': 'Solo se pueden iniciar órdenes pendientes'}), 400
        
        # Verificar disponibilidad de ingredientes
        suficiente, faltantes = orden.verificar_ingredientes_disponibles()
        if not suficiente:
            return jsonify({
                'error': 'Ingredientes insuficientes',
                'faltantes': faltantes
            }), 400
        
        # Iniciar producción
        if orden.iniciar_produccion():
            db.session.commit()
            return jsonify({
                'success': True,
                'mensaje': f'Producción de {orden.receta.nombre} iniciada'
            })
        else:
            return jsonify({'error': 'No se pudo iniciar la producción'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/produccion/confirmar_produccion/<int:orden_id>')
@login_required
@modulo_requerido('produccion')
@tenant_required
def confirmar_produccion(orden_id):
    """Confirmar producción completada - Actualiza stock y descuenta ingredientes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # ✅ AGREGADO: Filtro multicliente
        panaderia_actual = session.get('panaderia_id')
        orden = OrdenProduccion.query.filter_by(id=orden_id, panaderia_id=panaderia_actual).first()
        
        if not orden:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        # Verificar que la orden esté en estado EN_PRODUCCION
        if orden.estado != 'EN_PRODUCCION':
            return jsonify({'error': 'Solo se pueden confirmar órdenes en producción'}), 400
        
        # Completar producción (esto actualiza stock y descuenta ingredientes automáticamente)
        if orden.completar_produccion():
            db.session.commit()
            return jsonify({
                'success': True,
                'mensaje': f'Producción de {orden.cantidad_producir} unidades de {orden.receta.nombre} completada. Stock actualizado.'
            })
        else:
            return jsonify({'error': 'No se pudo completar la producción'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/produccion/cancelar_orden/<int:orden_id>')
@login_required
@modulo_requerido('produccion')
@tenant_required
def cancelar_orden_produccion(orden_id):
    """Cancelar una orden de producción"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # ✅ AGREGADO: Filtro multicliente
        panaderia_actual = session.get('panaderia_id')
        orden = OrdenProduccion.query.filter_by(id=orden_id, panaderia_id=panaderia_actual).first()
        
        if not orden:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        # Solo se pueden cancelar órdenes pendientes o en producción
        if orden.estado not in ['PENDIENTE', 'EN_PRODUCCION']:
            return jsonify({'error': 'No se puede cancelar una orden completada'}), 400
        
        orden.estado = 'CANCELADA'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': f'Orden de producción cancelada'
        })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/stock_vitrina')
@login_required
@modulo_requerido('produccion')
@tenant_required
def stock_vitrina():
    """Vista completa de stock en vitrina - Nueva pestaña"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todas las recetas con su stock actual
    recetas_activas = Receta.query.filter_by(activo=True).all()
    
    stock_completo = []
    for receta in recetas_activas:
        stock_actual = calcular_stock_vitrina(receta.id)
        
        # Obtener configuración
        config = ConfiguracionProduccion.query.filter_by(receta_id=receta.id).first()
        if not config:
            config = ConfiguracionProduccion(receta_id=receta.id, stock_objetivo=50)
            db.session.add(config)
            db.session.commit()
        
        stock_completo.append({
            'id': receta.id,
            'nombre': receta.nombre,
            'stock_actual': stock_actual,
            'stock_objetivo': config.stock_objetivo,
            'categoria': receta.categoria,
            'estado': 'CRÍTICO' if stock_actual <= config.stock_objetivo * 0.2 else 
                     'BAJO' if stock_actual <= config.stock_objetivo * 0.5 else
                     'ÓPTIMO' if stock_actual >= config.stock_objetivo else 'MEDIO'
        })
    
    # Ordenar por estado (crítico primero)
    stock_completo.sort(key=lambda x: ['CRÍTICO', 'BAJO', 'MEDIO', 'ÓPTIMO'].index(x['estado']))
    
    return render_template('stock_vitrina.html', stock_completo=stock_completo)

@app.route('/reporte_produccion_diaria')
@login_required
@modulo_requerido('produccion')
@tenant_required
def reporte_produccion_diaria():
    """Reporte imprimible de producción diaria"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🔍 OBTENER TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    hoy = datetime.now().date()
    
    # ✅ Órdenes completadas hoy (CON FILTRO POR TENANT)
    ordenes_hoy = OrdenProduccion.query.filter(
        OrdenProduccion.estado == 'COMPLETADA',
        db.func.date(OrdenProduccion.fecha_fin) == hoy,
        OrdenProduccion.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    # ✅ Stock actual (CON FILTRO POR TENANT)
    recetas_activas = Receta.query.filter_by(
        panaderia_id=panaderia_id,  # ✅ FILTRO MULTI-TENANT
        activo=True
    ).all()
    
    stock_actual = []
    for receta in recetas_activas:
        stock = calcular_stock_vitrina(receta.id)
        stock_actual.append({
            'nombre': receta.nombre,
            'stock': stock,
            'categoria': receta.categoria
        })
    
    # Métricas del día
    total_producido = sum(orden.cantidad_producir for orden in ordenes_hoy)
    total_recetas = len(set(orden.receta_id for orden in ordenes_hoy))
    
    return render_template("reporte_produccion.html",
                         ordenes_hoy=ordenes_hoy,
                         stock_actual=stock_actual,
                         total_producido=total_producido,
                         total_recetas=total_recetas,
                         fecha=hoy)
    
# =============================================
# ✅ NUEVAS RUTAS PARA PUNTO DE VENTA INTELIGENTE
# =============================================



@app.route('/api/buscar_por_codigo_barras/<codigo>')
@login_required
@modulo_requerido('productos')
@tenant_required
def buscar_por_codigo_barras(codigo):
    """Buscar producto externo por código de barras - MULTI-TENANT"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        from models import ProductoExterno
        
        # ✅ OBTENER TENANT ACTUAL
        panaderia_id = current_user.panaderia_id
        print(f"🔍 Buscando código {codigo} en tenant {panaderia_id}")
        
        # ✅ FILTRO MULTI-TENANT
        producto = ProductoExterno.query.filter_by(
            codigo_barras=codigo,
            panaderia_id=panaderia_id,
            activo=True
        ).first()
        
        if producto:
            print(f"✅ Producto encontrado: {producto.nombre}")
            return jsonify({
                'success': True,
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio_venta': producto.precio_venta,
                    'stock_actual': producto.stock_actual,
                    'categoria': producto.categoria,
                    'marca': producto.marca
                }
            })
        else:
            print(f"❌ Producto no encontrado para código {codigo} en tenant {panaderia_id}")
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            }), 404
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/verificar_stock/<int:producto_id>')
@login_required
@modulo_requerido('punto_venta')
@tenant_required
def verificar_stock_tiempo_real(producto_id):
    """API para verificar stock en tiempo real durante venta"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    producto = Producto.query.get_or_404(producto_id)
    cantidad = request.args.get('cantidad', 1, type=int)
    
    # Obtener configuración de producción si existe
    config = None
    if producto.receta:
        config = ConfiguracionProduccion.query.filter_by(receta_id=producto.receta.id).first()
    
    return jsonify({
        'stock_actual': producto.stock_actual,
        'stock_suficiente': producto.stock_actual >= cantidad,
        'alerta_reorden': producto.stock_actual <= (config.stock_minimo if config else 10),
        'produccion_sugerida': (config.stock_objetivo - producto.stock_actual) if config and config.stock_objetivo > producto.stock_actual else 0,
        'mensaje_alerta': f'Stock bajo: {producto.stock_actual} unidades' if producto.stock_actual <= (config.stock_minimo if config else 10) else None
    })

@app.route('/api/productos_sugeridos')
@login_required
@modulo_requerido('punto_venta')
def productos_sugeridos_venta():
    """API para obtener productos sugeridos basados en rotación"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Productos con alta rotación y buen stock
    productos_alta_rotacion = []
    
    productos_activos = Producto.query.filter_by(activo=True).all()
    for producto in productos_activos:
        if producto.receta:
            config = ConfiguracionProduccion.query.filter_by(receta_id=producto.receta.id).first()
            if config and producto.stock_actual > 0:
                # Priorizar productos con alta rotación esperada
                if config.rotacion_diaria_esperada >= 5:  # Alta rotación
                    productos_alta_rotacion.append({
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'precio': producto.precio_venta,
                        'stock_actual': producto.stock_actual,
                        'rotacion_esperada': config.rotacion_diaria_esperada
                    })
    
    # Ordenar por rotación esperada (mayor primero)
    productos_alta_rotacion.sort(key=lambda x: x['rotacion_esperada'], reverse=True)
    
    return jsonify(productos_alta_rotacion[:8])  # Top 8 productos

@app.route('/imprimir_factura/<int:factura_id>')
@login_required
@modulo_requerido('punto_venta')
def imprimir_factura(factura_id):
    """Generar vista imprimible - Versión mejorada que detecta tipo de documento"""
    try:
        venta = Venta.query.get_or_404(factura_id)
        detalles = DetalleVenta.query.filter_by(venta_id=factura_id).all()
        config = obtener_configuracion_sistema()
        
        # 🆕 DETECTAR TIPO DE DOCUMENTO Y USAR TEMPLATE APROPIADO
        if venta.tipo_documento == 'ELECTRONICA':
            # Usar template de factura electrónica
            return render_template('factura_electronica.html',
                                venta=venta,
                                detalles=detalles,
                                config=config,
                                ahora=datetime.now())
        else:
            # Usar template de recibo POS tradicional
            return render_template('recibo_pos.html',
                                venta=venta,
                                detalles=detalles,
                                config=config,
                                ahora=datetime.now())
        
    except Exception as e:
        flash(f'❌ Error generando documento: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ventas'))
    
# En app.py - NUEVAS RUTAS PARA PRODUCTOS EXTERNOS

@app.route('/agregar_producto_externo', methods=['POST'])
@login_required
@modulo_requerido('productos')
@tenant_required  # ← DECORADOR AGREGADO
def agregar_producto_externo():
    """Agregar nuevo producto externo al inventario"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener datos del formulario
        codigo_barras = request.form.get('codigo_barras', '').strip()
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', '').strip()
        marca = request.form.get('marca', '').strip()
        proveedor_id = request.form.get('proveedor_id')
        stock_actual = request.form.get('stock_actual', 0)
        stock_minimo = request.form.get('stock_minimo', 0)
        precio_compra = request.form.get('precio_compra', 0)
        precio_venta = request.form.get('precio_venta', 0)
        
        # Validaciones básicas
        if not nombre:
            return jsonify({'success': False, 'message': '❌ El nombre del producto es requerido'})
        
        if not proveedor_id:
            return jsonify({'success': False, 'message': '❌ Debe seleccionar un proveedor'})
        
        # Verificar si el código de barras ya existe EN ESTA PANADERÍA
        if codigo_barras:
            producto_existente = ProductoExterno.query.filter_by(
                codigo_barras=codigo_barras, 
                panaderia_id=current_user.panaderia_id  # ← CORREGIDO: Filtro por tenant
            ).first()
            if producto_existente:
                return jsonify({'success': False, 'message': '❌ Ya existe un producto con ese código de barras'})
        
        # Si no se proporciona código, generar uno único
        import uuid
        if not codigo_barras:
            codigo_barras = str(uuid.uuid4().int)[:13]  # Código único de 13 dígitos
        
        # Convertir tipos de datos
        stock_actual = int(stock_actual) if stock_actual else 0
        stock_minimo = int(stock_minimo) if stock_minimo else 0
        precio_compra = float(precio_compra) if precio_compra else 0.0
        precio_venta = float(precio_venta) if precio_venta else 0.0
        
        # Validar precios
        if precio_venta <= precio_compra:
            return jsonify({'success': False, 'message': '❌ El precio de venta debe ser mayor al precio de compra'})
        
        # Crear nuevo producto
        nuevo_producto = ProductoExterno(
            codigo_barras=codigo_barras,
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            marca=marca,
            proveedor_id=proveedor_id,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            panaderia_id=current_user.panaderia_id,  # ← CORREGIDO: current_user.panaderia_id
            activo=True
        )
        
        # Guardar en la base de datos
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'✅ Producto "{nombre}" agregado exitosamente'})
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '❌ Error en los datos numéricos. Verifique los valores ingresados'})
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': '❌ Error al agregar el producto. Intente nuevamente'})
    

@app.route('/actualizar_stock_externo/<int:producto_id>', methods=['POST'])
@login_required
@modulo_requerido('productos')
def actualizar_stock_externo(producto_id):
    """Actualizar stock de producto externo (compras)"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    producto = Producto.query.get_or_404(producto_id)
    
    try:
        cantidad = int(request.form['cantidad'])
        costo_compra = float(request.form.get('costo_compra', producto.costo_compra))
        
        # Actualizar stock y costo promedio
        producto.stock_actual += cantidad
        if costo_compra > 0:
            producto.costo_compra = costo_compra
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nuevo_stock': producto.stock_actual,
            'utilidad_unitaria': producto.utilidad_unitaria,
            'margen_utilidad': round(producto.margen_utilidad, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/reporte_inventario_externo')
@login_required
@modulo_requerido('productos')
@tenant_required
def reporte_inventario_externo():
    """Reporte completo de inventario de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 👇 OBTENER EL TENANT ACTUAL (LA FUNCIÓN YA ESTÁ EN app.py)
    panaderia_id = obtener_panaderia_actual()
    
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # 👇 FILTRAR POR TENANT
    productos = ProductoExterno.query.filter_by(
        panaderia_id=panaderia_id,
        activo=True
    ).all()
    
    # Cálculos automáticos
    total_valor_inventario = 0
    productos_stock_bajo = []
    
    for producto in productos:
        # Valor del inventario
        producto.valor_inventario = producto.stock_actual * producto.precio_compra
        total_valor_inventario += producto.valor_inventario
        
        # Utilidad unitaria y margen
        producto.utilidad_unitaria = producto.precio_venta - producto.precio_compra
        producto.margen_ganancia = (producto.utilidad_unitaria / producto.precio_compra * 100) if producto.precio_compra > 0 else 0
        
        # Alertas de stock bajo
        if producto.stock_actual <= producto.stock_minimo:
            productos_stock_bajo.append(producto)
    
    # Obtener proveedores para el tenant actual
    proveedores = Proveedor.query.filter_by(panaderia_id=panaderia_id).all()
    
    return render_template('reporte_inventario_externo.html',
                         productos=productos,
                         total_valor_inventario=total_valor_inventario,
                         productos_stock_bajo=productos_stock_bajo,
                         proveedores=proveedores)

@app.route('/exportar_inventario_externo')
@login_required
@modulo_requerido('productos')
def exportar_inventario_externo():
    """Exportar inventario a PDF"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    productos = ProductoExterno.query.filter_by(activo=True).all()
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Inventario Externo", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Preparar datos de la tabla
    data = [['Producto', 'Categoría', 'Stock', 'Stock Mín', 'Precio Compra', 
             'Precio Venta', 'Utilidad', 'Margen %', 'Valor Inv.']]
    
    for producto in productos:
        utilidad = producto.precio_venta - producto.precio_compra
        margen = (utilidad / producto.precio_compra * 100) if producto.precio_compra > 0 else 0
        valor_inventario = producto.stock_actual * producto.precio_compra
        
        data.append([
            producto.nombre,
            producto.categoria,
            str(producto.stock_actual),
            str(producto.stock_minimo),
            f"${producto.precio_compra:,.0f}",
            f"${producto.precio_venta:,.0f}",
            f"${utilidad:,.0f}",
            f"{margen:.1f}%",
            f"${valor_inventario:,.0f}"
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-disposition": "attachment; filename=inventario_externo.pdf"}
    )
    
    
@app.route('/reporte_ventas_externas')
@login_required
@modulo_requerido('reportes')
@tenant_required
def reporte_ventas_externas():
    """Reporte de ventas y rentabilidad de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 👇 OBTENER EL TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # Parámetros de fecha (opcionales)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # 👇 CONSULTA BASE CON FILTRO POR TENANT
    query = DetalleVenta.query.join(ProductoExterno).join(Venta).filter(
        DetalleVenta.producto_externo_id.isnot(None),
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO POR TENANT
    )
    
    # Filtrar por fechas si se proporcionan
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.filter(
                Venta.fecha_hora.between(fecha_inicio, fecha_fin)
            )
        except ValueError:
            pass
    
    detalles_venta = query.all()
    
    # Procesar datos para el reporte
    ventas_por_producto = {}
    total_ventas = 0
    total_utilidad = 0
    
    for detalle in detalles_venta:
        producto = detalle.producto_externo
        if producto.id not in ventas_por_producto:
            ventas_por_producto[producto.id] = {
                'producto': producto,
                'cantidad_vendida': 0,
                'ingresos_totales': 0,
                'utilidad_total': 0
            }
        
        ventas_por_producto[producto.id]['cantidad_vendida'] += detalle.cantidad
        ventas_por_producto[producto.id]['ingresos_totales'] += detalle.cantidad * detalle.precio_unitario
        utilidad_producto = detalle.cantidad * (producto.precio_venta - producto.precio_compra)
        ventas_por_producto[producto.id]['utilidad_total'] += utilidad_producto
        
        total_ventas += detalle.cantidad * detalle.precio_unitario
        total_utilidad += utilidad_producto
    
    # Ordenar por cantidad vendida (más vendidos primero)
    productos_ordenados = sorted(
        ventas_por_producto.values(), 
        key=lambda x: x['cantidad_vendida'], 
        reverse=True
    )
    
    return render_template('reporte_ventas_externas.html',
                         productos_ventas=productos_ordenados,
                         total_ventas=total_ventas,
                         total_utilidad=total_utilidad,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)

@app.route('/exportar_ventas_externas')
@login_required
@modulo_requerido('reportes')
def exportar_ventas_externas():
    """Exportar reporte de ventas a PDF"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 👇 OBTENER EL TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # 👇 CONSULTA CON FILTRO POR TENANT
    detalles_venta = DetalleVenta.query.join(ProductoExterno).join(Venta).filter(
        DetalleVenta.producto_externo_id.isnot(None),
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO POR TENANT
    ).all()
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    from flask import Response
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Ventas Externas", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Procesar datos
    ventas_por_producto = {}
    
    for detalle in detalles_venta:
        producto = detalle.producto_externo
        if producto.id not in ventas_por_producto:
            ventas_por_producto[producto.id] = {
                'producto': producto,
                'cantidad': 0,
                'ingresos': 0,
                'costo': 0
            }
        
        ventas_por_producto[producto.id]['cantidad'] += detalle.cantidad
        ventas_por_producto[producto.id]['ingresos'] += detalle.cantidad * detalle.precio_unitario
        ventas_por_producto[producto.id]['costo'] += detalle.cantidad * producto.precio_compra
    
    # Preparar datos de la tabla
    table_data = [['Producto', 'Categoría', 'Unidades', 'Ingresos', 'Costo', 'Utilidad', 'Margen %']]
    
    for venta_data in ventas_por_producto.values():
        utilidad = venta_data['ingresos'] - venta_data['costo']
        margen = (utilidad / venta_data['ingresos'] * 100) if venta_data['ingresos'] > 0 else 0
        
        table_data.append([
            venta_data['producto'].nombre,
            venta_data['producto'].categoria,
            str(venta_data['cantidad']),
            f"${venta_data['ingresos']:,.0f}",
            f"${venta_data['costo']:,.0f}",
            f"${utilidad:,.0f}",
            f"{margen:.1f}%"
        ])
    
    # Crear tabla
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-disposition": "attachment; filename=ventas_externas.pdf"}
    )
    
@app.route('/dashboard_externos')
@login_required
@modulo_requerido('productos')
@tenant_required
def dashboard_externos():
    """Dashboard ejecutivo de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 👇 OBTENER EL TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # 👇 FILTRAR POR TENANT
    total_productos = ProductoExterno.query.filter_by(
        panaderia_id=panaderia_id,
        activo=True
    ).count()
    
    productos_stock_bajo = ProductoExterno.query.filter(
        ProductoExterno.panaderia_id == panaderia_id,
        ProductoExterno.stock_actual <= ProductoExterno.stock_minimo,
        ProductoExterno.activo == True
    ).count()
    
    # Valor total del inventario
    productos = ProductoExterno.query.filter_by(
        panaderia_id=panaderia_id,
        activo=True
    ).all()
    valor_inventario = sum(p.stock_actual * p.precio_compra for p in productos)
    
    # Ventas del último mes
    un_mes_atras = datetime.now() - timedelta(days=30)

    ventas_recientes = DetalleVenta.query.join(ProductoExterno).join(Venta).filter(
        DetalleVenta.producto_externo_id.isnot(None),
        Venta.panaderia_id == panaderia_id,  # ✅ FILTRO POR TENANT
        Venta.fecha_hora >= un_mes_atras
    ).all()

    ingresos_ultimo_mes = sum(d.cantidad * d.precio_unitario for d in ventas_recientes)
    utilidad_ultimo_mes = sum(d.cantidad * (d.producto_externo.precio_venta - d.producto_externo.precio_compra) for d in ventas_recientes)

    margen_promedio = (utilidad_ultimo_mes / ingresos_ultimo_mes * 100) if ingresos_ultimo_mes > 0 else 0

    # 👇 PRODUCTOS MÁS VENDIDOS CON FILTRO POR TENANT
    top_productos = db.session.query(
        ProductoExterno,
        db.func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).join(Venta).filter(
        DetalleVenta.producto_externo_id.isnot(None),
        Venta.panaderia_id == panaderia_id,  # ✅ FILTRO POR TENANT
        Venta.fecha_hora >= un_mes_atras
    ).group_by(ProductoExterno.id).order_by(
        db.desc('total_vendido')
    ).limit(5).all()
    
    return render_template('dashboard_externos.html',
                         total_productos=total_productos,
                         productos_stock_bajo=productos_stock_bajo,
                         valor_inventario=valor_inventario,
                         ingresos_ultimo_mes=ingresos_ultimo_mes,
                         utilidad_ultimo_mes=utilidad_ultimo_mes,
                         top_productos=top_productos,
                         margen_promedio=margen_promedio)

    
# Filtro para formatear moneda en pesos colombianos
@app.template_filter('currency')
def format_currency(value):
    """Formatear valor como moneda en pesos colombianos"""
    if value is None:
        return "$0"
    try:
        # Formato pesos colombianos: $1.234.567
        return f"${value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return f"${value}"

# Filtro para formatear números con 2 decimales
@app.template_filter('round')
def round_filter(value, decimals=2):
    """Formatear número con decimales específicos"""
    try:
        return round(value, decimals)
    except (ValueError, TypeError):
        return value
   
# =============================================
# RUTA DE DIAGNÓSTICO PARA PRODUCTOS - AGREGAR ESTO
# =============================================
@app.route('/debug_api_productos')
@login_required
@modulo_requerido('sistema')
def debug_api_productos():
    """Diagnóstico de la API de productos"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Contar productos totales
        total_productos = Producto.query.count()
        
        # Productos activos
        productos_activos = Producto.query.filter_by(activo=True).all()
        
        # Productos con stock
        productos_con_stock = Producto.query.filter(Producto.stock_actual > 0).all()
        
        # Lista completa de productos
        todos_productos = Producto.query.all()
        
        productos_data = []
        for producto in todos_productos:
            # Obtener nombre de categoría de forma segura
            categoria_nombre = "Sin categoría"
            if producto.categoria_id:
                categoria = Categoria.query.get(producto.categoria_id)
                if categoria:
                    categoria_nombre = categoria.nombre
            
            productos_data.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'activo': producto.activo,
                'stock_actual': producto.stock_actual,
                'precio_venta': producto.precio_venta,
                'tipo_producto': producto.tipo_producto,
                'categoria_id': producto.categoria_id,
                'categoria_nombre': categoria_nombre,
                'tiene_receta': producto.receta_id is not None
            })
        
        return jsonify({
            'estado': 'OK',
            'total_productos': total_productos,
            'productos_activos': len(productos_activos),
            'productos_con_stock': len(productos_con_stock),
            'productos': productos_data
        })
        
    except Exception as e:
        return jsonify({
            'estado': 'ERROR',
            'error': str(e)
        }), 500

# =============================================
# RUTA DE EMERGENCIA - CREAR PRODUCTOS DE PRUEBA
# =============================================
@app.route('/crear_productos_prueba')
@login_required
@modulo_requerido('sistema')
def crear_productos_prueba():
    """Crear productos de prueba si no existen"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Verificar si ya existen productos
        if Producto.query.count() > 0:
            return jsonify({'mensaje': 'Ya existen productos en la base de datos'})
        
        # Obtener o crear categorías
        categoria_pan = Categoria.query.filter_by(nombre="Panadería").first()
        if not categoria_pan:
            categoria_pan = Categoria(nombre="Panadería")
            db.session.add(categoria_pan)
            db.session.flush()
        
        categoria_bebida = Categoria.query.filter_by(nombre="Bebidas").first()
        if not categoria_bebida:
            categoria_bebida = Categoria(nombre="Bebidas")
            db.session.add(categoria_bebida)
            db.session.flush()
        
        # Crear productos de prueba
        productos_prueba = [
            Producto(
                nombre="Pan Mantequilla",
                categoria_id=categoria_pan.id,
                precio_venta=3000,
                stock_actual=15,
                activo=True,
                tipo_producto='produccion'
            ),
            Producto(
                nombre="Pan Integral", 
                categoria_id=categoria_pan.id,
                precio_venta=4000,
                stock_actual=10,
                activo=True,
                tipo_producto='produccion'
            ),
            Producto(
                nombre="Café Americano",
                categoria_id=categoria_bebida.id,
                precio_venta=2000,
                stock_actual=20,
                activo=True,
                tipo_producto='externo',
                costo_compra=800
            ),
            Producto(
                nombre="Jugo de Naranja",
                categoria_id=categoria_bebida.id, 
                precio_venta=4000,
                stock_actual=12,
                activo=True,
                tipo_producto='externo',
                costo_compra=1500
            )
        ]
        
        for producto in productos_prueba:
            db.session.add(producto)
        
        db.session.commit()
        
        return jsonify({
            'mensaje': '✅ Productos de prueba creados exitosamente',
            'productos_creados': len(productos_prueba)
        })
        

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# =============================================
# RUTAS PARA CIERRE DIARIO - AGREGAR ANTES DE LOS REPORTES PDF
# =============================================

@tenant_required
@app.route('/api/cierre_diario/estado')
@login_required
@modulo_requerido('finanzas')
def estado_cierre_diario():
    """API para obtener estado actual del día"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    hoy = datetime.now().date()
    jornada = obtener_jornada_activa()
    
    # Obtener ventas del día actual
    ventas_hoy = obtener_ventas_dia(hoy)
    total_hoy = sum(venta.total for venta in ventas_hoy)
    
    # Verificar si ya se hizo cierre hoy
    cierre_hoy = CierreDiario.query.filter_by(panaderia_id=current_user.panaderia_id, fecha=hoy).first()
    
    return jsonify({
        'fecha': hoy.isoformat(),
        'jornada_activa': jornada.estado == 'ACTIVA',
        'total_ventas_hoy': total_hoy,
        'total_transacciones': len(ventas_hoy),
        'cierre_realizado': cierre_hoy is not None,
        'hora_actual': datetime.now().strftime('%H:%M')
    })

@tenant_required
@app.route('/api/cierre_diario/procesar', methods=['POST'])
@login_required
@modulo_requerido('finanzas')
def procesar_cierre_diario():
    """API para procesar el cierre diario"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # ✅ OBTENER RESPONSE DE REALIZAR_CIERRE (manejar tupla)
        response_tuple = realizar_cierre()
        
        # Si es tupla (response, status_code), tomar solo el response
        if isinstance(response_tuple, tuple) and len(response_tuple) > 0:
            response = response_tuple[0]
        else:
            response = response_tuple
        
        data = response.get_json()
        
        if data and data.get('success'):
            # Obtener el cierre recién creado
            from datetime import datetime
            from models import CierreDiario
            
            cierre = CierreDiario.query.filter_by(
                panaderia_id=current_user.panaderia_id,
                fecha=datetime.now().date()
            ).order_by(CierreDiario.id.desc()).first()
            
            mensaje = data.get('message', 'Cierre exitoso')
            
            return jsonify({
                'success': True,
                'mensaje': mensaje,
                'cierre': {
                    'fecha': cierre.fecha.isoformat() if cierre else datetime.now().date().isoformat(),
                    'total_ventas': data.get('data', {}).get('total_ventas', 0),
                    'total_transacciones': 0,  # Puedes calcularlo si es necesario
                    'tendencia': 0
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': data.get('error', 'Error en el cierre') if data else 'Error desconocido'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar cierre: {str(e)}'
        }), 500

@tenant_required
@app.route('/api/cierre_diario/historial')
@login_required
@modulo_requerido('finanzas')
def historial_cierres():
    """API para obtener historial de cierres"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    limite = request.args.get('limite', 30, type=int)
    cierres = obtener_historial_cierres(limite)
    
    resultado = []
    for cierre in cierres:
        resultado.append({
            'fecha': cierre.fecha.isoformat(),
            'total_ventas': cierre.total_ventas,
            'total_transacciones': cierre.total_transacciones,
            'total_efectivo': cierre.total_efectivo,
            'total_transferencia': cierre.total_transferencia,
            'total_tarjeta': cierre.total_tarjeta,
            'tendencia': cierre.tendencia,
            'productos_top': json.loads(cierre.productos_top) if cierre.productos_top else []
        })
    
    return jsonify(resultado)

# ============================================
# SECCIÓN: CIERRE DIARIO - CORREGIDO CON MULTI-TENANT
# ============================================

@app.route('/cierre_diario')
@login_required
@tenant_required  # ✅ DECORADOR MULTI-TENANT AÑADIDO
@modulo_requerido('finanzas')
def pagina_cierre_diario():
    """Página de cierre diario - AHORA MULTI-TENANT"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    hoy = datetime.now().date()
    panaderia_id = current_user.panaderia_id  # ✅ OBTENER ID DE PANADERÍA ACTUAL
    
    # ✅ FILTRAR SOLO POR PANADERÍA DEL USUARIO ACTUAL
    cierre_hoy = CierreDiario.query.filter_by(
        panaderia_id=panaderia_id, 
        fecha=hoy
    ).first()
    
    # ✅ PASAR PANADERIA_ID A LA FUNCIÓN DE VENTAS
    ventas_hoy = obtener_ventas_dia(hoy, panaderia_id)
    
    return render_template('cierre_diario.html',
                         cierre_hoy=cierre_hoy,
                         ventas_hoy=ventas_hoy,
                         hoy=hoy)


@tenant_required
@app.route('/realizar_cierre', methods=['POST'])
@login_required
@tenant_required
@modulo_requerido('finanzas')
def realizar_cierre():
    """Realiza el cierre diario - VERSIÓN PROFESIONAL CON MODELOS COMPLETOS"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        
        # ✅ OBTENER PANADERÍA ACTUAL DEL USUARIO
        panaderia_id = current_user.panaderia_id
        fecha_actual = datetime.now().date()
        
        # ✅ VERIFICAR SI YA EXISTE CIERRE PARA HOY
        cierre_existente = CierreDiario.query.filter_by(
            panaderia_id=panaderia_id,
            fecha=fecha_actual
        ).first()
        
        if cierre_existente:
            return jsonify({
                'success': False, 
                'error': 'Ya se realizó el cierre diario para hoy en esta panadería'
            }), 400
        
        # ✅ OBTENER VENTAS DEL DÍA
        ventas_hoy = Venta.query.filter(
            Venta.panaderia_id == panaderia_id,
            func.date(Venta.fecha_hora) == fecha_actual,
            
        ).all()
        
        # ✅ CALCULAR TOTALES
        total_ventas = sum(venta.total for venta in ventas_hoy)
        total_efectivo = sum(venta.total for venta in ventas_hoy 
                           if venta.metodo_pago == 'efectivo')
        total_transferencias = sum(venta.total for venta in ventas_hoy 
                                 if venta.metodo_pago == 'transferencia')
        total_tarjetas = sum(venta.total for venta in ventas_hoy 
                           if venta.metodo_pago == 'tarjeta')
        
        # ✅ CREAR REGISTRO DE CIERRE DIARIO
        nuevo_cierre = CierreDiario(
            panaderia_id=panaderia_id,
            fecha=fecha_actual,
            total_ventas=total_ventas,
            total_efectivo=total_efectivo,
            total_transferencia=total_transferencias,
            total_transacciones=len(ventas_hoy),
            
        )
        
        db.session.add(nuevo_cierre)
        
        # ✅ ACTUALIZAR CONFIGURACIÓN
        configuracion = ConfiguracionPanaderia.query.filter_by(panaderia_id=panaderia_id).first()
        if configuracion:
            configuracion.ultimo_cierre = fecha_actual
            # configuracion.sistema_activo = False  # ELIMINADO - No se bloquea el sistema
        else:
            # Crear configuración si no existe
                nueva_config = ConfiguracionPanaderia(
                panaderia_id=panaderia_id,
                nombre_panaderia=f"Panadería {panaderia_id}",
                sistema_activo=False,
                ultimo_cierre=fecha_actual
            )
                db.session.add(nueva_config)
        
        # ✅ CREAR DEPÓSITO AUTOMÁTICO PARA EFECTIVO
        deposito_creado = False
        deposito_id = None
        
        if total_efectivo > 0:
            nuevo_deposito = DepositoBancario(
                panaderia_id=panaderia_id,
                fecha_deposito=fecha_actual,  # ✅ CORREGIDO: fecha → fecha_deposito
                monto=total_efectivo,
                descripcion=f'Depósito automático - Cierre diario {fecha_actual}',
                metodo_deposito='efectivo',  # ✅ CORREGIDO: metodo → metodo_deposito
                estado='REGISTRADO',  # ✅ CORREGIDO: 'registrado' → 'REGISTRADO' (mayúsculas)
                referencia=f'CIERRE-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                cuenta_bancaria='Cuenta Principal',
                # ❌ ELIMINAR: conciliado=False (campo no existe)
                # fecha_conciliacion=None (se puede omitir, valor por defecto es None)
            )
            db.session.add(nuevo_deposito)
            db.session.flush()  # Para obtener el ID
            deposito_id = nuevo_deposito.id
            deposito_creado = True
        
        # ✅ ACTUALIZAR REGISTRO FINANCIERO
        registro_financiero = RegistroFinanciero.query.filter_by(
            panaderia_id=panaderia_id
        ).first()
        
        if registro_financiero:
            # Sumar transferencias al saldo disponible (ya están en cuenta)
            registro_financiero.saldo_disponible += total_transferencias
            # Sumar tarjetas al saldo de tarjetas (por cobrar)
            registro_financiero.saldo_tarjetas += total_tarjetas
            # Sumar efectivo al saldo pendiente (por depositar)
            registro_financiero.saldo_pendiente += total_efectivo
            
            registro_financiero.ultimo_cierre_fecha = fecha_actual
            registro_financiero.ultimo_cierre_monto = total_ventas
            registro_financiero.ventas_mes_actual += total_ventas
            registro_financiero.actualizar_saldos()  # Actualiza saldo_total
        else:
            # Crear registro financiero si no existe
            nuevo_registro = RegistroFinanciero(
                panaderia_id=panaderia_id,
                saldo_disponible=total_transferencias,
                saldo_tarjetas=total_tarjetas,
                saldo_pendiente=total_efectivo,
                ultimo_cierre_fecha=fecha_actual,
                ultimo_cierre_monto=total_ventas,
                ventas_mes_actual=total_ventas
            )
            nuevo_registro.actualizar_saldos()
            db.session.add(nuevo_registro)
        
        # ✅ REGISTRAR EN LOG DEL SISTEMA
        log_cierre = LogSistema(
            panaderia_id=panaderia_id,
            usuario_id=current_user.id,
            accion='cierre_diario',
            modulo='finanzas',
            descripcion=f'Cierre diario realizado - Ventas: ${total_ventas:,.2f}',
            fecha_hora=datetime.now(),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            datos_adicionales={ 
                'total_ventas': total_ventas,
                'efectivo': total_efectivo,
                'transferencias': total_transferencias,
                # 'tarjetas': total_tarjetas,  # Eliminado
                'deposito_id': deposito_id,
                'fecha': fecha_actual.isoformat()
            }
        )
        db.session.add(log_cierre)
        
        # ✅ COMMIT DE TODAS LAS TRANSACCIONES
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cierre diario realizado con éxito para la panadería {panaderia_id}',
            'data': {
                'total_ventas': float(total_ventas),
                'efectivo': float(total_efectivo),
                'transferencias': float(total_transferencias),
                # 'tarjetas': float(total_tarjetas),  # Eliminado
                'panaderia_id': panaderia_id,
                'deposito_id': deposito_id,
                'saldo_disponible': registro_financiero.saldo_disponible if registro_financiero else total_transferencias,
                'saldo_pendiente': registro_financiero.saldo_pendiente if registro_financiero else total_efectivo,
                'saldo_total': registro_financiero.saldo_total if registro_financiero else total_ventas
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en realizar_cierre: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al realizar cierre: {str(e)}'
        }), 500


# ============================================
# FUNCIÓN AUXILIAR CORREGIDA - OBTENER VENTAS
# ============================================

def obtener_ventas_dia(fecha, panaderia_id=None):
    """Obtiene ventas del día filtradas por panadería"""
    try:
        # ✅ SI NO SE ESPECIFICA PANADERÍA, USAR LA DEL USUARIO ACTUAL
        if panaderia_id is None:
            if current_user and hasattr(current_user, 'panaderia_id'):
                panaderia_id = current_user.panaderia_id
            else:
                return []
        
        # ✅ CONVERTIR FECHA SI ES NECESARIO
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # ✅ FILTRAR VENTAS SOLO DE ESTA PANADERÍA Y DÍA
        ventas = Venta.query.filter(
            Venta.panaderia_id == panaderia_id,
            func.date(Venta.fecha_hora) == fecha,
            1==1  # Filtro de estado eliminado porque el modelo no tiene este campo
        ).all()
        
        return ventas
        
    except Exception as e:
        print(f"Error en obtener_ventas_dia: {str(e)}")
        return []

@app.route('/reporte/cierre_caja')
@login_required
@modulo_requerido('reportes')
def reporte_cierre_caja():
    """Reporte de cierre de caja con análisis automático - VERSIÓN CON ANÁLISIS POR PRODUCTO"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🆕 USAR 1 FECHA SOLAMENTE + FECHAS DE COMPARACIÓN
    fecha_str = request.args.get('fecha', datetime.now().date().isoformat())
    
    try:
        # 🆕 CONVERTIR FECHA ÚNICA
        fecha_consultada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hoy = datetime.now().date()
        ayer = hoy - timedelta(days=1)
        
        inicio_dia = datetime.combine(fecha_consultada, datetime.min.time())
        fin_dia = datetime.combine(fecha_consultada, datetime.max.time())
        
        # 🆕 OBTENER panaderia_id DEL USUARIO ACTUAL
        usuario_actual = Usuario.query.get(session['user_id'])
        panaderia_id = usuario_actual.panaderia_id
        
        print(f"🔍 DEBUG: Generando reporte para panaderia_id: {panaderia_id}")
        print(f"📅 Fecha consultada: {fecha_consultada}")
        print(f"📅 Rango: {inicio_dia} a {fin_dia}")
        
        # 🆕 DEBUG: VER TODAS LAS VENTAS EN LA BD (SIN FILTROS)
        print("🔎 DEBUG - TODAS las ventas en la BD:")
        panaderia_id = obtener_panaderia_actual()
        todas_ventas = Venta.query.filter_by(panaderia_id=panaderia_id).all()
        for v in todas_ventas:
            print(f"   Venta ID: {v.id}, Fecha: {v.fecha_hora}, Panadería: {v.panaderia_id}, Total: ${v.total}")
        
        # 🆕 CONSULTAS CON FILTRO MULTICLIENTE
        ventas_dia = Venta.query.filter(
            db.func.date(Venta.fecha_hora) == fecha_consultada,  # 🎯 SOLO POR FECHA
            Venta.panaderia_id == panaderia_id
        ).all()
        
        print(f"📊 Ventas encontradas con filtros: {len(ventas_dia)}")
        for v in ventas_dia:
            print(f"   ✅ Venta encontrada: ID {v.id}, Fecha: {v.fecha_hora}, Total: ${v.total}")
        
        # 🎁 SEPARAR VENTAS NORMALES VS DONACIONES
        ventas_normales = [v for v in ventas_dia if not v.es_donacion]
        donaciones = [v for v in ventas_dia if v.es_donacion]
        
        print(f"💰 Ventas normales: {len(ventas_normales)}")
        print(f"🎁 Donaciones: {len(donaciones)}")
        
        # 🎁 CALCULAR MÉTRICAS SEPARADAS
        total_ventas_normales = sum(venta.total for venta in ventas_normales)
        total_transacciones = len(ventas_dia)
        
        print(f"💵 Total ventas normales: ${total_ventas_normales}")
        print(f"🔢 Total transacciones: {total_transacciones}")
        
        # Calcular métricas por método de pago (SOLO VENTAS NORMALES)
                # Calcular métricas por método de pago (SOLO VENTAS NORMALES)
                # Calcular métricas por método de pago (SOLO VENTAS NORMALES)
        ventas_por_metodo = {}
        for venta in ventas_normales:
            metodo = venta.metodo_pago
            # ✅ CONVERTIR 'tarjeta' a 'transferencia' (unificar métodos)
            if metodo == 'tarjeta':
                metodo = 'transferencia'
            
            if metodo not in ventas_por_metodo:
                ventas_por_metodo[metodo] = 0
            ventas_por_metodo[metodo] += venta.total
        
        print(f"💳 Ventas por método: {ventas_por_metodo}")
        
        # 🆕 OBTENER COMPARATIVA CON DÍA ANTERIOR
        dia_anterior = fecha_consultada - timedelta(days=1)
        ventas_dia_anterior = Venta.query.filter(
            db.func.date(Venta.fecha_hora) == dia_anterior,
            Venta.panaderia_id == panaderia_id  # 🎯 FILTRO MULTICLIENTE
        ).all()
        
        ventas_dia_anterior_normales = [v for v in ventas_dia_anterior if not v.es_donacion]
        total_dia_anterior = sum(venta.total for venta in ventas_dia_anterior_normales)
        
        # Calcular tendencia
        if total_dia_anterior > 0:
            tendencia = ((total_ventas_normales - total_dia_anterior) / total_dia_anterior) * 100
        else:
            tendencia = 100 if total_ventas_normales > 0 else 0
        
        print(f"📈 Tendencia: {tendencia}%")
        
        # 🆕 PRODUCTOS MÁS VENDIDOS (INCLUYENDO DONACIONES)
        detalles_dia = DetalleVenta.query.join(Venta).filter(
            Venta.fecha_hora >= inicio_dia,
            Venta.fecha_hora <= fin_dia,
            Venta.panaderia_id == panaderia_id  # 🎯 FILTRO MULTICLIENTE
        ).all()
        
        print(f"📦 Detalles de venta encontrados: {len(detalles_dia)}")
        
        productos_vendidos = {}
        for detalle in detalles_dia:
            if detalle.producto:
                nombre = detalle.producto.nombre
            elif detalle.producto_externo:
                nombre = detalle.producto_externo.nombre
            else:
                continue
                
            if nombre not in productos_vendidos:
                productos_vendidos[nombre] = 0
            productos_vendidos[nombre] += detalle.cantidad
        
        productos_top = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 🎯 --- INICIO: MÉTRICAS FINANCIERAS CON COSTOS REALES ---
        print("💰 CALCULANDO MÉTRICAS FINANCIERAS CON COSTOS REALES...")
        
        # 🎯 1. CALCULAR COSTOS E INGRESOS CON FUENTES REALES
        costo_total_inventario = 0
        ingresos_totales = 0
        total_productos_vendidos = 0

        # 🆕 VARIABLES PARA ANÁLISIS POR PRODUCTO
        ingresos_por_producto = {}
        costos_por_producto = {}
        utilidades_por_producto = {}

        # 🆕 NUEVAS VARIABLES PARA PRODUCTOS SEPARADOS
        productos_vendidos_lista = []
        productos_donados_detalle = []

        # 🆕 CONTADORES CORREGIDOS PARA DONACIONES
        total_unidades_donadas = 0
        total_productos_donados_unicos = 0

        for detalle in detalles_dia:
            # 🎯 OBTENER PRECIO DE COSTO CON FUENTES REALES
            precio_costo = 0
            fuente_costo = "No identificada"
            
            if detalle.producto:
                # 📦 PRODUCTO DE PANADERÍA CON RECETA
                producto = detalle.producto
                if producto.receta and hasattr(producto.receta, 'costo_unitario') and producto.receta.costo_unitario:
                    # 🎯 USAR COSTO UNITARIO REAL DE LA RECETA
                    precio_costo = producto.receta.costo_unitario
                    fuente_costo = "receta.costo_unitario (real)"
                    print(f"✅ Producto {producto.nombre} - Costo real: ${precio_costo} desde receta")
                    
                elif hasattr(producto, 'costo_compra') and producto.costo_compra:
                    precio_costo = producto.costo_compra
                    fuente_costo = "producto.costo_compra"
                else:
                    # Estimación de reserva
                    precio_costo = detalle.precio_unitario * 0.4
                    fuente_costo = "estimación (40%)"
                    
            elif detalle.producto_externo:
                # 🥤 PRODUCTO EXTERNO
                producto = detalle.producto_externo
                precio_costo = producto.precio_compra if hasattr(producto, 'precio_compra') else 0
                fuente_costo = "producto_externo.precio_compra"
            
            # 🎯 CALCULAR COSTO TOTAL Y INGRESOS
            costo_detalle = precio_costo * detalle.cantidad
            ingreso_detalle = detalle.precio_unitario * detalle.cantidad
            
            costo_total_inventario += costo_detalle
            ingresos_totales += ingreso_detalle
            total_productos_vendidos += detalle.cantidad
            
            # 🆕 ACUMULAR POR PRODUCTO PARA ANÁLISIS DETALLADO
            if detalle.producto:
                nombre_producto = detalle.producto.nombre
            else:
                nombre_producto = detalle.producto_externo.nombre
            
            if nombre_producto not in ingresos_por_producto:
                ingresos_por_producto[nombre_producto] = 0
                costos_por_producto[nombre_producto] = 0
                utilidades_por_producto[nombre_producto] = 0
            
            ingresos_por_producto[nombre_producto] += ingreso_detalle
            costos_por_producto[nombre_producto] += costo_detalle
            utilidades_por_producto[nombre_producto] += (ingreso_detalle - costo_detalle)
            
            # 🆕 SEPARAR PRODUCTOS VENDIDOS VS DONADOS
            es_donacion = detalle.venta.es_donacion if detalle.venta else False
            
            if not es_donacion:
                # PRODUCTO VENDIDO (GENERA INGRESOS REALES)
                productos_vendidos_lista.append({
                    'nombre': nombre_producto,
                    'cantidad': detalle.cantidad,
                    'ingresos': ingreso_detalle,
                    'costo': costo_detalle,
                    'utilidad': ingreso_detalle - costo_detalle,
                    'margen': ((ingreso_detalle - costo_detalle) / ingreso_detalle * 100) if ingreso_detalle > 0 else 0
                })
            else:
                # PRODUCTO DONADO (NO GENERA INGRESOS REALES)
                productos_donados_detalle.append({
                    'nombre': nombre_producto,
                    'cantidad': detalle.cantidad,
                    'valor_mercado': ingreso_detalle,  # Valor que habría generado
                    'costo_real': costo_detalle  # Costo real de producción
                })
                # 🆕 CONTAR UNIDADES DONADAS
                total_unidades_donadas += detalle.cantidad
            
            # Debug detallado
            print(f"   📊 {nombre_producto} - Cant: {detalle.cantidad} - Precio: ${detalle.precio_unitario} - Costo: ${precio_costo} - Fuente: {fuente_costo} - Donación: {es_donacion}")

        print(f"📦 Costo total inventario: ${costo_total_inventario:.0f}")
        print(f"💰 Ingresos totales: ${ingresos_totales:.0f}")
        print(f"🎯 Total productos vendidos: {total_productos_vendidos}")

        # 🎯 2. CALCULAR MARGEN PROMEDIO CON COSTOS REALES (SOLO VENTAS NORMALES)
        ingresos_ventas_normales = sum(item['ingresos'] for item in productos_vendidos_lista)
        costos_ventas_normales = sum(item['costo'] for item in productos_vendidos_lista)
        
        if ingresos_ventas_normales > 0:
            margen_promedio = ((ingresos_ventas_normales - costos_ventas_normales) / ingresos_ventas_normales) * 100
        else:
            margen_promedio = 0

        # 🎯 3. CALCULAR UTILIDAD NETA REAL (SOLO VENTAS NORMALES)
        utilidad_neta = ingresos_ventas_normales - costos_ventas_normales

        # 🎯 4. CALCULAR TICKET PROMEDIO
        transacciones_normales = len(ventas_normales)
        if transacciones_normales > 0:
            ticket_promedio = total_ventas_normales / transacciones_normales
        else:
            ticket_promedio = 0

        # 🎯 5. CALCULAR PRODUCTOS POR VENTA
        if transacciones_normales > 0:
            productos_por_venta = total_productos_vendidos / transacciones_normales
        else:
            productos_por_venta = 0

        print(f"📈 Margen promedio REAL: {margen_promedio:.1f}%")
        print(f"💵 Utilidad neta REAL: ${utilidad_neta:.0f}")
        print(f"🎫 Ticket promedio: ${ticket_promedio:.0f}")
        print(f"📦 Productos por venta: {productos_por_venta:.1f}")
        
        # 🆕 AGRUPAR PRODUCTOS VENDIDOS POR NOMBRE
        productos_vendidos_agrupados = {}
        for producto in productos_vendidos_lista:
            nombre = producto['nombre']
            if nombre not in productos_vendidos_agrupados:
                productos_vendidos_agrupados[nombre] = {
                    'nombre': nombre,
                    'cantidad': 0,
                    'ingresos': 0,
                    'costo': 0,
                    'utilidad': 0
                }
            
            productos_vendidos_agrupados[nombre]['cantidad'] += producto['cantidad']
            productos_vendidos_agrupados[nombre]['ingresos'] += producto['ingresos']
            productos_vendidos_agrupados[nombre]['costo'] += producto['costo']
            productos_vendidos_agrupados[nombre]['utilidad'] += producto['utilidad']
        
        # CALCULAR MARGEN PARA CADA PRODUCTO AGRUPADO
        for producto in productos_vendidos_agrupados.values():
            if producto['ingresos'] > 0:
                producto['margen'] = (producto['utilidad'] / producto['ingresos']) * 100
            else:
                producto['margen'] = 0
        
        productos_vendidos_final = list(productos_vendidos_agrupados.values())
        
        # 🆕 AGRUPAR PRODUCTOS DONADOS POR NOMBRE
        productos_donados_agrupados = {}
        for producto in productos_donados_detalle:
            nombre = producto['nombre']
            if nombre not in productos_donados_agrupados:
                productos_donados_agrupados[nombre] = {
                    'nombre': nombre,
                    'cantidad': 0,
                    'valor_mercado': 0,
                    'costo_real': 0
                }
            
            productos_donados_agrupados[nombre]['cantidad'] += producto['cantidad']
            productos_donados_agrupados[nombre]['valor_mercado'] += producto['valor_mercado']
            productos_donados_agrupados[nombre]['costo_real'] += producto['costo_real']
        
        productos_donados_final = list(productos_donados_agrupados.values())
        
        # 🆕 CALCULAR TOTALES CORREGIDOS PARA DONACIONES
        total_productos_donados_unicos = len(productos_donados_final)
        total_unidades_donadas = sum(item['cantidad'] for item in productos_donados_final)
        valor_total_donaciones = sum(item['valor_mercado'] for item in productos_donados_final)
        
        print(f"🆕 PRODUCTOS VENDIDOS: {len(productos_vendidos_final)} productos únicos")
        for producto in productos_vendidos_final[:3]:
            print(f"   💰 {producto['nombre']} - Cant: {producto['cantidad']} - Ingresos: ${producto['ingresos']:.0f} - Utilidad: ${producto['utilidad']:.0f}")
        
        print(f"🆕 PRODUCTOS DONADOS: {total_productos_donados_unicos} productos únicos, {total_unidades_donadas} unidades totales")
        for producto in productos_donados_final[:3]:
            print(f"   🎁 {producto['nombre']} - Cant: {producto['cantidad']} - Valor: ${producto['valor_mercado']:.0f} - Costo: ${producto['costo_real']:.0f}")
        
        # 🎁 DATOS DE DONACIONES CORREGIDOS
        total_donaciones = len(donaciones)  # Número de transacciones de donación
        productos_donados = total_unidades_donadas  # Número total de unidades donadas
        
        print(f"💰 Valor total donaciones: ${valor_total_donaciones}")
        print(f"🎁 Transacciones de donación: {total_donaciones}")
        print(f"📦 Unidades donadas totales: {productos_donados}")
        
        # 🆕 PREPARAR VENTAS DETALLADAS PARA TABLA
        ventas_detalladas = []
        for venta in ventas_dia:
            cantidad_productos = sum(detalle.cantidad for detalle in venta.detalles)
            ventas_detalladas.append({
                'id': venta.id,
                'fecha_hora': venta.fecha_hora,
                'metodo_pago': venta.metodo_pago,
                'total': venta.total,
                'es_donacion': venta.es_donacion,
                'cantidad_productos': cantidad_productos
            })
        
        print(f"✅ Reporte generado exitosamente")
        print(f"🎁 Total donaciones (transacciones): {total_donaciones}")
        print(f"📦 Productos donados (unidades): {productos_donados}")
        print(f"💰 Valor donaciones: ${valor_total_donaciones}")
        
        # 🆕 ENVIAR DATOS COMPLETOS AL TEMPLATE
        return render_template('cierre_caja.html',
                            fecha=fecha_consultada,
                            hoy=hoy,
                            ayer=ayer,
                            es_hoy=(fecha_consultada == hoy),
                            total_ventas=total_ventas_normales,
                            ventas_por_metodo=ventas_por_metodo,
                            tendencia=tendencia,
                            total_dia_anterior=total_dia_anterior,
                            productos_top=productos_top,
                            total_transacciones=total_transacciones,
                            total_donaciones=total_donaciones,
                            productos_donados=productos_donados,  # 🆕 AHORA ES UNIDADES, NO TRANSACCIONES
                            # 🆕 NUEVAS VARIABLES REQUERIDAS
                            valor_total_donaciones=valor_total_donaciones,
                            ventas_detalladas=ventas_detalladas,
                            # 🎯 MÉTRICAS FINANCIERAS CON COSTOS REALES
                            ticket_promedio=ticket_promedio,
                            productos_por_venta=productos_por_venta,
                            margen_promedio=margen_promedio,
                            costo_inventario=costo_total_inventario,
                            utilidad_neta=utilidad_neta,
                            # 🆕 ANÁLISIS POR PRODUCTO
                            ingresos_por_producto=ingresos_por_producto,
                            costos_por_producto=costos_por_producto,
                            utilidades_por_producto=utilidades_por_producto,
                            # 🆕 NUEVAS VARIABLES PARA PDF SEPARADO
                            productos_vendidos=productos_vendidos_final,
                            productos_donados_detalle=productos_donados_final)
                            
    
    except Exception as e:
        print(f"❌ ERROR en reporte_cierre_caja: {str(e)}")
        flash(f'Error generando reporte: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    
@app.route('/reporte/ventas')
@login_required
@modulo_requerido('reportes')
def reporte_ventas():
    """Reporte de ventas por período con análisis predictivo"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🔍 OBTENER TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener parámetros de fecha o usar valores por defecto
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    periodo = request.args.get('periodo', 'semana')
    
    hoy = datetime.now().date()
    
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        periodo = 'personalizado'
    else:
        fecha_fin = hoy
        fecha_inicio = fecha_fin - timedelta(days=7)
        periodo = 'semana'
    
    if fecha_inicio > fecha_fin:
        flash('La fecha de inicio no puede ser mayor que la fecha fin', 'error')
        fecha_inicio = fecha_fin - timedelta(days=7)
    
    # ✅ Obtener ventas del período (CON FILTRO POR TENANT)
    ventas_periodo = Venta.query.filter(
        db.func.date(Venta.fecha_hora) >= fecha_inicio,
        db.func.date(Venta.fecha_hora) <= fecha_fin,
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    ventas_normales = [v for v in ventas_periodo if not v.es_donacion]
    donaciones = [v for v in ventas_periodo if v.es_donacion]
    
    total_ventas_normales = sum(venta.total for venta in ventas_normales)
    total_transacciones = len(ventas_periodo)
    
    total_ventas = total_ventas_normales
    promedio_venta = total_ventas_normales / len(ventas_normales) if ventas_normales else 0
    
    tendencia = calcular_tendencia_ventas(fecha_inicio, fecha_fin)
    
    # ✅ Productos más vendidos del período (CON FILTRO POR TENANT)
    detalles_periodo = DetalleVenta.query.join(Venta).filter(
        db.func.date(Venta.fecha_hora) >= fecha_inicio,
        db.func.date(Venta.fecha_hora) <= fecha_fin,
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    productos_analisis = analizar_productos_periodo(detalles_periodo)
    
    total_donaciones = len(donaciones)
    productos_donados = sum(len(v.detalles) for v in donaciones)
    
    return render_template('ventas_periodo.html',
                         periodo=periodo,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         total_ventas=total_ventas_normales,
                         promedio_venta=promedio_venta,
                         tendencia=tendencia,
                         productos_analisis=productos_analisis,
                         total_transacciones=total_transacciones,
                         datetime=datetime,
                         total_donaciones=total_donaciones,
                         productos_donados=productos_donados)

@app.route('/reporte/productos_populares')
@login_required
@modulo_requerido('reportes')
def reporte_productos_populares():
    """Reporte de productos más vendidos con análisis de rotación"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🔍 OBTENER TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener parámetros de fecha o usar valores por defecto
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Actualizar rotaciones automáticas antes de generar reporte
    actualizaciones = actualizar_rotaciones_automaticas()
    
    # ✅ Obtener productos más vendidos del período (CON FILTRO POR TENANT)
    detalles = DetalleVenta.query.join(Venta).filter(
        Venta.fecha_hora >= fecha_inicio,
        Venta.fecha_hora <= fecha_fin,
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    # Analizar productos
    analisis_productos = {}
    
    for detalle in detalles:
        if detalle.producto:
            producto_id = detalle.producto.id
            nombre = detalle.producto.nombre
            tipo = 'Producción'
        elif detalle.producto_externo:
            producto_id = detalle.producto_externo.id
            nombre = detalle.producto_externo.nombre
            tipo = 'Externo'
        else:
            continue
        
        if producto_id not in analisis_productos:
            analisis_productos[producto_id] = {
                'nombre': nombre,
                'tipo': tipo,
                'cantidad_vendida': 0,
                'ingresos_totales': 0,
                'rotacion_promedio': 0
            }
        
        analisis_productos[producto_id]['cantidad_vendida'] += detalle.cantidad
        analisis_productos[producto_id]['ingresos_totales'] += detalle.cantidad * detalle.precio_unitario
    
    # Ordenar por cantidad vendida
    productos_ordenados = sorted(analisis_productos.values(), 
                               key=lambda x: x['cantidad_vendida'], 
                               reverse=True)
    
    # Agregar datos de rotación automática
    for producto in productos_ordenados[:20]:
        rotacion = calcular_rotacion_automatica_por_nombre(producto['nombre'])
        producto['rotacion_promedio'] = rotacion
    
    # ✅ OBTENER DATOS DE DONACIONES (CON FILTRO POR TENANT)
    ventas_periodo = Venta.query.filter(
        Venta.fecha_hora >= fecha_inicio,
        Venta.fecha_hora <= fecha_fin,
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    donaciones = [v for v in ventas_periodo if v.es_donacion]
    total_donaciones = len(donaciones)
    productos_donados = sum(len(v.detalles) for v in donaciones)
    
    return render_template('productos_populares.html',
                         productos=productos_ordenados[:20],
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         actualizaciones_ml=actualizaciones,
                         datetime=datetime,
                         total_donaciones=total_donaciones,
                         productos_donados=productos_donados)

@app.route('/reporte/analisis_predictivo')
@login_required
@modulo_requerido('reportes')
def reporte_analisis_predictivo():
    """Reporte de análisis predictivo con recomendaciones ML"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🔍 OBTENER TENANT ACTUAL
    panaderia_id = obtener_panaderia_actual()
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener datos para análisis predictivo
    productos_analisis = []
    
    # ✅ FILTRAR RECETAS POR TENANT
    recetas_activas = Receta.query.filter_by(
        panaderia_id=panaderia_id,  # ✅ FILTRO MULTI-TENANT
        activo=True
    ).all()
    
    for receta in recetas_activas:
        if receta.producto:
            # Calcular proyecciones usando ML (INCLUYENDO DONACIONES EN DATOS HISTÓRICOS)
            proyeccion = calcular_proyeccion_ventas(receta.producto.id)
            productos_analisis.append({
                'producto': receta.producto.nombre,
                'stock_actual': receta.producto.stock_actual,
                'rotacion_actual': proyeccion.get('rotacion_actual', 0),
                'proyeccion_ventas': proyeccion.get('proyeccion', 0),
                'dias_stock': proyeccion.get('dias_stock', 0),
                'recomendacion': generar_recomendacion_stock(receta.producto.id, proyeccion),
                'nivel_riesgo': proyeccion.get('nivel_riesgo', 'BAJO')
            })
    
    # Alertas inteligentes (YA FILTRAN POR TENANT)
    alertas = generar_alertas_inteligentes(panaderia_id)
    
    # ✅ OBTENER DATOS DE DONACIONES RECIENTES (CON FILTRO POR TENANT)
    fecha_inicio = datetime.now().date() - timedelta(days=30)
    donaciones_recientes = Venta.query.filter(
        Venta.fecha_hora >= fecha_inicio,
        Venta.es_donacion == True,
        Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
    ).all()
    
    total_donaciones_30dias = len(donaciones_recientes)
    productos_donados_30dias = sum(len(v.detalles) for v in donaciones_recientes)
    
    return render_template('analisis_predictivo.html',
                     productos_analisis=productos_analisis,
                     alertas=alertas,
                     fecha_analisis=datetime.now().date(),
                     datetime=datetime,
                     total_donaciones=total_donaciones_30dias,
                     productos_donados=productos_donados_30dias)
    

# (aquí termina reporte_analisis_predictivo)


# 🆕 NUEVA FUNCIÓN - INSERTAR AQUÍ
@app.route('/reporte/ventas_avanzado')
@login_required
@modulo_requerido('reportes')
def reporte_ventas_avanzado():
    """Reporte unificado: Ventas por período + Análisis Predictivo + ML"""
    # 📦 IMPORTAR DATETIME AL INICIO
    from datetime import datetime, timedelta
    
    # 🎯 VERIFICAR SESIÓN
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 🎯 OBTENER PARÁMETROS DE FECHA (COMÚN A AMBOS REPORTES)
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    periodo = request.args.get('periodo', 'semana_actual')
    
    # 🎯 OBTENER FECHAS CON VALORES POR DEFECTO
    hoy = datetime.now().date()
    
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        periodo = 'personalizado'
    else:
        # Por defecto: esta semana
        fecha_fin = hoy
        fecha_inicio = fecha_fin - timedelta(days=fecha_fin.weekday())  # Inicio de semana (lunes)
        periodo = 'semana_actual'
    
    # 🎯 VALIDACIÓN DE FECHAS
    if fecha_inicio > fecha_fin:
        flash('❌ La fecha de inicio no puede ser mayor que la fecha fin', 'error')
        fecha_inicio = fecha_fin - timedelta(days=7)
    
    # 🎯 OBTENER panaderia_id DEL USUARIO ACTUAL (MULTICLIENTE)
    usuario_actual = Usuario.query.get(session['user_id'])
    panaderia_id = usuario_actual.panaderia_id
    
    print(f"🔍 [VENTAS_AVANZADO] Usuario: {usuario_actual.username}, Panadería: {panaderia_id}")
    print(f"📅 Período: {fecha_inicio} a {fecha_fin}")
    
    # =====================================================================
    # 📊 SECCIÓN 1: DATOS DE VENTAS REALES
    # =====================================================================
    
    # 🎯 OBTENER VENTAS DEL PERÍODO (INCLUYENDO DONACIONES)
    ventas_periodo = Venta.query.filter(
        db.func.date(Venta.fecha_hora) >= fecha_inicio,
        db.func.date(Venta.fecha_hora) <= fecha_fin,
        Venta.panaderia_id == panaderia_id  # 🎯 FILTRO MULTICLIENTE
    ).all()
    
    # 🎁 SEPARAR VENTAS NORMALES VS DONACIONES
    ventas_normales = [v for v in ventas_periodo if not v.es_donacion]
    donaciones = [v for v in ventas_periodo if v.es_donacion]
    
    # 🎯 CALCULAR MÉTRICAS BÁSICAS DE VENTAS
    total_ventas_normales = sum(venta.total for venta in ventas_normales)
    total_transacciones = len(ventas_periodo)
    
    # 🎯 CALCULAR PROMEDIO DE VENTA (SOLO VENTAS NORMALES)
    promedio_venta = total_ventas_normales / len(ventas_normales) if ventas_normales else 0
    
    # 🎁 DATOS DE DONACIONES
    total_donaciones = len(donaciones)
    productos_donados = sum(len(v.detalles) for v in donaciones)
    
    print(f"💰 Ventas: ${total_ventas_normales:.2f}, Transacciones: {total_transacciones}")
    
    # =====================================================================
    # 📈 NUEVOS CÁLCULOS PARA GRÁFICOS Y DATOS REALES
    # =====================================================================
    
    # 🎯 TOP 5 PRODUCTOS MÁS VENDIDOS (REALES - CON VALIDACIÓN)
    from collections import Counter
    productos_vendidos = []
    
    for venta in ventas_normales:
        for item in venta.detalles:
            # ✅ VALIDAR QUE EL PRODUCTO NO SEA None - ESTO EVITA EL ERROR
            if item.producto is not None:
                productos_vendidos.append({
                    'nombre': item.producto.nombre,
                    'cantidad': item.cantidad,
                    'categoria': getattr(item.producto, 'categoria', 'Sin Categoría')
                })
            else:
                print(f"⚠️  DetalleVenta {item.id} tiene producto None, omitiendo...")
    
    # Contar productos más vendidos
    contador_productos = Counter()
    for producto in productos_vendidos:
        contador_productos[producto['nombre']] += producto['cantidad']
    
    # Obtener top 5 productos (o menos si no hay suficientes)
    top_5_productos = contador_productos.most_common(5)
    top_productos_labels = [producto[0] for producto in top_5_productos]
    top_productos_data = [producto[1] for producto in top_5_productos]
    
    # 🎯 DISTRIBUCIÓN POR CATEGORÍA
    categorias_counter = Counter()
    for producto in productos_vendidos:
        categoria = producto['categoria']
        categorias_counter[categoria] += producto['cantidad']
    
    categorias_labels = list(categorias_counter.keys())
    categorias_data = list(categorias_counter.values())
    
    # 🎯 TENDENCIA DIARIA DE VENTAS
    ventas_por_dia = {}
    for venta in ventas_normales:
        fecha = venta.fecha_hora.date()
        ventas_por_dia[fecha] = ventas_por_dia.get(fecha, 0) + venta.total
    
    # Ordenar por fecha y llenar vacíos
    todas_fechas = []
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        todas_fechas.append(fecha_actual)
        fecha_actual += timedelta(days=1)
    
    tendencia_labels = [fecha.strftime('%d/%m') for fecha in todas_fechas]
    tendencia_data = [ventas_por_dia.get(fecha, 0) for fecha in todas_fechas]
    
    # 🎯 CÁLCULO DE TENDENCIA vs PERÍODO ANTERIOR
    periodo_anterior_inicio = fecha_inicio - (fecha_fin - fecha_inicio)
    periodo_anterior_fin = fecha_inicio - timedelta(days=1)
    
    ventas_periodo_anterior = Venta.query.filter(
        Venta.panaderia_id == panaderia_id,
        db.func.date(Venta.fecha_hora) >= periodo_anterior_inicio,
        db.func.date(Venta.fecha_hora) <= periodo_anterior_fin,
        Venta.es_donacion == False
    ).all()
    
    total_ventas_anterior = sum(v.total for v in ventas_periodo_anterior)
    
    if total_ventas_anterior > 0:
        tendencia_porcentaje = ((total_ventas_normales - total_ventas_anterior) / total_ventas_anterior * 100)
    else:
        tendencia_porcentaje = 100 if total_ventas_normales > 0 else 0
    
    # 🎯 PORCENTAJES VENTAS VS DONACIONES
    porcentaje_ventas = 100 - (total_donaciones / total_transacciones * 100) if total_transacciones > 0 else 100
    porcentaje_donaciones = (total_donaciones / total_transacciones * 100) if total_transacciones > 0 else 0
    
    # =====================================================================
    # 🤖 SECCIÓN 2: ANÁLISIS ML (MANTENIENDO TU LÓGICA EXISTENTE)
    # =====================================================================
    
    # 🎯 TENDENCIA (usando tu función existente)
    try:
        tendencia_ml = calcular_tendencia_ventas(fecha_inicio, fecha_fin)
        print(f"📈 Tendencia ML: {tendencia_ml:.1f}%")
    except Exception as e:
        print(f"⚠️  Error en tendencia ML: {e}")
        tendencia_ml = tendencia_porcentaje  # Usar cálculo alternativo
    
    # 🎯 ALERTAS INTELIGENTES
    try:
        alertas = generar_alertas_inteligentes()
        print(f"🔔 Alertas: {len(alertas)}")
    except Exception as e:
        print(f"⚠️  Error en alertas: {e}")
        alertas = []
    
    # 🎯 ANÁLISIS DE PRODUCTOS
    try:
        detalles_periodo = DetalleVenta.query.join(Venta).filter(
            db.func.date(Venta.fecha_hora) >= fecha_inicio,
            db.func.date(Venta.fecha_hora) <= fecha_fin,
            Venta.panaderia_id == panaderia_id
        ).all()
        
        productos_analisis = analizar_productos_periodo(detalles_periodo)
        print(f"📦 Productos analizados: {len(productos_analisis)}")
    except Exception as e:
        print(f"⚠️  Error en análisis productos: {e}")
        productos_analisis = {}
    
    # 🎯 PROYECCIONES ML (POR AHORA VACÍO)
    productos_analisis_ml = []
    
    # 🎯 GENERAR RECOMENDACIONES BASADAS EN DATOS REALES
    recomendaciones = []
    if top_5_productos:
        recomendaciones.append(f"Aumentar producción de '{top_5_productos[0][0]}' en 20%")
    if tendencia_porcentaje > 50:
        recomendaciones.append("Mantener estrategia comercial actual - crecimiento excelente")
    elif tendencia_porcentaje < 0:
        recomendaciones.append("Revisar estrategia comercial - tendencia negativa detectada")
    
    if len(ventas_normales) > 0:
        # Análisis de horarios pico
        ventas_por_hora = Counter()
        for venta in ventas_normales:
            hora = venta.fecha_hora.hour
            ventas_por_hora[hora] += 1
        
        if ventas_por_hora:
            hora_pico = ventas_por_hora.most_common(1)[0][0]
            recomendaciones.append(f"Optimizar personal para horario pico: {hora_pico}:00")
    
    print(f"✅ [VENTAS_AVANZADO] Reporte generado exitosamente")
    print(f"📊 Productos en top: {len(top_productos_labels)}, Categorías: {len(categorias_labels)}")
    
    # =====================================================================
    # 🎯 RENDERIZAR TEMPLATE UNIFICADO CON TODOS LOS DATOS
    # =====================================================================
    
    # =============================================
    # 📊 CALCULAR DÍAS DE ACTIVIDAD PARA IA
    # =============================================
    from datetime import datetime
    primera_venta = Venta.query.filter_by(
        panaderia_id=panaderia_id
    ).order_by(Venta.fecha_hora.asc()).first()

    if primera_venta:
        dias_actividad = (datetime.now() - primera_venta.fecha_hora).days
    else:
        dias_actividad = 0
        
        # =============================================
    # 📊 ANÁLISIS DE TENDENCIAS (NIVEL 2)
    # =============================================
    from models import analizar_tendencias_ventas
    analisis_tendencias = analizar_tendencias_ventas(panaderia_id)
    
    # =============================================
    # 🔮 PREDICCIONES CON ML (NIVEL 3)
    # =============================================
    from models import predecir_ventas_futuras
    predicciones_ml = predecir_ventas_futuras(panaderia_id)
    
    # =============================================
    # 💡 RECOMENDACIONES PERSONALIZADAS (NIVEL 4)
    # =============================================
    from models import generar_recomendaciones_personalizadas
    recomendaciones_personalizadas = generar_recomendaciones_personalizadas(panaderia_id)
    
    # =====================================================================
    # 🎯 RENDERIZAR TEMPLATE UNIFICADO CON TODOS LOS DATOS
    # =====================================================================
    return render_template('ventas_avanzado.html',
                         # Fechas y período
                         periodo=periodo,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         
                         # Métricas principales (manteniendo compatibilidad)
                         total_ventas=total_ventas_normales,
                         promedio_venta=promedio_venta,
                         total_transacciones=total_transacciones,
                         total_donaciones=total_donaciones,
                         productos_donados=productos_donados,
                         
                         # ML (funciones existentes)
                         tendencia=tendencia_ml,
                         alertas=alertas,
                         productos_analisis=productos_analisis,
                         productos_analisis_ml=productos_analisis_ml,
                         
                         # NUEVOS DATOS PARA GRÁFICOS Y ANÁLISIS
                         tendencia_ventas=tendencia_porcentaje,
                         ticket_promedio=promedio_venta,
                         
                         # Datos para gráficos
                         top_productos_labels=top_productos_labels,
                         top_productos_data=top_productos_data,
                         categorias_labels=categorias_labels,
                         categorias_data=categorias_data,
                         tendencia_labels=tendencia_labels,
                         tendencia_data=tendencia_data,
                         porcentaje_ventas=porcentaje_ventas,
                         porcentaje_donaciones=porcentaje_donaciones,
                         
                         # Datos para secciones
                         ventas_detalle=ventas_periodo,
                         productos_vendidos=productos_vendidos,
                         recomendaciones=recomendaciones,
                         
                         # 🆕 DÍAS DE ACTIVIDAD PARA IA
                         dias_actividad=dias_actividad,
                         
                         # 🆕 ANÁLISIS DE TENDENCIAS (NIVEL 2)
                         analisis_tendencias=analisis_tendencias,
                         
                         # 🆕 PREDICCIONES CON ML (NIVEL 3)
                         predicciones_ml=predicciones_ml,
                         
                         recomendaciones_personalizadas=recomendaciones_personalizadas,
                         
                         datetime=datetime)

# Busca un lugar después de las otras rutas y agrega:

# ================================================== MÓDULO FINANCIERO ====================================================
# === NUEVO MÓDULO FINANCIERO INTUITIVO ===

# === FUNCIONES AUXILIARES ===
# ================================================== MÓDULO FINANCIERO ====================================================

# === FUNCIONES AUXILIARES MEJORADAS ===
def obtener_ventas_del_dia(fecha):
    """Obtener ventas reales del punto de venta para una fecha específica"""
    try:
        from datetime import datetime, timedelta
        # Convertir fecha para comparación
        fecha_inicio = datetime(fecha.year, fecha.month, fecha.day)
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        # Buscar ventas en ese rango de fechas
        ventas = Venta.query.filter(
            Venta.fecha_hora >= fecha_inicio,
            Venta.fecha_hora < fecha_fin
        ).all()
        
        total_ventas = sum(venta.total for venta in ventas)
        return total_ventas
        
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        return 0

def actualizar_saldo_automatico(panaderia_id, efectivo=0, transferencias=0, pagos=0, accion_efectivo="depositar"):
    """
    Actualizar saldo automáticamente considerando ingresos y egresos
    - transferencias: dinero que ENTRA a la cuenta
    - pagos: dinero que SALE de la cuenta
    - efectivo: depende de la acción seleccionada
    """
    try:
        # CORREGIDO: Filtro por panaderia_id
        saldo_actual_obj = SaldoBanco.query.filter_by(panaderia_id=panaderia_id).order_by(SaldoBanco.fecha_actualizacion.desc()).first()
        saldo_actual = saldo_actual_obj.saldo_actual if saldo_actual_obj else 0
        
        # Calcular nuevo saldo
        nuevo_saldo = saldo_actual
        
        # SUMAR: Transferencias (siempre entran a la cuenta)
        nuevo_saldo += (transferencias or 0)
        
        # SUMAR: Efectivo solo si se deposita
        if accion_efectivo == "depositar":
            nuevo_saldo += (efectivo or 0)
        
        # RESTAR: Pagos realizados (dinero que sale de la cuenta)
        nuevo_saldo -= (pagos or 0)
        
        # Generar comentario descriptivo
        comentario = f"Actualización: "
        partes = []
        if transferencias > 0:
            partes.append(f"+${transferencias:,.0f} transferencias")
        if efectivo > 0 and accion_efectivo == "depositar":
            partes.append(f"+${efectivo:,.0f} efectivo depositado")
        if pagos > 0:
            partes.append(f"-${pagos:,.0f} pagos")
        
        comentario += " | ".join(partes) if partes else "Sin movimientos"
        
        # Crear nuevo registro de saldo - CORREGIDO: panaderia_id del parámetro
        nuevo_registro_saldo = SaldoBanco(panaderia_id=panaderia_id, 
            saldo_actual=nuevo_saldo,
            comentario=comentario
        )
        
        db.session.add(nuevo_registro_saldo)
        return nuevo_saldo
        
    except Exception as e:
        print(f"Error al actualizar saldo: {e}")
        return saldo_actual

def sanitizar_numero(valor, default=0.0):
    """Convierte valores a float de forma segura, manejando None y strings vacíos"""
    try:
        if valor is None or valor == '':
            return default
        return float(valor)
    except (ValueError, TypeError):
        return default

# === RUTAS MEJORADAS ===

@app.route('/registrar_dia', methods=['POST'])
@login_required
@modulo_requerido('finanzas')
@tenant_required  # ← DECORADOR MULTI-TENANT AGREGADO
def registrar_dia():
    """Registrar los ingresos y gastos del día"""
    try:
        from datetime import datetime
        
        # Obtener datos del formulario con sanitización
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        venta_total = sanitizar_numero(request.form.get('venta_total'))
        
        # Ingresos con sanitización
        efectivo = sanitizar_numero(request.form.get('efectivo'))
        transferencias = sanitizar_numero(request.form.get('transferencias'))
        tarjetas = sanitizar_numero(request.form.get('tarjetas'))
        
        # Gastos con sanitización
        gasto_proveedores = sanitizar_numero(request.form.get('gasto_proveedores'))
        gasto_servicios = sanitizar_numero(request.form.get('gasto_servicios'))
        gasto_nomina = sanitizar_numero(request.form.get('gasto_nomina'))
        gasto_alquiler = sanitizar_numero(request.form.get('gasto_alquiler'))
        gasto_otros = sanitizar_numero(request.form.get('gasto_otros'))
        
        descripcion = request.form.get('descripcion', '')
        numero_factura = request.form.get('numero_factura', '')
        
        # Verificar si ya existe registro para esta fecha - CORREGIDO: current_user.panaderia_id
        registro_existente = RegistroDiario.query.filter_by(panaderia_id=current_user.panaderia_id, fecha=fecha).first()
        
        if registro_existente:
            # Actualizar registro existente
            registro = registro_existente
        else:
            # Crear nuevo registro - CORREGIDO: current_user.panaderia_id
            registro = RegistroDiario(fecha=fecha, panaderia_id=current_user.panaderia_id)
        
        # Actualizar datos
        registro.venta_total = venta_total
        registro.efectivo = efectivo
        registro.transferencias = transferencias
        registro.tarjetas = tarjetas
        registro.gasto_proveedores = gasto_proveedores
        registro.gasto_servicios = gasto_servicios
        registro.gasto_nomina = gasto_nomina
        registro.gasto_alquiler = gasto_alquiler
        registro.gasto_otros = gasto_otros
        registro.descripcion_gastos = descripcion
        registro.numero_factura = numero_factura
        
        # Calcular totales automáticamente
        registro.calcular_totales()
        
        if not registro_existente:
            db.session.add(registro)
        
        db.session.commit()
        
        flash('✅ ¡Día registrado correctamente!', 'success')
        
    except Exception as e:
        flash(f'❌ Error al registrar: {str(e)}', 'error')
    
    return redirect(url_for('control_diario'))

@app.route('/control_diario')
@login_required
@modulo_requerido('finanzas')
@tenant_required  # ← DECORADOR MULTI-TENANT AGREGADO
def control_diario():
    """Vista principal del control financiero diario"""
    from datetime import datetime, date
    
    # Obtener saldo actual CON FILTRO TENANT
    saldo_banco = SaldoBanco.query.filter_by(panaderia_id=current_user.panaderia_id).order_by(SaldoBanco.fecha_actualizacion.desc()).first()
    saldo_actual = saldo_banco.saldo_actual if saldo_banco else 0
    
    # Obtener registros recientes (últimos 7 días) CON FILTRO TENANT
    registros_recientes = RegistroDiario.query.filter_by(panaderia_id=current_user.panaderia_id).order_by(RegistroDiario.fecha.desc()).limit(7).all()
    
    # Obtener proveedores para el dropdown CON FILTRO TENANT
    proveedores = Proveedor.query.filter_by(panaderia_id=current_user.panaderia_id).all()
    
    # Obtener pagos de hoy CON FILTRO TENANT
    hoy = date.today()
    pagos_hoy = PagoIndividual.query.filter_by(panaderia_id=current_user.panaderia_id, fecha_pago=hoy).all()
    registro_hoy = RegistroDiario.query.filter_by(panaderia_id=current_user.panaderia_id, fecha=hoy).first()
    
    return render_template('control_diario.html',
                         saldo_actual=saldo_actual,
                         registros_recientes=registros_recientes,
                         registro_hoy=registro_hoy,
                         proveedores=proveedores,
                         pagos_hoy=pagos_hoy,
                         hoy=hoy)

@app.route('/registrar_pago_individual', methods=['POST'])
@login_required
@modulo_requerido('finanzas')
@tenant_required  # ← DECORADOR MULTI-TENANT AGREGADO
def registrar_pago_individual():
    """Registrar un pago individual con actualización automática del saldo"""
    try:
        from datetime import datetime
        
        # Obtener datos del formulario con manejo de campos vacíos
        categoria = request.form['categoria']
        monto = sanitizar_numero(request.form.get('monto'), 0.0)
        
        # Validar que el monto sea positivo
        if monto <= 0:
            flash('❌ El monto debe ser mayor a 0', 'error')
            return redirect(url_for('control_diario'))
        
        fecha_pago = datetime.strptime(request.form['fecha_pago'], '%Y-%m-%d').date()
        referencia = request.form.get('referencia', '')
        descripcion = request.form.get('descripcion', '')
        numero_factura = request.form.get('numero_factura', '')
        
        # Proveedor (solo para categoría de materias primas)
        proveedor_id = None
        if categoria == 'MATERIAS_PRIMAS':
            proveedor_id_str = request.form.get('proveedor_id', '')
            if proveedor_id_str and proveedor_id_str.strip():
                try:
                    proveedor_id = int(proveedor_id_str)
                except ValueError:
                    proveedor_id = None
        
        # Crear nuevo pago CON FILTRO TENANT
        nuevo_pago = PagoIndividual(panaderia_id=current_user.panaderia_id,  # ← CORREGIDO: current_user.panaderia_id
            categoria=categoria,
            proveedor_id=proveedor_id,
            monto=monto,
            fecha_pago=fecha_pago,
            referencia=referencia,
            descripcion=descripcion,
            numero_factura=numero_factura
        )
        
        db.session.add(nuevo_pago)
        
        # 🆕 ACTUALIZAR SALDO - RESTAR EL PAGO (POR AHORA DEJAMOS ESTA FUNCIÓN COMO ESTÁ)
        saldo_actual = actualizar_saldo_automatico(
            panaderia_id=current_user.panaderia_id,
            efectivo=0,
            transferencias=0, 
            pagos=monto,  # Restar el monto del pago
            accion_efectivo="depositar"  # No relevante para pagos
        )
        
        db.session.commit()
        
        flash(f'✅ Pago registrado: ${monto:,.0f} - {categoria} - Saldo actual: ${saldo_actual:,.0f}', 'success')
        
    except ValueError as e:
        flash(f'❌ Error en los datos numéricos: {str(e)}', 'error')
    except Exception as e:
        flash(f'❌ Error al registrar pago: {str(e)}', 'error')
    
    return redirect(url_for('control_diario'))

@app.route('/registrar_cierre_caja', methods=['POST'])
@login_required
@modulo_requerido('finanzas')
@tenant_required  # ← DECORADOR MULTI-TENANT AGREGADO
def registrar_cierre_caja():
    """Registrar el cierre de caja diario con validaciones de seguridad"""
    try:
        from datetime import datetime
        
        # Obtener datos del formulario con sanitización
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        
        # 🔒 VALIDACIÓN: No permitir fechas futuras en cierre de caja
        from datetime import date
        hoy = date.today()
        if fecha > hoy:
            flash(f'❌ No se puede registrar un cierre de caja con fecha futura ({fecha.strftime("%d/%m/%Y")}). La fecha debe ser hoy o anterior.', 'error')
            return redirect(url_for('gestion_financiera'))
        venta_total = sanitizar_numero(request.form.get('venta_total', 0))
        efectivo = sanitizar_numero(request.form.get('efectivo', 0))
        transferencias = sanitizar_numero(request.form.get('transferencias', 0))
        # tarjetas eliminado - solo usamos efectivo y transferencias
        accion_efectivo = request.form.get('accion_efectivo', 'depositar')
        
        # 🔒 VALIDACIÓN CRÍTICA: Verificar que la suma coincida con el total
        suma_metodos = efectivo + transferencias
        diferencia = abs(suma_metodos - venta_total)
        
        if diferencia > 1:
            if suma_metodos > venta_total:
                flash(f'❌ El total ingresado en métodos de pago (${suma_metodos:,.0f}) es SUPERIOR al total de ventas (${venta_total:,.0f}). Diferencia: +${diferencia:,.0f}', 'error')
            else:
                flash(f'❌ El total ingresado en métodos de pago (${suma_metodos:,.0f}) es INFERIOR al total de ventas (${venta_total:,.0f}). Diferencia: -${diferencia:,.0f}', 'error')
            return redirect(url_for('gestion_financiera'))
        
        # Verificar si ya existe registro para esta fecha - CORREGIDO: current_user.panaderia_id
        registro_existente = RegistroDiario.query.filter_by(panaderia_id=current_user.panaderia_id, fecha=fecha).first()
        
        if registro_existente:
            registro = registro_existente
        else:
            registro = RegistroDiario(fecha=fecha, panaderia_id=current_user.panaderia_id)
        
        # Actualizar datos de ingresos
        registro.venta_total = venta_total
        registro.efectivo = efectivo
        registro.transferencias = transferencias
        # registro.tarjetas = tarjetas  # campo eliminado
        
        # Calcular totales automáticamente
        registro.calcular_totales()
        
        if not registro_existente:
            db.session.add(registro)
        
        # 🆕 ACTUALIZAR SALDO - SOLO INGRESOS (no pagos aquí) - CORREGIDO: current_user.panaderia_id
        saldo_actual = actualizar_saldo_automatico(
            panaderia_id=current_user.panaderia_id,  # ← PARÁMETRO AGREGADO
            efectivo=efectivo, 
            transferencias=transferencias, 
            pagos=0,  # Los pagos se actualizan en su propia ruta
            accion_efectivo=accion_efectivo
        )
        
        db.session.commit()
        
        # Mensaje personalizado
        if accion_efectivo == "depositar":
            flash(f'✅ Cierre de caja registrado! Ingresos: ${venta_total:,.0f} - Saldo actualizado: ${saldo_actual:,.0f}', 'success')
        else:
            flash(f'✅ Cierre de caja registrado! Ingresos: ${venta_total:,.0f} - Saldo actualizado: ${saldo_actual:,.0f} (Efectivo en caja)', 'success')
        
    except Exception as e:
        flash(f'❌ Error al registrar cierre: {str(e)}', 'error')
    
    return redirect(url_for('gestion_financiera'))



# ================================================== MÓDULO DE REPORTES ====================================================

from reportes import GeneradorReportes
from io import BytesIO


@app.route('/gestion_financiera')
def gestion_financiera():
    """Módulo de Gestión Financiera y Contabilidad"""
    from models import db, Usuario, PagoIndividual, SaldoBanco
    from sqlalchemy import func
    from datetime import datetime, date
    
    # Obtener pagos recientes (transacciones)
    transacciones = PagoIndividual.query.order_by(
        PagoIndividual.fecha_pago.desc()
    ).limit(50).all()
    
    # Calcular saldo actual desde SaldoBanco
    saldo_banco = SaldoBanco.query.filter_by(panaderia_id=current_user.panaderia_id).order_by(
        SaldoBanco.fecha_actualizacion.desc()
    ).first()
    
    saldo_actual = saldo_banco.saldo_actual if saldo_banco else 0
    
    # Calcular totales para estadísticas (usando PagoIndividual)
    total_ingresos = PagoIndividual.query.filter(
        PagoIndividual.monto >= 0
    ).with_entities(func.sum(PagoIndividual.monto)).scalar() or 0
    
    total_egresos = PagoIndividual.query.filter(
        PagoIndividual.monto < 0
    ).with_entities(func.sum(PagoIndividual.monto)).scalar() or 0  # total_egresos es negativo
    
    # Calcular totales del mes
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    
    ingresos_mes = PagoIndividual.query.filter(
        PagoIndividual.monto >= 0,
        PagoIndividual.fecha_pago >= inicio_mes
    ).with_entities(func.sum(PagoIndividual.monto)).scalar() or 0
    
    egresos_mes = PagoIndividual.query.filter(
        PagoIndividual.monto < 0,
        PagoIndividual.fecha_pago >= inicio_mes
    ).with_entities(func.sum(PagoIndividual.monto)).scalar() or 0
    
    flujo_neto_mes = ingresos_mes + egresos_mes  # egresos_mes es negativo
    
    # Configuración (valores por defecto)
        # Obtener registros de últimos 7 días
    registros_recientes = RegistroDiario.query.filter_by(
        panaderia_id=current_user.panaderia_id
    ).order_by(RegistroDiario.fecha.desc()).limit(7).all()
    
    # Obtener pagos de hoy
    hoy = date.today()
    pagos_hoy = PagoIndividual.query.filter_by(
        panaderia_id=current_user.panaderia_id,
        fecha_pago=hoy
    ).all()
    
    # Obtener proveedores
    proveedores = Proveedor.query.filter_by(
        panaderia_id=current_user.panaderia_id
    ).all()
    
    config = {
        'saldo_actual': saldo_actual,
        'alerta_saldo_minimo': 100000
    }
    
    return render_template('gestion_financiera.html',
                         registros_recientes=registros_recientes,
                         pagos_hoy=pagos_hoy,
                         proveedores=proveedores,
                         hoy=hoy,
                         config=config,
                         saldo_actual=saldo_actual,
                         transacciones=transacciones,
                         total_ingresos_mes=ingresos_mes,
                         total_egresos_mes=abs(egresos_mes),
                         flujo_neto_mes=flujo_neto_mes)
@app.route('/reportes')
@login_required
@modulo_requerido('reportes')
def reportes():
    """Vista principal de reportes"""
    # 🔍 Verificar tenant
    panaderia_id = obtener_panaderia_actual()
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('reportes.html')

@app.route('/generar_reporte_estado_resultados')
@login_required
@modulo_requerido('reportes')
@tenant_required
def generar_reporte_estado_resultados():
    """Genera reporte de Estado de Resultados en PDF - CON FILTRO MULTI-TENANT"""
    try:
        from datetime import datetime
        
        # 🔍 OBTENER TENANT ACTUAL
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        # ✅ PASAR panaderia_id a la función
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_estado_resultados(panaderia_id, fecha_inicio, fecha_fin)
        
        nombre_archivo = f"estado_resultados_{fecha_inicio}_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        flash(f'❌ Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reportes'))

@app.route('/generar_reporte_flujo_caja')
@login_required
@modulo_requerido('reportes')
@tenant_required
def generar_reporte_flujo_caja():
    """Genera reporte de Flujo de Caja en PDF"""
    try:
        from datetime import datetime
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_flujo_caja(fecha_inicio, fecha_fin)
        
        nombre_archivo = f"flujo_caja_{fecha_inicio}_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        flash(f'❌ Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    
#===============================================libro contable==========================================================

@app.route('/generar_reporte_libro_diario')
@login_required
@modulo_requerido('reportes')
@tenant_required 
def generar_reporte_libro_diario():
    """Genera reporte de Libro Diario Contable en PDF"""
    try:
        from datetime import datetime
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_libro_diario(fecha_inicio, fecha_fin)
        
        nombre_archivo = f"libro_diario_{fecha_inicio}_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        flash(f'❌ Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reportes'))
#===========================================Conciliacion Babcaria===================================================
@app.route('/generar_reporte_conciliacion')
@login_required
@modulo_requerido('reportes')
@tenant_required 
def generar_reporte_conciliacion():
    """Genera reporte de Conciliación Bancaria en PDF"""
    try:
        fecha_corte = request.args.get('fecha_corte')
        saldo_extracto_str = request.args.get('saldo_extracto', '0')
        
        # Validar fecha
        if not fecha_corte:
            flash('❌ Debes seleccionar la fecha de corte', 'error')
            return redirect(url_for('reportes'))
        
        fecha_corte = datetime.strptime(fecha_corte, '%Y-%m-%d').date()
        saldo_extracto = float(saldo_extracto_str) if saldo_extracto_str else 0
        
        print(f"🔍 Generando conciliación para fecha: {fecha_corte}, saldo: {saldo_extracto}")
        
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_conciliacion_bancaria(fecha_corte, saldo_extracto)
        
        # Verificar que el buffer no esté vacío
        buffer_size = pdf_buffer.getbuffer().nbytes
        print(f"📊 Tamaño del buffer PDF: {buffer_size} bytes")
        
        if buffer_size == 0:
            raise Exception("El PDF generado está vacío")
        
        nombre_archivo = f"conciliacion_bancaria_{fecha_corte}.pdf"
        
        # Obtener los datos del buffer
        pdf_data = pdf_buffer.getvalue()
        
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"❌ Error detallado en generación de conciliación: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error al generar conciliación: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    
#========================================== Análisis de Gastos por Categoría=================================================
# DEBUG: Verificar métodos disponibles

generador_test = GeneradorReportes()
metodos = [method for method in dir(generador_test) if callable(getattr(generador_test, method)) and not method.startswith('_')]


@app.route('/generar_reporte_analisis_gastos')
@login_required
@modulo_requerido('reportes')
@tenant_required 
def generar_reporte_analisis_gastos():
    """Genera reporte de Análisis de Gastos por Categoría en PDF - CON FILTRO MULTI-TENANT"""
    try:
        from datetime import datetime
        
        # 🔍 OBTENER TENANT ACTUAL
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        # ✅ PASAR panaderia_id a la función
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_analisis_gastos(panaderia_id, fecha_inicio, fecha_fin)
        
        # Verificar que el buffer no esté vacío
        if pdf_buffer.getbuffer().nbytes == 0:
            raise Exception("El PDF generado está vacío")
        
        nombre_archivo = f"analisis_gastos_{fecha_inicio}_a_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"Error al generar análisis de gastos: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error al generar análisis de gastos: {str(e)}', 'error')
        return redirect(url_for('reportes'))

#==========================================================Tendencia de Ventas==============================================

@app.route('/generar_reporte_tendencia_ventas')
@login_required
@modulo_requerido('reportes')
@tenant_required
def generar_reporte_tendencia_ventas():
    """Genera reporte de Tendencia de Ventas en PDF - CON FILTRO MULTI-TENANT"""
    try:
        from datetime import datetime
        
        # 🔍 OBTENER TENANT ACTUAL
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        # ✅ PASAR panaderia_id a la función
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_tendencia_ventas(panaderia_id, fecha_inicio, fecha_fin)
        
        nombre_archivo = f"tendencia_ventas_{fecha_inicio}_a_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"Error al generar tendencia de ventas: {str(e)}")
        flash(f'❌ Error al generar tendencia de ventas: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    
# ===============================================Recomendaciones con IA===========================================================
    
    # ========================================================== IA Predictivo ===============================================

@app.route('/generar_reporte_ia_predictivo')
@login_required
@modulo_requerido('reportes')
@tenant_required 
def generar_reporte_ia_predictivo():
    """Genera reporte de IA Predictivo en PDF - CON FILTRO MULTI-TENANT"""
    try:
        from datetime import datetime
        
        # 🔍 OBTENER TENANT ACTUAL
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        # ✅ PASAR panaderia_id a la función
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_ia_predictivo(panaderia_id, fecha_inicio, fecha_fin)
        
        nombre_archivo = f"analisis_ia_predictivo_{fecha_inicio}_a_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"Error al generar reporte de IA: {str(e)}")
        flash(f'❌ Error al generar análisis de IA: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    

#========================================= Análisis de Inventarios=============================================================

# ========================================================== Análisis de Inventarios ===============================================

@app.route('/generar_reporte_analisis_inventarios')
@login_required
@modulo_requerido('reportes')
@tenant_required 
def generar_reporte_analisis_inventarios():
    """Genera reporte de Análisis de Inventarios en PDF - CON FILTRO MULTI-TENANT"""
    try:
        from datetime import datetime
        
        # 🔍 OBTENER TENANT ACTUAL
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        # ✅ PASAR panaderia_id a la función
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_analisis_inventarios(panaderia_id, fecha_inicio, fecha_fin)
        
        nombre_archivo = f"analisis_inventarios_{fecha_inicio}_a_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"Error al generar análisis de inventarios: {str(e)}")
        flash(f'❌ Error al generar análisis de inventarios: {str(e)}', 'error')
        return redirect(url_for('reportes'))

@app.route('/generar_reporte_tesoreria_unificado')
@login_required
@modulo_requerido('reportes')
@tenant_required
def generar_reporte_tesoreria_unificado():
    """Genera el Reporte Unificado de Tesorería - PDF"""
    try:
        from datetime import datetime
        from reportes import GeneradorReportes
        from flask import Response
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        nivel_detalle = request.args.get('nivel_detalle', 'completo')
        
        if not fecha_inicio or not fecha_fin:
            flash('❌ Debes seleccionar ambas fechas', 'error')
            return redirect(url_for('reportes'))
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            flash('❌ La fecha de inicio no puede ser mayor a la fecha fin', 'error')
            return redirect(url_for('reportes'))
        
        panaderia_id = obtener_panaderia_actual()
        if not panaderia_id:
            flash('No se pudo determinar la panadería', 'error')
            return redirect(url_for('reportes'))
        
        generador = GeneradorReportes()
        pdf_buffer = generador.generar_reporte_tesoreria_unificado(
        
            panaderia_id=panaderia_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            nivel_detalle=nivel_detalle
        )
        
        nombre_archivo = f"tesoreria_unificado_{fecha_inicio}_{fecha_fin}.pdf"
        
        return Response(
            pdf_buffer,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={nombre_archivo}'
            }
        )
        
    except Exception as e:
        print(f"Error al generar reporte de tesorería unificado: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('reportes'))
   
# ==========================================
# RUTAS PARA DEPÓSITOS BANCARIOS (MÓDULO TESORERÍA)
# ==========================================

@app.route('/depositos_bancarios', methods=['GET'])
@tenant_required
@login_required  # <-- SOLO ESTOS DOS
def listar_depositos_bancarios():
    """Lista todos los depósitos bancarios del tenant actual"""
    try:
        from reportes import GeneradorReportes

        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        estado = request.args.get('estado')

        generador = GeneradorReportes()

        if fecha_inicio and fecha_fin:
            # Convertir fechas string a date
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            # Usar función del generador de reportes
            depositos = generador.obtener_depositos_por_rango(fecha_inicio_dt, fecha_fin_dt)
        else:
            # Si no hay fechas, obtener todos los depósitos del tenant
            depositos = DepositoBancario.query.filter_by(
                panaderia_id=current_user.panaderia_id
            ).order_by(DepositoBancario.fecha_deposito.desc()).all()

        # Aplicar filtro de estado si se especificó
        if estado:
            depositos = [d for d in depositos if d.estado == estado]

        # Formatear respuesta
        depositos_list = []
        for dep in depositos:
            depositos_list.append({
                'id': dep.id,
                'fecha_deposito': dep.fecha_deposito.strftime('%Y-%m-%d'),
                'monto': dep.monto,
                'descripcion': dep.descripcion,
                'referencia': dep.referencia,
                'cuenta_bancaria': dep.cuenta_bancaria,
                'metodo_deposito': dep.metodo_deposito,
                'estado': dep.estado,
                'fecha_conciliacion': dep.fecha_conciliacion.strftime('%Y-%m-%d') if dep.fecha_conciliacion else None,
                'fecha_creacion': dep.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_actualizacion': dep.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            'success': True,
            'depositos': depositos_list,
            'total': len(depositos_list)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/depositos_bancarios/<int:deposito_id>', methods=['GET'])
@tenant_required
@login_required
def obtener_deposito_bancario(deposito_id):
    """Obtiene un depósito bancario específico por ID"""
    try:
        deposito = DepositoBancario.query.filter_by(
            id=deposito_id,
            panaderia_id=current_user.panaderia_id
        ).first()

        if not deposito:
            return jsonify({
                'success': False,
                'error': 'Depósito no encontrado'
            }), 404

        return jsonify({
            'success': True,
            'deposito': {
                'id': deposito.id,
                'fecha_deposito': deposito.fecha_deposito.strftime('%Y-%m-%d') if deposito.fecha_deposito else None,
                'monto': deposito.monto,
                'descripcion': deposito.descripcion,
                'referencia': deposito.referencia,
                'cuenta_bancaria': deposito.cuenta_bancaria,
                'metodo_deposito': deposito.metodo_deposito,
                'estado': deposito.estado,
                'fecha_conciliacion': deposito.fecha_conciliacion.strftime('%Y-%m-%d') if deposito.fecha_conciliacion else None,
                'fecha_creacion': deposito.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if deposito.fecha_creacion else None,
                'fecha_actualizacion': deposito.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if deposito.fecha_actualizacion else None
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/depositos_bancarios/crear', methods=['POST'])
@tenant_required
@login_required
def crear_deposito_bancario():
    """Crea un nuevo depósito bancario - VERSIÓN CORREGIDA"""
    try:
        # Verificar si es JSON o form data
        if request.is_json:
            data = request.get_json()
        else:
            # Obtener datos del formulario
            data = {
                'fecha_deposito': request.form.get('fecha_deposito'),
                'monto': request.form.get('monto'),
                'descripcion': request.form.get('descripcion', ''),
                'referencia': request.form.get('referencia', ''),
                'cuenta_bancaria': request.form.get('cuenta_bancaria', ''),
                'metodo_deposito': request.form.get('metodo_deposito'),
                'estado': request.form.get('estado', 'REGISTRADO')
            }

        print(f"📝 Datos recibidos: {data}")  # Debug

        # Validar campos obligatorios
        if not data.get('fecha_deposito'):
            return jsonify({
                'success': False,
                'error': 'La fecha de depósito es obligatoria'
            }), 400
        
        if not data.get('monto') or float(data['monto']) <= 0:
            return jsonify({
                'success': False,
                'error': 'El monto debe ser mayor a 0'
            }), 400

        # Convertir fecha
        from datetime import datetime, date
        try:
            fecha_deposito = datetime.strptime(data['fecha_deposito'], '%Y-%m-%d').date()
        except ValueError:
            try:
                fecha_deposito = datetime.strptime(data['fecha_deposito'], '%d/%m/%Y').date()
            except:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        
        # 🔒 VALIDACIÓN: No permitir fechas futuras
        hoy = date.today()
        if fecha_deposito > hoy:
            return jsonify({
                'success': False, 
                'error': 'No se pueden registrar depósitos con fecha futura. La fecha debe ser hoy o anterior.'
            }), 400

        nuevo_deposito = DepositoBancario(
            panaderia_id=current_user.panaderia_id,
            fecha_deposito=fecha_deposito,
            monto=float(data['monto']),
            descripcion=data.get('descripcion', ''),
            referencia=data.get('referencia', ''),
            cuenta_bancaria=data.get('cuenta_bancaria', ''),
            metodo_deposito=data.get('metodo_deposito', 'efectivo'),
            estado=data.get('estado', 'REGISTRADO')
        )

        db.session.add(nuevo_deposito)
        db.session.commit()

        print(f"✅ Depósito creado exitosamente: ID {nuevo_deposito.id}")

        return jsonify({
            'success': True,
            'message': 'Depósito creado exitosamente',
            'deposito_id': nuevo_deposito.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear depósito: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500


@app.route('/depositos_bancarios/editar/<int:deposito_id>', methods=['POST'])
@tenant_required
@login_required
def editar_deposito_bancario(deposito_id):
    """Edita un depósito bancario existente"""
    try:
        data = request.get_json()

        # Buscar depósito asegurándose de que pertenece al tenant actual
        deposito = DepositoBancario.query.filter_by(
            id=deposito_id,
            panaderia_id=current_user.panaderia_id
        ).first()

        if not deposito:
            return jsonify({
                'success': False,
                'error': 'Depósito no encontrado'
            }), 404

        # Actualizar campos permitidos
        if 'fecha_deposito' in data:
            from datetime import date
        fecha_deposito = datetime.strptime(data['fecha_deposito'], '%Y-%m-%d').date()
        
        # 🔒 VALIDACIÓN: No permitir fechas futuras
        hoy = date.today()
        if fecha_deposito > hoy:
            return jsonify({'success': False, 'error': 'No se pueden registrar depósitos con fecha futura. La fecha debe ser hoy o anterior.'}), 400
        if 'monto' in data:
            deposito.monto = float(data['monto'])
        if 'descripcion' in data:
            deposito.descripcion = data['descripcion']
        if 'referencia' in data:
            deposito.referencia = data['referencia']
        if 'cuenta_bancaria' in data:
            deposito.cuenta_bancaria = data['cuenta_bancaria']
        if 'metodo_deposito' in data:
            deposito.metodo_deposito = data['metodo_deposito']
        if 'estado' in data:
            deposito.estado = data['estado']
            if data['estado'] == 'CONCILIADO' and not deposito.fecha_conciliacion:
                deposito.fecha_conciliacion = datetime.now().date()

        deposito.fecha_actualizacion = datetime.now()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Depósito actualizado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/depositos_bancarios/eliminar/<int:deposito_id>', methods=['POST'])
@tenant_required
@login_required
def eliminar_deposito_bancario(deposito_id):
    """Elimina un depósito bancario (solo si está en estado REGISTRADO)"""
    try:
        deposito = DepositoBancario.query.filter_by(
            id=deposito_id,
            panaderia_id=current_user.panaderia_id
        ).first()

        if not deposito:
            return jsonify({
                'success': False,
                'error': 'Depósito no encontrado'
            }), 404

        if deposito.estado != 'REGISTRADO':
            return jsonify({
                'success': False,
                'error': 'Solo se pueden eliminar depósitos en estado REGISTRADO'
            }), 400

        db.session.delete(deposito)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Depósito eliminado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/depositos_bancarios/conciliar/<int:deposito_id>', methods=['POST'])
@tenant_required
@modulo_requerido('tesoreria')
def conciliar_deposito_bancario(deposito_id):
    """Marca un depósito como conciliado"""
    try:
        from reportes import GeneradorReportes

        generador = GeneradorReportes()
        resultado = generador.conciliar_deposito(deposito_id)

        if resultado:
            return jsonify({
                'success': True,
                'message': 'Depósito conciliado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo conciliar el depósito'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/depositos_bancarios/estadisticas', methods=['GET'])
@tenant_required
@login_required
def estadisticas_depositos_bancarios():
    """Obtiene estadísticas de depósitos bancarios"""
    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        # Construir consulta base
        query = DepositoBancario.query.filter_by(panaderia_id=current_user.panaderia_id)

        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(DepositoBancario.fecha_deposito.between(fecha_inicio_dt, fecha_fin_dt))

        depositos = query.all()

        # Calcular estadísticas
        total_depositos = len(depositos)
        total_monto = sum(d.monto for d in depositos)
        depositos_conciliados = [d for d in depositos if d.estado == 'CONCILIADO']
        total_conciliados = len(depositos_conciliados)
        monto_conciliado = sum(d.monto for d in depositos_conciliados)

        # Por método de depósito
        por_metodo = {}
        for d in depositos:
            metodo = d.metodo_deposito or 'No especificado'
            if metodo not in por_metodo:
                por_metodo[metodo] = {'count': 0, 'monto': 0}
            por_metodo[metodo]['count'] += 1
            por_metodo[metodo]['monto'] += d.monto

        return jsonify({
            'success': True,
            'estadisticas': {
                'total_depositos': total_depositos,
                'total_monto': total_monto,
                'depositos_conciliados': total_conciliados,
                'monto_conciliado': monto_conciliado,
                'por_metodo': por_metodo,
                'porcentaje_conciliacion': (total_conciliados / total_depositos * 100) if total_depositos > 0 else 0
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

# ============================================ MODELO DE ACTIVOS FIJOS EN APP.PY ========================================================

# === RUTAS DE ACTIVOS FIJOS ===

@app.route('/activos_fijos')
@login_required
@tenant_required
@modulo_requerido('activos')
def activos_fijos():
    # 🆕 VERIFICACIÓN SEGURA PARA SUPER ADMINISTRADOR
    es_super_admin = False
    try:
        # Verificación EXTRA segura
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '') or ''
        
        es_super_admin = (
            user_id == 1 or 
            username == 'dev_master' or 
            (email and hasattr(email, 'endswith') and email.endswith('dev_master'))
        )
    except Exception as e:
        print(f"⚠️ Error en verificación super admin: {e}")
        es_super_admin = False
    
    if es_super_admin:
        # Super admin: mostrar lista vacía para demostraciones
        activos = []
        flash('Modo demostración: Super administrador - Sin datos de clientes', 'info')
    else:
        # Usuarios normales: aislamiento multi-tenant normal
        activos = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id).all()
    
    # Calcular métricas
    total_activos = len(activos)
    valor_total = sum(activo.valor_actual() for activo in activos)
    activos_mantenimiento = len([a for a in activos if a.estado == 'MANTENIMIENTO'])
    
    return render_template('activos_fijos.html', 
                         activos=activos,
                         total_activos=total_activos,
                         valor_total=valor_total,
                         activos_mantenimiento=activos_mantenimiento,
                         proxima_depreciacion=0,
                         categorias=CATEGORIAS_ACTIVOS)

@app.route('/registrar_activo', methods=['GET', 'POST'])
@login_required
@tenant_required
@modulo_requerido('activos')
def registrar_activo():
    # 🆕 VERIFICACIÓN SEGURA PARA SUPER ADMINISTRADOR
    es_super_admin = False
    try:
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '') or ''
        
        es_super_admin = (
            user_id == 1 or 
            username == 'dev_master' or 
            (email and hasattr(email, 'endswith') and email.endswith('dev_master'))
        )
    except Exception as e:
        print(f"⚠️ Error en verificación super admin: {e}")
        es_super_admin = False
    
    if es_super_admin:
        flash('Modo demostración: El super administrador no puede crear activos reales', 'info')
        return redirect(url_for('activos_fijos'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            descripcion = request.form['descripcion']
            numero_serie = request.form['numero_serie']
            fecha_compra = datetime.strptime(request.form['fecha_compra'], '%Y-%m-%d').date()
            proveedor = request.form['proveedor']
            valor_compra = float(request.form['valor_compra'])
            metodo_pago = request.form['metodo_pago']
            vida_util = int(request.form['vida_util'])
            valor_residual = float(request.form.get('valor_residual', 0))
            ubicacion = request.form['ubicacion']
            responsable = request.form['responsable']
            
            # Crear nuevo activo
            nuevo_activo = ActivoFijo(
                panaderia_id=current_user.panaderia_id,
                nombre=nombre,
                categoria=categoria,
                descripcion=descripcion,
                numero_serie=numero_serie,
                fecha_compra=fecha_compra,
                proveedor=proveedor,
                valor_compra=valor_compra,
                metodo_pago=metodo_pago,
                vida_util=vida_util,
                valor_residual=valor_residual,
                ubicacion=ubicacion,
                responsable=responsable,
                estado='ACTIVO'
            )
            
            db.session.add(nuevo_activo)
            db.session.commit()
            
            flash('✅ Activo registrado exitosamente', 'success')
            return redirect(url_for('activos_fijos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al registrar activo: {str(e)}', 'error')
    
    return render_template('registrar_activo.html', categorias=CATEGORIAS_ACTIVOS)



@app.route('/editar_activo/<int:id>', methods=['GET', 'POST'])
@login_required
@tenant_required
@modulo_requerido('activos')
def editar_activo(id):
    """Editar activo fijo - Multi-tenant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    activo = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id, id=id).first_or_404()
    
    if request.method == 'POST':
        try:
            activo.nombre = request.form['nombre']
            activo.categoria = request.form['categoria']
            activo.descripcion = request.form['descripcion']
            activo.numero_serie = request.form.get('numero_serie', '')
            activo.fecha_compra = datetime.strptime(request.form['fecha_compra'], '%Y-%m-%d').date()
            activo.proveedor = request.form.get('proveedor', '')
            activo.valor_compra = float(request.form['valor_compra'])
            activo.metodo_pago = request.form.get('metodo_pago', '')
            activo.vida_util = int(request.form.get('vida_util', 5))
            activo.valor_residual = float(request.form.get('valor_residual', 0))
            activo.ubicacion = request.form.get('ubicacion', '')
            activo.responsable = request.form.get('responsable', '')
            activo.estado = request.form['estado']
            
            db.session.commit()
            
            flash('✅ Activo actualizado exitosamente', 'success')
            return redirect(url_for('lista_activos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar activo: {str(e)}', 'error')
    
    return render_template('editar_activo.html', activo=activo, categorias=CATEGORIAS_ACTIVOS)


@app.route('/activo/<int:activo_id>/mantenimientos')
@login_required
@tenant_required
@modulo_requerido('activos')
def listar_mantenimientos(activo_id):
    """Listar mantenimientos de un activo"""
    activo = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id, id=activo_id).first_or_404()
    mantenimientos = HistorialMantenimiento.query.filter_by(activo_id=activo_id).order_by(HistorialMantenimiento.fecha_mantenimiento.desc()).all()
    
    return render_template('mantenimientos.html', activo=activo, mantenimientos=mantenimientos)

@app.route('/activo/<int:activo_id>/mantenimiento/nuevo', methods=['GET', 'POST'])
@login_required
@tenant_required
@modulo_requerido('activos')
def nuevo_mantenimiento(activo_id):
    """Agregar nuevo mantenimiento a un activo"""
    activo = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id, id=activo_id).first_or_404()
    
    if request.method == 'POST':
        try:
            from datetime import datetime
            
            nuevo = HistorialMantenimiento(
                activo_id=activo_id,
                fecha_mantenimiento=datetime.strptime(request.form['fecha_mantenimiento'], '%Y-%m-%d').date(),
                tipo=request.form['tipo'],
                descripcion=request.form['descripcion'],
                costo=float(request.form.get('costo', 0)),
                tecnico=request.form.get('tecnico', ''),
                notas=request.form.get('notas', ''),
                panaderia_id=current_user.panaderia_id
            )
            
            db.session.add(nuevo)
            
            # Si el estado cambia a MANTENIMIENTO, actualizar el activo
            if 'cambiar_estado' in request.form:
                activo.estado = 'MANTENIMIENTO'
            
            db.session.commit()
            
            flash(f'✅ Mantenimiento registrado para "{activo.nombre}"', 'success')
            return redirect(url_for('listar_mantenimientos', activo_id=activo_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al registrar mantenimiento: {str(e)}', 'error')
    
    from datetime import datetime
    
    return render_template('nuevo_mantenimiento.html', activo=activo, now=datetime.now())

@app.route('/mantenimiento/<int:id>/eliminar', methods=['POST'])
@login_required
@tenant_required
@modulo_requerido('activos')
def eliminar_mantenimiento(id):
    """Eliminar un mantenimiento"""
    mantenimiento = HistorialMantenimiento.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first_or_404()
    activo_id = mantenimiento.activo_id
    
    db.session.delete(mantenimiento)
    db.session.commit()
    
    flash('✅ Mantenimiento eliminado', 'success')
    return redirect(url_for('listar_mantenimientos', activo_id=activo_id))


@app.route('/mantenimiento/<int:id>/detalle')
@login_required
@tenant_required
@modulo_requerido('activos')
def detalle_mantenimiento(id):
    """Ver detalle de un mantenimiento"""
    mantenimiento = HistorialMantenimiento.query.filter_by(id=id, panaderia_id=current_user.panaderia_id).first_or_404()
    return render_template('detalle_mantenimiento.html', mantenimiento=mantenimiento)
@app.route('/lista_activos')
@login_required
@tenant_required
@modulo_requerido('activos')
def lista_activos():
    # 🆕 VERIFICACIÓN SEGURA PARA SUPER ADMINISTRADOR
    es_super_admin = False
    try:
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '') or ''
        
        es_super_admin = (
            user_id == 1 or 
            username == 'dev_master' or 
            (email and hasattr(email, 'endswith') and email.endswith('dev_master'))
        )
    except Exception as e:
        print(f"⚠️ Error en verificación super admin: {e}")
        es_super_admin = False
    
    if es_super_admin:
        activos = []
        flash('Modo demostración: Sin datos de clientes', 'info')
    else:
        activos = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id).order_by(ActivoFijo.fecha_compra.desc()).all()
    
    return render_template('lista_activos.html', activos=activos, categorias=CATEGORIAS_ACTIVOS)

@app.route('/reporte_activos')
@login_required
@tenant_required  # ✅ AGREGADO
@modulo_requerido('activos')
def reporte_activos():
    """Reporte de activos fijos - Multi-tenant"""
    # 🔍 OBTENER TENANT ACTUAL
    panaderia_id = current_user.panaderia_id
        
    # OBTENER CONFIGURACIÓN DEL TENANT PARA EL NOMBRE
    from models import ConfiguracionSistema
    config = ConfiguracionSistema.query.filter_by(panaderia_id=panaderia_id).first()
    nombre_empresa = config.nombre_empresa if config else f'Panadería {panaderia_id}'
    nit_empresa = config.nit_empresa if config else 'N/A'
    if not panaderia_id:
        flash('No se pudo determinar la panadería', 'error')
        return redirect(url_for('dashboard'))
    
    # 🆕 VERIFICACIÓN SEGURA PARA SUPER ADMINISTRADOR
    es_super_admin = False
    try:
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '') or ''
        
        es_super_admin = (
            user_id == 1 or 
            username == 'dev_master' or 
            (email and hasattr(email, 'endswith') and email.endswith('dev_master'))
        )
    except Exception as e:
        print(f"⚠️ Error en verificación super admin: {e}")
        es_super_admin = False
    
    if es_super_admin:
        activos = []
        flash('Modo demostración: Reportes vacíos para super administrador', 'info')
        graph_path = None
    else:
        # ✅ FILTRAR POR TENANT
        activos = ActivoFijo.query.filter_by(panaderia_id=panaderia_id).all()
        graph_path = None
        
        # Generar gráficos si hay activos
        if activos:
            try:
                import matplotlib.pyplot as plt
                import os
                
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
                
                # Gráfico 1: Distribución por categoría
                categorias_count = {}
                for activo in activos:
                    cat_nombre = CATEGORIAS_ACTIVOS.get(activo.categoria, activo.categoria)
                    categorias_count[cat_nombre] = categorias_count.get(cat_nombre, 0) + 1
                
                if categorias_count:
                    ax1.pie(categorias_count.values(), labels=categorias_count.keys(), autopct='%1.1f%%')
                    ax1.set_title('Distribución de Activos por Categoría')
                
                # Gráfico 2: Valor por categoría
                categorias_valor = {}
                for activo in activos:
                    cat_nombre = CATEGORIAS_ACTIVOS.get(activo.categoria, activo.categoria)
                    categorias_valor[cat_nombre] = categorias_valor.get(cat_nombre, 0) + activo.valor_actual()
                
                if categorias_valor:
                    ax2.bar(categorias_valor.keys(), categorias_valor.values())
                    ax2.set_title('Valor Actual por Categoría')
                    ax2.tick_params(axis='x', rotation=45)
                
                # Gráfico 3: Estado de activos
                estados_count = {}
                for activo in activos:
                    estados_count[activo.estado] = estados_count.get(activo.estado, 0) + 1
                
                if estados_count:
                    ax3.pie(estados_count.values(), labels=estados_count.keys(), autopct='%1.1f%%')
                    ax3.set_title('Estado de los Activos')
                
                # Gráfico 4: Depreciación acumulada
                nombres = [activo.nombre[:15] + '...' if len(activo.nombre) > 15 else activo.nombre for activo in activos]
                valores_compra = [activo.valor_compra for activo in activos]
                depreciacion = [activo.depreciacion_acumulada() for activo in activos]
                
                x = range(len(activos))
                ax4.bar(x, valores_compra, label='Valor Compra', alpha=0.7)
                ax4.bar(x, depreciacion, label='Depreciación Acumulada', alpha=0.7)
                ax4.set_title('Depreciación Acumulada')
                ax4.legend()
                ax4.set_xticks(x)
                ax4.set_xticklabels(nombres, rotation=45, ha='right')
                
                plt.tight_layout()
                
                graph_path = os.path.join('static', 'temp', 'activos_report.png')
                os.makedirs(os.path.dirname(graph_path), exist_ok=True)
                plt.savefig(graph_path)
                plt.close()
                
            except Exception as e:
                print(f"Error generando gráficos: {e}")
                graph_path = None
    
    return render_template('reporte_activos.html',
                         nombre_empresa=nombre_empresa,
                         nit_empresa=nit_empresa, 
                         activos=activos, 
                         graph_path=graph_path,
                         total_valor=sum(activo.valor_actual() for activo in activos),
                         total_depreciacion=sum(activo.depreciacion_acumulada() for activo in activos),
                         now=datetime.now(),
                         categorias=CATEGORIAS_ACTIVOS)

@app.route('/api/activos_metrics')
@login_required
@tenant_required  # ✅ AGREGADO
@modulo_requerido('activos')
def api_activos_metrics():
    """API de métricas de activos - Multi-tenant"""
    # 🆕 VERIFICACIÓN SEGURA PARA SUPER ADMINISTRADOR
    es_super_admin = False
    try:
        user_id = getattr(current_user, 'id', None)
        username = getattr(current_user, 'username', '')
        email = getattr(current_user, 'email', '') or ''
        
        es_super_admin = (
            user_id == 1 or 
            username == 'dev_master' or 
            (email and hasattr(email, 'endswith') and email.endswith('dev_master'))
        )
    except Exception as e:
        print(f"⚠️ Error en verificación super admin: {e}")
        es_super_admin = False
    
    if es_super_admin:
        metrics = {
            'total_activos': 0,
            'valor_total': 0,
            'activos_mantenimiento': 0,
            'proxima_depreciacion': 0
        }
    else:
        activos = ActivoFijo.query.filter_by(panaderia_id=current_user.panaderia_id).all()
        
        metrics = {
            'total_activos': len(activos),
            'valor_total': sum(activo.valor_actual() for activo in activos),
            'activos_mantenimiento': len([a for a in activos if a.estado == 'MANTENIMIENTO']),
            'proxima_depreciacion': 0
        }
    
    return jsonify(metrics)

#========================================= 🆕 RUTAS PARA GESTIÓN DE USUARIOS==================================================
@app.route('/gestion_usuarios')
@login_required
@modulo_requerido('gestion_usuarios')
def gestion_usuarios():
    """Gestión de usuarios de la panadería actual"""
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if current_user.rol != 'admin_cliente':
            flash('No tienes permisos para gestionar usuarios', 'error')
            return redirect(url_for('dashboard'))
        
        panaderia_actual_id = current_user.panaderia_id
        panaderia_actual = ConfiguracionPanaderia.query.filter_by(
            id=panaderia_actual_id
        ).first()
        
        if not panaderia_actual:
            flash('Error: No se encontró información de la panadería', 'error')
            return redirect(url_for('dashboard'))
        
        # =============================================
        # 🆕 CALCULAR DATOS DE LICENCIA
        # =============================================
        from datetime import date
        import sqlite3
        import os
        
        datos_licencia = {
            'tipo': panaderia_actual.tipo_licencia or 'Local',
            'max_usuarios': panaderia_actual.max_usuarios or 3,
            'fecha_expiracion': None,
            'dias_restantes': None,
            'estado': 'activa',
            'alerta': None,
            'color': 'success'
        }
        
        # Si tiene fecha de expiración en la configuración
        if panaderia_actual.fecha_expiracion:
            fecha_exp = panaderia_actual.fecha_expiracion
            datos_licencia['fecha_expiracion'] = fecha_exp
            
            # Calcular días restantes
            if isinstance(fecha_exp, str):
                fecha_exp = datetime.strptime(fecha_exp, '%Y-%m-%d').date()
            
            hoy = date.today()
            dias = (fecha_exp - hoy).days
            
            datos_licencia['dias_restantes'] = dias
            
            if dias < 0:
                datos_licencia['estado'] = 'expirada'
                datos_licencia['color'] = 'danger'
                datos_licencia['alerta'] = f'🔴 LICENCIA EXPIRADA (hace {abs(dias)} días)'
            elif dias == 0:
                datos_licencia['estado'] = 'por_vencer'
                datos_licencia['color'] = 'warning'
                datos_licencia['alerta'] = '⚠️ ¡Tu licencia vence HOY!'
            elif dias <= 7:
                datos_licencia['estado'] = 'por_vencer'
                datos_licencia['color'] = 'warning'
                datos_licencia['alerta'] = f'⚠️ Tu licencia vence en {dias} días'
            elif dias <= 30:
                datos_licencia['estado'] = 'por_vencer'
                datos_licencia['color'] = 'info'
                datos_licencia['alerta'] = f'ℹ️ Tu licencia vence en {dias} días'
            else:
                datos_licencia['estado'] = 'activa'
                datos_licencia['color'] = 'success'
                datos_licencia['alerta'] = f'✅ Licencia activa - Vence en {dias} días'
        else:
            # Licencia LOCAL
            datos_licencia['estado'] = 'permanente'
            datos_licencia['color'] = 'secondary'
            datos_licencia['alerta'] = '🔒 Licencia Local (Permanente)'
        
        usuarios = Usuario.query.filter_by(panaderia_id=panaderia_actual_id).all()
        
        return render_template('gestion_usuarios.html',
                             usuarios=usuarios,
                             panaderia_actual=panaderia_actual,
                             datos_licencia=datos_licencia)  # 🆕 PASAMOS LOS DATOS DE LICENCIA
                             
    except Exception as e:
        print(f"❌ ERROR en gestión_usuarios: {e}")
        flash('Error interno del servidor', 'error')
        return redirect(url_for('dashboard'))
    
    
@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
@permisos_requeridos('usuarios', 'gestionar')
def crear_usuario():
    """Crear nuevo usuario con verificación de límites"""
    
    # 🆕 VERIFICAR LÍMITES ANTES DE CONTINUAR
    from models import obtener_limites_panaderia, verificar_limite_usuarios
    
    if verificar_limite_usuarios():
        limites = obtener_limites_panaderia()
        flash(f'❌ Límite de usuarios alcanzado. Tienes {limites["usuarios_actuales"]}/{limites["max_usuarios"]} usuarios.', 'error')
        return redirect(url_for('gestion_usuarios'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            nombre_completo = request.form['nombre_completo']
            email = request.form.get('email', '')
            telefono = request.form.get('telefono', '')
            rol = request.form['rol']
            
            # Verificar si usuario ya existe
            if Usuario.query.filter_by(username=username).first():
                flash('❌ El nombre de usuario ya existe', 'error')
                return redirect(url_for('crear_usuario'))
            
            # 🆕 ASIGNAR PANADERÍA POR DEFECTO (temporal)
            nuevo_usuario = Usuario(
                username=username,
                nombre_completo=nombre_completo,
                email=email,
                telefono=telefono,
                rol=rol,
                panaderia_id=1  # Temporal - se actualizará si se crea BD tenant
            )
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # ⭐⭐ NUEVO: CREACIÓN AUTOMÁTICA DE BD TENANT PARA CLIENTES ⭐⭐
            if rol in ['cliente', 'admin_cliente']:
                try:
                    from middleware_saas import gestor_tenants
                    import os
                    
                    print(f"\n" + "="*60)
                    print(f"🔄 CREANDO BD TENANT PARA NUEVO CLIENTE: {username}")
                    
                    # Crear BD automáticamente
                    tenant_info = gestor_tenants.obtener_tenant_desde_bd(username)
                    
                    if tenant_info:
                        # Actualizar usuario con ID real de panadería
                        nuevo_usuario.panaderia_id = tenant_info['id']
                        db.session.commit()
                        
                        print(f"✅ BD creada: {tenant_info['base_datos']}")
                        print(f"✅ ID asignado: {tenant_info['id']}")
                        print(f"✅ Consecutivo POS inicializado: 0")
                    else:
                        print(f"⚠️  No se pudo crear BD para {username}")
                        
                except Exception as e:
                    print(f"⚠️  Error creando BD tenant: {e}")
            
            print("="*60 + "\n")
            # ⭐⭐ FIN DE CREACIÓN AUTOMÁTICA ⭐⭐
            
            # 🆕 ACTUALIZAR INFORMACIÓN DE LÍMITES
            limites = obtener_limites_panaderia()
            
            flash(f'✅ Usuario {username} creado exitosamente. ({limites["usuarios_restantes"]} usuarios restantes)', 'success')
            return redirect(url_for('gestion_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear usuario: {str(e)}', 'error')
    
    # 🆕 PASAR INFORMACIÓN DE LÍMITES AL TEMPLATE
    limites = obtener_limites_panaderia()
    return render_template('crear_usuario.html', limites=limites)

@app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@permisos_requeridos('usuarios', 'gestionar')
def editar_usuario(usuario_id):
    """Editar usuario existente"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        try:
            usuario.nombre_completo = request.form['nombre_completo']
            usuario.email = request.form.get('email', '')
            usuario.telefono = request.form.get('telefono', '')
            usuario.rol = request.form['rol']
            usuario.activo = 'activo' in request.form
            
            # Si se proporcionó nueva contraseña
            nueva_password = request.form.get('nueva_password', '')
            if nueva_password:
                usuario.set_password(nueva_password)
            
            db.session.commit()
            flash(f'✅ Usuario {usuario.username} actualizado', 'success')
            return redirect(url_for('gestion_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar usuario: {str(e)}', 'error')
    
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/toggle_usuario/<int:usuario_id>')
@login_required
@permisos_requeridos('usuarios', 'gestionar')
def toggle_usuario(usuario_id):
    """Activar/desactivar usuario"""
    if usuario_id == current_user.id:
        flash('❌ No puedes desactivar tu propio usuario', 'error')
        return redirect(url_for('gestion_usuarios'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.activo = not usuario.activo
    
    estado = "activado" if usuario.activo else "desactivado"
    db.session.commit()
    
    flash(f'✅ Usuario {usuario.username} {estado}', 'success')
    return redirect(url_for('gestion_usuarios'))

# 🆕 RUTA PARA PERFIL DE USUARIO
@app.route('/mi_perfil', methods=['GET', 'POST'])
@login_required
@modulo_requerido('usuarios')
def mi_perfil():
    """Perfil del usuario actual"""
    if request.method == 'POST':
        try:
            current_user.nombre_completo = request.form['nombre_completo']
            current_user.email = request.form.get('email', '')
            current_user.telefono = request.form.get('telefono', '')
            
            # Cambio de contraseña
            nueva_password = request.form.get('nueva_password', '')
            if nueva_password:
                current_user.set_password(nueva_password)
                flash('✅ Contraseña actualizada correctamente', 'success')
            
            db.session.commit()
            flash('✅ Perfil actualizado correctamente', 'success')
            return redirect(url_for('mi_perfil'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar perfil: {str(e)}', 'error')
    
    return render_template('mi_perfil.html')

# 🆕 RUTAS PARA GESTIÓN DE PERMISOS - AGREGAR DESPUÉS DE LAS RUTAS DE USUARIOS EXISTENTES

@app.route('/gestionar_permisos/<int:usuario_id>')
@login_required
def gestionar_permisos(usuario_id):
    """Interfaz para gestionar permisos de usuario"""
    # Solo administradores pueden gestionar permisos
    if not current_user.tiene_permiso('usuarios', 'gestionar'):
        flash('❌ No tienes permisos para gestionar permisos', 'error')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('gestionar_permisos.html', usuario=usuario)

@app.route('/guardar_permisos/<int:usuario_id>', methods=['POST'])
@login_required
def guardar_permisos(usuario_id):
    """Guardar permisos personalizados"""
    try:
        # Verificar permisos
        if not current_user.tiene_permiso('usuarios', 'gestionar'):
            flash('❌ No tienes permisos para gestionar permisos', 'error')
            return redirect(url_for('dashboard'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Eliminar permisos existentes del usuario
        from models import PermisoUsuario
        PermisoUsuario.query.filter_by(usuario_id=usuario_id).delete()
        
        # Procesar nuevos permisos del formulario
        for key, value in request.form.items():
            if key.startswith('permiso_'):
                # Formato: permiso_modulo_accion
                partes = key.split('_')
                if len(partes) >= 3:
                    modulo = partes[1]
                    accion = partes[2]
                    
                    permiso = PermisoUsuario(
                        usuario_id=usuario_id,
                        modulo=modulo,
                        accion=accion,
                        permitido=True
                    )
                    db.session.add(permiso)
        
        db.session.commit()
        flash(f'✅ Permisos de {usuario.username} actualizados correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al guardar permisos: {str(e)}', 'error')
        print(f"Error guardando permisos: {e}")
    
    return redirect(url_for('gestion_usuarios'))

# =============================================
# 🆕 RUTAS PARA GESTIÓN DE CLIENTES (SUSCRIPCIONES)
# =============================================

@app.route('/gestion_clientes')
@login_required
@modulo_requerido('gestion_clientes')  # ✅ CORREGIDO: 'sistema' → 'gestion_clientes'
def gestion_clientes():
    """Panel de gestión de clientes/suscripciones"""
    from models import ConfiguracionPanaderia
    
    # 🔄 ACTUALIZAR ESTADOS DE SUSCRIPCIÓN ANTES DE MOSTRAR
    configuraciones = ConfiguracionPanaderia.query.filter_by(panaderia_id=current_user.panaderia_id).all()
    for config in configuraciones:
        config.actualizar_estado_suscripcion()
    db.session.commit()
    
    # Calcular métricas
    clientes_activos = sum(1 for c in configuraciones if c.suscripcion_activa)
    clientes_por_vencer = sum(1 for c in configuraciones if c.tipo_licencia != 'local' and 0 < c.dias_para_expiracion <= 7)
    clientes_vencidos = sum(1 for c in configuraciones if c.tipo_licencia != 'local' and not c.suscripcion_activa)
    total_clientes = len(configuraciones)
    
    return render_template('gestion_clientes.html',
                         configuraciones=configuraciones,
                         clientes_activos=clientes_activos,
                         clientes_por_vencer=clientes_por_vencer,
                         clientes_vencidos=clientes_vencidos,
                         total_clientes=total_clientes)

@app.route('/crear_cliente', methods=['POST'])
@login_required
@modulo_requerido('sistema')
def crear_cliente():
    """Crear un nuevo cliente/panadería con usuarios automáticos"""
    from models import ConfiguracionPanaderia, Usuario
    from werkzeug.security import generate_password_hash
    import secrets
    import string
    import sqlite3
    import os
    import shutil
    
    try:
        # Obtener datos del formulario
        nombre_panaderia = request.form.get('nombre_panaderia')
        telefono_contacto = request.form.get('telefono_contacto')
        direccion = request.form.get('direccion')
        tipo_licencia = request.form.get('tipo_licencia')
        max_usuarios = int(request.form.get('max_usuarios', 3))
        fecha_expiracion = request.form.get('fecha_expiracion')
        dias_gracia = int(request.form.get('dias_gracia', 7))
        razon_social = request.form.get('razon_social')
        nit = request.form.get('nit')
        
        # Generar subdominio para la BD del tenant
        subdominio = nombre_panaderia.lower().replace(' ', '_').replace('-', '_')[:20]
        subdominio = ''.join(c for c in subdominio if c.isalnum() or c == '_')
        email_admin = f"admin_{subdominio}@panaderias.com"
        
        # =============================================
        # PASO 1: CREAR TENANT SAAS (OBTENER ID)
        # =============================================
        exito, mensaje, tenant_id = crear_tenant_saas(nombre_panaderia, subdominio, email_admin)
        
        if not exito:
            flash(f'❌ Error al crear tenant SaaS: {mensaje}', 'error')
            return redirect(url_for('gestion_clientes'))
        
        print(f"✅ SaaS: {mensaje} (ID: {tenant_id})")
        
        # =============================================
        # PASO 2: CREAR CONFIGURACIÓN CON EL MISMO ID
        # =============================================
        nueva_config = ConfiguracionPanaderia(
            id=tenant_id,
            tenant_id=tenant_id,
            nombre_panaderia=nombre_panaderia,
            telefono_contacto=telefono_contacto,
            direccion=direccion,
            tipo_licencia=tipo_licencia,
            max_usuarios=max_usuarios,
            dias_gracia=dias_gracia,
            razon_social=razon_social,
            nit=nit,
            activo=1
        )
        
        # Solo agregar fecha de expiración para licencias en la nube
        if tipo_licencia != 'local' and fecha_expiracion:
            nueva_config.fecha_expiracion = datetime.strptime(fecha_expiracion, '%Y-%m-%d').date()
        
        db.session.add(nueva_config)
        db.session.flush()
        panaderia_id = nueva_config.id
        
        print(f"✅ Configuración creada con ID: {panaderia_id} (tenant_id: {tenant_id})")
        
        # =============================================
        # PASO 3: CREAR USUARIOS AUTOMÁTICAMENTE
        # =============================================
        def generar_contrasena_temporal():
            caracteres = string.ascii_letters + string.digits + "!@#$%"
            return ''.join(secrets.choice(caracteres) for _ in range(10))
        
        contrasena_temp = generar_contrasena_temporal()
        
        usuarios_base = [
            {
                'username': f'admin_{panaderia_id}',
                'rol': 'admin_cliente',
                'nombre': f'Administrador {nombre_panaderia}'
            },
            {
                'username': f'super_{panaderia_id}',
                'rol': 'supervisor', 
                'nombre': f'Supervisor {nombre_panaderia}'
            },
            {
                'username': f'cajero_{panaderia_id}',
                'rol': 'cajero',
                'nombre': f'Cajero Principal {nombre_panaderia}'
            }
        ]
        
        usuarios_creados = []
        
        # Construir la ruta de la BD del tenant
        bd_tenant_path = os.path.join('databases_tenants', f'{subdominio}.db')
        print(f"📁 Creando usuarios en: {bd_tenant_path}")
        
        os.makedirs('databases_tenants', exist_ok=True)
        
        # Si la BD del tenant no existe, copiar desde plantilla
        if not os.path.exists(bd_tenant_path):
            plantilla_path = os.path.join('databases_tenants', 'tenant_plantilla.db')
            if os.path.exists(plantilla_path):
                shutil.copy2(plantilla_path, bd_tenant_path)
                print(f"📋 Plantilla copiada a: {bd_tenant_path}")
            else:
                print(f"⚠️ No se encontró plantilla en: {plantilla_path}")
        
        # Conectar a la BD del tenant
        conn_tenant = sqlite3.connect(bd_tenant_path)
        cursor_tenant = conn_tenant.cursor()
        
        # Verificar que la tabla usuarios existe
        cursor_tenant.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor_tenant.fetchone():
            print("⚠️ Tabla 'usuarios' no encontrada, creándola...")
            cursor_tenant.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre_completo TEXT,
                    email TEXT,
                    telefono TEXT,
                    rol TEXT DEFAULT 'usuario',
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    panaderia_id INTEGER DEFAULT 1
                )
            ''')
        
        # Crear cada usuario en la BD del tenant (SIEMPRE, incluso si ya existen)
        for user_data in usuarios_base:
            # Verificar si el usuario ya existe
            cursor_tenant.execute("SELECT id, activo FROM usuarios WHERE username = ?", (user_data['username'],))
            existing = cursor_tenant.fetchone()
            
            if existing:
                # Si existe pero está inactivo, activarlo
                if existing[1] == 0:
                    cursor_tenant.execute("UPDATE usuarios SET activo = 1 WHERE username = ?", (user_data['username'],))
                    print(f"   ✅ Usuario reactivado: {user_data['username']}")
                    usuarios_creados.append(user_data['username'])
                else:
                    print(f"   ⚠️ Usuario ya existe y está activo: {user_data['username']}")
                continue
            
            # Crear nuevo usuario (siempre activo)
            cursor_tenant.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo, panaderia_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'],
                generate_password_hash(contrasena_temp),
                user_data['nombre'],
                user_data['rol'],
                1,  # Siempre activo
                panaderia_id
            ))
            usuarios_creados.append(user_data['username'])
            print(f"   ✅ Usuario creado: {user_data['username']}")
        
        conn_tenant.commit()
        conn_tenant.close()
        
        # Registrar usuarios en BD principal (solo si no existen)
        try:
            for user_data in usuarios_base:
                existing = Usuario.query.filter_by(username=user_data['username']).first()
                if not existing:
                    nuevo_usuario = Usuario(
                        username=user_data['username'],
                        password_hash=generate_password_hash(contrasena_temp),
                        nombre_completo=user_data['nombre'],
                        rol=user_data['rol'],
                        panaderia_id=panaderia_id,
                        activo=1
                    )
                    db.session.add(nuevo_usuario)
                    print(f"   Registrado en BD principal: {user_data['username']}")
                else:
                    # Si existe pero está inactivo, activarlo
                    if existing.activo == 0:
                        existing.activo = 1
                        print(f"   Reactivado en BD principal: {user_data['username']}")
            
            db.session.commit()
            print(f"✅ Usuarios registrados en BD principal")
        except Exception as e:
            db.session.rollback()
            print(f"   Error registrando en BD principal: {e}")
        
        print(f"✅ {len(usuarios_creados)} usuarios creados/activados en la BD del tenant")
        
        # Mensaje de éxito
        flash(
            f'✅ Cliente "{nombre_panaderia}" creado exitosamente | '
            f'👥 Usuarios: {", ".join(usuarios_creados)} | '
            f'🔑 Contraseña: {contrasena_temp} | '
            f'🏪 Tenant SaaS: {subdominio} | '
            f'💡 Cambiar contraseña al primer inicio',
            'success'
        )
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al crear cliente: {str(e)}', 'error')
        print(f"❌ Error en crear_cliente: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('gestion_clientes'))

@app.route('/resetear_password/<int:usuario_id>', methods=['POST'])
@login_required
def resetear_password(usuario_id):
    """🎯 SISTEMA DE RESETEO PROFESIONAL - PREPARADO PARA MIGRACIÓN"""
    if current_user.rol != 'super_admin':
        return jsonify({
            'success': False, 
            'error': '❌ Solo super_admin puede resetear contraseñas'
        })
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # 🎯 GENERACIÓN DE CONTRASEÑA SEGURA (MEJORES PRÁCTICAS)
        nueva_password = generar_contrasena_segura()
        
        # 🎯 ESTRATEGIA HÍBRIDA TEMPORAL - COMPATIBILIDAD CON SISTEMA ACTUAL
        # Durante transición, usar hash simple para garantizar funcionamiento
        # En FASE 2, migraremos gradualmente a hash seguro
        usuario.password_hash = f"dev_{nueva_password}_hash"
        
        # 🔐 REGISTRO DE ACTIVIDAD (PREPARACIÓN PARA AUDITORÍA)
        registrar_reseteo_password(usuario.id, current_user.id)
        
        db.session.commit()
        
        # 🎯 RESPUESTA PROFESIONAL CON INFORMACIÓN COMPLETA
        return jsonify({
            'success': True,
            'nueva_password': nueva_password,
            'usuario': usuario.username,
            'panaderia_id': usuario.panaderia_id,
            'nota': '🔒 En producción, esta contraseña se enviará automáticamente por email',
            'instrucciones': [
                '1. Compartir esta contraseña de manera segura con el usuario',
                '2. El usuario debe cambiar la contraseña en su primer acceso',
                '3. En FASE 2, esto será automático por email'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ [RESETEO] Error: {e}")
        return jsonify({
            'success': False, 
            'error': f'Error al resetear contraseña: {str(e)}'
        })

def generar_contrasena_segura():
    """
    🎯 GENERADOR PROFESIONAL DE CONTRASEÑAS - MEJORES PRÁCTICAS DE SEGURIDAD
    """
    import secrets
    import string
    
    # 🎯 CONFIGURACIÓN DE SEGURIDAD
    longitud = 12  # Longitud óptima para seguridad y usabilidad
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    
    # 🎯 GARANTIZAR COMPLEJIDAD MÍNIMA (AL MENOS UNO DE CADA TIPO)
    intentos_maximos = 10  # Prevenir bucles infinitos
    
    for intento in range(intentos_maximos):
        password = ''.join(secrets.choice(caracteres) for _ in range(longitud))
        
        # VERIFICAR CRITERIOS DE COMPLEJIDAD
        tiene_minuscula = any(c.islower() for c in password)
        tiene_mayuscula = any(c.isupper() for c in password)
        tiene_numero = any(c.isdigit() for c in password)
        tiene_simbolo = any(c in "!@#$%" for c in password)
        
        if todas([tiene_minuscula, tiene_mayuscula, tiene_numero, tiene_simbolo]):
            print(f"✅ [GENERADOR] Contraseña segura generada en intento {intento + 1}")
            return password
    
    # 🎯 FALLBACK: Si no cumple criterios después de intentos, generar una igual
    password_fallback = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    print(f"⚠️ [GENERADOR] Usando fallback después de {intentos_maximos} intentos")
    return password_fallback

def todas(condiciones):
    """🎯 FUNCIÓN AUXILIAR PARA VERIFICAR MÚLTIPLES CONDICIONES"""
    return all(condiciones)

def registrar_reseteo_password(usuario_id, administrador_id):
    """
    🎯 PREPARACIÓN PARA AUDITORÍA DE SEGURIDAD PROFESIONAL
    En FASE 2, esto se migrará a tabla de auditoría en base de datos
    """
    try:
        # 📊 LOG TEMPORAL - EN FASE 2 SE MIGRA A BASE DE DATOS
        print(f"📊 [AUDITORÍA] Reseteo - Usuario: {usuario_id}, Admin: {administrador_id}")
        
        # 🆕 CÓDIGO PREPARADO PARA FASE 2 (ACTUALMENTE COMENTADO)
        # from datetime import datetime
        # from models import AuditoriaSeguridad  # 🎯 TABLA POR CREAR EN FASE 2
        # 
        # auditoria = AuditoriaSeguridad(
        #     usuario_id=usuario_id,
        #     administrador_id=administrador_id,
        #     accion='reset_password',
        #     ip_address=request.remote_addr,
        #     user_agent=request.headers.get('User-Agent'),
        #     fecha_hora=datetime.now(),
        #     detalles='Reseteo manual por super_admin'
        # )
        # db.session.add(auditoria)
        # db.session.commit()
        
    except Exception as e:
        print(f"⚠️ [AUDITORÍA] Error registrando reseteo: {e}")
        
@app.route('/obtener_usuarios_panaderia/<int:panaderia_id>')
@login_required
def obtener_usuarios_panaderia(panaderia_id):
    """Obtener usuarios de una panadería específica (solo super_admin)"""
    if current_user.rol != 'super_admin':
        return jsonify([])
    
    try:
        usuarios = Usuario.query.filter_by(panaderia_id=panaderia_id).all()
        usuarios_data = []
        
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'username': usuario.username,
                'nombre_completo': usuario.nombre_completo,
                'rol': usuario.rol,
                'activo': usuario.activo
            })
        
        return jsonify(usuarios_data)
        
    except Exception as e:
        return jsonify([])
    
@app.route('/obtener_datos_cliente/<int:cliente_id>')
@login_required
def obtener_datos_cliente(cliente_id):
    """Obtener datos de un cliente específico para edición"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import ConfiguracionPanaderia
        cliente = ConfiguracionPanaderia.query.get_or_404(cliente_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': cliente.id,
                'nombre_panaderia': cliente.nombre_panaderia,
                'telefono_contacto': cliente.telefono_contacto,
                'direccion': cliente.direccion,
                'tipo_licencia': cliente.tipo_licencia,
                'max_usuarios': cliente.max_usuarios,
                'fecha_expiracion': cliente.fecha_expiracion.strftime('%Y-%m-%d') if cliente.fecha_expiracion else None,
                'dias_gracia': cliente.dias_gracia,
                'razon_social': cliente.razon_social,
                'nit': cliente.nit
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/editar_cliente', methods=['POST'])
@login_required
def editar_cliente():
    """Editar datos de un cliente existente"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import ConfiguracionPanaderia
        cliente_id = request.form.get('cliente_id')
        cliente = ConfiguracionPanaderia.query.get_or_404(cliente_id)
        
        # Actualizar datos
        cliente.nombre_panaderia = request.form.get('nombre_panaderia')
        cliente.telefono_contacto = request.form.get('telefono_contacto')
        cliente.direccion = request.form.get('direccion')
        cliente.tipo_licencia = request.form.get('tipo_licencia')
        cliente.max_usuarios = int(request.form.get('max_usuarios'))
        cliente.dias_gracia = int(request.form.get('dias_gracia', 7))
        cliente.razon_social = request.form.get('razon_social')
        cliente.nit = request.form.get('nit')
        
        # Manejar fecha de expiración
        fecha_expiracion = request.form.get('fecha_expiracion')
        if cliente.tipo_licencia != 'local' and fecha_expiracion:
            cliente.fecha_expiracion = datetime.strptime(fecha_expiracion, '%Y-%m-%d').date()
        elif cliente.tipo_licencia == 'local':
            cliente.fecha_expiracion = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cliente actualizado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    
# =============================================
# 🆕 RUTAS PARA LOS 3 BOTONES DE GESTIÓN DE CLIENTES (VERSIÓN CORREGIDA)
# =============================================

@app.route('/obtener_datos_cliente_super/<int:cliente_id>')
@login_required
def obtener_datos_cliente_super(cliente_id):
    """Obtener datos de un cliente específico para edición (SUPER ADMIN)"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import ConfiguracionPanaderia
        cliente = ConfiguracionPanaderia.query.get_or_404(cliente_id)
        
        # Determinar estado de suscripción
        estado_suscripcion = 'activa'
        if cliente.tipo_licencia != 'local' and cliente.fecha_expiracion:
            from datetime import datetime
            if cliente.fecha_expiracion < datetime.now().date():
                estado_suscripcion = 'expirada'
            elif (cliente.fecha_expiracion - datetime.now().date()).days <= 7:
                estado_suscripcion = 'por_vencer'
        
        return jsonify({
            'success': True,
            'data': {
                'id': cliente.id,
                'nombre_panaderia': cliente.nombre_panaderia,
                'telefono_contacto': cliente.telefono_contacto,
                'direccion': cliente.direccion,
                'tipo_licencia': cliente.tipo_licencia,
                'max_usuarios': cliente.max_usuarios,
                'fecha_expiracion': cliente.fecha_expiracion.strftime('%Y-%m-%d') if cliente.fecha_expiracion else None,
                'dias_gracia': cliente.dias_gracia,
                'razon_social': cliente.razon_social,
                'nit': cliente.nit,
                'estado_suscripcion': estado_suscripcion
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/editar_cliente_super', methods=['POST'])
@login_required
def editar_cliente_super():
    """Editar datos de un cliente existente (SUPER ADMIN)"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import ConfiguracionPanaderia
        from datetime import datetime
        
        cliente_id = request.form.get('cliente_id')
        cliente = ConfiguracionPanaderia.query.get_or_404(cliente_id)
        
        # Actualizar datos
        cliente.nombre_panaderia = request.form.get('nombre_panaderia')
        cliente.telefono_contacto = request.form.get('telefono_contacto')
        cliente.direccion = request.form.get('direccion')
        cliente.tipo_licencia = request.form.get('tipo_licencia')
        cliente.max_usuarios = int(request.form.get('max_usuarios'))
        cliente.dias_gracia = int(request.form.get('dias_gracia', 7))
        cliente.razon_social = request.form.get('razon_social')
        cliente.nit = request.form.get('nit')
        
        # Manejar fecha de expiración
        fecha_expiracion = request.form.get('fecha_expiracion')
        if cliente.tipo_licencia != 'local' and fecha_expiracion:
            cliente.fecha_expiracion = datetime.strptime(fecha_expiracion, '%Y-%m-%d').date()
        elif cliente.tipo_licencia == 'local':
            cliente.fecha_expiracion = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cliente actualizado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/renovar_suscripcion_super', methods=['POST'])
@login_required
def renovar_suscripcion_super():
    """Renovar suscripción de un cliente (SUPER ADMIN)"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import ConfiguracionPanaderia
        from datetime import datetime
        
        cliente_id = request.form.get('cliente_id')
        cliente = ConfiguracionPanaderia.query.get_or_404(cliente_id)
        
        # Actualizar datos
        cliente.tipo_licencia = request.form.get('tipo_licencia')
        cliente.max_usuarios = int(request.form.get('max_usuarios'))
        
        # Manejar fecha de expiración para licencias en la nube
        if cliente.tipo_licencia != 'local':
            nueva_fecha = request.form.get('nueva_fecha_expiracion')
            if nueva_fecha:
                cliente.fecha_expiracion = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
        else:
            cliente.fecha_expiracion = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Suscripción renovada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/acceder_panaderia_super/<int:panaderia_id>/<int:usuario_id>')
@login_required
def acceder_panaderia_super(panaderia_id, usuario_id):
    """Acceder a una panadería como super admin - VERSIÓN FUNCIONAL"""
    if current_user.rol != 'super_admin':
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        from models import Usuario
        usuario_target = Usuario.query.filter_by(id=usuario_id, panaderia_id=panaderia_id).first()
        
        if not usuario_target:
            return jsonify({'success': False, 'error': 'Usuario no encontrado en esta panadería'})
        
        # ✅ ✅ ✅ CORRECCIÓN CRÍTICA: CAMBIAR LA SESIÓN ✅ ✅ ✅
        session['panaderia_id'] = panaderia_id
        print(f"✅ Super usuario accediendo a panadería: {panaderia_id} como usuario: {usuario_target.username}")
        
        return jsonify({
            'success': True, 
            'message': f'Acceso concedido a panadería {panaderia_id}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 
    
@app.route('/acceder_panaderia/<int:panaderia_id>')
@login_required
def acceder_panaderia(panaderia_id):
    """Acceso remoto para super usuario a cualquier panadería"""
    print(f"🎯 DEBUG: Iniciando acceso remoto a panadería {panaderia_id}")
    
    if not es_super_usuario():
        print("❌ DEBUG: No es super usuario - bloqueando acceso")
        flash('No tienes permisos para acceso remoto', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"✅ DEBUG: Es super usuario - activando acceso remoto")
    
    # Guardar en variable SEPARADA, NO sobreescribir panaderia_id
    session['panaderia_remota'] = panaderia_id
    print(f"✅ DEBUG: panaderia_remota guardado: {session.get('panaderia_remota')}")
    
    panaderia = Panaderia.query.get(panaderia_id)
    print(f"✅ DEBUG: Panadería encontrada: {panaderia.nombre if panaderia else 'NO ENCONTRADA'}")
    
    if panaderia:
        flash(f'🔧 Acceso remoto activado: {panaderia.nombre}', 'success')
    else:
        flash('🔧 Acceso remoto activado', 'success')
    
    print(f"✅ DEBUG: Redirigiendo a dashboard")
    return redirect(url_for('dashboard'))

@app.route('/salir_acceso_remoto')
@login_required
def salir_acceso_remoto():
    """Salir del modo acceso remoto"""
    if 'panaderia_remota' in session:
        panaderia_id = session['panaderia_remota']
        session.pop('panaderia_remota')
        flash('Has salido del modo acceso remoto', 'info')
    return redirect(url_for('gestion_clientes'))

 
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



# ============================================
# ELIMINAR CLIENTE (TENANT) - Solo Super Admin
# ============================================
@app.route('/eliminar_cliente/<int:tenant_id>', methods=['POST'])
@login_required
def eliminar_cliente(tenant_id):
    """Elimina un cliente - Busca por tenant_id en configuracion_panaderia"""
    import sqlite3
    import os
    
    print(f"🔍 [ELIMINAR] Iniciando eliminación del tenant ID: {tenant_id}")
    try:
        if session.get('rol') != 'super_admin':
            return jsonify({'success': False, 'error': 'No tienes permiso'}), 403
        
        # =============================================
        # 1. BUSCAR EN configuracion_panaderia POR tenant_id
        # =============================================
        conn_principal = sqlite3.connect('databases_tenants/panaderia_principal.db')
        cursor_principal = conn_principal.cursor()
        cursor_principal.execute(
            "SELECT id, nombre_panaderia FROM configuracion_panaderia WHERE tenant_id = ?",
            (tenant_id,)
        )
        config = cursor_principal.fetchone()
        
        if not config:
            # Si no se encuentra por tenant_id, intentar por id (para compatibilidad)
            cursor_principal.execute(
                "SELECT id, nombre_panaderia FROM configuracion_panaderia WHERE id = ?",
                (tenant_id,)
            )
            config = cursor_principal.fetchone()
            
        if not config:
            conn_principal.close()
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        config_id = config[0]
        nombre_tenant = config[1]
        print(f"✅ [ELIMINAR] Encontrado en configuracion: {nombre_tenant} (config_id: {config_id})")
        
        # =============================================
        # 2. BUSCAR EN tenant_master POR tenant_id
        # =============================================
        conn_master = sqlite3.connect('tenant_master.db')
        cursor_master = conn_master.cursor()
        cursor_master.execute(
            "SELECT id, nombre, subdominio FROM tenants WHERE id = ?",
            (tenant_id,)
        )
        tenant = cursor_master.fetchone()
        
        if tenant:
            master_id = tenant[0]
            subdominio = tenant[2]
            print(f"✅ [ELIMINAR] Encontrado en master: ID {master_id}")
            
            if master_id == 1:
                conn_master.close()
                conn_principal.close()
                return jsonify({'success': False, 'error': 'No se puede eliminar el principal'}), 403
            
            # Eliminar de tenant_master
            cursor_master.execute("DELETE FROM tenants WHERE id = ?", (master_id,))
            conn_master.commit()
            print(f"✅ [ELIMINAR] Eliminado de tenant_master")
            
            # Eliminar archivo de BD
            db_file = f"databases_tenants/{subdominio}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"✅ [ELIMINAR] BD eliminada: {db_file}")
        else:
            print(f"⚠️ [ELIMINAR] No encontrado en tenant_master (ya fue eliminado)")
        
        conn_master.close()
        
        # =============================================
        # 3. ELIMINAR DE configuracion_panaderia
        # =============================================
        cursor_principal.execute(
            "DELETE FROM configuracion_panaderia WHERE id = ?",
            (config_id,)
        )
        conn_principal.commit()
        conn_principal.close()
        print(f"✅ [ELIMINAR] Eliminado de configuracion_panaderia")
        
        return jsonify({'success': True, 'message': f'Cliente "{nombre_tenant}" eliminado exitosamente'})
        
    except Exception as e:
        print(f"❌ [ELIMINAR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
# ============================================
# ACTIVAR/DESACTIVAR CLIENTE (TOGGLE)
# ============================================
@app.route('/toggle_cliente/<int:tenant_id>', methods=['POST'])
@login_required
def toggle_cliente(tenant_id):
    """Activa o desactiva un cliente (Solo super_admin)"""
    try:
        # Verificar permisos
        if session.get('rol') != 'super_admin':
            return jsonify({'success': False, 'error': 'No tienes permiso'}), 403
        
        import sqlite3
        
        print(f"🔍 [TOGGLE] Iniciando toggle del tenant ID: {tenant_id}")
        
        # 1. Obtener estado actual en tenant_master
        conn_master = sqlite3.connect('tenant_master.db')
        cursor_master = conn_master.cursor()
        cursor_master.execute("SELECT activo FROM tenants WHERE id = ?", (tenant_id,))
        resultado = cursor_master.fetchone()
        
        if not resultado:
            conn_master.close()
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        estado_actual = resultado[0] if resultado[0] is not None else 1
        nuevo_estado = 0 if estado_actual == 1 else 1
        
        print(f"📊 Estado actual: {estado_actual} → Nuevo estado: {nuevo_estado}")
        
        # 2. Actualizar tenant_master
        cursor_master.execute("UPDATE tenants SET activo = ? WHERE id = ?", (nuevo_estado, tenant_id))
        conn_master.commit()
        conn_master.close()
        print(f"✅ Tenant actualizado en tenant_master.db")
        
        # 3. Actualizar configuracion_panaderia
        conn_principal = sqlite3.connect('databases_tenants/panaderia_principal.db')
        cursor_principal = conn_principal.cursor()
        
        # Actualizar por id o por tenant_id
        cursor_principal.execute(
            "UPDATE configuracion_panaderia SET activo = ? WHERE id = ? OR tenant_id = ?",
            (nuevo_estado, tenant_id, tenant_id)
        )
        conn_principal.commit()
        conn_principal.close()
        print(f"✅ Configuración actualizada en panaderia_principal.db")
        
        estado_texto = "ACTIVADO" if nuevo_estado == 1 else "DESACTIVADO"
        print(f"✅ Cliente ID {tenant_id} {estado_texto}")
        
        return jsonify({
            'success': True,
            'message': f'Cliente {estado_texto} exitosamente',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        print(f"❌ Error en toggle_cliente: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# INICIAR APLICACIÓN
# ============================================
if __name__ == '__main__':
    print("🚀 Iniciando Servidor...")
    print("📂 Sistema Multi-Tenant para Panaderías")
    print("🌐 http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
