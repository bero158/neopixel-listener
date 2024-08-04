# debuging
# DUMMY = False
DUMMY = True
LOGLEVEL = 'DEBUG'


#neopixel settings
NEOPIXEL_GPIO = 1 #board.D18
NEOPIXEL_LED = 16
if not DUMMY:
    import board
    import neopixel
    NEOPIXEL_ORDER = neopixel.RGB
    NEOPIXEL_GPIO = board.D18
    

#comm settings
AUTHKEY = b'password'
PORT = 6000

BUTTON_LED_LEFT = range(0,NEOPIXEL_LED // 2 )
BUTTON_LED_RIGHT = range(NEOPIXEL_LED // 2,NEOPIXEL_LED)
BUTTON_LED_ALL = range(0,NEOPIXEL_LED)