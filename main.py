import middleware
import handlers
import formatters
from functions import CREATE_POST_ROUTER
from const import neko


if __name__ == '__main__':
    neko.add_texts()
    CREATE_POST_ROUTER.attach_router(neko=neko)
    neko.dp.middleware.setup(middleware.BanFilter())
    neko.register_formatter(formatters.start_func, 'start')
    neko.register_formatter(formatters.start_func, 'first_start')
    neko.dp.register_inline_handler(handlers.inline_echo)
    neko.start_polling()
