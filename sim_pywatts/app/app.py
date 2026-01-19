from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_migrate import Migrate
from models import db, Usuario, Dispositivo, ConsumoBimestral, Reporte
# CORRECCIÓN 1: Agregamos DISPOSITIVOS_DATA a la importación
from forms import (RegistroUsuarioForm, DispositivoForm, ConsumoBimestralForm, 
                   GenerarReporteForm, BusquedaUsuarioForm, DISPOSITIVOS_DATA)
from services.calculations import OptimizadorEnergetico
from services.recommendations import GeneradorRecomendaciones
from services.charts import GeneradorGraficas
from services.pdf_generator import GeneradorPDF
from datetime import datetime
import os

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'clave_secreta_real_ig'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pywatts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de carpetas
UPLOAD_FOLDER = 'exports/reports'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('lista_usuarios'))

@app.route('/registro', methods=['GET', 'POST'])
def registro_usuario():
    """Registro de nuevo usuario"""
    form = RegistroUsuarioForm()
    
    if form.validate_on_submit():
        usuario_existente = Usuario.query.filter_by(
            nombre_usuario=form.nombre_usuario.data
        ).first()
        
        if usuario_existente:
            flash('El nombre de usuario ya está registrado. Por favor, elija otro.', 'danger')
            return render_template('register.html', form=form)
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre_usuario=form.nombre_usuario.data,
            domicilio=form.domicilio.data
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash(f'Usuario {nuevo_usuario.nombre_usuario} registrado exitosamente!', 'success')
        return redirect(url_for('dashboard', usuario_id=nuevo_usuario.id))
    
    return render_template('register.html', form=form)


@app.route('/usuarios')
def lista_usuarios():
    busqueda_form = BusquedaUsuarioForm()
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return render_template('login.html', usuarios=usuarios, form=busqueda_form)


@app.route('/dashboard/<int:usuario_id>')
def dashboard(usuario_id):
    """Dashboard principal del usuario"""
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('lista_usuarios'))
    dispositivos = usuario.dispositivos
    consumos = usuario.consumos
    reportes = usuario.reportes
    
    # Calcular estadísticas básicas
    total_dispositivos = len(dispositivos)
    consumo_total = sum(d.consumo_bimestral_kwh() for d in dispositivos) if dispositivos else 0
    
    ultimo_consumo = consumos[-1] if consumos else None
    ultimo_reporte = reportes[-1] if reportes else None
    
    return render_template('dashboard.html',
                          usuario=usuario,
                          dispositivos=dispositivos,
                          total_dispositivos=total_dispositivos,
                          consumo_total=consumo_total,
                          ultimo_consumo=ultimo_consumo,
                          ultimo_reporte=ultimo_reporte)


@app.route('/usuario/<int:usuario_id>/dispositivo/agregar', methods=['GET', 'POST'])
def agregar_dispositivo(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('lista_usuarios'))
    
    dispositivos = usuario.dispositivos
    consumos = usuario.consumos
    reportes = usuario.reportes
    
    # Datos para el contexto del dashboard
    total_dispositivos = len(dispositivos)
    consumo_total = sum(d.consumo_bimestral_kwh() for d in dispositivos) if dispositivos else 0
    ultimo_consumo = consumos[-1] if consumos else None
    ultimo_reporte = reportes[-1] if reportes else None

    form = DispositivoForm()
    
    if form.validate_on_submit():
        nuevo_dispositivo = Dispositivo(
            usuario_id=usuario_id, 
            nombre=form.nombre.data,
            tipo=form.tipo.data,
            potencia_watts=form.potencia_watts.data,
            horas_uso_dia=form.horas_uso_dia.data
        )
        
        db.session.add(nuevo_dispositivo)
        db.session.commit()
        
        flash(f'Dispositivo "{nuevo_dispositivo.nombre}" agregado exitosamente!', 'success')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    return render_template('dashboard.html', 
                          usuario=usuario, 
                          form=form, 
                          modal_active=True,
                          dispositivos=dispositivos,
                          total_dispositivos=total_dispositivos,
                          consumo_total=consumo_total,
                          ultimo_consumo=ultimo_consumo,
                          ultimo_reporte=ultimo_reporte,
                          reportes=reportes)


