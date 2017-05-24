#!/usr/bin/python3
# coding: utf-8

import redis

html_body = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html;charset=utf-8">
    <title>SensorTag List</title>
    <style type="text/css">
        body {
            font-family: Verdana, Arial;
            font-size: 16px;
            background: #ffffff;
        }
        input {
            font-size: 100%%;
            text-align: center;
        }
    </style>
</head>
<body>
<div>
  <h1 style="text-align: center;">SensorTagリスト</h1>
  <table style="margin: 0 auto;" border="0" cellpadding="10">
    <thead>
      <tr>
        <th style="width: 200px;">センサー</th>
        <th>rssi</th>
        <th>電源ボタン</th>
        <th style="width: 100px;">チャネルID</th>
        <th style="width: 200px;">ライトキー</th>
        <th style="width: 100px;">設定</th>
      </tr>
    </thead>
    <tbody>
    %s
    </tbody>
  </table>
</div>
</body></html>"""

r = redis.StrictRedis(host='localhost', port=6379)
addrs = list(k.decode('utf-8') for k in r.keys())
ttemplate = '<form method="POST" action="result.py"><input type="hidden" name="addr" value="%s"><tr><td align="center">%s</td><td align="right">%s</td><td align="center">%s</td><td><input type="number" name="ch" value="%s"></td><td><input type="text" name="writekey" value="%s"></td><td align="center"><input type="submit" value="設定"></td></tr></form>'
tbody = ''
for addr in addrs:
    d = r.hgetall(addr)
    dd = dict([(k.decode('utf-8'), v.decode('utf-8')) for k, v in d.items()])
    ch = dd.get('ch', '')
    if ch == 'None': ch = ''
    writekey = dd.get('writekey', '')
    if writekey == 'None': writekey = ''
    button = dd.get('button', '')
    if button == 'None' or button == '': button = '-'
    tbody += ttemplate % (addr, addr, dd.get('rssi'), button, ch, writekey)

print('Content-type: text/html\r\n')
print(html_body % tbody)
