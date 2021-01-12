import discord
from discord.ext import commands
from discord import Embed
from bot import main_color, support_server_url
import os, datetime, aiohttp
import cloudinary, functools, asyncio, json

config1 = open('config.json', 'r')
config = json.load(config1)

import json
import requests

x_api_key = config['FN_API_KEY']
cloud_api_key = config['CLOUDINARY_API_KEY']
cloud_api_secret = config['CLOUDINARY_API_SECRET']

class renders(commands.Cog):
    """`Fortnite` Render commands which are accessible to all members of the server!"""

    def __init__(self, client : commands.Bot):
        self.client = client
        cloudinary.config(
            cloud_name="videro",
            api_key=cloud_api_key,
            api_secret=cloud_api_secret
        )

    async def get_renders(self, skin_name: str):
        def sync_task():
            result = cloudinary.Search() \
                .expression("videro" + skin_name.replace(" ", "_").title() + "*") \
                .sort_by('public_id') \
                .execute()
            return result
        render = functools.partial(sync_task)
        return await self.client.loop.run_in_executor(None, render)

    def get_embeds(self, data : dict):
        rsc : list = data['resources']
        links = []
        for x in rsc:
            links.append(x['secure_url'])
        return list(links)

    async def send_embeds(self, links : list, webhook : discord.Webhook, title : str):
        embeds = []
        for x in range(len(links)):
            embeds.append(
                discord.Embed(title=title, color=main_color, url='https://www.twitter.com/#videro')\
                .set_image(url=links[x])\
                .set_footer(text="TrixZ, developed with 💖 by Videro#9999", icon_url=self.client.user.avatar_url)
            )
        split_embeds = [embeds[x:x+4] for x in range(0, len(embeds),4)]
        for y in split_embeds:
            await webhook.send(embeds=y, username='TrixZ', avatar_url=self.client.user.avatar_url)
            await asyncio.sleep(1)

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
                create: discord.Webhook = await channel.create_webhook(name="TrixZ Renders",
                                                                       reason=f'TrixZ Renders :D')
                return create
            except discord.Forbidden:
                return None

    @commands.command(name="render", help="Sends the render of the skin mentioned.")
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def render(self, ctx : commands.Context, *, skin_name: str = None):
        e = discord.Embed(color=main_color, title="Temporarily Disabled 😢")
        e.description = f"""Hey, {ctx.author.name}, we are so sorry for this inconvenience caused. The command `render` is **currently disabled**.
If you want, you can still use the `render2` command, similar to the render command but a little less advanced.  (`{ctx.prefix}render2` instead of `{ctx.prefix}render`)
If you are interested in knowing the full details behind this, you can join the [support server]({support_server_url}) and read the latest announcement.
        """
        e.set_author(name="Message from Videro#9999", url='https://linktr.ee/videro', icon_url=self.client.user.avatar_url)
        return await ctx.send(embed=e)
