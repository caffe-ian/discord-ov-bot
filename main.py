import os, random, motor.motor_asyncio, lists, asyncio, discord, time
import interclass
from discord.ext import commands, tasks
from datetime import datetime
import functions
from functions import aa, finduser, updateset, updateinc, ab, gettitle
from dotenv import load_dotenv
import gc
import traceback, sys
load_dotenv()

dakey = os.getenv("TOKEN")
db_url = os.getenv("MONGO")
commandprefix = ["ov ", "OV ", "oV ", "Ov ", "ov", "OV", "oV", "Ov"]
prefix = "ov "
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(*commandprefix), help_command=None, case_insensitive=True,intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, replied_user=False, roles=False), chunk_guilds_at_startup=False)
color = discord.Colour
star = u"\u2B50"

extensions = ["cogs.funcog", "cogs.crimecog", "cogs.citycog", "cogs.carcog", "cogs.maincog", "cogs.othercog", "cogs.devcog"]
bot.exten = extensions

cluster = motor.motor_asyncio.AsyncIOMotorClient(db_url)
db = cluster['maindb']
cll = db['userdata']
bot.cll = cll
dcll = db['userdonatedata']
bot.dcll = dcll
gcll = db['guilddata']
bot.gcll = gcll
bm = db['blackmarket']
bot.bm = bm
ccll = db['cardata']
bot.ccll = ccll
dll = db['dispatcher']
bot.dll = dll

donatorlist = []

async def get_server_info():
    cluster = motor.motor_asyncio.AsyncIOMotorClient(db_url, serverSelectionTimeoutMS=5000)
    try:
        await cluster.server_info()
        print(" * Connected to the Database server.")
    except Exception:
        print("Unable to connect to the server.")

@bot.check
async def globalchecks(ctx):
  if ctx.guild is None and ctx.command.__str__() != "help" and ctx.command.__str__() != "claim":
    await ctx.respond("You cannot use commands in DMs")
    return False
  try:
    if ctx.command.__str__() != "learn":
      await ctx.interaction.response.defer()
  except:
    pass
  guild = await gcll.find_one({"id": 863025676213944340})
  if guild['maintenance'] == True and not ctx.author.id == 615037304616255491:
    return False
  if ctx.guild is not None:
    if not ctx.guild.chunked:
      await ctx.guild.chunk()
    user = await finduser(ctx.author.id)
    if user is not None:
      if ctx.guild.id in user['q']:
        if ctx.command.__str__() != "quarantine":
          return False
  return True

async def achieve(ctx, userdata):
  userdonatedata = await dcll.find_one({"id": userdata['id']})
  available_titles = await functions.new_title(userdonatedata, userdata)
  available_badges = functions.new_badge(userdonatedata, userdata)

  if available_titles or available_badges:
    embed = discord.Embed(title=f"Congratulations {ctx.author}", description=f"You achieved {len(available_titles + available_badges)} new achievement!", color=color.green())
    for achievement in (available_titles+available_badges)[:5]:
      if achievement in available_titles:
        embed.add_field(name=achievement, value=lists.title_description[achievement], inline=False)
      elif achievement in available_badges:
        embed.add_field(name=achievement, value=lists.badge_description[achievement], inline=False)
    if len(available_titles + available_badges) > 5:
      embed.add_field(name=f"You achieved another **{len(available_titles+available_badges)-5}** achievement!", value="Type `/accolade` to check it out!", inline=False)
    else:
      embed.set_footer(text="Type /accolade to check it out!")
    try:
      await ctx.channel.send(embed=embed)
    except:
      await ctx.respond("***Missing Permissions:*** Send messages")
    if available_titles:
      await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"titles": {"$each": available_titles}}})
    if available_badges:
      await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"badges": {"$each": available_badges}}})

async def inform(ctx, user, server):
  upd = None
  updates = [server['updates'][ts] for ts in list(server['updates'].keys()) if int(ts) > user['lastcmdtime']]
  announcement = [server['announcement'][ts] for ts in list(server['announcement'].keys()) if int(ts) > user['lastcmdtime']]
  if len(updates) and not len(announcement):
    t = "\n\U0001f4a0 "
    upd = discord.Embed(title="There was an update!", color=color.blurple()).set_footer(text="Join our official server for detailed information")
    upd.add_field(name="Latest changes", value=f"{t}{(t.join(sorted(updates, key=lambda x: list(server['updates'].keys())[list(server['updates'].values()).index(x)], reverse=True)[:4]))[:1024]}")
    upd.timestamp = datetime.now()
  elif len(announcement) and not len(updates):
    t = "\n\U0001f4a0 "
    upd = discord.Embed(title="Global announcement", color=color.blurple()).set_footer(text="Join our official server for detailed information")
    upd.add_field(name="Contents", value=f"{t}{(t.join(sorted(announcement, key=lambda x: list(server['announcement'].keys())[list(server['announcement'].values()).index(x)], reverse=True)[:4]))[:1024]}")
    upd.timestamp = datetime.now()
  elif len(updates) and len(announcement):
    t = "\n\U0001f4a0 "
    upd = discord.Embed(title="There was an update and announcement!", color=color.blurple()).set_footer(text="Join our official server for detailed information")
    upd.add_field(name="Updates", value=f"{t}{(t.join(sorted(updates, key=lambda x: list(server['updates'].keys())[list(server['updates'].values()).index(x)], reverse=True)[:4]))[:512]}", inline=True)
    upd.add_field(name="Announcements", value=f"{t}{(t.join(sorted(announcement, key=lambda x: list(server['announcement'].keys())[list(server['announcement'].values()).index(x)], reverse=True)[:4]))[:512]}", inline=True)
    upd.timestamp = datetime.now()
  if upd is None:
    if round(time.time())-user['lastcmdtime'] > 3600:
      try:
        await ctx.channel.send(f"Welcome back, {gettitle(user)}{ctx.author.mention}!")
      except:
        try:
          await ctx.respond("I am missing some permissions!\nCheck your channel permissions or my role permissions\nPermissions needed: View channels, Manage webhooks, Create invite, Change nickname, Manage nicknames, Send messages, Send messages in threads, Attach files, Add reactions, Use external emoji, Manage messages, Read message history, Use application commands, Connect, Speak")
        except discord.HTTPException:
          try:
            if ctx.guild.me.nick is None or " (Missing Permissions)" not in ctx.guild.me.nick:
              await ctx.guild.me.edit(nick = ((ctx.guild.me.nick + " (Missing Permissions)") if ctx.guild.me.nick is not None else (ctx.guild.me.name + " (Missing Permissions)")))
          except:
            pass
        return
  else:
    try:
      await ctx.channel.send(f"Welcome back, {gettitle(user)}{ctx.author.mention}!", embed=upd)
    except:
      try:
        await ctx.respond("I am missing some permissions!\nCheck your channel permissions or my role permissions\nPermissions needed: View channels, Manage webhooks, Create invite, Change nickname, Manage nicknames, Send messages, Send messages in threads, Attach files, Add reactions, Use external emoji, Manage messages, Read message history, Use application commands, Connect, Speak")
      except discord.HTTPException:
        try:
          if ctx.guild.me.nick is None or " (Missing Permissions)" not in ctx.guild.me.nick:
            await ctx.guild.me.edit(nick = ((ctx.guild.me.nick + " (Missing Permissions)") if ctx.guild.me.nick is not None else (ctx.guild.me.name + " (Missing Permissions)")))
        except:
          pass
      return

