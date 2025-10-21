# facturacion/generador_xml.py
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import uuid

def generar_xml_ubl_21(venta, config_empresa, detalles_venta):
    """
    Genera XML en formato UBL 2.1 para la DIAN
    Adaptado a la estructura real de tus modelos
    """
    try:
        # Namespaces UBL 2.1 requeridos por DIAN
        namespaces = {
            '': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }
        
        # Registrar namespaces
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri) if prefix else ET.register_namespace('', uri)
        
        # Crear elemento raíz
        root = ET.Element('Invoice', xmlns=namespaces[''])
        
        # === INFORMACIÓN BÁSICA DE LA FACTURA ===
        # CustomizationID (requerido por DIAN)
        customization_id = ET.SubElement(root, f'{{{namespaces["cbc"]}}}CustomizationID')
        customization_id.text = 'urn:cenb:names:specification:ubl:colombia:schema:xsd:ApplicationResponse-2'
        
        # ProfileID (requerido por DIAN)
        profile_id = ET.SubElement(root, f'{{{namespaces["cbc"]}}}ProfileID')
        profile_id.text = 'DIAN 2.1'
        
        # ID de factura (usar consecutivo POS o ID de venta)
        invoice_id = ET.SubElement(root, f'{{{namespaces["cbc"]}}}ID')
        invoice_id.text = str(venta.consecutivo_pos or venta.id)
        
        # UUID único
        uuid_elem = ET.SubElement(root, f'{{{namespaces["cbc"]}}}UUID')
        uuid_elem.text = str(uuid.uuid4()).upper()
        
        # Fecha de emisión
        issue_date = ET.SubElement(root, f'{{{namespaces["cbc"]}}}IssueDate')
        issue_date.text = venta.fecha_hora.strftime('%Y-%m-%d')
        
        # Hora de emisión
        issue_time = ET.SubElement(root, f'{{{namespaces["cbc"]}}}IssueTime')
        issue_time.text = venta.fecha_hora.strftime('%H:%M:%S')
        
        # Tipo de documento
        invoice_type = ET.SubElement(root, f'{{{namespaces["cbc"]}}}InvoiceTypeCode')
        invoice_type.text = '1'  # 1 = Factura electrónica de venta
        invoice_type.set('listID', '01')
        
        # === EMISOR (TU EMPRESA) ===
        supplier_party = ET.SubElement(root, f'{{{namespaces["cac"]}}}AccountingSupplierParty')
        party = ET.SubElement(supplier_party, f'{{{namespaces["cac"]}}}Party')
        
        # NIT emisor
        company_id = ET.SubElement(party, f'{{{namespaces["cac"]}}}PartyIdentification')
        company_id_scheme = ET.SubElement(company_id, f'{{{namespaces["cbc"]}}}ID')
        company_id_scheme.text = getattr(config_empresa, 'nit_empresa', '9000000001')
        company_id_scheme.set('schemeID', '31')  # 31 = NIT
        company_id_scheme.set('schemeName', '31')
        
        # Nombre emisor
        company_name = ET.SubElement(party, f'{{{namespaces["cac"]}}}PartyLegalEntity')
        company_name_elem = ET.SubElement(company_name, f'{{{namespaces["cbc"]}}}RegistrationName')
        company_name_elem.text = getattr(config_empresa, 'nombre_empresa', 'Mi Panadería SAS')
        
        # Dirección emisor
        address = ET.SubElement(company_name, f'{{{namespaces["cac"]}}}RegistrationAddress')
        city = ET.SubElement(address, f'{{{namespaces["cbc"]}}}CityName')
        city.text = getattr(config_empresa, 'ciudad_empresa', 'Bogotá')
        country = ET.SubElement(address, f'{{{namespaces["cbc"]}}}Country')
        country_code = ET.SubElement(country, f'{{{namespaces["cbc"]}}}IdentificationCode')
        country_code.text = 'CO'
        
        # === CLIENTE (CONSUMIDOR FINAL) ===
        customer_party = ET.SubElement(root, f'{{{namespaces["cac"]}}}AccountingCustomerParty')
        customer = ET.SubElement(customer_party, f'{{{namespaces["cac"]}}}Party')
        
        # Cliente genérico (consumidor final)
        customer_id = ET.SubElement(customer, f'{{{namespaces["cac"]}}}PartyIdentification')
        customer_id_scheme = ET.SubElement(customer_id, f'{{{namespaces["cbc"]}}}ID')
        customer_id_scheme.text = '222222222222'
        customer_id_scheme.set('schemeID', '13')  # 13 = Cédula de ciudadanía
        
        customer_name = ET.SubElement(customer, f'{{{namespaces["cac"]}}}PartyLegalEntity')
        customer_name_elem = ET.SubElement(customer_name, f'{{{namespaces["cbc"]}}}RegistrationName')
        customer_name_elem.text = 'CONSUMIDOR FINAL'
        
        # === LÍNEAS DE DETALLE (PRODUCTOS) ===
        line_count = 1
        for detalle in detalles_venta:
            line = ET.SubElement(root, f'{{{namespaces["cac"]}}}InvoiceLine')
            
            # ID de línea
            line_id = ET.SubElement(line, f'{{{namespaces["cbc"]}}}ID')
            line_id.text = str(line_count)
            
            # Cantidad
            quantity = ET.SubElement(line, f'{{{namespaces["cbc"]}}}InvoicedQuantity')
            quantity.text = str(detalle.cantidad)
            quantity.set('unitCode', '94')  # 94 = unidades
            
            # Monto de la línea (cantidad * precio unitario)
            line_amount = ET.SubElement(line, f'{{{namespaces["cbc"]}}}LineExtensionAmount')
            line_amount.text = str(detalle.precio_unitario * detalle.cantidad)
            line_amount.set('currencyID', 'COP')
            
            # Producto
            item = ET.SubElement(line, f'{{{namespaces["cac"]}}}Item')
            description = ET.SubElement(item, f'{{{namespaces["cbc"]}}}Description')
            
            # Manejar tanto productos internos como externos
            product_name = "Producto"
            if detalle.producto:
                product_name = detalle.producto.nombre
            elif detalle.producto_externo:
                product_name = detalle.producto_externo.nombre
            else:
                product_name = f"Producto {detalle.producto_id or detalle.producto_externo_id}"
                
            description.text = product_name
            
            # Precio unitario
            unit_price = ET.SubElement(line, f'{{{namespaces["cac"]}}}Price')
            unit_price_amount = ET.SubElement(unit_price, f'{{{namespaces["cbc"]}}}PriceAmount')
            unit_price_amount.text = str(detalle.precio_unitario)
            unit_price_amount.set('currencyID', 'COP')
            
            line_count += 1
        
        # === TOTALES ===
        legal_monetary_total = ET.SubElement(root, f'{{{namespaces["cac"]}}}LegalMonetaryTotal')
        
        # Total sin impuestos
        line_total = ET.SubElement(legal_monetary_total, f'{{{namespaces["cbc"]}}}LineExtensionAmount')
        line_total.text = str(venta.total)
        line_total.set('currencyID', 'COP')
        
        # Total con impuestos (para panadería, sin IVA)
        payable_amount = ET.SubElement(legal_monetary_total, f'{{{namespaces["cbc"]}}}PayableAmount')
        payable_amount.text = str(venta.total)
        payable_amount.set('currencyID', 'COP')
        
        # === MÉTODO DE PAGO ===
        payment_means = ET.SubElement(root, f'{{{namespaces["cac"]}}}PaymentMeans')
        payment_code = ET.SubElement(payment_means, f'{{{namespaces["cbc"]}}}PaymentMeansCode')
        
        # Mapear método de pago a código UBL
        metodo_pago_map = {
            'efectivo': '10',
            'tarjeta': '48', 
            'transferencia': '42'
        }
        payment_code.text = metodo_pago_map.get(venta.metodo_pago, '10')  # Default: efectivo
        
        # Convertir a string XML formateado
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_pretty = reparsed.toprettyxml(indent="  ", encoding='utf-8')
        
        return xml_pretty.decode('utf-8')
        
    except Exception as e:
        print(f"Error generando XML UBL 2.1: {str(e)}")
        # XML de error mínimo
        error_root = ET.Element('Error')
        error_msg = ET.SubElement(error_root, 'Mensaje')
        error_msg.text = f'No se pudo generar XML: {str(e)}'
        return ET.tostring(error_root, encoding='utf-8').decode('utf-8')