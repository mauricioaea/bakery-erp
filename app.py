import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Usuario, Producto, Venta, DetalleVenta, MateriaPrima, Receta, Categoria, Proveedor, HistorialCompra
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Obtener la ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configurar la base de datos en la carpeta principal
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'panaderia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta_muy_segura_panaderia_2025'

db.init_app(app)

# Crear las tablas y un usuario admin por defecto
with app.app_context():
    db.create_all()
    # Verificar si ya existe un usuario admin
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = generate_password_hash('admin123')
        admin_user = Usuario(username='admin', password_hash=hashed_password, rol='admin')
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Usuario admin creado: usuario: admin, contraseña: admin123")
    
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
    
    print("✅ Base de datos lista!")
    print(f"📁 Ubicación de la BD: {os.path.join(basedir, 'panaderia.db')}")

# Ruta para el login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['rol'] = user.rol
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Ruta para el punto de venta
@app.route('/punto_venta')
def punto_venta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('punto_venta.html')

# Ruta para buscar productos (API)
@app.route('/buscar_producto')
def buscar_producto():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    query = request.args.get('q', '').lower()
    productos = Producto.query.filter(Producto.activo == True).all()
    resultados = []
    for producto in productos:
        if query in producto.nombre.lower() or query in producto.codigo_barras.lower():
            resultados.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio_venta,
                'codigo_barras': producto.codigo_barras
            })
    return jsonify(resultados)

# Ruta para registrar la venta (checkout)
@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    carrito = data.get('carrito', [])
    metodo_pago = data.get('metodo_pago', 'efectivo')
    
    if not carrito:
        return jsonify({'error': 'El carrito está vacío'}), 400

    # Calcular total
    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    # Crear la venta
    nueva_venta = Venta(
        total=total,
        metodo_pago=metodo_pago,
        usuario_id=session['user_id']
    )
    db.session.add(nueva_venta)
    db.session.flush()  # Para obtener el ID de la venta

    # Crear los detalles de la venta
    for item in carrito:
        detalle = DetalleVenta(
            venta_id=nueva_venta.id,
            producto_id=item['id'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio']
        )
        db.session.add(detalle)

    db.session.commit()
    return jsonify({'success': True, 'venta_id': nueva_venta.id, 'total': total})

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
def proveedores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    todos_proveedores = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=todos_proveedores)

@app.route('/agregar_proveedor', methods=['GET', 'POST'])
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
# RUTAS DE MATERIAS PRIMAS - COMPLETAMENTE ACTUALIZADAS
# =============================================

@app.route('/materias_primas')
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
def desactivar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    materia.activo = False
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" desactivada correctamente', 'success')
    return redirect(url_for('materias_primas'))

@app.route('/activar_materia_prima/<int:id>')
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
def historial_compras(materia_prima_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(materia_prima_id)
    historial = HistorialCompra.query.filter_by(materia_prima_id=materia_prima_id).order_by(HistorialCompra.fecha_compra.desc()).all()
    
    return render_template('historial_compras.html', materia=materia, historial=historial)

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

if __name__ == '__main__':
    app.run(debug=True)