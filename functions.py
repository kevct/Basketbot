from typing import Optional, Union, List, Dict, Any

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import PlayerCareerStats, TeamInfoCommon, LeagueStandings
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from nba_api.stats.endpoints.teamyearbyyearstats import TeamYearByYearStats
from nba_api.stats.library.parameters import Season, LeagueID, SeasonType, SeasonAll

#This is a constant that I don't really expect to change
DEFAULT_DISPLAY_LENGTH = 10

def getPlayerSeasonStatsByID(player_id: int, season_id: str = Season.current_season) -> Optional[dict]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
        return None

    all_seasons = PlayerCareerStats(player_id=static_info.get('id')).get_normalized_dict().get('SeasonTotalsRegularSeason')

    target_season = None

    for season in all_seasons:
        if season.get('SEASON_ID') == season_id:
            target_season = season
            break

    if target_season is None:
        return None

    else:
        stats_dict = {}

        stats_dict['PTS'] = target_season.get('PTS')
        stats_dict['AST'] = target_season.get('AST')
        stats_dict['BLK'] = target_season.get('BLK')
        stats_dict['STL'] = target_season.get('STL')
        stats_dict['REB'] = target_season.get('REB')
        stats_dict['OREB'] = target_season.get('OREB')
        stats_dict['DREB'] = target_season.get('DREB')

        return stats_dict

def getPlayerCareerStatsByID(player_id: int) -> Optional[dict]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
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
    if static_info is None or len(static_info) < 1:
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

def getPlayerIdsByName(player_name: str) -> Optional[List[List]]:
    """
    Takes a string and returns all the names and IDs matching the string
    :param player_name: name of the player to search for
    :return: returns None if no matches found, returns an array of matching ids and their names otherwise
    """

    all_matches = players.find_players_by_full_name(player_name)
    ret_list = []

    if len(all_matches) < 1:
        return None
    else:
        for match in all_matches:
            ret_list.append([match.get('id'), match.get('full_name')])

    return ret_list

def getPlayerHeadshotURL(player_id: int) -> Optional[str]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
        return None

    return f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{str(player_id)}.png"

def getTeamCareerStatsByID(team_id: int) -> Optional[str]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None or len(static_info) < 1:
        return None

    stats_dict = {}

    all_seasons = TeamYearByYearStats(team_id = team_id).get_normalized_dict().get('TeamStats')
    stats_dict['W'] = 0
    stats_dict['L'] = 0
    stats_dict['PCT'] = 0
    stats_dict['MAX_CONF_RANK'] = all_seasons[0].get('CONF_RANK')
    print(f"initial max rank set to {stats_dict['MAX_CONF_RANK']}")
    stats_dict['MIN_CONF_RANK'] = all_seasons[0].get('CONF_RANK')
    stats_dict['MAX_DIV_RANK'] = all_seasons[0].get('DIV_RANK')
    stats_dict['MIN_DIV_RANK'] = all_seasons[0].get('DIV_RANK')
    # Add up all the stats for all seasons
    for season in all_seasons:
        stats_dict['W'] += season.get('WINS')
        stats_dict['L'] += season.get('LOSSES')

        if stats_dict['MAX_CONF_RANK'] > season.get('CONF_RANK') or stats_dict['MAX_CONF_RANK'] < 1:
            print(f"replaced max rank {stats_dict['MAX_CONF_RANK']} with {season.get('CONF_RANK')}")
            stats_dict['MAX_CONF_RANK'] = season.get('CONF_RANK')

        elif stats_dict['MIN_CONF_RANK'] < season.get('CONF_RANK'):
            stats_dict['MIN_CONF_RANK'] = season.get('CONF_RANK')

        if stats_dict['MAX_DIV_RANK'] > season.get('DIV_RANK'):
            stats_dict['MAX_DIV_RANK'] = season.get('DIV_RANK')

        elif stats_dict['MIN_DIV_RANK'] < season.get('DIV_RANK'):
            stats_dict['MIN_DIV_RANK'] = season.get('DIV_RANK')

    stats_dict['PCT'] = (stats_dict['W'] + stats_dict['L']) / float(stats_dict['W'])

    return stats_dict

def getTeamSeasonStatsByID(team_id: int, season_id: str = Season.current_season) -> Optional[Dict[str, Any]]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None or len(static_info) < 1:
        return None

    stats_dict = {}

    season_info = TeamInfoCommon(team_id = team_id, season_nullable=season_id).get_normalized_dict().get('TeamInfoCommon')[0]

    stats_dict['TEAM_CONFERENCE'] = season_info.get('TEAM_CONFERENCE')
    stats_dict['CONF_RANK'] = season_info.get('CONF_RANK')
    stats_dict['TEAM_DIVISION'] = season_info.get('TEAM_DIVISION')
    stats_dict['DIV_RANK'] = season_info.get('DIV_RANK')
    stats_dict['W'] = season_info.get('W')
    stats_dict['L'] = season_info.get('L')
    stats_dict['PCT'] = season_info.get('PCT')

    return stats_dict

def getTeamIdsByName(team_name: str) -> Optional[List[List]]:
    """
    Takes a string name and returns a list of all the teams and ids that match that string
    :param team_name:
    :return:
    """
    all_matches = teams.find_teams_by_full_name(team_name)
    ret_list = []

    if len(all_matches) < 1:
        return None

    else:
        for match in all_matches:
            ret_list.append([match.get('id'), match.get('full_name')])

    return ret_list