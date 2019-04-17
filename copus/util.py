# -*- coding: utf-8 -*-
"""
Agent Jones 用TubReaderのダミークラス。
テスト用学習データ作成などに利用するユーティリティとして使用可能。
"""
import os
import glob
import random
from datetime import datetime
from .part import USER_MODES, MOTOR_STATUS
from .tub import ImageFile

class DummyTubReader:
    """
    ダミーTubデータをVehicleフレームワーク上に提供するパーツクラス。
    """
    def __init__(self, tub_dir='copus/images'):
        """
        ダミーイメージファイル群が格納されているディレクトリパスをインスタンス変数へ格納し、
        ダミーイメージファイルのベース名をすべて取得しインスタンス変数へ格納する。

        引数
            tub_dir     ダミーイメージファイル群が格納されたディレクトリへのパス
        """
        if tub_dir is None:
            raise ValueError('no tub_dir')
        self.tub_dir = os.path.expanduser(tub_dir)
        if not os.path.exists(self.tub_dir) or not os.path.isdir(self.tub_dir):
                raise IOError('\"{}\" is not a directory'.format(str(self.tub_dir)))
        self.dummy_images = glob.glob(os.path.join(self.tub_dir, 
        DummyImageFile.NAME_PREFIX + '*' + DummyImageFile.NAME_SUFFIX))

    def get_dummy_status(self):
        """
        ランダムにモータステータスを選択して返却する。

        引数
            なし
        戻り値
            ランダムなモータステータス("move", "free", "brake")
        """
        return MOTOR_STATUS[random.randrange(len(MOTOR_STATUS))]
    
    def get_dummy_user_mode(self):
        """
        ランダムに運転モードを選択する。

        引数
            なし
        戻り値
            ランダムな運転モード（"user", "local"）
        """
        return USER_MODES[random.randrange(len(USER_MODES))]
    
    def get_dummy_value(self):
        """
        ランダムにモータ値を選択して返却する。

        引数
            なし
        戻り値
            ランダムなモータ値（-1.0～1.0）
        """
        return random.uniform(-1.0, 1.0)

    def get_dummy_record(self):
        """
        ランダムなレコードデータを返却する。

        引数
            なし
        戻り値
            'user/mode'         運転モード
            'user/left/value'   左モータ値（手動運転）
            'user/left/status'  左モータステータス（手動運転）
            'user/right/value'  右モータ値（手動運転）
            'user/right/status' 右モータステータス（手動運転）
            'user/lift/value'   リフトモータ値（手動運転）
            'user/lift/status'  リフトモータステータス（手動運転）
            'local/left/value'  左モータ値（自動運転）
            'local/left/status' 左モータステータス（自動運転）
            'local/right/value' 右モータ値（自動運転）
            'local/right/status'右モータステータス（自動運転）
            'local/lift/value'  リフトモータ値（自動運転）
            'local/lift/status' リフトモータステータス（自動運転）
            'timestamp'         時刻文字列（本メソッド呼び出し時刻）
        """
        return self.get_dummy_user_mode(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            str(datetime.now())
    
    def get_dummy_image(self):
        """
        ダミーイメージデータ（np.ndarray型式）を取得する。
        複数のダミーイメージファイルの中からランダムに１ファイル選択し、
        このデータを読み込みダミーイメージとして使用する。

        引数
            なし
        戻り値
            ダミーイメージデータ（np.ndarray型式）
        """
        index = str(random.randrange(len(self.dummy_images)))
        image_file = DummyImageFile(
            self.tub_dir, DummyImageFile.NAME_PREFIX + index + DummyImageFile.NAME_SUFFIX)
        return image_file.get_data()
    
    def run(self):
        """
        ランダムなTubデータを返却する。

        引数
            なし
        戻り値
            'cam/image_array'   イメージデータ（np.ndarray型式）
            'user/mode'         運転モード
            'user/left/value'   左モータ値（手動運転）
            'user/left/status'  左モータステータス（手動運転）
            'user/right/value'  右モータ値（手動運転）
            'user/right/status' 右モータステータス（手動運転）
            'user/lift/value'   リフトモータ値（手動運転）
            'user/lift/status'  リフトモータステータス（手動運転）
            'local/left/value'  左モータ値（自動運転）
            'local/left/status' 左モータステータス（自動運転）
            'local/right/value' 右モータ値（自動運転）
            'local/right/status'右モータステータス（自動運転）
            'local/lift/value'  リフトモータ値（自動運転）
            'local/lift/status' リフトモータステータス（自動運転）
            'timestamp'         時刻文字列（本メソッド呼び出し時刻）
        """
        return self.get_dummy_image(), \
            self.get_dummy_user_mode(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            self.get_dummy_value(), \
            self.get_dummy_status(), \
            str(datetime.now())

    def shutdown(self):
        """
        シャットダウン時処理、なにもしない。

        引数
            なし
        戻り値
            なし
        """
        pass

class DummyPiCamera:
    """
    PiCameraのない環境でも動作するダミーパーツクラス。
    """
    def __init__(self, tub_dir='tub'):
        """
        ダミーイメージファイル群が格納されているディレクトリパスをインスタンス変数へ格納し、
        ダミーイメージファイルのベース名をすべて取得しインスタンス変数へ格納する。

        引数
            tub_dir     ダミーイメージファイル群が格納されたディレクトリへのパス
        """
        if tub_dir is None:
            raise ValueError('no tub_dir')
        self.tub_dir = os.path.expanduser(tub_dir)
        if not os.path.exists(self.tub_dir) or not os.path.isdir(self.tub_dir):
                raise IOError('\"{}\" is not a directory'.format(str(self.tub_dir)))
        self.dummy_images = glob.glob(os.path.join(self.tub_dir, '*_cam-image_array_.jpg'))
    
    def run(self):
        """
        ランダムなTubデータを返却する。

        引数
            なし
        戻り値
            'cam/image_array'   イメージデータ（np.ndarray型式）
        """
        return self.get_dummy_image()
    
    def shutdown(self):
        pass
    
    def get_dummy_image(self):
        """
        ダミーイメージデータ（np.ndarray型式）を取得する。
        複数のダミーイメージファイルの中からランダムに１ファイル選択し、
        このデータを読み込みダミーイメージとして使用する。

        引数
            なし
        戻り値
            ダミーイメージデータ（np.ndarray型式）
        """
        index = str(random.randrange(len(self.dummy_images)))
        image_file = ImageFile(
            self.tub_dir, index + '_cam-image_array_.jpg')
        return image_file.get_data()

class DummyImageFile(ImageFile):
    """
    ダミー用イメージファイルを表すクラス。
    ダミーイメージファイルはTubイメージファイルとは異なるファイル名で
    格納されている（dummy連番.jpg）ため、ImageFileクラスを継承し
    仕様が異なる部分をオーバライドしている。
    """
    # ダミーイメージファイル先頭文字列
    NAME_PREFIX = 'dummy'
    # ダミーイメージファイル末尾文字列
    NAME_SUFFIX = '.jpg'
    def __init__(self, dir_path, basename):
        """
        ダミーイメージファイルが格納されているディレクトリパス、
        ダミーイメージファイルベース名をインスタンス変数として格納する。

        引数
            dir_path        ダミーイメージファイル格納ディレクトリパス
            basename        ダミーイメージファイルベース名
        戻り値
            なし
        例外
            IOError         ダミーイメージファイルフォーマットと異なる場合
        """
        self.dir_path = dir_path
        if DummyImageFile.NAME_PREFIX in basename and \
            DummyImageFile.NAME_SUFFIX in basename:
            self.basename = basename
        else:
            raise IOError(
                'basename\"{}\" is not match tub format'.format(
                    basename))


