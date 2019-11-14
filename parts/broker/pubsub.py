# -*- coding: utf-8 -*-
"""
Publisher/SubscriberモデルでAWS IoT Coreと通信を行うパーツクラス群モジュール。
"""
import json
from .util import arr_to_bytearray, bytearray_to_arr, create_json_topic, create_image_topic, create_hedge_topic, get_thing_name_from_hedge_topic

class PublisherBase:
    """
    Tubデータ(イメージ、JSONデータ)をMQTTプロトコルで送信する
    パブリッシャパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, debug=False):
        """
        フィールドを初期化する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.system = aws_iot_client_factory.system
        self.thing_type = aws_iot_client_factory.thing_type
        self.thing_group = aws_iot_client_factory.thing_group
        self.thing_name = aws_iot_client_factory.thing_name
        self._client = aws_iot_client_factory.get_mqtt_client()
        self.debug = debug
    

    
    def create_image_message(self, image_array):
        """
        Tubデータ(イメージデータ)をpublish送信するメッセージを取得する。
        引数：
            image_array         イメージデータ
        戻り値：
            メッセージ(bytearray)
        """
        return arr_to_bytearray(image_array)

    def shutdown(self):
        """
        実装なし。
        引数：
            なし
        戻り値：
            なし
        """
        self._client = None
        if self.debug:
            print('[Publisher] shutdown')

class TubPublisher(PublisherBase):
    """
    通常フォーマットのTubデータを送信するパーツクラス。
    IMUやHedgeなどのデータは送信されない。
    """
    def run(self, image_array,
    user_angle, user_throttle, user_lift_throttle,
    pilot_angle, pilot_throttle, pilot_lift_throttle,
    user_mode, timestamp):
        """
        Tubデータ(イメージ、JSONデータ)をpublish送信する。
        引数：
            image_array         イメージデータ
            user_angle          操舵角(手動運転)
            user_throttle       駆動値(手動運転)
            user_lift_throttle  リフト駆動値(手動運転)
            user_angle          操舵角(自動運転)
            user_throttle       駆動値(自動運転)
            user_lift_throttle  リフト駆動値(自動運転)
            user_mode           ユーザモード
            timestamp           タイムスタンプ
        戻り値：
            なし
        """
        json_topic = create_json_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'tub')
        json_message = self.create_json_message(user_angle, user_throttle, user_lift_throttle,
            pilot_angle, pilot_throttle, pilot_lift_throttle,
            user_mode, timestamp)
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[TubPublisher] published json  status: {}'.format(str(is_sent)))
        image_topic = create_image_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'tub')
        image_message = self.create_image_message(image_array)
        if self._client is not None:
            is_sent = self._client.publish(image_topic, image_message, 0)
            if self.debug:
                print('[TubPublisher] published image status: {}'.format(str(is_sent)))

    def create_json_message(self,
    user_angle, user_throttle, user_lift_throttle,
    pilot_angle, pilot_throttle, pilot_lift_throttle,
    user_mode, timestamp):
        """
        Tubデータ(JSONデータ)をpublish送信するためのメッセージを取得する。
        引数：
            user_angle          操舵角(手動運転)
            user_throttle       駆動値(手動運転)
            user_lift_throttle  リフト駆動値(手動運転)
            user_angle          操舵角(自動運転)
            user_throttle       駆動値(自動運転)
            user_lift_throttle  リフト駆動値(自動運転)
            user_mode           ユーザモード
            timestamp           タイムスタンプ
        戻り値：
            メッセージ文字列
        """
        v2f = lambda v: 0.0 if v is None else float(v)
        return json.dumps({
            'user/mode':            user_mode,
            'user/angle':           v2f(user_angle),
            'user/throttle':        v2f(user_throttle),
            'user/lift_throttle':   v2f(user_lift_throttle),
            'pilot/angle':          v2f(pilot_angle),
            'pilot/throttle':       v2f(pilot_throttle),
            'pilot/lift_throttle':  v2f(pilot_lift_throttle),
            'timestamp':            timestamp
        })

class ImagePublisher(PublisherBase):
    """
    cam/image_array のみpublishするパーツクラス。
    """
    def run(self, image_array):
        """
        Tubデータ(イメージ)をpublish送信する。
        引数：
            image_array         イメージデータ
        戻り値：
            なし
        """
        if image_array is None:
            if self.debug:
                print('[ImagePublisher] image_array is None(ignore publishing)')
            return
        image_topic = create_image_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'image')
        image_message = self.create_image_message(image_array)
        if self._client is not None:
            is_sent = self._client.publish(image_topic, image_message, 0)
            if self.debug:
                print('[ImagePublisher] published image status: {}'.format(str(is_sent)))


