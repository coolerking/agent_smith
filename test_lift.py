# -*- coding: utf-8 -*-
from time import sleep
RIGHT_MOTOR_PWM_GPIO = 16
RIGHT_MOTOR_IN1_GPIO = 21
RIGHT_MOTOR_IN2_GPIO = 20

# LEFT MOTOR
LEFT_MOTOR_PWM_GPIO = 26 #13
LEFT_MOTOR_IN1_GPIO = 13 #26
LEFT_MOTOR_IN2_GPIO = 19

# Calibrate angle value (added)
USER_ANGLE_DIFF = 0.0

# LIFT MOTOR
LIFT_MOTOR_PWM_GPIO = 17
LIFT_MOTOR_IN1_GPIO = 22
LIFT_MOTOR_IN2_GPIO = 27


# PWM settings
PWM_FREQ = 50
PWM_RANGE = 255

class ThrottleTest:
    def __init__(self):
        self.values=[0, 0.5, 1.0, 0.7, 0.3, 0, -0.5, -1.0, -0.5, 0]
        self.index = 0
    def run(self):
        value = self.values[self.index]
        self.index = self.index + 1
        if self.index >= len(self.values):
            self.index = 0
        print('{}, next index[{}]'.format(str(value), str(self.index)))
        return value, value, value

    def shutdown(self):
        pass

class PrintTest:
    def __init__(self):
        pass
    
    def shutdown(self):
        pass
    
    def run(self, left_in1, left_in2, left_vref, right_in1, right_in2, right_vref, lift_in1, lift_in2, lift_vref):
        print('')
        print('left   in1:{}, in2:{}, vref:{}'.format(str(left_in1), str(left_in2), str(left_vref)))
        print('right  in1:{}, in2:{}, vref:{}'.format(str(right_in1), str(right_in2), str(right_vref)))
        print('lift   in1:{}, in2:{}, vref:{}'.format(str(lift_in1), str(lift_in2), str(lift_vref)))

def test_motor():
    import pigpio
    pgio = pigpio.pi()
    from parts import PIGPIO_OUT, PIGPIO_PWM
    right_in1 = PIGPIO_OUT(pin=RIGHT_MOTOR_IN1_GPIO, pgio=pgio)
    right_in2 = PIGPIO_OUT(pin=RIGHT_MOTOR_IN2_GPIO, pgio=pgio)
    right_vref = PIGPIO_PWM(pin=RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    right_in1.run(1.0)
    right_in2.run(0.0)
    right_vref.run(0.5)
    print('right fwd')
    sleep(1)
    right_in1.run(0.0)
    right_in2.run(0.0)
    right_vref.run(0.0)
    print('right stop')
    sleep(3)

    left_in1 = PIGPIO_OUT(pin=LEFT_MOTOR_IN1_GPIO, pgio=pgio)
    left_in2 = PIGPIO_OUT(pin=LEFT_MOTOR_IN2_GPIO, pgio=pgio)
    left_vref = PIGPIO_PWM(pin=LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    left_in1.run(1.0)
    left_in2.run(0.0)
    left_vref.run(1.0)
    print('left fwd')
    sleep(1)
    left_in1.run(0.0)
    left_in2.run(0.0)
    left_vref.run(0.0)
    print('left stop')
    sleep(3)

    lift_in1 = PIGPIO_OUT(pin=LIFT_MOTOR_IN1_GPIO, pgio=pgio)
    lift_in2 = PIGPIO_OUT(pin=LIFT_MOTOR_IN2_GPIO, pgio=pgio)
    lift_vref = PIGPIO_PWM(pin=LIFT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    lift_in1.run(1.0)
    lift_in2.run(0.0)
    lift_vref.run(1.0)
    print('lift fwd')
    sleep(2)
    lift_in1.run(0.0)
    lift_in2.run(0.0)
    lift_vref.run(0.0)
    print('lift stop')
    #sleep(3)

    pgio.stop()


def test_driver():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    try:
        V.add(ThrottleTest(), outputs=['throttle', 'steering', 'lift_throttle'])

        from parts import ForkliftMotorDriver #, CalibrateAngle
        #V.add(CalibrateAngle(diff=0.05, debug=True), inputs=['steering'], outputs=['steering'])
        V.add(ForkliftMotorDriver(), 
            inputs=['throttle', 'steering', 'lift_throttle'],
            outputs=[
                'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'])

        V.add(PrintTest(), 
            inputs=[
                'left_motor_in1', 'left_motor_in2', 'left_motor_vref',
                'right_motor_in1', 'right_motor_in2', 'right_motor_vref',
                'lift_motor_in1', 'lift_motor_in2', 'lift_motor_vref'])


        V.start(rate_hz=20, max_loop_count=50)
    except:
        raise

def test_lift():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    import pigpio
    pgio = pigpio.pi()

    from parts import PIGPIO_OUT, PIGPIO_PWM, ForkliftMotorDriver #, CalibrateAngle


    left_in1 = PIGPIO_OUT(pin=LEFT_MOTOR_IN1_GPIO, pgio=pgio)
    left_in2 = PIGPIO_OUT(pin=LEFT_MOTOR_IN2_GPIO, pgio=pgio)
    left_vref = PIGPIO_PWM(pin=LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    right_in1 = PIGPIO_OUT(pin=RIGHT_MOTOR_IN1_GPIO, pgio=pgio)
    right_in2 = PIGPIO_OUT(pin=RIGHT_MOTOR_IN2_GPIO, pgio=pgio)
    right_vref = PIGPIO_PWM(pin=RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    lift_in1 = PIGPIO_OUT(pin=LIFT_MOTOR_IN1_GPIO, pgio=pgio)
    lift_in2 = PIGPIO_OUT(pin=LIFT_MOTOR_IN2_GPIO, pgio=pgio)
    lift_vref = PIGPIO_PWM(pin=LIFT_MOTOR_PWM_GPIO, pgio=pgio, freq=PWM_FREQ, range=PWM_RANGE)

    V.add(ThrottleTest(), outputs=['throttle', 'steering', 'lift_throttle'])

    #V.add(CalibrateAngle(diff=0.00, debug=False), inputs=['steering'], outputs=['steering'])
    #V.mem['dummy_gpio'] = 0

    driver = ForkliftMotorDriver(debug=True)
    V.add(driver, 
            inputs=['throttle', 'steering', 'lift_throttle'],
            outputs=[
                'left_motor_vref', 'left_motor_in1', 'left_motor_in2',
                'right_motor_vref', 'right_motor_in1', 'right_motor_in2',
                'lift_motor_vref', 'lift_motor_in1', 'lift_motor_in2'])

    V.add(lift_in1, inputs=['lift_motor_in1'])
    V.add(lift_in2, inputs=['lift_motor_in2'])
    V.add(lift_vref, inputs=['lift_motor_vref'])

    
    V.add(left_in1, inputs=['left_motor_in1'])
    V.add(left_in2, inputs=['left_motor_in2'])
    V.add(left_vref, inputs=['left_motor_vref'])

    V.add(right_in1, inputs=['right_motor_in1'])
    V.add(right_in2, inputs=['right_motor_in2'])
    V.add(right_vref, inputs=['right_motor_vref'])

    try:
        #V.mem['lift_throttle'] = 0.0
        V.start(rate_hz=20, max_loop_count=2000)

    finally:
        V.mem['throttle'] = 0.0
        V.mem['lift_throttle'] = 0.0
        sleep(1)
        pgio.stop()
        print('test stop')

if __name__ == '__main__':
    test_lift()
    #test_motor()
    #test_driver()

