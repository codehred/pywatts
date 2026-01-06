import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para servidor
import io
import base64
from datetime import datetime, timedelta
import numpy as np

class GeneradorGraficas:
    """
    Generas para visualización de consumo energético
    """
    
    def __init__(self):
        
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
    
    def _fig_to_base64(self, fig):
        """Convierte una figura de matplotlib a base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64
    
    def grafica_consumo_por_dispositivo(self, consumo_dispositivos):
        """
        Genera de barras del consumo por dispositivo
        
        Args:
            consumo_dispositivos: Dict con consumo de cada dispositivo
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        dispositivos = list(consumo_dispositivos.keys())
        consumos = [data['consumo_bimestral_kwh'] for data in consumo_dispositivos.values()]
        
        barras = ax.bar(dispositivos, consumos, color=self.colores[:len(dispositivos)])
        
        ax.set_xlabel('Dispositivos', fontsize=12, fontweight='bold')
        ax.set_ylabel('Consumo (kWh)', fontsize=12, fontweight='bold')
        ax.set_title('Consumo Energético Bimestral por Dispositivo', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
       
        for barra in barras:
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura,
                   f'{altura:.1f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_pie_distribucion(self, consumo_dispositivos):
        """
        Genera de pastel de la distribución de consumo
        
        Args:
            consumo_dispositivos: Dict con consumo de cada dispositivo
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        dispositivos = list(consumo_dispositivos.keys())
        porcentajes = [data['porcentaje'] for data in consumo_dispositivos.values()]
        
       
        wedges, texts, autotexts = ax.pie(
            porcentajes,
            labels=dispositivos,
            autopct='%1.1f%%',
            startangle=90,
            colors=self.colores[:len(dispositivos)]
        )
        
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(11)
        
        ax.set_title('Distribución del Consumo Energético', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_comparativa_antes_despues(self, ahorro_total):
        """
        Genera comparativa entre consumo actual y optimizado
        
        Args:
            ahorro_total: Dict con información del ahorro total
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categorias = ['Consumo Actual', 'Consumo Optimizado']
        valores = [
            ahorro_total['consumo_actual_kwh'],
            ahorro_total['consumo_optimizado_kwh']
        ]
        
        barras = ax.bar(categorias, valores, color=['#FF6B6B', '#4ECDC4'], width=0.5)
        
        ax.set_ylabel('Consumo (kWh)', fontsize=12, fontweight='bold')
        ax.set_title('Comparativa: Consumo Actual vs Optimizado', fontsize=14, fontweight='bold')
        
       
        for i, barra in enumerate(barras):
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura,
                   f'{altura:.1f} kWh',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
      
        ahorro = ahorro_total['ahorro_kwh']
        ax.text(0.5, max(valores) * 0.5, 
               f'Ahorro: {ahorro:.1f} kWh\n({ahorro_total["porcentaje_ahorro"]:.1f}%)',
               ha='center', fontsize=13, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_proyeccion_consumo(self, proyeccion):
        """
        Genera de línea con proyección de consumo
        
        Args:
            proyeccion: Lista de consumos proyectados
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        fechas = [item['fecha'] for item in proyeccion]
        consumos = [item['consumo_kwh'] for item in proyeccion]
        
       
        ax.plot(fechas, consumos, marker='o', linewidth=2, markersize=4, color='#4ECDC4')
        ax.fill_between(range(len(fechas)), consumos, alpha=0.3, color='#4ECDC4')
        
        ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        ax.set_ylabel('Consumo Diario (kWh)', fontsize=12, fontweight='bold')
        ax.set_title('Proyección de Consumo Energético', fontsize=14, fontweight='bold')
        
       
        paso = max(1, len(fechas) // 10)
        ax.set_xticks(range(0, len(fechas), paso))
        ax.set_xticklabels([fechas[i] for i in range(0, len(fechas), paso)], rotation=45, ha='right')
        
      
        promedio = np.mean(consumos)
        ax.axhline(y=promedio, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Promedio: {promedio:.2f} kWh')
        ax.legend()
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_costo_por_dispositivo(self, consumo_dispositivos):
        """
        Genera de barras horizontales del costo por dispositivo
        
        Args:
            consumo_dispositivos: Dict con consumo de cada dispositivo
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        dispositivos = list(consumo_dispositivos.keys())
        costos = [data['costo_bimestral'] for data in consumo_dispositivos.values()]
        
        
        indices = np.argsort(costos)[::-1]
        dispositivos_ordenados = [dispositivos[i] for i in indices]
        costos_ordenados = [costos[i] for i in indices]
        
        barras = ax.barh(dispositivos_ordenados, costos_ordenados, color=self.colores[:len(dispositivos)])
        
        ax.set_xlabel('Costo Bimestral ($)', fontsize=12, fontweight='bold')
        ax.set_title('Costo por Dispositivo', fontsize=14, fontweight='bold')
        
       
        for i, barra in enumerate(barras):
            ancho = barra.get_width()
            ax.text(ancho, barra.get_y() + barra.get_height()/2.,
                   f'${ancho:.2f}',
                   ha='left', va='center', fontweight='bold', fontsize=10, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_ahorro_por_dispositivo(self, configuracion_optima):
        """
        Genera del potencial de ahorro por dispositivo
        
        Args:
            configuracion_optima: Dict con configuración óptima
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        dispositivos = list(configuracion_optima.keys())
        ahorros = [config['ahorro_pesos'] for config in configuracion_optima.values()]
        
       
        indices = np.argsort(ahorros)[::-1]
        dispositivos_ordenados = [dispositivos[i] for i in indices]
        ahorros_ordenados = [ahorros[i] for i in indices]
        
        barras = ax.bar(dispositivos_ordenados, ahorros_ordenados, color='#4ECDC4')
        
        ax.set_xlabel('Dispositivos', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ahorro Potencial ($)', fontsize=12, fontweight='bold')
        ax.set_title('Potencial de Ahorro por Dispositivo', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        
        for barra in barras:
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura,
                   f'${altura:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_energia_acumulada(self, energia_acumulada, intervalo):
        """
        Genera de energía acumulada por intervalo
        
        Args:
            energia_acumulada: Dict con energía acumulada por dispositivo
            intervalo: 'dia', 'semana' o 'mes'
        
        Returns:
            str: Imagen en base64
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        dispositivos = list(energia_acumulada.keys())
        consumos = [data['consumo_kwh'] for data in energia_acumulada.values()]
        
        barras = ax.bar(dispositivos, consumos, color=self.colores[:len(dispositivos)])
        
        ax.set_xlabel('Dispositivos', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Energía Acumulada (kWh por {intervalo})', fontsize=12, fontweight='bold')
        ax.set_title(f'Energía Acumulada por {intervalo.capitalize()}', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        
        for barra in barras:
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura,
                   f'{altura:.1f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def grafica_dashboard_completo(self, consumo_dispositivos, ahorro_total, configuracion_optima):
        """
        Genera un dashboard completo con múltipless
        
        Args:
            consumo_dispositivos: Dict con consumo de cada dispositivo
            ahorro_total: Dict con información del ahorro total
            configuracion_optima: Dict con configuración óptima
        
        Returns:
            str: Imagen en base64
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1: Consumo por dispositivo (barras)
        ax1 = fig.add_subplot(gs[0, 0])
        dispositivos = list(consumo_dispositivos.keys())
        consumos = [data['consumo_bimestral_kwh'] for data in consumo_dispositivos.values()]
        ax1.bar(dispositivos, consumos, color=self.colores[:len(dispositivos)])
        ax1.set_title('Consumo por Dispositivo', fontweight='bold')
        ax1.set_ylabel('kWh')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 2: Distribución (pastel)
        ax2 = fig.add_subplot(gs[0, 1])
        porcentajes = [data['porcentaje'] for data in consumo_dispositivos.values()]
        ax2.pie(porcentajes, labels=dispositivos, autopct='%1.1f%%', 
               colors=self.colores[:len(dispositivos)])
        ax2.set_title('Distribución del Consumo', fontweight='bold')
        
        # 3: Comparativa antes/después
        ax3 = fig.add_subplot(gs[1, 0])
        categorias = ['Actual', 'Optimizado']
        valores = [ahorro_total['consumo_actual_kwh'], ahorro_total['consumo_optimizado_kwh']]
        ax3.bar(categorias, valores, color=['#FF6B6B', '#4ECDC4'])
        ax3.set_title('Comparativa Consumo', fontweight='bold')
        ax3.set_ylabel('kWh')
        for i, v in enumerate(valores):
            ax3.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 4: Ahorro por dispositivo
        ax4 = fig.add_subplot(gs[1, 1])
        dispositivos_ahorro = list(configuracion_optima.keys())
        ahorros = [config['ahorro_kwh'] for config in configuracion_optima.values()]
        indices = np.argsort(ahorros)[::-1][:5]  # Top 5
        dispositivos_top = [dispositivos_ahorro[i] for i in indices]
        ahorros_top = [ahorros[i] for i in indices]
        ax4.barh(dispositivos_top, ahorros_top, color='#4ECDC4')
        ax4.set_title('Top 5 Potencial de Ahorro', fontweight='bold')
        ax4.set_xlabel('Ahorro (kWh)')
        
        plt.suptitle('Dashboard de Optimización Energética', fontsize=16, fontweight='bold', y=0.98)
        
        return self._fig_to_base64(fig)