import csv
import nba_api.stats.static.players as players
from textdistance.algorithms import *
import time

from fuzzyids import getFuzzyPlayerIdsByName as fuzz

stats_file = "stats.csv"
misspelled = "nba_name_misspellings.csv"
MISSPELLED_INDEX = 0
CORRECT_INDEX = 1

#Algorithms that throw errors: Gotoh, ArithNCD
#Algorithms that are way too slow: Editex, MongeElkan, SmithWaterman, NeedlemanWunsch, LCSSeq
#Algorithms that are really bad at matches for this data: RLENCD, Tanimoto, BWTRLENCD, MongeElkan, MLIPNS
#Compression algorithms are experimental, so not testing them

algorithms = [Hamming(), Levenshtein(), DamerauLevenshtein(), JaroWinkler(), StrCmp95(), Jaccard(), Sorensen(),
              Tversky(), Overlap(), Cosine(), Bag(), LCSStr(), RatcliffObershelp(), SqrtNCD(), EntropyNCD(), MRA()]

with open(misspelled, 'r') as f:
    reader = csv.reader(f)

    stats_dict = {}
    for algorithm in algorithms:
        stats_dict[algorithm.__class__.__name__] = {'total': 0, 'correct': 0, 'incorrect': 0, 'total_time': 0,
                                                    'avg_time': 0, 'total_correct_ratio': 0, 'total_incorrect_ratio': 0,
                                                    'max_correct_ratio': 0, 'min_correct_ratio': 1,
                                                    'max_incorrect_ratio': 0, 'min_incorrect_ratio': 1}

    for row in reader:

        player_id = None
        try:
            player_id = int(row[CORRECT_INDEX])

        except ValueError:
            pass

        if player_id is None:
            players_dict = players.find_players_by_full_name(row[CORRECT_INDEX])
        else:
            players_dict = [players.find_player_by_id(player_id)]

        if not len(players_dict) == 1:
            print(f"Couldn't find player matching {row[CORRECT_INDEX]}")
        else:
            print(f"\"{row[MISSPELLED_INDEX]}\"")
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
                if best is None or not list(best.keys())[0] == players_dict[0].get('id'):
                    print(f"incorrect:{round(best.get('ratio'), 4)}", end='')
                    this_stats_dict['incorrect'] += 1
                    this_stats_dict['total_incorrect_ratio'] += best.get('ratio')

                    if best.get('ratio') < this_stats_dict['min_incorrect_ratio']:
                        this_stats_dict['min_incorrect_ratio'] = best.get('ratio')
                        print(' (IMIN)', end='')

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

print(stats_dict)
with open(stats_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['algorithm', 'total', 'correct', 'incorrect', 'correct_percent', 'total_time', 'avg_time',
                     'max_correct_ratio', 'min_correct_ratio', 'avg_correct_ratio', 'max_incorrect_ratio',
                     'min_incorrect_ratio', 'avg_incorrect_ratio'])

    for key, value in stats_dict.items():
        writer.writerow([key, value['total'], value['correct'], value['incorrect'], value['correct']/value['total'],
                        value['total_time'], value['avg_time'], value['max_correct_ratio'],
                        value['min_correct_ratio'], value['total_correct_ratio']/value['correct'],
                        value['max_incorrect_ratio'], value['min_incorrect_ratio'],
                        value['total_incorrect_ratio']/value['incorrect']])