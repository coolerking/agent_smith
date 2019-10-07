# -*- coding: utf-8 -*-
"""
Marvelmind社製モバイルビーコンを操作するDonkey Carパーツクラスおよびユーティリティ群モジュール。
Marvelmind社製モバイルビーコンをUSBケーブルで接続した状態であり、
Marvelmind社の提供するサンプルコード marvelmind.py が同じディレクトリに配置しないと動作しない。

- [marvelmind.py](https://github.com/MarvelmindRobotics/marvelmind.py)

なお、marvelmind.py はpyserial、crcmodという２つのpythonパッケージが前提となる。
"""
import os
from .marvelmind import MarvelmindHedge


class HedgeHogController:
    """
    Marvelmind社製モバイルビーコンからUSNav/IMUデータを取得し
    メモリへ書き出すパーツクラス。
    """
    def __init__(self, tty="/dev/ttyACM0", adr=79, debug=False):
        """
        モバイルビーコンから常時データ収集を開始する。
        引数：
            tty             シリアルポートを表すキャラクタデバイスパス
            adr             ビーコン側アドレス(ID)
            debug           marvelmind.pyにてデバッグ出力するか
        戻り値：
            なし
        """
        self.id = adr
        self.debug = debug
        self.init()
        self.hedge = MarvelmindHedge(adr=adr, tty=tty, debug=False)
        self.hedge.start()

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
        self.dist_id = 0
        self.dist_b1 = 0
        self.dist_b1d = 0
        self.dist_b2 = 0
        self.dist_b2d = 0
        self.dist_b3 = 0
        self.dist_b3d = 0
        self.dist_b4 = 0
        self.dist_b4d = 0
        self.dist_timestamp = 0

    def run(self):
        """
        インスタンス変数上の最新位置情報データを返却する。
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


    def update(self):
        """
        センサよりデータを取得しインスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.debug:
            self.hedge.print_position()
        usnav = self.hedge.position()
        if isinstance(usnav, list) and len(usnav) == 6 and usnav[0] == self.id:
            self.usnav_x = usnav[1]
            self.usnav_y = usnav[2]
            self.usnav_z = usnav[3]
            self.usnav_angle = usnav[4],
            self.usnav_timestamp = usnav[5]/1000.0
        if self.debug and self.hedge.valuesImuData is not None:
            print(self.hedge.valuesImuData)
        imu = list(self.hedge.valuesImuData)[-1]
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
            print('raw imu')
            print(self.hedge.valuesImuRawData)
        raw_imu = list(self.hedge.valuesImuRawData)[-1]
        if raw_imu is not None and len(raw_imu) == 10:
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
            self.hedge.print_distances()
        dist = self.hedge.distances()
        if dist is not None and len(dist) == 10:
            self.dist_id = dist[0]
            self.dist_b1 = dist[1]
            self.dist_b1d = dist[2]
            self.dist_b2 = dist[3]
            self.dist_b2d = dist[4]
            self.dist_b3 = dist[5]
            self.dist_b3d = dist[6]
            self.dist_b4 = dist[7]
            self.dist_b4d = dist[8]
            self.dist_timestamp = dist[9]


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
        #print('raw imu')
        #print(list(self.hedge.valuesImuRawData)[-1])
        print(self.hedge.distances())
        print(self.hedge.distances()[0])
        return self.usnav_id, self.usnav_x, self.usnav_y, self.usnav_z, \
            self.usnav_angle, self.usnav_timestamp, \
            self.imu_x, self.imu_y, self.imu_z, \
            self.imu_qw, self.imu_qx, self.imu_qy, self.imu_qz, \
            self.imu_vx, self.imu_vy, self.imu_vz, \
            self.imu_ax, self.imu_ay, self.imu_az, \
            self.imu_gx, self.imu_gy, self.imu_gz, \
            self.imu_mx, self.imu_my, self.imu_mz, \
            self.imu_timestamp, \
            self.dist_id, self.dist_b1, self.dist_b1d, self.dist_b2, self.dist_b2d, \
            self.dist_b3, self.dist_b3d, self.dist_b4, self.dist_b4d, \
            self.dist_timestamp

    def stop(self):
        """
        モバイルビーコンからデータ収集を停止する。
        引数：
            なし
        戻り値：
            なし
        """
        self.hedge.stop()

    def shutdown(self):
        """
        シャットダウン時呼び出されるメソッド。stopメソッドを呼び出す。
        引数：
            なし
        戻り値：
            なし
        """
        self.stop()
        self.hedge = None

class PrintHedgeHog:
    """
    モバイルビーコンから取得した主要なデータを出力するデバッグ用パーツクラス。
    """
    def run(self, usnav_id, usnav_x, usnav_y, usnav_z, usnav_angle, usnav_timestamp,
    imu_x, imu_y, imu_z, imu_qw, imu_qx, imu_qy, imu_qz, imu_vx, imu_vy, imu_vz,
    imu_ax, imu_ay, imu_az, imu_gx, imu_gy, imu_gz, imu_mx, imu_my, imu_mz, imu_timestamp,
    dist_id, dist_b1, dist_b1d, dist_b2, dist_b2d, dist_b3, dist_b3d, dist_b4, dist_b4d, 
    dist_timestamp):
        """
        モバイルビーコンから最新の位置情報データを出力する。
        引数：
            usnav_id        USNav取得元ステーショナリビーコンのアドレス
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
            imu_az          IMUより取得した加速度(Z座標)
            imu_mx          IMUより取得した磁力(X座標)
            imu_my          IMUより取得した磁力(Y座標)
            imu_mz          IMUより取得した磁力(Z座標)
            imu_timestamp   IMUより取得タイムスタンプ
            dist_id         Distanceを取得したモバイルビーコンのアドレス
            dist_b1         dist_b1dの対象ステーショナリビーコン
            dist_b1d        ステーショナリビーコンdist_b1までの距離
            dist_b1         dist_b1dの対象ステーショナリビーコン
            dist_b2d        ステーショナリビーコンdist_b2までの距離
            dist_b3         dist_b3dの対象ステーショナリビーコン
            dist_b3d        ステーショナリビーコンdist_b3までの距離
            dist_b4         dist_b4dの対象ステーショナリビーコン
            dist_b4d        ステーショナリビーコンdist_b4までの距離
            dist_timestamp  Distanceデータを取得したタイムスタンプ
        戻り値：
            なし
        """
        print('** Mobile Beacon ID[{}] **'.format(str(dist_id)))
        print('       P:({}, {}, {}) angle:{}, timestamp:{}'.format(
            str(usnav_x), str(usnav_y), str(usnav_z), 
            str(usnav_angle), str(usnav_timestamp)))
        print('       V:({}, {}, {}), A:({}, {}, {}), G({}, {}, {})'.format(
            str(imu_vx), str(imu_vy), str(imu_vz),
            str(imu_ax), str(imu_ay), str(imu_az),
            str(imu_gx), str(imu_gy), str(imu_gz)))
        print('       St-ID[{}]: distance:{}'.format(str(dist_b1), str(dist_b1d)))
        print('       St-ID[{}]: distance:{}'.format(str(dist_b2), str(dist_b2d)))
        print('       St-ID[{}]: distance:{}'.format(str(dist_b3), str(dist_b3d)))
        print('       St-ID[{}]: distance:{}'.format(str(dist_b4), str(dist_b4d)))


    def shutdown(self):
        """
        シャットダウン時処理、なにもしない。
        引数：
            なし
        戻り値：
            なし
        """
        pass