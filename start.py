# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
import getch
import pyaudio
import wave
import requests
import signal
import pygame
from mainUserMoves import main as main_user
from mainRobotMoves import main as main_robot
from dictionary import print_play, play_sound, play_sound_pyaudio
from replay import main as replay_game

# Audio settings
mic_name = 'USB Device 0x46d:0x8b2: Audio'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 4 # seconds to record
wav_output_filename = 'audio.wav' # name of .wav file
    
def handler(signum, frame):
    raise Exception("end of time")
    
def detect_keyboard(time):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function
    signal.alarm(time)
    try:
        try:
            control = getch.getch()
            pygame.mixer.music.stop()
        except OverflowError as exc:
            print(exc)
            control = ""
    except Exception as exc: 
        print(exc)
        control = ""
        
    signal.alarm(0)
    
    return control

def speech_or_keyboard(question, lang):
    text = "Sorry, can you please repeat that?"
    count = 0
    
    while (text == "Sorry, can you please repeat that?"):
        time = 3
        
        #Initalize microphone
        audio = pyaudio.PyAudio()
        
        dev_index = -1
        for ii in range(audio.get_device_count()):
            name = audio.get_device_info_by_index(ii).get('name')
            if (mic_name in name):
                dev_index = ii 
        
        if (dev_index == -1):
            control = detect_keyboard(time)
            
            if (control == '5'):
                control = '2'
            elif (control == '6'):
                control = '3'
            elif (control == '+'):
                control = '4'
            elif (control == '4'):
                control = '1'
            
            if (control == '1' or control == '3' or control == '4'):
                return control
            elif (control == '2'):
                print_play("Unable to detect microphone. Please unplug and plug it again.", lang)
                sys.exit()
            else:
                if (question == 1):
                    print_play("Unable to detect microphone. Please unplug and plug it again or continue by selecting option 1 or 3.", lang)
                else:
                    print_play("Continue by selecting option 1.", lang)

                control = getch.getch()
                pygame.mixer.music.stop()
                
                if (control == '5'):
                    control = '2'
                elif (control == '6'):
                    control = '3'
                elif (control == '+'):
                    control = '4'
                elif (control == '4'):
                    control = '1'
                
                if (not control == '1' and not control == '3' and not control == '4'):
                    print_play("Unable to detect microphone. Please unplug and plug it again.", lang)
                    sys.exit()
                else:
                    return control
                
        # create pyaudio stream
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        print("recording")
        frames = []
        
        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk, exception_on_overflow = False)
            frames.append(data)
        
        print("finished recording")
        
        control = detect_keyboard(time)
        print(control)
        
        if (control == '5'):
            control = '2'
        elif (control == '6'):
            control = '3'
        elif (control == '+'):
            control = '4'
        elif (control == '4'):
            control = '1'

        if (control == '1' or control == '2' or control == '3' or control == '4'):
            audio.terminate()
            return control
        
        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        
        r = requests.post("http://www.checkmate.tardis.ed.ac.uk/speech_recognition", files={
            'user_speech': open('audio.wav', 'rb'),
            'lang':lang
        })
    
        data = r.json()
        
        text = data['text']
        if (text == "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."):
            print_play(text, lang)
            sys.exit()
        if (text == "Sorry, can you please repeat that?" or not(text[0]=='o' or text[0]=='t' or text[0]=='f')):
            if (count == 3):
                print_play("Sorry I am having trouble understanding. Press q to exit or continue the game with keyboard control.", lang)
                
                control = getch.getch()
                pygame.mixer.music.stop()
                
                if (control == '5'):
                    control = '2'
                elif (control == '6'):
                    control = '3'
                elif (control == '+'):
                    control = '4'
                elif (control == '4'):
                    control = '1'
                
                audio.terminate()
                return control
                    
            count = count + 1
            
            print_play(text, lang)
        else:
            if (text[0] == 'o'):
                control = '1'
            elif (text == 'two'):
                control = '2'
            elif (text == 'three'):
                control = '3'
            elif (text == 'four'):
                control = '4'
            audio.terminate()
            return control
        
def main():
    play_sound_pyaudio('sounds/startup.wav')
    lang_num = print_play("Select language.", '')
    lang_num = getch.getch()
    pygame.mixer.music.stop()
    
    if (lang_num == '7'):
        lang_num = '2'
    elif (lang_num == '8'):
        lang_num = '3'
    elif (lang_num == '9'):
        lang_num = '4'
    elif (lang_num == '-'):
        lang_num = '5'
    else:
        lang_num = '1'
    
    lang_dict = {
        "1":'en',
        "2":'es',
        "3":'fr',
        "4":'de',
        "5":'zh-cn'
    }
    
    lang = lang_dict.get(lang_num, 'en')
    
    play_sound_pyaudio('sounds/welcome_en.wav')
    #print_play("Hi there, I'm Checkmate, your personal chess playing assistant! Let's make the world of chess more exciting and fun!", lang)
    
    print_play("Select or say 1 if you want to move your own pieces. Select or say 2 if you want me to move your pieces for you. Select or say 3 if you want me to replay your last game. Select or say 4 if you want to replay the legendary game Kasparov versus Deep Blue.", lang)

    control = getch.getch()
    pygame.mixer.music.stop()
    print(control)
    
    if (control == '5'):
        control = '2'
    elif (control == '6'):
        control = '3'
    elif (control == '+'):
        control = '4'
    elif (control == '4'):
        control = '1'
    
    if(control == 'q'):
        sys.exit()
    else:
        if (control == '4'):
            #Replay Kasparov
            replay_game(lang, True)    
            
        elif (control == '3'):
            replay_game(lang, False)
            
        elif (control == '2'):
            main_robot(lang)
            
        else:
            print_play("Select or say 1 for keyboard control. Select 2 for voice control.", lang, True)
            control = speech_or_keyboard(2, lang)
            if(control == 'q'):
                sys.exit()
            main_user(control, lang)
        


if __name__ == '__main__':
    main()
