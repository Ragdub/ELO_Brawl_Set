import datetime
import update


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

    decks_filenames = ["decks.json", "decks_decks_only.json", "decks_mixt_only.json"]
    players_filenames = ["players.json", "players_decks_only.json", "players_mixt_only.json"]
    elo_labels = ["g", "d", "m"]
    elo_clearance_filename = "players_ELO_clearance.txt"
    rencontres_filename = "rencontres.csv"
    
    with open(rencontres_filename, newline="", encoding="utf-8") as rencontres_file, open(elo_clearance_filename, encoding="utf-8") as elo_clearance_file:
        rencontres_list = list(csv.DictReader(rencontres_file))
        elo_clearance = elo_clearance_file.read().split("\n")
        elo_clearance = elo_clearance[0:len(elo_clearance)-1]
        
        for decks_filename, players_filename, elo_label in zip(decks_filenames, players_filenames, elo_labels):
            players_data, decks_data = generateELO(rencontres_list, elo_clearance, elo_label)

            with open(players_filename, mode="w", encoding="utf-8") as players_file:
                json.dump(players_data, players_file, ensure_ascii=False)

            with open(decks_filename, mode="w", encoding="utf-8") as decks_file:
                json.dump(decks_data, decks_file, ensure_ascii=False)

    import get_list_players
    get_list_players.writing_list_players_file("players.json", "list_players.csv")
    print("players generated")

    import get_list_sets
    get_list_sets.writing_list_sets_file("decks.json", "list_magic_sets.csv")
    print("sets generated")

    import get_list_decks
    get_list_decks.writing_list_decks_file("decks.json", "list_decks.csv")
    print("decks generated")

    import get_sorted_decks
    import get_sorted_decks_tournois
    import get_sorted_players
    import get_sorted_players_tournois

    get_sorted_decks.writing_sorted_decks("decks.json","sorted_decks.csv")
    get_sorted_decks_tournois.writing_sorted_decks_tournois("decks.json","sorted_decks_tournois.csv")
    get_sorted_players.writing_sorted_players("players.json", "sorted_players.csv",elo_clearance_filename)
    get_sorted_players_tournois.writing_sorted_players_tournois("players.json","sorted_players_tournois.csv",elo_clearance_filename)







