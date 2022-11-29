import argparse
import socket
import base64
import json
import os


def connect_to_socket(vm_id):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(f"/var/run/qemu-server/{args.vm_id}.qga")
    return client


def open_file(client, filepath):
    command = json.dumps({'execute': 'guest-file-open', 'arguments':
                          {'path': filepath, 'mode': 'w+'}})
    client.send(command.encode())
    answer = client.recv(2048).decode()
    print(answer)
    return json.loads(answer)['return']


def write_file(client, handle, buf_file):
    command = json.dumps({'execute': 'guest-file-write', 'arguments':
                          {'handle': handle, 'buf-b64': buf_file}})
    client.send(command.encode())
    print(client.recv(2048).decode())


def close_file(client, handle):
    command = json.dumps({'execute': 'guest-file-close', 'arguments':
                          {'handle': handle}})
    client.send(command.encode())
    print(command)
    print(client.recv(2048).decode())


def execute(client, remote_command, flags):
    command = json.dumps({'execute': 'guest-exec', 'arguments':
                          {'path': remote_command, 'arg': flags,
                           'capture-output': True}})
    client.send(command.encode())
    answer = client.recv(2048).decode()
    return json.loads(answer)['return']['pid']


def execute_status(client, pid):
    command = json.dumps({'execute': 'guest-exec-status', 'arguments':
                          {'pid': pid}})
    client.send(command.encode())
    answer = json.loads(client.recv(2048).decode())['return']
    return answer['exitcode'], answer['out-data']


def qemu_write_file(args):
    if args.host_file[0] == '/':
        host_file = args.host_file
    else:
        host_file = f'{os.getcwd()}\
/{args.host_file}'
    file = base64.b64encode(bytes(open(host_file).read(), 'utf-8'))
    client = connect_to_socket(args.vm_id)
    path = args.remote_file
    handle = open_file(client, path)
    write_file(client, handle, str(file)[2:-1])
    close_file(client, handle)


def qemu_execute_command(args):
    client = connect_to_socket(args.vm_id)
    flags = []
    command = args.command
    if len(command.split()) > 1:
        flags = command.split()[1:]
        command = command.split()[0]
    exitcode, outdata = execute_status(client, execute(client, command, flags))
    print('exitcode:', exitcode)
    print('output:', base64.b64decode(outdata).decode().replace('\n', ''))


def parse_args():
    parser = argparse.ArgumentParser(
            description='qemu-guest-agent file-* and exec-* commands wrapper')
    subparsers = parser.add_subparsers()
    parser_exec = subparsers.add_parser('exec')
    parser_file = subparsers.add_parser('file')
    parser_file.add_argument('host_file', type=str, help='host file path')
    parser_file.add_argument('remote_file', type=str, help='remote file path')
    parser_exec.add_argument('command', type=str, help='execute command')
    parser_exec.set_defaults(func=qemu_execute_command)
    parser_file.set_defaults(func=qemu_write_file)
    parser.add_argument('vm_id', type=int)
    return parser.parse_args()


args = parse_args()
args.func(args)
