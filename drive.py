# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Dozer Agent手動・自動運転スクリプト

Usage:
    manage.py [--model=<model>] [--tub=<tub1,tub2,..tubn>] [--use_imu] [--use_aws]

Options:
    -h --help           使い方を表示する。
    --model MODELPATH   モデルディレクトリを指定する。本引数を指定した場合、自動運転を行う。
    --tub TUBPATHS      タブディレクトリを指定する。
    --use_imu           USB経由で接続されているヘッジホッグよりIMU情報を受け取る
    --use_aws           ASW IoT Coreへpublishする
"""
from docopt import docopt
import donkeycar as dk


def drive(cfg, model_path, tub_dir, use_imu=False, use_aws=False):
    """
    自動もしくは手動運転を行う。

    引数：
        model_path      保存済みモデルファイルのパス
        tub_dir         Tubディレクトリパス
    戻り値：
        なし
    """

    # pigpio 初期化
    import pigpio
    pi = pigpio.pi()

    # Vehicle ループ生成
    V = dk.vehicle.Vehicle()

    #
    # ループ設定はじめ
    #

    # 初期値登録
    V.mem['user/mode'] = 'user' # 手動運転モード
    V.mem['recording'] = False # いきなりTubデータを保存しない

    #
    # 入力系
    #

    # タイムスタンプ
    from donkeycar.parts.clock import Timestamp
    clock = Timestamp()
    V.add(clock, outputs=['timestamp'])

    # カメラ画像
    from donkeycar.parts.camera import PiCamera
    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    # 屋内位置情報センサ
    adr = cfg.HEDGEHOG_ADDRESS
    tty = cfg.HEDGEHOG_SERIAL_TTY
    baud = cfg.HEDGEHOG_SERIAL_BAUD
    imu = [
        'imu/x', 'imu/y', 'imu/z',
        'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz',
        'imu/ax', 'imu/ay', 'imu/az']

    if use_imu:
        from gpio.hedgehog import HedgeHogIMU
        
    
        hedge = HedgeHogIMU(pi, adr=adr, tty=tty, baud=baud, debug=False)
        V.add(hedge, outputs=imu)

    if use_aws:
        from aws import Client, HedgeHogIMUReporter
        client = Client(cfg.AWS_YAML_PATH, cfg.AWS_YAML_TARGET)
        reporter = HedgeHogIMUReporter(client, force_disconnect=True)
        V.add(reporter, inputs=imu)


    # ジョイスティック (user)
    from elecom import DozerJoystickController
    joystick = DozerJoystickController()
    V.add(joystick, outputs=['user/left/value', 'user/left/status', 
            'user/right/value', 'user/right/status', 
            'user/mode', 'recording'], threaded=True)

    
    # オートパイロットフラグ(run_pilot)
    def pilot_condition(mode):
        if mode == 'user':
            return False
        else:
            return True
    from donkeycar.parts.transform import Lambda
    pilot_condition_part = Lambda(pilot_condition)
    V.add(pilot_condition_part,
        inputs=['user/mode'],
        outputs=['run_pilot'])

    # オートパイロット(local)
    from pilot.keras import KerasLinear 
    auto_pilot = KerasLinear()
    if model_path:
        auto_pilot.load(model_path)
    V.add(auto_pilot,
        inputs=['cam/image_array'],
        outputs=['local/left/value', 'local/left/status', 
            'local/right/value', 'local/right/status', 
        ],
        run_condition='run_pilot')

    # user/mode 値にあわせてPUへ伝達するデータを選択
    from mode import DriveModeSelector
    selector = DriveModeSelector()
    V.add(selector,
        inputs=['user/mode',
            'user/left/value', 'user/left/status', 
            'user/right/value', 'user/right/status', 
            #'user/lift/value', 'user/lift/status',
            'local/left/value', 'local/left/status', 
            'local/right/value', 'local/right/status', 
            #'local/lift/value', 'local/lift/status'
        ],
        outputs=[
            'pilot/left/value', 'pilot/left/status',
            'pilot/right/value', 'pilot/right/status',
            #'pilot/lift/value', 'pilot/lift/status'
        ])

    #
    # 出力系
    #


    from debug import PrintPowerSettings
    pps = PrintPowerSettings(title='PILOT')
    V.add(pps, inputs=[
        'pilot/left/value', 'pilot/left/status',
        'pilot/right/value', 'pilot/right/status',
        #'pilot/lift/value', 'pilot/lift/status',
        'user/mode'
    ])

    from gpio import PowerUnit
    pu = PowerUnit(pi, pu_gpios=cfg.PU_GPIOS)
    V.add(pu, 
        inputs=[
            'pilot/left/value',     'pilot/left/status',
            'pilot/right/value',    'pilot/right/status',
            #'pilot/lift/value',     'pilot/lift/status'
        ])


    # Tubデータの定義
    inputs = [
        'cam/image_array', 
        'user/left/value',  'user/left/status', 
        'user/right/value', 'user/right/status', 
        #'user/lift/value',  'user/lift/status', 
        #'range/cms',
        #'force/volts',      'bend/volts'
        'user/mode',        'timestamp']
    types = [
        'image_array',
        'float',            'str',
        'float',            'str', 
        #'float',            'str',
        #'float',
        #'float',            'float',
        'str',              'str']

    # multiple tubs
    # th = TubHandler(path=cfg.DATA_PATH)
    # tub = th.new_tub_writer(inputs=inputs, types=types)

    # Tubデータ書き込み
    from donkeycar.parts.datastore import TubWriter
    tub = TubWriter(path=tub_dir, inputs=inputs, types=types)
    V.add(tub, inputs=inputs, run_condition='recording')


    
    #from debug import PrintSensors
    #ps = PrintSensors()
    #V.add(ps, inputs=[
    #    'range/cms',
    #    'force/volts',
    #    'bend/volts'
    #])

    #
    # ループ設定おわり
    #

    # Vehicleループ開始
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)
    print('Start driving')

# スクリプト実行時
if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    # 運転関数呼び出し
    model_path = args['--model']
    use_imu = args['--imu']
    use_aws = args['--aws']
    tub_dir = args.get('--tub', 'tub')
    drive(cfg, model_path=model_path, tub_dir=tub_dir, use_imu=use_imu, use_aws=use_aws)

