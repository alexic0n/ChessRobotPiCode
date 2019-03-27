# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
import getch
import pyaudio
import wave
import requests
import signal
from mainUserMoves import main as main_user
from mainRobotMoves import main as main_robot

# Audio settings
mic_name = 'USB Device 0x46d:0x8b2: Audio (hw:1,0)'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 4 # seconds to record
wav_output_filename = 'audio.wav' # name of .wav file
    
def handler(signum, frame):
    raise Exception("end of time")
    
def detect_keyboard():
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function
    signal.alarm(5)
    try:
        try:
            control = getch.getch()
        except OverflowError as exc:
            print(exc)
            control = ""
    except Exception as exc: 
        print(exc)
        control = ""
        
    signal.alarm(0)
    
    return control

def play_sound(path):
    #define stream chunk   
    chunk = 1024  
    
    #open a wav format music  
    f = wave.open(path)  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  
    
    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    #stop stream  
    stream.stop_stream()  
    stream.close()  
    
    #close PyAudio  
    p.terminate()

def text_to_speech(text):
    r = requests.post("http://www.checkmate.tardis.ed.ac.uk/text_to_speech", files={
            'text': text,
        })

    with wave.open('sounds/audio.wav','wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(26500)
            file.writeframes(r.content)
    
    play_sound('sounds/audio.wav')

def speech_or_keyboard():
    text = "Sorry, can you please repeat that?"
    count = 0
    
    while (text == "Sorry, can you please repeat that?"):
        #Initalize microphone
        audio = pyaudio.PyAudio()
        
        dev_index = -1
        for ii in range(audio.get_device_count()):
            name = audio.get_device_info_by_index(ii).get('name')
            if (name == mic_name):
                dev_index = ii 
            
        if (dev_index == -1):
            play_sound('sounds/mic_not_detected.wav')
            print("Unable to detect microphone. Please unplug and plug it again.")
            sys.exit()
        
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
        
        control = detect_keyboard()

        if (control == '1' or control == '2'):
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
        })
    
        data = r.json()
        
        text = data['text']
        if (text == "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."):
            play_sound('sounds/server_down.wav')
            print(text)
            sys.exit()
        if (text == "Sorry, can you please repeat that?" or not(text[0]=='o' or text[0]=='t')):
            if (count == 3):
                play_sound('sounds/unable_to_understand.wav')
                print("Sorry I am having trouble understanding. Press q to exit or continue the game with keyboard control.")
                
                control = getch.getch()
                audio.terminate()
                return control
                    
            count = count + 1
            
            play_sound('sounds/repeat.wav')
            print(text)
        else:
            if (text[0] == 'o'):
                control = '1'
            else:
                control = '2'
            audio.terminate()
            return control

def main():
    print("Hi there, I'm Checkmate, your personal chess playing assistant! Let's make together the world of chess more exciting and fun!")
    play_sound('sounds/welcome.wav')
    
    print("Select or say 1 if you want to move your own pieces. Select or say 2 if you want Checkmate to move your pieces for you.")
    play_sound('sounds/user_robot_control.wav')

    control = speech_or_keyboard()
    
    if(control == 'q'):
        sys.exit()
    else:
        if (control == '1'):
            play_sound('sounds/user_options.wav')  
            print("Select or say 1 for keyboard control. Select 2 for voice control.")
            control = speech_or_keyboard()
            if(control == 'q'):
                sys.exit()
            main_user(control)
        else:
            main_robot()


if __name__ == '__main__':
    main()
