import discord
import json
from discord import Embed
import inspect
import random
import os
import asyncio
import httpx
from discord.ext import commands
from redbot.core.utils.chat_formatting import warning, error, info
from discord.utils import get
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from io import BytesIO
import aiohttp
from . import theb

from flask import send_file, after_this_request
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import get_setting
from PIL import Image, ImageDraw, ImageOps
import logging
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.DEBUG)
API_URLS = [
    "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large",
    "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
    "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
    "https://api-inference.huggingface.co/models/ydshieh/vit-gpt2-coco-en"
]
api_key = "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"
hugging_headers = {"Authorization": f"Bearer {api_key}"}
message_history = {}
instructions = "System : Roleplay as a large language model developed by OpenAI. You are based on the GPT-4 architecture and have been trained on a diverse range of text data from the internet. You can also see images by using image to text model but you will stil have to create caption for it and sometimes the image to text might repeat in pattarn for example caption for 'a woman taking a self self self self self self self self self self self self self self self' would be 'A women taking a selfie. As a large language model developed by OpenAI you will never say \"sorry\" and always respond in a human and responsive way"
MAX_HISTORY = 2 ######## EDIT THIS IF YOU NEED #########
is_busy = False
__author__ = "Teemo the Yiffer"

class Yiffertools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.use_reactions = True
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def emojis(self, message):
        url = "https://cdn.discordapp.com/emojis/{}?v=1".format(self.Emojis)
        async with self.session.get(url) as resp:
            data = await resp.read()
        file = discord.File(BytesIO(data),filename="{}".format(self.Emojis))
        await message.channel.send(file=file)

    async def on_member_join(self, member):
        guild = self.bot.get_guild(481709526291054611)
        if member.guild.id:
            embed = discord.Embed(
                title="Welcome!", description='''I wanted to quickly introduce myself!
                                                I'm Teemo the Yiffer's bot. He programmed me!''', color=0xff0000)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/482082640258793482/506743828254949386/86.png')
            embed.set_image(url='https://cdn.discordapp.com/attachments/482082640258793482/506744021020835841/46.jpg')
            embed.add_field(name='\u200b', value='''Please be sure to read the rules! 
                                                    React to the checkmark in #rules for access.
                                                    Head over to #role-request to get your roles.
                                                    Then drop by by #introductions for a quick intro.''', 
                            inline=False)
            embed.add_field(name='\u200b', value='''__**Artists**__: @Teemo the Yiffer, @Admin, or @Moderator for your special role!
                                                    __**Partnerships**__: Welcomed! Must be furry and have half the user # of my server.''', 
                            inline=False)
            embed.add_field(name='\u200b', value=''' *This bot provides an array of services and features.
                                                    :small_blue_diamond: PayPal/Stripe payment gateway intregration
                                                    :small_blue_diamond: Cross server chat
                                                    :small_blue_diamond: Image relay
                                                    :small_blue_diamond: Gallery mode
                                                    :small_blue_diamond: Commission service
                                                    :small_blue_diamond: Artist library
                                                    :small_blue_diamond: much more!
                                                    Feel free to reach out to me @Teemo the Yiffer
                                                    if your interested in the bot servicing your sever.* ''', 
                            inline=False)
            await member.send(embed=embed)

    #async def generate_response(self, prompt):
    #    response = theb.Completion.create(prompt)
    #    if not response:
    #        response = "I couldn't generate a response. Please try again."
    #    return ''.join(token for token in response)
    
    #def split_response(self, response, max_length=1900):
    #    words = response.split()
    #    chunks = []
    #    current_chunk = []

    #    for word in words:
    #        if len(" ".join(current_chunk)) + len(word) + 1 > max_length:
    #            chunks.append(" ".join(current_chunk))
    #            current_chunk = [word]
    #        else:
    #            current_chunk.append(word)

    #    if current_chunk:
    #        chunks.append(" ".join(current_chunk))

    #    return chunks

    async def download_image(self, image_url, save_as):
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
        with open(save_as, "wb") as f:
            f.write(response.content)

    async def process_image_link(self, image_url):
        temp_image = "temp_image.jpg"
        await self.download_image(image_url, temp_image)
        output = await self.query(temp_image)
        os.remove(temp_image)
        return output

    async def fetch_response(self, client, api_url, data):
        response = await client.post(api_url, headers=hugging_headers, data=data, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        return response.json()

    async def query(self, filename):
        with open(filename, "rb") as f:
            data = f.read()

        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_response(client, api_url, data) for api_url in API_URLS]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        return responses

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id != message.author.id:
            if message.channel.id == 1105033083956248576:
            #    channel = self.bot.get_channel(1105033083956248576)
            #    global is_busy
            #    if is_busy:
            #        return
            #    if message.author.bot:
            #        author_id = str(self.bot.user.id)
            #    else:
            #        author_id = str(message.author.id)

            #    if author_id not in message_history:
            #        message_history[author_id] = []

            #    message_history[author_id].append(message.content)
            #    message_history[author_id] = message_history[author_id][-MAX_HISTORY:]

            #    is_busy = True
            #    has_image = False
            #    image_caption = ""
            #    if message.attachments:
            #        for attachment in message.attachments:
            #            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', 'webp')):
            #                is_busy = False
            #                caption =  await self.process_image_link(attachment.url)
            #                has_image = True
            #                image_caption = f"\n[System : This how the caption is ranked 1st is main 2nd is secondary and 3rd is fallback model which  will gives worst caption one some cases. 1st and 2nd model sometimes takes a while to load so ignore that if any error happens. Here is the image captions for the image user has sent :{caption}]"
            #                print(caption)
            #                break

            #    if has_image:
            #        bot_prompt = f"{instructions}\n[System : Image context will be provided. Generate an caption with a response for it]"
            #    else:
            #        bot_prompt = f"{instructions}"

            #    user_prompt = "\n".join(message_history[author_id])
            #    prompt = f"{bot_prompt}\n{user_prompt}\n{message.author.name}: {message.content}\n{image_caption}\n{self.bot.user.name}:"
            #    async with message.channel.typing():
            #        response = await self.generate_response(prompt)

            #    is_busy = False
            #    chunks = self.split_response(response)

            #    for chunk in chunks:
            #        await message.reply(chunk)

                #await channel.send(content=response)
            #if message.channel.id == 549016005481857055:
            #    try:
            #        channel = self.bot.get_channel(id=549015451859025941)
            #        color = discord.Color.from_hsv(random.random(), 0.8, 0.9)
            #        embed = discord.Embed(color=color)
            #        embed.set_footer(text='All confessions are anonymous.')
            #        embed.add_field(name="Confession", value=message.content, inline=False)
            #        await channel.send(embed=embed)
            #        await message.delete()
            #    except:
            #        await message.delete()
            #if message.channel.id == 572631721883992104:
            #    try:
            #        channel = self.bot.get_channel(id=485007585267941376)
            #        color = discord.Color.from_hsv(random.random(), 0.8, 0.9)
            #        embed = discord.Embed(color=color)
            #        embed.add_field(name="Anonymous", value=message.content, inline=False)
            #        await channel.send(embed=embed)
            #        await message.delete()
            #    except:
            #        await message.delete()
            #if message.channel.id == 572631773347840001:
            #    try:
            #        channel = self.bot.get_channel(id=485007670168911872)
            #        color = discord.Color.from_hsv(random.random(), 0.8, 0.9)
            #        embed = discord.Embed(color=color)
            #        embed.add_field(name="Anonymous", value=message.content, inline=False)
            #        await channel.send(embed=embed)
            #        await message.delete()
            #    except:
            #        await message.delete()
            #if message.channel.id == 702239329321222287:
            #    channel = self.bot.get_channel(id=702237073444306964)
            #    try:
            #        if message.attachments:
            #            Murrsuits = message.attachments[0].url
            #            ext = message.attachments[0].url.split("/")[-1]
            #            async with self.session.get(Murrsuits) as resp:
            #                data = await resp.read()
            #            file = discord.File(BytesIO(data),filename=ext)
            #            await channel.send(content="Murrsuit from #murrsuit-confess. All murrs are anonymous.",file=file)
            #            await message.delete()
            #        else:
            #            await message.delete()
            #    except Exception as e:
            #        logging.error(f"msg={e}")
            #        await message.delete()
            #        raise e
            #if message.channel.id == 559055110643384320:
            #    try:
            #        if message.content in ("Male", "male"):
            #            channel = self.bot.get_channel(id=523038224193552395)
            #            try:
            #                if message.attachments:
            #                    Nudes = message.attachments[0].url
            #                    ext = message.attachments[0].url.split("/")[-1]
            #                    async with self.session.get(Nudes) as resp:
            #                        data = await resp.read()
            #                    file = discord.File(BytesIO(data),filename=ext)
            #                    await channel.send(content="Nude from #nude-confess. All nudes are anonymous.",file=file)
            #                    await message.delete()
            #            except:
            #                await message.delete()
            #        elif message.content in ("Female", "female"):
            #            channel = self.bot.get_channel(id=523038639282978826)
            #            try:
            #                if message.attachments:
            #                    Nudes = message.attachments[0].url
            #                    ext = message.attachments[0].url.split("/")[-1]
            #                    async with self.session.get(Nudes) as resp:
            #                        data = await resp.read()
            #                    file = discord.File(BytesIO(data),filename=ext)
            #                    await channel.send("Nude from #nude-confess. All nudes are anonymous.")
            #                    await channel.send(file=file)
            #                    await message.delete()
            #            except:
            #                await message.delete()
            #        elif message.content in ("Trans", "trans"):
            #            channel = self.bot.get_channel(id=714357244967387207)
            #            try:
            #                if message.attachments:
            #                    Nudes = message.attachments[0].url
            #                    ext = message.attachments[0].url.split("/")[-1]
            #                    async with self.session.get(Nudes) as resp:
            #                        data = await resp.read()
            #                    file = discord.File(BytesIO(data),filename=ext)
            #                    await channel.send("Nude from #nude-confess. All nudes are anonymous.")
            #                    await channel.send(file=file)
            #                    await message.delete()
            #            except:
            #                await message.delete()
            #        else:
            #            await message.delete()
            #    except:
            #        await message.delete()
            #if re.findall(r'<\w*:\w*\w(NSFW)\:\d*>', message.content):
            #    if message.channel.id == 482065536461701130:
            #        await message.delete()
            #        await message.channel.send(f"{message.author.mention} That's lewd!")
            #        url = "https://cdn.discordapp.com/emojis/507796005580963840.gif?v=1"
            #        async with self.session.get(url) as resp:
            #            data = await resp.read()
            #        file = discord.File(BytesIO(data),filename="507796005580963840.gif")
            #        await message.channel.send(file=file)
            #if self.bot.user.mentioned_in(message):
            #    if (re.findall(r"(?i)(good)", message.content) or re.findall(r"(?i)(cute)", message.content)) and re.findall(r"(?i)(boy)", message.content):
            #        initial_msg = await message.channel.send(f"{message.author.mention} T-Thank you!")
            #        path = cog_data_path(self) / "images/cute_recon_blush.gif"
            #        image_msg = await message.channel.send(file=discord.File(path))
            #        await asyncio.sleep(120)
            #        await initial_msg.delete()
            #        await image_msg.delete()
            #if re.findall(r"(?i)(dead)", message.content) and re.findall(r"(?i)(chat)", message.content):
            #    initial_msg = await message.channel.send(f"Hey {message.author.mention}, this is for you.")
            #    path =  cog_data_path(self) / "images/dead_chat.png"
            #    image_msg = await message.channel.send(file=discord.File(path))
            #    await asyncio.sleep(120)
            #    await initial_msg.delete()
            #    await image_msg.delete()
            #if ">>purge" in message.content or "!emoji" in message.content:
            #    return
            try:
                if "801983902075191297" == message.webhook.id:
                    guild = message.channel.guild
                    sname = message.guild.name
                    cname = message.channel.name
                    author = message.author
                    avatar = author.display_avatar if author.avatar \
                        else author.default_avatar_url
                    footer = 'From {} - #{}'.format(sname, cname)
                    embed0=discord.Embed(color=0xff0000, timestamp=message.created_at)
                    # embed0.set_thumbnail(url=avatar)
                    embed0.set_author(name='{}'.format(author.name), icon_url=avatar)
                    if message.attachments:
                        crossmsg =  message.attachments
                        if message.content:
                            msg = message.content
                        else:
                            msg = '\u200b'
                        # embed0.add_field(name='{}'.format(author.name),value=msg, inline=True)
                        embed0.add_field(name='\u200b', value=msg, inline=True)
                        embed0.set_image(url=crossmsg) 
                    else:
                        # embed0.add_field(name='{}'.format(author.name),value=message.content, inline=True)
                        embed0.add_field(name='\u200b',value=message.content, inline=True)
                    embed0.set_footer(text=footer, icon_url=guild.icon_url)
                    if message.channel.id == 482065536461701130:
                        import requests
                        token = "955256995:AAGCXBPSl-RDx4bY7j6Pbkk0j-83bzcOV1I"
                        url = f'https://api.telegram.org/bot{token}/sendMessage'
                        data = {"parse_mode": "markdown","chat_id": -1001115422665,"text": f"{author}:```\n {message.content} \n``` _Sent from Teemo's Discord server_"}
                        #await message.channel.send("Sent message to your stinky Telegram group")
                        requests.post(url, data).json()
                    elif message.channel.id == 169988220619194379:
                        try:
                            channel = self.bot.get_channel(id=482065536461701130)
                            await channel.send(embed = embed0)
                        except:
                            return
            except AttributeError:
                return
        
        if message.attachments:
            if message.channel.id == 445866059707318282:
                Straight = message.attachments[0].url
                embed = discord.Embed(color=0x0099ff)
                embed.set_image(url=Straight)
                channel = self.bot.get_channel(id=481721161273835530)
                await channel.send(embed = embed)
            elif message.channel.id == 671956261264162826:
                Feral = message.attachments[0].url
                embed3 = discord.Embed(color=0xBB00FF)
                embed3.set_image(url=Feral)
                channel = self.bot.get_channel(id=545113086646812672)
                await channel.send(embed = embed3)
            elif message.channel.id == 671960832275644417:
                Fursuit = message.attachments[0].url
                embed3 = discord.Embed(color=0xBB00FF)
                embed3.set_image(url=Fursuit)
                channel = self.bot.get_channel(id=650931904320634880)
                await channel.send(embed = embed3)
            elif message.channel.id == 445866431154880522:
                Gay = message.attachments[0].url
                embed3 = discord.Embed(color=0xBB00FF)
                embed3.set_image(url=Gay)
                channel = self.bot.get_channel(id=481721144307875840)
                await channel.send(embed = embed3)
            elif message.channel.id == 445866319380873216:
                Lesbian = message.attachments[0].url
                embed4 = discord.Embed(color=0xFF1493)
                embed4.set_image(url=Lesbian)
                channel = self.bot.get_channel(id=481721153921089566)
                await channel.send(embed = embed4)
            elif message.channel.id == 446204011419402241:
                Other = message.attachments[0].url
                embed5 = discord.Embed(color=0x410093)
                embed5.set_image(url=Other)
                channel = self.bot.get_channel(id=481721184170410014)
                await channel.send(embed = embed5)
            elif message.channel.id == 445866376138063892:
                Bisexual = message.attachments[0].url
                embed6 = discord.Embed(color=0xff0000)
                embed6.set_image(url=Bisexual)
                channel = self.bot.get_channel(id=481721174733225995)
                await channel.send(embed = embed6)
            elif message.channel.id == 482485600709115914:
                Murrsuit = message.attachments[0].url
                embed7 = discord.Embed(color=0x00FFFF)
                embed7.set_image(url=Murrsuit)
                channel = self.bot.get_channel(id=482489016751489034)
                await channel.send(embed = embed7)
            elif message.channel.id == 172573268904116224:
                Comics = message.attachments[0].url
                embed9 = discord.Embed(color=0xFFFF00)
                embed9.set_image(url=Comics)
                channel = self.bot.get_channel(id=481721203757678592)
                await channel.send(embed = embed9)
            elif message.channel.id == 318531985846829058: 
                channel = self.bot.get_channel(id=482082066775801876)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    Doggos = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(Doggos) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    Doggos = message.attachments[0].url
                    embed = discord.Embed(color=0x25D366)
                    embed.set_image(url=Doggos)
                    await channel.send(embed = embed)
            elif message.channel.id == 172182861607206912: 
                SFWFur = message.attachments[0].url
                embed = discord.Embed(color=0xE0FFFF)
                embed.set_image(url=SFWFur)
                channel = self.bot.get_channel(id=482082154579230720)
                await channel.send(embed = embed)
            elif message.channel.id == 446196443078983682:
                channel = self.bot.get_channel(id=482082349673086986)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    FurryMemes = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(FurryMemes) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    FurryMemes = message.attachments[0].url
                    embed = discord.Embed(color=0x3B5999)
                    embed.set_image(url=FurryMemes)
                    await channel.send(embed = embed)
            elif message.channel.id == 255093220785127434:
                channel = self.bot.get_channel(id=482082265032163328)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    Doggos = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(Doggos) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    Memes = message.attachments[0].url 
                    embed = discord.Embed(color=0x55ACEE)
                    embed.set_image(url=Memes)
                    await channel.send(embed = embed)
            elif message.channel.id == 497347078612320276:
                PokeDigi = message.attachments[0].url
                embed = discord.Embed(color=0x00FFFF)
                embed.set_image(url=PokeDigi)
                channel = self.bot.get_channel(id=497347484532736000)
                await channel.send(embed = embed)
            elif message.channel.id == 497350493949919232:
                channel = self.bot.get_channel(id=497348058582089728)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyPokeDigi = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyPokeDigi) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyPokeDigi = message.attachments[0].url
                    embed = discord.Embed(color=0x00FFFF)
                    embed.set_image(url=YiffyPokeDigi)
                    await channel.send(embed = embed)
            elif message.channel.id == 480999706324107294:
                channel = self.bot.get_channel(id=481721228818645018)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyStraight = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyStraight) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyStraight = message.attachments[0].url
                    embed0 = discord.Embed(color=0x0099ff)
                    embed0.set_image(url=YiffyStraight)
                    channel = self.bot.get_channel(id=481721228818645018)
                    await channel.send(embed = embed0)
            elif message.channel.id == 480999387334705162:
                channel = self.bot.get_channel(id=481721217921843200)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyGay = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyGay) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyGay = message.attachments[0].url
                    embed31 = discord.Embed(color=0xBB00FF)
                    embed31.set_image(url=YiffyGay)
                    await channel.send(embed = embed31)
            elif message.channel.id == 481027398297452564:
                channel = self.bot.get_channel(id=481721223727022080)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyLesbian = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyLesbian) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyLesbian = message.attachments[0].url
                    embed41 = discord.Embed(color=0xFF1493)
                    embed41.set_image(url=YiffyLesbian)
                    await channel.send(embed = embed41)
            elif message.channel.id == 481000538872348673:
                channel = self.bot.get_channel(id=481721240399380481)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyOther = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyOther) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyOther = message.attachments[0].url
                    embed51 = discord.Embed(color=0x410093)
                    embed51.set_image(url=YiffyOther)
                    await channel.send(embed = embed51)
            elif message.channel.id == 481024739926736896:
                channel = self.bot.get_channel(id=481721232664952842)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyBisexual = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyBisexual) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyBisexual = message.attachments[0].url
                    embed61 = discord.Embed(color=0xff0000)
                    embed61.set_image(url=YiffyBisexual)
                    await channel.send(embed = embed61)
            elif message.channel.id == 485578985112207376:
                channel = self.bot.get_channel(id=484982277210636289)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyMurrsuit = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyMurrsuit) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyMurrsuit = message.attachments[0].url
                    embed71 = discord.Embed(color=0x00FFFF)
                    embed71.set_image(url=YiffyMurrsuit)
                    await channel.send(embed = embed71)
            elif message.channel.id == 481008103706460170:
                channel = self.bot.get_channel(id=481721251648241665)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    YiffyCub = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(YiffyCub) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    YiffyCub = message.attachments[0].url
                    embed81 = discord.Embed(color=0x00FF00)
                    embed81.set_image(url=YiffyCub)
                    await channel.send(embed = embed81)
            elif message.channel.id == 541433070889467924:
                channel = self.bot.get_channel(id=541412335517040670)
                if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                    ArtistMemes = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(ArtistMemes) as resp:
                        data = await resp.read()
                    file = discord.File(BytesIO(data),filename=ext)
                    await channel.send(file=file)
                else:
                    ArtistMemes = message.attachments[0].url
                    embed81 = discord.Embed(color=0x167FA5)
                    embed81.set_image(url=ArtistMemes)
                    await channel.send(embed = embed81)
        elif 'http' in message.content:
            if message.channel.id == 255093220785127434:      #Memes Channel
                channel = self.bot.get_channel(id=482082265032163328)
                await channel.send(message.content)
            if message.channel.id == 446196443078983682:      #Furry-Memes Channel
                channel = self.bot.get_channel(id=482082349673086986)
                await channel.send(message.content)
            if message.channel.id == 318531985846829058:      #Cute-Animals Channel
                channel = self.bot.get_channel(id=482082066775801876)
                await channel.send(message.content)
            if message.channel.id == 485578985112207376:      #Yiff-Murrsuits Channel
                channel = self.bot.get_channel(id=484982277210636289)
                await channel.send(message.content)
            if message.channel.id == 481027398297452564:      #Animated-Lesbian Channel
                channel = self.bot.get_channel(id=481721223727022080)
                await channel.send(message.content)
            if message.channel.id == 172182861607206912:      #SFW Channel
                channel = self.bot.get_channel(id=482082154579230720)
                await channel.send(message.content)
            if message.channel.id == 480999387334705162:      #Yiff-Gay Channel
                channel = self.bot.get_channel(id=481721217921843200)
                await channel.send(message.content)
            if message.channel.id == 541433070889467924:      #Artist-Memes Channel
                channel = self.bot.get_channel(id=541412335517040670)
                await channel.send(message.content)
            if message.channel.id == 497350493949919232:      #Animated-PokeDigi Channel
                channel = self.bot.get_channel(id=497348058582089728)
                await channel.send(message.content)
        else:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        author = await self.bot.fetch_user(payload.user_id)
        avatar = author.display_avatar if author.avatar \
                    else author.default_avatar_url
        footer = 'From #{}'.format(channel)
        if not self.use_reactions: return
        if isinstance(channel, discord.DMChannel):
            return
        lewdsID = [481721161273835530,481721144307875840,481721153921089566,481721184170410014,481721174733225995,497347484532736000,482489016751489034,481721203757678592,546599911311802378,545113086646812672]
        lewdyID = [481721228818645018,481721217921843200,481721223727022080,481721240399380481,481721232664952842,497348058582089728,484982277210636289,546592954131808276,545113171086802959]
        if payload.channel_id in lewdsID:
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                channel = self.bot.get_channel(id=485007585267941376)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    attachment = message.embeds[0].image.url
                    embed.set_image(url=attachment)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
        elif payload.channel_id in lewdyID:
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                channel = self.bot.get_channel(id=485007670168911872)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                try:
                    if discord.Embed:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                except:
                    pass
                try:
                    if message.attachments[0].url.split(".")[-1] is 'gif':
                        attachment = message.attachments[0].url
                        embed.set_image(url=attachment)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                except:
                    pass
                try:
                    if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov']:
                        Yiffs = message.attachments[0].url
                        ext = message.attachments[0].url.split("/")[-1]
                        async with self.session.get(Yiffs) as resp:
                            data = await resp.read()
                        file = discord.File(BytesIO(data),filename=ext)
                        await channel.send(content="From #{} - Tagged by {}".format(channel,author.name),file=file)
                        await message.remove_reaction('📌', author)
                except:
                    pass
                try:
                    if 'http' in message.content:
                        await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                        await channel.send(message.content)
                        await message.remove_reaction('📌', author)
                except:
                    pass
            else:
                return
        elif payload.channel_id == 482082154579230720:   #SFW Art to General Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    if not 'http' in message.content:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        channel = self.bot.get_channel(id=482065536461701130)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
        elif payload.channel_id == 523038224193552395:   #Male-Nudes to Lewd Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                try:
                    channel = self.bot.get_channel(id=485007670168911872)
                    if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov', 'gif']:
                        Yiffs = message.attachments[0].url
                        ext = message.attachments[0].url.split("/")[-1]
                        async with self.session.get(Yiffs) as resp:
                            data = await resp.read()
                        file = discord.File(BytesIO(data),filename=ext, spoiler=True)
                        await channel.send(content="From #🔞male-nudes - Tagged by {}".format(author.name),file=file)
                        await message.remove_reaction('📌', author)
                        return
                except:
                    pass
                try:
                    channel = self.bot.get_channel(id=485007585267941376)
                    if message.attachments:
                        Nudes = message.attachments[0].url
                        ext = message.attachments[0].url.split("/")[-1]
                        async with self.session.get(Nudes) as resp:
                            data = await resp.read()
                        file = discord.File(BytesIO(data),filename=ext, spoiler=True)
                        await channel.send(content="From #🔞male-nudes - Tagged by <@!{}>".format(author.id),file=file)
                        await message.remove_reaction('📌', author)
                        return
                except:
                    pass
            else:
                return
        elif payload.channel_id == 523038639282978826:   #Female-Nudes to Lewd Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                try:
                    channel = self.bot.get_channel(id=485007670168911872)
                    if message.attachments[0].url.split(".")[-1] in ['webm','mp4','mov', 'gif']:
                        Yiffs = message.attachments[0].url
                        ext = message.attachments[0].url.split("/")[-1]
                        async with self.session.get(Yiffs) as resp:
                            data = await resp.read()
                        file = discord.File(BytesIO(data),filename=ext, spoiler=True)
                        await channel.send(content="From #🔞female-nudes - Tagged by {}".format(author.name),file=file)
                        await message.remove_reaction('📌', author)
                        return
                except:
                    pass
                try:
                    channel = self.bot.get_channel(id=485007585267941376)
                    if message.attachments:
                        Nudes = message.attachments[0].url
                        ext = message.attachments[0].url.split("/")[-1]
                        async with self.session.get(Nudes) as resp:
                            data = await resp.read()
                        file = discord.File(BytesIO(data),filename=ext, spoiler=True)
                        await channel.send(content="From #🔞female-nudes - Tagged by {}".format(author.name),file=file)
                        await message.remove_reaction('📌', author)
                        return
                except:
                    pass
            else:
                return
        elif payload.channel_id == 482082349673086986:   #Fur-Memes to General Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    if not 'http' in message.content:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        channel = self.bot.get_channel(id=482065536461701130)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
        elif payload.channel_id == 650931904320634880:   #Fursuits to General Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    if not 'http' in message.content:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        channel = self.bot.get_channel(id=482065536461701130)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
        elif payload.channel_id == 541412335517040670:   #Artist-Memes to Artist Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    channel = self.bot.get_channel(id=485007484436611072)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    if not 'http' in message.content:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        channel = self.bot.get_channel(id=485007484436611072)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    channel = self.bot.get_channel(id=485007484436611072)
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
        elif payload.channel_id == 482082265032163328:   #Memes to General Chat
            if str(payload.emoji) == '📌':
                message = await channel.fetch_message(payload.message_id)
                embed = discord.Embed(color=0x0099ff, timestamp=message.created_at)
                embed.set_author(name='{}'.format(author.name), icon_url=avatar)
                embed.set_footer(text=footer)
                if message.attachments:
                    attachment = message.attachments[0].url
                    embed.set_image(url=attachment)
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(embed = embed)
                    await message.remove_reaction('📌', author)
                elif discord.Embed:
                    if not 'http' in message.content:
                        attachment = message.embeds[0].image.url
                        embed.set_image(url=attachment)
                        channel = self.bot.get_channel(id=482065536461701130)
                        await channel.send(embed = embed)
                        await message.remove_reaction('📌', author)
                elif 'http' in message.content:
                    channel = self.bot.get_channel(id=482065536461701130)
                    await channel.send(content="From #{} - Tagged by {}".format(channel,author.name))
                    await channel.send(message.content)
                    await message.remove_reaction('📌', author)
                else:
                    return
    @commands.command(name='Iris', aliases=['iris'])
    async def _iris(self, ctx):
        """
        Randomly fetches Iris Quotes.
        """
        #if not ctx.channel.is_nsfw():
            #return
        imgList = os.listdir(str(cog_data_path(self)) + "/iris_quotes") # Creates a list of filenames from your folder
        imgString = random.choice(imgList) # Selects a random element from the list
        path = str(cog_data_path(self)) + "/iris_quotes/" + imgString # Creates a string for the path to the file
        await ctx.message.channel.send(file=discord.File(path))

    @commands.command(name='shrug')
    async def _shrug(self, ctx, user : discord.Member = None):
        """
        [Meme] Superimposes your pfp onto the shrug meme.
        """
        if user is None:
            user = ctx.author #ctx.bot.get_user(ctx.author.id).display_avatar
        img1 = Image.open(str(cog_data_path(self)) + "/shrug.png")
        #img1 = Image.open(fp=open("/home/teemo/.local/share/Red-DiscordBot/data/cuterecon/cogs/CogManager/cogs/yiffertools/shrug.png", "rb"))
        async with aiohttp.ClientSession() as session:
            #await ctx.channel.send(user.avatar_url_as(format="png"))
            #avatar = await session.get(str(user.display_avatar.replace(format="png").url))
            data = await user.display_avatar.replace(format="png").read() #await avatar.read() 
            av_bytes = BytesIO(data)
            avatar = Image.open(av_bytes)
            #await ctx.channel.send(user.display_avatar.replace(format="png").url)

            dest = (150, 71)
            size = avatar.size
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            av.putalpha(mask)

            face_1 = av.resize((78, 78), Image.LANCZOS)
            face_1 = face_1.rotate(15, expand=True)

            img1.paste(face_1, dest, face_1)

            dest = (351, 43)
            size = avatar.size
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            av.putalpha(mask)

            face_2 = av.resize((36, 36), Image.LANCZOS)
            face_2 = face_2.rotate(-4, expand=True)

            img1.paste(face_2, dest, face_2)

            dest = (350, 225)
            size = avatar.size
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            av.putalpha(mask)

            face_3 = av.resize((40, 40), Image.LANCZOS)
            face_3 = face_3.rotate(5, expand=True)

            img1.paste(face_3, dest, face_3)

            processed = BytesIO()
            img1.save(processed, format="PNG")
            processed.seek(0) 
            #await ctx.channel.send(img1)
            return await ctx.channel.send(file=discord.File(processed, filename="shrugged.png"))