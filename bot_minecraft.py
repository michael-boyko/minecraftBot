import logging
import threading
from telegram.ext import Application, ContextTypes
from telegram.error import NetworkError, RetryAfter, TimedOut
from handlers import register_handlers
from database import init_db
from telegram import Update
from pars_log_demon import monitor_log_file

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

    log_file_path = '/home/mboiko/BotMinecraft/logs/raw_minecraft.log'
    log_thread = threading.Thread(target=monitor_log_file, args=(log_file_path,))
    log_thread.start()

    application.add_error_handler(error_handler)

    # Запустите бота
    application.run_polling()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and continue."""
    try:
        raise context.error
    except NetworkError as e:
        logger.error(f"NetworkError: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Возникли проблемы с сетью, попробуйте позже.")
    except RetryAfter as e:
        logger.error(f"RetryAfter: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Возникли проблемы с API Telegram, попробуйте позже.")
    except TimedOut as e:
        logger.error(f"TimedOut: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Превышено время ожидания, попробуйте позже.")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=context.error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка, попробуйте позже.")


if __name__ == '__main__':
    main()
