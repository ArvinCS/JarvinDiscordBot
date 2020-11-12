import discord
from discord.ext import commands
import os
import re
import requests
from tqdm import tqdm

client = commands.Bot(command_prefix="!")
token = os.getenv("DISCORD_BOT_TOKEN")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.idle, activity = discord.Game("Listening to !help"))
    print("I'm online")

@client.command()
async def ping(ctx) :
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")

@client.command(name="whoami")
async def whoami(ctx) :
    await ctx.send(f"You are {ctx.message.author.name}")

@client.command()
async def clear(ctx, amount=3) :
    await ctx.channel.purge(limit=amount)

@client.event
async def on_message(message):
    print(message.content)
    if re.match(r'^(https:|http:)[\/][\/]www\.([^\/]+[\.])*facebook\.com\/(.+?)\/posts\/(\d+)', message.content):
        if message.author.bot:
            return None
        print("fb")
        # result = re.match(r'^https:|http:[\/][\/]www\.([^\/]+[\.])*facebook\.com\/(.+?)\/posts\/(\d+)', message.content)
        html = requests.get(message.content).content.decode('utf-8')

        _qualityhd = re.search('hd_src:"https', html)
        _qualitysd = re.search('sd_src:"https', html)
        _hd = re.search('hd_src:null', html)
        _sd = re.search('sd_src:null', html)

        list = []
        _thelist = [_qualityhd, _qualitysd, _hd, _sd]
        for id,val in enumerate(_thelist):
            if val != None:
                list.append(id)
        
        video_url = ""
        if 0 in list:
            video_url = re.search(rf'hd_src:"(.+?)"', html).group(1)
        elif 1 in list:
            video_url = re.search(rf'sd_src:"(.+?)"', html).group(1)

        await message.delete()
        await message.channel.send(f"{message.author.name} sent {video_url}")
        # file_size_request = requests.get(video_url, stream=True)
        # file_size = int(file_size_request.headers['Content-Length'])
        # block_size = 1024
        # filename = result.group(3)
        # t = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
        # with open(filename + '.mp4', 'wb') as f:
        #     for data in file_size_request.iter_content(block_size):
        #         t.update(len(data))
        #         f.write(data)
        # t.close()
        # with open(filename + '.mp4', 'wb') as f: 
        #     await message.channel.send(file=discord.File(f, 'meme.mp4'))
    elif re.match(r'(https:|http:)[\/][\/]www\.([^\/]+[\.])*instagram\.com\/p\/(\w+)', message.content):
        if message.author.bot:
            return None
        print("ig")
        html = requests.get(message.content).content.decode('utf-8')
        
        # print(html)
        video_url = re.search(rf'<meta property="og:video"[\s]content="(.+?)"[\s]/>', html).group(1)

        await message.delete()
        await message.channel.send(html)
        # await message.channel.send(f"{message.author.name} sent {video_url}")

client.run(token)
