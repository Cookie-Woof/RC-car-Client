# """
# dashboard_screen.py
# RC Car Dashboard — F1 Style
# Full-screen track background with floating UI, no panels or boxes.
# """

# import socket
# import time
# import math
# import datetime
# import pygame
# import constants

# # ─── Init ────────────────────────────────────────────────────────────────────

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# pygame.init()
# screen = pygame.display.set_mode(constants.Graphics.SIZE)
# pygame.display.set_caption("Tokyo Drift RC  //  F1 DASHBOARD")
# clock = pygame.time.Clock()

# W, H = constants.Graphics.WINDOW_WIDTH, constants.Graphics.WINDOW_HEIGHT  # 894 x 601
# # ─── Colours ─────────────────────────────────────────────────────────────────

# TEXT_WHITE    = (240, 240, 240)
# TEXT_DIM      = (150, 155, 165)
# TEXT_YELLOW   = (220, 178, 35)
# TEXT_GREEN    = (72, 200, 110)
# TEXT_RED      = (210, 55, 55)
# GRAPH_LINE    = (255, 255, 255)
# GRAPH_AXIS    = (120, 125, 135)
# THROTTLE_FILL = (195, 155, 28)
# THROTTLE_BG   = (40, 42, 50, 160)
# STEER_MARKER  = (200, 202, 210)


# # ─── Fonts ───────────────────────────────────────────────────────────────────

# def sf(names, size, bold=False):
#     for n in names:
#         try:
#             f = pygame.font.SysFont(n, size, bold=bold)
#             if f: return f
#         except: pass
#     return pygame.font.Font(None, size)

# SANS = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]

# f_huge      = sf(SANS, 56, bold=True)   # 69%
# f_big       = sf(SANS, 38, bold=True)   # 12° L
# f_med       = sf(SANS, 20, bold=True)   # DATA
# f_label     = sf(SANS, 13, bold=False)  # dim labels
# f_label_b   = sf(SANS, 15, bold=True)   # data values
# f_tiny      = sf(SANS, 11)


# # ─── Track → image mapping ───────────────────────────────────────────────────

# DOW_TRACK = [
#     "Silverstone",  # Monday
#     "Monaco",       # Tuesday
#     "Spa",          # Wednesday
#     "Abu Dhabi",    # Thursday
#     "COTA",         # Friday
#     "Nurburgring",  # Saturday
#     "Imola",        # Sunday
# ]

# TRACK_INFO = {
#     "Imola":       {"file": "track_images/imola.png",       "corners": 19, "length": "4.9"},
#     "Silverstone": {"file": "track_images/silverstone.png", "corners": 18, "length": "5.9"},
#     "Monaco":      {"file": "track_images/monaco.png",      "corners": 19, "length": "3.3"},
#     "Spa":         {"file": "track_images/spa.png",         "corners": 19, "length": "7.0"},
#     "Abu Dhabi":   {"file": "track_images/abu_dhabi.png",   "corners": 16, "length": "5.3"},
#     "COTA":        {"file": "track_images/cota.png",        "corners": 20, "length": "5.5"},
#     "Nurburgring": {"file": "track_images/nurburgring.png", "corners": 15, "length": "5.1"},
#     "Bahrain":     {"file": "track_images/bahrain.png",     "corners": 15, "length": "5.4"},
# }

# def todays_track():
#     dow = datetime.datetime.today().weekday()
#     return DOW_TRACK[dow]

# track_name = todays_track()
# info       = TRACK_INFO[track_name]

# # Load background — scale to window
# try:
#     bg_raw = pygame.image.load(info["file"]).convert()
#     bg_img = pygame.transform.scale(bg_raw, (W, H))
#     HAS_BG = True
#     print(f"Loaded background: {info['file']}")
# except Exception as e:
#     HAS_BG = False
#     print(f"Could not load background ({e}) — using dark fill")

# # ─── Side overlay surfaces (drawn once, reused every frame) ──────────────────
# # Left strip: semi-transparent dark gradient for graph readability
# # Right strip: same for data readability

# OVERLAY_W = 255   # width of each side overlay

# left_overlay  = pygame.Surface((OVERLAY_W, H), pygame.SRCALPHA)
# right_overlay = pygame.Surface((OVERLAY_W, H), pygame.SRCALPHA)

# # Gradient: opaque at edge → transparent toward centre
# for x in range(OVERLAY_W):
#     alpha = int(200 * (1 - x / OVERLAY_W) ** 0.6)
#     pygame.draw.line(left_overlay,  (8, 10, 14, alpha), (x, 0), (x, H))
#     pygame.draw.line(right_overlay, (8, 10, 14, alpha), (OVERLAY_W - 1 - x, 0), (OVERLAY_W - 1 - x, H))

# # ─── Controller ──────────────────────────────────────────────────────────────

# joystick = None
# if pygame.joystick.get_count() > 0:
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#     ctrl_name = joystick.get_name()[:22]
#     print(f"Connected: {ctrl_name}")
# else:
#     ctrl_name = "KEYBOARD"
#     print("Keyboard mode — Arrows, L = reset lap, Esc = quit")

