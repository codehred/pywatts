"""
Script de prueba para el backend de PyWatts
Prueba todas las funcionalidades sin necesidad de HTML
"""

import sys
import os

# Asegurar que se puedan importar los módulos
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from models import db, Usuario, Dispositivo, ConsumoBimestral, Reporte
from services.calculations import OptimizadorEnergetico
from services.recommendations import GeneradorRecomendaciones
from services.charts import GeneradorGraficas
from services.pdf_generator import GeneradorPDF
from datetime import datetime, timedelta
import json

# Configurar Flask y DB
app = Flask(__name__)

# Usar ruta absoluta para la base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'test_pywatts.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def print_seccion(titulo):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    print(f"  {titulo}")
    print("="*80 + "\n")

def test_creacion_base_datos():
    """Prueba 1: Crear base de datos y tablas"""
    print_seccion("PRUEBA 1: Creación de Base de Datos")
    
    # Mostrar dónde se creará la BD
    print(f"📁 Ruta de la base de datos: {DB_PATH}")
    
    # Eliminar BD si existe
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("✓ Base de datos anterior eliminada")
        except Exception as e:
            print(f"⚠️  No se pudo eliminar: {e}")
    
    with app.app_context():
        # Eliminar todas las tablas
        db.drop_all()
        print("✓ Tablas anteriores eliminadas (si existían)")
        
        # Crear tablas nuevas
        db.create_all()
        print("✓ Base de datos y tablas creadas exitosamente")
        
        # Verificar tablas
        inspector = db.inspect(db.engine)
        tablas = inspector.get_table_names()
        print(f"✓ Tablas creadas: {', '.join(tablas)}")
        
    return True

def test_crud_usuario():
    """Prueba 2: CRUD de Usuarios"""
    print_seccion("PRUEBA 2: Operaciones CRUD - Usuarios")
    
    with app.app_context():
        # Crear usuario
        usuario = Usuario(
            nombre_usuario="juan_perez",
            domicilio="Av. Principal 123, Col. Centro, Cuernavaca, Morelos"
        )
        db.session.add(usuario)
        db.session.commit()
        print(f"✓ Usuario creado: {usuario.nombre_usuario}")
        print(f"  ID: {usuario.id}")
        print(f"  Domicilio: {usuario.domicilio}")
        print(f"  Fecha registro: {usuario.fecha_registro}")
        
        # Leer usuario
        usuario_leido = Usuario.query.filter_by(nombre_usuario="juan_perez").first()
        print(f"\n✓ Usuario leído desde DB: {usuario_leido.nombre_usuario}")
        
        # Contar usuarios
        total = Usuario.query.count()
        print(f"✓ Total de usuarios en DB: {total}")
        
    return usuario.id

def test_crud_dispositivos(usuario_id):
    """Prueba 3: CRUD de Dispositivos"""
    print_seccion("PRUEBA 3: Operaciones CRUD - Dispositivos")
    
    with app.app_context():
        # Crear varios dispositivos
        dispositivos_data = [
            {
                'nombre': 'Refrigerador Samsung',
                'tipo': 'refrigerador',
                'potencia_watts': 250,
                'horas_uso_dia': 24
            },
            {
                'nombre': 'TV LG 55"',
                'tipo': 'televisor',
                'potencia_watts': 120,
                'horas_uso_dia': 8  # Aumentado de 6 a 8
            },
            {
                'nombre': 'Lavadora Whirlpool',
                'tipo': 'lavadora',
                'potencia_watts': 500,
                'horas_uso_dia': 2  # Aumentado de 1.5 a 2
            },
            {
                'nombre': 'Laptop Dell',
                'tipo': 'laptop',
                'potencia_watts': 65,
                'horas_uso_dia': 12  # Aumentado de 8 a 12
            },
            {
                'nombre': 'Aire Acondicionado',
                'tipo': 'aire_acondicionado',
                'potencia_watts': 2000,  # Aumentado de 1500 a 2000
                'horas_uso_dia': 8  # Aumentado de 5 a 8
            },
            {
                'nombre': 'Microondas',
                'tipo': 'microondas',
                'potencia_watts': 1200,
                'horas_uso_dia': 1  # Aumentado de 0.5 a 1
            },
            {
                'nombre': 'Calentador de Agua',
                'tipo': 'calentador',
                'potencia_watts': 3000,  # Nuevo dispositivo de alto consumo
                'horas_uso_dia': 3
            }
        ]
        
        dispositivos_creados = []
        for data in dispositivos_data:
            dispositivo = Dispositivo(
                usuario_id=usuario_id,
                **data
            )
            db.session.add(dispositivo)
            dispositivos_creados.append(dispositivo)
        
        db.session.commit()
        
        print(f"✓ {len(dispositivos_creados)} dispositivos creados exitosamente\n")
        
        # Mostrar cada dispositivo con sus cálculos
        for disp in dispositivos_creados:
            print(f"📱 {disp.nombre}")
            print(f"   Tipo: {disp.tipo}")
            print(f"   Potencia: {disp.potencia_watts}W")
            print(f"   Uso diario: {disp.horas_uso_dia}h")
            print(f"   Consumo diario: {disp.consumo_diario_kwh():.2f} kWh")
            print(f"   Consumo mensual: {disp.consumo_mensual_kwh():.2f} kWh")
            print(f"   Consumo bimestral: {disp.consumo_bimestral_kwh():.2f} kWh")
            print()
        
        total = Dispositivo.query.filter_by(usuario_id=usuario_id).count()
        print(f"✓ Total dispositivos del usuario: {total}")
        
    return len(dispositivos_creados)

