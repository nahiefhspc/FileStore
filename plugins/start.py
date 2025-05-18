# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import re
import string 
import string as rohit
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *

BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

async def short_url(client: Client, message: Message, base64_string):
    try:
        prem_link = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"
        short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, prem_link)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
                InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)
            ],
            [
                InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        await message.reply_photo(
            photo=SHORTENER_PIC,
            caption=SHORT_MSG.format(),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except IndexError:
        pass

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Handle normal message flow
    text = message.text

    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            if base64_string.startswith("yu3elk"):
                base64_string = base64_string[6:-1]
            print(f"Decoding base64 string: {base64_string}")  # Debug log

        except Exception as e:
            print(f"Error processing start payload: {e}")
            await message.reply_text("❌ Invalid link format.")
            return

        try:
            string = await decode(base64_string)
            print(f"Decoded string: {string}")  # Debug log
            argument = string.split("-")

            ids = []
            db_channel_id = None
            if len(argument) == 4:  # Batch link: get-<db_channel_id>-<start>-<end>
                try:
                    db_channel_id = int(argument[1])
                    db_channels = await db.show_db_channels()
                    print(f"Checking db_channel_id {db_channel_id} against {db_channels}")  # Debug log
                    if db_channel_id not in db_channels:
                        await message.reply_text(f"❌ Invalid database channel: {db_channel_id}")
                        return
                    start = int(int(argument[2]) / abs(db_channel_id))
                    end = int(int(argument[3]) / abs(db_channel_id))
                    ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
                except ValueError as e:
                    print(f"Error decoding batch IDs: {e}")
                    await message.reply_text("❌ Invalid batch link format.")
                    return

            elif len(argument) == 3:  # Single message: get-<db_channel_id>-<msg_id>
                try:
                    db_channel_id = int(argument[1])
                    db_channels = await db.show_db_channels()
                    print(f"Checking db_channel_id {db_channel_id} against {db_channels}")  # Debug log
                    if db_channel_id not in db_channels:
                        await message.reply_text(f"❌ Invalid database channel: {db_channel_id}")
                        return
                    ids = [int(int(argument[2]) / abs(db_channel_id))]
                except ValueError as e:
                    print(f"Error decoding single message ID: {e}")
                    await message.reply_text("❌ Invalid single message link format.")
                    return
            else:
                # Handle older link format (if applicable)
                await message.reply_text("❌ Unsupported link format. Please use a newer link.")
                return

            temp_msg = await message.reply("<b>Please wait...</b>")
            try:
                messages = await get_messages(client, ids, db_channel_id)
                if not messages:
                    await temp_msg.edit("❌ No messages found for the provided IDs.")
                    return
            except Exception as e:
                await temp_msg.edit("❌ Something went wrong while fetching messages!")
                print(f"Error getting messages: {e}")
                return
            finally:
                await temp_msg.delete()

            codeflix_msgs = []
            for msg in messages:
                if not msg:  # Skip None messages
                    continue
                caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                                filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                          else ("" if not msg.caption else msg.caption.html))

                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                try:
                    copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                               reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    codeflix_msgs.append(copied_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                               reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    codeflix_msgs.append(copied_msg)
                except Exception as e:
                    print(f"Failed to send message: {e}")
                    pass

            if FILE_AUTO_DELETE > 0:
                notification_msg = await message.reply(
                    f"<b>Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ  {get_exp_time(FILE_AUTO_DELETE)}. Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ.</b>"
                )

                await asyncio.sleep(FILE_AUTO_DELETE)

                for snt_msg in codeflix_msgs:    
                    if snt_msg:
                        try:    
                            await snt_msg.delete()  
                        except Exception as e:
                            print(f"Error deleting message {snt_msg.id}: {e}")

                try:
                    reload_url = (
                        f"https://t.me/{client.username}?start={message.command[1]}"
                        if message.command and len(message.command) > 1
                        else None
                    )
                    keyboard = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)]]
                    ) if reload_url else None

                    await notification_msg.edit(
                        "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    print(f"Error updating notification with 'Get File Again' button: {e}")
        except Exception as e:
            print(f"Error decoding link: {e}")
            await message.reply_text("❌ Failed to process the link.")
            return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟs •", url="https://t.me/Nova_Flix/50")],
                [
                    InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton('ʜᴇʟᴘ •', callback_data="help")
                ]
            ]
        )
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586)  # 🔥
        
        return