#         if not skin_name:
#             e = discord.Embed(color=discord.Color.red(), title="You did not mention a skin name. Try again.")
#             return await ctx.send(embed=e)
#         if skin_name:
#             renders : dict = await self.get_renders(skin_name)
#             if renders['resources'] != []:
#                 count = renders['total_count']
#                 time_took =  renders['time']
#                 all_renders = renders['resources']
#                 webhook = await self.get_trixz_webhook(ctx.channel)
#                 if not webhook:
#                     e3 = discord.Embed(title="Uh oh", color=discord.Color.red())
#                     e3.description = f"""
# • Hey {ctx.author.name}, it looks like I do not have the "**Manage Webhooks**" permissions in this server.
# • If you are an administrator of the server, please give me the appropriate permissions, in order for the command to work.
# • If you are a member of the server, please contact a server administrator and tell him to look into this!
#                     """
#                     return await ctx.send(embed=e3)
#                 if webhook:
#                     init = await ctx.send(f"Sending **{count}** {skin_name.title()} renders ✅")
#                     await asyncio.sleep(0.5)
#                     links = self.get_embeds(renders)
#                     await self.send_embeds(links=links, webhook=webhook, title=skin_name.title())
#                     await init.delete()
#             if renders['resources'] == []:
#                 init = await ctx.send(f"Searching for `{skin_name}` renders...")
#                 url = f"https://fnbr.co/api/images?search={str(skin_name).replace(' ', '%20')}"
#                 headers = {
#                     'x-api-key': x_api_key
#                 }
#                 async with aiohttp.ClientSession(headers=headers) as cs:
#                     async with cs.get(url) as wasd:
#                         data = await wasd.json()
#                 if data["data"] != []:
#                     # await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
#                     if data["data"][0]["images"]["featured"] != False:
#                         embed = discord.Embed(color=main_color, title=str(data["query"]["search"]).title(), url="https://fnbr.co/")
#                         embed.set_footer(
#                             icon_url=self.client.user.avatar_url,
#                             text="Developed with 💝 by Videro#9999")
#                         embed.set_image(url=data["data"][0]["images"]["featured"])
#                         await init.edit(content="", embed=embed)
#                     if data["data"][0]["images"]["featured"] == False:
#                         embed = discord.Embed(color=main_color, title=str(data["query"]["search"]).title(), url="https://fnbr.co/")
#                         embed.set_footer(
#                             icon_url=self.client.user.avatar_url,
#                             text="Developed with 💝 by Videro#9999")
#                         embed.set_image(url=data["data"][0]["images"]["icon"])
#                         await init.edit(content="", embed=embed)
#                 else:
#                     # await ctx.message.add_reaction("<a:vxcross:745553761598046280>")
#                     await init.delete()
#                     await ctx.send(f"**{ctx.author.name}**, the skin you requested (`{skin_name}`) was not found.")
#                     # return await ctx.invoke(self.client.get_command('renders'))

    @commands.command(name="render2", help="Sends the render of the skin mentioned. (2nd version)")
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def render2(self, ctx, *, skin_name: str):
        if skin_name.lower() == "crystal":
            await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
            crystal1 = discord.Embed(color=main_color)
            crystal1.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731247576627806288/three.png')
            crystal2 = discord.Embed(color=main_color)
            crystal2.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731247187518029844/free_render_mix.png')
            crystal3 = discord.Embed(color=main_color)
            crystal3.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731245967432482817/crystal.png')
            crystal4 = discord.Embed(color=main_color)
            crystal4.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731245966946074625/cryptic.png')
            crystal5 = discord.Embed(color=main_color)
            crystal5.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731242418611159141/hexhh.png?width=1058&height=595')
            crystal6 = discord.Embed(color=main_color)
            crystal6.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731241422031683664/qfnfx.png')
            crystal6.set_footer(text=f"Developed with 💝 by Videro#9999",
                                icon_url=self.client.user.avatar_url)
            await ctx.send(embed=crystal1)
            await ctx.send(embed=crystal2)
            await ctx.send(embed=crystal3)
            await ctx.send(embed=crystal4)
            await ctx.send(embed=crystal5)
            await ctx.send(embed=crystal6)
        elif skin_name.lower() == "aura":
            await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
            aura1 = discord.Embed(color=main_color)
            aura1.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731248369871093901/jump.png')
            aura2 = discord.Embed(color=main_color)
            aura2.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731247359358664764/siphon.png')
            aura3 = discord.Embed(color=main_color)
            aura3.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731247187236880384/free_pfp.png')
            aura4 = discord.Embed(color=main_color)
            aura4.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731246391283810335/Octane10.png')
            aura5 = discord.Embed(color=main_color)
            aura5.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731245584609968128/aura_pfp.png')
            aura6 = discord.Embed(color=main_color)
            aura6.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731245533779329075/Aura_axe.png')
            aura7 = discord.Embed(color=main_color)
            aura7.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731245432390418493/Aura2.png')
            aura8 = discord.Embed(color=main_color)
            aura8.set_image(
                url='https://media.discordapp.net/attachments/719534088934916162/731241213642014780/GoatifyG-2.png')
            aura8.set_footer(text=f"Developed with 💝 by Videro#9999",
                             icon_url=self.client.user.avatar_url)
            await ctx.send(embed=aura1)
            await ctx.send(embed=aura2)
            await ctx.send(embed=aura3)
            await ctx.send(embed=aura4)
            await ctx.send(embed=aura5)
            await ctx.send(embed=aura6)
            await ctx.send(embed=aura7)
            await ctx.send(embed=aura8)
        elif skin_name.lower() == "hush":
            await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
            hush1 = discord.Embed(color=main_color)
            hush1.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731738968458002514/hushpump.png')
            hush2 = discord.Embed(color=main_color)
            hush3 = discord.Embed(color=main_color)
            hush4 = discord.Embed(color=main_color)
            hush5 = discord.Embed(color=main_color)
            hush6 = discord.Embed(color=main_color)
            hush7 = discord.Embed(color=main_color)
            hush8 = discord.Embed(color=main_color)
            hush9 = discord.Embed(color=main_color)
            hush10 = discord.Embed(color=main_color)
            hush11 = discord.Embed(color=main_color)
            hush2.set_image(url='https://cdn.discordapp.com/attachments/731738715248132117/731738975370215445/Hush.png')
            hush3.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731738978402959420/hush-render.png')
            hush4.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731739362831892548/--036.png')
            hush5.set_image(url='https://cdn.discordapp.com/attachments/731738715248132117/731739711592202260/9.png')
            hush6.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731739843763109908/Hush_bored_png.png')
            hush7.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731739844417421312/Hush_render.PNG')
            hush8.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731739849928867871/hush_pfp.png')
            hush9.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731740082242977864/image0_17.png')
            hush10.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731740180989345872/image1.png')
            hush11.set_image(
                url='https://cdn.discordapp.com/attachments/731738715248132117/731740364016451594/PicsArt_03-17-06.55.44.png')
            hush11.set_footer(text=f"Developed with 💝 by Videro#9999",
                              icon_url=self.client.user.avatar_url)
            await ctx.send(embed=hush1)
            await ctx.send(embed=hush2)
            await ctx.send(embed=hush3)
            await ctx.send(embed=hush4)
            await ctx.send(f"{ctx.author.mention} Sending more...", delete_after=1)
            await ctx.send(embed=hush5)
            await ctx.send(embed=hush6)
            await ctx.send(embed=hush7)
            await ctx.send(embed=hush8)
            await ctx.send(f"{ctx.author.mention} Sending more...", delete_after=2)
            await ctx.send(embed=hush9)
            await ctx.send(embed=hush10)
            await ctx.send(embed=hush11)
        elif skin_name.lower() == 'ghoul trooper':
            await ctx.send(
                "https://media.discordapp.net/attachments/719534088934916162/731241212870262885/GoatifyG-1.png?width=567&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731241421499007056/qfnfx-4.png?width=895&height=594\n"
                "https://media.discordapp.net/attachments/719534088934916162/731241526318858280/1.png?width=769&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731241937750851644/14.png?width=525&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731244398209138708/Dark_Ghoul_-Scary-_2.png?width=1058&height=595")
            await ctx.send(
                "https://media.discordapp.net/attachments/719534088934916162/731246391661297714/Pink_Ghoul.png?width=539&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731246439430094918/render_5_quiro.png?width=1058&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731246487966580897/Render_9_alona.png?width=1058&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731246679063396483/rezon_ay_2.png?width=1058&height=595n"
                "https://media.discordapp.net/attachments/719534088934916162/731247142500434041/Ghoul-Thumbnail.png?width=1058&height=595\n"
                "https://media.discordapp.net/attachments/719534088934916162/731247188604354592/ghoul-render.png?width=1058&height=595\n")
            await ctx.send(
                "https://media.discordapp.net/attachments/719534088934916162/731247263635996723/Ghoul_Trooper.png?width=566&height=595")
        else:
            url = f"https://fnbr.co/api/images?search={str(skin_name).replace(' ', '%20')}"
            headers = {
                'x-api-key': x_api_key
            }
            async with aiohttp.ClientSession(headers=headers) as cs:
                async with cs.get(url) as wasd:
                    data = await wasd.json()
            if data["data"] != []:
                # await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
                if data["data"][0]["images"]["featured"] != False:
                    embed = discord.Embed(color=main_color, title=str(data["query"]["search"]).title())
                    embed.set_footer(
                        icon_url=self.client.user.avatar_url,
                        text="Developed with 💝 by Videro#9999")
                    embed.set_image(url=data["data"][0]["images"]["featured"])
                    await ctx.send(embed=embed)
                if data["data"][0]["images"]["featured"] == False:
                    embed = discord.Embed(color=main_color, title=data["query"]["search"])
                    embed.set_footer(
                        icon_url=self.client.user.avatar_url,
                        text="Developed with 💝 by Videro#9999")
                    embed.set_image(url=data["data"][0]["images"]["icon"])
                    await ctx.send(embed=embed)
            else:
                # await ctx.message.add_reaction("<a:vxcross:745553761598046280>")
                await ctx.send(f"**{ctx.author.name}**, the skin you requested (`{skin_name}`) was not found.")
                return await ctx.invoke(self.client.get_command('renders'))

    @commands.command(name="renders", help="Sends the list of all renders available.")
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def _renders(self, ctx : commands.Context):
        # await ctx.message.add_reaction("<a:vxtick:745550119436288061>")
        e = discord.Embed(title="Fortnite Renders (Currently Disabled)", color=main_color, url="https://www.fortnite.com/")
        e.description = \
        f"""
Hey {ctx.author.name}, You can get Fortnite renders by using the `t-render` command.
**───────────────**
> __**Custom Renders:**__
These are the renders made and provided by the community.
• \\⭐ `t-render crystal`
• `t-render hush`
• `t-render ghoul trooper`
• \\⭐ `t-render manic`
• `t-render arial assault trooper`
• `t-render assault trooper`
• \\⭐ `t-render focus`
• `t-render astra`
• `t-render bachii`
• \\⭐ `t-render sparkplug`
• `t-render birdie`
• \\⭐ `t-render dynamo`
• `t-render bullseye`
• `t-render brawler`
• \\⭐ `t-render chaos agent`
• `t-render clash`
• \\⭐ `t-render soccer skin`
• `t-render ...` [Click here to see full list](https://trixz.gitbook.io/trixz/commands/render-commands#render "Just click it already")
• \\⭐ = Popular Renders / Present in More quantity 
• More **coming soon**. Join the [support server]({support_server_url}) for all the updates!
**───────────────**
> __**Default Renders:**__
These are the renders provided by the game itself.
• `t-render any skin/pickaxe`
• Example: `t-render iron man`
**Please Note**:
• The name of the skin/pickaxe must be the exact same as the item in-game. For example, `iron man` is not a valid skin name but `tony stark` is.
• The different variants are not available. For example, do not type `purple skull trooper`.
**───────────────**
> __**Credits:**__
• Both this command and [bot](https://discord.ly/trixz "This link is good :D") are developed by [**Videro**](https://linktr.ee/videro "Click here <3").
• The custom renders are from [this pack](https://drive.google.com/drive/folders/10_iK2DxodEyOHxwmfdKNcmA-XhscwEXM?usp=sharing "Really great pack, by Harxu").
• All credits goes to the respective authors of the renders.
        """
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"Command used by {ctx.author.name} at", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=e)

def setup(client):
    client.add_cog(renders(client))
