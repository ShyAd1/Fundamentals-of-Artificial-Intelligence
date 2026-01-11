"""
Clasificador K-NN (K-Nearest Neighbors).
Implementa el algoritmo de clasificación por k vecinos más cercanos.
Implementación completamente manual sin bibliotecas externas.
"""

# ============================================================================
# FUNCIONES AUXILIARES IMPLEMENTADAS MANUALMENTE
# ============================================================================


def sqrt(n):
    """
    Calcula la raíz cuadrada usando el método de Newton-Raphson.

    Args:
        n: Número del cual calcular la raíz cuadrada

    Returns:
        Raíz cuadrada aproximada de n
    """
    if n < 0:
        raise ValueError("No se puede calcular raíz cuadrada de números negativos")
    if n == 0:
        return 0

    x = n
    y = (x + 1) / 2
    epsilon = 1e-10

    while abs(x - y) > epsilon:
        x = y
        y = (x + n / x) / 2

    return y


def euclidean_distance(point1, point2):
    """
    Calcula la distancia euclidiana entre dos puntos.

    Args:
        point1: Primer vector
        point2: Segundo vector

    Returns:
        Distancia euclidiana
    """
    if len(point1) != len(point2):
        raise ValueError("Los vectores deben tener la misma dimensión")

    sum_squares = 0
    for i in range(len(point1)):
        diff = point1[i] - point2[i]
        sum_squares += diff * diff

    return sqrt(sum_squares)


def manhattan_distance(point1, point2):
    """
    Calcula la distancia de Manhattan entre dos puntos.

    Args:
        point1: Primer vector
        point2: Segundo vector

    Returns:
        Distancia de Manhattan
    """
    if len(point1) != len(point2):
        raise ValueError("Los vectores deben tener la misma dimensión")

    sum_abs = 0
    for i in range(len(point1)):
        sum_abs += abs(point1[i] - point2[i])

    return sum_abs


def get_distance_function(metric_name):
    """
    Retorna la función de distancia correspondiente.

    Args:
        metric_name: 'euclidean' o 'manhattan'

    Returns:
        Función de distancia
    """
    metrics = {
        "euclidean": euclidean_distance,
        "euclidiana": euclidean_distance,
        "manhattan": manhattan_distance,
    }

    metric_lower = metric_name.lower()
    if metric_lower not in metrics:
        raise ValueError(f"Métrica no reconocida: {metric_name}")

    return metrics[metric_lower]


# ============================================================================
# CLASE DATASET INTEGRADA
# ============================================================================


class Dataset:
    """
    Clase para gestionar conjuntos de datos de entrenamiento.
    """

    def __init__(self, input_size, output_size):
        """
        Inicializa un dataset.

        Args:
            input_size: Dimensión del vector de entrada
            output_size: Dimensión del vector de salida
        """
        if input_size <= 0 or output_size <= 0:
            raise ValueError("Los tamaños de entrada y salida deben ser positivos")

        self.input_size = input_size
        self.output_size = output_size
        self.data = []

    def add_sample(self, input_vector, output_vector):
        """
        Agrega un par entrada-salida al dataset.

        Args:
            input_vector: Vector de entrada
            output_vector: Vector de salida
        """
        if len(input_vector) != self.input_size:
            raise ValueError(
                f"El vector de entrada debe tener {self.input_size} dimensiones"
            )
        if len(output_vector) != self.output_size:
            raise ValueError(
                f"El vector de salida debe tener {self.output_size} dimensiones"
            )

        self.data.append((list(input_vector), list(output_vector)))

    def load_from_file(self, filepath):
        """
        Carga datos desde un archivo de texto plano.
        Formato: entrada | salida
        """
        try:
            with open(filepath, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    try:
                        parts = line.split("|")
                        if len(parts) != 2:
                            raise ValueError(
                                f"Línea {line_num}: Se esperaba formato 'entrada | salida'"
                            )

                        input_str = parts[0].strip()
                        output_str = parts[1].strip()

                        input_vector = [float(x.strip()) for x in input_str.split(",")]
                        output_vector = [
                            float(x.strip()) for x in output_str.split(",")
                        ]

                        self.add_sample(input_vector, output_vector)
                    except ValueError as e:
                        raise ValueError(f"Error en línea {line_num}: {str(e)}")

            print(f"✓ Dataset cargado: {len(self.data)} muestras")
        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    def get_samples(self):
        """Retorna todas las muestras del dataset"""
        return self.data

    def get_size(self):
        """Retorna el número de muestras"""
        return len(self.data)


# ============================================================================
# CLASIFICADOR K-NN
# ============================================================================


class KNNClassifier:
    """
    Clasificador K-NN que realiza clasificación usando los k vecinos más cercanos.
    """

    def __init__(self, dataset, k=3, distance_metric="euclidean"):
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
        self.k = min(
            k, dataset.get_size()
        )  # k no puede ser mayor que el tamaño del dataset
        self.distance_metric = distance_metric
        self.distance_func = get_distance_function(distance_metric)
        self.is_trained = dataset.get_size() > 0

    def predict(self, input_vector):
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
            raise ValueError(
                "El clasificador no ha sido entrenado. Cargue datos primero."
            )

        if len(input_vector) != self.dataset.input_size:
            raise ValueError(
                f"Vector de entrada debe tener {self.dataset.input_size} dimensiones"
            )

        # Calcular distancias a todos los puntos de entrenamiento
        distances = []
        for train_input, train_output in self.dataset.get_samples():
            distance = self.distance_func(input_vector, train_input)
            distances.append((distance, train_output))

        # Ordenar por distancia y seleccionar los k más cercanos
        distances.sort(key=lambda x: x[0])
        k_nearest = distances[: self.k]

        # Promediar las salidas de los k vecinos más cercanos
        num_outputs = self.dataset.output_size
        prediction = [0.0] * num_outputs

        for _, output_vector in k_nearest:
            for i, val in enumerate(output_vector):
                prediction[i] += val

        # Calcular promedio
        prediction = [val / self.k for val in prediction]

        return prediction

    def set_k(self, k):
        """
        Cambia el valor de k.

        Args:
            k: Nuevo valor de k
        """
        if k < 1:
            raise ValueError("k debe ser mayor o igual a 1")
        self.k = min(k, self.dataset.get_size())

    def set_distance_metric(self, metric_name):
        """
        Cambia la métrica de distancia.

        Args:
            metric_name: 'euclidean' o 'manhattan'
        """
        self.distance_metric = metric_name
        self.distance_func = get_distance_function(metric_name)

    def get_info(self):
        """Retorna información sobre el clasificador"""
        return f"KNN(k={self.k}, métrica={self.distance_metric}, muestras={self.dataset.get_size()})"

    def predict_batch(self, input_vectors):
        """
        Predice para múltiples vectores de entrada.

        Args:
            input_vectors: Lista de vectores de entrada

        Returns:
            Lista de predicciones
        """
        return [self.predict(vec) for vec in input_vectors]
