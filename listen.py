import logging as LOGGER
import config
if config.DUMMY:
    import pixel_dummy as pixel
else:
    import pixel
from multiprocessing.connection import Listener
import time


LOGGER.basicConfig(level=config.LOGLEVEL)

def main():
    pixel.clean()
    LOGGER.info(f"Neopixel Listener starting") 
    pixel.fill((255,0,0)) # check red
    time.sleep(0.3)
    pixel.fill((0,255,0)) # check green
    time.sleep(0.3)
    pixel.fill((0,0,255)) # check bloe
    time.sleep(0.3)
    pixel.fill((8,8,8)) # set soft white as waiting for initial connection indicator

    address = ('localhost', config.PORT)     # family is deduced to be 'AF_INET'
    with Listener(address, authkey = config.AUTHKEY) as listener:
        try:
            while True:
                LOGGER.info(f"Neopixel Listener is waiting for connection at {listener.address}") 
                with listener.accept() as conn:
                    LOGGER.info(f"connection accepted from {listener.last_accepted}") 
                    pixel.clean()
                    while conn:
                        try:
                            datab = conn.recv_bytes()
                            LOGGER.debug(f"Data recieved {datab}") 
                            length = len(datab)
                            data = []
                            for n in range(0,length,4):
                                pixelB = (datab[n:n+4])
                                if len(pixelB) == 4:
                                    data.append((pixelB[0],tuple(pixelB[1:])))
                            pixel.set(data)
                        except (EOFError, ConnectionResetError) as e:
                            LOGGER.error(f"Connection closed {e}") 
                            conn = None
                            pass #ignore
        except KeyboardInterrupt:
            pass


    pixel.clean()
    LOGGER.info(f"Closed") 

main()