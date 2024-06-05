import subprocess

def send_command_say(nickname, msg):
    print(f'<{nickname}> {msg}')
    return

def send_command_list():
    return

def send_command_whitelist_add(nickname):
    return

def send_command_msg(nickname, msg):
    full_command = f"screen -S MinecraftServer -X stuff $'\nmsg {nickname} {msg}\n'"
    result = subprocess.run(full_command, shell=True, check=True, text=True, capture_output=True)
    return