# -*- coding: utf-8 -*-
"""
Agent Jones用Tub操作関連パーツを提供する。

- TubWriter: Agent Jones 用Tubデータ書き込みクラス
- TubGroup: Agent Jones 用TubデータCopus化クラス
- TubPlayer: Agent Jones用Tubデータ再生クラス
- TubPrinter: Agent Jones用Tubデータ標準出力クラス
"""
import os
import numpy as np
import donkeycar as dk
from donkeycar.parts.datastore import TubGroup
from PIL import Image
from datetime import datetime
from .tub import Dir, MetaFile, RecordFile

# 運転モード取りうる値
USER_MODES = ['user', 'local']
# モータステータス取りうる値
MOTOR_STATUS = ['move', 'free', 'brake']
# モータステータスを使用しているレコードファイルのキー群
MOTOR_STATUS_KEYS = [
    'user/left/status',  'user/right/status',  #'user/lift/status',
    'local/left/status', 'local/right/status', #'local/lift/status'
]
# デフォルトモータ値/ステータス
DEFAULT_VALUE = 0.0
DEFAULT_STATUS = MOTOR_STATUS[1]

class TubPlayer:
    """
    Agent Jones用Tubデータ再生クラス。
    Tubディレクトリ内のデータをVehicleフレームワーク上のメモリへ順番に書き込むパーツクラス。
    """
    def __init__(self, tub_dir):
        """
        Tubディレクトリオブジェクトを生成し、インデックスを初期化する。
        引数
            tub_dir     Tubディレクトリへのパス
        戻り値
            なし
        """
        self.dir = Dir(tub_dir)
        self.index = 0
    
    def run(self):
        """
        Tubデータを連番昇順に１件読み込むジェネレータ関数。

        引数
            なし
        戻り値
            'cam/image_array'       イメージデータ(np.ndarray型式)
            'user/mode'             運転モード('user', 'local')
            'user/left/value'       左モータユーザ入力値
            'user/left/status'      左モータユーザ入力ステータス('move','free', 'brake') 
            'user/right/value'      右モータユーザ入力値
            'user/right/status'     右モータユーザ入力ステータス('move','free', 'brake') 
            'user/lift/value'       リフトモータユーザ入力値
            'user/lift/status'      リフトモータユーザ入力ステータス('move','free', 'brake') 
            'local/left/value'      左モータ自動運転側入力値
            'local/left/status'     左モータ自動運転側入力ステータス('move','free', 'brake') 
            'local/right/value'     右モータ自動運転側入力値
            'local/right/status'    右モータ自動運転側入力ステータス('move','free', 'brake') 
            'local/lift/value'      リフトモータ自動運転側入力値
            'local/lift/status'     リフトモータ自動運転側入力ステータス('move','free', 'brake') 
            'timestamp'             タイムスタンプ文字列
        例外
            StopIteration   Tubデータディレクトリパスの妥当性検査に失敗した場合
        """
        image_file, record_file = self.dir.indexOf(self.index)
        self.index += 1
        record_data = record_file.get_data()
        return image_file.get_data(), \
            record_data.get('user/mode', USER_MODES[0]), \
            record_data.get('user/left/value', DEFAULT_VALUE), \
            record_data.get('user/left/status', DEFAULT_STATUS), \
            record_data.get('user/right/value', DEFAULT_VALUE), \
            record_data.get('user/right/status', DEFAULT_STATUS), \
            record_data.get('user/lift/value', DEFAULT_VALUE), \
            record_data.get('user/lift/status', DEFAULT_STATUS), \
            record_data.get('local/left/value', DEFAULT_VALUE), \
            record_data.get('local/left/status', DEFAULT_STATUS), \
            record_data.get('local/right/value', DEFAULT_VALUE), \
            record_data.get('local/right/status', DEFAULT_STATUS), \
            record_data.get('local/lift/value', DEFAULT_VALUE), \
            record_data.get('local/lift/status', DEFAULT_STATUS), \
            record_data.get('timestamp', str(datetime.now()))
    
    def shutdown(self):
        """
        シャットダウン時処理。なにもしない。
        引数
            なし
        戻り値
            なし
        """
        pass

