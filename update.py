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

def readPlayer(player, players_global, data_changed, elo_clearance, elo_clearances, is_trusted):
    """Returns the json of the player "player" in players_global and stores whether the player have agreed to have a personal ELO in elo_clearance. If player is not in players_global, returns a new entry and adds "players" to data_changed.
    
    player: the name of the player.
    players_global: the data base of all players data.
    data_changed: tracks new entries in the data_base.
    elo_clearance: list of players that have agreed to have a personal ELO.
    elo_clearances: list of clearances.
    is_trusted: bypass input verification.
    """
    elo_clearance = player in elo_clearance
    elo_clearances.append(elo_clearance)
    try:
        return players_global[player]
    except KeyError:
        is_player_correct = "Y"
        if not is_trusted:
            is_player_correct = input(f"Is {player} a new player? (Y/n)")
        if is_player_correct == "Y" or is_player_correct == "y" or is_player_correct == "" or is_trusted:
            if elo_clearance:
                new_player = getDefaultPlayerELO()
            else:
                new_player = getDefaultPlayerNoELO()
            players_global[player] = new_player
            data_changed.add("players")
            return new_player
        else:
            raise Exception("Bad player name")

def readSet(magic_set, decks_global, data_changed, is_trusted):
    """Returns the json of the set "magic_set" in decks_global. If magic_set is not in decks_global, returns a new entry and adds "sets" to data_changed.
    
    magic_set: the name of the set.
    decks_global: the data base of all decks data, organized in sets.
    data_changed: tracks new entries in the data_base.
    is_trusted: bypass input verification.
    """
    try:
        return decks_global[magic_set]
    except KeyError:
        is_set_correct = "Y"
        if not is_trusted:
            is_set_correct = input(f"Is {magic_set} a correct magic set? (Y/n)")
        magic_set_work = dict()
        if is_set_correct == "Y" or is_set_correct == "y" or is_set_correct == "" or is_trusted:
            decks_global[magic_set] = magic_set_work
            data_changed.add("sets")
            return magic_set_work
        else:
            raise Exception("Bad set name")

def readDeck(deck, decks_global, magic_set_work, data_changed, is_trusted):
    """Returns the json of the deck "deck" in decks_global[magic_set_work]. If deck is not in decks_global[magic_set_work], returns a new entry and adds "decks" to data_changed.
    
    deck: the name of the deck.
    decks_global: the data base of all decks data, organized in sets.
    magic_set_work: the name of the set of "deck"
    data_changed: tracks new entries in the data_base.
    is_trusted: bypass input verification.
    """
    try:
        return magic_set_work[deck]
    except KeyError:
        is_deck_correct = "Y"
        if not is_trusted:
            is_deck_correct = input(f"Is {deck} a correct deck from the set {magic_set}? (Y/n)")
        if is_deck_correct == "Y" or is_deck_correct == "y" or is_deck_correct == "" or is_trusted:
            new_deck = getDefaultDeck()
            magic_set_work[deck] = new_deck
            data_changed.add("decks")
            return new_deck
        else:
            raise Exception("Bad deck name")

def computeELOmixte(decks, players, data_label, elo_clearances):
    """Returns a list of the mixed elo.
    """
    elo_mixed = []
    for index in range(2):
        deck_elo = decks[index][data_label]["ELO"]
        if elo_clearances[index]:
            player_elo = players[index][data_label]["ELO"]
        else:
            player_elo = deck_elo
        elo_mixed.append(ALPHA * deck_elo + (1 - ALPHA) * player_elo)
    return elo_mixed

def computeELOmodifier(scores, elo_mixed):
    """Returns a list of the ELO modifiers.
    """
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
    return elo_modifier

def computeResult(scores, index):
    """Return the result given the scores.
    """
    opp_index = 1 - index
    if scores[index] > scores[opp_index]:
        return "win"
    elif scores[index] < scores[opp_index]:
        return "lose"
    else:
        return "draw"

