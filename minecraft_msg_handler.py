import os
import time
from bot_logger import logger

MAIN_COMMAND = 'screen -S MinecraftServer -X stuff'

def send_command_say(nickname, msg):
    local_command = f'\nsay <{nickname}(T)> {msg}\n'
    full_command = f'{MAIN_COMMAND} "{local_command}"'
    os.system(full_command)
    return

def send_command_list():
    full_command = f'{MAIN_COMMAND} "\nlist\n"'
    os.system(full_command)
    time.sleep(1)

    command_result = parse_last_online_line(
        '/home/mboiko/BotMinecraft/logs/command_logs.txt'
        )
    
    return command_result

def send_command_whitelist_add(nickname):
    return

def send_command_msg(nickname, msg):
    local_command = f'\nmsg {nickname} {msg}\n'
    full_command = f'{MAIN_COMMAND} "{local_command}"'

    logger.error(full_command)
    os.system(full_command)
    return

def parse_last_online_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Возьмите последнюю строку
    last_line = lines[-1].strip()

    # Парсинг строки для извлечения количества игроков и их имен
    import re
    pattern = r'\[.*\] There are (\d+) of a max of \d+ players online: ?(.*)'
    match = re.match(pattern, last_line)

    if match:
        count = match.group(1)
        players = match.group(2).split(', ') if match.group(2) else []

        if int(count) == 0:
            result = "Сервер работает, но никто не играет("
        else:
            result = f"Игроки на сервере: {count}\n" + '\n'.join(players)
        return result
    else:
        return "Ошибка при парсинге файла."