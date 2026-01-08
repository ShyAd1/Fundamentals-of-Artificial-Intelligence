#!/usr/bin/env python3
"""
INICIO RÁPIDO - Sistema de Clasificadores K-NN y Mínima Distancia
Ejecutar: python3 quick_start.py
"""

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier


def main():
    print("\n" + "="*70)
    print("INICIO RÁPIDO - SISTEMA DE CLASIFICADORES")
    print("="*70)
    
    # Paso 1: Cargar datos
    print("\n[1/4] Cargando datos de entrenamiento...")
    ds = Dataset(input_size=4, output_size=1)
    ds.load_from_file('data/training_data.txt')
    print(f"      {ds}")
    
    # Paso 2: Entrenar clasificadores
    print("\n[2/4] Entrenando clasificadores...")
    knn = KNNClassifier(ds, k=3, distance_metric='euclidean')
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    print(f"      {knn.get_info()}")
    print(f"      {md.get_info()}")
    
    # Paso 3: Realizar predicciones
    print("\n[3/4] Realizando predicciones...")
    test_cases = [
        ([5.1, 3.5, 1.4, 0.2], "Iris Setosa"),
        ([6.0, 2.7, 5.1, 1.6], "Iris Versicolor"),
        ([7.1, 3.0, 5.9, 2.1], "Iris Virginica"),
    ]
    
    for test_point, label in test_cases:
        knn_pred = knn.predict(test_point)
        md_pred = md.predict(test_point)
        print(f"\n      {label}:")
        print(f"        K-NN: {knn_pred[0]:.1f}  |  Mín Distancia: {md_pred[0]:.1f}")
    
    # Paso 4: Configurar parámetros
    print("\n[4/4] Ajustando parámetros...")
    knn.set_k(1)
    knn.set_distance_metric('manhattan')
    print(f"      {knn.get_info()}")
    
    pred = knn.predict([5.1, 3.5, 1.4, 0.2])
    print(f"      Nueva predicción con K=1: {pred[0]:.1f}")
    
    print("\n" + "="*70)
    print("✓ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print("\nPróximos pasos:")
    print("  • Ejecutar 'python3 main.py' para la interfaz interactiva")
    print("  • Ejecutar 'python3 examples.py' para más ejemplos")
    print("  • Ver README.md para documentación completa")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
