from multiprocessing.connection import Client
import config
import logging as LOGGER
import threading

LOGGER.basicConfig(level=config.LOGLEVEL)


class Sender:
    def __init__(self):
        self.run = False
        self.senderThread = None
        self.queue=[]
        self.senderSleeper = 1 # wait 1s in sender thread
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self.conn = None

    def stop(self):
        self.run = False
        with self.cond: 
            self.cond.notify_all()

    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()
    
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
        self.conn = Client(address, authkey = config.AUTHKEY)
        self.run = True
        self.startThread()
    

    def disconnect(self):
        if self.senderThread:
            self.stop()

        if self.conn:
            self.conn.close()

    def queueSenderThread(self):
        with self.cond:
            while self.run: 
                self.cond.wait()
                if not self.run:
                    break
                if self.queue:
                    with self.lock:
                        qcopy = self.queue
                        self.queue = []
                    try:
                        self.send(qcopy)
                    except (ConnectionError) as e:
                        LOGGER.error(f"Disconnected {e.strerror}")
                        break

    def addQueue(self,pixels):
        if self.conn and self.run:
            with self.lock:
                self.queue.extend(pixels)
            with self.cond: 
                self.cond.notify_all()

    def addQueueOne(self,pixel):
        if self.conn and self.run:
            with self.lock:
                self.queue.append(pixel)
            with self.cond: 
                self.cond.notify_all()


    def send(self,pixels):
        buffer = bytes()
        for pixel in pixels:
            buffer += pixel[0].to_bytes()
            buffer += bytes(pixel[1])
        self.conn.send_bytes(buffer)
        # self.conn.send(data)
        LOGGER.debug(f"Sent {buffer}") 

