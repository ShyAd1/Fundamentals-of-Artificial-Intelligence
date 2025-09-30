import pygame
import funciones
import interfaces

# Paletas y constantes (asegurar antes de funciones)
COLOR_PARED = (74, 74, 74)
COLOR_CAMINO = (255, 255, 255)
COLORES_TERRENO = {
    0: (110, 110, 110),  # Montaña
    1: (222, 180, 150),  # Tierra
    2: (70, 120, 200),  # Agua
    3: (230, 215, 120),  # Arena
    4: (60, 140, 60),  # Bosque
}
VALORES_ESPECIALES = ["V", "O", "I", "F", "X"]
SIMBOLOS_DESCRIP = {
    "I": "Inicio",
    "F": "Final",
    "V": "Visitado",
    "O": "Decision",
    "X": "Actual",
}
cell_size = 40

# Eliminamos lectura inicial directa para permitir carga dinámica
try:
    datos
except NameError:
    datos = []
try:
    recorridos
except NameError:
    recorridos = []

try:
    recorridos_inicial
except NameError:
    recorridos_inicial = None
info_celda_click = ""

modo_mapa = globals().get("modo_mapa", None)  # None, 'laberinto', 'terreno'
modificar_mapa = globals().get("modificar_mapa", False)
modo_valores = globals().get("modo_valores", False)

personaje_seleccionado = globals().get("personaje_seleccionado", None)
seleccionando_personaje = False
costo_acumulado = 0
# Set de celdas descubiertas por modo (solo indices (fila,col))
descubiertas_laberinto = set()
descubiertas_terreno = set()

personajes = ["Humano", "Mono", "Pulpo", "Sasquatch"]

# Nueva variable global para marcas de terreno
marcas_terreno = globals().get("marcas_terreno", [])

# Nueva variable para mostrar celdas cubiertas
mostrar_cubierto = globals().get("mostrar_cubierto", False)


def reset_estado_descubrimiento():
    global descubiertas_laberinto, descubiertas_terreno, mostrar_cubierto
    descubiertas_laberinto.clear()
    descubiertas_terreno.clear()
    mostrar_cubierto = True
    globals()["mostrar_cubierto"] = mostrar_cubierto


def cargar_laberinto():
    global datos, recorridos, modo_mapa, copy_recorridos, costo_acumulado, recorridos_inicial
    datos = funciones.leer_archivo_csv("PRACTICA1/laberinto.csv")
    recorridos = funciones.leer_archivo_csv("PRACTICA1/recorridos.csv")
    if recorridos_inicial is None:
        recorridos_inicial = [fila[:] for fila in recorridos]
    copy_recorridos = [fila[:] for fila in recorridos]
    modo_mapa = "laberinto"
    costo_acumulado = 0
    globals()["costo_acumulado"] = costo_acumulado
    reset_estado_descubrimiento()
    globals()["modo_mapa"] = modo_mapa


def cargar_terreno():
    global datos, recorridos, modo_mapa, marcas_terreno, costo_acumulado
    datos = funciones.leer_archivo_csv("PRACTICA1/terreno.csv")
    recorridos = []
    marcas_terreno = [["" for _ in fila[:15]] for fila in datos[:15]]
    modo_mapa = "terreno"
    costo_acumulado = 0
    globals()["costo_acumulado"] = costo_acumulado
    reset_estado_descubrimiento()
    globals()["modo_mapa"] = modo_mapa
    globals()["marcas_terreno"] = marcas_terreno


# Cargar costos de personajes para terreno
costos_terreno = {}
try:
    filas_costos = funciones.leer_archivo_csv("PRACTICA1/costo_personajes.csv")
    # Primera fila encabezados: Significado,Humano,Mono,Pulpo,Sasquatch
    encabezados = filas_costos[0][1:]
    # Mapear significado -> índice terreno (0..4) segun orden definido
    # Asumimos orden Montaña(0), Tierra(1), Agua(2), Arena(3), Bosque(4)
    significado_a_codigo = {
        "Montaña": 0,
        "Tierra": 1,
        "Agua": 2,
        "Arena": 3,
        "Bosque": 4,
    }
    # Inicializar diccionario por personaje
    for personaje in encabezados:
        costos_terreno[personaje] = {}
    for fila in filas_costos[1:]:
        if not fila or len(fila) < 2:
            continue
        sig = fila[0]
        if sig not in significado_a_codigo:
            continue
        codigo = significado_a_codigo[sig]
        for idx, personaje in enumerate(encabezados):
            valor = fila[idx + 1]
            if valor and valor.lower() != "nan":
                try:
                    costos_terreno[personaje][codigo] = int(valor)
                except ValueError:
                    pass
except FileNotFoundError:
    costos_terreno = {}


# Función para determinar nodo de decisión (>2 caminos y un vecino visitado)
def es_decision(i, j):
    if not datos or not recorridos:
        return False
    if i < 0 or j < 0 or i >= 15 or j >= 15:
        return False
    if datos[i][j] != "1":
        return False
    caminos = 0
    vecino_visitado = False
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < 15 and 0 <= nj < 15:
            if datos[ni][nj] == "1":
                caminos += 1
                celda = (
                    recorridos[ni][nj]
                    if recorridos and ni < len(recorridos) and nj < len(recorridos[0])
                    else ""
                )
                if celda and "V" in celda:
                    vecino_visitado = True
    return caminos > 2 and vecino_visitado


# Helpers de movimiento (asegurar definidos antes de uso)
def obtener_pos_actual_laberinto():
    if not recorridos:
        return None
    # Prioridad X
    for i in range(min(15, len(recorridos))):
        for j in range(min(15, len(recorridos[0]))):
            val = recorridos[i][j]
            if val and "X" in val:
                return (i, j)
    # Luego I
    for i in range(min(15, len(recorridos))):
        for j in range(min(15, len(recorridos[0]))):
            val = recorridos[i][j]
            if val and "I" in val:
                return (i, j)
    return None


