import logging
from commands import BasicCommand


class BasicHandler:
    def __init__(self):
        self._bot = None
        pass

    def setup(self, bot):
        self._bot = bot

    @property
    def usage_text(self) -> str:
        return "This should be overriden"

    async def handle(self, command: BasicCommand, command_context):
        pass


class SayHandler(BasicHandler):
    def __init__(self):
        super().__init__()

    @property
    def usage_text(self) -> str:
        return "<text to repeat>, this let the bot repeat a given sentence"

    async def handle(self, command: BasicCommand, command_context):
        logging.log(logging.INFO, "Got say command!")
        response_body = " ".join(command.arguments)
        await self._bot.send_message(command_context.room_id, response_body)


class HelpHandler(BasicHandler):
    def __init__(self):
        super().__init__()

    @property
    def usage_text(self) -> str:
        return "<command>, Gives more information about the specified command"

    def _create_command_overview(self) -> str:
        help_text = ""
        for command, handler in self._bot.command_handlers.items():
            help_text += f"!{command} {handler.usage_text}\n"

        return help_text

    async def handle(self, command: BasicCommand, command_context):
        if len(command.arguments) == 0:
            await self._bot.send_message(command_context.room_id, self._create_command_overview())


