import pygame
import sys
import time
import socket
import struct
from collections import deque
import constants

def panel(surf, rect, title):
    cfg = constants.Graphics.Dashboard
    pygame.draw.rect(surf, cfg.PANEL_COLOR, rect)
    pygame.draw.rect(surf, cfg.BORDER_COLOR, rect, 2)
    surf.blit(FONT_SM.render(title, True, cfg.TEXT_DIM), (rect.x + 10, rect.y + 8))

def bar(surf, rect, val, lo, hi, color):
    cfg = constants.Graphics.Dashboard
    pygame.draw.rect(surf, cfg.GAUGE_BG, rect)
    pygame.draw.rect(surf, cfg.BORDER_DIM, rect, 1)
    pct  = max(0, min(1, (val - lo) / (hi - lo)))
    fill = pygame.Rect(rect.x, rect.y, int(rect.w * pct), rect.h)
    if fill.w > 0:
        pygame.draw.rect(surf, color, fill)

def graph(surf, rect, history, lo, hi, color, centerline=False):
    cfg = constants.Graphics.Dashboard
    pygame.draw.rect(surf, cfg.GAUGE_BG, rect)
    pygame.draw.rect(surf, cfg.BORDER_DIM, rect, 1)
    if centerline:
        cy = rect.y + rect.h // 2
        for x in range(rect.x, rect.x + rect.w, 8):
            pygame.draw.line(surf, cfg.BORDER_COLOR, (x, cy), (x + 4, cy), 1)
    if len(history) < 2:
        return
    pts = []
    for i, v in enumerate(history):
        x   = rect.x + int(i / (len(history) - 1) * rect.w)
        pct = max(0, min(1, (v - lo) / (hi - lo)))
        y   = rect.y + rect.h - int(pct * rect.h)
        pts.append((x, max(rect.y + 1, min(rect.y + rect.h - 1, y))))
    pygame.draw.lines(surf, color, False, pts, 2)
    surf.blit(FONT_SM.render(str(lo),  True, cfg.TEXT_DIM), (rect.x + 3, rect.y + rect.h - 14))
    surf.blit(FONT_SM.render(str(hi),  True, cfg.TEXT_DIM), (rect.x + 3, rect.y + 2))
    surf.blit(FONT_SM.render("NOW",    True, cfg.TEXT_DIM), (rect.x + rect.w - 30, rect.y + rect.h - 14))