class HedgePublisher(PublisherBase):
    """
    Marvelmind モバイルルータ(IMU)データ(JSONデータ)をMQTTプロトコルで送信する
    パブリッシャパーツクラス。
    """
    def run(self,
    usnav_id, usnav_x, usnav_y, usnav_z, usnav_angle, usnav_timestamp,
    imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz,
    imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az,
    imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz,
    imu_timestamp,
    dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d,
    dist_b3, dist_b3d, dist_b4, dist_b4d, dist_timestamp,
    timestamp):
        """
        位置情報データ(JSONデータ)をpublish送信する。
        引数：
            usnav_id            デバイスID
            usnav_x             超音波計測：X座標
            usnav_y             超音波計測：Y座標
            usnav_z             超音波計測：Z座標
            usnav_angle         超音波計測：アングル
            usnav_timestamp     超音波計測したタイムスタンプ
            imu_x               IMU：X座標
            imu_y               IMU：Y座標
            imu_z               IMU：Z座標
            imu_qw              IMU：四元数(W)
            imu_qx              IMU：四元数(X)
            imu_qy              IMU：四元数(Y)
            imu_qz              IMU：四元数(Z)
            imu_vx              IMU：速度(X)
            imu_vy              IMU：速度(Y)
            imu_vz              IMU：速度(Z)
            imu_ax              IMU：加速度(X)
            imu_ay              IMU：加速度(Y)
            imu_az              IMU：加速度(Z)
            imu_gx              IMU：重力加速度(X)
            imu_gy              IMU：重力加速度(Y)
            imu_gz              IMU：重力加速度(Z)
            imu_mx              IMU：磁気速度(X)
            imu_my              IMU：磁気速度(Y)
            imu_mz              IMU：磁気速度(Z)
            imu_timestamp       IMU情報を計測したタイムスタンプ
            dist_id             距離：デバイスID
            dist_b1             距離：対象となるステーショナリビーコン1のデバイスID
            dist_b1d            距離：対象となるステーショナリビーコン1との距離
            dist_b2             距離：対象となるステーショナリビーコン2のデバイスID
            dist_b2d            距離：対象となるステーショナリビーコン2との距離
            dist_b3             距離：対象となるステーショナリビーコン3のデバイスID
            dist_b3d            距離：対象となるステーショナリビーコン3との距離
            dist_b4             距離：対象となるステーショナリビーコン4のデバイスID
            dist_b4d            距離：対象となるステーショナリビーコン4との距離
            dist_timestamp      距離：タイムスタンプ
            timestamp           Donkeycarタイムスタンプ
        戻り値：
            なし
        """
        json_topic = create_hedge_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'hedge')
        json_message = self.create_json_message(usnav_id, usnav_x, usnav_y, usnav_z,
            usnav_angle, usnav_timestamp,
            imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz,
            imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az,
            imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz,
            imu_timestamp,
            dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d,
            dist_b3, dist_b3d, dist_b4, dist_b4d, dist_timestamp,
            timestamp)
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[HedgePublisher] published json  status: {}'.format(str(is_sent)))

    def create_json_message(self,
    usnav_id, usnav_x, usnav_y, usnav_z, usnav_angle, usnav_timestamp,
    imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz,
    imu_vx, imu_vy, imu_vz, imu_ax, imu_ay, imu_az,
    imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz,
    imu_timestamp,
    dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d,
    dist_b3, dist_b3d, dist_b4, dist_b4d, dist_timestamp,
    timestamp):
        """
        位置情報データ(JSONデータ)をpublish送信するためのメッセージを取得する。
        引数：
            usnav_id            デバイスID
            usnav_x             超音波計測：X座標
            usnav_y             超音波計測：Y座標
            usnav_z             超音波計測：Z座標
            usnav_angle         超音波計測：アングル
            usnav_timestamp     超音波計測したタイムスタンプ
            imu_x               IMU：X座標
            imu_y               IMU：Y座標
            imu_z               IMU：Z座標
            imu_qw              IMU：四元数(W)
            imu_qx              IMU：四元数(X)
            imu_qy              IMU：四元数(Y)
            imu_qz              IMU：四元数(Z)
            imu_vx              IMU：速度(X)
            imu_vy              IMU：速度(Y)
            imu_vz              IMU：速度(Z)
            imu_ax              IMU：加速度(X)
            imu_ay              IMU：加速度(Y)
            imu_az              IMU：加速度(Z)
            imu_gx              IMU：重力加速度(X)
            imu_gy              IMU：重力加速度(Y)
            imu_gz              IMU：重力加速度(Z)
            imu_mx              IMU：磁気速度(X)
            imu_my              IMU：磁気速度(Y)
            imu_mz              IMU：磁気速度(Z)
            imu_timestamp       IMUデータを計測したタイムスタンプ
            dist_id             距離：デバイスID
            dist_b1             距離：対象となるステーショナリビーコン1のデバイスID
            dist_b1d            距離：対象となるステーショナリビーコン1との距離
            dist_b2             距離：対象となるステーショナリビーコン2のデバイスID
            dist_b2d            距離：対象となるステーショナリビーコン2との距離
            dist_b3             距離：対象となるステーショナリビーコン3のデバイスID
            dist_b3d            距離：対象となるステーショナリビーコン3との距離
            dist_b4             距離：対象となるステーショナリビーコン4のデバイスID
            dist_b4d            距離：対象となるステーショナリビーコン4との距離
            dist_timestamp      距離：タイムスタンプ
            timestamp           タイムスタンプ
        戻り値：
            メッセージ文字列
        """
        v2f = lambda v: 0.0 if v is None else float(v)
        return json.dumps({
            'usnav_id':             usnav_id,
            'usnav_x':              v2f(usnav_x),
            'usnav_y':              v2f(usnav_y),
            'usnav_z':              v2f(usnav_z),
            'usnav_angle':          v2f(usnav_angle),
            'usnav_timestamp':      usnav_timestamp,
            'imu_x':                v2f(imu_x),
            'imu_y':                v2f(imu_y),
            'imu_z':                v2f(imu_z),
            'imu_qw':               v2f(imu_qw),
            'imu_qx':               v2f(imu_qx),
            'imu_qy':               v2f(imu_qx),
            'imu_qz':               v2f(imu_qx),
            'imu_vx':               v2f(imu_vx),
            'imu_vy':               v2f(imu_vy),
            'imu_vz':               v2f(imu_vz),
            'imu_ax':               v2f(imu_ax),
            'imu_ay':               v2f(imu_ay),
            'imu_az':               v2f(imu_az),
            'imu_gx':               v2f(imu_gx),
            'imu_gy':               v2f(imu_gy),
            'imu_gz':               v2f(imu_gz),
            'imu_mx':               v2f(imu_mx),
            'imu_my':               v2f(imu_my),
            'imu_mz':               v2f(imu_mz),
            'imu_timestamp':        imu_timestamp,
            'dist_id':              dist_id,
            'dist_b1':              dist_b1,
            'dist_b1d':             v2f(dist_b1d),
            'dist_b2':              dist_b2,
            'dist_b2d':             v2f(dist_b2d),
            'dist_b3':              dist_b3,
            'dist_b3d':             v2f(dist_b3d),
            'dist_b4':              dist_b4,
            'dist_b4d':             v2f(dist_b4d),
            'dist_timestamp':       dist_timestamp,
            'timestamp':            timestamp
        })