# Command to set a database channel
@Bot.on_message(filters.command('setdbchannel') & filters.private & admin)
async def set_db_channel(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /setdbchannel <channel_id>\nExample: /setdbchannel -1001234567890")
        return
    try:
        channel_id = int(message.command[1])
        if await db.db_channel_exist(channel_id):
            await message.reply_text("This channel is already set as a database channel.")
            return
        await db.add_db_channel(channel_id)
        await message.reply_text(f"Database channel {channel_id} added successfully.")
    except ValueError:
        await message.reply_text("Invalid channel ID. Please provide a valid numeric channel ID (e.g., -1001234567890).")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Command to remove a database channel
@Bot.on_message(filters.command('removedbchannel') & filters.private & admin)
async def remove_db_channel(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /removedbchannel <channel_id>\nExample: /removedbchannel -1001234567890")
        return
    try:
        channel_id = int(message.command[1])
        if not await db.db_channel_exist(channel_id):
            await message.reply_text("This channel is not set as a database channel.")
            return
        await db.rem_db_channel(channel_id)
        await message.reply_text(f"Database channel {channel_id} removed successfully.")
    except ValueError:
        await message.reply_text("Invalid channel ID. Please provide a valid numeric channel ID (e.g., -1001234567890).")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Command to list database channels
@Bot.on_message(filters.command('listdbchannels') & filters.private & admin)
async def list_db_channels(client: Client, message: Message):
    db_channels = await db.show_db_channels()
    if not db_channels:
        await message.reply_text("No database channels are set.")
        return
    channel_list = "\n".join([f"• {ch_id}" for ch_id in db_channels])
    await message.reply_text(f"Current database channels:\n{channel_list}")

async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>Checking Subscription...</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()  # Should return list of (chat_id, mode) tuples
        for total, chat_id in enumerate(all_channels, start=1):
            mode = await db.get_channel_mode(chat_id)  # fetch mode 

            await message.reply_chat_action(ChatAction.TYPING)

            if not await is_sub(client, user_id, chat_id):
                try:
                    # Cache chat info
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    # Generate proper invite link based on the mode
                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            creates_join_request=True,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                        link = invite.invite_link

                    else:
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None)
                            link = invite.invite_link

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @rohit_1888</i></b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        # Retry Button
        try:
            buttons.append([
                InlineKeyboardButton(
                    text='♻️ Tʀʏ Aɢᴀɪɴ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ])
        except IndexError:
            pass

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @rohit_1888</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id  # Get user ID from the message
    status_message = await check_user_plan(user_id)
    await message.reply(status_message)

@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        await msg.reply_text(
            "Usage: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "Time Units:\n"
            "s - seconds\n"
            "m - minutes\n"
            "h - hours\n"
            "d - days\n"
            "y - years\n\n"
            "Examples:\n"
            "/addpremium 123456789 30 m → 30 minutes\n"
            "/addpremium 123456789 2 h → 2 hours\n"
            "/addpremium 123456789 1 d → 1 day\n"
            "/addpremium 123456789 1 y → 1 year"
        )
        return
    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()
        expiration_time = await add_premium(user_id, time_value, time_unit)
        await msg.reply_text(
            f"✅ User `{user_id}` added as a premium user for {time_value} {time_unit}.\n"
            f"Expiration Time: `{expiration_time}`"
        )
        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Premium Activated!\n\n"
                f"You have received premium access for `{time_value} {time_unit}`.\n"
                f"Expires on: `{expiration_time}`"
            ),
        )
    except ValueError:
        await msg.reply_text("❌ Invalid input. Please ensure user ID and time value are numbers.")
    except Exception as e:
        await msg.reply_text(f"⚠️ An error occurred: `{str(e)}`")

@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("useage: /remove_premium user_id ")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"User {user_id} has been removed.")
    except ValueError:
        await msg.reply_text("user_id must be an integer or not available in database.")

@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium_users_command(client, message):
    from pytz import timezone
    ist = timezone("Asia/Kolkata")
    premium_users_cursor = collection.find({})
    premium_user_list = ['Active Premium Users in database:']
    current_time = datetime.now(ist)
    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]
        try:
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)
            remaining_time = expiration_time - current_time
            if remaining_time.total_seconds() <= 0:
                await collection.delete_one({"user_id": user_id})
                continue
            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "No Username"
            first_name = user_info.first_name
            mention=user_info.mention
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"User: @{username}\n"
                f"Name: {mention}\n"
                f"Expiry: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"Error: Unable to fetch user details ({str(e)})"
            )
    if len(premium_user_list) == 1:
        await message.reply_text("I found 0 active premium users in my DB")
    else:
        await message.reply_text("\n\n".join(premium_user_list), parse_mode=None)

@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close")]])
    await message.reply(text=CMD_TXT, reply_markup=reply_markup, quote=True)
