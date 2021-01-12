import discord
from discord.ext import commands
from bot import tick, cross, main_color, main_emoji
from _Utils import Message
import asyncio

def setup(client):
    client.add_cog(membercount(client))

class membercount(commands.Cog):
    """Server's Member-Count commands which are only accessible to the administrators and owners of the server!"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        sum = 0
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        await asyncio.sleep(15)
        if channel_id:
            channel = await self.client.fetch_channel(channel_id=int(channel_id[0]['membercount_channel_id']))
            if not channel:
                admins = discord.utils.get(member.guild.roles, name="Admin")
                log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
                if not log_channel:
                    await self.client.pg_con.execute("DELETE FROM member_count_channels WHERE guild_id = $1", guild_id)
                    return
            if channel:
                await asyncio.sleep(5)
                sum += member.guild.member_count
                channel_name = str(channel.name).split('-')
                try:
                    await channel.edit(name=f'{str(channel_name[0])}- {sum}')
                except:
                    await channel.edit(name=f'{str(channel_name[0]).replace(" ", "")} - {sum}')
        if not channel_id:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        sum = 0
        await asyncio.sleep(10)
        if channel_id:
            channel = self.client.get_channel(int(channel_id[0]['membercount_channel_id']))
            if not channel:
                admins = discord.utils.get(member.guild.roles, name="Admin")
                log_channel = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
                if log_channel:
                    log_channel = self.client.get_channel(int(log_channel[0]["log_channel"]))
                if not log_channel:
                    log_channel = member.guild.system_channel if member.guild.system_channel else member.guild.text_channels[0]
                await log_channel.send(f'{admins.mention if admins else ""} I could not find the member count channel! Please use `t-membercount reset` to reset it and set it up again.')
                return
            if channel:
                sum += member.guild.member_count
                await asyncio.sleep(2)
                channel_name = str(channel.name).split('-')
                try:
                    await channel.edit(name=f'{channel_name[0]}- {sum}')
                except:
                    await channel.edit(name=f'{str(channel_name[0]).replace(" ", "")} - {sum}')
        if not channel_id:
            return

    @commands.group(name='membercount', hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def membercount(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('mcounthelp'), arg='membercount')
    
    @membercount.command(name="reset", help="Resets the current membercount settings!")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def membercount_reset(self, ctx : commands.Context):
        guild_id = str(ctx.guild.id)
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        if channel_id:
            await self.client.pg_con.execute("DELETE FROM member_count_channels WHERE guild_id = $1", guild_id)
            await Message.EmbedText(
                    title=f"{tick} Success",
                    color=main_color,
                    description=f"The Member-Count channel has been reset successfully, to set it up again, you can use `t-membercount setup`."
                ).send(ctx)
            return
        if not channel_id:
            await Message.EmbedText(
                    title=f"Member count is not setup!",
                    color=discord.Color.red(),
                    description=f"Please use `t-membercount setup` to set it up!"
                ).send(ctx)
            return

    @membercount.command(name='setup', help='Starts an interactive member count setup for your server!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def setup(self, ctx):
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        guild_id = str(ctx.guild.id)
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        if not channel_id:
            msg = f'{ctx.author.mention} What do you want to name the member count channel?'
            await ctx.send(msg)
            name_wait = await self.client.wait_for('message', timeout=120, check=check1)
            name = str(name_wait.content) + f' - {ctx.guild.member_count}'
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=False,)
            }
            created_channel = await ctx.guild.create_voice_channel(name=name, category=None, reason=f"As per {ctx.author.name}'s instructions :)", overwrites=overwrites)
            await self.client.pg_con.execute('INSERT INTO member_count_channels (guild_id, membercount_channel_id, membercount_channel_name) VALUES ($1, $2, $3)', guild_id, str(created_channel.id), str(created_channel.name))
            await name_wait.add_reaction(tick)
            await Message.EmbedText(
                title='Success!',
                description=f'Successfully set the member-count channel! The member count will update 15 seconds after a member has left/joined the server!',
                color=main_color
            ).send(ctx)
        else:
            await Message.EmbedText(
                title='Member-count channel is already set-up!',
                description='Type `t-help membercount` for more info.',
                color=main_color
            ).send(ctx)

    @membercount.command(name='rename', help='Renames the current member-count channel!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def rename(self, ctx):
        def check1(m):
            return m.author == ctx.author and m.channel == ctx.channel
        guild_id = str(ctx.guild.id)
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        if not channel_id:
            await Message.EmbedText(
                title='Member-count channel is not setup!',
                description=f'{ctx.author.mention}, To setup a member-count channel on the server, type `t-membercpunt setup`.\nFor more info type `t-help membercount`.',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(cross)
        if channel_id:
            channel = self.client.get_channel(int(channel_id[0]['membercount_channel_id']))
            await Message.EmbedText(
                title=f'What do you want to rename the channel to?',
                description=f'{ctx.author.mention}, Reply with the new name for the member count channel (without the "-").',
                color=main_color,
                fields=[
                    {'name': 'Current name', 'value': f"{channel.name}", 'inline': False}
                ]
            ).send(ctx)
            wait = await self.client.wait_for('message', timeout=180, check=check1)
            new_name = str(wait.content)
            await Message.EmbedText(
                title=f'{main_emoji} ' + 'Success!',
                description=f'Successfully set the new channel name to - **{new_name}**!',
                color=main_color
            ).send(ctx)
            await self.client.pg_con.execute('UPDATE member_count_channels SET membercount_channel_name = $1 WHERE guild_id = $2', new_name, guild_id)
            new_channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
            new_channel = self.client.get_channel(int(new_channel_id[0]['membercount_channel_id']))
            await wait.add_reaction(tick)
            count = str(ctx.guild.member_count)
            await asyncio.sleep(5)
            await new_channel.edit(name=new_name + ' - ' + count)

    @membercount.command(name='channel', help='Tells which channel is currently set as the member-count channel!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def channel(self, ctx):
        guild_id = str(ctx.guild.id)
        channel_id = await self.client.pg_con.fetch('SELECT membercount_channel_id FROM member_count_channels WHERE guild_id = $1', guild_id)
        if channel_id:
            channel = self.client.get_channel(int(channel_id[0]["membercount_channel_id"]))
            await Message.EmbedText(
                title=f'Member-count channel in {ctx.guild.name}',
                description=f'The member-count channel in **{ctx.guild.name}** is set to 🔊 **{channel.name}**',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(tick)

        if not channel_id:
            await Message.EmbedText(
                title='Member-count channel is not setup!',
                description=f'{ctx.author.mention}, To setup a member-count channel on the server, type `t-membercount setup`.\nFor more info type `t-help membercount`.',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(cross)
