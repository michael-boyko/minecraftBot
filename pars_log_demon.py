import re
import time
import json
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
    whitelist_path = '/home/mboiko/ServerMinecraft/whitelist.json'

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
    join_pattern = r'\d{2}:\d{2}:\d{2}\] (.+) joined the game'
    leave_pattern = r'\d{2}:\d{2}:\d{2}\] (.+) left the game'
    
    join_match = re.match(join_pattern, line)
    leave_match = re.match(leave_pattern, line)
    
    if join_match:
        player_name = join_match.group(1)
        result = f"{player_name} Присоединился к игре"
        return result
    elif leave_match:
        player_name = leave_match.group(1)
        result = f"{player_name} Покинул игру"
        return result
    else:
        return "Ошибка при парсинге строки."

# Обработчик событий для отслеживания изменений в файле
class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file, message_queue):
        self.log_file = log_file
        self.message_queue = message_queue
        self.position = 0
        self.player_log_file = open("/home/mboiko/BotMinecraft/logs/player_logs.txt", "a")
        self.system_log_file = open("/home/mboiko/BotMinecraft/logs/system_logs.txt", "a")
        self.command_log_file = open("/home/mboiko/BotMinecraft/logs/command_logs.txt", "a")
        self.join_leave_log_file = open("/home/mboiko/BotMinecraft/logs/join_leave_logs.txt", "a")

    def process_logs(self, lines):
        for line in lines:
            timestamp, message = parse_log_line(line)
            if is_user_message(message):
                self.player_log_file.write(f"{timestamp} {message}\n")
                self.player_log_file.flush()
            elif "joined the game" in message or "left the game" in message:
                line = ''
                join_msg = create_game_message(f"{message}\n")
                send_enter()
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
def monitor_log_file(log_file_path, stop_event, message_queue):
    event_handler = LogHandler(log_file_path, message_queue)
    observer = Observer()
    observer.schedule(event_handler, path=log_file_path, recursive=False)
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

