#!/usr/bin/env python3
"""
TUTORIAL INTERACTIVO - Sistema de Clasificadores
Guía paso a paso para experimentar con K-NN y Mínima Distancia
Ejecutar: python3 tutorial.py
"""

from src.dataset import Dataset
from src.knn_classifier import KNNClassifier
from src.minimum_distance_classifier import MinimumDistanceClassifier


def pausa():
    """Pausa para que el usuario lea la información"""
    input("\n➜ Presiona Enter para continuar...")


def linea():
    """Imprime una línea separadora"""
    print("\n" + "="*70 + "\n")


def paso(numero, titulo):
    """Imprime un título de paso"""
    print(f"\n{'─'*70}")
    print(f"PASO {numero}: {titulo}")
    print(f"{'─'*70}\n")


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   TUTORIAL INTERACTIVO - CLASIFICADORES                     ║
║                     K-NN y MÍNIMA DISTANCIA                                 ║
║                                                                              ║
║  Aprenderás cómo usar el sistema completo en 5 pasos simples                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    pausa()
    
    # PASO 1: Crear Dataset
    paso(1, "CREAR UN DATASET")
    print("""
Un DATASET es un contenedor para tus datos de entrenamiento.
Necesitas especificar:
  • Dimensión de entrada: ¿Cuántos valores de entrada?
  • Dimensión de salida: ¿Cuántos valores de salida?

Ejemplo: Clasificador de Iris
  • Entrada: 4 (largo sépalo, ancho sépalo, largo pétalo, ancho pétalo)
  • Salida: 1 (tipo de iris: 0=Setosa, 1=Versicolor, 2=Virginica)
""")
    
    print("\n📊 Creando Dataset...")
    ds = Dataset(input_size=4, output_size=1)
    print(f"✓ Dataset creado: {ds}")
    
    pausa()
    
    # PASO 2: Cargar datos
    paso(2, "CARGAR DATOS DE ENTRENAMIENTO")
    print("""
Hay dos formas de agregar datos:

Opción A: Cargar desde archivo (RECOMENDADO)
  Archivo: data/training_data.txt
  Formato: entrada1,entrada2,... | salida
  
Opción B: Agregar manualmente
  Cada muestra se agrega una por una
""")
    
    print("\n📁 Cargando datos desde archivo...")
    ds.load_from_file('data/training_data.txt')
    print(f"✓ {ds}")
    
    pausa()
    
    # PASO 3: Ver los datos
    paso(3, "EXAMINAR LOS DATOS")
    print("Los datos cargados son (formato: entrada → salida):\n")
    
    samples = ds.get_samples()
    for i, (entrada, salida) in enumerate(samples[:5], 1):
        print(f"  Muestra {i}: {entrada} → {salida}")
    
    if len(samples) > 5:
        print(f"  ... y {len(samples) - 5} muestras más")
    
    pausa()
    
    # PASO 4: Entrenar Clasificadores
    paso(4, "ENTRENAR CLASIFICADORES")
    print("""
Ahora entrenaremos DOS clasificadores:

1️⃣  K-NN (K-Nearest Neighbors)
    • Memoriza todos los datos
    • Para predecir, busca los K puntos más cercanos
    • Promedia sus salidas
    
    Parámetros:
    - K: número de vecinos a considerar
    - Métrica: euclidiana o manhattan

2️⃣  Mínima Distancia
    • Calcula un prototipo (centroide) por clase
    • Para predecir, busca el prototipo más cercano
    • Retorna su clase
    
    Parámetros:
    - Métrica: euclidiana o manhattan
""")
    
    print("\n🤖 Entrenando K-NN con K=3 (euclidiana)...")
    knn = KNNClassifier(ds, k=3, distance_metric='euclidean')
    print(f"✓ {knn.get_info()}")
    
    print("\n🤖 Entrenando Mínima Distancia (euclidiana)...")
    md = MinimumDistanceClassifier(ds, distance_metric='euclidean')
    print(f"✓ {md.get_info()}")
    print(f"  Clases detectadas: {md.get_prototypes_count()}")
    
    pausa()
    
    # PASO 5: Realizar Predicciones
    paso(5, "HACER PREDICCIONES")
    print("""
Ahora vamos a usar los clasificadores para predecir.

Te mostraré 3 ejemplos:
1. Una Setosa típica
2. Una Versicolor típica
3. Una Virginica típica
""")
    
    ejemplos = [
        ([5.1, 3.5, 1.4, 0.2], "🌸 Setosa (pequeña)"),
        ([6.0, 2.7, 5.1, 1.6], "🌺 Versicolor (mediana)"),
        ([7.1, 3.0, 5.9, 2.1], "🌻 Virginica (grande)"),
    ]
    
    for entrada, etiqueta in ejemplos:
        print(f"\n{etiqueta}")
        print(f"Entrada: {entrada}")
        
        pred_knn = knn.predict(entrada)
        pred_md = md.predict(entrada)
        
        print(f"  K-NN predice:           {pred_knn[0]:.1f}")
        print(f"  Mínima Distancia predice: {pred_md[0]:.1f}")
    
    pausa()
    
    # PASO 6: Experimentar con Parámetros
    paso(6, "EXPERIMENTAR CON PARÁMETROS")
    print("""
Vamos a cambiar los parámetros y ver cómo cambian las predicciones.

Cambio 1: Aumentar K (de 3 a 5)
""")
    
    print("Aumentando K a 5...")
    knn.set_k(5)
    print(f"✓ {knn.get_info()}")
    
    entrada_test = [6.0, 2.7, 5.1, 1.6]
    pred = knn.predict(entrada_test)
    print(f"\nPredicción con K=5: {pred[0]:.2f}")
    
    print("\n" + "─"*70)
    print("Cambio 2: Cambiar métrica a Manhattan")
    
    knn.set_distance_metric('manhattan')
    print(f"✓ {knn.get_info()}")
    
    pred = knn.predict(entrada_test)
    print(f"\nPredicción con Manhattan: {pred[0]:.2f}")
    
    pausa()
    
    # PASO 7: Predicción Personalizada
    paso(7, "PREDICCIÓN PERSONALIZADA")
    print("""
Ahora puedes crear tus propios valores para predecir.

Recuerda:
  • Necesitas 4 valores separados por comas
  • Rango típico: 4-8 para cada medida
  • Ejemplo: 6.5,3.0,5.5,1.8
""")
    
    while True:
        entrada_usuario = input("\n➜ Ingresa 4 valores (o 'salir' para terminar): ")
        
        if entrada_usuario.lower() == 'salir':
            break
        
        try:
            valores = [float(x.strip()) for x in entrada_usuario.split(',')]
            
            if len(valores) != 4:
                print("✗ Error: Debes ingresar exactamente 4 valores")
                continue
            
            print(f"\nPrediciendo para: {valores}")
            
            # Resetear parámetros a valores por defecto
            knn.set_k(3)
            knn.set_distance_metric('euclidean')
            
            pred_knn = knn.predict(valores)
            pred_md = md.predict(valores)
            
            print(f"  K-NN (k=3, euclidiana):     {pred_knn[0]:.1f}")
            print(f"  Mínima Distancia (euclidiana): {pred_md[0]:.1f}")
            
        except ValueError:
            print("✗ Error: Ingresa números separados por comas")
    
    # RESUMEN FINAL
    linea()
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ✓ TUTORIAL COMPLETADO                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 LO QUE APRENDISTE:

  1. Crear un Dataset con dimensiones específicas
  2. Cargar datos desde archivos
  3. Entrenar dos clasificadores diferentes
  4. Hacer predicciones
  5. Cambiar parámetros (K, métrica)
  6. Comparar resultados

🎯 PRÓXIMOS PASOS:

  1. Experimenta con la interfaz interactiva:
     $ python3 main.py
  
  2. Carga tus propios datos:
     Crea: data/mis_datos.txt con formato:
     valor1,valor2,... | salida
  
  3. Prueba diferentes configuraciones:
     • Distintos valores de K
     • Diferentes métricas (euclidiana, manhattan)
     • Tus propios datos

💡 TIPS:

  • K pequeño (1-3): Menos suavizado, más sensible a ruido
  • K grande (5+): Más suavizado, menos detalles
  • Euclidiana: Mejor para espacios continuos
  • Manhattan: Mejor para grids o datos urbanos
  • Normaliza tus datos para mejores resultados

🔗 VER TAMBIÉN:

  • examples.py - 6 ejemplos completos
  • quick_start.py - Demostración rápida
  • main.py - Interfaz interactiva completa
  • README.md - Documentación completa

═══════════════════════════════════════════════════════════════════════════════

¡Gracias por usar el Sistema de Clasificadores!
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tutorial interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
