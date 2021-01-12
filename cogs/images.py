import discord
from discord.ext import commands
from discord import Embed
import asyncio
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import aiohttp
from io import BytesIO
from bot import main_color, cross, tick
import random
from wand import image
from wand.drawing import Drawing

def pilimagereturn(image: bytes):
    try:
        io = BytesIO(image)
        io.seek(0)
        im = Image.open(io)
        return im
    except:
        print('Error in a Image command.')

class images(commands.Cog):
    """Image commands which are accessible to all members of the server!"""

    def __init__(self, client):
        self.client = client

    @commands.command(name="write", help="Writes your message on an image!")
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def write(self, ctx, *, message):
        img = Image.open("website.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('Font.otf', size=120)
        msg = message.replace('\\n', '\n')
        W, H = (1280, 720)
        w, h = draw.textsize(msg, font=font)
        draw.multiline_text(xy=((W - w) / 2, (H - h) / 2),
                            text=msg,
                            font=font, fill=(255, 255, 255),
                            align='center')
        with BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename="image.png"))

    @commands.command(name='sketch', help='Sends the sketched pfp of the member mentioned!')
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def sketch(self, ctx, member : discord.Member  = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as('png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.transform_colorspace("gray")
            img.sketch(0.5, 0.0, 98.0)
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename=f'{member.display_namee}_sketch.png'
                ), embed=discord.Embed(
                    title=f'I sketched {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://{member.display_name}_sketch.png').set_footer(text=f'Sketched because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='triggered')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def triggered(self, ctx, user : discord.Member = None):
        """Sends the `TRIGGERED` version of your avatar!"""
        user = ctx.author if not user else user
        asset = user.avatar_url_as(size=256, format="png")
        bytes = await asset.read()
        im = pilimagereturn(bytes)
        im = im.resize((370, 370), Image.ANTIALIAS)
        overlay = Image.open('triggered.png')
        ml = []
        for i in range(0, 10):
            blank = Image.new('RGBA', (256, 256))
            x = -1 * (random.randint(40, 100))
            y = -1 * (random.randint(40, 100))
            blank.paste(im, (x, y))
            rm = Image.new('RGBA', (256, 256), color=(255, 0, 0, 76))
            blank.paste(rm, mask=rm)
            blank.paste(overlay, mask=overlay, box=(0, 0))
            ml.append(blank)
        with BytesIO() as image_binary:
            ml[0].save(image_binary, format='gif', save_all=True, duration=1, append_images=ml, loop=0)
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename=f'triggered_{user.display_name}.gif'))

    @commands.command(name="invert", help="Sends a ghost pfp of the user mentioned!", aliases=["negative"])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def invert(self, ctx, user: discord.User = None):
        user = ctx.author if not user else user
        asset = user.avatar_url_as(size=1024, format="png")
        bytes = await asset.read()
        with Image.open(BytesIO(bytes)).convert("RGB") as my_image:
            inverted = ImageOps.invert(my_image)
            output_buffer = BytesIO()
            inverted.save(output_buffer,
                          "png")
            output_buffer.seek(0)
        await ctx.send(file=discord.File(fp=output_buffer, filename="invert.png"))

    @commands.command(name="gray", help="Sends the gray pfp of the user mentioned!", aliases=["grayscale", "b&w"])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def gray(self, ctx, user: discord.User = None):
        user = ctx.author if not user else user
        asset = user.avatar_url_as(size=1024, format="png")
        bytes = await asset.read()
        with Image.open(BytesIO(bytes)) as my_image:
            grayed = ImageOps.grayscale(my_image)
            output_buffer = BytesIO()
            grayed.save(output_buffer,
                        "png")
            output_buffer.seek(0)
        await ctx.send(file=discord.File(fp=output_buffer, filename="gray.png"))

    @commands.command(name="posterize", help="Posterizes the pfp of the user mentioned.")
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def posterize(self, ctx, bits: int, user: discord.User = None):
        if bits >= 8:
            await ctx.send("Please enter a number between 1-8.")
            return
        if bits <= 1:
            await ctx.send("Please enter a number between 1-8.")
            return
        user = ctx.author if not user else user
        asset = user.avatar_url_as(size=1024, format="png")
        bytes = await asset.read()
        with Image.open(BytesIO(bytes)).convert("RGB") as my_image:
            grayed = ImageOps.posterize(my_image, bits=bits)
            output_buffer = BytesIO()
            grayed.save(output_buffer,
                        "png")
            output_buffer.seek(0)
        await ctx.send(file=discord.File(fp=output_buffer, filename="posterize.png"))
    """
    @commands.command(name="blur", help="Sends the blurred pfp of the user mentioned")
    async def blur(self, ctx, radius: int, user: discord.User = None):
        user = ctx.author if not user else user
        asset = user.avatar_url_as(size=1024, format="png")
        bytes = await asset.read()
        with Image.open(BytesIO(bytes)).convert("RGB") as my_image:
            filter = ImageFilter.GaussianBlur(radius=radius)
            grayed = my_image.filter(filter)
            output_buffer = BytesIO()
            grayed.save(output_buffer,
                        "png")
            output_buffer.seek(0)
        await ctx.send(file=discord.File(fp=output_buffer, filename="blur.png"))
    
    @commands.command(name="blurfile", help="Sends the blurred image of the file's url given.")
    async def blurfile(self, ctx, radius: int, link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                bytes = await response.read()
        with Image.open(BytesIO(bytes)).convert("RGBA") as my_image:
            filter = ImageFilter.GaussianBlur(radius=radius)
            grayed = my_image.filter(filter)
            output_buffer = BytesIO()
            grayed.save(output_buffer,
                        "png")
            output_buffer.seek(0)
        await ctx.send(file=discord.File(fp=output_buffer, filename="blurfile.png"))
    """
    @commands.command(name='sketch', help='Sends the sketched pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def sketch(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.transform_colorspace("gray")
            img.sketch(0.5, 0.0, 98.0)
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='sketch.png'
                ), embed=discord.Embed(
                    title=f'I sketched {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://sketch.png').set_footer(
                    text=f'Sketched because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='dumb', help='Sends the __dumbified__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def dumb(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.implode(amount=0.5)
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='dumb.png'
                ), embed=discord.Embed(
                    title=f'I __dumbified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://dumb.png').set_footer(
                    text=f'dumbified because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='swirl', help='Sends the __swirled__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def swirl(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.swirl(degree=random.randint(90, 150))
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='swirl.png'
                ), embed=discord.Embed(
                    title=f'I __swirled__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://swirl.png').set_footer(
                    text=f'swirled because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='solarize', help='Sends the __solzrized__ pfp of the member mentioned! **[Must Try!]**')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def solarize(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='jpg', size=512)
        with image.Image(blob=await url.read()) as img:
            img.solarize(threshold=float(random.uniform(3 / 10, 8 / 10)) * img.quantum_range)
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='solarized.jpg'
                ), embed=discord.Embed(
                    title=f'I __solarized__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://solarized.jpg').set_footer(
                    text=f'solarized because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='waveify', help='Sends the __wave-ified__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def waveify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.wave(amplitude=img.height / random.randint(40, 60),
                     wave_length=img.width / random.randint(3, 5))
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='wave.png'
                ), embed=discord.Embed(
                    title=f'I __wave-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://wave.png').set_footer(
                    text=f'wave-ified because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='charcoal', help='Sends the __charcoal__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def charcoal(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.charcoal(radius=random.uniform(0.0, 1.5), sigma=random.uniform(0.0, 0.5))
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='charcoal.png'
                ), embed=discord.Embed(
                    title=f'I __charcoaled__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://charcoal.png').set_footer(
                    text=f'charcoaled because {ctx.author.name} told me to.'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='redify', help='Sends the __red-ified__ pfp of the member mentioned!', aliases=['red'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def redify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='red', alpha='rgb(5%, 0%, 0%)')
            img.tint(color='red', alpha='rgb(100%, 0%, 0%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='red.png'
                ), embed=discord.Embed(
                    title=f'I __red-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://red.png').set_footer(
                    text=f'red-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='blueify', help='Sends the __blue-ified__ pfp of the member mentioned!', aliases=['blue'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def blueify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='blue', alpha='rgb(0%, 0%, 5%)')
            img.tint(color='blue', alpha='rgb(0%, 0%, 100%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='blue.png'
                ), embed=discord.Embed(
                    title=f'I __blue-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://blue.png').set_footer(
                    text=f'blue-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='greenify', help='Sends the __green-ified__ pfp of the member mentioned!', aliases=['green'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def greenify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='green', alpha='rgb(0%, 5%, 0%)')
            img.tint(color='green', alpha='rgb(0%, 100%, 0%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='green.png'
                ), embed=discord.Embed(
                    title=f'I __green-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://green.png').set_footer(
                    text=f'green-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='cyanify', help='Sends the __cyan-ified__ pfp of the member mentioned!', aliases=['cyan', 'light-blue'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def cyanify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='cyan', alpha='rgb(0%, 5%, 5%)')
            img.tint(color='cyan', alpha='rgb(0%, 100%, 100%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='cyan.png'
                ), embed=discord.Embed(
                    title=f'I __cyan-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://cyan.png').set_footer(
                    text=f'cyan-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(aliases=['pink'] ,name='pinkify', help='Sends the __pink-ified__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def pinkify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='magenta', alpha='rgb(5%, 0%, 5%)')
            img.tint(color='magenta', alpha='rgb(100%, 0%, 100%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='pink.png'
                ), embed=discord.Embed(
                    title=f'I __pink-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://pink.png').set_footer(
                    text=f'pink-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='yellowify', help='Sends the __yellow-ified__ pfp of the member mentioned!', aliases=['yellow'])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def yellowify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.colorize(color='yellow', alpha='rgb(10%, 10%, 0%)')
            img.tint(color='yellow', alpha='rgb(100%, 100%, 0%)')
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='yellow.png'
                ), embed=discord.Embed(
                    title=f'I __yellow-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://yellow.png').set_footer(
                    text=f'yellow-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

    @commands.command(name='noise', help='Sends the __noisy__ pfp of the member mentioned!')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def noise(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        url = member.avatar_url_as(format='png', size=512)
        with image.Image(blob=await url.read()) as img:
            img.noise('laplacian', attenuate=4.0)
            with BytesIO() as img2:
                img.save(img2)
                img2.seek(0)
                await ctx.send(file=discord.File(
                    fp=img2,
                    filename='noise.png'
                ), embed=discord.Embed(
                    title=f'I __noise-ified__ {member.display_name}',
                    color=main_color
                ).set_image(url=f'attachment://noise.png').set_footer(
                    text=f'noise-ified because {ctx.author.name} told me to'))
                await ctx.message.add_reaction(tick)

def setup(client):
    client.add_cog(images(client))