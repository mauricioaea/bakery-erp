from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='cajero')  # 'admin' o 'cajero'
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    codigo_barras = db.Column(db.String(50), unique=True)
    activo = db.Column(db.Boolean, default=True)
    
class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    productos_que_suministra = db.Column(db.Text)
    tiempo_entrega_dias = db.Column(db.Integer, default=1)
    evaluacion = db.Column(db.Integer, default=5)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Relación con materias primas
    materias_primas = db.relationship('MateriaPrima', backref='proveedor_rel', lazy=True)

    
class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    unidad_medida = db.Column(db.String(20), nullable=False)
    stock_actual = db.Column(db.Float, default=0)
    stock_minimo = db.Column(db.Float, default=0)
    costo_promedio = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_vencimiento = db.Column(db.Date)
    alerta_vencimiento = db.Column(db.Integer, default=15)
    fecha_ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NUEVOS CAMPOS PARA GESTIÓN POR EMPAQUES
    gramos_por_empaque = db.Column(db.Float, nullable=False, default=1.0)
    unidad_compra = db.Column(db.String(50), nullable=False, default='Unidad')
    stock_minimo_empaques = db.Column(db.Integer, default=1)
    
    @property
    def valor_inventario(self):
        """Calcular valor total en inventario para esta materia prima"""
        return self.stock_actual * self.costo_promedio

class HistorialCompra(db.Model):
    __tablename__ = 'historial_compras'
    id = db.Column(db.Integer, primary_key=True)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id'), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad_empaques = db.Column(db.Integer, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    precio_unitario_empaque = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    materia_prima = db.relationship('MateriaPrima', backref='compras')
    usuario = db.relationship('Usuario')
    
class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(100))
    peso_unidad_gramos = db.Column(db.Float, nullable=False, default=0)
    porcentaje_perdida = db.Column(db.Float, default=10.0)
    costo_total = db.Column(db.Float, default=0)
    precio_venta = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NUEVOS CAMPOS PARA EL SISTEMA DE PRODUCCIÓN
    peso_total_masa = db.Column(db.Float, default=0)  # Peso total en gramos
    unidades_obtenidas = db.Column(db.Integer, default=0)  # Unidades por lote
    peso_horneado_unidad = db.Column(db.Float, default=0)  # Peso después de horneado
    costo_materias_primas = db.Column(db.Float, default=0)  # Costo solo de materias primas
    costo_indirecto = db.Column(db.Float, default=0)  # Costos indirectos (CIF)
    margen_ganancia = db.Column(db.Float, default=0)  # Margen de ganancia
    precio_venta_unitario = db.Column(db.Float, default=0)  # Precio de venta por unidad
    precio_por_gramo = db.Column(db.Float, default=0)  # Precio por gramo
    
    ingredientes = db.relationship('RecetaIngrediente', backref='receta', lazy=True, cascade='all, delete-orphan')

    # PROPIEDADES CALCULADAS (se mantienen como respaldo)
    @property
    def peso_total_masa_calculado(self):
        """Peso total de la masa sumando todos los ingredientes"""
        return sum(ing.cantidad_gramos for ing in self.ingredientes)

    @property
    def unidades_obtenidas_calculadas(self):
        """Cantidad de unidades que se obtienen del lote"""
        if self.peso_unidad_gramos > 0:
            return int(self.peso_total_masa / self.peso_unidad_gramos)
        return 0

    @property
    def peso_horneado_unidad_calculado(self):
        """Peso de cada unidad después del horneado (considerando pérdidas)"""
        if self.peso_unidad_gramos > 0:
            perdida_gramos = self.peso_unidad_gramos * (self.porcentaje_perdida / 100)
            return self.peso_unidad_gramos - perdida_gramos
        return 0

    @property
    def costo_unitario_calculado(self):
        """Costo por unidad producida"""
        if self.unidades_obtenidas > 0:
            return self.costo_total / self.unidades_obtenidas
        return 0

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)  # 'efectivo', 'tarjeta', 'transferencia'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    proveedor = db.Column(db.String(200), nullable=False)
    total = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compras'
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # 'nomina', 'servicios', 'alquiler', etc.
    monto = db.Column(db.Float, nullable=False)

class RecetaIngrediente(db.Model):
    __tablename__ = 'receta_ingredientes'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id'), nullable=False)
    porcentaje_aplicado = db.Column(db.Float, nullable=False)  # % sobre el total
    cantidad_gramos = db.Column(db.Float, nullable=False, default=0)
    costo_ingrediente = db.Column(db.Float, default=0)
    
    # Relación con materia prima
    materia_prima = db.relationship('MateriaPrima', backref='recetas_ingredientes')

class OrdenProduccion(db.Model):
    __tablename__ = 'ordenes_produccion'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    cantidad_producir = db.Column(db.Integer, nullable=False)
    fecha_produccion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, completada
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # NUEVOS CAMPOS PARA SEGUIMIENTO DE PRODUCCIÓN
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    costo_real = db.Column(db.Float, default=0)  # Costo real de la producción
    
    # Relaciones
    receta = db.relationship('Receta', backref='ordenes_produccion')
    usuario = db.relationship('Usuario')

# NUEVA CLASE PARA HISTORIAL DE DESCUENTO DE INVENTARIO
class HistorialInventario(db.Model):
    __tablename__ = 'historial_inventario'
    id = db.Column(db.Integer, primary_key=True)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id'), nullable=False)
    orden_produccion_id = db.Column(db.Integer, db.ForeignKey('ordenes_produccion.id'), nullable=False)
    cantidad_utilizada = db.Column(db.Float, nullable=False)
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_movimiento = db.Column(db.String(20), default='produccion')  # 'produccion', 'ajuste', 'compra'
    
    # Relaciones
    materia_prima = db.relationship('MateriaPrima', backref='movimientos_inventario')
    orden_produccion = db.relationship('OrdenProduccion', backref='movimientos_inventario')