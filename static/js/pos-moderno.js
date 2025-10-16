// =============================================
// POS MODERNO - JAVASCRIPT AVANZADO
// =============================================

// Variables globales
let carrito = [];
let todosProductos = [];
let categorias = [];
let productosFiltrados = [];
let categoriaActual = '';

// Iconos por categoría (Font Awesome)
const iconosCategorias = {
    'Panadería': 'fas fa-bread-slice',
    'Pastelería': 'fas fa-birthday-cake', 
    'Bebidas': 'fas fa-coffee',
    'Sandwiches': 'fas fa-hamburger',
    'Repostería': 'fas fa-cookie',
    'Especiales': 'fas fa-star',
    'Promociones': 'fas fa-tag',
    'General': 'fas fa-box'
};

// =============================================
// 1. INICIALIZACIÓN
// =============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando POS Moderno...');
    
    // Cargar carrito desde localStorage
    cargarCarritoPersistente();
    
    // Cargar productos y categorías
    cargarProductos();
    
    // Iniciar dashboard en tiempo real
    iniciarDashboardTiempoReal();
    
    // Configurar atajos de teclado
    configurarAtajosTeclado();
    
    // Configurar búsqueda en tiempo real
    configurarBusquedaTiempoReal();
    
    console.log('✅ POS Moderno inicializado');
});

// =============================================
// 2. CARRITO PERSISTENTE CON LOCALSTORAGE
// =============================================
function cargarCarritoPersistente() {
    try {
        const carritoGuardado = localStorage.getItem('carrito_pos_panaderia');
        if (carritoGuardado) {
            carrito = JSON.parse(carritoGuardado);
            console.log('🛒 Carrito cargado desde localStorage:', carrito.length, 'items');
            actualizarCarrito();
        }
    } catch (error) {
        console.error('❌ Error cargando carrito:', error);
        carrito = [];
    }
}

function guardarCarritoPersistente() {
    try {
        localStorage.setItem('carrito_pos_panaderia', JSON.stringify(carrito));
    } catch (error) {
        console.error('❌ Error guardando carrito:', error);
    }
}

// =============================================
// 3. CARGA DE PRODUCTOS Y CATEGORÍAS
// =============================================
async function cargarProductos() {
    try {
        console.log('📦 Cargando productos...');
        mostrarLoadingProductos();
        
        const response = await fetch('/buscar_producto?q=');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        todosProductos = await response.json();
        console.log(`✅ ${todosProductos.length} productos cargados`);
        
        // Procesar categorías
        procesarCategorias();
        
        // Mostrar productos
        mostrarProductosModernos(todosProductos);
        
        // Actualizar dashboard
        actualizarDashboard();
        
    } catch (error) {
        console.error('❌ Error cargando productos:', error);
        mostrarErrorProductos(error);
    }
}

function procesarCategorias() {
    // Extraer categorías únicas
    categorias = [...new Set(todosProductos.map(p => p.categoria).filter(Boolean))];
    
    // Agregar categoría "Todas"
    if (!categorias.includes('Todas')) {
        categorias.unshift('Todas');
    }
    
    // Actualizar selector de categorías
    actualizarSelectorCategorias();
    
    // Actualizar sidebar de categorías
    actualizarSidebarCategorias();
}

function actualizarSelectorCategorias() {
    const select = document.getElementById('categoriaFilter');
    select.innerHTML = '<option value="">Todas las categorías</option>';
    
    categorias.forEach(categoria => {
        if (categoria !== 'Todas') {
            select.innerHTML += `<option value="${categoria}">${categoria}</option>`;
        }
    });
}

function actualizarSidebarCategorias() {
    const listaCategorias = document.getElementById('listaCategorias');
    let html = '';
    
    // Agregar "Todas" primero
    html += `
        <a href="#" class="list-group-item list-group-item-action active" 
           data-categoria="Todas" onclick="filtrarPorCategoria('Todas')">
            <div class="categoria-icon">
                <i class="fas fa-th-large"></i>
            </div>
            <span>Todas las Categorías</span>
        </a>
    `;
    
    // Agregar demás categorías
    categorias.forEach(categoria => {
        if (categoria !== 'Todas') {
            const icono = iconosCategorias[categoria] || 'fas fa-box';
            html += `
                <a href="#" class="list-group-item list-group-item-action" 
                   data-categoria="${categoria}" onclick="filtrarPorCategoria('${categoria}')">
                    <div class="categoria-icon">
                        <i class="${icono}"></i>
                    </div>
                    <span>${categoria}</span>
                </a>
            `;
        }
    });
    
    listaCategorias.innerHTML = html;
}

