import argparse
import socket
import base64
import json
parser = argparse.ArgumentParser(
        description='qemu-guest-agent file-* commands wrapper')
parser.add_argument('-f', '--file', type=str, help='remote file path')
parser.add_argument('filename', nargs='?')
parser.add_argument('-e', '--execute', type=str, help='execute command')
args = parser.parse_args()

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


if args.file:
    path = args.file
    handle = open_file(path)
    write_file(handle, str(file)[1:])
    close_file(handle)

if args.execute:
    command = args.execute.split()[0]
    flags = args.execute.split()[1:]
    print(command, flags)
