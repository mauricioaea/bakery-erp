import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import math
from sqlalchemy import func, extract
from werkzeug.security import generate_password_hash, check_password_hash 
from sqlalchemy.orm import backref

# SOLO esta línea - elimina cualquier otra db
db = SQLAlchemy()


# 🆕 SISTEMA DE ROLES Y PERMISOS - VERSIÓN CORREGIDA
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20))
    
    # 🆕 NUEVOS CAMPOS PARA ROLES
    rol = db.Column(db.String(20), default='cajero')  # cajero, supervisor, administrador, gerente
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultimo_acceso = db.Column(db.DateTime)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=True)  # Para multi-sucursal futuro
    panaderia_id = db.Column(db.Integer, db.ForeignKey('configuracion_panaderia.id'), nullable=False, default=1)
    
    # 🆕 RELACIÓN CON PERMISOS PERSONALIZADOS
    permisos_personalizados = db.relationship('PermisoUsuario', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    # 🆕 CORREGIDO: Cambiar nombre de relación para evitar conflicto
    ventas_realizadas = db.relationship('Venta', backref='usuario_asociado', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 🆕 MÉTODOS ACTUALIZADOS PARA GESTIÓN DE PERMISOS
    def tiene_permiso(self, modulo, accion):
        """Verificar si usuario tiene permiso para acción en módulo"""
        # 1. Administrador tiene acceso completo
        if self.rol == 'administrador':
            return True
            
        # 2. Verificar permisos personalizados primero
        permiso_personalizado = PermisoUsuario.query.filter_by(
            usuario_id=self.id, 
            modulo=modulo, 
            accion=accion
        ).first()
        
        if permiso_personalizado:
            return permiso_personalizado.permitido
        
        # 3. Fallback a permisos del rol
        permisos_rol = ROLES_PERMISOS.get(self.rol, {})
        acciones_permitidas = permisos_rol.get(modulo, [])
        
        return accion in acciones_permitidas
    
    def puede_acceder_modulo(self, modulo):
        """Verificar si usuario puede acceder a un módulo completo"""
        if self.rol == 'administrador':
            return True
            
        # Verificar permisos personalizados
        tiene_permiso_personal = PermisoUsuario.query.filter_by(
            usuario_id=self.id, 
            modulo=modulo, 
            permitido=True
        ).first()
        
        if tiene_permiso_personal:
            return True
            
        # Verificar permisos del rol
        permisos_rol = ROLES_PERMISOS.get(self.rol, {})
        return modulo in permisos_rol
    
    def obtener_modulos_permitidos(self):
        """Obtener lista de módulos a los que tiene acceso"""
        if self.rol == 'administrador':
            return list(MODULOS_SISTEMA.keys())
        
        permisos_rol = ROLES_PERMISOS.get(self.rol, {})
        return list(permisos_rol.keys())
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.rol}>'

# 🆕 DEFINICIÓN DE ROLES Y PERMISOS (MANTENER IGUAL)
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

ROLES_PERMISOS = {
    'cajero': {
        'dashboard': ['ver'],
        'punto_venta': ['vender', 'ver_ventas_propias', 'imprimir_ticket', 'cierre_caja'], 
        'finanzas': ['ver_cierre_diario'],
        'usuarios': ['ver_perfil']  # Solo puede ver su propio perfil
    },
    
    'supervisor': {
        'dashboard': ['ver'],
        'punto_venta': ['vender', 'ver_todas_ventas', 'anular_ventas', 'cierre_caja'],
        'productos': ['ver', 'editar_stock'],
        'produccion': ['ver', 'producir'],
        'inventario': ['ver'],
        'clientes': ['ver', 'gestionar'],
        'proveedores': ['ver'],
        'ventas': ['ver_todas', 'exportar'],
        'reportes': ['ver_ventas', 'ver_produccion'],
        'finanzas': ['ver_cierre_diario'],
        'usuarios': ['ver_perfil']
    },
    
    'gerente': {
        'dashboard': ['ver'],
        'punto_venta': ['vender', 'ver_todas_ventas', 'anular_ventas', 'cierre_caja'],
        'productos': ['ver', 'crear', 'editar', 'eliminar'],
        'categorias': ['ver', 'gestionar'],
        'produccion': ['ver', 'producir', 'crear_recetas', 'editar_recetas'],
        'inventario': ['ver', 'gestionar'],
        'clientes': ['ver', 'gestionar'],
        'proveedores': ['ver', 'gestionar'],
        'ventas': ['ver_todas', 'exportar', 'analizar'],
        'reportes': ['ver_todos', 'exportar', 'analizar'],
        'finanzas': ['ver_todo', 'gestionar'],
        'activos': ['ver', 'gestionar'],
        'configuracion': ['ver', 'editar_parametros'],
        'usuarios': ['ver_perfil']
    },
    
    'admin_cliente': {
        # Acceso completo pero SOLO a SU panadería
        'dashboard': ['ver'],
        'punto_venta': ['vender', 'ver_todas_ventas', 'anular_ventas', 'cierre_caja'],
        'productos': ['ver', 'crear', 'editar', 'eliminar'],
        'categorias': ['ver', 'gestionar'],
        'produccion': ['ver', 'producir', 'crear_recetas', 'editar_recetas'],
        'inventario': ['ver', 'gestionar'],
        'clientes': ['ver', 'gestionar'],
        'proveedores': ['ver', 'gestionar'],
        'finanzas': ['ver_todo', 'gestionar'],
        'reportes': ['ver_todos', 'exportar', 'analizar'],
        'configuracion': ['ver', 'editar_parametros'],
        'activos': ['ver', 'gestionar'],
        'usuarios': ['gestionar', 'ver_perfil'],
        'gestion_usuarios': ['gestionar', 'ver_perfil'],
        'sistema': ['diagnosticar']
        # ❌ NO incluye: 'gestion_clientes' (gestión de múltiples clientes)
    },
    
    'super_admin': {
        # 🎯 ACCESO COMPLETO A TODO EL SISTEMA
        'dashboard': ['ver'],
        'punto_venta': ['vender', 'ver_todas_ventas', 'anular_ventas', 'cierre_caja'],
        'productos': ['ver', 'crear', 'editar', 'eliminar'],
        'categorias': ['ver', 'gestionar'],
        'produccion': ['ver', 'producir', 'crear_recetas', 'editar_recetas'],
        'inventario': ['ver', 'gestionar'],
        'clientes': ['ver', 'gestionar'],
        'proveedores': ['ver', 'gestionar'],
        'finanzas': ['ver_todo', 'gestionar'],
        'reportes': ['ver_todos', 'exportar', 'analizar'],
        'configuracion': ['ver', 'editar_parametros'],
        'activos': ['ver', 'gestionar'],
        'usuarios': ['gestionar', 'ver_perfil'],
        'sistema': ['diagnosticar', 'gestion_clientes']  # ✅ Solo super_admin ve gestión de clientes
    }
}

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    activa = db.Column(db.Boolean, default=True)
    
    usuarios = db.relationship('Usuario', backref='sucursal', lazy=True)
    
    def __repr__(self):
        return f'<Sucursal {self.nombre}>'
    
# =============================================
# 🆕 CLASE CATEGORÍA (FALTANTE) - AGREGAR ANTES DE PRODUCTO
# =============================================

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # ✅ NUEVO: Relación con panadería para multicliente
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, default=1)
    panaderia = db.relationship('Panaderia', backref=db.backref('categorias_list', lazy=True))
    
    # Relación con productos
    productos = db.relationship('Producto', backref='categoria_rel', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
    
# =============================================
# 🆕 MODELO PARA CONFIGURACIÓN DE PANADERÍA Y LICENCIAS
# =============================================

class ConfiguracionPanaderia(db.Model):
    __tablename__ = 'configuracion_panaderia'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    
    # 🆕 CAMPO PARA SINCRONIZAR CON TENANT_MASTER
    tenant_id = db.Column(db.Integer, nullable=True)
    
    # 🆕 CAMPO PARA ACTIVAR/DESACTIVAR CLIENTE
    activo = db.Column(db.Integer, default=1)
    
    # INFORMACIÓN BÁSICA DE LA PANADERÍA
    nombre_panaderia = db.Column(db.String(200), nullable=False, default='Mi Panadería')
    telefono_contacto = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    
    # 🆕 SISTEMA DE LICENCIAS Y LÍMITES
    tipo_licencia = db.Column(db.String(20), default='local')
    max_usuarios = db.Column(db.Integer, default=3)
    ventas_ilimitadas = db.Column(db.Boolean, default=True)
    
    # CONTROL DE SUSCRIPCIÓN PARA NUBE
    fecha_expiracion = db.Column(db.Date)
    estado_suscripcion = db.Column(db.String(20), default='activa')
    dias_gracia = db.Column(db.Integer, default=7)
    
    # SISTEMA DE NOTIFICACIONES
    ultima_notificacion = db.Column(db.DateTime)
    notificaciones_pendientes = db.Column(db.Integer, default=0)
    
    # DATOS DE FACTURACIÓN CLIENTE NUBE
    razon_social = db.Column(db.String(200))
    nit = db.Column(db.String(20))
    email_facturacion = db.Column(db.String(120))
    telefono_facturacion = db.Column(db.String(20))
    
    # DATOS DE PAGO
    metodo_pago = db.Column(db.String(50), default='transferencia')
    referencia_pago = db.Column(db.String(100))
    
    # FECHAS DE CONTROL
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ultimo_cierre = db.Column(db.Date)
    sistema_activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ConfiguracionPanaderia {self.nombre_panaderia} - {self.tipo_licencia}>'
    
    # =============================================
    # MÉTODOS DE LA CLASE
    # =============================================
    
    @property
    def usuarios_activos_count(self):
        """Cuenta cuántos usuarios activos tiene la panadería"""
        # ✅ FILTRAR POR panaderia_id
        return Usuario.query.filter_by(
            panaderia_id=self.panaderia_id,
            activo=True
        ).count()
    
    @property
    def puede_crear_usuario(self):
        """Verifica si se puede crear un nuevo usuario"""
        return self.usuarios_activos_count < self.max_usuarios
    
    @property
    def usuarios_restantes(self):
        """Calcula cuántos usuarios más se pueden crear"""
        return max(0, self.max_usuarios - self.usuarios_activos_count)
    
    @property
    def suscripcion_activa(self):
        """Verifica si la suscripción está activa (solo para nube)"""
        if self.tipo_licencia == 'local':
            return True
        
        if self.estado_suscripcion == 'bloqueada':
            return False
        
        if self.fecha_expiracion:
            from datetime import datetime
            dias_restantes = (self.fecha_expiracion - datetime.now().date()).days
            return dias_restantes + self.dias_gracia > 0
        
        return True
    
    @property
    def dias_para_expiracion(self):
        """Calcula días restantes para expiración (solo nube)"""
        if self.tipo_licencia == 'local' or not self.fecha_expiracion:
            return 999
        
        from datetime import datetime
        dias = (self.fecha_expiracion - datetime.now().date()).days
        return dias
    
    @property
    def estado_suscripcion_detallado(self):
        """Estado detallado de la suscripción - ACTUALIZADO AUTOMÁTICAMENTE"""
        # 🔄 Actualizar estado antes de mostrarlo
        self.actualizar_estado_suscripcion()
        
        if self.tipo_licencia == 'local':
            return "Licencia Local - Permanente"
        
        if self.estado_suscripcion == 'bloqueada':
            return "🔴 BLOQUEADA - Contactar soporte"
        
        if self.estado_suscripcion == 'expirada':
            return "🔴 EXPIRADA - Renovar para continuar"
        
        if self.estado_suscripcion == 'activa':
            dias = self.dias_para_expiracion
            if dias > 30:
                return f"🟢 ACTIVA - {dias} días restantes"
            elif dias > 7:
                return f"🟡 ACTIVA - {dias} días restantes ⚠️"
            elif dias > 0:
                return f"🟠 POR VENCER - {dias} días ⚠️⚠️"
            else:
                return f"🟢 ACTIVA - Sin fecha de vencimiento"
        
        return "Estado desconocido"
    
    def actualizar_estado_suscripcion(self):
        """Actualiza el estado de suscripción basado en fechas"""
        if self.tipo_licencia == 'local':
            self.estado_suscripcion = 'activa'
            return
        
        if not self.fecha_expiracion:
            self.estado_suscripcion = 'activa'
            return
        
        from datetime import datetime
        dias_restantes = (self.fecha_expiracion - datetime.now().date()).days
        
        if dias_restantes + self.dias_gracia < 0:
            self.estado_suscripcion = 'bloqueada'
        elif dias_restantes < 0:
            self.estado_suscripcion = 'expirada'
        else:
            self.estado_suscripcion = 'activa'           

class Panaderia(db.Model):
    __tablename__ = 'panaderias'
    
    # SOLO DEBE TENER UN ID COMO PRIMARY KEY
    id = db.Column(db.Integer, primary_key=True)  # ESTE es el que usan las foreign keys
    
    # ELIMINA esta línea: panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    ruc = db.Column(db.String(20))
    propietario = db.Column(db.String(100))
    
    # CONFIGURACIÓN
    moneda = db.Column(db.String(10), default='USD')
    impuesto = db.Column(db.Float, default=0.0)
    logo = db.Column(db.String(200))
    
    # CONTROL
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Añade default
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Panaderia {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'moneda': self.moneda
        }
        
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
     # ✅ NUEVO: Campos para aprendizaje automático
    vida_util_dias = db.Column(db.Integer, default=3)  # ✅ Vida útil realista del pan
    es_pan = db.Column(db.Boolean, default=True)  # ✅ Para identificar productos sin IVA
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    # ✅ NUEVO: Tipo de producto
    tipo_producto = db.Column(db.String(20), default='produccion')  # 'produccion' o 'externo'
    
    # ✅ NUEVO: Campos para productos externos
    costo_compra = db.Column(db.Float, default=0)  # Solo para productos externos
    proveedor_externo = db.Column(db.String(100))  # Solo para productos externos
    
    # ✅ ACTUALIZAR RELACIÓN CON RECETA (One-to-One)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=True)
    receta = db.relationship('Receta', 
                           foreign_keys=[receta_id],
                           backref=db.backref('producto_asociado', uselist=False))
    
    # ✅ NUEVO: Relación con panadería para multicliente
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, default=1)
    panaderia = db.relationship('Panaderia', backref=db.backref('productos_list', lazy=True))
    
    # ✅ NUEVAS PROPIEDADES CALCULADAS
    @property
    def es_produccion_interna(self):
        return self.tipo_producto == 'produccion'
    
    @property
    def es_producto_externo(self):
        return self.tipo_producto == 'externo'
    
    @property
    def utilidad_unitaria(self):
        if self.es_producto_externo:
            return self.precio_venta - self.costo_compra
        return 0  # Para producción interna, la utilidad se calcula en la receta
    
    @property
    def margen_utilidad(self):
        if self.es_producto_externo and self.precio_venta > 0:
            return (self.utilidad_unitaria / self.precio_venta) * 100
        return 0  
    
