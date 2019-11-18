# -*- coding: utf-8 -*-
"""
Subscriber用トピック文字列生成モジュール。
RATFでは、以下の形式でトピックを定義する。

<システムの種類>/<モノのタイプ>/<モノのグループ>/<モノの名前>/<メッセージタイプ>/<データ形式>

"""

""" ワイルドカード """
WILDCARD_ONE = '+'
WILDCARD_ANY = '#'
WILDCARDS = [
    WILDCARD_ONE,
    WILDCARD_ANY,
]

""" システムの種類 """
SYSTEM_REAL = 'real'
SYSTEM_VIRTUAL = 'virtual'
SYSTEMS = [
    SYSTEM_REAL,
    SYSTEM_VIRTUAL,
    WILDCARD_ONE,
    #WILDCARD_ANY,
]

""" モノのタイプ """
THING_TYPE_AGENT = 'agent'
THING_TYPE_MONITOR = 'monitor'
THING_TYPES = [
    THING_TYPE_AGENT,
    THING_TYPE_MONITOR,
    WILDCARD_ONE,
]

""" モノのグループ """
THING_GROUP_LOADER = 'loader'
THING_GROUP_MONITOR = 'monitor'
THING_GROUP_SIMULATOR = 'simulator'
THING_GROUPS = [
    THING_GROUP_LOADER,
    THING_GROUP_MONITOR,
    THING_GROUP_SIMULATOR,
    WILDCARD_ONE,
]

""" メッセージタイプ """
MESSAGE_TYPE_TUB = 'tub'
MESSAGE_TYPE_IMAGE = 'image'
MESSAGE_TYPE_HEDGE_USNAV = 'usnav'
MESSAGE_TYPE_HEDGE_USNAV_RAW = 'dist'
MESSAGE_TYPE_HEDGE_IMU = 'imu'
MESSAGE_TYPE_MPU6050 = 'mpu6050'
MESSAGE_TYPE_MPU9250 = 'mpu9250'
MESSAGE_TYPES = [
    MESSAGE_TYPE_TUB,
    MESSAGE_TYPE_IMAGE,
    MESSAGE_TYPE_HEDGE_USNAV,
    MESSAGE_TYPE_HEDGE_USNAV_RAW,
    MESSAGE_TYPE_HEDGE_IMU,
    MESSAGE_TYPE_MPU6050,
    MESSAGE_TYPE_MPU9250,
    WILDCARD_ONE,
]

""" データ型 """
DATA_TYPE_JSON = 'json'
DATA_TYPE_IMAGE = 'image'
DATA_TYPE_BIN = 'bin'
DATA_TYPES = [
    DATA_TYPE_JSON,
    DATA_TYPE_IMAGE,
    DATA_TYPE_BIN,
    WILDCARD_ONE,
    #WILDCARD_ANY,
]

""" セパレータ文字列 """
SEP = '/'

def _sub_base_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE,
thing_group=WILDCARD_ONE, thing_name=WILDCARD_ONE, message_type=WILDCARD_ONE,
data_type=WILDCARD_ONE):
    """
    Subscriber 用のトピック文字列を返却する。
    引数：
        system          システムの種類
        thing_type      モノのタイプ
        thing_group     モノのグループ
        thing_name      モノの名前
        message_type    メッセージタイプ 
        data_type       データ型
    戻り値：
        トピック名
    """
    if system not in SYSTEMS:
        raise ValueError('unknown system = {}'.format(str(system)))
    if thing_type not in THING_TYPES:
        raise ValueError('unknown thing type = {}'.format(str(thing_type)))
    if thing_group not in THING_GROUPS:
        raise ValueError('unknown thing group = {}'.format(str(thing_group)))
    if thing_name is None or thing_name == '':
        raise ValueError('illegal thing name = {}'.format(str(thing_name)))
    if message_type not in MESSAGE_TYPES:
        raise ValueError('unknown message type = {}'.format(str(message_type)))
    if data_type not in DATA_TYPES:
        raise ValueError('unknown data type = {}'.format(str(data_type)))
    return system + \
        SEP + thing_type + \
        SEP + thing_group + \
        SEP + thing_name + \
        SEP + message_type + \
        SEP + data_type

def sub_tub_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    Tubデータ(辞書型)を Subscribe する際に使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_TUB, DATA_TYPE_JSON)

def sub_tub_image_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    Tubデータ(イメージ、nd.array型)を Subscribe する際に使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_TUB, DATA_TYPE_IMAGE)

def sub_mpu9250_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    MPU9250データ(辞書型)を Subscribe する際に使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_MPU9250, DATA_TYPE_JSON)

def sub_mpu6050_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    MPU6050データ(辞書型)を Subscribe する際に使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_MPU6050, DATA_TYPE_JSON)

def sub_hedge_usnav_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    Marvelmindデータ(辞書型、位置情報のみ)を Subscribe する際に
    使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_HEDGE_USNAV, DATA_TYPE_JSON)

def sub_hedge_usnav_raw_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    Marvelmindデータ(辞書型、距離情報のみ)を Subscribe する際に
    使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_HEDGE_USNAV_RAW, DATA_TYPE_JSON)

def sub_hedge_imu_json_topic(system=WILDCARD_ONE, thing_type=WILDCARD_ONE, thing_group=WILDCARD_ONE):
    """
    Marvelmindデータ(辞書型、IMU情報のみ)を Subscribe する際に
    使用するトピック名を返却する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
    戻り値：
        トピック名
    """
    return _sub_base_topic(system, thing_type, thing_group, WILDCARD_ONE, 
        MESSAGE_TYPE_HEDGE_IMU, DATA_TYPE_JSON)

''' トピック名分類ユーティリティ '''

def is_json(topic_name):
    """
    トピック名からメッセージがJSON形式データであるかどうか判別する。
    引数：
        topic_name  トピック名
    戻り値：
        真偽値
    """
    if topic_name is None or topic_name == '':
        return False
    return topic_name.endswith(DATA_TYPE_JSON)

def is_image(topic_name):
    """
    トピック名からメッセージがイメージデータであるかどうか判別する。
    引数：
        topic_name  トピック名
    戻り値：
        真偽値
    """
    if topic_name is None or topic_name == '':
        return False
    return topic_name.endswith(DATA_TYPE_IMAGE)

def is_bin(topic_name):
    """
    トピック名からメッセージがbytearray型データであるかどうか判別する。
    引数：
        topic_name  トピック名
    戻り値：
        真偽値
    """
    if topic_name is None or topic_name == '':
        return False
    return topic_name.endswith(DATA_TYPE_BIN)

def is_thing_name(system, thing_type, thing_group, thing_name, topic_name):
    """
    トピック名から、引数で渡されたモノの名前から送信された
    メッセージであるかどうかを判別する。
    引数：
        system      システムの種類
        thing_type  モノのタイプ
        thing_group モノのグループ
        thing_name  モノの名前
        topic_name  トピック名
    戻り値：
        真偽値
    """
    prefix = system + SEP + thing_type + SEP + thing_group + \
        SEP + thing_name + SEP
    if topic_name is None or topic_name == '':
        return False
    return topic_name.startswith(prefix)
