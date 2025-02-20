"""Imports"""
import discord
from discord.commands import slash_command, Option
from discord.ext import commands, tasks

color = discord.Colour
star = u"\u2B50"

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

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donatorlist.start()

    def cog_unload(self):
        self.donatorlist.cancel()

    @slash_command(description="Shows a list of command and usage", usage='/help [command]')
    async def help(self, ctx, command: Option(str, "Command name") = None):
      await __import__('slash').help(self, ctx, command)

    @slash_command(description="Shows the user's profile", usage='/profile [user]')
    async def profile(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').profile(self, ctx, user)

    @slash_command(description='Shows items the user own', usage="/storage [user]\n/storage [page] [user]")
    async def storage(self, ctx, page: Option(int, "Page", min_value=1) = None, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').storage(self, ctx, page, user)

    @slash_command(description="Remind oneself's poverty", usage='/cash [user]')
    async def cash(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').cash(self, ctx, user)

    @slash_command(description='Deposit some cash', usage='/deposit <amount>')
    async def deposit(self, ctx, amount: Option(str, "Amount to deposit")):
      await __import__('slash').deposit(self, ctx, amount)

    @slash_command(description='Withdraw some cash', usage='/withdraw <amount>')
    async def withdraw(self, ctx, amount: Option(str, "Amount to withdraw")):
      await __import__('slash').withdraw(self, ctx, amount)
      
    @slash_command(description="Give cash to another user", usage="/givecash <amount> <user> [reason]")
    async def givecash(self, ctx, amount: Option(int, "Amount to give", min_value=1), user: Option(discord.Member, "User to give cash"), reason: Option(str, "Reason to give cash") = None):
      await __import__('slash').givecash(self, ctx, amount, user, reason)

    @slash_command(description="Give item to other user", usage="/give <quantity> <item> <user> [reason]\n/give max <item> <user> [reason]")
    async def giveitem(self, ctx, amount: Option(str, "Amount to give"), item: Option(str, "Item to give"), user: Option(discord.Member, "User to give item"), reason: Option(str, "Reason to give item") = None):
      await __import__('slash').giveitem(self, ctx, amount, item, user, reason)

    @slash_command(description="Use an item", usage="/use <item> [amount]\n/use <item> [car ID]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def use(self, ctx, item: Option(str, "Item to use"), amount: Option(int, "Amount to use / Car ID", min_value=1) = 1):
      await __import__('slash').use(self, ctx, item, amount)

    @slash_command(description="Check an item info", usage="/item <item>")
    async def item(self, ctx, item: Option(str, "Item name")):
      await __import__('slash').item(self, ctx, item)

    @slash_command(description="Equip something", usage="/equip <item>")
    async def equip(self, ctx, item: Option(str, "Item to equip")):
      await __import__('slash').equip(self, ctx, item)

    @slash_command(description="Unequip something", usage="/unequip <item>")
    async def unequip(self, ctx, item: Option(str, "Item to unequip")):
      await __import__('slash').unequip(self, ctx, item)

    @slash_command(description="Shows the server's leaderboard", usage="/leaderboard [page]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx, page: Option(int, "Page", min_value=1) = 1):
      await __import__('slash').leaderboard(self, ctx, page)

    @slash_command(description="Equip or see titles you achieved", usage="/title\n/title <title>\n/title list\n/title unequip")
    async def title(self, ctx, title: Option(str, "Title name / 'list' / 'unequip'") = None):
      await __import__('slash').title(self, ctx, title)
      
    @slash_command(description="Sleep to fill up your energy!", usage="/sleep")
    @commands.custom_cooldown(1, 7200, 1, 6000, commands.BucketType.user)
    async def sleep(self, ctx):
      await __import__('slash').sleep(self, ctx)

    @slash_command(description="Check your energy", usage="/energy [user]")
    async def energy(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').energy(self, ctx, user)

    @slash_command(description="Check your level and experience", usage="/level [user]")
    async def level(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').level(self, ctx, user)

    @slash_command(description="Check the user's reputation or send respect points", usage="/reputation [user]", aliases=["rep"])
    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user, wait=True)
    async def reputation(self, ctx, user: Option(discord.Member, "User to check") = None):
      await __import__('slash').reputation(self, ctx, user)

    @slash_command(description="Main storyline of the game!", usage="/story")
    @commands.max_concurrency(1, commands.BucketType.user, wait=True)
    async def story(self, ctx):
      await __import__('slash').story(self, ctx)

    @slash_command(description="Testing command for testing purpose", usage="/test", guild_ids=[714380821800288317])
    async def test(self, ctx):
        if not ctx.author.id == 615037304616255491:
            return
        # await self.bot.cll.update_many({}, {"$set": {"drugs": {"cannabis": 0, "ecstasy": 0, "heroin": 0, "methamphetamine": 0, "xanax": 0}}})
      # await self.bot.cll.update_many({}, {"$set": {"equipments": {"back": "", "weapon": "", "head": "", "chest": "", "leg": "", "foot": ""}}})
      # return
      # # Add new variables to every user
      # self.bot.cll.update_many({}, {"$set": {"affinity": "Single"}})
      # # Add new variables to every car
      # for user in await self.bot.cll.find().to_list(length=await self.bot.cll.count_documents({})):
      #   for x in range(len(user['garage'])):
      #     await self.bot.cll.update_one({"id": user['id']}, {"$set": {f"garage.{list(user['garage'].keys())[x]}.id": functions.randomid()}})
      # await ctx.send("Done")

        from functions import finduser, updateset
        # Looping through all collections
        count = 1
        for document in await self.bot.cll.find().to_list(length=None):
            try:
                cars = document['garage']
                new_cars = []
                for car in cars:
                    if car['name'] == "Dodge Challenger SRT Demon 170":
                        car['speed'] -= 63
                    if car['name'] == "Brabus S 7.3 W140":
                        car['speed'] -= 56
                    new_cars.append(car)
                await self.bot.cll.update_one({"id": document['id']}, {"$set": {"garage": new_cars}})
            except:
                pass

        await ctx.respond("Done renaming cars of all users")

        # from functions import finduser, updateset
        # # Looping through all collections
        # count = 1
        # dispatcher = {"OV": "Corsia", "Uthana": "Lucoro", "Euthania": "Donvia", "Sadean": "Arkovich", "Narvy": "Zelmor"}
        # for document in await self.bot.cll.find().to_list(length=None):
        #     try:
        #         await self.bot.cll.update_one({"id": document['id']}, {"$set": {"location": dispatcher[document['location']]}})
        #     except:
        #         pass

        # await ctx.respond("Done editing all users")

    @tasks.loop(seconds=60)
    async def donatorlist(self):
        try:
            global donatorlist
            donatorlist = [member['id'] for member in await self.bot.cll.find({"donor": {"$gt": 0}}).to_list(length=None)]
        except:
            pass

def setup(bot):
    bot.add_cog(MainCog(bot))