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

def fetch_api_data(url, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Cache-Control": "no-cache"
    } 
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            if response.status_code == 200: return response.json()
        except: time.sleep(1); continue
    return None

def calculate_league_table(df, team_logos):
    if df.empty: return pd.DataFrame()
    
    teams = list(team_logos.keys())
    # Yapıya 'Form' listesi ekledik
    table_data = {t: {'Pl': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0, 'Logo': team_logos.get(t), 'Form': []} for t in teams}
    
    # Sadece bitmiş maçlar
    finished_matches = df[df['IsFinished'] == True].sort_values('Date') # Tarihe göre sırala ki form doğru olsun

    for _, row in finished_matches.iterrows():
        h, a = row['HomeTeam'], row['AwayTeam']
        if h not in table_data or a not in table_data: continue
        
        hg, ag = int(row['FTHG']), int(row['FTAG'])

        # İstatistikler
        table_data[h]['Pl'] += 1; table_data[a]['Pl'] += 1
        table_data[h]['GF'] += hg; table_data[h]['GA'] += ag
        table_data[a]['GF'] += ag; table_data[a]['GA'] += hg
        
        # Puan ve Form (W=Win, D=Draw, L=Loss)
        if hg > ag: 
            table_data[h]['W'] += 1; table_data[h]['Pts'] += 3; table_data[a]['L'] += 1
            table_data[h]['Form'].append('W'); table_data[a]['Form'].append('L')
        elif ag > hg: 
            table_data[a]['W'] += 1; table_data[a]['Pts'] += 3; table_data[h]['L'] += 1
            table_data[a]['Form'].append('W'); table_data[h]['Form'].append('L')
        else: 
            table_data[h]['D'] += 1; table_data[h]['Pts'] += 1; table_data[a]['D'] += 1; table_data[a]['Pts'] += 1
            table_data[h]['Form'].append('D'); table_data[a]['Form'].append('D')

    # Averaj Hesapla ve Formu Son 5 Maçla Sınırla
    for t in table_data:
        table_data[t]['GD'] = table_data[t]['GF'] - table_data[t]['GA']
        table_data[t]['Form'] = table_data[t]['Form'][-5:] # Son 5 maç

    df_table = pd.DataFrame.from_dict(table_data, orient='index')
    df_table = df_table.sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
    
    df_table.reset_index(inplace=True)
    df_table.rename(columns={'index': 'Team'}, inplace=True)
    df_table.insert(0, 'Pos', range(1, 1 + len(df_table)))
    
    return df_table

def generate_mock_data():
    teams = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich", "Leicester", "Liverpool", "Luton", "Man City", "Man Utd", "Newcastle", "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"]
    team_logos = {t: f"https://resources.premierleague.com/premierleague/badges/100/t{i+1}.png" for i, t in enumerate(teams)}
    match_list = []
    today = datetime.now()
    for i in range(200):
        date = today - timedelta(days=i*2)
        home, away = random.sample(teams, 2)
        h_score, a_score = random.randint(0, 4), random.randint(0, 4)
        ftr = 'H' if h_score > a_score else ('A' if a_score > h_score else 'D')
        match_list.append({'Date': date.date(), 'HomeTeam': home, 'AwayTeam': away, 'FTHG': h_score, 'FTAG': a_score, 'FTR': ftr, 'HY': 0, 'AY': 0, 'HR': 0, 'AR': 0, 'IsLive': False, 'IsFinished': True, 'Referee': 'Mock Ref'})
    return pd.DataFrame(match_list), team_logos, {t: [] for t in teams}, ["https://resources.premierleague.com/premierleague/photos/players/110x140/p223340.png"] * 20

