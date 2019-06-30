#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for Rohm SensorMedal-EVK-002 [UDPデータ送信機能付き]
# Raspberry Piを使って、センサメダルのセンサ情報を表示します。
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#   pip3 がインストールされていない場合は、先に下記を実行
#       sudo apt-get update
#       sudo apt-get install python-pip libglib2.0-dev
#
#【実行方法】
#   実行するときは sudoを付与してください(動作表示あり)
#       sudo ./ble_logger_SensorMedal2_udp_tx.py &
#
#   継続的にバックグラウンドで実行する場合(動作表示なし)
#       sudo nohup ./ble_logger_SensorMedal2_udp_tx.py >& /dev/null &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 3                                            # 動作間隔
udp_to = '255.255.255.255'                              # UDPブロードキャスト
udp_port = 1024                                         # UDPポート番号
device_s = 'medal'                                      # デバイス識別名(5文字)
device_n = '3'                                          # デバイス識別番号(1桁)

from bluepy import btle
from sys import argv
import getpass
from time import sleep
import socket
import threading

mutex = False

def payval(num, bytes=1, sign=False):
    global val
    a = 0
    for i in range(0, bytes):
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:
        if a >= 2 ** (bytes * 8 - 1):
            a -= 2 ** (bytes * 8)
    return a

def send_udp(s):
    global mutex                                # グローバル変数mutexを取得
    mutex.acquire()                             # mutex状態に設定(排他処理開始)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # ソケット作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # ソケット設定
    print(threading.current_thread().name,'send :', s)          # 受信データを出力
    udp_bytes = (s + '\n').encode()                     # バイト列に変換
    try:                                                # 作成部
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
    sock.close()                                        # ソケットの切断
    sleep(0.5)                                          # 送信完了待ち
    mutex.release()                                     # mutex状態の開放

argc = len(argv)                                        # 引数の数をargcへ代入
if argc >= 2:                                           # 入力パラメータ数の確認
    udp_port = argv[1]                                  # ポート番号を設定
    if udp_port < 1 or udp_port > 65535:                # ポート1未満or65535超の時
        udp_port = 1024                                 # UDPポート番号を1024に
else:
    udp_port = 1024

scanner = btle.Scanner()
sensors = dict()
mutex = threading.Lock()                        # 排他処理用のオブジェクト生成
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
        print("\nDevice %s (%s), RSSI=%d dB" % (dev.addr,dev.addrType,dev.rssi))
        isRohmMedal = False
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
                sensors['Accelerometer'] = (sensors['Accelerometer X'] ** 2\
                                          + sensors['Accelerometer Y'] ** 2\
                                          + sensors['Accelerometer Z'] ** 2) ** 0.5
                sensors['Geomagnetic X'] = payval(16,2,True) / 10
                sensors['Geomagnetic Y'] = payval(18,2,True) / 10
                sensors['Geomagnetic Z'] = payval(20,2,True) / 10
                sensors['Geomagnetic']  = (sensors['Geomagnetic X'] ** 2\
                                         + sensors['Geomagnetic Y'] ** 2\
                                         + sensors['Geomagnetic Z'] ** 2) ** 0.5
                sensors['Pressure'] = payval(22,3) / 2048
                sensors['Illuminance'] = payval(25,2) / 1.2
                sensors['Magnetic'] = hex(payval(27))
                sensors['Steps'] = payval(28,2)
                sensors['Battery Level'] = payval(30)
                sensors['RSSI'] = dev.rssi

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

                # 照度センサ
                s = 'illum_' + device_n[0]
                s += ',' + str(round(sensors['Illuminance'],0))
                thread = threading.Thread(target=send_udp, args=([s]))
                thread.start()

                # 環境センサ
                s = 'envir_' + device_n[0]
                s += ',' + str(round(sensors['Temperature'],1))
                s += ',' + str(round(sensors['Humidity'],0))
                s += ',' + str(round(sensors['Pressure'],0))
                thread = threading.Thread(target=send_udp, args=([s]))
                thread.start()

                # 加速度センサ
                s = 'accem_' + device_n[0]
                s += ',' + str(round(sensors['Accelerometer X'],0))
                s += ',' + str(round(sensors['Accelerometer Y'],0))
                s += ',' + str(round(sensors['Accelerometer Z'],0))
                thread = threading.Thread(target=send_udp, args=([s]))
                thread.start()

                # センサメダル
                s = device_s[0:5] + '_' + device_n[0]
                s += ',' + str(round(sensors['Accelerometer'],0))
                s += ',' + str(round(sensors['Geomagnetic'],0))
                s += ',' + str(int(sensors['Magnetic'],16))
                s += ',' + str(sensors['Battery Level'])
                s += ',' + str(sensors['Steps'])
                s += ',' + str(sensors['RSSI'])
                thread = threading.Thread(target=send_udp, args=([s]))
                thread.start()
