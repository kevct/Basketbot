import logging
from asyncio import FIRST_COMPLETED
from time import time
import functions as src
import asyncio

LOGGER = logging.getLogger(__name__)

TEST_PLAYER_ID = 2544
TEST_PLAYER_FIRSTNAME = "Lebron"
TEST_PLAYER_LASTNAME = "James"
TEST_PLAYER_FULLNAME = "Lebron James"
HEARTBEAT_WARNING_TIME = 5
HEARTBEAT_FAIL_TIME = 15
TEST_TEAM_ID = 1610612747
TEST_TEAM_FULLNAME = "Los Angeles Lakers"
TEST_TEAM_CITY = "Los Angeles"
TEST_TEAM_NICKNAME = "Lakers"


# to show debug messages during tests
# python -m pytest *_test.py --log-cli-level=10

async def heartbeat_tester():
    """
    A short function that makes sure tests run fast enough to keep from blocking
    the discord server heartbeat
    :return: None
    """
    while True:
        start_time = time()
        await asyncio.sleep(0)
        end_time = time()

        heartbeat_time = end_time - start_time

        if heartbeat_time > HEARTBEAT_WARNING_TIME and heartbeat_time <= HEARTBEAT_FAIL_TIME:
            LOGGER.warning(f"Returned to heartbeat in {end_time - start_time}")

        elif heartbeat_time > HEARTBEAT_FAIL_TIME:
            LOGGER.critical(f"Returned to heartbeat in {end_time - start_time}")

        assert heartbeat_time <= HEARTBEAT_FAIL_TIME


async def schedule_with_heartbeat(function: asyncio.coroutine):
    heartbeat = asyncio.create_task(heartbeat_tester())
    task = asyncio.create_task(function)

    # Normally wait returns `done, pending`, but we know the heartbeat never returns
    # so it should always be the second one
    await asyncio.wait({task, heartbeat}, return_when=FIRST_COMPLETED)

    # If the heartbeat threw an error because it was blocked too long,
    # throw it now
    if heartbeat.done():
        heartbeat.result()
    else:
        heartbeat.cancel()

    if task.done():
        return task.result()
    else:
        assert False


def run_with_heartbeat(function: asyncio.coroutine):
    future_result = asyncio.gather(schedule_with_heartbeat(function))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(future_result)

    assert future_result.done()

    return future_result.result()


def test_getPlayerSeasonStatsByID_default():
    season_fun = src.getPlayerSeasonStatsByID(player_id=TEST_PLAYER_ID)

    season_stats = run_with_heartbeat(season_fun)

    # TODO: Actually validate season stats results
    assert True


def test_getPlayerSeasonStatsByID_noproxy():
    season_fun = src.getPlayerSeasonStatsByID(player_id=TEST_PLAYER_ID, use_proxy=False)

    season_stats = run_with_heartbeat(season_fun)

    # TODO: Actually validate season stats results
    assert True


def test_getPlayerSeasonStatsByID_forceproxy():
    season_fun = src.getPlayerSeasonStatsByID(player_id=TEST_PLAYER_ID, use_proxy=True)

    season_stats = run_with_heartbeat(season_fun)

    # TODO: Actually validate season stats results
    assert True


def test_getPlayerCareerStatsByID_default():
    career_fun = src.getPlayerCareerStatsByID(player_id=TEST_PLAYER_ID)

    career_stats = run_with_heartbeat(career_fun)

    # TODO: Actually validate results
    assert True


def test_getPlayerCareerStatsByID_noproxy():
    career_fun = src.getPlayerCareerStatsByID(player_id=TEST_PLAYER_ID, use_proxy=False)

    career_stats = run_with_heartbeat(career_fun)

    # TODO: Actually validate results
    assert True


def test_getPlayerCareerStatsByID_forceproxy():
    career_fun = src.getPlayerCareerStatsByID(player_id=TEST_PLAYER_ID, use_proxy=True)

    career_stats = run_with_heartbeat(career_fun)

    # TODO: Actually validate results
    assert True


