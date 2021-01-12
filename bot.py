import discord
from discord.ext import commands
import asyncio
import os
import datetime
import asyncpg
import ssl, json
from _Utils import Message

# config

config1 = open('config.json', 'r')
config = json.load(config1)

# custom prefixes

async def get_prefix(client, message):
    if message.guild:
        prefix1 = await client.pg_con.fetch('SELECT prefix from prefixes WHERE guild_id = $1', str(message.guild.id))
        return (prefix1[0]["prefix"], "t-", "T-", f"<@{client.user.id}> ", f"<@!{client.user.id}>") if prefix1 else ("t-", "T-", f"<@{client.user.id}> ", f"<@!{client.user.id}> ")
    else:
        return ("t-", "T-", f"<@{client.user.id}> ", f"<@!{client.user.id}> ")

# Client setup

intents = discord.Intents.all()
intents.presences = False
client = commands.Bot(command_prefix = get_prefix, case_insensitive = True, intents = intents, chunk_guilds_at_startup = True)
client.remove_command('help')
client.load_extension('jishaku')

# Database

async def create_pool():
    client.pg_con = await asyncpg.create_pool(database='trixz', user='postgres', password=config["DATABASE_PW"])

# defines

vxhelperlogs       = 736678078322966539
welcomelog         = 690498344765620274
tick               = "<a:tick:745550119436288061>"
cross              = '<a:cross:745553761598046280>'
online             = "<:online:753484504701730929>"
dnd                = "<:dnd:753484505477808188>"
idle               = '<:idle:753484505515556874>'
oflline            = '<:offline:753484505653706752>'
main_emoji         = "<a:trixz:754728379592343622>"
main_color         = 0x0ab5ff
invite_url         = 'https://discord.com/oauth2/authorize?client_id=716813265312940094&scope=bot&permissions=8'
support_server_url = 'https://discord.com/invite/u6SYTMh'
documentation_url  = 'https://trixz.gitbook.io/trixz/'
upvote_url         = 'https://botsfordiscord.com/bot/716813265312940094/vote'

# About embed

desc = "**TrixZ** is an **all-in-one** discord bot with the ability to power, entertain and look after your server 24/7 all by itself!"
features = "• **Logging system**. Logs every action in the server.\n" \
           "• **Level system**. Level logging also supported.\n" \
           "• **Welcome Logs** with custom message options.\n" \
           "• **Auto-Mod** features which look after your server 24/7.\n" \
           "• Quick and easy **Member-count** setup with other options.\n" \
           "• 20+ fun **Image** commands!\n" \
           "• 17+ advanced **Music** commands!\n" \
           "• Advanced and easy to understand **custom help command**.\n" \
           "• **17**+ command categories (**200+ commands**)!.\n" \
           f"• Active [**support server**]({support_server_url}).\n" \
           f"• Command list available [**here**](https://trixz.gitbook.io/trixz/commands)!\n" \
           "• **Many more!**\n\n" \
           f"{main_emoji} **Technical features**\n" \
           "• Fully secured **SSH database**, powered by [**AWS RDS**](https://aws.amazon.com/rds/).\n" \
           "• **Online 24/7**, hosted on [**AWS EC2**](https://aws.amazon.com/ec2/).\n" \
           f"• Full documentation available [**here**]({documentation_url})"

more_info = f"[Upvote TrixZ]({upvote_url}) `|` " \
            f"[Invite TrixZ]({invite_url}) `|` " \
            f"[Support Server]({support_server_url}) `|` " \
            f"[Documentation]({documentation_url})" \

main_embed = discord.Embed(
    color=main_color, description=desc,
    ).set_author(
    icon_url='https://cdn.discordapp.com/attachments/754223881723838485/754666392241963119/7.png',
    name=f'About TrixZ!',
    url=invite_url
).add_field(
    name=f'{main_emoji } Features',
    value=features,
    inline=False
).add_field(
    name=f'{main_emoji } Important links',
    value=more_info,
    inline=False
).set_footer(
    text='Developed with 💝 by Videro#9999'
)

# Join Embed

