

# ⚽ NEO-FOOTBALL: AI Powered Match Predictor

**NEO-FOOTBALL** is a futuristic football analytics engine that predicts Premier League match outcomes using **Fuzzy Logic (Mamdani Inference System)**. Unlike traditional statistical models that rely solely on hard numbers, this project mimics human reasoning to evaluate team performance, risk factors, and match atmosphere.

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
git clone https://github.com/yourusername/fuzzy-football.git
cd fuzzy-football

```


2. **Install dependencies**
```bash
pip install -r requirements.txt

```


3. **Run the app**
```bash
streamlit run app.py

```



---

## 📷 Screenshots

### 1. Dashboard & Comparison

<img width="1906" height="763" alt="Predictor" src="https://github.com/user-attachments/assets/bf5beae5-bb69-4da0-8a35-014d1e6955bb" />

<img width="1817" height="667" alt="Result" src="https://github.com/user-attachments/assets/4d7f5720-ac87-44dd-8522-81e8dfca8aac" />


### 2. Fuzzy Logic Graphs (Mamdani System)

<img width="1872" height="792" alt="Statistics" src="https://github.com/user-attachments/assets/c8c209d2-75d2-44ff-9a28-17c55216b3f9" />
<img width="1908" height="812" alt="FuzzyGraphics" src="https://github.com/user-attachments/assets/aa3a1216-41a0-4995-b9df-ad95213187ce" />
<img width="1703" height="735" alt="FuzzyGraphics2" src="https://github.com/user-attachments/assets/9e63d158-2802-4c95-be1c-1c38075baf93" />



---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/devlightening/FuzzyBall/issues).
---

