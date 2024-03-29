import asyncio, discord, textwrap, random, math, os
from discord.ext import commands

class Message:
    def __init__(self, **kwargs):
        self.max_chars = 2000
        self.pm_after = kwargs.get("pm_after", 1)
        self.force_pm = kwargs.get("force_pm", False)
        self.header = kwargs.get("header", "")
        self.footer = kwargs.get("footer", "")
        self.pm_react = kwargs.get("pm_react", "📬")
        self.message = kwargs.get("message", None)
        self.file = kwargs.get("file", None)
        self.max_pages = 0
        self.delete_after = kwargs.get("delete_after", None)

    def _get_file(self, file_path):
        if not os.path.exists(file_path):
            return None

        ext = file_path.split(".")
        fname = "Upload." + ext[-1] if len(ext) > 1 else "Upload"
        file_handle = discord.File(fp=file_path, filename=fname)
        return (file_handle, fname)

    async def _send_message(self, ctx, message, pm=False, file_path=None):
        send_file = None
        if not file_path == None:
            dfile = self._get_file(file_path)
            if not dfile:
                try:
                    await ctx.send("An error occurred!\nThe file specified couldn't be sent :(")
                except:
                    pass
                return None
            else:
                send_file = dfile[0]
        if pm == True and type(ctx) is discord.ext.commands.Context and not ctx.channel == ctx.author.dm_channel:
            try:
                message = await ctx.author.send(message, file=send_file, delete_after=self.delete_after)
                await ctx.message.add_reaction(self.pm_react)
                return message
            except discord.Forbidden:
                if self.force_pm:
                    try:
                        await ctx.send("An error occurred!\nCould not dm this message to you :(")
                    except:
                        pass
                    return None
                pass
        return await ctx.send(message, file=send_file, delete_after=self.delete_after)

    async def send(self, ctx):
        if not ctx or not self.message or not len(self.message):
            return
        text_list = textwrap.wrap(
            self.message,
            self.max_chars - len(self.header) - len(self.footer),
            break_long_words=True,
            replace_whitespace=False)

        to_pm = len(text_list) > self.pm_after if self.pm_after > -1 else False
        page_count = 1
        for m in text_list:
            if self.max_pages > 0 and page_count > self.max_pages:
                break
            message = await self._send_message(ctx, self.header + m + self.footer, to_pm)
            if not message:
                return None
            page_count += 1
        return message

