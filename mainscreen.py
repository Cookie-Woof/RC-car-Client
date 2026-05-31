"""
mainscreen.py -
the main screen opens up as soon as you start the program letting
you choose your role for the game equiped with working buttons.
"""

import pygame
import sys
import logging

# ── Window ────────────────────────────────────────────────────
WIDTH, HEIGHT = 686, 386
FPS           = 60
TITLE         = "Mazda Miata The Game"

# ── buttons and main screen location ─────────
BG_IMAGE            = "mainscreen/background.jpg"

BTN_DRIVER_NORMAL   = "mainscreen/driver_normal.jpg"
BTN_DRIVER_PRESSED  = "mainscreen/driver_pressed.jpg"

BTN_ENGINEER_NORMAL = "mainscreen/engineer_normal.jpg"
BTN_ENGINEER_PRESSED= "mainscreen/engineer_pressed.jpg"

BTN_EXIT_NORMAL     = "mainscreen/exit_normal.jpg"
BTN_EXIT_PRESSED    = "mainscreen/exit_pressed.jpg"

BTN_INFO_NORMAL     = "mainscreen/info_normal.jpg"
BTN_INFO_PRESSED    = "mainscreen/info_pressed.jpg"

# ── Button Sizes (match your images) ─────────────────────────
SIZE_MAIN   = (160, 55)    # Driver, Engineer
SIZE_BOTTOM = (100, 45)    # Exit, Info

# ── Button Positions (matching your screenshot layout) ────────
POS_DRIVER   = (510, 260)
POS_ENGINEER = (510, 320)
POS_EXIT     = (20,  330)
POS_INFO     = (130, 330)

# ── Info text ─────────────────────────────────────────────────
INFO_TEXT = [
    "Welcome to track! and yes, you pulled up in a Miata.",
    "Bold choice. Driver or Engineer, your call!",
    "Push it to the limit or build it to perfection.",
    "Either way this car is ready to prove a point.",
    "Small? Sure. Slow? Not a chance.",
    "Lights are out, let's see what you've got!",
]

# ── Colors ────────────────────────────────────────────────────
BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (180, 180, 180)
DARK_GRAY = (30,  30,  40)
OVERLAY   = (0,   0,   0, 190)


# ── Image Button ─────────────────────────────────────────────
class ImageButton:
    def __init__(self, pos, size, img_normal_path, img_pressed_path):
        self.rect       = pygame.Rect(pos, size)
        self.img_normal = self._load(img_normal_path, size)
        self.img_pressed= self._load(img_pressed_path, size)
        self.pressing   = False

    def _load(self, path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception:
            logging.warning("No buttons were found!")
            surf = pygame.Surface(size)
            surf.fill((60, 60, 70))
            return surf

    def draw(self, surface):
        img = self.img_pressed if self.pressing else self.img_normal
        surface.blit(img, self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressing = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            clicked = self.pressing and self.rect.collidepoint(event.pos)
            self.pressing = False
            return clicked
        return False


# ── Info ────────────────────────────────────────────────
def draw_info_popup(surface, font, small_font):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(60, 70, 566, 240)
    pygame.draw.rect(surface, DARK_GRAY, box, border_radius=10)
    pygame.draw.rect(surface, GRAY, box, width=1, border_radius=10)

    title = font.render("INFO", True, WHITE)
    surface.blit(title, (box.x + 20, box.y + 14))

    for i, line in enumerate(INFO_TEXT):
        txt = small_font.render(line, True, GRAY)
        surface.blit(txt, (box.x + 20, box.y + 55 + i * 26))

    hint = small_font.render("Click anywhere or press ESC to close", True, (80, 80, 90))
    surface.blit(hint, (box.x + 20, box.y + 208))


# ── Main ──────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("couriernew", 22, bold=True)
    small_font = pygame.font.SysFont("couriernew", 15)

    # Load background
    try:
        bg = pygame.image.load(BG_IMAGE).convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except Exception:
        bg = None
        logging.warning("no background found!")

    # Create buttons
    btn_driver   = ImageButton(POS_DRIVER,   SIZE_MAIN,   BTN_DRIVER_NORMAL,   BTN_DRIVER_PRESSED)
    btn_engineer = ImageButton(POS_ENGINEER, SIZE_MAIN,   BTN_ENGINEER_NORMAL, BTN_ENGINEER_PRESSED)
    btn_exit     = ImageButton(POS_EXIT,     SIZE_BOTTOM, BTN_EXIT_NORMAL,     BTN_EXIT_PRESSED)
    btn_info     = ImageButton(POS_INFO,     SIZE_BOTTOM, BTN_INFO_NORMAL,     BTN_INFO_PRESSED)

    buttons   = [btn_driver, btn_engineer, btn_exit, btn_info]
    show_info = False

    while True:
        # Background
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((15, 15, 20))

        # Draw buttons
        for btn in buttons:
            btn.draw(screen)

        # Info popup
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    show_info = False
                # Still need to clear pressing state on buttons
                for btn in buttons:
                    btn.handle_event(event)
                continue

            if btn_exit.handle_event(event):
                pygame.quit()
                sys.exit()

            if btn_info.handle_event(event):
                show_info = True

            if btn_driver.handle_event(event):
                logging.info("Driver selected")      # hook Driver screen here

            if btn_engineer.handle_event(event):
                logging.info("Engineer selected")    # hook Engineer screen here


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


if __name__ == "__main__":
    main()