def custom_cooldown(r, p, r2, p2, type = commands.BucketType.user):
    def decorator(func):
        if isinstance(func, commands.Command):
            func._buckets = commands.DynamicCooldownMapping(dummy, r, p, r2, p2, type)
        else:
            func.__commands_cooldown__ = commands.DynamicCooldownMapping(dummy, r, p, r2, p2, type)
        return func
    return decorator

commands.custom_cooldown = custom_cooldown

class DynamicCooldownMapping(commands.CooldownMapping):
    def __init__(self, factory, r, p, r2, p2, type) -> None:
        super().__init__(None, type)
        self._factory = factory
        self.r = r
        self.p = p
        self.r2 = r2
        self.p2 = p2
    def copy(self):
        ret = commands.DynamicCooldownMapping(self._factory, self._type)
        ret._cache = self._cache.copy()
        return ret
    @property
    def valid(self) -> bool:
        return True
    def create_bucket(self, message):
        return self._factory(message, self.r, self.p, self.r2, self.p2)

commands.DynamicCooldownMapping = DynamicCooldownMapping

def dummy(message, rate, per, rate2, per2):
    if message.author.id in donatorlist:
        return commands.Cooldown(rate2, per2)
    else:
        return commands.Cooldown(rate, per)

@bot.event
async def on_ready():
  print("Waiting for bot to ready")
  await bot.wait_until_ready()
  print(f"Logged in as {bot.user}")
  await gcll.update_one({"id": 863025676213944340}, [{"$set": {"2ndlastrestart": "$lastrestart"}}])
  await gcll.update_one({"id": 863025676213944340}, {"$set": {"lastrestart": round(time.time())}})

@bot.event
async def on_guild_join(guild):
  if await gcll.find_one({"id": guild.id}) == None:
    gd = await gcll.find_one({"$query": {},"$orderby": {"index": -1}})
    newguild = {"index": gd['index']+1, "id": guild.id, "name": guild.name, "members": guild.member_count, "attack": True, "larceny": True, "race": True}

    await gcll.insert_one(newguild)

    print(f"New server joined: {guild.name} ({guild.id})")

    joinembed = discord.Embed(title = "Thanks for inviting OV Bot to " + guild.name + "!", description = "Type `/story` to get started!\n\n**__[Join our official server here!](https://discord.gg/bBeCcuwE95)__**\n**__[Invite the bot to your server!](https://discord.com/api/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&redirect_uri=https%3A%2F%2Fov-bot.herokuapp.com%2F&scope=bot%20applications.commands)__**\n**__[Check out our official website!](https://ov-bot.up.railway.app/)__**\n\n__**[Privacy Policy](https://ov-bot.up.railway.app/privacy-policy/)**__", color = color.green())
    if not guild.icon == None:
      joinembed.set_thumbnail(url = guild.icon.url)
    joinembed.set_footer(text = "Have Fun!")

    channels = [x for x in guild.text_channels if x.permissions_for(guild.me).send_messages]

    try:
      await channels[0].send(embed=joinembed)
    except:
      await guild.me.edit(nick=bot.user.name+" [No Permission]")
    await guild.me.edit(nick=bot.user.name)
    await bot.get_channel(906514084453818398).send(f"**New server joined:** {guild.name} ({guild.id})")

@bot.event
async def on_guild_remove(guild):
  if guild.name is None:
    return
  if guild.id != 863025676213944340:
    await gcll.delete_one({"id": guild.id})

  print("Server left: " + guild.name + " " + str(guild.id))
  await bot.get_channel(906514084453818398).send(f"**Server left:** {guild.name} ({guild.id})")

@bot.event
async def on_message(msg):
  if msg.author == bot.user:
    return

  if "<@!863028787708559400>" in msg.content:
    await msg.channel.send("What do you want, type `/help` to see a list of commands")

  if msg.content.startswith("ov"):
    await msg.channel.send("This bot has migrated to slash commands! Type `/help` to see a list of commands")

  if "<@!615037304616255491>" in msg.content:
    owner = bot.get_user(615037304616255491)
    msglink = msg.jump_url
    channel = msg.channel
    messages = await channel.history(limit=5).flatten()
    messages.reverse()
    mentionembed = discord.Embed(title=f"{msg.author} Mentioned you in {msg.guild.name}!",description=f"**Message Link:** [**Jump**]({msglink})",color=color.green())
    mentionembed.add_field(name="Message Content",value="\n".join([("**" + str(msg.author) + ":** " + msg.content) for msg in messages]))
    mentionembed.timestamp = datetime.now()
    await owner.send(embed=mentionembed)

  await bot.process_commands(msg)

