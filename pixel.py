import board
import neopixel
import config
import logging as LOGGER

pixels = neopixel.NeoPixel(config.NEOPIXEL_GPIO, config.NEOPIXEL_LED, auto_write = False)

def set(changes):
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

def fill(color):
    if color:
        LOGGER.debug(f"Neopixel fill({color})") 
        pixels.fill(color)
        pixels.show()