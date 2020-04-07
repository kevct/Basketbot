# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 2020
@author: Samuel, Kevin, Christopher
"""
import discord
import os
import discord.ext.commands as commands
import functions as nba
import proxied_endpoint
import logging

TOKEN = open("token.txt", 'r').read()
LOGGER = logging.getLogger(__name__)

bot = commands.Bot(command_prefix='%')

@bot.command()
async def playercareerstats(ctx, *args):
    """[full or partial name] Displays a player's career statistics"""
    
    name = ""
    for x in args:
        name = name + " " + x
    
    embed = discord.Embed(title="Player Not Found", description="Double check that the player name is spelled correctly.", color = 0x595959)
    players = nba.getPlayerIdsByName(name.strip())
    if not players == None: #If the list of players is not empty
        playerIds = list(players.keys())
        playerNames = list(players.values())
        if len(playerIds) > 1:#If there are multiple players with the same name then list out all the players
            embed = discord.Embed(title="Multiple Players", description="There are multiple players with the name \"" + name.strip() + "\":", color = 0x595959)
            if len(playerIds) > 12: #If there are more than 12 players with the name specified
                for i in range (0, 12):
                    embed.add_field(name="\u200b", value=playerNames[i], inline=True)
                embed.add_field(name="\u200b", value="... and more", inline=True)
            else:
                for i in playerNames:
                    embed.add_field(name="\u200b", value=i, inline=True)
        else: #List the player's stats
            stats = nba.getPlayerCareerStatsByID(playerIds[0])
            height = stats["HEIGHT"].split("-")
            embed = discord.Embed(title=playerNames[0], description= stats["TEAM_CITY"] + " " + stats["TEAM_NAME"] + " | #" + stats["JERSEY"] + " | "  
                + stats["POSITION"] + "\n" + height[0] + "'" + height[1] + "\"" + " | " + stats["WEIGHT"] + " lbs" + " | " + str(stats["FROM_YEAR"]) + " - " + str(stats["TO_YEAR"]), color = stats["TEAM_COLOR"])
            embed.set_thumbnail(url=nba.getPlayerHeadshotURL(playerIds[0]))
            embed.add_field(name="Career Points", value=stats["PTS"], inline=False)
            embed.add_field(name="Career Rebounds", value=stats["REB"], inline=False)
            embed.add_field(name="Career Assists", value=stats["AST"], inline=False)
            embed.add_field(name="Career Blocks", value=stats["BLK"], inline=False)
            embed.add_field(name="Career Steals", value=stats["STL"], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def player(ctx, *args):
    """[full or partial name] Displays a active player's current season statistics"""
    name = ""
    for x in args:
        name = name + " " + x
        
    embed = discord.Embed(title="Player Not Found", description="Double check that the player name is spelled correctly, or try using %playercareerstats [player].", color = 0x595959)
    players = nba.getPlayerIdsByName(name.strip(), True, True)
    if not players == None: #If the list of players is not empty
        playerIds = list(players.keys())
        playerNames = list(players.values())
        if len(playerIds) > 1:#If there are multiple players with the same name then list out all the players
            embed = discord.Embed(title="Multiple Players", description="There are multiple players with the name \"" + name.strip() + "\":", color = 0x595959)
            if len(playerIds) > 12: #If there are more than 12 players with the name specified
                for i in range (0, 12):
                    embed.add_field(name="\u200b", value=playerNames[i], inline=True)
                embed.add_field(name="\u200b", value="... and more", inline=True)
            else:
                for i in playerNames:
                    embed.add_field(name="\u200b", value=i, inline=True)
        else: #List the player's stats
            stats = nba.getPlayerSeasonStatsByID(playerIds[0])
            height = stats["HEIGHT"].split("-")
            embed = discord.Embed(title=playerNames[0] + " | " + stats["SEASON_ID"], description= stats["TEAM_CITY"] + " " + stats["TEAM_NAME"] + " | #" + stats["JERSEY"] + " | "  
                + stats["POSITION"] + "\n" + height[0] + "'" + height[1] + "\"" + " | " + stats["WEIGHT"] + " lbs", color = stats["TEAM_COLOR"])
            embed.set_thumbnail(url=nba.getPlayerHeadshotURL(playerIds[0]))
            embed.add_field(name="Games Played", value=stats["GP"], inline=True)
            embed.add_field(name="Games Started", value=stats["GS"], inline=True)
            embed.add_field(name="Points", value=str(stats["PTS"]) + " (" + str(stats["PPG"]) + " PPG)", inline=False)
            embed.add_field(name="Rebounds", value=str(stats["REB"]) + " (" + str(stats["RPG"]) + " RPG)", inline=False)
            embed.add_field(name="Assists", value=str(stats["AST"]) + " (" + str(stats["APG"]) + " APG)", inline=False)
            embed.add_field(name="Blocks", value=str(stats["BLK"]) + " (" + str(stats["BPG"]) + " BPG)", inline=False)
            embed.add_field(name="Steals", value=str(stats["STL"]) + " (" + str(stats["SPG"]) + " SPG)", inline=False)
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

# Enable logging
logging.basicConfig()

# Uncomment the following line for proxy debug messages
# logging.getLogger(proxied_endpoint.__name__).setLevel(logging.DEBUG)

# If we can't connect to NBA servers, no reason to start the bot until we're sure we can
if not proxied_endpoint.is_direct_connect_allowed():
    LOGGER.info("Direct connection to NBA blocked, looking for available proxies")
    proxied_endpoint.populate_good_proxies(min_good_proxies=1, load_from_file=True)

LOGGER.info("Starting bot")
bot.run(TOKEN)