def descubrir_alrededor(conjunto, fila, col):
    for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = fila + di, col + dj
        if 0 <= ni < 15 and 0 <= nj < 15:
            conjunto.add((ni, nj))


def abrir_menu_personaje(
    screen, panel_x, btn_personaje_rect, btn_w, personajes, modo_mapa
):
    global personaje_seleccionado
    menu_x = panel_x - 10
    menu_y = btn_personaje_rect.y + btn_personaje_rect.height + 10
    menu_w = btn_w
    menu_h = len(personajes) * 38 + 20
    mf = pygame.font.Font(None, 26)
    abierto = True
    clock = pygame.time.Clock()
    while abierto:
        # Dibujar solo el menú sobre la pantalla existente (no limpiar fondo para mantener contexto)
        pygame.draw.rect(
            screen, (40, 40, 40), (menu_x, menu_y, menu_w, menu_h), border_radius=8
        )
        for idx, p in enumerate(personajes):
            r = pygame.Rect(menu_x + 10, menu_y + 10 + idx * 38, menu_w - 20, 30)
            pygame.draw.rect(screen, (70, 130, 180), r, border_radius=6)
            t = mf.render(p, True, (255, 255, 255))
            screen.blit(t, (r.x + 8, r.y + 4))
        pygame.display.update(pygame.Rect(menu_x, menu_y, menu_w, menu_h))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                abierto = False
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                abierto = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                # Click fuera cierra
                if not pygame.Rect(menu_x, menu_y, menu_w, menu_h).collidepoint(mx, my):
                    abierto = False
                    break
                for idx, p in enumerate(personajes):
                    r = pygame.Rect(
                        menu_x + 10, menu_y + 10 + idx * 38, menu_w - 20, 30
                    )
                    if r.collidepoint(mx, my):
                        personaje_seleccionado = p
                        # Inicializar posición según modo
                        if modo_mapa == "laberinto":
                            pos_i = obtener_pos_actual_laberinto()
                            if not pos_i and datos:
                                for i in range(min(15, len(datos))):
                                    placed = False
                                    for j in range(min(15, len(datos[0]))):
                                        if datos[i][j] == "1":
                                            if (
                                                recorridos
                                                and len(recorridos) > i
                                                and len(recorridos[0]) > j
                                            ):
                                                recorridos[i][j] = "IX"
                                                funciones.guardar_archivo_csv(
                                                    "PRACTICA1/recorridos.csv",
                                                    recorridos,
                                                )
                                                descubrir_alrededor(
                                                    descubiertas_laberinto, i, j
                                                )
                                                placed = True
                                                break
                                    if placed:
                                        break
                        elif modo_mapa == "terreno":
                            # Buscar I si existe
                            start_found = False
                            for i_r in range(len(marcas_terreno)):
                                for j_r in range(len(marcas_terreno[0])):
                                    if "I" in (marcas_terreno[i_r][j_r] or ""):
                                        globals()["pos_terreno"] = (i_r, j_r)
                                        descubrir_alrededor(
                                            descubiertas_terreno, i_r, j_r
                                        )
                                        start_found = True
                                        break
                                if start_found:
                                    break
                            if not start_found:
                                globals()["pos_terreno"] = (0, 0)
                                descubrir_alrededor(descubiertas_terreno, 0, 0)
                        abierto = False
                        break
        clock.tick(30)


# Funciones de dibujo
def dibujar_grid_base(surface):
    header_font = pygame.font.Font(None, 24)
    columnas = [chr(ord("A") + i) for i in range(15)]
    # Encabezados columnas
    for j, col in enumerate(columnas):
        txt = header_font.render(col, True, (255, 255, 255))
        x = j * cell_size + cell_size + (cell_size - txt.get_width()) // 2
        y = (cell_size - txt.get_height()) // 2
        surface.blit(txt, (x, y))
    # Encabezados filas
    for i in range(15):
        txt = header_font.render(str(i + 1), True, (255, 255, 255))
        x = (cell_size - txt.get_width()) // 2
        y = i * cell_size + cell_size + (cell_size - txt.get_height()) // 2
        surface.blit(txt, (x, y))


def dibujar_mapa_laberinto(surface, datos_l, recorridos_l):
    if not datos_l:
        return
    for i, fila in enumerate(datos_l):
        if i >= 15:
            break
        for j, valor in enumerate(fila):
            if j >= 15:
                break
            if mostrar_cubierto and (i, j) not in descubiertas_laberinto:
                # Celda no revelada
                x = j * cell_size + cell_size
                y = i * cell_size + cell_size
                pygame.draw.rect(surface, (15, 15, 25), (x, y, cell_size, cell_size))
                continue
            x = j * cell_size + cell_size
            y = i * cell_size + cell_size
            color = COLOR_CAMINO if valor == "1" else COLOR_PARED
            pygame.draw.rect(surface, color, (x, y, cell_size, cell_size))
            if valor == "1" and recorridos_l:
                if 0 <= i < len(recorridos_l) and 0 <= j < len(recorridos_l[0]):
                    val = recorridos_l[i][j]
                    if val and any(le in VALORES_ESPECIALES for le in val):
                        letra_font = pygame.font.Font(None, 20)
                        x_offset = 0
                        for letra in val:
                            if letra in VALORES_ESPECIALES:
                                letra_color = (
                                    (150, 0, 0)
                                    if letra == "I"
                                    else (
                                        (0, 0, 0)
                                        if letra == "F"
                                        else (
                                            (70, 130, 180)
                                            if letra == "O"
                                            else (
                                                (110, 0, 150)
                                                if letra == "X"
                                                else (0, 100, 20)
                                            )
                                        )
                                    )
                                )
                                letra_surface = letra_font.render(
                                    letra, True, letra_color
                                )
                                surface.blit(letra_surface, (x + 5 + x_offset, y + 12))
                                x_offset += letra_surface.get_width() + 2
    # Líneas
    for x in range(0, cell_size * 16, cell_size):
        pygame.draw.line(surface, (80, 80, 80), (x, 0), (x, cell_size * 16))
    for y in range(0, cell_size * 16, cell_size):
        pygame.draw.line(surface, (80, 80, 80), (0, y), (cell_size * 16, y))


