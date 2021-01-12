import asyncio
import aiohttp
import discord
from discord.ext import commands
import json
import os
import tempfile
import shutil
import time
from os.path import splitext
from PIL import Image
from _Utils import Message, DL
from urllib.parse import urlparse

def get_ext(url):
    """Return the filename extension from url, or ''."""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext[1:]


def canDisplay(firstTime, threshold):
    currentTime = int(time.time())
    if currentTime > (int(firstTime) + int(threshold)):
        return True
    else:
        return False


async def download(url, ext: str = "jpg", sizeLimit: int = 8000000, ua: str = 'CorpNewt DeepThoughtBot'):
    """Download the passed URL and return the file path."""
    url = str(url).strip("<>")
    dirpath = tempfile.mkdtemp()
    tempFileName = url.rsplit('/', 1)[-1]
    tempFileName = tempFileName.split('?')[0]
    imagePath = dirpath + "/" + tempFileName
    rImage = None

    try:
        rImage = await DL.async_dl(url, headers={"user-agent": ua})
    except:
        pass
    if not rImage:
        remove(dirpath)
        return None

    with open(imagePath, 'wb') as f:
        f.write(rImage)
    if not os.path.exists(imagePath):
        remove(dirpath)
        return None

    try:
        img = Image.open(imagePath)
        ext = img.format
        img.close()
    except Exception:
        remove(dirpath)
        return None

    if ext and not imagePath.lower().endswith("." + ext.lower()):
        os.rename(imagePath, '{}.{}'.format(imagePath, ext))
        return '{}.{}'.format(imagePath, ext)
    else:
        return imagePath


async def upload(ctx, file_path, title=None):
    return await Message.Embed(title=title, file=file_path, color=ctx.author)


def addExt(path):
    img = Image.open(path)
    os.rename(path, '{}.{}'.format(path, img.format))
    path = '{}.{}'.format(path, img.format)
    return path


def remove(path):
    """Removed the passed file's containing directory."""
    if not path == None and os.path.exists(path):
        shutil.rmtree(os.path.dirname(path), ignore_errors=True)


async def get(ctx, url, title=None, ua: str = 'CorpNewt DeepThoughtBot', **kwargs):
    """Download passed image, and upload it to passed channel."""
    downl = kwargs.get("download", False)
    if not downl:
        await Message.Embed(title=title, url=url, image=url, color=ctx.author).send(ctx)
        return
    message = await Message.Embed(description="Downloading...", color=ctx.author).send(ctx)
    afile = await download(url)
    if not afile:
        return await Message.Embed(title="An error occurred!",
                                   description="Oh *shoot* - I couldn't get that image...").edit(ctx, message)
    message = await Message.Embed(description="Uploading...").edit(ctx, message)
    message = await Message.Embed(title=title, file=afile).edit(ctx, message)
    remove(afile)
    return message
