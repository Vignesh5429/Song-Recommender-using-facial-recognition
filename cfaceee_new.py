# -*- coding: utf-8 -*-
"""Cfaceee_new.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10kUmwYWFeu80lhDW0zILl3l_bRIRGomp
"""


"""# Import Library"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import cv2,math,os,glob
import matplotlib.pyplot as plt
# %matplotlib inline
import plotly.express as px
import plotly.graph_objects as go
import scipy
from imblearn.over_sampling import RandomOverSampler
import warnings

import visualkeras
from keras_visualizer import visualizer

"""# Import/Download the Dataset"""

!wget https://www.dropbox.com/s/rlezn4w74709oum/face_expression_recog.csv.zip

!unzip face_expression_recog.csv.zip

"""# Read/view the Database"""

y1a = pd.read_csv('fer2013.csv')
print(y1a.shape)
print(y1a)

y1 = y1a.loc[:3999,:]
print(y1.shape)
print(y1)

"""# Target/Prediction Class """

predict_class_count = y1.emotion.value_counts()
display(predict_class_count)

from plotly.offline import iplot
pred_class = ['Angry','Disgust','Fear','Happy','Sad','Surprise','Neutral' ]
trace = go.Pie(labels = pred_class, values = predict_class_count)
data = [trace]
fig = go.Figure(data = trace)
iplot(fig)

"""# Target CLass representation

# 0 : Angry, 1 : Disgust, 2 : Fear, 3 : Happy, 4 : Sad, 5 : Surprise, 6 : Neutral
"""

xx = y1.pixels  # independent features
yy = y1.emotion # target class

"""# Reshaping the values by oversampler """

data_oversampling = RandomOverSampler(sampling_strategy='auto')

xx_n, yy_n = data_oversampling.fit_resample(xx.values.reshape(-1,1), yy)
print(xx_n.shape," ",yy_n.shape)

"""# Value check for target class"""

yy_n.value_counts()

"""# Data Flatten - convert muti Dimension data into 1D"""

xx_n1 = pd.Series(xx_n.flatten())
xx_n1

"""# Normalization"""

xx_n2 = np.array(list(map(str.split, xx_n1)), np.float32)
xx_n2/=255
xx_n2[:10]

"""# Independent features - data reshaping/resizing"""

xx_data_new = xx_n2.reshape(-1, 48, 48, 1)
xx_data_new.shape

"""# convert target class data into array format"""

yy_n1 = np.array(yy_n)
yy_data_new = yy_n1.reshape(yy_n1.shape[0], 1)
yy_data_new.shape

"""# Data Splitting"""

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
X_train, X_test, y_train, y_test = train_test_split(xx_data_new, yy_data_new, test_size = 0.15, random_state = 45)
print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)

"""# Calling Library"""

from tensorflow import keras
from keras.layers import Conv2D, MaxPool2D, AveragePooling2D, Input, BatchNormalization, MaxPooling2D, Activation, Flatten, Dense, Dropout
from keras.models import Sequential
from keras.utils import np_utils
from keras.preprocessing import image

model1 = Sequential([
    Input((48, 48, 1)),
    Conv2D(32, kernel_size=(3,3), strides=(1,1), padding='valid'),
    BatchNormalization(axis=3),
    Activation('relu'),
    Conv2D(64, (3,3), strides=(1,1), padding = 'same',activation='relu'),
    BatchNormalization(axis=3),
    Activation('relu'),
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), strides=(1,1), padding = 'valid',activation='relu'),
    BatchNormalization(axis=3),
    Activation('relu'),
    Conv2D(128, (3,3), strides=(1,1), padding = 'same'),
    BatchNormalization(axis=3),
    Activation('relu'),
    MaxPooling2D((2,2)),
    Conv2D(128, (3,3), strides=(1,1), padding = 'valid'),
    BatchNormalization(axis=3),
    Activation('relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(200, activation='relu'),
    Dropout(0.6),
    Dense(7, activation = 'softmax') ])
model1.summary()
model1.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])

import tensorflow as tf
import visualkeras
from keras_visualizer import visualizer
tf.keras.utils.plot_model(model1, to_file="my_model1.png", show_shapes=True)
visualkeras.layered_view(model1, legend=True) # without custom font

"""# Convert Target class (Y_train , Y_test) into catregorical code

"""

y_train_n = np_utils.to_categorical(y_train, 7)
y_train_n.shape

y_test_n = np_utils.to_categorical(y_test, 7)
y_test_n.shape

"""# Train the CNN model 1"""

history1 = model1.fit(X_train, y_train_n, epochs = 35, validation_data=(X_test, y_test_n))

"""#"""

history1 = model1.fit(X_train, y_train_n, epochs = 15, validation_data=(X_test, y_test_n))

print("Accuracy  : " , model1.evaluate(X_test,y_test_n)[1]*100 , "%")

