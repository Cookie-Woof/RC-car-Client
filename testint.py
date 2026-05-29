


"""
menu.py
Main menu window for the RC Car controller.
Shows Engineer / Driver role buttons, plus Exit and Info.
"""

import pygame
import sys

# ── Config ────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 400
FPS           = 60
TITLE         = "RC Car Controller"

# Colors
BG          = (15, 15, 20)
WHITE       = (255, 255, 255)
GRAY        = (160, 160, 160)
DARK_GRAY   = (40, 40, 50)
ACCENT_BLUE = (50, 120, 255)
ACCENT_RED  = (220, 60, 60)
HOVER_BLUE  = (80, 150, 255)
HOVER_RED   = (240, 90, 90)
OVERLAY     = (0, 0, 0, 180)

INFO_TEXT = "Info text goes here.\nReplace this with your own description."

# ── Button class ──────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, label, color, hover_color):
        self.rect        = pygame.Rect(x, y, w, h)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color

    def draw(self, surface, font):
        mouse = pygame.mouse.get_pos()
        col   = self.hover_color if self.rect.collidepoint(mouse) else self.color

        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        text = font.render(self.label, True, WHITE)
        tr   = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Info popup ────────────────────────────────────────────────
def draw_info_popup(surface, font, small_font):
    # Dim background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    # Popup box
    box = pygame.Rect(80, 80, 440, 240)
    pygame.draw.rect(surface, DARK_GRAY, box, border_radius=12)
    pygame.draw.rect(surface, GRAY, box, width=1, border_radius=12)

    # Title
    title = font.render("Info", True, WHITE)
    surface.blit(title, (box.x + 20, box.y + 16))

    # Body text (supports \n)
    lines = INFO_TEXT.split("\n")
    for i, line in enumerate(lines):
        txt = small_font.render(line, True, GRAY)
        surface.blit(txt, (box.x + 20, box.y + 60 + i * 28))

    # Close hint
    hint = small_font.render("Press ESC or click anywhere to close", True, (90, 90, 100))
    surface.blit(hint, (box.x + 20, box.y + 200))


# ── Main ──────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("segoeui", 28, bold=True)
    small_font = pygame.font.SysFont("segoeui", 20)
    title_font = pygame.font.SysFont("segoeui", 42, bold=True)

    # Main buttons (centered)
    btn_w, btn_h = 200, 65
    gap          = 30
    total_w      = btn_w * 2 + gap
    start_x      = (WIDTH - total_w) // 2
    center_y     = HEIGHT // 2 - btn_h // 2

    btn_engineer = Button(start_x,              center_y, btn_w, btn_h, "Engineer", ACCENT_BLUE, HOVER_BLUE)
    btn_driver   = Button(start_x + btn_w + gap, center_y, btn_w, btn_h, "Driver",   ACCENT_RED,  HOVER_RED)

    # Bottom buttons
    btn_exit = Button(20,          HEIGHT - 60, 120, 42, "Exit", (60, 60, 70), (90, 90, 100))
    btn_info = Button(WIDTH - 140, HEIGHT - 60, 120, 42, "Info", (60, 60, 70), (90, 90, 100))

    show_info = False

    while True:
        screen.fill(BG)

        # Title
        title_surf = title_font.render("RC Car Controller", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 120)))

        # Subtitle
        sub = small_font.render("Select your role to continue", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 165)))

        # Draw buttons
        btn_engineer.draw(screen, font)
        btn_driver.draw(screen, font)
        btn_exit.draw(screen, font)
        btn_info.draw(screen, font)

        # Info popup on top
        if show_info:
            draw_info_popup(screen, font, small_font)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if show_info:
                    show_info = False

            if show_info:
                # Any click closes the popup
                if event.type == pygame.MOUSEBUTTONDOWN:
                    show_info = False
                continue

            if btn_exit.is_clicked(event):
                pygame.quit()
                sys.exit()

            if btn_info.is_clicked(event):
                show_info = True

            if btn_engineer.is_clicked(event):
                print("Engineer selected")   # hook your Engineer screen here

            if btn_driver.is_clicked(event):
                print("Driver selected")     # hook your Driver screen here


if __name__ == "__main__":
    main()