#!/usr/bin/env python3
"""
CORRECCIÓN ESPECÍFICA PARA TU models.py - AGREGAR panaderia_id A MODELOS FALTANTES
Basado en tu estructura exacta de models.py
"""

import re
import os

def corregir_models_especifico(archivo_models):
    """Corrige TU models.py específicamente"""
    
    print("🔧 CORRECCIÓN ESPECÍFICA PARA TU models.py")
    print("=" * 60)
    
    with open(archivo_models, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # MODELOS QUE NECESITAN panaderia_id EN TU CÓDIGO
    modelos_a_corregir = {
        'Sucursal': 'sucursales',
        'ConfiguracionPanaderia': 'configuracion_panaderia', 
        'Panaderia': 'panaderias',
        'CompraExterna': 'compras_externas',
        'HistorialCompra': 'historial_compras',
        'Cliente': 'clientes',
        'DetalleVenta': 'detalle_venta',
        'Compra': 'compras',
        'DetalleCompra': 'detalle_compras',
        'Gasto': 'gastos',
        'RecetaIngrediente': 'receta_ingredientes',
        'HistorialInventario': 'historial_inventario',
        'StockProducto': 'stock_productos',
        'ConfiguracionProduccion': 'configuracion_produccion',
        'HistorialRotacionProducto': 'historial_rotacion_producto',
        'ControlVidaUtil': 'control_vida_util',
        'Factura': 'facturas',
        'JornadaVentas': 'jornadas_ventas',
        'CierreDiario': 'cierres_diarios',
        'PermisoUsuario': 'permisos_usuario',
        'ConsecutivoPOS': 'consecutivos_pos'
    }
    
    cambios_realizados = 0
    nuevo_contenido = contenido
    
    for modelo, tabla in modelos_a_corregir.items():
        print(f"🔍 Verificando {modelo}...")
        
        # Buscar la definición de la clase
        patron = rf'(class {modelo}\(.*?db\.Model.*?\):.*?)(__tablename__ = \'{tabla}\'.*?)(\n    \w+ = db\.Column)'
        match = re.search(patron, contenido, re.DOTALL)
        
        if match:
            # Verificar si ya tiene panaderia_id
            if f'class {modelo}(' in contenido and 'panaderia_id' not in match.group(0):
                # Insertar panaderia_id después del __tablename__
                parte_antes = match.group(1) + match.group(2)
                parte_despues = match.group(3)
                
                nueva_parte = parte_antes + f'\n    panaderia_id = db.Column(db.Integer, nullable=False, default=1)' + parte_despues
                
                nuevo_contenido = nuevo_contenido.replace(match.group(0), nueva_parte)
                cambios_realizados += 1
                print(f"  ✅ panaderia_id agregado a {modelo}")
            else:
                print(f"  ✅ {modelo} ya tiene panaderia_id o no necesita cambios")
        else:
            print(f"  ⚠️  No se pudo encontrar la definición de {modelo}")
    
    # Guardar cambios si hay modificaciones
    if cambios_realizados > 0:
        # Backup
        backup_file = archivo_models + '.backup_antes_panaderia_id'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"📁 Backup creado: {backup_file}")
        
        # Guardar nuevo contenido
        with open(archivo_models, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print(f"\n🎯 {cambios_realizados} modelos corregidos exitosamente")
    else:
        print("\nℹ️  No se necesitaron correcciones en los modelos")
    
    return cambios_realizados

def verificar_y_agregar_relaciones(archivo_models):
    """Verifica y agrega relaciones con Panaderia donde sea necesario"""
    
    print("\n🔗 VERIFICANDO RELACIONES CON PANADERIA...")
    print("=" * 60)
    
    with open(archivo_models, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Modelos que deberían tener relación con Panaderia
    modelos_con_relacion = [
        'Sucursal', 'ConfiguracionPanaderia', 'CompraExterna', 'HistorialCompra',
        'Cliente', 'DetalleVenta', 'Compra', 'DetalleCompra', 'Gasto', 
        'RecetaIngrediente', 'HistorialInventario', 'StockProducto',
        'ConfiguracionProduccion', 'HistorialRotacionProducto', 'ControlVidaUtil',
        'Factura', 'JornadaVentas', 'CierreDiario', 'PermisoUsuario', 'ConsecutivoPOS'
    ]
    
    relaciones_agregadas = 0
    
    for modelo in modelos_con_relacion:
        # Buscar si ya tiene la relación
        if f"class {modelo}(" in contenido:
            if f'panaderia = db.relationship(\'Panaderia\'' not in contenido:
                # Encontrar el final de la clase para agregar la relación
                patron_fin_clase = rf'(class {modelo}\(.*?\):.*?)(\n\nclass|\Z)'
                match = re.search(patron_fin_clase, contenido, re.DOTALL)
                
                if match:
                    # Agregar relación antes del final
                    relacion = f'\n    panaderia = db.relationship(\'Panaderia\', backref=db.backref(\'{modelo.lower()}_list\', lazy=True))'
                    
                    nuevo_contenido = contenido.replace(match.group(1), match.group(1) + relacion)
                    contenido = nuevo_contenido
                    relaciones_agregadas += 1
                    print(f"  ✅ Relación agregada a {modelo}")
    
    if relaciones_agregadas > 0:
        with open(archivo_models, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n🔗 {relaciones_agregadas} relaciones con Panaderia agregadas")
    
    return relaciones_agregadas

if __name__ == "__main__":
    archivo_models = "models.py"
    
    if not os.path.exists(archivo_models):
        print("❌ Error: models.py no encontrado")
        exit(1)
    
    print("🚀 CORRECCIÓN ESPECÍFICA PARA TU STRUCTURA")
    print("=" * 60)
    
    # Paso 1: Agregar panaderia_id a modelos
    cambios = corregir_models_especifico(archivo_models)
    
    # Paso 2: Agregar relaciones
    relaciones = verificar_y_agregar_relaciones(archivo_models)
    
    print("\n" + "=" * 60)
    print("🎯 CORRECCIÓN COMPLETADA")
    print(f"📊 Resumen:")
    print(f"   • Modelos corregidos: {cambios}")
    print(f"   • Relaciones agregadas: {relaciones}")
    print("\n📋 Próximos pasos:")
    print("   1. Ejecutar nuevamente: python diagnostico_modelos_relaciones.py")
    print("   2. Crear migración de base de datos")
    print("   3. Aplicar decoradores tenant a rutas críticas")