from multiprocessing.connection import Client
from . import config
import logging as LOGGER
import threading
import time
from collections import deque

class Sender:
    def __init__(self):
        self.run = False
        self.senderThread = None
        self.queue = deque(maxlen=1024)
        self.senderSleeper = 1 # wait 1s in sender thread
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self.conn = None
        self.address = ('localhost', config.PORT)     # family is deduced to be 'AF_INET'
        
    def stop(self):
        self.run = False
        with self.cond: 
            self.cond.notify_all()

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
    
    def start(self):
        self.run = True
        if not self.senderThread:
            self.senderThread = threading.Thread(target=self.sender, daemon=True)
            self.senderThread.start()
        else:
            if not self.senderThread.is_alive():
                self.senderThread = threading.Thread(target=self.sender, daemon=True)
                self.senderThread.start()

    
    def sendQueue(self):
        if not self.conn:
            return
        with self.cond:
            while self.run: 
                self.cond.wait()
                if not self.run: 
                    break
                if self.queue:
                    with self.lock:
                        qcopy = self.queue.copy()
                        self.queue.clear()
                    self.send(qcopy)


    def sender(self):
        while self.run: 
            try:
                LOGGER.debug(f"Connecting to {self.address}")
                self.conn = Client(self.address, authkey = config.AUTHKEY)
                self.sendQueue()
                self.conn.close()
            except ConnectionError as e:
                LOGGER.error(f"Unable to connect to {self.address} {e.strerror}")
                time.sleep(1) # wait 1s then try connect again
        
    def notifyThread(self):
        with self.cond: 
            self.cond.notify_all()

    def addQueue(self,pixels):
        if self.conn and self.run:
            with self.lock:
                if isinstance(pixels,list):
                    self.queue.extend(pixels)
                else:
                    self.queue.append(pixels)
            self.notifyThread()
    
    def send(self,pixels):
        buffer = bytes()
        for pixel in pixels:
            buffer += bytes((pixel[0],))
            buffer += bytes(pixel[1])
        self.conn.send_bytes(buffer)

