import math
from   discord.ext import commands
from _Utils import Message
import asyncio
from bot import main_color
def setup(client):
	client.add_cog(PickList(client))

class PickList(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        self.client.dispatch("picklist_reaction", reaction, user)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        self.client.dispatch("picklist_reaction", reaction, user)

class Picker:
    def __init__(self, **kwargs):
        self.client = kwargs.get('client', None)
        self.list = kwargs.get("list", [])
        self.title = kwargs.get("title", None)
        self.timeout = kwargs.get("timeout", 60)
        self.ctx = kwargs.get("ctx", None)
        self.message = kwargs.get("message", None) # message to edit
        self.self_message = None
        self.max = 10
        self.reactions = [ "🛑" ]

    async def _add_reactions(self, message, react_list):
        for r in react_list:
            await message.add_reaction(r)

    async def _remove_reactions(self, react_list = []):
        try:
            await self.self_message.clear_reactions()
        except:
            pass
            '''for r in react_list:
                await message.remove_reaction(r,message.author)'''

    async def pick(self):
        if self.ctx == None or not len(self.list) or len(self.list) > self.max:
            return (-3, None)
        msg = ""
        if self.title:
            msg += self.title + "\n"
        msg += "```c\n"
        current = 0
        current_reactions = []
        for item in self.list:
            current += 1
            current_number = current if current < 10 else 0
            current_reactions.append("{}\N{COMBINING ENCLOSING KEYCAP}".format(current_number))
            msg += "{}. {}\n".format(current, item)
        msg += "```"
        current_reactions.append(self.reactions[0])
        if self.message:
            self.self_message = self.message
            await self.self_message.edit(content=msg, embed=None)
        else:
            self.self_message = await self.ctx.send(msg)
        await self._add_reactions(self.self_message, current_reactions)
        def check(reaction, user):
            return reaction.message.id == self.self_message.id and user == self.ctx.author and str(reaction.emoji) in current_reactions
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
        except:
            await self._remove_reactions(current_reactions)
            return (-2, self.self_message)
        
        await self._remove_reactions(current_reactions)
        ind = current_reactions.index(str(reaction.emoji))
        if ind == len(current_reactions)-1:
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
