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

    @commands.command(brief='Adds a reaction-role to a message', help="With this command you can add a reaction-role following the instructions I'll tell you. You have to make sure I'm above the role you want me to grant, otherwise I won't be able to do my job.")
    async def add(self, ctx):

        def check_author(m):
            return m.author == ctx.message.author

        def check_reaction(reaction, user):
            return reaction.message.id == msg3.id and user == ctx.author

        async def clear_all():
            for i in msg_sent:
                await i.delete(delay=1.)
            return

        msg_sent = [ctx.message]

        msg1 = await ctx.send("In which channel is the message?")
        msg_sent.append(msg1)
        try:
            channel_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(channel_id)
            if not channel_id.channel_mentions:
                channel_id = int(channel_id.content)
                if self.client.get_channel(channel_id) is not None:
                    channel = self.client.get_channel(channel_id)
                else:
                    error_msg1a = await ctx.send('You have to give me a valid message')
                    msg_sent.append(error_msg1a)
                    await asyncio.sleep(5.)
                    return await clear_all()
            else:
                channel = channel_id.channel_mentions[0]
                channel_id = channel.id
        except ValueError:
            error_msg1b = await ctx.send('You have to give me a valid channel')
            msg_sent.append(error_msg1b)
            await asyncio.sleep(5.)
            return await clear_all()
        except asyncio.TimeoutError:
            return await clear_all()

        msg2 = await ctx.send("What is the message ID?")
        msg_sent.append(msg2)
        try:
            msg_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(msg_id)
            msg_id = int(msg_id.content)
            if await channel.fetch_message(msg_id) is None:
                error_msg2a = await ctx.send('You have to give a valid message ID, maybe it\'s not in the channel you told me before')
                msg_sent.append(error_msg2a)
                await asyncio.sleep(5.)
                return await clear_all()
        except asyncio.TimeoutError:
            return await clear_all()
        except ValueError:
            error_msg2b = await ctx.send('You have to give me a valid message ID')
            msg_sent.append(error_msg2b)
            await asyncio.sleep(5.)
            return await clear_all()

        msg3 = await ctx.send("React this message with the emoji you want for the reaction")
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

        msg4 = await ctx.send("What role you want me to give?")
        msg_sent.append(msg4)
        try:
            role_id = await self.client.wait_for("message", check=check_author, timeout=30.)
            msg_sent.append(role_id)
            if not role_id.role_mentions:
                role_id = int(role_id.content)
                if ctx.guild.get_role(role_id) is None:
                    error_msg4a = await ctx.send('You have to give me a valid role')
                    msg_sent.append(error_msg4a)
                    await asyncio.sleep(5.)
                    return await clear_all()
            else:
                role = role_id.role_mentions[0]
                role_id = role.id
        except ValueError:
            error_msg4b = await ctx.send('You have to give me a valid role')
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

        embed = discord.Embed(title="Setup Ready")
        embed.add_field(name="ID of the reaction", value=str(_id), inline=False)
        embed.add_field(name="Channel", value="<#"+str(channel_id)+'>', inline=False)
        embed.add_field(name="Link of the message", value=f'[click here]({msg.jump_url})', inline=False)
        embed.add_field(name="Emoji", value=reaction, inline=True)
        embed.add_field(name="Role", value="<@&"+str(role_id)+'>', inline=True)
        await ctx.send(embed=embed)
        await clear_all()

    @commands.command(brief='Deletes a reaction-role', help='Giving me the reaction ID, I will delete the reaction-role and I will stop giving the role to the users that react with the emoji.')
    async def delete(self, ctx, id):
        dlts = mongoreactions.delete_one({'_id': ObjectId(id)})
        if dlts.deleted_count != 1:
            await ctx.send('I didn\'t found any reaction with that ID')
            return
        await ctx.send('I\'ve deleted it correctly')
    
    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send('You have to give me a reaction ID')
            return
        if isinstance(error.original, bson.errors.InvalidId):
            await ctx.send('Invalid ID')
            return
        raise error
    
    @commands.command(brief='Shows you the list of reaction-roles of this server')
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
