# -*- coding: utf-8 -*-
"""
Forklift用WebControllerを提供する。
ただし、リフト操作はできない。
"""

from donkeycar.parts.web_controller.web import LocalWebController

class LocalWebForkliftController(LocalWebController):
    def __init__(self):
        super().__init__()
        self.lift_throttle = 0.0
        print('web controller not support lift controll')

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr
        return self.angle, self.throttle, self.lift_throttle, self.mode, self.recording
        
    def run(self, img_arr=None):
        self.img_arr = img_arr
        return self.angle, self.throttle, self.lift_throttle, self.mode, self.recording

