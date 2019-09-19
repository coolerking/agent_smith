# -*- coding: utf-8 -*-
"""
シャドウを用いたパーツクラス群。
各クラスは、コンストラクタ引数として AWSIoTClientFactoryインスタンス を必要とする。
"""
import json
from time import sleep

class PowerReporter:
    """
    電源状態を報告するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, interval=5, debug=False):
        """
        シャドウハンドラをフィールドへ格納する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            interval                インターバル（秒）
            debug                   デバッグフラグ
        戻り値：
            なし
        """
        self.debug = debug
        if self.debug:
            print('[PowerReporter] __init__ called')
        self.shadow_handler = aws_iot_client_factory.get_shadow_handler()
        self.interval = interval
        self.on_returned = True # 電源ON更新処理実行中：偽、実行なし：真
        self.off_returned = True # 電源OFF更新処理実行中：偽、実行なし：真
        self.on() # 電源オンしたことを報告する

    def run(self, is_power_on=True):
        """
        電源状態を報告する。
        引数：
            is_power_on    電源状態(真：on、偽：off)
        戻り値：
            なし
        """
        if self.debug:
            print('[PowerReporter] run called is_power_on: {}'.format(str(is_power_on)))
        if is_power_on:
            self.shadow_handler.shadowUpdate(
                self.create_shadow_message('on'),
                self.on_callback, self.interval)
        else:
            self.shadow_handler.shadowUpdate(
                self.create_shadow_message('off'),
                self.off_callback, self.interval)

    def on(self):
        """
        電源ON状態となったことを報告する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[PowerReporter] on called is_on_returned:{}'.format(str(self.on_returned)))
            if not self.on_returned:
                print('[PowerReporter] wait for fininsh previous on-process')
        while not self.on_returned:
            sleep(0.1)
        if self.debug:
            print('[PowerReporter] finished previous on-process')
        
        self.on_returned = False
        self.run(is_power_on=True)
        while not self.on_returned:
            sleep(0.1)
        if self.debug:
            print('[PowerReporter] sent power-on status')

    def off(self):
        """
        電源OFF状態となったことを報告する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[PowerReporter] off called is_on_returned:{}'.format(str(self.off_returned)))
            if not self.off_returned:
                print('[PowerReporter] wait for fininsh previous off-process')
        while not self.off_returned:
            sleep(0.1)
        if self.debug:
            print('[PowerReporter] finished previous off-process')
        
        self.off_returned = False
        self.run(is_power_on=False)
        while not self.off_returned:
            sleep(0.1)
        if self.debug:
            print('[PowerReporter] sent power-off status')

    def shutdown(self):
        """
        電源OFFとなったことを報告し、シャドウオブジェクトを開放する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[PowerReporter] shutdown called')
        if self.debug and (not self.off_returned):
                print('[PowerReporter] wait for fininsh previous off-process')
        while not self.off_returned:
            sleep(0.1)
        if self.debug and (not self.on_returned):
                print('[PowerReporter] wait for fininsh previous on-process')
        while not self.on_returned:
            sleep(0.1)
        self.off()
        self.shadow_handler = None

    def create_shadow_message(self, power='off'):
        """
        ON/OFFメッセージを作成する。
        引数：
            power       'on','off'のどちらか
        戻り値：
            メッセージ文字列(JSON形式)
        """
        return json.dumps({
            'state': {
                'reported': {
                    'power': power
                }
            }
        })

    def on_callback(self, payload, responseStatus, token):
        """
        電源ON更新処理終了時よびだされるコールバック関数。
        処理なし。
        引数：
            payload         JSON文字列、json.loads(payload)で辞書化して使用する
            responseStatus  ステータス文字列('timeout', 'accepted', 'rejected'など)
            token           トークン文字列
        戻り値：
            なし
        """
        self.on_returned = True
        if self.debug:
            print('[PowerReporter] updated on responseStatus: {}'.format(str(responseStatus)))

    def off_callback(self, payload, responseStatus, token):
        """
        電源OFF更新処理終了時よびだされるコールバック関数。
        処理なし。
        引数：
            payload         JSON文字列、json.loads(payload)で辞書化して使用する
            responseStatus  ステータス文字列('timeout', 'accepted', 'rejected'など)
            token           トークン文字列
        戻り値：
            なし
        """
        self.off_returned = True
        if self.debug:
            print('[PowerReporter] updated off responseStatus: {}'.format(str(responseStatus)))

