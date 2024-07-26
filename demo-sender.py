import config
import logging as LOGGER
import time
from sender import Sender
from led_effects import Effect, EffectCount, EffectFlash, EffectRainbow

LOGGER.basicConfig(level=config.LOGLEVEL)

def main():
    with Sender() as sender:
        fillLeft = Effect(sender,config.BUTTON_LED_LEFT)
        fillLeft.fill((32,16,0))
        fillRight = Effect(sender,config.BUTTON_LED_RIGHT)
        fillRight.fill((0,32,0))
        time.sleep(2)
        flash = EffectFlash(sender,config.BUTTON_LED_LEFT)
        
        flash.bRange = range(0,64,2)
        flash.color = (255,0,0)
        flash.setDuration(1)
        flash.repeat = -1
        flash.goThreaded()

        flashRight = EffectFlash(sender,config.BUTTON_LED_RIGHT)
        flashRight.bRange = range(0,64,1)
        flashRight.color = (255,255,0)
        flashRight.setDuration(1)
        flashRight.repeat = -1
        flashRight.goThreaded()


        time.sleep(20)
        flash.stop()
        flashRight.stop()

        rainbowLeft = EffectRainbow(sender, config.BUTTON_LED_LEFT)
        rainbowLeft.timing = 0.01
        rainbowLeft.repeat = -1
        rainbowLeft.goThreaded()

        rainbowRight = EffectRainbow(sender, config.BUTTON_LED_RIGHT)
        rainbowRight.timing = 0.02
        rainbowRight.repeat = -1
        rainbowRight.goThreaded()

        time.sleep(15)
        rainbowLeft.stop()
        rainbowRight.stop()

        clean = Effect(sender)
        clean.fill((0,0,0))

        countdownLeft = EffectCount(sender,config.BUTTON_LED_LEFT)
        countdownLeft.direction = -1
        countdownLeft.color = (0,64,0)
        countdownLeft.setDuration(3)
        countdownLeft.goThreaded()
        
        countdownRight = EffectCount(sender,config.BUTTON_LED_RIGHT)
        countdownRight.color = (0,0,64)
        countdownRight.direction = 1
        countdownRight.setDuration(4)
        countdownRight.goThreaded()
        
        time.sleep(30)
        countdownLeft.stop()
        time.sleep(5)
        
        clean = Effect(sender)
        clean.fill((0,0,0))
        time.sleep(1)

main()