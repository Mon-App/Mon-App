from flask import Flask, render_template_string, jsonify
from collector import get_fixtures_today, get_odds_1xbet
from analyzer import estimate_win_probability, is_value_bet

app = Flask(__name__)

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>ValueBet Scout</title></head>
    <body>
        <h1>🎯 ValueBet Scout</h1>
        <p> Coupons intelligents de 3–4 matchs avec avantage statistique </p>
        <button onclick="loadBets()">Charger les value bets du jour</button>
        <div id="bets"></div>
        <script>
            async function loadBets() {
                const res = await fetch('/api/value-bets');
                const data = await res.json();
                document.getElementById("bets").innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/value-bets')
def api_value_bets():
    fixtures = get_fixtures_today()
    value_bets = []
    for f in fixtures[:10]:  # Limite à 10 matchs
        odds = get_odds_1xbet(f['home'], f['away'])
        probs = estimate_win_probability(f['home'], f['away'])
        
        if is_value_bet(probs['home'], odds['home']):
            value_bets.append({
                'match': f"{f['home']} vs {f['away']}",
                'bet': '1',
                'odds': odds['home'],
                'estimated_prob': probs['home'],
                'edge': round(probs['home'] - (1/odds['home']), 3)
            })
        if is_value_bet(probs['away'], odds['away']):
            value_bets.append({
                'match': f"{f['home']} vs {f['away']}",
                'bet': '2',
                'odds': odds['away'],
                'estimated_prob': probs['away'],
                'edge': round(probs['away'] - (1/odds['away']), 3)
            })
    
    # Génère 1 coupon de 3–4 matchs
    coupon = value_bets[:4] if len(value_bets) >= 3 else []
    combined_prob = 1
    for bet in coupon:
        combined_prob *= bet['estimated_prob']
    
    return jsonify({
        'value_bets_count': len(value_bets),
        'coupon': coupon,
        'combined_probability': round(combined_prob, 3),
        'expected_return': round(combined_prob * sum(b['odds'] for b in coupon), 2)
    })
