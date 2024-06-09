import re
import time
import json
import os
from bot_logger import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from minecraft_msg_handler import send_enter

# Функция для парсинга логов
def parse_log_line(line):
    timestamp_regex = r"\[\d{2}:\d{2}:\d{2}\]"
    message_regex = r"\]: (.*)$"
    timestamp_match = re.search(timestamp_regex, line)
    message_match = re.search(message_regex, line)
    timestamp = timestamp_match.group(0) if timestamp_match else None
    message = message_match.group(1) if message_match else line.strip()
    return timestamp, message

def get_all_user_from_whitelist():
    path_to_whitelist = os.getenv('PATH_TO_WHITELIST')
    whitelist_path = f'{path_to_whitelist}whitelist.json'

    with open(whitelist_path, 'r') as file:
        whitelist = json.load(file)
    return [entry['name'] for entry in whitelist]
    

def is_user_message(message) -> bool:
    all_users = get_all_user_from_whitelist()

    for user in all_users:
        if f'<{user}>' in message:
            return True
    return False

def create_game_message(line):
    # Регулярное выражение для извлечения имени игрока и действия
    join_pattern = r'(.+) joined the game'
    leave_pattern = r'(.+) left the game'
    
    join_match = re.match(join_pattern, line)
    leave_match = re.match(leave_pattern, line)
    
    if join_match:
        player_name = join_match.group(1)
        result = f"<b>{player_name}</b> <strong>присоединился к игре</strong> 💃🕺"
        return result
    elif leave_match:
        player_name = leave_match.group(1)
        result = f"*{player_name}* **покинул игру** 🤦‍♂️"
        return result
    else:
        return "Ошибка при парсинге строки."

def format_message(log_line):
    # Регулярное выражение для извлечения имени пользователя и сообщения
    pattern = r'\[\d{2}:\d{2}:\d{2}\] \[Not Secure\] <(.*?)> (.*)'
    match = re.match(pattern, log_line)
    
    if match:
        name = match.group(1)
        msg = match.group(2)
        formatted_message = f"⛏️ <{name}> {msg}"
        return formatted_message
    else:
        return "Ошибка при парсинге строки."

# Обработчик событий для отслеживания изменений в файле
class LogHandler(FileSystemEventHandler):
    def __init__(self, path_to_logs, message_queue):
        self.log_file = f'{path_to_logs}raw_minecraft.log'
        self.message_queue = message_queue
        self.position = 0
        self.initialized = False
        self.player_log_file = open(f"{path_to_logs}player_logs.txt", "a")
        self.system_log_file = open(f"{path_to_logs}system_logs.txt", "a")
        self.command_log_file = open(f"{path_to_logs}command_logs.txt", "a")
        self.join_leave_log_file = open(f"{path_to_logs}join_leave_logs.txt", "a")

    def process_logs(self, lines):
        for line in lines:
            timestamp, message = parse_log_line(line)
            if is_user_message(message):
                playr_msg = format_message(f"{timestamp} {message}\n")
                self.message_queue.put(playr_msg)
                self.player_log_file.write(f"{timestamp} {message}\n")
                self.player_log_file.flush()
            elif "joined the game" in message or "left the game" in message:
                join_msg = create_game_message(message)
                self.message_queue.put(join_msg)
                self.join_leave_log_file.write(f"{timestamp} {message}\n")
                self.join_leave_log_file.flush()
            elif "There are" in message and "players online:" in message:
                self.command_log_file.write(f"{timestamp} {message}\n")
                self.command_log_file.flush()
            else:
                self.system_log_file.write(f"{timestamp} {message}\n")
                self.system_log_file.flush()

    def on_modified(self, event):
        if event.src_path == self.log_file:
            with open(self.log_file, 'r') as f:
                if not self.initialized:
                    f.seek(0, 2)  # Переходим в конец файла
                    self.position = f.tell()
                    self.initialized = True
                else:
                    f.seek(self.position)
                    new_lines = f.readlines()
                    self.position = f.tell()
                    self.process_logs(new_lines)

    def close_files(self):
        self.player_log_file.close()
        self.system_log_file.close()
        self.command_log_file.close()
        self.join_leave_log_file.close()

# Основная функция для запуска наблюдателя
def monitor_log_file(path_to_logs, stop_event, message_queue):
    event_handler = LogHandler(path_to_logs, message_queue)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_logs, recursive=False)
    observer.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        event_handler.close_files()

