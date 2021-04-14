import discord
from discord.ext import commands, tasks
import asyncio
import os

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='rf!', intents=intents)

cogs = ['reaction']

if __name__ == '__main__':
    for f in cogs:
        client.load_extension(f'cogs.{f}')


@client.event
async def on_ready():
    print('Loggeado como:')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def reload(ctx):
    for file in cogs:
        client.unload_extension(f'cogs.{file}')
        client.load_extension(f'cogs.{file}')
    await ctx.send('Se recargaron los cogs')


@client.command()
async def load(ctx):
    for file in cogs:
        client.load_extension(f'cogs.{file}')
    await ctx.send('Se cargaron los cogs')


@client.command()
async def unload(ctx):
    for file in cogs:
        client.unload_extension(f'cogs.{file}')
    await ctx.send('Se descargaron los cogs')

token = os.getenv('TOKEN')

client.run(token)
