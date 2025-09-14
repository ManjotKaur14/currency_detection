# 📁 Hierarchical Folder Structure Guide

## 🎯 **New Organized Structure**

The system now supports a **clean hierarchical folder structure** that's much easier to manage:

```
reference_notes/
├── INR/                    # Indian Rupees folder
│   ├── 10/                 # ₹10 notes folder
│   │   ├── main.jpg        # Primary ₹10 reference
│   │   ├── variant1.jpg    # ₹10 variant 1
│   │   ├── variant2.jpg    # ₹10 variant 2
│   │   ├── old_series.jpg  # Old series ₹10
│   │   └── worn.jpg        # Worn condition ₹10
│   ├── 20/                 # ₹20 notes folder
│   │   ├── main.jpg
│   │   ├── variant1.jpg
│   │   └── variant2.jpg
│   ├── 50/                 # ₹50 notes folder
│   ├── 100/                # ₹100 notes folder
│   ├── 200/                # ₹200 notes folder
│   ├── 500/                # ₹500 notes folder
│   └── 2000/               # ₹2000 notes folder
├── USD/                    # US Dollars folder
│   ├── 1/                  # $1 bills folder
│   ├── 5/                  # $5 bills folder
│   ├── 10/                 # $10 bills folder
│   ├── 20/                 # $20 bills folder
│   ├── 50/                 # $50 bills folder
│   └── 100/                # $100 bills folder
├── EUR/                    # Euros folder
│   ├── 5/
│   ├── 10/
│   ├── 20/
│   ├── 50/
│   ├── 100/
│   ├── 200/
│   └── 500/
└── GBP/                    # British Pounds folder
    ├── 5/
    ├── 10/
    ├── 20/
    └── 50/
```

## 🚀 **Benefits of Hierarchical Structure**

### **✅ Advantages:**
- **Super organized** - Easy to find and manage images
- **Scalable** - Add new currencies/denominations easily
- **Clean naming** - Simple filenames like `main.jpg`, `variant1.jpg`
- **Logical grouping** - All variants of same denomination together
- **Easy maintenance** - Clear structure for adding/removing images

### **📊 Comparison:**

| Flat Structure | Hierarchical Structure |
|----------------|----------------------|
| `INR_100_1.jpg` | `INR/100/variant1.jpg` |
| `INR_100_2.jpg` | `INR/100/variant2.jpg` |
| `INR_100_old.jpg` | `INR/100/old_series.jpg` |
| `USD_20_worn.jpg` | `USD/20/worn.jpg` |

## 📝 **Naming Convention Inside Folders**

**Inside each denomination folder, use descriptive names:**

```
INR/100/
├── main.jpg           # Primary/best reference
├── variant1.jpg       # Alternative version 1
├── variant2.jpg       # Alternative version 2
├── variant3.jpg       # Alternative version 3
├── old_series.jpg     # Old design series
├── new_series.jpg     # New design series
├── worn.jpg           # Worn condition
├── bright.jpg         # Bright lighting
├── dim.jpg            # Dim lighting
├── crisp.jpg          # Crisp/new condition
└── faded.jpg          # Slightly faded
```

## 🔧 **How It Works**

**The system automatically converts:**
- `INR/100/main.jpg` → `INR_100_main` (internal ID)
- `USD/20/variant1.jpg` → `USD_20_variant1` (internal ID)
- `EUR/50/old_series.jpg` → `EUR_50_old_series` (internal ID)

**For OCR, it uses the base denomination:**
- `INR_100_main` → Uses `INR_100` ROI coordinates
- `INR_100_variant1` → Uses `INR_100` ROI coordinates
- `USD_20_worn` → Uses `USD_20` ROI coordinates

## 🎯 **Recommended Setup Strategy**

### **Step 1: Create Currency Folders**
```bash
mkdir -p reference_notes/INR/{10,20,50,100,200,500,2000}
mkdir -p reference_notes/USD/{1,5,10,20,50,100}
mkdir -p reference_notes/EUR/{5,10,20,50,100,200,500}
mkdir -p reference_notes/GBP/{5,10,20,50}
```

### **Step 2: Add Images Systematically**
Start with your most common currency:
```
INR/100/main.jpg        # Best quality ₹100 note
INR/100/variant1.jpg    # Different lighting
INR/100/variant2.jpg    # Slightly worn
```

### **Step 3: Validate Setup**
```bash
python validate_references.py
```

## 🔄 **Backward Compatibility**

**The system supports BOTH structures simultaneously:**

✅ **Flat structure** (existing): `INR_100_1.jpg` in root folder
✅ **Hierarchical structure** (new): `INR/100/variant1.jpg` in folders

**Priority:** Flat structure files take precedence if both exist.

## 📈 **Expected Accuracy Improvements**

**With organized hierarchical structure:**

| Denomination | Images | Expected Accuracy |
|-------------|--------|------------------|
| INR/100/ | 1 image | 60-70% |
| INR/100/ | 3 images | 80-85% |
| INR/100/ | 5 images | 85-92% |
| INR/100/ | 7+ images | 90-95% |

## 💡 **Pro Tips**

### **Image Quality Priority:**
1. **main.jpg** - Highest quality, perfect lighting
2. **variant1.jpg** - Good quality, different angle
3. **variant2.jpg** - Different lighting condition
4. **old_series.jpg** - Different design series
5. **worn.jpg** - Realistic wear condition

### **Folder Management:**
- Keep **2-5 images** per denomination initially
- Add more based on accuracy needs
- Use **descriptive filenames** for easy identification
- **Test frequently** with validation script

### **Migration from Flat Structure:**
If you have existing flat structure files:
1. **Keep them** - they'll still work
2. **Gradually migrate** to folder structure
3. **Test both** to ensure accuracy
4. **Remove flat files** once folder structure is complete

## 🔍 **Validation Commands**

**Check folder structure:**
```bash
python validate_references.py
```

**Check specific currency:**
```bash
ls -la reference_notes/INR/
ls -la reference_notes/USD/
```

**Test server loading:**
```bash
python main.py
# Look for: "Scanning INR folder" and "Loading variants from INR_100 folder"
```

---

**🎉 This hierarchical structure makes managing hundreds of reference images much easier and more organized!**