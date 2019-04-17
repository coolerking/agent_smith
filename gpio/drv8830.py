# -*- coding: utf-8 -*-
"""
秋月電子通称 ＤＲＶ８８３０使用ＤＣモータードライブキット
AE-MOTOR8830 通販コード:K-06489
http://akizukidenshi.com/catalog/g/gK-06489/

上記キットのドライバを提供する。

DRV8830 はI2Cによる接続であるため、Raspberri PiのGPIOピンは固定となる。
SDA -> Pi:GPIO2(SDA)
SCL -> Pi:GPIO3(SCL)
OUT1 -> モータ(+)
OUT2 -> モータ(-)
VCC -> モータ電源(+)
GND -> モータ電源(-)/Pi:GND

本クラスは pigpio パッケージを使用しているため、パッケージのインストールおよび
pigpiodの起動(sudo pigpiod)が必須となる。

また、モータ電圧の最大値MAX_VOLTAGEは、使用するモータ電源により変更する必要がある。
"""

import pigpio
from time import sleep

# DRV8830 サブアドレス
ADDR_CONTROL= 0x00
ADDR_FAULT = 0x01

# 最小・最大電圧
MIN_VOLTAGE = 0.48
MAX_VOLTAGE = 3.04

class MotorDriver:
    """
    秋月電子 DRV8830使用DCモータドライブキットを表すドライバクラス。
    """
    def __init__(self, pi, i2cbus, slave_address, max_voltage=MAX_VOLTAGE, retry=3, raise_exception=True):
        """
        pigpioパッケージを使ってI2Cスレーブ(ドライバ本体)のハンドラを取得する。
        モータの状態をfreeにする。
        引数
            pi              pigpioパッケージのpiオブジェクト
            i2cbus          i2cdetect -l で登場するI2Cバスの番号
            slave_address   i2cdetect -y <i2cbus> で表示されるスレーブアドレス
            max_voltage     モータ電源電圧最大値
            retry           送信失敗時の繰り返し回数
            raise_exception 例外を再スローするかどうか
        """
        self.pi = pi
        self.i2cbus = i2cbus
        self.slave_address = slave_address
        self.max_voltage = max_voltage
        self.retry = retry
        self.raise_exception = raise_exception
        self.handler = pi.i2c_open(i2cbus, slave_address)
        self.free()

    def free(self):
        """
        モータを動力なし状態にする。
        引数
            なし
        戻り値
            なし
        """
        command_data = get_control_data(0.0, free=True)
        self.write_command_data(command_data)
    
    def brake(self):
        """
        モータに対し制動停止をかける。ドライバキット仕様には一旦free状態にしてからの
        使用が推奨されている。
        引数
            なし
        戻り値
            なし
        """
        command_data = get_control_data(0.0, brake=True)
        self.write_command_data(command_data)

    def move(self, pwm_value):
        """
        モータを動かす。引数pwm_valueがマイナス値の場合は逆転する。
        引数
            pwm_value       -1.0～1.0
        """
        command_data = get_control_data(self._pwm_value_to_voltage(pwm_value))
        self.write_command_data(command_data)

    def write_command_data(self, command_data):
        """
        コマンドデータを書き込む。
        引数
            command_data    コマンドデータ
        戻り値
            なし
        """
        self._write_data(ADDR_CONTROL, command_data)

    def write_fault_data(self, fault_data):
        """
        FAULTデータを書き込む。
        引数
            fault_data
        """
        self._write_data(ADDR_FAULT, fault_data)

    def _write_data(self, sub_address, data):
        """
        I2C通信書き込みをインスタンス変数retryに指定した回数実行する。
        失敗時の例外はインスタンス変数raise_exceptionがTrueの場合のみ
        再スローされる。
        引数
            sub_address     サブアドレス
            data            送信データ
        戻り値
            なし
        例外
            書き込み失敗時（インスタンス変数raise_exceptionがTrueの場合のみスロー）
        """
        success = False
        caught_exception = None
        for _ in range(self.retry):
            try:
                self.pi.i2c_write_byte_data(self.handler, sub_address, data)
                success = True
            except pigpio.error as e:
                print('error: {} at i2cbus:{} sub_addr:{} / slave_addr:{} data:{}'.format(
                    str(e), 
                    str(self.i2cbus), 
                    str(sub_address) ,
                    str(self.slave_address), 
                    str(bin(data)) ))
                caught_exception = e
                sleep(0.01)
        if not success:
            print('Failed after 3 retries at i2cbus:{} sub_addr:{} / slave_addr:{} data:{} !'.format(
                str(self.i2cbus),
                str(sub_address),
                str(self.slave_address),
                str(bin(data))
            ))
            if self.raise_exception:
                raise caught_exception

    def _pwm_value_to_voltage(self, pwm_value):
        """
        PWM値に対応する電圧値を返却する。
        引数
            pwm_value       -1.0～1.0までの浮動小数点値
        戻り値
            電圧値          -MAX_VOLTAGE ～ MAX_VOLTAGEの範囲の浮動小数点値
        """
        if pwm_value < 0:
            direction = -1.0
        else:
            direction = 1.0
        pwm_val = abs(pwm_value)
        voltage_value = float((self.max_voltage - MIN_VOLTAGE) * pwm_val + MIN_VOLTAGE)
        return voltage_value * direction

    def close(self):
        """
        本ドライバ（スレーブ）とのI2C通信を停止する。
        引数
            なし
        戻り値
            なし
        """
        self.free()
        self.pi.i2c_close(self.handler)

