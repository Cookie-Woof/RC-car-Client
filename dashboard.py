"""
engineer.py
Engineer dashboard — steering angle, speed, battery, connection + live graphs.

Controls (keyboard OR Xbox controller):
  Keyboard  : LEFT / RIGHT arrows = steer | UP = throttle | ESC = back
  Xbox      : Left stick X = steer | Right trigger = throttle | B = back
"""

import pygame
import sys
import time
import math
import random
from collections import deque

# ── Config ────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 540
FPS           = 30
TITLE         = "Engineer Dashboard"
HISTORY_SECS  = 20
ESP32_IP      = "192.168.50.223"

# ── Motor constants ───────────────────────────────────────────
MOTOR_VOLTAGE = 6.0
MOTOR_RPM     = 1500.0
KV            = MOTOR_RPM / MOTOR_VOLTAGE   # 250 RPM/V
GEAR_RATIO    = 3.23
WHEEL_R       = 0.02                        # meters

RPM_MAX       = (MOTOR_VOLTAGE * KV) / GEAR_RATIO
V_MAX_MS      = (RPM_MAX * 2 * math.pi * WHEEL_R) / 60
SPEED_MAX     = round(V_MAX_MS * 3.6, 1)   # ~3.5 km/h

def calc_speed(volts):
    rpm  = (volts * KV) / GEAR_RATIO
    v_ms = (rpm * 2 * math.pi * WHEEL_R) / 60
    return round(v_ms * 3.6, 2)

# ── Colors ────────────────────────────────────────────────────
BG         = (10,  10,  18)
PANEL_BG   = (13,  13,  20)
BORDER     = (58,  58,  92)
BORDER_DIM = (30,  30,  52)
TEXT       = (224, 224, 255)
TEXT_DIM   = (90,  90,  138)
PURPLE     = (192, 132, 252)
BLUE       = (56,  189, 248)
GREEN      = (74,  222, 128)
RED        = (248, 113, 113)
YELLOW     = (255, 200, 50)
DARK       = (26,  26,  46)

# ── Fonts ─────────────────────────────────────────────────────
pygame.init()
FONT_SM  = pygame.font.SysFont("couriernew", 13, bold=True)
FONT_MD  = pygame.font.SysFont("couriernew", 16, bold=True)
FONT_LG  = pygame.font.SysFont("couriernew", 32, bold=True)
FONT_HDR = pygame.font.SysFont("couriernew", 18, bold=True)


# ── Draw helpers ──────────────────────────────────────────────
def panel(surf, rect, title):
    pygame.draw.rect(surf, PANEL_BG, rect)
    pygame.draw.rect(surf, BORDER, rect, 2)
    surf.blit(FONT_SM.render(title, True, TEXT_DIM), (rect.x + 10, rect.y + 8))

def bar(surf, rect, val, lo, hi, color):
    pygame.draw.rect(surf, DARK, rect)
    pygame.draw.rect(surf, BORDER_DIM, rect, 1)
    pct  = max(0, min(1, (val - lo) / (hi - lo)))
    fill = pygame.Rect(rect.x, rect.y, int(rect.w * pct), rect.h)
    if fill.w > 0:
        pygame.draw.rect(surf, color, fill)

def graph(surf, rect, history, lo, hi, color, centerline=False):
    pygame.draw.rect(surf, DARK, rect)
    pygame.draw.rect(surf, BORDER_DIM, rect, 1)
    if centerline:
        cy = rect.y + rect.h // 2
        for x in range(rect.x, rect.x + rect.w, 8):
            pygame.draw.line(surf, BORDER, (x, cy), (x + 4, cy), 1)
    if len(history) < 2:
        return
    pts = []
    for i, v in enumerate(history):
        x   = rect.x + int(i / (len(history) - 1) * rect.w)
        pct = max(0, min(1, (v - lo) / (hi - lo)))
        y   = rect.y + rect.h - int(pct * rect.h)
        pts.append((x, max(rect.y + 1, min(rect.y + rect.h - 1, y))))
    pygame.draw.lines(surf, color, False, pts, 2)
    surf.blit(FONT_SM.render(str(lo),  True, TEXT_DIM), (rect.x + 3, rect.y + rect.h - 14))
    surf.blit(FONT_SM.render(str(hi),  True, TEXT_DIM), (rect.x + 3, rect.y + 2))
    surf.blit(FONT_SM.render("NOW",    True, TEXT_DIM), (rect.x + rect.w - 30, rect.y + rect.h - 14))