@st.cache_data(ttl=60, show_spinner=False)
def load_all_data():
    try:
        data_static = fetch_api_data(API_STATIC)
        if not data_static: return generate_mock_data()
        
        id_to_name = {}; team_logos = {}; team_players = {}; all_player_images = []
        if 'teams' in data_static:
            for t in data_static['teams']:
                t_name = t['name'].replace("Nottingham Forest", "Nott'm Forest").replace("Sheffield United", "Sheffield Utd")
                id_to_name[t['id']] = t_name
                team_logos[t_name] = f"https://resources.premierleague.com/premierleague/badges/100/t{t['code']}.png"
                team_players[t_name] = []
        if 'elements' in data_static:
            for p in data_static['elements']:
                t_name = id_to_name.get(p['team'])
                if t_name:
                    team_players[t_name].append({'web_name': p['web_name'], 'status': p['status'], 'chance': p.get('chance_of_playing_next_round', 100)})
                    if p.get('minutes', 0) > 0: all_player_images.append(f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{p['code']}.png")
        data_fixtures = fetch_api_data(API_FIXTURES)
        if not data_fixtures: return generate_mock_data()
        match_list = []
        for match in data_fixtures:
            if isinstance(match, dict):
                h_name = id_to_name.get(match['team_h'], "Unknown"); a_name = id_to_name.get(match['team_a'], "Unknown")
                started = match.get('started', False); finished = match.get('finished_provisional', False) or match.get('finished', False)
                h_score = match.get('team_h_score') if started else 0; a_score = match.get('team_a_score') if started else 0
                ftr = None
                if finished: ftr = 'H' if h_score > a_score else ('A' if a_score > h_score else 'D')
                hy, ay, hr, ar = 0, 0, 0, 0
                if 'stats' in match:
                    for stat in match['stats']:
                        if stat['identifier'] == 'yellow_cards': hy += sum(x['value'] for x in stat['h']); ay += sum(x['value'] for x in stat['a'])
                        if stat['identifier'] == 'red_cards': hr += sum(x['value'] for x in stat['h']); ar += sum(x['value'] for x in stat['a'])
                match_list.append({'Date': match.get('kickoff_time'), 'HomeTeam': h_name, 'AwayTeam': a_name, 'FTHG': h_score, 'FTAG': a_score, 'FTR': ftr, 'HY': hy, 'AY': ay, 'HR': hr, 'AR': ar, 'IsLive': started and not finished, 'IsFinished': finished, 'Referee': 'Ref'})
        df = pd.DataFrame(match_list)
        if df.empty: return generate_mock_data()
        df['DateObj'] = pd.to_datetime(df['Date']); df['Date'] = df['DateObj'].dt.date
        return df, team_logos, team_players, all_player_images
    except: return generate_mock_data()

def get_advanced_stats(df, team_players, team, last_n=5):
    if df.empty: return {"raw": {"rank": 10, "scored": 0, "conceded": 0, "missing": 0, "missing_names": [], "form_points": 5}, "fuzzy": {"form": 5.0, "rank": 5.0, "goals": 5.0, "cards": 5.0}}
    matches = df[(df["IsFinished"] == True) & ((df["HomeTeam"] == team) | (df["AwayTeam"] == team))].sort_values(by="Date")
    recent_matches = matches.tail(last_n)
    if len(matches) == 0: return {"raw": {"rank": 10, "scored": 0, "conceded": 0, "missing": 0, "missing_names": [], "form_points": 5}, "fuzzy": {"form": 5.0, "rank": 5.0, "goals": 5.0, "cards": 5.0}}
    points, scored, conceded, cards_weight = 0, 0, 0, 0
    for _, row in recent_matches.iterrows():
        is_home = row["HomeTeam"] == team; my_score = row["FTHG"] if is_home else row["FTAG"]; opp_score = row["FTAG"] if is_home else row["FTHG"]
        scored += my_score; conceded += opp_score
        if my_score > opp_score: points += 3
        elif my_score == opp_score: points += 1
        cards_weight += (row["HY"] if is_home else row["AY"]) + ((row["HR"] if is_home else row["AR"]) * 3)
    missing_count = 0; key_players_missing = []
    if team in team_players:
        for p in team_players[team]:
            if p['status'] in ['s', 'i'] and p['chance'] in [0, 25]: missing_count += 1; key_players_missing.append(p['web_name'])
    return {"raw": {"rank": 10, "scored": scored, "conceded": conceded, "missing": missing_count, "missing_names": key_players_missing, "form_points": points}, "fuzzy": {"form": round((points / (last_n * 3)) * 10, 2), "rank": 5.0, "goals": round(min(((scored / last_n) / 2.5) * 10, 10), 2) if last_n > 0 else 0, "cards": round(min(((cards_weight / last_n) / 3) * 10, 10), 2) if last_n > 0 else 0}}