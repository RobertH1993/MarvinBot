import asyncio
import logging

from bot import MarvinBot


async def main():
    bot = MarvinBot("../config.json")
    await bot.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
