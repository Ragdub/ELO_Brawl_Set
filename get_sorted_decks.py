import csv
import json

def writing_sorted_decks(decks_file_name, sorted_decks_file_name):
    with open(decks_file_name) as decks_file, open(sorted_decks_file_name, newline ="", mode = "w") as sorted_decks_csv :
        magic_sets = json.load(decks_file)
        decks_elo = []
        for magic_set,magic_set_decks in magic_sets.items():
            for deck,deck_value in magic_set_decks.items():
                decks_elo.append([deck,magic_set,deck_value["Data"]["ELO"]])
        writer = csv.writer(sorted_decks_csv)
        writer.writerow(["Decks","Set","ELO"])
        for deck in sorted(decks_elo,key = lambda x : x[2]) :
            writer.writerow(deck)

if __name__ == "__main__":
    writing_sorted_decks("decks.json","sorted_decks.csv")
