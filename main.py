import discord, os, asyncio, colorama,json, traceback, re, random
from discord.ext import commands
from discord import app_commands
from colorama import Fore
from discord.ui import View, Button

colorama.init(autoreset=True)
client = commands.Bot(
  command_prefix = commands.when_mentioned,
  intents = discord.Intents.all(),
  activity = discord.Game(
    name = "what a welcomer... - /help"
  ),
  status = discord.Status.idle
)

class ChangeViewModal(discord.ui.Modal, title='Change Welcome Configuration'):
    delay = discord.ui.TextInput(
        label='Delay:',
        placeholder='Amount of time to wait before sending a welcome DM',
        required = True,
    )  
    message = discord.ui.TextInput(
        label='Message To Send:',
        style=discord.TextStyle.short,
        placeholder='Do not use emojis in the :emoji: format, paste the real emoji instead.',
        required=True,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
     # await interaction.response.send_message(f'Your welcome configuration has successfully been changed jk no it hsnt, {self.delay.value}!',embed=embed, ephemeral=True)
      try:
        delay_int = float(self.delay.value)
        if delay_int > 20:
          await interaction.response.send_message("Your delay must be less than `20` seconds!")
        elif delay_int <= 20:
          with open(f"data/{interaction.guild.id}.txt", "w") as fek:
            fek.write(f"{self.message.value}:{delay_int}")
          ChangedViewModalVer = discord.Embed(
            title = "Success",
            description = f"T=he join configuration has successfully been updated.\n```yaml\nGuild ID: {interaction.guild.id}\nMessage: {self.message.value}\nDelay: {self.delay.value} seconds.\n```",
            color = 0x32CD32
          )
          await interaction.response.send_message(embed=ChangedViewModalVer)
      except ValueError as exclem:
        await interaction.response.send_message(f"Your delay must be an integer, not characters!", ephemeral = True)
        

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

class DataConfirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
      try:
        os.remove(f"data/{interaction.guild.id}.txt")
        await interaction.response.send_message('Your data has been removed and users will no longer receive a welcome message.')
      except Exception as exc:
        await interaction.response.send_message("You have not used our welcome feature yet, so we have nothing to delete!")
      self.value = True
      self.stop()

class ChangeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None
        
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label='Change Welcome Configuration', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(ChangeViewModal())
      self.value = True
      self.stop()

    @discord.ui.button(label='Remove Welcome Configuration', style=discord.ButtonStyle.red)
    async def eny(self, interaction: discord.Interaction, button: discord.ui.Button):
      try:
        os.remove(f"data/{interaction.guild.id}.txt")
        await interaction.response.send_message("Your welcome configuration has successfully been removed and users will no longer receive a DM when they join your server!")
      except:
        await interaction.response.send_message("Oops- seems like you haven't set a welcome configuration yet, so we have nothing to delete!", ephemeral=True)
      self.value = False
      self.stop()



@client.event
async def on_ready():
  await client.tree.sync()
  print(f"""{Fore.RED}
 ___________                                   .___
\_   _____/__  _______   ____  ___________  __| _/
 |    __)_\  \/  /  _ \_/ ___\/  _ \_  __ \/ __ | 
 |        \>    <  <_> )  \__(  <_> )  | \/ /_/ | 
/_______  /__/\_ \____/ \___  >____/|__|  \____ | 
        \/      \/          \/                 \/
                          Exo - The {Fore.RESET}{Fore.BLUE}Enhanced{Fore.RESET} {Fore.RED}Welcomer Project{Fore.RESET} ©️


          Bot ID: {client.user.id}
          Bot User: {client.user}
          Logged on: {Fore.LIGHTGREEN_EX}TRUE{Fore.RESET}
          Command Prefix: {client.command_prefix}
          Slash Synced: {Fore.LIGHTGREEN_EX}TRUE{Fore.RESET}
  """)

@client.tree.command(name = "serverinfo", description = "view the information of this current guild.")
async def serverinfo(interaction: discord.Interaction):
  guild = interaction.guild
  guild_name = guild.name
  guild_id = guild.id
  guild_owner = guild.owner_id 
  guild_server_pfp = guild.icon.url 
  guild_member_count = guild.member_count
  total_text_channels = len(guild.text_channels)
  total_voice_channels = len(guild.voice_channels)
  colors = random.randint(0, 0xffffff)
  server_info_embed = discord.Embed(
    title = f"{guild.name} | Server Information:",
    description = f"Guild Name: **{guild_name}**\nGuild ID: **{guild_id}**\nGuild Owner: <@{guild_owner}>\nMembercount: **{guild_member_count}**\nText channels: **{total_text_channels}**\nVoice channels: **{total_voice_channels}**",
    color = colors
  )
  server_info_embed.set_thumbnail(url=guild_server_pfp)
  await interaction.response.send_message(embed=server_info_embed)



@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.guild_only()
@client.tree.command(name = "setwelcome", description = "set a greet message to every new user who joins your guild!")
@app_commands.describe(
  message = "the message you want to send to new members!",
  delay = "amount of time to wait before the message is sent to the user in seconds!"
)
async def setwelcome(interaction: discord.Interaction, message: str, delay: int): # currently a slash command but set to modal inputs later on
  if delay > 20:
    errorWelcome = discord.Embed(
      description = "Error:\n```yaml\nYour delay cannot be longer than '20' secons to prevent confusion.\n```",
      color = 0xFF0000
    )
    await interaction.response.send_message(embed=errorWelcome, ephemeral = True, delete_after = 11)
  elif delay <= 20:
    filename = f"data/{interaction.guild.id}.txt"
    with open(filename, "w") as txtl:
      txtl.write(f"{message}:{delay}")
    successWelcome = discord.Embed(
      title = "Success",
      description = f"The join configuration has successfully been updated.\n```yaml\nGuild ID: {interaction.guild.id}\nMessage: {message}\nDelay: {delay} seconds\n```",
      color = 0x32CD32
    )
    view = ChangeView()
    await interaction.response.send_message(embed=successWelcome, view=view)
    view.message = await interaction.original_response()
  

@client.tree.error
async def on_app_command_error(interaction, error):
  if isinstance(error, app_commands.MissingPermissions):
    MissingPermissions = discord.Embed(
      description = f"Oops-\n```yam\n{error} 👀\n```",
      color = 0xFF0000
    )
    await interaction.response.send_message(embed=MissingPermissions, ephemeral = True, delete_after = 11)


@client.event
async def on_member_join(member):
  print(f"{member} joined from {member.guild.id} | {member.guild.name}")
  try:
    f = open(f"data/{member.guild.id}.txt", "r") 
    data = f.read()
    parts = data.strip().split(":")
    message = parts[0]
    delay = float(parts[1])
    try:
      kekkk = discord.ui.View()
      kekkk.add_item(discord.ui.Button(label = "Beware Of Scams", disabled=True))
      await asyncio.sleep(delay)
      print(f"Wait specified: {delay} seconds, sending dm now!")
      await member.send(content=f"> This message was sent from: **{member.guild.name}**\n\n{message}", view=kekkk)
      print(f"Sent message to: {member}")
    except Exception as exc:
      print(f"[{Fore.RED}ERROR{Fore.RESET}] An error occured {Fore.BLUE}::{Fore.RESET} {exc}")
  except Exception as e:
    print(f"[{Fore.RED}ERROR{Fore.RESET}] Can't send a DM maybe because no file created yet/no welcome enabled -> {e}")
    
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.guild_only()
@client.tree.command(name = "removewelcome", description = "remove the welcome feature on your server, this removes all message and delay data stored!")
async def removewelcome(interaction: discord.Interaction):
  dataremoval = discord.Embed(
    description = "```yaml\nPress the 'confirm' button below to validate you want to remove the welcome-feature and all data related to it\n```",
    color = 0x32CD32
  )
  view = DataConfirm()
  await interaction.response.send_message(embed=dataremoval, view=view)
  view.message = await interaction.original_response()

@app_commands.guild_only()
@commands.guild_only()
@client.tree.command(name = "help", description = "view the help command for this bot")
async def help(interaction: discord.Interaction):
  helpEmbed = discord.Embed(
    title = f"{client.user.name} | Welcomer Help:",
    description = f"Below are some of {client.user.name}'s commands:\nNote:\n> **[] = required arguments**\n> **() = optional arguments**\n\n> - `/setwelcome [message] [delay]` - set a welcome message for new users on dm when they join a server, with a specified message `[message]` and delay `[delay]`\n\n> - `/removewelcome` - remove **all** data stored for welcoming members. This will stop the bot from welcoming new users.\n\n> - `/help` - bring up the help command\n\n> - `/support` - get support on {client.user.name}",
    color = 0xFFC000
  )
  viewel = discord.ui.View()
  viewel.add_item(discord.ui.Button(label = "Get support", url = "https://discord.gg/vbZmAMJt7a", emoji = "🤖"))
  await interaction.response.send_message(embed=helpEmbed, view = viewel)

@client.tree.command(name = "support", description = "get support on our welcome bot")
async def support(interaction: discord.Interaction):
  await interaction.response.send_message("Get help by joining our support server and contacting a **staff** member!\n\n> :link: Support server - https://discord.gg/vbZmAMJt7a", ephemeral = True)

@app_commands.guild_only()
@client.tree.command(name = "ping", description = "uh- pong?")
async def ping(interaction: discord.Interaction):
  pingEmbed = discord.Embed(
    description = f"🏓 Pong! My latency is `{round(client.latency * 1000)}ms`.",
    color = 0x32CD32
  )
  await interaction.response.send_message(embed=pingEmbed)

@app_commands.guild_only()
@app_commands.checks.has_permissions(moderate_members=True)
@client.tree.command(name = "view", description = "view your welcome configuration, if you have any") # maybe modal bringup?
async def view(interaction: discord.Interaction):
  try:
    fi = open(f"data/{interaction.guild.id}.txt", "r")
    ki = fi.read()
    lm = ki.strip().split(":")
    viewEmbTrue = discord.Embed(
      title = f"{interaction.guild.name} | Welcome Configuration:",
      description = f"View your welcome configuration below:\n```yaml\nGuild ID: {interaction.guild.id}\nMessage: {lm[0]}\nDelay: {lm[1]}\n```\nChange your welcome configuration using the buttons below or use the `/setwelcome` command!\n\n> __**IMPORTANT NOTE:**__ You must __NOT__ use emojis in the `:emoji:` format when using the modal textbox, instead paste the real emoji like this 👋. If not done, your welcome feature won't work!",
      color = 0x32CD32
    )
    view=ChangeView()
    await interaction.response.send_message(embed=viewEmbTrue, view=view)
    view.message = await interaction.original_response()
  except Exception as ell:
    viewEmbFalse = discord.Embed(
      description = ":x: | You have not set a welcome configuration for your guild yet, use the buttons below or the `/setwelcome` command to set 1!\n\n> __**IMPORTANT NOTE:**__ You must __NOT__ use emojis in the `:emoji:` format when using the modal textbox, instead paste the real emoji like this 👋. If not done, your welcome feature won't work!",
      color = 0xFF0000
    )
    view=ChangeView()
    await interaction.response.send_message(embed=viewEmbFalse, view=view)
    view.message = await interaction.original_response()
"""
@app_commands.guild_only()
@app_commands.checks.has_permissions(moderate_members=True)
@client.tree.command(name="configuration", description = "Configure what can be allowed on the welcome message")
#async def configuration(interaction: discord.Interaction, antilink: bool):
  #if antilink == True:
    #with open(f"antilink/{guild.id}")
  elif antilink == False:
    print("false")
"""


if __name__ == '__main__':
  client.run("")
