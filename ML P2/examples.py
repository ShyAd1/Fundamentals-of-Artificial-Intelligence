"""
Ejemplos de uso del sistema de clasificadores.
Ejecutar: python3 examples.py
"""

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier
from src.distance_metrics import DistanceMetrics


def example_1_simple_classification():
    """Ejemplo 1: Clasificación simple con datos manuales"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Clasificación Simple")
    print("="*60)
    
    # Crear dataset para clasificar puntos en un plano 2D
    ds = Dataset(input_size=2, output_size=1)
    
    # Agregar datos de entrenamiento
    # Clase 0: esquina inferior izquierda
    ds.add_sample([0.1, 0.1], [0])
    ds.add_sample([0.2, 0.2], [0])
    
    # Clase 1: esquina superior derecha
    ds.add_sample([9.8, 9.8], [1])
    ds.add_sample([9.9, 9.9], [1])
    
    # Crear clasificadores
    knn = KNNClassifier(ds, k=1, distance_metric='euclidean')
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    
    # Realizar predicciones
    test_points = [[0.5, 0.5], [5.0, 5.0], [9.5, 9.5]]
    
    print("\nPredicciones:")
    for point in test_points:
        knn_pred = knn.predict(point)
        md_pred = md.predict(point)
        print(f"Punto {point}:")
        print(f"  K-NN (k=1):      {knn_pred}")
        print(f"  Mín Distancia:   {md_pred}")


def example_2_iris_dataset():
    """Ejemplo 2: Usar el dataset de Iris"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Dataset de Iris")
    print("="*60)
    
    # Cargar datos
    ds = Dataset(input_size=4, output_size=1)
    ds.load_from_file('data/training_data.txt')
    
    # Crear clasificadores con diferentes parámetros
    knn_k3 = KNNClassifier(ds, k=3, distance_metric='euclidean')
    knn_k5 = KNNClassifier(ds, k=5, distance_metric='manhattan')
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    
    # Punto de prueba (setosa típica)
    test_point = [5.1, 3.5, 1.4, 0.2]
    
    print(f"\nClasificando: {test_point}")
    print(f"KNN (k=3, euclidiana): {knn_k3.predict(test_point)}")
    print(f"KNN (k=5, manhattan):  {knn_k5.predict(test_point)}")
    print(f"Mínima Distancia:      {md.predict(test_point)}")
    print(f"Clases detectadas:     {md.get_prototypes_count()}")


def example_3_distance_metrics():
    """Ejemplo 3: Comparar métricas de distancia"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Métricas de Distancia")
    print("="*60)
    
    p1 = [1, 2, 3]
    p2 = [4, 5, 6]
    
    euclidean = DistanceMetrics.euclidean(p1, p2)
    manhattan = DistanceMetrics.manhattan(p1, p2)
    
    print(f"\nPunto 1: {p1}")
    print(f"Punto 2: {p2}")
    print(f"\nDistancia Euclidiana: {euclidean:.4f}")
    print(f"Distancia Manhattan:  {manhattan:.4f}")
    print(f"\nFórmulas:")
    print(f"Euclidiana: sqrt((4-1)² + (5-2)² + (6-3)²) = sqrt(9+9+9) = sqrt(27) ≈ {euclidean:.4f}")
    print(f"Manhattan:  |4-1| + |5-2| + |6-3| = 3 + 3 + 3 = {manhattan:.4f}")


def example_4_save_and_load():
    """Ejemplo 4: Guardar y cargar datos"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Guardar y Cargar Datos")
    print("="*60)
    
    # Crear dataset
    ds1 = Dataset(input_size=2, output_size=1)
    ds1.add_sample([1.0, 2.0], [0])
    ds1.add_sample([3.0, 4.0], [1])
    ds1.add_sample([5.0, 6.0], [0])
    
    # Guardar
    filepath = 'data/custom_data.txt'
    ds1.save_to_file(filepath)
    
    # Cargar
    ds2 = Dataset(input_size=2, output_size=1)
    ds2.load_from_file(filepath)
    
    print(f"\nDataset original: {ds1}")
    print(f"Dataset cargado:  {ds2}")
    print(f"¿Son iguales? {ds1.get_size() == ds2.get_size()}")


def example_5_batch_prediction():
    """Ejemplo 5: Predicciones por lotes"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Predicciones por Lotes")
    print("="*60)
    
    # Dataset simple
    ds = Dataset(input_size=2, output_size=1)
    ds.add_sample([0, 0], [0])
    ds.add_sample([1, 1], [1])
    ds.add_sample([1, 0], [0])
    ds.add_sample([0, 1], [1])
    
    # Clasificador
    knn = KNNClassifier(ds, k=2, distance_metric='euclidean')
    
    # Múltiples predicciones
    test_points = [
        [0.1, 0.1],
        [0.9, 0.9],
        [0.5, 0.5],
        [0.9, 0.1]
    ]
    
    predictions = knn.predict_batch(test_points)
    
    print("\nPredicciones por lotes:")
    for point, pred in zip(test_points, predictions):
        print(f"{point} -> {pred}")


def example_6_compare_classifiers():
    """Ejemplo 6: Comparar rendimiento de clasificadores"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Comparación de Clasificadores")
    print("="*60)
    
    # Dataset con datos de iris
    ds = Dataset(input_size=4, output_size=1)
    ds.load_from_file('data/training_data.txt')
    
    # Diferentes configuraciones
    classifiers = [
        ("KNN (k=1, euclidiana)", KNNClassifier(ds, k=1, distance_metric='euclidean')),
        ("KNN (k=3, euclidiana)", KNNClassifier(ds, k=3, distance_metric='euclidean')),
        ("KNN (k=3, manhattan)",  KNNClassifier(ds, k=3, distance_metric='manhattan')),
        ("Mín Distancia (euclidiana)", MinimumDistanceClassifier(ds, distance_metric='euclidean')),
        ("Mín Distancia (manhattan)",   MinimumDistanceClassifier(ds, distance_metric='manhattan')),
    ]
    
    # Puntos de prueba
    test_points = [
        ([5.1, 3.5, 1.4, 0.2], "Setosa"),
        ([6.0, 2.7, 5.1, 1.6], "Versicolor"),
        ([7.1, 3.0, 5.9, 2.1], "Virginica"),
    ]
    
    print("\nComparación de predicciones:")
    for point, label in test_points:
        print(f"\n{label}: {point}")
        for name, classifier in classifiers:
            pred = classifier.predict(point)
            print(f"  {name:30s} -> {pred}")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*70)
    print("EJEMPLOS DE USO DEL SISTEMA DE CLASIFICADORES")
    print("="*70)
    
    try:
        example_1_simple_classification()
        example_2_iris_dataset()
        example_3_distance_metrics()
        example_4_save_and_load()
        example_5_batch_prediction()
        example_6_compare_classifiers()
        
        print("\n" + "="*70)
        print("✓ Todos los ejemplos ejecutados correctamente")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
