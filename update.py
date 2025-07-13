import csv
import json

K_PLAYER = 20
K_DECKS = 10
ALPHA = 0.7

def getDefaultPlayerDataELO():
    return { "ELO" : 100, "match number" : 0, "decks played" : {}, "players fought" : {}, "historic" : {} }

def getDefaultPlayerDataNoELO():
    return { "match number" : 0, "decks played" : {}, "players fought" : {}}

def getDefaultDeckData():
    return { "ELO" : 100, "match number" : 0, "players" : {}, "decks fought" : {}, "historic" : {} }

def getDefaultPlayerELO():
    return { "Data" : getDefaultPlayerDataELO(), "Data Tournoi" : getDefaultPlayerDataELO() }
    
def getDefaultPlayerNoELO():
    return { "Data" : getDefaultPlayerDataNoELO(), "Data Tournoi" : getDefaultPlayerDataNoELO() }

def getDefaultDeck():
    return { "Data" : getDefaultDeckData(), "Data Tournoi" : getDefaultDeckData() }

def getEloModifier(won, elo_player, elo_opponent):
    """Returns the pourcentage to add to the ELO of a given player.

    won: 1 if player won, 0 if lost and 0.5 if draw.
    """
    return won - 1 / ( 1 + 10 ** ((elo_opponent - elo_player) / 400))

def processRencontre(rencontre, players_global, ELO_clearance, decks_global, is_trusted):
    """Process a match and update the ELO of decks and players involved
    Return which among "decks", "players" and "magic_sets" has a new entry
    
    rencontre: a match that happend at Date between JoueureuseA playing DeckA of SetA and JoueureuseB playing DeckB of SetB. The score is ScoreA to ScoreB. Tournois != "" if the match took place during a tournament.
    ELO_clearnace : table of which players want to have a ELO.
    is_trusted: is true if the verifications that the data in rencontre doesn't need double checking when not already in the database.
    """
    data_changed = set()
    players = []
    players_names = []
    decks = []
    decks_names = []
    scores = []
    for suffix in ["A", "B"]:
        player = rencontre[f"Joueureuse{suffix}"]
        players_names.append(player)
        deck = rencontre[f"Deck{suffix}"]
        decks_names.append(deck)
        magic_set = rencontre[f"Set{suffix}"]
        try:
            players.append(players_global[player])
        except KeyError:
            is_player_correct = "Y"
            if not is_trusted:
                is_player_correct = input(f"Is {player} a new player? (Y/n)")
            if is_player_correct == "Y" or is_player_correct == "y" or is_player_correct == "" or is_trusted:
                if player in ELO_clearance:
                    new_player = getDefaultPlayerELO()
                else:
                    new_player = getDefaultPlayerNoELO()
                players_global[player] = new_player
                players.append(new_player)
                data_changed.add("players")
            else:
                raise Exception("Bad player name")
        try:
            magic_set_work = decks_global[magic_set]
        except KeyError:
            is_set_correct = "Y"
            if not is_trusted:
                is_set_correct = input(f"Is {magic_set} a correct magic set? (Y/n)")
            magic_set_work = dict()
            if is_set_correct == "Y" or is_set_correct == "y" or is_set_correct == "" or is_trusted:
                decks_global[magic_set] = magic_set_work
                data_changed.add("sets")
            else:
                raise Exception("Bad set name")
        try:
            decks.append(magic_set_work[deck])
        except KeyError:
            is_deck_correct = "Y"
            if not is_trusted:
                is_deck_correct = input(f"Is {deck} a correct deck from the set {magic_set}? (Y/n)")
            if is_deck_correct == "Y" or is_deck_correct == "y" or is_deck_correct == "" or is_trusted:
                new_deck = getDefaultDeck()
                magic_set_work[deck] = new_deck
                decks.append(new_deck)
                data_changed.add("decks")
            else:
                raise Exception("Bad deck name")
        scores.append(rencontre[f"Score{suffix}"])

    data_to_modify = [ "Data" ]
    if rencontre["Tournois"]:
        data_to_modify.append("Data Tournoi")

    for data_label in data_to_modify:
        elo_mixed = []
        for index in range(2):
            deck_elo = decks[index][data_label]["ELO"]
            if players_names[index] in ELO_clearance:
                player_elo = players[index][data_label]["ELO"]
            else:
                player_elo = deck_elo
            elo_mixed.append(ALPHA * deck_elo + (1 - ALPHA) * player_elo)

        elo_modifier = []
        for index in range(2):
            opp_index = 1 - index
            if scores[index] > scores[opp_index]:
                won = 1.
            elif scores[index] < scores[opp_index]:
                won = 0.
            else:
                won = .5
            elo_modifier.append(getEloModifier(won, elo_mixed[index], elo_mixed[opp_index]))

        # Modifying elos
        for index in range(2):
            opp_index = 1 - index
            deck = decks[index][data_label]
            player = players[index][data_label]
            player_name = players_names[index]
            deck_name = decks_names[index]
            new_deck_elo = deck["ELO"] + K_DECKS * elo_modifier[index]
            if player_name in ELO_clearance:
                new_player_elo = player["ELO"] + K_PLAYER * elo_modifier[index]
            opponent_name = players_names[opp_index]
            opponent_deck_name = decks_names[opp_index]
            
            # decks and player are storing references to the data in the global datas.
            # we first update the data of the deck
            deck["ELO"] = new_deck_elo
            deck["match number"] += 1
            if not player_name in deck["players"].keys():
                deck["players"][player_name] = 0
            deck["players"][player_name] += 1
            if not opponent_deck_name in deck["decks fought"].keys():
                deck["decks fought"][opponent_deck_name] = {"win" : 0, "draw" : 0, "lose" : 0}
            if scores[index] > scores[opp_index]:
                deck["decks fought"][opponent_deck_name]["win"] += 1
            elif scores[index] < scores[opp_index]:
                deck["decks fought"][opponent_deck_name]["lose"] += 1
            else:
                deck["decks fought"][opponent_deck_name]["draw"] += 1
            deck["historic"][rencontre["Date"]] = new_deck_elo
            # then we update the data of the player
            if player_name in ELO_clearance:
                player["ELO"] = new_player_elo
                player["historic"][rencontre["Date"]] = new_player_elo
            player["match number"] += 1
            if not deck_name in player["decks played"].keys():
                player["decks played"][deck_name] = 0
            if not opponent_name in player["players fought"].keys():
                player["players fought"][opponent_name] = {"win" : 0, "draw" : 0, "lose" : 0}
            if scores[index] > scores[opp_index]:
                player["players fought"][opponent_name]["win"] += 1
            elif scores[index] < scores[opp_index]:
                player["players fought"][opponent_name]["lose"] += 1
            else:
                player["players fought"][opponent_name]["draw"] += 1
            player["decks played"][deck_name] += 1
    return data_changed

