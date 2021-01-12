import discord
from discord.ext import commands
import os
import tempfile
from bot import tick, cross, main_color
from _Utils import Message

def setup(client):
    client.add_cog(emoji(client))

class emoji(commands.Cog):
    """Emoji commands which are only accessible to the administrators and owners of the server!"""
    def __init__(self, client):
        self.client = client

    @commands.group(name='emoji')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def emoji(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.client.get_command('emojihelp'))

    @emoji.command(name='steal', help='Steals the emoji given and adds it to the server!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.has_permissions(manage_emojis=True)
    async def steal_emoji(self, ctx, emoji: discord.PartialEmoji = None):
        if not emoji:
            await Message.EmbedText(
                title='Please specify an emoji to steal.',
                color=main_color
            ).send(ctx)
            await ctx.message.add_reaction(cross)
        if emoji:
            url = emoji.url
            guild = ctx.guild
            fp = tempfile.NamedTemporaryFile(delete=True)
            if len(guild.emojis) < guild.emoji_limit:
                try:
                    await url.save(fp='emoji.png')
                    with open('emoji.png', 'rb') as image:
                        f = image.read()
                        b = bytearray(f)
                        await guild.create_custom_emoji(name=f'trixz{emoji.name}', image=b,
                                                        reason=f'Emoji added by {ctx.author.name} via TrixZ')
                    await Message.EmbedText(
                        title=f'Successfully added the emoji named {emoji.name}',
                        color=main_color
                    ).send(ctx)
                    await ctx.message.add_reaction(tick)
                    fp.close()
                    os.remove('emoji.png')
                finally:
                    if os.path.exists('emoji.png'):
                        os.remove('emoji.png')
                    fp.close()
            if len(guild.emojis) == guild.emoji_limit:
                await Message.EmbedText(
                    title='This server has reached its max emoji limit!',
                    color=discord.Color.red()
                ).send(ctx)
                await ctx.message.add_reaction(cross)

    @emoji.command(name='list', help='Shows all the emojis available in a server!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def list_emojis(self, ctx, guild: int = None):
        guild = ctx.guild if not guild else self.client.get_guild(guild)
        all_emojis = guild.emojis
        a_emojis = []
        emojis = []
        for emoji in all_emojis:
            if emoji.animated:
                a_emojis.append(emoji)
            else:
                emojis.append(emoji)
        e = discord.Embed(
            color=main_color
        ).set_author(
            name=guild.name,
            icon_url=guild.icon_url
        )
        if len(a_emojis) > 0:
            aEmojis = ' '.join(f'{emoji}' for emoji in a_emojis)
            e.add_field(
                name=f'Animated Emojis ({len(a_emojis)})',
                value=aEmojis if len(aEmojis) < 1024 else "Uh oh! Looks like there are too many emojis to be shown here!",
                inline=False)
        if len(emojis) > 0:
            regEmojis = ' '.join(emoji for emoji in emojis),
            e.add_field(
                name=f'Regular Emojis ({len(emojis)})',
                value=regEmojis if len(regEmojis) < 1024 else "Uh oh! Looks like there are too many emojis to be shown here!",
                inline=False
            )
        if len(a_emojis) <= 0:
            e.add_field(
                name=f'Animated Emojis',
                value='There are no animated emojis in this server, *yet*.',
                inline=False
            )
        if len(emojis) <= 0:
            e.add_field(
                name='Regular Emojis',
                value='There are no regular emojis in this server, *yet*.',
                inline=False
            )

        await ctx.message.add_reaction(tick)
        await ctx.send(embed=e)