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
        ret_str = "Player " + str(players_info[0].get('id')) + ": " + \
                  players_info[0].get('full_name') + \
                  "\n\t"

        ret_str += "Status: "
        if players_info[0].get('is_active'):
            ret_str += "Active"
        else:
            ret_str += "Inactive"

        # get the rest of the data from the NBA api endpoint
        # might want to change this to DataFrame if we need it for graphing later
        endpoint_info = commonplayerinfo.CommonPlayerInfo(player_id=players_info[0].get('id')) \
            .get_normalized_dict().get('CommonPlayerInfo')[0]

        ret_str += "\n\t#" + endpoint_info.get("JERSEY") + " on the " + endpoint_info.get('TEAM_CITY') + " " + \
                   endpoint_info.get('TEAM_NAME')

        #split the height into separate feet and inches for formatting
        height = endpoint_info.get("HEIGHT").split('-')
        ret_str += "\n\tHeight: " + height[0] + "\'" + height[1] + "\", Weight: " + endpoint_info.get("WEIGHT") + " lbs"


    return ret_str