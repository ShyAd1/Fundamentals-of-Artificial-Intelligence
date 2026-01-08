# Sistema de Carga y Manipulación de Datos - Arquitectura MVC

## 🏗️ Arquitectura MVC con GUI

Sistema completo desarrollado con arquitectura **Modelo-Vista-Controlador (MVC)** e interfaz gráfica usando **Tkinter**.

---

## 📁 Estructura del Proyecto

```
ML P1/
│
├── Model/
│   ├── __init__.py
│   └── DataModel.py          # MODELO - Lógica de negocio y datos
│
├── View/
│   ├── __init__.py
│   └── DataView.py            # VISTA - Interfaz gráfica (GUI)
│
├── Controller/
│   ├── __init__.py
│   └── DataController.py      # CONTROLADOR - Lógica de control
│
├── main_gui.py                # Aplicación principal con GUI
├── main.py                    # Versión de línea de comandos (legacy)
├── data_loader.py             # Clase DataLoader original (legacy)
├── muestraIris.csv            # Dataset de ejemplo
└── README_MVC.md              # Este archivo
```

---

## 🎨 Arquitectura MVC

### 📊 MODELO (`Model/DataModel.py`)
**Responsabilidad:** Gestión de datos y lógica de negocio
- Carga de archivos (CSV, TXT)
- Almacenamiento en matrices NumPy
- Análisis de atributos (cualitativos/cuantitativos)
- Cálculo de estadísticas
- Selección de subconjuntos (filas/columnas)
- Exportación de datos

**Independencia:** No conoce la Vista ni el Controlador

### 🖼️ VISTA (`View/DataView.py`)
**Responsabilidad:** Interfaz gráfica de usuario (GUI)
- Diseño con Tkinter
- 4 pestañas principales:
  - 📁 **Cargar Datos**
  - 🔍 **Análisis**
  - 📊 **Filtrado**
  - 💾 **Exportar**
- Componentes interactivos (botones, listboxes, comboboxes)
- Visualización de datos en tablas

**Independencia:** No conoce el Modelo, solo presenta información

### 🎮 CONTROLADOR (`Controller/DataController.py`)
**Responsabilidad:** Coordinación entre Modelo y Vista
- Maneja eventos de la Vista
- Llama métodos del Modelo
- Actualiza la Vista con resultados
- Valida datos de entrada
- Gestión de estado de la aplicación

**Flujo:** Vista → Controlador → Modelo → Controlador → Vista

---

## 🚀 Instalación y Ejecución

### Requisitos
```bash
Python 3.7+
numpy
tkinter (incluido en Python)
```

### Instalar Dependencias
```bash
pip install numpy
```

### Ejecutar la Aplicación GUI
```bash
python main_gui.py
```

---

## 💻 Uso de la Aplicación

### 🔷 Pestaña 1: Cargar Datos

1. **Examinar archivo** - Selecciona un archivo CSV o TXT
2. **Elegir separador** - Coma, punto y coma, tabulador, etc.
3. **Indicar si tiene encabezados**
4. **Cargar** - Presionar botón "CARGAR ARCHIVO"
5. **Vista previa automática** - Los datos se muestran en tabla

### 🔷 Pestaña 2: Análisis

1. **Ver información general** - Resumen del dataset
2. **Analizar atributos** - Presionar "ANALIZAR ATRIBUTOS"
3. **Resultados detallados:**
   - **Cuantitativos:** Mínimo, máximo, promedio, desv. estándar
   - **Cualitativos:** Categorías y frecuencias

### 🔷 Pestaña 3: Filtrado

**Selección de Columnas:**
- Lista con todas las columnas disponibles
- Selección múltiple (Ctrl/Shift + clic)
- Aplicar selección al dataset

**Selección de Filas - 3 Métodos:**

1. **Por índices:**
   - Formato: `0,5,10-15,20`
   - Soporta rangos y valores individuales

2. **Por rango:**
   - Especificar índice inicial y final
   - Ejemplo: Desde 0 hasta 50

3. **Por valor de columna:**
   - Seleccionar columna del combobox
   - Elegir valor a filtrar
   - Ejemplo: species = "iris-setosa"

### 🔷 Pestaña 4: Exportar

1. **Ver resumen** del dataset actual
2. **Elegir archivo de salida** - Examinar ubicación
3. **Seleccionar separador** - Para el archivo exportado
4. **Exportar** - Guardar datos procesados

---

## 🎯 Funcionalidades Implementadas

### ✅ Requisitos Cumplidos

| # | Funcionalidad | Estado |
|---|---------------|--------|
| 1 | Elegir archivo de texto plano | ✅ |
| 2 | Elegir carácter separador | ✅ |
| 3 | Detectar número de atributos automáticamente | ✅ |
| 4 | Obtener número de renglones | ✅ |
| 5 | Cargar en matriz interna | ✅ |
| 6 | Analizar tipo de atributos | ✅ |
| 7a | Cualitativo: obtener categorías | ✅ |
| 7b | Cuantitativo: mín, máx, promedio, desv. std | ✅ |
| 8 | Seleccionar subconjunto de atributos | ✅ |
| 9a | Selección de filas por enumeración | ✅ |
| 9b | Selección de filas por rango | ✅ |
| 9c | Selección de filas por valor de atributo | ✅ |
| 10 | Pasar dataset a uno nuevo | ✅ |

---

## 🎨 Características de la GUI

### Ventajas de la Interfaz Gráfica

- ✅ **Intuitiva** - No requiere conocimientos de programación
- ✅ **Visual** - Vista previa de datos en tablas
- ✅ **Organizada** - Pestañas separadas por funcionalidad
- ✅ **Interactiva** - Selección múltiple con ratón
- ✅ **Validación** - Mensajes de error y confirmación
- ✅ **Barra de estado** - Información en tiempo real
- ✅ **Responsive** - Ventana redimensionable