// =============================================
// 4. MOSTRAR PRODUCTOS - DISEÑO MODERNO
// =============================================
function mostrarProductosModernos(productos) {
    const container = document.getElementById('productosContainer');
    
    if (productos.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No se encontraron productos</h5>
                <p class="text-muted">No hay productos que coincidan con tu búsqueda.</p>
                <button class="btn btn-primary mt-2" onclick="limpiarBusqueda()">
                    <i class="fas fa-undo me-1"></i>Mostrar todos
                </button>
            </div>
        `;
        return;
    }

    // Agrupar por categoría
    const productosPorCategoria = {};
    productos.forEach(producto => {
        const categoria = producto.categoria || 'General';
        if (!productosPorCategoria[categoria]) {
            productosPorCategoria[categoria] = [];
        }
        productosPorCategoria[categoria].push(producto);
    });

    let html = '';
    
    Object.keys(productosPorCategoria).forEach(categoria => {
        // Solo mostrar título de categoría si no estamos filtrando por una específica
        if (!categoriaActual || categoriaActual === 'Todas' || categoriaActual === categoria) {
            html += `
                <div class="categoria-section mb-4">
                    <h5 class="categoria-title mb-3">
                        <i class="${iconosCategorias[categoria] || 'fas fa-box'} me-2"></i>
                        ${categoria}
                    </h5>
                    <div class="row">
            `;
            
            productosPorCategoria[categoria].forEach(producto => {
                html += crearCardProductoModerno(producto);
            });
            
            html += '</div></div>';
        }
    });

    container.innerHTML = html;
    
    // Enfocar primer input después de cargar
    setTimeout(() => {
        const primerInput = document.querySelector('.cantidad-input');
        if (primerInput) primerInput.focus();
    }, 100);
}

function crearCardProductoModerno(producto) {
    const sinStock = producto.stock_actual <= 0;
    const claseStock = sinStock ? 'sin-stock' : '';
    
    // Determinar badge de stock
    let badgeStock = '';
    let badgeClass = 'bg-stock-ok';
    
    if (sinStock) {
        badgeStock = '<span class="stock-badge bg-stock-critico">SIN STOCK</span>';
    } else if (producto.stock_actual <= 5) {
        badgeStock = `<span class="stock-badge bg-stock-critico">${producto.stock_actual}</span>`;
    } else if (producto.stock_actual <= 10) {
        badgeStock = `<span class="stock-badge bg-stock-bajo">${producto.stock_actual}</span>`;
    } else {
        badgeStock = `<span class="stock-badge bg-stock-ok">${producto.stock_actual}</span>`;
    }
    
    // Icono del producto basado en categoría
    const iconoProducto = iconosCategorias[producto.categoria] || 'fas fa-box';
    
    return `
        <div class="col-xl-3 col-lg-4 col-md-6 mb-3">
            <div class="producto-card-moderno ${claseStock}" 
                 data-producto-id="${producto.id}">
                ${badgeStock}
                
                <div class="producto-imagen">
                    <i class="${iconoProducto}"></i>
                </div>
                
                <div class="producto-nombre">${producto.nombre}</div>
                <div class="producto-precio">$${producto.precio}</div>
                <small class="text-muted">${producto.tipo_producto || 'Producción'}</small>
                
                ${!sinStock ? `
                <div class="quantity-selector-moderno mt-2">
                    <div class="input-group input-group-sm">
                        <input type="number" 
                            id="cantidad-${producto.id}" 
                            class="form-control cantidad-input" 
                            value="1" 
                            min="1" 
                            max="${producto.stock_actual}"
                            onkeypress="manejarEnter(event, ${producto.id})"
                            placeholder="Cant.">
                        <button class="btn btn-success" 
                                onclick="agregarAlCarritoConCantidad(${producto.id})"
                                title="Agregar al carrito (Enter)">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// =============================================
// 5. FILTRADO Y BÚSQUEDA
// =============================================
function configurarBusquedaTiempoReal() {
    const searchInput = document.getElementById('searchInput');
    let timeoutId;

    searchInput.addEventListener('input', function() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            filtrarProductos();
        }, 300); // Debouncing de 300ms
    });
}

function filtrarProductos() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoriaSeleccionada = document.getElementById('categoriaFilter').value;
    
    productosFiltrados = todosProductos.filter(producto => {
        const coincideNombre = producto.nombre.toLowerCase().includes(searchTerm);
        const coincideCategoria = !categoriaSeleccionada || producto.categoria === categoriaSeleccionada;
        return coincideNombre && coincideCategoria;
    });
    
    mostrarProductosModernos(productosFiltrados);
}

function filtrarPorCategoria(categoria) {
    categoriaActual = categoria;
    
    // Actualizar active state en sidebar
    document.querySelectorAll('#listaCategorias .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-categoria="${categoria}"]`).classList.add('active');
    
    // Actualizar selector dropdown
    document.getElementById('categoriaFilter').value = categoria === 'Todas' ? '' : categoria;
    
    // Filtrar productos
    if (categoria === 'Todas') {
        mostrarProductosModernos(todosProductos);
    } else {
        const productosCategoria = todosProductos.filter(p => p.categoria === categoria);
        mostrarProductosModernos(productosCategoria);
    }
    
    // Scroll to top
    document.querySelector('.products-grid-container').scrollTop = 0;
}

function limpiarBusqueda() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoriaFilter').value = '';
    categoriaActual = '';
    filtrarPorCategoria('Todas');
}

