#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import hashlib
import socket
import base64
import struct

class websocket_thread(threading.Thread):
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection

    def run(self):
        print('new websocket client joined!')
        reply = "i got u, from websocket server."
        print('reply before:',reply,type(reply))
        # reply = str.encode(reply)
        print('reply end:',reply,type(reply))
        length = len(reply)
        while True:
            print('kyle.zhang for test run 1')
            data = self.connection.recv(1024)
            print('kyle.zhang for test run 2')
            print("data: '%s'" % data, type(data))
            re = read_msg(data)
            print('re:'+re)
            # self.connection.send(0x81, length, reply)
            reply_msg = write_msg(reply)
            self.connection.send(reply_msg)
            # self.connection.send('%c%c%c' % (0x81, str(length).encode(), reply_msg.encode()))


def read_msg(data):
    msg_len = data[1] & 127  # 数据载荷的长度
    if msg_len == 126:
        mask = data[4:8]  # Mask 掩码
        content = data[8:]  # 消息内容
    elif msg_len == 127:
        mask = data[10:14]
        content = data[14:]
    else:
        mask = data[2:6]
        content = data[6:]

    raw_str = ''  # 解码后的内容
    for i, d in enumerate(content):
        raw_str += chr(d ^ mask[i % 4])
    return raw_str

def write_msg(message):
    data = struct.pack('B', 129)  # 写入第一个字节，10000001

    # 写入包长度
    msg_len = len(message)
    if msg_len <= 125:
        data += struct.pack('B', msg_len)
    elif msg_len <= (2 ** 16 - 1):
        data += struct.pack('!BH', 126, msg_len)
    elif msg_len <= (2 ** 64 - 1):
        data += struct.pack('!BQ', 127, msg_len)
    else:
        print('Message is too long!')
        return

    data += bytes(message, encoding='utf-8')  # 写入消息内容
    print(data)
    return data

def parse_headers(msg):
    msg_str=str(msg,encoding="utf-8")
    headers = {}
    header, data = msg_str.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, value = line.split(': ', 1)
        headers[key] = value
    headers['data'] = data
    return headers


def generate_token(msg):
    key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    print('key before:',key,type(key))
    key = key.encode("utf-8")
    print('key end:',key,type(key))
    ser_key = hashlib.sha1(key).digest()
    print('ser_key:', ser_key, type(ser_key))
    return base64.b64encode(ser_key)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.2', 9002))
    sock.listen(5)

    while True:
        connection, address = sock.accept()
        try:
            data = connection.recv(1024)
            import pprint
            print('data:',data,type(data))
            headers = parse_headers(data)
            pprint.pprint(headers)
            # print('headers:',headers,type(headers))
            token = generate_token(headers['Sec-WebSocket-Key'])
            print('token:',token,type(token))

            print('kyle.zhang for test5')
            #oken = str.encode(token)
            # connection.send(token.decode())
            send_msg = '\
            HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
            Upgrade: WebSocket\r\n\
            Connection: Upgrade\r\n\
            Sec-WebSocket-Accept: %s\r\n\r\n' % token.decode()
            connection.send(send_msg.encode())
            thread = websocket_thread(connection)
            thread.start()
        except socket.timeout:
            print('websocket connection timeout')