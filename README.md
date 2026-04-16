# 🌊 Deep-Sea Pipeline Leak Simulation

A physics-based simulation of **pinhole leaks in deep-sea oil pipelines**, integrated with **advanced sensing (DAS + acoustic)** and a **hybrid self-healing system**.

This project models leak behavior, detection limitations, and autonomous repair mechanisms using engineering principles and scientific references.

---

## 🚀 Features

* 🛢️ **Pipeline flow modeling**

  * Darcy–Weisbach pressure drop
  * ISO 5167 orifice leak flow

* 📉 **Leak detection analysis**

  * Pressure & flow signal degradation
  * Sensor noise simulation

* 🎧 **Advanced sensing systems**

  * Distributed Acoustic Sensing (DAS)
  * Hydrophone acoustic detection (FFT analysis)

* 🧪 **Hybrid self-healing system**

  * Microcapsule-based rapid sealing
  * Vascular network long-term healing

* 📊 **Scientific visualizations (6 figures)**

  * Pressure profiles
  * Sensor signals
  * Healing dynamics
  * Performance comparison
  * Environmental sensitivity

---

## 📁 Project Structure

```id="struct002"
pipeline-leak-simulation/
│
├── src/
│   ├── __init__.py
│   └── pipeline_simulation.py
│
├── main.py                  # entry point
├── .outputs/                # generated figures (ignored)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash id="clone01"
git clone https://github.com/your-username/pipeline-leak-simulation.git
cd pipeline-leak-simulation
```

### 2. Create virtual environment

```bash id="venv01"
python -m venv venv
```

### 3. Activate environment

**Windows**

```bash id="win01"
venv\Scripts\activate
```

**Mac/Linux**

```bash id="mac01"
source venv/bin/activate
```

### 4. Install dependencies

```bash id="dep01"
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the full simulation:

```bash id="run01"
python main.py
```

This will:

* generate 6 figures
* save them to `.outputs/`
* display them interactively

---

## 📊 Output

Generated figures are saved in:

```id="out01"
.outputs/
```

This directory is ignored in Git and is recreated automatically during execution.

---

## 📚 References

Key models and data sources used:

1. White et al. (2001) — Autonomic healing of polymer composites
2. Toohey et al. (2007) — Microvascular self-healing materials
3. Juarez et al. (2005) — DAS pipeline monitoring
4. Wenz (1962) — Ocean acoustic noise
5. ISO 5167 — Orifice flow equations
6. Munson et al. — Fluid mechanics fundamentals
7. API MPMS — Crude oil properties
