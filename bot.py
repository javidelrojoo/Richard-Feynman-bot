import discord
from discord.ext import commands, tasks
import asyncio
import os

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='rf!', intents=intents)

cogs = ['reaction', 'embed', 'others']

if __name__ == '__main__':
    for f in cogs:
        client.load_extension(f'cogs.{f}')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="rf!help"))
    print('Loggeado como:')
    print(client.user.name)
    print(client.user.id)
    print('------')


token = os.getenv('TOKEN')

client.run(token)
