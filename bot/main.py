import discord
from discord.ext import commands
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

client = commands.Bot(command_prefix="!")
token = os.getenv("DISCORD_BOT_TOKEN")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
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

def findAnime(title):
    search = title.replace(' ', '%20')

    raw = requests.get(f"https://myanimelist.net/search/all?q={search}&cat=all").content.decode('utf-8')
    soup = BeautifulSoup(raw,'html.parser')

    page = soup.find_all("div", {'class': 'list di-t w100'})

    anime_url = page[0].find("a", {'class': 'hoverinfo_trigger fw-b fl-l'})['href']
    raw = requests.get(anime_url).content.decode('utf-8')
    anime = BeautifulSoup(raw,'html.parser')

    json =  {
        'title': anime.find("h1", {'class': 'title-name h1_bold_none'}).text,
        'url': anime_url
    }

    # print(raw)
    for attr in re.findall(r'\<div[\s]+class\=\"spaceit\"\>[\s\n]+\<span[\s]+class\=\"dark_text\"\>(\w+)\:\<\/span\>[\s\n]+(\d+)[\s\n]+\<\/div\>', raw):
        # print(attr)
        # print(attr[0] + " -> " + attr[1])
        json[attr[0].lower()] = attr[1]
    
    # print(json['episodes'])
    return json

@client.command(name="anime")
async def anime(ctx, title):
    json = None
    found = True
    print(title)
    try:
        json = FindAnime(title)
    except:
        found = False
    
    if found:
        await ctx.send(f"Anime: {json['title']}\nEpisodes: {json['episodes']}")
    else:
        await ctx.send("The anime isn't exist!")
    

@client.event
async def on_message(message):
    print(message.content)
    if re.match(r'^(https:|http:)[\/][\/](www|web)\.([^\/]+[\.])*facebook\.com\/(.+?)\/(posts|videos)\/(\d+)', message.content):
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
        else:
            return None
        
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
        html = requests.get("https://www.instagram.com/p/CHSY_kMnVec/").content.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # video_url = soup.find("meta", property="og:video")['content']

        await message.delete()
        await message.channel.send(html[:1888])
        # await message.channel.send(f"{message.author.name} sent {video_url}")
    else:
        await client.process_commands(message)

# findAnime("Grand Blue")
client.run(token)
