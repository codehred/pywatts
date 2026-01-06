import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Clave secreta para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pywatts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Cambiar a True para debug SQL
    
    # Carpetas
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'exports', 'reports')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Conf archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'csv'}
    
    # sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    ###########
    # Configuración de WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Sin límite de tiempo para tokens CSRF
    ############
    
    # flask
    TESTING = False
    DEBUG = False
    
    #####################
    # Tarifas eléctricas (CFE - México)
    TARIFA_BASE = 0.82  # MXN por kWh (tarifa 1)
    TARIFA_INTERMEDIA = 1.05  # MXN por kWh (tarifa 1A)
    TARIFA_EXCEDENTE = 2.85  # MXN por kWh (tarifa DAC)
    
    # Límites de consumo para tarifas escalonadas (kWh bimestrales)
    LIMITE_TARIFA_1 = 150
    LIMITE_TARIFA_1A = 280
    LIMITE_TARIFA_1B = 400
    LIMITE_TARIFA_1C = 600
    
    # Configuración de optimización
    OBJETIVO_AHORRO_DEFAULT = 0.20  # 20%
    OBJETIVO_AHORRO_MIN = 0.10  # 10%
    OBJETIVO_AHORRO_MAX = 0.40  # 40%
    
    # Proyección de consumo
    DIAS_PROYECCION_DEFAULT = 30
    DIAS_PROYECCION_MIN = 7
    DIAS_PROYECCION_MAX = 365
    
    # Configuración de gráficas
    GRAFICAS_DPI = 100
    GRAFICAS_FORMATO = 'png'
    
    # Configuración de PDF
    PDF_PAGESIZE = 'letter'  # 'letter' o 'A4'
    PDF_MARGIN = 72  # puntos (1 inch = 72 points)
    
    # Factores ambientales
    CO2_POR_KWH = 0.527  # kg CO2 por kWh (promedio México)
    ARBOLES_POR_KG_CO2 = 0.06  # Árboles necesarios para absorber 1 kg CO2/año
    
    # Validación de dispositivos - Rangos típicos de potencia (Watts)
    RANGOS_POTENCIA = {
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
        'licuadora': (300, 1000),
        'cafetera': (500, 1200),
        'tostadora': (800, 1500),
        'secadora': (2000, 5000),
        'aspiradora': (1000, 2000),
        'router': (10, 50),
        'consola': (100, 200)
    }
    
    # Horas típicas de uso diario
    HORAS_USO_TIPICAS = {
        'refrigerador': (20, 24),
        'lavadora': (0.5, 2),
        'televisor': (3, 8),
        'tv': (3, 8),
        'computadora': (2, 12),
        'laptop': (2, 10),
        'aire_acondicionado': (2, 12),
        'microondas': (0.2, 1),
        'horno': (0.5, 2),
        'plancha': (0.5, 2),
        'calentador': (1, 6),
        'ventilador': (2, 12)
    }


    #########################
   
    MENSAJE_BIENVENIDA = "Bienvenido a PyWatts - Sistema de Optimización de Consumo Energético"
    MENSAJE_REGISTRO_EXITOSO = "Registro completado exitosamente"
    MENSAJE_ERROR_GENERAL = "Ha ocurrido un error. Por favor, intente nuevamente"
    
    @staticmethod
    def init_app(app):
        """Inicialización de la aplicación con configuraciones adicionales"""
        
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DATA_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
   
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Seguridad adicional en producción
    SESSION_COOKIE_SECURE = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        
        pass


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Obtiene la configuración apropiada
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
                    Si es None, usa la variable de entorno FLASK_ENV
    
    Returns:
        Clase de configuración apropiada
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, DevelopmentConfig)