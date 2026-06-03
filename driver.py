import pygame
import socket
import struct
import math
import time
import sys

import constants

def get_telemetry(throttle):
    volts = throttle * constants.Physics.MOTOR_VOLTAGE
    rpm   = (volts * constants.Physics.KV) / constants.Physics.GEAR_RATIO
    v_ms  = (rpm * 2 * math.pi * constants.Physics.WHEEL_R) / 60
    speed = round(v_ms * 3.6, 1)
    return int(rpm), speed


class InputHandler:
    def __init__(self):
        pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joy: 
            self.joy.init()
        self.angle = 110      
        self.throttle = 0.0    

    def update(self, keys):
        if keys[pygame.K_LEFT]:    self.angle = max(80,  self.angle - 2)
        elif keys[pygame.K_RIGHT]: self.angle = min(130, self.angle + 2)
        else:                      self.angle = 110
        
        if keys[pygame.K_UP]:      self.throttle = min(1.0, self.throttle + 0.04)
        else:                      self.throttle = max(0.0, self.throttle - 0.06)

        if self.joy:
            pygame.event.pump()
            raw_steer = self.joy.get_axis(0)
            if abs(raw_steer) < 0.08: raw_steer = 0.0
            self.angle = int(80 + (raw_steer + 1.0) / 2.0 * 50)
            try:    
                self.throttle = (self.joy.get_axis(5) + 1) / 2
            except: 
                self.throttle = 0.0

        return self.angle, self.throttle


def run():
    cfg = constants.Graphics.DriverCockpit
    
    screen = pygame.display.set_mode(cfg.SIZE)
    pygame.display.set_caption("DRIVER STATION // PLAYER 1")
    
    clock      = pygame.time.Clock()
    inp        = InputHandler()
    start_time = time.time()
    
    font_pixel_hd = pygame.font.SysFont("couriernew", 18, bold=True)
    font_pixel_sm = pygame.font.SysFont("couriernew", 15, bold=True)
    font_pixel_lg = pygame.font.SysFont("couriernew", 36, bold=True) 
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    queue_pos = 1 

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 

            angle, throttle = inp.update(pygame.key.get_pressed())
            rpm, speed = get_telemetry(throttle)

            packet = struct.pack("iff", angle, throttle, speed)
            try:
                sock.sendto(packet, (constants.Network.ESP_IP, constants.Network.UDP_PORT))
                sock.sendto(packet, (constants.Network.ENGINEER_IP, constants.Network.UDP_PORT))
            except:
                pass 

            try:
                data, _ = sock.recvfrom(1024)
                if len(data) == 4:
                    queue_pos = struct.unpack("i", data)[0]
            except (BlockingIOError, ConnectionResetError):
                pass

            if queue_pos == 0:
                status_txt, status_clr = "SYSTEM ONLINE // ACTIVE", cfg.COLOR_ACTIVE  
            else:
                status_txt, status_clr = f"IN QUEUE // POSITION {queue_pos}", cfg.COLOR_ALERT 

            sec = int(time.time() - start_time)
            time_str = f"{sec // 60:02d}:{sec % 60:02d}"

            screen.fill(cfg.BG_DARK) 

            pygame.draw.line(screen, cfg.BORDER_DIM, (30, 45), (cfg.WIDTH - 30, 45), 2)
            screen.blit(font_pixel_hd.render("MIATA COCKPIT CORE v1.0", True, cfg.TEXT_HDR), (32, 20))

            ui_rows = [
                ("PILOT STATUS", status_txt,          status_clr),
                ("TIME ELAPSED", time_str,            cfg.TEXT_WHITE),
                ("SPEEDOMETER",  f"{speed:.1f} KM/H", cfg.COLOR_SPEED), 
                ("MOTOR OUTPUT", f"{rpm} RPM",        cfg.COLOR_MOTOR) 
            ]

            for i, (label, val, clr) in enumerate(ui_rows):
                y_offset = 65 + (i * 76)
                screen.blit(font_pixel_sm.render(label, True, cfg.TEXT_LABEL), (35, y_offset))
                screen.blit(font_pixel_lg.render(val, True, clr), (35, y_offset + 20))

            pygame.display.flip()
            clock.tick(constants.Graphics.FPS)
            
    finally:
        sock.close()