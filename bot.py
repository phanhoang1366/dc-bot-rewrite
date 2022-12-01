# bot.py
import os
import random
import sqlite3
import asyncio
import threading
from typing import Sequence, Optional

from dismods.checktime import *
from dismods.insdeldb import *
from datetime import datetime
import parsedatetime
import dateparser
import subprocess
import re
import dismods.ggsearch
from dismods.vndict import vndict
from dismods.keep_alive import keep_alive
from dismods.dl import ydl
from dotenv import load_dotenv

import discord
from discord.ext import tasks, commands
from discord import app_commands

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']
#MY_GUILD = discord.Object(id=687132972591480854)

db = "database.db"
conn = sqlite3.connect(db)

cal = parsedatetime.Calendar()
        
class MyBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        #self.tree.copy_global_to(guild=MY_GUILD)
        self.check_remind.start()
        await self.tree.sync(guild=None)
        
    @tasks.loop()
    async def check_remind(self):
        conn.execute("""CREATE TABLE IF NOT EXISTS WARN (
                                "CaseID"    INTEGER,
                                "AuthorID"	INTEGER,
                                "WarnedID"	INTEGER,
                                "Timestamp"	INTEGER,
                                "Reason"	TEXT,
                                PRIMARY KEY("CaseID" AUTOINCREMENT));""")

        conn.execute("""CREATE TABLE IF NOT EXISTS REMINDME (
                                "ServerID"	INTEGER,
                                "ChannelID"	INTEGER,
                                "MessageID"	INTEGER,
                                "AuthorID"	INTEGER,
                                "UnixRemindTimestamp"	INTEGER);""")
                                
        await bot.wait_until_ready()
        while True:
            try:
                # I will rewrite this function, so that it supports threading and works more accurately.
                timerow = conn.execute("SELECT UnixRemindTimestamp FROM REMINDME ORDER BY UnixRemindTimestamp ASC LIMIT 1") # get earliest reminder
                time = timerow.fetchone()[0]
                if check_past(time):
                    rows = conn.execute("SELECT * FROM REMINDME ORDER BY UnixRemindTimestamp ASC LIMIT 1")
                    for row in rows:
                        user = await bot.fetch_user(row[3])
                        url = "https://discord.com/channels/" + str(row[0]) + "/" + str(row[1]) + "/" + str(row[2])
                        embed = discord.Embed(title="Hello, I'm here to remind you!", url=url)
                        if check_too_late(time):
                            embed.set_footer(text="oops it's too late")
                        else:
                            embed.set_footer(text="")
                        await user.send(embed=embed)
                    delete_remind(time)
            except TypeError:
                pass
            await asyncio.sleep(1)

bot = MyBot(intents = discord.Intents.all())

