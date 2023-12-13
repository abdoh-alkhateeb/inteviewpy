import asyncio
import aio_msgpack_rpc
from mailtm import get_mailtm_token, get_mailtm_emails

async def main():
    client = aio_msgpack_rpc.Client(*await asyncio.open_connection("localhost", 18000))

    address = "pyinterviewtest@wireconnected.com"
    password = "pyinterviewtest"

    token = get_mailtm_token(address, password)

    recieved_msgs = []

    while True:
        emails = get_mailtm_emails(token)
        for email in emails:
            if email["id"] not in recieved_msgs:
                await client.notify("on_new_mail", email["subject"], email["intro"])
                recieved_msgs.append(email["id"])

        await asyncio.sleep(60)

asyncio.get_event_loop().run_until_complete(main())
