import discord
from discord.ext import commands
import datetime
import asyncpg
import asyncio
from _Utils import Message
from bot import main_color, tick, main_emoji
class levels(commands.Cog):
    """Level system commands which are accessible to all members of the server!"""
    def __init__(self, client):
        self.client = client

    async def lvl_up(self, user):
        cur_lvl = user['level']
        cur_xp = user['xp']
        if cur_xp >= round((4 * (cur_lvl ** 3)) / 5):
            await self.client.pg_con.execute('UPDATE user_levels SET level = $1 WHERE user_id = $2 AND guild_id = $3', cur_lvl+1, user['user_id'], user['guild_id'])
            return True
        else:
            return False

    @commands.command(name='levels')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def levels(self, ctx,  on_off :str = None):
        """Turns level system on/off depending on the argument given. [on or off]"""
        if on_off:
            guild_id = str(ctx.guild.id)
            fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
            if fetch:
                if on_off == 'on':
                    await self.client.pg_con.execute('UPDATE all_guilds SET levels_enabled = $1 WHERE guild_id = $2',
                                                     'yes', guild_id)
                    await Message.EmbedText(
                        title='Level system is now turned on!',
                        color=main_color
                    ).send(ctx)
                if on_off == 'off':
                    await self.client.pg_con.execute('UPDATE all_guilds SET levels_enabled = $1 WHERE guild_id = $2', 'no', guild_id)
                    await ctx.message.add_reaction(tick)
                    await Message.EmbedText(
                        title='Level system is now turned off!',
                        color=main_color
                    ).send(ctx)
            if not fetch:
                if on_off == 'on':
                    await self.client.pg_con.execute('UPDATE all_guilds SET levels_enabled = $1 WHERE guild_id = $2', 'yes', guild_id)
                    await ctx.message.add_reaction(tick)
                    await Message.EmbedText(
                        title='Level system is now turned on!',
                        color=main_color
                    ).send(ctx)
                if on_off == 'off':
                    await Message.EmbedText(
                        title='Level system was already turned off!',
                        color=main_color
                    ).send(ctx)
        
        if not on_off:
            await Message.EmbedText(
                title='Please select whether you want to turn levels off/on.',
                color=main_color
            ).send(ctx)
        
        else:
            return 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            guild_id = str(message.guild.id)
            fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
            if fetch:
                if fetch[0]['levels_enabled'] == 'yes':
                    if not message.content.startswith('t-') and not message.embeds and not message.attachments and not message.author.bot and message.guild is not None:
                        guild_id = str(message.guild.id)
                        user_id = str(message.author.id)
                        user = await self.client.pg_con.fetch('SELECT * FROM user_levels WHERE user_id = $1 AND guild_id = $2', user_id, guild_id)
                        if not user:
                            await self.client.pg_con.execute('INSERT INTO user_levels (user_id, guild_id, level, xp) VALUES ($1, $2, 1, 0)', user_id, guild_id)
                        user = await self.client.pg_con.fetchrow('SELECT * FROM user_levels WHERE user_id = $1 AND guild_id = $2', user_id, guild_id)
                        await self.client.pg_con.execute('UPDATE user_levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3', user['xp'] + 1, user_id, guild_id)
                        if await self.lvl_up(user):
                            channel_id = int
                            log_channel = await self.client.pg_con.fetch('SELECT level_log_channel FROM level_log_channels WHERE guild_id = $1', guild_id)
                            if not log_channel:
                                channel_id = message.channel.id
                            if log_channel:
                                channel_id = int(log_channel[0]['level_log_channel'])
                            channel = await self.client.fetch_channel(channel_id=channel_id)
                            await channel.send(f'{main_emoji} **{message.author.name}** just leveled up to **level {user["level"] + 1}** {main_emoji}')

            else:
                return

    @commands.command(name='level', help="Shows the user's level!")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def level(self, ctx, member : discord.Member = None):
        """Shows the level of the user mentioned, if the user is mentioned, else the author of the command."""
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['levels_enabled'] == 'yes':
            member = ctx.author if not member else member
            member_id = str(member.id)
            guild_id = str(ctx.guild.id)
            user = await self.client.pg_con.fetch('SELECT * FROM user_levels WHERE user_id = $1 AND guild_id = $2', member_id, guild_id)
            if not user:
                await self.client.pg_con.fetch('INSERT INTO user_levels (user_id, guild_id, level, xp) VALUES ($1, $2, 1, 0)', member_id, guild_id)
            user = await self.client.pg_con.fetch('SELECT * FROM user_levels WHERE user_id = $1 AND guild_id = $2', member_id, guild_id)
            embed = discord.Embed(
                color=main_color,
                timestamp=datetime.datetime.utcnow()
            ).set_footer(
                text=ctx.guild.name,
                icon_url=ctx.guild.icon_url
            ).set_author(
                name=member.display_name,
                icon_url=member.avatar_url
            ).set_thumbnail(
                url=member.avatar_url
            ).add_field(
                name='💎 Level' + f' {user[0]["level"]}',
                value='Gain more XP to level up!',
                inline=False
            ).add_field(
                name='💎 ' + str(user[0]['xp']) + ' XP',
                value='Type in chat for more XP. +1 XP per message.'
            )
            await ctx.send(embed=embed)
        
        else:
            await Message.EmbedText(
                title='Level system is disabled in ' + ctx.guild.name, color=main_color
            ).send(ctx)

    @commands.command(name='leaderboard', help='Shows the leaderboard of the server!', aliases=['top'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def leaderboard(self, ctx):
        """Displays the leaderboard of the server! [Top 10 users]"""
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['levels_enabled'] == 'yes':
            users = await self.client.pg_con.fetch('SELECT * FROM user_levels WHERE guild_id = $1', str(ctx.guild.id))
            sorted_users = sorted(users, key=lambda x: x['xp'], reverse=True)
            desc = []
            index = 0
            medals = ['🥇', '🥈', '🥉', '🏅', '🏅', '🏅', '🏅', '🏅', '🏅', '🏅']
            for record in sorted_users:
                #{medals[index if index <= 10 else -1]}
                desc.append(f"**{medals[index if index <= 9 else -1]} <@!{record['user_id']}> - Level {record['level']} - {record['xp']} XP **\n")
                index += 1
            embed = discord.Embed(title=f"Leaderboard!",
                                  color=main_color,
                                  timestamp=ctx.message.created_at,
                                  description=''.join(f'{b}' for a, b in enumerate(desc[0:5], 1))
                                  )
            embed.set_footer(text='Page 1/2' if len(users) >= 10 else "", icon_url=ctx.message.guild.icon_url)
            await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
            embed_send = await ctx.send(embed=embed)
            if len(users) >= 10:
                await embed_send.add_reaction("▶")
                while True:
                    def check(reaction, user):
                        return str(reaction.emoji) == '▶' and user == ctx.message.author
    
                    try:
                        await self.client.wait_for('reaction_add', check=check, timeout=45)
                    except asyncio.TimeoutError:
                        break
                    else:
                        embed1 = discord.Embed(title=f"Leaderboard!",
                                               color=main_color,
                                               timestamp=ctx.message.created_at,
                                               description=''.join(f'{b}' for a, b in enumerate(desc[6:11], 1)))
                        embed1.set_footer(text='Page 2/2', icon_url=ctx.message.guild.icon_url)
                        await embed_send.edit(embed=embed1)
                        await embed_send.clear_reactions()
                        await embed_send.add_reaction('◀')
    
                    def check1(reaction, user):
                        return str(reaction.emoji) == '◀' and user == ctx.message.author
    
                    try:
                        await self.client.wait_for('reaction_add', check=check1, timeout=45)
                    except asyncio.TimeoutError:
                        break
                    else:
                        await embed_send.edit(embed=embed)
                        await embed_send.clear_reactions()
                        await embed_send.add_reaction('▶')
        else:
            await Message.EmbedText(
                title='Level system is disabled in ' + ctx.guild.name, color=main_color
            ).send(ctx)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def setlevels(self, ctx, channel: discord.TextChannel):
        """Sets the level log channel to the channel mentioned."""
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['levels_enabled'] == 'yes':
            channel_id = str(channel.id)
            guild_id = str(ctx.message.guild.id)
            log_channel = await self.client.pg_con.fetch(
                'SELECT level_log_channel FROM level_log_channels WHERE guild_id = $1', guild_id)
            if not log_channel:
                await self.client.pg_con.execute(
                    'INSERT INTO level_log_channels (guild_id, level_log_channel) VALUES ($1, $2)', guild_id, channel_id)
            await self.client.pg_con.execute('UPDATE level_log_channels SET level_log_channel = $1 WHERE guild_id = $2',
                                             channel_id, guild_id)
            log_channel = await self.client.pg_con.fetch(
                'SELECT level_log_channel FROM level_log_channels WHERE guild_id = $1', guild_id)
            await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
            await ctx.send(f'Successfully set the level logs to <#{int(log_channel[0]["level_log_channel"])}>.')
        else:
            await Message.EmbedText(
                title='Level system is disabled in ' + ctx.guild.name, color=main_color
            ).send(ctx)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def levelchannel(self, ctx):
        """Sends the current level log channel, if level logging is enabled."""
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT levels_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['levels_enabled'] == 'yes':
            guild_id = str(ctx.message.guild.id)
            log_channel = await self.client.pg_con.fetch(
                'SELECT level_log_channel FROM level_log_channels WHERE guild_id = $1', guild_id)
            if log_channel:
                await ctx.send(
                    f'The level logs channel in **{ctx.message.guild.name}** is set to <#{int(log_channel[0]["level_log_channel"])}>.\n'
                    f'To change the log channel, type - `t-setlevels #channel-name`.')
            if not log_channel:
                await ctx.send(
                    'The level logs are __not set__ to any channel, so, the bot will send the level up message in __the channel in which the user levels up__!\n'
                    'To set the level logs, type - `t-setlevels #channel-name`.'
                )
        else:
            await Message.EmbedText(
                title='Level system is disabled in ' + ctx.guild.name, color=main_color
            ).send(ctx)

def setup(client):
    client.add_cog(levels(client))