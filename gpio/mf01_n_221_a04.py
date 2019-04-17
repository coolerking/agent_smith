# -*- coding: utf-8 -*-
"""
ALPHA社製10.2mm Membrane Force Sensor MF01-N-221-A04 (薄膜状感圧センサ)を操作するためのドライバ。

- [データシート](https://docid81hrs3j1.cloudfront.net/medialibrary/2019/02/MF01-N-221-A04.pdf)

pigpoi ベースであるため、pigpiodが実行中である環境下でのみ動作する。
"""
import pigpio

# gpio4

class ForceDriver:
    def __init__(self, pi, read_gpio):
        self.gpio = read_gpio
        self.pi = pi
        self.pi.set_mode(self.gpio, pigpio.INPUT)
    
    def read(self):
        self.pi.read(self.gpio)