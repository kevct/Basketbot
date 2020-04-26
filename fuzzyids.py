import logging
from typing import Optional, Dict, List, Tuple, Type

import textdistance
import nba_api.stats.library.data as nba_data
import textdistance as tdist
import csv

# All the functions that don't use the player id searching the nba api, but use the data.py arrays directly
# Most of these functions should not be called directly, as cutting down the number of names to fuzzy match will greatly
# decrease runtime
# NOTE - INSTALL EXTRAS WITH TEXTDISTANCE BECAUSE OTHERWISE IT'S REALLY SLOW
# pip3 install textdistance[extras]

# A constant distance that usually works for getting relatively similar names (based on profiler returned
# max_correct_ratio)

PLAYER_SINGLENAME_MAX_DISTANCE = 0.2
PLAYER_FIRSTLAST_MAX_DISTANCE = 0.1907407407
PLAYER_FULLNAME_MAX_DISTANCE = 0.3571428571
TEAM_SINGLENAME_MAX_DISTANCE = 0.2738095238
TEAM_FULLNAME_MAX_DISTANCE = 0.1997988939
# A name below this distance is probably what we're looking for, usually only the correct result should be below this
# value (Based on profiler returned min_incorrect_ratio)
PLAYER_SINGLENAME_MIN_DISTANCE = 0.09090909091
PLAYER_FIRSTLAST_MIN_DISTANCE = 0.1125
PLAYER_FULLNAME_MIN_DISTANCE = 0.2307692308
TEAM_SINGLENAME_MIN_DISTANCE = .1805555556
TEAM_FULLNAME_MIN_DISTANCE = 0.3470899471
# The default text distance searching algorithms (chosen for speed and consistent ratios for correct values)
# (based on profiler returned correct_percent)
player_singlename_distance_algorithm = tdist.RatcliffObershelp
player_firstlast_distance_algorithm = tdist.JaroWinkler
player_fullname_distance_algorithm = tdist.RatcliffObershelp
team_singlename_distance_algorithm = tdist.JaroWinkler
team_fullname_distance_algorithm = tdist.JaroWinkler

LOGGER = logging.getLogger(__name__)


def getNameDistSingle(name, nba_player_info, only_active: bool = False, max_distance: Optional[float] = None,
                      dist_algorithm: textdistance.algorithms = None) -> Optional[Tuple[List, float]]:
    """
    Helper function to return the string distance between a given NBA player's name and a given first or last name.
    Designed to be used with multiprocessing.
    :param max_distance:
    :param name:
    :param nba_player_info:
    :param only_active:
    :param dist_algorithm:
    :return:
    """

    if dist_algorithm is None:
        dist_algorithm = player_singlename_distance_algorithm()

    if max_distance is None:
        max_distance = PLAYER_SINGLENAME_MAX_DISTANCE

    if not only_active or (only_active and nba_player_info[nba_data.player_index_is_active]):
        first_distance = dist_algorithm.normalized_distance(name, nba_player_info[nba_data.player_index_first_name]
                                                            .lower())
        last_distance = dist_algorithm.normalized_distance(name, nba_player_info[nba_data.player_index_last_name]
                                                           .lower())
        lesser_distance = min(first_distance, last_distance)

        if lesser_distance <= max_distance:
            return nba_player_info, lesser_distance

    return None


def getNameDistFirstLast(first_name, last_name, nba_player_info, only_active: bool = False, max_distance=None,
                         dist_algorithm=None) -> Optional[Tuple[List, float]]:
    """
    Helper function to return the string distance between a given NBA player's name and a first and last name.
    Designed to be used with multiprocessing.
    :param max_distance:
    :param first_name:
    :param last_name:
    :param nba_player_info:
    :param only_active:
    :param dist_algorithm:
    :return:
    """
    if dist_algorithm is None:
        dist_algorithm = player_firstlast_distance_algorithm()

    if max_distance is None:
        max_distance = PLAYER_FIRSTLAST_MAX_DISTANCE

    if not only_active or (only_active and nba_player_info[nba_data.player_index_is_active]):
        # Get the string distance for the first and last names, and record the better one
        first_distance = dist_algorithm.normalized_distance(first_name,
                                                            nba_player_info[nba_data.player_index_first_name]
                                                            .lower())
        last_distance = dist_algorithm.normalized_distance(last_name,
                                                           nba_player_info[nba_data.player_index_last_name]
                                                           .lower())
        weighted_distance = (first_distance + last_distance * 2) / 3

        if weighted_distance <= max_distance:
            return nba_player_info, weighted_distance

    return None


