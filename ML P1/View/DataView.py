"""
VISTA - Interfaz Gráfica de Usuario (GUI)
Arquitectura MVC para Sistema de Carga y Manipulación de Datos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Callable, Dict, List, Any


class DataView:
    """Vista - Interfaz gráfica con Tkinter"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Carga y Manipulación de Datos - IA")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables
        self.filepath_var = tk.StringVar()
        self.separator_var = tk.StringVar(value=',')
        self.has_header_var = tk.BooleanVar(value=True)
        
        # Callbacks (se asignarán desde el controlador)
        self.on_load_file: Callable = None
        self.on_analyze_attributes: Callable = None
        self.on_select_columns: Callable = None
        self.on_select_rows: Callable = None
        self.on_save_file: Callable = None
        self.on_show_preview: Callable = None
        self.on_apply_subset: Callable = None
        
        self._create_ui()
        
    def _create_ui(self):
        """Crea la interfaz gráfica completa"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestañas
        self.tab_load = ttk.Frame(self.notebook)
        self.tab_analyze = ttk.Frame(self.notebook)
        self.tab_filter = ttk.Frame(self.notebook)
        self.tab_export = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_load, text="📁 Cargar Datos")
        self.notebook.add(self.tab_analyze, text="🔍 Análisis")
        self.notebook.add(self.tab_filter, text="📊 Filtrado")
        self.notebook.add(self.tab_export, text="💾 Exportar")
        
        # Crear contenido de cada pestaña
        self._create_load_tab()
        self._create_analyze_tab()
        self._create_filter_tab()
        self._create_export_tab()
        
        # Barra de estado
        self._create_status_bar()
    
    def _create_load_tab(self):
        """Crea la pestaña de carga de archivos"""
        # Frame superior - Selección de archivo
        file_frame = ttk.LabelFrame(self.tab_load, text="Seleccionar Archivo", padding=15)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Ruta del archivo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.filepath_var, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Examinar...", command=self._browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame medio - Opciones de carga
        options_frame = ttk.LabelFrame(self.tab_load, text="Opciones de Carga", padding=15)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(options_frame, text="Separador:").grid(row=0, column=0, sticky=tk.W, pady=5)
        separator_combo = ttk.Combobox(options_frame, textvariable=self.separator_var, width=15, state='readonly')
        separator_combo['values'] = ('Coma (,)', 'Punto y coma (;)', 'Tabulador', 'Espacio')
        separator_combo.current(0)
        separator_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        separator_combo.bind('<<ComboboxSelected>>', self._update_separator)
        
        ttk.Checkbutton(options_frame, text="El archivo tiene encabezados", 
                       variable=self.has_header_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botón de cargar
        load_btn = ttk.Button(options_frame, text="🔄 CARGAR ARCHIVO", command=self._load_file_click)
        load_btn.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Frame inferior - Vista previa
        preview_frame = ttk.LabelFrame(self.tab_load, text="Vista Previa de Datos", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para mostrar datos
        self.data_tree = ttk.Treeview(preview_frame, show='tree headings', height=15)
        scrollbar_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        scrollbar_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.data_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Botón actualizar vista previa
        ttk.Button(preview_frame, text="🔄 Actualizar Vista Previa", 
                  command=self._refresh_preview).grid(row=2, column=0, pady=10)
    
    def _create_analyze_tab(self):
        """Crea la pestaña de análisis de atributos"""
        # Frame superior - Información general
        info_frame = ttk.LabelFrame(self.tab_analyze, text="Información del Dataset", padding=15)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_text = tk.Text(info_frame, height=5, wrap=tk.WORD, font=('Consolas', 10))
        self.info_text.pack(fill=tk.X, pady=5)
        
        # Botón analizar
        ttk.Button(info_frame, text="🔍 ANALIZAR ATRIBUTOS", 
                  command=self._analyze_click).pack(pady=10)
        
        # Frame inferior - Análisis detallado
        analysis_frame = ttk.LabelFrame(self.tab_analyze, text="Análisis Detallado de Atributos", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, wrap=tk.WORD, 
                                                       font=('Consolas', 9), height=25)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_filter_tab(self):
        """Crea la pestaña de filtrado de datos"""
        # Frame izquierdo - Selección de columnas
        left_frame = ttk.Frame(self.tab_filter)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns_frame = ttk.LabelFrame(left_frame, text="Seleccionar Columnas", padding=10)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(columns_frame, text="Columnas disponibles:").pack(anchor=tk.W, pady=5)
        
        # Listbox para columnas
        self.columns_listbox = tk.Listbox(columns_frame, selectmode=tk.MULTIPLE, height=15)
        scrollbar_cols = ttk.Scrollbar(columns_frame, orient=tk.VERTICAL, command=self.columns_listbox.yview)
        self.columns_listbox.configure(yscrollcommand=scrollbar_cols.set)
        self.columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_cols.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(columns_frame, text="✓ Aplicar Selección de Columnas", 
                  command=self._apply_column_selection).pack(pady=10)
        
        # Frame derecho - Selección de filas
        right_frame = ttk.Frame(self.tab_filter)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        rows_frame = ttk.LabelFrame(right_frame, text="Seleccionar Filas", padding=10)
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        # Método 1: Por índices
        method1_frame = ttk.LabelFrame(rows_frame, text="Método 1: Por Índices", padding=10)
        method1_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(method1_frame, text="Índices (ej: 0,5,10-15):").pack(anchor=tk.W)
        self.indices_entry = ttk.Entry(method1_frame, width=40)
        self.indices_entry.pack(fill=tk.X, pady=5)
        ttk.Button(method1_frame, text="Aplicar", 
                  command=lambda: self._apply_row_selection('indices')).pack(pady=5)
        
        # Método 2: Por rango
        method2_frame = ttk.LabelFrame(rows_frame, text="Método 2: Por Rango", padding=10)
        method2_frame.pack(fill=tk.X, pady=5)
        
        range_subframe = ttk.Frame(method2_frame)
        range_subframe.pack(fill=tk.X)
        ttk.Label(range_subframe, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.range_start_entry = ttk.Entry(range_subframe, width=10)
        self.range_start_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(range_subframe, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.range_end_entry = ttk.Entry(range_subframe, width=10)
        self.range_end_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(method2_frame, text="Aplicar", 
                  command=lambda: self._apply_row_selection('range')).pack(pady=5)
        
        # Método 3: Por valor
        method3_frame = ttk.LabelFrame(rows_frame, text="Método 3: Por Valor de Columna", padding=10)
        method3_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(method3_frame, text="Columna:").pack(anchor=tk.W)
        self.filter_column_combo = ttk.Combobox(method3_frame, state='readonly', width=30)
        self.filter_column_combo.pack(fill=tk.X, pady=5)
        self.filter_column_combo.bind('<<ComboboxSelected>>', self._update_filter_values)
        
        ttk.Label(method3_frame, text="Valor:").pack(anchor=tk.W)
        self.filter_value_combo = ttk.Combobox(method3_frame, state='readonly', width=30)
        self.filter_value_combo.pack(fill=tk.X, pady=5)
        
        ttk.Button(method3_frame, text="Aplicar", 
                  command=lambda: self._apply_row_selection('value')).pack(pady=5)
    
    def _create_export_tab(self):
        """Crea la pestaña de exportación"""
        export_frame = ttk.LabelFrame(self.tab_export, text="Exportar Dataset", padding=20)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Resumen del dataset actual
        ttk.Label(export_frame, text="Dataset Actual:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=10)
        
        self.export_info_text = tk.Text(export_frame, height=8, wrap=tk.WORD, font=('Consolas', 10))
        self.export_info_text.pack(fill=tk.X, pady=10)
        
        # Opciones de exportación
        options_frame = ttk.Frame(export_frame)
        options_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(options_frame, text="Archivo de salida:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.export_path_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.export_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(options_frame, text="Examinar...", command=self._browse_export_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Separador:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.export_separator_var = tk.StringVar(value=',')
        export_sep_combo = ttk.Combobox(options_frame, textvariable=self.export_separator_var, 
                                       width=20, state='readonly')
        export_sep_combo['values'] = ('Coma (,)', 'Punto y coma (;)', 'Tabulador')
        export_sep_combo.current(0)
        export_sep_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botón exportar
        ttk.Button(export_frame, text="💾 EXPORTAR DATOS", 
                  command=self._export_click, style='Accent.TButton').pack(pady=20)
    
    def _create_status_bar(self):
        """Crea la barra de estado en la parte inferior"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Listo", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.dataset_info_label = ttk.Label(status_frame, text="Sin datos cargados", anchor=tk.E)
        self.dataset_info_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # Métodos auxiliares
    def _browse_file(self):
        """Abre el diálogo para seleccionar archivo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("Archivos CSV", "*.csv"), 
                      ("Archivos de texto", "*.txt"),
                      ("Todos los archivos", "*.*")]
        )
        if filename:
            self.filepath_var.set(filename)
    
    def _browse_export_file(self):
        """Abre el diálogo para guardar archivo"""
        filename = filedialog.asksaveasfilename(
            title="Guardar datos como",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), 
                      ("Archivos de texto", "*.txt"),
                      ("Todos los archivos", "*.*")]
        )
        if filename:
            self.export_path_var.set(filename)
    
    def _update_separator(self, event=None):
        """Actualiza el separador según la selección"""
        # No hacer nada aquí, el mapeo se hace en _load_file_click
        pass
    
    def _load_file_click(self):
        """Maneja el clic en el botón de cargar"""
        if self.on_load_file:
            filepath = self.filepath_var.get()
            # Mapear el texto del separador al carácter real
            sep_map = {
                'Coma (,)': ',',
                'Punto y coma (;)': ';',
                'Tabulador': '\t',
                'Espacio': ' '
            }
            separator_text = self.separator_var.get()
            separator = sep_map.get(separator_text, ',')
            has_header = self.has_header_var.get()
            self.on_load_file(filepath, separator, has_header)
    
    def _analyze_click(self):
        """Maneja el clic en el botón de analizar"""
        if self.on_analyze_attributes:
            self.on_analyze_attributes()
    
    def _refresh_preview(self):
        """Actualiza la vista previa de datos"""
        if self.on_show_preview:
            self.on_show_preview()
    
    def _apply_column_selection(self):
        """Aplica la selección de columnas"""
        selected_indices = self.columns_listbox.curselection()
        if selected_indices and self.on_select_columns:
            self.on_select_columns(list(selected_indices))
    
    def _apply_row_selection(self, method: str):
        """Aplica la selección de filas según el método"""
        if not self.on_select_rows:
            return
        
        if method == 'indices':
            indices_str = self.indices_entry.get().strip()
            if indices_str:
                self.on_select_rows('indices', indices=indices_str)
        
        elif method == 'range':
            start = self.range_start_entry.get().strip()
            end = self.range_end_entry.get().strip()
            if start and end:
                try:
                    self.on_select_rows('range', start=int(start), end=int(end))
                except ValueError:
                    messagebox.showerror("Error", "Ingrese números válidos para el rango")
        
        elif method == 'value':
            column = self.filter_column_combo.get()
            value = self.filter_value_combo.get()
            if column and value:
                col_idx = self.filter_column_combo.current()
                self.on_select_rows('value', column_idx=col_idx, value=value)
    
    def _update_filter_values(self, event=None):
        """Actualiza los valores disponibles para filtrar"""
        # Este método será llamado desde el controlador
        pass
    
    def _export_click(self):
        """Maneja el clic en el botón de exportar"""
        if self.on_save_file:
            output_path = self.export_path_var.get()
            separator_text = self.export_separator_var.get()
            # Mapear el texto del separador al carácter real
            sep_map = {'Coma (,)': ',', 'Punto y coma (;)': ';', 'Tabulador': '\t'}
            separator = sep_map.get(separator_text, ',')
            self.on_save_file(output_path, separator)
    
    # Métodos públicos para actualizar la interfaz
    def update_status(self, message: str):
        """Actualiza la barra de estado"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_dataset_info(self, n_rows: int, n_columns: int):
        """Actualiza la información del dataset en la barra de estado"""
        self.dataset_info_label.config(text=f"📊 {n_rows} filas × {n_columns} columnas")
    
    def show_data_preview(self, data: List[List[str]]):
        """Muestra los datos en el Treeview"""
        # Limpiar árbol
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not data:
            return
        
        # Configurar columnas
        if len(data) > 0:
            self.data_tree['columns'] = [f"col{i}" for i in range(len(data[0]))]
            
            # Configurar encabezados
            for i, header in enumerate(data[0]):
                col_id = f"col{i}"
                self.data_tree.heading(col_id, text=header)
                self.data_tree.column(col_id, width=120)
            
            # Insertar datos
            for row in data[1:]:
                self.data_tree.insert('', tk.END, values=row)
    
    def show_info(self, info_dict: Dict[str, Any]):
        """Muestra información del dataset"""
        self.info_text.delete(1.0, tk.END)
        
        info_str = f"Archivo: {info_dict.get('filepath', 'N/A')}\n"
        info_str += f"Separador: '{info_dict.get('separator', ',')}'\n"
        info_str += f"Filas: {info_dict.get('n_rows', 0)}\n"
        info_str += f"Columnas: {info_dict.get('n_columns', 0)}\n"
        info_str += f"Total de elementos: {info_dict.get('total_elements', 0)}\n"
        
        self.info_text.insert(1.0, info_str)
        
        # También actualizar en la pestaña de exportación
        self.export_info_text.delete(1.0, tk.END)
        self.export_info_text.insert(1.0, info_str)
    
    def show_analysis(self, analysis_data: Dict[int, Dict[str, Any]]):
        """Muestra el análisis de atributos"""
        self.analysis_text.delete(1.0, tk.END)
        
        for col_idx, data in analysis_data.items():
            nombre = data['nombre']
            stats = data['stats']
            
            self.analysis_text.insert(tk.END, f"\n{'='*60}\n")
            self.analysis_text.insert(tk.END, f"[Columna {col_idx+1}] {nombre}\n")
            self.analysis_text.insert(tk.END, f"{'='*60}\n")
            
            if stats['tipo'] == 'cuantitativo':
                self.analysis_text.insert(tk.END, "TIPO: CUANTITATIVO\n\n")
                self.analysis_text.insert(tk.END, f"  Mínimo:              {stats['mínimo']:.4f}\n")
                self.analysis_text.insert(tk.END, f"  Máximo:              {stats['máximo']:.4f}\n")
                self.analysis_text.insert(tk.END, f"  Promedio:            {stats['promedio']:.4f}\n")
                self.analysis_text.insert(tk.END, f"  Desviación estándar: {stats['desviación_estándar']:.4f}\n")
            else:
                self.analysis_text.insert(tk.END, "TIPO: CUALITATIVO\n\n")
                self.analysis_text.insert(tk.END, f"  Categorías encontradas: {len(stats['categorías'])}\n\n")
                for cat, count in stats['cantidad_por_categoría'].items():
                    self.analysis_text.insert(tk.END, f"    • {cat}: {count} ocurrencias\n")
            
            self.analysis_text.insert(tk.END, "\n")
    
    def update_columns_listbox(self, headers: List[str]):
        """Actualiza la lista de columnas disponibles"""
        self.columns_listbox.delete(0, tk.END)
        for i, header in enumerate(headers):
            self.columns_listbox.insert(tk.END, f"[{i}] {header}")
    
    def update_filter_columns(self, headers: List[str]):
        """Actualiza el combobox de columnas para filtrar"""
        self.filter_column_combo['values'] = headers
        if headers:
            self.filter_column_combo.current(0)
    
    def update_filter_values(self, values: List[str]):
        """Actualiza los valores disponibles para filtrar"""
        self.filter_value_combo['values'] = values
        if values:
            self.filter_value_combo.current(0)
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Muestra un mensaje al usuario"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "success":
            messagebox.showinfo(title, "✓ " + message)
    
    def ask_question(self, title: str, message: str) -> bool:
        """Hace una pregunta al usuario"""
        return messagebox.askyesno(title, message)