setup_info_text='\n⚠ __**IMPORTANT!**__ ⚠\n'\
                '• Put the role named `TrixZ` above all roles except **administrators** and **owners**. See the GIF for a little tutorial.\n\n'\
                '📂 **Logs setup!**\n'\
                "• Use `t-setlogs #channel-name` to set the log channel. The log channel is the channel where the bot sends all the changes of the server!\n\n"\
                "📊 **Level system setup!**\n"\
                "• Use `t-levels on` to turn on the level system for your server, if you do not want the bot to send a message when the user levels up, you can use `t-setlevels #channel-name` to set the level log channel, to send the level up messages there.\n\n"\
                "🔢 **Member-count setup!**\n"\
                "• Use `t-membercount setup` to start an interactive setup. You can also use `t-membercount` for all other options available.\n\n"\
                "🛡 **Auto-mod setup!**\n"\
                "• Use `t-automod enable` to enable auto-mod in your server. Type `t-automod features` to all features of auto-mod.\n\n"\
                "🎉 **Welcome log setup!**\n"\
                "• Use `t-welcome setup` to start an interactive setup. To see all welcome log options, type `t-welcome`.\n\n"\
                "📨 **Invite tracker setup!**\n"\
                "• Use `t-invites setup` to start an interactive setup to setup Invite Tracker!"\
                "\n\n [See this](https://trixz.gitbook.io/trixz/getting-started) if the above text is too much for you to handle."
join_embed = discord.Embed(
    title='How to setup TrixZ, the correct way.',
    color=main_color,
    description=f'You can [click here]({documentation_url}) for the full tutorial on how to setup **TrixZ** properly. However, there is also a quick short tutorial down below -' + "\n" +setup_info_text
).add_field(
    name='More info',
    value=f"• Do not forget to report any of the issues you are facing with TrixZ. You can report them [**here**]({support_server_url}).",
    inline=False
).add_field(
    name='Additional links',
    value=more_info,
    inline=False
)

# Load the cogs

loaded = 0
for filename in os.listdir('cogs'):
    if filename.endswith('.py') and not filename.startswith("_") and not filename.startswith("~"):
        client.load_extension(f'cogs.{filename[:-3]}')
        loaded +=1

# Ready Functions

async def status_loop():
    while True:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f't-help in {len(client.guilds)} servers!'), status=discord.Status.idle)
        await asyncio.sleep(60*10)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'Videro!'), status=discord.Status.idle)
        await asyncio.sleep(10)

@client.event
async def on_ready():
    client.loop.create_task(status_loop())
    print("───────────────")
    print(f'Successfully Loaded {loaded} modules ({len(list(client.walk_commands()))} commands).')
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("Latency -", round(client.latency * 1000), "ms")
    print("Developed with 💝 by Videro#9999")
    print("───────────────")

## on_command event logging ##

import random

@client.event
async def on_command(ctx : commands.Context):
    if not ctx.command_failed:
        r = random.randint(0,15)
        if r == 5:
            await asyncio.sleep(5)
            e =discord.Embed(color=main_color,
                             description=f'**Quick tip:** Please consider __upvoting TrixZ__ by [**clicking here**]({upvote_url}). Means a lot 💝')
            await ctx.send(embed=e, delete_after=15)
    if ctx.guild:
        sys_channel = ctx.guild.system_channel if ctx.guild.system_channel is not None else ctx.guild.text_channels[-1]
    if not ctx.guild:
        sys_channel = 'DM Channel'
    if ctx.author.id == client.owner_id:
        return
    channel = await client.fetch_channel(channel_id=754716195382362152)
    e = discord.Embed(
        color=main_color,
        timestamp=datetime.datetime.utcnow()
                      #.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url, url=(await sys_channel.create_invite()) if ctx.guild else 'DM Channel'
    ).add_field(
        name=f'{main_emoji} Command used',
        value=str(ctx.message.content),
        inline=False
    ).add_field(
        name=f'{main_emoji} Command used by',
        value=ctx.author.mention + " - " + ctx.author.name + ' - ' + str(ctx.author.id)
        , inline=False
    ).add_field(
        name=f'{main_emoji} Command used in',
        value=f'{ctx.channel.mention} - {ctx.channel.name} - {ctx.channel.id}' if ctx.guild else 'DM Channel',
        inline=False
    ).add_field(
        name=f'{main_emoji} Command successful?',
        value=f'{tick} Yes!' if not ctx.command_failed else f'{cross} Nope..',
        inline=False
    ).set_footer(
        text='Command used'
    )
    if ctx.guild:
        e.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        e.set_thumbnail(url=ctx.guild.icon_url)

    await channel.send(embed=e)

# Server Join and remove

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

