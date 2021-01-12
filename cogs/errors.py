from discord.ext import commands
import discord
from bot import main_color, support_server_url, cross

def setup(client):
    client.add_cog(errors(client))

class errors(commands.Cog):

    def __init__(self, client):
        self.client = client

    def get_error_code_status(self, code : int):
        if code == 0:
            return "General error (such as a malformed request body, amongst other things)."
        elif code == 10001:
            return "Unknown account."
        elif code == 10002:
            return "Unknown application."
        elif code == 10003:
            return "Unknown channel."
        elif code == 10004:
            return "Unknown server."
        elif code == 10005:
            return "Unknown integration."
        elif code == 10006:
            return "Unknown invite."
        elif code == 10007:
            return "Unknown member."
        elif code == 10008:
            return "Unknown message."
        elif code == 10009:
            return "Unknown permission overwrite."
        elif code == 10010:
            return "Unknown provider."
        elif code == 10011:
            return "Unknown role."
        elif code == 10012:
            return "Unknown token."
        elif code == 10013:
            return "Unknown user."
        elif code == 10014:
            return "Unknown emoji."
        elif code == 10015:
            return "Unknown webhook."
        elif code == 10026:
            return "Unknown ban."
        elif code == 10027:
            return "Unknown SKU."
        elif code == 10028:
            return "Unknown Store Listing."
        elif code == 10029:
            return "Unknown entitlement."
        elif code == 10030:
            return "Unknown build."
        elif code == 10031:
            return "Unknown body."
        elif code == 10032:
            return "Unknown branch."
        elif code == 10036:
            return "Unknown redistributable."
        elif code == 10057:
            return "Unknown guild template."
        elif code == 20001:
            return "Bots cannot use this endpoint."
        elif code == 20002:
            return "Only bots can use this endpoint."
        elif code == 20022:
            return "This message cannot be edited due to announcement rate limits."
        elif code == 20028:
            return "The channel you are writing has hit the write rate limit."
        elif code == 30001:
            return "Maximum number of guilds reached (100)."
        elif code == 30002:
            return "Maximum number of friends reached (1000)."
        elif code == 30003:
            return "Maximum number of pins reached for the channel (50)."
        elif code == 30005:
            return "Maximum number of guild roles reached (250)."
        elif code == 30007:
            return "Maximum number of webhooks reached (10)."
        elif code == 30010:
            return "Maximum number of reactions reached (20)."
        elif code == 30013:
            return "Maximum number of guild channels reached (500)."
        elif code == 30015:
            return "Maximum number of attachments in a message reached (10)."
        elif code == 30016:
            return "Maximum number of invites reached (1000)."
        elif code == 40001:
            return "Unauthorized. Provide a valid token and try again."
        elif code == 40002:
            return "You need to verify your account in order to perform this action."
        elif code == 40005:
            return "Request entity too large. Try sending something smaller in size."
        elif code == 40006:
            return "This feature has been temporarily disabled server-side."
        elif code == 40007:
            return "The user is banned from this guild."
        elif code == 40033:
            return "This message has already been crossposted."
        elif code == 50001:
            return "Missing access."
        elif code == 50002:
            return "Invalid account type."
        elif code == 50003:
            return "Cannot execute action on a DM channel."
        elif code == 50004:
            return "Guild widget disabled."
        elif code == 50005:
            return "Cannot edit a message authored by another user."
        elif code == 50006:
            return "Cannot send an empty message."
        elif code == 50007:
            return "Cannot send messages to this user."
        elif code == 50008:
            return "Cannot send messages in a voice channel."
        elif code == 50010:
            return "OAuth2 application does not have a bot."
        elif code == 50011:
            return "OAuth2 application limit reached,"
        elif code == 50012:
            return "Invalid OAuth2 state."
        elif code == 50013:
            return "The bot does not have appropriate permissions to perform that action.\nMake sure the bot has `ADMINISTRATOR` permissions."
        elif code == 50014:
            return "Invalid authentication token provided."
        elif code == 50015:
            return "Note was too long."
        elif code == 50016:
            return "Provided too few or too many messages to delete. Must provide at least 2 and fewer than 100 messages to delete."
        elif code == 50019:
            return "A message can only be pinned to the channel it was sent in."
        elif code == 50020:
            return "Invite code was either invalid or taken."
        elif code == 50021:
            return "Cannot execute action on a system message."
        elif code == 50024:
            return "Cannot execute action on this channel type."
        elif code == 50025:
            return "Invalid OAuth2 access token provided."
        elif code == 50033:
            return "Invalid Recipient(s)."
        elif code == 50034:
            return "A message provided was too old to bulk delete."
        elif code == 50035:
            return "Invalid form body (returned for both application/json and multipart/form-data bodies), or invalid Content-Type provided."
        elif code == 50036:
            return "An invite was accepted to a guild the application's bot is not in."
        elif code == 50041:
            return "Invalid API version provided."
        elif code == 50074:
            return "Cannot delete a channel required for Community servers."
        elif code == 90001:
            return "Reaction was blocked."
        elif code == 130000:
            return "A message provided was too old to bulk delete."
        else:
            return "Unknown Error!"

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not hasattr(ctx.command, 'on_error'):
            error = getattr(error, "original", error)
            if isinstance(error, commands.NotOwner):
                e21 = discord.Embed(title="Sorry! Only Videro can use his command!", url="https://linktr.ee/videro", color=main_color)
                return await ctx.send(embed=e21)
            elif isinstance(error, commands.NoPrivateMessage):
                return await ctx.send(f'This command cannot be used in private messages. You will need to use this command on a server.\nYou can join this server to test all the commands :) {support_server_url}')
            elif isinstance(error, commands.MissingRequiredArgument):
                e2 = discord.Embed(
                    title=f"{ctx.author.name}, missing values in the command, type t-help {ctx.invoked_with} for more info.",
                    color=main_color)
                return await ctx.send(embed=e2)
            elif isinstance(error, commands.MissingPermissions):
                mPerms =  '\n'.join(f'**• `{str(x).replace("_", " ").replace("guild", "server").title()}`**' for x in error.missing_perms)
                e3 = discord.Embed(title=f"Uh oh!",
                                   description=f"Looks like you do not have the following permission{'' if len(error.missing_perms) == 1 else 's'}, which {'is' if len(error.missing_perms) == 1 else 'are'} required for this command -\n"
                                               f"{mPerms}",
                                   color=main_color)
                return await ctx.send(embed=e3)
            elif isinstance(error, discord.Forbidden):
                e0 = discord.Embed(title=f"Uh oh!",
                                   description=f"Looks like I ran into an error!\n```py\n{self.get_error_code_status(error.code)}\n```\n",
                                   color=main_color).set_footer(text="Please type t-support if it continues",
                                                                icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=e0)
            # elif isinstance(error, commands.CommandInvokeError):
            #     x : Exception = error.original
            #     if isinstance(x, discord.Forbidden):
            #         y = x.text
            #         return await ctx.send(f"Looks like I do not have the permission to do that!\n```py\n{y}\n```")
            elif isinstance(error, commands.BotMissingPermissions):
                return await ctx.send("I do not have the permission to do that!")
            elif isinstance(error, commands.CommandOnCooldown):
                e4 = discord.Embed(title=f"{ctx.author.name}, this command is on a cooldown! Try again in {round(int(error.retry_after)) if round(int(error.retry_after)) != 0 else '1.1'} seconds!",
                                   color=main_color)
                return await ctx.send(embed=e4)
            elif isinstance(error, commands.BadArgument):
                e5 = discord.Embed(
                    title=f"{ctx.author.name}, invalid argument provided, for more info type t-help {ctx.invoked_with if not isinstance(ctx.command, discord.ext.commands.Group) else ''}.",
                    color=main_color)
                return await ctx.send(embed=e5)
            elif isinstance(error, commands.NSFWChannelRequired):
                e6 = discord.Embed(
                    title=f"{cross} This channel needs to be NSFW to use `t-{ctx.invoked_with}`.",
                    color=main_color)
                return await ctx.send(embed=e6)
            elif isinstance(error, commands.CommandOnCooldown):
                e9 = discord.Embed(title="Please Wait!", color=main_color)
                e9.description = f"**The command `{ctx.message.content}` is on cooldown. Please try again in {round(int(error.retry_after))} seconds.**"
                return await ctx.send(embed=e9)
            elif isinstance(error, commands.CheckFailure):
                pass
            elif isinstance(error, commands.CommandNotFound):
                return await ctx.send(f"**{ctx.author.name}**, `{ctx.prefix}{ctx.invoked_with}` is not a valid command. Type `t-help` for more info.")
            else:
                await ctx.send(embed=discord.Embed(
                    title='Uh oh',
                    description=f'Looks like I ran into an error!\n```py\n{error}\n```',
                    color=discord.Colour.red()
                ).add_field(
                    name='More Help',
                    value=f"- Please report the error [**here**]({support_server_url}). We will try our best to fix it as soon as possible.\n"
                          f"- Thanks a lot for using **TrixZ** 💖",
                    inline=False
                ))
                videro = self.client.get_user(331084188268756993)
                await videro.send(f'**{ctx.author.name}** ({ctx.author.id}) ran into an error while using the command `{ctx.message.content}`.\n'
                                  f'Server - **{ctx.guild.name}** ({ctx.guild.id})\n'
                                  f'Channel name - {ctx.channel.name}\n'
                                  f'Channel ID - {ctx.channel.id} {ctx.channel.mention}\n'
                                  f'Error -\n'
                                  f'```py\n'
                                  f'{error}\n'
                                  f'```')
                raise error