class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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

class ProductoExterno(db.Model):
    __tablename__ = 'productos_externos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(100), unique=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    
    # RELACIÓN CON PROVEEDOR
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    proveedor = db.relationship('Proveedor', backref='productos')
    
    # RELACIÓN CON PANADERÍA (CORREGIDA)
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False)
    panaderia = db.relationship('Panaderia', backref='productos_externos')
    
    # INVENTARIO Y PRECIOS
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    
    # MÉTRICAS AUTOMÁTICAS
    total_ventas = db.Column(db.Integer, default=0)
    total_ingresos = db.Column(db.Float, default=0.0)
    utilidad_total = db.Column(db.Float, default=0.0)
    
    # CONTROL
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultima_compra = db.Column(db.DateTime)
    fecha_ultima_venta = db.Column(db.DateTime)
    
    def calcular_utilidad_unitaria(self):
        return self.precio_venta - self.precio_compra
    
    def calcular_margen_ganancia(self):
        if self.precio_compra > 0:
            return (self.calcular_utilidad_unitaria() / self.precio_compra) * 100
        return 0
    
    def valor_inventario(self):
        return self.stock_actual * self.precio_compra
    
    def __repr__(self):
        return f'<ProductoExterno {self.nombre} (Panadería {self.panaderia_id})>'

class CompraExterna(db.Model):
    __tablename__ = 'compras_externas'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos_externos.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    total_compra = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)
    
    # RELACIONES
    proveedor = db.relationship('Proveedor', backref='compras')
    producto = db.relationship('ProductoExterno', backref='compras')


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
    
    # ✅ RELACIÓN CON PANADERÍA (NUEVO - CLAVE PARA MULTICLIENTE)
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False)
    panaderia = db.relationship('Panaderia', backref='materias_primas')
    
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

    def __repr__(self):
        return f'<MateriaPrima {self.nombre} (Panadería {self.panaderia_id})>'
    
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
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)
    producto = db.relationship('Producto', 
                             foreign_keys=[producto_id],
                             backref=db.backref('receta_asociada', uselist=False)) 
    # =============================================
    
    # ✅ NUEVO: Relación con panadería para multicliente
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, default=1)
    panaderia = db.relationship('Panaderia', backref=db.backref('recetas_list', lazy=True))
    
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
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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

