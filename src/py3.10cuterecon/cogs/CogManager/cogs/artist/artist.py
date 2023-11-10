import discord
import logging
import inspect
import random
import asyncio
import string
from collections import namedtuple
from discord.ext import commands
from discord.utils import get
from redbot.core.utils.chat_formatting import warning, error, info
from discord import Embed
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
import re

from .paypal import Paypal

__author__ = "Teemo the Yiffer"

class Artist(commands.Cog, Paypal):
    """
    Artist database
    """
    def __init__(self, bot):
        self.bot = bot
        self.artist = Config.get_conf(self, identifier=5217205587303, force_registration=True)
        default_global = {
            "Artist_ID": {
                "Teemo_Commissionee": None,
                "Name": None,
                "Paypal_clientid": None, 
                "Paypal_secret": None, 
                "Paypal_email": None,
                "Stripe_api_key": None, 
                "Name_URL": None,
                "Description": None,
                "Commissions": None,
                "Art_Style": None,
                "Maturity": None,
                "Sketch_Bust": None,
                "Sketch_Half_Body": None,
                "Sketch_Full_Body": None,
                "Line_Bust": None,
                "Line_Half_Body": None,
                "Line_Full_Body": None,
                "Flat_Bust": None,
                "Flat_Half_Body": None,
                "Flat_Full_Body": None,
                "Shaded_Bust": None,
                "Shaded_Half_Body": None,
                "Shaded_Full_Body": None,
                "Image_URL": "http://en.wikifur.com/w/images/7/7f/Furnonimous.JPG",
                "Thumbnail_URL": None,
                "Portfolio": None,
                "Portfolio_URL": None,
                }
        }
        self.artist.register_global(**default_global)

    def regexs(self, s):
        regex = re.sub(r"\s*[^A-Za-z]+\s*", " ", s)
        return regex

    async def artist_embed(self, ctx):
        data = await self.artist.all()
        try:
            user = await self.bot.fetch_user(self.id)
        except:
            await ctx.send("Sorry but that artist is not in the database.")
            return
        self.Portfolio = data[self.id]["Portfolio"]
        self.Teemo_Commissionee = data[self.id]["Teemo_Commissionee"]
        self.Description = data[self.id]['Description']
        self.Portfolio_URL = data[self.id]['Portfolio_URL']
        self.Name = data[self.id]['Name']
        self.Name_URL = data[self.id]['Name_URL']
        self.author_icon = user.avatar_url if user.avatar \
                    else user.default_avatar_url
        if data[self.id]["Thumbnail_URL"] == "":
            self.Thumbnail_URL = user.avatar_url if user.avatar \
                        else user.default_avatar_url
        else:
            self.Thumbnail_URL = data[self.id]["Thumbnail_URL"]
        if data[self.id]["Image_URL"] == "":
            self.Image_URL = user.avatar_url if user.avatar \
                        else user.default_avatar_url
        else:
            self.Image_URL = data[self.id]["Image_URL"]
        self.Commissions = data[self.id]["Commissions"]
        self.Art_Style = data[self.id]["Art_Style"]
        self.Maturity = data[self.id]["Maturity"]
        self.Sketch_Bust = data[self.id]["Sketch_Bust"]
        self.Sketch_HalfBody = data[self.id]["Sketch_Half_Body"]
        self.Sketch_FullBody = data[self.id]["Sketch_Full_Body"]
        self.Line_Bust = data[self.id]["Line_Bust"]
        self.Line_HalfBody = data[self.id]["Line_Half_Body"]
        self.Line_FullBody = data[self.id]["Line_Full_Body"]
        self.Flat_Bust = data[self.id]["Flat_Bust"]
        self.Flat_HalfBody = data[self.id]["Flat_Half_Body"]
        self.Flat_FullBody = data[self.id]["Flat_Full_Body"]
        self.Shaded_Bust = data[self.id]["Shaded_Bust"]
        self.Shaded_HalfBody = data[self.id]["Shaded_Half_Body"]
        self.Shaded_FullBody = data[self.id]["Shaded_Full_Body"]

        embed = discord.Embed(
            title=self.Portfolio, description=self.Description, url=self.Portfolio_URL, color=0xff0000)
        embed.set_author(name=self.Name, url=self.Name_URL,
                         icon_url=self.author_icon)
        embed.set_thumbnail(url=self.Thumbnail_URL)
        embed.set_image(url=self.Image_URL)
        embed.add_field(name="Commissions", value=self.Commissions, inline=False)
        embed.add_field(name="Art Style", value=self.Art_Style, inline=True)
        embed.add_field(name="Maturity", value=self.Maturity, inline=True)
        if len(self.Sketch_FullBody) != 0:
            embed.add_field(name="Sketch", value='Bust: ' + self.Sketch_Bust + '''
                                                    Half Body: ''' + self.Sketch_HalfBody + '''
                                                    Full Body: ''' + self.Sketch_FullBody
                                                , inline=True)
        if len(self.Line_FullBody) != 0:
            embed.add_field(name="Line", value='Bust: ' + self.Line_Bust + '''
                                                    Half Body: ''' + self.Line_HalfBody + '''
                                                    Full Body: ''' + self.Line_FullBody
                                                , inline=True)
        if len(self.Flat_FullBody) != 0:
            embed.add_field(name="Flat", value='Bust: ' + self.Flat_Bust + '''
                                                    Half Body: ''' + self.Flat_HalfBody + '''
                                                    Full Body: ''' + self.Flat_FullBody
                                                , inline=True)
        if len(self.Shaded_FullBody) != 0:
            embed.add_field(name="Shaded", value='Bust: ' + self.Shaded_Bust + '''
                                                    Half Body: ''' + self.Shaded_HalfBody + '''
                                                    Full Body: ''' + self.Shaded_FullBody
                                                , inline=True)
        try:
            if self.Teemo_Commissionee == "Yes": 
                embed.add_field(name='Teemo the Yiffer Commissionee',
                            value=':white_check_mark:', inline=True)
        except:
            pass
        self.embed = await ctx.send(embed=embed)

    async def report(self, ctx):
        me = await self.bot.fetch_user('105188343750340608')
        guild = ctx.message.channel.guild
        sname = ctx.message.guild.name
        cname = ctx.message.channel.name
        author = ctx.message.author
        avatar = author.avatar_url if author.avatar \
            else author.default_avatar_url
        footer = 'Submitted in {} - #{}'.format(sname, cname)
        embed = discord.Embed(title='[Incoming Report]',
                              color=0xff0000,
                              timestamp=ctx.message.created_at)
        embed.set_footer(text=footer, icon_url=guild.icon_url)
        embed.set_author(name='{}'.format(author.name), icon_url=avatar)
        embed.add_field(name="Discord Username:",
                        value=ctx.message.author, inline=True)
        try:
            NameOnFile = await self.artist.get_raw(Artist_ID.content,"Name")
            embed.add_field(name="Name on File:",
                        value=NameOnFile, inline=True)
        except:
            pass
        embed.add_field(name="Reason:", value=self.Reason, inline=True)
        await me.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        # check whether the message was sent in a guild
        if message.guild is None:
            if message.content == "!commission_close":
                guild = self.bot.get_guild(481709526291054611)
                commission_role = guild.get_role(825536475633942528)
                member = guild.get_member(message.author.id)
                await member.remove_roles(commission_role)
                await message.channel.send(f"Roger that, {message.author.mention}! I have removed your `Commissions Open!` role to signify you've closed them. DM me `!commission_open` to re-add the role.")
                return
            elif message.content == "!commission_open":
                guild = self.bot.get_guild(481709526291054611)
                commission_role = guild.get_role(825536475633942528)
                member = guild.get_member(message.author.id)
                await member.add_roles(commission_role)
                await message.channel.send("Awesome! I've assigned you the role! If you close your commissions, DM me `!commissions_close`")
                return
            else:
                return
        # check whether the message author isn't a bot
        if message.author.bot:
            return
        # check whether the cog isn't disabled
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            print("Cog disabled.")
            return
        # check whether the channel isn't on the ignore list 
        if not await self.bot.ignored_channel_or_guild(message):
            print("Channel on ignore list.")
            return
        # check whether the message author isn't on allowlist/blocklist
        if not await self.bot.allowed_by_whitelist_blacklist(message.author):
            print("Author on block list.")
            return
        if message.channel.id in {485007168077037568, 501218094837137448, 511054890261413888}:
            if any(role for role in message.author.roles if role.id == 481721136225320961):
                if not any(role for role in message.author.roles if role.id == 825536475633942528):
                    listening = False
                    if re.findall(r"(?i)(commission)", message.content) or re.findall(r"(?i)(open)", message.content) or re.findall(r"(?i)(ych)", message.content):
                        listening = True
                    if message.embeds:
                        for embed in message.embeds:
                            embed = embed.to_dict()
                            if "commission" or "open" or "ych" in embed["description"].lower(): 
                                listening = True
                                break
                            elif "commission" or "open" or "ych" in embed["title"].lower(): 
                                listening = True
                                break
                                #await message.channel.send(embed["description"])
                    if listening:
                        ctx = message.channel
                        author = message.author
                        commission_question = await ctx.send(f"Hello, {author.mention}! Do you happen to have your commissions open? If so, please react to the ✅! If no, please react to the ❎.")
                        await commission_question.add_reaction('✅')
                        await commission_question.add_reaction('❎')
                        while listening:
                            react = lambda react, user: user == author and\
                                                    react.emoji in ['✅', '❎'] and\
                                                    react.message.id == commission_question.id
                            react, user = await self.bot.wait_for('reaction_add', check=react)
                            emoji = react.emoji
                            if emoji == '✅':
                                await commission_question.delete()
                                response = await ctx.send("Perfect! I've added your open commission message to my database and is accessible to users via `!commission_open` command.")
                                ping_question = await ctx.send("Would you like a 'commissions open' role that would allow potiential customers to ping you?")
                                #self.id = str(ctx.message.author.id)
                                await ping_question.add_reaction('✅')
                                await ping_question.add_reaction('❎')
                                react2 = lambda react, user: user == author and\
                                                    react.emoji in ['✅', '❎'] and\
                                                    react.message.id == ping_question.id
                                react2, user = await self.bot.wait_for('reaction_add', check=react2)
                                emoji2 = react2.emoji
                                if emoji2 == '✅':
                                    await ping_question.delete()
                                    await response.delete()
                                    commission_role = message.guild.get_role(825536475633942528)
                                    await author.add_roles(commission_role)
                                    accept_response = await ctx.send("Awesome! I've assigned you the role! If you close your commissions, DM me `!commission_close`")
                                    await asyncio.sleep(30)
                                    await accept_response.delete()
                                    listening = False
                                    return
                                elif emoji2 == '❎':
                                    listening = False
                                    await ping_question.delete()
                                    await response.delete()
                                    decline_response = await ctx.send("Okie! No role for customer inquiry pings!")
                                    await asyncio.sleep(30)
                                    await decline_response.delete()
                                    return
                                else:
                                    listening = False
                                    await ping_question.delete()
                                    await response.delete()
                                    await asyncio.sleep(120)
                                    await ping_question.delete()
                                    return
                            elif emoji == '❎':
                                listening = False
                                await commission_question.delete()
                                decline_response = await ctx.send("Opps, silly me! I made a mistake! carry on being beautiful~")
                                await asyncio.sleep(15)
                                await decline_response.delete()
                                return
                            else:
                                listening = False
                                await asyncio.sleep(120)
                                await commission_question.delete()
                                return

    @commands.command(name="commission")
    async def _commission(self, ctx, *, artist):
        """
        Request to Commission an Artist.
        """
        a = await self.artist.all()
        try:
            artistid = next(k for k, v in a.items() if ("Name", artist) in v.items())
        except StopIteration:
            await ctx.send("Sorry but that artist is not in the database or the name was incorrect. Check the artist list by running: >artists")
            return
        artistnick = await self.bot.fetch_user(artistid)
        if a[artistid]['Commissions'] in {'open', 'Open', 'Opened', 'opened'}:
            try:
                guild = ctx.message.channel.guild
                sname = ctx.message.guild.name
                cname = ctx.message.channel.name
                footer = 'Submitted in {} - #{}'.format(sname, cname)
                #embed1.set_footer(text=footer, icon_url=guild.icon_url)
            except:
                pass
            author = ctx.message.author
            avatar = author.avatar_url if author.avatar \
                else author.default_avatar_url
            embed1 = discord.Embed(title='[Potential Customer] Review Commissioner Information Below',
                                   description="React ✅ to Approve, ❎ to Decline, 💼 to decline & close your commissions.",
                                   color=0xff0000,
                                   timestamp=ctx.message.created_at)
            embed1.set_author(name='{}'.format(author.name), icon_url=avatar)
            await ctx.send("Excellent choice! I'm going to ask you several questions regarding your commission inquiry. Be sure to give a response to each question! You'll have 10 minutes to answer each question.")
            await asyncio.sleep(2)
            await ctx.send("Do you have a budget range? This is optional but it helps the artist guage what they can or cannot do for you. (Example: $5 - $25)")
            Budget = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            await ctx.send("How many characters are you requesting to be drawn?")
            usermsg = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg:
                Numbers = usermsg
            elif usermsg is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Is the maturity rating SFW, NSFW, or Either SFW/NSFW?")
            usermsg1 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg1:
                Maturity = usermsg1
            elif usermsg1 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("What art complexity do you seek: Sketch, Lineart, Flat, or Cell Shadded?")
            usermsg2 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg2:
                ArtComplexity = usermsg2
            elif usermsg2 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("What about the size: Bust, Half-body, or Full-body?")
            usermsg3 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg3:
                Size = usermsg3
            elif usermsg3 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Did you want it colored?")
            usermsg4 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg4:
                Color = usermsg4
            elif usermsg4 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Did you have a specific art style in mind? (Examples: Toon, Chibi, Nekomono, Anthro, etc.)")
            usermsg6 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg6:
                ArtStyle = usermsg6
            elif usermsg6 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Did you want a simplictic, complex, or no background?")
            usermsg7 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg7:
                Background = usermsg7
            elif usermsg7 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Please type out a description on what the fursona(s) will be doing, dressed, acting, etc. I'll give you 20 minutes to answer this question so take your time!")
            usermsg8 = await self.bot.wait_for('message', timeout=1200, check=lambda message: message.author == ctx.author)
            if usermsg8:
                Description = usermsg8
            elif usermsg8 is None:
                await ctx.send("Sorry but I didn't get any response from you so I've cancelled the request. '>commission' to re-attempt.")
                return
            await ctx.send("Do you have a reference sheet or picture?")
            try:
                if await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author):
                    global RefImage
                    embed1.set_image(url=RefImage)
            except:
                pass
            await ctx.send("Lastly, do you have a link to multiple references? (Examples: Dropbox, FA, Google Drive, etc.) [Your link will be deleted after posted for privacy]")
            usermsg9 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
            if usermsg9:
                ReferenceLink = usermsg9
            await ctx.send("Sent! Your artist will gest a notification with the information you provided and you should recieve a response soon!")
            await asyncio.sleep(4)
            try: 
                await usermsg9.delete()
            except:
                pass
            embed1.add_field(name="Discord Username:",
                             value=ctx.author, inline=True)
            embed1.add_field(name="Budget:", value=Budget.content, inline=True)
            embed1.add_field(name="Number of Characters:",
                             value=Numbers.content, inline=True)
            embed1.add_field(name="Maturity:",
                             value=Maturity.content, inline=True)
            embed1.add_field(name="Art Complexity:",
                             value=ArtComplexity.content, inline=True)
            embed1.add_field(name="Size:", value=Size.content, inline=True)
            embed1.add_field(name="Colored:", value=Color.content, inline=True)
            embed1.add_field(name="Art Style:",
                             value=ArtStyle.content, inline=True)
            embed1.add_field(name="Background:",
                             value=Background.content, inline=True)
            embed1.add_field(name="Description of Request:",
                             value=Description.content, inline=True)
            embed1.add_field(name="References (URL):",
                             value=ReferenceLink.content, inline=False)
            botmsg2 = await artistnick.send(embed=embed1)
            await botmsg2.add_reaction('✅')
            await botmsg2.add_reaction('❎')
            await botmsg2.add_reaction('💼')

            listening = True
            while listening:
                react = lambda react, user: user == artistnick and\
                                        react.emoji in ['✅', '❎', '💼'] and\
                                        react.message.id == botmsg2.id
                react, user = await self.bot.wait_for('reaction_add', check=react)
                emoji = react.emoji
                PaypalEmail = await self.artist.get_raw(artistid, "Paypal_email") 
                if emoji == '✅':
                    if PaypalEmail == "":
                        await artistnick.send("What is your PayPal e-mail? Type 'N/A' if you don't use Paypal")
                        PayPal_Email = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == artistnick)
                        await self.artist.set_raw(artistid,"Paypal_email", value=PayPal_Email.content)
                    await artistnick.send("What are your net terms? Net terms is the amount of days given to customer for payment. I recommend between 1 to 5 days.")
                    NetTerms = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == artistnick)
                    if NetTerms is None:
                        await artistnick.send("Sorry but I didn't get any response from you so I'll set the net terms to 5 days.")
                        NetTerms = "5 Days"
                    await artistnick.send("Please post any comments, a queue number, or Terms of Services you'd like the customer to know.")
                    Comments = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == artistnick)
                    if Comments is None:
                        Comments = "[None]"
                    await artistnick.send("Sent! I've notified the customer.")
                    author = artistnick
                    avatar = author.avatar_url if author.avatar \
                        else author.default_avatar_url
                    embed1 = discord.Embed(title='✅ Commission Approved!',
                                        description="Review and proceed to pay via PayPal with the e-mail below.",
                                        color=0xff0000,
                                        timestamp=ctx.message.created_at)
                    embed1.set_author(name='{}'.format(author.name), icon_url=avatar)
                    embed1.add_field(name="PayPal E-mail:",
                            value=PaypalEmail, inline=True)
                    embed1.add_field(name="Payment Due (Days):", value=NetTerms.content, inline=True)
                    embed1.add_field(name="Comments:",
                                    value=Comments.content, inline=False)
                    await ctx.message.author.send(embed=embed1)
                    await ctx.message.author.send("Please contact %s on Discord for any extra questions you may have." % artistnick)
                elif emoji == '❎':
                    await artistnick.send("Rejected! I'll let the customer know. Did you want to provide an explanation? Its optional, but feel free to enter a reason below.")
                    try:
                        RejectionReason = await self.bot.wait_for('message', timeout=120, check=lambda message: message.author == artistnick)
                    except:
                        pass
                    await ctx.message.author.send("Sorry but your commission request has been rejected. The artist may of provided an explanation below.")
                    await ctx.message.author.send(RejectionReason.content)
                    await artistnick.send("Sent!")
                elif emoji == '💼':
                    await artistnick.send("Rejected & Closing Commissions! I'll let the customer know. Did you want to provide an explanation? Its optional, but feel free to enter a reason below.")
                    RejectionReason1 = await self.bot.wait_for('message', timeout=120, check=lambda message: message.author == artistnick)
                    await ctx.message.author.send("Sorry but your commission request has been rejected as the artist has recently closed their commissions. The artist may of provided an explanation below.")
                    try:
                        await ctx.message.author.send(RejectionReason1.content)
                    except:
                        pass
                    if 'value' in self.artist[artistid]['embed']['fields'][0]:
                        self.artist[artistid]['embed']['fields'][0]['value'] = 'Closed'
                    await artistnick.send("Sent! I've also closed your commissions so you won't recieve notices until you re-open them via '>artist modify'")
            else:
                await ctx.send("Incorrect format, cancelling action.")
                return
        else:
            await ctx.send("Sorry! The artist closed their commissions.")
            return

    @commands.group(name="artist")
    async def _artist(self, ctx):
        """
        Teemo the Yiffer's artist directory.
        """

    @_artist.command(name="info")
    async def _info(self, ctx, *, artist):
        """
        [INFO TEST]
        """
        a = await self.artist.all()
        try:
            artistid = next(k for k, v in a.items() if ("Name", artist) in v.items())
        except StopIteration:
            await ctx.send("Sorry but that artist is not in the database or the name was incorrect. Check the artist list by running: >artists")
            return
        await ctx.send(artistid) 

    @_artist.command(name="test")
    async def cmd(self, ctx):
        embeds = []
        data = await self.artist.all()
        for Artist_ID in data.items():
            self.id = [109163977493204992, 177933233579622401, 476135159150936084]
            user = await self.bot.fetch_user(self.id)
            self.Portfolio = data[self.id]["Portfolio"]
            self.Teemo_Commissionee = data[self.id]["Teemo_Commissionee"]
            self.Description = data[self.id]['Description']
            self.Portfolio_URL = data[self.id]['Portfolio_URL']
            self.Name = data[self.id]['Name']
            self.Name_URL = data[self.id]['Name_URL']
            self.author_icon = user.avatar_url if user.avatar \
                        else user.default_avatar_url
            self.Thumbnail_URL = user.avatar_url if user.avatar \
                        else user.default_avatar_url
            self.Image_URL = data[self.id]["Image_URL"]
            self.Commissions = data[self.id]["Commissions"]
            self.Art_Style = data[self.id]["Art_Style"]
            self.Maturity = data[self.id]["Maturity"]
            self.Sketch_Bust = data[self.id]["Sketch_Bust"]
            self.Sketch_HalfBody = data[self.id]["Sketch_Half_Body"]
            self.Sketch_FullBody = data[self.id]["Sketch_Full_Body"]
            self.Line_Bust = data[self.id]["Line_Bust"]
            self.Line_HalfBody = data[self.id]["Line_Half_Body"]
            self.Line_FullBody = data[self.id]["Line_Full_Body"]
            self.Flat_Bust = data[self.id]["Flat_Bust"]
            self.Flat_HalfBody = data[self.id]["Flat_Half_Body"]
            self.Flat_FullBody = data[self.id]["Flat_Full_Body"]
            self.Shaded_Bust = data[self.id]["Shaded_Bust"]
            self.Shaded_HalfBody = data[self.id]["Shaded_Half_Body"]
            self.Shaded_FullBody = data[self.id]["Shaded_Full_Body"]

            embed = discord.Embed(
                title=self.Portfolio, description=self.Description, url=self.Portfolio_URL, color=0xff0000)
            embed.set_author(name=self.Name, url=self.Name_URL,
                            icon_url=self.author_icon)
            embed.set_thumbnail(url=self.Thumbnail_URL)
            embed.set_image(url=self.Image_URL)
            embed.add_field(name="Commissions", value=self.Commissions, inline=False)
            embed.add_field(name="Art Style", value=self.Art_Style, inline=True)
            embed.add_field(name="Maturity", value=self.Maturity, inline=True)
            if len(self.Sketch_FullBody) != 0:
                embed.add_field(name="Sketch", value='Bust: ' + self.Sketch_Bust + '''
                                                        Half Body: ''' + self.Sketch_HalfBody + '''
                                                        Full Body: ''' + self.Sketch_FullBody
                                                    , inline=True)
            if len(self.Line_FullBody) != 0:
                embed.add_field(name="Line", value='Bust: ' + self.Line_Bust + '''
                                                        Half Body: ''' + self.Line_HalfBody + '''
                                                        Full Body: ''' + self.Line_FullBody
                                                    , inline=True)
            if len(self.Flat_FullBody) != 0:
                embed.add_field(name="Flat", value='Bust: ' + self.Flat_Bust + '''
                                                        Half Body: ''' + self.Flat_HalfBody + '''!
                                                        Full Body: ''' + self.Flat_FullBody
                                                    , inline=True)
            if len(self.Shaded_FullBody) != 0:
                embed.add_field(name="Shaded", value='Bust: ' + self.Shaded_Bust + '''
                                                        Half Body: ''' + self.Shaded_HalfBody + '''
                                                        Full Body: ''' + self.Shaded_FullBody
                                                    , inline=True)
            try:
                if self.Teemo_Commissionee == "Yes": 
                    embed.add_field(name='Teemo the Yiffer Commissionee',
                                value=':white_check_mark:', inline=True)
            except:
                pass
            embeds.append(embed)
        return embeds

    @_artist.command(name="create")
    @commands.has_any_role("Artist","Admin","Moderator","Owner")
    async def _create(self, ctx):
        """
        Creates an empty artist embed.
        """
        try:
            await ctx.send(f"What is the User ID of the artist? If you're the artist, copy & paste your ID: {ctx.message.author.id}")
            Artist_ID = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("What is the name of the artist?")
            ArtistName = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("Write a sentence or two introducing the artist (Example: 'Just a happy go-lucky raccoon who loves to draw!')")
            Description = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("Are their commissions opened or closed?")
            Commissions = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("What is the art style?")
            ArtStyle = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("What is the maturity of the art (NSFW or SFW)?")
            Maturity = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await ctx.send("What is the artist's PayPal e-mail? Type 'N/A' for Not Available.")
            ArtistPayPal = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if ArtistPayPal.content == "N/A":
                ArtistPayPal = ''
            await ctx.send("What is the artist's social media URL? Type 'N/A' for Not Available.")
            NameURL = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if NameURL.content == "N/A":
                NameURL = "https://twitter.com/"
            await ctx.send("What is the artist's best & favorite drawing's URL? Type 'N/A' for Not Available.")
            ImageURL = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if ImageURL.attachments:
                ImageURL = ImageURL.attachments[0].url
            if ImageURL.content == "N/A":
                ImageURL = "http://en.wikifur.com/w/images/7/7f/Furnonimous.JPG"
            await ctx.send("What is the artist's thumbnail URL? Type 'N/A' for Not Available. It will default to the artist's Discord profile picture.")
            ThumbnailURL = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if ThumbnailURL.attachments:
                ThumbnailURL = ThumbnailURL.attachments[0].url
            if ThumbnailURL.content == "N/A":
                ThumbnailURL = ''
            await ctx.send("Where is the artist's portfolio located (Recommend: e621, e926, FA, & DA)? Type 'N/A' for Not Available.")
            Portfolio = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if Portfolio.content == "N/A":
                Portfolio = ''
            else:
                await ctx.send(f"What is the artist's {Portfolio.content} URL?")
                PortfolioURL = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await self.artist.set_raw(Artist_ID.content,"Teemo_Commissionee", value='')
            await self.artist.set_raw(Artist_ID.content,"Name", value=ArtistName.content)
            await self.artist.set_raw(Artist_ID.content,"Paypal_clientid", value='') 
            await self.artist.set_raw(Artist_ID.content,"Paypal_secret", value='')
            try:
                await self.artist.set_raw(Artist_ID.content,"Paypal_email", value=ArtistPayPal)
            except:
                await self.artist.set_raw(Artist_ID.content,"Paypal_email", value=ArtistPayPal.content)
            await self.artist.set_raw(Artist_ID.content,"Stripe_api_key", value='')
            try:
                await self.artist.set_raw(Artist_ID.content,"Name_URL", value=NameURL)
            except:
                await self.artist.set_raw(Artist_ID.content,"Name_URL", value=NameURL.content)
            await self.artist.set_raw(Artist_ID.content,'Description', value=Description.content)
            await self.artist.set_raw(Artist_ID.content,"Commissions", value=Commissions.content)
            await self.artist.set_raw(Artist_ID.content,"Art_Style", value=ArtStyle.content)
            await self.artist.set_raw(Artist_ID.content,"Maturity", value=Maturity.content)
            await self.artist.set_raw(Artist_ID.content,"Sketch_Bust", value='')
            await self.artist.set_raw(Artist_ID.content,"Sketch_Half_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Sketch_Full_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Line_Bust", value='')
            await self.artist.set_raw(Artist_ID.content,"Line_Half_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Line_Full_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Flat_Bust", value='')
            await self.artist.set_raw(Artist_ID.content,"Flat_Half_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Flat_Full_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Shaded_Bust", value='')
            await self.artist.set_raw(Artist_ID.content,"Shaded_Half_Body", value='')
            await self.artist.set_raw(Artist_ID.content,"Shaded_Full_Body", value='')
            try:
                await self.artist.set_raw(Artist_ID.content,"Image_URL", value=ImageURL)
            except:
                await self.artist.set_raw(Artist_ID.content,"Image_URL", value=ImageURL.content)
            try:
                await self.artist.set_raw(Artist_ID.content,"Thumbnail_URL", value=ThumbnailURL)
            except:
                await self.artist.set_raw(Artist_ID.content,"Thumbnail_URL", value=ThumbnailURL.content)
            try:
                await self.artist.set_raw(Artist_ID.content,"Portfolio", value=Portfolio)
            except:
                await self.artist.set_raw(Artist_ID.content,"Portfolio", value=Portfolio.content)
            try:
                await self.artist.set_raw(Artist_ID.content,'Portfolio_URL', value=PortfolioURL.content)
            except:
                await self.artist.set_raw(Artist_ID.content,'Portfolio_URL', value="")
            await ctx.send(f"Embed was created and saved for {ArtistName.content}")
            self.Reason = "New artist has been added to db. Update the bot."
            await self.report(ctx)
        except:
            await ctx.send("On no! Something went wrong with the database update. I've notified Teemo the Yiffer#0001 to update the datebase with your new name.")
            self.Reason = "Artist embed creation failure."
            await self.report(ctx)
            return
        await ctx.send("Although the database has been updated, the '!artist' cmd block needs to be updated as well.")
        await ctx.send("I've notified Teemo the Yiffer#0001 to update it.")
        await ctx.send("The artist can run '!artist modify' to change anything and preview their embed right now!")

    @_artist.command(name="modify")
    async def _modify(self, ctx):
        """
        Modifying artist's embed.
        """
        try:
            await self.artist.get_raw(ctx.message.author.id)
        except StopIteration:
            await ctx.send("You're not in the database. If you're interested in being added, type '>contact' to notify Teemo the Yiffer.", delete_after=120)
            return
        embed1 = discord.Embed(title='Arist Embed Modification',
                                description="React to what you would like to modify.", color=0xff0000)
        embed1.add_field(name="Social Media (URL):", value="📇", inline=True)
        embed1.add_field(name="Portfolio:", value="💼", inline=True)
        embed1.add_field(name="Commissions:", value="🤑", inline=True)
        embed1.add_field(name="Art Style:", value="🤓", inline=True)
        embed1.add_field(name="Maturity:", value="😏", inline=True)
        embed1.add_field(name="Descrption:", value="💬", inline=True)
        embed1.add_field(name="Thumbnail (URL):", value="📷", inline=True)
        embed1.add_field(name="Large Picture (URL):", value="😻", inline=True)
        embed1.add_field(name="[Preview Embed]", value="💻", inline=True)
        embed1.add_field(name="[Exit]", value="❌", inline=False)
        botmsg = await ctx.send(embed=embed1)
        await botmsg.add_reaction('📇')
        await botmsg.add_reaction('💼')
        await botmsg.add_reaction('🤑')
        await botmsg.add_reaction('🤓')
        await botmsg.add_reaction('😏')
        await botmsg.add_reaction('💬')
        await botmsg.add_reaction('😍')
        await botmsg.add_reaction('😻')
        await botmsg.add_reaction('📷')
        await botmsg.add_reaction('💻')
        await botmsg.add_reaction('❌')

        listening = True
        while listening:
            react = lambda react, user: user == ctx.message.author and\
                                    react.emoji in ['📇', '💼', '🤑', '🤓', '😏', '💬', '😻', '📷', '💻', '❌'] and\
                                    react.message.id == botmsg.id
            react, user = await self.bot.wait_for('reaction_add', check=react)
            emoji = react.emoji
            if emoji == '🤑':
                await ctx.send("Are your commissions open or closed?")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Commissions", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '📇':
                await ctx.send("What's your social media URL so people can follow you?")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Name_URL", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '💼':
                await ctx.send("Where is your portfolio located? (Recommend: e621, e926, FA, & DA)")
                response1 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Portfolio", value=response1.content)
                await ctx.send("What's the URL to your portfolio?")
                response2 = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Portfolio_URL", value=response2.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '🤓':
                await ctx.send("What's your art style?")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Art_Style", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '😏':
                await ctx.send("Is your art SFW or NSFW?")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Maturity", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '💬':
                await ctx.send("Type in your description.")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                await self.artist.set_raw(ctx.message.author.id,"Description", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '📷':
                await ctx.send("Paste your thumbnail.")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                if response.attachments:
                    await self.artist.set_raw(ctx.message.author.id,"Thumbnail_URL", value=response.attachments[0].url)
                else:
                    await self.artist.set_raw(ctx.message.author.id,"Thumbnail_URL", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '😻':
                await ctx.send("Paste your large picture.")
                response = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
                if response.attachments:
                    await self.artist.set_raw(ctx.message.author.id,"Image_URL", value=response.attachments[0].url)
                else:
                    await self.artist.set_raw(ctx.message.author.id,"Image_URL", value=response.content)
                await ctx.send("Done!", delete_after=5)
            elif emoji == '💻':
                self.id = str(ctx.message.author.id)
                await self.artist_embed(ctx)
                await self.embed.add_reaction('❌')
                react = lambda react, user: user == ctx.message.author and\
                                    react.emoji in ['❌'] and\
                                    react.message.id == self.embed.id
                msg = await ctx.send("Here's your embed! React ❌ to hide the preview.")
                react, user = await self.bot.wait_for('reaction_add', check=react)
                emoji = react.emoji
                if emoji == '❌':
                    await self.embed.delete()
                    await msg.delete()
            elif emoji == '❌':
                listening = False
                await botmsg.delete()
                return
            else:
                await asyncio.sleep(60)
                await msg.delete()
                await self.bot.delete_message(self.embed)
                return

    @_artist.command(name='Recon Scout Teemo', aliases=['Recon'])
    async def _ReconScoutTeemo(self, embed):
        """
        Yordle Specialist 
        """
        self.id = '109163977493204992'
        await self.artist_embed(embed)

    @_artist.command(name='Kansyr')
    async def _Kansyr(self, embed):
        """
        Anthro Artist
        """
        self.id = '177933233579622401'
        await self.artist_embed(embed)

    @_artist.command(name='Wild-Glitch')
    async def _WildGlitch(self, embed):
        """
        Anthro Artist 
        """
        self.id = '476135159150936084'
        await self.artist_embed(embed)

    @_artist.command(name='JimJim')
    async def _JimJim(self, embed):
        """
        Anthro Artist
        """
        self.id = '359107881171288075'
        await self.artist_embed(embed)

    @_artist.command(name='Sean')
    async def _Sean(self, embed):
        """
        Furry Artist
        """
        self.id = '122198950815072259'
        await self.artist_embed(embed)

    @_artist.command(name='Ange')
    async def _Ange(self, embed):
        """
       Furry & Human Artist
        """
        self.id = '208295565132300288'
        await self.artist_embed(embed)

    @_artist.command(name='chocolateknife')
    async def _chocolateknife(self, embed):
        """
       Furry & Human Artist
        """
        self.id = '227861277962272768'
        await self.artist_embed(embed)

    @_artist.command(name='Satan')
    async def _Satan(self, embed):
        """
       Furry & Human Artist
        """
        self.id = '428191562271555584'
        await self.artist_embed(embed)

    @_artist.command(name='Nekowuwu')
    async def _Nekowuwu(self, embed):
        """
        Kemono Specialist
        """
        self.id = '313412586668294144'
        await self.artist_embed(embed)

    @_artist.command(name='Starlight')
    async def _Starlight(self, embed):
        """
        Furry & Human Artist
        """
        self.id = '177922602801692673'
        await self.artist_embed(embed)

    @_artist.command(name='Nozabii')
    async def _Nozabii(self, embed):
        """
        Furry Artist
        """
        self.id = '484173387631951874'
        await self.artist_embed(embed)

    @_artist.command(name='Zanator')
    async def _Zanator(self, embed):
        """
        Anthro Artist
        """
        self.id = '82276748154109952'
        await self.artist_embed(embed)

    @_artist.command(name='Shougai')
    async def _Shougai(self, embed):
        """
        Cute-Chibi Specialist
        """
        self.id = '237336184211111938'
        await self.artist_embed(embed)

    @_artist.command(name='Lancey Lance McClain', aliases=['Lancey'])
    async def _LanceyLanceMcClain(self, embed):
        """
        Anthro Artist 
        """
        self.id = '348485508449435648'
        await self.artist_embed(embed)

    @_artist.command(name='Miiru-Inu')
    async def _MiiruInu(self, embed):
        """
        Furry Artist
        """
        self.id = '305500401938071552'
        await self.artist_embed(embed)
        
    @_artist.command(name="Teemo the Yiffer",  aliases=['Teemo'])
    async def _TeemotheYiffer(self, embed):
        """
        [TEST] Teemo the Yiffer's Embed
        """
        self.id = '105188343750340608'
        await self.artist_embed(embed)

    @_artist.command(name="Riches")
    async def _Riches(self, embed):
        """
        Furry Artist
        """
        self.id = '201275359121899520'
        await self.artist_embed(embed)

    @_artist.command(name="o0Riley0o")
    async def _o0Riley0o(self, embed):
        """
        Furry Artist
        """
        self.id = '164558273763082240'
        await self.artist_embed(embed)

    @_artist.command(name="lynstigo")
    async def _lynstigo(self, embed):
        """
        Furry Artist
        """
        self.id = '183659634106564610'
        await self.artist_embed(embed)

    @_artist.command(name="Pavlov")
    async def _Pavlov(self, ctx):
        """
        Furry Artist
        """
        self.id = '258044579591225345'
        await self.artist_embed(ctx)

    @_artist.command(name="Doritomon")
    async def _Doritomon(self, embed):
        """
        Furry Artist
        """
        self.id = '510305021020340233'
        await self.artist_embed(embed)

    @_artist.command(name="YaBoiDante")
    async def _YaBoiDante(self, embed):
        """
        Furry/Human Artist
        """
        self.id = '231785012465238017'
        await self.artist_embed(embed)

    @_artist.command(name="Roten")
    async def _Roten(self, embed):
        """
        Anthro/Feral Artist
        """
        self.id = '197799322035814400'
        await self.artist_embed(embed)

    @_artist.command(name="SpudShark")
    async def _SpudShark(self, embed):
        """
        Anthro Artist
        """
        self.id = '245189340530081803'
        await self.artist_embed(embed)

    @_artist.command(name="Mox")
    async def _Mox(self, embed):
        """
        Anthro Artist
        """
        self.id = '249903626846208000'
        await self.artist_embed(embed)

    @_artist.command(name="DevVoxy")
    async def _DevVoxy(self, embed):
        """
        Anthro Artist
        """
        self.id = '181035485936746497'
        await self.artist_embed(embed)

    @_artist.command(name="Kiska")
    async def _Kiska(self, embed):
        """
        Anthro Artist
        """
        self.id = '431210855632470020'
        await self.artist_embed(embed)

    @_artist.command(name="Tea")
    async def _Tea(self, embed):
        """
        Anthro Artist
        """
        self.id = '155568680053243904'
        await self.artist_embed(embed)

    @_artist.command(name="Genonair")
    async def _Genonair(self, embed):
        """
        Anthro Artist
        """
        self.id = '481974409280749568'
        await self.artist_embed(embed)

    @_artist.command(name="KasuSei")
    async def _KasuSei(self, embed):
        """
        Anthro Artist
        """
        self.id = '263101378027716617'
        await self.artist_embed(embed)

    @_artist.command(name="Boxy")
    async def _Boxy(self, embed):
        """
        Chibi/Animal Crossing-esque
        """
        self.id = '265844740002545664'
        await self.artist_embed(embed)

    @_artist.command(name="Gen")
    async def _Gen(self, embed):
        """
        Pokemon Artist
        """
        self.id = '481974409280749568'
        await self.artist_embed(embed)

    @_artist.command(name="Blackjack")
    async def _Blackjack(self, embed):
        """
        Furry Artist / Mouse Specialist
        """
        self.id = '142169778172329984'
        await self.artist_embed(embed)

    @_artist.command(name="Shirokoi")
    async def Shirokoi(self, embed):
        """
        Furry Artist / VN Developer
        """
        self.id = '212048188775989250'
        await self.artist_embed(embed)

    @_artist.command(name="Moonway")
    async def Moonway(self, embed):
        """
        Furry Artist
        """
        self.id = '78864838431875072'
        await self.artist_embed(embed)

    @_artist.command(name="the Gentle Giant", aliases=['the'])
    async def theGentleGiant(self, embed):
        """
        Furry Artist
        """
        self.id = '204953173281079296'
        await self.artist_embed(embed)

    @_artist.command(name="GalaxyDJx")
    async def GalaxyDJx(self, embed):
        """
        Furry Artist
        """
        self.id = '311283024312532993'
        await self.artist_embed(embed)

    @_artist.command(name="Catnip")
    async def GalaxyDJx(self, embed):
        """
        Furry Artist
        """
        self.id = '282502388240089089'
        await self.artist_embed(embed)