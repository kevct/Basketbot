from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo

def getPlayerStatsString(player_name: str) -> str:
    players_info = players.find_players_by_full_name(player_name)

    if len(players_info) < 1:
        return "No players found"

    elif len(players_info) > 1:
        ret_str = "The following players matched the search:"
        for player_info in players_info:
            ret_str += "\n" + player_info.get('full_name')

        ret_str += "\n\nPlease try again with one of the above names"

    else:
        ret_str = f"Player {str(players_info[0].get('id'))}: {players_info[0].get('full_name')}"

        ret_str += "\n\tStatus: "
        if players_info[0].get('is_active'):
            ret_str += "Active"
        else:
            ret_str += "Inactive"

        # get the rest of the data from the NBA api endpoint
        # might want to change this to DataFrame if we need it for graphing later
        ept_info = commonplayerinfo.CommonPlayerInfo(player_id=players_info[0].get('id')) \
            .get_normalized_dict().get('CommonPlayerInfo')[0]

        ret_str += f" ({ept_info.get('FROM_YEAR')}-{ept_info.get('TO_YEAR')})"

        ret_str += f"\n\t{ept_info.get('TEAM_CITY')} {ept_info.get('TEAM_NAME')} #{ept_info.get('JERSEY')}: {ept_info.get('POSITION')}"

        #split the height into separate feet and inches for formatting
        height = ept_info.get('HEIGHT').split('-')
        ret_str += f"\n\tHeight: {height[0]}\'{height[1]}\", Weight: {ept_info.get('WEIGHT')} lbs"

    return ret_str