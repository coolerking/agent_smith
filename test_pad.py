# -*- coding: utf-8 -*-
from time import sleep
import donkeycar as dk

def test_pad(cfg):
    from parts import get_js_controller
    controller = get_js_controller(cfg)
    V = dk.vehicle.Vehicle()

    V.add(controller, outputs=['angle', 'throttle', 'lift_throttle', 'mode', 'recording'], threaded=True)

    class Prt:
        def run(self, angle, throttle, lift_throttle, mode, recording):
            print('angle:{}, throttle:{}, lift:{}, mode:{}, rec:{}'.format(
                str(angle), str(throttle), str(lift_throttle), str(mode), str(recording)))
    V.add(Prt(), inputs=['angle', 'throttle', 'lift_throttle', 'mode', 'recording'])

    from parts import ForkliftMotorDriver
    motor_driver = ForkliftMotorDriver(debug=False)
    V.add(motor_driver, 
            inputs=['throttle', 'angle', 'lift_throttle'],
            outputs=[
                'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'
            ])

    class Prt2:
        def run(self,  left_verf, left_in1, left_in2, right_verf, right_in1, right_in2, lift_verf, lift_in1, lift_in2):
            print('ForkliftMD left   verf:{}, in1:{}, in2:{}'.format(str(left_verf), str(left_in1), str(left_in2)))
            print('ForkliftMD right  verf:{}, in1:{}, in2:{}'.format(str(right_verf), str(right_in1), str(right_in2)))
            print('ForkliftMD lift   verf:{}, in1:{}, in2:{}'.format(str(lift_verf), str(lift_in1), str(lift_in2)))

    V.add(Prt2(),inputs=[
                'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'
            ])

    import pigpio

    pgio = pigpio.pi()

    from parts import PIGPIO_OUT, PIGPIO_PWM
    V.add(PIGPIO_OUT(
        pin=cfg.LEFT_MOTOR_IN1_GPIO, pgio=pgio), inputs=['left_motor_in1'])
    V.add(PIGPIO_OUT(
        pin=cfg.LEFT_MOTOR_IN2_GPIO, pgio=pgio), inputs=['left_motor_in2'])
    V.add(PIGPIO_PWM(
        pin=cfg.LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
        range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['left_motor_vref'])

    V.add(PIGPIO_OUT(
        pin=cfg.RIGHT_MOTOR_IN1_GPIO, pgio=pgio), inputs = ['right_motor_in1'])
    V.add(PIGPIO_OUT(
        pin=cfg.RIGHT_MOTOR_IN2_GPIO, pgio=pgio), inputs = ['right_motor_in2'])
    V.add(PIGPIO_PWM(
        pin=cfg.RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
        range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['right_motor_vref'])

    V.add(PIGPIO_OUT(
        pin=cfg.LIFT_MOTOR_IN1_GPIO, pgio=pgio), inputs = ['lift_motor_in1'])
    V.add(PIGPIO_OUT(
        pin=cfg.LIFT_MOTOR_IN2_GPIO, pgio=pgio), inputs = ['lift_motor_in2'])
    V.add(PIGPIO_PWM(
        pin=cfg.LIFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
        range=cfg.PWM_RANGE,  threshold=cfg.PWM_INPUT_THRESHOLD), inputs = ['lift_motor_vref'])

    try:
        V.start(rate_hz=20, max_loop_count=10000)
    except KeyboardInterrupt:
        print('exit')
    finally:
        pgio.stop()


def test_motor(cfg):
    import pigpio
    pgio = pigpio.pi()

    V = dk.vehicle.Vehicle()
    from parts import PIGPIO_OUT, PIGPIO_PWM
    left_in1 = PIGPIO_OUT(
        pin=cfg.LEFT_MOTOR_IN1_GPIO, pgio=pgio)
    left_in2 = PIGPIO_OUT(
        pin=cfg.LEFT_MOTOR_IN2_GPIO, pgio=pgio)
    left_pwm = PIGPIO_PWM(
        pin=cfg.LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
        range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD)

    right_in1 = PIGPIO_OUT(
        pin=cfg.RIGHT_MOTOR_IN1_GPIO, pgio=pgio)
    right_in2 = PIGPIO_OUT(
        pin=cfg.RIGHT_MOTOR_IN2_GPIO, pgio=pgio)
    right_pwm = PIGPIO_PWM(
        pin=cfg.RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
        range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD)
    
    loop = True
    while loop:
        try:
            print('1, 0, 0.4')

            left_in1.run(1)
            left_in2.run(0)
            left_pwm.run(0.4)
            right_in1.run(1)
            right_in2.run(0)
            right_pwm.run(0.4)
            sleep(5)
            print('0, 1, 0.4')
            left_in1.run(0)
            left_in2.run(1)
            left_pwm.run(0.4)
            right_in1.run(0)
            right_in2.run(1)
            right_pwm.run(0.4)
            sleep(5)
        except KeyboardInterrupt:
            loop = False
    left_in1.run(0)
    left_in2.run(0)
    left_pwm.run(0)
    right_in1.run(0)
    right_in2.run(0)
    right_pwm.run(0)
    pgio.stop()
    print('stop')

if __name__ == '__main__':
    cfg = dk.load_config()
    #test_pad(cfg)
    test_motor(cfg)