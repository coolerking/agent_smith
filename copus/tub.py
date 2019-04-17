# -*- coding: utf-8 -*-
"""
Agent Jones 用Tub構造をあらわすデータモデルクラス群

tub.Data インスタンスは tub.MetaFile 、 tub.ImageFiles 、 tub.RecordFiles 各々の
インスタンスを保持する。
tub.ImageFilesクラスは、tub.ImageFileインスタンスを管理し、
tub.RecordFilesクラスは、tub.RecordFileインスタンスを管理する。
"""
import os
import glob
import json
import donkeycar as dk

class Dir:
    """
    Tubディレクトリをあらわすクラス。
    """
    def __init__(self, path):
        """
        実行時点のTubディレクトリの状態をMetaFile、ImageFiles、RecordFilesを
        インスタンス変数に格納することであらわしている。

        引数
            path        Tubディレクトリへのパス
        戻り値
            なし
        例外
            IOError     RecordファイルとImageファイルの数があわない場合
        """
        self.path = path
        self.meta_file = MetaFile(path)
        self.image_files = ImageFiles(path)
        self.record_files = RecordFiles(path)
        if self.image_files.total() != self.record_files.total():
            raise IOError('no match image/record count in {}'.format(path))

    def total(self):
        """
        インスタンス生成時点のTubデータ件数を返却する。

        引数
            なし
        戻り値
            なし
        例外
            IOError     RecordファイルとImageファイルの数があわない場合     
        """
        image_total = self.image_files.total()
        if image_total != self.record_files.total():
            raise IOError('no match image/record count in {}'.format(self.path))
        return image_total

    def indexOf(self, index):
        """
        引数指定された連番のImageFileインスタンス、RecordFileインスタンスを取得する。

        引数
            index           取得したい連番
        戻り値
            image_file      ImageFileインスタンス
            record_file     RecordFileインスタンス
        戻り値
            StopIteration   引数に指定したindexが範囲外だった場合
        """
        if 0 <= index and index < self.total():
            image_file = self.image_files.indexOf(index)
            record_file = self.record_files.indexOf(index)
            return image_file, record_file
        else:
            raise StopIteration(
                'index={} is out of range({})'.format(str(index), str(self.total())))

    def get_next(self, image_data, record_data):
        """
        最新の連番がふられたイメージファイル、Recordファイルを作成し、各インスタンス
        を返却する。
        イメージファイルを作成した時点でファイル名が確定するため、Recordファイルに
        書き込まれる'cam/image_array'値をイメージファイルベース名に変換してファイル化
        している。

        引数
            image_data          イメージファイルデータ（np.ndarray型式）
            record_data         Recordファイルデータ（辞書型）
        戻り値
            next_image_file     新規作成されたImageFileインスタンス
            next_record_file    新規作成されたRecordFileインスタンス
        """
        next_image_file = self.image_files.get_next_image_file(image_data)
        record_data['cam/image_array'] = next_image_file.basename
        next_record_file = self.record_files.get_next_record_file(record_data)
        return next_image_file, next_record_file

class MetaFile:
    """
    meta.jsonをあらわすクラス。
    Tubディレクトリ内に１つだけ存在する。
    """
    # デフォルトベースファイル名
    NAME = 'meta.json'
    # モータステータスをあらわすtype名
    TYPE_MOTOR_STATUS = "motor_status"
    # デフォルトmeta.jsonに格納されているデータ（辞書型）
    DEFAULT_DATA = {
        "types":    [
            "image_array", "str", 
            "float", TYPE_MOTOR_STATUS, "float", TYPE_MOTOR_STATUS, 
            "float", TYPE_MOTOR_STATUS, 
            "float", TYPE_MOTOR_STATUS, "float", TYPE_MOTOR_STATUS, 
            "float", TYPE_MOTOR_STATUS,
            "str"
        ],
        "inputs":   [
            "cam/image_array",      "user/mode", 
            "user/left/value",      "user/left/status", 
            "user/right/value",     "user/right/status", 
            "user/lift/value",      "user/lift/status", 
            "local/left/value",     "local/left/status", 
            "local/right/value",    "local/right/status", 
            "local/lift/value",     "local/lift/status",
            "timestamp"
        ]
    }

    def __init__(self, dir_path):
        """
        meta.jsonが存在する場合読み込み、存在しない場合は作成する。

        引数
            dir_path    Tubディレクトリへのパス
        戻り値
            なし
        例外
            IOError     既存のmeta.jsonがファイルではない場合
        """
        self.dir_path = dir_path
        self.basenames = MetaFile.NAME
        path = self._get_full_path()
        if os.path.exists(path):
            if os.path.isfile(path):
                self.data = self.get_data()
            else:
                raise IOError('{} is not a file'.format(path))
        else:
            self.data = self.create()

    def get_data(self):
        """
        meta.jsonを読み込み、内容を辞書化して返却する。

        引数
            なし
        戻り値
            data    meta.jsonデータ（辞書型）
        """
        path = self._get_full_path()
        with open(path, 'r') as f:
            data =json.load(f)
        return data
    
    def create(self):
        """
        新規meta.jsonを作成する。

        引数
            なし
        戻り値
            datMetaFile.DEFAULT_DATA    meta.jsonデータ（辞書型）
        """
        path = self._get_full_path()
        with open(path, 'w') as f:
            json.dump(MetaFile.DEFAULT_DATA, f)
        return MetaFile.DEFAULT_DATA

    def _get_full_path(self):
        """
        meta.jsonファイルのフルパスを取得する。

        引数
            なし
        戻り値
            meta.jsonファイルのフルパス
        """
        return os.path.join(os.path.expanduser(self.dir_path), MetaFile.NAME)


