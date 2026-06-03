import math

TITLE = "Mazda Miata The Game"
BG_IMAGE = "mainscreen/background.jpg"

POS_DRIVER   = (510, 260)
POS_ENGINEER = (510, 320)
POS_EXIT     = (20,  330)
POS_INFO     = (130, 330)

SIZE_MAIN   = (160, 55)
SIZE_BOTTOM = (100, 45)

INFO_TEXT = [
    "Welcome to track! and yes, you pulled up in a Miata.",
    "Bold choice. Driver or Engineer, your call!",
    "Push it to the limit or build it to perfection.",
    "Either way this car is ready to prove a point.",
    "Small? Sure. Slow? Not a chance.",
    "Lights are out, let's see what you've got!",
]

class Network:
    ESP_IP = "192.168.50.223"
    ENGINEER_IP = "127.0.0.1"
    UDP_PORT = 5005
    
class Physics:
    MOTOR_VOLTAGE = 6.0
    MOTOR_RPM = 1500.0
    KV = MOTOR_RPM / MOTOR_VOLTAGE
    GEAR_RATIO = 3.23
    WHEEL_R = 0.02
    
    RPM_MAX = (MOTOR_VOLTAGE * KV) / GEAR_RATIO
    V_MAX_MS = (RPM_MAX * 2 * math.pi * WHEEL_R) / 60
    SPEED_MAX = round(V_MAX_MS * 3.6, 1)

class Servo:
    MIN_ANGLE = 87
    MAX_ANGLE = 140 
    CENTER = 117
    SPEED = 2

class Graphics:
    FPS = 45
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 546
    SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
    MAIN_SCREEN = "test1.jpg"
 
    class Buttons:
        PLAY_BUTTON_NOT_PRESSED = "playbuttontest1.jpg"
        BTN_DRIVER_NORMAL   = "mainscreen/driver_normal.jpg"
        BTN_DRIVER_PRESSED  = "mainscreen/driver_pressed.jpg"
        BTN_ENGINEER_NORMAL = "mainscreen/engineer_normal.jpg"
        BTN_ENGINEER_PRESSED= "mainscreen/engineer_pressed.jpg"
        BTN_EXIT_NORMAL     = "mainscreen/exit_normal.jpg"
        BTN_EXIT_PRESSED    = "mainscreen/exit_pressed.jpg"
        BTN_INFO_NORMAL     = "mainscreen/info_normal.jpg"
        BTN_INFO_PRESSED    = "mainscreen/info_pressed.jpg"

    class DriverCockpit:
        WIDTH = 686
        HEIGHT = 386
        SIZE = (WIDTH, HEIGHT)
        
        BG_DARK      = (10, 10, 15)
        BORDER_DIM   = (30, 30, 50)
        TEXT_HDR     = (90, 90, 140)
        TEXT_LABEL   = (80, 80, 110)
        TEXT_WHITE   = (255, 255, 255)
        
        COLOR_ACTIVE = (74, 222, 128)
        COLOR_ALERT  = (248, 113, 113)
        COLOR_SPEED  = (56, 189, 248)
        COLOR_MOTOR  = (192, 132, 252)

    class Dashboard:
        HISTORY_SECS     = 20
        BG_COLOR         = (10, 10, 18)
        PANEL_COLOR      = (13, 13, 20)
        BORDER_COLOR     = (58, 58, 92)       
        BORDER_DIM       = (30, 30, 52)       
        TEXT_PRIMARY     = (224, 224, 255)    
        TEXT_ACCENT      = (192, 132, 252)    
        TEXT_DIM         = (90, 90, 138)      
        TEXT_GREEN       = (74, 222, 128)     
        TEXT_YELLOW      = (255, 200, 50)     
        GAUGE_BG         = (26, 26, 46)       
        GAUGE_FILL       = (248, 113, 113)    
        GAUGE_FILL_LOW   = (56, 189, 248)     
