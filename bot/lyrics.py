import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import re
from discord_components import *

class LyricsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def searchGenius(self, title):
        raw = requests.get(f"https://genius.com/search?q={title}").content.decode('utf-8')
        soup = BeautifulSoup(raw,'html.parser')

        column = soup.find("div", {'class': 'column_layout-column_span column_layout-column_span--primary'})

        print(column)

        results = []

        for e in column.find_all("a", {'class': 'mini_card'}):
            json = {
                'href': e['href'],
                'title': e.find("div", {'class': 'mini_card-title'}),
                'artist': e.find("div", {'class': 'mini_card-subtitle'}),
                'type': 'genius'
            }

            results.append(json)
            if len(results) >= 10:
                break 
        
        return result
    
    @commands.command(name="lyrics", aliases=["ly"])
    async def searchLyrics(self, ctx, *, title) :
        results = self.searchGenius(title)
        
        if len(results) == 0:
            await ctx.send("Can't find the song!")
        else:
            opt = []

            for song in results:
                opt.append(SelectOption(label=song['title'], value=song['href']))

            comp = Select(placeholder= "Select one of the song", options=opt)
            
            await ctx.send("Pick one of the list", components = comp)

def setup(bot):
    bot.add_cog(LyricsCog(bot))