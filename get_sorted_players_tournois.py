import csv
import json

def writing_sorted_players_tournois(players_file_name, sorted_players_tournois_file_name):
    with open(players_file_name) as players_file, open(sorted_players_tournois_file_name, newline ="", mode = "w") as sorted_players_csv :
        players = json.load(players_file)
        players_elo = []
        for player,player_elo in players.items():
            players_elo.append([player,player_elo["ELO Tournoi"]])
        writer = csv.writer(sorted_players_csv)
        writer.writerow(["Joueureuses","ELO"])
        for player in sorted(players_elo,key = lambda x : x[1]) :
            writer.writerow(player)

if __name__ == "__main__":
    writing_sorted_players_tournois("players.json","sorted_players_tournois.csv")