from typing import Optional, Dict

import textdistance
import nba_api.stats.library.data as nba_data
import textdistance as tdist
import csv


# All the functions that don't use the player id searching the nba api, but use the data.py arrays directly
# Most of these functions should not be called directly, as cutting down the number of names to fuzzy match will greatly
# decrease runtime
# NOTE - INSTALL EXTRAS WITH TEXTDISTANCE BECAUSE OTHERWISE IT'S REALLY SLOW
# pip3 install textdistance[extras]

# A constant distance that seems to work for getting relatively similar names
FUZZY_MAX_DISTANCE = 0.1907407407
# A name below this distance is probably what we're looking for, no need to keep searching
FUZZY_MIN_DISTANCE = 0.1125
# The default text distance searching algorithm (chosen because it's relatively fast and has consistently low ratios for
# correct values
default_distance_algorithm = tdist.JaroWinkler()

#TODO - Detect player initials that are passed in

def getFuzzyPlayerIdsByName(player_name: str,
                            only_active: bool = False,
                            max_distance: float = FUZZY_MAX_DISTANCE, min_distance: float = FUZZY_MIN_DISTANCE,
                            dist_algorithm: textdistance = default_distance_algorithm,
                            log_file: str = None, return_ratio: bool = False, only_return_best: bool = False) \
                            -> Optional[Dict[int, str]]:
    """
    Finds ids that closely match a given string
    :param player_name: The name to seach the NBA roster for
    :param only_active: Optional param to only return active players
    :param max_distance: Optional param to override the default maximum cutoff for matches
    :param min_distance: Optional param to override the default maximum cutoff for close matches
    :param dist_algorithm: Optional param to use a different textdistance algorithm to evaluate distance
    :param log_file: Optional param to generate .csv files with tables of distance ratios
    :param return_ratio: Optional param to add an entry to the return dictionary with the ratio of the best match. Only
                         works if only_return_best is True
    :param only_return_best: Optional param to return the single best match instead of a list of matches below the
                             cutoff
    :return:
    """

    # If logging is enabled, create a log file
    f = None
    logger = None
    if not log_file is None:
        f = open(log_file, 'w', newline='')
        logger = csv.writer(f)

        logger.writerow(['algorithm', 'target', 'player', 'first name distance', 'last name distance',
                        'result distance'])


    player_names = player_name.split()

    #dictionary indexed by player id with value player name
    matches = {}
    perfect_matches = {}
    best_id = None
    best_distance = None

    if len(player_names) < 1:
        return None

    elif len(player_names) == 1:
        #Only one name specified, check against first and last names
        name = player_names[0].lower()

        for nba_player in nba_data.players:

            if not only_active or (only_active and nba_player[nba_data.player_index_is_active]):
                #Get the string distance for the first and last names, and record the better one
                first_distance = dist_algorithm.normalized_distance(name,
                                                                    nba_player[nba_data.player_index_first_name]
                                                                    .lower())
                last_distance = dist_algorithm.normalized_distance(name,
                                                                   nba_player[nba_data.player_index_last_name]
                                                                   .lower())
                better_dist = min(first_distance, last_distance)

                #Check if either string is remotely close
                if better_dist <= max_distance:

                    # Add the id to the list of matches found
                    matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is closer than the close match threshold threshold
                    if better_dist < min_distance:
                        perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is  the best match so far
                    if best_distance is None or better_dist < best_distance:
                        best_distance = better_dist
                        best_id = nba_player[nba_data.player_index_id]

                    # Log to CSV if enabled
                    if not logger is None:
                        logger.writerow([dist_algorithm.__class__.__name__, player_name, nba_player[nba_data.player_index_full_name], first_distance,
                                         last_distance, better_dist])

    elif len(player_names) > 2:
        #More than two names specified, check against full names

        name = player_name.strip().lower()

        for nba_player in nba_data.players:
            if not only_active or (only_active and nba_player[nba_data.player_index_is_active]):
                # Get the string distance for the first and last names, and record the better one
                distance = dist_algorithm.normalized_distance(name, nba_player[nba_data.player_index_full_name].lower())

                # Check if either string is remotely close
                if distance <= max_distance:

                    # Add the id to the list of matches found
                    matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is closer than the close match threshold threshold
                    if distance < min_distance:
                        perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is  the best match so far
                    if best_distance is None or distance < best_distance:
                        best_distance = distance
                        best_id = nba_player[nba_data.player_index_id]

                    # Log to CSV if enabled
                    if not logger is None:
                        logger.writerow([dist_algorithm.__class__.__name__, player_name, nba_player[nba_data.player_index_full_name], '', '', distance])

    else:
        #Exactly two names specified, check against last name then first name
        first_name = player_names[0].lower()
        last_name = player_names[1].lower()

        for nba_player in nba_data.players:
            if not only_active or (only_active and nba_player[nba_data.player_index_is_active]):
                # Get the string distance for the first and last names, and record the better one
                first_distance = dist_algorithm.normalized_distance(first_name,
                                                                    nba_player[nba_data.player_index_first_name].lower())
                last_distance = dist_algorithm.normalized_distance(last_name,
                                                                   nba_player[nba_data.player_index_last_name].lower())

                # Theoretically the last name is more important than the first name, so give that one more weight
                weighted_distance = (first_distance + last_distance * 2) / 3

                # Check if either string is remotely close
                if weighted_distance <= max_distance:

                    # Add the id to the list of matches found
                    matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is closer than the close match threshold threshold
                    if weighted_distance < min_distance:
                        perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is  the best match so far
                    if best_distance is None or weighted_distance < best_distance:
                        best_distance = weighted_distance
                        best_id = nba_player[nba_data.player_index_id]

                    # Log to CSV if enabled
                    if not logger is None:
                        logger.writerow([dist_algorithm.__class__.__name__, player_name,
                                         nba_player[nba_data.player_index_full_name], first_distance, last_distance,
                                         weighted_distance])

    # If we're logging, close the file
    if not f is None:
        f.close()

    # Return the best match

    if only_return_best:
        if best_id is None:
            return None
        elif return_ratio:
            return {best_id: matches[best_id], 'ratio': best_distance}
        else:
            return {best_id: matches[best_id]}

    else:
        if len(perfect_matches) > 0:
            return perfect_matches
        elif len(matches) > 0:
            return matches
        else:
            return None


