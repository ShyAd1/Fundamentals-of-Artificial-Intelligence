"""
CONTROLADOR - Lógica de Control
Arquitectura MVC para Sistema de Carga y Manipulación de Datos
"""

from typing import Dict, Any
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.DataModel import DataModel
from View.DataView import DataView


class DataController:
    """Controlador - Maneja la interacción entre el Modelo y la Vista"""
    
    def __init__(self, model: DataModel, view: DataView):
        self.model = model
        self.view = view
        self.saved_models: Dict[str, DataModel] = {}  # Modelos guardados
        
        # Conectar los callbacks de la vista
        self._connect_view_callbacks()
        
        # Inicializar la vista
        self.view.update_status("Sistema listo. Cargue un archivo para comenzar.")
    
    def _connect_view_callbacks(self):
        """Conecta los eventos de la vista con los métodos del controlador"""
        self.view.on_load_file = self.load_file
        self.view.on_analyze_attributes = self.analyze_attributes
        self.view.on_select_columns = self.select_columns
        self.view.on_select_rows = self.select_rows
        self.view.on_save_file = self.save_file
        self.view.on_show_preview = self.show_preview
        
        # Conectar evento de cambio de columna en filtro
        self.view.filter_column_combo.bind('<<ComboboxSelected>>', self._on_filter_column_changed)
    
    def load_file(self, filepath: str, separator: str, has_header: bool):
        """Carga un archivo de datos"""
        if not filepath:
            self.view.show_message("Error", "Debe seleccionar un archivo", "error")
            return
        
        self.view.update_status("Cargando archivo...")
        
        # Cargar en el modelo
        success, message = self.model.load_file(filepath, separator, has_header)
        
        if success:
            self.view.show_message("Éxito", message, "success")
            self.view.update_status("Archivo cargado exitosamente")
            self.view.update_dataset_info(self.model.n_rows, self.model.n_columns)
            
            # Actualizar vista previa
            self.show_preview()
            
            # Actualizar información general
            self.view.show_info(self.model.get_summary())
            
            # Actualizar lista de columnas
            if self.model.headers:
                self.view.update_columns_listbox(self.model.headers)
                self.view.update_filter_columns(self.model.headers)
        else:
            self.view.show_message("Error", message, "error")
            self.view.update_status("Error al cargar archivo")
    
    def show_preview(self):
        """Muestra una vista previa de los datos"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        preview_data = self.model.get_data_preview(100)
        self.view.show_data_preview(preview_data)
        self.view.update_status(f"Mostrando {min(100, self.model.n_rows)} filas de {self.model.n_rows}")
    
    def analyze_attributes(self):
        """Analiza los atributos del dataset"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        self.view.update_status("Analizando atributos...")
        
        success, message, analysis_data = self.model.analyze_attributes()
        
        if success:
            self.view.show_analysis(analysis_data)
            self.view.update_status("Análisis completado")
        else:
            self.view.show_message("Error", message, "error")
            self.view.update_status("Error en el análisis")
    
    def select_columns(self, column_indices: list):
        """Selecciona un subconjunto de columnas"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        if not column_indices:
            self.view.show_message("Advertencia", "Debe seleccionar al menos una columna", "warning")
            return
        
        self.view.update_status("Aplicando selección de columnas...")
        
        success, message, new_model = self.model.select_attributes(list(column_indices))
        
        if success:
            # Preguntar si reemplazar el modelo actual
            replace = self.view.ask_question(
                "Aplicar cambios",
                f"{message}\n¿Desea aplicar estos cambios al dataset actual?"
            )
            
            if replace:
                self.model = new_model
                self.view.show_message("Éxito", "Cambios aplicados exitosamente", "success")
                self.view.update_dataset_info(self.model.n_rows, self.model.n_columns)
                
                # Actualizar la interfaz
                self.show_preview()
                self.view.show_info(self.model.get_summary())
                
                if self.model.headers:
                    self.view.update_columns_listbox(self.model.headers)
                    self.view.update_filter_columns(self.model.headers)
                
                self.view.update_status("Columnas seleccionadas aplicadas")
            else:
                self.view.update_status("Cambios cancelados")
        else:
            self.view.show_message("Error", message, "error")
            self.view.update_status("Error al seleccionar columnas")
    
    def select_rows(self, method: str, **kwargs):
        """Selecciona un subconjunto de filas"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        self.view.update_status("Aplicando selección de filas...")
        
        success = False
        message = ""
        new_model = None
        
        if method == 'indices':
            indices_str = kwargs.get('indices', '')
            try:
                indices = self._parse_indices(indices_str, self.model.n_rows)
                success, message, new_model = self.model.select_rows_by_list(indices)
            except Exception as e:
                self.view.show_message("Error", f"Error al parsear índices: {str(e)}", "error")
                return
        
        elif method == 'range':
            start = kwargs.get('start', 0)
            end = kwargs.get('end', 0)
            success, message, new_model = self.model.select_rows_by_range(start, end)
        
        elif method == 'value':
            column_idx = kwargs.get('column_idx', 0)
            value = kwargs.get('value', '')
            success, message, new_model = self.model.select_rows_by_value(column_idx, value)
        
        if success and new_model:
            # Preguntar si reemplazar el modelo actual
            replace = self.view.ask_question(
                "Aplicar cambios",
                f"{message}\n¿Desea aplicar estos cambios al dataset actual?"
            )
            
            if replace:
                self.model = new_model
                self.view.show_message("Éxito", "Cambios aplicados exitosamente", "success")
                self.view.update_dataset_info(self.model.n_rows, self.model.n_columns)
                
                # Actualizar la interfaz
                self.show_preview()
                self.view.show_info(self.model.get_summary())
                self.view.update_status("Filas seleccionadas aplicadas")
            else:
                self.view.update_status("Cambios cancelados")
        else:
            self.view.show_message("Error", message, "error")
            self.view.update_status("Error al seleccionar filas")
    
    def save_file(self, output_path: str, separator: str):
        """Guarda el dataset actual en un archivo"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        if not output_path:
            self.view.show_message("Error", "Debe especificar una ruta de salida", "error")
            return
        
        self.view.update_status("Guardando archivo...")
        
        success, message = self.model.save_to_file(output_path, separator)
        
        if success:
            self.view.show_message("Éxito", message, "success")
            self.view.update_status("Archivo guardado exitosamente")
        else:
            self.view.show_message("Error", message, "error")
            self.view.update_status("Error al guardar archivo")
    
    def _on_filter_column_changed(self, event=None):
        """Maneja el cambio de columna en el filtro"""
        if self.model.data_matrix is None:
            return
        
        col_idx = self.view.filter_column_combo.current()
        if col_idx >= 0:
            values = self.model.get_column_values(col_idx)
            self.view.update_filter_values(values)
    
    def _parse_indices(self, indices_str: str, max_value: int) -> list:
        """
        Parsea una cadena de índices
        Ejemplos: "0,2,4", "0-3", "0,2-4,6"
        """
        indices = []
        parts = indices_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Rango
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                indices.extend(range(start, min(end + 1, max_value)))
            else:
                # Índice individual
                idx = int(part)
                if 0 <= idx < max_value:
                    indices.append(idx)
        
        return sorted(list(set(indices)))  # Eliminar duplicados y ordenar
    
    def save_model_to_memory(self, name: str):
        """Guarda el modelo actual en memoria"""
        if self.model.data_matrix is None:
            self.view.show_message("Advertencia", "No hay datos cargados", "warning")
            return
        
        self.saved_models[name] = self.model
        self.view.show_message("Éxito", f"Dataset '{name}' guardado en memoria", "success")
    
    def load_model_from_memory(self, name: str):
        """Carga un modelo desde memoria"""
        if name in self.saved_models:
            self.model = self.saved_models[name]
            self.view.update_dataset_info(self.model.n_rows, self.model.n_columns)
            self.show_preview()
            self.view.show_info(self.model.get_summary())
            
            if self.model.headers:
                self.view.update_columns_listbox(self.model.headers)
                self.view.update_filter_columns(self.model.headers)
            
            self.view.show_message("Éxito", f"Dataset '{name}' cargado", "success")
        else:
            self.view.show_message("Error", f"Dataset '{name}' no encontrado", "error")
