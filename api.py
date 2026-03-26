from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import math

app = FastAPI(
    title="Eco-Scale Control API",
    description="Predictive Machine Learning API to safely shut down underutilized servers in a cluster.",
    version="1.0.0"
)

# Load the trained Random Forest model on startup
try:
    model = joblib.load("rf_cluster_model.pkl")
    print("✓ Model successfully loaded into memory.")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    model = None

class ClusterMetrics(BaseModel):
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of the day in 24hr format (0-23).")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of the week (0=Monday, 6=Sunday).")
    avg_cpu_load: float = Field(..., ge=0.0, le=100.0, description="Average % CPU utilization across the cluster.")
    avg_memory_load: float = Field(..., ge=0.0, le=100.0, description="Average % Memory utilization across the cluster.")
    network_traffic_gbps: float = Field(..., ge=0.0, description="Network traffic flowing into the cluster in Gbps.")
    total_servers: int = Field(1000, description="Total number of physical servers in the cluster.", ge=10)

class PredictionResponse(BaseModel):
    action: str
    servers_to_shutdown: int
    active_servers_remaining: int
    message: str

@app.get("/")
@app.get("/health")
def health_check():
    """Returns 200 if the API and Model are functioning online."""
    if model is None:
        raise HTTPException(status_code=503, detail="Machine Learning model failed to load.")
    return {"status": "online", "model": "RandomForestRegressor"}

@app.post("/predict/cluster", response_model=PredictionResponse)
def predict_cluster_capacity(metrics: ClusterMetrics):
    """
    Simulates sending live telemetry from your load balancers to the Eco-Scale ML Engine.
    Returns the exact number of nodes that can be strictly powered down.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Machine Learning model is not available.")
    
    # 1. Prepare features identically to the training schema
    features = pd.DataFrame([{
        'hour_of_day': metrics.hour_of_day,
        'day_of_week': metrics.day_of_week,
        'avg_cpu_load': metrics.avg_cpu_load,
        'avg_memory_load': metrics.avg_memory_load,
        'network_traffic_gbps': metrics.network_traffic_gbps
    }])
    
    # 2. Get the base prediction (which assumes a 1000-node cluster baseline)
    base_shutdown_prediction = model.predict(features)[0]
    
    # 3. Scale algebraically to the user's actual cluster size
    scaled_shutdowns = int(base_shutdown_prediction * (metrics.total_servers / 1000.0))
    
    # 4. Standard validation
    scaled_shutdowns = max(0, min(metrics.total_servers, scaled_shutdowns))
    active_servers = metrics.total_servers - scaled_shutdowns
    
    # 5. Format response
    if scaled_shutdowns > 0:
        action = "CONSOLIDATE_AND_SHUTDOWN"
        msg = f"It is statistically safe to power down {scaled_shutdowns} machines immediately. Leave {active_servers} machines online to handle current traffic spikes natively."
    else:
        action = "DO_NOT_SHUTDOWN"
        msg = f"Zero shutdowns recommended. Maintain all {metrics.total_servers} servers to handle the current load safely without hitting the 75% hardware capacity ceiling."
        
    return {
        "action": action,
        "servers_to_shutdown": scaled_shutdowns,
        "active_servers_remaining": active_servers,
        "message": msg
    }
