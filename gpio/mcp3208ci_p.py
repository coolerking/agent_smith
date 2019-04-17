# -*- coding: utf-8 -*-
"""
MCP3208CI-P ADコンバータをあらわすクラス。
Raspberry PiとはSPI通信により接続されるため、
sudo raspi-configにてSPIをenableにしておく必要がある。
また以下とおり結線しておく必要がある。

MCP3208     Pi
-------------------------------------------
Vdd         3.3V
Vref        3.3V(GNDとの間に01.μFのパスコン推奨)
AGND        GND(デジタル側と同じにする)
CLK         GPIO11(SPI_CLK)
OUT         GPIO09(SPI_MISO)
IN          GPIO10(SPI_MOSI)
CS          GPIO(SPI_CE0_N)
DGND        GND(アナログ側と同じにする)
"""
import pigpio
from time import sleep

class ADConverter:
    """
    MCP3208CI-P ADコンバータをあらわすクラス。
    """

    def __init__(self, pi, vref_volts=3.3, 
    spi_channel=0, spi_baud=50000, spi_flags=0, debug=False):
        """
        SPI通信を開く。

        引数：
            pi              pigpio piオブジェクト
            vref_volts      Vrefに接続した電圧(V)
            spi_channel     SPIチャネル
            baud            SPI通信速度(bits/sec)
            spi_flags       SPI フラグ
            debug           ADC読み取りのたびにrawデータを表示させるか
        戻り値：
            なし
        """
        self.pi = pi
        self.vref_volts = vref_volts
        self.handler = pi.spi_open(spi_channel, spi_baud, spi_flags)
        self.debug = debug

    def read_volts(self, channel):
        """
        指定されたチャネルの電圧を取得する。

        引数：
            channel     チャネル(0～7)
        戻り値
            volts       電圧(V)
        """
        c, raw = self.pi.spi_xfer(self.handler, [1, (8 + channel)<<4, 0])
        if self.debug:
            print("c: {0} raw: {1}".format(c, raw))
        raw2 = ((raw[1] & 3) << 8) + raw[2]
        volts = (raw2 * self.vref_volts ) / float(1023)
        volts = round(volts, 4)
        return volts

    def close(self):
        """
        SPI通信をクローズする。
        引数：
            なし
        戻り値：
            なし
        """
        self.debug = False
        self.pi.spi_close(self.handler)
