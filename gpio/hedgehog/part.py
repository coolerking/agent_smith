# -*- coding: utf-8 -*-
"""
IMU搭載のMarvelmind モバイルビーコンをあらわすパーツクラス。
"""
from .marvelmind import MarvelmindHedge


class HedgeHogBase:
    """
    Marvelmind モバイルビーコン基底パーツクラス
    """
    def __init__(self, pi, hedge):
        """
        引数で与えられた情報をインスタンス変数に格納する。

        引数：
            pi      pigpio.pi() オブジェクト
            hedge   MarvlmindHedge オブジェクト
        戻り値：
            なし
        """
        self.pi = pi
        self.hedge = hedge

    def init_all(self):
        """
        すべての取得情報格納領域を初期化する。

        引数：
            なし
        戻り値：
            なし
        """
        self.init_usnav()
        self.init_imu()

    def init_imu(self):
        """
        IMU取得情報格納領域を初期化する。

        引数：
            なし
        戻り値：
            なし
        """
        self.x = None
        self.y = None
        self.z = None
        self.qw = None
        self.qx = None
        self.qy = None
        self.qz = None
        self.vx = None
        self.vy = None
        self.vz = None
        self.ax = None
        self.ay = None
        self.az = None
        #self.timestamp = None
    
    def init_usnav(self):
        """
        USNav取得情報格納領域を初期化する。

        引数：
            なし
        戻り値：
            なし
        """
        self.x_usnav = None
        self.y_usnav = None
        self.z_usnav = None
        #self.timestamp_usnav = None


    def run_all(self):
        """
        すべての取得情報を返却する。

        引数：
            なし
        戻り値：
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
        """
        return self.run_usnav(), self.run_imu()


    def run_imu(self):
        """
        IMU取得情報を返却する。

        引数：
            なし
        戻り値：
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
        """
        return self.x, self.y, self.z, \
            self.qw, self.qx, self.qy, self.qz, \
            self.vx, self.vy, self.vz, \
            self.ax, self.ay, self.az, #self.timestamp

    def run_usnav(self):
        """
        USNav取得情報を返却する。

        引数：
            なし
        戻り値：
            x_usnav     X軸座標 (USNav)
            y_usnav     Y軸座標 (USNav)
            z_usnav     Z軸座標 (USNav)
        """
        return self.x_usnav, self.y_usnav, self.z_usnav #, self.timestamp_usnav


    def updateUSNavData(self):
        """
        USNav コールバック関数、インスタンス変数に最新データを格納する。

        引数：
            なし
        戻り値：
            なし
        """
        # [usnAdr, usnX, usnY, usnZ, usnTimestamp]
        position = self.hedge.position()
        self.x_usnav = position[1]
        self.y_usnav = position[2]
        self.z_usnav = position[3]
        #self.timestamp_usnav = position[4]
    
    def updateAccData(self):
        """
        IMU コールバック関数、インスタンス変数に最新データを格納する。

        引数：
            なし
        戻り値：
            なし
        """
        # [x/1000.0, y/1000.0, z/1000.0, qw/10000.0, qx/10000.0, qy/10000.0, qz/10000.0, vx/1000.0, vy/1000.0, vz/1000.0, ax/1000.0,ay/1000.0,az/1000.0, timestamp]
        self.x = self.hedge.valuesImuData[-1][0]
        self.y = self.hedge.valuesImuData[-1][1]
        self.z = self.hedge.valuesImuData[-1][2]
        self.qw = self.hedge.valuesImuData[-1][3]
        self.qx = self.hedge.valuesImuData[-1][4]
        self.qy = self.hedge.valuesImuData[-1][5]
        self.qz = self.hedge.valuesImuData[-1][6]
        self.vx = self.hedge.valuesImuData[-1][7]
        self.vy = self.hedge.valuesImuData[-1][8]
        self.vz =self.hedge.valuesImuData[-1][9]
        self.ax = self.hedge.valuesImuData[-1][10]
        self.ay = self.hedge.valuesImuData[-1][11]
        self.az = self.hedge.valuesImuData[-1][12]
        #self.timestamp = self.hedge.valuesImuData[-1][13]

    def shutdown(self):
        """
        スレッドの無限ループを停止させる。

        引数：
            なし
        戻り値：
            なし
        """
        self.hedge.stop()

