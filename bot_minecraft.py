import threading
import queue
import asyncio
from telegram.ext import Application
from bot_logger import logger
from handlers import register_handlers
from database import init_db
from pars_log_demon import monitor_log_file
from utils import broadcast_message
from bot_error import error_handler

message_queue = queue.Queue()

# Функция для запуска обработки очереди в отдельном потоке
def start_queue_processor(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue())

async def process_queue():
    while True:
        if not message_queue.empty():
            update = message_queue.get()
            await broadcast_message(update.message.text)
            # Здесь можно обработать сообщение из очереди
            logger.error(f"Обработка сообщения: {update.message.text}")
        await asyncio.sleep(2)

def main() -> None:
    # Инициализация базы данных
    init_db()

    # Создайте экземпляр Application и передайте ему ваш токен
    application = Application.builder().token("6553836190:AAHgRWBjdGYQ01yLJJnKUAcDwSLSB_qMIHw").build()

    # Регистрация обработчиков команд и сообщений
    register_handlers(application)

    stop_event = threading.Event()
    # new_message_event = asyncio.Event()

    log_file_path = '/home/mboiko/BotMinecraft/logs/raw_minecraft.log'
    log_thread = threading.Thread(
        target=monitor_log_file,
        args=(log_file_path, stop_event, message_queue)
    )
    log_thread.start()
    logger.error('MDB: start app ============================')

    application.add_error_handler(error_handler)

    # Создаем и запускаем поток для обработки очереди
    loop = asyncio.new_event_loop()
    queue_thread = threading.Thread(target=start_queue_processor, args=(loop,))
    queue_thread.start()

    # Запустите бота
    application.run_polling()

    stop_event.set()
    log_thread.join()

if __name__ == '__main__':
    main()
