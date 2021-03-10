import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import re

class InstagramCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def findUser(self, id):
        raw = requests.get(f"https://www.instagram.com/{id}/").content.decode('utf-8')
        soup = BeautifulSoup(raw,'html.parser')

        print(raw)

        json =  {
            'photo': soup.find("meta", property="og:image")['content'],
            'username': soup.find("meta", property="og:title")['content'],
            "url": soup.find("meta", property="og:url")['content'],
        }

        description = soup.find("meta", property="og:description")['content']
        if(re.match(r'((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sFollowers.+?((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sFollowing.+?((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sPosts', description)):
            groups = re.search(r'((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sFollowers.+?((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sFollowing.+?((\d{1,3},\d{3}(,\d{3})*)(\.\d*)?|\d+\.?\d*)\sPosts', description)

            json['followers'] = groups.group(1)
            json['following'] = groups.group(5)
            json['posts_count'] = groups.group(9)
        
        # print(json['episodes'])
        return json
    
    @commands.command(name="instagram", aliases=["ig"])
    async def searchprofile(self, ctx, *, id) :
        json = None
        found = True
        try:
            json = self.findUser(id)
        except:
            found = False
        
        if found:
            embedPage = discord.Embed(title=id, color=0x00ff00)
            embedPage.set_image(url=json['photo'])
            # embedPage.set_thumbnail(url=json['thumbnail'])
            embedPage.add_field(name="URL", value=json['url'], inline=False)
            embedPage.add_field(name="Followers", value=json['followers'], inline=False)
            embedPage.add_field(name="Following", value=json['following'], inline=False)
            embedPage.add_field(name="Posts", value=json['posts_count'], inline=False)

            await ctx.send(embed=embedPage)
        else:
            await ctx.send("The anime isn't exist!")

def setup(bot):
    bot.add_cog(InstagramCog(bot))