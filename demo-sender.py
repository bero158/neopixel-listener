from multiprocessing.connection import Client
import config
import logging as LOGGER
import time
import threading

LOGGER.basicConfig(level=config.LOGLEVEL)

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


class Sender:
    

    def __init__(self):
        self.run = False
        self.senderThread = None
        self.queue=[]
        self.senderSleeper = 1 # wait 1s in sender thread
        self.lock = threading.Condition()

    def stop(self):
        self.run = False
        with self.lock: 
            self.lock.notify_all()


    def startThread(self):
        if not self.run:
            return
        if not self.senderThread:
            self.senderThread = threading.Thread(target=self.queueSenderThread, daemon=True)
            self.senderThread.start()
        else:
            if not self.senderThread.is_alive():
                self.senderThread = threading.Thread(target=self.queueSenderThread, daemon=True)
                self.senderThread.start()

            

    def connect(self):
        address = ('localhost', config.PORT)     # family is deduced to be 'AF_INET'
        try:
            self.conn = Client(address, authkey = config.AUTHKEY)
            self.run = True
            self.startThread()
            
        except (ConnectionRefusedError, BrokenPipeError) as e:
            LOGGER.error(f"Connection Refused {e.strerror}")

    def disconnect(self):
        if self.senderThread:
            self.stop()

        if self.conn:
            self.conn.close()

    def queueSenderThread(self):
        with self.lock:
            while self.run: 
                self.lock.wait()
                if not self.run:
                    break
                if self.queue:
                    qcopy = self.queue
                    self.queue = []
                    try:
                        self.sendPixels(qcopy)
                    except (BrokenPipeError) as e:
                        LOGGER.error(f"Disconnected {e.strerror}")
                        break
    def addQueue(self,pixels):
        if self.conn and self.run:
            self.queue.extend(pixels)
            self.senderSleeper = 0 #send immediately
            with self.lock: 
                self.lock.notify_all()

    def addQueueOne(self,pixel):
        if self.conn and self.run:
            self.queue.append(pixel)
            self.senderSleeper = 0 #send immediately
            with self.lock: 
                self.lock.notify_all()


    def send(self,data):
        self.conn.send(data)
        LOGGER.debug(f"Sending {data}") 

    def sendPixels(self, pixels):
        self.send(pixels)

    def sendPixel(self, pixel, color):
        pixels = [(pixel,color)]
        self.sendPixels(pixels)

def main():
    sender = Sender()
    sender.connect()
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
    sender.disconnect()
main()