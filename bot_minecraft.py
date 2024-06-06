import logging
import threading
import queue
import signal
import sys
import asyncio
from telegram.ext import Application, ContextTypes
from telegram.error import NetworkError, RetryAfter, TimedOut
from handlers import register_handlers
from database import init_db
from telegram import Update
from pars_log_demon import monitor_log_file
from utils import broadcast_message

# Установите уровень логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

def main() -> None:
    # Инициализация базы данных
    init_db()

    # Создайте экземпляр Application и передайте ему ваш токен
    application = Application.builder().token("6553836190:AAHgRWBjdGYQ01yLJJnKUAcDwSLSB_qMIHw").build()

    # Регистрация обработчиков команд и сообщений
    register_handlers(application)

    stop_event = threading.Event()
    message_queue = queue.Queue()
    log_file_path = '/home/mboiko/BotMinecraft/logs/raw_minecraft.log'
    log_thread = threading.Thread(
        target=monitor_log_file,
        args=(log_file_path, stop_event, message_queue)
    )
    log_thread.start()

    application.add_error_handler(error_handler)

    async def process_messages():
        while not stop_event.is_set():
            try:
                message = message_queue.get_nowait()
                await broadcast_message(application.bot, message)
            except queue.Empty:
                await asyncio.sleep(1)

    async def periodic_task():
        while not stop_event.is_set():
            await process_messages()
            await asyncio.sleep(1)

    application.job_queue.run_once(
        lambda context: asyncio.create_task(periodic_task()),
        when=0
    )

    # Запустите бота
    application.run_polling()

    stop_event.set()
    log_thread.join()


    # Запустите бота
    application.run_polling()

    stop_event.set()
    log_thread.join()


async def error_handler(update: Update, context) -> None:
    """Log the error and continue."""
    try:
        raise context.error
    except NetworkError as e:
        logger.error(f"NetworkError: {e}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Возникли проблемы с сетью, попробуйте позже."
                )
    except RetryAfter as e:
        logger.error(f"RetryAfter: {e}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Возникли проблемы с API Telegram, попробуйте позже."
                )
    except TimedOut as e:
        logger.error(f"TimedOut: {e}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Превышено время ожидания, попробуйте позже."
                )
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=context.error)
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Произошла ошибка, попробуйте позже.")

if __name__ == '__main__':
    main()
