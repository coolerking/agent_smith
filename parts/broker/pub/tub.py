# -*- coding: utf-8 -*-
"""
TubデータをAWS IoT Core へ Publish するパーツクラスを定義するモジュール。
"""
import time
import json
from .base import PublisherBase, to_float, to_str, arr_to_bytearray
from .topic import pub_tub_json_topic, pub_tub_image_topic

class UserPublisher(PublisherBase):
    """
    Tubデータ(辞書型、手動運転データのみ)をAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory,'User', debug)
        self.topic = pub_tub_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[UserPublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, user_angle, user_throttle, user_lift_throttle, user_mode):
        """
        手動運転のみのTubデータをPublishする。
        引数：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            user_mode           運転モード
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                user_angle, user_throttle, user_lift_throttle, user_mode), 
                self.qos)
        if self.debug:
            print('[UserPublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, user_angle=None, user_throttle=None, 
    user_lift_throttle=None, user_mode=None):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            user_mode           運転モード
        戻り値：
            メッセージ文字列
        """
        message = {
            'user/aggle':           to_float(user_angle),
            'user/throttle':        to_float(user_throttle),
            'user/lift_throttle':   to_float(user_lift_throttle),
            'user/mode':            to_str(user_mode),
            'timestamp':            to_float(time.time()),
        }
        return json.dumps(message)

class Publisher(PublisherBase):
    """
    Tubデータ(辞書型、手動・自動運転データ両方)を
    AWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, '', debug)
        self.topic = pub_tub_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[Publisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, user_angle, user_throttle, user_lift_throttle,
    pilot_angle, pilot_throttle, pilot_lift_throttle, user_mode):
        """
        手動・自動運転両方のTubデータをPublishする。
        引数：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            pilot_angle         自動ステアリング値
            pilot_throttle      自動スロットル値
            pilot_lift_throttle 自動リフト値
            user_mode           運転モード
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                user_angle, user_throttle, user_lift_throttle, user_mode), 
                self.qos)
        if self.debug:
            print('[Publisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, user_angle=None, user_throttle=None, user_lift_throttle=None, 
    pilot_angle=None, pilot_throttle=None, pilot_lift_throttle=None,user_mode=None):
        """
        手動・自動運転両方のTubデータをメッセージ文字列化する。
        引数：
                user_angle          手動ステアリング値
                user_throttle       手動スロットル値
                user_lift_throttle  手動リフト値
                pilot_angle         自動ステアリング値
                pilot_throttle      自動スロットル値
                pilot_lift_throttle 自動リフト値
                user_mode           運転モード
        戻り値：
            メッセージ文字列
        """
        message = {
            'user/aggle':           to_float(user_angle),
            'user/throttle':        to_float(user_throttle),
            'user/lift_throttle':   to_float(user_lift_throttle),
            'pilot/aggle':          to_float(pilot_angle),
            'pilot/throttle':       to_float(pilot_throttle),
            'pilot/lift_throttle':  to_float(pilot_lift_throttle),
            'user/mode':            to_str(user_mode),
            'timestamp':            to_float(time.time()),
        }
        return json.dumps(message)

class ImagePublisher(PublisherBase):
    """
    Tubデータ(辞書型、手動・自動運転データ両方)を
    AWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'Image', debug)
        self.topic = pub_tub_image_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[ImagePublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, image_array):
        """
        手動・自動運転両方のTubデータをPublishする。
        引数：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            pilot_angle         自動ステアリング値
            pilot_throttle      自動スロットル値
            pilot_lift_throttle 自動リフト値
            user_mode           運転モード
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            arr_to_bytearray(image_array), 
                self.qos)
        if self.debug:
            print('[ImagePublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

