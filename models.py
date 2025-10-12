from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math  

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
    stock_actual = db.Column(db.Integer, default=0)  # ← NUEVO CAMPO
    stock_minimo = db.Column(db.Integer, default=10) # ← NUEVO CAMPO
    precio_venta = db.Column(db.Float, nullable=False)
    codigo_barras = db.Column(db.String(50), unique=True)
    activo = db.Column(db.Boolean, default=True)
    
class Proveedor(db.Model):
    __tablename__ = 'proveedor'
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
    
    # ✅ RELACIÓN CORREGIDA - Solo esta es necesaria
    # La relación se define en MateriaPrima con backref
    
class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    costo_promedio = db.Column(db.Float, default=0)
    stock_actual = db.Column(db.Float, default=0)
    stock_minimo = db.Column(db.Float, default=0)
    fecha_ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    # NUEVOS CAMPOS PARA EL SISTEMA DE EMPAQUES
    unidad_compra = db.Column(db.String(50), default='Unidad')
    gramos_por_empaque = db.Column(db.Float, default=1.0)
    stock_minimo_empaques = db.Column(db.Integer, default=1)
    
    # Relación con proveedor
    proveedor = db.relationship('Proveedor', backref='materias_primas')

    # ✅ AGREGA ESTAS PROPIEDADES QUE FALTAN
    @property
    def valor_inventario(self):
        """Calcula el valor total del inventario de esta materia prima"""
        return self.stock_actual * self.costo_promedio

    @property
    def stock_empaques_actual(self):
        """Calcula el stock actual en empaques"""
        if self.gramos_por_empaque > 0:
            return self.stock_actual / self.gramos_por_empaque
        return 0

    @property
    def proveedor_rel(self):
        """Propiedad para compatibilidad con el template"""
        return self.proveedor

    
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
    
    # NUEVOS CAMPOS PARA EL SISTEMA DE PRECIOS REALES
    precio_venta_real = db.Column(db.Float, default=0)  # ✅ PRECIO REAL DE VENTA
    precio_venta_unitario = db.Column(db.Float, default=0)  # Precio teórico por unidad
    precio_por_gramo = db.Column(db.Float, default=0)  # Precio por gramo teórico
    
    # CAMPOS EXISTENTES DE PRODUCCIÓN
    peso_total_masa = db.Column(db.Float, default=0)  # Peso total en gramos
    unidades_obtenidas = db.Column(db.Integer, default=0)  # Unidades por lote
    peso_horneado_unidad = db.Column(db.Float, default=0)  # Peso después de horneado
    costo_materias_primas = db.Column(db.Float, default=0)  # Costo solo de materias primas
    costo_indirecto = db.Column(db.Float, default=0)  # Costos indirectos (CIF)
    margen_ganancia = db.Column(db.Float, default=0)  # Margen de ganancia teórico
    
    
     # =============================================
    # ✅ NUEVO: RELACIÓN CON PRODUCTO (PASO 1.1)
    # =============================================
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)  # nullable=True temporalmente
    producto = db.relationship('Producto', backref=db.backref('recetas', lazy=True))
    # =============================================
    
    ingredientes = db.relationship('RecetaIngrediente', backref='receta', lazy=True, cascade='all, delete-orphan')
    
    
    # PROPIEDADES CALCULADAS PARA ANÁLISIS REAL
    @property
    def precio_venta_efectivo(self):
        """Precio que realmente se usa: real si existe, sino teórico"""
        return self.precio_venta_real if self.precio_venta_real > 0 else self.precio_venta_unitario
    
    @property
    def costo_unitario(self):
        """Costo por unidad producida"""
        if self.unidades_obtenidas > 0:
            return self.costo_total / self.unidades_obtenidas
        return 0

    @property
    def utilidad_real_pesos(self):
        """Utilidad real en pesos por unidad"""
        if self.precio_venta_efectivo > 0:
            return self.precio_venta_efectivo - self.costo_unitario
        return 0

    @property
    def utilidad_real_porcentaje(self):
        """Margen de utilidad real en porcentaje"""
        if self.precio_venta_efectivo > 0 and self.utilidad_real_pesos > 0:
            return (self.utilidad_real_pesos / self.precio_venta_efectivo) * 100
        return 0

    @property
    def margen_contribucion(self):
        """Margen de contribución por unidad (igual a utilidad en pesos)"""
        return self.utilidad_real_pesos

    @property
    def punto_equilibrio_unidades(self):
        """Punto de equilibrio en unidades (cuántas vender para cubrir costos fijos)"""
        if self.utilidad_real_pesos > 0:
            # Considerando solo costos variables para el punto de equilibrio
            return math.ceil(self.costo_total / self.utilidad_real_pesos)
        return 0

    @property
    def rentabilidad_categoria(self):
        """Categorizar la rentabilidad basada en el margen real"""
        margen = self.utilidad_real_porcentaje
        if margen >= 40:
            return "Alta"
        elif margen >= 25:
            return "Media"
        elif margen >= 15:
            return "Baja"
        elif margen > 0:
            return "Mínima"
        else:
            return "Pérdida"

    @property
    def eficiencia_costo(self):
        """Eficiencia en el uso de costos (qué % del precio es costo)"""
        if self.precio_venta_efectivo > 0:
            return (self.costo_unitario / self.precio_venta_efectivo) * 100
        return 100  # Si no hay precio, todo es costo

    @property
    def valor_produccion_total(self):
        """Valor total de la producción si se vende todo"""
        if self.unidades_obtenidas > 0:
            return self.precio_venta_efectivo * self.unidades_obtenidas
        return 0

    @property
    def utilidad_total_lote(self):
        """Utilidad total si se vende todo el lote"""
        return self.utilidad_real_pesos * self.unidades_obtenidas

    # PROPIEDADES CALCULADAS ORIGINALES (se mantienen como respaldo)
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
    
    # Agregar método a la clase Receta para calcular costos con ganancia
