from typing import Optional, Dict, Any

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import PlayerCareerStats, TeamInfoCommon, CommonPlayerInfo, TeamYearByYearStats
from nba_api.stats.library.parameters import Season
from proxied_endpoint import ProxiedEndpoint
import fuzzyids

teamClrs = {
    1610612737: 0xE03A3E, #Atlanta Hawks
    1610612738: 0x007A33, #Boston Celtics
    1610612739: 0x860038, #Cleveland Cavaliers
    1610612740: 0x0C2340, #New Orleans Pelicans
    1610612741: 0xCE1141, #Chicago Bulls
    1610612742: 0x00538C, #Dallas Mavericks
    1610612743: 0x0E2240, #Denver Nuggets
    1610612744: 0x006BB6, #Golden State Warriors
    1610612745: 0xCE1141, #Houston Rockets
    1610612746: 0x1D428A, #Los Angeles Clippers
    1610612747: 0xFDB927, #Los Angeles Lakers
    1610612748: 0x98002E, #Miami Heat
    1610612749: 0x00471B, #Milawukee Bucks
    1610612750: 0x0C2340, #Minnesota Timberwolves
    1610612751: 0x000000, #Brooklyn Nets
    1610612752: 0xF58426, #New York Knicks
    1610612753: 0x0077C0, #Orlando Magic
    1610612754: 0xFDBB30, #Indiana Pacers
    1610612755: 0x006BB6, #Philidelphia 76ers
    1610612756: 0xE56020, #Phoenix Suns
    1610612757: 0xE03A3E, #Portland Trail Blazers
    1610612758: 0x5A2D81, #Sacramento Kings
    1610612759: 0xC4CED4, #San Antonio Spurs
    1610612760: 0x007AC1, #Oklahoma City Thunder
    1610612761: 0xCE1141, #Toronto Raptors
    1610612762: 0xF9A01B, #Utah Jazz
    1610612763: 0x5D76A9, #Memphis Grizzlies
    1610612764: 0x002B5C, #Washington Wizards
    1610612765: 0xC8102E, #Detroit Pistons
    1610612766: 0x00788C  #Charlotte Hornets
}

async def getPlayerSeasonStatsByID(player_id: int, season_id: str = Season.current_season, use_proxy = None) -> Optional[dict]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
        return None

    all_seasons_response = await ProxiedEndpoint(PlayerCareerStats, player_id=static_info.get('id'), use_proxy=use_proxy)

    all_seasons = all_seasons_response.get_normalized_dict().get('SeasonTotalsRegularSeason')

    target_season = None

    for season in all_seasons:
        if season.get('SEASON_ID') == season_id:
            target_season = season
            break

    if target_season is None:
        return None

    else:

        common_info_response = await ProxiedEndpoint(CommonPlayerInfo, player_id=static_info.get('id'), use_proxy=use_proxy)

        common_info = common_info_response.get_normalized_dict().get('CommonPlayerInfo')[0]

        stats_dict = {}

        stats_dict['FROM_YEAR'] = common_info.get('FROM_YEAR')
        stats_dict['TO_YEAR'] = common_info.get('TO_YEAR')
        stats_dict['TEAM_COLOR'] = getTeamColor(common_info.get('TEAM_ID'))
        stats_dict['TEAM_CITY'] = common_info.get('TEAM_CITY')
        stats_dict['TEAM_NAME'] = common_info.get('TEAM_NAME')
        stats_dict['JERSEY'] = common_info.get('JERSEY')
        stats_dict['POSITION'] = common_info.get('POSITION')
        stats_dict['HEIGHT'] = common_info.get('HEIGHT')
        stats_dict['WEIGHT'] = common_info.get('WEIGHT')

        stats_dict['SEASON_ID'] = target_season.get('SEASON_ID')
        stats_dict['GP'] = target_season.get('GP')
        stats_dict['GS'] = target_season.get('GS')
        stats_dict['MIN'] = target_season.get('MIN')
        stats_dict['PTS'] = target_season.get('PTS')
        stats_dict['AST'] = target_season.get('AST')
        stats_dict['BLK'] = target_season.get('BLK')
        stats_dict['STL'] = target_season.get('STL')
        stats_dict['REB'] = target_season.get('REB')
        stats_dict['OREB'] = target_season.get('OREB')
        stats_dict['DREB'] = target_season.get('DREB')
        stats_dict['PPG'] = round(target_season.get('PTS') / target_season.get('GP'), 1)
        stats_dict['RPG'] = round(target_season.get('REB') / target_season.get('GP'), 1)
        stats_dict['APG'] = round(target_season.get('AST') / target_season.get('GP'), 1)
        stats_dict['BPG'] = round(target_season.get('BLK') / target_season.get('GP'), 1)
        stats_dict['SPG'] = round(target_season.get('STL') / target_season.get('GP'), 1)

        return stats_dict

