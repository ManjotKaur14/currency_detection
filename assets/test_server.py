import requests
import json

def test_image_analysis():
    """
    Test script to demonstrate image analysis functionality
    """
    
    # Server URL
    base_url = "http://localhost:3001"
    
    print("FastAPI ESP32-CAM Image Analysis Server Test")
    print("=" * 50)
    
    # Test the root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return
    
    print("\nTo test image analysis, you can:")
    print("1. Use the web interface at: http://localhost:3001/docs")
    print("2. Send POST request to /upload (saves image + analysis)")
    print("3. Send POST request to /analyze (analysis only)")
    
    print("\nExample curl commands:")
    print("# Upload and analyze:")
    print('curl -X POST "http://localhost:3001/upload" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "image=@your_image.jpg"')
    
    print("\n# Analyze only:")
    print('curl -X POST "http://localhost:3001/analyze" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "image=@your_image.jpg"')
    
    print("\nExpected response format:")
    print(json.dumps({
        "authenticity": "true/false",
        "value": "100",
        "country": "India"
    }, indent=2))

if __name__ == "__main__":
    test_image_analysis()
