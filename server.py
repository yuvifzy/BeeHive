# server.py

import socket
import threading
import paramiko
import uuid
from logger import log_event

HOST_KEY = paramiko.RSAKey.generate(2048)


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True


def fake_response(command):
    command = command.strip().lower()

    if command == "whoami":
        return "ubuntu\n"

    elif command == "pwd":
        return "/home/ubuntu\n"

    elif command == "ls":
        return "backup  logs  config  server.py\n"

    elif command == "id":
        return "uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),27(sudo)\n"

    elif command == "uname -a":
        return "Linux prod-server 5.15.0-91-generic x86_64 GNU/Linux\n"

    elif command == "cat /etc/passwd":
        return (
            "root:x:0:0:root:/root:/bin/bash\n"
            "ubuntu:x:1000:1000:ubuntu:/home/ubuntu:/bin/bash\n"
            "mysql:x:112:118:MySQL Server:/nonexistent:/bin/false\n"
        )

    elif command.startswith("cat"):
        return "Permission denied\n"

    elif "wget" in command or "curl" in command:
        return "Connecting... 200 OK\nSaved file to /tmp/payload.sh\n"

    elif "chmod +x" in command:
        return ""

    elif "crontab" in command:
        return "no crontab for ubuntu\n"

    elif "sudo" in command:
        return "ubuntu is not in the sudoers file. This incident will be reported.\n"

    elif command in ["exit", "quit"]:
        return "exit"

    elif command == "":
        return ""

    else:
        return f"{command}: command not found\n"


def handle_client(client, address):
    ip_address = address[0]
    session_id = str(uuid.uuid4())[:8]

    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)

    server = SSHServer()
    transport.start_server(server=server)

    channel = transport.accept(20)

    if channel is None:
        return

    channel.send("Welcome to Ubuntu 22.04 LTS\r\n")
    channel.send("ubuntu@prod-server:~$ ")

    while True:
        try:
            command = ""
            while True:
                char = channel.recv(1).decode("utf-8", errors="ignore")

                if char in ["\r", "\n"]:
                    channel.send("\r\n")
                    break

                if char == "\x03":
                    channel.send("^C\r\nubuntu@prod-server:~$ ")
                    command = ""
                    break

                command += char
                channel.send(char)

            command = command.strip()
            response = fake_response(command)

            if response == "exit":
                channel.send("logout\r\n")
                break

            intent = log_event(session_id, ip_address, command, response)
            print(f"[{session_id}] {ip_address} | {command} -> {intent}")
            channel.send(response.replace("\n", "\r\n"))
            channel.send("ubuntu@prod-server:~$ ")

        except Exception as e:
            print("Client error:", e)
            break

    channel.close()
    transport.close()


def start_server(host="0.0.0.0", port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(100)

    print(f"[+] Honeypot SSH server running on port {port}")

    while True:
        client, address = sock.accept()
        print(f"[+] Connection from {address}")
        thread = threading.Thread(target=handle_client, args=(client, address))
        thread.start()


if __name__ == "__main__":
    start_server()