"""Imports"""
import os
import discord
import functions
from functions import updateinc, finduser, ab, ad, updateset
import lists
from discord.ext import commands
from discord.commands import slash_command, Option
import time
import codes
from datetime import datetime
from importlib import reload
from itertools import islice
import copy
import functions
import asyncio
import psutil
import interclass
import random

color = discord.Colour

star = u"\u2B50"
lock = u"\U0001f512"

class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Reindex guilds or users in database", usage="ov reindex")
    async def reindexdb(self, ctx, mode = None):
      if not ctx.author.id == 615037304616255491:
        return
      if mode == None:
        await ctx.send("Give a mode!")
        return
      elif mode == "guilds":
        ctx.command.reset_cooldown(ctx)
        msg = await ctx.send("Reindexing guilds, please wait.")
        guilds = await self.bot.gcll.find().to_list(length=None)
        guildindex = 1
        for guild in guilds:
          try:
            await self.bot.gcll.update_one({"id": guild['id']}, {"$set": {'index': guildindex}})
          except:
            pass
          guildindex += 1
        await msg.edit("Successfully reindexed all guilds!")
      elif mode == "users":
        ctx.command.reset_cooldown(ctx)
        msg = await ctx.send("Reindexing users, please wait.")
        users = await self.bot.cll.find().to_list(length=await self.bot.cll.count_documents({}))
        userindex = 1
        for user in users:
          try:
            await self.bot.cll.update_one({"id": user['id']}, {"$set": {'index': userindex}})
          except:
            pass
          userindex += 1
        await msg.edit("Successfully reindexed all users!")

    @commands.command(description="Unblocks yourself", usage="ov unblock", aliases=['ub'])
    async def unblock(self, ctx, user: discord.User = None):
      if not ctx.author.id == 615037304616255491:
        return
      user = user or ctx.author
      await self.bot.cll.update_one({"id": user.id}, {"$set": {'blocked': False}})
      await ctx.reply(f"Unblocked **{user}**")

    @commands.command(aliases=['botstatistics'], description="Show the bot's statistics", usage="ov botstats")
    async def botstats(self, ctx):
      userscount = await self.bot.cll.count_documents({})
      serverscount = await self.bot.gcll.count_documents({})
      serverguild = await self.bot.gcll.find_one({"id": 863025676213944340})
      bottotaluptime = serverguild['totaluptime']

      statembed = discord.Embed(title="OV Bot statistics",description=f"**Chunked users:** {len(self.bot.users)}\n**Real users:** {userscount}\n**Total servers:** {serverscount}\n**Real servers:** {len(self.bot.guilds)}\n**Memory usage:** {round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2,2)}MB ({psutil.virtual_memory()[2]}%)\n**CPU usage:** {psutil.cpu_percent()}%\n**Total uptime:** {ab(bottotaluptime)}\n**Latest restart:** {ab(round(time.time())-serverguild['lastrestart'])} ago\n**Bot released on:** 17-8-2021\n\n**__[Join our official server here!](https://discord.gg/bBeCcuwE95)__**\n**__[Invite the bot to your server!](https://discord.com/api/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&redirect_uri=https%3A%2F%2Fovbotdiscord.herokuapp.com%2F&scope=bot%20applications.commands)__**",color=color.blue())
      statembed.set_footer(text="Invite the bot to your server to help us out!")

      await ctx.reply(embed=statembed)

    @commands.command(aliases=['la'], description="Show the bot's latest activity", usage="ov latestactivity", hidden=True)
    async def latestactivity(self, ctx):
      if not ctx.author.id == 615037304616255491:
        return
      server = await self.bot.gcll.find_one({"id": 863025676213944340})
      await ctx.reply(f"Last command exceuted: `{server['lastcmd']}` {ab(round(time.time())-server['lastcmdtime'])} ago by **{server['lastcmduser']} ({server['lastcmduserid']})**\nLatest user: **{server['latestuser']} ({server['latestuserid']})** started `{ab(round(time.time())-server['latestusertime'])}` ago\nLatest restart: **{ab(round(time.time())-server['lastrestart'])}**\n2nd Latest restart: **{ab(round(time.time())-server['2ndlastrestart'])}**\nRestart interval: **{ab(server['lastrestart']-server['2ndlastrestart'])}**\nTotal website visitors: **{server['websitevisitors']}**")

    @commands.command(aliases=['mt'], hidden=True, description="Toggle bot's maintenance mode", usage="ov maintenance <true/false> [time] [reason]")
    async def maintenance(self, ctx, boole = "true", timer = "Almost done", *, reason = "Fixing bugs"):
      if not ctx.author.id == 615037304616255491:
        return
      try:
        boole = boole.lower()
      except:
        pass
      guild = await self.bot.gcll.find_one({"id": 863025676213944340})
      if guild['maintenance'] == True and (boole == "t" or boole == "true"):
        await ctx.reply("Maintenance mode is already enabled!\nType `ov maintenance update <time> <reason>` if you want to update the time and reason!")
        return
      elif guild['maintenance'] == False and (boole == "f" or boole == "false" or boole == "u" or boole == "update"):
        await ctx.reply("Maintenance mode is not even enabled!")
        return
      if boole == "f" or boole == "false":
        await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"maintenance": False, "maintime": 0, "reason": "Fixing bugs"}})
        await ctx.reply("Maintenance mode has been disabled")
        return
      elif boole == "t" or boole == "true":
        try:
          timer = ad(timer)
        except:
          pass
        try:
          await self.bot.cll.update_many({}, {"$set": {'blocked': False}})
          timer = int(timer)
          await ctx.reply(f"Maintenance mode has been enabled\nReason: **{reason}**\nEstimated time: **{ab(timer)}**")
        except:
          await self.bot.cll.update_many({}, {"$set": {'blocked': False}})
          await ctx.reply(f"Maintenance mode has been enabled\nReason: **{reason}**\nEstimated time: **{timer}**")
          pass
        try:
            await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"maintenance": True, "maintime": round(time.time())+timer, "reason": reason}})
        except:
            pass
        return
      elif boole == "u" or boole == "update":
        try:
          timer = ad(timer)
        except:
          pass
        try:
            await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"maintime": round(time.time())+timer}})
        except:
            pass
        if not reason == "Fixing bugs":
          await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"reason": reason}})
          try:
            timer = int(timer)
            await ctx.reply(f"Updated maintenance time and reason\nNew reason: **{reason}**\nNew estimated time: **{ab(timer)}**")
          except:
            await ctx.reply(f"Updated maintenance time and reason\nNew reason: **{reason}**\nNew estimated time: **{timer}**")
            pass
        else:
          try:
            timer = int(timer)
            await ctx.reply(f"Updated maintenance time\nNew estimated time: **{ab(timer)}**")
          except:
            await ctx.reply(f"Updated maintenance time\nNew estimated time: **{timer}**")
            pass

    @commands.command(aliases=['ui'], hidden=True, description="Show the user's information", usage="ov userinfo [user]")
    async def userinfo(self, ctx, user: discord.User = None):
      if user == None:
        user = ctx.author
      if not user.public_flags.all() == []:
        flags = []
        for flag in user.public_flags.all():
          flags.append(str(flag))
        badges = ", ".join(flags)
      else:
        badges = "No badges"

      if user.bot == True:
        uiembed = discord.Embed(title=f"{user.name}#{user.discriminator}",description=f"{user.mention}\nThis user is a Bot",color=user.color)
      else:
        uiembed = discord.Embed(title=f"{user.name}#{user.discriminator}",description=f"{user.mention}\nThis user is not a Bot",color=user.color)
      uiembed.add_field(name="User ID",value=user.id,inline=False)
      uiembed.add_field(name="Account created",value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),inline=False)
      uiembed.add_field(name="Badges",value=badges,inline=False)
      userp = await finduser(user.id)
      if userp is not None:
        uiembed.add_field(name="Last command used", value=f"<t:{userp['lastcmdtime']}> ({ab(round(time.time())-userp['lastcmdtime'])} ago)", inline=False)
      if user.avatar.url != None:
        uiembed.set_thumbnail(url=user.avatar.url)
      uiembed.timestamp = datetime.now()
      await ctx.send(embed=uiembed)

      # joinpos = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=False).index(user) + 1

    @commands.command(aliases=['gi'], hidden=True, description="Show the guild's information", usage="ov guildinfo <guild ID>")
    async def guildinfo(self, ctx, guildid = None):
      if not ctx.author.id == 615037304616255491:
        return
      if guildid == None:
        await ctx.reply("Give a Guild ID")
        return
      await ctx.guild.chunk()
      guild = self.bot.get_guild(int(guildid))
      if guild == None:
        await ctx.reply("Cannot find this guild")
        return
      if guild.features == []:
        features = "No features"
      else:
        features = ", ".join(guild.features)
      if guild.description == "":
        desc = "No description"
      else:
        desc = guild.description
      giembed = discord.Embed(title=f"{guild.name}",description=f"**Guild Description**\n{desc}",color=color.default())
      giembed.add_field(name="Guild ID",value=guild.id,inline=False)
      giembed.add_field(name="Owner",value=f"**Name** {guild.owner}\n**ID** {guild.owner_id}",inline=False)
      giembed.add_field(name="Guild Members",value=f"**Total** {len(guild.members)}\n**Users** {len([m for m in guild.members if not m.bot])}\n**Bots** {len([m for m in guild.members if m.bot])}",inline=False)
      giembed.add_field(name="Guild Created",value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),inline=False)
      if guild.me.joined_at is not None:
        giembed.add_field(name="Bot joined at",value=guild.me.joined_at.strftime("%Y-%m-%d %H:%M:%S"),inline=False)
      giembed.add_field(name="Guild language",value=guild.preferred_locale,inline=False)
      giembed.add_field(name="Features",value=features,inline=False)
      guild.icon is not None and giembed.set_thumbnail(url=guild.icon.url) 
      giembed.timestamp = datetime.now()
      await ctx.send(embed=giembed)

    @commands.command(aliases=['gc','guildchannel'], hidden=True, description="Show the guild's channels", usage="ov guildchannels <guild ID>")
    async def guildchannels(self, ctx, guildid = None, catcount = None):
      if not ctx.author.id == 615037304616255491:
        return
      if guildid == None:
        await ctx.reply("Give a Guild ID")
        return
      guild = self.bot.get_guild(int(guildid))
      if guild == None:
        await ctx.reply("Cannot find this guild")
        return
      if guild.description == None:
        desc = "No description"
      else:
        desc = guild.description
      if catcount == None:
        catcount = 999
      giembed = discord.Embed(title=f"Channels for {guild.name}",description=f"**Guild Description**\n{desc}",color=color.default())
      giembed.add_field(name="Guild ID",value=guild.id,inline=False)
      cat = []
      for category in guild.categories[:int(catcount)]:
        if len(category.channels) > 11:
          categorychannels = list(islice(category.channels, 10))
          categorychannels.append("**Too much channels...**")
        categorychannels = '\n╰ '.join([c.name[:15] + '...' if len(c.name) > 15 else c.name for c in category.channels])
        cat.append(f"**{category.name}**\n╰ {categorychannels}")
      giembed.add_field(name="Channels",value="\n\n".join(cat),inline=False)
      if guild.icon is not None:
        giembed.set_thumbnail(url=guild.icon.url)
      giembed.timestamp = datetime.now()
      await ctx.send(embed=giembed)

    @commands.command(aliases=['ap'], hidden=True, description="Approve suggested cars", usage="ov approve [page]")
    async def approve(self, ctx, page: int = 1):
        if not (ctx.author.id in [1093706075699679242] and ctx.channel.id == 1326965600165040210) and ctx.author.id != 615037304616255491:
            return

        suggestions = (await self.bot.ccll.find_one({"id": "suggestions"}))["cars"]

        if page <= 0:
            page = 1
        elif page > len(suggestions):
            page = len(suggestions)

        suggestion = suggestions[page-1]
        specialty = await functions.carspecialty(self, suggestion["specialty"])
        rank = suggestion["rank"]
        price = suggestion["price"]
        speed = suggestion["speed"]
        name = suggestion["name"]
        remarks = suggestion["remarks"]
        image = suggestion["image"]
        suggestion["approved"] = False
        userid = int(suggestion["specialty"])
        user = await finduser(userid)
        approve = user['approve']
        if price <= 100:
            chance = 0.8
        elif 100 < price <= 500:
            chance = 0.6
        elif 500 < price <= 2000:
            chance = 0.4
        elif 2000 < price:
            chance = 0.1
        if rank == "Classic":
            chance = 0.8
        
        # Approve
        e = discord.Embed(title=name,description=f"Chance: {chance}\nRemarks: {'No remarks' if remarks == '' else remarks}\nTotal cars suggested: {approve}\n\n**Specialty** {specialty}\n**Rank** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH", color=color.random() if rank != "Exotic" else color.default())
        e.set_image(url=image)
        e.set_footer(text=f"Car prices can be a lot higher if it's fast!\nPage {page} of {len(suggestions)}")

        view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
        msg = await ctx.send(embed=e, view=view)
        view.message = msg

        while True:
            await view.wait()

            if view.value is None:
                return
            elif view.value == "left":
                page -= 1
                if page <= 0:
                    page = 1
                suggestion = suggestions[page-1]
                specialty = await functions.carspecialty(self, suggestion["specialty"])
                rank = suggestion["rank"]
                price = suggestion["price"]
                speed = suggestion["speed"]
                name = suggestion["name"]
                remarks = suggestion["remarks"]
                image = suggestion["image"]
                try:
                    if suggestion["approved"] == True:
                        name = name + " (Approved)"
                except:
                    suggestion["approved"] = False
                userid = int(suggestion["specialty"])
                user = await finduser(userid)
                approve = user['approve']
                if price <= 100:
                    chance = 0.8
                elif 100 < price <= 500:
                    chance = 0.6
                elif 500 < price <= 2000:
                    chance = 0.4
                elif 2000 < price:
                    chance = 0.1
                if rank == "Classic":
                    chance = 0.8
            elif view.value == "right":
                page += 1
                if page > len(suggestions):
                    page = len(suggestions)
                suggestion = suggestions[page-1]
                specialty = await functions.carspecialty(self, suggestion["specialty"])
                rank = suggestion["rank"]
                price = suggestion["price"]
                speed = suggestion["speed"]
                name = suggestion["name"]
                remarks = suggestion["remarks"]
                image = suggestion["image"]
                try:
                    if suggestion["approved"] == True:
                        name = name + " (Approved)"
                except:
                    suggestion["approved"] = False
                userid = int(suggestion["specialty"])
                user = await finduser(userid)
                approve = user['approve']
                if price <= 100:
                    chance = 0.8
                elif 100 < price <= 500:
                    chance = 0.6
                elif 500 < price <= 2000:
                    chance = 0.4
                elif 2000 < price:
                    chance = 0.1
                if rank == "Classic":
                    chance = 0.8
            elif view.value == "approve":
                await self.bot.ccll.update_one({"id": "allcars"},{"$push": {"allcars": name}})
                if rank == 'Low':
                    await self.bot.ccll.update_one({"id": "lowcar"},{"$push": {"lowcar": name}})
                elif rank == 'Average':
                    await self.bot.ccll.update_one({"id": "averagecar"},{"$push": {"averagecar": name}})
                elif rank == 'High':
                    await self.bot.ccll.update_one({"id": "highcar"},{"$push": {"highcar": name}})
                elif rank == 'Exotic':
                    await self.bot.ccll.update_one({"id": "exoticcar"},{"$push": {"exoticcar": name}})
                elif rank == 'Classic':
                    await self.bot.ccll.update_one({"id": "classiccar"},{"$push": {"classiccar": name}})
                elif rank == 'Exclusive':
                    await self.bot.ccll.update_one({"id": "exclusivecar"},{"$push": {"exclusivecar": name}})

                await self.bot.ccll.update_one({"id": "carprice"},{"$set": {f"carprice.{name}": price}})
                await self.bot.ccll.update_one({"id": "carspeed"},{"$set": {f"carspeed.{name}": speed}})
                await self.bot.ccll.update_one({"id": "carimage"},{"$set": {f"carimage.{name}": image}})
                await self.bot.ccll.update_one({"id": "carchance"},{"$set": {f"carchance.{name}": round(chance,2)}})
                await self.bot.ccll.update_one({"id": "carspecialty"}, {"$set": {f"carspecialty.{name}": suggestion['specialty']}})

                e = discord.Embed(title=name,description=f"{('**Specialty** ' + specialty) if specialty is not None and specialty != '' else ''}\n**Rank** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH",color=color.random() if rank != "Exotic" else color.default())
                e.set_image(url=image)
                e.set_footer(text="Car prices can be a lot higher if it's fast!")
                await msg.reply(content=f"Car added successfully!\n**{name}** with a **{round(chance*100)}%** stealing chance",embed=e)

                await self.bot.ccll.update_one({"id": "suggestions"}, {"$pull": {"cars": {"name": suggestion["name"]}}})
                await self.bot.cll.update_one({"id": userid}, {"$inc": {"approve": 1}})
                
                try:
                    dm = self.bot.get_user(int(suggestion["specialty"]))
                except:
                    dm = self.bot.get_user(userid)
                if dm is not None:
                    rembed = discord.Embed(title="Car suggestion update", description=f"Your car suggestion **{name}** has been approved!", color=color.green())
                    rembed.add_field(name="Note", value="You will be able to see your car after the next bot restart")
                    rembed.set_image(url=image)
                    rembed.set_footer(text="Bot restart happens when there is a new update")
                    await dm.send(embed=rembed)

                suggestion["approved"] = True
                name = name + " (Approved)"

            elif view.value == "reject":
                modal = interclass.Reject("Provide a valid reason")
                await view.interaction.response.send_modal(modal)
                await modal.wait()
                if modal.value == "":
                    view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
                    view.message = await msg.edit(view=view)
                    continue

                e = discord.Embed(title="Car suggestion rejected",description=f"Car suggestion **{name}**\n{specialty} was rejected by {modal.interaction.user} for the following reason:\n**{modal.value}**", color=color.red())

                await modal.interaction.channel.send(embed=e)

                await self.bot.ccll.update_one({"id": "suggestions"}, {"$pull": {"cars": {"name": suggestion["name"]}}})

                try:
                    dm = self.bot.get_user(int(suggestion["specialty"]))
                except:
                    dm = self.bot.get_user(userid)
                if dm is not None:
                    rembed = discord.Embed(title="Car suggestion update", description=f"Your car suggestion **{name}** has been rejected by {modal.interaction.user}!", color=color.red())
                    rembed.add_field(name="Reason", value=modal.value)
                    rembed.set_footer(text="You can always suggest it again in the future!")
                    await dm.send(embed=rembed)

                suggestion["approved"] = True
            elif view.value == "modify":
                modal = interclass.Modify(suggestion['name'], suggestion['price'], suggestion['speed'], suggestion['rank'], chance)
                await view.interaction.response.send_modal(modal)
                await modal.wait()
                if modal.children[0].value == '' and modal.children[1].value == '' and modal.children[2].value == '' and modal.children[3].value == '' and modal.children[4].value == '':
                    view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
                    view.message = await msg.edit(view=view)
                    continue

                if modal.children[0].value != '':
                    name = modal.children[0].value
                if modal.children[1].value != '':
                    price = int(modal.children[1].value)
                if modal.children[2].value != '':
                    speed = int(modal.children[2].value)
                if modal.children[3].value != '':
                    if modal.children[3].value.lower() in "low":
                        rank = "Low"
                    elif modal.children[3].value.lower() in "average":
                        rank = "Average"
                    elif modal.children[3].value.lower() in "high":
                        rank = "High"
                    elif modal.children[3].value.lower() in "exotic":
                        rank = "Exotic"
                    elif modal.children[3].value.lower() in "classic":
                        rank = "Classic"
                    elif modal.children[3].value.lower() in "exclusive":
                        rank = "Exclusive"
                    else:
                        await modal.interaction.channel.send(f"Invalid rank provided `{rank}`")
                        view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
                        view.message = await msg.edit(view=view)
                        continue
                if modal.children[4].value != '':
                    chance = float(modal.children[4].value)
                
            elif view.value == "modify2":
                modal = interclass.Modify2(suggestion['specialty'])
                await view.interaction.response.send_modal(modal)
                await modal.wait()
                if modal.children[0].value == '' and modal.children[1].value == '':
                    view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
                    view.message = await msg.edit(view=view)
                    continue
                
                if modal.children[0].value != '':
                    suggestion['specialty'] = modal.children[0].value
                if modal.children[1].value != '':
                    image = modal.children[1].value

            
            if "approved" not in suggestion:
                suggestion["approved"] = False
            try:
                user = await finduser(int(suggestion["specialty"]))
            except:
                user = await finduser(userid)
            approve = user['approve']
            
            # Approve
            e = discord.Embed(title=name,description=f"Chance: {chance}\nRemarks: {'No remarks' if remarks == '' else remarks}\nTotal cars suggested: {approve}\n\n**Specialty** {specialty}\n**Rank** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH", color=color.random() if rank != "Exotic" else color.default())
            e.set_image(url=image)
            e.set_footer(text=f"Car prices can be a lot higher if it's fast!\nPage {page} of {len(suggestions)}")

            view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
            try:
                view.message = await msg.edit(embed=e, view=view)
            except:
                await modal.interaction.channel.send(f"Invalid image provided `{image}`")
                suggestion['image'] = image
                view = interclass.Approve(ctx, page == 1, suggestion["approved"], page == len(suggestions))
                view.message = await msg.edit(view=view)

    @commands.command(aliases=['ac'], hidden=True, description="Add a new car to the database", usage="ov addcar <car name> <price> <speed> <image> <chance> [specialty] [golden: true/false] [golden car image]")
    async def addcar(self, ctx, name: str = None, price: int = None, speed: int = None, image: str = None, chance: float = None, specialty: str = None, golden: str = False, goldenimage: str = None):
      if not ctx.author.id == 615037304616255491:
        return
      if name == None:
        await ctx.reply("Give a car name!\nUsage: `ov addcar \"<name>\" <price> <speed> <image link> <chance> [specialty] [golden: true/false/none] [golden image link]`\n\"chance\" to check average chances")
        return
      if name == "chance":
        await ctx.reply("Low cars: 0.8\nAverage cars: 0.6\nHigh cars: 0.4\nExotic cars: 0.1")
        return
      elif name == "l" or name == "latest":
        car = await self.bot.ccll.find_one({"id": "allcars"})
        car = car['allcars'][-1]
        await ctx.reply(f"Latest added car is **{car}**")
        return
      if price == None:
        await ctx.reply("Enter the car's price!")
        return
      if speed == None:
        await ctx.reply("Enter the car's speed!")
        return
      if image == None:
        await ctx.reply("Enter the car's image link!")
        return
      if chance == None:
        await ctx.reply("Enter the car's stealing chance!")
        return
      if golden in ["false","true"]:
        golden = bool(golden)
        if golden == True and goldenimage == None:
          await ctx.reply("Enter the car's golden image link!")
          return
        if ".gif" in image and golden == False:
          await ctx.reply("GIF is allowed only if there is golden car image")
          return
      else:
        if golden == "none":
          golden = None
      if golden != True and golden != False and golden != None:
        await ctx.reply(f"Invalid golden input `{golden}`")
        return
      await self.bot.ccll.update_one({"id": "allcars"},{"$push": {"allcars": name}})
      if price <= 100:
        tier = 'l'
      elif 100 < price <= 500:
        tier = 'a'
      elif 500 < price <= 2000:
        tier = 'h'
      elif 2000 < price:
        tier = 's'
      if tier == 'l':
        await self.bot.ccll.update_one({"id": "lowcar"},{"$push": {"lowcar": name}})
        rank = "Low"
      elif tier == 'a':
        await self.bot.ccll.update_one({"id": "averagecar"},{"$push": {"averagecar": name}})
        rank = "Average"
      elif tier == 'h':
        await self.bot.ccll.update_one({"id": "highcar"},{"$push": {"highcar": name}})
        rank = "High"
      elif tier == 's':
        await self.bot.ccll.update_one({"id": "exoticcar"},{"$push": {"exoticcar": name}})
        rank = "Exotic"
      await self.bot.ccll.update_one({"id": "carprice"},{"$set": {f"carprice.{name}": price, }})
      await self.bot.ccll.update_one({"id": "carspeed"},{"$set": {f"carspeed.{name}": speed}})
      await self.bot.ccll.update_one({"id": "carimage"},{"$set": {f"carimage.{name}": image}})
      await self.bot.ccll.update_one({"id": "carchance"},{"$set": {f"carchance.{name}": round(chance,2)}})
      if specialty is not None and specialty != "" and specialty != "none":
        await self.bot.ccll.update_one({"id": "carspecialty"}, {"$set": {f"carspecialty.{name}": specialty}})
      
        specialty = await functions.carspecialty(self, specialty)
      if golden == True:
        await self.bot.ccll.update_one({"id": "goldencars"},{"$push": {"goldencars": name}})
        await self.bot.ccll.update_one({"id": "goldencarimage"},{"$set": {f"goldencarimage.{name}": goldenimage}})
        e = discord.Embed(title=name,description=f"{('**Specialty** ' + specialty) if specialty is not None and specialty != '' else ''}\n**Rank** {rank}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH",color=color.random() if rank != "Exotic" else color.default())
        e.set_image(url=image)
        e.set_footer(text="Car prices can be a lot higher if it's fast!")
        await ctx.reply(content=f"Car added successfully!\n**{name}** with a **{round(chance*100)}%** stealing chance\nPreview:",embed=e)
        e = discord.Embed(title=f"{star} Golden "+name,description=f"{('**Specialty** ' + specialty) if specialty is not None and specialty != '' else ''}\n**Rank** {rank}\n**Base Price:** <:cash:1329017495536930886> {round(price*2)}\n**Average Speed:** {speed} MPH")
        e.set_image(url=goldenimage)
        e.set_footer(text="Car prices can be a lot higher if it's fast!")
        await ctx.reply(content=f"**{star} Golden {name}**\nPreview:",embed=e)
      else:
        e = discord.Embed(title=name,description=f"{('**Specialty** ' + specialty) if specialty is not None and specialty != '' else ''}\n**Rank** {rank}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH",color=color.random() if rank != "Exotic" else color.default())
        if golden == None:
          await self.bot.ccll.update_one({"id": "nogolden"},{"$push": {"cars": name}})
          e.description += "\n(This car has no golden version)"
        e.set_image(url=image)
        e.set_footer(text="Car prices can be a lot higher if it's fast!")
        await ctx.reply(content=f"Car added successfully!\n**{name}** with a **{round(chance*100)}%** stealing chance",embed=e)

    # @commands.command(aliases=['rc'], hidden=True, description="Removes a car from the database", usage="ov removecar <car name>")
    # async def removecar(self, ctx, *, name: str = None):
    #   if not ctx.author.id == 615037304616255491:
    #     return
    #   if name == None:
    #     await ctx.reply("Enter a car name to remove!")
    #     return
    #   allcars = await self.bot.ccll.find_one({"id": "allcars"})
    #   if not name in allcars['allcars']:
    #     await ctx.reply("Cannot find this car!")
    #     return
    #   await self.bot.ccll.update_one({"id": "allcars"},{"$pull": {"allcars": name}})
    #   lowcar = await self.bot.ccll.find_one({"id": "lowcar"})
    #   averagecar = await self.bot.ccll.find_one({"id": "averagecar"})
    #   highcar = await self.bot.ccll.find_one({"id": "highcar"})
    #   exoticcar = await self.bot.ccll.find_one({"id": "exoticcar"})
    #   if name in lowcar['lowcar']:
    #     await self.bot.ccll.update_one({"id": "lowcar"},{"$pull": {"lowcar": name}})
    #   elif name in averagecar['averagecar']:
    #     await self.bot.ccll.update_one({"id": "averagecar"},{"$pull": {"averagecar": name}})
    #   elif name in highcar['highcar']:
    #     await self.bot.ccll.update_one({"id": "highcar"},{"$pull": {"highcar": name}})
    #   elif name in exoticcar['exoticcar']:
    #     await self.bot.ccll.update_one({"id": "exoticcar"},{"$pull": {"exoticcar": name}})
    #   await self.bot.ccll.update_one({"id": "carprice"},{"$unset": {f"carprice.{name}": 1}})
    #   await self.bot.ccll.update_one({"id": "carspeed"},{"$unset": {f"carspeed.{name}": 1}})
    #   await self.bot.ccll.update_one({"id": "carimage"},{"$unset": {f"carimage.{name}": 1}})
    #   await self.bot.ccll.update_one({"id": "carchance"},{"$unset": {f"carchance.{name}": 1}})
    #   await self.bot.ccll.update_one({"id": "carspecialty"},{"$unset": {f"carspecialty.{name}": 1}})
    #   goldencars = await self.bot.ccll.find_one({"id": "goldencars"})
    #   if name in goldencars['goldencars']:
    #     await self.bot.ccll.update_one({"id": "goldencars"},{"$pull": {"goldencars": name}})
    #     await self.bot.ccll.update_one({"id": "goldencarimage"},{"$unset": {f"goldencarimage.{name}": 1}})
    #   nogolden = await self.bot.ccll.find_one({"id": "nogolden"})
    #   if name in nogolden["cars"]:
    #     await self.bot.ccll.update_one({"id": "nogolden"},{"$pull": {"cars": name}})

    #   await ctx.reply(f"Car removed successfully!\n**{name}**")

    @commands.command(aliases=['rename', 'rc'], hidden=True, description="Rename a car", usage="ov renamecar <old car name> <new car name>")
    async def renamecar(self, ctx, name: str = None, new_name: str = None):
      if not (ctx.author.id in [1093706075699679242] and ctx.channel.id == 1326965600165040210) and ctx.author.id != 615037304616255491:
        return
      if name == None:
        await ctx.reply("Enter the old name of the car!")
        return
      if new_name == None:
        await ctx.reply("Enter the new name of the car!")
        return

      await ctx.reply("Renaming car in users garage")

      for document in await self.bot.cll.find().to_list(length=None):
          try:
              cars = document['garage']
              new_cars = []
              for car in cars:
                  if car['name'] == name:
                      car['name'] = new_name
                  new_cars.append(car)
              await self.bot.cll.update_one({"id": document['id']}, {"$set": {"garage": new_cars}})
          except:
              pass

      await ctx.send(f"Done renaming car **{name}** to **{new_name}** and cars in garage of all users")

      if not name in lists.allcars:
        try:
          if len(name) < 2:
            await ctx.reply("Enter at least 2 letters to search")
            return
          closematch = [x for x in lists.allcars if name in x.lower() or name in x.lower().replace(" ","")]
          if len(closematch) > 1:
            await ctx.reply(f"I found more than one car that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
            return
          else:
            name = closematch[0]
        except:
          await ctx.reply("Cannot find this vehicle, make sure you typed the full name of the vehicle!")
          return

      await self.bot.ccll.update_one({"id": "allcars"},{"$pull": {"allcars": name}})
      await self.bot.ccll.update_one({"id": "allcars"},{"$push": {"allcars": new_name}})
      lists.allcars.remove(name)
      lists.allcars.append(new_name)
      if name in lists.lowcar:
        await self.bot.ccll.update_one({"id": "lowcar"},{"$pull": {"lowcar": name}})
        await self.bot.ccll.update_one({"id": "lowcar"},{"$push": {"lowcar": new_name}})
        lists.lowcar.remove(name)
        lists.lowcar.append(new_name)
      elif name in lists.averagecar:
        await self.bot.ccll.update_one({"id": "averagecar"},{"$pull": {"averagecar": name}})
        await self.bot.ccll.update_one({"id": "averagecar"},{"$push": {"averagecar": new_name}})
        lists.averagecar.remove(name)
        lists.averagecar.append(new_name)
      elif name in lists.highcar:
        await self.bot.ccll.update_one({"id": "highcar"},{"$pull": {"highcar": name}})
        await self.bot.ccll.update_one({"id": "highcar"},{"$push": {"highcar": new_name}})
        lists.highcar.remove(name)
        lists.highcar.append(new_name)
      elif name in lists.exoticcar:
        await self.bot.ccll.update_one({"id": "exoticcar"},{"$pull": {"exoticcar": name}})
        await self.bot.ccll.update_one({"id": "exoticcar"},{"$push": {"exoticcar": new_name}})
        lists.exoticcar.remove(name)
        lists.exoticcar.append(new_name)
      elif name in lists.classiccar:
        await self.bot.ccll.update_one({"id": "classiccar"},{"$pull": {"classiccar": name}})
        await self.bot.ccll.update_one({"id": "classiccar"},{"$push": {"classiccar": new_name}})
        lists.classiccar.remove(name)
        lists.classiccar.append(new_name)
      elif name in lists.exclusivecar:
        await self.bot.ccll.update_one({"id": "exclusivecar"},{"$pull": {"exclusivecar": name}})
        await self.bot.ccll.update_one({"id": "exclusivecar"},{"$push": {"exclusivecar": new_name}})
        lists.exclusivecar.remove(name)
        lists.exclusivecar.append(new_name)

      await self.bot.ccll.update_one({"id": "carprice"},{"$rename": {f"carprice.{name}": f"carprice.{new_name}"}})
      lists.carprice.remove(name)
      lists.carprice.append(new_name)
      await self.bot.ccll.update_one({"id": "carspeed"},{"$rename": {f"carspeed.{name}": f"carspeed.{new_name}"}})
      lists.carspeed.remove(name)
      lists.carspeed.append(new_name)
      await self.bot.ccll.update_one({"id": "carimage"},{"$rename": {f"carimage.{name}": f"carimage.{new_name}"}})
      lists.carimage.remove(name)
      lists.carimage.append(new_name)
      await self.bot.ccll.update_one({"id": "carchance"},{"$rename": {f"carchance.{name}": f"carchance.{new_name}"}})
      lists.carchance.remove(name)
      lists.carchance.append(new_name)

      if name in lists.specialty:
        await self.bot.ccll.update_one({"id": "carspecialty"}, {"$rename": {f"carspecialty.{name}": f"carspecialty.{new_name}"}})
        lists.specialty.remove(name)
        lists.specialty.append(new_name)
      if name in lists.goldencars:
        await self.bot.ccll.update_one({"id": "goldencars"},{"$pull": {"goldencars": name}})
        await self.bot.ccll.update_one({"id": "goldencars"},{"$push": {"goldencars": new_name}})
        lists.goldencars.remove(name)
        lists.goldencars.append(new_name)
      if name in lists.nogolden:
        await self.bot.ccll.update_one({"id": "nogolden"},{"$pull": {"cars": name}})
        await self.bot.ccll.update_one({"id": "nogolden"},{"$push": {"cars": new_name}})
        lists.nogolden.remove(name)
        lists.nogolden.append(new_name)
      if name in lists.goldencarimage:
        await self.bot.ccll.update_one({"id": "goldencarimage"},{"$rename": {f"goldencarimage.{name}": f"goldencarimage.{new_name}"}})
        lists.goldencarimage.remove(name)
        lists.goldencarimage.append(new_name)

      await self.bot.ccll.update_one({"id": "exclusive"},{"$rename": {f"amount.{name}": f"amount.{new_name}"}})

    @commands.command(aliases=['ci'], hidden=True, description="Change a car image", usage="ov changeimage <car name> <image>")
    async def changeimage(self, ctx, name: str = None, image: str = None):
      if not (ctx.author.id in [1093706075699679242] and ctx.channel.id == 1326965600165040210) and ctx.author.id != 615037304616255491:
            return
      if name == None:
        await ctx.reply("Enter the name of the car!")
        return
      if image == None:
        await ctx.reply("Enter the new image link to change!")
        return

      if not name in lists.allcars:
        try:
          if len(name) < 2:
            await ctx.send("Enter at least 2 letters to search")
            return
          closematch = [x for x in lists.allcars if name in x.lower() or name in x.lower().replace(" ","")]
          if len(closematch) > 1:
            await ctx.send(f"I found more than one car that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
            return
          else:
            name = closematch[0]
        except:
          await ctx.send("Cannot find this vehicle, make sure you typed the full name of the vehicle!")
          return

      await self.bot.ccll.update_one({"id": "carimage"},{"$set": {f"carimage.{name}": image}})

      e = discord.Embed(title=name, description="Car image successfully changed", color=color.random())
      e.set_image(url=image)
      e.set_footer(text="Car prices can be a lot higher if it's fast!")
      await ctx.reply(embed=e)

    @commands.command(hidden=True, aliases=['ai'], description="Add a new item to the database", usage="ov additem <name> <id> <description> <category: normal, weapon, melee, drug, background, back, skin, head, chest, leg, foot, face, hair, foods, usables> <obtainable> <buyable: boolean> <price> <token: boolean>")
    async def additem(self, ctx, name: str = None, id: str = None, description: str = None, category: str = None, obtainable: bool = True, buyable: bool = False, price: int = 0, token: bool = False):
      if not ctx.author.id == 615037304616255491:
        return
      category = category.lower()
      valid_category = ["normal", "foods", "weapon", "drug", "background", "back", "skin", "head", "chest", "leg", "foot", "face", "usables", "melee", "hair"]
      wearables = ["background", "back", "skin", "head", "chest", "leg", "foot", "face", "hair"]
      if name is None:
        await ctx.send("Provide the name of the item")
        return
      elif id is None:
        await ctx.send("Provide the id of the item")
        return
      elif description is None:
        await ctx.send("Provide the item description")
        return
      elif category is None:
        await ctx.send("Provide the category of the item")
        return
      elif category not in valid_category:
        await ctx.send(f"Category can only be one of these: `{', '.join(valid_category)}`")
        return
      elif not obtainable and buyable:
        await ctx.send("Cannot be unobtainable and buyable at the same time!")
        return
      elif buyable and price == 0:
        await ctx.send("Price cannot be free!")
        return
      if category != "normal":
        await self.bot.dll.update_one({"id": "items"}, {"$push": {"allitem": name, category: name}, "$set": {f"item_id.{name}": id, f"item_description.{name}": description}})
        if category == "melee":
          await self.bot.dll.update_one({"id": "items"}, {"$push": {"weapon": name}})
      else:
        await self.bot.dll.update_one({"id": "items"}, {"$push": {"allitem": name}, "$set": {f"item_id.{name}": id, f"item_description.{name}": description}})
      if category in wearables:
        await self.bot.dll.update_one({"id": "items"}, {"$push": {"wearables": name}})
      if price != 0:
        await self.bot.dll.update_one({"id": "items"}, {"$push": {"bitem": name}, "$set": {f"item_prices.{name}": price}})
        if token:
          await self.bot.dll.update_one({"id": "items"}, {"$push": {"titem": name}})
      if not obtainable:
        await self.bot.dll.update_one({"id": "items"}, {"$push": {"unobtainable": name}})

      user = await finduser(ctx.author.id)
      userstorage = user['storage']
      try:
        itemowned = userstorage[name]
      except:
        itemowned = "Not owned"
      if token:
        price = 'Cannot be sold'
      itemembed = discord.Embed(title=name,description=description,color=color.blue())
      itemembed.add_field(name="Information",value=f"**Item ID:** `{id}`\n**Price:** {f'<:cash:1329017495536930886> {price}' or 'Cannot be sold'}\n**Item Owned:** {itemowned}")
      itemembed.set_footer(text="cheap item")

      if os.path.exists(f"images/{name.lower().replace(' ', '_')}.png"):
        file = discord.File(f"images/{name.lower().replace(' ', '_')}.png")
        itemembed.set_thumbnail(url=f"attachment://{name.lower().replace(' ', '_')}.png")
        await ctx.send(f"Successfully added item **{name}**!", embed=itemembed, file=file)
        return

      await ctx.send(f"Successfully added item **{name}**!", embed=itemembed)

    @commands.command(hidden=True, description="Removes an item from the database", usage="ov removeitem <name>")
    async def removeitem(self, ctx, *, name: str = None):
      if not ctx.author.id == 615037304616255491:
        return
      items = await self.bot.dll.find_one({"id": "items"})
      removed = False
      for l in items:
        if isinstance(l, list):
          if name in items[l]:
            await self.bot.dll.update_one({"id": "items"}, {"$pull": {l: name}})
            removed = True
        elif isinstance(l, dict):
          if name in items[l]:
            await self.bot.dll.update_one({"id": "items"}, {"$unset": {name: 1}})
            removed = True

      if removed:
        await ctx.send(f"Successfully removed item `{name}`")
      else:
        await ctx.send(f"Unable to remove item: `{name}` Not found")

    @commands.command(aliases=['ti'], hidden=True, description="Test if an image is valid", usage="ov testimage <image>")
    async def testimage(self, ctx, image):
      if not ctx.author.id == 615037304616255491:
        return
      e = discord.Embed(title="Testing Image",description=f"Image link: {image}",color=color.green())
      e.set_image(url=image)
      await ctx.reply(embed=e)

    @commands.command(hidden=True, description="Add cash to a user's account", usage="ov acs [user]", aliases=["acs"])
    async def addcash(self, ctx, amount: int, user: discord.User = None):
      if not ctx.author.id == 615037304616255491:
        return
      user = user or ctx.author
      await updateinc(user.id, 'cash', amount)
      await ctx.send(f"Added <:cash:1329017495536930886> {amount} to {user}'s account")

    @commands.command(aliases=['gmg'], hidden=True, description="Get mutual guilds of a user", usage="ov getmutualguilds <user>")
    async def getmutualguilds(self, ctx, user: discord.User = None):
      if user is None:
        await ctx.send("Provide a user!")
        return
      mutual = [x.name + ": " + str(x.id) for x in user.mutual_guilds]
      if len(mutual) == 0:
        await ctx.send("No mutual guilds found")
        return
      await ctx.send(f"**Mutual guilds with {user.name}**\n" + '\n'.join(mutual))

    @commands.command(aliases=['cu'], hidden=True, description="Clean up fake users/guilds", usage="ov cleanup users\nov cleanup guilds")
    async def cleanup(self, ctx, mode = None):
      if ctx.author.id != 615037304616255491:
        return
      if mode is None:
        await ctx.send("Provide a mode to clean, `users` or `guilds`")
        return
      elif mode == "users":
        await ctx.send("Fetching users, please wait...")
        users = await self.bot.cll.find().to_list(length=await self.bot.cll.count_documents({}))
        latestuser = await self.bot.cll.find_one({"$query": {}, "$orderby": {"index": -1}})
        fakeusers = [user for user in [user for user in users if self.bot.get_user(int(user['id'])) is not None] if (self.bot.get_user(int(user['id'])).mutual_guilds is None and user['cmd'] < 10) or (self.bot.get_user(int(user['id'])).mutual_guilds is not None and user['cmd'] < 10 and not ((latestuser['index'] - user['index']) <= 10))] + [user for user in users if (self.bot.get_user(int(user['id'])) is None and user['cmd'] < 10)]
        if len(fakeusers) == 0:
          await ctx.send("No fake users found")
          return
        fakeusersname = ", ".join([user['name'] for user in fakeusers])
        view = interclass.Confirm(ctx, ctx.author)
        view.message = await ctx.send(content="_ _",embed=discord.Embed(title="Cleaning fake users", description=f"Total fake users found: **{len(fakeusers)}**\nUsers: **{fakeusersname}**", color=color.green()), view=view)
        await view.wait()
        if view.value is None or view.value is False:
          await ctx.send("Cleaning users cancelled.")
          return
        msg = await ctx.send("Cleaning up users, please wait...")
        await self.bot.cll.delete_many({"id": {"$in": [user['id'] for user in fakeusers]}})
        await msg.edit(content=f"Successfully cleaned up all fake users\n**{fakeusersname}**")
      elif mode == "guilds":
        await ctx.send("Fetching guilds, please wait...")
        guilds = await self.bot.gcll.find().to_list(length=await self.bot.gcll.count_documents({}))
        fakeguilds = [guild for guild in guilds if self.bot.get_guild(guild['id']) is None]
        fakeguilds2 = [guild for guild in self.bot.guilds if guild.id not in [g['id'] for g in guilds]]
        if len(fakeguilds) == 0 and len(fakeguilds2) == 0:
          await ctx.send("No fake guilds found")
          return
        fakeguildsname = ", ".join([guild['name'] + f" ({guild['id']})" for guild in fakeguilds][:20]) + (", " if len(fakeguilds) else "") + ", ".join([guild.name + f" ({guild.id})" for guild in fakeguilds2][:20])
        view = interclass.Confirm(ctx, ctx.author)
        view.message = await ctx.send(content="_ _",embed=discord.Embed(title="Cleaning fake guilds", description=f"Total fake guilds found: **{len(fakeguilds+fakeguilds2)}**\nGuilds: **{fakeguildsname}**", color=color.green()), view=view)
        await view.wait()
        if view.value is None or view.value is False:
          await ctx.send("Cleaning guilds cancelled.")
          return
        msg = await ctx.send("Cleaning up guilds, please wait...")
        await self.bot.gcll.delete_many({"id": {"$in": [guild['id'] for guild in fakeguilds]}})
        for guild in fakeguilds2:
          await guild.leave()
        await msg.edit(content=f"Successfully cleaned up all fake guilds\n**{fakeguildsname}**")

    @commands.command(aliases=['lg'], hidden=True, description="Leave a guild while removing the guild data from database", usage="ov leaveguild <guild ID>")
    async def leaveguild(self, ctx, guildid = None):
        if not ctx.author.id == 615037304616255491:
            return
        if guildid is None:
            await ctx.send("Provide a guild ID!")
            return
        guild = self.bot.get_guild(int(guildid))
        if guild is None:
            await ctx.send("Cannot find this guild")
            return
        view = interclass.Confirm(ctx, ctx.author)
        view.message = await ctx.send(f"Are you sure you want to leave this guild **{guild.name} ({guild.id})**?", view=view)
        await view.wait()
        if view.value is None or view.value is False:
          await ctx.send("Leaving guild cancelled")
          return
        await guild.leave()
        await self.bot.gcll.delete_one({"id": guild.id})
        await ctx.send(f"Successfully left guild **{guild.name} ({guild.id})**")

    @commands.command(aliases=['ginv'], hidden=True, description="Get an invite from a guild", usage="ov getinvite <guild ID>")
    async def getinvite(self, ctx, guildid = None):
        if not ctx.author.id == 615037304616255491:
            return
        if guildid is None:
            await ctx.send("Provide a guild ID!")
            return
        guild = self.bot.get_guild(int(guildid))
        if guild is None:
            await ctx.send("Cannot find this guild")
            return
        invite = await guild.channels[0].create_invite(max_age=600)
        await ctx.send(f"Invite link for {guild.name}\n{invite.url}")

    @commands.command(hidden=True, description="Sudo a user to invoke a command", usage="ov sudo <user> <command> [args]")
    async def sudo(self, ctx, user: discord.User, *, command: str):
      if not ctx.author.id == 615037304616255491:
        await ctx.send("Only legends can use this command")
        return
      if user is None:
        await ctx.reply("Who is your sudo target?")
        return
      if user == ctx.author:
        await ctx.reply("You can't sudo yourself")
        return
      if command is None:
        await ctx.reply("Provide a command")
        return
      msg = copy.copy(ctx.message)
      msg.channel = ctx.channel
      msg.author = user
      msg.content = ctx.prefix + command
      new_ctx = await self.bot.get_context(msg, cls=type(ctx))
      await self.bot.invoke(new_ctx)

    @slash_command(hidden=True, description="Sudo a user to invoke a command", usage="ov sudo <user> <command> [args]")
    async def sudo(self, ctx, user: discord.User, *, command: str):
      if not ctx.author.id == 615037304616255491:
        await ctx.send("Only legends can use this command")
        return
      if user is None:
        await ctx.respond("Who is your sudo target?")
        return
      if user == ctx.author:
        await ctx.respond("You can't sudo yourself")
        return
      if command is None:
        await ctx.respond("Provide a command")
        return

      com = self.bot.get_application_command(command.split(" ")[0])
      if not com:
        await ctx.respond(f"Cannot find this command `{command.split(' ')[0]}`")
        return
      ctx.command = com
      ctx.author = user
      ctx.user = user
      args = command.split(" ", 1)[1:]
      await com(ctx, *command.split(" ", 1)[1:])

    @commands.command(hidden=True, description="Reload cogs", usage="ov reloadcogs [cog]", aliases=['rcogs'])
    async def reloadcogs(self, ctx, cog = None):
        if not ctx.author.id == 615037304616255491:
            return
        if cog is None:
            await ctx.send("Reloading cogs")
            for extension in self.bot.exten:
                try:
                    self.bot.reload_extension(extension)
                except:
                  raise
            await ctx.send("Reloaded all cogs")
        else:
            await ctx.send(f"Reloading `{cog.lower()}` cog")
            if not os.path.isfile(f"cogs/{cog.lower()}.py"):
                await ctx.send(f"Could not find this cog `{cog}`")
                return
            try:
                self.bot.reload_extension(f"cogs.{cog.lower()}")
            except:
              raise
            await ctx.send(f"Reloaded `{cog.lower()}` cog")

    @commands.command(hidden=True, description="Reload modules", usage="ov reloadmodules [module]", aliases=['rmods'])
    async def reloadmodules(self, ctx, module = None):
        if not ctx.author.id == 615037304616255491:
            return
        if module is None:
            await ctx.send("Reloading all modules")
            for mod in [lists, functions, interclass, codes, __import__("slash")]:
                try:
                    reload(mod)
                except:
                  raise
            await ctx.send("Reloaded all modules")
        else:
            await ctx.send(f"Reloading {module.lower()} module")
            if module.lower() not in ["lists", "functions", "interclass", "codes", "slash"]:
                await ctx.send(f"Cannot find this module `{module}`")
            dictionary = {"lists": lists, "functions": functions, "interclass": interclass, "codes": codes, "slash": __import__("slash")}
            try:
                reload(dictionary[module.lower()])
            except:
                raise
            await ctx.send(f"Reloaded {module.lower()} module")

    @commands.command(hidden=True, description="Reset all cooldowns", usage="ov resetcooldown [user]", aliases=['res'])
    async def resetcooldown(self, ctx, user: discord.User = None):
        if not ctx.author.id == 615037304616255491:
            return
        user = user or ctx.author
        for command in self.bot.walk_commands():
            command.reset_cooldown(ctx)
        for command in self.bot.walk_application_commands():
            if isinstance(command, discord.SlashCommandGroup):
                continue
            command.reset_cooldown(ctx)
        await ctx.send(f"All cooldowns for **{user.name}** has been resetted")

    @commands.command(hidden=True, description="Make a global bot announcement", usage="ov announce <contents>")
    async def announce(self, ctx, *, contents = None):
      if not ctx.author.id == 615037304616255491:
        return
      if contents is None:
        await ctx.send("Announcement contents cannot be empty!")
        return
      if "```" not in contents or contents.count("`") < 6:
        await ctx.send("Announcement contents must be wrapped in triple backticks!")
        return
      await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"announcement.{round(time.time())}": ''.join(contents.split('```')).strip()}})
      embed = discord.Embed(title="Successfully made announcement!", description=f"{''.join(contents.split('```'))}", color=color.green())
      await ctx.send(embed=embed)

    @commands.command(hidden=True, description="Make a global bot update", usage="ov update <changes>")
    async def update(self, ctx, *, changes = None):
      if not ctx.author.id == 615037304616255491:
        return
      if changes is None:
        await ctx.send("Update changes cannot be empty!")
        return
      if "```" not in changes or changes.count("`") < 6:
        await ctx.send("Update changes must be wrapped in triple backticks!")
        return
      await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"updates.{round(time.time())}": ''.join(changes.split('```')).strip()}})
      embed = discord.Embed(title="Successfully made update!", description=f"{''.join(changes.split('```'))}", color=color.green())
      await ctx.send(embed=embed)

    @commands.command(hidden=True, description="Create an event", usage="ov setevent <expiry> <event>")
    async def setevent(self, ctx, expiry = "999d", *, event: str = None):
      if not ctx.author.id == 615037304616255491:
        return
      if event is None:
        await ctx.send("Events cannot be nothing!")
        return
      try:
        expiry = ad(expiry)
      except:
        await ctx.send("Invalid expiry time!")
        return
      if "```" not in event or event.count("`") < 6:
        await ctx.send("Event must be wrapped in triple backticks!")
        return
      await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"events.{round(round(time.time())+expiry)}": ''.join(event.split('```')).strip()}})
      embed = discord.Embed(title="Successfully added event!", description=f"{''.join(event.split('```'))}", color=color.green())
      await ctx.send(embed=embed)

    @commands.command(hidden=True, description="Create a code", usage="ov setcode <code> <expiry time>\nov setcode <code> remove")
    async def setcode(self, ctx, code = None, expiry = "999d"):
      if not ctx.author.id == 615037304616255491:
        return
      if code is None:
        await ctx.send("Provide a code to set")
        return

      code = code.lower()
      if expiry == "remove":
        if code not in (await self.bot.gcll.find_one({"id": 863025676213944340}))["codes"]:
          await ctx.send(f"Unable to find this code `{code}`")
          return
        await self.bot.gcll.update_one({"id": 863025676213944340}, {"$unset": {f"codes.{code}": 1}})
        await ctx.send(f"Successfully removed code `{code}`")
        return

      try:
        expiry = ad(expiry)
      except:
        await ctx.send("Invalid expiry time!")
        return

      t = round(round(time.time())+expiry)
      await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"codes.{code}": t}})
      await ctx.send(f"Successfully added code `{code}`, expires in <t:{t}>")

    @commands.command(hidden=True, description="Execute code", usage="ov execute <code>")
    async def execute(self, ctx, *, code: str = None):
        if not ctx.author.id == 615037304616255491:
            return
        if code is None:
            await ctx.send("Cannot execute nothing!")
            return
        if "```" not in code or code.count("`") < 6:
            await ctx.send("Code must be wrapped in triple backticks!")
            return
        code = ''.join(code.split('```')).strip().replace("self.bot.http.token", "'Nice try'")
        exec(f"""
async def _ex(ctx):
    try:
        {code}
        await ctx.message.add_reaction("\U00002705")
    except Exception as e:
        await ctx.message.add_reaction("\U0000274c")
        await ctx.send("`[*] Error: " + str(e) + "`")

asyncio.ensure_future(_ex(ctx))
        """, locals(), globals())

    @execute.error
    async def executeerror(self, ctx, error):
      await ctx.message.add_reaction("\U0000274c")
      await ctx.send("`[*] Error: " + str(error.original) + "`")

    @commands.command(hidden=True, description="Removes a user from the database", usage="ov removeuser <user ID>", aliases=["ru"])
    async def removeuser(self, ctx, userid: int = None):
      if not ctx.author.id == 615037304616255491:
        return
      if userid is None:
        await ctx.send("Provide a user ID!")
        return

      user = await finduser(userid)
      if user is None:
        await ctx.send("Cannot find this user!")
        return

      view = interclass.Confirm(ctx, ctx.author)
      view.message = await ctx.send(f"Are you sure you want to remove this user from the database?\n{user['name']} **({user['id']})**", view=view)
      
      await view.wait()

      if view.value is None or view.value is False:
        await ctx.send("Removing user cancelled")
        return

      await self.bot.cll.delete_one({"id": user['id']})

      await ctx.send("Successfully removed the user from database")

    @commands.command(hidden=True, description="Let the bot says something", usage="ov say <texts>")
    async def say(self, ctx, *, text):
      await ctx.message.delete()
      await ctx.send(text)

def setup(bot):
    bot.add_cog(DevCog(bot))