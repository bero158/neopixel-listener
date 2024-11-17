
import neopixel
import config
import logging as LOGGER

pixels = neopixel.NeoPixel(config.NEOPIXEL_GPIO, config.NEOPIXEL_LED, auto_write = False)

def set(changes : tuple):
    if changes:    
        for change in changes:
            pixel = change[0]
            val = change[1]
            if pixel < config.NEOPIXEL_LED:
                pixels[pixel] = val
        pixels.show()

def clean():
    LOGGER.debug("Neopixel clean()") 
    pixels.fill((0,0,0))
    pixels.show()

def fill(color : tuple):
    if color:
        LOGGER.debug(f"Neopixel fill({color})") 
        pixels.fill(color)
        pixels.show()

def close():
    pixels.deinit()