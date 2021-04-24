import discord
from discord.ext import commands
import asyncio
import os

class Others(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(brief='Shows you my ping', help="Using this command i'll tell you my latency")
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000, 2)} ms')
    
    @commands.command(brief='A link so you can invite to other servers')
    async def invite(self, ctx):
        await ctx.send('https://discord.com/oauth2/authorize?client_id=767504106633035796&scope=bot&permissions=8')

def setup(client):
    client.add_cog(Others(client))