class HedgeHogIMU(HedgeHogBase):
    """
    IMU情報を取得するためのMarvelmind モバイルビーコンパーツクラス。
    """
    def __init__(self, pi, adr, tty='/dev/ttyACM0', baud=9600, debug=False):
        """
        IMU情報取得時コールバック関数を登録し、最新IMUデータを初期化する。

        引数：
            pi          pigpio.pi() オブジェクト
            adr         ヘッジホッグアドレス
            tty         シリアルポートキャラクタデバイスパス
            baud        ボーレート
            debug       デバッグフラグ
        戻り値：
            なし
        """
        super().__init__(pi, MarvelmindHedge(pi=pi, adr=adr, tty=tty, baud=baud,
            recieveUltrasoundPositionCallback=None, 
            recieveImuDataCallback = self.updateAccData, debug=debug))
        self.init_imu()

    def run(self):
        """
        IMU取得情報を返却する。

        引数：
            なし
        戻り値：
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
        """
        return self.run_imu()

    def shutdown(self):
        """
        IMU最新データ領域を初期化し、スレッドループへ停止を指示する。

        引数：
            なし
        戻り値：
            なし
        """
        self.init_imu()
        self.shutdown()

class HedgeHogUSNav(HedgeHogBase):
    """
    US Navコールバック関数を設定し、最新情報を取得する
    パーツクラスを提供する。
    """
    def __init__(self, pi, adr, tty='/dev/ttyACM0', baud=9600, debug=False):
        """
        Ultra Sonic Navigation情報取得時コールバック関数を登録し、
        最新データを初期化する。

        引数：
            pi          pigpio.pi() オブジェクト
            adr         ヘッジホッグアドレス
            tty         シリアルポートキャラクタデバイスパス
            baud        ボーレート
            debug       デバッグフラグ
        戻り値：
            なし
        """
        super().__init__(pi, MarvelmindHedge(pi=pi, adr=adr, tty=tty, baud=baud,
            recieveUltrasoundPositionCallback=self.updateUSNavData, 
            recieveImuDataCallback = None, debug=debug))
        self.init_usnav()

    def run(self):
        """
        USNav取得情報を返却する。

        引数：
            なし
        戻り値：
            x_usnav     X軸座標 (USNav)
            y_usnav     Y軸座標 (USNav)
            z_usnav     Z軸座標 (USNav)
        """
        return self.run_usnav()

    def shutdown(self):
        """
        USNav最新データ領域を初期化し、スレッドループへ停止を指示する。

        引数：
            なし
        戻り値：
            なし
        """
        self.init_usnav()
        self.shutdown()

class HedgeHog(HedgeHogBase):
    """
    IMU/US Nav両方ともコールバック関数を設定し、両方の最新情報を取得する
    パーツクラスを提供する。
    """
    def __init__(self, pi, adr, tty='/dev/ttyACM0', baud=9600, debug=False):
        """
        Ultra Sonic Navigation情報/IMU情報取得時コールバック関数をそれぞれ登録し、
        最新データを初期化する。

        引数：
            pi          pigpio.pi() オブジェクト
            adr         ヘッジホッグアドレス
            tty         シリアルポートキャラクタデバイスパス
            baud        ボーレート
            debug       デバッグフラグ
        戻り値：
            なし
        """
        super(pi, MarvelmindHedge(pi=pi, adr=adr, tty=tty, baud=baud,
            recieveUltrasoundPositionCallback=self.updateUSNavData, 
            recieveImuDataCallback = self.updateAccData, debug=debug))
        self.init_all()

    def run(self):
        """
        すべての取得情報を返却する。

        引数：
            なし
        戻り値：
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
        """
        return self.run_all()

    def shutdown(self):
        """
        最新データ領域を初期化し、スレッドループへ停止を指示する。

        引数：
            なし
        戻り値：
            なし
        """
        self.init_all()
        self.shutdown()