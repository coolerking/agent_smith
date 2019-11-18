# -*- coding: utf-8 -*-
"""
Vehicle上のデータを標準出力に表示するデバッグパーツ群。
"""
import os
import glob
import time
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

class PrintDist:
    def run(self, dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d, dist_b3, dist_b3d, dist_b4, dist_b4d, dist_timestamp):
        print('[DIST] id={}, timespamp={}'.format(str(dist_id), str(dist_timestamp)))
        print('       b1={},b1d={}, b2={},b2d={}, b3={},b3d={}, b4={},b4d={}'.format(
            str(dist_b1), str(dist_b1d), str(dist_b2), str(dist_b2d),
            str(dist_b3), str(dist_b3d), str(dist_b4), str(dist_b4d),
        ))

class PrintIMU:
    def run(self, x, y, z, qw, qx, qy, qz, vx, vy, vz, ax, ay, az, gx, gy, gz, mx, my, mz, timestamp):
        print('[IMU] timespamp={}'.format(str(timestamp)))
        print('        x={},   y={},  z={}'.format(str(x), str(y), str(z)))
        print('       qx={},  qy={}, qz={}, qw={}'.format(str(qx), str(qy), str(qz), str(qw)))
        print('       vx={},  vy={}, vz={}'.format(str(vx), str(vy), str(vz)))
        print('       ax={},  ay={}, az={}'.format(str(ax), str(ay), str(az)))
        print('       gx={},  gy={}, gz={}'.format(str(gx), str(gy), str(gz)))
        print('       mx={},  my={}, mz={}'.format(str(mx), str(my), str(mz)))

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

'''
        inputs += [
            # USNav
            'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
            # IMU
            'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
            'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
            'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
            # USNav Raw
            'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
            'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
        ]
'''


class GetHedge:

    def run(self):
        return get_id(), get_imu(), get_imu(), get_imu(), get_imu(), get_ts(), \
        get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), \
        get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), \
        get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), get_imu(), get_ts(), \
        get_id(), get_id(), get_cms(), get_id(), get_cms(), \
        get_id(), get_cms(), get_id(), get_cms(), get_ts()

class GetMpu:

    def run(self):
        return get_imu(), get_imu(), get_imu(), \
            get_imu(), get_imu(), get_imu(), \
            get_imu(), get_imu(), get_imu(), \
            get_cms(), time.time()

def get_id():
    all_id = ['11', '22', '33', '44', '55']
    return all_id[random.randrange(len(all_id))]

def get_value():
    return random.uniform(1.0, -1.0)

def get_imu():
    return random.uniform(300.0, -300.0)

def get_volts():
    return random.uniform(3.05, 0.0)

def get_cms():
    return random.uniform(100.0, 0.0)

def get_user_mode():
    all_user_mode = ['user', 'local']
    return all_user_mode[random.randrange(len(all_user_mode))]

def get_timestamp():
    return str(datetime.now())

cnt = 1
def get_ts():
    cnt = cnt + 1
    return cnt
    #return int(time.time()*100)