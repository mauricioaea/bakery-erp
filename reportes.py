# reportes.py - VERSIÓN 100% MULTI-TENANT
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
from models import db, RegistroDiario, PagoIndividual, SaldoBanco, Venta, Producto, Proveedor, DepositoBancario
from sqlalchemy import func, extract

# Importación para multi-tenant
from flask_login import current_user

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
    
    def generar_reporte_estado_resultados(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Estado de Resultados (Pérdidas y Ganancias) - CON FILTRO MULTI-TENANT"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # Encabezado
        elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
        elements.append(Paragraph("ESTADO DE RESULTADOS", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # ✅ FILTRAR POR TENANT
        ingresos = self._obtener_ingresos_periodo(panaderia_id, fecha_inicio, fecha_fin)
        gastos = self._obtener_gastos_periodo(panaderia_id, fecha_inicio, fecha_fin)
        
        total_ingresos = sum(ingresos.values()) if ingresos else 0
        total_gastos = sum(gastos.values()) if gastos else 0
        
        if total_ingresos == 0 and total_gastos == 0:
            elements.append(Paragraph("📊 SIN DATOS PARA EL PERÍODO", self.estilo_subtitulo))
            elements.append(Paragraph("No se encontraron registros de ingresos o gastos para las fechas seleccionadas.", self.styles['Normal']))
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💡 Recomendaciones:", self.styles['Normal']))
            elements.append(Paragraph("• Verifique que las fechas sean correctas", self.styles['Normal']))
            elements.append(Paragraph("• Confirme que existan ventas registradas en el período", self.styles['Normal']))
            elements.append(Paragraph("• Verifique los cierres de caja del período", self.styles['Normal']))
            
            elements.append(Spacer(1, 30))
            elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
        
        # Tabla de Ingresos
        elements.append(Paragraph("INGRESOS", self.estilo_subtitulo))
        data_ingresos = [['Concepto', 'Monto']]
        total_ingresos = 0
        
        for concepto, monto in ingresos.items():
            if monto > 0:
                data_ingresos.append([concepto, f"${monto:,.0f}"])
                total_ingresos += monto
        
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
                categoria_formateada = categoria.replace('_', ' ').title()
                data_gastos.append([categoria_formateada, f"${monto:,.0f}"])
                total_gastos += monto
        
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
        
        # Análisis de Rentabilidad
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("ANÁLISIS DE RENTABILIDAD", self.estilo_subtitulo))
        
        if total_ingresos > 0:
            margen_ganancia = (resultado_neto / total_ingresos * 100)
            relacion_gastos_ingresos = (total_gastos / total_ingresos * 100)
        else:
            margen_ganancia = 0
            relacion_gastos_ingresos = 0
        
        analisis_texto = f"""
        <b>Margen de Ganancia Neto:</b> {margen_ganancia:.1f}%<br/>
        <b>Relación Gastos/Ingresos:</b> {relacion_gastos_ingresos:.1f}%<br/>
        <b>Rentabilidad:</b> {'<font color="green">POSITIVA</font>' if resultado_neto >= 0 else '<font color="red">NEGATIVA</font>'}<br/>
        <b>Días del período:</b> {(fecha_fin - fecha_inicio).days + 1} días<br/>
        <b>Ingresos promedio por día:</b> ${(total_ingresos / ((fecha_fin - fecha_inicio).days + 1)):,.0f}
        """
        elements.append(Paragraph(analisis_texto, self.styles['Normal']))
        
        # Recomendaciones
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("RECOMENDACIONES", self.estilo_subtitulo))
        
        recomendaciones = []
        if resultado_neto < 0:
            recomendaciones.append("🔴 <b>Alerta de Pérdidas:</b> Se recomienda revisar gastos operativos")
            if total_gastos > total_ingresos * 2:
                recomendaciones.append("🔴 <b>Gastos Elevados:</b> Considerar optimización de costos")
        elif margen_ganancia > 20:
            recomendaciones.append("🟢 <b>Alta Rentabilidad:</b> Buen desempeño financiero")
        elif margen_ganancia > 10:
            recomendaciones.append("🟡 <b>Rentabilidad Moderada:</b> Oportunidad de mejora")
        else:
            recomendaciones.append("🟡 <b>Rentabilidad Baja:</b> Evaluar estrategias de crecimiento")
        
        if not recomendaciones:
            recomendaciones.append("⚪ <b>Estable:</b> Mantener estrategias actuales")
        
        for recomendacion in recomendaciones:
            elements.append(Paragraph(recomendacion, self.styles['Normal']))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_flujo_caja(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Flujo de Caja - CON FILTRO MULTI-TENANT"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []

        elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
        elements.append(Paragraph("REPORTE DE FLUJO DE CAJA", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 20))

        # ✅ FILTRAR POR TENANT
        flujo_data = self._obtener_flujo_caja_periodo(panaderia_id, fecha_inicio, fecha_fin)

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
    
    def _obtener_ingresos_periodo(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene ingresos combinando ventas directas y registros diarios - CON FILTRO MULTI-TENANT"""
        try:
            from datetime import datetime
            
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            print(f"🔍 BUSCANDO INGRESOS ENTRE: {fecha_inicio} Y {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            # ✅ FILTRAR POR TENANT
            registros_cierre = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin),
                RegistroDiario.panaderia_id == panaderia_id
            ).all()
            
            print(f"📊 REGISTROS DE CIERRE ENCONTRADOS: {len(registros_cierre)}")
            
            total_efectivo_cierre = 0
            total_transferencias_cierre = 0
            
            for registro in registros_cierre:
                efectivo = registro.efectivo or 0
                transferencias = registro.transferencias or 0
                
                total_efectivo_cierre += efectivo
                total_transferencias_cierre += transferencias
            
            total_cierre = total_efectivo_cierre + total_transferencias_cierre
            
            # ✅ FILTRAR VENTAS POR TENANT
            ventas_normales = Venta.query.filter(
                Venta.fecha_hora.between(fecha_inicio, fecha_fin),
                Venta.es_donacion == False,
                Venta.panaderia_id == panaderia_id
            ).all()
            
            ventas_efectivo = 0
            ventas_transferencia = 0
            total_ventas_directas = 0
            
            for venta in ventas_normales:
                total_ventas_directas += venta.total or 0
                if venta.metodo_pago == 'efectivo':
                    ventas_efectivo += venta.total or 0
                elif venta.metodo_pago == 'transferencia':
                    ventas_transferencia += venta.total or 0
            
            # ✅ ESTRATEGIA: Priorizar cierres de caja
            if total_cierre > 0:
                efectivo_final = total_efectivo_cierre
                transferencias_final = total_transferencias_cierre
                total_ventas_final = total_cierre
                fuente_datos = "Cierres de Caja"
            else:
                efectivo_final = ventas_efectivo
                transferencias_final = ventas_transferencia
                total_ventas_final = total_ventas_directas
                fuente_datos = "Ventas Directas"
            
            # ✅ FILTRAR DONACIONES POR TENANT
            ventas_donaciones = Venta.query.filter(
                Venta.fecha_hora.between(fecha_inicio, fecha_fin),
                Venta.es_donacion == True,
                Venta.panaderia_id == panaderia_id
            ).all()
            
            total_donaciones = sum(v.total for v in ventas_donaciones) if ventas_donaciones else 0
            
            ingresos = {
            'Ventas Normales': total_ventas_final,
            }
            
            # Solo incluir donaciones si hay alguna
            if total_donaciones > 0:
                ingresos['Donaciones'] = total_donaciones
            
            print(f"✅ INGRESOS CALCULADOS EXITOSAMENTE:")
            for concepto, monto in ingresos.items():
                print(f"   📈 {concepto}: ${monto:,}")
            
            return ingresos
            
        except Exception as e:
            print(f"⚠️ Error al obtener ingresos: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'Ventas Normales': 0,
                'Efectivo': 0,
                'Transferencias': 0,
                'Donaciones': 0
            }
    
    def _obtener_gastos_periodo(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene gastos agrupados por categoría - CON FILTRO MULTI-TENANT"""
        try:
            # ✅ FILTRAR POR TENANT
            pagos = PagoIndividual.query.filter(
                PagoIndividual.fecha_pago.between(fecha_inicio, fecha_fin),
                PagoIndividual.panaderia_id == panaderia_id
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
    
    def _obtener_flujo_caja_periodo(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene datos para flujo de caja diario - CON FILTRO MULTI-TENANT"""
        try:
            # ✅ FILTRAR POR TENANT
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin),
                RegistroDiario.panaderia_id == panaderia_id
            ).order_by(RegistroDiario.fecha).all()
            
            flujo_data = []
            for registro in registros:
                ingresos = (registro.efectivo or 0) + (registro.transferencias or 0)
                gastos = registro.total_egresos or 0
                flujo_data.append((registro.fecha, ingresos, gastos))
            
            return flujo_data
        except Exception as e:
            print(f"Error al obtener flujo de caja: {e}")
            return []
        
    #=======================================libro contable=================================================
    def generar_reporte_libro_diario(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Libro Mayor de Caja - CON FILTRO MULTI-TENANT"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []

        elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
        elements.append(Paragraph("LIBRO MAYOR DE CAJA", self.estilo_titulo))
        elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 15))

        # ✅ FILTRAR POR TENANT
        movimientos = self._obtener_movimientos_periodo(panaderia_id, fecha_inicio, fecha_fin)

        if not movimientos:
            elements.append(Paragraph("No hay movimientos de caja para el período seleccionado.", self.styles['Normal']))
        else:
            data = [['Fecha', 'Concepto', 'Referencia', 'Ingresos', 'Egresos', 'Saldo']]
            
            saldo_acumulado = 0
            total_ingresos = 0
            total_egresos = 0

            for movimiento in movimientos:
                fecha, concepto, referencia, ingresos, egresos, tipo = movimiento
                
                saldo_acumulado += ingresos - egresos
                total_ingresos += ingresos
                total_egresos += egresos

                data.append([
                    fecha.strftime('%d/%m/%Y'),
                    concepto,
                    referencia or '-',
                    f"${ingresos:,.0f}" if ingresos > 0 else "$0",
                    f"${egresos:,.0f}" if egresos > 0 else "$0",
                    f"${saldo_acumulado:,.0f}"
                ])

            data.append([
                'TOTALES',
                '',
                '',
                f"${total_ingresos:,.0f}",
                f"${total_egresos:,.0f}",
                f"${saldo_acumulado:,.0f}"
            ])

            tabla = Table(data, colWidths=[0.8*inch, 2.2*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.2*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 8),
            ]))
            
            elements.append(tabla)
            elements.append(Spacer(1, 20))

            elements.append(Paragraph("RESUMEN DE CAJA", self.estilo_subtitulo))
            
            saldo_caja = total_ingresos - total_egresos
            
            resumen_texto = f"""
            <b>Total Ingresos:</b> ${total_ingresos:,.0f}<br/>
            <b>Total Egresos:</b> ${total_egresos:,.0f}<br/>
            <b>Saldo de Caja:</b> ${saldo_caja:,.0f}<br/>
            <b>Total Movimientos:</b> {len(movimientos)}
            """
            elements.append(Paragraph(resumen_texto, self.styles['Normal']))

        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray)))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _obtener_movimientos_periodo(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene movimientos de caja (ingresos y egresos) para el libro mayor de caja - CON FILTRO MULTI-TENANT"""
        try:
            movimientos = []
            
            from datetime import datetime
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            print(f"🔍 BUSCANDO MOVIMIENTOS DE CAJA ENTRE: {fecha_inicio} Y {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            # ✅ FILTRAR POR TENANT
            registros = RegistroDiario.query.filter(
                RegistroDiario.fecha.between(fecha_inicio, fecha_fin),
                RegistroDiario.panaderia_id == panaderia_id
            ).order_by(RegistroDiario.fecha).all()
            
            print(f"📊 REGISTROS DE CIERRE ENCONTRADOS: {len(registros)}")
            
            for registro in registros:
                if registro.efectivo and registro.efectivo > 0:
                    movimientos.append((
                        registro.fecha,
                        "VENTAS EN EFECTIVO",
                        f"CIERRE {registro.fecha}",
                        registro.efectivo,
                        0,
                        'INGRESO'
                    ))
                    print(f"   💰 INGRESO EFECTIVO: ${registro.efectivo:,}")
                
                if registro.transferencias and registro.transferencias > 0:
                    movimientos.append((
                        registro.fecha,
                        "TRANSFERENCIAS RECIBIDAS",
                        f"CIERRE {registro.fecha}",
                        registro.transferencias,
                        0,
                        'INGRESO'
                    ))
                    print(f"   💰 INGRESO TRANSFERENCIA: ${registro.transferencias:,}")
                
                
            
            # ✅ FILTRAR PAGOS POR TENANT
            pagos = PagoIndividual.query.filter(
                PagoIndividual.fecha_pago.between(fecha_inicio, fecha_fin),
                PagoIndividual.panaderia_id == panaderia_id
            ).order_by(PagoIndividual.fecha_pago).all()
            
            print(f"📊 PAGOS ENCONTRADOS: {len(pagos)}")
            
            for pago in pagos:
                categoria_formateada = pago.categoria.replace('_', ' ').title()
                
                movimientos.append((
                    pago.fecha_pago,
                    f"PAGO - {categoria_formateada}",
                    pago.referencia or pago.numero_factura or f"PAGO#{pago.id}",
                    0,
                    pago.monto,
                    'EGRESO'
                ))
                print(f"   💸 EGRESO {categoria_formateada}: ${pago.monto:,}")
            
            movimientos.sort(key=lambda x: x[0])
            
            print(f"✅ TOTAL MOVIMIENTOS DE CAJA GENERADOS: {len(movimientos)}")
            
            total_ingresos = sum(m[3] for m in movimientos)
            total_egresos = sum(m[4] for m in movimientos)
            saldo_caja = total_ingresos - total_egresos
            
            print(f"📊 TOTAL INGRESOS: ${total_ingresos:,}")
            print(f"📊 TOTAL EGRESOS: ${total_egresos:,}") 
            print(f"📊 SALDO DE CAJA: ${saldo_caja:,}")
            
            return movimientos
            
        except Exception as e:
            print(f"❌ ERROR al obtener movimientos de caja: {e}")
            import traceback
            traceback.print_exc()
            return []

    #==========================================Conciliacion Bancaria=========================================================
    def generar_reporte_conciliacion_bancaria(self, fecha_corte, saldo_extracto):
        """Genera reporte de Conciliación Bancaria - CORREGIDO MULTI-TENANT"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            elements = []

            # Encabezado
            elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
            elements.append(Paragraph("CONCILIACIÓN BANCARIA", self.estilo_titulo))
            elements.append(Paragraph(f"Fecha de Corte: {fecha_corte}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # Obtener saldo del sistema - ✅ CORREGIDO: Añadido filtro panaderia_id
            saldo_sistema_obj = SaldoBanco.query.filter(
                SaldoBanco.fecha_actualizacion <= fecha_corte,
                SaldoBanco.panaderia_id == current_user.panaderia_id  # ✅ NUEVO FILTRO MULTI-TENANT
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
            <b>Preparado por:</b> Sistema de Gestión Panadería-POS
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
        """Obtiene depósitos bancarios en tránsito (no conciliados) - ACTUALIZADO CON NUEVO MODELO"""
        try:
            # Buscar depósitos no conciliados hasta la fecha de corte
            depositos = DepositoBancario.query.filter(
                DepositoBancario.fecha_deposito <= fecha_corte,
                DepositoBancario.estado == 'REGISTRADO',
                DepositoBancario.panaderia_id == current_user.panaderia_id
            ).order_by(DepositoBancario.fecha_deposito).all()
            
            depositos_lista = []
            for deposito in depositos:
                # Determinar descripción automática si no hay
                descripcion = deposito.descripcion
                if not descripcion:
                    descripcion = f"Depósito {deposito.metodo_deposito or 'bancario'}"
                    if deposito.cuenta_bancaria:
                        descripcion += f" - Cuenta: {deposito.cuenta_bancaria}"
                
                depositos_lista.append({
                    'id': deposito.id,
                    'fecha': deposito.fecha_deposito,
                    'descripcion': descripcion,
                    'referencia': deposito.referencia or f'DEP#{deposito.id}',
                    'monto': deposito.monto,
                    'cuenta_bancaria': deposito.cuenta_bancaria,
                    'metodo_deposito': deposito.metodo_deposito,
                    'estado': deposito.estado
                })
            
            print(f"📊 Depósitos pendientes encontrados: {len(depositos_lista)}")
            return depositos_lista
            
        except Exception as e:
            print(f"❌ Error al obtener depósitos pendientes: {e}")
            return []

    def _obtener_cheques_pendientes(self, fecha_corte):
        """Obtiene cheques pendientes de cobro"""
        # Por ahora retornar lista vacía - puedes expandir esto cuando implementes módulo de cheques
        return []

    def _obtener_otros_ajustes(self, fecha_corte):
        """Obtiene otros ajustes para conciliación"""
        # Por ahora retornar lista vacía - puedes expandir esto
        return []
    
    
        # ========================================== FUNCIONES PARA DEPÓSITOS BANCARIOS ===========================================

    def registrar_deposito_automatico(self, fecha, monto_efectivo, descripcion=None):
        """Registra automáticamente un depósito bancario basado en cierre de caja - MULTI-TENANT"""
        try:
            # Verificar si ya existe un depósito para esta fecha
            deposito_existente = DepositoBancario.query.filter(
                DepositoBancario.fecha_deposito == fecha,
                DepositoBancario.panaderia_id == current_user.panaderia_id,
                DepositoBancario.metodo_deposito == 'efectivo'
            ).first()
            
            if deposito_existente:
                print(f"ℹ️ Depósito para {fecha} ya existe. Actualizando monto...")
                deposito_existente.monto = monto_efectivo
                deposito_existente.descripcion = descripcion or f"Depósito automático de cierre {fecha}"
                deposito_existente.fecha_actualizacion = datetime.utcnow()
                db.session.commit()
                return deposito_existente
            
            # Crear nuevo depósito
            nuevo_deposito = DepositoBancario(
                panaderia_id=current_user.panaderia_id,
                fecha_deposito=fecha,
                monto=monto_efectivo,
                descripcion=descripcion or f"Depósito automático de cierre {fecha}",
                referencia=f"AUTO-{fecha.strftime('%Y%m%d')}",
                cuenta_bancaria="Cuenta Principal",  # Esto se debería configurar
                metodo_deposito='efectivo',
                estado='REGISTRADO'
            )
            
            db.session.add(nuevo_deposito)
            db.session.commit()
            
            print(f"✅ Depósito automático registrado: ${monto_efectivo:,.0f} para {fecha}")
            return nuevo_deposito
            
        except Exception as e:
            print(f"❌ Error al registrar depósito automático: {e}")
            db.session.rollback()
            return None

    def obtener_depositos_por_rango(self, fecha_inicio, fecha_fin):
        """Obtiene todos los depósitos en un rango de fechas - MULTI-TENANT"""
        try:
            depositos = DepositoBancario.query.filter(
                DepositoBancario.fecha_deposito.between(fecha_inicio, fecha_fin),
                DepositoBancario.panaderia_id == current_user.panaderia_id
            ).order_by(DepositoBancario.fecha_deposito.desc()).all()
            
            return depositos
            
        except Exception as e:
            print(f"❌ Error al obtener depósitos por rango: {e}")
            return []

    def conciliar_deposito(self, deposito_id):
        """Marca un depósito como conciliado - MULTI-TENANT"""
        try:
            deposito = DepositoBancario.query.filter(
                DepositoBancario.id == deposito_id,
                DepositoBancario.panaderia_id == current_user.panaderia_id
            ).first()
            
            if not deposito:
                print(f"❌ Depósito {deposito_id} no encontrado")
                return False
            
            deposito.estado = 'CONCILIADO'
            deposito.fecha_conciliacion = datetime.utcnow().date()
            db.session.commit()
            
            print(f"✅ Depósito {deposito_id} conciliado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al conciliar depósito: {e}")
            db.session.rollback()
            return False
    
    
    
#====================================== Análisis de Gastos por Categoría========================================================
    def generar_reporte_analisis_gastos(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Análisis de Gastos por Categoría CON GRÁFICOS - CON FILTRO MULTI-TENANT"""
        try:
            print(f"🎯 Generando análisis de gastos para {fecha_inicio} a {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            elements = []

            # Encabezado
            elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
            elements.append(Paragraph("ANÁLISIS DE GASTOS POR CATEGORÍA", self.estilo_titulo))
            elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # ✅ FILTRAR POR TENANT
            gastos_por_categoria = self._obtener_gastos_por_categoria(panaderia_id, fecha_inicio, fecha_fin)
            
            if not gastos_por_categoria:
                elements.append(Paragraph("No hay datos de gastos para el período seleccionado.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            total_gastos = sum(gastos_por_categoria.values())
            categorias_ordenadas = sorted(gastos_por_categoria.items(), key=lambda x: x[1], reverse=True)

            # Gráficos
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                
                fig = Figure(figsize=(10, 8))
                ax1 = fig.add_subplot(211)
                
                if len(categorias_ordenadas) > 6:
                    top_categorias = categorias_ordenadas[:6]
                    otros_monto = sum(monto for _, monto in categorias_ordenadas[6:])
                    labels = [cat[0].replace('_', ' ').title() for cat in top_categorias] + ['Otros']
                    valores = [cat[1] for cat in top_categorias] + [otros_monto]
                    explode = [0.05] * len(top_categorias) + [0]
                else:
                    labels = [cat[0].replace('_', ' ').title() for cat in categorias_ordenadas]
                    valores = [cat[1] for cat in categorias_ordenadas]
                    explode = [0.05] * len(categorias_ordenadas)
                
                colors_plt = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                
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
                
                for autotext in autotexts:
                    autotext.set_color('darkblue')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
                
                ax2 = fig.add_subplot(212)
                top_10 = categorias_ordenadas[:10]
                categorias_barras = [cat[0].replace('_', ' ').title() for cat in top_10]
                montos_barras = [cat[1] for cat in top_10]
                
                y_pos = np.arange(len(categorias_barras))
                colors_barras = plt.cm.viridis(np.linspace(0, 1, len(categorias_barras)))
                bars = ax2.barh(y_pos, montos_barras, color=colors_barras)
                ax2.set_yticks(y_pos)
                ax2.set_yticklabels(categorias_barras, fontsize=9)
                ax2.set_xlabel('Monto ($)', fontweight='bold')
                ax2.set_title('Top 10 Categorías por Monto Gastado', fontsize=12, fontweight='bold', pad=10)
                
                for bar, monto in zip(bars, montos_barras):
                    width = bar.get_width()
                    ax2.text(width + (max(montos_barras) * 0.01), bar.get_y() + bar.get_height()/2,
                            f'${monto:,.0f}', ha='left', va='center', fontsize=8, fontweight='bold')
                
                fig.tight_layout(pad=3.0)
                
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=150, bbox_inches='tight', 
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE GASTOS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6.5*inch, height=5*inch))
                elements.append(Spacer(1, 15))
                
                print("✅ Gráficos de matplotlib generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráfico: {e}. Continuando sin gráfico.")

            # Tabla detallada
            elements.append(Paragraph("DISTRIBUCIÓN DETALLADA DE GASTOS", self.estilo_subtitulo))
            
            data_gastos = [['Categoría', 'Monto', 'Porcentaje']]
            
            for categoria, monto in categorias_ordenadas:
                porcentaje = (monto / total_gastos * 100) if total_gastos > 0 else 0
                data_gastos.append([
                    categoria.replace('_', ' ').title(),
                    f"${monto:,.0f}",
                    f"{porcentaje:.1f}%"
                ])
            
            data_gastos.append([
                'TOTAL GASTOS',
                f"${total_gastos:,.0f}",
                '100%'
            ])
            
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

            # Análisis detallado
            elements.append(Paragraph("ANÁLISIS DETALLADO", self.estilo_subtitulo))
            
            categoria_mayor = categorias_ordenadas[0] if categorias_ordenadas else ('N/A', 0)
            top_3 = categorias_ordenadas[:3]
            porcentaje_top_3 = sum(monto for _, monto in top_3) / total_gastos * 100 if total_gastos > 0 else 0
            
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

            # Recomendaciones
            elements.append(Paragraph("RECOMENDACIONES ESTRATÉGICAS", self.estilo_subtitulo))
            
            recomendaciones = self._generar_recomendaciones_gastos(gastos_por_categoria, total_gastos)
            for recomendacion in recomendaciones:
                elements.append(Paragraph(f"• {recomendacion}", self.styles['Normal']))

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
            
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE GASTOS")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_gastos_por_categoria(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene gastos agrupados por categoría - CON FILTRO MULTI-TENANT"""
        try:
            # ✅ FILTRAR POR TENANT
            from models import PagoIndividual
            
            pagos = PagoIndividual.query.filter(
                PagoIndividual.fecha_pago.between(fecha_inicio, fecha_fin),
                PagoIndividual.panaderia_id == panaderia_id
            ).all()
            
            gastos = {}
            for pago in pagos:
                categoria = pago.categoria or 'Otros'
                gastos[categoria] = gastos.get(categoria, 0) + pago.monto
            
            return gastos
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

    def generar_reporte_tendencia_ventas(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Tendencia de Ventas con análisis de comportamiento - CON FILTRO MULTI-TENANT"""
        try:
            print(f"📈 Generando tendencia de ventas para {fecha_inicio} a {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch,
                                leftMargin=0.4*inch,
                                rightMargin=0.4*inch)
            
            elements = []

            elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
            elements.append(Paragraph("ANÁLISIS DE TENDENCIA DE VENTAS", self.estilo_titulo))
            elements.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))

            # ✅ FILTRAR POR TENANT
            datos_ventas = self._obtener_datos_tendencia_ventas(panaderia_id, fecha_inicio, fecha_fin)
            
            if not datos_ventas:
                elements.append(Paragraph("No hay datos de ventas para el período seleccionado.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # Gráficos
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                
                fig = Figure(figsize=(10, 8))
                
                fechas = [item['fecha'] for item in datos_ventas]
                ventas_diarias = [item['venta_total'] for item in datos_ventas]
                ventas_acumuladas = np.cumsum(ventas_diarias)
                
                ax1 = fig.add_subplot(311)
                ax1.plot(fechas, ventas_diarias, color='#3498db', linewidth=2, marker='o', markersize=3)
                ax1.fill_between(fechas, ventas_diarias, alpha=0.3, color='#3498db')
                
                if len(ventas_diarias) > 1:
                    z = np.polyfit(range(len(ventas_diarias)), ventas_diarias, 1)
                    p = np.poly1d(z)
                    ax1.plot(fechas, p(range(len(ventas_diarias))), "r--", alpha=0.8, linewidth=1, label='Tendencia')
                    ax1.legend(fontsize=8)
                
                ax1.set_title('Evolución de Ventas Diarias', fontsize=12, fontweight='bold', pad=10)
                ax1.set_ylabel('Ventas ($)', fontweight='bold', fontsize=9)
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45, labelsize=8)
                ax1.tick_params(axis='y', labelsize=8)
                
                ax2 = fig.add_subplot(312)
                ax2.plot(fechas, ventas_acumuladas, color='#27ae60', linewidth=2)
                ax2.fill_between(fechas, ventas_acumuladas, alpha=0.3, color='#27ae60')
                
                ax2.set_title('Ventas Acumuladas', fontsize=12, fontweight='bold', pad=10)
                ax2.set_ylabel('Ventas Acumuladas ($)', fontweight='bold', fontsize=9)
                ax2.grid(True, alpha=0.3)
                ax2.tick_params(axis='x', rotation=45, labelsize=8)
                ax2.tick_params(axis='y', labelsize=8)
                
                ax3 = fig.add_subplot(313)
                
                if len(datos_ventas) >= 7:
                    df_ventas = pd.DataFrame(datos_ventas)
                    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
                    df_ventas['dia_semana'] = df_ventas['fecha'].dt.day_name()
                    
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_esp = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                    
                    ventas_por_dia = df_ventas.groupby('dia_semana')['venta_total'].mean().reindex(dias_orden)
                    
                    bars = ax3.bar(dias_esp, ventas_por_dia.values, 
                                color=plt.cm.viridis(np.linspace(0, 1, 7)),
                                alpha=0.8)
                    
                    ax3.set_title('Promedio de Ventas por Día', fontsize=12, fontweight='bold', pad=10)
                    ax3.set_ylabel('Ventas Promedio ($)', fontweight='bold', fontsize=9)
                    ax3.grid(True, alpha=0.3, axis='y')
                    ax3.tick_params(axis='both', labelsize=8)
                    
                    for bar, valor in zip(bars, ventas_por_dia.values):
                        height = bar.get_height()
                        ax3.text(bar.get_x() + bar.get_width()/2., height + (max(ventas_por_dia.values) * 0.005),
                                f'${valor:,.0f}', ha='center', va='bottom', fontsize=7, fontweight='bold')
                else:
                    ax3.text(0.5, 0.5, 'Se necesitan más datos\npara análisis semanal', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Análisis Semanal (Datos Insuficientes)', fontsize=12, fontweight='bold', pad=10)
                
                fig.tight_layout(pad=2.0)
                
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE TENDENCIAS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))
                elements.append(Spacer(1, 10))
                
                print("✅ Gráficos de tendencia optimizados generados")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos de tendencia: {e}. Continuando sin gráficos.")

            # Estadísticas
            elements.append(Paragraph("ESTADÍSTICAS PRINCIPALES", self.estilo_subtitulo))
            
            ventas_totales = sum(item['venta_total'] for item in datos_ventas)
            venta_promedio = np.mean([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            venta_maxima = max([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            venta_minima = min([item['venta_total'] for item in datos_ventas]) if datos_ventas else 0
            dias_analizados = len(datos_ventas)
            
            mejor_dia = max(datos_ventas, key=lambda x: x['venta_total']) if datos_ventas else None
            peor_dia = min(datos_ventas, key=lambda x: x['venta_total']) if datos_ventas else None
            
            estadisticas_texto = f"""
            <b>Período Analizado:</b> {dias_analizados} días | <b>Ventas Totales:</b> ${ventas_totales:,.0f}<br/>
            <b>Venta Promedio:</b> ${venta_promedio:,.0f} | <b>Venta Máxima:</b> ${venta_maxima:,.0f} {f"({mejor_dia['fecha'].strftime('%d/%m')})" if mejor_dia else ""}<br/>
            <b>Venta Mínima:</b> ${venta_minima:,.0f} {f"({peor_dia['fecha'].strftime('%d/%m')})" if peor_dia else ""} | <b>Variabilidad:</b> ${venta_maxima - venta_minima:,.0f}
            """
            
            estilo_compacto = ParagraphStyle(
                'Compacto',
                parent=self.styles['Normal'],
                fontSize=9,
                leading=11,
                spaceAfter=6
            )
            
            elements.append(Paragraph(estadisticas_texto, estilo_compacto))
            elements.append(Spacer(1, 12))

            # Patrones
            elements.append(Paragraph("DETECCIÓN DE PATRONES", self.estilo_subtitulo))
            
            patrones = self._analizar_patrones_ventas(datos_ventas)
            for patron in patrones:
                elements.append(Paragraph(f"• {patron}", estilo_compacto))
            
            elements.append(Spacer(1, 10))

            # Proyecciones
            elements.append(Paragraph("PROYECCIÓN Y RECOMENDACIONES", self.estilo_subtitulo))
            
            proyecciones = self._generar_proyecciones_ventas(datos_ventas)
            for proyeccion in proyecciones:
                elements.append(Paragraph(f"• {proyeccion}", estilo_compacto))

            elements.append(Spacer(1, 15))
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de tendencia OPTIMIZADO generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_tendencia_ventas: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE TENDENCIA")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_tendencia_ventas(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene datos de tendencia de ventas - CON FILTRO MULTI-TENANT"""
        try:
            from models import Venta, RegistroDiario
            
            # ✅ FILTRAR POR TENANT
            ventas = Venta.query.filter(
                Venta.fecha_hora >= fecha_inicio,
                Venta.fecha_hora <= fecha_fin,
                Venta.panaderia_id == panaderia_id
            ).all()
            
            # Agrupar por fecha
            datos_por_fecha = {}
            
            for venta in ventas:
                fecha = venta.fecha_hora.date()
                if fecha not in datos_por_fecha:
                    datos_por_fecha[fecha] = 0
                datos_por_fecha[fecha] += venta.total
            
            # Ordenar por fecha
            datos_ordenados = []
            for fecha, total in sorted(datos_por_fecha.items()):
                datos_ordenados.append({
                    'fecha': fecha,
                    'venta_total': total
                })
            
            return datos_ordenados
            
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

    def generar_reporte_ia_predictivo(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de IA Predictivo con recomendaciones inteligentes - CON FILTRO MULTI-TENANT"""
        try:
            print(f"🤖 Generando análisis predictivo IA para {fecha_inicio} a {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch,
                                leftMargin=0.4*inch,
                                rightMargin=0.4*inch)
            
            elements = []

            elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
            elements.append(Paragraph("🤖 ANÁLISIS PREDICTIVO CON INTELIGENCIA ARTIFICIAL", self.estilo_titulo))
            elements.append(Paragraph(f"Período de análisis: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))

            # ✅ FILTRAR POR TENANT
            datos_ventas = self._obtener_datos_tendencia_ventas(panaderia_id, fecha_inicio, fecha_fin)
            datos_productos = self._obtener_datos_productos_populares(panaderia_id, fecha_inicio, fecha_fin)
            
            if not datos_ventas:
                elements.append(Paragraph("No hay datos suficientes para análisis predictivo.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # Gráficos predictivos
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                from datetime import timedelta
                
                fig = Figure(figsize=(10, 8))
                
                fechas = [item['fecha'] for item in datos_ventas]
                ventas_diarias = [item['venta_total'] for item in datos_ventas]
                
                # Gráfico 1: Tendencia con Proyección
                ax1 = fig.add_subplot(221)
                
                ax1.plot(fechas, ventas_diarias, color='#3498db', linewidth=2, marker='o', markersize=3, label='Ventas Reales')
                
                if len(ventas_diarias) > 5:
                    x = np.arange(len(ventas_diarias))
                    z = np.polyfit(x, ventas_diarias, 1)
                    p = np.poly1d(z)
                    
                    x_future = np.arange(len(ventas_diarias) + 7)
                    y_future = p(x_future)
                    
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
                
                # Gráfico 2: Análisis de Estacionalidad Semanal
                ax2 = fig.add_subplot(222)
                
                if len(datos_ventas) >= 14:
                    df = pd.DataFrame(datos_ventas)
                    df['fecha'] = pd.to_datetime(df['fecha'])
                    df['dia_semana'] = df['fecha'].dt.day_name()
                    df['semana'] = df['fecha'].dt.isocalendar().week
                    
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_esp = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                    
                    ventas_por_dia = df.groupby('dia_semana')['venta_total'].mean().reindex(dias_orden)
                    
                    bars = ax2.bar(dias_esp, ventas_por_dia.values, 
                                color=plt.cm.Set3(np.linspace(0, 1, 7)),
                                alpha=0.8)
                    
                    promedio_general = np.mean(ventas_diarias)
                    ax2.axhline(y=promedio_general, color='red', linestyle='--', alpha=0.7, 
                            label=f'Promedio: ${promedio_general:,.0f}')
                    
                    ax2.set_title('Patrón Semanal', fontsize=11, fontweight='bold', pad=8)
                    ax2.set_ylabel('Ventas Promedio ($)', fontsize=9)
                    ax2.legend(fontsize=7)
                    ax2.grid(True, alpha=0.3, axis='y')
                    ax2.tick_params(axis='both', labelsize=7)
                    
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
                
                # Gráfico 3: Análisis de Crecimiento
                ax3 = fig.add_subplot(223)
                
                if len(ventas_diarias) > 1:
                    crecimiento = []
                    for i in range(1, len(ventas_diarias)):
                        if ventas_diarias[i-1] > 0:
                            crecimiento.append(((ventas_diarias[i] - ventas_diarias[i-1]) / ventas_diarias[i-1]) * 100)
                        else:
                            crecimiento.append(0)
                    
                    colores = ['green' if x >= 0 else 'red' for x in crecimiento]
                    bars = ax3.bar(range(len(crecimiento)), crecimiento, color=colores, alpha=0.7)
                    
                    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                    ax3.set_title('Crecimiento Diario (%)', fontsize=11, fontweight='bold', pad=8)
                    ax3.set_ylabel('Crecimiento %', fontsize=9)
                    ax3.grid(True, alpha=0.3, axis='y')
                    ax3.tick_params(axis='both', labelsize=7)
                    
                    crecimiento_promedio = np.mean(crecimiento) if crecimiento else 0
                    ax3.axhline(y=crecimiento_promedio, color='blue', linestyle='--', alpha=0.7,
                            label=f'Promedio: {crecimiento_promedio:+.1f}%')
                    ax3.legend(fontsize=7)
                else:
                    ax3.text(0.5, 0.5, 'Insuficientes datos\npara análisis de crecimiento', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Crecimiento Diario', fontsize=11, fontweight='bold', pad=8)
                
                # Gráfico 4: Heatmap de Performance
                ax4 = fig.add_subplot(224)
                
                if len(datos_ventas) >= 7:
                    venta_max = max(ventas_diarias)
                    venta_min = min(ventas_diarias)
                    venta_prom = np.mean(ventas_diarias)
                    desviacion = np.std(ventas_diarias)
                    
                    metricas = ['Máxima', 'Mínima', 'Promedio', 'Estabilidad']
                    valores = [venta_max, venta_min, venta_prom, (1 - (desviacion/venta_prom)) * 100 if venta_prom > 0 else 0]
                    colores_metricas = ['#27ae60', '#e74c3c', '#3498db', '#f39c12']
                    
                    bars = ax4.bar(metricas, valores, color=colores_metricas, alpha=0.8)
                    ax4.set_title('Métricas Clave', fontsize=11, fontweight='bold', pad=8)
                    ax4.set_ylabel('Valor', fontsize=9)
                    ax4.grid(True, alpha=0.3, axis='y')
                    ax4.tick_params(axis='both', labelsize=7)
                    
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
                
                fig.tight_layout(pad=2.0)
                
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL PREDICTIVO", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))
                elements.append(Spacer(1, 10))
                
                print("✅ Gráficos predictivos generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos predictivos: {e}. Continuando sin gráficos.")

            # Recomendaciones inteligentes
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

            # Predicciones
            elements.append(Paragraph("🔮 PREDICCIONES PARA PRÓXIMA SEMANA", self.estilo_subtitulo))
            
            predicciones = self._generar_predicciones_semanales(datos_ventas)
            
            for prediccion in predicciones:
                elements.append(Paragraph(f"• {prediccion}", estilo_recomendacion))
            
            elements.append(Spacer(1, 10))

            # Plan de acción
            elements.append(Paragraph("🎯 PLAN DE ACCIÓN RECOMENDADO", self.estilo_subtitulo))
            
            plan_accion = self._generar_plan_accion(datos_ventas, datos_productos)
            
            for accion in plan_accion:
                elements.append(Paragraph(f"✓ {accion}", estilo_recomendacion))

            elements.append(Spacer(1, 15))
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"🤖 Generado por Sistema IA el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de IA predictivo generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_ia_predictivo: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE IA")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_productos_populares(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene datos de productos populares - CON FILTRO MULTI-TENANT"""
        try:
            from models import Producto, DetalleVenta, Venta
            from sqlalchemy import func
            
            # ✅ FILTRAR POR TENANT
            productos = Producto.query.filter_by(
                panaderia_id=panaderia_id,
                activo=True
            ).all()
            
            datos_productos = []
            for producto in productos:
                # Calcular ventas del período
                ventas = DetalleVenta.query.join(Venta).filter(
                    DetalleVenta.producto_id == producto.id,
                    Venta.fecha_hora >= fecha_inicio,
                    Venta.fecha_hora <= fecha_fin,
                    Venta.panaderia_id == panaderia_id
                ).with_entities(func.sum(DetalleVenta.cantidad)).scalar() or 0
                
                if ventas > 0:
                    datos_productos.append({
                        'nombre': producto.nombre,
                        'ventas': ventas,
                        'stock': producto.stock_actual or 0
                    })
            
            # Ordenar por ventas
            datos_productos.sort(key=lambda x: x['ventas'], reverse=True)
            return datos_productos[:10]  # Top 10
            
        except Exception as e:
            print(f"Error al obtener datos de productos populares: {e}")
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

    def generar_reporte_analisis_inventarios(self, panaderia_id, fecha_inicio, fecha_fin):
        """Genera reporte de Análisis de Inventarios con gestión de stock - CON FILTRO MULTI-TENANT"""
        try:
            print(f"📦 Generando análisis de inventarios para {fecha_inicio} a {fecha_fin}")
            print(f"🔍 PANADERÍA ID: {panaderia_id}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                pagesize=A4, 
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch,
                                leftMargin=0.4*inch,
                                rightMargin=0.4*inch)
            
            elements = []

            elements.append(Paragraph("PANADERÍA-POS", self.estilo_titulo))
            elements.append(Paragraph("📦 ANÁLISIS DE INVENTARIOS Y GESTIÓN DE STOCK", self.estilo_titulo))
            elements.append(Paragraph(f"Período de análisis: {fecha_inicio} a {fecha_fin}", self.styles['Normal']))
            elements.append(Spacer(1, 10))

            # ✅ FILTRAR POR TENANT
            datos_inventarios = self._obtener_datos_inventarios_reales(panaderia_id)
            datos_rotacion = self._obtener_datos_rotacion_reales(panaderia_id, fecha_inicio, fecha_fin)
            
            if not datos_inventarios:
                elements.append(Paragraph("No hay datos de inventarios disponibles para análisis.", self.styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # Gráficos
            try:
                import matplotlib.pyplot as plt
                from matplotlib.figure import Figure
                import numpy as np
                import pandas as pd
                
                fig = Figure(figsize=(10, 8))
                
                productos = [item['nombre'] for item in datos_inventarios]
                stock_actual = [item['stock_actual'] for item in datos_inventarios]
                stock_minimo = [item['stock_minimo'] for item in datos_inventarios]
                stock_maximo = [item.get('stock_maximo', item['stock_minimo'] * 3) for item in datos_inventarios]
                
                ax1 = fig.add_subplot(221)
                x_pos = np.arange(len(productos))
                ancho = 0.25
                
                productos_cortos = [p[:15] + '...' if len(p) > 15 else p for p in productos]
                
                bars1 = ax1.bar(x_pos - ancho, stock_actual, ancho, 
                            label='Stock Actual', alpha=0.8, color='#3498db')
                bars2 = ax1.bar(x_pos, stock_minimo, ancho, 
                            label='Stock Mínimo', alpha=0.8, color='#e74c3c')
                bars3 = ax1.bar(x_pos + ancho, stock_maximo, ancho, 
                            label='Stock Máximo', alpha=0.8, color='#27ae60')
                
                for i, (actual, minimo) in enumerate(zip(stock_actual, stock_minimo)):
                    if actual <= minimo:
                        ax1.axvline(x=i, color='red', alpha=0.3, linestyle='--')
                
                ax1.set_title('Niveles de Stock por Producto', fontsize=11, fontweight='bold', pad=8)
                ax1.set_ylabel('Cantidad en Stock', fontsize=9)
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(productos_cortos, rotation=45, ha='right', fontsize=7)
                ax1.legend(fontsize=7)
                ax1.grid(True, alpha=0.3, axis='y')
                
                ax2 = fig.add_subplot(222)
                valores_inventario = [item['valor_inventario'] for item in datos_inventarios]
                total_valor = sum(valores_inventario)
                
                datos_ordenados = sorted(zip(productos, valores_inventario, stock_actual), 
                                    key=lambda x: x[1], reverse=True)
                
                productos_ordenados = [item[0] for item in datos_ordenados]
                valores_ordenados = [item[1] for item in datos_ordenados]
                acumulado = np.cumsum(valores_ordenados)
                porcentaje_acumulado = (acumulado / total_valor * 100) if total_valor > 0 else [0]
                
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
                
                ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Límite A/B (80%)')
                ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7, label='Límite B/C (95%)')
                
                ax3 = fig.add_subplot(223)
                
                if datos_rotacion:
                    productos_rot = [item['producto'] for item in datos_rotacion]
                    rotacion = [item['indice_rotacion'] for item in datos_rotacion]
                    
                    colores = []
                    for rot in rotacion:
                        if rot > 12:
                            colores.append('#27ae60')
                        elif rot > 6:
                            colores.append('#f39c12')
                        else:
                            colores.append('#e74c3c')
                    
                    productos_rot_cortos = [p[:12] + '...' if len(p) > 12 else p for p in productos_rot]
                    bars = ax3.bar(productos_rot_cortos, rotacion, color=colores, alpha=0.8)
                    
                    ax3.set_title('Índice de Rotación de Inventario', fontsize=11, fontweight='bold', pad=8)
                    ax3.set_ylabel('Rotación (veces/año)', fontsize=9)
                    ax3.tick_params(axis='x', rotation=45, labelsize=7)
                    ax3.tick_params(axis='y', labelsize=7)
                    ax3.grid(True, alpha=0.3, axis='y')
                    
                    ax3.axhline(y=12, color='green', linestyle='--', alpha=0.5, label='Alta Rotación')
                    ax3.axhline(y=6, color='orange', linestyle='--', alpha=0.5, label='Media Rotación')
                    ax3.legend(fontsize=7)
                else:
                    ax3.text(0.5, 0.5, 'Datos de rotación\nno disponibles', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray"))
                    ax3.set_title('Índice de Rotación', fontsize=11, fontweight='bold', pad=8)
                
                ax4 = fig.add_subplot(224)
                
                dias_stock = []
                for item in datos_inventarios:
                    demanda_promedio = item.get('demanda_promedio', 0)
                    if demanda_promedio > 0:
                        dias = item['stock_actual'] / demanda_promedio
                    else:
                        dias = 999
                    dias_stock.append(dias)
                
                productos_cortos_dias = [p[:10] + '...' if len(p) > 10 else p for p in productos]
                
                colores_dias = []
                for dias in dias_stock:
                    if dias <= 7:
                        colores_dias.append('#e74c3c')
                    elif dias <= 14:
                        colores_dias.append('#f39c12')
                    else:
                        colores_dias.append('#27ae60')
                
                bars = ax4.bar(productos_cortos_dias, dias_stock, color=colores_dias, alpha=0.8)
                
                ax4.set_title('Días de Stock Disponible', fontsize=11, fontweight='bold', pad=8)
                ax4.set_ylabel('Días de Stock', fontsize=9)
                ax4.tick_params(axis='x', rotation=45, labelsize=6)
                ax4.tick_params(axis='y', labelsize=7)
                ax4.grid(True, alpha=0.3, axis='y')
                
                ax4.axhline(y=7, color='red', linestyle='--', alpha=0.7, label='Límite Crítico (7 días)')
                ax4.axhline(y=14, color='orange', linestyle='--', alpha=0.7, label='Límite Alerta (14 días)')
                ax4.legend(fontsize=6)
                
                fig.tight_layout(pad=2.0)
                
                graphic_buffer = BytesIO()
                fig.savefig(graphic_buffer, format='png', dpi=120, bbox_inches='tight',
                        facecolor='#f8f9fa', edgecolor='none')
                graphic_buffer.seek(0)
                
                from reportlab.platypus import Image
                elements.append(Paragraph("ANÁLISIS VISUAL DE INVENTARIOS", self.estilo_subtitulo))
                elements.append(Image(graphic_buffer, width=6*inch, height=6*inch))
                elements.append(Spacer(1, 10))
                
                print("✅ Gráficos de inventario generados exitosamente")
                
            except ImportError:
                print("⚠️ matplotlib/pandas no disponible. Generando reporte sin gráficos.")
            except Exception as e:
                print(f"⚠️ Error al generar gráficos de inventario: {e}. Continuando sin gráficos.")

            # Resumen Ejecutivo
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

            # Alertas
            elements.append(Paragraph("🚨 ALERTAS DE INVENTARIO", self.estilo_subtitulo))
            
            alertas = self._generar_alertas_inventarios(datos_inventarios)
            
            for alerta in alertas:
                elements.append(Paragraph(f"⚠ {alerta}", estilo_resumen))
            
            elements.append(Spacer(1, 12))

            # Recomendaciones
            elements.append(Paragraph("💡 RECOMENDACIONES DE OPTIMIZACIÓN", self.estilo_subtitulo))
            
            recomendaciones = self._generar_recomendaciones_inventarios(datos_inventarios, datos_rotacion)
            
            for recomendacion in recomendaciones:
                elements.append(Paragraph(f"✓ {recomendacion}", estilo_resumen))
            
            elements.append(Spacer(1, 10))

            # Tabla de Puntos de Reorden
            elements.append(Paragraph("📋 PUNTOS DE REORDEN SUGERIDOS", self.estilo_subtitulo))
            
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            datos_tabla = [['Producto', 'Stock Actual', 'Mínimo', 'Reorden', 'Estado', 'Valor']]
            
            for item in datos_inventarios[:8]:
                stock_actual = item['stock_actual']
                stock_min = item['stock_minimo']
                estado = "✅ OK" if stock_actual > stock_min else "🚨 BAJO"
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

            elements.append(Spacer(1, 15))
            from reportlab.lib import colors as rl_colors
            elements.append(Paragraph(f"📦 Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                    ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=7, textColor=rl_colors.gray)))

            doc.build(elements)
            buffer.seek(0)
            print(f"✅ Reporte de análisis de inventarios generado. Tamaño: {buffer.getbuffer().nbytes} bytes")
            return buffer

        except Exception as e:
            print(f"❌ Error en generar_reporte_analisis_inventarios: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_buffer = BytesIO()
            c = canvas.Canvas(error_buffer, pagesize=A4)
            c.drawString(100, 800, "ERROR AL GENERAR REPORTE DE INVENTARIOS")
            c.drawString(100, 780, f"Error: {str(e)}")
            c.showPage()
            c.save()
            error_buffer.seek(0)
            return error_buffer

    def _obtener_datos_inventarios_reales(self, panaderia_id):
        """Obtiene datos REALES de inventarios desde la base de datos - CON FILTRO MULTI-TENANT"""
        try:
            from models import MateriaPrima, Producto, ProductoExterno
            
            datos_inventarios = []
            
            # ✅ 1. MATERIAS PRIMAS (ingredientes)
            materias_primas = MateriaPrima.query.filter_by(
                activo=True,
                panaderia_id=panaderia_id  # ✅ FILTRO MULTI-TENANT
            ).all()
            
            for mp in materias_primas:
                valor_inventario = mp.stock_actual * mp.costo_promedio
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
                tipo_producto='produccion',
                panaderia_id=panaderia_id  # ✅ FILTRO MULTI-TENANT
            ).all()
            
            for producto in productos_produccion:
                if producto.receta:
                    costo_unitario = producto.receta.costo_unitario if producto.receta.costo_unitario > 0 else producto.precio_venta * 0.3
                else:
                    costo_unitario = producto.precio_venta * 0.3
                
                valor_inventario = producto.stock_actual * costo_unitario
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
            productos_externos = ProductoExterno.query.filter_by(
                activo=True,
                panaderia_id=panaderia_id  # ✅ FILTRO MULTI-TENANT
            ).all()
            
            for producto in productos_externos:
                valor_inventario = producto.stock_actual * producto.precio_compra
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
        """Calcula la demanda promedio de una materia prima basada en uso en recetas - CORREGIDO MULTI-TENANT"""
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
                # Obtener órdenes de producción para esta receta - CORREGIDO: Añadido filtro panaderia_id
                ordenes = OrdenProduccion.query.filter(
                    OrdenProduccion.receta_id == ingrediente.receta_id,
                    OrdenProduccion.fecha_produccion >= fecha_inicio,
                    OrdenProduccion.estado == 'COMPLETADA',
                    OrdenProduccion.panaderia_id == current_user.panaderia_id  # ✅ NUEVO FILTRO MULTI-TENANT
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
        """Calcula la demanda promedio de un producto basada en ventas históricas - CORREGIDO MULTI-TENANT"""
        try:
            from models import DetalleVenta, Venta
            from datetime import datetime, timedelta
            
            fecha_inicio = datetime.now() - timedelta(days=30)
            
            # ✅ CORREGIDO: Añadido filtro panaderia_id
            ventas_totales = DetalleVenta.query.join(Venta).filter(
                DetalleVenta.producto_id == producto_id,
                Venta.fecha_hora >= fecha_inicio,
                Venta.panaderia_id == current_user.panaderia_id  # ✅ NUEVO FILTRO MULTI-TENANT
            ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
            
            demanda_promedio = ventas_totales / 30.0
            return max(demanda_promedio, 0.1)
            
        except Exception as e:
            print(f"Error calculando demanda producto {producto_id}: {e}")
            return 1.0

    def _calcular_demanda_producto_externo(self, producto_externo_id):
        """Calcula la demanda promedio de un producto externo - CORREGIDO MULTI-TENANT"""
        try:
            from models import DetalleVenta, Venta
            from datetime import datetime, timedelta
            
            fecha_inicio = datetime.now() - timedelta(days=30)
            
            # ✅ CORREGIDO: Añadido filtro panaderia_id
            ventas_totales = DetalleVenta.query.join(Venta).filter(
                DetalleVenta.producto_externo_id == producto_externo_id,
                Venta.fecha_hora >= fecha_inicio,
                Venta.panaderia_id == current_user.panaderia_id  # ✅ NUEVO FILTRO MULTI-TENANT
            ).with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
            
            demanda_promedio = ventas_totales / 30.0
            return max(demanda_promedio, 0.1)
            
        except Exception as e:
            print(f"Error calculando demanda producto externo {producto_externo_id}: {e}")
            return 1.0

    def _obtener_datos_rotacion_reales(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene datos REALES de rotación de inventarios - CON FILTRO MULTI-TENANT"""
        try:
            from models import Producto, ProductoExterno, DetalleVenta, Venta
            from sqlalchemy import func
            
            datos_rotacion = []
            
            # ✅ Productos de producción
            productos = Producto.query.filter_by(
                activo=True,
                panaderia_id=panaderia_id  # ✅ FILTRO MULTI-TENANT
            ).all()
            
            for producto in productos:
                # ✅ Calcular ventas del período
                ventas_periodo = DetalleVenta.query.join(Venta).filter(
                    DetalleVenta.producto_id == producto.id,
                    Venta.fecha_hora >= fecha_inicio,
                    Venta.fecha_hora <= fecha_fin,
                    Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
                ).with_entities(func.sum(DetalleVenta.cantidad)).scalar() or 0
                
                stock_promedio = producto.stock_actual
                
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
            
            # ✅ Productos externos
            productos_externos = ProductoExterno.query.filter_by(
                activo=True,
                panaderia_id=panaderia_id  # ✅ FILTRO MULTI-TENANT
            ).all()
            
            for producto in productos_externos:
                # ✅ Calcular ventas del período
                ventas_periodo = DetalleVenta.query.join(Venta).filter(
                    DetalleVenta.producto_externo_id == producto.id,
                    Venta.fecha_hora >= fecha_inicio,
                    Venta.fecha_hora <= fecha_fin,
                    Venta.panaderia_id == panaderia_id  # ✅ FILTRO MULTI-TENANT
                ).with_entities(func.sum(DetalleVenta.cantidad)).scalar() or 0
                
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
        
    def _agregar_resumen_ejecutivo_tesoreria(self, elements, datos):
        """Agrega el resumen ejecutivo al reporte de tesorería"""
        metricas = datos['metricas']
        
        resumen_texto = f"""
        <b>Total Ingresos:</b> ${metricas['total_ingresos']:,.0f}<br/>
        <b>Total Egresos:</b> ${metricas['total_egresos']:,.0f}<br/>
        <b>Saldo Final:</b> ${metricas['saldo_final']:,.0f}<br/>
        <b>Flujo Neto Total:</b> ${metricas['flujo_neto_total']:,.0f}<br/>
        <b>Días Analizados:</b> {metricas['dias_analizados']}<br/>
        <b>Días con Flujo Positivo:</b> {metricas['dias_positivos']} ({metricas['dias_positivos']/metricas['dias_analizados']*100 if metricas['dias_analizados'] > 0 else 0:.1f}%)<br/>
        <b>Total Movimientos:</b> {metricas['total_movimientos']}
        """
        elements.append(Paragraph(resumen_texto, self.styles['Normal']))

    def _agregar_analisis_flujo_tesoreria(self, elements, datos):
        """Agrega el análisis de flujo al reporte"""
        metricas = datos['metricas']
        
        analisis_texto = f"""
        <b>Análisis de Flujo:</b><br/>
        - El flujo neto del período es <b>{'positivo' if metricas['flujo_neto_total'] >= 0 else 'negativo'}</b>.<br/>
        - El {metricas['dias_positivos']/metricas['dias_analizados']*100 if metricas['dias_analizados'] > 0 else 0:.1f}% de los días tuvo flujo positivo.<br/>
        - El saldo de caja final es de <b>${metricas['saldo_final']:,.0f}</b>.
        """
        elements.append(Paragraph(analisis_texto, self.styles['Normal']))

    def _agregar_detalle_movimientos_tesoreria(self, elements, datos):
        """Agrega el detalle de movimientos al reporte"""
        movimientos = datos['movimientos']
        
        if not movimientos:
            elements.append(Paragraph("No hay movimientos para mostrar.", self.styles['Normal']))
            return

        # Crear tabla de movimientos
        data = [['Fecha', 'Concepto', 'Referencia', 'Ingresos', 'Egresos', 'Saldo']]
        saldo_acumulado = 0

        for movimiento in movimientos:
            fecha, concepto, referencia, ingresos, egresos, tipo = movimiento
            saldo_acumulado += ingresos - egresos
            data.append([
                fecha.strftime('%d/%m/%Y'),
                concepto,
                referencia or '-',
                f"${ingresos:,.0f}" if ingresos > 0 else "$0",
                f"${egresos:,.0f}" if egresos > 0 else "$0",
                f"${saldo_acumulado:,.0f}"
            ])

            # Totales
            total_ingresos = sum(mov[3] for mov in movimientos)
            total_egresos = sum(mov[4] for mov in movimientos)
            data.append([
                'TOTALES', '', '', 
                f"${total_ingresos:,.0f}", 
                f"${total_egresos:,.0f}", 
                f"${saldo_acumulado:,.0f}"
            ])

            tabla = Table(data, colWidths=[0.8*inch, 2.2*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.2*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 8),
            ]))
            elements.append(tabla)

    def _agregar_recomendaciones_tesoreria(self, elements, datos):
        """Agrega recomendaciones estratégicas basadas en el análisis"""
        metricas = datos['metricas']
        recomendaciones = []

        # Análisis de saldo
        if metricas['saldo_final'] < 0:
            recomendaciones.append("• <b>Atención:</b> Saldo negativo detectado. Se recomienda revisar gastos operativos y considerar ajustes en el flujo de efectivo.")
        elif metricas['saldo_final'] < 100000:  # Umbral ajustable según tu negocio
            recomendaciones.append("• <b>Monitoreo:</b> Saldo bajo identificado. Se sugiere vigilancia cercana del flujo de caja en los próximos días.")

        # Análisis de consistencia de flujo
        if metricas['dias_analizados'] > 0:
            porcentaje_positivo = (metricas['dias_positivos'] / metricas['dias_analizados']) * 100
            if porcentaje_positivo < 50:
                recomendaciones.append("• <b>Oportunidad:</b> Menos del 50% de los días muestran flujo positivo. Evaluar estrategias para mejorar la consistencia de ingresos.")
            elif porcentaje_positivo > 80:
                recomendaciones.append("• <b>Fortalecimiento:</b> Alta consistencia en flujos positivos. Considerar oportunidades de reinversión o crecimiento.")

        # Recomendación general basada en el volumen
        if metricas['total_movimientos'] < 10:
            recomendaciones.append("• <b>Observación:</b> Baja actividad transaccional en el período. Validar completitud de registros.")
        
        # Mensaje final positivo si no hay alertas críticas
        if not recomendaciones:
            recomendaciones.append("• <b>Estabilidad:</b> La posición de tesorería se mantiene estable. Continuar con las prácticas actuales de gestión.")

        # Agregar todas las recomendaciones
        for rec in recomendaciones:
            elements.append(Paragraph(rec, self.styles['Normal']))

    def _generar_reporte_error(self, mensaje):
        """Genera un PDF de error mínimo"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = [Paragraph(f"Error: {mensaje}", self.styles['Normal'])]
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
        # ========================================== NUEVAS FUNCIONES PARA REPORTE UNIFICADO DE TESORERÍA ===========================================

    def _obtener_datos_tesoreria_combinados(self, panaderia_id, fecha_inicio, fecha_fin):
        """Obtiene datos combinados de tesorería - CON FILTRO MULTI-TENANT"""
        try:
            # ✅ FILTRAR POR TENANT
            movimientos = self._obtener_movimientos_periodo(panaderia_id, fecha_inicio, fecha_fin)
            flujo_data = self._obtener_flujo_caja_periodo(panaderia_id, fecha_inicio, fecha_fin)
            
            # Calcular totales
            total_ingresos = sum(m[3] for m in movimientos) if movimientos else 0
            total_egresos = sum(m[4] for m in movimientos) if movimientos else 0
            saldo_final = total_ingresos - total_egresos
            
            return {
                'movimientos': movimientos,
                'flujo_data': flujo_data,
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'saldo_final': saldo_final,
                'total_movimientos': len(movimientos) if movimientos else 0
            }
        except Exception as e:
            print(f"Error al obtener datos de tesorería: {e}")
            return {
                'movimientos': [],
                'flujo_data': [],
                'total_ingresos': 0,
                'total_egresos': 0,
                'saldo_final': 0,
                'total_movimientos': 0
            }

    def _agregar_resumen_ejecutivo_tesoreria(self, elements, datos):
        """Agrega el resumen ejecutivo al reporte"""
        metricas = datos['metricas']
        
        resumen_texto = f"""
        <b>Total Ingresos:</b> ${metricas['total_ingresos']:,.0f}<br/>
        <b>Total Egresos:</b> ${metricas['total_egresos']:,.0f}<br/>
        <b>Saldo Final:</b> ${metricas['saldo_final']:,.0f}<br/>
        <b>Flujo Neto Total:</b> ${metricas['flujo_neto_total']:,.0f}<br/>
        <b>Días Analizados:</b> {metricas['dias_analizados']}<br/>
        <b>Días con Flujo Positivo:</b> {metricas['dias_positivos']} ({metricas['dias_positivos']/metricas['dias_analizados']*100 if metricas['dias_analizados'] > 0 else 0:.1f}%)<br/>
        <b>Total Movimientos:</b> {metricas['total_movimientos']}
        """
        elements.append(Paragraph(resumen_texto, self.styles['Normal']))

    
    def _generar_reporte_error(self, mensaje):
        """Genera un PDF de error mínimo"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = [Paragraph(f"Error: {mensaje}", self.styles['Normal'])]
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_tesoreria_unificado(self, panaderia_id, fecha_inicio, fecha_fin, nivel_detalle='completo'):
        """Genera el Reporte Unificado de Tesorería - INCLUYE GASTOS Y UTILIDAD NETA"""
        try:
            from models import RegistroDiario, PagoIndividual, DepositoBancario
            from sqlalchemy import func
            from datetime import datetime
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,
                spaceAfter=20
            )
            story.append(Paragraph("REPORTE UNIFICADO DE TESORERÍA", title_style))
            story.append(Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # 1. OBTENER INGRESOS (de RegistroDiario)
            registros = RegistroDiario.query.filter_by(panaderia_id=panaderia_id).filter(
                RegistroDiario.fecha >= fecha_inicio,
                RegistroDiario.fecha <= fecha_fin
            ).order_by(RegistroDiario.fecha).all()
            
            total_ingresos = sum(r.total_ingresos or 0 for r in registros)
            
            # 2. OBTENER GASTOS (de PagoIndividual)
            gastos = PagoIndividual.query.filter_by(panaderia_id=panaderia_id).filter(
                PagoIndividual.fecha_pago >= fecha_inicio,
                PagoIndividual.fecha_pago <= fecha_fin
            ).all()
            
            # Clasificar gastos por categoría
            gastos_por_categoria = {}
            total_gastos = 0
            for g in gastos:
                categoria = g.categoria or 'Sin categoría'
                if categoria not in gastos_por_categoria:
                    gastos_por_categoria[categoria] = 0
                gastos_por_categoria[categoria] += g.monto
                total_gastos += g.monto
            
            # 3. CALCULAR FLUJO NETO Y UTILIDAD
            flujo_neto = total_ingresos - total_gastos
            utilidad_neta = flujo_neto  # La utilidad neta es el flujo neto
            
            # RESUMEN EJECUTIVO
            story.append(Paragraph("RESUMEN EJECUTIVO", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Crear tabla de resumen - Usar strings planos, NO Paragraphs
            datos_resumen = [
                ['Concepto', 'Monto'],
                ['Total Ingresos', f'${total_ingresos:,.0f}'],
                ['Total Gastos', f'${total_gastos:,.0f}'],
                ['Flujo Neto', f'${flujo_neto:,.0f}']
            ]
            
            # Si la utilidad es negativa, mostrarla con formato especial
            if utilidad_neta < 0:
                datos_resumen.append(['Utilidad Neta del Período', f'${utilidad_neta:,.0f} (PÉRDIDA)'])
            else:
                datos_resumen.append(['Utilidad Neta del Período', f'${utilidad_neta:,.0f}'])
            
            tabla_resumen = Table(datos_resumen, colWidths=[200, 200])
            
            # Estilo de la tabla
            estilo_tabla = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
            
            # Color para la fila de Utilidad Neta
            if utilidad_neta < 0:
                estilo_tabla.append(('BACKGROUND', (0, 4), (-1, 4), colors.pink))
                estilo_tabla.append(('TEXTCOLOR', (0, 4), (-1, 4), colors.black))
                estilo_tabla.append(('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'))
            else:
                estilo_tabla.append(('BACKGROUND', (0, 4), (-1, 4), colors.lightgreen))
                estilo_tabla.append(('TEXTCOLOR', (0, 4), (-1, 4), colors.black))
                estilo_tabla.append(('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'))
            
            tabla_resumen.setStyle(TableStyle(estilo_tabla))
            story.append(tabla_resumen)
            story.append(Spacer(1, 20))
            
            # GASTOS POR CATEGORÍA
            story.append(Paragraph("GASTOS POR CATEGORÍA", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Crear tabla de gastos - Usar strings planos
            datos_gastos = [['Categoría', 'Monto']]
            for cat, monto in sorted(gastos_por_categoria.items(), key=lambda x: x[1], reverse=True):
                datos_gastos.append([str(cat), f'${monto:,.0f}'])
            datos_gastos.append(['TOTAL GASTOS', f'${total_gastos:,.0f}'])
            
            tabla_gastos = Table(datos_gastos, colWidths=[250, 150])
            tabla_gastos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabla_gastos)
            story.append(Spacer(1, 20))
            
            # DETALLE DE REGISTROS DIARIOS
            story.append(Paragraph("DETALLE DE INGRESOS DIARIOS", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            datos_detalle = [['Fecha', 'Ingresos']]
            for r in registros:
                datos_detalle.append([
                    r.fecha.strftime('%d/%m/%Y'),
                    f'${(r.total_ingresos or 0):,.0f}'
                ])
            datos_detalle.append(['TOTAL', f'${total_ingresos:,.0f}'])
            
            tabla_detalle = Table(datos_detalle, colWidths=[150, 150])
            tabla_detalle.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabla_detalle)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error en generar_reporte_tesoreria_unificado: {e}")
            import traceback
            traceback.print_exc()
            raise