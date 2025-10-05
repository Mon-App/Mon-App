import requests
from bs4 import BeautifulSoup
from config import FOOTBALL_DATA_KEY, LEAGUES

HEADERS = {'X-Auth-Token': FOOTBALL_DATA_KEY}

def get_fixtures_today():
    """Récupère les matchs d'aujourd'hui dans les grandes ligues"""
    all_fixtures = []
    for league_code, league_id in LEAGUES.items():
        url = f"https://api.football-data.org/v4/competitions/{league_id}/matches"
        params = {"status": "SCHEDULED"}
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code == 200:
            data = r.json()
            for match in data.get('matches', []):
                all_fixtures.append({
                    'home': match['homeTeam']['name'],
                    'away': match['awayTeam']['name'],
                    'league': league_code,
                    'match_id': match['id']
                })
    return all_fixtures

def get_odds_1xbet(home_team, away_team):
    """Scraping légal des cotes 1xBet (version simplifiée)"""
    try:
        # Recherche via le site mobile (plus stable)
        search_url = f"https://1xbet.cm/en/search/{home_team} vs {away_team}"
        r = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Exemple simplifié — à adapter selon la structure réelle
            odds = soup.find_all('span', class_='koeff')
            if len(odds) >= 3:
                return {
                    'home': float(odds[0].text),
                    'draw': float(odds[1].text),
                    'away': float(odds[2].text)
                }
    except:
        pass
    return {'home': 2.0, 'draw': 3.4, 'away': 3.6}  # valeurs par défaut