async def getPlayerCareerStatsByID(player_id: int, use_proxy: Optional[bool] = None) -> Optional[dict]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
        return None

    stats_dict = {}

    common_info_response = await ProxiedEndpoint(CommonPlayerInfo, player_id=static_info.get('id'), use_proxy=use_proxy)
    career_stats_response = await ProxiedEndpoint(PlayerCareerStats, player_id=static_info.get('id'), use_proxy=use_proxy)

    common_info = common_info_response.get_normalized_dict().get('CommonPlayerInfo')[0]
    career_stats = career_stats_response.get_normalized_dict().get('CareerTotalsRegularSeason')[0]

    stats_dict['FROM_YEAR'] = common_info.get('FROM_YEAR')
    stats_dict['TO_YEAR'] = common_info.get('TO_YEAR')
    stats_dict['TEAM_COLOR'] = getTeamColor(common_info.get('TEAM_ID'))
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
    all_info = await getPlayerCareerStatsByID(player_id)

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

async def getPlayerIdsByName(player_name: str, #Only required argument
                       only_active: bool = False, fuzzy_match: bool = False) \
                        -> Optional[Dict[int, str]]:
    """
    Function that takes a player name and returns a dictionary of matching names indexed by id
    NOTE: any optional parameters set to True WILL make the function slower
    :param player_name: str to search for
    :param only_active: optional param to only return active players
    :param fuzzy_match: optional param to use fuzzy matching if more or less than one result is returned
    :return:
    """

    stripped_name = player_name.strip()

    if stripped_name == "":
        return None

    all_matches = players.find_players_by_full_name(stripped_name)
    ret_dict = {}

    if all_matches is None or len(all_matches) < 1:
        if fuzzy_match:
            return fuzzyids.getFuzzyPlayerIdsByName(stripped_name, only_active=only_active)
        else:
            return None

    elif only_active:
        for match in all_matches:
            if match.get('is_active'):
                ret_dict[match.get('id')] = match.get('full_name')

    else:
        for match in all_matches:
            ret_dict[match.get('id')] = match.get('full_name')

    if fuzzy_match and len(ret_dict) > 1:
        return fuzzyids.getFuzzyPlayerIdsByName(stripped_name, only_active=only_active)
    else:
        return ret_dict

async def getActivePlayerIdsByName(player_name: str, fuzzy_match = False) -> Optional[Dict[int, str]]:
    """
    Takes a string and returns all the active names and IDs matching the string
    :param player_name: name of the player to search for
    :param fuzzy_match: whether or not to enable fuzzy matching if more or less than one match is returned
    :return: a dictionary keyed by player id and with value player's full name
    """
    return await getPlayerIdsByName(player_name, only_active=True, fuzzy_match=fuzzy_match)

def getPlayerHeadshotURL(player_id: int) -> Optional[str]:
    static_info = players.find_player_by_id(player_id)

    if static_info is None or len(static_info) < 1:
        return None

    return f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{str(player_id)}.png"

def getTeamLogoURL(team_id: int) -> Optional[str]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None or len(static_info) < 1:
        return None

    teamThreeLetter = (TeamInfoCommon(team_id = team_id, season_nullable=Season.current_season).get_normalized_dict().get('TeamInfoCommon')[0]).get("TEAM_ABBREVIATION").lower()
    return f"https://a.espncdn.com/i/teamlogos/nba/500/{teamThreeLetter}.png"
    #Discord does not support .svg file extensions
    #return f"https://www.nba.com/assets/logos/teams/primary/web/{teamThreeLetter}.svg"

