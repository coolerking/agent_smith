# -*- coding: utf-8 -*-
"""
AWS IoT Core をMQTTブローカとして使用する際のクライアントオブジェクトを提供する。

1. AWS Consoleを開き AWS IoT Coreを構築
2. モノデバイスを1つ作成
3. クライアントアプリが接続するために必要な情報を確認し、認証ファイル群などダウンロード
4. conf/aws/template.yml をコピーして設定ファイルを作成、接続情報を入力
5. クライアントアプリコードでClientオブジェクトを使ってpub/subを実現

またデバイスシャドウを使用するためのラップオブジェクトも提供する。
"""
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient
from time import sleep
from datetime import datetime

import os
import yaml
import json
import numpy as np
import donkeycar as dk

class Config:
    """
    基底抽象クラス。新規のソフトウェアに対応する設定ファイルフォーマット用のサブクラスを
    作成して利用する。
    """
    KEY_THING_TYPE =        'thing_type'
    KEY_THING_GROUP =       'thing_group'
    KEY_THING_NAME =        'thing_name'
    KEY_ENDPOINT    =       'endpoint'
    KEY_PORT        =       'port'
    KEY_USE_WEBSOCKET =     'use_websocket'
    KEY_SYSTEM =            'system'
    KEY_AUTH   =            'auth'
    KEY_ROOT_CA  =              'root_ca'
    KEY_CERTIFICATE =           'certificate'
    KEY_PRIVATE_KEY =           'private_key'

    SEP = '/'

    TOPIC_ORDER = 'order'
    TOPIC_STATUS = 'status'
    TOPIC_REPORT = 'report'

    TYPE_JSON = 'json'
    TYPE_IMAGE_ARRAY = 'image_array'
    TYPE_BIN = 'bin'
    TYPE_STRING = 'string'

    def __init__(self, conf_path, client_id):
        """
        **説明**

        AWS IoT Coreを使用するために必要な設定項目を
        インスタンス変数へ格納する。

        **引数**

        *conf_path* - 設定ファイルのパス

        *client_id* - クライアントID、システム内で一意につける。
        設定ファイル内の設定情報選択にも使用される。

        **戻り値**

        Configインスタンス。
        """
        self.load_config(conf_path, client_id)

    def load_config(self, conf_path, client_id='john_doe'):
        """
        **説明**

        AWS IoT Coreを使用するために必要な設定項目を設定ファイルから
        読み込み、インスタンス変数へ格納する。

        **引数**

        *conf_path* - 設定ファイルのパス

        *client_id* - クライアントID、システム内で一意につける。
        設定ファイル内の設定情報選択にも使用される。

        **戻り値**

        なし。
        """
        conf = self._load_config(conf_path)[client_id]
        self.client_id = client_id
        self.endpoint = conf.get(Config.KEY_ENDPOINT, 'localhost')
        self.thing_type = conf.get(Config.KEY_THING_TYPE, None)
        self.thing_group = conf.get(Config.KEY_THING_GROUP, None)
        self.thing_name = conf.get(Config.KEY_THING_NAME, 'john_doe')
        self.use_websocket = conf.get(Config.KEY_USE_WEBSOCKET, False)
        if self.use_websocket:
            self.port = conf.get(Config.KEY_PORT, 443)
        else:
            self.port = conf.get(Config.KEY_PORT, 8883)
        self.system = conf.get(Config.KEY_SYSTEM, 'real')
        if not self.system.endswith(Config.SEP):
            self.system += Config.SEP
        auth = conf.get(Config.KEY_AUTH, {})
        self.root_ca = auth[Config.KEY_ROOT_CA]
        self.certificate = auth[Config.KEY_CERTIFICATE]
        self.private_key = auth[Config.KEY_PRIVATE_KEY]

    def _get_topic_prefix(self):
        '''
        **説明**

        全デバイス共通となる範囲までのトピック先頭文字列を返却する。

        **引数**

        なし

        **戻り値**

        全デバイス共通となる範囲までのトピック先頭文字列
        '''
        topic = self.system
        if not topic.endswith(Client.SEP):
            topic += Client.SEP
        if self.thing_type is not None:
            topic += self.thing_type
            if not topic.endswith(Client.SEP):
                topic += Client.SEP
        if self.thing_group is not None:
            topic += self.thing_group
            if not topic.endswith(Client.SEP):
                topic += Client.SEP
        topic += self.thing_name
        if not topic.endswith(Client.SEP):
                topic += Client.SEP
        return topic
    
    def _get_status_topic_prefix(self):
        '''
        **説明**

        全デバイス共通となる範囲までのstatusトピック先頭文字列を返却する。

        **引数**

        なし

        **戻り値**

        全デバイス共通となる範囲までのstatusトピック先頭文字列
        '''
        return self._get_topic_prefix() + Client.TOPIC_STATUS + Client.SEP
    
    def _get_report_topic_prefix(self):
        '''
        **説明**

        全デバイス共通となる範囲までのreportトピック先頭文字列を返却する。

        **引数**

        なし

        **戻り値**

        全デバイス共通となる範囲までのreportトピック先頭文字列
        '''
        return self._get_topic_prefix() + Client.TOPIC_REPORT + Client.SEP
    
    def _get_order_topic_prefix(self):
        '''
        **説明**

        全デバイス共通となる範囲までのorderトピック先頭文字列を返却する。

        **引数**

        なし

        **戻り値**

        全デバイス共通となる範囲までのorderトピック先頭文字列
        '''
        return self._get_topic_prefix() + Client.TOPIC_ORDER + Client.SEP
    
    def _get_topic_suffix(self, message):
        '''
        **説明**

        全デバイス共通となる範囲までのトピック末尾文字列を返却する。

        **引数**

        *message* - 送信メッセージ

        **戻り値**

        全デバイス共通となる範囲までのトピック末尾文字列
        '''
        if type(message) is dict:
            return Config.TYPE_JSON
        if type(message) is np.ndarray:
            return Config.TYPE_IMAGE_ARRAY
        if type(message) is bytearray:
            return Config.TYPE_BIN
        return Config.TYPE_STRING

    def get_will_topic(self):
        """
        **説明**

        Willメッセージ用トピックを取得する。

        **戻り値**

        Willメッセージ用トピック文字列
        """
        # $aws/things/thingName/shadow/update
        return '$aws/things/' + self.thing_name + '/shadow/update'
    
    def get_status_topic(self, message):
        """
        **説明**

        statusメッセージ用トピックを取得する。

        **引数**

        *message* - 送信メッセージ

        **戻り値**

        statusメッセージ用トピック文字列
        """
        return self._get_status_topic_prefix() + self._get_topic_suffix(message)
    
    def get_report_topic(self, message):
        """
        **説明**

        reportメッセージ用トピックを取得する。

        **引数**

        *message* - 送信メッセージ

        **戻り値**

        reportメッセージ用トピック文字列
        """
        return self._get_report_topic_prefix() + self._get_topic_suffix(message)

    def get_order_topic(self, message):
        """
        **説明**

        orderメッセージ用トピックを取得する。

        **引数**

        *message* - 送信メッセージ

        **戻り値**

        orderメッセージ用トピック文字列
        """
        return self._get_order_topic_prefix() + self._get_topic_suffix(message)
    
    def get_sub_topic(self):
        """
        **説明**

        Subscribeトピックを取得する。

        **引数**

        *message* - 送信メッセージ

        **戻り値**

        Subscribe トピック文字列
        """
        return self._get_topic_prefix() + '#'

    def _load_config(self, conf_path):
        """
        設定ファイルconf_pathを読み込み、各インスタンス変数に格納する。
        
        引数
            conf_path       設定ファイルパス
        戻り値
            なし
        """
        conf_path = os.path.expanduser(conf_path)
        if not os.path.exists(conf_path):
            raise Exception('conf_path={} is not exists'.format(conf_path))
        if not os.path.isfile(conf_path):
            raise Exception('conf_path={} is not a file'.format(conf_path))

        with open(conf_path, 'r') as f:
            conf = yaml.load(f)
        return conf


