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

from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
import pytz
from datetime import datetime
#rohit_1888 on Tg
from config import *
from database.db_premium import *
from database.database import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

# Suppress APScheduler logs below WARNING level
logging.getLogger("apscheduler").setLevel(logging.WARNING)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(remove_expired_users, "interval", seconds=10)

# Reset verify count for all users daily at 00:00 IST
async def daily_reset_task():
    try:
        await db.reset_all_verify_counts()
    except Exception:
        pass  

scheduler.add_job(daily_reset_task, "cron", hour=0, minute=0)

name ="""
 BY CODEFLIX BOTS
"""

def get_indian_time():
    """Returns the current time in IST."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        scheduler.start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Check access to all database channels
        try:
            db_channel_ids = await db.show_db_channels()
            if not db_channel_ids:
                self.LOGGER(__name__).warning("No database channels are set. Please add at least one using /setdbchannel.")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()

            self.db_channels = []
            for channel_id in db_channel_ids:
                try:
                    db_channel = await self.get_chat(channel_id)
                    # Verify bot is admin in the channel
                    chat_member = await self.get_chat_member(channel_id, usr_bot_me.id)
                    if chat_member.status not in ["administrator", "creator"]:
                        self.LOGGER(__name__).warning(f"Bot is not an admin in DB channel {channel_id}")
                        continue
                    self.db_channels.append(db_channel)
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Error accessing DB channel {channel_id}: {e}")
                    continue

            if not self.db_channels:
                self.LOGGER(__name__).warning("Bot could not access any DB channels or is not admin in any. Please check channel IDs and permissions.")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()

        except Exception as e:
            self.LOGGER(__name__).warning(f"Error checking DB channels: {e}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/weebs_support")
        self.LOGGER(__name__).info(f"""       


  ___ ___  ___  ___ ___ _    _____  _____  ___ _____ ___ 
 / __/ _ \|   \| __| __| |  |_ _\ \/ / _ )/ _ \_   _/ __|
| (_| (_) | |) | _|| _|| |__ | | >  <| _ \ (_) || | \__ \
 \___\___/|___/|___|_| |____|___/_/\_\___/\___/ |_| |___/
                                                         
 
                                          """)

        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username
        self.LOGGER(__name__).info(f"Bot Running..! Made by @Codeflix_Bots")   

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        try:
            await self.send_message(OWNER_ID, text=f"<b><blockquote> Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @Codeflix_Bots</blockquote></b>")
        except:
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @rohit_1888")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())

#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#
