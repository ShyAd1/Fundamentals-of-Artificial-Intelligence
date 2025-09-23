import pygame
import funciones
import interfaces

screen_width, screen_height = 1000, 600

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mi Juego")

# Leer datos de un archivo CSV
datos = funciones.leer_archivo_csv("PRACTICA1/laberinto.csv")
recorridos = funciones.leer_archivo_csv("PRACTICA1/recorridos.csv")


# Copia del recorrido original para restaurar después
copy_recorridos = [fila[:] for fila in recorridos]

# Definir nombres de columnas desde 'A' en adelante
num_columnas = len(datos[0]) if datos else 0
columnas = [chr(ord("A") + i) for i in range(num_columnas)]

costos_personaje = {
    "Humano": 1,
    "Mono": 2,
    "Pulpo": 3,
    "Sasquatch": 4,
}
costo_total = 0

# Bucle principal del juego
running = True
while running:
    # Botón para modo "cubrir mapa"
    modo_cubrir = globals().get("modo_cubrir", False)
    cubrir_texto = "Cubrir mapa" if not modo_cubrir else "Mostrar todo"
    cubrir_font = pygame.font.Font(None, 32)
    cubrir_surface = cubrir_font.render(cubrir_texto, True, (255, 255, 255))
    cubrir_width = cubrir_surface.get_width() + 30
    cubrir_height = cubrir_surface.get_height() + 20
    cubrir_x = screen_width - cubrir_width - 40
    cubrir_y = 80
    cubrir_rect = pygame.Rect(cubrir_x, cubrir_y, cubrir_width, cubrir_height)

    # Botón para seleccionar personaje
    personajes = ["Humano", "Mono", "Pulpo", "Sasquatch"]
    personaje_seleccionado = globals().get("personaje_seleccionado", None)
    seleccionando_personaje = globals().get("seleccionando_personaje", False)
    personaje_texto = (
        f"Personaje: {personaje_seleccionado if personaje_seleccionado else 'Escoger'}"
    )
    personaje_font = pygame.font.Font(None, 32)
    personaje_surface = personaje_font.render(personaje_texto, True, (255, 255, 255))
    personaje_width = personaje_surface.get_width() + 30
    personaje_height = personaje_surface.get_height() + 20
    personaje_x = screen_width - personaje_width - 40
    personaje_y = 200
    personaje_rect = pygame.Rect(
        personaje_x, personaje_y, personaje_width, personaje_height
    )
    modificar_mapa = globals().get("modificar_mapa", False)
    modo_valores = globals().get("modo_valores", False)
    valores_dict = {
        "V": "Lugar ya visitado",
        "O": "Decision",
        "I": "Inicio",
        "F": "Final",
        "X": "Posicion actual",
    }
    valores_lista = list(valores_dict.keys())

    font = pygame.font.Font(None, 32)
    # Botón Modificar mapa
    boton_texto = "Modificar mapa" if not modificar_mapa else "Terminar modificación"
    texto_surface = font.render(boton_texto, True, (255, 255, 255))
    boton_width = texto_surface.get_width() + 30
    boton_height = texto_surface.get_height() + 20
    screen_width, screen_height = screen.get_size()
    boton_x = screen_width - boton_width - 40
    boton_y = 20
    boton_rect = pygame.Rect(boton_x, boton_y, boton_width, boton_height)
    # Botón Valores especiales
    valores_texto = "Valores especiales" if not modo_valores else "Terminar valores"
    valores_surface = font.render(valores_texto, True, (255, 255, 255))
    valores_width = valores_surface.get_width() + 30
    valores_height = valores_surface.get_height() + 20
    valores_x = screen_width - valores_width - 40
    valores_y = 140
    valores_rect = pygame.Rect(valores_x, valores_y, valores_width, valores_height)
    eventos = pygame.event.get()
    for event in eventos:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Click en botón Modificar mapa
            if boton_rect.collidepoint(x, y):
                modificar_mapa = not modificar_mapa
                globals()["modificar_mapa"] = modificar_mapa
                modo_valores = False
                globals()["modo_valores"] = modo_valores
                # Sincronizar recorridos con datos
                for fi in range(len(datos)):
                    for co in range(len(datos[0])):
                        if datos[fi][co] == "1":
                            recorridos[fi][co] = ""
                        else:
                            recorridos[fi][co] = "Pared"
                funciones.guardar_archivo_csv("PRACTICA1/recorridos.csv", recorridos)
            # Click en botón Valores especiales
            elif valores_rect.collidepoint(x, y):
                modo_valores = not modo_valores
                globals()["modo_valores"] = modo_valores
                modificar_mapa = False
                globals()["modificar_mapa"] = modificar_mapa
            # Click en botón Cubrir mapa
            elif cubrir_rect.collidepoint(x, y):
                modo_cubrir = not modo_cubrir
                globals()["modo_cubrir"] = modo_cubrir
            # Click en botón Personaje
            elif personaje_rect.collidepoint(x, y):
                seleccionando_personaje = True
                globals()["seleccionando_personaje"] = True
            else:
                col = x // 40
                fila = y // 40
                nombre_col = columnas[col] if col < len(columnas) else col
                if modificar_mapa:
                    # Flip cell value and save
                    if 0 <= fila < len(datos) and 0 <= col < len(datos[0]):
                        nuevo_valor = "0" if datos[fila][col] == "1" else "1"
                        funciones.modificar_dato(datos, fila, col, nuevo_valor)
                        funciones.guardar_archivo_csv("PRACTICA1/laberinto.csv", datos)
                        # Sincronizar recorridos con datos tras modificar
                        for fi in range(len(datos)):
                            for co in range(len(datos[0])):
                                if datos[fi][co] == "1":
                                    recorridos[fi][co] = ""
                                else:
                                    recorridos[fi][co] = "Pared"
                        funciones.guardar_archivo_csv(
                            "PRACTICA1/recorridos.csv", recorridos
                        )
                elif modo_valores:
                    # Solo permitir valores especiales en celdas de camino
                    if (
                        0 <= fila < len(recorridos)
                        and 0 <= col < len(recorridos[0])
                        and datos[fila][col] == "1"
                    ):
                        seleccionando = True
                        while seleccionando:
                            menu_x = screen_width - 300
                            menu_y = screen_height // 2 - 120
                            menu_w = 260
                            menu_h = 220
                            pygame.draw.rect(
                                screen,
                                (40, 40, 40),
                                (menu_x, menu_y, menu_w, menu_h),
                                border_radius=10,
                            )
                            menu_font = pygame.font.Font(None, 36)
                            celda_actual = (
                                recorridos[fila][col] if recorridos[fila][col] else ""
                            )
                            for idx, val in enumerate(valores_lista):
                                btn_rect = pygame.Rect(
                                    menu_x + 20, menu_y + 20 + idx * 40, 60, 36
                                )
                                color_btn = (
                                    (255, 215, 0)
                                    if val in celda_actual
                                    else (70, 130, 180)
                                )
                                pygame.draw.rect(
                                    screen, color_btn, btn_rect, border_radius=8
                                )
                                btn_text = menu_font.render(val, True, (255, 255, 255))
                                screen.blit(btn_text, (btn_rect.x + 15, btn_rect.y + 5))
                            pygame.display.flip()
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    running = False
                                    seleccionando = False
                                elif e.type == pygame.MOUSEBUTTONDOWN:
                                    mx, my = e.pos
                                    for idx, val in enumerate(valores_lista):
                                        btn_rect = pygame.Rect(
                                            menu_x + 20, menu_y + 20 + idx * 40, 60, 36
                                        )
                                        if btn_rect.collidepoint(mx, my):
                                            celda = (
                                                recorridos[fila][col]
                                                if recorridos[fila][col]
                                                else ""
                                            )
                                            if val in celda:
                                                # Quitar valor
                                                celda = celda.replace(val, "")
                                            else:
                                                # Agregar valor
                                                celda += val
                                            recorridos[fila][col] = celda
                                            funciones.guardar_archivo_csv(
                                                "PRACTICA1/recorridos.csv", recorridos
                                            )
                                            # Copia del recorrido original para restaurar después
                                            copy_recorridos = [
                                                fila[:] for fila in recorridos
                                            ]

                                            seleccionando = False
                                            break
                                elif (
                                    e.type == pygame.KEYDOWN
                                    and e.key == pygame.K_ESCAPE
                                ):
                                    seleccionando = False
                                    break
                else:
                    if 0 <= fila < len(datos) and 0 <= col < len(datos[0]):
                        if datos[fila][col] == "1":
                            interfaces.mostrar_mensaje(
                                f"Clic en camino en ({nombre_col},{fila+1})", screen
                            )
                        else:
                            interfaces.mostrar_mensaje(
                                f"Clic en pared en ({nombre_col},{fila+1})", screen
                            )

    # Dibujar botón Personaje
    interfaces.dibujar_boton(screen, personaje_rect, (200, 100, 100), personaje_surface)

    # Menú de selección de personaje
    if seleccionando_personaje:
        menu_x = screen_width - 300
        menu_y = screen_height // 2 - 120
        menu_w = 260
        menu_h = 220
        interfaces.dibujar_menu_personaje(
            screen,
            menu_x,
            menu_y,
            menu_w,
            menu_h,
            [(nombre, costos_personaje[nombre]) for nombre in personajes],
        )
        pygame.display.flip()
        menu_open = True
        while menu_open:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    menu_open = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = e.pos
                    for idx, nombre in enumerate(personajes):
                        btn_rect = pygame.Rect(
                            menu_x + 20, menu_y + 20 + idx * 40, 180, 36
                        )
                        if btn_rect.collidepoint(mx, my):
                            personaje_seleccionado = nombre
                            seleccionando_personaje = False
                            globals()["personaje_seleccionado"] = personaje_seleccionado
                            globals()["seleccionando_personaje"] = False
                            menu_open = False
                            break
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    seleccionando_personaje = False
                    globals()["seleccionando_personaje"] = False
                    menu_open = False

    # Actualizar la pantalla
    pygame.display.flip()

    # Dibujar grid basado en los datos leídos
    screen.fill((0, 0, 0))  # Limpiar la pantalla con negro
    mostrar_celda = lambda i, j: False
    if modo_cubrir:
        # Buscar todas las posiciones X
        posiciones_xv = [
            (i, j)
            for i in range(len(recorridos))
            for j in range(len(recorridos[0]))
            if recorridos[i][j] and ("X" in recorridos[i][j] or "V" in recorridos[i][j])
        ]
        vecinos = set()
        for i, j in posiciones_xv:
            vecinos.add((i, j))
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < len(recorridos) and 0 <= nj < len(recorridos[0]):
                    vecinos.add((ni, nj))
        mostrar_celda = lambda i, j: (i, j) in vecinos
    else:
        mostrar_celda = lambda i, j: True

    for i, fila in enumerate(datos):
        for j, columna in enumerate(fila):
            if mostrar_celda(i, j):
                if columna == "1":
                    color = (255, 255, 255)  # Blanco para caminos o celdas validas
                else:
                    color = (74, 74, 74)  # Gris para paredes o celdas inválidas
                pygame.draw.rect(screen, color, (j * 40, i * 40, 40, 40))
                # Dibujar valores especiales si existen en recorridos
                if (
                    0 <= i < len(recorridos)
                    and 0 <= j < len(recorridos[0])
                    and datos[i][j] == "1"
                ):
                    val = recorridos[i][j]
                    if (
                        val
                        and val != "Null"
                        and any(letra in valores_lista for letra in val)
                    ):
                        letra_font = pygame.font.Font(None, 20)
                        x_offset = 0
                        for letra in val:
                            if letra in valores_lista:
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
                                screen.blit(
                                    letra_surface, (j * 40 + 5 + x_offset, i * 40 + 12)
                                )
                                x_offset += letra_surface.get_width() + 2
                else:
                    # Cubrir celda con gris si no es camino
                    pygame.draw.rect(screen, color, (j * 40, i * 40, 40, 40))

    # Movimiento del personaje con teclas
    if personaje_seleccionado:
        # Buscar posición actual (X) o inicio (I)
        pos_actual = None
        for i in range(len(recorridos)):
            for j in range(len(recorridos[0])):
                if recorridos[i][j] and "X" in recorridos[i][j]:
                    pos_actual = (i, j)
        if not pos_actual:
            for i in range(len(recorridos)):
                for j in range(len(recorridos[0])):
                    if recorridos[i][j] and "I" in recorridos[i][j]:
                        pos_actual = (i, j)
                        break
                if pos_actual:
                    break
        # Mostrar vecinos de la posición actual
        if pos_actual:
            vecinos = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = pos_actual[0] + di, pos_actual[1] + dj
                if 0 <= ni < len(recorridos) and 0 <= nj < len(recorridos[0]):
                    col_name = columnas[nj] if nj < len(columnas) else str(nj)
                    valor = recorridos[ni][nj] if recorridos[ni][nj] else "Camino"
                    significado = []
                    for letra in valor:
                        if letra in valores_dict:
                            significado.append(valores_dict[letra])
                    desc = f" ({'/'.join(significado)})" if significado else ""
                    vecinos.append(f"({col_name},{ni+1}): {valor}{desc}")
            vecinos_texto = "Vecinos: " + ", ".join(vecinos)
            interfaces.dibujar_vecinos(screen, vecinos_texto, screen_height)
        # Procesar eventos KEYDOWN usando la lista de eventos
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    dx, dy = -1, 0
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    dx, dy = 1, 0
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    dx, dy = 0, -1
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    dx, dy = 0, 1
                if dx != 0 or dy != 0:
                    ni = pos_actual[0] + dx
                    nj = pos_actual[1] + dy
                    if (
                        0 <= ni < len(datos)
                        and 0 <= nj < len(datos[0])
                        and datos[ni][nj] == "1"
                    ):
                        costo_mov = 0
                        # Sumar costo si la casilla destino tiene 'V' (ya visitada)
                        if "V" in recorridos[ni][nj]:
                            costo_mov = costos_personaje.get(personaje_seleccionado, 1)
                        # Marcar anterior como V
                        val_ant = recorridos[pos_actual[0]][pos_actual[1]]
                        nuevo_val_ant = ""
                        if "V" not in val_ant:
                            nuevo_val_ant = "V"
                        for letra in val_ant:
                            if letra in valores_lista and letra != "X":
                                nuevo_val_ant += letra
                        recorridos[pos_actual[0]][pos_actual[1]] = nuevo_val_ant
                        # Marcar nueva posición como X
                        val_nueva = recorridos[ni][nj] if recorridos[ni][nj] else ""
                        nuevo_val_nueva = "X"
                        for letra in val_nueva:
                            if letra in valores_lista and letra != "X":
                                nuevo_val_nueva += letra
                        recorridos[ni][nj] = nuevo_val_nueva
                        funciones.guardar_archivo_csv(
                            "PRACTICA1/recorridos.csv", recorridos
                        )
                        costo_total += costo_mov
                        # Si llegó a F, calcular costo por cantidad de V's
                        if "F" in nuevo_val_nueva:
                            # Contar todas las V en recorridos
                            v_count = sum(fila.count("V") for fila in recorridos)
                            peso = costos_personaje.get(personaje_seleccionado, 1)
                            costo_final = (
                                v_count + 2
                            ) * peso  # +2 por el movimiento de la casilla anterior a F y la F
                            interfaces.mostrar_mensaje(
                                f"¡Llegaste a la meta!     Costo total: {costo_final}",
                                screen,
                            )
                            recorridos = funciones.leer_archivo_csv(
                                "PRACTICA1/recorridos.csv"
                            )
                            funciones.guardar_archivo_csv(
                                "PRACTICA1/recorridos.csv", copy_recorridos
                            )
                            recorridos = [fila[:] for fila in copy_recorridos]
                            costo_total = 0
                            break

    # Dibujar grid
    for x in range(0, 600, 40):
        pygame.draw.line(screen, (128, 128, 128), (x, 0), (x, 600))
    for y in range(0, 600, 40):
        pygame.draw.line(screen, (128, 128, 128), (0, y), (600, y))

    # Dibujar botón Modificar mapa
    interfaces.dibujar_boton(screen, boton_rect, (70, 130, 180), texto_surface)
    interfaces.dibujar_boton(screen, valores_rect, (34, 177, 76), valores_surface)
    interfaces.dibujar_boton(screen, cubrir_rect, (80, 80, 80), cubrir_surface)


# Limpiar recorrido anterior
funciones.guardar_archivo_csv("PRACTICA1/recorridos.csv", copy_recorridos)
# Cerrar Pygame
pygame.quit()
