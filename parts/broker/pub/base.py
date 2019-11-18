# -*- coding: utf-8 -*-
"""
AWS IoT Core Publisher 基底クラスを定義するモジュール。
"""
import donkeycar as dk
import numpy as np

class PublisherBase:
    """
    Tubデータ(イメージ、JSONデータ)をMQTTプロトコルで送信する
    パブリッシャパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, name='Base', debug=False):
        """
        フィールドを初期化する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            name                    ターゲット名
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.system = aws_iot_client_factory.system
        self.thing_type = aws_iot_client_factory.thing_type
        self.thing_group = aws_iot_client_factory.thing_group
        self.thing_name = aws_iot_client_factory.thing_name
        self.name = name
        if debug:
            print('[{}Publisher] thing_name = {}'.format(
                self.name,self.thing_name))
        self.client = aws_iot_client_factory.get_mqtt_client()
        self.debug = debug

    def encode_image_message(self, image_array):
        """
        Tubデータ(イメージデータ)をpublish送信するメッセージを取得する。
        引数：
            image_array         イメージデータ
        戻り値：
            メッセージ(bytearray)
        """
        try:
            import donkeycar as dk
        except:
            raise
        return arr_to_bytearray(image_array)

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
            print('[{}Publisher] shutdown'.format(self.name))

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