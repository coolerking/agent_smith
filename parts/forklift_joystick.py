# -*- coding: utf-8 -*-
"""
フォークリフトを操作するための以下のジョイスティックパーツを提供するモジュール。

* Logicool F710
* ELECOM JC-U4113S (X-Box互換モードのみ)

またジョイスティックパーツオブジェクトを返却するファクトリを
ラップした関数も提供する。
"""
from donkeycar.parts.controller import Joystick, JoystickController

class ForkliftJoystickController(JoystickController):
    """
    フォークリフト操作用JoystickController基底パーツクラス。
    フォークリフトを操作をマッピングするための関数群を定義。
    """
    def __init__(self,
    poll_delay=0.0,
    throttle_scale=1.0,
    steering_scale=1.0,
    lift_throttle_scale=1.0,
    throttle_dir=-1.0,
    lift_throttle_dir=-1.0,
    dev_fn='/dev/input/js0',
    auto_record_on_throttle=True):
        """
        ぴゃクラスの初期化処理を実行し、
        フォークリフト追加（リフトスロットル操作）機能の初期化を行う。
        引数：
            poll_delay                  pollingのdelay値
            throttle_scale              スロットル値のスケール
            sttering_scale              ステアリング値のスケール
            lift_throttle_scale         リフト値のスケール
            throttle_dir                スロットル値方向変換用：スロットル地に掛ける
            lift_throttle_dir           リフト値方向変換用：リフト値に掛ける
            dev_fn                      キャラクタデバイスファイルパス
            auto_record_on_throttle     スロットルON時自動記録するかどうか（真偽値）
        戻り値：
            なし
        """
        super().__init__(poll_delay, 
        throttle_scale, steering_scale, throttle_dir, dev_fn, auto_record_on_throttle)
        self.lift_throttle = 0.0
        self.lift_throttle_scale = lift_throttle_scale
        self.lift_throttle_dir = lift_throttle_dir
        self.last_lift_throttle_axis_val = 0
        self.constant_lift_throttle = False

    def on_throttle_changes(self):
        '''
        手動運転時リフトスロットル値がゼロではない場合、記録モードをONにする。
        引数：
            なし
        戻り値：
            なし
        '''
        if self.auto_record_on_throttle:
            self.recording = ((abs(self.throttle) > self.dead_zone or abs(self.lift_throttle) > self.dead_zone) and self.mode == 'user')

    def emergency_stop(self):
        """
        緊急停止する。
        引数：
            なし
        戻り値：
            なし
        """
        super().emergency_stop()
        self.lift_throttle = 0.0

    def set_lift_throttle(self, axis_val):
        """
        リフトスロットル値を設定する。
        引数：
            axis_val       リフトスロットル値
        戻り値：
            なし
        """
        #this value is often reversed, with positive value when pulling down
        self.last_lift_throttle_axis_val = axis_val
        self.lift_throttle = (self.lift_throttle_dir * axis_val * self.lift_throttle_scale)
        #print("throttle", self.throttle)
        self.on_throttle_changes()

    def increase_max_lift_throttle(self):
        '''
        リフト最高速を上げる。
        引数：
            なし
        戻り値：
            なし
        '''
        self.lift_throttle_scale = round(min(1.0, self.lift_throttle_scale + 0.01), 2)
        if self.constant_lift_throttle:
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        else:
            self.lift_throttle = (self.lift_throttle_dir * self.last_lift_throttle_axis_val * self.lift_throttle_scale)

        print('lift_throttle_scale:', self.lift_throttle_scale)

    def increase_max(self):
        """
        最高速を上げる。
        引数：
            なし
        戻り値：
            なし
        """
        super().increase_max_throttle()
        self.increase_max_lift_throttle()

    def decrease_max_lift_throttle(self):
        '''
        リフト最高速を下げる。
        引数：
            なし
        戻り値：
            なし
        '''
        self.lift_throttle_scale = round(max(0.0, self.lift_throttle_scale - 0.01), 2)
        if self.constant_lift_throttle:
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        else:
            self.lift_throttle = (self.lift_throttle_dir * self.last_lift_throttle_axis_val * self.lift_throttle_scale)

        print('lift_throttle_scale:', self.lift_throttle_scale)

    def decrease_max(self):
        """
        最高速を下げる。
        引数：
            なし
        戻り値：
            なし
        """
        super().decrease_max_throttle()
        self.decrease_max_lift_throttle()

    def toggle_constant_lift_throttle(self):
        """
        リフトスロットル値をトグル操作で一定値にする。
        引数：
            なし
        戻り値：
            なし
        """
        if self.constant_lift_throttle:
            self.constant_lift_throttle = False
            self.lift_throttle = 0
            self.on_throttle_changes()
        else:
            self.constant_lift_throttle = True
            self.lift_throttle = self.lift_throttle_scale
            self.on_throttle_changes()
        print('constant_lift_throttle:', self.constant_lift_throttle)
    
    def toggle_constant(self):
        """
        全スロットル値をトグル操作で一定値にする。
        引数：
            なし
        戻り値：
            なし
        """
        super().toggle_constant_throttle()
        self.constant_lift_throttle()

    def normal_stop(self):
        """
        通常停止状態にする。
        引数：
            なし
        戻り値：
            なし
        """
        super().set_throttle(0.0)
        super().set_steering(0.0)
        self.set_lift_throttle(0.0)


    def increase_max_axis(self, axis_val):
        """
        increase_max_axis関数をアナログ入力で行う。
        引数：
            axis_val    アナログ値
        戻り値：
            なし
        """
        if self._trim_zero(axis_val) > 0.0:
            self.increase_max()
    
    def decrease_max_axis(self, axis_val):
        """
        decrease_max_axis関数をアナログ入力で行う。
        引数：
            axis_val    アナログ値
        戻り値：
            なし
        """
        if self._trim_zero(axis_val) > 0.0:
            self.decrease_max()
    
    def set_throttle_half(self, axis_val):
        """
        スロットルを半分開ける（アナログ入力）。
        引数：
            axis_val    アナログ値、ゼロ以外が半速
        戻り値：
            なし
        """
        super().set_throttle(axis_val * 0.5)

    def chaos_monkey_on_left_axis(self, axis_val):
        """
        chaos_monkey_on_left関数をアナログ入力で行う。
        引数：
            axis_val    アナログ値
        戻り値：
            なし
        """
        if self._trim_zero(axis_val) != 0:
            self.chaos_monkey_on_left()
        else:
            self.chaos_monkey_off()

    def chaos_monkey_on_right_axis(self, axis_val):
        """
        chaos_monkey_on_right関数をアナログ入力で行う。
        引数：
            axis_val    アナログ値
        戻り値：
            なし
        """
        if self._trim_zero(axis_val) != 0:
            self.chaos_monkey_on_right()
        else:
            self.chaos_monkey_off()

    def _trim_zero(self, val):
        """
        ほぼ0を0に変換する。
        引数：
            val     アナログ入力値
        戻り値：
            変換後の値
        """
        if -0.1 < val and val < 0.1:
            return 0.0
        else:
            return val

    def run_threaded(self, img_arr=None):
        '''
        process E-Stop state machine
        '''
        if self.estop_state > self.ES_IDLE:
            if self.estop_state == self.ES_START:
                self.estop_state = self.ES_THROTTLE_NEG_ONE
                return 0.0, -1.0 * self.throttle_scale,  0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_NEG_ONE:
                self.estop_state = self.ES_THROTTLE_POS_ONE
                return 0.0, 0.01, 0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_POS_ONE:
                self.estop_state = self.ES_THROTTLE_NEG_TWO
                self.throttle = -1.0 * self.throttle_scale
                return 0.0, self.throttle, 0.0, self.mode, False
            elif self.estop_state == self.ES_THROTTLE_NEG_TWO:
                self.throttle += 0.05
                if self.throttle >= 0.0:
                    self.throttle = 0.0
                    self.estop_state = self.ES_IDLE
                return 0.0, self.throttle, 0.0, self.mode, False

        if self.chaos_monkey_steering is not None:
            return self.chaos_monkey_steering, self.throttle, self.lift_throttle, self.mode, False

        return self.angle, self.throttle, self.lift_throttle, self.mode, self.recording

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        #return None, None, None, None, None

    ''' デバッグ用関数群 '''
    def _print(self, name):
        print('target: {}'.format(str(name)))
    def _print_axis(self, name, axis_val):
        print('target: {} axis_val:{}'.format(str(name), str(axis_val)))
    def _print_l1(self):
        self._print('L1/LT/7')
    def _print_r1(self):
        self._print('R1/RT/8')
    def _print_l1_axis(self, axis_val):
        self._print_axis('L1/LT/7', axis_val)
    def _print_r1_axis(self, axis_val):
        self._print_axis('R1/RT/8', axis_val)
    def _print_l2(self):
        self._print('L2/LB/5')
    def _print_r2(self):
        self._print('R2/RB/6')
    def _print_l2_axis(self, axis_val):
        self._print_axis('L2/LB/5', axis_val)
    def _print_r2_axis(self, axis_val):
        self._print_axis('R2/RB/5', axis_val)
    def _print_l3(self):
        self._print('L3/9')
    def _print_r3(self):
        self._print('R3/9')
    def _print_x(self):
        self._print('X/1/square')
    def _print_y(self):
        self._print('Y/2/triangle')
    def _print_a(self):
        self._print('A/3/cross')
    def _print_b(self):
        self._print('B/4/circle')
    def _print_back(self):
        self._print('back/11/select')
    def _print_start(self):
        self._print('start/12')
    def _print_logo(self):
        self._print('logo/13')
    def _print_dpad_vert(self, axis_val):
        self._print_axis('dpad_vert', axis_val)
    def _print_dpad_horz(self, axis_val):
        self._print_axis('dpad_horz', axis_val)
    def _print_left_vert(self, axis_val):
        self._print_axis('left_vert', axis_val)
    def _print_left_horz(self, axis_val):
        self._print_axis('left_horz', axis_val)
    def _print_right_vert(self, axis_val):
        self._print_axis('right_vert', axis_val)
    def _print_right_horz(self, axis_val):
        self._print_axis('right_horz', axis_val)

