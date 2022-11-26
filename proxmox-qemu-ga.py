import socket
import base64
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect("/var/run/qemu-server/101.qga")
handler = 0
test = "/tmp/test.py"


def open_file(file):
    command = f"{{'execute':'guest-file-open','arguments':\
{{'path':'{file}','mode':'w+'}}}}"
    client.send(command.encode())
    print(client.recv(2048).decode())


open_file(test)
