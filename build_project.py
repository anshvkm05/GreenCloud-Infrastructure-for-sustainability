import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import json

print("Generating synthetic Alibaba trace dataset...")
# Generate Synthetic Data (100 servers, 192 hours = 8 days)
np.random.seed(42)
num_servers = 100
hours = 192

timestamps = pd.date_range(start='2026-03-26', periods=hours, freq='H')
data = []

for t_idx, t in enumerate(timestamps):
    # Simulated diurnal cycle: higher load during day, lower at night
    hour_of_day = t.hour
    base_load = 40 + 20 * np.sin(np.pi * (hour_of_day - 8) / 12)  # Peak around 14:00
    
    for machine_id in range(num_servers):
        # Add random noise and occasional spikes
        cpu_load = max(5, min(100, np.random.normal(base_load, 15)))
        mem_load = max(10, min(100, cpu_load * 0.8 + np.random.normal(0, 10)))
        
        # Target variable: Is it severely underutilized? (CPU < 20%)
        is_underutilized = 1 if cpu_load < 20 else 0
        
        data.append([t, f"server_{machine_id}", cpu_load, mem_load, is_underutilized])

df = pd.DataFrame(data, columns=['timestamp', 'machine_id', 'cpu_utilization', 'memory_utilization', 'is_underutilized'])
df.to_csv("server_telemetry.csv", index=False)
print(f"Dataset saved to server_telemetry.csv with {len(df)} records.")

print("Training Logistic Regression Model...")
features = ['cpu_utilization', 'memory_utilization']
X = df[features]
y = df['is_underutilized']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate (for notebook output)
preds = model.predict(X_test)
print(classification_report(y_test, preds))

joblib.dump(model, "logistic_model.pkl")
print("Model saved to logistic_model.pkl.")

print("Generating model_development.ipynb...")
notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Eco-Scale: Predictive Energy Optimization\\n",
    "## Alibaba Cluster Trace - Logistic Regression Model\\n",
    "\\n",
    "This notebook covers the end-to-end ML lifecycle for identifying underutilized servers."
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
    "import plotly.graph_objects as go\\n",
    "from sklearn.model_selection import train_test_split\\n",
    "from sklearn.linear_model import LogisticRegression\\n",
    "from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve\\n",
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
    "# Load the synthetic Alibaba cluster trace dataset\\n",
    "df = pd.read_csv('server_telemetry.csv')\\n",
    "df['timestamp'] = pd.to_datetime(df['timestamp'])\\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2. Exploratory Data Analysis (EDA)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Univariate Analysis\\n",
    "fig = px.histogram(df, x='cpu_utilization', nbins=50, title='CPU Utilization Distribution')\\n",
    "fig.show()\\n",
    "\\n",
    "# Bivariate Analysis\\n",
    "fig2 = px.scatter(df.sample(2000, random_state=42), x='cpu_utilization', y='memory_utilization', color='is_underutilized', \\n",
    "                 title='CPU vs Memory (Underutilization mapped)')\\n",
    "fig2.show()\\n",
    "\\n",
    "# Time-series pattern (Multivariate)\\n",
    "agg = df.groupby('timestamp').mean(numeric_only=True).reset_index()\\n",
    "fig3 = px.line(agg, x='timestamp', y='cpu_utilization', title='Average CPU Load Over 8 Days')\\n",
    "fig3.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3. Data Preprocessing & Model Selection"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "X = df[['cpu_utilization', 'memory_utilization']]\\n",
    "y = df['is_underutilized']\\n",
    "\\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\\n",
    "\\n",
    "print(f\\\"Training set: {X_train.shape}, Test set: {X_test.shape}\\\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4. Model Training"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "model = LogisticRegression(class_weight='balanced')\\n",
    "model.fit(X_train, y_train)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5. Model Evaluation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "preds = model.predict(X_test)\\n",
    "probs = model.predict_proba(X_test)[:, 1]\\n",
    "\\n",
    "print(\\\"Classification Report:\\\")\\n",
    "print(classification_report(y_test, preds))\\n",
    "\\n",
    "print(f\\\"ROC-AUC Score: {roc_auc_score(y_test, probs):.4f}\\\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 6. Model Optimization & Tuning\\n",
    "*(Optional space for GridSearch if requested)*\\n",
    "We use class_weight='balanced' to naturally manage any class imbalance."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 7. Model Saving"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "joblib.dump(model, 'logistic_model_notebook.pkl')\\n",
    "print(\\\"Model successfully saved.\\\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 8. Sample API Usage Test"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "def query_model(cpu, mem):\\n",
    "    loaded_model = joblib.load('logistic_model_notebook.pkl')\\n",
    "    sample = pd.DataFrame({'cpu_utilization': [cpu], 'memory_utilization': [mem]})\\n",
    "    prediction = loaded_model.predict(sample)[0]\\n",
    "    prob = loaded_model.predict_proba(sample)[0][1]\\n",
    "    if prediction == 1:\\n",
    "        return f\\\"SHUTDOWN RECOMMENDED (Confidence: {prob:.2f})\\\"\\n",
    "    return f\\\"KEEP ACTIVE (Confidence: {1 - prob:.2f})\\\"\\n",
    "\\n",
    "# Test an idle machine\\n",
    "print(\\\"Test Idle:\\\", query_model(cpu=15, mem=45))\\n",
    "# Test an active machine\\n",
    "print(\\\"Test Active:\\\", query_model(cpu=80, mem=70))"
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
