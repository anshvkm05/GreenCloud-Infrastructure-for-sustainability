# 🍃 Eco-Scale - Predictive Energy Optimization for Cloud Infrastructure

A full-stack machine learning solution to digitize and automate server consolidation in massive data centers. Built with **Python + FastAPI + Streamlit + Scikit-Learn**.
<img width="1919" height="957" alt="Screenshot 2026-03-27 141114" src="https://github.com/user-attachments/assets/b81f8eaf-3144-46d5-af70-93db1a4fa891" />
<img width="1917" height="956" alt="Screenshot 2026-03-27 141124" src="https://github.com/user-attachments/assets/47caee40-7e04-4395-8baf-6a0a4650999d" />
<img width="1919" height="955" alt="Screenshot 2026-03-27 141148" src="https://github.com/user-attachments/assets/7320d621-16e2-46be-8135-c5b3e29eff1d" />

---


## 🎯 Features

### Machine Learning Engine
- **Time-Series Forecasting** — Analyzes diurnal cycles, weekends, and hourly load drops.
- **Cluster-Level Prediction** — Predicts exactly how many servers out of a 1000-node cluster can be safely shut down.
- **Extensive EDA** — Integrated Jupyter notebook (`model_development.ipynb`) with Plotly correlation heatmaps and feature importance graphs.
- **Synthesized Telemetry** — Generates hyper-realistic Alibaba Cluster Trace data predicting CPU, Memory, and Network I/O.

### Streamlit Dashboard (Frontend)
- **Interactive UI** — "Eco-Dark" theme designed specifically to impress hackathon judges.
- **Dynamic Scale Extrapolation** — Slide to simulate cluster sizes from 100 to 10,000 servers; model safely extrapolates predictions instantly.
- **Real-Time ROI Calculator** — Instantly calculates monetary savings ($/month) and carbon offsets (Tons of CO2/month) based on live AI predictions.
- **AI Action Center** — A physical slider interface allowing users to query the Random Forest model interactively.

### FastAPI Backend (API Layer) for Third party use
- **High-Performance Serving** — Powered by Uvicorn and FastAPI.
- **Pydantic Validation** — Strict type-checking and logical bounds checking (e.g., CPU cannot exceed 100%) preventing bad telemetry from crashing the ML model.
- **Interactive Swagger Docs** — Auto-generated OpenAPI documentation for instant testing and third-party integration.

---

## 🛠 Tech Stack

| Layer     | Technology                                |
|-----------|-------------------------------------------|
| Frontend  | Streamlit, Plotly (Dynamic Charting)      |
| Backend   | FastAPI, Uvicorn, Python 3.9+             |
| ML Engine | Scikit-Learn (Random Forest Regression)   |
| Data      | Pandas, NumPy                             |

---

## 📂 Project Structure

```text
eco-scale/
├── app.py                       # Streamlit UI Dashboard
├── api.py                       # FastAPI Backend endpoints for third party to intergrate our API
├── build_project.py             # Data synthesis & ML Model training script
├── test_api.py                  # Automated Requests testing script
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
│
├── Data & Models/
│   ├── cluster_telemetry.csv    # 30-day synthesized server data (Generated)
│   └── rf_cluster_model.pkl     # Serialized Random Forest Model (Generated)
│
└── Notebooks/
    └── model_development.ipynb  # EDA, Data pipeline, and ML lifecycle (Generated)
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.9+** installed on your system.
- A modern web browser.

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/anshvkm05/GreenCloud-Infrastructure-for-sustainability.git
cd GreenCloud-Infrastructure-for-sustainability
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Generate the Dataset and Train the Model**
Run the core builder script. This will create the dataset, train the AI, and output the model.
```bash
python build_project.py
```

**4. Start the Application & Server**
You can run the the application from below two command:
- **Frontend + Backend (Single File):** `streamlit run app.py`
- **Backend (For Integrate the API in your Application):** `uvicorn api:app --reload`

---

## 🔗 Application URLs

| Interface           | URL                                        |
|---------------------|--------------------------------------------|
| Streamlit Dashboard | `http://localhost:8501/`                   |
| API Backend Data    | `http://127.0.0.1:8000/`                   |
| API Swagger UI Docs | `http://127.0.0.1:8000/docs`               |

---

## 📝 API Endpoints

### Public/Cluster
| Method | Endpoint               | Description                                              |
|--------|------------------------|----------------------------------------------------------|
| GET    | `/health`              | Checks if ML model is loaded and API is online.          |
| POST   | `/predict/cluster`     | Accepts telemetry payload and returns safe shutdown count|

---

## 👨‍💻 Author

Built for international environmental hacking and sustainability tech competitions.

---

## 📄 License

This project is for educational and demonstrative purposes within the hackathon framework.
