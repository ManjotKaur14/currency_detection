# AI-Powered Currency Detection and Authenticity Verification System

An intelligent currency detection and authenticity verification system that uses **Computer Vision, Image Processing, and Machine Learning techniques** to identify currency denominations and analyze their authenticity.

The system processes currency images using advanced feature extraction, image matching, and Optical Character Recognition (OCR) to generate reliable detection results.

**Technology Stack:** Python | FastAPI | OpenCV | Tesseract OCR | Docker

---

## 1. Project Overview

The AI-Powered Currency Detection System is designed to automate the process of identifying and verifying currency notes through image analysis.

Users can upload currency images through a web interface or API. The system analyzes the uploaded image, extracts relevant visual features, performs OCR verification, and generates an authenticity assessment along with the detected denomination and country.

The system also supports multiple image orientations and evaluates image quality to improve the reliability of the analysis.

## 2. Key Features

### AI-Based Image Analysis
- ORB and SIFT-based feature extraction and matching.
- OCR-based verification using Tesseract.
- Multi-orientation image processing (0°, 90°, 180°, 270°).
- Image quality and sharpness assessment.
- Confidence-based authenticity scoring.

### User-Friendly Integration
- Interactive web interface.
- RESTful API endpoints.
- Real-time image processing.
- Docker-based deployment.
- ESP32-CAM integration for IoT applications.

## 3. Supported Currencies

| Currency | Supported Denominations |
|---|---|
| INR – Indian Rupee | ₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000 |
| USD – US Dollar | $1, $5, $10, $20, $50, $100 |
| EUR – Euro | €5, €10, €20, €50, €100, €200, €500 |
| GBP – British Pound | £5, £10, £20, £50 |

## 4. System Architecture and Workflow

The system follows a structured image-processing pipeline:

1. **Image Input:** The user uploads a currency image.
2. **Image Quality Assessment:** The system checks image sharpness and contrast.
3. **Image Enhancement:** The image is prepared for accurate processing.
4. **Orientation Handling:** Multiple image orientations are evaluated.
5. **Feature Extraction:** ORB and SIFT algorithms identify important visual features.
6. **Feature Matching:** Extracted features are compared with reference currency images.
7. **OCR Verification:** Tesseract OCR extracts and verifies relevant textual information.
8. **Confidence Scoring:** A confidence score is calculated from the analysis.
9. **Authenticity Decision:** The system generates an authenticity assessment.
10. **Result Generation:** The detected denomination, country, and authenticity status are returned.

## 5. Installation and Setup

### Option 1: Docker Deployment

Docker provides a convenient way to build and run the application in a containerized environment.

```bash
git clone https://github.com/yourusername/currency-detection-system.git

cd currency-detection-system

docker build -t currency-detection .

docker run -d -p 3000:3000 --name currency-app currency-detection
```

Access the application:

```text
http://localhost:3000
```

### Option 2: Local Installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/yourusername/currency-detection-system.git

cd currency-detection-system
```

**Step 2: Create a virtual environment**

```bash
python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Start the application**

```bash
python main.py
```

## 6. API Documentation

The application provides RESTful endpoints for image analysis, file uploads, and application health monitoring.

### 6.1 Web Interface

**Endpoint:** `GET /`

Provides an interactive web interface for uploading currency images and viewing analysis results.

### 6.2 Currency Image Analysis

**Endpoint:** `POST /analyze`

Accepts an image and performs currency detection and authenticity analysis.

**Request:**
```http
POST /analyze
Content-Type: multipart/form-data
```

**Response:**
```json
{
  "authenticity": "true",
  "value": "100",
  "country": "India"
}
```

### 6.3 Upload and Analyze

**Endpoint:** `POST /upload`

Uploads a currency image, stores the file, and performs the analysis.

**Response:**
```json
{
  "success": true,
  "message": "Image uploaded and analyzed successfully",
  "filename": "currency_20241215_143022.jpg",
  "size": 245760,
  "analysis": {
    "authenticity": "true",
    "value": "100",
    "country": "India"
  }
}
```

### 6.4 Application Health Check

**Endpoint:** `GET /health`

Checks the application's operational status and reference image availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T14:30:22.123456",
  "reference_images_loaded": 151
}
```

## 7. Docker Deployment

The application supports Docker Compose for simplified container management.

**Example docker-compose.yml**

```yaml
version: '3.8'

