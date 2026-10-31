# Posts flyer.jpg with ad.txt as caption from YOUR Telegram account.
import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    client = TelegramClient(StringSession(os.environ["TG_SESSION"]),
                            int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
    await client.start()
    caption = open("ad.txt", encoding="utf-8").read().strip()
    for chat in os.environ["CHAT_ID"].split():
        target = int(chat) if chat.lstrip("-").isdigit() else chat
        try:
            await client.send_file(target, "flyer.jpg", caption=caption)
            print("Posted to", chat)
        except Exception as e:
            print("Failed for", chat, e)
        await asyncio.sleep(30)   # pause between groups
    await client.disconnect()

asyncio.run(main())
