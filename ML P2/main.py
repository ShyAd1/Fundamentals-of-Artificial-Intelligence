"""
Sistema interactivo de clasificadores K-NN y Mínima Distancia.
Proporciona una interfaz de menú para entrenar, predecir y evaluar clasificadores.
"""

import os
import sys
from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier


class ClassifierSystem:
    """Sistema completo de clasificadores con interfaz interactiva"""
    
    def __init__(self):
        self.dataset = None
        self.knn_classifier = None
        self.md_classifier = None
        self.data_file = "data/training_data.txt"
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self, text: str):
        """Imprime un encabezado formateado"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def print_menu(self, title: str, options: dict):
        """Imprime un menú de opciones"""
        print(f"\n{title}")
        print("-" * 40)
        for key, value in options.items():
            print(f"  {key}. {value}")
        print("-" * 40)
    
    def setup_dataset(self):
        """Permite al usuario configurar el dataset"""
        self.print_header("Configuración de Dataset")
        
        try:
            input_size = int(input("Dimensión del vector de entrada: "))
            output_size = int(input("Dimensión del vector de salida: "))
            
            self.dataset = Dataset(input_size, output_size)
            print(f"\n✓ Dataset configurado: {self.dataset}")
            
        except ValueError as e:
            print(f"\n✗ Error: {e}")
    
    def add_samples_manual(self):
        """Permite agregar muestras manualmente"""
        if self.dataset is None:
            print("\n✗ Primero debe configurar un dataset")
            return
        
        self.print_header("Agregar Muestras Manualmente")
        print(f"Vector de entrada: {self.dataset.input_size} valores")
        print(f"Vector de salida: {self.dataset.output_size} valores")
        print("(Ingrese 'listo' para terminar)\n")
        
        while True:
            try:
                input_str = input("Vector de entrada (separados por coma): ").strip()
                if input_str.lower() == 'listo':
                    break
                
                output_str = input("Vector de salida (separados por coma): ").strip()
                
                input_vec = [float(x.strip()) for x in input_str.split(',')]
                output_vec = [float(x.strip()) for x in output_str.split(',')]
                
                self.dataset.add_sample(input_vec, output_vec)
                print("✓ Muestra agregada\n")
                
            except ValueError as e:
                print(f"✗ Error: {e}\n")
    
    def load_dataset_from_file(self):
        """Carga el dataset desde un archivo"""
        if self.dataset is None:
            print("\n✗ Primero debe configurar un dataset")
            return
        
        self.print_header("Cargar Dataset desde Archivo")
        
        filepath = input(f"Ruta del archivo [{self.data_file}]: ").strip()
        if not filepath:
            filepath = self.data_file
        
        try:
            self.dataset.load_from_file(filepath)
        except Exception as e:
            print(f"\n✗ Error al cargar archivo: {e}")
    
    def save_dataset_to_file(self):
        """Guarda el dataset actual en un archivo"""
        if self.dataset is None or self.dataset.get_size() == 0:
            print("\n✗ No hay dataset para guardar")
            return
        
        self.print_header("Guardar Dataset")
        
        filepath = input(f"Ruta del archivo [{self.data_file}]: ").strip()
        if not filepath:
            filepath = self.data_file
        
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            self.dataset.save_to_file(filepath)
        except Exception as e:
            print(f"\n✗ Error al guardar archivo: {e}")
    
    def train_classifiers(self):
        """Entrena ambos clasificadores"""
        if self.dataset is None or self.dataset.get_size() == 0:
            print("\n✗ No hay datos de entrenamiento")
            return
        
        self.print_header("Entrenamiento de Clasificadores")
        
        try:
            # Entrenar K-NN
            k_value = input("Valor de K para K-NN [3]: ").strip()
            k_value = int(k_value) if k_value else 3
            
            metric = self._select_distance_metric()
            
            self.knn_classifier = KNNClassifier(self.dataset, k=k_value, distance_metric=metric)
            print(f"✓ K-NN entrenado: {self.knn_classifier.get_info()}")
            
            # Entrenar Mínima Distancia
            metric = self._select_distance_metric()
            self.md_classifier = MinimumDistanceClassifier(self.dataset, distance_metric=metric)
            print(f"✓ Mínima Distancia entrenado: {self.md_classifier.get_info()}")
            print(f"  Clases detectadas: {self.md_classifier.get_prototypes_count()}")
            
        except Exception as e:
            print(f"\n✗ Error en entrenamiento: {e}")
    
    def _select_distance_metric(self) -> str:
        """Permite al usuario seleccionar una métrica de distancia"""
        print("\nMétricas de distancia disponibles:")
        print("  1. Euclidiana")
        print("  2. Manhattan")
        choice = input("Seleccione métrica [1]: ").strip()
        
        if choice == '2':
            return 'manhattan'
        return 'euclidean'
    
    def predict_single(self):
        """Realiza una predicción para un vector único"""
        if self.knn_classifier is None or self.md_classifier is None:
            print("\n✗ Los clasificadores no han sido entrenados")
            return
        
        self.print_header("Predicción Individual")
        
        try:
            print(f"Ingrese un vector de entrada con {self.dataset.input_size} valores")
            input_str = input("Vector de entrada (separados por coma): ").strip()
            input_vec = [float(x.strip()) for x in input_str.split(',')]
            
            print("\n" + "-"*40)
            
            knn_pred = self.knn_classifier.predict(input_vec)
            print(f"K-NN:              {knn_pred}")
            
            md_pred = self.md_classifier.predict(input_vec)
            print(f"Mínima Distancia:  {md_pred}")
            
            print("-"*40)
            
        except Exception as e:
            print(f"\n✗ Error en predicción: {e}")
    
    def configure_classifiers(self):
        """Permite configurar parámetros de los clasificadores"""
        if self.knn_classifier is None or self.md_classifier is None:
            print("\n✗ Los clasificadores no han sido entrenados")
            return
        
        self.print_header("Configuración de Clasificadores")
        
        options = {
            '1': 'Cambiar K en K-NN',
            '2': 'Cambiar métrica de distancia K-NN',
            '3': 'Cambiar métrica de distancia Mínima Distancia',
            '4': 'Volver'
        }
        
        while True:
            self.print_menu("Seleccione una opción", options)
            choice = input("Opción: ").strip()
            
            try:
                if choice == '1':
                    k = int(input("Nuevo valor de K: "))
                    self.knn_classifier.set_k(k)
                    print(f"✓ K-NN actualizado: {self.knn_classifier.get_info()}")
                
                elif choice == '2':
                    metric = self._select_distance_metric()
                    self.knn_classifier.set_distance_metric(metric)
                    print(f"✓ Métrica K-NN actualizada a {metric}")
                
                elif choice == '3':
                    metric = self._select_distance_metric()
                    self.md_classifier.set_distance_metric(metric)
                    print(f"✓ Métrica Mínima Distancia actualizada a {metric}")
                
                elif choice == '4':
                    break
                else:
                    print("✗ Opción no válida")
            except Exception as e:
                print(f"✗ Error: {e}")
    
    def show_statistics(self):
        """Muestra estadísticas del sistema"""
        self.print_header("Estadísticas del Sistema")
        
        if self.dataset:
            print(f"\nDataset:")
            print(f"  - Tamaño entrada: {self.dataset.input_size}")
            print(f"  - Tamaño salida: {self.dataset.output_size}")
            print(f"  - Muestras: {self.dataset.get_size()}")
        else:
            print("\nDataset: No configurado")
        
        if self.knn_classifier:
            print(f"\nK-NN:")
            print(f"  - {self.knn_classifier.get_info()}")
        else:
            print("\nK-NN: No entrenado")
        
        if self.md_classifier:
            print(f"\nMínima Distancia:")
            print(f"  - {self.md_classifier.get_info()}")
        else:
            print("\nMínima Distancia: No entrenado")
    
    def main_menu(self):
        """Menú principal del sistema"""
        while True:
            self.clear_screen()
            self.print_header("SISTEMA DE CLASIFICADORES")
            print("\n1. Configuración")
            print("2. Datos")
            print("3. Entrenamiento")
            print("4. Predicción")
            print("5. Configuración de Clasificadores")
            print("6. Estadísticas")
            print("7. Salir")
            
            choice = input("\nOpción: ").strip()
            
            if choice == '1':
                self.setup_dataset()
                input("\nPresione Enter para continuar...")
            
            elif choice == '2':
                self.data_menu()
            
            elif choice == '3':
                self.train_classifiers()
                input("\nPresione Enter para continuar...")
            
            elif choice == '4':
                self.predict_single()
                input("\nPresione Enter para continuar...")
            
            elif choice == '5':
                self.configure_classifiers()
            
            elif choice == '6':
                self.show_statistics()
                input("\nPresione Enter para continuar...")
            
            elif choice == '7':
                print("\n¡Hasta luego!")
                break
            
            else:
                print("✗ Opción no válida")
                input("\nPresione Enter para continuar...")
    
    def data_menu(self):
        """Menú de gestión de datos"""
        while True:
            self.clear_screen()
            self.print_header("GESTIÓN DE DATOS")
            
            options = {
                '1': 'Agregar muestras manualmente',
                '2': 'Cargar dataset desde archivo',
                '3': 'Guardar dataset a archivo',
                '4': 'Ver información del dataset',
                '5': 'Limpiar dataset',
                '6': 'Volver'
            }
            
            self.print_menu("Seleccione una opción", options)
            choice = input("Opción: ").strip()
            
            if choice == '1':
                self.add_samples_manual()
                input("\nPresione Enter para continuar...")
            
            elif choice == '2':
                self.load_dataset_from_file()
                input("\nPresione Enter para continuar...")
            
            elif choice == '3':
                self.save_dataset_to_file()
                input("\nPresione Enter para continuar...")
            
            elif choice == '4':
                if self.dataset:
                    print(f"\n{self.dataset}")
                else:
                    print("\n✗ No hay dataset configurado")
                input("\nPresione Enter para continuar...")
            
            elif choice == '5':
                if self.dataset:
                    confirm = input("\n¿Está seguro? (s/n): ").lower()
                    if confirm == 's':
                        self.dataset.clear()
                        print("✓ Dataset limpiado")
                else:
                    print("\n✗ No hay dataset para limpiar")
                input("\nPresione Enter para continuar...")
            
            elif choice == '6':
                break
            
            else:
                print("✗ Opción no válida")
                input("\nPresione Enter para continuar...")


def main():
    """Función principal"""
    system = ClassifierSystem()
    system.main_menu()


if __name__ == "__main__":
    main()