def updateDeck(deck, opponent_deck_name, player_name, date, result, elo_modifier):
    """Updates the data of the deck "deck".
    """
    new_deck_elo = deck["ELO"] + K_DECKS * elo_modifier
    deck["ELO"] = new_deck_elo
    deck["historic"][date] = new_deck_elo
    deck["match number"] += 1
    if not player_name in deck["players"].keys():
        deck["players"][player_name] = {"number" : 0, "win" : 0, "draw" : 0, "lose" : 0}
    if not opponent_deck_name in deck["decks fought"].keys():
        deck["decks fought"][opponent_deck_name] = {"number" : 0, "win" : 0, "draw" : 0, "lose" : 0}
    deck["players"][player_name]["number"] += 1
    deck["decks fought"][opponent_deck_name]["number"] += 1
    if result == "win":
        deck["players"][player_name]["win"] += 1
        deck["decks fought"][opponent_deck_name]["win"] += 1
    elif result == "lose":
        deck["players"][player_name]["lose"] += 1
        deck["decks fought"][opponent_deck_name]["lose"] += 1
    else:
        deck["players"][player_name]["draw"] += 1
        deck["decks fought"][opponent_deck_name]["draw"] += 1

def updatePlayer(player, elo_clearance, opponent_name, deck_name, date, result, elo_modifier):
    """Updates the data of the player "player".
    """
    if elo_clearance:
        new_player_elo = player["ELO"] + K_PLAYER * elo_modifier
        player["ELO"] = new_player_elo
        player["historic"][date] = new_player_elo
    player["match number"] += 1
    if not deck_name in player["decks played"].keys():
        player["decks played"][deck_name] = {"number" : 0, "win" : 0, "draw" : 0, "lose" : 0}
    if not opponent_name in player["players fought"].keys():
        player["players fought"][opponent_name] = {"number" : 0, "win" : 0, "draw" : 0, "lose" : 0}
    player["decks played"][deck_name]["number"] += 1
    player["players fought"][opponent_name]["number"] += 1
    if result == "win":
        player["decks played"][deck_name]["win"] += 1
        player["players fought"][opponent_name]["win"] += 1
    elif result == "lose":
        player["decks played"][deck_name]["lose"] += 1
        player["players fought"][opponent_name]["lose"] += 1
    else:
        player["decks played"][deck_name]["draw"] += 1
        player["players fought"][opponent_name]["draw"] += 1

def updateData(decks, players, decks_names, players_names, scores, date, elo_clearances, data_label):
    """Updates the data in decks and players.
    """
    elo_mixed = computeELOmixte(decks, players, data_label, elo_clearances)
    elo_modifier = computeELOmodifier(scores, elo_mixed)
    for index in range(2):
        opp_index = 1 - index
        result = computeResult(scores, index)
        deck = decks[index][data_label]
        player = players[index][data_label]
        player_name = players_names[index]
        deck_name = decks_names[index]
        opponent_name = players_names[opp_index]
        opponent_deck_name = decks_names[opp_index]
        
        updateDeck(deck, opponent_deck_name, player_name, date, result, elo_modifier[index])
        updatePlayer(player, elo_clearances[index], opponent_name, deck_name, date, result, elo_modifier[index])

def updateDataDecks(decks, decks_names, players_names, scores, date, data_label):
    """Updates the data in decks and players.
    """
    elo_decks = []
    elo_decks.append(decks[0][data_label]["ELO"])
    elo_decks.append(decks[1][data_label]["ELO"])
    elo_modifier = computeELOmodifier(scores, elo_decks)
    for index in range(2):
        opp_index = 1 - index
        result = computeResult(scores, index)
        deck = decks[index][data_label]
        player_name = players_names[index]
        deck_name = decks_names[index]
        opponent_name = players_names[opp_index]
        opponent_deck_name = decks_names[opp_index]
        
        updateDeck(deck, opponent_deck_name, player_name, date, result, elo_modifier[index])

