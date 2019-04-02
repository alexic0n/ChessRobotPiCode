import threading
import subprocess
import multiprocessing
import keyboardleds
from time import sleep
from start import main

on = False
game = None


def gameStopped():
    print("Game process stopped")
    game = None
    on = False
    # clear numlock
    subprocess.call(['/usr/bin/setleds', '-num'])

def startandwait():
    main()
    gameStopped()


if __name__ == "__main__":
    print("CheckMate Bootstrapper starting.")
    # clear numlock
    subprocess.call(['/usr/bin/setleds', '-num'])
    while True:
        state = subprocess.check_output('/usr/bin/setleds')
        if b'on' in state:
            # num lock on
            if not on:
                # requested game start
                print("Starting game")
                if game != None:
                    # something's gone wrong
                    raise Exception("Game still exists, cannot turn on.")
                #game = popenAndCall(gameStopped, ['python3', './start.py'])
                game = multiprocessing.Process(target=startandwait)
                game.start()
                on = True

        else:
            # num lock off
            if on:
                # requested game terminate
                print("Killing game")
                game.terminate()
                on = False
                game = None
    sleep(0.5)
