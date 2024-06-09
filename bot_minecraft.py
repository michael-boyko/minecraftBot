import threading
import queue
import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import Application
from bot_logger import logger
from handlers import register_handlers
from database import init_db
from pars_log_demon import monitor_log_file
from utils import broadcast_message
from bot_error import error_handler

message_queue = queue.Queue()

# Функция для запуска обработки очереди в отдельном потоке
def start_queue_processor(loop, application):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue(application))

async def process_queue(application):
    while True:
        if not message_queue.empty():
            msg = message_queue.get()
            await broadcast_message(application, msg)
            logger.info(f"Обработка сообщения: {msg}")
        await asyncio.sleep(2)

def main() -> None:
    # Инициализация базы данных
    init_db()

    load_dotenv()

    token = os.getenv('TOKEN')

    # Создайте экземпляр Application и передайте ему ваш токен
    application = Application.builder().token(token).build()

    # Регистрация обработчиков команд и сообщений
    register_handlers(application, message_queue)

    stop_event = threading.Event()

    path_to_logs = os.getenv('PATH_TO_LOGS')
    log_thread = threading.Thread(
        target=monitor_log_file,
        args=(path_to_logs, stop_event, message_queue)
    )
    log_thread.start()

    application.add_error_handler(error_handler)

    # Создаем и запускаем поток для обработки очереди
    loop = asyncio.new_event_loop()
    queue_thread = threading.Thread(target=start_queue_processor, args=(loop, application))
    queue_thread.start()

    # Запустите бота
    application.run_polling()

    stop_event.set()
    log_thread.join()

if __name__ == '__main__':
    main()
