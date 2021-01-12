import discord
from discord.ext import commands
from bot import main_color, main_emoji, documentation_url, support_server_url
import math
from _Utils import Message
import asyncio

class Picker:
	def __init__(self, **kwargs):
		self.client = kwargs.get('client', None)
		self.list = kwargs.get("list", [])
		self.title = kwargs.get("title", None)
		self.timeout = kwargs.get("timeout", 60)
		self.ctx = kwargs.get("ctx", None)
		self.message = kwargs.get("message", None)  # message to edit
		self.self_message = None
		self.max = 4  # Don't set programmatically - as we don't want this overridden
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
        # Expects self.list to contain the fields needed - each a dict with {"name":name,"value":value,"inline":inline}
        self.max = kwargs.get("max",10) # Must be between 1 and 25
        self.max = 4
        self.reactions = ["⏪","◀","▶","⏩","🔢","🛑"] # These will always be in the same order
        self.url = kwargs.get("url",None) # The URL the title of the embed will link to

    def _get_page_contents(self, page_number):
        # Returns the contents of the page passed
        start = self.max*page_number
        return self.list[start:start+self.max]

    async def pick(self):
        # This brings up the page picker and handles the events
        # It will return a tuple of (last_page_seen, message)
        # The return code is -1 for cancel, -2 for timeout, -3 for error, 0+ is index
        # Let's check our prerequisites first
        if self.ctx == None or not len(self.list):
            return (-3, None)
        page  = 0 # Set the initial page index
        pages = int(math.ceil(len(self.list)/self.max))
        # Setup the embed
        embed = {
            "title":self.title,
            "url":self.url,
            "description":self.message,
            "pm_after":25,
            "fields":self._get_page_contents(page),
            "footer":"Use t- before every command! ◦ Page {} of {}".format(page+1,pages)
        }
        if self.message:
            self.self_message = self.message
            await Message.Embed(**embed, color=main_color).edit(self.ctx, self.message)
        else:
            self.self_message = await Message.Embed(**embed, color=main_color).send(self.ctx)
        # First verify we have more than one page to display
        if pages <= 1:
            return (0,self.self_message)
        # Add our reactions
        await self._add_reactions(self.self_message, self.reactions)
        # Now we would wait...
        def check(reaction, user):
            return reaction.message.id == self.self_message.id and user == self.ctx.author and str(reaction.emoji) in self.reactions
        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
                await self.self_message.remove_reaction(emoji=reaction.emoji, member=self.ctx.author)
            except:
                # Didn't get a reaction
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            # Got a reaction - let's process it
            ind = self.reactions.index(str(reaction.emoji))
            if ind == 5:
                # We bailed - let's clear reactions and close it down
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            page = 0 if ind==0 else page-1 if ind==1 else page+1 if ind==2 else pages if ind==3 else page
            if ind == 4:
                # User selects a page
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
            embed["footer"] = "Use t- before every command! ◦ Page {} of {}".format(page+1,pages)
            await Message.Embed(**embed).edit(self.ctx, self.self_message)
        await self._remove_reactions(self.reactions)
        # Get the adjusted index
        return (page, self.self_message)

def setup(client):
    client.add_cog(help(client))

