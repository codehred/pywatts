from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    domicilio = db.Column(db.String(200), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    dispositivos = db.relationship('Dispositivo', backref='usuario', lazy=True, cascade='all, delete-orphan')
    consumos = db.relationship('ConsumoBimestral', backref='usuario', lazy=True, cascade='all, delete-orphan')
    reportes = db.relationship('Reporte', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'


class Dispositivo(db.Model):
    __tablename__ = 'dispositivos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # refrigerador, tv, lavadora, etc.
    potencia_watts = db.Column(db.Float, nullable=False)  # Potencia en watts
    horas_uso_dia = db.Column(db.Float, nullable=False)  # Horas promedio de uso al día
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def consumo_diario_kwh(self):
        """Calcula el consumo diario en kWh"""
        return (self.potencia_watts * self.horas_uso_dia) / 1000
    
    def consumo_mensual_kwh(self):
        """Calcula el consumo mensual en kWh"""
        return self.consumo_diario_kwh() * 30
    
    def consumo_bimestral_kwh(self):
        """Calcula el consumo bimestral en kWh"""
        return self.consumo_mensual_kwh() * 2
    
    def __repr__(self):
        return f'<Dispositivo {self.nombre} - {self.potencia_watts}W>'


class ConsumoBimestral(db.Model):
    __tablename__ = 'consumos_bimestrales'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    periodo_inicio = db.Column(db.Date, nullable=False)
    periodo_fin = db.Column(db.Date, nullable=False)
    consumo_kwh = db.Column(db.Float, nullable=False)  
    costo_total = db.Column(db.Float, nullable=False)  
    fecha_registro = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc)
)
    
    def costo_por_kwh(self):
        """Calcula el costo promedio por kWh"""
        if self.consumo_kwh > 0:
            return self.costo_total / self.consumo_kwh
        return 0
    
    def __repr__(self):
        return f'<ConsumoBimestral {self.consumo_kwh} kWh - ${self.costo_total}>'


class Reporte(db.Model):
    __tablename__ = 'reportes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    consumo_actual_kwh = db.Column(db.Float, nullable=False)
    consumo_optimizado_kwh = db.Column(db.Float, nullable=False)
    ahorro_kwh = db.Column(db.Float, nullable=False)
    ahorro_pesos = db.Column(db.Float, nullable=False)
    archivo_pdf = db.Column(db.String(200))  # ruta al archivo PDF generado
    
    def porcentaje_ahorro(self):
        """Calcula el porcentaje de ahorro"""
        if self.consumo_actual_kwh > 0:
            return (self.ahorro_kwh / self.consumo_actual_kwh) * 100
        return 0
    
    def __repr__(self):
        return f'<Reporte {self.fecha_generacion} - Ahorro: {self.ahorro_kwh} kWh>'