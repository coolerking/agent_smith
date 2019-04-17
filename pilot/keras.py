# -*- coding: utf-8 -*-
"""
本クラスは、以下のリポジトリより引用、加筆した。

- [autorope/donkeycar](https://github.com/autorope/donkeycar/)
 - `donkeycar/parts/keras.py`

> 上記サイトはMITライセンス準拠のコードである。

"""
""""
keras.py
functions to run and train autopilots using keras
"""

from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.models import Model, load_model
from tensorflow.python.keras.layers import Convolution2D
from tensorflow.python.keras.layers import Dropout, Flatten, Dense
from tensorflow.python.keras.callbacks import ModelCheckpoint, EarlyStopping
import numpy as np

# モータステータスの取りうる値のリスト
MOTOR_STATUS = ['move', 'free', 'brake']

class KerasPilot:

    def load(self, model_path):
        self.model = load_model(model_path)

    def shutdown(self):
        pass

    def train(self, train_gen, val_gen,
              saved_model_path, epochs=100, steps=100, train_split=0.8,
              verbose=1, min_delta=.0005, patience=5, use_early_stop=True):
        """
        train_gen: generator that yields an array of images an array of
        """

        # checkpoint to save model after each epoch
        save_best = ModelCheckpoint(saved_model_path,
                                    monitor='val_loss',
                                    verbose=verbose,
                                    save_best_only=True,
                                    mode='min')

        # stop training if the validation error stops improving.
        early_stop = EarlyStopping(monitor='val_loss',
                                   min_delta=min_delta,
                                   patience=patience,
                                   verbose=verbose,
                                   mode='auto')

        callbacks_list = [save_best]

        if use_early_stop:
            callbacks_list.append(early_stop)

        hist = self.model.fit_generator(
            train_gen,
            steps_per_epoch=steps,
            epochs=epochs,
            verbose=1,
            validation_data=val_gen,
            callbacks=callbacks_list,
            validation_steps=steps * (1.0 - train_split) / train_split)
        return hist


class KerasLinear(KerasPilot):
    def __init__(self, model=None, num_outputs=None, *args, **kwargs):
        super(KerasLinear, self).__init__(*args, **kwargs)
        if model:
            self.model = model
        elif num_outputs is not None:
            self.model = default_linear()
        else:
            self.model = default_linear()

    def run(self, img_arr):
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        outputs = self.model.predict(img_arr)
        # 左モータ値：回帰
        left_value = outputs[0][0][0]
        # 左モータステータス：分類
        left_status = MOTOR_STATUS[np.argmax(outputs[1][0][0])]
        # 右モータ値：回帰
        right_value = outputs[2][0][0]
        # 右モータステータス：分類
        right_status = MOTOR_STATUS[np.argmax(outputs[3][0][0])]
        # リフトモータ値：回帰
        lift_value = outputs[4][0][0]
        # リフトモータステータス：分類
        lift_status =  MOTOR_STATUS[np.argmax(outputs[5][0][0])]

        # Agent Jones用操作データを返却
        return left_value, left_status, right_value, right_status, lift_value, lift_status


def default_linear():
    img_in = Input(shape=(120, 160, 3), name='img_in')
    x = img_in

    # Convolution2D class name is an alias for Conv2D
    x = Convolution2D(filters=24, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=32, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)

    x = Flatten(name='flattened')(x)
    x = Dense(units=100, activation='linear')(x)
    x = Dropout(rate=.1)(x)
    x = Dense(units=50, activation='linear')(x)
    x = Dropout(rate=.1)(x)
    # 最終全結合層と活性化関数のみ差し替え
    # categorical output of the angle
    #angle_out = Dense(units=1, activation='linear', name='angle_out')(x)

    # continous output of throttle
    #throttle_out = Dense(units=1, activation='linear', name='throttle_out')(x)
    
    # 左モータ
    left_value_out  = Dense(units=1, activation='linear', name='left_value_out')(x)
    left_status_out = Dense(units=len(MOTOR_STATUS), activation='softmax', name='left_status_out')(x)

    # 右モータ
    right_value_out  = Dense(units=1, activation='linear', name='right_value_out')(x)
    right_status_out = Dense(units=len(MOTOR_STATUS), activation='softmax', name='right_status_out')(x)

    # リフトモータ
    lift_value_out  = Dense(units=1, activation='linear', name='lift_value_out')(x)
    lift_status_out = Dense(units=len(MOTOR_STATUS), activation='softmax', name='lift_status_out')(x)

    model = Model(inputs=[img_in], outputs=[left_value_out, left_status_out, right_value_out, right_status_out, lift_value_out, lift_status_out])

    # 回帰、分類別に最適化関数を使い分け
    model.compile(optimizer='adam',
                  loss={'left_value_out': 'mean_squared_error',
                        'left_status_out':  'categorical_crossentropy',
                        'right_value_out': 'mean_squared_error',
                        'right_status_out':  'categorical_crossentropy',
                        'lift_value_out': 'mean_squared_error',
                        'lift_status_out':  'categorical_crossentropy',},
                  loss_weights={'left_value_out': 0.5,
                        'left_status_out': 0.5,
                        'right_value_out': 0.5,
                        'right_status_out': 0.5,
                        'lift_value_out': 0.5,
                        'lift_status_out': 0.5})

    return model