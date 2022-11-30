import libvirt
import libvirt_qemu
import json
import base64
import argparse
import os
import time


def connect_to_vm(id):
    conn = libvirt.open()
    return conn.lookupByID(id)


def exec_command(args):
    flags = []
    command = args.command
    if len(command.split()) > 1:
        flags = command.split()[1:]
        command = command.split()[0]
    dom = connect_to_vm(args.vm_id)
    exec = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': 'guest-exec', 'arguments':
         {'path': command, 'arg': flags, 'capture-output': True}}), 60, 0)
    exec_status = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': 'guest-exec-status', 'arguments':
         {'pid': json.loads(exec)['return']['pid']}}), 60, 0)
    while not (json.loads(exec_status)['return']['exited']):
        print('please wait...')
        time.sleep(2)
        exec_status = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
            {'execute': 'guest-exec-status', 'arguments':
             {'pid': json.loads(exec)['return']['pid']}}), 60, 0)

    print('exitcode:', json.loads(exec_status)['return']['exitcode'])
    print(base64.b64decode(json.loads(exec_status)
                           ['return']['out-data'])[:-1].decode())


def write_file(args):
    host_file = args.host_file
    if host_file[0] != '/':
        host_file = f'{os.getcwd()}/{host_file}'
    buf_file = str(base64.b64encode(bytes(open(host_file).read(),
                                          'utf-8')))[2:-1]
    dom = connect_to_vm(args.vm_id)
    open_file = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': 'guest-file-open', 'arguments':
         {'path': args.remote_file, 'mode': 'w+'}}), 30, 0)
    print(open_file)
    handle = json.loads(open_file)['return']
    write_file = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': 'guest-file-write', 'arguments':
         {'handle': handle, 'buf-b64': buf_file}}), 30, 0)
    print(write_file)
    close_file = libvirt_qemu.qemuAgentCommand(dom, json.dumps(
        {'execute': 'guest-file-close', 'arguments':
         {'handle': handle}}), 30, 0)
    print(close_file)


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


def main():
    args = parse_args()
    args.func(args)


main()
