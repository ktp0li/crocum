#!/usr/bin/env python3
import argparse
import socket
import base64
import json


def send_to_socket(command, arguments):
    command = json.dumps({'execute': command, 'arguments': arguments})
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(f"/var/run/qemu-server/{args.vm_id}.qga")
    client.send(command.encode())
    answer = client.recv(2048).decode()
    return json.loads(answer)['return']


def qemu_write_file(args):
    file = str(base64.b64encode(bytes(open(args.host_file).read(),
                                      'utf-8')))[2:-1]
    handle = send_to_socket('guest-file-open', {'path': args.remote_file,
                                                'mode': 'w+'})
    commands = {'guest-file-write': {'handle': handle, 'buf-b64': file},
                'guest-file-close': {'handle': handle}}
    for i, j in commands.items():
        send_to_socket(i, j)


def qemu_execute_command(args):
    flags = (args.command.split()[1:] if len(args.command.split()) > 1 else [])
    out = send_to_socket('guest-exec-status',
                         {'pid':
                          send_to_socket('guest-exec',
                                         {'path': args.command.split()[0],
                                          'arg': flags,
                                          'capture-output': True})['pid']})
    out_type = ('out-data' if out.get('out-data') else 'err-data')
    print(f'out: "{base64.b64decode(out[out_type])[:-1].decode()}"')
    print(f'exitcode: {out["exitcode"]}')


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


if __name__ == '__main__':
    args = parse_args()
    args.func(args)
