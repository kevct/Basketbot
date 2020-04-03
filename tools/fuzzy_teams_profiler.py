import csv
import nba_api.stats.static.teams as teams
from textdistance.algorithms import *
import time

from fuzzyids import getFuzzyTeamIdsByName as fuzz

one_stats_file = "one_stats_teams.csv"
full_stats_file = "full_stats_teams.csv"
misspelled = "nba_team_misspellings.csv"
MISSPELLED_INDEX = 0
CORRECT_INDEX = 1

#Algorithms that throw errors: Gotoh, ArithNCD
#Algorithms that are way too slow: Editex, MongeElkan, SmithWaterman, NeedlemanWunsch, LCSSeq
#Algorithms that are really bad at matches for this data (<70% success): RLENCD, Tanimoto, BWTRLENCD, MongeElkan, MLIPNS,
#                                              Overlap (because it will return a ratio of 0.0 when it's wrong sometimes)
#Compression algorithms are experimental, so not testing them

algorithms = [Hamming(), Levenshtein(), DamerauLevenshtein(), JaroWinkler(), StrCmp95(), Jaccard(), Sorensen(),
              Tversky(), Cosine(), Bag(), LCSStr(), RatcliffObershelp(), SqrtNCD(), EntropyNCD(), MRA()]

with open(misspelled, 'r') as f:
    reader = csv.reader(f)

    one_stats_dict = {}
    full_stats_dict = {}

    for algorithm in algorithms:
        one_stats_dict[algorithm.__class__.__name__] = {'total': 0, 'correct': 0, 'incorrect': 0, 'total_time': 0,
                                                    'avg_time': 0, 'total_correct_ratio': 0, 'total_incorrect_ratio': 0,
                                                    'max_correct_ratio': 0, 'min_correct_ratio': 1,
                                                    'max_incorrect_ratio': 0, 'min_incorrect_ratio': 1}
        full_stats_dict[algorithm.__class__.__name__] = {'total': 0, 'correct': 0, 'incorrect': 0, 'total_time': 0,
                                                        'avg_time': 0, 'total_correct_ratio': 0,
                                                        'total_incorrect_ratio': 0,
                                                        'max_correct_ratio': 0, 'min_correct_ratio': 1,
                                                        'max_incorrect_ratio': 0, 'min_incorrect_ratio': 1}

    for row in reader:

        #First check if field has an ID instead of a name
        team_id = None
        try:
            team_id = int(row[CORRECT_INDEX])
        except ValueError:
            pass

        # If it's not an ID, get the team by their name
        if team_id is None:
            teams_dict = teams.find_teams_by_full_name(row[CORRECT_INDEX])
        else:
            teams_dict = [teams.find_team_name_by_id(team_id)]

        # Don't run the test if we don't know what the solution should be
        if not len(teams_dict) == 1:
            print(f"Couldn't find team matching {row[CORRECT_INDEX]}")
        else:
            print(f"\"{row[MISSPELLED_INDEX]}\" ", end='')

            # Figure out which mode the fuzzy code is going to run in
            team_names = row[MISSPELLED_INDEX].split()
            if len(team_names) == 1:
                stats_dict = one_stats_dict
                print('(First or last name mode)')
            else:
                stats_dict = full_stats_dict
                print('(Full name mode)')

            for algorithm in algorithms:
                print(f"\t{algorithm.__class__.__name__} - ", end='')
                start = 0
                end = 0

                start = time.time()
                best = fuzz(row[MISSPELLED_INDEX], max_distance=1,
                     log_file=f'log/{row[MISSPELLED_INDEX]}_{algorithm.__class__.__name__}.csv',
                     dist_algorithm=algorithm, return_ratio=True, only_return_best=True)
                end = time.time()

                this_stats_dict = stats_dict[algorithm.__class__.__name__]
                this_stats_dict['total'] += 1
                this_stats_dict['total_time'] += end - start
                this_stats_dict['avg_time'] = this_stats_dict['total_time'] / this_stats_dict['total']
                if best is None or not list(best.keys())[0] == teams_dict[0].get('id'):
                    print(f"incorrect:{round(best.get('ratio'), 4)}", end='')
                    this_stats_dict['incorrect'] += 1
                    this_stats_dict['total_incorrect_ratio'] += best.get('ratio')

                    if best.get('ratio') < this_stats_dict['min_incorrect_ratio']:
                        if best.get('ratio') > 0.0:
                            this_stats_dict['min_incorrect_ratio'] = best.get('ratio')
                            print(' (IMIN)', end='')
                        else:
                            # If the match was incorrect but the ratio was 0, the test is probably bad
                            print(' (IWARN)', end='')

                    if best.get('ratio') > this_stats_dict['max_incorrect_ratio']:
                        this_stats_dict['max_incorrect_ratio'] = best.get('ratio')
                        print(' (IMAX)', end='')

                    print()

                else:
                    print(f"correct:{round(best.get('ratio'), 4)}", end='')
                    stats_dict[algorithm.__class__.__name__]['correct'] += 1
                    this_stats_dict['total_correct_ratio'] += best.get('ratio')

                    if best.get('ratio') < this_stats_dict['min_correct_ratio']:
                        this_stats_dict['min_correct_ratio'] = best.get('ratio')
                        print(' (CMIN)', end='')

                    if best.get('ratio') > this_stats_dict['max_correct_ratio']:
                        this_stats_dict['max_correct_ratio'] = best.get('ratio')
                        print(' (CMAX)', end='')

                    print()

for stats_file, stats_dict in [(one_stats_file, one_stats_dict), (full_stats_file, full_stats_dict)]:
    print(stats_dict)
    with open(stats_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['algorithm', 'total', 'correct', 'incorrect', 'correct_percent', 'total_time', 'avg_time',
                         'max_correct_ratio', 'min_correct_ratio', 'avg_correct_ratio', 'max_incorrect_ratio',
                         'min_incorrect_ratio', 'avg_incorrect_ratio'])


        for key, value in stats_dict.items():
            try:
                correct_ratio = value['total_correct_ratio'] / value['correct']
            except ZeroDivisionError:
                correct_ratio = 0
            try:
                incorrect_ratio = value['total_incorrect_ratio']/value['incorrect']
            except ZeroDivisionError:
                incorrect_ratio = 0

            writer.writerow([key, value['total'], value['correct'], value['incorrect'], value['correct']/value['total'],
                            value['total_time'], value['avg_time'], value['max_correct_ratio'],
                            value['min_correct_ratio'], correct_ratio, value['max_incorrect_ratio'],
                            value['min_incorrect_ratio'], incorrect_ratio])