import discord
from discord.ext import commands
import asyncio
import os

class Others(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(brief='Shows you my ping :eyes:', help='Usando este comando podes averiguar el ping del bot.')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000, 2)} ms')

def setup(client):
    client.add_cog(Others(client))