class Mpu6050Publisher(PublisherBase):
    """
    MPU6050で取得したデータをPublishするパーツクラス。
    """
    model_type = 'mpu6050'
    def run(self, acl_x, acl_y, acl_z, gyr_x, gyr_y, gyr_z, 
    recent, timestamp):
        """
        MPU9250で取得したデータをPublishする。
        引数：
            acl_x       X軸加速度(float)
            acl_y       Y軸加速度(float)
            acl_z       Z軸加速度(float)
            gyr_x       X軸角速度(float)
            gyr_y       Y軸角速度(float)
            gyr_z       Z軸角速度(float)
            recent      過去数件の最新データ(str, json形式)
            timestamp   datetime.now()戻り値(float)
        戻り値：
            なし
        """
        json_topic = create_hedge_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, self.model_type)
        v2f = lambda v: 0.0 if v is None else float(v)
        json_message = json.dumps({
            'acl_x':                v2f(acl_x),
            'acl_y':                v2f(acl_y),
            'acl_z':                v2f(acl_z),
            'gyr_x':                v2f(gyr_x),
            'gyr_y':                v2f(gyr_y),
            'gyr_z':                v2f(gyr_z),
            'timestamp':            v2f(timestamp),
            'recent':               json.dumps(recent),
        })
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[{}Publisher] published json  status: {}'.format(
                    self.model_type, str(is_sent)))