if __name__ == "__main__" :

    with open("rencontres_fraiches.csv", newline="", encoding='utf-8') as rencontre_csv_file, open("players.json", encoding="utf-8") as players_file, open("decks.json", encoding="utf-8") as decks_file, open("players_ELO_clearance.txt", encoding='utf-8') as ELO_clearance_file:
        rencontres_csv = csv.DictReader(rencontre_csv_file)
        ELO_clearance = ELO_clearance_file.read().split("\n")
        ELO_clearance = ELO_clearance[0:len(ELO_clearance)-1]
        players = json.load(players_file)
        decks = json.load(decks_file)
        data_changed = set()
        for rencontre in rencontres_csv:
            data_changed = data_changed | processRencontre(rencontre, players, ELO_clearance, decks, False)

    with open("players.json","w") as players_file, open("decks.json","w") as decks_file :#, encoding="utf-8"
        json.dump(players, players_file, ensure_ascii=False)
        json.dump(decks, decks_file, ensure_ascii=False)
    
    with open("rencontres_fraiches.csv", newline="") as rencontres_fraiches_file, open("rencontres.csv", "a", newline="") as rencontres_file :
        rencontres_fraiches = csv.DictReader(rencontres_fraiches_file)
        fieldnames = rencontres_fraiches.fieldnames
        writer = csv.DictWriter(rencontres_file,fieldnames=fieldnames)
        writer.writerows(rencontres_fraiches)
        
    with open("rencontres_fraiches.csv", newline="", mode="w") as rencontres_fraiches_file :
        writer = csv.writer(rencontres_fraiches_file)
        writer.writerow(fieldnames)
    
    if "players" in data_changed:
        import get_list_players
        get_list_players.writing_list_players_file("players.json", "list_players.csv")
        print("players updated")
    
    if "sets" in data_changed:
        import get_list_sets
        get_list_sets.writing_list_sets_file("decks.json", "list_magic_sets.csv")
        print("sets updated")
    
    if "decks" in data_changed:
        import get_list_decks
        get_list_decks.writing_list_decks_file("decks.json", "list_decks.csv")
        print("decks updated")

    import get_sorted_decks
    import get_sorted_decks_tournois
    import get_sorted_players
    import get_sorted_players_tournois

    get_sorted_decks.writing_sorted_decks("decks.json","sorted_decks.csv")
    get_sorted_decks_tournois.writing_sorted_decks_tournois("decks.json","sorted_decks_tournois.csv")
    get_sorted_players.writing_sorted_players("players.json", "sorted_players.csv","players_ELO_clearance.txt")
    get_sorted_players_tournois.writing_sorted_players_tournois("players.json","sorted_players_tournois.csv","players_ELO_clearance.txt")
