# Sistema de Validación de Modelos ML - GUI

Sistema de validación de modelos de Machine Learning con interfaz gráfica.

**Implementación Propia:** Todos los algoritmos implementados manualmente sin usar scikit-learn.

## Inicio Rápido

### Windows (Más Fácil):

```bash
EJECUTAR.bat
```

_Doble clic en el archivo o ejecutar desde terminal_

### Cualquier Sistema:

```bash
pip install -r requirements.txt
python main.py
```

## Estructura del Proyecto

```
ML P3/
├── main.py              # GUI principal con todos los algoritmos
├── example_data.csv     # Dataset de ejemplo (Iris)
├── requirements.txt     # Dependencias necesarias
├── EJECUTAR.bat         # Ejecutar en Windows
└── README.md            # Esta documentación
```

## Cómo Usar la GUI

### 1. Cargar Datos

- Pestaña "Cargar Datos"
- Cargar archivo CSV o Excel
- Vista previa de los datos

### 2. Configurar

- Seleccionar columnas de entrada (X)
- Seleccionar columna de salida (Y)
- Elegir modelo de clasificación
- Confirmar configuración

### 3. Validar

Tres métodos disponibles:

**Train & Test:**

- Ajustar porcentaje de prueba (10-50%)
- Ver accuracy, error y matriz de confusión

**K-Fold Cross Validation:**

- Configurar número de folds (2-20)
- Ver métricas por fold y estadísticas

**Bootstrap:**

- Configurar experimentos (2-100)
- Ver métricas por experimento y estadísticas

## Modelos Implementados (SIN sklearn)

- **Decision Tree** - Árbol de decisión con índice Gini
- **Random Forest** - Conjunto de árboles
- **K-Nearest Neighbors** - KNN con distancia euclidiana
- **Naive Bayes** - Clasificador bayesiano gaussiano
- **Minimum Distance** - Clasificador basado en prototipos

## Métodos de Validación (SIN sklearn)

- **Train/Test Split** - División entrenamiento/prueba
- **K-Fold Cross Validation** - Validación cruzada con K folds
- **Bootstrap** - Muestreo con reemplazo

## Requisitos

- Python 3.7 o superior
- pandas
- numpy
- matplotlib
- tkinter (incluido con Python)

## Archivo de Ejemplo

Se incluye `example_data.csv` con el dataset Iris para pruebas.

**Uso rápido:**

1. Ejecutar la aplicación
2. Cargar `example_data.csv`
3. Seleccionar columnas 0-3 como entrada (X)
4. Seleccionar columna 4 como salida (Y)
5. Elegir un modelo
6. Probar los métodos de validación

## Métricas Calculadas

Para todos los métodos:

- **Accuracy** - Porcentaje de aciertos
- **Error** - Porcentaje de errores
- **Matriz de Confusión** - Análisis detallado

Para K-Fold y Bootstrap:

- **Desviación Estándar** - Variabilidad de resultados
- **Estadísticas por Fold/Experimento**

## Características

- Interfaz gráfica intuitiva
- Soporte para CSV y Excel
- Múltiples modelos de clasificación
- Tres métodos de validación
- Visualización clara de resultados
- Manejo de errores robusto
- 100% implementación propia (sin sklearn para algoritmos)

## Uso Educativo

Este proyecto es ideal para entender:

- Cómo funcionan los algoritmos de clasificación internamente
- Cómo se implementan los métodos de validación
- Cómo crear interfaces gráficas para ML

## Documentación

Todo el código está documentado. Los algoritmos están implementados manualmente sin usar sklearn para aprendizaje educativo.

¡Listo para usar!