def get_control_data(voltage, free=False, brake=False):
    """
    I2Cコマンドデータに変換して返却する。
    引数
        voltage         指定電圧値
        free            動作状態をfreeにする場合Trueにする。
        brake           動作状態を制動停止にする場合Trueにする。
    戻り値
        I2Cマスタへ書き込むコマンドデータ(8バイト)
        先頭6バイト：指定電圧値に対応するVSET値
        末尾2バイト：IN1、IN2指定値（正転・逆転・free・brake）
    """
    # データシート動作論理表を実装
    if brake:
        in1in2 = 0b11 # IN1:High IN2:High
    elif free or abs(voltage) < MIN_VOLTAGE:
        in1in2 = 0b00 # IN1:Low IN2:Low
    elif voltage > 0:
        in1in2 = 0b10 # IN1:High IN2:Low
    else:
        in1in2 = 0b01 # IN1:Low IN2:High

    # コマンドデータ化して返却
    return (get_vset(voltage) << 2) + in1in2
    '''
    if v < 0.56:
        return (0x06 << 2) + in1in2
    elif v < 0.64:
        return (0x07 << 2) + in1in2
    elif v < 0.72:
        return (0x08 << 2) + in1in2
    elif v < 0.80:
        return (0x09 << 2) + in1in2
    elif v < 0.88:
        return (0x0a << 2) + in1in2
    elif v < 0.96:
        return (0x0b << 2) + in1in2
    elif v < 1.04:
        return (0x0d << 2) + in1in2
    elif v < 1.12:
        return (0x0d << 2) + in1in2
    elif v < 1.20:
        return (0x0e << 2) + in1in2
    elif v < 1.29:
        return (0x0f << 2) + in1in2
    elif v < 1.37:
        return (0x10 << 2) + in1in2
    elif v < 1.45:
        return (0x11 << 2) + in1in2
    elif v < 1.53:
        return (0x12 << 2) + in1in2
    elif v < 1.61:
        return (0x13 << 2) + in1in2
    elif v < 1.69:
        return (0x14 << 2) + in1in2
    elif v < 1.77:
        return (0x15 << 2) + in1in2
    elif v < 1.85:
        return (0x16 << 2) + in1in2
    elif v < 1.93:
        return (0x17 << 2) + in1in2
    elif v < 2.01:
        return (0x18 << 2) + in1in2
    elif v < 2.09:
        return (0x19 << 2) + in1in2
    elif v < 2.17:
        return (0x1a << 2) + in1in2
    elif v < 2.25:
        return (0x1b << 2) + in1in2
    elif v < 2.33:
        return (0x1c << 2) + in1in2
    elif v < 2.41:
        return (0x1d << 2) + in1in2
    elif v < 2.49:
        return (0x1e << 2) + in1in2
    elif v < 2.57:
        return (0x1f << 2) + in1in2
    elif v < 2.65:
        return (0x20 << 2) + in1in2
    elif v < 2.73:
        return (0x21 << 2) + in1in2
    elif v < 2.81:
        return (0x22 << 2) + in1in2
    elif v < 2.89:
        return (0x23 << 2) + in1in2
    elif v < 2.97:
        return (0x24 << 2) + in1in2
    elif v < 3.05:
        return (0x25 << 2) + in1in2
    elif v < 3.13:
        return (0x26 << 2) + in1in2
    elif v < 3.21:
        return (0x27 << 2) + in1in2
    elif v < 3.29:
        return (0x28 << 2) + in1in2
    elif v < 3.37:
        return (0x29 << 2) + in1in2
    elif v < 3.45:
        return (0x2a << 2) + in1in2
    elif v < 3.53:
        return (0x2b << 2) + in1in2
    elif v < 3.61:
        return (0x2c << 2) + in1in2
    elif v < 3.69:
        return (0x2d << 2) + in1in2
    elif v < 3.77:
        return (0x2e << 2) + in1in2
    elif v < 3.86:
        return (0x2f << 2) + in1in2
    elif v < 3.94:
        return (0x30 << 2) + in1in2
    elif v < 4.02:
        return (0x31 << 2) + in1in2
    elif v < 4.10:
        return (0x32 << 2) + in1in2
    elif v < 4.18:
        return (0x33 << 2) + in1in2
    elif v < 4.26:
        return (0x34 << 2) + in1in2
    elif v < 4.34:
        return (0x35 << 2) + in1in2
    elif v < 4.42:
        return (0x36 << 2) + in1in2
    elif v < 4.50:
        return (0x37 << 2) + in1in2
    elif v < 4.58:
        return (0x38 << 2) + in1in2
    elif v < 4.66:
        return (0x39 << 2) + in1in2
    elif v < 4.74:
        return (0x3a << 2) + in1in2
    elif v < 4.82:
        return (0x3b << 2) + in1in2
    elif v < 4.90:
        return (0x3c << 2) + in1in2
    elif v < 4.98:
        return (0x3d << 2) + in1in2
    elif v < 5.06:
        return (0x3e << 2) + in1in2
    else:
        return (0x3f << 2) + in1in2
    '''

# 電圧表 出力電圧
VSET_VOLS = [
    0, 0.48, 0.56, 0.64, 0.72, 0.80, 0.88, 0.96, 1.04, 1.12, 1.20, 
    1.29, 1.37, 1.45, 1.53, 1.61, 1.69, 1.77, 1.85, 1.93, 2.01, 2.09, 2.17, 2.25, 2.33, 2.41, 2.49, 
    2.57, 2.65, 2.73, 2.81, 2.89, 2.97, 3.05, 3.13, 3.21, 3.29, 3.37, 3.45, 3.53, 3.61, 3.69, 3.77, 
    3.86, 3.94, 4.02, 4.10, 4.18, 4.26, 4.34, 4.42, 4.50, 4.58, 4.66, 4.74, 4.82, 4.90, 4.98, 5.06
]

# 電圧表 VSET[5..0]
VSET_DATA = [
    0x00, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f
]

def get_vset(voltage):
    """
    電圧値に対応するVSET値を返却する。
    引数
        電圧
    戻り値
        VSET値
    """
    vol = abs(voltage)
    for v in VSET_VOLS:
        if v > vol:
            return VSET_DATA[VSET_VOLS.index(v)]
    return VSET_DATA[-1]
