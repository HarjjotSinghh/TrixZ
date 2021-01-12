from discord.ext import commands
import discord
from bot import tick, main_color, cross
import datetime
from _Utils import Message
import asyncio

def setup(client):
    client.add_cog(invites(client))

class invites(commands.Cog):
            
    def __init__(self, client : commands.Bot):
        self.client = client
        self.invites1 = {}
        self.client.loop.create_task(self.refresh())
    
    async def refresh(self):
        await self.client.wait_until_ready()
        channel = self.client.get_channel(758741983081922600)
        while True:
            for guild in self.client.guilds:
                # await channel.send(guild.name)
                self.invites1[str(guild.id)] = []
                try:
                    all_invs = await guild.invites()
                except discord.Forbidden:
                    all_invs = []
                for i in all_invs:
                    if all_invs != []:
                        self.invites1[str(guild.id)] += [tuple((str(i.code),str(i.uses)))]
            await asyncio.sleep(130)
            
    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        guild_id = str(member.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT invites_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if fetch:
            if fetch[0]['invites_enabled'] == 'yes':
                channel1 = await self.client.pg_con.fetch("SELECT invites_channel_id FROM invites_channels WHERE guild_id = $1", guild_id)
                channel = await self.client.fetch_channel(int(channel1[0]['invites_channel_id']))
                for invite in await member.guild.invites():
                    if await member.guild.invites() != []:
                        if self.invites1.get(str(member.guild.id)) != []:
                            for i in self.invites1.get(str(member.guild.id)):
                                if str(i[0]) == str(invite.code):
                                    #await channel.send('yes')
                                    if int(invite.uses) > int(i[1]):
                                        uses = 0
                                        realinvite = await self.client.fetch_invite(f'https://discord.gg/{str(invite.code)}')
                                        for j in await member.guild.invites():
                                            if j.inviter == realinvite.inviter:
                                                uses += j.uses
                                        await channel.send(f"🎉 **{member.name + '#' + member.discriminator}** just joined the server.\n📨 Invited by **{realinvite.inviter.name + '#' + realinvite.inviter.discriminator}**. (**{uses}** invites)")
                                        break
                                    
            if fetch[0]['invites_enabled'] == 'no' or fetch[0]['invites_enabled'] == None:
                return
        else:
            return

    @commands.group(name='invites', hidden=True)
    async def invites(self, ctx : commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('inviteshelp'))

    @invites.command(name='doit', help='secret..', hidden=True)
    @commands.is_owner()
    async def invites_doit(self, ctx : commands.Context):
        await ctx.send('doing it..')
        num = 0
        for guild in self.client.guilds:
            guild_id  = str(guild.id)
            await self.client.pg_con.execute("UPDATE all_guilds SET invites_enabled = $1 WHERE guild_id = $2", 'no', guild_id)
            num += 1
        await ctx.send(f'Done. did it in {num} servers.')

    @invites.command(name='setup', help='Sets up the invite channel for the bot to send who invited the member!')
    @commands.has_permissions(manage_channels=True)
    async def invites_setup(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT invites_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        if not fetch:
            await ctx.message.add_reaction(cross)
            return await Message.EmbedText(
                title='Invites are disabled!',
                description='For more info, type `t-invites`.',
                color=main_color
            ).send(ctx)

        if fetch:
            if fetch[0]['invites_enabled'] == 'no' or fetch[0]['invites_enabled'] == None:
                await Message.EmbedText(
                    title='In which channel do you want to send invite logs?',
                    color=main_color
                ).send(ctx)
                def channel_check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and str(m.content).startswith('<') and str(m.content).endswith('>')
                try:
                    channel1 = await self.client.wait_for('message', check=channel_check, timeout=300)
                    channel = await commands.TextChannelConverter().convert(ctx=ctx, argument=channel1.content)
                    await self.client.pg_con.execute('INSERT INTO invites_channels (guild_id, invites_channel_id) VALUES ($1, $2)', guild_id, str(channel.id))
                    await self.client.pg_con.execute('UPDATE all_guilds SET invites_enabled = $1 WHERE guild_id = $2', 'yes', guild_id)
                    await channel1.add_reaction(tick)
                    await Message.EmbedText(
                        title='Success!',
                        description=f'Successfully set the invites log channel to {channel.mention}.\n'
                                    f'For More options, type `t-invites`.',
                        color=main_color
                    ).send(ctx)
                    return

                except asyncio.TimeoutError:
                    await ctx.send('Timeout! You did not reply in time!')
                    return
            if fetch[0]['invites_enabled'] == 'yes':
                await Message.EmbedText(
                    title='Invite channel is already setup!',
                    description='For more info type `t-invites`.',
                    color=main_color
                ).send(ctx)
                return
    
    @invites.command(name='disable', help='Disables the invites tracker in a server, if it is enabled.')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()    
    async def invites_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT invites_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        
        if fetch:
            if fetch[0]['invites_enabled'] == 'yes':
                await self.client.pg_con.execute("UPDATE all_guilds SET invites_enabled = $1 WHERE guild_id = $2", 'no', guild_id)
                await self.client.pg_con.execute("DELETE FROM invites_channels WHERE guild_id = $1", guild_id)
                await ctx.message.add_reaction(tick)
                await Message.EmbedText(title='Success!', description=f'Successfully disabled invite tracker in {ctx.guild.name}.').send(ctx)
                return
            if fetch[0]['invites_enabled'] == 'no' or fetch[0]['invites_enabled'] == None:
                await ctx.message.add_reaction(cross)
                await Message.EmbedText(title='Invite Tracker is already disabled!', color=discord.Color.red()).send(ctx)
                return
        if not fetch:
            return
    
    @invites.command(name="channel", help="Shows which channel is set as the invite tracker channel, if invite tracker is enabled.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def invites_channel(self, ctx):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch('SELECT invites_enabled FROM all_guilds WHERE guild_id = $1', guild_id)
        
        if fetch:
            if fetch[0]['invites_enabled'] == "yes":
                channel1 = await self.client.pg_con.fetch("SELECT invites_channel_id FROM invites_channels WHERE guild_id = $1", guild_id)
                channel  = await self.client.fetch_channel(int(channel1[0]['invites_channel_id']))
                e = discord.Embed(title="📨  Invite Tracker", color=main_color)
                e.add_field(name="Channel", value=f"{channel.mention} - {channel.name}")
                await ctx.send(embed=e)
                return
            if fetch[0]['invites_enabled'] == 'no' or fetch[0]['invites_enabled'] == None:
                await Message.EmbedText(title='Invite Tracker is not setup!', color=main_color, description=f"{ctx.author.mention} For more information, tpye `t-invites`.").send(ctx)
                return
    
    @invites.command(name='show', help='Shows the invites of the member mentioned!')
    async def invites_show(self, ctx : commands.Context, member : discord.Member = None):
        member = ctx.author if not member else member
        all_invites = await ctx.guild.invites()
        uses = 0
        for invite in all_invites:
            if invite.inviter == member:
                uses += invite.uses
        e = discord.Embed(title='📨  Invites', description=f'`{member.name + "#" + member.discriminator}` has `{uses}` invites!', color=main_color).set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.message.add_reaction(tick)
        await ctx.send(embed=e)

    @invites.command(name='top', help='Show the invites leaderboard in the server!')
    async def invites_top(self, ctx : commands.Context):
        invites = {}
        for invite in await ctx.guild.invites():
            if invite in list(invites.keys()):
                invites[str(invite.inviter.name + "#" + invite.inviter.discriminator)] += invite.uses
            else:
                if not invite.inviter.bot:
                    invites[str(invite.inviter.name + "#" + invite.inviter.discriminator)] = invite.uses
        medals = ['🥇', '🥈', '🥉', '🏅', '🏅', '🏅', '🏅', '🏅', '🏅', '🏅']
        desc = ''
        index = 0
        for k, v in sorted(invites.items(), key=lambda x: x[1], reverse=True)[0:10]:
            if int(v) != 0:
                desc += f'`{medals[index]}` `{k}` - `{v}` invite{"s" if int(v) != 1 else ""}\n'
                index += 1

        e = discord.Embed(color=main_color,
                          description=desc,
                          title=f'📨  Top Inviters!')
        e.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

        await ctx.send(embed=e)