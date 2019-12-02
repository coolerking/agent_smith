# -*- coding: utf-8 -*-
"""
Tubディレクトリ上のTubデータを連番の昇順にVehicleフレームワーク上のメモリへ
展開する Donkey パーツ TubLoader を提供する。
また、Vehicleフレームワーク上のメモリデータの運転情報部分をCSV型式で標準出力へ
表示する Donkey パーツ TubPrinter を提供する。
"""
import time
from .data import Tubs

class Loader:
    def __init__(self, tub_dir, repeat=False):
        """
        Tubデータを連番昇順に取得するTubsオブジェクトを生成し、
        インスタンス変数へ格納する。

        引数
            tub_dir         Tubデータディレクトリのパス
        戻り値
            なし
        例外
            Tubディレクトリパスの妥当性検査に不合格の場合
        """
        self.tubs = Tubs(tub_dir)
        if self.tubs.total() <= 0:
            exit('No data in {}'.format(tub_dir))
        #print(tub_dir)
        self.repeat = repeat
        self.index = 0
    
    def run(self):
        """
        Tubデータを連番昇順に１件読み込むジェネレータ関数。

        引数
            なし
        戻り値
            image                イメージデータ（バイナリ）
            user_mode           運転モード
            user_angle          手動操作のアングル値
            user_throttle       手動操作のスロットル値
            user_lift_throttle  手動操作のリフトスロットル値
            pilot_angle         オートパイロットのアングル値
            pilot_throttle      オートパイロットのスロットル値
            pilot_lift_throttle オートパイロットのリフトスロットル値
            timestamp           タイムスタンプ
        例外
            StopIteration   Tubデータディレクトリパスの妥当性検査に失敗した場合
        """
        total = self.tubs.total()
        #print(total)
        #print(self.index)
        if self.index < total:
            r, i = self.tubs.indexOf(self.index)
            user_mode = r.get('user/mode', 'user')
            user_angle = r.get('user/angle', 0.0)
            user_throttle = r.get('user/throttle', 0.0)
            user_lift_throttle = r.get('user/lift_throttle', 0.0)
            pilot_angle = r.get('pilot/angle', 0.0)
            pilot_throttle = r.get('pilot/throttle', 0.0)
            pilot_lift_throttle = r.get('pilot/lift_throttle', 0.0)
            timestamp = r.get('timestamp', float(time.time()))
            self.index += 1
            return i, user_mode, user_angle, user_throttle, user_lift_throttle, \
                pilot_angle, pilot_throttle, pilot_lift_throttle, timestamp
        elif self.index >= total and self.repeat:
            self.index = 0
            return self.run()
        else:
            raise StopIteration()
    
    def shutdown(self):
        self.tubs = None
        self.index = 0
        self.repeat = False

class UserLoader(Loader):
    def run(self):
        """
        Tubデータを連番昇順に１件読み込むジェネレータ関数。

        引数
            なし
        戻り値
            user_mode           運転モード
            user_angle          手動操作のアングル値
            user_throttle       手動操作のスロットル値
            user_lift_throttle  手動操作のリフトスロットル値
            timestamp           タイムスタンプ
        例外
            StopIteration   Tubデータディレクトリパスの妥当性検査に失敗した場合
        """
        
        _, user_mode, \
        user_angle, user_throttle, user_lift_throttle, \
        _, _, _, timestamp = super().run()
        return user_mode, \
            user_angle, user_throttle, user_lift_throttle, \
            timestamp

class ImageLoader(Loader):
    def run(self):
        """
        Tubデータを連番昇順に１件読み込むジェネレータ関数。

        引数
            なし
        戻り値
            image                イメージデータ（バイナリ）
        例外
            StopIteration   Tubデータディレクトリパスの妥当性検査に失敗した場合
        """
        i, _, _, _, _, _, _, _, _ = super().run()
        return i

