import discord
from discord.ext import commands
import asyncio
import datetime
from bot import tick, cross, main_color
from _Utils import Message

def setup(client):
    client.add_cog(roles(client))

class roles(commands.Cog):
    """Role managing commands which are only accessible to the administrators and owners of the server except a few commands!"""

    def __init__(self, client):
        self.client = client

    @commands.group(name='role')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def _role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('rolehelp'))

    @_role.command(name='add', help='Adds the role name mentioned!')
    @commands.has_permissions(manage_roles=True, manage_nicknames=True, kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def role_add(self, ctx, *, role_name : str):
        guild = ctx.guild
        await Message.EmbedText(
            title=f'Are you sure you want to add the role named "{role_name}"?',
            color=main_color
        ).send(ctx)
        wait = await self.client.wait_for('message', timeout=120, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content in ('y', 'yes', 'n', 'no', 'ya', 'na', 'yeah', 'nope'))
        if wait.content.lower() in ('y', 'yes', 'ya', 'yeah', 'yep', 'yah'):
            role = await guild.create_role(name=role_name, reason=f'{ctx.author.name} told me to add it.', hoist=False, mentionable=False)
            await ctx.message.add_reaction(tick)
            await Message.EmbedText(
                title=f'{tick} Successfully created the role "{role_name}"',
                color=main_color
            ).send(ctx)

        elif wait.content.lower() in ('n', 'no', 'na','nope', 'nah'):
            await ctx.message.add_reaction(tick)
            await Message.EmbedText(
                title=f'Ok...',
                color=main_color
            ).send(ctx)

    @_role.command(name='delete', help='Deletes the role mentioned!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def _delete(self, ctx, role: discord.Role):
        guild = ctx.guild
        await Message.EmbedText(
            title=f'Are you sure you want to add the role named "{role.name}"?',
            color=main_color
        ).send(ctx)
        wait = await self.client.wait_for('message', timeout=120, check=lambda
            x: x.author == ctx.author and x.channel == ctx.channel and x.content in (
        'y', 'yes', 'n', 'no', 'ya', 'na', 'yeah', 'nope'))
        if wait.content.lower() in ('y', 'yes', 'ya', 'yeah'):
            await role.delete(reason=f'{ctx.author.name} told me to do it :)')
            await ctx.message.add_reaction(tick)
            await Message.EmbedText(
                title=f'{tick} Successfully deleted the role "{role.name}"!',
                color=discord.Color.green()
            ).send(ctx)

        elif wait.content.lower() in ('n', 'no', 'na', 'nope'):
            await ctx.message.add_reaction(tick)
            await Message.EmbedText(
                title=f'Ok... I wont... Sad...',
                color=discord.Color.red()
            ).send(ctx)

    @_role.command(name='give_all', help='Gives the mentioned role to all the members of the server!')
    @commands.has_permissions(manage_roles=True, manage_nicknames=True, kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def role_all(self, ctx, role: discord.Role = None):
        if not role:
            await Message.EmbedText(
                title=f'Please mention a role.',
                color=main_color
            ).send(ctx)
            return
        if role:
            add_in = []
            for member in ctx.guild.members:
                if not role in member.roles:
                    add_in.append(member)
            send = await Message.EmbedText(
                    title=f'Adding the role {role.name} to {len(add_in)} members.\n ETA - {len(add_in)} seconds.',
                    color=main_color
                ).send(ctx)
            for member in add_in:
                await member.add_roles(role)
                await Message.EmbedText(
                    title=f'Added the role {role.name} to {member.name}',
                    color=main_color
                ).edit(message=send, ctx=ctx)
            await Message.EmbedText(
                title=f'Successfully added the role {role.name} to {len(add_in)} members.',
                color=main_color
            ).edit(ctx=ctx, message=send)
            await ctx.message.add_reaction(tick)

    @_role.command(name='take_all', help='Gives the mentioned role to all the members of the server!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_roles=True, manage_nicknames=True, kick_members=True)
    async def remove_all(self, ctx, role: discord.Role = None):
        if not role:
            await Message.EmbedText(
                title=f'Please mention a role.',
                color=main_color
            ).send(ctx)
            return
        if role:
            remove_in = []
            for member in ctx.guild.members:
                if role in member.roles:
                    remove_in.append(member)
            send = await Message.EmbedText(
                title=f'Adding the role {role.name} to {len(remove_in)} members.\n ETA - {len(remove_in)} seconds.',
                color=main_color
            ).send(ctx)
            for member in remove_in:
                await member.remove_roles(role)
                await Message.EmbedText(
                    title=f'Removed the role {role.name} from {member.name}',
                    color=main_color
                ).edit(message=send, ctx=ctx)
            await Message.EmbedText(
                title=f'Successfully removed the role {role.name} from {len(remove_in)} members.',
                color=main_color
            ).edit(ctx=ctx, message=send)
            await ctx.message.add_reaction(tick)

    @_role.command(name='list', help='Lists all roles of the server!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def _list(self, ctx, server = None):
        server = ctx.guild if not server else server
        Roles = [role for role in server.roles]
        Roles.pop(0)
        await ctx.message.add_reaction(tick)
        await Message.EmbedText(
            title=f'All roles in {server.name}',
            description=''.join(f'{b.mention}\n' for a,b in enumerate(Roles, 1)),
            color=main_color
        ).send(ctx)

    @_role.command(name='give',help='Gives the role mentioned to the member mentioned!')
    @commands.has_permissions(manage_roles=True, manage_nicknames=True, kick_members=True)
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def give(self, ctx, member:discord.Member = None, role:discord.Role = None):
        if not role:
            await Message.EmbedText(
                title='Please specify the role, `t-role give @member @role`',
                color=discord.Color.red()
            ).send(ctx)
        if not member:
            await Message.EmbedText(
                title='Please specify the member, `t-role give @member @role`',
                color=discord.Color.red()
            ).send(ctx)
        if member and role:
            await member.add_roles(role)
            await Message.EmbedText(
                title=f'Successfully gave the role {role.name} to {member.name}',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(tick)

    @_role.command(name='take', help='Takes the role mentioned from the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_roles=True, manage_nicknames=True, kick_members=True)
    async def take(self, ctx, member:discord.Member = None, role:discord.Role = None):
        if not role:
            await Message.EmbedText(
                title='Please specify the role, `t-role take @member @role`',
                color=discord.Color.red()
            ).send(ctx)
        if not member:
            await Message.EmbedText(
                title='Please specify the member, `t-role take @member @role`',
                color=discord.Color.red()
            ).send(ctx)
        if member and role:
            await member.remove_roles(role)
            await Message.EmbedText(
                title=f'Successfully took the role {role.name} from {member.name}',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(tick)