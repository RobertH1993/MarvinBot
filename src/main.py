import asyncio
from config import Config
from nio import AsyncClient, MatrixRoom, RoomMessageText, LoginResponse


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    print(f"Message received in room {room.display_name}\n"
          f"{room.user_name(event.sender)} | {event.body}"
          )


def write_credentials_to_config(response: LoginResponse, config_object: Config):
    config_object['matrix_credentials']['access_token'] = response.access_token
    config_object['matrix_credentials']['user_id'] = response.user_id
    config_object['matrix_credentials']['device_id'] = response.device_id
    config_object.save()


async def main():
    config_object = Config("config.json")
    async_client = AsyncClient(config_object['matrix_credentials']['homeserver'], config_object['matrix_credentials']['username'])
    async_client.add_event_callback(message_callback, RoomMessageText)

    if 'access_token' in config_object['matrix_credentials'].keys():
        async_client.access_token = config_object['matrix_credentials']['access_token']
        async_client.user_id = config_object['matrix_credentials']['user_id']
        async_client.device_id = config_object['matrix_credentials']['device_id']
    else:
        login_resp = await async_client.login(config_object['matrix_credentials']['password'])
        print(f"User_id: {login_resp.user_id}")
        print(f"Device_id: {login_resp.device_id}")
        print(f"Access token: {login_resp.access_token}")
        write_credentials_to_config(login_resp, config_object)

    print(await async_client.join("#testroom:hack42.nl"))
    print(await async_client.sync_forever(30000))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
