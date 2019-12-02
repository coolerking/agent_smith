# -*- coding: utf-8 -*-
"""
Tubデータ上のオブジェクトをあらわすクラス群。
part.pyが使用する。
"""
import os
import glob
import json
import time

try:
    import donkeycar as dk
except ImportError:
    exit('This code requires donkeycar package.')

class Tubs:
    """
    1つのインスタンスで1つのTubデータディレクトリをあらわすクラス。
    連番の昇順に送信データを生成するジェネレータとして機能する。
    """
    def __init__(self, tub_dir):
        """
        引数指定先Tubデータディレクトリの妥当性を検査し、連番の昇順にファイルパスを
        ならべなおし、recordファイル、imageファイル別のリスト（インスタンス変数）へ格納する。

        引数
            tub_dir     Tubデータディレクトリのパス
        戻り値
            なし
        例外
            妥当性検査に不合格の場合
        """
        if tub_dir is None:
            raise Exception('no tub_dir')
        self.tub_dir = os.path.expanduser(tub_dir)
        if not os.path.exists(self.tub_dir):
            raise Exception('{} is not exists'.format(self.tub_dir))
        if not os.path.isdir(self.tub_dir):
            raise Exception('{} is not a directory'.format(self.tub_dir))
        
        records = glob.glob(os.path.join(self.tub_dir, 'record_*.json'))
        #print(records)
        images = glob.glob(os.path.join(self.tub_dir, '*_cam-image_array_.jpg'))

        record_dict = {}
        for record in records:
            cnt = int(record.rsplit('record_')[-1].rsplit('.json')[0])
            record_dict[cnt] = record
        
        self.sorted_records = []
        sorted_record_keys = sorted(list(record_dict.keys()))
        for sorted_record_key in sorted_record_keys:
            self.sorted_records.append(record_dict[sorted_record_key])
        
        image_dict = {}
        for image in images:
            cnt = int(os.path.basename(image).rsplit('_cam-image_array_.jpg')[0])
            image_dict[cnt] = image
        
        self.sorted_images = []
        sorted_image_keys = sorted(list(image_dict.keys()))
        for sorted_image_key in sorted_image_keys:
            self.sorted_images.append(image_dict[sorted_image_key])

        if sorted_record_keys != sorted_image_keys:
            raise Exception('unmatch magic numner no_records={}, no_images={}'.format(
                str(sorted_record_keys - sorted_image_keys), str(sorted_image_keys - sorted_record_keys)
            ))
    
    def total(self):
        return len(self.sorted_records)
    
    def indexOf(self, index):
        record = TubRecord(self.sorted_records[index]).get()
        image = TubImage(self.sorted_images[index]).get()
        return record, image

class Tub:
    """
    Tubデータ操作のユーティリティを提供する基底クラス。
    """
    def eval_file(self, path):
        """
        引数pathにて指定されたパスがファイルであるかどうかを確認する。

        引数
            path    検査対象のパス
        戻り値
            検査対象のパス（ユーザ短縮を使用している場合展開）
        例外
            ファイルではない場合、発生させる
        """
        if path is None:
            raise Exception('no record_path')
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            raise Exception('{} is not exists'.format(path))
        if not os.path.isfile(path):
            raise Exception('{} is not a file'.format(path))
        return path

class TubRecord(Tub):
    """
    １インスタンスで１つのrecordファイルをあらすクラス。
    """
    def __init__(self, path):
        """
        JSONファイルを読み込み辞書型に変換しインスタンス変数へ格納する。

        引数
            path    JSONファイルのパス
        戻り値
            なし
        例外
            引数指定パスがファイルではない場合
        """
        with open(self.eval_file(path), 'r') as f:
            self.record = json.load(f)

    def get(self, use_timestamp = False):
        """
        送信用JSONデータを作成する。

        引数
            use_timestamp   オリジナルのタイムスタンプを送信する：真、現在時刻を使用する：偽
        戻り値
            送信用JSONデータ（辞書型）
        """
        if 'pilot/angle' not in self.record:
            self.record['pilot/angle'] = 0.0
        if 'pilot/throttle' not in self.record:
            if self.record['user/mode'] == 'local_angle':
                self.record['pilot/throttle'] = 0.5
            else:
                self.record['pilot/throttle'] = 0.0

        if self.record['user/mode'] == 'user':
            if 'angle' not in self.record:
                self.record['angle'] = self.record['user/angle']
            if 'throttle' not in self.record:
                self.record['throttle'] = self.record['user/throttle']
        elif self.record['user/mode'] == 'local_angle':
            if 'angle' not in self.record:
                self.record['angle'] = self.record['pilot/angle']
            if 'throttle' not in self.record:
                self.record['throttle'] = self.record['user/throttle']
        else:
            if 'angle' not in self.record:
                self.record['angle'] = self.record['pilot/angle']
            if 'throttle' not in self.record:
                self.record['throttle'] = self.record['pilot/throttle']

        if use_timestamp and 'timestamp' not in self.record:
            self.record['timestamp'] = float(time.time())

        return self.record

class TubImage(Tub):
    """
    １インスタンスで１つのイメージファイルをあらすクラス。
    """
    def __init__(self, path):
        """
        イメージファイルを読み込みPiCamera出力に合わせて型式を
        np.ndarray型(120, 160,3)に変換しインスタンス変数へ格納する。

        引数
            path    イメージファイルのパス
        戻り値
            なし
        例外
            引数指定パスがファイルではない場合
        """
        with open(self.eval_file(path), 'br') as f:
            binary = f.read()
        img = dk.utils.binary_to_img(binary)
        self.image_array = dk.utils.img_to_arr(img)

    def get(self):
        """
        イメージデータ(np.ndarray, dtype=uint8, shape=(120,160,3))を返却する

        引数
            なし
        戻り値
            self.image_array    イメージデータ(np.ndarray, dtype=uint8, shape=(120,160,3))
        """
        return self.image_array


