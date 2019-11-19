# -*- coding: utf-8 -*-
"""
Joystick データをAWS IoT Core へ Publish するパーツクラスを定義するモジュール。
"""
import time
import json
from .base import PublisherBase, to_float, to_str
from .topic import pub_joystick_json_topic

class JoystickPublisher(PublisherBase):
    """
    ジョイスティックデータをAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        super().__init__(aws_iot_client_factory, 'Joystick', debug)
        self.topic = pub_joystick_json_topic(
            self.system, self.thing_type, self.thing_group, self.thing_name)
        if self.debug:
            print('[JoystickPublisher] topic name = {}'.format(self.topic))
        self.qos = 0

    def run(self, user_angle, user_throttle, user_lift_throttle, user_mode, recording):
        """
        MPU6050 IMUデータ(辞書型)をPublishする。
        引数：
            user_angle          アングル値
            user_throttle       スロットル値
            user_lift_throttle  リフト値
            user_mode           運転モード
            recording           記録モード
        戻り値：
            なし
        """
        ret = self.client.publish(
            self.topic, 
            self.to_message(
                user_angle, user_throttle, user_lift_throttle, user_mode, recording), 
            self.qos)
        if self.debug:
            print('[JoystickPublisher] publish topic={} ret={}'.format(self.topic, str(ret)))

    def to_message(self, user_angle, user_throttle, user_lift_throttle, user_mode, recording):
        """
        手動運転のみのTubデータをメッセージ文字列化する。
        引数：
            user_angle          アングル値
            user_throttle       スロットル値
            user_lift_throttle  リフト値
            user_mode           運転モード
            recording           記録モード
        戻り値：
            メッセージ文字列
        """
        message = {
            'user/angle':           to_float(user_angle),
            'user/throttle':        to_float(user_throttle),
            'user/lift_throttle':   to_float(user_lift_throttle),
            'user/mode':            to_str(user_mode),
            'recording':            recording,
        }
        return json.dumps(message)