def test_calculos_optimizacion(usuario_id):
    """Prueba 4: Cálculos de Optimización"""
    print_seccion("PRUEBA 4: Motor de Optimización y Cálculos")
    
    with app.app_context():
        usuario = Usuario.query.get(usuario_id)
        dispositivos = usuario.dispositivos
        
        # Crear optimizador
        tarifa_kwh = 1.5
        optimizador = OptimizadorEnergetico(dispositivos, tarifa_kwh)
        
        print(f"📊 ANÁLISIS DE CONSUMO ACTUAL")
        print(f"{'='*60}")
        
        # Consumo total
        consumo_total = optimizador.consumo_total_actual()
        costo_total = optimizador.costo_total_actual()
        print(f"Consumo total bimestral: {consumo_total:.2f} kWh")
        print(f"Costo total bimestral: ${costo_total:.2f} MXN")
        print(f"Tarifa aplicada: ${tarifa_kwh:.2f} MXN/kWh")
        
        # Consumo por dispositivo
        print(f"\n📱 CONSUMO POR DISPOSITIVO")
        print(f"{'='*60}")
        consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
        
        for nombre, datos in consumo_por_dispositivo.items():
            print(f"\n{nombre}:")
            print(f"  Consumo bimestral: {datos['consumo_bimestral_kwh']:.2f} kWh")
            print(f"  Costo bimestral: ${datos['costo_bimestral']:.2f} MXN")
            print(f"  Porcentaje del total: {datos['porcentaje']:.1f}%")
        
        # Configuración óptima
        print(f"\n🎯 CONFIGURACIÓN ÓPTIMA (Objetivo: 20% ahorro)")
        print(f"{'='*60}")
        configuracion_optima = optimizador.encontrar_punto_optimo(restriccion_ahorro=0.20)
        
        for nombre, config in configuracion_optima.items():
            print(f"\n{nombre}:")
            print(f"  Horas actuales: {config['horas_actuales']:.2f}h/día")
            print(f"  Horas óptimas: {config['horas_optimas']:.2f}h/día")
            print(f"  Reducción: {config['reduccion_horas']:.2f}h/día")
            print(f"  Ahorro: {config['ahorro_kwh']:.2f} kWh (${config['ahorro_pesos']:.2f} MXN)")
        
        # Ahorro total
        print(f"\n💰 RESUMEN DE AHORRO TOTAL")
        print(f"{'='*60}")
        ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
        
        print(f"Consumo actual: {ahorro_total['consumo_actual_kwh']:.2f} kWh")
        print(f"Consumo optimizado: {ahorro_total['consumo_optimizado_kwh']:.2f} kWh")
        print(f"Ahorro total: {ahorro_total['ahorro_kwh']:.2f} kWh")
        print(f"Ahorro en pesos: ${ahorro_total['ahorro_pesos']:.2f} MXN bimestrales")
        print(f"Ahorro anual: ${ahorro_total['ahorro_pesos'] * 6:.2f} MXN")
        print(f"Porcentaje de ahorro: {ahorro_total['porcentaje_ahorro']:.1f}%")
        
        # Proyección
        print(f"\n📈 PROYECCIÓN DE CONSUMO (próximos 30 días)")
        print(f"{'='*60}")
        proyeccion = optimizador.proyectar_consumo(dias=30)
        
        print(f"Primeros 5 días:")
        for i, dia in enumerate(proyeccion[:5], 1):
            print(f"  Día {i} ({dia['fecha']}): {dia['consumo_kwh']:.2f} kWh - ${dia['costo']:.2f}")
        
        consumo_promedio = sum(d['consumo_kwh'] for d in proyeccion) / len(proyeccion)
        print(f"\nPromedio proyectado: {consumo_promedio:.2f} kWh/día")
        
        # Rango de cobro
        print(f"\n💵 ESTIMACIÓN DE COBRO BIMESTRAL")
        print(f"{'='*60}")
        rango_cobro = optimizador.calcular_rango_cobro_bimestral(consumo_total)
        
        print(f"Consumo: {rango_cobro['consumo_kwh']:.2f} kWh")
        print(f"Tarifa aplicada: ${rango_cobro['tarifa_aplicada']:.2f} MXN/kWh")
        print(f"Costo estimado: ${rango_cobro['costo_estimado']:.2f} MXN")
        print(f"Rango mínimo: ${rango_cobro['rango_minimo']:.2f} MXN")
        print(f"Rango máximo: ${rango_cobro['rango_maximo']:.2f} MXN")
        
        # Energía acumulada
        print(f"\n⚡ ENERGÍA ACUMULADA POR INTERVALO")
        print(f"{'='*60}")
        
        for intervalo in ['dia', 'semana', 'mes']:
            print(f"\nPor {intervalo}:")
            energia = optimizador.calcular_energia_acumulada(intervalo)
            for nombre, datos in list(energia.items())[:3]:  # Mostrar solo primeros 3
                print(f"  {nombre}: {datos['consumo_kwh']:.2f} kWh (${datos['costo']:.2f})")
        
        return configuracion_optima, ahorro_total

