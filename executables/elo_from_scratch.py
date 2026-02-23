import datetime
import update
from files import *

def generateELO(rencontres_list, elo_clearance, elo_label):
    global_players_data = {}
    global_decks_data = {}
    if elo_label == "g":
        for rencontre in rencontres_list:
            update.processRencontre(rencontre, global_players_data, elo_clearance, global_decks_data, True)
    elif elo_label == "d":
        for rencontre in rencontres_list:
            update.processRencontreDecksOnly(rencontre, global_decks_data, True)
    elif elo_label == "m":
        for rencontre in rencontres_list:
            update.processRencontreMixtOnly(rencontre, global_players_data, elo_clearance, global_decks_data, True)
    else:
        raise Exception("Bad elo_label")
    return global_players_data, global_decks_data

if __name__ == '__main__':
    import json
    import csv

    decks_file_names = [DECKS_JSON] #[DECKS_JSON, DECKS_D_JSON, DECKS_M_JSON]
    players_file_names = [PLAYER_JSON] #[PLAYER_JSON, PLAYER_D_JSON, PLAYER_M_JSON]
    elo_labels = ["g"] #["g", "d", "m"]
    
    with open(RENCONTRES, newline="", encoding="utf-8") as rencontres_file, open(CLEARANCE, encoding="utf-8") as elo_clearance_file:
        rencontres_list = list(csv.DictReader(rencontres_file))
        elo_clearance = elo_clearance_file.read().split("\n")
        elo_clearance = elo_clearance[0:len(elo_clearance)-1]
        
        for decks_filename, players_filename, elo_label in zip(decks_file_names, players_file_names, elo_labels):
            players_data, decks_data = generateELO(rencontres_list, elo_clearance, elo_label)

            with open(players_filename, mode="w", encoding="utf-8") as players_file:
                json.dump(dict(sorted(players_data.items())), players_file, ensure_ascii=False)

            with open(decks_filename, mode="w", encoding="utf-8") as decks_file:
                json.dump(dict(sorted(decks_data.items(), key=lambda tuple: tuple[1]["Date"])), decks_file, ensure_ascii=False)

    import get_list_players
    get_list_players.writing_list_players_file(PLAYER_JSON, LIST_PLAYERS)
    print("players generated")

    import get_list_sets
    get_list_sets.writing_list_sets_file(DECKS_JSON, LIST_SETS)
    print("sets generated")

    import get_list_decks
    get_list_decks.writing_list_decks_file(DECKS_JSON, LIST_DECKS)
    print("decks generated")

    import get_sorted
    get_sorted.writing_sorted_decks(DECKS_JSON, False)
    get_sorted.writing_sorted_decks(DECKS_JSON, True)
    get_sorted.writing_sorted_players(PLAYER_JSON, False)
    get_sorted.writing_sorted_players(PLAYER_JSON, True)







