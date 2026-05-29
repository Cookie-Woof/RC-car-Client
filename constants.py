"""
constants.py
Easy Constants access to store it all in one place
"""
 
class Network:
    ESP_IP = "192.168.4.1"
    UDP_PORT = 6000
 
 
class Graphics:
 
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 546
    SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
 
    MAIN_SCREEN = "test1.jpg"
 
    class Buttons:
        PLAY_BUTTON_NOT_PRESSED = "playbuttontest1.jpg"

        # PLAY_BUTTON_PRESSED = ""

        # ENGINEER_BUTTON_PRESSED = ""
        # ENGINEER_BUTTON_NOT_PRESSED = ""

        # INFO_BUTTON_NOT_PRESSED = ""
        # INFO_BUTTON_PRESSED = ""

        # DRIVER_BUTTON_PRESSED = ""
        # DRIVER_BUTTON_NOT_PRESSED = ""

        # EXIST_BUTTON_PRESSED = ""
        # EXIST_BUTTON_NOT_PRESSED = ""

    class Dashboard:
        DASHBOARD_BG = "test.png"

        BG_COLOR         = (8, 8, 12)
        PANEL_COLOR      = (14, 16, 22)
        BORDER_COLOR     = (220, 50, 50)
        BORDER_DIM       = (80, 20, 20)
        TEXT_PRIMARY     = (255, 255, 255)
        TEXT_ACCENT      = (220, 50, 50)
        TEXT_DIM         = (100, 110, 130)
        TEXT_GREEN       = (50, 220, 100)
        TEXT_YELLOW      = (255, 200, 50)
        GAUGE_BG         = (25, 28, 38)
        GAUGE_FILL       = (220, 50, 50)
        GAUGE_FILL_LOW   = (50, 200, 100)
        SCANLINE_COLOR   = (255, 255, 255)
        GRID_COLOR       = (20, 24, 34)