class Embed:
    def __init__(self, **kwargs):
        self.title_max = kwargs.get("title_max", 256)
        self.desc_max = kwargs.get("desc_max", 2048)
        self.field_max = kwargs.get("field_max", 25)
        self.fname_max = kwargs.get("fname_max", 256)
        self.fval_max = kwargs.get("fval_max", 1024)
        self.foot_max = kwargs.get("foot_max", 2048)
        self.auth_max = kwargs.get("auth_max", 256)
        self.total_max = kwargs.get("total_max", 6000)
        self.pm_after = kwargs.get("pm_after", 10)
        self.force_pm = kwargs.get("force_pm", False)
        self.pm_react = kwargs.get("pm_react", "📬")
        self.title = kwargs.get("title", None)
        self.page_count = kwargs.get("page_count", False)
        self.url = kwargs.get("url", None)
        self.description = kwargs.get("description", None)
        self.image = kwargs.get("image", None)
        self.footer = kwargs.get("footer", None)
        self.thumbnail = kwargs.get("thumbnail", None)
        self.author = kwargs.get("author", None)
        self.fields = kwargs.get("fields", [])
        self.file = kwargs.get("file", None)
        self.delete_after = kwargs.get("delete_after", None)
        self.colors = [
            discord.Color.teal(),
            discord.Color.dark_teal(),
            discord.Color.green(),
            discord.Color.dark_green(),
            discord.Color.blue(),
            discord.Color.dark_blue(),
            discord.Color.purple(),
            discord.Color.dark_purple(),
            discord.Color.magenta(),
            discord.Color.dark_magenta(),
            discord.Color.gold(),
            discord.Color.dark_gold(),
            discord.Color.orange(),
            discord.Color.dark_orange(),
            discord.Color.red(),
            discord.Color.dark_red(),
            discord.Color.lighter_grey(),
            discord.Color.dark_grey(),
            discord.Color.light_grey(),
            discord.Color.darker_grey(),
            discord.Color.blurple(),
            discord.Color.greyple(),
            discord.Color.default()
        ]
        self.color = kwargs.get("color", None)

    def add_field(self, **kwargs):
        self.fields.append({
            "name": kwargs.get("name", "None"),
            "value": kwargs.get("value", "None"),
            "inline": kwargs.get("inline", False)
        })

    def clear_fields(self):
        self.fields = []

    def _get_file(self, file_path):
        if not os.path.exists(file_path):
            return None
        ext = file_path.split(".")
        fname = "Upload." + ext[-1] if len(ext) > 1 else "Upload"
        file_handle = discord.File(fp=file_path, filename=fname)
        return (file_handle, fname)
    async def _send_embed(self, ctx, embed, pm=False, file_path=None):
        send_file = None
        if not file_path == None:
            dfile = self._get_file(file_path)
            if not dfile:
                try:
                    await Embed(title="An error occurred!", description="The file specified couldn't be sent :(",
                                color=self.color).send(ctx)
                except:
                    pass
                return None
            else:
                send_file = dfile[0]
                embed.set_image(url="attachment://" + str(dfile[1]))
        if pm == True and type(ctx) is discord.ext.commands.Context and not ctx.channel == ctx.author.dm_channel:
            try:
                if send_file:
                    message = await ctx.author.send(embed=embed, file=send_file, delete_after=self.delete_after)
                else:
                    message = await ctx.author.send(embed=embed, delete_after=self.delete_after)
                await ctx.message.add_reaction(self.pm_react)
                return message
            except discord.Forbidden:
                if self.force_pm:
                    try:
                        await Embed(title="An error occurred!", description="Could not dm this message to you :(",
                                    color=self.color).send(ctx)
                    except:
                        pass
                    return None
                pass
        if send_file:
            return await ctx.send(embed=embed, file=send_file, delete_after=self.delete_after)
        else:
            return await ctx.send(embed=embed, delete_after=self.delete_after)

    def _truncate_string(self, value, max_chars):
        if not type(value) is str:
            return value
        return (value[:max_chars - 3] + "...") if len(value) > max_chars else value

    def _total_chars(self, embed):
        tot = 0
        if embed.title:
            tot += len(embed.title)
        if embed.description:
            tot += len(embed.description)
        if not embed.footer is discord.Embed.Empty:
            tot += len(embed.footer)
        for field in embed.fields:
            tot += len(field.name) + len(field.value)
        return tot

    def _embed_with_self(self):
        if self.color == None:
            self.color = random.choice(self.colors)
        elif type(self.color) is discord.Member:
            self.color = self.color.color
        elif type(self.color) is discord.User:
            self.color = random.choice(self.colors)
        elif type(self.color) is tuple or type(self.color) is list:
            if len(self.color) == 3:
                try:
                    r, g, b = [int(a) for a in self.color]
                    self.color = discord.Color.from_rgb(r, g, b)
                except:
                    self.color = random.choice(self.colors)
            else:
                self.color = random.choice(self.colors)
        em = discord.Embed(color=self.color)
        em.title = self._truncate_string(self.title, self.title_max)
        em.url = self.url
        em.description = self._truncate_string(self.description, self.desc_max)
        if self.image:
            em.set_image(url=self.image)
        if self.thumbnail:
            em.set_thumbnail(url=self.thumbnail)
        if self.author:
            if type(self.author) is discord.Member or type(self.author) is discord.User:
                name = self.author.nick if hasattr(self.author, "nick") and self.author.nick else self.author.name
                em.set_author(
                    name=self._truncate_string(name, self.auth_max),
                    icon_url=self.author.avatar_url
                )
            elif type(self.author) is dict:
                if any(item in self.author for item in ["name", "url", "icon"]):
                    em.set_author(
                        name=self._truncate_string(self.author.get("name", discord.Embed.Empty), self.auth_max),
                        url=self.author.get("url", discord.Embed.Empty),
                        icon_url=self.author.get("icon_url", discord.Embed.Empty)
                    )
                else:
                    em.set_author(name=self._truncate_string(str(self.author), self.auth_max))
            else:
                em.set_author(name=self._truncate_string(str(self.author), self.auth_max))
        return em

    def _get_footer(self):
        footer_text = footer_icon = discord.Embed.Empty
        if type(self.footer) is str:
            footer_text = self.footer
        elif type(self.footer) is dict:
            footer_text = self.footer.get("text", discord.Embed.Empty)
            footer_icon = self.footer.get("icon_url", discord.Embed.Empty)
        elif self.footer == None:
            pass
        else:
            footer_text = str(self.footer)
        return (footer_text, footer_icon)

    async def edit(self, ctx, message):
        if self.color == None and len(message.embeds):
            self.color = message.embeds[0].color
        em = self._embed_with_self()
        footer_text, footer_icon = self._get_footer()

        to_pm = len(self.fields) > self.pm_after if self.pm_after > -1 else False

        if len(self.fields) <= self.pm_after and not to_pm:
            for field in self.fields:
                em.add_field(
                    name=self._truncate_string(field.get("name", "None"), self.fname_max),
                    value=self._truncate_string(field.get("value", "None"), self.fval_max),
                    inline=field.get("inline", False)
                )
            em.set_footer(
                text=self._truncate_string(footer_text, self.foot_max),
                icon_url=footer_icon
            )
            send_file = None
            if self.file:
                m = await self._send_embed(ctx, em, to_pm, self.file)
                await message.delete()
                return m
            await message.edit(content=None, embed=em, delete_after=self.delete_after)
            return message
        new_message = await self.send(ctx)
        if new_message.channel == ctx.author.dm_channel and not ctx.channel == ctx.author.dm_channel:
            em = Embed(title=self.title, description="📬 Check your dm's", color=self.color)._embed_with_self()
            await message.edit(content=None, embed=em, delete_after=self.delete_after)
        else:
            await message.delete()
        return new_message

    async def send(self, ctx):
        if not ctx:
            return

        em = self._embed_with_self()
        footer_text, footer_icon = self._get_footer()

        if not len(self.fields):
            em.set_footer(
                text=self._truncate_string(footer_text, self.foot_max),
                icon_url=footer_icon
            )
            return await self._send_embed(ctx, em, False, self.file)

        to_pm = len(self.fields) > self.pm_after if self.pm_after > -1 else False

        page_count = 1
        page_total = math.ceil(len(self.fields) / self.field_max)

        if page_total > 1 and self.page_count and self.title:
            add_title = " (Page {:,} of {:,})".format(page_count, page_total)
            em.title = self._truncate_string(self.title, self.title_max - len(add_title)) + add_title
        for field in self.fields:
            em.add_field(
                name=self._truncate_string(field.get("name", "None"), self.fname_max),
                value=self._truncate_string(field.get("value", "None"), self.fval_max),
                inline=field.get("inline", False)
            )
            if len(em.fields) >= self.field_max:
                if page_count > 1 and not self.page_count:
                    em.title = None
                if page_total == page_count:
                    em.set_footer(
                        text=self._truncate_string(footer_text, self.foot_max),
                        icon_url=footer_icon
                    )
                if page_count == 1 and self.file:
                    message = await self._send_embed(ctx, em, to_pm, self.file)
                else:
                    message = await self._send_embed(ctx, em, to_pm)
                if not message:
                    return None
                em.clear_fields()
                page_count += 1
                if page_total > 1 and self.page_count and self.title:
                    add_title = " (Page {:,} of {:,})".format(page_count, page_total)
                    em.title = self._truncate_string(self.title, self.title_max - len(add_title)) + add_title

        if len(em.fields):
            em.set_footer(
                text=self._truncate_string(footer_text, self.foot_max),
                icon_url=footer_icon
            )
            if page_total == 1 and self.file:
                message = await self._send_embed(ctx, em, to_pm, self.file)
            else:
                message = await self._send_embed(ctx, em, to_pm)
        return message


