import asyncio, discord, subprocess, os, re, time, math, uuid, ctypes, random, wavelink, json, tempfile, shutil
from   discord.ext import commands
from   cogs import Utils, DisplayName, PickList
from _Utils import Message, Nullify, DL
import re
from bot import main_color
import requests
import json
import textwrap

class Picker:
	def __init__(self, **kwargs):
		self.client = kwargs.get('client', None)
		self.list = kwargs.get("list", [])
		self.title = kwargs.get("title", None)
		self.timeout = kwargs.get("timeout", 60)
		self.ctx = kwargs.get("ctx", None)
		self.message = kwargs.get("message", None)
		self.self_message = None
		self.max = 10
		self.reactions = ["🛑"]

	async def _add_reactions(self, message, react_list):
		for r in react_list:
			await message.add_reaction(r)

	async def _remove_reactions(self, react_list=[]):
		try:
			await self.self_message.clear_reactions()
		except:
			pass
			'''for r in react_list:
                await message.remove_reaction(r,message.author)'''

	async def pick(self):
		if self.ctx == None or not len(self.list) or len(self.list) > self.max:
			return (-3, None)
		msg = ""
		if self.title:
			msg += self.title + "\n"
		msg += "```c\n"
		current = 0
		current_reactions = []
		for item in self.list:
			current += 1
			current_number = current if current < 10 else 0
			current_reactions.append("{}\N{COMBINING ENCLOSING KEYCAP}".format(current_number))
			msg += "{}. {}\n".format(current, item)
		msg += "```"
		current_reactions.append(self.reactions[0])
		if self.message:
			self.self_message = self.message
			await self.self_message.edit(content=msg, embed=None)
		else:
			self.self_message = await self.ctx.send(msg)
		await self._add_reactions(self.self_message, current_reactions)
		def check(reaction, user):
			return reaction.message.id == self.self_message.id and user == self.ctx.author and str(
				reaction.emoji) in current_reactions

		try:
			reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
		except:
			await self._remove_reactions(current_reactions)
			return (-2, self.self_message)

		await self._remove_reactions(current_reactions)
		ind = current_reactions.index(str(reaction.emoji))
		if ind == len(current_reactions) - 1:
			ind = -1
		return (ind, self.self_message)

class PagePicker(Picker):

    def __init__(self, **kwargs):
        Picker.__init__(self, **kwargs)
        self.max = kwargs.get("max",10)
        self.max = 1 if self.max < 1 else 10 if self.max > 10 else self.max
        self.reactions = ["⏪","◀","▶","⏩","🔢","🛑"]
        self.url = kwargs.get("url",None)

    def _get_page_contents(self, page_number):
        start = self.max*page_number
        return self.list[start:start+self.max]

    async def pick(self):
        if self.ctx == None or not len(self.list):
            return (-3, None)
        page  = 0
        pages = int(math.ceil(len(self.list)/self.max))
        embed = {
            "title":self.title,
            "url":self.url,
            "description":self.message,
            "pm_after":25,
            "fields":self._get_page_contents(page),
            "footer":"Page {} of {}".format(page+1,pages)
        }
        if self.message:
            self.self_message = self.message
            await Message.Embed(**embed, color=main_color).edit(self.ctx, self.message)
        else:
            self.self_message = await Message.Embed(**embed).send(self.ctx)
        if pages <= 1:
            return (0,self.self_message)
        await self._add_reactions(self.self_message, self.reactions)
        def check(reaction, user):
            return reaction.message.id == self.self_message.id and user == self.ctx.author and str(reaction.emoji) in self.reactions
        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
                await self.self_message.remove_reaction(emoji=reaction.emoji, member=self.ctx.author)
            except:
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            ind = self.reactions.index(str(reaction.emoji))
            if ind == 5:
                await self._remove_reactions(self.reactions)
                return (page, self.self_message)
            page = 0 if ind==0 else page-1 if ind==1 else page+1 if ind==2 else pages if ind==3 else page
            if ind == 4:
                page_instruction = await self.ctx.send("Type the number of that page to go to from {} to {}.".format(1,pages))
                def check_page(message):
                    try:
                        num = int(message.content)
                    except:
                        return False
                    return message.channel == self.self_message.channel and user == message.author
                try:
                    page_message = await self.client.wait_for('message', timeout=self.timeout, check=check_page)
                    page = int(page_message.content)-1
                except asyncio.TimeoutError as e:
                    print(e)
                    await page_message.clear_reactions()
                    pass
            page = 0 if page < 0 else pages-1 if page > pages-1 else page
            embed["fields"] = self._get_page_contents(page)
            embed["footer"] = "Page {} of {}".format(page+1,pages)
            await Message.Embed(**embed).edit(self.ctx, self.self_message)
        await self._remove_reactions(self.reactions)
        return (page, self.self_message)

def setup(client):
	client.add_cog(music(client))

