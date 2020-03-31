from typing import Optional

from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerCareerStats
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo

def getPlayerStatsString(player_id: int) -> Optional[str]:
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
    common_info = CommonPlayerInfo(player_id=static_info.get('id')).get_normalized_dict() \
        .get('CommonPlayerInfo')[0]
    career_stats = PlayerCareerStats(player_id=static_info.get('id')).get_normalized_dict() \
        .get('CareerTotalsRegularSeason')[0]

    ret_str += f" ({common_info.get('FROM_YEAR')}-{common_info.get('TO_YEAR')})"

    ret_str += f"\n\t{common_info.get('TEAM_CITY')} {common_info.get('TEAM_NAME')} #{common_info.get('JERSEY')}: {common_info.get('POSITION')}"

    #split the height into separate feet and inches for formatting
    height = common_info.get('HEIGHT').split('-')
    ret_str += f"\n\tHeight: {height[0]}\'{height[1]}\", Weight: {common_info.get('WEIGHT')} lbs"

    #career stats
    ret_str += "\n\n\t*Career Stats (Regular Season):*"
    ret_str += f"\n\tPoints: {career_stats.get('PTS')}"
    ret_str += f"\n\tAssists: {career_stats.get('AST')}"
    ret_str += f"\n\tBlocks: {career_stats.get('BLK')}"
    ret_str += f"\n\tSteals: {career_stats.get('STL')}"
    ret_str += f"\n\tRebounds: {career_stats.get('REB')}"
    ret_str += f"\n\t   Offensive: {career_stats.get('OREB')}"
    ret_str += f"\n\t   Defensive: {career_stats.get('DREB')}"

    return ret_str

def getPlayerStatsByName(player_name: str) -> str:
    all_matches = players.find_players_by_full_name(player_name)

    if len(all_matches) < 1:
        return "No matches found"

    elif len(all_matches) > 1:
        ret_str = "The following players matched the search:"
        for player in all_matches:
            ret_str += "\n" + player.get('full_name')

        ret_str += "\n\nPlease try again with one of the above names"

        return ret_str

    else:
        return getPlayerStatsString(all_matches[0].get('id'))