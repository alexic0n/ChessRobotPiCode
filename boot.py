from pyglet.window import key
import threading
import subprocess
import keyboardleds

window = pyglet.window.Window()
on = False
game = None
numlock = keyboardleds.LedKit(
    '/dev/input/by-id/usb-04d9_1203-event-kbd').num_lock


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.NUMLOCK:
        if on and game:
            print("Killing game")
            game.kill()
            on = False
        else:
            startGame()


@window.event
def on_draw():
  window.clear()


def startGame():
    if (not on) and (game == None):
        print("Starting game")
        game = popenAndCall(gameStopped, 'python3 ./start.py')
        on = True
    if (not on) and game:
        # something's gone wrong
        raise Exception("Game still exists, cannot turn on.")
    if on:
        return


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
        pass