def calcular_precio_venta(self):
    """Calcular precio de venta con CIF 45% y ganancia 45%"""
    # Costo total de materia prima
    costo_mp = self.calcular_costo_total()
    
    # Costo Indirecto de Fabricación (CIF 45%)
    cif = costo_mp * 0.45
    
    # Costo total (MP + CIF)
    costo_total = costo_mp + cif
    
    # Ganancia (45% sobre costo total)
    ganancia = costo_total * 0.45
    
    # Precio total de preparación
    precio_total = costo_total + ganancia
    
    # Precio por unidad
    if self.unidades_produccion > 0:
        precio_unidad = precio_total / self.unidades_produccion
    else:
        precio_unidad = 0
    
    return {
        'costo_materia_prima': costo_mp,
        'cif': cif,
        'costo_total': costo_total,
        'ganancia': ganancia,
        'precio_total_preparacion': precio_total,
        'precio_venta_unidad': precio_unidad
    }
    
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
    
    # ESTADOS ACTUALIZADOS - CAMBIAR 'pendiente' por 'PENDIENTE'
    estado = db.Column(db.String(20), default='PENDIENTE')  # ← MODIFICADO: PENDIENTE, EN_PRODUCCION, COMPLETADA, CANCELADA
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # NUEVOS CAMPOS PARA SEGUIMIENTO DE PRODUCCIÓN
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    costo_real = db.Column(db.Float, default=0)  # Costo real de la producción
    
    # NUEVO: Para tracking del stock generado
    stock_generado = db.Column(db.Boolean, default=False)  # ← NUEVO: Si ya se sumó al stock
    
    # Relaciones
    receta = db.relationship('Receta', backref='ordenes_produccion')
    usuario = db.relationship('Usuario')
    
    def __repr__(self):
        return f'<OrdenProduccion {self.id} - {self.receta.nombre if self.receta else "Sin receta"} - {self.estado}>'
    
    # NUEVO: Método para obtener el producto asociado
    @property
    def producto(self):
        """Devuelve el producto asociado a esta receta"""
        return self.receta.producto if self.receta else None
    
    # NUEVO: Método para calcular ingredientes necesarios
    def calcular_ingredientes_necesarios(self):
        """Calcula los ingredientes necesarios para esta orden"""
        if not self.receta:
            return {}
        
        ingredientes = {}
        for ingrediente in self.receta.ingredientes:
            # ✅ CORREGIDO: usar 'cantidad_gramos' en lugar de 'cantidad'
            # ✅ CORREGIDO: dividir por unidades_obtenidas para calcular por unidad
            if self.receta.unidades_obtenidas and self.receta.unidades_obtenidas > 0:
                cantidad_necesaria = (ingrediente.cantidad_gramos / self.receta.unidades_obtenidas) * self.cantidad_producir
            else:
                cantidad_necesaria = 0
                
            ingredientes[ingrediente.materia_prima.nombre] = {
                'cantidad': cantidad_necesaria,
                'unidad': ingrediente.materia_prima.unidad_medida,
                'materia_prima_id': ingrediente.materia_prima_id
            }
        return ingredientes
    
    # NUEVO: Método para verificar disponibilidad de ingredientes
    def verificar_ingredientes_disponibles(self):
        """Verifica si hay suficientes materias primas para esta orden"""
        ingredientes = self.calcular_ingredientes_necesarios()
        faltantes = []
        
        for nombre, datos in ingredientes.items():
            materia_prima = MateriaPrima.query.get(datos['materia_prima_id'])
            # ✅ CORREGIDO: usar 'stock_actual' en lugar de 'cantidad_disponible'
            if materia_prima and materia_prima.stock_actual < datos['cantidad']:
                faltantes.append({
                    'nombre': nombre,
                    'necesario': datos['cantidad'],
                    'disponible': materia_prima.stock_actual,
                    'unidad': datos['unidad']
                })
        
        return len(faltantes) == 0, faltantes
    
    # NUEVO: Método para iniciar producción
    def iniciar_produccion(self):
        """Marca la orden como en producción y registra fecha de inicio"""
        if self.estado == 'PENDIENTE':
            self.estado = 'EN_PRODUCCION'
            self.fecha_inicio = datetime.utcnow()
            return True
        return False
    
    # NUEVO: Método para completar producción
    def completar_produccion(self):
        """Marca la orden como completada, actualiza stock y descuenta ingredientes"""
        if self.estado == 'EN_PRODUCCION':
            self.estado = 'COMPLETADA'
            self.fecha_fin = datetime.utcnow()
            
            print(f"🔍 DEBUG: Completando producción - Receta: {self.receta.nombre if self.receta else 'N/A'}")
            print(f"🔍 DEBUG: Cantidad a producir: {self.cantidad_producir}")
        
            
             # =============================================
            # ✅ CORREGIDO: Actualizar stock del producto asociado
            # =============================================
            if self.receta and self.receta.producto:
                producto = self.receta.producto
                producto.stock_actual += self.cantidad_producir
                self.stock_generado = True
                print(f"✅ Stock actualizado: {self.cantidad_producir} unidades de {producto.nombre}")
                
                print(f"🔍 DEBUG: Producto antes de actualizar: {producto.nombre} - Stock: {producto.stock_actual}")
            
                producto.stock_actual += self.cantidad_producir
                self.stock_generado = True
                
                print(f"🔍 DEBUG: Producto después de actualizar: {producto.nombre} - Stock: {producto.stock_actual}")
                print(f"✅ Stock actualizado: {self.cantidad_producir} unidades de {producto.nombre}")
                
            else:
                print(f"⚠️  Advertencia: Receta '{self.receta.nombre if self.receta else 'N/A'}' no tiene producto asociado")
            # =============================================
            
            # Descontar ingredientes utilizados
            self._descontar_ingredientes()
            
             # ✅ NUEVO: Forzar commit de la sesión
            db.session.commit()
            print("🔍 DEBUG: Cambios guardados en la base de datos")
                
            return True
        return False
    
    # NUEVO: Método privado para descontar ingredientes
    def _descontar_ingredientes(self):
        """Descuenta las materias primas utilizadas en la producción"""
        ingredientes = self.calcular_ingredientes_necesarios()
        
        for nombre, datos in ingredientes.items():
            materia_prima = MateriaPrima.query.get(datos['materia_prima_id'])
            if materia_prima:
                # ✅ CORREGIDO: usar 'stock_actual' en lugar de 'cantidad_disponible'
                materia_prima.stock_actual -= datos['cantidad']
                # Registrar en historial de inventario si existe ese modelo
                # self._registrar_movimiento_inventario(materia_prima, datos['cantidad'])

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