@app.route('/usuario/<int:usuario_id>/dispositivo/<int:dispositivo_id>/editar', methods=['GET', 'POST'])
def editar_dispositivo(usuario_id, dispositivo_id):
    usuario = db.session.get(Usuario, usuario_id)
    dispositivo = db.session.get(Dispositivo, dispositivo_id)
    
    if dispositivo.usuario_id != usuario_id:
        flash('No tienes permiso para editar este dispositivo', 'danger')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    dispositivos = usuario.dispositivos
    consumos = usuario.consumos
    reportes = usuario.reportes
    
    total_dispositivos = len(dispositivos)
    consumo_total = sum(d.consumo_bimestral_kwh() for d in dispositivos) if dispositivos else 0
    ultimo_consumo = consumos[-1] if consumos else None
    ultimo_reporte = reportes[-1] if reportes else None

    form = DispositivoForm(obj=dispositivo)
    
    if form.validate_on_submit():
        dispositivo.nombre = form.nombre.data
        dispositivo.tipo = form.tipo.data
        dispositivo.potencia_watts = form.potencia_watts.data
        dispositivo.horas_uso_dia = form.horas_uso_dia.data
        
        db.session.commit()
        
        flash(f'Dispositivo "{dispositivo.nombre}" actualizado exitosamente!', 'success')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    return render_template('dashboard.html', 
                          usuario=usuario, 
                          form=form, 
                          dispositivo=dispositivo, 
                          modal_active=True, 
                          modo_edicion=True,
                          dispositivos=dispositivos,
                          total_dispositivos=total_dispositivos,
                          consumo_total=consumo_total,
                          ultimo_consumo=ultimo_consumo,
                          ultimo_reporte=ultimo_reporte,
                          reportes=reportes)


@app.route('/usuario/<int:usuario_id>/dispositivo/<int:dispositivo_id>/eliminar', methods=['POST'])
def eliminar_dispositivo(usuario_id, dispositivo_id):
    """Eliminar dispositivo"""
    dispositivo = Dispositivo.query.get_or_404(dispositivo_id)
    
    if dispositivo.usuario_id != usuario_id:
        flash('No tienes permiso para eliminar este dispositivo', 'danger')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    nombre = dispositivo.nombre
    db.session.delete(dispositivo)
    db.session.commit()
    
    flash(f'Dispositivo "{nombre}" eliminado exitosamente!', 'success')
    return redirect(url_for('dashboard', usuario_id=usuario_id))


