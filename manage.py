# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car

Usage:
    manage.py (drive) [--model=<model>] [--js] [--range] [--spi] [--hedge] [--aws] [--debug] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer|latent|tflite_linear)] [--camera=(single|stereo)] [--meta=<key:value> ...]
    manage.py (train) [--tub=<tub1,tub2,..tubn>] [--file=<file> ...] (--model=<model>) [--transfer=<model>] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer|tflite_linear)] [--continuous] [--aug]


Options:
    -h --help          Show this screen.
    --js               Use physical joystick.
    --range            Use range sensor
    --spi              Use sensors via SPI
    --hedge            Use Marvelmind Mobile Beacon via USB
    --aws              Use AWS IoT Core
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

def drive(cfg, model_path=None, use_joystick=False, use_range=False, use_spi=False, use_hedge=False, use_aws=False, use_debug=False, model_type=None, camera_type='single', meta=[] ):
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
    import pigpio
    pgio = pigpio.pi()

    #Initialize car
    V = dk.vehicle.Vehicle()

    # v3.0.0よりなくなったTimestampを復活させる
    from parts import Timestamp
    clock = Timestamp()
    V.add(clock, outputs=['timestamp']) # datetime.now() 文字列化

    # AWS IoT Coreを使用する場合
    if use_aws or cfg.USE_AWS_AS_DEFAULT:
        from parts.broker import AWSShadowClientFactory, PowerReporter
        factory = AWSShadowClientFactory(cfg.AWS_CONFIG_PATH, cfg.AWS_THING_NAME)
        # Power ON 情報の送信
        power = PowerReporter(factory, debug=use_debug)
        power.on()

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

    else:
        print("cfg.CAMERA_TYPE", cfg.CAMERA_TYPE)
        if cfg.DONKEY_GYM:
            from donkeycar.parts.dgym import DonkeyGymEnv 
        
        inputs = []
        threaded = True
        print("cfg.CAMERA_TYPE", cfg.CAMERA_TYPE)
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

    # Range Sensor
    if use_range or cfg.USE_RANGE_AS_DEFAULT:
        from parts import get_range_part

        ctr = get_range_part(cfg, pgio)
        V.add(ctr, outputs=['range/cms'])

        if use_aws or cfg.USE_AWS_AS_DEFAULT:
            from parts.broker import RangePublisher
            range_pub = RangePublisher(factory, debug=use_debug)
            V.add(range_pub, inputs=['range/cms', 'timestamp'])

    # Force/Bend Sensors via SPI ADC
    if use_spi or cfg.USE_SPI_AS_DEFAULT:
        from parts import PIGPIO_SPI_ADC

        adc = PIGPIO_SPI_ADC(pgio=pgio,
            vref_volts=cfg.SPI_VREF_VOLTS,
            spi_channel=cfg.SPI_CHANNEL,
            spi_baud=cfg.SPI_BAUD,
            spi_flags=cfg.SPI_FLAGS)
        V.mem['adc_force_ch'] = cfg.ADC_FORCE_CH
        V.mem['adc_bend_ch'] = cfg.ADC_BEND_CH
        V.add(adc, inputs=['adc_force_ch'], outputs=['force/volts'])
        V.add(adc, inputs=['adc_bend_ch'], outputs=['bend/volts'])

        if use_aws or cfg.USE_AWS_AS_DEFAULT:
            from parts.broker import ADCPublisher
            adc_pub = ADCPublisher(factory, debug=use_debug)
            V.add(adc_pub, inputs=['force/volts', 'bend/volts', 'timestamp'])
    
    # Marvelmind Mobile Beacon via USB
    if use_hedge or cfg.USE_HEDGE_AS_DEFAULT:
        hedge_items = [
            'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
            'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
            'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
            'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz',
            'imu/timestamp',
            'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
            'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp'
        ]
        from parts import HedgehogController
        hedge = HedgehogController(tty=cfg.HEDGE_SERIAL_TTY, adr=cfg.HEDGE_ID)
        V.add(hedge, outputs=hedge_items)

        hedge_aws_items = [
            'usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
            'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
            'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
            'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz',
            'imu/timestamp',
            'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
            'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp',
            'timestamp',
        ]
        
        if use_aws or cfg.USE_AWS_AS_DEFAULT:
            from parts.broker import HedgePublisher
            hedge_pub = HedgePublisher(factory, debug=use_debug)
            V.add(hedge_pub, inputs=hedge_aws_items)
        
    if use_joystick or cfg.USE_JOYSTICK_AS_DEFAULT:
        #modify max_throttle closer to 1.0 to have more power
        #modify steering_scale lower than 1.0 to have less responsive steering
        #from donkeycar.parts.controller import get_js_controller
        from parts import get_js_controller
        
        ctr = get_js_controller(cfg)
        
        if cfg.USE_NETWORKED_JS:
            from donkeycar.parts.controller import JoyStickSub
            netwkJs = JoyStickSub(cfg.NETWORK_JS_SERVER_IP)
            V.add(netwkJs, threaded=True)
            ctr.js = netwkJs

        # リフト値の追加
        V.add(ctr, 
            inputs=['cam/image_array'],
            outputs=['user/angle', 'user/throttle', 'user/lift_throttle', 'user/mode', 'recording'],
            threaded=True)

    else:        
        #This web controller will create a web server that is capable
        #of managing steering, throttle, and modes, and more.
        
        from .parts import LocalWebForkliftController
        ctr = LocalWebForkliftController()
        #ctr = LocalWebController()

        V.add(ctr, 
            inputs=['cam/image_array'],
            outputs=['user/angle', 'user/throttle', 'user/lift_throttle', 'user/mode', 'recording'],
            threaded=True)

    #class PrintControll:
    #    def run(self, angle, throttle, lift_throttle):
    #        print('angle={}, throttle={}, lift_throttle={}'.format(str(angle), str(throttle), str(lift_throttle)))
    #    def shutdown(self):
    #        pass
    
    #V.add(PrintControll(), inputs=['user/angle', 'user/throttle', 'user/lift_throttle'])

    #this throttle filter will allow one tap back for esc reverse
    th_filter = ThrottleFilter()
    V.add(th_filter, inputs=['user/throttle'], outputs=['user/throttle'])
    
    #See if we should even run the pilot module. 
    #This is only needed because the part run_condition only accepts boolean
    class PilotCondition:
        def run(self, mode):
            if mode == 'user':
                return False
            else:
                return True       

    V.add(PilotCondition(), inputs=['user/mode'], outputs=['run_pilot'])
    
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
        col = (0, 0, 0)
        for count, color in cfg.RECORD_ALERT_COLOR_ARR:
            if num_records >= count:
                col = color
        return col    

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

    if cfg.AUTO_RECORD_ON_THROTTLE and isinstance(ctr, JoystickController):
        #then we are not using the circle button. hijack that to force a record count indication
        def show_record_acount_status():
            rec_tracker_part.last_num_rec_print = 0
            rec_tracker_part.force_alert = 1
        # F710
        if cfg.CONTROLLER_TYPE == 'F710' or cfg.CONTROLLER_TYPE == 'F710_Forklift':
            ctr.set_button_down_trigger('back', show_record_acount_status)
        # JC-U3912T
        elif cfg.CONTROLLER_TYPE == 'JC-U3912T':
            ctr.set_button_down_trigger('7', show_record_acount_status)
        # default
        else:
            ctr.set_button_down_trigger('circle', show_record_acount_status)

    #Sombrero
    if cfg.HAVE_SOMBRERO:
        from donkeycar.parts.sombrero import Sombrero
        s = Sombrero()

    #IMU
    if cfg.HAVE_IMU:
        #from donkeycar.parts.imu import Mpu6050
        #imu = Mpu6050()
        from parts.sensors.imu import Mpu6050
        imu = Mpu6050(pgio=pgio, 
            bus=cfg.MPC6050_I2C_BUS, address=cfg.MPC6050_I2C_ADDRESS, debug=False)
        V.add(imu, outputs=['imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z'], threaded=True)

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
        inf_input = 'cam/image_array'
    else:
        inf_input = 'cam/normalized/cropped'
        V.add(ImgPreProcess(cfg),
            inputs=['cam/image_array'],
            outputs=[inf_input],
            run_condition='run_pilot')

    #Behavioral state
    if cfg.TRAIN_BEHAVIORS:
        bh = BehaviorPart(cfg.BEHAVIOR_LIST)
        V.add(bh, outputs=['behavior/state', 'behavior/label', "behavior/one_hot_state_array"])
        try:
            ctr.set_button_down_trigger('L1', bh.increment_state)
        except:
            pass

        inputs = [inf_input, "behavior/one_hot_state_array"]  
    #IMU
    elif model_type == "imu":
        #assert(cfg.HAVE_IMU)
        #Run the pilot if the mode is not user.
        if cfg.HAVE_IMU:
            inputs=['cam/image_array',
                'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
                'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z']
        else:
            assert(use_aws or cfg.USE_AWS_AS_DEFAULT)
            inputs=[
                'cam/image_array',
                'imu/ax', 'imu/ay', 'imu/az',
                'imu/vx', 'imu/vy', 'imu/vz'
            ]
    else:
        inputs=[inf_input]

    def load_model(kl, model_path):
        start = time.time()
        print('loading model', model_path)
        kl.load(model_path)
        print('finished loading in %s sec.' % (str(time.time() - start)) )

    def load_weights(kl, weights_path):
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
        from tensorflow.python import keras
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

        #this part will signal visual LED, if connected
        V.add(FileWatcher(model_path, verbose=True), outputs=['modelfile/modified'])

        #these parts will reload the model file, but only when ai is running so we don't interrupt user driving
        V.add(FileWatcher(model_path), outputs=['modelfile/dirty'], run_condition="ai_running")
        V.add(DelayedTrigger(100), inputs=['modelfile/dirty'], outputs=['modelfile/reload'], run_condition="ai_running")
        V.add(TriggeredCallback(model_path, model_reload_cb), inputs=["modelfile/reload"], run_condition="ai_running")

        outputs=['pilot/angle', 'pilot/throttle']


        

        if cfg.TRAIN_LOCALIZER:
            outputs.append("pilot/loc")
    
        V.add(kl, inputs=inputs, 
            outputs=outputs,
            run_condition='run_pilot')            

    V.mem['pilot/lift_throttle'] = 0.0

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

    
    #to give the car a boost when starting ai mode in a race.
    aiLauncher = AiLaunch(cfg.AI_LAUNCH_DURATION, cfg.AI_LAUNCH_THROTTLE, cfg.AI_LAUNCH_KEEP_ENABLED)
    
    V.add(aiLauncher,
        inputs=['user/mode', 'throttle'],
        outputs=['throttle'])

    if isinstance(ctr, JoystickController):
        ctr.set_button_down_trigger(cfg.AI_LAUNCH_ENABLE_BUTTON, aiLauncher.enable_ai_launch)


    class AiRunCondition:
        '''
        A bool part to let us know when ai is running.
        '''
        def run(self, mode):
            if mode == "user":
                return False
            return True

    V.add(AiRunCondition(), inputs=['user/mode'], outputs=['ai_running'])

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
                def run(self,  left_verf, left_in1, left_in2, right_verf, right_in1, right_in2, lift_verf, lift_in1, lift_in2):
                    print('ForkliftMD left   verf:{}, in1:{}, in2:{}'.format(str(left_verf), str(left_in1), str(left_in2)))
                    print('ForkliftMD right  verf:{}, in1:{}, in2:{}'.format(str(right_verf), str(right_in1), str(right_in2)))
                    print('ForkliftMD lift   verf:{}, in1:{}, in2:{}'.format(str(lift_verf), str(lift_in1), str(lift_in2)))

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

    
    #add tub to save data

    inputs=['cam/image_array',
            'user/angle', 'user/throttle', 'user/lift_throttle',
            'user/mode']

    types=['image_array',
           'float', 'float', 'float',
           'str']

    # timestamp
    inputs += ['timestamp']
    # float
    #types += ['float']
    types += ['str']

    if cfg.TRAIN_BEHAVIORS:
        inputs += ['behavior/state', 'behavior/label', "behavior/one_hot_state_array"]
        types += ['int', 'str', 'vector']
    
    if cfg.HAVE_IMU:
        inputs += ['imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z']

        types +=['float', 'float', 'float',
           'float', 'float', 'float']

    # Marvelmind Mobile Beacon 使用時
    elif use_hedge or cfg.USE_HEDGE_AS_DEFAULT:
        inputs += ['usnav/id', 'usnav/x', 'usnav/y', 'usnav/z', 'usnav/angle', 'usnav/timestamp',
            'imu/x', 'imu/y', 'imu/z', 'imu/qw', 'imu/qx', 'imu/qy', 'imu/qz',
            'imu/vx', 'imu/vy', 'imu/vz', 'imu/ax', 'imu/ay', 'imu/az',
            'imu/gx', 'imu/gy', 'imu/gz', 'imu/mx', 'imu/my', 'imu/mz', 'imu/timestamp',
            'dist/id', 'dist/b1', 'dist/b1d', 'dist/b2', 'dist/b2d', 
            'dist/b3', 'dist/b3d', 'dist/b4', 'dist/b4d', 'dist/timestamp']

        types += ['int', 'float',  'float',  'float',  'float', 'float',
            'float', 'float', 'float', 'float', 'float', 'float', 'float',
            'float', 'float', 'float', 'float', 'float', 'float',
            'float', 'float', 'float', 'float', 'float', 'float', 'float',
            'int', 'int', 'float', 'int', 'float',
            'int', 'float', 'int', 'float', 'float']

    # Range Sensor 使用時
    if use_range or cfg.USE_RANGE_AS_DEFAULT:
        inputs +=['range/cms']

        types += ['float']

    # Force/Bend Sensors via SPI ADC 使用時
    if use_spi or cfg.USE_SPI_AS_DEFAULT:
        inputs += ['force/volts', 'bend/volts']

        types += ['float', 'float']

    if cfg.RECORD_DURING_AI:
        inputs += ['pilot/angle', 'pilot/throttle', 'pilot/lift_throttle']
        types += ['float', 'float', 'float']
    
    th = TubHandler(path=cfg.DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
    V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')

    if cfg.PUB_CAMERA_IMAGES:
        from donkeycar.parts.network import TCPServeValue
        from donkeycar.parts.image import ImgArrToJpg
        pub = TCPServeValue("camera")
        V.add(ImgArrToJpg(), inputs=['cam/image_array'], outputs=['jpg/bin'])
        V.add(pub, inputs=['jpg/bin'])

    if type(ctr) is LocalWebController:
        print("You can now go to <your pi ip address>:8887 to drive your car.")
    elif isinstance(ctr, JoystickController):
        print("You can now move your joystick to drive your car.")
        #tell the controller about the tub        
        ctr.set_tub(tub)
        
        if cfg.BUTTON_PRESS_NEW_TUB:
    
            def new_tub_dir():
                V.parts.pop()
                tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
                V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')
                ctr.set_tub(tub)
    
            # F710
            if cfg.CONTROLLER_TYPE == 'F710' or cfg.CONTROLLER_TYPE == 'F710_Forklift':
                ctr.set_button_down_trigger('A', new_tub_dir)
            # JC-U3912T
            elif cfg.CONTROLLER_TYPE == 'JC-U3912T' or cfg.CONTROLLER_TYPE == 'JC-U3912T_Forklift':
                ctr.set_button_down_trigger('12', new_tub_dir)
            # default
            else:
                ctr.set_button_down_trigger('cross', new_tub_dir)

        ctr.print_controls()

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
                if use_debug:
                    print('Sending power off')
                power.off()
                power = None
            if factory is not None:
                if use_debug:
                    print('Disconnecting aws iot')
                factory.disconnect()
                factory = None
        print('Stopped')


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    
    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']
        drive(cfg,
            model_path = args['--model'],
            use_joystick = args['--js'],
            use_range = args['--range'],
            use_spi = args['--spi'],
            use_hedge = args['--hedge'],
            use_aws = args['--aws'],
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

