# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Fork Lift Agent手動・自動運転スクリプト

Usage:
    manage.py [--model=<model>] [--tub=<tub1,tub2,..tubn>]

Options:
    -h --help           使い方を表示する。
    --model MODELPATH   モデルディレクトリを指定する。本引数を指定した場合、自動運転を行う。
    --tub TUBPATHS      タブディレクトリを指定する。
"""
from docopt import docopt
import donkeycar as dk


def drive(cfg, model_path, tub_dir):
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
    #adr = cfg.HEDGEHOG_ADDRESS
    #tty = cfg.HEDGEHOG_SERIAL_TTY
    #baud = cfg.HEDGEHOG_SERIAL_BAUD

    #  IMUのみ
    #from gpio.hedgehog import HedgeHogIMU
    #imu = [
    #    'imu/x', 'imu/y', 'imu/z',
    #    'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
    #    'imu/vx', 'imu/vy', 'imu/vz',
    #    'imu/ax', 'imu/ay', 'imu/az']
    #
    #hedge = HedgeHogIMU(pi, adr=adr, tty=tty, baud=baud, debug=False)
    #V.add(hedge, outputs=imu)
    #from aws import Client, HedgeHogIMUReporter
    #client = Client(cfg.AWS_YAML_PATH, cfg.AWS_YAML_TARGET)
    #reporter = HedgeHogIMUReporter(client, force_disconnect=True)
    #V.add(reporter, inputs=imu)


    #  Ultra Sonic Navigation
    #from gpio.hedgehog import HedgeHogUSNav
    #hedge = HedgeHogUSNav(pi, adr=adr, tty=tty, baud=baud, debug=False)
    #usnav = [
    #    'usnav/x', 'usnav/y', 'usnav/z',
    #]
    #V.add(hedge, outputs=usnav)
    #from aws import Client, HedgeHogUSNavReporter
    #client = Client(cfg.AWS_YAML_PATH, cfg.AWS_YAML_TARGET)
    #reporter = HedgeHogUSNavReporter(client, force_disconnect=True)
    #V.add(reporter, inputs=usnav)

    # IMU/USNav 両方
    #from gpio.hedgehog import HedgeHog
    #hedge = HedgeHog(pi, adr=adr, tty=tty, baud=baud, debug=False)
    #usnav_ims = [
    #    'usnav/x', 'usnav/y', 'usnav/z',
    #    'imu/x', 'imu/y', 'imu/z',
    #    'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
    #    'imu/vx', 'imu/vy', 'imu/vz',
    #    'imu/ax', 'imu/ay', 'imu/az']
    #V.add(hedge, outputs=usnav_ims)
    #from aws import Client, HedgeHogReporter
    #client = Client(cfg.AWS_YAML_PATH, cfg.AWS_YAML_TARGET)
    #reporter = HedgeHogReporter(client, force_disconnect=True)
    #V.add(reporter, inputs=usnav_ims)

    #from debug import PrintUSNav, PrintIMU
    #p = PrintUSNav()
    #V.add(p, inputs=['usnav/x', 'usnav/y', 'usnav/z'])
    #p = PrintIMU()
    #V.add(p, inputs=['imu/x', 'imu/y', 'imu/z',
    #    'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
    #    'imu/vx', 'imu/vy', 'imu/vz',
    #    'imu/ax', 'imu/ay', 'imu/az'])

    # 超音波距離センサ
    from gpio import RangeSensor
    range = RangeSensor(pi, range_gpios=cfg.RANGE_GPIOS)
    V.add(range, outputs=['range/cms'], threaded=True)

    # 物理センサ群
    from gpio import PhysicalSensors
    ps = PhysicalSensors(pi, spi_settings=cfg.SPI_SETTINGS)
    V.add(ps, outputs=['force/volts', 'bend/volts'], threaded=True)
    
    # ジョイスティック (user)
    from logicool import ForkLiftJoystickController
    joystick = ForkLiftJoystickController()
    V.add(joystick, outputs=['user/left/value', 'user/left/status', 
            'user/right/value', 'user/right/status', 
            'user/lift/value', 'user/lift/status',
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
            'local/lift/value', 'local/lift/status'],
        run_condition='run_pilot')

    # user/mode 値にあわせてPUへ伝達するデータを選択
    from mode import DriveModeSelector
    selector = DriveModeSelector()
    V.add(selector,
        inputs=['user/mode',
            'user/left/value', 'user/left/status', 
            'user/right/value', 'user/right/status', 
            'user/lift/value', 'user/lift/status',
            'local/left/value', 'local/left/status', 
            'local/right/value', 'local/right/status', 
            'local/lift/value', 'local/lift/status'],
        outputs=[
            'pilot/left/value', 'pilot/left/status',
            'pilot/right/value', 'pilot/right/status',
            'pilot/lift/value', 'pilot/lift/status'])

    #
    # 出力系
    #


    from debug import PrintPowerSettings
    pps = PrintPowerSettings(title='PILOT')
    V.add(pps, inputs=[
        'pilot/left/value', 'pilot/left/status',
        'pilot/right/value', 'pilot/right/status',
        'pilot/lift/value', 'pilot/lift/status',
        'user/mode'
    ])

    from gpio import PowerUnit
    pu = PowerUnit(pi, pu_gpios=cfg.PU_GPIOS)
    V.add(pu, 
        inputs=[
            'pilot/left/value',     'pilot/left/status',
            'pilot/right/value',    'pilot/right/status',
            'pilot/lift/value',     'pilot/lift/status'])


    # Tubデータの定義
    inputs = [
        'cam/image_array', 
        'user/left/value',  'user/left/status', 
        'user/right/value', 'user/right/status', 
        'user/lift/value',  'user/lift/status', 
        'range/cms',
        'force/volts',      'bend/volts'
        'user/mode',        'timestamp']
    types = [
        'image_array',
        'float',            'str',
        'float',            'str', 
        'float',            'str',
        'float',
        'float',            'float',
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
    tub_dir = args.get('--tub', 'tub')
    drive(cfg, model_path=model_path, tub_dir=tub_dir)

