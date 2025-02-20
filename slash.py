import os
import random
import discord
import interclass
import lists
from functions import blocked, updateinc, finduser, updateset, ab, dboost, aa, ac, getdrive, randomcar, userbanned, insertdict, getluck, getcha, gettitle
from PIL import Image, ImageDraw
from io import BytesIO
from discord.ext import commands
import asyncio
import functions
import time
from datetime import datetime
import math
from itertools import compress
from lists import locname, locprice
import re
from lists import tttlose, tttwin, ttttie
from bs4 import BeautifulSoup
import requests, json, lxml
import operator
import codes

color = discord.Colour
star = u"\u2B50"
lock = u"\U0001f512"
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/91.0.864.59"
}

async def mlist(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        return

      user = await finduser(ctx.author.id)

      if user['lvl'] < 5:
        await ctx.respond("You need to be at least level 5 to access the market!")
        return

      mll = await self.bot.dll.find_one({"id": "market"})

      items = mll['items']

      maxpage = -(-len(items) // 10)

      if len(items) == 0:
        maxpage = 1
        page = 1

      if page > maxpage:
        page = maxpage
      elif page <= 0:
        page = 1

      if len(items) == 0:
        maxpage = 1
        page = 1
        membed = discord.Embed(title = f"Market", description = "There are no items in the market\nType `/market listcar` or `/market listitem` to sell something!", color = color.random())
      else:
        membed = discord.Embed(title = f"Market", description = "", color = color.random())
        for item in items[(page-1)*10:(page-1)*10+10]:
          if item['type'] == 'car':
            if item['carinfo']['golden'] == True:
              itemname = f"{star} Golden " + item['carinfo']['name']
            else:
              itemname = item['carinfo']['name']
            membed.add_field(name=f"{itemname} | `{item['listingid']}`", value = f"**Listed by:** {await self.bot.fetch_user(int(item['author']))}\n<:cash:1329017495536930886> {aa(item['listingprice'])}\n**Speed** {item['carinfo']['speed']} MPH **Tuned** {item['carinfo']['tuned']}\n**OVR** {round(((item['carinfo']['speed']/1.015**item['carinfo']['tuned'])-lists.carspeed[item['carinfo']['name']]+10)/2, 2)}/10\n\U0000231B {ab(item['exp']-round(time.time()))}", inline=False)
          elif item['type'] == 'item':
            membed.add_field(name=f"{item['name']} (x{item['amount']}) | `{item['listingid']}`", value = f"**Listed by:** {await self.bot.fetch_user(int(item['author']))}\n <:cash:1329017495536930886> {aa(item['listingprice'])}\n\U0000231B {ab(item['exp']-round(time.time()))}", inline=False)
      membed.set_footer(text = f"Page {page} of {maxpage}")

      view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
      await ctx.respond(embed=membed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1

        mll = await self.bot.dll.find_one({"id": "market"})

        items = mll['items']

        maxpage = -(-len(items) // 10)

        if len(items) == 0:
          maxpage = 1
          page = 1

        if page > maxpage:
          page = maxpage
        elif page <= 0:
          page = 1

        if len(items) == 0:
          membed = discord.Embed(title = f"Market", description = "There are no items in the market\nType `/market listcar` or `/market listitem` to sell something!", color = color.random())
        else:
          membed = discord.Embed(title = f"Market", description = "", color = color.random())
          for item in items[(page-1)*10:(page-1)*10+10]:
            if item['type'] == 'car':
              if item['carinfo']['golden'] == True:
                itemname = f"{star} Golden " + item['carinfo']['name']
              else:
                itemname = item['carinfo']['name']
              membed.add_field(name=f"{itemname} | `{item['listingid']}`", value = f"**Listed by:** {await self.bot.fetch_user(int(item['author']))}\n<:cash:1329017495536930886> {aa(item['listingprice'])}\n**Speed** {item['carinfo']['speed']} MPH **Tuned** {item['carinfo']['tuned']}\n**OVR** {round(((item['carinfo']['speed']/1.015**item['carinfo']['tuned'])-lists.carspeed[item['carinfo']['name']]+10)/2, 2)}/10\n\U0000231B {ab(item['exp']-round(time.time()))}", inline=False)
            elif item['type'] == 'item':
              membed.add_field(name=f"{item['name']} (x{item['amount']}) | `{item['listingid']}`", value = f"**Listed by:** {await self.bot.fetch_user(int(item['author']))}\n <:cash:1329017495536930886> {aa(item['listingprice'])}\n\U0000231B {ab(item['exp']-round(time.time()))}", inline=False)
        membed.set_footer(text = f"Page {page} of {maxpage}")

        view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
        view.message = await msg.edit(embed=membed, view=view)

async def mbuy(self, ctx, itemid):
      if await blocked(ctx.author.id) == False:
        return
      if itemid == None:
        await ctx.respond("Provide a market item ID!")
        return
      user = await finduser(ctx.author.id)
      if 'racing' in list(user) and user['racing']:
        await ctx.respond("You are currently racing! You cannot buy anything")
        return

      mll = await self.bot.dll.find_one({"id": "market"})

      items = mll['items']

      try:
        item = [i for i in items if i['listingid'] == int(itemid)][0]
      except:
        await ctx.respond("Cannot find this market item, make sure it's still available!")
        return

      if item['author'] == ctx.author.id:
        await ctx.respond("You cannot buy items listed by yourself!")
        return

      usercash = user['cash']
      
      if usercash < item['listingprice']:
        await ctx.respond("You don't even have enough cash too afford that poor guy")
        return

      if item['type'] == 'car':
        if len(user['garage']) == 0:
          carindex = 1
        else:
          carindex = user['garage'][-1]["index"]+1
        carinfo = {"index": carindex, 'id': item['carinfo']['id'], 'name': item['carinfo']['name'], 'price': item['carinfo']['price'], 'speed': item['carinfo']['speed'], 'tuned': item['carinfo']['tuned'], 'golden': item['carinfo']['golden'], 'locked': False}
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"garage": carinfo}, "$inc": {"cash": -item['listingprice']}})
        await self.bot.cll.update_one({"id": item['author']}, {"$inc": {"cash": round(item['listingprice']*0.95)}})
        await self.bot.dll.update_one({"id": "market"}, {"$pull": {"items": {"listingid": int(itemid)}}})


        getuser = self.bot.get_user(item['author'])
        if getuser is not None:
          itemname = item['carinfo']['name']
          if item['carinfo']['golden'] == True:
            itemname = f"{star} Golden " + itemname
          embed = discord.Embed(title="Item sold", description=f"Your listing of a **{itemname}** has been sold for **<:cash:1329017495536930886> {aa(round(item['listingprice']*0.95))}** after a 5% tax!", color=color.green())
          try:
            await getuser.send(embed=embed)
          except:
            pass

        await ctx.respond(f"You have successfully bought a {itemname} for <:cash:1329017495536930886> {aa(item['listingprice'])}!")
      elif item['type'] == 'item':
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {f"storage.{item['name']}": item['amount'], "cash": -item['listingprice']}})
        await self.bot.cll.update_one({"id": item['author']}, {"$inc": {"cash": round(item['listingprice']*0.95)}})
        await self.bot.dll.update_one({"id": "market"}, {"$pull": {"items": {"listingid": int(itemid)}}})

        await ctx.respond(f"You have successfully bought {aa(item['amount'])} {item['name']} for <:cash:1329017495536930886> {aa(item['listingprice'])}!")

        getuser = self.bot.get_user(item['author'])
        if getuser is not None:
          embed = discord.Embed(title="Item sold", description=f"Your listing of **{item['amount']} {item['name']}** has been sold for **<:cash:1329017495536930886> {aa(round(item['listingprice']*0.95))}** after a 5% tax!", color=color.green())
          try:
            await getuser.send(embed=embed)
          except:
            pass

async def mlistcar(self, ctx, carid, price, exp):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if user['donor'] == 0 and exp > 24:
        await ctx.respond("The maximum duration you can list as a non-Royal Member is 24 hours")
        return
      elif user['donor'] <= 1 and exp > 72:
        await ctx.respond("The maximum duration you can list as a Royal Member is 72 hours")
        return
      elif user['donor'] == 2 and exp > 120:
        await ctx.respond("The maximum duration you can list as a Royal+ Member is 120 hours")
        return
      items = (await self.bot.dll.find_one({"id": "market"}))['items']
      if len([i for i in items if i['author'] == ctx.author.id]) >= 3 and user['donor'] == 0:
        await ctx.respond("The maximum number of listings you can list as a non-Royal Member is 3 listings")
        return
      elif len([i for i in items if i['author'] == ctx.author.id]) >= 5 and user['donor'] <= 1:
        await ctx.respond("The maximum number of listings you can list as a Royal Member is 5 listings")
        return
      elif len([i for i in items if i['author'] == ctx.author.id]) >= 10 and user['donor'] == 2:
        await ctx.respond("The maximum number of listings you can list as a Royal+ Member is 10 listings")
        return

      if carid == None:
        await ctx.respond("You have to give a car ID!")
        return
      usergarage = user['garage']
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
        carid = getdrive(user, "id")

      try:
        carid = int(carid)
      except:
        await ctx.respond("You need to give a valid car ID!")
        return

      usercar = [x for x in usergarage if x['index'] == int(carid)]
      if len(usercar) == 0:
        await ctx.respond(f"You don't have the car ID `{carid}`")
        return
      if usercar[0]['locked'] == True:
        await ctx.respond(f"You cannot list locked cars!")
        return

      usercar = [x for x in usergarage if x['index'] == int(carid)][0]

      view = interclass.Confirm(ctx, ctx.author)

      usercarname = usercar['name']
      if usercar['golden'] == True:
        usercarname = f"{star} Golden " + usercarname

      await updateset(ctx.author.id, 'blocked', True)

      await ctx.respond(f"Are you sure you want to list your **{usercarname}** for <:cash:1329017495536930886> **{aa(price)}** for {exp} hour{'s' if exp > 1 else ''}?",view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value is None:
          await ctx.respond("You didn't respond")
          return
      elif view.value == False:
          await ctx.respond("Listing cancelled")
          return

      carinfo = {'id': usercar['id'], 'name': usercar['name'], 'price': usercar['price'], 'speed': usercar['speed'], 'tuned': usercar['tuned'], 'golden': usercar['golden'], 'locked': False}

      if user['drive'] == usercar['id']:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"id": usercar['id']}}, "$set": {"drive": ""}})
      else:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"id": usercar['id']}}})

      if len(items) == 0:
        listingid = 1
      else:
        listingid = items[-1]["listingid"]+1

      await self.bot.dll.update_one({"id": "market"}, {"$push": {"items": {"listingid": listingid, "listingprice": price, "carinfo": carinfo, "type": "car", "author": ctx.author.id, "exp": round(time.time())+(exp*60*60)}}})

      await ctx.respond(f"You have successfully listed your **{usercarname}** on the market for <:cash:1329017495536930886> **{aa(price)}** for **{exp} hour{'s' if exp > 1 else ''}**")

      await updateset(ctx.author.id, 'blocked', False)

async def mlistitem(self, ctx, item, price, amount, exp):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if user['donor'] == 0 and exp > 24:
        await ctx.respond("The maximum duration you can list as a non-Royal Member is 24 hours")
        return
      elif user['donor'] <= 1 and exp > 72:
        await ctx.respond("The maximum duration you can list as a Royal Member is 72 hours")
        return
      elif user['donor'] == 2 and exp > 120:
        await ctx.respond("The maximum duration you can list as a Royal+ Member is 120 hours")
        return
      items = (await self.bot.dll.find_one({"id": "market"}))['items']
      if len([i for i in items if i['author'] == ctx.author.id]) >= 3 and user['donor'] == 0:
        await ctx.respond("The maximum number of listings you can list as a non-Royal Member is 3 listings")
        return
      elif len([i for i in items if i['author'] == ctx.author.id]) >= 5 and user['donor'] <= 1:
        await ctx.respond("The maximum number of listings you can list as a Royal Member is 5 listings")
        return
      elif len([i for i in items if i['author'] == ctx.author.id]) >= 10 and user['donor'] == 2:
        await ctx.respond("The maximum number of listings you can list as a Royal+ Member is 10 listings")
        return
      try:
        amount = int(amount)
      except:
        if not amount == "max" or not amount == "all":
          await ctx.respond("Provide a valid amount!")
          return
      userstorage = user['storage']
      item = item.lower()
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in list(user['storage']) if item == x.lower() or item == x.lower().replace(" ","")]
        if len(closematch) == 0:
          closematch = [x for x in list(user['storage']) if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond("You don't have this item in your storage")
        return

      if item in lists.drug:
        await ctx.respond("You cannot list drugs on the market!")
        return

      if amount == "max" or amount == "all":
        amount = userstorage[item]

      if amount <= 0:
        await ctx.respond("Give a valid amount!")
        return
      userstorageitemq = userstorage[item]
      if amount > userstorageitemq:
        await ctx.respond("You don't have that much item in your storage!")
        return

      view = interclass.Confirm(ctx, ctx.author)

      await updateset(ctx.author.id, 'blocked', True)

      await ctx.respond(f"Are you sure you want to list **{amount} {item}** for <:cash:1329017495536930886> **{aa(price)}** for {exp} hour{'s' if exp > 1 else ''}?",view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value is None:
          await ctx.respond("You didn't respond")
          return
      elif view.value == False:
          await ctx.respond("Listing cancelled")
          return

      if userstorageitemq == amount:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.{item}': 1}})
      else:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {f'storage.{item}': -amount}})

      if len(items) == 0:
        listingid = 1
      else:
        listingid = items[-1]["listingid"]+1

      await self.bot.dll.update_one({"id": "market"}, {"$push": {"items": {"listingid": listingid, "listingprice": price, "amount": amount, "name": item, "type": "item", "author": ctx.author.id, "exp": round(time.time())+(exp*60*60)}}})

      await ctx.respond(f"You have successfully listed **{amount} {item}** on the market for <:cash:1329017495536930886> **{aa(price)}** for **{exp} hour{'s' if exp > 1 else ''}**")

      await updateset(ctx.author.id, 'blocked', False)

async def wishlist(self, ctx):
  if await blocked(ctx.author.id) == False:
    ctx.command.reset_cooldown(ctx)
    return
  user = await finduser(ctx.author.id)
  if user['lvl'] < 10:
    await ctx.respond("You have to be at least level 10!")
    return

  level = 1
  maxlevel = 5
  locked = False
  if (level == 2 or level == 3) and user['donor'] == 0:
    locked = True
  elif (level == 4 or level == 5) and user['donor'] <= 1:
    locked = True
  else:
    locked = False

  embed = discord.Embed(title=f"{gettitle(user)}{ctx.author.name}'s Wishlist", color=color.blurple())
  for i in range(1, maxlevel+1):
    if (i == 2 or i == 3) and user['donor'] == 0:
      embed.add_field(name=f"Slot {i}", value="\U0001f512 Royal Member exclusive", inline=False)
    elif (i == 4 or i == 5) and user['donor'] <= 1:
      embed.add_field(name=f"Slot {i}", value="\U0001f512 Royal+ Member exclusive", inline=False)
    else:
      embed.add_field(name=f"Slot {i}", value=(user["wishlist"][str(i)] if user["wishlist"][str(i)] != "" else f"**Cooldown** {ab(user['timer'][f'wishlist{i}']-round(time.time()))}" if f"wishlist{i}" in user['timer'] else "No car"), inline=False)
    if i == level:
      embed.fields[i-1].value = "_\>  " + embed.fields[i-1].value + "  \<_"

  view = interclass.Wishlist(ctx.author, level == 1, level == maxlevel, f"wishlist{level}" in user['timer'] or locked)
  await ctx.respond(embed=embed,view=view)
  msg = await ctx.interaction.original_response()
  view.message = msg

  while True:
    await view.wait()

    if view.value is None:
      return
    elif view.value == "up":
      level -= 1
    elif view.value == "down":
      level += 1
    elif view.value == "edit":

      modal = interclass.Wishlistcar(level)
      await view.interaction.response.send_modal(modal)
      await modal.wait()

      if modal.value == "":

        user['wishlist'][str(level)] = ""
        await updateset(ctx.author.id, f"wishlist.{level}", "")

      else:
        if not modal.value in lists.allcars:
          try:
            if len(modal.value) < 2:
              await modal.interaction.channel.send("Enter at least 2 letters to search")
              modal.value = None
            else:
              closematch = [x for x in lists.allcars if modal.value.lower() == x.lower() or modal.value.lower() == x.lower().replace(" ","")]
              if len(closematch) == 0:
                closematch = [x for x in lists.allcars if modal.value.lower() in x.lower() or modal.value.lower() in x.lower().replace(" ","")]
              if len(closematch) > 1:
                await modal.interaction.channel.send(f"I found more than one car that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
                modal.value = None
              else:
                modal.value = closematch[0]
          except:
            await modal.interaction.channel.send("Cannot find this vehicle, make sure you typed the full name of the vehicle!")
            modal.value = None

        if modal.value is not None:
          user['wishlist'][str(level)] = modal.value
          await updateset(ctx.author.id, f"wishlist.{level}", modal.value)

    if (level == 2 or level == 3) and user['donor'] == 0:
      locked = True
    elif (level == 4 or level == 5) and user['donor'] <= 1:
      locked = True
    else:
      locked = False

    embed = discord.Embed(title=f"{gettitle(user)}{ctx.author.name}'s Wishlist", color=color.blurple())
    for i in range(1, maxlevel+1):
      if (i == 2 or i == 3) and user['donor'] == 0:
        embed.add_field(name=f"Slot {i}", value="\U0001f512 Royal Member exclusive", inline=False)
      elif (i == 4 or i == 5) and user['donor'] <= 1:
        embed.add_field(name=f"Slot {i}", value="\U0001f512 Royal+ Member exclusive", inline=False)
      else:
        embed.add_field(name=f"Slot {i}", value=(user["wishlist"][str(i)] if user["wishlist"][str(i)] != "" else f"**Cooldown** {ab(user['timer'][f'wishlist{i}']-round(time.time()))}" if f"wishlist{i}" in user['timer'] else "No car"), inline=False)

      if i == level:
        embed.fields[i-1].value = "_\>  " + embed.fields[i-1].value + "  \<_"

    view = interclass.Wishlist(ctx.author, level == 1, level == maxlevel, f"wishlist{level}" in user['timer'] or locked)
    view.message = await msg.edit(embed=embed, view=view)

async def burglary(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      if user['lvl'] < 10:
        await ctx.respond("You have to be at least level 10!")
        return
      firstplace = random.choice(lists.randomhouses)
      secondplace = random.choice(lists.randomhouses)
      thirdplace = random.choice(lists.randomhouses)

      while firstplace == secondplace or firstplace == thirdplace or secondplace == firstplace or secondplace == thirdplace or thirdplace == firstplace or thirdplace == secondplace:
        firstplace = random.choice(lists.randomhouses)
        secondplace = random.choice(lists.randomhouses)
        thirdplace = random.choice(lists.randomhouses)

      e = discord.Embed(title="Pick a house to rob!",description=f"\U00000031\U0000FE0F\U000020E3 **{firstplace}**\n\U00000032\U0000FE0F\U000020E3 **{secondplace}**\n\U00000033\U0000FE0F\U000020E3 **{thirdplace}**",color=color.blurple())

      view = interclass.Three(ctx)

      await ctx.respond(embed=e,view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value is None:
        await ctx.respond("You are too slow, the owner came back home")
        return
      elif view.value == "1":
        selectedplace = firstplace
      elif view.value == "2":
        selectedplace = secondplace
      elif view.value == "3":
        selectedplace = thirdplace

      if random.random() > (lists.housechance[selectedplace]+(0.1*(getluck(user)))):
        e = discord.Embed(title="Whoops!", description=f"You tried to break into a {selectedplace} but failed!\n{random.choice(lists.housefail[selectedplace])}", color=color.red()).set_footer(text="hahaha too bad").set_image(url="https://img.freepik.com/premium-vector/failed-burglary-attempt-flat-illustration_94753-1663.jpg")
        view.message = await msg.edit(embed=e, view=None)
        heat = 40
        deviation = 10
        await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user))) ) )
        return

      e = discord.Embed(title=f"Robbing a {selectedplace}", description=f"You've successfully broken into the **{selectedplace}**!\nEscape when you are done robbing!", color=color.blurple()).set_image(url="https://img.freepik.com/free-vector/thief-concept-illustration_114360-7200.jpg")
      view = interclass.Rob(ctx)
      view.message = await msg.edit(embed=e, view=view)

      i = 0
      cash = 0
      items = []
      while True:
        await view.wait()
        i += 1

        if view.value is None:
          rtime = round(random.randint(180, 360)*((user['lvl']+100)/100))
          embed = discord.Embed(title="You have been caught!", description=f"You are too slow, the property owner saw you and called the cops!\nYou are now in jail for {ab(rtime)}", color=color.red())
          
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$set": {"injail": True, "timer.jail": round(time.time())+rtime, "heat": 0}})

          if "Bribe" in user['storage'] and user['storage']['Bribe'] > 0:
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
            if user['storage']['Bribe'] == 1:
              await self.bot.cll.update_one({"id": ctx.author.id}, {"$set": {"injail": False}, "$unset": {"timer.jail": 1, "storage.Bribe": 1}})
            else:
              await self.bot.cll.update_one({"id": ctx.author.id}, {"$set": {"injail": False}, "$unset": {"timer.jail": 1}, "$inc": {"storage.Bribe": -1}})
            return

          return
        elif view.value is True:
          rarity = random.random()
          if rarity <= (0.05 + 0.05*getluck(user)):
            # 0.1825
            item = random.choice(lists.houseitem[selectedplace]["mythic"])
          elif rarity <= (0.1 + 0.1*getluck(user)):
            # 0.465
            item = random.choice(lists.houseitem[selectedplace]["epic"])
          elif rarity <= (0.4 + 0.2*getluck(user)):
            # 0.8475
            item = random.choice(lists.houseitem[selectedplace]["rare"])
          else:
            item = random.choice(lists.houseitem[selectedplace]["common"])

          # Max Luck (825): 18.25% 28.25% 38.25% 15.25%

          if random.random() <= (lists.robchance[selectedplace]+(0.1*(getluck(user)))) and i <= 5:
            items.append(item)
            e = discord.Embed(title=f"Robbing a {selectedplace}", description=f"You stole a **{item}**!\nEscape when you are done robbing!\n\nStolen items: **{', '.join(items)}**", color=color.green()).set_image(url="https://img.freepik.com/free-vector/thief-concept-illustration_114360-7200.jpg")
            view = interclass.Rob(ctx)
            view.message = await msg.edit(embed=e, view=view)
          else:
            e = discord.Embed(title=f"Robbing a {selectedplace}", description=f"You attempted to steal a **{item}** but the owner caught you!\nYou managed to escape but failed to bring anything with you..\n\n{'Stolen items: **Nothing**' if len(items) == 0 else 'Stolen items: **' + ', '.join(items) + '**'}", color=color.red()).set_image(url="https://img.freepik.com/free-vector/thief-concept-illustration_114360-7200.jpg")
            await msg.edit(embed=e, view=None)
            return

        elif view.value is False:
          if len(items) == 0:
            e = discord.Embed(title=f"Robbing a {selectedplace}", description=f"You escaped the house with nothing, good job!", color=color.green()).set_image(url="https://img.freepik.com/free-vector/thief-concept-illustration_114360-7200.jpg")
            await msg.edit(embed=e, view=None)
            return
          else:
            e = discord.Embed(title=f"Robbing a {selectedplace}", description=f"You successfully escaped the {selectedplace} with these items: **{', '.join(items)}**", color=color.green()).set_image(url="https://img.freepik.com/free-vector/thief-concept-illustration_114360-7200.jpg")
            await msg.edit(embed=e, view=None)

            payload = {}
            for item in items:
              if item not in list(payload):
                payload[f"storage.{item}"] = 1
              else:
                payload[f"storage.{item}"] += 1

            await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": payload})
            return

async def suggest(self, ctx, name, price, speed, image, rank, remarks):
    if not await blocked(ctx.author.id):
        ctx.command.reset_cooldown(ctx)
        return
    user = await finduser(ctx.author.id)
    if user == None:
        return
    if await userbanned(ctx.author.id) == True:
        return

    suggestedcars = (await self.bot.ccll.find_one({"id": "suggestions"}))["cars"]
    if name in lists.allcars or len([car for car in suggestedcars if car['name'] == name]) != 0:
        await ctx.respond("This car may already exist in the bot or has already been suggested by another user!")
        return
    if len(image) > 500:
        await ctx.respond("This link is too long! Keep it under 500 characters")
        return

    if price < 500:
        price = 500
    price = round(price*2/1000)
    specialty = await functions.carspecialty(self, str(ctx.author.id))

    if rank is None:
        if price <= 100:
            rank = "Low"
        elif 100 < price <= 500:
            rank = "Average"
        elif 500 < price <= 2000:
            rank = "High"
        elif 2000 < price:
            rank = "Exotic"

    e = discord.Embed(title=name,description=f"**Specialty** {specialty}\n**Rank** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH",color=color.random() if rank != "Exotic" else color.default())
    e.set_image(url=image)
    e.set_footer(text="Car prices can be a lot higher if it's fast!")

    view = interclass.Submit(ctx, ctx.author)
    try:
        await ctx.respond(content=f"{gettitle(user)}{ctx.author.mention}\nThis is a preview of your car suggestion\nMake sure everything is correct and the image is showing before submitting!", embed=e, view=view)
    except:
        await ctx.respond("The given image link is invalid")
        return

    await view.wait()
    if view.value is None:
        ctx.command.reset_cooldown(ctx)
        await ctx.send_followup(content="You didn't respond")
        return
    elif view.value is False:
        ctx.command.reset_cooldown(ctx)
        await ctx.send_followup(content="You cancelled the submission")
        return
    elif view.value is True:
        await ctx.send_followup(content="You have successfully submitted the car suggestion!\nYou will be notified once it is approved, make sure to keep your DMs open!")

        carinfo = {'specialty': str(ctx.author.id), 'name': name.replace(".", "\uff0e"), 'price': price, 'speed': speed, 'rank': rank, 'image': image, 'remarks': remarks}
        await self.bot.ccll.update_one({"id": "suggestions"}, {"$push": {"cars": carinfo}})

        e = discord.Embed(title=name,description=f"**Specialty** {specialty}\n**Rank** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {price}\n**Average Speed:** {speed} MPH",color=color.random() if rank != "Exotic" else color.default())
        e.set_image(url=image)
        e.set_footer(text="Car prices can be a lot higher if it's fast!")

        await self.bot.get_channel(869218950255345704).send(content=f"Received car suggestion from {ctx.author} ({ctx.author.id})", embed=e)

async def fraud(self, ctx):
    if not await blocked(ctx.author.id):
        ctx.command.reset_cooldown(ctx)
        return
    user = await finduser(ctx.author.id)
    if user['lvl'] < 5:
        await ctx.respond("You have to be lvl 5 before committing fraud!")
        return
    embed = discord.Embed(title="Plan your fraud", description=f"**Success chance** {user['fraud']}%", color=color.random())
    
    colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
    firstcolor = random.choice(colors)
    colors.remove(firstcolor)

    img = Image.new("RGBA", (212, 21))

    pen = ImageDraw.Draw(img)
    pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
    pen.rounded_rectangle(((0, 0), (round(user['fraud']*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

    byte = BytesIO()

    img.save(byte, format="png")
    byte.seek(0)

    file = discord.File(fp=byte,filename="pic.png")

    embed.set_image(url="attachment://pic.png")
    embed.set_footer(text="Plan more to get higher success chance!")

    view = interclass.Fraud(ctx, user['fraud'])
    await ctx.respond(embed=embed, view=view, file=file)
    msg = await ctx.interaction.original_response()
    view.message = msg

    await view.wait()

    if view.value is None:
        ctx.command.reset_cooldown(ctx)
        await ctx.respond("You didn't respond")
        return
    elif view.value is True:
        plan = random.randint(10, 20)
        plan = round(plan + (plan * getluck(user)))
        if plan + user['fraud'] > 100:
            plan = round(100 - user['fraud'])
        await updateinc(ctx.author.id, "fraud", plan)
        embed = discord.Embed(title="Plan your fraud", description=f"You planned more and increased the success chance by **{plan}%**!\n\n**Success chance** {user['fraud'] + plan}%", color=color.random())
        colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
        firstcolor = random.choice(colors)
        colors.remove(firstcolor)

        img = Image.new("RGBA", (212, 21))

        pen = ImageDraw.Draw(img)
        pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
        pen.rounded_rectangle(((0, 0), (round((user['fraud']+plan)*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

        byte = BytesIO()

        img.save(byte, format="png")
        byte.seek(0)

        file = discord.File(fp=byte,filename="pic.png")

        embed.set_image(url="attachment://pic.png")
        embed.set_footer(text="Plan more to get higher success chance!")
        await msg.edit(embed=embed, attachments=[], file=file)
        return
    elif view.value is False:
        ran = random.randint(1, 100)
        await updateset(ctx.author.id, "fraud", 0)
        if ran <= user['fraud']:
            cash = random.randint(300, 600)
            cash = round(cash + (cash * user['stats']['cha']/1000))
            await updateinc(ctx.author.id, "cash", cash)
            embed = discord.Embed(title="Plan your fraud", description=f"You committed fraud and earned <:cash:1329017495536930886> {cash}!\n\n**Success chance** {user['fraud']}%", color=color.green())
            colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
            firstcolor = random.choice(colors)
            colors.remove(firstcolor)

            img = Image.new("RGBA", (212, 21))

            pen = ImageDraw.Draw(img)
            pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
            pen.rounded_rectangle(((0, 0), (round((user['fraud'])*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

            byte = BytesIO()

            img.save(byte, format="png")
            byte.seek(0)

            file = discord.File(fp=byte,filename="pic.png")

            embed.set_image(url="attachment://pic.png")
            embed.set_footer(text="Plan more to get higher success chance!")
            await msg.edit(embed=embed, attachments=[], file=file)
            return
        else:
            heat = 40
            deviation = 10
            await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -(getluck(user)))) ) )
            embed = discord.Embed(title="Plan your fraud", description=f"You committed fraud but failed!\n\n**Success chance** {user['fraud']}%", color=color.red())
            colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
            firstcolor = random.choice(colors)
            colors.remove(firstcolor)

            img = Image.new("RGBA", (212, 21))

            pen = ImageDraw.Draw(img)
            pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
            pen.rounded_rectangle(((0, 0), (round((user['fraud'])*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

            byte = BytesIO()

            img.save(byte, format="png")
            byte.seek(0)

            file = discord.File(fp=byte,filename="pic.png")

            embed.set_image(url="attachment://pic.png")
            embed.set_footer(text="Plan more to get higher success chance!")
            await msg.edit(embed=embed, attachments=[], file=file)
            return

async def search(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      # Search success chance
      chance = 0.65 + (0.65*getluck(user))
      searcharea = random.choice(lists.search)
      # Highway die chance = 25%
      randomchance2 = 0.25 - (0.25*getluck(user))
      if user['s'] == 7 or user['lvl'] < 5:
        randomchance2 = 0
      if user['s'] == 7:
        chance = 1
      # Rare item chance
      randomchance3 = 0.04 + (0.04*getluck(user))
      if searcharea == 'Highway' and random.random() <= randomchance2:
        await self.die(ctx, ctx.author, "while searching for cash in Highway", "You ran into a car and got flattened!")
        return

      if random.random() <= chance:
        randomcash = (round(random.uniform(10, 30)))
        cashfound = round(randomcash + (randomcash*user['stats']['cha']/1000) + (randomcash*dboost(user['donor'])))
        await updateinc(ctx.author.id, 'cash', round(cashfound))
        embed = discord.Embed(title = "Searched for cash", description = f"You found <:cash:1329017495536930886> {round(cashfound)} from the {searcharea}!", color = color.green())
        embed.set_footer(text = "there's a chance you'll find a rare item")
        random1 = random.random()
        if random1 < randomchance3:
          random2 = random.randint(1,8)
          if 0 < random2 <= 6:
            if random.randint(0, 1) == 1:
              await updateinc(ctx.author.id, 'storage.Average Car Key', 1)
              embed.add_field(name="Item found!",value="You found an Average Car Key!")
              embed.set_footer(text = "so lucky! free car!")
            else:
              await updateinc(ctx.author.id, 'storage.Garage Key', 1)
              embed.add_field(name="Item found!",value="You found a Garage Key!")
              embed.set_footer(text = "lucky!")
          elif 6 < random2 <= 8:
            await updateinc(ctx.author.id, 'storage.Safe', 1)
            embed.add_field(name="Item found!",value="You found a Safe!")
            embed.set_footer(text = "so lucky! free safe!")
          elif 8 < random2 <= 10:
            item = random.choice(['Medical Kit', 'Bribe'])
            await updateinc(ctx.author.id, f'storage.{item}', 1)
            embed.add_field(name="Item found!",value=f"You found a {item}!")
            embed.set_footer(text = "so lucky! free item!")

        await ctx.respond(embed=embed)
        if user['s'] == 7:
            await updateset(ctx.author.id, "s", 8)
      else:
        embed = discord.Embed(title = "Searched for cash", description = f"You found **nothing** while searching at the {searcharea}!", color = color.red())
        embed.set_footer(text = "increase your luck to increase the chance of succeeding!")
        await ctx.respond(embed=embed)

async def vehicletheft(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      usercarcount = len(user['garage'])
      if usercarcount >= user['garagec']:
        await ctx.respond("Your garage is full! Upgrade it or sell some cars")
        ctx.command.reset_cooldown(ctx)
        return
      if user['s'] == 9:
        firstcar = "Toyota Avalon"
        secondcar = "Volvo S60"
        thirdcar = "Buick Regal"
      elif user['s'] == 16:
        firstcar = "Ford Focus"
        secondcar = "Nissan Murano"
        thirdcar = "Honda Jazz"
      else:
        exclusive = await self.bot.ccll.find_one({"id": "exclusive"})
        firstcar = randomcar(user, exclusive["amount"])
        secondcar = randomcar(user, exclusive["amount"])
        thirdcar = randomcar(user, exclusive["amount"])
        while len(set([firstcar, secondcar, thirdcar])) != 3 or ((user['s'] == 9 or user['s'] == 16) and "1973 Ford Pinto" in [firstcar, secondcar, thirdcar]):
          firstcar = randomcar(user, exclusive["amount"])
          secondcar = randomcar(user, exclusive["amount"])
          thirdcar = randomcar(user, exclusive["amount"])

      view = interclass.Three(ctx)

      wishlisted = False
      if firstcar in list(user['wishlist'].values()) or secondcar in list(user['wishlist'].values()) or thirdcar in list(user['wishlist'].values()):
        wishlisted = True

      e = discord.Embed(title="Which car do you want to steal?",description=f"\U00000031\U0000FE0F\U000020E3 **{firstcar+' (Wishlisted)' if firstcar in list(user['wishlist'].values()) else firstcar}**\n\U00000032\U0000FE0F\U000020E3 **{secondcar+' (Wishlisted)' if secondcar in list(user['wishlist'].values()) else secondcar}**\n\U00000033\U0000FE0F\U000020E3 **{thirdcar+' (Wishlisted)' if thirdcar in list(user['wishlist'].values()) else thirdcar}**",color=color.blurple())

      await ctx.respond(embed=e,view=view)
      view.message = msg = await ctx.interaction.original_response()

      await view.wait()

      if view.value is None:
        await ctx.respond("You are too slow, the car owner drove the car away")
        return
      elif view.value == "1":
        selectedcar = firstcar
      elif view.value == "2":
        selectedcar = secondcar
      elif view.value == "3":
        selectedcar = thirdcar

      if selectedcar in lists.exclusivecar:
        stealing_chance = 0
      else:
        stealing_chance = lists.carchance[selectedcar]+(lists.carchance[selectedcar]*(getluck(user)*2))

      ### Lock picking ###
      success = 0
      chance = 0
      picked = [0, 0, 0, 0]
      pins = random.choices([1, 2, 3, 4], k=4)

      img = Image.open(r"images/car_lock.png")

      i = 0
      for pin in pins:
        p = Image.open(rf"images/pin_{pin}.png")
        img.paste(p, (80+(40 * i), img.size[1]-p.size[1]-48))
        i += 1

      byte = BytesIO()

      img.save(byte, format="png")

      byte.seek(0)

      file = discord.File(byte, "pic.png")

      embed = discord.Embed(title=f"{selectedcar}", description=f"Push the pins up starting from the left!\nSuccess chance +{round(chance*100)}%", color=color.blurple()).set_image(url="attachment://pic.png")
      view = interclass.Lockpicking(ctx)
      view.message = await msg.edit(embed=embed, view=view, file=file)

      i = 0
      while True:
        await view.wait()

        if view.value is None:
          await ctx.respond("You are too slow, the car owner drove the car away")
          return
        elif view.value == "instruction":
          page = 1

          desc = ["❧ Your goal is to align the bottom line of the yellow square to the red line, refer to the image below", "❧ The first thing is to examine the distance you need to push the pins up, refer to the red lines below\n❧ The first pin has the longest distance, therefore you need to click 4\n❧ The rightmost pin has the shortest distance, therefore you need to click 1", "❧ You have to push the pins in the right order from left to right\n❧ To pick the lock below you have to click 4 2 3 1 in the right order"]

          img = Image.open(rf"images/theft_instruction_{page}.png")

          byte = BytesIO()

          img.save(byte, format="png")

          byte.seek(0)

          file = discord.File(byte, "pic.png")

          embed = discord.Embed(title="How to pick a lock", description=desc[page-1], color=color.default()).set_image(url="attachment://pic.png")

          view2 = interclass.Page(ctx, ctx.author, page == 1, page == 3)
          view2.message = msg2 = await ctx.respond(embed=embed, file=file, ephemeral=True, view=view2)
          view = interclass.Lockpicking(ctx)
          view.message = await msg.edit(view=view)

          while True:
            await asyncio.sleep(0.5)

            if view.value in [1, 2, 3, 4]:
              for child in view2.children:
                child.disabled = True
              await msg2.edit(view=view2)
              break
            elif view2.value == "left":
              page -= 1

              img = Image.open(rf"images/theft_instruction_{page}.png")

              byte = BytesIO()

              img.save(byte, format="png")

              byte.seek(0)

              file = discord.File(byte, "pic.png")

              embed = discord.Embed(title="How to pick a lock", description=desc[page-1], color=color.default()).set_image(url="attachment://pic.png")

              view2 = interclass.Page(ctx, ctx.author, page == 1, page == 3)
              view2.message = await msg2.edit(embed=embed, file=file, view=view2)
            elif view2.value == "right":
              page += 1

              img = Image.open(rf"images/theft_instruction_{page}.png")

              byte = BytesIO()

              img.save(byte, format="png")

              byte.seek(0)

              file = discord.File(byte, "pic.png")

              embed = discord.Embed(title="How to pick a lock", description=desc[page-1], color=color.default()).set_image(url="attachment://pic.png")

              view2 = interclass.Page(ctx, ctx.author, page == 1, page == 3)
              view2.message = await msg2.edit(embed=embed, file=file, view=view2)

        else:
          img = Image.open(r"images/car_lock.png")

          picked[i] = view.value

          l = 0
          for pin in pins:
            p = Image.open(rf"images/pin_{pin}.png")
            img.paste(p, (80+(40 * l), img.size[1]-p.size[1]-48-(round(6*picked[l])+(1 if picked[l] != 0 else 0))))
            l += 1

          byte = BytesIO()

          img.save(byte, format="png")

          byte.seek(0)

          file = discord.File(byte, "pic.png")

          if picked[i] == pins[i]:
            success += 1
            if selectedcar not in lists.exclusivecar:
                chance += 0.05

          embed = discord.Embed(title=f"{selectedcar}", description=f"Push the pins up starting from the left!\nSuccess chance +{round(chance*100)}%", color=color.blurple()).set_image(url="attachment://pic.png")
          view = interclass.Lockpicking(ctx)

          if picked[i] != pins[i] or 0 not in picked:
            for child in view.children:
              child.disabled = True
            view.message = await msg.edit(embed=embed, view=view, file=file)
            break
          else:
            view.message = await msg.edit(embed=embed, view=view, file=file)

          i += 1

      ### ---------- ###

      stealing_chance += chance
      if selectedcar in lists.exclusivecar and success == 4:
        amount = await self.bot.ccll.find_one({"id": "exclusive"})
        if amount["amount"][selectedcar] <= 0:
            await ctx.respond("You are too slow, someone else stole the car!")
            return
        await self.bot.ccll.update_one({"id": "exclusive"}, {"$inc": {f"amount.{selectedcar}": -1}})
        if amount["amount"][selectedcar] == 1:
          await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"announcement.{round(time.time())}": f"A {selectedcar} has been stolen! There are 0 left in OV City, better luck next time!"}})
        else:
          await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {f"announcement.{round(time.time())}": f"A {selectedcar} has been stolen! There are {amount['amount'][selectedcar]-1} left in OV City!"}})
        stealing_chance = 1
      randomchance = round(random.random(), 6)
      randomgold = random.randint(1,2048)

      heat = 40
      deviation = 10
      await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user))) ) )
      await updateset(ctx.author.id, 'blocked', True)

      user = await finduser(ctx.author.id)

      file = None

      if randomchance < stealing_chance:
        if user['s'] == 9:
          randomchance = 0
          randomgold = 0
          await updateset(ctx.author.id, 's', 10)
        elif user['s'] == 16:
          randomchance = 0
          randomgold = 0
          await updateset(ctx.author.id, 's', 17)
        if selectedcar == "1973 Ford Pinto":
            await self.die(ctx, ctx.author, "while stealing the 1973 Ford Pinto!", "You accidentally kicked the rear of the car and it exploded")
            return
        if selectedcar in lists.lowcar:
          rank = "Low"
        elif selectedcar in lists.averagecar:
          rank = "Average"
        elif selectedcar in lists.highcar:
          rank = "High"
        elif selectedcar in lists.exoticcar:
          rank = "Exotic"
        elif selectedcar in lists.classiccar:
          rank = "Classic"
        elif selectedcar in lists.exclusivecar:
          rank = "Exclusive"
        else:
          rank = "Unknown"
        if len(user['garage']) == 0:
          carindex = 1
        else:
          carindex = user['garage'][-1]["index"]+1
        carspeed = round( random.triangular( (lists.carspeed[selectedcar]-10)*100, (lists.carspeed[selectedcar]+10)*100, round(lists.carspeed[selectedcar])*100 ) / 100, 2)
        tune = random.randint(0, 2)
        for _ in range(tune):
          carspeed = round((0.015*carspeed) + carspeed, 2)
        if randomgold == 1696:
          carinfo = {'index': carindex, 'id': functions.randomid(), 'name': selectedcar, 'price': lists.carprice[selectedcar], 'speed': carspeed, 'tuned': tune, 'golden': True, 'locked': False}
          if success == 4:
            vtembed = discord.Embed(title="Vrooom!",description=f"You drove off in the **{star} Golden {selectedcar}**!\n\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {lists.carprice[selectedcar]}\n**Speed** {carspeed} MPH\n**Tuned** {tune}\n**Overall Rating** {round(((carspeed/1.015**tune)-lists.carspeed[selectedcar]+10)/2, 2)}/10",color=color.green())
          else:
            vtembed = discord.Embed(title="Vrooom!",description=f"You **set off the alarm** but still managed to drive off in the **{star} Golden {selectedcar}**!\n\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {lists.carprice[selectedcar]}\n**Speed** {carspeed} MPH\n**Tuned** {tune}\n**Overall Rating** {round(((carspeed/1.015**tune)-lists.carspeed[selectedcar]+10)/2, 2)}/10",color=color.green())
          try:
            vtembed.set_image(url=lists.goldencarimage[selectedcar])
          except:
            byte = functions.goldfilter(lists.carimage[selectedcar])
            file = discord.File(fp=byte,filename="pic.jpg")
            vtembed.set_image(url="attachment://pic.jpg")
        else:
          carinfo = {'index': carindex, 'id': functions.randomid(), 'name': selectedcar, 'price': lists.carprice[selectedcar], 'speed': carspeed, 'tuned': tune, 'golden': False, 'locked': False}
          if success == 4:
            vtembed = discord.Embed(title="Vrooom!",description=f"You drove off in the **{selectedcar}**!\n\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {lists.carprice[selectedcar]}\n**Speed** {carspeed} MPH\n**Tuned** {tune}\n**Overall Rating** {round(((carspeed/1.015**tune)-lists.carspeed[selectedcar]+10)/2, 2)}/10",color=color.green())
          else:
            vtembed = discord.Embed(title="Vrooom!",description=f"You **set off the alarm** but still managed to drive off in the **{selectedcar}**!\n\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {lists.carprice[selectedcar]}\n**Speed** {carspeed} MPH\n**Tuned** {tune}\n**Overall Rating** {round(((carspeed/1.015**tune)-lists.carspeed[selectedcar]+10)/2, 2)}/10",color=color.green())
          vtembed.set_image(url=lists.carimage[selectedcar])


        # Wishlist
        wishlist = user['wishlist']
        if selectedcar in list(wishlist.values()) or wishlisted is True:
          level = list(wishlist.keys())[list(wishlist.values()).index(selectedcar)]
          # Add car
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"garage": carinfo}, "$set": {f"wishlist.{level}": "", f"timer.wishlist{level}": round(time.time()+86400)}})
        else:
          # Add car
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"garage": carinfo}})

        vtembed.set_footer(text="lucky lucky!")

        if file is None:
            await ctx.respond(embed=vtembed)
        else:
            await ctx.respond(embed=vtembed, file=file)
        await updateset(ctx.author.id, 'blocked', False)
        return
      else:
        if success == 4:
          failembed = discord.Embed(title="Whoops!",description=f"You successfully lock picked the car but still failed trying to break into the **{selectedcar}**!",color=color.red())
        else:
          failembed = discord.Embed(title="Whoops!",description=f"You **set off the alarm while** trying to break into the **{selectedcar}**!",color=color.red())
        failembed.set_image(url="https://img.freepik.com/premium-vector/theft-car-thieves-black-mask-take-apart-car-policeman-uniform-criminal-steals-auto-crime-damage-destruction-another-property-security-system-concept-cartoon-flat-vector-illustration_176411-2111.jpg")
        failembed.set_footer(text="try again next time!")
        await ctx.respond(embed=failembed)
        await updateset(ctx.author.id, 'blocked', False)
        return

async def larceny(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      guild = await self.bot.gcll.find_one({"id": ctx.guild.id})
      if guild['larceny'] == False:
        await ctx.respond("Imagine thinking you can commit larceny in this server")
        ctx.command.reset_cooldown(ctx)
        return
      if user == None:
        await ctx.respond("Who is your larceny target?")
        ctx.command.reset_cooldown(ctx)
        return
      if user == ctx.author:
        await ctx.respond("Lol imagine thinking that you can commit larceny on yourself")
        ctx.command.reset_cooldown(ctx)
        return
      if await finduser(user.id) == None:
        await ctx.respond("This user haven't started playing OV Bot yet!")
        ctx.command.reset_cooldown(ctx)
        return
      user2 = await finduser(user.id)
      if ctx.guild.id in user2['q']:
        await ctx.respond("The user quarantined themself, how lonely")
        return
      try:
        user2['timer']['larceny']
        await ctx.respond("The user just got stolen from his/her stash recently! They have a 4 hours shield after getting stolen by someone")
        ctx.command.reset_cooldown(ctx)
        return
      except:
        pass
      userstash = user2['stash']
      if userstash < 100:
        await ctx.respond("The user is too poor, you wont get anything from committing larceny on his/her stash")
        ctx.command.reset_cooldown(ctx)
        return
      userp = await finduser(ctx.author.id)
      user2 = await finduser(user.id)
      if userp['cash'] < 50:
        await ctx.respond("You need <:cash:1329017495536930886> 50 in order to commit larceny!")
        ctx.command.reset_cooldown(ctx)
        return
      await updateinc(ctx.author.id, 'cash', -50)
      await updateset(user.id, 'blocked', True)

      usersjoined = []

      view = interclass.Join(usersjoined, user)

      larembed = discord.Embed(title="Larceny!",description=f"{gettitle(userp)}{ctx.author} is committing larceny on {gettitle(user2)}{user}'s stash!\nClick the button below to join!",color = color.blue())
      larembed.set_footer(text="You only have 1 minute!")

      await ctx.respond(embed=larembed,view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      usersjoined = view.joined

      if len(usersjoined) == 0:
        await ctx.respond(f"No one joined the larceny, {gettitle(userp)}{ctx.author} paid {gettitle(user2)}{user} <:cash:1329017495536930886> 50 for no reason")
        gembed = discord.Embed(title="Good news!", description=f"{gettitle(userp)}{ctx.author} tried to commit larceny on you but failed! He paid you <:cash:1329017495536930886> 50 for nothing", color=color.green())
        gembed.timestamp = datetime.now()
        dm = self.bot.get_user(user.id)
        await dm.send(embed=gembed)
        await updateinc(user.id, 'cash', 50)
        await updateset(user.id, 'blocked', False)
        return
      else:
        await ctx.respond(f"The larceny is starting! There are {len(usersjoined)} users who joined the larceny")

      randomchance = round(random.random(), 6)
      chance = round((len(usersjoined)*0.15)-0.19,2)
      lenusersjoined = len(usersjoined)
      if randomchance <= chance:
        await updateset(user.id, 'timer.larceny', round(time.time())+14400)
        await updateset(user.id, 'stash', 0)
        userdied = []
        userd = []
        usersucceeded = []
        cashlost = 0
        for x in range(math.floor(len(usersjoined)*0.25)):
          userwhodied = random.choice(usersjoined)
          usersjoined.remove(userwhodied)
          userwhodieda = await finduser(int(userwhodied))
          userwhodiedname = userwhodieda['title']+userwhodieda['name']
          userwhodiedcash = userwhodieda['cash']
          cashlost += userwhodiedcash
          await updateset(int(userwhodied), 'cash', 0)
          userdied.append(userwhodiedname)
          userd = userdied
        cashearned = round(userstash / len(usersjoined))
        await updateset(user.id, 'cash', cashlost)
        for userwhojoined in usersjoined:
          userjoined = await finduser(int(userwhojoined))
          userjoinedname = userjoined['title']+userjoined['name']
          usersucceeded.append(userjoinedname)
          await updateinc(int(userwhojoined), 'cash', cashearned)
        if userdied == []:
          userdied.append("No user died")
        await ctx.respond(f"**Congratulations!**\n{lenusersjoined} users successfully stolen a total of <:cash:1329017495536930886> {userstash} from {gettitle(user2)}{user}'s stash!\n**Users who died:**\n{', '.join(userdied)}\n**Users who stole <:cash:1329017495536930886> {cashearned}:**\n{', '.join(usersucceeded)}")
        

        if not userd == []:
          dm = self.bot.get_user(user.id)
          larcembed = discord.Embed(title="You got stolen!", description=f"{gettitle(userp)}{ctx.author} along with {lenusersjoined} total users committed larceny on you and stolen <:cash:1329017495536930886> {userstash} in total!\nSome of them died and you gained a total of <:cash:1329017495536930886> {cashlost} from them",color=color.red())
          larcembed.timestamp = datetime.now()
          larcembed.set_footer(text="BIG RIP!")
          await dm.send(embed=larcembed)
        else:
          dm = self.bot.get_user(user.id)
          larcembed = discord.Embed(title="You got stolen!", description=f"{gettitle(userp)}{ctx.author} along with {lenusersjoined} total users committed larceny on you and stolen <:cash:1329017495536930886> {userstash} in total!\nToo bad no one died while committing larceny on you so you did not get anything back",color=color.red())
          larcembed.timestamp = datetime.now()
          larcembed.set_footer(text="BIG RIP!")
          await dm.send(embed=larcembed)

        await updateset(user.id, 'blocked', False)

      else:
        await ctx.respond(f"{len(usersjoined)} users tried to commit larceny on {gettitle(user2)}{user}'s stash but failed")
        gembed = discord.Embed(title="Good news!", description=f"{gettitle(userp)}{ctx.author} along with {len(usersjoined)} total users tried to commit larceny on you but failed! {gettitle(userp)}{ctx.author} paid you <:cash:1329017495536930886> 50 for nothing", color=color.green())
        gembed.timestamp = datetime.now()
        dm = self.bot.get_user(user.id)
        await dm.send(embed=gembed)
        await updateinc(user.id, 'cash', 50)
        for userjoined in usersjoined:
            await updateinc(int(userjoined), "heat", random.randint(50, 100))
        await updateset(user.id, 'blocked', False)
        return

async def race(self, ctx, user, bet):
        if await blocked(ctx.author.id) == False:
            ctx.command.reset_cooldown(ctx)
            return
        if user is None:
            await updateset(ctx.author.id, 'racing', True)
        guild = await self.bot.gcll.find_one({"id": ctx.guild.id})
        if guild['race'] == False and user is not None:
            await ctx.respond("You are not allowed to race with another user in this server!")
            await updateset(ctx.author.id, 'racing', False)
            return
        if user == ctx.author:
            await ctx.respond("You can't race yourself bruh")
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'racing', False)
            return
        userp = await finduser(ctx.author.id)
        if userp['drive'] == "":
            await ctx.respond("You have to drive a car to race!")
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'racing', False)
            return
        if not user is None:
            if await finduser(user.id) == None:
                await ctx.respond("This user haven't started playing OV Bot yet!")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'racing', False)
                return
        if userp['s'] == 24:
            await updateset(ctx.author.id, "s", 25)
        if user == None:
            await updateinc(ctx.author.id, "races", 1)

            msg = await ctx.interaction.original_response()

            usercarid = getdrive(userp, "id")
            usercar = getdrive(userp, "car")
            usercarname = usercar['name']
            if usercarname == "ThrustSSC":
              await ctx.respond("Your car has been banned from joining a race! (Too fast!!!)")
              ctx.command.reset_cooldown(ctx)
              return
            if usercarname == "1973 Ford Pinto":
                await self.die(ctx, ctx.author, "while driving your 1973 Ford Pinto to race", "You car were struck from the rear by another car and exploded")
                await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
                await updateset(ctx.author.id, 'drive', "")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'racing', False)
                return

            await ctx.respond("Heading towards the race, please wait..")

            usercarspeed = round(usercar['speed'], 2)

            usercargolden = usercar['golden']
            if usercargolden == True:
                usercarname = f"{star} Golden " + usercarname

            nc = [car for car in lists.allcars if lists.carspeed[car] > usercarspeed-30 and lists.carspeed[car] < usercarspeed+30]
            if nc == []:
              nc = [car for car in lists.allcars if lists.carspeed[car] > usercarspeed-100 and lists.carspeed[car] < usercarspeed+30]
            npccarname = random.choice(nc)
            npccarspeed = round(random.uniform(lists.carspeed[npccarname]-10, lists.carspeed[npccarname]+10), 2)

            if npccarspeed < 5:
                npccarspeed = 5

            fuel = ""

            if 'fuel' in userp['timer'] and 'methamphetamine' not in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*0.1), 2)
                fuel = " **(Boosted with fuel)**"
            elif 'fuel' not in userp['timer'] and 'methamphetamine' in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*(userp['drugs']['methamphetamine']*0.05)), 2)
                fuel = " **(Boosted with meth)**"
            elif 'fuel' in userp['timer'] and 'methamphetamine' in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*(0.1+(userp['drugs']['methamphetamine']*0.05) ) ) )
                fuel = " **(Boosted with fuel and meth)**"

            racemap = random.randint(0, 1)
            usercspeed = 0 # Current speed
            npccspeed = 0 # Current speed
            userdis = 0
            npcdis = 0
            mapname, racetrack = await functions.racetrack(racemap, userdis, npcdis)

            countdown = 3

            for i in range(countdown):

                raceembed = discord.Embed(title="Race! :checkered_flag:", description=f"{gettitle(userp)}{ctx.author.name} VS Random Hoodlum\n**Current Map:** {mapname}\n**STARTING IN {countdown}**", color=color.random())
                raceembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**Car** {usercarname}\n**Top Speed** {usercarspeed} MPH {fuel}", inline=True)
                raceembed.add_field(name=f"Random Hoodlum",value=f"**Car** {npccarname}\n**Top Speed** {npccarspeed} MPH", inline=True)
                raceembed.set_footer(text="Who will win?")
                raceembed.set_image(url="attachment://pic.png")

                if countdown == 3:
                    await msg.edit(content=None, embed=raceembed, attachments=[], file=racetrack)
                    await asyncio.sleep(3)
                else:
                    await msg.edit(embed=raceembed)

                countdown -= 1
                await asyncio.sleep(1)

            npcstats = {"stats": {"acc": random.triangular(0, userp['stats']['acc']+30, userp['stats']['acc']), "dri": random.triangular(0, userp['stats']['dri']+30, userp['stats']['dri']), "han": random.triangular(0, userp['stats']['han']+30, userp['stats']['han']), "luk": random.triangular(0, userp['stats']['luk']+30, userp['stats']['luk'])}}

            while True:
                userdis, usercspeed = await functions.raceevents(racemap, userdis, userp, usercspeed, usercarspeed)
                npcdis, npccspeed = await functions.raceevents(racemap, npcdis, npcstats, npccspeed, npccarspeed)
                mapname, racetrack = await functions.racetrack(racemap, userdis, npcdis)

                raceembed = discord.Embed(title="Race! :checkered_flag:", description=f"{gettitle(userp)}{ctx.author.name} VS Random Hoodlum\n**Current Map:** {mapname}", color=color.random())
                raceembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**Car** {usercarname}\n**Top Speed** {usercarspeed} MPH {fuel}\n**Current Speed** {usercspeed}", inline=True)
                raceembed.add_field(name=f"Random Hoodlum",value=f"**Car** {npccarname}\n**Top Speed** {npccarspeed} MPH\n**Current Speed** {npccspeed}", inline=True)
                raceembed.set_footer(text="Who will win?")
                raceembed.set_image(url="attachment://pic.png")

                await msg.edit(embed=raceembed, attachments=[], file=racetrack)

                await asyncio.sleep(3)

                if userdis >= 1000 or npcdis >= 1000:
                    break

            if userdis > npcdis:

                cashearned = round(random.uniform(60, 200))
                cashearned = round(cashearned + (cashearned*userp['stats']['cha'] / 1000) + (cashearned*dboost(userp['donor'])))
                if random.randint(1, 10) == 1:
                  token = 1
                else:
                  token = 0
                timedif = round((userdis-npcdis)/npccarspeed*10,2)

                winembed = discord.Embed(title=f"{gettitle(userp)}{ctx.author.name} won the race by {timedif} seconds!",description=f"You won the race against the Random Hoodlum!\nYou earned <:cash:1329017495536930886> {round(cashearned)}{(' and ' + str(token) + ' <:token:1313166204348792853>') if token != 0 else ''} from the race",color=color.green())
                winembed.set_footer(text="easy money")

                if random.random() < 0.05:
                  if random.randint(0,1) == 1:
                    winembed.add_field(name="Item found!",value="You found a Tuner!")
                    winembed.set_footer(text = "lucky!")
                    await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": round(cashearned), "token": token, "storage.Tuner": 1}, "$set": {"racing": False}})
                  else:
                    winembed.add_field(name="Item found!",value="You found an Average Car Key!")
                    winembed.set_footer(text = "lucky!")
                    await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": round(cashearned), "token": token, "storage.Average Car Key": 1}, "$set": {"racing": False}})
                else:
                  await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": round(cashearned), "token": token}, "$set": {"racing": False}})

                heat = 40
                deviation = 10
                await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
                await ctx.respond(embed=winembed)
            elif npcdis > userdis:
                diechance = round(random.random(),4)
                if userp['lvl'] < 5:
                    diechance = 1

                cashlost = round(random.uniform(5, 20))
                lostdis = npcdis - userdis
                timedif = round(lostdis/usercarspeed*10,2)

                if cashlost > userp['cash']:
                    cashlost = userp['cash']
                if diechance <= round(0.05-round(userp['stats']['bra']/10000*5, 2), 2):
                    lostembed = discord.Embed(title=f"Random Hoodlum won the race by {timedif} seconds!",description="You crashed your car and died!\nYour car is now damaged!",color=color.red())
                    lostembed.set_footer(text="so sad")
                    await ctx.respond(embed=lostembed)
                    await self.die(ctx, ctx.author, "from a race", "You crashed your car")
                    await self.repaircar(ctx, ctx.author, usercar, random.randint(50,150))
                else:
                    lostembed = discord.Embed(title=f"Random Hoodlum won the race by {timedif} seconds!",description=f"You lost the race against the Random Hoodlum!\nYou lost <:cash:1329017495536930886> {round(cashlost)} from the race",color=color.red())
                    lostembed.set_footer(text="so sad")
                    await updateinc(ctx.author.id,'cash',-(round(cashlost)))
                    await ctx.respond(embed=lostembed)
                    await updateset(ctx.author.id, 'racing', False)
            elif npcdis == userdis:

                tieembed = discord.Embed(title=f"Nobody won the race!",description=f"You both tied in the race!",color=color.gold())
                tieembed.set_footer(text="no cash for both of you")

                await ctx.respond(embed=tieembed)
                await updateset(ctx.author.id, 'racing', False)
                heat = 40
                deviation = 10
                await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
        elif user is not None:
            await updateset(ctx.author.id, 'blocked', True)
            user2 = await finduser(user.id)
            if ctx.guild.id in user2['q']:
                await ctx.respond("The user quarantined themself, how lonely")
                return
            if user2['injail'] == True:
                await ctx.respond("The user is in Jail! Too sad the user cannot race")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                return
            elif user2['inhosp'] == True:
                await ctx.respond("The user is in Hospital! Too sad the user cannot race")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                return
            if user2['drive'] == "":
                await ctx.respond("The user did not drive a car to race!")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                return

            view = interclass.Confirm(ctx, user)

            if bet is not None:
                if bet > 5000:
                    await ctx.respond("You cannot bet more than <:cash:1329017495536930886> 5000")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                elif bet < 10:
                    await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                if userp['cash'] < bet:
                    await ctx.respond("You are too poor for the bet")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                elif user2['cash'] < bet:
                    await ctx.respond("The user is too poor for the bet")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                await ctx.respond(f"{gettitle(user2)}{user.mention}, {gettitle(userp)}{ctx.author.mention} has challenged you to a race for **<:cash:1329017495536930886> {bet}** bet!\nDo you want to accept it?",view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg
            else:
                await ctx.respond(f"{gettitle(user2)}{user.mention}, {gettitle(userp)}{ctx.author.mention} has challenged you to a race!\nDo you want to accept it?",view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg

            await view.wait()

            if view.value is None:
                await ctx.respond(f"{gettitle(user2)}{user.mention} you didn't give a response, are you scared?")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                return
            elif view.value == False:
                await ctx.respond(f"{gettitle(user2)}{user.mention} is too scared to accept {gettitle(userp)}{ctx.author.mention}'s' challenge")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                return

            if bet is not None:
                await self.bot.cll.update_one({"id": {"$in": [ctx.author.id, user.id]}}, {"$inc": {"cash": -bet, "races": 1}})
            else:
                await self.bot.cll.update_one({"id": {"$in": [ctx.author.id, user.id]}}, {"$inc": {"races": 1}})
            await updateset(user.id, 'blocked', True)

            msg = await ctx.interaction.original_response()

            usercarid = getdrive(userp, "id")
            usercar = getdrive(userp, "car")
            usercarname = usercar['name']
            if usercarname == "ThrustSSC":
              await ctx.respond("Your car has been banned from joining a race! (Too fast!!!)")
              ctx.command.reset_cooldown(ctx)
              return
            if usercarname == "1973 Ford Pinto":
                await self.die(ctx, ctx.author, "while driving your 1973 Ford Pinto to race", "You car were struck from the rear by another car and exploded")
                await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": usercar}})
                await updateset(ctx.author.id, 'drive', "")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user.id, 'blocked', False)
                return

            await ctx.respond("Heading towards the race, please wait..")
            usercarspeed = round(usercar['speed'], 2)

            usercargolden = usercar['golden']
            if usercargolden == True:
                usercarname = f"{star} Golden " + usercarname

            userpfuel = ""
            if 'fuel' in userp['timer'] and 'methamphetamine' not in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*0.1), 2)
                userpfuel = " **(Boosted with fuel)**"
            elif 'fuel' not in userp['timer'] and 'methamphetamine' in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*(userp['drugs']['methamphetamine']*0.05)), 2)
                userpfuel = " **(Boosted with meth)**"
            elif 'fuel' in userp['timer'] and 'methamphetamine' in userp['timer']:
                usercarspeed = round(usercarspeed + (usercarspeed*(0.1+(userp['drugs']['methamphetamine']*0.05) ) ) )
                userpfuel = " **(Boosted with fuel and meth)**"

            user2 = await finduser(user.id)
            user2carid = getdrive(user2, "id")
            user2car = getdrive(user2, "car")
            user2carname = user2car['name']
            if user2carname == "ThrustSSC":
              await ctx.respond(f"{user.mention} Your car has been banned from joining a race! (Too fast!!!)")
              ctx.command.reset_cooldown(ctx)
              return
            if user2carname == "1973 Ford Pinto":
                await self.die(ctx, user, "while driving your 1973 Ford Pinto to race", "You car were struck from the rear by another car and exploded")
                await self.bot.cll.update_one({"id": user.id}, {"$pull": {"garage": user2car}})
                await updateset(user.id, 'drive', "")
                ctx.command.reset_cooldown(ctx)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user.id, 'blocked', False)
                return
            await ctx.respond("Heading towards the race, please wait..")
            user2carspeed = user2car['speed']

            user2cargolden = user2car['golden']
            if user2cargolden == True:
              user2carname = f"{star} Golden " + user2carname

            user2fuel = ""
            if 'fuel' in user2['timer'] and 'methamphetamine' not in user2['timer']:
                user2carspeed = round(user2carspeed + (user2carspeed*0.1), 2)
                user2fuel = " **(Boosted with fuel)**"
            elif 'fuel' not in user2['timer'] and 'methamphetamine' in user2['timer']:
                user2carspeed = round(user2carspeed + (user2carspeed*(user2['drugs']['methamphetamine']*0.05)), 2)
                user2fuel = " **(Boosted with meth)**"
            elif 'fuel' in user2['timer'] and 'methamphetamine' in user2['timer']:
                user2carspeed = round(user2carspeed + (user2carspeed*(0.1+(user2['drugs']['methamphetamine']*0.05) ) ) )
                user2fuel = " **(Boosted with fuel and meth)**"

            racemap = random.randint(0, 1)
            usercspeed = 0 # Current speed
            user2cspeed = 0 # Current speed
            userdis = 0
            user2dis = 0
            mapname, racetrack = await functions.racetrack(racemap, userdis, user2dis)

            countdown = 3

            for i in range(countdown):

                raceembed = discord.Embed(title="Race! :checkered_flag:", description=f"{gettitle(userp)}{ctx.author.name} VS {gettitle(user2)}{user.name}\n**Current Map:** {mapname}\n**STARTING IN {countdown}**", color=color.random())
                raceembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**Car** {usercarname}\n**Top Speed** {usercarspeed} MPH {userpfuel}", inline=True)
                raceembed.add_field(name=f"{gettitle(user2)}{user.name}",value=f"**Car** {user2carname}\n**Top Speed** {user2carspeed} MPH {user2fuel}", inline=True)
                raceembed.set_footer(text="Who will win?")
                raceembed.set_image(url="attachment://pic.png")

                if countdown == 3:
                    await msg.edit(content=None, embed=raceembed, attachments=[], file=racetrack)
                    await asyncio.sleep(3)
                else:
                    await msg.edit(embed=raceembed)

                countdown -= 1
                await asyncio.sleep(1)

            while True:
                userdis, usercspeed = await functions.raceevents(racemap, userdis, userp, usercspeed, usercarspeed)
                user2dis, user2cspeed = await functions.raceevents(racemap, user2dis, user2, user2cspeed, user2carspeed)
                mapname, racetrack = await functions.racetrack(racemap, userdis, user2dis)

                raceembed = discord.Embed(title="Race! :checkered_flag:", description=f"{gettitle(userp)}{ctx.author.name} VS {gettitle(user2)}{user.name}\n**Current Map:** {mapname}", color=color.random())
                raceembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**Car** {usercarname}\n**Top Speed** {usercarspeed} MPH {userpfuel}\n**Current Speed** {usercspeed}", inline=True)
                raceembed.add_field(name=f"{gettitle(user2)}{user.name}",value=f"**Car** {user2carname}\n**Top Speed** {user2carspeed} MPH {user2fuel}\n**Current Speed** {user2cspeed}", inline=True)
                raceembed.set_footer(text="Who will win?")
                raceembed.set_image(url="attachment://pic.png")

                await msg.edit(embed=raceembed, attachments=[], file=racetrack)

                await asyncio.sleep(3)

                if userdis >= 1000 or user2dis >= 1000:
                    break

            if userdis > user2dis:
                diechance = round(random.random(),4)

                if bet is None:
                    cashearned = round(random.uniform(5,15))
                    cashearned = round(cashearned + (cashearned*userp['stats']['cha'] / 1000) + (cashearned*dboost(userp['donor'])))
                elif bet is not None:
                    cashearned = round(bet*0.95) # Tax
                if random.randint(1, 10) == 1:
                  token = 1
                else:
                  token = 0
                if cashearned > user2['cash']:
                    cashearned = user2['cash']
                windis = userdis - user2dis
                timedif = round(windis/user2carspeed*10,2)

                winembed = discord.Embed(title=f"{gettitle(userp)}{ctx.author.name} won the race by {timedif} seconds!",description=f"{gettitle(userp)}{ctx.author.name} won the race against {gettitle(user2)}{user.name}!\nYou earned <:cash:1329017495536930886> {round(cashearned)} from {gettitle(user2)}{user.name}{(' and ' + str(token) + ' <:token:1313166204348792853>') if token != 0 else ''}",color=color.green())
                if diechance <= round(0.05-round(user2['stats']['bra']/10000*5, 2), 2):
                    winembed.add_field(name="Whoops!",value=f"{gettitle(user2)}{user.name} crashed their car and died!\n{gettitle(user2)}{user.name} your car is now damaged!",inline=False)
                    await self.die(ctx, user, "from a race", "You crashed your car")
                    await self.repaircar(ctx, user, user2car, random.randint(50,150))
                else:
                    await updateinc(user.id,'cash',-(round(cashearned)))
                winembed.set_footer(text="easy money")

                await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": round(cashearned), "token": token}, "$set": {"blocked": False}})
                heat = 40
                deviation = 10
                await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
                await ctx.respond(embed=winembed)
                await updateset(user.id, 'blocked', False)

            elif user2dis > userdis:
                diechance = round(random.random(),4)

                if bet is None:
                    cashearned = round(random.uniform(5,15))
                    cashearned = round(cashearned + (cashearned*user2['stats']['cha'] / 1000) + (cashearned*dboost(userp['donor'])))
                elif bet is not None:
                    cashearned = round(bet*0.95) # Tax
                if random.randint(1, 10) == 1:
                  token = 1
                else:
                  token = 0
                if cashearned > userp['cash']:
                    cashearned = userp['cash']
                windis = user2dis - userdis
                timedif = round(windis/usercarspeed*10,2)

                winembed = discord.Embed(title=f"{gettitle(user2)}{user.name} won the race by {timedif} seconds!",description=f"{gettitle(user2)}{user.name} won the race against {gettitle(userp)}{ctx.author.name}!\nYou earned <:cash:1329017495536930886> {round(cashearned)} from {gettitle(userp)}{ctx.author.name}{(' and ' + str(token) + ' <:token:1313166204348792853>') if token != 0 else ''}",color=color.green())
                if diechance <= round(0.05-round(userp['stats']['bra']/10000*5, 2), 2):
                    winembed.add_field(name="Whoops!",value=f"{gettitle(userp)}{ctx.author.name} crashed his/her car and died!\n{gettitle(userp)}{ctx.author.name} your car is now damaged!",inline=False)
                    await self.die(ctx, ctx.author, "from a race", "You crashed your car")
                    await self.repaircar(ctx, ctx.author, usercar, random.randint(50,150))
                else:
                    await updateinc(ctx.author.id,'cash',-round(cashearned))
                winembed.set_footer(text="slow slow")

                await self.bot.cll.update_one({"id": user.id}, {"$inc": {"cash": round(cashearned), "token": token}, "$set": {"blocked": False}})
                heat = 40
                deviation = 10
                await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
                await ctx.respond(embed=winembed)
                await updateset(ctx.author.id, 'blocked', False)

            elif userdis == user2dis:

                tieembed = discord.Embed(title=f"Nobody won the race!",description=f"You both tied in the race!",color=color.gold())
                tieembed.set_footer(text="no cash for both of you")

                await ctx.respond(embed=tieembed)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user.id, 'blocked', False)
                heat = 40
                deviation = 10
                await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
                await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )

async def bust(self, ctx, user):
        if await blocked(ctx.author.id) == False:
            ctx.command.reset_cooldown(ctx)
            return
        userp = await finduser(ctx.author.id)
        if userp['lvl'] < 5:
            await ctx.respond("You have to be lvl 5 before busting!")
            return
        random.seed(time.time())
        if user is None or isinstance(user, int):
            page = user or 1
            injail = await self.bot.cll.find({"timer.jail": {"$gt": round(time.time())}}).to_list(length=None)
            random.shuffle(injail)
            maxpage = len(injail)
            maxpage = maxpage or 1
            if page > maxpage:
                ctx.command.reset_cooldown(ctx)
                await ctx.respond(f"There are only {maxpage} pages")
                return

            jembed = discord.Embed(title="Jail", color=color.blurple()).set_footer(text=f"Bust someone with their ID\nLower level is easier to bust\nbut lesser experience!\nPage {page} of {maxpage}")

            if not len(injail):
                jembed.description = "**There are no inmates to bust**\n\n_ _"
                await ctx.respond(embed=jembed)
                ctx.command.reset_cooldown(ctx)
                return
            else:
                injail = injail[(page-1)]
                jembed.description = f"**{injail['title']}{injail['name']}**\nLevel **{injail['lvl']}**\n**Time left in Jail** {ab(round(injail['timer']['jail']-round(time.time())))}"
                jembed.set_thumbnail(url=self.bot.get_user(injail['id']).display_avatar.url)
                byte = functions.charimg(injail)
                file = discord.File(fp=byte, filename="character.png")
                jembed.set_image(url="attachment://character.png")

                view = interclass.Bust(ctx, ctx.author)

                await ctx.respond(file=file, embed=jembed, view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg

            while True:
                await view.wait()

                if view.value is None:
                    return
                elif view.value == "left":
                    page = page - 1 if page > 1 else page
                elif view.value == "right":
                    page = page + 1 if page < maxpage else page
                elif view.value == "bust":
                    user = self.bot.get_user(injail['id'])
                    break

                injail = await self.bot.cll.find({"timer.jail": {"$gt": round(time.time())}}).to_list(length=None)
                random.shuffle(injail)
                maxpage = len(injail)
                maxpage = maxpage or 1
                if page > maxpage: page = maxpage

                jembed = discord.Embed(title="Jail", color=color.blurple()).set_footer(text=f"Bust someone with their ID\nLow level players are easier to bust but gives lesser experience!\nPage {page} of {maxpage}")

                if not len(injail):
                    jembed.description = "**There are no inmates to bust**\n\n_ _"
                    await msg.edit(embed=jembed)
                    ctx.command.reset_cooldown(ctx)
                    return
                else:
                    injail = injail[(page-1)]
                    jembed.description = f"**{injail['title']}{injail['name']}**\nLevel **{injail['lvl']}**\n**Time left in Jail** {ab(round(injail['timer']['jail']-round(time.time())))}"
                    jembed.set_thumbnail(url=self.bot.get_user(injail['id']).display_avatar.url)
                    byte = functions.charimg(injail)
                    file = discord.File(fp=byte,filename="character.png")
                    jembed.set_image(url="attachment://character.png")

                view = interclass.Bust(ctx, ctx.author)

                view.message = await msg.edit(file=file, attachments=[], embed=jembed, view=view)

        target = await finduser(user.id)
        if target is None:
            await ctx.respond("Cannot find this user!")
            ctx.command.reset_cooldown(ctx)
            return
        if not target['injail']:
            await ctx.respond("The user is not in Jail!")
            ctx.command.reset_cooldown(ctx)
            return
        ran = (round(random.random(), 4)*(round(userp['lvl']/(1 if target['lvl'] <= 0 else target['lvl']), 2))) 
        ran = ran + (ran * getluck(userp) * (1.5 if userp['donor'] == 2 else 1.2 if userp['donor'] == 1 else 1))
        ran = 0.8 if ran > 0.8 else 0.05 if ran < 0.05 else ran
        if ran > round(random.random(), 4):
            await updateinc(ctx.author.id, "rep", 1)
            await updateset(user.id, 'injail', False)
            await self.bot.cll.update_one({"id": user.id}, {"$unset": {"timer.jail": 1}})
            embed = discord.Embed(title="Busted", description=f"You successfully busted {target['title']}{user} out of the Jail and gained 1 reputation point!", color=color.green()).set_footer(text="pog")
            await ctx.respond(embed=embed)
            embed = discord.Embed(title="Busted", description=f"{gettitle(userp)}{ctx.author} busted you out of Jail!\nYou no longer have to wait", color=color.green()).set_footer(text="pog")
            await user.send(embed=embed)
        else:
            heat = 40
            deviation = 10
            await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
            embed = discord.Embed(title="Failed", description=f"You tried to bust {target['title']}{user} out of Jail but failed!", color=color.red()).set_footer(text="haha bad")
            await ctx.respond(embed=embed)

async def shoplift(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      if user['lvl'] < 5:
        await ctx.respond("You have to be at least level 5!")
        return
      firstplace = random.choice(lists.randomplaces)
      secondplace = random.choice(lists.randomplaces)
      thirdplace = random.choice(lists.randomplaces)

      while firstplace == secondplace or firstplace == thirdplace or secondplace == firstplace or secondplace == thirdplace or thirdplace == firstplace or thirdplace == secondplace:
        firstplace = random.choice(lists.randomplaces)
        secondplace = random.choice(lists.randomplaces)
        thirdplace = random.choice(lists.randomplaces)

      e = discord.Embed(title="Which place do you want to shoplift?",description=f"\U00000031\U0000FE0F\U000020E3 **{firstplace}**\n\U00000032\U0000FE0F\U000020E3 **{secondplace}**\n\U00000033\U0000FE0F\U000020E3 **{thirdplace}**",color=color.blurple())

      view = interclass.Three(ctx)

      await ctx.respond(embed=e,view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      if view.value is None:
        await ctx.respond("You are too slow, the shop is already closed")
        return
      elif view.value == "1":
        selectedplace = firstplace
      elif view.value == "2":
        selectedplace = secondplace
      elif view.value == "3":
        selectedplace = thirdplace

      randomcash = random.randint(6, 12)
      randomcash = round(randomcash + (randomcash*user['stats']['cha']/1000) + (randomcash*dboost(user['donor'])))
      randomsuccess = round(random.random(),4)
      try:
        placechance = lists.placechance[selectedplace] + (lists.placechance[selectedplace]*getluck(user))
      except:
        placechance = 0
      if randomsuccess <= (lists.commonplacechance[selectedplace] + (lists.commonplacechance[selectedplace]*getluck(user))) and not randomsuccess < placechance:
        commonitem = lists.commonplaceitem[selectedplace]
        if type(commonitem) is list:
          commonitem = random.choice(commonitem)
        embed = discord.Embed(title="Shoplifting",description=f"You went to {selectedplace} for shoplifting and stole a {commonitem}!",color=color.green())
        await updateinc(ctx.author.id, f'storage.{commonitem}', 1)
      elif randomsuccess < placechance:
        item = lists.placeitem[selectedplace]
        if type(item) is list:
          item = random.choice(item)
        embed = discord.Embed(title="Shoplifting",description=f"You went to {selectedplace} for shoplifting and stole a {item}!",color=color.green())
        await updateinc(ctx.author.id, f'storage.{item}', 1)
      else:
        if not selectedplace == "Weapon store":
          heat = 40
          deviation = 10
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user))) ) )
          embed = discord.Embed(title="Shoplifting",description=f"You went to {selectedplace} for shoplifting but failed!\nBut you still managed to steal <:cash:1329017495536930886> {randomcash}",color=color.red())
          await updateinc(ctx.author.id, "cash", randomcash)
        else:
          randomdiechance = round(random.random(),4)
          embed = discord.Embed(title="Shoplifting",description=f"You went to {selectedplace} for shoplifting but failed!\nBut you still managed to steal <:cash:1329017495536930886> {randomcash}",color=color.red())
          await updateinc(ctx.author.id, "cash", randomcash)
          if randomdiechance <= 0.1 - (0.1*getluck(user)):
            embed.add_field(name="Whoops!",value="The store owner brought up a shotgun and blasted you!")
            await self.die(ctx, ctx.author, "while shoplifting a Weapon store", "You have been shot by the store owner")
          embed.set_footer(text="huge rip")
          await ctx.respond(embed=embed)
          return

      embed.set_footer(text="very small chance you will find a rare item!")

      await ctx.respond(embed=embed)

async def attack(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        await asyncio.sleep(5)
        return
      await updateset(ctx.author.id, 'blocked', True)
      guild = await self.bot.gcll.find_one({"id": ctx.guild.id})
      guildatt = guild['attack']
      if guildatt == False and user is not None:
        await ctx.respond("You cannot attack another user on this server!", ephemeral=True)
        await updateset(ctx.author.id, 'blocked', False)
        ctx.command.reset_cooldown(ctx)
        return
      userp = await finduser(ctx.author.id)
      if userp['lvl'] < 5:
        await ctx.respond("You have to be at least level 5 to attack!", ephemeral=True)
        await updateset(ctx.author.id, 'blocked', False)
        ctx.command.reset_cooldown(ctx)
        return
      if user is None:
        user2 = {"donor": 0, "storage": {"Grenade": 0}, "name": "Random Hoodlum#0", "injail": False, "inhosp": False, "title": "", "equipments": {"background": "", "back": "", "skin": "normal", "head": random.choice(lists.headw+[""]), "chest": "", "leg": "", "foot": "", "face": random.choice(lists.facew+[""]), "hair": "", "weapon": random.choice(lists.weapon+lists.melee+[""])}, "lvl": random.randint(userp['lvl']-10, (userp['lvl']+10) if (userp['lvl']+10) <= 160 else 160), "stats": {"str": round(random.uniform(userp['stats']['str']-20, userp['stats']['str']+20), 2), "def": round(random.uniform(userp['stats']['def']-20, userp['stats']['def']+20), 2), "spd": round(random.uniform(userp['stats']['spd']-20, userp['stats']['spd']+20), 2), "dex": round(random.uniform(userp['stats']['dex']-20, userp['stats']['dex']+20), 2), "luk": round(random.uniform(0 if userp['stats']['luk']-20 < 0 else userp['stats']['luk']-20, userp['stats']['luk']+20), 2)}, "cash": random.randint(100, 300), "drugs": {"cannabis": 0, "ecstasy": 0, "heroin": 0, "methamphetamine": 0, "xanax": 0}}
        if userp['s'] == 40:
            user2 = {"donor": 0, "storage": {"Grenade": 0}, "name": "Random Hoodlum#0", "injail": False, "inhosp": False, "title": "", "equipments": {"background": "", "back": "", "skin": "normal", "head": "", "chest": "", "leg": "", "foot": "", "face": "", "hair": "", "weapon": "Baseball Bat"}, "lvl": 5, "stats": {"str": 5, "def": 5, "spd": 5, "dex": 5, "luk": 0}, "cash": random.randint(10, 300), "drugs": {"cannabis": 0, "ecstasy": 0, "heroin": 0, "methamphetamine": 0, "xanax": 0}}
        user2['lvl'] = 5 if user2['lvl'] < 5 else user2['lvl']
        user2['stats']['str'] = 10 if user2['stats']['str'] < 10 else user2['stats']['str']
        user2['stats']['def'] = 10 if user2['stats']['def'] < 10 else user2['stats']['def']
        user2['stats']['spd'] = 10 if user2['stats']['spd'] < 10 else user2['stats']['spd']
        user2['stats']['dex'] = 10 if user2['stats']['dex'] < 10 else user2['stats']['dex']
        user2['stats']['luk'] = 10 if user2['stats']['luk'] < 10 else user2['stats']['luk']
      if user is not None:
          if user == ctx.author:
            await ctx.respond("You can't attack yourself idiot", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'blocked', False)
            return
      await ctx.channel.trigger_typing()
      if user is not None:
          if await finduser(user.id) == None:
            await ctx.respond("This user haven't started playing OV Bot yet!", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'blocked', False)
            return
      if user is not None:
        user2 = await finduser(user.id)
        if ctx.guild.id in user2['q']:
            await ctx.respond("The user quarantined themself, how lonely", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'blocked', False)
            return
        if user2['lvl'] < 5:
            await ctx.respond("You can only attack players who is above level 5!", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            await updateset(ctx.author.id, 'blocked', False)
            return
        await ctx.respond("Searching for the user...")
      else:
        await ctx.respond("Searching for random hoodlums...")
      att = await ctx.interaction.original_response()
      try:
        for timer in list(userp['timer']):
            if timer.startswith("user"):
                if userp['timer'][timer] <= round(time.time()):
                    await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f"timer.{timer}": 1}})
      except:
        pass
      userp = await finduser(ctx.author.id)
      try:
        if user.id in [int(timer[4:]) for timer in list(userp['timer']) if timer.startswith("user")]:
          await ctx.respond(f"You already beat this user recently! You have to wait {ab([userp['timer'][timer] for timer in list(userp['timer']) if timer.startswith('user') and int(timer[4:]) == user.id][0]-round(time.time()))} before bullying the user again", ephemeral=True)
          ctx.command.reset_cooldown(ctx)
          await updateset(ctx.author.id, 'blocked', False)
          await att.delete()
          return
      except:
        pass
      user2injail = user2['injail']
      user2inhosp = user2['inhosp']
      if user2injail == True:
        await ctx.respond("The user is in Jail! Too sad you can't attack them", ephemeral=True)
        ctx.command.reset_cooldown(ctx)
        await updateset(ctx.author.id, 'blocked', False)
        await att.delete()
        return
      elif user2inhosp == True:
        await ctx.respond("The user is in Hospital! Too sad you can't attack them", ephemeral=True)
        ctx.command.reset_cooldown(ctx)
        await updateset(ctx.author.id, 'blocked', False)
        await att.delete()
        return

      if user is not None:
        await updateset(user.id, 'blocked', True)
      userhealth, userpweapondmg, userstr, userdef, userspd, userdex = functions.atkboost(userp)
      usermaxhealth = userhealth
      userpweapon = userp['equipments']['weapon']

      user2health, user2weapondmg, user2str, user2def, user2spd, user2dex = functions.atkboost(user2)
      user2maxhealth = user2health
      user2weapon = user2['equipments']['weapon']

      if userpweapon == '':
        userpweapon = "No weapon"
      if user2weapon == '':
        user2weapon = "No weapon"

      if 'Grenade' in userp['storage']:
        usergrenade = userp['storage']['Grenade']
      else:
        usergrenade = 0

      attembed = discord.Embed(title="**ATTACK**",description=f"**It's your turn {gettitle(userp)}{ctx.author.mention}, what do you wanna do?**",color=color.blue())
      attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
      attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
      attembed.set_footer(text="Who's gonna win?")
      file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
      attembed.set_image(url="attachment://pic.png")
      if not userpweapon == 'No weapon':
        view = interclass.Attww(ctx, userpweapon, True, usergrenade)
      else:
        view = interclass.Att(ctx, True, usergrenade)
      await att.edit(ctx.author.mention, embed=attembed, file=file, view=view)
      view.message = att
      logs = []
      logs.append(f"The battle between {gettitle(userp)}{ctx.author.name} and {gettitle(user2)}{user2['name'][:-5]} has started!")

      while True:
        await view.wait()
        if view.value is None:
            attembed.description = f"**{gettitle(userp)}{ctx.author.mention} you didn't give a response so you lost the fight.**"
            logs.append(f"{gettitle(userp)}{ctx.author.name} didn't give a response and lost the fight")
            view = interclass.Attll(ctx, logs)
            view.message = await att.edit(embed=attembed, view=view)
            heat = 100
            deviation = 50
            if user is not None:
                rexp = round(random.uniform(3,6),2)
                bonus = (1/(user2['lvl']/userp['lvl']))
                rexp = round(rexp*(bonus if bonus <= 2 else 2), 2)
                if functions.not_max_level(user2):
                    await updateinc(user.id, 'exp', rexp)
                else:
                    rexp = 0
                winembed = discord.Embed(title="Attack won!",description=f"{gettitle(userp)}{ctx.author} tried to attack you but lost!\n\nYou gained {rexp} experience!",color=color.green())
                winembed.set_footer(text="easy win")
                await user.send(embed=winembed)
                await updateset(user.id, 'blocked', False)
                await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
            await updateset(ctx.author.id, 'blocked', False)
            await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
            while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
            return
        if view.value == "1":
          randomchance = round(random.random(),4)
          hitchance = round((userspd / user2dex / 2)+0.25,4)
          hitdamage = round(random.uniform(round((userstr / user2def * 10)-3,2),round((userstr / user2def * 10)+3,2)),2)

          pos = (["in the hand"]*5 + ["in the foot"]*5 + ["in the arm"]*10 + ["in the leg"]*10 + ["in the chest"]*40 + ["in the groin"]*20 + ["in the head"]*8 + ["in the **neck**"]*2)[round((1-random.triangular(0, 1, (500-userp['stats']['luk']+100)/1000))*100)-1]
          hitdamge = round(hitdamage * (0.5 if pos == "in the hand" or pos == "in the foot" else 0.75 if pos == "in the arm" or pos == "in the leg" else 1 if pos == "in the chest" else 1.2 if pos == "in the groin" else 1.5 if pos == "in the head" else 2), 2)

          if hitdamage < 1:
            hitdamage = 1
          if randomchance <= hitchance:
            user2health = round(user2health-hitdamage,2)
            logs.append(f"{gettitle(userp)}{ctx.author.name} hit {gettitle(user2)}{user2['name'][:-5]} {pos} with fist and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health,2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(userp)}{ctx.author.name} hit {gettitle(user2)}{user2['name'][:-5]} {pos} with fist and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health,2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          elif randomchance > hitchance:
            attembed.description = f"**{gettitle(userp)}{ctx.author.name} tried to hit {gettitle(user2)}{user2['name'][:-5]} but missed!**"
            await att.edit(embed=attembed)
            logs.append(f"{gettitle(userp)}{ctx.author.name} tried to hit {gettitle(user2)}{user2['name'][:-5]} but missed!")
          if user2health <= 0:
            break
        elif view.value == "2":
          randomchance = round(random.random(),4)
          hitchance = round((userspd / user2dex / 2)+0.25,4)
          hitdamage = round(random.uniform(round((userstr / user2def * 10)-3,2),round((userstr / user2def * 10)+3,2)) + userpweapondmg, 2)
          
          pos = (["in the hand"]*5 + ["in the foot"]*5 + ["in the arm"]*10 + ["in the leg"]*10 + ["in the chest"]*40 + ["in the groin"]*20 + ["in the head"]*8 + ["in the **neck**"]*2)[round((1-random.triangular(0, 1, (500-userp['stats']['luk']+100)/1000))*100)-1]
          hitdamge = round(hitdamage * (0.5 if pos == "in the hand" or pos == "in the foot" else 0.75 if pos == "in the arm" or pos == "in the leg" else 1 if pos == "in the chest" else 1.2 if pos == "in the groin" else 1.5 if pos == "in the head" else 2), 2)

          if hitdamage < 1:
            hitdamage = 1
          if userpweapon in lists.melee:
            m = "hit"
            a = "hit"
          else:
            m = "shot"
            a = "shoot"
          if randomchance <= hitchance:
            user2health = round(user2health-hitdamage,2)
            logs.append(f"{gettitle(userp)}{ctx.author.name} {m} {gettitle(user2)}{user2['name'][:-5]} {pos} with {userpweapon} and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(userp)}{ctx.author.name} {m} {gettitle(user2)}{user2['name'][:-5]} {pos} with {userpweapon} and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          elif randomchance > hitchance:
            attembed.description = f"**{gettitle(userp)}{ctx.author.name} tried to {a} {gettitle(user2)}{user2['name'][:-5]} but missed!**"
            await att.edit(embed=attembed)
            logs.append(f"{gettitle(userp)}{ctx.author.name} tried to {a} {gettitle(user2)}{user2['name'][:-5]} but missed!")
          if user2health <= 0:
            break
        elif view.value == "3":
          logs.append(f"{gettitle(userp)}{ctx.author.name} fled away what a coward")
          attembed.description = f"**{gettitle(userp)}{ctx.author.name} fled away what a coward**"
          view = interclass.Attll(ctx, logs)
          view.message = await att.edit(embed=attembed, view=view)
          heat = 100
          deviation = 50
          if user is not None:
              rexp = round(random.uniform(3,6),2)
              bonus = (1/(user2['lvl']/userp['lvl']))
              rexp = round(rexp*(bonus if bonus <= 2 else 2), 2)
              if functions.not_max_level(user2):
                await updateinc(user.id, 'exp', rexp)
              else:
                rexp = 0
              winembed = discord.Embed(title="Attack won!",description=f"{gettitle(userp)}{ctx.author} tried to attack you but they fled away!\n\nYou gained {rexp} experience!",color=color.green())
              winembed.set_footer(text="easy win")
              await user.send(embed=winembed)
              await updateset(user.id, 'blocked', False)
              await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
          await updateset(ctx.author.id, 'blocked', False)
          while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
          return
        elif view.value == "4":
          randomchance = round(random.random(),4)
          hitchance = 0.6 + (0.3*getluck(userp))

          usergrenade -= 1
          if usergrenade == 0:
            await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.Grenade': 1}})
          else:
            await updateinc(ctx.author.id, "storage.Grenade", -1)

          if randomchance <= hitchance:
            hitdamage = round((user2maxhealth * 0.6) + 60, 2)
          else:
            hitdamage = round((user2maxhealth * 0.4) + 60, 2)
          
          if hitdamage < 1:
            hitdamage = 1

          user2health = round(user2health-hitdamage,2)
          if randomchance <= hitchance:
            logs.append(f"{gettitle(userp)}{ctx.author.name} threw a grenade onto {gettitle(user2)}{user2['name'][:-5]} and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(userp)}{ctx.author.name} threw a grenade onto {gettitle(user2)}{user2['name'][:-5]} and dealt {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          elif randomchance > hitchance:
            logs.append(f"{gettitle(userp)}{ctx.author.name} threw a grenade onto {gettitle(user2)}{user2['name'][:-5]}, they took cover but still received {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(userp)}{ctx.author.name} threw a grenade onto {gettitle(user2)}{user2['name'][:-5]}, they took cover but still received {hitdamage} damage! {gettitle(user2)}{user2['name'][:-5]} is now left with {round(user2health, 2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          if user2health <= 0:
            break

        await asyncio.sleep(2)
        hitdamage = round(random.uniform(round((user2str / userdef * 10)-3,2),round((user2str / userdef * 10)+3,2)),2)
        if hitdamage < 1:
          hitdamage = 1

        if not user2weapon == "No weapon":
            choice = random.randint(1, 2)
        else:
            choice = 2

        if choice == 1:
          randomchance = round(random.random(),4)
          hitchance = round((user2spd / userdex / 2)+0.25,4)
          hitdamage = round(random.uniform(round((user2str / userdef * 10)-3,2),round((user2str / userdef * 10)+3,2)) + user2weapondmg, 2)
          
          pos = (["in the hand"]*5 + ["in the foot"]*5 + ["in the arm"]*10 + ["in the leg"]*10 + ["in the chest"]*40 + ["in the groin"]*20 + ["in the head"]*8 + ["in the **neck**"]*2)[round((1-random.triangular(0, 1, (500-user2['stats']['luk']+100)/1000))*100)-1]
          hitdamge = round(hitdamage * (0.5 if pos == "in the hand" or pos == "in the foot" else 0.75 if pos == "in the arm" or pos == "in the leg" else 1 if pos == "in the chest" else 1.2 if pos == "in the groin" else 1.5 if pos == "in the head" else 2), 2)

          if hitdamage < 1:
            hitdamage = 1
          if user2weapon in lists.melee:
            m = "hit"
            a = "hit"
          else:
            m = "shot"
            a = "shoot"
          if randomchance <= hitchance:
            userhealth = round(userhealth-hitdamage,2)
            logs.append(f"{gettitle(user2)}{user2['name'][:-5]} {m} {gettitle(userp)}{ctx.author.name} {pos} with {user2weapon} and dealt {hitdamage} damage! {gettitle(userp)}{ctx.author.name} is now left with {round(userhealth, 2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(user2)}{user2['name'][:-5]} {m} {gettitle(userp)}{ctx.author.name} {pos} with {user2weapon} and dealt {hitdamage} damage! {gettitle(userp)}{ctx.author.name} is now left with {round(userhealth, 2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          elif randomchance > hitchance:
            attembed.description = f"**{gettitle(user2)}{user2['name'][:-5]} tried to {a} {gettitle(userp)}{ctx.author.name} but missed!**"
            await att.edit(embed=attembed)
            logs.append(f"{gettitle(user2)}{user2['name'][:-5]} tried to {a} {gettitle(userp)}{ctx.author.name} but missed!")
          if userhealth <= 0:
            break

        elif choice == 2:
          randomchance = round(random.random(),4)
          hitchance = round((user2spd / userdex / 2)+0.25,4)
          
          pos = (["in the hand"]*5 + ["in the foot"]*5 + ["in the arm"]*10 + ["in the leg"]*10 + ["in the chest"]*40 + ["in the groin"]*20 + ["in the head"]*8 + ["in the **neck**"]*2)[round((1-random.triangular(0, 1, (500-user2['stats']['luk']+100)/1000))*100)-1]
          hitdamge = round(hitdamage * (0.5 if pos == "in the hand" or pos == "in the foot" else 0.75 if pos == "in the arm" or pos == "in the leg" else 1 if pos == "in the chest" else 1.2 if pos == "in the groin" else 1.5 if pos == "in the head" else 2), 2)

          if hitdamage < 1:
            hitdamage = 1
          if randomchance <= hitchance:
            userhealth = round(userhealth-hitdamage,2)
            logs.append(f"{gettitle(user2)}{user2['name'][:-5]} hit {gettitle(userp)}{ctx.author.name} {pos} with fist and dealt {hitdamage} damage! {gettitle(userp)}{ctx.author.name} is now left with {round(userhealth,2)} HP")
            attembed = discord.Embed(title="**ATTACK**",description=f"**{gettitle(user2)}{user2['name'][:-5]} hit {gettitle(userp)}{ctx.author.name} {pos} with fist and dealt {hitdamage} damage! {gettitle(userp)}{ctx.author.name} is now left with {round(userhealth,2)} HP**",color=color.blue())
            attembed.add_field(name=f"{gettitle(userp)}{ctx.author.name}",value=f"**STR:** {userstr} | **DEF:** {userdef} | **SPD:** {userspd} | **DEX:** {userdex}\n**HP:** {userhealth}\n**Weapon:** {userpweapon}")
            attembed.add_field(name=f"{gettitle(user2)}{user2['name'][:-5]}",value=f"**STR:** {user2str} | **DEF:** {user2def} | **SPD:** {user2spd} | **DEX:** {user2dex}\n**HP:** {user2health}\n**Weapon:** {user2weapon}")
            attembed.set_footer(text="Who's gonna win?")
            file = discord.File(fp=functions.attack_image(userhealth, user2health, userp, user2), filename="pic.png")
            attembed.set_image(url="attachment://pic.png")
            await att.edit(embed=attembed, file=file, attachments=[])
          elif randomchance > hitchance:
            attembed.description = f"**{gettitle(user2)}{user2['name'][:-5]} tried to hit {gettitle(userp)}{ctx.author.name} but missed!**"
            await att.edit(embed=attembed)
            logs.append(f"{gettitle(user2)}{user2['name'][:-5]} tried to hit {gettitle(userp)}{ctx.author.name} but missed!")
          if userhealth <= 0:
            break

        await asyncio.sleep(2)

        if not userpweapon == 'No weapon':
            view = interclass.Attww(ctx, userpweapon, False, usergrenade)
        else:
            view = interclass.Att(ctx, False, usergrenade)
        attembed.description = f"**It's your turn {gettitle(userp)}{ctx.author.mention}, what do you wanna do?**"
        view.message = await att.edit(embed=attembed, view=view)
      
      await asyncio.sleep(2)

      if user2health <= 0:
        view = interclass.Attl(ctx)
        attembed.description = f"**{gettitle(userp)}{ctx.author.mention} You won the battle! What do you wanna do now?**"
        view.message = await att.edit(embed=attembed, view=view)
        logs.append(f"{gettitle(userp)}{ctx.author.name} won the battle against {gettitle(user2)}{user2['name'][:-5]}")
        await view.wait()
        if view.value == None:
          attembed.description = f"**{gettitle(userp)}{ctx.author.mention} you didn't give a response so you got nothing**"
          logs.append(f"{gettitle(userp)}{ctx.author.name} didn't give a response and got nothing from {gettitle(user2)}{user2['name'][:-5]}")
          view = interclass.Attll(ctx, logs)
          view.message = await att.edit(embed=attembed, view=view)
          heat = 100
          deviation = 50
          if user is not None:
              winembed = discord.Embed(title="Attack lost!",description=f"Someone beaten you up!\n\nThey didn't do anything after winning so you lost nothing",color=color.red())
              winembed.set_footer(text="take a revenge noob")
              await user.send(embed=winembed)
              await updateset(user.id, 'blocked', False)
              await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
          await updateset(ctx.author.id, 'blocked', False)
          while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
          return
        if view.value == '1':
          heat = 100
          deviation = 50
          if user is not None:
            user2 = await finduser(user.id)
            await updateset(user.id, 'blocked', False)
            await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
          user2cash = user2['cash']
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
          await updateset(ctx.author.id, 'blocked', False)
          if user2cash > 0:
            rcash = round(user2cash*round(random.uniform(0.1, 1),2))
            if rcash < 1:
              rcash = 1
            token = random.randint(4, 6)
            token = round(token*user2['lvl']/userp['lvl']) if round(token*user2['lvl']/userp['lvl']) <= token else token
            logs.append(f"{gettitle(userp)}{ctx.author.name} mugged {gettitle(user2)}{user2['name'][:-5]} for <:cash:1329017495536930886> {rcash}")
            attembed.description = f"**You mugged {gettitle(user2)}{user2['name'][:-5]} for <:cash:1329017495536930886> {rcash}!\nYou also earned {token} <:token:1313166204348792853>!**"
            view = interclass.Attll(ctx, logs)
            view.message = await att.edit(embed=attembed, view=view)
            await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {'cash': round(rcash), 'token': token}})
            if user is not None:
                await updateinc(user.id, 'cash', -round(rcash))
                winembed = discord.Embed(title="Attack lost!",description=f"Someone beaten you up!\n\nThey mugged you for <:cash:1329017495536930886> {rcash}",color=color.red())
                winembed.set_footer(text="take a revenge noob")
                await user.send(embed=winembed)
          elif user2cash <= 0:
            logs.append(f"{gettitle(userp)}{ctx.author.name} mugged {gettitle(user2)}{user2['name'][:-5]} for nothing because {gettitle(user2)}{user2['name'][:-5]} is too poor")
            token = random.randint(4, 6)
            token = round(token*user2['lvl']/userp['lvl']) if round(token*user2['lvl']/userp['lvl']) <= token else token
            attembed.description = f"**You mugged {gettitle(user2)}{user2['name'][:-5]} for nothing because {gettitle(user2)}{user2['name'][:-5]} is broke!\nBut you still earned {token} <:token:1313166204348792853>!**"
            view = interclass.Attll(ctx, logs)
            view.message = await att.edit(embed=attembed, view=view)
            await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {'token': token}})
            if user is not None:
                winembed = discord.Embed(title="Attack lost!",description=f"Someone beaten you up!\n\nThey mugged you for nothing because you are too poor",color=color.red())
                winembed.set_footer(text="take revenge noob")
                await user.send(embed=winembed)
          if userp['s'] == 40 and user is None:
            await updateset(ctx.author.id, 's', 41)
          if user is not None:
            await updateset(ctx.author.id, f'timer.user{user.id}', round(time.time())+1800)
          while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
          return
        elif view.value == '2':
          heat = 100
          deviation = 50
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
          await updateset(ctx.author.id, 'blocked', False)
          if user is not None:
            await updateset(user.id, 'blocked', False)
            await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
          rhosp = random.randint(600,1200)
          rexp = round(random.uniform(3,10),2)
          bonus = (1/(userp['lvl']/user2['lvl']))
          rexp = round(rexp*(bonus if bonus <= 2 else 2), 2)
          if functions.not_max_level(userp):
            await updateinc(ctx.author.id, 'exp', rexp)
          else:
            rexp = 0
          token = random.randint(4, 6)
          token = round(token*user2['lvl']/userp['lvl']) if round(token*user2['lvl']/userp['lvl']) <= token else token
          attembed.description = f"**You hospitalized {gettitle(user2)}{user2['name'][:-5]} for {ab(rhosp)} and gained {rexp} experience!\nYou also earned {token} <:token:1313166204348792853>!**"
          logs.append(f"{gettitle(userp)}{ctx.author.name} hospitalized {gettitle(user2)}{user2['name'][:-5]} for {ab(rhosp)}")
          view = interclass.Attll(ctx, logs)
          view.message = await att.edit(embed=attembed, view=view)
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {'token': token}})
          if user is not None:
              await updateset(user.id, 'timer.hosp', round(time.time())+rhosp)
              await updateset(user.id, 'inhosp', True)
              winembed = discord.Embed(title="Attack lost!",description=f"Someone beaten you up!\n\nThey hospitalized you for {ab(rhosp)}",color=color.red()) 
              winembed.set_footer(text="take revenge noob")
              await user.send(embed=winembed)
              await updateset(ctx.author.id, f'timer.user{user.id}', round(time.time())+1800)
          if userp['s'] == 55 and user is None:
            await updateset(ctx.author.id, 's', 56)
          while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
          return
        elif view.value == '3':
          heat = 100
          deviation = 50
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
          await updateset(ctx.author.id, 'blocked', False)
          if user is not None:
            await updateset(user.id, 'blocked', False)
            await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
          rexp = round(random.uniform(6,15),2)
          bonus = (1/(userp['lvl']/user2['lvl']))
          rexp = round(rexp*(bonus if bonus <= 2 else 2), 2)
          if functions.not_max_level(userp):
            await updateinc(ctx.author.id, 'exp', rexp)
          else:
            rexp = 0
          token = random.randint(5, 7)
          token = round(token*user2['lvl']/userp['lvl']) if round(token*user2['lvl']/userp['lvl']) <= token else token
          attembed.description = f"**You walked away after beating {gettitle(user2)}{user2['name'][:-5]} and gained {rexp} extra experience!\nYou also earned {token} <:token:1313166204348792853>!**"
          logs.append(f"{gettitle(userp)}{ctx.author.name} walked away")
          view = interclass.Attll(ctx, logs)
          view.message = await att.edit(embed=attembed, view=view)
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {'token': token}})
          if user is not None:
              winembed = discord.Embed(title="Attack lost!",description=f"Someone beaten you up!\n\nThey walked away leaving you lying on the floor",color=color.red()) 
              winembed.set_footer(text="take revenge noob")
              await user.send(embed=winembed)
              await updateset(ctx.author.id, f'timer.user{user.id}', round(time.time())+1800)
          while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
          return
      elif userhealth <= 0:
        heat = 100
        deviation = 50
        await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(userp))) ) )
        await updateset(ctx.author.id, 'blocked', False)
        if user is not None:
            await updateset(user.id, 'blocked', False)
            await updateinc(user.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user2))) ) )
        logs.append(f"{gettitle(userp)}{ctx.author.name} lost the battle against {gettitle(user2)}{user2['name'][:-5]}")
        rhosp = random.randint(120,300)
        await updateset(ctx.author.id, 'timer.hosp', round(time.time())+rhosp)
        await updateset(ctx.author.id, 'inhosp', True)
        attembed.description = f"**{gettitle(userp)}{ctx.author.mention} You lost the battle against {gettitle(user2)}{user2['name'][:-5]}! You are now in hospital for {ab(rhosp)}**"
        view = interclass.Attll(ctx, logs)
        view.message = await att.edit(embed=attembed, view=view)
        if user is not None:
            rexp = round(random.uniform(3,6),2)
            bonus = (1/(user2['lvl']/userp['lvl']))
            rexp = round(rexp*(bonus if bonus <= 2 else 2), 2)
            if functions.not_max_level(user2):
                await updateinc(user.id, 'exp', rexp)
            else:
                rexp = 0
            winembed = discord.Embed(title="Attack won!",description=f"{gettitle(userp)}{ctx.author} tried to attack you but lost!\n\nYou gained {rexp} experience!",color=color.green())
            winembed.set_footer(text="easy win")
            await user.send(embed=winembed)
        while True:
                await view.wait()
                if view.value is None:
                    return
                view = interclass.Attll(ctx, logs)
                view.message = await att.edit(view=view)
        return

async def pickpocket(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      if user['lvl'] < 10:
        await ctx.respond("You have to be at least level 10!")
        return
      chance = 0.65 + (0.65*getluck(user))
      target = random.choice(lists.picktarget)
      if random.random() <= chance:
        randomkey = round(random.random(),4)
        itemchance = lists.targetitemchance[target] + (lists.targetitemchance[target]*getluck(user))
        randomitemchance = round(random.random(),6)
        randomcash = random.randint(9, 16)
        randomcash = round(randomcash + (randomcash*user['stats']['cha']/1000) + (randomcash*dboost(user['donor'])))
        await updateinc(ctx.author.id, 'cash', round(randomcash,2))
        ppembed = discord.Embed(title="Pickpocketing",description=f"You tried to pickpocket {target} and earned <:cash:1329017495536930886> {round(randomcash)}!",color=color.green())

        if 0.005 < randomkey <= 0.05:
          if random.randint(0, 1) == 1:
            ppembed.add_field(name="Found Key!",value="You also found an Average Car Key!")
            await updateinc(ctx.author.id,'storage.Average Car Key', 1)
          else:
            ppembed.add_field(name="Found Key!",value="You also found a Garage Key!")
            await updateinc(ctx.author.id,'storage.Garage Key', 1)
        elif randomkey <= 0.005:
          ppembed.add_field(name="Found Key!",value="You also found a Luxury Car Key!")
          await updateinc(ctx.author.id,'storage.Luxury Car Key', 1)

        if randomitemchance <= itemchance:
          item = lists.targetitem[target]
          if type(item) is list:
            item = random.choice(item)
          ppembed.add_field(name="Found item!",value=f"You also found a {item} from the target!")
          await updateinc(ctx.author.id, f'storage.{item}', 1)

        ppembed.set_footer(text="good skills!")
        await ctx.respond(embed=ppembed)
      else:
        if not target == "a Hoodie guy":
          heat = 40
          deviation = 10
          await updateinc(ctx.author.id, "heat", round(heat + (deviation * random.triangular(-1, 1, -getluck(user))) ) )
          failpp = discord.Embed(title="Pickpocketing", description=f"You tried to pickpocket {target} but failed!",color=color.red())
          failpp.set_footer(text="haha")
          await ctx.respond(embed=failpp)
        else:
          randomdiechance = round(random.random(),4)
          failpp = discord.Embed(title="Pickpocketing", description=f"You tried to pickpocket {target} but failed!",color=color.red())
          if randomdiechance <= lists.targetjail[target] - (lists.targetjail[target]*getluck(user)):
            failpp.add_field(name="Whoops!",value="The Hoodie guy turns out to be a gangster! He shot you and you died")
            await self.die(ctx, ctx.author, "while pickpocketing a Hoodie guy", "You got shot in the head")
          failpp.set_footer(text="huge rip")
          await ctx.respond(embed=failpp)

async def help(self, ctx, command):
      if await self.bot.cll.find_one({"id": ctx.author.id}) is None or (await self.bot.cll.find_one({"id": ctx.author.id}))['banned']:
        return
      if command is None:
        view = interclass.Help_select(ctx, ctx.author)
        view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
        view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
        view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
        view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
        helpembed = discord.Embed(title="Help command", description="Choose a command category", color = color.blue())
        helpembed.set_footer(text="Have questions? Join our official server!")
        await ctx.respond("ㅤ",embed=helpembed, view=view)
        hembed = await ctx.interaction.original_response()
        view.message = hembed

        while True:
          await view.wait()
          if view.value is None:
            return
          command = view.value
          if command == 'main':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="Main commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Main important commands', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('MainCog').walk_commands() if command.parent is None]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
          elif command == 'city':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="City commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Explore the city', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('CityCog').walk_commands()]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
          elif command == 'crime':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="Crime commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Crimes to earn cash', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('CrimeCog').walk_commands() if command.parent is None]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
          elif command == 'car':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="Car commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Manage your cars', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('CarCog').walk_commands() if command.parent is None]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
          elif command == 'fun':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="Fun commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Fun commands when you are bored', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('FunCog').walk_commands() if command.parent is None]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
          elif command == 'other':
            view = interclass.Help_select(ctx, ctx.author)
            view.add_item(discord.ui.Button(label='Official server', url='https://discord.gg/bBeCcuwE95', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Invite me', url='https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read', style=discord.ButtonStyle.url))
            view.add_item(discord.ui.Button(label='Official website', url='https://ovbot.up.railway.app/', style=discord.ButtonStyle.url, row=2))
            view.add_item(discord.ui.Button(label='Privacy Policy', url='https://ovbot.up.railway.app/privacy-policy/', style=discord.ButtonStyle.url, row=2))
            helpembed = discord.Embed(title="Other commands", description="`/help <command>` for more information of a specific command", color = color.blue())
            helpembed.add_field(name = 'Other helpful commands', value = f"`{'`, `'.join(sorted([command.name for command in self.bot.get_cog('OtherCog').walk_commands() if command.parent is None]))}`", inline=True)
            helpembed.set_footer(text="Have questions? Join our official server!")
            view.message = await hembed.edit("ㅤ",embed=helpembed, view=view)
        return
      cmd = self.bot.get_command(command)
      if not cmd:
        cmd = self.bot.get_application_command(command)
        slash = True
      else:
        slash = False
      if not cmd:
        await ctx.respond(f"Couldn't find this command: `{command}`")
        return
      if slash is False:
        try:
          helpembed = discord.Embed(title=f"{cmd.name}", color = color.blue())
          helpembed.add_field(name = 'Description', value = f"{cmd.description}", inline=False)
          helpembed.add_field(name = 'Usage', value = f"`{cmd.usage}`", inline=False)
          helpembed.add_field(name = 'Aliases', value = f"{', '.join(cmd.aliases if cmd.aliases else ['No aliases'])}", inline=False)
          helpembed.set_footer(text="<> = Necessary | [] = Unnecessary")
          await ctx.respond(embed=helpembed)
        except:
          await ctx.respond(f"Couldn't find this command: `{command}`")
          return
      else:
        try:
          helpembed = discord.Embed(title=f"{cmd.name}", color = color.blue())
          helpembed.add_field(name = 'Description', value = f"{cmd.description}", inline=False)
          helpembed.add_field(name = 'Usage', value = f"`/{cmd.name}`", inline=False)
          helpembed.set_footer(text="<> = Necessary | [] = Unnecessary")
          await ctx.respond(embed=helpembed)
        except:
          await ctx.respond(f"Couldn't find this command: `{command}`")
          return

async def profile(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        return
      user = user or ctx.author
      if await finduser(user.id) == None:
        await ctx.respond("The user haven't started playing OV Bot yet")
        return
      userp = await finduser(user.id)

      if userp['s'] == 38:
        await updateset(ctx.author.id, 's', 39)

      byte = functions.charimg(userp)
      file = discord.File(fp=byte,filename="character.png")

      desc = []
      if userp['inhosp'] == True:
        desc.append(f"**In Hospital for {ab(userp['timer']['hosp']-round(time.time()))}**")
      if userp['injail'] == True:
        desc.append(f"**In Jail for {ab(userp['timer']['jail']-round(time.time()))}**")

      if userp['donor'] == 0:
        desc.append(f"**Not a [Royal member](https://ovbot.up.railway.app/)**")
      elif userp['donor'] == 1:
        desc.append(f"**<:royal:1328385115503591526> [Royal Member](https://ovbot.up.railway.app/) for {ab(userp['timer']['donate']-round(time.time()))}**")
      elif userp['donor'] == 2:
        desc.append(f"**<:royal_plus:1328385118347464804> [Royal+ Member](https://ovbot.up.railway.app/) for {ab(userp['timer']['donate']-round(time.time()))}**")

      pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s character", description=discord.Embed.Empty if desc == [] else "\n".join(desc), color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
      pembed.set_image(url="attachment://character.png")
      pembed.set_footer(text = "Very cool user")

      view = interclass.Profile_select(ctx, ctx.author)

      await ctx.respond( file=file, embed=pembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      dispatcher = {"travel": "Travelled", "hosp": "Hospitalized", "jail": "Jailed", "fuel": "Car speed boost", "beer": "Drunk", "cashboost": "Cash boost", "cboost": "Luck boost", "warns": "Warn removal", "blocked": "Temporary blocked", "shield": "Immunity", "daily": "Next daily", "Weekly": "Next weekly", "donate": "Royal", "larceny": "Robbed!"}

      while True:
        await view.wait()
        userp = await finduser(user.id)

        if view.value is None:
          return
        elif view.value == "character":
          view = interclass.Profile_select(ctx, ctx.author)

          byte = functions.charimg(userp)
          file = discord.File(fp=byte,filename="character.png")

          desc = []
          if userp['inhosp'] == True:
            desc.append(f"**In Hospital for {ab(userp['timer']['hosp']-round(time.time()))}**")
          if userp['injail'] == True:
            desc.append(f"**In Jail for {ab(userp['timer']['jail']-round(time.time()))}**")

          if userp['donor'] == 0:
            desc.append(f"**Not a [Royal Member](https://ovbot.up.railway.app/)**")
          elif userp['donor'] == 1:
            desc.append(f"**<:royal:1328385115503591526> [Royal Member](https://ovbot.up.railway.app/) {ab(userp['timer']['donate']-round(time.time()))} left**")
          elif userp['donor'] == 2:
            desc.append(f"**<:royal_plus:1328385118347464804> [Royal+ Member](https://ovbot.up.railway.app/) {ab(userp['timer']['donate']-round(time.time()))} left**")

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s character", description=discord.Embed.Empty if desc == [] else "\n".join(desc), color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          pembed.set_image(url="attachment://character.png")
          pembed.set_footer(text = "Very cool user")
          
          view.message = await msg.edit(file=file, attachments=[], embed=pembed, view=view)
        elif view.value == "location":
          view = interclass.Profile_select(ctx, ctx.author)

          img = Image.open(r"images/map.png").convert('RGBA')

          img2 = Image.open(r"images/pointer.png").convert('RGBA')

          img.paste(img2, lists.locationcoords[userp['location']], img2)

          byte = BytesIO()

          img.save(byte, format="png")
          byte.seek(0)

          file = discord.File(fp=byte,filename="pic.png")
          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s location", description=f"**{userp['location']}**", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          pembed.set_image(url="attachment://pic.png")
          pembed.set_footer(text = "Very cool user")

          view.message = await msg.edit(file=file, attachments=[], embed=pembed, view=view)
        elif view.value == "level":
          view = interclass.Profile_select(ctx, ctx.author)

          colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
          firstcolor = random.choice(colors)
          colors.remove(firstcolor)

          img = Image.new("RGBA", (212, 21))

          pen = ImageDraw.Draw(img)
          pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
          pen.rounded_rectangle(((0, 0), (round((userp['exp']-(userp['lvl']*100))*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

          byte = BytesIO()

          img.save(byte, format="png")
          byte.seek(0)

          file = discord.File(fp=byte,filename="pic.png")

          maxed = "(Maxed)"
          if functions.not_max_level(userp):
            maxed = ""

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s level", description=f"**Level** {userp['lvl']} {maxed}\n**Experience** {aa(round(userp['exp'],2))} / {aa(round(((userp['lvl'] * 100) + 100)))}", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          pembed.set_image(url="attachment://pic.png")
          pembed.set_footer(text="Very cool user")

          view.message = await msg.edit(file=file, attachments=[], embed=pembed, view=view)

        elif view.value == "balance":
          view = interclass.Profile_select(ctx, ctx.author)

          colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]

          img = Image.new("RGBA", (212, 21))

          pen = ImageDraw.Draw(img)
          pen.rounded_rectangle(((0, 0), (200, 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

          mask = Image.new("L", (212, 21), "black")
          maskpen = ImageDraw.Draw(mask)
          width = round(userp['stash']/userp['stashc']*100*2) if userp['stashc'] != 0 else 0
          maskpen.rounded_rectangle(((0, 0), (width, 20)), fill="white", radius=9)

          img1 = Image.open(r"images/coins.png").convert("RGBA")
          pen1 = ImageDraw.Draw(img1)
          pen1.rounded_rectangle(((0, 0), (width, 20)), outline="black", width=2, radius=9)

          img.paste(img1, (0, 0), mask)

          byte = BytesIO()

          img.save(byte, format="png")
          byte.seek(0)

          file = discord.File(fp=byte,filename="pic.png")

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s balance", description=f"**Cash** <:cash:1329017495536930886> {aa(round(userp['cash']))}\n**Stash** <:cash:1329017495536930886> {aa(round(userp['stash']))} / {aa(round(userp['stashc']))}", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          if userp['token'] != 0:
            pembed.description += f"\n**Token** {userp['token']} <:token:1313166204348792853>"
          pembed.set_image(url="attachment://pic.png")
          pembed.set_footer(text="Very cool user")
          view.message = await msg.edit(file=file, attachments=[], embed=pembed, view=view)

        elif view.value == "car":
          view = interclass.Profile_select(ctx, ctx.author)

          if userp['drive'] != "":
            car = getdrive(userp)
            carname = getdrive(userp, "name")
            rawcarname = getdrive(userp, "rawname")
            cartuned = car['tuned']
            if rawcarname in lists.lowcar:
              rank = "Low"
            elif rawcarname in lists.averagecar:
              rank = "Average"
            elif rawcarname in lists.highcar:
              rank = "High"
            elif rawcarname in lists.exoticcar:
              rank = "Exotic"
            elif rawcarname in lists.classiccar:
              rank = "Classic"
            elif rawcarname in lists.exclusivecar:
              rank = "Exclusive"
            else:
              rank = "Unknown"

            if car['golden'] == True:
              carprice = lists.carprice[rawcarname]*2
              carspeed = car['speed']
              pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s car", description=f"**{carname}**\n{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {carprice}\n**Speed** {carspeed} MPH\n**Tuned** {cartuned}\n**Overall Rating** {round(((carspeed/1.015**cartuned)-lists.carspeed[carname]+10)/2, 2)}/10",color=color.random())
              if not rawcarname in lists.goldencars:
                byte = functions.goldfilter(lists.carimage[rawcarname])
                file = discord.File(fp=byte,filename="pic.jpg")
                pembed.set_image(url="attachment://pic.jpg")
              else:
                pembed.set_image(url=lists.goldencarimage[rawcarname])
            else:
              carprice = lists.carprice[rawcarname]
              carspeed = car['speed']
              pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s car", description=f"**{carname}**\n{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {carprice}\n**Speed** {carspeed} MPH\n**Tuned** {cartuned}\n**Overall Rating** {round(((carspeed/1.015**cartuned)-lists.carspeed[carname]+10)/2, 2)}/10",color=color.random())
              pembed.set_image(url=lists.carimage[rawcarname])
            
            pembed.set_footer(text="noob car")

            if car['golden'] == True and not rawcarname in lists.goldencars:
              view.message = await msg.edit(attachments=[], file=file, embed=pembed, view=view)
            else:
              view.message = await msg.edit(attachments=[], embed=pembed, view=view)
          else:
            pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s car", description="Not driving anything", color=color.random()).set_footer(text="poor guy")
            view.message = await msg.edit(attachments=[], embed=pembed, view=view)

        # elif view.value == "energy":
        #   view = interclass.Profile_select(ctx, ctx.author)

        #   colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
        #   firstcolor = random.choice(colors)
        #   colors.remove(firstcolor)

        #   img = Image.new("RGBA", (212, 21))

        #   maxenergy = round(userp['energy']/userp['energyc']*100*2) if round(userp['energy']/userp['energyc']*100*2) <= 200 else 200

        #   pen = ImageDraw.Draw(img)
        #   pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
        #   pen.rounded_rectangle(((0, 0), (maxenergy, 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

        #   byte = BytesIO()

        #   img.save(byte, format="png")
        #   byte.seek(0)

        #   file = discord.File(fp=byte,filename="pic.png")

        #   pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s energy", description=f"\U000026a1 {userp['energy']} / {userp['energyc']} **({userp['epm']}/min)**", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
        #   pembed.set_image(url="attachment://pic.png")
        #   pembed.set_footer(text="Very cool user")

        #   view.message = await msg.edit(file=file, attachments=[], embed=pembed, view=view)

        elif view.value == "stats":
          view = interclass.Profile_select(ctx, ctx.author)

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s statistics", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          pembed.add_field(name="**STR <:dumbbell:905773708369612811>**", value=f"{round(userp['stats']['str'],2)}", inline=True)
          pembed.add_field(name="**DEF <:shield:905782766673743922>**", value=f"{round(userp['stats']['def'],2)}", inline=True)
          pembed.add_field(name="**SPD <:speed:905800074955739147>**", value=f"{round(userp['stats']['spd'],2)}", inline=True)
          pembed.add_field(name="**DEX <:dodge1:905801069857218622>**", value=f"{round(userp['stats']['dex'],2)}", inline=True)
          if userp['stats']['int'] != 0:
            pembed.add_field(name="**INT <:intelligence:940955425443024896>**", value=f"{round(userp['stats']['int'])}", inline=True)
          if userp['stats']['luk'] != 0:
            luck = round(getluck(userp)*1000)
            boostp = 0
            boosta = 0
            if userp['drugs']['cannabis'] > 0:
              boostp += userp['drugs']['cannabis']
            if userp['donor'] == 2:
              boostp += 50
            elif userp['donor'] == 1:
             boostp += 20

            if "Lucky Clover" in userp['storage']:
              boostp += userp['storage']['Lucky Clover']

            if 'cboost' in userp['timer']:
              boosta += 50

            b = ''
            if boosta != 0 and boostp == 0:
              b = f" (Boost: +{boosta})"
            elif boosta == 0 and boostp != 0:
              b = f" (Boost: +{boostp}%)"
            elif boosta != 0 and boostp != 0:
              b = f" (Boost: +{boosta} & +{boostp}%)"

            pembed.add_field(name="**LUK <:luck:940955425308823582>**", value=f"{luck}{b}", inline=True)
          if userp['stats']['cha'] != 0:
            charisma = round(getcha(userp)*1000)
            boostp = 0
            if userp['drugs']['ecstasy'] > 0:
              boostp += (userp['drugs']['ecstasy'] * 5)

            if userp['donor'] == 2:
              boostp += 100
            elif userp['donor'] == 1:
              boostp += 50

            b = ''
            if boostp != 0:
              b = f" (Boost: +{boostp}%)"

            pembed.add_field(name="**CHA <:charisma:940955424910356491>**", value=f"{charisma}{b}", inline=True)
          if userp['stats']['acc'] != 0:
            pembed.add_field(name="**ACC <:accelerating:942699703835979797>**", value=f"{round(userp['stats']['acc'])}", inline=True)
          if userp['stats']['dri'] != 0:
            pembed.add_field(name="**DRI <:drifting:942700424820047903>**", value=f"{round(userp['stats']['dri'])}", inline=True)
          if userp['stats']['han'] != 0:
            pembed.add_field(name="**HAN <:handling:942699703789830164>**", value=f"{round(userp['stats']['han'])}", inline=True)
          if userp['stats']['bra'] != 0:
            pembed.add_field(name="**BRK <:braking:942699703492030475>**", value=f"{round(userp['stats']['bra'])}", inline=True)

          pembed.set_footer(text="Very cool user")

          view.message = await msg.edit(attachments=[], embed=pembed, view=view)

        elif view.value == "timers":
          view = interclass.Profile_select(ctx, ctx.author)
          timers = []
          for timer in userp['timer']:
            try:
              timers.append(f"**{dispatcher[timer]}** {ab(userp['timer'][timer]-round(time.time()))}")
            except:
              continue

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s timers", description="\n".join(timers) if timers != [] else "No timers", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          pembed.set_footer(text="Very cool user")

          view.message = await msg.edit(attachments=[], embed=pembed, view=view)

        elif view.value == "status":
          view = interclass.Profile_select(ctx, ctx.author)

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s status", description=f"**Job** {userp['job'] if userp['job'] != '' else 'Unemployed'}", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          if userp['property'] != '':
            pembed.description += f"\n**Property** {lists.propertyname[userp['property']]}"
          if userp['equipments']['weapon'] != '':
            pembed.description += f"\n**Weapon** {userp['equipments']['weapon']}"
          if userp['drive'] != '':
            pembed.description += f"\n**Driving** {getdrive(userp, 'name')}"
          if userp['heat'] != 0:
            pembed.description += f"\n**Heat** {userp['heat']}/1000"
          pembed.set_footer(text="Very cool user")

          view.message = await msg.edit(attachments=[], embed=pembed, view=view)
        elif view.value == "others":
          view = interclass.Profile_select(ctx, ctx.author)

          pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s other information", description=f"**Reputation** {userp['rep']}", color=color.random()).set_author(name=user, icon_url=user.display_avatar.url)
          if userp['business'] != 0:
            pembed.description += f"\n**Business gains** <:cash:1329017495536930886> {userp['business']/100}/min"
          if sum(list(userp['storage'].values())) != 0:
            pembed.description += f"\n**Items In Storage** {sum(list(userp['storage'].values()))}"
          if len(userp['garage']) != 0:
            pembed.description += f"\n**Cars Owned** {len(userp['garage'])}/{userp['garagec']}"
          pembed.set_footer(text="Very cool user")

          view.message = await msg.edit(attachments=[], embed=pembed, view=view)
        elif view.value == "overall":
          view = interclass.Profile_select(ctx, ctx.author)
          
          maxed = "(Maxed)"
          if functions.not_max_level(userp):
            maxed = ""

          desc = []
          if userp['inhosp'] == True:
            desc.append(f"**In Hospital for {ab(userp['timer']['hosp']-round(time.time()))}**")
          if userp['injail'] == True:
            desc.append(f"**In Jail for {ab(userp['timer']['jail']-round(time.time()))}**")

          if userp['donor'] == 0:
            desc.append(f"**Not a [Royal Member](https://ovbot.up.railway.app/)**")
          elif userp['donor'] == 1:
            desc.append(f"**<:royal:1328385115503591526> [Royal Member](https://ovbot.up.railway.app/) {ab(userp['timer']['donate']-round(time.time()))} left**")
          elif userp['donor'] == 2:
            desc.append(f"**<:royal_plus:1328385118347464804> [Royal+ Member](https://ovbot.up.railway.app/) {ab(userp['timer']['donate']-round(time.time()))} left**")

          pembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s profile", description=discord.Embed.Empty if desc == [] else "\n".join(desc) + f"\n**Location** {userp['location']}", color = color.random())
          pembed.add_field(name = "Level", value = f"**Level** {userp['lvl']} {maxed}\n**Experience**\n{round(userp['exp'],2)} / {round(((userp['lvl'] * 100) + 100))}", inline = True)
          pembed.add_field(name = "Balance", value = f"**Cash** <:cash:1329017495536930886> {aa(round(userp['cash'],2))}\n**Stash** <:cash:1329017495536930886> {aa(round(userp['stash']))} / {aa(round(userp['stashc']))}", inline = True)
          if userp['token'] != 0:
            pembed.fields[1].value += f"\n**Token** {userp['token']} <:token:1313166204348792853>"
          # pembed.add_field(name = "Energy", value = f"\U000026a1 {userp['energy']} / {userp['energyc']} **({userp['epm']}/min)**", inline = True)
          pembed.add_field(name = "Statistics", value = f"**STR <:dumbbell:905773708369612811>** {round(userp['stats']['str'],2)}\n**DEF <:shield:905782766673743922>** {round(userp['stats']['def'],2)}\n**SPD <:speed:905800074955739147>** {round(userp['stats']['spd'],2)}\n**DEX <:dodge1:905801069857218622>** {round(userp['stats']['dex'],2)}", inline = True)
          if userp['stats']['int'] != 0:
            pembed.fields[2].value += f"\n**INT <:intelligence:940955425443024896>** {round(userp['stats']['int'])}"
          if userp['stats']['luk'] != 0:
            luck = round(getluck(userp)*1000)
            boostp = 0
            boosta = 0
            if userp['drugs']['cannabis'] > 0:
              boostp += userp['drugs']['cannabis']
            if userp['donor'] == 2:
              boostp += 50
            elif userp['donor'] == 1:
             boostp += 20

            if "Lucky Clover" in userp['storage']:
              boostp += userp['storage']['Lucky Clover']

            if 'cboost' in userp['timer']:
              boosta += 50

            b = ''
            if boosta != 0 and boostp == 0:
              b = f" (Boost: +{boosta})"
            elif boosta == 0 and boostp != 0:
              b = f" (Boost: +{boostp}%)"
            elif boosta != 0 and boostp != 0:
              b = f" (Boost: +{boosta} & +{boostp}%)"

            pembed.fields[2].value += f"\n**LUK <:luck:940955425308823582>** {luck}{b}"
          if userp['stats']['cha'] != 0:
            charisma = round(getcha(userp)*1000)
            boostp = 0
            if userp['drugs']['ecstasy'] > 0:
              boostp += (userp['drugs']['ecstasy'] * 5)

            if userp['donor'] == 2:
              boostp += 100
            elif userp['donor'] == 1:
              boostp += 50

            b = ''
            if boostp != 0:
              b = f" (Boost: +{boostp}%)"

            pembed.fields[2].value += f"\n**CHA <:charisma:940955424910356491>** {charisma}{b}"
          if userp['stats']['acc'] != 0:
            pembed.fields[2].value += f"\n**ACC <:accelerating:942699703835979797>** {round(userp['stats']['acc'])}"
          if userp['stats']['dri'] != 0:
            pembed.fields[2].value += f"\n**DRI <:drifting:942700424820047903>** {round(userp['stats']['dri'])}"
          if userp['stats']['han'] != 0:
            pembed.fields[2].value += f"\n**HAN <:handling:942699703789830164>** {round(userp['stats']['han'])}"
          if userp['stats']['bra'] != 0:
            pembed.fields[2].value += f"\n**BRK <:braking:942699703492030475>** {round(userp['stats']['bra'])}"
          pembed.add_field(name = "Status", value = f"**Current Job** {userp['job'] if userp['job'] != '' else 'Unemployed'}", inline = True)
          if userp['property'] != '':
            pembed.fields[3].value += f"\n**Property** {lists.propertyname[userp['property']]}"
          if userp['equipments']['weapon'] != '':
            pembed.fields[3].value += f"\n**Weapon** {userp['equipments']['weapon']}"
          if userp['drive'] != '':
            pembed.fields[3].value += f"\n**Driving** {getdrive(userp, 'name')}"
          if userp['heat'] != 0:
            pembed.fields[3].value += f"\n**Heat** {userp['heat']}/1000"
          pembed.add_field(name = "Others", value = f"**Reputation** {userp['rep']}", inline = True)
          if userp['business'] != 0:
            pembed.fields[4].value += f"\n**Business gains** <:cash:1329017495536930886> {userp['business']/100}/min"
          if sum(list(userp['storage'].values())) != 0:
            pembed.fields[4].value += f"\n**Items In Storage** {sum(list(userp['storage'].values()))}"
          if len(userp['garage']) != 0:
            pembed.fields[4].value += f"\n**Cars Owned** {len(userp['garage'])}/{userp['garagec']}"
          pembed.set_thumbnail(url = user.display_avatar.url)
          pembed.set_footer(text = "Very cool person")

          view.message = await msg.edit(attachments=[], embed=pembed, view=view)

async def storage(self, ctx, page, user):
      if await blocked(ctx.author.id) == False:
        return
      if user == None:
        user = ctx.author
      if await finduser(user.id) == None:
        await ctx.respond("The user haven't started playing OV Bot yet")
        return
      if page == None:
        page = 1
      try:
        page = int(page)
      except:
        try:
          user = await commands.MemberConverter().convert(ctx, page)
          page = 1
        except:
          await ctx.respond("To use the storage command type `/storage [page] [user]`")
          return
      userp = await finduser(user.id)
      useritemcount = len(userp['storage'])
      userstorage = userp['storage']
      itemlist = sorted(list(userstorage))
      maxpage = math.ceil(useritemcount/5)

      if useritemcount == 0:
        maxpage = 1

      if page > maxpage and user == ctx.author:
        await ctx.respond(f"Your storage only has {maxpage} pages")
        return
      elif page == 0:
        await ctx.respond("Why are there weirdos like you")
        return
      elif page < 0:
        await ctx.respond("There are no negative pages, go to school")
        return
      elif page > maxpage and not user == ctx.author:
        await ctx.respond(f"The user's storage only has {maxpage} pages")
        return

      if userp['s'] == 34:
        await updateset(ctx.author.id, 's', 35)

      stoembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s storage", description = "**Your items**", color = color.random()).set_footer(text = f"Page {page} of {maxpage}")

      if useritemcount == 0:
        stoembed.add_field(name = "You have nothing to look here", value = "poor guy so poor", inline = False)
        await ctx.respond(embed=stoembed)
        return

      for item in itemlist[(page-1)*5:(page-1)*5+5]:
        stoembed.add_field(name = f"**{item}** (x{userstorage[item]})", value = f"ID | `{lists.item_id[item]}`", inline = False)

      view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
      await ctx.respond(embed=stoembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1

        stoembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s storage", description = "**Your items**", color = color.random()).set_footer(text = f"Page {page} of {maxpage}")

        for item in itemlist[(page-1)*5:(page-1)*5+5]:
          stoembed.add_field(name = f"**{item}** (x{userstorage[item]})", value = f"ID | `{lists.item_id[item]}`", inline = False)

        view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
        view.message = await msg.edit(embed=stoembed, view=view)

async def cash(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        return
      if user == None:
        user = ctx.author

      userp = await finduser(user.id)
      if userp is None:
        await ctx.respond("This user haven't started playing")
        return
      if userp['s'] == 20:
        await updateset(ctx.author.id, 's', 21)
      try:
        await updateset(user.id, 'stashc', (userp['property']*100)+(userp['storage']['Safe']*500))
      except:
        await updateset(user.id, 'stashc', userp['property']*100)
        pass
      userp = await finduser(user.id)

      colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]

      img = Image.new("RGBA", (212, 21))

      pen = ImageDraw.Draw(img)
      pen.rounded_rectangle(((0, 0), (200, 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

      mask = Image.new("L", (212, 21), "black")
      maskpen = ImageDraw.Draw(mask)
      width = round(userp['stash']/userp['stashc']*100*2) if userp['stashc'] != 0 else 0
      maskpen.rounded_rectangle(((0, 0), (width, 20)), fill="white", radius=9)

      img1 = Image.open(r"images/coins.png").convert("RGBA")
      pen1 = ImageDraw.Draw(img1)
      pen1.rounded_rectangle(((0, 0), (width, 20)), outline="black", width=2, radius=9)

      img.paste(img1, (0, 0), mask)

      byte = BytesIO()

      img.save(byte, format="png")
      byte.seek(0)

      file = discord.File(fp=byte,filename="pic.png")

      cashembed = discord.Embed(title = gettitle(userp) + user.name + "'s cash", description = f"**Cash** <:cash:1329017495536930886> {aa(round(userp['cash']))}\n**Stash** <:cash:1329017495536930886> {aa(round(userp['stash']))} / {aa(userp['stashc'])}\n**Token** {userp['token']} <:token:1313166204348792853>", color = color.random())
      cashembed.set_image(url="attachment://pic.png")
      cashembed.set_footer(text="poor")

      if userp['cash'] < 100:
        cashembed.set_footer(text = "broke broke")
      elif userp['cash'] >= 100 and userp['cash'] < 1000:
        cashembed.set_footer(text = "poor tramp")
      elif userp['cash'] >= 1000 and userp['cash'] < 10000:
        cashembed.set_footer(text = "dead end")
      elif userp['cash'] >= 10000 and userp['cash'] < 50000:
        cashembed.set_footer(text = "average homie")
      elif userp['cash'] >= 50000 and userp['cash'] < 100000:
        cashembed.set_footer(text = "business man")
      elif userp['cash'] >= 100000 and userp['cash'] < 500000:
        cashembed.set_footer(text = "rich homie")
      elif userp['cash'] >= 500000 and userp['cash'] < 1000000:
        cashembed.set_footer(text = "rich homie")
      elif userp['cash'] >= 1000000 and userp['cash'] < 5000000:
        cashembed.set_footer(text = "millionaire")
      elif userp['cash'] >= 5000000:
        cashembed.set_footer(text = "high roller")

      await ctx.respond(file=file, embed=cashembed)

async def deposit(self, ctx, amount):
      if await blocked(ctx.author.id) == False:
        return
      if amount == None:
        await ctx.respond("Type how much do you want to deposit")
        return
      user = await finduser(ctx.author.id)
      usercash = user['cash']
      if usercash == 0:
        await ctx.respond("You don't have any cash to deposit sadly")
        return
      if 'racing' in list(user) and user['racing']:
        await ctx.respond("You are currently racing! You cannot deposit any cash")
        return
      userstash = user['stash']
      userstashc = user['stashc']
      userstash = round(userstash)
      userstashc = round(userstashc)
      if round(userstashc - userstash) == 0:
        await ctx.respond("Your stash is already full!")
        return
      try:
        int(amount)
      except:
        if amount.strip() == "max" or amount.strip() == "all":
          amount = usercash
      try:
        amount = int(amount)
      except:
        await ctx.respond("Enter a valid amount of cash you want to deposit!")
        return
      amount = ac(amount)
      amount = round(amount)
      if amount < 1:
        await ctx.respond("Give a valid number of cash you have")
        return
      if amount > usercash:
        await ctx.respond("You don't even have that much cash poor guy")
        return
      if amount > round(userstashc - userstash):
        amount = round(userstashc - userstash)
      await updateinc(ctx.author.id, 'cash', -amount)
      await updateinc(ctx.author.id, 'stash', amount)
      await ctx.respond(f"You deposited <:cash:1329017495536930886> {aa(round(amount))} in your stash! You now have <:cash:1329017495536930886> {aa(round(usercash - amount))} cash left and <:cash:1329017495536930886> {aa(round(userstash + amount))} in your stash")

async def withdraw(self, ctx, amount):
      if await finduser(ctx.author.id) == None:
        return
      if await userbanned(ctx.author.id) == True:
        return
      user = await finduser(ctx.author.id)
      userinjail = user['injail']
      if userinjail == True:
        return
      if amount == None:
        await ctx.respond("Type how much do you want to withdraw")
        return
      userstash = user['stash']
      if userstash == 0:
        await ctx.respond("You don't have any cash to withdraw sadly")
        return
      try:
        int(amount)
      except:
        if amount.strip() == "max" or amount.strip() == "all":
          amount = user['stash']
      try:
        amount = int(amount)
      except:
        await ctx.respond("Enter a valid amount of cash you want to withdraw!")
        return
      amount = ac(amount)
      amount = round(amount)
      if amount < 1:
        await ctx.respond("Give a valid number of cash you have in your stash")
        return
      if amount > userstash:
        await ctx.respond("You don't even have that much cash in your stash poor guy")
        return
      await updateinc(ctx.author.id, 'stash', -amount)
      await updateinc(ctx.author.id, 'cash', amount)
      await ctx.respond(f"You withdrew <:cash:1329017495536930886> {aa(round(amount))} from your stash! You have <:cash:1329017495536930886> {aa(round(userstash - amount))} left in your stash")

async def givecash(self, ctx, amount, user, reason):
      if await blocked(ctx.author.id) == False:
        return
      if amount == None:
        await ctx.respond("You have to give an amount to transfer!")
        return
      try:
        amount = ac(amount)
      except:
        pass
      userp = await finduser(ctx.author.id)
      userpcash = userp['cash']
      if userpcash == 0:
        await ctx.respond("You don't even have cash to transfer noob")
        return
      if 'racing' in list(userp) and userp['racing']:
        await ctx.respond("You are currently racing! You cannot give any cash")
        return
      try:
        int(amount)
      except:
        if amount.strip() == "max" or amount.strip() == "all":
          amount = userpcash
      try:
        amount = int(amount)
      except:
        await ctx.respond("Enter a valid amount of cash you want to transfer!")
        return
      if amount < 1:
        await ctx.respond("You must give a valid amount!")
        return
      if user == ctx.author:
        await ctx.respond("Why are you giving cash to youself?")
        return
      if user == None:
        await ctx.respond("Who do you want to transfer the cash?")
        return
      if await finduser(user.id) == None:
        await ctx.respond("This user haven't started playing OV Bot yet!")
        return
      userdonor = userp['donor']
      if amount > userpcash:
        await ctx.respond("You don't even have that much cash liar")
        return
      if reason is not None and len(reason) > 1000:
        await ctx.respond("Reason cannot be more than 1000 words!")
        return
      user2 = await finduser(user.id)
      if ctx.guild.id in user2['q']:
          await ctx.respond("The user quarantined themself, how lonely")
          return
      if userp['location'] != user2['location']:
        await ctx.respond("You need to be in the same city as the user to send cash!")
        return
      amountbeforetax = amount
      if userdonor < 1:
        tax = round(amount*0.05)
        amount -= tax
        await updateinc(ctx.author.id, 'cash', -amountbeforetax)
        await updateinc(user.id,'cash',amount)
      else:
        await updateinc(ctx.author.id, 'cash', -amountbeforetax)
        await updateinc(user.id,'cash',amountbeforetax)
      if userdonor < 1:
        await ctx.respond(f"You transferred <:cash:1329017495536930886> {aa(amount)} to {gettitle(user2)}{user} after a 5% tax!")
        recembed = discord.Embed(title="Cash received",description=f"{gettitle(userp)}{ctx.author} sent you <:cash:1329017495536930886> {aa(amount)} after a 5% tax!" + ("" if reason is None else f"\n\n**Reason** {reason}"),color=color.green())
        recembed.set_footer(text="easy cash")
        await user.send(embed=recembed)
      else:
        await ctx.respond(f"You transferred <:cash:1329017495536930886> {aa(amountbeforetax)} to {gettitle(user2)}{user}! Because you are a Royal+ Member, you don't need to pay tax")
        recembed = discord.Embed(title="Cash received",description=f"{gettitle(userp)}{ctx.author} sent you <:cash:1329017495536930886> {aa(amountbeforetax)}!" + ("" if reason is None else f"\n\n**Reason** {reason}"),color=color.green())
        recembed.set_footer(text="easy cash")
        await user.send(embed=recembed)

async def giveitem(self, ctx, amount, item, user, reason):
      if await blocked(ctx.author.id) == False:
        return
      if user == ctx.author:
        await ctx.respond("You can't give item to yourself use common sense")
        return
      if amount is None:
        amount = 1
      try:
        amount = int(amount)
      except:
        if not amount == "max" or not amount == "all":
          await ctx.respond("To give someone item `/give <amount> <item> <user>`")
          return
      if item == None:
        await ctx.respond("What item are you giving?")
        return
      if user == None:
        await ctx.respond("Who do you want to give your item?")
        return
      user2 = await finduser(user.id)
      if user2 is None:
        await ctx.respond("Cannot find the user")
        return
      if ctx.guild.id in user2['q']:
        await ctx.respond("The user quarantined themself, how lonely")
        return
      if reason is not None and len(reason) > 1000:
        await ctx.respond("Reason cannot be more than 1000 words!")
        return
      userp = await finduser(ctx.author.id)
      if userp['location'] != user2['location']:
        await ctx.respond("You need to be in the same city as the user to send items!")
        return
      userstorage = userp['storage']
      item = item.lower()
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in list(userp['storage']) if item == x.lower() or item == x.lower().replace(" ","")]
        if len(closematch) == 0:
          closematch = [x for x in list(userp['storage']) if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond("You don't have this item in your storage")
        return

      if item in lists.drug:
        await ctx.respond("You cannot give drugs to other users")
        return

      if amount == "max" or amount == "all":
        amount = userstorage[item]

      if amount <= 0:
        await ctx.respond("Give a valid amount!")
        return
      userstorageitemq = userstorage[item]
      if amount > userstorageitemq:
        await ctx.respond("You don't have that much item in your storage!")
        return
      await updateinc(user.id, f'storage.{item}', amount)
      await updateinc(ctx.author.id, f'storage.{item}', -amount)
      userstorageitemq = userstorage[item] - amount
      if userstorageitemq == 0:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.{item}': 1}})
      recembed = discord.Embed(title="Item received",description=f"{gettitle(userp)}{ctx.author} sent you {amount} {item}!" + ("" if reason is None else f"\n\n**Reason** {reason}"),color=color.green())
      recembed.set_footer(text="cool")
      
      await ctx.respond(f"You sent {gettitle(user2)}{user} {amount} {item}!")
      await user.send(embed=recembed)

async def use(self, ctx, item, amount):
      if await finduser(ctx.author.id) == None:
        return
      if await userbanned(ctx.author.id) == True:
        return
      if item is None:
        await ctx.respond("What item do you want to use?")
        return
      try:
        item = item.lower()
      except:
        pass
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          ctx.command.reset_cooldown(ctx)
          return
        closematch = [x for x in lists.allitem if item == x.lower()] 
        if closematch == []:
          closematch = [x for x in lists.allitem if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          ctx.command.reset_cooldown(ctx)
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond(f"Cannot find this item '{item}', check if you spelled it correctly!")
        ctx.command.reset_cooldown(ctx)
        return
      if item in lists.weapon:
        await ctx.respond("You cannot use weapons, equip them by typing `/equip <weapon>` instead!")
        ctx.command.reset_cooldown(ctx)
        return
      if item not in lists.usables and item not in lists.foods:
        await ctx.respond("This item is not usable!")
        return
      if item in lists.foods:
        await ctx.respond("Energy feature has been removed! Wait for further updates...")
        # await functions.food(item, ctx, amount)
        return
      item = item.lower().replace(" ", "_")
      func = functions.dispatcher[item]
      cash = await func(ctx, amount)
      if cash is not None:
        await updateinc(ctx.author.id, "cash", cash)

async def item(self, ctx, item):
      if await blocked(ctx.author.id) == False:
        return
      if item == None:
        await ctx.respond("What item information do you wanna see?")
        return
      try:
        item = item.lower()
      except:
        pass
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in lists.allitem if item == x.lower() or item == x.lower().replace(" ","")]
        if closematch == []:
          closematch = [x for x in lists.allitem if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond(f"Cannot find this item '{item}', check if you spelled it correctly!")
        return
      try:
        if item in lists.titem:
          raise
        itemprice = aa(lists.item_prices[item])
        if item in lists.bitem and not item in lists.drug:
          itemprice = aa(round(lists.item_prices[item]/2))
        itemprice = "<:cash:1329017495536930886> " + str(itemprice)
      except:
        itemprice = "Cannot be sold"
      user = await finduser(ctx.author.id)
      userstorage = user['storage']
      try:
        itemowned = userstorage[item]
      except:
        itemowned = 0
      itemembed = discord.Embed(title=item,description=(lists.item_description[item] + "\nEdible") if item in lists.foods else lists.item_description[item],color=color.blue())
      itemembed.add_field(name="Information",value=f"**Item ID:** `{lists.item_id[item]}`\n**Price:** {itemprice}\n**Owned:** {itemowned}")
      itemembed.set_footer(text="cheap item")

      if os.path.exists(f"images/{item.lower().replace(' ', '_')}_icon.png"):
        file = discord.File(f"images/{item.lower().replace(' ', '_')}_icon.png")
        itemembed.set_thumbnail(url=f"attachment://{item.lower().replace(' ', '_')}_icon.png")
        await ctx.respond(embed=itemembed, file=file)
      elif os.path.exists(f"images/{item.lower().replace(' ', '_')}.png"):
        file = discord.File(f"images/{item.lower().replace(' ', '_')}.png")
        itemembed.set_thumbnail(url=f"attachment://{item.lower().replace(' ', '_')}.png")
        await ctx.respond(embed=itemembed, file=file)
      else:
        await ctx.respond(embed=itemembed)

async def equip(self, ctx, item):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if item == None:
        await ctx.respond("What do you wanna equip? If you wanna unequip something type `/unequip <item>`")
        return
      userstorage = user['storage']
      userstoragelist = sorted(list(userstorage))
      try:
        item = item.lower()
      except:
        pass
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in lists.allitem if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond(f"Cannot find this item `{item}`, check if you spelled it correctly!")
        return

      if closematch in [user['equipments'][equipment] for equipment in user['equipments'] if equipment != ""]:
        await ctx.respond(f"You are already equipping {closematch}")
        return
      elif item not in lists.weapon and item not in lists.wearables and item not in lists.melee:
        await ctx.respond("You can't even equip this item")
      elif item not in userstoragelist:
        await ctx.respond("You don't even have this item, don't lie to me")
      elif (item in lists.weapon or item in lists.wearables or item in lists.melee) and item in userstoragelist:
        dispatcher = {"weapon": lists.weapon+lists.melee, "background": lists.backgroundw, "back": lists.backw, "skin": lists.skinw, "head": lists.headw, "chest": lists.chestw, "leg": lists.legw, "foot": lists.footw, "face": lists.facew, "hair": lists.hairw}
        await updateset(ctx.author.id, f'equipments.{[t for t in dispatcher if item in dispatcher[t]][0]}', item)
        if item == "Baseball Bat" and user['s'] == 36:
          await updateset(ctx.author.id, 's', 37)
        elif item == "Plain Tee" and user['s'] == 57:
          await updateset(ctx.author.id, 's', 58)
        await ctx.respond(f"You equipped {item}")

async def unequip(self, ctx, item):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if not len([user['equipments'][equipment] for equipment in user['equipments'] if equipment != ""]):
        await ctx.respond("Imagine having nothing to unequip")
        return
      elif item is None:
        await ctx.respond("What do you want to unequip?")
        return

      try:
        item = item.lower()
      except:
        pass
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in (lists.wearables+lists.weapon+lists.melee) if item in x.lower() or item in x.lower().replace(" ","")]
        if not len(closematch):
          await ctx.respond("This item cannot be equipped or doesn't even exist, check if you spelled it correctly!")
          return
        closematch = [x for x in closematch if x in [user['equipments'][eq] for eq in list(user['equipments']) if user['equipments'][eq] != "normal"]]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond(f"You are not even equipping this item")
        return

      await updateset(ctx.author.id, f"equipments.{[equipment for equipment in user['equipments'] if user['equipments'][equipment] == item][0]}", "")
      await ctx.respond(f"You unequipped your {item}.")

async def leaderboard(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      page = page or 1
      page = int(page)

      printables = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()+,-./:;<=>?@[\\]^}{~ ")

      lblist = sorted(await self.bot.cll.find({"id": {"$in": [member.id for member in ctx.guild.members if member.bot is False]}}).to_list(length=None), key=lambda x: x['cash'] + x['stash'], reverse=True)[:10]

      def indexlb(lblist: list):
        lblist = [(member.split(" |")[0] + ("|".rjust(len(max([member.split("|")[0] for member in lblist], key=len))+3)+(member.split("|")[-1]))[(1+(len(member.split(" |")[0][1:]))):]) for member in lblist]
        if page == 1:
          if len(lblist) == 1:
            lblist = ["<:golden_trophy:900922720257212457>" + lblist[0]]
          elif len(lblist) == 2:
            lblist = ["<:golden_trophy:900922720257212457>" + lblist[0]] + ["<:silver_tophy:900922471128117268>" + lblist[1]]
          else:
            lblist = ["<:golden_trophy:900922720257212457>" + lblist[0]] + ["<:silver_tophy:900922471128117268>" + lblist[1]] + ["<:bronze_trophy:900922530221662218>" + lblist[2]] + [f"\U0001f4a0 {lblist[x+3]}" for x in range(len(lblist)-3)]
        else:
          lblist = [f"\U0001f4a0 {lblist[x]}" for x in range(len(lblist))]
        return lblist

      lblist = [f" `{''.join(filter(lambda x: x in printables, member['name']))} | {member['cash'] + member['stash']}`" for member in lblist if member['cash'] + member['stash'] > 10][:100]

      maxpage = -(-len(lblist) // 10)
      maxpage = maxpage or 1
      last = "wealth"
      if page > maxpage:
        await ctx.respond(f"There are only {maxpage} pages")
        return
      lblist = lblist[(page-1)*10:10+(page-1)*10]
      if len(lblist) == 0:
        lblist.append("**There are no users on the leaderboard**")
      else:
        lblist = indexlb(lblist)

      embed = discord.Embed(title=f"Leaderboard for {ctx.guild.name}", description="\U0001f4b5 Wealthiest user **(Cash and Stash)**", color=color.blurple()).set_footer(text=f"Page {page} of {maxpage}")
      embed.add_field(name="_ _", value="\n".join(lblist))
      
      view = interclass.Leaderboard_select(ctx, ctx.author)
      await ctx.respond(embed=embed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
          await view.wait()
          if view.value is None:
            return
          if view.value == "left":
            page = page - 1 if page > 1 else page
            view.value = last
          elif view.value == "right":
            page = page + 1 if page < maxpage else page
            view.value = last
          if view.value == "wealth":
            if last != "wealth":
              page = 1
            last = "wealth"
            view = interclass.Leaderboard_select(ctx, ctx.author)
            lblist = [f" `{''.join(filter(lambda x: x in printables, member['name']))} | {member['cash'] + member['stash']}`" for member in sorted(await self.bot.cll.find({"id": {"$in": [member.id for member in ctx.guild.members if member.bot is False]}}).to_list(length=None), key=lambda x: x['cash'] + x['stash'], reverse=True) if member['cash'] + member['stash'] > 10][:100]
            maxpage = -(-len(lblist) // 10)
            maxpage = maxpage or 1
            if len(lblist) == 0:
              lblist.append("**There are no users on the leaderboard**")
            else:
              lblist = indexlb(lblist[(page-1)*10:10+(page-1)*10])

            embed = discord.Embed(title=f"Leaderboard for {ctx.guild.name}", description="\U0001f4b5 Wealthiest user **(Cash and Stash)**", color=color.blurple()).set_footer(text=f"Page {page} of {maxpage}")
            embed.add_field(name="_ _", value="\n".join(lblist))
            view.message = await msg.edit(content="_ _", embed=embed, view=view)
          elif view.value == "level":
            if last != "level":
              page = 1
            last = "level"
            view = interclass.Leaderboard_select(ctx, ctx.author)
            lblist = [f" `{''.join(filter(lambda x: x in printables, member['name']))} | {round(member['lvl'] + (int(str(round(member['exp']))[-2:]) / 100), 2)}`" for member in sorted(await self.bot.cll.find({"id": {"$in": [member.id for member in ctx.guild.members if member.bot is False]}}).to_list(length=None), key=lambda x: round(x['lvl'] + (int(str(round(x['exp']))[-2:]) / 100), 2), reverse=True) if round(member['lvl'] + (int(str(round(member['exp']))[-2:]) / 100), 2) >= 1][:100]
            maxpage = -(-len(lblist) // 10)
            maxpage = maxpage or 1
            if len(lblist) == 0:
              lblist.append("**There are no users on the leaderboard**")
            else:
              lblist = indexlb(lblist[(page-1)*10:10+(page-1)*10])

            embed = discord.Embed(title=f"Leaderboard for {ctx.guild.name}", description="\U000023eb Most experienced user **(Level and Experience)**", color=color.blurple()).set_footer(text=f"Page {page} of {maxpage}")
            embed.add_field(name="_ _", value="\n".join(lblist))
            view.message = await msg.edit(content="_ _", embed=embed, view=view)
          elif view.value == "gwealth":
            if last != "gwealth":
              page = 1
            last = "gwealth"
            view = interclass.Leaderboard_select(ctx, ctx.author)
            lblist = [f" `{''.join(filter(lambda x: x in printables, member['name']))} | {member['cash'] + member['stash']}`" for member in sorted(await self.bot.cll.find().to_list(length=None), key=lambda x: x['cash'] + x['stash'], reverse=True) if member['cash'] + member['stash'] > 10][:100]
            maxpage = -(-len(lblist) // 10)
            maxpage = maxpage or 1
            if len(lblist) == 0:
              lblist.append("**There are no users on the leaderboard**")
            else:
              lblist = indexlb(lblist[(page-1)*10:10+(page-1)*10])

            embed = discord.Embed(title=f"Global Leaderboard", description="\U0001f4b5 Wealthiest user **(Cash and Stash)**", color=color.blurple()).set_footer(text=f"Page {page} of {maxpage}")
            embed.add_field(name="_ _", value="\n".join(lblist))
            view.message = await msg.edit(content="_ _", embed=embed, view=view)
          elif view.value == "glevel":
            if last != "glevel":
              page = 1
            last = "glevel"
            view = interclass.Leaderboard_select(ctx, ctx.author)
            lblist = [f" `{''.join(filter(lambda x: x in printables, member['name']))} | {round(member['lvl'] + (int(str(round(member['exp']))[-2:]) / 100), 2)}`" for member in sorted(await self.bot.cll.find().to_list(length=None), key=lambda x: round(x['lvl'] + (int(str(round(x['exp']))[-2:]) / 100), 2), reverse=True) if round(member['lvl'] + (int(str(round(member['exp']))[-2:]) / 100), 2) >= 1][:100]
            maxpage = -(-len(lblist) // 10)
            maxpage = maxpage or 1
            if len(lblist) == 0:
              lblist.append("**There are no users on the leaderboard**")
            else:
              lblist = indexlb(lblist[(page-1)*10:10+(page-1)*10])

            embed = discord.Embed(title=f"Global Leaderboard", description="\U000023eb Most experienced user **(Level and Experience)**", color=color.blurple()).set_footer(text=f"Page {page} of {maxpage}")
            embed.add_field(name="_ _", value="\n".join(lblist))
            view.message = await msg.edit(content="_ _", embed=embed, view=view)

async def title(self, ctx, title):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if title is None:
        if user['s'] == 61:
          await updateset(ctx.author.id, 's', 62)
        page = 1
        maxpage = -(-len(user['titles']) // 5)
        maxpage = maxpage or 1

        embed = discord.Embed(title="Your titles", description=f"You achieved **{len(user['titles'])}/{len([title for title in lists.title_description if title not in lists.hidden_titles])}** titles", color=color.random())
        embed.set_footer(text=f"Type '/title [title]' to equip a title!\nPage {page} of {maxpage}")
        if not len(user['titles']) == 0:
          for title in [i for i in lists.title_description if i in user['titles'][:5]]:
            embed.add_field(name=title, value=lists.title_description[title], inline=False)
        else: 
          embed.add_field(name="You don't have any titles", value="Type `/title list` to see a list of titles you can achieve")

        view = interclass.Page(ctx, ctx.author, page == 1, page == (-(-len(user['titles']) // 5) or 1))
        await ctx.respond(embed=embed, view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        while True:
          await view.wait()
          if view.value is None:
            return
          elif view.value == "left":
            page -= 1
          elif view.value == "right":
            page += 1

          embed = discord.Embed(title="Your titles", description=f"You achieved **{len(user['titles'])}/{len([title for title in lists.title_description if title not in lists.hidden_titles])}** titles", color=color.random())
          embed.set_footer(text=f"Type '/title [title]' to equip a title!\nPage {page} of {maxpage}")
          if not len(user['titles']) == 0:
            for title in [i for i in lists.title_description if i in user['titles'][(page-1)*5:(page-1)*5+5]]:
              embed.add_field(name=title, value=lists.title_description[title], inline=False)
          else: 
            embed.add_field(name="You don't have any titles", value="Type `/title list` to see a list of titles you can achieve")

          view = interclass.Page(ctx, ctx.author, page == 1, page == (-(-len(user['titles']) // 5) or 1))
          view.message = await msg.edit(embed=embed, view=view)

      elif title.lower() == "list":
        if user['s'] == 59:
          await updateset(ctx.author.id, 's', 60)
        page = 1
        maxpage = -(-len([title for title in list(lists.title_description) if title not in lists.hidden_titles]) // 5)

        embed = discord.Embed(title="List of titles", description=f"List of titles you can achieve!\nTitle marked with {star} is hidden, which means it is unobtainable through normal gameplay", color=color.random())
        embed.set_footer(text=f"Type '/title [title]' to equip a title!\nPage {page} of {maxpage}")

        for title in [title for title in list(lists.title_description) if title not in lists.hidden_titles][:5]:
          embed.add_field(name=title, value=lists.title_description[title], inline=False)

        view = interclass.Page(ctx, ctx.author, page == 1, page == -(-len([title for title in list(lists.title_description) if title not in lists.hidden_titles]) // 5))
        await ctx.respond(embed=embed, view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        while True:
          await view.wait()
          if view.value is None:
            return
          elif view.value == "left":
            page -= 1
          elif view.value == "right":
            page += 1

          embed = discord.Embed(title="List of titles", description=f"List of titles you can achieve!\nTitle marked with {star} is hidden, which means it is unobtainable through normal gameplay", color=color.random())
          embed.set_footer(text=f"Type '/title [title]' to equip a title!\nPage {page} of {maxpage}")

          for title in [title for title in list(lists.title_description) if title not in lists.hidden_titles][(page-1)*5:(page-1)*5+5]:
            embed.add_field(name=title, value=lists.title_description[title], inline=False)

          view = interclass.Page(ctx, ctx.author, page == 1, page == -(-len([title for title in list(lists.title_description) if title not in lists.hidden_titles]) // 5))
          view.message = await msg.edit(embed=embed, view=view)

      elif title.lower() == "unequip":
        if gettitle(user) == "":
          await ctx.respond("You didn't even equip a title")
          return
        await updateset(ctx.author.id, "title", "")

        await ctx.respond(f"Successfully unequipped title **{gettitle(user)}**")
        return

      title = title.lower()

      if len(title) < 2:
        await ctx.respond("Enter at least 2 letters to search")
        return
      closematch = [x for x in lists.title_description if title in x.lower() or title in x.lower().replace(" ","")]
      if not len(closematch):
        await ctx.respond("This title doesn't even exist!")
        return
      closematch = [x for x in closematch if x in user['titles']]
      if not len(closematch):
        await ctx.respond("You don't have this title!")
        return
      if len(closematch) > 1:
        await ctx.respond(f"I found more than one title that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
        return
      else:
        title = closematch[0]

      if title == gettitle(user)[1:-2]:
        await ctx.respond("You are already equipping this title, to unequip type `/title unequip` instead")
        return

      if user['s'] == 63 and title == "Hustler":
        await updateset(ctx.author.id, 's', 64)

      await updateset(ctx.author.id, "title", title)
      await ctx.respond(f"Successfully equipped the title **{title}**")

async def sleep(self, ctx):
      if await blocked(ctx.author.id) == False:
        await ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      if user['s'] == 28:
        await updateset(ctx.author.id, 's', 29)
      await ctx.respond("This feature has been removed from the bot! Wait for further updates...")
#       if user['energy'] >= user['energyc']:
#         await ctx.respond("You are already energetic enough!")
#         return
#       await updateset(ctx.author.id, "energy", user['energyc'])
#       await ctx.respond("You took a nap and filled up your energy!")

async def energy(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        return
      u = user = user or ctx.author
      user = await finduser(user.id)

      if user['s'] == 26:
        await updateset(ctx.author.id, 's', 27)

      await ctx.respond("This feature has been removed from the bot! Wait for further updates...")

#       colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
#       firstcolor = random.choice(colors)
#       colors.remove(firstcolor)

#       img = Image.new("RGBA", (212, 21))

#       maxenergy = round(user['energy']/user['energyc']*100*2) if round(user['energy']/user['energyc']*100*2) <= 200 else 200

#       pen = ImageDraw.Draw(img)
#       pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
#       pen.rounded_rectangle(((0, 0), (maxenergy, 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

#       byte = BytesIO()

#       img.save(byte, format="png")
#       byte.seek(0)

#       file = discord.File(fp=byte,filename="pic.png")

#       embed = discord.Embed(title=f"{gettitle(user)}{u.name}'s energy", description=f"\U000026a1 {user['energy']} / {user['energyc']}\nRegenerates **{user['epm']}** energy per minute", color=color.random()).set_footer(text="Sleep or eat to refill your energy")
#       embed.set_image(url="attachment://pic.png")
#       await ctx.respond(embed=embed, file=file)

async def level(self, ctx, user):
      if await blocked(ctx.author.id) is False:
        return
      user = user or ctx.author
      userp = await finduser(user.id)

      if userp is None:
        await ctx.respond("Cannot find this user!")
        return

      colors = ["#F9E076", "#C776F9", "#F976A8", "#A8F976", "#8576F9", "#76DAF9", "#F9A076", "#76f995", "#EAF976"]
      firstcolor = random.choice(colors)
      colors.remove(firstcolor)

      img = Image.new("RGBA", (212, 21))

      pen = ImageDraw.Draw(img)
      pen.rounded_rectangle(((0, 0), (200, 20)), fill=firstcolor, outline="black", width=2, radius=9)
      pen.rounded_rectangle(((0, 0), (round((userp['exp']-(userp['lvl']*100))*2), 20)), fill=random.choice(colors), outline="black", width=2, radius=9)

      byte = BytesIO()

      img.save(byte, format="png")
      byte.seek(0)

      file = discord.File(fp=byte,filename="pic.png")

      maxed = "(Maxed)"
      if functions.not_max_level(userp):
        maxed = ""

      pembed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s level", description=f"**Level** {userp['lvl']} {maxed}\n**Experience** {aa(round(userp['exp'],2))} / {aa(round(((userp['lvl'] * 100) + 100)))}", color=color.random())
      pembed.set_image(url="attachment://pic.png")
      await ctx.respond(file=file, embed=pembed)

async def reputation(self, ctx, user):
      if await blocked(ctx.author.id) is False:
        ctx.command.reset_cooldown(ctx)
        return
      user = user or ctx.author
      userp = await finduser(user.id)
      user2 = await finduser(ctx.author.id)

      if userp is None:
        await ctx.respond("Cannot find this user!")
        ctx.command.reset_cooldown(ctx)
        return

      rep = userp['rep']
      if userp['rep'] < 0:
        rep = "--" + str(rep)[1:]
      else:
        rep = "++" + str(rep)

      embed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s Reputation", description=f"{rep}\n\n**Your available respect points: {user2['rp']}**", color=color.blurple()).set_footer(text="Claim daily to refill your respect points!")
      
      view = interclass.Rep(ctx, ctx.author)
      await ctx.respond(embed=embed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      await view.wait()

      anonymous = False

      if view.value is None:
        ctx.command.reset_cooldown(ctx)
        return
      elif view.value == "a":
        anonymous = True

      view = interclass.Rep1(ctx, ctx.author, not user2['rp'] or user == ctx.author, anonymous)
      view.message = await msg.edit(view=view)

      reps = 0

      while True:
        await view.wait()
        if view.value is None:
          if reps:
            await updateinc(user.id, "rep", reps)

            if reps > 0:
              if anonymous:
                embed = discord.Embed(title="Respected", description=f"Somebody sent you {reps} respect points!", color=color.green())
              else:
                embed = discord.Embed(title="Respected", description=f"{ctx.author} sent you {reps} respect points!", color=color.green())
            else:
              if anonymous:
                embed = discord.Embed(title="Disrespected", description=f"Somebody sent you {reps} disrespect points!", color=color.red())
              else:
                embed = discord.Embed(title="Disrespected", description=f"{ctx.author} sent you {reps} disrespect points!", color=color.red())

            await user.send(embed=embed)
            return
          ctx.command.reset_cooldown(ctx)
          return

        elif view.value == "up":
          reps += 1
          userp['rep'] += 1
          user2['rp'] -= 1

          await updateinc(ctx.author.id, "rp", -1)

          rep = userp['rep']
          if userp['rep'] < 0:
            rep = "--" + str(rep)[1:]
          else:
            rep = "++" + str(rep)

          embed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s Reputation", description=f"{rep}\n\n**Your available respect points: {user2['rp']}**", color=color.blurple()).set_footer(text="Claim daily to refill your respect points!")
          
          view = interclass.Rep1(ctx, ctx.author, not user2['rp'] or user == ctx.author)
          view.message = await msg.edit(embed=embed, view=view)

        elif view.value == "down":
          reps -= 1
          userp['rep'] -= 1
          user2['rp'] -= 1

          await updateinc(ctx.author.id, "rp", -1)

          rep = userp['rep']
          if userp['rep'] < 0:
            rep = "--" + str(rep)[1:]
          else:
            rep = "++" + str(rep)

          embed = discord.Embed(title=f"{gettitle(userp)}{user.name}'s Reputation", description=f"{rep}\n\n**Your available respect points: {user2['rp']}**", color=color.blurple()).set_footer(text="Claim daily to refill your respect points!")
          
          view = interclass.Rep1(ctx, ctx.author, not user2['rp'] or user == ctx.author)
          view.message = await msg.edit(embed=embed, view=view)

async def story(self, ctx):
      guild = await self.bot.gcll.find_one({"id": 863025676213944340})
      if guild['maintenance'] == True and not ctx.author.id == 615037304616255491:
        return
      if await finduser(ctx.author.id) == None:
        ur = await self.bot.cll.find_one({"$query": {},"$orderby": {"index": -1}})
        newuser = {"drugs": {"cannabis": 0, "ecstasy": 0, "heroin": 0, "methamphetamine": 0, "xanax": 0}, "wishlist": {"1": "", "2": "", "3": "", "4": "", "5": ""}, "approve": 0, "index": ur['index']+1, "id": ctx.author.id, "name": ctx.author.name + "#" + ctx.author.discriminator, "title": "", "cash": 10, "stash": 0, "stashc": 0, "lvl": 0, "exp": 0, "property": 0, "donor": 0, "cmd": 0, "drive": "", "inhosp": False, "injail": False, 'blocked': False, 'banned': False, "stats":{"str": 10, "def": 10, "spd": 10, "dex": 10, "int": 0, "luk": 0, "cha": 0, "acc": 0, "dri": 0, "han": 0, "bra": 0},"storage": {}, "garage": [], "garagec": 5, "timer": {}, "dailystreak": 0, "job": "", "location": random.choice(list(lists.locationcoords)), 'cmdcount': 0, 'lastcmd': "", "lastcmdtime": round(time.time()), 'warns': 0, "br": "", 'business': 0, 'affinity': "Single", 'dbl': 0, 'topgg': 0, "equipments": {"background": "", "back": "", "skin": "normal", "foot": "", "leg": "", "hair": "", "face": "", "chest": "", "head": "", "weapon": ""}, "titles": [], "jobcount": 0, "codes": [], "token": 0, "q": [], "rep": 0, "rp": 1, "s": 0, "ins": 0, "heat": 0, "races": 0, "fraud": 0, "skill": 0}

        await insertdict(newuser)

        print(f"New user: {ctx.author} ({ctx.author.id})")
        await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"latestuser": str(ctx.author), "latestuserid": ctx.author.id, "latestusertime": round(time.time())}})

        await self.bot.get_channel(906514108143243342).send(f"**New user:** {ctx.author} ({ctx.author.id})")

      msg = None

      try:
        while True:
          user = await finduser(ctx.author.id)
          msg = await eval(f"functions.story{user['s']}(ctx, user, msg)")
          if not msg:
            break
      except AttributeError:
        await updateset(ctx.author.id, "s", 0)
        try:
          while True:
            user = await finduser(ctx.author.id)
            msg = await eval(f"functions.story{user['s']}(ctx, user, msg)")
            if not msg:
              break
        except AttributeError:
          await ctx.respond("Coming soon\nUse the tutorial command or help command!")
          pass

async def shop(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        return

      shopitem = [item for item in lists.bitem if item not in lists.drug+lists.weapon+lists.melee+lists.titem]

      maxpage = -(-len(shopitem) // 5)

      if page > maxpage:
        await ctx.respond(f"There is only {maxpage} pages can't you read smh")
      elif page <= 0:
        page = 1

      if (await finduser(ctx.author.id))['s'] == 30:
        await updateset(ctx.author.id, 's', 31)

      wembed = discord.Embed(title = "Shop", description = "City shop, buy everything here!", color = color.random()).set_footer(text=f"Page {page} of {maxpage}")

      for item in shopitem[(page-1)*5:(page-1)*5+5]:
        price = ('<:cash:1329017495536930886> ' + str(lists.item_prices[item])) if item not in lists.titem else (str(lists.item_prices[item]) + ' <:token:1313166204348792853>')
        wembed.add_field(name=item, value=f"{lists.item_description[item]}\n{price} | ID `{lists.item_id[item]}`", inline=False)

      view = interclass.Shop(ctx, ctx.author, page == 1, page == maxpage)
      await ctx.respond(embed=wembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1
        elif view.value == "normal":
          page = 1
          shopitem = [item for item in lists.bitem if item not in lists.drug+lists.weapon+lists.melee+lists.titem]
        elif view.value == "melee":
          page = 1
          shopitem = lists.melee
        elif view.value == "ranged":
          page = 1
          shopitem = lists.weapon
        elif view.value == "token":
          page = 1
          shopitem = lists.titem
        elif view.value == "insurance" or view.value == "buy":
          page = maxpage = 1
          dispatcher = {-1: 0, 0: 20, 1: 50, 2: 70, 3: 90, 4: 100, 5: 101, 6: 101}
          costs = {0: 100, 1: 150, 2: 200, 3: 250, 4: 300, 5: 500, 6: 0}
          user = await finduser(ctx.author.id)
          if view.value == "buy":
            await updateinc(ctx.author.id, 'ins', 1)
            await updateinc(ctx.author.id, 'cash', -costs[user['ins']])
            if user['s'] == 72:
              await updateset(ctx.author.id, 's', 73)

          user = await finduser(ctx.author.id)

          wembed = discord.Embed(title = "Shop", description = "City shop, buy everything here!", color = color.random())

          wembed.add_field(name=f"Insurance {dispatcher[user['ins']]}%", value=f"Covers {dispatcher[user['ins']]}% cash lost when you die\n\n**Your current Insurance covers {dispatcher[user['ins']-1]}% cash lost**")

          view = interclass.Insurance(ctx, ctx.author, costs[user['ins']], user['cash'])
          view.message = await msg.edit(embed=wembed, view=view)
          continue

        maxpage = -(-len(shopitem) // 5)

        wembed = discord.Embed(title = "Shop", description = "City shop, buy everything here!", color = color.random()).set_footer(text=f"Page {page} of {maxpage}")

        for item in shopitem[(page-1)*5:(page-1)*5+5]:
          price = ('<:cash:1329017495536930886> ' + str(lists.item_prices[item])) if item not in lists.titem else (str(lists.item_prices[item]) + ' <:token:1313166204348792853>')
          wembed.add_field(name=item, value=f"{lists.item_description[item]}\n{price} | ID `{lists.item_id[item]}`", inline=False)

        view = interclass.Shop(ctx, ctx.author, page == 1, page == maxpage)
        view.message = await msg.edit(embed=wembed, view=view)

async def estate(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        return

      user = await finduser(ctx.author.id)

      maxpage = len(list(lists.propertyid.keys()))

      if page > maxpage:
        await ctx.respond(f"There are only {maxpage} pages can't you read smh")
      elif page <= 0:
        await ctx.respond(f"Don't try to annoy me")

      prop = list(lists.propertyid.keys())[page-1]

      img = Image.open(rf"images/{lists.propertyid[prop]}.png").convert("RGB")

      byte = BytesIO()

      img.save(byte, format="png")

      byte.seek(0)

      file = discord.File(byte, "pic.png")

      embed = discord.Embed(title="Real Estate", description=f"{lists.propertyname[prop]}\n<:cash:1329017495536930886> {prop*100} Stash Capacity\n{lists.propertydesc[prop]}", color=color.random()).set_image(url="attachment://pic.png")
      embed.set_footer(text=f"Page {page} of {maxpage}")

      view = interclass.Estate(ctx, ctx.author, page == 1, page == maxpage, page < 5, page > maxpage-5, lists.propertyprice[lists.propertyname[prop]], user['cash'])
      await ctx.respond(embed=embed, view=view, file=file)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1
        elif view.value == "ll":
          page -= 5
          if page < 0:
            page = 0
        elif view.value == "rr":
          page += 5
          if page > maxpage:
            page = maxpage
        elif view.value == "buy":
          if prop == user['property']:
            await ctx.respond("You already owned this property")
            return
          if user['cash'] < lists.propertyprice[lists.propertyname[prop]]:
            await ctx.respond("You don't even have enough cash scammer")
            return
          if user['property'] != 0:
            view = interclass.Confirm(ctx, ctx.author)

            await ctx.respond(f"You will lose your current property if you buy a new one! Are you sure?", view=view)
            msg = await ctx.interaction.original_response()
            view.message = msg
            
            await view.wait()

            if view.value is None:
              await ctx.respond("You didn't respond")
              return
            if view.value == False:
              await ctx.respond("Alright then, see you next time")
              return
          
          await updateinc(ctx.author.id,'cash', -lists.propertyprice[lists.propertyname[prop]])
          await updateset(ctx.author.id,'property', prop)
          try:
            userstorage = user['storage']
            usersafeq = userstorage['Safe']
            await updateset(ctx.author.id, 'stashc', (propertyid*100)+(usersafeq*500))
          except:
            await updateset(ctx.author.id,'stashc', prop*100)

          await ctx.respond(f"You bought a {lists.propertyname[prop]} for <:cash:1329017495536930886> {lists.propertyprice[lists.propertyname[prop]]}!")
          return

        prop = list(lists.propertyid.keys())[page-1]

        img = Image.open(rf"images/{lists.propertyid[prop]}.png").convert("RGB")

        byte = BytesIO()

        img.save(byte, format="png")

        byte.seek(0)

        file = discord.File(byte, "pic.png")

        embed = discord.Embed(title="Real Estate", description=f"{lists.propertyname[prop]}\n<:cash:1329017495536930886> {prop*100} Stash Capacity\n{lists.propertydesc[prop]}", color=color.random()).set_image(url="attachment://pic.png")
        embed.set_footer(text=f"Page {page} of {maxpage}")

        view = interclass.Estate(ctx, ctx.author, page == 1, page == maxpage, page < 5, page > maxpage-5, lists.propertyprice[lists.propertyname[prop]], user['cash'])
        view.message = await msg.edit(embed=embed, view=view, file=file)

async def work(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      userjob = user['job']
      if userjob == "":
        await ctx.respond("How are you going to work without a job?")
        ctx.command.reset_cooldown(ctx)
        return

      passed, *extra = await functions.dispatcher[user['job']](ctx)

      if passed is False:
        if extra != []:
          embed = discord.Embed(title=f"Worked as {userjob}", description=f"You failed your job!", color=color.red())
          if extra != []:
            embed.add_field(name="Bonus!",value=extra[0])
          await ctx.respond(embed=embed)
        return

      salary = lists.jobsalary[userjob]
      salary = round(salary + (salary*user['stats']['cha']/1000) + (salary*dboost(user['donor'])))
      await updateinc(ctx.author.id, 'cash', salary)
      if user['stats']['cha'] < 3000:
        await updateinc(ctx.author.id, 'stats.cha', 1)
        embed = discord.Embed(title=f"Worked as {userjob}", description=f"You earned <:cash:1329017495536930886> {salary} and gained 1 Charisma <:charisma:940955424910356491>", color=color.green())
      else:
        embed = discord.Embed(title=f"Worked as {userjob}", description=f"You earned <:cash:1329017495536930886> {salary}", color=color.green())
      if extra != []:
        embed.add_field(name="Bonus!",value=extra[0])
      await ctx.respond(embed=embed)

async def menu(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        return
      maxpage = -(-len(lists.all_jobs) // 5)
      if page >= 4:
        await ctx.respond(f"There are only {maxpage} pages")
      elif page <= 0:
        page = 1
      user = await finduser(ctx.author.id)
      jobembed = discord.Embed(title="Jobs",description=f"You need to meet the requirements before assigning the job!\nJobs marked with {star} are the ones you assigned before\nYou can reassign without losing anything!",color=color.blue())
      jobembed.set_footer(text=f"Every job have different perks!\nPage {page} of {maxpage}")
      for job in lists.all_jobs[(page-1)*5:(page-1)*5+5]:
        jobname = job
        if job in compress(lists.all_jobs, [int(i) for i in format(user['jobcount'], 'b')[::-1]]):
          jobname += f" {star}"
        jobembed.add_field(name=jobname, value=f"**Salary** <:cash:1329017495536930886> {lists.jobsalary[job]}\n"+lists.job_requirements[job], inline=False)

      view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
      await ctx.respond(embed=jobembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1
        jobembed = discord.Embed(title="Jobs",description=f"You need to meet the requirements before assigning the job!\nJobs marked with {star} are the ones you assigned before, you can reassign without losing anything!",color=color.blue())
        jobembed.set_footer(text=f"Every job have different perks!\nPage {page} of {maxpage}")
        for job in lists.all_jobs[(page-1)*5:(page-1)*5+5]:
          jobname = job
          if job in compress(lists.all_jobs, [int(i) for i in format(user['jobcount'], 'b')[::-1]]):
            jobname += f" {star}"
          jobembed.add_field(name=jobname, value=f"**Salary** <:cash:1329017495536930886> {lists.jobsalary[job]}\n"+lists.job_requirements[job], inline=False)

        view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
        view.message = await msg.edit(embed=jobembed, view=view)

async def assign(self, ctx, job):
      if await blocked(ctx.author.id) == False:
        return
      if job == None:
        await ctx.respond("Give a job you want to assign!")
        ctx.command.reset_cooldown(ctx)
        return
      try:
        if len(job) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          ctx.command.reset_cooldown(ctx)
          return
        job = job.lower()
        closematch = [x for x in lists.all_jobs if job == x.lower()] 
        if closematch == []:
          closematch = [x for x in lists.all_jobs if job in x.lower() or job in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one jobs that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          ctx.command.reset_cooldown(ctx)
          return
        else:
          job = closematch[0]
      except:
        await ctx.respond(f"Cannot find this job '{job}', check if you spelled it correctly!")
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      userjob = user['job']
      userintel = user['stats']['int']
      userstorage = user['storage']
      if userjob == job:
        await ctx.respond(f"You are already working as a {job}")
        return
      if not userjob == "":
        view = interclass.Confirm(ctx, ctx.author)
        await ctx.respond(f"You are now currently working as a {userjob}, are you sure you want to change it to {job}?", view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg
        await view.wait()
        if view.value is None:
          await msg.edit("You didn't respond in time")
          ctx.command.reset_cooldown(ctx)
          return
        elif view.value is False:
          await msg.edit("Alright then")
          ctx.command.reset_cooldown(ctx)
          return
      if job not in compress(lists.all_jobs, [int(i) for i in format(user['jobcount'], 'b')[::-1]]):
        if job == 'Beggar':
          if userintel < 10:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Business man':
          if userintel < 100 or user['cash'] < 200:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Trash collector':
          try:
            usercan = userstorage['Can']
            usertrash = userstorage['Trash']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 30 or usercan < 1 or usertrash < 10:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Kidnapper':
          try:
            userlollipop = userstorage['Lollipop']
            userchocolate = userstorage['Chocolate']
            usercandy = userstorage['Candy']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 50 or userlollipop < 1 or userchocolate < 1 or usercandy < 25:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Teacher':
          try:
            usernotebook = userstorage['Notebook']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 120 or usernotebook < 2:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Chef':
          try:
            userbread = userstorage['Bread']
            userdrumstick = userstorage['Drumstick']
            usermeat = userstorage['Meat']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 40 or userbread < 5 or userdrumstick < 1 or usermeat < 30:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Gamer':
          try:
            userchips = userstorage['Bag of Chips']
            usersoda = userstorage['Soda']
            userconsole = userstorage['Console']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 100 or userchips < 5 or usersoda < 5 or userconsole < 1:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Doctor':
          try:
            userknife = userstorage['Surgeon Knife']
            usersteth = userstorage['Stethoscope']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 800 or userknife < 1 or usersteth < 1:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Artist':
          try:
            userbrush = userstorage['Paintbrush']
            userpaper = userstorage['Paper']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 80 or userbrush < 1 or userpaper < 5:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        elif job == 'Lawyer':
          try:
            usergavel = userstorage['Gavel']
          except:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
          if userintel < 200 or usergavel < 1:
            await ctx.respond("You don't meet the requirements for this job")
            ctx.command.reset_cooldown(ctx)
            return
        jobembed = discord.Embed(title="Job assigned",description=f"You are now working as a {job}!",color=color.green())
        await updateinc(ctx.author.id, 'jobcount', (2 ** lists.all_jobs.index(job)))
      else:
        jobembed = discord.Embed(title="Job assigned",description=f"You went back to work as a {job}!",color=color.green())
      await updateset(ctx.author.id, 'job', job)
      if job == 'Clown':
        jobembed.set_footer(text="Haha you clown")
      await ctx.respond(embed=jobembed)

async def perk(self, ctx, target):
      user = await self.bot.cll.find_one({"id": ctx.author.id})
      if user is None:
        ctx.command.reset_cooldown(ctx)
        return
      try:
        user['timer']['blocked']
        ctx.command.reset_cooldown(ctx)
        return
      except:
        if user['banned'] == True or user['blocked'] == True:
          ctx.command.reset_cooldown(ctx)
          return

      userjob = user['job']
      if userjob == "":
        await ctx.respond("You don't even have a job, type `/job menu` to learn more")
        ctx.command.reset_cooldown(ctx)
        return
      elif userjob == 'Clown':
        if target == None:
          await ctx.respond("You have to give a target to send!")
          ctx.command.reset_cooldown(ctx)
          return
        trollembed = discord.Embed(title="You died!",description="Someone killed you and you lost all your cash",color=color.red())
        trollembed.set_footer(text="BIG RIP\ntrolled")
        trollembed2 = discord.Embed(title="Someone shot you!",description="You have been shot and died\nYou lost all your cash",color=color.red())
        trollembed2.set_footer(text="so sad\njust kidding")
        trollembed3 = discord.Embed(title="You died!",description="You got beaten up in a fight and ended up in Hospital for 6969 hours!",color=color.red())
        trollembed3.set_footer(text="you cant use any medical kits!\njust kidding")
        trollembed4 = discord.Embed(title="Warn",description="You have been warned more than 3 times and now you are banned!",color=color.red())
        trollembed4.set_footer(text="no more ov bot for you\njust a joke")
        await target.send(embed=random.choice([trollembed,trollembed2,trollembed3,trollembed4]))
        await ctx.respond("You sent a fake message to the user!")
      elif userjob == 'Beggar':
        randomcash = round(random.uniform(0, 20))
        randomcash = round(randomcash + (randomcash*user['stats']['cha']/1000))
        await ctx.respond(f"You begged for some cash and gained <:cash:1329017495536930886> {randomcash}!")
        await updateinc(ctx.author.id, 'cash', round(randomcash))
      elif userjob == 'Business man':
        await ctx.respond(f"You successfully activated your Cash Boost for 20 minutes! You currently have {user['stats']['cha']/1000*100+50}% Cash Boost")
        await updateinc(ctx.author.id, 'stats.cha', 500)
        await updateset(ctx.author.id, 'timer.cashboost', round(time.time())+1200)
      elif userjob == 'Trash collector':
        randomcount = random.randint(4,8)
        await updateinc(ctx.author.id, 'storage.Trash', randomcount)
        await ctx.respond(f"You explored the dump and found {randomcount} Trash!")
      elif userjob == 'Kidnapper':
        await ctx.respond(f"You successfully activated your Luck Boost for 20 minutes! You currently have {user['stats']['luk']+50} Luck")
        await updateinc(ctx.author.id, 'stats.luk', 50)
        await updateset(ctx.author.id, 'timer.cboost', round(time.time())+1200)
      elif userjob == 'Teacher':
        await ctx.respond("Your perk is passive so you can't use it")
        ctx.command.reset_cooldown(ctx)
      elif userjob == 'Chef':
        randomcount = random.randint(2,6)
        await updateinc(ctx.author.id, 'storage.Meat', randomcount)
        await ctx.respond(f"You stole {randomcount} Meat from the kitchen!")
      elif userjob == 'Gamer':
        msg = await ctx.respond("Too bad, this job isn't available anymore due to Discord's limitations :(")
        # timeout = 30
        # count = 0
        # previous = None
        # while True:
        #   word = random.choice(lists.gamewordslist)
        #   while previous == word:
        #     word = random.choice(lists.gamewordslist)
        #   previous = word
        #   answer = lists.gamewords[word]
        #   start = time.time()
        #   await msg.edit(content=f"Type as much words as you can! You have 30 seconds\nType out the word `{word}`")
        #   def check(msg):
        #     return msg.channel == ctx.channel and msg.author == ctx.author and msg.content.lower() == answer
        #   try:
        #     await self.bot.wait_for("message", check=check,timeout=timeout)
            
        #     end = time.time()
        #     timeout -= (end - start)
        #     count += 1
        #   except asyncio.TimeoutError:
        #     break
        # if count == 0:
        #   await ctx.respond("You didn't even typed a single word, you earned nothing")
        #   return
        # cash = round(random.uniform((count*20)-5,(count*20)+5))
        # await ctx.respond(f"You typed {count} words and earned <:cash:1329017495536930886> {round(cash)}!")
        # await updateinc(ctx.author.id, 'cash', round(cash))
      elif userjob == 'Artist':
        randomchance = round(random.random(),4)
        if randomchance > 0.51:
          randomcash = round(random.uniform(35,70))
          await ctx.respond(f"You drew something but its too ugly and sold it for <:cash:1329017495536930886> {randomcash}")
          await updateinc(ctx.author.id, 'cash', randomcash)
        elif 0.11 < randomchance <= 0.51:
          randomcash = round(random.uniform(200,750))
          await ctx.respond(f"You drew something that is so realistic and it sold for <:cash:1329017495536930886> {randomcash}!")
          await updateinc(ctx.author.id,'cash',randomcash)
        elif randomchance <= 0.11:
          user = await finduser(ctx.author.id)
          randomc = random.choice(lists.highcar)
          randomgold = random.randint(1,1024)
          if len(user['garage']) == 0:
            carindex = 1
          else:
            carindex = user['garage'][-1]["index"]+1
          if randomgold == 896:
            await ctx.respond(f"You drew a **{star} Golden {randomc}** that is so realistic and it became real!")
            carinfo = {'index': carindex, 'id': functions.randomid(), 'name': randomc, 'price': lists.carprice[randomc], 'speed': round(random.uniform(lists.carspeed[randomc]-10, lists.carspeed[randomc]+10), 2), 'tuned': 0, 'golden': True, 'locked': False}
          else:
            await ctx.respond(f"You drew a **{randomc}** that is so realistic and it became real!")
            carinfo = {'index': carindex, 'id': functions.randomid(), 'name': randomc, 'price': lists.carprice[randomc], 'speed': round(random.uniform(lists.carspeed[randomc]-10, lists.carspeed[randomc]+10), 2), 'tuned': 0, 'golden': False, 'locked': False}
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"garage": carinfo}})
      elif userjob == 'Doctor':
        if target == None:
          target = ctx.author
        user = await finduser(target.id)
        if user is None:
          await ctx.respond("This user haven't started playing OV Bot yet!")
          return
        userinhosp = user['inhosp']
        if userinhosp == False and target == ctx.author:
          await ctx.respond("You are not even in Hospital")
          ctx.command.reset_cooldown(ctx)
          return
        elif userinhosp == False and not target == ctx.author:
          await ctx.respond("The user is not even in Hospital")
          ctx.command.reset_cooldown(ctx)
          return
        await updateset(target.id, 'inhosp', False)
        targetp = await finduser(target.id)
        await self.bot.cll.update_one({"id": target.id}, {"$unset": {"timer.hosp": 1}})
        msg = await ctx.respond(f"You revived {targetp['title']}{target.mention} and the user is now out of Hospital!")
        revembed = discord.Embed(title="Revived", description=f"{gettitle(user)}{ctx.author} revived you from Hospital!\nYou no longer have to wait for timer\n[**Jump to message**]({msg.jump_url})",color=color.green())
        revembed.set_footer(text='so nice!')
        await target.send(embed=revembed)
      elif userjob == 'Lawyer':
        if target == None:
          target = ctx.author
        user = await finduser(target.id)
        if user is None:
          await ctx.respond("This user haven't started playing OV Bot yet!")
          return
        userinjail = user['injail']
        if userinjail == False and target == ctx.author:
          await ctx.respond("You are not even in Jail")
          ctx.command.reset_cooldown(ctx)
          return
        elif userinjail == False and not target == ctx.author:
          await ctx.respond("The user is not even in Jail")
          ctx.command.reset_cooldown(ctx)
          return
        await updateset(target.id, 'injail', False)
        targetp = await finduser(target.id)
        await self.bot.cll.update_one({"id": target.id}, {"$unset": {"timer.jail": 1}})
        msg = await ctx.respond(f"You bailed {targetp['title']}{target.mention} out of Jail!")
        revembed = discord.Embed(title="Bailed", description=f"{gettitle(user)}{ctx.author} bailed you out of Jail!\nYou no longer have to wait for timer\n[**Jump to message**]({msg.jump_url})",color=color.green())
        revembed.set_footer(text='so nice!')
        await target.send(embed=revembed)

async def perklist(self, ctx, page):
    if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
    ctx.command.reset_cooldown(ctx)

    page = page or 1
    maxpage = 3

    if page >= 4:
      await ctx.respond("There are only 3 pages can't you read lol")
    elif page <= 0:
      page = 1

    jobembed = discord.Embed(title="Jobs",description="Every job have different perks!",color=color.blue())
    jobembed.add_field(name="Clown",value="Be a clown and send someone fake notification",inline=False)
    jobembed.add_field(name="Beggar",value="Gain extra cash",inline=False)
    jobembed.add_field(name="Business man", value="Gives you 50% Cash Boost for 20 minutes",inline=False)
    jobembed.add_field(name="Trash Collector",value="Gives you some trash",inline=False)
    jobembed.add_field(name="Kidnapper",value="Increases luck by 50 for 20 minutes",inline=False)
    jobembed.set_footer(text="Page 1 of 3")

    view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
    await ctx.respond(embed=jobembed, view=view)
    msg = await ctx.interaction.original_response()
    view.message = msg

    while True:
      await view.wait()
      if view.value is None:
        return
      elif view.value == "left":
        page -= 1
      elif view.value == "right":
        page += 1
      if page == 1:
        jobembed = discord.Embed(title="Jobs",description="Every job have different perks!",color=color.blue())
        jobembed.add_field(name="Clown",value="Be a clown and send someone fake notifcation",inline=False)
        jobembed.add_field(name="Beggar",value="Gain extra cash",inline=False)
        jobembed.add_field(name="Business man", value="Gives you 50% Cash Boost for 20 minutes",inline=False)
        jobembed.add_field(name="Trash Collector",value="Gives you some trash",inline=False)
        jobembed.add_field(name="Kidnapper",value="Increases luck by 50 for 20 minutes",inline=False)
      elif page == 2:
        jobembed = discord.Embed(title="Jobs",description="Every job have different perks!",color=color.blue())
        jobembed.add_field(name="Teacher",value="Gives you extra 2 intelligence <:intelligence:940955425443024896> while learning",inline=False)
        jobembed.add_field(name="Chef",value="Gets free meat",inline=False)
        jobembed.add_field(name="Gamer", value="Play a game and earn cash!",inline=False)
        jobembed.add_field(name="Doctor",value="Allows you to heal yourself or someone else from Hospital",inline=False)
        jobembed.add_field(name="Artist", value="Draw something and sell it! You might get a car",inline=False)
      elif page == 3:
        jobembed = discord.Embed(title="Jobs", description="Every job have different perks!",color=color.blue())
        jobembed.add_field(name="Lawyer", value="Allows you to bail yourself or someone else from Jail",inline=False)

      jobembed.set_footer(text=f"Page {page} of {maxpage}")
      view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
      view.message = await msg.edit(embed=jobembed, view=view)

async def blackmarket(self, ctx, page):
      if await blocked(ctx.author.id) == False:
        return
      if page >= 2:
        await ctx.respond("There are only 1 pages can't you read smh")
      elif page <= 0:
        await ctx.respond(f"Don't try to annoy me")
      user = await finduser(ctx.author.id)
      userlocation = user['location']
      city = await self.bot.bm.find_one({"city": userlocation})
      citydrugs = city['drugs']
      userstorage = user['storage']
      try:
        cannabis_owned = userstorage["Cannabis"]
      except:
        cannabis_owned = 0
      try:
        ecstasy_owned = userstorage["Ecstasy"]
      except:
        ecstasy_owned = 0
      try:
        heroin_owned = userstorage["Heroin"]
      except:
        heroin_owned = 0
      try:
        metham_owned = userstorage["Methamphetamine"]
      except:
        metham_owned = 0
      try:
        xanax_owned = userstorage["Xanax"]
      except:
        xanax_owned = 0
      if page == 1:
        bmembed = discord.Embed(title="Blackmarket",description=f"Blackmarket in **{userlocation}**\nPrice changes in **{ab(round(datetime.timestamp(self.bot.drugprices.next_iteration))-round(time.time()))}**",color=color.random())
        bmembed.add_field(name="Cannabis",value=f"<:cash:1329017495536930886> {round(citydrugs['Cannabis'])} | **Owned:** {cannabis_owned}", inline = False)
        bmembed.add_field(name="Ecstasy",value=f"<:cash:1329017495536930886> {round(citydrugs['Ecstasy'])} | **Owned:** {ecstasy_owned}", inline = False)
        bmembed.add_field(name="Heroin",value=f"<:cash:1329017495536930886> {round(citydrugs['Heroin'])} | **Owned:** {heroin_owned}", inline = False)
        bmembed.add_field(name="Methamphetamine",value=f"<:cash:1329017495536930886> {round(citydrugs['Methamphetamine'])} | **Owned:** {metham_owned}", inline = False)
        bmembed.add_field(name="Xanax",value=f"<:cash:1329017495536930886> {round(citydrugs['Xanax'])} | **Owned:** {xanax_owned}", inline = False)
        bmembed.set_footer(text="Prices will be different every 10 minutes\nPage 1 of 1")

        await ctx.respond(embed=bmembed)

async def travel(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)

      try:
        if user['timer']['travel'] > round(time.time()):
          cdembed = discord.Embed(title = "Command on cooldown!", color = color.gold())
          if user['donor'] == True:
            cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(user['timer']['travel']-round(time.time()))}`!\nYou are a royal member so the cooldown is `{ab(7200)}`")
          else:
            cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(user['timer']['travel']-round(time.time()))}`!\nCooldown for this command is `{ab(10800)}`\nRoyal members have lesser cooldown on some commands!")
          cdembed.set_footer(text = "Chill!")

          await ctx.respond(embed=cdembed)
          return
      except:
        pass

      if user['lvl'] < 10:
        await ctx.respond("You have to be at least level 10 to travel!")
        return

      img = Image.open(r"images/map.png").convert('RGBA')

      img2 = Image.open(r"images/pointer.png").convert('RGBA')

      img.paste(img2, lists.locationcoords[locname[user['location'].lower()]], img2)

      byte = BytesIO()

      img.save(byte, format="png")
      byte.seek(0)

      file = discord.File(fp=byte,filename="pic.png")

      view = interclass.Travel(ctx, ctx.author, user['location'], locname[user['location'].lower()], locprice[user['location'].lower()], user['cash'])

      embed = discord.Embed(title=f"{locname[user['location'].lower()]} Airport", color=color.blurple())
      embed.set_image(url="attachment://pic.png")
      embed.set_footer(text=f"Drug prices will be different in different countries!")

      await ctx.respond(file=file, embed=embed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg
      lastvalue = None

      while True:
        await view.wait()
        if view.value is None and view.locvalue is None:
          return
        elif view.value == "travel":
          await updateinc(ctx.author.id, 'cash', -locprice[lastvalue])
          if user['donor'] == True:
            await updateset(ctx.author.id, 'timer.travel', round(time.time())+7200)
          else:
            await updateset(ctx.author.id, 'timer.travel', round(time.time())+10800)
          randomcrash = round(random.random(),4)
          if randomcrash <= 0.01:
            await self.die(ctx, ctx.author, f'while travelling to {locname[lastvalue]}!', 'The airplane exploded for no reason')
            return
          else:
            await updateset(ctx.author.id, 'location', locname[lastvalue])
            await ctx.respond(f"You paid <:cash:1329017495536930886> {locprice[lastvalue]} and made a smooth landing in {locname[lastvalue]}!")
            return

        lastvalue = view.locvalue

        img = Image.open(r"images/map.png").convert('RGBA')

        img2 = Image.open(r"images/pointer.png").convert('RGBA')

        img.paste(img2, lists.locationcoords[locname[view.locvalue]], img2)

        byte = BytesIO()

        img.save(byte, format="png")
        byte.seek(0)

        file = discord.File(fp=byte,filename="pic.png")

        embed = discord.Embed(title=f"{locname[view.locvalue]} Airport", color=color.blurple())
        embed.set_image(url="attachment://pic.png")
        embed.set_footer(text=f"Drug prices will be different in different countries!")
        view = interclass.Travel(ctx, ctx.author, user['location'], locname[view.locvalue], locprice[view.locvalue], user['cash'])

        view.message = await msg.edit(attachments=[], file=file, embed=embed, view=view)

async def learn(self, ctx):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      user = await finduser(ctx.author.id)
      if user['stats']['int'] >= user['lvl']*10:
        await ctx.respond("You are too smart! Level up before learning again")
        return

      if random.random() <= 0.01 and 'Genius' not in user['titles']:
        modal = interclass.Learn("Find 𝑥, log₃(√𝑥 + 2)=½log₃(81)+log₃(𝑥 × ⅓)")
        await ctx.interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.value == 1:
          await modal.interaction.channel.send(content=f"You can't even do math? Go back to school")
          return
        userjob = user['job']
        intel = 10
        if userjob == 'Teacher':
          intel = 20
        await modal.interaction.channel.send(content=f"The answer `???` is correct! You gained {intel} intelligence <:intelligence:940955425443024896> and was awarded an achievement `Genius`!\n-# Check your titles")
        await updateinc(ctx.author.id, 'stats.int', intel)
        await cll.update_one({"id": ctx.author.id}, {"$addToSet": {"titles": "Genius"}})
      else:
        op = random.choice(["+", "-", "×"])
        if op in ["+", "-"]:
          firstnum = random.randint(10,99)
          secondnum = random.randint(10,99)
        else:
          firstnum = random.randint(2,12)
          secondnum = random.randint(2,12)
        dispatcher = {"+": operator.add, "-": operator.sub, "×": operator.mul}
        func = dispatcher[op]
        modal = interclass.Learn(f"What is {firstnum} {op} {secondnum}?")
        await ctx.interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.value == str(func(firstnum, secondnum)):
          await modal.interaction.channel.send(content=f"You can't even do math? **{round(firstnum)} {op} {round(secondnum)}** is **{func(firstnum, secondnum)}**")
          return
        userjob = user['job']
        intel = random.choice([1,1,1,2,1,1,1,1,1,1])
        if userjob == 'Teacher':
          intel += 2
        await modal.interaction.channel.send(content=f"The answer **{func(firstnum, secondnum)}** is correct! You gained {intel} intelligence <:intelligence:940955425443024896>!")
        await updateinc(ctx.author.id, 'stats.int', intel)

async def train(self, ctx, info):
      if await blocked(ctx.author.id) == False:
        return
      user = await self.bot.cll.find_one({"id": ctx.author.id})
      if info == "info":
        if user['s'] == 51:
          await updateset(ctx.author.id, 's', 52)
        tembed = discord.Embed(title = "Statistics information", description = "Type `/train` to train!", color = color.random())
        tembed.add_field(name = "Strength <:dumbbell:905773708369612811>", value = "Increases damage dealt in attacks", inline=False)
        tembed.add_field(name = "Defense <:shield:905782766673743922>", value = "Decreases damage when hit in attacks", inline=False)
        tembed.add_field(name = "Speed <:speed:905800074955739147>", value = "Increases chance to hit enemy in attacks", inline=False)
        tembed.add_field(name = "Dexterity <:dodge1:905801069857218622>", value = "Decreases chance to get hit in attacks", inline = False)
        tembed.set_footer(text = "/train to increase your stats!")

        view = interclass.Statistics_select(ctx, ctx.author)
        await ctx.respond(embed=tembed, view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        while True:
          await view.wait()
          if view.value is None:
            return
          elif view.value == "fighting":
            tembed = discord.Embed(title = "Statistics information", description = "Type `/train` to train!", color = color.random())
            tembed.add_field(name = "Strength <:dumbbell:905773708369612811>", value = "Increases damage dealt in attacks", inline=False)
            tembed.add_field(name = "Defense <:shield:905782766673743922>", value = "Decreases damage when hit in attacks", inline=False)
            tembed.add_field(name = "Speed <:speed:905800074955739147>", value = "Increases chance to hit enemy in attacks", inline=False)
            tembed.add_field(name = "Dexterity <:dodge1:905801069857218622>", value = "Decreases chance to get hit in attacks", inline = False)
            tembed.set_footer(text = "/train to increase your stats!")

            view = interclass.Statistics_select(ctx, ctx.author)
            view.message = await msg.edit(embed=tembed, view=view)

          elif view.value == "driving":
            tembed = discord.Embed(title = "Statistics information", description = "Type `/train` to train!", color = color.random())
            tembed.add_field(name = "Accelerating <:accelerating:942699703835979797>", value = "Increases the amount of speed that increases your total speed overtime", inline=False)
            tembed.add_field(name = "Drifting <:drifting:942700424820047903>", value = "Decreases the amount of speed you lose when drifting", inline=False)
            tembed.add_field(name = "Handling <:handling:942699703789830164>", value = "Increases the minimum speed of your car to prevent losing too much speed from drifting", inline=False)
            tembed.add_field(name = "Braking <:braking:942699703492030475>", value = "Decreases crashing chances", inline = False)
            tembed.set_footer(text = "upgrading your skills unlocks titles!")

            view = interclass.Statistics_select(ctx, ctx.author)
            view.message = await msg.edit(embed=tembed, view=view)

          elif view.value == "other":
            tembed = discord.Embed(title = "Statistics information", color = color.random())
            tembed.add_field(name="Intelligence <:intelligence:940955425443024896>", value="Allows you to find a better job!", inline = False)
            tembed.add_field(name="Luck <:luck:940955425308823582>", value="Increases chances of everything", inline = False)
            tembed.add_field(name="Charisma <:charisma:940955424910356491>", value="Increases cash earned in everything", inline = False)
            tembed.set_footer(text = "these stats are more useful than you'd expect")

            view = interclass.Statistics_select(ctx, ctx.author)
            view.message = await msg.edit(embed=tembed, view=view)

      elif info == None:

        img = Image.open(rf"images/gym_bg.png").convert("RGB")

        byte = BytesIO()

        img.save(byte, format="png")

        byte.seek(0)

        file = discord.File(byte, "pic.png")

        userstats = user['stats']
        userstr = userstats['str']
        userdef = userstats['def']
        userspd = userstats['spd']
        userdex = userstats['dex']

        embed = discord.Embed(title="Gym", description="What do you want to train?", color=color.blurple()).set_image(url="attachment://pic.png")
        embed.add_field(name="Strength <:dumbbell:905773708369612811>", value=round(userstr, 2), inline = False)
        embed.add_field(name="Defense <:shield:905782766673743922>", value=round(userdef, 2), inline = False)
        embed.add_field(name="Speed <:speed:905800074955739147>", value=round(userspd, 2), inline = False)
        embed.add_field(name="Dexterity <:dodge1:905801069857218622>", value=round(userdex, 2), inline = False)
        view = interclass.Train(ctx, ctx.author)
        await ctx.respond(embed=embed, view=view, file=file)
        msg = await ctx.interaction.original_response()
        view.message = msg

        userdonor = user['donor']
        userlvl = user['lvl']

        while True:

          await view.wait()

          if view.value is None:
            return
          elif view.value == "fighting":
            img = Image.open(rf"images/gym_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Gym", description="What do you want to train?", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Strength <:dumbbell:905773708369612811>", value=round(userstr, 2), inline = False)
            embed.add_field(name="Defense <:shield:905782766673743922>", value=round(userdef, 2), inline = False)
            embed.add_field(name="Speed <:speed:905800074955739147>", value=round(userspd, 2), inline = False)
            embed.add_field(name="Dexterity <:dodge1:905801069857218622>", value=round(userdex, 2), inline = False)
            view = interclass.Train(ctx, ctx.author)
            view.message = await msg.edit(embed=embed, view=view, file=file)

          elif view.value == "driving":
            img = Image.open(rf"images/driving_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Driving Center", description=f"What do you want to train?\n**Your cash** <:cash:1329017495536930886> {user['cash']}\n**Total races** {user['races']} (1 Race = 1 Max level)", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=userstats['acc'], inline = False)
            embed.add_field(name="Drifting <:drifting:942700424820047903>", value=userstats['dri'], inline = False)
            embed.add_field(name="Handling <:handling:942699703789830164>", value=userstats['han'], inline = False)
            embed.add_field(name="Braking <:braking:942699703492030475>", value=userstats['bra'], inline = False)
            view = interclass.Train2(ctx, ctx.author, user, acc=userstats['acc']>=600, dri=userstats['dri']>=600, han=userstats['han']>=500, bra=userstats['bra']>=100)
            view.message = await msg.edit(embed=embed, view=view, file=file)

          if view.value in ["str", "def", "spd", "dex"]:
            try:
              if user['timer']['train'] > round(time.time()):
                cdembed = discord.Embed(title = "Command on cooldown!", color = color.gold())
                if user['donor'] == True:
                  cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(user['timer']['train']-round(time.time()))}`!\nYou are a Royal member so the cooldown is `{ab(1200)}`")
                else:
                  cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(user['timer']['train']-round(time.time()))}`!\nCooldown for this command is `{ab(1800)}`\nRoyal members have lesser cooldown on some commands!")
                cdembed.set_footer(text = "Chill!")

                await ctx.respond(embed=cdembed)
                return
            except:
              pass

          if view.value == "str":
            if user['s'] == 53:
              await updateset(ctx.author.id, 's', 54)
            if userstr >= userlvl*10:
              await ctx.respond("You have to level up before you can train more!")
              return

            randomstr = round(random.uniform(2.25,5),2)
            userproperty = user['property']
            propertyname = lists.propertyname[userproperty]
            propertyboost = lists.propertyboost[propertyname]
            randomstr = round(randomstr + round(randomstr*propertyboost,2),2)
            if userdonor == 2:
              randomstr = round(randomstr*2,2)
            if (randomstr + userstr) > userlvl*10:
              randomstr = round((userlvl*10) - userstr,2)

            await updateinc(ctx.author.id, 'stats.str', round(randomstr, 2))
            trainembed = discord.Embed(title = "Training", description = f"{random.choice(lists.strength)} and gained {randomstr} Strength <:dumbbell:905773708369612811>", color = color.green())
            trainembed.set_footer(text = "Train more to get stronger!")
            await ctx.respond(embed=trainembed)
            if user['donor'] == True:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1200)
            else:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1800)

            break

          elif view.value == "def":
            if user['s'] == 53:
              await updateset(ctx.author.id, 's', 54)
            if userdef >= userlvl*10:
              await ctx.respond("You have to level up before you can train more!")
              return

            randomstr = round(random.uniform(2.25,5),2)
            userproperty = user['property']
            propertyname = lists.propertyname[userproperty]
            propertyboost = lists.propertyboost[propertyname]
            randomstr = round(randomstr + round(randomstr*propertyboost,2),2)
            if userdonor == 2:
              randomstr = round(randomstr*2,2)
            if (randomstr + userdef) > userlvl*10:
              randomstr = round((userlvl*10) - userdef,2)

            await updateinc(ctx.author.id, 'stats.def', round(randomstr, 2))
            trainembed = discord.Embed(title = "Training", description = f"{random.choice(lists.defense)} and gained {randomstr} Defense <:shield:905782766673743922>", color = color.green())
            trainembed.set_footer(text = "Train more to get stronger!")
            await ctx.respond(embed=trainembed)
            if user['donor'] == True:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1200)
            else:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1800)

            break

          elif view.value == "spd":
            if user['s'] == 53:
              await updateset(ctx.author.id, 's', 54)
            if userspd >= userlvl*10:
              await ctx.respond("You have to level up before you can train more!")
              return

            randomstr = round(random.uniform(2.25,5),2)
            userproperty = user['property']
            propertyname = lists.propertyname[userproperty]
            propertyboost = lists.propertyboost[propertyname]
            randomstr = round(randomstr + round(randomstr*propertyboost,2),2)
            if userdonor == 2:
              randomstr = round(randomstr*2,2)
            if (randomstr + userspd) > userlvl*10:
              randomstr = round((userlvl*10) - userspd,2)

            await updateinc(ctx.author.id, 'stats.spd', round(randomstr, 2))
            trainembed = discord.Embed(title = "Training", description = f"{random.choice(lists.speed)} and gained {randomstr} Speed <:speed:905800074955739147>", color = color.green())
            trainembed.set_footer(text = "Train more to get stronger!")
            await ctx.respond(embed=trainembed)
            if user['donor'] == True:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1200)
            else:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1800)

            break

          elif view.value == "dex":
            if user['s'] == 53:
              await updateset(ctx.author.id, 's', 54)
            if userdex >= userlvl*10:
              await ctx.respond("You have to level up before you can train more!")
              return

            randomstr = round(random.uniform(2.25,5),2)
            userproperty = user['property']
            propertyname = lists.propertyname[userproperty]
            propertyboost = lists.propertyboost[propertyname]
            randomstr = round(randomstr + round(randomstr*propertyboost,2),2)
            if userdonor == 2:
              randomstr = round(randomstr*2,2)
            if (randomstr + userdex) > userlvl*10:
              randomstr = round((userlvl*10) - userdex,2)

            await updateinc(ctx.author.id, 'stats.dex', round(randomstr, 2))
            trainembed = discord.Embed(title = "Training", description = f"{random.choice(lists.dexterity)} and gained {randomstr} Dexterity <:dodge1:905801069857218622>", color = color.green())
            trainembed.set_footer(text = "Train more to get stronger!")
            await ctx.respond(embed=trainembed)
            if user['donor'] == True:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1200)
            else:
              await updateset(ctx.author.id, 'timer.train', round(time.time())+1800)

            break

          elif view.value == "acc":
            if 'races' not in list(user) or user['stats']['acc'] >= user['races']:
              await ctx.respond("You have to race more before training more!")
              return
            if user['cash'] < round((user['stats']['acc']//100*50)+100):
              await ctx.respond("You don't have enough cash")
              return
            acc = 1
            if userdonor == 2:
              acc = 2
            await updateinc(ctx.author.id, 'stats.acc', acc)
            await updateinc(ctx.author.id, 'cash', -round((user['stats']['acc']//100*50)+100))

            user = await finduser(ctx.author.id)
            userstats = user['stats']

            img = Image.open(rf"images/driving_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Driving Center", description=f"What do you want to train?\n**Your cash** <:cash:1329017495536930886> {user['cash']}\n**Total races** {user['races']} (1 Race = 1 Max level)", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=userstats['acc'], inline = False)
            embed.add_field(name="Drifting <:drifting:942700424820047903>", value=userstats['dri'], inline = False)
            embed.add_field(name="Handling <:handling:942699703789830164>", value=userstats['han'], inline = False)
            embed.add_field(name="Braking <:braking:942699703492030475>", value=userstats['bra'], inline = False)

            view = interclass.Train2(ctx, ctx.author, user, acc=userstats['acc']>=600, dri=userstats['dri']>=600, han=userstats['han']>=500, bra=userstats['bra']>=100)
            view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

          elif view.value == "dri":
            if 'races' not in list(user) or user['stats']['dri'] >= user['races']:
              await ctx.respond("You have to race more before training more!")
              return
            if user['cash'] < round((user['stats']['dri']//100*50)+100):
              await ctx.respond("You don't have enough cash")
              return
            dri = 1
            if userdonor == 2:
              dri = 2
            await updateinc(ctx.author.id, 'stats.dri', dri)
            await updateinc(ctx.author.id, 'cash', -round((user['stats']['dri']//100*50)+100))
            
            user = await finduser(ctx.author.id)
            userstats = user['stats']

            img = Image.open(rf"images/driving_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Driving Center", description=f"What do you want to train?\n**Your cash** <:cash:1329017495536930886> {user['cash']}\n**Total races** {user['races']} (1 Race = 1 Max level)", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=userstats['acc'], inline = False)
            embed.add_field(name="Drifting <:drifting:942700424820047903>", value=userstats['dri'], inline = False)
            embed.add_field(name="Handling <:handling:942699703789830164>", value=userstats['han'], inline = False)
            embed.add_field(name="Braking <:braking:942699703492030475>", value=userstats['bra'], inline = False)

            view = interclass.Train2(ctx, ctx.author, user, acc=userstats['acc']>=600, dri=userstats['dri']>=600, han=userstats['han']>=500, bra=userstats['bra']>=100)
            view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

          elif view.value == "han":
            if 'races' not in list(user) or user['stats']['han'] >= user['races']:
              await ctx.respond("You have to race more before training more!")
              return
            if user['cash'] < round((user['stats']['han']//100*50)+100):
              await ctx.respond("You don't have enough cash")
              return
            han = 1
            if userdonor == 2:
              han = 2
            await updateinc(ctx.author.id, 'stats.han', han)
            await updateinc(ctx.author.id, 'cash', -round((user['stats']['han']//100*50)+100))
            
            user = await finduser(ctx.author.id)
            userstats = user['stats']

            img = Image.open(rf"images/driving_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Driving Center", description=f"What do you want to train?\n**Your cash** <:cash:1329017495536930886> {user['cash']}\n**Total races** {user['races']} (1 Race = 1 Max level)", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=userstats['acc'], inline = False)
            embed.add_field(name="Drifting <:drifting:942700424820047903>", value=userstats['dri'], inline = False)
            embed.add_field(name="Handling <:handling:942699703789830164>", value=userstats['han'], inline = False)
            embed.add_field(name="Braking <:braking:942699703492030475>", value=userstats['bra'], inline = False)

            view = interclass.Train2(ctx, ctx.author, user, acc=userstats['acc']>=600, dri=userstats['dri']>=600, han=userstats['han']>=500, bra=userstats['bra']>=100)
            view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

          elif view.value == "bra":
            if 'races' not in list(user) or user['stats']['bra'] >= user['races']:
              await ctx.respond("You have to race more before training more!")
              return
            if user['cash'] < 100:
              await ctx.respond("You don't have enough cash")
              return
            bra = 1
            if userdonor == 2:
              bra = 2
            await updateinc(ctx.author.id, 'stats.bra', bra)
            await updateinc(ctx.author.id, 'cash', -100)
            
            user = await finduser(ctx.author.id)
            userstats = user['stats']

            img = Image.open(rf"images/driving_bg.png").convert("RGB")

            byte = BytesIO()

            img.save(byte, format="png")

            byte.seek(0)

            file = discord.File(byte, "pic.png")
            embed = discord.Embed(title="Driving Center", description=f"What do you want to train?\n**Your cash** <:cash:1329017495536930886> {user['cash']}\n**Total races** {user['races']} (1 Race = 1 Max level)", color=color.blurple()).set_image(url="attachment://pic.png")
            embed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=userstats['acc'], inline = False)
            embed.add_field(name="Drifting <:drifting:942700424820047903>", value=userstats['dri'], inline = False)
            embed.add_field(name="Handling <:handling:942699703789830164>", value=userstats['han'], inline = False)
            embed.add_field(name="Braking <:braking:942699703492030475>", value=userstats['bra'], inline = False)

            view = interclass.Train2(ctx, ctx.author, user, acc=userstats['acc']>=600, dri=userstats['dri']>=600, han=userstats['han']>=500, bra=userstats['bra']>=100)
            view.message = await msg.edit(embed=embed, view=view, file=file, attachments=[])

async def statistics(self, ctx, user):
      if await blocked(ctx.author.id) == False:
        return
      if user == None:
        user = ctx.author
      if await finduser(user.id) == None:
        await ctx.respond("The user haven't started playing OV Bot yet")
        return

      userp = await finduser(user.id)

      if userp['s'] == 49:
        await updateset(ctx.author.id, 's', 50)

      userstats = userp['stats']
      userstr = round(userstats['str'],2)
      userdef = round(userstats['def'],2)
      userspd = round(userstats['spd'],2)
      userdex = round(userstats['dex'],2)
      gymembed = discord.Embed(title = f"{gettitle(userp)}{user.name}", description = "**Fighting statistics**", color = color.random())
      gymembed.add_field(name="Strength <:dumbbell:905773708369612811>", value=userstr, inline = False)
      gymembed.add_field(name="Defense <:shield:905782766673743922>", value=userdef, inline = False)
      gymembed.add_field(name="Speed <:speed:905800074955739147>", value=userspd, inline = False)
      gymembed.add_field(name="Dexterity <:dodge1:905801069857218622>", value=userdex, inline = False)
      gymembed.set_footer(text = "weak weak")

      view = interclass.Statistics_select(ctx, ctx.author)
      await ctx.respond(embed=gymembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "fighting":
          userp = await finduser(user.id)
          userstats = userp['stats']
          userstr = round(userstats['str'],2)
          userdef = round(userstats['def'],2)
          userspd = round(userstats['spd'],2)
          userdex = round(userstats['dex'],2)
          gymembed = discord.Embed(title = f"{gettitle(userp)}{user.name}", description = "**Fighting statistics**", color = color.random())
          gymembed.add_field(name="Strength <:dumbbell:905773708369612811>", value=userstr, inline = False)
          gymembed.add_field(name="Defense <:shield:905782766673743922>", value=userdef, inline = False)
          gymembed.add_field(name="Speed <:speed:905800074955739147>", value=userspd, inline = False)
          gymembed.add_field(name="Dexterity <:dodge1:905801069857218622>", value=userdex, inline = False)
          gymembed.set_footer(text = "weak weak")

          view = interclass.Statistics_select(ctx, ctx.author)
          view.message = await msg.edit(embed=gymembed, view=view)

        elif view.value == "driving":
          userp = await finduser(user.id)
          userstats = userp['stats']
          useracc = round(userstats['acc'],2)
          userdri = round(userstats['dri'],2)
          userhan = round(userstats['han'],2)
          userbra = round(userstats['bra'],2)
          gymembed = discord.Embed(title = f"{gettitle(userp)}{user.name}", description = "**Driving statistics**", color = color.random())
          gymembed.add_field(name="Accelerating <:accelerating:942699703835979797>", value=useracc, inline = False)
          gymembed.add_field(name="Drifting <:drifting:942700424820047903>", value=userdri, inline = False)
          gymembed.add_field(name="Handling <:handling:942699703789830164>", value=userhan, inline = False)
          gymembed.add_field(name="Braking <:braking:942699703492030475>", value=userbra, inline = False)
          if sum([useracc, userdri, userhan, userbra]) < 120:
            gymembed.set_footer(text = "rookie driver")
          elif sum([useracc, userdri, userhan, userbra]) < 200:
            gymembed.set_footer(text = "average driver")
          elif sum([useracc, userdri, userhan, userbra]) < 500:
            gymembed.set_footer(text = "veteran driver")
          elif sum([useracc, userdri, userhan, userbra]) < 1000:
            gymembed.set_footer(text = "racer")
          elif sum([useracc, userdri, userhan, userbra]) < 1800:
            gymembed.set_footer(text = "professional racer")
          elif sum([useracc, userdri, userhan, userbra]) >= 1800:
            gymembed.set_footer(text = "legendary racer")

          view = interclass.Statistics_select(ctx, ctx.author)
          view.message = await msg.edit(embed=gymembed, view=view)

        elif view.value == "other":
          userp = await finduser(user.id)
          userstats = userp['stats']
          gymembed = discord.Embed(title = f"{gettitle(userp)}{user.name}", description = "**Other statistics**", color = color.random())
          gymembed.add_field(name="Intelligence <:intelligence:940955425443024896>", value=userstats['int'], inline = False)

          luck = round(getluck(userp)*1000)
          boostp = 0
          boosta = 0
          if userp['drugs']['cannabis'] > 0:
            boostp += userp['drugs']['cannabis']
          if userp['donor'] == 2:
            boostp += 50
          elif userp['donor'] == 1:
           boostp += 20

          if 'cboost' in userp['timer']:
            boosta += 50

          if "Lucky Clover" in userp['storage']:
              boostp += userp['storage']['Lucky Clover']

          b = ''
          if boosta != 0 and boostp == 0:
            b = f" (Boost: +{boosta})"
          elif boosta == 0 and boostp != 0:
            b = f" (Boost: +{boostp}%)"
          elif boosta != 0 and boostp != 0:
            b = f" (Boost: +{boosta} & +{boostp}%)"

          gymembed.add_field(name="Luck <:luck:940955425308823582>", value=f"{luck}{b}", inline = False)

          charisma = round(getcha(userp)*1000)
          boostp = 0
          if userp['drugs']['ecstasy'] > 0:
            boostp += (userp['drugs']['ecstasy'] * 5)

          if userp['donor'] == 2:
            boostp += 100
          elif userp['donor'] == 1:
            boostp += 50

          b = ''
          if boostp != 0:
            b = f" (Boost: +{boostp}%)"

          gymembed.add_field(name="Charisma <:charisma:940955424910356491>", value=f"{charisma}{b}", inline = False)
          gymembed.set_footer(text = "so weak")

          view = interclass.Statistics_select(ctx, ctx.author)
          view.message = await msg.edit(embed=gymembed, view=view)

async def buy(self, ctx, item, amount):
      if await blocked(ctx.author.id) == False:
        return
      if item == None:
        await ctx.respond("What are you buying??")
        return
      user = await finduser(ctx.author.id)
      if 'racing' in list(user) and user['racing']:
        await ctx.respond("You are currently racing! You cannot buy anything")
        return
      usercash = user['cash']
      item = item.lower()
      try:
          if len(item) == 0:
            raise Exception
          if len(item) < 2:
            await ctx.respond("Enter at least 2 letters to search")
            return
          closematch = [x for x in lists.bitem if item in x.lower() or item in x.lower().replace(" ","")]
          if len(closematch) > 1:
            await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
            return
          else:
            item = closematch[0]
      except:
          await ctx.respond("Cannot find this item, check if you spelled it correctly!")
          return

      if amount == 0:
        await ctx.respond("Imagine buying nothing")
        return
      elif amount < 0:
        await ctx.respond("You thought you are funny?")
        return

      if item in lists.bitem and not item in lists.drug:
        price = round(lists.item_prices[item] * amount)
        cost = -abs(price)

        if item in lists.titem:
          if user['token'] < price:
            await ctx.respond("You don't even have enough tokens too afford that poor guy")
            return

          await updateinc(ctx.author.id, 'token', cost)
          await updateinc(ctx.author.id, f'storage.{item}', amount)

          await ctx.respond(f"You bought {aa(amount)} {item} for {aa(price)} <:token:1313166204348792853>!")
        else:
          if usercash < price:
            await ctx.respond("You don't even have enough cash too afford that poor guy")
            return

          if user['s'] == 32:
            await updateset(ctx.author.id, 's', 33)
          
          await updateinc(ctx.author.id, 'cash', cost)
          await updateinc(ctx.author.id, f'storage.{item}', amount)

          await ctx.respond(f"You bought {aa(amount)} {item} for <:cash:1329017495536930886> {aa(price)}!")
      elif item in lists.drug:
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        try:
          userdrugq = userstorage[item]
          if userdrugq >= 50:
            await ctx.respond("You can only have 50 of the same drug!")
            return
          if amount >= 50 - userdrugq:
            amount = 50 - userdrugq
        except:
          pass
        if amount > 50:
            amount = 50
        usercash = user['cash']
        city = await self.bot.bm.find_one({"city": user['location']})
        citydrugs = city['drugs']
        price = round(citydrugs[item] * amount)
        cost = -abs(price)

        if usercash < price:
          await ctx.respond("You don't even have enough cash too afford that poor guy")
          return

        await updateinc(ctx.author.id, 'cash', cost)
        await updateinc(ctx.author.id, f'storage.{item}', amount)

        await ctx.respond(f"You bought {aa(amount)} {item} for <:cash:1329017495536930886> {aa(price)}!")

async def sell(self, ctx, item, amount):
      if await blocked(ctx.author.id) == False:
        return 
      if item == None:
        await ctx.respond("You wanna sell nothing??")
        return 
      user = await finduser(ctx.author.id)
      userstorage = user['storage']
      userstoragelist = sorted(list(user['storage']))
      if len(item) == 0:
        raise Exception
      try:
        if len(item) < 2:
          await ctx.respond("Enter at least 2 letters to search")
          return
        closematch = [x for x in userstoragelist if item in x.lower() or item in x.lower().replace(" ","")]
        if len(closematch) > 1:
          await ctx.respond(f"I found more than one item that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
          return
        else:
          item = closematch[0]
      except:
        await ctx.respond("You don't have this item in your storage")
        return

      if item not in list(lists.item_prices) or item in lists.titem:
        await ctx.respond("This item cannot be sold!")
        return

      if amount == 0:
        await ctx.respond("Imagine selling nothing")
        return
      elif amount < 0:
        await ctx.respond("Imagine thinking it will work")
        return

      if item in lists.bitem and not item in lists.drug:
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if amount > userstorageitemq:
          await ctx.respond("You don't have that much item in your storage!")
          return
        price = round(((lists.item_prices[item]*0.5) * amount))

        await updateinc(ctx.author.id, 'cash', price)
        await updateinc(ctx.author.id, f'storage.{item}', -amount)
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if userstorageitemq == 0:
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.{item}': 1}})
        user = await finduser(ctx.author.id)
        userstoragelist = list(user['storage'])
        userweapon = user['equipments']['weapon']
        if not userweapon in userstoragelist:
          await updateset(ctx.author.id,'equipments.weapon','')
        await ctx.respond(f"You sold your {amount} {item} for <:cash:1329017495536930886> {aa(price)}!")
      elif (item not in lists.weapon or item not in lists.melee) and not item in lists.drug:
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if amount > userstorageitemq:
          await ctx.respond("You don't have that much item in your storage!")
          return
        price = round(((lists.item_prices[item]) * amount))

        await updateinc(ctx.author.id, 'cash', price)
        await updateinc(ctx.author.id, f'storage.{item}', -amount)
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if userstorageitemq == 0:
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.{item}': 1}})
        await ctx.respond(f"You sold your {amount} {item} for <:cash:1329017495536930886> {aa(price)}!")
      elif item in lists.drug:
        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if amount > userstorageitemq:
          await ctx.respond("You don't have that much item in your storage!")
          return
        userlocation = user['location']
        city = await self.bot.bm.find_one({"city": userlocation})
        citydrugs = city['drugs']
        price = round(citydrugs[item] * amount)

        await updateinc(ctx.author.id, 'cash', price)
        await updateinc(ctx.author.id, f'storage.{item}', -amount)

        user = await finduser(ctx.author.id)
        userstorage = user['storage']
        userstorageitemq = userstorage[item]
        if userstorageitemq == 0:
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$unset": {f'storage.{item}': 1}})
        await ctx.respond(f"You sold your {amount} {item} for <:cash:1329017495536930886> {aa(price)}!")

async def casino(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      csnembed = discord.Embed(title="Casino",description="Different games you can play!",color=color.blue())
      csnembed.add_field(name="Russian Roulette",value="Singleplayer: `/roulette <bullet> <bet>`\nDuo: `/roulette <user> <bet>`\nGive a bullet count 1-6, more bullet higher prizes but higher chance to lose",inline=False)
      csnembed.add_field(name="Blackjack",value="`/blackjack <bet>`\nWhoever gets 21 wins, `/blackjack rules` for more information",inline=False)
      csnembed.add_field(name="HighLow",value="`/highlow <bet>`\nGuess if your card is higher or lower than the dealer's",inline=False)
      csnembed.add_field(name="Slots",value="`/slot <bet>`\nSpin the slot machine!",inline=False)
      csnembed.set_footer(text="hope that you don't have gambling addicts")
      await ctx.respond(embed=csnembed)

async def roulette(self, ctx, bullet, bet):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      if bullet == None:
        await ctx.respond("You have to give a bullet count 1-6\nIf you want to versus someone then mention the user")
        ctx.command.reset_cooldown(ctx)
        return
      if bet == None:
        await ctx.respond("You have to give a bet!")
        ctx.command.reset_cooldown(ctx)
        return
      vs = False
      try:
        member = await commands.MemberConverter().convert(ctx, bullet)
        vs = True
      except:
        pass
      if vs == False:
        try:
          bullet = int(bullet)
        except:
          await ctx.respond("Give a valid amount of bullet!")
          return
          ctx.command.reset_cooldown(ctx)
        try:
          bet = int(bet)
        except:
          if not bet == 'max':
            await ctx.respond("Give a valid amount of bet!")
            ctx.command.reset_cooldown(ctx)
            return
          pass
        if bullet <= 0 or bullet > 6:
          await ctx.respond("You can only give a bullet count from 1 to 6")
          ctx.command.reset_cooldown(ctx)
          return
        user = await finduser(ctx.author.id)
        usercash = user['cash']
        try:
          if bet.lower() == 'max':
            bet = math.floor(usercash)
            if bet > 5000:
              bet = 5000
        except:
          pass
        if usercash < bet:
          await ctx.respond("You don't even have enough cash poor guy")
          ctx.command.reset_cooldown(ctx)
          return
        if bet > 5000:
          await ctx.respond("You cannot bet more than <:cash:1329017495536930886> 5000!")
          ctx.command.reset_cooldown(ctx)
          return
        if bet < 10:
          await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10!")
          ctx.command.reset_cooldown(ctx)
          return
        await ctx.respond(f"You loaded {bullet} bullet into the revolver...")
        msg = await ctx.interaction.original_response()
        randomchance = random.randint(1,6)
        randomchance2 = random.random()
        if bullet == 3:
          if randomchance2 <= 0.15:
            randomchance = 0
        if bullet == 6:
          if randomchance2 <= 0.05:
            bullet = str(bullet)
            await updateinc(ctx.author.id, 'cash', round((bet*lists.rrprize[bullet])-bet))
            await asyncio.sleep(2)
            user = await finduser(ctx.author.id)
            usercash = user['cash']
            luck = random.randint(1, 10)
            if luck == 1 and user['stats']['luk'] < 500:
              await updateinc(ctx.author.id, 'stats.luk', 1)
              await msg.edit(content=f"You pulled the trigger but the gun jammed! You won <:cash:1329017495536930886> {round((bet*lists.rrprize[str(bullet)])-bet)} (x{round(lists.rrprize[bullet]-1,2)}) and gained 1 Luck <:luck:940955425308823582>!\nYou currently have <:cash:1329017495536930886> {round(usercash)} cash left")
            else:
              await msg.edit(content=f"You pulled the trigger but the gun jammed! You won <:cash:1329017495536930886> {round((bet*lists.rrprize[str(bullet)])-bet)} (x{round(lists.rrprize[bullet]-1,2)})!\nYou currently have <:cash:1329017495536930886> {round(usercash)} cash left")
            return
        if randomchance <= bullet:
          await updateinc(ctx.author.id, 'cash', -bet)
          await asyncio.sleep(2)
          user = await finduser(ctx.author.id)
          usercash = user['cash']
          await msg.edit(content=f"You pulled the trigger and BANG! You lost <:cash:1329017495536930886> {bet}\nYou currently have <:cash:1329017495536930886> {round(usercash)} cash left")
        else:
          bullet = str(bullet)
          await updateinc(ctx.author.id, 'cash', round((bet*lists.rrprize[bullet])-bet))
          await asyncio.sleep(2)
          user = await finduser(ctx.author.id)
          usercash = user['cash']
          luck = random.randint(1, 10)
          if luck == 1 and user['stats']['luk'] < 500:
            await updateinc(ctx.author.id, 'stats.luk', 1)
            await msg.edit(content=f"You pulled the trigger and nothing happens! You won <:cash:1329017495536930886> {round((bet*lists.rrprize[str(bullet)])-bet)} (x{round(lists.rrprize[bullet]-1,2)}) and gained 1 Luck <:luck:940955425308823582>!\nYou currently have <:cash:1329017495536930886> {round(usercash)} cash left")
          else:
            await msg.edit(content=f"You pulled the trigger and nothing happens! You won <:cash:1329017495536930886> {round((bet*lists.rrprize[str(bullet)])-bet)} (x{round(lists.rrprize[bullet]-1,2)})!\nYou currently have <:cash:1329017495536930886> {round(usercash)} cash left")
      elif vs == True:
        try:
          bet = int(bet)
        except:
          if not bet == 'max':
            await ctx.respond("Give a valid amount of bet!")
            ctx.command.reset_cooldown(ctx)
            return
          pass
        user = await finduser(ctx.author.id)
        usercash = user['cash']
        try:
          if bet.lower() == 'max':
            bet = math.floor(usercash)
            if bet > 5000:
              bet = 5000
        except:
          pass
        if bet <= 0:
          await ctx.respond("You have to give a valid amount of bet")
          ctx.command.reset_cooldown(ctx)
          return
        if usercash < bet:
          await ctx.respond("You don't even have enough cash poor guy")
          ctx.command.reset_cooldown(ctx)
          return
        target = await finduser(member.id)
        if target is None:
          await ctx.respond("The user haven't started playing OV Bot yet")
          ctx.command.reset_cooldown(ctx)
          return
        if member == ctx.author:
          await ctx.respond("You can't play with yourself")
          ctx.command.reset_cooldown(ctx)
          return

        if target['cash'] < bet:
          await ctx.respond("The user doesn't even have enough cash to play with you")
          ctx.command.reset_cooldown(ctx)
          return
        if target['injail'] == True:
          await ctx.respond("The user is in Jail!")
          ctx.command.reset_cooldown(ctx)
          return
        elif target['inhosp'] == True:
          await ctx.respond("The user is in Hospital!")
          ctx.command.reset_cooldown(ctx)
          return
        if bet > 5000:
          await ctx.respond("You cannot bet more than <:cash:1329017495536930886> 5000!")
          ctx.command.reset_cooldown(ctx)
          return
        if bet < 10:
          await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10!")
          ctx.command.reset_cooldown(ctx)
          return

        view = interclass.Confirm(ctx, member)
        await ctx.respond(f"{target['title']}{member.mention}, {ctx.author.mention} challenged you to a <:cash:1329017495536930886> {bet} bet Russian Roulette!", view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        await view.wait()

        if view.value is None:
            await ctx.respond(f"{target['title']}{member.mention} ignored {ctx.author.mention} wow")
            ctx.command.reset_cooldown(ctx)
            return
        elif view.value is False:
            await ctx.respond(f"{target['title']}{member.mention} is too afraid to accept {ctx.author.mention}'s challenge")
            ctx.command.reset_cooldown(ctx)
            return

        msg = await ctx.respond(f"Russian Roulette battle {gettitle(user)}{ctx.author} against {target['title']}{member} is starting!")
        bullet = 0
        while True:
          bullet += 1
          await asyncio.sleep(2)
          await msg.edit(content=f"{gettitle(user)}{ctx.author} loaded {bullet} bullet into the revolver")
          randomchance = random.randint(1,6)
          randomchance2 = random.random()
          if randomchance <= bullet:
            await updateinc(ctx.author.id, 'cash', -bet)
            await updateinc(member.id, 'cash', round(bet*0.95))
            await asyncio.sleep(2)
            await msg.edit(content=f"{gettitle(user)}{ctx.author} pulled the trigger and BANG! {gettitle(user)}{ctx.author} lost <:cash:1329017495536930886> {bet} against {target['title']}{member}")
            return
          else:
            await asyncio.sleep(2)
            await msg.edit(content=f"{gettitle(user)}{ctx.author} pulled the trigger and nothing happens! Its now {target['title']}{member}'s turn")

          bullet += 1
          await asyncio.sleep(2)
          await msg.edit(content=f"{target['title']}{member} loaded {bullet} bullet into the revolver")
          randomchance = random.randint(1,6)
          randomchance2 = random.random()
          if randomchance <= bullet:
            await updateinc(member.id, 'cash', -bet)
            await updateinc(ctx.author.id, 'cash', round(bet*0.95))
            await asyncio.sleep(2)
            await msg.edit(content=f"{target['title']}{member} pulled the trigger and BANG! {target['title']}{member} lost <:cash:1329017495536930886> {bet} against {gettitle(user)}{ctx.author}")
            return
          else:
            await asyncio.sleep(2)
            await msg.edit(content=f"{target['title']}{member} pulled the trigger and nothing happens! Its now {gettitle(user)}{ctx.author}'s turn")

async def blackjack(self, ctx, bet, user2):
        if await blocked(ctx.author.id) == False:
            ctx.command.reset_cooldown(ctx)
            return
        if bet == None:
            await ctx.respond("You have to give a bet!")
            ctx.command.reset_cooldown(ctx)
            return
        try:
            bet = bet.lower()
        except:
            pass
        if bet == 'rules' or bet == 'r':
            bjr = discord.Embed(title="Blackjack Rules",description="**How to win?**\n❧ Keep hitting cards until you reach a total card value of 21 or higher than the dealer's total card value\n❧ The dealer's total card value will be unknown\n❧ You will lose when your total card value is lower than the dealer's total card value or your total card value is over 21\n❧ You will win instantly if you have 21 at the beginning", color=color.blurple())
            bjr.add_field(name="Hit",value="Ask for a card",inline=False)
            bjr.add_field(name="Stand",value="Stop asking cards, opponent's turn",inline=False)
            bjr.add_field(name="Double",value="Doubles your current bet, and automatically draws a card after before standing. Only available on your first turn if you have enough cash and current bet is equal or below <:cash:1329017495536930886> 2500",inline=False)
            bjr.add_field(name="Insurance",value="Only available if the dealer's open card is an 'A', you will remove half of your bet. Only available on your first turn")

            await ctx.respond(embed=bjr)
            return
        try:
            bet = int(bet)
        except:
            if not bet == 'max' and not bet == 'all':
                await ctx.respond("Give a valid amount of bet!")
                ctx.command.reset_cooldown(ctx)
                return
            pass
        user = await finduser(ctx.author.id)
        if bet == 'max' or bet == 'all':
            bet = math.floor(user['cash'])
        if user2 is None and bet > 5000 and ctx.author.id != 615037304616255491:
            bet = 5000
        if bet <= 0:
            await ctx.respond("You have to give a valid amount of bet")
            ctx.command.reset_cooldown(ctx)
            return
        if user['cash'] < bet:
            await ctx.respond("You don't even have enough cash poor guy")
            ctx.command.reset_cooldown(ctx)
            return
        if bet < 10:
            await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10!")
            ctx.command.reset_cooldown(ctx)
            return
        if user['lvl'] < 5:
            await ctx.respond("You have to be at least level 5 to play Blackjack!")
            ctx.command.reset_cooldown(ctx)
            return

        if user2 is None:
            await updateinc(ctx.author.id,'cash',-bet)
            await updateset(ctx.author.id, 'blocked', True)
            shuffled = random.sample(lists.cards, len(lists.cards))
            usercard = []
            dealercard = []
            for x in range(2):
                uservalue = 0
                card = random.choice(shuffled)
                while card in usercard or card in dealercard:
                    card = random.choice(shuffled)
                usercard.append(card)
                for c in usercard:
                    uservalue += lists.cardvalue[c]
                for c in usercard:
                    if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and uservalue > 21:
                        uservalue -= 10
            for x in range(2):
                dealervalue = 0
                drcard = random.choice(shuffled)
                while drcard in usercard or drcard in dealercard:
                    drcard = random.choice(shuffled)
                dealercard.append(drcard)
                for c in dealercard:
                    dealervalue += lists.cardvalue[c]
                for c in dealercard:
                    if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and dealervalue > 21:
                        dealervalue -= 10

            if uservalue == 21 and not dealervalue == 21:
                await updateinc(ctx.author.id,'cash',(bet*2)+round(bet/2)+round(bet*(user['stats']['cha']/1000/5)))
                luck = random.randint(1, 10)
                if luck == 1 and user['stats']['luk'] < 500:
                  await updateinc(ctx.author.id, 'stats.luk', 1)
                  bjembed = discord.Embed(title="Blackjack",description=f"You had a Blackjack! You won <:cash:1329017495536930886> {(bet)+(round(bet/2))+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                else:
                  bjembed = discord.Embed(title="Blackjack",description=f"You had a Blackjack! You won <:cash:1329017495536930886> {(bet)+(round(bet/2))+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await ctx.respond(embed=bjembed)
                await updateset(ctx.author.id, 'blocked', False)
                return
            elif uservalue == 21 and dealervalue == 21:
                await updateinc(ctx.author.id,'cash',bet)
                bjembed = discord.Embed(title="Blackjack",description=f"Push! No one won\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await ctx.respond(embed=bjembed)
                await updateset(ctx.author.id, 'blocked', False)
                return

            dcard = dealercard.copy()
            dcard[1] = "??"
            rounds = 0
            view = None
            msg = None
            if user['cash'] >= bet*2 and bet <= 2500:
                if dealercard[0] in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A']:
                    view = interclass.Blackjack(ctx, "di")
                    bjembed = discord.Embed(title="Blackjack",description=f"Bet: <:cash:1329017495536930886> {bet}",color=color.blue())
                else:
                    view = interclass.Blackjack(ctx, "d")
                    bjembed = discord.Embed(title="Blackjack",description=f"Bet: <:cash:1329017495536930886> {bet}",color=color.blue())
            else:
                if dealercard[0] in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A']:
                    view = interclass.Blackjack(ctx, "i")
                    bjembed = discord.Embed(title="Blackjack",description=f"Bet: <:cash:1329017495536930886> {bet}",color=color.blue())
                else:
                    view = interclass.Blackjack(ctx, "n")
                    bjembed = discord.Embed(title="Blackjack",description=f"Bet: <:cash:1329017495536930886> {bet}",color=color.blue())
            bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
            bjembed.add_field(name="Dealer's cards",value=f"`??` " + ", ".join(dcard),inline=True)
            bjembed.set_footer(text="'/blackjack rules' to read the rules!")
            await ctx.respond(embed=bjembed, view=view)
            msg = await ctx.interaction.original_response()
            view.message = msg
            while True:
                if rounds != 0:
                    view = interclass.Blackjack(ctx, "n")
                    view.message = await msg.edit(view=view)
                rounds += 1
                
                await view.wait()
                await asyncio.sleep(0.1)
                
                if view.value is None:
                    await ctx.respond(f"You took too long to response, the dealer took your bet away")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                elif view.value == "r":
                    await ctx.respond(f"You ran away leaving your bet, what a coward")
                    await updateset(ctx.author.id, 'blocked', False)
                    return
                elif view.value == "d":
                    await updateinc(ctx.author.id,'cash',-bet)
                    bet *= 2
                    card = random.choice(shuffled)
                    while card in usercard or card in dealercard:
                        card = random.choice(shuffled)
                    usercard.append(card)
                    uservalue = 0
                    for c in usercard:
                        uservalue += lists.cardvalue[c]
                    for c in usercard:
                        if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and uservalue > 21:
                            uservalue -= 10
     
                    if uservalue > 21:
                        bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}! You busted and lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    if dealervalue == 21:
                        bjembed = discord.Embed(title="Blackjack",description=f"You doubled your bet and got a {card}!\nYou had {uservalue} but the dealer had blackjack! You lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    while dealervalue < 17:
                        drcard = random.choice(shuffled)
                        while drcard in usercard or drcard in dealercard:
                            drcard = random.choice(shuffled)
                        dealercard.append(drcard)
                        dealervalue = 0
                        for c in dealercard:
                            dealervalue += lists.cardvalue[c]
                        for c in dealercard:
                            if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and dealervalue > 21:
                                dealervalue -= 10
                    if dealervalue > 21:
                        await updateinc(ctx.author.id,'cash', bet*2+round(bet*(user['stats']['cha']/1000/5)))
                        luck = random.randint(1, 10)
                        if luck == 1 and user['stats']['luk'] < 500:
                          await updateinc(ctx.author.id, 'stats.luk', 1)
                          bjembed = discord.Embed(title="Blackjack",description=f"The dealer busted! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        else:
                          bjembed = discord.Embed(title="Blackjack",description=f"The dealer busted! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    if dealervalue > uservalue:
                        bjembed = discord.Embed(title="Blackjack",description=f"You doubled your bet and got a {card}!\nYou had {uservalue} and the dealer had {dealervalue}! You lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    elif dealervalue < uservalue:
                        await updateinc(ctx.author.id,'cash',bet*2+round(bet*(user['stats']['cha']/1000/5)))
                        luck = random.randint(1, 10)
                        if luck == 1 and user['stats']['luk'] < 500:
                          await updateinc(ctx.author.id, 'stats.luk', 1)
                          bjembed = discord.Embed(title="Blackjack",description=f"You doubled your bet and got a {card}!\nYou had {uservalue} and the dealer had {dealervalue}! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        else:
                          bjembed = discord.Embed(title="Blackjack",description=f"You doubled your bet and got a {card}!\nYou had {uservalue} and the dealer had {dealervalue}! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    elif dealervalue == uservalue:
                        await updateinc(ctx.author.id,'cash',bet)
                        bjembed = discord.Embed(title="Blackjack",description=f"You doubled your bet and got a {card}!\nPush! No one won\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                elif view.value == "i":
                    await updateinc(ctx.author.id,'cash',round(bet/2))
                    bet = round(bet/2)
                    if not dealervalue == 21:
                        bjembed = discord.Embed(title="Blackjack",description=f"You insured but the dealer does not have a Blackjack!\nBet: <:cash:1329017495536930886> {bet}",color=color.blue())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`??` " + ", ".join(dcard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                    else:
                        bjembed = discord.Embed(title="Blackjack",description=f"You insured and the dealer had a Blackjack! You lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                elif view.value == "h":
                    card = random.choice(shuffled)
                    while card in usercard or card in dealercard:
                        card = random.choice(shuffled)
                    usercard.append(card)
                    uservalue = 0
                    for c in usercard:
                        uservalue += lists.cardvalue[c]
                    for c in usercard:
                        if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and uservalue > 21:
                            uservalue -= 10
                    if uservalue > 21:
                        bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}! You busted and lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    if uservalue == 21:
                        while dealervalue < 17:
                            drcard = random.choice(shuffled)
                            while drcard in usercard or drcard in dealercard:
                                drcard = random.choice(shuffled)
                            dealercard.append(drcard)
                            dealervalue = 0
                            for c in dealercard:
                                dealervalue += lists.cardvalue[c]
                            for c in dealercard:
                                if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and dealervalue > 21:
                                    dealervalue -= 10
                        if not dealervalue == 21:
                            await updateinc(ctx.author.id,'cash',bet*2+round(bet*(user['stats']['cha']/1000/5)))
                            luck = random.randint(1, 10)
                            if luck == 1 and user['stats']['luk'] < 500:
                              await updateinc(ctx.author.id, 'stats.luk', 1)
                              bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}! You had 21 and won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                            else:
                              bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}! You had 21 and won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                            bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                            bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                            bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                            await msg.edit(embed=bjembed, view=None)
                            await updateset(ctx.author.id, 'blocked', False)
                            return
                        elif dealervalue == 21:
                            await updateinc(ctx.author.id,'cash',bet)
                            bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}!\nPush! You and the dealer had 21!\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                            bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                            bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                            bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                            await msg.edit(embed=bjembed, view=None)
                            await updateset(ctx.author.id, 'blocked', False)
                            return
                    bjembed = discord.Embed(title="Blackjack",description=f"You hit a card and got {card}!\nBet: <:cash:1329017495536930886> {bet}",color=color.blue())
                    bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                    bjembed.add_field(name="Dealer's cards",value=f"`??` " + ", ".join(dcard),inline=True)
                    bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                    await msg.edit(embed=bjembed)
                elif view.value == "s":
                    if dealervalue == 21:
                        bjembed = discord.Embed(title="Blackjack",description=f"You had {uservalue} but the dealer had blackjack! You lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    while dealervalue < 17:
                        drcard = random.choice(shuffled)
                        while drcard in usercard or drcard in dealercard:
                            drcard = random.choice(shuffled)
                        dealercard.append(drcard)
                        dealervalue = 0
                        for c in dealercard:
                            dealervalue += lists.cardvalue[c]
                        for c in dealercard:
                            if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and dealervalue > 21:
                                dealervalue -= 10
                    if dealervalue > 21:
                        await updateinc(ctx.author.id,'cash', bet*2+round(bet*(user['stats']['cha']/1000/5)))
                        luck = random.randint(1, 10)
                        if luck == 1 and user['stats']['luk'] < 500:
                          await updateinc(ctx.author.id, 'stats.luk', 1)
                          bjembed = discord.Embed(title="Blackjack",description=f"The dealer busted! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        else:
                          bjembed = discord.Embed(title="Blackjack",description=f"The dealer busted! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    if dealervalue > uservalue:
                        bjembed = discord.Embed(title="Blackjack",description=f"You had {uservalue} and the dealer had {dealervalue}! You lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.red())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    elif dealervalue < uservalue:
                        await updateinc(ctx.author.id,'cash',bet*2+round(bet*(user['stats']['cha']/1000/5)))
                        luck = random.randint(1, 10)
                        if luck == 1 and user['stats']['luk'] < 500:
                          await updateinc(ctx.author.id, 'stats.luk', 1)
                          bjembed = discord.Embed(title="Blackjack",description=f"You had {uservalue} and the dealer had {dealervalue}! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))} and gained 1 Luck <:luck:940955425308823582>!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        else:
                          bjembed = discord.Embed(title="Blackjack",description=f"You had {uservalue} and the dealer had {dealervalue}! You won <:cash:1329017495536930886> {bet+round(bet*(user['stats']['cha']/1000/5))}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
                    elif dealervalue == uservalue:
                        await updateinc(ctx.author.id,'cash',bet)
                        bjembed = discord.Embed(title="Blackjack",description=f"Push! No one won\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                        bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                        bjembed.add_field(name="Dealer's cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                        bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                        await msg.edit(embed=bjembed, view=None)
                        await updateset(ctx.author.id, 'blocked', False)
                        return
        elif user2 != None:
            usert = await finduser(user2.id)

            if usert is None:
              await ctx.respond("The user haven't started playing OV Bot yet")
              ctx.command.reset_cooldown(ctx)
              return
            if user2 == ctx.author:
              await ctx.respond("You can't play with yourself")
              ctx.command.reset_cooldown(ctx)
              return

            if usert['injail'] == True:
                await ctx.respond("The user is in Jail!")
                ctx.command.reset_cooldown(ctx)
                return
            elif usert['inhosp'] == True:
                await ctx.respond("The user is in Hospital!")
                ctx.command.reset_cooldown(ctx)
                return
            if usert['cash'] < bet:
                await ctx.respond(f"{user2} is too poor to afford the bet")
                ctx.command.reset_cooldown(ctx)
                return
            if usert['lvl'] < 5:
                await ctx.respond("The user is not level 5 yet!")
                ctx.command.reset_cooldown(ctx)
                return

            await updateset(user2.id, 'blocked', True)
            await updateset(ctx.author.id, 'blocked', True)

            view = interclass.Confirm(ctx, ctx.author)
            await ctx.respond(f"{gettitle(user)}{ctx.author.mention} are you sure you want to bet <:cash:1329017495536930886> {bet} with {usert['title']}{user2.name}?", view=view)
            msg = await ctx.interaction.original_response()
            view.message = msg
            await view.wait()

            if view.value is None:
                await ctx.respond(f"You did not respond in time")
                ctx.command.reset_cooldown(ctx)
                await updateset(user2.id, 'blocked', False)
                await updateset(ctx.author.id, 'blocked', False)
                return
            elif view.value == False:
                await ctx.respond(f"Bet cancelled")
                ctx.command.reset_cooldown(ctx)
                await updateset(user2.id, 'blocked', False)
                await updateset(ctx.author.id, 'blocked', False)
                return

            interaction = view.interaction

            view = interclass.Confirm(ctx, user2)
            await ctx.respond(f"{usert['title']}{user2.mention}, {gettitle(user)}{ctx.author.mention} challenged you to a <:cash:1329017495536930886> {bet} bet Blackjack! Do you want to accept?", view=view)
            msg = await ctx.interaction.original_response()
            view.message = msg
            await view.wait()

            if view.value is None:
                await ctx.respond(f"{usert['title']}{user2.mention} ignored {gettitle(user)}{ctx.author.mention} wow")
                ctx.command.reset_cooldown(ctx)
                await updateset(user2.id, 'blocked', False)
                await updateset(ctx.author.id, 'blocked', False)
                return
            elif view.value == False:
                await ctx.respond(f"{usert['title']}{user2.mention} is too afraid to accept {gettitle(user)}{ctx.author.mention}'s challenge")
                ctx.command.reset_cooldown(ctx)
                await updateset(user2.id, 'blocked', False)
                await updateset(ctx.author.id, 'blocked', False)
                return

            interaction2 = view.interaction

            await updateinc(user2.id,'cash',-bet)
            await updateinc(ctx.author.id,'cash',-bet)
            shuffled = random.sample(lists.cards, len(lists.cards))
            usercard = []
            dealercard = []
            for x in range(2):
                uservalue = 0
                card = random.choice(shuffled)
                while card in usercard or card in dealercard:
                    card = random.choice(shuffled)
                usercard.append(card)
                for c in usercard:
                    uservalue += lists.cardvalue[c]
                for c in usercard:
                    if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and uservalue > 21:
                        uservalue -= 10
            for x in range(2):
                dealervalue = 0
                drcard = random.choice(shuffled)
                while drcard in usercard or drcard in dealercard:
                    drcard = random.choice(shuffled)
                dealercard.append(drcard)
                for c in dealercard:
                    dealervalue += lists.cardvalue[c]
                for c in dealercard:
                    if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and dealervalue > 21:
                        dealervalue -= 10

            if uservalue == 21 and not dealervalue == 21:
                await updateinc(ctx.author.id,'cash',round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{gettitle(user)}{ctx.author.name} had a Blackjack! {gettitle(user)}{ctx.author.name} won <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await ctx.respond(embed=bjembed)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            elif dealervalue == 21 and not uservalue == 21:
                await updateinc(user2.id,'cash',round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{usert['title']}{user2.name} had a Blackjack! {usert['title']}{user2.name} won <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await ctx.respond(embed=bjembed)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            elif uservalue == 21 and dealervalue == 21:
                await updateinc(user2.id,'cash',bet)
                await updateinc(ctx.author.id,'cash',bet)
                bjembed = discord.Embed(title="Blackjack",description=f"Push! No one won\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await ctx.respond(embed=bjembed)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return

            ucard = usercard.copy()
            ucard[1] = "??"
            dcard = dealercard.copy()
            dcard[1] = "??"
            rounds = 0
            view = None
            msg = None
            secondturn = False
            secondturn1 = False
            view = interclass.Blackjack(ctx, "n", False, user2)
            bjembed = discord.Embed(title="Blackjack",description=f"Bet: <:cash:1329017495536930886> {bet}",color=color.blue())
            bjembed.add_field(name=f"{ctx.author.name}'s cards",value=f"`??` " + ", ".join(ucard),inline=True)
            bjembed.add_field(name=f"{user2.name}'s cards",value=f"`??` " + ", ".join(dcard),inline=True)
            bjembed.set_footer(text="'/blackjack rules' to read the rules!")
            msg = await ctx.respond(f"{gettitle(user)}{ctx.author.mention} It's your turn!", embed=bjembed, view=view)
            view.message = msg
            msg1 = await interaction.followup.send(f"**Your cards**\n`{uservalue}` {', '.join(usercard)}", ephemeral=True)
            msg2 = await interaction2.followup.send(f"**Your cards**\n`{dealervalue}` {', '.join(dealercard)}", ephemeral=True)
            while True:
                if secondturn == True:
                    secondturn = False
                    secondturn1 = True
                    ctx.author, user2 = user2, ctx.author
                    usercard, dealercard = dealercard, usercard
                    uservalue, dealervalue = dealervalue, uservalue
                    ucard, dcard = dcard, ucard
                    user, usert = usert, user
                    if rounds != 0:
                        view = interclass.Blackjack(ctx, "n", True, user2, uservalue)
                        view.message = await msg.edit(f"{gettitle(user)}{ctx.author.mention} It's your turn!", view=view)
                elif secondturn == False and secondturn1 == False:
                    if rounds != 0:
                        view = interclass.Blackjack(ctx, "n", False, user2, uservalue)
                        view.message = await msg.edit(f"{gettitle(user)}{ctx.author.mention} It's your turn!", view=view)
                else:
                    if rounds != 0:
                        view = interclass.Blackjack(ctx, "n", True, user2, uservalue)
                        view.message = await msg.edit(f"{gettitle(user)}{ctx.author.mention} It's your turn!", view=view)
                rounds += 1

                await view.wait()
                await asyncio.sleep(0.1)

                if view.value is None:
                    await updateinc(user2.id,'cash',bet*2)
                    await ctx.respond(f"{gettitle(user)}{ctx.author.name} did not give a response, {usert['title']}{user2.name} took the bet away")
                    await updateset(ctx.author.id, 'blocked', False)
                    await updateset(user2.id, 'blocked', False)
                    return
                elif view.value == "r":
                    await updateinc(user2.id,'cash',bet*2)
                    await ctx.respond(f"{gettitle(user)}{ctx.author.name} ran away leaving the bet, what a coward")
                    await updateset(ctx.author.id, 'blocked', False)
                    await updateset(user2.id, 'blocked', False)
                    return
                elif view.value == "h":
                    card = random.choice(shuffled)
                    while card in usercard or card in dealercard:
                        card = random.choice(shuffled)
                    usercard.append(card)
                    uservalue = 0
                    for c in usercard:
                        uservalue += lists.cardvalue[c]
                    for c in usercard:
                        if c in ['\U00002660A','\U00002764A','\U00002663A','\U00002666A'] and uservalue > 21:
                            uservalue -= 10
                    ucard = usercard.copy()
                    ucard[1:] = ["??" for x in ucard[1:]]
                    bjembed = discord.Embed(title="Blackjack",description=f"{gettitle(user)}{ctx.author.name} hits a card!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                    bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`??` " + ", ".join(ucard),inline=True)
                    bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`??` " + ", ".join(dcard),inline=True)
                    bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                    await msg.edit(embed=bjembed)
                    if secondturn1 == False:
                        await msg1.edit(f"**Your cards**\n`{uservalue}` {', '.join(usercard)}")
                    else:
                        await msg2.edit(f"**Your cards**\n`{uservalue}` {', '.join(usercard)}")
                elif view.value == "s":
                    if secondturn1 == True:
                        break
                    bjembed = discord.Embed(title="Blackjack",description=f"{gettitle(user)}{ctx.author.name} stands!\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                    bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`??` " + ", ".join(ucard),inline=True)
                    bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`??` " + ", ".join(dcard),inline=True)
                    bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                    await msg.edit(embed=bjembed)
                    secondturn = True

            ctx.author, user2 = user2, ctx.author
            usercard, dealercard = dealercard, usercard
            uservalue, dealervalue = dealervalue, uservalue
            ucard, dcard = dcard, ucard
            user, usert = usert, user

            if uservalue > 21 and dealervalue > 21:
                await updateinc(user2.id,'cash',bet)
                await updateinc(ctx.author.id,'cash',bet)
                bjembed = discord.Embed(title="Blackjack",description=f"Push! {usert['title']}{user2.name} and {gettitle(user)}{ctx.author.name} busted\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit("No one wins", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            if uservalue > 21:
                await updateinc(user2.id,'cash',round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{gettitle(user)}{ctx.author.name} busted and lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit(f"{usert['title']}{user2.name} wins!", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            if dealervalue > 21:
                await updateinc(ctx.author.id,'cash', round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{usert['title']}{user2.name} busted and lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit(f"{gettitle(user)}{ctx.author.name} wins!", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            if dealervalue > uservalue:
                await updateinc(user2.id,'cash',round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{gettitle(user)}{ctx.author.name} had {uservalue} and {usert['title']}{user2.name} had {dealervalue}! {gettitle(user)}{ctx.author.name} lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit(f"{usert['title']}{user2.name} wins!", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            elif dealervalue < uservalue:
                await updateinc(ctx.author.id,'cash',round(bet*2*0.95))
                bjembed = discord.Embed(title="Blackjack",description=f"{usert['title']}{user2.name} had {dealervalue} and {gettitle(user)}{ctx.author.name} had {uservalue}! {usert['title']}{user2.name} lost <:cash:1329017495536930886> {bet}\nBet: <:cash:1329017495536930886> {bet}",color=color.green())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit(f"{gettitle(user)}{ctx.author.name} wins!", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return
            elif dealervalue == uservalue:
                await updateinc(user2.id,'cash',bet)
                await updateinc(ctx.author.id,'cash',bet)
                bjembed = discord.Embed(title="Blackjack",description=f"Push! No one won\nBet: <:cash:1329017495536930886> {bet}",color=color.gold())
                bjembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s cards",value=f"`{uservalue}` " + ", ".join(usercard),inline=True)
                bjembed.add_field(name=f"{usert['title']}{user2.name}'s cards",value=f"`{dealervalue}` " + ", ".join(dealercard),inline=True)
                bjembed.set_footer(text="'/blackjack rules' to read the rules!")
                await msg.edit(f"No one wins", embed=bjembed, view=None)
                await updateset(ctx.author.id, 'blocked', False)
                await updateset(user2.id, 'blocked', False)
                return

async def highlow(self, ctx, bet):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      if bet == None:
        await ctx.respond("You have to give a bet!")
        ctx.command.reset_cooldown(ctx)
        return
      try:
        bet = int(bet)
      except:
        if not bet.lower() == 'max':
          await ctx.respond("Give a valid amount of bet!")
          ctx.command.reset_cooldown(ctx)
          return
        pass
      user = await finduser(ctx.author.id)
      usercash = user['cash']
      try:
        if bet.lower() == 'max':
          bet = math.floor(usercash)
          if bet > 5000:
            bet = 5000
      except:
        pass
      if bet <= 0:
        await ctx.respond("You have to give a valid amount of bet")
        ctx.command.reset_cooldown(ctx)
        return
      if usercash < bet:
        await ctx.respond("You don't even have enough cash poor guy")
        ctx.command.reset_cooldown(ctx)
        return
      if bet > 5000:
        await ctx.respond("You cannot bet more than <:cash:1329017495536930886> 5000!")
        ctx.command.reset_cooldown(ctx)
        return
      if bet < 10:
        await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10!")
        ctx.command.reset_cooldown(ctx)
        return
      userlvl = user['lvl']
      if userlvl < 10:
        await ctx.respond("You have to be at least level 10 to play High Low!")
        return
      await updateinc(ctx.author.id,'cash',-bet)
      pot = bet
      shuffled = random.sample(lists.cards, len(lists.cards))
      takencard = []
      winstreak = 0
      previous = ''

      while True:
        card = random.choice(shuffled)
        while card in takencard:
          card = random.choice(shuffled)
        takencard.append(card)
        usercard = card
        uservalue = lists.cardvalue[usercard]
        card = random.choice(shuffled)
        while card in takencard:
          card = random.choice(shuffled)
        takencard.append(card)
        dealercard = card
        dealervalue = lists.cardvalue[dealercard]
        hlembed = discord.Embed(title="High Low",description=f"Is your card higher or lower than the dealer's?\nPot: <:cash:1329017495536930886> {pot} (x15%)\n\nWinstreak: **{winstreak}**",color=color.blue())
        hlembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s card",value=f"??",inline=True)
        hlembed.add_field(name=f"Dealer's card",value=f"{dealercard}",inline=True)
        if winstreak == 0 and not previous == 'tie':
          view = interclass.Highlow(ctx, ctx.author)
          await ctx.respond(embed=hlembed, view=view)
          msg = await ctx.interaction.original_response()
          view.message = msg
        else:
          if not previous == 'tie':
            view = interclass.Highlow2(ctx, ctx.author)
            hlnembed = discord.Embed(title="High Low",description=f"Your current pot is <:cash:1329017495536930886> {pot}!\nDo you want to cash out or play the next round?\n\nWinstreak: **{winstreak}**",color=color.blue())
            view.message = await msg.edit(embed=hlnembed, view=view)
            
            await view.wait()
            if view.value is None:
              await ctx.respond(f"You took too long to response, the dealer took your pot away")
              return

            if view.value == 'cash':
              await updateinc(ctx.author.id,'cash',pot)
              luck = random.randint(1, 10)
              if luck == 1 and user['stats']['luk'] < 500:
                await updateinc(ctx.author.id, 'stats.luk', 1)
                hlembed = discord.Embed(title="High Low",description=f"You cashed out <:cash:1329017495536930886> {pot} from your pot and gained 1 Luck <:luck:940955425308823582>!\nPot: <:cash:1329017495536930886> {pot}\n\nWinstreak: **{winstreak}**",color=color.green())
              else:
                hlembed = discord.Embed(title="High Low",description=f"You cashed out <:cash:1329017495536930886> {pot} from your pot!\nPot: <:cash:1329017495536930886> {pot}\n\nWinstreak: **{winstreak}**",color=color.green())
              hlembed.set_footer(text="GG")
              await msg.edit(embed=hlembed)
              return
            elif view.value == 'next':
              view = interclass.Highlow(ctx, ctx.author)
              view.message = await msg.edit(embed=hlembed, view=view)
          elif previous == 'tie':
            view = interclass.Highlow(ctx, ctx.author)
            view.message = await msg.edit(embed=hlembed, view=view)

        await view.wait()
        if view.value is None:
          await ctx.respond(f"You took too long to response, the dealer took your pot away")
          return

        if uservalue == dealervalue:
          previous = 'tie'
          hlembed = discord.Embed(title="High Low",description=f"Tie! Nothing happened\nPot: <:cash:1329017495536930886> {pot} (x15%)\nWinstreak: **{winstreak}**",color=color.gold())
          hlembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s card",value=f"{usercard}",inline=True)
          hlembed.add_field(name=f"Dealer's card",value=f"{dealercard}",inline=True)
          hlembed.set_footer(text="Don't forget to cash out!")
          await msg.edit(embed=hlembed, view=None)
          await asyncio.sleep(2)
        elif (uservalue > dealervalue and view.value == 'high') or (uservalue < dealervalue and view.value == 'low'):
          previous = 'win'
          winstreak += 1
          added = round(pot*0.15)
          pot = round(pot + added)
          if uservalue < dealervalue:
            m = 'lower'
          else:
            m = 'higher'
          hlembed = discord.Embed(title="High Low",description=f"Your card is {m} than the dealer's card! <:cash:1329017495536930886> {added} has been added to your pot\nPot: <:cash:1329017495536930886> {pot} (x15%)\nWinstreak: **{winstreak}**",color=color.green())
          hlembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s card",value=f"{usercard}",inline=True)
          hlembed.add_field(name=f"Dealer's card",value=f"{dealercard}",inline=True)
          hlembed.set_footer(text="Don't forget to cash out!")
          await msg.edit(embed=hlembed, view=None)
          await asyncio.sleep(2)
        else:
          previous = 'lose'
          if uservalue < dealervalue:
            m = 'lower'
          else:
            m = 'higher'
          hlembed = discord.Embed(title="High Low",description=f"Your card is {m} than the dealer's card! You lost <:cash:1329017495536930886> {bet}\nPot: <:cash:1329017495536930886> {pot} (x15%)\nWinstreak: **{winstreak}**",color=color.red())
          hlembed.add_field(name=f"{gettitle(user)}{ctx.author.name}'s card",value=f"{usercard}",inline=True)
          hlembed.add_field(name=f"Dealer's card",value=f"{dealercard}",inline=True)
          hlembed.set_footer(text="Rip")
          await msg.edit(embed=hlembed, view=None)
          return

async def slot(self, ctx, bet):
      if await blocked(ctx.author.id) == False:
        ctx.command.reset_cooldown(ctx)
        return
      if bet == None:
        await ctx.respond("You have to give a bet!")
        ctx.command.reset_cooldown(ctx)
        return
      if bet == "paytable":
        payouts = discord.Embed(title="Slot machine pay table", description="<:token:1313796725407875143><:token:1313796725407875143><:token:1313796725407875143> x2\n<:cash:1329017495536930886><:cash:1329017495536930886> x2\n<:cash:1329017495536930886><:cash:1329017495536930886><:cash:1329017495536930886> x4\n<:luck:1329361131172659252><:luck:1329361131172659252> x3\n<:luck:1329361131172659252><:luck:1329361131172659252><:luck:1329361131172659252> x5\n<:bullet:1329358006382624769><:bullet:1329358006382624769> x5\n<:bullet:1329358006382624769><:bullet:1329358006382624769><:bullet:1329358006382624769> x10\n<:desert_eagle:1329359892875579412><:desert_eagle:1329359892875579412> x8\n<:desert_eagle:1329359892875579412><:desert_eagle:1329359892875579412><:desert_eagle:1329359892875579412> x15\n<:gold:1329356387482075137><:gold:1329356387482075137> x10\n<:gold:1329356387482075137><:gold:1329356387482075137><:gold:1329356387482075137> x20\n\U0001F48E x5\n\U0001F48E\U0001F48E x15\n\U0001F48E\U0001F48E\U0001F48E JACKPOT", color=color.blurple())
        await ctx.respond(embed=payouts)
        ctx.command.reset_cooldown(ctx)
        return
      try:
        bet = int(bet)
      except:
        if not bet.lower() == 'max':
          await ctx.respond("Give a valid amount of bet!")
          ctx.command.reset_cooldown(ctx)
          return
        pass
      user = await finduser(ctx.author.id)
      usercash = user['cash']
      try:
        if bet.lower() == 'max':
          bet = math.floor(usercash)
          if bet > 5000:
            bet = 5000
      except:
        pass
      if bet <= 0:
        await ctx.respond("You have to give a valid amount of bet")
        ctx.command.reset_cooldown(ctx)
        return
      if usercash < bet:
        await ctx.respond("You don't even have enough cash poor guy")
        ctx.command.reset_cooldown(ctx)
        return
      if bet > 5000:
        await ctx.respond("You cannot bet more than <:cash:1329017495536930886> 5000!")
        ctx.command.reset_cooldown(ctx)
        return
      if bet < 10:
        await ctx.respond("You cannot bet less than <:cash:1329017495536930886> 10!")
        ctx.command.reset_cooldown(ctx)
        return
      userlvl = user['lvl']
      if userlvl < 10:
        await ctx.respond("You have to be at least level 5 to play the slot machine!")
        return
      await updateinc(ctx.author.id,'cash',-bet)
      server = await self.bot.gcll.find_one({"id": 863025676213944340})
      jackpot = server['jackpot']

      slotembed = discord.Embed(title="Slot machine", description=f"**Spinning**\n<a:slot:1329382326882533417><a:slot:1329382326882533417><a:slot:1329382326882533417>\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(jackpot)}", color=color.blurple())
      msg = await ctx.respond(embed=slotembed)

      payouts = {"token3": 2, "cash": 2, "cash3": 4, "luck": 3, "luck3": 5, "bullet": 5, "bullet3": 10, "gun": 8, "gun3": 15, "gold": 10, "gold3": 20, "diamond1": 5, "diamond": 15, "diamond3": "JACKPOT"}
      symbols = ['token','token','token','token','token', 'cash','cash','cash','cash', 'luck','luck','luck', 'bullet','bullet','bullet', 'gun','gun', 'gold','gold', 'diamond']
      emoji = {'token': '<:token:1313796725407875143>', 'cash': '<:cash:1329017495536930886>', 'luck': '<:luck:1329361131172659252>', 'bullet': '<:bullet:1329358006382624769>', 'gun': '<:desert_eagle:1329359892875579412>', 'gold': '<:gold:1329356387482075137>', 'diamond': '\U0001F48E'}

      await asyncio.sleep(1)
      firstwheel = random.choice(symbols)
      slotembed = discord.Embed(title="Slot machine", description=f"**Spinning**\n{emoji[firstwheel]}<a:slot:1329382326882533417><a:slot:1329382326882533417>\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(jackpot)}", color=color.blurple())
      msg = await msg.edit(embed=slotembed)
      await asyncio.sleep(0.5)
      secondwheel = random.choice(symbols)
      slotembed = discord.Embed(title="Slot machine", description=f"**Spinning**\n{emoji[firstwheel]}{emoji[secondwheel]}<a:slot:1329382326882533417>\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(jackpot)}", color=color.blurple())
      msg = await msg.edit(embed=slotembed)
      await asyncio.sleep(0.5)
      thirdwheel = random.choice(symbols)

      payout = 0
      if firstwheel == secondwheel == thirdwheel:
        payout = payouts[firstwheel + '3']
      elif (firstwheel == secondwheel) and secondwheel != 'token':
        payout = payouts[secondwheel]
      elif firstwheel == 'diamond':
        payout = payouts["diamond1"]


      if payout == "JACKPOT":
        prize = jackpot

        if user['stats']['luk']+5 <= 500:
          await updateinc(ctx.author.id, 'stats.luk', 5)
        await updateinc(ctx.author.id, 'cash', prize)
        slotembed = discord.Embed(title="Slot machine", description=f"**You won the JACKPOT and gained 5 Luck <:luck:940955425308823582>!**\n**<:cash:1329017495536930886> {aa(prize)}**\n{emoji[firstwheel]}{emoji[secondwheel]}{emoji[thirdwheel]}\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(10000)}", color=color.green())
        msg = await msg.edit(embed=slotembed)

        await self.bot.gcll.update_one({"id": 863025676213944340}, {"$set": {"jackpot": 10000}})

        return

      elif payout != 0:
        prize = bet*payout

        if random.randint(1,10) == 1 and user['stats']['luk'] < 500:
          await updateinc(ctx.author.id, 'stats.luk', 1)
          await updateinc(ctx.author.id, 'cash', prize)
          slotembed = discord.Embed(title="Slot machine", description=f"**You won <:cash:1329017495536930886> {aa(prize)} (x{payout}) and gained 1 Luck <:luck:940955425308823582>!**\n{emoji[firstwheel]}{emoji[secondwheel]}{emoji[thirdwheel]}\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(jackpot)}", color=color.green())
        else:
          await updateinc(ctx.author.id, 'cash', prize)
          slotembed = discord.Embed(title="Slot machine", description=f"**You won <:cash:1329017495536930886> {prize} (x{payout})!**\n{emoji[firstwheel]}{emoji[secondwheel]}{emoji[thirdwheel]}\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(jackpot)}", color=color.green())

        msg = await msg.edit(embed=slotembed)

        return

      slotembed = discord.Embed(title="Slot machine", description=f"**You got nothing.. Too bad!**\n{emoji[firstwheel]}{emoji[secondwheel]}{emoji[thirdwheel]}\n\nCurrent bet: <:cash:1329017495536930886> {bet}\nCurrent Jackpot: <:cash:1329017495536930886> {aa(round(jackpot + (bet/2)))}", color=color.red())
      msg = await msg.edit(embed=slotembed)

      await self.bot.gcll.update_one({"id": 863025676213944340}, {"$inc": {"jackpot": round(bet/10)}})

async def garage(self, ctx, page, user, filters, query):
      if await blocked(ctx.author.id) == False:
        return
      if user == None:
        user = ctx.author
      if await finduser(user.id) == None:
        await ctx.respond("The user haven't started playing OV Bot yet")
      userp = await finduser(user.id)
      if userp['s'] == 11:
        await updateset(ctx.author.id, "s", 12)
      usergarage = userp['garage']
      usergaragec = userp['garagec']
      try:
        query = query.lower()
      except:
        pass
      try:
        filters = filters.lower()
      except:
        pass
      if filters == "id":
        carlist = [str(x['index']) for x in usergarage]
      elif filters == "name":
        if query == None:
          carlists = sorted(usergarage, key=lambda x: x['name'])
          carlist = [str(x["index"]) for x in carlists]
        elif not query == None:
          # carlists = list(filter(lambda d: d['name'].lower().startswith(query), usergaragelist))
          carlists = [x for x in usergarage if query in x['name'].replace(" ", "").lower()]
          carlist = [str(x['index']) for x in sorted(carlists, key=lambda x: x['name'])]
          if len(carlist) == 0:
            await ctx.respond(f"No cars found starting with \"{query}\"")
            return
      elif filters == "rank":
        if query == None:
          carlists = sorted(usergarage, reverse=True, key=lambda x: 0 if x['name'] in lists.lowcar else 1 if x['name'] in lists.averagecar else 2 if x['name'] in lists.highcar else 3)
          carlist = [str(x['index']) for x in carlists]
        elif not query == None:
          dispatcher = {"low": "Low", "average": "Average", "high": "High", "exotic": "Exotic", "classic": "Classic", "exclusive": "Exclusive"}
          query = [rank for rank in list(dispatcher) if query.lower() == rank or query.lower() in rank]
          if query == []:
            await ctx.respond("You have to give a valid rank: `Low, Average, High, Exotic, Classic, Exclusive`")
            return
          else:
            query = query[0]
          query = dispatcher[query]
          dispatcher = {"Low": lists.lowcar, "Average": lists.averagecar, "High": lists.highcar, "Exotic": lists.exoticcar, "Classic": lists.classiccar, "Exclusive": lists.exclusivecar}
          carlist = [str(x['index']) for x in usergarage if x['name'] in dispatcher[query]]
          if len(carlist) == 0:
            if user == ctx.author:
              await ctx.respond(f"You don't have any {query} ranked cars!")
            else:
              await ctx.respond(f"The user don't have any {query} ranked cars!")
            return
      elif filters == "golden":
        carlist = [str(x['index']) for x in usergarage if x['golden'] == True]
        if len(carlist) == 0:
          if user == ctx.author:
            await ctx.respond("You dont have any golden cars")
          else:
            await ctx.respond("The user dont have any golden cars")
          return
      elif filters == "locked":
        carlist = [str(x['index']) for x in usergarage if x['locked'] == True]
        if len(carlist) == 0:
          if user == ctx.author:
            await ctx.respond("You dont have any locked cars")
          else:
            await ctx.respond("The user dont have any locked cars")
          return
      elif filters == "id-":
        carlist = [str(x['index']) for x in usergarage]
        carlist.reverse()
      elif filters == "alphabet":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['name'])]
      elif filters == "price":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['price'], reverse=True)]
      elif filters == "tuned":
        carlists = [x for x in usergarage if x['tuned'] > 0]
        carlist = [str(x['index']) for x in sorted(carlists, key=lambda x: x['tuned'], reverse=True)]
      elif filters == "tuned-":
        carlists = [x for x in usergarage if x['tuned'] > 0]
        carlist = [str(x['index']) for x in sorted(carlists, key=lambda x: x['tuned'])]
      elif filters == "speed":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['speed'], reverse=True)]
      elif filters == "alphabet-":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['name'], reverse=True)]
      elif filters == "price-":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['price'])]
      elif filters == "speed-":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: x['speed'])]
      elif filters == "ovr-":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: round(((x['speed']/1.015**x['tuned'])-lists.carspeed[x['name']]+10)/2, 2))]
      elif filters == "ovr":
        carlist = [str(x['index']) for x in sorted(usergarage, key=lambda x: round(((x['speed']/1.015**x['tuned'])-lists.carspeed[x['name']]+10)/2, 2), reverse=True)]
      else:
        carlist = [str(x['index']) for x in usergarage]

      if len(carlist) == 0:
        maxpage = 1

      maxpage = math.ceil(len(carlist)/10)

      if page > maxpage and user == ctx.author and not len(userp['garage']) == 0:
        await ctx.respond(f"Your garage only has {maxpage} pages")
        return
      elif page == 0:
        await ctx.respond("Why are there weirdos like you")
        return
      elif page < 0:
        await ctx.respond("There are no negative pages, go to school")
        return
      elif page > maxpage and not user == ctx.author and not len(userp['garage']) == 0:
        await ctx.respond(f"The user's garage only has {maxpage} pages")
        return

      if len(carlist) == 0:
        maxpage = 1
        page = 1
      if user == ctx.author:
        grgembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s garage", description = f"**Your cars** {len(usergarage)}/{usergaragec}\n**Total cars shown** {len(carlist)}\n\n", color = color.random())
      else:
        grgembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s garage", description = f"**{gettitle(userp)}{user.name}'s cars** {len(usergarage)}/{usergaragec}\n**Total cars shown** {len(carlist)}\n\n", color = color.random())
      grgembed.set_footer(text = f"Page {page} of {maxpage}")

      if len(carlist) == 0:
        if user == ctx.author:
          grgembed.add_field(name = "You have no cars to look", value = "go steal one", inline = False)
        else:
          grgembed.add_field(name = "The user have no cars", value = "poor guy", inline = False)
        await ctx.respond(embed=grgembed)
        return

      largest = len(str(max([int(x) for x in carlist[(page-1)*10:(page-1)*10+10]])))
      for car in carlist[(page-1)*10:(page-1)*10+10]:
        usercar = [x for x in usergarage if x["index"] == int(car)][0]
        car = (largest-len(str(car))) * " " + car
        carname = usercar['name']
        if usercar['golden'] == True:
          carname = f"{star} Golden " + usercar['name']
          usercar['price'] *= 2
        if usercar['locked'] == True:
          carname = carname + f" {lock}"
        if "speed" in filters:
          grgembed.description += f"**`{car}`** **{carname}** | Speed **{usercar['speed']}**\n"
        elif "price" in filters:
          grgembed.description += f"**`{car}`** **{carname}** | Base Price <:cash:1329017495536930886> **{round(usercar['price'])}**\n"
        elif "tuned" in filters:
          grgembed.description += f"**`{car}`** **{carname}** | Tuned **{usercar['tuned']}**\n"
        elif "rank" in filters:
          if usercar['name'] in lists.lowcar:
            rank = "Low"
          elif usercar['name'] in lists.averagecar:
            rank = "Average"
          elif usercar['name'] in lists.highcar:
            rank = "High"
          elif usercar['name'] in lists.exoticcar:
            rank = "Exotic"
          elif usercar['name'] in lists.classiccar:
            rank = "Classic"
          elif usercar['name'] in lists.exclusivecar:
            rank = "Exclusive"
          else:
            rank = "Unknown"
          grgembed.description += f"**`{car}`** **{carname}** | **{functions.rankconv(rank)}**\n"
        else:
          grgembed.description += f"**`{car}`** **{carname}** | OVR **{round(((usercar['speed']/1.015**usercar['tuned'])-lists.carspeed[usercar['name']]+10)/2, 2)}/10**\n"

      view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
      await ctx.respond(embed=grgembed, view=view)
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1

        if user == ctx.author:
          grgembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s garage", description = f"**Your cars {len(usergarage)}/{usergaragec}**\n**Total cars shown** {len(carlist)}\n\n", color = color.random())
        else:
          grgembed = discord.Embed(title = f"{gettitle(userp)}{user.name}'s garage", description = f"**{gettitle(userp)}{user.name}'s cars {len(usergarage)}/{usergaragec}**\n**Total cars shown** {len(carlist)}\n\n", color = color.random())
        grgembed.set_footer(text = f"Page {page} of {maxpage}")

        largest = len(str(max([int(x) for x in carlist[(page-1)*10:(page-1)*10+10]])))
        for car in carlist[(page-1)*10:(page-1)*10+10]:
          usercar = [x for x in usergarage if x["index"] == int(car)][0]
          car = (largest-len(str(car))) * " " + car
          carname = usercar['name']
          if usercar['golden'] == True:
            carname = f"{star} Golden " + usercar['name']
            usercar['price'] *= 2
          if usercar['locked'] == True:
            carname = carname + f" {lock}"
          if "speed" in filters:
            grgembed.description += f"**`{car}`** **{carname}** | Speed **{usercar['speed']}**\n"
          elif "price" in filters:
            grgembed.description += f"**`{car}`** **{carname}** | Base Price <:cash:1329017495536930886> **{round(usercar['price'])}**\n"
          elif "tuned" in filters:
            grgembed.description += f"**`{car}`** **{carname}** | Tuned **{usercar['tuned']}**\n"
          elif "rank" in filters:
            if usercar['name'] in lists.lowcar:
              rank = "Low"
            elif usercar['name'] in lists.averagecar:
              rank = "Average"
            elif usercar['name'] in lists.highcar:
              rank = "High"
            elif usercar['name'] in lists.exoticcar:
              rank = "Exotic"
            elif usercar['name'] in lists.classiccar:
              rank = "Classic"
            elif usercar['name'] in lists.exclusivecar:
              rank = "Exclusive"
            else:
              rank = "Unknown"
            grgembed.description += f"**`{car}`** **{carname}** | **{functions.rankconv(rank)}**\n"
          else:
            grgembed.description += f"**`{car}`** **{carname}** | OVR **{round(((usercar['speed']/1.015**usercar['tuned'])-lists.carspeed[usercar['name']]+10)/2, 2)}/10**\n"

        view = interclass.Page(ctx, ctx.author, page == 1, page == maxpage)
        view.message = await msg.edit(embed=grgembed, view=view)

async def givecar(self, ctx, user, carid):
      if await blocked(ctx.author.id) == False:
        return
      if user == None:
        await ctx.respond("Who do you want to give your car?")
        return
      if carid == None:
        await ctx.respond("You have to give a car ID!")
        return
      if user == ctx.author:
        await ctx.respond("You can't give cars to yourself")
        return
      usert = await finduser(user.id)
      if usert == None:
        await ctx.respond("Cannot find the user")
        return
      if ctx.guild.id in usert['q']:
        await ctx.respond("The user quarantined themselves, how lonely")
        return
      if len(usert['garage']) >= usert['garagec']:
        await ctx.respond("The user's garage is already full!")
        return
      userp = await finduser(ctx.author.id)
      if userp['location'] != usert['location']:
        await ctx.respond("You need to be in the same city as the user to send cars!")
        return
      usergarage = userp['garage']
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(userp['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if userp['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
        carid = getdrive(userp, "id")

      carid = str(carid)
      if "," in carid:
        carid = re.split(",", carid)
      else:
        carid = re.split(" ", carid)
      carid = [x.strip() for x in carid if x != '']
      repeat = functions.checksame(carid)
      if repeat == True:
        await ctx.respond("You can't give the same car twice!")
        return
      for carids in carid:
        usercar = [x for x in usergarage if x['index'] == int(carids)]
        if len(usercar) == 0:
          await ctx.respond(f"You don't have the car ID `{carids}`")
          return
        if usercar[0]['locked'] == True:
          await ctx.respond(f"You cannot give locked cars: `{carids}`")
          return
      await updateset(ctx.author.id, 'blocked', True)
      await updateset(user.id, 'blocked', True)

      cars = []
      total = 0
      for carids in carid:
        usercar = [x for x in usergarage if x['index'] == int(carids)][0]

        if len(usert['garage']) == 0:
          carindex = 1
        else:
          carindex = usert['garage'][-1]["index"]+1
        carindex += total
        carinfo = {"index": carindex, 'id': usercar['id'], 'name': usercar['name'], 'price': usercar['price'], 'speed': usercar['speed'], 'tuned': usercar['tuned'], 'golden': usercar['golden'], 'locked': False}
        cars.append(carinfo)
        total += 1

      if userp['drive'] in [x['id'] for x in cars]:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"id": {"$in": [x['id'] for x in cars]}}}, "$set": {"drive": ""}})
      else:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"id": {"$in": [x['id'] for x in cars]}}}})
      await self.bot.cll.update_one({"id": user.id}, {"$push": {"garage": {"$each": cars}}})
      a = [car['name'] if car['golden'] == False else star + ' Golden ' + car['name'] for car in cars]
      givecarembed = discord.Embed(title="Car given",description=f"You gave your **{', '.join(a)}** to {usert['title']}{user.mention}!",color=color.green())
      givecarembed.set_footer(text=":)")

      receiveembed = discord.Embed(title="Car received",description=f"{gettitle(userp)}{ctx.author.mention} gave you a **{', '.join(a)}**!",color=color.green())
      receiveembed.set_footer(text="wow")

      await ctx.respond(embed=givecarembed)
      await user.send(embed=receiveembed)
      await updateset(ctx.author.id, 'blocked', False)
      await updateset(user.id, 'blocked', False)

async def car(self, ctx, car):
      if await blocked(ctx.author.id) == False:
        return
      try:
        car = car.lower()
      except:
        pass
      if car == "list":
        await ctx.respond("There is no list for cars! Discover them yourself")
        return
      golden = False
      if car.startswith("golden "):
        car = re.split("golden ", car)[-1]
        golden = True
      if not car in lists.allcars:
        try:
          if len(car) < 2:
            await ctx.respond("Enter at least 2 letters to search")
            return
          closematch = [x for x in lists.allcars if car.lower() == x.lower() or car.lower() == x.lower().replace(" ","")]
          if len(closematch) == 0:
            closematch = [x for x in lists.allcars if car.lower() in x.lower() or car.lower() in x.lower().replace(" ","")]
          if len(closematch) > 1:
            await ctx.respond(f"I found more than one car that matches your search:\n**{', '.join(closematch)}**\nWhich one are you searching for?")
            return
          else:
            car = closematch[0]
        except:
          await ctx.respond("Cannot find this vehicle, make sure you typed the full name of the vehicle!")
          return
      index = lists.allcars.index(car)
      carname = lists.allcars[index]
      if carname in lists.lowcar:
        rank = "Low"
      elif carname in lists.averagecar:
        rank = "Average"
      elif carname in lists.highcar:
        rank = "High"
      elif carname in lists.exoticcar:
        rank = "Exotic"
      elif carname in lists.classiccar:
        rank = "Classic"
      elif carname in lists.exclusivecar:
        rank = "Exclusive"
      else:
        rank = "Unknown"
      if golden == True and car in lists.nogolden:
        await ctx.respond("This car has no golden version (It's too rare)!")
        return
      if golden == True:
        carprice = lists.carprice[carname]*2
        carspeed = lists.carspeed[carname]
        vembed = discord.Embed(title=f"{star} Golden " + carname, description=f"{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {carprice}\n**Average Speed:** {carspeed} MPH",color = color.random() if rank != "Exotic" else color.default())
        if not carname in lists.goldencars:
          byte = functions.goldfilter(lists.carimage[carname])
          file = discord.File(fp=byte,filename="pic.jpg")
          vembed.set_image(url="attachment://pic.jpg")
        else:
          vembed.set_image(url=lists.goldencarimage[carname])
      else:
        carprice = lists.carprice[carname]
        carspeed = lists.carspeed[carname]
        vembed = discord.Embed(title=carname, description=f"{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price:** <:cash:1329017495536930886> {carprice}\n**Average Speed:** {carspeed} MPH",color = color.random() if rank != "Exotic" else color.default())
        vembed.set_image(url=lists.carimage[carname])
      
      vembed.set_footer(text="Car prices can be a lot higher if it's fast!")

      if golden == True and not carname in lists.goldencars:
        await ctx.respond(file=file,embed=vembed)
      else:
        await ctx.respond(embed=vembed)

async def mycar(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      usergarage = user['garage']
      if carid == None:
        carid = usergarage[0]["index"]
      carid = str(carid)
      if carid.lower() == "latest" or carid.lower() == "l" or carid is None:
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
        carid = getdrive(user, "id")
      try:
        usercar = [x for x in usergarage if x["index"] == int(carid)][0]
      except:
        await ctx.respond("You don't have this car ID in your garage!")
        return
      carname = usercar['name']
      carprice = usercar['price']
      carspeed = usercar['speed']
      cartuned = usercar['tuned']

      if user['s'] == 13:
        await updateset(ctx.author.id, 's', 14)
      cname = carname
      if carname in lists.lowcar:
        rank = "Low"
      elif carname in lists.averagecar:
        rank = "Average"
      elif carname in lists.highcar:
        rank = "High"
      elif carname in lists.exoticcar:
        rank = "Exotic"
      elif carname in lists.classiccar:
        rank = "Classic"
      elif carname in lists.exclusivecar:
        rank = "Exclusive"
      else:
        rank = "Unknown"

      if usercar['locked'] == True:
        carname = carname + f" {lock}"
      if usercar['golden'] == True:
        carname = f"{star} Golden " + carname
        carprice *= 2

      mvembed = discord.Embed(title=f"{gettitle(user)}{ctx.author.name}'s {carname}", description=f"{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {carprice}\n**Speed** {carspeed} MPH\n**Tuned** {cartuned}\n**Overall Rating** {round(((carspeed/1.015**cartuned)-lists.carspeed[cname]+10)/2, 2)}/10",color=color.random())

      if usercar['golden'] == True:
        if not cname in lists.goldencars:
          byte = functions.goldfilter(lists.carimage[cname])
          file = discord.File(fp=byte,filename="pic.jpg")
          mvembed.set_image(url="attachment://pic.jpg")
        else:
          mvembed.set_image(url=lists.goldencarimage[cname])
      else:
        mvembed.set_image(url=lists.carimage[cname])
      page = usergarage.index(usercar)+1
      mvembed.set_footer(text=f"thats a noob car\nCar {page} of {len(usergarage)}")

      view = interclass.Page(ctx, ctx.author, page == 1, page == len(usergarage))

      if usercar['golden'] == True and not cname in lists.goldencars:
        await ctx.respond(file=file, embed=mvembed, view=view)
      else:
        await ctx.respond(embed=mvembed, view=view)
    
      msg = await ctx.interaction.original_response()
      view.message = msg

      while True:
        await view.wait()
        if view.value is None:
          return
        elif view.value == "left":
          page -= 1
        elif view.value == "right":
          page += 1

        try:
          usercar = usergarage[page-1]
        except:
          await ctx.respond("You don't have this car ID in your garage!")
          return
        carname = usercar['name']
        carprice = usercar['price']
        carspeed = usercar['speed']
        cartuned = usercar['tuned']

        cname = carname
        if carname in lists.lowcar:
          rank = "Low"
        elif carname in lists.averagecar:
          rank = "Average"
        elif carname in lists.highcar:
          rank = "High"
        elif carname in lists.exoticcar:
          rank = "Exotic"
        elif carname in lists.classiccar:
          rank = "Classic"
        elif carname in lists.exclusivecar:
          rank = "Exclusive"
        else:
          rank = "Unknown"
        mvembed = discord.Embed(title=f"{gettitle(user)}{ctx.author.name}'s {carname}", description=f"{(f'**Specialty** {(await functions.carspecialty(self, lists.specialty[carname]))}') if carname in list(lists.specialty) else ''}\n**Rank:** {functions.rankconv(rank)}\n**Base Price** <:cash:1329017495536930886> {carprice}\n**Speed** {carspeed} MPH\n**Tuned** {cartuned}\n**Overall Rating** {round(((carspeed/1.015**cartuned)-lists.carspeed[carname]+10)/2, 2)}/10",color=color.random())

        if usercar['locked'] == True:
          carname = carname + f" {lock}"
        if usercar['golden'] == True:
          carname = f"{star} Golden " + carname
          carprice *= 2
          if not cname in lists.goldencars:
            byte = functions.goldfilter(lists.carimage[cname])
            file = discord.File(fp=byte,filename="pic.jpg")
            mvembed.set_image(url="attachment://pic.jpg")
          else:
            mvembed.set_image(url=lists.goldencarimage[cname])
        else:
          mvembed.set_image(url=lists.carimage[cname])
        mvembed.set_footer(text=f"thats a noob car\nCar {page} of {len(usergarage)}")

        view = interclass.Page(ctx, ctx.author, page == 1, page == len(usergarage))
    
        if usercar['golden'] == True and not cname in lists.goldencars:
          view.message = await msg.edit(attachments=[], file=file, embed=mvembed, view=view)
        else:
          view.message = await msg.edit(attachments=[], embed=mvembed, view=view)

async def reindex(self, ctx):
    user = await finduser(ctx.author.id)
    if user is None:
      return
    else:
      try:
        user['timer']['blocked']
        return
      except:
        pass
      if user['banned'] == True or user['blocked'] == True:
        return
      carlist = user['garage']
      carcount = 1

      for car in carlist:
        car["index"] = carcount
        carcount += 1
      await updateset(ctx.author.id, "garage", carlist)
      await ctx.respond("Successfully reindexed your cars!")

async def sellcar(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      if carid == None:
        await ctx.respond("Give a car ID to sell!")
        return
      user = await finduser(ctx.author.id)
      usergarage = user['garage']
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
        carid = getdrive(user, "id")
      
      carid = str(carid)
      if "," in carid:
        caridlist = re.split(",", carid)
      else:
        caridlist = re.split(" ", carid)
      try:
        caridlist = [int(x.strip()) for x in caridlist if x != '']
      except:
        await ctx.respond(f"You don't have the car `{carid}`")
        return
      repeat = functions.checksame(caridlist)
      if repeat == True:
        await ctx.respond("You can't sell a car more than one time!")
        return
      for carids in caridlist:
        car = [x for x in usergarage if x["index"] == int(carids)]
        if len(car) == 0:
          await ctx.respond(f"You don't have the car `{carids}`")
          return
        if car[0]['locked'] == True:
          await ctx.respond("You cannot sell locked cars")
          return
      usercarnames = []
      cars = []
      carprices = 0
      for carids in caridlist:
        car = [x for x in usergarage if x["index"] == int(carids)][0]
        carprice = car['price']
        usercarname = car['name']
        usercargolden = car['golden']
        cars.append(car)

        if usercargolden == True:
          usercarnames.append(f"{star} Golden " + usercarname)
          carprices += carprice*2
        else:
          usercarnames.append(usercarname)
          carprices += carprice

      if user['drive'] in [x['id'] for x in cars]:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {f'garage': {"id": {"$in": [x["id"] for x in cars]}}}, "$inc": {"cash": carprices}, "$set": {"drive": ""}})  
      else:
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {f'garage': {"id": {"$in": [x["id"] for x in cars]}}}, "$inc": {"cash": carprices}})

      if user['s'] == 18:
        await updateset(ctx.author.id, "s", 19)

      usercarnames = ", ".join(usercarnames)
      sellembed = discord.Embed(title="Car sold",description=f"You sold your **{usercarnames}** for <:cash:1329017495536930886> {round(carprices)}!",color=color.green())
      sellembed.set_footer(text="noob car")

      await ctx.respond(embed=sellembed)

async def tune(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      if carid == None:
        await ctx.respond("Give a car ID!")
        return
      user = await finduser(ctx.author.id)
      usergarage = user['garage']
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
        carid = getdrive(user, "id")

      try:
        int(carid)
      except:
        await ctx.respond(f"You don't have this car ID `{carid}` in your garage!")
        return
      if int(carid) not in [x["index"] for x in usergarage]:
        await ctx.respond("You don't have this car ID in your garage!")
        return
      usercar = [x for x in usergarage if x["index"] == int(carid)][0]
      usercarname = usercar['name']
      usercartune = usercar['tuned']

      usercash = user['cash']
      if usercarname in lists.lowcar:
        rank = "Low"
      elif usercarname in lists.averagecar:
        rank = "Average"
      elif usercarname in lists.highcar:
        rank = "High"
      elif usercarname in lists.exoticcar:
        rank = "Exotic"
      elif usercarname in lists.classiccar:
        rank = "Classic"
      elif usercarname in lists.exclusivecar:
        rank = "Exclusive"
      else:
        rank = "Unknown"
      price = {"Low": 50, "Average": 200, "High": 500, "Exotic": 1000, "Classic": 1000, "Exclusive": 2000, "Unknown": 1000000000}
      if usercash < price[rank]:
        await ctx.respond(f"You don't have enough cash! You need <:cash:1329017495536930886> {aa(price[rank])} to tune your car")
        return

      if usercar['locked'] == True:
        await ctx.respond("You cannot tune a locked car")
        return
      await updateinc(ctx.author.id, 'cash', -price[rank])

      tunesuccess = functions.tunecar(usercartune, user)
      
      if tunesuccess == True:
        usercarspeed = usercar['speed']
        speedinc = round(usercarspeed*0.015 + usercarspeed, 2)

        await self.bot.cll.update_one({"id": ctx.author.id, "garage.index": usercar["index"]}, {"$inc": {"garage.$.tuned": 1}, "$set": {"garage.$.speed": round(speedinc,2)}})

        tuneembed = discord.Embed(title="Success!",description=f"You successfully paid <:cash:1329017495536930886> {price[rank]} and tuned your car {usercarname}!\nIt is now {usercartune+1} tuned",color=color.green())
        tuneembed.set_footer(text="lucky pog")
        await ctx.respond(embed=tuneembed)
      else:
        if usercar['id'] == user['drive']:
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"index": usercar["index"]}}, "$set": {"drive": ""}})
        else:
          await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"garage": {"index": usercar["index"]}}})

        tuneembed = discord.Embed(title="Fail!",description=f"You tuned your car but it exploded during testing!\nYou lost your car {usercarname}",color=color.red())
        tuneembed.set_footer(text="BIG RIP")
        await ctx.respond(embed=tuneembed)

async def upgradegarage(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      usergaragec = user['garagec']
      usercash = user['cash']
      if usercash < ((usergaragec-5)*50)+50:
        await ctx.respond(f"You need <:cash:1329017495536930886> {((usergaragec-5)*50)+50} to upgrade your garage")
        return
      if user['s'] == 66:
        await updateset(ctx.author.id, 's', 67)
      if usercash > ((usergaragec-5)*50)+50:
        await updateinc(ctx.author.id,'cash',-(((usergaragec-5)*50)+50))
        await updateinc(ctx.author.id,'garagec',1)
        upembed = discord.Embed(title="Successfully upgraded garage",description=f"You paid <:cash:1329017495536930886> {((usergaragec-5)*50)+50} to upgrade your garage!",color=color.green())
        upembed.set_footer(text="more cars!")

        await ctx.respond(embed=upembed)

async def lockcar(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = user['garage'][-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
      try:
        usercar = [x for x in user['garage'] if x["index"] == int(carid)][0]
      except:
        await ctx.respond("You dont have this car ID in your garage")
        return
      usercarname = usercar['name']
      if user['drive'] == usercar['id']:
        await ctx.respond("You cannot lock a car you are currently driving")
        return
      if usercar['locked'] == True:
        await ctx.respond("This car is already locked! Type `/unlockcar <car ID>` to unlock a car")
        return
      if usercar['golden'] == True:
        usercarname = f"{star} Golden " + usercarname
      l = discord.Embed(title="Car locked",description=f"You locked your **{usercarname}**!\nYou cannot do anything with your car until you unlock it",color=color.green())
      l.set_footer(text="nice")
      await self.bot.cll.update_one({"id": ctx.author.id, "garage.id": usercar['id']}, {"$set": {"garage.$.locked": True}})
      await ctx.respond(embed=l)

async def unlockcar(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      try:
        carid = carid.lower()
      except:
        pass
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = user['garage'][-1]["index"]
      elif carid.lower() == "drive" or carid.lower() == "d":
        if user['drive'] == "":
          await ctx.respond("You are not driving anything")
          return
      try:
        usercar = [x for x in user['garage'] if x["index"] == int(carid)][0]
      except:
        await ctx.respond("You dont have this car ID in your garage")
        return
      usercarname = usercar['name']
      if usercar['locked'] == False:
        await ctx.respond("This car isnt even locked")
        return
      if usercar['golden'] == True:
        usercarname = f"{star} Golden " + usercarname
      l = discord.Embed(title="Car unlocked",description=f"You unlocked your **{usercarname}**!\nYou can do anything with your car now",color=color.green())
      l.set_footer(text="nice")
      await self.bot.cll.update_one({"id": ctx.author.id, "garage.id": usercar['id']}, {"$set": {"garage.$.locked": False}})
      await ctx.respond(embed=l)

async def drive(self, ctx, carid):
      if await blocked(ctx.author.id) == False:
        return
      if carid == '' or carid == None:
        user = await finduser(ctx.author.id)
        userdrive = user['drive']
        if userdrive != "":
          await ctx.respond(f"You are now driving your {getdrive(user, 'name')}")
        else:
          await ctx.respond("You are not driving any car! Give a car ID to drive a car")
        return
      try:
        carid = carid.lower()
      except:
        pass
      user = await finduser(ctx.author.id)
      usergarage = user['garage']
      if carid == "latest" or carid == "l":
        if len(user['garage']) == 0:
          await ctx.respond("You don't have any cars")
          return
        carid = usergarage[-1]["index"]
      elif carid == "drive" or carid == "d":
        carid = getdrive(user, 'id')
        return
      try:
        int(carid)
      except:
        await ctx.respond("Give a valid car ID!")
        return
      try:
        usercar = [car for car in usergarage if car["index"] == int(carid)][0]
      except:
        await ctx.respond("You dont have this car ID in your garage")
        return
      if user['drive'] != "":
        if int(carid) == getdrive(user, 'id'):
          await ctx.respond("You are already driving this car! To park the car type `/park`")
          return
      usercarname = usercar['name']
      usercargolden = usercar['golden']
      usercarlocked = usercar['locked']
      if usercarlocked == True:
        await ctx.respond("You cannot drive a locked car!")
        return
      if usercargolden == True:
        usercarname = f"{star} Golden " + usercarname
      await updateset(ctx.author.id,'drive', usercar['id'])
      await ctx.respond(f"You are now driving your {usercarname}!")

async def park(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      userdrive = user['drive']
      if userdrive == "":
        await ctx.respond("You are not driving any car")
        return
      await updateset(ctx.author.id,'drive',"")
      await ctx.respond(f"You parked your {getdrive(user, 'name')}!")

async def tictactoe(self, ctx, user, bet):
        if await blocked(ctx.author.id) == False:
            return
        userp = await finduser(ctx.author.id)
        if user is None:
            matrix = [[0,0,0], [0,0,0], [0,0,0]]
            turn = random.randint(0, 1)
            prerow, precol = [None, None]
            prematrix = None
            if turn == 0:
                embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                embed.add_field(name=f"It's {gettitle(userp)}{ctx.author.name}'s turn!", value=await functions.tttdisplay(matrix))

                view = interclass.ttt(ctx, ctx.author, matrix, turn)
                await ctx.respond(embed=embed, view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg

            while True:
                if turn == 0:
                    await view.wait()

                    if view.value is None:
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name}'s did not respond", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed)
                        await ctx.respond("You did not respond in time")
                        return

                    row, col = [view.value[0], view.value[1]]

                    matrix[row][col] = 2

                    if await functions.checkwin(matrix):
                        rcash = random.randint(10, 30)
                        rcash = round(rcash + (rcash*userp['stats']['cha']/1000))
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} won the game and earned <:cash:1329017495536930886> {rcash}!", value=await functions.tttdisplay(matrix))

                        await updateinc(ctx.author.id, 'cash', rcash)

                        await msg.edit(embed=embed, view=None)

                        if prerow is not None or precol is not None or prematrix is not None:
                            # Blacklist the previous AI move because the AI lost after that move
                            try:
                                tttlose[repr(prematrix)].append([prerow, precol])
                            except KeyError:
                                tttlose[repr(prematrix)] = [[prerow, precol]]

                        return
                    elif await functions.checktie(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} and OV both tied!", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed, view=None)

                        if prerow is not None and precol is not None and prematrix is not None:
                            try:
                                if [prerow, precol] not in ttttie[repr(prematrix)] and [prerow, precol] not in tttlose[repr(prematrix)]:
                                    ttttie[repr(prematrix)].append([prerow, precol])
                            except KeyError:
                                ttttie[repr(prematrix)] = [[prerow, precol]]

                        return

                    turn = 1

                elif turn == 1:
                    embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                    embed.add_field(name=f"It's the Computer's turn! Thinking...", value=await functions.tttdisplay(matrix))

                    try:
                        await msg.edit(embed=embed, view=None)
                    except:
                        msg = await ctx.respond(embed=embed)

                    await asyncio.sleep(2)

                    if repr(matrix) in list(tttwin):
                        choices = []
                        row, col = random.choice(tttwin[repr(matrix)])
                    else:
                        # Provide all possible moves
                        choices = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
                        row, col = random.choice(choices)

                    # While this block is occupied or will lead to losing or will lead to tie
                    while matrix[row][col] != 0 or (repr(matrix) in list(tttlose) and [row, col] in tttlose[repr(matrix)]) or (repr(matrix) in list(ttttie) and [row, col] in ttttie[repr(matrix)]):
                        # Remove this move from all possible moves
                        choices.remove([row, col])
                        # If no possible moves left
                        if not len(choices):
                            if prerow is not None and precol is not None and prematrix is not None:
                                # Blacklist the previous move because no current move can prevent tying
                                try:
                                    if [prerow, precol] not in ttttie[repr(prematrix)]:
                                        ttttie[repr(prematrix)].append([prerow, precol])
                                except KeyError:
                                    ttttie[repr(prematrix)] = [[prerow, precol]]
                            # Provide all possible moves again
                            choices = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
                            row, col = random.choice(choices)
                            # While this block is occupied or will lead to losing
                            while matrix[row][col] != 0 or (repr(matrix) in list(tttlose) and [row, col] in tttlose[repr(matrix)]):
                                # Remove this move from all possible moves
                                choices.remove([row, col])
                                # If no possible moves left
                                if not len(choices):
                                    if prerow is not None and precol is not None and prematrix is not None:
                                        # Blacklist the previous move because no current move can prevent losing
                                        try:
                                            if [prerow, precol] not in tttlose[repr(prematrix)]:
                                                tttlose[repr(prematrix)].append([prerow, precol])
                                        except KeyError:
                                            tttlose[repr(prematrix)] = [[prerow, precol]]
                                    # Provide all possible moves again
                                    choices = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
                                    row, col = random.choice(choices)
                                    # While this block is occupied
                                    while matrix[row][col] != 0:
                                        # Remove this move from all possible moves
                                        choices.remove([row, col])
                                        row, col = random.choice(choices)
                                    break
                                else:
                                    row, col = random.choice(choices)
                            break
                        else:
                            row, col = random.choice(choices)

                    prerow, precol = [row, col]
                    prematrix = __import__('copy').deepcopy(matrix) # Before AI places

                    matrix[row][col] = 3

                    if await functions.checkwin(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                        embed.add_field(name=f"OV won the game! Too bad 4 you", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed, view=None)

                        try:
                            if [prerow, precol] not in tttwin[repr(prematrix)]:
                                tttwin[repr(prematrix)].append([prerow, precol])
                        except KeyError:
                            tttwin[repr(prematrix)] = [[prerow, precol]]

                        return
                    elif await functions.checktie(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} and OV both tied!", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed, view=None)

                        try:
                            if [prerow, precol] not in ttttie[repr(prematrix)] and [prerow, precol] not in tttlose[repr(prematrix)]:
                                ttttie[repr(prematrix)].append([prerow, precol])
                        except KeyError:
                            ttttie[repr(prematrix)] = [[prerow, precol]]

                        return

                    turn = 0

                    embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs OV", color=color.embed_background())
                    embed.add_field(name=f"It's {gettitle(userp)}{ctx.author.name}'s turn!", value=await functions.tttdisplay(matrix))

                    view = interclass.ttt(ctx, ctx.author, matrix, turn)
                    view.message = await msg.edit(embed=embed, view=view)

        elif user is not None:
            user2 = await finduser(user.id)
            if user2 is None:
                await ctx.respond("This user haven't started playing yet!")
                return
            if user == ctx.author:
                await ctx.respond("You can't play with yourself")
                ctx.command.reset_cooldown(ctx)
                return
            if bet is not None:
                if bet < 10:
                    await ctx.respond("You cannot bet lesser than <:cash:1329017495536930886> 10")
                    return
                if userp['cash'] < bet:
                    await ctx.respond("You don't even have that much cash")
                    return
                elif user2['cash'] < bet:
                    await ctx.respond("The user is too poor to afford the bet")
                    return
                try:
                    functions.ac(bet)
                except:
                    try:
                        bet = int(bet)
                    except:
                        await ctx.respond("You have to give a number!")
                        return

            view = interclass.Confirm(ctx, user)
            if bet is None:
                await ctx.respond(f"{user.mention}, {gettitle(userp)}{ctx.author.name} challenged you to a Tic-Tac-Toe game!\nDo you want to accept it?", view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg
            else:
                await ctx.respond(f"{user.mention}, {gettitle(userp)}{ctx.author.name} challenged you to a <:cash:1329017495536930886> {bet} bet Tic-Tac-Toe game!\nDo you want to accept it?", view=view)
                msg = await ctx.interaction.original_response()
                view.message = msg

            await view.wait()
            if view.value is None:
                await ctx.respond(f"{user} ignored you")
                return
            elif view.value is False:
                await ctx.respond(f"{user} is too scared to accept")
                return

            if bet is not None:
                await updateinc(ctx.author.id, 'cash', -bet)
                await updateinc(user.id, 'cash', -bet)

            matrix = [[0,0,0], [0,0,0], [0,0,0]]
            turn = random.randint(0, 1)

            if turn == 0:
                embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                embed.add_field(name=f"It's {gettitle(userp)}{ctx.author.name}'s turn!", value=await functions.tttdisplay(matrix))

                view = interclass.ttt(ctx, ctx.author, matrix, turn)
                view.message = await msg.edit(embed=embed, view=view)
            elif turn == 1:
                embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                embed.add_field(name=f"It's {gettitle(user2)}{user.name}'s turn!", value=await functions.tttdisplay(matrix))

                view = interclass.ttt(ctx, user, matrix, turn)
                view.message = await msg.edit(embed=embed, view=view)

            while True:
                if turn == 0:
                    await view.wait()

                    if view.value is None:
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name}'s did not respond", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed)
                        await ctx.respond("You did not respond in time")
                        return

                    row, col = [view.value[0], view.value[1]]

                    matrix[row][col] = 2

                    if await functions.checkwin(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        if bet is None:
                            embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} won the game!", value=await functions.tttdisplay(matrix))
                        else:
                            embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} won the game and earned <:cash:1329017495536930886> {round(bet*2*0.95)}!", value=await functions.tttdisplay(matrix))
                            await updateinc(ctx.author.id, 'cash', round(bet*2*0.95))

                        await msg.edit(embed=embed, view=None)

                        return
                    elif await functions.checktie(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} and {gettitle(user2)}{user.name} both tied!", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed, view=None)

                        if bet is not None:
                            await updateinc(ctx.author.id, 'cash', bet)
                            await updateinc(user.id, 'cash', bet)

                        return

                    turn = 1

                    embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                    embed.add_field(name=f"It's {gettitle(user2)}{user.name}'s turn!", value=await functions.tttdisplay(matrix))

                    view = interclass.ttt(ctx, user, matrix, turn)
                    view.message = await msg.edit(embed=embed, view=view)

                elif turn == 1:
                    await view.wait()

                    if view.value is None:
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(user2)}{user.name}'s did not respond", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed)
                        await ctx.respond(f"{user.mention} You did not respond in time")
                        return

                    row, col = [view.value[0], view.value[1]]

                    matrix[row][col] = 3

                    if await functions.checkwin(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        if bet is None:
                            embed.add_field(name=f"{gettitle(user2)}{user.name} won the game!", value=await functions.tttdisplay(matrix))
                        else:
                            embed.add_field(name=f"{gettitle(user2)}{user.name} won the game and earned <:cash:1329017495536930886> {round(bet*2*0.95)}!", value=await functions.tttdisplay(matrix))
                            await updateinc(user.id, 'cash', round(bet*2*0.95))

                        await msg.edit(embed=embed, view=None)

                        return
                    elif await functions.checktie(matrix):
                        embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                        embed.add_field(name=f"{gettitle(userp)}{ctx.author.name} and {gettitle(user2)}{user.name} both tied!", value=await functions.tttdisplay(matrix))

                        await msg.edit(embed=embed, view=None)

                        if bet is not None:
                            await updateinc(ctx.author.id, 'cash', bet)
                            await updateinc(user.id, 'cash', bet)

                        return

                    turn = 0

                    embed = discord.Embed(title="Tic Tac Toe", description=f"{gettitle(userp)}{ctx.author.name} vs {gettitle(user2)}{user.name}", color=color.embed_background())
                    embed.add_field(name=f"It's {gettitle(userp)}{ctx.author.name}'s turn!", value=await functions.tttdisplay(matrix))

                    view = interclass.ttt(ctx, ctx.author, matrix, turn)
                    view.message = await msg.edit(embed=embed, view=view)

async def define(self, ctx, query):
        if await blocked(ctx.author.id) == False:
            return
        await ctx.respond("This command is temporary unavailable due to Discord limitations")
        return
        if query is None:
            await ctx.respond("Provide a word to define!")
            return
        r = requests.get(f"https://www.google.com/search?q=define+{query.replace(' ', '+')}", headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        word = soup.find('span', {"data-dobid": "hdw"})
        if not word:
            embed = discord.Embed(title=f"Definition for {query}", description=f"Hmmm, couldn't find a definition for this word `{query}`", color=color.red()).set_footer(text="Powered by Google\nDefinitions from Oxford Languages")
            await ctx.respond(embed=embed)
            return
        embed = discord.Embed(title=f"Definition for {query}", description=f"**{word.text}**", color=color.blurple()).set_footer(text="Powered by Google\nDefinitions from Oxford Languages")
        i = 0
        for parts_of_speech in soup.find_all('div', {"jsname": "r5Nvmf"}):
            if parts_of_speech.find('span', {'class': 'YrbPuc'}) is None:
                break
            embed.add_field(name=parts_of_speech.find('span', {'class': 'YrbPuc'}).text, value="", inline=False)
            index = 1
            for definitions in parts_of_speech.find_all("li", {"jsname": "gskXhf"}):
                for definition in definitions.find_all("div", {"data-dobid": "dfn"}):
                    embed.fields[i].value += f"**{index}.** {definition.span.text}\n"
                    index += 1
                for example in definitions.find_all("div", {"class": "ubHt5c"}):
                    embed.fields[i].value += f"**Example** {example.text}\n"
                embed.fields[i].value += "\n"
            i += 1
        html = requests.get(f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch", headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')
        all_script_tags = soup.select("script")
        matched_images_data = "".join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
        matched_images_data_fix = json.dumps(matched_images_data)
        matched_images_data_json = json.loads(matched_images_data_fix)
        matched_google_image_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)
        matched_google_images_thumbnails = ", ".join(
            re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                       str(matched_google_image_data))).split(", ")
        thumbnails = [bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails]
        removed_matched_google_images_thumbnails = re.sub(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))
        img_link = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)
        page = 1
        embed.set_image(url=img_link[page-1])
        view = interclass.Page(ctx, ctx.author, True, False)
        await ctx.respond(embed=embed, view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg
        while True:
            await view.wait()
            if view.value is None:
                return
            elif view.value == "left":
                page -= 1
            elif view.value == "right":
                page += 1
            embed.set_image(url=img_link[page-1])
            if page == 1:
                view = interclass.Page(ctx, ctx.author, True, False)
            elif page == len(img_link):
                view = interclass.Page(ctx, ctx.author, False, True)
            else:
                view = interclass.Page(ctx, ctx.author, False, False)
            view.message = await msg.edit(embed=embed, view=view)

async def image(self, ctx, query):
        if query is None:
          await ctx.respond("You have to give something to search! Example `/search apple`")
          return
        await ctx.respond("This command is temporary unavailable due to Discord limitations")
        return
        page = 1
        html = requests.get(f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch", headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')
        all_script_tags = soup.select("script")
        matched_images_data = "".join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
        matched_images_data_fix = json.dumps(matched_images_data)
        matched_images_data_json = json.loads(matched_images_data_fix)
        matched_google_image_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)
        matched_google_images_thumbnails = ", ".join(
            re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                       str(matched_google_image_data))).split(", ")
        thumbnails = [bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails]
        removed_matched_google_images_thumbnails = re.sub(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))
        img_link = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)

        embed = discord.Embed(title=f"Searched image for {query}", color=color.blurple()).set_footer(text="Powered by Google Images")
        embed.set_image(url=img_link[page-1])
        view = interclass.Page(ctx, ctx.author, True, False)
        await ctx.respond(embed=embed, view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg
        while True:
            await view.wait()
            if view.value is None:
                return
            elif view.value == "left":
                page -= 1
            elif view.value == "right":
                page += 1
            embed.set_image(url=img_link[page-1])
            if page == 1:
                view = interclass.Page(ctx, ctx.author, True, False)
            elif page == len(img_link):
                view = interclass.Page(ctx, ctx.author, False, True)
            else:
                view = interclass.Page(ctx, ctx.author, False, False)
            view.message = await msg.edit(embed=embed, view=view)

async def news(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      if user['s'] == 70:
        await updateset(ctx.author.id, 's', 71)
      server = await self.bot.gcll.find_one({"id": 863025676213944340})
      updates = [server['updates'][ts] for ts in list(server['updates'].keys())]
      announcement = [server['announcement'][ts] for ts in list(server['announcement'].keys())]
      t = "\n\U0001f4a0 "
      upd = discord.Embed(title="Latest updates and announcements", color=color.blurple()).set_footer(text="Join our official server for detailed information")
      upd.add_field(name="Update changes", value=f"{t}{(t.join(sorted(updates, key=lambda x: list(server['updates'].keys())[list(server['updates'].values()).index(x)], reverse=True)[:2]))[:512]}", inline=True)
      upd.add_field(name="Announcement contents", value=f"{t}{(t.join(sorted(announcement, key=lambda x: list(server['announcement'].keys())[list(server['announcement'].values()).index(x)], reverse=True)[:2]))[:512]}", inline=True)
      upd.timestamp = datetime.now()
      await ctx.respond(embed=upd)

async def claim(self, ctx, code):
      if await blocked(ctx.author.id) == False:
        return
      if await self.bot.dcll.find_one({"id": ctx.author.id}) is None and code is None:
        await ctx.respond("You have to donate or enter a code to claim something")
        return

      user = await self.bot.cll.find_one({"id": ctx.author.id})

      if code:
        code = code.lower()
        server = await self.bot.gcll.find_one({"id": 863025676213944340})
        if code not in server['codes']:
          await ctx.respond(f"Invalid code `{code}`!")
          return
        elif code in user['codes']:
          await ctx.respond(f"You already claimed this code before `{code}`!")
          return
        elif server['codes'][code] <= round(time.time()):
          await ctx.respond(f"This code has expired! Too bad")
          return
        await codes.dispatcher[code](ctx, ctx.author)
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"codes": code}})
        return

      duser = await self.bot.dcll.find_one({"id": ctx.author.id})
      if 'Royal Pack' in duser:
        userroyalpack = duser['Royal Pack']
      else:
        userroyalpack = 0
      if 'Royal+ Pack' in duser:
        userroyalppack = duser['Royal+ Pack']
      else:
        userroyalppack = 0
      if 'Stack of Tokens' in duser:
        userskt = duser["Stack of Tokens"]
      else:
        userskt = 0
      if 'Pile of Tokens' in duser:
        userpt = duser["Pile of Tokens"]
      else:
        userpt = 0
      if 'Stash of Tokens' in duser:
        usersht = duser["Stash of Tokens"]
      else:
        usersht = 0
      if 'Chest of Tokens' in duser:
        userct = duser["Chest of Tokens"]
      else:
        userct = 0
      donatearray = []
      userdonor = user['donor']

      if userroyalpack == 0 and userroyalppack == 0 and userskt == 0 and userpt == 0 and usersht == 0 and userct == 0:
        await ctx.respond("You have nothing to claim")
        return

      if userroyalpack > 0:
        await updateinc(ctx.author.id, 'storage.Royal Case', userroyalpack*2)
        donatearray.append(f"{userroyalpack} Royal Pack")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Royal Pack": 0}})
        await updateset(ctx.author.id, 'donor', 1)
        if userdonor == 0 or userdonor == 2:
          await updateset(ctx.author.id, 'timer.donate', round(time.time())+(2592000*userroyalpack))
        elif userdonor == 1:
          await updateinc(ctx.author.id, 'timer.donate', 2592000)

      if userroyalppack > 0:
        await updateinc(ctx.author.id, 'storage.Royal Case', userroyalppack*4)
        donatearray.append(f"{userroyalppack} Royal+ Pack")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Royal+ Pack": 0}})
        await updateset(ctx.author.id, 'donor', 2)
        if userdonor == 0 or userdonor == 1:
          await updateset(ctx.author.id, 'timer.donate', round(time.time())+(2592000*userroyalppack))
        elif userdonor == 2:
          await updateinc(ctx.author.id, 'timer.donate', 2592000)

      if userskt > 0:
        await updateinc(ctx.author.id, 'token', 340*userskt)
        donatearray.append(f"{userskt*340} Tokens")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Stack of Tokens": 0}})
      
      if userpt > 0:
        await updateinc(ctx.author.id, 'token', 700*userpt)
        donatearray.append(f"{userpt*700} Tokens")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Pile of Tokens": 0}})

      if usersht > 0:
        await updateinc(ctx.author.id, 'token', 1460*usersht)
        donatearray.append(f"{usersht*1460} Tokens")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Stash of Tokens": 0}})

      if userct > 0:
        await updateinc(ctx.author.id, 'token', 3080*userct)
        donatearray.append(f"{userct*3080} Tokens")
        await self.bot.dcll.update_one({"id": ctx.author.id}, {"$set": {"Chest of Tokens": 0}})

      splitted = ", ".join([str(i) for i in donatearray])
      pembed = discord.Embed(title = "Thanks for purchasing!", description = f"You claimed **{splitted}**.", color = color.green())
      if userroyalpack > 0 or userroyalppack > 0:
        pembed.set_footer(text = "You are now a Royal member!")
      await ctx.respond("Check your DMs! Thanks for supporting us!")
      userdm = await ctx.author.create_dm()
      await userdm.send(embed=pembed)

async def daily(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      usertimer = user['timer']
      userstreak = user['dailystreak']
      try:
        userdaily = usertimer['daily']
        await ctx.respond(f"You have to wait {ab(userdaily-round(time.time()))} before claiming another daily! The cooldown for this command is 20 hours. You are on a {userstreak} daily streak!")
        return
      except:
        pass
      userdonor = user['donor']
      cash = random.randint(80, 120)
      cash = round(cash + (cash*user['stats']['cha']/1000) + (cash*dboost(userdonor)) + ((cash*0.01)*userstreak))
      await self.bot.cll.update_one({"id": ctx.author.id}, {"$inc": {"cash": round(cash), "dailystreak": 1}, "$set": {"timer.daily": round(time.time())+72000, "rp": (user["lvl"]//10)+1}})
      user = await finduser(ctx.author.id)
      if user['s'] == 42:
        await updateset(ctx.author.id, 's', 43)
      usertimer = user['timer']
      embed = discord.Embed(title="Daily", description=f"You claimed <:cash:1329017495536930886> {round(cash)} from your daily today!\nYou are on a {userstreak+1} daily streak", color=color.green())
      bonus = []
      bribe, medkit = 0, 0
      for _ in range(random.choice([4,4,4,3,3,3,2,2,2,2])):
        ranitem = random.choice(['Bribe', 'Medical Kit'])
        bribe += 1 if ranitem == "Bribe" else 0
        medkit += 1 if ranitem == "Medical Kit" else 0
      if bribe != 0:
        bonus.append(f"You got **{bribe}** Bribe!")
        await updateinc(ctx.author.id, "storage.Bribe", bribe)
      if medkit != 0:
        bonus.append(f"You got **{medkit}** Medical Kit!")
        await updateinc(ctx.author.id, "storage.Medical Kit", medkit)
      if bonus != []:
        embed.add_field(name="Bonus!", value="\n".join(bonus))
      await ctx.respond(embed=embed)

async def weekly(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      userdonor = user['donor']
      userlvl = user['lvl']
      if userlvl < 10:
        await ctx.respond("You have to be at least level 10 to claim weekly!")
        return
      if userdonor < 1:
        await ctx.respond("This command is only for Royal Members!")
        return
      usertimer = user['timer']
      try:
        userweekly = usertimer['weekly']
        await ctx.respond(f"You have to wait {ab(userweekly-round(time.time()))} before claiming another weekly! The cooldown for this command is 6 days and 20 hours")
        return
      except:
        pass
      userdonor = user['donor']
      cash = random.randint(800, 1600)
      cash = round(cash + (cash*user['stats']['cha']/1000) + (cash*dboost(userdonor)))
      await updateinc(ctx.author.id, 'cash', round(cash))
      await updateset(ctx.author.id, 'timer.weekly', round(time.time())+590400)
      embed = discord.Embed(title="Weekly", description=f"You claimed <:cash:1329017495536930886> {round(cash)} from your weekly this week!", color=color.green())
      bonus = []
      bribe = medkit = carkey = garagekey = 0
      for _ in range(random.choice([3,3,3,4,4,4,4,5,2,2,2])):
        ranitem = random.choice(['Bribe', 'Medical Kit', 'Bribe', 'Medical Kit', 'Average Car Key', 'Garage Key'])
        bribe += 1 if ranitem == "Bribe" else 0
        medkit += 1 if ranitem == "Medical Kit" else 0
        carkey += 1 if ranitem == "Average Car Key" else 0
        garagekey += 1 if ranitem == "Garage Key" else 0
      if bribe != 0:
        bonus.append(f"You got **{bribe}** Bribe!")
        await updateinc(ctx.author.id, "storage.Bribe", bribe)
      if medkit != 0:
        bonus.append(f"You got **{medkit}** Medical Kit!")
        await updateinc(ctx.author.id, "storage.Medical Kit", medkit)
      if carkey != 0:
        bonus.append(f"You got **{carkey}** Average Car Key!")
        await updateinc(ctx.author.id, "storage.Average Car Key", carkey)
      if garagekey != 0:
        bonus.append(f"You got **{garagekey}** Garage Key!")
        await updateinc(ctx.author.id, "storage.Garage Key", garagekey)
      if bonus != []:
        embed.add_field(name="Bonus!", value="\n".join(bonus))
      await ctx.respond(embed=embed)

async def donate(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      dembed = discord.Embed(title="Donate",description="Donate to support OV Bot! By donating you can get a Royal status which gives you different perks and some Royal cases! Type `/royalperks` for more information!\n\n[**Donate here from our official website!**](https://ovbot.up.railway.app/)",color=color.blue())
      dembed.set_footer(text="Remember to type `/claim` after donating!")
      await ctx.respond(embed=dembed)

async def royalperks(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      dpembed = discord.Embed(title="Royal Perks",description="[**Royal Pack**](https://ovbot.up.railway.app/)\n2 Royal Cases\n30 Days of Royal status <:royal:1328385115503591526>\nGain access to all premium commands\n50% Boost on cash earned from all crimes\n20\% extra luck on everything\n\n[**Royal+ Pack**](https://ovbot.up.railway.app/)\n4 Royal Cases\n30 Days of Royal+ status <:royal_plus:1328385118347464804>\nTax exempted when transferring cash\n100% Boost on cash earned from all crimes\n50\% extra luck on everything\nDouble gains from gym training",color=color.blue())
      dpembed.set_footer(text="Remember to type `/claim` after making a purchase!")
      await ctx.respond(embed=dpembed)

async def invite(self, ctx):
      invembed = discord.Embed(title="Invite the bot",description="[**Invite the bot to your server!**](https://discord.com/oauth2/authorize?client_id=863028787708559400&permissions=277767121985&response_type=code&redirect_uri=https%3A%2F%2Fovbot.up.railway.app%2F&integration_type=0&scope=identify+bot+applications.commands+applications.commands.permissions.update+messages.read)",color=color.blue())
      invembed.set_footer(text="Thanks for inviting!")
      await ctx.respond(embed=invembed)

async def server(self, ctx):
      servembed = discord.Embed(title="Join our official server",description="Our official server perks:\nGives double EXP\nHigher chance to succeed in crimes\nHigher chance for Random Events\n\n[**Join our official server here!**](https://discord.gg/bBeCcuwE95)",color=color.blue())
      servembed.timestamp = datetime.now()
      await ctx.respond(embed=servembed)

async def disable(self, ctx, cmd, trueorfalse):
      guild = await self.bot.gcll.find_one({"id": 863025676213944340})
      guildmaintenance = guild['maintenance']
      if guildmaintenance == True:
        return
      if cmd == None:
        await ctx.respond("Commands you can disable: Attack, Larceny, Race\nThe default setting for every command is False\nTo disable a command you have to set it to True")
        return
      if trueorfalse == None:
        await ctx.respond("You have to type True or False after the command you want to disable")
        return
      if trueorfalse.lower() == "true":
        trueorfalse = False
        trueorfalser = True
      elif trueorfalse.lower() == "false":
        trueorfalse = True
        trueorfalser = False
      if cmd.lower() == "attack" and not trueorfalse == None:
        await self.bot.gcll.update_one({"id": ctx.guild.id}, {"$set": {'attack': trueorfalse}})
        await ctx.respond(f"Disabled command for Attack: {trueorfalser}")
      elif cmd.lower() == "larceny" and not trueorfalse == None:
        await self.bot.gcll.update_one({"id": ctx.guild.id}, {"$set": {'larceny': trueorfalse}})
        await ctx.respond(f"Disabled command for Larceny: {trueorfalser}")
      elif cmd.lower() == "race" and not trueorfalse == None:
        await self.bot.gcll.update_one({"id": ctx.guild.id}, {"$set": {'race': trueorfalse}})
        await ctx.respond(f"Disabled command for Race: {trueorfalser}")
      else:
        await ctx.respond("You can only disable these commands: Attack, Larceny, Race\nThe default setting for every commands is False\nTo disable a command you have to set it to True")
        return

async def ping(self, ctx):
      before = time.monotonic()
      botlatency = round(self.bot.latency * 1000)
      await ctx.respond("Pong!")
      msg = await ctx.interaction.original_response()
      await msg.edit(content=f'Pong! In **{botlatency}ms**')
      await msg.edit(content=f'Pong! In **{botlatency}ms** Response time in **{round((time.monotonic() - before) * 1000)}ms**')

async def id(self, ctx, user):
    user = user or ctx.author
    await ctx.respond(f"{user}'s Discord ID is: {user.id}")

async def vote(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      user = await finduser(ctx.author.id)
      usertimer = user['timer']
      try:
        userdbl = usertimer['dbl']
        dblurl = f"**Discord Bot List** | Vote again in: {ab(userdbl-round(time.time()))}!"
      except:
        dblurl = "[**Discord Bot List**](https://discordbotlist.com/bots/ov/upvote)"
      try:
        usertopgg = usertimer['topgg']
        topggurl = f"**Top.gg** | Vote again in: {ab(usertopgg-round(time.time()))}!"
      except:
        topggurl = "[**Top.gg**](https://top.gg/bot/863028787708559400/vote)"
      voteembed = discord.Embed(title="Upvote!",description=f"Upvote the bot to get rewards!\nYou can get 1 Safe, 2 Average Car Keys and <:cash:1329017495536930886> 500 Cash by voting in any of the website below every 12 hours!\n\n{dblurl}\n{topggurl}",color=color.blue())
      voteembed.timestamp = datetime.now()
      await ctx.respond(embed=voteembed)

async def tutorial(self, ctx):
      guild = await self.bot.gcll.find_one({"id": 863025676213944340})
      if guild['maintenance'] == True and not ctx.author.id == 615037304616255491:
        return

      await functions.tutorial(ctx)

async def events(self, ctx):
      if await blocked(ctx.author.id) == False:
        return
      if (await finduser(ctx.author.id))['s'] == 68:
        await updateset(ctx.author.id, 's', 69)
      server = await self.bot.gcll.find_one({"id": 863025676213944340})
      expiredevents = [t for t in server['events'] if int(t) <= round(time.time())]
      if expiredevents:
        for events in expiredevents:
          await self.bot.gcll.update_one({"id": 863025676213944340}, {"$unset": {f"events.{events}": 1}})
      events = [f"\n\U0001f4a0 (Expires in {ab(int(t) - round(time.time()))})\n" + server['events'][t] for t in server['events'] if int(t) > round(time.time())]
      if not len(events):
        events = ["No events"]
      embed = discord.Embed(title="Ongoing events", description="\n".join(events), color=color.blurple())
      await ctx.respond(embed=embed)

async def quarantine(self, ctx):
      if await blocked(ctx.author.id) is False:
        return

      user = await finduser(ctx.author.id)

      try:
        if user['timer']['q'] > round(time.time()):
          cdembed = discord.Embed(title = "Command on cooldown!", color = color.gold())
          cdembed.add_field(name = "You have to wait before typing the command again!", value = f"Try again after `{ab(user['timer']['q']-round(time.time()))}`!\nCooldown for this command is `{ab(172800)}`")
          cdembed.set_footer(text = "Chill!")

          await ctx.respond(embed=cdembed)
          return
      except:
        pass

      if ctx.guild.id not in user['q']:

        if len(user['q']) >= 3:
          await ctx.respond("You cannot quarantine yourself in more than 3 servers!")
          ctx.command.reset_cooldown(ctx)
          return

        view = interclass.Confirm(ctx, ctx.author)
        await ctx.respond("Are you sure you want to quarantine yourself?\nYou cannot use any bot commands and other users cannot interact with you until you release yourself!\nYou can only use this command every 48 hours", view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        await view.wait()

        if view.value is None:
          await ctx.respond("Imagine not responding")
          ctx.command.reset_cooldown(ctx)
          return
        elif view.value is False:
          await ctx.respond("ok bye")
          ctx.command.reset_cooldown(ctx)
          return

        view = interclass.Confirm(ctx, ctx.author)
        view.message = await msg.edit("Double confirm?", view=view)

        await view.wait()

        if view.value is None:
          await ctx.respond("Imagine not responding")
        elif view.value is False:
          await ctx.respond("ok bye")
          ctx.command.reset_cooldown(ctx)
          return

        await updateset(ctx.author.id, "timer.q", round(time.time())+172800)
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$push": {"q": ctx.guild.id}})

        embed = discord.Embed(title="Quarantined", description="You quarantined yourself from this server!\nFrom now on you cannot use any bot commands and other users cannot interact with you until you release yourself\nYou cannot release yourself for the next 48 hours!", color=color.gold()).set_footer(text="imagine getting quarantined")

        await msg.edit(content="", embed=embed, view=None)

      else:

        view = interclass.Confirm(ctx, ctx.author)
        await ctx.respond("Are you sure you want to release yourself?\nYou can only use this command every 48 hours", view=view)
        msg = await ctx.interaction.original_response()
        view.message = msg

        await view.wait()

        if view.value is None:
          await ctx.respond("Imagine not responding")
          ctx.command.reset_cooldown(ctx)
          return
        elif view.value is False:
          await ctx.respond("ok bye")
          ctx.command.reset_cooldown(ctx)
          return

        view = interclass.Confirm(ctx, ctx.author)
        view.message = await msg.edit("Double confirm?", view=view)

        await view.wait()

        if view.value is None:
          await ctx.respond("Imagine not responding")
        elif view.value is False:
          await ctx.respond("ok bye")
          ctx.command.reset_cooldown(ctx)
          return


        await updateset(ctx.author.id, "timer.q", round(time.time())+172800)
        await self.bot.cll.update_one({"id": ctx.author.id}, {"$pull": {"q": ctx.guild.id}})

        embed = discord.Embed(title="Released", description="You released yourself from this server!\nFrom now on you can use all the bot commands and other users can interact with you", color=color.gold()).set_footer(text="haha yes release yourself so you can get mugged")

        await msg.edit(content="", embed=embed, view=None)