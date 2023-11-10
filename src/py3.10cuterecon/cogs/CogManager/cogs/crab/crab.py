import os
import aiohttp
import asyncio
import logging
import functools
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

from init import bot, logger

CRAB_LINK = (
    "https://github.com/DankMemer/meme-server"
    "/raw/9ce10a61e133f5b87b24d425fc671c9295affa6a/assets/crab/template.mp4"
)
# Use a historical link incase something changes
FONT_FILE = (
    "https://github.com/matomo-org/travis-scripts/"
    "raw/65cace9ce09dca617832cbac2bbae3dacdffa264/fonts/Verdana.ttf"
)
logger = logging.getLogger(__name__)

"""
Create your very own crab rave
"""

async def check_video_file():
    if not ("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/template.mp4"):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(CRAB_LINK) as resp:
                    data = await resp.read()
            with open("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/" / "template.mp4", "wb") as save_file:
                save_file.write(data)
        except Exception:
            logger.error("Error downloading crabrave video template", exc_info=True)
            return False
    return True

async def check_font_file():
    if not ("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/Verdana.ttf"):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(FONT_FILE) as resp:
                    data = await resp.read()
            with open("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/Verdana.ttf", "wb") as save_file:
                save_file.write(data)
        except Exception:
            logger.error("Error downloading crabrave video template", exc_info=True)
            return False
    return True

async def crab(ctx):
    """Make crab rave videos

        There must be exactly 1 `,` to split the message
    """
    chat = ctx.chat_id
    t = ctx.text.replace("/crab", "")
    # t = ctx.text.clean_content[len(f"{ctx.prefix}{ctx.invoked_with}"):]
    t = t.upper().replace(", ", ",").split(",")
    if not await check_video_file():
        return await ctx.respond("I couldn't download the template file.")
    if not await check_font_file():
        return await ctx.respond("I couldn't download the font file.")
    if len(t) != 2:
        return await ctx.respond("You must submit exactly two strings split by comma")
    if (not t[0] and not t[0].strip()) or (not t[1] and not t[1].strip()):
        return await ctx.respond("Cannot render empty text")
    fake_task = functools.partial(make_crab, t=t, u_id=ctx.chat_id)
    task = bot.loop.run_in_executor(None, fake_task)
    async with bot.action(chat, 'typing'):
        try:
            await asyncio.wait_for(task, timeout=300)
        except asyncio.TimeoutError:
            logger.error("Error generating crabrave video", exc_info=True)
            return
    fp = f"/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/{ctx.chat_id}crabrave.mp4"
    try:
        await bot.send_file(chat, file=fp)
    except Exception:
        logger.error("Error sending crabrave video", exc_info=True)
        pass
    try:
        os.remove(fp)
    except Exception:
        logger.error("Error deleting crabrave video", exc_info=True)

def make_crab(t, u_id):
    """Non blocking crab rave video generation from DankMemer bot

    https://github.com/DankMemer/meme-server/blob/master/endpoints/crab.py
    """
    fp = str("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/Verdana.ttf")
    clip = VideoFileClip(str("/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/template.mp4"))
    # clip.volume(0.5)
    text = TextClip(t[0], fontsize=48, color="white", font=fp)
    text2 = (
        TextClip("____________________", fontsize=48, color="white", font=fp)
        .set_position(("center", 210))
        .set_duration(15.4)
    )
    text = text.set_position(("center", 200)).set_duration(15.4)
    text3 = (
        TextClip(t[1], fontsize=48, color="white", font=fp)
        .set_position(("center", 270))
        .set_duration(15.4)
    )

    video = CompositeVideoClip(
        [clip, text.crossfadein(1), text2.crossfadein(1), text3.crossfadein(1)]
    ).set_duration(15.4)
    video = video.volumex(0.1)
    video.write_videofile(
        (f"/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/{u_id}crabrave.mp4"),
        threads=1,
        preset="superfast",
        verbose=False,
        logger=None,
        temp_audiofile=(f"/home/teemo/.local/share/Red-DiscordBot/cogs/CrabRave/{u_id}crabraveaudio.mp3")
        # ffmpeg_params=["-filter:a", "volume=0.5"]
    )
    clip.close()
    video.close()
    return True