"""Imports"""
import random
import discord
import asyncio
import functions
import time
import interclass
from functions import blocked, updateinc, finduser, updateset, ab, dboost, aa, getdrive, randomcar, cll, gettitle
from discord.commands import slash_command, Option
from discord.ext import commands, tasks
from PIL import Image, ImageDraw
from io import BytesIO
import lists
import datetime
import math

color = discord.Colour
donatorlist = []
events = []

def custom_cooldown(r, p, r2, p2, type = commands.BucketType.user):
    def decorator(func):
        if isinstance(func, commands.Command):
            func._buckets = commands.DynamicCooldownMapping(dummy, type, r, p, r2, p2)
        else:
            func.__commands_cooldown__ = commands.DynamicCooldownMapping(dummy, type, r, p, r2, p2)
        return func
    return decorator

commands.custom_cooldown = custom_cooldown

def theft_cooldown(message):
    if any(["motor madness" in event.lower() for event in events]):
        if message.author.id in donatorlist:
            return commands.Cooldown(1, 22)
        else:
            return commands.Cooldown(1, 30)
    if message.author.id in donatorlist:
        return commands.Cooldown(1, 45)
    else:
        return commands.Cooldown(1, 60)

class DynamicCooldownMapping(commands.CooldownMapping):
    def __init__(self, factory, type, r, p, r2, p2) -> None:
        super().__init__(None, type)
        self._factory = factory
        self.r = r
        self.p = p
        self.r2 = r2
        self.p2 = p2
    def copy(self):
        ret = DynamicCooldownMapping(self._factory, self._type, self.r, self.p, self.r2, self.p2)
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

star = u"\u2B50"

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

      dieembed = discord.Embed(title = f"{gettitle(userp)}{user} died {where}!", description = f"{reason}\nYou lost <:cash:1329017495536930886> {aa(cashlost)}\nYou are now in hospital for `{ab(randomtime)}`", color = color.red())
      if userp['ins'] != 0:
        dispatcher = {-1: 0, 0: 20, 1: 50, 2: 70, 3: 90, 4: 100, 5: 101, 6: 101}
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