// =============================================
// 6. FUNCIONALIDAD DEL CARRITO
// =============================================
function agregarAlCarritoConCantidad(productoId) {
    const cantidadInput = document.getElementById('cantidad-' + productoId);
    const cantidad = parseInt(cantidadInput.value);
    
    const producto = todosProductos.find(p => p.id === productoId);
    
    if (!producto) {
        mostrarNotificacion('❌ Producto no encontrado', 'error');
        return;
    }

    if (producto.stock_actual <= 0) {
        mostrarNotificacion('❌ No hay stock disponible', 'error');
        return;
    }

    if (isNaN(cantidad) || cantidad < 1) {
        mostrarNotificacion('❌ La cantidad debe ser al menos 1', 'error');
        cantidadInput.focus();
        cantidadInput.select();
        return;
    }

    if (cantidad > producto.stock_actual) {
        mostrarNotificacion(`❌ Stock insuficiente. Máximo: ${producto.stock_actual}`, 'error');
        cantidadInput.value = producto.stock_actual;
        cantidadInput.focus();
        cantidadInput.select();
        return;
    }

    // Buscar si ya está en el carrito
    const itemExistente = carrito.find(item => item.id === productoId);
    
    if (itemExistente) {
        const cantidadTotal = itemExistente.cantidad + cantidad;
        if (cantidadTotal > producto.stock_actual) {
            mostrarNotificacion(`❌ Stock insuficiente. Ya tienes ${itemExistente.cantidad} en el carrito`, 'error');
            return;
        }
        itemExistente.cantidad += cantidad;
    } else {
        carrito.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: cantidad,
            stock_maximo: producto.stock_actual
        });
    }

    actualizarCarrito();
    mostrarFeedbackAgregado(producto.nombre, cantidad);
    
    // Resetear a 1 después de agregar
    cantidadInput.value = 1;
    
    // Enfocar siguiente input automáticamente
    setTimeout(() => {
        const inputs = document.querySelectorAll('.cantidad-input');
        const currentIndex = Array.from(inputs).findIndex(input => 
            input.id === 'cantidad-' + productoId);
        const nextIndex = (currentIndex + 1) % inputs.length;
        if (inputs[nextIndex]) {
            inputs[nextIndex].focus();
            inputs[nextIndex].select();
        }
    }, 10);
}

function manejarEnter(event, productoId) {
    if (event.key === 'Enter') {
        event.preventDefault();
        agregarAlCarritoConCantidad(productoId);
    }
}