# ── Input handler ─────────────────────────────────────────────
class InputHandler:
    """Reads keyboard or Xbox controller and returns angle + throttle."""
    DEAD_ZONE = 0.08

    def __init__(self):
        pygame.joystick.init()
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

        self.angle   = 110      # 80–130
        self.throttle = 0.0    # 0.0–1.0 (maps to voltage)

    def update(self, keys):
        # ── Keyboard ──────────────────────────────────────────
        if keys[pygame.K_LEFT]:
            self.angle = max(80,  self.angle - 2)
        elif keys[pygame.K_RIGHT]:
            self.angle = min(130, self.angle + 2)
        else:
            # Snap back to center when no key held
            if self.angle < 110:
                self.angle = min(110, self.angle + 2)
            elif self.angle > 110:
                self.angle = max(110, self.angle - 2)

        if keys[pygame.K_UP]:
            self.throttle = min(1.0, self.throttle + 0.03)
        else:
            self.throttle = max(0.0, self.throttle - 0.05)

        # ── Xbox controller (overrides keyboard if connected) ──
        if self.joy:
            pygame.event.pump()

            # Left stick X → steering
            raw = self.joy.get_axis(0)
            if abs(raw) < self.DEAD_ZONE:
                raw = 0.0
            self.angle = int(80 + (raw + 1.0) / 2.0 * 50)

            # Right trigger (axis 5 on Xbox, range -1 to +1)
            try:
                trig = (self.joy.get_axis(5) + 1) / 2   # normalize 0–1
            except:
                trig = 0.0
            self.throttle = trig

        return self.angle, self.throttle