# =============================================
# 🆕 NUEVO MODELO CLIENTE PARA FACTURACIÓN ELECTRÓNICA
# =============================================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ INFORMACIÓN BÁSICA DEL CLIENTE
    documento = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)  # Nombre o Razón Social
    tipo_documento = db.Column(db.String(2), default='31')  # 31=NIT, 13=CC, 22=CE, 41=Pasaporte
    tipo_persona = db.Column(db.String(1), default='J')  # J=Jurídica, N=Natural
    
    # ✅ INFORMACIÓN DE CONTACTO Y UBICACIÓN
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    
    # ✅ INFORMACIÓN TRIBUTARIA
    regimen = db.Column(db.String(50))  # Simplificado, Común, Especial
    responsabilidades = db.Column(db.Text)  # Responsabilidades fiscales separadas por coma
    
    # ✅ CONTROL DEL REGISTRO
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ✅ RELACIÓN CON VENTAS (una venta puede tener un cliente)
    ventas = db.relationship('Venta', back_populates='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.documento} - {self.nombre}>'
    
    # ✅ PROPIEDADES PARA FACILITAR EL USO
    @property
    def es_persona_juridica(self):
        """Retorna True si es persona jurídica"""
        return self.tipo_persona == 'J'
    
    @property
    def es_persona_natural(self):
        """Retorna True si es persona natural"""
        return self.tipo_persona == 'N'
    
    @property
    def codigo_tipo_documento_dian(self):
        """Retorna el código DIAN para el tipo de documento"""
        codigos = {
            '31': '31',  # NIT
            '13': '13',  # Cédula de ciudadanía
            '22': '22',  # Cédula de extranjería
            '41': '41',  # Pasaporte
            '11': '11'   # Registro civil
        }
        return codigos.get(self.tipo_documento, '13')
    
    @property
    def nombre_tipo_documento(self):
        """Retorna el nombre del tipo de documento"""
        nombres = {
            '31': 'NIT',
            '13': 'Cédula de Ciudadanía', 
            '22': 'Cédula de Extranjería',
            '41': 'Pasaporte',
            '11': 'Registro Civil'
        }
        return nombres.get(self.tipo_documento, 'Cédula')
    
    @property
    def nombre_tipo_persona(self):
        """Retorna el nombre del tipo de persona"""
        return 'Persona Jurídica' if self.es_persona_juridica else 'Persona Natural'
    
    def obtener_responsabilidades_lista(self):
        """Convierte las responsabilidades de string a lista"""
        if self.responsabilidades:
            return [r.strip() for r in self.responsabilidades.split(',')]
        return []
    
    def to_dict(self):
        """Convierte el cliente a diccionario para JSON"""
        return {
            'id': self.id,
            'documento': self.documento,
            'nombre': self.nombre,
            'tipo_documento': self.tipo_documento,
            'tipo_persona': self.tipo_persona,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'ciudad': self.ciudad,
            'departamento': self.departamento,
            'regimen': self.regimen,
            'responsabilidades': self.responsabilidades,
            'nombre_tipo_documento': self.nombre_tipo_documento,
            'nombre_tipo_persona': self.nombre_tipo_persona
        }

# =============================================
# FIN NUEVO MODELO CLIENTE
# =============================================

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.now) 
    total = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)  # 'efectivo', 'transferencia'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True) 
    
    # === 🆕 NUEVOS CAMPOS PARA MODULARIDAD ===
    tipo_documento = db.Column(db.String(20), default='POS')  # 'POS' o 'ELECTRONICA'
    consecutivo_pos = db.Column(db.Integer)  # Número de recibo POS
    cufe = db.Column(db.String(100))  # Para factura electrónica (UUID DIAN)
    estado_dian = db.Column(db.String(50), default='NO_APLICA')  # 'ACEPTADA', 'RECHAZADA', 'PENDIENTE', 'NO_APLICA'
    qr_factura = db.Column(db.Text)  # QR para factura electrónica
    respuesta_dian = db.Column(db.Text)  # JSON respuesta DIAN/proveedor
    texto_legal = db.Column(db.Text, default='Documento equivalente POS – No válido como factura electrónica de venta')
    es_donacion = db.Column(db.Boolean, default=False)
    motivo_donacion = db.Column(db.String(200), nullable=True)
    
    # ✅ NUEVO: Relación con panadería para multicliente
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, default=1)
    panaderia = db.relationship('Panaderia', backref=db.backref('ventas_list', lazy=True))
    
    # ✅✅✅ RELACIONES CORREGIDAS - SIN CONFLICTOS
    # NO necesitas: usuario = db.relationship(...) - ya lo crea Usuario.ventas_realizadas
    cliente = db.relationship('Cliente', back_populates='ventas')  # ← back_populates COINCIDE

    def __repr__(self):
        return f'<Venta {self.id} - ${self.total} - {self.tipo_documento}>'
    
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)  # Hacer nullable
    producto_externo_id = db.Column(db.Integer, db.ForeignKey('productos_externos.id'), nullable=True)  # ✅ NUEVO
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    
    # Relaciones
    #producto = db.relationship('Producto', backref='detalles_venta')
    #producto_externo = db.relationship('ProductoExterno', backref='detalles_venta')  #
    #usuario = db.relationship('Usuario', backref='ventas_asociadas', lazy=True)

    venta = db.relationship('Venta', backref='detalles')
    producto = db.relationship('Producto', backref='detalles_venta')
    producto_externo = db.relationship('ProductoExterno', backref='detalles_venta_externa')
    
class Compra(db.Model):
    __tablename__ = 'compras'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    proveedor = db.Column(db.String(200), nullable=False)
    total = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compras'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Gasto(db.Model):
    __tablename__ = 'gastos'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # 'nomina', 'servicios', 'alquiler', etc.
    monto = db.Column(db.Float, nullable=False)

class RecetaIngrediente(db.Model):
    __tablename__ = 'receta_ingredientes'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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
    
    estado = db.Column(db.String(20), default='PENDIENTE')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    costo_real = db.Column(db.Float, default=0)
    stock_generado = db.Column(db.Boolean, default=False)
    
    # ✅ FILTRO MULTICLIENTE
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, default=1)
    
    # RELACIONES
    receta = db.relationship('Receta', backref='ordenes_produccion')
    usuario = db.relationship('Usuario')
    panaderia = db.relationship('Panaderia', backref=db.backref('ordenes_produccion_list', lazy=True))
    
    def __repr__(self):
        return f'<OrdenProduccion {self.id} - {self.receta.nombre if self.receta else "Sin receta"} - {self.estado}>'
    
    @property
    def producto(self):
        """Devuelve el producto asociado a esta receta"""
        return self.receta.producto if self.receta else None
    
    # ✅ MANTENER SOLO UNA DEFINICIÓN de este método
    def calcular_ingredientes_necesarios(self):
        """Calcula los ingredientes necesarios para esta orden"""
        if not self.receta:
            return {}
        
        ingredientes = {}
        for ingrediente in self.receta.ingredientes:
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
    
    def verificar_ingredientes_disponibles(self):
        """Verifica si hay suficientes materias primas para esta orden"""
        ingredientes = self.calcular_ingredientes_necesarios()
        faltantes = []
        
        for nombre, datos in ingredientes.items():
            materia_prima = MateriaPrima.query.get(datos['materia_prima_id'])
            if materia_prima and materia_prima.stock_actual < datos['cantidad']:
                faltantes.append({
                    'nombre': nombre,
                    'necesario': datos['cantidad'],
                    'disponible': materia_prima.stock_actual,
                    'unidad': datos['unidad']
                })
        
        return len(faltantes) == 0, faltantes
    
    def iniciar_produccion(self):
        """Marca la orden como en producción y registra fecha de inicio"""
        if self.estado == 'PENDIENTE':
            self.estado = 'EN_PRODUCCION'
            self.fecha_inicio = datetime.utcnow()
            return True
        return False
    
    def completar_produccion(self):
        """Marca la orden como completada, actualiza stock y descuenta ingredientes"""
        if self.estado == 'EN_PRODUCCION':
            self.estado = 'COMPLETADA'
            self.fecha_fin = datetime.utcnow()
            
            print(f"🔍 DEBUG: Completando producción - Receta: {self.receta.nombre if self.receta else 'N/A'}")
            print(f"🔍 DEBUG: Cantidad a producir: {self.cantidad_producir}")
        
            # ✅ ACTUALIZAR STOCK DEL PRODUCTO
            if self.receta and self.receta.producto:
                producto = self.receta.producto
                print(f"🔍 DEBUG: Producto antes de actualizar: {producto.nombre} - Stock: {producto.stock_actual}")
                
                producto.stock_actual += self.cantidad_producir
                self.stock_generado = True
                
                print(f"🔍 DEBUG: Producto después de actualizar: {producto.nombre} - Stock: {producto.stock_actual}")
                print(f"✅ Stock actualizado: +{self.cantidad_producir} unidades de {producto.nombre}")
            
            else:
                print(f"⚠️  Advertencia: Receta '{self.receta.nombre if self.receta else 'N/A'}' no tiene producto asociado")
                # ✅ MANTENER: Crear producto automáticamente como respaldo
                if self.receta and not self.receta.producto:
                    try:
                        self._crear_producto_desde_receta()
                        print(f"✅ Producto creado automáticamente para receta: {self.receta.nombre}")
                    except Exception as e:
                        print(f"❌ Error creando producto automático: {e}")
            
            # Descontar ingredientes utilizados
            self._descontar_ingredientes()
                
            return True
        return False

    def _descontar_ingredientes(self):
        """Descuenta las materias primas utilizadas en la producción"""
        ingredientes = self.calcular_ingredientes_necesarios()
        
        for nombre, datos in ingredientes.items():
            materia_prima = MateriaPrima.query.get(datos['materia_prima_id'])
            if materia_prima:
                materia_prima.stock_actual -= datos['cantidad']

    # ✅ MANTENER ESTE MÉTODO COMO RESPALDO
    def _crear_producto_desde_receta(self):
        """Crea un producto automáticamente a partir de la receta si no existe (RESPALDO)"""
        if not self.receta or self.receta.producto:
            return False
        
        try:
            # Buscar categoría existente o crear una nueva
            nombre_categoria = self.receta.categoria.strip().title()
            categoria = Categoria.query.filter_by(nombre=nombre_categoria).first()
            
            if not categoria:
                # Crear categoría si no existe
                categoria = Categoria(nombre=nombre_categoria)
                db.session.add(categoria)
                db.session.flush()
            
            # Crear producto automático
            producto_automatico = Producto(
                nombre=self.receta.nombre,
                descripcion=self.receta.descripcion,
                categoria_id=categoria.id,
                precio_venta=self.receta.precio_venta_efectivo,
                stock_actual=self.cantidad_producir,
                stock_minimo=10,
                codigo_barras=f"PROD{self.receta.id:06d}",
                tipo_producto='produccion',
                es_pan=True if 'pan' in self.receta.nombre.lower() else False,
                receta_id=self.receta.id,
                activo=True,
                panaderia_id=self.panaderia_id  # ✅ AGREGAR FILTRO MULTICLIENTE
            )
            
            db.session.add(producto_automatico)
            db.session.flush()
            
            # Asignar el producto a la receta
            self.receta.producto_id = producto_automatico.id
            self.stock_generado = True
            
            print(f"✅ Producto automático creado: {producto_automatico.nombre} con {self.cantidad_producir} unidades")
            return True
            
        except Exception as e:
            print(f"❌ Error en _crear_producto_desde_receta: {e}")
            return False

# NUEVA CLASE PARA HISTORIAL DE DESCUENTO DE INVENTARIO
class HistorialInventario(db.Model):
    __tablename__ = 'historial_inventario'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
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
    
