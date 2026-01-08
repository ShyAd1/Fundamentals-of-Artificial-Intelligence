"""
Sistema de Carga y Manipulación de Conjuntos de Datos
para Problemas de Inteligencia Artificial
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import os


class DataLoader:
    """Clase para cargar y manipular conjuntos de datos desde archivos de texto plano"""
    
    def __init__(self):
        self.filepath: Optional[str] = None
        self.separator: str = ','
        self.data_matrix: Optional[np.ndarray] = None
        self.headers: Optional[List[str]] = None
        self.n_rows: int = 0
        self.n_columns: int = 0
        self.attribute_types: Dict[int, str] = {}
        self.attribute_stats: Dict[int, Dict[str, Any]] = {}
        
    def load_file(self, filepath: str, separator: str = ',', has_header: bool = True) -> bool:
        """
        Carga un archivo de texto plano
        
        Args:
            filepath: Ruta al archivo
            separator: Carácter separador de datos
            has_header: Si el archivo tiene encabezados
            
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        try:
            if not os.path.exists(filepath):
                print(f"Error: El archivo {filepath} no existe")
                return False
            
            self.filepath = filepath
            self.separator = separator
            
            # Leer el archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                print("Error: El archivo está vacío")
                return False
            
            # Procesar encabezados si existen
            if has_header:
                self.headers = [h.strip() for h in lines[0].strip().split(separator)]
                data_lines = lines[1:]
            else:
                # Generar encabezados automáticos
                first_line = lines[0].strip().split(separator)
                self.headers = [f"Atributo_{i+1}" for i in range(len(first_line))]
                data_lines = lines
            
            # Cargar datos en una lista temporal
            data_list = []
            for line in data_lines:
                line = line.strip()
                if line:  # Ignorar líneas vacías
                    row = [val.strip() for val in line.split(separator)]
                    data_list.append(row)
            
            # Convertir a numpy array (mantener como string inicialmente)
            self.data_matrix = np.array(data_list, dtype=object)
            self.n_rows, self.n_columns = self.data_matrix.shape
            
            print(f"✓ Archivo cargado exitosamente")
            print(f"  - Archivo: {filepath}")
            print(f"  - Separador: '{separator}'")
            print(f"  - Número de atributos (columnas): {self.n_columns}")
            print(f"  - Número de muestras (filas): {self.n_rows}")
            
            return True
            
        except Exception as e:
            print(f"Error al cargar el archivo: {str(e)}")
            return False
    
    def analyze_attributes(self) -> None:
        """Analiza cada atributo para determinar si es cualitativo o cuantitativo"""
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("ANÁLISIS DE ATRIBUTOS")
        print("="*60)
        
        for col_idx in range(self.n_columns):
            column_data = self.data_matrix[:, col_idx]
            attribute_name = self.headers[col_idx] if self.headers else f"Atributo_{col_idx+1}"
            
            # Intentar convertir a numérico
            is_numeric = self._is_numeric_column(column_data)
            
            if is_numeric:
                self.attribute_types[col_idx] = "cuantitativo"
                self._calculate_numeric_stats(col_idx, column_data)
            else:
                self.attribute_types[col_idx] = "cualitativo"
                self._calculate_categorical_stats(col_idx, column_data)
    
    def _is_numeric_column(self, column_data: np.ndarray) -> bool:
        """Determina si una columna contiene datos numéricos"""
        try:
            # Intentar convertir todos los valores a float
            for val in column_data:
                float(val)
            return True
        except (ValueError, TypeError):
            return False
    
    def _calculate_numeric_stats(self, col_idx: int, column_data: np.ndarray) -> None:
        """Calcula estadísticas para atributos cuantitativos"""
        attribute_name = self.headers[col_idx] if self.headers else f"Atributo_{col_idx+1}"
        
        # Convertir a float
        numeric_data = np.array([float(val) for val in column_data])
        
        stats = {
            'tipo': 'cuantitativo',
            'mínimo': np.min(numeric_data),
            'máximo': np.max(numeric_data),
            'promedio': np.mean(numeric_data),
            'desviación_estándar': np.std(numeric_data)
        }
        
        self.attribute_stats[col_idx] = stats
        
        print(f"\n[Columna {col_idx+1}] {attribute_name} - CUANTITATIVO")
        print(f"  Mínimo: {stats['mínimo']:.4f}")
        print(f"  Máximo: {stats['máximo']:.4f}")
        print(f"  Promedio: {stats['promedio']:.4f}")
        print(f"  Desviación estándar: {stats['desviación_estándar']:.4f}")
    
    def _calculate_categorical_stats(self, col_idx: int, column_data: np.ndarray) -> None:
        """Calcula estadísticas para atributos cualitativos"""
        attribute_name = self.headers[col_idx] if self.headers else f"Atributo_{col_idx+1}"
        
        # Obtener categorías únicas
        unique_values, counts = np.unique(column_data, return_counts=True)
        categories = list(unique_values)
        
        stats = {
            'tipo': 'cualitativo',
            'categorías': categories,
            'cantidad_por_categoría': dict(zip(categories, counts.tolist()))
        }
        
        self.attribute_stats[col_idx] = stats
        
        print(f"\n[Columna {col_idx+1}] {attribute_name} - CUALITATIVO")
        print(f"  Categorías encontradas: {len(categories)}")
        for cat, count in zip(categories, counts):
            print(f"    - {cat}: {count} ocurrencias")
    
    def select_attributes(self, attribute_indices: List[int]) -> 'DataLoader':
        """
        Selecciona un subconjunto de atributos (columnas)
        
        Args:
            attribute_indices: Lista de índices de columnas a conservar (0-indexed)
            
        Returns:
            Nuevo objeto DataLoader con el subconjunto de datos
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return self
        
        # Validar índices
        valid_indices = [idx for idx in attribute_indices if 0 <= idx < self.n_columns]
        
        if not valid_indices:
            print("Error: No se proporcionaron índices válidos")
            return self
        
        # Crear nuevo DataLoader
        new_loader = DataLoader()
        new_loader.filepath = self.filepath
        new_loader.separator = self.separator
        new_loader.data_matrix = self.data_matrix[:, valid_indices]
        new_loader.headers = [self.headers[i] for i in valid_indices] if self.headers else None
        new_loader.n_rows = new_loader.data_matrix.shape[0]
        new_loader.n_columns = new_loader.data_matrix.shape[1]
        
        print(f"\n✓ Subconjunto de atributos creado: {len(valid_indices)} columnas seleccionadas")
        
        return new_loader
    
    def select_rows_by_list(self, row_indices: List[int]) -> 'DataLoader':
        """
        Selecciona filas específicas por sus índices
        
        Args:
            row_indices: Lista de índices de filas a conservar (0-indexed)
            
        Returns:
            Nuevo objeto DataLoader con el subconjunto de datos
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return self
        
        # Validar índices
        valid_indices = [idx for idx in row_indices if 0 <= idx < self.n_rows]
        
        if not valid_indices:
            print("Error: No se proporcionaron índices válidos")
            return self
        
        return self._create_subset(valid_indices)
    
    def select_rows_by_range(self, start_idx: int, end_idx: int) -> 'DataLoader':
        """
        Selecciona filas en un rango
        
        Args:
            start_idx: Índice inicial (0-indexed, inclusivo)
            end_idx: Índice final (0-indexed, inclusivo)
            
        Returns:
            Nuevo objeto DataLoader con el subconjunto de datos
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return self
        
        # Validar rango
        start_idx = max(0, start_idx)
        end_idx = min(self.n_rows - 1, end_idx)
        
        if start_idx > end_idx:
            print("Error: Rango inválido")
            return self
        
        row_indices = list(range(start_idx, end_idx + 1))
        
        return self._create_subset(row_indices)
    
    def select_rows_by_value(self, column_idx: int, value: Any) -> 'DataLoader':
        """
        Selecciona filas según el valor de un atributo específico
        
        Args:
            column_idx: Índice de la columna (0-indexed)
            value: Valor a buscar
            
        Returns:
            Nuevo objeto DataLoader con el subconjunto de datos
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return self
        
        if not (0 <= column_idx < self.n_columns):
            print("Error: Índice de columna inválido")
            return self
        
        # Buscar filas que coincidan con el valor
        column_data = self.data_matrix[:, column_idx]
        row_indices = [i for i, val in enumerate(column_data) if val == str(value)]
        
        if not row_indices:
            print(f"Advertencia: No se encontraron filas con valor '{value}' en la columna {column_idx+1}")
            return self
        
        print(f"✓ Encontradas {len(row_indices)} filas con valor '{value}' en columna {column_idx+1}")
        
        return self._create_subset(row_indices)
    
    def _create_subset(self, row_indices: List[int]) -> 'DataLoader':
        """Crea un nuevo DataLoader con un subconjunto de filas"""
        new_loader = DataLoader()
        new_loader.filepath = self.filepath
        new_loader.separator = self.separator
        new_loader.data_matrix = self.data_matrix[row_indices, :]
        new_loader.headers = self.headers.copy() if self.headers else None
        new_loader.n_rows = new_loader.data_matrix.shape[0]
        new_loader.n_columns = new_loader.data_matrix.shape[1]
        
        print(f"\n✓ Subconjunto de datos creado: {len(row_indices)} filas seleccionadas")
        
        return new_loader
    
    def show_data(self, n_rows: int = 10) -> None:
        """
        Muestra las primeras n filas de datos
        
        Args:
            n_rows: Número de filas a mostrar
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("VISTA PREVIA DE DATOS")
        print("="*60)
        
        # Mostrar encabezados
        if self.headers:
            header_line = " | ".join([f"{h[:15]:15}" for h in self.headers])
            print(header_line)
            print("-" * len(header_line))
        
        # Mostrar filas
        rows_to_show = min(n_rows, self.n_rows)
        for i in range(rows_to_show):
            row_line = " | ".join([f"{str(val)[:15]:15}" for val in self.data_matrix[i]])
            print(row_line)
        
        if self.n_rows > n_rows:
            print(f"\n... ({self.n_rows - n_rows} filas más)")
    
    def get_summary(self) -> None:
        """Muestra un resumen del conjunto de datos"""
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("RESUMEN DEL CONJUNTO DE DATOS")
        print("="*60)
        print(f"Archivo: {self.filepath}")
        print(f"Separador: '{self.separator}'")
        print(f"Dimensiones: {self.n_rows} filas × {self.n_columns} columnas")
        print(f"Total de elementos: {self.n_rows * self.n_columns}")
        
        if self.headers:
            print(f"\nAtributos: {', '.join(self.headers)}")
    
    def save_to_file(self, output_path: str, separator: str = None) -> bool:
        """
        Guarda el conjunto de datos actual en un archivo
        
        Args:
            output_path: Ruta del archivo de salida
            separator: Separador a usar (usa el original si no se especifica)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        if self.data_matrix is None:
            print("Error: No hay datos cargados")
            return False
        
        sep = separator if separator else self.separator
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Escribir encabezados
                if self.headers:
                    f.write(sep.join(self.headers) + '\n')
                
                # Escribir datos
                for row in self.data_matrix:
                    f.write(sep.join([str(val) for val in row]) + '\n')
            
            print(f"✓ Datos guardados exitosamente en: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error al guardar el archivo: {str(e)}")
            return False
