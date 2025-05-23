from functions import updateinc


async def christmas2021(ctx, user):
	await updateinc(user.id, "storage.Santa Hat", 1)
	await ctx.respond("You claimed 1 Santa Hat!")

async def happy2022(ctx, user):
	await updateinc(user.id, "storage.2022 Glasses", 1)
	await updateinc(user.id, "cash", 2022)
	await ctx.respond("You claimed 1 2022 Glasses and <:cash:1329017495536930886> 2022 Cash!")

async def valentine2022(ctx, user):
	await updateinc(user.id, "storage.Heart Glasses", 1)
	await updateinc(user.id, "storage.Chocolate", 2)
	await ctx.respond("You claimed 1 Heart Glasses and 2 Chocolate bars!")

async def grenade2(ctx, user):
	await updateinc(user.id, "storage.Grenade", 2)
	await ctx.respond("You claimed 2 Grenades!")

async def happy2025(ctx, user):
	await updateinc(user.id, "cash", 10000)
	await updateinc(user.id, "storage.Luxury Car Key", 1)
	await updateinc(user.id, "storage.Bribe", 10)
	await updateinc(user.id, "storage.Medical Kit", 10)
	await ctx.respond("You claimed <:cash:1329017495536930886> 10000 Cash, 10 Bribe, 10 Medical Kit and 1 Luxury Car Key!")

async def slot777(ctx, user):
	await updateinc(user.id, "storage.Luxury Car Key", 1)
	await updateinc(user.id, "storage.Lucky Clover", 1)
	await ctx.respond("You claimed 1 Luxury Car Key and 1 Lucky Clover!")

async def valentines2025(ctx, user):
	await updateinc(user.id, "cash", 5000)
	await updateinc(user.id, "storage.Tiny Angel Wings", 1)
	await updateinc(user.id, "storage.Chocolate", 2)
	await ctx.respond("You claimed <:cash:1329017495536930886> 5000, 1 Tiny Angel Wings and 2 Chocolate bars!")

async def giveaway4fun(ctx, user):
	await updateinc(user.id, "token", 20)
	await updateinc(user.id, "storage.Luxury Car Key", 1)
	await ctx.respond("You claimed 20 tokens and 1 Luxury Car Key!")

dispatcher = {"valentines2025": valentines2025, "christmas2021": christmas2021, "happy2022": happy2022, "valentine2022": valentine2022, "grenade2": grenade2, "happy2025": happy2025, "slot777": slot777, "giveaway4fun": giveaway4fun}
