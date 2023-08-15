import asyncio
import logging

from bot import MarvinBot
from handler import SayHandler, HelpHandler


async def main():
    bot = MarvinBot("../config.json")
    bot.register_command_handler("say", SayHandler())
    bot.register_command_handler("help", HelpHandler())
    await bot.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
