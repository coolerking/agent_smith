# -*- coding: utf-8 -*-
"""
MPU6050/MPU9250モジュールを操作するパーツクラスを提供する。
要pigpioパッケージ、I2C接続前提。
"""

import time
import json

class Mpu6050:
    def __init__(self, pgio=None, bus=1, address=0x68, depth=3, debug=False):
        """
        MPU6050ドライバを生成しインスタンス変数へ格納する。
        引数：
            pgip    pgio.pi()インスタンス
            address アドレス値
            bus     バス値
            depth   残しておく最新データ件数
            debug   デバッグフラグ
        戻り値：
            なし
        """
        self.mpu = _mpu6050(pgio, address, bus)
        self.debug = debug
        self.depth = depth
        if self.debug:
            print('[Mpu6050] depth={}'.format(str(self.depth)))
        self.init_imu_data()

    def init_imu_data(self):
        """
        IMU情報を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.temp = 0
        self.accel_data = {'x': 0, 'y': 0, 'z': 0}
        self.gyro_data =  {'x': 0, 'y': 0, 'z': 0}
        self.timestamp = time.time()
        self.recent_data = []
        packed_data = pack(self.timestamp, self.temp, self.accel_data, self.gyro_data)
        for _ in range(self.depth):
            self.recent_data.append(packed_data)

    def update(self):
        """
        IMU情報をセンサから読み取りインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        temp = self.mpu.get_temp()
        if temp is not None:
            self.temp = temp
        self.accel_data = omit_none(self.accel_data, self.mpu.get_accel_data())
        self.gyro_data = omit_none(self.gyro_data, self.mpu.get_gyro_data())
        self.timestamp = time.time()
        push_recent_data(self.recent_data, pack(self.timestamp, self.temp, self.accel_data, self.gyro_data))

    def run(self):
        """
        MPU6050を読み込みIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)
        """
        self.update()
        return self.run_threaded()
    
    def run_threaded(self):
        """
        インスタンス変数上のIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)、気温、
            過去最新データ（文字列）、タイムスタンプ
        """
        accel_x, accel_y, accel_z = \
            self.accel_data['x'], self.accel_data['y'] ,self.accel_data['z']
        gyro_x, gyro_y, gyro_z = \
            self.gyro_data['x'], self.gyro_data['y'] ,self.gyro_data['z']
        if self.debug:
            print('temp:[{}], acc:[{}, {}, {}], gyro:[{}, {}, {}] ts:{}'.format(
                str(self.temp), str(accel_x), str(accel_y), str(accel_z), 
                str(gyro_x), str(gyro_y), str(gyro_z), str(self.timestamp)))
        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, \
            self.temp, str_recent_data(self.recent_data), self.timestamp

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
        if pgio is None:
            try:
                import pigpio
                self.pi = pigpio.pi()
            except:
                raise
        else:
            self.pi = pgio 
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
        """
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
            加速度座標辞書、ジャイロスコープ座標辞書、温度のリスト
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

class Mpu9250:
    def __init__(self, pgio=None, bus=1, 
    mpu9250_address=None, ak8963_address=None, depth=3, debug=False):
        """
        MPU9250ドライバを生成しインスタンス変数へ格納する。
        引数：
            pgip                pgio.pi() インスタンス
            bus                 I2Cバス値
            mpu9250_address     MPU9250 I2Cスレーブアドレス
            ak8963_address      AK8963 I2Cスレーブアドレス
            depth               最新データを残す件数(デフォルト:3)
            debug               デバッグフラグ(デフォルト:False)
        戻り値：
            なし
        """
        self.mpu = _mpu9250(
            pgio=pgio, 
            mpu9250_address=mpu9250_address, 
            ak8963_address=ak8963_address, 
            debug=debug)
        self.debug = debug
        self.depth = depth
        if self.debug:
            print('[Mpu9250] depth={}'.format(str(self.depth)))
        self.init_imu_data()

    def init_imu_data(self):
        """
        IMU情報を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.temp = 0
        self.accel_data = {'x': 0, 'y': 0, 'z': 0}
        self.gyro_data =  {'x': 0, 'y': 0, 'z': 0}
        self.magnet_data = {'x': 0, 'y': 0, 'z': 0}
        self.timestamp = time.time()
        self.recent_data = []
        packed_data = pack(self.timestamp, self.temp, 
            self.accel_data, self.gyro_data, self.magnet_data)
        for _ in range(self.depth):
            self.recent_data.append(packed_data)

    def update(self):
        """
        IMU情報をセンサから読み取りインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        temp = self.mpu.readTemperature()
        if temp is not None:
            self.temp = temp
        self.accel_data = omit_none(self.accel_data,self.mpu.readAccel())
        self.gyro_data = omit_none(self.gyro_data, self.mpu.readGyro())
        self.magnet_data = omit_none(self.magnet_data, self.mpu.readMagnet())
        self.timestamp = time.time()
        push_recent_data(
            self.recent_data, 
            pack(self.timestamp, self.temp, 
                self.accel_data, self.gyro_data, self.magnet_data))

    def run(self):
        """
        MPU9250を読み込みIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)
        """
        self.update()
        return self.run_threaded()
    
    def run_threaded(self):
        """
        インスタンス変数上のIMU情報を返却する。
        引数：
            なし
        戻り値：
            加速度座標値(x,y,z)、ジャイロスコープ座標値(x,y,z)、磁束密度値(x, y, z)、
            気温、最新過去データ文字列、現在時刻
        """
        accel_x, accel_y, accel_z = \
            self.accel_data['x'], self.accel_data['y'] ,self.accel_data['z']
        gyro_x, gyro_y, gyro_z = \
            self.gyro_data['x'], self.gyro_data['y'] ,self.gyro_data['z']
        magnet_x, magnet_y, magnet_z = \
            self.magnet_data['x'], self.magnet_data['y'] ,self.magnet_data['z']
        if self.debug:
            print('temp:[{}], acc:[{}, {}, {}], gyro:[{}, {}, {}] magnet:[{}, {}, {}] ts:{}'.format(
                str(self.temp), str(accel_x), str(accel_y), str(accel_z), 
                str(gyro_x), str(gyro_y), str(gyro_z), 
                str(magnet_x), str(magnet_y), str(magnet_z), str(self.timestamp)))
        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, \
            magnet_x, magnet_y, magnet_z, \
            self.temp, str_recent_data(self.recent_data), self.timestamp

    def shutdown(self):
        """
        MPU9250をクローズする。
        引数：
            なし
        戻り値：
            なし
        """
        self.mpu.close()
        self.init_imu_data()
        self.mpu = None
        if self.debug:
            print('[Mpu9250] shutdown')

class _mpu9250:
    """
    MPU9260ドライバクラス。
    以下のライブラリをsmbusからpigpioに変更したもの。
    https://github.com/FaBoPlatform/FaBo9AXIS-MPU9250-Python
    なおベースのコード(V1.0.0)はApache-2.0ライセンス準拠である。
    """

    ## MPU9250 デフォルト I2C スレーブアドレス
    SLAVE_ADDRESS        = 0x68
    ## AK8963 I2C スレーブアドレス
    AK8963_SLAVE_ADDRESS = 0x0C
    ## デバイス ID
    DEVICE_ID            = 0x71

    ''' MPU-9250 レジスタアドレス '''
    ## sample rate driver
    SMPLRT_DIV     = 0x19
    CONFIG         = 0x1A
    GYRO_CONFIG    = 0x1B
    ACCEL_CONFIG   = 0x1C
    ACCEL_CONFIG_2 = 0x1D
    LP_ACCEL_ODR   = 0x1E
    WOM_THR        = 0x1F
    FIFO_EN        = 0x23
    I2C_MST_CTRL   = 0x24
    I2C_MST_STATUS = 0x36
    INT_PIN_CFG    = 0x37
    INT_ENABLE     = 0x38
    INT_STATUS     = 0x3A
    ACCEL_OUT      = 0x3B
    TEMP_OUT       = 0x41
    GYRO_OUT       = 0x43

    I2C_MST_DELAY_CTRL = 0x67
    SIGNAL_PATH_RESET  = 0x68
    MOT_DETECT_CTRL    = 0x69
    USER_CTRL          = 0x6A
    PWR_MGMT_1         = 0x6B
    PWR_MGMT_2         = 0x6C
    FIFO_R_W           = 0x74
    WHO_AM_I           = 0x75

    ## Gyro Full Scale Select 250dps
    GFS_250  = 0x00
    ## Gyro Full Scale Select 500dps
    GFS_500  = 0x01
    ## Gyro Full Scale Select 1000dps
    GFS_1000 = 0x02
    ## Gyro Full Scale Select 2000dps
    GFS_2000 = 0x03
    ## Accel Full Scale Select 2G
    AFS_2G   = 0x00
    ## Accel Full Scale Select 4G
    AFS_4G   = 0x01
    ## Accel Full Scale Select 8G
    AFS_8G   = 0x02
    ## Accel Full Scale Select 16G
    AFS_16G  = 0x03

    # AK8963 レジスタアドレス
    AK8963_ST1        = 0x02
    AK8963_MAGNET_OUT = 0x03
    AK8963_CNTL1      = 0x0A
    AK8963_CNTL2      = 0x0B
    AK8963_ASAX       = 0x10
    AK8963_ASAY       = 0x11
    AK8963_ASAZ       = 0x12

    # CNTL1 モードセレクト
    ## パワーダウンモード
    AK8963_MODE_DOWN   = 0x00
    ## One shot データ出力
    AK8963_MODE_ONE    = 0x01

    ## Continous data output 8Hz
    AK8963_MODE_C8HZ   = 0x02
    ## Continous data output 100Hz
    AK8963_MODE_C100HZ = 0x06

    # 磁束密度スケール選択
    ## 14 ビット出力
    AK8963_BIT_14 = 0x00
    ## 16 ビット出力
    AK8963_BIT_16 = 0x01

    def __init__(self, pgio=None, bus=1, 
    mpu9250_address=SLAVE_ADDRESS, ak8963_address=AK8963_SLAVE_ADDRESS, debug=False):
        """
        初期化処理。pigpioオブジェクトが与えられなかった場合は
        内部で生成される。
        引数：
            pgio                pigpioオブジェクト
            bus                 I2C バス
            mpu9250_address     MPU9250スレーブアドレス
            ak8963_address      AK8963スレーブアドレス
            debug               デバッグフラグ
        戻り値：
            なし
        """
        self.bus = bus
        self.debug = debug
        if pgio is None:
            try:
                import pigpio
                self.pi = pigpio.pi()
                if self.debug:
                    print('[_mpu9250] open pigpio')
                self.use_close = True
            except:
                raise
        else:
            self.pi = pgio
            self.use_close = False
        self.mpu9250_address = mpu9250_address
        self.mpu9250_handler = self.pi.i2c_open(bus, mpu9250_address)
        if self.debug:
            print('[_mpu9250] open mpu9250 i2c bus:{} addr:{}'.format(
                str(self.bus), str(self.mpu9250_address)))
        self.configMPU9250(self.GFS_250, self.AFS_2G)
        self.ak8963_address = ak8963_address
        self.ak8963_handler = self.pi.i2c_open(bus, ak8963_address)
        self.configAK8963(self.AK8963_MODE_C8HZ, self.AK8963_BIT_16)
        if self.debug:
            print('[_mpu9250] open ak8963  i2c bus:{} addr:{}'.format(
                str(self.bus), str(self.ak8963_address)))

    def searchDevice(self):
        """
        デバイスが存在するかを検索する。
        引数：
            なし
        戻り値：
            boolean(有無)
        """
        who_am_i = self.pi.i2c_read_byte_data(self.mpu9250_handler, self.WHO_AM_I)
        if(who_am_i == self.DEVICE_ID):
            return True
        else:
            return False

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self, gfs, afs):
        """
        MPU9250の初期設定をおこなう。
        引数：
            gfs     ジャイロフルスケール指定（デフォルト：GFS_250[+250dps]）
            afs     加速度フルスケール指定（デフォルト：AFS_2G[2g]）
        戻り値：
            なし
        """
        if gfs == self.GFS_250:
            self.gres = 250.0/32768.0
        elif gfs == self.GFS_500:
            self.gres = 500.0/32768.0
        elif gfs == self.GFS_1000:
            self.gres = 1000.0/32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0/32768.0

        if afs == self.AFS_2G:
            self.ares = 2.0/32768.0
        elif afs == self.AFS_4G:
            self.ares = 4.0/32768.0
        elif afs == self.AFS_8G:
            self.ares = 8.0/32768.0
        else: # afs == AFS_16G:
            self.ares = 16.0/32768.0

        # スリープOFF
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # DLPF_CFG
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.CONFIG, 0x03)
        # sample rate divider
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.SMPLRT_DIV, 0x04)
        # ジャイロフルスケール指定
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.GYRO_CONFIG, gfs << 3)
        # 加速度フルスケール指定
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.ACCEL_CONFIG, afs << 3)
        # A_DLPFCFG
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        self.pi.i2c_write_byte_data(self.mpu9250_handler, self.INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    def configAK8963(self, mode, mfs):
        """
        AK8963の初期設定を行う。
        引数：
            mode    磁束密度モード指定（デフォルト：AK8963_MODE_C8HZ[連続8Hz]）
            mfs     磁束密度スケール指定（デフォルト：AK8963_BIT_16[16ビット]）
        """
        if mfs == self.AK8963_BIT_14:
            self.mres = 4912.0/8190.0
        else: #  mfs == AK8963_BIT_16:
            self.mres = 4912.0/32760.0

        self.pi.i2c_write_byte_data(self.ak8963_handler, self.AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        self.pi.i2c_write_byte_data(self.ak8963_handler, self.AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = self._read_i2c_block_data(self.ak8963_handler, self.AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        self.pi.i2c_write_byte_data(self.ak8963_handler, self.AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        self.pi.i2c_write_byte_data(self.ak8963_handler, self.AK8963_CNTL1, (mfs<<4|mode))
        time.sleep(0.01)

    def checkDataReady(self):
        """
        MPU9250がデータ読み取り準備ができているかどうか判別する。
        引数：
            なし
        戻り値：
            boolean(OK/NG)
        """
        drdy = self.pi.i2c_read_byte_data(self.mpu9250_handler, self.INT_STATUS)
        if drdy & 0x01:
            return True
        else:
            return False

    def readAccel(self):
        """
        加速度データを読み取る。
        引数：
            なし
        戻り値：
            辞書(x, y, z)
        """
        data = self._read_i2c_block_data(self.mpu9250_handler, self.ACCEL_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.ares, 3)
        y = round(y*self.ares, 3)
        z = round(z*self.ares, 3)

        return {"x":x, "y":y, "z":z}

    def readGyro(self):
        """
        ジャイロデータを読み取る。
        引数：
            なし
        戻り値：
            辞書(x, y, z)
        """
        data = self._read_i2c_block_data(self.mpu9250_handler, self.GYRO_OUT, 6)

        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.gres, 3)
        y = round(y*self.gres, 3)
        z = round(z*self.gres, 3)

        return {"x":x, "y":y, "z":z}

    def readMagnet(self):
        """
        磁束密度データを読み取る。
        引数：
            なし
        戻り値：
            辞書(x, y, z)
        """
        x=0
        y=0
        z=0

        # データ読み取り準備の確認
        drdy = self.pi.i2c_read_byte_data(self.ak8963_handler, self.AK8963_ST1)
        if drdy & 0x01 :
            data = self._read_i2c_block_data(self.ak8963_handler, self.AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08)!=0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])

                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)

        return {"x":x, "y":y, "z":z}

    def readTemperature(self):
        """
        温度を読み取る。
        引数：
            なし
        戻り値：
            温度(C)
        """
        data = self._read_i2c_block_data(self.mpu9250_handler, self.TEMP_OUT, 2)
        temp = self.dataConv(data[1], data[0])

        temp = round((temp / 333.87 + 21.0), 3)
        return temp

    def dataConv(self, data1, data2):
        """
        データをコンバートする。
        引数：
            data1   LSB
            data2   MSB
        戻り値：
            コンバート値(int 16ビット)
        """
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

    def close(self):
        """
        クローズ処理。
        引数：
            なし
        戻り値：
            なし
        """
        if self.mpu9250_handler >= 0:
            self.pi.i2c_close(self.mpu9250_handler)
            if self.debug:
                print('[_mpu9250] close mpu9250 i2c bus:{} addr:{}'.format(
                    str(self.bus), str(self.mpu9250_address)))
        if self.ak8963_handler >= 0:
            self.pi.i2c_close(self.ak8963_handler)
            if self.debug:
                print('[_mpu9250] close ak8963  i2c bus:{} addr:{}'.format(
                    str(self.bus), str(self.ak8963_address)))
        if self.use_close and self.pi is not None:
            self.pi.close()
            if self.debug:
                print('[_mpu9250] close pigpio')

    def _read_i2c_block_data(self, handler, reg, count):
        """
        SMBusのread_i2c_block_dataと戻り値を合わせるための関数。
        引数：
            handler     pigpio I2C ハンドラ
            reg         デバイスレジスタ
            count       読み込むバイト数
        戻り値：
            int[]       read_i2c_block_dataの戻り値はlong[]だがpython3
                        なのでint[]
        例外：
            ConnectionError エラーの場合
        """
        (b, d) = self.pi.i2c_read_i2c_block_data(handler, reg, count)
        if b >= 0:
            data = []
            for i in range(count):
                value = int(d[i])
                data.append(value)
            return data
        else:
            raise ConnectionError('Error:{} in i2c_read_i2c_block_data'.format(str(b)))

class PrintMpu9250:
    def run(self, ax, ay, az, gx, gy, gz, mx, my, mz, temp, recent, ts):
        print('[MPU9250] temp:{} ts:{} a:({}, {}, {}) g:({}, {}, {}) m:({}, {}, {})'.format(
            str(temp), str(ts),
            str(ax), str(ay), str(az),
            str(gx), str(gy), str(gz),
            str(mx), str(my), str(mz)
        ))
        print('          {}'.format(str(recent)))
    def shutdown(self):
        pass


# ユーティリティ関数群

def push_recent_data(recent_data, current_dict):
    """
    引数recent_dataで渡された配列の最期に引数current_data値を
    格納し、先頭データを削除した配列を返却する。
    引数：
        recent_data     配列、編集元
        current_data    追加する要素
    戻り値：
        編集後配列
    """
    return_data = recent_data[1:]
    return_data.append(current_dict)
    return return_data

def str_recent_data(recent_data):
    """
    引数recent_data で渡された配列の要素すべてを辞書化して
    文字列に変換する。
    引数：
        recent_data     文字列化対象の配列(最新データ群)
    戻り値：
        文字列化化された最新データ群
    """
    return_dict = {}
    depth = len(recent_data)
    for i in range(depth):
        return_dict[str(i)] = recent_data[i]
    return json.dumps(return_dict)

def pack(timestamp, temp, accel_data, gyro_data, magnet_data=None):
    """
    最新位置情報データを辞書化する。
    引数：
        timestamp   時刻
        temp        気温(float)
        accel_data  加速度データ（辞書）
        gyro_data   角速度データ（辞書）
        magnet_data 磁束密度データ（辞書）：オプション
    戻り値：
        最新位置情報データ群（辞書）
    """
    return_dict =  {'accel': accel_data, 'gyro': gyro_data, 'temp': temp, 'timestamp': timestamp}
    if magnet_data is not None:
        return_dict['magnet'] = magnet_data
    return return_dict

def omit_none(recent_dict, current_dict):
    """
    None値を１件前のデータに置き換える。
    引数：
        recent_dict     1件前のデータ（辞書）
        current_dict    最新データ（辞書）
    戻り値：
        Noneを1件前のデータに置き換えられた最新データ（辞書）
    """
    return_dict = {}
    for key in ['x', 'y', 'z']:
        if current_dict[key] is None:
            return_dict[key] = to_float(recent_dict[key])
        else:
            return_dict[key] = to_float(current_dict[key])
    return return_dict

def to_float(value):
    """
    Noneを0.0に置き換えfloat化する。
    引数：
        value   対象値
    戻り値：
        置き換え済みfloat値
    """
    if value is None:
        return 0.0
    else:
        return float(value)

## テストコード

def test_mpu6050():
    """
    MPU6050の疎通テストを行う。
    引数：
        なし
    戻り値：
        temp        温度
        accel_dict  加速度データ（辞書）
        gyro_dict   ジャイロデータ（辞書）
        magnet_dict 磁束密度データ（辞書）（ダミー）
    """
    mpu = _mpu6050()
    temp = mpu.get_temp()
    accel_dict = mpu.get_accel_data()
    gyro_dict = mpu.get_gyro_data()
    magnet_dict = {'x': None, 'y': None, 'z': None}
    return temp, accel_dict, gyro_dict, magnet_dict

def test_mpu9250():
    """
    MPU9250の疎通テストを行う。
    引数：
        なし
    戻り値：
        temp        温度
        accel_dict  加速度データ（辞書）
        gyro_dict   ジャイロデータ（辞書）
        magnet_dict 磁束密度データ（辞書）
    """
    mpu = _mpu9250()
    temp = mpu.readTemperature()
    accel_dict = mpu.readAccel()
    gyro_dict = mpu.readGyro()
    magnet_dict = mpu.readMagnet()
    mpu.close()
    return temp, accel_dict, gyro_dict, magnet_dict

if __name__ == "__main__":
    '''
    動作確認
    '''

    # MPU6050
    #temp, accel_dict, gyro_dict, magnet_dict = test_mpu6050()

    # MPU9250
    temp, accel_dict, gyro_dict, magnet_dict = test_mpu9250()


    print('Temp: {}'.format(str(temp)))
    print('Accel: ({}, {}, {})'.format(
        str(accel_dict['x']), str(accel_dict['y']), str(accel_dict['z'])))
    print('Gyro: ({}, {}, {})'.format(
        str(gyro_dict['x']), str(gyro_dict['y']), str(gyro_dict['z'])))
    print('Magnet: ({}, {}, {})'.format(
        str(magnet_dict['x']), str(magnet_dict['y']), str(magnet_dict['z'])))

