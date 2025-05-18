#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from asyncio import TimeoutError
from helper_func import encode, get_message_id, admin

@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text="Forward the First Message from any DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            # Identify the DB channel
            db_channels = await db.show_db_channels()
            db_channel_id = None
            if first_message.forward_from_chat:
                for ch_id in db_channels:
                    if first_message.forward_from_chat.id == ch_id:
                        db_channel_id = ch_id
                        break
            elif first_message.text:
                pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
                matches = re.match(pattern, first_message.text)
                if matches:
                    channel_id = matches.group(1)
                    for ch_id in db_channels:
                        chat = await client.get_chat(ch_id)
                        if channel_id.isdigit():
                            if f"-100{channel_id}" == str(ch_id):
                                db_channel_id = ch_id
                                break
                        else:
                            if channel_id == chat.username.lstrip('@'):
                                db_channel_id = ch_id
                                break
            if db_channel_id:
                break
        await first_message.reply("❌ Error\n\nThis Forwarded Post or Link is not from any of my DB Channels.", quote=True)
        continue

    while True:
        try:
            second_message = await client.ask(text="Forward the Last Message from the same DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            # Verify it's from the same DB channel
            if second_message.forward_from_chat and second_message.forward_from_chat.id == db_channel_id:
                break
            elif second_message.text:
                pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
                matches = re.match(pattern, second_message.text)
                if matches:
                    channel_id = matches.group(1)
                    chat = await client.get_chat(db_channel_id)
                    if channel_id.isdigit():
                        if f"-100{channel_id}" == str(db_channel_id):
                            break
                    else:
                        if channel_id == chat.username.lstrip('@'):
                            break
        await second_message.reply("❌ Error\n\nThis Forwarded Post or Link is not from the same DB Channel.", quote=True)
        continue

    string = f"get-{db_channel_id}-{f_msg_id * abs(db_channel_id)}-{s_msg_id * abs(db_channel_id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text="Forward Message from any DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            # Identify the DB channel
            db_channels = await db.show_db_channels()
            db_channel_id = None
            if channel_message.forward_from_chat:
                for ch_id in db_channels:
                    if channel_message.forward_from_chat.id == ch_id:
                        db_channel_id = ch_id
                        break
            elif channel_message.text:
                pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
                matches = re.match(pattern, channel_message.text)
                if matches:
                    channel_id = matches.group(1)
                    for ch_id in db_channels:
                        chat = await client.get_chat(ch_id)
                        if channel_id.isdigit():
                            if f"-100{channel_id}" == str(ch_id):
                                db_channel_id = ch_id
                                break
                        else:
                            if channel_id == chat.username.lstrip('@'):
                                db_channel_id = ch_id
                                break
            if db_channel_id:
                break
        await channel_message.reply("❌ Error\n\nThis Forwarded Post or Link is not from any of my DB Channels.", quote=True)
        continue

    string = f"get-{db_channel_id}-{msg_id * abs(db_channel_id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)
    db_channel_id = None

    # Ask for the DB channel to store messages
    while True:
        try:
            db_choice = await client.ask(text="Forward a message from the DB Channel you want to store messages in..\nor Send the DB Channel Link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        db_channels = await db.show_db_channels()
        if db_choice.forward_from_chat:
            for ch_id in db_channels:
                if db_choice.forward_from_chat.id == ch_id:
                    db_channel_id = ch_id
                    break
        elif db_choice.text:
            pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
            matches = re.match(pattern, db_choice.text)
            if matches:
                channel_id = matches.group(1)
                for ch_id in db_channels:
                    chat = await client.get_chat(ch_id)
                    if channel_id.isdigit():
                        if f"-100{channel_id}" == str(ch_id):
                            db_channel_id = ch_id
                            break
                    else:
                        if channel_id == chat.username.lstrip('@'):
                            db_channel_id = ch_id
                            break
        if db_channel_id:
            break
        await db_choice.reply("❌ Error\n\nPlease select a valid DB Channel.", quote=True)
        continue

    await message.reply("Send all messages you want to include in batch.\n\nPress STOP when you're done.", reply_markup=STOP_KEYBOARD)

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text="Waiting for files/messages...\nPress STOP to finish.",
                timeout=60
            )
        except asyncio.TimeoutError:
            break

        if user_msg.text and user_msg.text.strip().upper() == "STOP":
            break

        try:
            sent = await user_msg.copy(db_channel_id, disable_notification=True)
            collected.append(sent.id)
        except Exception as e:
            await message.reply(f"❌ Failed to store a message:\n<code>{e}</code>")
            continue

    await message.reply("✅ Batch collection complete.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        await message.reply("❌ No messages were added to batch.")
        return

    start_id = collected[0] * abs(db_channel_id)
    end_id = collected[-1] * abs(db_channel_id)
    string = f"get-{db_channel_id}-{start_id}-{end_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await message.reply(f"<b>Here is your custom batch link:</b>\n\n{link}", reply_markup=reply_markup)
