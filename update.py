import csv
import json

K_PLAYER = 20
K_DECKS = 10
ALPHA = 0.7

def getDefaultPlayerELO():
    return { "ELO" : 100, "ELO Tournoi" : 100 }

def getDefaultDeckELO():
    return { "ELO" : 100, "ELO Tournoi" : 100 }

def getEloModifier(won, elo_player, elo_opponent):
    """Returns the pourcentage to add to the ELO of a given player.

    won: 1 if player won, 0 if lost and 0.5 if draw.
    """
    return won - 1 / ( 1 + 10 ** ((elo_opponent - elo_player) / 400))

def processRencontre(rencontre, players_global, decks_global, is_trusted):
    data_changed = set()
    players = []
    decks = []
    scores = []
    for suffix in ["A", "B"]:
        player = rencontre[f"Joueureuse{suffix}"]
        deck = rencontre[f"Deck{suffix}"]
        magic_set = rencontre[f"Set{suffix}"]
        try:
            players.append(players_global[player])
        except KeyError:
            is_player_correct = "Y"
            if not is_trusted:
                is_player_correct = input(f"Is {player} a new player? (Y/n)")
            if is_player_correct == "Y" or is_player_correct == "y" or is_player_correct == "" or is_trusted:
                new_player = getDefaultPlayerELO()
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
                new_deck = getDefaultDeckELO()
                magic_set_work[deck] = new_deck
                decks.append(new_deck)
                data_changed.add("decks")
            else:
                raise Exception("Bad deck name")
        scores.append(rencontre[f"Score{suffix}"])

    elo_to_modify = [ "ELO" ]
    if rencontre["Tournois"]:
        elo_to_modify.append("ELO Tournoi")

    for elo_label in elo_to_modify:
        elo_mixed = []
        for index in range(2):
            deck_elo = decks[index][elo_label]
            player_elo = players[index][elo_label]
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
            old_deck_elo = decks[index][elo_label]
            old_player_elo = players[index][elo_label]
            # decks and player are storing references to the data in the global datas.
            decks[index][elo_label] += K_DECKS * elo_modifier[index]
            players[index][elo_label] += K_PLAYER * elo_modifier[index]
    return data_changed

if __name__ == "__main__" :

    with open("rencontres_fraiches.csv", newline="") as rencontre_csv_file, open("players.json") as players_file, open("decks.json") as decks_file :
        rencontres_csv = csv.DictReader(rencontre_csv_file)
        players = json.load(players_file)
        decks = json.load(decks_file)
        data_changed = set()
        for rencontre in rencontres_csv:
            data_changed = data_changed | processRencontre(rencontre, players, decks, False)

    with open("players.json","w") as players_file, open("decks.json","w") as decks_file :
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
    get_sorted_players.writing_sorted_players("players.json", "sorted_players.csv")
    get_sorted_players_tournois.writing_sorted_players_tournois("players.json","sorted_players_tournois.csv")