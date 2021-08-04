from aiogram.types import Message, CallbackQuery
from typing import Union
from html import escape


async def start_function(message: Union[Message, CallbackQuery]):
    """
    Start command
    """
    neko_obj = message.conf['neko']
    if isinstance(message, Message):
        await message.delete()
    if await neko_obj.storage.check("""SELECT id FROM users WHERE id=%s""", (message.from_user.id,)) > 0:
        # User exists
        data = await neko_obj.build_text(text='start', user=message.from_user,
                                         text_format=escape(message.from_user.full_name))
        await neko_obj.storage.set_user_data(data={}, user_id=message.from_user.id, replace=True)
    else:
        # New user
        language_code = message.from_user.language_code
        if language_code in neko_obj.texts.keys():
            lang = language_code
        elif (language_code == 'uk' or language_code == 'uz') and 'ru' in neko_obj.texts.keys():
            # Set Russian for those with Ukrainian and Uzbek
            lang = 'ru'
        else:
            # Set language to English for others
            lang = 'en'

        await neko_obj.storage.apply("""INSERT INTO users (id, lang, preferred_lang, data, username) VALUES """
                                     """(%s, %s, %s, %s, %s)""",
                                     (message.from_user.id, lang, language_code, '{}', message.from_user.username))
        data = await neko_obj.build_text(text='first_start', user=message.from_user,
                                         text_format=escape(message.from_user.full_name), lang='en')
    if isinstance(message, Message):
        await message.reply(text=data.data.text, parse_mode=data.data.parse_mode, disable_notification=data.data.silent,
                            disable_web_page_preview=data.data.no_preview, reply_markup=data.data.markup, reply=False)
    else:
        await message.message.edit_text(text=data.data.text, parse_mode=data.data.parse_mode,
                                        disable_web_page_preview=data.data.no_preview, reply_markup=data.data.markup)
