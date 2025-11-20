# corregir_modelos_tenant.py
"""
Script para agregar panaderia_id a modelos faltantes
"""

def agregar_panaderia_id_a_modelos():
    modelos_faltantes = [
        'Sucursal', 'ConfiguracionPanaderia', 'Panaderia', 'CompraExterna',
        'HistorialCompra', 'Cliente', 'DetalleVenta', 'Compra', 'DetalleCompra',
        'Gasto', 'RecetaIngrediente', 'HistorialInventario', 'StockProducto',
        'ConfiguracionProduccion', 'HistorialRotacionProducto', 'ControlVidaUtil',
        'Factura', 'JornadaVentas', 'CierreDiario', 'PermisoUsuario', 'ConsecutivoPOS'
    ]
    
    # Este script modificará models.py automáticamente
    # Agregando panaderia_id a cada modelo