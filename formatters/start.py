from NekoGram import Neko, types, BuildResponse
from html import escape


async def start(data: BuildResponse, user: types.User, _: Neko):
    await data.data.assemble_markup(text_format=escape(user.full_name))
