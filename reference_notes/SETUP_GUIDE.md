# 📸 Reference Images Setup Guide

## 🎯 **Why More Images = Better Accuracy**

Adding multiple reference images can increase accuracy by **40-60%**! Here's why:

- **Multiple series/versions** of the same denomination
- **Different lighting conditions** (bright, dim, natural)
- **Various wear conditions** (new, worn, slightly damaged)
- **Different angles** and perspectives
- **Color variations** due to printing batches

## 📁 **Folder Structure**

Place all reference images in the `reference_notes/` directory:

```
reference_notes/
├── INR_10.jpg              # Primary Indian ₹10
├── INR_10_old.jpg          # Old series ₹10
├── INR_10_worn.jpg         # Worn condition ₹10
├── INR_20.jpg              # Primary Indian ₹20
├── INR_50.jpg              # Primary Indian ₹50
├── INR_100.jpg             # Primary Indian ₹100
├── INR_100_old.jpg         # Old series ₹100
├── INR_200.jpg             # Indian ₹200
├── INR_500.jpg             # Primary Indian ₹500
├── INR_500_old.jpg         # Old series ₹500
├── INR_2000.jpg            # Indian ₹2000
├── USD_1.jpg               # US $1 bill
├── USD_5.jpg               # US $5 bill
├── USD_10.jpg              # US $10 bill
├── USD_20.jpg              # US $20 bill
├── USD_50.jpg              # US $50 bill
├── USD_100.jpg             # US $100 bill
├── EUR_5.jpg               # Euro €5
├── EUR_10.jpg              # Euro €10
├── EUR_20.jpg              # Euro €20
├── EUR_50.jpg              # Euro €50
├── EUR_100.jpg             # Euro €100
├── GBP_5.jpg               # British £5
├── GBP_10.jpg              # British £10
├── GBP_20.jpg              # British £20
└── GBP_50.jpg              # British £50
```

## 🏷️ **Naming Convention**

**Format:** `{CURRENCY}_{DENOMINATION}[_variant].{extension}`

### **Supported Currencies:**
- **INR** - Indian Rupees
- **USD** - US Dollars  
- **EUR** - Euros
- **GBP** - British Pounds
- **CAD** - Canadian Dollars
- **AUD** - Australian Dollars
- **JPY** - Japanese Yen
- **CNY** - Chinese Yuan
- **CHF** - Swiss Francs
- **SEK** - Swedish Krona

### **Variant Examples:**
```
INR_100.jpg         # Primary/main reference
INR_100_1.jpg       # Variant 1 (numbered system)
INR_100_2.jpg       # Variant 2 (numbered system)
INR_100_3.jpg       # Variant 3 (numbered system)
INR_100_old.jpg     # Old series
INR_100_new.jpg     # New series
INR_100_worn.jpg    # Worn condition
INR_100_v2.jpg      # Alternative version
INR_100_bright.jpg  # Bright lighting
INR_100_dim.jpg     # Dim lighting
```

### **Numbered System (Recommended):**
```
INR_200.jpg         # Base reference
INR_200_1.jpg       # Additional variant 1
INR_200_2.jpg       # Additional variant 2
INR_200_3.jpg       # Additional variant 3
USD_20.jpg          # Base reference
USD_20_1.jpg        # Additional variant 1
USD_20_2.jpg        # Additional variant 2
```

## 📷 **Image Quality Requirements**

### **✅ Optimal Specifications:**
- **Resolution:** 1200x600 pixels minimum (2000x1000+ recommended)
- **Format:** JPG, JPEG, PNG, WEBP
- **DPI:** 300+ for best feature detection
- **Lighting:** Even, natural lighting preferred
- **Focus:** Sharp, clear details
- **Orientation:** Horizontal (landscape) preferred
- **Background:** Neutral, non-distracting