async def getTeamCareerStatsByID(team_id: int, use_proxy: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None or len(static_info) < 1:
        return None

    stats_dict = {}

    all_seasons_response = await ProxiedEndpoint(TeamYearByYearStats, team_id = team_id, use_proxy=use_proxy)

    all_seasons = all_seasons_response.get_normalized_dict().get('TeamStats')

    stats_dict['W'] = 0
    stats_dict['L'] = 0
    stats_dict['PCT'] = 0
    stats_dict['MAX_CONF_RANK'] = all_seasons[0].get('CONF_RANK')
    stats_dict['MIN_CONF_RANK'] = all_seasons[0].get('CONF_RANK')
    stats_dict['MAX_DIV_RANK'] = all_seasons[0].get('DIV_RANK')
    stats_dict['MIN_DIV_RANK'] = all_seasons[0].get('DIV_RANK')
    # Add up all the stats for all seasons
    for season in all_seasons:
        stats_dict['W'] += season.get('WINS')
        stats_dict['L'] += season.get('LOSSES')

        if stats_dict['MAX_CONF_RANK'] > season.get('CONF_RANK') or stats_dict['MAX_CONF_RANK'] < 1:
            stats_dict['MAX_CONF_RANK'] = season.get('CONF_RANK')

        elif stats_dict['MIN_CONF_RANK'] < season.get('CONF_RANK'):
            stats_dict['MIN_CONF_RANK'] = season.get('CONF_RANK')

        if stats_dict['MAX_DIV_RANK'] > season.get('DIV_RANK'):
            stats_dict['MAX_DIV_RANK'] = season.get('DIV_RANK')

        elif stats_dict['MIN_DIV_RANK'] < season.get('DIV_RANK'):
            stats_dict['MIN_DIV_RANK'] = season.get('DIV_RANK')

    stats_dict['PCT'] = (stats_dict['W'] + stats_dict['L']) / float(stats_dict['W'])

    return stats_dict

async def getTeamSeasonStatsByID(team_id: int, season_id: str = Season.current_season, use_proxy: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    static_info = teams.find_team_name_by_id(team_id)

    if static_info is None or len(static_info) < 1:
        return None

    stats_dict = {}

    season_info_response = await ProxiedEndpoint(TeamInfoCommon, team_id = team_id, season_nullable=season_id, use_proxy=use_proxy)
    season_stats_response =  await ProxiedEndpoint(TeamInfoCommon(team_id = team_id, season_nullable=season_id))

    season_info = season_info_response.get_normalized_dict().get('TeamInfoCommon')[0]
    season_stats = season_stats_response.get_normalized_dict().get('TeamSeasonRanks')[0]

    stats_dict['TEAM_CONFERENCE'] = season_info.get('TEAM_CONFERENCE')
    stats_dict['CONF_RANK'] = season_info.get('CONF_RANK')
    stats_dict['TEAM_DIVISION'] = season_info.get('TEAM_DIVISION')
    stats_dict['DIV_RANK'] = season_info.get('DIV_RANK')
    stats_dict['W'] = season_info.get('W')
    stats_dict['L'] = season_info.get('L')
    stats_dict['PCT'] = season_info.get('PCT')
    stats_dict['TEAM_COLOR'] = getTeamColor(team_id)
    stats_dict['SEASON_ID'] = season_id
    stats_dict['PPG'] = season_stats['PTS_PG']
    stats_dict['PTS_RANK'] = season_stats['PTS_RANK']
    stats_dict['RPG'] = season_stats['REB_PG']
    stats_dict['REB_RANK'] = season_stats['REB_RANK']
    stats_dict['APG'] = season_stats['AST_PG']
    stats_dict['AST_RANK'] = season_stats['AST_RANK']
    stats_dict['OPPG'] = season_stats['OPP_PTS_PG']
    stats_dict['OPPG_RANK'] = season_stats['OPP_PTS_RANK']

    return stats_dict

async def getTeamIdsByName(team_name: str, fuzzy_match: bool = False) -> Optional[Dict[int, str]]:
    """
    Takes a string name and returns a list of all the teams and ids that match that string
    :param team_name:
    :return:
    """

    stripped_name = team_name.strip()

    if stripped_name == "":
        return None

    all_matches = teams.find_teams_by_full_name(stripped_name)
    ret_dict = {}

    if all_matches is None or len(all_matches) < 1:
        if fuzzy_match:
            return fuzzyids.getFuzzyTeamIdsByName(stripped_name)
        else:
            return None

    else:
        for match in all_matches:
            ret_dict[match.get('id')] = match.get('full_name')

    if fuzzy_match and len(ret_dict) > 1:
        return fuzzyids.getFuzzyPlayerIdsByName(stripped_name)
    else:
        return ret_dict

def getTeamColor(team_code: int) -> int:
    if team_code in teamClrs:
        return teamClrs[team_code]
    return 0xFFFFFE