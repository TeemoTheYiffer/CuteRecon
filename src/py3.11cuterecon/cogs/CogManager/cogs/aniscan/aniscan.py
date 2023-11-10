# Standard Library
import asyncio
import calendar
import logging
from datetime import datetime

# Discord.py
import discord

# Red
from redbot.core import Config, commands
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.data_manager import cog_data_path

import os
import aiohttp
import json
import tracemoepy

log = logging.basicConfig(level=logging.DEBUG)

__author__ = "Teemo the Yiffer"

class Aniscan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracemoe = tracemoepy.tracemoe.TraceMoe()
        #self.teemoai = Config.get_conf(self, identifier=2166355741317, force_registration=True)
        #default_global = {
        #    "API_Key": None,
        #    "User": {
        #        "temperature": "0.5"
        #        }
        #    }
        #self.teemoai.register_global(**default_global)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        # check whether the message was sent in a guild
        if message.guild is None:
            return
        # check whether the message author isn't a bot
        if message.author.bot:
            return
        # check whether the cog isn't disabled
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        # check whether the channel isn't on the ignore list 
        if not await self.bot.ignored_channel_or_guild(message):
            return
        # check whether the message author isn't on allowlist/blocklist
        if not await self.bot.allowed_by_whitelist_blacklist(message.author):
            return

    @commands.command()
    @commands.guild_only()
    async def animescan(self, ctx):
        """
        Scans anime capture for retrieval"
        """
        await ctx.send("Upload anime screen capture.")
        response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        if response.attachments:
            screencap=response.attachments[0].url
            async with tracemoepy.AsyncTrace() as tracemoe:
                result = await tracemoe.search(screencap, is_url = True)
                data = result["result"][0]
                #logging.info(data)
                #image_preview = self.tracemoe.image_preview(result)
                #await ctx.send(file=discord.File(image_preview, "image.png")) 
                #embed.set_image(url=self.Image_URL)
                video = self.tracemoe.natural_preview(result)
                with open(cog_data_path(self) / 'preview.mp4', 'wb') as f:
                    f.write(video)
                clip = str(cog_data_path(self) / 'preview.mp4')
                file = discord.File(clip, filename="preview.mp4")
                try:
                    await ctx.send(files=[file])
                except Exception:
                    log.error("Error sending video", exc_info=True)
                    pass
                try:
                    os.remove(clip)
                except Exception:
                    log.error("Error deleting video", exc_info=True)

                embed1 = discord.Embed(title='Anime Result',
                            description="Results for the screen capture scan.", color=0xff0000)
                embed1.add_field(name="Title:", value=f"{data['anilist']['title']['english']}"+ "\u200b", inline=True)
                embed1.add_field(name="Japanese Title:", value=f"{data['anilist']['title']['native']}"+ "\u200b", inline=True)
                embed1.add_field(name="AniList ID:", value=f"{data['anilist']['id']}"+ "\u200b", inline=True)
                #embed1.add_field(name="Season:", value=f"{data['season']}"+ "\u200b", inline=True)
                embed1.add_field(name="Episode:", value=f"{data['episode']}"+ "\u200b", inline=True)
                embed1.add_field(name="Filename:", value=f"{data['anilist']['filename']}"+ "\u200b", inline=False)

            await ctx.send(embed=embed1)
        else:
            await ctx.send("You took too long!", delete_after=60)
        await ctx.send("Done!")