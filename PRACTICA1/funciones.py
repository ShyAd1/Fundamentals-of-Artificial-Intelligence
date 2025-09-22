def leer_archivo_csv(nombre_archivo):
    """
    Lee un archivo CSV y devuelve su contenido como una lista de listas.

    :param nombre_archivo: Nombre del archivo CSV a leer.
    :return: Lista de listas que representa las filas y columnas del archivo CSV.
    """
    contenido = []
    with open(nombre_archivo, "r") as archivo:
        for linea in archivo:
            fila = linea.strip().split(",")
            contenido.append(fila)
    return contenido


def guardar_archivo_csv(nombre_archivo, datos):
    """
    Guarda una lista de listas en un archivo CSV.

    :param nombre_archivo: Nombre del archivo CSV donde se guardarán los datos.
    :param datos: Lista de listas que representa las filas y columnas a guardar.
    """
    with open(nombre_archivo, "w") as archivo:
        for fila in datos:
            linea = ",".join(fila)
            archivo.write(linea + "\n")


def modificar_dato(datos, fila, columna, nuevo_valor):
    """
    Modifica un dato específico en una lista de listas.

    :param datos: Lista de listas que representa las filas y columnas.
    :param fila: Índice de la fila donde se encuentra el dato a modificar.
    :param columna: Índice de la columna donde se encuentra el dato a modificar.
    :param nuevo_valor: Nuevo valor que se asignará al dato especificado.
    """
    if 0 <= fila < len(datos) and 0 <= columna < len(datos[0]):
        datos[fila][columna] = nuevo_valor
    else:
        raise IndexError("Índice de fila o columna fuera de rango.")
