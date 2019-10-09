# -*- coding: utf-8 -*-
"""
Marvelmind社製モバイルビーコンを操作するDonkey Carパーツクラス。
Marvelmind社製モバイルビーコンをUSBケーブルで接続した状態であり、
Marvelmind社の提供するサンプルコード marvelmind.py が同じディレクトリに配置しないと動作しない。

- [marvelmind.py](https://github.com/MarvelmindRobotics/marvelmind.py)

なお、marvelmind.py はpyserial、crcmodという２つのpythonパッケージが前提となる。
"""
from .marvelmind import MarvelmindHedge

class HedgehogController:
    """
    Marvelmind側のコールバック機能を使用したモバイルビーコンデータ取得パーツクラス。
    """
    def __init__(self, tty='/dev/ttyACM0', adr=79, debug=False):
        """
        インスタンス変数を初期化し、Marvelmindスレッドを開始する。
        引数：
            tty             シリアルポートを表すキャラクタデバイスパス
            adr             ビーコン側アドレス(ID)
            debug           marvelmind.pyにてデバッグ出力するか
        戻り値：
            なし
        """
        if debug:
            print('[HedgehogController] __init__ called adr={}'.format(str(adr)))
        self.id = adr
        self.debug = debug
        self.init()
        self.hedge = MarvelmindHedge(
            adr=adr,
            tty=tty,
            recieveUltrasoundPositionCallback=self.usnav_callback,
            recieveImuRawDataCallback=self.imu_raw_callback,
            recieveImuDataCallback=self.imu_callback,
            recieveUltrasoundRawDataCallback=self.usnav_raw_callback,
            debug=debug) # Marvelmind側ログも出す場合
            #debug=False) # ログがうざい場合
        self.hedge.start()
        if self.debug:
            print('[HedgehogController] start marbelmind thread')

    def init(self):
        """
        位置情報を格納するインスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        self.usnav_id = self.id
        self.usnav_x = 0
        self.usnav_y = 0
        self.usnav_z = 0
        self.usnav_angle = 0
        self.usnav_timestamp = 0
        self.imu_x = 0
        self.imu_y = 0
        self.imu_z = 0
        self.imu_qw = 0
        self.imu_qx = 0
        self.imu_qy = 0
        self.imu_qz = 0
        self.imu_vx = 0
        self.imu_vy = 0
        self.imu_vz = 0
        self.imu_ax = 0
        self.imu_ay = 0
        self.imu_az = 0
        self.imu_gx = 0
        self.imu_gy = 0
        self.imu_gz = 0
        self.imu_mx = 0
        self.imu_my = 0
        self.imu_mz = 0
        self.imu_timestamp = 0
        self.dist_id = self.id
        self.dist_b1 = 0
        self.dist_b1d = 0
        self.dist_b2 = 0
        self.dist_b2d = 0
        self.dist_b3 = 0
        self.dist_b3d = 0
        self.dist_b4 = 0
        self.dist_b4d = 0
        self.dist_timestamp = 0
        if self.debug:
            print('[HedgehogController] init instance values')


    def usnav_callback(self):
        """
        位置情報をインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        # [usnAdr, usnX, usnY, usnZ, usnAngle, usnTimestamp]
        usnav = self.hedge.position()
        if self.debug:
            print('[HedgehogController] usnav data recieved')
            print(usnav)
        if usnav[0] != self.id:
            if self.debug:
                print('[HedgehogController] usnav data ignored id:{} is not {}'.format(
                    str(usnav[0]),
                    str(self.id)
                ))
        if isinstance(usnav, list) and len(usnav) == 6:
            self.usnav_id = usnav[0]
            self.usnav_x = usnav[1]
            self.usnav_y = usnav[2]
            self.usnav_z = usnav[3]
            self.usnav_angle = usnav[4]
            self.usnav_timestamp = usnav[5]/1000.0
            if self.debug:
                print('[HedgehogController] (x, y, z)=({}, {}, {}), angle={}, timestamp={}'.format(
                    str(self.usnav_x),
                    str(self.usnav_y),
                    str(self.usnav_z),
                    str(self.usnav_angle),
                    str(self.usnav_timestamp)
                ))
        else:
            if self.debug:
                print('[HedgehogController] usnav data ignored no match format')


    def imu_raw_callback(self):
        """
        加速度、ジャイロ、磁束密度を取得し、インスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        # [ax, ay, az, gx, gy, gz, mx, my, mz, timestamp]
        if self.debug:
            print('[HedgehogController] imu raw data recieved')
        values_raw_imu = getattr(self.hedge, 'valuesImuRawData', None)
        if values_raw_imu is None:
            if self.debug:
                print('[HedgehogController] imu raw data has no valuesImuRawData')
            return
        raw_imu = list(values_raw_imu)[-1]
        if raw_imu is None:
            if self.debug:
                print('[HedgehogController] imu raw data is None')
            return
        if self.debug:
            print(raw_imu)
        if len(raw_imu) == 10:
            self.imu_ax = raw_imu[0]
            self.imu_ay = raw_imu[1]
            self.imu_az = raw_imu[2]
            self.imu_gx = raw_imu[3]
            self.imu_gy = raw_imu[4]
            self.imu_gz = raw_imu[5]
            self.imu_mx = raw_imu[6]
            self.imu_my = raw_imu[7]
            self.imu_mz = raw_imu[8]
            self.imu_timestamp = raw_imu[9]
            if self.debug:
                print('[HedgehogController] (ax, ay, az) = ({}, {}, {}), timestamp={}'.format(
                    str(self.imu_ax),
                    str(self.imu_ay),
                    str(self.imu_az),
                    str(self.imu_timestamp)
                ))
                print('[HedgehogController] (gx, gy, gz) = ({}, {}, {})'.format(
                    str(self.imu_gx),
                    str(self.imu_gy),
                    str(self.imu_gz)
                ))
                print('[HedgehogController] (mx, my, mz) = ({}, {}, {})'.format(
                    str(self.imu_mx),
                    str(self.imu_my),
                    str(self.imu_mz)
                ))
            return
        if self.debug:
            print('[HedgehogController] no match format')

    def imu_callback(self):
        """
        IMUデータをインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        #  [x/1000.0, y/1000.0, z/1000.0,
        #   qw/10000.0, qx/10000.0, qy/10000.0, qz/10000.0,
        #   vx/1000.0, vy/1000.0, vz/1000.0,
        #   ax/1000.0,ay/1000.0,az/1000.0, timestamp]
        imu = list(self.hedge.valuesImuData)[-1]
        if self.debug:
            print('[HedgehogController] imu data recieved')
            print(imu)
        if isinstance(imu, list) and len(imu) == 14:
            self.imu_x = imu[0]
            self.imu_y = imu[1]
            self.imu_z = imu[2]
            self.imu_qw = imu[3]
            self.imu_qx = imu[4]
            self.imu_qy = imu[5]
            self.imu_qz = imu[6]
            self.imu_vx = imu[7]
            self.imu_vy = imu[8]
            self.imu_vz = imu[9]
            self.imu_ax = imu[10]
            self.imu_ay = imu[11]
            self.imu_az = imu[12]
            self.imu_timestamp = imu[13]
            if self.debug:
                print('[HedgehogController] (x, y, z) = ({}, {}, {})'.format(
                    str(self.imu_x),
                    str(self.imu_y),
                    str(self.imu_z)
                ))
                print('[HedgehogController] (qw, qx, qy, qz) = ({}, {}, {}, {})'.format(
                    str(self.imu_qw),
                    str(self.imu_qx),
                    str(self.imu_qy),
                    str(self.imu_qz)
                ))
                print('[HedgehogController] (vx, vy, vz) = ({}, {}, {})'.format(
                    str(self.imu_vx),
                    str(self.imu_vy),
                    str(self.imu_vz)
                ))
                print('[HedgehogController] (ax, ay, az) = ({}, {}, {}), timestamp={}'.format(
                    str(self.imu_ax),
                    str(self.imu_ay),
                    str(self.imu_az),
                    str(self.imu_timestamp)
                ))

    def usnav_raw_callback(self):
        """
        ビーコン間距離データをインスタンス変数へ格納する。
        引数： 
            なし
        戻り値：
            なし
        """
        # [HedgeAdr, b1, b1d/1000.0, b2, b2d/1000.0,
        #  b3, b3d/1000.0, b4, b4d/1000.0, timestamp]
        if self.hedge is None:
            print('self.hedge is None')
            return
        values_dist = getattr(self.hedge, 'valuesUltrasoundRawData', None)
        if values_dist is None:
            print('self.hedge has no valuesUltrasoundRawData')
            return
        dist = self.hedge.distances()
        if self.debug:
            print('[HedgehogController] usnav raw data(distances) recieved')
            print(dist)
        if len(dist) == 10 and dist[0] == self.id:
            self.dist_id = dist[0]
            self.dist_b1 = dist[1]
            self.dist_b1d = dist[2]
            self.dist_b2 = dist[3]
            self.dist_b2d = dist[4]
            self.dist_b3 = dist[5]
            self.dist_b3d = dist[6]
            self.dist_b4 = dist[7]
            self.dist_b4d = dist[8]
            self.dist_timestamp = dist[9]/1000.0
            if self.debug:
                print('[HedgehogController] Adr:{} B1:{}:{}, B2:{}:{}, B3:{},{}, B4:{},{}, t={}'.format(
                    str(self.dist_id),
                    str(self.dist_b1),
                    str(self.dist_b1d),
                    str(self.dist_b2),
                    str(self.dist_b2d),
                    str(self.dist_b3),
                    str(self.dist_b3d),
                    str(self.dist_b4),
                    str(self.dist_b4d),
                    str(self.dist_timestamp)
                ))
        else:
            if self.debug:
                print('[HedgehogController] usnav raw data ignored id:{} is not {} or len={}'.format(
                    str(dist[0]),
                    str(self.id),
                    str(len(dist))
                ))

    def update(self):
        """
        marvelmind側のスレッドを使用するため、処理なし。
        引数： 
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[HedgehogController] update called')

    def run(self):
        """
        インスタンス変数から最新データを取得する。
        ただし、実装はrun_threadedを呼び出しているだけ。
        引数：
            なし
        戻り値：
            usnav_id        ステーショナリビーコンのアドレス
            usnav_x         USNavより取得したX座標
            usnav_y         USNavより取得したY座標
            usnav_z         USNavより取得したZ座標
            usnav_angle     USNavより取得したアングル値
            usnav_timestamp USNav取得タイムスタンプ
            imu_x           IMUより取得したX座標
            imu_y           IMUより取得したX座標
            imu_z           IMUより取得したX座標
            imu_qw          IMUより取得した四元数qw
            imu_qx          IMUより取得した四元数qx
            imu_qy          IMUより取得した四元数qy
            imu_qz          IMUより取得した四元数qz
            imu_vx          IMUより取得した速度(X座標)
            imu_vy          IMUより取得した速度(Y座標)
            imu_vz          IMUより取得した速度(Z座標)
            imu_ax          IMUより取得した加速度(X座標)
            imu_ay          IMUより取得した加速度(Y座標)
            imu_az          IMUより取得した加速度(X座標)
            imu_mx          IMUより取得した磁力(X座標)
            imu_my          IMUより取得した磁力(Y座標)
            imu_mz          IMUより取得した磁力(Z座標)
            imu_timestamp   IMUより取得タイムスタンプ
            dist_id         モバイルビーコンのアドレス
            dist_b1         ステーショナリビーコン1のアドレス
            dist_b1d        ステーショナリビーコン1までの距離
            dist_b2         ステーショナリビーコン2のアドレス
            dist_b2d        ステーショナリビーコン2までの距離
            dist_b3         ステーショナリビーコン3のアドレス
            dist_b3d        ステーショナリビーコン3までの距離
            dist_b4         ステーショナリビーコン4のアドレス
            dist_b4d        ステーショナリビーコン4までの距離
            dist_timestamp  Distance取得タイムスタンプ
        """
        self.update()
        return self.run_threaded()

    def run_threaded(self):
        """
        インスタンス変数から最新データを取得する。
        引数：
            なし
        戻り値：
            usnav_id        ステーショナリビーコンのアドレス
            usnav_x         USNavより取得したX座標
            usnav_y         USNavより取得したY座標
            usnav_z         USNavより取得したZ座標
            usnav_angle     USNavより取得したアングル値
            usnav_timestamp USNav取得タイムスタンプ
            imu_x           IMUより取得したX座標
            imu_y           IMUより取得したX座標
            imu_z           IMUより取得したX座標
            imu_qw          IMUより取得した四元数qw
            imu_qx          IMUより取得した四元数qx
            imu_qy          IMUより取得した四元数qy
            imu_qz          IMUより取得した四元数qz
            imu_vx          IMUより取得した速度(X座標)
            imu_vy          IMUより取得した速度(Y座標)
            imu_vz          IMUより取得した速度(Z座標)
            imu_ax          IMUより取得した加速度(X座標)
            imu_ay          IMUより取得した加速度(Y座標)
            imu_az          IMUより取得した加速度(X座標)
            imu_mx          IMUより取得した磁力(X座標)
            imu_my          IMUより取得した磁力(Y座標)
            imu_mz          IMUより取得した磁力(Z座標)
            imu_timestamp   IMUより取得タイムスタンプ
            dist_id         モバイルビーコンのアドレス
            dist_b1         ステーショナリビーコン1のアドレス
            dist_b1d        ステーショナリビーコン1までの距離
            dist_b2         ステーショナリビーコン2のアドレス
            dist_b2d        ステーショナリビーコン2までの距離
            dist_b3         ステーショナリビーコン3のアドレス
            dist_b3d        ステーショナリビーコン3までの距離
            dist_b4         ステーショナリビーコン4のアドレス
            dist_b4d        ステーショナリビーコン4までの距離
            dist_timestamp  Distance取得タイムスタンプ
        """
        if self.debug:
            print('[HedgehogController] run_threaded called')
            print('dist_id={}, b1:{}, b1d:{}'.format(
                str(self.dist_id),
                str(self.dist_b1),
                str(self.dist_b1d)
            ))
        return  self.usnav_id, \
                self.usnav_x, \
                self.usnav_y, \
                self.usnav_z, \
                self.usnav_angle, \
                self.usnav_timestamp, \
                self.imu_x, \
                self.imu_y, \
                self.imu_z, \
                self.imu_qw, \
                self.imu_qx, \
                self.imu_qy, \
                self.imu_qz, \
                self.imu_vx, \
                self.imu_vy, \
                self.imu_vz, \
                self.imu_ax, \
                self.imu_ay, \
                self.imu_az, \
                self.imu_gx, \
                self.imu_gy, \
                self.imu_gz, \
                self.imu_mx, \
                self.imu_my, \
                self.imu_mz, \
                self.imu_timestamp, \
                self.dist_id, \
                self.dist_b1, \
                self.dist_b1d, \
                self.dist_b2, \
                self.dist_b2d, \
                self.dist_b3, \
                self.dist_b3d, \
                self.dist_b4, \
                self.dist_b4d, \
                self.dist_timestamp

    def shutdown(self):
        """
        Marvelmind側のスレッドを停止し、インスタンス変数を初期化する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            print('[HedgehogController] shutdown called')
        self.hedge.stop()
        self.hedge = None
        self.init()