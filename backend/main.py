from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import requests
import numpy as np
import pandas as pd
from meteostat import Point, Daily
from datetime import datetime, timedelta
from geopy.distance import geodesic
import logging

import json
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained Random Forest model
MODEL_PATH = "random_forest_model.pkl"
try:
    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise e

# Load charging station data
STATION_DATA_PATH = "charging_stations.csv"
def load_station_data(csv_file_path):
    try:
        df = pd.read_csv(csv_file_path)
        df.columns = df.columns.str.strip()
        stations = {
            row["station_name"]: {
                "location": {"lat": row["latitude"], "lon": row["longitude"]},
                "encoded": row["encoded"],
            }
            for _, row in df.iterrows()
        }
        logging.info("Charging stations loaded successfully.")
        return stations
    except Exception as e:
        logging.error(f"Failed to load station data: {e}")
        raise e

charging_stations = load_station_data(STATION_DATA_PATH)

# HERE API Setup
HERE_API_KEY = "OywB5dZJhueuop5qQb-gCIESDdExRxg1IgjrYtjgWiQ"
ROUTING_URL = "https://router.hereapi.com/v8/routes"

def get_traffic_data(origin_lat, origin_lon, dest_lat, dest_lon):
    params = {
        "transportMode": "car",
        "origin": f"{origin_lat},{origin_lon}",
        "destination": f"{dest_lat},{dest_lon}",
        "return": "summary",
        "apikey": HERE_API_KEY,
    }
    try:
        response = requests.get(ROUTING_URL, params=params)
        response.raise_for_status()
        summary = response.json()["routes"][0]["sections"][0]["summary"]
        return {
            "length_m": summary["length"],
            "duration_s": summary["duration"],
            "base_duration_s": summary["baseDuration"],
        }
    except Exception as e:
        logging.error(f"Error fetching traffic data: {e}")
        return {"length_m": 0, "duration_s": 0, "base_duration_s": 0}

def get_weather_data(latitude, longitude):
    try:
        end = datetime.now()
        start = end - timedelta(days=4)
        location = Point(latitude, longitude)
        data = Daily(location, start, end).fetch()
        return {
            "tmin": data["tmin"].min() if "tmin" in data else 0,
            "tmax": data["tmax"].max() if "tmax" in data else 0,
            "tavg": data["tavg"].mean() if "tavg" in data else 0,
            "coco": data["coco"].values[0] if "coco" in data else 0,
        }
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return {"tmin": 0, "tmax": 0, "tavg": 0, "coco": 0}

class PredictionInput(BaseModel):
    latitude: float
    longitude: float

def find_closest_stations(user_lat, user_lon, stations, radius_km=5):
    user_location = (user_lat, user_lon)
    closest_stations = {
        name: {
            "distance_km": geodesic(user_location, (info["location"]["lat"], info["location"]["lon"])).kilometers,
            "encoded": info["encoded"],
        }
        for name, info in stations.items()
        if geodesic(user_location, (info["location"]["lat"], info["location"]["lon"])).kilometers <= radius_km
    }
    return dict(sorted(closest_stations.items(), key=lambda x: x[1]["distance_km"]))

@app.post("/predict")
async def predict_energy(input_data: PredictionInput):
    charging_time_seconds = 2000
    user_location = (input_data.latitude, input_data.longitude)
    try:
        closest_stations = find_closest_stations(input_data.latitude, input_data.longitude, charging_stations, 3)
        if not closest_stations:
            raise HTTPException(status_code=404, detail="No charging stations found within 3 km.")
        predictions = []
        for station_name, details in closest_stations.items():
            station = charging_stations[station_name]
            station_location = (station["location"]["lat"], station["location"]["lon"])
            traffic = get_traffic_data(input_data.latitude, input_data.longitude, station["location"]["lat"], station["location"]["lon"])
            weather = get_weather_data(station["location"]["lat"], station["location"]["lon"])
            now = datetime.now()
            features = np.array([
                input_data.latitude, input_data.longitude,
                weather["tmin"], weather["tmax"], weather["tavg"], weather["coco"],
                station["location"]["lat"], station["location"]["lon"],
                traffic["length_m"], traffic["duration_s"], traffic["base_duration_s"],
                now.year, now.month, now.day, now.hour, now.weekday(),
                charging_time_seconds, station["encoded"]
            ]).reshape(1, -1)
            predicted_energy = model.predict(features)[0]
            predictions.append({
                "station_name": station_name,
                "station_location": station_location,
                "user_location": user_location,
                "distance_km": details["distance_km"],
                "predicted_energy_kwh": predicted_energy,
                "traffic_duration_s": traffic["duration_s"],
            })
        # Sort by predicted energy consumption
        top_stations = sorted(predictions, key=lambda x: x["predicted_energy_kwh"])[:5]
        return {"top_stations": top_stations}

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
