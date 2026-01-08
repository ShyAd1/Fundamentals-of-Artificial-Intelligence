"""
Sistema de Validación de Modelos de Machine Learning
Implementa Train/Test, K-Fold Cross Validation y Bootstrap
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
import warnings
warnings.filterwarnings('ignore')


class ValidationSystem:
    """Clase principal que implementa los métodos de validación"""
    
    def __init__(self):
        self.data = None
        self.X = None
        self.y = None
        self.model = None
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Cargar base de datos desde archivo CSV o Excel"""
        try:
            if filepath.endswith('.csv'):
                self.data = pd.read_csv(filepath)
            elif filepath.endswith(('.xls', '.xlsx')):
                self.data = pd.read_excel(filepath)
            else:
                raise ValueError("Formato no soportado. Use CSV o Excel")
            return self.data
        except Exception as e:
            raise Exception(f"Error al cargar datos: {str(e)}")
    
    def set_features(self, input_features: List[str], output_feature: str):
        """Especificar atributos de entrada y salida"""
        if self.data is None:
            raise ValueError("Primero debe cargar los datos")
        
        self.X = np.array(self.data[input_features].values)
        self.y = np.array(self.data[output_feature].values)
        
    def train_and_test(self, test_size: float = 0.3, model=None) -> Dict:
        """
        Implementa validación Train and Test
        
        Args:
            test_size: Porcentaje de muestras para prueba (0-1)
            model: Modelo de clasificación a utilizar
            
        Returns:
            Dict con accuracy, error, y matrices de confusión
        """
        if self.X is None or self.y is None:
            raise ValueError("Debe especificar features primero")
        
        if model is None:
            model = DecisionTreeClassifier(random_state=42)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=42
        )
        
        # Entrenar modelo
        model.fit(X_train, y_train)
        
        # Predecir
        y_pred = model.predict(X_test)
        
        # Calcular métricas
        accuracy = accuracy_score(y_test, y_pred)
        error = 1 - accuracy
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'accuracy': accuracy * 100,
            'error': error * 100,
            'confusion_matrix': cm,
            'y_test': y_test,
            'y_pred': y_pred,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def k_fold_cross_validation(self, k: int = 5, model=None) -> Dict:
        """
        Implementa K-Fold Cross Validation
        
        Args:
            k: Número de grupos (folds)
            model: Modelo de clasificación a utilizar
            
        Returns:
            Dict con accuracy por fold, promedio y desviación estándar
        """
        if self.X is None or self.y is None:
            raise ValueError("Debe especificar features primero")
        
        if model is None:
            model = DecisionTreeClassifier(random_state=42)
        
        kfold = KFold(n_splits=k, shuffle=True, random_state=42)
        
        accuracies = []
        errors = []
        fold_results = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(kfold.split(self.X)):
            X_train, X_test = self.X[train_idx], self.X[test_idx]
            y_train, y_test = self.y[train_idx], self.y[test_idx]
            
            # Clonar modelo para cada fold
            from sklearn.base import clone
            fold_model = clone(model)
            
            # Entrenar
            fold_model.fit(X_train, y_train)
            
            # Predecir
            y_pred = fold_model.predict(X_test)
            
            # Métricas
            acc = accuracy_score(y_test, y_pred)
            err = 1 - acc
            
            accuracies.append(acc * 100)
            errors.append(err * 100)
            
            fold_results.append({
                'fold': fold_idx + 1,
                'accuracy': acc * 100,
                'error': err * 100,
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            })
        
        return {
            'fold_results': fold_results,
            'accuracies': accuracies,
            'errors': errors,
            'mean_accuracy': np.mean(accuracies),
            'std_accuracy': np.std(accuracies),
            'mean_error': np.mean(errors),
            'std_error': np.std(errors)
        }
    
    def bootstrap(self, n_experiments: int = 10, train_size: int | None = None, 
                  test_size: int | None = None, model=None) -> Dict:
        """
        Implementa Bootstrap
        
        Args:
            n_experiments: Número de experimentos (K)
            train_size: Tamaño del conjunto de entrenamiento
            test_size: Tamaño del conjunto de prueba
            model: Modelo de clasificación a utilizar
            
        Returns:
            Dict con resultados por experimento y estadísticas generales
        """
        if self.X is None or self.y is None:
            raise ValueError("Debe especificar features primero")
        
        if model is None:
            model = DecisionTreeClassifier(random_state=42)
        
        n_samples = len(self.X)
        
        # Tamaños por defecto
        if train_size is None:
            train_size = int(n_samples * 0.7)
        if test_size is None:
            test_size = n_samples - train_size
            
        accuracies = []
        errors = []
        experiment_results = []
        
        # Obtener clases únicas
        unique_classes = np.unique(np.array(self.y))
        class_accuracies = {cls: [] for cls in unique_classes}
        
        for exp in range(n_experiments):
            # Bootstrap sampling con reemplazo
            train_indices = np.random.choice(n_samples, size=train_size, replace=True)
            
            # Test samples (las que no están en train o un nuevo muestreo)
            remaining_indices = list(set(range(n_samples)) - set(train_indices))
            if len(remaining_indices) < test_size:
                # Si no hay suficientes muestras diferentes, hacer sampling con reemplazo
                test_indices = np.random.choice(n_samples, size=test_size, replace=True)
            else:
                test_indices = np.random.choice(remaining_indices, size=test_size, replace=False)
            
            X_train = self.X[train_indices]
            y_train = self.y[train_indices]
            X_test = self.X[test_indices]
            y_test = self.y[test_indices]
            
            # Clonar modelo
            from sklearn.base import clone
            exp_model = clone(model)
            
            # Entrenar
            exp_model.fit(X_train, y_train)
            
            # Predecir
            y_pred = exp_model.predict(X_test)
            
            # Métricas generales
            acc = accuracy_score(y_test, y_pred)
            err = 1 - acc
            
            accuracies.append(acc * 100)
            errors.append(err * 100)
            
            # Métricas por clase
            cm = confusion_matrix(y_test, y_pred, labels=unique_classes)
            class_acc = {}
            
            for idx, cls in enumerate(unique_classes):
                if cm[idx].sum() > 0:
                    class_accuracy = cm[idx, idx] / cm[idx].sum() * 100
                else:
                    class_accuracy = 0.0
                class_acc[cls] = class_accuracy
                class_accuracies[cls].append(class_accuracy)
            
            experiment_results.append({
                'experiment': exp + 1,
                'accuracy': acc * 100,
                'error': err * 100,
                'class_accuracies': class_acc,
                'confusion_matrix': cm
            })
        
        # Estadísticas por clase
        class_stats = {}
        for cls in unique_classes:
            class_stats[cls] = {
                'mean_accuracy': np.mean(class_accuracies[cls]),
                'std_accuracy': np.std(class_accuracies[cls])
            }
        
        return {
            'experiment_results': experiment_results,
            'accuracies': accuracies,
            'errors': errors,
            'mean_accuracy': np.mean(accuracies),
            'std_accuracy': np.std(accuracies),
            'mean_error': np.mean(errors),
            'std_error': np.std(errors),
            'class_stats': class_stats,
            'n_experiments': n_experiments,
            'train_size': train_size,
            'test_size': test_size
        }


