import asyncio
import discord
import random
import datetime
import requests, json
from   discord.ext import commands
from   _Utils import Nullify
import re
from bot import main_color
from cogs import DisplayName
import asyncio, urllib, os
from wand.image import Image, COMPOSITE_OPERATORS
from wand.drawing import Drawing
from wand.display import display
from io import BytesIO

def memberForID(checkid, server):
    mems = server.members
    try:
        checkid = int(checkid)
    except:
        return None
    for member in mems:
        if member.id == checkid:
            return member
    return None

def memberForName(name, server):
    mems = server.members
    name = str(name)
    for member in mems:
        if not hasattr(member, "nick"):
            break
        if member.nick:
            if member.nick.lower() == name.lower():
                return member
    for member in mems:
        if member.name.lower() == name.lower():
            return member
    mem_parts = name.split("#")
    if len(mem_parts) == 2:
        try:
            mem_name = mem_parts[0]
            mem_disc = int(mem_parts[1])
        except:
            mem_name = mem_disc = None
        if mem_name:
            for member in mems:
                if member.name.lower() == mem_name.lower() and int(member.discriminator) == mem_disc:
                    return member
    mem_id = re.sub(r'\W+', '', name)
    new_mem = memberForID(checkid=name,server=server)
    if new_mem:
        return new_mem

    return None

def name(member: discord.Member):
    nick = name = None
    try:
        nick = member.nick
    except AttributeError:
        pass
    try:
        name = member.name
    except AttributeError:
        pass
    if nick:
        return Nullify.clean(nick)
    if name:
        return Nullify.clean(name)
    return None

def setup(client):
	client.add_cog(fun(client))