# =============================================
# ✅ NUEVOS MODELOS PARA APRENDIZAJE AUTOMÁTICO
# =============================================

class HistorialRotacionProducto(db.Model):
    __tablename__ = 'historial_rotacion_producto'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    ventas_dia = db.Column(db.Integer, default=0)
    rotacion_real = db.Column(db.Float, default=0.0)
    tendencia_semanal = db.Column(db.Float, default=1.0)
    
    producto = db.relationship('Producto', backref='historial_rotacion')
    
    __table_args__ = (db.UniqueConstraint('producto_id', 'fecha', name='unique_rotacion_diaria'),)

class ControlVidaUtil(db.Model):
    __tablename__ = 'control_vida_util'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fecha_produccion = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    stock_inicial = db.Column(db.Integer, nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    dias_sin_rotacion = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='FRESCO')  # FRESCO, ALERTA, RIESGO, PERDIDA
    
    producto = db.relationship('Producto', backref='control_vida_util')

class Factura(db.Model):
    __tablename__ = 'facturas'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=0.0)  # ✅ CERO para pan
    total = db.Column(db.Float, nullable=False)
    # Información de la panadería (configurable)
    nombre_panaderia = db.Column(db.String(200), default='Semillas Panadería')
    nit_panaderia = db.Column(db.String(50), default='1085297960')
    direccion_panaderia = db.Column(db.Text, default='Carrera 18 #9-45, Pasto')
    telefono_panaderia = db.Column(db.String(20), default='+57 3189098818')
    
    venta = db.relationship('Venta', backref='factura')
    
    
# =============================================
# NUEVAS TABLAS PARA CIERRE DIARIO - AGREGAR ANTES DE LAS FUNCIONES ML
# =============================================

class JornadaVentas(db.Model):
    """Control de jornadas comerciales diarias"""
    __tablename__ = 'jornadas_ventas'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    estado = db.Column(db.String(20), default='ACTIVA')  # ACTIVA, CERRADA
    total_ventas = db.Column(db.Float, default=0)
    total_efectivo = db.Column(db.Float, default=0)
    total_transferencia = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cerrada_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Jornada {self.fecha} - {self.estado}>'

class CierreDiario(db.Model):
    """Registro de cierres diarios"""
    __tablename__ = 'cierres_diarios'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    jornada_id = db.Column(db.Integer, db.ForeignKey('jornadas_ventas.id'))
    
    # TOTALES CALCULADOS
    total_ventas = db.Column(db.Float, nullable=False)
    total_efectivo = db.Column(db.Float, nullable=False)
    total_transferencia = db.Column(db.Float, nullable=False)
    
    total_transacciones = db.Column(db.Integer, nullable=False)
    
    # PRODUCTOS MÁS VENDIDOS (serializado como JSON)
    productos_top = db.Column(db.Text)  # JSON con productos más vendidos
    
    # COMPARATIVAS
    ventas_dia_anterior = db.Column(db.Float, default=0)
    tendencia = db.Column(db.Float, default=0)  # % vs día anterior
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    jornada = db.relationship('JornadaVentas', backref=db.backref('cierre', uselist=False))
    
    def __repr__(self):
        return f'<CierreDiario {self.fecha} - ${self.total_ventas:,.0f}>'
    
    
class PermisoUsuario(db.Model):
    __tablename__ = 'permisos_usuario'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    permitido = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Permiso {self.modulo}.{self.accion}: {self.permitido}>'

# =============================================
# FUNCIONES DE APOYO PARA ANÁLISIS ML (agregar al final de models.py)
# =============================================

def calcular_tendencia_ventas(fecha_inicio, fecha_fin):
    """Calcula tendencia de ventas usando datos históricos"""
    try:
        # Período anterior para comparación (misma duración)
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        fecha_inicio_anterior = fecha_inicio - timedelta(days=dias_periodo)
        fecha_fin_anterior = fecha_inicio - timedelta(days=1)
        
        # Ventas período actual
        ventas_actual = Venta.query.filter(
            db.func.date(Venta.fecha_hora) >= fecha_inicio,
            db.func.date(Venta.fecha_hora) <= fecha_fin
        ).all()
        total_actual = sum(venta.total for venta in ventas_actual)
        
        # Ventas período anterior
        ventas_anterior = Venta.query.filter(
            db.func.date(Venta.fecha_hora) >= fecha_inicio_anterior,
            db.func.date(Venta.fecha_hora) <= fecha_fin_anterior
        ).all()
        total_anterior = sum(venta.total for venta in ventas_anterior)
        
        if total_anterior > 0:
            return ((total_actual - total_anterior) / total_anterior) * 100
        return 100 if total_actual > 0 else 0
        
    except Exception as e:
        print(f"Error calculando tendencia: {e}")
        return 0

def analizar_productos_periodo(detalles):
    """Análisis básico de productos en un período (sin categorías)"""
    productos = {}
    
    for detalle in detalles:
        try:
            if detalle.producto:
                key = f"P{detalle.producto.id}"
                nombre = detalle.producto.nombre
                categoria = "Producción"
            elif detalle.producto_externo:
                key = f"E{detalle.producto_externo.id}"
                nombre = detalle.producto_externo.nombre
                categoria = "Externo"
            else:
                continue
            
            if key not in productos:
                productos[key] = {
                    'nombre': nombre,
                    'categoria': categoria,
                    'cantidad': 0,
                    'ingresos': 0,
                    'frecuencia': 0
                }
            
            productos[key]['cantidad'] += detalle.cantidad
            productos[key]['ingresos'] += detalle.cantidad * detalle.precio_unitario
            productos[key]['frecuencia'] += 1
                
        except Exception as e:
            print(f"Error procesando detalle: {e}")
            continue
    
    return productos

def calcular_rotacion_automatica(producto_id):
    """Calcula la rotación automática de un producto basado en ventas históricas"""
    try:
        # Obtener ventas de los últimos 30 días
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        ventas = DetalleVenta.query.join(Venta).filter(
            DetalleVenta.producto_id == producto_id,
            Venta.fecha_hora >= fecha_inicio
        ).all()
        
        # Calcular total vendido en el período
        total_vendido = sum(detalle.cantidad for detalle in ventas)
        
        # Calcular rotación diaria promedio
        rotacion_diaria = total_vendido / 30.0  # Promedio de 30 días
        
        return round(rotacion_diaria, 2)
        
    except Exception as e:
        print(f"Error calculando rotación automática para producto {producto_id}: {e}")
        return 0
    
def actualizar_rotaciones_automaticas():
    """Actualiza las rotaciones automáticas para todos los productos activos"""
    try:
        productos_activos = Producto.query.filter_by(activo=True).all()
        actualizaciones = 0
        
        for producto in productos_activos:
            rotacion = calcular_rotacion_automatica(producto.id)
            
            # Buscar o crear registro en HistorialRotacionProducto
            historial = HistorialRotacionProducto.query.filter_by(
                producto_id=producto.id,
                fecha=datetime.now().date()
            ).first()
            
            if not historial:
                historial = HistorialRotacionProducto(
                    producto_id=producto.id,
                    fecha=datetime.now().date(),
                    rotacion_calculada=rotacion,
                    tipo_calculo='automático'
                )
                db.session.add(historial)
            else:
                historial.rotacion_calculada = rotacion
            
            actualizaciones += 1
        
        db.session.commit()
        return actualizaciones
        
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando rotaciones automáticas: {e}")
        return 0

def calcular_rotacion_automatica_por_nombre(nombre_producto):
    """Calcula rotación automática por nombre de producto"""
    try:
        from app import db
        # Buscar producto por nombre
        producto = Producto.query.filter_by(nombre=nombre_producto).first()
        if producto:
            return calcular_rotacion_automatica(producto.id)
        
        producto_externo = ProductoExterno.query.filter_by(nombre=nombre_producto).first()
        if producto_externo:
            # Para productos externos, cálculo simplificado
            return producto_externo.total_ventas / 30 if producto_externo.total_ventas else 0
            
        return 0
    except Exception as e:
        print(f"Error calculando rotación para {nombre_producto}: {e}")
        return 0

