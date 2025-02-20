"""Imports"""
import random
import discord
import interclass
import time
from functions import updateinc, finduser, updateset, ab, aa, gettitle
from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands, tasks

color = discord.Colour
donatorlist = []

def custom_cooldown(r, p, r2, p2, type = commands.BucketType.user):
    def decorator(func):
        if isinstance(func, commands.Command):
            func._buckets = commands.DynamicCooldownMapping(dummy, type, r, p, r2, p2)
        else:
            func.__commands_cooldown__ = commands.DynamicCooldownMapping(dummy, type, r, p, r2, p2)
        return func
    return decorator

commands.custom_cooldown = custom_cooldown

class DynamicCooldownMapping(commands.CooldownMapping):
    def __init__(self, factory, type, r, p, r2, p2) -> None:
        super().__init__(None, type)
        self._factory = factory
        self.r = r
        self.p = p
        self.r2 = r2
        self.p2 = p2
    def copy(self):
        ret = commands.DynamicCooldownMapping(self._factory, self._type, self.r, self.p, self.r2, self.p2)
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

class CityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donatorlist.start()
        self.die = die

    def cog_unload(self):
        self.donatorlist.cancel()

    job = SlashCommandGroup("job", "Job related commands")

    market = SlashCommandGroup("market", "Market related commands")

    @market.command(name="list", description="Market for player trading", usage="/market [page]")
    async def marketlist(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').mlist(self, ctx, page)

    @market.command(name="buy", description="Buy something from the market", usage="/market buy <item>")
    async def mbuy(self, ctx, itemid: Option(int, "Item ID in market")):
      await __import__('slash').mbuy(self, ctx, itemid)

    @market.command(name="listcar", description="List a car on the market for sale", usage="/market sellcar <car ID> <price")
    async def mlistcar(self, ctx, carid: Option(str, "Car ID"), price: Option(int, "Price for sale", min_value=1), exp: Option(int, "Listing duration in hours, 24 max for non-royal members", min_value=1) = 24):
      await __import__('slash').mlistcar(self, ctx, carid, price, exp)

    @market.command(name="listitem", description="List an item on the market for sale", usage="/market sellitem <item> <price> <amount>")
    async def mlistitem(self, ctx, item: Option(str, "Item name"), price: Option(int, "Price for sale", min_value=1), amount: Option(int, "Amount to sell", min_value=1) = 1, exp: Option(int, "Listing duration in hours, 24 max for non-royal members", min_value=1) = 24):
      await __import__('slash').mlistitem(self, ctx, item, price, amount, exp)

    @slash_command(description="Place to buy stuff", usage="/shop [page]")
    async def shop(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').shop(self, ctx, page)

    @slash_command(description='Place to check property information and prices', usage="/estate [page]")
    async def estate(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').estate(self, ctx, page)

    @job.command(description="Work for salary", usage="/job work")
    @commands.custom_cooldown(1, 1800, 1, 1200, commands.BucketType.user)
    async def work(self, ctx):
      await __import__('slash').work(self, ctx)

    @job.command(description="Check out a list of jobs", usage="/job menu [page]")
    async def menu(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').menu(self, ctx, page)

    @job.command(description="Assign a job", usage="/job assign")
    @commands.cooldown(1, 10800, commands.BucketType.user)
    async def assign(self, ctx, job: Option(str, "Job name")):
      await __import__('slash').assign(self, ctx, job)

    @job.command(description="Use your job perk", usage="/job perk [user]")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def perk(self, ctx, target: Option(discord.Member, "Target to use you perk on") = None):
      await __import__('slash').perk(self, ctx, target)
      
    @job.command(description="Shows a list of job perks", usage="/job perklist")
    async def perklist(self, ctx, page: Option(int, "Page") = 1):
      await __import__('slash').perklist(self, ctx, page)

    @slash_command(description="Shows drug prices in your location", usage="/blackmarket [page]")
    async def blackmarket(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').blackmarket(self, ctx, page)

    @slash_command(description="Travel to somewhere else or check travelling prices", usage="/travel [location]")
    async def travel(self, ctx):
      await __import__('slash').travel(self, ctx)

    @slash_command(description="Play a game to increase your intelligence", usage="/learn")
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def learn(self, ctx):
      await __import__('slash').learn(self, ctx)

    @slash_command(description="Train yourself to get stronger when attacking", usage="/train [info]")
    async def train(self, ctx, info: Option(str, "Check statistic info", choices=["info"]) = None):
      await __import__('slash').train(self, ctx, info)

    @slash_command(description="Shows oneself's statistics", usage="/stats [user]")
    async def stats(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').statistics(self, ctx, user)

    @slash_command(description="Buy something from the shop", usage="/buy <item> [amount]")
    async def buy(self, ctx, item: Option(str, "Item name"), amount: Option(int, "Amount to buy", min_value=1) = 1):
      await __import__('slash').buy(self, ctx, item, amount)

    @slash_command(description="Sell something", usage="/sell <item> [amount]")
    async def sell(self, ctx, item: Option(str, "Item name"), amount: Option(int, "Amount to sell", min_value=1) = 1):
      await __import__('slash').sell(self, ctx, item, amount)

    @slash_command(description="Shows a list of casino games", usage="/casino")
    async def casino(self, ctx):
      await __import__('slash').casino(self, ctx)

    @slash_command(description="Play Russian roulette with yourself or another user", usage="/roulette <bullet count> <bet>\n/roulette <user> <bet>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roulette(self, ctx, bullet: Option(str, "Bullet count 1-6 or a user"), bet: Option(int, "Amount to bet", min_value=10, max_value=5000)):
      await __import__('slash').roulette(self, ctx, bullet, bet)

    @slash_command(description="Play blackjack with the dealer or another user", usage="/blackjack <bet> [user]\n/blackjack rules")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blackjack(self, ctx, bet: Option(str, "Amount of bet or 'rules'"), user: Option(discord.Member, "User to bet with") = None):
      await __import__('slash').blackjack(self, ctx, bet, user)

    @slash_command(description="Play high low with the dealer", usage="/highlow <bet>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def highlow(self, ctx, bet: Option(int, "Amount of bet", min_value=10, max_value=5000)):
      await __import__('slash').highlow(self, ctx, bet)

    @slash_command(description="Play the slot machine", usage="/slot <bet>\n/slot paytable")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slot(self, ctx, bet: Option(str, "Amount of bet or 'paytable'")):
      await __import__('slash').slot(self, ctx, bet)

    @tasks.loop(seconds=60)
    async def donatorlist(self):
        try:
            global donatorlist
            donatorlist = [member['id'] for member in await self.bot.cll.find({"donor": {"$gt": 0}}).to_list(length=None)]
        except:
            pass

def setup(bot):
    bot.add_cog(CityCog(bot))