def getFuzzyTeamIdsByName(team_name: str,
                          max_distance: float = FUZZY_MAX_DISTANCE, min_distance: float = FUZZY_MIN_DISTANCE,
                          dist_algorithm: textdistance = default_distance_algorithm,
                          log_file: str = None, return_ratio: bool = False, only_return_best: bool = False) \
                            -> Optional[Dict[int, str]]:
    """
    Finds ids that closely match a given string
    :param team_name: The name to seach the NBA roster for
    :param max_distance: Optional param to override the default maximum cutoff for matches
    :param min_distance: Optional param to override the default maximum cutoff for close matches
    :param dist_algorithm: Optional param to use a different textdistance algorithm to evaluate distance
    :param log_file: Optional param to generate .csv files with tables of distance ratios
    :param return_ratio: Optional param to add an entry to the return dictionary with the ratio of the best match. Only
                         works if only_return_best is True
    :param only_return_best: Optional param to return the single best match instead of a list of matches below the
                             cutoff
    :return:
    """

    # If logging is enabled, create a log file
    f = None
    logger = None
    if not log_file is None:
        f = open(log_file, 'w', newline='')
        logger = csv.writer(f)

        logger.writerow(['algorithm', 'target', 'team', 'city distance', 'nickname distance',
                        'abbreviation distance', 'result distance'])


    team_names = team_name.split()

    #dictionary indexed by team id with value team full name
    matches = {}
    perfect_matches = {}
    best_id = None
    best_distance = None

    if len(team_names) == 1:
        #Only one name specified, check against city, nickname, and abbreviation
        name = team_names[0].lower()

        for nba_team in nba_data.teams:

            #Get the string distance for the city, nick, and abbrev, and record the better one
            city_distance = dist_algorithm.normalized_distance(name,
                                                                nba_team[nba_data.team_index_city]
                                                                .lower())
            nick_distance = dist_algorithm.normalized_distance(name,
                                                               nba_team[nba_data.team_index_nickname]
                                                               .lower())
            abbrev_distance = dist_algorithm.normalized_distance(name, nba_team[nba_data.team_index_abbreviation]
                                                               .lower())

            best_dist = min(city_distance, nick_distance, abbrev_distance)

            #Check if either string is remotely close
            if best_dist <= max_distance:

                # Add the id to the list of matches found
                matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if best_dist < min_distance:
                    perfect_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is  the best match so far
                if best_distance is None or best_dist < best_distance:
                    best_distance = best_dist
                    best_id = nba_team[nba_data.team_index_id]

                # Log to CSV if enabled
                if not logger is None:
                    logger.writerow([dist_algorithm.__class__.__name__, team_name, nba_team[nba_data.team_index_full_name], city_distance,
                                     nick_distance, abbrev_distance, best_dist])

    else:
        # More than one name specified, check against full names

        name = team_name.strip().lower()

        for nba_team in nba_data.teams:
            # Get the string distance for the first and last names, and record the better one
            distance = dist_algorithm.normalized_distance(name, nba_team[nba_data.team_index_full_name].lower())

            # Check if either string is remotely close
            if distance <= max_distance:

                # Add the id to the list of matches found
                matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if distance < min_distance:
                    perfect_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is  the best match so far
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_id = nba_team[nba_data.team_index_id]

                # Log to CSV if enabled
                if not logger is None:
                    logger.writerow([dist_algorithm.__class__.__name__, team_name, nba_team[nba_data.team_index_full_name], '', '', '', distance])

    # If we're logging, close the file
    if not f is None:
        f.close()

    # Return the best match

    if only_return_best:
        if best_id is None:
            return None
        elif return_ratio:
            return {best_id: matches[best_id], 'ratio': best_distance}
        else:
            return {best_id: matches[best_id]}

    else:
        if len(perfect_matches) > 0:
            return perfect_matches
        elif len(matches) > 0:
            return matches
        else:
            return None