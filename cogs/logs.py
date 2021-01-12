import discord
from discord.ext import commands
import asyncio
import datetime
from bot import tick, cross, main_color
from _Utils import Message

def setup(client):
    client.add_cog(logs(client))

class logs(commands.Cog):
    """Server logging commands which are only accessible to the administrators and owners of the server!"""

    def __init__(self, client):
        self.client = client

    @commands.group(name='logs')
    async def logs(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('logshelp'))

    @logs.command(name='disable', help='Disables all the logs!')
    @commands.cooldown(1, 3 , commands.BucketType.member)
    @commands.has_permissions(manage_guild=True)
    async def logs_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if log_channel:
            await self.client.pg_con.execute('DELETE FROM log_channels WHERE guild_id = $1', guild_id)
            await Message.EmbedText(
                color=main_color,
                title='Successfully disabled logging!',
            ).send(ctx)
            await ctx.message.add_reaction(tick)
        if not log_channel:
            await Message.EmbedText(
                color=main_color,
                title='Logging was already disabled!',
            ).send(ctx)
            await ctx.message.add_reaction(tick)

    @logs.command(name='enable', help='Enables all the logs, if the logs are disabled.')
    @commands.cooldown(1, 3 , commands.BucketType.member)
    @commands.has_permissions(manage_guild=True)
    async def logs_enable(self, ctx):
        guild_id = str(ctx.guild.id)
        log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        log_channel1 = ctx.guild.system_channel if ctx.guild.system_channel else ctx.guild.text_channels[-1]

        if log_channel:
            await Message.EmbedText(
                color=main_color,
                title='Logging is already enabled!',
            ).send(ctx)
            await ctx.message.add_reaction(tick)

        if not log_channel:
            await self.client.pg_con.execute('INSERT INTO log_channels (guild_id, log_channel) VALUES ($1, $2)', guild_id, str(log_channel1.id))
            log_channel12 = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
            await Message.EmbedText(
                color=main_color,
                title='Successfully enabled logging!',
                description=f'The logs are now set to <#{log_channel12[0]["log_channel"]}>. For more info, type `t-logs`'
            ).send(ctx)
            await ctx.message.add_reaction(tick)

    @logs.command(name='channel', help='Shows which channel is set as the logging channel!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True)
    async def logs_channel(self, ctx, server: discord.Guild = None):
        server = ctx.guild if not server else server
        guild_id = str(server.id)
        log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if log_channel:
            await Message.EmbedText(
                title='Log channel!',
                description=f'The log channel in **{server}** is set to <#{log_channel[0]["log_channel"]}>. For more info, reply with `t-logs`.',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(tick)
        if not log_channel:
            await Message.EmbedText(
                title='Logging is disabled in ' + server.name,
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(cross)


    @logs.command(name='set', help='Sets the log channel')
    @commands.has_permissions(manage_guild=True)
    async def logs_set(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)
        log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if not log_channel:
            await self.client.pg_con.execute('INSERT INTO log_channels (guild_id, log_channel) VALUES ($1, $2)', guild_id,
                                        channel_id)
            await Message.EmbedText(
                color=main_color,
                title='Successfully set the log channel!',
                description=f'Set the log channel to {channel.mention}.'
            ).send(ctx)
            await ctx.message.add_reaction(tick)
        if log_channel:
            await self.client.pg_con.execute('UPDATE log_channels SET log_channel = $1 WHERE guild_id = $2', channel_id, guild_id)
            await Message.EmbedText(
                color=main_color,
                title='Successfully set the log channel!',
                description=f'Set the log channel to {channel.mention}.'
            ).send(ctx)
            await ctx.message.add_reaction('<a:vxtick:745550119436288061>')