@client.event
async def on_guild_join(guild):
    log_channel = client.get_channel(754716195382362152)
    videro = client.get_user(331084188268756993)
    try:
        await client.pg_con.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)", str(guild.id), "t-")
        await client.pg_con.execute('INSERT INTO all_guilds (guild_name, guild_id, levels_enabled, automod_enabled, welcome_log_enabled, invites_enabled) VALUES ($1, $2, $3, $4, $5, $6)', str(guild.name), str(guild.id), 'no', 'no', 'no', 'no')
        await videro.send(f'Added **{guild.name}** to the database.')
        await log_channel.send(f'Added **{guild.name}** to the database.')
    except Exception as e:
        print(e)
        await videro.send(f'```py\n{e}\n```')
        await log_channel.send(f'```py\n{e}\n```')
    # inv = str
    channel = guild.system_channel if guild.system_channel else guild.text_channels[0]
    try:
        inv = await channel.create_invite()
    except:
        inv = 'Could not generate an invite.'
    
    e3 = discord.Embed(title="New Server", color=main_color)
    e3.set_thumbnail(url=guild.icon_url)
    e3.description = f'Server Name: **{guild.name}** ({guild.id}).\nServer Owner: **{str(guild.owner)}** ({guild.owner.id})\nServer members: **{len(guild.members)}**\nInvite: {inv}'
    e3.timestamp = guild.created_at
    e3.set_footer(text="Server created at:")
    await videro.send(embed=e3)
    await log_channel.send(embed=e3)

    img = Image.open('Thanks.png')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font='Font.otf', size=85)
    draw.text(
        xy=(680, 705),
        text=guild.name,
        font=font,
        fill=(23, 161, 198),
        align='left'
    )
    with BytesIO() as img1:
        img.save(img1, 'PNG')
        img1.seek(0)
        await asyncio.sleep(3)
        
        e = discord.Embed(title="Thanks for inviting TrixZ!", description=f"Thanks a lot for inviting Trixz in your server! To get started, read the following info!", color=main_color)
        e.add_field(
                name='Setup',
                value=f"Type `t-setup` on your server to setup TrixZ properly.\nAdditionaly, you can [click this](https://trixz.gitbook.io/trixz/getting-started) if you are looking for an in-depth setup!",
                inline=False
            )
        e.add_field(
                name="Other",
                value=f"Type `t-support` if you run into an error.\nType `t-about` to see all the features you can use in your server!\nType `t-docs` to see the official documentation.",
                inline=False
            )
        e.add_field(
                name="More Info",
                value=more_info
            )
        e.set_image(url="attachment://Thanks_Videro_Loves_You.png")
        await channel.send(file=discord.File(fp=img1, filename='Thanks_Videro_Loves_You.png'), embed=e)
        return

@client.event
async def on_guild_remove(guild):
    channel = guild.system_channel if guild.system_channel else guild.text_channels[0]
    try:
        inv = await channel.create_invite()
    except:
        inv = 'Could not generate an invite.'
    e3 = discord.Embed(title="-1 Server", color=main_color)
    e3.set_thumbnail(url=guild.icon_url)
    e3.description = f'Server Name: **{guild.name}** ({guild.id}).\nServer Owner: **{str(guild.owner)}** ({guild.owner.id})\nServer members: **{len(guild.members)}**\nInvite: {inv}'
    e3.timestamp = guild.created_at
    e3.set_footer(text="Server created at:")
    log_channel = client.get_channel(754716195382362152)
    videro = client.get_user(331084188268756993)
    # msg = f'I was removed from **{guild.name}**.\nOwner - {guild.owner.mention} [{guild.owner.name}]'
    await videro.send(embed=e3)
    await log_channel.send(embed=e3)

# Triggers

# @client.event
# async def on_message(message):
#     if message.channel.id == 716033477342134332:
#         if message.attachments:
#             await message.add_reaction("⭐")
#         elif message.content.startswith("https://"):
#             await message.add_reaction("⭐")
#         else:
#             await message.delete()
#             await message.author.send(f"{message.author.mention}, {message.channel.mention} is an Image-Only channel.")
#     if message.channel.id == 750639704545689631:
#         if message.attachments:
#             await message.add_reaction("⭐")
#         elif message.content.startswith("https://"):
#             await message.add_reaction("⭐")
#         else:
#             await message.delete()
#             await message.author.send(f"{message.author.mention}, {message.channel.mention} is an Image-Only channel.")
#     if message.channel.id == 750770074763264000:
#         if message.author == client.user:
#             return
#         elif not message.content.lower().startswith("!vx"):
#             await message.delete()
#     await client.process_commands(message)

#Update Command

@client.command(hidden=True)
@commands.is_owner()
async def notify(ctx):
    await ctx.send("Send the message - (you have 3 minutes)")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    wait1 = await client.wait_for("message", check=check, timeout=180)
    message = wait1.content
    fail = 0
    success = 0
    for guild in client.guilds:
        channel = guild.system_channel if guild.system_channel is not None else guild.text_channels[-1]
        try:
            await channel.send(message)
            success += 1
        except:
            fail += 1
    await ctx.send(f"Sent the message in {success} servers. It could not be sent in {fail} servers.")
    return

