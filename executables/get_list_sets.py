import csv
import json

def writing_list_sets_file(magic_sets_file_name, list_magic_sets_file_name):
    with open(magic_sets_file_name) as decks_file, open(list_magic_sets_file_name, newline ="", mode = "w") as list_magic_sets_csv :
        magic_sets = json.load(decks_file)
        
        writer = csv.writer(list_magic_sets_csv)
        writer.writerow(["Set"])
        for magic_set in sorted(magic_sets) :
            writer.writerow([magic_set])

if __name__ == "__main__":
    writing_list_sets_file("decks.json", "list_magic_sets.csv")
