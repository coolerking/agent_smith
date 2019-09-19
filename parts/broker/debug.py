# -*- coding: utf-8 -*-
"""
Vehicle上のデータを標準出力に表示するデバッグパーツ群。
"""
import os
import glob
import random
import numpy as np
#import donkeycar as dk
from datetime import datetime

class PrintPowerSettings:

    def __init__(self, title=''):
        self.title = title

    def run(self, angle, throttle, lift_throttle, mode):
        print('[{}] Angle:{}, Throttle:{} lift:{} ::{}'.format(
            self.title,
            str(angle), str(throttle), str(lift_throttle),
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
    def run(self, id_usnav, x_usnav, y_usnav, z_usnav, angle_usnav, timestamp_usnav):
        print('[USNav:{}] x={}, y={}, z={}'.format(str(id_usnav), str(x_usnav), str(y_usnav), str(z_usnav)))
    
    def shutdown(self):
        pass

class GetImage:
    def __init__(self, img_dir='assets/tests'):
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
        import donkeycar as dk
        return dk.utils.img_to_arr(dk.utils.binary_to_img(data))

class GetTub:

    def run(self):
        return get_user_mode(), \
            get_value(), get_value(), get_value(), \
            get_value(), get_value(), get_value(), get_timestamp()

    def shutdown(self):
        pass


def get_value():
    return random.uniform(1.0, -1.0)

def get_volts():
    return random.uniform(3.05, 0.0)

def get_cms():
    return random.uniform(100.0, 0.0)

def get_user_mode():
    all_user_mode = ['user', 'local']
    return all_user_mode[random.randrange(len(all_user_mode))]

def get_timestamp():
    return str(datetime.now())