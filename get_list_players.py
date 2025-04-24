import csv
import json

def writing_list_players_file(players_file_name, list_players_file_name):
    with open(players_file_name) as players_file, open(list_players_file_name, newline ="", mode = "w") as list_players_csv :
        players = json.load(players_file)
        writer = csv.writer(list_players_csv)
        writer.writerow(["Joueureuses"])
        for player in sorted(players.keys()) :
            writer.writerow([player])

if __name__ == "__main__":
    writing_list_players_file("players.json", "list_players.csv")
