# -*- coding: utf-8 -*-
"""
AWS IoT Core 利用時のユーティリティモジュール。

| **関数名** | **用途** |
|:--|:--|
| `arr_to_bytearray` | Donkey Carイメージファイル操作：nd.array形式からbytearray型へ変換する |
| `bytearray_to_arr` | Donkey Carイメージファイル操作：bytearray型からnd.array形式へ変換する |
| `create_json_topic`  | トピック名作成：RATF準拠のJSON型データ送受信用トピック名を作成する |
| `create_image_topic` | トピック名作成：RATF準拠のimage_array型データ送受信用トピック名を作成する |
| `create_bin_topic`   | トピック名作成：RATF準拠のバイトデータ(bytes/bytearray)送受信用トピック名を作成する |
"""
import numpy as np
import donkeycar as dk

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
        return dk.utils.img_to_arr(dk.util.img.binary_to_img(binary))
    else:
        raise ValueError('unknown type=' +str(type(binary)))


def create_json_topic(system='real', thing_type='agent', thing_group='loader',
thing_name='john_doe', message_type='tub'):
    return _create_base_topic(system, thing_type, thing_group, thing_name, message_type) + '/json'

def create_image_topic(system='real', thing_type='agent', thing_group='loader',
thing_name='john_doe', message_type='tub'):
    return _create_base_topic(system, thing_type, thing_group, thing_name, message_type) + '/image'

def create_bin_topic(system='real', thing_type='agent', thing_group='loader',
thing_name='john_doe', message_type='tub'):
    return _create_base_topic(system, thing_type, thing_group, thing_name, message_type) + '/bin'

def _create_base_topic(system, thing_type, thing_group, thing_name, message_type):
    return '/' + system + '/' + thing_type + '/' + thing_group + '/' + thing_name + '/' + message_type
