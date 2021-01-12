import discord
from discord.ext import commands
from discord import Embed
import asyncio
import random
import datetime
import re
from bot import main_color, tick, cross
from _Utils import Message
import io
import os
import tempfile
from discord.ext.commands import TextChannelConverter
from bot import support_server_url, invite_url

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        self.argument = argument
        args = self.argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time

class moderation(commands.Cog):
    """Moderation commands only available to the administrators of the server!"""

    def __init__(self, client):
        self.client = client

    @commands.command(name="kick", help="Kicks the member mentioned.")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        await member.kick(reason=f'Kicked by {ctx.author.display_name} via TrixZ.')
        await ctx.message.add_reaction(tick)
        embed = discord.Embed(title=f"Successfully Kicked {member.display_name}.",
                              color=main_color)
        await ctx.send(embed=embed)

    """Ban"""

    @commands.command(name="ban", help="Bans the member mentioned.")
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        await member.ban()
        embed = discord.Embed(title=f"Successfully Banned {member.display_name}.",
                              color=main_color)
        await ctx.message.add_reaction(tick)
        await ctx.send(embed=embed)

    """Unban"""

    @commands.command(name="unban", help="Unbans the member mentioned.")
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx : commands.Context, user : discord.User = None, *, reason : str = None):
        if not reason:
            reason = "No Reason Provided"
        if user:
            bans = []
            for x in await ctx.guild.bans():
                bans.append(x[1])
            if user in bans:
                await ctx.guild.unban(member=user, reason=reason)
                embed = discord.Embed(title=f"Successfully Unbanned {str(user)}.", color=main_color)
                return await ctx.send(embed=embed)
            if not user in bans:
                embed = discord.Embed(title=f"The user {str(user)} is not banned!", color=main_color)
                return await ctx.send(embed=embed)
        if not user:
            embed = discord.Embed(title="You need to provide a user to unban!", color=main_color, description=
                                  "Example-\n"
                                  "**`t-unban Ninja He apologized :)`**\n"
                                  "**`t-unban 331084188268756993 Hes nice now :)`**")
            return await ctx.send(embed=embed)


    """Nick"""

    @commands.command(name="nick", help="Changes the nickname of the member mentioned.", aliases=['setnick', 'nickname'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member = None, *, nick : str = None):
        if not nick:
            await Message.EmbedText(
                title=f'Please mention the nickname to change to.',
                color=main_color
            ).send(ctx)
        if not member:
            await Message.EmbedText(
                title=f'Please mention the member to change the nickname of.',
                color=main_color
            ).send(ctx)
        if member and nick:
            await ctx.channel.purge(limit=1)
            guilds = self.client.guilds
            embed = discord.Embed(title=f"{tick} Successfully changed {member.display_name}'s Nickname to __{nick}__.",
                                  color=main_color)
            await member.edit(nick=nick)
            await ctx.send(embed=embed)

    @commands.command(name='mute', help='Mutes the member mentioned for the time period specified!')
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_roles=True, manage_channels=True, manage_guild=True)
    async def mute(self, ctx, duration : TimeConverter = None, member: discord.Member = None):
        if not duration:
            await Message.EmbedText(
                title='Please mention a duration in d/h/m/s',
                color=discord.Color.red()
            ).send(ctx)
        elif not member:
            await Message.EmbedText(
                title='Please mention a member to mute.',
                color=discord.Color.red()
            ).send(ctx)
        if duration and member:
            mute_role = discord.utils.find(lambda m: m.name == 'Muted', ctx.guild.roles)
            if mute_role:
                roles = []
                for role1 in member.roles[1:]:
                    roles.append(role1)
                    await member.remove_roles(role1)
                await member.add_roles(mute_role)
                await Message.EmbedText(
                    title=f'Successfully muted {member.display_name} for {str((duration))}.',
                    color=main_color,
                    delete_after=10
                ).send(ctx)
                await asyncio.sleep(int(duration))
                await member.remove_roles(mute_role)
                for role3 in roles:
                    await member.add_roles(role3)
                await Message.EmbedText(
                    title=f'{member.display_name} has been un-muted.',
                    color=main_color,
                    delete_after=10
                ).send(ctx)
            if not mute_role:
                x = await Message.EmbedText(
                    title='Did not find a muted role, creating one.',
                    color=main_color
                ).send(ctx)
                mute_role1 = await ctx.guild.create_role(name='Muted',color=discord.Color(value=main_color), reason='Creating Muted role as it does not exist.',
                                            permissions=discord.Permissions(send_messages = False, read_messages=True))
                await ctx.guild.edit_role_positions(positions={mute_role1 : 5})
                roles = []
                for role2 in member.roles[1:]:
                    roles.append(role2)
                    await member.remove_roles(role2)
                await member.add_roles(mute_role1)
                await Message.EmbedText(
                    title=f'Successfully muted {member.display_name} for {int(duration)} seconds.',
                    color=main_color,
                    delete_after=10
                ).send(ctx)
                await x.delete()
                await asyncio.sleep(int(duration))
                await member.remove_roles(mute_role1)
                for role4 in roles:
                    await member.add_roles(role4)
                await Message.EmbedText(
                    title=f'{member.display_name} has been un-muted.',
                    color=main_color,
                    delete_after=10
                ).send(ctx)

    @commands.command(name='unmute', help='Unmutes the member mentioned, if the member is muted.')
    @commands.has_permissions(manage_channels=True, manage_roles = True, manage_guild = True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member = None):
        if not member:
            await Message.EmbedText(
                title='Please mention a member to un-mute.',
                color=discord.Color.red()
            ).send(ctx)
        if member:
            mute_role = discord.utils.find(lambda m: m.name == 'Muted', ctx.guild.roles)
            if mute_role:
                await member.remove_roles(mute_role)
                await ctx.message.add_reaction(tick)
                await Message.EmbedText(
                    title=f'Successfully unmuted {member.display_name}.',
                    color=main_color
                ).send(ctx)
            if not mute_role:
                await Message.EmbedText(
                    title=f'{member.display_name} is not muted!',
                    color=main_color
                ).send(ctx)

def setup(client):
    client.add_cog(moderation(client))