class MLValidationGUI:
    """Interfaz gráfica para el sistema de validación"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Validación de Modelos ML")
        self.root.geometry("1200x800")
        
        self.system = ValidationSystem()
        self.data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Carga de Datos
        self.tab_data = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text="📁 Cargar Datos")
        self.setup_data_tab()
        
        # Pestaña 2: Train and Test
        self.tab_traintest = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_traintest, text="🔀 Train & Test")
        self.setup_traintest_tab()
        
        # Pestaña 3: K-Fold Cross Validation
        self.tab_kfold = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_kfold, text="🔄 K-Fold CV")
        self.setup_kfold_tab()
        
        # Pestaña 4: Bootstrap
        self.tab_bootstrap = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bootstrap, text="🎲 Bootstrap")
        self.setup_bootstrap_tab()
        
    def setup_data_tab(self):
        """Configurar pestaña de carga de datos"""
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_data, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Cargar y Configurar Base de Datos", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Botón cargar archivo
        btn_load = ttk.Button(main_frame, text="📂 Cargar Archivo CSV/Excel", 
                             command=self.load_file, width=30)
        btn_load.pack(pady=10)
        
        # Label archivo cargado
        self.lbl_file = ttk.Label(main_frame, text="No se ha cargado ningún archivo", 
                                 foreground="gray")
        self.lbl_file.pack(pady=5)
        
        # Frame para selección de features
        feature_frame = ttk.LabelFrame(main_frame, text="Selección de Atributos", 
                                      padding="10")
        feature_frame.pack(fill='both', expand=True, pady=20)
        
        # Input features
        ttk.Label(feature_frame, text="Atributos de Entrada (X):").pack(anchor='w', pady=5)
        
        self.input_frame = ttk.Frame(feature_frame)
        self.input_frame.pack(fill='both', expand=True, pady=5)
        
        self.input_listbox = tk.Listbox(self.input_frame, selectmode='multiple', 
                                        height=8, exportselection=False)
        self.input_listbox.pack(side='left', fill='both', expand=True)
        
        input_scroll = ttk.Scrollbar(self.input_frame, command=self.input_listbox.yview)
        input_scroll.pack(side='right', fill='y')
        self.input_listbox.config(yscrollcommand=input_scroll.set)
        
        # Output feature
        ttk.Label(feature_frame, text="Atributo de Salida (Y):").pack(anchor='w', pady=(15, 5))
        
        self.output_var = tk.StringVar()
        self.output_combo = ttk.Combobox(feature_frame, textvariable=self.output_var, 
                                        state='readonly', width=40)
        self.output_combo.pack(anchor='w', pady=5)
        
        # Modelo de clasificación
        ttk.Label(feature_frame, text="Modelo de Clasificación:").pack(anchor='w', pady=(15, 5))
        
        self.model_var = tk.StringVar(value="Decision Tree")
        models = ["Decision Tree", "Random Forest", "K-Nearest Neighbors", "Naive Bayes"]
        self.model_combo = ttk.Combobox(feature_frame, textvariable=self.model_var, 
                                       values=models, state='readonly', width=40)
        self.model_combo.pack(anchor='w', pady=5)
        
        # Botón confirmar
        btn_confirm = ttk.Button(feature_frame, text="✓ Confirmar Configuración", 
                                command=self.confirm_features, width=30)
        btn_confirm.pack(pady=20)
        
        # Vista previa de datos
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding="10")
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=10, wrap='none')
        self.preview_text.pack(fill='both', expand=True)
        
        preview_scroll_y = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        preview_scroll_y.pack(side='right', fill='y')
        self.preview_text.config(yscrollcommand=preview_scroll_y.set)
        
    def setup_traintest_tab(self):
        """Configurar pestaña Train and Test"""
        
        main_frame = ttk.Frame(self.tab_traintest, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Validación Train and Test", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill='x', pady=10)
        
        ttk.Label(config_frame, text="Porcentaje para Prueba (%):").grid(row=0, column=0, 
                                                                          sticky='w', pady=5)
        self.tt_test_size = ttk.Scale(config_frame, from_=10, to=50, orient='horizontal', 
                                     length=300)
        self.tt_test_size.set(30)
        self.tt_test_size.grid(row=0, column=1, padx=10)
        
        self.tt_test_label = ttk.Label(config_frame, text="30%")
        self.tt_test_label.grid(row=0, column=2)
        
        self.tt_test_size.config(command=lambda v: self.tt_test_label.config(
            text=f"{int(float(v))}%"))
        
        # Botón ejecutar
        btn_execute = ttk.Button(config_frame, text="▶ Ejecutar Train & Test", 
                                command=self.run_traintest, width=30)
        btn_execute.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.tt_results_text = tk.Text(results_frame, height=15, font=('Courier', 10))
        self.tt_results_text.pack(fill='both', expand=True)
        
    def setup_kfold_tab(self):
        """Configurar pestaña K-Fold Cross Validation"""
        
        main_frame = ttk.Frame(self.tab_kfold, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="K-Fold Cross Validation", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill='x', pady=10)
        
        ttk.Label(config_frame, text="Número de Folds (K):").grid(row=0, column=0, 
                                                                   sticky='w', pady=5)
        self.kfold_k = ttk.Spinbox(config_frame, from_=2, to=20, width=10)
        self.kfold_k.set(5)
        self.kfold_k.grid(row=0, column=1, padx=10, sticky='w')
        
        # Botón ejecutar
        btn_execute = ttk.Button(config_frame, text="▶ Ejecutar K-Fold CV", 
                                command=self.run_kfold, width=30)
        btn_execute.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.kfold_results_text = tk.Text(results_frame, height=20, font=('Courier', 10))
        self.kfold_results_text.pack(fill='both', expand=True)
        
    def setup_bootstrap_tab(self):
        """Configurar pestaña Bootstrap"""
        
        main_frame = ttk.Frame(self.tab_bootstrap, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Validación Bootstrap", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill='x', pady=10)
        
        ttk.Label(config_frame, text="Número de Experimentos (K):").grid(row=0, column=0, 
                                                                          sticky='w', pady=5)
        self.bs_k = ttk.Spinbox(config_frame, from_=2, to=100, width=10)
        self.bs_k.set(10)
        self.bs_k.grid(row=0, column=1, padx=10, sticky='w')
        
        ttk.Label(config_frame, text="Tamaño Conjunto Entrenamiento:").grid(row=1, column=0, 
                                                                             sticky='w', pady=5)
        self.bs_train_size = ttk.Entry(config_frame, width=10)
        self.bs_train_size.grid(row=1, column=1, padx=10, sticky='w')
        
        ttk.Label(config_frame, text="Tamaño Conjunto Prueba:").grid(row=2, column=0, 
                                                                      sticky='w', pady=5)
        self.bs_test_size = ttk.Entry(config_frame, width=10)
        self.bs_test_size.grid(row=2, column=1, padx=10, sticky='w')
        
        ttk.Label(config_frame, text="(Dejar vacío para automático)", 
                 foreground="gray").grid(row=3, column=0, columnspan=2, pady=5)
        
        # Botón ejecutar
        btn_execute = ttk.Button(config_frame, text="▶ Ejecutar Bootstrap", 
                                command=self.run_bootstrap, width=30)
        btn_execute.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.bs_results_text = tk.Text(results_frame, height=20, font=('Courier', 10))
        self.bs_results_text.pack(fill='both', expand=True)
        
    def load_file(self):
        """Cargar archivo de datos"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), 
                      ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            self.data = self.system.load_data(filepath)
            self.lbl_file.config(text=f"✓ Archivo cargado: {filepath.split('/')[-1]}", 
                               foreground="green")
            
            # Actualizar listbox y combobox
            columns = self.data.columns.tolist()
            
            self.input_listbox.delete(0, tk.END)
            for col in columns:
                self.input_listbox.insert(tk.END, col)
            
            self.output_combo['values'] = columns
            if len(columns) > 0:
                self.output_combo.current(len(columns) - 1)
            
            # Mostrar vista previa
            self.preview_text.delete(1.0, tk.END)
            preview = f"Dimensiones: {self.data.shape[0]} filas x {self.data.shape[1]} columnas\n\n"
            preview += self.data.head(10).to_string()
            self.preview_text.insert(1.0, preview)
            
            messagebox.showinfo("Éxito", "Datos cargados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
            
    def confirm_features(self):
        """Confirmar selección de features"""
        try:
            # Obtener features seleccionados
            selected_indices = self.input_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Advertencia", 
                                     "Debe seleccionar al menos un atributo de entrada")
                return
            
            input_features = [self.input_listbox.get(i) for i in selected_indices]
            output_feature = self.output_var.get()
            
            if not output_feature:
                messagebox.showwarning("Advertencia", 
                                     "Debe seleccionar un atributo de salida")
                return
            
            # Configurar features en el sistema
            self.system.set_features(input_features, output_feature)
            
            messagebox.showinfo("Éxito", 
                              f"Configuración confirmada:\n"
                              f"Entrada: {', '.join(input_features)}\n"
                              f"Salida: {output_feature}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar features:\n{str(e)}")
    
    def get_model(self):
        """Obtener modelo seleccionado"""
        model_name = self.model_var.get()
        
        if model_name == "Decision Tree":
            return DecisionTreeClassifier(random_state=42)
        elif model_name == "Random Forest":
            return RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_name == "K-Nearest Neighbors":
            return KNeighborsClassifier(n_neighbors=5)
        elif model_name == "Naive Bayes":
            return GaussianNB()
        else:
            return DecisionTreeClassifier(random_state=42)
    
    def run_traintest(self):
        """Ejecutar Train and Test"""
        try:
            if self.system.X is None:
                messagebox.showwarning("Advertencia", 
                                     "Primero debe cargar datos y configurar features")
                return
            
            test_size = int(self.tt_test_size.get()) / 100
            model = self.get_model()
            
            results = self.system.train_and_test(test_size=test_size, model=model)
            
            # Mostrar resultados
            output = "="*60 + "\n"
            output += "RESULTADOS TRAIN AND TEST\n"
            output += "="*60 + "\n\n"
            output += f"Modelo: {self.model_var.get()}\n"
            output += f"Tamaño Train: {results['train_size']} muestras ({100-test_size*100:.0f}%)\n"
            output += f"Tamaño Test: {results['test_size']} muestras ({test_size*100:.0f}%)\n\n"
            output += f"ACCURACY: {results['accuracy']:.2f}%\n"
            output += f"ERROR: {results['error']:.2f}%\n\n"
            output += "Matriz de Confusión:\n"
            output += str(results['confusion_matrix']) + "\n"
            
            self.tt_results_text.delete(1.0, tk.END)
            self.tt_results_text.insert(1.0, output)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar Train & Test:\n{str(e)}")
    
    def run_kfold(self):
        """Ejecutar K-Fold Cross Validation"""
        try:
            if self.system.X is None:
                messagebox.showwarning("Advertencia", 
                                     "Primero debe cargar datos y configurar features")
                return
            
            k = int(self.kfold_k.get())
            model = self.get_model()
            
            results = self.system.k_fold_cross_validation(k=k, model=model)
            
            # Mostrar resultados
            output = "="*60 + "\n"
            output += "RESULTADOS K-FOLD CROSS VALIDATION\n"
            output += "="*60 + "\n\n"
            output += f"Modelo: {self.model_var.get()}\n"
            output += f"Número de Folds: {k}\n\n"
            
            output += "Resultados por Fold:\n"
            output += "-"*60 + "\n"
            for fold in results['fold_results']:
                output += f"Fold {fold['fold']}: "
                output += f"Accuracy = {fold['accuracy']:.2f}%, "
                output += f"Error = {fold['error']:.2f}%\n"
            
            output += "\n" + "="*60 + "\n"
            output += "ESTADÍSTICAS GENERALES\n"
            output += "="*60 + "\n"
            output += f"Accuracy Promedio: {results['mean_accuracy']:.2f}%\n"
            output += f"Desviación Estándar Accuracy: {results['std_accuracy']:.2f}%\n"
            output += f"Error Promedio: {results['mean_error']:.2f}%\n"
            output += f"Desviación Estándar Error: {results['std_error']:.2f}%\n"
            
            self.kfold_results_text.delete(1.0, tk.END)
            self.kfold_results_text.insert(1.0, output)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar K-Fold CV:\n{str(e)}")
    
    def run_bootstrap(self):
        """Ejecutar Bootstrap"""
        try:
            if self.system.X is None:
                messagebox.showwarning("Advertencia", 
                                     "Primero debe cargar datos y configurar features")
                return
            
            n_exp = int(self.bs_k.get())
            
            train_size = self.bs_train_size.get()
            train_size = int(train_size) if train_size else None
            
            test_size = self.bs_test_size.get()
            test_size = int(test_size) if test_size else None
            
            model = self.get_model()
            
            results = self.system.bootstrap(n_experiments=n_exp, train_size=train_size,
                                           test_size=test_size, model=model)
            
            # Mostrar resultados
            output = "="*60 + "\n"
            output += "RESULTADOS BOOTSTRAP\n"
            output += "="*60 + "\n\n"
            output += f"Modelo: {self.model_var.get()}\n"
            output += f"Número de Experimentos: {results['n_experiments']}\n"
            output += f"Tamaño Train: {results['train_size']}\n"
            output += f"Tamaño Test: {results['test_size']}\n\n"
            
            output += "Resultados por Experimento:\n"
            output += "-"*60 + "\n"
            for exp in results['experiment_results'][:10]:  # Mostrar primeros 10
                output += f"Experimento {exp['experiment']}: "
                output += f"Accuracy = {exp['accuracy']:.2f}%\n"
                output += f"  Por clase: {exp['class_accuracies']}\n"
            
            if len(results['experiment_results']) > 10:
                output += f"... ({len(results['experiment_results']) - 10} experimentos más)\n"
            
            output += "\n" + "="*60 + "\n"
            output += "ESTADÍSTICAS GENERALES\n"
            output += "="*60 + "\n"
            output += f"Accuracy Promedio: {results['mean_accuracy']:.2f}%\n"
            output += f"Desviación Estándar Accuracy: {results['std_accuracy']:.2f}%\n"
            output += f"Error Promedio: {results['mean_error']:.2f}%\n"
            output += f"Desviación Estándar Error: {results['std_error']:.2f}%\n\n"
            
            output += "Estadísticas por Clase:\n"
            output += "-"*60 + "\n"
            for cls, stats in results['class_stats'].items():
                output += f"Clase {cls}:\n"
                output += f"  Accuracy Promedio: {stats['mean_accuracy']:.2f}%\n"
                output += f"  Desviación Estándar: {stats['std_accuracy']:.2f}%\n"
            
            self.bs_results_text.delete(1.0, tk.END)
            self.bs_results_text.insert(1.0, output)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar Bootstrap:\n{str(e)}")


def main():
    root = tk.Tk()
    app = MLValidationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
