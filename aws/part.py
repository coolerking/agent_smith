# -*- coding: utf-8 -*-

import json
import random
import numpy as np
import donkeycar as dk
import array
from time import sleep
from datetime import datetime
from aws.broker import Config, Client, ShadowHandler, bytearray_to_arr

class PubImageArray:
    def __init__(self, client, interval=0.05, force_disconnect=False):
        self.client = client
        self.interval = 0.05
        self.force_disconnect = force_disconnect
        self.can_loop = True
        self.image_array = None

    def run(self, image_array):
        self.image_array = image_array
        self.update_loop()

    def run_threaded(self, image_array):
        self.image_array = image_array

    def update(self):
        """
        マルチスレッド内で実行される。
        self.can_loopが真である間、self.interval秒間隔でself.update_loop()を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.can_loop:
            self.update_loop()
            sleep(self.interval)

    def update_loop(self):
        if self.image_array is not None:
            #ret = self.client.publish(msg=self.image_array, qos=0)
            ret = self.client.publish_status(self.image_array)
        #print('published ret={}'.format(str(ret)))

    def shutdown(self):
        self.image_array = None
        self.can_loop = False
        if self.force_disconnect:
            sleep(self.interval)
            self.client.disconnect()


class SubImageArray:
    def __init__(self, client, force_disconnect=False):
        self.image_array = None
        self.client = client
        self.force_disconnect = force_disconnect
        ret = self.client.subscribe(qos=0, callback=self.sub_callback)
        #print('start subscribing: {}'.format(str(ret)))

    def run(self):
        return self.image_array

    def sub_callback(self, client, userdata, message):
        if message.topic.endswith(Config.TYPE_IMAGE_ARRAY):
            #print('subscribed {}'.format(message.topic))
            self.image_array = bytearray_to_arr(message.payload)

    def shutdown(self):
        if self.force_disconnect:
            self.client.disconnect()
        self.image_array = None
        #print('disconnected')

class PubSubImageArray:
    def __init__(self, client, interval=0.05, force_disconnect=True):
        self.client = client
        self.interval = interval
        self.force_disconnect = force_disconnect
        self.can_loop = True
        self.pub_image_array = None
        self.sub_image_array = None
        self.client.subscribe(qos=0, callback=self.sub_callback)
        #print('start subscribing')

    def update(self):
        """
        マルチスレッド内で実行される。
        self.can_loopが真である間、self.interval秒間隔でself.update_loop()を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.can_loop:
            self.update_loop()
            sleep(self.interval)

    def update_loop(self):
        if self.pub_image_array is not None:
            ret = self.client.publish(msg=self.pub_image_array, qos=0)
            #print('published ret={}'.format(str(ret)))
    
    def sub_callback(self, client, userdata, message):
        if message.topic.endswith(Config.TYPE_IMAGE_ARRAY):
            #print('subscribed {}'.format(message.topic))
            self.sub_image_array = bytearray_to_arr(message.payload)

    def run(self, image_array):
        self.run_threaded(image_array)
        self.update_loop()
        return self.sub_image_array

    def run_threaded(self, image_array):
        self.pub_image_array = image_array
        return self.sub_image_array

    def shutdown(self):
        self.pub_image_array = None
        if self.force_disconnect:
            sleep(self.interval)
            self.client.disconnect()
        self.sub_image_array = None

