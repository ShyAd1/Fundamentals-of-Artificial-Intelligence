# Sistema de Clasificadores K-NN y Mínima Distancia

## Descripción

Sistema completo de aprendizaje automático que implementa dos algoritmos de clasificación:

1. **K-NN (K-Nearest Neighbors)**: Clasifica basándose en los k vecinos más cercanos
2. **Mínima Distancia**: Clasifica basándose en la distancia mínima a prototipos de clase

## Características Implementadas

✓ Define el tamaño de los vectores de entrada y salida  
✓ Introduce valores para vectores de entrada y salida  
✓ Entrena a partir de archivos de texto plano  
✓ K-NN con distancia euclidiana y Manhattan  
✓ Mínima Distancia con distancia euclidiana y Manhattan  
✓ Interfaz interactiva completa  

## Estructura del Proyecto

```
.
├── src/
│   ├── __init__.py
│   ├── dataset.py                      # Gestión de datos
│   ├── distance_metrics.py             # Métricas de distancia
│   ├── knn_classifier.py               # Clasificador K-NN
│   └── minimum_distance_classifier.py  # Mínima Distancia
├── data/
│   └── training_data.txt               # Datos de ejemplo
├── tests/
├── main.py                             # Interfaz principal
└── README.md                           # Documentación
```

## Instalación y Uso

```bash
# Ejecutar el sistema
python3 main.py
```

## Ejecución en Windows

```bash
# Opcional: crear entorno virtual
python -m venv .venv
".venv\\Scripts\\activate"

# Ejecutar GUI (Tkinter)
python gui.py

# Alternativa: interfaz de texto
python main.py
```

Notas:
- Usa el instalador oficial de Python marcando "tcl/tk" (Tkinter viene incluido por defecto).
- Ejecuta los comandos desde la carpeta del proyecto.
- Rutas de datos (`data/`) funcionan sin cambios; si usas rutas absolutas, en Windows van con `\\`.

## Menú Principal

```
1. Configuración       - Define tamaños de entrada/salida
2. Datos             - Carga, agrega o guarda datos
3. Entrenamiento     - Entrena los clasificadores
4. Predicción        - Realiza predicciones
5. Configuración     - Ajusta K y métricas
6. Estadísticas      - Ve información del sistema
7. Salir
```

## Formato de Datos

```
entrada1,entrada2,entrada3 | salida1
entrada4,entrada5,entrada6 | salida2
```

Ejemplo:
```
5.1,3.5,1.4,0.2 | 0
7.0,3.2,4.7,1.4 | 1
6.3,3.3,6.0,2.5 | 2
```

## API de Clases

### Dataset
```python
ds = Dataset(input_size=4, output_size=1)
ds.add_sample([5.1, 3.5, 1.4, 0.2], [0])
ds.load_from_file('data/training_data.txt')
ds.save_to_file('output.txt')
```

### K-NN
```python
knn = KNNClassifier(ds, k=3, distance_metric='euclidean')
prediction = knn.predict([5.5, 3.0, 1.5, 0.2])
knn.set_k(5)
knn.set_distance_metric('manhattan')
```

### Mínima Distancia
```python
md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
prediction = md.predict([5.5, 3.0, 1.5, 0.2])
md.set_distance_metric('manhattan')
print(md.get_prototypes_count())  # Número de clases
```

## Requisitos

- Python 3.7+
- Sin dependencias externas

## Autor

Sistema de Fundamentos de IA - Enero 2026
