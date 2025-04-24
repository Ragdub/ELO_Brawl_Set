import datetime
import update

def generateELO(rencontres_list):
    global_players_data = {}
    global_decks_data = {}
    for rencontre in rencontres_list:
        update.processRencontre(rencontre, global_players_data, global_decks_data)

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
        json.dump(players_data, players_file)

    with open(decks_filename, mode="w") as decks_file:
        json.dump(decks_data, decks_file)








