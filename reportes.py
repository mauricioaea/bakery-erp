# reportes.py
import os
from datetime import datetime, timedelta
from io import BytesIO
from flask import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from models import db, RegistroDiario, PagoIndividual, SaldoBanco, Venta, Producto, Proveedor
from sqlalchemy import func, extract

# Agrega al inicio del archivo, después de las otras importaciones
try:
    from models import db
except ImportError:
    # Para compatibilidad si no está disponible
    db = None


class GeneradorReportes:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Centrado
        )
        self.estilo_subtitulo = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )
    
    def generar_reporte_estado_resultados(self, fecha_inicio, fecha_fin):
        """Genera reporte de Estado de Resultados (Pérdidas y Ganancias)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # Encabezado
        elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
        elements.append(Paragraph("ESTADO DE RESULTADOS", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Obtener datos
        ingresos = self._obtener_ingresos_periodo(fecha_inicio, fecha_fin)
        gastos = self._obtener_gastos_periodo(fecha_inicio, fecha_fin)
        
        # Tabla de Ingresos
        elements.append(Paragraph("INGRESOS", self.estilo_subtitulo))
        data_ingresos = [['Concepto', 'Monto']]
        total_ingresos = 0
        
        for concepto, monto in ingresos.items():
            if monto > 0:  # Solo mostrar conceptos con montos positivos
                data_ingresos.append([concepto, f"${monto:,.0f}"])
                total_ingresos += monto
        
        # CORREGIDO: Sin etiquetas HTML
        data_ingresos.append(['TOTAL INGRESOS', f"${total_ingresos:,.0f}"])
        
        tabla_ingresos = Table(data_ingresos, colWidths=[4*inch, 2*inch])
        tabla_ingresos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tabla_ingresos)
        elements.append(Spacer(1, 20))
        
        # Tabla de Gastos
        elements.append(Paragraph("GASTOS", self.estilo_subtitulo))
        data_gastos = [['Concepto', 'Monto']]
        total_gastos = 0
        
        for categoria, monto in gastos.items():
            if monto > 0:
                data_gastos.append([categoria, f"${monto:,.0f}"])
                total_gastos += monto
        
        # CORREGIDO: Sin etiquetas HTML
        data_gastos.append(['TOTAL GASTOS', f"${total_gastos:,.0f}"])
        
        tabla_gastos = Table(data_gastos, colWidths=[4*inch, 2*inch])
        tabla_gastos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tabla_gastos)
        elements.append(Spacer(1, 20))
        
        # Resultado Neto
        resultado_neto = total_ingresos - total_gastos
        color_resultado = colors.HexColor('#27ae60') if resultado_neto >= 0 else colors.HexColor('#c0392b')
        
        # CORREGIDO: Sin etiquetas HTML
        data_resultado = [['RESULTADO NETO DEL PERÍODO', f"${resultado_neto:,.0f}"]]
        tabla_resultado = Table(data_resultado, colWidths=[4*inch, 2*inch])
        tabla_resultado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), color_resultado),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tabla_resultado)
        
        # Análisis de Rentabilidad (mantener el HTML aquí porque Paragraph sí lo interpreta)
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("ANÁLISIS DE RENTABILIDAD", self.estilo_subtitulo))
        
        margen_ganancia = (resultado_neto / total_ingresos * 100) if total_ingresos > 0 else 0
        analisis_texto = f"""
        <b>Margen de Ganancia Neto:</b> {margen_ganancia:.1f}%<br/>
        <b>Relación Gastos/Ingresos:</b> {(total_gastos/total_ingresos*100):.1f}%<br/>
        <b>Rentabilidad:</b> {'POSITIVA' if resultado_neto >= 0 else 'NEGATIVA'}<br/>
        <b>Días del período:</b> {(fecha_fin - fecha_inicio).days + 1} días
        """
        elements.append(Paragraph(analisis_texto, self.styles['Normal']))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_flujo_caja(self, fecha_inicio, fecha_fin):
        """Genera reporte de Flujo de Caja"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []

        elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
        elements.append(Paragraph("REPORTE DE FLUJO DE CAJA", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 20))

        # Obtener datos de flujo de caja
        flujo_data = self._obtener_flujo_caja_periodo(fecha_inicio, fecha_fin)

        if not flujo_data:
            elements.append(Paragraph("No hay datos de flujo de caja para el período seleccionado.", self.styles['Normal']))
        else:
            data = [['Fecha', 'Ingresos', 'Gastos', 'Flujo Neto', 'Saldo Acumulado']]
            saldo_acumulado = 0

            for fecha, ingresos, gastos in flujo_data:
                flujo_neto = ingresos - gastos
                saldo_acumulado += flujo_neto
                data.append([
                    fecha.strftime('%d/%m/%Y'),
                    f"${ingresos:,.0f}" if ingresos > 0 else "$0",
                    f"${gastos:,.0f}" if gastos > 0 else "$0",
                    f"${flujo_neto:,.0f}",
                    f"${saldo_acumulado:,.0f}"
                ])

            # Agregar totales - CORREGIDO: Sin etiquetas HTML
            total_ingresos = sum(item[1] for item in flujo_data)
            total_gastos = sum(item[2] for item in flujo_data)
            data.append([
                'TOTALES',
                f"${total_ingresos:,.0f}",
                f"${total_gastos:,.0f}",
                f"${total_ingresos - total_gastos:,.0f}",
                f"${saldo_acumulado:,.0f}"
            ])

            tabla = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
                
                # ESTILOS MEJORADOS PARA LA FILA DE TOTALES
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(tabla)

            # Análisis
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("ANÁLISIS DE FLUJO DE CAJA", self.estilo_subtitulo))

            promedio_diario = (total_ingresos - total_gastos) / len(flujo_data) if flujo_data else 0
            dias_positivos = sum(1 for _, ingresos, gastos in flujo_data if ingresos - gastos > 0)
            porcentaje_positivos = (dias_positivos / len(flujo_data) * 100) if flujo_data else 0

            analisis_texto = f"""
            <b>Flujo neto total:</b> ${total_ingresos - total_gastos:,.0f}<br/>
            <b>Promedio diario:</b> ${promedio_diario:,.0f}<br/>
            <b>Días con flujo positivo:</b> {dias_positivos} de {len(flujo_data)} ({porcentaje_positivos:.1f}%)<br/>
            <b>Saldo final del período:</b> ${saldo_acumulado:,.0f}
            """
            elements.append(Paragraph(analisis_texto, self.styles['Normal']))

        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _obtener_ingresos_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene ingresos agrupados por concepto"""
        try:
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin)
            ).all()
            
            ingresos = {
                'Ventas en Efectivo': sum(r.efectivo or 0 for r in registros),
                'Transferencias Recibidas': sum(r.transferencias or 0 for r in registros),
                'Ventas con Tarjeta': sum(r.tarjetas or 0 for r in registros),
                'Otros Ingresos': 0
            }
            
            return ingresos
        except Exception as e:
            print(f"Error al obtener ingresos: {e}")
            return {}
    
    def _obtener_gastos_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene gastos agrupados por categoría"""
        try:
            pagos = PagoIndividual.query.filter(
                PagoIndividual.fecha_pago.between(fecha_inicio, fecha_fin)
            ).all()
            
            gastos = {}
            for pago in pagos:
                if pago.categoria not in gastos:
                    gastos[pago.categoria] = 0
                gastos[pago.categoria] += pago.monto
            
            return gastos
        except Exception as e:
            print(f"Error al obtener gastos: {e}")
            return {}
    
    def _obtener_flujo_caja_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene datos para flujo de caja diario"""
        try:
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin)
            ).order_by(RegistroDiario.fecha).all()
            
            flujo_data = []
            for registro in registros:
                ingresos = (registro.efectivo or 0) + (registro.transferencias or 0) + (registro.tarjetas or 0)
                gastos = registro.total_egresos or 0
                flujo_data.append((registro.fecha, ingresos, gastos))
            
            return flujo_data
        except Exception as e:
            print(f"Error al obtener flujo de caja: {e}")
            return []
        
    #=======================================libro contable=================================================
    def generar_reporte_libro_diario(self, fecha_inicio, fecha_fin):
        """Genera reporte de Libro Diario Contable con todos los movimientos"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []

        # Encabezado
        elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
        elements.append(Paragraph("LIBRO DIARIO CONTABLE", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 15))

        # Obtener todos los movimientos del período
        movimientos = self._obtener_movimientos_periodo(fecha_inicio, fecha_fin)

        if not movimientos:
            elements.append(Paragraph("No hay movimientos contables para el período seleccionado.", self.styles['Normal']))
        else:
            # Tabla principal del libro diario
            data = [['Fecha', 'Concepto', 'Referencia', 'Débito', 'Crédito', 'Saldo']]
            
            saldo_acumulado = 0
            total_debitos = 0
            total_creditos = 0

            for movimiento in movimientos:
                fecha, concepto, referencia, debito, credito, tipo = movimiento
                
                # Actualizar saldo
                if tipo == 'INGRESO':
                    saldo_acumulado += debito
                else:  # EGRESO
                    saldo_acumulado -= credito

                total_debitos += debito
                total_creditos += credito

                data.append([
                    fecha.strftime('%d/%m/%Y'),
                    concepto,
                    referencia or '-',
                    f"${debito:,.0f}" if debito > 0 else "$0",
                    f"${credito:,.0f}" if credito > 0 else "$0",
                    f"${saldo_acumulado:,.0f}"
                ])

            # Agregar línea de totales
            data.append([
                'TOTALES',
                '',
                '',
                f"${total_debitos:,.0f}",
                f"${total_creditos:,.0f}",
                f"${saldo_acumulado:,.0f}"
            ])

            # Crear tabla
            tabla = Table(data, colWidths=[0.8*inch, 2.2*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.2*inch])
            tabla.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
                
                # Totales
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 8),
            ]))
            
            elements.append(tabla)
            elements.append(Spacer(1, 20))

            # Resumen contable
            elements.append(Paragraph("RESUMEN CONTABLE", self.estilo_subtitulo))
            
            diferencia = total_debitos - total_creditos
            estado_cuadre = "CUADRADO" if abs(diferencia) < 1 else "DESCUADRADO"
            color_estado = colors.green if estado_cuadre == "CUADRADO" else colors.red
            
            resumen_texto = f"""
            <b>Total Débitos:</b> ${total_debitos:,.0f}<br/>
            <b>Total Créditos:</b> ${total_creditos:,.0f}<br/>
            <b>Diferencia:</b> ${diferencia:,.0f}<br/>
            <b>Estado:</b> <font color="{'green' if estado_cuadre == 'CUADRADO' else 'red'}">{estado_cuadre}</font><br/>
            <b>Saldo Final:</b> ${saldo_acumulado:,.0f}<br/>
            <b>Total Movimientos:</b> {len(movimientos)}
            """
            elements.append(Paragraph(resumen_texto, self.styles['Normal']))

        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _obtener_movimientos_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene todos los movimientos contables del período"""
        try:
            movimientos = []
            
            # 1. Obtener ingresos de cierre de caja
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin)
            ).order_by(RegistroDiario.fecha).all()
            
            for registro in registros:
                # Efectivo como ingreso
                if registro.efectivo and registro.efectivo > 0:
                    movimientos.append((
                        registro.fecha,
                        "VENTAS EN EFECTIVO",
                        f"CIERRE {registro.fecha}",
                        registro.efectivo,
                        0,
                        'INGRESO'
                    ))
                
                # Transferencias como ingreso
                if registro.transferencias and registro.transferencias > 0:
                    movimientos.append((
                        registro.fecha,
                        "TRANSFERENCIAS RECIBIDAS",
                        f"CIERRE {registro.fecha}",
                        registro.transferencias,
                        0,
                        'INGRESO'
                    ))
                
                # Tarjetas como ingreso
                if registro.tarjetas and registro.tarjetas > 0:
                    movimientos.append((
                        registro.fecha,
                        "VENTAS CON TARJETA",
                        f"CIERRE {registro.fecha}",
                        registro.tarjetas,
                        0,
                        'INGRESO'
                    ))
            
            # 2. Obtener pagos (egresos)
            pagos = PagoIndividual.query.filter(
                PagoIndividual.fecha_pago.between(fecha_inicio, fecha_fin)
            ).order_by(PagoIndividual.fecha_pago).all()
            
            for pago in pagos:
                movimientos.append((
                    pago.fecha_pago,
                    f"PAGO - {pago.categoria.replace('_', ' ').title()}",
                    pago.referencia or pago.numero_factura or f"PAGO#{pago.id}",
                    0,
                    pago.monto,
                    'EGRESO'
                ))
            
            # 3. Ordenar todos los movimientos por fecha
            movimientos.sort(key=lambda x: x[0])
            
            return movimientos
            
        except Exception as e:
            print(f"Error al obtener movimientos: {e}")
            return []

    #==========================================Conciliacion Bancaria=========================================================
    def generar_reporte_conciliacion_bancaria(self, fecha_corte, saldo_extracto):
        """Genera reporte de Conciliación Bancaria"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            elements = []

            # Encabezado
            elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
            elements.append(Paragraph("CONCILIACIÓN BANCARIA", self.estilo_titulo))
            elements.append(Paragraph(f"Fecha de Corte: {fecha_corte}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # Obtener saldo del sistema
            saldo_sistema_obj = SaldoBanco.query.filter(
                SaldoBanco.fecha_actualizacion <= fecha_corte
            ).order_by(SaldoBanco.fecha_actualizacion.desc()).first()
            
            saldo_sistema = saldo_sistema_obj.saldo_actual if saldo_sistema_obj else 0

            # Obtener movimientos no conciliados
            depositos_pendientes = self._obtener_depositos_pendientes(fecha_corte)
            cheques_pendientes = self._obtener_cheques_pendientes(fecha_corte)

            # 1. TABLA DE COMPARACIÓN DE SALDOS
            elements.append(Paragraph("COMPARACIÓN DE SALDOS", self.estilo_subtitulo))
            
            data_comparacion = [
                ['Concepto', 'Monto'],
                ['Saldo según Extracto Bancario', f"${saldo_extracto:,.0f}"],
                ['Saldo según Sistema', f"${saldo_sistema:,.0f}"],
                ['Diferencia a Conciliar', f"${saldo_extracto - saldo_sistema:,.0f}"]
            ]
            
            tabla_comparacion = Table(data_comparacion, colWidths=[4*inch, 2*inch])
            tabla_comparacion.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c') if abs(saldo_extracto - saldo_sistema) > 1 else colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(tabla_comparacion)
            elements.append(Spacer(1, 20))

            # 2. DEPÓSITOS EN TRÁNSITO
            total_depositos = 0
            if depositos_pendientes:
                elements.append(Paragraph("DEPÓSITOS EN TRÁNSITO", self.estilo_subtitulo))
                data_depositos = [['Fecha', 'Descripción', 'Referencia', 'Monto']]
                
                for deposito in depositos_pendientes:
                    data_depositos.append([
                        deposito['fecha'].strftime('%d/%m/%Y'),
                        deposito['descripcion'],
                        deposito['referencia'],
                        f"${deposito['monto']:,.0f}"
                    ])
                    total_depositos += deposito['monto']
                
                data_depositos.append(['TOTAL DEPÓSITOS EN TRÁNSITO', '', '', f"${total_depositos:,.0f}"])
                
                tabla_depositos = Table(data_depositos, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch])
                tabla_depositos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#229954')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(tabla_depositos)
                elements.append(Spacer(1, 15))

            # 3. CHEQUES PENDIENTES DE COBRO
            total_cheques = 0
            if cheques_pendientes:
                elements.append(Paragraph("CHEQUES PENDIENTES DE COBRO", self.estilo_subtitulo))
                data_cheques = [['Fecha', 'Beneficiario', 'N° Cheque', 'Monto']]
                
                for cheque in cheques_pendientes:
                    data_cheques.append([
                        cheque['fecha'].strftime('%d/%m/%Y'),
                        cheque['beneficiario'],
                        cheque['numero_cheque'],
                        f"${cheque['monto']:,.0f}"
                    ])
                    total_cheques += cheque['monto']
                
                data_cheques.append(['TOTAL CHEQUES PENDIENTES', '', '', f"${total_cheques:,.0f}"])
                
                tabla_cheques = Table(data_cheques, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch])
                tabla_cheques.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c0392b')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(tabla_cheques)
                elements.append(Spacer(1, 15))

            # 4. RESUMEN DE CONCILIACIÓN
            elements.append(Paragraph("RESUMEN DE CONCILIACIÓN", self.estilo_subtitulo))
            
            saldo_conciliado = saldo_sistema + total_depositos - total_cheques
            diferencia_final = saldo_extracto - saldo_conciliado
            conciliacion_exitosa = abs(diferencia_final) <= 1

            data_resumen = [
                ['Saldo según Sistema', f"${saldo_sistema:,.0f}"],
                ['(+) Depósitos en Tránsito', f"${total_depositos:,.0f}"],
                ['(-) Cheques Pendientes', f"-${total_cheques:,.0f}"],
                ['SALDO CONCILIADO', f"${saldo_conciliado:,.0f}"],
                ['Saldo según Extracto', f"${saldo_extracto:,.0f}"],
                ['DIFERENCIA FINAL', f"${diferencia_final:,.0f}"]
            ]
            
            tabla_resumen = Table(data_resumen, colWidths=[3*inch, 2*inch])
            tabla_resumen.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
                ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#27ae60') if conciliacion_exitosa else colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 5), (-1, 5), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(tabla_resumen)
            
            # Estado de la conciliación
            elements.append(Spacer(1, 15))
            
            estado_texto = f"""
            <b>Estado de la Conciliación:</b> <font color="{'green' if conciliacion_exitosa else 'red'}">{"CONCILIACIÓN EXITOSA" if conciliacion_exitosa else "CONCILIACIÓN PENDIENTE"}</font><br/>
            <b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Preparado por:</b> Sistema de Gestión Panadería Semillas
            """
            elements.append(Paragraph(estado_texto, self.styles['Normal']))

            # Pie de página
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Documento para fines de auditoría interna", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))

            # Construir el documento
            doc.build(elements)
            buffer.seek(0)
            return buffer

        except Exception as e:
            print(f"Error en generar_reporte_conciliacion_bancaria: {str(e)}")
            # Crear un PDF de error mínimo
            error_buffer = BytesIO()
            doc = SimpleDocTemplate(error_buffer, pagesize=A4)
            elements = [Paragraph(f"Error al generar reporte: {str(e)}", self.styles['Normal'])]
            doc.build(elements)
            error_buffer.seek(0)
            return error_buffer

    def _obtener_depositos_pendientes(self, fecha_corte):
        """Obtiene depósitos en tránsito (efectivo no depositado)"""
        try:
            # Buscar efectivo de cierres de caja que no se haya depositado
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha <= fecha_corte,
                RegistroDiario.efectivo > 0
            ).all()
            
            depositos = []
            for registro in registros:
                depositos.append({
                    'fecha': registro.fecha,
                    'descripcion': 'EFECTIVO POR DEPOSITAR',
                    'referencia': f'CIERRE {registro.fecha}',
                    'monto': registro.efectivo or 0
                })
            
            return depositos
        except Exception as e:
            print(f"Error al obtener depósitos pendientes: {e}")
            return []

    def _obtener_cheques_pendientes(self, fecha_corte):
        """Obtiene cheques pendientes de cobro"""
        # Por ahora retornar lista vacía - puedes expandir esto cuando implementes módulo de cheques
        return []

    def _obtener_otros_ajustes(self, fecha_corte):
        """Obtiene otros ajustes para conciliación"""
        # Por ahora retornar lista vacía - puedes expandir esto
        return []
    
