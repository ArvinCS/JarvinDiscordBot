import discord
from discord.ext import commands, tasks
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
import json
import collections
from discord_components import *
import urllib.parse

client = commands.Bot(command_prefix="!")
token = os.getenv("DISCORD_BOT_TOKEN")

initial_extensions = [
    'instagram',
    'customchannel',
    # 'lyrics'
]

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    DiscordComponents(client)
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

@client.command(name="covid")
async def covid(ctx):
    raw = requests.get(f"https://data.covid19.go.id/public/api/prov.json").content.decode('utf-8')
    jsn = json.loads(raw)

    embedPage = discord.Embed(title=f"Data COVID-19 Indonesia", description="Berdasarkan setiap provinsi", color=0x00ff00)
    
    data = dict()
    for prov in jsn['list_data']:
        print(prov)
        data[prov['key']] = f"Positif: {prov['jumlah_kasus']}\nMeninggal: {prov['jumlah_meninggal']}\nSembuh: {prov['jumlah_sembuh']}"

    page = 1
    maxPage = int((len(data)+5)/6)
    
    data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    keys_list = list(data.keys())

    for index in range((page-1)*6, min(page*6, len(data))):
        embedPage.add_field(name=keys_list[index], value=data[keys_list[index]])

    buttons = [
        Button(style=ButtonStyle.blue, label="Previous", custom_id="prv"), 
        Button(style=ButtonStyle.blue, label="Next", custom_id="nxt")
    ]

    message = await ctx.send(embed=embedPage, components=buttons)
    
    # def check(reaction, user):
    #     return reaction.message == message and (not user.bot) and str(reaction.emoji) in ["◀️", "▶️"]
    
    # while True:
    #     try:
    #         reaction, user = await message.wait_for_component#("button_click", timeout=300, check=check)
            
    #         if str(reaction.emoji) == "▶️" and page < maxPage:
    #             page += 1

    #             embedPage = discord.Embed(title=f"Data COVID-19 Indonesia", description="Berdasarkan setiap provinsi", color=0x00ff00)
                
    #             for index in range((page-1)*6, min(page*6, len(data))):
    #                 embedPage.add_field(name=keys_list[index], value=data[keys_list[index]])

    #             await message.edit(embed=embedPage)
    #             await message.remove_reaction(reaction, user)
    #         elif str(reaction.emoji) == "◀️" and page > 1:
    #             page -= 1

    #             embedPage = discord.Embed(title=f"Data COVID-19 Indonesia", description="Berdasarkan setiap provinsi", color=0x00ff00)
                
    #             for index in range((page-1)*6, min(page*6, len(data))):
    #                 embedPage.add_field(name=keys_list[index], value=data[keys_list[index]])

    #             await message.edit(embed=embedPage)
    #             await message.remove_reaction(reaction, user)
    #         else:
    #             await message.remove_reaction(reaction, user)
    #             # removes reactions if the user tries to go forward on the last page or
    #             # backwards on the first page
    #     except:
    #         await message.delete()
    #         break
    #         # ending the loop if user doesn't react after x seconds

@client.command(name="nsearch")
async def nhentaiSearch(ctx, *, title):
    oldTitle = title
    raw = requests.get("https://nhentai.net/search/?q="+title.replace(" ", "+")).content.decode('utf-8')
    soup = BeautifulSoup(raw, 'html.parser')

    result = []
    for gallery in soup.find_all("div", {'class': 'gallery'}):
        json = {}
        json['url'] = "https://nhentai.net" + gallery.find("a", {'class': 'cover'})['href']
        json['thumbnail'] = gallery.find("img")['data-src']
        json['title'] = gallery.find("div").text
        result.append(json)

    if(len(result) > 0):
        page = 1

        embedPage = discord.Embed(title=f"Search result ({oldTitle})", description=f"Total: {len(result)} results", color=0x00ff00)
        embedPage.set_image(url=result[page-1]['thumbnail'])
        embedPage.add_field(name="Title", value=result[page-1]['title'])
        embedPage.add_field(name="Code", value=re.match(r"https:\/\/nhentai\.net\/g\/(\d+)", result[page-1]['url']).group(1))

        message = await ctx.send(embed=embedPage)

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return reaction.message == message and (not user.bot) and user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        
        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)

                if str(reaction.emoji) == "▶️" and page < len(result):
                    page += 1

                    embedPage = discord.Embed(title=f"Search result ({oldTitle})", description=f"Total: {len(result)} results", color=0x00ff00)
                    embedPage.set_image(url=result[page-1]['thumbnail'])
                    embedPage.add_field(name="Title", value=result[page-1]['title'])
                    embedPage.add_field(name="Code", value=re.match(r"https:\/\/nhentai\.net\/g\/(\d+)", result[page-1]['url']).group(1))
                    
                    await message.edit(embed=embedPage)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1

                    embedPage = discord.Embed(title=f"Search result ({oldTitle})", description=f"Total: {len(result)} results", color=0x00ff00)
                    embedPage.set_image(url=result[page-1]['thumbnail'])
                    embedPage.add_field(name="Title", value=result[page-1]['title'])
                    embedPage.add_field(name="Code", value=re.match(r"https:\/\/nhentai\.net\/g\/(\d+)", result[page-1]['url']).group(1))
                    
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
    else:
        await ctx.send("Not found!")

