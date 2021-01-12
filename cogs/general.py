import discord
from discord.ext import commands
from googleapiclient.discovery import build
import datetime
import asyncio
import aiohttp
import requests, json
import praw
import random
import re
from bot import main_color, main_emoji
from bot import tick, cross, invite_url
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
from io import BytesIO
from typing import *

config1 = open('config.json', 'r')
config = json.load(config1)

class TextChannelConvert(commands.TextChannelConverter):
    async def convert(self, ctx, argument):
        channel = await super().convert(ctx, argument)
        return channel

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        self.argument = argument
        args = self.argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time

api_key = config['RANDOM_API_KEY']
base_url = "http://api.openweathermap.org/data/2.5/weather?"
YT_Key = config['YOUTUBE_API_KEY']
giphy_api_key = config['GIPHY_API_KEY']

class general(commands.Cog):
    """"General commands which are accessible to all members of the server!"""

    def __init__(self, client):
        self.client = client

    """suggest"""

    @commands.command(name="suggest", help='Make your own suggestions!')
    @commands.guild_only()
    async def suggest(self, ctx, time: TimeConverter, *, suggestion: str):
        if int(time) < 10800:
            await ctx.send("Please enter a time more than 3 hours.(3h)")
        if int(time) > 86400:
            await ctx.send("Please enter a time less than 24 hours(24h)")
        if not int(time) < 10800 and not int(time) > 86400:
            embed = discord.Embed(title=f"Suggestion by {ctx.author.name}!",
                                  description="**" + suggestion + "**" + "\n\nReact with <a:vxtick:745550119436288061> if you agree.\nReact with <a:vxcross:745553761598046280> if you disagree.",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=datetime.datetime.now())
            embed.set_footer(text="Started")
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed_send = await ctx.send(embed=embed)
            await embed_send.add_reaction(tick)
            await embed_send.add_reaction(cross)
            tick_count = 0
            cross_count = 0

            await asyncio.sleep(int(time))
            message = await ctx.message.channel.fetch_message(embed_send.id)
            for reaction in message.reactions:
                if reaction.emoji.name == "trixztick":
                    tick_count += reaction.count

                if reaction.emoji.name == "trixzcross":
                    cross_count += reaction.count

            if tick_count > cross_count:
                embed_edit1 = discord.Embed(title=f"Suggestion by {ctx.author.name}!",
                                            description="**" + suggestion + "**" + "\n\n__**<a:vxtick:745550119436288061> This suggestion was accepted!**__",
                                            color=discord.Color.green(),
                                            timestamp=datetime.datetime.now())
                embed_edit1.set_footer(text="Ended")
                embed_edit1.set_thumbnail(url=ctx.author.avatar_url)
                await embed_send.edit(embed=embed_edit1)
                await embed_send.clear_reactions()

            elif cross_count > tick_count:
                embed_edit2 = discord.Embed(title=f"Suggestion by {ctx.author.name}!",
                                            description="**" + suggestion + "**" + "\n\n__**<a:vxcross:745553761598046280> This suggestion was rejected!**__",
                                            color=discord.Color.red(),
                                            timestamp=datetime.datetime.now())
                embed_edit2.set_footer(text="Ended")
                embed_edit2.set_thumbnail(url=ctx.author.avatar_url)
                await embed_send.edit(embed=embed_edit2)
                await embed_send.clear_reactions()

            elif cross_count == tick_count:
                embed_edit3 = discord.Embed(title=f"Suggestion by {ctx.author.name}!",
                                            description="**" + suggestion + "**" + "\n\n__**🟡 This suggestion was tied!**__",
                                            color=0xebc934,
                                            timestamp=datetime.datetime.now())
                embed_edit3.set_footer(text="Ended")
                embed_edit3.set_thumbnail(url=ctx.author.avatar_url)
                await embed_send.edit(embed=embed_edit3)
                await embed_send.clear_reactions()

    """"gif"""
    
    @commands.command(name="please", help="Requests someone to do something.")
    @commands.guild_only()
    async def please(self, ctx : commands.Context, *message):
        if len(message) > 1:
            desc = " 👏🏻 ".join(x for x in message)
            if len(desc) < 2000:
                return await ctx.send(desc, allowed_mentions=discord.AllowedMentions.none())
            else:
                await ctx.send("Uh oh! Please try again with a shorter message!")
        else : #<a:trixzFastParrot:763304729471746099>
            e = discord.Embed(color=main_color, title="Nope!",
                              description=f"- {ctx.author.name}, you need to give a message more than one word!\n- Example: **`t-please this is my long message`**")
            return await ctx.send(embed=e)
    
    @commands.command(name="parrots", help="Bunch of funky parrots in ya message")
    @commands.guild_only()
    async def parrots(self, ctx : commands.Context, *message):
        if len(message) > 1:
            desc = " <a:trixzFastParrot:763304729471746099> ".join(x for x in message)
            if len(desc) < 2000:
                return await ctx.send(desc, allowed_mentions=discord.AllowedMentions.none())
            else:
                await ctx.send("Uh oh! Please try again with a shorter message!")
        else:
            e = discord.Embed(color=main_color, title="Nope!",
                              description=f"- {ctx.author.name}, you need to give a message more than one word!\n- Example: **`t-parrots this is my long message`**")
            return await ctx.send(embed=e)
    
    @commands.command(name="emojify", help="Send the message with a bunch of emojis which are mentioned!")
    @commands.guild_only()
    async def emojify(self, ctx : commands.Context, emoji : str = None, *message):
        if emoji:
            if len(message) > 1:
                desc = f" {emoji} ".join(x for x in message)
                if len(desc) < 2000:
                    return await ctx.send(desc, allowed_mentions=discord.AllowedMentions.none())
                else:
                    await ctx.send("Uh oh! Please try again with a shorter message!")
            else:
                e = discord.Embed(color=main_color, title="Nope!",
                                  description=f"- {ctx.author.name}, you need to give a message more than one word!\n- Example: **`t-emojify ⭐ this is my long message`**")
                return await ctx.send(embed=e)
        if not emoji:
            e = discord.Embed(color=main_color, title="Nope!",
                              description=f"- {ctx.author.name}, you need to give an emoji and a message more than one word!\n- Example: **`t-emojify ⭐ this is my long message`**")
            return await ctx.send(embed=e)

    @commands.command(name="gif", help="Sends a random gif of the topic searched.")
    @commands.is_nsfw()
    async def gif(self, ctx, *, search: str):
        session = aiohttp.ClientSession()
        if search == '':
            embed = discord.Embed(color=ctx.message.guild.me.top_role.color, timestamp=datetime.datetime.utcnow())
            response = await session.get(f'https://api.giphy.com/v1/gifs/random?api_key={giphy_api_key}')
            data = json.loads(await response.text())
            embed.set_image(url=data['data']['images']['original']['url'])

        else:
            await ctx.message.add_reaction(tick)
            search.replace(' ', '+')
            response = await session.get(
                f'http://api.giphy.com/v1/gifs/search?q={search}&api_key={giphy_api_key}&limit=40')
            data = json.loads(await response.text())
            gif_choice = random.randint(0, 39)
            embed = discord.Embed(title=str(data['data'][gif_choice]['title']).title(),
                                  color=ctx.message.guild.me.top_role.color, timestamp=datetime.datetime.utcnow())
            embed.set_image(url=data['data'][gif_choice]['images']['original']['url'])
            embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author.name}.")

        await session.close()
        await ctx.send(embed=embed)

    @commands.command(name="yt", help="Tells the YouTube statistics of the YouTube channel mentioned.", aliases=["ytstats", "ytinfo",])
    async def ytchannel(self, ctx, *, yt_channel_name: Union[str, discord.Member]):
        if isinstance(yt_channel_name, discord.Member):
            yt_channel_name = str(yt_channel_name.name)
        youtube = build("youtube", "v3", developerKey=YT_Key)
        search_response = youtube.search().list(q=str(yt_channel_name), part="id,snippet", maxResults=1, type="channel").execute()
        if len(search_response.get('items')) == 0:
            await ctx.send("No channels found.")
        else:
            chanid = search_response.get('items')[0]['id']['channelId']
            data = youtube.channels().list(part='statistics,snippet', id=chanid).execute()
            subs = str(data['items'][0]['statistics']
                       ['subscriberCount'])
            views = str(data['items'][0]['statistics']['viewCount'])
            name = str(data['items'][0]['snippet']['title'])
            videos = str(data['items'][0]['statistics']['videoCount'])

            img = str(data['items'][0]['snippet']['thumbnails']['medium']['url'])
            chanurl = "https://www.youtube.com/channel/" + chanid
            created_at_str = str(data['items'][0]['snippet']['publishedAt'])
            created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y")
            data = discord.Embed(
                title=f"{name}", colour=main_color, url=chanurl)
            data.add_field(name="Subscribers",
                           value=subs, inline=False)
            data.add_field(name="Total Views",
                           value=views, inline=False)
            data.add_field(name="Created At",
                           value=created_at, inline=False)
            data.add_field(name="Number of Videos",
                           value=videos, inline=False)
            data.set_thumbnail(url=img)
            data.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.avatar_url
            )
            try:
                # await ctx.message.add_reaction(tick)
                await ctx.send(embed=data)
            except discord.HTTPException:
                return await ctx.send("Looks like the bot doesn't have embed links perms. It kinda needs these, so I'd suggest adding them!")

    @commands.command(name='embed',aliases=['e'],help="Sends an embed containing the values given in the arguments.")
    @commands.guild_only()
    async def embed(self, ctx):
            global footer
            footer = ' '
            global author
            author = ' '
            # sample embed
            sample_embed = discord.Embed(title='Title', color=main_color,
                                         timestamp=datetime.datetime.utcnow(),
                                         description='This is the description of the embed.')
            sample_embed.add_field(name='Field 1 Name', value='This is the "value" of field 1.', inline=False)
            sample_embed.add_field(name='Field 2 Name', value='This is the "value" of field 2.', inline=False)
            sample_embed.add_field(name='Field 3 Name', value='This is the "value" of field 3.', inline=False)
            sample_embed.set_author(name='<- Author Icon | Author Name', icon_url='https://cdn.discordapp.com/attachments/725546147640246284/769120085893709844/Author_inverted.png')
            sample_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725546147640246284/769120089487704084/Thumbnail_inverted.png')
            sample_embed.set_image(url='https://cdn.discordapp.com/attachments/725546147640246284/769120088262967296/IMAGE_inverted.png')
            sample_embed.set_footer(text='<- Footer icon | Footer Text.',
                                    icon_url='https://cdn.discordapp.com/attachments/725546147640246284/769120087814701076/Footer_inverted.png')
            sample = await ctx.send('<a:trixzhaloween:762682117603065908> Here is a sample embed -', embed=sample_embed)
            embed = discord.Embed(title='‏‏‎ ')
            init_send = await ctx.send(f"{main_emoji} You can reply with __any option from the following to add that option__-\n"
                                       '```prolog\n⚔ Title\n⚔ Description\n⚔ Thumbnail\n⚔ Timestamp\n⚔ Fields\n⚔ Color\n⚔ Author\n⚔ Author Icon\n⚔ Image\n⚔ Footer\n⚔ Footer Icon\n```\n'
                                       f"{main_emoji} Reply with `save` => save the embed built.\n"
                                       f"{main_emoji} Reply with `exit` => exit out of the command.\n"
                                       f"{main_emoji} If you do not reply __within 2 minutes__, the command will stop.",
                                       file=discord.File(fp='trixz-divider.gif', filename='trixz-divider.gif'))
            # _________
            options = 14
            def normal_check(m):
                return m.content is not None and m.author == ctx.author and m.channel == ctx.message.channel
            def url_check(m):
                return m.content.startswith("https://") and m.author == ctx.author and m.channel == ctx.message.channel
            def yn_check(m):
                return m.content in ['Y', 'N'] and m.author == ctx.author and m.channel == ctx.message.channel
            # def save_check(reaction, user):
            # return str(reaction.emoji) == "<a:vxtick:745550119436288061>" and user.id == ctx.author.id
            def number_check(m):
                return len(m.content) == 1 and m.author == ctx.author and m.channel == ctx.message.channel and m.content in ['1', '2', '3', '4', '5']
            while options > 0:
                try:
                    wait = await self.client.wait_for('message', check=normal_check, timeout=180)
                    if "fields" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask = await ctx.send('<a:trixzhaloween:762682117603065908> How many fields do you want to enter? [From 1 to 5]')
                        number_of_fields = await self.client.wait_for('message', check=number_check, timeout=120)
                        #await number_of_fields.delete()
                        await ask.delete()
                        number_of_fields1 = int(number_of_fields.content)
                        options -= 1
                        field = 0
                        while number_of_fields1 > 0:
                            number_of_fields1 -= 1
                            field += 1
                            ask12 = await ctx.send(
                                f"{main_emoji} Enter field {field}'s **name** and **value** separated by `//`\nExample - \n```Ball//The ball is red.```")
                            field_ = await self.client.wait_for('message', check=normal_check)
                            #await field_.delete()
                            await ask12.delete()
                            separated = field_.content.split('//')
                            embed.add_field(name=separated[0], value=separated[1], inline=False)
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "title" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask2 = await ctx.send('<a:trixzhaloween:762682117603065908> Enter title of the embed -')
                        title = await self.client.wait_for('message', check=normal_check, timeout=120)
                        #await title.delete()
                        await ask2.delete()
                        embed.title = title.content
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "description" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask3 = await ctx.send('<a:trixzhaloween:762682117603065908> Enter description of the embed -')
                        description = await self.client.wait_for('message', check=normal_check, timeout=120)
                        #await description.delete()
                        await ask3.delete()
                        embed.description = description.content
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "thumbnail" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask4 = await ctx.send('<a:trixzhaloween:762682117603065908> Enter the thumbnail url link-')

                        url = await self.client.wait_for('message', check=url_check, timeout=120)
                        #await url.delete()
                        await ask4.delete()
                        embed.set_thumbnail(url=url.content)
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "timestamp" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask5 = await ctx.send('<a:trixzhaloween:762682117603065908> Enter timestamp in the embed? [Y/N]')
                        timestamp = await self.client.wait_for('message', check=yn_check, timeout=120)
                        #await timestamp.delete()
                        await ask5.delete()
                        embed.timestamp = datetime.datetime.utcnow() if "y" in timestamp.content.lower() else discord.Embed.Empty
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "color" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask6 = await ctx.send(
                            '<a:trixzhaloween:762682117603065908> Enter the hex code of the color __without__ the "#" [You can get the hex code from here - https://www.google.com/search?q=color+picker]')

                        Color = await self.client.wait_for('message', check=normal_check, timeout=120)
                        #await Color.delete()
                        await ask6.delete()
                        embed.colour = int(Color.content, base=16)
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if wait.content.lower() == "author":
                        # await ctx.message.channel.purge(limit=1)
                        ask7 = await ctx.send('<a:trixzhaloween:762682117603065908> Enter author name -')

                        author = await self.client.wait_for('message', check=normal_check, timeout=120)
                        #await author.delete()
                        await ask7.delete()
                        embed.set_author(name=author.content)
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if wait.content.lower() == "author icon":
                        # await ctx.message.channel.purge(limit=1)
                        ask8 = await ctx.send(f"{main_emoji} Enter author icon's url link -")

                        author_icon = await self.client.wait_for('message', check=url_check, timeout=120)
                        #await author_icon.delete()
                        await ask8.delete()
                        embed.set_author(icon_url=author_icon.content,
                                         name=author.content if author.content is not None else '‏‏‎ ')
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "image" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        ask9 = await ctx.send(f"{main_emoji} Enter image's url link -")

                        image_ = await self.client.wait_for('message', check=url_check, timeout=120)
                        #await image_.delete()
                        await ask9.delete()
                        embed.set_image(url=image_.content)
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if wait.content.lower() == "footer":
                        # await ctx.message.channel.purge(limit=1)
                        ask10 = await ctx.send(f"{main_emoji} Enter footer -")
                        footer = await self.client.wait_for('message', check=normal_check, timeout=120)
                        #await footer.delete()
                        # await ask10.delete()
                        embed.set_footer(text=footer.content)
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if wait.content.lower() == "footer icon":
                        # await ctx.message.channel.purge(limit=1)
                        ask11 = await ctx.send(f"{main_emoji} Enter footer icon's url link -")

                        footer_icon = await self.client.wait_for('message', check=url_check, timeout=120)
                        #await footer_icon.delete()
                        # await ask11.delete()
                        embed.set_footer(icon_url=footer_icon.content,
                                         text=footer.content if footer.content is not None else '‏‏‎ ')
                        options -= 1
                        await ctx.send(
                            f"{main_emoji} You can save this embed by replying with `save` or continue to build your embed.",
                            embed=embed)
                    if "exit" in wait.content.lower():
                        await wait.add_reaction("<a:vxtick:745550119436288061>")
                        await ctx.send('<a:trixzhaloween:762682117603065908> Successfully exited.')
                        break
                    if "save" in wait.content.lower():
                        # await ctx.message.channel.purge(limit=1)
                        await ctx.send('<a:trixzhaloween:762682117603065908> Saved the embed!', embed=embed)
                        await ctx.send('<a:trixzhaloween:762682117603065908> In which channel would you like to send this embed?')
                        def channel_check(m):
                            return len(m.channel_mentions) == 1 and m.channel == ctx.channel and m.author == ctx.author
                        where = await self.client.wait_for('message', check=channel_check)
                        channel = await TextChannelConvert().convert(ctx=ctx, argument=where.content)
                        await channel.send(embed=embed)
                        await where.add_reaction("<a:vxtick:745550119436288061>")
                        await ctx.send(f'Successfully sent the embed in {channel.mention}.')
                        break
                except Exception as e:
                    print(e)
                    # await sample.delete()
                    # await init_send.delete()
                    await ctx.send(f"Timeout/Error!", delete_after=5)
                    break

    @commands.command(name="hello", aliases=['hey', 'hi', 'yo', 'wassup', 'sup'], help="Sends a hello image!")
    async def _hello(self, ctx):
        W, H = (1500, 500)
        img = Image.open('Hello.png')
        draw = ImageDraw.Draw(img)
        msg = ctx.author.display_name + '!'
        font = ImageFont.truetype('Font.otf', size=120)
        w, h = draw.textsize(msg, font=font)
        draw.text(
            xy=((W-w)/2, ((H-h)/2) + 115),
            text=msg,
            font=font,
            fill=(23, 161, 198),
        )
        with BytesIO() as image:
            img.save(image, 'PNG')
            image.seek(0)
            await ctx.message.add_reaction(tick)
            await ctx.send(file=discord.File(fp=image, filename=f'Hello_{ctx.author.display_name}.png'))

    """Bye"""

    @commands.command(name="bye", aliases=["gtg", "cya", "bie"], help="Sends a bye message!")
    async def _bye(self, ctx, ):
        W, H = (1500, 500)
        img = Image.open('Bye.png')
        draw = ImageDraw.Draw(img)
        msg = ctx.author.display_name + '!'
        font = ImageFont.truetype('Font.otf', size=120)
        w, h = draw.textsize(msg, font=font)
        draw.text(
            xy=((W - w) / 2, ((H - h) / 2) + 115),
            text=msg,
            font=font,
            fill=(23, 161, 198),
        )
        with BytesIO() as image:
            img.save(image, 'PNG')
            image.seek(0)
            # await ctx.message.add_reaction(tick)
            await ctx.send(file=discord.File(fp=image, filename=f'Bye_{ctx.author.display_name}.png'))

    @commands.command(name="ping", help="Tells the ping of the bot.")
    async def ping(self, ctx):
        latency = round(self.client.latency * 1000)
        embed = discord.Embed(title=f"Ping: {latency}ms", color=main_color)
        await ctx.send(embed=embed)

    @commands.command(name="file", help="Sends the image(link) in an embed format!")
    async def file(self, ctx, link):
        embed = discord.Embed(color=main_color)
        embed.set_image(url=link)
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await ctx.message.delete()

    @commands.command(name="videro", help="Sends Videro's socials!")
    async def videro(self, ctx, social: str):
        if social.lower() == "yt":
            ytembed = discord.Embed(title="Click here for Videro's YT Channel", url='https://www.tinyurl.com/mrmaxay', color=main_color)
            await ctx.send(embed=ytembed)
        elif social.lower() == "twitter":
            twitterembed = discord.Embed(title="Click here for Videro's Twitter",
                                         url='https://www.twitter.com/Videro1407',
                                         color=main_color)
            await ctx.send(embed=twitterembed)
        elif social.lower() == "insta":
            instaembed = discord.Embed(title="Click here for Videro's Insta", url='https://www.instagram.com/videro.dzns',
                                       color=main_color)
            await ctx.send(embed=instaembed)
        else:
            await ctx.send(f"{ctx.author.mention} the socials available are - `yt`, `twitter` and `insta`.")

    @commands.command(name="ops", help="Lets you give ops on an image.", aliases=["giveops"])
    @commands.guild_only()
    async def _ops(self, ctx, user: discord.User):
        ops = []
        ops_given_to = []
        image_link = []
        channel = await ctx.author.create_dm()
        submit_channel = ctx.message.channel
        await channel.send(f"On which Image do you want to give ops?[Copy the link of the image and send it below]",
                           file=discord.File(fp="example.png",
                                             filename="example.png"))
        await ctx.message.add_reaction(tick)
        await submit_channel.send(f"{ctx.author.mention} Check your DM!")

        def check2(m2):
            return m2.content is not None and m2.author == ctx.author and m2.channel == channel

        msg2 = await self.client.wait_for("message",
                                     check=check2)
        image_link.append(msg2.content)
        await channel.send(f"{ctx.author.mention} Please send your ops in this format below -\n"
                           "1st Opinion.\n"
                           "2nd Opinion.")

        def check3(m3):
            return m3.content is not None and m3.author == ctx.author and m3.channel == channel

        msg3 = await self.client.wait_for("message", check=check3)
        ops.append(msg3.content)
        image_link1 = "".join(f'{a}. {b}' for a, b in enumerate(image_link))
        ops1 = "".join(f'{a}. {b}' for a, b in enumerate(ops, 1))
        imagelink = image_link1[2:]
        embed = discord.Embed(title="Opinions!",
                              color=main_color,
                              description=ops1)
        embed.set_image(url=imagelink)
        await submit_channel.send(f"**Ops given by {ctx.author.mention} to {user.mention}.**",
                                  embed=embed)
        await channel.send(
            f"{ctx.author.mention} you successfully gave ops to {user.mention} in {ctx.message.channel.mention}.")

    @commands.command(name="say", help="Sends the message mentioned in the mentioned channel!")
    async def say(self, ctx : commands.Context, channel: discord.TextChannel, *, message):
        if ctx.author.permissions_in(channel).send_messages:
            await channel.send(message + f'\n\n -said by {ctx.author.name}#{ctx.author.discriminator}.', allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
            await ctx.message.add_reaction(tick)
            return
        
        else:
            await ctx.send(f"Sorry, you do not have the permission to send messages in {channel.mention}")
            return
        
def setup(client):
    client.add_cog(general(client))