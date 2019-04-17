# -*- coding: utf-8 -*-
"""
パッシブセンサをまとめてパーツ化したクラスを提供する。
"""

from time import sleep
from .mcp3208ci_p import ADConverter

class PhysicalSensors:
    """
    感圧センサ、曲げセンサを管理するパーツクラス。
    """
    def __init__(self, pi, spi_settings, adc_ch_force=0, adc_ch_bend=1, wait_sec=0.01):
        """
        ADCチャネル設定および感圧センサ結果、曲げセンサ結果を初期化して、ADCインスタンスを
        新規生成する。

        引数：
            pi              pigpioパッケージのpiオブジェクト
            spi_settings    config.pyのSPI_SETTINGS（配列）
            adc_ch_force    感圧センサが接続されたADC CH番号(0-7)
            adc_ch_bend     曲げセンサが接続されたADC CH番号(0-7)
            wait_sec
        戻り値：
            なし
        """
        self.adc_ch_force = adc_ch_force
        self.adc_ch_bend = adc_ch_bend
        self.force_volts = None
        self.bend_volts = None
        self.wait_sec = wait_sec
        self.run_loop = True
        self.adc = ADConverter(pi, spi_settings[0], spi_settings[1], spi_settings[2])

    def update_force_volts(self):
        """
        感圧センサ結果を読み取り、インスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        self.force_volts = self.adc.read_volts(self.adc_ch_force)
    
    def update_bend_volts(self):
        """
        曲げセンサ結果を読み取り、インスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        self.bend_volts = self.adc.read_volts(self.adc_ch_bend)
    
    def update(self):
        """
        マルチスレッドで動作する処理を実装する。
        引数：
            なし
        戻り値：
            なし
        """
        self.update_loop()
    
    def update_loop(self):
        """
        マルチスレッドで動作するループを実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.run_loop:
            self.update_force_volts()
            self.update_bend_volts()
            sleep(self.wait_sec)

    def run(self):
        """
        各センサから結果を読み取り、返却する。
        通常スレッドでの実行の場合呼び出される。
        引数：
            なし
        戻り値：
            force_volts     感圧センサ電圧(感圧なしの場合0V、未実施の場合None)
            bend_volts      曲げセンサ電圧(曲げなしの場合0v、未実施の場合None)
        """
        self.update_force_volts()
        self.update_bend_volts()
        return self.force_volts, self.bend_volts

    def run_threaded(self):
        """
        各インスタンス変数に格納された最新のセンサ結果を返却する。
        引数：
            なし
        戻り値：
            force_volts     感圧センサ電圧(感圧なしの場合0V、未実施の場合None)
            bend_volts      曲げセンサ電圧(曲げなしの場合0v、未実施の場合None)
        """
        return self.force_volts, self.bend_volts
    
    def shutdown(self):
        """
        スレッド内ループを終了し、SPI通信を終了する。
        引数：
            なし
        戻り値：
            なし
        """
        self.run_loop = False
        self.force_volts = None
        self.bend_volts = None
        self.adc.close()