def test_getPlayerCareerString_default():
    career_fun = src.getPlayerCareerString(player_id=TEST_PLAYER_ID)

    career_string = run_with_heartbeat(career_fun)

    # TODO: Actually validate results
    assert True


def test_getPlayerIdsByName_full():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_FULLNAME)

    assert len(player_id) == 1


def test_getPlayerIdsByName_first():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_FIRSTNAME)

    assert len(player_id) == 1


def test_getPlayerIdsByName_last():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_LASTNAME)

    assert len(player_id) > 0


def test_getPlayerIdsByName_full_fuzzy():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_FULLNAME, fuzzy_match=True)

    assert len(player_id) == 1


def test_getPlayerIdsByName_first_fuzzy():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_FIRSTNAME, fuzzy_match=True)

    assert len(player_id) == 1


def test_getPlayerIdsByName_last_fuzzy():
    player_id = src.getPlayerIdsByName(TEST_PLAYER_LASTNAME, fuzzy_match=True)

    assert len(player_id) > 0


def test_getActivePlayerIdsByName_full():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_FULLNAME)

    assert len(player_id) == 1


def test_getActivePlayerIdsByName_first():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_FIRSTNAME)

    assert len(player_id) == 1


def test_getActivePlayerIdsByName_last():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_LASTNAME)

    assert len(player_id) > 0


def test_getActivePlayerIdsByName_full_fuzzy():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_FULLNAME, fuzzy_match=True)

    assert len(player_id) == 1


def test_getActivePlayerIdsByName_first_fuzzy():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_FIRSTNAME, fuzzy_match=True)

    assert len(player_id) == 1


def test_getActivePlayerIdsByName_last_fuzzy():
    player_id = src.getActivePlayerIdsByName(TEST_PLAYER_LASTNAME, fuzzy_match=True)

    assert len(player_id) > 0


def test_getPlayerHeadshotURL():
    url = src.getPlayerHeadshotURL(TEST_PLAYER_ID)

    assert url is not None


def test_getTeamLogoURL():
    url = src.getTeamLogoURL(TEST_TEAM_ID)

    assert url is not None


def test_getTeamCareerStatsByID_default():
    career_fun = src.getTeamCareerStatsByID(TEST_TEAM_ID)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamCareerStatsByID_noproxy():
    career_fun = src.getTeamCareerStatsByID(TEST_TEAM_ID, use_proxy=False)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamCareerStatsByID_forceproxy():
    career_fun = src.getTeamCareerStatsByID(TEST_TEAM_ID, use_proxy=True)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamSeasonStatsByID_default():
    career_fun = src.getTeamSeasonStatsByID(TEST_TEAM_ID)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamSeasonStatsByID_noproxy():
    career_fun = src.getTeamSeasonStatsByID(TEST_TEAM_ID, use_proxy=False)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamSeasonStatsByID_forceproxy():
    career_fun = src.getTeamSeasonStatsByID(TEST_TEAM_ID, use_proxy=True)

    career_stats = run_with_heartbeat(career_fun)

    assert True


def test_getTeamIdsByName_full():
    team_id = src.getTeamIdsByName(TEST_TEAM_FULLNAME)

    assert len(team_id) == 1


def test_getTeamIdsByName_city():
    team_id = src.getTeamIdsByName(TEST_TEAM_CITY)

    assert len(team_id) > 1


def test_getTeamIdsByName_nickname():
    team_id = src.getTeamIdsByName(TEST_TEAM_NICKNAME)

    assert len(team_id) == 1


def test_getTeamIdsByName_full_fuzzy():
    team_id = src.getTeamIdsByName(TEST_TEAM_FULLNAME, fuzzy_match=True)

    assert len(team_id) == 1


def test_getTeamIdsByName_city_fuzzy():
    team_id = src.getTeamIdsByName(TEST_TEAM_CITY, fuzzy_match=True)

    assert len(team_id) > 1


def test_getTeamIdsByName_nickname_fuzzy():
    team_id = src.getTeamIdsByName(TEST_TEAM_NICKNAME, fuzzy_match=True)

    assert len(team_id) == 1


def test_getTeamColor():
    team_color = src.getTeamColor(TEST_TEAM_ID)

    assert True
