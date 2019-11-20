# -*- coding: utf-8 -*-
"""
Joystick データをAWS IoT Core から Subscribe するパーツクラスを定義するモジュール。
"""
from .base import SubscriberBase
from .topic import sub_joystick_json_topic, SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER

class JoystickPublisher(SubscriberBase):
    """
    ジョイスティックデータをAWS IoT CoreへPublishするパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        self.topic = sub_joystick_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[USNavSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Joystick', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribe したジョイスティックデータを取得する。
        引数：
            なし
        戻り値：
            user_angle          アングル値
            user_throttle       スロットル値
            user_lift_throttle  リフト値
            user_mode           運転モード
            recording           記録モード
        """
        if self.debug:
            print('[JoystickSubscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('user/angle', 0.0), \
            self.message.get('user/throttle', 0.0), \
            self.message.get('user/lift_throttle', 0.0), \
            self.message.get('user/mode', 'user'), \
            self.message.get('recording', True)
