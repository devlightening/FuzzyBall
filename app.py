import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import random
import skfuzzy as fuzz
from datetime import datetime
from data_utils import load_all_data, get_advanced_stats, calculate_league_table
from fuzzy_system import match_sim, card_sim, form, rank, goals, result, aggression, tension, chaos

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FUZZYBED", page_icon="⚽", layout="wide")

# --- DİL SÖZLÜĞÜ ---
TRANS = {
    "TR": {
        "header_title": "FUZZYBED",
        "header_sub": "Yapay Zeka Destekli Futbol Analiz Motoru",
        "tab_sim": "🔮 MAÇ SİMÜLASYONU",
        "tab_table": "🏆 PUAN DURUMU",
        "tab_live": "🔴 CANLI / GÜNÜN MAÇLARI",
        "subtab_res": "⚡ ANALİZ SONUCU",
        "subtab_stat": "📈 İSTATİSTİK DETAYLARI",
        "subtab_fuzzy": "🧠 FUZZY GRAFİKLERİ",
        "live_no_match": "Bugün maç yok.",
        "home": "EV SAHİBİ", "away": "DEPLASMAN",
        "start_btn": "SİMÜLASYONU BAŞLAT",
        "warning_same_team": "⚠️ Lütfen iki farklı takım seçin.",
        "spinner": "Mamdani Motoru Çalışıyor...",
        "refresh_btn": "VERİLERİ YENİLE",
        "refresh_desc": "Veriler güncel değilse tıklayın.",
        "wins": "KAZANIR", "draw": "BERABERLİK",
        "winner_title": "YAPAY ZEKA TAHMİNİ (Mamdani)",
        "confidence": "Güven Skoru",
        "stat_rank": "LİG SIRASI", "stat_goals": "GOL (A/Y)", "stat_form": "FORM PUANI", "stat_missing": "EKSİK OYUNCU",
        "last_matches": "Son Maçlar",
        "missing_alert": "🚨 Eksikler: {0}", "full_squad": "✅ Tam Kadro",
        "graph_info": "Giriş değerlerinin bulanık kümelere üyelik dereceleri:",
        "g_form": "GİRDİ 1: Form", "g_rank": "GİRDİ 2: Sıralama", "g_goals": "GİRDİ 3: Gol Gücü",
        "g_result": "SONUÇ: {0} Şansı",
        "final_res": "🏆 SONUÇ VE ATMOSFER",
        "prob_win": "{0} Galibiyet İhtimali",
        "prob_chaos": "🔥 YÜKSEK TANSİYON! Kaos Skoru: {0:.2f}/10.",
        "prob_chaos_low": "🟢 Temiz Maç Beklentisi. Kaos Skoru: {0:.2f}/10",
        "slot_msg": "OYUNCULAR VE VERİLER ANALİZ EDİLİYOR...",
        "tbl_team": "TAKIM", "tbl_input": "GİRİŞ", "tbl_decision": "BASKIN KARAR",
        
        # Kısaltmalar
        "short_w": "G", "short_d": "B", "short_l": "M",
        
        "terms": {"kotu": "KÖTÜ", "orta": "ORTA", "iyi": "İYİ", "dusuk": "DÜŞÜK", "yuksek": "YÜKSEK", "kisir": "KISIR", "normal": "NORMAL", "golcu": "GOLCÜ", "maglubiyet": "MAĞLUBİYET", "beraberlik": "BERABERLİK", "galibiyet": "GALİBİYET"}
    },
    "EN": {
        "header_title": "FUZZYBED",
        "header_sub": "AI Powered Football Analytics Engine",
        "tab_sim": "🔮 MATCH SIMULATION",
        "tab_table": "🏆 LEAGUE TABLE",
        "tab_live": "🔴 LIVE / TODAY",
        "subtab_res": "⚡ PREDICTION RESULT",
        "subtab_stat": "📈 DETAILED STATS",
        "subtab_fuzzy": "🧠 FUZZY CHARTS",
        "live_no_match": "No matches today.",
        "home": "HOME TEAM", "away": "AWAY TEAM",
        "start_btn": "START SIMULATION",
        "warning_same_team": "⚠️ Please select two different teams.",
        "spinner": "Running Mamdani Engine...",
        "refresh_btn": "REFRESH DATA",
        "refresh_desc": "Click if outdated.",
        "wins": "WINS", "draw": "DRAW",
        "winner_title": "AI PREDICTION (Mamdani)",
        "confidence": "Confidence Score",
        "stat_rank": "LEAGUE RANK", "stat_goals": "GOALS (F/A)", "stat_form": "FORM POINTS", "stat_missing": "MISSING PLAYERS",
        "last_matches": "Last Matches",
        "missing_alert": "🚨 Missing: {0}", "full_squad": "✅ Full Squad",
        "graph_info": "Membership degrees of input values to fuzzy sets:",
        "g_form": "INPUT 1: Form", "g_rank": "INPUT 2: Rank", "g_goals": "INPUT 3: Goal Power",
        "g_result": "OUTPUT: {0} Chance",
        "final_res": "🏆 RESULT & ATMOSPHERE",
        "prob_win": "{0} Win Probability",
        "prob_chaos": "🔥 HIGH TENSION! Chaos Score: {0:.2f}/10.",
        "prob_chaos_low": "🟢 Clean Match Expected. Chaos Score: {0:.2f}/10",
        "slot_msg": "ANALYZING PLAYERS AND DATA...",
        "tbl_team": "TEAM", "tbl_input": "INPUT", "tbl_decision": "DECISION",
        
        "short_w": "W", "short_d": "D", "short_l": "L",

        "terms": {"kotu": "POOR", "orta": "AVERAGE", "iyi": "GOOD", "dusuk": "LOW", "yuksek": "HIGH", "kisir": "WEAK", "normal": "NORMAL", "golcu": "STRONG", "maglubiyet": "DEFEAT", "beraberlik": "DRAW", "galibiyet": "VICTORY"}
    }
}