class Mpu9250Publisher(PublisherBase):
    """
    MPU9250で取得したデータをPublishするパーツクラス。
    """
    model_type = 'mpu9250'
    def run(self, acl_x, acl_y, acl_z, gyr_x, gyr_y, gyr_z, 
    mgt_x, mgt_y, mgt_z, temp, recent, timestamp):
        """
        MPU9250で取得したデータをPublishする。
        引数：
            acl_x       X軸加速度(float)
            acl_y       Y軸加速度(float)
            acl_z       Z軸加速度(float)
            gyr_x       X軸角速度(float)
            gyr_y       Y軸角速度(float)
            gyr_z       Z軸角速度(float)
            mgt_x       X軸磁束密度(float)
            mgt_y       Y軸磁束密度(float)
            mgt_z       Z軸磁束密度(float)
            temp        セルシウス温度(float)
            recent      過去数件の最新データ(str, json形式)
            timestamp   datetime.now()戻り値(float)
        戻り値：
            なし
        """
        json_topic = create_hedge_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, self.model_type)
        v2f = lambda v: 0.0 if v is None else float(v)
        json_message = json.dumps({
            'acl_x':                v2f(acl_x),
            'acl_y':                v2f(acl_y),
            'acl_z':                v2f(acl_z),
            'gyr_x':                v2f(gyr_x),
            'gyr_y':                v2f(gyr_y),
            'gyr_z':                v2f(gyr_z),
            'mgt_x':                v2f(mgt_x),
            'mgt_y':                v2f(mgt_y),
            'mgt_z':                v2f(mgt_z),
            'temp':                 v2f(temp),
            'timestamp':            v2f(timestamp),
            'recent':               json.dumps(recent),
        })
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[{}Publisher] published json  status: {}'.format(
                    self.model_type, str(is_sent)))


class RangePublisher(PublisherBase):
    """
    前方距離センサデータを送信するPublisherパーツプラス
    """
    def run(self, range_cms, timestamp):
        """
        前方距離データ(イメージ、JSONデータ)をpublish送信する。
        引数：
            range_cms           前方距離(cm)
            timestamp           タイムスタンプ
        戻り値：
            なし
        """
        json_topic = create_json_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'range')
        json_message = self.create_json_message(range_cms, timestamp)
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[RangePublisher] published json  status: {}'.format(str(is_sent)))

    def create_json_message(self, range_cms, timestamp):
        """
        前方距離センサデータ(JSONデータ)をpublish送信するためのメッセージを取得する。
        引数：
            range_cms           前方距離(cm)
            timestamp           タイムスタンプ
        戻り値：
            メッセージ文字列
        """
        v2f = lambda v: 0.0 if v is None else float(v)
        return json.dumps({
            'range_cms':            v2f(range_cms),
            'timestamp':            timestamp
        })

class ADCPublisher(PublisherBase):
    """
    ADC経由で取得したセンサデータを送信するPublisherパーツプラス
    """
    def run(self, force_volts, bend_volts, timestamp):
        """
        ADCデータ(JSONデータ)をpublish送信する。
        引数：
            force_volts         圧力センサ(V)
            bend_volts          曲げセンサ(V)
            timestamp           タイムスタンプ
        戻り値：
            なし
        """
        json_topic = create_json_topic(self.system, self.thing_type,
        self.thing_group, self.thing_name, 'adc')
        json_message = self.create_json_message(force_volts, bend_volts, timestamp)
        if self._client is not None:
            is_sent = self._client.publish(json_topic, json_message, 0)
            if self.debug:
                print('[RangePublisher] published json  status: {}'.format(str(is_sent)))

    def create_json_message(self, force_volts, bend_volts, timestamp):
        """
        ADCデータ(JSONデータ)をpublish送信するためのメッセージを取得する。
        引数：
            force_volts         圧力センサ(V)
            bend_volts          曲げセンサ(V)
            timestamp           タイムスタンプ
        戻り値：
            メッセージ文字列
        """
        v2f = lambda v: 0.0 if v is None else float(v)
        return json.dumps({
            'force_volts':          v2f(force_volts),
            'bend_volts':           v2f(bend_volts),
            'timestamp':            timestamp
        })


