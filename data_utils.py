import os
import pandas as pd
import requests
import streamlit as st
import urllib3
import random
import time
from datetime import datetime, timedelta

# SSL Hatalarını Engelle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_STATIC = "https://fantasy.premierleague.com/api/bootstrap-static/"
API_FIXTURES = "https://fantasy.premierleague.com/api/fixtures/"

# --- 1. GÜÇLÜ İSTEK FONKSİYONU ---
def fetch_api_data(url, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://fantasy.premierleague.com",
        "Referer": "https://fantasy.premierleague.com/"
    }
    
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            if response.status_code == 200:
                return response.json()
        except:
            time.sleep(1)
            continue
    return None

# --- 2. YEDEK VERİ OLUŞTURUCU (MOCK DATA) ---
def generate_mock_data():
    # Bu fonksiyon API çalışmazsa devreye girer ve sahte ama düzgün veri üretir.
    teams = [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich", 
        "Leicester", "Liverpool", "Luton", "Man City", "Man Utd", 
        "Newcastle", "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"
    ]
    
    id_to_name = {i+1: t for i, t in enumerate(teams)}
    
    # Gerçek logoları kullanmaya çalışalım
    team_logos = {t: f"https://resources.premierleague.com/premierleague/badges/100/t{i+1}.png" for i, t in enumerate(teams)}
    
    team_players = {}
    for t in teams:
        team_players[t] = [
            {'web_name': f'Star ({t})', 'status': 'a', 'chance': 100},
            {'web_name': f'Defender ({t})', 'status': 'a', 'chance': 100}
        ]
    
    match_list = []
    today = datetime.now()
    
    # Rastgele maç geçmişi
    for i in range(100):
        date = today - timedelta(days=i*3)
        home = random.choice(teams)
        away = random.choice(teams)
        while home == away: away = random.choice(teams)
        
        h_score = random.randint(0, 4)
        a_score = random.randint(0, 4)
        
        ftr = 'H' if h_score > a_score else ('A' if a_score > h_score else 'D')
        
        match_list.append({
            'Date': date.date(),
            'HomeTeam': home, 'AwayTeam': away,
            'FTHG': h_score, 'FTAG': a_score, 'FTR': ftr,
            'HY': random.randint(0, 2), 'AY': random.randint(0, 2),
            'HR': 0, 'AR': 0
        })
        
    df = pd.DataFrame(match_list)
    # Varsayılan bir oyuncu resmi
    all_player_images = ["https://resources.premierleague.com/premierleague/photos/players/110x140/p223340.png"] * 20
    
    return df, team_logos, team_players, all_player_images

