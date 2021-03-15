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
    
    async def getVoiceChannel(self, ctx, user):
        role = next((role for role in user.roles if "@owner" in role.name.lower()), None)
        if role is None:
            return None

        return discord.utils.get(ctx.message.guild.channels, id=int(role.name.split('@')[0]))

    @commands.command(name="createvoice", aliases=["cv"])
    async def createVoiceRoomCmd(self, ctx, *, title) :
        user = ctx.message.author
        channel = await self.getVoiceChannel(ctx, user)

        if channel is not None:
            await ctx.send("You can only have 1 custom channel at the same time! !dv for delete.")
            return

        success = True
        try:
            guild = ctx.message.guild
            channel = await guild.create_voice_channel(title, category = discord.utils.get(guild.categories, name="Custom"))
            role = await guild.create_role(name=f"{channel.id}@owner")
            await user.add_roles(role)
        except:
            success = False
        
        if success:
            await ctx.send("Room created!")
        else:
            await ctx.send("Sorry, there is something wrong :(")

    @commands.command(name="limitvoice", aliases=["lv"])
    async def setVoiceRoomLimitCmd(self, ctx, limit) :
        user = ctx.message.author
        channel = await self.getVoiceChannel(ctx, user)

        if channel is None:
            await ctx.send("You don't have any custom channel right now!")
            return

        try:
            limit = int(limit)
        except:
            pass

        if not isinstance(limit, int):
            await ctx.send("Limit must be a number!")
            return
        
        if limit < 0 or limit > 99:
            await ctx.send("Limit must be in range 0 and 99 (inclusive)!")
            return

        success = True
        try:
            await channel.edit(user_limit= int(limit))
        except:
            success = False
        
        if success:
            await ctx.send(f"Limit member set to {limit}!")
        else:
            await ctx.send("Sorry, there is something wrong :(")
    
    @commands.command(name="deletevoice", aliases=["dv"])
    async def deleteVoiceRoomCmd(self, ctx) :
        user = ctx.message.author
        channel = await self.getVoiceChannel(ctx, user)

        if channel is None:
            await ctx.send("You don't have any custom channel right now!")
            return

        success = True
        try:
            role = next((role for role in user.roles if "@owner" in role.name.lower()), None)
            await user.remove_roles(role)
            await role.delete()
            await channel.delete()
        except:
            success = False
        
        if success:
            await ctx.send("Room deleted!")
        else:
            await ctx.send("Sorry, there is something wrong :(")

def setup(bot):
    bot.add_cog(CustomChannelCog(bot))