@client.command(name="nhentai")
async def nhentai(ctx, id=190105, public=True):
    # raw = requests.get(f"https://api.getproxylist.com/proxy?allowsHttps=1").content.decode('utf-8')
    page = 1
    maxPage = 30

    raw = requests.get(f"https://nhentai.net/g/{id}").content.decode('utf-8')
    soup = BeautifulSoup(raw, 'html.parser')

    for div in soup.find_all("div", {'class': 'tag-container field-name'}):
        if div.text.strip().startswith("Pages"):
            maxPage = int(div.find("span").text.strip())
            print(maxPage)
            break
    
    raw = requests.get(f"https://nhentai.net/g/{id}/{page}/").content.decode('utf-8')
    soup = BeautifulSoup(raw, 'html.parser')

    cover = soup.find("section", {'id': 'image-container'})
    cover_url = cover.find("img")['src']
    
    message = await ctx.send(cover_url)

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return reaction.message == message and (not user.bot) and (public or user == ctx.author) and str(reaction.emoji) in ["◀️", "▶️"]
    
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)

            if str(reaction.emoji) == "▶️" and page < maxPage:
                page += 1

                raw = requests.get(f"https://nhentai.net/g/{id}/{page}/").content.decode('utf-8')
                soup = BeautifulSoup(raw, 'html.parser')

                cover = soup.find("section", {'id': 'image-container'})
                cover_url = cover.find("img")['src']
                
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
    if "facebook.com" in message.content:
        if message.author.bot:
            return None
        
        # result = re.match(r'^https:|http:[\/][\/]www\.([^\/]+[\.])*facebook\.com\/(.+?)\/posts\/(\d+)', message.content)
        html = requests.get(message.content.replace("www", "m")).content.decode('utf-8')

        soup = BeautifulSoup(html, 'html.parser')
        
        videos = soup.find_all("div", {'class' : 'cc'})

        video_url = ""
        if len(videos) > 0:
            link = videos[0].find_all("a")[0]['href']
            link = urllib.parse.unquote(link).partition("src=")[2]
            video_url = link
        else:
            return None
        
        
        if video_url is None:
            return
        
        # embedPage = discord.Embed(title="Video", description=f"Sent by {message.author.name}", color=0x00ff00)
        # embedPage.set_image(url=json['thumbnail'])
        # # embedPage.set_thumbnail(url=json['thumbnail'])
        # embedPage.add_field(name="Episodes", value=json['episodes'], inline=False)
        # embedPage.add_field(name="Duration", value=json['duration'], inline=False)
        # embedPage.add_field(name="Source", value=json['source'], inline=False)
        # await ctx.send(embed=embedPage)

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
        html = requests.get("https://www.instagram.com/p/CHSY_kMnVec/").content.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # video_url = soup.find("meta", property="og:video")['content']

        await message.delete()
        await message.channel.send(html[:1888])
        # await message.channel.send(f"{message.author.name} sent {video_url}")
    else:
        await client.process_commands(message)

# html = requests.get("https://www.facebook.com/muhammad.bahtiar.3994/videos/4248281311854098/").content.decode('utf-8')
# print(html)
# print(video_url)
# print(findAnime("Grand Blue"))

if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)

client.run(token)