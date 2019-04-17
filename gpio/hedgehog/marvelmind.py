#!/usr/bin/env python
#
# marvelmind.py - Marvelmind モバイルビーコンからの USB/シリアルポートによる座標の受信と解析のための小さなクラス
# 作成者： Alexander Rudykh (awesomequality@gmail.com)
#
### 属性：
#
#   pi  - pigpio.pi() オブジェクト
#
#   tty - シリアルポートのデバイス名(物理またはUSB/仮想）。 必ず指定すること：
#       /dev/ttyACM0           -  Linux/Raspberry Piにおける例
#       /dev/tty.usbmodem1451  -  Mac OS Xにおける例
#
#   baud - ボーレート。ヘッジホッグビーコンのボーレートと合わせなくてはなりません。
#       デフォルト: 9600
#
#   maxvaluescount - バッファに格納されている座標の最大測定数
#       デフォルト： 3
#
#   valuesUltrasoundPosition - 測定バッファ
#
#   debug - コンソール出力を有効にするデバッグフラグ    
#       デフォルト： False
#
#   pause - 一時停止フラグ、真値の場合、クラスはシリアルデータを読み込みません。
#
#   terminationRequired - 真値の場合、スレッドはメインループから出て停止します。
#
#
### メソッド：
#
#   __init__ (self, tty="/dev/ttyACM0", baud=9600, maxvaluescount=3, debug=False) 
#       コンストラクタ
#
#   print_position(self)
#       デフォルトフォーマットの最新測定データを出力
#
#   position(self)
#       配列 [x, y, z, timestamp] の最新測定データを返却
#
#   stop(self)
#       無限ループを脱出しポートを閉鎖
#
### 必要となるライブラリ：
#
# このスクリプトで使用されている crcmod モジュールに関するエラーがインストール時に
# 発生しないようにするには、次の一連のコマンドを実行してください。
#   sudo apt-get install python-pip
#   sudo apt-get update
#   sudo apt-get install python-dev
#   sudo pip install crcmod
#
###

###
# 変更履歴:
# lastValues -> valuesUltrasoundPosition
# recieveLinearDataCallback -> recieveUltrasoundPositionCallback
# lastImuValues -> valuesImuRawData
# recieveAccelerometerDataCallback -> recieveImuRawDataCallback
# mm and cm -> m
###

import crcmod
import serial
import struct
import collections
import time
from threading import Thread
import math

# import numpy as np
# import marvelmindQuaternion as mq

class MarvelmindHedge (Thread):
    def __init__ (self, pi, adr, tty="/dev/ttyACM0", baud=9600, maxvaluescount=3, debug=False, recieveUltrasoundPositionCallback=None, recieveImuRawDataCallback=None, recieveImuDataCallback=None, recieveUltrasoundRawDataCallback=None):
        self.tty = tty  # serial
        self.baud = baud  # baudrate
        self.debug = debug  # debug flag
        self._bufferSerialDeque = collections.deque(maxlen=255)  # serial buffer

        self.valuesUltrasoundPosition = collections.deque([[0]*5]*maxvaluescount, maxlen=maxvaluescount) # ultrasound position buffer
        self.recieveUltrasoundPositionCallback = recieveUltrasoundPositionCallback
        
        self.valuesImuRawData = collections.deque([[0]*10]*maxvaluescount, maxlen=maxvaluescount) # raw imu data buffer
        self.recieveImuRawDataCallback = recieveImuRawDataCallback

        self.valuesImuData = collections.deque([[0]*14]*maxvaluescount, maxlen=maxvaluescount) # processed imu data buffer
        self.recieveImuDataCallback = recieveImuDataCallback

        self.valuesUltrasoundRawData = collections.deque([[0]*5]*maxvaluescount, maxlen=maxvaluescount)
        self.recieveUltrasoundRawDataCallback = recieveUltrasoundRawDataCallback


        self.pause = False
        self.terminationRequired = False
        
        self.adr = adr
        self.pi = pi
        self.serialPort = None
        self.handler = None
        Thread.__init__(self)

    def print_position(self):
        if (isinstance(self.position()[1], int)):
            print ("Hedge {:d}: X: {:d} m, Y: {:d} m, Z: {:d} m at time T: {:.2f}".format(self.position()[0], self.position()[1], self.position()[2], self.position()[3], self.position()[4]/1000.0))
        else:
            print ("Hedge {:d}: X: {:.2f}, Y: {:.2f}, Z: {:.2f} at time T: {:.2f}".format(self.position()[0], self.position()[1], self.position()[2], self.position()[3], self.position()[4]/1000.0))

    def position(self):
        return list(self.valuesUltrasoundPosition)[-1]
    
    def stop(self):
        self.terminationRequired = True
        print ("stopping")

    def run(self):      
        while (not self.terminationRequired):
            if (not self.pause):
                try:
                    #if (self.serialPort is None):
                    #    self.serialPort = serial.Serial(self.tty, self.baud, timeout=3)
                    if self.handler is None:
                        self.handler = self.pi.serial_open(self.tty, self.baud)
                    #readChar = self.serialPort.read(1)
                    readChar = self.pi.serial_read(self.handler, 1)
                    while (readChar is not None) and (readChar is not '') and (not self.terminationRequired):
                        self._bufferSerialDeque.append(readChar)
                        #readChar = self.serialPort.read(1)
                        readChar = self.pi.serial_read(self.handler, 1)
                        bufferList = list(self._bufferSerialDeque)
                        
                        strbuf = (b''.join(bufferList))

                        pktHdrOffset = strbuf.find(b'\xff\x47')
                        if (pktHdrOffset >= 0 and len(bufferList) > pktHdrOffset + 4 and pktHdrOffset<220):