services:
  currency-detection:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./uploads:/app/uploads
      - ./reference_notes:/app/reference_notes:ro
    restart: unless-stopped
```

Start the application:

```bash
docker-compose up -d
```

Additional Docker commands:

```bash
docker build -t currency-detection .

docker logs currency-app -f

docker stop currency-app
```

## 8. ESP32-CAM Integration

The system supports integration with ESP32-CAM, enabling image capture through an IoT camera module.

Captured currency images can be transmitted to the FastAPI backend for analysis through HTTP requests.

This integration allows the system to be extended into a camera-based currency detection application.

## 9. Configuration and Optimization

The system provides configurable parameters to control image quality assessment, feature extraction, and authenticity verification.

### Image Quality Parameters

```python
MIN_SHARPNESS = 50
MIN_CONTRAST = 40
MIN_MATCH_COUNT = 15
CONFIDENCE_THRESHOLD = 0.20
```

### Feature Detection Parameters

```python
ORB_FEATURES = 3000
SIFT_FEATURES = 2000
ORIENTATIONS = 4
```

These parameters can be adjusted according to image quality and processing requirements.

## 10. Performance Metrics

| Metric | Performance |
|---|---|
| Processing Time | 1–3 seconds per image |
| Accuracy | 95%+ with good-quality images |
| Supported Formats | JPG, PNG, WEBP |
| Maximum File Size | 10 MB |
| Memory Usage | 100–200 MB |
| Reference Images | 151 loaded |

*Performance values are based on the project's documented configuration.*

## 11. Project Structure

```text
currency-detection-system/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── assets/
│   └── image_analysis.py
│
├── reference_notes/
│   ├── INR/
│   │   ├── 10/
│   │   ├── 20/
│   │   ├── 50/
│   │   └── ...
│   ├── USD/
│   └── EUR/
│
├── uploads/
├── static/
│
└── README.md
```

### Directory Description

- **main.py:** Main FastAPI application.
- **requirements.txt:** Python dependencies.
- **assets/image_analysis.py:** Core image-processing and feature-matching algorithms.
- **reference_notes/:** Reference images organized by currency and denomination.
- **uploads/:** Stores uploaded currency images.
- **static/:** Contains static web interface resources.
- **Dockerfile:** Defines the container build configuration.

## 12. Adding New Currencies

The system can be extended to support additional currencies.

Steps:

1. Create a new currency directory inside `reference_notes/`.
2. Create separate subdirectories for each denomination.
3. Add multiple reference images for every denomination.
4. Update `CURRENCY_DENOMINATIONS` in `image_analysis.py`.
5. Configure the corresponding ROI coordinates in `NOTE_ROIS`.

## 13. Testing

The project supports automated testing using Pytest.

Install testing dependencies:

```bash
pip install pytest pytest-asyncio httpx
```

Run tests:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=assets tests/
```

## 14. Troubleshooting

### Tesseract OCR Not Found

Install Tesseract OCR according to your operating system.

```bash
# Windows
choco install tesseract

# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

### Poor Image Quality

- Ensure sufficient lighting.
- Keep the currency note in focus.
- Avoid camera movement.
- Clean the camera lens.
- Capture the note from a suitable distance.

### Reference Images Not Loading

- Verify that the `reference_notes/` directory exists.
- Check the supported image formats.
- Maintain the required directory structure.
- Verify file permissions.

### Port Already in Use

Check whether another process is using port 3000.

```bash
netstat -ano | findstr :3000
```

Alternatively, use another available port.

## 15. Future Scope

Potential improvements and extensions include:

- Support for additional international currencies.
- Improved image classification and authenticity verification.
- Integration with additional camera-based devices.
- Enhanced processing speed and accuracy.
- Improved user interface and reporting capabilities.

## 16. License

This project is distributed under the MIT License.

## 17. Acknowledgements

We acknowledge the following technologies and tools used in the development of this project:

- **OpenCV:** Computer vision and image processing.
- **FastAPI:** Backend API development.
- **Tesseract OCR:** Text extraction and verification.
- **ORB and SIFT:** Feature detection and matching.
- **Docker:** Application containerization and deployment.

---

**Developed with the aim of making currency identification and authenticity analysis more accessible through AI and computer vision.**