class help(commands.Cog):
    """"Help Command!"""
    def __init__(self, client):
        self.client = client

    @commands.command(name='help', help='Help Command!', hidden=True)
    async def _help(self, ctx, *arg: str):
        if arg:
            if arg[0] == 'automod' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('automodhelp'))
                return
            if arg[0] == 'roles' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('rolehelp'))
                return
            if arg[0] == 'membercount' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('mcounthelp'))
                return
            if arg[0] == 'logs':
                await ctx.invoke(self.client.get_command('logshelp'))
                return
            if arg[0] == 'emoji' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('emojihelp'))
                return
            if arg[0] == 'welcome' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('welcomehelp'))
                return
            if arg[0] == 'invites' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('inviteshelp'))
                return
            if arg[0] == 'rr' and len(arg) == 1:
                await ctx.invoke(self.client.get_command('rrhelp'))
                return
            for cog in self.client.cogs:
                cog1 = self.client.get_cog(cog)
                for command in cog1.walk_commands():
                    if len(arg) > 1:
                        if command.qualified_name == arg[0] + ' ' + arg[1]:
                            command1 = self.client.get_command(command.qualified_name)
                            help_embed = discord.Embed(color=main_color)
                            help_embed.add_field(
                                name='t-' + command1.name,
                                value="└─ " + command1.help,
                                inline=False).add_field(
                                    name=f'{main_emoji} Usage',
                                    value='t-' + command.qualified_name + ' ' + command1.signature,
                                    inline=False
                                    )
                            await ctx.send(embed=help_embed)
                            return

            cog1 = self.client.get_cog(name=arg[0])
            if cog1:
                help_embed = discord.Embed(title="<a:trixzhaloween:762682117603065908> Category " + "'" + arg[0] + "'", color=main_color)
                for command1 in cog1.walk_commands():
                    help_embed.add_field(
                        name="t-" + command1.name + ' ' +  command1.signature,
                        value="└─ " + str(command1.help),
                        inline=False
                    )
                await ctx.send(embed=help_embed)
                return
                
            command2 = self.client.get_command(name=arg[0])
            if command2:
                help_embed = discord.Embed(color=main_color)
                help_embed.add_field(
                    name='t-' + command2.name,
                    value=command2.help,
                    inline=False
                )
                help_embed.add_field(
                    name=f'{main_emoji} Usage',
                    value='t-' + command2.name + ' ' + command2.signature,
                    inline=False
                )
                help_embed.add_field(
                    name=f'{main_emoji} Category',
                    value=command2.cog.qualified_name if command2.cog is not None else 'No Category'
                )
                await ctx.send(embed=help_embed)
                return

        else:
            help_embed = discord.Embed(color=main_color)
            help_embed.title = f'{main_emoji} Command categories ({len(self.client.cogs) - 8})'
            help_embed_desc = ''
            cogs = []
            for cog in self.client.cogs:
                if cog not in ('DisplayName', 'logging', 'PickList', 'Settings', 'Utils', 'help', 'Uptime', 'Jishaku', 'errors', 'extra'):
                    cogs.append(cog)
            fields1 = []
            for cog in cogs:
                cog1 = self.client.get_cog(cog)
                mylist = []
                for item in cog1.walk_commands():
                    if not isinstance(item, commands.Group):
                        parent = item.parent
                        if not parent:
                            mylist.append(item.name)
                        if parent:
                            mylist.append(f"{parent.name} {item.name}")
                fields1.append({
                    "name"  : f"{main_emoji} {cog1.qualified_name.title()}",
                    "value" : ' ◦ '.join(f'`{x}`' for x in mylist),
                    "inline": False
                })
                help_embed.add_field(
                    name=f'{main_emoji} {cog1.qualified_name.title()}',
                    value=', '.join(f'`{x}`' for x in mylist),
                    inline=False
                )
            fields1.append({
                    "name"  : 'More Info',
                    "value" : f'⇀ Full command list [available here]({documentation_url})\n'\
                              f'⇀ Join the [support server]({support_server_url}) to report a bug or suggest something!\n'\
                              f'⇀ For more info on a specific category, type `t-help <category>`\n',
                    "inline": False
            })
            await PagePicker(list=fields1, client=self.client, timeout=200, title=f'Help!', ctx=ctx, color=main_color, footer='Use t- before every command!').pick()
            return

    @commands.command(name='mcounthelp', hidden=True)
    async def mcounthelp(self, ctx, arg = 'membercount'):
        cog1 = self.client.get_cog(name=arg)
        if cog1:
            help_embed = discord.Embed(title="Category " + arg, color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-membercount " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            await ctx.send(embed=help_embed)
            
    @commands.command(name='rolehelp', hidden=True)
    async def rolehelp(self, ctx):
        cog1 = self.client.get_cog('roles')
        if cog1:
            help_embed = discord.Embed(title="Category 'role'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-role " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            
            await ctx.send(embed=help_embed)

    @commands.command(name='logshelp', hidden=True)
    async def logshelp(self, ctx):
        cog1 = self.client.get_cog('logs')
        if cog1:
            help_embed = discord.Embed(title="Category 'logs'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-logs " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            
            await ctx.send(embed=help_embed)

    @commands.command(name='emojihelp', hidden=True)
    async def emojihelp(self, ctx):
        cog1 = self.client.get_cog('emoji')
        if cog1:
            help_embed = discord.Embed(title="Category 'emoji'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-emoji " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            await ctx.send(embed=help_embed)

    @commands.command(name='welcomehelp', hidden=True)
    async def welcomehelp(self, ctx):
        cog1 = self.client.get_cog('welcome')
        if cog1:
            help_embed = discord.Embed(title="Category 'welcome'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-welcome " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )

            await ctx.send(embed=help_embed)

    @commands.command(name='automodhelp', hidden=True)
    async def automodhelp(self, ctx):
        cog1 = self.client.get_cog('automod')
        if cog1:
            help_embed = discord.Embed(title="Category 'automod'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-automod " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )

            await ctx.send(embed=help_embed)

    @commands.command(name='inviteshelp', hidden=True)
    async def inviteshelp(self, ctx):
        cog1 = self.client.get_cog('invites')
        if cog1:
            help_embed = discord.Embed(title="Category 'invites'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-invites " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )

            await ctx.send(embed=help_embed)
    
    @commands.command(name='rrhelp', hidden=True)
    async def rrhelp(self, ctx):
        cog1 = self.client.get_cog('rr')
        if cog1:
            help_embed = discord.Embed(title="Category 'rr' (reaction roles)", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group):
                    help_embed.add_field(
                        name="t-rr " + command1.name + ' ' +  command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )

            await ctx.send(embed=help_embed)

    @commands.command(name='blacklisthelp', hidden=True)
    async def blacklisthelp(self, ctx) :
        cog1 = self.client.get_cog('blacklist')
        if cog1 :
            help_embed = discord.Embed(title="Category BlackList", color=main_color)
            for command1 in cog1.walk_commands() :
                if not isinstance(command1, discord.ext.commands.Group) :
                    help_embed.add_field(
                        name="t-bl " + command1.name + ' ' + command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            await ctx.send(embed=help_embed)

    @commands.command(name='channelhelp', hidden=True)
    async def channelhelp(self, ctx) :
        cog1 = self.client.get_cog('blacklist')
        if cog1:
            help_embed = discord.Embed(title="Category \'Channel\'", color=main_color)
            for command1 in cog1.walk_commands():
                if not isinstance(command1, discord.ext.commands.Group) :
                    help_embed.add_field(
                        name="t-cl " + command1.name + ' ' + command1.signature,
                        value="└─ " + command1.help,
                        inline=False
                    )
            await ctx.send(embed=help_embed)

    @commands.command()
    async def help2(self, ctx):
        commands = []
        for command in self.client.walk_commands():
            commands.append(command.qualified_name)
        # .join("`" + command + "`\n") for command in commands
        commands_list = "\n".join(
            f'▫ ' + '{:<12}'.format(b.title()) + '{:^12}'.format('= ') + '{:>12}'.format(f't-help {b}') for a, b in
            enumerate(commands[0:25], 1))
        commands_list1 = "\n".join(
            f'▫ ' + '{:<12}'.format(b.title()) + '{:^12}'.format('= ') + '{:>12}'.format(f't-help {b}') for a, b in
            enumerate(commands[26:50], 1))
        commands_list2 = "\n".join(
            f'▫ ' + '{:<12}'.format(b.title()) + '{:^12}'.format('= ') + '{:>12}'.format(f't-help {b}') for a, b in
            enumerate(commands[51:75], 1))
        commands_list3 = "\n".join(
            f'▫ ' + '{:<12}'.format(b.title()) + '{:^12}'.format('= ') + '{:>12}'.format(f't-help {b}') for a, b in
            enumerate(commands[76:100], 1))
        commands_list4 = "\n".join(
            f'▫ ' + '{:<12}'.format(b.title()) + '{:^12}'.format('= ') + '{:>12}'.format(f't-help {b}') for a, b in
            enumerate(commands[101:125], 1))
        await ctx.send(f"```prolog\n{commands_list}\n```")
        await ctx.send(f"```prolog\n{commands_list1}\n```")
        if len(commands) > 51:
            await ctx.send(f"```prolog\n{commands_list2}\n```")
        if len(commands) > 100:
            await ctx.send(f"```prolog\n{commands_list3}\n```")
        if len(commands) > 125:
            await ctx.send(f"```prolog\n{commands_list4}\n```")