class StateReporter:
    """
    命令実行状態を報告するパーツクラス。
    """
    def __init__(self, aws_iot_client_factory, interval=5, debug=False):
        """
        シャドウハンドラをフィールドへ格納する。
        引数：
            aws_iot_client_factory  AWSIoTClientFactoryオブジェクト
            interval                インターバル（秒）
        戻り値：
            なし
        """
        if debug:
            print('[StateReporter] __init__ called')
        self.shadow_handler = aws_iot_client_factory.get_shadow_handler()
        self.interval = interval
        self.get_returned = True # 報告済み命令実行状態を取得する処理実行中：偽、実行済み/なし：真
        self.update_returned = True # 命令実行状態報告処理実行中：偽、実行済み/なし：真
        self._status = None # 現在の命令実行状態
        self.debug = debug
        self.update_status('wait') # 待機状態として報告する
        if debug:
            print('[StateReporter] status:{}'.format(str(self._status)))

    def run(self, order_state):
        """
        命令実行状態を報告する。
        引数：
            order_state     命令実行状態
        戻り値：
            なし
        """
        if self.debug:
            print('[StateReporter] run callsed order_state = {}'.format(str(order_state)))
        self.update_status(order_state)

    def wait(self):
        """
        待機状態を報告する
        """
        self.update_status('wait')

    def running(self):
        """
        実行中であることを報告する。
        引数：
            なし
        戻り値：
            命令実行状態をあらわす文字列
        """
        return self.update_status('running')

    def accident(self):
        """
        異常発生状態であることを報告する。
        引数：
            なし
        戻り値：
            命令実行状態をあらわす文字列
        """
        self.update_status('accident')

    def get_status(self):
        """
        最新の命令状態を取得する。
        引数：
            なし
        戻り値：
            命令実行状態をあらわす文字列
        """
        if self.debug:
            print('[StateReporter] get_status called')
            if not self.get_returned:
                print('[StateReporter] yet finished previous get-proccess')
        while not self.get_returned:
            sleep(self.interval)
        if self.debug:
            print('[StateReporter] finished previous get-process')
        self.get_returned = False
        self.shadow_handler.shadowGet(self.get_callback, 5)
        if self.debug:
            print('[StateReporter] sent shadow get')
        while not self.get_returned:
            sleep(self.interval)
        if self.debug:
            print('[StateReporter] get-process returned status:{}'.format(str(self._status)))
        return self._status

    def update_status(self, order_state='wait'):
        """
        命令状態を更新する。
        引数：
            order_state     命令状態をあらわす文字列
        戻り値：
            命令状態をあらわす文字列
        """
        if self.debug:
            print('[StateReporter] update_status called')
            if not self.update_returned:
                print('[StateReporter] yet finished previous update-proccess')
        while not self.update_returned:
            sleep(self.interval)
        if self.debug:
            print('[StateReporter] finished previous update-process')
        self.update_returned = False
        # シャドウ更新
        self.shadow_handler.shadowUpdate(
            self.create_shadow_message(order_state),
            self.update_callback, self.interval)
        if self.debug:
            print('[StateReporter] sent shadow update')
        while not self.update_returned:
            sleep(self.interval)
        if self.debug:
            print('[StateReporter] update-process returned status:{}'.format(str(self._status)))
        return self._status

    def create_shadow_message(self, status='wait'):
        """
        命令状態報告メッセージを作成する。
        引数：
            status     命令実行状態
        戻り値：
            メッセージ文字列(JSON形式)
        """
        return json.dumps({
            'state': {
                'reported': {
                    'order': status
                }
            }
        })
    
    def get_status_from_message(self, payload):
        """
        payload文字列から命令状態をあらわす文字列を取得する。
        引数：
            payload     メッセージ文字列
        戻り値：
            order_state 命令状態をあらわす文字列
        """
        if self.debug:
            print('[StateReporter] get_status_from_message called payload={}'.format(str(payload)))
        msg_dict = json.load(payload)
        state_dict = msg_dict.get('state', None)
        if state_dict is None:
            if self.debug:
                print('[StateReporter] no state value')
            return state_dict
        reported_dict = state_dict.get('reported', None)
        if reported_dict is None:
            if self.debug:
                print('[StateReporter] no reported value')
            return reported_dict
        order_value = reported_dict.get('order', None)
        if order_value is None:
            if self.debug:
                print('[StateReporter] no order value')
        return str(order_value)

    def shutdown(self):
        """
        シャットダウン時の処理を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[StateReporter] shutdown called')
            print('[StateReporter] get_returned = {}'.format(self.get_returned))
        while not self.get_returned:
            sleep(self.interval)
        if self.debug:
            print('[StateReporter] update_returned = {}'.format(self.update_returned))
        while not self.update_returned:
            sleep(self.interval)
        self._state = None
        self.shadow_handler = None


    def get_callback(self, payload, responseStatus, token):
        '''
        命令状態取得完了時よびだされるコールバック関数。
        処理なし。
        引数：
            payload         JSON文字列、json.loads(payload)で辞書化して使用する
            responseStatus  ステータス文字列('timeout', 'accepted', 'rejected'など)
            token           トークン文字列
        戻り値：
            なし
        '''
        if self.debug:
            print('[StateReporter] get_callback called responseStatus: {}'.format(str(responseStatus)))
        if responseStatus == 'accepted':
            if self.debug:
                print('[StateReporter] get_callback payload = {}'.format(str(payload)))
            self._status = self.get_status_from_message(payload)
            if self.debug:
                print('[StateReporter] get_callback status = {}'.format(str(self._status)))
        self.get_returned = True

    def update_callback(self, payload, responseStatus, token):
        '''
        命令状態報告完了時よびだされるコールバック関数。
        処理なし。
        引数：
            payload         JSON文字列、json.loads(payload)で辞書化して使用する
            responseStatus  ステータス文字列('timeout', 'accepted', 'rejected'など)
            token           トークン文字列
        戻り値：
            なし
        '''
        if self.debug:
            print('[StateReporter] update_callback called responseStatus: {}'.format(str(responseStatus)))
        if responseStatus == 'accepted':
            self._status = self.get_status_from_message(payload)
            if self.debug:
                print('[StateReporter] update_callback status = {}'.format(str(self._status)))
        self.update_returned = True
