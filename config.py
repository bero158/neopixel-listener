# debuging
DUMMY = True
LOGLEVEL = 'DEBUG'


#neopixel settings
# import board
# import neopixel
NEOPIXEL_GPIO = 1 #board.D18
NEOPIXEL_LED = 16
if not DUMMY:
    NEOPIXEL_ORDER = neopixel.RGB
    

#comm settings
AUTHKEY = b'password'
PORT = 6000

BUTTON_LED_LEFT = range(0,NEOPIXEL_LED // 2 )
BUTTON_LED_RIGHT = range(NEOPIXEL_LED // 2,NEOPIXEL_LED)
BUTTON_LED_ALL = range(0,NEOPIXEL_LED)