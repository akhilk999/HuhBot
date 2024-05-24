import os
import re

import discord
from discord.ext import commands
from discord.utils import find

from keep_alive import keep_alive

token = os.environ['TOKEN']

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.typing = False
intents.presences = False
intents.reactions = True

huh_re = r"(?i)( |^)huh( |$)"

count = 0

#client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='^',
                      help_command=commands.MinimalHelpCommand(),
                      activity=discord.Game(name="^help"),
                      intents=intents)


#overrides page formatting for MinimalHelpCommand -> puts each page in an embed
class MyNewHelp(commands.MinimalHelpCommand):
  async def send_pages(self):
    destination = self.get_destination()
    for page in self.paginator.pages:
      emby = discord.Embed(description=page)
      await destination.send(embed=emby)

client.help_command = MyNewHelp()

class MyHelp(commands.HelpCommand):
  def get_command_signature(self, command):
    return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

  #overall help command
  async def send_bot_help(self, mapping):
    embed = discord.Embed(title="Help", color=discord.Color.blurple())
    for cog, commands in mapping.items():
      filtered = await self.filter_commands(commands, sort=True)
      command_signatures = [self.get_command_signature(c) for c in filtered]
      if command_signatures:
        cog_name = getattr(cog, "qualified_name", "No Category")
        embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
    channel = self.get_destination()
    await channel.send(embed=embed)

  #help for a certain command
  async def send_command_help(self, command):
    embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.random())
    if command.help:
      embed.description = command.help
    if alias := command.aliases:
      embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

    channel = self.get_destination()
    await channel.send(embed=embed)

  #helper function to add commands to embed
  async def send_help_embed(self, title, description, commands):
    embed = discord.Embed(title=title, description=description or "No help found...")
    if filtered_commands := await self.filter_commands(commands):
      for command in filtered_commands:
        embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
    await self.get_destination().send(embed=embed)

  async def send_group_help(self, group):
    title = self.get_command_signature(group)
    await self.send_help_embed(title, group.help, group.commands)

  async def send_cog_help(self, cog):
    title = cog.qualified_name or "No"
    await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


#bot joins server
@client.event
async def on_guild_join(guild):
  general = find(lambda x: x.name == 'general', guild.text_channels)
  if general and general.permissions_for(guild.me).send_messages:
    await general.send('Hello {}!'.format(guild.name))





#when a message is sent
@client.event
async def on_message(message):
  global count
  #returns nothing if message is from bot
  if message.author == client.user:
    return

  #message contains huh -> adds to counter
  if re.search(huh_re, message.content) and message.author.id == 302148042461675530:
    count += 1
    await message.channel.send('Added 1 huh, Total is now: ' + str(count))

  if message.content.startswith('real'):
    await message.channel.send('real')

  # process commands
  await client.process_commands(message)


#client.remove_command('help')

#commands
@client.command()
async def huh(ctx):
  embed = discord.Embed(description="Total number of huh's: " + str(count))
  await ctx.send(embed=embed)


#keep_alive()
client.run(token)