# --- 3. ANA VERİ YÜKLEME FONKSİYONU ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_all_data():
    # BURADA ASLA st.toast veya st.error KULLANMA!
    # Sadece veri döndür. Hata olursa mock data döndür.
    
    try:
        # 1. Statik Veriyi Çek
        data_static = fetch_api_data(API_STATIC)
        if not data_static: return generate_mock_data() # API yoksa direkt mock dön

        id_to_name = {}
        team_logos = {}
        team_players = {} 
        all_player_images = []

        if 'teams' in data_static:
            for t in data_static['teams']:
                t_name = t['name']
                name_map = {
                    "Nottingham Forest": "Nott'm Forest", "Wolverhampton Wanderers": "Wolves",
                    "Leicester City": "Leicester", "Ipswich Town": "Ipswich", "Luton Town": "Luton",
                    "Sheffield United": "Sheffield Utd", "Manchester United": "Man Utd",
                    "Manchester City": "Man City", "Newcastle United": "Newcastle",
                    "Tottenham Hotspur": "Tottenham", "West Ham United": "West Ham"
                }
                if t_name in name_map: t_name = name_map[t_name]
                id_to_name[t['id']] = t_name
                team_logos[t_name] = f"https://resources.premierleague.com/premierleague/badges/100/t{t['code']}.png"
                team_players[t_name] = []

        if 'elements' in data_static:
            for p in data_static['elements']:
                team_name = id_to_name.get(p['team'])
                if team_name:
                    team_players[team_name].append({
                        'web_name': p['web_name'],
                        'status': p['status'], 
                        'chance': p.get('chance_of_playing_next_round', 100)
                    })
                    if p.get('minutes', 0) > 0:
                        all_player_images.append(f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{p['code']}.png")

        # 2. Fikstür Verisini Çek
        data_fixtures = fetch_api_data(API_FIXTURES)
        if not data_fixtures or not isinstance(data_fixtures, list):
             return generate_mock_data() # Fikstür yoksa mock dön

        match_list = []
        for match in data_fixtures:
            if isinstance(match, dict) and match.get('finished'):
                h_name = id_to_name.get(match['team_h'], "Unknown")
                a_name = id_to_name.get(match['team_a'], "Unknown")
                h_score = match.get('team_h_score', 0)
                a_score = match.get('team_a_score', 0)
                
                hy, ay, hr, ar = 0, 0, 0, 0
                stats = match.get('stats', [])
                if isinstance(stats, list):
                    for stat in stats:
                        if stat.get('identifier') == 'yellow_cards':
                            for x in stat.get('h', []): hy += x.get('value', 0)
                            for x in stat.get('a', []): ay += x.get('value', 0)
                        if stat.get('identifier') == 'red_cards':
                            for x in stat.get('h', []): hr += x.get('value', 0)
                            for x in stat.get('a', []): ar += x.get('value', 0)

                match_list.append({
                    'Date': match.get('kickoff_time'),
                    'HomeTeam': h_name, 'AwayTeam': a_name,
                    'FTHG': h_score, 'FTAG': a_score, 
                    'FTR': 'H' if h_score > a_score else ('A' if a_score > h_score else 'D'),
                    'HY': hy, 'AY': ay, 'HR': hr, 'AR': ar
                })

        df = pd.DataFrame(match_list)
        if df.empty: return generate_mock_data()
        
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df, team_logos, team_players, all_player_images

    except Exception:
        # Ne hata olursa olsun, sessizce mock dataya geç
        return generate_mock_data()

def get_advanced_stats(df, team_players, team, last_n=5):
    # Veri boşsa varsayılan döndür
    if df.empty:
        return {"raw": {"rank": 10, "scored": 0, "conceded": 0, "missing": 0, "missing_names": [], "form_points": 5},
                "fuzzy": {"form": 5.0, "rank": 5.0, "goals": 5.0, "cards": 5.0}}

    matches = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)].sort_values(by="Date")
    recent_matches = matches.tail(last_n)
    
    if len(matches) == 0:
        return {"raw": {"rank": 10, "scored": 0, "conceded": 0, "missing": 0, "missing_names": [], "form_points": 5},
                "fuzzy": {"form": 5.0, "rank": 5.0, "goals": 5.0, "cards": 5.0}}

    points, scored, conceded, cards_weight = 0, 0, 0, 0

    for _, row in recent_matches.iterrows():
        is_home = row["HomeTeam"] == team
        my_score = row["FTHG"] if is_home else row["FTAG"]
        opp_score = row["FTAG"] if is_home else row["FTHG"]
        
        scored += my_score
        conceded += opp_score
        if my_score > opp_score: points += 3
        elif my_score == opp_score: points += 1
        
        cards_weight += (row["HY"] if is_home else row["AY"]) + ((row["HR"] if is_home else row["AR"]) * 3)

    # Sıralama Hesapla
    table = {t: 0 for t in pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()}
    for _, row in df.iterrows():
        if row['FTR'] == 'H': table[row['HomeTeam']] += 3
        elif row['FTR'] == 'A': table[row['AwayTeam']] += 3
        else: table[row['HomeTeam']] += 1; table[row['AwayTeam']] += 1
            
    sorted_table = sorted(table.items(), key=lambda x: x[1], reverse=True)
    rank = 20
    for i, (t_name, pts) in enumerate(sorted_table):
        if t_name == team: rank = i + 1; break

    missing_count = 0
    key_players_missing = []
    if team in team_players:
        for p in team_players[team]:
            if p['status'] in ['s', 'i'] and p['chance'] in [0, 25]:
                missing_count += 1
                key_players_missing.append(p['web_name'])

    return {
        "raw": {
            "rank": rank, "scored": scored, "conceded": conceded,
            "missing": missing_count, "missing_names": key_players_missing, "form_points": points
        },
        "fuzzy": {
            "form": round((points / (last_n * 3)) * 10, 2),
            "rank": round(max(0, (21 - rank) / 2), 2),
            "goals": round(min(((scored / last_n) / 2.5) * 10, 10), 2) if last_n > 0 else 0,
            "cards": round(min(((cards_weight / last_n) / 3) * 10, 10), 2) if last_n > 0 else 0
        }
    }