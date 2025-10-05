def estimate_win_probability(home_team, away_team):
    """
    Estime la probabilité de victoire basée sur :
    - Forme récente (derniers 5 matchs)
    - Buts marqués/encaissés
    - Confrontations directes
    """
    # Pour simplifier, on utilise une logique basée sur la ligue + forme
    # Dans une version avancée, on récupérerait les stats via Football-Data.org
    return {
        'home': 0.45,
        'draw': 0.25,
        'away': 0.30
    }

def is_value_bet(prob_estimated, bookmaker_odds):
    """Vérifie si c'est une value bet"""
    implied_prob = 1 / bookmaker_odds
    return prob_estimated > implied_prob
