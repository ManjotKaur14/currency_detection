# 🚀 Currency Detection System - Deployment Guide

This guide covers various deployment options for the Currency Detection System, from local development to production environments.

## 📋 Table of Contents

- [Local Development](#local-development)
- [Network Deployment](#network-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [ESP32-CAM Integration](#esp32-cam-integration)
- [Production Considerations](#production-considerations)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🏠 Local Development

### Prerequisites
- Python 3.7+
- Git
- 4GB RAM minimum, 8GB recommended

### Quick Setup
```bash
# Clone repository
git clone https://github.com/yourusername/currency-detection-system.git
cd currency-detection-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

### Access Points
- **Local**: http://localhost:3000
- **Web Interface**: http://localhost:3000
- **API Docs**: http://localhost:3000/docs (FastAPI auto-generated)

---

## 🌐 Network Deployment

### Local Network Access

#### 1. Find Your IP Address
```bash
# Windows
ipconfig | findstr IPv4

# macOS/Linux
ifconfig | grep inet
```

#### 2. Configure Firewall
**Windows:**
```bash
# Allow Python through firewall
netsh advfirewall firewall add rule name="Python Currency Detection" dir=in action=allow protocol=TCP localport=3000
```

**Linux (Ubuntu):**
```bash
sudo ufw allow 3000
```

#### 3. Start Server
```bash
python main.py
```

#### 4. Access from Network
- **URL Format**: `http://[YOUR_IP]:3000`
- **Example**: `http://192.168.1.100:3000`

### Custom Port Configuration
```python
# In main.py, change:
uvicorn.run(app, host="0.0.0.0", port=8080)  # Custom port
```

---

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads static

# Expose port
EXPOSE 3000

# Run application
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  currency-detection:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./uploads:/app/uploads
      - ./reference_notes:/app/reference_notes
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    
  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - currency-detection
    restart: unless-stopped
```

### Build and Run
```bash
# Build image
docker build -t currency-detection .

# Run container
docker run -d -p 3000:3000 --name currency-app currency-detection

# Or use docker-compose
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM) minimum
- **OS**: Ubuntu 20.04 LTS
- **Security Group**: Allow HTTP (80), HTTPS (443), Custom TCP (3000)

#### 2. Setup Script
```bash
#!/bin/bash
# setup.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y libgl1-mesa-glx libglib2.0-0 tesseract-ocr

# Clone repository
git clone https://github.com/yourusername/currency-detection-system.git
cd currency-detection-system

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/currency-detection.service > /dev/null <<EOF
[Unit]
Description=Currency Detection API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/currency-detection-system
Environment=PATH=/home/ubuntu/currency-detection-system/venv/bin
ExecStart=/home/ubuntu/currency-detection-system/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable currency-detection
sudo systemctl start currency-detection
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/currency-detection
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle large file uploads
        client_max_body_size 10M;
    }
}
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/currency-detection
gcloud run deploy --image gcr.io/PROJECT_ID/currency-detection --platform managed
```

### Heroku Deployment

#### Procfile
```
web: python main.py
```

#### Deploy Commands
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-currency-app

# Set buildpacks
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt

# Create Aptfile for system dependencies
echo "tesseract-ocr" > Aptfile

# Deploy
git push heroku main
```

---

## 📷 ESP32-CAM Integration

### ESP32-CAM Code Example
```cpp
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://192.168.1.100:3000/analyze";

void setup() {
  Serial.begin(115200);
  
  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  // ... other pin configurations
  
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_UXGA;
  config.jpeg_quality = 10;
  config.fb_count = 1;
  
  esp_camera_init(&config);
  
  // Optimize camera settings for currency detection
  sensor_t * s = esp_camera_sensor_get();
  s->set_quality(s, 8);        // Higher quality
  s->set_contrast(s, 1);       // Increase contrast
  s->set_sharpness(s, 2);      // Maximum sharpness
  s->set_denoise(s, 1);        // Enable denoising
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
}

void captureAndAnalyze() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW");
  
  String body = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n";
  body += "Content-Disposition: form-data; name=\"image\"; filename=\"currency.jpg\"\r\n";
  body += "Content-Type: image/jpeg\r\n\r\n";
  
  // Send image data
  int httpResponseCode = http.POST(body + String((char*)fb->buf, fb->len) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n");
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Analysis result: " + response);
  }
  
  esp_camera_fb_return(fb);
  http.end();
}
```

### ESP32-CAM Optimization Settings
```cpp
// For better image quality with currency detection
sensor_t * s = esp_camera_sensor_get();

// Quality settings (lower = better quality)
s->set_quality(s, 6);         // 0-63, lower is better
s->set_framesize(s, FRAMESIZE_UXGA); // 1600x1200

// Image enhancement
s->set_brightness(s, 0);      // -2 to 2
s->set_contrast(s, 2);        // -2 to 2, increase for currency
s->set_saturation(s, 0);      // -2 to 2
s->set_sharpness(s, 2);       // -2 to 2, maximum for text clarity
s->set_denoise(s, 1);         // Enable noise reduction

// Auto settings
s->set_whitebal(s, 1);        // Enable auto white balance
s->set_awb_gain(s, 1);        // Enable AWB gain
s->set_wb_mode(s, 0);         // Auto white balance mode
```

---

## 🏭 Production Considerations

### Performance Optimization

#### 1. Server Configuration
```python
# main.py - Production settings
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        workers=4,              # Multiple workers
        access_log=False,       # Disable access logs for performance
        log_level="warning"     # Reduce log verbosity
    )
