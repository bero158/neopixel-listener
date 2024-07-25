# for testing on PC
import config
import logging as LOGGER


def set(changes):
    if changes:    
        for change in changes:
            pixel = change[0]
            val = change[1]
            if pixel < config.NEOPIXEL_LED:
                LOGGER.info(f"Set {pixel} to {val}")             

def clean():
    LOGGER.info("Neopixel clean()") 

def fill(color):
    if color:
        LOGGER.info(f"Neopixel fill({color})") 
