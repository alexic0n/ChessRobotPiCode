# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
import pyttsx3 as tts
import getch
from mainUserMoves import main as main_user
from mainRobotMoves import main as main_robot

def main():
    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 15)
    TextToSpeechEngine.setProperty("rate", 170)
    
    TextToSpeechEngine.say("Hi there, I'm Checkmate, your personal chess playing assistant! Let's make together the world of chess more exciting and fun!")
    TextToSpeechEngine.runAndWait()
    print("Hi there, I'm Checkmate, your personal chess playing assistant! Let's make together the world of chess more exciting and fun!")

    TextToSpeechEngine.say("Select 1 if you want to move your own pieces. Select 2 if you want Checkmate to move your pieces for you.")
    TextToSpeechEngine.runAndWait()
    print("Select 1 if you want to move your own pieces. Select 2 if you want Checkmate to move your pieces for you.")

    control = getch.getch()
    
    if(control == 'q'):
        sys.exit()
    else:
        if (control == '1'):
            TextToSpeechEngine.say("Select 1 for keyboard control. Select 2 for voice control.")
            TextToSpeechEngine.runAndWait()    
            print("Select 1 for keyboard control. Select 2 for voice control.")
            control = getch.getch()
            if(control == 'q'):
                sys.exit()
            main_user(control)
        else:
            main_robot()


if __name__ == '__main__':
    main()