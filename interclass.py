import discord
import functions
from functions import finduser

class Wishlistcar(discord.ui.Modal):
    def __init__(self, level) -> None:
        super().__init__(title=f"Wishlist Slot {level}")
        self.add_item(discord.ui.InputText(label="Car name", placeholder="Enter a car name (Leave empty to remove a car)", required=False))
        self.value = None
        self.interaction = None

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        self.value = self.children[0].value
        self.interaction = interaction
        await interaction.response.defer()

class Wishlist(discord.ui.View):
  def __init__(self, user, top = False, bottom = False, locked = True):
    super().__init__(timeout=300)
    self.value = None
    self.interaction = None
    self.user = user

    upbutton = discord.ui.Button(emoji="\u2B06\uFE0F", style=discord.ButtonStyle.primary)
    if top:
      upbutton.disabled = True
    self.add_item(upbutton)
    upbutton.callback = self.upbutton

    editbutton = discord.ui.Button(emoji="\u270F\uFE0F", style=discord.ButtonStyle.primary)
    if locked:
      editbutton.disabled = True
    self.add_item(editbutton)
    editbutton.callback = self.editbutton

    downbutton = discord.ui.Button(emoji="\u2B07\uFE0F", style=discord.ButtonStyle.primary)
    if bottom:
      downbutton.disabled = True
    self.add_item(downbutton)
    downbutton.callback = self.downbutton

  async def upbutton(self, interaction: discord.Interaction):
    self.stop()
    self.value = "up"
    await interaction.response.defer()

  async def downbutton(self, interaction: discord.Interaction):
    self.stop()
    self.value = "down"
    await interaction.response.defer()

  async def editbutton(self, interaction: discord.Interaction):
    self.stop()
    self.value = "edit"
    self.interaction = interaction

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Confirm(discord.ui.View):
  def __init__(self, obj, user):
    super().__init__(timeout=20)
    self.obj = obj
    self.value = None
    self.user = user
    self.interaction = None

  @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
  async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = True
    self.interaction = interaction
    await interaction.response.defer()
    # await interaction.response.send_message("Confirming", ephemeral=True)

  @discord.ui.button(label="No", style=discord.ButtonStyle.red)
  async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = False
    await interaction.response.defer()
    # await interaction.response.send_message("Cancelling", ephemeral=True)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Submit(discord.ui.View):
  def __init__(self, obj, user):
    super().__init__(timeout=60)
    self.obj = obj
    self.value = None
    self.user = user
    self.interaction = None

  @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
  async def submit(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = True
    self.interaction = interaction
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)
    # await interaction.response.send_message("Confirming", ephemeral=True)

  @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
  async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = False
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)
    # await interaction.response.send_message("Cancelling", ephemeral=True)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Approve(discord.ui.View):
  def __init__(self, ctx, left = False, approved = False, right = False):
    super().__init__(timeout=300)
    self.ctx = ctx
    self.value = None
    self.interaction = None

    leftbutton = discord.ui.Button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
    if left:
      leftbutton.disabled = True
    self.add_item(leftbutton)
    leftbutton.callback = self.left

    approvebutton = discord.ui.Button(label="Approve", style=discord.ButtonStyle.green)
    if approved:
      approvebutton.disabled = True
    self.add_item(approvebutton)
    approvebutton.callback = self.approve

    modifybutton = discord.ui.Button(label="Modify", style=discord.ButtonStyle.primary, row=1)
    if approved:
      modifybutton.disabled = True
    self.add_item(modifybutton)
    modifybutton.callback = self.modify

    modify2button = discord.ui.Button(label="Modify 2", style=discord.ButtonStyle.primary, row=1)
    if approved:
      modify2button.disabled = True
    self.add_item(modify2button)
    modify2button.callback = self.modify2

    rejectbutton = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)
    if approved:
      rejectbutton.disabled = True
    self.add_item(rejectbutton)
    rejectbutton.callback = self.reject

    rightbutton = discord.ui.Button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
    if right:
      rightbutton.disabled = True
    self.add_item(rightbutton)
    rightbutton.callback = self.right

  async def left(self, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  async def right(self, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  async def approve(self, interaction: discord.Interaction):
    self.stop()
    self.value = "approve"
    self.interaction = interaction
    await interaction.response.defer()

  async def modify(self, interaction: discord.Interaction):
    self.stop()
    self.value = "modify"
    self.interaction = interaction

  async def modify2(self, interaction: discord.Interaction):
    self.stop()
    self.value = "modify2"
    self.interaction = interaction

  async def reject(self, interaction: discord.Interaction):
    self.stop()
    self.value = "reject"
    self.interaction = interaction

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("You are not allowed to perform such action!", ephemeral=True)
      return False
    return True

class Reject(discord.ui.Modal):
    def __init__(self, label) -> None:
        super().__init__(title="Reason of rejection")
        self.add_item(discord.ui.InputText(label=label, placeholder="Reason", required=False))
        self.value = None
        self.interaction = None

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        self.value = self.children[0].value
        self.interaction = interaction
        await interaction.response.defer()

class Modify(discord.ui.Modal):
    def __init__(self, name, price, speed, rank, chance) -> None:
        super().__init__(title="Modify suggestion")
        self.add_item(discord.ui.InputText(label=f"Car name ({name})"[:45], placeholder="New car name", required=False))
        self.add_item(discord.ui.InputText(label=f"Car price ({price})", placeholder="New car price", required=False))
        self.add_item(discord.ui.InputText(label=f"Car speed ({speed})", placeholder="New car speed", required=False))
        self.add_item(discord.ui.InputText(label=f"Car rank ({rank})", placeholder="New car rank", required=False))
        self.add_item(discord.ui.InputText(label=f"Car chance ({chance})", placeholder="New car chance", required=False))
        self.interaction = None

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        self.interaction = interaction
        await interaction.response.defer()

class Modify2(discord.ui.Modal):
    def __init__(self, specialty) -> None:
        super().__init__(title="Modify suggestion")
        self.add_item(discord.ui.InputText(label=f"Car specialty ({specialty})"[:45], placeholder="New car specialty", required=False))
        self.add_item(discord.ui.InputText(label="Car image", placeholder="New car image", required=False))
        self.interaction = None

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        self.interaction = interaction
        await interaction.response.defer()

class Three(discord.ui.View):
  def __init__(self, obj):
    super().__init__(timeout=30)
    self.obj = obj
    self.value = None

  @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "1"
    await interaction.response.defer()

  @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "2"
    await interaction.response.defer()

  @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "3"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.obj.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Rob(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Rob", style=discord.ButtonStyle.primary)
  async def rob(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = True
    await interaction.response.defer()

  @discord.ui.button(label="Escape", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = False
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Clown(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 1
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 2
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 3
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="I AM COLOUR BLIND", style=discord.ButtonStyle.primary)
  async def fourth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 4
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Beggar(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Look in the dumpster", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 1
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Beg for cash", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 2
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Look at the sky", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 3
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Business(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Buy more shares", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 1
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Hold the shares", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 2
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Sell all shares", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 3
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Trash(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Glass", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 1
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Paper", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 2
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Plastic", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = 3
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Chef(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None
    self.ing = []
    self.choice = 0

  @discord.ui.button(label="Carrot", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Carrot")
    self.value = 1
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Lettuce", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Lettuce")
    self.value = 2
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Cucumber", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Cucumber")
    self.value = 3
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Tomato", style=discord.ButtonStyle.primary)
  async def fourth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Tomato")
    self.value = 4
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Potato", style=discord.ButtonStyle.primary)
  async def fifth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Potato")
    self.value = 5
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Meat", style=discord.ButtonStyle.primary)
  async def sixth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Meat")
    self.value = 6
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Egg", style=discord.ButtonStyle.primary)
  async def seventh(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Egg")
    self.value = 7
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Cheese", style=discord.ButtonStyle.primary)
  async def eighth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Cheese")
    self.value = 8
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Flour", style=discord.ButtonStyle.primary)
  async def ninth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Flour")
    self.value = 9
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Sugar", style=discord.ButtonStyle.primary)
  async def tenth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Sugar")
    self.value = 10
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Milk", style=discord.ButtonStyle.primary)
  async def eleventh(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Milk")
    self.value = 11
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Salt", style=discord.ButtonStyle.primary)
  async def twelfth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Salt")
    self.value = 12
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Corn", style=discord.ButtonStyle.primary)
  async def thirteenth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Corn")
    self.value = 13
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Chili", style=discord.ButtonStyle.primary)
  async def fourteenth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Chili")
    self.value = 14
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Oil", style=discord.ButtonStyle.primary)
  async def fifteenth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.choice += 1
    self.ing.append("Oil")
    self.value = 15
    if self.choice == 3:
      self.stop()
      for child in self.children:
        child.disabled = True
      await interaction.response.edit_message(view=self)
      return
    button.disabled = True
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Kidnapper(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="On your left", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 1
    await interaction.response.defer()

  @discord.ui.button(label="Infront of you", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 2
    await interaction.response.defer()

  @discord.ui.button(label="On your right", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 3
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Kidnapper2(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Brute force", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Brute force"
    await interaction.response.defer()

  @discord.ui.button(label="Small talk", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Small talk"
    await interaction.response.defer()

  @discord.ui.button(label="Seduce", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Seduce"
    await interaction.response.defer()

  @discord.ui.button(label="Persuade", style=discord.ButtonStyle.primary)
  async def fourth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Persuade"
    await interaction.response.defer()

  @discord.ui.button(label="Threaten", style=discord.ButtonStyle.primary)
  async def fifth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Threaten"
    await interaction.response.defer()

  @discord.ui.button(label="Act pity", style=discord.ButtonStyle.primary)
  async def twelfth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Act pity"
    await interaction.response.defer()

  @discord.ui.button(label="Money", style=discord.ButtonStyle.primary)
  async def sixth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Money"
    await interaction.response.defer()

  @discord.ui.button(label="Candy", style=discord.ButtonStyle.primary)
  async def seventh(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Candy"
    await interaction.response.defer()

  @discord.ui.button(label="Beer", style=discord.ButtonStyle.primary)
  async def eighth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Beer"
    await interaction.response.defer()

  @discord.ui.button(label="Dog", style=discord.ButtonStyle.primary)
  async def ninth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Dog"
    await interaction.response.defer()

  @discord.ui.button(label="Food", style=discord.ButtonStyle.primary)
  async def tenth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Food"
    await interaction.response.defer()

  @discord.ui.button(label="Games", style=discord.ButtonStyle.primary)
  async def eleventh(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Games"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Kidnapper3(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Threaten them to transfer you money", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Threaten them to transfer you money"
    await interaction.response.defer()

  @discord.ui.button(label="Call their mom", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their mom"
    await interaction.response.defer()

  @discord.ui.button(label="Call their grandmother", style=discord.ButtonStyle.primary, row=1)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their grandmother"
    await interaction.response.defer()

  @discord.ui.button(label="Call their child", style=discord.ButtonStyle.primary, row=1)
  async def fourth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their child"
    await interaction.response.defer()

  @discord.ui.button(label="Call their best friend", style=discord.ButtonStyle.primary, row=1)
  async def fifth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their best friend"
    await interaction.response.defer()

  @discord.ui.button(label="Call their cousin", style=discord.ButtonStyle.primary, row=2)
  async def sixth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their cousin"
    await interaction.response.defer()

  @discord.ui.button(label="Call their lover", style=discord.ButtonStyle.primary, row=2)
  async def seventh(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call their lover"
    await interaction.response.defer()

  @discord.ui.button(label="Call a police", style=discord.ButtonStyle.primary, row=2)
  async def eighth(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "Call a police"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Respect(discord.ui.View):
  def __init__(self, obj):
    super().__init__(timeout=15)
    self.obj = obj
    self.value = None

  @discord.ui.button(label="F", style=discord.ButtonStyle.primary)
  async def respect(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = True
    self.user = interaction.user
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

class Join(discord.ui.View):
  def __init__(self, joined, victim):
    super().__init__(timeout=60)
    self.joined = joined
    self.victim = victim

  @discord.ui.button(label="Join larceny", style=discord.ButtonStyle.green)
  async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
    if interaction.user.id not in self.joined:
      self.joined.append(interaction.user.id)
      await interaction.response.send_message(f"{interaction.user.name} joined the larceny.")
    else:
      await interaction.response.send_message(f"Chill, you already joined the larceny", ephemeral=True)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user == self.victim:
      await interaction.response.send_message("You cannot commit larceny on yourself idiot", ephemeral=True)
      return False
    elif await finduser(interaction.user.id) == None:
      await interaction.response.send_message("You havent started OV Bot yet!\nType `ov tutorial` to start playing!", ephemeral=True)
      return False
    return True

class Attww(discord.ui.View):
  def __init__(self, obj, name, flee = False, usergrenade = 0):
    super().__init__(timeout=40)
    self.obj = obj
    self.value = None
    self.name = name
    button = discord.ui.Button(label=self.name, style=discord.ButtonStyle.primary)
    self.add_item(button)
    button.callback = self.second
    button1 = discord.ui.Button(label="Flee", style=discord.ButtonStyle.primary)
    if not flee:
      button1.disabled = True
    self.add_item(button1)
    button1.callback = self.third

    if usergrenade != 0:
      button2 = discord.ui.Button(label=f"Grenade x{usergrenade}", style=discord.ButtonStyle.primary)
      self.add_item(button2)
      button2.callback = self.fourth

  @discord.ui.button(label="Fist", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.value = "1"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def second(self, interaction: discord.Interaction):
    self.value = "2"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def third(self, interaction: discord.Interaction):
    self.value = "3"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def fourth(self, interaction: discord.Interaction):
    self.value = "4"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.obj.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Att(discord.ui.View):
  def __init__(self, obj, flee = False, usergrenade = 0):
    super().__init__(timeout=40)
    self.obj = obj
    self.value = None
    button = discord.ui.Button(label="No weapon", style=discord.ButtonStyle.primary, disabled=True)
    self.add_item(button)
    button1 = discord.ui.Button(label="Flee", style=discord.ButtonStyle.primary)
    if not flee:
      button1.disabled = True
    self.add_item(button1)
    button1.callback = self.third

    if usergrenade != 0:
      button2 = discord.ui.Button(label=f"Grenade x{usergrenade}", style=discord.ButtonStyle.primary)
      self.add_item(button2)
      button2.callback = self.fourth

  @discord.ui.button(label="Fist", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.value = "1"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def third(self, interaction: discord.Interaction):
    self.value = "3"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def fourth(self, interaction: discord.Interaction):
    self.value = "4"
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.obj.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Attl(discord.ui.View):
  def __init__(self, obj):
    super().__init__(timeout=40)
    self.obj = obj
    self.value = None

  @discord.ui.button(label="Mug", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "1"
    await interaction.response.defer()

  @discord.ui.button(label="Hospitalize", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "2"
    await interaction.response.defer()

  @discord.ui.button(label="Walk away", style=discord.ButtonStyle.primary)
  async def third(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "3"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.obj.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Attll(discord.ui.View):
  def __init__(self, obj, logs):
    super().__init__(timeout=300)
    self.obj = obj
    self.logs = logs
    self.value = None

  @discord.ui.button(label="Check logs", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.value = "1"
    self.stop()
    await interaction.response.send_message("```Latest 20 logs\n"+"\n".join(self.logs[-20:])+"```", ephemeral=True)

  @discord.ui.button(label="Delete this message", style=discord.ButtonStyle.red)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.value = None
    self.stop()
    await interaction.message.delete()
    return

  async def on_timeout(self):
    try:
      self.stop()
      for child in self.children:
        child.disabled = True
      self.value = None
      await self.message.edit(view=self)
    except:
      pass

  async def interaction_check(self, interaction):
    if interaction.user != self.obj.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Help_select(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.select(placeholder='Command categories', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Main commands', description='Main and common important commands', emoji='\U0001f3e0', value="main"),
    discord.SelectOption(label='City commands', description='Explore the city', emoji='\U0001f3d9', value="city"),
    discord.SelectOption(label='Crime commands', description='Crimes to earn cash', emoji='\U0001f6a8', value="crime"),
    discord.SelectOption(label='Car commands', description='Manage your cars', emoji='\U0001f3ce', value="car"),
    discord.SelectOption(label='Fun commands', description='Fun commands when you are bored', emoji='\U0001f389', value="fun"),
    discord.SelectOption(label='Other commands', description='Other helpful commands', emoji='\U00002699', value="other"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Blackjack(discord.ui.View):
  def __init__(self, obj, condition, secondturn = False, seconduser = None, cardvalue = None):
    super().__init__(timeout=60)
    self.obj = obj
    self.value = None
    self.cardvalue = cardvalue
    self.seconduser = seconduser
    self.secondturn = secondturn
    if condition == "di":
        button = discord.ui.Button(label="Double", style=discord.ButtonStyle.primary)
        self.add_item(button)
        button.callback = self.third
        button2 = discord.ui.Button(label="Insurance", style=discord.ButtonStyle.primary)
        self.add_item(button2)
        button2.callback = self.fourth
    elif condition == "d":
        button = discord.ui.Button(label="Double", style=discord.ButtonStyle.primary)
        self.add_item(button)
        button.callback = self.third
    elif condition == "i":
        button2 = discord.ui.Button(label="Insurance", style=discord.ButtonStyle.primary)
        self.add_item(button2)
        button2.callback = self.fourth
    button3 = discord.ui.Button(label="Run away", style=discord.ButtonStyle.red, row=1)
    self.add_item(button3)
    button3.callback = self.fifth

  @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
  async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
    try:
      if self.cardvalue > 21:
        await interaction.response.send_message("Your card value is over 21! You can't hit anymore!", ephemeral=True)
        return
      elif self.cardvalue == 21:
        await interaction.response.send_message("Your card value is already 21! You can't hit anymore!", ephemeral=True)
        return
    except:
      pass
    self.stop()
    self.value = "h"
    await interaction.response.defer()

  @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary)
  async def second(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "s"
    await interaction.response.defer()

  async def third(self, interaction: discord.Interaction):
    self.stop()
    self.value = "d"
    await interaction.response.defer()

  async def fourth(self, interaction: discord.Interaction):
    self.stop()
    self.value = "i"
    await interaction.response.defer()

  async def fifth(self, interaction: discord.Interaction):
    self.stop()
    self.value = "r"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if self.seconduser is None and interaction.user.id != 615037304616255491:
      if interaction.user != self.obj.author:
        await interaction.response.send_message("Its not for you!", ephemeral=True)
        return False
    else:
      if self.secondturn == False:
        if interaction.user == self.seconduser:
          await interaction.response.send_message("Its not your turn yet!", ephemeral=True)
          return False
        elif not interaction.user == self.obj.author:
          await interaction.response.send_message("Its not for you!", ephemeral=True)
          return False
      if self.secondturn == True:
        if interaction.user == self.seconduser:
          await interaction.response.send_message("Your turn is over!", ephemeral=True)
          return False
        elif not interaction.user == self.obj.author:
          await interaction.response.send_message("Its not for you!", ephemeral=True)
          return False
    return True

class Highlow(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.button(label="High", style=discord.ButtonStyle.primary)
  async def high(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "high"
    await interaction.response.defer()

  @discord.ui.button(label="Low", style=discord.ButtonStyle.primary)
  async def low(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "low"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Highlow2(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
  async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "next"
    await interaction.response.defer()

  @discord.ui.button(label="Cash out", style=discord.ButtonStyle.primary)
  async def cash(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "cash"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Leaderboard_select(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
  async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  @discord.ui.button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
  async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  @discord.ui.select(placeholder='Leaderboard category', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Server Wealth', description='Shows the richest user in this server', emoji='\U0001f4b5', value="wealth"),
    discord.SelectOption(label='Server Level', description='Shows the most experienced user in this server', emoji='\U000023eb', value="level"),
    discord.SelectOption(label='Global Wealth', description='Shows the globally richest user', emoji='\U0001f4b5', value="gwealth"),
    discord.SelectOption(label='Global Level', description='Shows the globally most experienced user', emoji='\U000023eb', value="glevel")
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Profile_select(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.select(placeholder='Other information', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Character', emoji='<:character:905639779050352670>', value="character"),
    discord.SelectOption(label='Location', emoji='<:pointer:905681276751716402>', value="location"),
    discord.SelectOption(label='Level', emoji='\U000023eb', value="level"),
    discord.SelectOption(label='Balance', emoji='\U0001f4b5', value="balance"),
    discord.SelectOption(label='Car', emoji='\U0001f697', value="car"),
    discord.SelectOption(label='Statistics', emoji='\U0001f4aa', value="stats"),
    discord.SelectOption(label='Timers', emoji='\U000023f0', value="timers"),
    discord.SelectOption(label='Status', emoji='\U0001f4ad', value="status"),
    discord.SelectOption(label='Others', emoji='\U00002699', value="others"),
    discord.SelectOption(label='Overall', emoji='\U0001f4a0', value="overall"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Travel(discord.ui.View):
  def __init__(self, ctx, user, userlocation, location, price, usercash):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.locvalue = None
    self.user = user
    self.userlocation = userlocation
    self.location = location
    self.price = price
    self.usercash = usercash

    if self.location == self.userlocation:
      button1 = discord.ui.Button(emoji="\U00002708", label="You are already here", style=discord.ButtonStyle.green, disabled=True)
    elif self.usercash < self.price:
      button1 = discord.ui.Button(emoji="\U00002708", label="You don't have enough cash", style=discord.ButtonStyle.green, disabled=True)
    else:
      button1 = discord.ui.Button(emoji="<:cash:1329017495536930886>", label=f"{self.price}", style=discord.ButtonStyle.green)
    self.add_item(button1)
    button1.callback = self.travel

  async def travel(self, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "travel"
    await interaction.response.edit_message(view=self)

  @discord.ui.select(placeholder='Choose a location', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Corsia', value="corsia"),
    discord.SelectOption(label='Lucoro', value="lucoro"),
    discord.SelectOption(label='Donvia', value="donvia"),
    discord.SelectOption(label='Arkovich', value="arkovich"),
    discord.SelectOption(label='Zelmor', value="zelmor"),
  ])
  async def travel_callback(self, select, interaction):
    self.stop()
    self.locvalue = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Bust(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
  async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  @discord.ui.button(label="Bust", emoji="\U0001f4a5", style=discord.ButtonStyle.green)
  async def bust(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "bust"
    await interaction.response.edit_message(view=self)
  
  @discord.ui.button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
  async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Page(discord.ui.View):
  def __init__(self, ctx, user, left = False, right = False, timeout=None):
    if timeout is None:
      timeout = 300
    super().__init__(timeout=timeout)
    self.ctx = ctx
    self.value = None
    self.user = user
    leftbutton = discord.ui.Button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
    if left:
      leftbutton.disabled = True
    self.add_item(leftbutton)
    leftbutton.callback = self.left
    rightbutton = discord.ui.Button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
    if right:
      rightbutton.disabled = True
    self.add_item(rightbutton)
    rightbutton.callback = self.right

  async def left(self, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  async def right(self, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Rep1(discord.ui.View):
  def __init__(self, ctx, user, disabled = False, anonymous = False):
    super().__init__(timeout=10)
    self.ctx = ctx
    self.value = None
    self.user = user
    self.disabled = disabled
    if anonymous:
      upbutton = discord.ui.Button(label="++Anonymous Respect", style=discord.ButtonStyle.green)
    else:
      upbutton = discord.ui.Button(label="++Respect", style=discord.ButtonStyle.green)
    self.add_item(upbutton)
    upbutton.callback = self.up
    if anonymous:
      downbutton = discord.ui.Button(label="--Anonymous Disrespect", style=discord.ButtonStyle.red)
    else:
      downbutton = discord.ui.Button(label="--Disrespect", style=discord.ButtonStyle.red)
    self.add_item(downbutton)
    downbutton.callback = self.down
    delbutton = discord.ui.Button(label="Delete this message", style=discord.ButtonStyle.red, row=1)
    self.add_item(delbutton)
    delbutton.callback = self.delete

    if disabled:
      upbutton.disabled = True
      downbutton.disabled = True

  async def up(self, interaction: discord.Interaction):
    self.stop()
    self.value = "up"
    await interaction.response.defer()

  async def down(self, interaction: discord.Interaction):
    self.stop()
    self.value = "down"
    await interaction.response.defer()

  async def delete(self, interaction: discord.Interaction):
    self.value = None
    self.stop()
    await interaction.message.delete()
    return

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Rep(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=20)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.select(placeholder='Respect mode', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Normal', description='Send respect points showing your identity', value="ua"),
    discord.SelectOption(label='Anonymous', description='Send respect points anonymously', value="a"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Next(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
  async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = True
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Story(discord.ui.View):
  def __init__(self, ctx, label1, label2 = None, timeout = 60):
    super().__init__(timeout=timeout)
    self.ctx = ctx
    self.value = None
    truebutton = discord.ui.Button(label=label1, style=discord.ButtonStyle.primary)
    self.add_item(truebutton)
    truebutton.callback = self.yes

    if label2 is not None:
      falsebutton = discord.ui.Button(label=label2, style=discord.ButtonStyle.primary)
      self.add_item(falsebutton)
      falsebutton.callback = self.no

  async def yes(self, interaction: discord.Interaction):
    self.stop()
    self.value = True
    await interaction.response.defer()

  async def no(self, interaction: discord.Interaction):
    self.stop()
    self.value = False
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Shop(discord.ui.View):
  def __init__(self, ctx, user, left = False, right = False, timeout=None):
    if timeout is None:
      timeout = 30
    super().__init__(timeout=timeout)
    self.ctx = ctx
    self.value = None
    self.user = user
    leftbutton = discord.ui.Button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
    if left:
      leftbutton.disabled = True
    self.add_item(leftbutton)
    leftbutton.callback = self.left
    rightbutton = discord.ui.Button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
    if right:
      rightbutton.disabled = True
    self.add_item(rightbutton)
    rightbutton.callback = self.right

  async def left(self, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  async def right(self, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  @discord.ui.select(placeholder='Category', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Normal Items', value="normal"),
    discord.SelectOption(label='Melee Weapons', value="melee"),
    discord.SelectOption(label='Ranged Weapons', value="ranged"),
    discord.SelectOption(label='Insurance', value="insurance"),
    discord.SelectOption(label='Token Shop', value="token"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Insurance(discord.ui.View):
  def __init__(self, ctx, user, cost, usercash):
    super().__init__(timeout=20)
    self.ctx = ctx
    self.value = None
    self.user = user
    if cost != 100:
      label = f"Upgrade Insurance {cost}"
    else:
      label = f"Buy Insurance {cost}"
    button = discord.ui.Button(emoji="<:cash:1329017495536930886>", label=label, style=discord.ButtonStyle.primary)
    if cost == 0:
      button.label = "Insurance maxed"
      button.disabled = True
    elif usercash < cost:
      button.label = label + " (Not enough cash)"
      button.disabled = True
    self.add_item(button)
    button.callback = self.buy

  async def buy(self, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "buy"
    await interaction.response.defer()
    await self.message.edit(view=self)

  @discord.ui.select(placeholder='Category', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Normal Items', value="normal"),
    discord.SelectOption(label='Melee Weapons', value="melee"),
    discord.SelectOption(label='Ranged Weapons', value="ranged"),
    discord.SelectOption(label='Insurance', value="insurance"),
    discord.SelectOption(label='Token Shop', value="token"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Statistics_select(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=30)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.select(placeholder='Statistics', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Fighting statistics', value="fighting"),
    discord.SelectOption(label='Driving statistics', value="driving"),
    discord.SelectOption(label='Other statistics', value="other"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Train(discord.ui.View):
  def __init__(self, ctx, user):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None
    self.user = user

  @discord.ui.button(label="Strength", emoji="<:dumbbell:905773708369612811>", style=discord.ButtonStyle.primary)
  async def strength(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "str"
    await interaction.response.defer()
    await self.message.edit(view=self)

  @discord.ui.button(label="Defense", emoji="<:shield:905782766673743922>", style=discord.ButtonStyle.primary)
  async def defense(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "def"
    await interaction.response.defer()
    await self.message.edit(view=self)

  @discord.ui.button(label="Speed", emoji="<:speed:905800074955739147>", style=discord.ButtonStyle.primary)
  async def speed(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "spd"
    await interaction.response.defer()
    await self.message.edit(view=self)

  @discord.ui.button(label="Dexterity", emoji="<:dodge1:905801069857218622>", style=discord.ButtonStyle.primary)
  async def dexterity(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = "dex"
    await interaction.response.defer()
    await self.message.edit(view=self)

  @discord.ui.select(placeholder='Statistics', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Fighting statistics', value="fighting"),
    discord.SelectOption(label='Driving statistics', value="driving"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Train2(discord.ui.View):
  def __init__(self, ctx, user, userdata, acc = False, dri = False, han = False, bra = False):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None
    self.user = user

    accbutton = discord.ui.Button(label=f"Accelerating: {round((userdata['stats']['acc']//100*50)+100)}", emoji="<:accelerating:942699703835979797>", style=discord.ButtonStyle.primary)
    if acc:
      accbutton.disabled = True
      accbutton.label = "Accelerating (Maxed)"
    self.add_item(accbutton)
    accbutton.callback = self.accelerating

    dributton = discord.ui.Button(label=f"Drifting: {round((userdata['stats']['dri']//100*50)+100)}", emoji="<:drifting:942700424820047903>", style=discord.ButtonStyle.primary)
    if dri:
      dributton.disabled = True
      dributton.label = "Drifting (Maxed)"
    self.add_item(dributton)
    dributton.callback = self.drifting

    hanbutton = discord.ui.Button(label=f"Handling: {round((userdata['stats']['han']//100*50)+100)}", emoji="<:handling:942699703789830164>", style=discord.ButtonStyle.primary)
    if han:
      hanbutton.disabled = True
      hanbutton.label = "Handling (Maxed)"
    self.add_item(hanbutton)
    hanbutton.callback = self.handling

    brabutton = discord.ui.Button(label="Braking: 100", emoji="<:braking:942699703492030475>", style=discord.ButtonStyle.primary)
    if bra:
      brabutton.disabled = True
      brabutton.label = "Brake (Maxed)"
    self.add_item(brabutton)
    brabutton.callback = self.braking

  async def accelerating(self, interaction: discord.Interaction):
    self.stop()
    self.value = "acc"
    await interaction.response.defer()

  async def drifting(self, interaction: discord.Interaction):
    self.stop()
    self.value = "dri"
    await interaction.response.defer()

  async def handling(self, interaction: discord.Interaction):
    self.stop()
    self.value = "han"
    await interaction.response.defer()

  async def braking(self, interaction: discord.Interaction):
    self.stop()
    self.value = "bra"
    await interaction.response.defer()

  @discord.ui.select(placeholder='Statistics', min_values=1, max_values=1, options=[
    discord.SelectOption(label='Fighting statistics', value="fighting"),
    discord.SelectOption(label='Driving statistics', value="driving"),
  ])
  async def select_callback(self, select, interaction):
    self.stop()
    self.value = select.values[0]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Learn(discord.ui.Modal):
    def __init__(self, label) -> None:
        super().__init__(title="Answer the question")
        self.add_item(discord.ui.InputText(label=label, placeholder="Enter your answer here"))
        self.value = None
        self.interaction = None

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        self.value = self.children[0].value
        self.interaction = interaction
        await interaction.response.defer()

class ttt(discord.ui.View):
  def __init__(self, ctx, user, matrix, turn):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None
    self.user = user

    if not turn:
      emoji = "\U00002b55"
    else:
      emoji = "\U0000274c"

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary)
    if matrix[0][0]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place00

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary)
    if matrix[0][1]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place01

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary)
    if matrix[0][2]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place02

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=1)
    if matrix[1][0]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place10

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=1)
    if matrix[1][1]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place11

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=1)
    if matrix[1][2]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place12

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=2)
    if matrix[2][0]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place20

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=2)
    if matrix[2][1]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place21

    placebutton = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.primary, row=2)
    if matrix[2][2]:
      placebutton.disabled = True
    self.add_item(placebutton)
    placebutton.callback = self.place22

  async def place00(self, interaction: discord.Interaction):
    self.stop()
    self.value = [0, 0]
    await interaction.response.defer()

  async def place01(self, interaction: discord.Interaction):
    self.stop()
    self.value = [0, 1]
    await interaction.response.defer()

  async def place02(self, interaction: discord.Interaction):
    self.stop()
    self.value = [0, 2]
    await interaction.response.defer()

  async def place10(self, interaction: discord.Interaction):
    self.stop()
    self.value = [1, 0]
    await interaction.response.defer()

  async def place11(self, interaction: discord.Interaction):
    self.stop()
    self.value = [1, 1]
    await interaction.response.defer()

  async def place12(self, interaction: discord.Interaction):
    self.stop()
    self.value = [1, 2]
    await interaction.response.defer()

  async def place20(self, interaction: discord.Interaction):
    self.stop()
    self.value = [2, 0]
    await interaction.response.defer()

  async def place21(self, interaction: discord.Interaction):
    self.stop()
    self.value = [2, 1]
    await interaction.response.defer()

  async def place22(self, interaction: discord.Interaction):
    self.stop()
    self.value = [2, 2]
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Jail(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=300)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="Bribe the guards", style=discord.ButtonStyle.primary)
  async def bribe(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = True
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Fraud(discord.ui.View):
  def __init__(self, ctx, userfraud):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

    planbutton = discord.ui.Button(label="Plan more", style=discord.ButtonStyle.primary)
    if userfraud >= 100:
      planbutton.disabled = True
      planbutton.label = "Fully planned"
    self.add_item(planbutton)
    planbutton.callback = self.plan

    commitbutton = discord.ui.Button(label="Commit fraud", style=discord.ButtonStyle.primary)
    if userfraud <= 0:
      commitbutton.disabled = True
      commitbutton.label = "Nothing planned"
    self.add_item(commitbutton)
    commitbutton.callback = self.commit

  async def plan(self, interaction: discord.Interaction):
    self.stop()
    self.value = True
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def commit(self, interaction: discord.Interaction):
    self.stop()
    self.value = False
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Teacher(discord.ui.View):
  def __init__(self, ctx, words):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

    for word in words:
      b = discord.ui.Button(label=word, style=discord.ButtonStyle.primary, custom_id=word)
      self.add_item(b)
      b.callback = self.button

  async def button(self, interaction: discord.Interaction):
    self.stop()
    self.value = interaction.custom_id
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Gamer(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

    b1 = discord.ui.Button(label="ㅤ", style=discord.ButtonStyle.secondary)
    self.add_item(b1)
    b1.callback = self.empty
    b2 = discord.ui.Button(emoji="\U0001f53c", style=discord.ButtonStyle.primary)
    self.add_item(b2)
    b2.callback = self.up
    b3 = discord.ui.Button(label="ㅤ", style=discord.ButtonStyle.secondary)
    self.add_item(b3)
    b3.callback = self.empty
    b4 = discord.ui.Button(emoji="\U000025c0", style=discord.ButtonStyle.primary, row=1)
    self.add_item(b4)
    b4.callback = self.left
    b5 = discord.ui.Button(label="ㅤ", style=discord.ButtonStyle.secondary, row=1)
    self.add_item(b5)
    b5.callback = self.empty
    b6 = discord.ui.Button(emoji="\U000025b6", style=discord.ButtonStyle.primary, row=1)
    self.add_item(b6)
    b6.callback = self.right
    b7 = discord.ui.Button(label="ㅤ", style=discord.ButtonStyle.secondary, row=2)
    self.add_item(b7)
    b7.callback = self.empty
    b8 = discord.ui.Button(emoji="\U0001f53d", style=discord.ButtonStyle.primary, row=2)
    self.add_item(b8)
    b8.callback = self.down
    b9 = discord.ui.Button(label="ㅤ", style=discord.ButtonStyle.secondary, row=2)
    self.add_item(b9)
    b9.callback = self.empty

  async def up(self, interaction: discord.Interaction):
    self.stop()
    self.value = "up"
    await interaction.response.defer()

  async def left(self, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  async def right(self, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  async def down(self, interaction: discord.Interaction):
    self.stop()
    self.value = "down"
    await interaction.response.defer()

  async def empty(self, interaction: discord.Interaction):
    self.stop()
    self.value = "empty"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Artist(discord.ui.View):
  def __init__(self, ctx, shape, colour, mode):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

    squares = {
      "red": "\U0001f7e5",
      "green": "\U0001f7e9",
      "blue": "\U0001f7e6",
      "yellow": "\U0001f7e8",
      "purple": "\U0001f7ea",
      "brown": "\U0001f7eb",
      "orange": "\U0001f7e7",
      "black": "\U00002b1b",
      "white": "\U00002b1c",
    }

    circles = {
      "red": "\U0001f534",
      "green": "\U0001f7e2",
      "blue": "\U0001f535",
      "yellow": "\U0001f7e1",
      "purple": "\U0001f7e3",
      "brown": "\U0001f7e4",
      "orange": "\U0001f7e0",
      "black": "\U0001f534",
      "white": "\U000026aa",
    }

    triangles_up = {
      "red": "\U0001f53a",
      "green": "\U0001f53a",
      "blue": "\U0001f53a",
      "yellow": "\U0001f53a",
      "purple": "\U0001f53a",
      "brown": "\U0001f53a",
      "orange": "\U0001f53a",
      "black": "\U0001f53a",
      "white": "\U0001f53a",
    }

    triangles_down = {
      "red": "\U0001f53b",
      "green": "\U0001f53b",
      "blue": "\U0001f53b",
      "yellow": "\U0001f53b",
      "purple": "\U0001f53b",
      "brown": "\U0001f53b",
      "orange": "\U0001f53b",
      "black": "\U0001f53b",
      "white": "\U0001f53b",
    }

    diamonds = {
      "red": "\U0001f537",
      "green": "\U0001f537",
      "blue": "\U0001f537",
      "yellow": "\U0001f537",
      "purple": "\U0001f537",
      "brown": "\U0001f537",
      "orange": "\U0001f536",
      "black": "\U0001f537",
      "white": "\U0001f537",
    }

    shapes = {
      "square": squares,
      "circle": circles,
      "triangle up": triangles_up,
      "triangle down": triangles_down,
      "diamond": diamonds,
    }

    shapes2 = {
      "square": "\U0001f7e5",
      "circle": "\U0001f534",
      "triangle up": "\U0001f53a",
      "triangle down": "\U0001f53b",
      "diamond": "\U0001f537",
    }

    # print(shapes[shape][colour].replace("\\", "."))
    for i in range(9):
      b = discord.ui.Button(emoji=shapes[shape][colour], style=discord.ButtonStyle.primary, custom_id=str(i), row=i // 3)
      self.add_item(b)
      b.callback = self.draw
      if i == 2:
        b = discord.ui.Button(label=f"{shapes2[shape]}", emoji="\U0001f501", style=discord.ButtonStyle.success)
        self.add_item(b)
        b.callback = self.change_shape
      elif i == 5:
        b = discord.ui.Button(label=f"{squares[colour]}", emoji="\U0001f501", style=discord.ButtonStyle.success, row=1)
        self.add_item(b)
        b.callback = self.change_colour
      elif i == 8:
        b = discord.ui.Button(emoji="\U0001f58c" if mode else "\U0001f6ab", style=discord.ButtonStyle.success, row=2)
        self.add_item(b)
        b.callback = self.change_mode

  async def draw(self, interaction: discord.Interaction):
    self.stop()
    self.value = int(interaction.custom_id)
    await interaction.response.defer()

  async def change_shape(self, interaction: discord.Interaction):
    self.stop()
    self.value = "shape"
    await interaction.response.defer()

  async def change_colour(self, interaction: discord.Interaction):
    self.stop()
    self.value = "colour"
    await interaction.response.defer()

  async def change_mode(self, interaction: discord.Interaction):
    self.stop()
    self.value = "mode"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Doctor(discord.ui.View):
  def __init__(self, ctx, tools, disabled):
    super().__init__(timeout=120)
    self.ctx = ctx
    self.value = None

    for tool in tools:
      b = discord.ui.Button(label=tool, style=discord.ButtonStyle.primary, custom_id=tool)
      if tool in disabled:
        b.disabled = True
      self.add_item(b)
      b.callback = self.button

  async def button(self, interaction: discord.Interaction):
    self.stop()
    self.value = interaction.custom_id
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Lawyer(discord.ui.View):
  def __init__(self, ctx, evidences, disabled):
    super().__init__(timeout=120)
    self.ctx = ctx
    self.value = None

    for evidence in evidences:
      b = discord.ui.Button(label=evidence, style=discord.ButtonStyle.primary, custom_id=evidence, row=evidences.index(evidence) // 3)
      if evidence in disabled:
        b.disabled = True
      self.add_item(b)
      b.callback = self.button

  async def button(self, interaction: discord.Interaction):
    self.stop()
    self.value = interaction.custom_id
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Lawyer2(discord.ui.View):
  def __init__(self, ctx, objections):
    super().__init__(timeout=120)
    self.ctx = ctx
    self.value = None

    for objection in objections:
      b = discord.ui.Button(label=objection, style=discord.ButtonStyle.primary, custom_id=objection, row=objections.index(objection) // 3)
      self.add_item(b)
      b.callback = self.button

  async def button(self, interaction: discord.Interaction):
    self.stop()
    self.value = interaction.custom_id
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Event(discord.ui.View):
  def __init__(self, ctx, label):
    super().__init__(timeout=20)
    self.ctx = ctx
    self.value = []

    b = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
    self.add_item(b)
    b.callback = self.event

  async def event(self, interaction: discord.Interaction):
    self.value.append(interaction.user.id)
    self.stop()
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.message.edit(view=self)

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = []
    await self.message.edit(view=self)

class Estate(discord.ui.View):
  def __init__(self, ctx, user, left = False, right = False, ll = False, rr = False, price = None, usercash = None):
    super().__init__(timeout=300)
    self.ctx = ctx
    self.value = None
    self.user = user

    llbutton = discord.ui.Button(emoji="\U000023EA", style=discord.ButtonStyle.primary)
    if ll:
      llbutton.disabled = True
    self.add_item(llbutton)
    llbutton.callback = self.ll

    leftbutton = discord.ui.Button(emoji="\U000025c0", style=discord.ButtonStyle.primary)
    if left:
      leftbutton.disabled = True
    self.add_item(leftbutton)
    leftbutton.callback = self.left

    buybutton = discord.ui.Button(emoji="<:cash:1329017495536930886>", label=f"{functions.aa(price)}", style=discord.ButtonStyle.primary)
    if usercash < price:
      buybutton.disabled = True
      buybutton.label = f"{functions.aa(price)} (Not enough cash)"
    self.add_item(buybutton)
    buybutton.callback = self.buy

    rightbutton = discord.ui.Button(emoji="\U000025b6", style=discord.ButtonStyle.primary)
    if right:
      rightbutton.disabled = True
    self.add_item(rightbutton)
    rightbutton.callback = self.right

    rrbutton = discord.ui.Button(emoji="\U000023E9", style=discord.ButtonStyle.primary)
    if rr:
      rrbutton.disabled = True
    self.add_item(rrbutton)
    rrbutton.callback = self.rr

  async def buy(self, interaction: discord.Interaction):
    self.stop()
    self.value = "buy"
    for child in self.children:
      child.disabled = True
    await self.message.edit(view=self)

  async def left(self, interaction: discord.Interaction):
    self.stop()
    self.value = "left"
    await interaction.response.defer()

  async def right(self, interaction: discord.Interaction):
    self.stop()
    self.value = "right"
    await interaction.response.defer()

  async def ll(self, interaction: discord.Interaction):
    self.stop()
    self.value = "ll"
    await interaction.response.defer()

  async def rr(self, interaction: discord.Interaction):
    self.stop()
    self.value = "rr"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.user and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True

class Lockpicking(discord.ui.View):
  def __init__(self, ctx):
    super().__init__(timeout=60)
    self.ctx = ctx
    self.value = None

  @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
  async def one(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 1
    await interaction.response.defer()

  @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
  async def two(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 2
    await interaction.response.defer()

  @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
  async def three(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 3
    await interaction.response.defer()

  @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
  async def four(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = 4
    await interaction.response.defer()

  @discord.ui.button(label="How to pick a lock", style=discord.ButtonStyle.primary, row=1)
  async def instruction(self, button: discord.ui.Button, interaction: discord.Interaction):
    self.stop()
    self.value = "instruction"
    await interaction.response.defer()

  async def on_timeout(self):
    self.stop()
    for child in self.children:
      child.disabled = True
    self.value = None
    await self.message.edit(view=self)

  async def interaction_check(self, interaction):
    if interaction.user != self.ctx.author and interaction.user.id != 615037304616255491:
      await interaction.response.send_message("Its not for you!", ephemeral=True)
      return False
    return True