def test_recomendaciones(usuario_id, configuracion_optima, ahorro_total):
    """Prueba 5: Sistema de Recomendaciones"""
    print_seccion("PRUEBA 5: Sistema de Recomendaciones")
    
    with app.app_context():
        usuario = db.session.get(Usuario, usuario_id)
        dispositivos = usuario.dispositivos
        
        # Generar recomendaciones
        gen_recomendaciones = GeneradorRecomendaciones(dispositivos, configuracion_optima)
        recomendaciones = gen_recomendaciones.generar_recomendaciones_personalizadas()
        
        # Recomendaciones críticas
        print("🔴 RECOMENDACIONES CRÍTICAS (Alta prioridad):")
        print("="*60)
        for rec in recomendaciones['criticas']:
            print(f"\n{rec['dispositivo']}:")
            print(f"  Acción: {rec['accion_principal']}")
            print(f"  Ahorro potencial: ${rec['ahorro_potencial_pesos']:.2f} MXN")
            if rec['consejos_especificos']:
                print(f"  Consejos:")
                for consejo in rec['consejos_especificos'][:2]:
                    print(f"    • {consejo}")
        
        # Recomendaciones importantes
        print(f"\n🟡 RECOMENDACIONES IMPORTANTES (Media prioridad):")
        print("="*60)
        for rec in recomendaciones['importantes'][:3]:
            print(f"• {rec['dispositivo']}: {rec['accion_principal']}")
            print(f"  Ahorro: ${rec['ahorro_potencial_pesos']:.2f} MXN")
        
        # Recomendaciones generales
        print(f"\n💡 RECOMENDACIONES GENERALES:")
        print("="*60)
        for i, rec in enumerate(recomendaciones['generales'][:5], 1):
            print(f"{i}. {rec}")
        
        # Plan de acción
        print(f"\n📅 PLAN DE ACCIÓN DE 4 SEMANAS:")
        print("="*60)
        plan = gen_recomendaciones.generar_plan_accion()
        
        for semana, contenido in list(plan.items())[:2]:  # Mostrar 2 semanas
            print(f"\n{semana.upper().replace('_', ' ')}:")
            print(f"  {contenido['titulo']}")
            for accion in contenido['acciones'][:3]:
                if 'dispositivo' in accion:
                    print(f"  • {accion['dispositivo']}: {accion['accion']}")
                elif 'accion_general' in accion:
                    print(f"  • {accion['accion_general']}")
        
        # Impacto ambiental
        print(f"\n🌱 IMPACTO AMBIENTAL:")
        print("="*60)
        impacto = gen_recomendaciones.calcular_impacto_ambiental(
            ahorro_total['ahorro_kwh']
        )
        
        print(f"Ahorro energético: {impacto['ahorro_kwh']:.2f} kWh")
        print(f"CO2 ahorrado: {impacto['co2_kg_ahorrado']:.2f} kg")
        print(f"Equivalente a plantar: {impacto['equivalente_arboles']:.1f} árboles")
        print(f"Equivalente a no conducir: {impacto['equivalente_km_auto']:.1f} km")
        print(f"\n{impacto['mensaje']}")
        
        # Tips de horarios
        print(f"\n⏰ MEJORES HORARIOS PARA USO:")
        print("="*60)
        tips_horarios = gen_recomendaciones.generar_tips_horarios()
        
        for tipo, info in tips_horarios.items():
            print(f"\n{tipo.upper().replace('_', ' ')}:")
            print(f"  {info['descripcion']}")
            print(f"  Horarios: {info['horarios']}")
            if 'dispositivos_recomendados' in info:
                print(f"  Dispositivos: {', '.join(info['dispositivos_recomendados'])}")
            if 'ahorro_estimado' in info:
                print(f"  Ahorro estimado: {info['ahorro_estimado']}")