def calcular_proyeccion_ventas(producto_id, dias_proyeccion=7):
    """Calcula proyección de ventas usando datos históricos y ML"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from app import db
        
        # Obtener ventas históricas (últimos 60 días)
        fecha_inicio = datetime.now().date() - timedelta(days=60)
        
        ventas = DetalleVenta.query.join(Venta).filter(
            DetalleVenta.producto_id == producto_id,
            Venta.fecha_hora >= fecha_inicio
        ).all()
        
        if not ventas:
            return {'proyeccion': 0, 'rotacion_actual': 0, 'dias_stock': 999, 'nivel_riesgo': 'BAJO'}
        
        # Agrupar ventas por día
        ventas_por_dia = {}
        for venta in ventas:
            if venta.venta and venta.venta.fecha_hora:
                fecha = venta.venta.fecha_hora.date()
                if fecha not in ventas_por_dia:
                    ventas_por_dia[fecha] = 0
                ventas_por_dia[fecha] += venta.cantidad
        
        # Calcular promedio y tendencia
        ventas_diarias = list(ventas_por_dia.values())
        promedio_ventas = sum(ventas_diarias) / len(ventas_diarias) if ventas_diarias else 0
        
        # Proyección simple
        proyeccion = promedio_ventas * dias_proyeccion
        
        # Obtener stock actual
        producto = Producto.query.get(producto_id)
        stock_actual = producto.stock_actual if producto else 0
        
        # Calcular días de stock restante
        dias_stock = stock_actual / promedio_ventas if promedio_ventas > 0 else 999
        
        # Determinar nivel de riesgo
        if dias_stock < 2:
            nivel_riesgo = 'ALTO'
        elif dias_stock < 5:
            nivel_riesgo = 'MEDIO'
        else:
            nivel_riesgo = 'BAJO'
        
        return {
            'proyeccion': round(proyeccion),
            'rotacion_actual': round(promedio_ventas, 2),
            'dias_stock': round(dias_stock, 1),
            'nivel_riesgo': nivel_riesgo
        }
        
    except Exception as e:
        print(f"Error en proyección para producto {producto_id}: {e}")
        return {'proyeccion': 0, 'rotacion_actual': 0, 'dias_stock': 0, 'nivel_riesgo': 'DESCONOCIDO'}

def generar_recomendacion_stock(producto_id, proyeccion):
    """Genera recomendación inteligente de stock"""
    dias_stock = proyeccion.get('dias_stock', 0)
    nivel_riesgo = proyeccion.get('nivel_riesgo', 'BAJO')
    
    if nivel_riesgo == 'ALTO':
        return "⚠️ PRODUCIR URGENTE - Stock crítico"
    elif nivel_riesgo == 'MEDIO':
        return "📦 Programar producción - Stock bajo"
    else:
        return "✅ Stock adecuado - Monitorear"

def generar_alertas_inteligentes(panaderia_id=None):
    """
    Genera alertas inteligentes basadas en análisis ML
    Args:
        panaderia_id: ID del tenant (si no se pasa, se intenta obtener del contexto)
    """
    alertas = []
    
    # 🔍 Si no se pasa panaderia_id, intentar obtener del contexto
    if panaderia_id is None:
        from flask import session
        if 'panaderia_id' in session:
            panaderia_id = session['panaderia_id']
        else:
            # Si no hay contexto, retornar lista vacía
            return alertas
    
    try:
        # 📊 1. Alertas de stock crítico (SOLO del tenant actual)
        productos_bajo_stock = Producto.query.filter(
            Producto.panaderia_id == panaderia_id,
            Producto.stock_actual <= Producto.stock_minimo
        ).all()
        
        for producto in productos_bajo_stock:
            alertas.append({
                'tipo': 'STOCK_CRITICO',
                'mensaje': f'🔴 Stock crítico: {producto.nombre} ({producto.stock_actual} unidades)',
                'prioridad': 'ALTA',
                'producto': producto.nombre,
                'stock_actual': producto.stock_actual,
                'stock_minimo': producto.stock_minimo
            })
        
        # 📊 2. Alertas de productos sin movimiento (SOLO del tenant actual)
        try:
            productos_sin_ventas = obtener_productos_sin_ventas_recientes(panaderia_id)
            for producto in productos_sin_ventas:
                alertas.append({
                    'tipo': 'SIN_MOVIMIENTO',
                    'mensaje': f'🟡 Sin ventas recientes: {producto.nombre}',
                    'prioridad': 'MEDIA',
                    'producto': producto.nombre
                })
        except Exception as e:
            print(f"Error generando alertas de productos sin movimiento: {e}")
            # Continuar sin estas alertas en lugar de fallar completamente
        
        # 📊 3. Resumen (para mostrar en el dashboard)
        if alertas:
            # Agregar resumen al inicio
            total_criticas = sum(1 for a in alertas if a.get('prioridad') == 'ALTA')
            total_media = sum(1 for a in alertas if a.get('prioridad') == 'MEDIA')
            alertas.insert(0, {
                'tipo': 'RESUMEN',
                'mensaje': f'📋 {len(alertas)} alertas activas ({total_criticas} críticas, {total_media} media)',
                'prioridad': 'INFO'
            })
        else:
            alertas.append({
                'tipo': 'EXITO',
                'mensaje': '✅ Todo en orden. No hay alertas activas para esta panadería.',
                'prioridad': 'INFO'
            })
        
        return alertas
        
    except Exception as e:
        print(f"Error general en generar_alertas_inteligentes: {e}")
        return [{
            'tipo': 'ERROR',
            'mensaje': '⚠️ Error al generar alertas. Intenta nuevamente.',
            'prioridad': 'INFO'
        }]
    

def obtener_productos_sin_ventas_recientes(panaderia_id=None, dias=7):
    """
    Identifica productos sin ventas en los últimos días - Versión segura
    Args:
        panaderia_id: ID del tenant (obligatorio para filtrar)
        dias: Número de días a considerar
    """
    from datetime import datetime, timedelta
    
    # 🔍 Si no se pasa panaderia_id, intentar obtener del contexto
    if panaderia_id is None:
        from flask import session
        if 'panaderia_id' in session:
            panaderia_id = session['panaderia_id']
        else:
            # Si no hay contexto, retornar lista vacía
            return []
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    try:
        # 🔍 Obtener todos los IDs de ventas recientes del tenant actual
        ventas_recientes = Venta.query.filter(
            Venta.panaderia_id == panaderia_id,  # ✅ FILTRO POR TENANT
            Venta.fecha_hora >= fecha_limite
        ).with_entities(Venta.id).all()
        
        venta_ids = [vr[0] for vr in ventas_recientes]
        
        if not venta_ids:
            # Si no hay ventas recientes, todos los productos del tenant están sin ventas
            return Producto.query.filter(
                Producto.panaderia_id == panaderia_id,  # ✅ FILTRO POR TENANT
                Producto.activo == True
            ).all()
        
        # 🔍 Obtener productos que SÍ tienen ventas recientes (del tenant actual)
        productos_con_ventas = DetalleVenta.query.filter(
            DetalleVenta.venta_id.in_(venta_ids),
            DetalleVenta.producto_id.isnot(None)
        ).with_entities(DetalleVenta.producto_id).distinct().all()
        
        ids_con_ventas = [pcv[0] for pcv in productos_con_ventas if pcv[0] is not None]
        
        # 🔍 Productos activos del tenant que NO están en la lista de con ventas
        productos_sin_ventas = Producto.query.filter(
            Producto.panaderia_id == panaderia_id,  # ✅ FILTRO POR TENANT
            Producto.activo == True,
            ~Producto.id.in_(ids_con_ventas) if ids_con_ventas else True
        ).all()
        
        return productos_sin_ventas
        
    except Exception as e:
        print(f"Error en obtener_productos_sin_ventas_recientes: {e}")
        # En caso de error, retornar lista vacía para no romper el sistema
        return []



# =============================================
# FUNCIONES PARA CIERRE DIARIO - AGREGAR DESPUÉS DE LAS FUNCIONES ML
# =============================================

def obtener_jornada_activa():
    """Obtiene o crea la jornada activa del día actual"""
    hoy = datetime.now().date()
    jornada = JornadaVentas.query.filter_by(fecha=hoy).first()
    
    if not jornada:
        jornada = JornadaVentas(fecha=hoy, estado='ACTIVA')
        db.session.add(jornada)
        db.session.commit()
    
    return jornada

def cerrar_jornada_actual():
    """Cierra la jornada actual y crea registro de cierre"""
    hoy = datetime.now().date()
    jornada = JornadaVentas.query.filter_by(fecha=hoy, estado='ACTIVA').first()
    
    if not jornada:
        return None, "No hay jornada activa para cerrar"
    
    try:
        # Obtener ventas del día
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())
        
        ventas_dia = Venta.query.filter(
            Venta.fecha_hora >= inicio_dia,
            Venta.fecha_hora <= fin_dia
        ).all()
        
        # Calcular totales
        total_ventas = sum(venta.total for venta in ventas_dia)
        total_efectivo = sum(v.total for v in ventas_dia if v.metodo_pago == 'efectivo')
        total_transferencia = sum(v.total for v in ventas_dia if v.metodo_pago == 'transferencia')
        
        
        # Obtener productos más vendidos
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
        
        # Calcular comparativa con día anterior
        dia_anterior = hoy - timedelta(days=1)
        ventas_anterior = Venta.query.filter(
            db.func.date(Venta.fecha_hora) == dia_anterior
        ).all()
        total_anterior = sum(v.total for v in ventas_anterior)
        
        tendencia = 0
        if total_anterior > 0:
            tendencia = ((total_ventas - total_anterior) / total_anterior) * 100
        
        # Crear registro de cierre
        cierre = CierreDiario(
            fecha=hoy,
            jornada_id=jornada.id,
            total_ventas=total_ventas,
            total_efectivo=total_efectivo,
            
            total_transacciones=len(ventas_dia),
            productos_top=json.dumps(productos_top),
            ventas_dia_anterior=total_anterior,
            tendencia=tendencia
        )
        
        # Cerrar jornada
        jornada.estado = 'CERRADA'
        jornada.cerrada_at = datetime.utcnow()
        jornada.total_ventas = total_ventas
        jornada.total_efectivo = total_efectivo
        jornada.total_transferencia = total_transferencia
        
        
        db.session.add(cierre)
        db.session.commit()
        
        return cierre, "Jornada cerrada exitosamente"
        
    except Exception as e:
        db.session.rollback()
        return None, f"Error al cerrar jornada: {str(e)}"

def obtener_ventas_dia(fecha=None):
    """Obtiene ventas de un día específico (hoy por defecto)"""
    if not fecha:
        fecha = datetime.now().date()
    
    inicio_dia = datetime.combine(fecha, datetime.min.time())
    fin_dia = datetime.combine(fecha, datetime.max.time())
    
    return Venta.query.filter(
        Venta.fecha_hora >= inicio_dia,
        Venta.fecha_hora <= fin_dia
    ).all()

def obtener_historial_cierres(limite=30):
    """Obtiene historial de cierres recientes"""
    return CierreDiario.query.order_by(CierreDiario.fecha.desc()).limit(limite).all()
    

# ======================================= NUEVO MÓDULO FINANCIERO MEJORADO =================================================
# ======================================= NUEVO MÓDULO FINANCIERO MEJORADO =================================================

class RegistroDiario(db.Model):
    """Registro diario simplificado para el usuario"""
    __tablename__ = 'registros_diarios'
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    fecha = db.Column(db.Date, nullable=False, default=datetime.now().date)
    
    # INGRESOS
    venta_total = db.Column(db.Float, default=0)
    efectivo = db.Column(db.Float, default=0)
    transferencias = db.Column(db.Float, default=0)
    
    
    # EGRESOS
    gasto_proveedores = db.Column(db.Float, default=0)
    gasto_servicios = db.Column(db.Float, default=0)
    gasto_nomina = db.Column(db.Float, default=0)
    gasto_alquiler = db.Column(db.Float, default=0)
    gasto_otros = db.Column(db.Float, default=0)
    
    # INFORMACIÓN ADICIONAL
    descripcion_gastos = db.Column(db.String(300))
    numero_factura = db.Column(db.String(100))
    
    # CÁLCULOS AUTOMÁTICOS
    total_ingresos = db.Column(db.Float, default=0)
    total_egresos = db.Column(db.Float, default=0)
    saldo_dia = db.Column(db.Float, default=0)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def calcular_totales(self):
        """Calcula automáticamente los totales con manejo seguro de None"""
        try:
            # Convertir None a 0 para evitar errores
            self.efectivo = self.efectivo or 0
            self.transferencias = self.transferencias or 0            # self.tarjetas = self.tarjetas or 0  # campo eliminado
            self.total_ingresos = self.efectivo + self.transferencias
            
            # Convertir None a 0 en gastos
            self.gasto_proveedores = self.gasto_proveedores or 0
            self.gasto_servicios = self.gasto_servicios or 0
            self.gasto_nomina = self.gasto_nomina or 0
            self.gasto_alquiler = self.gasto_alquiler or 0
            self.gasto_otros = self.gasto_otros or 0
            
            self.total_egresos = (self.gasto_proveedores + self.gasto_servicios + 
                                self.gasto_nomina + self.gasto_alquiler + self.gasto_otros)
            self.saldo_dia = self.total_ingresos - self.total_egresos
        except Exception as e:
            print(f"Error en calcular_totales: {e}")
            # Valores por defecto en caso de error
            self.total_ingresos = 0
            self.total_egresos = 0
            self.saldo_dia = 0
    
    def validar_cierre_caja(self):
        """Valida que los métodos de pago coincidan con el total vendido"""
        try:
            suma_metodos = (self.efectivo or 0) + (self.transferencias or 0) 
            diferencia = abs(suma_metodos - (self.venta_total or 0))
            
            # Permitir pequeñas diferencias por redondeo (menos de $1)
            return diferencia <= 1, suma_metodos, diferencia
        except Exception as e:
            print(f"Error en validar_cierre_caja: {e}")
            return False, 0, 0
    
    def __repr__(self):
        return f'<RegistroDiario {self.fecha} - Ingresos: ${self.total_ingresos}>'

class SaldoBanco(db.Model):
    """Seguimiento del saldo bancario actual"""
    __tablename__ = 'saldos_banco'
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now)
    saldo_actual = db.Column(db.Float, default=0)
    comentario = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<SaldoBanco ${self.saldo_actual}>'
    
class DepositoBancario(db.Model):
    """Modelo para registrar depósitos bancarios - 100% MULTI-TENANT"""
    __tablename__ = 'depositos_bancarios'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ CRÍTICO: Aislamiento multi-tenant
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False)
    
    # Información básica del depósito
    fecha_deposito = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200))
    referencia = db.Column(db.String(50))
    cuenta_bancaria = db.Column(db.String(100))
    metodo_deposito = db.Column(db.String(50))  # 'efectivo', 'transferencia', 'cheque'
    
    # Estado del depósito
    estado = db.Column(db.String(20), default='REGISTRADO')  # REGISTRADO, CONCILIADO, ANULADO
    fecha_conciliacion = db.Column(db.Date)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    panaderia = db.relationship('Panaderia', backref=db.backref('depositos_bancarios', lazy=True))
    
    def __repr__(self):
        return f'<DepositoBancario {self.id}: ${self.monto} - {self.fecha_deposito}>'
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'panaderia_id': self.panaderia_id,
            'fecha_deposito': self.fecha_deposito.isoformat() if self.fecha_deposito else None,
            'monto': self.monto,
            'descripcion': self.descripcion,
            'referencia': self.referencia,
            'cuenta_bancaria': self.cuenta_bancaria,
            'metodo_deposito': self.metodo_deposito,
            'estado': self.estado,
            'fecha_conciliacion': self.fecha_conciliacion.isoformat() if self.fecha_conciliacion else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
# === NUEVA CLASE PARA PAGOS INDIVIDUALES ===

class PagoIndividual(db.Model): 
    """Registro individual de cada pago"""
    __tablename__ = 'pagos_individuales'
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    fecha_pago = db.Column(db.Date, nullable=False)
    
    # Información del pago
    categoria = db.Column(db.String(50), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    referencia = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    numero_factura = db.Column(db.String(100))
    
    # Relaciones
    proveedor = db.relationship('Proveedor', backref='pagos')
    
    def __repr__(self):
        return f'<Pago {self.categoria} - ${self.monto}>'
    
# ============================================ MODELO DE ACTIVOS FIJOS ========================================================
# === MODELO DE ACTIVOS FIJOS ===
class ActivoFijo(db.Model):
    __tablename__ = 'activos_fijos'
    
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    numero_serie = db.Column(db.String(100))
    fecha_compra = db.Column(db.Date, nullable=False)
    proveedor = db.Column(db.String(200))
    valor_compra = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(100))
    vida_util = db.Column(db.Integer)  # en años
    valor_residual = db.Column(db.Float, default=0)
    metodo_depreciacion = db.Column(db.String(50), default='LINEAL')
    ubicacion = db.Column(db.String(200))
    estado = db.Column(db.String(50), default='ACTIVO')  # ACTIVO, MANTENIMIENTO, BAJA
    responsable = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    fecha_baja = db.Column(db.Date)
    
    def calcular_depreciacion_mensual(self):
        if self.vida_util and self.vida_util > 0:
            depreciacion_anual = (self.valor_compra - self.valor_residual) / self.vida_util
            return depreciacion_anual / 12
        return 0
    
    def depreciacion_acumulada(self):
        if not self.fecha_compra:
            return 0
            
        meses_transcurridos = (datetime.now().date() - self.fecha_compra).days // 30
        return min(meses_transcurridos * self.calcular_depreciacion_mensual(), 
                  self.valor_compra - self.valor_residual)
    
    def valor_actual(self):
        return self.valor_compra - self.depreciacion_acumulada()

# Categorías predefinidas para activos fijos
CATEGORIAS_ACTIVOS = {
    "MAQUINARIA_EQUIPOS": "Maquinaria y Equipos",
    "EQUIPOS_TECNOLOGICOS": "Equipos Tecnológicos", 
    "MOBILIARIO": "Mobiliario y Mesas",
    "HERRAMIENTAS": "Herramientas de Panadería",
    "VEHICULOS": "Vehículos de Reparto",
    "INSTALACIONES": "Instalaciones y Mejoras",
    "SOFTWARE": "Software y Licencias",
    "LICENCIAS_PERMISOS": "Licencias y Permisos",
    "SEÑALETICA": "Señalética y Publicidad",
    "SEGURIDAD": "Equipos de Seguridad"
}

# ====================================== 🆕 NUEVOS MODELOS PARA SISTEMA POS/FACTURACIÓN =====================================

class ConsecutivoPOS(db.Model):
    """Maneja el consecutivo persistente para recibos POS"""
    __tablename__ = 'consecutivos_pos'
    
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    id = db.Column(db.Integer, primary_key=True)
    numero_actual = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConsecutivoPOS: {self.numero_actual}>'

class ConfiguracionSistema(db.Model):
    """Configuración global del sistema"""
    __tablename__ = 'configuracion_sistema'
    panaderia_id = db.Column(db.Integer, nullable=False, default=1)
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_facturacion = db.Column(db.String(20), default='POS')  # 'POS' o 'ELECTRONICA'
    nombre_empresa = db.Column(db.String(200), default='Mi Panadería')
    nit_empresa = db.Column(db.String(20), default='')
    direccion_empresa = db.Column(db.String(300), default='')
    telefono_empresa = db.Column(db.String(20), default='')
    ciudad_empresa = db.Column(db.String(100), default='')
    regimen_empresa = db.Column(db.String(100), default='Simplificado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConfiguracionSistema: {self.tipo_facturacion}>'
    
# =============================================
# 🆕 FUNCIONES DE VERIFICACIÓN DE LÍMITES
# =============================================

def obtener_configuracion_panaderia(panaderia_id=1):
    """Obtiene la configuración de la panadería (por defecto ID 1)"""
    config = ConfiguracionPanaderia.query.get(panaderia_id)
    if not config:
        # Crear configuración por defecto si no existe
        config = ConfiguracionPanaderia(
            id=panaderia_id,        
            nombre_panaderia="Panadería Principal",
            tipo_licencia="local"
        )
        db.session.add(config)
        db.session.commit()
    return config

def verificar_limite_usuarios():
    """Verifica si se ha alcanzado el límite de usuarios"""
    config = obtener_configuracion_panaderia()
    return not config.puede_crear_usuario

def obtener_limites_panaderia():
    """Obtiene información de límites actuales"""
    config = obtener_configuracion_panaderia()
    return {
        'max_usuarios': config.max_usuarios,
        'usuarios_actuales': config.usuarios_activos_count,
        'usuarios_restantes': config.usuarios_restantes,
        'puede_crear_usuario': config.puede_crear_usuario,
        'tipo_licencia': config.tipo_licencia,
        'suscripcion_activa': config.suscripcion_activa
    }
    
# ============================================
# MODELO: LogSistema - REGISTRO DE ACTIVIDADES
# ============================================

class LogSistema(db.Model):
    __tablename__ = 'logs_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)  # 'cierre_diario', 'login', 'crear_venta', etc.
    modulo = db.Column(db.String(30))  # 'finanzas', 'ventas', 'inventario', etc.
    descripcion = db.Column(db.String(500))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    datos_adicionales = db.Column(db.JSON)    # Datos adicionales en formato JSON
    
    # Relaciones
    panaderia = db.relationship('Panaderia', backref='logs_sistema', lazy=True)
    usuario = db.relationship('Usuario', backref='logs_sistema', lazy=True)
    def __repr__(self):
        return f'<LogSistema {self.id}: {self.accion} - {self.fecha_hora}>'


# ============================================
# MODELO: RegistroFinanciero - CONTROL DE SALDOS
# ============================================

class RegistroFinanciero(db.Model):
    __tablename__ = 'registros_financieros'
    
    id = db.Column(db.Integer, primary_key=True)
    panaderia_id = db.Column(db.Integer, db.ForeignKey('panaderias.id'), nullable=False, unique=True)
    
    # Saldos actuales
    saldo_disponible = db.Column(db.Float, default=0.0)  # Dinero en cuentas bancarias
    saldo_pendiente = db.Column(db.Float, default=0.0)   # Efectivo por depositar
    saldo_tarjetas = db.Column(db.Float, default=0.0)    # Tarjetas por cobrar
    saldo_total = db.Column(db.Float, default=0.0)       # Suma de todos los saldos
    
    # Control de cierres
    ultimo_cierre_fecha = db.Column(db.Date)
    ultimo_cierre_monto = db.Column(db.Float, default=0.0)
    
    # Estadísticas
    ventas_mes_actual = db.Column(db.Float, default=0.0)
    gastos_mes_actual = db.Column(db.Float, default=0.0)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    panaderia = db.relationship('Panaderia', backref='registro_financiero', lazy=True)
    
    def actualizar_saldos(self):
        """Actualiza automáticamente los saldos totales"""
        self.saldo_total = self.saldo_disponible + self.saldo_pendiente + self.saldo_tarjetas
        self.fecha_actualizacion = datetime.utcnow()
    
    def __repr__(self):
        return f'<RegistroFinanciero Panadería {self.panaderia_id}: ${self.saldo_total}>'

# =============================================
# ANÁLISIS DE TENDENCIAS (NIVEL 2)
# =============================================

def analizar_tendencias_ventas(panaderia_id, dias_historial=30):
    """
    Analiza tendencias de ventas usando estadísticas básicas y patrones
    Args:
        panaderia_id: ID del tenant
        dias_historial: Número de días a analizar
    Returns:
        dict: Información de tendencias y patrones
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    import statistics
    
    try:
        # 1. Obtener ventas diarias del período
        fecha_inicio = datetime.now() - timedelta(days=dias_historial)
        
        ventas_diarias = db.session.query(
            func.date(Venta.fecha_hora).label('fecha'),
            func.sum(Venta.total).label('total')
        ).filter(
            Venta.panaderia_id == panaderia_id,
            Venta.fecha_hora >= fecha_inicio
        ).group_by(
            func.date(Venta.fecha_hora)
        ).order_by(
            func.date(Venta.fecha_hora)
        ).all()
        
        # 2. Si no hay suficientes datos
        if len(ventas_diarias) < 7:
            return {
                'tiene_datos_suficientes': False,
                'mensaje': 'Se necesitan al menos 7 días de datos para analizar tendencias.',
                'dias_analizados': len(ventas_diarias),
                'tendencia': 'insuficiente_datos',
                'recomendacion': 'Continúa registrando ventas para generar análisis más precisos.'
            }
        
        # 3. Calcular métricas básicas
        valores_ventas = [v.total for v in ventas_diarias]
        promedio = statistics.mean(valores_ventas) if valores_ventas else 0
        maximo = max(valores_ventas) if valores_ventas else 0
        minimo = min(valores_ventas) if valores_ventas else 0
        mediana = statistics.median(valores_ventas) if valores_ventas else 0
        
        # 4. Calcular tendencia (comparar última semana con semana anterior)
        mitad = len(valores_ventas) // 2
        primera_mitad = valores_ventas[:mitad]
        segunda_mitad = valores_ventas[mitad:]
        
        promedio_primera = statistics.mean(primera_mitad) if primera_mitad else 0
        promedio_segunda = statistics.mean(segunda_mitad) if segunda_mitad else 0
        
        cambio_porcentaje = ((promedio_segunda - promedio_primera) / promedio_primera * 100) if promedio_primera > 0 else 0
        
        # 5. Identificar días con mayor venta
        dias_con_mayor_venta = []
        for i, venta in enumerate(ventas_diarias):
            if venta.total > promedio * 1.4:  # 40% por encima del promedio
                dias_con_mayor_venta.append(i)
        
        # 6. Identificar días con menor venta
        dias_con_menor_venta = []
        for i, venta in enumerate(ventas_diarias):
            if venta.total < promedio * 0.6:  # 40% por debajo del promedio
                dias_con_menor_venta.append(i)
        
        # 7. Determinar tendencia general
        if cambio_porcentaje > 10:
            tendencia_general = 'creciente'
            icono_tendencia = '📈'
            color_tendencia = 'success'
        elif cambio_porcentaje < -10:
            tendencia_general = 'decreciente'
            icono_tendencia = '📉'
            color_tendencia = 'danger'
        else:
            tendencia_general = 'estable'
            icono_tendencia = '➡️'
            color_tendencia = 'warning'
        
        # 8. Generar recomendaciones
        recomendaciones = []
        if dias_con_mayor_venta:
            recomendaciones.append(
                f"Los días {', '.join([str(i+1) for i in dias_con_mayor_venta[:3]])} tuvieron ventas excepcionales. "
                "Considera aumentar inventario para esos días."
            )
        if dias_con_menor_venta:
            recomendaciones.append(
                "Hay días con ventas por debajo del promedio. "
                "Considera promociones especiales o descuentos para esos días."
            )
        if cambio_porcentaje > 15:
            recomendaciones.append(
                f"📈 Las ventas están creciendo un {cambio_porcentaje:.1f}%. "
                "¡Excelente tendencia! Mantén el ritmo."
            )
        elif cambio_porcentaje < -15:
            recomendaciones.append(
                f"📉 Las ventas están disminuyendo un {abs(cambio_porcentaje):.1f}%. "
                "Revisa estrategias de marketing o promociones."
            )
        
        if not recomendaciones:
            recomendaciones.append("✅ Las ventas se mantienen estables. Sigue así.")
        
        return {
            'tiene_datos_suficientes': True,
            'dias_analizados': len(ventas_diarias),
            'promedio_diario': promedio,
            'maximo_diario': maximo,
            'minimo_diario': minimo,
            'mediana_diaria': mediana,
            'cambio_porcentaje': cambio_porcentaje,
            'tendencia_general': tendencia_general,
            'icono_tendencia': icono_tendencia,
            'color_tendencia': color_tendencia,
            'dias_pico': len(dias_con_mayor_venta),
            'dias_bajos': len(dias_con_menor_venta),
            'recomendaciones': recomendaciones,
            'ventas_diarias': [{'fecha': v.fecha, 'total': v.total} for v in ventas_diarias],
            'mensaje': f"📊 Análisis de {len(ventas_diarias)} días de actividad."
        }
        
    except Exception as e:
        print(f"Error en analizar_tendencias_ventas: {e}")
        return {
            'tiene_datos_suficientes': False,
            'mensaje': f"Error al analizar tendencias: {str(e)}",
            'tendencia': 'error'
        }
        