def processRencontre(rencontre, players_global, elo_clearance, decks_global, is_trusted):
    """Process a match and update the ELO of decks and players involved.
    Return which among "decks", "players" and "magic_sets" has a new entry.
    
    rencontre: a match that happend at Date between JoueureuseA playing DeckA of SetA and JoueureuseB playing DeckB of SetB. The score is ScoreA to ScoreB. Tournois != "" if the match took place during a tournament.
    elo_clearnace : list of which players want to have a ELO.
    is_trusted: is true if the data in rencontre don't need double checking when not already in the database.
    """
    data_changed = set()
    players = []
    players_names = []
    decks = []
    decks_names = []
    scores = []
    date = rencontre["Date"]
    elo_clearances = []
    for suffix in ["A", "B"]:
        player = rencontre[f"Joueureuse{suffix}"]
        players_names.append(player)
        deck = rencontre[f"Deck{suffix}"]
        decks_names.append(deck)
        magic_set = rencontre[f"Set{suffix}"]
        scores.append(rencontre[f"Score{suffix}"])
        
        players.append(readPlayer(player, players_global, data_changed, elo_clearance, elo_clearances, is_trusted))
        magic_set_work = readSet(magic_set, decks_global, data_changed, is_trusted)
        decks.append(readDeck(deck, decks_global, magic_set_work, data_changed, is_trusted))

    data_to_modify = [ "Data" ]
    if rencontre["Tournois"]:
        data_to_modify.append("Data Tournoi")

    for data_label in data_to_modify:
        updateData(decks, players, decks_names, players_names, scores, date, elo_clearances, data_label)
    
    return data_changed

def processRencontreDecksOnly(rencontre, decks_global, is_trusted):
    """Process a match and update the ELO of decks involved.
    Return which among "decks" and "magic_sets" has a new entry.
    
    rencontre: a match that happend at Date between JoueureuseA playing DeckA of SetA and JoueureuseB playing DeckB of SetB. The score is ScoreA to ScoreB. Tournois != "" if the match took place during a tournament.
    is_trusted: is true if the data in rencontre don't need double checking when not already in the database.
    """
    data_changed = set()
    players_names = []
    decks = []
    decks_names = []
    scores = []
    date = rencontre["Date"]
    elo_clearances = []
    for suffix in ["A", "B"]:
        player = rencontre[f"Joueureuse{suffix}"]
        players_names.append(player)
        deck = rencontre[f"Deck{suffix}"]
        decks_names.append(deck)
        magic_set = rencontre[f"Set{suffix}"]
        scores.append(rencontre[f"Score{suffix}"])
        
        magic_set_work = readSet(magic_set, decks_global, data_changed, is_trusted)
        decks.append(readDeck(deck, decks_global, magic_set_work, data_changed, is_trusted))

    data_to_modify = [ "Data" ]
    if rencontre["Tournois"]:
        data_to_modify.append("Data Tournoi")

    for data_label in data_to_modify:
        updateDataDecks(decks, decks_names, players_names, scores, date, data_label)
    
    return data_changed

def checkClearance(players, elo_clearance):
    """Return wether all players is "players" are in elo_clearance
    """
    resu = True
    for player in players:
        resu = resu & (player in elo_clearance)
    return resu