class TubWriter:
    """
    Agent Jones 用Tubデータ書き込みクラス。
    image_arrayはイメージファイルとして書き込み、
    recordデータはJSON型式でレコードファイルに書き出す。
    引数
        tub_dir     Tubディレクトリへのパス
    戻り値
        なし
    """
    def __init__(self, tub_dir):
        self.dir = Dir(tub_dir)
    
    def run(self, image_array, user_mode,
        user_left_value, user_left_status, 
        user_right_value, user_right_status, 
        user_lift_value, user_lift_status,
        local_left_value, local_left_status, 
        local_right_value, local_right_status, 
        local_lift_value, local_lift_status,
        timestamp):
        """
        Vehiecleフレームワーク上から取得したTunデータを表示する。

        引数
            image_array         イメージデータファイルベースネーム
            user_mode           運転モード('user', 'local')
            user_left_value     左モータユーザ入力値
            user_left_status    左モータユーザ入力ステータス('move','free', 'brake') 
            user_right_value    右モータユーザ入力値
            user_right_status   右モータユーザ入力ステータス('move','free', 'brake') 
            user_lift_value     リフトモータユーザ入力値
            user_lift_status    リフトモータユーザ入力ステータス('move','free', 'brake') 
            local_left_value    左モータ自動運転側入力値
            local_left_status   左モータ自動運転側入力ステータス('move','free', 'brake') 
            local_right_value   右モータ自動運転側入力値
            local_right_status  右モータ自動運転側入力ステータス('move','free', 'brake') 
            local_lift_value    リフトモータ自動運転側入力値
            local_lift_status   リフトモータ自動運転側入力ステータス('move','free', 'brake') 
            timestamp           タイムスタンプ文字列
        戻り値
            なし
        """
        # 'cam/image_array'は、ファイル名確定されるget_next()内で追加される
        record_data = {
            'user/mode':            user_mode,
            'user/left/value':      user_left_value,
            'user/left/status':     user_left_status,
            'user/right/value':     user_right_value,
            'user/right/status':    user_right_status,
            'user/lift/value':      user_lift_value,
            'user/lift/status':     user_lift_status,
            'local/left/value':     local_left_value,
            'local/left/status':    local_left_status,
            'local/right/value':    local_right_value,
            'local/right/status':   local_right_status,
            'local/lift/value':     local_lift_value,
            'local/lift/status':    local_lift_status,
            'timestamp':            timestamp
        }
        self.dir.get_next(image_array, record_data)
    
    def shutdown(self):
        """
        シャットダウン時処理。なにもしない。
        引数
            なし
        戻り値
            なし
        """
        pass

class TubPrinter:
    """
    Agent Jones用Tubデータ標準出力クラス。
    CSV型式で出力するパーツクラス。
    """
    def __init__(self):
        """
        ヘッダを表示する。

        引数
            なし
        戻り値
            なし
        """
        print('\"user/mode\", ' +
            '\"user/left/value\", \"user/left/status\", ' + 
            '\"user/right/value\", \"user/right/status\", ' + 
            '\"user/lift/value\", \"user/lift/status\"' +
            '\"local/left/value\", \"local/left/status\", ' + 
            '\"local/right/value\", \"local/right/status\", ' + 
            '\"local/lift/value\", \"local/lift/status\"' +
            '\"timestamp\"')

    def run(self, image_array, user_mode,
        user_left_value, user_left_status, 
        user_right_value, user_right_status, 
        user_lift_value, user_lift_status,
        local_left_value, local_left_status, 
        local_right_value, local_right_status, 
        local_lift_value, local_lift_status,
        timestamp):
        """
        Vehiecleフレームワーク上から取得したTunデータを表示する。

        引数
            image_array         イメージデータ（np.ndarray型式）
            user_mode           運転モード('user', 'local')
            user_left_value     左モータユーザ入力値
            user_left_status    左モータユーザ入力ステータス('move','free', 'brake') 
            user_right_value    右モータユーザ入力値
            user_right_status   右モータユーザ入力ステータス('move','free', 'brake') 
            user_lift_value     リフトモータユーザ入力値
            user_lift_status    リフトモータユーザ入力ステータス('move','free', 'brake') 
            local_left_value    左モータ自動運転側入力値
            local_left_status   左モータ自動運転側入力ステータス('move','free', 'brake') 
            local_right_value   右モータ自動運転側入力値
            local_right_status  右モータ自動運転側入力ステータス('move','free', 'brake') 
            local_lift_value    リフトモータ自動運転側入力値
            local_lift_status   リフトモータ自動運転側入力ステータス('move','free', 'brake') 
            timestamp           タイムスタンプ文字列
        戻り値
            なし
        """
        print('\"{}\", {}, \"{}\", {}, \"{}\", {}, \"{}\", {}, \"{}\", {}, \"{}\", {}, \"{}\", {}'.format(
            user_mode,
            str(user_left_value), user_left_status, str(user_right_value), user_right_status,
            str(user_lift_value), user_lift_status, str(local_left_value), local_left_status,
            str(local_right_value), local_right_status, str(local_lift_value), local_lift_status,
            timestamp
        ))

    def shutdown(self):
        """
        シャットダウン時処理。なにもしない。
        引数
            なし
        戻り値
            なし
        """
        pass

