import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import json
import asyncio
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
import datetime
import DiscordUtils
import praw
import apraw
import jishaku
import aiohttp
import string
import requests
import time, threading
import asyncio
from pathlib import Path

def get_prefix(client,message):

    with open("other_files\prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix = get_prefix,intents = intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


bot.remove_command("help")




@bot.command()
async def load(ctx,extension):
    bot.load_extension(f'Cogs.{extension}')
    await ctx.channel.send("Cogs loaded")

@bot.command()
async def unload(ctx,extension):
    bot.unload_extension(f'Cogs.{extension}')
    await ctx.channel.send("Cogs unloaded")

bot.load_extension('jishaku')

for filename in os.listdir("./Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")

def convert(time):
    pos = ['s','m','h','d']
    time_dict = {"s":1,"m":60,"h":3600,"d":3600*24}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2
    return val * time_dict[unit]

async def get_bank_data():
    with open("other_files\mainbank.json",'r') as f:
        users = json.load(f)
    return users

async def update_bank(user,change=0,mode = "wallet"):
    users = await get_bank_data()
    users[str(user.id)][mode] +=change
    with open("other_files\mainbank.json",'w') as f:
        json.dump(users,f)

    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return user

@bot.command()
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    if amount ==None:
        await ctx.send("Please enter the amount!")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You dont have enough credits")
        return
    if amount < 0:
        await ctx.send("Amount cannot be negative noob")
        return
    await update_bank(ctx.author,amount,amount)
    await update_bank(ctx.author,amount,-1*amount,"bank")
    await ctx.send(f"You withdrew {amount} noahcoins")

async def open_account(user):
    users = await get_bank_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0

    with open("other_files\mainbank.json",'r+') as f:
        json.dump(users,f)
    return True

@bot.event
async def on_guild_join(guild):
    with open("other_files\prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = "noah "
    with open("other_files\prefixes.json", "w") as f:
        json.dump(prefixes,f,indent =4)

@bot.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    wallet_amt = users[str(user.id)]['wallet']
    bank_amt = users[str(user.id)]['bank']
    embed = discord.Embed(title = f"{ctx.author.name}'s balance",color = discord.Color.red())
    embed.add_field(name = "Wallet balance",value = wallet_amt)
    embed.add_field(name = "Bank balance",value = bank_amt)
    await ctx.send(embed = embed)

@bot.command()
async def beg(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    earnings = random.randrange(101)
    await ctx.send(f"**Someone gave you {earnings} noacoins!**")
    users[str(user.id)]['wallet'] += earnings
    with open("other_files\mainbank.json",'w') as f:
        users = json.dump(users,f)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print("{} logged in successfully \n".format(bot.user))
        print(f"{guild.name}(id: {guild.id})")
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild members:\n -  {members}')
    await bot.change_presence(activity=discord.Game(name = "on {} servers".format(len(bot.guilds))))
    await bot.change_presence(activity = discord.Streaming(name = "Streaming",url = "https://twitch.com"))
    await bot.change_presence(activity=discord.Activity(type = discord.ActivityType.listening,name = "Noah"))
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching,name = "How was Noah made"))
    print(guild.members)
    print("\n")
    print(list(filter(lambda m: not m.bot, guild.members)))
    print(bot.user)
    for server in bot.guilds:
        for channel in server.channels:
            channel_type = channel.type
            if channel.type == discord.ChannelType.text:
                invitelinknew = await channel.create_invite(destination=channel, xkcd=True, max_uses=100)
                print(invitelinknew.url)
                break

async def change_presence():
    await bot.wait_until_ready()
    statuses = ['Noah',f'on {len(bot.guilds)} servers | noah help','discord.py']
    while not bot.is_closed():
        status = random.choice(statuses)

        await bot.change_presence(activity=discord.Game(name = status))


        await asyncio.sleep(10)
bot.loop.create_task(change_presence())

@bot.event
async  def on_member_join(member):
    channel = bot.get_all_channels()
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to the server!! am currently developing so please dont mind if i didnt mention the server name (have a nice day)")

@commands.has_permissions(administrator=True)
async def changeprefix(ctx,prefix):
    with open("other_files\prefixes.json",'r') as f:
        prefixes = json.load()
    prefixes[str(ctx.guild.id)] = prefix
    with open("other_files\prefixes.json",'w') as f:
        json.dump(prefixes, f,indent=4)


@bot.event
async  def on_message(message):
    try:
        if message.content == '<@!796735541101854740>':

            with open("prefixes.json", "r") as f:
                prefixes = json.load(f)

            pre = prefixes[str(message.guild.id)]

            await message.channel.send(f"My prefix for this server is {pre}")
    except:
        pass
    
    await bot.process_commands(message)


# @bot.event
# async  def on_error(event , *args , **kwargs):
#     with open("other_files\err.log" , 'a') as f:
#         if event == "on_message":
#             f.write(f"Unhandled message: {args[0]}\n")
#         else:
#             raise

@bot.command()
async def allcommands(ctx):
    await ctx.send(len(bot.commands))

# @bot.event
# async  def on_command_error(ctx,error):
#     try:
#         if isinstance(error,commands.errors.CheckFailure):
#                 await ctx.send("You dont have permission to do that! XD")
#         elif isinstance(error , commands.CommandNotFound):
#             await ctx.send("This command do not exist use `noah help` to see the commands available")
#     except discord.errors.Forbidden:
#         await ctx.send("Make sure I have the following permissions: `Manage Messages`, `Read Message History`, "
#                        "`Add Reactions`, `Mute Members`")

with open("other_files\\token.0",'r',encoding="utf-8") as f:
    token = f.read()

bot.run(token)