```

#### 2. Gunicorn Configuration
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:3000
```

#### 3. Environment Variables
```bash
# .env file
WORKERS=4
LOG_LEVEL=warning
MAX_UPLOAD_SIZE=10485760  # 10MB
REFERENCE_IMAGES_PATH=/app/reference_notes
```

### Security Considerations

#### 1. Rate Limiting
```python
# Add to requirements.txt
slowapi==0.1.5

# In main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze")
@limiter.limit("10/minute")  # 10 requests per minute
async def analyze_only(request: Request, image: UploadFile = File(...)):
    # ... existing code
```

#### 2. Input Validation
```python
# File size and type validation
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]

@app.post("/analyze")
async def analyze_only(image: UploadFile = File(...)):
    # Validate file type
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")
    
    # Validate file size
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
```

#### 3. HTTPS Configuration
```nginx
# Nginx SSL configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        # ... other proxy settings
    }
}
```

### Monitoring Setup

#### 1. Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reference_images_loaded": len(_reference_features) if _reference_features else 0
    }
```

#### 2. Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('currency_detection.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

#### 3. Metrics Collection
```python
# Add prometheus metrics (optional)
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 📊 Monitoring & Maintenance

### System Monitoring

#### 1. Server Status Check
```bash
# Check if service is running
sudo systemctl status currency-detection

# View logs
sudo journalctl -u currency-detection -f

# Restart service
sudo systemctl restart currency-detection
```

#### 2. Performance Monitoring
```bash
# Monitor resource usage
htop

# Check disk space
df -h

# Monitor network connections
netstat -tulpn | grep :3000
```

#### 3. Log Analysis
```bash
# View application logs
tail -f currency_detection.log

# Check for errors
grep "ERROR" currency_detection.log

# Monitor request patterns
grep "POST /analyze" currency_detection.log | tail -20
```

### Backup Strategy

#### 1. Reference Images Backup
```bash
# Create backup
tar -czf reference_images_backup_$(date +%Y%m%d).tar.gz reference_notes/

# Restore backup
tar -xzf reference_images_backup_20241215.tar.gz
```

#### 2. Configuration Backup
```bash
# Backup configuration files
cp main.py main.py.backup
cp requirements.txt requirements.txt.backup
```

### Update Procedure

#### 1. Application Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart currency-detection
```

#### 2. System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip list --outdated
pip install --upgrade package_name
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 PID
```

#### 2. Permission Denied
```bash
# Fix file permissions
chmod +x main.py
chown -R $USER:$USER /path/to/project
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h

# Clear cache
sudo sync && sudo sysctl vm.drop_caches=3
```

#### 4. Image Quality Issues
- Check ESP32-CAM settings
- Improve lighting conditions
- Adjust quality thresholds in code
- Clean camera lens

### Performance Tuning

#### 1. Reduce Reference Images
```bash
# Keep only best quality images per denomination
ls reference_notes/INR/100/ | wc -l  # Check count
# Remove low-quality variants manually
```

#### 2. Optimize Image Processing
```python
# In image_analysis.py, reduce feature counts
ORB_create(nfeatures=1500)  # Instead of 3000
SIFT_create(nfeatures=1000)  # Instead of 2000
```

#### 3. Enable Caching
```python
# Add caching for processed images
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_feature_extraction(image_hash):
    # Cache feature extraction results
    pass
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Daily**: Check service status and logs
- **Weekly**: Monitor disk space and performance
- **Monthly**: Update dependencies and system packages
- **Quarterly**: Backup reference images and configurations

### Support Contacts

- **Technical Issues**: Create GitHub issue
- **Performance Problems**: Check monitoring dashboard
- **Security Concerns**: Follow security update procedures

---

**Note**: This deployment guide covers various scenarios from development to production. Choose the appropriate deployment method based on your requirements, scale, and infrastructure preferences.