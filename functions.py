from typing import Optional, Union

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import PlayerCareerStats, TeamInfoCommon, LeagueStandings
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from nba_api.stats.library.parameters import Season, LeagueID, SeasonType

#This is a constant that I don't really expect to change
DEFAULT_DISPLAY_LENGTH = 10

def getPlayerCareerStatsByID(player_id: int) -> Optional[dict]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None:
        return None

    stats_dict = {}

    common_info = CommonPlayerInfo(player_id=static_info.get('id')).get_normalized_dict() \
        .get('CommonPlayerInfo')[0]
    career_stats = PlayerCareerStats(player_id=static_info.get('id')).get_normalized_dict() \
        .get('CareerTotalsRegularSeason')[0]

    stats_dict['FROM_YEAR'] = common_info.get('FROM_YEAR')
    stats_dict['TO_YEAR'] = common_info.get('TO_YEAR')
    stats_dict['TEAM_CITY'] = common_info.get('TEAM_CITY')
    stats_dict['TEAM_NAME'] = common_info.get('TEAM_NAME')
    stats_dict['JERSEY'] = common_info.get('JERSEY')
    stats_dict['POSITION'] = common_info.get('POSITION')
    stats_dict['HEIGHT'] = common_info.get('HEIGHT')
    stats_dict['WEIGHT'] = common_info.get('WEIGHT')
    stats_dict['PTS'] = career_stats.get('PTS')
    stats_dict['AST'] = career_stats.get('AST')
    stats_dict['BLK'] = career_stats.get('BLK')
    stats_dict['STL'] = career_stats.get('STL')
    stats_dict['REB'] = career_stats.get('REB')
    stats_dict['OREB'] = career_stats.get('OREB')
    stats_dict['DREB'] = career_stats.get('DREB')

    return stats_dict

def getPlayerCareerString(player_id: int) -> Optional[str]:
    static_info = players.find_player_by_id(player_id)

    #If that id doesn't return a player, return None
    if static_info is None:
        return None

    ret_str = f"**Player {str(static_info.get('id'))}: {static_info.get('full_name')}**"

    ret_str += "\n\tStatus: "
    if static_info.get('is_active'):
        ret_str += "Active"
    else:
        ret_str += "Inactive"

    # get the rest of the data from the NBA api endpoint
    # might want to change this to DataFrame if we need it for graphing later
    all_info = getPlayerCareerStatsByID(player_id)

    ret_str += f" ({all_info.get('FROM_YEAR')}-{all_info.get('TO_YEAR')})"

    ret_str += f"\n\t{all_info.get('TEAM_CITY')} {all_info.get('TEAM_NAME')} #{all_info.get('JERSEY')}: {all_info.get('POSITION')}"

    #split the height into separate feet and inches for formatting
    height = all_info.get('HEIGHT').split('-')
    ret_str += f"\n\tHeight: {height[0]}\'{height[1]}\", Weight: {all_info.get('WEIGHT')} lbs"

    #career stats
    ret_str += "\n\n\t*Career Stats (Regular Season):*"
    ret_str += f"\n\tPoints: {all_info.get('PTS')}"
    ret_str += f"\n\tAssists: {all_info.get('AST')}"
    ret_str += f"\n\tBlocks: {all_info.get('BLK')}"
    ret_str += f"\n\tSteals: {all_info.get('STL')}"
    ret_str += f"\n\tRebounds: {all_info.get('REB')}"
    ret_str += f"\n\t   Offensive: {all_info.get('OREB')}"
    ret_str += f"\n\t   Defensive: {all_info.get('DREB')}"

    return ret_str

def getPlayerStatsByName(player_name: str) -> str:
    all_matches = players.find_players_by_full_name(player_name)

    if len(all_matches) < 1:
        return f"No matches found for \"{player_name}\""

    elif len(all_matches) > 1:
        ret_str = "The following players matched the search:"
        for player in all_matches:
            ret_str += "\n" + player.get('full_name')

        ret_str += "\n\nPlease try again with one of the above names"

        return ret_str

    else:
        return getPlayerStatsString(all_matches[0].get('id'))

def getPlayerHeadshotURL(player_id: int) -> Optional[str]:
    return f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{str(player_id)}.png"

def getPlayerHeadshotURLByName(player_name: str) -> Optional[str]:
    all_matches = players.find_players_by_full_name(player_name)
    if not len(all_matches) == 1:
        return None
    else:
        return getPlayerHeadshotURL(all_matches[0].get('id'))


def getTeamStatsString(team_id: int) -> Optional[str]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None:
        return None

    ret_str = f"**{static_info.get('full_name')} ({static_info.get('year_founded')})**"

    common_info = TeamInfoCommon(team_id = team_id).get_normalized_dict().get('TeamInfoCommon')[0]

    ret_str += f"\n\t{common_info.get('TEAM_CONFERENCE')} Conference Rank: {common_info.get('CONF_RANK')}"
    ret_str += f"\n\t{common_info.get('TEAM_DIVISION')} Division Rank: {common_info.get('DIV_RANK')}"
    ret_str += f"\n\tWins: {common_info.get('W')}, Losses: {common_info.get('L')}"
    ret_str += f"\n\tPCT: {common_info.get('PCT')}"

    return ret_str

def getTeamStatsByName(team_name: str) -> Optional[str]:
    all_matches = teams.find_teams_by_full_name(team_name)

    if len(all_matches) < 1:
        return f"No matches found for \"{team_name}\""

    elif len(all_matches) > 1:
        ret_str = "The following teams matched the search:"
        for team in all_matches:
            ret_str += "\n" + team.get('full_name')

        ret_str += "\n\nPlease try again with one of the above names"

        return ret_str

    else:
        return getTeamStatsString(all_matches[0].get('id'))
