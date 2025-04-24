import csv
import json

def writing_list_decks_file(decks_file_name, list_decks_file_name):
    with open(decks_file_name) as decks_file, open(list_decks_file_name, newline ="", mode = "w") as list_decks_csv :
        magic_sets = json.load(decks_file)
        decks = set()
        for magic_set_decks in magic_sets.values():
            for deck in magic_set_decks:
                decks.add(deck)
        writer = csv.writer(list_decks_csv)
        writer.writerow(["Decks"])
        for deck in sorted(decks) :
            writer.writerow([deck])

if __name__ == "__main__":
    writing_list_decks_file("decks.json", "list_decks.csv")
