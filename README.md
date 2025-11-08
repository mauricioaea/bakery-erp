
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

**¿Quieres que personalicemos alguna sección específica o agreguemos algo más?** 🚀