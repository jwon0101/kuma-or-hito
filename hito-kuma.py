# -*- coding: utf-8 -*-
"""hackathon

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12rC_CH0Knduk5UH1zA7MAs_qWCaASPTW
"""

# Mount
from google.colab import drive
drive.mount('/content/drive/')

# Imports
import os, warnings
import matplotlib.pyplot as plt
from matplotlib import gridspec

import cv2
from google.colab.patches import cv2_imshow

import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.layers.experimental import preprocessing
import tensorflow_hub as hub

# Reproducability
def set_seed(seed=1234):
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
set_seed()

# Set Matplotlib defaults
plt.rc('figure', autolayout=True)
plt.rc('axes', labelweight='bold', labelsize='large',
       titleweight='bold', titlesize=18, titlepad=10)
plt.rc('image', cmap='magma')
warnings.filterwarnings("ignore") # to clean up output cells

path = '/content/drive/MyDrive/Hackathon/data/'

# Load training and validation sets
ds_train_ = image_dataset_from_directory(
    path+'train',
    labels='inferred',
    label_mode='binary',
    image_size=[60, 80],
    interpolation='nearest',
    batch_size=16,
    shuffle=True,
)

ds_valid_ = image_dataset_from_directory(
    path+'valid',
    labels='inferred',
    label_mode='binary',
    image_size=[60, 80],
    interpolation='nearest',
    batch_size=16,
    shuffle=True,
)



# Data Pipeline
def convert_to_float(image, label):
    image = tf.image.convert_image_dtype(image, dtype=tf.float32)
    return image, label

AUTOTUNE = tf.data.experimental.AUTOTUNE

ds_train = (
    ds_train_
    .map(convert_to_float)
    .cache()
    .prefetch(buffer_size=AUTOTUNE)
)
ds_valid = (
    ds_valid_
    .map(convert_to_float)
    .cache()
    .prefetch(buffer_size=AUTOTUNE)
)

# Pretrained Model (InceptionV1)使う
base_model = hub.KerasLayer('https://tfhub.dev/google/imagenet/inception_v1/classification/5', input_shape = (60, 80, 3))
base_model.trainable=False

model = keras.Sequential([
    # Import Pre-trained Model
    base_model,
    # Head
    layers.BatchNormalization(renorm=True),
    layers.Flatten(),
    layers.Dense(8, activation='relu'),
    layers.Dense(1, activation='sigmoid'),
])

#Train
optimizer = tf.keras.optimizers.Adam(epsilon=0.01)
model.compile(
    optimizer=optimizer,
    loss='binary_crossentropy',
    metrics=['binary_accuracy'],
)

history = model.fit(
    ds_train,
    validation_data=ds_valid,
    epochs=10,
)

# Plot learning curves
history_frame = pd.DataFrame(history.history)
history_frame.loc[:, ['loss', 'val_loss']].plot()
history_frame.loc[:, ['binary_accuracy', 'val_binary_accuracy']].plot();

model.save('hitokuma.h5') # Generate Model Information to use this model on RaspberryPi

# Code for checking
file_path = '/content/drive/MyDrive/Hackathon/data/valid_1/hito/'
file_list = os.listdir(file_path)
image_paths = [file_path+file for file in file_list]
predictions = []
flag = 0

for path in image_paths:
  img = cv2.imread(path)
  img = tf.convert_to_tensor(img)
  img = tf.expand_dims(img, axis=0)
  img = tf.divide(img, 255)
  prediction = model.predict(img)
  if prediction[0] < 0.5:
    flag = 1
  predictions.append(flag)

print(predictions)

# 熊が0, 人が1