class fun(commands.Cog):
	"""Fun commands which are available to all the members of the server!"""
	class actionable:
		nothingList = []
		clientList  = []
		selfList    = []
		memberList  = []
		itemList    = []

		def computeAction(self, client, ctx, target):
			'''return a message based on the context and argument of the command'''
			mesg = ""

			if not target: # no arguments
				mesg = random.choice(self.nothingList)
			else:
				targetMember = memberForName(name=target, server=ctx.guild)

				if targetMember:
					if self.clientList and targetMember.id == client.user.id:
						mesg = random.choice(self.clientList)
					elif self.selfList and targetMember.id == ctx.message.author.id:
						mesg = random.choice(self.selfList)
					else:
						mesg = random.choice(self.memberList).replace("{}",name(targetMember))
				else:
					mesg = random.choice(self.itemList)
					if '{}' in mesg:
						mesg = mesg.format(target)

			mesgFull = '*{}*, {}'.format(name(ctx.message.author), mesg)
			mesgFull = Nullify.clean(mesgFull)
			return mesgFull
	class eating(actionable):
		nothingList = [ 'you sit quietly and eat *nothing*...',
						'you\'re *sure* there was something to eat, so you just chew on nothingness...',
						'there comes a time when you need to realize that you\'re just chewing nothing for the sake of chewing.  That time is now.']
		clientList = [ 'you try to eat *me* - but unfortunately, I saw it coming - your jaw hangs open as I deftly sidestep.',
					'your mouth hangs open for a brief second before you realize that *I\'m* eating *you*.',
					'I\'m a client.  You can\'t eat me.',
					'your jaw clamps down on... wait... on nothing, because I\'m *digital!*.',
					'what kind of client would I be if I let you eat me?']
		selfList = ['you clamp down on your own forearm - not surprisingly, it hurts.',
					'you place a finger into your mouth, but *just can\'t* force yourself to bite down.',
					'you happily munch away, but can now only wave with your left hand.',
					'wait - you\'re not a sandwich!',
					'you might not be the smartest...']
		memberList = [  'you unhinge your jaw and consume *{}* in one bite.',
						'you try to eat *{}*, but you just can\'t quite do it - you spit them out, the taste of failure hanging in your mouth...',
						'you take a quick bite out of *{}*.  They probably didn\'t even notice.',
						'you sink your teeth into *{}\'s* shoulder - they turn to face you, eyes wide as you try your best to scurry away and hide.',
						'your jaw clamps down on *{}* - a satisfying *crunch* emanates as you finish your newest meal.']
		itemList = [ 	'you take a big chunk out of *{}*. *Delicious.*',
						'your teeth sink into *{}* - it tastes satisfying.',
						'you rip hungrily into *{}*, tearing it to bits!',
						'you just can\'t bring yourself to eat *{}* - so you just hold it for awhile...',
						'you attempt to bite into *{}*, but you\'re clumsier than you remember - and fail...']

	class drinking(actionable):
		nothingList = [ 'you stare at your glass full of *nothing*...',
						'that cup must\'ve had something in it, so you drink *nothing*...',
						'you should probably just go get a drink.',
						'that desk looks pretty empty',
						'are you sure you know what drinking is?',
						'you desperatly search for something to drink']
		clientList = [ 'you try to drink *me*, but I dodge your straw.',
					'You search for me, only to realise that *I* am already drinking you!',
					'I\'m a client.  You can\'t drink me.',
					'you stick a straw in... wait... in nothing, because I\'m *digital!*.',
					'what do you think I am to let you drink me?',
					'I don\'t think you would like the taste of me.',
					'you can\'t drink me, I\'m a machine!']
		selfList = ['you stab yourself with a straw - not surprisingly, it hurts.',
					'you fit yourself in to a cup, but you just can\'t do it.',
					'you happily drink away, but you are now very floppy.',
					'wait - you\'re not a drink!',
					'you might not be the smartest...',
					'you might have some issues.',
					'you try to drink yourself.',
					'why would you drink yourself?']
		memberList = [  'you grab your lucky straw and empty *{}* in one sip.',
						'you try to drink *{}*, but you just can\'t quite do it - you spit them out, the taste of failure hanging in your mouth...',
						'you drink a small sip of *{}*.  They probably didn\'t even notice.',
						'you stab your straw into *{}\'s* shoulder - You run away as they run after you.',
						'you happily drink away - *{}* starts to look like an empty Capri Sun package.',
						'you are thirsty - *{}* sacrifices themself involuntarily.',
						'somehow you end up emptying *{}*.']
		itemList = ['you take a big sip of *{}*. *Delicious.*',
					'your straw sinks into *{}* - it tastes satisfying.',
					'you thirstly guzzle *{}*, it\'s lovely!',
					'you just can\'t bring yourself to drink *{}* - so you just hold it for awhile...',
					'you attempt to drain *{}*, but you\'re clumsier than you remember - and fail...',
					'you drink *{}*.',
					'*{}* dries up from your drinking.',
					'*{}* starts resembling the Aral Sea.']

	class booping(actionable):
		nothingList = [ 'you stretch out your hand in the air, but there\'s nothing there...',
						'you try and find someone to boop, but there\'s no one there.',
						'you look around the channel for someone to boop.',
						'you eye all the heads in the room, just waiting to be booped.',
						'are you sure you have someone to boop?',
						'I get it. You want to boop *someone*.']
		selfList = ['you boop yourself on the nose with your finger.',
					'you try to boop your head, but your hand gets lost along the way.',
					'you happily boop yourself, but you are now very giddy.',
					'wait - are you sure you want to boop yourself?',
					'you might not be the smartest...',
					'you might have some issues.',
					'you try to boop yourself.',
					'why would you boop yourself?']
		memberList = [  'you outstretch your lucky finger and boop *{}* in one go.',
						'you try to boop *{}*, but you just can\'t quite do it - you miss their head, the taste of failure hanging stuck to your hand...',
						'you sneak a boop onto *{}*.  They probably didn\'t even notice.',
						'you poke your hand onto *{}\'s* hand - You run away as they run after you.',
						'you happily drum your fingers away - *{}* starts to look annoyed.',
						'you\'re feeling boopy - *{}* sacrifices themself involuntarily.',
						'somehow you end up booping *{}*.',
						'you climb *{}*\'s head and  use it as a bouncy castle... they feel amused.']
		itemList = ['you put your hand onto *{}*\'s head. *Bliss.*',
					'your hand touches *{}*\'s snoot - it feels satisfying.',
					'you happily boop *{}*, it\'s lovely!',
					'you just can\'t bring yourself to boop *{}* - so you just let your hand linger...',
					'you attempt to boop *{}*, but you\'re clumsier than you remember - and fail...',
					'you boop *{}*.',
					'*{}* feels annoyed from your booping.',
					'*{}* starts resembling a happy pupper.']

	class spooky(actionable):
		nothingList = [ 'you spook no one but yourself',
						'you spook nothing, sp00py...',
						'sadly, no one got spooked',
						'it is sp00... you can\t spook air']
		clientList = [ 'you scared the living pumpkin out of me!',
					'you spooked me so hard, I got the Heebie-jeebies...',
					'you sp00p me? But I\'m a client... I can\'t be spooked!',
					'sorry, but I cannot let you spook me; My digital emotions will get all messed up!'
					'aaaaaaaaaah! Don\t you scare me like that again!']
		selfList = ['go watch a scary movie to be absolutely sp00ped!',
					'boo! Did you scare you?',
					'you look yourself in the mirror and get a little scared...',
					'get spooked by... yourself?',
					'sp00py, but why spook yourself?']
		memberList = [  'you sp00p *{}* so hard that they start screaming!',
						'you tried to sneak up on *{}*, but they heard you sneakin\' and fail...',
						'it is sp00py time! Hey *{}*, boo!',
						'congrats, *{}* dun sp00ked.',
						'get spook3d *{}*!']
		itemList = ['you spook *{}* with no reaction, leaving you looking weird...',
					'*{}* got sp00p3d so hard, it ran away!',
					'you trick or treat *{}* without any reaction...',
					'you do your best to sp00p *{}*, but fail...',
					'sp00py time! *{}* gets sp00ped harder than you thought and starts crying!']

	class highfives(actionable):
		nothingList = [ 'you stand alone for an eternity, hand raised up - desperate for any sort of recognition...',
						'with a wild swing you throw your hand forward - the momentum carries you to the ground and you just lay there - high fiveless...',
						'the only sound you hear as a soft *whoosh* as your hand connects with nothing...']
		clientList = [ 'the sky erupts with 1\'s and 0\'s as our hands meet in an epic high five of glory!',
					'you beam up to the cloud and receive a quick high five from me before downloading back to Earth.',
					'I unleash a fork-bomb of high five processes!',
					'01001000011010010110011101101000001000000100011001101001011101100110010100100001']
		selfList = ['ahh - high fiving yourself, classy...',
					'that\'s uh... that\'s just clapping...',
					'you run in a large circle - *totally* high fiving all your friends...',
					'now you\'re at clienth ends of a high five!']
		memberList = [  'you and *{}* jump up for an epic high five - freeze-framing as the credits roll and some wicked 80s synth plays out.',
						'you and *{}* elevate to a higher plane of existence in wake of that tremendous high five!',
						'a 2 hour, 3 episode anime-esque fight scene unfolds as you and *{}* engage in a world-ending high five!',
						'it *was* tomorrow - before you and *{}* high fived with enough force to spin the Earth in reverse!',
						'like two righteous torpedoes - you and *{}* connect palms, subsequently deafening everyone in a 300-mile radius!']
		itemList = ['neat... you just high fived *{}*.',
					'your hand flops through the air - hitting *{}* with a soft thud.',
					'you reach out a hand, gently pressing your palm to *{}*.  A soft *"high five"* escapes your lips as a tear runs down your cheek...',
					'like an open-handed piston of ferocity - you drive your palm into *{}*.']

	class petting(actionable):
		nothingList = [ 'you absentmindedly wave your hand in the air.',
						'you could have sworn there was a cat there!',
						'you remember that there are no cats here.',
						'you try to pet the cat, but miss because the cat is gone.']
		clientList = [ 'I may be electronic but I still appreciate pets.',
					'*purrrrrrrrrrrrrrr*.',
					'you electrocute yourself trying to pet a computer.']
		selfList = ['you give yourself a nice pat on the head.',
					'too bad there\'s no one else to pet you.',
					'in lieu of anything else to pet, you pet yourself.',
					'your hair is warm and soft.']
		memberList = [  'you give *{}* a pat on the head.',
						'you rub your hand through *{}\'s* hair.',
						'*{}* smiles from your petting.',
						'you try to pet *{}*, but miss because they hid under the bed.',
						'*{}* purrs from your petting.',
						'you pet *{}* but they bite your hand',
						'you try to pet *{}* but they hiss and run away.']
		itemList = ['you rub *{}* but it doesn\'t feel like a cat.',
					'you don\'t hear any purring from *{}*.',
					'you hurt your hand trying to pet *{}*.']

	# Init with the client reference, and a reference to the settings var
	def __init__(self, client):
		self.client = client

	@commands.command(name="pikachu", help="*pika pika*")
	@commands.cooldown(1, 3, commands.BucketType.member)
	@commands.guild_only()
	async def pikachu(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/pikachu")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="dog", help="*bark bark*")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def dog(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/dog")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="cat", help="*meow meow*")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def cat(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/cat")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="fox", help="does a fox howl? lol im dumb")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def fox(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/fox")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="bird", help="a **bird** lol")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def bird(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/birb")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="koala", help="cute, I guess")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def koala(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/koala")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="kangaroo", help="hippity hop hop")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def kangaroo(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/kangaroo")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="raccoon", help="what does a raccoon even do?")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def raccoon(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/racoon")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="whale", help="whale hello there")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def whale(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/img/whale")
		data = json.loads(r1.content)
		await ctx.send(data["link"])
		return

	@commands.command(name="meme", help="Random meme from anywhere on this planet")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def meme(self, ctx: commands.Context):
		r1 = requests.get("https://some-random-api.ml/meme")
		data = json.loads(r1.content)
		e = discord.Embed(color=main_color)
		e.set_footer(
			text=f'"{data["category"].title()}" category • Requested by {ctx.author.name + "#" + ctx.author.discriminator}')
		e.set_image(url=data["image"])
		e.title = data["caption"].title()
		await ctx.send(embed=e)
		return

	@commands.command(name="pokestats", help="pokemon stats, but for nerds.")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def pokestats(self, ctx: commands.Context, *, pokemon: str = None):
		if not pokemon:
			await ctx.send("You did'nt specify a pokemon..")
			return
		if pokemon:
			r1 = requests.get(f"https://some-random-api.ml/pokedex?pokemon={pokemon.replace(' ', '%20')}")
			data = json.loads(r1.content)
			desc = ""
			for k, v in dict(data).items():
				desc += f'    "{k}" : {v},\n'
			desc1 = desc.replace("'", '"')
			await ctx.send(f"```json\n"
						   f"{'{'}\n{desc1}{'}'}\n"
						   f"```")
			return

	@commands.command(name="joke", help="ha.. ha.. ha...")
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def joke(self, ctx: commands.Context):

		r1 = requests.get("https://some-random-api.ml/joke")
		data = json.loads(r1.content)
		embed = discord.Embed(color=main_color)
		if len(data["joke"]) > 100:
			embed.description = "**" + data["joke"] + "**"
			await ctx.send(embed=embed)
			return
		if len(data["joke"]) < 100:
			embed.title = data["joke"]
			await ctx.send(embed=embed)
			return

	@commands.command(name="comment", help="comment on a yt vid, very very nice")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def comment(self, ctx: commands.Context, member: discord.Member, *, message: str = None):
		member = ctx.author if not member else member
		avatar = member.avatar_url
		message = message.replace(' ', '%20')
		url = f"https://some-random-api.ml/canvas/youtube-comment?avatar={avatar}&username={member.display_name}&comment={message}"
		request = requests.get(url)
		with open("youtube-comment.png", "wb") as f:
			f.write(request.content)
		await ctx.send(file=discord.File(fp="youtube-comment.png", filename="youtube-comment.png"),
					   embed=discord.Embed(title=f"{member.display_name} commented...", color=main_color).set_image(
						   url=f"attachment://youtube-comment.png"))
		os.remove("youtube-comment.png")
		return

	@commands.command(name="gay", help="well. it.. **gay-ifies**...")
	@commands.cooldown(1, 3, commands.BucketType.member)
	@commands.guild_only()
	async def gay(self, ctx: commands.Context, member: discord.Member = None):
		member = ctx.author if not member else member
		avatar = member.avatar_url_as(size=512, format='png')
		av = Image(blob=await avatar.read())
		road = Image(filename="gay_flag.png")
		g = av.clone()
		r = road.clone()
		with Drawing() as draw:
			r.resize(width=g.width + 50, height=g.height + 20)
			r.scale(int(r.width * 1.2), int(r.height * 1.2))
			r.rotate(degree=-2.5)
			rand_amplitude = random.uniform(1.2, 2.6)
			rand_wave = random.uniform(20.0, 50.5)
			r.wave(amplitude=rand_amplitude - 0.1, wave_length=100.0 + rand_wave, method="undefined")
			r.alpha_channel = True
			r.evaluate(operator='set', value=r.quantum_range * 0.5, channel='alpha')
			draw.composite(operator="over", left=-30, top=-45, width=r.width, height=r.height, image=r)
			draw(g)
			with BytesIO() as img:
				g.format = 'png'
				g.save(img)
				img.seek(0)
				await ctx.send(file=discord.File(fp=img, filename="gay.png"))
				return

	@commands.command(name="start", help='shh. secret.. it cant be used by you...')
	@commands.cooldown(1, 3, commands.BucketType.member)
	@commands.is_owner()
	async def start(self, ctx: commands.Context):
		await ctx.send("started..")
		while True:
			try:
				wait = await self.client.wait_for("message", timeout=10,
												  check=lambda x: x.author == ctx.author and x.channel == ctx.channel)
				r1 = requests.get(f"https://some-random-api.ml/chatbot?message={str(wait.content).replace(' ', '%20')}")
				data = json.loads(r1.content)
				await ctx.send(data["response"])
			except asyncio.TimeoutError:
				await ctx.send("stopped.")
				break

	@commands.command(name="panda", help="idk its a panda")
	@commands.cooldown(1, 3, commands.BucketType.member)
	@commands.guild_only()
	async def panda(self, ctx: commands.Context, red: str = None):
		if not red:
			r1 = requests.get("https://some-random-api.ml/img/Panda")
			data = json.loads(r1.content)
			await ctx.send(data["link"])
			return
		if red.lower() == "red":
			r1 = requests.get("https://some-random-api.ml/img/red_panda")
			data = json.loads(r1.content)
			await ctx.send(data["link"])
			return

        
	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def eat(self, ctx, *, member : str = None):
		"""Eat like a boss."""

		msg = self.eating.computeAction(self.eating, self.client, ctx, member)
		return

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def drink(self, ctx, *, member : str = None):
		"""Drink like a boss."""

		msg = self.drinking.computeAction(self.drinking, self.client, ctx, member)
		await ctx.channel.send(msg)
		return

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def boop(self, ctx, *, member : str = None):
		"""Boop da snoot."""

		msg = self.booping.computeAction(self.booping, self.client, ctx, member)
		await ctx.channel.send(msg)
		return

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def spook(self, ctx, *, member : str = None):
		"""sp00ktober by camiel."""

		if datetime.date.today().month == 10:
			# make it extra sp00py because it is spooktober
			await ctx.message.add_reaction("🎃")
		msg = self.spooky.computeAction(self.spooky, self.client, ctx, member)
		await ctx.channel.send(msg)
		return

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def highfive(self, ctx, *, member : str = None):
		"""High five like a boss."""

		msg = self.highfives.computeAction(self.highfives, self.client, ctx, member)
		await ctx.channel.send(msg)
		return

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def pet(self, ctx, *, member : str = None):
		"""pet kitties."""

		msg = self.petting.computeAction(self.petting, self.client, ctx, member)
		await ctx.channel.send(msg)
		return
	
	@commands.command(name="ppsize")
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.member)
	async def ppsize(self, ctx : commands.Context, member : discord.Member = None):
		"""pretty self-explanatory..."""
		member = ctx.author if not member else member
		ID = member.id
		lol = round(ID / 47 ** 10)
		pp = "8"
		pp += "=" * lol
		pp += "D"
		return await ctx.send(f"{str(ctx.author)} found {str(member)}'s PP!\n"
							  f"**{pp}**")
