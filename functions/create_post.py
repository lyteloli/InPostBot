from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils import send_post, telegraph_upload
from NekoGram import Neko, BuildResponse, NekoRouter
from typing import Dict, Any
from html import escape
from io import BytesIO
import const
try:
    import ujson as json
except ImportError:
    import json


ROUTER: NekoRouter = NekoRouter()


@ROUTER.function()
async def menu_create_post_step_1(_: BuildResponse, message: Message, neko: Neko):
    """
    Received post media
    """
    if message.caption is None or len(message.caption) <= 1024:
        content_type = message.content_type
        if content_type == 'photo':
            # Photo
            f = await (max(message.photo, key=lambda c: c.width)).download(destination=BytesIO())
            thumb = await (min(message.photo, key=lambda c: c.width)).download(destination=BytesIO())
            mime = 'photo/png'
        elif content_type == 'video':
            # Video
            f = await message.video.download(destination=BytesIO())
            thumb = await message.video.thumb.download(destination=BytesIO())
            mime = 'video/mp4'
        elif content_type == 'text':
            # Text
            f = None
            thumb = None
            mime = None
        else:
            # Animation
            f = await message.animation.download(destination=BytesIO())
            thumb = await message.animation.thumb.download(destination=BytesIO())
            mime = 'video/mp4'

        file_link = True
        thumb_link = None
        if content_type != 'text':
            # Upload file if not text
            file_link = await telegraph_upload(f, mime=mime)
            thumb_link = await telegraph_upload(thumb)

        try:
            caption = message.html_text
        except TypeError:
            caption = None

        if file_link:
            await neko.storage.set_user_data(data={'file_link': file_link, 'caption': caption,
                                                   'file_type': content_type, 'thumb': thumb_link},
                                             user_id=message.from_user.id)
            data = await neko.build_text(text='menu_create_post_step_2', user=message.from_user)
        else:
            data = await neko.build_text(text='upload_error', user=message.from_user)
    else:
        data = await neko.build_text(text='caption_too_long', user=message.from_user, text_format=len(message.caption))

    await message.reply(text=data.data.text, parse_mode=data.data.parse_mode, disable_notification=data.data.silent,
                        disable_web_page_preview=data.data.no_preview, reply_markup=data.data.markup, reply=False)


@ROUTER.function()
async def menu_create_post_step_2(data: BuildResponse, message: Message, neko: Neko):
    buttons = []
    markup = InlineKeyboardMarkup()
    user_data: Dict[str, Any] = await neko.storage.get_user_data(user_id=message.from_user.id)
    try:
        if not message.text.startswith('⭕️') or not message.text.endswith('⭕️'):
            for row in message.text.split('\n'):
                dict_row = []
                inline_keyboard_row = []
                for button in row.split('#'):
                    text = button.split('+')[0].strip()
                    link = button.split('+')[1].strip()
                    dict_row.append({'link': link, 'text': text})
                    inline_keyboard_row.append(InlineKeyboardButton(text=text, url=link))
                buttons.append(dict_row)
                markup.row(*inline_keyboard_row)
        data = await neko.build_text(text='menu_create_post_step_3', user=message.from_user)
        await send_post({'uid': message.from_user.id, 'type': user_data['file_type'],
                         'file_link': user_data['file_link'], 'caption': user_data['caption'],
                         'markup': markup})
        await neko.storage.set_user_data(data={'markup': buttons}, user_id=message.from_user.id)
    except (KeyError, TypeError, ValueError, IndexError):
        await neko.storage.set_user_data(data={'menu': 'menu_create_post_step_2'}, user_id=message.from_user.id)
    await message.reply(text=data.data.text, parse_mode=data.data.parse_mode, disable_notification=data.data.silent,
                        disable_web_page_preview=data.data.no_preview, reply_markup=data.data.markup, reply=False)


@ROUTER.function()
async def menu_create_post_step_3(_: BuildResponse, message: Message, neko: Neko):
    user_data: Dict[str, Any] = await neko.storage.get_user_data(user_id=message.from_user.id)
    if message.text.startswith(const.bot_name):  # Make sure we don't include bot name in the code
        message.text = (message.text.replace(const.bot_name, '')).strip()

    if len(message.text) <= 50:
        if not await neko.storage.check("""SELECT id FROM posts WHERE code=%s""", message.text):
            await neko.storage.apply("""INSERT INTO posts (code, type, link, caption, markup, owner, thumb) """
                                     """VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                     (message.text, user_data['file_type'], user_data['file_link'],
                                      user_data['caption'], json.dumps(user_data['markup']), message.from_user.id,
                                      user_data['thumb']))
            # Send the post created text
            data = await neko.build_text(text='post_created', user=message.from_user)
            await neko.storage.set_user_data(data={}, user_id=message.from_user.id)
            await message.reply(text=data.data.text, parse_mode=data.data.parse_mode,
                                disable_notification=data.data.silent, reply_markup=data.data.markup,
                                disable_web_page_preview=data.data.no_preview, reply=False)

            markup = InlineKeyboardMarkup()
            button_text = (await neko.build_text(text='share', user=message.from_user)).data.text
            markup.add(InlineKeyboardButton(text=button_text, switch_inline_query=message.text))
            await message.reply(text=f'{const.bot_name} {escape(message.text)}', parse_mode=data.data.parse_mode,
                                disable_notification=data.data.silent, reply_markup=data.data.markup,
                                disable_web_page_preview=data.data.no_preview, reply=False)

            await neko.delete_markup(user_id=message.from_user.id)
            await neko.start_function(message)
            return
        else:
            data = await neko.build_text(text='code_taken', user=message.from_user)
    else:
        data = await neko.build_text(text='code_too_long', user=message.from_user, text_format=len(message.text))

    await message.reply(text=data.data.text, parse_mode=data.data.parse_mode, disable_notification=data.data.silent,
                        disable_web_page_preview=data.data.no_preview, reply_markup=data.data.markup, reply=False)