@bot.event
async def on_application_command(ctx):
  if ctx.guild is None:
    return
  if ctx.guild.me.nick is not None and " (Missing Permissions)" in ctx.guild.me.nick:
    try:
      await ctx.guild.me.edit(nick = ctx.guild.me.nick.replace(" (Missing Permissions)", ""))
    except:
      pass
  user = await finduser(ctx.author.id)
  if user is not None:
    if user['blocked'] == True:
      await ctx.respond("Please wait before using another command")
      return
  if await gcll.find_one({"id": ctx.guild.id}) == None:
    bot.dispatch("guild_join", ctx.guild)
  if not ctx.author.id == 615037304616255491:
    await gcll.update_one({"id": 863025676213944340}, {"$set": {"lastcmd": str(ctx.command), "lastcmduser": str(ctx.author), "lastcmduserid": ctx.author.id, "lastcmdtime": round(time.time())}})
  server = await gcll.find_one({"id": 863025676213944340})
  servermaintenance = server['maintenance']
  if not ctx.author.id == 615037304616255491:
    if servermaintenance == True:
      servermaintime = server['maintime']
      serverreason = server['reason']
      try:
        servermaintime = int(servermaintime)
        m = discord.Embed(title="The bot is under maintenance",description="Please stand by",color=color.green())
        m.add_field(name="Reason",value=serverreason,inline=False)
        m.add_field(name="Estimated time",value=ab(servermaintime-round(time.time())),inline=False)
        m.add_field(name="Support",value="Join our official server **[here](https://discord.gg/bBeCcuwE95)** for more information if you have any questions",inline=False)
        await ctx.respond(embed=m)
        return
      except:
        m = discord.Embed(title="The bot is under maintenance",description="Please stand by",color=color.green())
        m.add_field(name="Reason",value=serverreason,inline=False)
        m.add_field(name="Estimated time",value=servermaintime,inline=False)
        m.add_field(name="Support",value="Join our official server **[here](https://discord.gg/bBeCcuwE95)** for more information if you have any questions",inline=False)
        await ctx.respond(embed=m)
        return
  user = await finduser(ctx.author.id)
  if user is None and ctx.command.__str__() != "":
    await ctx.respond(f"Hey {ctx.author.mention}! Type `/story` to start playing OV Bot!")
    return
  if ctx.guild.id in user['q']:
    if ctx.command.__str__() != "quarantine":
      await ctx.respond("You quarantined yourself in this server!")
  await inform(ctx, user, server)
  await updateset(ctx.author.id, "lastcmdtime", round(time.time()))
  await updateinc(ctx.author.id, 'cmd', 1)
  if user['lvl'] >= 100 and "m4" not in user:
    embed = discord.Embed(title="The Syndicate’s Call", description=f"_You've proven yourself, {ctx.author.name}, by reaching **Level 100**. That means you’re either smart, ruthless, or lucky. Maybe all three.\nThe Mafia Council is watching. I’m giving you a seat at the table—one that doesn’t come with second chances. You take it, or you walk away and stay in the shadows where you came from.\nDecide fast. This offer won’t wait._\n\n_Join our [official server](https://discord.gg/bBeCcuwE95) and use /claim to join the mafia council_\n**As a member of the Mafia Council, you’ll gain access to exclusive insider news, including first-hand reports and confidential information unavailable to the public.**", color=color.default())
    
    file = await functions.npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    view = interclass.Story(ctx, "Do not show again")
    msg = view.message = await ctx.respond(embed=embed, view=view, file=file, ephemeral=True)

    await view.wait()
    if view.value is None:
      pass
    elif view.value is True:
      await updateset(ctx.author.id, 'm4', 1)
      await msg.edit(content="This will not show up again", embed=None, view=None, attachments=[])
  username = user['name']
  if not username == ctx.author.name:
    await updateset(ctx.author.id, 'name', ctx.author.name)
  guild = await gcll.find_one({"id": ctx.guild.id})
  guildname = guild['name']
  guildmembers = guild['members']
  if not guildname == ctx.guild.name:
    await gcll.update_one({"id": ctx.guild.id}, {"$set": {"name": ctx.guild.name}})
  if not guildmembers == ctx.guild.member_count:
    await gcll.update_one({"id": ctx.guild.id}, {"$set": {"members": ctx.guild.member_count}})
  userbanned = user['banned']
  usertimer = user['timer']
  if userbanned == True:
    await ctx.respond(embed=discord.Embed(title="Rip", description=f"You are banned from the bot for the following reason: {user['br']}\n\nJoin our official server for support or ban appeal **__[here](https://discord.gg/bBeCcuwE95)__**", color=color.red()))
    return
  try:
    userblockedtimer = usertimer['blocked']
    await ctx.respond(f"You have been temporarily blocked from playing the Bot! Time left: {ab(userblockedtimer-round(time.time()))}")
    return
  except:
    pass

  if str(ctx.command) != "use":
    try:
      userinhosptimer = usertimer['hosp']
      if userinhosptimer > 1: # and ctx.command.__str__() != "use":
        await ctx.respond(f"You are in Hospital! You can't do anything for {ab(userinhosptimer-round(time.time()))}\n-# Tips: You can use medical kits by typing `/use item:medical` to get out of the hospital!")
        return
    except:
      pass

    try:
      userinjailtimer = usertimer['jail']
      if userinjailtimer > 1: # and ctx.command.__str__() != "use":
        await ctx.respond(f"You are in Jail! You can't do anything for {ab(userinjailtimer-round(time.time()))}\n-# Tips: You can use `/bust` to bust people out of jail!")
        return
    except:
      pass
  await achieve(ctx, user)
  userlastcmd = user['lastcmd']
  if str(ctx.command) == userlastcmd:
    await updateinc(ctx.author.id, 'cmdcount', 1)
  else:
    await updateset(ctx.author.id, 'cmdcount', 0)
  user = await finduser(ctx.author.id)
  usercmdcount = user['cmdcount']
  userwarns = user['warns']
  if usercmdcount == 10 and not userlastcmd in lists.spamcmds:
    await ctx.channel.send(f"{gettitle(user)}{ctx.author.mention} stop repeating the same command, it will get you warned")
  if usercmdcount >= 20 and not userlastcmd in lists.spamcmds:
    blockedtime = 300 + (300*userwarns)
    await updateset(ctx.author.id, 'timer.blocked', round(time.time())+blockedtime)
    await updateset(ctx.author.id, 'timer.warns', round(time.time())+2592000)
    await updateinc(ctx.author.id, 'warns', 1)
    await updateset(ctx.author.id, 'cmdcount', 0)
    dm = bot.get_user(ctx.author.id)
    warnembed = discord.Embed(title="Warn",description=f"You seem like using an autotyper!\nAutotyper is not allowed and it is against the bot rules\nIt will get you banned if you keep on using it\nIf you are not using one, stop spamming the same command!\n\n**You are now currently blocked from playing the bot for {ab(blockedtime)}**\n\nYou have been warned {userwarns+1} times in total\n3 Total warns will get you banned!\nWarns will be automatically removed after a month",color=color.gold())
    warnembed.set_footer(text="Stop doing it as it will get you banned from the bot!")
    await dm.send(embed=warnembed)
    await ctx.channel.send(f"{ctx.author.mention}", embed=warnembed)
  user = await finduser(ctx.author.id)
  userwarns = user['warns']
  if userwarns > 3:
    await updateset(ctx.author.id, 'banned', True)
    await updateset(ctx.author.id, 'br', 'Using an Autotyper')
    dm = bot.get_user(ctx.author.id)
    banembed = discord.Embed(title="You have been banned!",description="You have been banned from the bot for the reason of: Using an autotyper\nIf you have any questions join our official Discord server and ask for help!\n[**Join our official server here!**](https://discord.gg/bBeCcuwE95)",color=color.red())
    banembed.set_footer(text="rip 4ever")
    await dm.send(embed=banembed)
    await updateset(ctx.author.id, 'cmdcount', 0)
    return
  if userwarns > 0:
    try:
      usertimer['warns']
    except:
      await updateset(ctx.author.id, 'timer.warns', round(time.time())+2592000)
  if user['heat'] >= 1000:
    await functions.jail(ctx, ctx.author)
  await updateset(ctx.author.id, 'lastcmd', str(ctx.command))
  userproperty = user['property']
  userstorage = user['storage']
  userlvl = user['lvl']
  usercmd = user['cmd']
  usercash = user['cash']
  userstash = user['stash']
  userstashc = user['stashc']
  userstoragelist = sorted(list(user['storage']))
  userweapon = user['equipments']['weapon']
  usertimer = user['timer']

  await updateset(ctx.author.id, 'cash', round(usercash))

  try:
    usersafeq = userstorage['Safe']
    await updateset(ctx.author.id,'stashc',(userproperty*100)+(usersafeq*500))
  except:
    await updateset(ctx.author.id, 'stashc', userproperty*100)
    pass
  if userstash > userstashc and ctx.author.id != 615037304616255491:
    exceed = userstash - userstashc
    await updateinc(ctx.author.id, 'stash', -exceed)
    await updateinc(ctx.author.id, 'cash', exceed)

  if not userweapon == "" and not userweapon in userstoragelist:
    await updateset(ctx.author.id,'equipments.weapon',"")

  if usercmd == 5:
    await updateinc(ctx.author.id, 'exp', 100)

  exppercmd = 0

  if userlvl < 5:
    exppercmd = random.uniform(2.00, 3.00)
  elif userlvl < 10:
    exppercmd = random.uniform(1.00, 1.50)
  elif userlvl < 30:
    exppercmd = random.uniform(0.80, 1.20)
  elif userlvl < 50:
    exppercmd = random.uniform(0.50, 1.00)
  elif userlvl < 80:
    exppercmd = random.uniform(0.20, 0.60)
  elif userlvl < 100:
    exppercmd = random.uniform(0.10, 0.20)
  elif userlvl < 120:
    if random.randint(1,5) == 1:
      exppercmd = random.uniform(0.1, 0.2)
  elif userlvl < 150:
    if random.randint(1,5) == 1:
      exppercmd = random.uniform(0.05, 0.1)
  elif userlvl >= 150:
    if random.randint(1,10) == 1:
      exppercmd = random.uniform(0.05, 0.1)

  if exppercmd != 0:
    if user['donor'] == 1:
      exppercmd *= 1.5
    elif user['donor'] == 2:
      exppercmd *= 2
    if ctx.channel.id == 876672414086475776:
      exppercmd = round(exppercmd * 1.5, 2)
    if functions.not_max_level(user):
      await updateinc(ctx.author.id, 'exp', round(exppercmd, 2))

  user = await finduser(ctx.author.id)
  userlvl = user['lvl']
  userexp = user['exp']

  if userexp >= ((userlvl * 100) + 100):
    await updateinc(ctx.author.id, 'lvl', 1)
    user = await finduser(ctx.author.id)
    userlvl = user['lvl']
    await updateinc(ctx.author.id, 'cash', (userlvl*50))
    await ctx.channel.send(f"Congratulations {gettitle(user)}{ctx.author.mention}, you are now level {userlvl}! <:cash:1329017495536930886> {userlvl*50} has been awarded to you! Buy a better property to increase maximum level!")

  if random.random() <= (0.01+(0.01*user['drugs']['ecstasy'])):
    events = ["Bling-bling", "Runaway!", "Free Hugs!", "Beat Up"]
    event_desc = {
      "Bling-bling": "There's something shiny on the ground!", 
      "Runaway!": "A robber is running away!", 
      "Free Hugs!": "Hug the mascot!", 
      "Beat Up": "Punch the hoodlum!"
    }
    button = {
      "Bling-bling": "Pick", 
      "Runaway!": "Tackle", 
      "Free Hugs!": "Hug", 
      "Beat Up": "Punch"
      }
    event = random.randint(0, len(events)-1)
    random_event = events[event]
    embed = discord.Embed(title=random_event, description=event_desc[random_event], color=color.random()).set_footer(text="Be the first one to click the button below!")
    view = interclass.Event(ctx, button[random_event])
    view.message = await ctx.channel.send(embed=embed, view=view)

    await view.wait()

    if view.value != []:
      if event == 0:
        prize = random.randint(60, 70)
        await ctx.channel.send(f"<@{view.value[0]}> you picked up the item and it turns out to be {'a' if prize == 69 else 'an'} {'Luxury Car Key <:luxury_car_key:1358506290237804695>' if prize == 69 else 'Average Car Key <:average_car_key:1358506292725022761>'}!")
        if prize == 69:
          await updateinc(view.value[0], 'storage.Luxury Car Key', 1)
        else:
          await updateinc(view.value[0], 'storage.Average Car Key', 1)
      elif event == 1:
        prize = random.randint(200, 1000)
        prize = prize+round(prize*(user['stats']['cha']/1000))
        await ctx.channel.send(f"<@{view.value[0]}> you tackled the robber and the victim gave you <:cash:1329017495536930886> {prize}!")
        await updateinc(view.value[0], 'cash', prize)
      elif event == 2:
        cha = random.randint(2, 4)
        if cha + user['stats']['cha'] > 3000:
          cha = 3000 - user['stats']['cha']
        await ctx.channel.send(f"<@{view.value[0]}> you hugged the mascot and gained {cha} charisma <:charisma:940955424910356491>!")
        await updateinc(view.value[0], 'stats.cha', cha)
      elif event == 3:
        stat = random.choice(["str", "def", "spd", "dex"])
        statistic = {
          "str": "strength",
          "def": "defense",
          "spd": "speed",
          "dex": "dexterity"
        }
        emoji = {
          "str": "<:dumbbell:905773708369612811>",
          "def": "<:shield:905782766673743922>",
          "spd": "<:speed:905800074955739147>",
          "dex": "<:dodge1:905801069857218622>"
        }
        amount = random.randint(5, 10)
        user = await finduser(view.value[0])
        if round(amount + user['stats'][stat], 2) > user['lvl']*10:
          amount = round(user['lvl']*10 - user['stats'][stat], 2)
        if amount < 0:
          amount = 0
        await ctx.channel.send(f"<@{view.value[0]}> you punched the hoodlum and gained {amount} {statistic[stat]} {emoji[stat]}!")
        await updateinc(view.value[0], f'stats.{stat}', amount)

  if random.randint(1, 100) == 1:
    await ctx.channel.send(f"-# Tips: {random.choice(lists.tips)}")

