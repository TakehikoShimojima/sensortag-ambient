# -*- coding: utf-8 -*-
# while True:
#     SensorTagをスキャンし、見つけたデバイスに接続し、
#     温度、湿度、気圧、照度、バッテリーレベルを取得し、Ambientに送信
#
import bluepy
import time
import sys
import argparse
import ambient

def main():
    channelId = チャネルID
    writeKey = 'ライトキー'

    parser = argparse.ArgumentParser()
    parser.add_argument('-i',action='store',type=float, default=120.0, help='scan interval')
    parser.add_argument('-t',action='store',type=float, default=5.0, help='scan time out')

    arg = parser.parse_args(sys.argv[1:])

    scanner = bluepy.btle.Scanner(0)
    am = ambient.Ambient(channelId, writeKey)

    while True:
        dev = None
        print('scanning tag...')
        devices = scanner.scan(arg.t)  # BLEをスキャンする
        for d in devices:
            for (sdid, desc, val) in d.getScanData():
                if sdid == 9 and val == 'CC2650 SensorTag': # ローカルネームが'CC2650 SensorTag'のものを探す
                    dev = d
                    print('found SensorTag, addr = %s' % dev.addr)
        sys.stdout.flush()

        if dev is not None:
            tag = bluepy.sensortag.SensorTag(dev.addr) # 見つけたデバイスに接続する

            tag.IRtemperature.enable()
            tag.humidity.enable()
            tag.barometer.enable()
            tag.battery.enable()
            tag.lightmeter.enable()

            # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
            # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
            time.sleep(1.0)

            data = {}
            data['d1'] = tag.IRtemperature.read()[0]  # set ambient temperature to d1
            data['d2'] = tag.humidity.read()[1]  # set humidity to d2
            data['d3'] = tag.barometer.read()[1]  # set barometer to d3
            data['d5'] = tag.lightmeter.read()  # set light to d5
            data['d4'] = tag.battery.read()  # set battery level to d4

            tag.IRtemperature.disable()
            tag.humidity.disable()
            tag.barometer.disable()
            tag.battery.disable()
            tag.lightmeter.disable()

            print(data)
            r = am.send(data)
            print(r.status_code)
            sys.stdout.flush()

            time.sleep(arg.i)
            # tag.waitForNotifications(arg.t)

            tag.disconnect()
            del tag

if __name__ == "__main__":
    main()
