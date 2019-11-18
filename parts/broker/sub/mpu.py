# -*- coding: utf-8 -*-
"""
MPU9250から取得したIMUデータをSubscribeするパーツクラス群。
同じシステム分類内のagent/loaderをSubscribeする。
"""
from .base import SubscriberBase
from .topic import sub_mpu6050_json_topic, sub_mpu9250_json_topic, THING_TYPE_AGENT, THING_GROUP_LOADER

class Mpu6050Subscriber(SubscriberBase):
    """
    MPU5050 IMUデータ(辞書型)をAWS IoT Core から
    Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        同じシステム分類内のagent/loaderをSubscribeする。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_mpu6050_json_topic(
            self.system, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[Mpu6050Subscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Mpu6050', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した MPU6050 IMUデータ(辞書型)を取得する。
        引数：
            なし
        戻り値：
            imu/acl_x           加速度(X軸)
            imu/acl_y           加速度(Y軸)
            imu/acl_z           加速度(Z軸)
            imu/gyr_x           角速度(X軸)
            imu/gyr_y           角速度(Y軸)
            imu/gyr_z           角速度(Z軸)
            imu/mpu_timestamp   Subscribeした時刻(time.time()結果)
        """
        if self.message is None:
            self.message = {}
        return self.message.get('imu/acl_x', 0.0), \
            self.message.get('imu/acl_y', 0.0), \
            self.message.get('imu/acl_z', 0.0), \
            self.message.get('imu/gyr_x', 0.0), \
            self.message.get('imu/gyr_y', 0.0), \
            self.message.get('imu/gyr_z', 0.0), \
            self.message.get('imu/mpu_timestamp', 0.0)

class Mpu9250Subscriber(SubscriberBase):
    """
    MPU9250 IMUデータ(辞書型)をAWS IoT Core から
    Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        同じシステム分類内のagent/loaderをSubscribeする。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_mpu9250_json_topic(
            self.system, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[Mpu6050Subscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Mpu9250', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した MPU9250 IMUデータを取得する。
        引数：
            なし
        戻り値：
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_gx          角速度(X軸)
            imu_gy          角速度(Y軸)
            imu_gz          角速度(Z軸)
            imu_mx          磁束密度(X軸)
            imu_my          磁束密度(Y軸)
            imu_mz          磁束密度(Z軸)
            imu_temp        温度(C)
            imu_timestamp   Subscribeした時刻(time.time()結果)
        """
        if self.message is None:
            self.message = {}
        return self.message.get('imu/acl_x', 0.0), \
            self.message.get('imu/acl_y', 0.0), \
            self.message.get('imu/acl_z', 0.0), \
            self.message.get('imu/gyr_x', 0.0), \
            self.message.get('imu/gyr_y', 0.0), \
            self.message.get('imu/gyr_z', 0.0), \
            self.message.get('imu/mgt_x', 0.0), \
            self.message.get('imu/mgt_y', 0.0), \
            self.message.get('imu/mgt_z', 0.0), \
            self.message.get('imu/temp', 0.0), \
            self.message.get('imu/mpu_timestamp', 0.0)