@bot.event
async def on_command_error(ctx, error):
  if not isinstance(error, commands.CommandOnCooldown):
    try:
      ctx.command.reset_cooldown(ctx)
    except:
      pass
  if isinstance(error, commands.CommandOnCooldown):
    user = await finduser(ctx.author.id)
    userinhosp = user['inhosp']
    userinjail = user['injail']
    if userinhosp == True or userinjail == True:
      return
    cdembed = discord.Embed(title = "Command on cooldown!", color = color.gold())
    if ctx.author.id in donatorlist:
      cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(error.retry_after)}`!\nYou are a donator so the cooldown is `{ab(error.cooldown.per)}`")
    else:
      cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(error.retry_after)}`!\nCooldown for this command is `{ab(error.cooldown.per)}`\nDonator has shorter cooldown on some commands!")
    cdembed.set_footer(text = "Chill!")

    await ctx.send(embed=cdembed)
  elif isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have the permission to use this command: `Administrator`")
  elif isinstance(error, commands.MaxConcurrencyReached):
    await ctx.send("There is already a larceny going on in the server")
  elif isinstance(error, commands.UserNotFound):
    await ctx.send("Cannot find this user!")
  elif isinstance(error, commands.MemberNotFound):
    await ctx.send("Cannot find this member!")
  elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
    await ctx.send("Enter something valid")
  elif isinstance(error, commands.CommandInvokeError):
    print(f"{ctx.author}: {ctx.command} " + str(error.original))
    error = error.original
    if isinstance(error, discord.HTTPException):
      if error.code == 50035:
        await ctx.send("Embed error")
        return
      elif error.code == 50015 or error.code == 50013:
        try:
          await ctx.send("I am missing some permissions!\nCheck your channel permissions or my role permissions\nPermissions needed: View channels, Manage webhooks, Create invite, Change nickname, Manage nicknames, Send messages, Send messages in threads, Attach files, Add reactions, Use external emoji, Manage messages, Read message history, Use application commands, Connect, Speak")
        except discord.HTTPException:
          if ctx.guild.me.nick is None or " (Missing Permissions)" not in ctx.guild.me.nick:
            await ctx.guild.me.edit(nick = ((ctx.guild.me.nick + " (Missing Permissions)") if ctx.guild.me.nick is not None else (ctx.guild.me.name + " (Missing Permissions)")))
        return
  else:
    print(f"{ctx.author}: {ctx.command} | {ctx.message.content} | " + str(error)[:100])
  if not isinstance(error, commands.CommandNotFound) and not isinstance(error, commands.CommandOnCooldown) and bot.user.id == 863028787708559400:
    await bot.get_channel(909716483704238111).send(f"**Error from {ctx.author} ({ctx.author.id})**: Command `{ctx.command}` | {ctx.message.content} | {str(error)[:200]}")

