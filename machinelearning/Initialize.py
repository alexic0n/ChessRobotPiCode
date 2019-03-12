import keras
import os
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.metrics import categorical_crossentropy

def load_weights():
    # Loads the weigths for the neural network model

    vgg16_model = keras.applications.vgg16.VGG16()
    vgg16_model.layers.pop()
    model = Sequential()
    for layer in vgg16_model.layers:
        model.add(layer)
    model.add(Dense(6, activation='softmax'))
    model.compile(Adam(lr=.0001), loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', 'model.h5'))
    print("WEIGHTS LOADED")
    model._make_predict_function()
    return model

# lowercase - black
# uppercase - white
# * - empty square
# w - whites turn
# KQkq - castling available for both black and white
# '-' - no en passant available
# 0 - no half moves
# 1 - first move
def initialize_fen():
    # Initializes the board state with correctly set up pieces for the beginning of the game

    fen_notation='rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    if not os.path.exists("./Board State/previousFEN.txt"):
        with open("./Board State/previousFEN.txt", "w+") as text_file:
            print(fen_notation, file=text_file)
