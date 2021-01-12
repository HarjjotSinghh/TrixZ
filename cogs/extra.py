import os, asyncio
import datetime
import discord
from discord.ext import commands
from bot import main_color

def setup(client):
    client.add_cog(extra(client))

class extra(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.command(name="sendmsg", help="Sends your message to the user mentioned!")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, 10)
    async def sendmsg(self, ctx : commands.Context, user : discord.User):
        user = await self.client.fetch_user(user_id=user.id)
        if user:
            await ctx.send("Send your message - ")
            try:
                msg = await self.client.wait_for('message', timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel)
                await user.send(msg.content)
                await ctx.send(f"Successfully sent the message to **{str(user)}** :\n{msg.content}")
                return
            except asyncio.TimeoutError:
                return await ctx.send("You did not reply in time!")
        if not user:
            return await ctx.send("I cannot send that user any message!")

    @commands.command(name='verify')
    @commands.guild_only()
    async def verify(self, ctx : commands.Context):
        if ctx.guild.id == 766275358327963699:
            e = discord.Embed(color=discord.Colour.gold())
            e.set_author(name="Indo Pak GFX/VFX Customs", url=ctx.guild.icon_url, icon_url=ctx.guild.icon_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text="Indo Pak GFX/VFX Customs", icon_url=ctx.guild.icon_url)
            e.set_thumbnail(url=ctx.guild.icon_url)
            e.set_image(url='https://cdn.discordapp.com/attachments/760735693760364554/766550457044303902/image0.png')
            e.description = "⨠ Head over to [speedtest.net](https://www.speedtest.net/) and take a screen shot your results as shown below. You may blur out your IP Address from the screenshot.\n└─ Kindly Send Screenshots and be patient. Do not spam tag or dm staff.\n\n⨠ Link 1 of Your Projects"
            await ctx.send(embed=e)
        else:
            await ctx.send("Sorry, this command cannot be used here :(")
    """
    @commands.command(name='specs')
    async def specs(self, ctx : commands.Context):
        cpu_usage=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2)) + "%"
        tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
        memorystats = f"Total - {tot_m} MB\nUsed - {used_m} MB\nFree - {free_m} MB"
        e = discord.Embed(title="PC Specs!", color=main_color)
        e.add_field(name="")
    """