@bot.event
async def on_application_command_error(ctx, error):
  if not isinstance(error, commands.CommandOnCooldown):
    try:
      ctx.command.reset_cooldown(ctx)
    except:
      pass
  if isinstance(error, commands.CommandOnCooldown):
    user = await finduser(ctx.author.id)
    userinhosp = user['inhosp']
    userinjail = user['injail']
    if userinhosp == True or userinjail == True:
      return
    cdembed = discord.Embed(title = "Command on cooldown!", color = color.gold())
    if ctx.author.id in donatorlist:
      cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(error.retry_after)}`!\nYou are a donator so the cooldown is `{ab(error.cooldown.per)}`")
    else:
      cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(error.retry_after)}`!\nCooldown for this command is `{ab(error.cooldown.per)}`\nDonator has shorter cooldown on some commands!")
    cdembed.set_footer(text = "Chill!")

    await ctx.respond(embed=cdembed)
  elif isinstance(error, commands.MissingPermissions):
    await ctx.respond("You don't have the permission to use this command: `Administrator`")
  elif isinstance(error, commands.MaxConcurrencyReached):
    await ctx.respond("There is already a larceny going on in the server")
  elif isinstance(error, commands.UserNotFound):
    await ctx.respond("Cannot find this user!")
  elif isinstance(error, commands.MemberNotFound):
    await ctx.respond("Cannot find this member!")
  elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
    await ctx.respond("Enter something valid")
  elif isinstance(error, commands.CommandInvokeError):
    print(f"{ctx.author}: {ctx.command} " + str(error.original))
    error = error.original
    if isinstance(error, discord.HTTPException):
      if error.code == 50035:
        await ctx.respond("Embed error")
        return
      else: # if error.code == 50015 or error.code == 50013 or error.code == 50001:
        try:
          await ctx.respond("I am missing some permissions!\nCheck your channel permissions or my role permissions\nPermissions needed: View channels, Manage webhooks, Create invite, Change nickname, Manage nicknames, Send messages, Send messages in threads, Attach files, Add reactions, Use external emoji, Manage messages, Read message history, Use application commands, Connect, Speak")
        except discord.HTTPException:
          try:
            if ctx.guild.me.nick is None or " (Missing Permissions)" not in ctx.guild.me.nick:
              await ctx.guild.me.edit(nick = ((ctx.guild.me.nick + " (Missing Permissions)") if ctx.guild.me.nick is not None else (ctx.guild.me.name + " (Missing Permissions)")))
          except:
            pass
        return
  else:
    # if ctx.author.id == 615037304616255491:
    #   traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    # else:
    print(f"{ctx.author}: {ctx.command} | {ctx.selected_options} | " + str(error))
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
  if not isinstance(error, commands.CommandNotFound) and not isinstance(error, commands.CommandOnCooldown) and bot.user.id == 863028787708559400:
    error.past_tb = "".join(traceback.format_stack())
    await bot.get_channel(909716483704238111).send(f"**Error from {ctx.author} ({ctx.author.id})**: Command `{ctx.command}` | `{ctx.selected_options}` | \nSTACK:\n{str(error.past_tb)[:2000]}{error}")

