# Posts the media file (MEDIA) with ad.txt as caption, from the Telegram account in TG_SESSION,
# to every chat listed in chats.txt.
import os, re, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

MEDIA = os.environ.get("MEDIA", "ad.mp4")
CHATS_FILE = os.environ.get("CHATS_FILE", "chats.txt")
CAPTION_FILE = os.environ.get("CAPTION_FILE", "ad.txt")

def clean(s):
    # keep letters/digits only so emojis, flags and extra spaces don't break name matching
    return re.sub(r"[^\w]+", " ", s).strip().lower()

def read_targets():
    targets = []
    for line in open(CHATS_FILE, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        topic = None
        if "|" in line:
            line, t = [p.strip() for p in line.rsplit("|", 1)]
            topic = int(t)
        targets.append((line, topic))
    return targets

async def main():
    client = TelegramClient(StringSession(os.environ["TG_SESSION"]),
                            int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
    await client.start()
    caption = open(CAPTION_FILE, encoding="utf-8").read().strip()

    dialogs = [d async for d in client.iter_dialogs() if d.is_group or d.is_channel]

    def find_by_name(name):
        want = clean(name)
        exact = [d for d in dialogs if clean(d.name) == want]
        if exact:
            return exact[0].entity
        partial = [d for d in dialogs if want in clean(d.name)]
        if len(partial) > 1:
            print("  Note: several chats match", repr(name), "- using", repr(partial[0].name))
        return partial[0].entity if partial else None

    for name, topic in read_targets():
        label = name + (f" (topic {topic})" if topic else "")
        try:
            if name.startswith("@") or name.lstrip("-").isdigit():
                target = int(name) if name.lstrip("-").isdigit() else name
            else:
                target = find_by_name(name)
                if target is None:
                    print("Not found in your chats:", label)
                    continue
            await client.send_file(target, MEDIA, caption=caption,
                                   supports_streaming=True, reply_to=topic)
            print("Posted to", label)
        except Exception as e:
            print("Failed for", label, "-", e)
        await asyncio.sleep(30)
    await client.disconnect()

asyncio.run(main())
