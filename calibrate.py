# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from time import sleep
import donkeycar as dk




def drive_straight(cfg, pgio, left_balance=1.0, right_balance=1.0):

    from parts import PIGPIO_OUT, PIGPIO_PWM
    left_in1 = PIGPIO_OUT(pin=cfg.LEFT_MOTOR_IN1_GPIO, pgio=pgio)
    left_in2 = PIGPIO_OUT(pin=cfg.LEFT_MOTOR_IN2_GPIO, pgio=pgio)
    left_pwm = PIGPIO_PWM(pin=cfg.LEFT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
            range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD)

    right_in1 = PIGPIO_OUT(pin=cfg.RIGHT_MOTOR_IN1_GPIO, pgio=pgio)
    right_in2 = PIGPIO_OUT(pin=cfg.RIGHT_MOTOR_IN2_GPIO, pgio=pgio)
    right_pwm = PIGPIO_PWM(pin=cfg.RIGHT_MOTOR_PWM_GPIO, pgio=pgio, freq=cfg.PWM_FREQ, 
            range=cfg.PWM_RANGE, threshold=cfg.PWM_INPUT_THRESHOLD)


    from parts import ForkliftMotorDriver
    driver = ForkliftMotorDriver(left_balance=left_balance, right_balance=right_balance)
    left_pwm_v, left_in1_v, left_in2_v, right_pwm_v, right_in1_v, right_in2_v, _, _, _ = driver.run(0.5, 0.0, 0.0)

    print('drive start')
    left_in1.run(left_in1_v)
    left_in2.run(left_in2_v)
    right_in1.run(right_in1_v)
    right_in2.run(right_in2_v)
    left_pwm.run(left_pwm_v)
    right_pwm.run(right_pwm_v)

    sleep(3)
    left_pwm.run(0)
    right_pwm.run(0)
    print('drive end')

def input_balances(left_balance=1.0, right_balance=1.0):
    print('input left balance(current:{}) exit to input not digital value'.format(str(left_balance)))
    try:
        left_balance = float(input().strip())
    except:
        raise
    print('input left balance(current:{}) exit to input not digital value'.format(str(left_balance)))
    try:
        right_balance = float(input().strip())
    except:
        raise
    print('new balance left:{}, right:{}'.format(str(left_balance), str(right_balance)))
    return left_balance, right_balance

if __name__ == '__main__':
    cfg = dk.load_config()

    import pigpio
    try:
        pgio = pigpio.pi()
    except:
        raise
    loop = True
    left_balance = 1.0
    right_balance = 1.0
    print('put car at the test place and push enter key to start driving for 3 seconds')
    input()
    while loop:
        drive_straight(cfg, pgio, left_balance=left_balance, right_balance=right_balance)
        try:
            left_balance, right_balance = input_balances()
        except:
            loop = False
    print('last left_balance={}, right_balance={}'.format(str(left_balance), str(right_balance)))
