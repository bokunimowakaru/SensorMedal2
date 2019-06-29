#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for Rohm SensorMedal-EVK-002 [基本]
# Raspberry Piを使って、センサメダルのセンサ情報を表示します。
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

# ご注意：
# bluepy (Bluetooth LE interface for Python)をインストールしてください
#   sudo pip install bluepy
#
# 実行するときは sudoを付与してください
#   sudo ./ble_logger_SensorMedal2_basic.py
#
# 参考文献：本プログラムを作成するにあたり下記を参考にしました
# https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf
# https://ianharvey.github.io/bluepy-doc/scanner.html

from bluepy import btle

def payval(num, bytes=1, sign=False):
    global val
    a = 0
    for i in range(0, bytes):
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:
        if a >= 2 ** (bytes * 8 - 1):
            a -= 2 ** (bytes * 8)
    return a

scanner = btle.Scanner()
while True:
    devices = scanner.scan(3)
    for dev in devices:
        print("Device %s (%s), RSSI=%d dB" % (dev.addr,dev.addrType,dev.rssi))
        isRohmMedal = False
        sensors = dict()
        for (adtype, desc, val) in dev.getScanData():
            if desc == 'Short Local Name' and val[0:10] == 'ROHMMedal2':
                isRohmMedal = True
            if isRohmMedal and desc == 'Manufacturer':
                sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
                sensors['Humidity'] = 100 * payval(6,2) / 65536
                sensors['Pressure'] = payval(22,3) / 2048
                sensors['Illuminance'] = payval(25,2) / 1.2
                for sensor in sensors:
                    print('    ',sensor,'=',round(sensors[sensor],2))

''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/SensorMedal2
pi@raspberrypi:~ $ cd SensorMedal2
pi@raspberrypi:~/SensorMedal2 $ sudo ./ble_logger_SensorMedal2_basic.py
Device ff:e0:9b:XX:XX:XX (random), RSSI=-56 dB
     Humidity = 72.82
     Temperature = 29.31
     Illuminance = 246.67
     Pressure = 992.51
Device ff:e0:9b:XX:XX:XX (random), RSSI=-55 dB
     Humidity = 72.84
     Temperature = 29.38
     Illuminance = 313.33
     Pressure = 992.55
Device ff:e0:9b:XX:XX:XX (random), RSSI=-53 dB
     Humidity = 72.69
     Temperature = 29.35
     Illuminance = 366.67
     Pressure = 992.52
'''
