"""Imports"""
import typing
import discord
import functions
import interclass
from functions import blocked, updateinc, finduser, updateset, getdrive
from discord.commands import slash_command, Option
from discord.ext import commands
import lists
import math
import re

color = discord.Colour

star = u"\u2B50"
lock = u"\U0001f512"

class CarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Check your cars\n/garage [page] [user] [sort] [query]", usage='/garage [page] [user] [sort] [query]')
    async def garage(self, ctx, page: Option(int, "Page", min_value=1) = 1, user: Option(discord.Member, "User to check") = None, sort: Option(str, "Filters", choices=["name","rank","id","id-","alphabet","alphabet-","price","price-","speed","speed-","tuned","tuned-","locked","golden","ovr","ovr-"]) = "id", query: Option(str, "Query for name or rank filter") = None):
      await __import__('slash').garage(self, ctx, page, user, sort, query)

    @slash_command(description="Give a car to another user\nGive multiple cars at once by separating the car IDs with a ',' comma", usage="/givecar <user> <car ID>\n/givecar <user> latest/drive")
    async def givecar(self, ctx, user: Option(discord.Member, "User to give"), cars: Option(str, "Cars to give / 'latest' / 'drive', multiple cars can be separated with a ','")):
      await __import__('slash').givecar(self, ctx, user, cars)

    @slash_command(description="Show the information of a car", usage="/car <car name>")
    async def car(self, ctx, car: Option(str, "Car name")):
      await __import__('slash').car(self, ctx, car)

    @slash_command(description="Show the information of a car you own", usage="/mycar <car ID>\n/mycar lastest/drive")
    async def mycar(self, ctx, carid: Option(str, "Car ID / 'latest' / 'drive'") = None):
      await __import__('slash').mycar(self, ctx, carid)

    @slash_command(description="Reindex your cars", usage="/reindex")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def reindex(self, ctx):
      await __import__('slash').reindex(self, ctx)

    @slash_command(description="Sell a car you own\nGive multiple cars at once by separating the car IDs with a space or a `,`", usage="/sellcar <car ID>\n/sellcar latest/drive")
    async def sellcar(self, ctx, carid: Option(str, "Car ID / 'latest' / 'drive'")):
      await __import__('slash').sellcar(self, ctx, carid)

    @slash_command(description="Tune a car and make its speed faster, there is a chance your car will explode", usage="/tune <car ID>")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tune(self, ctx, carid: Option(str, "Car ID / 'latest' / 'drive'")):
      await __import__('slash').tune(self, ctx, carid)

    @slash_command(description="Upgrade your garage", usage="/upgarage")
    async def upgarage(self, ctx):
      await __import__('slash').upgradegarage(self, ctx)

    @slash_command(description="Lock a car", usage="/lockcar <car ID>")
    async def lockcar(self, ctx, carid: Option(str, "Car ID / 'latest' / 'drive'")):
      await __import__('slash').lockcar(self, ctx, carid)

    @slash_command(description="Unlock a car", usage="/unlockcar <car ID>")
    async def unlockcar(self, ctx, carid: Option(str, "Car ID / 'latest' / 'drive'")):
      await __import__('slash').unlockcar(self, ctx, carid)

    @slash_command(description="Shows the car you are currently driving or pick another car to drive", usage="/drive [car ID]")
    async def drive(self, ctx, carid: Option(str, "Car ID / 'latest'") = None):
      await __import__('slash').drive(self, ctx, carid)
      
    @slash_command(description="Park the car you are currently driving", usage="/park")
    async def park(self, ctx):
      await __import__('slash').park(self, ctx)

    @slash_command(description="Suggest a car to be added into the bot!", usage="/suggest <Car Name> <Car Price in USD> <Car Speed in MPH> <Car Image (Link)> [Car Rank] [Remarks]")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest(self, ctx, name: Option(str, "Full car name"), price: Option(int, "Price in USD"), speed: Option(int, "Car speed in MPH"), image: Option(str, "Image link of the car"), rank: Option(str, "Rank of the car (Leave blank for auto)", choices=["Low", "Average", "High", "Exotic", "Classic"]) = None, remarks: Option(str, "Additional remarks for the devs") = ""):
      await __import__('slash').suggest(self, ctx, name, price, speed, image, rank, remarks)

    @slash_command(description="Add cars to your wishlist to increase the chance of finding it in theft!", usage="/wishlist")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wishlist(self, ctx):
      await __import__('slash').wishlist(self, ctx)

def setup(bot):
    bot.add_cog(CarCog(bot))