def processRencontreMixtOnly(rencontre, players_global, elo_clearance, decks_global, is_trusted):
    """Process a match and update the ELO of decks and players involved when both opponent agreed to have a ELO.
    Return which among "decks", "players" and "magic_sets" has a new entry
    
    rencontre: a match that happend at Date between JoueureuseA playing DeckA of SetA and JoueureuseB playing DeckB of SetB. The score is ScoreA to ScoreB. Tournois != "" if the match took place during a tournament.
    elo_clearnace : table of which players want to have a ELO.
    is_trusted: is true if the data in rencontre don't need double checking when not already in the database.
    """
    data_changed = set()
    players = []
    players_names = []
    decks = []
    decks_names = []
    magic_set_names = []
    scores = []
    date = rencontre["Date"]
    elo_clearances = [True,True]
    for suffix in ["A", "B"]:
        player = rencontre[f"Joueureuse{suffix}"]
        players_names.append(player)
        deck = rencontre[f"Deck{suffix}"]
        decks_names.append(deck)
        magic_set = rencontre[f"Set{suffix}"]
        magic_set_names.append(magic_set)
        scores.append(rencontre[f"Score{suffix}"])
    
    if not checkClearance(players_names, elo_clearance):
        return set()
    for index in range(2):
        players.append(readPlayer(players_names[index], players_global, data_changed, elo_clearance, [], is_trusted))
        magic_set_work = readSet(magic_set_names[index], decks_global, data_changed, is_trusted)
        decks.append(readDeck(decks_names[index], decks_global, magic_set_work, data_changed, is_trusted))

    data_to_modify = [ "Data" ]
    if rencontre["Tournois"]:
        data_to_modify.append("Data Tournoi")

    for data_label in data_to_modify:
        updateData(decks, players, decks_names, players_names, scores, date, elo_clearances, data_label)
    
    return data_changed

def computeELO(rencontres, players, elo_clearance, decks, is_trusted):
    data_changed = set()
    for rencontre in rencontres:
        data_changed = data_changed | processRencontre(rencontre, players, elo_clearance, decks, is_trusted)
    return data_changed

def computeELODecksOnly(rencontres, players, elo_clearance, decks, is_trusted):
    for rencontre in rencontres:
        processRencontreDecksOnly(rencontre, players, elo_clearance, decks, is_trusted)

def computeELOMixtOnly(rencontres, players, elo_clearance, decks, is_trusted):
    data_changed = set()
    for rencontre in rencontres:
        processRencontreMixtOnly(rencontre, players, elo_clearance, decks, is_trusted)

if __name__ == "__main__" :
    
    decks_filenames = ["decks.json", "decks_decks_only.json", "decks_mixt_only.json"]
    players_filename = ["players.json", "players_decks_only.json", "players_mixt_only.json"]
    elo_labels = ["g", "d", "m"]
    elo_clearance_filename = "players_ELO_clearance.txt"
    rencontres_filename = "rencontres.csv"
    
    with open(rencontres_file_name, newline="", encoding='utf-8') as rencontre_csv_file, open(elo_clearance_file_name, encoding='utf-8') as elo_clearance_file:
        rencontres_csv = csv.DictReader(rencontre_csv_file)
        elo_clearance = elo_clearance_file.read().split("\n")
        elo_clearance = elo_clearance[0:len(elo_clearance)-1]
        for decks_filename, players_filename, elo_label in zip(decks_filenames, players_filenames, elo_labels):
            with open(players_file_name, encoding="utf-8") as players_file, open(decks_file_name, encoding="utf-8") as decks_file:
                players = json.load(players_file)
                decks = json.load(decks_file)
                if elo_label == "g":
                    data_changed = computeELO(rencontres, players, elo_clearance, decks, False)
                elif elo_label == "d":
                    computeELODecksOnly(rencontres, players, elo_clearance, decks, False)
                elif elo_label == "m":
                    computeELOMixtOnly(rencontres, players, elo_clearance, decks, False)
                else:
                    raise Exception("Bad elo_label")
        
            with open(players_file_name,"w", encoding="utf-8") as players_file, open(decks_file_name,"w", encoding="utf-8") as decks_file :#, encoding="utf-8"
                json.dump(players, players_file, ensure_ascii=False)
                json.dump(decks, decks_file, ensure_ascii=False)
    
    with open(rencontres_file_name, newline="") as rencontres_fraiches_file, open("rencontres.csv", "a", newline="") as rencontres_file :
        rencontres_fraiches = csv.DictReader(rencontres_fraiches_file)
        fieldnames = rencontres_fraiches.fieldnames
        writer = csv.DictWriter(rencontres_file,fieldnames=fieldnames)
        writer.writerows(rencontres_fraiches)
        
    with open(rencontres_file_name, newline="", mode="w") as rencontres_fraiches_file :
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