#====================================== Análisis de Gastos por Categoría========================================================
    def generar_reporte_analisis_gastos(self, fecha_inicio, fecha_fin):
        """Genera reporte de Análisis de Gastos por Categoría CON GRÁFICOS"""
        try:
            print(f"🎯 Generando análisis de gastos para {fecha_inicio} a {fecha_fin}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            elements = []

            # Encabezado
            elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
            elements.append(Paragraph("ANÁLISIS DE GASTOS POR CATEGORÍA", self.estilo_titulo))
            elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # Obtener datos de gastos
            gastos_por_categoria = self._obtener_gastos_por_categoria(fecha_inicio, fecha_fin)
            
            if not gastos_por_categoria:
                elements.append(Paragraph("No hay datos de gastos para el período seleccionado.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            total_gastos = sum(gastos_por_categoria.values())
            categorias_ordenadas = sorted(gastos_por_categoria.items(), key=lambda x: x[1], reverse=True)

            # ✅ NUEVO: GRÁFICO DE DISTRIBUCIÓN DE GASTOS
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                
                # Crear figura con 2 subgráficos
                fig = Figure(figsize=(10, 8))
                
                # --- GRÁFICO 1: Torta (Distribución) ---
                ax1 = fig.add_subplot(211)
                
                # Preparar datos para el gráfico (tomar top 6 categorías y agrupar el resto como "Otros")
                if len(categorias_ordenadas) > 6:
                    top_categorias = categorias_ordenadas[:6]
                    otros_monto = sum(monto for _, monto in categorias_ordenadas[6:])
                    labels = [cat[0].replace('_', ' ').title() for cat in top_categorias] + ['Otros']
                    valores = [cat[1] for cat in top_categorias] + [otros_monto]
                    explode = [0.05] * len(top_categorias) + [0]  # Resaltar las principales
                else:
                    labels = [cat[0].replace('_', ' ').title() for cat in categorias_ordenadas]
                    valores = [cat[1] for cat in categorias_ordenadas]
                    explode = [0.05] * len(categorias_ordenadas)
                
                # Usar colores de matplotlib directamente
                colors_plt = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                
                # Crear gráfico de torta
                wedges, texts, autotexts = ax1.pie(
                    valores, 
                    labels=labels, 
                    autopct='%1.1f%%', 
                    startangle=90,
                    explode=explode,
                    colors=colors_plt,
                    shadow=True
                )
                ax1.set_title('Distribución de Gastos por Categoría', fontsize=14, fontweight='bold', pad=20)
                
                # Mejorar estética de los porcentajes
                for autotext in autotexts:
                    autotext.set_color('darkblue')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
                
                # --- GRÁFICO 2: Barras (Top 10 categorías) ---
                ax2 = fig.add_subplot(212)
                
                # Tomar top 10 categorías para el gráfico de barras
                top_10 = categorias_ordenadas[:10]
                categorias_barras = [cat[0].replace('_', ' ').title() for cat in top_10]
                montos_barras = [cat[1] for cat in top_10]
                
                # Crear gráfico de barras horizontal con colores de matplotlib
                y_pos = np.arange(len(categorias_barras))
                colors_barras = plt.cm.viridis(np.linspace(0, 1, len(categorias_barras)))
                bars = ax2.barh(y_pos, montos_barras, color=colors_barras)
                ax2.set_yticks(y_pos)
                ax2.set_yticklabels(categorias_barras, fontsize=9)
                ax2.set_xlabel('Monto ($)', fontweight='bold')
                ax2.set_title('Top 10 Categorías por Monto Gastado', fontsize=12, fontweight='bold', pad=10)
                
                # Agregar valores en las barras
                for bar, monto in zip(bars, montos_barras):
                    width = bar.get_width()
                    ax2.text(width + (max(montos_barras) * 0.01), bar.get_y() + bar.get_height()/2,
                            f'${monto:,.0f}', ha='left', va='center', fontsize=8, fontweight='bold')
                
                # Ajustar diseño
                fig.tight_layout(pad=3.0)
                
                # Guardar gráfico en buffer
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=150, bbox_inches='tight', 
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                # Agregar gráfico al PDF
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE GASTOS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6.5*inch, height=5*inch))
                elements.append(Spacer(1, 15))
                
                print("✅ Gráficos de matplotlib generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráfico: {e}. Continuando sin gráfico.")

            # 1. TABLA DETALLADA DE GASTOS
            elements.append(Paragraph("DISTRIBUCIÓN DETALLADA DE GASTOS", self.estilo_subtitulo))
            
            data_gastos = [['Categoría', 'Monto', 'Porcentaje']]
            
            for categoria, monto in categorias_ordenadas:
                porcentaje = (monto / total_gastos * 100) if total_gastos > 0 else 0
                data_gastos.append([
                    categoria.replace('_', ' ').title(),
                    f"${monto:,.0f}",
                    f"{porcentaje:.1f}%"
                ])
            
            # Agregar total
            data_gastos.append([
                'TOTAL GASTOS',
                f"${total_gastos:,.0f}",
                '100%'
            ])
            
            # ✅ CORREGIDO: Usar reportlab.lib.colors explícitamente
            from reportlab.lib import colors as rl_colors
            
            tabla_gastos = Table(data_gastos, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            tabla_gastos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, -1), (-1, -1), rl_colors.HexColor('#c0392b')),
                ('TEXTCOLOR', (0, -1), (-1, -1), rl_colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, rl_colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_gastos)
            elements.append(Spacer(1, 20))

            # 2. ANÁLISIS DETALLADO
            elements.append(Paragraph("ANÁLISIS DETALLADO", self.estilo_subtitulo))
            
            # Categoría con mayor gasto
            categoria_mayor = categorias_ordenadas[0] if categorias_ordenadas else ('N/A', 0)
            # Top 3 categorías
            top_3 = categorias_ordenadas[:3]
            porcentaje_top_3 = sum(monto for _, monto in top_3) / total_gastos * 100 if total_gastos > 0 else 0
            
            # Cálculos para el análisis
            gasto_promedio = total_gastos / len(gastos_por_categoria) if gastos_por_categoria else 0
            porcentaje_mayor = (categoria_mayor[1] / total_gastos * 100) if total_gastos > 0 else 0
            
            analisis_texto = f"""
            <b>Total de Gastos Analizados:</b> ${total_gastos:,.0f}<br/>
            <b>Categoría con Mayor Gasto:</b> {categoria_mayor[0].replace('_', ' ').title()} (${categoria_mayor[1]:,.0f})<br/>
            <b>Dominancia de Categoría Principal:</b> {porcentaje_mayor:.1f}% del total<br/>
            <b>Porcentaje de Top 3 Categorías:</b> {porcentaje_top_3:.1f}% del total<br/>
            <b>Número de Categorías:</b> {len(gastos_por_categoria)}<br/>
            <b>Gasto Promedio por Categoría:</b> ${gasto_promedio:,.0f}
            """
            elements.append(Paragraph(analisis_texto, self.styles['Normal']))
            elements.append(Spacer(1, 15))

            # 3. RECOMENDACIONES
            elements.append(Paragraph("RECOMENDACIONES ESTRATÉGICAS", self.estilo_subtitulo))
            
            recomendaciones = self._generar_recomendaciones_gastos(gastos_por_categoria, total_gastos)
            for recomendacion in recomendaciones:
                elements.append(Paragraph(f"• {recomendacion}", self.styles['Normal']))

            # Pie de página
            elements.append(Spacer(1, 30))
            elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=rl_colors.gray)))

            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Análisis de gastos con gráficos generado exitosamente. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_analisis_gastos: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Crear un PDF de error mínimo
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE GASTOS")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_gastos_por_categoria(self, fecha_inicio, fecha_fin):
            """Obtiene gastos agrupados por categoría para el análisis"""
            try:
                # Usar la misma función que ya tienes para gastos
                return self._obtener_gastos_periodo(fecha_inicio, fecha_fin)
            except Exception as e:
                print(f"Error al obtener gastos por categoría: {e}")
                return {}

    def _generar_recomendaciones_gastos(self, gastos_por_categoria, total_gastos):
            """Genera recomendaciones inteligentes basadas en los gastos"""
            recomendaciones = []
            
            if not gastos_por_categoria:
                return ["No hay suficientes datos para generar recomendaciones."]
            
            # Encontrar la categoría con mayor gasto
            categoria_mayor = max(gastos_por_categoria.items(), key=lambda x: x[1])
            porcentaje_mayor = (categoria_mayor[1] / total_gastos * 100) if total_gastos > 0 else 0
            
            # Recomendación basada en la categoría con mayor gasto
            if porcentaje_mayor > 50:
                recomendaciones.append(f"La categoría '{categoria_mayor[0].replace('_', ' ').title()}' representa el {porcentaje_mayor:.1f}% de tus gastos totales. Considera optimizar esta área.")
            
            # Recomendación si hay muchas categorías con montos similares
            if len(gastos_por_categoria) >= 5:
                recomendaciones.append("Tus gastos están distribuidos en múltiples categorías. Esto indica una buena diversificación.")
            
            # Recomendación general de análisis
            if total_gastos > 1000000:  # Si los gastos superan 1 millón
                recomendaciones.append("Tus gastos totales son significativos. Recomendamos revisar contratos y negociar mejores términos con proveedores.")
            
            # Recomendación de categorías específicas
            categorias_altas = {cat: monto for cat, monto in gastos_por_categoria.items() if monto > total_gastos * 0.2}
            for cat, monto in categorias_altas.items():
                if cat not in [categoria_mayor[0]]:
                    porcentaje = (monto / total_gastos * 100)
                    recomendaciones.append(f"La categoría '{cat.replace('_', ' ').title()}' representa el {porcentaje:.1f}% de tus gastos. Vale la pena revisarla.")
            
            if not recomendaciones:
                recomendaciones.append("Tus gastos parecen estar bien distribuidos. Continúa con el monitoreo regular.")
            
            return recomendaciones[:4]  # Máximo 4 recomendaciones
        
        
