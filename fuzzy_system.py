import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# SİSTEM 1: MAÇ SONUCU TAHMİNİ (MAMDANI - 3 GİRDİ)
# =============================================================================

# --- GİRDİLER (INPUTS) ---
# Form (0-10)
form = ctrl.Antecedent(np.arange(0, 11, 1), 'form')
form['kotu'] = fuzz.trimf(form.universe, [0, 0, 4])
form['orta'] = fuzz.trimf(form.universe, [3, 5, 7])
form['iyi']  = fuzz.trimf(form.universe, [6, 10, 10])

# Sıralama (0-10)
rank = ctrl.Antecedent(np.arange(0, 11, 1), 'rank')
rank['dusuk']  = fuzz.trimf(rank.universe, [0, 0, 4])
rank['orta']   = fuzz.trimf(rank.universe, [3, 5, 7])
rank['yuksek'] = fuzz.trimf(rank.universe, [6, 10, 10])

# Gol Ortalaması (0-10)
goals = ctrl.Antecedent(np.arange(0, 11, 1), 'goals')
goals['kisir']  = fuzz.trimf(goals.universe, [0, 0, 4])
goals['normal'] = fuzz.trimf(goals.universe, [3, 5, 7])
goals['golcu']  = fuzz.trimf(goals.universe, [6, 10, 10])

# --- ÇIKTI (OUTPUT) ---
result = ctrl.Consequent(np.arange(0, 11, 1), 'result')
result['maglubiyet'] = fuzz.trimf(result.universe, [0, 0, 4])
result['beraberlik'] = fuzz.trimf(result.universe, [3, 5, 7])
result['galibiyet']  = fuzz.trimf(result.universe, [6, 10, 10])

# --- KURALLAR (MATCH RULES) ---
match_rules = [
    # Galibiyet Senaryoları
    ctrl.Rule(form['iyi'] & rank['yuksek'] & goals['golcu'], result['galibiyet']),
    ctrl.Rule(form['iyi'] & rank['yuksek'] & goals['normal'], result['galibiyet']),
    ctrl.Rule(form['orta'] & rank['yuksek'] & goals['golcu'], result['galibiyet']),
    
    # Beraberlik Senaryoları
    ctrl.Rule(form['orta'] & rank['orta'] & goals['normal'], result['beraberlik']),
    ctrl.Rule(form['iyi'] & rank['dusuk'], result['beraberlik']), # Sürpriz
    ctrl.Rule(rank['yuksek'] & form['kotu'], result['beraberlik']), # Favori formsuzsa
    ctrl.Rule(goals['kisir'], result['beraberlik']), # Kimse atamıyorsa
    
    # Mağlubiyet Senaryoları
    ctrl.Rule(form['kotu'] & rank['dusuk'], result['maglubiyet']),
    ctrl.Rule(rank['dusuk'] & goals['kisir'], result['maglubiyet']),
    ctrl.Rule(form['kotu'] & goals['kisir'], result['maglubiyet']),
]

match_ctrl = ctrl.ControlSystem(match_rules)
match_sim = ctrl.ControlSystemSimulation(match_ctrl)


# =============================================================================
# SİSTEM 2: KART VE KAOS (Eksik Kurallar Tamamlandı)
# =============================================================================

aggression = ctrl.Antecedent(np.arange(0, 11, 1), 'aggression')
tension = ctrl.Antecedent(np.arange(0, 11, 1), 'tension')
chaos = ctrl.Consequent(np.arange(0, 11, 1), 'chaos')

# Üyelik Fonksiyonları
aggression['sakin'] = fuzz.trimf(aggression.universe, [0, 0, 4])
aggression['sert']  = fuzz.trimf(aggression.universe, [3, 5, 7])
aggression['vahsi'] = fuzz.trimf(aggression.universe, [6, 10, 10])

tension['dostluk'] = fuzz.trimf(tension.universe, [0, 0, 4])
tension['rekabet'] = fuzz.trimf(tension.universe, [3, 5, 7])
tension['final']   = fuzz.trimf(tension.universe, [6, 10, 10])

chaos['temiz'] = fuzz.trimf(chaos.universe, [0, 0, 4])
chaos['normal']= fuzz.trimf(chaos.universe, [3, 5, 7])
chaos['kirmizi']= fuzz.trimf(chaos.universe, [6, 10, 10])

# --- GÜNCELLENMİŞ KURALLAR (HATA ÇIKARMAMASI İÇİN) ---
card_rules = [
    # Yüksek Kaos
    ctrl.Rule(aggression['vahsi'] & tension['final'], chaos['kirmizi']),
    ctrl.Rule(aggression['vahsi'] & tension['rekabet'], chaos['kirmizi']),
    ctrl.Rule(aggression['sert'] & tension['final'], chaos['kirmizi']),
    
    # Normal Kaos
    ctrl.Rule(aggression['sert'] & tension['rekabet'], chaos['normal']),
    ctrl.Rule(aggression['sakin'] & tension['final'], chaos['normal']),
    ctrl.Rule(aggression['vahsi'] & tension['dostluk'], chaos['normal']),
    ctrl.Rule(aggression['sert'] & tension['dostluk'], chaos['normal']),
    
    # Temiz Maç (BURASI EKSİKTİ, EKLENDİ)
    ctrl.Rule(aggression['sakin'] & tension['dostluk'], chaos['temiz']),
    ctrl.Rule(aggression['sakin'] & tension['rekabet'], chaos['temiz']), # Bu kural eksikti!
]

card_ctrl = ctrl.ControlSystem(card_rules)
card_sim = ctrl.ControlSystemSimulation(card_ctrl)