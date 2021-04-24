import discord
from discord.ext import commands
import asyncio
import os

class Embed(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    async def get_title_content():
        def check_author(m):
            return m.author == ctx.message.author

        async def clear_all():
            for i in msg_sent:
                await i.delete(delay=1.)
            return

        msg_sent = [ctx.message]
        
        msg1 = await ctx.send('¿Que titulo queres para el embed?')
        msg_sent.append(msg1)

        try:
            title_embed_msg = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(title_embed_msg)
            title_embed = title_embed_msg.content
        except asyncio.TimeoutError:
            return await clear_all()
        except Exception as error:
            await clear_all()
            raise error
            return
        
        msg2 = await ctx.send('¿Que contenido queres para el embed?')
        msg_sent.append(msg2)

        try:
            content_embed_msg = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(content_embed_msg)
            content_embed = content_embed_msg.content
        except asyncio.TimeoutError:
            return await clear_all()
        except Exception as error:
            await clear_all()
            raise error
            return
        return title_embed, content_embed
    
    @commands.command()
    async def embed(self, ctx):

        title_embed, content_embed = await self.client.get_title_content()
        
        embed=discord.Embed(title=title_embed, description=content_embed)
        await ctx.send(embed=embed)
        await clear_all()

        return
    
    @commands.command()
    async def edit(self, ctx, url):
        url = url.split('/')
        server_id = int(link[4])
        channel_id = int(link[6])
        msg_id = int(link[5])
        server = client.get_guild(server_id)
        channel = server.get_channel(channel_id)
        message = await channel.fetch_message(msg_id)

        title_embed, content_embed = await self.client.get_title_content()
        embed=discord.Embed(title=title_embed, description=content_embed)

        await message.edit(embed=embed)

        return

def setup(client):
    client.add_cog(Embed(client))