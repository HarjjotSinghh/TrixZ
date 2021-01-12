import discord
from discord.ext import commands
from bot import main_color, cross, tick
from _Utils import Message
import asyncio
import wand
from wand.font import Font
from wand.drawing import Drawing
from wand.image import Image
from io import BytesIO
import datetime

def setup(client):
    client.add_cog(welcome(client))

class welcome(commands.Cog):
    """Welcome log commands, mostly available to the mods and admins of the server!"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='welcome')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('welcomehelp'))

    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        guild_id = str(member.guild.id)
        memberc = (member.guild.member_count)
        memberc1 = ''
        if str(memberc).endswith('1'):
            memberc1 += 'st'
        elif str(memberc).endswith('2'):
            memberc1 += 'nd'
        elif str(memberc).endswith('3'):
            memberc1 += 'rd'
        else:
            memberc1 += 'th'
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            return
        if fetch[0]['welcome_log_enabled'] == 'yes':
            channel1 = await self.client.pg_con.fetch('SELECT welcome_log_channel FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            message1 = await self.client.pg_con.fetch('SELECT welcome_log_message FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            message = str(message1[0]['welcome_log_message'])
            channel = self.client.get_channel(int(channel1[0]['welcome_log_channel']))
            url = member.avatar_url_as(format='png', size=512)
            with wand.image.Image(filename='welcome.png') as canvas:
                left, top, width, height = 484, 40, 910, 330
                with Drawing() as context:
                    context.fill_color = 'white'
                    font = Font('Font.ttf', size=65, color=wand.image.Color('white'), antialias=True)
                    context(canvas)
                    canvas.caption(message.replace('\\n', '\n'),
                                   left=left, top=top, width=width, height=height, font=font, gravity='center')
                with wand.image.Image(blob=await url.read()) as av:
                    av.resize(350, 350)
                    with wand.image.Image(width=av.width, height=av.height,
                                          background=wand.image.Color('white')) as mask:
                        with Drawing() as ctx2:
                            ctx2.fill_color = wand.image.Color('black')
                            ctx2.rectangle(
                                left=0,
                                top=0,
                                height=mask.height,
                                width=mask.width,
                                radius=mask.width
                            )
                            ctx2(mask)
                            av.composite_channel('all_channels', mask, 'screen')
                            av.transparent_color(wand.image.Color('#FFF'), alpha=0)
                            canvas.composite(av, left=50, top=38)
                    with BytesIO() as img1:
                        canvas.save(img1)
                        img1.seek(0)
                        wp = await channel.send(file=discord.File(fp=img1, filename='test.png'),
                                           embed=discord.Embed(
                                               title=f'{member.display_name} just joined the server!',
                                               color=main_color,
                                               description=f'{member.mention} you are the **{str(memberc) + memberc1}** member of **{member.guild.name}**!',
                                               timestamp=datetime.datetime.utcnow()
                                           ).set_image(url='attachment://test.png'))
            await channel.send(member.mention, delete_after=0.1)

    @welcome.command(name='setup', help='Starts an interactive setup for setting the welcome log!')
    @commands.has_permissions(manage_guild=True, manage_channels = True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def welcome_setup(self, ctx : commands.Context):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.Embed(
                title='Which channel do you want to be the log channel?',
                color=main_color
            ).send(ctx)
            try:
                channel1 = await self.client.wait_for('message',
                                                  check=lambda x: x.author == ctx.author and x.channel == ctx.channel, timeout=200)
            except asyncio.TimeoutError:
                await ctx.send('Timeout!')
                return
            channel = await commands.TextChannelConverter().convert(ctx=ctx, argument=channel1.content)
            channel_id = str(channel.id)

            await Message.EmbedText(
                title='What custom message do you want in the welcome image? [max. 100 words]',
                color=main_color
            ).send(ctx)
            try:
                message1 = await self.client.wait_for('message', check=lambda x: x.author == ctx.author and x.channel == ctx.channel and len(x.content) < 101)
            except asyncio.TimeoutError:
                await ctx.send('Timeout!')
                return
            custom_message = message1.content
            await self.client.pg_con.execute('INSERT INTO welcome_log_channels (guild_id, welcome_log_channel, welcome_log_message) VALUES ($1, $2, $3)', guild_id, channel_id, custom_message)
            await self.client.pg_con.execute('UPDATE all_guilds SET welcome_log_enabled = $1 WHERE guild_id = $2', 'yes', guild_id)
            await Message.EmbedText(
                title='Successfully Enabled Welcome Logging!',
                description=f'The welcome log channel is set to - {channel.mention}\nCustom message is set to -\n"{custom_message}".\n\n'
                            f'To change the welcome log channel or the custom message, type `t-welcome` for more info on that.',
                color=main_color
            ).send(ctx)

        if fetch[0]['welcome_log_enabled'] == 'yes':
            await Message.EmbedText(
                title=f'The welcome logs are already setup! Fore more info, type `t-welcome`.',
                color=discord.Color.red()
            ).send(ctx)

    @welcome.command(name='disable', help='Disables the welcome logs, if they are currently enabled.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == 'yes':
            await self.client.pg_con.execute('UPDATE all_guilds SET welcome_log_enabled = $1 WHERE guild_id = $2', 'no', guild_id)
            await Message.EmbedText(
                title=f'Successfully disabled welcome logs!',
                color=main_color
            ).send(ctx)
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are already disabled!',
                color=main_color
            ).send(ctx)
            return

    @welcome.command(name='channel', help='Changes the custom welcome message, if the welcome logs are enabled!')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_channel(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1',
                                               guild_id)
        if fetch[0]['welcome_log_enabled'] == 'yes':
            await Message.EmbedText(
                title='What do you want the channel to be? [mention the channel]',
                color=main_color
            ).send(ctx)
            try:
                message1 = await self.client.wait_for('message', check=lambda
                    x: x.author == ctx.author and x.channel == ctx.channel, timeout=200)
                channel = await commands.TextChannelConverter().convert(ctx=ctx, argument=message1.content)
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=10)
                return
            await self.client.pg_con.execute(
                'UPDATE welcome_log_channels SET welcome_log_channel = $1 WHERE guild_id = $2', str(channel.id), guild_id)
            await ctx.send(embed=discord.Embed(
                title=f'Successfully set the new welcome log channel!',
                color=main_color
            ).add_field(
                name='New log channel',
                value=channel.mention,
                inline=False
            ))
            await ctx.message.add_reaction(tick)
            return
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are  disabled in {}'.format(ctx.guild.name),
                color=main_color
            ).send(ctx)
            return

    @welcome.command(name='show', help='Shows weather the welcome logs are turned on/off!', aliases = ['info'])
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def welcome_show(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == 'yes':
            data = await self.client.pg_con.fetch('SELECT * FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            e = discord.Embed(color=main_color)
            e.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            e.add_field(
                name='Welcome log enabled?',
                value=f'{tick} Yes!',
                inline=False
            )
            e.add_field(
                name='Welcome log channel',
                value='<#' + str(data[0]['welcome_log_channel']) + '>',
                inline=False
            )
            e.add_field(
                name='Welcome log message',
                value=str(data[0]['welcome_log_message']),
                inline=False
            )
            e.set_thumbnail(url=ctx.guild.icon_url)
            await ctx.send(embed=e)
            return
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are disabled.',
                description='To enable welcome logs type `t-welcome setup`.',
                color=main_color
            ).send(ctx)
            return

    @welcome.command(name='message', help='Changes the custom welcome message, if the welcome logs are enabled!')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_message(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == 'yes':
            await Message.EmbedText(
                title='What do you want the message to be? [max. 100 characters]',
                color=main_color
            ).send(ctx)
            try:
                message1 = await self.client.wait_for('message', check=lambda x: x.author == ctx.author and x.channel == ctx.channel and len(x.content) < 101, timeout=200)
                new = message1.content
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=10)
                return
            await self.client.pg_con.execute('UPDATE welcome_log_channels SET welcome_log_message = $1 WHERE guild_id = $2', new, guild_id)
            await ctx.send(embed=discord.Embed(
                title=f'Successfully set the new welcome log message!',
                color=main_color
            ).add_field(
                name='New Message',
                value=new,
                inline=False
            ))
            await ctx.message.add_reaction(tick)
            return
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are  disabled in {}'.format(ctx.guild.name),
                color=main_color
            ).send(ctx)
            return

    @welcome.command(name='channelshow', help='Shows the current channel which is set as the welcome log channel.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_channelshow(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are disabled.',
                description='To enable welcome logs type `t-welcome setup`.',
                color=main_color
            ).send(ctx)
            return
        if fetch[0]['welcome_log_enabled'] == 'yes':
            channel_fetch = await self.client.pg_con.fetch('SELECT welcome_log_channel FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            channel = self.client.get_channel(int(channel_fetch[0]['welcome_log_channel']))
            await ctx.send(embed=discord.Embed(
                color=main_color
            ).add_field(
                name='Welcome log channel',
                value=channel.mention
            ))
            return

    @welcome.command(name='messageshow', help='Shows the current message which is set as the welcome log message.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_messageshow(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1',
                                               guild_id)
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are disabled.',
                description='To enable welcome logs type `t-welcome setup`.',
                color=main_color
            ).send(ctx)
            return
        if fetch[0]['welcome_log_enabled'] == 'yes':
            channel_fetch = await self.client.pg_con.fetch('SELECT welcome_log_message FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            message = channel_fetch[0]['welcome_log_message']
            await ctx.send(embed=discord.Embed(
                color=main_color
            ).add_field(
                name='Welcome log message',
                value=message
            ))
            return

    @welcome.command(name='example', help='Shows an example welcome image which is sent when a member joins!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_example(self, ctx, member : discord.Member, *, message: str):
        url = member.avatar_url_as(format='png', size=512)
        with wand.image.Image(filename='welcome.png') as canvas:
            left, top, width, height = 484, 40, 910, 330
            with Drawing() as context:
                context.fill_color = 'white'
                font = Font('Font.ttf', size=65, color=wand.image.Color('white'), antialias=True)
                context(canvas)
                canvas.caption(message.replace('\\n', '\n'),
                               left=left, top=top, width=width, height=height, font=font, gravity='center')
            with wand.image.Image(blob=await url.read()) as av:
                av.resize(350, 350)
                with wand.image.Image(width=av.width, height=av.height,
                                      background=wand.image.Color('white')) as mask:
                    with Drawing() as ctx2:
                        ctx2.fill_color = wand.image.Color('black')
                        ctx2.rectangle(
                            left=0,
                            top=0,
                            height=mask.height,
                            width=mask.width,
                            radius=mask.width
                        )
                        ctx2(mask)
                        av.composite_channel('all_channels', mask, 'screen')
                        av.transparent_color(wand.image.Color('#FFF'), alpha=0)
                        canvas.composite(av, left=50, top=38)
                with BytesIO() as img1:
                    canvas.save(img1)
                    img1.seek(0)
                    wp = await ctx.send(file=discord.File(fp=img1, filename='test.png'),
                                            embed=discord.Embed(
                                                title=f'{member.display_name} just joined the server!',
                                                color=main_color,
                                                timestamp=datetime.datetime.utcnow()
                                            ).set_image(url='attachment://test.png'))

    @welcome.command(name='preview', help='Shows an preview welcome image which is sent when a member joins!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def welcome_preview(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1',
                                               guild_id)
        if fetch[0]['welcome_log_enabled'] == 'yes':
            message1 = await self.client.pg_con.fetch('SELECT welcome_log_message FROM welcome_log_channels WHERE guild_id = $1', guild_id)
            message = message1[0]["welcome_log_message"]
            await ctx.invoke(self.client.get_command('welcome example'), member=ctx.author, message=message)
            return
        if fetch[0]['welcome_log_enabled'] == None or fetch[0]['welcome_log_enabled'] == 'no':
            await Message.EmbedText(
                title='Welcome logs are disabled.',
                description='To enable welcome logs type `t-welcome setup`.',
                color=main_color
            ).send(ctx)
            return