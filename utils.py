from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union
from io import BytesIO
from const import neko
import aiohttp
try:
    import ujson as json
except ImportError:
    import json


async def load_mkp(markup: str) -> InlineKeyboardMarkup:
    mkp = InlineKeyboardMarkup()
    for row in json.loads(markup):
        cr = []
        for button in row:
            cr.append(InlineKeyboardButton(text=button['text'], url=button['link']))
        mkp.row(*cr)
    return mkp


async def send_post(row: dict):
    markup = await load_mkp(row['markup']) if isinstance(row['markup'], str) else row['markup']
    if row['type'] == 'text':
        await neko.bot.send_message(chat_id=row['uid'], text=row['caption'], reply_markup=markup,
                                    disable_web_page_preview=True)
    elif row['type'] == 'photo':
        await neko.bot.send_photo(chat_id=row['uid'], photo=row['file_link'], caption=row['caption'],
                                  reply_markup=markup)
    elif row['type'] == 'video':
        await neko.bot.send_video(chat_id=row['uid'], video=row['file_link'], caption=row['caption'],
                                  reply_markup=markup)
    elif row['type'] == 'animation':
        await neko.bot.send_animation(chat_id=row['uid'], animation=row['file_link'], caption=row['caption'],
                                      reply_markup=markup)


async def telegraph_upload(f: BytesIO, mime: str = 'image/png') -> Union[str, bool]:
    """
    Uploads media to telegra.ph

    Example usage:
    f = await (max(message.photo, key=lambda c: c.width)).download(destination=BytesIO())
    """
    data = aiohttp.FormData()
    data.add_field('file', f.read(), filename=f'photo.{mime.split("/")[1]}', content_type=mime)
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(url='https://telegra.ph/upload', data=data) as r:
                r = await r.json()
                if not r[-1]["src"].startswith('/'):
                    r[-1]["src"] = '/' + r[-1]["src"]
                return f'https://telegra.ph{r[-1]["src"]}'
    except (aiohttp.ClientPayloadError, Exception):
        # https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions
        return False