def getNameDistFull(name: str, nba_player_info, only_active: bool = False, max_distance: Optional[float] = None,
                    dist_algorithm=None) -> Optional[Tuple[List, float]]:
    """
    Helper function to return the string distance between a given NBA player's name and a full name.
    Designed to be used with multiprocessing
    :param max_distance:
    :param name: String representing the name to compare against
    :param nba_player_info: The list of info about an NBA player to compare against
    :param only_active: Whether or not to filter out inactive players
    :param dist_algorithm: a textdistance algorithm to compare the two names
    :return:
    """
    if dist_algorithm is None:
        dist_algorithm = player_fullname_distance_algorithm()

    if max_distance is None:
        max_distance = PLAYER_FULLNAME_MAX_DISTANCE

    if not only_active or (only_active and nba_player_info[nba_data.player_index_is_active]):
        distance = dist_algorithm.normalized_distance(name, nba_player_info[nba_data.player_index_full_name].lower())

        if distance <= max_distance:
            return nba_player_info, distance

    return None


def getTeamDistSingle(name: str, nba_team_info, max_distance: Optional[float] = None, dist_algorithm=None) \
        -> Optional[Tuple[List, float]]:
    """
    Helper function to get the string distance between name string and the various names for an nba team
    :param name:
    :param nba_team_info:
    :param max_distance:
    :param dist_algorithm:
    :return:
    """
    if dist_algorithm is None:
        dist_algorithm = team_singlename_distance_algorithm()

    if max_distance is None:
        max_distance = TEAM_SINGLENAME_MAX_DISTANCE

    # Get the string distance for the city, nick, and abbrev, and record the better one
    city_distance = dist_algorithm.normalized_distance(name,
                                                       nba_team_info[nba_data.team_index_city]
                                                       .lower())
    nick_distance = dist_algorithm.normalized_distance(name,
                                                       nba_team_info[nba_data.team_index_nickname]
                                                       .lower())
    abbrev_distance = dist_algorithm.normalized_distance(name, nba_team_info[nba_data.team_index_abbreviation]
                                                         .lower())

    best_dist = min(city_distance, nick_distance, abbrev_distance)

    # Check if either string is remotely close
    if best_dist <= max_distance:
        return nba_team_info, best_dist
    else:
        return None


def getTeamDistFull(name: str, nba_team_info, max_distance: Optional[float] = None, dist_algorithm=None) \
        -> Optional[Tuple[List, float]]:
    """
    Helper function to get the string distance between a string and a team name
    :param name:
    :param nba_team_info:
    :param max_distance:
    :param dist_algorithm:
    :return:
    """
    if dist_algorithm is None:
        dist_algorithm = team_singlename_distance_algorithm()

    if max_distance is None:
        max_distance = TEAM_FULLNAME_MAX_DISTANCE

    # Get the string distance for the full team name
    distance = dist_algorithm.normalized_distance(name, nba_team_info[nba_data.team_index_full_name].lower())

    # Check if either string is remotely close
    if distance <= max_distance:
        return nba_team_info, distance
    else:
        return None


