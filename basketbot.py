# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 2020
@author: Samuel, Kevin, Christopher
"""
import discord
import os
import discord.ext.commands as commands
import functions as nba

TOKEN = open("token.txt", 'r').read()

bot = commands.Bot(command_prefix='%')

@bot.command()
async def playercareerstats(ctx, *args):
    """[full or partial name] Displays a player's career statistics"""
    name = ""
    for x in args:
        name = name + " " + x
    
    embed = discord.Embed(title="test", description="test", color = 0x595959)
    players = nba.getPlayerIdsByName(name.strip())
    if not players == None: #If the list of players is not empty
        if len(players) > 1:#If there are multiple players with the same name then list out all the players
            embed = discord.Embed(title="Multiple Players", description="There are multiple players with the name \"" + name.strip() + "\":", color = 0x595959)
            if len(players) > 12: #If there are more than 12 players with the name specified
                for i in range (0, 12):
                    embed.add_field(name="\u200b", value=players[i][1], inline=True)
                embed.add_field(name="\u200b", value="... and more", inline=True)
            else:
                for i in players:
                    embed.add_field(name="\u200b", value=i[1], inline=True)
        else: #List the player's stats
            stats = nba.getPlayerCareerStatsByID(players[0][0])
            height = stats["HEIGHT"].split("-")
            embed = discord.Embed(title=players[0][1], description= stats["TEAM_CITY"] + " " + stats["TEAM_NAME"] + " | #" + stats["JERSEY"] + " | "  
                + stats["POSITION"] + "\n" + height[0] + "'" + height[1] + "\"" + " | " + stats["WEIGHT"] + " lbs" + " | " + str(stats["FROM_YEAR"]) + " - " + str(stats["TO_YEAR"]), color = nba.getTeamColor(stats["TEAM_ID"]))
            embed.set_thumbnail(url=nba.getPlayerHeadshotURL(players[0][0]))
            embed.add_field(name="Career Points", value=stats["PTS"], inline=False)
            embed.add_field(name="Career Rebounds", value=stats["REB"], inline=False)
            embed.add_field(name="Career Assists", value=stats["AST"], inline=False)
            embed.add_field(name="Career Blocks", value=stats["BLK"], inline=False)
            embed.add_field(name="Career Steals", value=stats["STL"], inline=False)
    else:
        embed = discord.Embed(title="Player Not Found", description="Double check that the player name is spelled correctly.", color = 0x595959)
    await ctx.send(embed=embed)
    
@bot.event
async def on_message(message):
    """Do something when a message is sent"""
    if not message.author == bot.user:
        pass
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    print(error)
    embed = discord.Embed(title="Invalid Command", description="See %help for commands.", color = 0x595959)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

bot.run(TOKEN)
