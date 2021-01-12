from discord.ext import commands
import discord
import asyncio
from bot import main_color, cross, tick
import emojis

def setup(client):
    client.add_cog(revamp(client))

class revamp(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client

    @commands.command(name='revamp', help="Revamps the server! (Fully Customizable!)")
    @commands.has_permissions(manage_guild=True, manage_channels=True, manage_roles=True)
    @commands.cooldown(1, 10)
    @commands.guild_only()
    async def revamp(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)
        fetch = await self.client.pg_con.fetch("SELECT * FROM revamps WHERE guild_id = $1", guild_id)
        one = "┃"
        two = "┇"
        three = "┝"
        four = "╏"
        five = "║"
        six = "╠"
        seven = "▪"
        if not fetch:
            e6 = discord.Embed(color=main_color, title="Select an emoji!")
            e6.description = f"Hey {ctx.author.name}!\n" \
                             f"- Please **react with a default emoji** which will be the main emoji of the server!\n" \
                             f"- You have **2 minutes** to react with an emoji."
            e6.set_image(url="https://cdn.discordapp.com/attachments/718627431673626664/768396240052158464/revamp.gif")
            ask = await ctx.send(embed=e6)

            def rcheck(reaction, user):
                return user == ctx.author and reaction.message == ask

            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=120, check=rcheck)
                if reaction.custom_emoji:
                    e5 = discord.Embed(title="Uh oh", color=discord.Colour.red())
                    e5.description = f"Sorry, you cannot use custom emojis, discord does not allow custom emojis in the channel/role names.\nPlease run the command again and choose a default discord emoji :)"
                    return await ctx.send(embed=e5)
                if not reaction.custom_emoji:
                    # ("┃", "┇", "┝", "╏", "║", "╠", "▪")
                    await ctx.send(f"Alright! The emoji will be `{reaction.emoji}`!")
                    await asyncio.sleep(0.5)
                    await ctx.send(
                        f"{ctx.author.mention} Please choose one of the following dividers for the channel names.\n"
                        f":one: - `{reaction.emoji}{one}#channel-name`\n"
                        f":two: - `{reaction.emoji}{two}#channel-name`\n"
                        f":three: - `{reaction.emoji}{three}#channel-name`\n"
                        f":four: - `{reaction.emoji}{four}#channel-name`\n"
                        f":five: - `{reaction.emoji}{five}#channel-name`\n"
                        f":six: - `{reaction.emoji}{six}#channel-name`\n"
                        f":seven: - `{reaction.emoji}{seven}#channel-name`\n\n"
                        f"Please reply with the **number** of divider you choose below :point_down_tone3:")
                    typeOfDivider: discord.Message = await self.client.wait_for('message', timeout=250, check=lambda
                        x: x.author == ctx.author and x.channel == ctx.channel and x.content in (
                    "1", "2", "3", "4", "5", "6", "7") and len(x.content) == 1)

                    async def revamp(emoji: str, divider: str):
                        eta = len(ctx.guild.text_channels) + len(ctx.guild.voice_channels) + len(
                            ctx.guild.categories) + len(ctx.guild.roles)
                        init = discord.Embed(color=main_color, title="Starting!")
                        init.description = f"Starting revamping the server with the following options in 5 seconds.\n" \
                                           f"Emoji - **`{emoji}`**\n" \
                                           f"Divider - **`{divider}`**\n" \
                                           f"ETA - **{eta}** seconds."
                        init.set_footer(text=f"Command used by {ctx.author.name}")
                        await ctx.send(embed=init)
                        await asyncio.sleep(5)
                        await ctx.guild.edit(name=f"{emoji}{divider}{ctx.guild.name}",
                                             reason=f"Revamping the server | Asked by {ctx.author.name}")
                        for x in ctx.guild.text_channels:
                            await asyncio.sleep(1)
                            await x.edit(name=f"{emoji}{divider}{x.name}",
                                         reason=f"Revamping the server | Asked by {ctx.author.name}")
                        await ctx.send(f"✅ Revamped {len(ctx.guild.text_channels)} text channels successfully!")
                        for x in ctx.guild.voice_channels:
                            await asyncio.sleep(1)
                            await x.edit(name=f"{emoji}{divider}{x.name}",
                                         reason=f"Revamping the server | Asked by {ctx.author.name}")
                        await ctx.send(f"✅ Revamped {len(ctx.guild.voice_channels)} voice channels successfully!")
                        for x in ctx.guild.categories:
                            await asyncio.sleep(1)
                            await x.edit(name=f"{emoji}{divider}{x.name}",
                                         reason=f"Revamping the server | Asked by {ctx.author.name}")
                        await ctx.send(f"✅ Revamped {len(ctx.guild.categories)} categories successfully!")
                        success = 0
                        fail = 0
                        for x in ctx.guild.roles:
                            try:
                                await asyncio.sleep(1)
                                await x.edit(name=f"{emoji}{divider}{x.name}")
                                success += 1
                            except:
                                fail += 1
                                pass
                        await ctx.send(f"✅ Revamped {success} role{'s' if success != 1 else ''} successfully!")
                        await self.client.pg_con.execute(
                            "INSERT INTO revamps (guild_id, emoji, divider) VALUES ($1, $2, $3)", guild_id, emoji,
                            divider)
                        e3 = discord.Embed(color=main_color,
                                           title="Success!",
                                           description=f"🎉 Successfully revamped the server!").add_field(
                            name="Emoji",
                            value=emoji
                        ).add_field(
                            name="Divider",
                            value="`" + divider + "`"
                        ).add_field(
                            name="More Info",
                            value="To reset the revamp, type `t-resetrevamp`.\n",
                            inline=False
                        )

                    if typeOfDivider.content == "1":
                        await revamp(emoji=str(reaction.emoji), divider=one)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #               f"Emoji - `{reaction.emoji}`\n"
                        #               f"Divider - `{one}`")
                        return
                    elif typeOfDivider.content == "2":
                        await revamp(emoji=str(reaction.emoji), divider=two)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #               f"Emoji - `{reaction.emoji}`\n"
                        #               f"Divider - `{two}`")
                        return
                    elif typeOfDivider.content == "3":
                        await revamp(emoji=str(reaction.emoji), divider=three)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #                f"Emoji - `{reaction.emoji}`\n"
                        #                f"Divider - `{three}`")
                        return
                    elif typeOfDivider.content == "4":
                        await revamp(emoji=str(reaction.emoji), divider=four)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #                f"Emoji - `{reaction.emoji}`\n"
                        #                f"Divider - `{four}`")
                        return
                    elif typeOfDivider.content == "5":
                        await revamp(emoji=str(reaction.emoji), divider=five)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #                f"Emoji - `{reaction.emoji}`\n"
                        #                f"Divider - `{five}`")
                        return
                    elif typeOfDivider.content == "6":
                        await revamp(emoji=str(reaction.emoji), divider=six)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #                f"Emoji - `{reaction.emoji}`\n"
                        #                f"Divider - `{six}`")
                        return
                    elif typeOfDivider.content == "7":
                        await revamp(emoji=str(reaction.emoji), divider=seven)
                        # await ctx.send(f"🎉 Successfully revamped the server!\n"
                        #                f"Emoji - `{reaction.emoji}`\n"
                        #                f"Divider - `{seven}`\n\n"
                        #                f"You can undo the changes by the command `t-resetrevamp`")
                        return
                    elif typeOfDivider.content.lower() == "exit":
                        await ctx.message.add_reaction(tick)
                        return await ctx.send("Successfully exit.")
            except BaseException as eE:
                if isinstance(eE, asyncio.TimeoutError):
                    e8 = discord.Embed(title="You did not reply in time!", color=main_color)
                    await ctx.send(embed=e8)
                else:
                    e9 = discord.Embed(title="Uh Oh", color=main_color,
                                       description=f"Looks like I ran into an error. Please make sure I have the `Administrator` permission. Try again.")
                    await ctx.send(embed=e9)
                    raise eE
        if fetch:
            data = fetch[0]
            e = discord.Embed(color=main_color, title="Already Revamped!")
            e.description = f"Hey {ctx.author.mention}, this server has already been revamped!\nIf you want to reset the revamp done, type **`t-resetrevamp`**"
            e.add_field(name="Emoji", value="\\" + data["emoji"], inline=False)
            e.add_field(name="Divider", value=f"`{data['divider']}`", inline=False)
            return await ctx.send(embed=e)

    @commands.command(name='resetrevamp', help="Resets the revamp, if the server has been revamped.")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def resetrevamp(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)
        check = await self.client.pg_con.fetch("SELECT * FROM revamps WHERE guild_id = $1", guild_id)
        if check:
            vcCount = len(ctx.guild.voice_channels)
            textCount = len(ctx.guild.text_channels)
            catCount = len(ctx.guild.categories)
            vcCheck = 0
            textCheck = 0
            catCheck = 0
            for x in ctx.guild.voice_channels:
                if len(emojis.get(x.name)) == 1:
                    vcCheck += 1
            for x in ctx.guild.text_channels:
                if len(emojis.get(x.name)) == 1:
                    textCheck += 1
            for x in ctx.guild.categories:
                if len(emojis.get(x.name)) == 1:
                    catCheck += 1
            if vcCheck == vcCount and textCheck == textCount and catCount == catCheck:
                await self.client.pg_con.execute("DELETE FROM revamps WHERE guild_id = $1", guild_id)
                await ctx.send("Resetting the revamp in 3 seconds.")
                await asyncio.sleep(3)
                await ctx.guild.edit(name=ctx.guild.name[2:],
                                     reason=f"Un-Revamping the server | Asked by {ctx.author.name}")
                for x in ctx.guild.text_channels:
                    await asyncio.sleep(1)
                    await x.edit(name=f"{x.name[2:]}", reason=f"Un-Revamping the server | Asked by {ctx.author.name}")
                await ctx.send(f"✅ Reset all the text channels successfully!")
                for x in ctx.guild.voice_channels:
                    await asyncio.sleep(1)
                    await x.edit(name=f"{x.name[2:]}", reason=f"Un-Revamping the server | Asked by {ctx.author.name}")
                await ctx.send(f"✅ Reset all the voice channels successfully!")
                for x in ctx.guild.categories:
                    await asyncio.sleep(1)
                    await x.edit(name=f"{x.name[2:]}", reason=f"Un-Revamping the server | Asked by {ctx.author.name}")
                await ctx.send(f"✅ Reset all the categories successfully!")
                for x in ctx.guild.roles:
                    try:
                        await asyncio.sleep(1)
                        await x.edit(name=x.name[2:], reason=f"Un-Revamping the server | Asked by {ctx.author.name}")
                    except:
                        pass
                await ctx.send(f"✅ Reset most of the roles successfully!")
                await asyncio.sleep(0.3)
                await ctx.send(f"✅ Reset the server successfully!")
                return

            else:
                return await ctx.send(f"There is an exception.\n"
                                      f"- A channel/role/category **does not have an emoji/divider** in its name.\n"
                                      f"- Make sure that all the channels/roles/categories have their **first 2 characters same**.\n\n"
                                      f"If this problem continues, please type **`t-support`** and we will be happy to help. Thanks")
        if not check:
            e9 = discord.Embed(color=main_color, title="Server not revamped!",
                               description=f"The server **{ctx.guild.name}** has not been revamped yet!\n"
                                           f"To revamp the server, simply type **`t-revamp`**")
            return await ctx.send(embed=e9)