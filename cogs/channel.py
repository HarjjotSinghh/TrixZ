import discord, asyncio
from discord.ext import commands
from bot import main_color

def setup(bot):
    bot.add_cog(channel(bot))

class channel(commands.Cog):
    """"
    The channel commands allows you to create, delete, and modify channels.
    """
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.group(name="channel", aliases=['ch', 'cl'], case_insensetive=True)
    @commands.guild_only()
    async def _channel(self, ctx : commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.invoke(self.bot.get_command('channelhelp'))

    @_channel.command(name="create", help="Creates a channel.")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def _channel_create(self, ctx: commands.Context, channel_name : str = None):
        if not channel_name:
            e = discord.Embed(title='What do you want to name the channel?', color=main_color)
            await ctx.send(embed=e)
            def check(m : discord.Message):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg : discord.Message = await self.bot.wait_for('message', check=check, timeout=300)
                channel_name = msg.clean_content
                try:
                    new = await ctx.guild.create_text_channel(name=channel_name)
                    e2 = discord.Embed(description=f"**\👍🏻 Created the text channel: {new.mention}**")
                    return await ctx.send(embed=e2)
                except:
                    await ctx.send("Looks like I do not have the permissions to make a channel in this server.")
            except asyncio.TimeoutError:
                return await ctx.send("You did not specify a channel name on time.")