async def repaircar(ctx, user, usercar, price):
      userp = await finduser(user.id)
      usergarage = userp['garage']
      usercargold = usercar['golden']
      usercarname = usercar['name']
      if usercargold == True:
        usercarname = f"{star} Golden " + usercarname
      
      view = interclass.Confirm(ctx, user)

      await ctx.respond(f"{gettitle(userp)}{user.mention} you crashed your car {usercarname}! It costs <:cash:1329017495536930886> {price} to repair, do you want to repair it? You have 30 seconds to withdraw cash and respond", view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value == None:
        await ctx.respond(f"{gettitle(userp)}{user.mention} You didn't reply in 30 seconds, I guess you don't wanna repair your car")
        await cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
        await updateset(user.id, 'drive', "")
        return
      elif view.value == False:
        await ctx.respond("Alright then say bye to your car")
        await cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
        await updateset(user.id, 'drive', "")
        return
      userp = await finduser(user.id)
      usercash = userp['cash']
      if usercash < price:
        view = interclass.Confirm(ctx, user)

        await ctx.respond(f"{gettitle(userp)}{user.mention} You don't have enough cash to repair! Withdraw your cash if you have any, and this is your last chance to respond")
        msg = await ctx.interaction.original_response()
        view.message = msg
        
        await view.wait()

        if view.value == None:
          await ctx.respond(f"{gettitle(userp)}{user.mention} You didn't reply in 30 seconds, I guess you don't wanna repair your car")
          await cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
          await updateset(user.id, 'drive', "")
          return
        elif view.value == False:
          await ctx.respond("Alright then say bye to your car")
          await cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
          await updateset(user.id, 'drive', "")
          return
        userp = await finduser(user.id)
        usercash = userp['cash']
        if usercash < price:
          await ctx.respond(f"{gettitle(userp)}{user.mention} I told you that you don't have enough cash to repair, too bad it's too late to repair it now")
          await cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
          await updateset(user.id, 'drive', "")
          return
        await ctx.respond(f"You paid <:cash:1329017495536930886> {price} to repair your car {usercarname}!")
        await updateinc(user.id, 'cash', -price)
      elif usercash >= price:
        await ctx.respond(f"You paid <:cash:1329017495536930886> {price} to repair your car {usercarname}!")
        await updateinc(user.id, 'cash', -price)

class CrimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donatorlist.start()
        self.die = die
        self.repaircar = repaircar

    def cog_unload(self):
        self.donatorlist.cancel()

    @slash_command(description="Plan and commit fraud", usage="/fraud")
    @commands.custom_cooldown(1, 120, 1, 90, commands.BucketType.user)  
    async def fraud(self, ctx):
        await __import__('slash').fraud(self, ctx)

    @slash_command(description="Bust someone out of jail", usage="/bust [user]")
    @commands.custom_cooldown(1, 300, 1, 240, commands.BucketType.user)
    async def bust(self, ctx, user: Option(discord.User, "User to bust") = None):
        await __import__('slash').bust(self, ctx, user)

    @slash_command(description="Shoplifting somewhere", usage="/shoplift")
    @commands.custom_cooldown(1, 60, 1, 45, commands.BucketType.user)
    async def shoplift(self, ctx):
        await __import__('slash').shoplift(self, ctx)

    @slash_command(description="Commit burglary on random houses", usage="/burglary")
    @commands.custom_cooldown(1, 120, 1, 90, commands.BucketType.user)
    async def burglary(self, ctx):
        await __import__('slash').burglary(self, ctx)

    @slash_command(description="Pickpocket strangers", usage="/pickpocket")
    @commands.custom_cooldown(1, 45, 1, 30, commands.BucketType.user)
    async def pickpocket(self, ctx):
        await __import__('slash').pickpocket(self, ctx)

    @slash_command(description="Attack a user", usage="/attack <user>")
    @commands.custom_cooldown(1, 900, 1, 600, commands.BucketType.user)
    async def attack(self, ctx, user: Option(discord.Member, "User to attack") = None):
        await __import__('slash').attack(self, ctx, user)

    @slash_command(description="Race against a random hoodlum or another user", usage="/race [user] [bet]")
    @commands.custom_cooldown(1, 120, 1, 90, commands.BucketType.user)
    async def race(self, ctx, user: Option(discord.Member, "User to race against") = None, bet: Option(int, "Bet amount", min_value=10, max_value=5000) = None):
        await __import__('slash').race(self, ctx, user, bet)

    @slash_command(description="Commit larceny on a user's stash", usage="/larceny <user>")
    @commands.custom_cooldown(1, 300, 1, 240, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    async def larceny(self, ctx, user: Option(discord.Member, "User to commit larceny")):
      await __import__('slash').larceny(self, ctx, user)

    @slash_command(description="Search around for cash", usage="/search")
    @commands.custom_cooldown(1, 30, 1, 20, commands.BucketType.user)
    async def search(self, ctx):
      await __import__('slash').search(self, ctx)

    @slash_command(description="Steal a vehicle", usage="/vehicletheft")
    @commands.dynamic_cooldown(theft_cooldown, commands.BucketType.user)
    async def theft(self, ctx):
      await __import__('slash').vehicletheft(self, ctx)

    @tasks.loop(seconds=60)
    async def donatorlist(self):
        try:
            global donatorlist
            donatorlist = [member['id'] for member in await self.bot.cll.find({"donor": {"$gt": 0}}).to_list(length=None)]
        except:
            pass
        try:
            global events
            server = await self.bot.gcll.find_one({"id": 863025676213944340})
            events = [server['events'][t] for t in server['events'] if int(t) > round(time.time())]
        except:
            pass

def setup(bot):
    bot.add_cog(CrimeCog(bot))