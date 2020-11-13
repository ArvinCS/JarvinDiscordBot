import discord
from discord.ext import commands
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
import json

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

@client.command(name="nhentai")
async def nhentai(ctx, id=696969):
    # raw = requests.get(f"https://api.getproxylist.com/proxy?allowsHttps=1").content.decode('utf-8')
    page = 1
    maxPage = 30

    raw = requests.get(f"https://nhentai.net/g/{id}").content.decode('utf-8')
    soup = BeautifulSoup(raw, 'html.parser')

    for div in soup.find_all("div", {'class': 'tag-container field-name'}):
        if div.text.strip().startswith("Pages"):
            maxPage = int(div.find("span").text.strip())
            break
    
    raw = requests.get(f"https://nhentai.net/g/{id}/{page}/").content.decode('utf-8')
    soup = BeautifulSoup(raw, 'html.parser')

    cover = soup.find("section", {'id': 'image-container'})
    cover_url = cover.find("img")['src']
    
    message = await ctx.send(cover_url)

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
    
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)

            if str(reaction.emoji) == "▶️" and page < maxPage:
                page += 1

                raw = requests.get(f"https://nhentai.net/g/{id}/{page}/").content.decode('utf-8')
                soup = BeautifulSoup(raw, 'html.parser')

                cover = soup.find("section", {'id': 'image-container'})
                cover_url = cover.find("img")['src']
                
                print(cover)
                print(cover_url)
                await message.edit(content=cover_url)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and page > 1:
                page -= 1

                raw = requests.get(f"https://nhentai.net/g/{id}/{page}/").content.decode('utf-8')
                soup = BeautifulSoup(raw, 'html.parser')

                cover = soup.find("section", {'id': 'image-container'})
                cover_url = cover.find("img")['src']
                
                await message.edit(content=cover_url)
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

@client.command(name="topanime")
async def topAnime(ctx, start=1):
    raw = requests.get(f"https://myanimelist.net/topanime.php?limit={start-1}").content.decode('utf-8')
    soup = BeautifulSoup(raw,'html.parser')
    topList = soup.find_all("tr", {'class': 'ranking-list'})
    
    embedPage = discord.Embed(title=f"Top Anime ({start}-{start+19})", description="By rating", color=0x00ff00)
    cnt = 0
    for tr in topList:
        cnt += 1
        h3 = tr.find("h3", {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
        embedPage.add_field(name=f"{start+cnt-1}.{h3.find('a').text}", value=f"⭐ {tr.find('div', {'class': 'js-top-ranking-score-col di-ib al'}).find('span').text}", inline=False)
        if cnt >= 20:
            break
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

    message = await ctx.send(embed=embedPage)
    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)

            if str(reaction.emoji) == "▶️" and start+20 <= 1000:
                start += 20

                raw = requests.get(f"https://myanimelist.net/topanime.php?limit={start-1}").content.decode('utf-8')
                soup = BeautifulSoup(raw,'html.parser')
                topList = soup.find_all("tr", {'class': 'ranking-list'})
                # topList = soup.find_all("h3", {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
                embedPage = discord.Embed(title=f"Top Anime ({start}-{start+19})", description="By rating", color=0x00ff00)
                cnt = 0
                for tr in topList:
                    cnt += 1
                    h3 = tr.find("h3", {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
                    embedPage.add_field(name=f"{start+cnt-1}.{h3.find('a').text}", value=f"⭐ {tr.find('div', {'class': 'js-top-ranking-score-col di-ib al'}).find('span').text}", inline=False)
                    if cnt >= 20:
                        break
                await message.edit(embed=embedPage)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and start-20 >= 1:
                start -= 20

                raw = requests.get(f"https://myanimelist.net/topanime.php?limit={start-1}").content.decode('utf-8')
                soup = BeautifulSoup(raw,'html.parser')
                topList = soup.find_all("tr", {'class': 'ranking-list'})
                # topList = soup.find_all("h3", {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
                embedPage = discord.Embed(title=f"Top Anime ({start}-{start+19})", description="By rating", color=0x00ff00)
                cnt = 0
                for tr in topList:
                    cnt += 1
                    h3 = tr.find("h3", {'class': 'hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3'})
                    embedPage.add_field(name=f"{start+cnt-1}.{h3.find('a').text}", value=f"⭐ {tr.find('div', {'class': 'js-top-ranking-score-col di-ib al'}).find('span').text}", inline=False)
                    if cnt >= 20:
                        break
                await message.edit(embed=embedPage)
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

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
        'url': anime_url,
        'thumbnail': anime.find("img", {'itemprop': 'image'})['data-src'],
        'description': anime.find("p", {'itemprop': 'description'}).text
    }

    # print(raw)
    for attr in re.findall(r'\<div.+\>[\s\n]+\<span[\s]+class\=\"dark_text\"\>(\w+)\:\<\/span\>[\s\n]+(.+?)[\s\n]+\<\/div\>', raw):
        # print(attr)
        # print(attr[0] + " -> " + attr[1])
        json[attr[0].lower()] = attr[1]
    
    # print(json['episodes'])
    return json

@client.command(name="anime")
async def anime(ctx, *, title):
    json = None
    found = True
    print(title)
    try:
        json = findAnime(title)
    except:
        found = False
    
    if found:
        embedPage = discord.Embed(title=json['title'], description=json['description'], color=0x00ff00)
        embedPage.set_image(url=json['thumbnail'])
        # embedPage.set_thumbnail(url=json['thumbnail'])
        embedPage.add_field(name="Episodes", value=json['episodes'], inline=False)
        embedPage.add_field(name="Duration", value=json['duration'], inline=False)
        embedPage.add_field(name="Source", value=json['source'], inline=False)
        await ctx.send(embed=embedPage)
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

# print(findAnime("Grand Blue"))
client.run(token)
