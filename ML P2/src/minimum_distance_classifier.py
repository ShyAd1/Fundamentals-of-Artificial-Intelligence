"""
Clasificador de Mínima Distancia.
Implementa el algoritmo de clasificación basado en prototipos de mínima distancia.
"""

from typing import List, Dict, Tuple
from src.distance_metrics import DistanceMetrics
from src.dataset import Dataset


class MinimumDistanceClassifier:
    """
    Clasificador de Mínima Distancia que utiliza prototipos (centros de clases)
    para realizar clasificación.
    """
    
    def __init__(self, dataset: Dataset, distance_metric: str = 'euclidean'):
        """
        Inicializa el clasificador de mínima distancia.
        
        Args:
            dataset: Dataset con los datos de entrenamiento
            distance_metric: 'euclidean' o 'manhattan'
        """
        self.dataset = dataset
        self.distance_metric = distance_metric
        self.distance_func = DistanceMetrics.get_distance_function(distance_metric)
        self.prototypes: Dict[int, Tuple[List[float], List[float]]] = {}
        self.is_trained = False
        self._train()
    
    def _train(self) -> None:
        """
        Entrena el clasificador calculando los prototipos (centros de clases).
        
        Agrupa las muestras por clase (usando la salida como identificador)
        y calcula el centroide de cada grupo.
        """
        if self.dataset.get_size() == 0:
            self.is_trained = False
            return
        
        # Agrupar muestras por clase (usando la representación en string de la salida)
        classes: Dict[str, List[Tuple[List[float], List[float]]]] = {}
        
        for input_vec, output_vec in self.dataset.get_samples():
            # Usar la salida como identificador de clase
            class_key = str(output_vec)
            if class_key not in classes:
                classes[class_key] = []
            classes[class_key].append((input_vec, output_vec))
        
        # Calcular el centroide de cada clase
        self.prototypes = {}
        for idx, (class_key, samples) in enumerate(classes.items()):
            # Calcular centroide de los vectores de entrada
            input_centroid = self._calculate_centroid([inp for inp, _ in samples])
            # Usar el promedio de las salidas
            output_centroid = self._calculate_centroid([out for _, out in samples])
            self.prototypes[idx] = (input_centroid, output_centroid)
        
        self.is_trained = True
    
    @staticmethod
    def _calculate_centroid(vectors: List[List[float]]) -> List[float]:
        """
        Calcula el centroide (promedio) de un conjunto de vectores.
        
        Args:
            vectors: Lista de vectores
            
        Returns:
            Vector centroide
        """
        if not vectors:
            return []
        
        dim = len(vectors[0])
        centroid = [0.0] * dim
        
        for vector in vectors:
            for i, val in enumerate(vector):
                centroid[i] += val
        
        centroid = [val / len(vectors) for val in centroid]
        return centroid
    
    def predict(self, input_vector: List[float]) -> List[float]:
        """
        Predice la salida para un vector de entrada usando mínima distancia.
        
        Algoritmo:
        1. Calcula la distancia del vector de entrada a todos los prototipos
        2. Selecciona el prototipo más cercano (mínima distancia)
        3. Retorna la salida asociada a ese prototipo
        
        Args:
            input_vector: Vector de entrada para predecir
            
        Returns:
            Vector de salida predicho
        """
        if not self.is_trained:
            raise ValueError("El clasificador no ha sido entrenado. Cargue datos primero.")
        
        if len(input_vector) != self.dataset.input_size:
            raise ValueError(f"Vector de entrada debe tener {self.dataset.input_size} dimensiones")
        
        # Encontrar el prototipo más cercano
        min_distance = float('inf')
        closest_prototype = None
        
        for prototype_input, prototype_output in self.prototypes.values():
            distance = self.distance_func(input_vector, prototype_input)
            if distance < min_distance:
                min_distance = distance
                closest_prototype = prototype_output
        
        if closest_prototype is None:
            raise RuntimeError("No se encontró prototipo válido")
        
        return closest_prototype
    
    def set_distance_metric(self, metric_name: str) -> None:
        """
        Cambia la métrica de distancia y reentrena si es necesario.
        
        Args:
            metric_name: 'euclidean' o 'manhattan'
        """
        self.distance_metric = metric_name
        self.distance_func = DistanceMetrics.get_distance_function(metric_name)
    
    def get_info(self) -> str:
        """Retorna información sobre el clasificador"""
        return f"MinimumDistance(métrica={self.distance_metric}, clases={len(self.prototypes)})"
    
    def get_prototypes_count(self) -> int:
        """Retorna el número de prototipos (clases) encontrados"""
        return len(self.prototypes)
    
    def predict_batch(self, input_vectors: List[List[float]]) -> List[List[float]]:
        """
        Predice para múltiples vectores de entrada.
        
        Args:
            input_vectors: Lista de vectores de entrada
            
        Returns:
            Lista de predicciones
        """
        return [self.predict(vec) for vec in input_vectors]
