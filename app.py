from flask import Flask, render_template_string, jsonify
from collector import get_fixtures_today, get_odds_1xbet
from analyzer import estimate_win_probability, is_value_bet

app = Flask(__name__)

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>🎯 ValueBet Scout — Prédiction Fiable</title>
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: #f8fafc;
                margin: 0;
                padding: 20px;
                color: #1e293b;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                overflow: hidden;
            }
            header {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                padding: 24px 20px;
                text-align: center;
            }
            h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 700;
            }
            .subtitle {
                opacity: 0.9;
                margin-top: 8px;
                font-size: 16px;
            }
            .content {
                padding: 24px;
            }
            .info-box {
                background: #eff6ff;
                border-left: 4px solid #3b82f6;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 24px;
                font-size: 14px;
            }
            .match-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }
            .match-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }
            .team {
                font-weight: 700;
                font-size: 18px;
            }
            .vs {
                color: #94a3b8;
                font-weight: 600;
            }
            .probabilities {
                display: flex;
                gap: 20px;
                margin: 16px 0;
            }
            .prob-item {
                text-align: center;
                flex: 1;
            }
            .prob-label {
                font-size: 14px;
                color: #64748b;
                margin-bottom: 6px;
            }
            .prob-value {
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
            }
            .recommendation {
                background: #dcfce7;
                color: #166534;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                text-align: center;
                margin-top: 16px;
            }
            button {
                width: 100%;
                padding: 14px;
                background: #1d4ed8;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #1e40af;
            }
            #result {
                margin-top: 24px;
            }
            .loading {
                text-align: center;
                color: #3b82f6;
                font-weight: 600;
                margin: 20px 0;
            }
            .error {
                background: #fee2e2;
                color: #b91c1c;
                padding: 12px;
                border-radius: 8px;
                margin-top: 16px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎯 ValueBet Scout</h1>
                <div class="subtitle">Prédictions intelligentes • Coupons de 3–4 matchs • Avantage statistique</div>
            </header>
            <div class="content">
                <div class="info-box">
                    <strong>Comment ça marche ?</strong><br>
                    1. L’outil analyse la forme récente des équipes (résultats, buts).<br>
                    2. Il compare avec les cotes des bookmakers.<br>
                    3. Il ne propose que les paris où <strong>ta probabilité > probabilité implicite</strong> → <em>value bet</em>.
                </div>

                <button onclick="loadBets()">🔍 Analyser les matchs d'aujourd'hui</button>

                <div id="result"></div>
            </div>
        </div>

        <script>
            async function loadBets() {
                const btn = document.querySelector('button');
                btn.disabled = true;
                btn.textContent = 'Chargement...';

                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<div class="loading">Analyse en cours... (20-30 secondes)</div>';

                try {
                    const res = await fetch('/api/value-bets');
                    const data = await res.json();

                    if (data.error) {
                        resultDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                    } else {
                        renderResults(data);
                    }
                } catch (err) {
                    resultDiv.innerHTML = `<div class="error">❌ Erreur de connexion : ${err.message}</div>`;
                } finally {
                    btn.disabled = false;
                    btn.textContent = '🔍 Analyser les matchs d\'aujourd\'hui';
                }
            }

            function renderResults(data) {
                if (!data.coupon || data.coupon.length === 0) {
                    document.getElementById('result').innerHTML = `
                        <div class="error">
                            ❌ Aucun value bet trouvé aujourd'hui.<br>
                            Essayez demain ou élargissez les ligues.
                        </div>
                    `;
                    return;
                }

                let html = `<h3>✅ ${data.coupon.length} matchs recommandés</h3>`;

                data.coupon.forEach(bet => {
                    const [home, away] = bet.match.split(' vs ');
                    const isHome = bet.bet === '1';
                    const favored = isHome ? home : away;

                    html += `
                    <div class="match-card">
                        <div class="match-header">
                            <span class="team">${home}</span>
                            <span class="vs">vs</span>
                            <span class="team">${away}</span>
                        </div>
                        <div class="probabilities">
                            <div class="prob-item">
                                <div class="prob-label">Probabilité estimée</div>
                                <div class="prob-value">${(bet.estimated_prob * 100).toFixed(1)}%</div>
                            </div>
                            <div class="prob-item">
                                <div class="prob-label">Cote</div>
                                <div class="prob-value">${bet.odds}</div>
                            </div>
                        </div>
                        <div class="recommendation">
                            ➤ <strong>${favored}</strong> est le meilleur pari (${(bet.estimated_prob * 100).toFixed(1)}%)
                        </div>
                    </div>
                    `;
                });

                // Coupon combiné
                const combinedProb = (data.combined_probability * 100).toFixed(1);
                const expectedReturn = data.expected_return ? `+${(data.expected_return * 100).toFixed(0)}%` : 'N/A';

                html += `
                <div class="match-card" style="border-top: 2px dashed #cbd5e1; margin-top: 24px;">
                    <h3>🧾 Coupon combiné (3–4 matchs)</h3>
                    <p><strong>Probabilité de gagner :</strong> ${combinedProb}%</p>
                    <p><strong>Rendement attendu :</strong> ${expectedReturn}</p>
                    <p style="font-size:14px; color:#64748b;">
                        💡 Conseil : Ne misez jamais plus de 2–5% de votre bankroll sur ce coupon.
                    </p>
                </div>
                `;

                document.getElementById('result').innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/api/value-bets')
def api_value_bets():
    try:
        fixtures = get_fixtures_today()
        value_bets = []

        for f in fixtures[:10]:  # Limite à 10 matchs
            odds = get_odds_1xbet(f['home'], f['away'])
            probs = estimate_win_probability(f['home'], f['away'])

            if odds and 'home' in odds and 'away' in odds:
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

        # Coupon de 3–4 matchs
        coupon = value_bets[:4] if len(value_bets) >= 3 else []
        combined_prob = 1
        for bet in coupon:
            combined_prob *= bet['estimated_prob']

        expected_return = None
        if coupon:
            combined_odds = 1
            for b in coupon:
                combined_odds *= b['odds']
            expected_return = round(combined_prob * combined_odds, 2)

        return jsonify({
            'value_bets_count': len(value_bets),
            'coupon': coupon,
            'combined_probability': round(combined_prob, 3),
            'expected_return': expected_return
        })

    except Exception as e:
        return jsonify({'error': str(e)})
