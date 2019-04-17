# -*- coding: utf-8 -*-
"""
DRV8830(i2C接続)モータドライバを使用した場合のパワーユニットパーツクラス。

DRV8830は、I2C通信を使ってRaspberry Piと接続する仕様となっている。
"""
import pigpio
#from time import sleep
from .drv8830 import MotorDriver

# 運転モード値
BRAKE =     'brake'
FREE =      'free'

class PowerUnit:
    """
    DRV8830を用いたDCモータ3基を操作するためのパーツクラス。
    """
    def __init__(self, pi, i2c_motor_settings, epsilone=0.1):
        '''
        フォークリフトに接続された左モータ、右モータ、リフトモータを管理する
        DRV8830を操作可能な状態にする。
        引数：
            pi                      pigpioパッケージのpiオブジェクト
            i2c_motor_settings      各モータドライバのI2C設定（２次元配列）
            epsilone                0と認識する前後範囲
                                    (-epsilone～epsilone)が0と認識
        戻り値：
            なし
        '''
        self.pi = pi
        self.ep = epsilone
        self.left_motor = MotorDriver(
            pi, 
            i2c_motor_settings[0][0], 
            i2c_motor_settings[0][1], 
            i2c_motor_settings[0][2])
        self.right_motor = MotorDriver(
            pi, 
            i2c_motor_settings[1][0], 
            i2c_motor_settings[1][1], 
            i2c_motor_settings[1][2])
        self.lift_motor = MotorDriver(
            pi, 
            i2c_motor_settings[2][0], 
            i2c_motor_settings[2][1], 
            i2c_motor_settings[2][2])
        self.left_motor.free()
        self.right_motor.free()
        self.lift_motor.free()

    def update(self):
        pass

    def run(self, left_value, left_status, right_value, right_status, lift_value, lift_status):
        '''
        それぞれのモータに指示を出す。
        引数：
            left_value      左モータ動作レベル(-1.0～1.0)
            left_status     左モータステータス(move, free, brake)
            right_value     右モータ動作レベル(-1.0～1.0)
            right_status    右モータステータス(move, free, brake)
            lift_value      リフトモータ動作レベル(-1.0～1.0)
            lift_status     左モータステータス(move, free, brake)
        戻り値：
            なし
        '''
        if left_value is None or right_value is None or lift_value is None:
            return

        if left_status == BRAKE:
            self.left_motor.brake()
        elif left_status == FREE or self._is_idled_zero(left_value):
            self.left_motor.free()
        else:
            self.left_motor.move(left_value)
        
        if right_status == BRAKE:
            self.right_motor.brake()
        elif right_status == FREE or self._is_idled_zero(right_value):
            self.right_motor.free()
        else:
            self.right_motor.move(right_value)

        if lift_status == BRAKE:
            self.lift_motor.brake()
        elif lift_status == FREE or self._is_idled_zero(lift_value):
            self.lift_motor.free()
        else:
            self.lift_motor.move(lift_value)

    def run_threaded(self, left_value, left_status, right_value, right_status, lift_value, lift_status):
        '''
        それぞれのモータに指示を出す。
        引数：
            left_value      左モータ動作レベル(-1.0～1.0)
            left_status     左モータステータス(move, free, brake)
            right_value     右モータ動作レベル(-1.0～1.0)
            right_status    右モータステータス(move, free, brake)
            lift_value      リフトモータ動作レベル(-1.0～1.0)
            lift_status     左モータステータス(move, free, brake)
        戻り値：
            なし
        '''
        self.run(left_value, left_status, right_value, right_status, lift_value, lift_status)

    def shutdown(self):
        '''
        シャットダウン時、各モータの動力がない状態にする。
        引数：
            なし
        戻り値：
            なし
        '''
        self.left_motor.close()
        self.right_motor.close()
        self.lift_motor.close()

    def _is_idled_zero(self, input_value):
        """
        input_value値が0値あそび範囲(-EPSILONE～EPSILONE)に入っているかどうかを判別する。
        引数：
            input_value     float([-1.0, 1.0])  Controller/AutoPilotによる入力値
        戻り値：
            boolean         True:ほぼゼロ、False:ほぼゼロではない
        """
        if self.ep > abs(input_value):
            return True
        else:
            return False

