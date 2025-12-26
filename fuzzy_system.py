import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# MAMDANI ÇIKARIM MEKANİZMASI (RESİMDEKİ MANTIK)
# =============================================================================
# Fotoğraftaki gibi girişleri üçgen (trimf) ve yamuk (trapmf) fonksiyonlarla tanımlıyoruz.

# --- GİRDİLER (INPUTS) ---
# Evrensel Küme: 0 ile 10 arası puanlama

# 1. GİRDİ: FORM DURUMU (Fotoğraftaki Mu_A gibi)
# Kötü: Sol tarafı yüksek yamuk (0'dan başlar, 3'e kadar yüksek, 5'te biter)
# Orta: Tam bir üçgen (3'te başlar, 5'te zirve, 7'de biter)
# İyi: Sağ tarafı yüksek yamuk (5'te başlar, 7'den sonra hep yüksek)
form = ctrl.Antecedent(np.arange(0, 11, 1), 'form')
form['kotu'] = fuzz.trapmf(form.universe, [0, 0, 3, 5])
form['orta'] = fuzz.trimf(form.universe, [3, 5, 7])
form['iyi']  = fuzz.trapmf(form.universe, [5, 7, 10, 10])

# 2. GİRDİ: LİG SIRALAMASI (Fotoğraftaki Mu_B gibi)
rank = ctrl.Antecedent(np.arange(0, 11, 1), 'rank')
rank['dusuk']  = fuzz.trapmf(rank.universe, [0, 0, 3, 5])
rank['orta']   = fuzz.trimf(rank.universe, [3, 5, 7])
rank['yuksek'] = fuzz.trapmf(rank.universe, [5, 7, 10, 10])

# 3. GİRDİ: GOL GÜCÜ (Fotoğraftaki Mu_C gibi)
goals = ctrl.Antecedent(np.arange(0, 11, 1), 'goals')
goals['kisir']  = fuzz.trapmf(goals.universe, [0, 0, 3, 5])
goals['normal'] = fuzz.trimf(goals.universe, [3, 5, 7])
goals['golcu']  = fuzz.trapmf(goals.universe, [5, 7, 10, 10])

# --- ÇIKTI (OUTPUT) ---
# SONUÇ: MAÇI KAZANMA İHTİMALİ (Defuzzification: Centroid/Ağırlık Merkezi)
# Fotoğraftaki sol grafik gibi sonuç kümeleri
result = ctrl.Consequent(np.arange(0, 11, 1), 'result')
result['maglubiyet'] = fuzz.trimf(result.universe, [0, 0, 4])   # Sol Üçgen
result['beraberlik'] = fuzz.trimf(result.universe, [3, 5, 7])   # Orta Üçgen
result['galibiyet']  = fuzz.trimf(result.universe, [6, 10, 10]) # Sağ Üçgen

# =============================================================================
# KURAL TABANI (RULE BASE)
# =============================================================================
# Fotoğraftaki "0.34 H, 0.34 T -> 0.34 GA" mantığı burada MIN operatörüyle işlenir.
# Sistem otomatik olarak en düşük üyelik derecesini (Min) alır ve sonucu keser (Clipping).

rules = [
    # --- KESİN GALİBİYET KURALLARI ---
    # Form İYİ ve Sıralama YÜKSEK ise -> KESİN GALİBİYET
    ctrl.Rule(form['iyi'] & rank['yuksek'], result['galibiyet']),
    # Golcü takım ve Form İYİ ise -> GALİBİYET
    ctrl.Rule(goals['golcu'] & form['iyi'], result['galibiyet']),
    
    # --- BERABERLİK KURALLARI ---
    # Takımlar denk ise (Orta Form, Orta Sıra) -> BERABERLİK
    ctrl.Rule(form['orta'] & rank['orta'], result['beraberlik']),
    # Güçlü takım formsuz ise (Sıra Yüksek ama Form Kötü) -> BERABERLİK
    ctrl.Rule(rank['yuksek'] & form['kotu'], result['beraberlik']),
    # İki takım da kısır (gol atamıyor) ise -> BERABERLİK
    ctrl.Rule(goals['kisir'] & rank['orta'], result['beraberlik']),

    # --- MAĞLUBİYET KURALLARI ---
    # Form KÖTÜ ve Sıralama DÜŞÜK ise -> MAĞLUBİYET
    ctrl.Rule(form['kotu'] & rank['dusuk'], result['maglubiyet']),
    # Takım gol atamıyor (Kısır) ve Form KÖTÜ ise -> MAĞLUBİYET
    ctrl.Rule(goals['kisir'] & form['kotu'], result['maglubiyet']),
    
    # --- KARMAŞIK DURUMLAR (FOTOĞRAFTAKİ GİBİ ÇOKLU GİRDİ) ---
    # Form Orta, Sıralama Yüksek, Gol Normal -> Galibiyete Yakın
    ctrl.Rule(form['orta'] & rank['yuksek'] & goals['normal'], result['galibiyet']),
    # Form İyi, Sıralama Düşük, Gol Kısır -> Beraberlik (Sürpriz Takım)
    ctrl.Rule(form['iyi'] & rank['dusuk'] & goals['kisir'], result['beraberlik']),
]

# Sistemi Oluştur
match_ctrl = ctrl.ControlSystem(rules)
match_sim = ctrl.ControlSystemSimulation(match_ctrl)


# =============================================================================
# EKSTRA: KAOS VE KART SİSTEMİ (ATMOSFER)
# =============================================================================
# Bu kısım maçın gerginliğini ölçer, ana skoru etkilemez ama kullanıcıya bilgi verir.

aggression = ctrl.Antecedent(np.arange(0, 11, 1), 'aggression')
tension = ctrl.Antecedent(np.arange(0, 11, 1), 'tension')
chaos = ctrl.Consequent(np.arange(0, 11, 1), 'chaos')

aggression['sakin'] = fuzz.trapmf(aggression.universe, [0, 0, 3, 5])
aggression['sert']  = fuzz.trimf(aggression.universe, [3, 5, 7])
aggression['vahsi'] = fuzz.trapmf(aggression.universe, [5, 7, 10, 10])

tension['dostluk'] = fuzz.trapmf(tension.universe, [0, 0, 3, 5])
tension['rekabet'] = fuzz.trimf(tension.universe, [3, 5, 7])
tension['final']   = fuzz.trapmf(tension.universe, [5, 7, 10, 10])

chaos['temiz'] = fuzz.trimf(chaos.universe, [0, 0, 4])
chaos['normal']= fuzz.trimf(chaos.universe, [3, 5, 7])
chaos['kirmizi']= fuzz.trimf(chaos.universe, [6, 10, 10])

card_rules = [
    ctrl.Rule(aggression['vahsi'] | tension['final'], chaos['kirmizi']),
    ctrl.Rule(aggression['sert'] & tension['rekabet'], chaos['normal']),
    ctrl.Rule(aggression['sakin'] & tension['dostluk'], chaos['temiz']),
    ctrl.Rule(aggression['sakin'] & tension['rekabet'], chaos['temiz']),
    ctrl.Rule(aggression['sert'] & tension['dostluk'], chaos['normal']),
    ctrl.Rule(aggression['vahsi'] & tension['dostluk'], chaos['normal']),
]

card_ctrl = ctrl.ControlSystem(card_rules)
card_sim = ctrl.ControlSystemSimulation(card_ctrl)