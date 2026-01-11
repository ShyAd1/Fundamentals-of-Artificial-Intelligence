"""
Clasificador de Mínima Distancia.
Implementa el algoritmo de clasificación basado en prototipos de mínima distancia.
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
# CLASIFICADOR DE MÍNIMA DISTANCIA
# ============================================================================


class MinimumDistanceClassifier:
    """
    Clasificador de Mínima Distancia que utiliza prototipos (centros de clases)
    para realizar clasificación.
    """

    def __init__(self, dataset, distance_metric="euclidean"):
        """
        Inicializa el clasificador de mínima distancia.

        Args:
            dataset: Dataset con los datos de entrenamiento
            distance_metric: 'euclidean' o 'manhattan'
        """
        self.dataset = dataset
        self.distance_metric = distance_metric
        self.distance_func = get_distance_function(distance_metric)
        self.prototypes = {}
        self.is_trained = False
        self._train()

    def _train(self):
        """
        Entrena el clasificador calculando los prototipos (centros de clases).

        Agrupa las muestras por clase (usando la salida como identificador)
        y calcula el centroide de cada grupo.
        """
        if self.dataset.get_size() == 0:
            self.is_trained = False
            return

        # Agrupar muestras por clase (usando la representación en string de la salida)
        classes = {}

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
    def _calculate_centroid(vectors):
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

    def predict(self, input_vector):
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
            raise ValueError(
                "El clasificador no ha sido entrenado. Cargue datos primero."
            )

        if len(input_vector) != self.dataset.input_size:
            raise ValueError(
                f"Vector de entrada debe tener {self.dataset.input_size} dimensiones"
            )

        # Encontrar el prototipo más cercano
        min_distance = float("inf")
        closest_prototype = None

        for prototype_input, prototype_output in self.prototypes.values():
            distance = self.distance_func(input_vector, prototype_input)
            if distance < min_distance:
                min_distance = distance
                closest_prototype = prototype_output

        if closest_prototype is None:
            raise RuntimeError("No se encontró prototipo válido")

        return closest_prototype

    def set_distance_metric(self, metric_name):
        """
        Cambia la métrica de distancia y reentrena si es necesario.

        Args:
            metric_name: 'euclidean' o 'manhattan'
        """
        self.distance_metric = metric_name
        self.distance_func = get_distance_function(metric_name)

    def get_info(self):
        """Retorna información sobre el clasificador"""
        return f"MinimumDistance(métrica={self.distance_metric}, clases={len(self.prototypes)})"

    def get_prototypes_count(self):
        """Retorna el número de prototipos (clases) encontrados"""
        return len(self.prototypes)

    def predict_batch(self, input_vectors):
        """
        Predice para múltiples vectores de entrada.

        Args:
            input_vectors: Lista de vectores de entrada

        Returns:
            Lista de predicciones
        """
        return [self.predict(vec) for vec in input_vectors]
