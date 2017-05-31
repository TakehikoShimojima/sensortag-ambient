# sensortag-ambient

TIのSensorTagを使い、気温、湿度、気圧、照度とバッテリーレベルを測定し、Bluetooth Low Energy(BLE)でRaspberry Pi3(RPi3)に送り、
RPi3から[IoTクラウドサービスAmbient](https://ambidata.io)に送信してグラフ化するためのPythonプログラム。

二つのプログラムst2ambient.pyとst2ambient2.pyがあります。

* st2ambient.py: SensorTagで測定した気温、湿度、気圧、照度、バッテリーレベルをBLEで取得し、Ambientに送るプログラム
* st2ambient2.py: 複数台のSensorTagを扱えるようにし、AmbientのチャネルID、ライトキーをSensorTag設定ポータルから設定するバージョン

## st2ambient.pyの使い方

RPi3上でbluepyとAmbientライブラリーをインストールします。

    pi$ sudo apt-get install python-pip libglib2.0-dev
    pi$ git clone https://github.com/IanHarvey/bluepy.git
    pi$ cd bluepy
    pi$ python3 setup.py build
    pi$ sudo python3 setup.py install
    pi$ sudo pip3 install git+https://github.com/TakehikoShimojima/ambient-python-lib.git

起動にはroot権限が必要なので、次のように動かします。

    pi$ sudo python3 st2ambient.py

## st2ambient2.pyの使い方

RPi3上でbluepy、Redis、Ambientライブラリーをインストールします。

    pi$ cd /var
    pi$ sudo mkdir -p www/html
    pi$ cd www/html
    pi$ sudo apt-get install python-pip libglib2.0-dev
    pi$ git clone https://github.com/IanHarvey/bluepy.git
    pi$ cd bluepy
    pi$ python3 setup.py build
    pi$ sudo python3 setup.py install
    pi$ cd bluepy
    pi$ cp blescan.py btle.py bluepy-helper __init__.py sensortag.py uuids.json ../..

    pi$ sudo apt-get install redis-server
    pi$ sudo pip3 install redis

    pi$ sudo pip3 install git+https://github.com/TakehikoShimojima/ambient-python-lib.git

このプログラムをインストールします。

    pi$ cd /var/www/html
    pi$ sudo wget https://github.com/TakehikoShimojima/sensortag-ambient/archive/master.zip
    pi$ sudo unzip master.zip
    pi$ cd sensortag-ambient-master
    pi$ sudo chmod +x cgi-bin/sensortaglist.py cgi-bin/result.py
    pi$ sudo mv * ..
    pi$ cd ..

起動にはroot権限が必要なので、次のように起動します。

    pi$ sudo python3 st2ambient2.py -v

RPi3をログアウトしてもプログラムが終了しないようにするには、次のように起動します。

    pi$ sudo nohup python3 st2ambient2.py -v < /dev/null &

プログラムのオプションは次の二つです。

* -i n: 測定間隔をn秒で指定します。省略時は300秒(5分)間隔になります。
* -v: 動作状況を出力します。

詳しくは[「SensorTagで温度、湿度などを測りRaspberry Pi3経由でAmbientに送ってグラフ化する」](https://ambidata.io/examples/sensortag/)をご覧ください。
