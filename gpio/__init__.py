# -*- coding: utf-8 -*-
#
# sudo apt update
# sudo apt install pigpio
# sudo pigpiod (sudo systemctl start pigpiod)

# 疑似PWMを使用する場合
from .pu_pwm import PowerUnit
# I2C通信を使用する場合
#from .pu_i2c import PowerUnit
from .range import RangeSensor
from .passive_spi import PhysicalSensors

