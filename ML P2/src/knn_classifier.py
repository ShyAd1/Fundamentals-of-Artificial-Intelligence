"""
Clasificador K-NN (K-Nearest Neighbors).
Implementa el algoritmo de clasificación por k vecinos más cercanos.
"""

from typing import List, Tuple
from src.distance_metrics import DistanceMetrics
from src.dataset import Dataset


class KNNClassifier:
    """
    Clasificador K-NN que realiza clasificación usando los k vecinos más cercanos.
    """
    
    def __init__(self, dataset: Dataset, k: int = 3, distance_metric: str = 'euclidean'):
        """
        Inicializa el clasificador K-NN.
        
        Args:
            dataset: Dataset con los datos de entrenamiento
            k: Número de vecinos a considerar (debe ser >= 1)
            distance_metric: 'euclidean' o 'manhattan'
        """
        if k < 1:
            raise ValueError("k debe ser mayor o igual a 1")
        
        self.dataset = dataset
        self.k = min(k, dataset.get_size())  # k no puede ser mayor que el tamaño del dataset
        self.distance_metric = distance_metric
        self.distance_func = DistanceMetrics.get_distance_function(distance_metric)
        self.is_trained = dataset.get_size() > 0
    
    def predict(self, input_vector: List[float]) -> List[float]:
        """
        Predice la salida para un vector de entrada usando K-NN.
        
        Algoritmo:
        1. Calcula la distancia del vector de entrada a todos los puntos de entrenamiento
        2. Selecciona los k puntos más cercanos
        3. Promedia sus salidas (para regresión) o vota (para clasificación)
        
        Args:
            input_vector: Vector de entrada para predecir
            
        Returns:
            Vector de salida predicho
        """
        if not self.is_trained:
            raise ValueError("El clasificador no ha sido entrenado. Cargue datos primero.")
        
        if len(input_vector) != self.dataset.input_size:
            raise ValueError(f"Vector de entrada debe tener {self.dataset.input_size} dimensiones")
        
        # Calcular distancias a todos los puntos de entrenamiento
        distances = []
        for train_input, train_output in self.dataset.get_samples():
            distance = self.distance_func(input_vector, train_input)
            distances.append((distance, train_output))
        
        # Ordenar por distancia y seleccionar los k más cercanos
        distances.sort(key=lambda x: x[0])
        k_nearest = distances[:self.k]
        
        # Promediar las salidas de los k vecinos más cercanos
        num_outputs = self.dataset.output_size
        prediction = [0.0] * num_outputs
        
        for _, output_vector in k_nearest:
            for i, val in enumerate(output_vector):
                prediction[i] += val
        
        # Calcular promedio
        prediction = [val / self.k for val in prediction]
        
        return prediction
    
    def set_k(self, k: int) -> None:
        """
        Cambia el valor de k.
        
        Args:
            k: Nuevo valor de k
        """
        if k < 1:
            raise ValueError("k debe ser mayor o igual a 1")
        self.k = min(k, self.dataset.get_size())
    
    def set_distance_metric(self, metric_name: str) -> None:
        """
        Cambia la métrica de distancia.
        
        Args:
            metric_name: 'euclidean' o 'manhattan'
        """
        self.distance_metric = metric_name
        self.distance_func = DistanceMetrics.get_distance_function(metric_name)
    
    def get_info(self) -> str:
        """Retorna información sobre el clasificador"""
        return f"KNN(k={self.k}, métrica={self.distance_metric}, muestras={self.dataset.get_size()})"
    
    def predict_batch(self, input_vectors: List[List[float]]) -> List[List[float]]:
        """
        Predice para múltiples vectores de entrada.
        
        Args:
            input_vectors: Lista de vectores de entrada
            
        Returns:
            Lista de predicciones
        """
        return [self.predict(vec) for vec in input_vectors]
