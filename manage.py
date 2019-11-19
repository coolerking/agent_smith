# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car

Usage:
    manage.py (drive) [--model=<model>] [--js] [--hedge] [--aws] [--map] [--debug] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer|latent|tflite_linear)] [--camera=(single|stereo)] [--meta=<key:value> ...]
    manage.py (train) [--tub=<tub1,tub2,..tubn>] [--file=<file> ...] (--model=<model>) [--transfer=<model>] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer|tflite_linear)] [--continuous] [--aug]


Options:
    -h --help          Show this screen.
    --js               Use physical joystick.
    --range            Use range sensor
    --spi              Use sensors via SPI
    --hedge            Use Marvelmind Mobile Beacon via USB
    --aws              Use AWS IoT Core
    --map              Use 2d map image instead of camera
    --debug            Show debug message
    -f --file=<file>   A text file containing paths to tub files, one per line. Option may be used more than once.
    --meta=<key:value> Key/Value strings describing describing a piece of meta data about this drive. Option may be used more than once.
"""
import os
import time

from docopt import docopt
import numpy as np

import donkeycar as dk

#import parts
from donkeycar.parts.transform import Lambda, TriggeredCallback, DelayedTrigger
from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.controller import LocalWebController, JoystickController
from donkeycar.parts.throttle_filter import ThrottleFilter
from donkeycar.parts.behavior import BehaviorPart
from donkeycar.parts.file_watcher import FileWatcher
from donkeycar.parts.launch import AiLaunch
from donkeycar.utils import *

def drive(cfg, model_path=None, use_joystick=False, use_hedge=False, use_aws=False, use_map=False, use_debug=False, model_type=None, camera_type='single', meta=[] ):
    '''
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    '''

    if cfg.DONKEY_GYM:
        #the simulator will use cuda and then we usually run out of resources
        #if we also try to use cuda. so disable for donkey_gym.
        os.environ["CUDA_VISIBLE_DEVICES"]="-1" 

    if model_type is None:
        if cfg.TRAIN_LOCALIZER:
            model_type = "localizer"
        elif cfg.TRAIN_BEHAVIORS:
            model_type = "behavior"
        else:
            model_type = cfg.DEFAULT_MODEL_TYPE

    # pigpio 初期化
    try:
        import pigpio
    except:
        raise
    pgio = pigpio.pi()

    #Initialize car
    V = dk.vehicle.Vehicle()

    '''
    カメラ
    '''
    if camera_type == "stereo":

        if cfg.CAMERA_TYPE == "WEBCAM":
            from donkeycar.parts.camera import Webcam            

            camA = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 0)
            camB = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 1)

        elif cfg.CAMERA_TYPE == "CVCAM":
            from donkeycar.parts.cv import CvCam

            camA = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 0)
            camB = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 1)
        else:
            raise(Exception("Unsupported camera type: %s" % cfg.CAMERA_TYPE))

        V.add(camA, outputs=['cam/image_array_a'], threaded=True)
        V.add(camB, outputs=['cam/image_array_b'], threaded=True)

        from donkeycar.parts.image import StereoPair

        V.add(StereoPair(), inputs=['cam/image_array_a', 'cam/image_array_b'], 
            outputs=['cam/image_array'])


    elif cfg.CAMERA_TYPE != "MAP" and use_map == False:
        print("cfg.CAMERA_TYPE", cfg.CAMERA_TYPE)
        if cfg.DONKEY_GYM:
            from donkeycar.parts.dgym import DonkeyGymEnv 
        
        inputs = []
        threaded = True
        #print("cfg.CAMERA_TYPE", cfg.CAMERA_TYPE)
        if cfg.DONKEY_GYM:
            from donkeycar.parts.dgym import DonkeyGymEnv 
            cam = DonkeyGymEnv(cfg.DONKEY_SIM_PATH, env_name=cfg.DONKEY_GYM_ENV_NAME)
            threaded = True
            inputs = ['angle', 'throttle']
        elif cfg.CAMERA_TYPE == "PICAM":
            from donkeycar.parts.camera import PiCamera
            cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "WEBCAM":
            from donkeycar.parts.camera import Webcam
            cam = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "CVCAM":
            from donkeycar.parts.cv import CvCam
            cam = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "CSIC":
            from donkeycar.parts.camera import CSICamera
            cam = CSICamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE, gstreamer_flip=cfg.CSIC_CAM_GSTREAMER_FLIP_PARM)
        elif cfg.CAMERA_TYPE == "V4L":
            from donkeycar.parts.camera import V4LCamera
            cam = V4LCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE)
        elif cfg.CAMERA_TYPE == "MOCK":
            from donkeycar.parts.camera import MockCamera
            cam = MockCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        else:
            raise(Exception("Unkown camera type: %s" % cfg.CAMERA_TYPE))
            
        V.add(cam, inputs=inputs, outputs=['cam/image_array'], threaded=threaded)
    
    '''
    Marvelmind 位置情報システム
    '''
    # Marvelmind USNav データ
    hedge_items = []
    hedge_types = []
    usnav_items = [
        'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
    ]
    usnav_types = [
        'str', 'float', 'float', 'float', 'float', 'float',
    ]
    hedge_items += usnav_items
    hedge_types += usnav_types
    # Marvelmind USNav Raw データ
    usnav_raw_items = [
        'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
        'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp'
    ]
    usnav_raw_types = [
        'str', 'str', 'float', 'str', 'float',
        'str', 'float', 'str', 'float', 'float',
    ]
    hedge_items += usnav_raw_items
    hedge_types += usnav_raw_types
    # Marvelmind IMU データ
    imu_items = [
        'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
        'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
        'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz',
        'imu/timestamp',
    ]
    imu_types = [
        'float', 'float', 'float', 'float', 'float', 'float', 'float',
        'float', 'float', 'float', 'float', 'float', 'float',
        'float', 'float', 'float', 'float', 'float', 'float',
        'float'
    ]
    # Marvelmind 全データ
    hedge_items += imu_items
    hedge_types += imu_types
    # Veichle上の Marvelmind 全データ初期化
    for i in range(len(hedge_items)):
        _item = hedge_items[i]
        _type = hedge_types[i]
        if _type == 'str':
            V.mem[_item] = '0'
        elif _type == 'float':
            V.mem[_item] = 0.0
        else:
            raise ValueError('unknown type:{}'.format(_type))

    if cfg.HAVE_HEDGE and (use_hedge or cfg.USE_HEDGE_AS_DEFAULT):
        '''
        Marvelmind システムを使用する場合
        '''
        print('Using Marvelmind Mobile Beacon')
        # Marvelmind モバイルビーコンパーツ追加
        from parts import HedgehogController
        hedge = HedgehogController(tty=cfg.HEDGE_SERIAL_TTY, adr=cfg.HEDGE_ID)
        V.add(hedge, outputs=hedge_items)

    '''
    IMU(MPU9250/MPU6050)
    '''
    mpu6050_items = [
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
        'imu/recent', 'imu/mpu_timestamp',
    ]
    mpu6050_types = [
        'float', 'float', 'float',
        'float', 'float', 'float',
        'str', 'float',
    ]
    mpu9250_items = [
        'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
        'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',  
        'imu/mgt_x', 'imu/mgt_y', 'imu/mgt_z',
        'imu/temp',
        'imu/recent', 'imu/mpu_timestamp',
    ]
    mpu9250_types = [
        'float', 'float', 'float',
        'float', 'float', 'float',
        'float', 'float', 'float',
        'float',
        'str', 'float',
    ]
    if cfg.HAVE_IMU:
        mpu_items = []
        mpu_types = []
        if cfg.IMU_TYPE == 'mpu6050':
            '''
            MPU6050を使用する場合
            '''
            mpu_items += mpu6050_items
            mpu_types += mpu6050_types
            from parts.sensors.imu import Mpu6050
            imu = Mpu6050(
                pgio=pgio, 
                bus=cfg.MPU6050_I2C_BUS, 
                address=cfg.MPU6050_I2C_ADDRESS, 
                depth=cfg.MPU6050_DEPTH,
                debug=use_debug)

        elif cfg.IMU_TYPE == 'mpu9250':
            '''
            MPU9250を使用する場合
            '''
            mpu_items += mpu9250_items
            mpu_types += mpu9250_types
            from parts.sensors.imu import Mpu9250
            imu = Mpu9250(
                pgio=pgio,
                bus=cfg.MPU9250_I2C_BUS, 
                mpu9250_address=cfg.MPU9250_I2C_ADDRESS, 
                ak8963_address=cfg.AK8963_I2C_ADDRESS,
                depth=cfg.MPU9250_DEPTH,
                debug=use_debug)
        else:
            raise ValueError('unknown IMU_TYPE = {}'.format(str(cfg.IMU_TYPE)))

        # Veihcle上のIMUデータを初期化
        for i in range(len(mpu_items)):
            _item = mpu_items[i]
            _type = mpu_types[i]
            if _type == 'str':
                V.mem[_item] = '{}'
            elif _type == 'float':
                V.mem[_item] = 0.0
            else:
                raise ValueError('unknown type:{}'.format(_type))
        
        # IMUパーツの追加
        V.add(imu, outputs=mpu_items)

    '''
    2D マップ画像 (usnav/x, usnav/y, imu/recent を使用する)
    '''
    map_items = [
        'usnav/x', 'usnav/y', 'imu/recent',
    ]
    map_types = [
        'float', 'float', 'str',
    ]
    if use_map or cfg.CAMERA_TYPE == "MAP":
        '''
        2D マップ画像でカメラの代替とする場合
        '''
        if cfg.HAVE_HEDGE and (use_hedge or cfg.USE_HEDGE_AS_DEFAULT):
            '''
            Marvelmindが有効である場合
            '''
            if (cfg.HAVE_IMU and cfg.IMU_TYPE == 'mpu9250'):
                '''
                MPU9250を使用する場合
                '''
                # 2D マップ生成パーツを追加
                from parts import MapImageCreator
                creator = MapImageCreator(base_image_path=cfg.MAP_BASE_IMAGE_PATH, debug=use_debug)
                V.add(creator,
                    inputs=map_items,
                    outputs=['cam/image_array'])
            else:
                raise ValueError('2D map needs mpu9250 data')
        else:
            raise ValueError('2D map needs Marvelmind USNav data')

    '''
    ジョイスティック
    '''
    user_items = [
        'user/angle', 'user/throttle', 'user/lift_throttle', 'user/mode',
    ]
    user_types = [
        'float', 'float', 'float', 'str',
    ]
    joystick_items = []
    joystick_types = []
    joystick_items += user_items
    joystick_types += user_types
    joystick_items += ['recording']
    joystick_types += ['boolean']
    # ジョイスティックパーツのアウトプット値なのでここでは初期化せず

    if use_joystick or cfg.USE_JOYSTICK_AS_DEFAULT:
        '''
        ジョイスティックを使用する場合
        '''
        #　フォークリフト用ジョイスティックパーツ取得ファクトリ関数を呼び出す
        from parts import get_js_controller
        ctr = get_js_controller(cfg)
        
        if cfg.USE_NETWORKED_JS:
            '''
            ネットワーク経由で操作する場合(Donkeycar標準)
            '''
            from donkeycar.parts.controller import JoyStickSub
            netwkJs = JoyStickSub(cfg.NETWORK_JS_SERVER_IP)
            V.add(netwkJs, threaded=True)
            ctr.js = netwkJs

        # リフト値の追加
        V.add(ctr, 
            inputs=['cam/image_array'],
            outputs=joystick_items,
            threaded=True)

    else:
        '''
        Webコントローラを使用する
        '''
        # user/lift_throttle 値が常に0となるWebコントローラパーツを生成
        from parts import LocalWebForkliftController
        ctr = LocalWebForkliftController()

        V.add(ctr, 
            inputs=['cam/image_array'],
            outputs=joystick_items,
            threaded=True)

    # 変数ctrはこの後でも使用する

    '''
    スロットルフィルタ(ワンタップESC後進)
    '''
    # 入力値はジョイスティックパーツがアウトプット
    #this throttle filter will allow one tap back for esc reverse
    th_filter = ThrottleFilter()
    V.add(th_filter, inputs=['user/throttle'], outputs=['user/throttle'])


    '''
    手動運転・自動運転判定フラグ設定
    '''
    #See if we should even run the pilot module. 
    #This is only needed because the part run_condition only accepts boolean
    class PilotCondition:
        def run(self, mode):
            if mode == 'user':
                return False
            else:
                return True       
    V.add(PilotCondition(), inputs=['user/mode'], outputs=['run_pilot'])
    # run_pilot 値はboolean(偽：手動運転、真：一部もしくは全て自動運転)


    '''
    3色LED表示
    '''
    class LedConditionLogic:
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self, mode, recording, recording_alert, behavior_state, model_file_changed, track_loc):
            #returns a blink rate. 0 for off. -1 for on. positive for rate.
            
            if track_loc is not None:
                led.set_rgb(*self.cfg.LOC_COLORS[track_loc])
                return -1

            if model_file_changed:
                led.set_rgb(self.cfg.MODEL_RELOADED_LED_R, self.cfg.MODEL_RELOADED_LED_G, self.cfg.MODEL_RELOADED_LED_B)
                return 0.1
            else:
                led.set_rgb(self.cfg.LED_R, self.cfg.LED_G, self.cfg.LED_B)

            if recording_alert:
                led.set_rgb(*recording_alert)
                return self.cfg.REC_COUNT_ALERT_BLINK_RATE
            else:
                led.set_rgb(self.cfg.LED_R, self.cfg.LED_G, self.cfg.LED_B)
        
            if behavior_state is not None and model_type == 'behavior':
                r, g, b = self.cfg.BEHAVIOR_LED_COLORS[behavior_state]
                led.set_rgb(r, g, b)
                return -1 #solid on

            if recording:
                return -1 #solid on
            elif mode == 'user':
                return 1
            elif mode == 'local_angle':
                return 0.5
            elif mode == 'local':
                return 0.1
            return 0

    if cfg.HAVE_RGB_LED and not cfg.DONKEY_GYM:
        #from donkeycar.parts.led_status import RGB_LED
        #led = RGB_LED(cfg.LED_PIN_R, cfg.LED_PIN_G, cfg.LED_PIN_B, cfg.LED_INVERT)
        from parts import RGB_LED
        led = RGB_LED(pgio, cfg.LED_PIN_R, cfg.LED_PIN_G, cfg.LED_PIN_B, cfg.LED_INVERT)
        led.set_rgb(cfg.LED_R, cfg.LED_G, cfg.LED_B)        
        
        V.add(LedConditionLogic(cfg), inputs=['user/mode', 'recording', "records/alert", 'behavior/state', 'modelfile/modified', "pilot/loc"],
              outputs=['led/blink_rate'])

        V.add(led, inputs=['led/blink_rate'])
        

    def get_record_alert_color(num_records):
        """
        Tubデータ件数を色PWMタプル(r,　g, b)：各0-100に変換する。
        件数範囲、PWMタプルはconfig.py上のRECORD_ALERT_COLOR_ARR
        を参照している。
        引数：
            num_records     Tubデータ件数
        戻り値
            色PWMタプル     (r, g, b)形式(0-100)
        """
        col = (0, 0, 0)
        for count, color in cfg.RECORD_ALERT_COLOR_ARR:
            if num_records >= count:
                col = color
        return col    

    '''
    レコードトラッカ
    '''

    class RecordTracker:
        def __init__(self):
            self.last_num_rec_print = 0
            self.dur_alert = 0
            self.force_alert = 0

        def run(self, num_records):
            if num_records is None:
                return 0
            
            if self.last_num_rec_print != num_records or self.force_alert:
                self.last_num_rec_print = num_records

                if num_records % 10 == 0:
                    print("recorded", num_records, "records")
                        
                if num_records % cfg.REC_COUNT_ALERT == 0 or self.force_alert:
                    self.dur_alert = num_records // cfg.REC_COUNT_ALERT * cfg.REC_COUNT_ALERT_CYC
                    self.force_alert = 0
                    
            if self.dur_alert > 0:
                self.dur_alert -= 1

            if self.dur_alert != 0:
                return get_record_alert_color(num_records)

            return 0

    rec_tracker_part = RecordTracker()
    V.add(rec_tracker_part, inputs=["tub/num_records"], outputs=['records/alert'])

    '''
    自動記録
    '''

    if cfg.AUTO_RECORD_ON_THROTTLE and isinstance(ctr, JoystickController):
        """
        自動記録指定されておりかつジョイスティックを使用する場合
        """
        #then we are not using the circle button. hijack that to force a record count indication
        def show_record_acount_status():
            rec_tracker_part.last_num_rec_print = 0
            rec_tracker_part.force_alert = 1
        
        # ジョイスティックのボタンにレコード件数表示用のボタン割当

        # F710
        if cfg.CONTROLLER_TYPE == 'F710' or cfg.CONTROLLER_TYPE == 'F710_Forklift':
            ctr.set_button_down_trigger('back', show_record_acount_status)
        # JC-U3912T
        elif cfg.CONTROLLER_TYPE == 'JC-U3912T':
            ctr.set_button_down_trigger('7', show_record_acount_status)
        # default
        else:
            ctr.set_button_down_trigger('circle', show_record_acount_status)

    '''
    Sombero HAT
    '''
    #Sombrero
    if cfg.HAVE_SOMBRERO:
        from donkeycar.parts.sombrero import Sombrero
        _ = Sombrero()

    # この段階でカメラ or 2Dマップ画像が cam/image_array に格納されている

    '''
    画像前処理
    '''

    class ImgPreProcess():
        '''
        preprocess camera image for inference.
        normalize and crop if needed.
        '''
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self, img_arr):
            return normalize_and_crop(img_arr, self.cfg)

    if "coral" in model_type:
        '''
        coral を使用する場合は画像をそのまま使用
        '''
        inf_input = 'cam/image_array'
    else:
        '''
        自動運転時のみ正規化・CROP処理する
        '''
        inf_input = 'cam/normalized/cropped'
        V.add(ImgPreProcess(cfg),
            inputs=['cam/image_array'],
            outputs=[inf_input],
            run_condition='run_pilot')



    #Behavioral state
    if cfg.TRAIN_BEHAVIORS:
        '''
        behaviorモデルを使用する場合
        '''

        bh = BehaviorPart(cfg.BEHAVIOR_LIST)
        V.add(bh, outputs=['behavior/state', 'behavior/label', "behavior/one_hot_state_array"])
        try:
            # L1ボタンにbehavior状態更新を割当
            ctr.set_button_down_trigger('L1', bh.increment_state)
        except:
            pass

        inputs = [inf_input, "behavior/one_hot_state_array"]


    #IMU
    elif model_type == "imu":
        '''
        IMU（MPU9250/MPU6050）モデル
        '''

        #assert(cfg.HAVE_IMU)
        #Run the pilot if the mode is not user.
        if cfg.HAVE_IMU:
            # 機械学習モデルのインプットにMPU9250/6050の加速度、角速度を追加
            inputs=['cam/image_array',
                'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
                'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
            ]
        elif cfg.HAVE_HEDGE and (use_hedge or cfg.USE_HEDGE_AS_DEFAULT) and cfg.USE_HEDGE_IMU:
            # 機械学習モデルのインプットにMarvelmindの加速度、角速度を追加
            inputs=[
                'cam/image_array',
                'imu/ax', 'imu/ay', 'imu/az',
                'imu/vx', 'imu/vy', 'imu/vz'
            ]
        else:
            raise ValueError('can not use imu model without imu data')
    else:
        # 機械学習モデルのインプットは画像のみ
        inputs=[inf_input]

    '''
    機械学習モデル
    '''

    def load_model(kl, model_path):
        """
        機械学習モデルに学習済みパラメータをロードする。
        引数：
            kl          機械学習モデルオブジェクト
            model_path  学習済みパラーメータファイルのパス
        戻り値：
            なし
        """
        start = time.time()
        print('loading model', model_path)
        kl.load(model_path)
        print('finished loading in %s sec.' % (str(time.time() - start)) )

    def load_weights(kl, weights_path):
        """
        機械学習モデルに学習済みパラメータをロードする。
        引数：
            kl          機械学習モデルオブジェクト
            model_path  学習済みパラーメータファイルのパス
        戻り値：
            なし
        """
        start = time.time()
        try:
            print('loading model weights', weights_path)
            kl.model.load_weights(weights_path)
            print('finished loading in %s sec.' % (str(time.time() - start)) )
        except Exception as e:
            print(e)
            print('ERR>> problems loading weights', weights_path)

    def load_model_json(kl, json_fnm):
        start = time.time()
        print('loading model json', json_fnm)
        try:
            from tensorflow.python import keras
        except:
            raise
        try:
            with open(json_fnm, 'r') as handle:
                contents = handle.read()
                kl.model = keras.models.model_from_json(contents)
            print('finished loading json in %s sec.' % (str(time.time() - start)) )
        except Exception as e:
            print(e)
            print("ERR>> problems loading model json", json_fnm)

    if model_path:
        #When we have a model, first create an appropriate Keras part
        kl = dk.utils.get_model_by_type(model_type, cfg)

        model_reload_cb = None

        if '.h5' in model_path or '.uff' in model_path or 'tflite' in model_path or '.pkl' in model_path:
            #when we have a .h5 extension
            #load everything from the model file
            load_model(kl, model_path)

            def reload_model(filename):
                load_model(kl, filename)

            model_reload_cb = reload_model

        elif '.json' in model_path:
            #when we have a .json extension
            #load the model from there and look for a matching
            #.wts file with just weights
            load_model_json(kl, model_path)
            weights_path = model_path.replace('.json', '.weights')
            load_weights(kl, weights_path)

            def reload_weights(filename):
                weights_path = filename.replace('.json', '.weights')
                load_weights(kl, weights_path)
            
            model_reload_cb = reload_weights

        else:
            print("ERR>> Unknown extension type on model file!!")
            return

        '''
        モデルファイル更新監視
        '''

        #this part will signal visual LED, if connected
        V.add(FileWatcher(model_path, verbose=True), outputs=['modelfile/modified'])

        #these parts will reload the model file, but only when ai is running so we don't interrupt user driving
        V.add(FileWatcher(model_path), outputs=['modelfile/dirty'], run_condition="ai_running")
        V.add(DelayedTrigger(100), inputs=['modelfile/dirty'], outputs=['modelfile/reload'], run_condition="ai_running")
        V.add(TriggeredCallback(model_path, model_reload_cb), inputs=["modelfile/reload"], run_condition="ai_running")

        outputs=['pilot/angle', 'pilot/throttle']

        '''
        ローカライザモデルの場合の出力編集
        '''

        if cfg.TRAIN_LOCALIZER:
            outputs.append("pilot/loc")
    
        V.add(kl, inputs=inputs, 
            outputs=outputs,
            run_condition='run_pilot')            

    '''
    モデルがない場合の自動運転結果初期値設定
    '''

    V.mem['pilot/throttle'] = 0.0
    V.mem['pilot/angle'] = 0.0
    V.mem['pilot/lift_throttle'] = 0.0

    '''
    運転モードから、モータ入力値決定
    '''

    #Choose what inputs should change the car.
    class DriveMode:
        def run(self, mode, 
                    user_angle, user_throttle, user_lift_throttle,
                    pilot_angle, pilot_throttle, pilot_lift_throttle):
            if mode == 'user': 
                return user_angle, user_throttle, user_lift_throttle
            
            elif mode == 'local_angle':
                return pilot_angle, user_throttle, user_lift_throttle
            
            else: 
                return pilot_angle, (pilot_throttle * cfg.AI_THROTTLE_MULT), (pilot_lift_throttle * cfg.AI_THROTTLE_MULT)
        
    V.add(DriveMode(), 
          inputs=['user/mode', 'user/angle', 'user/throttle', 'user/lift_throttle',
                  'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle'], 
          outputs=['angle', 'throttle', 'lift_throttle'])

    # Donkeycarへの最終的な指示が angle, throttle, lift_throttle 値となる

    '''
    AIランチャ
    '''

    #to give the car a boost when starting ai mode in a race.
    aiLauncher = AiLaunch(cfg.AI_LAUNCH_DURATION, cfg.AI_LAUNCH_THROTTLE, cfg.AI_LAUNCH_KEEP_ENABLED)
    
    V.add(aiLauncher,
        inputs=['user/mode', 'throttle'],
        outputs=['throttle'])

    if isinstance(ctr, JoystickController):
        ctr.set_button_down_trigger(cfg.AI_LAUNCH_ENABLE_BUTTON, aiLauncher.enable_ai_launch)

    '''
    AIによる自動運転かどうかの判定
    '''

    class AiRunCondition:
        '''
        A bool part to let us know when ai is running.
        '''
        def run(self, mode):
            if mode == "user":
                return False
            return True

    V.add(AiRunCondition(), inputs=['user/mode'], outputs=['ai_running'])

    '''
    AI運転時の記録モード
    '''

    #Ai Recording
    class AiRecordingCondition:
        '''
        return True when ai mode, otherwize respect user mode recording flag
        '''
        def run(self, mode, recording):
            if mode == 'user':
                return recording
            return True

    if cfg.RECORD_DURING_AI:
        V.add(AiRecordingCondition(), inputs=['user/mode', 'recording'], outputs=['recording'])

    '''
    モータ駆動
    '''

    #Drive train setup
    if cfg.DONKEY_GYM:
        pass

    elif cfg.DRIVE_TRAIN_TYPE == "SERVO_ESC":
        from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle

        steering_controller = PCA9685(cfg.STEERING_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
        steering = PWMSteering(controller=steering_controller,
                                        left_pulse=cfg.STEERING_LEFT_PWM, 
                                        right_pulse=cfg.STEERING_RIGHT_PWM)
        
        throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
        throttle = PWMThrottle(controller=throttle_controller,
                                        max_pulse=cfg.THROTTLE_FORWARD_PWM,
                                        zero_pulse=cfg.THROTTLE_STOPPED_PWM, 
                                        min_pulse=cfg.THROTTLE_REVERSE_PWM)

        V.add(steering, inputs=['angle'])
        V.add(throttle, inputs=['throttle'])
        V.mem['lift_throttle'] = 0

    elif cfg.DRIVE_TRAIN_TYPE == "DC_STEER_THROTTLE":
        from donkeycar.parts.actuator import Mini_HBridge_DC_Motor_PWM
        
        steering = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_LEFT, cfg.HBRIDGE_PIN_RIGHT)
        throttle = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_FWD, cfg.HBRIDGE_PIN_BWD)

        V.add(steering, inputs=['angle'])
        V.add(throttle, inputs=['throttle'])
        V.mem['lift_throttle'] = 0

    elif cfg.DRIVE_TRAIN_TYPE == "DC_TWO_WHEEL":
        from donkeycar.parts.actuator import TwoWheelSteeringThrottle, Mini_HBridge_DC_Motor_PWM

        left_motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_LEFT_FWD, cfg.HBRIDGE_PIN_LEFT_BWD)
        right_motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_RIGHT_FWD, cfg.HBRIDGE_PIN_RIGHT_BWD)
        two_wheel_control = TwoWheelSteeringThrottle()

        V.add(two_wheel_control, 
                inputs=['throttle', 'angle'],
                outputs=['left_motor_speed', 'right_motor_speed'])

        V.add(left_motor, inputs=['left_motor_speed'])
        V.add(right_motor, inputs=['right_motor_speed'])
        V.mem['lift_motor_throttle'] = 0




    # Forklift 駆動モータ操作
    elif cfg.DRIVE_TRAIN_TYPE == "THREE_MOTORS_PIGPIO":
        '''
        フォークリフト３モータ駆動
        '''

        from parts import PIGPIO_OUT, PIGPIO_PWM, ForkliftMotorDriver

        motor_driver = ForkliftMotorDriver(
            left_balance=cfg.LEFT_PWM_BALANCE, 
            right_balance=cfg.RIGHT_PWM_BALANCE, debug=False)
        V.add(motor_driver, 
                inputs=['throttle', 'angle', 'lift_throttle'],
                outputs=[
                    'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                    'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                    'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'
                ])

        if use_debug:
            class Prt:
                def run(self,  left_vref, left_in1, left_in2, right_vref, right_in1, right_in2, lift_vref, lift_in1, lift_in2):
                    print('ForkliftMD left   vref:{}, in1:{}, in2:{}'.format(str(left_vref), str(left_in1), str(left_in2)))
                    print('ForkliftMD right  vref:{}, in1:{}, in2:{}'.format(str(right_vref), str(right_in1), str(right_in2)))
                    print('ForkliftMD lift   vref:{}, in1:{}, in2:{}'.format(str(lift_vref), str(lift_in1), str(lift_in2)))

            V.add(Prt(),inputs=[
                    'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                    'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                    'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'
                ])

        # TB6612#1 A系（右モータ、左折時駆動する）
        V.add(PIGPIO_OUT(
            pin=cfg.LEFT_MOTOR_IN1_GPIO, pgio=pgio), inputs=['left_motor_in1'])
        V.add(PIGPIO_OUT(
            pin=cfg.LEFT_MOTOR_IN2_GPIO, pgio=pgio), inputs=['left_motor_in2'])
        V.add(PIGPIO_PWM(
            pin=cfg.LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
            range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['left_motor_vref'])

        # TB6612#1 B系（左モータ、右折時駆動する）
        V.add(PIGPIO_OUT(
            pin=cfg.RIGHT_MOTOR_IN1_GPIO, pgio=pgio), inputs = ['right_motor_in1'])
        V.add(PIGPIO_OUT(
            pin=cfg.RIGHT_MOTOR_IN2_GPIO, pgio=pgio), inputs = ['right_motor_in2'])
        V.add(PIGPIO_PWM(
            pin=cfg.RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
            range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['right_motor_vref'])

        # TB6612#2 A系（リフトモータ）
        V.add(PIGPIO_OUT(
            pin=cfg.LIFT_MOTOR_IN1_GPIO, pgio=pgio), inputs = ['lift_motor_in1'])
        V.add(PIGPIO_OUT(
            pin=cfg.LIFT_MOTOR_IN2_GPIO, pgio=pgio), inputs = ['lift_motor_in2'])
        V.add(PIGPIO_PWM(
            pin=cfg.LIFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
            range=cfg.PWM_RANGE,  threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['lift_motor_vref'])

    elif cfg.DRIVE_TRAIN_TYPE == "SERVO_HBRIDGE_PWM":
        from donkeycar.parts.actuator import ServoBlaster, PWMSteering
        steering_controller = ServoBlaster(cfg.STEERING_CHANNEL) #really pin
        #PWM pulse values should be in the range of 100 to 200
        assert(cfg.STEERING_LEFT_PWM <= 200)
        assert(cfg.STEERING_RIGHT_PWM <= 200)
        steering = PWMSteering(controller=steering_controller,
                                        left_pulse=cfg.STEERING_LEFT_PWM, 
                                        right_pulse=cfg.STEERING_RIGHT_PWM)
       

        from donkeycar.parts.actuator import Mini_HBridge_DC_Motor_PWM
        motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_FWD, cfg.HBRIDGE_PIN_BWD)

        V.add(steering, inputs=['angle'])
        V.add(motor, inputs=["throttle"])
        V.mem['lift_throttle'] = 0

    
    '''
    Tubデータ
    '''
    # ベースとなるTubデータ
    inputs=['cam/image_array']
    inputs += user_items
    types=['image_array']
    types += user_types

    if cfg.TRAIN_BEHAVIORS:
        '''
        behaviorモデルを使用する場合の入力データを追加
        '''
        inputs += ['behavior/state', 'behavior/label', 'behavior/one_hot_state_array']
        types += ['int', 'str', 'vector']

    '''
    IMU(MPU6050)データ追加
    '''

    if model_type == 'imu' or cfg.DEFAULT_MODEL_TYPE == 'imu':
        '''
        IMUモデルを使用する場合
        '''
        # 入力データに加速度、角速度を追加
        imu_inputs = [
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
        ]
        imu_input_types = [
            'float', 'float', 'float',
            'float', 'float', 'float',
        ]
        inputs += imu_inputs
        types += imu_input_types
            
        if not cfg.HAVE_IMU:
            '''
            MPU9250/MPU6050を持っていない場合
            '''
            if cfg.HAVE_HEDGE and (use_hedge or cfg.USE_HEDGE_AS_DEFAULT):
                '''
                Marvelmind が有効な場合
                '''
                if cfg.USE_HEDGE_IMU:
                    '''
                    Marvelmind IMUが使用可能な場合
                    '''
                    # 必要な Marvelmind IMUデータを移動させる
                    class MoveIMU:
                        def run(self, ax, ay, az, gx, gy, gz):
                            return ax, ay, az, gx, gy, gz
                    move = MoveIMU()
                    V.add(move, 
                        inputs=[
                            'imu/ax', 'imu/ay', 'imu/az',
                            'imu/gx', 'imu/gy', 'imu/gz',
                        ],
                        outputs=imu_inputs)

    if cfg.RECORD_DURING_AI:
        '''
        自動運転中であっても記録しておくモードの場合
        '''
        # pilot/* を Tub データに加える
        inputs += ['pilot/angle', 'pilot/throttle', 'pilot/lift_throttle']
        types += ['float', 'float', 'float']

    '''
    Tubデータ書き込み
    '''
    th = TubHandler(path=cfg.DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
    V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')


    if cfg.PUB_CAMERA_IMAGES:
        '''
        カメライメージを通信して貰う場合(Donkeycar標準)
        '''
        from donkeycar.parts.network import TCPServeValue
        from donkeycar.parts.image import ImgArrToJpg
        pub = TCPServeValue("camera")
        V.add(ImgArrToJpg(), inputs=['cam/image_array'], outputs=['jpg/bin'])
        V.add(pub, inputs=['jpg/bin'])

    '''
    操縦系統別
    '''

    if type(ctr) is LocalWebController:
        '''
        LocalWebController を使用している場合の usage を表示
        '''
        print("You can now go to <your pi ip address>:8887 to drive your car.")
    elif isinstance(ctr, JoystickController):
        '''
        ジョイスティックを使用している場合の usage を表示
        '''
        print("You can now move your joystick to drive your car.")
        #tell the controller about the tub        
        ctr.set_tub(tub)
        
        if cfg.BUTTON_PRESS_NEW_TUB:
            '''
            cfg.BUTTON_PRESS_NEW_TUB が True の場合、ボタンを押すごとに別のTubディレクトリに
            データが格納されるようになる（デフォルト:False）。
            '''
    
            def new_tub_dir():
                V.parts.pop()
                tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
                V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')
                ctr.set_tub(tub)

            # ボタン割当
            # F710
            if cfg.CONTROLLER_TYPE == 'F710' or cfg.CONTROLLER_TYPE == 'F710_Forklift':
                ctr.set_button_down_trigger('A', new_tub_dir)
            # JC-U3912T
            elif cfg.CONTROLLER_TYPE == 'JC-U3912T' or cfg.CONTROLLER_TYPE == 'JC-U3912T_Forklift':
                ctr.set_button_down_trigger('12', new_tub_dir)
            # default
            else:
                ctr.set_button_down_trigger('cross', new_tub_dir)

        # 現時点のボタン割当状態を表示
        ctr.print_controls()


    """
    AWS IoT Core
    """
    if use_aws or cfg.USE_AWS_AS_DEFAULT:
        print('AWS Configuration')
        from parts.broker import AWSShadowClientFactory, PowerReporter
        factory = AWSShadowClientFactory(cfg.AWS_CONFIG_PATH, cfg.AWS_THING_NAME)
        # Power ON 情報の送信
        power = PowerReporter(factory, debug=use_debug)
        power.on()

        # Tubデータ(json)送信
        from parts.broker.pub import Publisher
        pub_tub = Publisher(factory, debug=use_debug)
        V.add(pub_tub, inputs=[
            'user/angle', 'user/throttle', 'user/lift_throttle',
            'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
            'user/mode'
        ])

        # Tubデータ(イメージ)送信
        from parts.broker.pub import ImagePublisher
        pub_img = ImagePublisher(factory, debug=use_debug)
        V.add(pub_img, inputs=[
            'cam/image_array',
        ])

        '''
        ジョイスティックデータの送信
        '''
        if use_joystick or cfg.USE_JOYSTICK_AS_DEFAULT:
            '''
            ジョイスティックを使用している場合
            '''
            from parts.broker.pub import JoystickPublisher
            pub_joy = JoystickPublisher(factory, debug=use_debug)
            V.add(pub_joy, inputs=joystick_items)

        '''
        Marvelmind システムデータの送信
        '''
        if cfg.HAVE_HEDGE and (use_hedge or cfg.USE_HEDGE_AS_DEFAULT):
            '''
            Marvelmind システムを使用している場合
            '''
            if cfg.USE_HEDGE_USNAV:
                '''
                Marvelmind 位置情報を使用している場合
                '''
                from parts.broker.pub import USNavPublisher
                pub_usn = USNavPublisher(factory, debug=use_debug)
                print('usnav')
                print(usnav_items)
                V.add(pub_usn, inputs=usnav_items)

            if cfg.USE_HEDGE_USNAV_RAW:
                '''
                Marvelmind 距離情報を使用している場合
                '''
                from parts.broker.pub import USNavRawPublisher
                pub_raw = USNavRawPublisher(factory, debug=use_debug)
                print('usnav_raw')
                print(usnav_raw_items)
                V.add(pub_raw, inputs=usnav_raw_items)

            if cfg.USE_HEDGE_IMU:
                '''
                Marvelmind IMU情報を使用している場合
                '''
                from parts.broker.pub import IMUPublisher
                pub_imu = IMUPublisher(factory, debug=use_debug)
                print('imu')
                print(imu_items)
                V.add(pub_imu, inputs=imu_items)

        '''
        MPU9250/MPU6050 データの送信
        '''
        if cfg.HAVE_IMU:
            '''
            MPU9250/MPU6050 を使用している場合
            '''
            print('mpu')
            print(mpu_items)
            if cfg.IMU_TYPE == 'mpu6050':
                '''
                MPU6050を使用している場合
                '''
                from parts.broker.pub import Mpu6050Publisher
                pub_mpu = Mpu6050Publisher(factory, debug=use_debug)
                V.add(pub_mpu, inputs=mpu_items)
            
            elif cfg.IMU_TYPE == 'mpu9250':
                '''
                MPU6050を使用している場合
                '''
                from parts.broker.pub import Mpu9250Publisher
                pub_mpu = Mpu9250Publisher(factory, debug=use_debug)
                V.add(pub_mpu, inputs=mpu_items)

    '''
    運転ループ
    '''

    try:
        print('Start running')
        #run the vehicle for 20 seconds
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, 
                max_loop_count=cfg.MAX_LOOPS)
    except KeyboardInterrupt:
        # Ctrl+C押下時
        pass
    finally:
        # デバッグ
        if use_debug:
            print('Stop running')
        # pigpio 利用停止
        pgio.stop()
        if use_aws or cfg.USE_AWS_AS_DEFAULT:
            if power is not None:
                # Power Off 情報の送信
                if use_debug:
                    print('Sending power off')
                power.off()
                # 送信するまで待機
                time.sleep(1)
        print('Stopped')


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    
    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']
        use_map = args['--map']
        use_hedge = args['--hedge']
        if use_map and (not use_hedge):
            raise ValueError('map option needs hedge input')
        drive(cfg,
            model_path = args['--model'],
            use_joystick = args['--js'],
            use_hedge = use_hedge,
            use_aws = args['--aws'],
            use_map = use_map,
            use_debug = args['--debug'],
            model_type = model_type,
            camera_type = camera_type,
            meta = args['--meta'])
    
    if args['train']:
        from train import multi_train, preprocessFileList
        
        tub = args['--tub']
        model = args['--model']
        transfer = args['--transfer']
        model_type = args['--type']
        continuous = args['--continuous']
        aug = args['--aug']     

        dirs = preprocessFileList( args['--file'] )
        if tub is not None:
            tub_paths = [os.path.expanduser(n) for n in tub.split(',')]
            dirs.extend( tub_paths )

        multi_train(cfg, dirs, model, transfer, model_type, continuous, aug)

