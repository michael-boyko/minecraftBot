import json
import os
import random
import subprocess
import constants as c
from bot_logger import logger
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from database import get_user_by_telegram_id, add_user
from utils import handle_user_messages
from minecraft_msg_handler import send_command_msg, send_command_list

# Определение состояний для ConversationHandler
NICKNAME, AUTH_CODE = range(2)

async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    telegram_id = user.id

    # Проверка, авторизован ли пользователь
    user_data = get_user_by_telegram_id(telegram_id)

    if user_data:
        username = user_data[c.BD_NICKNAME]  # Предполагается, что имя пользователя хранится в третьем поле
        await update.message.reply_text(
            f'Привет, {username}! Чем помочь тебе сегодня?'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f'Привет, {user.first_name}! Пожалуйста, укажи свое имя'
            'на лучшем в мире сервере Minecraft - Pure_Craft_Friends\n\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tВНИМАНИЕ!\n'
            'Для авторизации зайдите на сервер Mincraft\n'
            'ТУДА БУДЕТ ОТПРАВЛЕН СЕКРЕТНЫЙ КОД'
        )
        return NICKNAME

def validate_auth_nickname(nickname):
    whitelist_path = '/home/mboiko/ServerMinecraft/whitelist.json'

    if not os.path.exists(whitelist_path):
        logger.error(f"File not found: {whitelist_path}")
        return False

    with open(whitelist_path, 'r') as file:
        whitelist = json.load(file)

    for entry in whitelist:
        if entry['name'] == nickname:
            return True
    return False


async def nickname(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    nickname = update.message.text
    context.user_data['nickname'] = nickname
    context.user_data['username'] = user.first_name
    if validate_auth_nickname(nickname):
        true_code = generate_auth_code()
        context.user_data['true_code'] = true_code
        send_command_msg(nickname, true_code)
        await update.message.reply_text(
            'Спасибо! Теперь, пожалуйста, напишите код авторизации.\n\n'
            'КОД ОТПРАВЛЕН ВАМ В МАЙНКРАФТЕ'
        )
    else:
        await update.message.reply_text(
            f'Извините, но игрока с именем "{nickname}"'
            'не существует, попробуй другое имя'
        )
        return NICKNAME
    return AUTH_CODE

async def auth_code(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    telegram_id = user.id
    auth_code = update.message.text
    true_code = context.user_data['true_code']
    nickname = context.user_data['nickname']

    # Здесь вы можете добавить проверку кода авторизации
    if validate_auth_code(true_code, auth_code):
        username = context.user_data['username']
        add_user(telegram_id, nickname, username, 'user')
        await update.message.reply_text('Вы успешно авторизованы как user!'
                                        'Теперь вы можете отправлять сообщения.')
        return ConversationHandler.END
    else:
        await update.message.reply_text('Неверный код авторизации.'
                                        'Попробуйте снова.')
        send_command_msg(nickname, true_code)
        return AUTH_CODE

def generate_auth_code() -> str:
    return str(random.randint(1000, 9999))

def validate_auth_code(true_code: str, code: str) -> bool:
    return true_code == code

async def status(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    telegram_id = user.id
    user_data = get_user_by_telegram_id(telegram_id)

    if user_data:
        id, telegram_id, nickname, username, role = user_data
        if role in ['user', 'admin', 'god']:
            command_result = send_command_list()
            await update.message.reply_text(command_result)
        else:
            await update.message.reply_text('У вас нет прав для'
                                            'выполнения этой команды.')

async def message_handler(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    msg = update.message.text
    telegram_id = user.id

    # Проверка, авторизован ли пользователь
    user_data = get_user_by_telegram_id(telegram_id)

    if user_data:
        # Пользователь авторизован, обрабатываем его сообщение
        
        await handle_user_messages(update, context, user_data, msg)
    else:
        await update.message.reply_text('Пожалуйста, сначала выполните'
                                        'авторизацию, отправте /start '
                                        'и следуйте инструкциям')

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id
    user_data = get_user_by_telegram_id(telegram_id)

    logger.error('MDB: shutdown tests +++++')
    if user_data and user_data[c.BD_ROLE] == 'god':
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
            await update.message.reply_text("Server is shutting down.")
        except subprocess.CalledProcessError as e:
            await update.message.reply_text(f"Error shutting down the server: {e}")

def register_handlers(application, message_queue):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname)],
            AUTH_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_code)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    message_queue.put('Сервер запущен! Можно начинать играть!')