def getFuzzyPlayerIdsByName(player_name: str,
                            only_active: bool = False,
                            max_distance: float = None, min_distance: float = None,
                            dist_algorithm: textdistance.algorithms = None,
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
    if log_file is not None:
        f = open(log_file, 'w', newline='')
        logger = csv.writer(f)

        logger.writerow(['algorithm', 'target', 'player', 'string distance'])

    player_names = player_name.split()

    # dictionary indexed by player id with value player name
    matches = {}
    good_matches = {}
    perfect_matches = {}
    best_id: Optional[int] = None
    best_distance = None

    if len(player_names) < 1:
        return None

    elif len(player_names) == 1:
        # Only one name specified, check against first and last names
        name = player_names[0].lower()

        if min_distance is None:
            min_distance = PLAYER_SINGLENAME_MIN_DISTANCE

        for nba_player in nba_data.players:

            if not only_active or (only_active and nba_player[nba_data.player_index_is_active]):
                # Get the string distance for the first and last names, and record the better one
                distance_result = getNameDistSingle(name, nba_player, only_active=only_active,
                                                    max_distance=max_distance,
                                                    dist_algorithm=dist_algorithm)

                if distance_result is not None:
                    nba_player, distance = distance_result
                    LOGGER.debug(
                        f"Single name distance ({name}|{nba_player[nba_data.player_index_full_name]}) = {distance}")

                    # Add the id to the list of matches found
                    matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    # Check if this match is closer than the close match threshold threshold
                    if distance < min_distance:
                        good_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                        if distance == 0:
                            perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[
                                nba_data.player_index_full_name]

                    # Check if this match is  the best match so far
                    if best_distance is None or distance < best_distance:
                        best_distance = distance
                        best_id = nba_player[nba_data.player_index_id]

                    # Log to CSV if enabled
                    if logger is not None:
                        logger.writerow([dist_algorithm.__class__.__name__, player_name,
                                         nba_player[nba_data.player_index_full_name], distance])

    elif len(player_names) > 2:
        # More than two names specified, check against full names

        name = player_name.strip().lower()

        if min_distance is None:
            min_distance = PLAYER_FULLNAME_MIN_DISTANCE

        for nba_player in nba_data.players:

            # Get the string distance for the first and last names, and record the better one
            distance_result = getNameDistFull(name, nba_player, only_active=only_active, max_distance=max_distance,
                                              dist_algorithm=dist_algorithm)

            if distance_result is not None:
                nba_player, distance = distance_result
                LOGGER.debug(f"Full name distance ({name}|{nba_player[nba_data.player_index_full_name]}) = {distance}")

                # Add the id to the list of matches found
                matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if distance < min_distance:
                    good_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    if distance == 0:
                        perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[
                            nba_data.player_index_full_name]

                # Check if this match is  the best match so far
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_id = nba_player[nba_data.player_index_id]

                # Log to CSV if enabled
                if logger is not None:
                    logger.writerow(
                        [dist_algorithm.__class__.__name__, player_name, nba_player[nba_data.player_index_full_name],
                         distance])

    else:
        # Exactly two names specified, check against last name then first name
        first_name = player_names[0].lower()
        last_name = player_names[1].lower()

        if min_distance is None:
            min_distance = PLAYER_FIRSTLAST_MIN_DISTANCE

        for nba_player in nba_data.players:

            # Theoretically the last name is more important than the first name, so give that one more weight
            distance_result = getNameDistFirstLast(first_name, last_name, nba_player, only_active, max_distance,
                                                   dist_algorithm)

            if distance_result is not None:
                nba_player, distance = distance_result
                LOGGER.debug(
                    f"First/last distance ({first_name} {last_name}|{nba_player[nba_data.player_index_full_name]}) = {distance}")

                # Add the id to the list of matches found
                matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if distance < min_distance:
                    good_matches[nba_player[nba_data.player_index_id]] = nba_player[nba_data.player_index_full_name]

                    if distance == 0:
                        perfect_matches[nba_player[nba_data.player_index_id]] = nba_player[
                            nba_data.player_index_full_name]

                # Check if this match is  the best match so far
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_id = nba_player[nba_data.player_index_id]

                # Log to CSV if enabled
                if logger is not None:
                    logger.writerow([dist_algorithm.__class__.__name__, player_name,
                                     nba_player[nba_data.player_index_full_name], distance])

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
            return {int(best_id): matches[best_id]}

    else:
        if len(perfect_matches) > 0:
            return perfect_matches
        elif len(good_matches) > 0:
            return good_matches
        elif len(matches) > 0:
            return matches
        else:
            return None


def getFuzzyTeamIdsByName(team_name: str,
                          max_distance: Optional[float] = None, min_distance: Optional[float] = None,
                          dist_algorithm: textdistance.algorithms = None,
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
    if log_file is not None:
        f = open(log_file, 'w', newline='')
        logger = csv.writer(f)

        logger.writerow(['algorithm', 'target', 'team', 'city distance', 'nickname distance',
                         'abbreviation distance', 'result distance'])

    team_names = team_name.split()

    # dictionary indexed by team id with value team full name
    matches = {}
    perfect_matches = {}
    good_matches = {}
    best_id: Optional[int] = None
    best_distance: Optional[float] = None

    if len(team_names) == 1:
        # Only one name specified, check against city, nickname, and abbreviation
        name = team_names[0].lower()

        if min_distance is None:
            min_distance = TEAM_SINGLENAME_MIN_DISTANCE

        for nba_team in nba_data.teams:

            distance_result = getTeamDistSingle(name, nba_team, max_distance, dist_algorithm)

            # Check if either string is remotely close
            if distance_result is not None:
                nba_team, distance = distance_result

                # Add the id to the list of matches found
                matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if distance < min_distance:
                    good_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                    if distance == 0:
                        perfect_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is the best match so far
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_id = nba_team[nba_data.team_index_id]

                # Log to CSV if enabled
                if logger is not None:
                    logger.writerow(
                        [dist_algorithm.__class__.__name__, team_name, nba_team[nba_data.team_index_full_name],
                         distance])

    else:
        # More than one name specified, check against full names

        name = team_name.strip().lower()

        if min_distance is None:
            min_distance = TEAM_FULLNAME_MIN_DISTANCE

        for nba_team in nba_data.teams:
            # Get the string distance for the first and last names, and record the better one
            distance_result = getTeamDistFull(name, nba_team, max_distance, dist_algorithm)

            if distance_result is not None:
                nba_team, distance = distance_result

                # Add the id to the list of matches found
                matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is closer than the close match threshold threshold
                if distance < min_distance:
                    good_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                    if distance == 0:
                        perfect_matches[nba_team[nba_data.team_index_id]] = nba_team[nba_data.team_index_full_name]

                # Check if this match is  the best match so far
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_id = nba_team[nba_data.team_index_id]

                # Log to CSV if enabled
                if logger is not None:
                    logger.writerow(
                        [dist_algorithm.__class__.__name__, team_name, nba_team[nba_data.team_index_full_name],
                         distance])

    # If we're logging, close the file
    if not f is None:
        f.close()

    # Return the best match

    if only_return_best:
        if best_id is None:
            return None
        elif return_ratio:
            return {best_id: matches[best_id], -1: best_distance}
        else:
            return {best_id: matches[best_id]}

    else:
        if len(perfect_matches) > 0:
            return perfect_matches
        elif len(good_matches) > 0:
            return good_matches
        elif len(matches) > 0:
            return matches
        else:
            return None
