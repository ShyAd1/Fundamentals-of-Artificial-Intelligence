"""
Módulo para calcular diferentes métricas de distancia.
Implementación completamente manual sin bibliotecas externas.
"""


def sqrt(n):
    """
    Calcula la raíz cuadrada usando el método de Newton-Raphson.
    Implementación manual sin usar librerías matemáticas.

    Args:
        n: Número del cual calcular la raíz cuadrada

    Returns:
        Raíz cuadrada aproximada de n
    """
    if n < 0:
        raise ValueError("No se puede calcular raíz cuadrada de números negativos")
    if n == 0:
        return 0

    # Método Newton-Raphson: x_nuevo = (x_viejo + n/x_viejo) / 2
    x = n
    y = (x + 1) / 2
    epsilon = 1e-10  # Precisión

    while abs(x - y) > epsilon:
        x = y
        y = (x + n / x) / 2

    return y


def abs_value(x):
    """
    Calcula el valor absoluto de un número.
    Implementación manual sin usar abs() de Python.

    Args:
        x: Número

    Returns:
        Valor absoluto de x
    """
    return x if x >= 0 else -x


class DistanceMetrics:
    """
    Clase con métodos estáticos para calcular diferentes distancias.
    Todas las implementaciones son manuales sin bibliotecas externas.
    """

    @staticmethod
    def euclidean(point1, point2):
        """
        Calcula la distancia euclidiana entre dos puntos.

        Formula: d = sqrt(sum((p1[i] - p2[i])^2))

        Args:
            point1: Primer vector (lista de números)
            point2: Segundo vector (lista de números)

        Returns:
            Distancia euclidiana (float)
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")

        # Calcular suma de cuadrados de diferencias
        sum_squares = 0
        for i in range(len(point1)):
            diff = point1[i] - point2[i]
            sum_squares += diff * diff

        return sqrt(sum_squares)

    @staticmethod
    def manhattan(point1, point2):
        """
        Calcula la distancia de Manhattan (distancia L1) entre dos puntos.
        También conocida como distancia taxicab o city block.

        Formula: d = sum(|p1[i] - p2[i]|)

        Args:
            point1: Primer vector (lista de números)
            point2: Segundo vector (lista de números)

        Returns:
            Distancia de Manhattan (float)
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")

        # Calcular suma de diferencias absolutas
        sum_abs = 0
        for i in range(len(point1)):
            diff = point1[i] - point2[i]
            sum_abs += abs_value(diff)

        return sum_abs

    @staticmethod
    def chebyshev(point1, point2):
        """
        Calcula la distancia de Chebyshev entre dos puntos.
        También conocida como distancia L-infinito o distancia del tablero de ajedrez.

        Formula: d = max(|p1[i] - p2[i]|)

        Args:
            point1: Primer vector (lista de números)
            point2: Segundo vector (lista de números)

        Returns:
            Distancia de Chebyshev (float)
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")

        # Encontrar la diferencia máxima
        max_diff = 0
        for i in range(len(point1)):
            diff = abs_value(point1[i] - point2[i])
            if diff > max_diff:
                max_diff = diff

        return max_diff

    @staticmethod
    def minkowski(point1, point2, p=3):
        """
        Calcula la distancia de Minkowski entre dos puntos.
        Generalización de varias distancias (p=1: Manhattan, p=2: Euclidiana).

        Formula: d = (sum(|p1[i] - p2[i]|^p))^(1/p)

        Args:
            point1: Primer vector (lista de números)
            point2: Segundo vector (lista de números)
            p: Parámetro de orden (por defecto 3)

        Returns:
            Distancia de Minkowski (float)
        """
        if len(point1) != len(point2):
            raise ValueError("Los vectores deben tener la misma dimensión")
        if p <= 0:
            raise ValueError("El parámetro p debe ser positivo")

        # Calcular suma de diferencias elevadas a la p
        sum_powered = 0
        for i in range(len(point1)):
            diff = abs_value(point1[i] - point2[i])
            sum_powered += diff**p

        # Calcular raíz p-ésima
        return sum_powered ** (1 / p)

    @staticmethod
    def get_distance_function(metric_name):
        """
        Retorna la función de distancia correspondiente al nombre.

        Args:
            metric_name: Nombre de la métrica ('euclidean', 'manhattan', 'chebyshev', 'minkowski')

        Returns:
            Función de distancia
        """
        metrics = {
            "euclidean": DistanceMetrics.euclidean,
            "euclidiana": DistanceMetrics.euclidean,
            "manhattan": DistanceMetrics.manhattan,
            "chebyshev": DistanceMetrics.chebyshev,
            "minkowski": DistanceMetrics.minkowski,
        }

        metric_lower = metric_name.lower()
        if metric_lower not in metrics:
            raise ValueError(
                f"Métrica de distancia no reconocida: {metric_name}. Opciones: {', '.join(metrics.keys())}"
            )

        return metrics[metric_lower]
