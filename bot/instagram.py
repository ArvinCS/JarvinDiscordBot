import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import re
import json

class InstagramCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def findUser(self, id):
        url = f"https://www.instagram.com/{id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
        }

        data = json.loads(
            re.search(
                r"<script type=\"text/javascript\">window\._sharedData = (.*});",
                requests.get(url, headers=headers).text,
            ).group(1)
        )
        print(json.dumps(data, indent=4))
        result =  {
            'photo': data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["profile_pic_url_hd"],
            'username': data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["username"],
            "url": url,
            "description": "\n".join([data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["biography"], data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["external_url"]]),
            "followers": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"],
            "following": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_follow"]["count"],
            "posts_count": data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"],
        }
        
        return result
    
    @commands.command(name="instagram", aliases=["ig"])
    async def searchprofile(self, ctx, *, id) :
        data = None
        found = True
        try:
            data = self.findUser(id)
        except:
            found = False
        
        if found:
            embedPage = discord.Embed(title=id, color=0x00ff00)
            embedPage.set_image(url=data['photo'])
            # embedPage.set_thumbnail(url=data['thumbnail'])
            embedPage.add_field(name="URL", value=data['url'], inline=False)
            embedPage.add_field(name="Followers", value=data['followers'], inline=False)
            embedPage.add_field(name="Following", value=data['following'], inline=False)
            embedPage.add_field(name="Posts", value=data['posts_count'], inline=False)

            await ctx.send(embed=embedPage)
        else:
            await ctx.send("The user isn't exist!")

def setup(bot):
    bot.add_cog(InstagramCog(bot))