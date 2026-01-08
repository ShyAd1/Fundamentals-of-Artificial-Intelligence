"""
MODELO - Capa de Datos
Arquitectura MVC para Sistema de Carga y Manipulación de Datos
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import os


class DataModel:
    """Modelo de datos - Maneja toda la lógica de negocio y manipulación de datos"""
    
    def __init__(self):
        self.filepath: Optional[str] = None
        self.separator: str = ','
        self.data_matrix: Optional[np.ndarray] = None
        self.headers: Optional[List[str]] = None
        self.n_rows: int = 0
        self.n_columns: int = 0
        self.attribute_types: Dict[int, str] = {}
        self.attribute_stats: Dict[int, Dict[str, Any]] = {}
        self.has_header: bool = True
        
    def load_file(self, filepath: str, separator: str = ',', has_header: bool = True) -> Tuple[bool, str]:
        """
        Carga un archivo de texto plano
        
        Args:
            filepath: Ruta al archivo
            separator: Carácter separador de datos
            has_header: Si el archivo tiene encabezados
            
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if not os.path.exists(filepath):
                return False, f"El archivo {filepath} no existe"
            
            self.filepath = filepath
            self.separator = separator
            self.has_header = has_header
            
            # Leer el archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return False, "El archivo está vacío"
            
            # Procesar encabezados si existen
            if has_header:
                self.headers = [h.strip() for h in lines[0].strip().split(separator)]
                data_lines = lines[1:]
            else:
                first_line = lines[0].strip().split(separator)
                self.headers = [f"Atributo_{i+1}" for i in range(len(first_line))]
                data_lines = lines
            
            # Cargar datos en una lista temporal
            data_list = []
            for line in data_lines:
                line = line.strip()
                if line:
                    row = [val.strip() for val in line.split(separator)]
                    data_list.append(row)
            
            if not data_list:
                return False, "No se encontraron datos en el archivo"
            
            # Convertir a numpy array
            self.data_matrix = np.array(data_list, dtype=object)
            self.n_rows, self.n_columns = self.data_matrix.shape
            
            # Limpiar estadísticas anteriores
            self.attribute_types.clear()
            self.attribute_stats.clear()
            
            message = f"Archivo cargado exitosamente\n"
            message += f"Atributos: {self.n_columns}\n"
            message += f"Muestras: {self.n_rows}"
            
            return True, message
            
        except Exception as e:
            return False, f"Error al cargar el archivo: {str(e)}"
    
    def analyze_attributes(self) -> Tuple[bool, str, Dict[int, Dict[str, Any]]]:
        """
        Analiza cada atributo para determinar si es cualitativo o cuantitativo
        
        Returns:
            Tuple (éxito, mensaje, diccionario con estadísticas)
        """
        if self.data_matrix is None:
            return False, "No hay datos cargados", {}
        
        stats_summary = {}
        
        for col_idx in range(self.n_columns):
            column_data = self.data_matrix[:, col_idx]
            attribute_name = self.headers[col_idx] if self.headers else f"Atributo_{col_idx+1}"
            
            is_numeric = self._is_numeric_column(column_data)
            
            if is_numeric:
                self.attribute_types[col_idx] = "cuantitativo"
                stats = self._calculate_numeric_stats(col_idx, column_data)
            else:
                self.attribute_types[col_idx] = "cualitativo"
                stats = self._calculate_categorical_stats(col_idx, column_data)
            
            self.attribute_stats[col_idx] = stats
            stats_summary[col_idx] = {
                'nombre': attribute_name,
                'stats': stats
            }
        
        return True, "Análisis completado", stats_summary
    
    def _is_numeric_column(self, column_data: np.ndarray) -> bool:
        """Determina si una columna contiene datos numéricos"""
        if len(column_data) == 0:
            return False
        
        numeric_count = 0
        total_count = 0
        
        for val in column_data:
            val_str = str(val).strip()
            if not val_str or val_str.lower() in ['', 'nan', 'none', 'null']:
                continue
            
            total_count += 1
            try:
                float(val_str)
                numeric_count += 1
            except (ValueError, TypeError):
                pass
        
        # Si al menos el 80% de los valores no vacíos son numéricos, es cuantitativo
        if total_count == 0:
            return False
        
        return (numeric_count / total_count) >= 0.8
    
    def _calculate_numeric_stats(self, col_idx: int, column_data: np.ndarray) -> Dict[str, Any]:
        """Calcula estadísticas para atributos cuantitativos"""
        # Filtrar solo valores numéricos válidos
        numeric_values = []
        for val in column_data:
            val_str = str(val).strip()
            if val_str and val_str.lower() not in ['nan', 'none', 'null', '']:
                try:
                    numeric_values.append(float(val_str))
                except (ValueError, TypeError):
                    pass
        
        if not numeric_values:
            return {
                'tipo': 'cuantitativo',
                'mínimo': 0.0,
                'máximo': 0.0,
                'promedio': 0.0,
                'desviación_estándar': 0.0,
                'valores_válidos': 0
            }
        
        numeric_data = np.array(numeric_values)
        
        return {
            'tipo': 'cuantitativo',
            'mínimo': float(np.min(numeric_data)),
            'máximo': float(np.max(numeric_data)),
            'promedio': float(np.mean(numeric_data)),
            'desviación_estándar': float(np.std(numeric_data)),
            'valores_válidos': len(numeric_values)
        }
    
    def _calculate_categorical_stats(self, col_idx: int, column_data: np.ndarray) -> Dict[str, Any]:
        """Calcula estadísticas para atributos cualitativos"""
        unique_values, counts = np.unique(column_data, return_counts=True)
        categories = list(unique_values)
        
        return {
            'tipo': 'cualitativo',
            'categorías': categories,
            'cantidad_por_categoría': dict(zip(categories, counts.tolist()))
        }
    
    def select_attributes(self, attribute_indices: List[int]) -> Tuple[bool, str, 'DataModel']:
        """
        Selecciona un subconjunto de atributos (columnas)
        
        Args:
            attribute_indices: Lista de índices de columnas a conservar
            
        Returns:
            Tuple (éxito, mensaje, nuevo modelo)
        """
        if self.data_matrix is None:
            return False, "No hay datos cargados", None
        
        valid_indices = [idx for idx in attribute_indices if 0 <= idx < self.n_columns]
        
        if not valid_indices:
            return False, "No se proporcionaron índices válidos", None
        
        new_model = DataModel()
        new_model.filepath = self.filepath
        new_model.separator = self.separator
        new_model.has_header = self.has_header
        new_model.data_matrix = self.data_matrix[:, valid_indices]
        new_model.headers = [self.headers[i] for i in valid_indices] if self.headers else None
        new_model.n_rows = new_model.data_matrix.shape[0]
        new_model.n_columns = new_model.data_matrix.shape[1]
        
        message = f"Subconjunto creado: {len(valid_indices)} columnas"
        return True, message, new_model
    
    def select_rows_by_list(self, row_indices: List[int]) -> Tuple[bool, str, 'DataModel']:
        """Selecciona filas específicas por sus índices"""
        if self.data_matrix is None:
            return False, "No hay datos cargados", None
        
        valid_indices = [idx for idx in row_indices if 0 <= idx < self.n_rows]
        
        if not valid_indices:
            return False, "No se proporcionaron índices válidos", None
        
        return self._create_subset(valid_indices)
    
    def select_rows_by_range(self, start_idx: int, end_idx: int) -> Tuple[bool, str, 'DataModel']:
        """Selecciona filas en un rango"""
        if self.data_matrix is None:
            return False, "No hay datos cargados", None
        
        start_idx = max(0, start_idx)
        end_idx = min(self.n_rows - 1, end_idx)
        
        if start_idx > end_idx:
            return False, "Rango inválido", None
        
        row_indices = list(range(start_idx, end_idx + 1))
        return self._create_subset(row_indices)
    
    def select_rows_by_value(self, column_idx: int, value: Any) -> Tuple[bool, str, 'DataModel']:
        """Selecciona filas según el valor de un atributo específico"""
        if self.data_matrix is None:
            return False, "No hay datos cargados", None
        
        if not (0 <= column_idx < self.n_columns):
            return False, "Índice de columna inválido", None
        
        column_data = self.data_matrix[:, column_idx]
        row_indices = [i for i, val in enumerate(column_data) if val == str(value)]
        
        if not row_indices:
            return False, f"No se encontraron filas con valor '{value}'", None
        
        return self._create_subset(row_indices)
    
    def _create_subset(self, row_indices: List[int]) -> Tuple[bool, str, 'DataModel']:
        """Crea un nuevo DataModel con un subconjunto de filas"""
        new_model = DataModel()
        new_model.filepath = self.filepath
        new_model.separator = self.separator
        new_model.has_header = self.has_header
        new_model.data_matrix = self.data_matrix[row_indices, :]
        new_model.headers = self.headers.copy() if self.headers else None
        new_model.n_rows = new_model.data_matrix.shape[0]
        new_model.n_columns = new_model.data_matrix.shape[1]
        
        message = f"Subconjunto creado: {len(row_indices)} filas"
        return True, message, new_model
    
    def get_data_preview(self, n_rows: int = 10) -> List[List[str]]:
        """Obtiene una vista previa de los datos"""
        if self.data_matrix is None:
            return []
        
        rows_to_show = min(n_rows, self.n_rows)
        preview = []
        
        if self.headers:
            preview.append(self.headers)
        
        for i in range(rows_to_show):
            preview.append([str(val) for val in self.data_matrix[i]])
        
        return preview
    
    def get_column_values(self, column_idx: int) -> List[str]:
        """Obtiene los valores únicos de una columna"""
        if self.data_matrix is None or not (0 <= column_idx < self.n_columns):
            return []
        
        unique_values = np.unique(self.data_matrix[:, column_idx])
        return list(unique_values)
    
    def save_to_file(self, output_path: str, separator: str = None) -> Tuple[bool, str]:
        """
        Guarda el conjunto de datos actual en un archivo
        
        Args:
            output_path: Ruta del archivo de salida
            separator: Separador a usar
            
        Returns:
            Tuple (éxito, mensaje)
        """
        if self.data_matrix is None:
            return False, "No hay datos cargados"
        
        sep = separator if separator else self.separator
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if self.headers:
                    f.write(sep.join(self.headers) + '\n')
                
                for row in self.data_matrix:
                    f.write(sep.join([str(val) for val in row]) + '\n')
            
            return True, f"Datos guardados en: {output_path}"
            
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del conjunto de datos"""
        if self.data_matrix is None:
            return {}
        
        return {
            'filepath': self.filepath,
            'separator': self.separator,
            'n_rows': self.n_rows,
            'n_columns': self.n_columns,
            'headers': self.headers,
            'total_elements': self.n_rows * self.n_columns
        }
