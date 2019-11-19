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

    def run(self, imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_recent, imu_mpu_timestamp):
        """
        MPU6050 IMUデータ(辞書型)をPublishする。
        引数：
            imu_ax              加速度(X軸)
            imu_ay              加速度(Y軸)
            imu_az              加速度(Z軸)
            imu_gx              重力加速度(X軸)
            imu_gy              重力加速度(Y軸)
            imu_gz              重力加速度(Z軸)
            imu_recent          過去データ文字列
            imu_mpu_timestamp   取得時時刻
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_recent, imu_mpu_timestamp), 
            self.qos)
        if self.debug:
            print('[Mpu6050Publisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self,  imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_recent, imu_mpu_timestamp):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_gx          角速度(X軸)
            imu_gy          角速度(Y軸)
            imu_gz          角速度(Z軸)
            imu_recent          過去データ文字列
            imu_mpu_timestamp   取得時時刻
        戻り値：
            メッセージ文字列
        """
        message = {
            'imu/acl_x':            to_float(imu_ax),
            'imu/acl_y':            to_float(imu_ay),
            'imu/acl_z':            to_float(imu_az),
            'imu/gyr_x':            to_float(imu_gx),
            'imu/gyr_y':            to_float(imu_gy),
            'imu/gyr_z':            to_float(imu_gz),
            'imu/recent':           to_str(imu_recent),
            'imu/mpu_timestamp':    to_float(imu_mpu_timestamp),
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

    def run(self, imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, 
    imu_mx, imu_my, imu_mz, imu_temp, imu_recent, imu_mpu_timestamp):
        """
        MPU9250 IMUデータ(辞書型)をPublishする。
        引数：
            imu_ax              加速度(X軸)
            imu_ay              加速度(Y軸)
            imu_az              加速度(Z軸)
            imu_gx              角速度(X軸)
            imu_gy              角速度(Y軸)
            imu_gz              角速度(Z軸)
            imu_mx              磁束密度(X軸)
            imu_my              磁束密度(Y軸)
            imu_mz              磁束密度(Z軸)
            imu_temp            温度(C)
            imu_recent          過去データ
            imu_mpu_timestamp   取得時時刻
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz, imu_temp, imu_recent, imu_mpu_timestamp), 
            self.qos)
        if self.debug:
            print('[Mpu9250Publisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self,  imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz,
    imu_temp, imu_recent, imu_mpu_timestamp):
        """
        MPU9250 IMUデータ(辞書型)をメッセージ文字列に変換する。
        引数：
            imu_ax              加速度(X軸)
            imu_ay              加速度(Y軸)
            imu_az              加速度(Z軸)
            imu_gx              角速度(X軸)
            imu_gy              角速度(Y軸)
            imu_gz              角速度(Z軸)
            imu_mx              磁束密度(X軸)
            imu_my              磁束密度(Y軸)
            imu_mz              磁束密度(Z軸)
            imu_temp            温度(C)
            imu_recent          過去データ
            imu_mpu_timestamp   取得時時刻
        戻り値：
            メッセージ文字列
        """
        message = {
            'imu/acl_x':            to_float(imu_ax),
            'imu/acl_y':            to_float(imu_ay),
            'imu/acl_z':            to_float(imu_az),
            'imu/gyr_x':            to_float(imu_gx),
            'imu/gyr_y':            to_float(imu_gy),
            'imu/gyr_z':            to_float(imu_gz),
            'imu/mgt_x':            to_float(imu_mx),
            'imu/mgt_y':            to_float(imu_my),
            'imu/mgt_z':            to_float(imu_mz),
            'imu/temp':             to_float(imu_temp),
            'imu/recent':           to_str(imu_recent),
            'imu/mpu_timestamp':    to_float(imu_mpu_timestamp),
        }
        return json.dumps(message)