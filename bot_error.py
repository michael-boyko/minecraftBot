from telegram.error import NetworkError, RetryAfter, TimedOut
from bot_logger import logger
from telegram import Update

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