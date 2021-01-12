from discord.ext import commands
import discord, asyncio
from _Utils import Message
from bot import main_color, tick, cross, support_server_url

def setup(client):
    client.add_cog(automod(client))

class automod(commands.Cog):

    """Auto-Mod commands which assist the moderators and admins of the server!"""

    def __init__(self, client):
        self.client = client

    @commands.group(name='automod', hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('automodhelp'))

    @automod.command(name='features', help='Shows all the features which TrixZ AutoMod provides!')
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    async def automod_features(self, ctx):
        desc = "TrixZ AutoMod provides the following features, as of now.\n\n" \
               "• **Anti-Spam**: Automatically deletes any spam messages sent by the users which do not have the '**Manage Server**' permission.\n\n" \
               "• **Anti-Invites**: Automatically deletes any invites sent by the users which do not have the '**Manage Server**' permission.\n\n" \
               "• **Anti-Hoisting**: Automatically changes the nicknames of users whose name/nickname starts with `!` or **any other unicode character** which brings the user at the **top** of the member list.\n\n" \
               "• **Anti-MassMentions**: Automatically deletes the message with more than **4 user/role mentions** and also mutes the member for **60 seconds**.\n\n" \
               "• **Anti-Everyone**: Automatically deletes the message with `@here` or `@everyone` ping and also mutes the member for **30 seconds**.\n\n" \
               "Still not **enough** features? Many more coming in the near future!\n" \
               f"Want to make some suggestions? Join [this server]({support_server_url}) to make your own suggestions!"
        await ctx.message.add_reaction(tick)
        await ctx.send(embed=discord.Embed(
            title='💎 TrixZ AutoMod',
            description=desc,
            color=main_color
        ))

    @automod.command(name='show', help='Shows whether the Auto-Mod is turned off/on in the server!')
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def automod_show(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        yesorno = ""
        if fetch:
            if fetch[0]['automod_enabled'] == None:
                yesorno += f"{cross} Auto-Mod is disabled in {ctx.guild.name}."
            if fetch[0]['automod_enabled'] == 'yes':
                yesorno += f"{tick} Auto-Mod is enabled in {ctx.guild.name}."
            if fetch[0]['automod_enabled'] == 'no':
                yesorno += f"{cross} Auto-Mod is disabled in {ctx.guild.name}."
        if not fetch:
            yesorno += f"{cross} Auto-Mod is disabled in {ctx.guild.name}."
        e = discord.Embed(title=yesorno, color=main_color)
        await ctx.send(embed=e)

    @automod.command(name='enable', help='Enables Auto-Mod!', aliases=['on'])
    @commands.has_permissions(manage_channels=True, manage_guild=True, manage_messages=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def auto_mod_enable(self, ctx):
        guild_id = str(ctx.guild.id)
        await Message.EmbedText(
            title='Enable TrixZ AutoMod? [Y/N]',
            color=main_color,
            delete_after=60
        ).send(ctx)
        def check1(m):
            return m.content.lower() in ('y', 'n') and m.author == ctx.author and m.channel == ctx.channel
        yesorno = await self.client.wait_for('message', check = check1, timeout=60)
        if yesorno.content.lower() == 'y':
            fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
            if fetch[0]['automod_enabled'] == None:
                await self.client.pg_con.execute('UPDATE all_guilds SET automod_enabled = $1 WHERE guild_id = $2', 'yes', guild_id)
                await Message.EmbedText(
                    title='Auto Mod is now enabled!',
                    color=main_color
                ).send(ctx)
                return
            if fetch[0]['automod_enabled'] == 'no':
                await self.client.pg_con.execute('UPDATE all_guilds SET automod_enabled = $1 WHERE guild_id = $2', 'yes', guild_id)
                await ctx.message.add_reaction(tick)
                await Message.EmbedText(
                    title=f'Successfully enabled TrixZ AutoMod!',
                    color=main_color
                ).send(ctx)
                return
        if yesorno.content.lower() == 'n':
            await Message.EmbedText(
                title='Ok... Sad...',
                color=main_color,
                delete_after=5
            ).send(ctx)
            return

    @automod.command(name='disable', help='Disables Auto-Mod!', aliases=['off'])
    @commands.has_permissions(manage_channels=True, manage_guild=True, manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    async def auto_mod_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        await Message.EmbedText(
            title='Disable TrixZ AutoMod? [Y/N]',
            color=main_color,
            delete_after=60
        ).send(ctx)
        def check1(m):
            return m.content in ('Y', 'N') and m.author == ctx.author and m.channel == ctx.channel

        yesorno = await self.client.wait_for('message', check=check1, timeout=60)
        if yesorno.content == 'Y':
            fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1',
                                                   guild_id)
            if fetch[0]['automod_enabled'] == None or fetch[0]['automod_enabled'] == 'no':
                await self.client.pg_con.execute('UPDATE all_guilds SET automod_enabled = $1 WHERE guild_id = $2', 'no',guild_id)
                await ctx.message.add_reaction(tick)
                await Message.EmbedText(
                    title='Successfully disabled TrixZ AutoMod!',
                    color=main_color
                ).send(ctx)
                return
            if fetch[0]['automod_enabled'] == 'yes':
                await self.client.pg_con.execute('UPDATE all_guilds SET automod_enabled = $1 WHERE guild_id = $2', 'no', guild_id)
                await ctx.message.add_reaction(tick)
                await Message.EmbedText(
                    title=f'Successfully disabled TrixZ AutoMod!',
                    color=main_color
                ).send(ctx)
                return
        if yesorno.content == 'N':
            await Message.EmbedText(
                title='Ok... Sad...',
                color=main_color,
                delete_after=5
            ).send(ctx)

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.guild:
            content = message.content
            guild_id = str(message.guild.id)
            if message.guild is not None:
                fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
                if fetch is not None:
                    if fetch[0]['automod_enabled'] == 'no' or fetch[0]['automod_enabled'] == None:
                        return
                    if fetch[0]['automod_enabled'] == 'yes':
                        if not message.embeds and not message.author.bot:
                            if not message.author.guild_permissions.manage_guild:
                                ctx = await self.client.get_context(message)
                                if 'discord.gg/' in content or 'discord.com/invite' in content:
                                    await message.delete()
                                    await Message.EmbedText(
                                        color=discord.Color.red(),
                                        title=f'<a:trixzcross:745553761598046280> No invite links, {message.author.name}',
                                        delete_after=10
                                    ).send(message.channel)
                                    return
                                try:
                                    repeated_message = await self.client.wait_for('message', check=lambda x: x.author == message.author and x.channel == message.channel, timeout=0.7)
                                    if repeated_message.content == message.content:
                                        await repeated_message.delete()
                                        try:
                                            await message.delete()
                                        except:
                                            pass
                                        await Message.EmbedText(
                                            title=f'{cross} {message.author.name},  Please do not spam!',
                                            color=discord.Color.red(),
                                            delete_after=10
                                        ).send(message.channel)
                                        return
                                except asyncio.TimeoutError:
                                    pass
                                if len(message.mentions) > 4 or len(message.role_mentions) > 4 or (len(message.mentions) + len(message.role_mentions)) > 4:
                                    await message.delete()
                                    await Message.EmbedText(
                                        title=f'{cross} {message.author.name},  Please do not mass mention! You have been muted for 60 seconds.',
                                        color=discord.Color.red(),
                                        delete_after=10
                                    ).send(message.channel)
                                    await ctx.invoke(self.client.get_command('mute'), member=message.author, duration='60')
                                    return
                                if '@here' in message.content or '@everyone' in message.content:
                                    await message.delete()
                                    await Message.EmbedText(
                                        title=f'{cross} {message.author.name},  Please do not mention `@here`/`@eveyone`! You have been muted for 30 seconds.',
                                        color=discord.Color.red(),
                                        delete_after=10
                                    ).send(message.channel)
                                    await ctx.invoke(
                                        self.client.get_command('mute'), member=message.author, duration='30')
                                    return

                if fetch is None:
                    return

    @commands.Cog.listener()
    async def on_message_edit(self, before : discord.Message, after : discord.Message):
        if before.guild:
            content = after.content
            guild_id = str(before.guild.id)
            if before.guild is not None:
                fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
                if fetch is not None:
                    if fetch[0]['automod_enabled'] == 'no' or fetch[0]['automod_enabled'] == None:
                        return
                    if fetch[0]['automod_enabled'] == 'yes':
                        if not after.embeds and not after.author.bot:
                            if not after.author.guild_permissions.manage_guild:
                                if 'discord.gg/' in content or 'discord.com/invite' in content:
                                    await after.delete()
                                    await Message.EmbedText(
                                        color=discord.Color.red(),
                                        title=f'<a:trixzcross:745553761598046280> No invite links, {after.author.name}',
                                        delete_after=10
                                    ).send(after.channel)
                                    return

    @commands.Cog.listener()
    async def on_member_update(self, before : discord.Member, after: discord.Member):
        guild_id = str(before.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT automod_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch is not None:
            if fetch[0]['automod_enabled'] == 'no' or fetch[0]['automod_enabled'] == None:
                return
            if fetch[0]['automod_enabled'] == 'yes':
                if before.nick != after.nick:
                    if not after.guild_permissions.manage_channels:
                        r1 = open('all.txt', encoding='utf8')
                        r = r1.read()
                        if after.nick is not None:
                            if after.nick.startswith(tuple(r)):
                                await after.edit(nick='dont hoist', reason='TrixZ AutoMod enabled.')
                                return