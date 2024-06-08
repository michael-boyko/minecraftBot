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

    # Создайте экземпляр Application и передайте ему ваш токен
    application = Application.builder().token("6553836190:AAHgRWBjdGYQ01yLJJnKUAcDwSLSB_qMIHw").build()

    # Регистрация обработчиков команд и сообщений
    register_handlers(application, message_queue)

    stop_event = threading.Event()

    log_file_path = '/home/mboiko/BotMinecraft/logs/raw_minecraft.log'
    log_thread = threading.Thread(
        target=monitor_log_file,
        args=(log_file_path, stop_event, message_queue)
    )
    log_thread.start()

    application.add_error_handler(error_handler)

    # Создаем и запускаем поток для обработки очереди
    loop = asyncio.new_event_loop()
    queue_thread = threading.Thread(target=start_queue_processor, args=(loop, application))
    queue_thread.start()

    # Запустите бота
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.error("Остановка бота...")
        message_queue.put('🔴 Сервер ушел спатоньки. Увидемся завтра!')
        application.stop()

    stop_event.set()
    log_thread.join()

if __name__ == '__main__':
    main()
