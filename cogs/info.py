import discord
from discord.ext import commands
from discord import Embed
import wikipedia
import asyncio
import textwrap
from _Utils import Message, Nullify
from urllib.request import urlopen
from bot import main_emoji, cross, tick, main_color
import math

class Picker:
	def __init__(self, **kwargs):
		self.client = kwargs.get('client', None)
		self.list = kwargs.get("list", [])
		self.title = kwargs.get("title", None)
		self.timeout = kwargs.get("timeout", 60)
		self.ctx = kwargs.get("ctx", None)
		self.message = kwargs.get("message", None)  # message to edit
		self.self_message = None
		self.max = 10  # Don't set programmatically - as we don't want this overridden
		self.reactions = ["🛑"]

	async def _add_reactions(self, message, react_list):
		for r in react_list:
			await message.add_reaction(r)

	async def _remove_reactions(self, react_list=[]):
		# Try to remove all reactions - if that fails, iterate and remove our own
		try:
			await self.self_message.clear_reactions()
		except:
			pass
			# The following "works", but is super slow - and if we can't clear
			# all reactions, it's probably just best to leave them there and bail.
			'''for r in react_list:
                await message.remove_reaction(r,message.author)'''

	async def pick(self):
		# This actually brings up the pick list and handles the nonsense
		# Returns a tuple of (return_code, message)
		# The return code is -1 for cancel, -2 for timeout, -3 for error, 0+ is index
		# Let's check our prerequisites first
		if self.ctx == None or not len(self.list) or len(self.list) > self.max:
			return (-3, None)
		msg = ""
		if self.title:
			msg += self.title + "\n"
		msg += "```c\n"
		# Show our list items
		current = 0
		# current_reactions = [self.reactions[0]]
		current_reactions = []
		for item in self.list:
			current += 1
			current_number = current if current < 10 else 0
			current_reactions.append("{}\N{COMBINING ENCLOSING KEYCAP}".format(current_number))
			msg += "{}. {}\n".format(current, item)
		msg += "```"
		# Add the stop reaction
		current_reactions.append(self.reactions[0])
		if self.message:
			self.self_message = self.message
			await self.self_message.edit(content=msg, embed=None)
		else:
			self.self_message = await self.ctx.send(msg)
		# Add our reactions
		await self._add_reactions(self.self_message, current_reactions)

		# Now we would wait...
		def check(reaction, user):
			return reaction.message.id == self.self_message.id and user == self.ctx.author and str(
				reaction.emoji) in current_reactions

		try:
			reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
		except:
			# Didn't get a reaction
			await self._remove_reactions(current_reactions)
			return (-2, self.self_message)

		await self._remove_reactions(current_reactions)
		# Get the adjusted index
		ind = current_reactions.index(str(reaction.emoji))
		if ind == len(current_reactions) - 1:
			ind = -1
		return (ind, self.self_message)

class PagePicker(Picker):

    def __init__(self, **kwargs):
        Picker.__init__(self, **kwargs)
        self.max = kwargs.get("max",10)
        self.max = 1 if self.max < 1 else 10 if self.max > 10 else self.max
        self.reactions = ["⏪","◀","▶","⏩","🔢","🛑"]
        self.url = kwargs.get("url",None)

    def _get_page_contents(self, page_number):
        start = self.max*page_number
        return self.list[start:start+self.max]

    async def pick(self):
        if self.ctx == None or not len(self.list):
            return (-3, None)
        page  = 0
        pages = int(math.ceil(len(self.list)/self.max))
        embed = {
            "title":self.title,
            "url":self.url,
            "description":self.message,
            "pm_after":25,
            "fields":self._get_page_contents(page),
            "footer":"Page {} of {}".format(page+1,pages)
        }
        if self.message:
            self.self_message = self.message
            await Message.Embed(**embed, color=main_color).edit(self.ctx, self.message)
        else:
            self.self_message = await Message.Embed(**embed).send(self.ctx)
        if pages <= 1:
            return (0,self.self_message)
        await self._add_reactions(self.self_message, self.reactions)
        def check(reaction, user):
            return reaction.message.id == self.self_message.id and user == self.ctx.author and str(reaction.emoji) in self.reactions
        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
            except:
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            ind = self.reactions.index(str(reaction.emoji))
            if ind == 5:
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            page = 0 if ind==0 else page-1 if ind==1 else page+1 if ind==2 else pages if ind==3 else page
            if ind == 4:
                page_instruction = await self.ctx.send("Type the number of that page to go to from {} to {}.".format(1,pages))
                def check_page(message):
                    try:
                        num = int(message.content)
                    except:
                        return False
                    return message.channel == self.self_message.channel and user == message.author
                try:
                    page_message = await self.client.wait_for('message', timeout=self.timeout, check=check_page)
                    page = int(page_message.content)-1
                except asyncio.TimeoutError as e:
                    print(e)
                    await page_message.clear_reactions()
                    pass
            page = 0 if page < 0 else pages-1 if page > pages-1 else page
            embed["fields"] = self._get_page_contents(page)
            embed["footer"] = "Page {} of {}".format(page+1,pages)
            await Message.Embed(**embed).edit(self.ctx, self.self_message)
        await self._remove_reactions(self.reactions)
        return (page, self.self_message)

