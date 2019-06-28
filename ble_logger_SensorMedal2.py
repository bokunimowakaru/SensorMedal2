#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for Rohm SensorMedal-EVK-002
# Raspberry Piを使って、センサメダルのセンサ情報を表示します。
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

# ご注意：
# bluepy (Bluetooth LE interface for Python)をインストールしてください
#   sudo pip install bluepy
#
# 実行するときは sudoを付与してください
#   sudo ./ble_logger_SensorMedal2.py
#
# 参考文献：本プログラムを作成するにあたり下記を参考にしました
# https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf
# https://ianharvey.github.io/bluepy-doc/scanner.html

from bluepy import btle

def payval(number, bytes=1, sign=False):
    global val
    p = (number - 2) * 2
    ret = int(val[p:p+2],16)
    if bytes >= 2:
        p += 2
        ret += 256 * int(val[p:p+2],16)
    if bytes >= 3:
        p += 2
        ret += 65536 * int(val[p:p+2],16)
    if sign:
        if ret >= 2 ** (bytes * 7):
            ret -= 2 ** (bytes * 8)
    return ret

scanner = btle.Scanner()
while True:
    devices = scanner.scan(3)   # timeout in seconds
    for dev in devices:
        print("\nDevice %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        isRohmMedal = False
        sensors = dict()
        for (adtype, desc, val) in dev.getScanData():
            print("  %s = %s" % (desc, val))
            if desc == 'Short Local Name' and val[0:10] == 'ROHMMedal2':
                isRohmMedal = True
            if isRohmMedal and desc == 'Manufacturer':
                sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
                sensors['Humidity'] = 100 * payval(6,2) / 65536
                sensors['SEQ'] = payval(8)
                sensors['Condition Flags'] = bin(int(val[16:18],16))
                sensors['Accelerometer X'] = payval(10,2,True) / 4096
                sensors['Accelerometer Y'] = payval(12,2,True) / 4096
                sensors['Accelerometer Z'] = payval(14,2,True) / 4096
                sensors['Geomagnetic X'] = payval(16,2,True) / 10
                sensors['Geomagnetic Y'] = payval(18,2,True) / 10
                sensors['Geomagnetic Z'] = payval(20,2,True) / 10
                sensors['Pressure'] = payval(22,3) / 2048
                sensors['Illuminance'] = payval(25,2) / 1.2
                sensors['Magnetic'] = hex(payval(27))
                sensors['Steps'] = payval(28,2)
                sensors['Battery Level'] = payval(30)

                '''
                for key, value in sorted(sensors.items(), key=lambda x:x[0]):
                    print('    ',key,'=',value)
                '''
                print('    SEQ           =',sensors['SEQ'])
                print('    Temperature   =',round(sensors['Temperature'],2),'℃')
                print('    Humidity      =',round(sensors['Humidity'],2),'%')
                print('    Accelerometer =',round(sensors['Accelerometer X'],3),\
                                            round(sensors['Accelerometer Y'],3),\
                                            round(sensors['Accelerometer Z'],3),'g')
                print('    Geomagnetic   =',round(sensors['Geomagnetic X'],1),\
                                            round(sensors['Geomagnetic Y'],1),\
                                            round(sensors['Geomagnetic Z'],1),'uT')
                print('    Pressure      =',round(sensors['Pressure'],3),'hPa')
                print('    Illuminance   =',round(sensors['Illuminance'],1),'lx')
                print('    Magnetic      =',sensors['Magnetic'])
                print('    Steps         =',sensors['Steps'],'歩')
                print('    Battery Level =',sensors['Battery Level'],'%')

''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/SensorMedal2
pi@raspberrypi:~ $ cd SensorMedal2
pi@raspberrypi:~/SensorMedal2 $ sudo ./ble_logger_SensorMedal2.py

Device ff:e0:9b:XX:XX:XX (random), RSSI=-56 dB
  Short Local Name = ROHMMedal2_9999_01.00
  Flags = 06
  Incomplete 16b Services = 0000180a-0000-1000-8000-00805f9b34fb
  Manufacturer = 01007d6f28bb30042dff3500b2ef68ffdbffd2ff27071f00000300005a
    SEQ           = 48
    Temperature   = 31.21 ℃
    Humidity      = 73.108 %
    Accelerometer = -0.052 0.013 -1.019 g
    Geomagnetic   = -15.2 -3.7 -4.6 uT
    Pressure      = 992.894 hPa
    Illuminance   = 0.0 lx
    Magnetic      = 0x3
    Steps         = 0 歩
    Battery Level = 90 %
'''