class ImageFiles:
    """
    イメージファイルをあらわすクラス。
    """
    def __init__(self, dir_path):
        """
        Tubディレクトリパス、イメージファイルベース名をインスタンス変数へ格納する。

        引数
            dir_path        Tubディレクトリへのパス
        戻り値
            なし
        """
        self.dir_path = dir_path
        self.basenames = self._get_basenames()

    def _get_basenames(self):
        """
        Tubディレクトリ内のすべてのイメージファイルベース名のリストを
        昇順に並び替えて返却する。

        引数
            なし
        戻り値
            images  イメージファイルベース名のリスト（昇順）
        """
        _images = glob.glob(
            os.path.join(
                os.path.expanduser(self.dir_path),
                '*' + ImageFile.NAME_SUFFIX))
        if _images is None or len(_images) == 0:
            return []

        image_dict = {}
        for _image in _images:
            image = os.path.basename(_image)
            cnt = int(image.rsplit(ImageFile.NAME_SUFFIX)[0])
            image_dict[cnt] = image
        
        images = []
        sorted_image_keys = sorted(list(image_dict.keys()))
        for sorted_image_key in sorted_image_keys:
            images.append(image_dict[sorted_image_key])
        return images

    def total(self):
        """
        Tubディレクトリ上に存在するイメージファイルの件数を返却する。

        引数
            なし
        戻り値
            Tubディレクトリ上に存在するイメージファイルの件数
        """
        return len(self.basenames)
    
    def indexOf(self, index):
        """
        引数indexに指定された連番のイメージファイルインスタンスを取得する。

        引数
            index       取得対象の連番
        戻り値
            引数indexに指定された連番のイメージファイルインスタンス
        例外
            IndexError  引数indexが範囲外を指定した場合
        """
        if 0 <= index and index < self.total():
            return ImageFile(self.dir_path, self.basenames[index])
        else:
            raise IndexError(
                'index=\"{}\" is out of range({})'.format(
                    str(index), str(self.total())))

    def next_basename(self):
        """
        新たな連番をふったイメージファイルのベース名を取得する。
        
        引数
            なし
        戻り値
            next_bname  新たな連番をふったイメージファイルのベース名
        """
        next_bname = str(self.total()) + ImageFile.NAME_SUFFIX
        self.basenames.append(next_bname)
        return next_bname
    
    def get_next_image_file(self, data):
        """
        新たな連番をふったイメージファイルを作成し、ImageFileインスタンスを
        返却する。

        引数
            data        イメージファイルへ格納するデータ（np.ndarray型式）
        """
        next_image_file = ImageFile(self.dir_path, self.next_basename())
        next_image_file.set_data(data)
        return next_image_file

class ImageFile:
    """
    イメージファイルをあらわすクラス。
    """
    # イメージファイル名の末尾部分
    NAME_SUFFIX = '_cam-image_array_.jpg'
    def __init__(self, dir_path, basename):
        """
        Tubディレクトリパス、ベース名をインスタンス変数へ保管する。

        引数
            dir_path        Tubディレクトリへのパス
            basename        イメージファイルベースネーム
        戻り値
            なし
        例外
            IOError         引数basenameにイメージファイル末尾部分が存在しない場合
        """
        self.dir_path = dir_path
        if ImageFile.NAME_SUFFIX in basename:
            self.basename = basename
        else:
            raise IOError(
                'basename\"{}\" is not match tub format'.format(basename))
    
    def get_full_path(self):
        """
        イメージファイルのフルパスを返却する。

        引数
            なし
        戻り値
            イメージファイルのフルパス
        """
        return os.path.join(
            os.path.expanduser(self.dir_path), self.basename)

    def get_data(self):
        """
        イメージファイルを読み込み、バイナリをnp.ndarray型式に変換し返却する。

        引数
            なし
        戻り値
            イメージデータ（np.ndarray型式）
        """
        full_path = self.get_full_path()
        with open(full_path, 'br') as f:
            binary = f.read()
        return dk.util.img.img_to_arr(
            dk.util.img.binary_to_img(binary))
    
    def set_data(self, data):
        """
        イメージデータ（np.ndarray型式）をバイナリに変換しファイルへ書き込む。

        引数
            data    イメージデータ（np.ndarray型式）
        戻り値
            なし
        """
        full_path = self.get_full_path()
        binary = dk.util.img.arr_to_binary(data)
        with open(full_path, 'bw') as f:
            f.write(binary)

