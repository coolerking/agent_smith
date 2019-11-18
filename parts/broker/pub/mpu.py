# -*- coding: utf-8 -*-
"""
MPU9250から取得したIMUデータをPublishするパーツクラス群。
"""
import time
import json
from .base import PublisherBase, to_str, to_float
from .topic import pub_mpu6050_json_topic, pub_mpu9250_json_topic

class Mpu6050Publisher(PublisherBase):
    """
    MPU5050 IMUデータ(辞書型)をAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'Mpu6050', debug)
        self.topic = pub_mpu6050_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[Mpu6050Publisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az):
        """
        MPU6050 IMUデータ(辞書型)をPublishする。
        引数：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az), 
            self.qos)
        if self.debug:
            print('[Mpu6050Publisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self,  imu_vx=None, imu_vy=None, imu_vz=None,
    imu_ax=None, imu_ay=None, imu_az=None):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
        戻り値：
            メッセージ文字列
        """
        message = {
            'imu/vx':           to_float(imu_vx),
            'imu/vy':           to_float(imu_vy),
            'imu/vz':           to_float(imu_vz),
            'imu/ax':           to_float(imu_ax),
            'imu/ay':           to_float(imu_ay),
            'imu/az':           to_float(imu_az),
            'imu/timestamp':    to_float(time.time()),
        }
        return json.dumps(message)

class Mpu9250Publisher(PublisherBase):
    """
    MPU9250 IMUデータ(辞書型)をAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'Mpu9250', debug)
        self.topic = pub_mpu9250_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[Mpu9250Publisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az, imu_mx, imu_my, imu_mz):
        """
        MPU9250 IMUデータ(辞書型)をPublishする。
        引数：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_mx          磁束密度(X軸)
            imu_my          磁束密度(Y軸)
            imu_mz          磁束密度(Z軸)
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az, imu_mx, imu_my, imu_mz), 
            self.qos)
        if self.debug:
            print('[Mpu9250Publisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self,  imu_vx=None, imu_vy=None, imu_vz=None,
    imu_ax=None, imu_ay=None, imu_az=None, imu_mx=None, imu_my=None, imu_mz=None):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_mx          磁束密度(X軸)
            imu_my          磁束密度(Y軸)
            imu_mz          磁束密度(Z軸)
        戻り値：
            メッセージ文字列
        """
        message = {
            'imu/vx':           to_float(imu_vx),
            'imu/vy':           to_float(imu_vy),
            'imu/vz':           to_float(imu_vz),
            'imu/ax':           to_float(imu_ax),
            'imu/ay':           to_float(imu_ay),
            'imu/az':           to_float(imu_az),
            'imu/mx':           to_float(imu_mx),
            'imu/my':           to_float(imu_my),
            'imu/mz':           to_float(imu_mz),
            'imu/timestamp':    to_float(time.time()),
        }
        return json.dumps(message)