# -*- coding: utf-8 -*-
"""
MPU9250から取得したIMUデータをSubscribeするパーツクラス群。
"""
from base import SubscriberBase
from topic import sub_mpu6050_json_topic, sub_mpu9250_json_topic

class Mpu6050Subscriber(SubscriberBase):
    """
    MPU5050 IMUデータ(辞書型)をAWS IoT Core から
    Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_mpu6050_json_topic(
            self.system, self.thing_type, self.thing_group)
        if debug:
            print('[Mpu6050Subscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Mpu6050', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した MPU6050 IMUデータ(辞書型)を取得する。
        引数：
            なし
        戻り値：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_timestamp   Subscribeした時刻(time.time()結果)
        """
        if self.message is None:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        return self.message.get('imu/vx', 0.0), \
            self.message.get('imu/vy', 0.0), \
            self.message.get('imu/vz', 0.0), \
            self.message.get('imu/ax', 0.0), \
            self.message.get('imu/ay', 0.0), \
            self.message.get('imu/az', 0.0), \
            self.message.get('imu/timestamp', 0.0)

class Mpu9250Subscriber(SubscriberBase):
    """
    MPU9250 IMUデータ(辞書型)をAWS IoT Core から
    Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_mpu9250_json_topic(
            self.system, self.thing_type, self.thing_group)
        if debug:
            print('[Mpu6050Subscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Mpu9250', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した MPU9250 IMUデータを取得する。
        引数：
            なし
        戻り値：
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_mx          磁束密度(X軸)
            imu_my          磁束密度(Y軸)
            imu_mz          磁束密度(Z軸)
            imu_timestamp   Subscribeした時刻(time.time()結果)
        """
        if self.message is None:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        return self.message.get('imu/vx', 0.0), \
            self.message.get('imu/vy', 0.0), \
            self.message.get('imu/vz', 0.0), \
            self.message.get('imu/ax', 0.0), \
            self.message.get('imu/ay', 0.0), \
            self.message.get('imu/az', 0.0), \
            self.message.get('imu/mx', 0.0), \
            self.message.get('imu/my', 0.0), \
            self.message.get('imu/mz', 0.0), \
            self.message.get('imu/timestamp', 0.0)