from bot import cross,tick, documentation_url
import datetime

offline_emoji = "<:vxoffline:753484505653706752>"
online_emoji = "<:vxonline:753484504701730929>"
dnd_emoji = "<:vxdnd:753484505477808188>"
idle_emoji = "<:vxidle:753484505515556874>"

class info(commands.Cog):
    """Informative commands which are accessible to all members of the server!"""

    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.command(name="avatar", help="Sends the pfp of the user mentioned.", aliases=['profilepic', 'pfp', 'av'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def avatar(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(color=main_color, title="Avatar")
        png = member.avatar_url_as(format="png", size=1024)
        jpg = member.avatar_url_as(format="jpg", size=1024)
        webp = member.avatar_url_as(format="webp", size=1024)
        embed.description = f"[`png`]({png}) | [`jpg`]({jpg}) | [`webp`]({webp})"
        embed.set_image(url=member.avatar_url)
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", help="Sends the info of the user mentioned.", aliases=['user'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def userinfo(self, ctx, user: discord.Member = None, ):
        user = ctx.author if not user else user
        all_flags = user.public_flags.all()

        async with ctx.channel.typing():
            await ctx.send(
                embed=discord.Embed(
                    color=main_color,
                ).set_author(
                    name=user.name + '#' + user.discriminator,
                    icon_url=user.avatar_url
                ).add_field(
                    name='📇 ID',
                    value=user.id
                    , inline=True
                ).add_field(
                    name='🕗 Created at',
                    value=user.created_at.strftime("%A, %d %B %Y at %I:%M:%S")
                    , inline=True
                ).add_field(
                    name='🕤 Joined at',
                    value=user.joined_at.strftime("%A, %d %B %Y at %I:%M:%S"),
                    inline=True
                ).add_field(
                    name='🤵🏻 Human?',
                    value='Yes!' if not user.bot else 'Nope'
                    , inline=True
                ).add_field(
                    name='✨ PFP Animated?',
                    value='Yes!' if user.is_avatar_animated() else 'Nope..'
                    , inline=True
                ).add_field(
                    name='🛠 System',
                    value='Mobile 📱' if user.is_on_mobile() else 'Desktop 💻',
                    inline=True
                ).add_field(
                    name='🔗 Link for PFP',
                    value=f"[Click here]({user.avatar_url})"
                    , inline=True
                ).add_field(
                    name='🎖 Badges',
                    value=''.join((f'• {str(x[0]).replace("_", " ").title()}\n' for x in all_flags) if all_flags != [] else 'No **badges** 🤷🏻‍♂️'),
                    inline=True
                ).add_field(
                    name=f'🎮 Activities ({len(user.activities)})' if user.activities else '🎮 Activity',
                    value=''.join((f'• {str(x.name)}\n' for x in user.activities)) if user.activities else 'No **activity** set 🤷🏻‍♂️',
                    inline=True
                ).add_field(
                    name=f'👨‍👦‍👦 Roles ({len(sorted(user.roles[1:], reverse=True))})',
                    value=' • '.join(f'{role.mention}' for role in sorted(user.roles[1:], reverse=True)) if len(user.roles) > 1 else f'{user.mention} has no roles.. Sad..',
                    inline=False
                ).set_footer(
                    text=f'Requested by {ctx.author.name + "#" + ctx.author.discriminator}',
                )
            )

    @commands.command(name="serverinfo", help="Sends the info of the current server.", aliases=['server'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def serverinfo(self, ctx):
        global flag_emoji
        guild = ctx.guild
        boosters = [booster for booster in guild.premium_subscribers]
        features = [feature for feature in guild.features]
        online_members = []
        offline_members = []
        dnd_members = []
        idle_members = []
        for member in guild.members:
            if member.status == discord.Status.online:
                online_members.append(member)
            elif member.status == discord.Status.dnd:
                dnd_members.append(member)
            elif member.status == discord.Status.offline:
                offline_members.append(member)
            elif member.status == discord.Status.idle:
                idle_members.append(member)
        if guild.region == discord.VoiceRegion.amsterdam:
            flag_emoji = ':flag_nl:'
        elif guild.region == discord.VoiceRegion.brazil:
            flag_emoji = ':flag_br:'
        elif guild.region == discord.VoiceRegion.dubai:
            flag_emoji = ':flag_ae:'
        elif guild.region in (discord.VoiceRegion.europe, discord.VoiceRegion.eu_west, discord.VoiceRegion.eu_central):
            flag_emoji = ':flag_eu:'
        elif guild.region == discord.VoiceRegion.frankfurt:
            flag_emoji = ':flag_de:'
        elif guild.region == discord.VoiceRegion.india:
            flag_emoji = ':flag_in:'
        elif guild.region == discord.VoiceRegion.hongkong:
            flag_emoji = ':flag_hk:'
        elif guild.region == discord.VoiceRegion.japan:
            flag_emoji = ':flag_jp:'
        elif guild.region == discord.VoiceRegion.london:
            flag_emoji = ':flag_gb:'
        elif guild.region == discord.VoiceRegion.russia:
            flag_emoji = ':flag_ru:'
        elif guild.region == discord.VoiceRegion.singapore:
            flag_emoji = ':flag_sg:'
        elif guild.region == discord.VoiceRegion.southafrica:
            flag_emoji = ':flag_za:'
        elif guild.region == discord.VoiceRegion.sydney:
            flag_emoji = ':flag_au:'
        elif guild.region in (discord.VoiceRegion.us_central, discord.VoiceRegion.us_east, discord.VoiceRegion.us_south,
                              discord.VoiceRegion.us_west, discord.VoiceRegion.vip_us_east,
                              discord.VoiceRegion.vip_us_west):
            flag_emoji = ':flag_us:'
        elif guild.region == discord.VoiceRegion.vip_amsterdam:
            flag_emoji = ':flag_nl:'
        channel = guild.system_channel if guild.system_channel is not None else self.client.get_channel(
            id=guild.text_channels[1].id)

        # TrixZ info
        guild_id    = str(ctx.guild.id)
        logs        = await self.client.pg_con.fetch("SELECT log_channel FROM log_channels WHERE guild_id = $1", guild_id)
        levels      = await self.client.pg_con.fetch("SELECT levels_enabled FROM all_guilds WHERE guild_id = $1", guild_id)
        welcome     = await self.client.pg_con.fetch("SELECT welcome_log_enabled FROM all_guilds WHERE guild_id = $1", guild_id)
        automod     = await self.client.pg_con.fetch("SELECT automod_enabled FROM all_guilds WHERE guild_id = $1", guild_id)
        invites     = await self.client.pg_con.fetch("SELECT invites_enabled FROM all_guilds WHERE guild_id = $1", guild_id)
        membercount = await self.client.pg_con.fetch("SELECT membercount_channel_name FROM member_count_channels WHERE guild_id = $1", guild_id)
        # -----
        ago = datetime.datetime.now() - ctx.guild.created_at
        months = round(ago.days / 30.417)
        embed = discord.Embed(color=main_color).set_author(name=f"{guild.name}'s Info",
                                                                            icon_url=guild.icon_url)
        embed.add_field(name="⮡  Created at", value='🕓 ' + guild.created_at.strftime("**%d %B** %Y") + f'\n🕣 {"**" + str(ago.days) + " days" + "**" if int(ago.days) < 31 and ago.days >= 0 else ""} {"**" + str(months) + " months" + "**"} ago', inline=True)
        embed.add_field(name="⮡  Owner", value='👱🏻‍♂️ '+ '**' + guild.owner.name + '#' + guild.owner.discriminator + '**',
                        inline=True)
        embed.add_field(name="⮡  System Channel",
                        value=guild.system_channel.mention if guild.system_channel is not None else '🙁 No **System Channel**',
                        inline=True)
        embed.add_field(name="⮡  Verification Level", value=(f'{tick} ' + str(guild.verification_level).title()) if not guild.verification_level == discord.VerificationLevel.none else f'{cross} No Verification', inline=True)
        embed.add_field(name="⮡  Boosts",
                        value=f'🔼 {guild.premium_subscription_count}' if guild.premium_subscription_count > 0 else '🙁 No **Boosts**',
                        inline=True)
        embed.add_field(name="⮡  Region", value=f'{flag_emoji} ' + '**' +str(guild.region).title().replace('-', ' ') + '**',
                        inline=True)
        embed.add_field(name=f"⮡  Features {('(' + f'{len(guild.features)}' + ')') if len(guild.features) > 0 else ''}",
                        value=''.join(
                            ['✨ ' + str(feature).title().replace('_', ' ') + "\n" for feature in features] if len(
                                features) > 0 else '🙁 No **Features**'), inline=True)
        embed.add_field(name=f"⮡  Server Boosters ({len(boosters)})" if len(boosters) > 0 else "⮡  Server Boosters",
                        value=''.join(['🚀 ' + booster.mention + '\n' for booster in boosters] if len(boosters) > 0 else '🙁 No **Server Boosters**'),
                        inline=True)
        embed.add_field(name="⮡  AFK Channel",
                        value=f'😴 [{guild.afk_channel.name}]({await guild.afk_channel.create_invite()})' if guild.afk_channel is not None else '🤷🏻‍♂️ No **AFK Channel**',
                        inline=True)
        embed.add_field(name='⮡  Channels', value=  f'🌐 Text Channels - **{len(guild.text_channels)}**\n'
                                                    f'🌐 Voice Channels - **{len(guild.voice_channels)}**\n'
                                                    f'🌐 Categories - **{len(guild.categories)}**', inline=True)
        embed.add_field(name='⮡  Extras (3)', value=f'⚔ Emojis limit   - **{guild.emoji_limit}** emojis\n'
                                                    f'⚔ Bitrate limit  - **{round(int(guild.bitrate_limit) / 1000)}** kb/s\n'
                                                    f'⚔ Filesize limit - **{round(guild.filesize_limit / 1000000)}** MB',
                        inline=True)
        embed.add_field(name=f"⮡  Members ({guild.member_count})",
                        value=f'{online_emoji} **{len(online_members)}**   -   {dnd_emoji} **{len(dnd_members)}**\n'
                              f'{idle_emoji} **{len(idle_members)}**   -   {offline_emoji} **{len(offline_members)}**',
                        inline=True)
        prefix = await self.client.pg_con.fetch("SELECT prefix from prefixes WHERE guild_id = $1", str(ctx.guild.id))
        embed.add_field(inline=False,
                        name=f'{main_emoji} TrixZ',
                        value=f'{tick if automod[0]["automod_enabled"] == "yes" else cross} AutoMod\n'
                              f'{tick if logs else cross} Logging\n'
                              f'{tick if levels[0]["levels_enabled"] == "yes" else cross} Level System\n'
                              f'{tick if welcome[0]["welcome_log_enabled"] == "yes" else cross} Welcomer\n'
                              f'{tick if membercount else cross} Member-Count\n'
                              f'{tick if invites[0]["invites_enabled"] == "yes" else cross} Invite Tracker\n'
                              f'{tick if prefix[0]["prefix"] != "t-" else cross} Custom Prefix\n'
                        )
        await ctx.send(embed=embed)

    @commands.command(name="stats", help="Sends the info of the bot.", aliases=["botinfo", "botstats"])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def _botinfo(self, ctx : commands.Context):
        embed = discord.Embed(color=main_color)
        embed.add_field(name="👨 Developer", value="[Videro#9999](https://discord.bio/p/videro)")
        embed.add_field(name="🎗 Prefix", value=ctx.prefix)
        embed.add_field(name="📚 Library", value=f"[{discord.__version__}](https://discordpy.readthedocs.io/en/latest/api.html)")
        embed.add_field(name="📊 Used in", value=f"{len(self.client.guilds)} servers")
        embed.add_field(name="📈 Used by", value=f"{len(list(self.client.get_all_members()))} users")
        embed.add_field(name="📋 Total commands", value=f"{len(list(self.client.walk_commands()))} commands")
        embed.add_field(name="📕 Docs", value=f"[Click here]({documentation_url})")
        embed.add_field(name="🕤 Started at", value=f"1st June 2020")
        embed.add_field(name="🕓 Released at", value=f"24th September 2020")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def wiki(self, ctx, *, search: str = None):
        """Search anything from the Wikipedia!"""
        if search == None:
            await Message.EmbedText(
                title=f'Please search for something!',
                color=discord.Color.red()
            ).send(ctx)
            return

        results = wikipedia.search(search)

        if not len(results):
            await Message.EmbedText(
                title=f'No results found for {search}.',
                color=discord.Color.red()
            ).send(ctx)
            return

        message = None
        if len(results) > 1:
            if len(results) > 5:
                results = results[:5]
            index, message = await Picker(
                title="There were multiple results for `{}`, please pick from the following list:".format(
                    search.replace('`', '\\`')),
                list=results,
                ctx=ctx,
                timeout=120,
                client=self.client
            ).pick()

            if index < 0:
                await message.edit(content="Wiki results for `{}` canceled.".format(search.replace('`', '\\`')))
                return
            newSearch = results[index]
        else:
            newSearch = results[0]

        try:
            wik = wikipedia.page(newSearch)
        except wikipedia.DisambiguationError:
            msg = "That search wasn't specific enough - try again with more detail."
            if message:
                await message.edit(content=msg)
            else:
                await ctx.send(msg)
            return

        wiki_embed = discord.Embed(color=main_color)
        wiki_embed.title = wik.title
        textList = textwrap.wrap(wik.content, 2045, break_long_words=True, replace_whitespace=False)
        wiki_embed.description = textList[0] + '...'
        wiki_embed.add_field(name='Read More', value=f'[Click here]({wik.url}) to read more about `{wik.title}`.')

        if message:
            await message.edit(content=" ", embed=wiki_embed)
            await message.clear_reactions()
        else:
            await ctx.send(embed=wiki_embed)
            await message.clear_reactions()

    async def tiny_url(self, url, bot):
        apiurl = "http://tinyurl.com/api-create.php?url="
        tinyurl = await bot.loop.run_in_executor(None, lambda: urlopen(apiurl + url).read().decode("utf-8"))
        return tinyurl

    def name(self, member : discord.Member):
        nick = name = None
        try:
            nick = member.nick
        except AttributeError:
            pass
        try:
            name = member.name
        except AttributeError:
            pass
        if nick:
            return Nullify.clean(nick)
        if name:
            return Nullify.clean(name)
        return None

    async def get_search(self, ctx, query, service=""):
        service = "s={}&".format(service) if service else ""
        lmgtfy = "http://lmgtfy.com/?{}q={}".format(service, query)
        try:
            lmgtfyT = await self.tiny_url(lmgtfy, self.client)
        except Exception as e:
            print(e)
            msg = "It looks like I couldn't search for that... :("
        else:
            msg = '*{}*, you can find your answers here:\n\n<{}>'.format(self.name(ctx.message.author), lmgtfyT)
        return msg

    @commands.command(name='google', help='Googles the search term for you!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def google(self, ctx, search_term: str = None):
        if not search_term:
            await Message.EmbedText(
                title='Please specify a search term!',
                color=discord.Color.red()
            ).send(ctx)
        if search_term:
            msg = await self.get_search(ctx, search_term)
            await Message.EmbedText(
                description=msg,
                color=main_color
            ).send(ctx)


def setup(client):
    client.add_cog(info(client))