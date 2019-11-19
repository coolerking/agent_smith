# -*- coding: utf-8 -*-
"""
MarvelmindデータをAWS IoT Core から Subscribeするパーツクラスを定義するモジュール。
real/agent/loaderをSubscribeする。
"""
from .base import SubscriberBase
from .topic import sub_hedge_usnav_json_topic, sub_hedge_usnav_raw_json_topic, sub_hedge_imu_json_topic, SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER


class USNavSubscriber(SubscriberBase):
    """
    Marvelmindデータ(辞書型、位置情報データのみ)をAWS IoT Core から
    Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        real/agent/loaderをSubscribeする。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_hedge_usnav_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[USNavSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='USNav', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した Marvelmind データ(辞書型、位置情報データのみ)を取得する。
        引数：
            なし
        戻り値：
            usnav_id        モバイルビーコンID
            usnav_x         位置情報(X軸)
            usnav_y         位置情報(Y軸)
            usnav_z         位置情報(Z軸)
            usnav_angle     位置情報(向き)
            usnav_timestamp 位置情報取得時刻
        """
        if self.debug:
            print('[USNavSubscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('usnav/id', '0'), \
            self.message.get('usnav/x', 0.0), \
            self.message.get('usnav/y', 0.0), \
            self.message.get('usnav/z', 0.0), \
            self.message.get('usnav/angle', 0.0), \
            self.message.get('usnav/timestamp', 0)

class USNavRawSubscriber(SubscriberBase):
    """
    Marvelmindデータ(辞書型、ビーコン間距離データのみ)を
    AWS IoT Core から Subscribe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        real/agent/loaderをSubscribeする。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_hedge_usnav_raw_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[USNavRawSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='USNavRaw', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した Marvelmindデータ(辞書型、ビーコン間距離データのみ)を取得する。
        引数：
            なし
        戻り値：
            dist_id         モバイルビーコンID
            dist_b1         対象となるビーコンID1
            dist_b1d        ビーコンID1との距離
            dist_b2         対象となるビーコンID2
            dist_b2d        ビーコンID2との距離
            dist_b3         対象となるビーコンID3
            dist_b3d        ビーコンID3との距離
            dist_b4         対象となるビーコンID4
            dist_b4d        ビーコンID4との距離
            dist_timestamp  ビーコン間距離取得時刻
        """
        if self.debug:
            print('[USNavRawSubscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('dist/id', '0'), \
            self.message.get('dist/b1', '0'), \
            self.message.get('dist/b1d', 0.0), \
            self.message.get('dist/b2', '0'), \
            self.message.get('dist/b2d', 0.0), \
            self.message.get('dist/b3', '0'), \
            self.message.get('dist/b3d', 0.0), \
            self.message.get('dist/b4', '0'), \
            self.message.get('dist/b4d', 0.0), \
            self.message.get('dist/timestamp', 0)

class IMUSubscriber(SubscriberBase):
    """
    Marvelmindデータ(辞書型、IMUデータのみ)を
    AWS IoT Core から Subscirbe するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        Subscribeを実行する。
        real/agent/loaderをSubscribeする。
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_hedge_imu_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[IMUSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='IMU', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe した Marvelmindデータ(辞書型、IMUデータのみ)を取得する。
        引数：
            なし
        戻り値：
            imu_x           位置情報(X軸)
            imu_y           位置情報(Y軸)
            imu_z           位置情報(Z軸)
            imu_qw          四元数(Q)
            imu_qx          四元数(X)
            imu_qy          四元数(Y)
            imu_qz          四元数(Z)
            imu_vx          速度(X軸)
            imu_vy          速度(Y軸)
            imu_vz          速度(Z軸)
            imu_ax          加速度(X軸)
            imu_ay          加速度(Y軸)
            imu_az          加速度(Z軸)
            imu_gx          角速度(X軸)
            imu_gy          角速度(Y軸)
            imu_gz          角速度(Z軸)
            imu_mx          磁束密度(X軸)
            imu_my          磁束密度(Y軸)
            imu_mz          磁束密度(Z軸)
            imu_timestamp   IMUデータ取得時刻
        """
        if self.debug:
            print('[IMUSubscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('imu/x', 0.0), \
            self.message.get('imu/y', 0.0), \
            self.message.get('imu/z', 0.0), \
            self.message.get('imu/qw', 0.0), \
            self.message.get('imu/qx', 0.0), \
            self.message.get('imu/qy', 0.0), \
            self.message.get('imu/qz', 0.0), \
            self.message.get('imu/vx', 0.0), \
            self.message.get('imu/vy', 0.0), \
            self.message.get('imu/vz', 0.0), \
            self.message.get('imu/ax', 0.0), \
            self.message.get('imu/ay', 0.0), \
            self.message.get('imu/az', 0.0), \
            self.message.get('imu/gx', 0.0), \
            self.message.get('imu/gy', 0.0), \
            self.message.get('imu/gz', 0.0), \
            self.message.get('imu/mx', 0.0), \
            self.message.get('imu/my', 0.0), \
            self.message.get('imu/mz', 0.0), \
            self.message.get('imu/timestamp', 0)
