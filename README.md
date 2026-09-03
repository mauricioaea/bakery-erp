

# 🥖 PanaderíaPro - ERP Multi-Tenant para Panaderías

> **Sistema de gestión integral para panaderías con arquitectura SaaS multi-tenant**

---

## 👋 ¡Bienvenido/a!

¡Hola! Soy **Mauricio Erazo Arango**, desarrollador de sistemas POS registrado en Cámara de Comercio. Este proyecto representa meses de dedicación creando una solución completa para panaderías.

### 💝 Mi Motivación
Desarrollé este sistema para ayudar a pequeños y medianos empresarios de panaderías a digitalizar sus operaciones y crecer sus negocios de manera profesional.

### 🤝 Para Visitantes
- **¿Eres desarrollador?** ¡Tu feedback es invaluable!
- **¿Tienes una panadería?** Próximamente disponible como servicio en la nube
- **¿Te gusta el proyecto?** ⭐ Dale una estrella en GitHub
- **¿Tienes ideas?** ¡Abre un issue y hablemos!

---

## 📋 Tabla de Contenidos

- [Estado Actual](#-estado-actual)
- [Características Principales](#-características-principales)
- [Arquitectura Multi-Tenant](#-arquitectura-multi-tenant)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Módulos del Sistema](#-módulos-del-sistema)
- [Sistema de Licencias](#-sistema-de-licencias)
- [Roles y Permisos](#-roles-y-permisos)
- [Plan Maestro](#-plan-maestro)
- [Base de Datos](#-base-de-datos)
- [Comandos Útiles](#-comandos-útiles)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribución](#-contribución)
- [Registro de Cambios](#-registro-de-cambios)
- [Contacto y Soporte](#-contacto-y-soporte)
- [Registro de Cambios](#-registro-de-cambios)

---

## 🚀 Estado Actual

| Aspecto | Estado |
|---------|--------|
| **Versión** | v1.0.0 |
| **Estado** | ✅ **100% Funcional** |
| **Arquitectura** | Multi-tenant con PostgreSQL |
| **Desarrollo** | Activo - Mejoras continuas |
| **Próximo hito** | Migración a la nube (SaaS) |

### ✅ Funcionalidades Completadas
- [x] Sistema de autenticación y roles multi-tenant
- [x] Punto de venta (POS) completo con búsqueda rápida
- [x] Gestión de inventario (materias primas, productos, externos)
- [x] Sistema de producción con recetas
- [x] Reportes profesionales (PDF, gráficos, IA)
- [x] Gestión financiera con cierre de caja
- [x] Sistema de licencias (Básica / Premium)
- [x] Activos fijos
- [x] Migración completa a PostgreSQL
- [x] Dashboard por tenant con métricas clave

### 🚧 Próximas Funcionalidades
- [ ] Pasarela de pagos (Stripe/MercadoPago)
- [ ] Portal de clientes (autogestión)
- [ ] App móvil para pedidos
- [ ] Sistema de loyalty program

---

## ✨ Características Principales

### 🔐 Autenticación y Roles
- **Super Admin:** Acceso completo al sistema multicliente
- **Administrador:** Gestión de una panadería específica
- **Supervisor:** Operaciones de producción y reportes
- **Cajero:** Punto de venta y cierre de caja
- **Login seguro** con gestión de sesiones y hasheo pbkdf2:sha256

### 🏪 Punto de Venta (POS)
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
- Productos externos con fecha de vencimiento
- Productos próximos a vencer (alertas en dashboard)

### 🍞 Producción y Recetas
- Gestión de recetas con costos
- Control de producción diaria
- Cálculo automático de rendimientos
- Relación productos-materias primas

### 📊 Reportes y Analytics
- Estado de Resultados (Básica)
- Flujo de Caja (Premium)
- Libro Diario (Premium)
- Conciliación Bancaria (Premium)
- Análisis de Gastos (Premium)
- Tendencia de Ventas (Premium)
- **IA Predictivo** (Premium)
- Análisis de Inventarios (Premium)
- Tesorería Unificado (Premium)

### 🏢 Arquitectura Multi-Tenant
- Base de datos segregada por panadería (schemas PostgreSQL)
- Configuración independiente por cliente
- Super admin con visión global
- Aislamiento completo de datos entre tenants

---

## 🏗️ Arquitectura Multi-Tenant

### Estrategia: Schemas separados por tenant en PostgreSQL

panaderia_master (base de datos principal)
├── public (tablas maestras: tenants, usuarios maestros)
├── tenant_1 (Panadería Principal)
│ ├── usuarios
│ ├── productos
│ ├── categorias
│ ├── ventas
│ └── configuracion_panaderia
├── tenant_2 (Panadería Test)
│ └── (misma estructura)
└── tenant_X (cada nuevo tenant)
└── (misma estructura)



### 🔒 Seguridad Multi-Tenant
- Todas las consultas tienen filtro `panaderia_id`
- Decoradores: `@tenant_required`, `@login_required`
- Aislamiento completo entre tenants
- Validación automática de acceso

---

## 🛠️ Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.10+ | Lenguaje principal |
| **Flask** | 3.1.2 | Framework web |
| **SQLAlchemy** | 2.0 | ORM para base de datos |
| **PostgreSQL** | 17.10 | Base de datos principal (puerto 5433) |
| **Flask-Login** | - | Gestión de autenticación |
| **Werkzeug** | - | Seguridad de contraseñas (pbkdf2:sha256) |
| **ReportLab** | - | Generación de reportes PDF |

### Frontend
| Tecnología | Uso |
|------------|-----|
| **HTML5/CSS3** | Estructura y estilos |
| **JavaScript** | Interactividad |
| **Bootstrap 5.1.3** | Framework CSS |
| **Chart.js** | Gráficos y reportes |

### Base de Datos
- **PostgreSQL 17.10** (producción)
- **SQLite** (desarrollo - legacy)

---

## 📥 Instalación y Configuración

### Prerrequisitos
- Python 3.10 o superior
- PostgreSQL 17.10 (puerto 5433)
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

# 5. Configurar PostgreSQL
# Conectar a PostgreSQL:
psql -U postgres -p 5433 -h localhost

# Crear base de datos maestra:
CREATE DATABASE panaderia_master;
\q

# 6. Configurar variables de entorno (crear .env)
DATABASE_URL=postgresql://postgres:PanaderiaPro2026!@localhost:5433/panaderia_master
FLASK_ENV=development
SECRET_KEY=panaderiapro2026

# 7. Inicializar base de datos
python inicializar_bd.py

# 8. Crear super admin
python configurar_super_admin.py

# 9. Ejecutar aplicación
python app.py


Credenciales por Defecto
Usuario	Contraseña	Rol
dev_master	admin123	Super Admin
admin_1	generada automáticamente	Admin Cliente (Panadería Principal)


📂 Estructura del Proyecto
text
panaderia_profesional/
├── app.py (384 KB)              # Aplicación principal
├── models.py (115 KB)           # Modelos SQLAlchemy
├── reportes.py (147 KB)         # Generación de reportes PDF
├── middleware_saas.py           # Middleware multi-tenant
├── tenant_decorators.py         # Decoradores multi-tenant
├── tenant_context.py            # Contexto multi-tenant
├── requirements.txt             # Dependencias del proyecto
├── .env                         # Variables de entorno
├── databases_tenants/           # BDs SQLite (legacy)
├── templates/                   # Templates HTML (Jinja2)
│   ├── base.html
│   ├── punto_venta.html
│   └── ... (+40 templates)
├── static/                      # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
└── scripts/                     # Scripts de utilidad
    ├── backup_manager.py
    ├── limpiar_tenants.py
    └── ...


📋 Módulos del Sistema
🔹 FASE 1: CONFIGURACIÓN INICIAL
Orden	Módulo	Propósito
1	Gestión de Proveedores	Registrar proveedores (base de suministro)
2	Gestión de Materias Primas	Registrar ingredientes, costos, stock inicial
3	Recetas y Fórmulas	Crear recetas, calcular costos y rentabilidad
🔹 FASE 2: OPERACIÓN DIARIA
Orden	Módulo	Propósito
4	Producción Diaria	Ordenar producciones, gestionar stock en vitrina
5	Productos Externos	Gestionar productos no producidos (bebidas, snacks)
6	Punto de Venta	Realizar ventas (completado)
🔹 FASE 3: CONTROL Y ADMINISTRACIÓN
Orden	Módulo	Propósito
7	Gestión Financiera	Control diario, cierre de caja, depósitos bancarios
8	Reportes Profesionales	Análisis de rentabilidad, gastos, tendencias, IA
9	Activos Fijos	Gestión de equipos, mobiliario, inversiones
10	Gestión de Usuarios	Administración de empleados y permisos
🔹 FASE 4: VISIÓN GLOBAL
Orden	Módulo	Propósito
11	Dashboard	Panel principal con métricas clave y acceso rápido
💰 Sistema de Licencias
Planes de Suscripción
Tipo	Usuarios	Módulos Premium	Precio
Básica	1 (admin)	❌ Bloqueados	$50,000 COP/mes
Premium	3 (admin, super, cajero)	✅ Acceso completo	$150,000 COP/mes
Módulos Premium (Bloqueados para Básica)
❌ Activos Fijos

❌ Reportes Gerenciales (Análisis Gastos, Tendencia Ventas, IA Predictivo, Análisis Inventarios)

❌ Gestión de Usuarios

Comparativa de Módulos
Módulo	Básica	Premium
Punto de Venta	✅ (sin Reporte IA)	✅ (con Reporte IA)
Producción	✅	✅
Productos Externos	✅	✅
Recetas	✅	✅
Materias Primas	✅	✅
Proveedores	✅	✅
Gestión Financiera	✅	✅
Reporte Cierre de Caja	✅	✅
Estado de Resultados	✅	✅
Reportes Gerenciales	❌	✅
Activos Fijos	❌	✅
Gestión de Usuarios	❌	✅


👤 Roles y Permisos
Matriz de Permisos
Rol	Descripción	Acceso
super_admin	Dueño del sistema	Gestiona TODOS los tenants, licencias y configuración global
admin_cliente	Administrador de panadería	Acceso TOTAL a su tenant
supervisor	Supervisor	Producción, recetas, materias primas, proveedores, reportes
cajero	Cajero	Solo punto de venta y cierre de caja
Decoradores de Seguridad
@login_required - Autenticación requerida

@tenant_required - Filtro multi-tenant

@modulo_requerido('modulo') - Acceso a módulo específico

@permisos_requeridos('modulo', 'accion') - Permisos específicos

@licencia_premium_requerida() - Verificación de licencia Premium


🗺️ Plan Maestro

✅ FASE 1: DEPURACIÓN (COMPLETADA)
☑ Backup completo creado
☑ Verificación de consultas SQL (todas con filtro panaderia_id)
☑ Corrección de advertencias SQLAlchemy
☑ Eliminación de código duplicado
☑ Sincronización de IDs entre bases de datos
☑ Migración de SQLite a PostgreSQL
☑ Corrección de reseteo de contraseñas (pbkdf2:sha256)

✅ FASE 2: FUNCIONALIDADES (COMPLETADA)
☑ Dashboard por tenant
☑ Reportes por tenant
☑ Módulo de inventario
☑ Módulo de compras (Productos Externos)
☑ Módulo de clientes
☑ Gestión de usuarios por tenant
☑ Sistema de licencias (Básica/Premium)

🚀 FASE 3: PREPARACIÓN PARA LA NUBE (EN PROGRESO)
#	Tarea	Prioridad	Estado
1	Migrar a PostgreSQL	🔴 ALTA	✅ COMPLETADO
2	Configurar subdominios dinámicos	🔴 ALTA	⏳ PENDIENTE
3	Dockerizar la aplicación	🟡 MEDIA	⏳ PENDIENTE
4	Backups automáticos por tenant	🟡 MEDIA	⏳ PENDIENTE
5	Migrar a producción (AWS/DigitalOcean)	🔴 ALTA	⏳ PENDIENTE

🚀 FASE 4: SEGURIDAD Y ESCALABILIDAD (PENDIENTE)
#	Tarea	Prioridad	Estado
1	HTTPS/SSL para todos los subdominios	🔴 ALTA	⏳ PENDIENTE
2	Rate limiting	🟡 MEDIA	⏳ PENDIENTE
3	Logging y auditoría	🟡 MEDIA	⏳ PENDIENTE
4	Monitoreo de caídas/errores	🟢 BAJA	⏳ PENDIENTE
5	Caché (Redis)	🟢 BAJA	⏳ PENDIENTE

🚀 FASE 5: MONETIZACIÓN (PENDIENTE)
#	Tarea	Prioridad	Estado
1	Planes de suscripción	🔴 ALTA	✅ COMPLETADO
2	Pasarela de pagos (Stripe/MercadoPago)	🔴 ALTA	⏳ PENDIENTE
3	Portal de clientes (autogestión)	🟡 MEDIA	⏳ PENDIENTE
4	Facturación automática	🟡 MEDIA	⏳ PENDIENTE


🗄️ Base de Datos
PostgreSQL - Credenciales de Conexión
Parámetro	Valor
Host	localhost
Puerto	5433
Usuario	postgres
Contraseña	PanaderiaPro2026!
Base de datos	panaderia_master
URL de Conexión
text
postgresql://postgres:PanaderiaPro2026!@localhost:5433/panaderia_master
Conectar a PostgreSQL
bash
psql -U postgres -p 5433 -h localhost -d panaderia_master
Estructura de Base de Datos
Tablas Maestras (public)
tenants - Información de cada panadería

usuarios - Usuarios del sistema (dev_master y admins)

configuracion_panaderia - Configuración global

Tablas por Tenant (tenant_X)
usuarios - Usuarios del tenant (admin, super, cajero)

productos - Productos internos

categorias - Categorías de productos

ventas - Ventas realizadas

detalles_venta - Detalles de cada venta

clientes - Clientes finales

proveedores - Proveedores

materias_primas - Materias primas

recetas - Recetas y fórmulas

configuracion_panaderia - Configuración del tenant

activos_fijos - Activos fijos

produccion_diaria - Producción diaria

cierre_caja - Cierres de caja

productos_externos - Productos externos


🔧 Comandos Útiles

Iniciar Aplicación
bash
python app.py
Acceder a la Aplicación
text
http://localhost:5000
Conectar a PostgreSQL
bash
psql -U postgres -p 5433 -h localhost -d panaderia_master
Ver Tenants Activos
sql
SELECT id, nombre, fecha_registro FROM public.tenants;
Ver Usuarios del Sistema
sql
SELECT id, username, rol, panaderia_id FROM public.usuarios;
Eliminar un Tenant (Ejemplo: tenant_2)
sql
-- 1. Eliminar el schema
DROP SCHEMA IF EXISTS tenant_2 CASCADE;

-- 2. Eliminar el tenant
DELETE FROM public.tenants WHERE id = 2;

-- 3. Eliminar configuración
DELETE FROM public.configuracion_panaderia WHERE tenant_id = 2;

-- 4. Eliminar usuario admin
DELETE FROM public.usuarios WHERE username = 'admin_2';

-- 5. Reparar secuencias
SELECT setval('tenants_id_seq', (SELECT COALESCE(MAX(id), 1) FROM public.tenants));
SELECT setval('configuracion_panaderia_id_seq', (SELECT COALESCE(MAX(id), 1) FROM public.configuracion_panaderia));
Backup de Base de Datos
bash
# Backup completo
pg_dump -U postgres -p 5433 -h localhost panaderia_master > backup_$(date +%Y%m%d).sql

# Backup de un tenant específico
pg_dump -U postgres -p 5433 -h localhost -n tenant_1 panaderia_master > tenant_1_backup.sql
Restaurar Backup
bash
psql -U postgres -p 5433 -h localhost -d panaderia_master < backup.sql
🐛 Solución de Problemas
Error: "No se puede conectar a PostgreSQL"
bash
# Verificar que PostgreSQL está corriendo
# Windows:
net start PostgreSQL

# Linux/Mac:
sudo systemctl start postgresql

# Verificar puerto
netstat -an | findstr 5433
Error: "Role 'postgres' does not exist"
bash
# Crear usuario postgres
createuser -U postgres -s postgres
Error: "Database 'panaderia_master' does not exist"
bash
# Crear base de datos
createdb -U postgres -p 5433 -h localhost panaderia_master
Error: "FATAL: password authentication failed"
bash
# Verificar contraseña en .env
# La contraseña correcta es: PanaderiaPro2026!

# la contraseña 

# O resetear contraseña de postgres
# En pg_hba.conf cambiar a trust, luego:
psql -U postgres -p 5433 -h localhost
ALTER USER postgres WITH PASSWORD 'PanaderiaPro2026!';
Error: "No module named 'flask'"
bash
# Verificar que el entorno virtual está activado
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
🤝 Contribución
Reportar Issues
Verificar que no exista un issue similar

Describir el problema detalladamente

Incluir pasos para reproducir

Especificar entorno y versión


Desarrollo
bash
1. Fork del proyecto
2. Crear rama feature: git checkout -b feature/nueva-funcionalidad
3. Commit cambios: git commit -m 'Agrega nueva funcionalidad'
4. Push: git push origin feature/nueva-funcionalidad
5. Crear Pull Request
📝 Registro de Cambios
[Versión 1.0.0] - 2026-08-28
Agregado
Sistema de reseteo de contraseñas con pbkdf2:sha256

Generador de contraseñas seguro (solo caracteres - como especial)

Verificación POST-COMMIT para garantizar persistencia

Módulo de productos externos con fecha de vencimiento

Alertas de stock bajo en dashboard

Sistema de licencias (Básica/Premium)

Inteligencia Artificial para reportes predictivos

Migración completa a PostgreSQL

Mejorado
Arquitectura multi-tenant con schemas PostgreSQL

Seguridad de contraseñas con pbkdf2:sha256

Rendimiento de consultas con índices

Experiencia de usuario en POS

Validación de entrada robusta

Corregido
Error crítico en reseteo de contraseñas

Filtros multi-tenant en todas las consultas

Advertencias de SQLAlchemy (métodos legacy)

Sincronización de IDs entre bases de datos

Caracteres problemáticos en generación de contraseñas

### [Versión 1.0.1] - 2026-09-02

#### 🎨 Rediseño Profesional del Frontend

**Login Page:**
- ✅ Rediseño completo con identidad de marca PanaderíaPro
- ✅ Logo "PanaderíaPro" con línea decorativa en dorado
- ✅ Paleta de colores: Negro elegante (#0a0e17) + Dorado (#f5b81b)
- ✅ Nuevo eslogan: "Controla tu panadería desde el horno hasta la venta"
- ✅ Microtexto con valor diferencial: IA predictiva • Utilidad real • Stock automático • Alertas inteligentes
- ✅ Favicon personalizado con "P" estilizada

**Dashboard:**
- ✅ Rediseño estilo Apple con fondo claro y tarjetas blancas
- ✅ Header con logo PanaderíaPro (blanco + dorado)
- ✅ Colores distintivos por módulo (10 módulos con identidad visual única)
- ✅ Badges "NUEVO" para funcionalidades recientes
- ✅ Sección "Aliados Comerciales" para monetización con proveedores
- ✅ Estilo consistente con la identidad de marca

**Nuevas Páginas:**
- ✅ `recuperar_password.html` - Página de recuperación de contraseña con información de contacto
- ✅ `solicitar_demo.html` - Página para solicitar demo con WhatsApp y Email

**Mejoras Técnicas:**
- ✅ Favicon funcionando en todos los templates
- ✅ Estilos CSS optimizados y consistentes
- ✅ Mejora en la experiencia de usuario
- ✅ Preparación para futura migración a logos reales de proveedores

**Monetización:**
- ✅ Sección "Aliados Comerciales" no invasiva para publicidad
- ✅ Diseño profesional con iniciales en círculos dorados
- ✅ Preparado para escalar a logos reales y enlaces web


📞 Contacto y Soporte

Desarrollador: Mauricio Erazo Arango

Email: mauricioandreserazo@outlook.com

GitHub: mauricioaea
Telefono: +57 3102482881

Sitio Web: www.mauricioerazo.com

📄 Licencia
📋 Licencia Actual
Este proyecto utiliza la Licencia MIT durante la fase de desarrollo.

💼 Uso Comercial
Estado Actual: Versión de desarrollo - Repositorio público para colaboración

Próxima Fase: Servicio SaaS en la nube bajo licencia comercial propietaria

Desarrollador Registrado: Mauricio Erazo - Sistemas POS Registrado en Cámara de Comercio -> Pasto-Colombia

🔒 Transición a SaaS
Este código será la base para un servicio en la nube comercial. El repositorio se hará privado al alcanzar la versión 1.0 estable.

Para información sobre licencias comerciales: Contactar al desarrollador.

🙏 Agradecimientos
A Dios por la sabiduria que me dio para este proyecto, mi familia Esposa e Matias y Mathin, y a los dueños de panaderías que inspiran este proyecto.

"Crear software que realmente ayude a los negocios es mi pasión" 🎯

¿Problemas o sugerencias? Abre un issue en GitHub o contacta al desarrollador.



