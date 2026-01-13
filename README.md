# 🌱 EcoTrip Planner

A Streamlit web application that helps travelers in India make environmentally conscious travel decisions by calculating carbon emissions and suggesting greener alternatives.

## Features

- 🌍 Carbon footprint calculation for Indian travel routes
- 📊 Interactive visualizations of emissions data
- 🚗 Alternative route suggestions with cost comparisons
- 🗺️ Integration with real-time mapping and routing APIs
- 🇮🇳 India-specific travel data and recommendations

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   - **Climatiq API Key**: Get from [climatiq.io](https://www.climatiq.io/)
   - **Google Maps API Key**: Get from [Google Cloud Console](https://developers.google.com/maps/documentation/directions/get-api-key)

### 3. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
ecotrip-planner/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                   # Environment variables template
├── README.md                      # Project documentation
└── components/                    # Modular application components
    ├── __init__.py
    ├── models.py                  # Data models and structures
    ├── session_manager.py         # Session state management
    ├── ui_components.py           # User interface components
    ├── api_client.py              # External API integration
    ├── carbon_calculator.py       # Emissions calculation engine
    └── geographic_data.py         # Indian cities and distance calculations
```

## Development Status

This project is currently under development. The basic project structure and dependencies have been set up. Additional features will be implemented incrementally according to the development plan.

## API Requirements

- **Climatiq API**: For accurate carbon emissions data
- **Google Maps Directions API**: For route alternatives and mapping

Both APIs have fallback mechanisms using static data when services are unavailable.

## License

This project is developed for sustainable travel awareness and education.