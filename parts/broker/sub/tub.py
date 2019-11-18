# -*- coding: utf-8 -*-
"""
TubデータをAWS IoT Core から Subscribe するパーツクラスを定義するモジュール。
"""
from base import SubscriberBase, bytearray_to_arr
from topic import sub_tub_json_topic, sub_tub_image_topic

class UserSubscriber(SubscriberBase):
    """
    Tubデータ(辞書型、手動運転データのみ)をAWS IoT Coreから Subscribe するパーツクラス。
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
        self.topic = sub_tub_json_topic(
            self.system, self.thing_type, self.thing_group)
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
        return self.to_values()

    def to_values(self):
        """
        手動運転のみのTubデータをメッセージ文字列から抽出する。
        引数： 
            なし
        戻り値：
            user_angle          手動ステアリング値
            user_throttle       手動スロットル値
            user_lift_throttle  手動リフト値
            user_mode           運転モード
            timestamp           Subscribe時点の時刻(time.time()結果)
        """
        if self.message is None:
            return 0.0, 0.0, 0.0, 'user', 0.0
        return self.message.get('user/aggle', 0.0), \
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
        引数：
            aws_iot_client_factory  AWS IoT Coreファクトリオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.topic = sub_tub_json_topic(
            self.system, self.thing_type, self.thing_group)
        if debug:
            print('[UserSubscriber] topic name = {}'.format(self.topic))
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
        return self.to_values()

    def to_values(self):
        """
        手動・自動運転両方のTubデータをメッセージ文字列化する。
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
        if self.message is None:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'user', 0.0
        return self.message.get('user/aggle', 0.0), \
            self.message.get('user/throttle', 0.0), \
            self.message.get('user/lift_throttle', 0.0), \
            self.message.get('pilot/aggle', 0.0), \
            self.message.get('pilot/throttle', 0.0), \
            self.message.get('pilot/lift_throttle', 0.0), \
            self.message.get('user/mode', 'user'), \
            self.message.get('timestamp', 0.0)

class ImageSubscriber(SubscriberBase):
    """
    Tubデータ(辞書型、手動・自動運転データ両方)を
    AWS IoT CoreへPublishするパーツクラス。
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
        self.topic = sub_tub_image_topic(
            self.system, self.thing_type, self.thing_group)
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
        return self.message
