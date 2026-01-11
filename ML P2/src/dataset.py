"""
Módulo para gestionar conjuntos de datos.
Permite cargar, almacenar y recuperar datos de entrenamiento.
Implementación completamente manual sin bibliotecas externas.
"""


class Dataset:
    """
    Clase para gestionar conjuntos de datos de entrenamiento.
    Permite definir tamaños de vectores de entrada/salida y almacenar pares entrada-salida.
    Implementación manual sin dependencias externas.
    """

    def __init__(self, input_size, output_size):
        """
        Inicializa un dataset con tamaños específicos.

        Args:
            input_size: Dimensión del vector de entrada (debe ser > 0)
            output_size: Dimensión del vector de salida (debe ser > 0)

        Raises:
            ValueError: Si los tamaños no son positivos
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
            input_vector: Vector de entrada (lista de números)
            output_vector: Vector de salida (lista de números)

        Raises:
            ValueError: Si los tamaños no coinciden con los definidos
        """
        if len(input_vector) != self.input_size:
            raise ValueError(
                f"El vector de entrada debe tener {self.input_size} dimensiones"
            )
        if len(output_vector) != self.output_size:
            raise ValueError(
                f"El vector de salida debe tener {self.output_size} dimensiones"
            )

        # Crear copias de las listas para evitar referencias
        input_copy = [float(x) for x in input_vector]
        output_copy = [float(x) for x in output_vector]

        self.data.append((input_copy, output_copy))

    def load_from_file(self, filepath):
        """
        Carga datos desde un archivo de texto plano.

        Formato esperado: cada línea contiene entrada y salida separadas por |
        Ejemplo: 1.0,2.0,3.0 | 0.5,1.5
        Las líneas vacías y las que empiezan con # se ignoran (comentarios).

        Args:
            filepath: Ruta del archivo

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato es incorrecto
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                line_count = 0
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith("#"):
                        continue

                    try:
                        # Separar entrada y salida
                        parts = line.split("|")
                        if len(parts) != 2:
                            raise ValueError(
                                f"Línea {line_num}: Se esperaba formato 'entrada | salida'"
                            )

                        input_str = parts[0].strip()
                        output_str = parts[1].strip()

                        # Parsear entrada
                        input_vector = self._parse_vector(input_str)
                        # Parsear salida
                        output_vector = self._parse_vector(output_str)

                        # Agregar al dataset
                        self.add_sample(input_vector, output_vector)
                        line_count += 1

                    except ValueError as e:
                        raise ValueError(
                            f"Error al procesar línea {line_num}: {str(e)}"
                        )

            print(f"✓ Dataset cargado: {line_count} muestras desde {filepath}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
        except Exception as e:
            raise Exception(f"Error al cargar dataset: {str(e)}")

    def _parse_vector(self, vector_str):
        """
        Parsea una cadena de texto a un vector de números.
        Implementación manual del parseo.

        Args:
            vector_str: Cadena con números separados por comas (ej: "1.5, 2.3, 4.1")

        Returns:
            Lista de números flotantes

        Raises:
            ValueError: Si el formato es incorrecto
        """
        if not vector_str:
            raise ValueError("Cadena de vector vacía")

        # Dividir por comas
        parts = vector_str.split(",")
        vector = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            try:
                number = float(part)
                vector.append(number)
            except ValueError:
                raise ValueError(f"No se pudo convertir '{part}' a número")

        return vector

    def save_to_file(self, filepath):
        """
        Guarda el dataset en un archivo de texto plano.

        Args:
            filepath: Ruta del archivo de destino
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # Escribir encabezado con información del dataset
                f.write(
                    f"# Dataset con {self.input_size} entrada(s) y {self.output_size} salida(s)\n"
                )
                f.write(f"# Total de muestras: {len(self.data)}\n")
                f.write(f"# Formato: entrada | salida\n")
                f.write("#\n")

                # Escribir cada muestra
                for input_vec, output_vec in self.data:
                    # Convertir vectores a cadenas
                    input_str = self._vector_to_string(input_vec)
                    output_str = self._vector_to_string(output_vec)

                    f.write(f"{input_str} | {output_str}\n")

            print(f"✓ Dataset guardado: {len(self.data)} muestras en {filepath}")

        except Exception as e:
            raise Exception(f"Error al guardar dataset: {str(e)}")

    def _vector_to_string(self, vector):
        """
        Convierte un vector a cadena de texto.
        Implementación manual del formateo.

        Args:
            vector: Lista de números

        Returns:
            Cadena con números separados por comas
        """
        # Formatear cada número y unirlos con comas
        str_parts = []
        for num in vector:
            # Formatear con precisión adecuada
            if num == int(num):
                str_parts.append(str(int(num)))
            else:
                str_parts.append(f"{num:.6f}".rstrip("0").rstrip("."))

        return ", ".join(str_parts)

    def get_samples(self):
        """
        Retorna todas las muestras del dataset.

        Returns:
            Lista de tuplas (input_vector, output_vector)
        """
        return self.data

    def get_size(self):
        """
        Retorna el número de muestras en el dataset.

        Returns:
            Número de muestras (entero)
        """
        return len(self.data)

    def clear(self):
        """
        Limpia todas las muestras del dataset.
        Mantiene las dimensiones definidas.
        """
        self.data = []
        print("✓ Dataset limpiado")

    def get_statistics(self):
        """
        Calcula estadísticas básicas del dataset.
        Implementación manual sin bibliotecas externas.

        Returns:
            Diccionario con estadísticas del dataset
        """
        if len(self.data) == 0:
            return {
                "size": 0,
                "input_min": None,
                "input_max": None,
                "input_mean": None,
                "output_min": None,
                "output_max": None,
                "output_mean": None,
            }

        # Inicializar acumuladores
        input_sums = [0.0] * self.input_size
        output_sums = [0.0] * self.output_size

        input_mins = [float("inf")] * self.input_size
        input_maxs = [float("-inf")] * self.input_size

        output_mins = [float("inf")] * self.output_size
        output_maxs = [float("-inf")] * self.output_size

        # Recorrer todas las muestras
        for input_vec, output_vec in self.data:
            for i in range(self.input_size):
                val = input_vec[i]
                input_sums[i] += val
                if val < input_mins[i]:
                    input_mins[i] = val
                if val > input_maxs[i]:
                    input_maxs[i] = val

            for i in range(self.output_size):
                val = output_vec[i]
                output_sums[i] += val
                if val < output_mins[i]:
                    output_mins[i] = val
                if val > output_maxs[i]:
                    output_maxs[i] = val

        # Calcular promedios
        n = len(self.data)
        input_means = [s / n for s in input_sums]
        output_means = [s / n for s in output_sums]

        return {
            "size": n,
            "input_min": input_mins,
            "input_max": input_maxs,
            "input_mean": input_means,
            "output_min": output_mins,
            "output_max": output_maxs,
            "output_mean": output_means,
        }

    def __str__(self):
        """
        Representación en cadena del dataset.

        Returns:
            Cadena descriptiva del dataset
        """
        return f"Dataset(entrada={self.input_size}, salida={self.output_size}, muestras={len(self.data)})"

    def __repr__(self):
        """
        Representación técnica del dataset.

        Returns:
            Cadena técnica del dataset
        """
        return self.__str__()