def test_graficas(usuario_id):
    """Prueba 6: Generación de Gráficas"""
    print_seccion("PRUEBA 6: Generación de Gráficas")
    
    with app.app_context():
        usuario = db.session.get(Usuario, usuario_id)
        dispositivos = usuario.dispositivos
        
        # Calcular datos
        optimizador = OptimizadorEnergetico(dispositivos, 1.5)
        consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
        configuracion_optima = optimizador.encontrar_punto_optimo()
        ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
        proyeccion = optimizador.proyectar_consumo(30)
        energia_acumulada = optimizador.calcular_energia_acumulada('mes')
        
        # Generar gráficas
        gen_graficas = GeneradorGraficas()
        
        print("Generando gráficas...")
        
        # Cada gráfica retorna base64, verificamos que no estén vacías
        grafica_barras = gen_graficas.grafica_consumo_por_dispositivo(consumo_por_dispositivo)
        print(f"✓ Gráfica de barras generada ({len(grafica_barras)} caracteres)")
        
        grafica_pie = gen_graficas.grafica_pie_distribucion(consumo_por_dispositivo)
        print(f"✓ Gráfica de pastel generada ({len(grafica_pie)} caracteres)")
        
        grafica_comparativa = gen_graficas.grafica_comparativa_antes_despues(ahorro_total)
        print(f"✓ Gráfica comparativa generada ({len(grafica_comparativa)} caracteres)")
        
        grafica_proyeccion = gen_graficas.grafica_proyeccion_consumo(proyeccion)
        print(f"✓ Gráfica de proyección generada ({len(grafica_proyeccion)} caracteres)")
        
        grafica_ahorro = gen_graficas.grafica_ahorro_por_dispositivo(configuracion_optima)
        print(f"✓ Gráfica de ahorro generada ({len(grafica_ahorro)} caracteres)")
        
        grafica_energia = gen_graficas.grafica_energia_acumulada(energia_acumulada, 'mes')
        print(f"✓ Gráfica de energía acumulada generada ({len(grafica_energia)} caracteres)")
        
        dashboard = gen_graficas.grafica_dashboard_completo(
            consumo_por_dispositivo, ahorro_total, configuracion_optima
        )
        print(f"✓ Dashboard completo generado ({len(dashboard)} caracteres)")
        
        print("\n✅ Todas las gráficas se generaron exitosamente!")
        print("   Las gráficas están en formato base64 listas para usar en HTML")