# ── Dashboard ─────────────────────────────────────────────────
class Dashboard:
    def __init__(self, screen):
        self.screen     = screen
        self.start_time = time.time()
        self.battery    = 100.0
        max_pts         = HISTORY_SECS * FPS
        self.spd_hist   = deque(maxlen=max_pts)
        self.ang_hist   = deque(maxlen=max_pts)

    def draw(self, angle, speed, throttle):
        self.battery = max(0, self.battery - 0.003)
        self.spd_hist.append(speed)
        self.ang_hist.append(angle)

        s = self.screen
        s.fill(BG)
        W, H    = s.get_size()
        PAD     = 14
        LW      = 290          # left column width
        RW      = W - LW - PAD * 3
        TOP     = 46
        PH      = (H - TOP - PAD * 5) // 4   # panel height
        GH      = (H - TOP - PAD * 3) // 2   # graph height
        px, gx  = PAD, PAD * 2 + LW

        # ── Header ────────────────────────────────────────────
        s.blit(FONT_HDR.render("ENGINEER DASHBOARD", True, PURPLE), (PAD, PAD))
        elapsed = int(time.time() - self.start_time)
        sess    = FONT_SM.render(f"SESSION  {elapsed//60:02d}:{elapsed%60:02d}", True, TEXT_DIM)
        s.blit(sess, (W - sess.get_width() - PAD, PAD + 4))
        hint = FONT_SM.render("ESC: back  |  ARROWS / L-STICK: steer  |  UP / R-TRIG: throttle", True, BORDER)
        s.blit(hint, (PAD, 30))
        pygame.draw.line(s, BORDER_DIM, (PAD, 42), (W - PAD, 42), 1)

        # ── Steering ──────────────────────────────────────────
        r1 = pygame.Rect(px, TOP, LW, PH)
        panel(s, r1, "STEERING ANGLE")
        s.blit(FONT_LG.render(str(angle), True, TEXT), (r1.x + 10, r1.y + 22))
        s.blit(FONT_SM.render("DEG", True, TEXT_DIM), (r1.x + 60, r1.y + 38))
        br = pygame.Rect(r1.x + 10, r1.y + PH - 32, LW - 20, 12)
        bar(s, br, angle, 80, 130, PURPLE)
        pct    = (angle - 80) / 50
        needle = br.x + int(pct * br.w)
        pygame.draw.rect(s, PURPLE, (needle - 3, br.y - 2, 6, br.h + 4))
        cx = br.x + br.w // 2
        pygame.draw.line(s, BORDER, (cx, br.y - 3), (cx, br.y + br.h + 3), 1)
        for lbl, xp in [("L", br.x), ("CTR", cx - 10), ("R", br.x + br.w - 8)]:
            s.blit(FONT_SM.render(lbl, True, TEXT_DIM), (xp, br.y + br.h + 3))

        # ── Speed ─────────────────────────────────────────────
        r2 = pygame.Rect(px, TOP + PH + PAD, LW, PH)
        panel(s, r2, "SPEED")
        s.blit(FONT_LG.render(f"{speed:.1f}", True, TEXT), (r2.x + 10, r2.y + 22))
        s.blit(FONT_SM.render("KM/H", True, TEXT_DIM), (r2.x + 90, r2.y + 38))
        sb = pygame.Rect(r2.x + 10, r2.y + PH - 32, LW - 20, 12)
        bar(s, sb, speed, 0, SPEED_MAX, BLUE)
        s.blit(FONT_SM.render("0", True, TEXT_DIM), (sb.x, sb.y + sb.h + 3))
        mx = FONT_SM.render(f"{SPEED_MAX}", True, TEXT_DIM)
        s.blit(mx, (sb.x + sb.w - mx.get_width(), sb.y + sb.h + 3))

        # ── Battery ───────────────────────────────────────────
        r3 = pygame.Rect(px, TOP + (PH + PAD) * 2, LW, PH)
        panel(s, r3, "BATTERY")
        bat  = int(self.battery)
        bcol = GREEN if bat > 40 else (YELLOW if bat > 20 else RED)
        s.blit(FONT_LG.render(f"{bat}%", True, bcol), (r3.x + 10, r3.y + 22))
        bw = (LW - 20 - 16) // 5
        for i in range(5):
            bx     = r3.x + 10 + i * (bw + 4)
            by     = r3.y + PH - 32
            filled = (i * 20) < bat
            pygame.draw.rect(s, bcol if filled else DARK, (bx, by, bw, 12))
            pygame.draw.rect(s, BORDER_DIM, (bx, by, bw, 12), 1)

        # ── Connection ────────────────────────────────────────
        r4 = pygame.Rect(px, TOP + (PH + PAD) * 3, LW, PH)
        panel(s, r4, "CONNECTION")
        for i, (k, v, col) in enumerate([
            ("STATUS", "ONLINE",       GREEN),
            ("PING",   "12 MS",        TEXT),
            ("ESP32",  ESP32_IP,       PURPLE),
        ]):
            ry = r4.y + 26 + i * 20
            s.blit(FONT_SM.render(k, True, TEXT_DIM), (r4.x + 10, ry))
            vt = FONT_SM.render(v, True, col)
            s.blit(vt, (r4.x + LW - vt.get_width() - 10, ry))

        # ── Speed graph ───────────────────────────────────────
        rg1 = pygame.Rect(gx, TOP, RW, GH)
        panel(s, rg1, f"SPEED / TIME  (20s)  max {SPEED_MAX} km/h")
        graph(s, pygame.Rect(rg1.x+10, rg1.y+24, rg1.w-20, rg1.h-34),
              self.spd_hist, 0, SPEED_MAX, BLUE)

        # ── Steering graph ────────────────────────────────────
        rg2 = pygame.Rect(gx, TOP + GH + PAD, RW, GH)
        panel(s, rg2, "STEERING / TIME  (20s)")
        graph(s, pygame.Rect(rg2.x+10, rg2.y+24, rg2.w-20, rg2.h-34),
              self.ang_hist, 80, 130, PURPLE, centerline=True)

        pygame.display.flip()


# ── Main ──────────────────────────────────────────────────────
def run(screen=None):
    standalone = screen is None
    if standalone:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

    clock   = pygame.time.Clock()
    dash    = Dashboard(screen)
    inp     = InputHandler()

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if standalone:
                    pygame.quit(); sys.exit()
                else:
                    return

        angle, throttle = inp.update(keys)
        volts = throttle * MOTOR_VOLTAGE
        speed = calc_speed(volts)

        dash.draw(angle, speed, throttle)
        clock.tick(FPS)


if __name__ == "__main__":
    run()