class PubData:
    def __init__(self, client, interval=0.05, force_disconnect=False):
        self.client = client
        self.interval = interval
        self.force_disconnect = force_disconnect
        self.can_loop = True
        self._init()

    def _init(self):
        self.image_array = None
        self.user_mode = 'user'
        self.user_left_value = 0
        self.user_left_status = 'free'
        self.user_right_value = 0
        self.user_right_status = 'free'
        self.user_lift_value = 0
        self.user_lift_status = 'free' 
        self.local_left_value = 0
        self.local_left_status = 'free'
        self.local_right_value = 0
        self.local_right_status = 'free'
        self.local_lift_value = 0
        self.local_lift_status = 'free'
        self.pilot_left_value = 0
        self.pilot_left_status = 'free'
        self.pilot_right_value = 0
        self.pilot_right_status = 'free'
        self.pilot_lift_value = 0
        self.pilot_lift_status = 'free'
        self.range_cms = 0
        self.force_volts = 0
        self.bend_volts = 0  
        self.recording = False
        self.timestamp = str(datetime.now())
    
    def _eval_init_tub(self):
        if self.user_mode == 'user' and \
            self.user_left_value == 0 and \
            self.user_left_status == 'free' and \
            self.user_right_value == 0 and \
            self.user_right_status == 'free' and \
            self.user_lift_value == 0 and \
            self.user_lift_status == 'free' and \
            self.local_left_value == 0 and \
            self.local_left_status == 'free' and \
            self.local_right_value == 0 and \
            self.local_right_status == 'free' and \
            self.local_lift_value == 0 and \
            self.local_lift_status == 'free' and \
            self.pilot_left_value == 0 and \
            self.pilot_left_status == 'free' and \
            self.pilot_right_value == 0 and \
            self.pilot_right_status == 'free' and \
            self.pilot_lift_value == 0 and \
            self.pilot_lift_status == 'free' and \
            self.range_cms == 0 and \
            self.force_volts == 0 and \
            self.bend_volts == 0 and \
            self.recording == False:
            return True
        return False

    def _eval_init_image(self):
        return self.image_array is None

    def update(self):
        """
        マルチスレッド内で実行される。
        self.can_loopが真である間、self.interval秒間隔でself.update_loop()を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.can_loop:
            self.update_loop()
            sleep(self.interval)

    def update_loop(self):
        print('update_loop() image: {}'.format(self._eval_init_image()==False ))
        if self._eval_init_image() == False:
            #ret = self.client.publish(msg=self.image_array, qos=0)
            ret = self.client.publish_status(self.image_array)
            print('published image ret={}'.format(str(ret)))
        print('update_loop() tub: {}'.format(self._eval_init_tub()==False))
        if self._eval_init_tub() == False:
            message = {
                "user/mode": self.user_mode,
                "user/left/value": self.user_left_value,
                "user/left/status": self.user_left_status,
                "user/right/value": self.user_right_value,
                "user/right/status": self.user_right_status,
                "user/lift/value": self.user_lift_value,
                "user/lift/status": self.user_lift_status,
                "local/left/value": self.local_left_value,
                "local/left/status": self.local_left_status,
                "local/right/value": self.local_right_value,
                "local/right/status": self.local_right_status,
                "local/lift/value": self.local_lift_value,
                "local/lift/status": self.local_lift_status,
                "pilot/left/value": self.pilot_left_value,
                "pilot/left/status": self.pilot_left_status,
                "pilot/right/value": self.pilot_right_value,
                "pilot/right/status": self.pilot_right_status,
                "pilot/lift/value": self.pilot_lift_value,
                "pilot/lift/status": self.pilot_lift_status,
                "range/cms": self.range_cms,
                "force/volts": self.force_volts,
                "bend/volts": self.bend_volts, 
                "recording": self.recording,
                "timestamp": self.timestamp
            }
            print(self.pilot_left_value)
            print(self.pilot_right_value)
            print(self.pilot_lift_value)
            #ret = self.client.publish(msg=message, qos=0)
            ret = self.client.publish_status(message)
            print('published tub ret={}'.format(str(ret)))

    def run_threaded(self, image_array, user_mode,
        user_left_value, user_left_status, user_right_value, user_right_status, user_lift_value, user_lift_status, 
        local_left_value, local_left_status, local_right_value, local_right_status, local_lift_value, local_lift_status,
        pilot_left_value, pilot_left_status, pilot_right_value, pilot_right_status, pilot_lift_value, pilot_lift_status,
        range_cms, force_volts, bend_volts,   
        recording, timestamp):
        """
        マルチスレッドの場合のrunメソッド。
        引数で与えられたデータを送信可能な辞書に変換し、
        インスタンス変数へ格納する。
        引数
            image_array             イメージデータ:カメラ入力データ
            user_mode               運転モード(user,local):手動入力値
            user_left_value         左モータ値:手動入力値
            user_left_status        左モータステータス:手動入力値
            user_right_value        右モータ値:手動入力値
            user_right_status       右モータステータス:手動入力値
            user_lift_value         リフトモータ値:手動入力値
            user_lift_status        リフトモータステータス:手動入力値
            local_left_value        左モータ値:オートパイロット入力値
            local_left_status       左モータステータス:オートパイロット入力値
            local_right_value       右モータ値:オートパイロット入力値
            local_right_status      右モータステータス:オートパイロット入力値
            local_lift_value        リフトモータ値:オートパイロット入力値
            local_lift_status       リフトモータステータス:オートパイロット入力値
            pilot_left_value        左モータ値:パワーユニットが採用した入力値
            pilot_left_status       左モータステータス:パワーユニットが採用した入力値
            pilot_right_value       右モータ値:パワーユニットが採用した入力値
            pilot_right_status      右モータステータス:パワーユニットが採用した入力値
            pilot_lift_value        リフトモータ値:パワーユニットが採用した入力値
            pilot_lift_status       リフトモータステータス:パワーユニットが採用した入力値
            range_cms               前方距離 (cm):センサ計測値
            force_volts             圧電センサ電圧:センサ計測値
            bend_volts              曲げセンサ電圧:センサ計測値
            recording               記録モード真偽値:手動入力値
            timestamp               タイムスタンプ
        戻り値
            なし
        """
        if image_array is not None:
            self.image_array = image_array
        
        # データ未投入時は初期値で代替
        to_mode = lambda m: 'user' if m not in ['user', 'local'] else m
        to_value = lambda v: 0 if v is None else v
        to_status = lambda s: 'free' if s not in ['move', 'free', 'brake'] else s
        to_timestamp = lambda t: str(datetime.now()) if t is None else t
        to_recording = lambda r: False if r is None else r

        self.user_mode = to_mode(user_mode)
        self.user_left_value = to_value(user_left_value)
        self.user_left_status = to_status(user_left_status)
        self.user_right_value = to_value(user_right_value)
        self.user_right_status = to_status(user_right_status)
        self.user_lift_value = to_value(user_lift_value)
        self.user_lift_status = to_status(user_lift_status)
        self.local_left_value = to_value(local_left_value)
        self.local_left_status = to_status(local_left_status)
        self.local_right_value = to_value(local_right_value)
        self.local_right_status = to_status(local_right_status)
        self.local_lift_value = to_value(local_lift_value)
        self.local_lift_status = to_status(local_lift_status)
        self.pilot_left_value = to_value(pilot_left_value)
        self.pilot_left_status = to_status(pilot_left_status)
        self.pilot_right_value = to_value(pilot_right_value)
        self.pilot_right_status = to_status(pilot_right_status)
        self.pilot_lift_value = to_value(pilot_lift_value)
        self.pilot_lift_status = to_status(pilot_lift_status)
        self.range_cms = to_value(range_cms)
        self.force_volts = to_value(force_volts)
        self.bend_volts = to_value(bend_volts)
        self.recording = to_recording(recording)
        self.timestamp = to_timestamp(timestamp)


    def run(self, image_array, user_mode,
        user_left_value, user_left_status, user_right_value, user_right_status, user_lift_value, user_lift_status, 
        local_left_value, local_left_status, local_right_value, local_right_status, local_lift_value, local_lift_status,
        pilot_left_value, pilot_left_status, pilot_right_value, pilot_right_status, pilot_lift_value, pilot_lift_status,
        range_cms, force_volts, bend_volts,   
        recording, timestamp):
        """
        非マルチスレッドの場合のrunメソッド。
        引数で与えられたデータをインスタンス変数へ格納する。
        その後、データをpubishする。

        引数
            image_array             イメージデータ:カメラ入力データ
            user_mode               運転モード(user,local):手動入力値
            user_left_value         左モータ値:手動入力値
            user_left_status        左モータステータス:手動入力値
            user_right_value        右モータ値:手動入力値
            user_right_status       右モータステータス:手動入力値
            user_lift_value         リフトモータ値:手動入力値
            user_lift_status        リフトモータステータス:手動入力値
            local_left_value        左モータ値:オートパイロット入力値
            local_left_status       左モータステータス:オートパイロット入力値
            local_right_value       右モータ値:オートパイロット入力値
            local_right_status      右モータステータス:オートパイロット入力値
            local_lift_value        リフトモータ値:オートパイロット入力値
            local_lift_status       リフトモータステータス:オートパイロット入力値
            pilot_left_value        左モータ値:パワーユニットが採用した入力値
            pilot_left_status       左モータステータス:パワーユニットが採用した入力値
            pilot_right_value       右モータ値:パワーユニットが採用した入力値
            pilot_right_status      右モータステータス:パワーユニットが採用した入力値
            pilot_lift_value        リフトモータ値:パワーユニットが採用した入力値
            pilot_lift_status       リフトモータステータス:パワーユニットが採用した入力値
            range_cms               前方距離 (cm):センサ計測値
            force_volts             圧電センサ電圧:センサ計測値
            bend_volts              曲げセンサ電圧:センサ計測値
            recording               記録モード真偽値:手動入力値
            timestamp               タイムスタンプ
        戻り値
            なし
        """
        self.run_threaded(image_array, user_mode,
        user_left_value, user_left_status, user_right_value, user_right_status, user_lift_value, user_lift_status, 
        local_left_value, local_left_status, local_right_value, local_right_status, local_lift_value, local_lift_status,
        pilot_left_value, pilot_left_status, pilot_right_value, pilot_right_status, pilot_lift_value, pilot_lift_status,
        range_cms, force_volts, bend_volts,   
        recording, timestamp)
        self.update_loop()

    
    def shutdown(self):
        self.can_loop = False
        self._init()
        if self.force_disconnect:
            sleep(self.interval)
            self.client.disconnect()



class SubPilotData:
    def __init__(self, client, force_disconnect=False):
        self._init()
        self.client = client
        self.force_disconnect = force_disconnect
        ret = self.client.subscribe(qos=0, callback=self.sub_callback)
        print('start subscribing: {}'.format(str(ret)))

    def run(self):
        return self.left_value, self.left_status, \
            self.right_value, self.right_status, \
            self.lift_value, self.lift_status
    
    def shutdown(self):
        if self.force_disconnect:
            self.client.disconnect()
        self._init()

    def sub_callback(self, client, userdata, message):
        if message.topic.endswith(Config.TYPE_JSON):
            msg = json.loads(message.payload)
            #print(msg)
            self.left_value = float(msg.get('pilot/left/value', self.left_value))
            self.left_status = msg.get('pilot/left/status', self.left_status)
            self.right_value = float(msg.get('pilot/right/value', self.right_value))
            self.right_status = msg.get('pilot/right/status', self.right_status)
            self.lift_value = float(msg.get('pilot/lift/value', self.lift_value))
            self.lift_status = msg.get('pilot/lift/status', self.lift_status)
            print('subscribed json {}'.format(message.topic))

    def _init(self):
        """
        インスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.left_value = 0
        self.left_status = 'free'
        self.right_value = 0
        self.right_status = 'free'
        self.lift_value = 0
        self.lift_status = 'free'
    


