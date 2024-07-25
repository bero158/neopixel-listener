import config
import logging as LOGGER
import time
import threading


class Effect:
    def __init__(self, sender, buttonRange = config.BUTTON_LED_ALL):
        self.run = True #tells the effect to be running
        self.buttonRange = buttonRange
        self.sender = sender
        self.repeat = 1
    
    def setDuration(self, duration_s):
        self.timing = duration_s / len(self.buttonRange)
    
    def go(self):
        iter = self.repeat
        while (iter > 0 or self.repeat == -1) and self.run: # -1 = forever
            self.goOnce()
            iter -= 1

    def goOnce(self):
        ...
    
    def goThreaded(self):
        self.thread = threading.Thread(target=self.go, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.run = False
    
    def fill(self,color):
        pixels = [(i,color) for i in self.buttonRange]
        self.sender.addQueue(pixels)



class EffectFade(Effect):

    def goOnce(self):
        for brightness in self.bRange:
            self.fill((self.color[0] * brightness // 255, self.color[1] * brightness // 255, self.color[2] * brightness // 255))
            time.sleep(self.timing)
            if not self.run:
                    break

    def setDuration(self, duration_s):
        self.timing = duration_s / len(self.bRange)
    
class EffectFlash(Effect):
    def startFade(self,bRange):
        self.effect = EffectFade(self.sender,self.buttonRange)
        self.effect.color = self.color
        self.effect.bRange = bRange
        self.effect.timing = self.timing / 2
        self.effect.go()

    def goOnce(self):
        self.startFade(self.bRange)
        if self.effect.run:
            back = range(self.bRange.stop - self.bRange.step, self.bRange.start - self.bRange.step, 0 - self.bRange.step)
            self.startFade(back)

    def stop(self):
        super().stop()
        if self.effect:
            self.effect.stop()

    def setDuration(self, duration_s):
        self.timing = duration_s / len(self.bRange)
    

class EffectRainbow(Effect):
    def goOnce(self):
        LOGGER.debug("running rainbow cycle")
        for j in range(255):
            pixels = []
            for i in self.buttonRange:
                pixel_index = (i * 256 // len(self.buttonRange)) + j
                pixels.append((i,self.wheel(pixel_index & 255)))
            else:
                self.sender.addQueue(pixels)
                time.sleep(self.timing)
                if not self.run:
                    break

    def wheel(self,pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)

class EffectCount(Effect):
    direction = -1 #-1 = Down, 1 = Up
    def goOnce(self):
        LOGGER.debug(f"running countdown {self.buttonRange.start} - {self.buttonRange.stop}")
        for i in self.buttonRange:
            if self.direction == -1:
                led = self.buttonRange.stop - i - 1 + self.buttonRange.start
            else:
                led = i

            self.sender.addQueueOne((led,self.color))
            time.sleep(self.timing)
            if not self.run:
                break