class RecordFiles:
    """
    Tubディレクトリ内のすべてのレコードファイルをあらわすクラス。
    """
    def __init__(self, dir_path):
        """
        Tubディレクトリパスをインスタンス変数へ格納し、Tubディレクトリ内の
        すべてのレコードファイル名を読み込みそのベース名リストをインスタンス
        変数に格納する。

        引数
            dir_path    Tubディレクトリパス
        戻り値
            なし
        """
        self.dir_path = dir_path
        self.basenames = self.get_records()
    
    def get_records(self):
        """
        Tubディレクトリ内のすべてのレコードファイル名を読み込みそのベース名
        リストを返却する。

        引数
            なし
        戻り値
            Recordファイルベース名リスト
        """
        _records = glob.glob(
            os.path.join(
                os.path.expanduser(self.dir_path),
                RecordFile.NAME_PREFIX + '*' + 
                RecordFile.NAME_SUFFIX))
        if _records is None or len(_records) == 0:
            return []

        record_dict = {}
        for _record in _records:
            record = os.path.basename(_record)
            cnt = int(
                record.rsplit(
                    RecordFile.NAME_PREFIX)[-1].rsplit(
                        RecordFile.NAME_SUFFIX)[0])
            record_dict[cnt] = record
        
        records = []
        sorted_record_keys = sorted(list(record_dict.keys()))
        for sorted_record_key in sorted_record_keys:
            records.append(record_dict[sorted_record_key])
        return records
    
    def total(self):
        """
        インスタンス作成時に読み込んだレコードファイル件数を返却する。

        引数
            なし
        戻り値
            インスタンス作成時に読み込んだレコードファイル件数
        """
        return len(self.basenames)

    def indexOf(self, index):
        """
        引数indexに合致する連番のRecordFileインスタンスを返却する。

        引数
            index       取得したいレコードファイルの連番
        戻り値
            RecordFile  RecordFileインスタンス
        例外
            IndexError  引数indexが範囲外だった場合
        """
        if 0 <= index and index < self.total():
            return RecordFile(self.dir_path, self.basenames[index])
        else:
            raise IndexError(
                'index=\"{}\" is out of range({})'.format(
                    str(index), str(self.total())))

    def next_basename(self):
        """
        読み込んだレコードファイルの次の連番のベース名を返却する。
        本メソッドを呼び出した段階では、ファイルは存在しない。
        ただしself.basenamesには追加される。

        引数
            なし
        戻り値
            次の連番がふられたレコードファイルベース名
        """
        next_bname = RecordFile.NAME_PREFIX + \
            str(self.total()) + RecordFile.NAME_SUFFIX
        self.basenames.append(next_bname)
        return next_bname

    def get_next_record_file(self, data):
        """
        次の連番がふられたレコードファイルを作成し、引数dataで渡された
        辞書データをJSON型式で格納する。

        引数
            data                レコードファイルデータ（辞書型）
        戻り値
            next_record_file    RecordFileインスタンス
        """
        next_record_file = RecordFile(
            self.dir_path, self.next_basename())
        next_record_file.set_data(data)
        return next_record_file

class RecordFile:
    """
    レコードファイルをあらわすクラス。
    """
    # レコードファイルベース名先頭部分
    NAME_PREFIX = 'record_'
    # レコードファイルベース名末尾部分
    NAME_SUFFIX = '.json'
    def __init__(self, dir_path, basename):
        """
        Tubディレクトリパス、ベース名をインスタンス変数へ格納する。

        引数
            dir_path        Tubディレクトリパス
            basename        レコードファイルベース名
        戻り値
            なし
        例外
            IOError         引数basenameの先頭文字列末尾文字列が仕様どおりではない場合
        """
        self.dir_path = dir_path
        if RecordFile.NAME_PREFIX in basename and \
            RecordFile.NAME_SUFFIX in basename:
            self.basename = basename
        else:
            raise IOError(
                'basename\"{}\" is not match tub format'.format(
                    basename))
    
    def get_full_path(self):
        """
        レコードファイルのフルパスを返却する。

        引数
            なし
        戻り値
            レコードファイルのフルパス
        """
        return os.path.join(
            os.path.expanduser(self.dir_path), self.basename)
    
    def get_data(self):
        """
        レコードファイルを読み込み、データを辞書化して返却する。

        引数
            なし
        戻り値
            data    レコードデータ（辞書型）
        """
        full_path = self.get_full_path()
        with open(full_path, 'r') as f:
            data = json.load(f)
        return data
    
    def set_data(self, data):
        """
        引数で渡された辞書dataをレコードファイルへJSON型式で書き込む。

        引数
            data    レコードデータ（辞書型）
        戻り値
            なし
        """
        full_path = self.get_full_path()
        with open(full_path, 'w') as f:
            json.dump(data, f)