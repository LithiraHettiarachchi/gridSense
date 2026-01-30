# gridSense

**Intelligent Energy Consumption Prediction for EV Charging Stations**

GridSense is an advanced machine learning system that predicts energy consumption at electric vehicle (EV) charging stations by analyzing consumption patterns, traffic data, and weather conditions. This enables utilities and charging network operators to optimize grid management, reduce peak loads, and improve EV traffic flow prediction.

## 🌟 Key Features

- **Energy Consumption Prediction**: Accurate forecasting of power demand at charging stations using historical consumption data
- **Traffic Pattern Analysis**: Predict EV arrival patterns and charging station occupancy based on traffic data
- **Weather Integration**: Incorporate meteorological factors (temperature, humidity, wind speed) that influence charging behavior
- **Analysing Machine Learning and Time Series Models**: Best model to forecast consumption
- **Real-Time Dashboard**: Interactive web interface for monitoring and predictions
- **Scalable Backend**: RESTful API for integration with utility management systems

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Data Requirements](#data-requirements)
- [Model Architecture](#model-architecture)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip and npm package managers
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LithiraHettiarachchi/gridSense.git
   cd gridSense
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start the backend server**:
   ```bash
   cd ../backend
   python app.py
   ```

5. **Start the frontend application** (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```

6. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:3000`

## 🏗️ System Architecture

gridSense follows a modern three-tier architecture:

### Backend
- **Framework**: Python Flask/FastAPI
- **Database**: Time-series database for consumption and traffic data
- **ML Pipeline**: Model training, evaluation, and inference
- **API Server**: RESTful endpoints for predictions and data management

### Frontend
- **Code Base**: HTML, CSS
- **Real-time Updates**: WebSocket integration for live data streaming
- **Visualization**: Interactive charts and heatmaps for energy consumption patterns
- **User Interface**: Dashboard for monitoring predictions and station metrics

### Data Pipeline
- **Data Sources**: EV charging consumption records, traffic sensors, weather APIs
- **Preprocessing**: Feature engineering, normalization, and temporal alignment
- **Storage**: Structured data storage for model training

## 💾 Installation

### Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database and API credentials
```

## 📊 Usage

### Running Predictions

#### Via API

```bash
# Get prediction for a specific charging station
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "CS001",
    "hours_ahead": 24,
    "weather_data": {
      "temperature": 22,
      "humidity": 65,
      "wind_speed": 5
    }
  }'
```

#### Via Python SDK

```python
from gridSense.models import EnergyPredictor

predictor = EnergyPredictor()
prediction = predictor.predict(
    station_id="CS001",
    hours_ahead=24,
    weather_data={"temperature": 22, "humidity": 65}
)
print(prediction.energy_forecast)
```

### Dashboard Features

The interactive dashboard provides:
- Real-time energy consumption monitoring
- 24-72 hour demand forecasts
- Traffic pattern visualization
- Weather impact analysis
- Historical trend analysis
- Charging station performance metrics

## 📈 Data Requirements

gridSense requires the following data inputs for optimal performance:

### Energy Consumption Data
- **Format**: Time-series data at 15-minute or hourly intervals
- **Required Fields**: Station ID, timestamp, kWh consumed, number of active chargers
- **Minimum History**: 6-12 months of historical data

### Traffic Data
- **Format**: Vehicle arrival/departure counts
- **Required Fields**: Station ID, timestamp, vehicle count
- **Optional**: Vehicle type classification (Tesla, Nissan Leaf, etc.)

### Weather Data
- **Format**: Point location or grid-based data
- **Required Fields**: Temperature, humidity, wind speed, cloud cover
- **Source**: Integration with OpenWeatherMap, NOAA, or local meteorological stations

### Sample Data Format

```csv
timestamp,station_id,energy_consumed_kwh,vehicles_charging,temperature_c,humidity_pct,wind_speed_kmh
2023-01-01 00:00,CS001,150.5,8,15.2,65,3.2
2023-01-01 01:00,CS001,180.3,10,14.8,68,2.9
2023-01-01 02:00,CS001,165.2,9,14.5,72,4.1
```

## 🤖 Model Architecture

gridSense employs an ensemble approach combining multiple machine learning paradigms:

### Models Included

1. **LSTM Neural Networks**
   - Captures long-term temporal dependencies
   - Particularly effective for energy consumption patterns
   - Architecture: Multi-layer bidirectional LSTM with attention mechanism

2. **XGBoost Gradient Boosting**
   - Handles non-linear relationships between features
   - Feature importance ranking for interpretability
   - Fast inference for real-time predictions

3. **ARIMA/SARIMA**
   - Classical time-series forecasting
   - Useful for baseline comparisons
   - Excellent for trend and seasonality decomposition

### Ensemble Strategy
Predictions are combined using weighted averaging, with weights optimized based on validation performance metrics across different time horizons and weather conditions.

### Performance Metrics

Standard metrics used for model evaluation:
- Mean Absolute Percentage Error (MAPE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- Peak Load Prediction Accuracy (±10%)

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Get Energy Forecast
```
POST /api/predict
Content-Type: application/json

Request:
{
  "station_id": "string",
  "hours_ahead": number (1-168),
  "weather_data": {
    "temperature": number,
    "humidity": number,
    "wind_speed": number
  },
  "include_confidence_interval": boolean (optional)
}

Response:
{
  "station_id": "string",
  "forecast": [
    {
      "timestamp": "2023-01-01T12:00:00Z",
      "predicted_energy_kwh": 175.5,
      "confidence_interval": [165.2, 185.8],
      "traffic_forecast": 9
    }
  ],
  "model_accuracy": 0.94,
  "last_updated": "2023-01-01T11:55:00Z"
}
```

#### Get Historical Data
```
GET /api/stations/{station_id}/history?start_date=2023-01-01&end_date=2023-01-31

Response:
{
  "station_id": "string",
  "data": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "energy_kwh": 150.5,
      "vehicles": 8,
      "temperature": 15.2
    }
  ]
}
```

#### List All Stations
```
GET /api/stations

