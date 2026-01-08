"""
Módulo para calcular diferentes métricas de distancia.
"""

import math
from typing import List


class DistanceMetrics:
    """Clase con métodos estáticos para calcular diferentes distancias"""
    
    @staticmethod
    def euclidean(point1: List[float], point2: List[float]) -> float:
        """
        Calcula la distancia euclidiana entre dos puntos.
        
        Formula: d = sqrt(sum((p1[i] - p2[i])^2))
        
        Args:
            point1: Primer vector
            point2: Segundo vector
            
        Returns:
            Distancia euclidiana
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")
        
        sum_squares = sum((x - y) ** 2 for x, y in zip(point1, point2))
        return math.sqrt(sum_squares)
    
    @staticmethod
    def manhattan(point1: List[float], point2: List[float]) -> float:
        """
        Calcula la distancia de Manhattan (distancia L1) entre dos puntos.
        
        Formula: d = sum(|p1[i] - p2[i]|)
        
        Args:
            point1: Primer vector
            point2: Segundo vector
            
        Returns:
            Distancia de Manhattan
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")
        
        return sum(abs(x - y) for x, y in zip(point1, point2))
    
    @staticmethod
    def get_distance_function(metric_name: str):
        """
        Retorna la función de distancia correspondiente al nombre.
        
        Args:
            metric_name: 'euclidean' o 'manhattan'
            
        Returns:
            Función de distancia
        """
        metrics = {
            'euclidean': DistanceMetrics.euclidean,
            'manhattan': DistanceMetrics.manhattan,
            'euclidiana': DistanceMetrics.euclidean,
            'manhattan': DistanceMetrics.manhattan
        }
        
        metric_lower = metric_name.lower()
        if metric_lower not in metrics:
            raise ValueError(f"Métrica de distancia no reconocida: {metric_name}")
        
        return metrics[metric_lower]