class AutoPilot:
    def __init__(self, client, interval=0.05, force_disconnect=False, debug=False):
        self.client = client
        self.interval = interval
        self.force_disconnect = force_disconnect
        self.debug = debug
        self.can_loop = True
        self._init()
        ret = self.client.subscribe(qos=0, callback=self.sub_callback)
        print('start subscribing: {}'.format(str(ret)))

    def update(self):
        """
        マルチスレッド内で実行される。
        self.can_loopが真である間、self.interval秒間隔でself.update_loop()を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.can_loop:
            self.update_loop()
            sleep(self.interval)

    def update_loop(self):
        if self._eval_init_image() == False:
            #ret = self.client.publish(msg=self.image_array, qos=0)
            ret = self.client.publish_status(self.image_array)
            print('published image ret={}'.format(str(ret)))

    def run(self, image_array):
        self.image_array = image_array
        self.update_loop()
        return self.run_threaded(image_array)

    def run_threaded(self, image_array):
        self.image_array = image_array
        if self.debug:
            self._debug()
            print('use debug data (random)')
        return self.left_value, self.left_status, \
            self.right_value, self.right_status, \
            self.lift_value, self.lift_status
    
    def shutdown(self):
        self.can_loop = False
        if self.force_disconnect:
            sleep(self.interval)
            self.client.disconnect()
        self._init()

    def sub_callback(self, client, userdata, message):
        print('subscribed topic: {}'.format(message.topic))
        if message.topic.endswith(Config.TYPE_JSON):
            msg = json.loads(message.payload)
            self.left_value = float(msg.get('local/left/value', self.left_value))
            self.left_status = msg.get('local/left/status', self.left_status)
            self.right_value = float(msg.get('local/right/value', self.right_value))
            self.right_status = msg.get('local/right/status', self.right_status)
            self.lift_value = float(msg.get('local/lift/value', self.lift_value))
            self.lift_status = msg.get('local/lift/status', self.lift_status)

    def _init(self):
        """
        インスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.image_array = None
        self.left_value = 0
        self.left_status = 'free'
        self.right_value = 0
        self.right_status = 'free'
        self.lift_value = 0
        self.lift_status = 'free'



    def _eval_init_pilot(self):
        if self.left_value == 0 and \
            self.left_status == 'free' and \
            self.right_value == 0 and \
            self.right_status == 'free' and \
            self.lift_value == 0 and \
            self.lift_status == 'free':
            return True
        return False

    def _eval_init_image(self):
        return self.image_array is None

    def _debug(self):
        self.left_value = self._get_value()
        self.right_value = self._get_value()
        self.lift_value = self._get_value()
        self.left_status = self._get_status()
        self.right_status = self._get_status()
        self.lift_status = self._get_status()

    def _get_value(self):
        return random.uniform(1.0, -1.0)

    def _get_status(self):
        all_status = ['free', 'move', 'brake']
        return all_status[random.randrange(len(all_status))]