''' Logicool F710 '''

class F710ForkliftJoystick(Joystick):
    """
    Logicool F710 のボタン・アナログ入力定義クラス。
    """
    def __init__(self, *args, **kwargs):
        """
        Logicool F710 ボタン・アナログ入力定義をおこなう。
        引数：
            可変（親クラスに依存）
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)
        # ボタン定義
        self.button_names = {
            # from wizard
            0x130 : 'A',
            0x131 : 'B',
            0x133 : 'X',
            0x134 : 'Y',
            0x136 : 'L1',
            0x137 : 'R1',
            0x13a : 'back', # 反応なし！
            0x13b : 'start',
            0x13c : 'logo',
            0x13d : 'L3',
            0x13e : 'R3',
        }

        # アナログ定義
        self.axis_names = {
            # from wizard
            0x10 : 'dpad_leftright', # 1 is right, -1 is left
            0x11 : 'dpad_updown', # 1 is down, -1 is up

            0x2 : 'L2',
            0x5 : 'R2',

            0x0 : 'left_stick_horz',
            0x1 : 'left_stick_vert',
            0x3 : 'right_stick_horz',
            0x4 : 'right_stick_vert',
        }

class F710ForkliftJoystickController(ForkliftJoystickController):
    """
    Logicool F710 に
    フォークリフト操作を割り当てたパーツクラス。
    """
    def __init__(self, *args, **kwargs):
        """
        初期化処理。
        引数：
            可変（親クラスに依存）
            debug      デバッグオプション
        戻り値：
            なし
        """
        self.debug = kwargs.pop('debug') or False
        super().__init__(*args, **kwargs)
        print('mode is {}'.format(self.mode))

    def init_js(self):
        """
        Logicool F710 ボタン・アナログ入力定義を行う。
        引数：
            可変（親クラスに依存）
        戻り値：
            なし
        """
        try:
            self.js = F710ForkliftJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        """
        ボタン・アナログ入力へフォークリフト操作を割り当てる。
        引数：
            なし
        戻り値：
            なし
        """
        # ボタン押下時操作割り当て
        self.button_down_trigger_map = {
            'back' : self.toggle_mode, # 動かず
            'start' : self.toggle_constant_throttle,
            'logo' : self.toggle_mode, # self.normal_stop,

            'B': self.toggle_manual_recording,
            'Y': self.erase_last_N_records,
            'A': self.emergency_stop,
            'X': self.normal_stop,

            'R1' : self.chaos_monkey_on_right,
            'L1' : self.chaos_monkey_on_left,

            'R3' : self.normal_stop,
            'L3' : self.normal_stop,
        }
        # ボタン離脱時操作割り当て
        self.button_up_trigger_map = {
            'R1' : self.chaos_monkey_off,
            'L1' : self.chaos_monkey_off,
        }
        # アナログ入力時操作割り当て
        self.axis_trigger_map = {
            'left_stick_horz' : self.set_steering,
            'left_stick_vert' : self.set_throttle,

            'right_stick_horz' : self.set_steering,
            'right_stick_vert' : self.set_lift_throttle,

            'dpad_leftright' : self.set_steering,
            'dpad_updown' : self.set_throttle_half,

            'L2' : self.decrease_max_axis,
            'R2' : self.increase_max_axis,
        }

        # デバッグ用
        if self.debug:
            self.button_down_trigger_map = {
                'back' : self._print_back,
                'start' : self._print_start,
                'logo' : self._print_logo,
                'B': self._print_b,
                'Y': self._print_y,
                'A': self._print_a,
                'X': self._print_x,
                'R1' : self._print_r1,
                'L1' : self._print_l1,
                'R3' : self._print_r3,
                'L3' : self._print_l3,
            }
            self.axis_trigger_map = {
                'left_stick_horz' : self._print_left_horz,
                'left_stick_vert' : self._print_left_vert,
                'right_stick_horz' : self._print_right_horz,
                'right_stick_vert' : self._print_right_vert,
                'dpad_leftright' : self._print_dpad_horz,
                'dpad_updown' : self._print_dpad_vert,
                'L2' : self._print_l2_axis,
                'R2' : self._print_r2_axis,
            }
            print('[F710ForkliftJoystickController] debug on')


''' Elecom JC-U4113S '''

class ELECOM_JCU4113SJoystick(Joystick):
    """
    JC-U4113Sにおける/dev/input/js0 でのボタン/パッド/ジョイスティック
    各々のコードをマップ化したクラス。
    """
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出し、ボタン・ジョイスティック
        の入力キーを割り当てる。
        引数：
            可変（親クラスJoystic依存）
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)
        # ボタン入力定義
        self.button_names = {
            # 右ボタン群
            0x133 : '1',    # X
            0x134 : '2',    # Y
            0x130 : '3',    # A
            0x131 : '4',    # B
            # 上部ボタン群
            0x136 : '5',    # LB
            0x137 : '6',    # RB
            # 中央部ボタン群
            0x13a : '11',   # BACK
            0x13b : '12',   # START
            0x13c : '13',   # GUIDE
            # アナログスティック押下
            0x13d : '9',    # 左アナログスティック押下
            0x13e : '10',   # 右アナログスティック押下
        }

        # アナログ入力定義
        self.axis_names = {
            # 左アナログスティック
            0x0 : 'left_horz',  # 左アナログ上下
            0x1 : 'left_vert',  # 左アナログ左右
            # 右アナログスティック
            0x3 : 'right_horz', # 右アナログ上下
            0x4 : 'right_vert', # 右アナログ左右
            # 十字キー
            0x10 : 'dpad_horz', # 十字キー左右
            0x11 : 'dpad_vert', # 十字キー上下
            # 上部ボタン群
            0x2 : '7',          # LT
            0x5 : '8',          # RT
        }

class JCU4113SForkliftJoystickController(ForkliftJoystickController):
    """
    フォークリフト操作専用
    ELECOM社製JC-U4113S XBox互換 ワイヤレスゲームパッド
    パーツクラス
    """
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出す。
        引数：
            可変    親クラス参照のこと
            debug   デバッグオプション
        戻り値：
            なし
        """
        self.debug = kwargs.pop('debug') or False
        super().__init__(*args, **kwargs)
        print('mode is {}'.format(self.mode))

    def init_js(self):
        """
        親クラスのコンストラクタから呼び出され、
        ジョイスティック初期化処理を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        try:
            # ボタンやアナログ入力定義を行う
            self.js = ELECOM_JCU4113SJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        """
        ボタンやアナログスティックへ機能を割り当てる。
        引数：
            なし
        戻り値：
            なし
        """
        # ボタン押下時操作割り当て
        self.button_down_trigger_map = {
            # 中央ボタン群
            '11' : self.toggle_mode,
            '12' : self.toggle_constant_throttle,
            '13' : self.toggle_mode, # self.normal_stop,
            # 右ボタン群
            '4': self.toggle_manual_recording,
            '2': self.erase_last_N_records,
            '3': self.emergency_stop,
            '1': self.normal_stop,
            # 上部トリガ小
            '5' : self.decrease_max,
            '6' : self.increase_max,
            # アナログスティック押下
            '9' : self.normal_stop,
            '10' : self.normal_stop,
        }
        # ボタン離脱時操作割り当て
        self.button_up_trigger_map = {}
        # アナログ入力時操作割り当て
        self.axis_trigger_map = {
            # 左アナログスティック
            'left_horz' : self.set_steering,
            'left_vert' : self.set_throttle,
            # 右アナログスティック
            'right_horz' : self.set_steering,
            'right_vert' : self.set_lift_throttle,
            # 十字キー
            'dpad_horz' : self.set_steering,
            'dpad_vert' : self.set_throttle_half,
            # 上部トリガ大
            '7' : self.chaos_monkey_on_left_axis,
            '8' : self.chaos_monkey_on_right_axis,
        }

        # デバッグ用
        if self.debug:
            self.button_down_trigger_map = {
                '11' : self._print_back,
                '12' : self._print_start,
                '13' : self._print_logo,
                '4': self._print_b,
                '2': self._print_y,
                '1': self._print_a,
                '3': self._print_x,
                '5' : self._print_l2,
                '6' : self._print_r2,
                '9' : self._print_r3,
                '10' : self._print_l3,
            }
            self.axis_trigger_map = {
                'left_horz' : self._print_left_horz,
                'left_vert' : self._print_left_vert,
                'right_horz' : self._print_right_horz,
                'right_vert' : self._print_right_vert,
                'dpad_horz' : self._print_dpad_horz,
                'dpad_vert' : self._print_dpad_vert,
                '7' : self._print_l1_axis,
                '8' : self._print_r1_axis,
            }
            print('[JCU4113SForkliftJoystickController] debug on')

''' ファクトリ関数 '''

def get_js_controller(cfg):
    """
    フォークリフト用Joystickパーツクラスファクトリ関数。
    donkeycar.parts.controllerの同名関数をラップしている。
    引数：
        cfg config.py/myconfig.py 上の定義をインスタンス変数として
            参照可能なオブジェクト
    戻り値
        ctr フォークリフト用Joystickパーツクラスオブジェクト
    """
    if cfg.CONTROLLER_TYPE == "F710_Forklift":
        cont_class = F710ForkliftJoystickController
        ctr = cont_class(
            throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
            throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
            steering_scale=cfg.JOYSTICK_STEERING_SCALE,
            #steering_dir=cfg.JOYSTICK_STEERING_DIR,
            lift_throttle_dir=cfg.JOYSTICK_LIFT_THROTTLE_DIR,
            lift_throttle_scale=cfg.JOYSTICK_MAX_LIFT_THROTTLE,
            auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
            debug=cfg.JOYSTICK_DEBUG)
        ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
        return ctr
    elif cfg.CONTROLLER_TYPE == 'JCU4113S_Forklift':
        cont_class = JCU4113SForkliftJoystickController
        ctr = cont_class(
            throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
            throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
            steering_scale=cfg.JOYSTICK_STEERING_SCALE,
            #steering_dir=cfg.JOYSTICK_STEERING_DIR,
            lift_throttle_dir=cfg.JOYSTICK_LIFT_THROTTLE_DIR,
            lift_throttle_scale=cfg.JOYSTICK_MAX_LIFT_THROTTLE,
            auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
            debug=cfg.JOYSTICK_DEBUG)
        ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
        return ctr
    else:
        try:
            return donkeycar.parts.controller.get_js_controller(cfg)
        except:
            raise