class Client(Config):
    """
    AWS IoTクライアントをラップしたクラス。
    """
    def __init__(self, conf_path, client_id, will_message=None):
        """
        **説明**

        AWS IoTクライアントをラップしたオブジェクトを返却する。
        本メソッド処理した時点でブローカとの接続が実行される。

        **引数**

        *conf_path* - 設定ファイルのパス

        *client_id* - クライアントID、システム内で一意につける。
        設定ファイル内の設定情報選択にも使用される。

        *will_message* - Willメッセージ、Noneの場合はWillを送信しない

        **戻り値**

        AWS IoTクライアントをラップしたオブジェクト。
        """
        super().__init__(conf_path=conf_path, client_id=client_id)
        if self.use_websocket:
            client = AWSIoTMQTTClient(self.client_id, useWebsocket=True)
        else:
            client = AWSIoTMQTTClient(self.client_id)
        client.configureEndpoint(self.endpoint, self.port)
        if self.use_websocket:
            client.configureCredentials(self.root_ca)
        else:
            client.configureCredentials(self.root_ca, self.private_key, self.certificate)
        client.configureAutoReconnectBackoffTime(1, 32, 20)
        client.configureOfflinePublishQueueing(-1)
        client.configureDrainingFrequency(2)
        client.configureConnectDisconnectTimeout(10)
        client.configureMQTTOperationTimeout(5)
        if will_message is None:
            will_message = json.dumps({
                "state": {
                    "reported": {
                        "power": "off"
                    }
                }
            })
        client.configureLastWill(self.get_will_topic(), will_message, QoS=0, retain=False)
        print('set will message: {}'.format(will_message))
        client.connect()
        print('connected')
        client.publish(self.get_will_topic(), json.dumps({
                "state": {
                    "reported": {
                        "power": "on"
                    }
                }
        }), QoS=0)
        self.client = client

    def publish(self, topic, message, qos=0):
        """
        **説明**

        引数で渡されたメッセージを発行する。

        **引数**

        *topic* - トピック文字列

        *msg* - メッセージ

        *qos* - QoSレベル(0, 1, 2)、デフォルトは0。

        **戻り値**

        発行が正常に完了したかどうか。
        """
        if type(message) is dict:
            return self.client.publish(topic, json.dumps(message), qos)
        if type(message) is np.ndarray:
            return self.client.publish(topic, arr_to_bytearray(message), qos)
        else:
            return self.client.publish(topic, message, qos)

    def publish_status(self, status_message):
        return self.publish(self.get_status_topic(status_message), status_message, qos=0)

    def publish_report(self, report_message):
        return self.publish(self.get_report_topic(report_message), report_message, qos=1)

    def publish_order(self, order_message):
        return self.publish(self.get_order_topic(order_message), order_message, qos=1)

    def subscribe(self, topic=None, qos=0, callback=None):
        """
        **説明**

        購読を開始する。
        
        **説明**

        *qos* - QoSレベル。デフォルト0。

        *callback* - 購読メッセージ受領時呼び出すコールバック関数。

        **戻り値**

        購読登録が正常におこなわれたかどうか。
        """
        if topic is None:
            topic = self.get_sub_topic()
        if callback is None:
            callback = self._subscribe_callback
        return self.client.subscribe(topic, qos, callback)
    
    def _subscribe_callback(self, client, userdata, message):
        '''
        **説明**

        デフォルトで登録されているサブスクライブ時のコールバック関数。

        **引数**

        *client* - AWS IoT クライアント
        
        *userdata* - ユーザデータ
        
        *message* - 受信メッセージ
        
        **戻り値**

        なし
        '''
        print('----- {} -----'.format(str(datetime.now())))
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

    def isOrder(self, message):
        """
        **説明**

        引数で渡されたメッセージが orderトピックかどうか判定する。

        **引数**

        *message* - メッセージデータ

        **戻り値**

        真偽値
        """
        return Client.TOPIC_ORDER in message.topic
    
    def isStatus(self, message):
        """
        **説明**

        引数で渡されたメッセージが statusトピックかどうか判定する。

        **引数**

        *message* - メッセージデータ

        **戻り値**

        真偽値
        """
        return Client.TOPIC_STATUS in message.topic
    
    def isReport(self, message):
        """
        **説明**

        引数で渡されたメッセージが reportトピックかどうか判定する。

        **引数**

        *message* - メッセージデータ

        **戻り値**

        真偽値
        """
        return Client.TOPIC_REPORT in message.topic

    def disconnect(self):
        """
        **説明**

        ブローカとの接続を解除する。

        **引数**

        なし

        **戻り値**

        なし
        """
        self.client.disconnect()
        #print('disconnected')
    