Response:
{
  "stations": [
    {
      "station_id": "CS001",
      "location": "Downtown",
      "chargers": 12,
      "last_updated": "2023-01-01T11:55:00Z"
    }
  ]
}
```

## 🔧 Configuration

Configuration is managed through environment variables. Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/gridsense
REDIS_URL=redis://localhost:6379

# API
API_PORT=5000
API_HOST=0.0.0.0
API_DEBUG=False

# Models
MODEL_PATH=./models/
RETRAIN_FREQUENCY_DAYS=7

# External APIs
WEATHER_API_KEY=your_api_key
TRAFFIC_API_KEY=your_api_key

# Frontend
FRONTEND_URL=http://localhost:3000
```

## 📁 Project Structure

```
gridSense/
├── backend/
│   ├── app.py                 # Flask/FastAPI application
│   ├── config.py              # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Request/response schemas
│   ├── models/
│   │   ├── lstm_model.py      # LSTM implementation
│   │   ├── xgboost_model.py   # XGBoost implementation
│   │   └── ensemble.py        # Ensemble methods
│   └── utils/
│       ├── data_loader.py     # Data loading utilities
│       └── preprocessor.py    # Data preprocessing
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page layouts
│   │   ├── services/          # API client services
│   │   └── App.js             # Main application
│   ├── package.json           # Node dependencies
│   └── public/                # Static assets
├── models/
│   ├── lstm/                  # Pre-trained LSTM models
│   ├── xgboost/               # Pre-trained XGBoost models
│   └── scaler/                # Feature scalers
├── data/
│   ├── raw/                   # Raw data files
│   ├── processed/             # Processed datasets
│   └── schemas/               # Data schemas
├── notebooks/
│   ├── eda.ipynb              # Exploratory data analysis
│   ├── model_training.ipynb   # Model training pipeline
│   └── evaluation.ipynb       # Performance evaluation
└── README.md
```

## 🧪 Testing

Run the test suite:

```bash
# Backend tests
cd backend
pytest tests/ -v
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:
- Data preparation guide
- Model training and tuning
- API integration examples
- Deployment best practices
- Troubleshooting guide

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- Tests are included for new functionality
- Documentation is updated accordingly

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- EV charging infrastructure data providers
- Weather data sources (OpenWeatherMap, NOAA)
- Open-source machine learning communities

## 📞 Support & Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact: [lithirahettiarachchi.info@gmail.com]

---

**gridSense** - Making EV charging networks smarter, one prediction at a time. 🔋⚡
