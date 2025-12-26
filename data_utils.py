import os
import sys

# SSL Hatalarını Kökten Çözme
if 'REQUESTS_CA_BUNDLE' in os.environ: del os.environ['REQUESTS_CA_BUNDLE']
if 'CURL_CA_BUNDLE' in os.environ: del os.environ['CURL_CA_BUNDLE']

import pandas as pd
import requests
import streamlit as st
import urllib3
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_STATIC = "https://fantasy.premierleague.com/api/bootstrap-static/"
API_FIXTURES = "https://fantasy.premierleague.com/api/fixtures/"

@st.cache_data(ttl=1800)
def load_all_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r_static = requests.get(API_STATIC, headers=headers, verify=False, timeout=20)
        data_static = r_static.json()
        
        id_to_name = {}
        team_logos = {}
        team_players = {} 
        all_player_images = [] # YENİ: Oyuncu resimlerini tutacak liste

        for t in data_static['teams']:
            t_name = t['name']
            # İsim Düzeltmeleri
            if t_name == "Nottingham Forest": t_name = "Nott'm Forest"
            if t_name == "Wolverhampton Wanderers": t_name = "Wolves"
            if t_name == "Leicester City": t_name = "Leicester"
            if t_name == "Ipswich Town": t_name = "Ipswich"
            if t_name == "Luton Town": t_name = "Luton"
            if t_name == "Sheffield United": t_name = "Sheffield Utd"
            if t_name == "Manchester United": t_name = "Man Utd"
            if t_name == "Manchester City": t_name = "Man City"
            if t_name == "Newcastle United": t_name = "Newcastle"
            if t_name == "Tottenham Hotspur": t_name = "Tottenham"
            if t_name == "West Ham United": t_name = "West Ham"

            id_to_name[t['id']] = t_name
            team_logos[t_name] = f"https://resources.premierleague.com/premierleague/badges/100/t{t['code']}.png"
            team_players[t_name] = []

        for p in data_static['elements']:
            team_name = id_to_name.get(p['team'])
            if team_name:
                team_players[team_name].append({
                    'web_name': p['web_name'],
                    'status': p['status'], 
                    'chance': p['chance_of_playing_next_round']
                })
                
                # YENİ: Sadece aktif ve fotoğrafı olan oyuncuları listeye ekle
                # 'code' parametresi oyuncunun fotoğraf ismidir.
                if p['minutes'] > 0: # Hiç oynamamış yedekleri alma
                    photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{p['code']}.png"
                    all_player_images.append(photo_url)

        r_fixtures = requests.get(API_FIXTURES, headers=headers, verify=False, timeout=20)
        data_fixtures = r_fixtures.json()
        match_list = []

        for match in data_fixtures:
            if match['finished']:
                h_name = id_to_name.get(match['team_h'], "Unknown")
                a_name = id_to_name.get(match['team_a'], "Unknown")
                
                h_score = match['team_h_score']
                a_score = match['team_a_score']
                
                hy, ay, hr, ar = 0, 0, 0, 0
                for stat in match['stats']:
                    if stat['identifier'] == 'yellow_cards':
                        for x in stat['h']: hy += x['value']
                        for x in stat['a']: ay += x['value']
                    if stat['identifier'] == 'red_cards':
                        for x in stat['h']: hr += x['value']
                        for x in stat['a']: ar += x['value']

                if h_score > a_score: ftr = 'H'
                elif a_score > h_score: ftr = 'A'
                else: ftr = 'D'

                match_list.append({
                    'Date': match['kickoff_time'],
                    'HomeTeam': h_name, 'AwayTeam': a_name,
                    'FTHG': h_score, 'FTAG': a_score, 'FTR': ftr,
                    'HY': hy, 'AY': ay, 'HR': hr, 'AR': ar
                })

        df = pd.DataFrame(match_list)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
        return df, team_logos, team_players, all_player_images # YENİ LİSTEYİ DÖNDÜR

    except Exception as e:
        st.error(f"Veri Hatası: {e}")
        return pd.DataFrame(), {}, {}, []

def get_advanced_stats(df, team_players, team, last_n=5):
    # Bu fonksiyon aynen kalıyor, değişikliğe gerek yok
    matches = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)].sort_values(by="Date")
    recent_matches = matches.tail(last_n)
    
    if len(matches) == 0: return {}

    points = 0
    scored = 0
    conceded = 0
    cards_weight = 0

    for _, row in recent_matches.iterrows():
        is_home = row["HomeTeam"] == team
        my_score = row["FTHG"] if is_home else row["FTAG"]
        opp_score = row["FTAG"] if is_home else row["FTHG"]
        
        scored += my_score
        conceded += opp_score
        
        if my_score > opp_score: points += 3
        elif my_score == opp_score: points += 1
        
        y = row["HY"] if is_home else row["AY"]
        r = row["HR"] if is_home else row["AR"]
        cards_weight += y + (r * 3)

    table = {}
    for t_name in pd.concat([df['HomeTeam'], df['AwayTeam']]).unique(): table[t_name] = 0
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
            if p['status'] == 's' or (p['status'] == 'i' and p['chance'] in [0, 25]):
                missing_count += 1
                key_players_missing.append(p['web_name'])

    norm_form = (points / (last_n * 3)) * 10
    norm_rank = max(0, (21 - rank) / 2)
    
    avg_scored = scored / last_n if last_n > 0 else 0
    norm_goals = min((avg_scored / 2.5) * 10, 10)
    
    avg_cards = cards_weight / last_n if last_n > 0 else 0
    norm_card_risk = min((avg_cards / 3) * 10, 10)

    return {
        "raw": {
            "rank": rank, "scored": scored, "conceded": conceded,
            "missing": missing_count, "missing_names": key_players_missing, "form_points": points
        },
        "fuzzy": {
            "form": round(norm_form, 2),
            "rank": round(norm_rank, 2),
            "goals": round(norm_goals, 2),
            "cards": round(norm_card_risk, 2)
        }
    }