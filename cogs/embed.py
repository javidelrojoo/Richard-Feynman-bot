import discord
from discord.ext import commands
import asyncio
import os

class Embed(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    async def get_title_content(self, ctx):
        def check_author(m):
            return m.author == ctx.message.author

        async def clear_all():
            for i in msg_sent:
                await i.delete(delay=1.)
            return

        msg_sent = [ctx.message]
        
        msg1 = await ctx.send('What title you want for the embed?')
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
        
        msg2 = await ctx.send('What content you want for the embed?')
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
        await clear_all()
        return title_embed, content_embed
    
    @commands.command(brief="Creates a embed", help="With this command I\'ll create a embed, the aim it\'s to make it easy and fast to use, that's why is simple.")
    async def embed(self, ctx):

        title_embed, content_embed = await self.get_title_content(ctx)
        
        embed=discord.Embed(title=title_embed, description=content_embed)
        await ctx.send(embed=embed)

        return
    
    @commands.command(brief="Edits a embed", help="Edits a embed that was created with the embed command, for now it only works with the message link.")
    async def edit(self, ctx, url):
        url = url.split('/')
        server_id = int(url[4])
        channel_id = int(url[5])
        msg_id = int(url[6])
        server = self.client.get_guild(server_id)
        channel = server.get_channel(channel_id)
        message = await channel.fetch_message(msg_id)

        title_embed, content_embed = await self.get_title_content(ctx)
        embed=discord.Embed(title=title_embed, description=content_embed)

        await message.edit(embed=embed)

        return

def setup(client):
    client.add_cog(Embed(client))