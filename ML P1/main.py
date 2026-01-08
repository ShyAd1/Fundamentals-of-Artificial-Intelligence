"""
Sistema de Carga y Manipulación de Datos - Arquitectura MVC
para Problemas de Inteligencia Artificial

Aplicación con Interfaz Gráfica (GUI) usando Tkinter

Autor: Sistema de IA
Fecha: Diciembre 2025
"""

import tkinter as tk
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Model.DataModel import DataModel
from View.DataView import DataView
from Controller.DataController import DataController


def main():
    """Función principal - Inicia la aplicación MVC con GUI"""
    # Crear ventana principal
    root = tk.Tk()
    
    # Configurar icono (opcional)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Crear componentes MVC
    model = DataModel()
    view = DataView(root)
    controller = DataController(model, view)
    
    # Iniciar el loop de la aplicación
    root.mainloop()


if __name__ == "__main__":
    main()
            else:
                print("\n❌ Opción inválida. Intente de nuevo.")
            
            input("\nPresione Enter para continuar...")
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*70)
        print("MENÚ PRINCIPAL")
        print("="*70)
        
        if self.current_loader and self.current_loader.data_matrix is not None:
            print(f"📊 Dataset actual: {self.current_loader.n_rows} filas × {self.current_loader.n_columns} columnas")
        else:
            print("⚠️  No hay dataset cargado actualmente")
        
        print("\n1. 📁 Cargar archivo de datos")
        print("2. 🔍 Analizar atributos")
        print("3. 📊 Seleccionar subconjunto de atributos (columnas)")
        print("4. 📋 Seleccionar subconjunto de filas")
        print("5. 👁️  Visualizar datos")
        print("6. 💾 Guardar dataset actual en memoria")
        print("7. 📤 Exportar datos a archivo")
        print("8. 📚 Gestionar datasets guardados")
        print("9. 🚪 Salir")
    
    def load_file_menu(self):
        """Menú para cargar archivos"""
        print("\n" + "="*70)
        print("CARGAR ARCHIVO DE DATOS")
        print("="*70)
        
        # Solicitar ruta del archivo
        filepath = input("Ingrese la ruta del archivo (o 'cancelar' para volver): ").strip()
        
        if filepath.lower() == 'cancelar':
            return
        
        # Remover comillas si las hay
        filepath = filepath.strip('"').strip("'")
        
        if not os.path.exists(filepath):
            print(f"\n❌ Error: El archivo '{filepath}' no existe")
            return
        
        # Solicitar separador
        print("\nSeparadores comunes:")
        print("  1. Coma (,)")
        print("  2. Punto y coma (;)")
        print("  3. Tabulador (\\t)")
        print("  4. Espacio ( )")
        print("  5. Otro (especificar)")
        
        sep_choice = input("\nSeleccione el separador: ").strip()
        
        separator_map = {
            '1': ',',
            '2': ';',
            '3': '\t',
            '4': ' '
        }
        
        if sep_choice in separator_map:
            separator = separator_map[sep_choice]
        elif sep_choice == '5':
            separator = input("Ingrese el carácter separador: ").strip()
            if not separator:
                separator = ','
        else:
            print("Opción inválida, usando coma como separador por defecto")
            separator = ','
        
        # Preguntar si tiene encabezados
        has_header_input = input("\n¿El archivo tiene encabezados? (s/n, default=s): ").strip().lower()
        has_header = has_header_input != 'n'
        
        # Cargar archivo
        loader = DataLoader()
        if loader.load_file(filepath, separator, has_header):
            self.current_loader = loader
            print("\n✅ Archivo cargado exitosamente en el dataset actual")
        else:
            print("\n❌ Error al cargar el archivo")
    
    def analyze_attributes_menu(self):
        """Menú para analizar atributos"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("ANALIZANDO ATRIBUTOS...")
        print("="*70)
        
        self.current_loader.analyze_attributes()
    
    def select_attributes_menu(self):
        """Menú para seleccionar atributos"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("SELECCIÓN DE ATRIBUTOS (COLUMNAS)")
        print("="*70)
        
        # Mostrar atributos disponibles
        print("\nAtributos disponibles:")
        for i, header in enumerate(self.current_loader.headers):
            print(f"  [{i}] {header}")
        
        print("\nIngrese los índices de las columnas a conservar")
        print("Formatos aceptados:")
        print("  - Lista: 0,2,4")
        print("  - Rango: 0-3")
        print("  - Combinado: 0,2-4,6")
        
        indices_input = input("\nÍndices: ").strip()
        
        if not indices_input:
            print("❌ No se ingresaron índices")
            return
        
        # Parsear índices
        try:
            indices = self._parse_indices(indices_input, self.current_loader.n_columns)
            
            if not indices:
                print("❌ No se proporcionaron índices válidos")
                return
            
            # Crear subconjunto
            new_loader = self.current_loader.select_attributes(indices)
            
            # Preguntar si reemplazar o guardar
            action = input("\n¿Desea reemplazar el dataset actual? (s/n): ").strip().lower()
            if action == 's':
                self.current_loader = new_loader
                print("✅ Dataset actual actualizado")
            else:
                print("ℹ️  El subconjunto se creó pero no se guardó. Use la opción 6 para guardarlo.")
                self.current_loader = new_loader
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        """Menú para seleccionar filas"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("SELECCIÓN DE FILAS")
        print("="*70)
        print(f"Total de filas disponibles: {self.current_loader.n_rows}")
        
        print("\nMétodos de selección:")
        print("  1. Enumerar filas específicas")
        print("  2. Especificar un rango")
        print("  3. Filtrar por valor de atributo")
        
        method = input("\nSeleccione el método: ").strip()
        
        new_loader = None
        
        if method == '1':
            indices_input = input("\nIngrese los índices de las filas (ej: 0,5,10-15): ").strip()
            try:
                indices = self._parse_indices(indices_input, self.current_loader.n_rows)
                new_loader = self.current_loader.select_rows_by_list(indices)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                return
        
        elif method == '2':
            try:
                start = int(input("Índice inicial (0-indexed): ").strip())
                end = int(input("Índice final (0-indexed, inclusivo): ").strip())
                new_loader = self.current_loader.select_rows_by_range(start, end)
            except ValueError:
                print("❌ Error: Ingrese números válidos")
                return
        
        elif method == '3':
            print("\nAtributos disponibles:")
            for i, header in enumerate(self.current_loader.headers):
                print(f"  [{i}] {header}")
            
            try:
                col_idx = int(input("\nÍndice de la columna a filtrar: ").strip())
                value = input("Valor a buscar: ").strip()
                new_loader = self.current_loader.select_rows_by_value(col_idx, value)
            except ValueError:
                print("❌ Error: Índice de columna inválido")
                return
        else:
            print("❌ Método inválido")
            return
        
        if new_loader and new_loader.data_matrix is not None:
            action = input("\n¿Desea reemplazar el dataset actual? (s/n): ").strip().lower()
            if action == 's':
                self.current_loader = new_loader
                print("✅ Dataset actual actualizado")
            else:
                self.current_loader = new_loader
                print("ℹ️  Dataset actualizado en memoria temporal")
    
    def show_data_menu(self):
        """Menú para visualizar datos"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("VISUALIZACIÓN DE DATOS")
        print("="*70)
        
        print("\n1. Resumen del dataset")
        print("2. Vista previa de datos")
        print("3. Análisis de atributos")
        
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice == '1':
            self.current_loader.get_summary()
        elif choice == '2':
            try:
                n_rows = input("\n¿Cuántas filas desea ver? (default=10): ").strip()
                n_rows = int(n_rows) if n_rows else 10
                self.current_loader.show_data(n_rows)
            except ValueError:
                self.current_loader.show_data()
        elif choice == '3':
            self.current_loader.analyze_attributes()
        else:
            print("❌ Opción inválida")
    
    def save_dataset_menu(self):
        """Guarda el dataset actual en memoria para operaciones futuras"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("GUARDAR DATASET EN MEMORIA")
        print("="*70)
        
        name = input("Ingrese un nombre para este dataset: ").strip()
        
        if not name:
            print("❌ Debe proporcionar un nombre")
            return
        
        self.saved_datasets[name] = self.current_loader
        print(f"✅ Dataset '{name}' guardado en memoria")
        print(f"   Total de datasets guardados: {len(self.saved_datasets)}")
    
    def save_to_file_menu(self):
        """Menú para exportar datos a archivo"""
        if not self._check_data_loaded():
            return
        
        print("\n" + "="*70)
        print("EXPORTAR DATOS A ARCHIVO")
        print("="*70)
        
        output_path = input("Ingrese la ruta del archivo de salida: ").strip()
        output_path = output_path.strip('"').strip("'")
        
        if not output_path:
            print("❌ Debe proporcionar una ruta")
            return
        
        # Preguntar por el separador
        use_same = input("\n¿Usar el mismo separador del archivo original? (s/n): ").strip().lower()
        
        separator = None
        if use_same != 's':
            print("\nSeparadores comunes:")
            print("  1. Coma (,)")
            print("  2. Punto y coma (;)")
            print("  3. Tabulador (\\t)")
            
            sep_choice = input("\nSeleccione el separador: ").strip()
            
            separator_map = {'1': ',', '2': ';', '3': '\t'}
            separator = separator_map.get(sep_choice, ',')
        
        self.current_loader.save_to_file(output_path, separator)
    
    def manage_datasets_menu(self):
        """Menú para gestionar datasets guardados"""
        print("\n" + "="*70)
        print("DATASETS GUARDADOS EN MEMORIA")
        print("="*70)
        
        if not self.saved_datasets:
            print("\n⚠️  No hay datasets guardados en memoria")
            return
        
        print("\nDatasets disponibles:")
        for i, (name, loader) in enumerate(self.saved_datasets.items(), 1):
            print(f"  {i}. {name} ({loader.n_rows} filas × {loader.n_columns} columnas)")
        
        print("\nAcciones:")
        print("  1. Cargar un dataset")
        print("  2. Eliminar un dataset")
        print("  3. Volver")
        
        action = input("\nSeleccione una acción: ").strip()
        
        if action == '1':
            name = input("\nIngrese el nombre del dataset a cargar: ").strip()
            if name in self.saved_datasets:
                self.current_loader = self.saved_datasets[name]
                print(f"✅ Dataset '{name}' cargado como dataset actual")
            else:
                print("❌ Dataset no encontrado")
        
        elif action == '2':
            name = input("\nIngrese el nombre del dataset a eliminar: ").strip()
            if name in self.saved_datasets:
                del self.saved_datasets[name]
                print(f"✅ Dataset '{name}' eliminado")
            else:
                print("❌ Dataset no encontrado")
    
    def _check_data_loaded(self) -> bool:
        """Verifica si hay datos cargados"""
        if self.current_loader is None or self.current_loader.data_matrix is None:
            print("\n⚠️  Error: No hay datos cargados. Use la opción 1 para cargar un archivo.")
            return False
        return True
    
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


def main():
    """Función principal"""
    system = DataManagementSystem()
    system.run()


if __name__ == "__main__":
    main()