#                           print(bufferList)
                            isMmMessageDetected = False
                            isCmMessageDetected = False
                            isRawImuMessageDetected = False
                            isImuMessageDetected = False
                            isDistancesMessageDetected = False
                            pktHdrOffsetCm = strbuf.find(b'\xff\x47\x01\x00')
                            pktHdrOffsetMm = strbuf.find(b'\xff\x47\x11\x00')
                            pktHdrOffsetRawImu = strbuf.find(b'\xff\x47\x03\x00')
                            pktHdrOffsetDistances = strbuf.find(b'\xff\x47\x04\x00')
                            pktHdrOffsetImu = strbuf.find(b'\xff\x47\x05\x00')

                            if (pktHdrOffsetMm!=-1):
                                isMmMessageDetected = True
                                if (self.debug): print ('Message with US-position(mm) was detected')
                            elif (pktHdrOffsetCm!=-1):
                                isCmMessageDetected = True
                                if (self.debug): print ('Message with US-position(cm) was detected')
                            elif (pktHdrOffsetRawImu!=-1):
                                isRawImuMessageDetected = True
                                if (self.debug): print ('Message with raw IMU data was detected')
                            elif (pktHdrOffsetDistances!=-1):
                                isDistancesMessageDetected = True
                                if (self.debug): print ('Message with distances was detected')
                            elif (pktHdrOffsetImu!=-1):
                                isImuMessageDetected = True
                                if (self.debug): print ('Message with processed IMU data was detected')
                            msgLen = ord(bufferList[pktHdrOffset + 4])
                            if (self.debug): print ('Message length: ', msgLen)

                            try:
                                if (len(bufferList) > pktHdrOffset + 4 + msgLen + 2):
                                    usnCRC16 = 0
                                    if (isCmMessageDetected):
                                        usnTimestamp, usnX, usnY, usnZ, usnAdr, usnCRC16 = struct.unpack_from ('<LhhhxBxxxxH', strbuf, pktHdrOffset + 5)
                                        usnX = usnX/100.0
                                        usnY = usnY/100.0
                                        usnZ = usnZ/100.0
                                    elif (isMmMessageDetected):
                                        usnTimestamp, usnX, usnY, usnZ, usnAdr, usnCRC16 = struct.unpack_from ('<LlllxBxxxxH', strbuf, pktHdrOffset + 5)
                                        usnX = usnX/1000.0
                                        usnY = usnY/1000.0
                                        usnZ = usnZ/1000.0
                                    elif (isRawImuMessageDetected):
                                        ax, ay, az, gx, gy, gz, mx, my, mz, timestamp, usnCRC16 = struct.unpack_from ('<hhhhhhhhhxxxxxxLxxxxH', strbuf, pktHdrOffset + 5)
                                    elif (isImuMessageDetected):
                                        x, y, z, qw, qx, qy, qz, vx, vy, vz, ax, ay, az, timestamp, usnCRC16 = struct.unpack_from ('<lllhhhhhhhhhhxxLxxxxH', strbuf, pktHdrOffset + 5)
                                    # add start hori
                                    elif (isDistancesMessageDetected):
                                        HedgeAdr, b1, b1d, b2, b2d, b3, b3d, b4, b4d, timestamp,usnCRC16 = struct.unpack_from ('<BBlxBlxBlxBlxLxxxH', strbuf, pktHdrOffset + 5)
                                    # add start hori

                                    crc16 = crcmod.predefined.Crc('modbus')
                                    crc16.update(strbuf[ pktHdrOffset : pktHdrOffset + msgLen + 5 ])
                                    CRC_calc = int(crc16.hexdigest(), 16)

                                    if CRC_calc == usnCRC16:
                                        if (isMmMessageDetected or isCmMessageDetected):
                                            value = [usnAdr, usnX, usnY, usnZ, usnTimestamp]
                                            self.valuesUltrasoundPosition.append(value)
                                            if (self.recieveUltrasoundPositionCallback is not None):
                                                self.recieveUltrasoundPositionCallback()
                                        elif (isRawImuMessageDetected):
                                            value = [ax, ay, az, gx, gy, gz, mx, my, mz, timestamp]
                                            self.valuesImuRawData.append(value)
                                            if (self.recieveImuRawDataCallback is not None):
                                                self.recieveImuRawDataCallback()
                                        # elif (isDistancesMessageDetected):
                                        #     value = 
                                        #     self.valuesUltrasoundRawData.append(value)
                                        #     if (self.recieveUltrasoundRawDataCallback is not None):
                                        #         self.recieveUltrasoundRawDataCallback()

                                        # add start hori
                                        elif (isDistancesMessageDetected):
                                            value = [HedgeAdr, b1, b1d/1000.0, b2, b2d/1000.0, b3, b3d/1000.0, b4, b4d/1000.0, timestamp]
                                            self.valuesUltrasoundRawData.append(value)
                                            self.distancesUpdated= True
                                            if (self.recieveUltrasoundRawDataCallback is not None):
                                                self.recieveUltrasoundRawDataCallback()
                                        # add end hori

                                        elif (isImuMessageDetected):
                                            value = [x/1000.0, y/1000.0, z/1000.0, qw/10000.0, qx/10000.0, qy/10000.0, qz/10000.0, vx/1000.0, vy/1000.0, vz/1000.0, ax/1000.0,ay/1000.0,az/1000.0, timestamp]
                                            self.valuesImuData.append(value)
                                            if (self.recieveImuDataCallback is not None):
                                                self.recieveImuDataCallback()
                                    else:
                                        if self.debug:
                                            print ('\n*** CRC ERROR')

                                    if pktHdrOffset == -1:
                                        if self.debug:
                                            print ('\n*** ERROR: Marvelmind USNAV beacon packet header not found (check modem board or radio link)')
                                        continue
                                    elif pktHdrOffset >= 0:
                                        if self.debug:
                                            print ('\n>> Found USNAV beacon packet header at offset %d' % pktHdrOffset)
                                    for x in range(0, pktHdrOffset + msgLen + 7):
                                        self._bufferSerialDeque.popleft()
                            except struct.error:
                                print ('smth wrong')
                except OSError:
                    if self.debug:
                        print ('\n*** ERROR: OS error (possibly serial port is not available)')
                    time.sleep(1)
                #except serial.SerialException:
                except:
                    if self.debug:
                        print ('\n*** ERROR: serial port error (possibly beacon is reset, powered down or in sleep mode). Restarting reading process...')
                    self.serialPort = None
                    self.handler = None
                    time.sleep(1)
            else: 
                time.sleep(1)
    
        #if (self.serialPort is not None):
        #    self.serialPort.close()
        if self.handler is not None:
            self.pi.serial_close(self.handler)