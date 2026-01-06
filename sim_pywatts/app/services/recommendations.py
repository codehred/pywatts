class GeneradorRecomendaciones:
    """
    Genera recomendaciones personalizadas para optimizar el consumo energético
    """
    
    
    RECOMENDACIONES_BASE = {
        'refrigerador': [
            'Mantén la temperatura entre 3°C y 5°C, y el congelador a -18°C',
            'No introduzcas alimentos calientes, déjalos enfriar primero',
            'Revisa que las gomas de las puertas sellen correctamente',
            'Descongela regularmente si no es frost-free',
            'Ubícalo lejos de fuentes de calor y con espacio para ventilar'
        ],
        'lavadora': [
            'Usa ciclos de agua fría siempre que sea posible',
            'Llena la lavadora a su capacidad máxima antes de usarla',
            'Utiliza la cantidad adecuada de detergente',
            'Programa lavados en horarios de tarifa reducida',
            'Limpia el filtro regularmente para mayor eficiencia'
        ],
        'televisor': [
            'Activa el modo de ahorro de energía en la configuración',
            'Reduce el brillo de la pantalla a un nivel confortable',
            'Apaga completamente el TV en lugar de dejarlo en standby',
            'Desconecta cuando no lo uses por períodos largos',
            'Considera usar un temporizador para apagado automático'
        ],
        'tv': [
            'Activa el modo de ahorro de energía en la configuración',
            'Reduce el brillo de la pantalla a un nivel confortable',
            'Apaga completamente el TV en lugar de dejarlo en standby',
            'Desconecta cuando no lo uses por períodos largos',
            'Considera usar un temporizador para apagado automático'
        ],
        'computadora': [
            'Activa el modo de suspensión después de 10-15 minutos de inactividad',
            'Reduce el brillo de la pantalla',
            'Desconecta cargadores cuando no estén en uso',
            'Apaga completamente al terminar el día',
            'Usa protectores de pantalla oscuros o negros'
        ],
        'aire_acondicionado': [
            'Configura la temperatura a 24-25°C para mayor eficiencia',
            'Limpia o cambia los filtros mensualmente',
            'Cierra puertas y ventanas mientras está en uso',
            'Utiliza ventiladores de techo para circular el aire',
            'Programa el apagado automático durante la noche',
            'Sella grietas en puertas y ventanas'
        ],
        'microondas': [
            'Descongela alimentos en el refrigerador en lugar del microondas',
            'Limpia el interior regularmente para mayor eficiencia',
            'Usa recipientes aptos que permitan cocción uniforme',
            'No abras la puerta innecesariamente durante el uso',
            'Desconéctalo cuando no esté en uso'
        ],
        'plancha': [
            'Plancha varias prendas en una sola sesión',
            'Comienza con telas que requieren baja temperatura',
            'Desconecta antes de terminar, usa el calor residual',
            'Humedece la ropa para planchar más rápido',
            'Usa tabla de planchar con superficie reflectante'
        ],
        'calentador': [
            'Ajusta la temperatura a 50-60°C máximo',
            'Aísla el tanque y tuberías de agua caliente',
            'Repara fugas de agua caliente inmediatamente',
            'Instala regaderas de bajo flujo',
            'Programa el encendido en horarios específicos'
        ],
        'licuadora': [
            'Usa el tiempo mínimo necesario para licuar',
            'Corta los alimentos en trozos pequeños antes',
            'Limpia inmediatamente después de usar',
            'No dejes funcionando sin supervisión',
            'Desconecta después de cada uso'
        ]
    }
    
    RECOMENDACIONES_GENERALES = [
        'Reemplaza focos incandescentes por LED (ahorran hasta 80% de energía)',
        'Desconecta aparatos en standby (pueden consumir hasta 10% de tu factura)',
        'Aprovecha la luz natural durante el día',
        'Sella grietas en puertas y ventanas para evitar pérdidas de clima',
        'Usa regletas con interruptor para apagar varios dispositivos a la vez',
        'Considera instalar paneles solares si tu ubicación lo permite',
        'Programa tareas de alto consumo en horarios de tarifa reducida',
        'Realiza mantenimiento preventivo a tus electrodomésticos'
    ]
    
    def __init__(self, dispositivos, configuracion_optima):
        """
        Inicializa el generador de recomendaciones
        
        Args:
            dispositivos: Lista de objetos Dispositivo
            configuracion_optima: Dict con la configuración óptima calculada
        """
        self.dispositivos = dispositivos
        self.configuracion_optima = configuracion_optima
        
    def generar_recomendaciones_personalizadas(self):
        """
        Genera recomendaciones personalizadas basadas en los dispositivos
        y la configuración óptima
        
        Returns:
            dict: Recomendaciones organizadas por prioridad
        """
        recomendaciones = {
            'criticas': [],  # Alto consumo y alto potencial de ahorro
            'importantes': [],  # Consumo medio con buen potencial
            'opcionales': [],  # Bajo consumo o bajo potencial
            'generales': []  # Recomendaciones generales
        }
        
        # Ordenar dispositivos por potencial de ahorro
        dispositivos_ordenados = sorted(
            self.configuracion_optima.items(),
            key=lambda x: x[1]['ahorro_kwh'],
            reverse=True
        )
        
        for nombre_dispositivo, config in dispositivos_ordenados:
            dispositivo = next((d for d in self.dispositivos if d.nombre == nombre_dispositivo), None)
            if not dispositivo:
                continue
            
            ahorro_kwh = config['ahorro_kwh']
            reduccion_horas = config['reduccion_horas']
            
            # prioridad
            if ahorro_kwh > 50:  # Alto ahorro
                prioridad = 'criticas'
            elif ahorro_kwh > 20:  # Ahorro medio
                prioridad = 'importantes'
            else:  # Bajo ahorro
                prioridad = 'opcionales'
            
            tipo_normalizado = dispositivo.tipo.lower().replace(' ', '_')
            recomendaciones_especificas = self.RECOMENDACIONES_BASE.get(tipo_normalizado, [])
            
           
            recomendacion = {
                'dispositivo': nombre_dispositivo,
                'tipo': dispositivo.tipo,
                'accion_principal': f'Reducir uso de {reduccion_horas:.1f} horas diarias',
                'ahorro_potencial_kwh': round(ahorro_kwh, 2),
                'ahorro_potencial_pesos': round(config['ahorro_pesos'], 2),
                'horas_actuales': config['horas_actuales'],
                'horas_recomendadas': config['horas_optimas'],
                'consejos_especificos': recomendaciones_especificas[:3]  # Top 3 consejos
            }
            
            recomendaciones[prioridad].append(recomendacion)
        
        
        recomendaciones['generales'] = self.RECOMENDACIONES_GENERALES[:5]
        
        return recomendaciones
    
    def generar_plan_accion(self):
        """
        Genera un plan de acción escalonado para implementar mejoras
        
        Returns:
            dict: Plan de acción por semanas
        """
        recomendaciones = self.generar_recomendaciones_personalizadas()
        
        plan = {
            'semana_1': {
                'titulo': 'Cambios Inmediatos de Alto Impacto',
                'acciones': []
            },
            'semana_2': {
                'titulo': 'Optimización de Dispositivos Principales',
                'acciones': []
            },
            'semana_3': {
                'titulo': 'Mejoras Adicionales y Hábitos',
                'acciones': []
            },
            'semana_4': {
                'titulo': 'Monitoreo y Ajustes Finales',
                'acciones': []
            }
        }
        
        # Semana 1: Críticas
        for rec in recomendaciones['criticas'][:3]:
            plan['semana_1']['acciones'].append({
                'dispositivo': rec['dispositivo'],
                'accion': rec['accion_principal'],
                'ahorro_esperado': f"${rec['ahorro_potencial_pesos']:.2f}"
            })
        
        # Semana 2: Importantes
        for rec in recomendaciones['importantes'][:3]:
            plan['semana_2']['acciones'].append({
                'dispositivo': rec['dispositivo'],
                'accion': rec['accion_principal'],
                'consejos': rec['consejos_especificos'][:2]
            })
        
        # Semana 3: Opcionales y generales
        for rec in recomendaciones['opcionales'][:2]:
            plan['semana_3']['acciones'].append({
                'dispositivo': rec['dispositivo'],
                'accion': rec['accion_principal']
            })
        plan['semana_3']['acciones'].extend([
            {'accion_general': rec} for rec in recomendaciones['generales'][:3]
        ])
        
        # Semana 4: Monitoreo
        plan['semana_4']['acciones'] = [
            {'accion': 'Revisar el consumo semanal y comparar con el objetivo'},
            {'accion': 'Ajustar horarios de uso según resultados observados'},
            {'accion': 'Identificar nuevos dispositivos para optimizar'},
            {'accion': 'Documentar hábitos exitosos para mantenerlos'}
        ]
        
        return plan
    
    def calcular_impacto_ambiental(self, ahorro_kwh):
        """
        Calcula el impacto ambiental del ahorro energético
        
        Args:
            ahorro_kwh: Ahorro total en kWh
        
        Returns:
            dict: Equivalencias ambientales
        """
       #factores
        co2_por_kwh = 0.527  # kg CO2 por kWh (promedio México)
        arboles_por_kg_co2 = 0.06  # Árboles necesarios para absorber 1 kg CO2/año
        autos_km_por_kg_co2 = 0.24  # km recorridos por auto por kg CO2
        
        co2_ahorrado = ahorro_kwh * co2_por_kwh
        
        return {
            'ahorro_kwh': round(ahorro_kwh, 2),
            'co2_kg_ahorrado': round(co2_ahorrado, 2),
            'equivalente_arboles': round(co2_ahorrado * arboles_por_kg_co2, 1),
            'equivalente_km_auto': round(co2_ahorrado / autos_km_por_kg_co2, 1),
            'mensaje': f'Tu ahorro equivale a plantar {round(co2_ahorrado * arboles_por_kg_co2, 1)} árboles o dejar de conducir {round(co2_ahorrado / autos_km_por_kg_co2, 1)} km'
        }
    
    def generar_tips_horarios(self):
        """
        Genera tips sobre los mejores horarios para usar dispositivos
        basado en tarifas eléctricas
        
        Returns:
            dict: Tips de horarios
        """
        return {
            'horario_base': {
                'descripcion': 'Tarifa más económica',
                'horarios': 'Lunes a Viernes: 00:00-06:00, Fines de semana: todo el día',
                'dispositivos_recomendados': ['Lavadora', 'Lavavajillas', 'Calentador'],
                'ahorro_estimado': '20-30%'
            },
            'horario_intermedio': {
                'descripcion': 'Tarifa moderada',
                'horarios': 'Lunes a Viernes: 06:00-20:00 (excepto 18:00-22:00)',
                'dispositivos_recomendados': ['Plancha', 'Aspiradora', 'Microondas'],
                'ahorro_estimado': '10-15%'
            },
            'horario_punta': {
                'descripcion': 'Tarifa más alta - EVITAR',
                'horarios': 'Lunes a Viernes: 18:00-22:00',
                'dispositivos_evitar': ['Aire acondicionado', 'Calentador', 'Plancha', 'Lavadora'],
                'recomendacion': 'Minimiza el uso de dispositivos de alto consumo'
            }
        }