# =============================================
# NUEVOS MODELOS PARA STOCK Y PRODUCCIÓN DIARIA
# =============================================

class StockProducto(db.Model):
    __tablename__ = 'stock_productos'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=10)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con receta
    receta = db.relationship('Receta', backref=db.backref('stock_info', lazy=True))

# MANTENER ESTA (elimina la otra)
class ConfiguracionProduccion(db.Model):
    __tablename__ = 'configuracion_produccion'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    
    # ✅ CONFIGURACIÓN PERSONALIZABLE POR PRODUCTO
    stock_objetivo = db.Column(db.Integer, default=50)
    stock_minimo = db.Column(db.Integer, default=10)  # ✅ NUEVO: Stock mínimo personalizado
    stock_maximo = db.Column(db.Integer, default=100) # ✅ NUEVO: Stock máximo
    
    # Parámetros de alertas
    porcentaje_critico = db.Column(db.Float, default=20.0)    # ≤ 20% = CRÍTICO
    porcentaje_bajo = db.Column(db.Float, default=50.0)       # ≤ 50% = BAJO  
    porcentaje_medio = db.Column(db.Float, default=80.0)      # ≤ 80% = MEDIO
    
    # Métricas de ventas
    tendencia_ventas = db.Column(db.Float, default=1.0)  # Factor de tendencia
    rotacion_diaria_esperada = db.Column(db.Float, default=10.0)  # ✅ NUEVO: Rotación esperada por día
    
    activo = db.Column(db.Boolean, default=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now)
    
    receta = db.relationship('Receta', backref=db.backref('config_produccion', lazy=True))
    
    def __repr__(self):
        return f'<ConfiguracionProduccion {self.receta_id}>'
    
    # ✅ NUEVO: Método mejorado para calcular estado
    def calcular_estado_stock(self, stock_actual):
        """Calcula el estado del stock basado en stock mínimo personalizado"""
        if stock_actual <= self.stock_minimo:
            return "CRÍTICO"
        elif stock_actual <= (self.stock_minimo * 2):
            return "BAJO"
        elif stock_actual <= self.stock_objetivo:
            return "MEDIO"
        else:
            return "ÓPTIMO"
    
    # ✅ NUEVO: Calcular días de inventario
    def calcular_dias_inventario(self, stock_actual, ventas_promedio):
        """Calcula cuántos días de inventario quedan"""
        if ventas_promedio > 0:
            return stock_actual / ventas_promedio
        return 999  # Si no hay ventas, inventario infinito