class HedgeHogReporter:
    """
    IMU/USNavデータをデバイスシャドウへ書き込むパーツクラス。
    """
    def __init__(self, client, force_disconnect=False):
        """
        Shadowハンドラを生成する。

        引数：
            client              Clientオブジェクト
            force_disconnect    シャットダウン時disconnectを実行するかどうか
        戻り値：
            なし
        """
        self.client = client
        self.handler = ShadowHandler(client, shadow_name=client.client_id)
        self.force_disconnect = force_disconnect
    
    def run(self, x_usnav, y_usnav, z_usnav, x , y, z, qw, qx, qy, qz, vx, vy, vz, ax, ay, az):
        """
        IMU最新情報をデバイスシャドウへ書き込む。

        引数：
            x_usnav     X軸座標 (USNav)
            y_usnav     Y軸座標 (USNav)
            z_usnav     Z軸座標 (USNav)
            x           X軸座標 (IMU)
            y           Y軸座標 (IMU)
            z           Z軸座標 (IMU)
            qw          四元数(W) (IMU)
            qx          四元数(X) (IMU)
            qy          四元数(Y) (IMU)
            qz          四元数(Z) (IMU)
            vx          X軸速度 (IMU)
            vy          Y軸速度 (IMU)
            vz          Z軸速度 (IMU)
            ax          X軸加速度 (IMU)
            ay          Y軸加速度 (IMU)
            az          Z軸加速度 (IMU)
        戻り値：
            なし
        """
        self.message = {
            "state": {
                "reported": {
                    "usnav": {
                        "coordinate": {
                            "x": x_usnav,
                            "y": y_usnav,
                            "z": z_usnav
                        }
                    },
                    "imu": {
                        "coordinate": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "quaternion": {
                            "qw": qw,
                            "qx": qx,
                            "qy": qy,
                            "qz": qz
                        },
                        "velocity": {
                            "vx": vx,
                            "vy": vy,
                            "vz": vz
                        },
                        "acceleration": {
                            "ax": ax,
                            "ay": ay,
                            "az": az
                        }
                    }
                }
            }
        }
        self.handler.shadowUpdate(json.dumps(self.message), self.upd_callback, 5)
    
    def upd_callback(self, payload, responseStatus, token):
        """
        何もしない。

        引数：
            payload         ペイロード
            responseStatus  応答ステータス
            token           トークン
        """
        pass
    
    def shutdown(self):
        """
        self.force_disconnect が真の場合のみクライアントをdisconnectする。

        引数：
            なし
        戻り値：
            なし
        """
        if self.force_disconnect:
            self.client.disconnect()

