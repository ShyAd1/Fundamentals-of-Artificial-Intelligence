#!/usr/bin/env python3
"""
DEMOSTRACIÓN COMPLETA - Sistema de Clasificadores
Muestra un flujo completo de uso sin necesidad de entrada interactiva
Ejecutar: python3 demo_completa.py
"""

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier


def print_header(titulo):
    """Imprime encabezado"""
    print("\n" + "█"*80)
    print(f"  {titulo}")
    print("█"*80)


def print_section(numero, titulo):
    """Imprime sección"""
    print(f"\n{'─'*80}")
    print(f"  PASO {numero}: {titulo}")
    print(f"{'─'*80}\n")


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           DEMOSTRACIÓN COMPLETA - SISTEMA DE CLASIFICADORES               ║
║                    K-NN y MÍNIMA DISTANCIA                                ║
║                                                                            ║
║  Este script te muestra todo lo que puedes hacer con el sistema           ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    input("➜ Presiona Enter para comenzar...")
    
    # PASO 1: Crear Dataset
    print_section(1, "CREAR UN DATASET")
    print("¿Qué es un Dataset?")
    print("  • Un contenedor para datos de entrenamiento")
    print("  • Define la dimensión de entrada y salida")
    print("\nPara Iris usaremos:")
    print("  • Entrada: 4 dimensiones (medidas de la flor)")
    print("  • Salida: 1 dimensión (tipo de Iris)")
    
    print("\n📊 Creando Dataset...")
    ds = Dataset(input_size=4, output_size=1)
    print(f"✓ {ds}")
    
    input("\n➜ Presiona Enter para continuar...")
    
    # PASO 2: Cargar Datos
    print_section(2, "CARGAR DATOS DE ENTRENAMIENTO")
    print("Cargaremos 9 muestras de Iris desde archivo:")
    print("  Archivo: data/training_data.txt")
    
    print("\n📁 Leyendo archivo...")
    ds.load_from_file('data/training_data.txt')
    print(f"✓ Dataset cargado con éxito")
    print(f"✓ {ds}")
    
    input("\n➜ Presiona Enter para ver los datos...")
    
    # PASO 3: Examinar Datos
    print_section(3, "EXAMINAR LOS DATOS")
    print("Primeras 5 muestras (entrada → salida):\n")
    
    samples = ds.get_samples()
    for i, (entrada, salida) in enumerate(samples[:5], 1):
        entrada_str = ', '.join(f'{x:.1f}' for x in entrada)
        print(f"  Muestra {i}: [{entrada_str}] → {int(salida[0])}")
    
    if len(samples) > 5:
        print(f"  ... (y {len(samples) - 5} muestras más)")
    
    print("\n📊 Estadísticas:")
    print(f"  • Total de muestras: {ds.get_size()}")
    print(f"  • Dimensión entrada: {ds.input_size}")
    print(f"  • Dimensión salida: {ds.output_size}")
    
    input("\n➜ Presiona Enter para entrenar clasificadores...")
    
    # PASO 4: Entrenar Clasificadores
    print_section(4, "ENTRENAR CLASIFICADORES")
    print("Vamos a entrenar dos clasificadores diferentes:\n")
    
    print("1️⃣  CLASIFICADOR K-NN")
    print("   • Mantiene en memoria todos los datos de entrenamiento")
    print("   • Para predecir: busca los K puntos más cercanos")
    print("   • Promedia sus valores de salida")
    print("   • Parámetros: K=3, Métrica=Euclidiana")
    
    print("\n   🤖 Entrenando...")
    knn = KNNClassifier(ds, k=3, distance_metric='euclidean')
    print(f"   ✓ {knn.get_info()}")
    
    print("\n2️⃣  CLASIFICADOR MÍNIMA DISTANCIA")
    print("   • Calcula un prototipo (centroide) por clase")
    print("   • Para predecir: busca el prototipo más cercano")
    print("   • Retorna la clase del prototipo más cercano")
    print("   • Parámetro: Métrica=Euclidiana")
    
    print("\n   🤖 Entrenando...")
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    print(f"   ✓ {md.get_info()}")
    print(f"   ✓ Clases detectadas automáticamente: {md.get_prototypes_count()}")
    
    input("\n➜ Presiona Enter para ver predicciones...")
    
    # PASO 5: Predicciones Básicas
    print_section(5, "REALIZAR PREDICCIONES")
    print("Ahora usaremos los clasificadores para hacer predicciones.\n")
    
    test_cases = [
        ([5.1, 3.5, 1.4, 0.2], "🌸 SETOSA (pequeña)"),
        ([6.0, 2.7, 5.1, 1.6], "🌺 VERSICOLOR (mediana)"),
        ([7.1, 3.0, 5.9, 2.1], "🌻 VIRGINICA (grande)"),
    ]
    
    for entrada, etiqueta in test_cases:
        entrada_str = ', '.join(f'{x:.1f}' for x in entrada)
        print(f"\n{etiqueta}")
        print(f"Entrada: [{entrada_str}]")
        
        pred_knn = knn.predict(entrada)
        pred_md = md.predict(entrada)
        
        print(f"├─ K-NN (k=3):             Clase {int(pred_knn[0])}")
        print(f"└─ Mínima Distancia:       Clase {int(pred_md[0])}")
    
    input("\n➜ Presiona Enter para experimentar con parámetros...")
    
    # PASO 6: Modificar Parámetros
    print_section(6, "EXPERIMENTAR CON PARÁMETROS")
    print("Veamos cómo cambian las predicciones al modificar parámetros.\n")
    
    entrada_test = [6.0, 2.7, 5.1, 1.6]
    print(f"Usando punto de prueba: [{', '.join(f'{x:.1f}' for x in entrada_test)}]\n")
    
    configs = [
        (1, 'euclidean', 'K=1, Euclidiana'),
        (3, 'euclidean', 'K=3, Euclidiana'),
        (5, 'euclidean', 'K=5, Euclidiana'),
        (3, 'manhattan', 'K=3, Manhattan'),
    ]
    
    print("Comparación de configuraciones:\n")
    for k, metric, label in configs:
        knn.set_k(k)
        knn.set_distance_metric(metric)
        pred = knn.predict(entrada_test)
        print(f"  {label:25s} → Predicción: {int(pred[0])}")
    
    # Resetear a valores por defecto
    knn.set_k(3)
    knn.set_distance_metric('euclidean')
    
    input("\n➜ Presiona Enter para predicciones múltiples...")
    
    # PASO 7: Predicciones por lotes
    print_section(7, "PREDICCIONES POR LOTES")
    print("Podemos hacer varias predicciones a la vez.\n")
    
    conjunto_test = [
        [4.9, 3.0, 1.4, 0.2],
        [5.5, 2.6, 4.4, 1.2],
        [7.2, 3.0, 5.8, 1.6],
    ]
    
    print("Realizando 3 predicciones simultáneamente:\n")
    
    predicciones_knn = knn.predict_batch(conjunto_test)
    predicciones_md = md.predict_batch(conjunto_test)
    
    for i, (entrada, pred_knn, pred_md) in enumerate(
        zip(conjunto_test, predicciones_knn, predicciones_md), 1
    ):
        entrada_str = ', '.join(f'{x:.1f}' for x in entrada)
        print(f"Punto {i}: [{entrada_str}]")
        print(f"  K-NN: {int(pred_knn[0])}  |  MD: {int(pred_md[0])}")
    
    input("\n➜ Presiona Enter para ver comparación detallada...")
    
    # PASO 8: Comparación Detallada
    print_section(8, "COMPARACIÓN DE CLASIFICADORES")
    print("Ahora compararemos ambos clasificadores con distintas métricas.\n")
    
    punto_prueba = [6.0, 2.7, 5.1, 1.6]
    
    print(f"Punto de prueba: [{', '.join(f'{x:.1f}' for x in punto_prueba)}]\n")
    
    print("K-NN con diferentes K:")
    for k_val in [1, 3, 5, 7]:
        knn.set_k(k_val)
        pred = knn.predict(punto_prueba)
        print(f"  K={k_val}: {int(pred[0])}")
    
    print("\nK-NN con diferentes métricas (K=3):")
    knn.set_k(3)
    for metric in ['euclidean', 'manhattan']:
        knn.set_distance_metric(metric)
        pred = knn.predict(punto_prueba)
        metrica_nombre = 'Euclidiana' if metric == 'euclidean' else 'Manhattan'
        print(f"  {metrica_nombre}: {int(pred[0])}")
    
    print("\nMínima Distancia con diferentes métricas:")
    for metric in ['euclidean', 'manhattan']:
        md.set_distance_metric(metric)
        pred = md.predict(punto_prueba)
        metrica_nombre = 'Euclidiana' if metric == 'euclidean' else 'Manhattan'
        print(f"  {metrica_nombre}: {int(pred[0])}")
    
    input("\n➜ Presiona Enter para continuar...")
    
    # Resumen Final
    print_header("✓ DEMOSTRACIÓN COMPLETA TERMINADA")
    
    print("""
📚 RESUMEN DE LO QUE VISTE:

  1. ✓ Crear un Dataset con dimensiones específicas
  2. ✓ Cargar datos desde archivo (9 muestras de Iris)
  3. ✓ Entrenar dos clasificadores distintos
  4. ✓ Hacer predicciones individuales
  5. ✓ Cambiar parámetros (K, métrica)
  6. ✓ Hacer predicciones por lotes
  7. ✓ Comparar diferentes configuraciones

🎯 AHORA ES TU TURNO:

Tienes varias opciones para experimentar:

  1. INTERFAZ INTERACTIVA (RECOMENDADO):
     $ python3 main.py
     
     Menú completo donde puedes:
     ├─ Configurar nuevos datasets
     ├─ Cargar tus propios datos
     ├─ Entrenar clasificadores
     ├─ Hacer predicciones
     ├─ Ajustar parámetros
     └─ Ver estadísticas

  2. VER MÁS EJEMPLOS:
     $ python3 examples.py
     
     6 ejemplos diferentes incluyendo:
     ├─ Clasificación simple
     ├─ Dataset Iris completo
     ├─ Métricas de distancia
     ├─ Guardar/cargar datos
     ├─ Predicciones por lotes
     └─ Comparación de clasificadores

  3. TUTORIAL INTERACTIVO (CON ENTRADA):
     $ python3 tutorial.py
     
     Guía paso a paso con predicciones personalizadas

  4. PRUEBAS DEL SISTEMA:
     $ python3 tests/test_system.py
     
     Valida que todo funciona correctamente

💡 TIPS PARA EXPERIMENTAR:

  • Crea tus propios datos en: data/mi_archivo.txt
  • Formato: valor1,valor2,... | salida
  • Prueba con K pequeño (1) vs grande (7+)
  • Compara Euclidiana vs Manhattan
  • Normaliza tus datos para mejores resultados

📖 DOCUMENTACIÓN:

  • README.md - Guía general
  • RESUMEN.txt - Características técnicas
  • INDICE.txt - Descripción de archivos
  • Docstrings en el código

═══════════════════════════════════════════════════════════════════════════════

¡Ahora es momento de que experimentes por tu cuenta!
Empieza con: python3 main.py
""")


if __name__ == "__main__":
    try:
        main()
        print("\n✓ ¡Hasta luego!\n")
    except KeyboardInterrupt:
        print("\n\n❌ Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