class Dashboard:
    def __init__(self, screen):
        self.screen     = screen
        self.start_time = time.time()
        self.battery    = 100.0
        
        max_pts         = constants.Graphics.Dashboard.HISTORY_SECS * constants.Graphics.FPS
        self.spd_hist   = deque(maxlen=max_pts)
        self.ang_hist   = deque(maxlen=max_pts)
        
        self._init_layout()

    def _init_layout(self):
        W, H    = self.screen.get_size()
        PAD     = 14
        LW      = 290          
        RW      = W - LW - PAD * 3
        TOP     = 46
        PH      = (H - TOP - PAD * 5) // 4   
        GH      = (H - TOP - PAD * 3) // 2   
        
        self.rect_steer   = pygame.Rect(PAD, TOP, LW, PH)
        self.rect_speed   = pygame.Rect(PAD, TOP + PH + PAD, LW, PH)
        self.rect_battery = pygame.Rect(PAD, TOP + (PH + PAD) * 2, LW, PH)
        self.rect_conn    = pygame.Rect(PAD, TOP + (PH + PAD) * 3, LW, PH)
        
        gx = PAD * 2 + LW
        self.rect_g1_panel = pygame.Rect(gx, TOP, RW, GH)
        self.rect_g1_inner = pygame.Rect(gx + 10, TOP + 24, RW - 20, GH - 34)
        
        self.rect_g2_panel = pygame.Rect(gx, TOP + GH + PAD, RW, GH)
        self.rect_g2_inner = pygame.Rect(gx + 10, TOP + GH + PAD + 24, RW - 20, GH - 34)

    def draw(self, angle, speed, throttle):
        cfg = constants.Graphics.Dashboard
        self.battery = max(0, self.battery - 0.003)
        self.spd_hist.append(speed)
        self.ang_hist.append(angle)

        self.screen.fill(cfg.BG_COLOR)
        
        self._draw_header()
        self._draw_steering(angle)
        self._draw_speed(speed)
        self._draw_battery()
        self._draw_connection()
        self._draw_graphs()

        pygame.display.flip()

    def _draw_header(self):
        cfg = constants.Graphics.Dashboard
        W, _ = self.screen.get_size()
        PAD = 14
        self.screen.blit(FONT_HDR.render("ENGINEER DASHBOARD", True, cfg.TEXT_ACCENT), (PAD, PAD))
        elapsed = int(time.time() - self.start_time)
        sess    = FONT_SM.render(f"SESSION  {elapsed//60:02d}:{elapsed%60:02d}", True, cfg.TEXT_DIM)
        self.screen.blit(sess, (W - sess.get_width() - PAD, PAD + 4))
        hint = FONT_SM.render("ESC: back  |  MONITORING MODE ACTIVE  |  READONLY", True, cfg.BORDER_COLOR)
        self.screen.blit(hint, (PAD, 30))
        pygame.draw.line(self.screen, cfg.BORDER_DIM, (PAD, 42), (W - PAD, 42), 1)

    def _draw_steering(self, angle):
        cfg = constants.Graphics.Dashboard
        r = self.rect_steer
        panel(self.screen, r, "STEERING ANGLE")
        val_surf = FONT_LG.render(str(angle), True, cfg.TEXT_PRIMARY)
        self.screen.blit(val_surf, (r.x + 16, r.y + 22))
        unit_x = r.x + 16 + val_surf.get_width() + 6
        self.screen.blit(FONT_SM.render("DEG", True, cfg.TEXT_DIM), (unit_x, r.y + 36))
        
        br = pygame.Rect(r.x + 16, r.y + r.h - 32, r.w - 32, 12)
        bar(self.screen, br, angle, 80, 130, cfg.TEXT_ACCENT)
        
        cx = br.x + br.w // 2
        pygame.draw.line(self.screen, cfg.BORDER_COLOR, (cx, br.y - 3), (cx, br.y + br.h + 3), 1)
        
        pct    = (angle - 80) / 50
        needle = br.x + int(pct * br.w)
        pygame.draw.rect(self.screen, cfg.TEXT_ACCENT, (needle - 2, br.y - 2, 4, br.h + 4))
        
        self.screen.blit(FONT_SM.render("L", True, cfg.TEXT_DIM), (br.x, br.y + br.h + 3))
        self.screen.blit(FONT_SM.render("CTR", True, cfg.TEXT_DIM), (cx - 12, br.y + br.h + 3))
        self.screen.blit(FONT_SM.render("R", True, cfg.TEXT_DIM), (br.x + br.w - 8, br.y + br.h + 3))

    def _draw_speed(self, speed):
        cfg = constants.Graphics.Dashboard
        r = self.rect_speed
        panel(self.screen, r, "SPEED")
        val_surf = FONT_LG.render(f"{speed:.1f}", True, cfg.TEXT_PRIMARY)
        self.screen.blit(val_surf, (r.x + 16, r.y + 22))
        unit_x = r.x + 16 + val_surf.get_width() + 6
        self.screen.blit(FONT_SM.render("KM/H", True, cfg.TEXT_DIM), (unit_x, r.y + 36))
        
        sb = pygame.Rect(r.x + 16, r.y + r.h - 32, r.w - 32, 12)
        bar(self.screen, sb, speed, 0, constants.Physics.SPEED_MAX, cfg.GAUGE_FILL_LOW)
        self.screen.blit(FONT_SM.render("0", True, cfg.TEXT_DIM), (sb.x, sb.y + sb.h + 3))
        mx = FONT_SM.render(f"{constants.Physics.SPEED_MAX}", True, cfg.TEXT_DIM)
        self.screen.blit(mx, (sb.x + sb.w - mx.get_width(), sb.y + sb.h + 3))

    def _draw_battery(self):
        cfg = constants.Graphics.Dashboard
        r = self.rect_battery
        panel(self.screen, r, "BATTERY")
        bat  = int(self.battery)
        bcol = cfg.TEXT_GREEN if bat > 40 else (cfg.TEXT_YELLOW if bat > 20 else cfg.TEXT_ACCENT)
        self.screen.blit(FONT_LG.render(f"{bat}%", True, bcol), (r.x + 10, r.y + 22))
        bw = (r.w - 20 - 16) // 5
        for i in range(5):
            bx     = r.x + 10 + i * (bw + 4)
            by     = r.y + r.h - 32
            filled = (i * 20) < bat
            pygame.draw.rect(self.screen, bcol if filled else cfg.GAUGE_BG, (bx, by, bw, 12))
            pygame.draw.rect(self.screen, cfg.BORDER_DIM, (bx, by, bw, 12), 1)

    def _draw_connection(self):
        cfg = constants.Graphics.Dashboard
        r = self.rect_conn
        panel(self.screen, r, "CONNECTION")
        for i, (k, v, col) in enumerate([
            ("STATUS", "ONLINE",       cfg.TEXT_GREEN),
            ("PING",   "12 MS",        cfg.TEXT_PRIMARY),
            ("ESP32",  constants.Network.ESP_IP,  cfg.TEXT_ACCENT),
        ]):
            ry = r.y + 26 + i * 20
            self.screen.blit(FONT_SM.render(k, True, cfg.TEXT_DIM), (r.x + 10, ry))
            vt = FONT_SM.render(v, True, col)
            self.screen.blit(vt, (r.x + r.w - vt.get_width() - 10, ry))

    def _draw_graphs(self):
        cfg = constants.Graphics.Dashboard
        panel(self.screen, self.rect_g1_panel, f"SPEED / TIME  (20s)  max {constants.Physics.SPEED_MAX} km/h")
        graph(self.screen, self.rect_g1_inner, self.spd_hist, 0, constants.Physics.SPEED_MAX, cfg.GAUGE_FILL_LOW)

        panel(self.screen, self.rect_g2_panel, "STEERING / TIME  (20s)")
        graph(self.screen, self.rect_g2_inner, self.ang_hist, 80, 130, cfg.TEXT_ACCENT, centerline=True)


