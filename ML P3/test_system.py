"""
Script de prueba para validar la funcionalidad del sistema
sin necesidad de GUI
"""

from main import ValidationSystem
import pandas as pd

# Crear instancia del sistema
system = ValidationSystem()

# Cargar datos de ejemplo
print("="*60)
print("CARGANDO DATOS")
print("="*60)
data = system.load_data("example_data.csv")
print(f"✓ Datos cargados: {data.shape[0]} filas x {data.shape[1]} columnas")
print(f"✓ Columnas: {list(data.columns)}")
print()

# Configurar features
print("="*60)
print("CONFIGURANDO FEATURES")
print("="*60)
input_features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
output_feature = 'species'
system.set_features(input_features, output_feature)
print(f"✓ Features de entrada: {input_features}")
print(f"✓ Feature de salida: {output_feature}")
print()

# 1. TRAIN AND TEST
print("="*60)
print("1. TRAIN AND TEST")
print("="*60)
results = system.train_and_test(test_size=0.3)
print(f"Accuracy: {results['accuracy']:.2f}%")
print(f"Error: {results['error']:.2f}%")
print(f"Train size: {results['train_size']}")
print(f"Test size: {results['test_size']}")
print()

# 2. K-FOLD CROSS VALIDATION
print("="*60)
print("2. K-FOLD CROSS VALIDATION")
print("="*60)
results = system.k_fold_cross_validation(k=5)
print(f"K = 5 folds")
for fold in results['fold_results']:
    print(f"  Fold {fold['fold']}: Accuracy = {fold['accuracy']:.2f}%")
print(f"\nPromedio: {results['mean_accuracy']:.2f}% ± {results['std_accuracy']:.2f}%")
print()

# 3. BOOTSTRAP
print("="*60)
print("3. BOOTSTRAP")
print("="*60)
results = system.bootstrap(n_experiments=10)
print(f"Experimentos: {results['n_experiments']}")
print(f"Train size: {results['train_size']}")
print(f"Test size: {results['test_size']}")
print(f"\nPromedio general: {results['mean_accuracy']:.2f}% ± {results['std_accuracy']:.2f}%")
print("\nEstadísticas por clase:")
for cls, stats in results['class_stats'].items():
    print(f"  {cls}: {stats['mean_accuracy']:.2f}% ± {stats['std_accuracy']:.2f}%")
print()

print("="*60)
print("✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("="*60)
