"""Imports"""
import discord
from discord.commands import slash_command, Option
from discord.ext import commands

color = discord.Colour

star = u"\u2B50"
lock = u"\U0001f512"

class OtherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Check the latest updates and announcements", usage="/news")
    async def news(self, ctx):
      await __import__('slash').news(self, ctx)

    @slash_command(description="Claim a code or donation reward", usage="/claim [code]")
    async def claim(self, obj, code: Option(str, "Code to claim, put this empty if you are claiming a donation reward") = None):
      await __import__('slash').claim(self, obj, code)

    @slash_command(description="Claim free cash daily", usage="/daily")
    async def daily(self, obj):
      await __import__('slash').daily(self, obj)

    @slash_command(description="Claim free cash weekly", usage="/weekly")
    async def weekly(self, obj):
      await __import__('slash').weekly(self, obj)

    @slash_command(description="Donate to support us!", usage="/donate")
    async def donate(self, obj):
      await __import__('slash').donate(self, obj)

    @slash_command(description="Check out donator perks and rewards", usage="/royalperks")
    async def royalperks(self, obj):
      await __import__('slash').royalperks(self, obj)

    @slash_command(description="Invite the bot to your server", usage="/invite")
    async def invite(self, obj):
      await __import__('slash').invite(self, obj)

    @slash_command(description="Get an invite to our official support server", usage="/server")
    async def server(self, obj):
      await __import__('slash').server(self, obj)

    @slash_command(description="Disable a specific command", usage="/disable <command name> true: Disables a command\n/disable <command name> false: Enables a command")
    @commands.has_permissions(administrator=True)
    async def disable(self, obj, command: Option(str, "Command name"), disable: Option(str, "True or False", choices=["true", "false"])):
      await __import__('slash').disable(self, obj, command, disable)

    @slash_command(description="Gets the bot's latency", usage="/ping")
    async def ping(self, obj):
      await __import__('slash').ping(self, obj)

    @slash_command(description="Gets the user's ID", usage="/id [user]")
    async def id(self, ctx, user: Option(discord.User, "User to check") = None):
      await __import__('slash').id(self, ctx, user)

    @slash_command(description="Upvote the bot for rewards!", usage="/upvote")
    async def vote(self, obj):
      await __import__('slash').vote(self, obj)

    @slash_command(description="Tutorial for the bot", usage="/tutorial")
    async def tutorial(self, obj):
      await __import__('slash').tutorial(self, obj)

    @slash_command(description="Shows ongoing events", usage="/events")
    async def events(self, ctx):
      await __import__('slash').events(self, ctx)

    @slash_command(description="Quarantine yourself from the server", usage="/quarantine")
    @commands.max_concurrency(1, commands.BucketType.user, wait=True)
    async def quarantine(self, ctx):
      await __import__('slash').quarantine(self, ctx)

def setup(bot):
    bot.add_cog(OtherCog(bot))