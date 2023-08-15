import logging
from commands import BasicCommand


class BasicHandler:
    def __init__(self):
        self._bot = None
        pass

    def setup(self, bot):
        self._bot = bot

    async def handle(self, command: BasicCommand, command_context):
        pass


class SayHandler(BasicHandler):
    def __init__(self):
        super().__init__()

    async def handle(self, command: BasicCommand, command_context):
        logging.log(logging.INFO, "Got say command!")
        response_body = " ".join(command.arguments)
        await self._bot.send_message(command_context.room_id, response_body)