@tasks.loop(seconds=5)
async def maintimer():

  items = (await dll.find_one({"id": "market"}))['items']
  expired = [item for item in items if item['exp'] <= round(time.time())]
  for item in expired:
    getuser = bot.get_user(item['author'])
    if getuser is not None:
      if item['type'] == 'car':
        itemname = item['carinfo']['name']
        if item['carinfo']['golden'] == True:
          itemname = f"{star} Golden " + itemname
        embed = discord.Embed(title="Market listing expired", description=f"Your listing of a **{itemname}** for **<:cash:1329017495536930886> {item['listingprice']}** has expired! The car has been returned to your garage", color=color.gold())
      elif item['type'] == 'item':
        embed = discord.Embed(title="Market listing expired", description=f"Your listing of **{item['amount']} {item['name']}** for **<:cash:1329017495536930886> {item['listingprice']}** has expired! The item has been returned to your storage", color=color.gold())
      try:
        await getuser.send(embed=embed)
      except:
        pass
    user = await finduser(item['author'])
    if item['type'] == 'car':
      if len(user['garage']) == 0:
        carindex = 1
      else:
        carindex = user['garage'][-1]["index"]+1
      carinfo = {"index": carindex, 'id': item['carinfo']['id'], 'name': item['carinfo']['name'], 'price': item['carinfo']['price'], 'speed': item['carinfo']['speed'], 'tuned': item['carinfo']['tuned'], 'golden': item['carinfo']['golden'], 'locked': False, 'damage': item['carinfo']['damage']}
      await dll.update_one({"id": "market"}, {"$pull": {"items": {"listingid": int(item['listingid'])}}})
      await cll.update_one({"id": item['author']}, {"$push": {"garage": carinfo}})

      user['carlogs'].append(f"Car unsold returned: {item['carinfo']['name']}")
      await cll.update_one({"id": item['author']}, {"$set": {"carlogs": user['carlogs'][-20:]}})
    elif item['type'] == 'item':
      await dll.update_one({"id": "market"}, {"$pull": {"items": {"listingid": int(item['listingid'])}}})
      await cll.update_one({"id": item['author']}, {"$inc": {f"storage.{item['name']}": item['amount']}})

      user['cashlogs'].append(f"Item unsold returned: {item['amount']} {item['name']}")
      await cll.update_one({"id": item['author']}, {"$set": {"cashlogs": user['cashlogs'][-20:]}})

  cll.update_many({'timer.wishlist1': {"$lte": round(time.time())}}, {"$unset":{'timer.wishlist1': 1}})
  cll.update_many({'timer.wishlist2': {"$lte": round(time.time())}}, {"$unset":{'timer.wishlist2': 1}})
  cll.update_many({'timer.wishlist3': {"$lte": round(time.time())}}, {"$unset":{'timer.wishlist3': 1}})
  cll.update_many({'timer.wishlist4': {"$lte": round(time.time())}}, {"$unset":{'timer.wishlist4': 1}})
  cll.update_many({'timer.wishlist5': {"$lte": round(time.time())}}, {"$unset":{'timer.wishlist5': 1}})

  try:
    users = await cll.find({'timer.dbl': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.dbl': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      dblembed = discord.Embed(title="You can vote again!",description=f"You can vote again on **Discord Bot List**!\n\n[**Click here to vote on Discord Bot List**](https://discordbotlist.com/bots/ov/upvote)",color=color.green())
      dblembed.set_footer(text="You can get 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash by voting every 12 hours")
      try:
        await getuser.send(embed=dblembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.topgg': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.topgg': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      topggembed = discord.Embed(title="You can vote again!",description=f"You can vote again on **Top.gg**!\n\n[**Click here to vote on Top.gg**](https://top.gg/bot/863028787708559400/vote)",color=color.green())
      topggembed.set_footer(text="You can get 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash by voting every 12 hours")
      try:
        await getuser.send(embed=topggembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'topgg': 1}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$set": {'topgg': 0}, "$inc": {'storage.Safe': 1, 'cash': 500, 'storage.Average Car Key': 2}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      topggembed = discord.Embed(title="Thanks for voting!",description=f"Thanks for voting on **Top.gg**!\nYou claimed 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash",color=color.green())
      topggembed.set_footer(text="You can get 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash by voting every 12 hours")
      try:
        await getuser.send(embed=topggembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'dbl': 1}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$set": {'dbl': 0}, "$inc": {'storage.Safe': 1, 'cash': 500, 'storage.Average Car Key': 2}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      dblembed = discord.Embed(title="Thanks for voting!",description=f"Thanks for voting on **Discord Bot List**!\nYou claimed 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash",color=color.green())
      dblembed.set_footer(text="You can get 1 Safe, 2 Average Car Key <:average_car_key:1358506292725022761> and <:cash:1329017495536930886> 500 Cash by voting every 12 hours")
      try:
        await getuser.send(embed=dblembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.daily': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.daily': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      dailyembed = discord.Embed(title="Daily!",description="You can claim your daily again!",color=color.green())
      dailyembed.set_footer(text="Free cash!")
      try:
        await getuser.send(embed=dailyembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.weekly': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.weekly': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      weeklyembed = discord.Embed(title="Weekly!",description="You can claim your weekly again!",color=color.green())
      weeklyembed.set_footer(text="Free cash!")
      try:
        await getuser.send(embed=weeklyembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.blocked': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.blocked': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      blockedembed = discord.Embed(title="Unblocked",description="You are now unblocked!",color=color.green())
      blockedembed.set_footer(text="Don't break the rules again!")
      try:
        await getuser.send(embed=blockedembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.blocked': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.blocked': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      blockedembed = discord.Embed(title="Unblocked",description="You are now unblocked!",color=color.green())
      blockedembed.set_footer(text="Don't break the rules again!")
      try:
        await getuser.send(embed=blockedembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.donate': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({'id': {"$in": [user['id'] for user in users]}}, {"$set": {'donor': 0}, "$unset": {'timer.donate': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      if user['donor'] == 1:
        donaembed = discord.Embed(title="Royal status expired",description="Your Royal status has expired!",color=color.red())
      elif user['donor'] == 2:
        donaembed = discord.Embed(title="Royal+ status expired",description="Your Royal+ status has expired!",color=color.red())

      if user['title'] == "Royal" or user['title'] == "Royal+":
        await updateset(user['id'], 'title', '')
      if user['badge'] == "<:royal:1328385115503591526>" or user['badge'] == "<:royal_plus:1328385118347464804>":
        await updateset(user['id'], 'badge', '')
      donaembed.set_footer(text="Thanks for the support!")
      try:
        await getuser.send(embed=donaembed)
      except:
        pass
  except:
    pass

  cll.update_many({'timer.warns': {"$lte": round(time.time())}}, {"$inc": {'warns': -1}, "$unset":{'timer.warns': 1}})

  try:
    users = await cll.find({'timer.cashboost': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({'id': {"$in": [user['id'] for user in users]}}, {"$inc": {'stats.cha': -500}, "$unset": {'timer.cashboost': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      cashembed = discord.Embed(title="Time ended",description="Your business cash boost has ended!",color=color.red())
      cashembed.set_footer(text="no more Cash Boost")
      try:
        await getuser.send(embed=cashembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.cboost': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({'id': {"$in": [user['id'] for user in users]}}, {"$inc": {'stats.luk': -50}, "$unset": {'timer.cboost': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      cashembed = discord.Embed(title="Time ended",description="Your kidnapper chance boost has ended!",color=color.red())
      cashembed.set_footer(text="no more Chance Boost")
      try:
        await getuser.send(embed=cashembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.beer': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.beer': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      beerembed = discord.Embed(title="Sober",description="You are not drunk anymore!",color=color.red())
      beerembed.set_footer(text="no more HP Boost")
      try:
        await getuser.send(embed=beerembed)
      except:
        pass
  except:
    pass

  cll.update_many({'timer.cannabis': {"$lte": round(time.time())}}, {"$unset": {'timer.cannabis': 1}, "$set": {"drugs.cannabis": 0}})
  cll.update_many({'timer.ecstasy': {"$lte": round(time.time())}}, {"$unset": {'timer.ecstasy': 1}, "$set": {"drugs.ecstasy": 0}})
  cll.update_many({'timer.heroin': {"$lte": round(time.time())}}, {"$unset": {'timer.heroin': 1}, "$set": {"drugs.heroin": 0}})
  cll.update_many({'timer.methamphetamine': {"$lte": round(time.time())}}, {"$unset": {'timer.methamphetamine': 1}, "$set": {"drugs.methamphetamine": 0}})
  cll.update_many({'timer.xanax': {"$lte": round(time.time())}}, {"$unset": {'timer.xanax': 1}, "$set": {"drugs.xanax": 0}})
  
  try:
    users = await cll.find({'timer.fuel': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.fuel': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      fuelembed = discord.Embed(title="Cool",description="You finished your fuel!",color=color.green())
      fuelembed.set_footer(text="no more car speed Boost")
      try:
        await getuser.send(embed=fuelembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.shield': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$unset": {'timer.shield': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      shieldembed = discord.Embed(title="Your immunity is gone!",description="You will no longer protected when you die",color=color.red())
      shieldembed.set_footer(text="Don't die!")
      try:
        await getuser.send(embed=shieldembed)
      except:
        pass
  except:
    pass
  users = await dcll.find({'gifts.quantity': {"$gt": 0}}).to_list(length=None)
  dcll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$set": {'gifts': {}}})
  try:
    for user in users:
      usergifts = user['gifts']
      itemname = usergifts['itemname']
      quantity = int(usergifts['quantity'])
      gifterid = int(usergifts['gifterid'])
      gifter = await cll.find_one({'id': gifterid})
      giftername = gifter['name']

      getuser = bot.get_user(int(user['id']))
      userid = user['id']
      try:
        await bot.get_channel(1313868780455333949).send(f"Donation received from {giftername} ({gifterid})\n{quantity} {itemname}: **${round(quantity*lists.donation_price[itemname], 2)}**\n{'(Not gifting anyone)' if userid == gifterid else f'Gifting {getuser}' if getuser is not None else f'Gifting user {userid}'}")
      except Exception as e:
        print(e)
        pass

      if str(user['id']) == str(gifterid):
        giftembed = discord.Embed(title="Thanks for purchasing!",description=f"You received {quantity} {itemname}! Type `/claim` to claim it!",color=color.green())
        try:
          await getuser.send(embed=giftembed)
        except:
          pass
      else:
        giftuser = bot.get_user(int(gifterid))
        gifterembed = discord.Embed(title="Thanks for purchasing!",description=f"You purchased {quantity} {itemname} and gifted {user['name']}! Ask them to type `/claim` to claim it!",color=color.green())

        try:
          if giftuser is not None:
            await giftuser.send(embed=gifterembed)
        except:
          pass

        giftembed = discord.Embed(title="You've received a gift!",description=f"{giftername} purchased and gifted you {quantity} {itemname}! Type `/claim` to claim it!",color=color.green())
        giftembed.set_footer(text="wow free gift!")
        getuser = bot.get_user(int(user['id']))
        try:
          await getuser.send(embed=giftembed)
        except:
          pass
  except:
    pass

  try:
    users = await cll.find({'timer.hosp': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$set": {'inhosp': False}, "$unset": {'timer.hosp': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      recoembed = discord.Embed(title="Recovered",description="You are out of the Hospital!",color=color.green())
      recoembed.set_footer(text="Don't die again next time!")
      try:
        await getuser.send(embed=recoembed)
      except:
        pass
  except:
    pass
  try:
    users = await cll.find({'timer.jail': {"$lte": round(time.time())}}).to_list(length=None)
    cll.update_many({"id": {"$in": [user['id'] for user in users]}}, {"$set": {'injail': False}, "$unset": {'timer.jail': 1}})
    for user in users:
      getuser = bot.get_user(user['id'])
      if getuser is None: continue
      releembed = discord.Embed(title="Released",description="You are out of the Jail!",color=color.green())
      releembed.set_footer(text="Bribe the guards next time!")
      try:
        await getuser.send(embed=releembed)
      except:
        pass
  except:
    pass

@tasks.loop(minutes=10)
async def drugprices():
  cities = bm.find({})
  cities_list = await cities.to_list(None)
  for city in cities_list:
    drugs = city['drugs']
    cityname = city['city']
    for drug in drugs:
      drugprice = drugs[drug]
      await bm.update_one({"city": cityname}, {"$set":{f'drugs.{drug}': round(drugprice)}})
      randomchance = round(random.random(),4)
      randomprice = round(random.uniform(10,100))
      if randomchance <= (drugprice / lists.item_prices[drug] / 2):
        if drugprice - round(randomprice) < 50:
          await bm.update_one({"city": cityname}, {"$set": {f'drugs.{drug}': 50}})
        else:
          await bm.update_one({"city": cityname}, {"$inc": {f'drugs.{drug}': -round(randomprice)}})
      else:
        await bm.update_one({"city": cityname}, {"$inc": {f'drugs.{drug}': round(randomprice)}})
  # Cannabis
  # Ecstasy
  # Heroin
  # Methamphetamine
  # Xanax

bot.drugprices = drugprices

@tasks.loop(minutes=10)
async def businesstimer():
  cll.update_many({'business': {"$gt": 0}}, [{"$set": {"cash": {"$add": ["$cash", "$business"]}}}])

@tasks.loop(seconds=2)
async def main2timer():
  try:
    gcll.update_one({"id": 863025676213944340}, {"$inc": {"totaluptime": 2}})
    gcll.update_one({"id": 863025676213944340, "maintime": {"$lte": round(time.time())}},{"$set": {"maintime": "Almost done"}})
  except:
    pass
  cll.update_many({'timer.larceny': {"$lte": round(time.time())}}, {"$unset": {'timer.larceny': 1}})
  cll.update_many({'timer.travel': {"$lte": round(time.time())}}, {"$unset": {'timer.travel': 1}})
  cll.update_many({'timer.train': {"$lte": round(time.time())}}, {"$unset": {'timer.train': 1}})

  try:
    cll.update_many({"blocked": True, "timer.blockedtimeout": {"$exists": False}},{"$set": {"timer.blockedtimeout": round(time.time())+120}})
  except:
    pass
  try:
    cll.update_many({"racing": True, "timer.racingtimeout": {"$exists": False}},{"$set": {"timer.racingtimeout": round(time.time())+120}})
  except:
    pass
  try:
    cll.update_many({"timer.blockedtimeout": {"$exists": True}, "blocked": False},{"$unset": {"timer.blockedtimeout": 1}})
  except:
    pass
  try:
    cll.update_many({"timer.blockedtimeout": {"$lte": round(time.time())}}, {"$set": {"blocked": False}})
  except:
    pass
  try:
    cll.update_many({"timer.racingtimeout": {"$exists": True}, "racing": False},{"$unset": {"timer.racingtimeout": 1}})
  except:
    pass
  try:
    cll.update_many({"timer.racingtimeout": {"$lte": round(time.time())}}, {"$set": {"racing": False}})
  except:
    pass

@tasks.loop(seconds=60)
async def donatorlistloop():
  try:
    donatorlist = [member['id'] for member in await cll.find({"donor": {"$gt": 0}}).to_list(length=None)]
  except:
    pass

  leaked_objects = [obj for obj in gc.get_objects() if isinstance(obj, discord.ui.View)]
  print(f"Leaked Views: {len(leaked_objects)}")
  # await cll.update_many({}, [{"$set": {"energy": {"$cond": {"if": {"$lt": ["$energy", "$energyc"]}, "then": {"$add": ["$energy", "$epm"]}, "else": "$energy"}}}}])

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
        print(f"Loaded {extension[5:].capitalize()} extension")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(get_server_info())

maintimer.start()
main2timer.start()
businesstimer.start()
drugprices.start()
donatorlistloop.start()
bot.run(dakey)
