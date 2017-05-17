# sensortag-ambient

TIのSensorTagを使い、気温、湿度、気圧、照度とバッテリーレベルを測定し、Bluetooth Low Energy(BLE)でRaspberry Pi3(RPi3)に送り、
RPi3から[IoTクラウドサービスAmbient](https://ambidata.io)に送信してグラフ化するためのPythonプログラム。

## 使い方

RPi3上でbluepyとAmbientライブラリーをインストールします。

    pi$ sudo apt-get install python-pip libglib2.0-dev
    pi$ git clone https://github.com/IanHarvey/bluepy.git
    pi$ cd bluepy
    pi$ python3 setup.py build
    pi$ sudo python3 setup.py install
    pi$ sudo pip3 install git+https://github.com/TakehikoShimojima/ambient-python-lib.git

起動にはroot権限が必要なので、次のように動かします。

    pi$ sudo python3 st2ambient.py
