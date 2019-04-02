import threading
import subprocess
import keyboardleds
from time import sleep

on = False
game = None
numlock = keyboardleds.LedKit(
    '/dev/input/by-id/usb-04d9_1203-event-kbd').num_lock


def gameStopped():
    print("Game process stopped")
    game = None
    on = False
    numlock.reset()


def popenAndCall(onExit, *popenArgs, **popenKWArgs):
    """
    Runs a subprocess.Popen, and then calls the function onExit when the
    subprocess completes.

    Use it exactly the way you'd normally use subprocess.Popen, except include a
    callable to execute as the first argument. onExit is a callable object, and
    *popenArgs and **popenKWArgs are simply passed up to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs, popenKWArgs):
        proc = subprocess.Popen(*popenArgs, **popenKWArgs)
        proc.wait()
        onExit()
        return

    thread = threading.Thread(target=runInThread,
                              args=(onExit, popenArgs, popenKWArgs))
    thread.start()

    return thread  # returns immediately after the thread starts


if __name__ == "__main__":
    print("CheckMate Bootstrapper starting.")
    numlock.reset()
    while True:
        state = numlock.get()
        if state == True:
            # num lock on
            if not on:
                # requested game start
                print("Starting game")
                if game != None:
                    # something's gone wrong
                    raise Exception("Game still exists, cannot turn on.")
                game = popenAndCall(gameStopped, 'python3 ./start.py')
                on = True

        else:
            # num lock off
            if on:
                # requested game terminate
                print("Killing game")
                game.kill()
                on = False
                game = None
    sleep(0.5)  

