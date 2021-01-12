import discord
from discord.ext import commands
from discord import Embed
import asyncio
from  bot import tick, cross
main_color = 0x40cc88
questions = [
        'Do you want to apply as GFX Designer or VFX Editor?',
        'Whats your real name and Age?',
        'Send your portfolio-',
        'Since When have you been designing/editing?',
        'Why do you want to join VX?',
    ]
answers = []

def vx_check(ctx):
    return ctx.guild.id == 690494216572239922

from time import sleep

class vx(commands.Cog):
    """Commands which can only be used in the [VX](https://www.discord.com/invite/keMaPa6/) server!"""

    def __init__(self, client):
        self.client = client

    @commands.command(name="new", help="Creates a ticket on the server.", aliases=["buy", "order"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def new(self, ctx, *, product: str):
        guild = ctx.message.guild
        if guild.id == 690494216572239922:
            category = discord.utils.get(guild.categories, name="🔰┃Orders")
            ticket_channel = await guild.create_text_channel(name=f"🔰┃order-{ctx.author.name}", category=category,
                                                             topic=f"{ctx.author.name} wants to order {product}.")
            role1 = ctx.guild.get_role(692753853963173928)
            await ticket_channel.set_permissions(role1, send_messages=True, read_messages=True, add_reactions=True,
                                                 embed_links=True, attach_files=True, read_message_history=True,
                                                 external_emojis=True)

            role2 = ctx.guild.get_role(699148926313299969)
            await ticket_channel.set_permissions(role2, send_messages=True, read_messages=True, add_reactions=True,
                                                 embed_links=True, attach_files=True, read_message_history=True,
                                                 external_emojis=True)

            await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True,
                                                 embed_links=True, attach_files=True, read_message_history=True,
                                                 external_emojis=True)

            await ticket_channel.send("|| @everyone ||")
            await ticket_channel.purge(limit=1)

            em = discord.Embed(title=f"Hey {ctx.author.display_name}!",
                               description=f"{ctx.author.mention} You will be contacted by the team as soon as possible!\nUntill then, you can try using `t-portfolios` to view the portfolios of the team members and `t-prices` to view the prices of our services!",
                               color = main_color)
            em.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')
            em.set_footer(text=f"Ticket created by {ctx.author.display_name}.", icon_url=ctx.author.avatar_url)
            await ticket_channel.send(embed=em)

            em2 = discord.Embed(color = main_color,
                                title=f"{tick} Ticket was successfully created - {ticket_channel.mention}.")
            await ctx.message.add_reaction(tick)
            await ctx.send(embed=em2)
            await ctx.author.send(embed=em2)
        else:
            e = discord.Embed(description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**', colour=discord.Color.red())
            await ctx.send(embed=e)

    @commands.command(name="apply", help="Sends you DM regarding the info to apply for VX.")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def apply(self, ctx):
        if ctx.guild.id == 690494216572239922:
            answers = []
            submit_channel = self.client.get_channel(742181947396194304)
            channel = await ctx.author.create_dm()
            videro = self.client.get_user(id=331084188268756993)
            clurdy = self.client.get_user(668301845873295360)
            ISA = self.client.get_user(498808686345453580)
            await ctx.message.add_reaction(tick)
            await ctx.send(f"{ctx.author.mention} DM Sent!")

            def check(m):
                return m.content is not None and m.author == ctx.author and m.channel == channel

            for question in questions:
                sleep(.5)
                await channel.send(question)
                msg = await self.client.wait_for('message', check=check)
                answers.append(msg.content)

            submit_wait = True
            while submit_wait:
                await channel.send(f"Are you sure you want to send this application? Type `yes` to finish.")
                msg = await self.client.wait_for('message', check=check)
                if "yes" in msg.content.lower():
                    await msg.add_reaction(tick)
                    await channel.send(f"{ctx.author.mention}, Your application was successfully sent!")
                    submit_wait = False
                    answers1 = "\n".join(f'{a}. {b}' for a, b in enumerate(answers, 1))
                    submit_msg = f"Application From {msg.author.mention} \n\nThe Answers are- \n{answers1}"
                    await submit_channel.send(f"@everyone", delete_after=0.5)
                    await submit_channel.send(submit_msg)
                    await videro.send(submit_msg)
        else:
            e = discord.Embed(
                description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**',
                colour=discord.Color.red())
            await ctx.send(embed=e)

    @commands.command(name="portfolios", help="Sends a list of all the portfolios of the VX members.")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def portfolios(self, ctx):
        if ctx.guild.id == 690494216572239922:
            embed = discord.Embed(title=f"VX Portfolios", description=f"\nVX Videro's Portfolio-"
                                                                      f"\n```t-portfolio VideroDesigns.```"
                                                                      f"\n\nVX Harxu's Portfoslio-"
                                                                      f"\n```t-portfolio Harxu Designs```"
                                                                      f"\n\nVX Kai's Portfolio-"
                                                                      f"\n```t-portfolio NxT Kai```"
                                                                      f"\n\nVX MetalOoze's Portfolio-"
                                                                      f"\n```t-portfolio MetalOoze```"
                                                                      f"\n\nVX ItzNinja518's Portfolio-"
                                                                      f"\n```t-portfolio ItzNinja518```"
                                                                      f"\n\nVX VXNM's Portfolio-"
                                                                      f"\n```t-portfolio VXNM```", color = main_color)
            embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')
            embed.set_footer(text=f"VX™")
            await ctx.send(embed=embed)
        else:
            e = discord.Embed(
                description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**',
                colour=discord.Color.red())
            await ctx.send(embed=e)

    @commands.command(name="portfolio", help="Sends the portfolio of the VX member mentioned.")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def portfolio(self, ctx, *, vx_member: discord.User):
        if ctx.guild.id == 690494216572239922:
            harxu_embed = discord.Embed(title=f"VX Harxu",
                                        description=f"[Click Here](https://www.behance.net/harxudesigns) for Harxu's Portfolio.",
                                        color = main_color)
            harxu_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            videro_embed = discord.Embed(title=f"VX Videro",
                                         description=f"[Click Here](https://www.twitter.com/viderodzns) for Videro's Portfolio.",
                                         color = main_color)
            videro_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            kai_embed = discord.Embed(title=f"VX Kai",
                                      description=f"[Click Here](https://www.instagram.com/_kaidzns_/) for Kai's Portfolio.",
                                      color = main_color)
            kai_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            metalooze_embed = discord.Embed(title=f"VX MetalOoze",
                                            description=f"[Click Here](https://behance.net/MetalOoze) for MetalOoze's Portfolio.",
                                            color = main_color)
            metalooze_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            seriously_embed = discord.Embed(title=f"VX Serious_ly",
                                            description=f"[Click Here](https://www.behance.net/notseriously) for Serious_ly's Portfolio.",
                                            color = main_color)
            seriously_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            happy_embed = discord.Embed(title=f"VX Happy",
                                        description=f"[Click Here](https://notyasir06.wixsite.com/website-1) for Happy's Portfolio.",
                                        color = main_color)
            happy_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            bbtd_embed = discord.Embed(title=f"VX BBTD",
                                       description=f"[Click Here](https://www.youtube.com/channel/UCfQYSKSEBQmzizWQWfHqvmA) for BBTD's Portfolio.",
                                       color = main_color)
            bbtd_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            ninja_embed = discord.Embed(title=f"VX ItzNinja518",
                                        description=f"[Click Here](https://www.instagram.com/itzninja518/) for Ninja's Portfolio.",
                                        color = main_color)
            ninja_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            rafay_embed = discord.Embed(title=f"VX Rafay Edits",
                                        description=f"[Click Here](https://www.youtube.com/watch?v=_CRIEaXLNCM) for Rafay's Portfolio.",
                                        color = main_color)
            rafay_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            vxnm_embed = discord.Embed(title=f"VX VXNM",
                                       description=f"[Click here](https://www.behance.net/divijsethi) for VXNM's Portfolio.",
                                       color = main_color)
            vxnm_embed.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')

            if vx_member.id == 688645815018848266:
                await ctx.send(embed=harxu_embed)
                return
            if vx_member.id == 331084188268756993:
                await ctx.send(embed=videro_embed)
                return
            if vx_member.id == 446274931509166080:
                await ctx.send(embed=kai_embed)
                return
            if vx_member.id == 331005037062914050:
                await ctx.send(embed=metalooze_embed)
                return
            if vx_member.id == 531855998336499724:
                await ctx.send(embed=happy_embed)
                return
            if vx_member.id == 449498858049765378:
                await ctx.send(embed=ninja_embed)
                return
            if vx_member.id == 396334277132025856:
                await ctx.send(embed=vxnm_embed)
                return
            else:
                await ctx.send(f"{vx_member.mention} is not in VX.")

        else:
            e = discord.Embed(
                description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**',
                colour=discord.Color.red())
            await ctx.send(embed=e)

    @commands.command(name="prices", help="Sends the official price list of VX.", aliases=['shop', 'services'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def services(self, ctx):
        if ctx.guild.id == 690494216572239922:
            e = discord.Embed(title="VX Price List", description=f"```"
                                                                 f"     Products      │ Basic │ Advanced\n\n"
                                                                 f"Twitch Emotes(X5)     $8       $8\n\n"
                                                                 f"Twitch Panels(x2)     $2       $4\n\n"
                                                                 f"Stream Package        $15     $30\n\n"
                                                                 f"Animated Intro        $3       $6\n\n"
                                                                 f"Animated Logo         $2       $4\n\n"
                                                                 f"Team Intro            $4       $8\n\n"
                                                                 f"Team Intro Video      $5      $10\n\n"
                                                                 f"Animated Outro        $2       $4\n\n"
                                                                 f"Montage Edit(1min)    $2       $4\n\n"
                                                                 f"Montage Edit(2min)    $4       $8\n\n"
                                                                 f"Montage Edit(3min)    $6      $12\n\n"
                                                                 f"Custom FN Jersey      $8      $16\n\n"
                                                                 f"Fortnite PNG Render   $1       $2\n\n"
                                                                 f"Fortnite PFP          $1       $2\n\n"
                                                                 f"Regular Logo          $2       $4\n\n"
                                                                 f"Concept Logo          $3       $6\n\n"
                                                                 f"2D Twitter/YT Banner  $2       $4\n\n"
                                                                 f"3D Twitter/YT Banner  $4       $8\n\n"
                                                                 f"Regular Thumbnail     $1       $2\n\n"
                                                                 f"Custom Thumbnail      $2       $4\n\n"
                                                                 f"Stream Screen         $1       $4\n\n"
                                                                 f"Stream Alert          $1       $2\n\n"
                                                                 f"Stream Transition     $1       $2\n\n"
                                                                 f"Stream Facecam        $1       $2\n\n"
                                                                 f"Animated Facecam      $2       $4\n\n"
                                                                 f"Stream Overlay        $1       $2\n\n"
                                                                 f"Animated Overlay      $2       $4\n\n"
                                                                 f"Tournament Poster     $2       $4\n\n"
                                                                 f"Introducing Poster    $1       $2\n\n"
                                                                 f"```\n"
                                                                 f"**For any queries kindly contact- VideroDesigns.#9999.**\n\n"
                                                                 f"**For Samples, type-**\n"
                                                                 f"```t-portfolios```", color = main_color)
            e.set_thumbnail(url='https://cdn.probot.io/agdJCAIfLR.png')
            e.set_footer(text=f"Prices requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.message.add_reaction(tick)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**',
                colour=discord.Color.red())
            await ctx.send(embed=e)

    """Close"""

    @commands.command(name="close", help="Closes the ticket.", aliases=['delete'])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def close(self, ctx):
        if ctx.guild.id == 690494216572239922:
            guilds = self.client.guilds
            embedmessage = discord.Embed(title="Do you want to delete this channel?",
                                         description=f"React with {tick} to delete this channel.\n"
                                                     f"React with {cross} to delete this message.", color=main_color)
            editembed5 = discord.Embed(title="Deleting this channel in 5 seconds.", color=main_color)
            editembed4 = discord.Embed(title="Deleting this channel in 4 seconds.", color=main_color)
            editembed3 = discord.Embed(title="Deleting this channel in 3 seconds.", color=main_color)
            editembed2 = discord.Embed(title="Deleting this channel in 2 seconds.", color=main_color)
            editembed1 = discord.Embed(title="Deleting this channel in 1 second.", color=main_color)

            message = await ctx.send(embed=embedmessage)
            await message.add_reaction(tick)
            await message.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [tick, cross]

            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=check, timeout=120)
                    if str(reaction.emoji) == tick:
                        editmessage = await ctx.send(embed=editembed5)
                        edit4 = editembed4
                        edit3 = editembed3
                        edit2 = editembed2
                        edit1 = editembed1
                        await asyncio.sleep(delay=1)
                        await editmessage.edit(embed=edit4)
                        await asyncio.sleep(delay=1)
                        await editmessage.edit(embed=edit3)
                        await asyncio.sleep(delay=1)
                        await editmessage.edit(embed=edit2)
                        await asyncio.sleep(delay=1)
                        await editmessage.edit(embed=edit1)
                        await asyncio.sleep(delay=1)
                        await message.channel.delete()
                        break
                    if str(reaction.emoji) == cross:
                        await message.delete()
                        break
                except asyncio.TimeoutError:
                    await message.delete()
                    break
        else:
            e = discord.Embed(
                description=f'**This command can only be used in the [VX GFX/VFX Community](https://www.discord.gg/keMaPa6) server!**',
                colour=discord.Color.red())
            await ctx.send(embed=e)

def setup(client):
    client.add_cog(vx(client))