def run():
    global FONT_SM, FONT_MD, FONT_LG, FONT_HDR
    pygame.init()
    FONT_SM  = pygame.font.SysFont("couriernew", 13, bold=True)
    FONT_MD  = pygame.font.SysFont("couriernew", 16, bold=True)
    FONT_LG  = pygame.font.SysFont("couriernew", 32, bold=True)
    FONT_HDR = pygame.font.SysFont("couriernew", 18, bold=True)

    screen = pygame.display.set_mode((constants.Graphics.WINDOW_WIDTH, constants.Graphics.WINDOW_HEIGHT))
    pygame.display.set_caption(constants.Graphics.MAIN_SCREEN)

    clock   = pygame.time.Clock()
    dash    = Dashboard(screen)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        server_socket.bind(("0.0.0.0", constants.Network.UDP_PORT)) 
        server_socket.setblocking(False)       

        angle, throttle, speed = 110, 0.0, 0.0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            while True:
                try:
                    data, addr = server_socket.recvfrom(1024)
                    if len(data) == 12:
                        angle, throttle, speed = struct.unpack("iff", data)
                except BlockingIOError:
                    break

            dash.draw(angle, speed, throttle)
            clock.tick(constants.Graphics.FPS)
            
    finally:
        server_socket.close()

if __name__ == "__main__":
    run()