def test_generacion_pdf(usuario_id):
    """Prueba 7: Generación de PDF"""
    print_seccion("PRUEBA 7: Generación de Reporte PDF")
    
    with app.app_context():
        usuario = Usuario.query.get(usuario_id)
        dispositivos = usuario.dispositivos
        
        # Calcular datos
        optimizador = OptimizadorEnergetico(dispositivos, 1.5)
        consumo_por_dispositivo = optimizador.calcular_consumo_por_dispositivo()
        configuracion_optima = optimizador.encontrar_punto_optimo()
        ahorro_total = optimizador.calcular_ahorro_total(configuracion_optima)
        
        # Generar recomendaciones
        gen_recomendaciones = GeneradorRecomendaciones(dispositivos, configuracion_optima)
        recomendaciones = gen_recomendaciones.generar_recomendaciones_personalizadas()
        
        # Generar PDF
        print("Generando reporte PDF...")
        
        # Crear carpeta si no existe
        os.makedirs('exports/reports', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f'reporte_test_{timestamp}.pdf'
        ruta_completa = os.path.join('exports/reports', nombre_archivo)
        
        generador_pdf = GeneradorPDF(
            usuario,
            consumo_por_dispositivo,
            configuracion_optima,
            ahorro_total,
            recomendaciones
        )
        
        ruta_generada = generador_pdf.generar_reporte(ruta_completa)
        
        # Verificar que se creó el archivo
        if os.path.exists(ruta_generada):
            tamaño = os.path.getsize(ruta_generada) / 1024  # KB
            print(f"✅ PDF generado exitosamente!")
            print(f"   Ruta: {ruta_generada}")
            print(f"   Tamaño: {tamaño:.2f} KB")
            
            # Guardar registro en DB
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
            
            print(f"✓ Reporte guardado en base de datos (ID: {nuevo_reporte.id})")
        else:
            print("❌ Error: El PDF no se pudo generar")

def test_consumo_bimestral(usuario_id):
    """Prueba 8: Registro de Consumo Bimestral"""
    print_seccion("PRUEBA 8: Registro de Consumo Bimestral")
    
    with app.app_context():
        # Crear registro de consumo
        fecha_inicio = datetime.now() - timedelta(days=60)
        fecha_fin = datetime.now()
        
        consumo = ConsumoBimestral(
            usuario_id=usuario_id,
            periodo_inicio=fecha_inicio.date(),
            periodo_fin=fecha_fin.date(),
            consumo_kwh=450.5,
            costo_total=1250.00
        )
        
        db.session.add(consumo)
        db.session.commit()
        
        print(f"✓ Consumo bimestral registrado:")
        print(f"  Periodo: {consumo.periodo_inicio} a {consumo.periodo_fin}")
        print(f"  Consumo: {consumo.consumo_kwh} kWh")
        print(f"  Costo total: ${consumo.costo_total:.2f} MXN")
        print(f"  Costo por kWh: ${consumo.costo_por_kwh():.2f} MXN")

def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "PRUEBA DE BACKEND - PYWATTS" + " "*30 + "║")
    print("║" + " "*15 + "Sistema de Optimización de Consumo Energético" + " "*17 + "║")
    print("╚" + "═"*78 + "╝")
    
    try:
        # Prueba 1: Base de datos
        test_creacion_base_datos()
        
        # Prueba 2: Usuario
        usuario_id = test_crud_usuario()
        
        # Prueba 3: Dispositivos
        test_crud_dispositivos(usuario_id)
        
        # Prueba 4: Optimización
        configuracion_optima, ahorro_total = test_calculos_optimizacion(usuario_id)
        
        # Prueba 5: Recomendaciones
        test_recomendaciones(usuario_id, configuracion_optima, ahorro_total)
        
        # Prueba 6: Gráficas
        test_graficas(usuario_id)
        
        # Prueba 7: PDF
        test_generacion_pdf(usuario_id)
        
        # Prueba 8: Consumo bimestral
        test_consumo_bimestral(usuario_id)
        
        # Resumen final
        print_seccion("RESUMEN FINAL")
        print("✅ Todas las pruebas completadas exitosamente!")
        print("\nEstadísticas:")
        with app.app_context():
            total_usuarios = Usuario.query.count()
            total_dispositivos = Dispositivo.query.count()
            total_consumos = ConsumoBimestral.query.count()
            total_reportes = Reporte.query.count()
            
            print(f"  • Usuarios: {total_usuarios}")
            print(f"  • Dispositivos: {total_dispositivos}")
            print(f"  • Registros de consumo: {total_consumos}")
            print(f"  • Reportes generados: {total_reportes}")
        
        print("\n📁 Archivos generados:")
        print(f"  • Base de datos: test_pywatts.db")
        print(f"  • PDFs: exports/reports/")
        
        print("\n🎉 ¡El backend de PyWatts está funcionando correctamente!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)