@bot.tree.command(description='Download videos from Youtube or Facebook with yt-dlp')
@app_commands.describe(
    url='The URL you want to get the video from.',
    option='Optional. Defaults to lowest watchable quality.',
)
async def dl(interaction: discord.Interaction, url: str, option: Optional[str] = ""):
    await interaction.response.send_message('Working on it.')
    
    status = ydl(url, option)
    if status == 0 or status == 1:
        if status == 0:
            upfile = "video.mp4"
        else:
            upfile = "video.mp4.webm"
        try:
            await interaction.edit_original_response(content="Here is your video:", attachments=[discord.File(upfile)])
        except discord.errors.HTTPException:
            await interaction.edit_original_response(content='Looks like the file is too large, so I can\'t upload it.')
        os.remove(upfile)
    elif status == 10 or status == 11:
        await interaction.edit_original_response(content="Something happened. Output:", attachments=[discord.File("output.txt")])
        os.remove("output.txt")
    

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )
    
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='99', help='Responds with a random quote from Brooklyn 99')
    async def nine_nine(self, ctx):
        brooklyn_99_quotes = [
            'I\'m the human form of the 💯 emoji.',
            'Bingpot!',
            (
                'Cool. Cool cool cool cool cool cool cool, '
                'no doubt no doubt no doubt no doubt.'
            ),
        ]

        response = random.choice(brooklyn_99_quotes)
        await ctx.send(response)

    @commands.command(pass_context = True, help='Fake warn someone (why?)')
    async def fakewarn(self, ctx, user:discord.User = None, *reason:str):
    
        await ctx.message.delete()

        if user is None:
            await ctx.send("```user is a required argument that is missing.```", delete_after = 2)
            return

        if not reason:
            reason = "No reason given."
        else:
            reason = ' '.join(reason)

        author = ctx.message.author.id
        warned = user.id

        if(ctx.message.author.id == user.id):
            if(not "--force-yes" in reason):
                await ctx.send("You can't warn yourself!", delete_after = 2)
                return
            else:
                reason = reason.replace("--force-yes", "")

        embed=discord.Embed(title=f"{user.name} has been warned.", description=f"Reason: {reason}", color=0xff0000)
        await ctx.send(embed=embed, delete_after = 5)

        await asyncio.sleep(1)

        try:
            user = await bot.fetch_user(user_id=warned)
            await user.send("You are not actually warned.")
        except discord.errors.Forbidden:
            print(user.name)
            print("I can't send a message to this user.")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, help='A warn command. Needs a role named Muted to work.')
    async def warn(self, ctx, user:discord.User = None, *reason:str):
        if(ctx.message.author.guild_permissions.administrator):
            if user is None:
                await ctx.send("```user is a required argument that is missing.```", delete_after = 2)
                return

            if not reason:
                reason = "No reason given."
            else:
                reason = ' '.join(reason)
            
            author = ctx.message.author.id
            warned = user.id

            if(ctx.message.author.id == user.id):
                if(not "--force-yes" in reason):
                    await ctx.send("You can't warn yourself!", delete_after = 2)
                    return
                else:
                    reason = reason.replace("--force-yes", "")
            
            timestamp = datetime.now().timestamp()
            # dump to a database
            insert_warn(author, warned, timestamp, reason)
            
            embed=discord.Embed(title=f"{user.name} has been warned.", description=f"Reason: {reason}", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have enough permissions to do this.", delete_after = 2)


    @commands.command(pass_context = True, help='Remove warn by moderator.')
    async def rmwarn(self, ctx, caseid:int):
        if ctx.message.author.guild_permissions.administrator:
            try:
                delete_warn(caseid)
                await ctx.send(f"CaseID {caseid} deleted.")
            except Exception:
                await ctx.send("CaseID doesn't exist.", delete_after = 2)
        else:
            await ctx.send("Permission denied.", delete_after = 2)
            
            

    @commands.command(pass_context = True, help="Another test mute command")
    async def mute(self, ctx, member: discord.Member, *reason:str):
         if ctx.message.author.guild_permissions.administrator:
            role = discord.utils.get(member.guild.roles, name='Muted')
            await member.add_roles(role)
            
            embed = discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff0000)
            
            if not reason:
                embed.set_footer(text="No reason given.")
            else:
                embed.set_footer(text=f"Reason: {reason}")
            
            await ctx.send(embed=embed)
         else:
            embed = discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
            await ctx.send(embed=embed, delete_after = 2)
            
            
    @commands.command(pass_context = True, help="An unmute command. Same thing as mute.")
    async def unmute(self, ctx, member: discord.Member):
        if ctx.message.author.guild_permissions.administrator:
            role = discord.utils.get(member.guild.roles, name='Muted')
            await member.remove_roles(role)
            embed = discord.Embed(title="User Unmuted!", description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author), color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff0000)
            await ctx.send(embed=embed, delete_after = 2)

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, help='Download videos from Youtube or Facebook')
    async def dl(self, ctx, url, option: str = ""):
        if url is None:
            await ctx.send("An URL is missing.", delete_after = 2)
            return
            
        status = ydl(url, option)
        if status == 0 or status == 1:
            if status == 0:
                upfile = "video.mp4"
            else:
                upfile = "video.mp4.webm"
            try:
                await ctx.send(file=discord.File(upfile))
            except discord.errors.HTTPException:
                await ctx.send('Looks like the file is too large, so I can\'t upload it.')
            os.remove(upfile)
        elif status == 10 or status == 11:
            await ctx.send("Looks like something wrong has occurred.\nOutput:", file=discord.File("output.txt"))
            os.remove("output.txt")

    @commands.command(aliases=["gg", "google"], pass_context = True, help='Quick box answer heckery.')
    async def search(self, ctx, *query:str):

        if not query:
            return
        else:
            query = '+'.join(query)

        await ctx.send(ggsearch.gsearch(query))

    @commands.command(aliases=["vndict", "td"], pass_context = True, help='Vietnamese dictionary heckery.')
    async def tudien(self, ctx, *query:str):

        if not query:
            return
        else:
            query = ' '.join(query)
            
        await ctx.send(vndict(query))



        
    
@bot.command(name='RemindMe', aliases=["remindme"], usage='<duration>', help='Similar to RemindMe bot on Reddit.')
async def remind_me(ctx, *, arg):
    try:
        date_time = dateparser.parse(arg, settings={"PREFER_DATES_FROM": 'future'}).timestamp()
    except Exception:
        date_time = None
        
    if date_time is None:
        try:
            date_time, result_code = cal.parse(arg)
            if result_code == 0:
                date_time = None
            else:
                date_time = datetime(*date_time[:6]).timestamp()
        except Exception:
            date_time = None
    
    if date_time is None:
        await ctx.send("Looks like I can't parse your time correctly. Try and make it as clear as possible.", delete_after = 2)
        
    elif check_past(date_time):
        await ctx.send("I can't time travel to remind you in the past. Check syntax and try again.", delete_after = 2)
        
    else:
        server = ctx.message.guild.id
        channel = ctx.message.channel.id
        message = ctx.message.id
        author = ctx.message.author.id
        insert_remind(server, channel, message, author, date_time)
        await ctx.send("Reminder created.")

if "KOYEB" in os.environ:
    keep_alive()
    

async def main():
    async with bot:
        await bot.add_cog(Fun(bot))
        await bot.add_cog(Moderation(bot))
        await bot.add_cog(Utilities(bot))
        await bot.start(TOKEN)
        
asyncio.run(main())
