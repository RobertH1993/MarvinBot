import asyncio
from typing import List

from nio import AsyncClient, AsyncClientConfig, LoginResponse, MatrixRoom, RoomMessageText, JoinedRoomsResponse
from config import Config
from commands import BasicCommand
from handler import BasicHandler
import logging


class BotMessageCommandContext:
    def __init__(self, room_id: str, sender_id: str):
        self._room_id: str = room_id
        self._sender_id: str = sender_id

    @property
    def room_id(self) -> str:
        return self._room_id

    @property
    def sender_id(self) -> str:
        return self._sender_id


class MarvinBot:
    def __init__(self, config_path: str):
        # Flag that specifies if the bot has logged in
        self._logged_in = False

        # Flag that specifies if the first sync with the server has succeeded
        self._synced = False

        # The path to the config file that is currently loaded
        self._config_path: str = config_path

        # The config object
        self._config: Config = Config(config_path)

        # Subset of the JSON config
        self._credentials: dict = self._config['matrix_credentials']

        # Subset of the JSON config
        self._rooms: dict = self._config['matrix_rooms']

        # List with internal-ids of rooms we joined, this gets populated after connecting to the server
        self._joined_rooms: List = []

        # Dict with command handlers
        self._command_handlers: dict = dict()

        self._client_config = AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
            store_name="python-bot.db"
        )

        self._client: AsyncClient = AsyncClient(
            self._credentials['homeserver'],
            self._credentials['username'],
            config=self._client_config,
            store_path='./store',
            device_id='python-bot.db'
        )

        # Register callbacks
        self._client.add_event_callback(self._room_message_callback, RoomMessageText)

    async def start(self) -> None:
        if not self._logged_in:
            self._logged_in = await self._login()

        asyncio.create_task(self._on_first_sync(self._client.synced))
        await self._client.sync_forever(30000, full_state=True)

    async def send_message(self, room_id: str, message: str) -> None:
        await self._client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )

    def register_command_handler(self, command: str, command_handler: BasicHandler) -> None:
        if command not in self._command_handlers.keys():
            self._command_handlers[command] = command_handler
            command_handler.setup(self)
        else:
            raise KeyError(f"command: {command} is already registered to a handler!")

    def remove_command_handler(self, command: str) -> None:
        if command in self._command_handlers.keys():
            del self._command_handlers['key']

    async def _room_message_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
        logging.log(logging.DEBUG, f"Received a message in room {room.display_name}, from: {room.user_name(event.sender)}")

        # Dont parse messages of ourself
        if event.sender == self._credentials['user_id']:
            return

        # Check if a valid command has been send
        if event.body.startswith("!"):
            command_parts = event.body.split(" ")
            command_parts[0] = command_parts[0].strip("!")
            if command_parts[0] not in self._command_handlers.keys():
                logging.log(logging.INFO, f"Got a command that cannot be handled: {command_parts[0]}")
            else:
                command_to_handle = BasicCommand(command_parts[0], command_parts[1:])
                command_context = BotMessageCommandContext(room.room_id, event.sender)
                await self._command_handlers[command_to_handle.command].handle(command_to_handle, command_context)

    async def _on_first_sync(self, event: asyncio.Event):
        await event.wait()
        logging.log(logging.INFO, "Sync event fired")
        self._synced = True

        if self._client.should_upload_keys:
            logging.log(logging.INFO, "Uploading keys to server")
            await self._client.keys_upload()

        rooms_resp: JoinedRoomsResponse = await self._client.joined_rooms()
        self._joined_rooms = rooms_resp.rooms

        for room_id, options in self._rooms.items():
            if 'internal_id' in options:
                if options['internal_id'] in self._joined_rooms:
                    logging.log(logging.INFO, f"Already joined room {room_id}, skipping...")
                    continue

            join_resp = await self._client.join(room_id)
            # TODO check for error response

            logging.log(logging.INFO, f"Joining room {room_id}, internal id: {join_resp.room_id}")
            options['internal_id'] = join_resp.room_id

        self._config['matrix_rooms'] = self._rooms
        self._config.save()

    async def _login(self) -> bool:
        if 'user_id' in self._credentials and 'device_id' in self._credentials and 'access_token' in self._credentials:
            logging.log(logging.INFO, "Logging into server by access token")
            self._client.restore_login(self._credentials['user_id'], self._credentials['device_id'], self._credentials['access_token'])
        else:
            logging.log(logging.INFO, "Logging into server by username and password authentication")
            login_resp = await self._client.login(self._credentials['password'])
            # TODO check if login_resp is of type loginResponse or is an error
            self._save_access_data_to_config(login_resp)

        return True

    def _save_access_data_to_config(self, response: LoginResponse):
        self._credentials['access_token'] = response.access_token
        self._credentials['user_id'] = response.user_id
        self._credentials['device_id'] = response.device_id
        self._config['matrix_credentials'] = self._credentials
        self._config.save()
