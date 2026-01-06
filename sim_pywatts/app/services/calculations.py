import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta

class OptimizadorEnergetico:
    """
    Clase para realizar cálculos de optimización de consumo energético
    usando cálculo diferencial (máximos y mínimos)
    """
    
    def __init__(self, dispositivos, tarifa_kwh=1.5):
        """
        Inicializa el optimizador
        
        Args:
            dispositivos: Lista de objetos Dispositivo
            tarifa_kwh: Tarifa promedio por kWh en pesos
        """
        self.dispositivos = dispositivos
        self.tarifa_kwh = tarifa_kwh
        
    def consumo_total_actual(self):
        """Calcula el consumo total actual en kWh bimestral"""
        return sum(d.consumo_bimestral_kwh() for d in self.dispositivos)
    
    def costo_total_actual(self):
        """Calcula el costo total actual en pesos"""
        return self.consumo_total_actual() * self.tarifa_kwh
    
    def calcular_consumo_por_dispositivo(self):
        """Retorna un diccionario con el consumo de cada dispositivo"""
        return {
            d.nombre: {
                'potencia_watts': d.potencia_watts,
                'horas_uso_dia': d.horas_uso_dia,
                'consumo_diario_kwh': d.consumo_diario_kwh(),
                'consumo_mensual_kwh': d.consumo_mensual_kwh(),
                'consumo_bimestral_kwh': d.consumo_bimestral_kwh(),
                'costo_bimestral': d.consumo_bimestral_kwh() * self.tarifa_kwh,
                'porcentaje': (d.consumo_bimestral_kwh() / self.consumo_total_actual() * 100) if self.consumo_total_actual() > 0 else 0
            }
            for d in self.dispositivos
        }
    
    def encontrar_punto_optimo(self, restriccion_ahorro=0.20):
        """
        Encuentra el punto óptimo de consumo usando optimización
        Aplica cálculo diferencial para minimizar el consumo
        
        Args:
            restriccion_ahorro: Porcentaje mínimo de ahorro deseado (default 20%)
        
        Returns:
            dict: Configuración óptima de horas de uso por dispositivo
        """
        n_dispositivos = len(self.dispositivos)
        
        
        def objetivo(horas_uso):
            consumo_total = 0
            for i, dispositivo in enumerate(self.dispositivos):
                consumo_total += (dispositivo.potencia_watts * horas_uso[i]) / 1000
            return consumo_total * 60  
        
      
        limites = [(0, d.horas_uso_dia) for d in self.dispositivos]
        
    
        horas_iniciales = [d.horas_uso_dia for d in self.dispositivos]
        
       
        consumo_actual = self.consumo_total_actual()
        consumo_objetivo = consumo_actual * (1 - restriccion_ahorro)
        
        def restriccion_ahorro_func(horas_uso):
            consumo = objetivo(horas_uso)
            return consumo_objetivo - consumo
        
        restricciones = {'type': 'ineq', 'fun': restriccion_ahorro_func}
        
        # Optimización
        resultado = minimize(
            objetivo,
            horas_iniciales,
            method='SLSQP',
            bounds=limites,
            constraints=restricciones
        )
        
       
        configuracion_optima = {}
        for i, dispositivo in enumerate(self.dispositivos):
            horas_optimas = resultado.x[i]
            reduccion_horas = dispositivo.horas_uso_dia - horas_optimas
            
            consumo_actual_disp = dispositivo.consumo_bimestral_kwh()
            consumo_optimo_disp = (dispositivo.potencia_watts * horas_optimas * 60) / 1000
            ahorro_disp = consumo_actual_disp - consumo_optimo_disp
            
            configuracion_optima[dispositivo.nombre] = {
                'horas_actuales': round(dispositivo.horas_uso_dia, 2),
                'horas_optimas': round(horas_optimas, 2),
                'reduccion_horas': round(reduccion_horas, 2),
                'consumo_actual_kwh': round(consumo_actual_disp, 2),
                'consumo_optimo_kwh': round(consumo_optimo_disp, 2),
                'ahorro_kwh': round(ahorro_disp, 2),
                'ahorro_pesos': round(ahorro_disp * self.tarifa_kwh, 2)
            }
        
        return configuracion_optima
    
    def calcular_ahorro_total(self, configuracion_optima):
        """Calcula el ahorro total de la configuración óptima"""
        ahorro_total_kwh = sum(config['ahorro_kwh'] for config in configuracion_optima.values())
        ahorro_total_pesos = ahorro_total_kwh * self.tarifa_kwh
        consumo_actual = self.consumo_total_actual()
        
        return {
            'consumo_actual_kwh': round(consumo_actual, 2),
            'consumo_optimizado_kwh': round(consumo_actual - ahorro_total_kwh, 2),
            'ahorro_kwh': round(ahorro_total_kwh, 2),
            'ahorro_pesos': round(ahorro_total_pesos, 2),
            'porcentaje_ahorro': round((ahorro_total_kwh / consumo_actual * 100) if consumo_actual > 0 else 0, 2)
        }
    
    def proyectar_consumo(self, dias=30):
        """
        Proyecta el consumo de energía para los próximos días
        
        Args:
            dias: Número de días a proyectar
        
        Returns:
            list: Lista de consumos proyectados por día
        """
        consumo_diario = sum(d.consumo_diario_kwh() for d in self.dispositivos)
        
      
        proyeccion = []
        fecha_inicio = datetime.now()
        
        for i in range(dias):
            variacion = np.random.uniform(0.9, 1.1)
            consumo = consumo_diario * variacion
            fecha = fecha_inicio + timedelta(days=i)
            proyeccion.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'consumo_kwh': round(consumo, 2),
                'costo': round(consumo * self.tarifa_kwh, 2)
            })
        
        return proyeccion
    
    def calcular_rango_cobro_bimestral(self, consumo_kwh):
        """
        Calcula el rango aproximado de cobro basado en tarifas escalonadas
        (Simulación de tarifas CFE)
        
        Args:
            consumo_kwh: Consumo en kWh
        
        Returns:
            dict: Rangos de cobro
        """
     
        if consumo_kwh <= 150:
            tarifa = 0.82
        elif consumo_kwh <= 280:
            tarifa = 1.05
        elif consumo_kwh <= 400:
            tarifa = 1.35
        elif consumo_kwh <= 600:
            tarifa = 1.85
        else:
            tarifa = 2.85
        
        costo_base = consumo_kwh * tarifa
        costo_min = costo_base * 0.95  # -5%
        costo_max = costo_base * 1.05  # +5%
        
        return {
            'consumo_kwh': round(consumo_kwh, 2),
            'tarifa_aplicada': tarifa,
            'costo_estimado': round(costo_base, 2),
            'rango_minimo': round(costo_min, 2),
            'rango_maximo': round(costo_max, 2)
        }
    
    def calcular_energia_acumulada(self, intervalo='dia'):
        """
        Calcula la energía acumulada por dispositivo en intervalos
        
        Args:
            intervalo: 'dia', 'semana' o 'mes'
        
        Returns:
            dict: Energía acumulada por dispositivo
        """
        multiplicador = {
            'dia': 1,
            'semana': 7,
            'mes': 30
        }.get(intervalo, 1)
        
        energia_acumulada = {}
        for dispositivo in self.dispositivos:
            consumo_intervalo = dispositivo.consumo_diario_kwh() * multiplicador
            energia_acumulada[dispositivo.nombre] = {
                'consumo_kwh': round(consumo_intervalo, 2),
                'costo': round(consumo_intervalo * self.tarifa_kwh, 2),
                'intervalo': intervalo
            }
        
        return energia_acumulada