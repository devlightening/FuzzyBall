import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import random  # <--- YENİ EKLENDİ (Rastgele ikonlar için)
from data_utils import load_all_data, get_advanced_stats
from fuzzy_system import match_sim, card_sim, form, rank, goals, result, aggression, tension, chaos

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="NEO-FOOTBALL ULTIMATE", page_icon="⚽", layout="wide")

# --- DİL SÖZLÜĞÜ (TRANSLATION DICTIONARY) ---
TRANS = {
    "TR": {
        "header_title": "NEO-PREDICTOR ULTIMATE",
        "header_sub": "Yapay Zeka Destekli Futbol Analiz Motoru",
        "home": "EV SAHİBİ",
        "away": "DEPLASMAN",
        "start_btn": "SİMÜLASYONU BAŞLAT",
        "warning_same_team": "⚠️ Lütfen iki farklı takım seçin.",
        "spinner": "Mamdani Çıkarım Mekanizması Çalışıyor...",
        "tab1": "⚡ ANALİZ SONUCU",
        "tab2": "📈 İSTATİSTİK DETAYLARI",
        "tab3": "🧠 FUZZY GRAFİKLERİ",
        "winner_title": "YAPAY ZEKA TAHMİNİ (Mamdani)",
        "confidence": "Güven Skoru",
        "wins": "KAZANIR",
        "draw": "BERABERLİK",
        "chaos_high": "🔥 YÜKSEK TANSİYON! Kaos Skoru: {0:.2f}/10. Kırmızı kart ihtimali yüksek.",
        "chaos_low": "🟢 Temiz Maç Beklentisi. Kaos Skoru: {0:.2f}/10",
        "stat_rank": "LİG SIRASI",
        "stat_goals": "GOL (A/Y)",
        "stat_form": "FORM PUANI",
        "stat_missing": "EKSİK OYUNCU",
        "last_matches": "{0} Son Maçlar",
        "missing_alert": "🚨 Eksikler: {0}",
        "full_squad": "✅ Tam Kadro",
        "graph_info": "Bu grafikler Yapay Zeka'nın kullandığı 3 Temel Girdi ve Karar Çıktısını gösterir.",
        "g_form": "GİRDİ 1: Form",
        "g_rank": "GİRDİ 2: Sıralama",
        "g_goals": "GİRDİ 3: Gol Gücü",
        "g_result": "SONUÇ: {0} Şansı",
        "g_chaos": "ORTAK: Kaos Tahmini",
        "res_win": "G", "res_draw": "B", "res_loss": "M",
        "comp_home": "EV SAHİBİ GİRDİLERİ",
        "comp_away": "DEPLASMAN GİRDİLERİ",
        "final_res": "🏆 SONUÇ VE ATMOSFER",
        "prob_win": "{0} Galibiyet İhtimali",
        "prob_chaos": "🔥 KAOS / KART RİSKİ (ORTAK)",
        "loading_error": "Veri kaynağına erişilemedi."
    },
    "EN": {
        "header_title": "NEO-PREDICTOR ULTIMATE",
        "header_sub": "AI Powered Football Analytics Engine",
        "home": "HOME TEAM",
        "away": "AWAY TEAM",
        "start_btn": "START SIMULATION",
        "warning_same_team": "⚠️ Please select two different teams.",
        "spinner": "Running Mamdani Inference System...",
        "tab1": "⚡ PREDICTION RESULT",
        "tab2": "📈 DETAILED STATS",
        "tab3": "🧠 FUZZY LOGIC CHARTS",
        "winner_title": "AI PREDICTION (Mamdani)",
        "confidence": "Confidence Score",
        "wins": "WINS",
        "draw": "DRAW",
        "chaos_high": "🔥 HIGH TENSION! Chaos Score: {0:.2f}/10. High probability of red cards.",
        "chaos_low": "🟢 Clean Match Expected. Chaos Score: {0:.2f}/10",
        "stat_rank": "LEAGUE RANK",
        "stat_goals": "GOALS (F/A)",
        "stat_form": "FORM POINTS",
        "stat_missing": "MISSING PLAYERS",
        "last_matches": "{0} Last Matches",
        "missing_alert": "🚨 Missing: {0}",
        "full_squad": "✅ Full Squad",
        "graph_info": "These charts show the 3 Core Inputs and Decision Output used by the AI.",
        "g_form": "INPUT 1: Form",
        "g_rank": "INPUT 2: Rank",
        "g_goals": "INPUT 3: Goal Power",
        "g_result": "OUTPUT: {0} Chance",
        "g_chaos": "SHARED: Chaos Prediction",
        "res_win": "W", "res_draw": "D", "res_loss": "L",
        "comp_home": "HOME TEAM INPUTS",
        "comp_away": "AWAY TEAM INPUTS",
        "final_res": "🏆 RESULT & ATMOSPHERE",
        "prob_win": "{0} Win Probability",
        "prob_chaos": "🔥 CHAOS / CARD RISK (SHARED)",
        "loading_error": "Unable to access data source."
    }
}

