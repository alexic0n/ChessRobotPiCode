import pyaudio
import wave

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

def print_play(text, lang):
    text_sound_dict = {
        "Select language.":'lang',
        "Sorry, can you please repeat that?":'repeat',
        "Unable to detect microphone. Please unplug and plug it again.":'mic_not_detected',
        "Sorry I am having trouble understanding. Press q to exit or continue the game with keyboard control.":'unable_to_understand',
        "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead.":'server_down',
        "Hi there, I'm Checkmate, your personal chess playing assistant! Let's make the world of chess more exciting and fun!":'welcome',
        "Select or say 1 if you want to move your own pieces. Select or say 2 if you want me to move your pieces for you. Select or say 3 if you want me to replay your last game.":'user_robot_control',
        "Select or say 1 for keyboard control. Select 2 for voice control.":'user_options',
        "Checkmate: Game Over!":'game_over',
        "You are in check...save your king!":'check',
        "Make your move on the board. Confirm by pressing 1.":'move_user_button',
        "You can only make queen promotion. Please place the queen on the desired square and press yes when you are done.":'promotion',
        "You have made queenside castling. Is this correct? y or n":'queenside_castling',
        "You have made kingside castling. Is this correct? y or n":'kingside_castling',
        "Are you sure that you made a legal move? y or n":'legal_move',
        "Please make a new move. Press 1 to confirm.":'move_again_user',
        "Your move is invalid. Please make a new move and confirm it by pressing 1.":'invalid_move',
        "Please confirm the board is clear before proceeding by pressing 1.":'board_clear',
        "1.Select mode of play (e for easy, m for moderate, h for hard, p for pro):":'mode_of_play_button',
        "2.Select mode of play (e for easy, m for moderate, h for hard, p for pro):":'mode_of_play_speech',
        "1.White or black? w or b: ":'white_black_button',
        "2.White or black? w or b: ":'white_black_speech',
        "You have selected white.":'white',
        "You have selected black.":'black',
        "Congratulations! You won the game.":'won',
        "I made kingside castling. Your turn!":'robot_kingside_castling',
        "I made queenside castling. Your turn!":'robot_queenside_castling',
        "Please choose your next move and press 1 when you are ready to announce it.":'move_robot',
        "You want to make kingside castling. Is this correct?":'next_move_kingside_castling',
        "You want to make queenside castling. Is this correct?":'next_move_queenside_castling',
        "Please press 1 again when you are ready to announce your move.":'move_again_robot',
        "You haven't played any games yet.":'no_games',
        "You played with white.":'prev_white',
        "You played with black.":'prev_black',
        "Piece taken! Please remove it from the gripper and press yes.":'take_piece'
    }
    path = 'sounds/'
    
    if (text == "Select language."):
        print("Press the button with the British flag for English. Drücken Sie die Schaltfläche mit der deutschen Flagge für Deutsch. 按下中文按钮")

        play_sound(path + text_sound_dict.get(text) + '_' + 'en' + '.wav')
        #play_sound(path + text_sound_dict.get(text) + '_' + 'es' + '.wav')
        #play_sound(path + text_sound_dict.get(text) + '_' + 'fr' + '.wav')
        play_sound(path + text_sound_dict.get(text) + '_' + 'de' + '.wav')
        play_sound(path + text_sound_dict.get(text) + '_' + 'zh-cn' + '.wav')
    
    if (text == "Sorry, can you please repeat that?"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "Unable to detect microphone. Please unplug and plug it again."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "Sorry I am having trouble understanding. Press q to exit or continue the game with keyboard control."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if(text == "Hi there, I'm Checkmate, your personal chess playing assistant! Let's make the world of chess more exciting and fun!"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Select or say 1 if you want to move your own pieces. Select or say 2 if you want me to move your pieces for you. Select or say 3 if you want me to replay your last game."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Select or say 1 for keyboard control. Select 2 for voice control."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "Checkmate: Game Over!"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "You are in check...save your king!"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "Make your move on the board. Confirm by pressing 1."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "You can only make queen promotion. Please place the queen on the desired square and press yes when you are done."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if (text == "You have made queenside castling. Is this correct? y or n"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
    
    if(text == "You have made kingside castling. Is this correct? y or n"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Are you sure that you made a legal move? y or n"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Please make a new move. Press 1 to confirm."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Your move is invalid. Please make a new move and confirm it by pressing 1."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Please confirm the board is clear before proceeding by pressing 1."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "1.Select mode of play (e for easy, m for moderate, h for hard, p for pro):"):
        print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "2.Select mode of play (e for easy, m for moderate, h for hard, p for pro):"):
        print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "1.White or black? w or b: "):
        print("White or black? w or b: ")
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "2.White or black? w or b: "):
        print("White or black? w or b: ")
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "You have selected white."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "You have selected black."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "Congratulations! You won the game."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "I made kingside castling. Your turn!"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav') 
        
    if (text == "I made queenside castling. Your turn!"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
             
    if (text == "Please choose your next move and press 1 when you are ready to announce it."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
             
    if (text == "You want to make kingside castling. Is this correct?"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
             
    if (text == "You want to make queenside castling. Is this correct?"):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
             
    if (text == "Please press 1 again when you are ready to announce your move."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "You haven't played any games yet."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "You played with white."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "You played with black."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
    if (text == "Piece taken! Please remove it from the gripper and press yes."):
        print(text)
        play_sound(path + text_sound_dict.get(text) + '_' + lang + '.wav')
        
        
