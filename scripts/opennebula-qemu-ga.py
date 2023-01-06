#!/usr/bin/env python3
import libvirt
import libvirt_qemu
import json
import base64
import argparse
import time


def send_command(command, arguments):
    dom = libvirt.open().lookupByName(f'one-{args.vm_id}')
    cmd = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': command, 'arguments': arguments}), 30, 0)
    return json.loads(cmd)['return']


def exec_command(args):
    flags = (args.command.split()[1:] if len(args.command.split()) > 1 else [])
    pid = send_command('guest-exec',
                       {'path': args.command.split()[0],
                        'arg': flags, 'capture-output': True})['pid']
    while not ((out := send_command('guest-exec-status',
                                    {'pid': pid}))['exited']):
        print('please wait..')
        time.sleep(1)
    out_type = ('out-data' if out.get('out-data') else 'err-data')
    print('out: "{0}"'.format(base64.b64decode(out[out_type])[:-1].decode()
                              if out.get(out_type) else ""))
    print(f'exitcode: {out["exitcode"]}')


def write_file(args):
    file = str(base64.b64encode(bytes(open(args.host_file).read(),
                                      'utf-8')))[2:-1]
    handle = send_command('guest-file-open',
                          {'path': args.remote_file, 'mode': 'w+'})
    commands = {'guest-file-write': {'handle': handle, 'buf-b64': file},
                'guest-file-close': {'handle': handle}}
    for i, j in commands.items():
        send_command(i, j)


def parse_args():
    parser = argparse.ArgumentParser(
            description='qemu-guest-agent file-* and exec-* commands wrapper')
    subparsers = parser.add_subparsers()
    parser_exec = subparsers.add_parser('exec')
    parser_file = subparsers.add_parser('file')
    parser_file.add_argument('host_file', type=str, help='host file path')
    parser_file.add_argument('remote_file', type=str, help='remote file path')
    parser_exec.add_argument('command', type=str, help='execute command')
    parser_exec.set_defaults(func=exec_command)
    parser_file.set_defaults(func=write_file)
    parser.add_argument('vm_id', type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.func(args)
