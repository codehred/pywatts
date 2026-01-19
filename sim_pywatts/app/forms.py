from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError, EqualTo
from datetime import datetime

DISPOSITIVOS_DATA = {
    'refrigerador': ('Refrigerador', 250),
    'lavadora': ('Lavadora', 500),
    'televisor': ('Televisión / Smart TV', 100),
    'microondas': ('Horno de Microondas', 1200),
    'computadora': ('Computadora de Escritorio', 200),
    'laptop': ('Laptop / Portátil', 50),
    'aire_acondicionado': ('Aire Acondicionado (Minisplit)', 1500),
    'ventilador': ('Ventilador de Pedestal', 70),
    'foco_led': ('Foco LED', 10),
    'foco_incandescente': ('Foco Incandescente', 60),
    'plancha': ('Plancha de Ropa', 1000),
    'cafetera': ('Cafetera', 800),
    'consola': ('Consola de Videojuegos', 150),
    'modem': ('Módem / Router', 10),
    'horno': ('Horno Eléctrico', 3000),
    'calentador': ('Calentador de Agua', 2500),
    'licuadora': ('Licuadora', 400),
    'tostadora': ('Tostadora', 900),
    'secadora': ('Secadora de Ropa', 3000),
    'aspiradora': ('Aspiradora', 1400),
    'otro': ('Otro Dispositivo', 100)
}

class RegistroUsuarioForm(FlaskForm):
    nombre_usuario = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
        ],
        render_kw={'placeholder': 'Ingrese su nombre de usuario'}
    )

    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={'placeholder': 'Ingrese su contraseña'}
    )
    
    confirm_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Confirme su contraseña'),
            EqualTo('password', message='Las contraseñas deben coincidir')
        ],
        render_kw={'placeholder': 'Repita su contraseña'}
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
        choices=[('', 'Seleccione un tipo')] + [(k, v[0]) for k, v in DISPOSITIVOS_DATA.items()],
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
        
        rangos_tipicos = {
            'refrigerador': (100, 800),
            'lavadora': (300, 1500),
            'televisor': (30, 400),
            'computadora': (100, 800),
            'laptop': (30, 150),
            'aire_acondicionado': (800, 5000),
            'microondas': (600, 1500),
            'horno': (1000, 5000),
            'plancha': (800, 2500),
            'calentador': (1000, 5000),
            'ventilador': (30, 150),
            'foco_led': (1, 50),
            'foco_incandescente': (20, 150),
            'cafetera': (500, 1500),
            'modem': (5, 30),
            'consola': (50, 400),
            'licuadora': (200, 1000),
            'tostadora': (500, 1500),
            'secadora': (1000, 4000),
            'aspiradora': (500, 2000),
            'otro': (1, 10000)
        }
        
        if self.tipo.data in rangos_tipicos:
            min_val, max_val = rangos_tipicos[self.tipo.data]
            if field.data < min_val or field.data > max_val:
                raise ValidationError(
                    f'La potencia típica para este dispositivo suele estar entre {min_val}W y {max_val}W. '
                    f'Verifica la etiqueta del fabricante.'
                )


class ConsumoBimestralForm(FlaskForm):
    
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
            
            # -----------------------------------------------
            # diferencia = (field.data - self.periodo_inicio.data).days
            # if diferencia < 50 or diferencia > 70:
            #    raise ValidationError(
            #        f'El periodo debe ser aproximadamente bimestral (60 días). '
            #        f'El periodo ingresado es de {diferencia} días'
            #    )
            # ---------------------------------------------
    def validate_consumo_kwh(self, field):
        if field.data:
            if field.data < 10: 
                raise ValidationError('El consumo parece muy bajo. Verifique el valor.')
            elif field.data > 5000:
                raise ValidationError('El consumo parece excesivo para un hogar residencial.')


class GenerarReporteForm(FlaskForm):
    
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

AgregarDispositivoForm = DispositivoForm