class HedgeHogIMUReporter:
    """
    IMUデータをデバイスシャドウへ書き込むパーツクラス。
    """
    def __init__(self, client, force_disconnect=False):
        """
        Shadowハンドラを生成する。

        引数：
            client              Clientオブジェクト
            force_disconnect    シャットダウン時disconnectを実行するかどうか
        戻り値：
            なし
        """
        self.client = client
        self.handler = ShadowHandler(client, shadow_name=client.client_id)
        self.force_disconnect = force_disconnect
    
    def run(self, x , y, z, qw, qx, qy, qz, vx, vy, vz, ax, ay, az):
        """
        IMU最新情報をデバイスシャドウへ書き込む。

        引数：
            x           X軸座標 (IMU)
            y           Y軸座標 (IMU)
            z           Z軸座標 (IMU)
            qw          四元数(W) (IMU)
            qx          四元数(X) (IMU)
            qy          四元数(Y) (IMU)
            qz          四元数(Z) (IMU)
            vx          X軸速度 (IMU)
            vy          Y軸速度 (IMU)
            vz          Z軸速度 (IMU)
            ax          X軸加速度 (IMU)
            ay          Y軸加速度 (IMU)
            az          Z軸加速度 (IMU)
        戻り値：
            なし
        """
        self.message = {
            "state": {
                "reported": {
                    #"usnav": None,
                    "imu": {
                        "coordinate": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "quaternion": {
                            "qw": qw,
                            "qx": qx,
                            "qy": qy,
                            "qz": qz,
                        },
                        "velocity": {
                            "vx": vx,
                            "vy": vy,
                            "vz": vz
                        },
                        "acceleration": {
                            "ax": ax,
                            "ay": ay,
                            "az": az
                        }
                    }
                }
            }
        }
        self.handler.shadowUpdate(json.dumps(self.message), self.upd_callback, 5)
    
    def upd_callback(self, payload, responseStatus, token):
        """
        何もしない。

        引数：
            payload         ペイロード
            responseStatus  応答ステータス
            token           トークン
        """
        pass
    
    def shutdown(self):
        """
        self.force_disconnect が真の場合のみクライアントをdisconnectする。

        引数：
            なし
        戻り値：
            なし
        """
        if self.force_disconnect:
            self.client.disconnect()