# =============================================
# PREDICCIONES CON ML (NIVEL 3)
# =============================================

def predecir_ventas_futuras(panaderia_id, dias_a_predecir=7, dias_historial=30):
    """
    Predice ventas futuras usando regresión lineal simple
    Args:
        panaderia_id: ID del tenant
        dias_a_predecir: Número de días a predecir
        dias_historial: Número de días de historial a usar
    Returns:
        dict: Predicciones y métricas de confianza
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    import statistics
    import math
    
    try:
        # 1. Obtener ventas diarias del historial
        fecha_inicio = datetime.now() - timedelta(days=dias_historial)
        
        ventas_historial = db.session.query(
            func.date(Venta.fecha_hora).label('fecha'),
            func.sum(Venta.total).label('total')
        ).filter(
            Venta.panaderia_id == panaderia_id,
            Venta.fecha_hora >= fecha_inicio
        ).group_by(
            func.date(Venta.fecha_hora)
        ).order_by(
            func.date(Venta.fecha_hora)
        ).all()
        
        # 2. Verificar suficiencia de datos
        if len(ventas_historial) < 7:
            return {
                'disponible': False,
                'mensaje': 'Se necesitan al menos 7 días de datos para hacer predicciones.',
                'dias_historial': len(ventas_historial)
            }
        
        # 3. Preparar datos para regresión lineal
        valores = [v.total for v in ventas_historial]
        dias = list(range(len(valores)))
        
        # 4. Calcular regresión lineal simple
        n = len(dias)
        sum_x = sum(dias)
        sum_y = sum(valores)
        sum_xy = sum(dias[i] * valores[i] for i in range(n))
        sum_x2 = sum(x**2 for x in dias)
        
        # Pendiente (m) e intercepto (b)
        m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2) if (n * sum_x2 - sum_x**2) != 0 else 0
        b = (sum_y - m * sum_x) / n if n > 0 else 0
        
        # 5. Calcular error estándar (confianza)
        if n > 2:
            predicciones_historial = [m * x + b for x in dias]
            errores = [valores[i] - predicciones_historial[i] for i in range(n)]
            mse = sum(e**2 for e in errores) / (n - 2) if n > 2 else 0
            std_error = math.sqrt(mse) if mse > 0 else 0
        else:
            std_error = 0
        
        # 6. Generar predicciones
        predicciones = []
        for i in range(1, dias_a_predecir + 1):
            dia = len(valores) + i
            valor_predicho = max(0, round(m * dia + b, 0))  # No puede ser negativo
            
            # Calcular intervalo de confianza (68-95-99.7 rule)
            if std_error > 0:
                intervalo_inferior = max(0, round(valor_predicho - std_error, 0))
                intervalo_superior = round(valor_predicho + std_error, 0)
            else:
                intervalo_inferior = round(valor_predicho * 0.8, 0)
                intervalo_superior = round(valor_predicho * 1.2, 0)
            
            fecha_predicha = datetime.now() + timedelta(days=i)
            
            predicciones.append({
                'dia': i,
                'fecha': fecha_predicha.strftime('%d/%m/%Y'),
                'prediccion': valor_predicho,
                'intervalo_inferior': intervalo_inferior,
                'intervalo_superior': intervalo_superior,
                'confianza': 'Alta' if std_error < valor_predicho * 0.1 else 'Media' if std_error < valor_predicho * 0.2 else 'Baja'
            })
        
        # 7. Determinar tendencia general
        tendencia = 'creciente' if m > 5 else 'decreciente' if m < -5 else 'estable'
        mensaje_tendencia = '📈 Tendencia creciente' if tendencia == 'creciente' else '📉 Tendencia decreciente' if tendencia == 'decreciente' else '➡️ Tendencia estable'
        
        return {
            'disponible': True,
            'predicciones': predicciones,
            'tendencia': tendencia,
            'mensaje_tendencia': mensaje_tendencia,
            'dias_historial': len(ventas_historial),
            'pendiente': m,
            'intercepto': b,
            'error_estandar': std_error,
            'promedio_historico': statistics.mean(valores) if valores else 0,
            'mensaje': f"📊 Predicciones basadas en {len(ventas_historial)} días de datos históricos."
        }
        
    except Exception as e:
        print(f"Error en predecir_ventas_futuras: {e}")
        return {
            'disponible': False,
            'mensaje': f"Error al generar predicciones: {str(e)}",
            'tendencia': 'error'
        }
# =============================================
# RECOMENDACIONES PERSONALIZADAS (NIVEL 4)
# =============================================

def generar_recomendaciones_personalizadas(panaderia_id, dias_historial=30):
    """
    Genera recomendaciones personalizadas basadas en análisis de datos
    Args:
        panaderia_id: ID del tenant
        dias_historial: Número de días a analizar
    Returns:
        dict: Recomendaciones personalizadas por categoría
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    try:
        fecha_inicio = datetime.now() - timedelta(days=dias_historial)
        recomendaciones = []
        tiene_datos = False
        
        # 1. RECOMENDACIÓN: Productos con stock crítico
        productos_criticos = Producto.query.filter(
            Producto.panaderia_id == panaderia_id,
            Producto.stock_actual <= Producto.stock_minimo,
            Producto.activo == True
        ).all()
        
        if productos_criticos:
            tiene_datos = True
            recomendaciones.append({
                'categoria': 'stock_critico',
                'titulo': '🔴 Stock Crítico',
                'mensaje': f'Tienes {len(productos_criticos)} productos con stock por debajo del mínimo.',
                'accion': 'Revisa y reabastece estos productos urgentemente.',
                'productos': [p.nombre for p in productos_criticos[:5]],
                'prioridad': 'alta'
            })
        
        # 2. RECOMENDACIÓN: Productos más rentables
        productos_rentables = db.session.query(
            Producto,
            db.func.sum(DetalleVenta.cantidad).label('total_vendido')
        ).join(DetalleVenta).join(Venta).filter(
            Venta.panaderia_id == panaderia_id,
            Venta.fecha_hora >= fecha_inicio,
            DetalleVenta.producto_id.isnot(None)
        ).group_by(Producto.id).order_by(
            db.desc('total_vendido')
        ).limit(5).all()
        
        if productos_rentables:
            tiene_datos = True
            recomendaciones.append({
                'categoria': 'productos_populares',
                'titulo': '📈 Productos Más Vendidos',
                'mensaje': 'Estos productos generan la mayoría de tus ingresos.',
                'accion': 'Asegura suficiente stock y considera promociones cruzadas.',
                'productos': [p.nombre for p, total in productos_rentables[:3]],
                'prioridad': 'media'
            })
        
        # 3. RECOMENDACIÓN: Productos sin ventas recientes
        productos_olvidados = Producto.query.filter(
            Producto.panaderia_id == panaderia_id,
            Producto.activo == True
        ).all()
        
        productos_sin_ventas = []
        for producto in productos_olvidados:
            ventas_recientes = DetalleVenta.query.join(Venta).filter(
                Venta.panaderia_id == panaderia_id,
                DetalleVenta.producto_id == producto.id,
                Venta.fecha_hora >= fecha_inicio
            ).count()
            if ventas_recientes == 0 and producto.stock_actual > 0:
                productos_sin_ventas.append(producto)
        
        if productos_sin_ventas:
            tiene_datos = True
            recomendaciones.append({
                'categoria': 'productos_inactivos',
                'titulo': '📉 Productos Sin Movimiento',
                'mensaje': f'Tienes {len(productos_sin_ventas)} productos que no han vendido en {dias_historial} días.',
                'accion': 'Considera promociones especiales o descuentos para reactivarlos.',
                'productos': [p.nombre for p in productos_sin_ventas[:3]],
                'prioridad': 'media'
            })
        
        # 4. RECOMENDACIÓN: Días de mayor venta (basado en tendencias)
        ventas_por_dia = db.session.query(
            func.strftime('%w', Venta.fecha_hora).label('dia_semana'),
            func.sum(Venta.total).label('total')
        ).filter(
            Venta.panaderia_id == panaderia_id,
            Venta.fecha_hora >= fecha_inicio
        ).group_by(
            func.strftime('%w', Venta.fecha_hora)
        ).order_by(
            func.sum(Venta.total).desc()
        ).all()
        
        if ventas_por_dia:
            dias_semana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
            mejores_dias = []
            for dia, total in ventas_por_dia[:3]:
                if total > 0:
                    mejores_dias.append(dias_semana[int(dia)])
            
            if mejores_dias:
                tiene_datos = True
                recomendaciones.append({
                    'categoria': 'mejores_dias',
                    'titulo': '📅 Mejores Días de Ventas',
                    'mensaje': f'Los mejores días para tus ventas son: {", ".join(mejores_dias)}.',
                    'accion': 'Aumenta inventario y personal en estos días clave.',
                    'productos': mejores_dias,
                    'prioridad': 'baja'
                })
        
        # 5. RECOMENDACIÓN: Análisis de tendencia general
        if len(productos_rentables) > 0 or len(productos_sin_ventas) > 0:
            tendencia_recomendacion = {
                'categoria': 'tendencia_general',
                'titulo': '📊 Resumen de Análisis',
                'mensaje': 'Basado en el análisis de tus datos, te recomendamos:',
                'accion': 'Mantén el enfoque en productos populares y reactiva productos inactivos.',
                'productos': [],
                'prioridad': 'media'
            }
            
            if productos_rentables:
                tendencia_recomendacion['productos'].append(
                    f'✅ Mantén stock de: {", ".join([p.nombre for p, _ in productos_rentables[:2]])}'
                )
            if productos_sin_ventas:
                tendencia_recomendacion['productos'].append(
                    f'⚠️ Revisa promociones para: {", ".join([p.nombre for p in productos_sin_ventas[:2]])}'
                )
            if productos_criticos:
                tendencia_recomendacion['productos'].append(
                    f'🔴 Urgente: Reabastece {", ".join([p.nombre for p in productos_criticos[:2]])}'
                )
            
            if len(tendencia_recomendacion['productos']) > 0:
                tiene_datos = True
                recomendaciones.append(tendencia_recomendacion)
        
        # 6. RECOMENDACIÓN: Si no hay datos suficientes
        if not tiene_datos:
            return {
                'disponible': False,
                'mensaje': 'No hay suficientes datos para generar recomendaciones personalizadas.',
                'recomendaciones': [],
                'sugerencia': 'Continúa registrando ventas y productos para recibir recomendaciones.'
            }
        
        return {
            'disponible': True,
            'recomendaciones': recomendaciones,
            'total_recomendaciones': len(recomendaciones),
            'mensaje': f'📊 {len(recomendaciones)} recomendaciones generadas para tu negocio.'
        }
        
    except Exception as e:
        print(f"Error en generar_recomendaciones_personalizadas: {e}")
        return {
            'disponible': False,
            'mensaje': f"Error al generar recomendaciones: {str(e)}",
            'recomendaciones': [],
            'sugerencia': 'Intenta nuevamente más tarde.'
        }
# =============================================
# HELPER PARA FILTRAR POR TENANT
# =============================================

def filtrar_por_tenant(query, panaderia_id):
    """
    Filtra una consulta por panaderia_id si el modelo tiene ese campo
    Args:
        query: Consulta de SQLAlchemy
        panaderia_id: ID del tenant
    Returns:
        Consulta filtrada
    """
    if panaderia_id is None:
        return query
    
    # Verificar si el modelo tiene la columna panaderia_id
    model = query.column_descriptions[0]['entity']
    if hasattr(model, 'panaderia_id'):
        return query.filter(model.panaderia_id == panaderia_id)
    return query
        
# =============================================
# FIN DE MODELS.PY
# ============================================= 