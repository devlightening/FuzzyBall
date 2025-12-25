import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
from data_utils import load_all_data, get_advanced_stats
# Fuzzy importları
from fuzzy_system import match_sim, card_sim, form, rank, goals, result, aggression, tension, chaos

st.set_page_config(page_title="NEO-FOOTBALL ULTIMATE", page_icon="⚽", layout="wide")

# CSS TASARIMI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&display=swap');

    .stApp { background-color: #020202; color: #e0e0e0; font-family: 'Rajdhani', sans-serif; background-image: radial-gradient(circle at 50% 30%, #111 0%, #000 90%); }
    .neon-header { font-family: 'Orbitron', sans-serif; text-align: center; font-size: 3.5rem; font-weight: 900; background: -webkit-linear-gradient(#00f260, #0575e6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 50px rgba(0, 242, 96, 0.3); margin-bottom: 40px; letter-spacing: 4px; }
    
    .logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; }
    .logo-side { width: 90px; height: 90px; object-fit: contain; filter: blur(3px) grayscale(100%); opacity: 0.3; transform: scale(0.8); transition: all 0.5s ease; }
    .logo-center { width: 200px; height: 200px; object-fit: contain; filter: drop-shadow(0 0 30px rgba(0, 242, 96, 0.5)); transform: scale(1.1); z-index: 10; animation: float 3s ease-in-out infinite; transition: all 0.5s ease; }
    @keyframes float { 0% { transform: translateY(0px) scale(1.1); } 50% { transform: translateY(-10px) scale(1.1); } 100% { transform: translateY(0px) scale(1.1); } }
    
    .team-name-box { font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 700; margin-top: 15px; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.5); background: rgba(255,255,255,0.05); padding: 8px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    
    .big-btn-container { display: flex; justify-content: center; width: 100%; margin-top: 30px; }
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

def plot_fuzzy_chart(var, sim, title, color_hex):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 2.5))
    fig.patch.set_facecolor('#00000000'); ax.set_facecolor('#00000000')
    for label in var.terms:
        ax.plot(var.universe, var.terms[label].mf, label=label, linewidth=1.5, alpha=0.7)
        ax.fill_between(var.universe, 0, var.terms[label].mf, alpha=0.1)
    try:
        val = sim.output[var.label]
        ax.vlines(val, 0, 1, color=color_hex, linewidth=2.5, linestyle='--')
        ax.scatter([val], [0.5], s=100, color=color_hex, zorder=10)
    except: pass
    ax.set_title(title, color='white', fontsize=10); ax.tick_params(labelsize=8, colors='#888'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.grid(False)
    return fig

def display_match_history(df, team_name):
    matches = df[(df["HomeTeam"] == team_name) | (df["AwayTeam"] == team_name)].sort_values("Date", ascending=False)
    if matches.empty: st.write("Veri yok."); return
    for _, row in matches.iterrows():
        is_home = row["HomeTeam"] == team_name
        opp = row["AwayTeam"] if is_home else row["HomeTeam"]
        mys = int(row["FTHG"] if is_home else row["FTAG"])
        ops = int(row["FTAG"] if is_home else row["FTHG"])
        if mys > ops: tag_class = "win-tag"; res_text = "G"
        elif mys < ops: tag_class = "loss-tag"; res_text = "M"
        else: tag_class = "draw-tag"; res_text = "B"
        st.markdown(f"""<div class="history-row {tag_class}"><div style="font-weight:bold;">VS {opp}</div><div style="font-family:'Orbitron';">{mys} - {ops} ({res_text})</div></div>""", unsafe_allow_html=True)

# ANA PROGRAM
st.markdown('<div class="neon-header">NEO-PREDICTOR ULTIMATE</div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#666; font-size: 0.9rem; margin-bottom:50px; letter-spacing:2px; text-transform:uppercase;'>AI Powered Football Analytics Engine</div>", unsafe_allow_html=True)

df, team_logos, team_players = load_all_data()
if df.empty: st.error("Veri kaynağına erişilemedi."); st.stop()
teams = sorted(list(team_logos.keys()))

if 'h_index' not in st.session_state: st.session_state.h_index = 0
if 'a_index' not in st.session_state: st.session_state.a_index = 1

def change_team(side, direction):
    key = 'h_index' if side == 'home' else 'a_index'
    if direction == 'next': st.session_state[key] = (st.session_state[key] + 1) % len(teams)
    else: st.session_state[key] = (st.session_state[key] - 1) % len(teams)

mc1, mc2, mc3 = st.columns([1, 0.15, 1])

with mc1:
    st.markdown("<h3 style='text-align:center; color:#00f260; font-family:Orbitron; letter-spacing:2px;'>🏠 EV SAHİBİ</h3>", unsafe_allow_html=True)
    idx = st.session_state.h_index
    nl, la, nr = st.columns([0.2, 1, 0.2])
    with nl: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❮", key="h_prev", on_click=change_team, args=('home', 'prev')); st.markdown('</div>', unsafe_allow_html=True)
    with la: st.markdown(f"""<div class="logo-container"><img src="{team_logos[teams[idx]]}" class="logo-center"><div class="team-name-box">{teams[idx]}</div></div>""", unsafe_allow_html=True)
    with nr: st.write(""); st.write(""); st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True); st.button("❯", key="h_next", on_click=change_team, args=('home', 'next')); st.markdown('</div>', unsafe_allow_html=True)

with mc2: st.markdown("""<div style="height:350px; display:flex; align-items:center; justify-content:center;"><div style="width:1px; height:200px; background: linear-gradient(to bottom, transparent, #444, transparent);"></div></div>""", unsafe_allow_html=True)

with mc3:
    st.markdown("<h3 style='text-align:center; color:#0575e6; font-family:Orbitron; letter-spacing:2px;'>✈️ DEPLASMAN</h3>", unsafe_allow_html=True)
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
    start = st.button("SİMÜLASYONU BAŞLAT", key="start_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if start:
    if h_team == a_team:
        st.warning("⚠️ Lütfen iki farklı takım seçin.")
    else:
        with st.spinner("Mamdani Çıkarım Mekanizması Çalışıyor..."):
            time.sleep(1)
            h_stats = get_advanced_stats(df, team_players, h_team)
            a_stats = get_advanced_stats(df, team_players, a_team)
            
            # --- MAMDANI SİMÜLASYONU (EV SAHİBİ) ---
            match_sim.input['form'] = h_stats['fuzzy']['form']
            match_sim.input['rank'] = h_stats['fuzzy']['rank']
            match_sim.input['goals'] = h_stats['fuzzy']['goals']
            match_sim.compute()
            res_h = match_sim.output['result']
            
            # --- MAMDANI SİMÜLASYONU (DEPLASMAN) ---
            match_sim.input['form'] = a_stats['fuzzy']['form']
            match_sim.input['rank'] = a_stats['fuzzy']['rank']
            match_sim.input['goals'] = a_stats['fuzzy']['goals']
            match_sim.compute()
            res_a = match_sim.output['result']
            
            final_h = res_h + 1.0 # Saha avantajı
            final_a = res_a
            
            # --- KART SİSTEMİ (GÜVENLİK KİLİTLİ) ---
            match_aggression = (h_stats['fuzzy']['cards'] + a_stats['fuzzy']['cards']) / 2
            rank_diff = abs(h_stats['raw']['rank'] - a_stats['raw']['rank'])
            match_tension = max(0, min(10 - (rank_diff / 2), 10))
            
            card_sim.input['aggression'] = match_aggression
            card_sim.input['tension'] = match_tension
            
            # --- TRY-EXCEPT İLE CRASH ÖNLEME ---
            try:
                card_sim.compute()
                res_chaos = card_sim.output['chaos']
            except:
                res_chaos = 5.0 # Hata olursa varsayılan (Normal) değeri ata

        st.markdown("---")
        t1, t2, t3 = st.tabs(["⚡ ANALİZ SONUCU", "📈 İSTATİSTİK DETAYLARI", "🧠 FUZZY GRAFİKLERİ"])
        
        with t1:
            diff = final_h - final_a
            if diff > 1.5: pred_text = "KAZANIR"; clr = "#00f260"; glow_clr = "rgba(0, 242, 96, 0.6)"; winner_logo = team_logos.get(h_team, "")
            elif diff < -1.5: pred_text = "KAZANIR"; clr = "#00c6ff"; glow_clr = "rgba(0, 198, 255, 0.6)"; winner_logo = team_logos.get(a_team, "")
            else: pred_text = "BERABERLİK"; clr = "#fce803"; glow_clr = "rgba(252, 232, 3, 0.6)"; winner_logo = "https://resources.premierleague.com/premierleague/pl_icon.png"

            html_content = f"""
            <div class="winner-card" style="border-color: {clr}; box-shadow: 0 0 50px {glow_clr};">
                <h3 style="color:#aaa; letter-spacing:4px; margin:0; font-size: 1rem;">YAPAY ZEKA TAHMİNİ (Mamdani)</h3>
                <img src="{winner_logo}" style="width: 250px; height: 250px; object-fit: contain; margin: 30px auto; display:block; filter: drop-shadow(0 0 30px {glow_clr}); animation: float 4s infinite;">
                <div class="result-text" style="color:{clr}; text-shadow: 0 0 20px {glow_clr};">{pred_text}</div>
                <div style="margin-top:20px; color:#ccc; font-family:'Rajdhani'; font-size: 1.2rem;">Güven Skoru: <b>{min(abs(diff), 9.9):.2f} / 10</b></div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if res_chaos > 6.5: st.error(f"🔥 YÜKSEK TANSİYON! Kaos Skoru: {res_chaos:.2f}/10. Kırmızı kart ihtimali yüksek.")
            else: st.success(f"🟢 Temiz Maç Beklentisi. Kaos Skoru: {res_chaos:.2f}/10")

        with t2:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='stat-card'><div class='stat-label'>LİG SIRASI</div><div class='stat-value'>{h_stats['raw']['rank']} - {a_stats['raw']['rank']}</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-label'>GOL (A/Y)</div><div class='stat-value'>{h_stats['raw']['scored']}/{h_stats['raw']['conceded']} - {a_stats['raw']['scored']}/{a_stats['raw']['conceded']}</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-label'>FORM PUANI</div><div class='stat-value'>{h_stats['raw']['form_points']} - {a_stats['raw']['form_points']}</div></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='stat-card'><div class='stat-label'>EKSİK OYUNCU</div><div class='stat-value' style='color:#ff4444'>{h_stats['raw']['missing']} - {a_stats['raw']['missing']}</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            hc, ac = st.columns(2)
            with hc:
                st.subheader(f"{h_team} Son Maçlar")
                if h_stats['raw']['missing_names']: st.warning(f"🚨 **Eksikler:** {', '.join(h_stats['raw']['missing_names'])}")
                else: st.success("✅ Tam Kadro")
                display_match_history(df, h_team)
            with ac:
                st.subheader(f"{a_team} Son Maçlar")
                if a_stats['raw']['missing_names']: st.warning(f"🚨 **Eksikler:** {', '.join(a_stats['raw']['missing_names'])}")
                else: st.success("✅ Tam Kadro")
                display_match_history(df, a_team)

        with t3:
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:20px;">
                <span style="color:#00f260; font-size:1.5rem; font-weight:bold; margin-right:20px;">🏠 {h_team}</span>
                <span style="color:#666; font-size:1.2rem;">VS</span>
                <span style="color:#00c6ff; font-size:1.5rem; font-weight:bold; margin-left:20px;">✈️ {a_team}</span>
            </div>
            """, unsafe_allow_html=True)

            # --- 1. ADIM: EV SAHİBİ GRAFİKLERİNİ OLUŞTUR ---
            match_sim.input['form'] = h_stats['fuzzy']['form']
            match_sim.input['rank'] = h_stats['fuzzy']['rank']
            match_sim.input['goals'] = h_stats['fuzzy']['goals']
            match_sim.compute()
            
            # Grafikleri çiz ve değişkene ata (Ekrana basma)
            fig_h_form = plot_fuzzy_chart(form, match_sim, f"FORM: {h_team} ({h_stats['fuzzy']['form']})", "#00f260")
            fig_h_rank = plot_fuzzy_chart(rank, match_sim, f"SIRALAMA: {h_team} ({h_stats['fuzzy']['rank']})", "#00f260")
            fig_h_goals = plot_fuzzy_chart(goals, match_sim, f"GOL GÜCÜ: {h_team} ({h_stats['fuzzy']['goals']})", "#00f260")
            fig_h_res = plot_fuzzy_chart(result, match_sim, f"SONUÇ: {h_team} Şansı", "#ffffff")

            # --- 2. ADIM: DEPLASMAN GRAFİKLERİNİ OLUŞTUR ---
            match_sim.input['form'] = a_stats['fuzzy']['form']
            match_sim.input['rank'] = a_stats['fuzzy']['rank']
            match_sim.input['goals'] = a_stats['fuzzy']['goals']
            match_sim.compute()
            
            # Grafikleri çiz ve değişkene ata
            fig_a_form = plot_fuzzy_chart(form, match_sim, f"FORM: {a_team} ({a_stats['fuzzy']['form']})", "#00c6ff")
            fig_a_rank = plot_fuzzy_chart(rank, match_sim, f"SIRALAMA: {a_team} ({a_stats['fuzzy']['rank']})", "#00c6ff")
            fig_a_goals = plot_fuzzy_chart(goals, match_sim, f"GOL GÜCÜ: {a_team} ({a_stats['fuzzy']['goals']})", "#00c6ff")
            fig_a_res = plot_fuzzy_chart(result, match_sim, f"SONUÇ: {a_team} Şansı", "#ffffff")

            # --- 3. ADIM: YAN YANA GÖSTERİM (LAYOUT) ---
            
            # Başlıklar
            c1, c2 = st.columns(2)
            c1.markdown("<h4 style='text-align:center; color:#00f260'>EV SAHİBİ GİRDİLERİ</h4>", unsafe_allow_html=True)
            c2.markdown("<h4 style='text-align:center; color:#00c6ff'>DEPLASMAN GİRDİLERİ</h4>", unsafe_allow_html=True)

            # Grafik 1: Form
            col1, col2 = st.columns(2)
            with col1: st.pyplot(fig_h_form)
            with col2: st.pyplot(fig_a_form)
            
            # Grafik 2: Sıralama
            col3, col4 = st.columns(2)
            with col3: st.pyplot(fig_h_rank)
            with col4: st.pyplot(fig_a_rank)
            
            # Grafik 3: Goller
            col5, col6 = st.columns(2)
            with col5: st.pyplot(fig_h_goals)
            with col6: st.pyplot(fig_a_goals)

            st.markdown("---")
            
            # Sonuçlar ve Kaos
            st.markdown("<h4 style='text-align:center;'>🏆 SONUÇ VE ATMOSFER</h4>", unsafe_allow_html=True)
            r1, r2, r3 = st.columns([1, 1, 1])
            with r1: 
                st.markdown(f"<div style='text-align:center'>🏠 {h_team} Galibiyet İhtimali</div>", unsafe_allow_html=True)
                st.pyplot(fig_h_res)
            with r2:
                st.markdown("<div style='text-align:center'>🔥 KAOS / KART RİSKİ (ORTAK)</div>", unsafe_allow_html=True)
                st.pyplot(plot_fuzzy_chart(chaos, card_sim, f"Atmosfer: {res_chaos:.2f}", "#ff0055"))
            with r3:
                st.markdown(f"<div style='text-align:center'>✈️ {a_team} Galibiyet İhtimali</div>", unsafe_allow_html=True)
                st.pyplot(fig_a_res)