class AgentTubGroup(TubGroup):
    """
    Agent Jones用meta.jsonに新たに加わったタイプ"motor_status"に対応する
    ためにトレーニングデータ生成用クラスTubGroupをオーバライドしたクラス。
    """


    def put_record(self, data):
        """
        csvログに保存できない画像などの値を保存し、
        csvに保存できる保存値への参照を含むレコードを返す。
        モータステータスの場合、文字列などとおなじ扱いで操作するように
        オーバライドしている。

        引数
            data        保存対象データ
        戻り値
            なし
        例外
            TypeError   保存対象データに未知のタイプが含まれている場合
        """
        json_data = {}

        for key, val in data.items():
            typ = self.get_input_type(key)

            if typ in ['str', 'float', 'int', 'boolean', MetaFile.TYPE_MOTOR_STATUS]:
                json_data[key] = val

            elif typ is 'image':
                name = self.make_file_name(key, ext='.jpg')
                val.save(os.path.join(self.path, name))
                json_data[key] = name

            elif typ == 'image_array':
                img = Image.fromarray(np.uint8(val))
                name = self.make_file_name(key, ext='.jpg')
                img.save(os.path.join(self.path, name))
                json_data[key] = name

            else:
                msg = 'Tub does not know what to do with this type {}'.format(typ)
                raise TypeError(msg)

        self.write_json_record(json_data)
        self.current_ix += 1
        return self.current_ix

    def get_record_gen(self, record_transform=None, shuffle=True, df=None):
        """
        レコードデータを1件返却するジェネレータ関数。

        引数
            record_transform    辞書フォーマットのレコードデータを操作するマッピング関数。
            shuffle : bool
            Shuffle records
        df : numpy Dataframe
            If df is specified, the generator will use the records specified in that DataFrame. If None,
            the internal DataFrame will be used by calling get_df()

        Returns
        -------
        A dict with keys mapping to the specified keys, and values lists of size batch_size.

        See Also
        --------
        get_df
        """
        if df is None:
            df = self.get_df()

        while True:
            for _ in self.df.iterrows():
                if shuffle:
                    record_dict = df.sample(n=1).to_dict(orient='record')[0]

                record_dict = self.read_record(record_dict)

                if record_transform:
                    record_dict = record_transform(record_dict)

                for status_key in MOTOR_STATUS_KEYS:
                    status_val = record_dict[status_key]
                    if status_val is not None:
                        record_dict[status_key] = self.motor_status_to_list(status_val)
                    else:
                        raise ValueError('no key={} in loaded record'.format(status_key))
                yield record_dict

    def motor_status_to_list(self, val):
        classes = np.zeros(len(MOTOR_STATUS)).tolist()
        classes[MOTOR_STATUS.index(val)] = 1
        return classes

def agent_record_transform(record_dict):
    """
    TubGroupクラスのメソッドget_train_val_genの引数として渡し、
    Agent用Tubデータ仕様のものでも学習データ化できるようにする
    マッピング関数。

    引数
        record_dict     もとのレコードデータ（Agent用Tubデータ、辞書型）
    戻り値
        record_dict     AIのinput/output層にあったマッピングが終わったレコードデータ（辞書型）
    例外
        ValueError      モータステータスキーが１件も存在しない場合
    """
    for status_key in MOTOR_STATUS_KEYS:
        status_val = record_dict[status_key]
        if status_val is not None:
            record_dict[status_key] = motor_status_to_list(status_val)
        else:
            raise ValueError('no key={} in loaded record'.format(status_key))
    return record_dict

def motor_status_to_list(val):
    """
    モータステータス値を数値リスト化する。

    引数
        モータステータス値
    戻り値
        数値リスト
    """
    classes = np.zeros(len(MOTOR_STATUS)).tolist()
    classes[MOTOR_STATUS.index(val)] = 1
    return classes

def list_to_motor_status(classes):
    """
    モータステータス予測結果数値リストをモータステータス値に変換する。

    引数
        モータステータス予測結果数値リスト
    戻り値
        モータステータス値
    """
    return MOTOR_STATUS[np.argmax(classes)]