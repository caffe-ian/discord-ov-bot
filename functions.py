import os
import motor.motor_asyncio
import random
import lists
import asyncio
from PIL import Image, ImageDraw
from io import BytesIO
# from pymongo import MongoClient
import time
import re
import interclass
import discord
from bs4 import BeautifulSoup
import requests, json, lxml
import simulator

db_url = os.getenv("MONGO")

# client = MongoClient(db_url)
# pdb = client['maindb']

cluster = motor.motor_asyncio.AsyncIOMotorClient(db_url)
db = cluster['maindb']
cll = db['userdata']
gcll = db['guilddata']

star = u"\u2B50"
color = discord.Colour
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/91.0.864.59"
}

async def new_title(userdonatedata, userdata):
  achievements = []

  # Donator titles
  if userdonatedata is not None:
    if round((userdonatedata['totaldonated']+(userdonatedata['totalitembought']/100))) >= 1000 and "<:kingpin1:1354900979966935373><:kingpin2:1354900974992621648><:kingpin3:1354900969216933909><:kingpin4:1354900957686661234>" not in userdata['titles']:
      achievements += ["<:kingpin1:1354900979966935373><:kingpin2:1354900974992621648><:kingpin3:1354900969216933909><:kingpin4:1354900957686661234>"]
    # achievements += ([lists.title_donator_dispatcher[req] for req in list(lists.title_donator_dispatcher) if userdata['donor'] != 0 and userdata['donor'] >= req and lists.title_donator_dispatcher[req] not in userdata['titles']])

  # Job titles
  achievements += ([lists.title_job_dispatcher1[userdata['job']]] if userdata['job'] != "" and lists.title_job_dispatcher1[userdata['job']] not in userdata['titles'] else []) 
  
  # Level titles
  achievements += ([lists.title_level_dispatcher[level] for level in lists.title_level_dispatcher if userdata['lvl'] >= level and lists.title_level_dispatcher[level] not in userdata['titles']])

  # Cash titles
  achievements += ([lists.title_cash_dispatcher[cash] for cash in lists.title_cash_dispatcher if (userdata['cash']+userdata['stash']) >= cash and lists.title_cash_dispatcher[cash] not in userdata['titles']])

  # Job amount titles
  achievements += ([lists.title_job_dispatcher[job] for job in lists.title_job_dispatcher if sum([int(i) for i in format(userdata['jobcount'], 'b')[::-1]]) >= job and lists.title_job_dispatcher[job] not in userdata['titles']])

  # Race skill titles
  achievements += ([lists.title_race_dispatcher[skill] for skill in lists.title_race_dispatcher if sum([userdata['stats']['acc'], userdata['stats']['dri'], userdata['stats']['han'], userdata['stats']['bra']]) >= skill and lists.title_race_dispatcher[skill] not in userdata['titles']])

  # Car approval titles
  achievements += ([lists.title_approval_dispatcher[amount] for amount in lists.title_approval_dispatcher if userdata['approve'] >= amount and lists.title_approval_dispatcher[amount] not in userdata['titles']])
  
  if userdata['id'] == (await cll.find().sort("exp", -1).limit(1).to_list(length=None))[0]['id']:
    if userdata['id'] == sorted(await cll.find().to_list(length=None), key=lambda x: x['cash'] + x['stash'], reverse=True)[0]['id']:
      if "_The Godfather_" not in userdata['titles']:
        achievements += ["_The Godfather_"]

  return achievements

def new_badge(userdonatedata, userdata):
  achievements = []

  if userdonatedata is None:
    return []

  # Donator titles
  achievements += ([lists.badge_donator_dispatcher[req] for req in list(lists.badge_donator_dispatcher) if round((userdonatedata['totaldonated']+(userdonatedata['totalitembought']/100))) >= req and lists.badge_donator_dispatcher[req] not in userdata['badges']])

  return achievements

async def getbadge(self, userdata):
  achievements = []

  lblist = [member['id'] for member in sorted(await self.bot.cll.find().to_list(length=None), key=lambda x: x['cash'] + x['stash'], reverse=True) if member['cash'] + member['stash'] > 10][:3]
  if userdata['id'] == lblist[0]:
    achievements += ["<:wealth_trophy_gold:1354106868145852436>"]
  elif userdata['id'] == lblist[1]:
    achievements += ["<:wealth_trophy_silver:1354106870432006265>"]
  elif userdata['id'] == lblist[2]:
    achievements += ["<:wealth_trophy_bronze:1354106873594515486>"]

  lblist = [member['id'] for member in sorted(await self.bot.cll.find().to_list(length=None), key=lambda x: round(x['lvl'] + (int(str(round(x['exp']))[-2:]) / 100), 2), reverse=True) if round(member['lvl'] + (int(str(round(member['exp']))[-2:]) / 100), 2) >= 1][:3]
  if userdata['id'] == lblist[0]:
    achievements += ["<:level_trophy_gold:1354106878350594048>"]
  elif userdata['id'] == lblist[1]:
    achievements += ["<:level_trophy_silver:1354106881206911058>"]
  elif userdata['id'] == lblist[2]:
    achievements += ["<:level_trophy_bronze:1354106887859081328>"]

  return achievements

