from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
import aiofiles
from pathlib import Path
from assets.image_analysis import analyze_image_authenticity

app = FastAPI(title="ESP32-CAM Image Upload Server")

# Create static directory for frontend files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
# Image analysis logic moved to `image_analysis.py`

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Currency Detection Test Interface</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.1em; opacity: 0.9; }
            .content { padding: 40px; }
            .upload-section {
                border: 3px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                transition: all 0.3s ease;
            }
            .upload-section:hover { border-color: #4facfe; background: #f8f9ff; }
            .upload-section.dragover { border-color: #00f2fe; background: #e6f7ff; }
            .file-input {
                display: none;
            }
            .upload-btn {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .upload-btn:hover { transform: translateY(-2px); }
            .analyze-btn {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 20px;
                font-size: 1em;
                cursor: pointer;
                margin: 10px;
                transition: transform 0.2s ease;
            }
            .analyze-btn:hover { transform: translateY(-2px); }
            .analyze-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .preview-section {
                margin: 20px 0;
                text-align: center;
            }
            .preview-image {
                max-width: 100%;
                max-height: 300px;
                border-radius: 10px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }
            .results {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 25px;
                margin-top: 20px;
            }
            .result-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                margin: 10px 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .result-label { font-weight: 600; color: #333; }
            .result-value { 
                font-weight: 500;
                padding: 5px 15px;
                border-radius: 15px;
                color: white;
            }
            .authentic { background: #28a745; }
            .fake { background: #dc3545; }
            .value { background: #007bff; }
            .country { background: #6f42c1; }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4facfe;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Currency Detector</h1>
                <p>Upload currency images for AI-powered authenticity analysis</p>
            </div>
            
            <div class="content">
                <div class="upload-section" id="uploadSection">
                    <h3>📸 Select or Drop Currency Image</h3>
                    <p style="margin: 15px 0; color: #666;">Supports JPG, PNG, WEBP formats</p>
                    <input type="file" id="fileInput" class="file-input" accept="image/*">
                    <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                        Choose Image File
                    </button>
                    <p style="margin-top: 15px; color: #888; font-size: 0.9em;">
                        Or drag and drop an image here
                    </p>
                </div>
                
                <div class="preview-section" id="previewSection" style="display: none;">
                    <img id="previewImage" class="preview-image" alt="Preview">
                    <div style="margin-top: 15px;">
                        <button class="analyze-btn" onclick="analyzeImage(false)">🔍 Analyze Only</button>
                        <button class="analyze-btn" onclick="analyzeImage(true)">💾 Upload & Analyze</button>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing currency image...</p>
                </div>
                
                <div id="results"></div>
            </div>
        </div>

        <script>
            let selectedFile = null;
            
            // File input handling
            document.getElementById('fileInput').addEventListener('change', function(e) {
                handleFile(e.target.files[0]);
            });
            
            // Drag and drop handling
            const uploadSection = document.getElementById('uploadSection');
            
            uploadSection.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadSection.classList.add('dragover');
            });
            
            uploadSection.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadSection.classList.remove('dragover');
            });
            
            uploadSection.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadSection.classList.remove('dragover');
                handleFile(e.dataTransfer.files[0]);
            });
            
            function handleFile(file) {
                if (!file || !file.type.startsWith('image/')) {
                    showError('Please select a valid image file');
                    return;
                }
                
                selectedFile = file;
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('previewImage').src = e.target.result;
                    document.getElementById('previewSection').style.display = 'block';
                    document.getElementById('results').innerHTML = '';
                };
                reader.readAsDataURL(file);
            }
            
            async function analyzeImage(shouldUpload) {
                if (!selectedFile) {
                    showError('Please select an image first');
                    return;
                }
                
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                
                loading.style.display = 'block';
                results.innerHTML = '';
                
                try {
                    const formData = new FormData();
                    formData.append('image', selectedFile);
                    
                    const endpoint = shouldUpload ? '/upload' : '/analyze';
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        displayResults(data, shouldUpload);
                    } else {
                        showError(data.detail || 'Analysis failed');
                    }
                } catch (error) {
                    showError('Network error: ' + error.message);
                } finally {
                    loading.style.display = 'none';
                }
            }
            
            function displayResults(data, wasUploaded) {
                const results = document.getElementById('results');
                
                // Handle different response formats
                const analysis = data.analysis || data;
                const authenticity = analysis.authenticity === 'true';
                
                let html = '<div class="results"><h3>🔍 Analysis Results</h3>';
                
                if (wasUploaded && data.filename) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">📁 Saved as:</span>
                            <span class="result-value" style="background: #6c757d;">${data.filename}</span>
                        </div>
                    `;
                }
                
                html += `
                    <div class="result-item">
                        <span class="result-label">🔐 Authenticity:</span>
                        <span class="result-value ${authenticity ? 'authentic' : 'fake'}">
                            ${authenticity ? '✅ AUTHENTIC' : '❌ SUSPICIOUS'}
                        </span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">💵 Denomination:</span>
                        <span class="result-value value">${analysis.value || 'Unknown'}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">🌍 Country:</span>
                        <span class="result-value country">${analysis.country || 'Unknown'}</span>
                    </div>
                `;
                
                if (data.size) {
                    html += `
                        <div class="result-item">
                            <span class="result-label">📏 File Size:</span>
                            <span class="result-value" style="background: #17a2b8;">${(data.size / 1024).toFixed(1)} KB</span>
                        </div>
                    `;
                }
                
                html += '</div>';
                results.innerHTML = html;
            }
            
            function showError(message) {
                const results = document.getElementById('results');
                results.innerHTML = `<div class="error">❌ Error: ${message}</div>`;
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    # Check if file was uploaded
    if not image:
        raise HTTPException(status_code=400, detail="No image received")
    
    # Check if it's an image file (optional validation)
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate filename with timestamp
    timestamp = datetime.now().isoformat().replace(':', '-')
    filename = f"esp32-cam-{timestamp}.jpg"
    file_path = uploads_dir / filename
    
    try:
        # Read image content
        content = await image.read()
        
        # Analyze image for authenticity
        analysis_result = analyze_image_authenticity(content)
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        file_size = len(content)
        
        print(f"Image received: {filename}")
        print(f"Size: {file_size} bytes")
        print(f"Analysis result: {analysis_result}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Image uploaded and analyzed successfully",
                "filename": filename,
                "size": file_size,
                "analysis": analysis_result
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze")
async def analyze_only(image: UploadFile = File(...)):
    """
    Endpoint that only returns the analysis result in the requested format
    """
    # Check if file was uploaded
    if not image:
        raise HTTPException(status_code=400, detail="No image received")
    
    # Check if it's an image file
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image content
        content = await image.read()
        
        # Analyze image for authenticity
        analysis_result = analyze_image_authenticity(content)
        
        print(f"Analysis completed: {analysis_result}")
        
        # Return only the analysis result in the requested format
        return analysis_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
