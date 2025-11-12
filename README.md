# 🏪 Sistema ERP Panadería - Gestión Multicliente

## 👋 ¡Bienvenido/a!

¡Hola! Soy **Mauricio**, desarrollador de sistemas POS registrado en Cámara de Comercio. 
Este proyecto representa meses de dedicación creando una solución completa para panaderías.

### 💝 Mi Motivación
Desarrollé este sistema para ayudar a pequeños y medianos empresarios de panaderías 
a digitalizar sus operaciones y crecer sus negocios de manera profesional.

### 🤝 Para Visitantes
- **¿Eres desarrollador?** ¡Tu feedback es invaluable!
- **¿Tienes una panadería?** Próximamente disponible como servicio en la nube
- **¿Te gusta el proyecto?** ⭐ Dale una estrella en GitHub
- **¿Tienes ideas?** ¡Abre un issue y hablemos!

### 🚀 Estado Actual
✅ **Versión funcional completa** - Sistema 100% operativo  
🔧 **Desarrollo activo** - Mejorando continuamente  
🌐 **Próximamente** - Servicio SaaS en la nube

---

*"Crear software que realmente ayude a los negocios es mi pasión"* 🎯



# 🏪 Sistema ERP Panadería - Gestión Multicliente

## 📋 Descripción General
Sistema de gestión integral para panaderías con arquitectura multicliente. Desarrollado en Python/Flask con funcionalidades completas de POS, inventario, producción y reportes financieros.

## 🚀 Características Principales

### 🔐 Autenticación y Roles
- **Super Admin:** Acceso completo al sistema multicliente
- **Administrador:** Gestión de una panadería específica  
- **Usuario:** Operaciones básicas de venta y consulta
- **Login seguro** con gestión de sesiones

### 🏪 Módulo Punto de Venta (POS)
- Interfaz moderna y responsive
- Búsqueda rápida de productos
- Cálculo automático de totales
- Gestión de métodos de pago
- Impresión de tickets
- Cierre de caja diario

### 📦 Gestión de Inventario
- Control de materias primas
- Gestión de productos terminados
- Alertas de stock bajo
- Proveedores y compras
- Productos externos (no producidos)

### 🍞 Producción y Recetas
- Gestión de recetas con costos
- Control de producción diaria
- Cálculo automático de rendimientos
- Relación productos-materias primas

### 📊 Reportes y Analytics
- Ventas por período
- Productos más vendidos
- Análisis de rentabilidad
- Reportes financieros
- Producción vs Ventas

### 🏢 Arquitectura Multicliente
- Base de datos segregada por panadería
- Configuración independiente por cliente
- Super admin con visión global

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.10+** - Lenguaje principal
- **Flask 3.1.2** - Framework web
- **SQLAlchemy 2.0** - ORM database
- **Flask-Login** - Autenticación
- **Werkzeug** - Seguridad de contraseñas

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript** - Interactividad
- **Bootstrap** - Framework CSS
- **Chart.js** - Gráficos y reportes

### Base de Datos
- **SQLite** (desarrollo)
- **MySQL** compatible (producción)
- **Alembic** para migraciones

### Reportes
- **PDF** generación automática
- **Excel** exportación de datos
- **Gráficos** interactivos

## 📥 Instalación y Configuración

### Prerrequisitos
- Python 3.10 o superior
- pip (gestor de paquetes)
- Git

### Pasos de Instalación
```bash
# 1. Clonar repositorio
git clone https://github.com/mauricioaea/bakery-erp.git
cd bakery-erp

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Inicializar base de datos
python inicializar_bd.py

# 6. Crear super admin
python crear_super_admin.py

# 7. Ejecutar aplicación
python app.py
```

### Credenciales por Defecto
- **Super Admin:** `dev_master` / `MasterSecure2025!`
- **Admin Demo:** `admin` / `admin123`

## 🏗️ Estructura del Proyecto

