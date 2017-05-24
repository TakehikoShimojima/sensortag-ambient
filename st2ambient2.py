# -*- coding: utf-8 -*-
# scanthreadを起動
# while True:
#     SensorTagをスキャンし、見つけたらSensorTagのオブジェクトを作り、スレッドを起動
#
# SensorTagオブジェクトのスレッド
# while True:
#     温度、湿度、気圧、照度、バッテリーレベルを取得し、Ambientに送信する
#     SensorTagとの接続が切れたら再接続する
#
# メインスレッド
# httpサーバー
#
import bluepy
import struct
import threading
import time
from datetime import datetime as dt
import sys
import argparse
import http.server
import redis
import ambient

BTNAME='Complete Local Name'
MAXDEVICES=16

sensors = [
#    'accelerometer'
    'barometer'
    ,'battery'
#    ,'gyroscope'
    ,'humidity'
    ,'IRtemperature'
#    ,'keypress'
    ,'lightmeter'
#    ,'magnetometer'
]

class NotificationDelegate(bluepy.btle.DefaultDelegate):
    POWER_BUTTON = 0x02

    def __init__(self, sensortag):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.sensortag = sensortag
        self.button = 0

    # ノーティフィケーションハンドラー  ボタンが押された時に呼ばれる
    def handleNotification(self, cHandle, data):
        button = struct.unpack("B", data)[0]
        print('button %d on dev %s' % (button, self.sensortag.tag.addr))
        if not self.button & self.POWER_BUTTON and button & self.POWER_BUTTON:
            if self.sensortag.r:
                self.sensortag.r.hset(self.sensortag.tag.addr, 'button', 'on')
        self.button = button

class _SensorTag():
    def __init__( self, dev, devdata ):
        self.tag = bluepy.sensortag.SensorTag(dev.addr)
        self.r = redis.StrictRedis(host='localhost', port=6379)
        self.notification = NotificationDelegate(self)
        self.tag.withDelegate(self.notification)
        self.tag.keypress.enable()

        self.devdata = devdata
        self.name = self.devdata[ BTNAME ]
        self.addr = dev.addr
        self.rssi = dev.rssi
        self.addrType = dev.addrType
        self.devicetype = "Sensortag CC2650"
    def unpair(self):
        if args.d:
            print('unpairing %s' % self)
        self.running = False
        self.thread.join()
        pass
    def _sensorlookup(self, sensorname):
        if not hasattr(self.tag, sensorname):
            if args.d:
                print('not found %s' % sensorname)
            return None
        return getattr(self.tag,sensorname)

    def start(self, interval):
        if args.d:
            print('starting')
        self.r.hset(self.addr, 'rssi', self.rssi)
        self.am = None
        self.running = True
        self.thread = threading.Thread(target=self.runner, args=(sensors, interval))
        self.thread.daemon = True
        self.thread.start()
    def reconnect(self):
        try:
            if args.d:
                print('try to reconnect...')
            self.tag.connect(self.addr)
            if args.d:
                print('reconnected.')
            return True
        except bluepy.btle.BTLEException:
            if args.d:
                print('reconnect failed.')
            return False
        return True
    def sendambient(self, sensorval):
        data = {}
        data['d1'] = sensorval['IRtemperature'][0]
        data['d2'] = sensorval['humidity'][1]
        data['d3'] = sensorval['barometer'][1]
        data['d5'] = sensorval['lightmeter']
        data['d4'] = sensorval['battery']
        if not self.am:
            d = self.r.hgetall(self.addr)
            dd = dict([(k.decode('utf-8'), v.decode('utf-8')) for k, v in d.items()])
            ch = dd.get('ch', '')
            if ch == 'None': ch = ''
            writekey = dd.get('writekey', '')
            if writekey == 'None': writekey = ''
            if ch != '' and writekey != '':
                self.am = ambient.Ambient(ch, writekey)
        if args.d:
            print(dt.now().strftime("%Y/%m/%d %H:%M:%S"), end='')
            print(data)
        if self.am:
            ret = self.am.send(data)
            if args.d:
                print('sent to Ambient (ret: %d)' % ret.status_code)
        sys.stdout.flush()
    def runread(self, sensors):
        sensorval = {}
        try:
            for sensor in sensors: # sensorsにあるセンサーをenableにする
                tagfn = self._sensorlookup(sensor)
                if tagfn:
                    tagfn.enable()
            time.sleep( 1.0 )
            for sensor in sensors: # sensorsにあるセンサーを読んで、disableにする
                tagfn = self._sensorlookup(sensor)
                if tagfn:
                    sensorval[sensor] = tagfn.read()
                    tagfn.disable()
        except bluepy.btle.BTLEException as e:
            if args.d:
                print('BTLE Exception while reading.')
            return False
        self.sendambient(sensorval)
        return True
    def runner(self, sensors, interval):
        while self.running:
            if args.d:
                print('thread running(%s)' % self.addr)
                sys.stdout.flush()
            while True:
                if self.runread(sensors): # センサーを読み、うまくいけばbreak
                    break
                while True: # うまくいくまで再接続を試みる
                    if self.reconnect():
                        self.tag.keypress.enable() # DISCONNECT例外が起きるとkeypressはdisableになるようなので、再度enabeにする
                        break;
            try:
                self.tag.waitForNotifications(interval)
            except bluepy.btle.BTLEException:
                print('BTLE Exception while waitForNotifications')
                while True: # うまくいくまで再接続を試みる
                    if self.reconnect():
                        self.tag.keypress.enable()
                        break;
        if args.d:
            print('Aborting')

class ScanDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.devaddrs = []
        self.activedevlist = []

    # スキャンハンドラー  アドバタイズデーターを受信すると呼ばれる
    # isNewDev は新しいMACアドレスのデバイスを見つけるとTrueになるとbluepyの資料には書いてあるが、
    # http://ianharvey.github.io/bluepy-doc/delegate.html
    # 実際にはscan()を呼ぶごとにisNewDevがTrueになることがある
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            # if args.d:
            #     print("New device found: %s, %d, %d" % (dev.addr, isNewDev, isNewData))
            if len(self.activedevlist)<MAXDEVICES:
                devdata = {}
                for (adtype, desc, value) in dev.getScanData():
                    devdata[desc]=value
                if BTNAME not in devdata.keys():
                    devdata[BTNAME] = 'Unknown!'
                if devdata[BTNAME] == 'CC2650 SensorTag':
                    # devaddrs[]にSensorTagのaddrを記録し、新しいデバイスが見つかったときだけ
                    # __SensorTagオブジェクトのインスタンスを作る
                    if dev.addr in self.devaddrs:
                        if args.d:
                            print('Known SensorTag %s' % dev.addr)
                        return
                    if args.d:
                        print('New SensorTag %s' % dev.addr)
                        sys.stdout.flush()
                    self.devaddrs.append(dev.addr)
                    thisdev = _SensorTag(dev, devdata)
                    self.activedevlist.append(thisdev)
                    thisdev.start(args.i)
            else:
                if args.d:
                    print('TOO MANY DEVICES - IGNORED %s' % dev.addr)
        elif isNewData:
            # if args.d:
            #     print('Received new data from %s' % dev.addr)
            pass

    def shutdown( self ):
        if args.d:
            print('My activedevlist= %s' % self.activedevlist)
        for dev in self.activedevlist:
            if args.d:
                print('dev= %s' % dev)
            dev.unpair()

def runscan():
    scandelegate = ScanDelegate()
    scanner = bluepy.btle.Scanner().withDelegate(scandelegate)

    try:
        while True:
            try:
                devices = scanner.scan(timeout=30.0) # スキャンする。デバイスを見つけた後の処理はScanDelegateに任せる
            except bluepy.btle.BTLEException:
                if args.d:
                    print('BTLE Exception while scannning.')
    except KeyboardInterrupt:
        pass

    # scandelegate.shutdown()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',action='store',type=float, default=300.0, help='measurement interval in seconds')
    parser.add_argument('-d',action='store_true', help='debug msg on')

    global args
    args = parser.parse_args(sys.argv[1:])

    scanthread = threading.Thread(target=runscan, args=())
    scanthread.daemon = True
    scanthread.start()

    server_address = ("", 80)
    handler_class = http.server.CGIHTTPRequestHandler #1 ハンドラを設定
    server = http.server.HTTPServer(server_address, handler_class)
    server.serve_forever()

if __name__ == "__main__":
    main()
