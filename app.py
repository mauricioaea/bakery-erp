import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Usuario, Producto, Venta, DetalleVenta, MateriaPrima, Receta, Categoria
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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

# Ruta para agregar producto al ticket (simulación, en realidad se hará en el frontend)
# En una implementación real, esto podría manejar el carrito en sesión o en el frontend.

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

    # Crear los detalles de la venta y actualizar inventario
    for item in carrito:
        detalle = DetalleVenta(
            venta_id=nueva_venta.id,
            producto_id=item['id'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio']
        )
        db.session.add(detalle)

        # Actualizar el inventario: descontar las materias primas según la receta
        # Comentado por ahora hasta que tengamos el módulo de recetas configurado
        # producto = Producto.query.get(item['id'])
        # recetas = Receta.query.filter_by(producto_id=producto.id).all()
        # for receta in recetas:
        #     materia_prima = MateriaPrima.query.get(receta.materia_prima_id)
        #     cantidad_descontar = receta.cantidad_utilizada * item['cantidad']
        #     if materia_prima.stock_actual >= cantidad_descontar:
        #         materia_prima.stock_actual -= cantidad_descontar
        #     else:
        #         db.session.rollback()
        #         return jsonify({'error': f'Stock insuficiente de {materia_prima.nombre}'}), 400

    db.session.commit()
    return jsonify({'success': True, 'venta_id': nueva_venta.id, 'total': total})

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))


# Ruta para gestión de materias primas
@app.route('/materias_primas')
def materias_primas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todas las materias primas (activas e inactivas)
    materias = MateriaPrima.query.all()
    return render_template('materias_primas.html', materias_primas=materias)

# Ruta para agregar nueva materia prima
@app.route('/agregar_materia_prima', methods=['GET', 'POST'])
def agregar_materia_prima():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            proveedor = request.form.get('proveedor', '').strip()
            unidad_medida = request.form['unidad_medida']
            precio_compra = float(request.form['precio_compra'])
            cantidad_embalaje = float(request.form['cantidad_embalaje'])
            stock_minimo = float(request.form.get('stock_minimo', 0))
            
            # VALIDACIONES DEL SERVIDOR
            if not proveedor:
                flash('El campo proveedor es requerido', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if precio_compra <= 0:
                flash('El precio de compra debe ser mayor a 0', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if cantidad_embalaje <= 0:
                flash('La cantidad de embalaje debe ser mayor a 0', 'error')
                return redirect(url_for('agregar_materia_prima'))
                
            if stock_minimo < 0:
                flash('El stock mínimo no puede ser negativo', 'error')
                return redirect(url_for('agregar_materia_prima'))
            
            # Calcular costo por unidad
            costo_unitario = precio_compra / cantidad_embalaje
            
            nueva_materia = MateriaPrima(
                nombre=nombre,
                proveedor=proveedor,
                unidad_medida=unidad_medida,
                costo_promedio=costo_unitario,
                stock_actual=0,
                stock_minimo=stock_minimo,
                activo=True
            )
            
            db.session.add(nueva_materia)
            db.session.commit()
            
            flash(f'Materia prima "{nombre}" agregada correctamente', 'success')
            return redirect(url_for('materias_primas'))
            
        except ValueError as e:
            flash('Error: Los campos numéricos deben contener valores válidos', 'error')
            return redirect(url_for('agregar_materia_prima'))
        except Exception as e:
            flash('Error inesperado al agregar la materia prima', 'error')
            return redirect(url_for('agregar_materia_prima'))
    
    return render_template('agregar_materia_prima.html')

# Ruta para editar materia prima
@app.route('/editar_materia_prima/<int:id>', methods=['GET', 'POST'])
def editar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            materia.nombre = request.form['nombre']
            materia.proveedor = request.form.get('proveedor', '').strip()
            materia.unidad_medida = request.form['unidad_medida']
            materia.stock_minimo = float(request.form.get('stock_minimo', 0))
            
            # Validaciones
            if not materia.proveedor:
                flash('El campo proveedor es requerido', 'error')
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
            flash('Error inesperado al actualizar la materia prima', 'error')
            return redirect(url_for('editar_materia_prima', id=id))
    
    return render_template('editar_materia_prima.html', materia=materia)

# Ruta para desactivar materia prima (eliminación lógica) - CAMBIADO A GET
@app.route('/desactivar_materia_prima/<int:id>')
def desactivar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    materia.activo = False
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" desactivada correctamente', 'success')
    return redirect(url_for('materias_primas'))

# Ruta para activar materia prima - CAMBIADO A GET
@app.route('/activar_materia_prima/<int:id>')
def activar_materia_prima(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    materia = MateriaPrima.query.get_or_404(id)
    materia.activo = True
    db.session.commit()
    
    flash(f'Materia prima "{materia.nombre}" activada correctamente', 'success')
    return redirect(url_for('materias_primas'))

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