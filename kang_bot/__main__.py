import asyncio
import logging

from kang_bot import bot, disp
from kang_bot.handlers import kang_handler


async def main():
    try:
        logging.info("Kang Bot started")
        disp.register_message_handler(kang_handler, commands={"kang"})
        await disp.start_polling()
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
