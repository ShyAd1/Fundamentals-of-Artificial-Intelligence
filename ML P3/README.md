# Sistema de Validación de Modelos ML

Sistema completo de validación de modelos de Machine Learning con interfaz gráfica interactiva.

## 📋 Características

### Requisitos Implementados:

✅ **REQUISITOS GENERALES**
1. Carga de base de datos (CSV/Excel)
2. Selección de atributos de entrada (X)
3. Selección de atributo de salida (Y)

✅ **TRAIN AND TEST**
- Porcentaje configurable para entrenamiento/prueba
- Cálculo de accuracy y error
- Matriz de confusión

✅ **K-FOLD CROSS VALIDATION**
- Número de folds (K) configurable
- Métricas por cada fold
- Estadísticas generales con desviación estándar

✅ **BOOTSTRAP**
- Número de experimentos configurable
- Tamaños de conjuntos configurables
- Métricas por experimento y por clase
- Estadísticas generales con desviación estándar

✅ **GUI 100% Funcional e Interactiva**
- Interfaz intuitiva con pestañas
- Visualización clara de resultados
- Múltiples modelos de clasificación

## 🚀 Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

```bash
python main.py
```

## 📖 Uso

### 1. Cargar Datos
- Ve a la pestaña "📁 Cargar Datos"
- Haz clic en "Cargar Archivo CSV/Excel"
- Selecciona tu archivo de datos

### 2. Configurar Features
- Selecciona los atributos de entrada (X) - puedes seleccionar múltiples
- Selecciona el atributo de salida (Y)
- Elige el modelo de clasificación
- Haz clic en "Confirmar Configuración"

### 3. Ejecutar Validaciones

#### Train & Test:
- Ve a la pestaña "🔀 Train & Test"
- Ajusta el porcentaje de prueba
- Haz clic en "Ejecutar Train & Test"

#### K-Fold CV:
- Ve a la pestaña "🔄 K-Fold CV"
- Especifica el número de folds (K)
- Haz clic en "Ejecutar K-Fold CV"

#### Bootstrap:
- Ve a la pestaña "🎲 Bootstrap"
- Configura número de experimentos
- Opcionalmente, especifica tamaños de conjuntos
- Haz clic en "Ejecutar Bootstrap"

## 🎯 Modelos Disponibles

- **Decision Tree**: Árbol de decisión
- **Random Forest**: Bosque aleatorio
- **K-Nearest Neighbors**: K vecinos más cercanos
- **Naive Bayes**: Clasificador bayesiano

## 📊 Archivo de Ejemplo

Se incluye `example_data.csv` con datos del dataset Iris para pruebas.

## 🛠️ Tecnologías

- **Python 3.x**
- **Tkinter**: Interfaz gráfica
- **Pandas**: Manipulación de datos
- **NumPy**: Cálculos numéricos
- **Scikit-learn**: Modelos de ML y métricas
- **Matplotlib**: Visualización (preparado para gráficos)

## 📝 Estructura del Proyecto

```
ML P3/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── example_data.csv     # Datos de ejemplo
└── README.md           # Este archivo
```

## 👨‍💻 Características Técnicas

### ValidationSystem Class:
- `load_data()`: Carga CSV/Excel
- `set_features()`: Configura X e Y
- `train_and_test()`: Validación train/test
- `k_fold_cross_validation()`: K-Fold CV
- `bootstrap()`: Validación bootstrap

### MLValidationGUI Class:
- Interfaz con 4 pestañas
- Validación de entrada
- Visualización de resultados
- Manejo de errores

## 📈 Métricas Calculadas

Todas las validaciones calculan:
- **Accuracy**: Porcentaje de aciertos
- **Error**: Porcentaje de errores
- **Matriz de Confusión**: Para análisis detallado
- **Desviación Estándar**: Para K-Fold y Bootstrap

Bootstrap adicional:
- Métricas por clase
- Estadísticas por experimento

## ⚙️ Configuraciones

### Train & Test:
- Porcentaje de prueba: 10-50%

### K-Fold CV:
- Número de folds: 2-20

### Bootstrap:
- Experimentos: 2-100
- Tamaños auto o manual

## 🎨 Interfaz

La GUI incluye:
- 📁 Pestaña de carga de datos con vista previa
- 🔀 Pestaña Train & Test con slider de configuración
- 🔄 Pestaña K-Fold con spinner de folds
- 🎲 Pestaña Bootstrap con configuración completa
- Resultados formateados y legibles
- Mensajes de error informativos

## 🧪 Ejemplo de Uso Rápido

1. Ejecuta `python main.py`
2. Carga `example_data.csv`
3. Selecciona columnas 0-3 como entrada
4. Selecciona columna 4 (species) como salida
5. Prueba cada método de validación

¡Sistema 100% funcional y listo para usar!
