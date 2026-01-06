import os
import sys

# PRIMERO: Buscar y eliminar TODAS las bases de datos de prueba
print("🔍 Buscando bases de datos antiguas...")

# Buscar en la carpeta actual y subcarpetas
for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'test_pywatts.db':
            ruta_completa = os.path.join(root, file)
            print(f"   Encontrada: {ruta_completa}")
            try:
                os.remove(ruta_completa)
                print(f"   ✓ Eliminada!")
            except Exception as e:
                print(f"   ✗ Error: {e}")

print("\n🚀 Ahora ejecutando pruebas...\n")

# Ahora importar y ejecutar
from flask import Flask
from models import db, Usuario, Dispositivo
from services.calculations import OptimizadorEnergetico
from services.recommendations import GeneradorRecomendaciones
from services.charts import GeneradorGraficas
from services.pdf_generator import GeneradorPDF
from datetime import datetime

# Configurar Flask
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'test_pywatts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

print(f"📁 Base de datos se creará en: {DB_PATH}\n")

# Crear BD limpia
with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos creada\n")
    
    # Crear usuario
    usuario = Usuario(
        nombre_usuario=f"usuario_test_{datetime.now().strftime('%H%M%S')}",
        domicilio="Calle Test 123"
    )
    db.session.add(usuario)
    db.session.commit()
    print(f"✅ Usuario creado: {usuario.nombre_usuario}\n")
    
    # Crear dispositivos
    dispositivos_data = [
        {'nombre': 'Refrigerador', 'tipo': 'refrigerador', 'potencia_watts': 250, 'horas_uso_dia': 24},
        {'nombre': 'TV', 'tipo': 'televisor', 'potencia_watts': 120, 'horas_uso_dia': 8},
        {'nombre': 'Aire Acondicionado', 'tipo': 'aire_acondicionado', 'potencia_watts': 2000, 'horas_uso_dia': 8},
    ]
    
    for disp_data in dispositivos_data:
        dispositivo = Dispositivo(usuario_id=usuario.id, **disp_data)
        db.session.add(dispositivo)
    
    db.session.commit()
    print(f"✅ {len(dispositivos_data)} dispositivos creados\n")
    
    # Optimización
    print("🧮 Ejecutando optimización...")
    dispositivos = usuario.dispositivos
    optimizador = OptimizadorEnergetico(dispositivos, 1.5)
    consumo_total = optimizador.consumo_total_actual()
    configuracion_optima = optimizador.encontrar_punto_optimo()
    ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
    
    print(f"   Consumo actual: {ahorro_total['consumo_actual_kwh']:.2f} kWh")
    print(f"   Consumo optimizado: {ahorro_total['consumo_optimizado_kwh']:.2f} kWh")
    print(f"   Ahorro: ${ahorro_total['ahorro_pesos']:.2f} MXN")
    print(f"   Porcentaje: {ahorro_total['porcentaje_ahorro']:.1f}%\n")
    
    # Recomendaciones
    print("💡 Generando recomendaciones...")
    gen_rec = GeneradorRecomendaciones(dispositivos, configuracion_optima)
    recomendaciones = gen_rec.generar_recomendaciones_personalizadas()
    print(f"   Críticas: {len(recomendaciones['criticas'])}")
    print(f"   Importantes: {len(recomendaciones['importantes'])}")
    print(f"   Generales: {len(recomendaciones['generales'])}\n")
    
    # Gráficas
    print("📊 Generando gráficas...")
    gen_graficas = GeneradorGraficas()
    consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
    grafica_barras = gen_graficas.grafica_consumo_por_dispositivo(consumo_por_dispositivo)
    print(f"   ✓ Gráfica de barras: {len(grafica_barras)} bytes\n")
    
    # PDF
    print("📄 Generando PDF...")
    os.makedirs('exports/reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ruta_pdf = f'exports/reports/test_final_{timestamp}.pdf'
    
    generador_pdf = GeneradorPDF(
        usuario,
        consumo_por_dispositivo,
        configuracion_optima,
        ahorro_total,
        recomendaciones
    )
    generador_pdf.generar_reporte(ruta_pdf)
    
    tamaño = os.path.getsize(ruta_pdf) / 1024
    print(f"   ✓ PDF generado: {ruta_pdf}")
    print(f"   ✓ Tamaño: {tamaño:.2f} KB\n")

print("="*70)
print("✅ ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
print("="*70)
print(f"\n📁 Archivos generados:")
print(f"   • Base de datos: {DB_PATH}")
print(f"   • PDF: {ruta_pdf}")
print(f"\n🎉 ¡TODO FUNCIONA PERFECTAMENTE!")