@client.command()
@commands.cooldown(1, 5, commands.BucketType.member)
async def about(ctx):
    await ctx.message.add_reaction(tick)
    await ctx.send(embed=main_embed)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.member)
async def setupinfo(ctx):
    await ctx.message.add_reaction(tick)
    await ctx.send(embed=join_embed)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.member)
async def vx(ctx):
    await Message.EmbedText(
        title=f'Hey {ctx.author.name}, Now, its `t-` instead of `!vx` !',
        color=main_color,
    ).send(ctx)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.member)
@commands.is_owner()
async def usage(ctx):
    for cog1 in client.cogs:
        await ctx.send(f'**Commands in the category __{cog1}__**')
        cog = client.get_cog(cog1)
        for command1 in cog.walk_commands():
            command = client.get_command(command1.name)
            if command:
                await ctx.send(f'```py\n'
                               '{:<8}'.format(f'Usage') +
                               '{:^8}'.format(f':') +
                               '{:<8}'.format(f'{ctx.prefix}{command.qualified_name + " " + command.signature}')+ '\n'\
                               '{:<8}'.format(f'Info') +
                               '{:^8}'.format(f':') +
                               '{:<8}'.format(f'{command.help}') + '\n' \
                               '{:<8}'.format(f'Aliases') +
                               '{:^8}'.format(f':') +
                               '{:<8}'.format(f'{", ".join(f"{x}" for x in command.aliases) if command.aliases else "None"}') + '\n' \
                               f'```')
            else:
                await ctx.send(f'Could not list a command.')

# @client.command()
# @commands.cooldown(1, 5)
# @commands.is_owner()
# async def addall(ctx):
#     for guild in client.guilds:
#         guild_id = str(guild.id)
#         await client.pg_con.execute('INSERT INTO all_guilds (guild_name, guild_id, levels_enabled, automod_enabled, welcome_log_enabled) VALUES ($1, $2, $3, $4, $5)', guild.name, guild_id, 'no', 'no', 'no')
#         await ctx.send('Added {} to the database'.format(guild.name))

@client.command(name="invite", help="Sends the bot's invite link!", aliases=["invitelink"])
@commands.cooldown(1, 5, commands.BucketType.member)
async def invite(ctx):
    embed = discord.Embed(color=main_color,description=f"**[Click Here]({invite_url}) to invite me to your server! Thanks!**")
    await ctx.send(embed=embed)

@client.command(name='upvote', help="Sends the bot's upvote link!")
@commands.cooldown(1, 5, commands.BucketType.member)
async def upvote(ctx):
    dBotList = "https://discordbotlist.com/bots/trixz/upvote"
    dBoats = "https://discord.boats/bot/716813265312940094/vote"
    vBots = "https://voidbots.net/bot/716813265312940094/vote"
    sBotList = "https://space-bot-list.xyz/bots/716813265312940094/vote"
    botsForDiscord = "https://botsfordiscord.com/bot/716813265312940094/vote"
    embed = discord.Embed(color=main_color,title="Upvote TrixZ!",
                          description=f'You can **upvote TrixZ** on any of the following websites 💝 Thanks a lot!\n'
                                                        f'[**`Discord Boats`**]({dBoats})\n'
                                                        f'[**`Bots For Discord`**]({botsForDiscord})\n'
                                                        f'[**`Discord Bot List`**]({dBotList})\n'
                                                        f'[**`Void Bots`**]({vBots})\n'
                                                        f'[**`Space Bot List`**]({sBotList})\n'
                                                        )
    return await ctx.send(embed=embed)

@client.command(name='docs', help="Sends the official documentation link!")
@commands.cooldown(1, 5, commands.BucketType.member)
async def docs(ctx):
    await ctx.send(documentation_url)

@client.command(name='dashboard', aliases=['website', 'db'], help='Sends the official dashboard/website link!')
@commands.cooldown(1, 5, commands.BucketType.member)
async def dashboard(ctx):
    return await ctx.send("**Official Website/Dashboard** - https://www.trixz.xyz/")

@client.command(name="support", help="Sends the support server link!")
@commands.cooldown(1, 5, commands.BucketType.member)
async def support(ctx : commands.Context):
    await ctx.send(support_server_url)
    await ctx.send("You can join the support server to report an error/make suggestions.")