# --- CSS TASARIMI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&display=swap');
    
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Rajdhani', sans-serif; background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #050505 70%); }
    .neon-header { font-family: 'Orbitron', sans-serif; text-align: center; font-size: 3.5rem; font-weight: 900; background: -webkit-linear-gradient(#00f260, #0575e6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 50px rgba(0, 242, 96, 0.3); margin-bottom: 20px; letter-spacing: 4px; }
    
    /* Live Card */
    .live-card { background: rgba(255,255,255,0.05); border-left: 3px solid #00f260; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .live-card.live { border-left: 3px solid #ff0055; animation: pulse 2s infinite; }
    .live-time { font-size: 0.8rem; color: #888; display: flex; justify-content: space-between; }
    .live-teams { font-size: 0.95rem; font-weight: bold; margin: 5px 0; display: flex; justify-content: space-between; align-items: center; }
    .live-score { background: #111; padding: 2px 8px; border-radius: 4px; color: #00f260; font-family: 'Orbitron'; font-size: 1.1rem;}
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 0, 85, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); } }
    
    /* Team Selection Buttons */
    .logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px; }
    .logo-center { width: 150px; height: 150px; object-fit: contain; filter: drop-shadow(0 0 20px rgba(0, 242, 96, 0.3)); transform: scale(1.1); animation: float 3s ease-in-out infinite; }
    .team-name-box { font-family: 'Orbitron', sans-serif; font-size: 1.4rem; font-weight: 700; margin-top: 15px; color: #fff; background: rgba(255,255,255,0.05); padding: 8px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    @keyframes float { 0% { transform: translateY(0px) scale(1.1); } 50% { transform: translateY(-10px) scale(1.1); } 100% { transform: translateY(0px) scale(1.1); } }
    
    .nav-btn-container button { border-radius: 50% !important; width: 50px !important; height: 50px !important; background: rgba(0,0,0,0.5) !important; border: 1px solid #444 !important; color: #888 !important; font-size: 1.5rem !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    .nav-btn-container button:hover { color: #00f260 !important; border-color: #00f260 !important; box-shadow: 0 0 15px rgba(0, 242, 96, 0.4) !important; }

    /* Big Start Button */
    .big-btn-container button { width: 100% !important; background: linear-gradient(90deg, #00f260 0%, #0575e6 100%) !important; color: white !important; font-family: 'Orbitron', sans-serif !important; font-size: 1.5rem !important; font-weight: 800 !important; padding: 18px 0 !important; border-radius: 12px !important; border: 2px solid rgba(255,255,255,0.2) !important; box-shadow: 0 0 40px rgba(0, 242, 96, 0.3) !important; }
    .big-btn-container button:hover { transform: scale(1.02) !important; box-shadow: 0 0 60px rgba(5, 117, 230, 0.6) !important; }

    /* Winner Card */
    .winner-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; text-align: center; margin-top: 30px; backdrop-filter: blur(10px); }
    .result-text { font-family: 'Orbitron'; font-size: 3.5rem; font-weight: 900; margin-top: 15px; letter-spacing: 2px; }

    /* Stats */
    .stat-card { background: linear-gradient(180deg, rgba(30,30,40,0.95), rgba(10,10,10,0.95)); border-top: 3px solid #0575e6; padding: 15px; text-align: center; border-radius: 12px; margin-bottom: 10px; }
    .stat-value { font-size: 1.8rem; font-weight: bold; color: white; }
    .stat-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    
    /* MAÇ GEÇMİŞİ (YENİLENMİŞ REFERANS TASARIM - RENKLİ İSİMLER) */
    .history-row { 
        background-color: #000; 
        padding: 12px; 
        margin-bottom: 2px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        font-family: 'Rajdhani', sans-serif; 
        font-size: 0.95rem;
    }
    .history-row:hover { background-color: rgba(255,255,255,0.05); }
    
    /* Renk Kodları */
    .border-win { border-left: 4px solid #00f260; }
    .border-loss { border-left: 4px solid #ff0055; }
    .border-draw { border-left: 4px solid #fce803; }
    
    .text-win { color: #00f260; font-weight: bold; font-family: 'Orbitron'; letter-spacing: 1px; }
    .text-loss { color: #ff0055; font-weight: bold; font-family: 'Orbitron'; letter-spacing: 1px; }
    .text-draw { color: #fce803; font-weight: bold; font-family: 'Orbitron'; letter-spacing: 1px; }

    /* Puan Durumu Tablosu */
    .pl-table { width: 100%; border-collapse: collapse; font-family: 'Rajdhani', sans-serif; color: #fff; font-size: 0.95rem; background-color: transparent; }
    .pl-table th { background-color: #38003c; color: #fff; text-align: center; padding: 12px 8px; font-weight: bold; border-bottom: 2px solid #555; text-transform: uppercase; font-size: 0.8rem; }
    .pl-table th:nth-child(2) { text-align: left; } 
    .pl-table td { padding: 10px 8px; border-bottom: 1px solid #222; vertical-align: middle; text-align: center; }
    .pl-table td:nth-child(2) { text-align: left; } 
    .pl-table tr:nth-child(even) { background-color: rgba(255,255,255,0.02); }
    .pl-table tr:hover { background-color: rgba(255,255,255,0.05); }
    .pos-cell { font-weight: bold; color: #aaa; }
    .team-cell { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 1rem; }
    .form-badges { display: flex; gap: 4px; justify-content: center; }
    .badge { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: white; font-family: sans-serif; }
    .badge-W { background-color: #13CF00; }
    .badge-L { background-color: #D81920; }
    .badge-D { background-color: #76766f; }
    .stat-cell { color: #ddd; }
    .pts-cell { font-weight: bold; font-size: 1.1rem; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- TABLO RENDERING FONKSİYONU ---
def render_league_table_html(df, matches_df, logos):
    if df.empty: return "<div style='text-align:center; padding:20px;'>Veri Yok</div>"
    html = """<table class="pl-table"><thead><tr><th style="width:50px;">Pos</th><th>Club</th><th>Pl</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th><th>Form</th><th>Next</th></tr></thead><tbody>"""
    for _, row in df.iterrows():
        team_name = row['Team']
        form_html = '<div class="form-badges">'
        for res in row['Form']: form_html += f'<div class="badge badge-{res}">{res}</div>'
        form_html += '</div>'
        upcoming = matches_df[((matches_df['HomeTeam'] == team_name) | (matches_df['AwayTeam'] == team_name)) & (matches_df['IsFinished'] == False)].sort_values('DateObj')
        next_logo_html = "-"
        if not upcoming.empty:
            next_match = upcoming.iloc[0]
            opponent = next_match['AwayTeam'] if next_match['HomeTeam'] == team_name else next_match['HomeTeam']
            opp_logo = logos.get(opponent, "")
            if opp_logo: next_logo_html = f'<img src="{opp_logo}" style="width:25px; height:25px; object-fit:contain;" title="vs {opponent}">'
        row_html = f"""<tr><td class="pos-cell">{row['Pos']}</td><td class="team-cell"><img src="{row['Logo']}" style="width:25px; height:25px;">{team_name}</td><td class="stat-cell">{row['Pl']}</td><td class="stat-cell">{row['W']}</td><td class="stat-cell">{row['D']}</td><td class="stat-cell">{row['L']}</td><td class="stat-cell">{row['GF']}</td><td class="stat-cell">{row['GA']}</td><td class="stat-cell">{row['GD']}</td><td class="pts-cell">{row['Pts']}</td><td>{form_html}</td><td style="text-align:center;">{next_logo_html}</td></tr>"""
        html += row_html
    html += "</tbody></table>"
    return html

# --- GRAFİK ---
def plot_fuzzy_chart(var, sim, title, color_hex, val=None):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 2.5))
    fig.patch.set_facecolor('#00000000'); ax.set_facecolor('#00000000')
    for label in var.terms:
        ax.plot(var.universe, var.terms[label].mf, label=label, linewidth=1.5, alpha=0.5)
        ax.fill_between(var.universe, 0, var.terms[label].mf, alpha=0.05)
    plot_val = val
    if val is None:
        try: plot_val = sim.output[var.label]
        except: plot_val = 0
    if plot_val is not None:
        ax.vlines(plot_val, 0, 1, color=color_hex, linewidth=2.5, linestyle='--', zorder=5)
        ax.scatter([plot_val], [0.5], s=100, color='white', edgecolor=color_hex, zorder=10)
    ax.set_title(title, color='white', fontsize=11, pad=10)
    ax.tick_params(labelsize=8, colors='#888')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.set_ylim(0, 1.05); ax.grid(False)
    return fig

def display_fuzzy_table(var, val_home, val_away, name_home, name_away, lang_dict):
    rows = []
    def get_row_data(team_name, val):
        row = {lang_dict["tbl_team"]: team_name, lang_dict["tbl_input"]: val}
        max_degree = 0; dominant_label = ""
        for label in var.terms:
            degree = fuzz.interp_membership(var.universe, var.terms[label].mf, val)
            translated_label = lang_dict["terms"].get(label, label.upper())
            row[translated_label] = f"{degree:.2f}"
            if degree > max_degree: max_degree = degree; dominant_label = translated_label
        row[lang_dict["tbl_decision"]] = f"{dominant_label} (%{int(max_degree*100)})"
        return row
    rows.append(get_row_data(name_home, val_home))
    rows.append(get_row_data(name_away, val_away))
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

def run_slot_effect(player_images, text_msg):
    slot_container = st.empty()
    for i in range(15):
        c1, c2, c3 = random.sample(player_images, 3)
        html_code = f"""<div style="display:flex; justify-content:center; gap:20px; margin: 30px 0;"><div style="background:rgba(255,255,255,0.05); padding:5px; border-radius:15px; border:2px solid #00f260; width:110px; height:120px; display:flex; align-items:center; justify-content:center;"><img src="{c1}" style="width:100px; height:110px; object-fit:cover; border-radius:10px;"></div><div style="background:rgba(255,255,255,0.05); padding:5px; border-radius:15px; border:2px solid #0575e6; width:110px; height:120px; display:flex; align-items:center; justify-content:center;"><img src="{c2}" style="width:100px; height:110px; object-fit:cover; border-radius:10px;"></div><div style="background:rgba(255,255,255,0.05); padding:5px; border-radius:15px; border:2px solid #fce803; width:110px; height:120px; display:flex; align-items:center; justify-content:center;"><img src="{c3}" style="width:100px; height:110px; object-fit:cover; border-radius:10px;"></div></div><div style="text-align:center; font-family:'Orbitron'; color:#ccc; letter-spacing:3px;">{text_msg}</div>"""
        slot_container.markdown(html_code, unsafe_allow_html=True)
        time.sleep(0.05)
    slot_container.empty()

# --- YENİ MAÇ GEÇMİŞİ FONKSİYONU (RENKLİ İSİM + LOGO) ---
def display_match_history(df, team_name, team_logos, lang_dict):
    matches = df[((df["HomeTeam"] == team_name) | (df["AwayTeam"] == team_name)) & (df["IsFinished"] == True)].sort_values("Date", ascending=False)
    if matches.empty: st.write("Veri yok."); return
    for _, row in matches.iterrows():
        is_home = row["HomeTeam"] == team_name
        opp = row["AwayTeam"] if is_home else row["HomeTeam"]
        mys = int(row["FTHG"] if is_home else row["FTAG"])
        ops = int(row["FTAG"] if is_home else row["FTHG"])
        
        # Renk ve Harf Mantığı
        if mys > ops: 
            border_cls = "border-win"; text_cls = "text-win"; res_char = lang_dict["short_w"]
        elif mys < ops: 
            border_cls = "border-loss"; text_cls = "text-loss"; res_char = lang_dict["short_l"]
        else: 
            border_cls = "border-draw"; text_cls = "text-draw"; res_char = lang_dict["short_d"]
            
        # Rakip Logosu
        opp_logo_url = team_logos.get(opp, "")
        img_html = f'<img src="{opp_logo_url}" style="width:20px; height:20px; vertical-align:middle; margin-right:8px;">' if opp_logo_url else ""

        st.markdown(f"""
        <div class="history-row {border_cls}">
            <div class="{text_cls}" style="display:flex; align-items:center;">
                {img_html} VS {opp}
            </div>
            <div class="{text_cls}">
                {mys} - {ops} ({res_char})
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("## 🌍 Language")
lang = st.sidebar.radio("", ["TR", "EN"], label_visibility="collapsed")
T = TRANS[lang]
st.sidebar.markdown("---")
st.sidebar.caption(T["refresh_desc"])
if st.sidebar.button(T["refresh_btn"]): st.cache_data.clear(); st.rerun()

# --- DATA ---
df, team_logos, team_players, player_images = load_all_data()
if df.empty: st.error("Veri alınamadı."); st.stop()
teams = sorted(list(team_logos.keys()))
league_table = calculate_league_table(df, team_logos)

# --- HEADER ---
st.markdown(f'<div class="neon-header">{T["header_title"]}</div>', unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:#666; font-size: 0.9rem; margin-bottom:50px; letter-spacing:2px; text-transform:uppercase;'>{T['header_sub']}</div>", unsafe_allow_html=True)

# --- TABS ---
tab_sim, tab_table, tab_live = st.tabs([T["tab_sim"], T["tab_table"], T["tab_live"]])

# ==========================================
# 1. MAÇ SİMÜLASYONU
# ==========================================
with tab_sim:
    if 'h_idx' not in st.session_state: st.session_state.h_idx = 0
    if 'a_idx' not in st.session_state: st.session_state.a_idx = 1
    def change_team(side, direction):
        key = 'h_idx' if side == 'home' else 'a_idx'
        if direction == 'next': st.session_state[key] = (st.session_state[key] + 1) % len(teams)
        else: st.session_state[key] = (st.session_state[key] - 1) % len(teams)

    h_team = teams[st.session_state.h_idx]
    a_team = teams[st.session_state.a_idx]

    mc1, mc2, mc3 = st.columns([1, 0.2, 1])
    with mc1:
        st.markdown(f"<h3 style='text-align:center; color:#00f260; font-family:Orbitron; letter-spacing:2px;'>🏠 {T['home']}</h3>", unsafe_allow_html=True)
        nl, la, nr = st.columns([0.2, 1, 0.2])
        with nl: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❮", key="h_prev", on_click=change_team, args=('home', 'prev')); st.markdown('</div>', unsafe_allow_html=True)
        with la: st.markdown(f"""<div class="logo-container"><img src="{team_logos[h_team]}" class="logo-center"><div class="team-name-box">{h_team}</div></div>""", unsafe_allow_html=True)
        with nr: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❯", key="h_next", on_click=change_team, args=('home', 'next')); st.markdown('</div>', unsafe_allow_html=True)
    with mc2: st.markdown("""<div style="height:350px; display:flex; align-items:center; justify-content:center;"><div style="width:1px; height:200px; background: linear-gradient(to bottom, transparent, #444, transparent);"></div></div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown(f"<h3 style='text-align:center; color:#0575e6; font-family:Orbitron; letter-spacing:2px;'>✈️ {T['away']}</h3>", unsafe_allow_html=True)
        dl, da, dr = st.columns([0.2, 1, 0.2])
        with dl: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❮", key="a_prev", on_click=change_team, args=('away', 'prev')); st.markdown('</div>', unsafe_allow_html=True)
        with da: st.markdown(f"""<div class="logo-container"><img src="{team_logos[a_team]}" class="logo-center"><div class="team-name-box">{a_team}</div></div>""", unsafe_allow_html=True)
        with dr: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❯", key="a_next", on_click=change_team, args=('away', 'next')); st.markdown('</div>', unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 3, 1])
    with b2:
        st.markdown('<div class="big-btn-container">', unsafe_allow_html=True)
        start = st.button(T["start_btn"], key="start_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if start:
        if h_team == a_team: st.warning(T["warning_same_team"])
        else:
            run_slot_effect(player_images, T["slot_msg"])
            with st.spinner(T["spinner"]):
                h_stats = get_advanced_stats(df, team_players, h_team)
                a_stats = get_advanced_stats(df, team_players, a_team)
                try:
                    if not league_table.empty:
                        h_rank_num = league_table.loc[league_table['Team'] == h_team, 'Pos'].values[0]
                        a_rank_num = league_table.loc[league_table['Team'] == a_team, 'Pos'].values[0]
                        h_stats['fuzzy']['rank'] = round(max(0, (21 - h_rank_num) / 2), 2)
                        a_stats['fuzzy']['rank'] = round(max(0, (21 - a_rank_num) / 2), 2)
                        h_stats['raw']['rank'] = h_rank_num
                        a_stats['raw']['rank'] = a_rank_num
                except: pass
                match_sim.input['form'] = h_stats['fuzzy']['form']; match_sim.input['rank'] = h_stats['fuzzy']['rank']; match_sim.input['goals'] = h_stats['fuzzy']['goals']; match_sim.compute(); res_h = match_sim.output['result']
                match_sim.input['form'] = a_stats['fuzzy']['form']; match_sim.input['rank'] = a_stats['fuzzy']['rank']; match_sim.input['goals'] = a_stats['fuzzy']['goals']; match_sim.compute(); res_a = match_sim.output['result']
                final_h = res_h + 1.0; final_a = res_a; diff = final_h - final_a
                card_sim.input['aggression'] = (h_stats['fuzzy']['cards'] + a_stats['fuzzy']['cards']) / 2
                card_sim.input['tension'] = max(0, min(10 - abs(h_stats['raw']['rank'] - a_stats['raw']['rank']) / 2, 10))
                try: card_sim.compute(); res_chaos = card_sim.output['chaos']
                except: res_chaos = 5.0

            st.markdown("---")
            subtab_res, subtab_stat, subtab_fuzzy = st.tabs([T["subtab_res"], T["subtab_stat"], T["subtab_fuzzy"]])
            
            # SONUÇ
            with subtab_res:
                if diff > 1.5: pred_text = T["wins"]; clr = "#00f260"; glow = "rgba(0, 242, 96, 0.6)"; w_logo = team_logos[h_team]
                elif diff < -1.5: pred_text = T["wins"]; clr = "#00c6ff"; glow = "rgba(0, 198, 255, 0.6)"; w_logo = team_logos[a_team]
                else: pred_text = T["draw"]; clr = "#fce803"; glow = "rgba(252, 232, 3, 0.6)"; w_logo = "https://resources.premierleague.com/premierleague/pl_icon.png"
                st.markdown(f"""<div class="winner-card" style="border-color: {clr}; box-shadow: 0 0 50px {glow};"><h3 style="color:#aaa; letter-spacing:4px; margin:0; font-size: 1rem;">{T['winner_title']}</h3><img src="{w_logo}" style="width: 250px; height: 250px; object-fit: contain; margin: 30px auto; display:block; filter: drop-shadow(0 0 30px {glow}); animation: float 4s infinite;"><div class="result-text" style="color:{clr}; text-shadow: 0 0 20px {glow};">{pred_text}</div><div style="margin-top:20px; color:#ccc; font-family:'Rajdhani'; font-size: 1.2rem;">{T['confidence']}: <b>{min(abs(diff), 9.9):.2f} / 10</b></div></div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if res_chaos > 6.5: st.error(T["prob_chaos"].format(res_chaos), icon="🔥")
                else: st.success(T["prob_chaos_low"].format(res_chaos), icon="🟢")

            # İSTATİSTİK
            with subtab_stat:
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_rank']}</div><div class='stat-value'>{h_stats['raw']['rank']} - {a_stats['raw']['rank']}</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_goals']}</div><div class='stat-value'>{h_stats['raw']['scored']}/{h_stats['raw']['conceded']} - {a_stats['raw']['scored']}/{a_stats['raw']['conceded']}</div></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_form']}</div><div class='stat-value'>{h_stats['raw']['form_points']} - {a_stats['raw']['form_points']}</div></div>", unsafe_allow_html=True)
                c4.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_missing']}</div><div class='stat-value' style='color:#ff4444'>{h_stats['raw']['missing']} - {a_stats['raw']['missing']}</div></div>", unsafe_allow_html=True)
                st.markdown("---")
                hc, ac = st.columns(2)
                with hc:
                    st.markdown(f"### <img src='{team_logos.get(h_team)}' style='width:30px; vertical-align:middle; margin-right:10px;'> {h_team} {T['last_matches']}", unsafe_allow_html=True)
                    if h_stats['raw']['missing_names']: st.warning(T["missing_alert"].format(', '.join(h_stats['raw']['missing_names'])))
                    else: st.success(T["full_squad"])
                    display_match_history(df, h_team, team_logos, T)
                with ac:
                    st.markdown(f"### <img src='{team_logos.get(a_team)}' style='width:30px; vertical-align:middle; margin-right:10px;'> {a_team} {T['last_matches']}", unsafe_allow_html=True)
                    if a_stats['raw']['missing_names']: st.warning(T["missing_alert"].format(', '.join(a_stats['raw']['missing_names'])))
                    else: st.success(T["full_squad"])
                    display_match_history(df, a_team, team_logos, T)

            # FUZZY
            with subtab_fuzzy:
                st.info(T["graph_info"])
                match_sim.input['form'] = h_stats['fuzzy']['form']; match_sim.input['rank'] = h_stats['fuzzy']['rank']; match_sim.input['goals'] = h_stats['fuzzy']['goals']; match_sim.compute()
                fig_h_form = plot_fuzzy_chart(form, match_sim, f"{T['g_form']} ({h_stats['fuzzy']['form']})", "#00f260", val=h_stats['fuzzy']['form'])
                fig_h_rank = plot_fuzzy_chart(rank, match_sim, f"{T['g_rank']} ({h_stats['fuzzy']['rank']})", "#00f260", val=h_stats['fuzzy']['rank'])
                fig_h_goals = plot_fuzzy_chart(goals, match_sim, f"{T['g_goals']} ({h_stats['fuzzy']['goals']})", "#00f260", val=h_stats['fuzzy']['goals'])
                match_sim.input['form'] = a_stats['fuzzy']['form']; match_sim.input['rank'] = a_stats['fuzzy']['rank']; match_sim.input['goals'] = a_stats['fuzzy']['goals']; match_sim.compute()
                fig_a_form = plot_fuzzy_chart(form, match_sim, f"{T['g_form']} ({a_stats['fuzzy']['form']})", "#00c6ff", val=a_stats['fuzzy']['form'])
                fig_a_rank = plot_fuzzy_chart(rank, match_sim, f"{T['g_rank']} ({a_stats['fuzzy']['rank']})", "#00c6ff", val=a_stats['fuzzy']['rank'])
                fig_a_goals = plot_fuzzy_chart(goals, match_sim, f"{T['g_goals']} ({a_stats['fuzzy']['goals']})", "#00c6ff", val=a_stats['fuzzy']['goals'])

                c1, c2 = st.columns(2); c1.pyplot(fig_h_form); c2.pyplot(fig_a_form)
                display_fuzzy_table(form, h_stats['fuzzy']['form'], a_stats['fuzzy']['form'], h_team, a_team, T)
                st.markdown("---")
                c3, c4 = st.columns(2); c3.pyplot(fig_h_rank); c4.pyplot(fig_a_rank)
                display_fuzzy_table(rank, h_stats['fuzzy']['rank'], a_stats['fuzzy']['rank'], h_team, a_team, T)
                st.markdown("---")
                c5, c6 = st.columns(2); c5.pyplot(fig_h_goals); c6.pyplot(fig_a_goals)
                display_fuzzy_table(goals, h_stats['fuzzy']['goals'], a_stats['fuzzy']['goals'], h_team, a_team, T)
                
                # --- SONUÇ VE ATMOSFER ---
                st.markdown("---")
                st.markdown(f"### {T['final_res']}")
                match_sim.input['form'] = h_stats['fuzzy']['form']; match_sim.input['rank'] = h_stats['fuzzy']['rank']; match_sim.input['goals'] = h_stats['fuzzy']['goals']; match_sim.compute()
                fig_h_res = plot_fuzzy_chart(result, match_sim, T["g_result"].format(h_team), "#ffffff")
                match_sim.input['form'] = a_stats['fuzzy']['form']; match_sim.input['rank'] = a_stats['fuzzy']['rank']; match_sim.input['goals'] = a_stats['fuzzy']['goals']; match_sim.compute()
                fig_a_res = plot_fuzzy_chart(result, match_sim, T["g_result"].format(a_team), "#ffffff")
                r1, r2, r3 = st.columns([1, 1, 1])
                r1.markdown(f"<div style='text-align:center'>{T['prob_win'].format(h_team)}</div>", unsafe_allow_html=True); r1.pyplot(fig_h_res)
                r2.markdown(f"<div style='text-align:center'>{T['prob_chaos']}</div>", unsafe_allow_html=True); r2.pyplot(plot_fuzzy_chart(chaos, card_sim, f"Atmosfer: {res_chaos:.2f}", "#ff0055"))
                r3.markdown(f"<div style='text-align:center'>{T['prob_win'].format(a_team)}</div>", unsafe_allow_html=True); r3.pyplot(fig_a_res)

# ==========================================
# 2. PUAN DURUMU (ÖZEL HTML TABLO + NEXT MATCH)
# ==========================================
with tab_table:
    st.markdown("### Premier League 2024/25")
    if not league_table.empty:
        # Tabloyu oluşturmak için df (tüm maçlar) ve team_logos'u da gönderiyoruz
        st.markdown(render_league_table_html(league_table, df, team_logos), unsafe_allow_html=True)
    else: st.warning("Puan durumu verisi oluşturulamadı.")

# ==========================================
# 3. CANLI SKORLAR
# ==========================================
with tab_live:
    today = datetime.now().date()
    todays_matches = df[df['Date'] == today].sort_values('DateObj')
    if todays_matches.empty: st.info(T["live_no_match"])
    else:
        st.markdown('<div class="live-grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap:15px;">', unsafe_allow_html=True)
        for _, match in todays_matches.iterrows():
            if match['IsLive']: status = "CANLI"; css = "live"; score = f"{int(match['FTHG'])}-{int(match['FTAG'])}"
            elif match['IsFinished']: status = "BİTTİ"; css = "finished"; score = f"{int(match['FTHG'])}-{int(match['FTAG'])}"
            else: status = match['DateObj'].strftime("%H:%M"); css = "future"; score = "v"
            st.markdown(f"""<div class="live-card {css}"><div class="live-time"><span>{status}</span> <span style="color:#ff0055">PL</span></div><div class="live-teams"><img src="{team_logos.get(match['HomeTeam'],'')}" style="width:25px; height:25px;"><span>{match['HomeTeam']}</span><span class="live-score">{score}</span><span>{match['AwayTeam']}</span><img src="{team_logos.get(match['AwayTeam'],'')}" style="width:25px; height:25px;"></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)