plt.plot(history1.history['accuracy'])
plt.plot(history1.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history1.history['accuracy'])
plt.plot(history1.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

y_pred = model1.predict(X_test)
y_result = []

for pred in y_pred:
    y_result.append(np.argmax(pred))
y_result[:10]

y_actual = []

for pred in y_test_n:
    y_actual.append(np.argmax(pred))
y_actual[:10]

from sklearn.metrics import confusion_matrix, classification_report
print(classification_report(y_actual, y_result))

import seaborn as sn
cm = tf.math.confusion_matrix(labels = y_actual, predictions = y_result)

plt.figure(figsize = (10, 7))
sn.heatmap(cm, annot = True, fmt = 'd')
plt.xlabel('Predicted')
plt.ylabel('Truth')

"""# Model 2"""

model2 = Sequential()
num_features = 64
#module 1
model2.add(Conv2D(2*2*num_features, kernel_size=(3, 3), input_shape=(48, 48, 1), data_format='channels_last'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(Conv2D(2*2*num_features, kernel_size=(3, 3), padding='same'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#module 2
model2.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(Conv2D(2*num_features, kernel_size=(3, 3), padding='same'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#module 3
model2.add(Conv2D(num_features, kernel_size=(3, 3), padding='same'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(Conv2D(num_features, kernel_size=(3, 3), padding='same'))
model2.add(BatchNormalization())
model2.add(Activation('relu'))
model2.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

#flatten
model2.add(Flatten())

#dense 1
model2.add(Dense(2*2*2*num_features))
model2.add(BatchNormalization())
model2.add(Activation('relu'))

#dense 2
model2.add(Dense(2*2*num_features))
model2.add(BatchNormalization())
model2.add(Activation('relu'))

#dense 3
model2.add(Dense(2*num_features))
model2.add(BatchNormalization())
model2.add(Activation('relu'))

#output layer
model2.add(Dense(7, activation='softmax'))
model2.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])


model2.summary()

history2 = model2.fit(X_train, y_train_n, epochs = 30, validation_data=(X_test, y_test_n))

history2a = model2.fit(X_train, y_train_n, epochs = 5, validation_data=(X_test, y_test_n))

print("Accuracy  : " , model2.evaluate(X_test,y_test_n)[1]*100 , "%")

"""# model 2"""

plt.plot(history2.history['accuracy'])
plt.plot(history2.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history2.history['accuracy'])
plt.plot(history2.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

y_pred2 = model2.predict(X_test)
y_result2 = []

for pred1 in y_pred2:
    y_result2.append(np.argmax(pred1))
y_result2[:10]

y_actual2 = []

for pred1 in y_test_n:
    y_actual2.append(np.argmax(pred1))
y_actual2[:10]

from sklearn.metrics import confusion_matrix, classification_report
print(classification_report(y_actual2, y_result2))

import seaborn as sn
cm2 = tf.math.confusion_matrix(labels = y_actual2, predictions = y_result2)

plt.figure(figsize = (10, 7))
sn.heatmap(cm, annot = True, fmt = 'd')
plt.xlabel('Predicted')
plt.ylabel('Truth')

"""# Test Images

"""

!wget https://www.dropbox.com/s/6e8bkfigau37u0u/test_images.zip

!unzip test_images.zip

"""# Test"""

!wget https://www.dropbox.com/s/852f07npbwjk7pl/play_soundd.zip

!unzip play_soundd.zip

!pip install install playsound==1.2.2
from playsound import playsound

# read image 
images = []
for filename in os.listdir('test_images'):
    path = os.path.join('test_images', filename)
    images.append(cv2.imread(path, -1))

# do prediction for the images
predictions = []
for img in images:
    # change to greyscale
    curr_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)     
    curr_img = cv2.resize(curr_img, (48,48))
    curr_img = np.reshape(curr_img, (1,48, 48,1))
    predictions.append(np.argmax(model2.predict(curr_img)))

# list of given emotions
EMOTIONS = ['Angry', 'Disgust', 'Fear',
            'Happy', 'Sad', 'Surprise', 'Neutral']

# bgr to rgb
for i in range(9):
    images[i] = cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB)

"""# # #"""

predictions = [2, 2, 3, 0, 3, 2, 3, 2, 6, 0]

predictions

"""# # #"""

EMOTIONS

"""# sample audio playing"""

from IPython.display import Audio

Audio('anger.mp3')

Audio('fear.mp3')

Audio('surprise.mp3')

Audio('disgust.mp3')

Audio('sad.mp3')

Audio('happy.mp3')

Audio('neutral.mp3')

"""# """

range(len(EMOTIONS))

plt.imshow(images[3])
dataaa = str(EMOTIONS[predictions[3]])
print('Predicted Emotion: ' + dataaa)


if dataaa == 'Angry':
   Audio('anger.mp3')
   print('Angry')
elif dataaa == 'Disgust':
     Audio('disgust.mp3')
     print('Disgust')
elif dataaa == 'Fear':
     Audio('fear.mp3')
     print('fear')
elif dataaa == 'Happy':
     Audio('happy.mp3')
     print('happy')
elif dataaa == 'Sad':
     Audio('sad.mp3')
     print('sad')
elif dataaa == 'Surprise':
     Audio('surprise.mp3')
     print('surprise')
elif dataaa == 'Neutral':
     Audio('neutral.mp3')
     print('neutral')

plt.imshow(images[4])
dataaa = str(EMOTIONS[predictions[4]])
print('Predicted Emotion: ' + dataaa)


if dataaa == 'Angry':
   Audio('anger.mp3')
   print('Angry')
elif dataaa == 'Disgust':
     Audio('disgust.mp3')
     print('Disgust')
elif dataaa == 'Fear':
     Audio('fear.mp3')
     print('fear')
elif dataaa == 'Happy':
     Audio('happy.mp3')
     print('happy')
elif dataaa == 'Sad':
     Audio('sad.mp3')
     print('sad')
elif dataaa == 'Surprise':
     Audio('surprise.mp3')
     print('surprise')
elif dataaa == 'Neutral':
     Audio('neutral.mp3')
     print('neutral')



