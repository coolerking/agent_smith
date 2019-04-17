# -*- coding: utf-8 -*-
"""
Vehicle上のデータを標準出力に表示するデバッグパーツ群。
"""
import os
import glob
import random
import numpy as np
import donkeycar as dk
from datetime import datetime

class PrintPowerSettings:

    def __init__(self, title=''):
        self.title = title

    def run(self, left_value, left_status, right_value, right_status, lift_value, lift_status, mode):
        print('[{}] L:{}({}), R:{}({}) lift:{}({}) ::{}'.format(
            self.title,
            str(left_value), left_status,
            str(right_value), right_status,
            str(lift_value), lift_status,
            mode
        ))
    
    def shutdown(self):
        pass

class PrintSensors:

    def run(self, range_cms, force_volts, bend_volts):
        print('Range: {}cms, Force: {}V, Bend: {}V'.format(
            str(range_cms), str(force_volts), str(bend_volts)
        ))
    
    def shutdown(self):
        pass

class PrintRecording:

    def run(self, recording):
        print('recording: {}'.format('on' if recording else 'off'))
    
    def shutdown(self):
        pass


class PrintIMU:
    def run(self, x, y, z, qw, qx, qy, qz, vx, vy, vz, ax, ay, az):
        print('[IMU]  x={},   y={},  z={}'.format(str(x), str(y), str(z)))
        print('[IMU] qx={},  qy={}, qz={}, qw={}'.format(str(qx), str(qy), str(qz), str(qw)))
        print('[IMU] vx={},  vy={}, vz={}'.format(str(vx), str(vy), str(vz)))
        print('[IMU] ax={},  ay={}, az={}'.format(str(vx), str(vy), str(vz)))

    def shutdown(self):
        pass

class PrintUSNav:
    def run(self, x_usnav, y_usnav, z_usnav):
        print('[USNav] x={}, y={}, z={}'.format(str(x_usnav), str(y_usnav), str(z_usnav)))
    
    def shutdown(self):
        pass

class GetImage:
    def __init__(self, img_dir='debug/images'):
        self.image_dir = os.path.expanduser(img_dir)
        self.files = glob.glob(os.path.join(self.image_dir, '*.jpg'))

    def run(self):
        return self.get_image_array()
    
    def shutdown(self):
        pass

    def _get_image_filepath(self):
        #return os.path.join(self.image_dir, self.files[random.randrange(len(self.files))])
        return self.files[random.randrange(len(self.files))]
    
    def get_image_binary(self):
        with open(self._get_image_filepath(), 'rb') as f:
            data = f.read()
        return data

    def get_image_array(self):
        data = self.get_image_binary()
        return dk.util.img.img_to_arr(dk.util.img.binary_to_img(data))

class GetTub:

    def __init__(self):
        self.all_status = ['free', 'move', 'brake']
        self.all_user_mode = ['user', 'local']
    
    def _get_value(self):
        return random.uniform(1.0, -1.0)

    def _get_volts(self):
        return random.uniform(3.05, 0.0)

    def _get_cms(self):
        return random.uniform(100.0, 0.0)

    def _get_status(self):
        return self.all_status[random.randrange(len(self.all_status))]

    def _get_user_mode(self):
        return self.all_user_mode[random.randrange(len(self.all_user_mode))]

    def run(self):
        return self._get_user_mode(), \
            self._get_value(), self._get_status(), self._get_value(), self._get_status(), self._get_value(), self._get_status(), \
            self._get_value(), self._get_status(), self._get_value(), self._get_status(), self._get_value(), self._get_status(), \
            self._get_cms(), self._get_volts(), self._get_volts(), True, str(datetime.now())

    def to_binary(self, data):
        """
        イメージデータimage_arrayがnd.array型の場合、バイナリに変換する。
        引数：
            data            イメージデータ
        戻り値：
            image           バイナリ変換後のイメージデータ
        """
        if type(data) is np.ndarray:
            import donkeycar as dk
            return dk.util.img.arr_to_binary(data)
        elif type(data) is bytes:
            return data
        else:
            raise ValueError('unknown image_array type=' +str(type(data)))

