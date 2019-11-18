# -*- coding: utf-8 -*-
"""
MarvelmindデータをAWS IoT Core へ Publish するパーツクラスを定義するモジュール。
"""
import time
import json
from .base import PublisherBase, to_float, to_str
from .topic import pub_hedge_usnav_json_topic, pub_hedge_usnav_raw_json_topic, pub_hedge_imu_json_topic


class USNavPublisher(PublisherBase):
    """
    Marvelmindデータ(辞書型、位置情報データのみ)をAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'USNav', debug)
        self.topic = pub_hedge_usnav_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[USNavPublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, usnav_id, usnav_x, us_nav_y, usnav_z, usnav_angle, usnav_timestamp):
        """
        Marvelmindデータ(辞書型、位置情報データのみ)をPublishする。
        引数：
            usnav_id        モバイルビーコンID
            usnav_x         位置情報(X軸)
            usnav_y         位置情報(Y軸)
            usnav_z         位置情報(Z軸)
            usnav_angle     位置情報(向き)
            usnav_timestamp 位置情報取得時刻
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                usnav_id, usnav_x, us_nav_y, usnav_z, usnav_angle, usnav_timestamp), 
                self.qos)
        if self.debug:
            print('[USNavPublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, usnav_id=None, usnav_x=None, usnav_y=None, usnav_z=None, 
    usnav_angle=None, usnav_timestamp=None):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            usnav_id        モバイルビーコンID
            usnav_x         位置情報(X軸)
            usnav_y         位置情報(Y軸)
            usnav_z         位置情報(Z軸)
            usnav_angle     位置情報(向き)
            usnav_timestamp 位置情報取得時刻
        戻り値：
            メッセージ文字列
        """
        message = {
            'usnav/id':         to_str(usnav_id),
            'usnav/x':          to_float(usnav_x),
            'usnav/y':          to_float(usnav_y),
            'usnav/z':          to_float(usnav_z),
            'usnav/timestamp':  to_float(usnav_timestamp),
        }
        return json.dumps(message)

class USNavRawPublisher(PublisherBase):
    """
    Marvelmindデータ(辞書型、ビーコン間距離データのみ)を
    AWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'USNavRaw', debug)
        self.topic = pub_hedge_usnav_raw_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[USNavRawPublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d,
    dist_b3, dist_b3d, dist_b4, dist_b4d, dist_timestamp):
        """
        Marvelmindデータ(辞書型、ビーコン間距離データのみ)をPublishする。
        引数：
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
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d,
                dist_b3, dist_b3d, dist_timestamp), 
            self.qos)
        if self.debug:
            print('[USNavRawPublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, dist_id=None, dist_b1=None, dist_b1d=None, dist_b2=None,
    dist_b2d=None, dist_b3=None, dist_b3d=None, dist_b4=None, dist_b4d=None,
    dist_timestamp=None):
        """
        Marvelmindデータ(辞書型、ビーコン間距離データのみ)を
        メッセージ文字列化する。
        引数：
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
        戻り値：
            メッセージ文字列
        """
        message = {
            'dist/id':          to_str(dist_id),
            'dist/b1':          to_str(dist_b1),
            'dist/b1d':         to_float(dist_b1d),
            'dist/b2':          to_str(dist_b2),
            'dist/b2d':         to_float(dist_b2d),
            'dist/b3':          to_str(dist_b3),
            'dist/b3d':         to_float(dist_b3d),
            'dist/b4':          to_str(dist_b4),
            'dist/b4d':         to_float(dist_b4d),
            'dist/timestamp':   to_str(dist_timestamp),
        }
        return json.dumps(message)

class IMUPublisher(PublisherBase):
    """
    Marvelmindデータ(辞書型、IMUデータのみ)を
    AWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'IMU', debug)
        self.topic = pub_hedge_usnav_raw_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[IMUPublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz,
    imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz,
    imu_mx, imu_my, imu_mz,
    imu_timestamp):
        """
        Marvelmindデータ(辞書型、IMUデータのみ)をPublishする。
        引数：
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
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz,
                imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az,
                imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz,
                imu_timestamp), 
            self.qos)
        if self.debug:
            print('[IMUPublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, imu_x=None, imu_y=None, imu_z=None,
    imu_qw=None, imu_qx=None, imu_qy=None, imu_qz=None,
    imu_vx=None, imu_vy=None, imu_vz=None,
    imu_ax=None, imu_ay=None, imu_az=None,
    imu_gx=None, imu_gy=None, imu_gz=None,
    imu_mx=None, imu_my=None, imu_mz=None,
    imu_timestamp=None):
        """
        Marvelmindデータ(辞書型、IMUデータのみ)を
        メッセージ文字列化する。
        引数：
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
        戻り値：
            メッセージ文字列
        """
        message = {
            'imu/x':            to_float(imu_x),
            'imu/y':            to_float(imu_y),
            'imu/z':            to_float(imu_z),
            'imu/qw':           to_float(imu_qw),
            'imu/qx':           to_float(imu_qx),
            'imu/qy':           to_float(imu_qy),
            'imu/qz':           to_float(imu_qz),
            'imu/vx':           to_float(imu_vx),
            'imu/vy':           to_float(imu_vy),
            'imu/vz':           to_float(imu_vz),
            'imu/ax':           to_float(imu_ax),
            'imu/ay':           to_float(imu_ay),
            'imu/az':           to_float(imu_az),
            'imu/gx':           to_float(imu_gx),
            'imu/gy':           to_float(imu_gy),
            'imu/gz':           to_float(imu_gz),
            'imu/mx':           to_float(imu_mx),
            'imu/my':           to_float(imu_my),
            'imu/mz':           to_float(imu_mz),
            'imu/timestamp':    to_str(imu_timestamp),
        }
        return json.dumps(message)