# -*- coding: utf-8 -*-
"""
TP7291P(疑似PWM)モータドライバを使用した場合のパワーユニットパーツクラス。

KerasLinear/JoyStickControllerからは範囲[-1.0, 1.0]のfloat値が出力される。
"""
from .ta7291p import MotorDriver

EPSILONE = 0.1

BRAKE = 'brake'
FREE =  'free'

class PowerUnit:
    '''
    フォークリフトに搭載された３つのモータを管理するクラス。
    Donkey値は-1.0から+1.0のfloat値であらわす絶対値が大きい値になるほど速くなる。
    0値の場合は、速度が0となる。
    '''
    def __init__(self, pi, pu_gpios):
        '''
        フォークリフトに接続された左モータ、右モータ、リフトモータを管理する
        TA7291Pを操作可能な状態にする。
        引数：
            pi          pigpioパッケージのpiオブジェクト
            pu_gpios    パワーユニット用GPIO番号が格納された２次元配列
        '''
        self.pi = pi
        self.left_motor =   MotorDriver(self.pi, pu_gpios[0][0], pu_gpios[0][1], pu_gpios[0][2])
        self.right_motor =  MotorDriver(self.pi, pu_gpios[1][0], pu_gpios[1][1], pu_gpios[1][2])
        self.lift_motor =   MotorDriver(self.pi, pu_gpios[2][0], pu_gpios[2][1], pu_gpios[2][2])

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
        # 未入力状態の場合、何もしない
        if left_value is None or right_value is None or lift_value is None:
            return

        if left_status == BRAKE:
            self.left_motor.brake()
        elif left_status == FREE:
            self.left_motor.free()
        else:
            self.left_motor.move(self._add_idle(left_value))
        
        if right_status == BRAKE:
            self.right_motor.brake()
        elif right_status == FREE:
            self.right_motor.free()
        else:
            self.right_motor.move(self._add_idle(right_value))
        
        if lift_status == BRAKE:
            self.lift_motor.brake()
        elif lift_status == FREE:
            self.lift_motor.free()
        else:
            self.lift_motor.move(self._add_idle(lift_value))
    
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
        self.left_motor.free()
        self.right_motor.free()
        self.lift_motor.free()

    def _add_idle(self, input_value):
        """
        ゼロの前後あそび(EPSILONE)範囲内の値をゼロとして扱う補正を加え返却する。
        引数：
            input_value     float([-1.0,1.0])   入力された値
        戻り値：
            idled_value     float([-1.0,1.0])   0近傍補正された入力値
        """
        if input_value < -1.0:
            idled_value = -1.0
        elif 1.0 < input_value:
            idled_value = 1.0
        elif EPSILONE > abs(input_value):
            idled_value = 0.0
        else:
            idled_value = input_value
        return idled_value

