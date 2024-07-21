import logging as LOGGER
import config
import pixel
from multiprocessing.connection import Listener
import time


LOGGER.basicConfig(level=config.LOGLEVEL)



def command(cmd):
    LOGGER.debug(f"Cmd = {cmd}") 
    if cmd:
        fnc = cmd.get("fnc")
        if fnc == "clean":
            pixel.clean()
        elif fnc == "close":
            return False # False means close
        elif fnc == "fill":
            args = cmd.get("args")
            if args:
                color = args.get("color")
                pixel.fill(color)
    return True
        

def main():
    pixel.clean()
    LOGGER.info(f"Neopixel Listener starting") 
    pixel.fill((255,0,0))
    time.sleep(0.3)
    pixel.fill((0,255,0))
    time.sleep(0.3)
    pixel.fill((0,0,255))
    time.sleep(0.3)
    pixel.clean()

    address = ('localhost', config.PORT)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey = config.AUTHKEY)
    LOGGER.info(f"Neopixel Listener waiting for connection at {listener.address}") 
    cont = True
    try:
        while cont:
            conn = listener.accept()
            LOGGER.info(f"connection accepted from {listener.last_accepted}") 
            pixel.fill((64,32,0))
            pixel.clean()
            
            while conn:
                try:
                    data = conn.recv()
                except EOFError as e:
                    LOGGER.error(f"Connection closed {e}") 
                    conn = None
                    pass #ignore
                LOGGER.debug(f"Data recieved {data}") 

                if data:
                    pixel.set(data)
    except KeyboardInterrupt:
        pass

    listener.close()
    pixel.clean()
    LOGGER.info(f"Closed") 

main()