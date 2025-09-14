# 💰 Currency Detection System

An AI-powered currency authenticity detection system built with FastAPI and OpenCV. This system uses advanced computer vision techniques including feature matching (ORB + SIFT), OCR verification, and multi-orientation support to analyze currency notes and determine their authenticity.

## 🚀 Features

- **Multi-Algorithm Feature Matching**: Uses both ORB and SIFT algorithms for robust feature detection
- **OCR Verification**: Pytesseract-based denomination verification with multiple preprocessing techniques
- **Multi-Orientation Support**: Automatically handles different note orientations
- **Image Quality Assessment**: Evaluates image sharpness, brightness, and contrast
- **Real-time Analysis**: Fast processing with confidence scoring
- **Web Interface**: Beautiful, responsive web UI for easy testing
- **REST API**: Clean API endpoints for integration

## 🏗️ Architecture

### Supported Currencies
- **INR** (Indian Rupees): 10, 20, 50, 100, 200, 500, 2000
- **USD** (US Dollars): 1, 5, 10, 20, 50, 100
- **EUR** (Euro): 5, 10, 20, 50, 100, 200, 500
- **GBP** (British Pounds): 5, 10, 20, 50

### Analysis Pipeline
1. **Image Quality Assessment** - Evaluates sharpness, brightness, contrast
2. **Image Enhancement** - CLAHE enhancement and noise reduction
3. **Multi-Orientation Processing** - Tests 4 different orientations
4. **Feature Matching** - ORB and SIFT feature extraction and matching
5. **OCR Verification** - Denomination text recognition
6. **Confidence Scoring** - Combined confidence calculation
7. **Authenticity Decision** - Final authentic/suspicious classification

## 📋 Prerequisites

- Python 3.7+
- Tesseract OCR (for text recognition)
- OpenCV compatible system

### Installing Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Verify: `tesseract --version`

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/currency-detection-system.git
cd currency-detection-system
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up reference notes** (Optional)
Create a `reference_notes/` directory and add reference currency images:
```
reference_notes/
├── INR/
│   ├── 100/
│   │   ├── front.jpg
│   │   └── back.jpg
│   └── 500/
│       └── sample.jpg
├── USD/
│   └── 20/
│       └── reference.jpg
└── ...
```

## 🚀 Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:3000`

### API Endpoints

#### 1. Web Interface
```
GET /
```
Access the web interface for interactive testing.

#### 2. Upload and Analyze
```
POST /upload
```
Upload an image file and save it while getting analysis results.

**Request:**
- Form data with `image` file

**Response:**
```json
{
  "success": true,
  "message": "Image uploaded and analyzed successfully",
  "filename": "esp32-cam-2024-01-15T10-30-45.jpg",
  "size": 245760,
  "analysis": {
    "authenticity": "true",
    "value": "100",
    "country": "India"
  }
}
```

#### 3. Analyze Only
```
POST /analyze
```
Analyze an image without saving it.

**Request:**
- Form data with `image` file

**Response:**
```json
{
  "authenticity": "true",
  "value": "100",
  "country": "India"
}
```

### Using the Web Interface

1. Open `http://localhost:3000` in your browser
2. Click "Choose Image File" or drag and drop an image
3. Click "🔍 Analyze Only" for analysis without saving
4. Click "💾 Upload & Analyze" to save and analyze
5. View results with authenticity status, denomination, and country

## 🔧 Configuration

### Key Parameters (in `assets/image_analysis.py`)

```python
MIN_MATCH_COUNT = 15  # Minimum feature matches required
FEATURE_MATCH_CONFIDENCE_THRESHOLD = 0.20  # Minimum confidence for feature matching
GEOMETRIC_VERIFICATION_THRESHOLD = 0.6  # Homography validation threshold
```

### ROI Configuration
Region of Interest coordinates for denomination detection can be customized in the `NOTE_ROIS` dictionary.

## 📁 Project Structure

```
currency-detection-system/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── assets/
│   └── image_analysis.py   # Core analysis algorithms
├── uploads/               # Uploaded images (created automatically)
├── static/               # Static files (created automatically)
├── reference_notes/      # Reference currency images (optional)
├── venv/                # Virtual environment
└── README.md            # This file
```

## 🧪 Testing

### Sample Test Cases

1. **High Quality Images**: Clear, well-lit currency notes
2. **Different Orientations**: Rotated notes (90°, 180°, 270°)
3. **Various Lighting**: Different lighting conditions
4. **Multiple Currencies**: Test with different currency types
5. **Edge Cases**: Blurry, partially visible, or damaged notes

### Expected Behavior

- **Authentic Notes**: Should return `authenticity: "true"` with correct denomination
- **Poor Quality**: Should return `authenticity: "false"` for very blurry images
- **Unknown Currency**: Should return `value: "0"` and `country: "Unknown"`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Ensure Tesseract is installed and in PATH
   - OCR will be disabled if Tesseract is not available

2. **No reference features loaded**
   - Check if `reference_notes/` directory exists
   - Ensure reference images are in supported formats (jpg, png, webp)

3. **Poor detection accuracy**
   - Ensure good image quality (sharp, well-lit)
   - Add more reference images for better matching
   - Adjust confidence thresholds in configuration

4. **Server won't start**
   - Check if port 3000 is available
   - Ensure all dependencies are installed
   - Verify Python version compatibility

### Debug Mode

Enable detailed logging by setting the logging level in `assets/image_analysis.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

- **Processing Time**: ~1-3 seconds per image
- **Supported Formats**: JPG, PNG, WEBP
- **Recommended Image Size**: 800x600 to 2000x1500 pixels
- **Memory Usage**: ~100-200MB during processing

## 🛡️ Security Considerations

- Input validation for file types and sizes
- No persistent storage of sensitive data
- Temporary file cleanup
- Rate limiting recommended for production use

## 📞 Support

For support, please open an issue on GitHub or contact [your-email@example.com].

---

**Note**: This system is designed for educational and research purposes. For production use in financial applications, additional security measures and regulatory compliance may be required.