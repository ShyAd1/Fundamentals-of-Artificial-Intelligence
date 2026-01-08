"""
Script de pruebas para validar el sistema de clasificadores.
Ejecuta: python3 tests/test_system.py
"""

import sys
import os

# Agregar la ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier
from src.distance_metrics import DistanceMetrics


def test_distance_metrics():
    """Prueba las métricas de distancia"""
    print("\n" + "="*60)
    print("PRUEBA 1: Métricas de Distancia")
    print("="*60)
    
    p1 = [0, 0]
    p2 = [3, 4]
    
    euclidean = DistanceMetrics.euclidean(p1, p2)
    manhattan = DistanceMetrics.manhattan(p1, p2)
    
    print(f"Punto 1: {p1}")
    print(f"Punto 2: {p2}")
    print(f"Distancia Euclidiana: {euclidean:.4f} (esperado: 5.0)")
    print(f"Distancia Manhattan: {manhattan:.4f} (esperado: 7.0)")
    
    assert abs(euclidean - 5.0) < 0.001, "Error en distancia euclidiana"
    assert abs(manhattan - 7.0) < 0.001, "Error en distancia manhattan"
    print("✓ Métricas de distancia OK")
    return True


def test_dataset():
    """Prueba la gestión de datasets"""
    print("\n" + "="*60)
    print("PRUEBA 2: Dataset")
    print("="*60)
    
    # Crear dataset
    ds = Dataset(2, 1)
    print(f"Dataset creado: {ds}")
    
    # Agregar muestras
    ds.add_sample([0, 0], [0])
    ds.add_sample([1, 1], [1])
    ds.add_sample([1, 0], [0])
    
    print(f"Muestras agregadas: {ds.get_size()}")
    assert ds.get_size() == 3, "Error al agregar muestras"
    
    # Guardar y cargar
    filepath = "tests/test_data.txt"
    os.makedirs("tests", exist_ok=True)
    ds.save_to_file(filepath)
    
    ds2 = Dataset(2, 1)
    ds2.load_from_file(filepath)
    print(f"Muestras cargadas: {ds2.get_size()}")
    assert ds2.get_size() == 3, "Error al cargar dataset"
    
    print("✓ Dataset OK")
    return True


def test_knn():
    """Prueba el clasificador K-NN"""
    print("\n" + "="*60)
    print("PRUEBA 3: Clasificador K-NN")
    print("="*60)
    
    # Crear dataset simple
    ds = Dataset(2, 1)
    ds.add_sample([0, 0], [0])
    ds.add_sample([1, 1], [1])
    ds.add_sample([1, 0], [0])
    ds.add_sample([0, 1], [1])
    
    # Crear clasificador K-NN
    knn = KNNClassifier(ds, k=1, distance_metric='euclidean')
    print(f"Clasificador creado: {knn.get_info()}")
    
    # Realizar predicciones
    pred1 = knn.predict([0.1, 0.1])
    pred2 = knn.predict([0.9, 0.9])
    
    print(f"Predicción para [0.1, 0.1]: {pred1} (esperado cercano a [0])")
    print(f"Predicción para [0.9, 0.9]: {pred2} (esperado cercano a [1])")
    
    # Cambiar parámetros
    knn.set_k(3)
    knn.set_distance_metric('manhattan')
    print(f"Parámetros actualizados: {knn.get_info()}")
    
    print("✓ K-NN OK")
    return True


def test_minimum_distance():
    """Prueba el clasificador de Mínima Distancia"""
    print("\n" + "="*60)
    print("PRUEBA 4: Clasificador Mínima Distancia")
    print("="*60)
    
    # Crear dataset
    ds = Dataset(2, 1)
    ds.add_sample([0, 0], [0])
    ds.add_sample([1, 1], [1])
    ds.add_sample([1, 0], [0])
    ds.add_sample([0, 1], [1])
    
    # Crear clasificador
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    print(f"Clasificador creado: {md.get_info()}")
    print(f"Clases detectadas: {md.get_prototypes_count()}")
    
    # Realizar predicciones
    pred1 = md.predict([0.1, 0.1])
    pred2 = md.predict([0.9, 0.9])
    
    print(f"Predicción para [0.1, 0.1]: {pred1}")
    print(f"Predicción para [0.9, 0.9]: {pred2}")
    
    # Cambiar métrica
    md.set_distance_metric('manhattan')
    print(f"Métrica actualizada: {md.get_info()}")
    
    print("✓ Mínima Distancia OK")
    return True


def test_iris_dataset():
    """Prueba con el dataset de iris"""
    print("\n" + "="*60)
    print("PRUEBA 5: Dataset de Iris")
    print("="*60)
    
    # Cargar datos de iris
    ds = Dataset(4, 1)
    try:
        ds.load_from_file('data/training_data.txt')
        print(f"✓ Dataset Iris cargado: {ds}")
        
        # Probar K-NN
        knn = KNNClassifier(ds, k=3, distance_metric='euclidean')
        pred = knn.predict([5.1, 3.5, 1.4, 0.2])
        print(f"K-NN predicción: {pred}")
        
        # Probar Mínima Distancia
        md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
        pred = md.predict([5.1, 3.5, 1.4, 0.2])
        print(f"MD predicción: {pred}")
        print(f"Clases detectadas: {md.get_prototypes_count()}")
        
        print("✓ Dataset Iris OK")
        return True
    except FileNotFoundError:
        print("✗ Archivo de iris no encontrado")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("PRUEBAS DEL SISTEMA DE CLASIFICADORES")
    print("="*60)
    
    tests = [
        ("Distancia", test_distance_metrics),
        ("Dataset", test_dataset),
        ("K-NN", test_knn),
        ("Mínima Distancia", test_minimum_distance),
        ("Iris", test_iris_dataset),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Error en {name}: {e}")
            failed += 1
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Pruebas pasadas: {passed}/{len(tests)}")
    print(f"Pruebas fallidas: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ¡Todas las pruebas pasaron!")
        return 0
    else:
        print(f"\n✗ {failed} prueba(s) fallaron")
        return 1


if __name__ == "__main__":
    exit(main())
