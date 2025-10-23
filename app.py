import os
import uuid
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract
from reportes import GeneradorReportes
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from models import JornadaVentas, CierreDiario, obtener_jornada_activa, cerrar_jornada_actual, obtener_ventas_dia, obtener_historial_cierres
from facturacion.generador_xml import generar_xml_ubl_21
from models import ConsecutivoPOS, ConfiguracionSistema, Cliente


# 🆕 DEFINICIÓN DE MÓDULOS DEL SISTEMA - AGREGAR ESTO PRIMERO
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

# 🆕 OBTENER LA RUTA BASE DEL PROYECTO - ANTES DE CREAR LA APP
basedir = os.path.abspath(os.path.dirname(__file__))

# 🆕 CREAR APLICACIÓN FLASK - AHORA SÍ PUEDE USAR basedir
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'panaderia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta_muy_segura_panaderia_2025'

# 🆕 DECORADORES PARA CONTROL DE ACCESO - DESPUÉS DE CREAR 'app'
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
    """Decorador para verificar acceso al módulo completo - VERSIÓN CORREGIDA"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            # ✅ CORRECCIÓN: Redirigir a una ruta segura
            if not current_user.puede_acceder_modulo(modulo):
                flash(f'❌ No tienes acceso al módulo {MODULOS_SISTEMA.get(modulo, modulo)}', 'error')
                # Redirigir al perfil del usuario (siempre accesible)
                return redirect(url_for('mi_perfil'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 🆕 CONTEXT PROCESSOR PARA PERMISOS EN TEMPLATES
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

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Importar db desde models - UNA sola instancia
from models import db

# Inicializar db con la app
db.init_app(app)

# ... EL RESTO DE TU CÓDIGO PERMANECE IGUAL ...

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Importar modelos DESPUÉS de inicializar db
from models import Usuario, Producto, Venta, DetalleVenta, MateriaPrima, Receta, RecetaIngrediente
from models import OrdenProduccion, Categoria, Proveedor, HistorialCompra, HistorialInventario
from models import ConfiguracionProduccion, HistorialRotacionProducto, ControlVidaUtil, Factura
from models import ProductoExterno, CompraExterna, RegistroDiario, SaldoBanco, PagoIndividual
from models import calcular_rotacion_automatica, actualizar_rotaciones_automaticas
from models import calcular_tendencia_ventas, analizar_productos_periodo, calcular_rotacion_automatica_por_nombre
from models import calcular_proyeccion_ventas, generar_recomendacion_stock, generar_alertas_inteligentes
from models import obtener_productos_sin_ventas_recientes, ActivoFijo, CATEGORIAS_ACTIVOS

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear tablas y datos iniciales
with app.app_context():
    db.create_all()
    
    # Verificar si ya existe un usuario admin
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = generate_password_hash('admin123')
        admin_user = Usuario(
            username='admin', 
            password_hash=hashed_password, 
            nombre_completo='Administrador Principal',  # ← ¡AGREGA ESTE CAMPO!
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
    
    # CREAR PROVEEDORES DE EJEMPLO SI NO EXISTEN
    if not Proveedor.query.first():
        proveedores_ejemplo = [
            Proveedor(
                nombre="Haz de Oros",
                contacto="Juan Pérez",
                telefono="3001234567",
                email="ventas@hazdeoros.com",
                direccion="Calle 123 #45-67, Bogotá",
                productos_que_suministra="Harina de trigo, harina integral, salvado",
                tiempo_entrega_dias=2,
                evaluacion=5
            ),
            Proveedor(
                nombre="Lacteos La Sabana",
                contacto="María González",
                telefono="3109876543", 
                email="pedidos@lacteoslasabana.com",
                direccion="Av. 68 #12-34, Medellín",
                productos_que_suministra="Leche, mantequilla, queso, crema de leche",
                tiempo_entrega_dias=1,
                evaluacion=4
            ),
            Proveedor(
                nombre="Dulces del Valle",
                contacto="Carlos Rodríguez",
                telefono="3205558888",
                email="info@dulcesdelvalle.com",
                direccion="Cr. 45 #78-90, Cali", 
                productos_que_suministra="Azúcar, panela, miel, esencias",
                tiempo_entrega_dias=3,
                evaluacion=4
            )
        ]
        
        db.session.add_all(proveedores_ejemplo)
        db.session.commit()
        print("✅ Proveedores de ejemplo creados automáticamente")
    
    # 🆕 HACER COMMIT FINAL DE TODOS LOS CAMBIOS
    db.session.commit()
    
    print("✅ Base de datos lista!")
    print(f"📁 Ubicación de la BD: {os.path.join(basedir, 'panaderia.db')}")


# Ruta para el login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        # Verificar usuario y contraseña
        if user and user.check_password(password):
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['rol'] = user.rol
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

#======COLOCA AQUÍ TODAS TUS RUTAS EXISTENTES=======
# 🆕 RUTA DE FALLBACK SEGURA
@app.route('/acceso_denegado')
@login_required
def acceso_denegado():
    return render_template('acceso_denegado.html')

# Luego modifica el decorador:
def modulo_requerido(modulo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if not current_user.puede_acceder_modulo(modulo):
                flash(f'❌ No tienes acceso al módulo {MODULOS_SISTEMA.get(modulo, modulo)}', 'error')
                return redirect(url_for('acceso_denegado'))  # ← RUTA SEGURA
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Ruta para el dashboard
@app.route('/dashboard')
@login_required
#@modulo_requerido('dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Ruta para el punto de venta
@app.route('/punto_venta')
@login_required
@modulo_requerido('punto_venta')
def punto_venta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('punto_venta.html')

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
def buscar_producto():
    """Búsqueda unificada de productos (panadería + externos) - VERSIÓN FUNCIONAL"""
    query = request.args.get('q', '').lower()
    
    try:
        resultados = []
        
        print(f"🔍 Iniciando búsqueda con query: '{query}'")
        
        # PRODUCTOS DE PANADERÍA
        productos_panaderia = Producto.query.filter(
            Producto.activo == True,
            Producto.stock_actual > 0
        ).all()
        print(f"🍞 Productos panadería encontrados: {len(productos_panaderia)}")
        
        # PRODUCTOS EXTERNOS
        productos_externos = ProductoExterno.query.filter(
            ProductoExterno.activo == True, 
            ProductoExterno.stock_actual > 0
        ).all()
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
    productos_panaderia = Producto.query.filter(
        Producto.activo == True,
        Producto.stock_actual > 0
    ).all()
    
    # Productos externos
    productos_externos = ProductoExterno.query.filter(
        ProductoExterno.activo == True, 
        ProductoExterno.stock_actual > 0
    ).all()
    
    resultado = {
        'panaderia_count': len(productos_panaderia),
        'externos_count': len(productos_externos),
        'panaderia': [{'id': p.id, 'nombre': p.nombre, 'stock': p.stock_actual} for p in productos_panaderia],
        'externos': [{'id': p.id, 'nombre': p.nombre, 'stock': p.stock_actual} for p in productos_externos]
    }
    
    return jsonify(resultado)
    
    
    # === 🆕 FUNCIONES PARA MANEJO DE CONSECUTIVOS POS ===


def obtener_consecutivo_pos():
    """
    Obtiene y incrementa automáticamente el consecutivo POS
    Si no existe, crea el registro inicial con valor 0
    """
    try:
        consecutivo = ConsecutivoPOS.query.first()
        if not consecutivo:
            # 🆕 Crear registro inicial si no existe
            consecutivo = ConsecutivoPOS(numero_actual=0)
            db.session.add(consecutivo)
            db.session.commit()
            print("✅ Registro de consecutivo POS creado inicialmente")
        
        # Incrementar consecutivo
        consecutivo.numero_actual += 1
        consecutivo.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ Consecutivo POS actualizado: {consecutivo.numero_actual}")
        return consecutivo.numero_actual
        
    except Exception as e:
        print(f"❌ Error en obtener_consecutivo_pos: {e}")
        db.session.rollback()
        # 🆕 MEJORA: Usar timestamp como fallback más único
        fallback = int(datetime.utcnow().timestamp() % 1000000)
        print(f"🔄 Usando consecutivo fallback: {fallback}")
        return fallback

def obtener_configuracion_sistema():
    """
    Obtiene la configuración del sistema desde la base de datos
    Si no existe, crea una configuración por defecto
    """
    try:
        config = ConfiguracionSistema.query.first()
        if not config:
            # Crear configuración por defecto
            config = ConfiguracionSistema(
                tipo_facturacion='POS',
                nombre_empresa='Panaderia Semillas',
                nit_empresa='9000000001',
                direccion_empresa='Cra 18 # 9-45, Atahualpa',
                telefono_empresa='+57 3189098818',
                ciudad_empresa='Pasto',
                regimen_empresa='Simplificado'
            )
            db.session.add(config)
            db.session.commit()
        return config
    except Exception as e:
        print(f"Error obteniendo configuración: {e}")
        # Retornar objeto por defecto en caso de error
        return type('ConfigDefault', (), {
            'nit_empresa': '9000000001',
            'nombre_empresa': 'Panaderia Semillas',
            'direccion_empresa': 'Cra 18 # 9-45, Atahualpa',
            'telefono_empresa': '+57 3189098818',
            'ciudad_empresa': 'Pasto'
        })()

def reiniciar_consecutivo_pos():
    """
    ⚠️ SOLO PARA PRUEBAS: Reinicia el consecutivo a 0
    """
    try:
        consecutivo = ConsecutivoPOS.query.first()
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
def registrar_venta():
    """Registrar venta con productos mixtos (panadería + externos) - VERSIÓN MEJORADA CON CLIENTES"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        data = request.get_json()
        carrito = data.get('carrito', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        cliente_id = data.get('cliente_id')  # 👈 NUEVO: Obtener cliente_id
        tipo_documento_solicitado = data.get('tipo_documento')  # 👈 NUEVO: Tipo solicitado desde frontend
        
        print(f'🛒 Datos de venta recibidos - Cliente: {cliente_id}, Tipo: {tipo_documento_solicitado}')
        
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
            consecutivo_pos = obtener_consecutivo_pos()  # 🆕 OBTENER CONSECUTIVO
            texto_legal = "Documento equivalente POS – No válido como factura electrónica de venta"
        
        # 🆕 CREAR VENTA CON NUEVOS CAMPOS
        nueva_venta = Venta(
            usuario_id=session['user_id'],
            total=0,  # Se calculará después
            metodo_pago=metodo_pago,
            cliente_id=cliente_id,  # 👈 NUEVO: Asignar cliente
            # 🆕 NUEVOS CAMPOS
            tipo_documento=tipo_documento,
            consecutivo_pos=consecutivo_pos,
            texto_legal=texto_legal
        )
        db.session.add(nueva_venta)
        db.session.flush()  # Para obtener el ID
        
        total_venta = 0
        detalles_venta = []
        
        # PROCESAR CADA PRODUCTO DEL CARRITO (TU CÓDIGO EXISTENTE CON APRENDIZAJE AUTOMÁTICO)
        for item in carrito:
            producto_id = item['id']
            cantidad = item['cantidad']
            
            # DETERMINAR SI ES PRODUCTO EXTERNO (ID > 10000)
            if producto_id > 10000:
                # Es producto externo
                producto_externo_id = producto_id - 10000
                producto = ProductoExterno.query.get(producto_externo_id)
                
                if not producto or producto.stock_actual < cantidad:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock insuficiente: {producto.nombre if producto else "Producto"}'
                    })
                
                # Actualizar stock externo
                producto.stock_actual -= cantidad
                producto.total_ventas += cantidad
                producto.total_ingresos += cantidad * producto.precio_venta
                producto.utilidad_total += cantidad * (producto.precio_venta - producto.precio_compra)
                producto.fecha_ultima_venta = datetime.utcnow()
                
                # Calcular total
                subtotal = cantidad * producto.precio_venta
                total_venta += subtotal
                
                # Crear detalle de venta
                detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=None,  # No asociado a Producto tradicional
                    producto_externo_id=producto_externo_id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )
                detalles_venta.append(detalle)
                
            else:
                # Es producto normal de panadería
                producto = Producto.query.get(producto_id)
                
                if not producto or producto.stock_actual < cantidad:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock insuficiente: {producto.nombre if producto else "Producto"}'
                    })
                
                # Actualizar stock panadería
                producto.stock_actual -= cantidad
                
                # Calcular total
                subtotal = cantidad * producto.precio_venta
                total_venta += subtotal
                
                # Crear detalle de venta
                detalle = DetalleVenta(
                    venta_id=nueva_venta.id,
                    producto_id=producto_id,
                    producto_externo_id=None,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )
                detalles_venta.append(detalle)
        
        # Actualizar total de la venta
        nueva_venta.total = total_venta
        
        # Agregar todos los detalles
        for detalle in detalles_venta:
            db.session.add(detalle)
        
        # 🆕 MODIFICAR: CREAR FACTURA O RECIBO SEGÚN CONFIGURACIÓN
        if tipo_documento == 'ELECTRONICA':
            # Para factura electrónica
            factura = Factura(
                venta_id=nueva_venta.id,
                numero_factura=f"FE{datetime.now().strftime('%Y%m%d')}{nueva_venta.id:04d}",
                subtotal=total_venta,
                iva=0,
                total=total_venta
            )
            mensaje_exito = f'Factura electrónica #{factura.numero_factura} generada'
        else:
            # Para recibo POS
            factura = Factura(
                venta_id=nueva_venta.id,
                numero_factura=f"POS{consecutivo_pos:06d}",  # 🆕 Formato POS000001
                subtotal=total_venta,
                iva=0,
                total=total_venta
            )
            mensaje_exito = f'Recibo POS #{consecutivo_pos} generado correctamente'
        
        db.session.add(factura)
        db.session.commit()
        
        # 🆕 PREPARAR RESPUESTA CON INFORMACIÓN COMPLETA
        respuesta = {
            'success': True,
            'venta_id': nueva_venta.id,
            'factura_id': factura.id,
            'numero_factura': factura.numero_factura,
            'consecutivo_pos': consecutivo_pos,
            'tipo_documento': tipo_documento,
            'total': total_venta,
            'mensaje': mensaje_exito
        }
        
        # 🆕 AGREGAR INFORMACIÓN DEL CLIENTE SI EXISTE
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            if cliente:
                respuesta['cliente'] = cliente.to_dict()
                print(f'✅ Cliente incluido en respuesta: {cliente.nombre}')
        
        # 🆕 LIMPIAR CARRITO DESPUÉS DE VENTA EXITOSA
        if 'carrito' in session:
            session.pop('carrito')
            session.modified = True
        
        print(f'✅ Venta registrada exitosamente - ID: {nueva_venta.id}, Tipo: {tipo_documento}, Cliente: {cliente_id}')
        
        return jsonify(respuesta)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al registrar venta: {e}")
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
            cliente_existente.fecha_actualizacion = datetime.utcnow()
            
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
            ahora=datetime.utcnow()
        )
        
    except Exception as e:
        flash(f'❌ Error generando factura: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ventas'))
    
