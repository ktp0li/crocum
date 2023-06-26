import json
import base64
import libvirt
import libvirt_qemu


class QemuGuestAgentCommand:
    def __init__(
        self, args: list, pid: int = None, exitcode: int = None, outdata: str = None
    ):
        self.pid = pid
        self.args = args
        self.exitcode = exitcode
        self.outdata = outdata

    def __repr__(self):
        return (
            f"<QemuGuestAgentCommand pid={self.pid} args={self.args} "
            + f"exitcode={self.exitcode} outdata={self.outdata}>"
        )


class QemuGuestAgentFile:
    def __init__(self, remote_path: str, file_content: bytes):
        self.remote_path = remote_path
        self.file_content = file_content

    def __repr__(self):
        return (
            f"<QemuGuestAgentFile remote_path={self.remote_path} "
            + f"file_content={self.file_content}>"
        )


class QemuGuestAgent:
    def __init__(self, vm_id: int):
        self.vm_id = vm_id

    def __repr__(self):
        return f"<QemuGuestAgent vm_id={self.vm_id}>"

    def _send_command(self, command, arguments) -> str:
        dom = libvirt.open().lookupByName(f"one-{self.vm_id}")
        cmd = libvirt_qemu.qemuAgentCommand(
            dom, json.dumps({"execute": command, "arguments": arguments}), 30, 0
        )
        return json.loads(cmd)["return"]

    def exec_command(self, args: list) -> QemuGuestAgentCommand:
        flags = args[1:] if len(args) > 1 else []
        pid = self._send_command(
            "guest-exec",
            {"path": args[0], "arg": flags, "capture-output": True},
        )
        pid = pid["pid"]
        out = self._send_command("guest-exec-status", {"pid": pid})
        out_type = "out-data" if out.get("out-data") else "err-data"
        outdata = (
            base64.b64decode(out[out_type])[:-1].decode() if out.get(out_type) else None
        )
        exitcode = out["exitcode"] if out.get("exitcode") else None

        return QemuGuestAgentCommand(args, pid, exitcode, outdata)

    def get_output(self, command: QemuGuestAgentCommand) -> QemuGuestAgentCommand:
        out_com = self._send_command("guest-exec-status", {"pid": command.pid})
        if out_com.get("out-data"):
            out = out_com["out-data"][:-1].decode()
        else:
            out = out_com["err-data"][:-1].decode()
        command.outdata = out

        return command

    def send_file(self, remote_path: str, file_content: bytes) -> QemuGuestAgentFile:
        data = str(base64.b64encode(file_content))[2:-1]

        handle = self._send_command(
            "guest-file-open", {"path": remote_path, "mode": "w+"}
        )
        commands = {
            "guest-file-write": {"handle": handle, "buf-b64": data},
            "guest-file-close": {"handle": handle},
        }
        for i, j in commands.items():
            self._send_command(i, j)

        return QemuGuestAgentFile(remote_path, file_content)
