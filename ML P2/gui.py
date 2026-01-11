#!/usr/bin/env python3
"""
GUI para el sistema de clasificadores K-NN y Mínima Distancia.
Permite definir dimensiones, cargar datos, entrenar y predecir sin usar la consola.
Uso: python3 gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier


class ClassifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clasificadores K-NN y Mínima Distancia")
        self.root.geometry("880x620")
        self.dataset = None
        self.knn = None
        self.md = None

        self._build_ui()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Label(self.root, text="Sistema de Clasificadores", font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, pady=10)

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        frame_setup = ttk.Frame(notebook)
        frame_data = ttk.Frame(notebook)
        frame_train = ttk.Frame(notebook)
        frame_predict = ttk.Frame(notebook)

        notebook.add(frame_setup, text="Configuración")
        notebook.add(frame_data, text="Datos")
        notebook.add(frame_train, text="Entrenamiento")
        notebook.add(frame_predict, text="Predicción")

        self._setup_tab(frame_setup)
        self._data_tab(frame_data)
        self._train_tab(frame_train)
        self._predict_tab(frame_predict)

        self.log = tk.Text(self.root, height=10, state="disabled", bg="#0e1116", fg="#d7d7d7")
        self.log.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.root.rowconfigure(2, weight=1)

    def _setup_tab(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Dimensión entrada:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ttk.Label(frame, text="Dimensión salida:").grid(row=1, column=0, sticky="w", pady=5, padx=5)

        self.entry_input_size = ttk.Entry(frame)
        self.entry_output_size = ttk.Entry(frame)
        self.entry_input_size.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.entry_output_size.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(frame, text="Crear dataset", command=self._create_dataset).grid(row=2, column=0, columnspan=2, pady=10)
        self.lbl_dataset_info = ttk.Label(frame, text="Dataset no configurado")
        self.lbl_dataset_info.grid(row=3, column=0, columnspan=2, sticky="w", pady=5, padx=5)

    def _data_tab(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Cargar desde archivo (.txt)").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ttk.Button(frame, text="Seleccionar archivo", command=self._load_file).grid(row=0, column=1, sticky="w", pady=5, padx=5)

        ttk.Separator(frame, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(frame, text="Agregar muestra manual").grid(row=2, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        ttk.Label(frame, text="Entrada (valores separados por coma)").grid(row=3, column=0, sticky="w", padx=5)
        ttk.Label(frame, text="Salida (valores separados por coma)").grid(row=4, column=0, sticky="w", padx=5)

        self.entry_manual_input = ttk.Entry(frame)
        self.entry_manual_output = ttk.Entry(frame)
        self.entry_manual_input.grid(row=3, column=1, sticky="ew", pady=3, padx=5)
        self.entry_manual_output.grid(row=4, column=1, sticky="ew", pady=3, padx=5)

        ttk.Button(frame, text="Agregar muestra", command=self._add_manual_sample).grid(row=5, column=0, columnspan=2, pady=10)

    def _train_tab(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Métrica de distancia:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.combo_metric = ttk.Combobox(frame, values=["euclidean", "manhattan"], state="readonly")
        self.combo_metric.current(0)
        self.combo_metric.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(frame, text="Valor de K (solo K-NN):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_k = ttk.Entry(frame)
        self.entry_k.insert(0, "3")
        self.entry_k.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(frame, text="Entrenar clasificadores", command=self._train_classifiers).grid(row=2, column=0, columnspan=2, pady=10)
        self.lbl_train_info = ttk.Label(frame, text="Clasificadores no entrenados")
        self.lbl_train_info.grid(row=3, column=0, columnspan=2, sticky="w", pady=5, padx=5)

    def _predict_tab(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Vector de entrada (separado por comas)").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entry_predict = ttk.Entry(frame)
        self.entry_predict.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        ttk.Button(frame, text="Predecir", command=self._predict).grid(row=1, column=0, columnspan=2, pady=10)

        self.lbl_pred_knn = ttk.Label(frame, text="K-NN: —")
        self.lbl_pred_md = ttk.Label(frame, text="Mínima Distancia: —")
        self.lbl_pred_knn.grid(row=2, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        self.lbl_pred_md.grid(row=3, column=0, columnspan=2, sticky="w", pady=5, padx=5)

    def _create_dataset(self):
        try:
            input_size = int(self.entry_input_size.get())
            output_size = int(self.entry_output_size.get())
            if input_size <= 0 or output_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Dimensiones inválidas. Usa enteros positivos.")
            return

        self.dataset = Dataset(input_size, output_size)
        self.knn = None
        self.md = None
        self.lbl_dataset_info.config(text=f"Dataset(entrada={input_size}, salida={output_size}, muestras=0)")
        self.lbl_train_info.config(text="Clasificadores no entrenados")
        self._log(f"Dataset creado con entrada={input_size}, salida={output_size}")

    def _load_file(self):
        if self.dataset is None:
            messagebox.showwarning("Atención", "Primero crea un dataset (dimensiones).")
            return
        filepath = filedialog.askopenfilename(title="Selecciona archivo de datos", filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not filepath:
            return
        try:
            self.dataset.clear()
            self.dataset.load_from_file(filepath)
            self.lbl_dataset_info.config(text=str(self.dataset))
            self._log(f"Archivo cargado: {filepath}. Muestras: {self.dataset.get_size()}")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def _add_manual_sample(self):
        if self.dataset is None:
            messagebox.showwarning("Atención", "Primero crea un dataset (dimensiones).")
            return
        try:
            inp = [float(x.strip()) for x in self.entry_manual_input.get().split(',') if x.strip()]
            out = [float(x.strip()) for x in self.entry_manual_output.get().split(',') if x.strip()]
            self.dataset.add_sample(inp, out)
            self.lbl_dataset_info.config(text=str(self.dataset))
            self._log(f"Muestra agregada. Total: {self.dataset.get_size()}")
            self.entry_manual_input.delete(0, tk.END)
            self.entry_manual_output.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _train_classifiers(self):
        if self.dataset is None or self.dataset.get_size() == 0:
            messagebox.showwarning("Atención", "Carga o agrega datos antes de entrenar.")
            return
        try:
            k_val = int(self.entry_k.get()) if self.entry_k.get().strip() else 3
            metric = self.combo_metric.get() or "euclidean"
            self.knn = KNNClassifier(self.dataset, k=k_val, distance_metric=metric)
            self.md = MinimumDistanceClassifier(self.dataset, distance_metric=metric)
            self.lbl_train_info.config(text=f"Entrenados | KNN k={self.knn.k}, métrica={metric} | Clases MD={self.md.get_prototypes_count()}")
            self._log(f"KNN y Mínima Distancia entrenados con métrica={metric}, k={k_val}")
        except Exception as e:
            messagebox.showerror("Error en entrenamiento", str(e))

    def _predict(self):
        if self.dataset is None or self.knn is None or self.md is None:
            messagebox.showwarning("Atención", "Primero entrena los clasificadores.")
            return
        try:
            inp = [float(x.strip()) for x in self.entry_predict.get().split(',') if x.strip()]
            pred_knn = self.knn.predict(inp)
            pred_md = self.md.predict(inp)
            self.lbl_pred_knn.config(text=f"K-NN: {pred_knn}")
            self.lbl_pred_md.config(text=f"Mínima Distancia: {pred_md}")
            self._log(f"Predicción para {inp} -> KNN {pred_knn} | MD {pred_md}")
        except Exception as e:
            messagebox.showerror("Error en predicción", str(e))

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")


def main():
    root = tk.Tk()
    ClassifierGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
