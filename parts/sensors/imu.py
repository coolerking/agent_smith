"""
MPU6050モジュールを操作するパーツクラスを提供する。
要pigpioパッケージ。
"""

class Mpu6050:
    def __init__(self, pgio=None, bus=1, address=0x68, debug=False):
        """
        MPU6050ドライバを生成しインスタンス変数へ格納する。
        引数：
            pgip    pgio.pi()インスタンス
            address アドレス値
            bus     バス値
            debug   デバッグフラグ
        戻り値：
            なし
        """
        self.mpu = _mpu6050(pgio, address, bus)
        self.debug = debug
        self.init_imu_data()

    def init_imu_data(self):
        """
        IMU情報を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.accel_data = {
            'x':    0,
            'y':    0,
            'z':    0,
        }
        self.gyro_data = self.accel_data

    def update(self):
        """
        IMU情報をセンサから読み取りインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        self.accel_data = self.mpu.get_accel_data()
        self.gyro_data = self.mpu.get_gyro_data()

    def run(self):
        """
        MPU6050を読み込みIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)
        """
        self.accel_data = self.mpu.get_accel_data()
        self.gyro_data = self.mpu.get_gyro_data()
        self.update()
        return self.run_threaded()
    
    def run_threaded(self):
        """
        インスタンス変数上のIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)
        """
        if self.debug:
            print('temp:[{}], acc:[{}, {}, {}], gyro:[{}, {}, {}]'.format(
                self.mpu.get_temp(),
                self.accel_data['x'], self.accel_data['y'], self.accel_data['z'],
                self.gyro_data['x'], self.gyro_data['y'], self.gyro_data['z']))
        return self.accel_data['x'], self.accel_data['y'], self.accel_data['z'], \
            self.gyro_data['x'], self.gyro_data['y'], self.gyro_data['z']

    def shutdown(self):
        """
        処理なし
        引数：
            なし
        戻り値：
            なし
        """
        self.init_imu_data()
        self.mpu = None
        if self.debug:
            print('Mpu6050 shutdown')

class _mpu6050:
    """
    MPU6050 ドライバクラス。
    pigpioパッケージを使ってI2C通信を実行する。
    """

    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    def __init__(self, pgio=None, address=0x68, bus=1):
        """
        I2C通信を開き、MPU6050を起動する。
        引数：
            pgip    pgio.pi()インスタンス
            address アドレス値
            bus     バス値
        戻り値：
            なし
        """
        import pigpio
        self.pi = pgio or pigpio.pi() 
        self.handler = self.pi.i2c_open(bus, address)
        # MPU6050を起動
        self.pi.i2c_write_byte_data(self.handler, self.PWR_MGMT_1, 0x00)

    # I2C 通信関連メソッド

    def read_i2c_word(self, register):
        """
        ２つのI2Cレジスタを読み込み統合する。
        引数：
            register    最初に読み込むレジスタ
        戻り値：
            統合された結果
        """
        # レジスタからデータを読み込み
        high = self.pi.i2c_read_byte_data(self.handler, register)
        low = self.pi.i2c_read_byte_data(self.handler, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 関連メソッド

    def get_temp(self):
        """
        MPU6050上に搭載された温度センサより温度を読み込む。
        引数：
            なし
        戻り値：
            実測温度値（セルシウス）
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)
        actual_temp = (raw_temp / 340.0) + 36.53
        return actual_temp

    def set_accel_range(self, accel_range):
        """
        加速度計の範囲を指定する。
        引数：
            accel_range     加速度計に設定する範囲
        戻り値：
            なし
        """
        # ACCEL_CONFIG レジスタに 0x00 を書き込む
        self.pi.i2c_write_byte_data(self.handler, self.ACCEL_CONFIG, 0x00)

        # ACCEL_CONFIG レジスタに範囲を書き込む
        self.pi.i2c_write_byte_data(self.handler, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw = False):
        """
        加速度計から設定された範囲を読み取る。
        引数：
            raw     真値：ACCEL_CONFIGから読み取る、偽値：整数を返却
        戻り値：
            -1, 2, 4, 8, 16の整数もしくは範囲
        """
        raw_data = self.pi.i2c_read_byte_data(self.handler, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g = False):
        """
        加速度計から座標値を取得する。
        引数：
            g       真値：重力加速度を返却、偽値：m.s^2 を返却
        戻り値：
            加速度（座標値）辞書
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_scale_modifier = None
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """
        ジャイロスコープの範囲を書き込む。
        引数：
            gyro_range      ジャイロスコープ範囲
        戻り値：
            なし
        """
        # GYRO_CONFIG レジスタに0x00を書き込む
        self.pi.i2c_write_byte_data(self.handler, self.GYRO_CONFIG, 0x00)

        # GYRO_CONFIG レジスタに範囲を書き込む
        self.pi.i2c_write_byte_data(self.handler, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw = False):
        """Reads the range the gyroscope is set to.
        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        ジャイロスコープに設定されている範囲を読み取る。
        引数：
            raw 真値：GYRO_CONFIGレジスタから読み取る、偽値：250,500,1000, 2000を返却
        戻り値：
            範囲（エラーの場合-1を返却）
        """
        raw_data = self.pi.i2c_read_byte_data(self.handler, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """
        ジャイロスコープから座標値を読み取る。
        引数：
            なし
        戻り値：
            ジャイロスコープ座標（辞書）
        """
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyro_scale_modifier = None
        gyro_range = self.read_gyro_range(True)

        if gyro_range == self.GYRO_RANGE_250DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG
        elif gyro_range == self.GYRO_RANGE_500DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_500DEG
        elif gyro_range == self.GYRO_RANGE_1000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyro_range == self.GYRO_RANGE_2000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unkown range - gyro_scale_modifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG

        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier

        return {'x': x, 'y': y, 'z': z}

    def get_all_data(self):
        """
        すべての値を標準出力へ表示する。
        引数：
            なし
        戻り値：
            加速度座標辞書、じゃ虚スコープ座標辞書、温度のリスト
        """
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        return [accel, gyro, temp]
    
    def __del__(self):
        """
        インスタンス変数をクリア。
        引数：
            なし
        戻り値：
            なし
        """
        self.handler = None
        self.pi = None

if __name__ == "__main__":
    '''
    動作確認
    '''
    mpu = _mpu6050()
    print(mpu.get_temp())
    accel_data = mpu.get_accel_data()
    print(accel_data['x'])
    print(accel_data['y'])
    print(accel_data['z'])
    gyro_data = mpu.get_gyro_data()
    print(gyro_data['x'])
    print(gyro_data['y'])
    print(gyro_data['z'])