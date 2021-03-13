import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import re

text_channels = {}
voice_channels = {}

class CustomChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="createvoice", aliases=["cv"])
    async def createVoiceRoomCmd(self, ctx, *, title) :
        if ctx.message.author.id in voice_channels:
            await ctx.send("You can only have 1 custom channel at the same time! !dv for delete.")
            return

        success = True
        try:
            guild = ctx.message.guild
            channel = await guild.create_voice_channel(title, category = discord.utils.get(guild.categories, name="Custom"))
            voice_channels[ctx.message.author.id] = channel
        except:
            success = False
        
        if success:
            await ctx.send("Room created!")
        else:
            await ctx.send("Sorry, there is something wrong :(")

    @commands.command(name="deletevoice", aliases=["dv"])
    async def deleteVoiceRoomCmd(self, ctx) :
        if ctx.message.author.id not in voice_channels:
            await ctx.send("You don't have any custom channel right now!")
            return

        success = True
        try:
            await voice_channels[ctx.message.author.id].delete()
            del voice_channels[ctx.message.author.id]
        except:
            success = False
        
        if success:
            await ctx.send("Room deleted!")
        else:
            await ctx.send("Sorry, there is something wrong :(")

def setup(bot):
    bot.add_cog(CustomChannelCog(bot))