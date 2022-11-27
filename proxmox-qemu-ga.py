import os
import socket
import base64
import json
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect("/var/run/qemu-server/101.qga")
test = "/tmp/test.py"


def open_file(file):
    command = f"{{'execute':'guest-file-open','arguments':\
{{'path':'{file}','mode':'w+'}}}}"
    client.send(command.encode())
    answer = client.recv(2048).decode()
    return json.loads(answer)['return']


handler = open_file(test)