### Componentes Principales

- **Treeview** - Visualización de datos en tabla
- **Listbox** - Selección múltiple de columnas
- **Combobox** - Listas desplegables
- **Entry** - Campos de texto
- **Button** - Acciones del usuario
- **ScrolledText** - Áreas de texto con scroll
- **Notebook** - Sistema de pestañas

---

## 📊 Ejemplo de Uso Completo

### Caso: Analizar Flores Iris

1. **Cargar `muestraIris.csv`**
   - Pestaña "Cargar Datos"
   - Examinar → seleccionar archivo
   - Separador: Coma
   - Tiene encabezados: Sí
   - Cargar

2. **Analizar Atributos**
   - Pestaña "Análisis"
   - Ver que hay 4 atributos cuantitativos y 1 cualitativo
   - Observar estadísticas de cada columna

3. **Filtrar Solo Setosa**
   - Pestaña "Filtrado"
   - Método 3: Por valor
   - Columna: species
   - Valor: iris-setosa
   - Aplicar → Confirmar

4. **Seleccionar Solo Pétalos**
   - Mismo tab "Filtrado"
   - Seleccionar columnas: petal_length, petal_width
   - Aplicar → Confirmar

5. **Exportar Resultado**
   - Pestaña "Exportar"
   - Examinar → elegir ubicación: `setosa_petalos.csv`
   - Separador: Coma
   - Exportar

**Resultado:** Archivo con solo medidas de pétalos de flores setosa

---

## 🔧 Ventajas de MVC

### Separación de Responsabilidades
- **Modelo** - Solo datos y lógica
- **Vista** - Solo interfaz
- **Controlador** - Solo coordinación

### Mantenibilidad
- Cambios en la GUI no afectan la lógica
- Cambios en los datos no afectan la interfaz
- Fácil de extender y modificar

### Reutilización
- El Modelo puede usarse con otra Vista (web, mobile)
- La Vista puede conectarse a otro Modelo
- El Controlador se adapta a ambos

### Testabilidad
- Cada componente se puede probar independientemente
- Menor acoplamiento entre capas

---

## 🎓 Patrones Aplicados

### MVC (Model-View-Controller)
Patrón arquitectónico principal

### Observer Pattern
Vista observa eventos del usuario, Controlador responde

### Callback Pattern
Vista usa callbacks para comunicarse con Controlador

### Separation of Concerns
Cada módulo tiene una única responsabilidad

---

## 📝 Comparación: CLI vs GUI

| Aspecto | CLI (main.py) | GUI (main_gui.py) |
|---------|---------------|-------------------|
| **Interfaz** | Línea de comandos | Interfaz gráfica |
| **Uso** | Requiere conocer comandos | Intuitivo con mouse |
| **Visualización** | Texto plano | Tablas y componentes |
| **Selección** | Escribir índices | Clic múltiple |
| **Feedback** | Texto en consola | Mensajes y diálogos |
| **Flexibilidad** | Scripts y automatización | Exploración manual |

**Ambas versiones están disponibles según necesidad del usuario**

---

## 🚀 Futuras Mejoras

### Posibles Extensiones
- ✨ Gráficos y visualizaciones (matplotlib)
- ✨ Operaciones matemáticas entre columnas
- ✨ Exportación a múltiples formatos (Excel, JSON)
- ✨ Historial de operaciones (deshacer/rehacer)
- ✨ Temas personalizables
- ✨ Validación avanzada de datos
- ✨ Fusión de datasets
- ✨ Búsqueda y filtrado avanzado

---

## 👨‍💻 Código de Ejemplo

### Usar Solo el Modelo (sin GUI)

```python
from Model.DataModel import DataModel

# Crear modelo
model = DataModel()

# Cargar datos
success, msg = model.load_file("muestraIris.csv", ",", True)

# Analizar
success, msg, stats = model.analyze_attributes()

# Filtrar
success, msg, nuevo_modelo = model.select_rows_by_value(4, "iris-setosa")

# Guardar
success, msg = nuevo_modelo.save_to_file("resultado.csv", ",")
```

---

## 📚 Documentación de Clases

### DataModel
```python
load_file(filepath, separator, has_header) -> (bool, str)
analyze_attributes() -> (bool, str, dict)
select_attributes(indices) -> (bool, str, DataModel)
select_rows_by_list(indices) -> (bool, str, DataModel)
select_rows_by_range(start, end) -> (bool, str, DataModel)
select_rows_by_value(col_idx, value) -> (bool, str, DataModel)
save_to_file(path, separator) -> (bool, str)
```

### DataView
```python
show_data_preview(data)
show_analysis(analysis_data)
update_status(message)
show_message(title, message, type)
```

### DataController
```python
load_file(filepath, separator, has_header)
analyze_attributes()
select_columns(indices)
select_rows(method, **kwargs)
save_file(output_path, separator)
```

---

## ✅ Conclusión

Sistema completo con **arquitectura MVC** e **interfaz gráfica** que cumple todos los requisitos solicitados. La separación en capas facilita el mantenimiento y extensión del sistema.

**Ventajas clave:**
- 🎯 Arquitectura limpia y mantenible
- 🖱️ Interfaz gráfica intuitiva
- 📊 Análisis completo de datos
- 🔧 Fácil de extender
- 📦 Modular y reutilizable

---

**Desarrollado para:** Fundamentos de Inteligencia Artificial  
**Fecha:** Diciembre 2025  
**Arquitectura:** MVC (Model-View-Controller)  
**GUI Framework:** Tkinter  
**Lenguaje:** Python 3.7+
