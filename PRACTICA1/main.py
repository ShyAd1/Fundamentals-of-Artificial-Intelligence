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

# Variables para animación de algoritmos
alg_animating = globals().get("alg_animating", False)
alg_current = globals().get("alg_current", None)
alg_frontier = globals().get("alg_frontier", set())
alg_path = globals().get("alg_path", set())
alg_tree_edges = globals().get("alg_tree_edges", set())
alg_path_seq = globals().get("alg_path_seq", [])

# Tipo de algoritmo actual (para diferenciar visualmente BFS/DFS)
alg_type = globals().get("alg_type", None)

# Nueva variable para mostrar celdas cubiertas
mostrar_cubierto = globals().get("mostrar_cubierto", False)

# Visualización de árbol de decisiones y ruta ideal
show_tree = globals().get("show_tree", False)
tree_node_pos = globals().get("tree_node_pos", {})  # (i,j) -> (x,y)
tree_edges_cached = globals().get("tree_edges_cached", set())  # set(((i,j),(ni,nj)))
route_ideal = globals().get("route_ideal", [])  # [((i,j), dirCode)]
# Toast flotante para mostrar la ruta ideal automáticamente tras la búsqueda
route_toast = globals().get("route_toast", None)  # dict con title, cells, dirs
route_toast_until = globals().get(
    "route_toast_until", 0
)  # pygame.time.get_ticks() límite


def cell_name(i, j):
    try:
        return f"{chr(ord('A')+j)}{i+1}"
    except Exception:
        return f"({i},{j})"


def dir_code(from_cell, to_cell):
    (i, j), (ni, nj) = from_cell, to_cell
    di, dj = ni - i, nj - j
    if di == -1 and dj == 0:
        return "A"  # Arriba
    if di == 1 and dj == 0:
        return "B"  # Abajo
    if di == 0 and dj == -1:
        return "I"  # Izquierda
    if di == 0 and dj == 1:
        return "D"  # Derecha


def build_tree_from_edges(root, edges):
    from collections import defaultdict

    tree = defaultdict(list)
    for a, b in edges:
        tree[a].append(b)
    # Asegurar root existe aunque no tenga hijos
    if root not in tree:
        tree[root] = []
    return tree


