import os

# Base de données
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Football-Data.org
FOOTBALL_DATA_KEY = os.environ.get('FOOTBALL_DATA_KEY', '')

# Ligues supportées (ID Football-Data.org)
LEAGUES = {
    'PL': 2021,   # Premier League
    'SA': 2019,   # Serie A
    'BL': 2002,   # Bundesliga
    'LL': 2014,   # La Liga
    'FL': 2015,   # Ligue 1
}
