--------------------------------------------------------------------------------
# BLE Logger for Rohm SensorMedal-EVK-002

### Raspberry Piを使って、ローム製「センサメダル」のセンサ情報を表示します。

--------------------------------------------------------------------------------
## ファイル

	基本動作：
		ble_logger_SensorMedal2_basic.py  

	表示のみ：
		ble_logger_SensorMedal2.py  
	
	保存機能付き：
		ble_logger_SensorMedal2_save.py
	
	IoT用クラウドサービスAmbientへの送信機能付き：
		ble_logger_SensorMedal2_ambient.py

## インストール方法

本レポジトリをダウンロードして下さい  

	git clone http://github.com/bokunimowakaru/SensorMedal2

bluepy (Bluetooth LE interface for Python)をインストールしてください  

	bluepyのインストール：
		sudo pip3 install bluepy
	
	pipがインストールされていないとき：
		sudo apt-get update
		sudo apt-get install python-pip python-dev libglib2.0-dev

## 実行方法

実行するときは以下のように sudoを付与してください  

	実行する時はsudoが必要：
		sudo ./ble_logger_SensorMedal2.py

ロガーとして継続的にバックグラウンドで実行する場合は、以下のように先頭に「sudo nohup」を、後方に「>& /dev/null &」を付与して実行ください。

	ロガー機能の実行：
		sudo nohup ./ble_logger_SensorMedal2_save.py >& /dev/null &
		tail -f SensorMedal2.csv

## 実行結果の一例  

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

### 参考文献
本プログラムを作成するにあたり下記を参考にしました  

	https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf  
	https://ianharvey.github.io/bluepy-doc/scanner.html  

--------------------------------------------------------------------------------

Copyright (c) 2019 Wataru KUNINO  
ボクにもわかるIoT  
<https://bokunimo.net/>

