#! /usr/bin/env python
# -*- coding:utf-8 -*-


import time
from websocket import create_connection
ws = create_connection("ws://127.0.0.2:9002/")
print("Sending 'Hello, World'...")
for i in range(20):
    ws.send("Hello, World %s" % i)
    print("Sent %s",i)
    print("Received...%s",i)
    result = ws.recv()
    print("Received '%s'" % result)
    time.sleep(10)
time.sleep(30)
ws.close()