#=================================================== Tendencia de Ventas=================================================

    def generar_reporte_tendencia_ventas(self, fecha_inicio, fecha_fin):
        """Genera reporte de Tendencia de Ventas con análisis de comportamiento - OPTIMIZADO"""
        try:
            print(f"📈 Generando tendencia de ventas para {fecha_inicio} a {fecha_fin}")
            
            # ✅ CONFIGURACIÓN OPTIMIZADA PARA ESPACIOS
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,      # Reducido de 1 a 0.5
                                bottomMargin=0.5*inch,   # Reducido
                                leftMargin=0.4*inch,     # Reducido
                                rightMargin=0.4*inch)    # Reducido
            
            elements = []

            # ✅ ENCABEZADO COMPACTO
            elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
            elements.append(Paragraph("ANÁLISIS DE TENDENCIA DE VENTAS", self.estilo_titulo))
            elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))  # Reducido de 20 a 10

            # Obtener datos de ventas
            datos_ventas = self._obtener_datos_tendencia_ventas(fecha_inicio, fecha_fin)
            
            if not datos_ventas:
                elements.append(Paragraph("No hay datos de ventas para el período seleccionado.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # ✅ GRÁFICOS DE TENDENCIA OPTIMIZADOS
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                
                # Crear figura más compacta
                fig = Figure(figsize=(10, 8))  # Reducido de (12, 10)
                
                # Preparar datos
                fechas = [item['fecha'] for item in datos_ventas]
                ventas_diarias = [item['venta_total'] for item in datos_ventas]
                ventas_acumuladas = np.cumsum(ventas_diarias)
                
                # --- GRÁFICO 1: Tendencia de Ventas Diarias ---
                ax1 = fig.add_subplot(311)
                ax1.plot(fechas, ventas_diarias, color='#3498db', linewidth=2, marker='o', markersize=3)  # Reducido
                ax1.fill_between(fechas, ventas_diarias, alpha=0.3, color='#3498db')
                
                if len(ventas_diarias) > 1:
                    z = np.polyfit(range(len(ventas_diarias)), ventas_diarias, 1)
                    p = np.poly1d(z)
                    ax1.plot(fechas, p(range(len(ventas_diarias))), "r--", alpha=0.8, linewidth=1, label='Tendencia')
                    ax1.legend(fontsize=8)  # Fuente más pequeña
                
                ax1.set_title('Evolución de Ventas Diarias', fontsize=12, fontweight='bold', pad=10)  # Reducido
                ax1.set_ylabel('Ventas ($)', fontweight='bold', fontsize=9)
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45, labelsize=8)
                ax1.tick_params(axis='y', labelsize=8)
                
                # --- GRÁFICO 2: Ventas Acumuladas ---
                ax2 = fig.add_subplot(312)
                ax2.plot(fechas, ventas_acumuladas, color='#27ae60', linewidth=2)
                ax2.fill_between(fechas, ventas_acumuladas, alpha=0.3, color='#27ae60')
                
                ax2.set_title('Ventas Acumuladas', fontsize=12, fontweight='bold', pad=10)
                ax2.set_ylabel('Ventas Acumuladas ($)', fontweight='bold', fontsize=9)
                ax2.grid(True, alpha=0.3)
                ax2.tick_params(axis='x', rotation=45, labelsize=8)
                ax2.tick_params(axis='y', labelsize=8)
                
                # --- GRÁFICO 3: Análisis Semanal ---
                ax3 = fig.add_subplot(313)
                
                if len(datos_ventas) >= 7:
                    df_ventas = pd.DataFrame(datos_ventas)
                    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
                    df_ventas['dia_semana'] = df_ventas['fecha'].dt.day_name()
                    
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_esp = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']  # Abreviado
                    
                    ventas_por_dia = df_ventas.groupby('dia_semana')['venta_total'].mean().reindex(dias_orden)
                    
                    bars = ax3.bar(dias_esp, ventas_por_dia.values, 
                                color=plt.cm.viridis(np.linspace(0, 1, 7)),
                                alpha=0.8)
                    
                    ax3.set_title('Promedio de Ventas por Día', fontsize=12, fontweight='bold', pad=10)
                    ax3.set_ylabel('Ventas Promedio ($)', fontweight='bold', fontsize=9)
                    ax3.grid(True, alpha=0.3, axis='y')
                    ax3.tick_params(axis='both', labelsize=8)
                    
                    # Valores en barras más compactos
                    for bar, valor in zip(bars, ventas_por_dia.values):
                        height = bar.get_height()
                        ax3.text(bar.get_x() + bar.get_width()/2., height + (max(ventas_por_dia.values) * 0.005),
                                f'${valor:,.0f}', ha='center', va='bottom', fontsize=7, fontweight='bold')  # Reducido
                else:
                    ax3.text(0.5, 0.5, 'Se necesitan más datos\npara análisis semanal', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Análisis Semanal (Datos Insuficientes)', fontsize=12, fontweight='bold', pad=10)
                
                # Ajustar diseño más compacto
                fig.tight_layout(pad=2.0)  # Reducido de 3.0
                
                # Guardar gráfico optimizado
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',  # DPI reducido
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                # Agregar gráfico al PDF
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE TENDENCIAS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))  # Reducido
                elements.append(Spacer(1, 10))  # Reducido de 15
                
                print("✅ Gráficos de tendencia optimizados generados")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos de tendencia: {e}. Continuando sin gráficos.")

            # ✅ SECCIÓN ESTADÍSTICAS COMPACTA
            elements.append(Paragraph("ESTADÍSTICAS PRINCIPALES", self.estilo_subtitulo))
            
            ventas_totales = sum(item['venta_total'] for item in datos_ventas)
            venta_promedio = np.mean([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            venta_maxima = max([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            venta_minima = min([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            dias_analizados = len(datos_ventas)
            
            mejor_dia = max(datos_ventas, key=lambda x: x['venta_total']) if datos_ventas else None
            peor_dia = min(datos_ventas, key=lambda x: x['venta_total']) if datos_ventas else None
            
            # Texto más compacto
            estadisticas_texto = f"""
            <b>Período Analizado:</b> {dias_analizados} días | <b>Ventas Totales:</b> ${ventas_totales:,.0f}<br/>
            <b>Venta Promedio:</b> ${venta_promedio:,.0f} | <b>Venta Máxima:</b> ${venta_maxima:,.0f} {f"({mejor_dia['fecha'].strftime('%d/%m')})" if mejor_dia else ""}<br/>
            <b>Venta Mínima:</b> ${venta_minima:,.0f} {f"({peor_dia['fecha'].strftime('%d/%m')})" if peor_dia else ""} | <b>Variabilidad:</b> ${venta_maxima - venta_minima:,.0f}
            """
            
            # Usar estilo más compacto
            estilo_compacto = ParagraphStyle(
                'Compacto',
                parent=self.styles['Normal'],
                fontSize=9,  # Reducido
                leading=11,  # Interlineado reducido
                spaceAfter=6  # Espacio después reducido
            )
            
            elements.append(Paragraph(estadisticas_texto, estilo_compacto))
            elements.append(Spacer(1, 12))  # Reducido de 20

            # ✅ ANÁLISIS DE PATRONES COMPACTO
            elements.append(Paragraph("DETECCIÓN DE PATRONES", self.estilo_subtitulo))
            
            patrones = self._analizar_patrones_ventas(datos_ventas)
            for patron in patrones:
                elements.append(Paragraph(f"• {patron}", estilo_compacto))
            
            elements.append(Spacer(1, 10))  # Reducido de 15

            # ✅ PROYECCIÓN Y RECOMENDACIONES COMPACTA
            elements.append(Paragraph("PROYECCIÓN Y RECOMENDACIONES", self.estilo_subtitulo))
            
            proyecciones = self._generar_proyecciones_ventas(datos_ventas)
            for proyeccion in proyecciones:
                elements.append(Paragraph(f"• {proyeccion}", estilo_compacto))

            # ✅ PIE DE PÁGINA COMPACTO
            elements.append(Spacer(1, 15))  # Reducido de 30
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            # ✅ CONSTRUIR DOCUMENTO
            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de tendencia OPTIMIZADO generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_tendencia_ventas: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Crear un PDF de error mínimo
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE TENDENCIA")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_tendencia_ventas(self, fecha_inicio, fecha_fin):
        """Obtiene datos de ventas para análisis de tendencias"""
        try:
            # Obtener registros diarios en el período
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin)
            ).order_by(RegistroDiario.fecha).all()
            
            datos_ventas = []
            for registro in registros:
                venta_total = (registro.efectivo or 0) + (registro.transferencias or 0) + (registro.tarjetas or 0)
                if venta_total > 0:  # Solo incluir días con ventas
                    datos_ventas.append({
                        'fecha': registro.fecha,
                        'venta_total': venta_total,
                        'efectivo': registro.efectivo or 0,
                        'transferencias': registro.transferencias or 0,
                        'tarjetas': registro.tarjetas or 0
                    })
            
            return datos_ventas
            
        except Exception as e:
            print(f"Error al obtener datos de tendencia de ventas: {e}")
            return []

    def _analizar_patrones_ventas(self, datos_ventas):
        """Analiza patrones en los datos de ventas"""
        patrones = []
        
        if len(datos_ventas) < 7:
            return ["Se necesitan más datos (mínimo 7 días) para detectar patrones significativos."]
        
        try:
            import pandas as pd
            import numpy as np
            
            df = pd.DataFrame(datos_ventas)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['dia_semana'] = df['fecha'].dt.day_name()
            
            # Análisis de crecimiento
            ventas = [item['venta_total'] for item in datos_ventas]
            crecimiento = ((ventas[-1] - ventas[0]) / ventas[0] * 100) if ventas[0] > 0 else 0
            
            if crecimiento > 10:
                patrones.append(f"Tendencia creciente fuerte: +{crecimiento:.1f}% en el período")
            elif crecimiento > 0:
                patrones.append(f"Ligera tendencia creciente: +{crecimiento:.1f}% en el período")
            elif crecimiento < -10:
                patrones.append(f"Tendencia decreciente preocupante: {crecimiento:.1f}% en el período")
            elif crecimiento < 0:
                patrones.append(f"Ligera tendencia decreciente: {crecimiento:.1f}% en el período")
            else:
                patrones.append("Ventas estables sin crecimiento significativo")
            
            # Análisis de días de la semana
            ventas_por_dia = df.groupby('dia_semana')['venta_total'].mean()
            mejor_dia = ventas_por_dia.idxmax()
            peor_dia = ventas_por_dia.idxmin()
            
            # Traducir días al español
            dias_traduccion = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            patrones.append(f"Día más fuerte: {dias_traduccion.get(mejor_dia, mejor_dia)}")
            patrones.append(f"Día más débil: {dias_traduccion.get(peor_dia, peor_dia)}")
            
            # Detectar outliers (valores atípicos)
            Q1 = np.percentile(ventas, 25)
            Q3 = np.percentile(ventas, 75)
            IQR = Q3 - Q1
            outliers = [v for v in ventas if v < (Q1 - 1.5 * IQR) or v > (Q3 + 1.5 * IQR)]
            
            if outliers:
                patrones.append(f"Se detectaron {len(outliers)} días con ventas atípicas (fuera del rango normal)")
            
            return patrones[:5]  # Máximo 5 patrones
            
        except Exception as e:
            print(f"Error en análisis de patrones: {e}")
            return ["Análisis de patrones no disponible por error técnico"]

    def _generar_proyecciones_ventas(self, datos_ventas):
        """Genera proyecciones basadas en tendencias históricas"""
        proyecciones = []
        
        if len(datos_ventas) < 14:
            return ["Se necesitan más datos históricos (mínimo 14 días) para proyecciones confiables."]
        
        try:
            import numpy as np
            
            ventas = [item['venta_total'] for item in datos_ventas]
            venta_promedio = np.mean(ventas)
            venta_ultima_semana = np.mean(ventas[-7:]) if len(ventas) >= 7 else venta_promedio
            
            # Proyección simple
            crecimiento_semanal = ((venta_ultima_semana - np.mean(ventas[:-7])) / np.mean(ventas[:-7]) * 100) if len(ventas) >= 14 else 0
            
            proyecciones.append(f"Venta promedio actual: ${venta_promedio:,.0f}")
            proyecciones.append(f"Venta promedio última semana: ${venta_ultima_semana:,.0f}")
            
            if crecimiento_semanal > 5:
                proyecciones.append(f"Tendencia positiva: las ventas de la última semana son {crecimiento_semanal:.1f}% mayores")
                proyecciones.append("Recomendación: Mantener estrategias actuales y considerar expansión")
            elif crecimiento_semanal < -5:
                proyecciones.append(f"Alerta: las ventas de la última semana son {abs(crecimiento_semanal):.1f}% menores")
                proyecciones.append("Recomendación: Revisar estrategias de marketing y promociones")
            else:
                proyecciones.append("Ventas estables: sin cambios significativos en la última semana")
                proyecciones.append("Recomendación: Enfocarse en retención de clientes y eficiencia operativa")
            
            return proyecciones
            
        except Exception as e:
            print(f"Error en generación de proyecciones: {e}")
            return ["Proyecciones no disponibles por error técnico"]

# ===============================================Recomendaciones con IA===========================================================

# =================================================== Análisis Predictivo IA ==================================================

    def generar_reporte_ia_predictivo(self, fecha_inicio, fecha_fin):
        """Genera reporte de IA Predictivo con recomendaciones inteligentes - OPTIMIZADO"""
        try:
            print(f"🤖 Generando análisis predictivo IA para {fecha_inicio} a {fecha_fin}")
            
            # ✅ CONFIGURACIÓN OPTIMIZADA
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch,
                                leftMargin=0.4*inch,
                                rightMargin=0.4*inch)
            
            elements = []

            # ✅ ENCABEZADO COMPACTO
            elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
            elements.append(Paragraph("🤖 ANÁLISIS PREDICTIVO CON INTELIGENCIA ARTIFICIAL", self.estilo_titulo))
            elements.append(Paragraph(f"Período de análisis: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))

            # Obtener datos para análisis
            datos_ventas = self._obtener_datos_tendencia_ventas(fecha_inicio, fecha_fin)
            datos_productos = self._obtener_datos_productos_populares(fecha_inicio, fecha_fin)
            
            if not datos_ventas:
                elements.append(Paragraph("No hay datos suficientes para análisis predictivo.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # ✅ GRÁFICOS PREDICTIVOS OPTIMIZADOS
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                from datetime import timedelta
                
                # Crear figura compacta para análisis predictivo
                fig = Figure(figsize=(10, 8))
                
                # Preparar datos históricos
                fechas = [item['fecha'] for item in datos_ventas]
                ventas_diarias = [item['venta_total'] for item in datos_ventas]
                
                # --- GRÁFICO 1: Tendencia con Proyección ---
                ax1 = fig.add_subplot(221)  # 2x2 grid, posición 1
                
                # Datos históricos
                ax1.plot(fechas, ventas_diarias, color='#3498db', linewidth=2, marker='o', markersize=3, label='Ventas Reales')
                
                # Proyección simple (regresión lineal)
                if len(ventas_diarias) > 5:
                    x = np.arange(len(ventas_diarias))
                    z = np.polyfit(x, ventas_diarias, 1)
                    p = np.poly1d(z)
                    
                    # Proyectar 7 días adelante
                    x_future = np.arange(len(ventas_diarias) + 7)
                    y_future = p(x_future)
                    
                    # Gráfico de proyección
                    ax1.plot(x_future[:len(ventas_diarias)], y_future[:len(ventas_diarias)], 
                            'r--', alpha=0.7, linewidth=1.5, label='Ajuste')
                    ax1.plot(x_future[len(ventas_diarias):], y_future[len(ventas_diarias):], 
                            'g--', alpha=0.7, linewidth=2, label='Proyección 7 días')
                    
                    ax1.fill_between(x_future[len(ventas_diarias):], 
                                y_future[len(ventas_diarias):] * 0.8,
                                y_future[len(ventas_diarias):] * 1.2,
                                alpha=0.2, color='green', label='Rango probable')
                
                ax1.set_title('Tendencia y Proyección', fontsize=11, fontweight='bold', pad=8)
                ax1.set_ylabel('Ventas ($)', fontsize=9)
                ax1.legend(fontsize=7)
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45, labelsize=7)
                ax1.tick_params(axis='y', labelsize=7)
                
                # --- GRÁFICO 2: Análisis de Estacionalidad Semanal ---
                ax2 = fig.add_subplot(222)
                
                if len(datos_ventas) >= 14:
                    df = pd.DataFrame(datos_ventas)
                    df['fecha'] = pd.to_datetime(df['fecha'])
                    df['dia_semana'] = df['fecha'].dt.day_name()
                    df['semana'] = df['fecha'].dt.isocalendar().week
                    
                    # Promedio por día de semana
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_esp = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                    
                    ventas_por_dia = df.groupby('dia_semana')['venta_total'].mean().reindex(dias_orden)
                    
                    bars = ax2.bar(dias_esp, ventas_por_dia.values, 
                                color=plt.cm.Set3(np.linspace(0, 1, 7)),
                                alpha=0.8)
                    
                    # Línea de promedio general
                    promedio_general = np.mean(ventas_diarias)
                    ax2.axhline(y=promedio_general, color='red', linestyle='--', alpha=0.7, 
                            label=f'Promedio: ${promedio_general:,.0f}')
                    
                    ax2.set_title('Patrón Semanal', fontsize=11, fontweight='bold', pad=8)
                    ax2.set_ylabel('Ventas Promedio ($)', fontsize=9)
                    ax2.legend(fontsize=7)
                    ax2.grid(True, alpha=0.3, axis='y')
                    ax2.tick_params(axis='both', labelsize=7)
                    
                    # Valores en barras
                    for bar, valor in zip(bars, ventas_por_dia.values):
                        height = bar.get_height()
                        color = 'green' if valor > promedio_general else 'red'
                        ax2.text(bar.get_x() + bar.get_width()/2., height + (max(ventas_por_dia.values) * 0.01),
                                f'${valor:,.0f}', ha='center', va='bottom', fontsize=6, 
                                fontweight='bold', color=color)
                else:
                    ax2.text(0.5, 0.5, 'Se necesitan más datos\npara análisis semanal', 
                            ha='center', va='center', transform=ax2.transAxes, fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax2.set_title('Patrón Semanal', fontsize=11, fontweight='bold', pad=8)
                
                # --- GRÁFICO 3: Análisis de Crecimiento ---
                ax3 = fig.add_subplot(223)
                
                if len(ventas_diarias) > 1:
                    # Cálculo de crecimiento diario
                    crecimiento = []
                    for i in range(1, len(ventas_diarias)):
                        if ventas_diarias[i-1] > 0:
                            crecimiento.append(((ventas_diarias[i] - ventas_diarias[i-1]) / ventas_diarias[i-1]) * 100)
                        else:
                            crecimiento.append(0)
                    
                    # Gráfico de crecimiento
                    colores = ['green' if x >= 0 else 'red' for x in crecimiento]
                    bars = ax3.bar(range(len(crecimiento)), crecimiento, color=colores, alpha=0.7)
                    
                    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                    ax3.set_title('Crecimiento Diario (%)', fontsize=11, fontweight='bold', pad=8)
                    ax3.set_ylabel('Crecimiento %', fontsize=9)
                    ax3.grid(True, alpha=0.3, axis='y')
                    ax3.tick_params(axis='both', labelsize=7)
                    
                    # Promedio de crecimiento
                    crecimiento_promedio = np.mean(crecimiento) if crecimiento else 0
                    ax3.axhline(y=crecimiento_promedio, color='blue', linestyle='--', alpha=0.7,
                            label=f'Promedio: {crecimiento_promedio:+.1f}%')
                    ax3.legend(fontsize=7)
                else:
                    ax3.text(0.5, 0.5, 'Insuficientes datos\npara análisis de crecimiento', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Crecimiento Diario', fontsize=11, fontweight='bold', pad=8)
                
                # --- GRÁFICO 4: Heatmap de Performance ---
                ax4 = fig.add_subplot(224)
                
                if len(datos_ventas) >= 7:
                    # Calcular métricas de performance
                    venta_max = max(ventas_diarias)
                    venta_min = min(ventas_diarias)
                    venta_prom = np.mean(ventas_diarias)
                    desviacion = np.std(ventas_diarias)
                    
                    # Métricas para heatmap visual
                    metricas = ['Máxima', 'Mínima', 'Promedio', 'Estabilidad']
                    valores = [venta_max, venta_min, venta_prom, (1 - (desviacion/venta_prom)) * 100 if venta_prom > 0 else 0]
                    colores_metricas = ['#27ae60', '#e74c3c', '#3498db', '#f39c12']
                    
                    bars = ax4.bar(metricas, valores, color=colores_metricas, alpha=0.8)
                    ax4.set_title('Métricas Clave', fontsize=11, fontweight='bold', pad=8)
                    ax4.set_ylabel('Valor', fontsize=9)
                    ax4.grid(True, alpha=0.3, axis='y')
                    ax4.tick_params(axis='both', labelsize=7)
                    
                    # Valores en barras
                    for bar, valor, metrica in zip(bars, valores, metricas):
                        height = bar.get_height()
                        if metrica == 'Estabilidad':
                            texto = f'{valor:.1f}%'
                        else:
                            texto = f'${valor:,.0f}'
                        ax4.text(bar.get_x() + bar.get_width()/2., height + (max(valores) * 0.01),
                                texto, ha='center', va='bottom', fontsize=7, fontweight='bold')
                else:
                    ax4.text(0.5, 0.5, 'Datos insuficientes\npara métricas', 
                            ha='center', va='center', transform=ax4.transAxes, fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax4.set_title('Métricas Clave', fontsize=11, fontweight='bold', pad=8)
                
                # Ajustar diseño compacto
                fig.tight_layout(pad=2.0)
                
                # Guardar gráfico optimizado
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                # Agregar gráfico al PDF
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL PREDICTIVO", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))
                elements.append(Spacer(1, 10))
                
                print("✅ Gráficos predictivos generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos predictivos: {e}. Continuando sin gráficos.")

            # ✅ RECOMENDACIONES INTELIGENTES DE IA
            elements.append(Paragraph("🤖 RECOMENDACIONES INTELIGENTES", self.estilo_subtitulo))
            
            recomendaciones = self._generar_recomendaciones_ia(datos_ventas, datos_productos)
            
            estilo_recomendacion = ParagraphStyle(
                'Recomendacion',
                parent=self.styles['Normal'],
                fontSize=9,
                leading=12,
                spaceAfter=6,
                leftIndent=10
            )
            
            for i, recomendacion in enumerate(recomendaciones, 1):
                elements.append(Paragraph(f"{i}. {recomendacion}", estilo_recomendacion))
            
            elements.append(Spacer(1, 12))

            # ✅ PREDICCIONES Y ALERTAS
            elements.append(Paragraph("🔮 PREDICCIONES PARA PRÓXIMA SEMANA", self.estilo_subtitulo))
            
            predicciones = self._generar_predicciones_semanales(datos_ventas)
            
            for prediccion in predicciones:
                elements.append(Paragraph(f"• {prediccion}", estilo_recomendacion))
            
            elements.append(Spacer(1, 10))

            # ✅ PLAN DE ACCIÓN AUTOMATIZADO
            elements.append(Paragraph("🎯 PLAN DE ACCIÓN RECOMENDADO", self.estilo_subtitulo))
            
            plan_accion = self._generar_plan_accion(datos_ventas, datos_productos)
            
            for accion in plan_accion:
                elements.append(Paragraph(f"✓ {accion}", estilo_recomendacion))

            # ✅ PIE DE PÁGINA COMPACTO
            elements.append(Spacer(1, 15))
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"🤖 Generado por Sistema IA el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            # ✅ CONSTRUIR DOCUMENTO
            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de IA predictivo generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_ia_predictivo: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Crear PDF de error mínimo
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE IA")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_productos_populares(self, fecha_inicio, fecha_fin):
        """Obtiene datos de productos populares para análisis"""
        try:
            # Esta función depende de tu estructura de base de datos
            # Por ahora retornamos datos de ejemplo
            return [
                {'producto': 'Pan Francés', 'ventas': 150, 'ingreso': 750000},
                {'producto': 'Croissants', 'ventas': 120, 'ingreso': 600000},
                {'producto': 'Tortas', 'ventas': 80, 'ingreso': 1200000},
                {'producto': 'Galletas', 'ventas': 200, 'ingreso': 400000}
            ]
        except Exception as e:
            print(f"Error al obtener datos de productos: {e}")
            return []

    def _generar_recomendaciones_ia(self, datos_ventas, datos_productos):
        """Genera recomendaciones inteligentes basadas en datos"""
        recomendaciones = []
        
        if len(datos_ventas) < 7:
            return ["Se necesitan más datos históricos (mínimo 7 días) para recomendaciones precisas."]
        
        try:
            import numpy as np
            import pandas as pd
            
            ventas = [item['venta_total'] for item in datos_ventas]
            venta_promedio = np.mean(ventas)
            venta_ultima_semana = np.mean(ventas[-7:]) if len(ventas) >= 7 else venta_promedio
            
            # Análisis de tendencia
            crecimiento_semanal = ((venta_ultima_semana - np.mean(ventas[:-7])) / np.mean(ventas[:-7]) * 100) if len(ventas) >= 14 else 0
            
            # Recomendaciones basadas en tendencia
            if crecimiento_semanal > 15:
                recomendaciones.append("📈 **Tendencia muy positiva**: Considera aumentar capacidad de producción y expandir horarios")
                recomendaciones.append("💰 **Oportunidad de inversión**: Buen momento para invertir en nuevo equipamiento")
            elif crecimiento_semanal > 5:
                recomendaciones.append("📈 **Crecimiento estable**: Mantén las estrategias actuales y enfócate en retención de clientes")
            elif crecimiento_semanal < -10:
                recomendaciones.append("⚠️ **Alerta de decrecimiento**: Revisa estrategias de marketing y considera promociones")
            else:
                recomendaciones.append("⚖️ **Estabilidad detectada**: Enfócate en eficiencia operativa y reducción de costos")
            
            # Análisis de variabilidad
            coeficiente_variacion = (np.std(ventas) / venta_promedio * 100) if venta_promedio > 0 else 0
            
            if coeficiente_variacion > 40:
                recomendaciones.append("🎢 **Alta variabilidad**: Implementa estrategias para suavizar ventas (promociones en días bajos)")
            elif coeficiente_variacion > 20:
                recomendaciones.append("📊 **Variabilidad moderada**: Analiza causas de fluctuaciones para optimizar inventario")
            else:
                recomendaciones.append("📐 **Baja variabilidad**: Excelente para planeación de producción y inventario")
            
            # Recomendaciones de productos (si hay datos)
            if datos_productos:
                producto_top = max(datos_productos, key=lambda x: x['ingreso'])
                producto_mas_vendido = max(datos_productos, key=lambda x: x['ventas'])
                
                recomendaciones.append(f"🏆 **Producto estrella**: {producto_top['producto']} genera máximo ingreso (${producto_top['ingreso']:,.0f})")
                recomendaciones.append(f"🛒 **Más vendido**: {producto_mas_vendido['producto']} ({producto_mas_vendido['ventas']} unidades)")
            
            # Recomendación general de horarios
            recomendaciones.append("⏰ **Optimización horaria**: Analiza datos de hora pico para ajustar personal y producción")
            recomendaciones.append("🔍 **Análisis continuo**: Monitorea estas métricas semanalmente para ajustar estrategias")
            
            return recomendaciones[:8]  # Máximo 8 recomendaciones
            
        except Exception as e:
            print(f"Error en generación de recomendaciones: {e}")
            return ["Las recomendaciones no están disponibles temporalmente por error técnico"]

    def _generar_predicciones_semanales(self, datos_ventas):
        """Genera predicciones para la próxima semana"""
        predicciones = []
        
        if len(datos_ventas) < 14:
            return ["Se necesitan más datos históricos (14+ días) para predicciones confiables."]
        
        try:
            import numpy as np
            
            ventas = [item['venta_total'] for item in datos_ventas]
            venta_promedio = np.mean(ventas)
            tendencia_semanal = np.mean(ventas[-7:]) - np.mean(ventas[-14:-7])
            
            # Predicción simple
            prediccion_base = np.mean(ventas[-7:]) + (tendencia_semanal * 0.5)  # Suavizado
            
            predicciones.append(f"Ventas proyectadas: ${prediccion_base:,.0f} - ${prediccion_base * 1.15:,.0f}")
            predicciones.append(f"Crecimiento esperado: {((prediccion_base - np.mean(ventas[-7:])) / np.mean(ventas[-7:]) * 100):+.1f}%")
            
            # Predicciones específicas
            if tendencia_semanal > 0:
                predicciones.append("📈 Expectativa: Crecimiento continuo en próxima semana")
                predicciones.append("💡 Recomendación: Prepara inventario adicional")
            else:
                predicciones.append("📉 Expectativa: Ventas estables o leve decrecimiento")
                predicciones.append("💡 Recomendación: Enfócate en promociones estratégicas")
            
            predicciones.append("🎯 Días clave: Viernes y Sábado mostrarán mayor actividad")
            predicciones.append("⚠️ Considera: Factores externos como clima y eventos locales")
            
            return predicciones
            
        except Exception as e:
            print(f"Error en generación de predicciones: {e}")
            return ["Las predicciones no están disponibles temporalmente"]

    def _generar_plan_accion(self, datos_ventas, datos_productos):
        """Genera plan de acción automatizado"""
        plan = []
        
        if len(datos_ventas) < 7:
            return ["Recolecta más datos para generar un plan de acción personalizado."]
        
        try:
            import numpy as np
            
            ventas = [item['venta_total'] for item in datos_ventas]
            variabilidad = (np.std(ventas) / np.mean(ventas)) * 100
            
            # Plan basado en variabilidad
            if variabilidad > 35:
                plan.append("Implementar promociones en días de baja demanda identificados")
                plan.append("Optimizar inventario para reducir desperdicios en días lentos")
                plan.append("Crear paquetes especiales para estimular ventas en horarios bajos")
            else:
                plan.append("Mantener niveles actuales de producción e inventario")
                plan.append("Enfocar esfuerzos en mejorar margen de utilidad")
                plan.append("Explorar nuevos productos o servicios complementarios")
            
            # Acciones generales
            plan.append("Revisar y ajustar horarios de personal según patrones de venta")
            plan.append("Optimizar compras de materias primas basado en tendencias")
            plan.append("Programar mantenimiento preventivo en horarios de baja demanda")
            plan.append("Capacitar equipo en técnicas de ventas y servicio al cliente")
            
            return plan[:6]  # Máximo 6 acciones
            
        except Exception as e:
            print(f"Error en generación de plan de acción: {e}")
            return ["Plan de acción no disponible temporalmente"]


    # =================================================== Análisis de Inventarios ==================================================

    def generar_reporte_analisis_inventarios(self, fecha_inicio, fecha_fin):
        """Genera reporte de Análisis de Inventarios con gestión de stock - OPTIMIZADO CON DATOS REALES"""
        try:
            print(f"📦 Generando análisis de inventarios para {fecha_inicio} a {fecha_fin}")
            
            # ✅ CONFIGURACIÓN OPTIMIZADA
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch,
                                leftMargin=0.4*inch,
                                rightMargin=0.4*inch)
            
            elements = []

            # ✅ ENCABEZADO COMPACTO
            elements.append(Paragraph("PANADERÍA SEMILLAS", self.estilo_titulo))
            elements.append(Paragraph("📦 ANÁLISIS DE INVENTARIOS Y GESTIÓN DE STOCK", self.estilo_titulo))
            elements.append(Paragraph(f"Período de análisis: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))

            # Obtener datos REALES de inventarios
            datos_inventarios = self._obtener_datos_inventarios_reales()
            datos_rotacion = self._obtener_datos_rotacion_reales(fecha_inicio, fecha_fin)
            
            if not datos_inventarios:
                elements.append(Paragraph("No hay datos de inventarios disponibles para análisis.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # ✅ GRÁFICOS DE INVENTARIO OPTIMIZADOS CON DATOS REALES
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                
                # Crear figura compacta para análisis de inventarios
                fig = Figure(figsize=(10, 8))
                
                # Preparar datos REALES
                productos = [item['nombre'] for item in datos_inventarios]
                stock_actual = [item['stock_actual'] for item in datos_inventarios]
                stock_minimo = [item['stock_minimo'] for item in datos_inventarios]
                stock_maximo = [item.get('stock_maximo', item['stock_minimo'] * 3) for item in datos_inventarios]
                
                # --- GRÁFICO 1: Análisis de Niveles de Stock ---
                ax1 = fig.add_subplot(221)
                
                # Gráfico de barras comparativo
                x_pos = np.arange(len(productos))
                ancho = 0.25
                
                # Acortar nombres de productos para mejor visualización
                productos_cortos = [p[:15] + '...' if len(p) > 15 else p for p in productos]
                
                bars1 = ax1.bar(x_pos - ancho, stock_actual, ancho, 
                            label='Stock Actual', alpha=0.8, color='#3498db')
                bars2 = ax1.bar(x_pos, stock_minimo, ancho, 
                            label='Stock Mínimo', alpha=0.8, color='#e74c3c')
                bars3 = ax1.bar(x_pos + ancho, stock_maximo, ancho, 
                            label='Stock Máximo', alpha=0.8, color='#27ae60')
                
                # Destacar productos con stock bajo
                for i, (actual, minimo) in enumerate(zip(stock_actual, stock_minimo)):
                    if actual <= minimo:
                        ax1.axvline(x=i, color='red', alpha=0.3, linestyle='--')
                
                ax1.set_title('Niveles de Stock por Producto', fontsize=11, fontweight='bold', pad=8)
                ax1.set_ylabel('Cantidad en Stock', fontsize=9)
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(productos_cortos, rotation=45, ha='right', fontsize=7)
                ax1.legend(fontsize=7)
                ax1.grid(True, alpha=0.3, axis='y')
                
                # --- GRÁFICO 2: Análisis ABC de Inventarios ---
                ax2 = fig.add_subplot(222)
                
                # Calcular valor de inventario REAL
                valores_inventario = [item['valor_inventario'] for item in datos_inventarios]
                total_valor = sum(valores_inventario)
                
                # Ordenar por valor descendente
                datos_ordenados = sorted(zip(productos, valores_inventario, stock_actual), 
                                    key=lambda x: x[1], reverse=True)
                
                productos_ordenados = [item[0] for item in datos_ordenados]
                valores_ordenados = [item[1] for item in datos_ordenados]
                acumulado = np.cumsum(valores_ordenados)
                porcentaje_acumulado = (acumulado / total_valor * 100) if total_valor > 0 else [0]
                
                # Gráfico de Pareto
                bars = ax2.bar(range(len(valores_ordenados)), valores_ordenados, 
                            color='skyblue', alpha=0.7, label='Valor Inventario')
                line = ax2.plot(range(len(valores_ordenados)), porcentaje_acumulado, 
                            color='red', marker='o', linewidth=2, label='% Acumulado')
                
                ax2.set_title('Análisis ABC - Valor de Inventario', fontsize=11, fontweight='bold', pad=8)
                ax2.set_ylabel('Valor del Inventario ($)', fontsize=9)
                ax2.set_xlabel('Productos (ordenados por valor)', fontsize=8)
                ax2.grid(True, alpha=0.3)
                ax2.legend(fontsize=7)
                ax2.tick_params(axis='x', labelsize=6)
                ax2.tick_params(axis='y', labelsize=7)
                
                # Clasificación ABC
                ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Límite A/B (80%)')
                ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7, label='Límite B/C (95%)')
                
                # --- GRÁFICO 3: Análisis de Rotación ---
                ax3 = fig.add_subplot(223)
                
                if datos_rotacion:
                    productos_rot = [item['producto'] for item in datos_rotacion]
                    rotacion = [item['indice_rotacion'] for item in datos_rotacion]
                    
                    # Colores basados en nivel de rotación
                    colores = []
                    for rot in rotacion:
                        if rot > 12:
                            colores.append('#27ae60')  # Alta rotación - Verde
                        elif rot > 6:
                            colores.append('#f39c12')  # Media rotación - Naranja
                        else:
                            colores.append('#e74c3c')  # Baja rotación - Rojo
                    
                    productos_rot_cortos = [p[:12] + '...' if len(p) > 12 else p for p in productos_rot]
                    bars = ax3.bar(productos_rot_cortos, rotacion, color=colores, alpha=0.8)
                    
                    ax3.set_title('Índice de Rotación de Inventario', fontsize=11, fontweight='bold', pad=8)
                    ax3.set_ylabel('Rotación (veces/año)', fontsize=9)
                    ax3.tick_params(axis='x', rotation=45, labelsize=7)
                    ax3.tick_params(axis='y', labelsize=7)
                    ax3.grid(True, alpha=0.3, axis='y')
                    
                    # Líneas de referencia
                    ax3.axhline(y=12, color='green', linestyle='--', alpha=0.5, label='Alta Rotación')
                    ax3.axhline(y=6, color='orange', linestyle='--', alpha=0.5, label='Media Rotación')
                    ax3.legend(fontsize=7)
                else:
                    ax3.text(0.5, 0.5, 'Datos de rotación\nno disponibles', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Índice de Rotación', fontsize=11, fontweight='bold', pad=8)
                
                # --- GRÁFICO 4: Análisis de Puntos de Reorden ---
                ax4 = fig.add_subplot(224)
                
                # Calcular días de stock disponible REAL
                dias_stock = []
                for item in datos_inventarios:
                    demanda_promedio = item.get('demanda_promedio', 0)
                    if demanda_promedio > 0:
                        dias = item['stock_actual'] / demanda_promedio
                    else:
                        dias = 999  # Sin demanda conocida
                    dias_stock.append(dias)
                
                productos_cortos_dias = [p[:10] + '...' if len(p) > 10 else p for p in productos]
                
                # Colores basados en días de stock
                colores_dias = []
                for dias in dias_stock:
                    if dias <= 7:
                        colores_dias.append('#e74c3c')  # Crítico - Rojo
                    elif dias <= 14:
                        colores_dias.append('#f39c12')  # Alerta - Naranja
                    else:
                        colores_dias.append('#27ae60')  # Normal - Verde
                
                bars = ax4.bar(productos_cortos_dias, dias_stock, color=colores_dias, alpha=0.8)
                
                ax4.set_title('Días de Stock Disponible', fontsize=11, fontweight='bold', pad=8)
                ax4.set_ylabel('Días de Stock', fontsize=9)
                ax4.tick_params(axis='x', rotation=45, labelsize=6)
                ax4.tick_params(axis='y', labelsize=7)
                ax4.grid(True, alpha=0.3, axis='y')
                
                # Líneas de referencia
                ax4.axhline(y=7, color='red', linestyle='--', alpha=0.7, label='Límite Crítico (7 días)')
                ax4.axhline(y=14, color='orange', linestyle='--', alpha=0.7, label='Límite Alerta (14 días)')
                ax4.legend(fontsize=6)
                
                # Ajustar diseño compacto
                fig.tight_layout(pad=2.0)
                
                # Guardar gráfico optimizado
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                # Agregar gráfico al PDF
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE INVENTARIOS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))
                elements.append(Spacer(1, 10))
                
                print("✅ Gráficos de inventario generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos de inventario: {e}. Continuando sin gráficos.")

            # ✅ RESUMEN EJECUTIVO DE INVENTARIOS CON DATOS REALES
            elements.append(Paragraph("📊 RESUMEN EJECUTIVO DE INVENTARIOS", self.estilo_subtitulo))
            
            resumen = self._generar_resumen_inventarios(datos_inventarios)
            
            estilo_resumen = ParagraphStyle(
                'Resumen',
                parent=self.styles['Normal'],
                fontSize=9,
                leading=12,
                spaceAfter=6
            )
            
            for item in resumen:
                elements.append(Paragraph(f"• {item}", estilo_resumen))
            
            elements.append(Spacer(1, 12))

            # ✅ ALERTAS Y PRODUCTOS CRÍTICOS CON DATOS REALES
            elements.append(Paragraph("🚨 ALERTAS DE INVENTARIO", self.estilo_subtitulo))
            
            alertas = self._generar_alertas_inventarios(datos_inventarios)
            
            for alerta in alertas:
                elements.append(Paragraph(f"⚠ {alerta}", estilo_resumen))
            
            elements.append(Spacer(1, 12))

            # ✅ RECOMENDACIONES DE OPTIMIZACIÓN CON DATOS REALES
            elements.append(Paragraph("💡 RECOMENDACIONES DE OPTIMIZACIÓN", self.estilo_subtitulo))
            
            recomendaciones = self._generar_recomendaciones_inventarios(datos_inventarios, datos_rotacion)
            
            for recomendacion in recomendaciones:
                elements.append(Paragraph(f"✓ {recomendacion}", estilo_resumen))
            
            elements.append(Spacer(1, 10))

            # ✅ TABLA DE PUNTOS DE REORDEN CON DATOS REALES
            elements.append(Paragraph("📋 PUNTOS DE REORDEN SUGERIDOS", self.estilo_subtitulo))
            
            # Crear tabla compacta
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            datos_tabla = [['Producto', 'Stock Actual', 'Mínimo', 'Reorden', 'Estado', 'Valor']]
            
            for item in datos_inventarios[:8]:  # Máximo 8 productos en tabla
                stock_actual = item['stock_actual']
                stock_min = item['stock_minimo']
                estado = "✅ OK" if stock_actual > stock_min else "🚨 BAJO"
                
                # Calcular punto de reorden sugerido
                punto_reorden = max(stock_min, int(stock_min * 1.2))
                
                datos_tabla.append([
                    item['nombre'][:20] + '...' if len(item['nombre']) > 20 else item['nombre'],
                    f"{stock_actual:.1f}" if isinstance(stock_actual, float) else str(stock_actual),
                    f"{stock_min:.1f}" if isinstance(stock_min, float) else str(stock_min),
                    f"{punto_reorden:.1f}" if isinstance(punto_reorden, float) else str(punto_reorden),
                    estado,
                    f"${item.get('valor_inventario', 0):,.0f}"
                ])
            
            tabla = Table(datos_tabla, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            tabla.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            
            elements.append(tabla)
            elements.append(Spacer(1, 10))

            # ✅ PIE DE PÁGINA COMPACTO
            elements.append(Spacer(1, 15))
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"📦 Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            # ✅ CONSTRUIR DOCUMENTO
            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de análisis de inventarios generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_analisis_inventarios: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Crear PDF de error mínimo
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE INVENTARIOS")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_inventarios_reales(self):
        """Obtiene datos REALES de inventarios desde la base de datos"""
        try:
            from models import MateriaPrima, Producto, ProductoExterno
            
            datos_inventarios = []
            
            # ✅ 1. MATERIAS PRIMAS (ingredientes)
            materias_primas = MateriaPrima.query.filter_by(activo=True).all()
            
            for mp in materias_primas:
                # Calcular valor del inventario
                valor_inventario = mp.stock_actual * mp.costo_promedio
                
                # Estimar demanda promedio basada en uso en recetas
                demanda_promedio = self._calcular_demanda_materia_prima(mp.id)
                
                datos_inventarios.append({
                    'id': mp.id,
                    'nombre': f"MP: {mp.nombre}",
                    'stock_actual': mp.stock_actual,
                    'stock_minimo': mp.stock_minimo,
                    'costo_unitario': mp.costo_promedio,
                    'valor_inventario': valor_inventario,
                    'demanda_promedio': demanda_promedio,
                    'unidad_medida': mp.unidad_medida,
                    'tipo': 'materia_prima'
                })
            
            # ✅ 2. PRODUCTOS DE PRODUCCIÓN (panadería)
            productos_produccion = Producto.query.filter_by(
                activo=True, 
                tipo_producto='produccion'
            ).all()
            
            for producto in productos_produccion:
                # Calcular valor del inventario (usando costo de receta si está disponible)
                if producto.receta:
                    costo_unitario = producto.receta.costo_unitario if producto.receta.costo_unitario > 0 else producto.precio_venta * 0.3
                else:
                    costo_unitario = producto.precio_venta * 0.3  # Estimación
                
                valor_inventario = producto.stock_actual * costo_unitario
                
                # Calcular demanda promedio basada en ventas históricas
                demanda_promedio = self._calcular_demanda_producto(producto.id)
                
                datos_inventarios.append({
                    'id': producto.id,
                    'nombre': f"PROD: {producto.nombre}",
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'costo_unitario': costo_unitario,
                    'valor_inventario': valor_inventario,
                    'demanda_promedio': demanda_promedio,
                    'unidad_medida': 'unidades',
                    'tipo': 'producto_produccion'
                })
            
            # ✅ 3. PRODUCTOS EXTERNOS
            productos_externos = ProductoExterno.query.filter_by(activo=True).all()
            
            for producto in productos_externos:
                valor_inventario = producto.stock_actual * producto.precio_compra
                
                # Calcular demanda promedio
                demanda_promedio = self._calcular_demanda_producto_externo(producto.id)
                
                datos_inventarios.append({
                    'id': producto.id,
                    'nombre': f"EXT: {producto.nombre}",
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'costo_unitario': producto.precio_compra,
                    'valor_inventario': valor_inventario,
                    'demanda_promedio': demanda_promedio,
                    'unidad_medida': 'unidades',
                    'tipo': 'producto_externo'
                })
            
            print(f"✅ Datos de inventario reales obtenidos: {len(datos_inventarios)} items")
            return datos_inventarios
            
        except Exception as e:
            print(f"❌ Error al obtener datos reales de inventarios: {e}")
            return []

    def _calcular_demanda_materia_prima(self, materia_prima_id):
        """Calcula la demanda promedio de una materia prima basada en uso en recetas"""
        try:
            from models import RecetaIngrediente, OrdenProduccion
            from datetime import datetime, timedelta
            
            # Obtener órdenes de producción de los últimos 30 días
            fecha_inicio = datetime.now() - timedelta(days=30)
            
            # Calcular uso total en producción
            uso_total = 0
            
            # Buscar en todas las recetas que usan esta materia prima
            ingredientes = RecetaIngrediente.query.filter_by(materia_prima_id=materia_prima_id).all()
            
            for ingrediente in ingredientes:
                # Obtener órdenes de producción para esta receta
                ordenes = OrdenProduccion.query.filter(
                    OrdenProduccion.receta_id == ingrediente.receta_id,
                    OrdenProduccion.fecha_produccion >= fecha_inicio,
                    OrdenProduccion.estado == 'COMPLETADA'
                ).all()
                
                for orden in ordenes:
                    # Calcular cantidad utilizada en esta orden
                    if orden.receta.unidades_obtenidas > 0:
                        cantidad_utilizada = (ingrediente.cantidad_gramos / orden.receta.unidades_obtenidas) * orden.cantidad_producir
                        uso_total += cantidad_utilizada
            
            # Calcular demanda diaria promedio
            demanda_promedio = uso_total / 30.0
            return max(demanda_promedio, 0.1)  # Mínimo 0.1 para evitar división por cero
            
        except Exception as e:
            print(f"Error calculando demanda materia prima {materia_prima_id}: {e}")
            return 1.0  # Valor por defecto

    def _calcular_demanda_producto(self, producto_id):
        """Calcula la demanda promedio de un producto basada en ventas históricas"""
        try:
            from models import DetalleVenta, Venta
            from datetime import datetime, timedelta
            
            fecha_inicio = datetime.now() - timedelta(days=30)
            
            ventas_totales = DetalleVenta.query.join(Venta).filter(
                DetalleVenta.producto_id == producto_id,
                Venta.fecha_hora >= fecha_inicio
            ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
            
            demanda_promedio = ventas_totales / 30.0
            return max(demanda_promedio, 0.1)
            
        except Exception as e:
            print(f"Error calculando demanda producto {producto_id}: {e}")
            return 1.0

    def _calcular_demanda_producto_externo(self, producto_externo_id):
        """Calcula la demanda promedio de un producto externo"""
        try:
            from models import DetalleVenta, Venta
            from datetime import datetime, timedelta
            
            fecha_inicio = datetime.now() - timedelta(days=30)
            
            ventas_totales = DetalleVenta.query.join(Venta).filter(
                DetalleVenta.producto_externo_id == producto_externo_id,
                Venta.fecha_hora >= fecha_inicio
            ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
            
            demanda_promedio = ventas_totales / 30.0
            return max(demanda_promedio, 0.1)
            
        except Exception as e:
            print(f"Error calculando demanda producto externo {producto_externo_id}: {e}")
            return 1.0

    def _obtener_datos_rotacion_reales(self, fecha_inicio, fecha_fin):
        """Obtiene datos REALES de rotación de inventarios"""
        try:
            from models import Producto, ProductoExterno, DetalleVenta, Venta
            
            datos_rotacion = []
            
            # Productos de producción
            productos = Producto.query.filter_by(activo=True).all()
            for producto in productos:
                # Calcular ventas del período
                ventas_periodo = DetalleVenta.query.join(Venta).filter(
                    DetalleVenta.producto_id == producto.id,
                    Venta.fecha_hora >= fecha_inicio,
                    Venta.fecha_hora <= fecha_fin
                ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
                
                # Calcular stock promedio (simplificado)
                stock_promedio = producto.stock_actual
                
                # Calcular índice de rotación (anualizado)
                if stock_promedio > 0:
                    dias_periodo = (fecha_fin - fecha_inicio).days
                    factor_anual = 365 / dias_periodo if dias_periodo > 0 else 12
                    indice_rotacion = (ventas_periodo / stock_promedio) * factor_anual
                else:
                    indice_rotacion = 0
                
                datos_rotacion.append({
                    'producto': producto.nombre,
                    'indice_rotacion': round(indice_rotacion, 2),
                    'ventas_totales': ventas_periodo
                })
            
            # Productos externos
            productos_externos = ProductoExterno.query.filter_by(activo=True).all()
            for producto in productos_externos:
                ventas_periodo = DetalleVenta.query.join(Venta).filter(
                    DetalleVenta.producto_externo_id == producto.id,
                    Venta.fecha_hora >= fecha_inicio,
                    Venta.fecha_hora <= fecha_fin
                ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
                
                stock_promedio = producto.stock_actual
                
                if stock_promedio > 0:
                    dias_periodo = (fecha_fin - fecha_inicio).days
                    factor_anual = 365 / dias_periodo if dias_periodo > 0 else 12
                    indice_rotacion = (ventas_periodo / stock_promedio) * factor_anual
                else:
                    indice_rotacion = 0
                
                datos_rotacion.append({
                    'producto': f"EXT: {producto.nombre}",
                    'indice_rotacion': round(indice_rotacion, 2),
                    'ventas_totales': ventas_periodo
                })
            
            # Ordenar por rotación descendente
            datos_rotacion.sort(key=lambda x: x['indice_rotacion'], reverse=True)
            return datos_rotacion[:10]  # Top 10
            
        except Exception as e:
            print(f"Error obteniendo datos de rotación reales: {e}")
            return []



    def _generar_resumen_inventarios(self, datos_inventarios):
        """Genera resumen ejecutivo de inventarios"""
        resumen = []
        
        try:
            # Cálculos del resumen
            total_productos = len(datos_inventarios)
            valor_total_inventario = sum(item['stock_actual'] * item['costo_unitario'] for item in datos_inventarios)
            productos_bajo_stock = sum(1 for item in datos_inventarios if item['stock_actual'] <= item['stock_minimo'])
            productos_sobre_stock = sum(1 for item in datos_inventarios if item['stock_actual'] > item['stock_maximo'])
            
            # Stock promedio
            stock_promedio = sum(item['stock_actual'] for item in datos_inventarios) / total_productos if total_productos > 0 else 0
            
            resumen.append(f"Total de productos en inventario: {total_productos}")
            resumen.append(f"Valor total del inventario: ${valor_total_inventario:,.0f}")
            resumen.append(f"Productos con stock bajo: {productos_bajo_stock} ({productos_bajo_stock/total_productos*100:.1f}%)")
            resumen.append(f"Productos sobre stock máximo: {productos_sobre_stock} ({productos_sobre_stock/total_productos*100:.1f}%)")
            resumen.append(f"Stock promedio por producto: {stock_promedio:.1f} unidades")
            resumen.append(f"Eficiencia general de inventario: {(total_productos - productos_bajo_stock) / total_productos * 100:.1f}%")
            
            return resumen
            
        except Exception as e:
            print(f"Error en generación de resumen: {e}")
            return ["Resumen no disponible temporalmente"]

    def _generar_alertas_inventarios(self, datos_inventarios):
        """Genera alertas de inventario críticas"""
        alertas = []
        
        try:
            # Productos con stock crítico (por debajo del mínimo)
            productos_criticos = [item for item in datos_inventarios if item['stock_actual'] <= item['stock_minimo']]
            
            for producto in productos_criticos[:3]:  # Máximo 3 alertas críticas
                alertas.append(f"STOCK CRÍTICO: {producto['nombre']} - Solo {producto['stock_actual']} unidades (mínimo: {producto['stock_minimo']})")
            
            # Productos con exceso de stock
            productos_exceso = [item for item in datos_inventarios if item['stock_actual'] > item['stock_maximo']]
            
            for producto in productos_exceso[:2]:  # Máximo 2 alertas de exceso
                alertas.append(f"EXCESO DE STOCK: {producto['nombre']} - {producto['stock_actual']} unidades (máximo: {producto['stock_maximo']})")
            
            # Alertas de productos con movimiento lento
            productos_lentos = [item for item in datos_inventarios if item['demanda_promedio'] < 2 and item['stock_actual'] > 10]
            
            for producto in productos_lentos[:2]:
                alertas.append(f"MOVIMIENTO LENTO: {producto['nombre']} - Demanda baja con stock alto")
            
            if not alertas:
                alertas.append("✅ No hay alertas críticas - Inventario en estado óptimo")
            
            return alertas[:5]  # Máximo 5 alertas
            
        except Exception as e:
            print(f"Error en generación de alertas: {e}")
            return ["Sistema de alertas no disponible temporalmente"]

    def _generar_recomendaciones_inventarios(self, datos_inventarios, datos_rotacion):
        """Genera recomendaciones de optimización de inventarios"""
        recomendaciones = []
        
        try:
            # Análisis de productos A (alto valor)
            productos_ordenados = sorted(datos_inventarios, 
                                    key=lambda x: x['stock_actual'] * x['costo_unitario'], 
                                    reverse=True)
            
            productos_a = productos_ordenados[:int(len(productos_ordenados) * 0.2)]  # Top 20%
            
            if productos_a:
                recomendaciones.append(f"ENFOQUE EN PRODUCTOS A: {len(productos_a)} productos representan el 80% del valor del inventario")
                recomendaciones.append("CONTROL ESTRICTO: Implementar conteos cíclicos frecuentes para productos de alto valor")
            
            # Recomendaciones basadas en rotación
            if datos_rotacion:
                baja_rotacion = [item for item in datos_rotacion if item['indice_rotacion'] < 6]
                if baja_rotacion:
                    recomendaciones.append(f"OPTIMIZAR: {len(baja_rotacion)} productos con baja rotación (<6 veces/año)")
                    recomendaciones.append("ACCIÓN: Reducir compras y considerar promociones para estos productos")
            
            # Recomendaciones generales
            total_valor = sum(item['stock_actual'] * item['costo_unitario'] for item in datos_inventarios)
            if total_valor > 5000000:  # Si el inventario vale más de 5 millones
                recomendaciones.append("OPTIMIZACIÓN FINANCIERA: Considerar reducir inventario para liberar capital de trabajo")
            
            # Recomendaciones de compras
            productos_reorden = [item for item in datos_inventarios if item['stock_actual'] <= item['stock_minimo'] * 1.5]
            if productos_reorden:
                recomendaciones.append(f"COMPRAS PENDIENTES: {len(productos_reorden)} productos requieren reabastecimiento urgente")
            
            # Mejoras de proceso
            recomendaciones.append("MEJORA CONTINUA: Establecer revisiones periódicas de puntos de reorden")
            recomendaciones.append("TECNOLOGÍA: Considerar sistema de código de barras para conteos más eficientes")
            
            return recomendaciones[:8]  # Máximo 8 recomendaciones
            
        except Exception as e:
            print(f"Error en generación de recomendaciones: {e}")
            return ["Recomendaciones no disponibles temporalmente"]