def compute_levels_positions(root, tree, area, node_radius=12):
    # area: (x,y,w,h). Compute BFS levels and spread nodes per level.
    from collections import deque, defaultdict

    x0, y0, w, h = area
    levels = defaultdict(list)
    level_of = {root: 0}
    q = deque([root])
    seen = {root}
    while q:
        # Permitir interacción básica durante la animación (botones Árbol/Ruta/Cubrir, salir)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                globals()["running"] = False
                alg_animating = False
                globals()["alg_animating"] = alg_animating
                return False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                # Cancelar/abortar animación
                alg_animating = False
                globals()["alg_animating"] = alg_animating
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                x, y = ev.pos
                _btn_tree = globals().get("btn_tree_rect")
                if _btn_tree and _btn_tree.collidepoint(x, y):
                    globals()["show_tree"] = not globals().get("show_tree", False)
                _btn_route = globals().get("btn_route_rect")
                if _btn_route and _btn_route.collidepoint(x, y):
                    globals()["show_route"] = not globals().get("show_route", False)
                _btn_cover = globals().get("btn_cover_rect")
                if _btn_cover and _btn_cover.collidepoint(x, y):
                    globals()["mostrar_cubierto"] = not globals().get(
                        "mostrar_cubierto", False
                    )
        u = q.popleft()
        lvl = level_of[u]
        levels[lvl].append(u)
        for v in tree.get(u, []):
            if v not in seen:
                seen.add(v)
                level_of[v] = lvl + 1
                q.append(v)
    max_level = max(levels.keys()) if levels else 0
    pos = {}
    for lvl in range(0, max_level + 1):
        nodes = levels.get(lvl, [])
        n = max(1, len(nodes))
        y = y0 + (h * (lvl + 1) // (max_level + 2))
        for idx, node in enumerate(nodes):
            x = x0 + (w * (idx + 1) // (n + 1))
            pos[node] = (x, y)
    return pos


def prepare_tree_visual():
    # Usa alg_tree_edges y alg_path_seq actuales para preparar posiciones y ruta ideal
    global tree_node_pos, tree_edges_cached, route_ideal
    if not alg_tree_edges:
        return False
    # Encontrar root desde 'I' en recorridos o usar primer punto del path
    root = None
    try:
        for i in range(min(15, len(recorridos))):
            for j in range(min(15, len(recorridos[0]))):
                if recorridos[i][j] and "I" in recorridos[i][j]:
                    root = (i, j)
                    break
            if root:
                break
    except Exception:
        root = None
    if root is None:
        root = alg_path_seq[0] if alg_path_seq else None
    if root is None:
        return False
    # Construir árbol dirigido desde edges
    tree_edges_cached = set(alg_tree_edges)
    tree = build_tree_from_edges(root, tree_edges_cached)
    # Layout en el área del grid (izquierda)
    grid_area = (10, 50, 620, 540)
    tree_node_pos = compute_levels_positions(root, tree, grid_area)
    # Calcular ruta ideal (lista de (cell_name, dir))
    rlist = []
    if alg_path_seq and len(alg_path_seq) > 1:
        for idx in range(len(alg_path_seq) - 1):
            a = alg_path_seq[idx]
            b = alg_path_seq[idx + 1]
            rlist.append((cell_name(*a), dir_code(a, b)))
    route_ideal = rlist
    globals()["tree_node_pos"] = tree_node_pos
    globals()["tree_edges_cached"] = tree_edges_cached
    globals()["route_ideal"] = route_ideal
    return True


def draw_decision_tree(surface):
    if not tree_node_pos or not tree_edges_cached:
        return
    # Fondo translúcido
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    # Título con tipo de algoritmo
    title = f"Árbol {alg_type}" if alg_type else "Árbol"
    tfont = pygame.font.Font(None, 28)
    title_surf = tfont.render(title, True, (255, 255, 255))
    title_bg = pygame.Surface(
        (title_surf.get_width() + 16, title_surf.get_height() + 10), pygame.SRCALPHA
    )
    title_bg.fill((20, 20, 20, 180))
    surface.blit(title_bg, (12, 12))
    surface.blit(title_surf, (20, 17))
    # Dibujar edges (primero)
    path_edges = set()
    if alg_path_seq and len(alg_path_seq) > 1:
        for idx in range(len(alg_path_seq) - 1):
            path_edges.add((alg_path_seq[idx], alg_path_seq[idx + 1]))
    base_edge_color = (150, 220, 120) if alg_type == "BFS" else (200, 150, 240)
    path_edge_color = (70, 130, 200)
    for a, b in tree_edges_cached:
        if a in tree_node_pos and b in tree_node_pos:
            color = path_edge_color if (a, b) in path_edges else base_edge_color
            width = 4 if (a, b) in path_edges else 3
            pygame.draw.line(surface, color, tree_node_pos[a], tree_node_pos[b], width)
    # Dibujar nodos
    fnode = pygame.font.Font(None, 15)
    node_radius = 11  # radios más pequeño para reducir solapamiento visual
    outline_w = 2
    for node, (x, y) in tree_node_pos.items():
        pygame.draw.circle(surface, (30, 30, 30), (x, y), node_radius)
        pygame.draw.circle(surface, (220, 220, 220), (x, y), node_radius, outline_w)
        label = cell_name(*node)
        txt = fnode.render(label, True, (255, 255, 255))
        # Centrar el texto exactamente en el centro del nodo
        txt_rect = txt.get_rect(center=(x, y))
        surface.blit(txt, txt_rect)
    # Dibujar etiquetas de dirección al final, con offset para evitar superponer nodos
    for a, b in tree_edges_cached:
        if a not in tree_node_pos or b not in tree_node_pos:
            continue
        ax, ay = tree_node_pos[a]
        bx, by = tree_node_pos[b]
        vx, vy = (bx - ax, by - ay)
        length = max(1.0, (vx * vx + vy * vy) ** 0.5)
        ux, uy = (vx / length, vy / length)  # unit along edge
        nx, ny = (-uy, ux)  # perpendicular unit
        # posición a lo largo de la arista, sesgada para alejarse de los nodos
        t = 0.58
        px = ax + ux * (length * t)
        py = ay + uy * (length * t)

        # si está muy cerca de un nodo, alejar un poco más
        def dist2(x1, y1, x2, y2):
            dx, dy = x1 - x2, y1 - y2
            return dx * dx + dy * dy

        node_r = node_radius + 3
        if dist2(px, py, ax, ay) < (node_r * node_r):
            t = 0.68
            px = ax + ux * (length * t)
            py = ay + uy * (length * t)
        if dist2(px, py, bx, by) < (node_r * node_r):
            t = 0.42
            px = ax + ux * (length * t)
            py = ay + uy * (length * t)
        d = dir_code(a, b)
        f = pygame.font.Font(None, 15)
        label_s = f.render(d, True, (255, 230, 0))
        # fondo semitransparente para legibilidad
        bg_w, bg_h = label_s.get_width() + 8, label_s.get_height() + 4
        bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        # contorno ligero
        outline_f = pygame.font.Font(None, 15)
        outline_s = outline_f.render(d, True, (0, 0, 0))
        # colocar
        bx0 = int(px - bg_w / 2)
        by0 = int(py - bg_h / 2)
        surface.blit(bg, (bx0, by0))
        for dx in (-1, 1):
            for dy in (-1, 1):
                surface.blit(outline_s, (bx0 + 4 + dx, by0 + 2 + dy))
        surface.blit(label_s, (bx0 + 4, by0 + 2))


def draw_route_toast(surface):
    """Muestra un mensaje flotante temporal con la ruta ideal al terminar la búsqueda."""
    if not route_toast or pygame.time.get_ticks() > route_toast_until:
        return
    width, height = surface.get_size()
    margin = 10
    font_title = pygame.font.Font(None, 28)
    font_body = pygame.font.Font(None, 24)
    title = route_toast.get("title", "Ruta ideal")
    cells = route_toast.get("cells", [])
    dirs = route_toast.get("dirs", [])

    # Construir líneas compactas (una para celdas, otra para direcciones)
    cells_str = " ".join(cells)
    dirs_str = " ".join(dirs) if dirs else ""
    ts = font_title.render(title, True, (255, 255, 255))
    cs = font_body.render(cells_str, True, (255, 230, 0))
    ds = font_body.render(dirs_str, True, (180, 180, 255)) if dirs_str else None

    box_w = (
        max(ts.get_width(), cs.get_width(), ds.get_width() if ds else 0) + 2 * margin
    )
    box_h = (
        ts.get_height() + cs.get_height() + (ds.get_height() if ds else 0) + 3 * margin
    )
    # Posición flotante arriba-izquierda del grid
    bx, by = 10, 10
    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    panel.blit(ts, (margin, margin))
    panel.blit(cs, (margin, margin + ts.get_height() + 4))
    if ds:
        panel.blit(ds, (margin, margin + ts.get_height() + 4 + cs.get_height() + 2))
    # Borde
    pygame.draw.rect(panel, (200, 200, 200), panel.get_rect(), 1)
    surface.blit(panel, (bx, by))


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
    global datos, recorridos, modo_mapa, copy_recorridos, costo_acumulado, recorridos_inicial
    datos = funciones.leer_archivo_csv("PRACTICA1/terreno.csv")
    # Cargar marcas/recorridos de terreno desde archivo (archivo esperado: recorridos_terreno.csv)
    # Guardamos en la variable marcas_terreno (y también en 'recorridos' para compatibilidad)
    marcas = []
    try:
        marcas = funciones.leer_archivo_csv("PRACTICA1/recorridos_terreno.csv")
    except FileNotFoundError:
        # Crear estructura vacía compatible (15x15)
        marcas = [["" for _ in range(15)] for __ in range(15)]
    # Asegurar dimensiones 15x15
    marcas_terreno_local = [
        [
            (marcas[i][j] if j < len(marcas[i]) else "") if i < len(marcas) else ""
            for j in range(15)
        ]
        for i in range(15)
    ]
    globals()["marcas_terreno"] = marcas_terreno_local
    recorridos = marcas_terreno_local
    if recorridos_inicial is None:
        recorridos_inicial = [fila[:] for fila in recorridos]
    copy_recorridos = [fila[:] for fila in recorridos]
    modo_mapa = "terreno"
    costo_acumulado = 0
    globals()["costo_acumulado"] = costo_acumulado
    reset_estado_descubrimiento()
    globals()["modo_mapa"] = modo_mapa


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


def aplicar_camino_en_recorridos(path):
    # Marca V en cada paso (excepto I/F), limpia X anteriores y pone X en objetivo; guarda CSV
    global recorridos, costo_acumulado
    if not path:
        return False
    # Quitar X anterior
    for i_r in range(min(15, len(recorridos))):
        for j_r in range(min(15, len(recorridos[0]))):
            if recorridos[i_r][j_r] and "X" in recorridos[i_r][j_r]:
                recorridos[i_r][j_r] = recorridos[i_r][j_r].replace("X", "")
    pasos = 0
    for idx, (i, j) in enumerate(path):
        actual = (
            recorridos[i][j]
            if recorridos and i < len(recorridos) and j < len(recorridos[0])
            else ""
        )
        # No sobrescribir I o F
        if "I" not in actual and "F" not in actual and "X" not in actual:
            if "V" not in actual:
                recorridos[i][j] = (actual or "") + "V"
        pasos += 1
        descubrir_alrededor(descubiertas_laberinto, i, j)
    # Poner X en el último
    li, lj = path[-1]
    if "X" not in (recorridos[li][lj] or ""):
        recorridos[li][lj] = (recorridos[li][lj] or "") + "X"
    # Incrementar costo por pasos (cada movimiento 1)
    globals()["costo_acumulado"] = globals().get("costo_acumulado", 0) + max(
        0, pasos - 1
    )
    # Normalizar orden en todo el grid (I,F,V,O,X)
    orden = {c: i for i, c in enumerate(["I", "F", "V", "O", "X"])}
    for i_r in range(min(15, len(recorridos))):
        for j_r in range(min(15, len(recorridos[0]))):
            if recorridos[i_r][j_r]:
                sorted_val = "".join(
                    sorted(
                        [c for c in recorridos[i_r][j_r] if c in orden],
                        key=lambda c: orden[c],
                    )
                )
                recorridos[i_r][j_r] = sorted_val
    try:
        funciones.guardar_archivo_csv("PRACTICA1/recorridos.csv", recorridos)
    except Exception:
        pass
    return True


# Versión animada de BFS que actualiza globals para que la UI muestre progreso
def bfs_laberinto_animado(start, goal, datos_grid, screen, delay_ms=120):
    global alg_animating, alg_current, alg_frontier, alg_path, alg_tree_edges, alg_path_seq, alg_type
    from collections import deque

    alg_animating = True
    alg_current = None
    alg_frontier = set()
    alg_path = set()
    # Tipo de algoritmo y reinicio de estructuras de árbol
    alg_type = "BFS"
    alg_tree_edges = set()
    alg_path_seq = []
    globals()["alg_animating"] = alg_animating
    globals()["alg_type"] = alg_type
    globals()["alg_tree_edges"] = alg_tree_edges
    globals()["alg_path_seq"] = alg_path_seq

    si, sj = start
    gi, gj = goal
    visited = [[False] * len(datos_grid[0]) for _ in range(len(datos_grid))]
    parent = {}
    q = deque()
    q.append((si, sj))
    visited[si][sj] = True
    found = False
    # marcar inicio como descubierto (no marcar V sobre I)
    globals()["alg_frontier"] = set(q)
    # conjuntos ya reiniciados más arriba
    while q:
        i, j = q.popleft()
        alg_current = (i, j)
        alg_frontier = set(q)
        globals()["alg_current"] = alg_current
        globals()["alg_frontier"] = alg_frontier

        # Marcar visitado en recorridos (excepto I/F/X)
        try:
            actual = recorridos[i][j] if recorridos and i < len(recorridos) else ""
        except Exception:
            actual = ""
        if (
            actual is not None
            and "I" not in actual
            and "F" not in actual
            and "X" not in actual
        ):
            if "V" not in actual:
                try:
                    recorridos[i][j] = (actual or "") + "V"
                except Exception:
                    pass
        descubrir_alrededor(descubiertas_laberinto, i, j)

        # Actualizar UI
        pygame.event.pump()
        try:
            render_frame(screen)
        except Exception:
            pygame.display.flip()
        pygame.time.delay(delay_ms)

        if (i, j) == (gi, gj):
            found = True
            break

        # Expandir vecinos en orden (arriba, abajo, derecha, izquierda)
        vecinos = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        # Si hay 'O' en la celda actual, todavía expandimos todos sus vecinos (BFS explora todos)
        try:
            raw = recorridos[i][j] if recorridos and i < len(recorridos) else ""
        except Exception:
            raw = ""
        # Para BFS, simplemente encolar todos los vecinos válidos que no hayan sido visitados
        for di, dj in vecinos:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(datos_grid) and 0 <= nj < len(datos_grid[0]):
                if not visited[ni][nj] and datos_grid[ni][nj] == "1":
                    visited[ni][nj] = True
                    parent[(ni, nj)] = (i, j)
                    q.append((ni, nj))
                    try:
                        alg_tree_edges.add(((i, j), (ni, nj)))
                    except Exception:
                        pass
                    globals()["alg_tree_edges"] = alg_tree_edges

    if found:
        # reconstruir camino
        path = []
        cur = (gi, gj)
        while cur != (si, sj):
            path.append(cur)
            cur = parent.get(cur)
            if cur is None:
                path = []
                break
        if path:
            path.append((si, sj))
            path.reverse()
            alg_path = set(path)
            globals()["alg_path"] = alg_path
            # guardar secuencia completa para dibujo y export
            alg_path_seq = list(path)
            globals()["alg_path_seq"] = alg_path_seq
            # animar el camino final con mayor intensidad
            for step in path:
                alg_current = step
                globals()["alg_current"] = alg_current
                try:
                    render_frame(screen)
                except Exception:
                    pygame.display.flip()
                pygame.time.delay(delay_ms)
            aplicar_camino_en_recorridos(path)
            # Configurar toast de ruta por 6 segundos
            try:
                cells = [cell_name(*p) for p in path]
                dirs = []
                for idx in range(len(path) - 1):
                    dirs.append(dir_code(path[idx], path[idx + 1]))
                title = f"Ruta ideal ({alg_type})"
                globals()["route_toast"] = {
                    "title": title,
                    "cells": cells,
                    "dirs": dirs,
                }
                globals()["route_toast_until"] = pygame.time.get_ticks() + 6000
            except Exception:
                pass

    # finalizar animación
    alg_animating = False
    alg_current = None
    alg_frontier = set()
    globals()["alg_animating"] = alg_animating
    globals()["alg_current"] = alg_current
    globals()["alg_frontier"] = alg_frontier
    globals()["alg_path"] = alg_path
    try:
        prepare_tree_visual()
    except Exception:
        pass
    return found


def dfs_laberinto_animado(start, goal, datos_grid, screen, delay_ms=120):
    global alg_animating, alg_current, alg_frontier, alg_path, alg_tree_edges, alg_path_seq, alg_type
    alg_animating = True
    alg_current = None
    alg_frontier = set()
    alg_path = set()
    # Tipo de algoritmo y reinicio de estructuras de árbol
    alg_type = "DFS"
    alg_tree_edges = set()
    alg_path_seq = []
    globals()["alg_animating"] = alg_animating
    globals()["alg_type"] = alg_type
    globals()["alg_tree_edges"] = alg_tree_edges
    globals()["alg_path_seq"] = alg_path_seq
    si, sj = start
    gi, gj = goal
    visited = [[False] * len(datos_grid[0]) for _ in range(len(datos_grid))]
    parent = {}
    stack = [(si, sj, None)]  # (i,j, parent)
    visited[si][sj] = True
    found = False
    # Prioridad de movimientos solicitada: arriba, abajo, derecha, izquierda
    prioridad = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    alg_tree_edges = globals().get("alg_tree_edges", set())
    alg_path_seq = globals().get("alg_path_seq", [])
    while stack:
        # Permitir interacción básica durante la animación (botones Árbol/Ruta/Cubrir, salir)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                globals()["running"] = False
                alg_animating = False
                globals()["alg_animating"] = alg_animating
                return False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                alg_animating = False
                globals()["alg_animating"] = alg_animating
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                x, y = ev.pos
                _btn_tree = globals().get("btn_tree_rect")
                if _btn_tree and _btn_tree.collidepoint(x, y):
                    globals()["show_tree"] = not globals().get("show_tree", False)
                _btn_route = globals().get("btn_route_rect")
                if _btn_route and _btn_route.collidepoint(x, y):
                    globals()["show_route"] = not globals().get("show_route", False)
                _btn_cover = globals().get("btn_cover_rect")
                if _btn_cover and _btn_cover.collidepoint(x, y):
                    globals()["mostrar_cubierto"] = not globals().get(
                        "mostrar_cubierto", False
                    )
        i, j, came_from = stack.pop()
        alg_current = (i, j)
        # construir frontier set desde stack
        alg_frontier = set((x, y) for x, y, _ in stack)
        globals()["alg_current"] = alg_current
        globals()["alg_frontier"] = alg_frontier

        # Marcar visitado en recorridos (excepto I/F/X)
        try:
            actual = recorridos[i][j] if recorridos and i < len(recorridos) else ""
        except Exception:
            actual = ""
        if (
            actual is not None
            and "I" not in actual
            and "F" not in actual
            and "X" not in actual
        ):
            if "V" not in actual:
                try:
                    recorridos[i][j] = (actual or "") + "V"
                except Exception:
                    pass
        descubrir_alrededor(descubiertas_laberinto, i, j)

        pygame.event.pump()
        try:
            render_frame(screen)
        except Exception:
            pygame.display.flip()
        pygame.time.delay(delay_ms)

        if (i, j) == (gi, gj):
            found = True
            break

        # En cada celda (incluyendo O) intentar moverse en orden de prioridad, evitando volver a 'came_from' y celdas ya visitadas
        moved = False
        # prioridad ya definida más arriba: [(-1,0),(1,0),(0,1),(0,-1)]
        # Añadir en orden inverso para que LIFO tome la prioridad correcta
        for di, dj in reversed(prioridad):
            ni, nj = i + di, j + dj
            if 0 <= ni < len(datos_grid) and 0 <= nj < len(datos_grid[0]):
                if datos_grid[ni][nj] == "1" and not visited[ni][nj]:
                    # evitar regresar al padre
                    if came_from and (ni, nj) == came_from:
                        continue
                    visited[ni][nj] = True
                    parent[(ni, nj)] = (i, j)
                    stack.append((ni, nj, (i, j)))
                    try:
                        alg_tree_edges.add(((i, j), (ni, nj)))
                    except Exception:
                        pass
                    globals()["alg_tree_edges"] = alg_tree_edges
                    moved = True
        # Si no pudo moverse en prioridad (bloqueado), el stack puede contener otras ramas ya añadidas; DFS seguirá con ellas
        # Si la celda es O y hay múltiples opciones, el comportamiento sigue la prioridad de movimientos

    if found:
        path = []
        cur = (gi, gj)
        while cur != (si, sj):
            path.append(cur)
            cur = parent.get(cur)
            if cur is None:
                path = []
                break
        if path:
            path.append((si, sj))
            path.reverse()
            alg_path = set(path)
            globals()["alg_path"] = alg_path
            alg_path_seq = list(path)
            globals()["alg_path_seq"] = alg_path_seq
            for step in path:
                alg_current = step
                globals()["alg_current"] = alg_current
                try:
                    render_frame(screen)
                except Exception:
                    pygame.display.flip()
                pygame.time.delay(delay_ms)
            aplicar_camino_en_recorridos(path)
            # Configurar toast de ruta por 6 segundos
            try:
                cells = [cell_name(*p) for p in path]
                dirs = []
                for idx in range(len(path) - 1):
                    dirs.append(dir_code(path[idx], path[idx + 1]))
                title = f"Ruta ideal ({alg_type})"
                globals()["route_toast"] = {
                    "title": title,
                    "cells": cells,
                    "dirs": dirs,
                }
                globals()["route_toast_until"] = pygame.time.get_ticks() + 6000
            except Exception:
                pass

    alg_animating = False
    alg_current = None
    alg_frontier = set()
    globals()["alg_animating"] = alg_animating
    globals()["alg_current"] = alg_current
    globals()["alg_frontier"] = alg_frontier
    globals()["alg_path"] = alg_path
    try:
        prepare_tree_visual()
    except Exception:
        pass
    return found


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
                                                # Actualizar snapshot y recorridos_inicial
                                                try:
                                                    # Crear copia limpia sin V/O
                                                    clean = [
                                                        [
                                                            "".join(
                                                                [
                                                                    c
                                                                    for c in (
                                                                        recorridos[ii][
                                                                            jj
                                                                        ]
                                                                        if recorridos[
                                                                            ii
                                                                        ][jj]
                                                                        else ""
                                                                    )
                                                                    if c
                                                                    not in ("V", "O")
                                                                ]
                                                            )
                                                            for jj in range(
                                                                len(recorridos[0])
                                                            )
                                                        ]
                                                        for ii in range(len(recorridos))
                                                    ]
                                                    copy_recorridos = [
                                                        fila[:] for fila in clean
                                                    ]
                                                    recorridos_inicial = [
                                                        fila[:] for fila in recorridos
                                                    ]
                                                    globals()[
                                                        "copy_recorridos"
                                                    ] = copy_recorridos
                                                    globals()[
                                                        "recorridos_inicial"
                                                    ] = recorridos_inicial
                                                except Exception:
                                                    pass
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
            # Dibujar overlay de animación (búsqueda): casilla explorada/frontier/path en verde
            try:
                # Dibujar aristas del árbol de búsqueda
                if alg_tree_edges:
                    for a, b in alg_tree_edges:
                        (i1, j1), (i2, j2) = a, b
                        x1 = j1 * cell_size + cell_size + cell_size // 2
                        y1 = i1 * cell_size + cell_size + cell_size // 2
                        x2 = j2 * cell_size + cell_size + cell_size // 2
                        y2 = i2 * cell_size + cell_size + cell_size // 2
                # Dibujar aristas del camino final (más fuertes)
                if alg_path_seq:
                    for k in range(len(alg_path_seq) - 1):
                        (i1, j1) = alg_path_seq[k]
                        (i2, j2) = alg_path_seq[k + 1]
                        x1 = j1 * cell_size + cell_size + cell_size // 2
                        y1 = i1 * cell_size + cell_size + cell_size // 2
                        x2 = j2 * cell_size + cell_size + cell_size // 2
                        y2 = i2 * cell_size + cell_size + cell_size // 2
                if alg_animating:
                    if (i, j) in alg_frontier:
                        s = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        s.fill((0, 255, 0, 80))
                        surface.blit(s, (x, y))
                    if (i, j) == alg_current:
                        s2 = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        s2.fill((0, 200, 0, 140))
                        surface.blit(s2, (x, y))
                    if (i, j) in alg_path:
                        s3 = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        s3.fill((0, 180, 0, 200))
                        surface.blit(s3, (x, y))
            except Exception:
                pass
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


def render_frame(screen):
    """Dibuja la UI completa en pantalla usando el estado global actual."""
    # Dibujar UI base botones cargar
    screen.fill((0, 0, 0))
    ui_font = pygame.font.Font(None, 32)
    btn_lab_text = ui_font.render("Cargar Laberinto", True, (255, 255, 255))
    btn_ter_text = ui_font.render("Cargar Terreno", True, (255, 255, 255))
    btn_w = max(btn_lab_text.get_width(), btn_ter_text.get_width()) + 40
    btn_h = btn_lab_text.get_height() + 20
    panel_x = screen.get_width() - btn_w - 40
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

    # Botón Árbol de decisiones
    tree_text = f"Árbol: {'ON' if show_tree else 'OFF'}"
    tree_surface = ui_font.render(tree_text, True, (255, 255, 255))
    btn_tree_rect = pygame.Rect(panel_x, estado_base_y, btn_w, btn_h)
    interfaces.dibujar_boton(
        screen,
        btn_tree_rect,
        (60, 160, 80) if show_tree else (60, 60, 60),
        tree_surface,
    )
    estado_base_y = btn_tree_rect.bottom + 20

    # (Ruta ideal ya no tiene botón; se muestra como toast al terminar búsquedas)

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
                            if partes:
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
                            if partes:
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
        estado_lineas = [l for l in estado_lineas if not l.startswith("A:")]
        estado_lineas.append(vecinos_compacto)
    # (Ruta ideal larga se mostrará en un toast; no ocupar panel)
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
        pos_t = globals().get("pos_terreno", None)
        if pos_t:
            px = pos_t[1] * cell_size + cell_size
            py = pos_t[0] * cell_size + cell_size
            pygame.draw.circle(
                screen, (255, 120, 0), (px + cell_size // 2, py + cell_size // 2), 10
            )

    # Dibujar árbol de decisiones si está activado
    if show_tree:
        draw_decision_tree(screen)
    # Dibujar toast de ruta si está activo
    draw_route_toast(screen)

    pygame.display.flip()


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
                                if "X" not in actual:
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
                                # Actualizar snapshot tras modificación del mapa (usar versión limpia sin V/O)
                                try:
                                    clean = [
                                        [
                                            "".join(
                                                [
                                                    c
                                                    for c in (
                                                        recorridos[i][j]
                                                        if recorridos[i][j]
                                                        else ""
                                                    )
                                                    if c not in ("V", "O")
                                                ]
                                            )
                                            for j in range(len(recorridos[0]))
                                        ]
                                        for i in range(len(recorridos))
                                    ]
                                    copy_recorridos = [fila[:] for fila in clean]
                                    recorridos_inicial = [
                                        fila[:] for fila in recorridos
                                    ]
                                    globals()["copy_recorridos"] = copy_recorridos
                                    globals()["recorridos_inicial"] = recorridos_inicial
                                except Exception:
                                    pass
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
                                    # Marcar visita en marcas_terreno (similar a laberinto pero en terreno abierto)
                                    marcas = globals().get("marcas_terreno", None)
                                    if (
                                        marcas is not None
                                        and 0 <= ni < len(marcas)
                                        and 0 <= nj < len(marcas[0])
                                    ):
                                        actual = marcas[ni][nj] or ""
                                        # Añadir V si no existe
                                        if "X" not in actual:
                                            if "V" not in actual:
                                                marcas[ni][nj] = (actual or "") + "V"
                                        # Quitar X anterior
                                        for i_r in range(min(15, len(marcas))):
                                            for j_r in range(min(15, len(marcas[0]))):
                                                if (
                                                    marcas[i_r][j_r]
                                                    and "X" in marcas[i_r][j_r]
                                                ):
                                                    marcas[i_r][j_r] = marcas[i_r][
                                                        j_r
                                                    ].replace("X", "")
                                        # Poner X en la celda actual si no existe
                                        if "X" not in marcas[ni][nj]:
                                            marcas[ni][nj] = (
                                                marcas[ni][nj] or ""
                                            ) + "X"
                                        # Guardar cambios en archivo
                                        try:
                                            funciones.guardar_archivo_csv(
                                                "PRACTICA1/recorridos_terreno.csv",
                                                marcas,
                                            )
                                        except Exception:
                                            pass
                                    descubrir_alrededor(descubiertas_terreno, ni, nj)
                                    # Reset si llega a F (comportamiento igual al laberinto)
                                    if marcas_terreno and "F" in (
                                        marcas_terreno[ni][nj] or ""
                                    ):
                                        # Restaurar estado inicial desde snapshot copy_recorridos
                                        if (
                                            "copy_recorridos" in globals()
                                            and copy_recorridos
                                        ):
                                            for i_r in range(len(marcas_terreno)):
                                                for j_r in range(
                                                    len(marcas_terreno[0])
                                                ):
                                                    marcas_terreno[i_r][j_r] = (
                                                        copy_recorridos[i_r][j_r]
                                                    )
                                            # Guardar en CSV
                                            try:
                                                funciones.guardar_archivo_csv(
                                                    "PRACTICA1/recorridos_terreno.csv",
                                                    marcas_terreno,
                                                )
                                            except Exception:
                                                pass
                                        globals()["costo_acumulado"] = 0
                                        reset_estado_descubrimiento()
                                        # Reposicionar X en I (si existe) similar al laberinto
                                        for i_r in range(min(15, len(marcas_terreno))):
                                            for j_r in range(
                                                min(15, len(marcas_terreno[0]))
                                            ):
                                                if (
                                                    marcas_terreno[i_r][j_r]
                                                    and "I" in marcas_terreno[i_r][j_r]
                                                ):
                                                    if (
                                                        "X"
                                                        not in marcas_terreno[i_r][j_r]
                                                    ):
                                                        marcas_terreno[i_r][j_r] += "X"
                                                    try:
                                                        funciones.guardar_archivo_csv(
                                                            "PRACTICA1/recorridos_terreno.csv",
                                                            marcas_terreno,
                                                        )
                                                    except Exception:
                                                        pass
                                                    descubrir_alrededor(
                                                        descubiertas_terreno, i_r, j_r
                                                    )
                                                    globals()["pos_terreno"] = (
                                                        i_r,
                                                        j_r,
                                                    )
                                                    break
                                            else:
                                                continue
                                            break
                                        else:
                                            # No se encontró I, reposicionar en (0,0)
                                            globals()["pos_terreno"] = (0, 0)
                                            descubrir_alrededor(
                                                descubiertas_terreno, 0, 0
                                            )

                # Permitir ejecutar búsquedas en el laberinto con F5 (BFS) y F6 (DFS)
                # Solo cuando hay un personaje seleccionado y estamos en modo laberinto
                try:
                    if (
                        event.key == pygame.K_F5
                        and modo_mapa == "laberinto"
                        and personaje_seleccionado
                        and recorridos
                    ):
                        start = obtener_pos_actual_laberinto()
                        goal = None
                        for i_g in range(len(recorridos)):
                            for j_g in range(len(recorridos[0])):
                                if recorridos[i_g][j_g] and "F" in recorridos[i_g][j_g]:
                                    goal = (i_g, j_g)
                                    break
                            if goal:
                                break
                        if start and goal:
                            # Ejecutar versión animada (bloqueante en UI, con pequeño delay)
                            bfs_laberinto_animado(
                                start, goal, datos, screen, delay_ms=100
                            )
                    elif (
                        event.key == pygame.K_F6
                        and modo_mapa == "laberinto"
                        and personaje_seleccionado
                        and recorridos
                    ):
                        start = obtener_pos_actual_laberinto()
                        goal = None
                        for i_g in range(len(recorridos)):
                            for j_g in range(len(recorridos[0])):
                                if recorridos[i_g][j_g] and "F" in recorridos[i_g][j_g]:
                                    goal = (i_g, j_g)
                                    break
                            if goal:
                                break
                        if start and goal:
                            dfs_laberinto_animado(
                                start, goal, datos, screen, delay_ms=100
                            )
                except Exception:
                    pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            _btn_cover = globals().get("btn_cover_rect")
            if _btn_cover and _btn_cover.collidepoint(x, y):
                mostrar_cubierto = not mostrar_cubierto
                globals()["mostrar_cubierto"] = mostrar_cubierto
                continue
            _btn_tree = globals().get("btn_tree_rect")
            if _btn_tree and _btn_tree.collidepoint(x, y):
                show_tree = not show_tree
                globals()["show_tree"] = show_tree
                # Si se activa y no hay preparación previa, intenta preparar con estado actual
                if show_tree and (not tree_node_pos or not tree_edges_cached):
                    try:
                        prepare_tree_visual()
                    except Exception:
                        pass
                continue
            # (Ruta: botón eliminado, se muestra como toast)
            # Detectar clicks en botones de carga
            _btn_lab = globals().get("btn_laberinto_rect")
            if _btn_lab and _btn_lab.collidepoint(x, y):
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
            elif globals().get("btn_terreno_rect") and globals()[
                "btn_terreno_rect"
            ].collidepoint(x, y):
                cargar_terreno()
                modo_valores = False
                globals()["modo_valores"] = modo_valores
            elif globals().get("btn_personaje_rect") and globals()[
                "btn_personaje_rect"
            ].collidepoint(x, y):
                # Abrir menú modal y luego continuar sin propagar el clic
                abrir_menu_personaje(
                    screen, panel_x, btn_personaje_rect, btn_w, personajes, modo_mapa
                )
            elif globals().get("btn_modificar_rect") and globals()[
                "btn_modificar_rect"
            ].collidepoint(x, y):
                modificar_mapa = not modificar_mapa
                if modificar_mapa:
                    modo_valores = False
                globals()["modificar_mapa"] = modificar_mapa
                globals()["modo_valores"] = modo_valores
            elif (
                globals().get("btn_valores_rect")
                and modo_mapa == "laberinto"
                and globals()["btn_valores_rect"].collidepoint(x, y)
            ):
                modo_valores = not modo_valores
                if modo_valores:
                    modificar_mapa = False
                globals()["modo_valores"] = modo_valores
                globals()["modificar_mapa"] = modificar_mapa
            # Nueva condición para botón valores en terreno
            elif globals().get("btn_valores_rect") and globals()[
                "btn_valores_rect"
            ].collidepoint(x, y):
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
                                                    # Actualizar snapshot (copy_recorridos) para que el reset use la última modificación
                                                    try:
                                                        # Crear copia limpia quitando marcas transitorias V y O
                                                        clean = [
                                                            [
                                                                "".join(
                                                                    [
                                                                        c
                                                                        for c in (
                                                                            recorridos[
                                                                                i
                                                                            ][j]
                                                                            if recorridos[
                                                                                i
                                                                            ][
                                                                                j
                                                                            ]
                                                                            else ""
                                                                        )
                                                                        if c
                                                                        not in (
                                                                            "V",
                                                                            "O",
                                                                        )
                                                                    ]
                                                                )
                                                                for j in range(
                                                                    len(recorridos[0])
                                                                )
                                                            ]
                                                            for i in range(
                                                                len(recorridos)
                                                            )
                                                        ]
                                                        copy_recorridos = [
                                                            fila[:] for fila in clean
                                                        ]
                                                        recorridos_inicial = [
                                                            fila[:]
                                                            for fila in recorridos
                                                        ]
                                                        globals()[
                                                            "copy_recorridos"
                                                        ] = copy_recorridos
                                                        globals()[
                                                            "recorridos_inicial"
                                                        ] = recorridos_inicial
                                                    except Exception:
                                                        pass
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
                                                    # Guardar cambios en archivo de recorridos de terreno
                                                    try:
                                                        funciones.guardar_archivo_csv(
                                                            "PRACTICA1/recorridos_terreno.csv",
                                                            marcas_terreno,
                                                        )
                                                    except Exception:
                                                        pass
                                                    # Actualizar snapshot (copy_recorridos) y recorridos_inicial
                                                    try:
                                                        clean = [
                                                            [
                                                                "".join(
                                                                    [
                                                                        c
                                                                        for c in (
                                                                            marcas_terreno[
                                                                                i
                                                                            ][
                                                                                j
                                                                            ]
                                                                            if marcas_terreno[
                                                                                i
                                                                            ][
                                                                                j
                                                                            ]
                                                                            else ""
                                                                        )
                                                                        if c
                                                                        not in (
                                                                            "V",
                                                                            "O",
                                                                        )
                                                                    ]
                                                                )
                                                                for j in range(
                                                                    len(
                                                                        marcas_terreno[
                                                                            0
                                                                        ]
                                                                    )
                                                                )
                                                            ]
                                                            for i in range(
                                                                len(marcas_terreno)
                                                            )
                                                        ]
                                                        copy_recorridos = [
                                                            fila[:] for fila in clean
                                                        ]
                                                        recorridos_inicial = [
                                                            fila[:]
                                                            for fila in marcas_terreno
                                                        ]
                                                        globals()[
                                                            "copy_recorridos"
                                                        ] = copy_recorridos
                                                        globals()[
                                                            "recorridos_inicial"
                                                        ] = recorridos_inicial
                                                    except Exception:
                                                        pass
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

    # Botón Árbol de decisiones
    tree_text = f"Árbol: {'ON' if show_tree else 'OFF'}"
    tree_surface = ui_font.render(tree_text, True, (255, 255, 255))
    btn_tree_rect = pygame.Rect(panel_x, estado_base_y, btn_w, btn_h)
    interfaces.dibujar_boton(
        screen,
        btn_tree_rect,
        (60, 160, 80) if show_tree else (60, 60, 60),
        tree_surface,
    )
    estado_base_y = btn_tree_rect.bottom + 20

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

    # Dibujar árbol de decisiones si está activado
    if show_tree:
        draw_decision_tree(screen)

    # Dibujar toast de ruta si está activo
    try:
        draw_route_toast(screen)
    except Exception:
        pass

    pygame.display.flip()

pygame.quit()
