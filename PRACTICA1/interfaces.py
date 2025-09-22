import pygame


def mostrar_mensaje(texto, screen):
    font = pygame.font.Font(None, 36)
    mensaje = font.render(texto, True, (255, 255, 255))
    bg = pygame.Surface(
        (mensaje.get_width() + 20, mensaje.get_height() + 20), pygame.SRCALPHA
    )
    bg.fill((30, 30, 30, 220))
    x = screen.get_width() // 2 - mensaje.get_width() // 2 - 10
    y = 40
    screen.blit(bg, (x, y))
    screen.blit(mensaje, (screen.get_width() // 2 - mensaje.get_width() // 2, 50))
    pygame.display.update(pygame.Rect(x, y, bg.get_width(), bg.get_height()))
    pygame.time.delay(900)


def dibujar_boton(surface, rect, color, texto_surface):
    pygame.draw.rect(surface, color, rect, border_radius=10)
    surface.blit(texto_surface, (rect.x + 15, rect.y + 10))


def dibujar_menu_personaje(surface, menu_x, menu_y, menu_w, menu_h, personajes):
    pygame.draw.rect(
        surface, (40, 40, 40), (menu_x, menu_y, menu_w, menu_h), border_radius=10
    )
    menu_font = pygame.font.Font(None, 36)
    for idx, (nombre, pasos) in enumerate(personajes):
        btn_rect = pygame.Rect(menu_x + 20, menu_y + 20 + idx * 40, 180, 36)
        pygame.draw.rect(surface, (70, 130, 180), btn_rect, border_radius=8)
        btn_text = menu_font.render(f"{nombre} ({pasos})", True, (255, 255, 255))
        surface.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 5))


def dibujar_menu_valores(
    surface, menu_x, menu_y, menu_w, menu_h, valores_lista, celda_actual
):
    pygame.draw.rect(
        surface, (40, 40, 40), (menu_x, menu_y, menu_w, menu_h), border_radius=10
    )
    menu_font = pygame.font.Font(None, 36)
    for idx, val in enumerate(valores_lista):
        btn_rect = pygame.Rect(menu_x + 20, menu_y + 20 + idx * 40, 60, 36)
        color_btn = (255, 215, 0) if val in celda_actual else (70, 130, 180)
        pygame.draw.rect(surface, color_btn, btn_rect, border_radius=8)
        btn_text = menu_font.render(val, True, (255, 255, 255))
        surface.blit(btn_text, (btn_rect.x + 15, btn_rect.y + 5))


def dibujar_vecinos(surface, vecinos_texto, screen_height):
    font_vecino = pygame.font.Font(None, 16)
    vecino_surface = font_vecino.render(vecinos_texto, True, (255, 255, 0))
    bg_width = vecino_surface.get_width() + 20
    bg_height = vecino_surface.get_height() + 10
    bg_x = 35
    bg_y = screen_height - 45
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    bg_surface.fill((30, 30, 30, 250))
    surface.blit(bg_surface, (bg_x, bg_y))
    surface.blit(vecino_surface, (bg_x + 10, bg_y + 5))
