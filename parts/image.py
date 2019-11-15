# -*- coding: utf-8 -*-
"""
2D画像イメージを生成するパーツクラスを提供する。
要pillowパッケージ。
`pip install pillow`
"""
from .VisionGenerator.SpoolMobile import SpoolMobileVision
from .VisionGenerator.madgwickahrs import MadgwickAHRS
import donkeycar as dk
from PIL import Image
import numpy as np
import math
import json

class MapImageCreator:
    """
    位置情報システムの出力データをもとにマップ画像を生成する
    パーツクラス。
    """
    def __init__(self, base_image_path, debug=False):
        """
        ベースイメージパス、エージェントイメージパスを
        インスタンス変数へ格納する。
        引数：
            base_image_path             ベースイメージパス
            debug                       デバッグフラグ
        """
        self.base_image_path = base_image_path
        self.angle = 90  # x-axis +direction

        self.dead_zone = 0.05  # looks like we may consider the mobile beacon stationary in this range
        self.imu_processing_rate = 143  # looks like 143~144 msec is taken for processing, don't know how to change
        self.x_end_ref = np.zeros((2,1))  # Stationary beacon's position set as the end of x-axis by the dashboard randomly
        self.origin_ref = np.zeros((2,1))  # Stationary beacon's position set as the origin by the dashboard random
        self.x_end_ref[0,0], self.x_end_ref[1,0] = 76 * 0.008, 0  # coordinate of No.39 stationary beacon, as the x-axis end
        self.origin_ref[0,0], self.origin_ref[1,0] = 0, 60 * 0.008  # coordinate of No.73 stationary beacon, as the origin
        self.file_name_trailer_count = 0
        self.skip_very_first_data = 0
        self.scale = 1   # always 1 for vision generation
        self.stud = 8 / 1000     # 8mm/stud

        self.debug = debug

        self.dt_vision = SpoolMobileVision(59, 20, 20, self.angle, 
        4, 0, self.scale, landscape=Image.open(self.base_image_path))

        self.heading = MadgwickAHRS(sampleperiod=1/20, beta=2)

    '''Marvelmind IMU利用
    def run(self, x, y, qw, qx, qy, qz, timestamp, qw_f, qx_f, qy_f, qz_f, timestamp_f):
        """
        位置情報システムのX,Y,Z座標と四元数から
        マップ画像を生成し返却する。
        引数：
            x           位置情報システムX座標
            y           位置情報システムY座標
            qw          最新の位置情報システム四元数w
            qx          最新の位置情報システム四元数x
            qy          最新の位置情報システム四元数y
            qz          最新の位置情報システム四元数z
            timestamp   最新の位置情報システムからの取得時刻
            qw_f        １件前の位置情報システム四元数w
            qx_f        １件前の位置情報システム四元数x
            qy_f        １件前の位置情報システム四元数y
            qz_f        １件前の位置情報システム四元数z
            timestamp_f １件前の位置情報システムからの取得時刻
        戻り値：
            image_array マップ画像
        """
        if x is None or y is None or qw is None or qx is None or \
            qy is None or qz is None or timestamp is None or \
            qw_f is None or qx_f is None or qy_f is None or \
            qz_f is None or timestamp_f is None:
            if self.debug:
                print('[MapImageCreator] return base image because None exists')
            return self.base_to_array()

        # Miniature-Warehouse reference frame only concerns x, y position and yaw angle(around z-axis)
        # transform the Stationary-Beacon reference frame to the Miniature-Warehouse reference frame
        # Both stationary-beacon frame and the miniature-warehouse frame are rigth-hand-z-down reference.
        rotation_angle = math.degrees(math.atan2(self.origin_ref[1, 0], self.x_end_ref[0, 0]))
        position = np.zeros((2, 1))
        position[0, 0] = x
        position[1, 0] = y

        # Rotete the processed position data (x, y) -1 * rotation_angle
        rot_matrix = [[math.cos(math.radians(rotation_angle)), math.sin(math.radians(rotation_angle))],
                  [-1 * math.sin(math.radians(rotation_angle)), math.cos(math.radians(rotation_angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_position = rot_matrix @ position

        # shift the rotatde position by origin_ref
        # print('rotated %f to p( %f, %f )' % (rotation_angle, rotated_position[0, 0], rotated_position[1,0]))
        rotated_position = rotated_position + self.origin_ref

        # transform the quaternian to the Euler angles (we need yaw angle only)
        # We use delta value to add the angle of mobile
        # while the absolute delta value is below 0.05 degree within the timeslice, we'll consider it as 0, that is stationary.
        q0, q1, q2, q3 = qw, qx, qy, qz
        yaw = math.atan2(2.0 * (q1 * q2 + q0 * q3), q0 * q0 + q1 * q1 - q2 * q2 - q3 * q3)
        q10, q11, q12, q13, timestamp1 = qw_f, qx_f, qy_f, qz_f, timestamp_f
        yaw1 = math.atan2(2.0 * (q11 * q12 + q10 * q13), q10 * q10 + q11 * q11 - q12 * q12 - q13 * q13)
        delta_yaw = math.degrees(yaw) - math.degrees(yaw1)
        elapsed_time = timestamp - timestamp1

        if self.skip_very_first_data == 0:
            self.skip_very_first_data = 1
        else:
            if elapsed_time != 0:
                number_of_timeslice = elapsed_time / self.imu_processing_rate
                if abs(delta_yaw / number_of_timeslice) > self.dead_zone:
                    self.angle = self.angle + delta_yaw
            else:
                if abs(delta_yaw) > self.dead_zone:
                    self.angle = self.angle + delta_yaw

        if self.debug:
            print('[MapImageCreator] x:%f y:%f delta-yaw:%f angle:%f in %f msec sampled at %f msec' % (rotated_position[0, 0], rotated_position[1, 0], delta_yaw, self.angle % 360, elapsed_time, timestamp))
        im = self.dt_vision.get_vision(rotated_position[0, 0] / self.stud, rotated_position[1, 0] / self.stud, self.angle)
        return dk.utils.img_to_arr(im)
    '''

    '''MPU9250からIMUデータ取得'''

    def run(self, x, y, recent):
        """
        位置情報システムのX,Y,Z座標とMPU9250の最新IMUデータ2件から
        マップ画像を生成し返却する。
        引数：
            x           Marvelmind位置情報システムX座標(float)
            y           Marvelmind位置情報システムY座標(float)
            recent      MPU9260最新データ群(JSON形式文字列)
        戻り値：
            image_array マップ画像
        """
        # 引数チェック
        #print('[MapImageCreator] x:{}, y:{}, recent:{}'.format(str(x), str(y), str(recent)))
        if x is None or y is None or recent is None:
            if self.debug:
                print('[MapImageCreator] return base image because None exists')
            return self.base_to_array()

        # 座標
        # Miniature-Warehouse reference frame only concerns x, y position and yaw angle(around z-axis)
        # transform the Stationary-Beacon reference frame to the Miniature-Warehouse reference frame
        # Both stationary-beacon frame and the miniature-warehouse frame are rigth-hand-z-down reference.
        rotation_angle = math.degrees(math.atan2(self.origin_ref[1, 0], self.x_end_ref[0, 0]))
        position = np.zeros((2, 1))
        position[0, 0] = x
        position[1, 0] = y

        # Rotete the processed position data (x, y) -1 * rotation_angle
        rot_matrix = [[math.cos(math.radians(rotation_angle)), math.sin(math.radians(rotation_angle))],
                  [-1 * math.sin(math.radians(rotation_angle)), math.cos(math.radians(rotation_angle))]]
        rot_matrix = np.array(rot_matrix)
        rotated_position = rot_matrix @ position

        # shift the rotatde position by origin_ref
        # print('rotated %f to p( %f, %f )' % (rotation_angle, rotated_position[0, 0], rotated_position[1,0]))
        rotated_position = rotated_position + self.origin_ref

        ## 最新IMUデータ2件を復元
        from .sensors.imu import array_recent_data, unpack
        recent_array = array_recent_data(recent)
        cur_timestamp, _, cur_accel_data, cur_gyro_data, cur_magnet_data = unpack(recent_array[-1])
        pre_timestamp, _, pre_accel_data, pre_gyro_data, pre_magnet_data = unpack(recent_array[-2])

        delta_yaw = 0

        #elapsed_time = hedge.valuesImuRawData[-1][9] - hedge.valuesImuRawData[-2][9]
        elapsed_time = cur_timestamp - pre_timestamp

        ## heading.sampleperiod = elapsed_time / 1000
        #gyr = np.array([math.radians(hedge.valuesImuRawData[-1][3]), math.radians(hedge.valuesImuRawData[-1][4]),
        #            math.radians(hedge.valuesImuRawData[-1][5])])
        gyr = np.array([
            math.radians(cur_gyro_data['x']),
            math.radians(cur_gyro_data['y']),
            math.radians(cur_gyro_data['z']),
        ])
        #acc = np.array([hedge.valuesImuRawData[-1][0], hedge.valuesImuRawData[-1][1], hedge.valuesImuRawData[-1][2]])
        acc = np.array([
            cur_accel_data['x'], cur_accel_data['y'], cur_accel_data['z'],
        ])
        #mgt = np.array([hedge.valuesImuRawData[-1][6], hedge.valuesImuRawData[-1][7], hedge.valuesImuRawData[-1][8]])
        mgt = np.array([
            cur_magnet_data['x'], cur_magnet_data['y'], cur_magnet_data['z'],
        ])
        self.heading.update(gyr, acc, mgt)
        _, _, yaw = self.heading.quaternion.to_euler123()  # roll, pitch, 最初の角度

        if self.skip_very_first_data != 0:  # 2回目以降は常に実行
            #gyr1 = np.array([math.radians(hedge.valuesImuRawData[-2][3]), math.radians(hedge.valuesImuRawData[-2][4]),
            #             math.radians(hedge.valuesImuRawData[-2][5])])
            gyr1 = np.array([
                math.radians(pre_gyro_data['x']),
                math.radians(pre_gyro_data['y']),
                math.radians(pre_gyro_data['z']),
            ])
            #acc1 = np.array([hedge.valuesImuRawData[-2][0], hedge.valuesImuRawData[-2][1], hedge.valuesImuRawData[-2][2]])
            acc1 = np.array([
                pre_accel_data['x'], pre_accel_data['y'], pre_accel_data['z'],
            ])
            #mgt1 = np.array([hedge.valuesImuRawData[-2][6], hedge.valuesImuRawData[-2][7], hedge.valuesImuRawData[-2][8]])
            mgt1 = np.array([
                pre_magnet_data['x'], pre_magnet_data['y'], pre_magnet_data['z'],
            ])
            self.heading.update(gyr1, acc1, mgt1)
            _, _, yaw1 = self.heading.quaternion.to_euler123()  # roll1, pitch1, 最初の角度

        if self.skip_very_first_data == 0:
            self.angle = math.degrees(yaw)  # 方向を最初の角度に設定
            self.skip_very_first_data = 1
        else:
            delta_yaw = math.degrees(yaw) - math.degrees(yaw1)  # 2回目以降は差分を検査して加算する
            if elapsed_time != 0:
                number_of_timeslice = elapsed_time / self.imu_processing_rate
                if abs(delta_yaw / number_of_timeslice) > self.dead_zone:
                    self.angle = self.angle + delta_yaw
            else:
                if abs(delta_yaw) > self.dead_zone:
                    self.angle = self.angle + delta_yaw
        if self.debug:
            print('[MapImageCreator] turn %f degeres heading %f degrees elapsed time:%f' % (delta_yaw, self.angle % 360, elapsed_time))
        #self.dt_vision.update_vision(76, 60, self.angle)
        im = self.dt_vision.get_vision(rotated_position[0, 0] / self.stud, rotated_position[1, 0] / self.stud, self.angle)
        return dk.utils.img_to_arr(im)

    def base_to_array(self):
            with open(self.base_image_path, 'rb') as f:
                data = f.read()
            return dk.utils.img_to_arr(dk.utils.binary_to_img(data))

    def shutdown(self):
        """
        インスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.base_image_path = None
        self.dt_vision = None
        if self.debug:
            print('[MapImageCreator] shutdown called')