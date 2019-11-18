# -*- coding: utf-8 -*-
"""
AWS IoT Core Subscriber基底クラスを定義するモジュール。
"""
import time
import json
import donkeycar as dk
import numpy as np
from topic import is_json, is_image, is_bin, is_thing_name

class SubscriberBase:
    """
    AWS IoT CoreへMQTTプロトコルで送信するSubscriberパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, name='Base', topic_name='#', 
    callback=None, retry=10, debug=False):
        """
        フィールドを初期化する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            name                    名前
            topic_name              Subscribeトピック名
            callback                callback関数
            retry                   Subscribe失敗時繰り返す回数
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.system = aws_iot_client_factory.system
        self.thing_type = aws_iot_client_factory.thing_type
        self.thing_group = aws_iot_client_factory.thing_group
        self.thing_name = aws_iot_client_factory.thing_name
        self.client = aws_iot_client_factory.get_mqtt_client()
        self.name = name
        self.message = None
        self.debug = debug
        if self.debug:
            print('[{}Publisher] init thing_name = {}'.format(
                self.name, self.thing_name))
        self.topic_name = topic_name
        self.qos = 0
        if callback is None:
            ret = self.client.subscribe(self.topic_name, 0, self.mycallback)
        else:
            ret = self.client.subscribe(self.topic_name, 0, callback)
        if not ret:
            print('[{}Publisher] failed subscribing topic={}'.format(
                self.name, self.topic_name))

    def mycallback(self, client, userdata, message):
        """
        トピック名からデータ形式を判別して、それぞれのメッセージペイロード
        に合わせた形式でself.messageへ格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if not is_thing_name(self.system, self.thing_type, 
        self.thing_group, self.thing_name, message.topic):
            if is_image(message.topic):
                self.image_callback(client, userdata, message)
            elif is_bin(message.topic):
                self.bin_callback(client, userdata, message)
            elif is_json(message.topic):
                self.json_callback(client, userdata, message)
            else:
                if self.debug:
                    print('[{}Subscriber] illegal topic({}) data type'.format(
                        self.name, message.topic))
        else:
            if self.debug:
                print('[{}Subscriber] ignore message(myself) :topic({})'.format(
                    self.name, message.topic))

    def image_callback(self, client, userdata, message):
        """
        イメージデータがSubscribeされた場合、self.messageへnd.array形式で格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if self.debug:
            print('[{}Subscriber] image subscribed topic={}'.format(self.name, self.topic_name))
        self.message = bytearray_to_arr(message.payload)

    def json_callback(self, client, userdata, message):
        """
        JSONデータがSubscribeされた場合、self.messageへnd.array形式で格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if self.debug:
            print('[{}Subscriber] image subscribed topic={}'.format(self.name, self.topic_name))
        self.message = json.loads(message.payload)

    def bin_callback(self, client, userdata, message):
        """
        イメージデータがSubscribeされた場合、self.messageへbytearray形式で格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if self.debug:
            print('[{}Subscriber] image subscribed topic={}'.format(self.name, self.topic_name))
        self.message = message.payload

    def shutdown(self):
        """
        実装なし。
        引数：
            なし
        戻り値：
            なし
        """
        self.client = None
        if self.debug:
            print('[{}Publisher] shutdown thing_name = {}'.format(self.name, self.thing_name))

'''ユーティリティ関数'''

def arr_to_bytearray(arr):
    """
    np.array(uint8, (120,160,3))オブジェクトをbytearrayオブジェクトに
    変換する。
    引数：
        arr     np.array(uint8, (120,160,3))オブジェクト
    戻り値：
        bytearray化されたオブジェクト
    """
    return bytearray(_arr_to_bin(arr))

def bytearray_to_arr(bytearray_data):
    """
    bytearrayオブジェクトをnp.array(uint8, (120,160,3))オブジェクトに
    変換する。
    引数：
        bytearray_data      bytearray化されたオブジェクト
    戻り値：
        np.array(uint8, (120,160,3))オブジェクト
    """
    return _bin_to_arr(bytes(bytearray_data))

def _arr_to_bin(arr):
    """
    イメージデータimage_arrayがnd.array型の場合、バイナリに変換する。
    引数：
        arr    イメージデータ
    戻り値：
        bin    バイナリ変換後のイメージデータ
    """
    if type(arr) is bytes or type(arr) is bytearray:
        return arr
    elif type(arr) is np.ndarray:
        return dk.utils.arr_to_binary(arr)
    else:
        raise ValueError('unknown type=' +str(type(arr)))
    
def _bin_to_arr(binary):
    """
    引数binaryの値がバイナリの場合のみ、image_array型式に変換する。
    引数：
        binary          バイナリデータ
    戻り値：
        arr             image_array 型式データ
    """
    if type(binary) is np.ndarray:
        return binary
    elif type(binary) is bytes:
        return dk.utils.img_to_arr(dk.utils.binary_to_img(binary))
    else:
        raise ValueError('unknown type=' +str(type(binary)))


def to_float(value):
    """
    float値に変換する。
    引数：
        value   対象値
    戻り値
        float値
    """
    if value is None or value == '':
        return 0.0
    return float(value)

def to_int(value):
    """
    int値に変換する。
    引数：
        value   対象値
    戻り値
        int値
    """
    if value is None or value == '':
        return 0.0
    return float(value)

def to_str(value):
    """
    文字列に変換する。
    引数：
        value   対象値
    戻り値
        str値
    """
    if value is None:
        return 'None'
    return str(value)