function actualizarCarrito() {
    const carritoItems = document.getElementById('carritoItems');
    const contadorCarrito = document.getElementById('contadorCarrito');
    const btnPagar = document.getElementById('btnPagar');
    
    // Guardar en localStorage
    guardarCarritoPersistente();
    
    if (carrito.length === 0) {
        carritoItems.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-cart-plus fa-2x mb-2"></i>
                <p>El carrito está vacío</p>
            </div>
        `;
        contadorCarrito.textContent = '0';
        btnPagar.disabled = true;
    } else {
        let html = '';
        let subtotal = 0;
        
        carrito.forEach((item, index) => {
            const totalItem = item.precio * item.cantidad;
            subtotal += totalItem;
            
            html += `
                <div class="carrito-item-moderno">
                    <div class="carrito-item-header">
                        <h6 class="carrito-item-nombre">${item.nombre}</h6>
                        <span class="carrito-item-precio">$${totalItem}</span>
                    </div>
                    <div class="carrito-item-controls">
                        <span class="carrito-item-cantidad">${item.cantidad} x $${item.precio}</span>
                        <div class="carrito-item-actions">
                            <button class="btn btn-outline-secondary btn-sm" 
                                    onclick="modificarCantidad(${index}, -1)"
                                    ${item.cantidad <= 1 ? 'disabled' : ''}>
                                <i class="fas fa-minus"></i>
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" 
                                    onclick="modificarCantidad(${index}, 1)"
                                    ${item.cantidad >= item.stock_maximo ? 'disabled' : ''}>
                                <i class="fas fa-plus"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" 
                                    onclick="eliminarDelCarrito(${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        carritoItems.innerHTML = html;
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('total').textContent = `$${subtotal.toFixed(2)}`;
        contadorCarrito.textContent = carrito.length;
        btnPagar.disabled = false;
    }
    
    // Actualizar resumen
    document.getElementById('totalProductos').textContent = carrito.length;
    document.getElementById('totalItems').textContent = carrito.reduce((sum, item) => sum + item.cantidad, 0);
}

function modificarCantidad(index, cambio) {
    const item = carrito[index];
    const nuevaCantidad = item.cantidad + cambio;
    
    if (nuevaCantidad <= 0) {
        eliminarDelCarrito(index);
        return;
    }
    
    if (nuevaCantidad > item.stock_maximo) {
        mostrarNotificacion(`❌ Stock máximo: ${item.stock_maximo} unidades`, 'error');
        return;
    }
    
    item.cantidad = nuevaCantidad;
    actualizarCarrito();
}

function eliminarDelCarrito(index) {
    carrito.splice(index, 1);
    actualizarCarrito();
    mostrarNotificacion('🗑️ Producto eliminado del carrito', 'info');
}

function limpiarCarrito() {
    if (carrito.length === 0) return;
    
    if (confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
        carrito = [];
        actualizarCarrito();
        mostrarNotificacion('🛒 Carrito limpiado', 'info');
    }
}

