import tensorflow as tf
import numpy as np
import csv
import cv2
from scipy import ndimage
import os
import sklearn
from sklearn.model_selection import train_test_split

global SOURCE_PATH, EPOCHS
SOURCE_PATH = 'new_data2/'
EPOCHS = 1

def create_model():
    
    print("Creating Model")

    # Ask to create a new model or use an existing one

    if input("Want a new model[y/n] : ") == 'n' and 'model.h5' in os.listdir():
        print("-------------------------------- Loading previous model --------------------------------")
        model = tf.keras.models.load_model('model.h5')
    
    else:
        print("-------------------------------- Creating new model --------------------------------")
        model = tf.keras.models.Sequential([
                            tf.keras.layers.Lambda(lambda x: x / 255.0 - 0.5, input_shape=(160, 320, 3)),
                            tf.keras.layers.Cropping2D(cropping=((50, 20), (0, 0))),
                            tf.keras.layers.Conv2D(6, (5, 5), activation='relu'),
                            tf.keras.layers.MaxPooling2D(),
                            tf.keras.layers.Conv2D(6, (3, 3), activation='relu'),
                            tf.keras.layers.MaxPooling2D(),
                            tf.keras.layers.Flatten(),
                            tf.keras.layers.Dense(120),
                            tf.keras.layers.Dense(84),
                            tf.keras.layers.Dense(1)])

        model.compile(loss='mse', optimizer='adam')
    return model
    

def generator(samples, batch_size=32):

    num_samples = len(samples)
    np.random.shuffle(samples)

    while 1: # Loop forever so the generator never terminates
        
        for offset in range(0, num_samples, batch_size):

            batch_samples = samples[offset:offset+batch_size]

            images = []
            measurements = []

            for batch_sample in batch_samples:

                source_path = batch_sample[0][batch_sample[0].index('IMG'):]
                filename = SOURCE_PATH + source_path
                image = cv2.imread(filename)[:, :, ::-1]
                images.append(image)
                measurements.append(float(batch_sample[3]))

            X_train = np.array(images)
            y_train = np.array(measurements)

            yield sklearn.utils.shuffle(X_train, y_train)

def train_model(model):
    
    global SOURCE_PATH, EPOCHS

    samples = []
    print("Reading CSV")
    with open(SOURCE_PATH + 'driving_log.csv') as csv_file:
        reader = csv.reader(csv_file)
        for line in reader:
            samples.append(line)
    
    train_samples, validation_samples = train_test_split(samples, test_size=0.2)

    train_generator = generator(train_samples, batch_size=512)
    validation_generator = generator(validation_samples, batch_size=512)
    
    try:
        for epoch in range(EPOCHS):
            
            print(f"In Epoch : {epoch}")
            
            x_train, y_train = next(train_generator)
            x_val, y_val = next(validation_generator)

            model.fit(x_train, y_train, steps_per_epoch=len(x_train), validation_data=(x_val, y_val), epochs=1)
    except KeyboardInterrupt:
        pass
    
    model.save('model.h5')