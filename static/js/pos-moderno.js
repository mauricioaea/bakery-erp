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
// CONFIGURACIÓN DE TICKETS PERSONALIZADOS
// =============================================

const configTicket = {
    empresa: {
        nombre: "Panadería Semillas",
        direccion: "Cra 18 #9-45 Atahualpa #123",
        telefono: "+57 3189098818",
        ruc: "123456789-0"  // ← Cambié "rut" por "ruc"
    },
    ticket: {
        mostrarLogo: true,
        logoUrl: "static/img/semillas.png",  // ← Ruta CORREGIDA
        mensajePersonalizado: "¡Gracias por su compra! Vuelva pronto",
        mostrarQR: true,
        qrMensaje: "Escanea para dejar tu reseña",
        qrUrl: "https://semillasbakery.com/resenas",
        mostrarPromociones: true,
        
    },
    diseño: {
        encabezadoColor: "#2c3e50",
        textoColor: "#2c3e50", 
        enfasisColor: "#e74c3c",
        fontSize: "12px",
        mostrarBordes: true
    }
};
// =============================================
// 1. INICIALIZACIÓN
// =============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando POS Moderno...');
    
    // Cargar carrito desde localStorage
    cargarCarritoPersistente();

    cargarConfiguracionTickets()
    
    // Cargar productos y categorías
    cargarProductos();
    
    // Iniciar dashboard en tiempo real
    iniciarDashboardTiempoReal();
    
    // Configurar atajos de teclado
    configurarAtajosTeclado();
    
    // Configurar búsqueda en tiempo real
    configurarBusquedaTiempoReal();
    
    // Verificar estado de cierre diario
    verificarEstadoCierreDiario();
    
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

