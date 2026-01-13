# EcoTrip Planner Deployment Guide

## Overview

This guide covers deployment options for the EcoTrip Planner application, from local development to production deployment on various platforms.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)
- API keys for external services (optional but recommended)

## Environment Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ecotrip-planner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` file with your API keys:

```env
# Required for real-time emissions data
CLIMATIQ_API_KEY=your_climatiq_api_key_here

# Required for detailed route alternatives
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

**Note:** The application works without API keys using fallback data, but functionality will be limited.

### 3. API Key Setup

#### Climatiq API
1. Visit [Climatiq.io](https://www.climatiq.io/)
2. Sign up for a free account
3. Generate an API key from your dashboard
4. Add to `.env` file

#### Google Maps API
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Directions API
4. Create credentials (API key)
5. Add to `.env` file

## Local Development

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Development Configuration

The application includes development-friendly features:
- Automatic error handling with fallback mechanisms
- Comprehensive logging and debugging information
- Session state management for data persistence
- Real-time API status monitoring

## Production Deployment

### Streamlit Cloud (Recommended)

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py` as the main file
   - Add environment variables in the Streamlit Cloud dashboard

3. **Environment Variables in Streamlit Cloud**
   - Go to your app settings
   - Add secrets in TOML format:
   ```toml
   CLIMATIQ_API_KEY = "your_key_here"
   GOOGLE_MAPS_API_KEY = "your_key_here"
   ```

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI (varies by OS)
   # Visit: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create ecotrip-planner-app
   heroku config:set CLIMATIQ_API_KEY=your_key_here
   heroku config:set GOOGLE_MAPS_API_KEY=your_key_here
   ```

3. **Create Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t ecotrip-planner .
   docker run -p 8501:8501 \
     -e CLIMATIQ_API_KEY=your_key_here \
     -e GOOGLE_MAPS_API_KEY=your_key_here \
     ecotrip-planner
   ```

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Configure security groups (port 8501)
   - Launch with your key pair

2. **Setup on EC2**
   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # Install dependencies
   sudo apt update
   sudo apt install python3-pip python3-venv git -y

   # Clone and setup
   git clone <repository-url>
   cd ecotrip-planner
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env with your API keys

   # Run with nohup for persistent execution
   nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
   ```

## Configuration Options

### Streamlit Configuration

The application includes a comprehensive `.streamlit/config.toml` file with:
- Eco-friendly theme colors
- Performance optimizations
- Security settings
- Caching configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLIMATIQ_API_KEY` | No | API key for real-time emissions data |
| `GOOGLE_MAPS_API_KEY` | No | API key for detailed route information |
| `STREAMLIT_SERVER_PORT` | No | Custom port (default: 8501) |
| `STREAMLIT_SERVER_ADDRESS` | No | Custom address (default: localhost) |

### Performance Tuning

For production deployments:

1. **Enable Caching**
   - Streamlit caching is enabled by default
   - API responses are cached to reduce external calls

2. **Memory Management**
   - Session state is automatically cleaned up
   - Large data objects are handled efficiently

3. **Error Handling**
   - Graceful degradation when APIs are unavailable
   - Comprehensive error logging and user feedback

## Monitoring and Maintenance

### Health Checks

The application includes built-in health monitoring:
- API connectivity status
- Session state validation
- Error tracking and reporting

### Logging

Logs are available through:
- Streamlit's built-in logging
- Application-specific error tracking
- API call monitoring

### Updates and Maintenance

1. **Regular Updates**
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```

2. **API Key Rotation**
   - Update environment variables
   - Restart the application
   - Monitor for connectivity issues

3. **Backup and Recovery**
   - No persistent data storage required
   - Configuration files should be version controlled
   - API keys should be securely stored

## Troubleshooting

### Common Issues

1. **API Connection Failures**
   - Check API key validity
   - Verify network connectivity
   - Application automatically falls back to static data

2. **Port Conflicts**
   - Change port in configuration
   - Use `--server.port` flag when running

3. **Memory Issues**
   - Monitor session state size
   - Clear browser cache
   - Restart application if needed

### Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test API connectivity
4. Review Streamlit documentation

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secure secret management
   - Rotate keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Configure appropriate firewall rules
   - Monitor for unusual traffic patterns

3. **Data Privacy**
   - No user data is permanently stored
   - Session data is temporary and browser-specific
   - API calls may be logged by external services

## Performance Benchmarks

Expected performance metrics:
- **Load Time**: < 3 seconds for initial page load
- **Calculation Time**: < 5 seconds for emissions calculation
- **API Response**: < 2 seconds for external API calls
- **Memory Usage**: < 100MB per active session

## Scaling Considerations

For high-traffic deployments:
1. Use load balancers for multiple instances
2. Implement API rate limiting and caching
3. Monitor resource usage and scale accordingly
4. Consider CDN for static assets