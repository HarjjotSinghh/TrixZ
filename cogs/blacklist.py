import discord
from discord.ext import commands
from bot import main_color

def setup(client):
    client.add_cog(blacklist(client))

class blacklist(commands.Cog):
    """"Blacklist commands which can blacklist channels and users."""
    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.group(name="blacklist", aliases=["bl"], case_insensitive=True)
    async def blacklist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return await ctx.invoke(self.client.get_command('blacklisthelp'))

    @blacklist.command(name="channel", help="Blacklists the channel mentioned.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True, manage_guild=True, manage_roles=True)
    async def _bl_channel(self, ctx : commands.Context, channel: discord.TextChannel = None):
        query = "INSERT INTO blacklist (channel_id) VALUES ($1)"
        channel = ctx.channel if not channel else channel
        await self.client.pg_con.execute(query, str(channel.id))
        e = discord.Embed(color=main_color, title=f"Successfully blacklisted {channel.name}.")
        return await ctx.send(embed=e)

    # @blacklist.command(name="user", help="Blacklists the channel mentioned.")
    # @commands.is_owner()
    # async def _bl_user(self, ctx: commands.Context, user: discord.Member) :
    #     query = "INSERT INTO blacklist (channel_id, user_id) VALUES ($1, $2)"
    #     await self.client.pg_con.execute(query, None, str(user.id))
    #     e = discord.Embed(color=main_color, title=f"Successfully blacklisted {str(user)}.")
    #     return await ctx.send(embed=e)

    @blacklist.command(name="remove", help="Removes a channel from the blacklist, if it has been blacklisted.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True, manage_guild=True, manage_roles=True)
    async def _bl_remove(self, ctx: commands.Context, channel : discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        query = "SELECT * FROM blacklist WHERE channel_id = $1"
        check = await self.client.pg_con.fetch(query, str(channel.id))
        if not check:
            e = discord.Embed(title=f"{channel.name} is not blacklisted.", color=main_color)
            return await ctx.send(embed=e)
        if check:
            query2 = "DELETE FROM blacklist WHERE channel_id = $1"
            await self.client.pg_con.execute(query2, str(channel.id))
            e = discord.Embed(title=f"Successfully removed {channel.name} from the blacklist.", color=main_color)
            return await ctx.send(embed=e)