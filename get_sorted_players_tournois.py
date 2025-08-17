import csv
import json

def writing_sorted_players_tournois(players_file_name, sorted_players_tournois_file_name, ELO_clearance_file_name):
    with open(players_file_name) as players_file, open(sorted_players_tournois_file_name, newline ="", mode = "w") as sorted_players_csv, open(ELO_clearance_file_name) as ELO_clearance_file:
        ELO_clearance = ELO_clearance_file.read().split("\n")
        ELO_clearance = ELO_clearance[0:len(ELO_clearance)-1]
        players = json.load(players_file)
        players_elo = []
        for player in ELO_clearance:
            players_elo.append([player,players[player]["Data Tournoi"]["ELO"]])
        writer = csv.writer(sorted_players_csv)
        writer.writerow(["Joueureuses","ELO"])
        for player in sorted(players_elo,key = lambda x : x[1]) :
            writer.writerow(player)

if __name__ == "__main__":
    writing_sorted_players_tournois("players.json","sorted_players_tournois.csv","players_ELO_clearance.txt")
