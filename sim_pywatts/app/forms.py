from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from datetime import datetime

class RegistroUsuarioForm(FlaskForm):
    """Formulario para registrar un nuevo usuario"""
    nombre_usuario = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
        ],
        render_kw={'placeholder': 'Ingrese su nombre de usuario'}
    )
    
    domicilio = StringField(
        'Domicilio',
        validators=[
            DataRequired(message='El domicilio es obligatorio'),
            Length(min=5, max=200, message='El domicilio debe tener entre 5 y 200 caracteres')
        ],
        render_kw={'placeholder': 'Calle, Número, Colonia, Ciudad'}
    )
    
    submit = SubmitField('Registrar Usuario')


class DispositivoForm(FlaskForm):
    """Formulario para agregar/editar dispositivos"""
    
    # Tipos de dispositivos comunes
    TIPOS_DISPOSITIVOS = [
        ('', 'Seleccione un tipo'),
        ('refrigerador', 'Refrigerador'),
        ('lavadora', 'Lavadora'),
        ('televisor', 'Televisor'),
        ('tv', 'TV'),
        ('computadora', 'Computadora'),
        ('laptop', 'Laptop'),
        ('aire_acondicionado', 'Aire Acondicionado'),
        ('microondas', 'Microondas'),
        ('horno', 'Horno'),
        ('plancha', 'Plancha'),
        ('calentador', 'Calentador de Agua'),
        ('ventilador', 'Ventilador'),
        ('licuadora', 'Licuadora'),
        ('cafetera', 'Cafetera'),
        ('tostadora', 'Tostadora'),
        ('secadora', 'Secadora'),
        ('aspiradora', 'Aspiradora'),
        ('router', 'Router/Módem'),
        ('consola', 'Consola de Videojuegos'),
        ('otro', 'Otro')
    ]
    
    nombre = StringField(
        'Nombre del Dispositivo',
        validators=[
            DataRequired(message='El nombre del dispositivo es obligatorio'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
        ],
        render_kw={'placeholder': 'Ej: Refrigerador Samsung'}
    )
    
    tipo = SelectField(
        'Tipo de Dispositivo',
        choices=TIPOS_DISPOSITIVOS,
        validators=[DataRequired(message='Debe seleccionar un tipo de dispositivo')]
    )
    
    potencia_watts = FloatField(
        'Potencia (Watts)',
        validators=[
            DataRequired(message='La potencia es obligatoria'),
            NumberRange(min=1, max=10000, message='La potencia debe estar entre 1 y 10,000 W')
        ],
        render_kw={'placeholder': 'Ej: 150'}
    )
    
    horas_uso_dia = FloatField(
        'Horas de Uso Diario',
        validators=[
            DataRequired(message='Las horas de uso son obligatorias'),
            NumberRange(min=0.1, max=24, message='Las horas deben estar entre 0.1 y 24')
        ],
        render_kw={'placeholder': 'Ej: 8.5'}
    )
    
    submit = SubmitField('Guardar Dispositivo')
    
    def validate_potencia_watts(self, field):
        """Validación personalizada para potencia según tipo de dispositivo"""
        rangos_tipicos = {
            'refrigerador': (100, 800),
            'lavadora': (300, 1500),
            'televisor': (50, 400),
            'tv': (50, 400),
            'computadora': (200, 600),
            'laptop': (30, 100),
            'aire_acondicionado': (1000, 5000),
            'microondas': (600, 1500),
            'horno': (2000, 5000),
            'plancha': (800, 2000),
            'calentador': (1500, 5000),
            'ventilador': (50, 150),
        }
        
        if self.tipo.data in rangos_tipicos:
            min_val, max_val = rangos_tipicos[self.tipo.data]
            if field.data < min_val or field.data > max_val:
                raise ValidationError(
                    f'La potencia típica para {self.tipo.data} está entre {min_val}W y {max_val}W. '
                    f'Verifique la especificación del fabricante.'
                )


class ConsumoBimestralForm(FlaskForm):
    """Formulario para registrar consumo bimestral"""
    
    periodo_inicio = DateField(
        'Fecha de Inicio del Periodo',
        validators=[DataRequired(message='La fecha de inicio es obligatoria')],
        format='%Y-%m-%d'
    )
    
    periodo_fin = DateField(
        'Fecha de Fin del Periodo',
        validators=[DataRequired(message='La fecha de fin es obligatoria')],
        format='%Y-%m-%d'
    )
    
    consumo_kwh = FloatField(
        'Consumo Total (kWh)',
        validators=[
            DataRequired(message='El consumo es obligatorio'),
            NumberRange(min=0.1, max=100000, message='El consumo debe ser mayor a 0')
        ],
        render_kw={'placeholder': 'Ej: 450.5'}
    )
    
    costo_total = FloatField(
        'Costo Total (MXN)',
        validators=[
            DataRequired(message='El costo es obligatorio'),
            NumberRange(min=0.1, max=1000000, message='El costo debe ser mayor a 0')
        ],
        render_kw={'placeholder': 'Ej: 1250.00'}
    )
    
    submit = SubmitField('Registrar Consumo')
    
    def validate_periodo_fin(self, field):
        """Valida que la fecha de fin sea posterior a la de inicio"""
        if self.periodo_inicio.data and field.data:
            if field.data <= self.periodo_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')
            
           
            diferencia = (field.data - self.periodo_inicio.data).days
            if diferencia < 50 or diferencia > 70:
                raise ValidationError(
                    f'El periodo debe ser aproximadamente bimestral (60 días). '
                    f'El periodo ingresado es de {diferencia} días'
                )
    
    def validate_consumo_kwh(self, field):
        """Valida que el consumo sea razonable para un hogar"""
        if field.data:
            # Consumo típico residencial en México: 150-1000 kWh bimestrales
            if field.data < 50:
                raise ValidationError(
                    'El consumo parece muy bajo para un hogar. Verifique el valor.'
                )
            elif field.data > 2000:
                raise ValidationError(
                    'El consumo parece muy alto para un hogar residencial. Verifique el valor.'
                )


class GenerarReporteForm(FlaskForm):
    """Formulario para generar reportes"""
    
    OPCIONES_AHORRO = [
        ('0.15', '15% - Conservador'),
        ('0.20', '20% - Moderado (Recomendado)'),
        ('0.25', '25% - Agresivo'),
        ('0.30', '30% - Muy Agresivo')
    ]
    
    objetivo_ahorro = SelectField(
        'Objetivo de Ahorro',
        choices=OPCIONES_AHORRO,
        default='0.20',
        validators=[DataRequired()]
    )
    
    incluir_graficas = SelectField(
        'Incluir Gráficas en PDF',
        choices=[('si', 'Sí'), ('no', 'No')],
        default='si'
    )
    
    submit = SubmitField('Generar Reporte')


class ConfiguracionSistemaForm(FlaskForm):
    """Formulario para configuración del sistema"""
    
    tarifa_kwh = FloatField(
        'Tarifa por kWh (MXN)',
        validators=[
            DataRequired(message='La tarifa es obligatoria'),
            NumberRange(min=0.1, max=10, message='La tarifa debe estar entre 0.1 y 10 MXN')
        ],
        default=1.5,
        render_kw={'placeholder': 'Ej: 1.5'}
    )
    
    dias_proyeccion = FloatField(
        'Días para Proyección',
        validators=[
            DataRequired(message='Los días de proyección son obligatorios'),
            NumberRange(min=7, max=365, message='Los días deben estar entre 7 y 365')
        ],
        default=30,
        render_kw={'placeholder': 'Ej: 30'}
    )
    
    submit = SubmitField('Guardar Configuración')


class BusquedaUsuarioForm(FlaskForm):
    """Formulario para buscar usuarios"""
    
    nombre_usuario = StringField(
        'Nombre de Usuario',
        validators=[Length(max=100)],
        render_kw={'placeholder': 'Buscar usuario...'}
    )
    
    submit = SubmitField('Buscar')