@app.route('/usuario/<int:usuario_id>/consumo/agregar', methods=['GET', 'POST'])
def agregar_consumo(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    
    dispositivos = usuario.dispositivos
    consumos = usuario.consumos
    reportes = usuario.reportes
    
    total_dispositivos = len(dispositivos)
    consumo_total = sum(d.consumo_bimestral_kwh() for d in dispositivos) if dispositivos else 0
    ultimo_consumo = consumos[-1] if consumos else None
    ultimo_reporte = reportes[-1] if reportes else None

    form = ConsumoBimestralForm()
    
    if form.validate_on_submit():
        nuevo_consumo = ConsumoBimestral(
            usuario_id=usuario_id,
            periodo_inicio=form.periodo_inicio.data,
            periodo_fin=form.periodo_fin.data,
            consumo_kwh=form.consumo_kwh.data,
            costo_total=form.costo_total.data
        )
        
        db.session.add(nuevo_consumo)
        db.session.commit()
        
        flash('Consumo bimestral registrado exitosamente!', 'success')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    return render_template('dashboard.html', 
                          usuario=usuario, 
                          form=form, 
                          modal_consumo_active=True,
                          dispositivos=dispositivos,
                          total_dispositivos=total_dispositivos,
                          consumo_total=consumo_total,
                          ultimo_consumo=ultimo_consumo,
                          ultimo_reporte=ultimo_reporte,
                          reportes=reportes)


@app.route('/usuario/<int:usuario_id>/analizar')
def analizar_consumo(usuario_id):
    """Página de análisis detallado"""
    usuario = Usuario.query.get_or_404(usuario_id)
    dispositivos = usuario.dispositivos
    
    if not dispositivos:
        flash('Debe agregar al menos un dispositivo para realizar el análisis', 'warning')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    # Tarifa promedio
    tarifa_kwh = 1.5
    ultimo_consumo = usuario.consumos[-1] if usuario.consumos else None
    if ultimo_consumo:
        tarifa_kwh = ultimo_consumo.costo_por_kwh()
    
    # Realizar cálculos
    optimizador = OptimizadorEnergetico(dispositivos, tarifa_kwh)
    consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
    configuracion_optima = optimizador.encontrar_punto_optimo(restriccion_ahorro=0.20)
    ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
    proyeccion = optimizador.proyectar_consumo(dias=30)
    
    # Generar gráficas
    gen_graficas = GeneradorGraficas()
    grafica_barras = gen_graficas.grafica_consumo_por_dispositivo(consumo_por_dispositivo)
    grafica_pie = gen_graficas.grafica_pie_distribucion(consumo_por_dispositivo)
    grafica_comparativa = gen_graficas.grafica_comparativa_antes_despues(ahorro_total)
    
    # Generar recomendaciones
    gen_recomendaciones = GeneradorRecomendaciones(dispositivos, configuracion_optima)
    recomendaciones = gen_recomendaciones.generar_recomendaciones_personalizadas()
    impacto_ambiental = gen_recomendaciones.calcular_impacto_ambiental(
        ahorro_total['ahorro_kwh']
    )
    
    return render_template('report.html',
                          usuario=usuario,
                          consumo_por_dispositivo=consumo_por_dispositivo,
                          configuracion_optima=configuracion_optima,
                          ahorro_total=ahorro_total,
                          recomendaciones=recomendaciones,
                          impacto_ambiental=impacto_ambiental,
                          grafica_barras=grafica_barras,
                          grafica_pie=grafica_pie,
                          grafica_comparativa=grafica_comparativa)


@app.route('/usuario/<int:usuario_id>/generar-pdf')
def generar_pdf(usuario_id):
    """Generar reporte en PDF"""
    usuario = Usuario.query.get_or_404(usuario_id)
    dispositivos = usuario.dispositivos
    
    if not dispositivos:
        flash('Debe agregar al menos un dispositivo para generar el reporte', 'warning')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    # Tarifa promedio
    tarifa_kwh = 1.5
    ultimo_consumo = usuario.consumos[-1] if usuario.consumos else None
    if ultimo_consumo:
        tarifa_kwh = ultimo_consumo.costo_por_kwh()
    
    # Realizar cálculos
    optimizador = OptimizadorEnergetico(dispositivos, tarifa_kwh)
    consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
    configuracion_optima = optimizador.encontrar_punto_optimo(restriccion_ahorro=0.20)
    ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
    
    # Generar recomendaciones
    gen_recomendaciones = GeneradorRecomendaciones(dispositivos, configuracion_optima)
    recomendaciones = gen_recomendaciones.generar_recomendaciones_personalizadas()
    
    # Generar PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f'reporte_{usuario.nombre_usuario}_{timestamp}.pdf'
    ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
    
    generador_pdf = GeneradorPDF(
        usuario,
        consumo_por_dispositivo,
        configuracion_optima,
        ahorro_total,
        recomendaciones
    )
    
    generador_pdf.generar_reporte(ruta_completa)
    
    # Guardar registro del reporte
    nuevo_reporte = Reporte(
        usuario_id=usuario_id,
        consumo_actual_kwh=ahorro_total['consumo_actual_kwh'],
        consumo_optimizado_kwh=ahorro_total['consumo_optimizado_kwh'],
        ahorro_kwh=ahorro_total['ahorro_kwh'],
        ahorro_pesos=ahorro_total['ahorro_pesos'],
        archivo_pdf=nombre_archivo
    )
    
    db.session.add(nuevo_reporte)
    db.session.commit()
    
    flash('Reporte PDF generado exitosamente!', 'success')
    return send_file(ruta_completa, as_attachment=True, download_name=nombre_archivo)


@app.route('/usuario/<int:usuario_id>/reportes')
def ver_reportes(usuario_id):
    """Ver historial de reportes"""
    usuario = Usuario.query.get_or_404(usuario_id)
    reportes = usuario.reportes
    
    return render_template('dashboard.html', usuario=usuario, reportes=reportes, 
                          mostrar_reportes=True)


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('base.html', error='Página no encontrada'), 404


@app.errorhandler(500)
def error_servidor(e):
    return render_template('base.html', error='Error interno del servidor'), 500


@app.route('/usuario/<int:usuario_id>/consumo/<int:consumo_id>/eliminar', methods=['POST'])
def eliminar_consumo(usuario_id, consumo_id):
    """Eliminar un registro de consumo"""
    # Buscar el recibo en la base de datos
    consumo = db.session.get(ConsumoBimestral, consumo_id)
    
    # Verificar que exista y pertenezca al usuario
    if not consumo or consumo.usuario_id != usuario_id:
        flash('No se pudo eliminar el consumo.', 'danger')
        return redirect(url_for('dashboard', usuario_id=usuario_id))
    
    # Borrarlo
    db.session.delete(consumo)
    db.session.commit()
    
    flash('Recibo eliminado exitosamente.', 'success')
    return redirect(url_for('dashboard', usuario_id=usuario_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)