class OrderSubscriber:
    """
    プランナから命令を受信するさぬスクライバパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, interval=5, callback=None, debug=False):
        """
        サブスクライブを開始する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            interval                インターバル（秒）
            callback                コールバック関数
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self._client = aws_iot_client_factory.get_mqtt_client()
        self.interval = interval
        self.order = None
        self.debug = debug
        self.topic = create_json_topic(aws_iot_client_factory.system,
            aws_iot_client_factory.thing_type,
            aws_iot_client_factory.thing_group,
            aws_iot_client_factory.thing_name,
            'order')
        self.callback = callback or self.subscribe_order_callback
        self._client.subscribe(self.topic, 0, self.callback)

    def subscribe_order_callback(self, client, userdata, message):
        """
        Subscribe時呼び出される。フィールドに命令を格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if self.debug:
            print('[OrderSubscriber] subscribed: {}'.format(str(message.payload)))
        self.order = message.payload #json.loads(message.payload)

    def run(self):
        """
        最新の命令を取得する。
        引数：
            なし
        戻り値：
            order       命令(辞書型)
        """
        return self.order

    def shutdown(self):
        """
        Unsubscribeしてフィールドを開放する。
        引数：
            なし
        戻り値：
            なし
        """
        self._client.unsubscribe(self.topic, 0)
        self.order = None
        self._client = None
        self.topic = None
        if self.debug:
            print('[OrderSubscriber] shutdown')

class HedgeSubscriber:
    """
    Marvelmind位置情報システムデータをsubscribeするパーツクラス。
    自分以外のloaderエージェント最新位置情報を取得する。
    """
    def __init__(self, aws_iot_client_factory, interval=5, callback=None, debug=False):
        """
        サブスクライブを開始する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            interval                インターバル（秒）
            callback                コールバック関数
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self._client = aws_iot_client_factory.get_mqtt_client()
        self.interval = interval
        self.hedge = {}
        self.debug = debug
        self.thing_name = aws_iot_client_factory.thing_name
        self.topic = create_hedge_topic(
            system=aws_iot_client_factory.system,
            thing_type=aws_iot_client_factory.thing_type,
            message_type='hedge')
        self.callback = callback or self.subscribe_hedge_callback
        self._client.subscribe(self.topic, 0, self.callback)
        if self.debug:
            print('[HedgeSubscriber] subscribe topic={}'.format(self.topic))

    def subscribe_hedge_callback(self, client, userdata, message):
        """
        Subscribe時呼び出される。フィールドに命令を格納する。
        引数：
            client          MQTTクライアントオブジェクト
            userdata        ユーザデータ
            message         メッセージ
        戻り値：
            なし
        """
        if self.debug:
            print('[HedgeSubscriber] subscribed: topic={} payload={}'.format(
                str(message.topic), str(message.payload)))
        thing_name = get_thing_name_from_hedge_topic(topic=str(message.topic))
        if thing_name is None:
            if self.debug:
                print('[HedgeSubscriber] topic has no thing_name')
        elif thing_name == self.thing_name:
            if self.debug:
                print('[HedgeSubscriber] ignore my data({})'.format(thing_name))
        elif message.payload is None:
            if self.debug:
                print('[HedgeSubscriber] no messsage.payload')
        elif isinstance(self.hedge, dict):
            import ast
            self.hedge[thing_name] = ast.literal_eval(message.payload.decode('utf-8'))
            #self.hedge[thing_name] = json.loads(message.payload)
        else:
            if self.debug:
                print('[HedgeSubscriber] unknown type self.hedge')

    def run(self):
        """
        コレまでに取得した他のモノの最新位置情報を返却する。
        引数：
            なし
        戻り値：
            hedge       文字列型（｛モノの名前：JSON文字列｝）
        """
        if self.debug:
            print('[HedgeSubscriber] run return {}'.format(str(self.hedge)))
        return str(self.hedge)

    def shutdown(self):
        """
        Unsubscribeしてフィールドを開放する。
        引数：
            なし
        戻り値：
            なし
        """
        self._client.unsubscribe(self.topic, 0)
        self.order = None
        self._client = None
        self.topic = None
        if self.debug:
            print('[HegdeSubscriber] shutdown')