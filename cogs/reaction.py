import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import os
import pymongo

mongo_url = token = os.getenv('MONGO_URL')
mongoclient = pymongo.MongoClient(mongo_url)
mongodb = mongoclient['Feynman']
mongoreactions = mongodb['Reactions']

reactions_dict = [
    {
        'msg_id': 830177189764661278,
        'channel_id': 734846058613440643,
        'reaction_name': '👀',
        'role_id': 730894218297475083
    }
]


class Reaction(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

    @commands.command()
    async def reactiones(self, ctx):
        print(reactions_dict)

    @commands.command()
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

        mongoreactions.insert_one({'msg_id': msg_id, 'channel_id': channel_id, 'reaction_name': reaction_name, 'role_id': role_id})
        msg = await channel.fetch_message(msg_id)
        await msg.add_reaction(reaction)

        embed = discord.Embed(title="Setup Listo")
        embed.add_field(name="Canal", value="<#"+str(channel_id)+'>', inline=False)
        embed.add_field(name="ID del mensaje", value=str(msg_id), inline=False)
        embed.add_field(name="Emoji", value=reaction, inline=True)
        embed.add_field(name="Rol", value="<@&"+str(role_id)+'>', inline=True)
        await ctx.send(embed=embed)
        await clear_all()

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