class EmbedText(Embed):
    def __init__(self, **kwargs):
        Embed.__init__(self, **kwargs)
        self.pm_after = kwargs.get("pm_after", 1)
        self.max_pages = kwargs.get("max_pages", 0)
        self.desc_head = kwargs.get("desc_head", "")
        self.desc_foot = kwargs.get("desc_foot", "")

    async def edit(self, ctx, message):
        if self.color == None and len(message.embeds):
            self.color = message.embeds[0].color
        em = self._embed_with_self()
        footer_text, footer_icon = self._get_footer()

        if self.description == None or not len(self.description):
            text_list = []
        else:
            text_list = textwrap.wrap(
                self.description,
                self.desc_max - len(self.desc_head) - len(self.desc_foot),
                break_long_words=True,
                replace_whitespace=False)
        to_pm = len(text_list) > self.pm_after if self.pm_after > -1 else False
        if len(text_list) <= 1 and not to_pm:
            if len(text_list):
                em.description = self.desc_head + text_list[0] + self.desc_foot
            em.set_footer(
                text=self._truncate_string(footer_text, self.foot_max),
                icon_url=footer_icon
            )
            send_file = None
            if self.file:
                m = await self._send_embed(ctx, em, to_pm, self.file)
                await message.delete()
                return m
            await message.edit(content=None, embed=em, delete_after=self.delete_after)
            return message
        new_message = await self.send(ctx)
        if new_message.channel == ctx.author.dm_channel and not ctx.channel == ctx.author.dm_channel:
            em = Embed(title=self.title, description="📬 Check your dm's", color=self.color)._embed_with_self()
            await message.edit(content=None, embed=em, delete_after=self.delete_after)
        else:
            await message.delete()
        return new_message

    async def send(self, ctx):
        if not ctx:
            return

        em = self._embed_with_self()
        footer_text, footer_icon = self._get_footer()
        if self.description == None or not len(self.description):
            em.set_footer(
                text=self._truncate_string(footer_text, self.foot_max),
                icon_url=footer_icon
            )
            return await self._send_embed(ctx, em, False, self.file)

        text_list = textwrap.wrap(
            self.description,
            self.desc_max - len(self.desc_head) - len(self.desc_foot),
            break_long_words=True,
            replace_whitespace=False)
        to_pm = len(text_list) > self.pm_after if self.pm_after > -1 else False
        page_count = 1
        page_total = len(text_list)

        if len(text_list) > 1 and self.page_count and self.title:
            add_title = " (Page {:,} of {:,})".format(page_count, page_total)
            em.title = self._truncate_string(self.title, self.title_max - len(add_title)) + add_title

        i = 0
        for i in range(len(text_list)):
            m = text_list[i]
            if self.max_pages > 0 and i >= self.max_pages:
                break
            if i > 0 and not self.page_count:
                em.title = None
            if i == len(text_list) - 1:
                em.set_footer(
                    text=self._truncate_string(footer_text, self.foot_max),
                    icon_url=footer_icon
                )
            em.description = self.desc_head + m + self.desc_foot
            if i == 0 and self.file != None:
                message = await self._send_embed(ctx, em, to_pm, self.file)
            else:
                message = await self._send_embed(ctx, em, to_pm)
            if not message:
                return None
            page_count += 1
            if len(text_list) > 1 and self.page_count and self.title:
                add_title = " (Page {:,} of {:,})".format(page_count, page_total)
                em.title = self._truncate_string(self.title, self.title_max - len(add_title)) + add_title
        return message