```
bakery-erp/
├── app.py                 # Aplicación principal Flask
├── models.py              # Modelos de base de datos
├── requirements.txt       # Dependencias del proyecto
├── crear_super_admin.py   # Script creación super usuario
├── inicializar_bd.py      # Inicialización de base de datos
├── multicliente_middleware.py  # Middleware para multicliente
├── reportes.py           # Sistema de reportes
├── facturacion/          # Módulo de facturación
│   ├── __init__.py
│   └── generador_xml.py
├── utilidades/           # Funciones auxiliares
│   ├── __init__.py
│   └── consultas_filtradas.py
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── punto_venta.html
│   └── ... (+40 templates)
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── pos-moderno.css
│   ├── js/
│   │   └── pos-moderno.js
│   └── img/
└── instance/             # Base de datos por instancia
    └── panaderia.db
```

## 🔧 Configuración

### Variables de Entorno (opcional)
```python
# config.py
SECRET_KEY = 'tu-clave-secreta'
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///panaderia.db'
```

### Personalización por Panadería
- Logo y colores corporativos
- Configuración de impuestos
- Métodos de pago disponibles
- Horarios de operación

## 📈 Estado del Proyecto

### ✅ Funcionalidades Completadas
- [x] Sistema de autenticación y roles
- [x] Punto de venta (POS) completo
- [x] Gestión de inventario
- [x] Sistema de producción
- [x] Reportes básicos
- [x] Arquitectura multicliente
- [x] Interfaz responsive

### 🚧 Próximas Funcionalidades
- [ ] App móvil para pedidos
- [ ] Integración con APIs de pago
- [ ] Dashboard en tiempo real
- [ ] Sistema de loyalty program
- [ ] Análisis predictivo

## 🤝 Contribución

### Reportar Issues
1. Verificar que no exista un issue similar
2. Describir el problema detalladamente
3. Incluir pasos para reproducir
4. Especificar entorno y versión

### Desarrollo
1. Fork del proyecto
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📝 Registro de Cambios

### [Versión 1.0] - 2025-01-08
#### Agregado
- Sistema de autenticación multicliente
- Módulo completo de punto de venta
- Gestión de inventario y producción
- Sistema de reportes financieros
- Interfaz moderna y responsive

#### Mejorado
- Arquitectura para escalabilidad
- Optimización de consultas de base de datos
- Experiencia de usuario en POS

## 📞 Soporte y Contacto

