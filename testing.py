

# import pygame
# import socket
# import time
# import sys
# import logging

# # ── Logging ───────────────────────────────────────────────────
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# log = logging.getLogger(__name__)

# # ── Config ────────────────────────────────────────────────────
# ESP32_IP      = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.1"
# ESP32_PORT    = 9000
# ANGLE_MIN     = 80
# ANGLE_MAX     = 130
# ANGLE_CENTER  = 110
# DEAD_ZONE     = 0.08
# SEND_INTERVAL = 0.05

# # ========== angle control logic ==========
# def map_axis_to_angle(raw: float) -> int:
#     if abs(raw) < DEAD_ZONE:
#         return ANGLE_CENTER
#     angle = ANGLE_MIN + (raw + 1.0) / 2.0 * (ANGLE_MAX - ANGLE_MIN)
#     return int(round(max(ANGLE_MIN, min(ANGLE_MAX, angle))))

# #============ throttle control logic ==========
# # def map_axis_to_throttle(raw: float) -> int:
#     # throttle = 

# # ============= main =============
# def main():
#     # Controller init
#     pygame.init()
#     pygame.joystick.init()

#     if pygame.joystick.get_count() == 0:
#         log.error("No controller detected. Plug in Xbox controller and retry.")
#         sys.exit(1)

#     joy = pygame.joystick.Joystick(0)
#     joy.init()
#     log.info(f"Controller connected: {joy.get_name()}")

#     # WiFi / TCP connection to ESP32
#     log.info(f"Connecting to ESP32 at {ESP32_IP}:{ESP32_PORT} ...")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     try:
#         sock.connect((ESP32_IP, ESP32_PORT))
#         log.info("Connected to ESP32!")
#     except ConnectionRefusedError:
#         log.error(f"Could not connect to ESP32 at {ESP32_IP}:{ESP32_PORT}")
#         log.error("Make sure the ESP32 is on and the IP is correct.")
#         sys.exit(1)

#     last_angle = -1
#     last_sent  = 0.0

#     log.info("Running. Press Ctrl+C to stop.")

#     try:
#         while True:
#             pygame.event.pump()

#             raw   = joy.get_axis(0)   # left stick X-axis
#             angle = map_axis_to_angle(raw)
#             now   = time.time()

#             if angle != last_angle and (now - last_sent) >= SEND_INTERVAL:
#                 sock.sendall(f"{angle}\n".encode())
#                 log.debug(f"Sent angle: {angle}")
#                 last_angle = angle
#                 last_sent  = now

#             time.sleep(0.01)

#     except KeyboardInterrupt:
#         log.info("Stopped by user.")
#     finally:
#         sock.close()
#         pygame.quit()

# if __name__ == "__main__":
#     main()




