import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# MAMDANI ÇIKARIM MEKANİZMASI (3 INPUT -> 1 OUTPUT)
# =============================================================================

# --- GİRDİLER (INPUTS) ---
# 0-10 Puan arası normalize edilmiş veriler

# Grafik 1: Form Durumu (Son 5 Maç)
form = ctrl.Antecedent(np.arange(0, 11, 1), 'form')
form['kotu'] = fuzz.trimf(form.universe, [0, 0, 4])
form['orta'] = fuzz.trimf(form.universe, [3, 5, 7])
form['iyi']  = fuzz.trimf(form.universe, [6, 10, 10])

# Grafik 2: Lig Sıralaması
rank = ctrl.Antecedent(np.arange(0, 11, 1), 'rank')
rank['dusuk']  = fuzz.trimf(rank.universe, [0, 0, 4])   # Alt sıralar
rank['orta']   = fuzz.trimf(rank.universe, [3, 5, 7])   # Orta sıralar
rank['yuksek'] = fuzz.trimf(rank.universe, [6, 10, 10]) # Zirve takımları

# Grafik 3: Gol Ortalaması
goals = ctrl.Antecedent(np.arange(0, 11, 1), 'goals')
goals['kisir']  = fuzz.trimf(goals.universe, [0, 0, 4])   # Az gol atıyor
goals['normal'] = fuzz.trimf(goals.universe, [3, 5, 7])   # Normal
goals['golcu']  = fuzz.trimf(goals.universe, [6, 10, 10]) # Çok gol atıyor

# --- ÇIKTI (OUTPUT) ---
result = ctrl.Consequent(np.arange(0, 11, 1), 'result')
result['maglubiyet'] = fuzz.trimf(result.universe, [0, 0, 4])
result['beraberlik'] = fuzz.trimf(result.universe, [3, 5, 7])
result['galibiyet']  = fuzz.trimf(result.universe, [6, 10, 10])

# --- KURAL TABANI (MAMDANI RULES) ---
# 3 Değişken olduğu için kombinasyonlar arttı. Mantıklı senaryoları yazıyoruz.

rules = [
    # --- GALİBİYET SENARYOLARI (GÜÇLÜ) ---
    # Form İyi VE Sıralama Yüksek VE Golcü -> KESİN GALİBİYET
    ctrl.Rule(form['iyi'] & rank['yuksek'] & goals['golcu'], result['galibiyet']),
    # Form İyi VE Sıralama Yüksek (Gol normal olsa bile) -> GALİBİYET
    ctrl.Rule(form['iyi'] & rank['yuksek'] & goals['normal'], result['galibiyet']),
    # Sıralama Yüksek VE Golcü (Form orta olsa bile) -> GALİBİYET
    ctrl.Rule(form['orta'] & rank['yuksek'] & goals['golcu'], result['galibiyet']),

    # --- BERABERLİK SENARYOLARI (DENGELİ) ---
    # Her şey ortaysa -> BERABERLİK
    ctrl.Rule(form['orta'] & rank['orta'] & goals['normal'], result['beraberlik']),
    # Form İyi ama Sıralama Düşük (Sürpriz takım) -> BERABERLİK
    ctrl.Rule(form['iyi'] & rank['dusuk'], result['beraberlik']),
    # Güçlü takım ama Form Kötü -> BERABERLİK
    ctrl.Rule(rank['yuksek'] & form['kotu'], result['beraberlik']),
    # Takım gol atamıyorsa (Kısır) -> BERABERLİK ihtimali artar
    ctrl.Rule(rank['orta'] & goals['kisir'], result['beraberlik']),

    # --- MAĞLUBİYET SENARYOLARI (ZAYIF) ---
    # Form Kötü VE Sıralama Düşük -> MAĞLUBİYET
    ctrl.Rule(form['kotu'] & rank['dusuk'], result['maglubiyet']),
    # Sıralama Düşük VE Gol Atamıyor -> MAĞLUBİYET
    ctrl.Rule(rank['dusuk'] & goals['kisir'], result['maglubiyet']),
    # Form Kötü VE Gol Kısır -> MAĞLUBİYET
    ctrl.Rule(form['kotu'] & goals['kisir'], result['maglubiyet']),
]

# Sistemi Kur
match_ctrl = ctrl.ControlSystem(rules)
match_sim = ctrl.ControlSystemSimulation(match_ctrl)

# --- EKSTRA: KART VE KAOS SİSTEMİ (OPSİYONEL OLARAK KALDI) ---
aggression = ctrl.Antecedent(np.arange(0, 11, 1), 'aggression')
tension = ctrl.Antecedent(np.arange(0, 11, 1), 'tension')
chaos = ctrl.Consequent(np.arange(0, 11, 1), 'chaos')

aggression['sakin'] = fuzz.trimf(aggression.universe, [0, 0, 4])
aggression['sert']  = fuzz.trimf(aggression.universe, [3, 5, 7])
aggression['vahsi'] = fuzz.trimf(aggression.universe, [6, 10, 10])

tension['dostluk'] = fuzz.trimf(tension.universe, [0, 0, 4])
tension['rekabet'] = fuzz.trimf(tension.universe, [3, 5, 7])
tension['final']   = fuzz.trimf(tension.universe, [6, 10, 10])

chaos['temiz'] = fuzz.trimf(chaos.universe, [0, 0, 4])
chaos['normal']= fuzz.trimf(chaos.universe, [3, 5, 7])
chaos['kirmizi']= fuzz.trimf(chaos.universe, [6, 10, 10])

card_rules = [
    ctrl.Rule(aggression['vahsi'] & tension['final'], chaos['kirmizi']),
    ctrl.Rule(aggression['vahsi'] & tension['rekabet'], chaos['kirmizi']),
    ctrl.Rule(aggression['sert'] & tension['final'], chaos['kirmizi']),
    ctrl.Rule(aggression['sert'] & tension['rekabet'], chaos['normal']),
    ctrl.Rule(aggression['sakin'] & tension['final'], chaos['normal']),
    ctrl.Rule(aggression['sakin'] & tension['dostluk'], chaos['temiz']),
    ctrl.Rule(aggression['sert'] & tension['dostluk'], chaos['normal']),
]

card_ctrl = ctrl.ControlSystem(card_rules)
card_sim = ctrl.ControlSystemSimulation(card_ctrl)