# 🍃 Eco-Scale: Predictive Energy Optimization for Cloud Infrastructure

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Random_Forest-green.svg)]()

**Eco-Scale** is a proactive, AI-driven infrastructure management solution designed to drastically reduce the carbon footprint of massive data centers. Built for international environmental hackathons, this project solves the "Always-On" problem of cloud computing.

## 🧠 The Problem
Data centers waste massive amounts of electricity because they rely on static provisioning. To prevent crashes, servers run near full capacity 24/7. During off-peak hours, these machines sit idle but continue to draw significant baseline power, heavily contributing to the tech industry's carbon emissions.

## 🚀 The Solution
Instead of reactively scaling *after* a load spike, Eco-Scale uses predictive machine learning (Random Forest Regression) to forecast precise CPU/Memory requirements hours in advance. By identifying exactly how many servers can be safely shut down during low-load periods, the system proactively consolidates tasks, drastically reducing energy waste without sacrificing performance.

---

## 🏗️ Architecture

1. **The Data Engine:** Synthesized based on the highly granular **Alibaba Cluster Trace Program**. It generates 30 days of hourly telemetry for a scalable server cluster, mapping diurnal patterns and network traffic.
2. **The ML Model (`rf_cluster_model.pkl`):** A Random Forest Regressor trained to predict the *exact subset* of servers that can be safely powered down while maintaining a strict 75% capacity threshold for the remaining active fleet.
3. **The API Layer (`api.py`):** A robust FastAPI backend allowing third-party orchestrators (like Kubernetes) to query the model programmatically and receive JSON actions.
4. **The UI Dashboard (`app.py`):** An aesthetically stunning, interactive Streamlit front-end. It features live telemetry charts, dynamic cluster-size scaling, and an interactive "AI Action Center" for real-time inference.

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/anshvkm05/GreenCloud-Infrastructure-for-sustainability.git
cd GreenCloud-Infrastructure-for-sustainability
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate the Dataset and Train the Model
This will synthesize the 30-day cluster telemetry and train the Random Forest Regressor.
```bash
python build_project.py
```

---

## 🖥️ Running the Project

### Option A: The Streamlit Interactive Dashboard (For Pitching/UI Demo)
Launch the beautiful user interface to explore charts and make live predictions.
```bash
streamlit run app.py
```

### Option B: The FastAPI Backend (For Architecture/API Demo)
Launch the standalone backend API service.
```bash
uvicorn api:app --reload
```
Once running, navigate to `http://127.0.0.1:8000/docs` in your browser to access the interactive Swagger UI and test the `/predict/cluster` endpoint directly. You can also run the automated test script:
```bash
python test_api.py
```

---

## 🌟 Unique Pitch Features
- **Interactive Extrapolation:** In the Streamlit app, users can dynamically drag the slider to change the entire physical size of the cluster (e.g., from 100 to 10,000 servers). The model's predictions, carbon offsets, and UI charts automatically scale algebraically without needing to retrain the ML model.
- **ROI & Carbon Tracking:** Real-time metrics calculate exactly how much money and Tons of CO2 are being saved strictly based on the model's current active consolidation recommendations.

---
*Developed for Global Tech & Sustainability Competitions.*