# --- DİL SEÇİMİ (SIDEBAR) ---
st.sidebar.markdown("## 🌍 Language / Dil")
selected_lang = st.sidebar.radio("", ["TR", "EN"], index=0) 
T = TRANS[selected_lang]

# --- CSS TASARIMI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&display=swap');
    .stApp { background-color: #020202; color: #e0e0e0; font-family: 'Rajdhani', sans-serif; background-image: radial-gradient(circle at 50% 30%, #111 0%, #000 90%); }
    .neon-header { font-family: 'Orbitron', sans-serif; text-align: center; font-size: 3.5rem; font-weight: 900; background: -webkit-linear-gradient(#00f260, #0575e6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 50px rgba(0, 242, 96, 0.3); margin-bottom: 40px; letter-spacing: 4px; }
    .logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; }
    .logo-center { width: 200px; height: 200px; object-fit: contain; filter: drop-shadow(0 0 30px rgba(0, 242, 96, 0.5)); transform: scale(1.1); z-index: 10; animation: float 3s ease-in-out infinite; transition: all 0.5s ease; }
    @keyframes float { 0% { transform: translateY(0px) scale(1.1); } 50% { transform: translateY(-10px) scale(1.1); } 100% { transform: translateY(0px) scale(1.1); } }
    .team-name-box { font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 700; margin-top: 15px; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.5); background: rgba(255,255,255,0.05); padding: 8px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .big-btn-container { display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 30px; }
    .big-btn-container button { width: 100% !important; min-width: 300px !important; background: linear-gradient(90deg, #00f260 0%, #0575e6 100%) !important; color: white !important; font-family: 'Orbitron', sans-serif !important; font-size: 1.5rem !important; font-weight: 800 !important; padding: 18px 0 !important; border-radius: 12px !important; border: 2px solid rgba(255,255,255,0.2) !important; box-shadow: 0 0 40px rgba(0, 242, 96, 0.3) !important; transition: all 0.3s ease !important; white-space: nowrap !important; }
    .big-btn-container button:hover { transform: scale(1.02) !important; box-shadow: 0 0 60px rgba(5, 117, 230, 0.6) !important; }
    .nav-btn-container button { border-radius: 50% !important; width: 50px !important; height: 50px !important; background: rgba(0,0,0,0.5) !important; border: 1px solid #444 !important; color: #888 !important; font-size: 1.5rem !important; padding: 0 !important; margin: 0 auto !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    .nav-btn-container button:hover { color: #00f260 !important; border-color: #00f260 !important; box-shadow: 0 0 15px rgba(0, 242, 96, 0.4) !important; }
    .winner-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; text-align: center; margin-top: 30px; backdrop-filter: blur(10px); }
    .result-text { font-family: 'Orbitron'; font-size: 3.5rem; font-weight: 900; margin-top: 15px; letter-spacing: 2px; }
    .stat-card { background: linear-gradient(180deg, rgba(30,30,40,0.95), rgba(10,10,10,0.95)); border-top: 3px solid #0575e6; padding: 20px; text-align: center; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stat-value { font-size: 1.8rem; font-weight: bold; color: white; }
    .stat-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .history-row { padding: 12px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; font-size: 1rem; transition: background 0.2s; }
    .history-row:hover { background: rgba(255,255,255,0.05); }
    .win-tag { border-left: 4px solid #00f260; color: #00f260; }
    .loss-tag { border-left: 4px solid #ff0055; color: #ff0055; }
    .draw-tag { border-left: 4px solid #fce803; color: #fce803; }
</style>
""", unsafe_allow_html=True)

# --- GRAFİK FONKSİYONU ---
def plot_fuzzy_chart(var, sim, title, color_hex, val=None):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 2.5))
    fig.patch.set_facecolor('#00000000')
    ax.set_facecolor('#00000000')
    
    for label in var.terms:
        ax.plot(var.universe, var.terms[label].mf, label=label, linewidth=1.5, alpha=0.7)
        ax.fill_between(var.universe, 0, var.terms[label].mf, alpha=0.1)
    
    if val is not None:
        plot_val = val
        ax.vlines(plot_val, 0, 1, color=color_hex, linewidth=2.5, linestyle='--')
        ax.scatter([plot_val], [0.5], s=100, color=color_hex, zorder=10)
    else:
        try:
            plot_val = sim.output[var.label]
            ax.vlines(plot_val, 0, 1, color=color_hex, linewidth=2.5, linestyle='--')
            ax.scatter([plot_val], [0.5], s=100, color=color_hex, zorder=10)
        except: pass
    
    ax.set_title(title, color='white', fontsize=10)
    ax.tick_params(labelsize=8, colors='#888')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.grid(False)
    return fig

# --- SLOT MAKİNESİ (FREESPIN) EFEKTİ ---
def run_slot_effect():
    slot_container = st.empty()
    # Slot ikonları (Futbol ve Şans karışık)
    icons = ["⚽", "🥅", "🏆", "🔥", "❌", "💰", "🎲", "7️⃣", "🍒", "💎", "⚡"]
    
    # 20 kez hızlıca döndür
    for i in range(20):
        c1, c2, c3 = random.sample(icons, 3)
        html_code = f"""
        <div style="display:flex; justify-content:center; gap:20px; margin: 30px 0;">
            <div style="font-size:60px; background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; border:2px solid #00f260; width:100px; text-align:center;">{c1}</div>
            <div style="font-size:60px; background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; border:2px solid #0575e6; width:100px; text-align:center;">{c2}</div>
            <div style="font-size:60px; background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; border:2px solid #fce803; width:100px; text-align:center;">{c3}</div>
        </div>
        <div style="text-align:center; font-family:'Orbitron'; color:#ccc; letter-spacing:3px;">ANALYZING...</div>
        """
        slot_container.markdown(html_code, unsafe_allow_html=True)
        time.sleep(0.08) # Hız ayarı
    
    slot_container.empty() # Efekti temizle

# --- MAÇ GEÇMİŞİ FONKSİYONU ---
def display_match_history(df, team_name, lang_dict):
    matches = df[(df["HomeTeam"] == team_name) | (df["AwayTeam"] == team_name)].sort_values("Date", ascending=False)
    if matches.empty: st.write("Veri yok."); return
    for _, row in matches.iterrows():
        is_home = row["HomeTeam"] == team_name
        opp = row["AwayTeam"] if is_home else row["HomeTeam"]
        mys = int(row["FTHG"] if is_home else row["FTAG"])
        ops = int(row["FTAG"] if is_home else row["FTHG"])
        if mys > ops: tag_class = "win-tag"; res_text = lang_dict["res_win"]
        elif mys < ops: tag_class = "loss-tag"; res_text = lang_dict["res_loss"]
        else: tag_class = "draw-tag"; res_text = lang_dict["res_draw"]
        st.markdown(f"""<div class="history-row {tag_class}"><div style="font-weight:bold;">VS {opp}</div><div style="font-family:'Orbitron';">{mys} - {ops} ({res_text})</div></div>""", unsafe_allow_html=True)

# --- ANA PROGRAM ---
st.markdown(f'<div class="neon-header">{T["header_title"]}</div>', unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:#666; font-size: 0.9rem; margin-bottom:50px; letter-spacing:2px; text-transform:uppercase;'>{T['header_sub']}</div>", unsafe_allow_html=True)

df, team_logos, team_players = load_all_data()
if df.empty: st.error(T["loading_error"]); st.stop()
teams = sorted(list(team_logos.keys()))
if 'h_index' not in st.session_state: st.session_state.h_index = 0
if 'a_index' not in st.session_state: st.session_state.a_index = 1
def change_team(side, direction):
    key = 'h_index' if side == 'home' else 'a_index'
    if direction == 'next': st.session_state[key] = (st.session_state[key] + 1) % len(teams)
    else: st.session_state[key] = (st.session_state[key] - 1) % len(teams)

mc1, mc2, mc3 = st.columns([1, 0.15, 1])
with mc1:
    st.markdown(f"<h3 style='text-align:center; color:#00f260; font-family:Orbitron; letter-spacing:2px;'>🏠 {T['home']}</h3>", unsafe_allow_html=True)
    idx = st.session_state.h_index
    nl, la, nr = st.columns([0.2, 1, 0.2])
    with nl: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❮", key="h_prev", on_click=change_team, args=('home', 'prev')); st.markdown('</div>', unsafe_allow_html=True)
    with la: st.markdown(f"""<div class="logo-container"><img src="{team_logos[teams[idx]]}" class="logo-center"><div class="team-name-box">{teams[idx]}</div></div>""", unsafe_allow_html=True)
    with nr: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❯", key="h_next", on_click=change_team, args=('home', 'next')); st.markdown('</div>', unsafe_allow_html=True)
with mc2: st.markdown("""<div style="height:350px; display:flex; align-items:center; justify-content:center;"><div style="width:1px; height:200px; background: linear-gradient(to bottom, transparent, #444, transparent);"></div></div>""", unsafe_allow_html=True)
with mc3:
    st.markdown(f"<h3 style='text-align:center; color:#0575e6; font-family:Orbitron; letter-spacing:2px;'>✈️ {T['away']}</h3>", unsafe_allow_html=True)
    idx_a = st.session_state.a_index
    dl, da, dr = st.columns([0.2, 1, 0.2])
    with dl: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❮", key="a_prev", on_click=change_team, args=('away', 'prev')); st.markdown('</div>', unsafe_allow_html=True)
    with da: st.markdown(f"""<div class="logo-container"><img src="{team_logos[teams[idx_a]]}" class="logo-center" style="filter: drop-shadow(0 0 30px rgba(5, 117, 230, 0.6));"><div class="team-name-box">{teams[idx_a]}</div></div>""", unsafe_allow_html=True)
    with dr: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❯", key="a_next", on_click=change_team, args=('away', 'next')); st.markdown('</div>', unsafe_allow_html=True)
h_team = teams[st.session_state.h_index]
a_team = teams[st.session_state.a_index]
st.markdown("<br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([1, 3, 1])
with b2:
    st.markdown('<div class="big-btn-container">', unsafe_allow_html=True)
    start = st.button(T["start_btn"], key="start_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if start:
    if h_team == a_team: st.warning(T["warning_same_team"])
    else:
        # --- FREESPIN EFEKTİ BURADA ÇAĞRILIYOR ---
        run_slot_effect()
        
        with st.spinner(T["spinner"]):
            h_stats = get_advanced_stats(df, team_players, h_team)
            a_stats = get_advanced_stats(df, team_players, a_team)
            
            match_sim.input['form'] = h_stats['fuzzy']['form']
            match_sim.input['rank'] = h_stats['fuzzy']['rank']
            match_sim.input['goals'] = h_stats['fuzzy']['goals']
            match_sim.compute()
            res_h = match_sim.output['result']
            
            match_sim.input['form'] = a_stats['fuzzy']['form']
            match_sim.input['rank'] = a_stats['fuzzy']['rank']
            match_sim.input['goals'] = a_stats['fuzzy']['goals']
            match_sim.compute()
            res_a = match_sim.output['result']
            
            final_h = res_h + 1.0; final_a = res_a
            
            match_aggression = (h_stats['fuzzy']['cards'] + a_stats['fuzzy']['cards']) / 2
            rank_diff = abs(h_stats['raw']['rank'] - a_stats['raw']['rank'])
            match_tension = max(0, min(10 - (rank_diff / 2), 10))
            card_sim.input['aggression'] = match_aggression
            card_sim.input['tension'] = match_tension
            try: card_sim.compute(); res_chaos = card_sim.output['chaos']
            except: res_chaos = 5.0

        st.markdown("---")
        t1, t2, t3 = st.tabs([T["tab1"], T["tab2"], T["tab3"]])
        with t1:
            diff = final_h - final_a
            if diff > 1.5: pred_text = T["wins"]; clr = "#00f260"; glow_clr = "rgba(0, 242, 96, 0.6)"; winner_logo = team_logos.get(h_team, "")
            elif diff < -1.5: pred_text = T["wins"]; clr = "#00c6ff"; glow_clr = "rgba(0, 198, 255, 0.6)"; winner_logo = team_logos.get(a_team, "")
            else: pred_text = T["draw"]; clr = "#fce803"; glow_clr = "rgba(252, 232, 3, 0.6)"; winner_logo = "https://resources.premierleague.com/premierleague/pl_icon.png"
            html_content = f"""<div class="winner-card" style="border-color: {clr}; box-shadow: 0 0 50px {glow_clr};"><h3 style="color:#aaa; letter-spacing:4px; margin:0; font-size: 1rem;">{T['winner_title']}</h3><img src="{winner_logo}" style="width: 250px; height: 250px; object-fit: contain; margin: 30px auto; display:block; filter: drop-shadow(0 0 30px {glow_clr}); animation: float 4s infinite;"><div class="result-text" style="color:{clr}; text-shadow: 0 0 20px {glow_clr};">{pred_text}</div><div style="margin-top:20px; color:#ccc; font-family:'Rajdhani'; font-size: 1.2rem;">{T['confidence']}: <b>{min(abs(diff), 9.9):.2f} / 10</b></div></div>"""
            st.markdown(html_content, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if res_chaos > 6.5: st.error(T["chaos_high"].format(res_chaos))
            else: st.success(T["chaos_low"].format(res_chaos))
        with t2:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_rank']}</div><div class='stat-value'>{h_stats['raw']['rank']} - {a_stats['raw']['rank']}</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_goals']}</div><div class='stat-value'>{h_stats['raw']['scored']}/{h_stats['raw']['conceded']} - {a_stats['raw']['scored']}/{a_stats['raw']['conceded']}</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_form']}</div><div class='stat-value'>{h_stats['raw']['form_points']} - {a_stats['raw']['form_points']}</div></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='stat-card'><div class='stat-label'>{T['stat_missing']}</div><div class='stat-value' style='color:#ff4444'>{h_stats['raw']['missing']} - {a_stats['raw']['missing']}</div></div>", unsafe_allow_html=True)
            st.markdown("---")
            hc, ac = st.columns(2)
            with hc:
                st.subheader(T["last_matches"].format(h_team))
                if h_stats['raw']['missing_names']: st.warning(T["missing_alert"].format(', '.join(h_stats['raw']['missing_names'])))
                else: st.success(T["full_squad"])
                display_match_history(df, h_team, T)
            with ac:
                st.subheader(T["last_matches"].format(a_team))
                if a_stats['raw']['missing_names']: st.warning(T["missing_alert"].format(', '.join(a_stats['raw']['missing_names'])))
                else: st.success(T["full_squad"])
                display_match_history(df, a_team, T)
        with t3:
            st.markdown(f"""<div style="text-align:center; margin-bottom:20px;"><span style="color:#00f260; font-size:1.5rem; font-weight:bold; margin-right:20px;">🏠 {h_team}</span><span style="color:#666; font-size:1.2rem;">VS</span><span style="color:#00c6ff; font-size:1.5rem; font-weight:bold; margin-left:20px;">✈️ {a_team}</span></div>""", unsafe_allow_html=True)
            st.info(T["graph_info"])
            match_sim.input['form'] = h_stats['fuzzy']['form']; match_sim.input['rank'] = h_stats['fuzzy']['rank']; match_sim.input['goals'] = h_stats['fuzzy']['goals']; match_sim.compute()
            fig_h_form = plot_fuzzy_chart(form, match_sim, f"{T['g_form']} ({h_stats['fuzzy']['form']})", "#00f260", val=h_stats['fuzzy']['form'])
            fig_h_rank = plot_fuzzy_chart(rank, match_sim, f"{T['g_rank']} ({h_stats['fuzzy']['rank']})", "#00f260", val=h_stats['fuzzy']['rank'])
            fig_h_goals = plot_fuzzy_chart(goals, match_sim, f"{T['g_goals']} ({h_stats['fuzzy']['goals']})", "#00f260", val=h_stats['fuzzy']['goals'])
            fig_h_res = plot_fuzzy_chart(result, match_sim, T["g_result"].format(h_team), "#ffffff")

            match_sim.input['form'] = a_stats['fuzzy']['form']; match_sim.input['rank'] = a_stats['fuzzy']['rank']; match_sim.input['goals'] = a_stats['fuzzy']['goals']; match_sim.compute()
            fig_a_form = plot_fuzzy_chart(form, match_sim, f"{T['g_form']} ({a_stats['fuzzy']['form']})", "#00c6ff", val=a_stats['fuzzy']['form'])
            fig_a_rank = plot_fuzzy_chart(rank, match_sim, f"{T['g_rank']} ({a_stats['fuzzy']['rank']})", "#00c6ff", val=a_stats['fuzzy']['rank'])
            fig_a_goals = plot_fuzzy_chart(goals, match_sim, f"{T['g_goals']} ({a_stats['fuzzy']['goals']})", "#00c6ff", val=a_stats['fuzzy']['goals'])
            fig_a_res = plot_fuzzy_chart(result, match_sim, T["g_result"].format(a_team), "#ffffff")

            c1, c2 = st.columns(2)
            c1.markdown(f"<h4 style='text-align:center; color:#00f260'>{T['comp_home']}</h4>", unsafe_allow_html=True)
            c2.markdown(f"<h4 style='text-align:center; color:#00c6ff'>{T['comp_away']}</h4>", unsafe_allow_html=True)
            col1, col2 = st.columns(2); col1.pyplot(fig_h_form); col2.pyplot(fig_a_form)
            col3, col4 = st.columns(2); col3.pyplot(fig_h_rank); col4.pyplot(fig_a_rank)
            col5, col6 = st.columns(2); col5.pyplot(fig_h_goals); col6.pyplot(fig_a_goals)
            st.markdown("---")
            st.markdown(f"<h4 style='text-align:center;'>{T['final_res']}</h4>", unsafe_allow_html=True)
            r1, r2, r3 = st.columns([1, 1, 1])
            r1.markdown(f"<div style='text-align:center'>{T['prob_win'].format(h_team)}</div>", unsafe_allow_html=True); r1.pyplot(fig_h_res)
            r2.markdown(f"<div style='text-align:center'>{T['prob_chaos']}</div>", unsafe_allow_html=True); r2.pyplot(plot_fuzzy_chart(chaos, card_sim, f"Atmosfer: {res_chaos:.2f}", "#ff0055"))
            r3.markdown(f"<div style='text-align:center'>{T['prob_win'].format(a_team)}</div>", unsafe_allow_html=True); r3.pyplot(fig_a_res)