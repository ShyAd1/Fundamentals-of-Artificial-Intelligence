# Sistema de Clasificadores ML - GUI

Sistema de clasificación de patrones con interfaz gráfica usando K-NN y Mínima Distancia.

## Inicio Rápido

```bash
python gui.py
```

## Estructura del Proyecto

```
ML P2/
├── src/                    # Biblioteca principal (implementación manual)
│   ├── dataset.py          # Gestión de datasets
│   ├── distance_metrics.py # Métricas de distancia
│   ├── knn_classifier.py   # Clasificador K-NN
│   └── minimum_distance_classifier.py
├── data/                   # Datos de entrenamiento
│   └── training_data.txt   # Dataset de ejemplo (Iris)
└── gui.py                  # Interfaz gráfica
```

## Cómo Usar la GUI

1. **Ejecutar la aplicación:**

   ```bash
   python gui.py
   ```

2. **Cargar datos:**

   - Haz clic en "Cargar Dataset"
   - Selecciona `data/training_data.txt` o tu propio archivo

3. **Configurar clasificador:**

   - Elige entre K-NN o Mínima Distancia
   - Ajusta parámetros (k, métrica de distancia)

4. **Hacer predicciones:**
   - Ingresa valores de entrada
   - Haz clic en "Predecir"
   - Ver resultados

## Formato de Datos

Los archivos deben seguir este formato:

```
# Comentarios empiezan con #
entrada1, entrada2, entrada3, entrada4 | salida
5.1, 3.5, 1.4, 0.2 | 0.0
6.0, 2.7, 5.1, 1.6 | 1.0
7.1, 3.0, 5.9, 2.1 | 2.0
```

## Características

- Implementación 100% manual (sin numpy, sklearn, etc.)
- Interfaz gráfica intuitiva
- Múltiples métricas de distancia (Euclidiana, Manhattan)
- K-NN con k ajustable
- Clasificador de Mínima Distancia
- Visualización de resultados

## Requisitos

- Python 3.6 o superior
- Tkinter (incluido con Python)

## Algoritmos Implementados

### K-NN (K-Nearest Neighbors)

- Encuentra los k vecinos más cercanos
- Promedia sus valores de salida
- Ajustable mediante parámetro k

### Mínima Distancia

- Calcula prototipos (centros) de cada clase
- Clasifica según el prototipo más cercano
- Entrenamiento automático

## Documentación

Todo el código está implementado manualmente sin bibliotecas externas. Ver archivos en `src/` para detalles de implementación.

## Uso Educativo

Este proyecto es ideal para aprender cómo funcionan los algoritmos de clasificación internamente, ya que todo está implementado desde cero.