class ShadowHandler:
    """
    AWS IoT Core シャドウハンドラをラップしたクラス。
    """
    def __init__(self, client, shadow_name=None, isPersistentSubscribe=True):
        """
        ** 説明 **

        シャドウハンドラを生成し、インスタンス変数へ格納する。

        **引数**
            *client* - aws.broker.Client オブジェクト。
            
            *shadow_name* - シャドウ名、非設定時はclient idを使用する。

            *isPrtsistentSubscribe* - 応答があるときに、シャドウ応答（承認/拒否）トピックの購読を
            中止するかどうか。シャドウ要求が最初に行われたときに購読し、
            isPersistentSubscribeが設定されている場合は購読を中止しない。
            非設定時は、True。
        
        **戻り値**

            AWS IoT Core シャドウハンドラをラップしたオブジェクト。
        """
        self.shadow_name = shadow_name
        if shadow_name is None and client is not None:
            self.shadow_name = client.client_id

        self.shadow_client = AWSIoTMQTTShadowClient(client.client_id, 
            useWebsocket=client.use_websocket, awsIoTMQTTClient=client.client)
        self.shadow_handler = \
        self.shadow_client.createShadowHandlerWithName(self.shadow_name, isPersistentSubscribe)
        print('shadow handler created')

    def generalCallback(self, client, userdata, message):
        """
        **説明**
        
        一般的な、コールバック関数。

        **引数**

        *client* - AWS IoT クライアント

        *userdata* - ユーザデータ

        *message* - 受信メッセージ

        **戻り値**

        なし。
        """
        self.shadow_handler.generalCallback(client, userdata, message)

    def shadowGet(self, srcCallback, srcTimeout):
        """
        **説明**
        
        空のJSONドキュメントを対応するシャドウトピックに公開することによって、
        AWS IoTからデバイスシャドウJSONドキュメントを取得する。
        シャドウレスポンストピックは、get操作の結果に関してAWS IoTからのレスポンスを
        受け取るように登録される。
        取得したshadow JSONドキュメントは、
        登録済みのコールバックで利用可能になる。
        指定されたタイムアウト時間内に応答がない場合、
        タイムアウト通知が登録済みコールバックに渡される。

        **文法**

        .. code:: python

          # タイムアウトを5秒に設定して、AWS IoTからshadow JSONドキュメントを取得
          BotShadow.shadowGet(customCallback, 5)

        **引数**

        *srcCallback* - このシャドウリクエストに対するレスポンスが戻ってきたときに呼ばれる関数。 
        :code:`customCallback(payload, responseStatus, token)` において、
        :code:`payload` は戻ってきたJSONドキュメントを、 
        :code:`responseStatus` はリクエストがacceptされたか reject されたか デルタドキュメントかを、
        :code:`token` はこのリクエストのトラッキングのために使用されるトークンをそれぞれあらわす。

        *srcTimeout* - 要求が無効かどうかを判断するためのタイムアウト。
        リクエストがタイムアウトになると、タイムアウト通知が生成され、
        ユーザに通知するために登録済みのコールバックに渡される。

        **戻り値**

        このシャドウ要求でトレースに使用されるトークン。
        """
        return self.shadow_handler.shadowGet(srcCallback, srcTimeout)


    def shadowDelete(self, srcCallback, srcTimeout):
        """
        **説明**

        空のJSONドキュメントを対応するシャドウトピックに公開することによって、
        AWS IoTからデバイスシャドウを削除する。
        シャドウレスポンストピックは、get操作の結果に関してAWS IoTからの
        レスポンスを受け取るように登録される。
        応答は登録されたコールバックで利用可能になる。
        指定されたタイムアウト時間内に応答がない場合、
        タイムアウト通知が登録済みコールバックに渡される。

        **文法**

        .. code:: python

          # タイムアウトを5秒に設定して、AWS IoTからデバイスシャドウを削除
          BotShadow.shadowDelete(customCallback, 5)

        **引数**

        *srcCallback* - このシャドウリクエストに対するレスポンスが戻ってきたときに呼ばれる関数。
        :code:`customCallback(payload, responseStatus, token)` において、
        :code:`payload` は戻ってきたJSONドキュメントを、 
        :code:`responseStatus` はリクエストがacceptされたか reject されたか デルタドキュメントかを、
        :code:`token` はこのリクエストのトラッキングのために使用されるトークンをそれぞれあらわす。

        *srcTimeout* - 要求が無効かどうかを判断するためのタイムアウト。
        リクエストがタイムアウトになると、タイムアウト通知が生成され、
        ユーザに通知するために登録済みのコールバックに渡される。

        **戻り値**

        このシャドウ要求でトレースに使用されるトークン。

        """
        self.shadow_handler.shadowDelete(srcCallback, srcTimeout)
    
    def shadowUpdate(self, srcJSONPayload, srcCallback, srcTimeout):
        """
        **説明**

        提供されたJSONドキュメントを対応するシャドウトピックに公開することによって、
        AWS IoTからデバイスシャドウJSONドキュメント文字列を更新する。
        シャドウレスポンストピックは、get操作の結果に関してAWS IoTからのレスポンスを
        受け取るように登録される。
        応答は登録されたコールバックで利用可能になる。
        指定されたタイムアウト時間内に応答がない場合、
        タイムアウト通知が登録済みコールバックに渡される。

        **文法**

        .. code:: python

          # タイムアウトを5秒に設定して、AWS IoTからshadow JSONドキュメントを更新
          BotShadow.shadowUpdate(newShadowJSONDocumentString, customCallback, 5)

        **引数**

        *srcJSONPayload* - JSON document string used to update shadow JSON document in AWS IoT.

        *srcCallback* - このシャドウリクエストに対するレスポンスが戻ってきたときに呼ばれる関数。
        :code:`customCallback(payload, responseStatus, token)` において、
        :code:`payload` は戻ってきたJSONドキュメントを、 
        :code:`responseStatus` はリクエストがacceptされたか reject されたか デルタドキュメントかを、
        :code:`token` はこのリクエストのトラッキングのために使用されるトークンをそれぞれあらわす。

        *srcTimeout* - 要求が無効かどうかを判断するためのタイムアウト。
        リクエストがタイムアウトになると、タイムアウト通知が生成され、
        ユーザに通知するために登録済みのコールバックに渡される。

        **戻り値**

        このシャドウ要求でトレースに使用されるトークン。

        """
        return self.shadow_handler.shadowUpdate(srcJSONPayload, srcCallback, srcTimeout)
    
    def shadowRegisterDeltaCallback(self, srcCallback):
        """
        **説明**

        デルタトピックを購読することにより、このデバイスシャドウのデルタトピックをListenする。
        要求された状態と報告された状態の間に違いがあるときはいつでも、
        登録されたコールバックが呼びだされ、デルタペイロードはコールバックで利用可能となる。

        **文法**

        .. code:: python

          # BotShadowのデルタトピックをListen
          BotShadow.shadowRegisterDeltaCallback(customCallback)

        **引数**

        *srcCallback* - このシャドウリクエストに対するレスポンスが戻ってきたときに呼び出される関数。 
        :code:`customCallback(payload, responseStatus, token)` において、
        :code:`payload` は戻ってきたJSONドキュメントを、 
        :code:`responseStatus` はリクエストがacceptされたか reject されたか デルタドキュメントかを、
        :code:`token` はこのリクエストのトラッキングのために使用されるトークンをそれぞれあらわす。

        **戻り値**

        なし。

        """
        self.shadow_handler.shadowRegisterDeltaCallback(srcCallback)
    
    def shadowUnregisterDeltaCallback(self):
        """
        **説明**

        デルタトピックの購読を中止して、このデバイスシャドウのデルタトピックの
        受信をキャンセルする。
        望ましい状態と報告された状態の間に違いがあっても、
        このAPI呼び出しの後に受信されたデルタメッセージは存在しない。

        **文法**

        .. code:: python

          # BotShadowのデルタトピックのListenを中止する
          BotShadow.shadowUnregisterDeltaCallback()

        **引数**

        なし。

        **戻り値**

        なし。

        """
        self.shadow_handler.shadowUnregisterDeltaCallback()