def dibujar_mapa_terreno(surface, datos_t):
    if not datos_t:
        return
    for i, fila in enumerate(datos_t):
        if i >= 15:
            break
        for j, valor in enumerate(fila):
            if j >= 15:
                break
            if mostrar_cubierto and (i, j) not in descubiertas_terreno:
                x = j * cell_size + cell_size
                y = i * cell_size + cell_size
                pygame.draw.rect(surface, (10, 10, 20), (x, y, cell_size, cell_size))
                continue
            try:
                tipo = int(valor)
            except ValueError:
                continue
            color = COLORES_TERRENO.get(tipo, (30, 30, 30))
            x = j * cell_size + cell_size
            y = i * cell_size + cell_size
            pygame.draw.rect(surface, color, (x, y, cell_size, cell_size))
            if (
                marcas_terreno
                and 0 <= i < len(marcas_terreno)
                and 0 <= j < len(marcas_terreno[0])
            ):
                val = marcas_terreno[i][j]
                if val:
                    letra_font = pygame.font.Font(None, 20)
                    x_offset = 0
                    for letra in val:
                        if letra in VALORES_ESPECIALES:
                            letra_color = (
                                (150, 0, 0)
                                if letra == "I"
                                else (
                                    (0, 0, 0)
                                    if letra == "F"
                                    else (
                                        (70, 130, 180)
                                        if letra == "O"
                                        else (
                                            (110, 0, 150)
                                            if letra == "X"
                                            else (0, 100, 20)
                                        )
                                    )
                                )
                            )
                            letra_surface = letra_font.render(letra, True, letra_color)
                            surface.blit(letra_surface, (x + 5 + x_offset, y + 12))
                            x_offset += letra_surface.get_width() + 2
    # Líneas
    for x in range(0, cell_size * 16, cell_size):
        pygame.draw.line(surface, (80, 80, 80), (x, 0), (x, cell_size * 16))
    for y in range(0, cell_size * 16, cell_size):
        pygame.draw.line(surface, (80, 80, 80), (0, y), (cell_size * 16, y))


# Inicializar Pygame solo si no estaba
pygame.init()
screen_width, screen_height = 1000, 640
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Laberinto / Terreno Interactivo")

# Botones adicionales se integrarán dentro del bucle principal; aseguramos variables necesarias
costos_personaje = {
    "Humano": 1,
    "Mono": 2,
    "Pulpo": 3,
    "Sasquatch": 4,
}

