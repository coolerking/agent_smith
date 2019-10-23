# -*- coding: utf-8 -*-
"""
pigpioパッケージを使用したGPIO操作を行うためのパーツクラス群。
"""


DEFAULT_FREQ=75
DEFAULT_RANGE=255
class PIGPIO:
    """
    pigpioパッケージを使用するGPIOピンの基底クラス。
    """
    def __init__(self, pin, mode=None, pgio=None, debug=False):
        """
        引数の各値をインスタンス変数へ格納する。piインスタンスがNoneの場合生成する。
        モードを対象ピンへ設定する。
        引数：
            pin     int     GPIOピン番号(0-31の整数)
            pgio            piインスタンス、Noneの場合生成する
            debug   boolean デバッグフラグ、デフォルトはFalse
        """
        self.debug = debug
        import pigpio
        #pigpio.exceptions = self.debug
        self.pgio = pgio or pigpio.pi()
        self.pin = pin
        if mode is not None:
            self.pgio.set_mode(pin, mode)
            if self.debug:
                print('gpio:{} set mode {}'.format(str(pin), str(mode)))

    def shutdown(self):
        """
        piインスタンスを開放する（クローズしない）。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('gpio:{} shutdown'.format(str(self.pin)))
        self.pgio = None

class PIGPIO_OUT(PIGPIO):
    """
    デジタル出力ピンをあらわすクラス。
    """
    def __init__(self, pin, pgio=None, debug=False):
        """
        親コンストラクタ処理後、指定ピンへ０値を出力する。
        引数：
            pin     int     GPIOピン番号(0-31の整数)
            pgio            piインスタンス、Noneの場合生成する
            debug   boolean デバッグフラグ、デフォルトはFalse
        """
        super().__init__(pin, mode=pigpio.OUTPUT, pgio=pgio, debug=debug)
        self.pgio.write(self.pin, 0)
        if self.debug:
            print('gpio:{} set value 0'.format(str(pin)))
        

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
            self.pgio.write(self.pin, 1)
            if self.debug:
                print('gpio:{} set value 1'.format(str(self.pin)))
        else:
            self.pgio.write(self.pin, 0)
            if self.debug:
                print('gpio:{} set value 0'.format(str(self.pin)))

class PIGPIO_PWM(PIGPIO):
    """
    PWM出力ピンを表すクラス。
    指定ピンがハードウェアPWMに対応しない場合は、疑似PWMとして操作する。
    """
    def __init__(self, pin, pgio=None, freq=None, range=None, threshold=0.01, debug=False):
        """
        親クラスのコンストラクタ処理後、指定のピンに対しPWM出力ピンとして設定を行う。
        初期値としてPWMサイクル値をゼロに指定する。
        引数：
            pin     int     GPIOピン番号、必須
            pgio            piインスタンス、Noneの場合は生成する
            freq    int     PWM Frequency値（Hz）
            range   int     PWMサイクル値の範囲(25から40,000までの整数)
            threshold   float   入力値を0として認識するしきい値(-threshold < value< threshold => 0)
        """
        super().__init__(pin, mode=pigpio.OUTPUT, pgio=pgio, debug=debug)
        self.freq = freq or DEFAULT_FREQ
        self.range = range or DEFAULT_RANGE
        if self.freq is not None:
            self.pgio.set_PWM_frequency(self.pin, self.freq)
            if self.debug:
                print('gpio:{} set pwm freq {}'.format(str(pin), str(self.freq)))
        self.threshold = threshold

        if self.range is not None:
            self.pgio.set_PWM_range(self.pin, self.range)
            if self.debug:
                print('gpio:{} set pwm range {}'.format(str(pin), str(self.range)))
        
        self.pgio.set_PWM_dutycycle(self.pin, 0)
        if self.debug:
            print('gpio:{} set cycle 0'.format(str(pin)))

    def run(self, input_value):
        """
        引数で渡されたpulse値をPWMサイクル値に変換し、指定ピンへ出力する。
        引数：
            input_value float       コントローラ/AIからの入力値
        戻り値：
            なし
        """
        cycle = self.to_duty_cycle(input_value)
        if self.debug:
            print('gpio:{} set cycle {}(input_value:{})'.format(str(self.pin), str(cycle), str(input_value)))
        self.pgio.set_PWM_dutycycle(self.pin, cycle)


    def to_duty_cycle(self, input_value):
        """
        コントローラ/AIからの入力値をPWMサイクル値に変換する。
        しきい値範囲内の場合やNoneの場合は、0として扱う。
        引数：
            input_value     float   コントローラ/AIからの入力値（None含む）
        戻り値：
            cycle           int     PWMサイクル値
        """
        if input_value is None:
            if self.debug:
                print('gpio:{} input_value None to zero'.format(str(self.pin)))
            return int(0)
        elif abs(float(input_value)) < self.threshold:
            if self.debug:
                print('gpio:{} input_value {} to zero'.format(str(input_value), str(self.pin)))
            return int(0)
        return int(float(self.range) * float(abs(float(input_value))))

class PIGPIO_IN(PIGPIO):
    """
    INPUT ピンを操作するための基底クラス。
    """
    def __init__(self, pin, pgio=None, debug=False):
        """
        親クラスのコンストラクタを呼び出すだけ。

        引数：
            pin     int         GPIOピン番号、必須
            pgio                piインスタンス、すでに生成している場合のみ指定する 
            debug   boolean     デバッグフラグ、デフォルトはFalse
        戻り値：
            なし
        """
        super().__init__(pin, mode=pigpio.INPUT, pgio=pgio, debug=debug)
    
    def run(self):
        """
        デジタル値を読み取る
        """
        value = self.pgio.read(self.pin)
        if self.debug:
            print('gpio:{} read value {}'.format(str(self.pin), str(value)))
        return value

class PIGPIO_SPI_ADC:
    """
    MCP3208CI-P ADコンバータをあらわすクラス。
    """

    def __init__(self, pgio=None, vref_volts=3.3, 
    spi_channel=0, spi_baud=50000, spi_flags=0, debug=False):
        """
        SPI通信を開く。

        引数：
            pi              pigpio piオブジェクト
            vref_volts      Vrefに接続した電圧(V)
            spi_channel     SPIチャネル
            baud            SPI通信速度(bits/sec)
            spi_flags       SPI フラグ
        戻り値：
            なし
        """
        #pigpio.exceptions = debug
        import pigpio
        self.pgio = pgio or pigpio.pi()
        self.vref_volts = vref_volts
        self.debug = debug
        self.spi_channel = spi_channel
        self.handler = self.pgio.spi_open(spi_channel, spi_baud, spi_flags)
        if self.debug:
            print('spi channel:{} set baud {}, flags {}'.format(
                str(spi_channel), str(spi_baud), str(spi_flags)))

    def read_volts(self, channel):
        """
        指定されたチャネルの電圧を取得する。

        引数：
            channel     チャネル(0～7)
        戻り値
            volts       電圧(V)
        """
        c, raw = self.pgio.spi_xfer(self.handler, [1, (8 + channel)<<4, 0])
        if self.debug:
            print("spi channel:{} xfer c: {0} raw: {1}".format(str(self.spi_channel), c, raw))
        raw2 = ((raw[1] & 3) << 8) + raw[2]
        volts = (raw2 * self.vref_volts ) / float(1023)
        return round(volts, 4)
    
    def run(self, channel):
        """
        指定チャネルの電圧値を読み取る。
        引数：
            channel     int     チャネル番号(0から7までの整数)
        戻り値：
            volts       float   電圧値（V）
        """
        volts = self.read_volts(channel)
        if self.debug:
            print("spi channel:{} read {} volts".format(str(self.spi_channel), str(volts)))
        return volts
    
    def __del__(self):
        """
        SPIチャネルを閉じる。

        引数：
            なし
        戻り値：
            なし
        """
        self.pgio.spi_close(self.handler)
        if self.debug:
            print('spi channel:{} close'.format(str(self.spi_channel)))
        self.pgio = None
    
    def shutdown(self):
        """
        実装なし。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('spi channel:{} shutdown'.format(str(self.spi_channel)))