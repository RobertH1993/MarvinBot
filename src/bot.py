import asyncio

from nio import AsyncClient, AsyncClientConfig, LoginResponse, MatrixRoom, RoomMessageText
from config import Config
import logging


class MarvinBot:
    def __init__(self, config_path: str):
        self._logged_in = False
        self._synced = False
        self._config_path: str = config_path
        self._config: Config = Config(config_path)
        self._credentials = self._config['matrix_credentials']

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

    async def _room_message_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
        logging.log(logging.DEBUG, f"Received a message in room {room.display_name}, from: {room.user_name(event.sender)}")

        # Dont parse messages of ourself
        if event.sender == self._credentials['user_id']:
            return

        if event.body.startswith("!say"):
            data = event.body.partition(" ")[2]
            await self._client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": data},
                ignore_unverified_devices=True
            )

    async def _on_first_sync(self, event: asyncio.Event):
        await event.wait()
        logging.log(logging.INFO, "Sync event fired")
        self._synced = True

        if self._client.should_upload_keys:
            logging.log(logging.INFO, "Uploading keys to server")
            await self._client.keys_upload()

        # TODO join rooms

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

    def _save_access_data_to_config(self, response : LoginResponse):
        self._credentials['access_token'] = response.access_token
        self._credentials['user_id'] = response.user_id
        self._credentials['device_id'] = response.device_id
        self._config['matrix_credentials'] = self._credentials
        self._config.save()
