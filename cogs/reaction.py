import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import os
import pymongo
from bson import ObjectId
import bson

mongo_url = os.getenv('MONGO_URL')
mongoclient = pymongo.MongoClient(mongo_url)
mongodb = mongoclient['Feynman']
mongoreactions = mongodb['Reactions']

class Reaction(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(brief='Agrega un reaction-role', help='Con este comando podés agregar un reaction-role siguiendo las instrucciones que el mismo bot te va a ir diciendo. Una falla común es que el bot esté por debajo del rol que quiere asignar, lo cual va a desencadenar en que el bot no pueda hacer su trabajo, para evitar eso asegurarse que el bot esté por encima de los roles que quiere agregar como reaction-role.')
    async def add(self, ctx):

        def check_author(m):
            return m.author == ctx.message.author

        def check_reaction(reaction, user):
            return reaction.message.id == msg3.id and user == ctx.author

        async def clear_all():
            for i in msg_sent:
                await i.delete()
            return

        msg_sent = [ctx.message]

        msg1 = await ctx.send("¿En que canal está el mensaje para reaccionar?")
        msg_sent.append(msg1)
        try:
            channel_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(channel_id)
            if not channel_id.channel_mentions:
                channel_id = int(channel_id.content)
                if self.client.get_channel(channel_id) is not None:
                    channel = self.client.get_channel(channel_id)
                else:
                    error_msg1a = await ctx.send('Tenés que pasarme un canal válido')
                    msg_sent.append(error_msg1a)
                    await asyncio.sleep(5.)
                    return await clear_all()
            else:
                channel = channel_id.channel_mentions[0]
                channel_id = channel.id
        except ValueError:
            error_msg1b = await ctx.send('Tenés que pasarme un canal válido')
            msg_sent.append(error_msg1b)
            await asyncio.sleep(5.)
            return await clear_all()
        except asyncio.TimeoutError:
            return await clear_all()

        msg2 = await ctx.send("¿En que mensaje? (Pasame el ID)")
        msg_sent.append(msg2)
        try:
            msg_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(msg_id)
            msg_id = int(msg_id.content)
            if await channel.fetch_message(msg_id) is None:
                error_msg2a = await ctx.send('Tenés que pasarme una ID válida')
                msg_sent.append(error_msg2a)
                await asyncio.sleep(5.)
                return await clear_all()
        except asyncio.TimeoutError:
            return await clear_all()
        except ValueError:
            error_msg2b = await ctx.send('Tenés que pasarme una ID válida')
            msg_sent.append(error_msg2b)
            await asyncio.sleep(5.)
            return await clear_all()

        msg3 = await ctx.send("Reaccioná a este mensaje con el emoji que quieras usar para dar el rol")
        msg_sent.append(msg3)
        try:
            emote, *_ = await self.client.wait_for("reaction_add", check=check_reaction, timeout=30.)
            reaction_name = str(emote.emoji.name)
            if emote.emoji.animated:
                reaction = '<a:'+reaction_name+':'+str(emote.emoji.id)+'>'

            else:
                reaction = '<:' + reaction_name + ':' + str(emote.emoji.id) + '>'
        except AttributeError:
            reaction = emote.emoji
            reaction_name = reaction
        except asyncio.TimeoutError:
            return await clear_all()

        msg4 = await ctx.send("¿Que rol queres dar?")
        msg_sent.append(msg4)
        try:
            role_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(role_id)
            if not role_id.role_mentions:
                role_id = int(role_id.content)
                if ctx.guild.get_role(role_id) is None:
                    error_msg4a = await ctx.send('Tenés que pasarme un rol válido')
                    msg_sent.append(error_msg4a)
                    await asyncio.sleep(5.)
                    return await clear_all()
            else:
                role = role_id.role_mentions[0]
                role_id = role.id
        except ValueError:
            error_msg4b = await ctx.send('Tenés que pasarme un rol válido')
            msg_sent.append(error_msg4b)
            await asyncio.sleep(5.)
            return await clear_all()
        except asyncio.TimeoutError:
            return await clear_all()
        
        guild_id = ctx.guild.id
        
        _id = mongoreactions.insert_one({'guild_id':guild_id ,'msg_id': msg_id, 'channel_id': channel_id, 'reaction_name': reaction_name, 'role_id': role_id})
        _id = _id.inserted_id
        msg = await channel.fetch_message(msg_id)
        await msg.add_reaction(reaction)

        embed = discord.Embed(title="Setup Listo")
        embed.add_field(name="ID de la reacción", value=str(_id), inline=False)
        embed.add_field(name="Canal", value="<#"+str(channel_id)+'>', inline=False)
        embed.add_field(name="Link del mensaje", value=f'[Hacé click acá]({msg.jump_url})', inline=False)
        embed.add_field(name="Emoji", value=reaction, inline=True)
        embed.add_field(name="Rol", value="<@&"+str(role_id)+'>', inline=True)
        await ctx.send(embed=embed)
        await clear_all()

    @commands.command(brief='Borra un reaction-role', help='Dando una ID como argumento, borra ese reaction-role. Podés buscar la ID en el mensaje luego de ser seteado o con el comando rf!list')
    async def delete(self, ctx, id):
        dlts = mongoreactions.delete_one({'_id': ObjectId(id)})
        if dlts.deleted_count != 1:
            await ctx.send('No se encontró ninguna reacción con esa ID')
            return
        await ctx.send('Se borró correctamente')
    
    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send('Me tenés que dar una ID como argumento')
            return
        if isinstance(error.original, bson.errors.InvalidId):
            await ctx.send('Ingresá una ID válida')
            return
        raise error
    
    @commands.command(brief='Muestra los reaction-role de este server', help='Te muestra un embed con los reaction-role de este server, si son muchos los separa en páginas. Por cada reaction-role muestra, su ID, el link del mensaje, la reacción y el rol que asigna.')
    async def list(self, ctx):
        guild_id = ctx.guild.id

        contents = []
        embed = discord.Embed()
        for x in mongoreactions.find({'guild_id': guild_id}):
            embed.add_field(name=str(x['_id']), value=f"[Hacé click acá](https://discord.com/channels/{x['guild_id']}/{x['channel_id']}/{x['msg_id']})\n{x['reaction_name']}\n<@&{x['role_id']}>", inline=True)
            if len(embed.fields) == 24:
                contents.append(embed)
                embed = discord.Embed()
        
        contents.append(embed)
        
        if contents == []:
            await ctx.send('No hay ningún reaction-role en este server')
            return
        
        pages = len(contents)
        cur_page = 1
        contents[0].set_footer(text=f'Pagina {cur_page}/{pages}')
        message = await ctx.send(embed=contents[0])

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=15, check=check)
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    contents[cur_page-1].set_footer(text=f'Pagina {cur_page}/{pages}')
                    await message.edit(embed=contents[cur_page-1])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    contents[cur_page - 1].set_footer(text=f'Pagina {cur_page}/{pages}')
                    await message.edit(embed=contents[cur_page-1])
                    await message.remove_reaction(reaction, user)
                else:
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.remove_reaction("◀️", self.client.user)
                await message.remove_reaction("▶️", self.client.user)
                break

    async def process_reaction(self, payload):
        for i in mongoreactions.find():
            if payload.message_id == i['msg_id'] and payload.channel_id == i['channel_id'] and payload.emoji.name == i['reaction_name']:
                guild = self.client.get_guild(payload.guild_id)
                member = get(guild.members, id=payload.user_id)
                if member.bot:
                    return
                if payload.event_type == 'REACTION_ADD':
                    await member.add_roles(member.guild.get_role(i['role_id']))
                elif payload.event_type == 'REACTION_REMOVE':
                    await member.remove_roles(member.guild.get_role(i['role_id']))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.process_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.process_reaction(payload)


def setup(client):
    client.add_cog(Reaction(client))
