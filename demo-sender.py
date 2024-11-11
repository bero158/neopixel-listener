import config
import logging as LOGGER
import time
from led_effects import PrivilegedSender
import led_effects as effects

LOGGER.basicConfig(level=config.LOGLEVEL)

def main():
    with PrivilegedSender() as sender:
        """
        fillLeft = Effect(sender,config.LED_LEFT)
        fillLeft.fill((32,16,0))
        fillRight = Effect(sender,config.LED_RIGHT)
        fillRight.fill((0,32,0))
        time.sleep(2)
        flash = EffectFlash(sender,config.LED_LEFT)
        
        flash.bRange = range(0,64,2)
        flash.color = (255,0,0)
        flash.setDuration(1)
        flash.repeat = -1
        flash.goThreaded()

        flashRight = EffectFlash(sender,config.LED_RIGHT)
        flashRight.bRange = range(0,64,1)
        flashRight.color = (255,255,0)
        flashRight.setDuration(1)
        flashRight.repeat = -1
        flashRight.goThreaded()


        time.sleep(20)
        flash.stop()
        flashRight.stop()

        rainbowLeft = EffectRainbow(sender, config.LED_LEFT)
        rainbowLeft.timing = 0.01
        rainbowLeft.repeat = -1
        rainbowLeft.goThreaded()

        rainbowRight = EffectRainbow(sender, config.LED_RIGHT)
        rainbowRight.timing = 0.02
        rainbowRight.repeat = -1
        rainbowRight.goThreaded()

        time.sleep(15)
        rainbowLeft.stop()
        rainbowRight.stop()

        clean = Effect(sender,config.LED_ALL )
        clean.fill((0,0,0))

        countdownLeft = EffectCount(sender,config.LED_LEFT)
        countdownLeft.direction = -1
        countdownLeft.color = (0,64,0)
        countdownLeft.setDuration(3)
        countdownLeft.goThreaded()
        
        countdownRight = EffectCount(sender,config.LED_RIGHT)
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
        """
        time.sleep(0.5) #wait for sender thread init
        countdownLeft = effects.EffectCount(sender,config.LED_LEFT)
        countdownLeft.direction = 1
        countdownLeft.mirror = True
        countdownLeft.offset = 7
        countdownLeft.color = (0,64,0)
        countdownLeft.setDuration(1)
        countdownLeft.goOnce()
        countdownLeft.reset()
        countdownLeft.offset = 14
        countdownLeft.color = (255,255,255)
        countdownLeft.goOnce()
        countdownLeft.fill((0,0,0))

        srRight = effects.EffectShiftRegister(sender,config.LED_RIGHT)
        srRight.direction = 1
        srRight.offset = 7
        srRight.setDuration(1)
        # srRight.set([(64,0,32),(255,0,0)])
        srRight.reset()
        srRight.inject((64,0,32))
        srRight.repeat = 2
        srRight.run()

        srRight = effects.EffectComet(sender,config.LED_RIGHT)
        srRight.direction = 1
        srRight.offset = 7
        srRight.color=(0,255,0)
        srRight.setDuration(1)
        srRight.injectComet(2)
        srRight.repeat = 2
        srRight.run()

        srRight = effects.EffectDisco(sender,config.LED_RIGHT)
        srRight.direction = 1
        srRight.offset = 7
        srRight.color=(255,0,255)
        srRight.backColor=(0,255,0)
        srRight.setDuration(5)
        srRight.repeat = -1
        srRight.stepping = 3
        
        srLeft = effects.EffectDisco(sender,config.LED_LEFT, syncWith = srRight)
        srLeft.direction = 1
        srLeft.offset = 7
        srLeft.color=(255,0,255)
        srLeft.backColor=(0,255,0)
        srLeft.setDuration(5)
        srLeft.repeat = -1
        srLeft.stepping = 3
        srLeft.run(threaded = True)
        
        
        srRight.run(threaded = True)
        time.sleep(2)
        fillLeft = effects.Effect(sender,config.LED_LEFT,privilegeLevel=PrivilegedSender.Level.HIGH)
        fillLeft.lock()
        fillLeft.fill((32,16,0))
        time.sleep(2)
        fillLeft.unlock()
        time.sleep(5)

if __name__ == "__main__":
    main()