def arr_to_bytearray(arr):
    """
    **説明**

    np.array(uint8, (120,160,3))オブジェクトをbytearrayオブジェクトに
    変換する。

    **引数**

    *arr* - np.array(uint8, (120,160,3))オブジェクト

    **戻り値**

    bytearray化されたオブジェクト
    """
    return bytearray(_arr_to_bin(arr))

def bytearray_to_arr(bytearray_data):
    """
    **説明**

    bytearrayオブジェクトをnp.array(uint8, (120,160,3))オブジェクトに
    変換する。

    **引数**

    *bytearray_data* - bytearray化されたオブジェクト

    **戻り値**

    np.array(uint8, (120,160,3))オブジェクト
    """
    return _bin_to_arr(bytes(bytearray_data))

def _arr_to_bin(arr):
    """
    **説明**
    
    イメージデータimage_arrayがnd.array型の場合、バイナリに変換する。
    
    **引数**
    
    *arr* - イメージデータ
    
    **戻り値**

    *bin* - バイナリ変換後のイメージデータ
    """
    if type(arr) is np.ndarray:
        return dk.util.img.arr_to_binary(arr)
    elif type(arr) is bytes:
        return arr
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
        return dk.util.img.img_to_arr(dk.util.img.binary_to_img(binary))
    else:
        raise ValueError('unknown type=' +str(type(binary)))