class music(commands.Cog):
	"""Music commands which are accessible to all members of the server!"""

	__slots__ = ("client","settings","""queue1""","skips","vol","loop11","data")

	def __init__(self, client : commands.Bot):
		self.client     = client
		self.queue1     = {}
		self.skips      = {}
		self.vol        = {}
		self.loop11     = {}
		self.data       = {}
		self.url_regex  = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
		global Utils, DisplayName
		Utils = self.client.get_cog("Utils")
		DisplayName = self.client.get_cog("DisplayName")
		if not hasattr(self.client,'wavelink'): self.client.wavelink = wavelink.Client(bot=self.client)
		self.client.loop.create_task(self.start_nodes())

	def channelForName(self, name, server, typeCheck=None):
		name = str(name)
		for channel in server.channels:
			if typeCheck:
				if typeCheck.lower() == "text" and not type(channel) is discord.TextChannel:
					continue
				if typeCheck.lower() == "voice" and not type(channel) is discord.VoiceChannel:
					continue
				if typeCheck.lower() == "category" and not type(channel) is discord.CategoryChannel:
					continue
			if channel.name.lower() == name.lower():
				return channel
		chanID = re.sub(r'\W+', '', name)
		newChan = self.channelForID(chanID, server, typeCheck)
		if newChan:
			return newChan
		return None

	async def download(self, url):
		url = url.strip("<>")
		dirpath = tempfile.mkdtemp()
		tempFileName = url.rsplit('/', 1)[-1]
		tempFileName = tempFileName.split('?')[0]
		filePath = dirpath + "/" + tempFileName
		rImage = None
		try:
			rImage = await DL.async_dl(url)
		except:
			pass
		with open(filePath, 'wb') as f:
			f.write(rImage)
		return filePath

	async def start_nodes(self):
		node = self.client.wavelink.get_best_node()
		if not node:
			node = await self.client.wavelink.initiate_node(host='127.0.0.1',
				port=2020,
				rest_uri='http://127.0.0.1:2020',
				password='youshallnotpass',
				identifier='TrixZ',
				region='us_east')
		node.set_hook(self.on_event_hook)

	def skip_pop(self, ctx):
		self.skips.pop(str(ctx.guild.id),None)
		self.client.dispatch("skip_song",ctx)

	def dict_pop(self, ctx):
		guild = ctx if isinstance(ctx,discord.Guild) else ctx.guild if isinstance(ctx,discord.ext.commands.Context) else ctx.channel.guild if isinstance(ctx,discord.VoiceState) else None
		self.queue1.pop(str(guild.id),None)
		self.vol.pop(str(guild.id),None)
		self.skips.pop(str(guild.id),None)
		self.loop11.pop(str(guild.id),None)
		self.data.pop(str(guild.id),None)

	async def resolve_search(self, ctx, url, shuffle = False):
		
		message = await Message.EmbedText(
			title="🎶 Searching For: {}...".format(url.strip("<>")),
			color=main_color
			).send(ctx)
		data = await self.add_to_queue(ctx, url, message, shuffle)
		if data == False: return
		if data == None:
			return await Message.EmbedText(title="🎶 I couldn't find anything for that search!",description="Try using more specific search terms, or pass a url instead.",color=main_color,).edit(ctx,message)
		if isinstance(data,wavelink.Track):
			await Message.Embed(
				title="🎶 Enqueued: {}".format(data.title),
				fields=[
					{"name":"Duration","value":self.format_duration(data.duration,data),"inline":False},
					{"name":"Requsted by","value": ctx.author.mention, "inline": False}
				],
				color=main_color,
				thumbnail=data.thumb,
				url=data.uri,
				
			).edit(ctx,message)
		else:
			await Message.EmbedText(
				title="🎶 Added {}playlist: {} ({} song{})".format("shuffled " if shuffle else "",data.data["playlistInfo"]["name"],len(data.tracks),"" if len(data.tracks)==1 else "s"),
				url=data.search,
				fields=[{
					'name': 'Requested By', 'value': ctx.author.mention, 'inline': False
				}],
				color=main_color
			).edit(ctx,message)

	async def add_to_queue(self, ctx, url, message, shuffle = False):
		
		queue = self.queue1.get(str(ctx.guild.id),[])
		url = url.strip('<>')
		def get_urls(message):
			message = message.content if isinstance(message,discord.Message) else message.content if isinstance(message,discord.ext.commands.Context) else str(message)
			return [x.group(0) for x in re.finditer(re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"),message)]

		urls = get_urls(url)
		url = urls[0] if len(urls) else "ytsearch:"+url.replace('/', '')
		tracks = await self.client.wavelink.get_tracks(url)
		if tracks == None: return None
		if (url.startswith("ytsearch:") or isinstance(tracks,list)) and len(tracks):
			if ctx.guild is not None:
				list_show = "Please select the number of the track you'd like to add:"
				index, message = await Picker(
					title=list_show,
					list=[x.info['title'] for x in tracks[:5]],
					ctx=ctx,
					message=message,
					timeout = 180,
					client = self.client
				).pick()
				if index < 0:
					if index == -3:
						await message.edit(content="Something went wrong :(",)
					elif index == -2:
						await message.edit(content="Times up! You Can Search For Music Another Time!",)
					else:
						await message.edit(content="Aborting! You Can Search For Music Another Time!",)
					return False
				tracks = tracks[index]
			else:
				tracks = tracks[0]
		player = self.client.wavelink.get_player(ctx.guild.id)
		if isinstance(tracks,wavelink.Track):
			tracks.info["added_by"] = ctx.author
			tracks.info["ctx"] = ctx
			tracks.info["search"] = url
			try:
				seek_str = next((x[2:] for x in url.split("?")[1].split("&") if x.lower().startswith("t=")),"0").lower()
				values = [x for x in re.split("(\\d+)",seek_str) if x]
				total_time = 0
				last_type = "s"
				for x in values[::-1]:
					if not x.isdigit():
						last_type = x
						continue
					if last_type == "h":
						total_time += int(x) * 3600
					elif last_type == "m":
						total_time += int(x) * 60
					elif last_type == "s":
						total_time += int(x)
				seek_pos = total_time
			except Exception:
				seek_pos = 0
			tracks.info["seek"] = seek_pos
			queue.append(tracks)
			self.queue1[str(ctx.guild.id)] = queue
			if not player.is_playing and not player.is_paused:
				self.client.dispatch("next_song",ctx)
			return tracks
		tracks.search = url
		try: starting_index = next((int(x[6:])-1 for x in url.split("?")[1].split("&") if x.lower().startswith("index=")),0)
		except: starting_index = 0
		starting_index = 0 if starting_index >= len(tracks.tracks) or starting_index < 0 else starting_index
		tracks.tracks = tracks.tracks[starting_index:]
		if shuffle: random.shuffle(tracks.tracks)
		for index,track in enumerate(tracks.tracks):
			track.info["added_by"] = ctx.author
			track.info["ctx"] = ctx
			queue.append(track)
			self.queue1[str(ctx.guild.id)] = queue
			if index == 0 and not player.is_playing and not player.is_paused:
				self.client.dispatch("next_song",ctx)
		return tracks

	def format_duration(self, dur, data = False):
		if data and data.is_stream:
			return "[Live Stream]"
		dur = dur // 1000
		hours = dur // 3600
		minutes = (dur % 3600) // 60
		seconds = dur % 60
		return "{:02d}h:{:02d}m:{:02d}s".format(hours, minutes, seconds)

	def format_elapsed(self, player, track):
		progress = player.last_position
		total    = track.duration
		return "{} -- {}".format(self.format_duration(progress),self.format_duration(total,track))

	def progress_bar(self,player,track,bar_width=27,show_percent=True,include_time=False):
		progress = player.last_position
		total    = track.duration if not track.is_stream else 0
		bar = ""
		bar_width = 10 if bar_width-2 < 10 else bar_width-2
		if total == 0:
			bar = "[{}]".format("/"*bar_width)
		else:
			p = int(round((progress/total*bar_width)))
			bar = "[{}{}]".format("■"*p,"□"*(bar_width-p))
		if show_percent:
			bar += " --%" if total == 0 else " {}%".format(int(round(progress/total*100)))
		if include_time:
			time_prefix = "{} - {}\n".format(self.format_duration(progress),self.format_duration(total,track))
			bar = time_prefix + bar
		return bar

	def progress_moon(self,player,track,moon_count=10,show_percent=True,include_time=False):
		progress = player.last_position
		total    = track.duration if not track.is_stream else 0
		if total == 0:
			moon_list = ["🌕","🌑"]*math.ceil(moon_count/2)
			moon_list = moon_list[:moon_count]
			bar = "".join(moon_list)
		else:
			moon_max = 100/moon_count
			percent  = progress/total*100
			full_moons = int(percent/moon_max)
			leftover   = percent%moon_max
			remaining  = int(leftover/(moon_max/4))
			bar = "🌕"*full_moons
			bar += ["🌑","🌘","🌗","🌖","🌕"][remaining]
			bar += "🌑"*(moon_count-full_moons-1)
		if show_percent:
			bar += " --%" if total == 0 else " {}%".format(int(round(progress/total*100)))
		if include_time:
			time_prefix = "{} - {}\n".format(self.format_duration(progress),self.format_duration(total,track))
			bar = time_prefix + bar
		return bar

	def print_eq(self, eq, max_len = 5):
		bar      = "│"
		topleft  = "┌"
		topright = "┐"
		clientleft  = "└"
		clientright = "┘"
		cap      = "─"
		emp      = " "
		inner    = " "
		sep      = "─"
		sup      = "┴"
		sdn      = "┬"
		lpad     = ""
		eq_list  = []
		nums     = ""
		vals     = ""
		for band,value in eq:
			value *= 4
			ourbar = math.ceil(abs(value)*max_len)
			vals += str(ourbar if value > 0 else -1*ourbar).rjust(2)+" "
			nums += str(band+1).rjust(2)+" "
			if value == 0:
				our_cent = our_left = our_right = emp*max_len + sep + emp*max_len
			elif value > 0:
				our_left  = emp*max_len + sup + bar*(ourbar-1)   + topleft  + emp*(max_len-ourbar)
				our_cent  = emp*max_len + sep + inner*(ourbar-1) + cap      + emp*(max_len-ourbar)
				our_right = emp*max_len + sup + bar*(ourbar-1)   + topright + emp*(max_len-ourbar)
			else:
				our_left  = emp*(max_len-ourbar) + clientleft  + bar*(ourbar-1) + sdn + emp*max_len
				our_cent  = emp*(max_len-ourbar) + cap    + inner*(ourbar-1) + sep + emp*max_len
				our_right = emp*(max_len-ourbar) + clientright + bar*(ourbar-1) + sdn + emp*max_len
			our_left  = [x for x in our_left][::-1]
			our_cent  = [x for x in our_cent][::-1]
			our_right = [x for x in our_right][::-1]
			eq_list.extend([our_left,our_cent,our_right])
		graph = "```\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n```".format(
			"Bands".center(len(nums),sep),
			nums,
			sep*(len(nums)),
			"\n".join(["{}{}{}".format(lpad,x,lpad) for x in map("".join, zip(*eq_list))]),
			"Values".center(len(vals),sep),
			vals,
			sep*(len(vals))
		)
		return graph

	@commands.Cog.listener()
	async def on_loaded_extension(self, ext):
		if not self._is_submodule(ext.__name__, self.__module__):
			return

	def _is_submodule(self, parent, child):
		return parent == child or child.startswith(parent + ".")

	@commands.Cog.listener()
	async def on_unloaded_extension(self, ext):
		if not self._is_submodule(ext.__name__, self.__module__):
			return
		for x in self.client.guilds:
			player = self.client.wavelink.players.get(x.id,None)
			if player: await player.destroy()

	async def on_event_hook(self, event):
		if isinstance(event,(wavelink.TrackEnd, wavelink.TrackException, wavelink.TrackStuck)):
			try: ctx = self.data[str(event.player.guild_id)].info["ctx"]
			except: return
			
			if isinstance(event,(wavelink.TrackException,wavelink.TrackStuck)):
				await Message.EmbedText(title="🎶 Something went wrong playing that song ☹",color=discord.Color.red()).send(ctx)
				return await event.player.stop()
			self.client.dispatch("next_song",ctx)

	@commands.Cog.listener()
	async def on_skip_song(self,ctx):
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player != None and player.is_connected:
			await player.stop()

	@commands.Cog.listener()
	async def on_play_next(self,player,track):
		await player.play(track)
		seek = track.info.get("seek",0)*1000
		if seek and not seek > track.duration: await player.seek(track.info["seek"]*1000)
	
	@commands.Cog.listener()
	async def on_next_song(self,ctx,error=None):
		task = "playing"
		if error:
			print(error)
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None: return
		if not player.is_connected:
			return await player.destroy()
		if player.is_playing or player.is_paused: return await player.stop()
		queue = self.queue1.get(str(ctx.guild.id),[])
		if self.loop11.get(str(ctx.guild.id),False) and self.data.get(str(ctx.guild.id),None):
			queue.append(self.data.get(str(ctx.guild.id),None))
		if not len(queue):
			await Message.EmbedText(title="🎶 End of playlist!",color=main_color,).send(ctx)
			await asyncio.sleep(3)
			await player.disconnect()
			return
		data = queue.pop(0)
		self.data[str(ctx.guild.id)] = data
		volume = 100
		eq = wavelink.eqs.Equalizer.flat()
		if not player.volume == volume/2: await player.set_volume(volume/2)
		if not player.eq.raw == eq.raw: await player.set_eq(eq)
		player._equalizer = eq
		async with ctx.typing():
			self.client.dispatch("play_next",player,data)
		await Message.Embed(
			title="🎶 Now {}".format(task.capitalize(),),
			fields=[
				{"name":"Duration","value":self.format_duration(data.duration,data),"inline":True},
				{'name': 'Requested By', 'value': data.info["added_by"].mention if data.info["added_by"] else '', 'inline': True}
			],
			description=f"[**{data.title}**]({data.uri})",
			color=main_color,
			image=data.thumb,
			delete_after=data.duration // 1000,
		).send(ctx)

	@commands.command()
	async def saveq(self, ctx, *, options = ""):
		"""Saves the current playlist to a json file that can be loaded later with the `t-loadq` command."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		timestamp = False
		time = 0
		for x in options.split():
			if x.lower() == "ts": timestamp = True
		current = self.data.get(str(ctx.guild.id),None)
		queue = [x for x in self.queue1.get(str(ctx.guild.id),[])]
		if current and (player.is_playing or player.is_paused):
			if timestamp and current.info.get("uri"):
				current.info["seek"] = int(player.last_position/1000)
			queue.insert(0,current)
		if not len(queue):
			return await Message.EmbedText(title="🎶 No playlist to save!",color=main_color,).send(ctx)
		message = await Message.EmbedText(title="🎶 Gathering info...",color=main_color).send(ctx)
		songs = []
		for x in queue:
			if x.uri == None: continue
			x.info.pop("added_by",None)
			x.info.pop("ctx",None)
			x.info["id"] = x.id
			songs.append(x.info)
		await Message.EmbedText(title="🎶 Saving and uploading...",color=main_color).edit(ctx,message)
		temp = tempfile.mkdtemp()
		temp_json = os.path.join(temp,"playlist.json")
		try:
			json.dump(songs,open(temp_json,"w"),indent=2)
			await ctx.send(file=discord.File(temp_json))
		except Exception as e:
			return await Message.EmbedText(title="🎶 An error occurred creating the playlist!",description=str(e),color=main_color).edit(ctx,message)
		finally:
			shutil.rmtree(temp,ignore_errors=True)
		return await Message.EmbedText(title="🎶 Uploaded playlist!",color=main_color).edit(ctx,message)

	async def _load_playlist_from_url(self, url, ctx, shuffle = False):
		
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			await ctx.invoke(self.client.get_command('join', channel=ctx.author.voice.channel))
		if url == None and len(ctx.message.attachments) == 0:
			return await ctx.send("Usage: `{}loadpl [url or attachment]`".format(ctx.prefix))
		if url == None:
			url = ctx.message.attachments[0].url
		message = await Message.EmbedText(title="🎶 Downloading...",color=main_color).send(ctx)
		path = await self.download(url)
		if not path:
			return await Message.EmbedText(title="🎶 Couldn't download playlist!",color=main_color).edit(ctx,message)
		try:
			playlist = json.load(open(path))
		except Exception as e:
			return await Message.EmbedText(title="🎶 Couldn't serialize playlist!",description=str(e),color=main_color,).edit(ctx,message)
		finally:
			shutil.rmtree(os.path.dirname(path),ignore_errors=True)
		if not len(playlist): return await Message.EmbedText(title="🎶 Playlist is empty!",color=main_color).edit(ctx,message)
		if not isinstance(playlist,list): return await Message.EmbedText(title="🎶 Playlist json is incorrectly formatted!",color=main_color).edit(ctx,message)
		if shuffle:
			random.shuffle(playlist)
		queue = self.queue1.get(str(ctx.guild.id),[])
		for x in playlist:
			if not "id" in x and isinstance(x["id"],str): continue
			x["added_by"] = ctx.author
			x["ctx"] = ctx
			queue.append(wavelink.Track(x["id"],x))
		self.queue1[str(ctx.guild.id)] = queue
		await Message.EmbedText(title="🎶 Added {} {}song{} from playlist!".format(len(playlist),"shuffled " if shuffle else "", "" if len(playlist) == 1 else "s"),color=main_color,).edit(ctx,message)
		if not player.is_playing and not player.is_paused:
			self.client.dispatch("next_song",ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def loadq(self, ctx, *, url = None):
		"""Loads the passed queue json data.  Accepts a url - or picks the first attachment.
		Only files dumped via the saveq command are supported."""
		await self._load_playlist_from_url(url, ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def shuffle(self, ctx, *, url = None):
		"""Loads and shuffles the passed queue json data.  Accepts a url - or picks the first attachment.
		Note that the structure of this file is very specific and alterations may not work.
		
		Only files dumped via the saveq command are supported."""
		await self._load_playlist_from_url(url, ctx, shuffle=True)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def summon(self, ctx, *, channel = None):
		"""Joins the summoner's voice channel."""
		await ctx.invoke(self.join,channel=channel)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def join(self, ctx, *, channel = None):
		"""Joins a voice channel."""

		if channel == None:
			if not ctx.author.voice:
				return await Message.EmbedText(title="🎶 You need to pass a voice channel for me to join!",color=main_color,).send(ctx)
			channel = ctx.author.voice.channel
		else:
			channel = self.channelForName(channel, ctx.guild, "voice")
		if not channel:
			return await Message.EmbedText(title="🎶 I couldn't find that voice channel!",color=main_color,).send(ctx)
		player = self.client.wavelink.get_player(ctx.guild.id)
		if player.is_connected:
			if not (player.is_paused or player.is_playing):
				await player.connect(channel.id)
				return await Message.EmbedText(title="🎶 Ready to play music in {}!".format(channel),color=main_color,).send(ctx)
			else:
				return await Message.EmbedText(title="🎶 I'm already playing music in {}!".format(ctx.guild.get_channel(int(player.channel_id))),color=main_color,).send(ctx)
		await player.connect(channel.id)
		await Message.EmbedText(title="🎶 Ready to play music in {}!".format(channel),color=main_color,).send(ctx)

	@commands.command(aliases=['p'])
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def play(self, ctx, *, url = None):
		"""Plays from a url/search term or resumes a currently paused song."""
		if ctx.author.voice:
			player = self.client.wavelink.get_player(ctx.guild.id)
			if not player.is_connected:
				return await Message.EmbedText(title="🎶 I am not connected to a voice channel!",color=main_color,).send(ctx)
			if player.is_paused and url == None:
				await player.set_pause(False)
				data = self.data.get(str(ctx.guild.id))
				return await Message.EmbedText(title="🎶 Resumed: {}".format(data.title),color=main_color,).send(ctx)
			if url == None:
				return await Message.EmbedText(title="🎶 You need to pass a url or search term!",color=main_color,).send(ctx)
			await self.resolve_search(ctx, url)

		if not ctx.author.voice:
			return await Message.EmbedText(title="🎶 You need to be in a Voice Channel!", color=main_color).send(ctx)


	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def pause(self, ctx):
		"""Pauses the currently playing song."""

		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if player.is_paused:
			return await ctx.invoke(self.play)
		if not player.is_playing:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		await player.set_pause(True)
		data = self.data.get(str(ctx.guild.id))
		await Message.EmbedText(title="🎶 Paused: {}".format(data.title),color=main_color,).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def paused(self, ctx, *, moons = None):
		"""Lists whether or not the player is paused. Alias of the playing command."""
		
		await ctx.invoke(self.playing,moons=moons)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def resume(self, ctx):
		"""Resumes the song if paused."""

		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 I am not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_paused:
			return await Message.EmbedText(title="🎶 Not currently paused!",color=main_color,).send(ctx)
		await player.set_pause(False)
		data = self.data.get(str(ctx.guild.id))
		await Message.EmbedText(title="🎶 Resumed: {}".format(data.title),color=main_color,).send(ctx)

	@commands.command()
	async def unplay(self, ctx, *, song_number = None):
		"""Removes the passed song number from the queue.  You must be the requestor, or an admin to remove it.  Does not include the currently playing song."""
		
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 I am not connected to a voice channel!",color=main_color,).send(ctx)
		queue = self.queue1.get(str(ctx.guild.id),[])
		if not len(queue):
			return await Message.EmbedText(title="🎶 No songs in queue!", description="If you want to bypass a currently playing song, use `{}skip` instead.".format(ctx.prefix),color=main_color,).send(ctx)
		try:
			song_number = int(song_number)-1
		except:
			return await Message.EmbedText(title="🎶 Not a valid song number!",color=main_color,).send(ctx)
		if song_number < 0 or song_number > len(queue):
			return await Message.EmbedText(title="🎶 Out of bounds!  Song number must be between 2 and {}.".format(len(queue)),color=main_color,).send(ctx)
		song = queue[song_number]
		if song.info.get("added_by",None) == ctx.author or ctx.author.guild_permissions.administrator:
			queue.pop(song_number)
			return await Message.EmbedText(title="🎶 Removed {} at position {}!".format(song.title,song_number+1),color=main_color,).send(ctx)
		await Message.EmbedText(title="🎶 You can only remove songs you requested!", description="Only {} or an admin can remove that song!".format(song["added_by"].mention),color=main_color,).send(ctx)

	@commands.command(aliases=['unq'])
	async def unqueue(self, ctx):
		"""Removes all songs you've added from the queue (does not include the currently playing song).  Admins remove all songs from the queue."""

		
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 I am not connected to a voice channel!",color=main_color,).send(ctx)
		queue = self.queue1.get(str(ctx.guild.id),[])
		if not len(queue):
			return await Message.EmbedText(title="🎶 No songs in queue!", description="If you want to bypass a currently playing song, use `{}skip` instead.".format(ctx.prefix),color=main_color,).send(ctx)
		removed = 0
		new_queue = []
		for song in queue:
			if song.info.get("added_by",None) == ctx.author or ctx.author.guild_permissions.administrator:
				removed += 1
			else:
				new_queue.append(song)
		self.queue1[str(ctx.guild.id)] = new_queue
		if removed > 0:
			return await Message.EmbedText(title="🎶 Removed {} song{} from queue!".format(removed,"" if removed == 1 else "s"),color=main_color,).send(ctx)
		await Message.EmbedText(title="🎶 You can only remove songs you requested!", description="Only an admin can remove all queued songs!",color=main_color,).send(ctx)

	@commands.command()
	async def shuffleq(self, ctx, *, url = None):
		"""Shuffles the current queue. If you pass a playlist url or search term, it first shuffles that, then adds it to the end of the queue."""

		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			if url == None:
				return await Message.EmbedText(title="🎶 I am not connected to a voice channel!",color=main_color,).send(ctx)
			if not ctx.author.voice:
				return await Message.EmbedText(title="🎶 You are not connected to a voice channel!",color=main_color,).send(ctx)
			await player.connect(ctx.author.voice.channel.id)
		if url == None:
			queue = self.queue1.get(str(ctx.guild.id),[])
			if not len(queue):
				return await Message.EmbedText(title="🎶 No songs in queue!",color=main_color,).send(ctx)
			random.shuffle(queue)
			self.queue1[str(ctx.guild.id)] = queue
			return await Message.EmbedText(title="🎶 Shuffled {} song{}!".format(len(queue),"" if len(queue) == 1 else "s"),color=main_color,).send(ctx)
		await self.resolve_search(ctx, url, shuffle=True)

	@commands.command()
	async def playing(self, ctx, *, moons = None):
		"""Lists the currently playing song if any."""

		
		player = self.client.wavelink.players.get(ctx.guild.id,None) if ctx.guild.id in self.client.wavelink.players else None
		if player == None or not player.is_connected or not (player.is_playing or player.is_paused):
			return await Message.EmbedText(
				title="🎶 Currently Playing",
				color=main_color,
				description="Not playing anything.",
				
			).send(ctx)
		data = self.data.get(str(ctx.guild.id))
		play_text = "Playing" if (player.is_playing and not player.is_paused) else "Paused"
		cv = int(player.volume*2)
		await Message.Embed(
			title="🎶 Currently {}: {}".format(play_text,data.title),
			color=main_color,
			fields=[
				{"name":"Elapsed","value":self.format_elapsed(player,data),"inline":False},
				{"name":"Progress","value":self.progress_moon(player,data) if moons and moons.lower() in ["moon","moons","moonme","moon me"] else self.progress_bar(player,data),"inline":False},
				{"name":"Requested by","value":data.info["added_by"].mention if data.info["added_by"] else '',"inline":False},

			],
			url=data.uri,
			thumbnail=data.thumb,
			
		).send(ctx)

	@commands.command()
	async def playingin(self, ctx):
		"""Shows the number of servers the client is currently playing music in."""
		server_list = []
		for x in self.client.wavelink.players:
			server = self.client.get_guild(int(x))
			if not server: continue
			p = self.client.wavelink.get_player(x)
			if p.is_playing and not p.is_paused:
				server_list.append({"name":server.name,"value":p.current.info.get("title","Unknown title")})
		msg = "🎶 Playing music in {:,} of {:,} server{}.".format(len(server_list), len(self.client.guilds), "" if len(self.client.guilds) == 1 else "s")
		if len(server_list): await PagePicker(title=msg,list=server_list,ctx=ctx).pick()
		else: await Message.EmbedText(title=msg,color=main_color,).send(ctx)

	@commands.command(aliases=['q'])
	async def queue(self, ctx):
		"""Lists the queued songs in the playlist."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected or not (player.is_playing or player.is_paused):
			return await Message.EmbedText(
				title="🎶 Current Queue!",
				color=main_color,
				description="Not playing anything.",
			).send(ctx)
		data = self.data.get(str(ctx.guild.id))
		play_text = "Playing" if player.is_playing else "Paused"
		queue = self.queue1.get(str(ctx.guild.id),[])
		fields = [{"name":"{}".format(data.title),"value":"Currently {} - at {} - Requested by {} - [Link]({})".format(
			play_text,
			self.format_elapsed(player,data),
			data.info["added_by"].mention if data.info["added_by"] else '',
			data.uri),"inline":False},
		]
		if len(queue):
			total_time = 0
			total_streams = 0
			time_string = stream_string = ""
			for x in queue:
				t = x.duration
				if t:
					total_time+=t
				else:
					total_streams+=1
			if total_time:
				time_string += "{} total -- ".format(self.format_duration(total_time))
			if total_streams:
				time_string += "{:,} Stream{} -- ".format(total_streams, "" if total_streams == 1 else "s") 
			q_text = "-- {:,} Song{} in Queue -- {}".format(len(queue), "" if len(queue) == 1 else "s", time_string)
			fields.append({"name":"🎶 Up Next","value":q_text,"inline":False})
		for x,y in enumerate(queue):
			x += 1
			fields.append({
				"name":"{}. {}".format(x,y.title),
				"value":"{} - Requested by {} - [Link]({})".format(self.format_duration(y.duration,y),y.info["added_by"].mention if data.info["added_by"] else '',y.uri),
				"inline":False})
		if self.loop11.get(str(ctx.guild.id),False):
			pl_string = " - Repeat Enabled"
		else:
			pl_string = ""
		await PagePicker(title="🎶 Current Queue!{}".format(pl_string), color=main_color , list=fields, ctx=ctx, timeout=200, client=self.client).pick()

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def unskip(self, ctx):
		"""Removes your vote to skip the current song."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		
		skips = self.skips.get(str(ctx.guild.id),[])
		if not ctx.author.id in skips: return await Message.EmbedText(title="🎶 You haven't voted to skip this song!",color=main_color,).send(ctx)
		skips.remove(ctx.author.id)
		self.skips[str(ctx.guild.id)] = skips
		channel = ctx.guild.get_channel(int(player.channel_id))
		if not channel:
			return await Message.EmbedText(title="🎶 Something went wrong!",description="That voice channel doesn't seem to exist anymore...",color=main_color,).send(ctx)
		skippers = [x for x in channel.members if not x.bot]
		needed_skips = math.ceil(len(skippers)/2)
		await Message.EmbedText(title="🎶 You have removed your vote to skip - {}/{} votes entered - {} more needed to skip!".format(len(skips),needed_skips,needed_skips-len(skips)),color=main_color,).send(ctx)

	@commands.command(aliases=['next'])
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def skip(self, ctx):
		"""Adds your vote to skip the current song.  50% or more of the non-client users need to vote to skip a song.  Original requestors and admins can skip without voting."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		data = self.data.get(str(ctx.guild.id))
		if ctx.author.guild_permissions.administrator:
			self.skip_pop(ctx)
			return await Message.EmbedText(title="🎶 Admin override activated - skipping!",color=main_color,).send(ctx)	
		if data.info.get("added_by",None) == ctx.author:
			self.skip_pop(ctx)
			return await Message.EmbedText(title="🎶 Requestor chose to skip - skipping!",color=main_color,).send(ctx)
		if not ctx.author.voice or not ctx.author.voice.channel.id == int(player.channel_id):
			return await Message.EmbedText(title="🎶 You have to be in the same voice channel as me to use that!",color=main_color,).send(ctx)
		skips = self.skips.get(str(ctx.guild.id),[])
		new_skips = []
		channel = ctx.guild.get_channel(int(player.channel_id))
		if not channel:
			return await Message.EmbedText(title="🎶 Something went wrong!",description="That voice channel doesn't seem to exist anymore...",color=main_color,).send(ctx)
		for x in skips:
			member = ctx.guild.get_member(x)
			if not member or member.bot:
				continue
			if not member in channel.members:
				continue
			new_skips.append(x)
		if not ctx.author.id in new_skips:
			new_skips.append(ctx.author.id)
		skippers = [x for x in channel.members if not x.bot]
		needed_skips = math.ceil(len(skippers)/2)
		if len(new_skips) >= needed_skips:
			self.skip_pop(ctx)
			return await Message.EmbedText(title="🎶 Skip threshold met ({}/{}) - skipping!".format(len(new_skips),needed_skips),color=main_color,).send(ctx)
		self.skips[str(ctx.guild.id)] = new_skips
		await Message.EmbedText(title="🎶 Skip threshold not met - {}/{} skip votes entered - need {} more!".format(len(new_skips),needed_skips,needed_skips-len(new_skips)),color=main_color,).send(ctx)

	@commands.command(aliases=['ff', 'ffw'])
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def seek(self, ctx, position = None):
		"""Seeks to the passed position in the song if possible.  Position should be in seconds or in HH:MM:SS format."""

		if position == None or position.lower() in ["moon","moons","moonme","moon me"]:
			return await ctx.invoke(self.playing,moons=position)
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		vals = position.split(":")
		seconds = 0
		multiplier = [3600,60,1]
		vals = ["0"] * (len(multiplier)-len(vals)) + vals if len(vals) < len(multiplier) else vals
		for index,mult in enumerate(multiplier):
			try: seconds += mult * float("".join([x for x in vals[index] if x in "0123456789."]))
			except: return await Message.EmbedText(title="🎶 Malformed seek value!",description="Please make sure the seek time is in seconds, or using HH:MM:SS format.",color=main_color,).send(ctx)
		ms = int(seconds*1000)
		await player.seek(ms)
		return await Message.EmbedText(title="🎶 Seeking to {}!".format(self.format_duration(ms)),color=main_color,).send(ctx)

	@commands.command(aliases=['vol'])
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def volume(self, ctx, volume = None):
		"""Changes the player's volume (0-150%)."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing and not player.is_paused:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		if volume == None:
			cv = int(player.volume*2)
			return await Message.EmbedText(title="🎶 Current volume at {}%.".format(cv),color=main_color,).send(ctx)
		try:
			volume = float(volume)
			volume = int(volume) if volume - int(volume) < 0.5 else int(volume)+1
		except:
			return await Message.EmbedText(title="🎶 Volume must be an integer between 0-150.",color=main_color,).send(ctx)
		volume = 150 if volume > 200 else 0 if volume < 0 else volume
		self.vol[str(ctx.guild.id)] = volume
		await player.set_volume(volume/2)
		await Message.EmbedText(title="🎶 Changed volume to {}%.".format(volume),color=main_color,).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def geteq(self, ctx):
		"""Shows the current equalizer settings."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing and not player.is_paused:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		eq_text = self.print_eq(player.eq.raw)
		return await Message.EmbedText(title="🎶 Current Equalizer Settings",description=eq_text,color=main_color,).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def seteq(self, ctx, *, bands = None):
		"""Sets the equalizer to the passed 15 space-delimited values from -5 (silent) to 5 (double volume)."""
		
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing and not player.is_paused:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		if bands == None: 
			return await Message.EmbedText(title="🎶 Please specify the eq values!",description="15 numbers separated by a space from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		try:
			band_ints = [int(x) for x in bands.split()]
		except:
			return await Message.EmbedText(title="🎶 Invalid eq values passed!",description="15 numbers separated by a space from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		if not len(band_ints) == 15: return await Message.EmbedText(title="🎶 Incorrect number of eq values! ({} - need 15)".format(len(band_ints)),description="15 numbers separated by a space from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		eq_list = [(x,float(0.25 if y/20 > 0.25 else -0.25 if y/20 < -0.25 else y/20)) for x,y in enumerate(band_ints)]
		eq = wavelink.eqs.Equalizer.build(levels=eq_list)
		await player.set_eq(eq)
		player._equalizer = eq # Dirty hack to fix a bug in wavelink
		eq_text = self.print_eq(player.eq.raw)
		return await Message.EmbedText(title="🎶 Set equalizer to Custom preset!",description=eq_text,color=main_color,).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def setband(self, ctx, band_number = None, value = None):
		"""Sets the value of the passed eq band (1-15) to the passed value from -5 (silent) to 5 (double volume)."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing and not player.is_paused:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		if band_number == None or value == None:
			return await Message.EmbedText(title="🎶 Please specify a band and value!",description="Bands can be between 1 and 15, and eq values from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		try:
			band_number = int(band_number)
			assert 0 < band_number < 16
		except:
			return await Message.EmbedText(title="🎶 Invalid band passed!",description="Bands can be between 1 and 15, and eq values from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		try:
			value = int(value)
			value = -5 if value < -5 else 5 if value > 5 else value
		except:
			return await Message.EmbedText(title="🎶 Invalid eq value passed!",description="Bands can be between 1 and 15, and eq values from -5 (silent) to 5 (double volume)",color=main_color,).send(ctx)
		new_bands = [(band_number-1,float(value/20)) if x == band_number-1 else (x,y) for x,y in player.eq.raw]
		eq = wavelink.eqs.Equalizer.build(levels=new_bands)
		await player.set_eq(eq)
		player._equalizer = eq
		eq_text = self.print_eq(player.eq.raw)
		return await Message.EmbedText(title="🎶 Set band {} to {}!".format(band_number,value),description=eq_text,color=main_color,).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def reseteq(self, ctx):
		"""Resets the current eq to the flat preset."""
		await ctx.invoke(self.eqpreset, preset="flat")

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def eqpreset(self, ctx, preset = None):
		"""Sets the current eq to one of the following presets:  Boost, Flat, Metal"""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)
		if not player.is_playing and not player.is_paused:
			return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		if preset == None or not preset.lower() in ("boost","flat","metal"):
			return await Message.EmbedText(title="🎶 Please specify a valid eq preset!",description="Options are:  Boost, Flat, Metal",color=main_color,).send(ctx)
		eq = wavelink.eqs.Equalizer.boost() if preset.lower() == "boost" else wavelink.eqs.Equalizer.flat() if preset.lower() == "flat" else wavelink.eqs.Equalizer.metal()
		await player.set_eq(eq)
		player._equalizer = eq
		eq_text = self.print_eq(player.eq.raw)
		return await Message.EmbedText(title="🎶 Set equalizer to {} preset!".format(preset.lower().capitalize()),description=eq_text,color=main_color,).send(ctx)

	@commands.command(name="loop", aliases=['repeat'])
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def loop(self, ctx, *, yes_no = None):
		"""Checks or sets whether to repeat the current playlist."""
		player = self.client.wavelink.players.get(ctx.guild.id, None)
		if player == None or not player.is_connected:
			return await Message.EmbedText(title="♫ Not connected to a voice channel!", color=main_color).send(ctx)
		current = self.loop11.get(str(ctx.guild.id), False)
		setting_name = "Loop"
		if yes_no == None:
			return await Message.EmbedText(
				title="You did not specify if you want to turn loop on or off!",
				color=discord.Color.red()
			).send(ctx)
		elif yes_no.lower() in ["yes", "on", "true", "enabled", "enable"]:
			yes_no = True
			if current == True:
				msg = '{} remains enabled!'.format(setting_name)
			else:
				msg = '{} is now enabled!'.format(setting_name)
		elif yes_no.lower() in ["no", "off", "false", "disabled", "disable"]:
			yes_no = False
			if current == False:
				msg = '{} remains disabled!'.format(setting_name)
			else:
				msg = '{} is now disabled!'.format(setting_name)
		else:
			msg = "That's not a valid setting!"
			yes_no = current
		if not yes_no == None and not yes_no == current:
			self.loop11[str(ctx.guild.id)] = yes_no
		await Message.EmbedText(title="♫ " + msg, color=main_color).send(ctx)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def stop(self, ctx):
		"""Stops and empties the current playlist."""
		self.dict_pop(ctx)
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if player != None:
			if player.is_playing or player.is_paused:
				await player.stop()
				return await Message.EmbedText(title="🎶 Music stopped and playlist cleared!",color=main_color,).send(ctx)
			else:
				return await Message.EmbedText(title="🎶 Not playing anything!",color=main_color,).send(ctx)
		await Message.EmbedText(title="🎶 Not connected to a voice channel!",color=main_color,).send(ctx)

	@commands.command(aliases=['dc'])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def leave(self, ctx):
		"""Stops and disconnects the client from voice."""
		player = self.client.wavelink.players.get(ctx.guild.id,None)
		if ctx.author.voice:
			if player != None and player.is_connected:
				self.dict_pop(ctx)
				await player.destroy()
				return await Message.EmbedText(title="🎶 I've left the voice channel!",color=main_color,).send(ctx)
			if player == None:
				return await Message.EmbedText(title=f'🎶 I am not connected to a voice channel!').send(ctx)
		if not ctx.author.voice:
			return await Message.EmbedText(title="You are not connected to the voice channel!", color=main_color).send(ctx)
	
	@commands.command(name="lyrics", help="Shows the lyrics of the song mentioned!")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def lyrics(self, ctx : commands.Context, *, song : str = None):
		if song:
			search = song.replace(' ', '%20')
			r1 = requests.get(f'https://some-random-api.ml/lyrics?title={search}')
			data = json.loads(r1.content)
			if not "error" in data:
				e = discord.Embed(color=main_color, title=data["author"] + " - "  + data["title"])
				e.set_thumbnail(url=list(data["thumbnail"].values())[0])
				if len(data["lyrics"]) < 2048:
					e.description = data["lyrics"]
					await ctx.send(embed=e)
					return
				elif len(data["lyrics"]) > 2048:
					lyr1 = data["lyrics"]
					list1 = textwrap.wrap(str(lyr1), width=1000, replace_whitespace=False)
					list2 = []
					index = 0
					for i in list1:
						index += 1
						list2.append({
							"name"  : f"Page {index}",
							"value" : i
						})
					await PagePicker(list=list2,timeout=200,client=self.client,ctx=ctx,color=main_color,title=data["author"] + " - "  + data["title"], max=1,thumbnail=list(data["thumbnail"].values())[0]).pick()
					return
			if "error" in data:
				await Message.EmbedText(
						title=f"Sorry I couldn't find that song's lyrics"
					).send(ctx)
				return
		if not song:
			data = self.data.get(str(ctx.guild.id))
			r1 = requests.get(f'https://some-random-api.ml/lyrics?title={data.title.replace(" ", "%20")}')
			data = json.loads(r1.content)
			if not "error" in data:
				e = discord.Embed(color=main_color, title=data["author"] + " - "  + data["title"])
				e.set_thumbnail(url=list(data["thumbnail"].values())[0])
				if len(data["lyrics"]) < 2048:
					e.description = data["lyrics"]
					await ctx.send(embed=e)
					return
				elif len(data["lyrics"]) > 2048:
					lyr1 = data["lyrics"]
					list1 = textwrap.wrap(str(lyr1), width=1000, replace_whitespace=False)
					list2 = []
					index = 0
					for i in list1:
						index += 1
						list2.append({
							"name"  : f"Page {index}",
							"value" : i
						})
					await PagePicker(list=list2,timeout=200,client=self.client,ctx=ctx,color=main_color,title=data["author"] + " - "  + data["title"], max=1,thumbnail=list(data["thumbnail"].values())[0]).pick()
					return
			if "error" in data:
				await Message.EmbedText(
						title=f"Sorry I couldn't find that song's lyrics",
						color=discord.Color.red()
					).send(ctx)
				return