class HedgeHogUSNavReporter:
    """
    IMUデータをデバイスシャドウへ書き込むパーツクラス。
    """
    def __init__(self, client, force_disconnect=False):
        """
        Shadowハンドラを生成する。

        引数：
            client              Clientオブジェクト
            force_disconnect    シャットダウン時disconnectを実行するかどうか
        戻り値：
            なし
        """
        self.client = client
        self.handler = ShadowHandler(client, shadow_name=client.client_id)
        self.force_disconnect = force_disconnect
    
    def run(self, x , y, z):
        """
        IMU最新情報をデバイスシャドウへ書き込む。

        引数：
            x           X軸座標 (USNav)
            y           Y軸座標 (USNav)
            z           Z軸座標 (USNav)
        戻り値：
            なし
        """
        self.message = {
            "state": {
                "reported": {
                    "usnav": {
                        "coordinate": {
                            "x": x,
                            "y": y,
                            "z": z
                        }
                    } #,
                    #"imu": None
                }
            }
        }
        self.handler.shadowUpdate(json.dumps(self.message), self.upd_callback, 5)
    
    def upd_callback(self, payload, responseStatus, token):
        """
        何もしない。

        引数：
            payload         ペイロード
            responseStatus  応答ステータス
            token           トークン
        """
        pass
    
    def shutdown(self):
        """
        self.force_disconnect が真の場合のみクライアントをdisconnectする。

        引数：
            なし
        戻り値：
            なし
        """
        if self.force_disconnect:
            self.client.disconnect()
