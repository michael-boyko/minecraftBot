import constants as c
from bot_logger import logger
from telegram.ext import CallbackContext, Application
from database import get_all_users_from_bd
from telegram import Update
from minecraft_msg_handler import send_command_say

async def handle_user_messages(
        update: Update, context: CallbackContext, user_data, msg
        ):
    users = get_all_users_from_bd()

    send_command_say(user_data[c.BD_NICKNAME], msg)

    message = f'<{user_data[c.BD_NICKNAME]}(T)> {msg}'

    for user_item in users:
        if user_data[c.BD_NICKNAME] != user_item[c.BD_NICKNAME]:
            try:
                await context.bot.send_message(
                    chat_id=user_item[c.BD_TELEGRAM_ID], text=message
                    )
            except Exception as e:
                print('Failed to send message to ' 
                      f'{user_item[c.BD_TELEGRAM_ID]}: {e}')
    
    return

async def send_online_message(application: Application):
    users = get_all_users_from_bd()
    msg = 'Бот снова на связи!'

    for user_item in users:
        try:
            await application.bot.send_message(
                chat_id=user_item[c.BD_TELEGRAM_ID],
                text=msg
            )
        except Exception as e:
            print('Failed to send message to '
                  f'{user_item[c.BD_TELEGRAM_ID]}: {e}')

    return

async def broadcast_message(context: CallbackContext, message: str):
    users = get_all_users_from_bd()
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

# async def broadcast(msg) -> None:
#     message = " ".join(context.args)
#     await broadcast_message(context, message)
