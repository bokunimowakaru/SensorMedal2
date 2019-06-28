#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for Rohm SensorMedal-EVK-002 [Ambientへのデータ送信機能付き]
# Raspberry Piを使って、センサメダルのセンサ情報を表示します。
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

# ご注意：
# bluepy (Bluetooth LE interface for Python)をインストールしてください
#   sudo pip install bluepy
#
# 実行するときは sudoを付与してください
#   sudo ./ble_logger_SensorMedal2_ambient.py
#
# 参考文献：本プログラムを作成するにあたり下記を参考にしました
# https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf
# https://ianharvey.github.io/bluepy-doc/scanner.html

from bluepy import btle
ambient_chid='0000'                 # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, \
            'd1':0, 'd2':0, 'd3':0, 'd4':0, 'd5':0, 'd6':0, 'd7':0, 'd8':0}

def save(filename, data):
    try:
        fp = open(filename, mode='a')                   # 書込用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
    fp.write(data + '\n')                               # dataをファイルへ
    fp.close()                                          # ファイルを閉じる

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
    devices = scanner.scan(30)   # timeout in seconds
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

                body_dict['d1'] = sensors['Temperature']
                body_dict['d2'] = sensors['Humidity']
                body_dict['d3'] = sensors['Pressure']
                body_dict['d4'] = sensors['Illuminance']
                body_dict['d5'] = sensors['Accelerometer X'] + sensors['Accelerometer Y'] + sensors['Accelerometer Z']
                body_dict['d6'] = sensors['Geomagnetic X'] + sensors['Geomagnetic Y'] + sensors['Geomagnetic Z']
                body_dict['d7'] = sensors['Steps']
                body_dict['d8'] = sensors['Battery Level']

                print(head_dict)                                # 送信ヘッダhead_dictを表示
                print(body_dict)                                # 送信内容body_dictを表示
                post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                                # POSTリクエストデータを作成
                try:                                            # 例外処理の監視を開始
                    res = urllib.request.urlopen(post)          # HTTPアクセスを実行
                except Exception as e:                          # 例外処理発生時
                    print(e,url_s)                              # エラー内容と変数url_sを表示
                    exit()                                      # プログラムの終了
                res_str = res.read().decode()                   # 受信テキストを変数res_strへ
                res.close()                                     # HTTPアクセスの終了
                if len(res_str):                                # 受信テキストがあれば
                    print('Response:', res_str)                 # 変数res_strの内容を表示
                else:
                    print('Done')                               # Doneを表示
