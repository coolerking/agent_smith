# -*- coding: utf-8 -*-
"""
periphery パッケージをつかったGPIO/PWM/I2C操作を行う
ラッパクラス群を提供するモジュール。

要peripheryパッケージインストール
$ git clone https://github.com/vsergeev/python-periphery.git
$ cd python-periphery/
$ sudo python setup.py install
"""

# input ピン
IN = 'in'
# output ピン
OUT = 'out'
# PWM output ピン
PWM = 'pwm'

# PWM デフォルトFrequency(Hz)
DEFAULT_FREQ=75

class PERIPHERY:
    """
    peripheryパッケージを使用するGPIOピンの基底クラス。
    """
    def __init__(self, pin, mode=None, debug=False):
        """
        GPIOオブジェクトを生成し、インスタンス変数へ格納する。
        引数：
            pin     int     GPIOピン番号
            debug   boolean デバッグフラグ、デフォルトはFalse
        """
        self.debug = debug
        self.pin = pin
        if mode != IN and mode != OUT and mode != PWM:
            raise ValueError('[PERIPHERY] unsupported mode: {}'.format(str(mode)))
        self.mode = mode
        try:
            from periphery import GPIO
        except ImportError:
            exit('[PERIPHERY] This code requires periphery package')
        if (pin == 73 or pin== 77) and mode != OUT:
            raise ValueError('[PERIPHERY] GPIO73 and GPIO77 currently support only the "out" direction.')
        if mode != PWM:
            self.gpio = GPIO(pin, mode)
        else:
            self.gpio = None
        if self.debug:
            print('[PERIPHERY] set pin:{} mode:{}'.format(str(pin), str(mode)))
    
    def shutdown(self):
        self.gpio.close()

class PERIPHERY_OUT(PERIPHERY):
    """
    デジタル出力ピンをあらわすクラス。
    """
    def __init__(self, pin, debug=False):
        """
        親コンストラクタ処理後、指定ピンへ０値を出力する。
        引数：
            pin     int     GPIOピン番号
            debug   boolean デバッグフラグ、デフォルトはFalse
        """
        super().__init__(pin, mode=OUT, debug=debug)
        self.gpio.write(False)
        if self.debug:
            print('[PERIPHERY_OUT] gpio:{} set value 0'.format(str(self.pin)))
        

    def run(self, pulse):
        """
        引数で渡されたpulse値が０より大きい値の場合は１，
        None含むそうでない場合０として、指定ピンへ出力する。
        引数：
            pulse       float       コントローラ/AIからの入力値
        戻り値：
            なし
        """
        if pulse > 0:
            self.gpio.write(True)
            if self.debug:
                print('[PERIPHERY_OUT] gpio:{} set value 1'.format(str(self.pin)))
        else:
            self.gpio.write(False)
            if self.debug:
                print('[PERIPHERY_OUT] gpio:{} set value 0'.format(str(self.pin)))
    
class PERIPHERY_PWM(PERIPHERY):
    """
    PWM出力ピンを表すクラス。
    指定ピンがハードウェアPWMに対応しない場合は、疑似PWMとして操作する。
    """
    def __init__(self, pin, freq=None, range=None, threshold=0.01, debug=False):
        """
        親クラスのコンストラクタ処理後、指定のピンに対しPWM出力ピンとして設定を行う。
        初期値としてPWMサイクル値をゼロに指定する。
        引数：
            pin     int     PWM番号、必須(1～3)
            freq    int     PWM Frequency値（Hz）
            range   int     PWMサイクル値の範囲(25から40,000までの整数)
            threshold   float   入力値を0として認識するしきい値(-threshold < value< threshold => 0)
        """
        super().__init__(pin, mode=OUT, debug=debug)
        self.freq = freq or DEFAULT_FREQ
        self.threshold = threshold
        if self.pin == 1:
            self.chip_number = 0
            self.channel_number = 0
        elif self.pin == 2:
            self.chip_number = 1
            self.channel_number = 0
        elif self.pin == 3:
            self.chip_number = 2
            self.channel_number = 0
        else:
            raise ValueError('[PERIPHERY_PWM] pwm:{} is out of range(1.. 3)'.format(str(self.pin)))
        try:
            from periphery import PWM
        except ImportError:
            exit('[PERIPHERY_PWM] This code requires periphery package')
        self.gpio = PWM(self.chip_number, self.channel_number)
        self.gpio.frequency = self.freq
        self.gpio.duty_cycle = 0
        self.gpio.enable()
        self.run(0)
        if self.debug:
            print('[PERIPHERY_PWM] pwm:{} set freq:{}/dutycycle:{}, enabled and set value 0'.format(
                str(self.pin), str(self.freq), str(self.gpio.duty_cycle)))

    def run(self, input_value):
        """
        引数で渡されたpulse値をPWMサイクル値に変換し、指定ピンへ出力する。
        引数：
            input_value float       コントローラ/AIからの入力値
        戻り値：
            なし
        """
        cycle = self.to_duty_cycle(input_value)
        self.gpio.duty_cycle(cycle)
        if self.debug:
            print('[PERIPHERY_PWM] pwm:{} set cycle {}(input_value:{})'.format(
                str(self.pin), str(cycle), str(input_value)))


    def to_duty_cycle(self, input_value):
        """
        コントローラ/AIからの入力値をPWMサイクル値に変換する。
        しきい値範囲内の場合やNoneの場合は、0として扱う。
        引数：
            input_value     float   コントローラ/AIからの入力値（None含む）
        戻り値：
            cycle           float     PWM duty_cycle値
        """
        if input_value is None or (abs(float(input_value)) < self.threshold):
            if self.debug:
                print('[PERIPHERY_PWM] gpio:{} input_value None to zero'.format(str(self.pin)))
            return float(0)
        input_value = abs(input_value)
        if input_value >= 1.0:
            return float(1.0)
        return float(input_value)
    
    def shutdown(self):
        self.run(0)
        self.gpio.disable()
        if self.debug:
            print('[PERIPHERY_PWM] set duty_cycle to 0 and disabled')
        super().shutdown()

class PERIPHERY_I2C:
    I2C_DEV_PATH_PREFIX = '/dev/i2c-'
    def __init__(self, i2cbus=1):
        self.devpath = self.I2C_DEV_PATH_PREFIX + str(i2cbus)
        try:
            from periphery import I2C
        except ImportError:
            exit('[PERIPHERY_PWM] This code requires periphery package')
        self.i2c = I2C(self.devpath)



    def to_message(self, data, read=False, flags=0):
        try:
            from periphery import I2C.Message
        except ImportError:
            exit('[PERIPHERY_PWM] This code requires periphery package')
        return I2C.Message(data, read, flags)

    def shutdown(self):
        self.i2c.close()