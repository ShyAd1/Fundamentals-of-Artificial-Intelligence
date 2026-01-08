# Sistema de Carga y Manipulación de Conjuntos de Datos

Sistema completo para cargar, analizar y manipular conjuntos de datos para problemas de Inteligencia Artificial.

## 📋 Características Implementadas

### 1. ✅ Carga de Archivos
- Soporta archivos de texto plano (.txt, .csv)
- Selección de carácter separador personalizado
- Detección automática de encabezados

### 2. ✅ Análisis Automático de Datos
- Detección automática del número de atributos (columnas)
- Conteo automático de muestras (filas)
- Carga de datos en matriz interna (NumPy)

### 3. ✅ Análisis de Atributos
**Atributos Cualitativos:**
- Identificación de categorías únicas
- Conteo de ocurrencias por categoría

**Atributos Cuantitativos:**
- Cálculo de valor mínimo
- Cálculo de valor máximo
- Cálculo de promedio
- Cálculo de desviación estándar

### 4. ✅ Selección de Subconjuntos de Atributos
- Reducción de la matriz seleccionando columnas específicas
- Soporta múltiples formatos de entrada

### 5. ✅ Selección de Subconjuntos de Filas
Tres métodos de selección:
- **a) Enumeración:** Especificar índices individuales (ej: 0,5,10)
- **b) Rangos:** Especificar rangos de filas (ej: 0-10)
- **c) Filtrado por valor:** Seleccionar filas según el valor de un atributo

### 6. ✅ Gestión de Múltiples Datasets
- Guardar datasets procesados en memoria
- Cargar datasets guardados
- Trabajar con múltiples conjuntos de datos simultáneamente

### 7. ✅ Exportación de Datos
- Guardar datasets procesados en archivos
- Selección de separador para exportación

## 🚀 Instalación

### Requisitos
```bash
Python 3.7+
numpy
```

### Instalar dependencias
```bash
pip install numpy
```

## 💻 Uso

### Ejecución del Sistema
```bash
python main.py
```

### Ejemplo de Uso Básico

1. **Cargar un archivo:**
   - Seleccionar opción 1
   - Ingresar la ruta: `muestraIris.csv`
   - Seleccionar separador: `,` (coma)
   - Confirmar si tiene encabezados: `s`

2. **Analizar atributos:**
   - Seleccionar opción 2
   - El sistema mostrará automáticamente:
     - Tipo de cada atributo (cualitativo/cuantitativo)
     - Estadísticas correspondientes

3. **Filtrar datos por especie:**
   - Seleccionar opción 4 (Seleccionar filas)
   - Método 3 (Filtrar por valor)
   - Columna 4 (species)
   - Valor: `iris-setosa`

4. **Guardar el subconjunto:**
   - Seleccionar opción 6 (Guardar en memoria)
   - Asignar un nombre: `solo_setosa`

5. **Exportar a archivo:**
   - Seleccionar opción 7
   - Ingresar ruta: `iris_setosa.csv`

## 📁 Estructura del Proyecto

```
ML P1/
│
├── data_loader.py       # Clase principal DataLoader
├── main.py             # Sistema interactivo con menú
├── muestraIris.csv     # Dataset de ejemplo (Iris)
└── README.md           # Este archivo
```

## 🔧 Componentes Principales

### Clase `DataLoader`
Maneja todas las operaciones de carga y manipulación de datos:
- `load_file()`: Carga archivos de texto plano
- `analyze_attributes()`: Analiza tipos de atributos
- `select_attributes()`: Selecciona columnas específicas
- `select_rows_by_list()`: Selecciona filas por índices
- `select_rows_by_range()`: Selecciona filas por rango
- `select_rows_by_value()`: Filtra filas por valor
- `save_to_file()`: Exporta datos a archivo

### Clase `DataManagementSystem`
Sistema de menú interactivo que facilita el uso del DataLoader

## 📊 Ejemplo con Dataset Iris

El archivo `muestraIris.csv` incluido contiene 60 muestras del famoso dataset Iris:
- **4 atributos cuantitativos:** sepal_length, sepal_width, petal_length, petal_width
- **1 atributo cualitativo:** species (iris-setosa, iris-versicolor, iris-virginica)
- **60 muestras** (20 de cada especie)

### Operaciones Comunes:

**Filtrar solo flores setosa:**
```
Opción 4 → Método 3 → Columna 4 → Valor: iris-setosa
```

**Seleccionar solo medidas de pétalos:**
```
Opción 3 → Índices: 2,3
```

**Obtener primeras 10 muestras:**
```
Opción 4 → Método 2 → Inicio: 0, Fin: 9
```

## 🎯 Casos de Uso

1. **Preprocesamiento de datos** para algoritmos de ML
2. **Exploración de datasets** antes del análisis
3. **Filtrado y limpieza** de datos
4. **Selección de características** (feature selection)
5. **Creación de subconjuntos** para entrenamiento/prueba

## 📝 Notas Técnicas

- Los índices son **0-indexed** (comienzan en 0)
- Los datos se almacenan en matrices NumPy para eficiencia
- Los subconjuntos creados son **nuevos objetos** (no modifican el original)
- Los datasets se pueden guardar en memoria para operaciones posteriores

## 🔍 Formato de Índices Soportados

- **Individual:** `0,2,5,7`
- **Rango:** `0-10`
- **Combinado:** `0,2-5,8,10-15`

## ⚡ Ventajas del Sistema

- ✅ Interfaz interactiva fácil de usar
- ✅ No requiere programación para uso básico
- ✅ Análisis automático de tipos de datos
- ✅ Múltiples métodos de filtrado
- ✅ Gestión de múltiples datasets
- ✅ Exportación flexible

## 🎓 Ejemplo de Sesión Completa

```
1. Cargar muestraIris.csv
2. Analizar atributos → Ver estadísticas
3. Guardar dataset como "iris_completo"
4. Filtrar solo iris-setosa
5. Seleccionar solo columnas de pétalos (2,3)
6. Guardar como "setosa_petalos"
7. Exportar a "setosa_petalos.csv"
8. Cargar "iris_completo" de memoria
9. Continuar con otros análisis...
```

## 🤝 Autor

Sistema desarrollado para Fundamentos de Inteligencia Artificial

---

**Fecha:** Diciembre 2025
