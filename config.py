# debuging
# DUMMY = False
DUMMY = True
DEBUG = True

LOGLEVEL = 'DEBUG' if DEBUG else 'INFO'

#comm settings
AUTHKEY = b'password' # communication password
PORT = 6000
LISTENER_IP = '192.168.1.103' # for remote access in debug mode
# LISTENER_IP = '127.0.0.1' # for local development
ADDRESS = LISTENER_IP if DEBUG else 'localhost'

#neopixel settings
if not DUMMY:
    import board
    import neopixel
    NEOPIXEL_ORDER = neopixel.RGB
    NEOPIXEL_GPIO = board.D18


# LED strip(s) definitions:

# strip types length definition
LED_CIRCLE_LEN = 24
LED_LINE_LEN = 8

# Groups definition
LED_GROUPS = [
    LED_CIRCLE_LEN,
    LED_CIRCLE_LEN,
    LED_LINE_LEN
]

# LED range definitions
LED_LEFT = range(LED_GROUPS[0])
LED_RIGHT = range(LED_LEFT.stop,LED_LEFT.stop+LED_GROUPS[1])
LED_TOP = range(LED_RIGHT.stop,LED_RIGHT.stop+LED_GROUPS[2])

NEOPIXEL_LED = sum(LED_GROUPS)
LED_ALL = range(NEOPIXEL_LED)