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
    def __init__(self, tty="/dev/ttyACM0", adr=None, debug=False):
        """
        モバイルビーコンから常時データ収集を開始する。
        引数：
            tty             シリアルポートを表すキャラクタデバイスパス
            adr             ビーコン側アドレス(ID)
            debug           marvelmind.pyにてデバッグ出力するか
        戻り値：
            なし
        """
        self.hedge = MarvelmindHedge(tty, adr, debug)
        self.hedge.start()

    def run(self):
        """
        モバイルビーコンから最新の位置情報データを取得する。
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
            imu_ay          IMUより取得した加速度(X座標)
            imu_az          IMUより取得した加速度(X座標)
            dist_id         モバイルビーコンのアドレス
            dist_b1         ステーショナリビーコン1のアドレス
            dist_b1d        ステーショナリビーコン1までのアドレス
            dist_b2         ステーショナリビーコン2のアドレス
            dist_b2d        ステーショナリビーコン2までのアドレス
            dist_b3         ステーショナリビーコン3のアドレス
            dist_b3d        ステーショナリビーコン3までのアドレス
            dist_b4         ステーショナリビーコン4のアドレス
            dist_b4d        ステーショナリビーコン4までのアドレス
            dist_timestamp  Distance取得タイムスタンプ
        """
        usn = lambda:list(self.hedge.valuesUltrasoundPosition)[-1]
        imu = lambda:list(self.hedge.valuesImuData)[-1]
        dist = lambda:list(self.hedge.valuesUltrasoundRawData)[-1]
        return usn()[0], usn()[1], usn()[2], usn()[3], usn()[4], usn()[5], \
            imu()[0], imu()[1], imu()[2], \
            imu()[3], imu()[4], imu()[5], imu()[6], \
            imu()[7], imu()[8], imu()[9], imu()[10], imu()[11], imu()[12], \
            dist()[0], dist()[1], dist()[2], dist()[3], dist()[4], \
            dist()[5], dist()[6], dist()[7], dist()[8], dist()[9]

    def run_threaded(self):
        """
        スレッド実行時呼び出されるテンプレートメソッド。
        呼び出すと、必ず NotImplementedError を発生させる。
        引数：
            なし
        戻り値：
            なし
        """
        raise NotImplementedError('thread run not supported')

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
    imu_ax, imu_ay, imu_az, 
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
            imu_ay          IMUより取得した加速度(X座標)
            imu_az          IMUより取得した加速度(X座標)
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
        print('       V:({}, {}, {}), A:({}, {}, {})'.format(
            str(imu_vx), str(imu_vy), str(imu_vz),
            str(imu_ax), str(imu_ay), str(imu_az)))
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