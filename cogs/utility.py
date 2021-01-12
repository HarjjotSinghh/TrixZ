import discord
from discord.ext import commands
import asyncio
import random
import datetime
import re
from bot import main_color, tick, cross
from _Utils import Message
import os
from bot import support_server_url, invite_url
import calendar, functools
from typing import *
import functools

class TextChannelConvert(commands.TextChannelConverter):
    async def convert(self, ctx, argument):
        channel = await super().convert(ctx, argument)
        return channel

def get_years(timeBetween, year, reverse):
    years = 0

    while True:
        if reverse:
            year -= 1
        else:
            year += 1

        year_days = 366 if calendar.isleap(year) else 365
        year_seconds = year_days * 86400

        if timeBetween < year_seconds:
            break

        years += 1
        timeBetween -= year_seconds

    return timeBetween, years, year

def get_months(timeBetween, year, month, reverse):
    months = 0

    while True:
        month_days = calendar.monthrange(year, month)[1]
        month_seconds = month_days * 86400

        if timeBetween < month_seconds:
            break

        months += 1
        timeBetween -= month_seconds

        if reverse:
            if month > 1:
                month -= 1
            else:
                month = 12
                year -= 1
        else:
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1

    return timeBetween, months

def getReadableTimeBetween(first, last, reverse=False):
    # A helper function to make a readable string between two times
    timeBetween = int(last - first)
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    timeBetween, years, year = get_years(timeBetween, year, reverse)
    timeBetween, months = get_months(timeBetween, year, month, reverse)

    weeks = int(timeBetween / 604800)
    days = int((timeBetween - (weeks * 604800)) / 86400)
    hours = int((timeBetween - (days * 86400 + weeks * 604800)) / 3600)
    minutes = int((timeBetween - (hours * 3600 + days * 86400 + weeks * 604800)) / 60)
    seconds = int(timeBetween - (minutes * 60 + hours * 3600 + days * 86400 + weeks * 604800))
    msg = ""

    if years > 0:
        msg += "1 year, " if years == 1 else "{:,} years, ".format(years)
    if months > 0:
        msg += "1 month, " if months == 1 else "{:,} months, ".format(months)
    if weeks > 0:
        msg += "1 week, " if weeks == 1 else "{:,} weeks, ".format(weeks)
    if days > 0:
        msg += "1 day, " if days == 1 else "{:,} days, ".format(days)
    if hours > 0:
        msg += "1 hour, " if hours == 1 else "{:,} hours, ".format(hours)
    if minutes > 0:
        msg += "1 minute, " if minutes == 1 else "{:,} minutes, ".format(minutes)
    if seconds > 0:
        msg += "1 second, " if seconds == 1 else "{:,} seconds, ".format(seconds)

    if msg == "":
        return "0 seconds"
    else:
        return msg[:-2]

def setup(client):
    client.add_cog(utility(client))