async def die(ctx, user, where, reason):
      userp = await finduser(user.id)
      try:
        userptimer = userp['timer']
        userptimer['shield']
        dieembed = discord.Embed(title = f"{gettitle(userp)}{user} died {where}!", description = f"{reason}\n**But you have immunity so you are fine!**",color = color.red())
        await ctx.respond(embed=dieembed)
        return
      except:
        pass
      usercash = userp['cash']
      cashlost = round(round(round(random.uniform(5, 10), 1) / 10, 2) * usercash)
      randomtime = round(random.randint(300, 900)*((userp['lvl']+100)/100))
      await updateset(user.id, 'timer.hosp', round(time.time())+randomtime)
      await updateset(user.id, 'inhosp', True)
      await cll.update_one({"id": user.id}, {"$set": {"drugs.cannabis": 0, "drugs.ecstasy": 0, "drugs.heroin": 0, "drugs.methamphetamine": 0, "drugs.xanax": 0}, "$unset": {"timer.cannabis": 1, "timer.ecstasy": 1, "timer.heroin": 1, "timer.methamphetamine": 1, "timer.xanax": 1}})

      view = interclass.Respect(ctx)

      dieembed = discord.Embed(title = f"{gettitle(userp)}{user} died {where}!", description = f"{reason}\n\nYou lost <:cash:1329017495536930886> {aa(cashlost)}\nYou are now in hospital for `{ab(randomtime)}`", color = color.red())
      if userp['ins'] != 0:
        dispatcher = {-1: 0, 0: 20, 1: 50, 2: 70, 3: 90, 4: 100, 5: 101, 6: 101}
        if userp['ins'] == 6:
          cashback = round(cashlost * (round(dispatcher[userp['ins']-2]/100, 2)))
          await updateinc(user.id, 'cash', round(cashback-cashlost))
          await updateinc(user.id, 'ins', -1)
          dieembed.add_field(name="You had an insurance!", value=f"Your insurance is only willing to pay 100% of your losses and you regained <:cash:1329017495536930886> {aa(cashback)} cash")
        else:
          cashback = round(cashlost * (round(dispatcher[userp['ins']-1]/100, 2)))
          await updateinc(user.id, 'cash', round(cashback-cashlost))
          await updateinc(user.id, 'ins', -1)
          dieembed.add_field(name="You had an insurance!", value=f"You had a {dispatcher[userp['ins']-1]}% cover from insurance and regained <:cash:1329017495536930886> {aa(cashback)} cash")
      else:
        await updateinc(user.id, 'cash', -cashlost)
      dieembed.set_footer(text = "F to pay respect")

      await ctx.respond("ㅤ",embed=dieembed,view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value == None:
        await ctx.respond(f"No one paid respect to {gettitle(userp)}{user.mention}, how sad")
        return
      elif view.value == True:
        gained = round(random.uniform(3, 6))
        await updateinc(view.user.id, 'cash', gained)
        viewuser = await finduser(view.user.id)
        if view.user == user:
          await ctx.respond(f"{viewuser['title']}{view.user.mention} paid respect to themselves and gained <:cash:1329017495536930886> {gained}, lol")
        else:
          await updateinc(view.user.id, 'rep', 1)
          await ctx.respond(f"{viewuser['title']}{view.user.mention} paid respect to {gettitle(userp)}{user.mention} and gained <:cash:1329017495536930886> {gained} along with 1 reputation point")

def getrank(car):
  if car in lists.lowcar:
    return "Low"
  elif car in lists.averagecar:
    return "Average"
  elif car in lists.highcar:
    return "High"
  elif car in lists.exoticcar:
    return "Exotic"
  elif car in lists.classiccar:
    return "Classic"
  elif car in lists.exclusivecar:
    return "Exclusive"
  else:
    return "Unknown"

def rankconv(query):
  dispatcher = {"Unknown": "Unknown", "Low": "Low", "Average": "Average", "High": "High", "Exotic": "Exotic", "Classic": "<:classic1:1306561616795402270><:classic2:1306561614748844133><:classic3:1306561743228502027><:classic4:1306562702818414634>", "Exclusive": "<a:exclusive1:1307247993161781409><a:exclusive2:1307247988808351774><a:exclusive3:1307247985754902540><a:exclusive4:1307248122082099200>"}
  try:
    return dispatcher[query]
  except:
    print(f"Rank conversion error: {query}")
    return query

async def carspecialty(self, query):
  if str(query).isdigit():
    user = await self.bot.fetch_user(int(query))
    if user is not None:
      return f"Suggested by {user}"
    else:
      return "Player suggestion"

  return query

async def jail(ctx, user, reason=None):
  if reason is None:
    reason = "Your heat bar is full and the cops threw you into the jail!"
  userdata = await finduser(user.id)
  # if userdata['heat'] < 1000:
  #   return
  rtime = round(random.randint(180, 360)*((userdata['lvl']+100)/100))
  embed = discord.Embed(title="You have been caught!", description=f"**Reason:** {reason}\nYou are now in jail for {ab(rtime)}", color=color.red())
  
  await cll.update_one({"id": ctx.author.id}, {"$set": {"injail": True, "timer.jail": round(time.time())+rtime, "heat": 0}})

  if "Bribe" in userdata['storage'] and userdata['storage']['Bribe'] > 0:
    view = interclass.Jail(ctx)
    msg = view.message = await ctx.followup.send(embed=embed, view=view)
  else:
    await ctx.respond(embed=embed)
    return

  await view.wait()

  if view.value is None:
    return
  elif view.value:
    embed = discord.Embed(title="You are now out of the jail!", description=f"You bribed the guards", color=color.green())
    await msg.edit(embed=embed, view=None)
    if userdata['storage']['Bribe'] == 1:
      await cll.update_one({"id": ctx.author.id}, {"$set": {"injail": False}, "$unset": {"timer.jail": 1, "storage.Bribe": 1}})
    else:
      await cll.update_one({"id": ctx.author.id}, {"$set": {"injail": False}, "$unset": {"timer.jail": 1}, "$inc": {"storage.Bribe": -1}})
    return

def gettitle(user):
  t = ""
  if user['badge'] != "":
    t += f"{user['badge']} "
  if user['title'] != "":
    t += f"｢{user['title']}｣ "
  return t

async def getluck(user):
  luck = user['stats']['luk']*(1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)
  luck = round(luck + (luck * (user['drugs']['cannabis']/100)))
  if "Lucky Clover" in user['storage']:
    luck = round(luck + (user['storage']['Lucky Clover']/100 * luck))
  server = await gcll.find_one({"id": 863025676213944340})
  events = [server['events'][t] for t in server['events'] if int(t) > round(time.time())]
  if any(["st. patrick's day" in event.lower() for event in events]):
    luck *= 1.5

  return luck/1000

def getcha(user, ctx):
  char = user['stats']['cha']*(2 if user['donor'] == 2 else 1.5 if user['donor'] == 1 else 1)
  char = round(char + (char * (user['drugs']['ecstasy']/100*5)))

  if any([user['location'] == 'Corsia' and ctx.channel.id == 876437561072054333, user['location'] == 'Lucoro' and ctx.channel.id == 1372216579038904400, user['location'] == 'Donvia' and ctx.channel.id == 1372216628347146260, user['location'] == 'Zelmor' and ctx.channel.id == 1372216677353263184, user['location'] == 'Arkovich' and ctx.channel.id == 1372216719354888193]):
    char *= 1.05

  return char/1000

def getoverdose(user):
  overdose = 0
  for _ in range(user['drugs']['cannabis']):
    overdose += random.randint(1, 2)
  for _ in range(user['drugs']['ecstasy']):
    overdose += random.randint(1, 3)
  for _ in range(user['drugs']['heroin']):
    overdose += random.randint(1, 3)
  for _ in range(user['drugs']['methamphetamine']):
    overdose += random.randint(1, 4)
  for _ in range(user['drugs']['xanax']):
    overdose += random.randint(1, 5)

  if overdose > 10:
    return True
  return False

async def heroin(ctx, amount = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userheroin = userstorage['Heroin']
  except:
    await ctx.respond("You don't have any Heroin in your storage")
    return
  if userheroin < amount:
    await ctx.respond("You don't have enough Heroin in your storage!")
    return
  if userheroin == amount:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Heroin": 1}})
  else:
    await updateinc(ctx.author.id, "storage.Heroin", -amount)
  for _ in range(amount):
    user['drugs']['heroin'] += 1
    if getoverdose(user):
      await die(ctx, ctx.author, "while consuming a heroin!", "You overdosed by accident")
      return
  await cll.update_one({"id": ctx.author.id},{"$inc":{'drugs.heroin': amount}, "$set": {"timer.heroin": round(time.time()) + 3600} })
  await ctx.respond(f"You consumed a heroin and increased your HP by {5*amount}% for 1 hour! (Stack: {(user['drugs']['heroin']) * 5}% HP Boost)")

async def cannabis(ctx, amount = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usercannabis = userstorage['Cannabis']
  except:
    await ctx.respond("You don't have any Cannabis in your storage")
    return
  if usercannabis < amount:
    await ctx.respond("You don't have enough Cannabis in your storage!")
    return
  if usercannabis == amount:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Cannabis": 1}})
  else:
    await updateinc(ctx.author.id, "storage.Cannabis", -amount)
  for _ in range(amount):
    user['drugs']['cannabis'] += 1
    if getoverdose(user):
      await die(ctx, ctx.author, "while consuming a cannabis!", "You overdosed by accident")
      return
  await cll.update_one({"id": ctx.author.id},{"$inc":{'drugs.cannabis': amount}, "$set": {"timer.cannabis": round(time.time()) + 3600} })
  await ctx.respond(f"You consumed a cannabis and increased your <:luck:940955425308823582> by {amount}% for 1 hour! (Stack: {user['drugs']['cannabis']}% <:luck:940955425308823582> Boost)")

async def ecstasy(ctx, amount = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userecstasy = userstorage['Ecstasy']
  except:
    await ctx.respond("You don't have any Ecstasy in your storage")
    return
  if userecstasy < amount:
    await ctx.respond("You don't have enough Ecstasy in your storage!")
    return
  if userecstasy == amount:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Ecstasy": 1}})
  else:
    await updateinc(ctx.author.id, "storage.Ecstasy", -amount)
  for _ in range(amount):
    user['drugs']['ecstasy'] += 1
    if getoverdose(user):
      await die(ctx, ctx.author, "while consuming a ecstasy!", "You overdosed by accident")
      return
  await cll.update_one({"id": ctx.author.id},{"$inc":{'drugs.ecstasy': amount}, "$set": {"timer.ecstasy": round(time.time()) + 3600} })
  await ctx.respond(f"You consumed a ecstasy and increased your <:charisma:940955424910356491> by {5*amount}% and Random event chance by {10*amount}% for 1 hour! (Stack: {(user['drugs']['ecstasy']) * 5}% <:charisma:940955424910356491> Boost & {(user['drugs']['ecstasy']+amount) * 10}% Random event chance)")

async def methamphetamine(ctx, amount = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usermeth = userstorage['Methamphetamine']
  except:
    await ctx.respond("You don't have any Methamphetamine in your storage")
    return
  if usermeth < amount:
    await ctx.respond("You don't have enough Methamphetamine in your storage!")
    return
  if usermeth == amount:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Methamphetamine": 1}})
  else:
    await updateinc(ctx.author.id, "storage.Methamphetamine", -amount)
  for _ in range(amount):
    user['drugs']['methamphetamine'] += 1
    if getoverdose(user):
      await die(ctx, ctx.author, "while consuming a methamphetamine!", "You overdosed by accident")
      return
  await cll.update_one({"id": ctx.author.id},{"$inc":{'drugs.methamphetamine': amount}, "$set": {"timer.methamphetamine": round(time.time()) + 3600} })
  await ctx.respond(f"You consumed a methamphetamine and increased your racing speed by {5*amount}% for 1 hour! (Stack: {(user['drugs']['methamphetamine']) * 5}% Racing Speed Boost)")

async def xanax(ctx, amount = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userxanax = userstorage['Xanax']
  except:
    await ctx.respond("You don't have any Xanax in your storage")
    return
  if userxanax < amount:
    await ctx.respond("You don't have enough Xanax in your storage!")
    return
  if userxanax == amount:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Xanax": 1}})
  else:
    await updateinc(ctx.author.id, "storage.Xanax", -amount)
  for _ in range(amount):
    user['drugs']['xanax'] += 1
    if getoverdose(user):
      await die(ctx, ctx.author, "while consuming a xanax!", "You overdosed by accident")
      return
  await cll.update_one({"id": ctx.author.id},{"$inc":{'drugs.xanax': amount}, "$set": {"timer.xanax": round(time.time()) + 3600} })
  await ctx.respond(f"You consumed a xanax and increased your strength by {50*amount}% for 1 hour! (Stack: {(user['drugs']['xanax']) * 50}% STR Boost)")

class Atkboost:
  def __init__(self, stats, user):
    self.stats = stats
    self.user = user

  def santa_hat(self):
    self.stats["userstr"] = round(self.stats["userstr"] * 1.05, 2)

  def heart_glasses(self):
    self.stats['userhealth'] = round(self.stats['userhealth'] + 20)

  def active(self, user):
    try:
      if user['timer']['beer'] > round(time.time()):
        self.stats["userhealth"] += 20
    except:
      pass
    self.stats["userhealth"] = round(self.stats['userhealth'] + (self.stats['userhealth'] * (user['drugs']['heroin']/100*5)))
    self.stats['userstr'] = round(self.stats['userstr'] + (self.stats['userstr']*(user['drugs']['xanax']*0.5)), 2)

def atkboost(user):
  userstats = user['stats']
  stats = {
    "userhealth": 100 + ((user['lvl']-1) * 5),
    "userweapondmg": lists.weapon_boost[user['equipments']['weapon']],
    "userstr": round(userstats['str'],2),
    "userdef": round(userstats['def'],2),
    "userspd": round(userstats['spd'],2),
    "userdex": round(userstats['dex'],2),
  }
  stats = Atkboost(stats, user)
  for equipment in user['equipments'].values():
    try:
      equipment = equipment.lower().replace(" ", "_")
      exec("stats." + equipment + "()")
    except:
      pass
  stats.stats["userweapondmg"] = round(stats.stats["userweapondmg"] * ((100 + ((user['lvl']-1) * 5))/100), 2)
  stats.active(user)
  return [stats.stats[stat] for stat in stats.stats]

def attack_image(userhealth, user2health, user, user2, img):
  userhealth = 0 if userhealth < 0 else round(userhealth)
  user2health = 0 if user2health < 0 else round(user2health)
  userchar = charimg(user, False).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  user2char = charimg(user2, False)
  bg = Image.open(rf"images/attack_bg_{img}.png").convert('RGBA')

  healthbar1 = Image.new("RGBA", (212, 21))
  healthbar2 = healthbar1.copy()

  pen = ImageDraw.Draw(healthbar1)
  pen.rounded_rectangle(((0, 0), (200, 20)), fill=(255, 204, 203), outline="black", width=2, radius=9)
  pen.rounded_rectangle(((0, 0), ((round(userhealth/(100 + ((user['lvl']-1) * 5))*100*2)) if userhealth != 0 else 0, 20)), fill=(220, 0, 0), outline="black", width=2, radius=9)

  pen = ImageDraw.Draw(healthbar2)
  pen.rounded_rectangle(((0, 0), (200, 20)), fill=(255, 204, 203), outline="black", width=2, radius=9)
  pen.rounded_rectangle(((0, 0), ((round(user2health/(100 + ((user2['lvl']-1) * 5))*100*2)) if user2health != 0 else 0, 20)), fill=(220, 0, 0), outline="black", width=2, radius=9)

  bg.paste(userchar, (43, 126), userchar)
  bg.paste(healthbar1, (20, 100), healthbar1)
  bg.paste(user2char, (445, 126), user2char)
  bg.paste(healthbar2, (415, 100), healthbar2)

  healthbar1.close()
  healthbar2.close()

  bg = bg.resize((480, 270), Image.Resampling.LANCZOS)

  bg = bg.convert("P")

  byte = BytesIO()

  bg.save(byte, format="png")
  bg.close()
  userchar.close()
  user2char.close()
  byte.seek(0)

  return byte

def not_max_level(user):
  if (user['property'] == 0 and user['lvl'] < 10) or (user['property'] == 10 and user['lvl'] < 20) or (user['property'] == 15 and user['lvl'] < 30) or (user['property'] == 40 and user['lvl'] < 40) or (user['property'] == 75 and user['lvl'] < 50) or (user['property'] == 100 and user['lvl'] < 60) or (user['property'] == 150 and user['lvl'] < 70) or (user['property'] == 250 and user['lvl'] < 80) or (user['property'] == 400 and user['lvl'] < 90) or (user['property'] == 750 and user['lvl'] < 100) or (user['property'] == 1000 and user['lvl'] < 110) or (user['property'] == 1500 and user['lvl'] < 120) or (user['property'] == 3000 and user['lvl'] < 130) or (user['property'] == 7500 and user['lvl'] < 140) or (user['property'] == 15000 and user['lvl'] < 150) or (user['property'] == 30000 and user['lvl'] < 160):
    return True
  return False

def getdrive(user, mode = "car"):
  car = [x for x in user['garage'] if x['id'] == int(user['drive'])][0]
  if car is None: raise
  if mode == "name":
    carname = car['name']
    if car['golden'] is True:
      carname = "\u2B50 Golden " + carname
    if car['locked'] is True:
      carname += " \U0001f512"
    return carname
  elif mode == "rawname":
    return car['name']
  elif mode == "id":
    return car["index"]
  else:
    return car

def randomid():
  # "".join([i+str(random.randint(0,9)) for i in str(round(time.time()))])[10:]
  return int("".join([i + str(random.randint(0, 9)) for i in (str(random.randint(1,9)) + str(time.time()*1000).split(".")[-1].ljust(4, "0"))]))

def charimg(userdata, byte=True, equipments=None):
  if equipments is None:
    userequipments = [x for x in list(userdata['equipments'].values()) if x != ""]
  else:
    userequipments = [x for x in list(equipments.values()) if x != ""]
  if byte is False and "background" in userequipments[0].lower():
    userequipments.pop(0)

  img = Image.open(rf"images/{userequipments[0].lower().replace(' ', '_')}.png").convert('RGBA')
  img = img.resize((152, 216), Image.Resampling.LANCZOS)
  userequipments.pop(0)

  for equipment in userequipments:
      img2 = Image.open(rf"images/{equipment.lower().replace(' ', '_')}.png").convert('RGBA')
      img2 = img2.resize((152, 216), Image.Resampling.LANCZOS)
      img.paste(img2, (0, 0), img2)
      img2.close()

  if byte:
    byte = BytesIO()

    img.save(byte, format="png")
    img.close()
    byte.seek(0)

    return byte
  else:
    return img

def goldfilter(iurl):
  TINT_COLOR = (255, 215, 0)
  TRANSPARENCY = .3
  OPACITY = int(255 * TRANSPARENCY)

  url = iurl

  response = requests.get(url)
  img = Image.open(BytesIO(response.content))
  img = img.convert("RGBA")

  sizex, sizey = img.size

  overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
  draw = ImageDraw.Draw(overlay)
  draw.rectangle((0, 0, sizex, sizey), fill=TINT_COLOR+(OPACITY,))

  img = Image.alpha_composite(img, overlay)
  img = img.convert("RGB")

  byte = BytesIO()

  img.save(byte,format="jpeg")
  img.close()
  overlay.close()
  byte.seek(0)
  img = byte.read()
  byte = BytesIO(img)

  return byte

async def finduser(id):
  return await cll.find_one({"id": id})

async def updateset(id, key: str, value):
  return await cll.update_one({"id": id}, {"$set": {key: value}})

async def updateinc(id, key: str, value):
  return await cll.update_one({"id": id}, {"$inc": {key: value}})

async def insertdict(dic):
  return await cll.insert_one(dic)

def ad(str):
  seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
  seconds = 0
  try:
    for s in str.split(" "):
      seconds += int(s[:-1]) * seconds_per_unit[s[-1].lower()]
    return seconds
  except:
    raise

def ac(n):
    n = str(n)
    num = 0
    conv = {'K':1000, 'M':1000000, 'B':1000000000, 'T':1000000000000}
    if n.isdigit():
        num = int(n)
    else:
        if len(n) > 1:
            num = float(n[:-1]) * conv.get(n[-1].upper(), 1)
    return int(num)

def aa(n):
  return str("{:,}".format(int(n)))

def ab(seconds):
  if seconds == None or seconds == "":
    return ""
  if seconds >= 60:
    minutes = seconds // 60
    seconds -= (minutes*60)
    if minutes >= 60:
      hours = minutes // 60
      minutes -= (hours*60)
      if hours >= 24:
        days = hours // 24
        hours -= (days*24)
        return f"{round(days)}d {round(hours)}h {round(minutes)}m {round(seconds, 1)}s"
      else:
        return f"{round(hours)}h {round(minutes)}m {round(seconds, 1)}s"
    else:
      return f"{round(minutes)}m {round(seconds, 1)}s"
  else:
    return str(round(seconds, 1))+"s"
  
async def blocked(userid):
  user = await cll.find_one({"id": userid})
  if user is None:
    return False
  try:
    user['timer']['blocked']
    return False
  except:
    if user['banned'] == True or user['inhosp'] == True or user['injail'] == True or user['blocked'] == True:
      return False
  return True

async def userbanned(userid):
  try:
    user = await cll.find_one({"id": userid})
  except:
    return False
  userbanned = user['banned']
  if userbanned == True:
    return True
  return False

def dboost(dtier):
  if dtier == 0:
    return 0
  elif dtier == 1:
    return 0.5
  elif dtier == 2:
    return 1

def checksame(lists):
    if len(lists) == len(set(lists)):
        return False
    else:
        return True

def randomcar(userdata, exclusiveamount):
  wishlist = [car for car in list(userdata['wishlist'].values()) if car != ""]
  exclusives = [car for car in list(exclusiveamount) if car in list(exclusiveamount) and exclusiveamount[car] > 0]
  # 38.85% 60% 1.5% 0.3% 0.05%
  randomchance = random.random()
  # Average car 60%
  averchance = 0.6185 + (0.3*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # High car 1.5%
  highchance = 0.0185 + (0.0185*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # Exotic car 0.3%
  exochance = 0.0035 + (0.0035*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # Exclusive car 0.05%
  excchance = 0.0005 + (0.0005*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  if exclusives == []:
    if randomchance <= exochance:

      if random.randint(1, 5) == 1:
        if len([car for car in wishlist if car in lists.classiccar]) > 0:
          if random.randint(1,3) == 1:
            return random.choice([car for car in wishlist if car in lists.classiccar])
        return random.choice(lists.classiccar)

      if len([car for car in wishlist if car in lists.exoticcar]) > 0:
        if random.randint(1,3) == 1:
          return random.choice([car for car in wishlist if car in lists.exoticcar])
      return random.choice(lists.exoticcar)

    elif exochance < randomchance <= highchance:

      if len([car for car in wishlist if car in lists.highcar]) > 0:
        if random.random() <= 0.2*len([car for car in wishlist if car in lists.highcar]):
          return random.choice([car for car in wishlist if car in lists.highcar])
      return random.choice(lists.highcar)

    elif highchance < randomchance <= averchance:
      if len([car for car in wishlist if car in lists.averagecar]) > 0:
        if random.random() <= 0.05*len([car for car in wishlist if car in lists.averagecar]):
          return random.choice([car for car in wishlist if car in lists.averagecar])
      return random.choice(lists.averagecar)
    elif averchance < randomchance:
      if len([car for car in wishlist if car in lists.lowcar]) > 0:
        if random.random() <= 0.05*len([car for car in wishlist if car in lists.lowcar]):
          return random.choice([car for car in wishlist if car in lists.lowcar])
      return random.choice(lists.lowcar)
  else:
    if randomchance <= excchance:

      if len([car for car in wishlist if car in exclusives]) > 0:
        if random.randint(1,2) == 1:
          return random.choice([car for car in wishlist if car in exclusives])
      return random.choice(exclusives)

    elif excchance < randomchance <= exochance:

      if random.randint(1, 5) == 1:
        if len([car for car in wishlist if car in lists.classiccar]) > 0:
          if random.randint(1,3) == 1:
            return random.choice([car for car in wishlist if car in lists.classiccar])
        return random.choice(lists.classiccar)

      if len([car for car in wishlist if car in lists.exoticcar]) > 0:
        if random.randint(1,3) == 1:
          return random.choice([car for car in wishlist if car in lists.exoticcar])
      return random.choice(lists.exoticcar)

    elif exochance < randomchance <= highchance:
      if len([car for car in wishlist if car in lists.highcar]) > 0:
        if random.random() <= 0.2*len([car for car in wishlist if car in lists.lowcar]):
          return random.choice([car for car in wishlist if car in lists.highcar])
      return random.choice(lists.highcar)
    elif highchance < randomchance <= averchance:
      if len([car for car in wishlist if car in lists.averagecar]) > 0:
        if random.random() <= 0.05*len([car for car in wishlist if car in lists.averagecar]):
          return random.choice([car for car in wishlist if car in lists.averagecar])
      return random.choice(lists.averagecar)
    elif averchance < randomchance:
      if len([car for car in wishlist if car in lists.lowcar]) > 0:
        if random.random() <= 0.05*len([car for car in wishlist if car in lists.lowcar]):
          return random.choice([car for car in wishlist if car in lists.lowcar])
      return random.choice(lists.lowcar)

def randomgaragecar(userdata):
  # 45% 45% 0% 0% | Classic 10%
  randomchance = random.random()
  # Average car 45%
  averchance = 0.55 + (0.3*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # Classic car 10% (1 in 7 when 825 luck)
  classicchance = 0.1 + (0.05*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  if randomchance <= classicchance:
    return random.choice(lists.classiccar)
  elif classicchance < randomchance <= averchance:
    return random.choice(lists.highcar)
  elif averchance < randomchance:
    return random.choice(lists.lowcar)

def randomaveragecar(userdata):
  # 18% 50% 30% 2%
  randomchance = random.random()
  # Average car 50%
  averchance = 0.82 + (0.2*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # High car 20%
  highchance = 0.22 + (0.22*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  # Exotic car 2% (1 in 50 when 0 luck, 1 in 33 when 500 luck, 1 in 27 when 825 luck)
  exochance = 0.02 + (0.02*userdata['stats']['luk']/1000 * (1.5 if userdata['donor'] == 2 else 1.2 if userdata['donor'] == 1 else 1))
  if randomchance <= exochance:
    if random.randint(1, 5) == 1:
      return random.choice(lists.classiccar)
    return random.choice(lists.exoticcar)
  elif exochance < randomchance <= highchance:
    return random.choice(lists.highcar)
  elif highchance < randomchance <= averchance:
    return random.choice(lists.averagecar)
  elif averchance < randomchance:
    return random.choice(lists.lowcar)

def randomluxurycar(userdata):
  randomchance = random.random()
  # Average car 10%
  averchance = 1
  # High car 65%
  highchance = 0.9
  # Exotic car 25%
  exochance = 0.25
  if randomchance <= exochance:
    if random.randint(1, 5) == 1:
      return random.choice(lists.classiccar)
    return random.choice(lists.exoticcar)
  elif exochance < randomchance <= highchance:
    return random.choice(lists.highcar)
  elif highchance < randomchance <= averchance:
    return random.choice(lists.averagecar)

def racemap(mode, location, p1grid, p2grid, p1direction, p2direction, variation, p1dis, p2dis):
  if mode == 'easy':
    racetrack = Image.open(rf"images/{location.lower()}_easy{variation}.png").convert("RGB")
  else:
    racetrack = Image.open(rf"images/{location.lower()}.png").convert("RGB")

  p1car = Image.open(r"images/p1car_sw.png").convert("RGBA")
  if p1direction == "se":
    p1car = p1car.rotate(90)
  elif p1direction == "nw":
    p1car = p1car.rotate(-90)
  elif p1direction == "ne":
    p1car = p1car.rotate(180)

  p2car = Image.open(r"images/p2car_sw.png").convert("RGBA")
  if p2direction == "se":
    p2car = p2car.rotate(90)
  elif p2direction == "nw":
    p2car = p2car.rotate(-90)
  elif p2direction == "ne":
    p2car = p2car.rotate(180)
  endpointer = Image.open(r"images/end.png").convert("RGBA")
  endloc = lists.racecoords[location]['endloc'][variation]

  if p1dis < 0:
    p1dis = 0
  if p2dis < 0:
    p2dis = 0

  if mode == 'easy':
    p1pos = lists.racecoords[location]["p1nodes"][p1grid[0]][p1grid[1]]
    p2pos = lists.racecoords[location]["p2nodes"][p2grid[0]][p2grid[1]]
  else:
    if p1direction in lists.availableroute[location][variation][p1grid[0]][p1grid[1]] and p1dis != 0:
      c = lists.racecoords[location]["p1nodes"][p1grid[0]][p1grid[1]]
      if p1direction == 'sw':
        n = lists.racecoords[location]["p1nodes"][p1grid[0]][p1grid[1]-1]
      elif p1direction == 'ne':
        n = lists.racecoords[location]["p1nodes"][p1grid[0]][p1grid[1]+1]
      elif p1direction == 'se':
        n = lists.racecoords[location]["p1nodes"][p1grid[0]+1][p1grid[1]]
      elif p1direction == 'nw':
        n = lists.racecoords[location]["p1nodes"][p1grid[0]-1][p1grid[1]]
      p1pos = (round(((n[0]-c[0])*p1dis/100)+c[0]), round(((n[1]-c[1])*p1dis/100)+c[1]))
    else:
      p1pos = lists.racecoords[location]["p1nodes"][p1grid[0]][p1grid[1]]

    if p2direction in lists.availableroute[location][variation][p2grid[0]][p2grid[1]] and p2dis != 0:
      c = lists.racecoords[location]["p2nodes"][p2grid[0]][p2grid[1]]
      if p2direction == 'sw':
        n = lists.racecoords[location]["p2nodes"][p2grid[0]][p2grid[1]-1]
      elif p2direction == 'ne':
        n = lists.racecoords[location]["p2nodes"][p2grid[0]][p2grid[1]+1]
      elif p2direction == 'se':
        n = lists.racecoords[location]["p2nodes"][p2grid[0]+1][p2grid[1]]
      elif p2direction == 'nw':
        n = lists.racecoords[location]["p2nodes"][p2grid[0]-1][p2grid[1]]
      p2pos = (round(((n[0]-c[0])*p2dis/100)+c[0]), round(((n[1]-c[1])*p2dis/100)+c[1]))
    else:
      p2pos = lists.racecoords[location]["p2nodes"][p2grid[0]][p2grid[1]]

  if p1pos == ():
    print(f"Empty p1pos: {p1grid[0]}, {p1grid[1]}")
  if p2pos == ():
    print(f"Empty p2pos: {p2grid[0]}, {p2grid[1]}")

  racetrack.paste(p1car, p1pos, p1car)
  racetrack.paste(p2car, p2pos, p2car)
  racetrack.paste(endpointer, endloc, endpointer)

  p1car.close()
  p2car.close()
  endpointer.close()

  byte = BytesIO()
  racetrack.save(byte, format="png")
  racetrack.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  return file

def _rotation(direction, mode):
  if mode == 'right':
    clock = ['sw', 'nw', 'ne', 'se']
  elif mode == 'left':
    clock = ['sw', 'se', 'ne', 'nw']
  index = clock.index(direction)+1
  if index == 4:
    index = 0
  return clock[index]

def raceprogress(mode, variation, userdata, pgrid, pdirection, actions, currentspeed, topspeed, userdis, npc = True, usercar = None):
  # Drifitng increases maximum speed allowed to drift
  # Handling reduces speed lost when turning and drifting
  # Braking decreases car damage when a mistake was made

  if mode == 'easy':
    comp = ''
    warn = ''
    cardamage = 0

    acceleration = round(topspeed * (0.15 + round(userdata['stats']['acc'] / 1000, 2)), 2)
    suggested = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]]

    if suggested == pdirection:
      if 'drift' in actions:
        deceleration = 10
        if npc is False:
          if usercar['abs'] is True:
            deceleration *= 2
        elif npc is True:
          deceleration *= 2
        if currentspeed <= 60:
          if usercar is not None:
            deceleration = deceleration * (1 + (usercar['tunedb'] / 10))
          currentspeed -= deceleration
        else:
          if usercar is not None:
            deceleration = (deceleration/100) * (1 + (usercar['tunedb'] / 10))
          currentspeed *= (1-deceleration)
      else:
        currentspeed += acceleration
    else:
      if npc:
        if random.randint(0, 1) == 1:
          actions.append('drift')
      pdirection = suggested
      if 'drift' in actions:
        turningmaxspeed = topspeed*0.7+round(userdata['stats']['dri']/10, 1)
        if npc is False:
          if usercar['abs'] is True:
            turningmaxspeed *= 0.8

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.3
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.15

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)
      else:
        turningmaxspeed = 40+round(userdata['stats']['dri']/10, 1)

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.3 + ((currentspeed-turningmaxspeed)/100)
          if deceleration >= 1.6:
            warn += 'Too fast for a turn! Car damaged heavily\n'
            cardamage += 3
          elif  deceleration >= 1:
            warn += 'Too fast for a turn! Car damaged moderately\n'
            cardamage += 2
          else:
            warn += 'Too fast for a turn! Car damaged slightly\n'
            cardamage += 1
        else:
          deceleration = 0.3

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

    if currentspeed < 0:
      currentspeed = 0
    elif currentspeed > topspeed:
      currentspeed = topspeed

    userdis += round(currentspeed)
    if userdis >= 100:
      for i in range(round(userdis // 100)):
        suggested = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]]
        if pdirection == 'sw':
          if pdirection == suggested:
            pgrid[1] -= 1
        elif pdirection == 'ne':
          if pdirection == suggested:
            pgrid[1] += 1
        elif pdirection == 'se':
          if pdirection == suggested:
            pgrid[0] += 1
        elif pdirection == 'nw':
          if pdirection == suggested:
            pgrid[0] -= 1
      userdis = round((userdis / 100) % 1, 4)*100

    cardamage *= round(1-(userdata['stats']['bra']/1000), 3)
    return [pgrid, pdirection, userdis, round(currentspeed, 2), comp, warn, cardamage]

  comp = ''
  warn = ''
  turned = False
  brake = False
  acc = False
  cardamage = 0

  avail = lists.availableroute[userdata['location']][variation][pgrid[0]][pgrid[1]]

  if npc is False:
    if 'left' not in actions and 'right' not in actions and pdirection not in avail:
      suggested = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]]
      if _rotation(pdirection, 'left') == suggested:
        actions.append('left')
      elif _rotation(pdirection, 'right') == suggested:
        actions.append('right')
      else:
        rotation = random.choice([r for r in [_rotation(pdirection, 'left'), _rotation(pdirection, 'right')] if r in avail])
        if rotation == _rotation(pdirection, 'left'):
          actions.append('left')
        elif rotation == _rotation(pdirection, 'right'):
          actions.append('right')
  else:
    suggested = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]]

    if suggested == pdirection:
      actions.append("acc")

      if pdirection == 'sw':
        n = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]-1]
      elif pdirection == 'ne':
        n = lists.suggestedroute[userdata['location']][variation][pgrid[0]][pgrid[1]+1]
      elif pdirection == 'se':
        n = lists.suggestedroute[userdata['location']][variation][pgrid[0]+1][pgrid[1]]
      elif pdirection == 'nw':
        n = lists.suggestedroute[userdata['location']][variation][pgrid[0]-1][pgrid[1]]

      if n != pdirection:
        if currentspeed >= 100:
          actions.append("brake")
      else:
        actions.append("acc")
    else:

      _currentspeed = currentspeed
      while _currentspeed >= (40+round(userdata['stats']['dri']/10, 1)) and len(actions) < 2:
        actions.append('brake')
        _currentspeed -= 20

      if _rotation(pdirection, 'left') == suggested:
        actions.append('left')
      elif _rotation(pdirection, 'right') == suggested:
        actions.append('right')

  for i in range(len(actions)):
    try:
      action = actions[i]
    except IndexError:
      break
    if action == 'left' or action == 'right':

      if (userdis / 100) % 1 >= 0.2 and pdirection in avail:
        if pdirection == 'sw':
          pgrid[1] -= 1
        elif pdirection == 'ne':
          pgrid[1] += 1
        elif pdirection == 'se':
          pgrid[0] += 1
        elif pdirection == 'nw':
          pgrid[0] -= 1
        avail = lists.availableroute[userdata['location']][variation][pgrid[0]][pgrid[1]]
        userdis -= 100

        rotation = _rotation(pdirection, action)
        if rotation not in avail or turned is True:
          if pdirection == 'sw':
            pgrid[1] += 1
          elif pdirection == 'ne':
            pgrid[1] -= 1
          elif pdirection == 'se':
            pgrid[0] -= 1
          elif pdirection == 'nw':
            pgrid[0] += 1
          avail = lists.availableroute[userdata['location']][variation][pgrid[0]][pgrid[1]]
          userdis += 100
          continue

      rotation = _rotation(pdirection, action)
      if rotation not in avail or turned is True:
        continue
      pdirection = rotation
      turned = True

      if (action == 'left' and len(actions[i+1:]) > 1 and actions[i+1] == 'brake' and actions[i+2] == 'right') or (action == 'right' and len(actions[i+1:]) > 1 and actions[i+1] == 'brake' and actions[i+2] == 'left'):
        # E-Drift
        comp = "Perfect E-Drift"
        turningmaxspeed = 100+round(userdata['stats']['dri']/10, 1)
        if usercar['abs'] is True:
          turningmaxspeed *= 0.8
        actions = actions[i+3:]

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.3
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.15

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

      elif len(actions[i+1:]) > 0 and actions[i+1] == 'brake':
        # Incomplete E-Drift
        comp = "Poor E-Drift"
        turningmaxspeed = 60+round(userdata['stats']['dri']/10, 1)
        if usercar['abs'] is True:
          turningmaxspeed *= 0.8
        actions = actions[i+2:]

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.4
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.2

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

      elif (userdata['stats']['dri'] >= 300) and ((action == 'left' and len(actions[i+1:]) > 2 and actions[i+1] == 'right' and actions[i+2] == 'left' and actions[i+3] == 'right') or (action == 'right' and len(actions[i+1:]) > 2 and actions[i+1] == 'left' and actions[i+2] == 'right' and actions[i+3] == 'left')):
        # Perfect Throttle Drift
        comp = "Perfect Throttle Drift"
        turningmaxspeed = 120+round(userdata['stats']['dri']/10, 1)
        if usercar['abs'] is True:
          turningmaxspeed *= 0.8
        actions = actions[i+4:]

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.45
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.05

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

      elif (userdata['stats']['dri'] >= 300) and ((action == 'left' and len(actions[i+1:]) > 1 and actions[i+1] == 'right' and actions[i+2] == 'left') or (action == 'right' and len(actions[i+1:]) > 1 and actions[i+1] == 'left' and actions[i+2] == 'right')):
        # Good Throttle Drift
        comp = "Good Throttle Drift"
        turningmaxspeed = 100+round(userdata['stats']['dri']/10, 1)
        if usercar['abs'] is True:
          turningmaxspeed *= 0.8
        actions = actions[i+3:]

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.4
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.1

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

      elif (userdata['stats']['dri'] >= 300) and ((action == 'left' and len(actions[i+1:]) > 0 and actions[i+1] == 'right') or (action == 'right' and len(actions[i+1:]) > 0 and actions[i+1] == 'left')):
        # Poor Throttle Drift
        comp = "Poor Throttle Drift"
        turningmaxspeed = 80+round(userdata['stats']['dri']/10, 1)
        if usercar['abs'] is True:
          turningmaxspeed *= 0.8
        actions = actions[i+2:]

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.35
          warn += 'Too fast for a drift! Car damaged slightly\n'
          cardamage += 1
        else:
          deceleration = 0.2

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

      else:

        turningmaxspeed = 40+round(userdata['stats']['dri']/10, 1)

        if currentspeed > turningmaxspeed: # Speed penalty
          deceleration = 0.3 + ((currentspeed-turningmaxspeed)/100)
          if deceleration >= 1.6:
            warn += 'Too fast for a turn! Car damaged heavily\n'
            cardamage += 3
          elif  deceleration >= 1:
            warn += 'Too fast for a turn! Car damaged moderately\n'
            cardamage += 2
          else:
            warn += 'Too fast for a turn! Car damaged slightly\n'
            cardamage += 1
        else:
          deceleration = 0.3

        deceleration *= (1-round(userdata['stats']['han']/1000/2, 3))

        currentspeed *= (1-deceleration)

    elif action == 'brake':
      deceleration = 10
      if npc is False:
        if usercar['abs'] is True:
          deceleration *= 2
      elif npc is True:
        deceleration *= 2
      if currentspeed <= 60:
        if usercar is not None:
          deceleration = deceleration * (1 + (usercar['tunedb'] / 10))
        currentspeed -= deceleration
      else:
        if usercar is not None:
          deceleration = (deceleration/100) * (1 + (usercar['tunedb'] / 10))
        currentspeed *= (1-deceleration)

      brake = True
    elif action == 'acc':
      acceleration = round(topspeed * (0.2 * (1+round(userdata['stats']['acc'] / 1000, 3))), 2)
      currentspeed = round(currentspeed + round(random.triangular(-5, 5, userdata['stats']['luk']/100)) + acceleration, 2)
      acc = True


  if brake is False and turned is False and acc is False:
    acceleration = round(topspeed*0.1, 2)
    currentspeed = round(currentspeed + round(random.triangular(-5, 5, userdata['stats']['luk']/100)) + acceleration, 2)

  if currentspeed < 0:
    currentspeed = 0
  elif currentspeed > topspeed:
    currentspeed = topspeed

  userdis += round(currentspeed)
  if userdis >= 100:
    for i in range(round(userdis // 100)):
      avail = lists.availableroute[userdata['location']][variation][pgrid[0]][pgrid[1]]
      if pdirection == 'sw':
        if pdirection in avail:
          pgrid[1] -= 1
      elif pdirection == 'ne':
        if pdirection in avail:
          pgrid[1] += 1
      elif pdirection == 'se':
        if pdirection in avail:
          pgrid[0] += 1
      elif pdirection == 'nw':
        if pdirection in avail:
          pgrid[0] -= 1
    userdis = round((userdis / 100) % 1, 4)*100

  cardamage *= round(1-(userdata['stats']['bra']/1000), 3)
  return [pgrid, pdirection, userdis, round(currentspeed, 2), comp, warn, cardamage]

async def racetrack(racemap, userdis, user2dis):
  pos = userdis // 100
  pos2 = user2dis // 100
  if pos > 10:
    pos = 10
  if pos2 > 10:
    pos2 = 10
  if racemap == 0:
    userpos = lists.p1racetrack0[pos]
    user2pos = lists.p2racetrack0[pos2]
  elif racemap == 1:
    userpos = lists.p1racetrack1[pos]
    user2pos = lists.p2racetrack1[pos2]

  mapname = lists.racemaps[racemap]

  racetrack = Image.open(rf"images/race_track{racemap}.png").convert("RGB")

  p1car = Image.open(r"images/p1car.png").convert("RGBA")
  p2car = Image.open(r"images/p2car.png").convert("RGBA")

  racetrack.paste(p1car, userpos, p1car)
  racetrack.paste(p2car, user2pos, p2car)

  p1car.close()
  p2car.close()

  byte = BytesIO()

  racetrack.save(byte, format="png")
  racetrack.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  return [mapname, file]

async def raceevents(racemap, userdis, userdata, usercspeed, usercarspeed):
  if racemap == 0:
    event = lists.racetrack0events[userdis // 100]
  elif racemap == 1:
    event = lists.racetrack1events[userdis // 100]

  accelerated = round(usercarspeed * (0.15 + round(userdata['stats']['acc'] / 1000, 2)), 2)

  # Prvevents going over top speed
  if round(accelerated + usercspeed, 2) > usercarspeed:
    accelerated = round(usercarspeed - usercspeed, 2)

  if event == "turn":

    # Reduces speed when turning
    percentage = (0.8 - round(userdata['stats']['dri'] / 1000, 2))
    if accelerated <= 0:
      decelerated = round((usercarspeed*0.4) * percentage, 2)
    else:
      decelerated = round(accelerated * percentage, 2)

    minspeed = round(round(0.1 + userdata['stats']['han'] / 1000, 2) * usercarspeed)

    # Prevents decelerating over minimum speed
    if (accelerated - decelerated) + usercspeed < minspeed:
      decelerated = round(usercspeed - minspeed + accelerated, 2)
    if decelerated < 0:
      decelerated =  0


    if accelerated > 0:
      # Calculate total velocity
      accelerated = accelerated - decelerated
    else:
      # Check if speed is maxed
      accelerated = round((usercarspeed * (0.2 + round(userdata['stats']['acc'] / 1000, 2))) - decelerated, 2)
      if accelerated > 0:
        accelerated = 0

  usercspeed = round(usercspeed + round(random.triangular(-10, 10, userdata['stats']['luk']/100)) + accelerated, 2) 
  if usercspeed < 0:
    usercspeed = 0
  elif usercspeed > usercarspeed:
    usercspeed = usercarspeed

  userdis += round(usercspeed)

  return [userdis, usercspeed]

def tunecar(tuned, user):
  randomchance = random.random()
  if tuned == 0:
    succhance = (0.95 + (0.05*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 1:
    succhance = (0.9 + (0.08*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 2:
    succhance = (0.85 + (0.1*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 3:
    succhance = (0.85 + (0.1*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 4:
    succhance = (0.8 + (0.1*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 5:
    succhance = (0.8 + (0.1*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 6:
    succhance = (0.75 + (0.15*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 7:
    succhance = (0.7 + (0.2*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned == 8:
    succhance = (0.7 + (0.2*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if 9 <= tuned < 20:
    succhance = (0.6 + (0.3*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True
  if tuned >= 20:
    succhance = (0.5 + (0.3*(1.5 if user['job'] == "Mechanic" else 1)*user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))
    if succhance >= 1:
      succhance = 0.99
    if randomchance > succhance:
      return False
    return True

def donatorcase():
  a = False
  b = False
  cash = 0
  medkit = 0
  bribe = 0
  carkey = 0
  luxurykey = 0
  safe = 0
  weapon = []
  for x in range(3):
    randomchance = round(random.random(), 8)
    while a == True and randomchance > 0.7:
      randomchance = round(random.random(), 8)
    while b == True and 0.3 < randomchance <= 0.5:
      randomchance = round(random.random(), 8)
    if randomchance > 0.7:
      for x in range(random.randint(6, 16)):
        item = random.choice(['medkit','bribe'])
        if item == 'medkit':
          medkit += 1
        elif item == 'bribe':
          bribe += 1
        a = True
    elif 0.5 < randomchance <= 0.7:
      for x in range(random.randint(6, 12)):
        carkey += 1
    elif 0.2 < randomchance <= 0.5:
      randomcash = round(random.uniform(3000, 6000))
      cash += round(randomcash)
      b = True
    elif 0.1 < randomchance <= 0.2:
      c = True
      while c == True:
        w = random.choice(lists.weapon)
        wprice = lists.item_prices[w]
        if wprice >= 10000:
          randomchance2 = round(random.random(), 8)
          if randomchance2 <= 0.6:
            c = True
          else:
            c = False
            weapon.append(w)
        else:
          c = False
          weapon.append(w)
  safe += random.randint(5, 10)
  luxurykey += random.choice([1, 2, 2, 2])
  return {'cash': round(cash), 'medkit': medkit, 'bribe': bribe,'carkey': carkey,'luxurykey': luxurykey, 'safe': safe,'weapon': weapon}

def purser():
  randomchance = round(random.random(),2)
  if randomchance <= 0.5:
    randomitem = random.choice(['candy','candy','notebook','notebook','soda','candy','trash','chocolate','ring','fake','bread','bread'])
    return randomitem
  else:
    randomcash = round(random.uniform(300,900))
    return round(randomcash)

def giftboxr():
  randomchance = round(random.random(),2)
  if randomchance <= 0.5:
    randomitem = random.choice(['candy','rose','candy','candy','chocolate','daisy','ribbon','ring','console','console','daisy','daisy','pet','bread','bread'])
    return randomitem
  else:
    randomcash = round(random.uniform(200,600))
    return round(randomcash)

def drugstash():
  drug = random.choice(['cannabis','ecstasy','cannabis','ecstasy','cannabis','ecstasy','cannabis','ecstasy','heroin','heroin','heroin','cannabis','metham','metham','xanax'])
  randomcount = random.randint(4,12)
  return str(randomcount) + " " + drug

# async def food(item, ctx, count = 1, *args):
#   if await blocked(ctx.author.id) == False:
#     return
#   user = await finduser(ctx.author.id)
#   userstorage = user['storage']
#   try:
#     userstorage[item]
#   except:
#     await ctx.respond("You don't have this food!")
#     return
#   if userstorage[item] <= 0:
#     await ctx.respond("You don't have this food!")
#     return
#   if count == "max":
#     count = userstorage[item]
#   try:
#     count = int(count)
#   except:
#     await ctx.respond("Invalid quantity, it must be a number!")
#     return
#   if userstorage[item] < count:
#     await ctx.respond("You don't have that much item!")
#     return
#   if count <= 0:
#     await ctx.respond("You have to give a positive number idiot")
#     return
#   if user['energy'] >= user['energyc']:
#     await ctx.respond("You have too much energy!")
#     return
#   await updateinc(ctx.author.id, f"storage.{item}", -count)
#   user = await finduser(ctx.author.id)
#   if user['storage'][item] <= 0:
#     await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.{item}': 1}})
#   dispatcher = {"Energy Drink": 80, "Bag of Chips": 10, "Bread": 30, "Soda": 20, "Milk": 20, "Meat": 50, "Sausage": 40, "Chocolate": 80, "Lollipop": 10, "Drumstick": 50}
#   if user['s'] == 28 and item == "Meat":
#     await updateset(ctx.author.id, 's', 29)
#   energy = dispatcher[item] * count
#   await updateinc(ctx.author.id, "energy", energy)
#   await ctx.respond(f"You ate {count} {item} and gained {energy} energy!")

async def pill(ctx, *args):
  user = await finduser(ctx.author.id)
  try:
    user['storage']['Pill']
  except:
    await ctx.respond("You don't have any pills!")
    return
  if user['storage']["Pill"] <= 0:
    await ctx.respond("You don't have any pills!")
    return
  await updateinc(ctx.author.id, "storage.Pill", -1)
  if user['storage']['Pill'] == 1:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Pill': 1}})
  if not user['inhosp']:
    if random.randint(0, 1):
      await updateset(ctx.author.id, "inhosp", True)
      t = round(time.time()) + random.randint(30, 120)
      await updateset(ctx.author.id, "timer.hosp", t)
      await ctx.respond(f"You ate the wrong pill and sent yourself into the hospital for {ab(t-round(time.time()))}!")
    else:
      await ctx.respond("You swallowed the pill and nothing happened...")
  else:
    if user['timer']['hosp'] > 600:
      await ctx.respond("Your wounds are too severe! You can't even swallow a pill")
      return
    if random.randint(0, 3):
      t = round(time.time()) + random.randint(30, 120)
      await ctx.respond(f"You ate the wrong pill and fainted! You have to stay in the hospital for another {ab(t-round(time.time()))}")
      await updateinc(ctx.author.id, "timer.hosp", t)
    else:
      await updateset(ctx.author.id, "inhosp", False)
      await cll.update_one({"id": ctx.author.id}, {"$unset": {'timer.hosp': 1}})
      await ctx.respond("Lucky fellow! The pill magically cured you!")

async def garage_key(ctx, count, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usergk = userstorage['Garage Key']
  except:
    await ctx.respond("You don't have any Garage Key in your storage")
    return
  if usergk < count:
    await ctx.respond("You don't have enough Garage Keys in your storage!")
    return

  await updateset(ctx.author.id, 'blocked', True)

  carlist = []
  carlistnames = []
  total = 0
  for x in range(count):
    if random.random() > 0.05:
      continue
    user = await finduser(ctx.author.id)
    car = randomgaragecar(user)
    randomgold = random.randint(1,2048)

    if len(user['garage']) == 0:
      carindex = 1
    else:
      carindex = user['garage'][-1]["index"]+1
    carindex += total

    total += 1

    if randomgold == 1696:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': True, 'locked': False}
    else:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': False, 'locked': False}
    
    carlist.append(carinfo)

    if randomgold == 1696:
      carlistnames.append(f"{star} Golden " + car)
    else:
      carlistnames.append(car)

  if len(carlist)+len(user['garage']) >= user['garagec']:
    if user['garagec'] - (len(carlist)+len(user['garage'])) <= 0:
      carlist = []
      carlistnames = []
    else:
      carlist = carlist[:(user['garagec']-len(user['garage']))]
      carlistnames = carlistnames[:(user['garagec']-len(user['garage']))]

  if user['storage']['Garage Key'] == count:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$unset": {"storage.Garage Key": 1}, "$inc": {"garagec": count*2}})
  else:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$inc": {"storage.Garage Key": -count, "garagec": count*2}})

  await updateset(ctx.author.id,'blocked',False)

  embed = discord.Embed(title=f"Used {count} Garage Key{'s' if count > 1 else ''}", description=f"You used {count} Garage Key{'s' if count > 1 else ''} and gained {count*2} garage capacity!", color=color.green())
  if len(carlistnames) > 0:
    embed.add_field(name="Barnfind!",value=f"You've also found {'these cars' if len(carlistnames) > 1 else 'a car'} from {count} Garage Key{'s' if count > 1 else ''}:\n{', '.join(carlistnames)}")

  await ctx.respond(embed=embed)

async def tatter(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  count = 30
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usertatter = userstorage['Tatter']
  except:
    await ctx.respond("You don't have any Tatter in your storage")
    return
  if usertatter < count:
    await ctx.respond("You don't have enough Tatters in your storage!")
    return
  await updateinc(ctx.author.id, 'storage.Tatter', -count)
  await updateinc(ctx.author.id, f'storage.Apparel Box', 1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  usertatter = userstorage['Tatter']
  if usertatter <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Tatter': 1}})
  await ctx.respond(f"You turned 30 Tatters into 1 Apparel Box!")

async def tuner(ctx, carid = None, *args):
  await ctx.respond("This item can now be used through `/tune`")
  return 
  # if await blocked(ctx.author.id) == False:
  #   return
  # if carid is None:
  #   await ctx.respond("You have to give a car ID!")
  #   return
  # carid = str(carid)
  # user = await finduser(ctx.author.id)
  # userstorage = user['storage']
  # usergarage = user['garage']
  # try:
  #   usertuner = userstorage['Tuner']
  # except:
  #   await ctx.respond("You don't have any Tuner in your storage")
  #   return
  # try:
  #   int(carid)
  # except:
  #   await ctx.respond("Give a valid car ID!")
  #   return
  # try:
  #   usercar = [x for x in usergarage if x["index"] == int(carid)][0]
  # except:
  #   await ctx.respond("You don't have this car in your garage!")
  #   return
  # if usercar['tuned'] >= 20:
  #   chance = 0.5 * 10 ** (-0.0586 * ((usercar['tuned'] - 20) - 1))
  # else:
  #   chance = 1
  # if random.random() <= chance:
  #   usercarspeed = usercar['speed']
  #   speedinc = round(usercarspeed*0.015 + usercarspeed,2)
  #   if user['storage']["Tuner"] == 1:
  #     await cll.update_one({"id": ctx.author.id, "garage.index": usercar["index"]}, {"$inc": {"garage.$.tuned": 1}, "$set": {"garage.$.speed": round(speedinc,2)}, "$unset": {"storage.Tuner": 1} } )
  #   else:
  #     await cll.update_one({"id": ctx.author.id, "garage.index": usercar["index"]}, {"$inc": {"garage.$.tuned": 1, "storage.Tuner": -1}, "$set": {"garage.$.speed": round(speedinc,2)}})

  #   if usercar['golden'] == True:
  #     await ctx.respond(f"You tuned your {star} Golden {usercar['name']} and it's now {usercar['tuned'] + 1} tuned!")
  #   else:
  #     await ctx.respond(f"You tuned your {usercar['name']} and it's now {usercar['tuned'] + 1} tuned!")
  # else:
  #   if user['storage']["Tuner"] == 1:
  #     await cll.update_one({"id": ctx.author.id, "garage.index": usercar["index"]}, {"$unset": {"storage.Tuner": 1} } )
  #   else:
  #     await cll.update_one({"id": ctx.author.id, "garage.index": usercar["index"]}, {"$inc": {"storage.Tuner": -1}})

  #   if usercar['golden'] == True:
  #     await ctx.respond(f"You tried to tune your {star} Golden {usercar['name']} but failed!")
  #   else:
  #     await ctx.respond(f"You tried to tune your {usercar['name']} but failed!")

async def scrap(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  count = 4
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userscrap = userstorage['Scrap']
  except:
    await ctx.respond("You don't have any Scrap in your storage")
    return
  if userscrap < count:
    await ctx.respond("You don't have enough Scraps in your storage!")
    return
  await updateinc(ctx.author.id, 'storage.Scrap', -count)
  await updateinc(ctx.author.id, f'storage.Luxury Car Key', 1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userscrap = userstorage['Scrap']
  if userscrap <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Scrap': 1}})
  await ctx.respond(f"You turned 4 Scraps into 1 Luxury Car Key <:luxury_car_key:1358506290237804695>!")

async def trash(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  count = 50
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usertrash = userstorage['Trash']
  except:
    await ctx.respond("You don't have any trash in your storage")
    return
  if usertrash < count:
    await ctx.respond("You can't figure anything out with that little of trash!")
    return
  await updateinc(ctx.author.id, 'storage.Trash', -count)
  item = random.choice(["Bribe", "Medical Kit", "Fuel", "Beer", "Tuner", "Scrap", "Average Car Key"])
  await updateinc(ctx.author.id, f'storage.{item}', 1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  usertrash = userstorage['Trash']
  if usertrash <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Trash': 1}})
  await ctx.respond(f"You fabricated a concotion of trash into a {item}!")

  if user['s'] == 103:
    await updateset(ctx.author.id, 's', 104)

async def ribbon(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  count = 20
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userribbon = userstorage['Ribbon']
  except:
    await ctx.respond("You don't have any ribbons in your storage")
    return
  if userribbon < count:
    await ctx.respond("You can't figure anything out with that little of ribbon!")
    return
  await updateinc(ctx.author.id, 'storage.Ribbon', -count)
  await updateinc(ctx.author.id, f'storage.Giftbox', 1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userribbon = userstorage['Ribbon']
  if userribbon <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Ribbon': 1}})
  await ctx.respond(f"You crafted a giftbox out of 20 ribbons!")

async def laptop(ctx, count: int = 1, *args): 
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userlaptop = userstorage['Laptop']
  except:
    await ctx.respond("You don't have any Laptop in your storage")
    return
  if count == 'max':
    count = userlaptop
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    return
  if userlaptop < count:
    await ctx.respond("You don't have that much Laptops in your storage!")
    return
  await updateinc(ctx.author.id, 'storage.Laptop', -count)
  await updateinc(ctx.author.id, 'business', count)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userlaptop = userstorage['Laptop']
  userbusiness = user['business']
  if userlaptop <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Laptop': 1}})
  await ctx.respond(f"You started {count} business and now you will earn <:cash:1329017495536930886> {userbusiness*0.01} every minute!")

async def document(ctx, count: int = 1, *args): 
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userdoc = userstorage['Document']
  except:
    await ctx.respond("You don't have any Document in your storage")
    return
  if count == 'max':
    count = userdoc
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    return
  if userdoc < count:
    await ctx.respond("You don't have that much Document in your storage!")
    return
  await updateinc(ctx.author.id, 'storage.Document', -count)
  await updateinc(ctx.author.id, 'stats.int', count*20)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userdoc = userstorage['Document']
  if userdoc <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Document': 1}})
  await ctx.respond(f"You read {count} Document and gained {count*20} Intelligence <:intelligence:940955425443024896>!")

async def homework(ctx, count: int = 1, *args): 
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userhw = userstorage['Homework']
  except:
    await ctx.respond("You don't have any Homework in your storage")
    return
  if count == 'max':
    count = userhw
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    return
  if userhw < count:
    await ctx.respond("You don't have that much Homework in your storage!")
    return
  await updateinc(ctx.author.id, 'storage.Homework', -count)
  await updateinc(ctx.author.id, 'stats.int', count*10)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userhw = userstorage['Homework']
  if userhw <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Homework': 1}})
  await ctx.respond(f"You finished {count} Homework and gained {count*10} Intelligence <:intelligence:940955425443024896>!")

async def beer(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userbeer = userstorage['Beer']
  except:
    await ctx.respond("You don't have any Beer in your storage!")
    return
  try:
    user = await finduser(ctx.author.id)
    usertimer = user['timer']
    userbeertimer = usertimer['beer']
    await ctx.respond(f"You are already drunk! You still have {ab(userbeertimer-round(time.time()))} left")
    return
  except:
    pass
  await updateinc(ctx.author.id, 'storage.Beer', -1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userbeer = userstorage['Beer']
  if userbeer <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Beer': 1}})
  await updateset(ctx.author.id, 'timer.beer', round(time.time())+3600)
  await ctx.respond("You drank your Beer and now you have 1 hour HP Boost!")

async def fuel(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    userfuel = userstorage['Fuel']
  except:
    await ctx.respond("You don't have any Fuel in your storage!")
    return
  try:
    user = await finduser(ctx.author.id)
    usertimer = user['timer']
    userfueltimer = usertimer['fuel']
    await ctx.respond(f"You already used a fuel! You still have {ab(userfueltimer-round(time.time()))} left")
    return
  except:
    pass
  await updateinc(ctx.author.id, 'storage.Fuel', -1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userfuel = userstorage['Fuel']
  if userfuel <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Fuel': 1}})
  await updateset(ctx.author.id, 'timer.fuel', round(time.time())+3600)
  await ctx.respond("You used a Fuel and now you have 1 hour car speed Boost!")

# async def insurance(ctx, *args):
#   if await blocked(ctx.author.id) == False:
#     return
#   user = await finduser(ctx.author.id)
#   userstorage = user['storage']
#   try:
#     userinsurance = userstorage['Insurance']
#   except:
#     await ctx.respond("You didn't buy any insurance")
#     return
#   try:
#     user = await finduser(ctx.author.id)
#     usertimer = user['timer']
#     usershieldtimer = usertimer['shield']
#     await ctx.respond(f"You already have a protection! You still have {ab(usershieldtimer-round(time.time()))} death protection left")
#     return
#   except:
#     pass
#   await updateinc(ctx.author.id, 'storage.Insurance', -1)
#   user = await finduser(ctx.author.id)
#   userstorage = user['storage']
#   userinsurance = userstorage['Insurance']
#   if userinsurance <= 0:
#     await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Insurance': 1}})
#   await updateset(ctx.author.id, 'timer.shield', round(time.time())+3600)
#   await ctx.respond("You activated your insurance and now you have 1 hour death protection!")

async def morphine(ctx, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  try:
    usermorphine = userstorage['Morphine']
  except:
    await ctx.respond("You don't have any Morphines in your storage")
    return
  try:
    usertimer = user['timer']
    usershieldtimer = usertimer['shield']
    await ctx.respond(f"You already have a protection! You still have {ab(usershieldtimer-round(time.time()))} death protection left")
    return
  except:
    pass
  await updateinc(ctx.author.id, 'storage.Morphine', -1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  usermorphine = userstorage['Morphine']
  if usermorphine <= 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Morphine': 1}})
  await updateset(ctx.author.id, 'timer.shield', round(time.time())+21600)
  await ctx.respond("You used a morphine and now you have 6 hour death protection!")

async def bribe(ctx, *args):
  if await finduser(ctx.author.id) == None:
    return
  if await userbanned(ctx.author.id) == True:
    return
  user = await finduser(ctx.author.id)
  userinjail = user['injail']
  if userinjail == False:
    await ctx.respond("You are not even in Jail, why are you using a Bribe?")
    return
  userstoragelist = list(user['storage'])
  if not "Bribe" in userstoragelist:
    await ctx.respond("You don't have any bribes left to bribe the guard!")
    return
  await updateinc(ctx.author.id, "storage.Bribe", -1)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userbribeq = userstorage["Bribe"]
  if userbribeq == 0:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f'storage.Bribe': 1}})
  await updateset(ctx.author.id, 'injail', False)
  await cll.update_one({"id": ctx.author.id}, {"$unset": {'timer.jail': 1}})
  if user['s'] == 47:
    await updateset(ctx.author.id, 's', 48)
  await ctx.respond("You used 1 Bribe to get out of the Jail!")

async def medical_kit(ctx, count, *args):
  if await finduser(ctx.author.id) == None:
    return
  if await userbanned(ctx.author.id) == True:
    return
  user = await finduser(ctx.author.id)
  userinhosp = user['inhosp']
  if userinhosp == False:
    await ctx.respond("You are not even in Hospital, why are you using a Medical Kit?")
    return
  userstoragelist = list(user['storage'])
  if not "Medical Kit" in userstoragelist:
    await ctx.respond("You don't have any medkits left to heal yourself!")
    return
  await updateinc(ctx.author.id, "storage.Medical Kit", -count)
  if user['storage']['Medical Kit'] == count:
    await cll.update_one({"id": ctx.author.id},{"$unset":{f"storage.Medical Kit": 1}})
  if user['timer']['hosp'] - (600*count) < round(time.time()):
    await updateset(ctx.author.id, 'inhosp', False)
    await cll.update_one({"id": ctx.author.id}, {"$inc": {'timer.hosp': -(600*count)}})
    await ctx.respond(f"You used {count} Medical Kit and got out of the hospital!")
  else:
    await cll.update_one({"id": ctx.author.id}, {"$inc": {'timer.hosp': -(600*count)}})
    await ctx.respond(f"You used {count} Medical Kit and reduced {count*10} minutes of hospital time! Time remaining: {ab(user['timer']['hosp']-(600*count)-round(time.time()))}")

async def royal_case(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  userstorage = user['storage']
  if 'Royal Case' not in userstoragelist:
    await ctx.respond("You don't have any Royal Case in your storage! Type `/claim` if you performed a purchase recently")
    await updateset(ctx.author.id, 'blocked', False)
    return
  userroyalq = userstorage["Royal Case"]
  if count == 'max':
    count = userroyalq
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    await updateset(ctx.author.id, 'blocked', False)
    return
  if count > userroyalq:
    await ctx.respond("You don't have that much Royal Cases to open!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  msg = await ctx.respond(f"Unboxing {count} Royal Cases...")
  allitems = []
  cash = 0
  medkit = 0
  bribe = 0
  carkey = 0
  luxurykey = 0
  safe = 0
  weapon = 0
  apparel = 0

  for _ in range(count):
    cash += random.randint(30000, 60000)
    medkit += random.randint(10, 20)
    bribe += random.randint(10, 20)
    carkey += random.randint(5, 15)
    luxurykey += random.randint(4, 6)
    safe += random.randint(5, 10)
    weapon += random.randint(1, 3)
    apparel += random.randint(1, 3)

  allitems.append(f"<:cash:1329017495536930886> **{aa(round(cash))}**")
  allitems.append(f"**{medkit}** Medical Kits")
  allitems.append(f"**{bribe}** Bribes")
  allitems.append(f"**{carkey}** Average Car Key <:average_car_key:1358506292725022761>")
  allitems.append(f"**{luxurykey}** Luxury Car Key <:luxury_car_key:1358506290237804695>")
  allitems.append(f"**{safe}** Safes")
  allitems.append(f"**{weapon}** Weapon Cases")
  allitems.append(f"**{apparel}** Apparel Boxes")

  if userroyalq == count:
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Medical Kit": medkit, "storage.Bribe": bribe, "storage.Average Car Key": carkey, "storage.Luxury Car Key": luxurykey, "storage.Safe": safe, "storage.Weapon Case": weapon, "storage.Apparel Box": apparel}, "$unset": {f"storage.Royal Case": 1}})
  else:
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Royal Case": -count, "storage.Medical Kit": medkit, "storage.Bribe": bribe, "storage.Average Car Key": carkey, "storage.Luxury Car Key": luxurykey, "storage.Safe": safe, "storage.Weapon Case": weapon, "storage.Apparel Box": apparel}})

  allitems = "\n".join(allitems)
  await msg.edit(f"You unboxed {count} Royal Case and got:\n{allitems}")
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userproperty = user['property']
  try:
    usersafeq = userstorage['Safe']
    await updateset(ctx.author.id,'stashc', (userproperty*100)+(usersafeq*500))
  except:
    pass
  await updateset(ctx.author.id,'blocked',False)
  return round(cash)

async def donator_case(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  userstorage = user['storage']
  if 'Donator Case' not in userstoragelist:
    await ctx.respond("You don't have any Donator Case in your storage! Type `/claim` if you have donated recently")
    await updateset(ctx.author.id, 'blocked', False)
    return
  userdonatorq = userstorage["Donator Case"]
  if count == 'max':
    count = userdonatorq
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    await updateset(ctx.author.id, 'blocked', False)
    return
  if count > userdonatorq:
    await ctx.respond("You don't have that much Donator Cases to open!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  msg = await ctx.respond(f"Unboxing {count} Donator Cases...")
  allitems = []
  cash = 0
  medkit = 0
  bribe = 0
  carkey = 0
  luxurykey = 0
  safe = 0
  weapon = []
  for x in range(count):
    items = donatorcase()
    cash = cash + round(items['cash'])
    medkit = medkit + items['medkit']
    bribe = bribe + items['bribe']
    carkey = carkey + items['carkey']
    luxurykey = luxurykey + items['luxurykey']
    safe = safe + items['safe']
    weapon = items['weapon']
  await updateinc(ctx.author.id, "storage.Donator Case", -count)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userdonatorq = userstorage["Donator Case"]
  if userdonatorq == 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {f"storage.Donator Case": 1}})
  if not cash == 0:
    await updateinc(ctx.author.id, 'cash', round(cash))
    allitems.append(f"<:cash:1329017495536930886> **{round(cash)}**")
  if not medkit == 0:
    await updateinc(ctx.author.id, f"storage.Medical Kit", medkit)
    allitems.append(f"**{medkit}** Medical Kit")
  if not bribe == 0:
    await updateinc(ctx.author.id, f"storage.Bribe", bribe)
    allitems.append(f"**{bribe}** Bribe")
  if not carkey == 0:
    await updateinc(ctx.author.id, f"storage.Average Car Key", carkey)
    allitems.append(f"**{carkey}** Average Car Key <:average_car_key:1358506292725022761>")
  if not luxurykey == 0:
    await updateinc(ctx.author.id, f"storage.Luxury Car Key", luxurykey)
    allitems.append(f"**{luxurykey}** Luxury Car Key <:luxury_car_key:1358506290237804695>")
  if not safe == 0:
    await updateinc(ctx.author.id, f"storage.Safe", safe)
    allitems.append(f"**{safe}** Safe")
  if not weapon == []:
    for weap in weapon:
      await updateinc(ctx.author.id, f"storage.{weap}", 1)
      allitems.append(f"**1** {weap}")
  allitems = "\n".join(allitems)
  await msg.edit(f"You opened {count} Donator Case and got:\n{allitems}")
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userproperty = user['property']
  try:
    usersafeq = userstorage['Safe']
    await updateset(ctx.author.id,'stashc', (userproperty*100)+(usersafeq*500))
  except:
    pass
  await updateset(ctx.author.id,'blocked',False)

async def purse(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    return
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  if 'Purse' not in userstoragelist:
    await ctx.respond("You don't have any Purse in your storage!")
    return
  userstorage = user['storage']
  userpurseq = userstorage["Purse"]
  if count == 'max':
    count = userpurseq
  if count > userpurseq:
    await ctx.respond("You don't have that much Purses to open!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  allitems = []
  cash = 0
  candy = 0
  soda = 0
  notebook = 0
  trash = 0
  chocolate = 0
  ring = 0
  fake = 0
  bread = 0
  for x in range(count):
    item = purser()
    try:
      int(item)
      cash = cash + round(item)
    except:
      c = random.randint(1, 4)
      if item == 'candy':
        candy += c
      elif item == 'soda':
        soda += c
      elif item == 'notebook':
        notebook += 1
      elif item == 'trash':
        trash += c
      elif item == 'chocolate':
        chocolate += 1
      elif item == 'ring':
        ring += 1
      elif item == 'fake':
        fake += random.randint(1, 2)
      elif item == 'bread':
        bread += c
  await updateinc(ctx.author.id, f"storage.Purse", -count)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userpurseq = userstorage['Purse']
  if userpurseq == 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {f"storage.Purse": 1}})
  if not cash == 0:
    await updateinc(ctx.author.id, 'cash', round(cash))
    allitems.append(f"**{round(cash)}** Cash")
  if not candy == 0:
    await updateinc(ctx.author.id, f"storage.Candy", candy)
    allitems.append(f"**{candy}** Candy")
  if not soda == 0:
    await updateinc(ctx.author.id, f"storage.Soda", soda)
    allitems.append(f"**{soda}** Soda")
  if not notebook == 0:
    await updateinc(ctx.author.id, f"storage.Notebook", notebook)
    allitems.append(f"**{notebook}** Notebook")
  if not trash == 0:
    await updateinc(ctx.author.id, f"storage.Trash", trash)
    allitems.append(f"**{trash}** Trash")
  if not chocolate == 0:
    await updateinc(ctx.author.id, f"storage.Chocolate", chocolate)
    allitems.append(f"**{chocolate}** Chocolate")
  if not ring == 0:
    await updateinc(ctx.author.id, f"storage.Diamond Ring", ring)
    allitems.append(f"**{ring}** Diamond Ring")
  if not fake == 0:
    await updateinc(ctx.author.id, f"storage.Fake Necklace", fake)
    allitems.append(f"**{fake}** Fake Necklace")
  await ctx.respond(f"You opened {count} Purse and got:\n"+'\n'.join(allitems))
  await updateset(ctx.author.id,'blocked',False)

async def giftbox(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if count <= 0:
    await ctx.respond("You have to give a valid amount of item to use")
    return
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  if 'Giftbox' not in userstoragelist:
    await ctx.respond("You don't have any Giftbox in your storage!")
    return
  userstorage = user['storage']
  usergiftq = userstorage["Giftbox"]
  if count == 'max':
    count = usergiftq
  if count > usergiftq:
    await ctx.respond("You don't have that much Giftboxes to open!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  allitems = []
  cash = 0
  pet = 0
  candy = 0
  rose = 0
  daisy = 0
  chocolate = 0
  ring = 0
  ribbon = 0
  console = 0
  bread = 0
  for x in range(count):
    item = giftboxr()
    try:
      int(item)
      cash = cash + round(item)
    except:
      c = random.randint(1, 6)
      if item == 'candy':
        candy += c
      elif item == 'pet':
        pet += c
      elif item == 'rose':
        rose += 1
      elif item == 'daisy':
        daisy += c
      elif item == 'chocolate':
        chocolate += c
      elif item == 'ring':
        ring += c
      elif item == 'ribbon':
        ribbon += c
      elif item == 'console':
        console += 1
      elif item == 'bread':
        bread += c
  await updateinc(ctx.author.id, f"storage.Giftbox", -count)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  usergiftq = userstorage['Giftbox']
  if usergiftq == 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {f"storage.Giftbox": 1}})
  if not cash == 0:
    allitems.append(f"**{round(cash)}** Cash")
  if not candy == 0:
    await updateinc(ctx.author.id, f"storage.Candy", candy)
    allitems.append(f"**{candy}** Candy")
  if not pet == 0:
    await updateinc(ctx.author.id, f"storage.Pet Food", pet)
    allitems.append(f"**{pet}** Pet Food")
  if not rose == 0:
    await updateinc(ctx.author.id, f"storage.Rose", rose)
    allitems.append(f"**{rose}** Rose")
  if not daisy == 0:
    await updateinc(ctx.author.id, f"storage.Daisy", daisy)
    allitems.append(f"**{daisy}** Daisy")
  if not chocolate == 0:
    await updateinc(ctx.author.id, f"storage.Chocolate", chocolate)
    allitems.append(f"**{chocolate}** Chocolate")
  if not ring == 0:
    await updateinc(ctx.author.id, f"storage.Diamond Ring", ring)
    allitems.append(f"**{ring}** Diamond Ring")
  if not ribbon == 0:
    await updateinc(ctx.author.id, f"storage.Ribbon", ribbon)
    allitems.append(f"**{ribbon}** Ribbon")
  if not console == 0:
    await updateinc(ctx.author.id, f"storage.Console", console)
    allitems.append(f"**{console}** Console")
  await ctx.respond(f"You opened {count} Giftbox and got:\n"+'\n'.join(allitems))
  await updateset(ctx.author.id,'blocked',False)

  return round(cash)

async def drug_stash(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  if 'Drug Stash' not in userstoragelist:
    await ctx.respond("You don't have any Drug Stash in your storage!")
    return
  userstorage = user['storage']
  userdrugq = userstorage["Drug Stash"]
  if count == 'max':
    count = userdrugq
  if count > userdrugq:
    await ctx.respond("You don't have that much Drug Stashes to open!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  msg = await ctx.respond(f"Unboxing {count} Drug Stashes...")
  allitems = []
  cannabis = 0
  ecstasy = 0
  heroin = 0
  metham = 0
  xanax = 0
  for x in range(count):
    item = drugstash()
    itemq = int(re.split(" ", item)[0])
    item = re.split(" ", item)[1]
    if item == 'cannabis':
      cannabis += itemq
    elif item == 'ecstasy':
      ecstasy += itemq
    elif item == 'heroin':
      heroin += itemq
    elif item == 'metham':
      metham += itemq
    elif item == 'xanax':
      xanax += itemq
  await updateinc(ctx.author.id, f"storage.Drug Stash", -count)
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  userdrugq = userstorage['Drug Stash']
  if userdrugq == 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {f"storage.Drug Stash": 1}})
  if not cannabis == 0:
    await updateinc(ctx.author.id, f"storage.Cannabis", cannabis)
    allitems.append(f"**{cannabis}** Cannabis")
  if not ecstasy == 0:
    await updateinc(ctx.author.id, f"storage.Ecstasy", ecstasy)
    allitems.append(f"**{ecstasy}** Ecstasy")
  if not heroin == 0:
    await updateinc(ctx.author.id, f"storage.Heroin", heroin)
    allitems.append(f"**{heroin}** Heroin")
  if not metham == 0:
    await updateinc(ctx.author.id, f"storage.Methamphetamine", metham)
    allitems.append(f"**{metham}** Methamphetamine")
  if not xanax == 0:
    await updateinc(ctx.author.id, f"storage.Xanax", xanax)
    allitems.append(f"**{xanax}** Xanax")
  await msg.edit(f"You opened {count} Drug Stash and got:\n"+'\n'.join(allitems))
  await updateset(ctx.author.id,'blocked',False)

async def average_car_key(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if count > 100:
    await ctx.respond("You can only use 100 at once maximum!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  if count <= 0:
    await ctx.respond(f"You can only give a positive number")
    await updateset(ctx.author.id, 'blocked', False)
    return
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  if "Average Car Key" not in userstoragelist:
    await ctx.respond("You don't have any average car keys!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  userstorage = user['storage']
  usercarkeyq = userstorage['Average Car Key']
  if count == 'max':
    count = usercarkeyq
  usercarcount = len(user['garage'])
  usergaragec = user['garagec']
  if count > usercarkeyq:
    await ctx.respond("You don't have that much in your storage!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  if count > (usergaragec - usercarcount):
    await ctx.respond("You don't have that much space in your garage to fit those cars!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  msg = await ctx.respond(f"Using {count} Average Car Key <:average_car_key:1358506292725022761>...")

  carlist = []
  carlistnames = []
  total = 0
  for x in range(count):
    user = await finduser(ctx.author.id)
    car = randomaveragecar(user)
    randomgold = random.randint(1,2048)

    if len(user['garage']) == 0:
      carindex = 1
    else:
      carindex = user['garage'][-1]["index"]+1
    carindex += total

    total += 1

    if randomgold == 1696:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': True, 'locked': False, 'damage': random.randint(0, 40)}
    else:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': False, 'locked': False, 'damage': random.randint(0, 40)}
    
    carlist.append(carinfo)

    if randomgold == 1696:
      carlistnames.append(f"{star} Golden " + car)
    else:
      carlistnames.append(car)
  if user['storage']['Average Car Key'] == count:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$unset": {"storage.Average Car Key": 1}})
  else:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$inc": {"storage.Average Car Key": -count}})

  if user['s'] == 63:
    await updateset(ctx.author.id, 's', 64)
  await msg.edit(content=f"You got these cars from {count} Average Car Key <:average_car_key:1358506292725022761>:\n{', '.join(carlistnames)}")
  await updateset(ctx.author.id,'blocked',False)

async def luxury_car_key(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if count > 100:
    await ctx.respond("You can only use 100 at once maximum!")
    return
  await updateset(ctx.author.id, 'blocked', True)
  if count <= 0:
    await ctx.respond(f"You can only give a positive number")
    await updateset(ctx.author.id, 'blocked', False)
    return
  user = await finduser(ctx.author.id)
  userstoragelist = list(user['storage'])
  if "Luxury Car Key" not in userstoragelist:
    await ctx.respond("You don't have any luxury car keys!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  userstorage = user['storage']
  userluxurykeyq = userstorage['Luxury Car Key']
  if count == 'max':
    count = userluxurykeyq
  usercarcount = len(user['garage'])
  usergaragec = user['garagec']
  if count > userluxurykeyq:
    await ctx.respond("You don't have that much in your storage!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  if count > (usergaragec - usercarcount):
    await ctx.respond("You don't have that much space in your garage to fit those cars!")
    await updateset(ctx.author.id, 'blocked', False)
    return
  msg = await ctx.respond(f"Using {count} Luxury Car Key <:luxury_car_key:1358506290237804695>...")

  carlist = []
  carlistnames = []
  total = 0

  for x in range(count):
    await updateinc(ctx.author.id, 'm2', 1)
    user = await finduser(ctx.author.id)
    if user['m2'] == 4:
        car = random.choice(lists.exoticcar)
        await updateset(ctx.author.id, 'm2', 0)
    else:
        car = randomluxurycar(user)
    if car in lists.exoticcar:
        await updateset(ctx.author.id, 'm2', 0)
    randomgold = random.randint(1,2048)

    if len(user['garage']) == 0:
      carindex = 1
    else:
      carindex = user['garage'][-1]["index"]+1
    carindex += total

    total += 1

    if randomgold == 1696:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': True, 'locked': False, 'damage': random.randint(0, 40)}
    else:
      carinfo = {'index': carindex, 'id': randomid(), 'name': car, 'price': lists.carprice[car], 'speed': round(random.uniform(lists.carspeed[car]-10, lists.carspeed[car]+10), 2), 'tuned': 0, 'golden': False, 'locked': False, 'damage': random.randint(0, 40)}
    
    carlist.append(carinfo)
    if randomgold == 1696:
      carlistnames.append(f"{star} Golden " + car)
    else:
      carlistnames.append(car)

  if user['storage']['Luxury Car Key'] == count:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$unset": {"storage.Luxury Car Key": 1}})
  else:
    await cll.update_one({"id": ctx.author.id}, {"$push": {"garage": {"$each": carlist}}, "$inc": {"storage.Luxury Car Key": -count}})

  await msg.edit(content=f"You got these cars from {count} Luxury Car Key <:luxury_car_key:1358506290237804695>:\n{', '.join(carlistnames)}")
  await updateset(ctx.author.id,'blocked',False)

async def weapon_case(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  item = "Weapon Case"
  try:
    userstorage[item]
  except:
    await ctx.respond("You don't have any weapon cases!")
    return
  if count == "max":
    count = userstorage[item]
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if userstorage[item] <= 0:
    await ctx.respond("You don't have any weapon cases!")
  elif userstorage[item] < count:
    await ctx.respond("You don't have that many weapon cases!")
  if count <= 0:
    await ctx.respond("You have to give a positive number idiot")
    return
  await updateinc(ctx.author.id, "storage.Weapon Case", -count)
  msg = await ctx.respond(f"Unboxing {count} Weapon Cases...")
  weapons = []
  for _ in range(count):
    weapons.append(random.choices(sorted(lists.melee+lists.weapon, key=lambda x: lists.item_prices[x], reverse=True), weights=[(x+1)**2*10 for x in range(len(lists.melee+lists.weapon))])[0])

  for weapon in weapons:
    await updateinc(ctx.author.id, f"storage.{weapon}", 1)

  if userstorage[item] - count <= 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {"storage.Weapon Case": 1}})

  await msg.edit(f"You got these weapons from {count} Weapon Cases:\n**{', '.join(weapons)}**")

async def apparel_box(ctx, count: int = 1, *args):
  if await blocked(ctx.author.id) == False:
    return
  user = await finduser(ctx.author.id)
  userstorage = user['storage']
  item = "Apparel Box"
  try:
    userstorage[item]
  except:
    await ctx.respond("You don't have any apparel boxes!")
    return
  if count == "max":
    count = userstorage[item]
  try:
    count = int(count)
  except:
    await ctx.respond("Invalid quantity, it must be a number!")
    return
  if userstorage[item] <= 0:
    await ctx.respond("You don't have any apparel boxes!")
  elif userstorage[item] < count:
    await ctx.respond("You don't have that many apparel boxes!")
  if count <= 0:
    await ctx.respond("You have to give a positive number idiot")
    return
  await updateinc(ctx.author.id, "storage.Apparel Box", -count)
  msg = await ctx.respond(f"Unboxing {count} Apparel Boxes...")
  clothes = []
  for _ in range(count):
    clothes.append(random.choice([clothes for clothes in lists.wearables if clothes not in lists.unobtainable]))

  for c in clothes:
    await updateinc(ctx.author.id, f"storage.{c}", 1)

  if userstorage[item] - count <= 0:
    await cll.update_one({"id": ctx.author.id}, {"$unset": {f"storage.{item}": 1}})

  await msg.edit(f"You got these apparels from {count} Apparel Boxes:\n**{', '.join(clothes)}**")

async def clown(ctx):
  color = random.sample(lists.colors, 3)
  img = Image.open(r"images/clown_bg.png").convert("RGB")

  pen = ImageDraw.Draw(img)
  pen.ellipse((40,40,84,89), fill=color[0])
  pen.ellipse((127,40,171,89), fill=color[1])
  pen.ellipse((215,40,259,89), fill=color[2])

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  view = interclass.Clown(ctx)

  rcolor = random.choice(color)

  embed = discord.Embed(title=f"A kid wants a {rcolor} coloured balloon!", description="Give the kid what they want!", color=discord.Colour.blurple()).set_image(url="attachment://pic.png")
  view.message = await ctx.respond(embed=embed, view=view, file=file)

  await view.wait()

  if view.value == None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]
  elif view.value == 4:
    await updateinc(ctx.author.id, "m0", 1)
    user = await finduser(ctx.author.id)
    try:
      if user["m0"] == 5:
        await updateinc(ctx.author.id, "storage.Clown Hair", 1)
        return [False, "For your impressive dedication to work as a clown despite you are color blind, you've officially earned your clown hair—because some jobs really are just a joke!\n-# Check your storage"]
      else:
        await ctx.respond("Too bad 4 you, go choose a new job")
    except KeyError:
      await ctx.respond("Too bad 4 you, go choose a new job")
      pass
    return [False]
  elif not color[view.value-1] == rcolor:
    await ctx.respond("So.. you are colour blind?")
    return [False]

  return [True]

async def beggar(ctx):
  img = Image.open(r"images/beggar_bg.png").convert("RGB")

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  embed = discord.Embed(title="Where do you want to look?", color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Beggar(ctx)

  view.message = await ctx.respond(embed=embed, view=view, file=file)

  await view.wait()

  if view.value == None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]
  elif view.value == 1:
    r = round(random.random(), 2)
    if r <= 0.1:
      await updateinc(ctx.author.id, "storage.Homework", 1)
      await ctx.respond(f"You found {ctx.author.name}'s' homework! Why did you throw it away?")
      return [False]
    if r <= 0.4:
      count = random.randint(1, 3)
      await updateinc(ctx.author.id, "storage.Bread", count)
      if count == 1:
        await ctx.respond(f"A piece of bread? Perhaps it is still edible")
      else:
        await ctx.respond(f"{count} pieces of bread? Who wastes so much food?")
      return [False]
    elif r <= 0.5:
      count = random.randint(1, 2)
      await updateinc(ctx.author.id, "storage.Trash", count)
      if count == 1:
        await ctx.respond(f"You found some trash! Well there is only a piece of trash in the dumpster")
      else:
        await ctx.respond(f"You found some trash! Well there are {count} pieces of trash in the dumpster")
      return [False]
    else:
      await ctx.respond("You found nothing.. Too bad you have no luck")
      return [False]
    # Insert rare item here
  elif view.value == 2:
    return [True]
  elif view.value == 3:
    r = round(random.random(), 2)
    if r <= 0.02:
      cash = random.randint(1069, 3069)
      await updateinc(ctx.author.id, "cash", cash)
      await ctx.respond(f"A \U0001F4B0 DROPPED from the sky! I guess the fairy tales are real!\nYou opened the bag and counted a total of <:cash:1329017495536930886> {cash} cash!")
      return [False]
      # Insert new title here
    else:
      await ctx.respond("You spent all your time looking at the sky...")
      # Insert new title here
      return [False]

async def business_man(ctx):
  img = Image.open(r"images/business_bg.png").convert("RGB")

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  embed = discord.Embed(title="Stonks", color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Business(ctx)

  view.message = await ctx.respond(embed=embed, view=view, file=file)

  await view.wait()

  if view.value is None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]
  elif view.value == 1:
    r = random.randint(1, 10)
    if r == 1:
      await ctx.respond("You bought more shares and you earned so much money that you fired your boss!\njust kidding, you are still a wage slave")
      cash = random.randint(1001, 4069)
      await updateinc(ctx.author.id, "cash", cash)
      return [True, f"Extra <:cash:1329017495536930886> {cash} cash from the shares!"]
    elif r <= 5:
      await ctx.respond("You bought more shares and it rose!")
      return [True]
    else:
      await ctx.respond("Stonks! Your shares rocketed! ...towards the ground")
      return [False]
  elif view.value == 2:
    r = random.randint(1, 2)
    if r == 1:
      return [True]
    else:
      await ctx.respond("You watched the shares dropping drastically..")
      return [False]
  elif view.value == 3:
    if random.randint(1, 2) == 1:
      cash = random.randint(1, 2)
      await updateinc(ctx.author.id, "cash", cash)
      return [True, f"You sold all the shares before they drop and your boss gave you <:cash:1329017495536930886> {cash} extra cash!"]
    return [True]

async def trash_collector(ctx):
  img = Image.open(r"images/trash_bg.png").convert("RGB")

  r = random.randint(0,5)

  trash = Image.open(rf"images/trash{r}.png").convert("RGBA")

  w, h = img.size
  w0, h0 = trash.size

  img.paste(trash, ((w//2)-(w0//2), h//2-(h0//2)), trash)

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()
  trash.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  embed = discord.Embed(title="Classify the trash!", color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Trash(ctx)
  view.message = await ctx.respond(embed=embed, view=view, file=file)

  await view.wait()

  if view.value is None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]
  elif ((r - 2) if r >= 3 else (r + 1)) != view.value:
    await ctx.respond("Go back to school")
    return [False]
  return [True]

async def chef(ctx):
  img = Image.open(r"images/chef_bg.png").convert("RGB")

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  embed = discord.Embed(title="Pick 3 ingredients", color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Chef(ctx)

  await ctx.respond(embed=embed, view=view, file=file)
  msg = await ctx.interaction.original_response()
  view.message = msg

  await view.wait()

  if view.value is None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]
  elif len(view.ing) != 3:
    await ctx.respond("You have to pick 3 ingredients!")
    return [False]

  cooked_food = [food for food, ingredient in lists.food_ingredients.items() if all([item in ingredient and ingredient[0] in view.ing for item in view.ing])]

  if not len(cooked_food):
    await ctx.respond(f"You ended up with a nasty mess with those ingredients **{', '.join(view.ing)}**\n\nHave a recipe suggestion?\nSuggest it in the official server!")
    return [False]

  cooked_food = random.choice(cooked_food)

  embed.description = f"You successfully made a {cooked_food}!"
  await updateinc(ctx.author.id, "m1", 1)
  user = await finduser(ctx.author.id)
  if user['m1'] == 20:
    await updateinc(ctx.author.id, "storage.Toque", 1)
    return [True, "For the exceptional dishes you've crafted, you’ve been awarded the prestigious toque, a mark of honor for your culinary achievements.\n(Check your storage)"]
  elif user['m1'] == 30:
    await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"titles": "Gourmet"}})
    return [True, "For your outstanding culinary creations, you are now being bestowed with the esteemed title of Gourmet, a recognition reserved for the finest chefs in the art of cuisine.\n-# Check your titles"]
  await msg.edit(embed=embed)
  return [True]

async def kidnapper(ctx):
  img = Image.open(r"images/kidnapper_bg.png").convert("RGB")

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  victim = random.sample(lists.kv, 3)

  embed = discord.Embed(title="Pick your victim", description=f"**On your left side -** {lists.kvc[victim[0]]}\n**Infront of you -** {lists.kvc[victim[1]]}\n**On your right side -** {lists.kvc[victim[2]]}", color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Kidnapper(ctx)
  await ctx.respond(embed=embed, view=view, file=file)
  msg = await ctx.interaction.original_response()
  view.message = msg

  await view.wait()

  if view.value is None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]

  victim = victim[view.value-1]

  embed.title = "What do you plan to do next?"
  embed.description = f"The victim turns out to be a {victim}!"

  view = interclass.Kidnapper2(ctx)
  view.message = await msg.edit(embed=embed, view=view)

  await view.wait()

  if view.value is None:
    await ctx.respond("You took too long to respond goodbye")
    return [False]

  user = await finduser(ctx.author.id)

  chance = lists.kvchance[victim][view.value] + (lists.kvchance[victim][view.value]*(user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))

  if random.random() < chance:
    embed.title = "How are you going to get their cash?"
    embed.description += f"\nYou used **{view.value}** and kidnapped the {victim}!\n{lists.kvsuccess[victim][view.value]}"

    view = interclass.Kidnapper3(ctx)
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()

    if view.value is None:
        await ctx.respond("You took too long to respond goodbye")
        return [False]

    chance = lists.kvchance2[victim][view.value] + (lists.kvchance2[victim][view.value]*(user['stats']['luk']/1000 * (1.5 if user['donor'] == 2 else 1.2 if user['donor'] == 1 else 1)))

    if random.random() < chance:
      embed.title = "Nice!"
      embed.color = color.green()
      embed.description += "\nYou " + (f"called {view.value[5:]}" if view.value.startswith("Call") else f"threatened {view.value[8:]}") + f" and they sent you money!\n{lists.kvsuccess2[victim][view.value]}"

      await msg.edit(embed=embed, view=None)

      return [True]

    else:
      embed.title = "Too bad!"
      embed.color = color.red()
      embed.description += f"\nYou " + (f"called {view.value[5:]}" if view.value.startswith("Call") else f"threatened {view.value[8:]}") + f" but failed!\n{lists.kvfail2[victim][view.value]}"

      await msg.edit(embed=embed, view=None)

      if view.value == "Call a police":
        await updateinc(ctx.author.id, 'm3', 1)
        user = await finduser(ctx.author.id)
        if user['m3'] == 5:
          await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"titles": "0 IQ"}})
          return [False, "For your brilliant strategy of repeatedly calling the cops on yourself, you've earned the prestigious title of '0 IQ'—a true mastermind in the art of self-sabotage!\n(Check your titles)"]
        
        rtime = random.randint(60, 120)
        await ctx.respond(embed=discord.Embed(title="lol", description=f"The police officer caught you and sent you to the jail\nYou are now in jail for {ab(rtime)}!", color=color.red()))
        
        await updateset(ctx.author.id, 'injail', True)
        await updateset(ctx.author.id, 'timer.jail', round(time.time())+rtime)

        return [False]

      return [False]

  else:
    embed.title = "Too bad!"
    embed.color = color.red()
    embed.description += f"\nYou used **{view.value}** but failed!\n{lists.kvfail[victim][view.value]}"

    await msg.edit(embed=embed, view=None)

    return [False]

async def teacher(ctx):
  await ctx.respond("This job is temporarily unavailable due to Discord's limitations!")
  return [False]
  # words = random.sample(lists.teacher_words, 10)
  # word = random.choice(words)

  # html = requests.get(f"https://www.google.com/search?q={word.replace(' ', '+')}&tbm=isch", headers=headers)
  # soup = BeautifulSoup(html.text, 'lxml')
  # all_script_tags = soup.select("script")
  # matched_images_data = "".join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
  # matched_images_data_fix = json.dumps(matched_images_data)
  # matched_images_data_json = json.loads(matched_images_data_fix)
  # matched_google_image_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)
  # matched_google_images_thumbnails = ", ".join(
  #     re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
  #                str(matched_google_image_data))).split(", ")
  # thumbnails = [bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails]
  # removed_matched_google_images_thumbnails = re.sub(
  #     r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))
  # img_link = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)

  # embed = discord.Embed(title=f"What's in the image?", color=color.blurple()).set_image(url=img_link[0])

  # view = interclass.Teacher(ctx, words)

  # view.message = await ctx.respond(embed=embed, view=view)

  # await view.wait()

  # if view.value is None:
  #   await ctx.respond("You took too long to respond goodbye")
  #   return [False]
  # elif view.value != word:
  #   await ctx.respond("You failed your students")
  #   return [False]
  # return [True]

async def gamer(ctx):
  p = simulator.User(1)
  await p.setup()

  # Prim's algorithm maze generation
  for y in range(p.height):
    if y % 2 == 0:
      continue
    for x in range(p.width):
      if x % 2 != 0:
        directions = [1, 2, 3, 4]
        while True:
          direction = random.choice(directions)
          if direction == 1:
            if x != 1 and p.get(x-2, y) == 2:
              p.set(x-1, y, 0)
              break
            directions.remove(direction)
          elif direction == 2:
            if x != p.width-2 and p.get(x+2, y) == 2:
              p.set(x+1, y, 0)
              break
            directions.remove(direction)
          elif direction == 3:
            if y != 1 and p.get(x, y-2) == 2:
              p.set(x, y-1, 0)
              break
            directions.remove(direction)
          elif direction == 4:
            if y != p.height-2 and p.get(x, y+2) == 2:
              p.set(x, y+1, 0)
              break
            directions.remove(direction)

          if directions == []:
            break
        p.set(x, y, 0)

  for i in range(3):
    x, y = random.randrange(1, 10, 2), random.randrange(1, 10, 2)
    while p.get(x, y) != 0:
      x, y = random.randrange(1, 10, 2), random.randrange(1, 10, 2)
    p.set(x, y, 3)
  p.set(1, 1, 1)

  embed = discord.Embed(title="Collect all green squares!", description=p.convert().content, color=color.blurple())
  
  view = interclass.Gamer(ctx)
  await ctx.respond(embed=embed, view=view)
  msg = await ctx.interaction.original_response()
  view.message = msg

  while True:
    await view.wait()
    if view.value is None:
      await ctx.respond("You took too long to respond goodbye")
      return [False]
    elif view.value == "up":
      p.up()
    elif view.value == "left":
      p.left()
    elif view.value == "right":
      p.right()
    elif view.value == "down":
      p.down()

    embed = discord.Embed(title="Collect all green squares!", description=p.convert().content, color=color.blurple())
    view = interclass.Gamer(ctx)
    view.message = await msg.edit(embed=embed, view=view)

    check = []
    for y in range(p.height):
      check.append(3 not in p.grid[y])

    if all(check):
      for child in view.children:
        child.disabled = True
      await view.message.edit(view=view)
      return [True]

async def artist(ctx):

  shapes = ["square", "circle", "triangle up", "triangle down", "diamond"]
  colours = ["red", "green", "blue", "yellow", "purple", "brown", "orange", "black", "white"]

  colour_fill = {
    "red": "#ff2450",
    "green": "lightgreen",
    "blue": "deepskyblue",
    "yellow": "#ffff60",
    "purple": "#e880e5",
    "brown": "#e0795a",
    "orange": "#ff9900",
    "black": "black",
    "white": "white",
  }

  canvas = [[], [], [], [], [], [], [], [], []]

  s, c, m = 0, 0, True

  req = [[random.choice(colours), random.choice(shapes)]]
  for i in range(2):
    temp = [random.choice(colours), random.choice(shapes)]
    while temp in req:
      temp = [random.choice(colours), random.choice(shapes)]
    req.append(temp)


  img = Image.new("RGB", (300, 300), (255, 255, 255))

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  draw = []
  for r in req:
    draw.append(" ".join(r))

  embed = discord.Embed(title="Follow the instructions!", description=f"Draw a {', '.join(draw)}", color=color.blurple()).set_image(url="attachment://pic.png")
  view = interclass.Artist(ctx, shapes[s], colours[c], m)
  await ctx.respond(embed=embed, view=view, file=file)
  msg = await ctx.interaction.original_response()
  view.message = msg

  while True:
    await view.wait()
    if view.value is None:
      await ctx.respond("You took too long to respond goodbye")
      return [False]
    elif view.value == "shape":
      s += 1
      if s > len(shapes)-1:
        s = 0
    elif view.value == "colour":
      c += 1
      if c > len(colours)-1:
        c = 0
    elif view.value == "mode":
      m = not m
    else:
      pen = ImageDraw.Draw(img)
      if m:
        if shapes[s] == "square":
          pen.rectangle([((view.value - (view.value // 3 * 3)) * 100, view.value // 3 *100), ((view.value - (view.value // 3 * 3)) *100+100, view.value // 3 *100+100)], fill=colour_fill[colours[c]])
          canvas[view.value].append([colours[c], shapes[s]])
        elif shapes[s] == "circle":
          pen.ellipse([((view.value - (view.value // 3 * 3)) * 100, view.value // 3 *100), ((view.value - (view.value // 3 * 3)) *100+100, view.value // 3 *100+100)], fill=colour_fill[colours[c]])
          canvas[view.value].append([colours[c], shapes[s]])
        elif shapes[s] == "triangle up":
          pen.regular_polygon((((view.value - (view.value // 3 * 3)) * 100 + 50, view.value // 3 *100 + 50), 50), 3, fill=colour_fill[colours[c]])
          canvas[view.value].append([colours[c], shapes[s]])
        elif shapes[s] == "triangle down":
          pen.regular_polygon((((view.value - (view.value // 3 * 3)) * 100 + 50, view.value // 3 *100 + 50), 50), 3, fill=colour_fill[colours[c]], rotation=180)
          canvas[view.value].append([colours[c], shapes[s]])
        elif shapes[s] == "diamond":
          pen.regular_polygon(((view.value - (view.value // 3 * 3)) * 100 + 50, view.value // 3 *100 + 50, 50), 4, fill=colour_fill[colours[c]], rotation=45)
          canvas[view.value].append([colours[c], shapes[s]])
      else:
        pen.rectangle([((view.value - (view.value // 3 * 3)) * 100, view.value // 3 * 100), ((view.value - (view.value // 3 * 3)) * 100+100, view.value // 3 * 100+100)], fill="white")
        canvas[view.value] = []

    byte = BytesIO()

    img.save(byte, format="png")

    byte.seek(0)

    file = discord.File(byte, "pic.png")

    embed = discord.Embed(title="Follow the instructions!", description=f"Draw a {', '.join(draw)}", color=color.blurple()).set_image(url="attachment://pic.png")
    view = interclass.Artist(ctx, shapes[s], colours[c], m)
    view.message = await msg.edit(embed=embed, view=view, file=file)

    if all([1 if r in [i for c in canvas for i in c] else 0 for r in req]):
      for child in view.children:
        child.disabled = True
      await view.message.edit(view=view)
      return [True]

async def doctor(ctx):
  tools = ["Scalpel", "Suture", "Ultrasound", "Anesthetic", "Antiseptic", "Splint", "Pin", "Gauze", "Defibrillator", "Clamp", "Transfusion", "Ventilator", "Antibiotic", "Mend"]
  # random.shuffle(tools)
  injuries = ["Influenza", "Joint Dislocation", "Broken Leg", "Broken Arm", "Bullet Wound", "Shattered Bones", "Appendicitis", "Liver Infection", "Lung Infection", "Bowel Infection", "Heart Attack", "Major Trauma", "Dyslipidemia", "Brain Tumor"]
  injury = random.choices(injuries, weights=[15, 15, 10, 10, 8, 8, 5, 5, 5, 5, 5, 4, 3, 2], k=1)[0]

  issues = {
    "Influenza": ["Reduce the fever"],
    "Joint Dislocation": ["Relocate the bone"],
    "Broken Leg": ["Fix the broken bones", "fractured bone", "fractured bone"],
    "Broken Arm": ["Fix the broken bones", "fractured bone", "fractured bone"] + ["shattered bone"] * random.randint(0, 1),
    "Bullet Wound": ["Remove the bullets", "bullet wound", "bullet wound"],
    "Shattered Bones": ["Fix the shattered bones"] + ["shattered bone"] * random.randint(2, 3),
    "Appendicitis": ["Remove the appendix"],
    "Liver Infection": ["Remove the infection"],
    "Lung Infection": ["Remove the infection"],
    "Bowel Infection": ["Remove the infection"],
    "Heart Attack": ["Clear the artery"],
    "Major Trauma": ["Heal all physical injuries"] + ["fractured bone"] * random.randint(1, 3) + ["shattered bone"] * random.randint(1, 2),
    "Dyslipidemia": ["Remove excess lipid"],
    "Brain Tumor": ["Remove the tumor"],
  }

  mended = {
    "Influenza": "",
    "Joint Dislocation": "You relocated the bone",
    "Broken Leg": "",
    "Broken Arm": "",
    "Bullet Wound": "You removed a bullet",
    "Shattered Bones": "",
    "Appendicitis": "You removed the appendix",
    "Liver Infection": "You removed the infection part",
    "Lung Infection": "You removed the infection part",
    "Bowel Infection": "You removed the infection part",
    "Heart Attack": "You cleared the heart artery",
    "Major Trauma": "You healed all physical injuries",
    "Dyslipidemia": "You cleared up the blood capillaries",
    "Brain Tumor": "You removed the tumor",
  }

  def blood(pulse):
    if pulse >= 10: # 10>
      return "Strong \U0001f7e2"
    elif pulse >= 6: # 6 7 8 9
      return "Weak \U0001f535"
    elif pulse >= 1: # 1 2 3 4 5
      return "Very Weak \U0001f534"
    else:
      return "No pulse \U0001f534"

  def bleeding(meter):
    if meter >= 9:
      return "Losing blood quickly! \U0001f534"
    elif meter >= 6:
      return "Losing blood \U0001f7e0"
    elif meter >= 3:
      return "Losing blood slowly \U0001f535"
    else:
      return ""

  def sighting(sight):
    if sight >= 6:
      return "You can't see anything! \U0001f534"
    elif sight >= 3:
      return "It's hard to see \U0001f535"
    else:
      return ""

  def cleanliness(hygiene):
    if hygiene >= 6:
      return "Unsanitary \U0001f534"
    elif hygiene >= 3: 
      return "Unsanitized \U0001f535"
    else:
      return "Sanitary \U0001f7e2"

  def sleep(status):
    if status >= 3:
      return "Unconscious \U0001f7e2"
    elif status >= 1:
      return "Going to wake up \U0001f7e1"
    else:
      return "Awake \U0001f534"

  def temperature(temp):
    if temp > 39:
      return str(temp) + "°C \U0001f534"
    elif temp > 37:
      return str(temp) + "°C \U0001f7e1"
    else:
      return str(temp) + "°C \U0001f7e2"

  def oximeter(oxygen):
    if oxygen >= 97:
      return str(oxygen) + "% \U0001f7e2"
    elif oxygen >= 94:
      return str(oxygen) + "% \U0001f7e1"
    else:
      return str(oxygen) + "% \U0001f534"

  def heart(heartbeat):
    if heartbeat >= 5:
      return "The patient's heart has stopped! \U0001f534"
    else:
      return ""

  data = {
    # Progress, Pulse, Temp, Hygiene, Oxygen, Bleed, Sight, Incision, Mend, Hygiene increase, Heartbeat
    "Influenza": ["The patient is suffering from Influenza!", 12, 40.5, 3, 97, 0, 0, 0, 0, 0, 0],
    "Joint Dislocation": ["The patient is waiting for you...", 12, 37, 3, 97, 0, 0, 0, 1, 0, 0],
    "Broken Leg": ["The patient is waiting for you...", 12, 37, 3, 97, 0, 0, 0, 0, 0, 0],
    "Broken Arm": ["The patient is waiting for you...", 12, 37, 3, 97, 0, 0, (1 if "shattered bone" in issues[injury] else 0), 0, 0, 0],
    "Bullet Wound": ["The patient is waiting for you...", 8, 38, 3, 97, 4, 1, 2, 2, 1, 1],
    "Shattered Bones": ["The patient is waiting for you...", 12, 37, 3, 97, 0, 0, 1, 0, 1, 0],
    "Appendicitis": ["The patient is waiting for you...", 8, 39, 3, 97, 0, 1, 3, 1, 1, 1],
    "Liver Infection": ["The patient is waiting for you...", 8, 38.5, 6, 96, 0, 1, 3, 1, 1, 2],
    "Lung Infection": ["The patient is waiting for you...", 8, 38.5, 6, 92, 7, 1, 2, 1, 1, 2],
    "Bowel Infection": ["The patient is waiting for you...", 7, 39, 6, 96, 0, 4, 2, 1, 1, 2],
    "Heart Attack": ["The patient is waiting for you...", 6, 37, 3, 94, 1, 1, 3, 1, 1, 3],
    "Major Trauma": ["The patient is waiting for you...", 4, 39, 7, 95, 12, 6, 3, 1, 1, 3],
    "Dyslipidemia": ["The patient is waiting for you...", 4, 37, 7, 96, 0, 8, 3, 1, 3, 3],
    "Brain Tumor": ["The patient is waiting for you...", 12, 37, 3, 97, 0, 0, 5, 1, 1, 0],
  }
  action = ""
  incision, incision_open, status, progress, pulse, temp, hygiene, oxygen, bleed, sight, increq, mend, hinc, heartbeat = 0, 0, 0, *data[injury]
  disabled = []
  issue = issues[injury][0] + "\n" + ", ".join([str(issues[injury].count(i)) + " " + i + ("s" if issues[injury].count(i) > 1 else "") for i in list(dict.fromkeys(issues[injury][1:]))]) + "\n"

  if progress == "The patient is waiting for you...":
    issue = ""
  if not incision:
    disabled.extend([t for t in ["Suture", "Pin"] if t not in disabled])
  if sight >= 6:
    disabled.extend([t for t in tools if t not in disabled])
    disabled.remove("Gauze")
  if heartbeat >= 5:
    disabled.extend([t for t in tools if t not in disabled])
    disabled.remove("Defibrillator")
  if incision != increq or mend == 0:
    disabled.extend([t for t in ["Mend"] if t not in disabled])
  if progress != "The patient is waiting for you...":
    if "Ultrasound" not in disabled:
      disabled.append("Ultrasound")

  img = Image.open(r"images/doctor_bg.png").convert("RGB")

  byte = BytesIO()

  img.save(byte, format="png")
  img.close()

  byte.seek(0)

  file = discord.File(byte, "pic.png")

  embed = discord.Embed(title=progress, description=issue+f"**{incision} incision"+("s" if incision > 1 else "")+f"**\n**Status:** {sleep(status)}\n**Pulse:** {blood(pulse)}\n**Temperature:** {temperature(temp)}\n**Hygiene:** {cleanliness(hygiene)}\n**Oxygen:** {oximeter(oxygen)}"+('\n' + bleeding(bleed) if bleeding(bleed) != '' else '')+('\n' + sighting(sight) if sighting(sight) != '' else '')+('\n' + heart(heartbeat) if heart(heartbeat) != '' else '')+('\n\n'+action if action != '' else ''), color=color.blurple()).set_image(url="attachment://pic.png")

  view = interclass.Doctor(ctx, tools, disabled)

  await ctx.respond(embed=embed, view=view, file=file)
  msg = await ctx.interaction.original_response()
  view.message = msg

  reason = ""

  while True:
    await view.wait()
    if view.value is None:
      await ctx.respond("You took too long to react and your patient died")
      return [False]
    user = await finduser(ctx.author.id)
    if not random.uniform(0, 100) <= (20 - user['skill']*0.18):
      if view.value == "Scalpel":
        if status == 0:
          reason = "You cut the patient open while they are awake and they died!"
          action = "You cut the patient open and they screamed!"
        elif increq == 0:
          action = "You made an unnecessary incision on the patient!"
          incision += 1
          bleed += 3
          heartbeat += 1
        elif incision == increq:
          action = "You made an extra incision on the patient!"
          incision += 1
          bleed += 3
          heartbeat += 1
        elif progress == "The patient is waiting for you...":
          reason = "You cut the patient open without diagnosing them!"
          action = "You cut the patient without knowing their illness!"
        else:
          action = "You made an incision on the patient..."
          incision += 1
      elif view.value == "Suture":
        if incision == 0:
          action = "You did nothing with the suture because there was no incision"
        else:
          action = "You sutured an incision on the patient..."
          incision -= 1
          bleed -= 2
          if bleed < 0:
            bleed = 0
      elif view.value == "Ultrasound":
        progress = f"The patient is suffering from {injury}!"
        action = f"You used the ultrasound and found out that the patient is suffering from {injury}!"
      elif view.value == "Anesthetic":
        action = "You used an anesthetic and put the patient to sleep"
        status += 15
        if status > 15:
          status = 15
      elif view.value == "Antiseptic":
        action = "You used an antiseptic to sanitize the tools"
        hygiene -= 3
        if hygiene < 0:
          hygiene = 0
      elif view.value == "Splint":
        if issues[injury].count("fractured bone") >= 1:
          action = "You used a splint to splint a fractured bone"
          issues[injury].remove("fractured bone")
        else:
          action = "You used a splint for nothing because there are no fractured bones!"
      elif view.value == "Pin":
        if issues[injury].count("shattered bone") >= 1:
          action = "You used a pin to pin a shattered bone into a fractured bone"
          issues[injury].remove("shattered bone")
          issues[injury].append("fractured bone")
        else:
          action = "You used a splint for nothing because there are no shattered bones!"
      elif view.value == "Gauze":
        action = "You used a gauze sponge to clean up the blood!"
        sight = 0
      elif view.value == "Defibrillator":
        if heartbeat >= 5:
          action = "You used the defibrillator and shocked the patient back to life!"
          heartbeat = 0
        else:
          reason = "The shocked the patient while their heart is beating and they died!"
          action = "You used the defibrillator while their heart is fine!"
      elif view.value == "Clamp":
        action = "You used a clamp to stop the patient from losing blood"
        bleed -= 3
        if bleed < 0:
          bleed = 0
      elif view.value == "Transfusion":
        action = "You transfused some blood to the patient..."
        pulse += 2
        if pulse > 12:
          pulse = 12
      elif view.value == "Ventilator":
        action = "You used the ventilator to help the patient breathe..."
        oxygen += 1
        if oxygen > 97:
          oxygen = 97
      elif view.value == "Antibiotic":
        action = "You used some antibiotics to reduce the patient's fever..."
        temp -= 1
        if temp < 37:
          temp = 37
      elif view.value == "Mend":
        action = mended[injury]
        mend -= 1
        if mend < 0:
          mend = 0
        if issues[injury].count("bullet wound") >= 1:
          issues[injury].remove("bullet wound")
    else:
      action = f"[Skill fail: {20 - user['skill']*0.18}%] You made a mistake!"

    # End action
    if view.value != "Clamp" and view.value != "Transfusion":
      if bleed >= 9:
        pulse -= 3
      elif bleed >= 6:
        pulse -= 2
      elif bleed >= 3:
        pulse -= 1
    if view.value != "Ventilator" and oxygen != 97:
      oxygen -= 1
    if view.value != "Antibiotic" and temp != 37:
      temp += 0.5
    if incision > 0:
      incision_open += 1
    else:
      incision_open = 0
    if incision > 0 and incision_open > 2:
      bleed += 1
    if random.randint(0, 2) == 1:
      heartbeat += 1
      if heartbeat < 5 and random.randint(1, 8) == 1:
        heartbeat = 5
    if view.value != "Anesthetic":
      if status > 0:
        status -= 1
    if view.value != "Antiseptic" and incision > 0:
      hygiene += hinc
      if hygiene >= 6:
        hygiene = 6
    if view.value != "Gauze" and incision > 0:
      if hygiene >= 6:
        sight += 2
      elif hygiene >= 3:
        sight += 1

    if heartbeat >= 8:
      reason = "The patient's heart stopped for too long!"
    elif pulse <= 0:
      reason = "The patient lost too much blood and died!"
    elif oxygen < 90:
      reason = "The patient's brain shut down due to lack of oxygen and died!"
    elif temp >= 42:
      reason = "The fever went too high and your patient died!"

    disabled = []
    issue = issues[injury][0] + "\n" + ", ".join([str(issues[injury].count(i)) + " " + i + ("s" if issues[injury].count(i) > 1 else "") for i in list(dict.fromkeys(issues[injury][1:]))]) + "\n"

    if progress == "The patient is waiting for you...":
      issue = ""
    if not incision:
      disabled.extend([t for t in ["Suture", "Pin"] if t not in disabled])
    if sight >= 6:
      disabled.extend([t for t in tools if t not in disabled])
      disabled.remove("Gauze")
    if heartbeat >= 5:
      disabled.extend([t for t in tools if t not in disabled])
      disabled.remove("Defibrillator")
    if incision != increq or mend == 0:
      disabled.extend([t for t in ["Mend"] if t not in disabled])
    if progress != "The patient is waiting for you...":
      if "Ultrasound" not in disabled:
        disabled.append("Ultrasound")

    embed = discord.Embed(title=progress, description=issue+f"**{incision} incision"+("s" if incision > 1 else "")+f"**\n**Status:** {sleep(status)}\n**Pulse:** {blood(pulse)}\n**Temperature:** {temperature(temp)}\n**Hygiene:** {cleanliness(hygiene)}\n**Oxygen:** {oximeter(oxygen)}"+('\n' + bleeding(bleed) if bleeding(bleed) != '' else '')+('\n' + sighting(sight) if sighting(sight) != '' else '')+('\n' + heart(heartbeat) if heart(heartbeat) != '' else '')+('\n\n'+action if action != '' else ''), color=color.blurple()).set_image(url="attachment://pic.png")

    view = interclass.Doctor(ctx, tools, disabled)

    # Fail
    if reason != "":
      embed.description += f"\nYou failed to save your patient!"
      for child in view.children:
        child.disabled = True
      view.message = await msg.edit(embed=embed, view=view)
      await ctx.respond(reason)
      return [False]
    elif mend == 0 and incision == 0 and temp == 37 and oxygen == 97 and pulse >= 10 and bleed < 3 and heartbeat < 5 and issues[injury].count("fractured bone") == 0 and issues[injury].count("shattered bone") == 0:
      embed.description += "\nYou have successfully cured your patient!"
      for child in view.children:
        child.disabled = True
      view.message = await msg.edit(embed=embed, view=view)
      await updateinc(ctx.author.id, "m4", 1)
      if user['skill'] < 100:
        await updateinc(ctx.author.id, "skill", 1)
      user = await finduser(ctx.author.id)
      if user['m4'] == 20:
        await updateinc(ctx.author.id, "storage.Angel Wings", 1)
        # The Angels of Mercy, having witnessed your unmatched devotion, now entrust you with their most sacred gift, a power reserved for only the most deserving souls...
        return [True, f"Psst, {user['title']}{ctx.author.mention}!\nThe Angels of Mercy have watched in silence, and now, in their enigmatic grace, they bestow upon you their sacred gift...\n(Check your storage)"]
      return [True]
    else:
      view.message = await msg.edit(embed=embed, view=view)

async def lawyer(ctx):
    crimes = ["pickpocketing", "shoplifting", "vehicle theft", "identity theft", "fraudulent", "an assault", "domestic violence", "stalking", "attempted murder", "being an accomplice", "drug dealing", "arson", "a robbery", "a grand larceny", "murder", "terrorism", "serial killing"]
    evidences = ["Security Camera", "Billing Records", "Audio Records", "Registration Data", "Fingerprint", "Witness Testimonial", "DNA Test", "Blood Sample", "Medical Report"]
    crime = random.choice(crimes)

    persuasion = {
        "pickpocketing": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 5,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "shoplifting": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 5,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "vehicle theft": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 5,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "identity theft": {
            "Security Camera": 0,
            "Billing Records": 10,
            "Audio Records": 0,
            "Registration Data": 10,
            "Fingerprint": 0,
            "Witness Testimonial": 5,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "fraudulent": {
            "Security Camera": 0,
            "Billing Records": 10,
            "Audio Records": 0,
            "Registration Data": 10,
            "Fingerprint": 0,
            "Witness Testimonial": 5,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "an assault": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 5,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 5,
            "Medical Report": 0,
        },
        "domestic violence": {
            "Security Camera": 0,
            "Billing Records": 0,
            "Audio Records": 10,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 0,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 10,
        },
        "stalking": {
            "Security Camera": 10,
            "Billing Records": 10,
            "Audio Records": 0,
            "Registration Data": 5,
            "Fingerprint": 0,
            "Witness Testimonial": 5,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "attempted murder": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "being an accomplice": {
            "Security Camera": 10,
            "Billing Records": 5,
            "Audio Records": 5,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 0,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "drug dealing": {
            "Security Camera": 0,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 0,
            "DNA Test": 5,
            "Blood Sample": 0,
            "Medical Report": 10,
        },
        "arson": {
            "Security Camera": 10,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "a robbery": {
            "Security Camera": 0,
            "Billing Records": 10,
            "Audio Records": 5,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 10,
            "DNA Test": 5,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "a grand larceny": {
            "Security Camera": 0,
            "Billing Records": 10,
            "Audio Records": 5,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "murder": {
            "Security Camera": 0,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 10,
            "Witness Testimonial": 5,
            "DNA Test": 10,
            "Blood Sample": 10,
            "Medical Report": 0,
        },
        "terrorism": {
            "Security Camera": 10,
            "Billing Records": 5,
            "Audio Records": 0,
            "Registration Data": 10,
            "Fingerprint": 0,
            "Witness Testimonial": 10,
            "DNA Test": 0,
            "Blood Sample": 0,
            "Medical Report": 0,
        },
        "serial killing": {
            "Security Camera": 0,
            "Billing Records": 0,
            "Audio Records": 0,
            "Registration Data": 0,
            "Fingerprint": 0,
            "Witness Testimonial": 0,
            "DNA Test": 10,
            "Blood Sample": 10,
            "Medical Report": 0,
        },
    }

    reason = {
        "None": "This evidence has nothing to prove the defendant's innocence",
        "Security Camera": "The camera shows no presence of the defendant",
        "Billing Records": "The billing record of the defendant shows no abnormal transactions",
        "Audio Records": "The suspect has a different voice tone compared to the defendant",
        "Registration Data": "The registration data of the defendant shows nothing abnormal",
        "Fingerprint": "The fingerprint does not match with the defendant",
        "Witness Testimonial": "The witness denied the presence of the defendant",
        "DNA Test": "The DNA at the crime scene does not match with the defendant's DNA",
        "Blood Sample": "The blood sample does not match with the defendant's blood",
        "Medical Report": "The defendant's medical report shows all indicators are normal",
    }

    objections = ["Objection Hearsay", "Objection Leading", "Objection Compound", "Objection Lack of Foundation", "Objection Relevance", "Objection Speculation", "Objection Argumentative", "Objection Vague", "Objection Unfair"]
    shirt_colour = random.choice(['blue', 'red', 'green', 'yellow', 'brown', 'purple', 'orange'])
    questions_list = ["It was told that the defendant was present at the crime scene.", "One person claimed their friend said they saw the defendant at the crime scene.", f"You were wearing a {shirt_colour} shirt during the time of incident, right?", "You were in OV City, weren't you?", "Where were you and what did you do?", "Did you see what happened and what happened?", "How many people were around at the scene?", "What was the weather during the time of incident?", "What did you eat before the time of incident?", "Where is your family during the time of incident?", "What do you think the witness saw?", "So you are saying that you are not present at the crime scene?", "Are you sure that you have totally no idea?", "Where were you earlier?", "Why did you make a call?", "The defendant have been into jail for a couple of times before.", "You have a history of many criminal records."]
    questions = {
        "It was told that the defendant was present at the crime scene.": ["Objection Hearsay"],
        "One person claimed their friend said they saw the defendant at the crime scene.": ["Objection Hearsay"],
        f"You were wearing a {shirt_colour} shirt during the time of incident, right?": ["Objection Leading"],
        "You were in OV City, weren't you?": ["Objection Leading"],
        "Where were you and what did you do?": ["Objection Compound", "Objection Vague"],
        "Did you see what happened and what happened?": ["Objection Compound"],
        "How many people were around at the scene?": ["Objection Lack of Foundation"],
        "What was the weather during the time of incident?": ["Objection Lack of Foundation", "Objection Relevance"],
        "What did you eat before the time of incident?": ["Objection Relevance"],
        "Where is your family during the time of incident?": ["Objection Relevance", "Objection Lack of Foundation"],
        "You might have a weapon on you during the time of incident.": ["Objection Speculation"],
        "What do you think the witness saw?": ["Objection Speculation"],
        "So you are saying that you are not present at the crime scene?": ["Objection Argumentative"],
        "Are you sure that you have totally no idea?": ["Objection Argumentative"],
        "Where were you earlier?": ["Objection Vague"],
        "Why did you make a call?": ["Objection Vague"],
        "The defendant have been into jail for a couple of times before.": ["Objection Unfair"],
        "You have a history of many criminal records.": ["Objection Unfair"],
    }
    sustain = {
        "It was told that the defendant was present at the crime scene.": "**Judge:** I sustain the Objection. The evidence was told by somebody else.",
        "One person claimed their friend said they saw the defendant at the crime scene.": "**Judge:** I sustain the Objection. The evidence was heard from someone else.",
        f"You were wearing a {shirt_colour} shirt during the time of incident, right?": f"**Judge:** I sustain the Objection. The question implies that the defendant were wearing a {shirt_colour} shirt.",
        "You were in OV City, weren't you?": "**Judge:** I sustain the Objection. The question implies that the defendant were in OV City.",
        "Where were you and what did you do?": "**Judge:** I sustain the Objection. The question is not specific and there are more than one question in it.",
        "Did you see what happened and what happened?": "**Judge:** I sustain the Objection. There are more than one question in the question.",
        "How many people were around at the scene?": "**Judge:** I sustain the Objection. The defendant doesn't have a firsthand knowledge about the matter.",
        "What was the weather during the time of incident?": "**Judge:** I sustain the Objection. The defendant doesn't have a firsthand knowledge about the matter and the question is irrelevant.",
        "What did you eat before the time of incident?": "**Judge:** I sustain the Objection. The defendant doesn't have a firsthand knowledge about the matter and the question is irrelevant.",
        "Where is your family during the time of incident?": "**Judge:** I sustain the Objection. The question is irrelevant.",
        "You might have a weapon on you during the time of incident.": "**Judge:** I sustain the Objection. Only testify after confirming that it is true.",
        "What do you think the witness saw?": "**Judge:** I sustain the Objection. Only testify after confirming that it is true.",
        "So you are saying that you are not present at the crime scene?": "**Judge:** I sustain the Objection. The question makes an argument.",
        "Are you sure that you have totally no idea?": "**Judge:** I sustain the Objection. The question makes an argument.",
        "Where were you earlier?": "**Judge:** I sustain the Objection. State the specific time instead of stating earlier.",
        "Why did you make a call?": "**Judge:** I sustain the Objection. The question is too ambiguous.",
        "The defendant have been into jail for a couple of times before.": "**Judge:** I sustain the Objection. Been into jail does not imply anything.",
        "You have a history of many criminal records.": "**Judge:** I sustain the Objection. Having history of many criminal records does not imply anything.",
    }

    client = f"Your client was accused of **{crime}** but they are innocent"
    disabled = []
    evidence = []
    points = 0

    img = Image.open(r"images/lawyer_bg.png").convert("RGB")

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    file = discord.File(byte, "pic.png")

    embed = discord.Embed(title="Defend your client!", description=f"{client}\n**Points** {points}\n\nPick the first evidence", color=color.blurple()).set_image(url="attachment://pic.png")

    view = interclass.Lawyer(ctx, evidences, disabled)

    await ctx.respond(embed=embed, view=view, file=file)
    msg = await ctx.interaction.original_response()
    view.message = msg

    first = ""
    second = ""

    for i in range(2):
        await view.wait()
        if view.value is None:
            await ctx.respond("You took too long to respond")
            return [False]
        else:
            evidence.append(view.value)
            points += persuasion[crime][view.value]
            if i == 0:
                first = view.value
                embed.description = f"{client}\n**Points** {points}\n\n**First evidence** {view.value} (+{persuasion[crime][view.value]} Points)\n[{reason[view.value] if persuasion[crime][view.value] > 0 else reason['None']}]\n\nPick the second evidence"
                disabled.append(view.value)

                view = interclass.Lawyer(ctx, evidences, disabled)

                view.message = await msg.edit(embed=embed, view=view)
            elif i == 1:
                second = view.value
                question = random.choice(questions_list)
                questions_list.remove(question)
                embed.description = f"{client}\n**Points** {points}\n\n**First evidence** {first} (+{persuasion[crime][first]} Points)\n\n**Second evidence** {view.value} (+{persuasion[crime][view.value]} Points)\n[{reason[view.value] if persuasion[crime][view.value] > 0 else reason['None']}]"
                embed.add_field(name="**object the plaintiff's testimonial!**", value="**Q1:** " + question)

                view = interclass.Lawyer2(ctx, objections)

                view.message = await msg.edit(embed=embed, view=view)

    for i in range(5):
        await view.wait()
        if view.value is None:
            await ctx.respond("You took too long to respond")
            return [False]
        else:
            embed.fields[0].value += f"\n**[{view.value}]**\n{sustain[question] if view.value in questions[question] else '**Judge:** Overrule. The objection is not suitable. (-5 Points)'}"
            
            if view.value not in questions[question]:
                points -= 5

            embed.description = f"{client}\n**Points** {points}\n\n**First evidence** {first} (+{persuasion[crime][first]} Points)\n**Second evidence** {second} (+{persuasion[crime][second]} Points)"

            question = random.choice(questions_list)
            questions_list.remove(question)

            if i != 4:
                embed.fields[0].value += f"\n\n**Q{i+2}** {question}"
            else:
                embed.fields[0].value += "\n\n**You won the case and proved your client's innocence!**"

            view = interclass.Lawyer2(ctx, objections)

            view.message = await msg.edit(embed=embed, view=view)

        if points <= 0:
            for child in view.children:
                child.disabled = True
            await ctx.respond("Your points are too low and you lost the case!")
            return [False]
    return [True]

async def car_dealer(ctx):
    user = await finduser(ctx.author.id)

    cars = random.sample([car for car in lists.allcars if car not in lists.exclusivecar], k=5)
    wanted_car = random.choice(cars)
    traits = []
    carspeed = lists.carspeed[wanted_car]
    carprice = lists.carprice[wanted_car]
    carrank = getrank(wanted_car)
    if carrank == "Unknown":
      await ctx.bot.get_channel(909716483704238111).send(f"**Error from {ctx.author} ({ctx.author.id})**: Command `{ctx.command}` | `{ctx.selected_options}` | {wanted_car}: Unkown rank")

    lowspeed = ["crawls like it’s carrying bodies", "moves like it’s weighed down by guilt", "slugs along like it's dodging questions"]
    averagespeed = ["rolls just enough to keep up with the street", "moves like it knows when not to rush", "keeps a steady pace—like a man with nothing to prove"]
    highspeed = ["runs like it's late to a heist", "moves quick, like it’s ditching heat", "zips past like a deal gone wrong"]
    fastspeed = ["vanishes before the sirens wail", "flies like it’s got death on its tail", "outruns trouble before it starts"]
    lowprice = ["costs less than a dirty favor", "feels like a bargain from the back alley", "could be had for a lucky dice roll"]
    averageprice = ["won’t empty your stash, but still earns respect", "is affordable, if you know the right guy", "has value without flashing cash"]
    highprice = ["comes with a price tag and a reputation", "makes people think you know someone dangerous", "costs enough to get noticed"]
    expprice = ["reeks of power and blood money", "commands respect just by pulling up", "costs a fortune—like your soul’s in the glovebox"]
    lowrank = ["don’t expect it to turn heads on the street", "ain’t winning style points, that’s for sure", "looks like it’s borrowed from a getaway rookie"]
    averagerank = ["gets the job done without fanfare", "won’t make a scene, but won’t embarrass you either", "blends in like a wise guy in the crowd"]
    highrank = ["rides with class, like it’s seen things", "pulls up with weight, but don’t flaunt it", "tells a story without saying a word"]
    exoticrank = ["ain’t from around here, and that’s the charm", "steals the spotlight like a don at a funeral", "looks like it came with a private island"]
    classicrank = ["carries history in its chrome and silence", "drives like an old oath—never forgotten", "was made when respect meant something"]
    unkrank = ["I don’t care what badge it wears, as long as it gets the job done."]

    intro = random.choice(["I need wheels that", "Bring me something that", "Find a car that", "I'm lookin’ for a ride that"])
    ending = random.choice([", capiche?", ". Make it quick.", ". I don’t ask twice.", ". Make it worth my time.", ". Don’t disappoint me."])

    if carspeed <= 100:
      speeddesc = random.choice(lowspeed)
    elif 100 < carspeed <= 180:
      speeddesc = random.choice(averagespeed)
    elif 150 < carspeed <= 250:
      speeddesc = random.choice(highspeed)
    elif carspeed > 250:
      speeddesc = random.choice(fastspeed)
    if carprice <= 50:
      pricedesc = random.choice(lowprice)
    elif 50 < carprice <= 200:
      pricedesc = random.choice(averageprice)
    elif 200 < carprice <= 1500:
      pricedesc = random.choice(highprice)
    elif carprice > 1500:
      pricedesc = random.choice(expprice)

    rankdesc = ""
    if carrank == "Low":
      rankdesc = random.choice(lowrank)
    elif carrank == "Average":
      rankdesc = random.choice(averagerank)
    elif carrank == "High":
      rankdec = random.choice(highrank)
    elif carrank == "Exotic":
      rankdesc = random.choice(exoticrank)
    elif carrank == "Classic":
      rankdesc = random.choice(classicrank)
    elif carrank == "Unknown":
      rankdesc = random.choice(unkrank)
    else:
      rankdesc = random.choice(unkrank)
      await ctx.bot.get_channel(909716483704238111).send(f"**Error from {ctx.author} ({ctx.author.id})**: Command `{ctx.command}` | `{ctx.selected_options}` | {wanted_car}: {carrank}")


    page = 1

    embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
    embed.set_image(url=lists.carimage[cars[page-1]])
    view = interclass.CarDealer(ctx, ctx.author, page == 1, page == 5)

    await ctx.respond(embed=embed, view=view)

    msg = await ctx.interaction.original_response()
    view.message = msg

    while True:
      await view.wait()
      if view.value is None:
        await ctx.respond("You took too long to pick, your customer left")
        return [False]
      elif view.value == "left":
        page -= 1
      elif view.value == "right":
        page += 1
      elif view.value == "pick":
        common = 0
        selected_car = cars[page-1]
        if carspeed <= 100 and lists.carspeed[selected_car] <= 100:
          common += 1
        elif 100 < carspeed <= 180 and 100 < lists.carspeed[selected_car] <= 180:
          common += 1
        elif 150 < carspeed <= 250 and 150 < lists.carspeed[selected_car] <= 250:
          common += 1
        elif carspeed > 250 and lists.carspeed[selected_car] > 250:
          common += 1
        if carprice <= 50 and lists.carprice[selected_car] <= 50:
          common += 1
        elif 50 < carprice <= 200 and 50 < lists.carprice[selected_car] <= 200:
          common += 1
        elif 200 < carprice <= 1500 and 200 < lists.carprice[selected_car] <= 1500:
          common += 1
        elif carprice > 1500 and lists.carprice[selected_car] > 1500:
          common += 1
        if carrank == "Low" and getrank(selected_car) == "Low":
          common += 1
        elif carrank == "Average" and getrank(selected_car) == "Average":
          common += 1
        elif carrank == "High" and getrank(selected_car) == "High":
          common += 1
        elif carrank == "Exotic" and getrank(selected_car) == "Exotic":
          common += 1
        elif carrank == "Classic" and getrank(selected_car) == "Classic":
          common += 1
        elif carrank == "Unknown":
          common += 1

        if common == 0:
          embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
          embed.set_image(url=lists.carimage[cars[page-1]])
          embed.description += "\n\n**Hoodlum:** That’s a joke, right? Get that heap outta my sight."
          embed.color = color.red()
          await msg.edit(embed=embed)
          return [False]
        elif common == 1:
          embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
          embed.set_image(url=lists.carimage[cars[page-1]])
          embed.description += "\n\n**Hoodlum:** You're gettin' warmer, but this ain’t it, kid."
          embed.color = color.gold()
          await msg.edit(embed=embed)
          return [True, 500]
        elif common == 2:
          embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
          embed.set_image(url=lists.carimage[cars[page-1]])
          embed.description += "\n\n**Hoodlum:** Now we're talkin’. Almost there — but not quite."
          embed.color = color.gold()
          await msg.edit(embed=embed)
          return [True, 1000]
        elif common == 3:
          embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
          embed.set_image(url=lists.carimage[cars[page-1]])
          embed.description += "\n\n**Hoodlum:** That's the one. You’ve got taste — and a future in this business."
          embed.color = color.green()
          await msg.edit(embed=embed)

          await updateinc(ctx.author.id, 'm5', 1)
          
          if 'm5' in user and user['m5'] == 19:
            await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"titles": "<:luxury_car_key:1358506290237804695>"}})
            return [True, "You've been awarded the title <:luxury_car_key:1358506290237804695> for successfully becoming the city's top car dealer. Looks like business is booming."]

          return [True]

      embed = discord.Embed(title="Recommend a car to the hoodlum!", description=f"**Hoodlum:** {intro} {speeddesc} and {pricedesc}, which {rankdesc}{ending}", color=color.blurple())
      embed.set_image(url=lists.carimage[cars[page-1]])
      view = interclass.CarDealer(ctx, ctx.author, page == 1, page == 5)

      await msg.edit(embed=embed, view=view)

def mechanic_img(screws, pinned, screwdriverpos, screwdriverpin):
    img = Image.open(r"images/mechanic_bg.png").convert("RGB")

    if screwdriverpin is False:
      screwdriverimg = Image.open(r"images/mechanic_screwdriver1.png").convert("RGBA")
      img.paste(screwdriverimg, (screwdriverpos, 0), screwdriverimg)
    else:
      screwdriverimg = Image.open(r"images/mechanic_screwdriver.png").convert("RGBA")
      img.paste(screwdriverimg, (screwdriverpos, 10), screwdriverimg)

    screwdriverimg.close()

    for screw in screws:
      screwimg = Image.open(r"images/mechanic_screw.png").convert("RGBA")
      if screw not in pinned:
        img.paste(screwimg, (screw, 224), screwimg)
      else:
        img.paste(screwimg, (screw, 260), screwimg)
      screwimg.close()

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    return byte

async def mechanic(ctx):

    embed = discord.Embed(title="Align the screwdriver with the screws!", color=color.blurple())

    screwdis = [10, 80, 150, 220, 290, 360, 430, 500, 570]
    rotation = 0
    screwdriverpos = screwdis[rotation]+5
    screwdriverpin = False
    screws = random.sample(screwdis, k=3)
    pinned = []
    timeout = 3

    byte = mechanic_img(screws, pinned, screwdriverpos, screwdriverpin)
    file = discord.File(byte, "pic.png")
    embed.set_image(url="attachment://pic.png")

    view = interclass.Mechanic(ctx, "Screw!", None, timeout)
    await ctx.respond(embed=embed, view=view, file=file)
    view.message = msg = await ctx.interaction.original_response()

    total = 0
    failed = False

    while True:
      if total == 27:
        break
      await view.wait()

      if view.value is True:
        embed = discord.Embed(title="Align the screwdriver with the screws!", color=color.blurple())

        screwdriverpin = True
        if screwdriverpos-5 in screws:
          pinned.append(screwdriverpos-5)
        else:
          failed = True

        byte = mechanic_img(screws, pinned, screwdriverpos, screwdriverpin)
        file = discord.File(byte, "pic.png")
        embed.set_image(url="attachment://pic.png")

        await msg.edit(embed=embed, view=None, file=file, attachments=[])

      elif view.value is None:
        total += 1
        embed = discord.Embed(title="Align the screwdriver with the screws!", color=color.blurple())

        screwdriverpin = False
        rotation += 1
        screwdriverpos = screwdis[rotation]+5
        if rotation == len(screwdis)-1:
          rotation = 0
          screwdis = screwdis[::-1]

        byte = mechanic_img(screws, pinned, screwdriverpos, screwdriverpin)
        file = discord.File(byte, "pic.png")
        embed.set_image(url="attachment://pic.png")

        view = interclass.Mechanic(ctx, "Screw!", None, timeout)
        view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])
        continue

      if screwdriverpin is True:
        await asyncio.sleep(2)
        embed = discord.Embed(title="Align the screwdriver with the screws!", color=color.blurple())

        screwdriverpin = False

        byte = mechanic_img(screws, pinned, screwdriverpos, screwdriverpin)
        file = discord.File(byte, "pic.png")
        embed.set_image(url="attachment://pic.png")

        await msg.edit(embed=embed, view=None, file=file, attachments=[])

        if len(pinned) == 3 or failed is True:
          break

        await asyncio.sleep(2)

        total += 1
        embed = discord.Embed(title="Align the screwdriver with the screws!", color=color.blurple())

        rotation += 1
        screwdriverpos = screwdis[rotation]+5
        if rotation == len(screwdis)-1:
          rotation = 0
          screwdis = screwdis[::-1]

        byte = mechanic_img(screws, pinned, screwdriverpos, screwdriverpin)
        file = discord.File(byte, "pic.png")
        embed.set_image(url="attachment://pic.png")

        view = interclass.Mechanic(ctx, "Screw!", None, timeout)
        view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])
        continue

    if len(pinned) == 3:
      return [True]
    elif len(pinned) == 2:
      return [True, 1000]
    elif len(pinned) == 1:
      return [True, 500]
    else:
      return [False]

def farmer_img(tiles):
    img = Image.new('RGBA', (676, 676), (255, 0, 0, 0))

    column = 0
    row = 0
    for tile in tiles:
        if column == 3:
            column = 0
            row += 1
        tileimg = Image.open(rf"images/farmer_tile{tile}.png").convert("RGBA")
        img.paste(tileimg, (50+(column*192), 50+(row*192)), tileimg)
        column += 1
        tileimg.close()

    grassimg = Image.open(r"images/farmer_grass.png").convert("RGBA")
    img.paste(grassimg, (0, 0), grassimg)

    byte = BytesIO()

    img.save(byte, format="png")
    grassimg.close()
    img.close()

    byte.seek(0)

    return byte

async def farmer(ctx):
    action = 9
    harvest = 0
    embed = discord.Embed(title=f"{ctx.author.name}'s Farm", description=f"**Energy left:** {action}",color=color.blurple())

    user = await finduser(ctx.author.id)
    if 'farmer' in user:
        tiles = user['farmer']
        tiles = [tile-1 if tile == 8 else tile+1 if tile % 2 == 0 and tile != 0 and tile != 8 else tile for tile in tiles]
    else:
        tiles = [0,0,0, 0,0,0, 0,0,0]

    byte = farmer_img(tiles)
    file = discord.File(byte, "pic.png")
    embed.set_image(url="attachment://pic.png")

    view = interclass.Farmer(ctx, ctx.author, tiles)
    await ctx.respond(embed=embed, view=view, file=file)
    view.message = msg = await ctx.interaction.original_response()

    while action:
        await view.wait()

        if view.value is None:
          await ctx.respond("You took too long to respond")
          await updateset(ctx.author.id, 'farmer', tiles)
          return [False]

        action -= 1

        if tiles[view.value] == 7 or tiles[view.value] == 8:
          tiles[view.value] = 0
          harvest += 1
          lastaction = "You harvested your crop!"
        else:
          if tiles[view.value] % 2 == 0 and tiles[view.value] != 0:
            tiles[view.value] += 2
            lastaction = "You fertilized your crop.."
          else:
            tiles[view.value] += 1
            lastaction = "You watered your crop.."

        byte = farmer_img(tiles)
        file = discord.File(byte, "pic.png")
        embed.set_image(url="attachment://pic.png")

        if tiles[view.value] == 1:
          lastaction = "You planted some carrot seeds.."
          

        embed.description = f"**Energy left:** {action}\n{lastaction}"

        view = interclass.Farmer(ctx, ctx.author, tiles)
        view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])
    
    await updateset(ctx.author.id, 'farmer', tiles)
    return [True, 1000 + (harvest*1000)]

async def fencer(ctx):
    await ctx.respond("This job is still under development!")
    return [False]

async def racer(ctx):
    await ctx.respond("This job is still under development!")
    return [False]

tutembeds = [
    ["What is OV about?", "❧ Become a member of the mafia in the OV City!\n❧ Commit crimes, collect cars, race and attack with other users!\n❧ Click the next button to continue!\n\nUseful resources\n__[**Join our official server here!**](https://discord.gg/bBeCcuwE95)__\n__[**Invite the bot to your server!**](https://discord.com/api/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&redirect_uri=https%3A%2F%2Fov-bot.herokuapp.com%2F&scope=bot%20applications.commands)__\n__[**Check out our official website!**](https://ov-bot.up.railway.app/)__"],
    ["Preface", "❧ The following tutorial shows you the basics, and the story command guides you interactively\n\n❧ Use the story command if you are not a reading kind of person!\n\n❧ **Only '/help' can be used in DMs**"],
    ["Commands I", "❧ You can check a list of commands by typing `/help`\n❧ There are a total of 6 different command categories: **Main commands, City commands, Crime commands, Car commands, Fun commands and Other commands**\n❧ **Note to those who doesn't know**, you can scroll in the selection menu!"],
    ["Commands II", "❧ To understand what a command does, type `/help [command name]`\n❧ In the help menu, text wrapped in `<>` or `[]` such as `[command name]` are parameters you can input\n❧ For example typing `/help help` shows a description of the `help` command"],
    ["Currency", "❧ The main currency in OV City is simply called cash, yes CASH, along with this symbol <:cash:1329017495536930886>\n❧ Tokens \U0001fa99, which is used to buy special items that wasn't intended to be bought"],
    ["Crimes", "❧ Crime commands are the primary way to get cash, including tokens\n❧ Type `/help` and pick 'Crime commands' to check a list of available crime commands"],
    ["Cars I | Are you a fan of cars?", "❧ Cars are quite the big cheese in OV City\n❧ You can search for existing cars by typing `/car <car_name>`, it can be any car that exists in real life, for example typing `/car lamborghini gallardo`, or just `/car gallardo`\n❧ Cars can be used for racing or as a collection to show off"],
    ["Shop", "❧ Everything that is buyable can be found in the city shop\n❧ You can access the shop by typing `/shop`"],
    ["Property I | Home sweet home", "❧ You can purchase a real estate using the `/property <property ID>` command\n❧ List of properties can be found using the `/estate` command"],
    ["Balance", "❧ You can check your balance by typing `/cash`\n❧ Stash is where you can safely keep your cash from losing it when dying or getting attacked\n❧ Stash capacity will increase as you purchase a better property"],
    ["Stash", "❧ Beware that users can cooperate and commit larceny on your stash, but there's only a tiny chance it will succeed\n❧ Stash capacity can also be increased using safes, safe is an item you can obtain from committing crimes or voting for the bot"],
    ["End of the basic tutorial", "❧ It is strongly recommended to continue using the story command!\n\n❧ The advanced tutorial shows additional features that can be explored throughout normal gameplay"],
    ["Jail & Hospital | Your second home", "❧ Getting into jail and hospital happens very often\n❧ You can use a bribe to release yourself from the jail immediately, or else you can opt to wait for 3-15 minutes (Scales with level) until you get released from the jail\n❧ Same goes to hospital, but you have to use a medical kit instead\n❧ Bribes and Medical Kits can be found while looking for cash or claiming your daily rewards using the command `/daily`"],
    ["Garage", "❧ This is where all your cars will be parked, to see cars you own simply type `/garage`\n❧ Garage have a maximum capacity, you cannot steal anymore cars if your garage is full\n❧ You can upgrade your garage using the command `/upgarage`\n❧ Each garage upgrade cost <:cash:1329017495536930886> 50 more than the previous upgrade, starting from <:cash:1329017495536930886> 50\n\n❧ In the garage menu you will see your cars listed with numbers on the left side, they are called car IDs\n❧ On the right side there are overall rating, which is explained on the next page"],
    ["Cars II", "❧ Yes, more about cars, cars can be classified into 6 different ranks\n❧ The ranks are low, average, high, exotic, classic and exclusive\n❧ Cars such as Ford Transit are considered low rank, while Lamborghini Gallardo is considered high rank\n❧ Cars are collectables, you can try to get one from stealing using the `/theft` command\n❧ All cars have an average speed, cars you steal will slightly differ from the avearge speed based on your luck\n❧ To check a car you own, just simply type `/mycar <car ID>`\n❧ Overall rating is a comparison of your car's speed to the car's average speed"],
    ["Attack | Smash other players!", "❧ You can attack a NPC or other users using the attack command\n❧ Increase your stats to get better in fighting\n❧ You can increase them by training using the `/train` command\n❧ Your statistics can be seen using the `/stats` command\n❧ There are four fighting statistics: Strength, Defense, Speed and Dexterity\n❧ Type `/train info` to see how they can help you in fighting"],
    ["Racing | Don't crash your car!", "❧ You can race with NPCs or another user, and you can place bets with another user\n❧ Before racing you need to drive a car, you can do that by typing `/drive <car ID>`\n❧ Winning a race will get you some cash and tokens, but you will lose some cash when losing\n❧ There's an extremely tiny chance that you will crash your car while racing, so don't drive a precious car to race if you don't have enough cash to repair it!"],
    ["Storage | Rats!", "❧ All of your items are stored here\n❧ Check the information of an item using the command `/item <item name>`\n❧ Some items can be used, try using them by typing `/use <item name>`"],
    ["Tuning | Create fireworks!", "❧ Is your car too slow but you love how it looks? Well, not a problem! Tune your car by typing `/tune <car ID>`\n❧ Each tune costs <:cash:1329017495536930886> 50\n❧ But beware! There is a chance your car will explode everytime you tune your car, the chances gets higher the more you tune it"],
    ["Golden Cars | Shiny!", "❧ There is a tiny probability the car you steal will turn out to be a golden car\n❧ Golden cars usually have **\u2B50 Golden** at the front of the car name\n❧ You can try searching the golden form of a specific car, such as `/car golden transit`\n❧ Oh, you don't know what golden cars are used for? Flexing of course!"],
    ["Property II", "❧ A better property increases your stash capacity\n❧ A better property also decreases the succeeding chance of other users committing larceny on you\n❧ Property also allows you to gain more statistic when training"],
    ["Death | You won't like it", "❧ Dying removes all the cash from your pocket, but not your stash!\n❧ So having a large stash is super useful\n❧ You can prevent money loss by purchasing insurance from the shop by typing `/shop`\n❧ Upgrade your insurance to decrease money loss from dying!"],
    ["Friends | Hope you have some..", "❧ You can give items to your friends using the command `/giveitem`\n❧ For transferring cash you can use the command `/givecash`\n❧ What about cars? You can transfer cars using the command `/givecar`"],
    ["Reputation | Are you trustworthy?", "❧ You can send people reputation points if you think they are trustworthy!\n❧ Reputation points usually shows if you are trustworthy and it's useful for trading with another user\n❧ To check your own reputation points, type `/reputation`\n❧ To give someone reputation points, you can type `/reputation <user>`"],
    ["Casino | Feed your gambling addicts", "❧ There are couple casino games, type `/casino` to check them\n❧ For each game you can bet a minimum amount of <:cash:1329017495536930886> 10 up to a maximum amount of <:cash:1329017495536930886> 5000\n❧ Games such as russian roulette and blackjack can be played with another user, and you can bet cash with them too!\n❧ Note there's a 5% tax when gambling with another user just like transferring cash"],
    ["Finally | What now?", "❧ You have successfully completed the tutorial! Use the story command to continue playing!"]
]

async def tutorial(ctx):
    img = Image.open(r"images/tutorial.png").convert("RGB")

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    file = discord.File(byte, "pic.png")

    page = 1
    maxpage = len(tutembeds)
    msg = None

    while True:
        embed = discord.Embed(title = ctx.author.name + "#" + ctx.author.discriminator + " Welcome to OV City!", description="This tutorial shows you the basics", color = color.green()).add_field(name=tutembeds[page-1][0], value=tutembeds[page-1][1], inline=False).set_thumbnail(url = ctx.author.display_avatar.url).set_footer(text = "Tutorial").set_image(url="attachment://pic.png")

        view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage, timeout=300)

        try:
            view.message = await msg.edit(embed=embed, view=view)
        except:
            await ctx.respond(embed=embed, view=view, file=file)
            msg = await ctx.interaction.original_response()
            view.message = msg

        await view.wait()

        if view.value is None:
            return
        elif view.value == "left":
            page -= 1
        elif view.value == "right":
            page += 1

async def npc(name):
    img = Image.open(rf"images/{name}.png")

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    file = discord.File(byte, "npc.png")

    return file

async def getimg(name):
    img = Image.open(rf"images/{name}.png")

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    file = discord.File(byte, "pic.png")

    return file

async def storyimg(s):
    img = Image.open(rf"images/story{s}.png")

    byte = BytesIO()

    img.save(byte, format="png")
    img.close()

    byte.seek(0)

    file = discord.File(byte, "story.png")

    return file

async def story0(ctx, user, msg = None):

    embed = discord.Embed(title="Prologue", description="Your eyes flutter open, a dull ache throbbing in your skull as you regain consciousness from an impact you don’t recall. Dim light spills into the narrow alley around you, the air thick with the scent of rain and decay.", color=color.blurple())
    file = await storyimg("0")
    embed.set_image(url="attachment://story.png")
    view = interclass.Story(ctx, "...")
    if msg is None:
        await ctx.respond(embed=embed, view=view, file=file)
        msg = await ctx.interaction.original_response()
        view.message = msg
    else:
        view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

    await view.wait()
    if view.value is None:
        return None

    embed.description += f"\n\nYou struggle to rise, limbs trembling with exhaustion. A towering figure looms over you, wrapped in a khaki coat, a black fedora casting his face in shadow, a menacing silhouette in the dim light."
    file = await storyimg("0a")
    embed.set_image(url="attachment://story.png")
    view = interclass.Story(ctx, "...")
    view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

    await view.wait()
    if view.value is None:
        return None

    embed.description += "\n\n**Vince \"The Fixer\" Montello**, the figure introduces himself, a grizzled former mafia consigliere with a knack for spotting potential. Vince, half-impressed and half-bemused, decides to make you his protégé."

    view = interclass.Story(ctx, "...")
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description = "**Vince:** You look like you’ve had better days. Lucky for you, I’m feeling generous. Stick with me, kid, and I’ll teach you how to turn this dump into your playground. First lesson: never stay down. Now, what’s your name?"
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    view = interclass.Story(ctx, f"{ctx.author.name}")
    view.message = await msg.edit(embed=embed, view=view, file=file)

    await view.wait()
    if view.value is None:
        return None

    embed.description += f"\n\n**You:** {ctx.author.name}\n\n**Vince:** Alright, {ctx.author.name}, let’s get started. The mafia life ain’t for the faint-hearted, but follow my lead, and you’ll go from zero to hero."
    view = interclass.Story(ctx, "Alright")
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.title = "Chapter 1: Welcome to the Family"
    embed.description = "**Vince:** Lesson one: money makes the world go ‘round. If you ain’t got cash, you ain’t got options. Start by looking around—there’s treasure in trash if you know where to look."
    view = interclass.Story(ctx, "...")
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 1:** Use **/search** to find cash.\n> **Vince:** Dig deep, kid. Sometimes it’s a goldmine, sometimes it’s… well, a gum wrapper. Let’s see what you’ve got."
    # file = await npc("vince")
    # embed.set_thumbnail(url="attachment://npc.png")
    # file2 = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, files=[file, file2], view=None, attachments=[])

    await updateset(ctx.author.id, "s", 1)
    return msg

async def story1(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 1:** Use **/search** to find cash.\n> **Vince:** Dig deep, kid. Sometimes it’s a goldmine, sometimes it’s… well, a gum wrapper. Let’s see what you’ve got.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story2(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** Not bad for your first score. Now, let’s move on to bigger fish: stealing a car.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 2:** Use **/theft** to steal a vehicle.\n> **Vince:** A decent ride can take you places—and fill your pockets. Pick one and make it yours, come find me after. Just don’t scratch the paint."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 3)

    return msg

async def story3(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 2:** Use **/theft** to steal a vehicle.\n> **Vince:** A decent ride can take you places—and fill your pockets. Pick one and make it yours, come find me after. Just don’t scratch the paint.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story4(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** Good job on that first car! Every car you steal will go into your garage.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 3:** Use **/garage** to view cars.\n> **Vince:** Welcome to your garage. Think of it as your trophy case for all the rides you ‘borrow’ permanently. Can you see the number on the left side of your car in your garage? It's your car's ID, used to identify your car."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 5)

    return msg

async def story5(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 3:** Use **/garage** to view cars.\n> **Vince:** Welcome to your garage. Think of it as your trophy case for all the rides you ‘borrow’ permanently. Can you see the number on the left side of your car in your garage? It's your car's ID, used to identify your car.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story6(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 4:** Use **/mycar <car ID>** to inspect a car. For example `/mycar 1`\n> **Vince:** Every car’s got stats: speed, value, and tuning potential. Knowledge is power—remember that. The base price is the money you can get for selling it. The speed section is your car's speed, it slightly differs from the average speed of that car, you can check the average speed of that car by typing `/car <car name>`.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 7)

    return None

async def story7(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 4:** Use **/mycar <car ID>** to inspect a car. For example `/mycar 1`\n> **Vince:** Every car’s got stats: speed, value, and tuning potential. Knowledge is power—remember that. The base price is the money you can get for selling it. The speed section is your car's speed, it slightly differs from the average speed of that car, you can check the average speed of that car by typing `/car <car name>`.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story8(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** One car isn’t enough for someone with ambition. Let’s make it two.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 5:** Use **/theft** to steal a second car.\n> **Vince:** Good, now you’re building your empire."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 9)

    return msg

async def story9(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 5:** Use **/theft** to steal a second car.\n> **Vince:** Good, now you’re building your empire.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story10(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 6:** Use **/sellcar <car ID>** to sell one of the cars.\n> **Vince:** Time to cash in. No point holding onto something that’s better off paying your bills.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 11)

    return None

async def story11(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 6:** Use **/sellcar <car ID>** to sell one of the cars.\n> **Vince:** Time to cash in. No point holding onto something that’s better off paying your bills.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story12(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** Want to make your car faster? You can tune it up. Spend some cash, and your ride might fly—or, well, it might explode if you’re unlucky.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 7:** Use **/tune** to tune a car.\n> **Vince:** Careful, kid. The faster the car, the higher the stakes. But hey, fortune favors the bold."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 13)

    return msg

async def story13(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 7:** Use **/tune <car ID>** to tune a car.\n> **Vince:** Careful, kid. The faster the car, the higher the stakes. But hey, fortune favors the bold.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story14(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** Now that you’ve got a ride, it’s time to hit the streets. Let’s see you take it for a spin.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 8:** Use **/drive** to start driving a car.\n> **Vince:** Nice wheels, kid. Now let’s see how you handle the heat."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 15)

    return msg

async def story15(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 8:** Use **/drive <car ID>** to start driving a car.\n> **Vince:** Nice wheels, kid. Now let’s see how you handle the heat.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story16(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 9:** Use **/race** to participate in a race.\n> **Vince:** Racing’s a good way to make a name for yourself. Show them what you’ve got!", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 17)

    return None

async def story17(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 9:** Use **/race** to participate in a race.\n> **Vince:** Racing’s a good way to make a name for yourself. Show them what you’ve got!", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story18(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Vince:** Now, here’s a little bonus. You can claim daily rewards just for being consistent.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 10:** Use **/daily** to claim a daily bonus.\n> **Vince:** You can claim this once every 20 hours. Consider it a little encouragement to keep hustling."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)
    
    await updateset(ctx.author.id, "s", 19)

    return msg

async def story19(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**Task 10:** Use **/daily** to claim a daily bonus.\n> **Vince:** You can claim this once every 20 hours. Consider it a little encouragement to keep hustling.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story20(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 1: Welcome to the Family", description="**End of Chapter Reward:** Vince tosses you <:cash:1329017495536930886> 500 cash.\n\n**Vince:** Not bad, rookie. Let’s see if you’re ready for the next level.", color=color.blurple())
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": 500}, "$set": {'s': 21}})
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "What's next?")
    view.message = msg = await ctx.respond(embed=embed, view=view, file=file)

    await view.wait()
    if view.value is None:
        return None

    embed.title = "Chapter 2: Earning Your Stripes"
    embed.description = "**Vince:** Alright, kid. You’ve got the basics down, but surviving this world means more than fast cars and loose cash. It’s time to toughen you up and give you the tools to defend yourself—and make a real name out there."
    view = interclass.Story(ctx, "...")
    view.message = msg = await msg.edit(embed=embed, view=view)
    
    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 1:** Use **/shop** to browse weapons.> **Vince:** Every good mafioso needs a weapon they can rely on. You never know when someone will try to mess with you—or when you’ll need to mess with someone else. Head to the shop and scope out the selection."
    # file = await npc("vince")
    # embed.set_thumbnail(url="attachment://npc.png")
    # file2 = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")

    # await msg.edit(embed=embed, view=None, files=[file, file2], attachments=[])
    await updateset(ctx.author.id, "s", 21)

    return msg

async def story21(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 1:** Use **/shop** to browse weapons.\n> **Vince:** Every good mafioso needs a weapon they can rely on. You never know when someone will try to mess with you—or when you’ll need to mess with someone else. Head to the shop and scope out the selection.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story22(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 2:** Use **/buy baseball bat** to purchase the weapon.\n> **Vince:** See that bat? Classic, effective, and it gets the job done. Buy it. Trust me, you’ll be thankful when things get rough.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 23)

    return None

async def story23(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 2:** Use **/buy baseball bat** to purchase the weapon.\n> **Vince:** See that bat? Classic, effective, and it gets the job done. Buy it. Trust me, you’ll be thankful when things get rough.", color=color.blurple())
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story24(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 3:** Use **/storage** to view items.\n> **Vince:** Now that you’ve got your bat, let’s take inventory. Everything you own is kept in your storage. Knowing what you’ve got can mean the difference between life and death. Check it out.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 25)

    return None

async def story25(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 3:** Use **/storage** to view items.\n> **Vince:** Now that you’ve got your bat, let’s take inventory. Everything you own is kept in your storage. Knowing what you’ve got can mean the difference between life and death. Check it out.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story26(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 4:** Use **/equip baseball bat** to equip the bat.\n> **Vince:** What’s the point of having a weapon if you don’t use it? Equip that bat so you’re ready for action. No one will take you seriously if you’re walking around empty-handed.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])
    await updateset(ctx.author.id, "s", 27)

    return None

async def story27(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 4:** Use **/equip baseball bat** to equip the bat.\n> **Vince:** What’s the point of having a weapon if you don’t use it? Equip that bat so you’re ready for action. No one will take you seriously if you’re walking around empty-handed.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story28(ctx, user, msg = None):
    if user['lvl'] < 5:
      embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Vince:** What are you still doing here? Go work the streets! I don’t have any more use for you until you reach level 5.", color=color.blurple())

      file = await npc("vince")
      embed.set_thumbnail(url="attachment://npc.png")

      await ctx.respond(embed=embed, file=file)

      return None
    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 5:** Use **/attack** and **mug** a random hoodlum.\n> **Vince:** You’ve got the tools, now show me you’ve got the guts. See that guy over there? He looks like he’s got more cash than sense. Go teach him a lesson and take what’s yours.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])
    await updateset(ctx.author.id, "s", 29)

    return None

async def story29(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 5:** Use **/attack** and **mug** a random hoodlum.\n> **Vince:** You’ve got the tools, now show me you’ve got the guts. See that guy over there? He looks like he’s got more cash than sense. Go teach him a lesson and take what’s yours.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story30(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 6:** Use **/estate** to purchase a mattress. (You can skip this if you already own a better property)\n> **Vince:** Nice work, but carrying your cash around is a rookie mistake. You need a place to stash your earnings. Buy a mattress—it’s not fancy, but it’s your first step.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 31)

    return None

async def story31(ctx, user, msg = None):

    if user['property'] >= 10:
      await updateset(ctx.author.id, 's', 32)
      return msg

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 6:** Use **/estate** to purchase a mattress. (You can skip this if you already own a better property)\n> **Vince:** Nice work, but carrying your cash around is a rookie mistake. You need a place to stash your earnings. Buy a mattress—it’s not fancy, but it’s your first step.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story32(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 7:** Use **/deposit 100** to deposit 100 cash.\n> **Vince:** Smart. Keeping your cash in a stash means it’s safe from thieves. Put some away now, and you’ll sleep better tonight.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    await updateset(ctx.author.id, "s", 33)

    return None

async def story33(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 7:** Use **/deposit 100** to deposit 100 cash.\n> **Vince:** Smart. Keeping your cash in a stash means it’s safe from thieves. Put some away now, and you’ll sleep better tonight.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    await ctx.respond(embed=embed, files=[file, file2])

    return None

async def story34(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Reward:** Vince hands you denim shorts, a plain tee, and black flip-flops.\n**Vince:** Look at you, moving up in the world. Here’s a little something to help you fit in with the locals. Throw these on and take a look at yourself.", color=color.blurple())

    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Denim Shorts": 1, "storage.Plain Tee": 1, "storage.Black Flip-flops": 1}, "$set": {'s': 35}})

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "Thanks!")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 10:** Use **/daily** to claim a daily bonus.\n> **Vince:** You can claim this once every 20 hours. Consider it a little encouragement to keep hustling."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)

    return msg

async def story35(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 8:** Use **/equip shorts**, **/equip plain tee**, **/equip black flip-flops** to wear the clothes and **/profile** to view your character.\n> **Vince:** Now you look like you belong. Check yourself out—it’s good to know the face everyone else will see.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story36(ctx, user, msg = None):
    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 9:** Reach level 10.\n> **Vince:** You’re climbing the ladder, kid. Reaching level 10 is no small feat. By now, you’ve probably been in a few scrapes—maybe even jail or the hospital. If not, consider yourself lucky.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 37)
    return None

async def story37(ctx, user, msg = None):
    if user['lvl'] < 10:
      embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Task 9:** Reach level 10.\n> **Vince:** You’re climbing the ladder, kid. Reaching level 10 is no small feat. By now, you’ve probably been in a few scrapes—maybe even jail or the hospital. If not, consider yourself lucky.", color=color.blurple())

      file = await npc("vince")
      embed.set_thumbnail(url="attachment://npc.png")

      file2 = await getimg("beggar_bg")
      embed.set_image(url="attachment://pic.png")

      if msg is None:
        await ctx.respond(embed=embed, files=[file, file2])
      else:
        await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

      return None
    
    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**Reward:** 2 Bribes and 2 Medical Kits.\n> **Vince:** Bribes get you out of jail, and medical kits patch you up when you’re hurt. Use them wisely—you never know when you’ll need them.", color=color.blurple())

    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Bribe": 2, "storage.Medical Kit": 2}, "$set": {'s': 38}})

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")


    view = interclass.Story(ctx, "...")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    return msg

async def story38(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 2: Earning Your Stripes", description="**End of Chapter Reward:** a leather jacket, and a pair of shades.\n**Vince:** Congrats, kid. You’ve proven you’ve got the grit and smarts to survive. But don’t get comfortable—the real challenge is just beginning.", color=color.blurple())
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Black Leather Jacket - White": 1, "storage.Shades": 1}, "$set": {'s': 39}})
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "What's next?")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.title = "Chapter 3: Forged in Iron"
    embed.description = "**Vince:** Didn’t think you’d make it this far, you’ve impressed me! It’s time to start your training."
    view = interclass.Story(ctx, "...")
    view.message = msg = await msg.edit(embed=embed, view=view)
    
    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 1:** Use **/shop** to browse weapons.> **Vince:** Every good mafioso needs a weapon they can rely on. You never know when someone will try to mess with you—or when you’ll need to mess with someone else. Head to the shop and scope out the selection."
    # file = await npc("vince")
    # embed.set_thumbnail(url="attachment://npc.png")
    # file2 = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")

    # await msg.edit(embed=embed, view=None, files=[file, file2], attachments=[])

    return msg

async def story39(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 1:** Use **/stats** to view your stats.\n> **Vince:** Every fighter needs to know their strengths and weaknesses. Let’s check your stats and see where you shine—and where you need work.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 40)

    return None

async def story40(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 1:** Use **/stats** to view your stats.\n> **Vince:** Every fighter needs to know their strengths and weaknesses. Let’s check your stats and see where you shine—and where you need work.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story41(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 2:** Use **/train info:info** to learn about stats.\n> **Vince:** Understanding the game is half the battle. Take a moment to learn what your stats do—you’ll thank me later.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 42)

    return None

async def story42(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 2:** Use **/train info:info** to learn about stats.\n> **Vince:** Understanding the game is half the battle. Take a moment to learn what your stats do—you’ll thank me later.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story43(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 3:** Use **/train** to boost one stat.\n> **Vince:** Time to hit the gym. Pick a stat to train—it’s the best way to get stronger. Remember, you can train every 30 minutes, so don’t slack off.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 44)

    return None

async def story44(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 3:** Use **/train** to boost one stat.\n> **Vince:** Time to hit the gym. Pick a stat to train—it’s the best way to get stronger. Remember, you can train every 30 minutes, so don’t slack off.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story45(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 4:** **Attack** and **hospitalize** another hoodlum.\n> **Vince:** You’re getting stronger, but power means nothing if you don’t use it. Find another target and show the streets who’s boss. Put them in the hospital—it’s the ultimate statement.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 46)

    return None

async def story46(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 4:** **Attack** and **hospitalize** another hoodlum.\n> **Vince:** You’re getting stronger, but power means nothing if you don’t use it. Find another target and show the streets who’s boss. Put them in the hospital—it’s the ultimate statement.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story47(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 5:** Make <:cash:1329017495536930886> 5,000 cash.\n> **Vince:** Money talks, kid. Hit the streets, make some deals, and hustle your way to 5 grand. You’ve got this.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 48)

    return None

async def story48(ctx, user, msg = None):

    if user['cash'] < 5000:
      embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 5:** Make <:cash:1329017495536930886> 5,000 cash.\n> **Vince:** Money talks, kid. Hit the streets, make some deals, and hustle your way to 5 grand. You’ve got this.", color=color.blurple())

      file = await npc("vince")
      embed.set_thumbnail(url="attachment://npc.png")

      file2 = await getimg("beggar_bg")
      embed.set_image(url="attachment://pic.png")

      if msg is None:
        await ctx.respond(embed=embed, files=[file, file2])
      else:
        await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

      return None

    await updateset(ctx.author.id, 's', 49)
    return msg

async def story49(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 6:** Use **/accoalde** to view and equip titles and badges.\n> **Vince:** Titles are more than bragging rights—they show the world what you’ve accomplished. Equip ‘Hustler’ to show off your success. You can always unequip it if you want with /title unequip.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 50)

    return None

async def story50(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 6:** Use **/accolade** to view and equip titles and badges.\n> **Vince:** Titles are more than bragging rights—they show the world what you’ve accomplished. Equip ‘Hustler’ to show off your success. You can always unequip it if you want with /title unequip.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story51(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 7:** Steal **5** cars to fill your garage.\n**Vince:** You’ve got a garage—now it’s time to fill it. Steal 5 cars and build your collection. The bigger your fleet, the bigger your reputation.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 52)

    return None

async def story52(ctx, user, msg = None):

    if len(user['garage']) < 5:
      embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 7:** Steal **5** cars to fill your garage.\n**Vince:** You’ve got a garage—now it’s time to fill it. Steal 5 cars and build your collection. The bigger your fleet, the bigger your reputation.", color=color.blurple())

      file = await npc("vince")
      embed.set_thumbnail(url="attachment://npc.png")

      file2 = await getimg("beggar_bg")
      embed.set_image(url="attachment://pic.png")

      if msg is None:
        await ctx.respond(embed=embed, files=[file, file2])
      else:
        await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

      return None

    await updateset(ctx.author.id, 's', 53)
    return msg

async def story53(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 8:** Use **/upgarage** to upgrade your garage.\n> **Vince:** More cars mean more room. Upgrade your garage, but keep in mind that each upgrade costs <:cash:1329017495536930886> 50 more than the last.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 54)

    return None

async def story54(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 8:** Use **/upgarage** to upgrade your garage.\n> **Vince:** More cars mean more room. Upgrade your garage, but keep in mind that each upgrade costs <:cash:1329017495536930886> 50 more than the last.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story55(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 9:** Buy one level of **insurance** from the **shop**.\n> **Vince:** Here’s a tip: if you die, you lose cash that isn’t stashed. Insurance reduces your losses, so make sure you’ve got a policy in place.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, 's', 56)
    return None

async def story56(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 9:** Buy one level of **insurance** from the **shop**.\n> **Vince:** Here’s a tip: if you die, you lose cash that isn’t stashed. Insurance reduces your losses, so make sure you’ve got a policy in place.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story57(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Vince:** And don’t forget—if you die, your insurance level drops. Always check it after a close call.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "Alright")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 10:** Use **/daily** to claim a daily bonus.\n> **Vince:** You can claim this once every 20 hours. Consider it a little encouragement to keep hustling."

    # file = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, file=file, view=None)

    await updateset(ctx.author.id, 's', 58)

    return msg

async def story58(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 10:** Use **/events** to check ongoing events.\n> **Vince:** Events are your chance to grab limited-time rewards. Don’t miss out—those prizes could give you an edge.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 59)

    return None

async def story59(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 10:** Use **/events** to check ongoing events.\n> **Vince:** Events are your chance to grab limited-time rewards. Don’t miss out—those prizes could give you an edge.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story60(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 11:** Use **/news** to check updates and announcements.\n> **Vince:** Stay in the loop, kid. Knowing what’s happening in the game keeps you ahead of the competition.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 61)

    return None

async def story61(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**Task 11:** Use **/news** to check updates and announcements.\n> **Vince:** Stay in the loop, kid. Knowing what’s happening in the game keeps you ahead of the competition.", color=color.blurple())

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story62(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 3: Forged in Iron", description="**End of Chapter Reward:** <:cash:1329017495536930886> 2,000 cash, 1 machete, 1 Average Car Key <:average_car_key:1358506292725022761>\n> **Vince:** Your reputation on the streets is building up, good job on surviving this long! Here’s a little something to help you defend yourself.", color=color.blurple())
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Machete": 1, "storage.Average Car Key": 1}, "$set": {'s': 63}})
    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "What's next?")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.title = "Chapter 4: Clowning Around and Getting Smart"
    embed.description = "Alright, kid, you’ve been making waves, but the real work starts now. You’ve got to think bigger, act smarter, and, most importantly, stay sharp. Rosie LaRue’s gonna help you with that. She’s one of the best brains in the business, and lucky for you, she’s on our side."
    view = interclass.Story(ctx, "Rosie?")
    view.message = msg = await msg.edit(embed=embed, view=view)
    
    await view.wait()
    if view.value is None:
        return None

    embed.description = "_Rosie steps forward, adjusting her glasses with a smirk_"

    view = interclass.Story(ctx, "...")
    view.message = await msg.edit(embed=embed, view=view, attachments=[])

    await view.wait()
    if view.value is None:
        return None

    embed.description = "Vince tells me you’ve got potential, but I’ll be the judge of that. Smarts win wars, not just muscle. Let’s get started."
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")
    view = interclass.Story(ctx, f"...")
    view.message = await msg.edit(embed=embed, view=view, file=file)

    await view.wait()
    if view.value is None:
        return None

    return msg

async def story63(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 1:** Use **/use average** to find the car that matches the key you have.\n> **Rosie:** First thing’s first: let’s put that key of yours to use. Every key unlocks a specific car. You’ll need to figure out which one matches. Go ahead, give it a try.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")
    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story64(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Good job finding your match! Now you’ve got a car to show for your effort. Let’s move on—you’re going to need some steady work if you want to survive out here.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 65)

    return msg

async def story65(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 2:** Use **/job menu** to look up available jobs.\n> **Rosie:** Jobs may not sound glamorous, but they’re the foundation of your empire. Look up what’s available and see what catches your eye.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 66)

    return None

async def story66(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 2:** Use **/job menu** to look up available jobs.\n> **Rosie:** Jobs may not sound glamorous, but they’re the foundation of your empire. Look up what’s available and see what catches your eye.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story67(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Nice work. Now let’s start small. Don’t laugh, but you’re about to become the life of the party.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 68)

    return msg

async def story68(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 3:** Become a clown using **/job assign clown**.\n> **Rosie:** Clowns don’t just bring laughs; they bring opportunity. It might not be the most dignified start, but every legend begins somewhere.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 69)

    return None

async def story69(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 3:** Become a clown using **/job assign clown**.\n> **Rosie:** Clowns don’t just bring laughs; they bring opportunity. It might not be the most dignified start, but every legend begins somewhere.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story70(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Congratulations! Welcome to the world of oversized shoes and balloon animals. Let’s see what you can do with this gig.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 71)

    return msg

async def story71(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 4:** Work as a clown using **/job work**.\n> **Rosie:** Every job teaches you something. Your task now? Make people laugh—or scream. Either works for me. Get to work, clown.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 72)

    return None

async def story72(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 4:** Work as a clown using **/job work**.\n> **Rosie:** Every job teaches you something. Your task now? Make people laugh—or scream. Either works for me. Get to work, clown.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story73(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Good job, Bozo! You’re starting to get the hang of this, remember you can work your job every 30 minutes. But what makes any job worthwhile are the perks.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 74)

    return msg

async def story74(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 5:** Use **/job perklist** to look up job perks.\n> **Rosie:** Every job has perks, little bonuses that can make a big difference. Let’s take a look at what being a clown gets you.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 75)

    return None

async def story75(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 5:** Use **/job perklist** to look up job perks.\n> **Rosie:** Every job has perks, little bonuses that can make a big difference. Let’s take a look at what being a clown gets you.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story76(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Interesting, huh? Those perks could come in handy. Time to put them to use.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 77)

    return msg

async def story77(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 6:** Use the clown job perk by typing **/job perk**.\n> **Rosie:** Now that you’ve got the clown perk, let’s see how it works. Use it and watch the magic—or chaos—unfold.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 78)

    return None

async def story78(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 6:** Use the clown job perk by typing **/job perk**.\n> **Rosie:** Now that you’ve got the clown perk, let’s see how it works. Use it and watch the magic—or chaos—unfold.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story79(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Not bad! Clowning around isn’t so silly after all, you can use this perk once every 60 minutes. Now let’s talk about brains and how to use them.", color=color.blurple())
    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description = "**Rosie:** Let me clue you in. Charisma helps you charm your way into—or out of—sticky situations and increases cash earned in everything that you do. You earn charisma by successfully completing your work. Intelligence, on the other hand, is all about strategy and execution. It allows you to find a better job, and get paid more! Both are vital if you want to make it big."
    view = interclass.Story(ctx, "Alright")
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description = "**Rosie:** Now that you know the basics, let’s get you a little smarter."
    view = interclass.Story(ctx, "...")
    view.message = await msg.edit(embed=embed, view=view)

    await view.wait()
    if view.value is None:
        return None

    # embed.description = "**Task 1:** Use **/search** to find cash.\n> **Vince:** Dig deep, kid. Sometimes it’s a goldmine, sometimes it’s… well, a gum wrapper. Let’s see what you’ve got."
    # file = await npc("vince")
    # embed.set_thumbnail(url="attachment://npc.png")
    # file2 = await getimg("beggar_bg")
    # embed.set_image(url="attachment://pic.png")
    # await msg.edit(embed=embed, files=[file, file2], view=None, attachments=[])

    await updateset(ctx.author.id, "s", 80)

    return msg

async def story80(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 7:** Use **/learn** to study intelligence.\n> **Rosie:** Hit the books—or, you know, whatever passes for studying in this world. Intelligence pays off, so start learning.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story81(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Good job sharpening your mind, keep at it: you can learn more every 30 minutes. But smarts alone won’t get you by—you need street skills too.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 82)

    return msg

async def story82(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 8:** Shoplift in town using **/shoplift**.\n> **Rosie:** Let’s test your nerves. Shoplifting’s quick and risky, but it’s a skill you’ll need. Find something valuable and take it—quietly.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 83)

    return None

async def story83(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 8:** Shoplift in town using **/shoplift**.\n> **Rosie:** Let’s test your nerves. Shoplifting’s quick and risky, but it’s a skill you’ll need. Find something valuable and take it—quietly.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story84(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Smooth work! But shoplifting’s just the appetizer. Time to get a little more personal.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 85)

    return msg

async def story85(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 9:** Pickpocket someone using **/pickpocket**.\n> **Rosie:** Pickpocketing is an art. It’s all about precision and timing. Find your mark and lighten their load.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 86)

    return None

async def story86(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 9:** Pickpocket someone using **/pickpocket**.\n> **Rosie:** Pickpocketing is an art. It’s all about precision and timing. Find your mark and lighten their load.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story87(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Nice hands! With skills like that, you’ll be cleaning up in no time. Ready for something bolder?", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 88)

    return msg

async def story88(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 10:** Commit a burglary using **/burglary**.\n> **Rosie:** Breaking and entering takes guts. Find a house, get in, grab what you can, and get out before anyone notices.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 89)

    return None

async def story89(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 10:** Commit a burglary using **/burglary**.\n> **Rosie:** Breaking and entering takes guts. Find a house, get in, grab what you can, and get out before anyone notices.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story90(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Impressive! You’ve got the makings of a true criminal. Let’s boost that brainpower some more.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 91)

    return msg

async def story91(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 11:** Reach 10 intelligence.\n> **Rosie:** Keep at it. Intelligence opens doors—literally and figuratively. Hit 10, and we’ll talk about your next move.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 92)

    return None

async def story92(ctx, user, msg = None):

    if user['stats']['int'] < 10:

      embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 11:** Reach 10 intelligence.\n> **Rosie:** Keep at it. Intelligence opens doors—literally and figuratively. Hit 10, and we’ll talk about your next move.", color=color.blurple())

      file = await npc("rosie")
      embed.set_thumbnail(url="attachment://npc.png")

      file2 = await getimg("beggar_bg")
      embed.set_image(url="attachment://pic.png")

      if msg is None:
        await ctx.respond(embed=embed, files=[file, file2])
      else:
        await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

      return None

    await updateset(ctx.author.id, 's', 93)
    return msg

async def story93(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Look at you, Einstein! Smarter, sharper, and ready for the next step. Here’s a little something for your efforts. Put it to good use! Maybe put it towards a better estate?\n**Reward:** <:cash:1329017495536930886> 1,000 cash", color=color.blurple())
    await cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": 1000}, "$set": {'s': 94}})

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    return msg

async def story94(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 12:** Become a beggar using **/job assign beggar**.\n> **Rosie:** Now it’s time to go low to aim high. Begging might not be glamorous, but it’s a start. Sign up and start working the streets.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 95)

    return None

async def story95(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 12:** Become a beggar using **/job assign beggar**.\n> **Rosie:** Now it’s time to go low to aim high. Begging might not be glamorous, but it’s a start. Sign up and start working the streets.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story96(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Good. Even kings start as peasants. Let’s see what you can scrounge up.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 97)

    return msg

async def story97(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 13:** Work as a beggar using **/job work**.\n> **Rosie:** You’re out there with nothing but a cup and charm. Begging’s about persistence—get out there and earn your keep.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 98)

    return None

async def story98(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 13:** Work as a beggar using **/job work**.\n> **Rosie:** You’re out there with nothing but a cup and charm. Begging’s about persistence—get out there and earn your keep.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story99(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Not bad for someone starting from scratch. But you’ve got to keep grinding.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 100)

    return msg

async def story100(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 14:** Collect **50** trash.\n> **Rosie:** Trash might look worthless, but one man’s junk is another man’s opportunity. Start collecting—50 pieces should do.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 101)

    return None

async def story101(ctx, user, msg = None):
    try:
      if user['storage']['Trash'] >= 50:
        await updateset(ctx.author.id, 's', 102)
        return msg
    except:
      pass

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 14:** Collect **50** trash.\n> **Rosie:** Trash might look worthless, but one man’s junk is another man’s opportunity. Start collecting—50 pieces should do.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story102(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 15:** Craft something with the trash using **/use trash**.\n> **Rosie:** Time to get creative. Use that trash to craft something useful. Let’s see what you’ve got.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 103)

    return None

async def story103(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 15:** Craft something with the trash using **/use trash**.\n> **Rosie:** Time to get creative. Use that trash to craft something useful. Let’s see what you’ve got.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story104(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Not bad! Even junk has value if you know how to use it. You can always check on the items you have by checking your **/storage**. Who knows, maybe you’ll find more cool things you can build out of items?", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    await updateset(ctx.author.id, 's', 105)

    return msg

async def story105(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 16:** Attempt to commit larceny against another player by using **/larceny**.\n> **Rosie:** Now for the ultimate test: stealing from someone who can fight back. It’s risky, but if you pull it off, it’s worth it. Go for it.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    await updateset(ctx.author.id, "s", 106)

    return None

async def story106(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Task 16:** Attempt to commit larceny against another player by using **/larceny**.\n> **Rosie:** Now for the ultimate test: stealing from someone who can fight back. It’s risky, but if you pull it off, it’s worth it. Go for it.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    file2 = await getimg("beggar_bg")
    embed.set_image(url="attachment://pic.png")

    if msg is None:
      await ctx.respond(embed=embed, files=[file, file2])
    else:
      await msg.edit(embed=embed, files=[file, file2], attachments=[], view=None)

    return None

async def story107(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 4: Clowning Around and Getting Smart", description="**Rosie:** Well done! You’re not just surviving anymore—you’re thriving.", color=color.blurple())

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    view.message = msg = await ctx.respond(embed=embed, file=file, view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description += "\n\n**Vince:** You’ve proven you’re more than just muscle. You’ve got brains, guts, and the skills to back it up. Take this Luxury Car Key <:luxury_car_key:1358506290237804695>—it’s the start of something big."

    file = await npc("vince")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "Thanks!")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = msg = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description += "\n\n_Rosie nods approvingly_\n\n**Rosie:** Keep sharpening your mind, kid. The smarter you are, the farther you’ll go. Let’s see if you’ve got what it takes to use that key."

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "Alright")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = msg = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    embed.description += "\n\n**End of Chapter Reward:** 1 Luxury Car Key <:luxury_car_key:1358506290237804695>."

    await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Luxury Car Key": 1}, "$set": {'s': 108}})

    file = await npc("rosie")
    embed.set_thumbnail(url="attachment://npc.png")

    view = interclass.Story(ctx, "...")
    if msg is None:
      view.message = msg = await ctx.respond(embed=embed, file=file, view=view)
    else:
      view.message = msg = await msg.edit(embed=embed, file=file, attachments=[], view=view)

    await view.wait()
    if view.value is None:
        return None

    return msg

async def story108(ctx, user, msg = None):

    embed = discord.Embed(title="Chapter 5: Luck, Lies, and Legacy", description=f"Chapter 5 Coming Soon!\nNew characters will be introduced\n\n**Credits: Thanks to {ctx.bot.get_user(416050252919865344)} for creating the story!**", color=color.blurple())

    if msg is None:
      await ctx.respond(embed=embed)
    else:
      await msg.edit(embed=embed, view=None, attachments=[])

    return None

# async def story18(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** You have stolen 2 cars now, it's time to sell them! Who's gonna buy it? No one knows! Sell your cars at once by typing `/car <car IDs>`, separate the car IDs with a `,` comma! Example `/sellcar 1, 2`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story19(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Nice, now you got some cash. Check your cash by typing `/cash`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 20)

#     return None

# async def story20(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Nice, now you got some cash. Check your cash by typing `/cash`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story21(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description=f"**Eric:** See, you have <:cash:1329017495536930886> {user['cash']} cash! You can increase your stash capacity by having safes. Storing your cash in your stash helps prevent losing it when you die or getting attacked! You can obtain safes by searching for cash `/search` or vote for the bot `/vote`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     view = interclass.Next(ctx)
#     if msg is None:
#         await ctx.respond(embed=embed, file=file, view=view)
#         msg = await ctx.interaction.original_response()
#         view.message = msg
#     else:
#         view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

#     await view.wait()
#     if view.value:
#         await updateset(ctx.author.id, 's', 22)
#         return msg

# async def story22(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Come back when you are driving a car. To drive a car type `/drive <car ID>`. Good luck", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 23)

#     return None

# async def story23(ctx, user, msg = None):
#     if user['drive'] == "":
#         embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Come back when you are driving a car. To drive a car type `/drive <car ID>`. Good luck", color=color.blurple())
#         file = await eric()
#         embed.set_thumbnail(url="attachment://pic.png")

#         if msg is None:
#             msg = await ctx.respond(embed=embed, file=file)
#         else:
#             await msg.edit(embed=embed, file=file, attachments=[])

#         return None

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Nice car you have! You should go for a race with some random hoodlums. Type `/race` to start racing!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 24)

#     return None

# async def story24(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Nice car you have! You should go for a race with some random hoodlums. Type `/race` to start racing!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story25(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Is racing fun? Well, you might be tired now. Check your energy by typing `/energy`!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 26)

#     return None

# async def story26(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Is racing fun? Well, you might be tired now. Check your energy by typing `/energy`!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story27(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** You will use up your energy everytime you steal a car, race or attack someone. You can always wait for your energy to be refilled. But you can also sleep or eat something to refill it instantly! Here, take 5 meat, type `/use meat` to eat the meat, or you can type `/sleep` to refill it instantly", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 28)
#     await updateinc(ctx.author.id, 'storage.Meat', 5)

#     return None

# async def story28(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** You will use up your energy everytime you steal a car, race or attack someone. You can always wait for your energy to be refilled. But you can also sleep or eat something to refill it instantly! Here, take 5 meat, type `/use meat` to eat the meat, or you can type `/sleep` to refill it instantly", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story29(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** You have completed Chapter 1! Here's <:cash:1329017495536930886> 200 cash for completing Chapter 1!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": 200}, "$set": {"s": "29a"}})

#     return None

# async def story29a(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Good, now I want you to visit the city shop. Do that by typing `/shop`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 30)

#     return None

# async def story30(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Good, now I want you to visit the city shop. Do that by typing `/shop`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story31(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Did you see some weapons? Go and purchase a baseball bat, do that by typing `/buy baseball bat`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 32)

#     return None

# async def story32(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Did you see some weapons? Go and purchase a baseball bat, do that by typing `/buy baseball bat`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story33(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Now you have a weapon! All items you own are stored in your storage, type `/storage` to take a look at your baseball bat!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 34)

#     return None

# async def story34(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Now you have a weapon! All items you own are stored in your storage, type `/storage` to take a look at your baseball bat!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story35(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** So what can you do with a baseball bat? Equip it of course! Type `/equip baseball` to equip your baseball bat!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 36)

#     return None

# async def story36(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** So what can you do with a baseball bat? Equip it of course! Type `/equip baseball` to equip your baseball bat!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story37(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Alright, so you equipped your baseball bat.. You wanna see how you look? Type `/profile` to check it out!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 38)

#     return None

# async def story38(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Alright, so you equipped your baseball bat.. You wanna see how you look? Type `/profile` to check it out!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story39(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Hmm, so that's your character.. Short limbs with a short neck, and a ridiculously large head.. Anyways lets move on, did you see that random hoodlum beside the street? Go beat him up and take his money! Do that by typing `/attack`, and **mug** the hoodlum after beating him up!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 40)

#     return None

# async def story40(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Hmm, so that's your character.. Short limbs with a short neck, and a ridiculously large head.. Anyways lets move on, did you see that random hoodlum beside the street? Go beat him up and take his money! Do that by typing `/attack`, and **mug** the hoodlum after beating him up!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story41(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Well done homie, I have a gift for you for playing the bot today, go claim your daily! You can claim your daily every 20 hours and get some loots, do that by typing `/daily`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 42)

#     return None

# async def story42(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Well done homie, I have a gift for you for playing the bot today, go claim your daily! You can claim your daily every 20 hours and get some loots, do that by typing `/daily`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story43(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Great! You have gotten my approval for being a part of the mafia. Now you should be able to make a living yourself. Before you continue, here's a gift for you for completing the basics!\n\nEric handed you a denim shorts, plain tee and a pair of black flip-flops", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Denim Shorts": 1, "storage.Plain Tee": 1, "storage.Black Flip-flops": 1}, "$set": {"s": 44}})

#     view = interclass.Next(ctx)

#     if msg is None:
#         await ctx.respond(embed=embed, file=file, view=view)
#         msg = await ctx.interaction.original_response()
#         view.message = msg
#     else:
#         view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

#     await view.wait()
#     if view.value:
#         await updateset(ctx.author.id, 's', 45)
#         return msg

# async def story44(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 1: Fresh Start", description="**Eric:** Great! You have gotten my approval for being a part of the mafia. Now you should be able to make a living yourself. Before you continue, here's a gift for you for completing the basics! You can read the tutorial by typing `/tutorial` if you have any questions!\n\nEric handed you a denim shorts, plain tee and a pair of flip-flops", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     view = interclass.Next(ctx)

#     if msg is None:
#         await ctx.respond(embed=embed, file=file, view=view)
#         msg = await ctx.interaction.original_response()
#         view.message = msg
#     else:
#         view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

#     await view.wait()
#     if view.value:
#         await updateset(ctx.author.id, 's', 45)
#         return msg

# async def story45(ctx, user, msg = None):

#     if user['lvl'] < 5:
#         embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Hey homie, come back when you are level 5", color=color.blurple())
#         file = await eric()
#         embed.set_thumbnail(url="attachment://pic.png")

#         if msg is None:
#             msg = await ctx.respond(embed=embed, file=file)
#         else:
#             await msg.edit(embed=embed, file=file, attachments=[])

#         return None

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** So you have already reached level 5? That's quick, I bet you had been into the jail or hospital before, if you don't then you're a lucky fellow! Everytime when you are thrown into the jail or hospital, you have to wait until you get released or recovered. But there is something that can prevent you from waiting!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     view = interclass.Next(ctx)

#     if msg is None:
#         await ctx.respond(embed=embed, file=file, view=view)
#         msg = await ctx.interaction.original_response()
#         view.message = msg
#     else:
#         view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

#     await view.wait()
#     if view.value:
#         await updateset(ctx.author.id, 's', 46)
#         return msg

# async def story46(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Here, keep these 2 Bribes and 2 Medical Kits! Use the bribes when you are in jail and medical kits when you are in hospital. Do that by typing `/use bribe` or `/use medical`, come back when you used a bribe **or** a medical kit!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await cll.update_one({"id": ctx.author.id}, {"$inc": {"storage.Bribe": 2, "storage.Medical Kit": 2}, "$set": {"s": 47}})

#     return None

# async def story47(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Here, keep these 2 Bribes and 2 Medical Kits! Use the bribes when you are in jail and medical kits when you are in hospital. Do that by typing `/use bribe` or `/use medical`, come back when you used a bribe **or** a medical kit!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story48(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Remember the last time you beaten up a hoodlum? Well this time I want you to beat another hoodlum! Any hoodlum you like, but before that, you need to know how weak you are. Check your fighting statistics by typing `/statistics`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 49)

#     return None

# async def story49(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Remember the last time you beaten up a hoodlum? Well this time I want you to beat another hoodlum! Any hoodlum you like, but before that, you need to know how weak you are. Check your fighting statistics by typing `/statistics`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story50(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great, are you wondering what those statistics do? Type `/train info` to check it out!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 51)

#     return None

# async def story51(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great, are you wondering what those statistics do? Type `/train info` to check it out!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story52(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Now I want you to train yourself to get stronger, these statistics will make you stronger in fights. Type `/train` to train yourself", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 53)

#     return None

# async def story53(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Now I want you to train yourself to get stronger, these statistics will make you stronger in fights. Type `/train` to train yourself", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story54(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright, you are now stronger, you can train every 30 minutes. I want you to go beat up a random hoodlum on the street, and **hospitalize** them after winning!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 55)

#     return None

# async def story55(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright, you are now stronger, you can train every 30 minutes. I want you to go beat up a random hoodlum on the street, and **hospitalize** them after winning!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story56(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Wait what? Do you not know how to wear clothes? In case you don't, you can do that just by typing `/equip <clothes or weapon>` for example `/equip plain`. Try equipping a plain tee!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 57)

#     return None

# async def story57(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Wait what? Do you not know how to wear clothes? In case you don't, you can do that just by typing `/equip <clothes or weapon>` for example `/equip plain`. Try equipping a plain tee!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story58(ctx, user, msg = None):

#     if user['cash'] < 5000:
#         embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Hey kid, come back when you have <:cash:1329017495536930886> 5,000", color=color.blurple())
#         file = await eric()
#         embed.set_thumbnail(url="attachment://pic.png")

#         if msg is None:
#             msg = await ctx.respond(embed=embed, file=file)
#         else:
#             await msg.edit(embed=embed, file=file, attachments=[])

#         return None

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright, so you already got <:cash:1329017495536930886> 5,000? I bet you also unlocked the Hustler achievement! Wonder what achievement gives you? Type `/title list` to check a list of titles!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 59)

#     return None

# async def story59(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright, so you already got <:cash:1329017495536930886> 5,000? I bet you also unlocked the Hustler achievement! Wonder what achievement gives you? Type `/title list` to check a list of titles!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story60(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great, so now you know achievement unlocks different titles. Now type `/title` again but without `list`, this time it will show the titles you own or the achievements you unlocked", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 61)

#     return None

# async def story61(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great, so now you know achievement unlocks different titles. Now type `/title` again but without `list`, this time it will show the titles you own or the achievements you unlocked", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story62(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Okay, I bet you saw the **Hustler** title you achieved. I want you to equip the title, do that by typing `/title hustler`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 63)

#     return None

# async def story63(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Okay, I bet you saw the **Hustler** title you achieved. I want you to equip the title, do that by typing `/title hustler`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story64(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Nice! Now try and go racing or attacking, you will see your title displayed infront of your name, how cool! You can always unequip your title by typing `/title unequip`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     view = interclass.Next(ctx)

#     if msg is None:
#         await ctx.respond(embed=embed, file=file, view=view)
#         msg = await ctx.interaction.original_response()
#         view.message = msg
#     else:
#         view.message = await msg.edit(embed=embed, file=file, attachments=[], view=view)

#     await view.wait()
#     if view.value:
#         await updateset(ctx.author.id, 's', 65)
#         return msg

# async def story65(ctx, user, msg = None):

#     if len(user['garage']) < 5:
#         embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Come back when you have 5 cars or more!", color=color.blurple())
#         file = await eric()
#         embed.set_thumbnail(url="attachment://pic.png")

#         if msg is None:
#             msg = await ctx.respond(embed=embed, file=file)
#         else:
#             await msg.edit(embed=embed, file=file, attachments=[])

#         return None

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright you got 5 cars? Your garage is probably full! But no worries, type `/upgarage` to upgrade your garage! Each upgrade cost <:cash:1329017495536930886> 50 more than the previous upgrade!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 66)

#     return None

# async def story66(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Alright you got 5 cars? Your garage is probably full! But no worries, type `/upgarage` to upgrade your garage! Each upgrade cost <:cash:1329017495536930886> 50 more than the previous upgrade!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story67(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Wait, never miss out any ongoing events! You will regret missing them because there will be limited items. Check ongoing events by typing `/events`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 68)

#     return None

# async def story68(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Wait, never miss out any ongoing events! You will regret missing them because there will be limited items. Check ongoing events by typing `/events`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story69(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Other than events, check the latest announcements and the latest updates! Do that by typing `/news`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 70)

#     return None

# async def story70(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Other than events, check the latest announcements and the latest updates! Do that by typing `/news`", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story71(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Have you died before and lost your cash? Do you know, you can prevent losing your cash by purchasing insurance? Head to the city shop insurance section and buy an insurance", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 72)

#     return None

# async def story72(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Have you died before and lost your cash? Do you know, you can prevent losing your cash by purchasing insurance? Head to the city shop insurance section and buy an insurance, 20% would be good enough!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story73(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great! You can upgrade your insurance anytime, I recommend you to do that only when you have more than <:cash:1329017495536930886> 5,000. Oh yeah, I found this average car key beside the street, try using it by typing `/use average`, you will get a random car!\n\nEric handed you an Average Car Key", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     await updateset(ctx.author.id, 's', 74)
#     await updateinc(ctx.author.id, 'storage.Average Car Key', 1)

#     return None

# async def story74(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="**Eric:** Great! You can upgrade your insurance anytime, I recommend you to do that only when you have more than <:cash:1329017495536930886> 5,000. Oh yeah, I found this average car key beside the street, try using it by typing `/use average`, you will get a random car!\n\nEric handed you an Average Car Key", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

# async def story75(ctx, user, msg = None):

#     embed = discord.Embed(title="Chapter 2: Errand Runner", description="Coming soon\nUse the tutorial command or help command!", color=color.blurple())
#     file = await eric()
#     embed.set_thumbnail(url="attachment://pic.png")

#     if msg is None:
#         msg = await ctx.respond(embed=embed, file=file)
#     else:
#         await msg.edit(embed=embed, file=file, attachments=[])

#     return None

dispatcher = {"Racer": racer, "Car Dealer": car_dealer, "Fencer": fencer, "Farmer": farmer, "Mechanic": mechanic, "ribbon": ribbon, "cannabis": cannabis, "ecstasy": ecstasy, "heroin": heroin, "methamphetamine": methamphetamine, "xanax": xanax, "trash": trash, "Lawyer": lawyer, "Doctor": doctor, "Artist": artist, "Gamer": gamer, "Teacher": teacher, "Kidnapper": kidnapper, "Chef": chef, "Trash collector": trash_collector, "Business man": business_man, "Beggar": beggar, "Clown": clown, "tuner": tuner, "scrap": scrap, "laptop": laptop, "document": document, "homework": homework, "beer": beer, "fuel": fuel, "morphine": morphine, "bribe": bribe, "medical_kit": medical_kit, "donator_case": donator_case, "purse": purse, "giftbox": giftbox, "drug_stash": drug_stash, "average_car_key": average_car_key, "luxury_car_key": luxury_car_key, "pill": pill, "weapon_case": weapon_case, "apparel_box": apparel_box, "tatter": tatter, "garage_key": garage_key, "royal_case": royal_case}

async def tttdisplay(matrix):
  blocks = {0: "\U00002b1c", 1: "\U00002b1b", 2: "\U00002b55", 3: "\U0000274c"}
  board = [[1,1,1,1,1,1,1], [1, matrix[0][0] ,1, matrix[0][1] ,1, matrix[0][2] ,1] , [1,1,1,1,1,1,1], [1, matrix[1][0] ,1, matrix[1][1] ,1, matrix[1][2] ,1] , [1,1,1,1,1,1,1], [1, matrix[2][0] ,1, matrix[2][1] ,1, matrix[2][2] ,1] , [1,1,1,1,1,1,1]]

  for row in range(len(board)):
    board[row] = [blocks[block] for block in board[row]]

  board = "\n".join(["".join(row) for row in board])

  return board

async def checkwin(matrix):

  async def checkrows(matrix):
    return any([len(set(row)) == 1 and 0 not in row for row in matrix])

  async def checkcols(matrix):
    return any([len(set(col)) == 1 and 0 not in col for col in list(zip(*matrix))])

  async def checkdiag(matrix):
    return any([len(set(diag)) == 1 and 0 not in diag for diag in [[matrix[i][i] for i in range(len(matrix))]] + [[matrix[i][len(matrix)-i-1] for i in range(len(matrix))]]])

  return any([await checkrows(matrix), await checkcols(matrix), await checkdiag(matrix)])

async def checktie(matrix):
    return len([block for row in matrix for block in row if block != 0]) == len([block for row in matrix for block in row])