# # ─── State ───────────────────────────────────────────────────────────────────

# angle       = 90
# speed_pct   = 0.0
# direction   = "FWD"
# send_count  = 0
# start_time  = time.time()
# lap_start   = time.time()
# tick        = 0
# response_ms = 0
# charge_pct  = 100

# MAX_HIST    = 120
# pos_history = [0.0] * MAX_HIST
# vel_history = [0.0] * MAX_HIST

# # ─── Drawing helpers ─────────────────────────────────────────────────────────

# def txt(surf, text, font, color, x, y, anchor="topleft"):
#     s = font.render(str(text), True, color)
#     r = s.get_rect(**{anchor: (x, y)})
#     surf.blit(s, r)

# def alpha_rect(surf, rect, color_rgba):
#     s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
#     s.fill(color_rgba)
#     surf.blit(s, rect.topleft)

# def hbar(surf, rect, pct, fill):
#     """Throttle bar — bg is a translucent rect, fill is solid."""
#     alpha_rect(surf, rect, (40, 42, 50, 140))
#     if pct > 0.001:
#         filled = pygame.Rect(rect.x, rect.y, max(4, int(rect.width * min(pct, 1.0))), rect.height)
#         pygame.draw.rect(surf, fill, filled, border_radius=2)

# def draw_steering_bar(surf, rect, angle_deg):
#     """Horizontal bar with sliding marker."""
#     alpha_rect(surf, rect, (40, 42, 50, 140))
#     cx   = rect.centerx
#     norm = (angle_deg - 90) / 90.0
#     mx   = cx + int(norm * (rect.width // 2 - 8))
#     # centre tick
#     pygame.draw.line(surf, (80, 84, 95), (cx, rect.y), (cx, rect.bottom))
#     # marker
#     pygame.draw.rect(surf, STEER_MARKER,
#                      pygame.Rect(mx - 5, rect.y - 3, 10, rect.height + 6),
#                      border_radius=2)

# def draw_battery(surf, x, y, w, h, pct):
#     col = TEXT_GREEN if pct > 40 else (TEXT_YELLOW if pct > 20 else TEXT_RED)
#     alpha_rect(surf, pygame.Rect(x, y, w, h), (40, 42, 50, 160))
#     fill_w = max(2, int((w - 4) * pct / 100))
#     pygame.draw.rect(surf, col, pygame.Rect(x + 2, y + 2, fill_w, h - 4), border_radius=1)
#     pygame.draw.rect(surf, (80, 84, 95), pygame.Rect(x + w, y + h // 3, 3, h // 3))

# def draw_graph(surf, rect, history, y_label):
#     """Floating graph — no background box, just axes and line."""
#     # Faint axis lines only
#     pygame.draw.line(surf, GRAPH_AXIS, (rect.x, rect.y),     (rect.x, rect.bottom), 1)
#     pygame.draw.line(surf, GRAPH_AXIS, (rect.x, rect.bottom), (rect.right, rect.bottom), 1)

#     # Rotated Y label
#     ls = f_tiny.render(y_label, True, TEXT_DIM)
#     lr = pygame.transform.rotate(ls, 90)
#     surf.blit(lr, (rect.x - lr.get_width() - 4,
#                    rect.centery - lr.get_height() // 2))
#     txt(surf, "t", f_tiny, TEXT_DIM, rect.right - 8, rect.bottom + 3)

#     # Plot
#     mn = 0.0
#     mx = max(max(history), 0.001)
#     pts = []
#     for i, v in enumerate(history):
#         px = rect.x + int(i / (MAX_HIST - 1) * rect.width)
#         py = rect.bottom - int((v - mn) / mx * (rect.height - 4)) - 2
#         py = max(rect.y + 1, min(rect.bottom - 1, py))
#         pts.append((px, py))
#     if len(pts) >= 2:
#         pygame.draw.lines(surf, GRAPH_LINE, False, pts, 1)

# # ─── Main Draw ───────────────────────────────────────────────────────────────

# def draw(angle, speed_pct, direction, send_count, tick):

#     elapsed = time.time() - start_time
#     lap_t   = time.time() - lap_start
#     lap_str = f"{int(lap_t//60)}:{int(lap_t%60):02d}.{int((lap_t%1)*10)}"

#     # ── Background ─────────────────────────────────────────────────────────
#     if HAS_BG:
#         screen.blit(bg_img, (0, 0))
#     else:
#         screen.fill((10, 12, 15))

#     # ── Side overlays ──────────────────────────────────────────────────────
#     screen.blit(left_overlay,  (0, 0))
#     screen.blit(right_overlay, (W - OVERLAY_W, 0))

#     # ════════════════════════════════════════════════════════════════════════
#     # LEFT SIDE — Graphs (floating, no box)
#     # ════════════════════════════════════════════════════════════════════════

#     GX = 52
#     GW = 178
#     GH = 105

#     g1 = pygame.Rect(GX, 30,  GW, GH)
#     g2 = pygame.Rect(GX, 165, GW, GH)