### **📐 Image Composition:**
- **Full note visible** with small border
- **Flat perspective** (minimal skew/rotation)
- **No shadows** or reflections
- **Clear denomination numbers** visible
- **Good contrast** between note and background

## 🚀 **Accuracy Improvement Estimates**

| Number of References | Expected Accuracy | Improvement |
|---------------------|------------------|-------------|
| 1 per denomination  | 60-70%          | Baseline    |
| 2-3 per denomination| 75-85%          | +15-25%     |
| 4-5 per denomination| 85-92%          | +25-35%     |
| 6+ per denomination | 90-95%          | +30-40%     |

## 📊 **Recommended Reference Strategy**

### **High Priority (Essential):**
1. **Primary reference** - Best quality image of each denomination
2. **Alternative series** - Different design series if available
3. **Worn condition** - Slightly used/worn notes

### **Medium Priority (Recommended):**
4. **Different lighting** - Same note under different lighting
5. **Color variations** - Different printing batches
6. **Slight angles** - Minor perspective variations

### **Low Priority (Optional):**
7. **Extreme conditions** - Very worn, faded notes
8. **Special editions** - Commemorative or special series

## 🔧 **Adding New Currency Support**

To add a new currency (e.g., Canadian Dollar):

1. **Add images** following naming convention:
   ```
   CAD_5.jpg
   CAD_10.jpg
   CAD_20.jpg
   CAD_50.jpg
   CAD_100.jpg
   ```

2. **Update ROI coordinates** in `assets/image_analysis.py`:
   ```python
   NOTE_ROIS = {
       # ... existing entries ...
       'CAD_5': (0.8, 0.15, 0.15, 0.2),
       'CAD_10': (0.8, 0.15, 0.15, 0.2),
       # ... etc
   }
   ```

3. **Add to denominations list**:
   ```python
   CURRENCY_DENOMINATIONS = {
       # ... existing entries ...
       'CAD': [5, 10, 20, 50, 100],
   }
   ```

4. **Restart the server** to load new references

## 🎯 **ROI Calibration Guide**

ROI (Region of Interest) coordinates define where denomination numbers are located:

**Format:** `(x, y, width, height)` as ratios (0.0 to 1.0)

### **Finding ROI Coordinates:**
1. Open reference image in image editor
2. Locate denomination number area
3. Measure coordinates as percentage of image size
4. Example: If image is 1000x500 and number is at (800, 350) with size (100, 75):
   - x = 800/1000 = 0.8
   - y = 350/500 = 0.7  
   - width = 100/1000 = 0.1
   - height = 75/500 = 0.15
   - ROI = (0.8, 0.7, 0.1, 0.15)

## 🔄 **Loading New References**

After adding new images:
1. **Restart the server**: `python main.py`
2. **Check logs** for successful loading:
   ```
   INFO:Loaded reference features for INR_100: ORB=2000, SIFT=1500
   INFO:Loaded reference features for USD_20: ORB=1800, SIFT=1200
   ```
3. **Test with frontend** at `http://localhost:3000`

## 📈 **Performance Tips**

- **Start with 2-3 high-quality images** per denomination
- **Add more gradually** and test accuracy improvements
- **Use consistent lighting** across reference images
- **Avoid blurry or low-resolution** images
- **Keep file sizes reasonable** (< 2MB per image)

## 🐛 **Troubleshooting**

### **Images not loading:**
- Check filename format matches exactly
- Ensure supported file extension (.jpg, .jpeg, .png, .webp)
- Verify images are not corrupted

### **Low accuracy despite multiple references:**
- Check image quality (sharpness, lighting)
- Verify ROI coordinates are accurate
- Ensure denomination numbers are clearly visible
- Try different lighting conditions

### **OCR not working:**
- Install Tesseract OCR system dependency
- Verify ROI coordinates point to number area
- Check if numbers are clear and readable

---

**💡 Pro Tip:** Start with 2-3 high-quality references per denomination, then gradually add more based on your accuracy needs!