running = True
while running:
    screen_width, screen_height = screen.get_size()
    eventos = pygame.event.get()
    for event in eventos:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if personaje_seleccionado:
                # Movimiento
                di, dj = 0, 0
                if event.key in (pygame.K_UP, pygame.K_w):
                    di = -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    di = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dj = -1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dj = 1
                if di != 0 or dj != 0:
                    if modo_mapa == "laberinto" and recorridos:
                        pos = obtener_pos_actual_laberinto()
                        if pos:
                            ni = pos[0] + di
                            nj = pos[1] + dj
                            if 0 <= ni < 15 and 0 <= nj < 15 and datos[ni][nj] == "1":
                                globals()["costo_acumulado"] = (
                                    globals().get("costo_acumulado", 0) + 1
                                )
                                actual = recorridos[ni][nj]
                                # Marcar visita
                                if (
                                    "I" not in actual
                                    and "F" not in actual
                                    and "X" not in actual
                                ):
                                    if "V" not in actual:
                                        recorridos[ni][nj] = (actual or "") + "V"
                                # Quitar X anterior
                                for i_r in range(min(15, len(recorridos))):
                                    for j_r in range(min(15, len(recorridos[0]))):
                                        if (
                                            recorridos[i_r][j_r]
                                            and "X" in recorridos[i_r][j_r]
                                        ):
                                            recorridos[i_r][j_r] = recorridos[i_r][
                                                j_r
                                            ].replace("X", "")
                                if "X" not in recorridos[ni][nj]:
                                    recorridos[ni][nj] = (
                                        recorridos[ni][nj] or ""
                                    ) + "X"
                                # Auto-decision O
                                if es_decision(ni, nj):
                                    if "O" not in recorridos[ni][nj]:
                                        recorridos[ni][nj] += "O"
                                # Normalizar orden
                                orden = {
                                    c: i
                                    for i, c in enumerate(["I", "F", "V", "O", "X"])
                                }
                                for i_r in range(min(15, len(recorridos))):
                                    for j_r in range(min(15, len(recorridos[0]))):
                                        if recorridos[i_r][j_r]:
                                            sorted_val = "".join(
                                                sorted(
                                                    [
                                                        c
                                                        for c in recorridos[i_r][j_r]
                                                        if c in orden
                                                    ],
                                                    key=lambda c: orden[c],
                                                )
                                            )
                                            recorridos[i_r][j_r] = sorted_val
                                funciones.guardar_archivo_csv(
                                    "PRACTICA1/recorridos.csv", recorridos
                                )
                                descubrir_alrededor(descubiertas_laberinto, ni, nj)
                                # Si llego a F reset
                                if "F" in recorridos[ni][nj]:
                                    # Restaurar estado inicial
                                    for i_r in range(len(recorridos)):
                                        for j_r in range(len(recorridos[0])):
                                            recorridos[i_r][j_r] = copy_recorridos[i_r][
                                                j_r
                                            ]
                                    funciones.guardar_archivo_csv(
                                        "PRACTICA1/recorridos.csv", recorridos
                                    )
                                    globals()["costo_acumulado"] = 0
                                    reset_estado_descubrimiento()
                                    # Reposicionar X en I
                                    for i_r in range(min(15, len(recorridos))):
                                        for j_r in range(min(15, len(recorridos[0]))):
                                            if (
                                                recorridos[i_r][j_r]
                                                and "I" in recorridos[i_r][j_r]
                                            ):
                                                if "X" not in recorridos[i_r][j_r]:
                                                    recorridos[i_r][j_r] += "X"
                                                funciones.guardar_archivo_csv(
                                                    "PRACTICA1/recorridos.csv",
                                                    recorridos,
                                                )
                                                descubrir_alrededor(
                                                    descubiertas_laberinto, i_r, j_r
                                                )
                                                break
                                        else:
                                            continue
                                        break
                    elif modo_mapa == "terreno":
                        pos_t = globals().get("pos_terreno", None)
                        if pos_t:
                            ni = pos_t[0] + di
                            nj = pos_t[1] + dj
                            if 0 <= ni < 15 and 0 <= nj < 15:
                                try:
                                    tipo = int(datos[ni][nj])
                                except:
                                    tipo = None
                                if (
                                    tipo is not None
                                    and personaje_seleccionado in costos_terreno
                                    and tipo in costos_terreno[personaje_seleccionado]
                                ):
                                    globals()["pos_terreno"] = (ni, nj)
                                    globals()["costo_acumulado"] = (
                                        globals().get("costo_acumulado", 0)
                                        + costos_terreno[personaje_seleccionado][tipo]
                                    )
                                    descubrir_alrededor(descubiertas_terreno, ni, nj)
                                    # Reset si llega a F
                                    if marcas_terreno and "F" in (
                                        marcas_terreno[ni][nj] or ""
                                    ):
                                        globals()["costo_acumulado"] = 0
                                        reset_estado_descubrimiento()
                                        # Reposicionar en I si existe
                                        start_found = False
                                        for i_r in range(len(marcas_terreno)):
                                            for j_r in range(len(marcas_terreno[0])):
                                                if "I" in marcas_terreno[i_r][j_r]:
                                                    globals()["pos_terreno"] = (
                                                        i_r,
                                                        j_r,
                                                    )
                                                    descubrir_alrededor(
                                                        descubiertas_terreno, i_r, j_r
                                                    )
                                                    start_found = True
                                                    break
                                            if start_found:
                                                break
                                        if not start_found:
                                            globals()["pos_terreno"] = (0, 0)
                                            descubrir_alrededor(
                                                descubiertas_terreno, 0, 0
                                            )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if "btn_cover_rect" in globals() and btn_cover_rect.collidepoint(x, y):
                mostrar_cubierto = not mostrar_cubierto
                globals()["mostrar_cubierto"] = mostrar_cubierto
                continue
            # Detectar clicks en botones de carga
            if "btn_laberinto_rect" in globals() and btn_laberinto_rect.collidepoint(
                x, y
            ):
                cargar_laberinto()
                # Restaurar a snapshot inicial (evitar acumulación)
                if recorridos_inicial is not None:
                    for i_r in range(len(recorridos)):
                        for j_r in range(len(recorridos[0])):
                            recorridos[i_r][j_r] = recorridos_inicial[i_r][j_r]
                    funciones.guardar_archivo_csv(
                        "PRACTICA1/recorridos.csv", recorridos
                    )
                modo_valores = False
                globals()["modo_valores"] = modo_valores
            elif "btn_terreno_rect" in globals() and btn_terreno_rect.collidepoint(
                x, y
            ):
                cargar_terreno()
                modo_valores = False
                globals()["modo_valores"] = modo_valores
            elif "btn_personaje_rect" in globals() and btn_personaje_rect.collidepoint(
                x, y
            ):
                # Abrir menú modal y luego continuar sin propagar el clic
                abrir_menu_personaje(
                    screen, panel_x, btn_personaje_rect, btn_w, personajes, modo_mapa
                )
            elif "btn_modificar_rect" in globals() and btn_modificar_rect.collidepoint(
                x, y
            ):
                modificar_mapa = not modificar_mapa
                if modificar_mapa:
                    modo_valores = False
                globals()["modificar_mapa"] = modificar_mapa
                globals()["modo_valores"] = modo_valores
            elif (
                "btn_valores_rect" in globals()
                and modo_mapa == "laberinto"
                and btn_valores_rect.collidepoint(x, y)
            ):
                modo_valores = not modo_valores
                if modo_valores:
                    modificar_mapa = False
                globals()["modo_valores"] = modo_valores
                globals()["modificar_mapa"] = modificar_mapa
            # Nueva condición para botón valores en terreno
            elif "btn_valores_rect" in globals() and btn_valores_rect.collidepoint(
                x, y
            ):
                modo_valores = not modo_valores
                if modo_valores:
                    modificar_mapa = False
                globals()["modo_valores"] = modo_valores
                globals()["modificar_mapa"] = modificar_mapa
            else:
                # Clic en grid (excluye panel derecho y encabezados)
                if (
                    x >= cell_size
                    and y >= cell_size
                    and x < cell_size * 16
                    and y < cell_size * 16
                ):
                    col = (x - cell_size) // cell_size
                    fila = (y - cell_size) // cell_size
                    if 0 <= fila < 15 and 0 <= col < 15 and datos:
                        # Info contextual clic
                        if modo_mapa == "laberinto":
                            tipo = "Camino" if datos[fila][col] == "1" else "Pared"
                            simb = ""
                            if (
                                datos[fila][col] == "1"
                                and recorridos
                                and 0 <= fila < len(recorridos)
                                and 0 <= col < len(recorridos[0])
                            ):
                                raw = recorridos[fila][col] or ""
                                partes = []
                                for c in raw:
                                    if (
                                        c in SIMBOLOS_DESCRIP
                                        and SIMBOLOS_DESCRIP[c] not in partes
                                    ):
                                        partes.append(SIMBOLOS_DESCRIP[c])
                                if partes:
                                    simb = " (" + ",".join(partes) + ")"
                            info_celda_click = (
                                f"[{fila+1},{chr(ord('A')+col)}] {tipo}{simb}"
                            )
                        else:
                            try:
                                t = int(datos[fila][col])
                            except:
                                t = None
                            nombres = {
                                0: "Montaña",
                                1: "Tierra",
                                2: "Agua",
                                3: "Arena",
                                4: "Bosque",
                            }
                            base = nombres.get(t, "?") if t is not None else "?"
                            raw = ""
                            if (
                                marcas_terreno
                                and 0 <= fila < len(marcas_terreno)
                                and 0 <= col < len(marcas_terreno[0])
                            ):
                                raw = marcas_terreno[fila][col] or ""
                            partes = []
                            for c in raw:
                                if (
                                    c in SIMBOLOS_DESCRIP
                                    and SIMBOLOS_DESCRIP[c] not in partes
                                ):
                                    partes.append(SIMBOLOS_DESCRIP[c])
                            simb = " (" + ",".join(partes) + ")" if partes else ""
                            info_celda_click = (
                                f"[{fila+1},{chr(ord('A')+col)}] {base}{simb}"
                            )
                        globals()["info_celda_click"] = info_celda_click
                        # ...existing code continues...
                    if 0 <= fila < 15 and 0 <= col < 15 and datos:
                        if modificar_mapa:
                            if modo_mapa == "laberinto":
                                # Toggle 0/1
                                valor_actual = datos[fila][col]
                                nuevo = "0" if valor_actual == "1" else "1"
                                datos[fila][col] = nuevo
                                funciones.guardar_archivo_csv(
                                    "PRACTICA1/laberinto.csv", datos
                                )
                                # sincronizar recorridos
                                if recorridos:
                                    if nuevo == "1":
                                        recorridos[fila][col] = ""
                                    else:
                                        recorridos[fila][col] = "Pared"
                                    funciones.guardar_archivo_csv(
                                        "PRACTICA1/recorridos.csv", recorridos
                                    )
                            elif modo_mapa == "terreno":
                                # Menú emergente selección 0..4
                                seleccionando = True
                                opciones = [
                                    (0, "Montaña"),
                                    (1, "Tierra"),
                                    (2, "Agua"),
                                    (3, "Arena"),
                                    (4, "Bosque"),
                                ]
                                menu_w = 180
                                menu_h = len(opciones) * 40 + 20
                                menu_x = min(x + 10, cell_size * 16 - menu_w - 5)
                                menu_y = min(y + 10, cell_size * 16 - menu_h - 5)
                                while seleccionando:
                                    pygame.draw.rect(
                                        screen,
                                        (30, 30, 30),
                                        (menu_x, menu_y, menu_w, menu_h),
                                        border_radius=8,
                                    )
                                    mf = pygame.font.Font(None, 24)
                                    for idx, (cod, nombre) in enumerate(opciones):
                                        r = pygame.Rect(
                                            menu_x + 10,
                                            menu_y + 10 + idx * 40,
                                            menu_w - 20,
                                            32,
                                        )
                                        color_btn = (
                                            (90, 90, 90)
                                            if str(cod) == datos[fila][col]
                                            else (70, 130, 180)
                                        )
                                        pygame.draw.rect(
                                            screen, color_btn, r, border_radius=6
                                        )
                                        t = mf.render(
                                            f"{cod} - {nombre}", True, (255, 255, 255)
                                        )
                                        screen.blit(t, (r.x + 8, r.y + 6))
                                    pygame.display.update(
                                        pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                                    )
                                    for e in pygame.event.get():
                                        if e.type == pygame.QUIT:
                                            seleccionando = False
                                            running = False
                                        elif e.type == pygame.MOUSEBUTTONDOWN:
                                            mx, my = e.pos
                                            for idx, (cod, nombre) in enumerate(
                                                opciones
                                            ):
                                                r = pygame.Rect(
                                                    menu_x + 10,
                                                    menu_y + 10 + idx * 40,
                                                    menu_w - 20,
                                                    32,
                                                )
                                                if r.collidepoint(mx, my):
                                                    datos[fila][col] = str(cod)
                                                    funciones.guardar_archivo_csv(
                                                        "PRACTICA1/terreno.csv", datos
                                                    )
                                                    seleccionando = False
                                                    break
                                            if not seleccionando:
                                                break
                                        elif (
                                            e.type == pygame.KEYDOWN
                                            and e.key == pygame.K_ESCAPE
                                        ):
                                            seleccionando = False
                                            break
                        elif modo_valores and modo_mapa == "laberinto":
                            # Solo caminos pueden tener valores
                            if datos[fila][col] == "1" and recorridos:
                                seleccionando_v = True
                                lista_val = ["I", "F", "V", "O", "X"]
                                menu_w = 200
                                menu_h = len(lista_val) * 38 + 20
                                menu_x = min(x + 10, cell_size * 16 - menu_w - 5)
                                menu_y = min(y + 10, cell_size * 16 - menu_h - 5)
                                while seleccionando_v:
                                    pygame.draw.rect(
                                        screen,
                                        (40, 40, 60),
                                        (menu_x, menu_y, menu_w, menu_h),
                                        border_radius=10,
                                    )
                                    mf = pygame.font.Font(None, 26)
                                    celda_actual = (
                                        recorridos[fila][col]
                                        if recorridos[fila][col]
                                        else ""
                                    )
                                    for idx, simb in enumerate(lista_val):
                                        r = pygame.Rect(
                                            menu_x + 10,
                                            menu_y + 10 + idx * 38,
                                            menu_w - 20,
                                            30,
                                        )
                                        activo = simb in celda_actual
                                        pygame.draw.rect(
                                            screen,
                                            (
                                                (200, 160, 40)
                                                if activo
                                                else (70, 130, 180)
                                            ),
                                            r,
                                            border_radius=6,
                                        )
                                        t = mf.render(simb, True, (255, 255, 255))
                                        screen.blit(t, (r.x + 8, r.y + 4))
                                    pygame.display.update(
                                        pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                                    )
                                    for e in pygame.event.get():
                                        if e.type == pygame.QUIT:
                                            seleccionando_v = False
                                            running = False
                                        elif e.type == pygame.MOUSEBUTTONDOWN:
                                            mx, my = e.pos
                                            for idx, simb in enumerate(lista_val):
                                                r = pygame.Rect(
                                                    menu_x + 10,
                                                    menu_y + 10 + idx * 38,
                                                    menu_w - 20,
                                                    30,
                                                )
                                                if r.collidepoint(mx, my):
                                                    celda = (
                                                        recorridos[fila][col]
                                                        if recorridos[fila][col]
                                                        else ""
                                                    )
                                                    if simb in celda:
                                                        celda = celda.replace(simb, "")
                                                    else:
                                                        # Evitar duplicados
                                                        if simb not in celda:
                                                            celda += simb
                                                    # Normalizar orden (I,F,V,O,X)
                                                    orden = {
                                                        c: i
                                                        for i, c in enumerate(
                                                            ["I", "F", "V", "O", "X"]
                                                        )
                                                    }
                                                    celda_ordenada = "".join(
                                                        sorted(
                                                            [
                                                                c
                                                                for c in celda
                                                                if c in orden
                                                            ],
                                                            key=lambda c: orden[c],
                                                        )
                                                    )
                                                    recorridos[fila][
                                                        col
                                                    ] = celda_ordenada
                                                    funciones.guardar_archivo_csv(
                                                        "PRACTICA1/recorridos.csv",
                                                        recorridos,
                                                    )
                                                    seleccionando_v = False
                                                    break
                                            if not seleccionando_v:
                                                break
                                        elif (
                                            e.type == pygame.KEYDOWN
                                            and e.key == pygame.K_ESCAPE
                                        ):
                                            seleccionando_v = False
                                            break
                        elif modo_valores:
                            # Ahora también aplica a terreno
                            if modo_mapa == "laberinto":
                                if datos[fila][col] == "1" and recorridos:
                                    # reutilizar menú laberinto para recorridos
                                    seleccionando_v = True
                                    lista_val = ["I", "F", "V", "O", "X"]
                                    menu_w = 200
                                    menu_h = len(lista_val) * 38 + 20
                                    menu_x = min(x + 10, cell_size * 16 - menu_w - 5)
                                    menu_y = min(y + 10, cell_size * 16 - menu_h - 5)
                                    while seleccionando_v:
                                        pygame.draw.rect(
                                            screen,
                                            (40, 40, 60),
                                            (menu_x, menu_y, menu_w, menu_h),
                                            border_radius=10,
                                        )
                                        mf = pygame.font.Font(None, 26)
                                        celda_actual = (
                                            recorridos[fila][col]
                                            if recorridos[fila][col]
                                            else ""
                                        )
                                        for idx, simb in enumerate(lista_val):
                                            r = pygame.Rect(
                                                menu_x + 10,
                                                menu_y + 10 + idx * 38,
                                                menu_w - 20,
                                                30,
                                            )
                                            activo = simb in celda_actual
                                            pygame.draw.rect(
                                                screen,
                                                (
                                                    (200, 160, 40)
                                                    if activo
                                                    else (70, 130, 180)
                                                ),
                                                r,
                                                border_radius=6,
                                            )
                                            t = mf.render(simb, True, (255, 255, 255))
                                            screen.blit(t, (r.x + 8, r.y + 4))
                                        pygame.display.update(
                                            pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                                        )
                                        for e in pygame.event.get():
                                            if e.type == pygame.QUIT:
                                                seleccionando_v = False
                                                running = False
                                            elif e.type == pygame.MOUSEBUTTONDOWN:
                                                mx, my = e.pos
                                                for idx, simb in enumerate(lista_val):
                                                    r = pygame.Rect(
                                                        menu_x + 10,
                                                        menu_y + 10 + idx * 38,
                                                        menu_w - 20,
                                                        30,
                                                    )
                                                    if r.collidepoint(mx, my):
                                                        celda = (
                                                            recorridos[fila][col]
                                                            if recorridos[fila][col]
                                                            else ""
                                                        )
                                                        if simb in celda:
                                                            celda = celda.replace(
                                                                simb, ""
                                                            )
                                                        else:
                                                            if simb not in celda:
                                                                celda += simb
                                                        orden = {
                                                            c: i
                                                            for i, c in enumerate(
                                                                [
                                                                    "I",
                                                                    "F",
                                                                    "V",
                                                                    "O",
                                                                    "X",
                                                                ]
                                                            )
                                                        }
                                                        celda_ord = "".join(
                                                            sorted(
                                                                [
                                                                    c
                                                                    for c in celda
                                                                    if c in orden
                                                                ],
                                                                key=lambda c: orden[c],
                                                            )
                                                        )
                                                        recorridos[fila][
                                                            col
                                                        ] = celda_ord
                                                        funciones.guardar_archivo_csv(
                                                            "PRACTICA1/recorridos.csv",
                                                            recorridos,
                                                        )
                                                        seleccionando_v = False
                                                        break
                                                if not seleccionando_v:
                                                    break
                                            elif (
                                                e.type == pygame.KEYDOWN
                                                and e.key == pygame.K_ESCAPE
                                            ):
                                                seleccionando_v = False
                                                break

                            elif modo_mapa == "terreno":
                                seleccionando_t = True
                                lista_val = ["I", "F", "V", "O", "X"]
                                menu_w = 200
                                menu_h = len(lista_val) * 38 + 20
                                menu_x = min(x + 10, cell_size * 16 - menu_w - 5)
                                menu_y = min(y + 10, cell_size * 16 - menu_h - 5)
                                while seleccionando_t:
                                    pygame.draw.rect(
                                        screen,
                                        (50, 40, 40),
                                        (menu_x, menu_y, menu_w, menu_h),
                                        border_radius=10,
                                    )
                                    mf = pygame.font.Font(None, 26)
                                    celda_actual = (
                                        marcas_terreno[fila][col]
                                        if marcas_terreno[fila][col]
                                        else ""
                                    )
                                    for idx, simb in enumerate(lista_val):
                                        r = pygame.Rect(
                                            menu_x + 10,
                                            menu_y + 10 + idx * 38,
                                            menu_w - 20,
                                            30,
                                        )
                                        activo = simb in celda_actual
                                        pygame.draw.rect(
                                            screen,
                                            (
                                                (180, 120, 40)
                                                if activo
                                                else (70, 130, 180)
                                            ),
                                            r,
                                            border_radius=6,
                                        )
                                        t = mf.render(simb, True, (255, 255, 255))
                                        screen.blit(t, (r.x + 8, r.y + 4))
                                    pygame.display.update(
                                        pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                                    )
                                    for e in pygame.event.get():
                                        if e.type == pygame.QUIT:
                                            seleccionando_t = False
                                            running = False
                                        elif e.type == pygame.MOUSEBUTTONDOWN:
                                            mx, my = e.pos
                                            for idx, simb in enumerate(lista_val):
                                                r = pygame.Rect(
                                                    menu_x + 10,
                                                    menu_y + 10 + idx * 38,
                                                    menu_w - 20,
                                                    30,
                                                )
                                                if r.collidepoint(mx, my):
                                                    celda = (
                                                        marcas_terreno[fila][col]
                                                        if marcas_terreno[fila][col]
                                                        else ""
                                                    )
                                                    if simb in celda:
                                                        celda = celda.replace(simb, "")
                                                    else:
                                                        if simb not in celda:
                                                            celda += simb
                                                    orden = {
                                                        c: i
                                                        for i, c in enumerate(
                                                            ["I", "F", "V", "O", "X"]
                                                        )
                                                    }
                                                    celda_ord = "".join(
                                                        sorted(
                                                            [
                                                                c
                                                                for c in celda
                                                                if c in orden
                                                            ],
                                                            key=lambda c: orden[c],
                                                        )
                                                    )
                                                    marcas_terreno[fila][
                                                        col
                                                    ] = celda_ord
                                                    seleccionando_t = False
                                                    break
                                            if not seleccionando_t:
                                                break
                                        elif (
                                            e.type == pygame.KEYDOWN
                                            and e.key == pygame.K_ESCAPE
                                        ):
                                            seleccionando_t = False
                                            break

    # Dibujar UI base botones cargar
    screen.fill((0, 0, 0))
    ui_font = pygame.font.Font(None, 32)
    btn_lab_text = ui_font.render("Cargar Laberinto", True, (255, 255, 255))
    btn_ter_text = ui_font.render("Cargar Terreno", True, (255, 255, 255))
    btn_w = max(btn_lab_text.get_width(), btn_ter_text.get_width()) + 40
    btn_h = btn_lab_text.get_height() + 20
    panel_x = screen_width - btn_w - 40
    btn_laberinto_rect = pygame.Rect(panel_x, 20, btn_w, btn_h)
    btn_terreno_rect = pygame.Rect(panel_x, 20 + btn_h + 20, btn_w, btn_h)
    interfaces.dibujar_boton(screen, btn_laberinto_rect, (70, 130, 180), btn_lab_text)
    interfaces.dibujar_boton(screen, btn_terreno_rect, (100, 100, 100), btn_ter_text)

    # Botón Personaje
    pers_text = (
        f"Personaje: {personaje_seleccionado if personaje_seleccionado else 'Escoger'}"
    )
    pers_surface = ui_font.render(pers_text, True, (255, 255, 255))
    btn_personaje_rect = pygame.Rect(
        panel_x, btn_terreno_rect.bottom + 20, btn_w, btn_h
    )
    interfaces.dibujar_boton(screen, btn_personaje_rect, (120, 60, 90), pers_surface)

    # Botón Modificar mapa
    mod_texto = "Modificar: ON" if modificar_mapa else "Modificar: OFF"
    mod_surface = ui_font.render(mod_texto, True, (255, 255, 255))
    btn_modificar_rect = pygame.Rect(
        panel_x, btn_personaje_rect.bottom + 20, btn_w, btn_h
    )
    interfaces.dibujar_boton(
        screen,
        btn_modificar_rect,
        (150, 90, 40) if modificar_mapa else (90, 60, 40),
        mod_surface,
    )

    # Botón Valores especiales (ahora ambos mapas si alguno cargado)
    if modo_mapa in ("laberinto", "terreno"):
        val_texto = f"Valores: {'ON' if modo_valores else 'OFF'}"
        val_surface = ui_font.render(val_texto, True, (255, 255, 255))
        btn_valores_rect = pygame.Rect(
            panel_x, btn_modificar_rect.bottom + 20, btn_w, btn_h
        )
        interfaces.dibujar_boton(
            screen,
            btn_valores_rect,
            (180, 140, 30) if modo_valores else (110, 90, 40),
            val_surface,
        )
        estado_base_y = btn_valores_rect.bottom + 20
    else:
        estado_base_y = btn_modificar_rect.bottom + 20

    # Botón Cubrir/Descubrir
    cover_text = "Descubrir: ON" if mostrar_cubierto else "Descubrir: OFF"
    cover_surface = ui_font.render(cover_text, True, (255, 255, 255))
    btn_cover_rect = pygame.Rect(panel_x, estado_base_y, btn_w, btn_h)
    interfaces.dibujar_boton(
        screen,
        btn_cover_rect,
        (40, 120, 160) if mostrar_cubierto else (60, 60, 90),
        cover_surface,
    )
    estado_base_y = btn_cover_rect.bottom + 20

    # Placeholder texto estado
    estado_font = pygame.font.Font(None, 24)
    estado_lineas = []
    estado_lineas.append(
        f"{modo_mapa or 'Sin mapa'} | {personaje_seleccionado or '-'} | Cost:{costo_acumulado}"
    )
    if modo_mapa in ("laberinto", "terreno") and personaje_seleccionado:
        # Determinar posición actual
        if modo_mapa == "laberinto":
            pos_act = obtener_pos_actual_laberinto()
        else:
            pos_act = globals().get("pos_terreno", None)
        if pos_act:
            i0, j0 = pos_act

            def label_vecino(i, j):
                if not (0 <= i < 15 and 0 <= j < 15):
                    return "Fuera"
                if modo_mapa == "laberinto":
                    tipo = "Camino" if datos[i][j] == "1" else "Pared"
                    simb = ""
                    if (
                        datos[i][j] == "1"
                        and recorridos
                        and 0 <= i < len(recorridos)
                        and 0 <= j < len(recorridos[0])
                    ):
                        simb_raw = recorridos[i][j] or ""
                        if simb_raw:
                            partes = []
                            for c in simb_raw:
                                if (
                                    c in SIMBOLOS_DESCRIP
                                    and SIMBOLOS_DESCRIP[c] not in partes
                                ):
                                    partes.append(SIMBOLOS_DESCRIP[c])
                            simb = ",".join(partes)
                        else:
                            simb = ""
                    return f"{tipo}{' '+simb if simb else ''}".strip()
                else:
                    try:
                        t = int(datos[i][j])
                    except:
                        return "N/A"
                    nombres = {
                        0: "Montaña",
                        1: "Tierra",
                        2: "Agua",
                        3: "Arena",
                        4: "Bosque",
                    }
                    base = nombres.get(t, str(t))
                    simb = ""
                    if (
                        marcas_terreno
                        and 0 <= i < len(marcas_terreno)
                        and 0 <= j < len(marcas_terreno[0])
                    ):
                        simb_raw = marcas_terreno[i][j] or ""
                        if simb_raw:
                            partes = []
                            for c in simb_raw:
                                if (
                                    c in SIMBOLOS_DESCRIP
                                    and SIMBOLOS_DESCRIP[c] not in partes
                                ):
                                    partes.append(SIMBOLOS_DESCRIP[c])
                            simb = ",".join(partes)
                        else:
                            simb = ""
                    return f"{base}{' '+simb if simb else ''}".strip()

            vecinos_info = {
                "Arriba": label_vecino(i0 - 1, j0),
                "Abajo": label_vecino(i0 + 1, j0),
                "Izq": label_vecino(i0, j0 - 1),
                "Der": label_vecino(i0, j0 + 1),
            }
            estado_lineas.append("Vecinos:")
            for k, v in vecinos_info.items():
                estado_lineas.append(f" {k}: {v}")
    if info_celda_click:
        estado_lineas.append(info_celda_click)
    # Limitar a 8 líneas máximas
    estado_lineas = estado_lineas[:8]

    # Vecinos compactos unificados
    if modo_mapa in ("laberinto", "terreno") and personaje_seleccionado:
        if modo_mapa == "laberinto":
            pos_act = obtener_pos_actual_laberinto()
        else:
            pos_act = globals().get("pos_terreno", None)
        if pos_act:
            i0, j0 = pos_act
        else:
            # Buscar primera celda válida camino/terreno como fallback
            i0 = j0 = 0

        def short_label(i, j):
            if not (0 <= i < 15 and 0 <= j < 15):
                return "—"
            if modo_mapa == "laberinto":
                base = "C" if datos and datos[i][j] == "1" else "P"
                simb_raw = ""
                if (
                    datos
                    and datos[i][j] == "1"
                    and recorridos
                    and 0 <= i < len(recorridos)
                    and 0 <= j < len(recorridos[0])
                ):
                    simb_raw = recorridos[i][j] or ""
                orden = ["I", "F", "V", "O", "X"]
                simb_fil = "".join([c for c in simb_raw if c in orden])
                return base + (":" + simb_fil if simb_fil else "")
            else:
                try:
                    t = int(datos[i][j])
                except:
                    return "?"
                nombres_c = {0: "M", 1: "T", 2: "Ag", 3: "Ar", 4: "B"}
                base = nombres_c.get(t, str(t))
                simb_raw = (
                    marcas_terreno[i][j]
                    if (
                        marcas_terreno
                        and 0 <= i < len(marcas_terreno)
                        and 0 <= j < len(marcas_terreno[0])
                    )
                    else ""
                )
                orden = ["I", "F", "V", "O", "X"]
                simb_fil = "".join([c for c in simb_raw if c in orden])
                return base + (":" + simb_fil if simb_fil else "")

        vecinos_compacto = f"A:{short_label(i0-1,j0)} B:{short_label(i0+1,j0)} I:{short_label(i0,j0-1)} D:{short_label(i0,j0+1)}"
        # Insertar/actualizar línea de vecinos (si ya existía remover anterior marcada 'A:' pattern)
        estado_lineas = [l for l in estado_lineas if not l.startswith("A:")]
        estado_lineas.append(vecinos_compacto)
    # Limitar a 8 líneas máximas
    estado_lineas = estado_lineas[:8]

    for li, linea in enumerate(estado_lineas):
        esurf = estado_font.render(linea, True, (255, 255, 0))
        screen.blit(esurf, (panel_x, estado_base_y + li * 14))

    # Dibujo grid base y mapa
    dibujar_grid_base(screen)
    if modo_mapa == "laberinto":
        dibujar_mapa_laberinto(screen, datos, recorridos)
    elif modo_mapa == "terreno":
        dibujar_mapa_terreno(screen, datos)
        # Draw player on terreno
        pos_t = globals().get("pos_terreno", None)
        if pos_t:
            px = pos_t[1] * cell_size + cell_size
            py = pos_t[0] * cell_size + cell_size
            pygame.draw.circle(
                screen, (255, 120, 0), (px + cell_size // 2, py + cell_size // 2), 10
            )

    pygame.display.flip()

pygame.quit()
