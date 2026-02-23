import csv
import json

from files import *

def writing_sorted_decks(decks_file_name, tournois):
    if tournois:
        data_label = "Data Tournoi"
        file = SORTED_DECKS_TOURNOIS
    else:
        data_label = "Data"
        file = SORTED_DECKS
    with open(decks_file_name) as decks_file, open(file, newline ="", mode = "w") as sorted_decks_csv :
        magic_sets = json.load(decks_file)
        decks_elo = []
        for magic_set,magic_set_decks in magic_sets.items():
            for deck,deck_value in magic_set_decks["Decks"].items():
                decks_elo.append([deck,magic_set,deck_value[data_label]["ELO"]])
        writer = csv.writer(sorted_decks_csv)
        writer.writerow(["Decks","Set","ELO"])
        for deck in sorted(decks_elo,key = lambda x : x[2]) :
            writer.writerow(deck)

def writing_sorted_players(players_file_name, tournois):
    if tournois:
        data_label = "Data Tournoi"
        file = SORTED_PLAYERS_TOURNOIS
    else:
        data_label = "Data"
        file = SORTED_PLAYERS
    with open(players_file_name) as players_file, open(file, newline ="", mode = "w") as sorted_players_csv, open(CLEARANCE) as ELO_clearance_file:
        players = json.load(players_file)
        ELO_clearance = ELO_clearance_file.read().split("\n")
        ELO_clearance = ELO_clearance[0:len(ELO_clearance)-1]
        players_elo = []
        for player in ELO_clearance:
            players_elo.append([player,players[player]["Data"]["ELO"]])
        writer = csv.writer(sorted_players_csv)
        writer.writerow(["Joueureuses","ELO"])
        for player in sorted(players_elo,key = lambda x : x[1]) :
            writer.writerow(player)
