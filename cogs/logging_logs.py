import discord
from discord import Webhook, AsyncWebhookAdapter, RequestsWebhookAdapter
from discord.ext import commands
from bot import main_color
main_emoji = "💎"
tick = "✅"
cross = "❌"
username = 'Trixz Logging'
from _Utils import Message
import asyncio
import datetime

av = "https://cdn.discordapp.com/avatars/716813265312940094/75ecee48cff516dc957c7919c0048067.webp?size=512"

def setup(client):
    client.add_cog(logging(client))

class logging(commands.Cog):

    def __init__(self, client : commands.Bot):
        self.client = client

    async def get_trixz_webhook(self, channel: discord.TextChannel):
        try:
            if channel:
                for i in await channel.webhooks():
                    if i.user == self.client.user:
                        return i
            else:
                return None
        except discord.Forbidden:
            return None
        else:
            try:
                create: discord.Webhook = await channel.create_webhook(name=username,
                                                                       reason=f'TrixZ')
                return create
            except discord.Forbidden:
                return None


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild_id = str(channel.guild.id)
        guild = channel.guild
        embed = discord.Embed(description=f"{main_emoji} New channel created.",
                              color=main_color,
                              timestamp=datetime.datetime.utcnow())
        embed.add_field(
            name='Channel name',
            value='`' + channel.name + '`',
            inline=False,
        ).add_field(
            name='Channel category',
            value='`' + channel.category.name + "`" if channel.category else 'No Category',
            inline=False
        ).set_thumbnail(
            url=guild.icon_url
        )
        embed.set_author(name=guild.name, icon_url=guild.icon_url)
        yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if yes:
            try:
                logChannel = await self.client.fetch_channel(channel_id=int(yes[0]["log_channel"]))
            except:
                logChannel = None
            if logChannel:
                webhook = await self.get_trixz_webhook(channel=logChannel)
                if webhook:
                    await webhook.send(embed=embed, username=username, avatar_url=av)
                    return
                else:
                    return
        else:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild:
            guild = before.guild
            embed = discord.Embed(
                description=f"{main_emoji} **{before.author.mention}** edited a message in  **{before.channel.mention}**.",
                color=main_color,
                timestamp=datetime.datetime.utcnow())
            embed.set_author(name=guild.name, icon_url=guild.icon_url) \
                .add_field(
                name='Before',
                value=('```' + before.content + '```') if not '```' in before.content else before.content,
                inline=False
            ).add_field(
                name='After',
                value=('```' + after.content + '```') if not '```' in after.content else after.content,
                inline=False)
            embed.set_thumbnail(url=after.author.avatar_url)
            guild_id = str(before.guild.id)
            yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
            if yes:
                try:
                    logChannel = await self.client.fetch_channel(channel_id=int(yes[0]["log_channel"]))
                except:
                    logChannel = None
                webhook = await self.get_trixz_webhook(channel=logChannel)
                if logChannel and webhook:
                    if before.author.bot: return
                    if before.embeds: return
                    if "https://" in before.content: return
                    await webhook.send(embed=embed, username=username, avatar_url=av)
                    return
            else:
                return

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild:
            # await asyncio.sleep(0.5)
            guild_id = str(message.guild.id)
            yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
            if yes:
                guild = message.guild
                embed = discord.Embed(
                    description=f"{main_emoji} Message sent by **{message.author.mention}** deleted in **{message.channel.mention}**.",
                    color=main_color,
                    timestamp=datetime.datetime.utcnow())
                embed.set_author(name=guild.name, icon_url=guild.icon_url) \
                    .add_field(
                    name='Message content',
                    value=message.content,
                    inline=False
                )
                embed.set_thumbnail(url=message.author.avatar_url)
                if message.author == self.client.user:
                    return
                if message.author.bot:
                    return
                else:
                    try:
                        logChannel = await self.client.fetch_channel(channel_id=int(yes[0]["log_channel"]))
                    except:
                        logChannel = None
                    webhook = await self.get_trixz_webhook(channel=logChannel)
                    if logChannel and webhook:
                        await webhook.send(embed=embed, username=username, avatar_url=av)
                        return
            else:
                return
        else:
            return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        guild_id = str(guild.id)
        yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        # await asyncio.sleep(0.5)
        if yes:
            log_channel = self.client.get_channel(int(yes[0]['log_channel']))
            try:
                create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                create2 = await self.client.fetch_webhook(create.id)
                embed = discord.Embed(description=f"{main_emoji} A role was deleted.", color=main_color,
                        timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=guild.icon_url).set_author(name=guild.name, icon_url=guild.icon_url)
                embed.add_field(
                    name='Name',
                    value=role.name,
                    inline=False
                )
                await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)

                await create2.delete()
                return
            except:
                for webhook in await log_channel.webhooks():
                    await webhook.delete()
                    return
        else:
            return

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        before_name = before.name
        after_name = after.name
        guild = before.guild
        guild_id = str(guild.id)
        yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if not yes:
            return
        if yes:
            log_channel = self.client.get_channel(int(yes[0]['log_channel']))
            if before_name != after_name:
                try:
                    create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                    create2 = await self.client.fetch_webhook(create.id)
                    embed = discord.Embed(color=main_color,
                                  description=f"{main_emoji} **{after.mention}**'s name was changed.",
                        timestamp=datetime.datetime.utcnow())
                    embed.add_field(
                        name='Before',
                        value=before.name,
                        inline=False
                    ).add_field(
                        name='After',
                        value=after.name,
                        inline=False
                    )
                    embed.set_author(icon_url=before.guild.icon_url, name=before.guild.name)
                    embed.set_thumbnail(url=before.guild.icon_url)
                    await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)

                    await create2.delete()
                    return
                except:
                    for webhook in await log_channel.webhooks():
                        await webhook.delete()
                        return
            else:
                return
        else:
            return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        guild = role.guild
        guild_id = str(guild.id)
        yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        # # await asyncio.sleep(0.5)
        if yes:
            log_channel = self.client.get_channel(int(yes[0]['log_channel']))
            try:
                create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                create2 = await self.client.fetch_webhook(create.id)
                embed = discord.Embed(title=f"{guild.name}", description=f"{main_emoji} New role created.",
                                      color=main_color,
                        timestamp=datetime.datetime.utcnow())
                embed.add_field(
                    name='Role name',
                    value= role.name +' - '+ role.mention,
                    inline=False
                )
                embed.set_author(name=guild.name, icon_url=guild.icon_url)
                embed.set_thumbnail(url=guild.icon_url)
                await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)

                await create2.delete()
                return
            except:
                for webhook in await log_channel.webhooks():
                    await webhook.delete()
                    return
        else:
            return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = before.guild
        guild_id = str(guild.id)
        yes = await self.client.pg_con.fetch('SELECT log_channel FROM log_channels WHERE guild_id = $1', guild_id)
        if yes:
            log_channel = self.client.get_channel(int(yes[0]['log_channel']))
            before_roles = before.roles
            after_roles = after.roles
            guild = before.guild
            new_roles = []
            new_roles_1 = []
            if before.nick != after.nick:
                try:
                    create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                    create2 = await self.client.fetch_webhook(create.id)
                    embed = discord.Embed(color=before.guild.me.top_role.color,
                                          timestamp=datetime.datetime.utcnow(),
                                          description=f"{main_emoji} **{before.mention}**'s nickname was changed.")
                    embed.add_field(
                        name='Before',
                        value=before.nick if before.nick else before.name,
                        inline=False
                    ).add_field(
                        name='After',
                        value=after.nick if after.nick else after.name,
                        inline=False
                    )
                    embed.set_thumbnail(url=before.avatar_url)
                    embed.set_author(icon_url=before.avatar_url, name=before.name)
                    await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)
                    await create2.delete()
                    return
                except:
                    for webhook in await log_channel.webhooks():
                        await webhook.delete()
                        return
            for role in before_roles:
                if role not in after_roles:
                    new_roles_1.append(role)
            for role in after_roles:
                if role not in before_roles:
                    new_roles.append(role)
            if len(before_roles) < len(after_roles):
                try:
                    create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                    create2 = await self.client.fetch_webhook(create.id)
                    embed = discord.Embed(color=main_color, description=f'**{before.mention}** roles have been updated.',
                        timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=before.avatar_url)
                    embed.set_author(icon_url=before.avatar_url, name=before.name)
                    embed.add_field(
                        name=f'{tick} Role added',
                        value=new_roles[0].mention
                    )
                    await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)

                    await create2.delete()
                    return
                except:
                    for webhook in await log_channel.webhooks():
                        await webhook.delete()
                        return
            if len(after_roles) < len(before_roles):
                try:
                    create = await log_channel.create_webhook(name='TrixZ Logging 💎', reason=f'TrixZ Logging Enabled.')
                    create2 = await self.client.fetch_webhook(create.id)
                    embed = discord.Embed(color=main_color,
                                          description=f'**{before.mention}** roles have been updated.',
                        timestamp=datetime.datetime.utcnow())
                    embed.add_field(
                        name=f'{cross} Role removed',
                        value=new_roles_1[0].mention
                    )
                    embed.set_thumbnail(url=before.avatar_url)
                    embed.set_author(icon_url=before.avatar_url, name=before.name)
                    await create2.send(embed=embed, username='TrixZ 💎', avatar_url=av)

                    await create2.delete()
                except:
                    for webhook in await log_channel.webhooks():
                        await webhook.delete()
                        return
            else:
                return
        else:
            return