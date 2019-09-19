# -*- coding: utf-8 -*-
import os
import yaml
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class AWSConfig:

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
        conf = self._load_config(conf_path)[client_id]
        self.client_id = client_id
        self.endpoint = conf.get(AWSConfig.KEY_ENDPOINT, 'localhost')
        self.thing_type = conf.get(AWSConfig.KEY_THING_TYPE, None)
        self.thing_group = conf.get(AWSConfig.KEY_THING_GROUP, None)
        self.thing_name = conf.get(AWSConfig.KEY_THING_NAME, 'john_doe')
        self.use_websocket = conf.get(AWSConfig.KEY_USE_WEBSOCKET, False)
        if self.use_websocket:
            self.port = int(conf.get(AWSConfig.KEY_PORT, 443))
        else:
            self.port = int(conf.get(AWSConfig.KEY_PORT, 8883))
        self.system = conf.get(AWSConfig.KEY_SYSTEM, 'real')
        auth = conf.get(AWSConfig.KEY_AUTH, {})
        self.root_ca = auth[AWSConfig.KEY_ROOT_CA]
        self.certificate = auth[AWSConfig.KEY_CERTIFICATE]
        self.private_key = auth[AWSConfig.KEY_PRIVATE_KEY]

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
            conf = yaml.load(f, Loader=yaml.BaseLoader)
        return conf

class AWSShadowClientFactory(AWSConfig):


    def __init__(self, conf_path, client_id):
        super().__init__(conf_path, client_id)
        self._shadow_handler = None
        self._shadow_client = None

    def get_shadow_handler(self):
        if self._shadow_handler is None:
            self._shadow_handler = self._get_shadow_client().createShadowHandlerWithName(
                self.thing_name, True)
        return self._shadow_handler

    def get_mqtt_client(self):
        return self._get_shadow_client().getMQTTConnection() #.get_mqtt_connection()

    def _get_shadow_client(self):
        if self._shadow_client is not None:
            return self._shadow_client
        if self.use_websocket:
            client = AWSIoTMQTTShadowClient(self.client_id, useWebsocket=True)
        else:
            client = AWSIoTMQTTShadowClient(self.client_id)
        client.configureEndpoint(self.endpoint, self.port)
        if self.use_websocket:
            client.configureCredentials(self.root_ca)
        else:
            client.configureCredentials(self.root_ca, self.private_key, self.certificate)
        client.configureAutoReconnectBackoffTime(1, 32, 20)
        #client.configureOfflinePublishQueueing(-1)
        #client.configureDrainingFrequency(2)
        client.configureConnectDisconnectTimeout(10)
        client.configureMQTTOperationTimeout(5)
        client.clearLastWill()
        client.connect()
        self._shadow_client = client
        return self._shadow_client

    def configureLastWill(self, topic, payload):
        shadow_client = self._get_shadow_client()
        shadow_client.configureLastWill(topic, payload, 0)

    def disconnect(self):
        if self._shadow_client is not None:
            self._shadow_client.disconnect()
        self._shadow_handler = None
        self._shadow_client = None
