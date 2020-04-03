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
    """Displays a player's career statistics"""
    
    name = ""
    for x in args:
        name = name + " " + x
    
    embed = discord.Embed(title="Player Not Found", description="Double check that the player name is spelled correctly.", color = 0x595959)
    players = nba.getPlayerIdsByName(name.strip(), False, True)
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
            embed.add_field(name="Career Points", value="**" + str(stats["PTS"]) + "**", inline=False)
            embed.add_field(name="Career Rebounds", value="**" + str(stats["REB"]) + "**", inline=False)
            embed.add_field(name="Career Assists", value="**" + str(stats["AST"]) + "**", inline=False)
            embed.add_field(name="Career Blocks", value="**" + str(stats["BLK"]) + "**", inline=False)
            embed.add_field(name="Career Steals", value="**" + str(stats["STL"]) + "**", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def player(ctx, *args):
    """Displays a active player's current season statistics"""
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
            embed = discord.Embed(title=playerNames[0], description=stats["SEASON_ID"] + "\n" +  stats["TEAM_CITY"] + " " + stats["TEAM_NAME"] + " | #" + stats["JERSEY"] + " | "  
                + stats["POSITION"] + "\n" + height[0] + "'" + height[1] + "\"" + " | " + stats["WEIGHT"] + " lbs", color = stats["TEAM_COLOR"])
            embed.set_thumbnail(url=nba.getPlayerHeadshotURL(playerIds[0]))
            embed.add_field(name="Games Played", value="**" + str(stats["GP"]) + "**", inline=True)
            embed.add_field(name="Games Started", value="**" + str(stats["GS"]) + "**", inline=True)
            embed.add_field(name="Points", value="**" + str(stats["PTS"]) + "** (" + str(stats["PPG"]) + " PPG)", inline=False)
            embed.add_field(name="Rebounds", value="**" + str(stats["REB"]) + "** (" + str(stats["RPG"]) + " RPG)", inline=False)
            embed.add_field(name="Assists", value="**" + str(stats["AST"]) + "** (" + str(stats["APG"]) + " APG)", inline=False)
            embed.add_field(name="Blocks", value="**" + str(stats["BLK"]) + "** (" + str(stats["BPG"]) + " BPG)", inline=False)
            embed.add_field(name="Steals", value="**" + str(stats["STL"]) + "** (" + str(stats["SPG"]) + " SPG)", inline=False)
    await ctx.send(embed=embed)    
 
@bot.command()
async def team(ctx, *args):
    """Displays a team's current season statistics"""
    name = ""
    for x in args:
        name = name + " " + x
    
    embed = discord.Embed(title="Team Not Found", description="Double check that the team name is spelled correctly.", color = 0x595959)
    teams = nba.getTeamIdsByName(name)
    if not teams == None:
        teamIds = list(teams.keys())
        teamNames = list(teams.values())
        if len(teamIds) > 1: #If there are multiple teams with the same name
            embed = discord.Embed(title="Multiple Teams", description="There are multiple teams with the name \"" + name.strip() + "\":", color = 0x595959)
            if len(teamIds) > 30: #If there are more than 30 teams with the name specified
                for i in range (0, 30):
                    embed.add_field(name="\u200b", value=teamNames[i], inline=True)
                embed.add_field(name="\u200b", value="... and more", inline=True)
            else: #List the teams
                for i in teamNames:
                    embed.add_field(name="\u200b", value=i, inline=True)
        else: #List the team's stats
            stats = nba.getTeamSeasonStatsByID(teamIds[0])
            embed = discord.Embed(title=teamNames[0], description=stats["SEASON_ID"] + "\n" + make_ordinal(stats["CONF_RANK"]) + " in " + stats["TEAM_CONFERENCE"] 
                + " | " + make_ordinal(stats["DIV_RANK"]) + " in " + stats["TEAM_DIVISION"]+ "\n", color = stats["TEAM_COLOR"])
            embed.set_thumbnail(url=nba.getTeamLogoURL(teamIds[0]))
            embed.add_field(name="Points Per Game", value="**" + str(stats["PPG"]) + "** (" + make_ordinal(stats["PTS_RANK"]) + " in the league)", inline=False)
            embed.add_field(name="Rebounds Per Game", value="**" + str(stats["RPG"]) + "** (" + make_ordinal(stats["REB_RANK"]) + " in the league)", inline=False)
            embed.add_field(name="Assists Per Game", value="**" + str(stats["APG"]) + "** (" + make_ordinal(stats["AST_RANK"]) + " in the league)", inline=False)
            embed.add_field(name="Opponent Points Per Game", value="**" + str(stats["OPPG"]) + "** (" + make_ordinal(stats["OPPG_RANK"]) + " in the league)", inline=False)
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

"""Credit to https://stackoverflow.com/users/857390/florian-brucker for this function"""
def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

bot.run(TOKEN)
