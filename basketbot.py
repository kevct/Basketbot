# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 2020
@author: Samuel, Kevin, Christopher
"""
import discord
import os
import discord.ext.commands as commands
import random
from regex_parsing import parse_discord_message

TOKEN = ""

bot = commands.Bot(command_prefix='-')

@bot.command()
async def command(ctx):
    """Put what command does here"""

@bot.event
async def on_message(message):
    """Do something when a message is sent"""

@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send("Invalid command. See -help for commands.")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(""))
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

bot.run(TOKEN)
