import logging as LOGGER
import time
import threading
import config
import collections
from sender import Sender

# Neopixel gama correction. Taken from neopixel example
gamma8 = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

def calcColor(color : tuple, brightness : int):
    brightness = gamma8[brightness]
    return (color[0] * brightness // 255, color[1] * brightness // 255, color[2] * brightness // 255)

class Locker:
    locked : list[int]

    def __init(self):
        self.locked=[0]*len(config.LED_ALL)
    
    def lock(self, leds : range, level : int):
        for i in leds:
            self.locked[i] = level


class Effect:
    running : bool # running state
    leds : range # physical LED mapping
    sender : Sender # sender class
    repeat : int # count of iterations
    syncWith : object # Effect class multithreading synchronisation with other thread
    ledLength : int # Length of my part of the strip. Calculated from leds
    logLeds : int # Logical leds (starting with 0)
    color : tuple # (R,G,B) LED color
    backColor : tuple # (R,G,B) LED color for clearing etc.
    tempColor : tuple # (R,G,B) LED temporary color applied at next round only.
    mirror : bool = False # mirroring to other side
    timing : float # one step delay
    stepping : int # how many steps in one step
    def __init__(self, sender : Sender, physLeds : range, syncWith : object = None):
        """
        sender = sender class. Must be created and set before.
        leds = Physical mappintto button LED
        syncWith = Synchronisation between worker threads. If used sleep in thread is replaced with waiting."""
        self.running = True #tells the effect to be running
        self.leds = physLeds
        self.sender = sender
        self.repeat = 1
        self.syncWith = syncWith
        self.ledLength = len(self.leds)    
        self.logLeds = range( 0, self.ledLength, physLeds.step )
        self.tempColor = None
        self.mirror = False
        self.timing = 0
        self.stepping = 1
        self.backColor = (0,0,0)
        
    def setDuration(self, duration_s):
        """Duration of one whole cycle. For threaded output"""
        self.timing = duration_s / len(self.leds)
    
    def go(self):
        """Thread main cycle. Don't call directly. Started through goThreaded"""
        iter = self.repeat
        while (iter > 0 or self.repeat == -1) and self.running: # -1 = forever
            self.goOnce()
            if self.repeat > 0:
                iter -= 1
        self.running = False

    def next(self, steps : int = 1):
        """Math should be here. Implement in inherited classes"""
        ...
    
    def goOnce(self):
        LOGGER.debug(f"running {self.leds.start} - {self.leds.stop}")
        steps = len(self.logLeds)//2 if self.mirror else len(self.logLeds)
        steps = steps//self.stepping
        for _ in range(steps):
            self.next(self.stepping)
            time.sleep(self.timing)
            if not self.running:
                break
    
    def run(self, threaded = False):
        """Call this for starting the effect!"""
        if threaded:
            self.goThreaded() # nonblocking
        else:
            self.go() # blocking

    def goThreaded(self):
        """Threaded run"""
        self.thread = threading.Thread(target=self.go, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stops the effect thread"""
        self.running = False
    
    def fill(self,color : tuple = None):
        """Fill witn one color. For clearing etc."""
        color = color if color else self.color
        pixels = [(i,color) for i in self.leds]
        self.sender.addQueue(pixels)

    def clear(self):
        """clears the led strip"""
        self.fill(self.backColor)
        



class EffectShine(Effect):
    def goOnce(self):
        """one passthrough, waiting"""
        # pdb.set_trace()
        LOGGER.debug("EffectShine On")
        self.fill((self.color))
        time.sleep(self.timing)
        self.fill((0,0,0))
        LOGGER.debug("EffectShine Off")
    
    def setDuration(self, duration_s):
        self.timing = duration_s

class EffectFade(Effect):
    bRange : range # brightness range
    currentBrightness : int # for sharing between threads
    def goOnce(self):
        """one passthrough, waiting"""
        for brightness in self.bRange:
            self.currentBrightness = brightness
            if self.syncWith:
                if (hasattr(self.syncWith,"effect")):
                    brightness = self.syncWith.effect.currentBrightness
            self.fill( calcColor(self.color, brightness ))
            time.sleep(self.timing)
            if not self.running:
                break

    def setDuration(self, duration_s):
        self.timing = duration_s / len(self.bRange)
    
class EffectFlash(Effect):
    def startFade(self,bRange : range, color : tuple):
        self.effect = EffectFade(self.sender, physLeds = self.leds, syncWith = self.syncWith)
        self.effect.timing = self.timing / 2
        self.effect.bRange = bRange
        self.effect.color = color
        self.effect.go()

    def goOnce(self):
        oldtempColor = self.tempColor 
        color = self.color if oldtempColor == None else oldtempColor
        self.startFade(self.bRange, color)
        if self.running:
           # back = range(self.bRange.stop - self.bRange.step, self.bRange.start - self.bRange.step, 0 - self.bRange.step)
           back = reversed(self.bRange)
           self.startFade(back, color)
        if oldtempColor: #only when temp color was previously set.
            self.tempColor = None 

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
            for i in self.leds:
                pixel_index = (i * 256 // len(self.leds)) + j
                pixels.append((i,self.wheel(pixel_index & 255)))
            else:
                self.sender.addQueue(pixels)
                time.sleep(self.timing)
                if not self.running:
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

class LogicalMapping(Effect):
    def log2physLed(self, logLed : int) -> int:
        logLed = logLed*self.leds.step+self.offset
        pos = logLed%self.ledLength
        physLed = self.leds.start + pos
        return physLed
    
    def addQueue(self, led : int, color : tuple = None):
        if not color:
            color = self.color
        physLed = self.log2physLed(led)
        self.sender.addQueue((physLed,color))

class EffectCount(LogicalMapping):
    direction : int = -1 #-1 = Down, 1 = Up
    pos : int = 0
    offset : int = 0 # starting position
    
    
    
    def step(self, i : int):
        if self.direction == -1:
            led = (self.ledLength - 1) - i
        else:
            led = i
        self.addQueue(led)

        if self.mirror:
            # add mirrored side
            ledM =  0 - led
            ledM = ledM%(self.ledLength )
            self.addQueue(ledM)

    def reset(self):
            self.pos = 0
    
    def next(self, steps : int = 1):
        for i in range(steps):
            self.step(self.pos)
            self.pos += 1

            if self.pos < 0:
                self.pos = 0
            if self.pos > self.ledLength:
                self.pos = self.ledLength
    
    def repaint(self):
        """repaints last state. Intended use is for effect mixing"""
        for i in range(0, self.pos):
            self.step(i)
            
class EffectShiftRegister(LogicalMapping):
    register : collections.deque
    injectQueue : list
    def __init__(self, *args, **kwargs):
        super(LogicalMapping,self).__init__(*args, **kwargs)
        self.reset()
        self.injectQueue = []

    def reset(self):
        self.register=collections.deque( [(0,0,0)]*self.ledLength , maxlen=self.ledLength)
                
    def set(self, vals : collections.deque):
        self.reset()
        for i, val in enumerate(vals):
            self.register[i] = val
    
    def rotate(self, n : int):
        self.register.rotate(n)

    def repaint(self):
        for led,color in enumerate(self.register):
            self.addQueue(led,color)

    def next(self, steps : int = 1):
        """Shows the actual state and calls rotate"""
        self.repaint()
        if len(self.injectQueue):
            for _ in range(steps):
                if len(self.injectQueue):
                    self.inject(self.injectQueue.pop(0))
        else:
            self.rotate(steps*self.direction)

    def inject(self, color : tuple, n : int = 1):
        """inject a new value at the begining of the array"""
        for _ in range(n):
            self.register.pop()
            self.register.appendleft(color)
        
    def injectDelayed(self, color : tuple):
        """inject a new value at the begining of the array"""
        self.injectQueue.append(color)
        

class EffectComet(EffectShiftRegister):

    def injectComet(self, tail : int):
        self.injectDelayed((255,255,255))
        gradient = 255//tail
        for i in range( 0, tail ):
            self.injectDelayed(calcColor(self.color,255-(gradient*i)))    

class EffectDisco(EffectShiftRegister):
    def run(self, *args, **kwargs):
        for _ in range(len(self.leds)//self.stepping):
            self.inject(self.color,self.stepping)
            self.inject(self.backColor,self.stepping)
        super(EffectShiftRegister,self).run(*args, **kwargs)
        
