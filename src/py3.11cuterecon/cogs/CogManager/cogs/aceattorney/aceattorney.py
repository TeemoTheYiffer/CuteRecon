import discord
import asyncio
import threading
import logging
import time
import sys
import os
import requests, json
import gc
from typing import List

from discord.ext import commands, tasks
from redbot.core.utils.chat_formatting import warning, error, info
from discord import Embed
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from objection_engine.beans.comment import Comment
from objection_engine.renderer import render_comment_list
from objection_engine import get_all_music_available
from .message import Message
from .render import Render, State
from .deletion import Deletion
logging.basicConfig(level=logging.DEBUG)

__author__ = "Teemo the Yiffer"

# Global Variables:
renderQueue = []
deletionQueue = []
lastRender = 0
deletionDelay = 0
cooldown = 30
staff_only = False

class AceAttorney(commands.Cog):
    """
    Ace Attorney Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.artist = Config.get_conf(self, identifier=5217205587303, force_registration=True)
        self.data_folder = str(cog_data_path(self))

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

    def addToDeletionQueue(self, message: discord.Message):
        # Only if deletion delay is grater than 0, add it to the deletionQueue.
        if int(deletionDelay) > 0:
            newDeletion = Deletion(message, int(deletionDelay))
            deletionQueue.append(newDeletion)

    @tasks.loop(minutes=5)
    async def garbageCollection(self):
        gc.collect()
        logging.info("Garbage collected")

    @tasks.loop(seconds=1)
    async def deletionQueueLoop(self):
        global deletionQueue
        deletionQueueSize = len(deletionQueue)
        # Delete message and remove from queue if remaining time is less than (or equal to) 0
        if deletionQueueSize > 0:
            for index in reversed(range(deletionQueueSize)):
                if await deletionQueue[index].update():
                    deletionQueue.pop(index)

    @tasks.loop(seconds=5)
    async def renderQueueLoop(self):
        global renderQueue
        renderQueueSize = len(renderQueue)
        #await changeActivity(f"{prefix}help | queue: {renderQueueSize}")
        for positionInQueue, render in enumerate(iterable=renderQueue, start=1):
            try:
                if render.getState() == State.QUEUED:
                    newFeedback = f"""
                    `Fetching messages... Done!`
                    `Position in the queue: #{(positionInQueue)}`
                    """
                    await render.updateFeedback(newFeedback)

                if render.getState() == State.INPROGRESS:
                    newFeedback = f"""
                    `Fetching messages... Done!`
                    `Your video is being generated...`
                    """
                    await render.updateFeedback(newFeedback)

                if render.getState() == State.FAILED:
                    newFeedback = f"""
                    `Fetching messages... Done!`
                    `Your video is being generated... Failed!`
                    """
                    await render.updateFeedback(newFeedback)
                    render.setState(State.DONE)

                if render.getState() == State.RENDERED:
                    newFeedback = f"""
                    `Fetching messages... Done!`
                    `Your video is being generated... Done!`
                    `Uploading file to Discord...`
                    """
                    await render.updateFeedback(newFeedback)

                    render.setState(State.UPLOADING)

                    # If the file size is lower than the maximun file size allowed in this guild, upload it to Discord
                    logging.info(f"File: {render.getOutputFilename()}")
                    fileSize = os.path.getsize(render.getOutputFilename())
                    if fileSize < render.getContext().channel.guild.filesize_limit:
                        await render.getContext().send(content=render.getContext().author.mention, file=discord.File(render.getOutputFilename()))
                        render.setState(State.DONE)
                        newFeedback = f"""
                        `Fetching messages... Done!`
                        `Your video is being generated... Done!`
                        `Uploading file to Discord... Done!`
                        """
                        await render.updateFeedback(newFeedback)
                    else:
                        try:
                            newFeedback = f"""
                            `Fetching messages... Done!`
                            `Your video is being generated... Done!`
                            `Video file too big for you server! {round(fileSize/1000000, 2)} MB`
                            `Trying to upload file to an external server...`
                            """
                            await render.updateFeedback(newFeedback)
                            with open(render.getOutputFilename(), 'rb') as videoFile:
                                files = {'files[]': (render.getOutputFilename(), videoFile)}
                                response = requests.post('https://uguu.se/upload.php?output=text', files=files).content.decode("utf-8").strip()
                                parsed_response = json.loads(response)
                                url = parsed_response["files"][0]["url"]
                                newFeedback = f"""
                                `Fetching messages... Done!`
                                `Your video is being generated... Done!`
                                `Video file too big for you server! {round(fileSize/1000000, 2)} MB`
                                `Trying to upload file to an external server... Done!`
                                """
                                await render.updateFeedback(newFeedback)
                                await render.getContext().send(content=f"{render.getContext().author.mention}\n{url}\n_This video will be deleted in 48 hours_")
                                render.setState(State.DONE)

                        except Exception as exception:
                            newFeedback = f"""
                            `Fetching messages... Done!`
                            `Your video is being generated... Done!`
                            `Video file too big for you server! {round(fileSize/1000000, 2)} MB`
                            `Trying to upload file to an external server... Failed!`
                            """
                            await render.updateFeedback(newFeedback)
                            exceptionEmbed = discord.Embed(description=exception, color=0xff0000)
                            exceptionMessage = await render.getContext().send(embed=exceptionEmbed)
                            self.addToDeletionQueue(exceptionMessage)
                            render.setState(State.DONE)

            except Exception as e:
                logging.exception(e)
                try:
                    render.setState(State.DONE)
                except:
                    pass
            finally:
                if render.getState() == State.DONE:
                    self.clean(render.getMessages(), render.getOutputFilename())
                    self.addToDeletionQueue(render.getFeedbackMessage())

        # Remove from queue if state is DONE
        if renderQueueSize > 0:
            for index in reversed(range(renderQueueSize)):
                if renderQueue[index].getState() == State.DONE:
                    renderQueue.pop(index)

    #def to_Comment(self):
    #    return Comment(user_id=self.user.id, user_name=self.user.name, text_content=self.text, evidence_path=self.evidence)    
    #def addToDeletionQueue(message: discord.Message):
    #    # Only if deletion delay is grater than 0, add it to the deletionQueue.
    #    if int(deletionDelay) > 0:
    #        newDeletion = Deletion(message, int(deletionDelay))
    #        deletionQueue.append(newDeletion)

    @commands.command()
    @commands.guild_only()
    async def queue(self, context):
        filename = self.data_folder + "/queue.txt"
        with open(filename, 'rb') as queue:
            global renderQueue
            renderQueueSize = len(renderQueue)
            queue.write(f"There are {renderQueueSize} item(s) in the queue!\n")
            for positionInQueue, render in enumerate(iterable=renderQueue):
                queue.write(f"\n#{positionInQueue:04}\n")
                try: queue.write(f"Requested by: {context.author.author.name}#{context.author.discriminator}\n")
                except: pass
                try: queue.write(f"Number of messages: {len(render.getMessages())}\n")
                except: pass
                try: queue.write(f"Guild: {render.getFeedbackMessage().channel.guild.name}\n")
                except: pass
                try: queue.write(f"Channel: #{render.getFeedbackMessage().channel.name}\n")
                except: pass
                try: queue.write(f"State: {render.getStateString()}\n")
                except: pass
        await context.send(file=discord.File(filename))
        self.clean([], filename)

    @commands.command()
    @commands.guild_only()
    async def acerender(self, ctx, numberOfMessages: int = 0, music: str = 'pwr'):
        """
        Ace Attorney Render
        """
        feedbackMessage = await ctx.send("Attempting Ace Attorney Render.")
        global lastRender, cooldown
        if lastRender is not None and cooldown is not None:
            if (time.time() - lastRender) < cooldown:
                errEmbed = discord.Embed(description=f"Please wait **{round(cooldown - (time.time() - lastRender))}** seconds before using this command again.", color=0xff0000)
                errMsg = await ctx.send(embed=errEmbed)
                self.addToDeletionQueue(errMsg)
                return
        try:
            #await feedbackMessage.edit(content="`Fetching messages...`")
            if numberOfMessages == 0:
                raise Exception("Please specify the number of messages to be rendered!")
            if not (numberOfMessages in range(1, 101)):
                raise Exception("Number of messages must be between 1 and 100")

            # baseMessage is the message from which the specified number of messages will be fetch, not including itself
            baseMessage = ctx.message.reference.resolved if ctx.message.reference else ctx.message
            courtMessages = []
            discordMessages = []

            # If the render command was executed within a reply (baseMessage and context.Message aren't the same), we want
            # to append the message the user replied to (baseMessage) to the 'discordMessages' list and substract 1 from
            # 'numberOfMessages' that way we are taking the added baseMessage into consideration and avoid getting 1 extra message)
            if not baseMessage.id == ctx.message.id:
                numberOfMessages = numberOfMessages - 1
                discordMessages.append(baseMessage)
            #logging.info(ctx.channel.history(limit=numberOfMessages, oldest_first=False, before=baseMessage))
            discordMessages = [message async for message in ctx.channel.history(limit=numberOfMessages, oldest_first=False, before=baseMessage)]
            #discordMessages = ctx.channel.history(limit=numberOfMessages, oldest_first=False, before=baseMessage) #.flatten()
            
            for discordMessage in discordMessages:
                message = Message(discordMessage)
                if message.text.strip():
                    courtMessages.insert(0, message.to_Comment())
            if len(courtMessages) < 1:
                raise Exception("There should be at least one person in the conversation.")

            newRender = Render(State.QUEUED, ctx, feedbackMessage, courtMessages, music)
            renderQueue.append(newRender)
            lastRender = time.time()
            try:
                for render in renderQueue:
                    if render.getState() == State.QUEUED:
                        render.setState(State.INPROGRESS)
                        try:
                            render_comment_list(render.getMessages(), render.getOutputFilename(), music_code=render.music_code, resolution_scale=2)
                            render.setState(State.RENDERED)
                        except Exception as exception:
                            logging.exception(exception)
                            render.setState(State.FAILED)
                        finally:
                            break
            except Exception as e:
                logging.exception(e)

        except Exception as exception:
            exceptionEmbed = discord.Embed(description=str(exception), color=0xff0000)
            await feedbackMessage.edit(content="", embed=exceptionEmbed)
            self.addToDeletionQueue(feedbackMessage)


    @commands.Cog.listener()
    async def on_ready(self):
        backgroundThread = threading.Thread(target=self.renderThread, name="RenderThread")
        backgroundThread.start()
        self.renderQueueLoop.start()
        self.deletionQueueLoop.start()

    def clean(self, thread: List[Comment], filename):
        try:
            os.remove(filename)
        except Exception as e:
            logging.exception(e)
        try:
            for comment in thread:
                if (comment.evidence_path is not None):
                    os.remove(comment.evidence_path)
        except Exception as e:
            logging.exception(e)

    def renderThread(self):
        global renderQueue
        while True:
            time.sleep(2)
            try:
                for render in renderQueue:
                    if render.getState() == State.QUEUED:
                        render.setState(State.INPROGRESS)
                        try:
                            render_comment_list(render.getMessages(), render.getOutputFilename(), music_code=render.music_code, resolution_scale=2)
                            render.setState(State.RENDERED)
                        except Exception as e:
                            logging.exception(e)
                            render.setState(State.FAILED)
                        finally:
                            break
            except Exception as e:
                logging.exception(e)