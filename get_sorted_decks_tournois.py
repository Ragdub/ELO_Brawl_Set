import csv
import json
with open("decks.json") as decks_file, open("sorted_decks_tournois.csv", newline ="", mode = "w") as sorted_decks_csv :
    magic_sets = json.load(decks_file)
    decks_elo = []
    for magic_set,magic_set_decks in magic_sets.items():
        for deck,deck_value in magic_set_decks.items():
            decks_elo.append([deck,magic_set,deck_value["ELO Tournoi"]])
    writer = csv.writer(sorted_decks_csv)
    writer.writerow(["Decks","Set","ELO"])
    for deck in sorted(decks_elo,key = lambda x : x[2]) :
        writer.writerow(deck)