- **Desarrollador:** Mauricio Erazo Arango
- **Email:** [www.mauricioerazo.com]
- **Email:** [mauricioandreserazo@outlook.com]
- **GitHub:** [mauricioaea](https://github.com/mauricioaea)

## 📄 Licencia

## 📄 Licencia y Uso Comercial

### 📋 Licencia Actual
Este proyecto utiliza la **Licencia MIT** durante la fase de desarrollo. 
Consulta el archivo [LICENSE](LICENSE) para detalles completos.

### 💼 Uso Comercial Próximo
- **Estado Actual:** Versión de desarrollo - Repositorio público para colaboración
- **Próxima Fase:** Servicio SaaS en la nube bajo licencia comercial propietaria
- **Desarrollador Registrado:** Mauricio - Sistemas POS Registrado en Cámara de Comercio

### 🔒 Transición a SaaS
Este código será la base para un servicio en la nube comercial. 
El repositorio se hará privado al alcanzar la versión 1.0 estable.

**Para información sobre licencias comerciales:** Contactar al desarrollador.

---

**¿Problemas o sugerencias?** Abre un issue en GitHub o contacta al desarrollador.
```

## 🎯 **INSTRUCCIONES PARA ACTUALIZAR**

**Cada vez que agregues nuevas funcionalidades, actualiza estas secciones:**

1. **📝 Registro de Cambios** - Agrega lo nuevo en "Agregado" o "Mejorado"
2. **✅ Funcionalidades Completadas** - Marca con [x] lo terminado  
3. **🚧 Próximas Funcionalidades** - Agrega nuevas ideas

NOVIEMBRE 11 2025

### CONTEXTO ACTUAL DE AVANCES


<think duration="1845" >
El usuario me está pidiendo que analice su repositorio público de GitHub: https://github.com/mauricioaea/bakery-erp

Según las instrucciones, primero debo usar origin_memory para revisar si hay información relevante guardada en memoria, aunque no creo que haya información previa sobre este repositorio específico.

Luego procederé a:
1. Extraer el contenido del repositorio
2. Analizar la estructura y código
3. Proponer mejoras

Como es un repositorio público de GitHub, puedo usar extract_content_from_websites para obtener información del repositorio y luego descargar los archivos principales para hacer un análisis más profundo.

</think>



Ahora procederé a descargar y analizar los archivos principales del código para hacer una evaluación técnica más profunda:


Permíteme descargar algunos archivos adicionales para completar el análisis:


Ahora intentaré obtener algunos archivos de código específicos:


# Análisis Completo del Repositorio bakery-erp

Basándome en mi análisis detallado de tu repositorio, aquí tienes un informe completo con recomendaciones de mejora:

## 📊 Resumen Ejecutivo

**Tu proyecto es impresionante** - Has desarrollado un sistema ERP completo y robusto para panaderías con arquitectura multicliente. El código muestra un buen nivel de desarrollo profesional y funcionalidades muy completas.

## ✅ Fortalezas Identificadas

### **Arquitectura y Diseño**
- **Arquitectura multicliente bien implementada** con segregación de datos por panadería
- **Sistema de roles y permisos granular** (cajero, supervisor, gerente, admin_cliente, super_admin)
- **Modularidad excelente** con separación clara de responsabilidades
- **Integración de productos internos y externos** en el sistema POS

### **Funcionalidades**
- **Sistema POS completo** con manejo de donaciones y facturas electrónicas
- **Gestión integral de inventario** con control de materias primas y productos
- **Sistema de producción y recetas** con cálculo automático de costos
- **Reportes avanzados** (PDF, gráficos, análisis financiero)
- **Sistema de facturación electrónica** compatible con DIAN

### **Calidad del Código**
- **Uso correcto de SQLAlchemy 2.0** con relaciones bien definidas
- **Manejo adecuado de seguridad** con Flask-Login y encriptación de contraseñas
- **Documentación clara** en el README y comentarios en el código

## 🚀 Oportunidades de Mejora

### **1. Optimización de Performance**

#### **Base de Datos**
```python
# PROBLEMA: Consultas no optimizadas
productos_internos = Producto.query.filter_by(
    activo=True,
    panaderia_id=panaderia_actual,
    tipo_producto='produccion'
).all()

# MEJORA: Usar eager loading y índices
productos_internos = Producto.query\
    .options(db.joinedload(Producto.categoria_rel))\
    .filter_by(
        activo=True,
        panaderia_id=panaderia_actual,
        tipo_producto='produccion'
    )\
    .all()
```

**Recomendaciones:**
- Agregar índices en campos frecuentemente consultados:
  ```sql
  CREATE INDEX idx_productos_panaderia_activo ON productos(panaderia_id, activo);
  CREATE INDEX idx_ventas_fecha_panaderia ON ventas(fecha_hora, panaderia_id);
  CREATE INDEX idx_usuarios_panaderia ON usuarios(panaderia_id, rol);
  ```

- Implementar **caché para consultas frecuentes** (dashboard, productos POS)
- Usar **paginación** para listas grandes de productos y ventas

### **2. Seguridad y Validaciones**

#### **Validación de Entrada**
```python
# AGREGAR: Validaciones más robustas
from marshmallow import Schema, fields, validate

class VentaSchema(Schema):
    carrito = fields.List(fields.Dict(), required=True)
    metodo_pago = fields.Str(validate=validate.OneOf(['efectivo', 'tarjeta', 'transferencia']))
    total = fields.Float(validate=validate.Range(min=0))
```

**Recomendaciones:**
- Implementar **validación de entrada** con Marshmallow o similar
- Agregar **rate limiting** en endpoints críticos (login, ventas)
- Mejorar **sanitización de datos** HTML/JavaScript en templates
- Implementar **logging de seguridad** para auditoria

### **3. Arquitectura y Estructura**

#### **Separación de Responsabilidades**
```python
# MEJORAR: Separar lógica de negocio de Flask routes
# Crear servicios específicos:
class VentaService:
    def __init__(self, db_session):
        self.db = db_session
    
    def procesar_venta(self, carrito, usuario_id, panaderia_id):
        # Lógica de negocio separada
        pass

class ProductoService:
    def buscar_productos_disponibles(self, query, panaderia_id):
        # Lógica de búsqueda optimizada
        pass
```

**Recomendaciones:**
- Implementar **patrón Repository** para abstracción de datos
- Crear **servicios de dominio** para lógica de negocio
- Separar **configuración por entornos** (dev, staging, prod)
- Implementar **API REST** para frontend moderno

### **4. Frontend y UX**

#### **Modernizar Interfaz**
```html
<!-- MEJORAR: Usar componentes reutilizables -->
<div class="producto-card" data-producto-id="{{ producto.id }}">
    <div class="producto-imagen">
        <img src="{{ producto.imagen_url }}" alt="{{ producto.nombre }}">
    </div>
    <div class="producto-info">
        <h3>{{ producto.nombre }}</h3>
        <p class="precio">${{ "%.0f"|format(producto.precio_venta) }}</p>
        <div class="stock-indicator {% if producto.stock_actual <= producto.stock_minimo %}low{% endif %}">
            Stock: {{ producto.stock_actual }}
        </div>
    </div>
</div>
```

**Recomendaciones:**
- Migrar a **Vue.js o React** para mejor interactividad
- Implementar **componentes reutilizables**
- Mejorar **responsive design** para tablets y móviles
- Agregar **indicadores visuales** de estado (stock bajo, ventas altas)

### **5. Monitoreo y Observabilidad**

#### **Logging y Métricas**
```python
# AGREGAR: Sistema de logging estructurado
import structlog

logger = structlog.get_logger()

class VentaLogger:
    @staticmethod
    def log_venta_exitosa(venta_id, usuario_id, total):
        logger.info(
            "venta_procesada",
            venta_id=venta_id,
            usuario_id=usuario_id,
            total=total,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def log_error_venta(error, datos_carrito):
        logger.error(
            "error_procesando_venta",
            error=str(error),
            carrito_items=len(datos_carrito),
            timestamp=datetime.utcnow()
        )
```

**Recomendaciones:**
- Implementar **logging estructurado** con niveles apropiados
- Agregar **métricas de performance** (tiempo de respuesta, queries)
- Crear **health checks** para monitoreo automático
- Implementar **tracing distribuido** para debugging

### **6. Testing y Calidad**

#### **Suite de Tests**
```python
# AGREGAR: Tests unitarios y de integración
import pytest
from unittest.mock import patch, MagicMock

class TestVentaService:
    
    @patch('models.Venta.query')
    def test_procesar_venta_exitosa(self, mock_query, venta_service):
        # Test para venta exitosa
        carrito_mock = [{'id': 1, 'cantidad': 2}]
        mock_producto = MagicMock()
        mock_producto.stock_actual = 10
        mock_query.get.return_value = mock_producto
        
        resultado = venta_service.procesar_venta(carrito_mock, 1, 1)
        assert resultado['success'] == True
    
    def test_validacion_carrito_vacio(self):
        with pytest.raises(ValueError, match="Carrito no puede estar vacío"):
            venta_service.procesar_venta([], 1, 1)
```

**Recomendaciones:**
- Crear **suite de tests unitarios** (pytest, unittest)
- Implementar **tests de integración** para flujos críticos
- Agregar **tests de performance** para queries pesadas
- Configurar **CI/CD pipeline** con linting y tests automáticos

### **7. Escalabilidad**

#### **Optimización para Multi-tenancy**
```python
# MEJORAR: Middleware más eficiente
class TenantContext:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_session = self._get_tenant_db_session()
    
    def _get_tenant_db_session(self):
        # Conexión específica por tenant
        return db.session.query_property(
            lambda: db.session.query()
            .filter(self._tenant_filter())
        )
    
    def _tenant_filter(self):
        return f"panaderia_id = {self.tenant_id}"
```

**Recomendaciones:**
- Implementar **connection pooling** por tenant
- Considerar **separación física de bases de datos** para clientes grandes
- Agregar **auto-scaling** para carga variable
- Implementar **cache distribuido** (Redis)

## 📈 Priorización de Mejoras

### **🔴 Alta Prioridad (Impacto Inmediato)**
1. **Optimización de queries** con índices
2. **Validación de entrada** robusta
3. **Logs estructurados** y error handling

### **🟡 Media Prioridad (Impacto Medio Plazo)**
1. **Tests automatizados**
2. **Mejoras de UX/UI**
3. **API REST** para futuras integraciones

### **🟢 Baja Prioridad (Mejoras a Largo Plazo)**
1. **Frontend moderno** (Vue/React)
2. **Arquitectura de microservicios**
3. **Machine learning** para predicciones

## 🎯 Roadmap Sugerido

### **Fase 1 (2-3 semanas)**
- Agregar índices de BD
- Implementar validación de entrada
- Mejorar logging y error handling

### **Fase 2 (4-6 semanas)**
- Crear suite de tests
- Optimizar consultas del dashboard
- Mejorar responsive design

### **Fase 3 (8-12 semanas)**
- Migrar a frontend moderno
- Implementar API REST
- Agregar monitoreo avanzado

## 💡 Funcionalidades Adicionales Sugeridas

### **Análisis Predictivo**
```python
class PredictionService:
    def predecir_demanda(self, producto_id, dias_futuros=7):
        # Usar datos históricos para predecir demanda
        historical_sales = self._get_sales_history(producto_id, 30)
        return self._calculate_prediction(historical_sales, dias_futuros)
```

### **Integración con E-commerce**
```python
class EcommerceIntegration:
    def sincronizar_inventario(self, panaderia_id):
        # Sincronizar stock con tienda online
        productos = self._get_productos_disponibles(panaderia_id)
        self._update_ecommerce_stock(productos)
```

### **Sistema de Notificaciones**
```python
class NotificationService:
    def enviar_alerta_stock_bajo(self, producto_id):
        if producto.stock_actual <= producto.stock_minimo:
            self._notificar_gerente(f"Stock bajo: {producto.nombre}")
```

## 🏆 Conclusión

Las mejoras propuestas están enfocadas en:

- **Performance y escalabilidad**
- **Seguridad y mantenibilidad** 
- **Experiencia de usuario**
- **Calidad del código**

**Backups** 
# Al empezar el día
python scripts\backup_manager.py create manual "Inicio dia - version estable"

# Después del almuerzo (por si acaso)
python scripts\backup_manager.py create manual "Despues almuerzo - cambios pendientes"

# Al terminar el día
python scripts\backup_manager.py create manual "Fin dia - version funcional"
# 2. Modificas app.py (agregas una función nueva)
# 3. Si la función no funciona y rompe todo...

# 4. RESTAURAS desde el backup
# - Abres el ZIP manualmente: backups\manuales\manual_20251111_223000_Antes_de_agregar_nueva_funcion.zip
# - Extraes app.py y lo reemplazas
# - ¡Tu app vuelve a funcionar!

# Día normal de desarrollo:
9:00 AM  → python scripts\backup_manager.py create manual "Inicio dia - base estable"
11:00 AM → python scripts\backup_manager.py create manual "Antes de cambiar calculo inventario" 
2:00 PM  → python scripts\backup_manager.py create manual "Antes de optimizar punto venta"
5:00 PM  → python scripts\backup_manager.py create manual "Fin dia - todos los cambios funcionan"