// 🆕 FUNCIÓN PARA ACTUALIZAR CARRITO EN MÓVILES (NO EXISTÍA)
function actualizarCarritoMobile() {
    console.log('📱 Actualizando carrito móvil...');
    
    try {
        const contadorMobile = document.getElementById('carritoContadorMobile');
        const contadorCarrito = document.getElementById('contadorCarrito');
        
        if (contadorMobile && window.carrito) {
            const totalItems = window.carrito.reduce((total, item) => total + item.cantidad, 0);
            contadorMobile.textContent = totalItems;
            console.log('✅ Carrito móvil actualizado:', totalItems, 'items');
        }
        
        if (contadorCarrito && window.carrito) {
            const totalItems = window.carrito.reduce((total, item) => total + item.cantidad, 0);
            contadorCarrito.textContent = totalItems;
        }
    } catch (error) {
        console.warn('⚠️ Error en actualizarCarritoMobile:', error);
    }
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
// GENERADOR DE TICKETS OPTIMIZADO PARA IMPRESORAS TÉRMICAS
// =============================================

function generarTicketHTML(ventaData) {
    const { carrito, total, metodo_pago, numero_factura, fecha } = ventaData;
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ticket - ${configTicket.empresa.nombre}</title>
            <style>
                /* RESET PARA IMPRESORAS TÉRMICAS */
                * { 
                    margin: 0; 
                    padding: 0; 
                    box-sizing: border-box; 
                    font-family: 'Courier New', monospace !important;
                }
                
                body { 
                    width: 80mm !important; 
                    max-width: 80mm !important;
                    margin: 0 !important;
                    padding: 2mm !important;
                    font-size: 12px !important;
                    line-height: 1.2 !important;
                    background: white !important;
                    color: black !important;
                }
                
                .ticket-container {
                    width: 100% !important;
                    max-width: 76mm !important;
                    margin: 0 auto !important;
                }
                
                /* ENCABEZADO */
                .ticket-header {
                    text-align: center;
                    border-bottom: 1px dashed #000;
                    padding-bottom: 3mm;
                    margin-bottom: 3mm;
                }
                
                .ticket-empresa {
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 2mm;
                    text-transform: uppercase;
                }
                
                .ticket-info {
                    font-size: 10px;
                    margin-bottom: 2mm;
                }
                
                /* INFORMACIÓN DE VENTA */
                .venta-info {
                    text-align: center;
                    margin-bottom: 3mm;
                    font-size: 11px;
                }
                
                /* TABLA DE PRODUCTOS */
                .ticket-items {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 3mm 0;
                    font-size: 11px;
                }
                
                .ticket-items th {
                    text-align: left;
                    border-bottom: 1px solid #000;
                    padding: 1mm 0;
                    font-weight: bold;
                }
                
                .ticket-items td {
                    padding: 1mm 0;
                    border-bottom: 1px dotted #ccc;
                }
                
                .cantidad { text-align: center; width: 15%; }
                .precio { text-align: right; width: 25%; }
                .producto { width: 60%; }
                
                /* TOTAL */
                .ticket-total {
                    font-weight: bold;
                    font-size: 13px;
                    text-align: right;
                    margin-top: 3mm;
                    padding-top: 2mm;
                    border-top: 2px dashed #000;
                }
                
                /* MENSAJES */
                .ticket-mensaje {
                    text-align: center;
                    margin: 3mm 0;
                    padding: 2mm;
                    font-style: italic;
                    font-size: 10px;
                }
                
                .ticket-promocion {
                    text-align: center;
                    font-size: 9px;
                    margin: 2mm 0;
                    font-weight: bold;
                }
                
                /* QR SIMPLIFICADO */
                .ticket-qr {
                    text-align: center;
                    margin: 3mm 0;
                    font-size: 9px;
                }
                
                .qr-placeholder {
                    background: #f0f0f0;
                    padding: 3mm;
                    display: inline-block;
                    margin: 2mm 0;
                    font-size: 8px;
                }
                
                /* FOOTER */
                .ticket-footer {
                    text-align: center;
                    font-size: 8px;
                    margin-top: 4mm;
                    border-top: 1px dashed #ccc;
                    padding-top: 2mm;
                }
                
                /* OCULTAR ELEMENTOS EN IMPRESIÓN */
                @media print {
                    .no-print { display: none !important; }
                    body { 
                        width: 80mm !important; 
                        margin: 0 !important; 
                        padding: 0 !important;
                    }
                    .ticket-container { 
                        padding: 2mm !important;
                    }
                }
                
                /* ESTILOS PARA VISTA PREVIA */
                @media screen {
                    body { 
                        background: #f5f5f5; 
                        padding: 10px;
                    }
                    .ticket-container {
                        background: white;
                        padding: 5mm;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                }
            </style>
        </head>
        <body>
            <div class="ticket-container">
                <!-- ENCABEZADO CON LOGO -->
                <div class="ticket-header">
                    ${configTicket.ticket.mostrarLogo ? 
                        `<div style="text-align: center; margin-bottom: 2mm;">
                            <strong>[LOGO]</strong><br>
                            <small>${configTicket.empresa.nombre}</small>
                        </div>` 
                        : `<div class="ticket-empresa">${configTicket.empresa.nombre}</div>`
                    }
                    
                    <div class="ticket-info">
                        ${configTicket.empresa.direccion}<br>
                        Tel: ${configTicket.empresa.telefono}<br>
                        ${configTicket.empresa.ruc ? `NIT: ${configTicket.empresa.ruc}` : ''}
                    </div>
                </div>

                <!-- INFORMACIÓN DE LA VENTA -->
                <div class="venta-info">
                    <strong>FACTURA: ${numero_factura}</strong><br>
                    ${new Date(fecha).toLocaleDateString('es-CO')} ${new Date(fecha).toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'})}<br>
                    Método: ${metodo_pago.toUpperCase()}
                </div>

                <!-- ITEMS DE LA VENTA -->
                <table class="ticket-items">
                    <thead>
                        <tr>
                            <th class="producto">PRODUCTO</th>
                            <th class="cantidad">CANT</th>
                            <th class="precio">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${carrito.map(item => `
                            <tr>
                                <td class="producto">${item.nombre}</td>
                                <td class="cantidad">${item.cantidad}</td>
                                <td class="precio">$${(item.precio * item.cantidad).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <!-- TOTAL -->
                <div class="ticket-total">
                    TOTAL: $${total.toLocaleString()}
                </div>

                <!-- MENSAJE PERSONALIZADO -->
                ${configTicket.ticket.mensajePersonalizado ? `
                    <div class="ticket-mensaje">
                        ${configTicket.ticket.mensajePersonalizado}
                    </div>
                ` : ''}

                <!-- PROMOCIÓN -->
                ${configTicket.ticket.mostrarPromociones && configTicket.ticket.promocionActual ? `
                    <div class="ticket-promocion">
                        💫 ${configTicket.ticket.promocionActual}
                    </div>
                ` : ''}

                <!-- CÓDIGO QR -->
                ${configTicket.ticket.mostrarQR ? `
                    <div class="ticket-qr">
                        <div>${configTicket.ticket.qrMensaje}</div>
                        <div class="qr-placeholder">
                            [ CÓDIGO QR ]<br>
                            <small>${configTicket.ticket.qrUrl}</small>
                        </div>
                    </div>
                ` : ''}

                <!-- FOOTER -->
                <div class="ticket-footer">
                    ¡Gracias por su preferencia!<br>
                    Sistema POS Panadería v1.0
                </div>

                <!-- BOTONES SOLO EN VISTA PREVIA -->
                <div class="no-print" style="text-align: center; margin-top: 5mm; padding-top: 3mm; border-top: 1px dashed #ccc;">
                    <button onclick="window.print()" style="padding: 5px 10px; margin: 0 5px; font-size: 12px;">
                        🖨️ Imprimir
                    </button>
                    <button onclick="window.close()" style="padding: 5px 10px; margin: 0 5px; font-size: 12px;">
                        ❌ Cerrar
                    </button>
                </div>
            </div>
            
            <script>
                // Auto-imprimir en impresoras térmicas
                setTimeout(() => {
                    window.print();
                }, 500);
            </script>
        </body>
        </html>
    `;
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
            window.ultimaFacturaId = resultado.venta_id;
             window.tipoDocumento = resultado.tipo_documento || 'POS';
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

// =============================================
// IMPRESIÓN MEJORADA DE TICKETS
// =============================================

/**
 * FUNCIÓN UNIFICADA - Maneja ambos casos: POS y Facturación Electrónica
 */
function imprimirFactura(ventaId = null, tipoDocumento = null) {
    // Determinar el ID de la venta y tipo de documento
    const idVenta = ventaId || window.ultimaFacturaId;
    const tipoDoc = tipoDocumento || window.tipoDocumento || 'POS';
    
    console.log('🔍 Debug imprimirFactura:', { idVenta, tipoDoc, ventaId, tipoDocumento });
    
    if (!idVenta) {
        mostrarNotificacion('❌ No hay factura para imprimir', 'error');
        return;
    }

    console.log('🖨️ Imprimiendo:', tipoDoc, 'ID:', idVenta);

    if (tipoDoc === 'ELECTRONICA') {
        // Imprimir factura electrónica
        const url = `/api/imprimir-factura/${idVenta}`;
        console.log('📄 Abriendo factura electrónica:', url);
        const printWindow = window.open(url, '_blank', 'width=400,height=600');
    } else {
        // Para POS, usar el sistema de recibo tradicional
        console.log('🧾 Abriendo recibo POS');
        const url = `/imprimir_factura/${idVenta}`;
        const printWindow = window.open(url, '_blank');
    }
}

/**
 * Función para descargar XML de factura electrónica
 */
function descargarXMLFactura(ventaId) {
    if (!ventaId) {
        mostrarNotificacion('❌ No hay venta para exportar', 'error');
        return;
    }
    
    console.log('📥 Descargando XML para venta:', ventaId);
    const link = document.createElement('a');
    link.href = `/api/exportar-xml/${ventaId}`;
    link.download = `factura_${ventaId}.xml`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Función para descargar XML de factura electrónica
 */
function descargarXMLFactura(ventaId) {
    const link = document.createElement('a');
    link.href = `/api/exportar-xml/${ventaId}`;
    link.download = `factura_${ventaId}.xml`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Función auxiliar para calcular total
function calcularTotalCarrito() {
    return carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0);
}

// =============================================
// CONFIGURADOR DE TICKETS DESDE INTERFAZ
// =============================================

function mostrarConfiguracionTickets() {
    const modalHTML = `
        <div class="modal fade" id="configTicketModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-receipt me-2"></i>
                            Configuración de Tickets
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="formConfigTicket">
                            <!-- Información de Empresa -->
                            <div class="mb-3">
                                <label class="form-label">Nombre de Empresa</label>
                                <input type="text" class="form-control" 
                                       value="${configTicket.empresa.nombre}" 
                                       id="empresaNombre">
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label">Dirección</label>
                                    <input type="text" class="form-control" 
                                           value="${configTicket.empresa.direccion}" 
                                           id="empresaDireccion">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Teléfono</label>
                                    <input type="text" class="form-control" 
                                           value="${configTicket.empresa.telefono}" 
                                           id="empresaTelefono">
                                </div>
                            </div>

                            <!-- Mensajes Personalizados -->
                            <div class="mb-3">
                                <label class="form-label">Mensaje Personalizado</label>
                                <textarea class="form-control" rows="2" 
                                          id="ticketMensaje">${configTicket.ticket.mensajePersonalizado}</textarea>
                            </div>

                                <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" 
                                            ${configTicket.ticket.mostrarLogo ? 'checked' : ''}
                                            id="mostrarLogo" onchange="toggleLogoUrl()">
                                        <label class="form-check-label">Mostrar Logo</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" 
                                            ${configTicket.ticket.mostrarQR ? 'checked' : ''}
                                            id="mostrarQR">
                                        <label class="form-check-label">Mostrar QR</label>
                                    </div>
                                </div>
                            </div>

                            <!-- 🆕 AGREGAR ESTO INMEDIATAMENTE DESPUÉS -->
                            <div class="mb-3" id="logoUrlContainer" style="${configTicket.ticket.mostrarLogo ? '' : 'display: none;'}">
                                <label class="form-label">URL del Logo</label>
                                <input type="text" class="form-control" 
                                    value="${configTicket.ticket.logoUrl || ''}" 
                                    id="logoUrl" 
                                    placeholder="ruta/logo.png o https://ejemplo.com/logo.png">
                                <small class="text-muted">
                                    Ejemplo: "static/img/logo.png" o URL completa
                                </small>
                            </div>

                            <!-- Vista Previa -->
                            <div class="mt-4 p-3 border rounded">
                                <h6>Vista Previa del Ticket</h6>
                                <div style="font-size: 12px; font-family: 'Courier New';">
                                    <strong>${configTicket.empresa.nombre}</strong><br>
                                    ${configTicket.empresa.direccion}<br>
                                    ${configTicket.ticket.mensajePersonalizado}
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="guardarConfigTicket()">
                            Guardar Configuración
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('configTicketModal'));
    modal.show();

    // Limpiar al cerrar
    document.getElementById('configTicketModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}


function guardarConfigTicket() {
    // 1. Recoger datos del formulario (igual que antes)
    const configActualizada = {
        empresa: {
            nombre: document.getElementById('empresaNombre').value,
            direccion: document.getElementById('empresaDireccion').value,
            telefono: document.getElementById('empresaTelefono').value,
            nit: document.getElementById('empresaNIT')?.value || "900000000-1", // 🆕 Agregar si no existe
            ciudad: document.getElementById('empresaCiudad')?.value || "Pasto" // 🆕 Agregar si no existe
        },
        ticket: {
            mostrarLogo: document.getElementById('mostrarLogo').checked,
            logoUrl: document.getElementById('logoUrl')?.value || "", // 🆕 Agregar si no existe
            mensajePersonalizado: document.getElementById('ticketMensaje').value,
            mostrarQR: document.getElementById('mostrarQR').checked,
            qrMensaje: "Escanea para dejar tu reseña", // 🆕 Valor por defecto
            mostrarPromociones: true // 🆕 Valor por defecto
        },
        diseño: {
            encabezadoColor: "#2c3e50",
            textoColor: "#2c3e50",
            enfasisColor: "#e74c3c"
        }
    };

    // 2. 🆕 GUARDAR EN LOCALSTORAGE (para el recibo POS)
    localStorage.setItem('configTicketPersonalizada', JSON.stringify(configActualizada));

    // 3. 🆕 OPCIONAL: Guardar también en la variable global para compatibilidad
    if (typeof configTicket !== 'undefined') {
        Object.assign(configTicket, configActualizada);
    }

    // 4. Cerrar modal y mostrar mensaje
    bootstrap.Modal.getInstance(document.getElementById('configTicketModal')).hide();
    
    // 5. 🆕 ACTUALIZAR VISTA PREVIA INMEDIATA
    actualizarVistaPreviaTicket(configActualizada);
    
    alert('✅ Configuración de tickets guardada correctamente');
}

// 🆕 AGREGAR ESTA FUNCIÓN AUXILIAR SI NO EXISTE:
function actualizarVistaPreviaTicket(config) {
    const vistaPrevia = document.querySelector('#configTicketModal .border.rounded');
    if (vistaPrevia) {
        vistaPrevia.innerHTML = `
            <h6>Vista Previa del Ticket</h6>
            <div style="font-size: 12px; font-family: 'Courier New';">
                <strong>${config.empresa.nombre}</strong><br>
                ${config.empresa.direccion}<br>
                Tel: ${config.empresa.telefono}<br>
                ${config.ticket.mensajePersonalizado}
            </div>
        `;
    }
}

// Cargar configuración al iniciar
function cargarConfiguracionTickets() {
    const configGuardada = localStorage.getItem('config_ticket_panaderia');
    if (configGuardada) {
        Object.assign(configTicket, JSON.parse(configGuardada));
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
    
    // Verificar estado de cierre diario cada 30 segundos
    setInterval(verificarEstadoCierreDiario, 30000);
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
// 11. FUNCIONES PARA CIERRE DIARIO
// =============================================

async function procesarCierreDiario() {
    if (!confirm('¿Estás seguro de que deseas realizar el CIERRE DIARIO?\n\nEsta acción no se puede deshacer y reiniciará los contadores para el siguiente día.')) {
        return;
    }
    
    const btnCierre = document.getElementById('btnCierreDiario');
    const textoOriginal = btnCierre.innerHTML;
    
    try {
        btnCierre.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Procesando...';
        btnCierre.disabled = true;
        
        const response = await fetch('/api/cierre_diario/procesar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            // Mostrar modal de éxito
            mostrarModalCierreExitoso(resultado.cierre);
            
            // Recargar datos del dashboard
            actualizarDashboard();
            verificarEstadoCierreDiario();
            
            // Reiniciar contadores locales
            reiniciarContadoresDia();
            
        } else {
            throw new Error(resultado.error);
        }
        
    } catch (error) {
        console.error('Error en cierre diario:', error);
        alert('❌ Error al procesar cierre diario: ' + error.message);
    } finally {
        btnCierre.innerHTML = textoOriginal;
        btnCierre.disabled = false;
    }
}

function mostrarModalCierreExitoso(cierre) {
    const modalHTML = `
        <div class="modal fade" id="cierreExitosoModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-check-circle me-2"></i>
                            Cierre Diario Exitoso
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center mb-3">
                            <i class="fas fa-lock fa-3x text-success mb-3"></i>
                            <h4>Jornada Cerrada Correctamente</h4>
                        </div>
                        
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="metric-value text-primary">$${cierre.total_ventas.toLocaleString()}</div>
                                <div class="metric-label">Total Ventas</div>
                            </div>
                            <div class="col-6">
                                <div class="metric-value text-info">${cierre.total_transacciones}</div>
                                <div class="metric-label">Transacciones</div>
                            </div>
                        </div>
                        
                        <div class="mt-3 p-3 bg-light rounded">
                            <small class="text-muted">
                                <i class="fas fa-info-circle me-1"></i>
                                Los contadores se han reiniciado para el nuevo día.
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                            <i class="fas fa-check me-1"></i>
                            Entendido
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar modal al DOM y mostrarlo
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('cierreExitosoModal'));
    modal.show();
    
    // Limpiar modal después de cerrar
    document.getElementById('cierreExitosoModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function reiniciarContadoresDia() {
    // Reiniciar contadores locales del dashboard
    document.getElementById('ventasHoy').textContent = '0';
    document.getElementById('ingresosHoy').textContent = '0';
    document.getElementById('totalItems').textContent = '0';
    
    // Aquí puedes agregar más reinicios según necesites
    console.log('Contadores del día reiniciados');
}

// Función para verificar estado del cierre diario
async function verificarEstadoCierreDiario() {
    try {
        const response = await fetch('/api/cierre_diario/estado');
        const estado = await response.json();
        
        // Actualizar dashboard con datos reales
        document.getElementById('ventasHoy').textContent = estado.total_transacciones;
        document.getElementById('ingresosHoy').textContent = estado.total_ventas_hoy.toLocaleString();
        
        // Deshabilitar botón de cierre si ya se realizó
        const btnCierre = document.getElementById('btnCierreDiario');
        if (estado.cierre_realizado) {
            btnCierre.disabled = true;
            btnCierre.innerHTML = '<i class="fas fa-lock me-2"></i> CERRADO';
            btnCierre.classList.remove('btn-warning');
            btnCierre.classList.add('btn-secondary');
        }
        
    } catch (error) {
        console.error('Error verificando estado de cierre:', error);
    }
}

function toggleLogoUrl() {
    const mostrarLogo = document.getElementById('mostrarLogo').checked;
    const logoUrlContainer = document.getElementById('logoUrlContainer');
    
    if (logoUrlContainer) {
        logoUrlContainer.style.display = mostrarLogo ? 'block' : 'none';
    }
}



function irAConfiguracionFacturacion() {
    window.location.href = '/configuracion/facturacion';
}

// =============================================
// 12. INICIALIZACIÓN FINAL
// =============================================
console.log('🎯 POS Moderno cargado. Funciones disponibles:');
console.log('- F1-F8: Navegación rápida por categorías');
console.log('- F2: Limpiar búsqueda');
console.log('- F3: Limpiar carrito');
console.log('- F9: Actualizar productos');
console.log('- F12: Procesar venta');
console.log('- ENTER: Agregar producto al carrito');
console.log('- ESC: Salir de campo de cantidad');

// 🆕 EXPORTAR FUNCIONES AL ÁMBITO GLOBAL PARA INTEGRACIÓN CON FACTURACIÓN
// Esto permite que las funciones sean accesibles desde punto_venta.html

// Asignar funciones al objeto window para que sean globales
window.actualizarCarritoMobile = actualizarCarritoMobile;
window.actualizarCarrito = actualizarCarrito;
window.limpiarCarrito = limpiarCarrito;
window.cargarProductos = cargarProductos;
window.limpiarBusqueda = limpiarBusqueda;
window.procesarCierreDiario = procesarCierreDiario;
window.calcularTotalCarrito = calcularTotalCarrito; 

// 🆕 Hacer variables globales accesibles
window.carrito = carrito;

console.log('✅ Funciones del carrito exportadas al ámbito global');

// 🆕 INICIALIZACIÓN COMPATIBILIDAD
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Inicializando compatibilidad POS + Facturación electrónica');
    
    // Verificar que todas las funciones estén disponibles
    const funcionesRequeridas = [
        'actualizarCarritoMobile', 'actualizarCarrito', 'limpiarCarrito',
        'cargarProductos', 'limpiarBusqueda', 'procesarCierreDiario'
    ];
    
    funcionesRequeridas.forEach(funcion => {
        if (typeof window[funcion] === 'function') {
            console.log(`✅ ${funcion} disponible`);
        } else {
            console.warn(`⚠️ ${funcion} NO disponible`);
        }
    });
    
    // Inicializar carrito si no existe
    if (typeof window.carrito === 'undefined') {
        window.carrito = [];
        console.log('🔄 Carrito inicializado');
    }
});