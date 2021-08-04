from aiogram.types import Message, CallbackQuery
from typing import Union
from const import neko
import aiogram

try:
    import ujson as json
except ImportError:
    import json


class BanFilter(aiogram.dispatcher.middlewares.BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self):
        super(BanFilter, self).__init__()

    @staticmethod
    async def sync_values(obj: Union[Message, CallbackQuery], user_data: dict):
        if user_data['username'] != obj.from_user.username:
            await neko.storage.apply("""UPDATE users SET username=%s WHERE id=%s""",
                                     (obj.from_user.username, obj.from_user.id))

    async def on_pre_process_message(self, message: Message, _: dict):
        """
        This handler is called when dispatcher receives a message
        """
        user_data = await neko.storage.get("""SELECT alias, username, data FROM users WHERE id=%s""",
                                           message.from_user.id)
        if user_data:
            if user_data['alias'] == 'banned':
                data = await neko.build_text(text='banned', user=message.from_user)
                await message.reply(text=data.data.text, reply_markup=data.data.markup,
                                    disable_web_page_preview=data.data.no_preview,
                                    disable_notification=data.data.silent, parse_mode=data.data.parse_mode, reply=False)
                raise aiogram.dispatcher.handler.CancelHandler()
            else:
                await self.sync_values(message, user_data)

    async def on_pre_process_callback_query(self, call: CallbackQuery, _: dict):
        """
        This handler is called when dispatcher receives a call
        """
        user_data = await neko.storage.get("""SELECT alias, username, data FROM users WHERE id=%s""", call.from_user.id)
        if len(user_data.keys()) > 0:
            if user_data['alias'] == 'banned':
                data = await neko.build_text(text='banned', user=call.from_user)
                await call.message.edit_text(text=data.data.text, parse_mode=data.data.parse_mode,
                                             disable_web_page_preview=data.data.no_preview,
                                             reply_markup=data.data.markup)
                raise aiogram.dispatcher.handler.CancelHandler()
            else:
                await self.sync_values(call, user_data)
