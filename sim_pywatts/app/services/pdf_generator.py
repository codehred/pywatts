from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import os

class GeneradorPDF:
    """
    Genera reportes en PDF con análisis y recomendaciones de consumo energético
    """
    
    def __init__(self, usuario, consumo_dispositivos, configuracion_optima, 
                 ahorro_total, recomendaciones, graficas=None):
        """
        Inicializa el generador de PDF
        
        Args:
            usuario: Objeto Usuario
            consumo_dispositivos: Dict con consumo de cada dispositivo
            configuracion_optima: Dict con configuración óptima
            ahorro_total: Dict con información del ahorro total
            recomendaciones: Dict con recomendaciones personalizadas
            graficas: Dict con gráficas en base64 (opcional)
        """
        self.usuario = usuario
        self.consumo_dispositivos = consumo_dispositivos
        self.configuracion_optima = configuracion_optima
        self.ahorro_total = ahorro_total
        self.recomendaciones = recomendaciones
        self.graficas = graficas or {}
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configura estilos personalizados para el PDF"""
        
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
      
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10,
            alignment=TA_JUSTIFY
        ))
        
      
        self.styles.add(ParagraphStyle(
            name='Destacado',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#27AE60'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
    
    def _crear_encabezado(self, canvas, doc):
        """Crea el encabezado de cada página"""
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#34495E'))
        canvas.drawString(inch, letter[1] - 0.5*inch, "PyWatts - Optimización de Consumo Energético")
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(letter[0] - inch, letter[1] - 0.5*inch, 
                              f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        canvas.line(inch, letter[1] - 0.6*inch, letter[0] - inch, letter[1] - 0.6*inch)
        canvas.restoreState()
    
    def _crear_pie_pagina(self, canvas, doc):
        """Crea el pie de página de cada página"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#95A5A6'))
        canvas.drawCentredString(letter[0]/2, 0.5*inch, f"Página {doc.page}")
        canvas.restoreState()
    
    def generar_reporte(self, ruta_salida):
        """
        Genera el reporte completo en PDF
        
        Args:
            ruta_salida: Ruta donde se guardará el PDF
        
        Returns:
            str: Ruta del archivo generado
        """
        doc = SimpleDocTemplate(ruta_salida, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        elementos = []
        
     
        elementos.extend(self._crear_portada())
        elementos.append(PageBreak())
        
     
        elementos.extend(self._crear_resumen_ejecutivo())
        elementos.append(PageBreak())
        
        
        elementos.extend(self._crear_analisis_consumo())
        elementos.append(PageBreak())
        
       
        elementos.extend(self._crear_configuracion_optima())
        elementos.append(PageBreak())
        
    
        elementos.extend(self._crear_recomendaciones())
        elementos.append(PageBreak())
        
        
        elementos.extend(self._crear_plan_accion())
        
     
        doc.build(elementos, onFirstPage=self._crear_encabezado, 
                 onLaterPages=self._crear_encabezado)
        
        return ruta_salida
    
    def _crear_portada(self):
        """Crea la portada del reporte"""
        elementos = []
        
        elementos.append(Spacer(1, 2*inch))
        
        titulo = Paragraph("REPORTE DE OPTIMIZACIÓN<br/>DE CONSUMO ENERGÉTICO", 
                          self.styles['TituloPrincipal'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.5*inch))
        
        info_usuario = f"""
        <para align=center>
        <b>Usuario:</b> {self.usuario.nombre_usuario}<br/>
        <b>Domicilio:</b> {self.usuario.domicilio}<br/>
        <b>Fecha de generación:</b> {datetime.now().strftime('%d de %B de %Y')}<br/>
        </para>
        """
        elementos.append(Paragraph(info_usuario, self.styles['TextoNormal']))
        elementos.append(Spacer(1, inch))
        
        resumen = Paragraph(
            f"<b>AHORRO POTENCIAL: ${self.ahorro_total['ahorro_pesos']:.2f} MXN BIMESTRALES</b>",
            self.styles['Destacado']
        )
        elementos.append(resumen)
        
        return elementos
    
    def _crear_resumen_ejecutivo(self):
        """Crea el resumen ejecutivo"""
        elementos = []
        
        elementos.append(Paragraph("RESUMEN EJECUTIVO", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
   
        datos_resumen = [
            ['Métrica', 'Valor'],
            ['Consumo Actual', f"{self.ahorro_total['consumo_actual_kwh']:.2f} kWh"],
            ['Consumo Optimizado', f"{self.ahorro_total['consumo_optimizado_kwh']:.2f} kWh"],
            ['Ahorro Energético', f"{self.ahorro_total['ahorro_kwh']:.2f} kWh"],
            ['Ahorro Económico', f"${self.ahorro_total['ahorro_pesos']:.2f} MXN"],
            ['Porcentaje de Ahorro', f"{self.ahorro_total['porcentaje_ahorro']:.1f}%"],
            ['Dispositivos Analizados', str(len(self.consumo_dispositivos))]
        ]
        
        tabla = Table(datos_resumen, colWidths=[3*inch, 2.5*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')])
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 0.3*inch))
        
        texto_resumen = f"""
        Este reporte presenta un análisis detallado del consumo energético en su hogar,
        identificando oportunidades de optimización que pueden generar un ahorro de
        <b>${self.ahorro_total['ahorro_pesos']:.2f} MXN</b> cada bimestre, lo que equivale a
        <b>${self.ahorro_total['ahorro_pesos'] * 6:.2f} MXN anuales</b>.
        <br/><br/>
        El análisis se basa en técnicas de optimización matemática aplicadas a los patrones
        de consumo de {len(self.consumo_dispositivos)} dispositivos registrados en su domicilio.
        """
        elementos.append(Paragraph(texto_resumen, self.styles['TextoNormal']))
        
        return elementos
    
    def _crear_analisis_consumo(self):
        """Crea la sección de análisis de consumo actual"""
        elementos = []
        
        elementos.append(Paragraph("ANÁLISIS DE CONSUMO ACTUAL", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
       
        datos_dispositivos = [
            ['Dispositivo', 'Potencia (W)', 'Horas/Día', 'Consumo (kWh)', 'Costo ($)', '%']
        ]
        
        for nombre, datos in self.consumo_dispositivos.items():
            datos_dispositivos.append([
                nombre,
                f"{datos['potencia_watts']:.0f}",
                f"{datos['horas_uso_dia']:.1f}",
                f"{datos['consumo_bimestral_kwh']:.2f}",
                f"${datos['costo_bimestral']:.2f}",
                f"{datos['porcentaje']:.1f}%"
            ])
        
       
        total_consumo = sum(d['consumo_bimestral_kwh'] for d in self.consumo_dispositivos.values())
        total_costo = sum(d['costo_bimestral'] for d in self.consumo_dispositivos.values())
        
        datos_dispositivos.append([
            'TOTAL',
            '-',
            '-',
            f"{total_consumo:.2f}",
            f"${total_costo:.2f}",
            '100%'
        ])
        
        tabla = Table(datos_dispositivos, colWidths=[1.8*inch, 0.9*inch, 0.9*inch, 1*inch, 0.9*inch, 0.7*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#ECF0F1')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 0.3*inch))
        
      
        dispositivo_mayor = max(self.consumo_dispositivos.items(), 
                               key=lambda x: x[1]['consumo_bimestral_kwh'])
        
        insight = f"""
        <b>Dispositivo con mayor consumo:</b> {dispositivo_mayor[0]} representa el
        {dispositivo_mayor[1]['porcentaje']:.1f}% del consumo total, con
        {dispositivo_mayor[1]['consumo_bimestral_kwh']:.2f} kWh bimestrales.
        """
        elementos.append(Paragraph(insight, self.styles['TextoNormal']))
        
        return elementos
    
    def _crear_configuracion_optima(self):
        """Crea la sección de configuración óptima"""
        elementos = []
        
        elementos.append(Paragraph("CONFIGURACIÓN ÓPTIMA RECOMENDADA", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
        intro = """
        Mediante técnicas de optimización matemática (cálculo de máximos y mínimos),
        hemos identificado la configuración óptima de uso de sus dispositivos:
        """
        elementos.append(Paragraph(intro, self.styles['TextoNormal']))
        elementos.append(Spacer(1, 0.2*inch))
        
     
        datos_config = [
            ['Dispositivo', 'Horas Actuales', 'Horas Óptimas', 'Reducción', 'Ahorro ($)']
        ]
        
        for nombre, config in self.configuracion_optima.items():
            datos_config.append([
                nombre,
                f"{config['horas_actuales']:.1f}h",
                f"{config['horas_optimas']:.1f}h",
                f"{config['reduccion_horas']:.1f}h",
                f"${config['ahorro_pesos']:.2f}"
            ])
        
        tabla = Table(datos_config, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.1*inch, 1*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F8F5')])
        ]))
        
        elementos.append(tabla)
        
        return elementos
    
    def _crear_recomendaciones(self):
        """Crea la sección de recomendaciones"""
        elementos = []
        
        elementos.append(Paragraph("RECOMENDACIONES PERSONALIZADAS", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
       
        if self.recomendaciones['criticas']:
            elementos.append(Paragraph("<b>PRIORIDAD ALTA - Implementar Inmediatamente:</b>", 
                                      self.styles['TextoNormal']))
            elementos.append(Spacer(1, 0.1*inch))
            
            for i, rec in enumerate(self.recomendaciones['criticas'], 1):
                texto = f"""
                <b>{i}. {rec['dispositivo']}</b><br/>
                • Acción: {rec['accion_principal']}<br/>
                • Ahorro potencial: ${rec['ahorro_potencial_pesos']:.2f} MXN<br/>
                """
                if rec['consejos_especificos']:
                    texto += "• Consejos específicos:<br/>"
                    for consejo in rec['consejos_especificos']:
                        texto += f"  - {consejo}<br/>"
                
                elementos.append(Paragraph(texto, self.styles['TextoNormal']))
                elementos.append(Spacer(1, 0.15*inch))
        
        
        if self.recomendaciones['importantes']:
            elementos.append(Paragraph("<b>PRIORIDAD MEDIA - Implementar Gradualmente:</b>", 
                                      self.styles['TextoNormal']))
            elementos.append(Spacer(1, 0.1*inch))
            
            for i, rec in enumerate(self.recomendaciones['importantes'], 1):
                texto = f"""
                <b>{i}. {rec['dispositivo']}</b> - {rec['accion_principal']}<br/>
                Ahorro: ${rec['ahorro_potencial_pesos']:.2f} MXN<br/>
                """
                elementos.append(Paragraph(texto, self.styles['TextoNormal']))
                elementos.append(Spacer(1, 0.1*inch))
        
       
        if self.recomendaciones['generales']:
            elementos.append(Spacer(1, 0.2*inch))
            elementos.append(Paragraph("<b>RECOMENDACIONES GENERALES:</b>", 
                                      self.styles['TextoNormal']))
            elementos.append(Spacer(1, 0.1*inch))
            
            for consejo in self.recomendaciones['generales'][:5]:
                elementos.append(Paragraph(f"• {consejo}", self.styles['TextoNormal']))
        
        return elementos
    
    def _crear_plan_accion(self):
        """Crea el plan de acción"""
        elementos = []
        
        elementos.append(Paragraph("PLAN DE ACCIÓN DE 4 SEMANAS", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
        intro = """
        Para facilitar la implementación de las mejoras, hemos diseñado un plan
        de acción escalonado de 4 semanas:
        """
        elementos.append(Paragraph(intro, self.styles['TextoNormal']))
        elementos.append(Spacer(1, 0.2*inch))
        
        
        from .recommendations import GeneradorRecomendaciones
        gen_rec = GeneradorRecomendaciones([], self.configuracion_optima)
        plan = gen_rec.generar_plan_accion()
        
        for semana, contenido in plan.items():
            elementos.append(Paragraph(f"<b>{contenido['titulo']}</b>", self.styles['TextoNormal']))
            elementos.append(Spacer(1, 0.1*inch))
            
            for accion in contenido['acciones'][:3]:
                if 'dispositivo' in accion:
                    texto = f"• {accion['dispositivo']}: {accion['accion']}"
                elif 'accion_general' in accion:
                    texto = f"• {accion['accion_general']}"
                else:
                    texto = f"• {accion.get('accion', '')}"
                elementos.append(Paragraph(texto, self.styles['TextoNormal']))
            
            elementos.append(Spacer(1, 0.15*inch))
        
      
        elementos.append(Spacer(1, 0.3*inch))
        conclusion = f"""
        <b>Recuerde:</b> Implementando estas recomendaciones, puede ahorrar hasta
        <b>${self.ahorro_total['ahorro_pesos']:.2f} MXN bimestrales</b>, lo que representa
        <b>${self.ahorro_total['ahorro_pesos'] * 6:.2f} MXN anuales</b> y contribuye
        significativamente a la sostenibilidad ambiental.
        """
        elementos.append(Paragraph(conclusion, self.styles['Destacado']))
        
        return elementos