import time
#import RPi.GPIO as GPIO

class LED:
    ''' 
    Toggle a GPIO pin for led control
    '''
    def __init__(self, pgio, pin):
        import pigpio
        self.pi = pgio or pigpio.pi() 
        self.pin = pin_to_gpio(pin)

        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(self.pin, GPIO.OUT)
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.blink_changed = 0
        self.on = False

    def toggle(self, condition):
        if condition:
            #GPIO.output(self.pin, GPIO.HIGH)
            self.pi.write(self.pin, 1)
            self.on = True
        else:
            #GPIO.output(self.pin, GPIO.LOW)
            self.pi.write(self.pin, 0)
            self.on = False            

    def blink(self, rate):
        if time.time() - self.blink_changed > rate:
            self.toggle(not self.on)
            self.blink_changed = time.time()

    def run(self, blink_rate):
        if blink_rate == 0:
            self.toggle(False)
        elif blink_rate > 0:
            self.blink(blink_rate)
        else:
            self.toggle(True)

    def shutdown(self):
        self.toggle(False)
        self.pi = None        
        #GPIO.cleanup()


class RGB_LED:
    ''' 
    Toggle a GPIO pin on at max_duty pwm if condition is true, off if condition is false.
    Good for LED pwm modulated
    '''
    def __init__(self, pgio, pin_r, pin_g, pin_b, invert_flag=False):
        import pigpio
        self.pi = pgio or pigpio.pi()
        self.pin_r = pin_to_gpio(pin_r)
        self.pin_g = pin_to_gpio(pin_g)
        self.pin_b = pin_to_gpio(pin_b)
        self.invert = invert_flag
        print('setting up gpio in board mode')
        #GPIO.setwarnings(False)
        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(self.pin_r, GPIO.OUT)
        self.pi.set_mode(self.pin_r, pigpio.OUTPUT)
        #GPIO.setup(self.pin_g, GPIO.OUT)
        self.pi.set_mode(self.pin_g, pigpio.OUTPUT)
        #GPIO.setup(self.pin_b, GPIO.OUT)
        self.pi.set_mode(self.pin_b, pigpio.OUTPUT)
        freq = 50
        #self.pwm_r = GPIO.PWM(self.pin_r, freq)
        self.pi.set_PWM_frequency(self.pin_r, freq)
        #self.pwm_g = GPIO.PWM(self.pin_g, freq)
        self.pi.set_PWM_frequency(self.pin_g, freq)
        #self.pwm_b = GPIO.PWM(self.pin_b, freq)
        self.pi.set_PWM_frequency(self.pin_b, freq)
        #self.pwm_r.start(0)
        self.pi.set_PWM_dutycycle(self.pin_r, 0)
        #self.pwm_g.start(0)
        self.pi.set_PWM_dutycycle(self.pin_g, 0)
        #self.pwm_b.start(0)
        self.pi.set_PWM_dutycycle(self.pin_b, 0)
        self.zero = 0
        if( self.invert ):
            self.zero = 100

        self.rgb = (50, self.zero, self.zero)

        self.blink_changed = 0
        self.on = False

    def toggle(self, condition):
        if condition:
            r, g, b = self.rgb
            self.set_rgb_duty(r, g, b)
            self.on = True
        else:
            self.set_rgb_duty(self.zero, self.zero, self.zero)
            self.on = False

    def blink(self, rate):
        if time.time() - self.blink_changed > rate:
            self.toggle(not self.on)
            self.blink_changed = time.time()

    def run(self, blink_rate):
        if blink_rate == 0:
            self.toggle(False)
        elif blink_rate > 0:
            self.blink(blink_rate)
        else:
            self.toggle(True)

    def set_rgb(self, r, g, b):
        r = r if not self.invert else 100-r
        g = g if not self.invert else 100-g
        b = b if not self.invert else 100-b
        self.rgb = (r, g, b)
        self.set_rgb_duty(r, g, b)

    def set_rgb_duty(self, r, g, b):
        #self.pwm_r.ChangeDutyCycle(r)
        self.pi.set_PWM_dutycycle(self.pin_r, r)
        #self.pwm_g.ChangeDutyCycle(g)
        self.pi.set_PWM_dutycycle(self.pin_g, g)
        #self.pwm_b.ChangeDutyCycle(b)
        self.pi.set_PWM_dutycycle(self.pin_b, b)

    def shutdown(self):
        self.toggle(False)
        self.pi = None
        #GPIO.cleanup()

"""
Raspberry Pi 3B+ のピン番号・GPIO番号マップ
"""
PI3BP_PIN2GPIO = {
    #1: -1,     # 3.3V
    #2: -1,     # 5V
    3: 2,       # SDA1
    #4: -1,     # 5V
    5: 3,       # SCL1
    #6: -1,     # GND
    7: 4,       # GPIO_GCLK
    8: 14,      # TXD0
    #9: -1,     # GND
    10: 15,     # RXD0
    11: 17,     # GPIO_GEN0
    12: 18,     # GPIO_GEN1
    13: 27,     # GPIO_GEN2
    #14: -1,    # GND
    15: 22,     # GPIO_GEN3
    16: 23,     # GPIO_GEN4
    #17: -1,    # 3.3V
    18: 24,     # GPIO_GEN5
    19: 10,     # SPI_MOSI
    #20: -1,    # GND
    21: 9,      # SPI_MISO
    22: 25,     # SPI_GPIO_GEN6
    23: 11,     # SPI_CLK
    24: 8,
    #25: -1,    # GND
    26: 7,
    #27: -1,    # ID_SD
    #28: -1,    # ID_SC
    29: 5,
    #30: -1,    # GND
    31: 6,
    32: 12,
    33: 13,
    #34: -1,    # GND
    35: 19,
    36: 16,
    37: 26,
    38: 20,
    #39: -1,    # GND
    40: 21,
}
def pin_to_gpio(pin):
    """
    Raspberry Pi 3B+ のGPIO番号を返却
    引数：
        pin         ピン番号
    戻り値：
        gpio番号
    例外：
        ValueError  存在しない場合
    """
    gpio = PI3BP_PIN2GPIO.get(pin, -1)
    if gpio == -1:
        raise ValueError('pin no {} does not have gpio no')
    return gpio

if __name__ == "__main__":
    import time
    import sys
    import pigpio
    pin_r = int(sys.argv[1])
    pin_g = int(sys.argv[2])
    pin_b = int(sys.argv[3])
    rate = float(sys.argv[4])
    print('output pin', pin_r, pin_g, pin_b, 'rate', rate)

    pi = pigpio.pi()
    p = RGB_LED(pi, pin_r, pin_g, pin_b)
    
    iter = 0
    while iter < 50:
        p.run(rate)
        time.sleep(0.1)
        iter += 1
    
    delay = 0.1

    iter = 0
    while iter < 100:
        p.set_rgb(iter, 100-iter, 0)
        time.sleep(delay)
        iter += 1
    
    iter = 0
    while iter < 100:
        p.set_rgb(100 - iter, 0, iter)
        time.sleep(delay)
        iter += 1

    p.shutdown()
    pi.stop()

