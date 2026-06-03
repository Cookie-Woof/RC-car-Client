import pygame
import sys
import logging

import dashboard
import driver
import constants

class ImageButton:
    def __init__(self, pos, size, img_normal_path, img_pressed_path):
        self.rect        = pygame.Rect(pos, size)
        self.img_normal  = self._load(img_normal_path, size)
        self.img_pressed = self._load(img_pressed_path, size)
        self.pressing    = False

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


def draw_info_popup(surface, font, small_font):
    cfg_dash = constants.Graphics.Dashboard
    cfg_cockpit = constants.Graphics.DriverCockpit
    
    overlay = pygame.Surface((constants.Graphics.DriverCockpit.WIDTH, constants.Graphics.DriverCockpit.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(60, 70, 566, 240)
    pygame.draw.rect(surface, (30, 30, 40), box, border_radius=10)
    pygame.draw.rect(surface, (180, 180, 180), box, width=1, border_radius=10)

    title = font.render("INFO", True, (255, 255, 255))
    surface.blit(title, (box.x + 20, box.y + 14))

    for i, line in enumerate(constants.INFO_TEXT):
        txt = small_font.render(line, True, (180, 180, 180))
        surface.blit(txt, (box.x + 20, box.y + 55 + i * 26))

    hint = small_font.render("Click anywhere or press ESC to close", True, (80, 80, 90))
    surface.blit(hint, (box.x + 20, box.y + 208))


def main():
    pygame.init()
    
    cfg_cockpit = constants.Graphics.DriverCockpit
    cfg_btn = constants.Graphics.Buttons
    
    screen = pygame.display.set_mode((cfg_cockpit.WIDTH, cfg_cockpit.HEIGHT))
    pygame.display.set_caption(constants.TITLE)
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("couriernew", 22, bold=True)
    small_font = pygame.font.SysFont("couriernew", 15)

    try:
        bg = pygame.image.load(constants.BG_IMAGE).convert()
        bg = pygame.transform.scale(bg, (cfg_cockpit.WIDTH, cfg_cockpit.HEIGHT))
    except Exception:
        bg = None
        logging.warning("no background found!")

    btn_driver   = ImageButton(constants.POS_DRIVER,   constants.SIZE_MAIN,   cfg_btn.BTN_DRIVER_NORMAL,   cfg_btn.BTN_DRIVER_PRESSED)
    btn_engineer = ImageButton(constants.POS_ENGINEER, constants.SIZE_MAIN,   cfg_btn.BTN_ENGINEER_NORMAL, cfg_btn.BTN_ENGINEER_PRESSED)
    btn_exit     = ImageButton(constants.POS_EXIT,     constants.SIZE_BOTTOM, cfg_btn.BTN_EXIT_NORMAL,     cfg_btn.BTN_EXIT_PRESSED)
    btn_info     = ImageButton(constants.POS_INFO,     constants.SIZE_BOTTOM, cfg_btn.BTN_INFO_NORMAL,     cfg_btn.BTN_INFO_PRESSED)

    buttons   = [btn_driver, btn_engineer, btn_exit, btn_info]
    show_info = False

    while True:
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((15, 15, 20))

        for btn in buttons:
            btn.draw(screen)

        if show_info:
            draw_info_popup(screen, font, small_font)

        pygame.display.flip()
        clock.tick(constants.Graphics.FPS)

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
                for btn in buttons:
                    btn.handle_event(event)
                continue

            if btn_exit.handle_event(event):
                pygame.quit()
                sys.exit()

            if btn_info.handle_event(event):
                show_info = True

            if btn_driver.handle_event(event):
                logging.info("Driver selected")
                driver.run()
                screen = pygame.display.set_mode((cfg_cockpit.WIDTH, cfg_cockpit.HEIGHT))
                pygame.display.set_caption(constants.TITLE)
                
            if btn_engineer.handle_event(event):
                logging.info("Engineer selected - Launching Live Metrics Window")
                dashboard.run()
                screen = pygame.display.set_mode((cfg_cockpit.WIDTH, cfg_cockpit.HEIGHT))
                pygame.display.set_caption(constants.TITLE)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    main()