"""
Módulo para gestionar conjuntos de datos.
Permite cargar, almacenar y recuperar datos de entrenamiento.
"""

import math
from typing import List, Tuple, Optional


class Dataset:
    """
    Clase para gestionar conjuntos de datos de entrenamiento.
    Permite definir tamaños de vectores de entrada/salida y almacenar pares entrada-salida.
    """
    
    def __init__(self, input_size: int, output_size: int):
        """
        Inicializa un dataset con tamaños específicos.
        
        Args:
            input_size: Dimensión del vector de entrada
            output_size: Dimensión del vector de salida
        """
        if input_size <= 0 or output_size <= 0:
            raise ValueError("Los tamaños de entrada y salida deben ser positivos")
        
        self.input_size = input_size
        self.output_size = output_size
        self.data: List[Tuple[List[float], List[float]]] = []
    
    def add_sample(self, input_vector: List[float], output_vector: List[float]) -> None:
        """
        Agrega un par entrada-salida al dataset.
        
        Args:
            input_vector: Vector de entrada
            output_vector: Vector de salida
            
        Raises:
            ValueError: Si los tamaños no coinciden con los definidos
        """
        if len(input_vector) != self.input_size:
            raise ValueError(f"El vector de entrada debe tener {self.input_size} dimensiones")
        if len(output_vector) != self.output_size:
            raise ValueError(f"El vector de salida debe tener {self.output_size} dimensiones")
        
        self.data.append((list(input_vector), list(output_vector)))
    
    def load_from_file(self, filepath: str) -> None:
        """
        Carga datos desde un archivo de texto plano.
        Formato esperado: cada línea contiene entrada y salida separadas por |
        Ejemplo: 1.0,2.0,3.0 | 0.5,1.5
        
        Args:
            filepath: Ruta del archivo
        """
        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        parts = line.split('|')
                        if len(parts) != 2:
                            raise ValueError(f"Línea {line_num}: Se esperaba formato 'entrada | salida'")
                        
                        input_str = parts[0].strip()
                        output_str = parts[1].strip()
                        
                        input_vector = [float(x.strip()) for x in input_str.split(',')]
                        output_vector = [float(x.strip()) for x in output_str.split(',')]
                        
                        self.add_sample(input_vector, output_vector)
                    except ValueError as e:
                        raise ValueError(f"Error al procesar línea {line_num}: {str(e)}")
            
            print(f"✓ Dataset cargado: {len(self.data)} muestras")
        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    
    def save_to_file(self, filepath: str) -> None:
        """
        Guarda el dataset en un archivo de texto plano.
        
        Args:
            filepath: Ruta del archivo de destino
        """
        with open(filepath, 'w') as f:
            f.write(f"# Dataset con {self.input_size} entrada(s) y {self.output_size} salida(s)\n")
            for input_vec, output_vec in self.data:
                input_str = ','.join(str(x) for x in input_vec)
                output_str = ','.join(str(x) for x in output_vec)
                f.write(f"{input_str} | {output_str}\n")
        print(f"✓ Dataset guardado: {len(self.data)} muestras")
    
    def get_samples(self) -> List[Tuple[List[float], List[float]]]:
        """Retorna todas las muestras del dataset"""
        return self.data
    
    def get_size(self) -> int:
        """Retorna el número de muestras"""
        return len(self.data)
    
    def clear(self) -> None:
        """Limpia todas las muestras del dataset"""
        self.data = []
    
    def __str__(self) -> str:
        return f"Dataset(entrada={self.input_size}, salida={self.output_size}, muestras={len(self.data)})"
