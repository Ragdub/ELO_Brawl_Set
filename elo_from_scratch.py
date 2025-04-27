import datetime
import update


def generateELO(rencontres_list):
    global_players_data = {}
    global_decks_data = {}
    for rencontre in rencontres_list:
        update.processRencontre(rencontre, global_players_data, global_decks_data, True)

    return global_players_data, global_decks_data

if __name__ == '__main__':
    import json
    import csv

    decks_filename = "decks.json"
    players_filename = "players.json"
    rencontres_filename = "rencontres.csv"

    with open(rencontres_filename, newline="") as rencontres_file:
        rencontres_list = csv.DictReader(rencontres_file)

        players_data, decks_data = generateELO(rencontres_list)

    with open(players_filename, mode="w") as players_file:
        json.dump(players_data, players_file, ensure_ascii=False)

    with open(decks_filename, mode="w") as decks_file:
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

    get_sorted_decks.writing_sorted_decks("decks.json","list_magic_sets.csv")
    get_sorted_decks_tournois.writing_sorted_decks_tournois("decks.json","sorted_decks_tournois.csv")
    get_sorted_players.writing_sorted_players("players.json", "sorted_players.csv")
    get_sorted_players_tournois.writing_sorted_players_tournois("players.json","sorted_players_tournois.csv")







