#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for Rohm SensorMedal-EVK-002
# Raspberry Piを使って、センサメダルのセンサ情報を表示します。
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#   pip3 がインストールさせていない場合は、先に下記を実行
#       sudo apt-get update
#       sudo apt-get install python-pip python-dev libglib2.0-dev
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_SensorMedal2.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 3 # 動作間隔

from bluepy import btle
from sys import argv
import getpass
from time import sleep

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
    # BLE受信処理
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print("ERROR",e)
        if getpass.getuser() != 'root':
            print('使用方法: sudo', argv[0])
            exit()
        sleep(interval)
        continue

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        print("\nDevice %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        isRohmMedal = False
        sensors = dict()
        for (adtype, desc, val) in dev.getScanData():
            print("  %s = %s" % (desc, val))
            if desc == 'Short Local Name' and val[0:10] == 'ROHMMedal2':
                isRohmMedal = True
            if isRohmMedal and desc == 'Manufacturer':

                # センサ値を辞書型変数sensorsへ代入
                sensors['ID'] = hex(payval(2,2))
                sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
                sensors['Humidity'] = 100 * payval(6,2) / 65536
                sensors['SEQ'] = payval(8)
                sensors['Condition Flags'] = bin(int(val[16:18],16))
                sensors['Accelerometer X'] = payval(10,2,True) / 4096
                sensors['Accelerometer Y'] = payval(12,2,True) / 4096
                sensors['Accelerometer Z'] = payval(14,2,True) / 4096
                sensors['Accelerometer'] = sensors['Accelerometer X']\
                                         + sensors['Accelerometer Y']\
                                         + sensors['Accelerometer Z']
                sensors['Geomagnetic X'] = payval(16,2,True) / 10
                sensors['Geomagnetic Y'] = payval(18,2,True) / 10
                sensors['Geomagnetic Z'] = payval(20,2,True) / 10
                sensors['Geomagnetic']   = sensors['Geomagnetic X']\
                                         + sensors['Geomagnetic Y']\
                                         + sensors['Geomagnetic Z']
                sensors['Pressure'] = payval(22,3) / 2048
                sensors['Illuminance'] = payval(25,2) / 1.2
                sensors['Magnetic'] = hex(payval(27))
                sensors['Steps'] = payval(28,2)
                sensors['Battery Level'] = payval(30)

                # 画面へ表示
                print('    ID            =',sensors['ID'])
                print('    SEQ           =',sensors['SEQ'])
                print('    Temperature   =',round(sensors['Temperature'],2),'℃')
                print('    Humidity      =',round(sensors['Humidity'],2),'%')
                print('    Pressure      =',round(sensors['Pressure'],3),'hPa')
                print('    Illuminance   =',round(sensors['Illuminance'],1),'lx')
                print('    Accelerometer =',round(sensors['Accelerometer'],3),'g (',\
                                            round(sensors['Accelerometer X'],3),\
                                            round(sensors['Accelerometer Y'],3),\
                                            round(sensors['Accelerometer Z'],3),'g)')
                print('    Geomagnetic   =',round(sensors['Geomagnetic'],1),'uT (',\
                                            round(sensors['Geomagnetic X'],1),\
                                            round(sensors['Geomagnetic Y'],1),\
                                            round(sensors['Geomagnetic Z'],1),'uT)')
                print('    Magnetic      =',sensors['Magnetic'])
                print('    Steps         =',sensors['Steps'],'歩')
                print('    Battery Level =',sensors['Battery Level'],'%')

                '''
                for key, value in sorted(sensors.items(), key=lambda x:x[0]):
                    print('    ',key,'=',value)
                '''
''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/SensorMedal2
pi@raspberrypi:~ $ cd SensorMedal2
pi@raspberrypi:~/SensorMedal2 $ sudo ./ble_logger_SensorMedal2.py

Device ff:e0:9b:XX:XX:XX (random), RSSI=-56 dB
  Short Local Name = ROHMMedal2_9999_01.00
  Flags = 06
  Incomplete 16b Services = 0000180a-0000-1000-8000-00805f9b34fb
  Manufacturer = 01006d6f7cae7c0238ff1800680f20ff05008efd1c051f7000032c005a
    ID            = 0x1
    SEQ           = 124
    Temperature   = 31.17 ℃
    Humidity      = 68.16 %
    Pressure      = 992.639 hPa
    Illuminance   = 93.3 lx
    Accelerometer = 0.92 g ( -0.049 0.006 0.963 g)
    Geomagnetic   = -84.5 uT ( -22.4 0.5 -62.6 uT)
    Magnetic      = 0x3
    Steps         = 44 歩
    Battery Level = 90 %
'''