@app.route('/recibo-pos/<int:venta_id>')
@login_required
@modulo_requerido('punto_venta')
def recibo_pos(venta_id):
    """
    🆕 Genera el recibo POS para impresión térmica
    """
    try:
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
        config = obtener_configuracion_sistema()
        
        return render_template('recibo_pos.html', 
                             venta=venta, 
                             detalles=detalles, 
                             config=config)
                             
    except Exception as e:
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
# RUTAS DE PROVEEDORES
# =============================================

@app.route('/proveedores')
@login_required
@modulo_requerido('proveedores')
def proveedores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    todos_proveedores = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=todos_proveedores)

@app.route('/agregar_proveedor', methods=['GET', 'POST'])
@login_required
@modulo_requerido('proveedores')
def agregar_proveedor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            nuevo_proveedor = Proveedor(
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
            
            flash(f'Proveedor "{nuevo_proveedor.nombre}" agregado correctamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            flash('Error al agregar el proveedor', 'error')
            return redirect(url_for('agregar_proveedor'))
    
    return render_template('agregar_proveedor.html')

@app.route('/editar_proveedor/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('proveedores')
def editar_proveedor(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    proveedor = Proveedor.query.get_or_404(id)
    
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
            flash(f'Proveedor "{proveedor.nombre}" actualizado correctamente', 'success')
            return redirect(url_for('proveedores'))
            
        except Exception as e:
            flash('Error al actualizar el proveedor', 'error')
            return redirect(url_for('editar_proveedor', id=id))
    
    return render_template('editar_proveedor.html', proveedor=proveedor)

@app.route('/toggle_proveedor/<int:id>')
@login_required
@modulo_requerido('proveedores')
def toggle_proveedor(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    proveedor = Proveedor.query.get_or_404(id)
    proveedor.activo = not proveedor.activo
    db.session.commit()
    
    estado = "activado" if proveedor.activo else "desactivado"
    flash(f'Proveedor "{proveedor.nombre}" {estado} correctamente', 'success')
    return redirect(url_for('proveedores'))


# =============================================
# RUTAS DE PRODUCTOS EXTERNOS
# =============================================

@app.route('/productos_externos')
@login_required
@modulo_requerido('productos')
def productos_externos():
    """Gestión de productos externos (bebidas, helados)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    productos = ProductoExterno.query.filter_by(activo=True).all()
    proveedores = Proveedor.query.filter_by(activo=True).all()
    
    # Calcular métricas adicionales para cada producto
    for producto in productos:
        producto.utilidad_unitaria = producto.precio_venta - producto.precio_compra
        producto.margen_ganancia = (producto.utilidad_unitaria / producto.precio_compra * 100) if producto.precio_compra > 0 else 0
    
    return render_template('productos_externos.html', 
                         productos=productos, 
                         proveedores=proveedores)


@app.route('/registrar_compra_externa', methods=['POST'])
@login_required
@modulo_requerido('productos')
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
        
        producto = ProductoExterno.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Registrar la compra
        compra = CompraExterna(
            producto_id=producto_id,
            proveedor_id=proveedor_id,
            cantidad=cantidad,
            precio_compra=precio_compra,
            total_compra=cantidad * precio_compra,
            notas=notas
        )
        
        # Actualizar stock y precios del producto
        producto.stock_actual += cantidad
        producto.precio_compra = precio_compra  # Actualizar último precio de compra
        producto.fecha_ultima_compra = datetime.utcnow()
        
        db.session.add(compra)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Compra registrada: {cantidad} unidades de {producto.nombre}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/editar_producto_externo/<int:producto_id>', methods=['POST'])
@login_required
@modulo_requerido('productos')
def editar_producto_externo(producto_id):
    """Editar producto externo existente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        producto = ProductoExterno.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        producto.nombre = request.form['nombre']
        producto.categoria = request.form['categoria']
        producto.marca = request.form.get('marca', '')
        producto.descripcion = request.form.get('descripcion', '')
        producto.codigo_barras = request.form.get('codigo_barras', '')
        producto.proveedor_id = request.form.get('proveedor_id')
        producto.precio_venta = float(request.form['precio_venta'])
        producto.stock_minimo = int(request.form.get('stock_minimo', 5))
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Producto "{producto.nombre}" actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/eliminar_producto_externo/<int:producto_id>')
@login_required
@modulo_requerido('productos')
def eliminar_producto_externo(producto_id):
    """Eliminar producto externo (soft delete)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    producto = ProductoExterno.query.get(producto_id)
    if producto:
        producto.activo = False
        db.session.commit()
        flash(f'Producto "{producto.nombre}" eliminado exitosamente', 'success')
    
    return redirect(url_for('productos_externos'))

# =============================================
# RUTAS DE MATERIAS PRIMAS - COMPLETAMENTE ACTUALIZADAS
# =============================================

@app.route('/materias_primas')
@login_required
@modulo_requerido('inventario')
def materias_primas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todas las materias primas (activas e inactivas)
    materias = MateriaPrima.query.all()
    
    # CALCULAR FECHAS PARA ALERTAS DE VENCIMIENTO
    hoy = datetime.now().date()
    hoy_mas_15 = hoy + timedelta(days=15)
    
    return render_template('materias_primas.html', 
                         materias_primas=materias,
                         hoy=hoy,
                         hoy_mas_15=hoy_mas_15)

@app.route('/agregar_materia_prima', methods=['GET', 'POST'])
@login_required
@modulo_requerido('inventario')
def agregar_materia_prima():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    
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
                activo=True
            )
            
            db.session.add(nueva_materia)
            db.session.flush()  # Para obtener el ID
            
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
def editar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    proveedores = Proveedor.query.filter_by(activo=True).all()
    
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
                materia.fecha_ultima_actualizacion = datetime.utcnow()
                
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
def desactivar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    materia.activo = False
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" desactivada correctamente', 'success')
    return redirect(url_for('materias_primas'))

@app.route('/activar_materia_prima/<int:id>')
@login_required
@modulo_requerido('inventario')
def activar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    materia.activo = True
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" activada correctamente', 'success')
    return redirect(url_for('materias_primas'))

# NUEVA RUTA PARA VER HISTORIAL DE COMPRAS
@app.route('/historial_compras/<int:materia_prima_id>')
@login_required
@modulo_requerido('inventario')
def historial_compras(materia_prima_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(materia_prima_id)
    historial = HistorialCompra.query.filter_by(materia_prima_id=materia_prima_id).order_by(HistorialCompra.fecha_compra.desc()).all()
    
    return render_template('historial_compras.html', materia=materia, historial=historial)

# =============================================
# RUTAS DE PRODUCCIÓN Y RECETAS - COMPLETAMENTE ACTUALIZADAS CON PRECIOS REALES
# =============================================
@app.route('/recetas')
@login_required
@modulo_requerido('produccion')
def recetas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    todas_recetas = Receta.query.all()
    return render_template('recetas.html', recetas=todas_recetas)

@app.route('/detalle_receta/<int:id>')
@login_required
@modulo_requerido('produccion')
def detalle_receta(id):
    """Página de detalle de una receta específica"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receta = Receta.query.get_or_404(id)
    return render_template('detalle_receta.html', receta=receta)

@app.route('/producir_receta/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
def producir_receta(id):
    """Producción de una receta - cálculo de ingredientes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receta = Receta.query.get_or_404(id)
    
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
                fecha_inicio=datetime.utcnow()
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
                    tipo_movimiento='produccion'
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
def calcular_ingredientes(id):
    """API para calcular ingredientes necesarios (AJAX)"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    receta = Receta.query.get_or_404(id)
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
@app.route('/api/actualizar_precio_real/<int:receta_id>', methods=['POST'])
@login_required
@modulo_requerido('produccion')
def actualizar_precio_real(receta_id):
    """API para actualizar el precio real de una receta desde la lista"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    receta = Receta.query.get_or_404(receta_id)
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
                materia_prima = MateriaPrima.query.get(materia_prima_id)
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
def crear_receta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # VERIFICAR QUE HAY MATERIAS PRIMAS DISPONIBLES
    materias_primas = MateriaPrima.query.filter_by(activo=True).all()
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
                precio_venta_real=precio_venta_real  # ✅ ASIGNAR PRECIO REAL
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
                
                materia_prima = MateriaPrima.query.get(materia_prima_id)
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
                categoria_id=obtener_categoria_id(nueva_receta.categoria),
                precio_venta=precio_venta_real if precio_venta_real > 0 else precio_venta_unitario,
                stock_actual=0,  # Inicialmente sin stock - se llena con producción
                stock_minimo=10,
                codigo_barras=f"PROD{nueva_receta.id:06d}",
                tipo_producto='produccion',
                es_pan=True if 'pan' in nueva_receta.nombre.lower() else False,
                receta_id=nueva_receta.id,
                activo=True
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

# ✅ NUEVA FUNCIÓN HELPER - AGREGAR ESTA FUNCIÓN EN app.py
def obtener_categoria_id(nombre_categoria):
    """Obtiene el ID de categoría basado en el nombre - crea si no existe"""
    # Normalizar nombre de categoría
    nombre_categoria = nombre_categoria.strip().title()
    
    categoria = Categoria.query.filter_by(nombre=nombre_categoria).first()
    if not categoria:
        # Crear categoría si no existe
        categoria = Categoria(nombre=nombre_categoria)
        db.session.add(categoria)
        db.session.commit()
        print(f"✅ Nueva categoría creada: {nombre_categoria}")
    
    return categoria.id

# ✅ RUTA MEJORADA PARA EDITAR RECETAS EXISTENTES
@app.route('/editar_receta/<int:id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
def editar_receta(id):
    """Editar una receta existente - AHORA CON PRECIO REAL"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receta = Receta.query.get_or_404(id)
    materias_primas = MateriaPrima.query.filter_by(activo=True).all()
    
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
                
                materia_prima = MateriaPrima.query.get(materia_prima_id)
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
def produccion_diaria():
    """Dashboard principal de producción diaria - ACTUALIZADO"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todas las recetas activas
    recetas_activas = Receta.query.filter_by(activo=True).all()
    
    recetas_con_stock = []
    alertas = []
    
    for receta in recetas_activas:
        # Calcular stock actual
        stock_actual = calcular_stock_vitrina(receta.id)
        
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
        
        # ✅ USAR STOCK MÍNIMO PERSONALIZADO
        stock_minimo_personalizado = config.stock_minimo
        
        # Calcular ventas del día actual
        hoy = datetime.now().date()
        ventas_hoy = calcular_ventas_hoy(receta.nombre, hoy)
        
        # Proyección de agotamiento (mejorada)
        proyeccion_horas = None
        if config.rotacion_diaria_esperada > 0 and stock_actual > 0:
            horas_restantes = (stock_actual / config.rotacion_diaria_esperada) * 24
            if horas_restantes < 168:  # Mostrar si es menos de 7 días
                proyeccion_horas = int(horas_restantes)
        
        # ✅ GENERAR ALERTAS MEJORADAS
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
            'stock_minimo': stock_minimo_personalizado,  # ✅ PERSONALIZADO
            'stock_maximo': config.stock_maximo,
            'ventas_hoy': ventas_hoy,
            'proyeccion_horas': proyeccion_horas,
            'rotacion_esperada': config.rotacion_diaria_esperada,
            'config': config  # ✅ Pasar configuración completa
        })
    
    # Obtener órdenes de producción activas (código existente)
    ordenes_activas = OrdenProduccion.query.filter(
        OrdenProduccion.estado.in_(['PENDIENTE', 'EN_PRODUCCION'])
    ).order_by(OrdenProduccion.fecha_produccion.desc()).limit(10).all()
    
    # ✅ Obtener órdenes completadas del día para el historial
    hoy = datetime.now().date()
    ordenes_completadas_hoy_db = OrdenProduccion.query.filter(
        OrdenProduccion.estado == 'COMPLETADA',
        db.func.date(OrdenProduccion.fecha_fin) == hoy
    ).all()
    
    return render_template('produccion_diaria.html',
                         recetas_con_stock=recetas_con_stock,
                         ordenes_activas=ordenes_activas,
                         todas_las_ordenes_completadas=ordenes_completadas_hoy_db,
                         alertas=alertas)
    
# ✅ NUEVA RUTA: Configuración personalizada de stock por producto
@app.route('/configurar_stock_producto/<int:receta_id>', methods=['GET', 'POST'])
@login_required
@modulo_requerido('produccion')
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
            config.fecha_actualizacion = datetime.utcnow()
            
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
            config.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            flash(f'✅ Configuración de stock para "{receta.nombre}" actualizada', 'success')
            return redirect(url_for('produccion_diaria'))
            
        except Exception as e:
            flash(f'❌ Error al actualizar configuración: {str(e)}', 'error')
    
    return render_template('configurar_stock.html', receta=receta, config=config)

# ✅ NUEVO: API para obtener configuración de stock
@app.route('/api/configuracion_stock/<int:receta_id>')
@login_required
@modulo_requerido('produccion')
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
def ordenar_produccion():
    """Crear nueva orden de producción desde el dashboard"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        receta_id = request.form.get('receta_id', type=int)
        cantidad = request.form.get('cantidad', type=int)
        
        if not receta_id or not cantidad or cantidad <= 0:
            return jsonify({'error': 'Datos inválidos'}), 400
        
        # Crear orden de producción
        nueva_orden = OrdenProduccion(
            receta_id=receta_id,
            cantidad_producir=cantidad,
            estado='PENDIENTE',
            usuario_id=session['user_id']
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
def iniciar_produccion(orden_id):
    """Iniciar una orden de producción - Cambia estado a EN_PRODUCCION"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        orden = OrdenProduccion.query.get_or_404(orden_id)
        
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
def confirmar_produccion(orden_id):
    """Confirmar producción completada - Actualiza stock y descuenta ingredientes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        orden = OrdenProduccion.query.get_or_404(orden_id)
        
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
def cancelar_orden_produccion(orden_id):
    """Cancelar una orden de producción"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        orden = OrdenProduccion.query.get_or_404(orden_id)
        
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
def reporte_produccion_diaria():
    """Reporte imprimible de producción diaria"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    hoy = datetime.now().date()
    
    # Órdenes completadas hoy
    ordenes_hoy = OrdenProduccion.query.filter(
        OrdenProduccion.estado == 'COMPLETADA',
        db.func.date(OrdenProduccion.fecha_fin) == hoy
    ).all()
    
    # Stock actual
    recetas_activas = Receta.query.filter_by(activo=True).all()
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

@app.route('/api/verificar_stock/<int:producto_id>')
@login_required
@modulo_requerido('punto_venta')
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
                                ahora=datetime.utcnow())
        else:
            # Usar template de recibo POS tradicional
            return render_template('recibo_pos.html',
                                venta=venta,
                                detalles=detalles,
                                config=config,
                                ahora=datetime.utcnow())
        
    except Exception as e:
        flash(f'❌ Error generando documento: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ventas'))
    
# En app.py - NUEVAS RUTAS PARA PRODUCTOS EXTERNOS

@app.route('/agregar_producto_externo', methods=['POST'])
@login_required
@modulo_requerido('productos')
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
        
        # Verificar si el código de barras ya existe
        if codigo_barras:
            producto_existente = ProductoExterno.query.filter_by(codigo_barras=codigo_barras).first()
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
def reporte_inventario_externo():
    """Reporte completo de inventario de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    productos = ProductoExterno.query.filter_by(activo=True).all()
    
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
    
    return render_template('reporte_inventario_externo.html',
                         productos=productos,
                         total_valor_inventario=total_valor_inventario,
                         productos_stock_bajo=productos_stock_bajo,
                         total_productos=len(productos))

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
def reporte_ventas_externas():
    """Reporte de ventas y rentabilidad de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Parámetros de fecha (opcionales)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Consulta base de detalles de venta de productos externos
    query = DetalleVenta.query.join(ProductoExterno).filter(
        DetalleVenta.producto_externo_id.isnot(None)
    )
    
    # Filtrar por fechas si se proporcionan
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.join(Venta).filter(
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
    
    detalles_venta = DetalleVenta.query.join(ProductoExterno).filter(
        DetalleVenta.producto_externo_id.isnot(None)
    ).all()
    
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
    
    # Preparar datos de la tabla - CORREGIDO (cambiar nombre de variable)
    table_data = [['Producto', 'Categoría', 'Unidades', 'Ingresos', 'Costo', 'Utilidad', 'Margen %']]  # ← Cambié 'data' por 'table_data'
    
    for venta_data in ventas_por_producto.values():  # ← Cambié 'data' por 'venta_data'
        utilidad = venta_data['ingresos'] - venta_data['costo']
        margen = (utilidad / venta_data['ingresos'] * 100) if venta_data['ingresos'] > 0 else 0
        
        table_data.append([  # ← Usar 'table_data' en lugar de 'data'
            venta_data['producto'].nombre,
            venta_data['producto'].categoria,
            str(venta_data['cantidad']),
            f"${venta_data['ingresos']:,.0f}",
            f"${venta_data['costo']:,.0f}",
            f"${utilidad:,.0f}",
            f"{margen:.1f}%"
        ])
    
    # Crear tabla
    table = Table(table_data)  # ← Usar 'table_data'
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
def dashboard_externos():
    """Dashboard ejecutivo de productos externos"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Métricas generales
    total_productos = ProductoExterno.query.filter_by(activo=True).count()
    productos_stock_bajo = ProductoExterno.query.filter(
        ProductoExterno.stock_actual <= ProductoExterno.stock_minimo,
        ProductoExterno.activo == True
    ).count()
    
    # Valor total del inventario
    productos = ProductoExterno.query.filter_by(activo=True).all()
    valor_inventario = sum(p.stock_actual * p.precio_compra for p in productos)
    
    # Ventas del último mes
    un_mes_atras = datetime.utcnow() - timedelta(days=30)

    ventas_recientes = DetalleVenta.query.join(ProductoExterno).join(Venta).filter(
        DetalleVenta.producto_externo_id.isnot(None),
        Venta.fecha_hora >= un_mes_atras
    ).all()

    ingresos_ultimo_mes = sum(d.cantidad * d.precio_unitario for d in ventas_recientes)
    utilidad_ultimo_mes = sum(d.cantidad * (d.producto_externo.precio_venta - d.producto_externo.precio_compra) for d in ventas_recientes)

    # ← AGREGA ESTA LÍNEA FALTANTE ↓
    margen_promedio = (utilidad_ultimo_mes / ingresos_ultimo_mes * 100) if ingresos_ultimo_mes > 0 else 0

    # Productos más vendidos (top 5) - CORREGIDO
    top_productos = db.session.query(
        ProductoExterno,
        db.func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).filter(
        DetalleVenta.producto_externo_id.isnot(None)
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
    cierre_hoy = CierreDiario.query.filter_by(fecha=hoy).first()
    
    return jsonify({
        'fecha': hoy.isoformat(),
        'jornada_activa': jornada.estado == 'ACTIVA',
        'total_ventas_hoy': total_hoy,
        'total_transacciones': len(ventas_hoy),
        'cierre_realizado': cierre_hoy is not None,
        'hora_actual': datetime.now().strftime('%H:%M')
    })

@app.route('/api/cierre_diario/procesar', methods=['POST'])
@login_required
@modulo_requerido('finanzas')
def procesar_cierre_diario():
    """API para procesar el cierre diario"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        cierre, mensaje = cerrar_jornada_actual()
        
        if cierre:
            return jsonify({
                'success': True,
                'mensaje': mensaje,
                'cierre': {
                    'fecha': cierre.fecha.isoformat(),
                    'total_ventas': cierre.total_ventas,
                    'total_transacciones': cierre.total_transacciones,
                    'tendencia': cierre.tendencia
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar cierre: {str(e)}'
        }), 500

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

@app.route('/cierre_diario')
@login_required
@modulo_requerido('finanzas')
def pagina_cierre_diario():
    """Página de cierre diario"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    hoy = datetime.now().date()
    cierre_hoy = CierreDiario.query.filter_by(fecha=hoy).first()
    ventas_hoy = obtener_ventas_dia(hoy)
    
    return render_template('cierre_diario.html',
                         cierre_hoy=cierre_hoy,
                         ventas_hoy=ventas_hoy,
                         hoy=hoy)

# =============================================
# RUTAS DE REPORTES PDF CON APRENDIZAJE AUTOMÁTICO
# =============================================

@app.route('/reporte/cierre_caja')
@login_required
@modulo_requerido('reportes')
def reporte_cierre_caja():
    """Reporte de cierre de caja con análisis automático"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    fecha = request.args.get('fecha', datetime.now().date().isoformat())
    
    try:
        # Obtener ventas del día
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        inicio_dia = datetime.combine(fecha_obj, datetime.min.time())
        fin_dia = datetime.combine(fecha_obj, datetime.max.time())
        
        ventas_dia = Venta.query.filter(
            Venta.fecha_hora >= inicio_dia,
            Venta.fecha_hora <= fin_dia
        ).all()
        
        # Calcular métricas
        total_ventas = sum(venta.total for venta in ventas_dia)
        ventas_por_metodo = {}
        
        for venta in ventas_dia:
            if venta.metodo_pago not in ventas_por_metodo:
                ventas_por_metodo[venta.metodo_pago] = 0
            ventas_por_metodo[venta.metodo_pago] += venta.total
        
        # Obtener comparativa con día anterior
        dia_anterior = fecha_obj - timedelta(days=1)
        ventas_dia_anterior = Venta.query.filter(
            db.func.date(Venta.fecha_hora) == dia_anterior
        ).all()
        
        total_dia_anterior = sum(venta.total for venta in ventas_dia_anterior)
        
        # Calcular tendencia
        if total_dia_anterior > 0:
            tendencia = ((total_ventas - total_dia_anterior) / total_dia_anterior) * 100
        else:
            tendencia = 100 if total_ventas > 0 else 0
        
        # Productos más vendidos del día
        detalles_dia = DetalleVenta.query.join(Venta).filter(
            Venta.fecha_hora >= inicio_dia,
            Venta.fecha_hora <= fin_dia
        ).all()
        
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
        
        return render_template('cierre_caja.html',
                            fecha=fecha_obj,
                            total_ventas=total_ventas,
                            ventas_por_metodo=ventas_por_metodo,
                            tendencia=tendencia,
                            total_dia_anterior=total_dia_anterior,
                            productos_top=productos_top,
                            total_transacciones=len(ventas_dia))
    
    except Exception as e:
        flash(f'Error generando reporte: {str(e)}', 'error')
        return redirect(url_for('punto_venta'))

@app.route('/reporte/ventas')
@login_required
@modulo_requerido('reportes')
def reporte_ventas():
    """Reporte de ventas por período con análisis predictivo"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener parámetros de fecha o usar valores por defecto
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    periodo = request.args.get('periodo', 'semana')  # Cambiado a 'semana' como default
    
    hoy = datetime.now().date()
    
    if fecha_inicio_str and fecha_fin_str:
        # Usar fechas proporcionadas por el usuario
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        periodo = 'personalizado'
    else:
        # Valores por defecto (últimos 7 días)
        fecha_fin = hoy
        fecha_inicio = fecha_fin - timedelta(days=7)
        periodo = 'semana'
    
    # Validar que fecha_inicio no sea mayor que fecha_fin
    if fecha_inicio > fecha_fin:
        flash('La fecha de inicio no puede ser mayor que la fecha fin', 'error')
        fecha_inicio = fecha_fin - timedelta(days=7)
    
    # Obtener ventas del período
    ventas_periodo = Venta.query.filter(
        db.func.date(Venta.fecha_hora) >= fecha_inicio,
        db.func.date(Venta.fecha_hora) <= fecha_fin
    ).all()
    
    # Calcular métricas avanzadas
    total_ventas = sum(venta.total for venta in ventas_periodo)
    promedio_venta = total_ventas / len(ventas_periodo) if ventas_periodo else 0
    
    # Análisis de tendencia usando ML
    tendencia = calcular_tendencia_ventas(fecha_inicio, fecha_fin)
    
    # Productos más vendidos del período
    detalles_periodo = DetalleVenta.query.join(Venta).filter(
        db.func.date(Venta.fecha_hora) >= fecha_inicio,
        db.func.date(Venta.fecha_hora) <= fecha_fin
    ).all()
    
    productos_analisis = analizar_productos_periodo(detalles_periodo)
    
    return render_template('ventas_periodo.html',
                         periodo=periodo,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         total_ventas=total_ventas,
                         promedio_venta=promedio_venta,
                         tendencia=tendencia,
                         productos_analisis=productos_analisis,
                         total_transacciones=len(ventas_periodo),
                         datetime=datetime)  # Añadido para usar en templates

@app.route('/reporte/productos_populares')
@login_required
@modulo_requerido('reportes')
def reporte_productos_populares():
    """Reporte de productos más vendidos con análisis de rotación"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener parámetros de fecha o usar valores por defecto
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if fecha_inicio_str and fecha_fin_str:
        # Usar fechas proporcionadas por el usuario
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        # Valores por defecto (últimos 30 días)
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Actualizar rotaciones automáticas antes de generar reporte
    actualizaciones = actualizar_rotaciones_automaticas()
    
    # Obtener productos más vendidos del período
    detalles = DetalleVenta.query.join(Venta).filter(
        Venta.fecha_hora >= fecha_inicio,
        Venta.fecha_hora <= fecha_fin
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
    for producto in productos_ordenados[:20]:  # Top 20
        rotacion = calcular_rotacion_automatica_por_nombre(producto['nombre'])
        producto['rotacion_promedio'] = rotacion
    
    return render_template('productos_populares.html',
                         productos=productos_ordenados[:20],
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         actualizaciones_ml=actualizaciones,
                         datetime=datetime)  # ← ¡ESTO ES LO QUE FALTA!

@app.route('/reporte/analisis_predictivo')
@login_required
@modulo_requerido('reportes')
def reporte_analisis_predictivo():
    """Reporte de análisis predictivo con recomendaciones ML"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener datos para análisis predictivo
    productos_analisis = []
    recetas_activas = Receta.query.filter_by(activo=True).all()
    
    for receta in recetas_activas:
        if receta.producto:
            # Calcular proyecciones usando ML
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
    
    # Alertas inteligentes
    alertas = generar_alertas_inteligentes()
    
    return render_template('analisis_predictivo.html',
                     productos_analisis=productos_analisis,
                     alertas=alertas,
                     fecha_analisis=datetime.now().date(),
                     datetime=datetime)  # ¡Importante! Pasar datetime al template
    

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

def actualizar_saldo_automatico(efectivo=0, transferencias=0, pagos=0, accion_efectivo="depositar"):
    """
    Actualizar saldo automáticamente considerando ingresos y egresos
    - transferencias: dinero que ENTRA a la cuenta
    - pagos: dinero que SALE de la cuenta
    - efectivo: depende de la acción seleccionada
    """
    try:
        saldo_actual_obj = SaldoBanco.query.order_by(SaldoBanco.fecha_actualizacion.desc()).first()
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
        
        # Crear nuevo registro de saldo
        nuevo_registro_saldo = SaldoBanco(
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
        
        # Verificar si ya existe registro para esta fecha
        registro_existente = RegistroDiario.query.filter_by(fecha=fecha).first()
        
        if registro_existente:
            # Actualizar registro existente
            registro = registro_existente
        else:
            # Crear nuevo registro
            registro = RegistroDiario(fecha=fecha)
        
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
def control_diario():
    """Vista principal del control financiero diario"""
    from datetime import datetime, date
    
    # Obtener saldo actual
    saldo_banco = SaldoBanco.query.order_by(SaldoBanco.fecha_actualizacion.desc()).first()
    saldo_actual = saldo_banco.saldo_actual if saldo_banco else 0
    
    # Obtener registros recientes (últimos 7 días)
    registros_recientes = RegistroDiario.query.order_by(RegistroDiario.fecha.desc()).limit(7).all()
    
    # Obtener proveedores para el dropdown
    proveedores = Proveedor.query.all()
    
    # Obtener pagos de hoy
    hoy = date.today()
    pagos_hoy = PagoIndividual.query.filter_by(fecha_pago=hoy).all()
    registro_hoy = RegistroDiario.query.filter_by(fecha=hoy).first()
    
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
        
        # Crear nuevo pago
        nuevo_pago = PagoIndividual(
            categoria=categoria,
            proveedor_id=proveedor_id,
            monto=monto,
            fecha_pago=fecha_pago,
            referencia=referencia,
            descripcion=descripcion,
            numero_factura=numero_factura
        )
        
        db.session.add(nuevo_pago)
        
        # 🆕 ACTUALIZAR SALDO - RESTAR EL PAGO
        saldo_actual = actualizar_saldo_automatico(
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
def registrar_cierre_caja():
    """Registrar el cierre de caja diario con validaciones de seguridad"""
    try:
        from datetime import datetime
        
        # Obtener datos del formulario con sanitización
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        venta_total = sanitizar_numero(request.form.get('venta_total', 0))
        efectivo = sanitizar_numero(request.form.get('efectivo', 0))
        transferencias = sanitizar_numero(request.form.get('transferencias', 0))
        tarjetas = sanitizar_numero(request.form.get('tarjetas', 0))
        accion_efectivo = request.form.get('accion_efectivo', 'depositar')
        
        # 🔒 VALIDACIÓN CRÍTICA: Verificar que la suma coincida con el total
        suma_metodos = efectivo + transferencias + tarjetas
        diferencia = abs(suma_metodos - venta_total)
        
        if diferencia > 1:
            if suma_metodos > venta_total:
                flash(f'❌ El total ingresado en métodos de pago (${suma_metodos:,.0f}) es SUPERIOR al total de ventas (${venta_total:,.0f}). Diferencia: +${diferencia:,.0f}', 'error')
            else:
                flash(f'❌ El total ingresado en métodos de pago (${suma_metodos:,.0f}) es INFERIOR al total de ventas (${venta_total:,.0f}). Diferencia: -${diferencia:,.0f}', 'error')
            return redirect(url_for('control_diario'))
        
        # Verificar si ya existe registro para esta fecha
        registro_existente = RegistroDiario.query.filter_by(fecha=fecha).first()
        
        if registro_existente:
            registro = registro_existente
        else:
            registro = RegistroDiario(fecha=fecha)
        
        # Actualizar datos de ingresos
        registro.venta_total = venta_total
        registro.efectivo = efectivo
        registro.transferencias = transferencias
        registro.tarjetas = tarjetas
        
        # Calcular totales automáticamente
        registro.calcular_totales()
        
        if not registro_existente:
            db.session.add(registro)
        
        # 🆕 ACTUALIZAR SALDO - SOLO INGRESOS (no pagos aquí)
        saldo_actual = actualizar_saldo_automatico(
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
    
    return redirect(url_for('control_diario'))

# ... todo tu código existente ...

# ================================================== MÓDULO DE REPORTES ====================================================

from reportes import GeneradorReportes
from io import BytesIO

@app.route('/reportes')
@login_required
@modulo_requerido('reportes')
def reportes():
    """Vista principal de reportes"""
    return render_template('reportes.html')

@app.route('/generar_reporte_estado_resultados')
@login_required
@modulo_requerido('reportes')
def generar_reporte_estado_resultados():
    """Genera reporte de Estado de Resultados en PDF"""
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
        pdf_buffer = generador.generar_reporte_estado_resultados(fecha_inicio, fecha_fin)
        
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
print("🔍 Verificando métodos de GeneradorReportes...")
generador_test = GeneradorReportes()
metodos = [method for method in dir(generador_test) if callable(getattr(generador_test, method)) and not method.startswith('_')]
print("📋 Métodos disponibles:", metodos)

@app.route('/generar_reporte_analisis_gastos')
@login_required
@modulo_requerido('reportes')
def generar_reporte_analisis_gastos():
    """Genera reporte de Análisis de Gastos por Categoría en PDF"""
    try:
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
        pdf_buffer = generador.generar_reporte_analisis_gastos(fecha_inicio, fecha_fin)
        
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

# Verificación temporal de métodos
def verificar_metodos():
    generador = GeneradorReportes()
    metodos = [method for method in dir(generador) if callable(getattr(generador, method)) and not method.startswith('_')]
    print("🔍 Métodos disponibles en GeneradorReportes:", metodos)

# Ejecutar verificación (esto se mostrará en la terminal de Flask al iniciar)
verificar_metodos()

#==========================================================Tendencia de Ventas==============================================

@app.route('/generar_reporte_tendencia_ventas')
@login_required
@modulo_requerido('reportes')
def generar_reporte_tendencia_ventas():
    """Genera reporte de Tendencia de Ventas en PDF"""
    try:
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
        pdf_buffer = generador.generar_reporte_tendencia_ventas(fecha_inicio, fecha_fin)
        
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
def generar_reporte_ia_predictivo():
    """Genera reporte de IA Predictivo en PDF"""
    try:
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
        pdf_buffer = generador.generar_reporte_ia_predictivo(fecha_inicio, fecha_fin)
        
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
def generar_reporte_analisis_inventarios():
    """Genera reporte de Análisis de Inventarios en PDF"""
    try:
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
        pdf_buffer = generador.generar_reporte_analisis_inventarios(fecha_inicio, fecha_fin)
        
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
    
# ============================================ MODELO DE ACTIVOS FIJOS ========================================================

# === RUTAS DE ACTIVOS FIJOS ===

@app.route('/activos_fijos')
@login_required
@modulo_requerido('activos')
def activos_fijos():
    activos = ActivoFijo.query.all()
    
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
@modulo_requerido('activos')
def registrar_activo():
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
            
            flash('Activo registrado exitosamente', 'success')
            return redirect(url_for('activos_fijos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar activo: {str(e)}', 'error')
    
    return render_template('registrar_activo.html', categorias=CATEGORIAS_ACTIVOS)

@app.route('/lista_activos')
@login_required
@modulo_requerido('activos')
def lista_activos():
    activos = ActivoFijo.query.order_by(ActivoFijo.fecha_compra.desc()).all()
    return render_template('lista_activos.html', activos=activos, categorias=CATEGORIAS_ACTIVOS)

@app.route('/reporte_activos')
@login_required
@modulo_requerido('activos')
def reporte_activos():
    activos = ActivoFijo.query.all()
    
    # Generar gráficos si hay activos
    if activos:
        try:
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
            
            # Guardar gráfico
            graph_path = os.path.join('static', 'temp', 'activos_report.png')
            os.makedirs(os.path.dirname(graph_path), exist_ok=True)
            plt.savefig(graph_path)
            plt.close()
            
        except Exception as e:
            print(f"Error generando gráficos: {e}")
            graph_path = None
    else:
        graph_path = None
    
    return render_template('reporte_activos.html', 
                         activos=activos, 
                         graph_path=graph_path,
                         total_valor=sum(activo.valor_actual() for activo in activos),
                         total_depreciacion=sum(activo.depreciacion_acumulada() for activo in activos),
                         now=datetime.now(),
                         categorias=CATEGORIAS_ACTIVOS)

@app.route('/api/activos_metrics')
@login_required
@modulo_requerido('activos')
def api_activos_metrics():
    activos = ActivoFijo.query.all()
    
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
@permisos_requeridos('usuarios', 'gestionar')   
def gestion_usuarios():
    """Página principal de gestión de usuarios"""
    usuarios = Usuario.query.all()
    return render_template('gestion_usuarios.html', usuarios=usuarios)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
@permisos_requeridos('usuarios', 'gestionar')
def crear_usuario():
    """Crear nuevo usuario"""
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
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                username=username,
                nombre_completo=nombre_completo,
                email=email,
                telefono=telefono,
                rol=rol
            )
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash(f'✅ Usuario {username} creado exitosamente', 'success')
            return redirect(url_for('gestion_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear usuario: {str(e)}', 'error')
    
    return render_template('crear_usuario.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

