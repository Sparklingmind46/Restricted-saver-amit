import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
from os import environ

bot_token = environ.get("TOKEN", "")
api_hash = environ.get("HASH", "")
api_id = int(environ.get("ID", ""))
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(
        message.chat.id,
        f"👋 Hii {message.from_user.mention}, **I am Save Restricted Bot, I can send you restricted content by its post link**\n\n{USAGE}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Updates Channel", url="https://t.me/Amit_0_1")]]),
        reply_to_message_id=message.id
    )


@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # Public chat handling
    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            username = datas[3]

            try:
                msg = bot.get_messages(username, msgid)
            except UsernameNotOccupied:
                bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                return

            try:
                bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            time.sleep(3)


USAGE = """**➥ ONLY FOR PUBLIC CHATS 👇**
• Post the link to see the bot in action 😎😁

**➥ MULTI POSTS** (To download multiple posts at once)
Send link in this format (From-to) 👇
https://t.me/xxxx/1001-1010

**➥ Developed by - @Ur_Amit_01 🧸✨**
"""

# Start polling
bot.run()
