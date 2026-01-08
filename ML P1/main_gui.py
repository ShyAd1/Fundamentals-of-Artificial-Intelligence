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
