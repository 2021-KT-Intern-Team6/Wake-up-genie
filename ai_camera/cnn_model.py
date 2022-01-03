# cnn 모델의 계층 구조를 정의
# 정의한 모델과 dataset을 사용해 눈의 상태(open, close)를 감지하는 모델을 학습해 모델을 저장

import datetime
import numpy as np
import matplotlib.pyplot as plt
from helpers import *
from tensorflow import keras
#from keras.layers import Input, Activation, Conv2D, Flatten, Dense, MaxPooling2D
#from keras.models import Model, load_model
#from keras.preprocessing.image import ImageDataGenerator
#from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
plt.style.use('dark_background')

#====================================Data scailing=============================================#

# train data와 validation data 로드
x_train = np.load('data/x_train.npy').astype(np.float32)
y_train = np.load('data/y_train.npy').astype(np.float32)
x_val = np.load('data/x_val.npy').astype(np.float32)
y_val = np.load('data/y_val.npy').astype(np.float32)

# label : 눈을 감고 있는 이미지 = 1 / 눈을 뜨고 있는 이미지 = 0
# print(x_train.shape, y_train.shape) #2647장 * 26 * 34 * 1 / 2647 * 1
# print(x_val.shape, y_val.shape) #295장 * 26 * 34  * 1 / 295 * 1

# 데이터 증식을 위해 사용할 ImageDataGenerator 객체 생성
# training data
train_datagen = keras.preprocessing.image.ImageDataGenerator(                   # 정확도를 높이기 위해 랜덤하게 이미지를 리스케일링
    rescale=1./255,             # 크기 재조절 (픽셀값을 0~1사이 값으로 변경)
    rotation_range=10,          # 무작위 회전
    width_shift_range=0.2,      # 이미지 수평 방향 이동
    height_shift_range=0.2,     # 이미지 수직 방향 이동
    shear_range=0.2             # 밀림 강도
)

# validation data
# 따로 데이터 스케일과정이 필요없으므로 픽셀값만 0~1사이의 값으로 변경
val_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# 이미지 변형(batch size, shuffle 여부 정의)
# training data
train_generator = train_datagen.flow(
    x=x_train, y=y_train,
    batch_size=32,
    shuffle=True
)

#validation data
val_generator = val_datagen.flow(
    x=x_val, y=y_val,
    batch_size=32,
    shuffle=False
)

#====================================CNN 계층구조 정의=============================================#
# layer는 convolution layer 4개, pooling layer 4개 이후 fully connected layer로 구성
# 0~1사이의 값으로 구성된 26*34*1의 픽셀 값들을 입력으로 받아 이미지가 opened eye(1) 인지 closed eye(0)인지 분류
inputs = keras.layers.Input(shape=(26, 34, 1))

net = keras.layers.Conv2D(16, kernel_size=3, strides=1, padding='same', activation='relu')(inputs)
net = keras.layers.MaxPooling2D(pool_size=2)(net)

net = keras.layers.Conv2D(32, kernel_size=3, strides=1, padding='same', activation='relu')(net)
net = keras.layers.MaxPooling2D(pool_size=2)(net)

net = keras.layers.Conv2D(64, kernel_size=3, strides=1, padding='same', activation='relu')(net)
net = keras.layers.MaxPooling2D(pool_size=2)(net)

net = keras.layers.Conv2D(128, kernel_size=3, strides=1, padding='same', activation='relu')(net)
net = keras.layers.MaxPooling2D(pool_size=2)(net)

net = keras.layers.Flatten()(net)                           # convolution layer와 pooling layer를 통과하며 특징을 1차원으로 변환

net = keras.layers.Dense(1024)(net)                         # fully connected layer
net = keras.layers.Activation('relu')(net)
net = keras.layers.Dense(1)(net)                            # 출력을 하나로 모아줌
outputs = keras.layers.Activation('sigmoid')(net)           # activation function으로 sigmoid를 사용해 0~1사이의 값으로 분류

model = keras.models.Model(inputs=inputs, outputs=outputs)  # 모델의 input layer과 ouput layer을 결정

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])    # 모델 학습 방식 설정 (optimizer, loss function, metric(평가지표)) (모델을 빌드하고 학습하기 전에 컴파일하는 것)

model.summary()                                             # 모델의 정보 출력

#====================================CNN 모델 학습=============================================#
start_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')     # 모델을 학습한 시간

model.fit_generator(                                        # 주어진 epoch=50 만큼 모델 학습 (fit() 과의 차이점 : fit은 학습에 사용할 데이터 전체를 한번에 입력으로 사용, fit_generator는 python의 generator 사용해 형성된 대용량의 데이터를 batch-by-batch로 효율적으로 학습 => ImageDataGenerator를 사용한 경우 fit_generator사용)
    train_generator, epochs=50, steps_per_epoch=2649/32, validation_steps=295/32, validation_data=val_generator,
    # stpes_per_epoch : 한 번 epoch 돌 때 데이터를 몇 번 볼 것인가
    # validation_steps : 한 번 epoch 돌고 난 후 validation accuracy를 측정할 때 validation data를 몇번 볼 것인가
    callbacks=[
        keras.callbacks.ModelCheckpoint('models/%s.h5' % (start_time), monitor='val_acc', save_best_only=True, mode='max', verbose=1),  # 파일명을 모델을 학습하는 시간으로 하고 가장 accuracy가 좋은 모델만 저장
        keras.callbacks.ReduceLROnPlateau(monitor='val_acc', factor=0.2, patience=10, verbose=1, mode='auto', min_lr=1e-05)             # 모델의 개선이 없을 경우 learning rate를 조절해 모델의 개선을 유도
    ]
)
#=============================================================================================#

