# ⚽ FUZZYBED: AI Powered Match Predictor

**FUZZYBED** is a futuristic football analytics engine that predicts Premier League match outcomes using **Fuzzy Logic (Mamdani Inference System)**. Unlike traditional statistical models that rely solely on hard numbers, this project mimics human reasoning to evaluate team performance, risk factors, and match atmosphere.

🔗 **[Live Demo](https://fuzzyball-predictor.streamlit.app)**

---

## 🚀 Features

* **Real-Time Data:** Fetches live data (fixtures, results, player stats) from the official **Fantasy Premier League (FPL) API**.
* **Fuzzy Logic Engine:** Uses a custom-built Mamdani Inference System to calculate winning probabilities.
* **Dual-Analysis:** Compares "Home" and "Away" performance side-by-side using dynamic charts.
* **Chaos Theory:** A secondary engine predicts the "Match Tension" and probability of red/yellow cards.
* **Futuristic UI:** Built with Streamlit, featuring a neon-themed interface and 3D team logo carousel.

---

## 🧠 How It Works (The Logic)

This project does not use simple averages. It uses **Scikit-Fuzzy** to fuzzify crisp inputs into linguistic variables (e.g., "Strong", "Weak", "Critical").

### 1. The Inputs (Fuzzification)

The system analyzes 3 key metrics for each team:

* **📈 Form:** Based on points collected in the last 5 matches.
* **🏆 League Rank:** The team's current standing in the Premier League table.
* **⚽ Goal Power:** Average goals scored in recent games.

### 2. The Rule Base (Inference)

We defined a **3x3 Rule Matrix** based on football expertise.

* *Example Rule:* `IF (Form is Good) AND (Rank is High) AND (Attack is Strong) THEN (Result is Win)`
* *Example Rule:* `IF (Rank is High) BUT (Form is Bad) THEN (Result is Draw)`

### 3. The Output (Defuzzification)

The system aggregates these rules to produce a single **"Win Score" (0-10)** for both the Home and Away teams. It also accounts for the **Home Field Advantage** factor.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Web Framework:** Streamlit
* **AI/Logic:** Scikit-Fuzzy (Fuzzy Logic Algorithms)
* **Data Processing:** Pandas, NumPy
* **Visualization:** Matplotlib
* **API:** Requests (FPL API)

---

## 📦 Installation

To run this project locally:

1. **Clone the repository**
```bash
git clone [https://github.com/devlightening/FuzzyBall.git](https://github.com/devlightening/FuzzyBall.git)
cd FuzzyBall