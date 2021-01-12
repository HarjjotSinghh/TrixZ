import time
from bot import main_color
from   discord.ext import commands
from _Utils import Message, ReadableTime


def setup(client):
	# Add the client
	client.add_cog(Uptime(client))

# This is the Uptime module. It keeps track of how long the client's been up

class Uptime(commands.Cog):

	# Init with the client reference, and a reference to the settings var
	def __init__(self, client):
		self.client = client
		self.startTime = int(time.time())

	@commands.command()
	async def uptime(self, ctx):
		"""Tells the uptime of the bot!"""
		currentTime = int(time.time())
		timeString  = ReadableTime.getReadableTimeBetween(self.startTime, currentTime)
		msg = 'I\'ve been up for *{}*.'.format(timeString)
		await Message.EmbedText(
			title=f'Uptime - {timeString}',
			color=main_color,
		).send(ctx)