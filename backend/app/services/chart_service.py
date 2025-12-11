"""Service for generating charts and visualizations"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import io
import base64
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

from ..models.execution_accuracy import ExecutionAccuracy
from ..models.component_matching import ComponentMatching
from ..models.time_to_answer import TimeToAnswer


class ChartService:
    """Service for generating charts and visualizations for evaluation metrics"""
    
    def __init__(self):
        # Configure matplotlib for high-quality output
        matplotlib.rcParams['figure.dpi'] = 300
        matplotlib.rcParams['savefig.dpi'] = 300
        matplotlib.rcParams['font.size'] = 12
        matplotlib.rcParams['axes.titlesize'] = 14
        matplotlib.rcParams['axes.labelsize'] = 12
        matplotlib.rcParams['xtick.labelsize'] = 10
        matplotlib.rcParams['ytick.labelsize'] = 10
        matplotlib.rcParams['legend.fontsize'] = 10
        
        # Set seaborn style for professional appearance
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def generate_ex_chart(self, execution_accuracy_records: List[ExecutionAccuracy]) -> bytes:
        """
        Genera un gráfico de barras mostrando el porcentaje de Precisión de Ejecución (EX).
        
        Args:
            execution_accuracy_records: Lista de registros ExecutionAccuracy
            
        Returns:
            bytes: Datos de imagen PNG con resolución de 300 DPI
            
        Raises:
            ValueError: Si no se proporcionan datos
        """
        if not execution_accuracy_records:
            raise ValueError("No hay datos de precisión de ejecución disponibles para generar el gráfico")
        
        # Calculate EX percentage
        correct_count = sum(1 for record in execution_accuracy_records if record.is_correct)
        total_count = len(execution_accuracy_records)
        ex_percentage = (correct_count / total_count) * 100
        
        # Create figure with high DPI
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        
        # Create bar chart
        categories = ['Consultas Correctas', 'Consultas Incorrectas']
        values = [correct_count, total_count - correct_count]
        colors = ['#2E8B57', '#DC143C']  # Professional green and red
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{value}\n({value/total_count*100:.1f}%)',
                   ha='center', va='bottom', fontweight='bold')
        
        # Customize chart
        ax.set_title(f'Precisión de Ejecución (EX): {ex_percentage:.2f}%', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Número de Consultas', fontsize=12, fontweight='bold')
        ax.set_xlabel('Tipo de Resultado', fontsize=12, fontweight='bold')
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # Set y-axis to start from 0 and add some padding
        ax.set_ylim(0, max(values) * 1.1)
        
        # Add total count annotation
        ax.text(0.02, 0.98, f'Total de Consultas: {total_count}', 
               transform=ax.transAxes, fontsize=10, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Get PNG data
        png_data = buffer.getvalue()
        buffer.close()
        
        # Close the figure to free memory
        plt.close(fig)
        
        return png_data
    
    def generate_component_chart(self, component_matching_records: List[ComponentMatching]) -> bytes:
        """
        Genera un gráfico de barras comparando puntuaciones F1 para cada componente SQL.
        
        Args:
            component_matching_records: Lista de registros ComponentMatching
            
        Returns:
            bytes: Datos de imagen PNG con resolución de 300 DPI
            
        Raises:
            ValueError: Si no se proporcionan datos
        """
        if not component_matching_records:
            raise ValueError("No hay datos de coincidencia de componentes disponibles para generar el gráfico")
        
        # Calculate F1 scores for each component
        components = {
            'SELECT': [],
            'WHERE': [],
            'GROUP BY': [],
            'ORDER BY': [],
            'KEYWORDS': []
        }
        
        for record in component_matching_records:
            components['SELECT'].append(record.select_correct)
            components['WHERE'].append(record.where_correct)
            components['GROUP BY'].append(record.group_by_correct)
            components['ORDER BY'].append(record.order_by_correct)
            components['KEYWORDS'].append(record.keywords_correct)
        
        # Calculate accuracy percentage for each component
        component_scores = {}
        for component, values in components.items():
            if values:
                accuracy = (sum(values) / len(values)) * 100
                component_scores[component] = accuracy
            else:
                component_scores[component] = 0.0
        
        # Create figure with high DPI
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
        
        # Prepare data for plotting
        component_names = list(component_scores.keys())
        scores = list(component_scores.values())
        
        # Create color palette
        colors = sns.color_palette("husl", len(component_names))
        
        # Create horizontal bar chart for better label readability
        bars = ax.barh(component_names, scores, color=colors, alpha=0.8, 
                      edgecolor='black', linewidth=1)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                   f'{score:.1f}%', ha='left', va='center', fontweight='bold')
        
        # Customize chart
        ax.set_title('Precisión por Componente SQL', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Porcentaje de Precisión (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Componentes SQL', fontsize=12, fontweight='bold')
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_axisbelow(True)
        
        # Set x-axis limits
        ax.set_xlim(0, 105)
        
        # Agregar anotación del total de evaluaciones
        total_evaluaciones = len(component_matching_records)
        ax.text(0.02, 0.98, f'Total de Evaluaciones: {total_evaluaciones}', 
               transform=ax.transAxes, fontsize=10, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Get PNG data
        png_data = buffer.getvalue()
        buffer.close()
        
        # Close the figure to free memory
        plt.close(fig)
        
        return png_data
    
    def generate_tta_histogram(self, time_to_answer_records: List[TimeToAnswer]) -> bytes:
        """
        Genera un histograma mostrando la distribución del Tiempo de Respuesta (TTA).
        
        Args:
            time_to_answer_records: Lista de registros TimeToAnswer
            
        Returns:
            bytes: Datos de imagen PNG con resolución de 300 DPI
            
        Raises:
            ValueError: Si no se proporcionan datos
        """
        if not time_to_answer_records:
            raise ValueError("No hay datos de tiempo de respuesta disponibles para generar el gráfico")
        
        # Extract duration values
        durations = [record.duration_seconds for record in time_to_answer_records]
        
        # Create figure with high DPI
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
        
        # Create histogram
        n_bins = min(20, len(durations) // 2) if len(durations) > 10 else 10
        n, bins, patches = ax.hist(durations, bins=n_bins, alpha=0.7, 
                                  color='skyblue', edgecolor='black', linewidth=1)
        
        # Color bars with gradient
        for i, patch in enumerate(patches):
            patch.set_facecolor(plt.cm.viridis(i / len(patches)))
        
        # Calcular estadísticas
        media_tta = sum(durations) / len(durations)
        mediana_tta = sorted(durations)[len(durations) // 2]
        
        # Agregar líneas verticales para media y mediana
        ax.axvline(media_tta, color='red', linestyle='--', linewidth=2, 
                  label=f'Media: {media_tta:.2f}s')
        ax.axvline(mediana_tta, color='orange', linestyle='--', linewidth=2, 
                  label=f'Mediana: {mediana_tta:.2f}s')
        
        # Customize chart
        ax.set_title('Distribución del Tiempo de Respuesta (TTA)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Tiempo de Respuesta (segundos)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Agregar caja de estadísticas
        stats_text = f'Total: {len(durations)} evaluaciones\n'
        stats_text += f'Media: {media_tta:.2f}s\n'
        stats_text += f'Mediana: {mediana_tta:.2f}s\n'
        stats_text += f'Mín: {min(durations):.2f}s\n'
        stats_text += f'Máx: {max(durations):.2f}s'
        
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Get PNG data
        png_data = buffer.getvalue()
        buffer.close()
        
        # Close the figure to free memory
        plt.close(fig)
        
        return png_data
    
    def save_chart_to_file(self, chart_data: bytes, filename: str) -> str:
        """
        Save chart data to a file.
        
        Args:
            chart_data: PNG image data
            filename: Name of the file to save
            
        Returns:
            str: Path to the saved file
        """
        with open(filename, 'wb') as f:
            f.write(chart_data)
        return filename
    
    def chart_to_base64(self, chart_data: bytes) -> str:
        """
        Convert chart data to base64 string for web display.
        
        Args:
            chart_data: PNG image data
            
        Returns:
            str: Base64 encoded string
        """
        return base64.b64encode(chart_data).decode('utf-8')