#     draw_graph(screen, g1, pos_history, "x Position")
#     draw_graph(screen, g2, vel_history, "V Velocity")

#     # ════════════════════════════════════════════════════════════════════════
#     # RIGHT SIDE — Throttle / Steering / Data (floating text)
#     # ════════════════════════════════════════════════════════════════════════

#     RX  = W - OVERLAY_W + 16   # left edge of right column
#     RXR = W - 18               # right-align anchor

#     # ── THROTTLE ───────────────────────────────────────────────────────────
#     txt(screen, "THROTTLE", f_label, TEXT_DIM, RX, 18)
#     spd_int = int(speed_pct)
#     tc = TEXT_GREEN if spd_int < 40 else (TEXT_YELLOW if spd_int < 75 else TEXT_RED)
#     txt(screen, f"{spd_int}%", f_huge, tc, RXR, 32, anchor="topright")
#     hbar(screen, pygame.Rect(RX, 96, RXR - RX, 10), speed_pct / 100, THROTTLE_FILL)

#     # ── STEERING ───────────────────────────────────────────────────────────
#     txt(screen, "STEERING ANGLE", f_label, TEXT_DIM, RX, 122)
#     nd   = angle - 90
#     side = " L" if nd < 0 else (" R" if nd > 0 else "")
#     txt(screen, f"{abs(nd)}°{side}", f_big, TEXT_WHITE, RXR, 138, anchor="topright")
#     draw_steering_bar(screen, pygame.Rect(RX, 184, RXR - RX, 10), angle)

#     # ── DATA ───────────────────────────────────────────────────────────────
#     txt(screen, "DATA", f_med, TEXT_WHITE, RXR, 212, anchor="topright")
#     draw_battery(screen, RXR - 54, 240, 50, 14, charge_pct)

#     mode = "Sport" if speed_pct > 50 else "Comfort"
#     rows = [
#         ("Power",    f"{max(2.8, 4.2 - (100-charge_pct)*0.015):.1f}v"),
#         ("Charge",   f"{charge_pct}%"),
#         ("Lap time", lap_str),
#         ("Mode",     mode),
#         ("Response", f"{response_ms}ms"),
#         ("Packets",  str(send_count)),
#     ]
#     for i, (label, val) in enumerate(rows):
#         ry = 265 + i * 32
#         txt(screen, label + ":", f_label,   TEXT_DIM,   RX,   ry)
#         txt(screen, val,         f_label_b, TEXT_WHITE,  RXR,  ry, anchor="topright")

#     # Controller row (smaller, at the bottom of data)
#     txt(screen, "Controller:", f_label, TEXT_DIM,  RX,  265 + len(rows) * 32)
#     txt(screen, ctrl_name,     f_tiny,  TEXT_WHITE, RXR, 268 + len(rows) * 32, anchor="topright")

#     pygame.display.flip()

# # ─── Main Loop ───────────────────────────────────────────────────────────────

# running = True

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             if event.key == pygame.K_l:
#                 lap_start = time.time()

#     # ── Input ─────────────────────────────────────────────────────────────
#     if joystick:
#         axis_val  = joystick.get_axis(0)
#         angle     = int((axis_val + 1) * 90)
#         try:
#             t_raw     = joystick.get_axis(5)
#             speed_pct = max(0.0, (t_raw + 1) / 2 * 100)
#         except:
#             speed_pct = 0.0
#         try:
#             direction = "REV" if joystick.get_axis(2) > 0.1 else "FWD"
#         except:
#             direction = "FWD"
#     else:
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_LEFT]:
#             angle = max(0, angle - 3)
#         elif keys[pygame.K_RIGHT]:
#             angle = min(180, angle + 3)
#         else:
#             if angle < 90:   angle = min(90, angle + 2)
#             elif angle > 90: angle = max(90, angle - 2)

#         if keys[pygame.K_UP]:
#             speed_pct = min(100.0, speed_pct + 4)
#             direction = "FWD"
#         elif keys[pygame.K_DOWN]:
#             speed_pct = min(100.0, speed_pct + 4)
#             direction = "REV"
#         else:
#             speed_pct = max(0.0, speed_pct - 3)

#     # Battery drain (1% per 5s)
#     charge_pct = max(0, 100 - int((time.time() - start_time) / 5))

#     # Graphs — only real input, no noise
#     vel_val = speed_pct / 100.0
#     pos_history.append(
#         pos_history[-1] + vel_val * 0.02 if vel_val > 0 else pos_history[-1]
#     )
#     vel_history.append(vel_val)
#     pos_history.pop(0)
#     vel_history.pop(0)

#     # UDP send
#     t0 = time.time()
#     try:
#         sock.sendto(str(angle).encode(),
#                     (constants.Network.ESP_IP, constants.Network.UDP_PORT))
#         send_count  += 1
#         response_ms  = max(1, int((time.time() - t0) * 1000))
#     except:
#         pass

#     draw(angle, speed_pct, direction, send_count, tick)
#     tick += 1
#     clock.tick(50)

# pygame.quit()