# -*- coding: utf-8 -*-
"""
TubデータをAWS IoT Core から Subscribe するパーツクラスを定義するモジュール。
real/agent/loaderをSubscribeする。
"""
from .base import SubscriberBase, bytearray_to_arr
from .topic import sub_tub_json_topic, sub_tub_image_topic, sub_tub_fwd_image_topic, SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER

class UserSubscriber(SubscriberBase):
    """
    Tubデータ(辞書型、手動運転データのみ)をAWS IoT Coreから Subscribe するパーツクラス。
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
        self.topic = sub_tub_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[UserSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='User', topic_name=self.topic, debug=debug)

    def run(self):
        """
        手動運転のみのTubデータをPublishする。
        引数：
            なし
        戻り値：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            user_mode           運転モード
            timestamp           Subscribe時点の時刻(time.time()結果)
        """
        if self.debug:
            print('[UserSubscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('user/angle', 0.0), \
            self.message.get('user/throttle', 0.0), \
            self.message.get('user/lift_throttle', 0.0), \
            self.message.get('user/mode', 'user'), \
            self.message.get('timestamp', 0.0)

class Subscriber(SubscriberBase):
    """
    Tubデータ(辞書型、手動・自動運転データ両方)を
    AWS IoT Coreから Subscribe するパーツクラス。
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
        self.topic = sub_tub_json_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[Subscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Subscribeした手動・自動運転両方のTubデータを取得する。
        引数：
            なし
        戻り値：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            pilot_angle         自動ステアリング値
            pilot_throttle      自動スロットル値
            pilot_lift_throttle 自動リフト値
            user_mode           運転モード
            timestamp           Subscribe時点の時刻(time.time()結果)
        """
        if self.debug:
            print('[Subscriber] subscribed:{}'.format(str(self.arrive)))
        if self.message is None:
            self.message = {}
        return self.message.get('user/angle', 0.0), \
            self.message.get('user/throttle', 0.0), \
            self.message.get('user/lift_throttle', 0.0), \
            self.message.get('pilot/angle', 0.0), \
            self.message.get('pilot/throttle', 0.0), \
            self.message.get('pilot/lift_throttle', 0.0), \
            self.message.get('user/mode', 'user'), \
            self.message.get('timestamp', 0.0)

class ImageSubscriber(SubscriberBase):
    """
    Tubデータ(cam/image_array)を
    AWS IoT CoreへPublishするパーツクラス。
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
        self.topic = sub_tub_image_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[ImageSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Image', topic_name=self.topic, debug=debug)

    def run(self):
        """
        手動・自動運転両方のTubデータをPublishする。
        引数：
            なし
        戻り値：
            イメージデータ(nd.array形式)
        """
        if self.debug:
            print('[ImageSubscriber] subscribed:{}'.format(str(self.arrive)))
        return self.message

class FwdImageSubscriber(SubscriberBase):
    """
    Tubデータ(fwd/image_array)を
    Subscribeするパーツクラス。
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
        self.topic = sub_tub_fwd_image_topic(
            SYSTEM_REAL, THING_TYPE_AGENT, THING_GROUP_LOADER)
        if debug:
            print('[FwdImageSubscriber] topic name = {}'.format(self.topic))
        super().__init__(aws_iot_client_factory, name='Image', topic_name=self.topic, debug=debug)

    def run(self):
        """
        Tubデータ(前方視界データ)をPublishする。
        引数：
            なし
        戻り値：
            イメージデータ(nd.array形式)
        """
        if self.debug:
            print('[FwdImageSubscriber] subscribed:{}'.format(str(self.arrive)))
        return self.message