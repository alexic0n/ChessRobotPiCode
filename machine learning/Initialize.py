import keras
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
    model.load_weights('model/model.h5')
    print("WEIGHTS LOADED")
    return model

