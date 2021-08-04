from aiogram.types import (InlineQuery, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent,
                           InlineQueryResultVideo)
from utils import load_mkp
from const import neko
import re


async def inline_echo(inline_query: InlineQuery):
    results = []
    async for post in neko.storage.select("""SELECT id, type, link, thumb, caption, markup FROM posts WHERE code=%s""",
                                          inline_query.query):
        if post['type'] == 'photo':
            results.append(InlineQueryResultPhoto(id=str(post['id']), photo_url=post['link'], title='Post',
                                                  thumb_url=post['thumb'], caption=post['caption'],
                                                  reply_markup=await load_mkp(post['markup']), parse_mode='HTML'))
        elif post['type'] == 'text':
            title = re.sub(r'<.*?>', '', post['caption'])
            r = InlineQueryResultArticle(id=str(post['id']), title=title, reply_markup=await load_mkp(post['markup']),
                                         input_message_content=InputTextMessageContent(message_text=post['caption'],
                                                                                       disable_web_page_preview=True,
                                                                                       parse_mode='HTML'))
            results.append(r)
        else:
            title = re.sub(r'<.*?>', '', post['caption']) if post['caption'] is not None else 'Post'
            results.append(InlineQueryResultVideo(id=str(post['id']), video_url=post['link'], mime_type='video/mp4',
                                                  thumb_url=post['thumb'], title=title, caption=post['caption'],
                                                  reply_markup=await load_mkp(post['markup']), parse_mode='HTML'))
    await inline_query.answer(results=results, cache_time=1)