// =============================================
// 7. PROCESAMIENTO DE VENTA
// =============================================
async function procesarVenta() {
    if (carrito.length === 0) {
        mostrarNotificacion('❌ El carrito está vacío', 'error');
        return;
    }

    const metodoPago = document.querySelector('input[name="metodoPago"]:checked').value;
    
    try {
        // Mostrar loading
        document.getElementById('btnPagar').innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
        document.getElementById('btnPagar').disabled = true;
        
        const response = await fetch('/registrar_venta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                carrito: carrito,
                metodo_pago: metodoPago
            })
        });

        const resultado = await response.json();
        
        if (resultado.success) {
            // Mostrar modal de éxito
            document.getElementById('modalMessage').textContent = 
                `Venta #${resultado.venta_id} procesada correctamente`;
            document.getElementById('modalTotal').textContent = `$${resultado.total}`;
            document.getElementById('modalFactura').textContent = resultado.numero_factura;
            document.getElementById('modalMetodo').textContent = 
                metodoPago.charAt(0).toUpperCase() + metodoPago.slice(1);
            
            // Guardar datos para impresión
            window.ultimaFacturaId = resultado.factura_id;
            window.ultimoTotal = resultado.total;
            
            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
            modal.show();
            
            // Limpiar carrito y recargar productos
            carrito = [];
            actualizarCarrito();
            cargarProductos();
            
            mostrarNotificacion('✅ Venta procesada exitosamente', 'success');
            
        } else {
            mostrarNotificacion(`❌ Error: ${resultado.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error procesando venta:', error);
        mostrarNotificacion('❌ Error al procesar la venta', 'error');
    } finally {
        // Restaurar botón
        document.getElementById('btnPagar').innerHTML = '<i class="fas fa-cash-register me-2"></i>PROCESAR VENTA';
        document.getElementById('btnPagar').disabled = false;
    }
}

function imprimirFactura() {
    if (window.ultimaFacturaId) {
        window.open(`/imprimir_factura/${window.ultimaFacturaId}`, '_blank');
    }
}

// =============================================
// 8. DASHBOARD EN TIEMPO REAL
// =============================================
function iniciarDashboardTiempoReal() {
    // Actualizar hora cada segundo
    setInterval(actualizarHora, 1000);
    
    // Cargar métricas iniciales
    actualizarDashboard();
    
    // Actualizar cada 30 segundos
    setInterval(actualizarDashboard, 30000);
}

function actualizarHora() {
    const ahora = new Date();
    document.getElementById('horaActual').textContent = 
        ahora.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
}

async function actualizarDashboard() {
    try {
        // En un sistema real, aquí harías una llamada a una API
        // Por ahora usamos datos simulados basados en el carrito
        const ventasHoy = Math.floor(Math.random() * 50) + 10; // Simulado
        const ingresosHoy = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
        
        document.getElementById('ventasHoy').textContent = ventasHoy;
        document.getElementById('ingresosHoy').textContent = ingresosHoy.toFixed(0);
    } catch (error) {
        console.error('Error actualizando dashboard:', error);
    }
}

// =============================================
// 9. ATAJOS DE TECLADO
// =============================================
function configurarAtajosTeclado() {
    document.addEventListener('keydown', function(event) {
        // F1-F8: Navegación rápida por categorías
        if (event.key >= 'F1' && event.key <= 'F8' && categorias.length > 0) {
            event.preventDefault();
            const index = parseInt(event.key.slice(1)) - 1;
            if (index < categorias.length) {
                const categoria = categorias[index];
                filtrarPorCategoria(categoria);
                mostrarNotificacion(`📁 Categoría: ${categoria}`, 'info');
            }
        }
        
        // F2: Limpiar búsqueda
        if (event.key === 'F2') {
            event.preventDefault();
            limpiarBusqueda();
            mostrarNotificacion('🔍 Búsqueda limpiada', 'info');
        }
        
        // F3: Limpiar carrito
        if (event.key === 'F3') {
            event.preventDefault();
            limpiarCarrito();
        }
        
        // F9: Actualizar productos
        if (event.key === 'F9') {
            event.preventDefault();
            cargarProductos();
            mostrarNotificacion('🔄 Productos actualizados', 'info');
        }
        
        // F12: Procesar venta
        if (event.key === 'F12') {
            event.preventDefault();
            procesarVenta();
        }
        
        // ESC: Salir de inputs
        if (event.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement.classList.contains('cantidad-input')) {
                activeElement.blur();
            }
        }
    });
}

// =============================================
// 10. UTILIDADES Y NOTIFICACIONES
// =============================================
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear notificación toast
    const toast = document.createElement('div');
    toast.className = `alert alert-${tipo === 'error' ? 'danger' : tipo} alert-dismissible fade show`;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
    `;
    toast.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

function mostrarFeedbackAgregado(nombreProducto, cantidad = 1) {
    mostrarNotificacion(`✅ Agregado: ${cantidad} x ${nombreProducto}`, 'success');
}

function mostrarLoadingProductos() {
    document.getElementById('productosContainer').innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando productos...</span>
            </div>
            <p class="mt-2 text-muted">Cargando catálogo de productos...</p>
        </div>
    `;
}

function mostrarErrorProductos(error) {
    document.getElementById('productosContainer').innerHTML = `
        <div class="alert alert-danger text-center">
            <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
            <h5>Error al cargar productos</h5>
            <p class="mb-3">${error.message}</p>
            <div class="btn-group">
                <button onclick="cargarProductos()" class="btn btn-warning">
                    <i class="fas fa-redo me-1"></i>Reintentar
                </button>
                <button onclick="location.reload()" class="btn btn-secondary">
                    <i class="fas fa-sync me-1"></i>Recargar Página
                </button>
            </div>
        </div>
    `;
}

// =============================================
// FUNCIONES DE REPORTES PDF
// =============================================

function abrirReporteCierreCaja() {
    const hoy = new Date().toISOString().split('T')[0];
    window.open(`/reporte/cierre_caja?fecha=${hoy}`, '_blank');
}

function abrirReporteVentas() {
    window.open('/reporte/ventas', '_blank');
}

function abrirReporteProductos() {
    window.open('/reporte/productos_populares', '_blank');
}

function abrirAnalisisPredictivo() {
    window.open('/reporte/analisis_predictivo', '_blank');
}

// =============================================
// 11. INICIALIZACIÓN FINAL
// =============================================
console.log('🎯 POS Moderno cargado. Funciones disponibles:');
console.log('- F1-F8: Navegación rápida por categorías');
console.log('- F2: Limpiar búsqueda');
console.log('- F3: Limpiar carrito');
console.log('- F9: Actualizar productos');
console.log('- F12: Procesar venta');
console.log('- ENTER: Agregar producto al carrito');
console.log('- ESC: Salir de campo de cantidad');