import subprocess
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

MAIN_COMMAND = 'screen -S MinecraftServer -X stuff'

def send_command_say(nickname, msg):
    print(f'<{nickname}> {msg}')
    return

def send_command_list():
    return

def send_command_whitelist_add(nickname):
    return

def send_command_msg(nickname, msg):
    local_command = f'\nmsg {nickname} {msg}\n'
    full_command = f'{MAIN_COMMAND} "{local_command}"'

    logger.error(full_command)
    os.system(full_command)
    #result = subprocess.run(full_command, shell=True, check=True, text=True, capture_output=True)
    return