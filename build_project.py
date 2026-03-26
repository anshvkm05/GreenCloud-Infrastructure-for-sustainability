import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json

print("Generating synthetic Cluster-Level dataset...")
np.random.seed(42)
hours = 720 # 30 days of hourly data

timestamps = pd.date_range(start='2026-03-01', periods=hours, freq='H')
data = []

total_servers = 1000
safe_capacity_limit = 0.75 # We want active servers to be at most 75% utilized

for t in timestamps:
    hour = t.hour
    day_of_week = t.dayofweek
    
    # Base load logic: higher during day (8-18), lower at night. Drops on weekends (days 5, 6)
    is_weekend = 1 if day_of_week >= 5 else 0
    weekend_multiplier = 0.6 if is_weekend else 1.0
    
    # Diurnal CPU cycle (peak around 14:00)
    base_cpu = 40 + 30 * np.sin(np.pi * (hour - 8) / 12)
    base_cpu = max(10, base_cpu) * weekend_multiplier
    
    # Add noise
    avg_cpu_load = max(5, min(95, np.random.normal(base_cpu, 5)))
    avg_memory_load = max(10, min(90, avg_cpu_load * 0.8 + np.random.normal(0, 5)))
    network_traffic_gbps = max(1, avg_cpu_load * 0.5 + np.random.normal(0, 2))
    
    # Target Logic: How many servers can we shutdown?
    if avg_cpu_load >= safe_capacity_limit * 100:
        safe_shutdown_count = 0
    else:
        # Calculate max servers we can afford to lose
        required_servers = (total_servers * (avg_cpu_load / 100.0)) / safe_capacity_limit
        safe_shutdown_count = max(0, total_servers - int(required_servers))
        
        # Add a small buffer so we aren't perfectly predictable (adds realism to the ML task)
        safe_shutdown_count = max(0, safe_shutdown_count - np.random.randint(0, 20))

    data.append([t, hour, day_of_week, avg_cpu_load, avg_memory_load, network_traffic_gbps, safe_shutdown_count])

df = pd.DataFrame(data, columns=['timestamp', 'hour_of_day', 'day_of_week', 'avg_cpu_load', 'avg_memory_load', 'network_traffic_gbps', 'safe_shutdown_count'])
df.to_csv("cluster_telemetry.csv", index=False)
print(f"Dataset generated with {len(df)} records.")

print("Training Random Forest Regressor Model...")
features = ['hour_of_day', 'day_of_week', 'avg_cpu_load', 'avg_memory_load', 'network_traffic_gbps']
X = df[features]
y = df['safe_shutdown_count']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)
print(f"MAE: {mae:.2f} servers")
print(f"R2 Score: {r2:.4f}")

joblib.dump(model, "rf_cluster_model.pkl")
print("Model saved to rf_cluster_model.pkl")

print("Generating model_development.ipynb...")
notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Eco-Scale: Prediction of Safe Server Shutdowns\\n",
    "## Time-Series & Cluster-Level Regression\\n",
    "\\n",
    "Instead of predicting binary load on a single server, this notebook predicts the **exact number of servers** out of a 1000-node cluster that can be safely powered down while keeping overall capacity at a safe 75% limit."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "import plotly.express as px\\n",
    "from sklearn.model_selection import train_test_split\\n",
    "from sklearn.ensemble import RandomForestRegressor\\n",
    "from sklearn.metrics import mean_absolute_error, r2_score\\n",
    "import joblib"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 1. Data Loading"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv('cluster_telemetry.csv')\\n",
    "df['timestamp'] = pd.to_datetime(df['timestamp'])\\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2. Exploratory Data Analysis (EDA) & Feature Relationships"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Time-Series View of Cluster Load\\n",
    "fig = px.line(df[:168], x='timestamp', y=['avg_cpu_load', 'safe_shutdown_count'], \\n",
    "              title='1-Week Snapshot: Inverse Relationship between CPU Load & Servers to Shutdown')\\n",
    "fig.show()\\n",
    "\\n",
    "# Correlation Heatmap\\n",
    "corr = df.drop('timestamp', axis=1).corr()\\n",
    "fig2 = px.imshow(corr, text_auto=True, aspect=\\\"auto\\\", title=\\\"Feature Correlation Heatmap\\\")\\n",
    "fig2.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3. Model Training (Random Forest Regressor)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "features = ['hour_of_day', 'day_of_week', 'avg_cpu_load', 'avg_memory_load', 'network_traffic_gbps']\\n",
    "X = df[features]\\n",
    "y = df['safe_shutdown_count']\\n",
    "\\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\\n",
    "\\n",
    "model = RandomForestRegressor(n_estimators=100, random_state=42)\\n",
    "model.fit(X_train, y_train)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4. Evaluation & Feature Importance"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "preds = model.predict(X_test)\\n",
    "print(f\\\"Mean Absolute Error (MAE): {mean_absolute_error(y_test, preds):.2f} servers\\\")\\n",
    "print(f\\\"R^2 Score: {r2_score(y_test, preds):.4f}\\\")\\n",
    "\\n",
    "importances = pd.DataFrame({\\n",
    "    'Feature': features,\\n",
    "    'Importance': model.feature_importances_\\n",
    "}).sort_values(by='Importance', ascending=False)\\n",
    "\\n",
    "fig3 = px.bar(importances, x='Importance', y='Feature', orientation='h', title='Feature Importance in Random Forest Model')\\n",
    "fig3.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5. Model Saving"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "joblib.dump(model, 'rf_cluster_model_notebook.pkl')\\n",
    "print(\\\"Model saved successfully.\\\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("model_development.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("Finished!")
