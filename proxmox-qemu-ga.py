import os
import socket
import base64
import json
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect("/var/run/qemu-server/101.qga")
test = "/tmp/test.py"
file = base64.b64encode(bytes(open('pytest/r1.py').read(), 'utf-8'))


def open_file(filepath):
    command = f"{{'execute':'guest-file-open','arguments':\
{{'path':'{filepath}','mode':'w+'}}}}"
    client.send(command.encode())
    answer = client.recv(2048).decode()
    print(answer)
    return json.loads(answer)['return']


def write_file(handle, buf_file):
    command = f"{{'execute':'guest-file-write',\
'arguments':{{'handle':{handle},'buf-b64':{buf_file}}}}}"
    client.send(command.encode())
    print(command)
    print(client.recv(2048).decode())


def close_file(handle):
    command = f"{{'execute':'guest-file-close',\
'arguments':{{'handle':{handle}}}}}"
    client.send(command.encode())
    print(command)
    print(client.recv(2048).decode())


handle = open_file(test)
write_file(handle, str(file)[1:])
close_file(handle)