@client.command(name="setup", help="Starts an interactive setup! (Works best if you just invited TrixZ to a server)")
@commands.cooldown(1, 5, commands.BucketType.member)
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def setup(ctx: commands.Context):
    await Message.EmbedText(title="Do you want to enable Levels System?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
    try:
        wait1 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait1.content.lower() == "yes":
            await ctx.invoke(client.get_command('levels'), on_off='on')
            pass
        if wait1.content.lower() == "no":
            pass
        await Message.EmbedText(title="Do you want to enable Member Count?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
        wait2 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait2.content.lower() == "yes":
            await asyncio.sleep(1)
            await ctx.invoke(client.get_command('membercount setup'))
            pass
        if wait2.content.lower() == "no":
            pass
        await Message.EmbedText(title="Do you want to enable Invite Tracker?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
        wait3 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait3.content.lower() == "yes":
            await asyncio.sleep(1)
            await ctx.invoke(client.get_command('invites setup'))
            pass
        if wait3.content.lower() == "no":
            pass
        await Message.EmbedText(title="Do you want to enable Logging?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
        wait4 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait4.content.lower() == "yes":
            await asyncio.sleep(1)
            await ctx.invoke(client.get_command('logs enable'))
            pass
        if wait4.content.lower() == "no":
            pass
        await Message.EmbedText(title="Do you want to enable Welcome Image Logs?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
        wait5 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait5.content.lower() == "yes":
            await asyncio.sleep(1)
            await ctx.invoke(client.get_command('welcome setup'))
            pass
        if wait5.content.lower() == "no":
            pass
        await Message.EmbedText(title="Do you want to enable Auto Moderation?", color=main_color, description=f"{ctx.author.mention} Reply with either 'yes' or 'no'.").send(ctx)
        wait6 = await client.wait_for("message", timeout=200, check=lambda x: x.author == ctx.author and x.channel == ctx.channel and x.content.lower() in ("yes", "no"))
        if wait6.content.lower() == "yes":
            await asyncio.sleep(1)
            await ctx.invoke(client.get_command('automod enable'))
            pass
        if wait5.content.lower() == "no":
            pass
        e = discord.Embed(title="You are all good to go!", description=f"You can get started by using `t-help` or you can see the command list with all the available commands by [clicking here](https://trixz.gitbook.io/trixz/commands)!", color=main_color)
        await ctx.send(embed=e)
        return
    except asyncio.TimeoutError:
        embed2 = discord.Embed(title=f"You did not answer in time!", color=discord.Colour.red())
        await ctx.send(embed=embed2)
        return

@client.command(help="Shows the prefix of the server!")
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.member)
@commands.has_permissions(manage_guild=True)
async def prefix(ctx : commands.Context):
    guild_id = str(ctx.guild.id)
    fetch = await client.pg_con.fetch("SELECT prefix FROM prefixes WHERE guild_id = $1", guild_id)
    e = discord.Embed(title=f"The prefix here is set to `{fetch[0]['prefix']}`", color=main_color, description="To change the prefix in this server, type **`t-changeprefix prefix`**.")
    await ctx.send(embed=e)
    return

@client.command(aliases=["changep"], help="Changes the prefix in a specific server!")
@commands.guild_only()
@commands.cooldown(1, 60, commands.BucketType.member)
@commands.has_permissions(manage_guild=True)
async def changeprefix(ctx : commands.Context, prefix : str):
    if len(prefix) <= 5:
        await client.pg_con.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, str(ctx.guild.id))
        e = discord.Embed(title=f"Successfully set the prefix to `{prefix}`", color=main_color)
        await ctx.send(embed=e)
        return
    elif len(prefix) > 5:
        e = discord.Embed(title=f"Prefix must be less than 5 characters!", color=main_color)
        await ctx.send(embed=e)
        return

# blacklists

@client.check
async def check_if_channel(ctx : commands.Context):
    fetch = await client.pg_con.fetch("SELECT * FROM blacklist")
    blocked_channels = [int(x['channel_id']) for x in fetch]
    if ctx.channel.id in blocked_channels:
        await ctx.send(f":x: **{ctx.author.name}**, you cannot use bot commands in this channel!")
    return ctx.channel.id not in blocked_channels

# @client.check_once
# async def check_if_user(ctx : commands.Context):
#     fetch = await client.pg_con.fetch("SELECT * FROM blacklist")
#     blocked_users = [int(x['user_id']) for x in fetch]
#     if ctx.author.id in blocked_users:
#         await ctx.send(f":x: **{ctx.author.name}**, you are blocked from using <@{client.user.id}>.")
#     return ctx.author.id not in blocked_users

# Run the Bot

client.loop.run_until_complete(create_pool())
client.run(config['BOT_TOKEN'])