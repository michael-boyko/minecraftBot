import os

def send_command_say(nickname, msg):
    print(f'<{nickname}> {msg}')
    return

def send_command_list():
    return

def send_command_whitelist_add(nickname):
    return

def send_command_msg(nickname, msg):
    full_command = f"screen -S MinecraftServer -X stuff '\nmsg {nickname} {msg}\n'"
    os.system(full_command)
    return