class utility(commands.Cog):
    """Utility commands which assist the administrators and moderators of the server!"""
    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.command(name="poll", help="Sets up a voting poll!", aliases=["setpoll"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_messages=True)
    async def _poll(self, ctx):
        await Message.EmbedText(
            title='How many options for the poll? [From 2-7]',
            color=main_color
        ).send(ctx)

        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.channel

        wait1 = await self.client.wait_for("message", check=check, timeout=100)
        number_of_options = int(wait1.content)
        if number_of_options > 7:
            await Message.EmbedText(
                description="Maximum number of choices which can be set are **__7__**.\n"
                            "Please run the command again and specify a correct value."
            ).send(ctx)
            return
        else:
            def check2(m):
                return m.author == ctx.author and m.channel == ctx.channel

            messages = {}
            for i in range(int(number_of_options)):
                await Message.EmbedText(
                    title=f'Enter option {i + 1}:'
                ).send(ctx)
                message = await self.client.wait_for("message", check=check2, timeout=100)
                message_contet = message.content
                messages[i] = message_contet

            t = range(number_of_options)

            count_emoji = list([f'1\N{combining enclosing keycap}', f'2\N{combining enclosing keycap}',
                                f'3\N{combining enclosing keycap}', f'4\N{combining enclosing keycap}',
                                f'5\N{combining enclosing keycap}', f'6\N{combining enclosing keycap}',
                                f'7\N{combining enclosing keycap}'])
            emojis_list = []
            for t in count_emoji:
                emojis_list.append(t)

            s = "\n"
            embed_description = str(
                s.join(str(f"**{count_emoji} - {o}**") for count_emoji, o in zip(emojis_list, messages.values())))
            embed = discord.Embed(title="📊 New Poll! 📊",
                                  color=main_color,
                                  timestamp=datetime.datetime.utcnow(),
                                  description=f"\n{embed_description}")
            embed.set_footer(text=ctx.message.guild.name)
            embed_send = await ctx.send(embed=embed)
            for option in range(number_of_options):
                await embed_send.add_reaction(f'{option + 1}\N{combining enclosing keycap}')

    @commands.command(name="changenicks", help="Changes the nickname of the hoisters.")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.has_permissions(manage_nicknames=True)
    async def _changenicks(self, ctx):
        changed_nicks_users = 0
        for member in ctx.message.guild.members:
            if not str(member.display_name).lower().startswith(
                    tuple(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"])):
                await member.edit(nick="don't hoist")
                changed_nicks_users += 1
        await ctx.send(f"Changed the nick of {changed_nicks_users} members to `don't hoist.`")

    @commands.command(name="clear", help="Deletes the number of messages mentioned from the channel.\nOptions available - `t-clear <amount> <member>` | `t-clear <amount> bots` | `t-clear <amount>`", aliases=['purge'])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.member)
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx : commands.Context, amount : int = 0, member : Union[discord.Member, str] = None):
        if not member:
            if amount > 100:
                e = discord.Embed(color=main_color, title=f"{ctx.author.name}, You cannot delete more than __100 messages__!")
                return await ctx.send(embed=e)
            await ctx.channel.purge(limit=amount + 1)
            # await ctx.message.add_reaction(tick)
            return await Message.EmbedText(
                title=f'Successfully cleared {amount} message{"s" if amount > 1 else ""}.',
                footer='This message will be deleted in 2 seconds.',
                delete_after=2
            ).send(ctx)
        if member:
            if isinstance(member, discord.Member):
                def member_check(m : discord.Message):
                    return m.author == member
                await ctx.channel.purge(limit=amount + 1, check=member_check)
                # await ctx.message.add_reaction(tick)
                return await Message.EmbedText(
                    title=f'Successfully cleared {amount} message{"s" if amount > 1 else ""} by {member.display_name}.',
                    footer='This message will be deleted in 2 seconds.',
                    delete_after=2
                ).send(ctx)
            if isinstance(member, str):
                if member.lower() in ("bot", "bots"):
                    def member_check(m):
                        return m.author.bot == True
                    await ctx.channel.purge(limit=amount + 1, check=member_check)
                    return await Message.EmbedText(
                        title=f'Successfully cleared {amount} message{"s" if amount > 1 else ""} by all bots.',
                        footer='This message will be deleted in 2 seconds.',
                        delete_after=2
                    ).send(ctx)
                else:
                    e0 =  discord.Embed(title="Nope!",
                                        description=f"{ctx.author.name}, **{member}** is not a valid option!\n"
                                                    f"Available Options:\n"
                                                    f"- **`t-clear <amount> <member>`** to clear all the messages sent by the member.\n"
                                                    f"- **`t-clear <amount> bots`** to clear all the messages sent by bots.",
                                        color=main_color)
                    return await ctx.send(embed=e0)

    """
    @commands.command(name="giveaway", help="Starts an interactive giveaway setup!")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _giveaway(self, ctx):
        ask1 = await ctx.send(f'{ctx.author.mention}, What is the prize of the giveaway?')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        prize = await self.client.wait_for('message', check=check, timeout=200)

        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await prize.delete()
        await ask1.delete()
        ask2 = await ctx.send(
            f'{ctx.author.mention}, In which channel do you want to set the giveaway? [Mention the channel]')
        channel1 = await self.client.wait_for('message', timeout=200, check=check1)
        await ask2.delete()
        await channel1.delete()
        channel = channel1.channel_mentions[0] if channel1.channel_mentions[0] else ctx.guild.text_channels[2]
        ask3 = await ctx.send(f'{ctx.author.mention}, Whats the duration of the giveaway? [Example - 24h]')
        duration1 = await self.client.wait_for('message', timeout=200, check=check)
        duration = 0
        time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
        time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
        matches = re.findall(time_regex, duration1.content)
        for v, k in matches:
            try:
                duration += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        await ask3.delete()
        await duration1.delete()
        giveaway_embed = discord.Embed(title=f"{str(prize.content)}",
                                       description=f"Hosted by - {ctx.author.mention}\n"
                                                   f"**React with :tada: to enter!\n**"
                                                   f"Time Remaining: {int(duration)} seconds",
                                       color=main_color,)
        embed_send = await channel.send(content=":tada: **GIVEAWAY** :tada:", embed=giveaway_embed)

        await embed_send.add_reaction("🎉")

        await ctx.send(f"Successfully setup the giveaway in {channel.mention}.", delete_after=5)

        def check(reaction, user):
            return user is not None and str(reaction.emoji) == '🎉'

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
            await embed_send.remove_reaction('🎉', self.client.user)
        except asyncio.TimeoutError:
            await embed_send.remove_reaction("🎉", member=self.client.user)

        while duration > 0:
            await asyncio.sleep(120)
            duration -= 120
            giveaway_embed = discord.Embed(title=f"{str(prize.content)}",
                                           description=f"Hosted by - {ctx.author.mention}\n"
                                                       f"**React with :tada: to enter!\n**"
                                                       f"Time Remaining: {getReadableTimeBetween()} seconds",
                                           color=main_color, )
            await embed_send.edit(embed=giveaway_embed)

        message = await channel.fetch_message(embed_send.id)
        reactions = message.reactions
        reply = list()

        for reaction in reactions:
            if reaction.emoji == "🎉":
                users = reaction.users()
                async for user in users:
                    reply.append("<@" + str(user.id) + ">")

        winner = random.choice(reply)

        giveaway_embed2 = discord.Embed(title=f"{str(prize.content)}",
                                        description=f"**Giveaway ended.**\n"
                                                    f"Hosted by - {ctx.author.mention}\n"
                                                    f"Winner - {winner}"
                                                    ,
                                        color=discord.Color.red(),
                                        timestamp=datetime.datetime.now()).add_field(
            name='Additional Links',
            value=f'[Invite TrixZ]({invite_url})\n'
                  f'[Support Server]({support_server_url})'
        )

        await embed_send.edit(content=":tada: **GIVEAWAY ENDED** :tada:", embed=giveaway_embed2)
        await embed_send.clear_reactions()

        congo = await channel.send(
            f"Congratulations {winner}, you just won **{prize.content}**! (Giveaway hosted by {ctx.author.mention})\n"
            f"{message.jump_url}")

        await congo.add_reaction("🙂")

        for mention in congo.mentions:
            await mention.send(f"Congratulations {winner}, you just won **{prize.content}**!\n"
                               f"{message.jump_url}")
    """ 

    @commands.command(name="nuke", help="Nukes the channel completely.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 120, commands.BucketType.member)
    async def _nuke(self, ctx):
        pin1 = await ctx.send(f'Started nuking this channel!')
        await ctx.channel.purge(limit=10000000000000000000000)
        channel = ctx.channel
        nuke_url = 'https://attackofthefanboy.com/wp-content/uploads/2019/10/nuke-cod-mobile.jpg'
        embed = discord.Embed(title=f"{str(ctx.author)} just nuked this channel!",
                              color=main_color)
        # print(f"{ctx.author.display_name} just nuked {channel}.")
        embed.set_image(url=nuke_url)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name="announce", help="Starts an interactive announcement builder!")
    @commands.has_permissions(manage_channels=True, manage_guild=True, manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def _announce(self, ctx):
        await Message.EmbedText(
            title=f'Would you like to send an `embed` announcement or a `message` announcement?',
            color=main_color
        ).send(ctx)
        def check20(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ('embed', 'message')
        embedormessage = await self.client.wait_for('message', check=check20, timeout=120)
        if 'embed' in embedormessage.content.lower():
            send = await ctx.send('Starting the embed builder.')
            await asyncio.sleep(1)
            await send.delete()
            await ctx.invoke(self.client.get_command('embed'))
        elif 'message' in embedormessage.content.lower():
            ask1 = await Message.EmbedText(
                title='Enter the announcement message:',
                color=main_color
            ).send(ctx)
            a_message = await self.client.wait_for('message', check=lambda x: x.author == ctx.author and x.channel == ctx.channel)
            await ask1.delete()
            await a_message.delete()
            ask2 = await Message.EmbedText(
                title='Where do you want to send the message? [Mention the channel]',
                color=main_color
            ).send(ctx)
            channel1 = await self.client.wait_for('message', check=lambda x: x.author == ctx.author and x.channel == ctx.channel)
            channel = await TextChannelConvert().convert(ctx=ctx, argument=channel1.content)
            await channel.send(a_message.content)
            await ask2.delete()
            await channel1.add_reaction(tick)

    @commands.command(name="history", help="Saves all the messages of a channel in a `.txt` file!",
                      aliases=['transcript'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    async def _history(self, ctx, limit = 10000000):
        channel = ctx.message.channel
        await ctx.send("Collecting all the messages and writing them into a file!")
        messages = await ctx.channel.history(
            limit=limit).flatten()
        def save_all_messages():
            with open(f"{channel}_messages.txt", "a+", encoding="utf-8") as f:
                print(f"\nTranscript Saved by - {ctx.author.display_name}.\n\n", file=f)
                for message in messages:
                    if len(message.embeds) != 0:
                        embed = message.embeds[0].description if message.embeds[0].description else message.embeds[0].title
                        print(f"{message.author.name} - {embed}", file=f)
                    else:
                        print(f"{message.author.name} - {message.clean_content}", file=f)
        save = functools.partial(save_all_messages)
        await self.client.loop.run_in_executor(None, save)
        await ctx.message.add_reaction(tick)
        history = discord.File(fp=f'{channel}_messages.txt', filename=f'{channel}_messages.txt')
        await ctx.send(f"{ctx.author.mention}, Transcript for the channel {ctx.channel.mention} saved.", file=history)
        try:
            os.remove(f'{channel}_messages.txt')
        except:
            pass

    # """dm"""
    #
    # @commands.command(name="dm", help="Sends the mentioned user the message you type.")
    # @commands.cooldown(1, 5)
    # @commands.has_permissions(administrator=True)
    # async def dm(self, ctx, user: discord.User, *, message: str):
    #     await user.send(message)
    #     await user.send(content='Message sent to you by ' + ctx.author.name + ' via me!')
    #     e = discord.Embed(title=f"Message sent to {user.display_name}.", description=message, color=main_color)
    #     e.set_footer(text=f"Sent by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    #     await ctx.message.add_reaction(tick)
    #     await ctx.send(embed=e)
