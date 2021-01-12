from discord.ext import commands
import discord
from bot import main_color, cross, tick
import datetime
from _Utils.Message import EmbedText as etext

def setup(client):
    client.add_cog(rr(client))

class rr(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.group(name='rr')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def rr(self, ctx : commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('rrhelp'))
            return 

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role :discord.Role):
        all_roles = await self.client.pg_con.fetch("SELECT role_id FROM reaction_roles")
        for i in all_roles:
            if i["role_id"] == str(role.id):
                await self.client.pg_con.execute("DELETE FROM reaction_roles WHERE role_id = $1", str(role.id))
                return

    @commands.Cog.listener()
    async def on_message_delete(self, message : discord.Message):
        all_messages = await self.client.pg_con.fetch("SELECT message_id FROM reaction_roles")
        for i in all_messages:
            if i["message_id"] == str(message.id):
                await self.client.pg_con.execute("DELETE FROM reaction_roles WHERE message_id = $1", str(message.id))

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild : discord.Guild, before : list, after : list):
        removed = []
        for emoji in before:
            if emoji not in after:
                removed.append(emoji)
        if removed != []:
            all_emojis = await self.client.pg_con.fetch("SELECT emoji FROM reaction_roles")
            for i in all_emojis:
                if str(i["emoji"]) == str(removed[0]):
                    await self.client.pg_con.execute("DELETE FROM reaction_roles WHERE emoji = $1 AND guild_id = $2", str(i["emoji"]), str(guild.id))
                    return
        else:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        all_messages = await self.client.pg_con.fetch("SELECT * FROM reaction_roles WHERE guild_id = $1", guild_id)
        for message in all_messages:
            if payload.message_id == int(message["message_id"]):
                emoji1 = await self.client.pg_con.fetch("SELECT emoji FROM reaction_roles WHERE message_id = $1", message["message_id"])
                role1 = await self.client.pg_con.fetch("SELECT role_id FROM reaction_roles WHERE message_id = $1", message["message_id"])
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(int(role1[0]["role_id"]))
                emoji = emoji1[0]["emoji"]
                if str(payload.emoji) == emoji:
                    if role != None:
                        await payload.member.add_roles(role)
                        e = discord.Embed(title="🎃 Role Given", description=f"The **{role.name}** role was given to you in **{guild.name}**", color=main_color)
                        e.set_footer(text=f"ID : {payload.member.id}")
                        e.timestamp = datetime.datetime.utcnow()
                        await payload.member.send(embed=e)
                        return
            else:
                return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        all_messages = await self.client.pg_con.fetch("SELECT * FROM reaction_roles WHERE guild_id = $1", guild_id)
        #channel = self.client.get_channel(758741983081922600)
        #await channel.send(all_messages)
        for message in all_messages:
            if payload.message_id == int(message["message_id"]):
                emoji1 = await self.client.pg_con.fetch("SELECT emoji FROM reaction_roles WHERE message_id = $1",
                                                        message["message_id"])
                role1 = await self.client.pg_con.fetch("SELECT role_id FROM reaction_roles WHERE message_id = $1",
                                                       message["message_id"])
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(int(role1[0]["role_id"]))
                emoji = emoji1[0]["emoji"]
                if str(payload.emoji) == emoji:
                    if role != None:
                        member = guild.get_member(payload.user_id)
                        await member.remove_roles(role)
                        e = discord.Embed(title="🎃 Role Removed",
                                          description=f"The **{role.name}** role was removed from you in **{guild.name}**",
                                          color=main_color)
                        e.set_footer(text=f"ID • {payload.user_id}")
                        e.timestamp = datetime.datetime.utcnow()
                        await member.send(embed=e)
            else:
                return

    @rr.command(name="add", help="Adds reaction roles to a message.")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_channels = True, manage_messages=True, manage_guild=True)
    async def rr_add(self, ctx : commands.Context, message_id : discord.Message, emoji : str, role: discord.Role):
        guild_id = str(ctx.guild.id)
        role_id = str(role.id)
        await self.client.pg_con.execute("INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id) VALUES ($1, $2, $3, $4)", guild_id, str(message_id.id), emoji, role_id)
        message = await ctx.channel.fetch_message(int(message_id.id))
        await message.add_reaction(emoji)
        e = discord.Embed(title=f"{tick}  Success", description=f"Successfully setup the reaction roles.", color=main_color)
        e.add_field(
            name='Role',
            value=role.mention
        )
        e.add_field(
            name='Emoji',
            value=f"{emoji}",
        )
        e.add_field(
            name="Message",
            value=f"[Click here]({message_id.jump_url})"
        )
        await ctx.send(embed=e)
        return

    @rr.command(name="remove", help="Removes reaction roles from a message, if a reaction role exists on the message.")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_channels = True, manage_messages=True, manage_guild=True)
    async def rr_remove(self, ctx: commands.Context, message_id: discord.Message = None):
        if not message_id:
            await ctx.send(f"You did not specify a message ID. Try again.")
            return
        exists = await self.client.pg_con.fetchrow("SELECT * FROM reaction_roles WHERE message_id = $1", str(message_id.id))
        if exists:
            emoji = exists["emoji"]
            role1 = exists["role_id"]
            role = ctx.guild.get_role(int(role1))
            await self.client.pg_con.execute("DELETE FROM reaction_roles WHERE message_id = $1", str(message_id.id))
            message = await ctx.channel.fetch_message(int(exists["message_id"]))
            await message.clear_reaction(emoji)
            e = discord.Embed(color=main_color, title=f"{tick}  Success", description=f"Successfully removed the reaction roles.")
            e.add_field(
                name="Role",
                value=role.mention
            )
            e.add_field(
                name="Emoji",
                value=emoji
            )
            e.add_field(
                name="Message",
                value=f"[Click here]({message_id.jump_url})",

            )
            await ctx.send(embed=e)
            return
        if not exists:
            await etext(
                title=f"{cross} No reaction roles are set on that message!",
                description=f"For more info reply with `t-help rr`.",
                color=discord.Color.red()
            ).send(ctx)
            return

    @rr.command(name="show", help="Shows all the active reaction roles in the server.")
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_channels = True, manage_messages=True, manage_guild=True)
    async def rr_show(self, ctx : commands.Context):
        guild_id = str(ctx.guild.id)
        show = await self.client.pg_con.fetch("SELECT * FROM reaction_roles WHERE guild_id = $1", guild_id)
        desc = ""
        num = 0
        if show:
            for i in show:
                num += 1
                role1 = i["role_id"]
                role = ctx.guild.get_role(int(role1))
                desc += f"{i['emoji']} → Message ID - {i['message_id']} • Role - {role.mention}\n"
            e = discord.Embed(title="Reaction Roles", description=f"**There are {len(show)} reaction roles setup in {ctx.guild.name}.**\n───────────────────────────────\n{desc}", colour=main_color)
            e.set_footer(text="Server ID : " + str(ctx.guild.id))
            await ctx.message.add_reaction(tick)
            await ctx.send(embed=e)
            return

        if not show:
            await ctx.message.add_reaction(cross)
            await etext(
                title=f"{cross}  There are not any reaction roles setup!",
                description=f"For more info reply with `t-help rr`.",
                color=discord.Color.red()
            ).send(ctx)
            return