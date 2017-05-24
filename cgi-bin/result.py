#!/usr/bin/python3
# coding: utf-8

import cgi
import redis
import cgitb
cgitb.enable()

html_body = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html;charset=utf-8">
    <title>SensorTag List</title>
</head>
<body>
<div>
  <h1 style="text-align: center;">SensorTagリスト</h1>
  <meta http-equiv="refresh" content="0; URL='sensortaglist.py'" />
</html>"""

r = redis.StrictRedis(host='localhost', port=6379)

print('Content-type: text/html\r\n')
print(html_body)

form=cgi.FieldStorage()
addr = form.getvalue('addr')
ch = form.getvalue('ch')
writekey = form.getvalue('writekey')
if addr:
    r.hmset(addr, {'ch': ch, 'writekey': writekey, 'button': 'None'})
