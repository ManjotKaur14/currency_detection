"""
Enhanced Currency Detection using Multi-Algorithm Approach
- Feature Matching (ORB + SIFT)
- OCR Verification with multiple preprocessing techniques
- Image quality assessment and enhancement
- Multi-orientation support
- Confidence scoring with multiple validation layers
"""

import cv2
import numpy as np
import pytesseract
import os
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import re
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced configuration parameters
REFERENCE_NOTES_DIR = Path(__file__).parent.parent / "reference_notes"
MIN_MATCH_COUNT = 15  # Reduced for better sensitivity
FEATURE_MATCH_CONFIDENCE_THRESHOLD = 0.20  # Lowered threshold
GEOMETRIC_VERIFICATION_THRESHOLD = 0.6  # For homography validation

# ROI coordinates for denomination numbers on different currency notes
# Format: (x, y, width, height) - relative to image dimensions
# IMPORTANT: These assume a HORIZONTAL note orientation
NOTE_ROIS = {
    # Indian Rupees (INR) - Bottom right corner typically
    'INR_10': (0.85, 0.7, 0.1, 0.15),
    'INR_20': (0.85, 0.7, 0.1, 0.15),
    'INR_50': (0.85, 0.7, 0.1, 0.15),
    'INR_100': (0.85, 0.7, 0.1, 0.15),
    'INR_200': (0.85, 0.7, 0.1, 0.15),
    'INR_500': (0.85, 0.7, 0.1, 0.15),
    'INR_2000': (0.85, 0.7, 0.1, 0.15),
    
    # US Dollars (USD) - Various positions
    'USD_1': (0.75, 0.15, 0.2, 0.2),
    'USD_5': (0.75, 0.15, 0.2, 0.2),
    'USD_10': (0.75, 0.15, 0.2, 0.2),
    'USD_20': (0.8, 0.1, 0.15, 0.15),
    'USD_50': (0.75, 0.15, 0.2, 0.2),
    'USD_100': (0.75, 0.15, 0.2, 0.2),
    
    # Euro (EUR) - Top right corner typically
    'EUR_5': (0.8, 0.1, 0.15, 0.2),
    'EUR_10': (0.8, 0.1, 0.15, 0.2),
    'EUR_20': (0.8, 0.1, 0.15, 0.2),
    'EUR_50': (0.8, 0.1, 0.15, 0.2),
    'EUR_100': (0.8, 0.1, 0.15, 0.2),
    'EUR_200': (0.8, 0.1, 0.15, 0.2),
    'EUR_500': (0.8, 0.1, 0.15, 0.2),
    
    # British Pounds (GBP)
    'GBP_5': (0.8, 0.15, 0.15, 0.2),
    'GBP_10': (0.8, 0.15, 0.15, 0.2),
    'GBP_20': (0.8, 0.15, 0.15, 0.2),
    'GBP_50': (0.8, 0.15, 0.15, 0.2),
}

# Expected denominations for each currency
CURRENCY_DENOMINATIONS = {
    'INR': [10, 20, 50, 100, 200, 500, 2000],
    'USD': [1, 5, 10, 20, 50, 100],
    'EUR': [5, 10, 20, 50, 100, 200, 500],
    'GBP': [5, 10, 20, 50],
}

# Global variables for cached reference features
_reference_features = None
_orb_detector = None
_sift_detector = None
_tesseract_available = True


def initialize_reference_features():
    """
    Load and pre-compute features for all reference notes using multiple algorithms.
    This is called once to improve performance.
    """
    global _reference_features, _orb_detector, _sift_detector
    
    if _reference_features is not None:
        return
    
    # Initialize multiple feature detectors for better accuracy
    _orb_detector = cv2.ORB_create(nfeatures=3000, scaleFactor=1.2, nlevels=8)
    try:
        _sift_detector = cv2.SIFT_create(nfeatures=2000)
        logger.info("SIFT detector initialized successfully")
    except AttributeError:
        logger.warning("SIFT not available, using ORB only")
        _sift_detector = None
    
    _reference_features = {}
    
    if not REFERENCE_NOTES_DIR.exists():
        print(f"Error: Reference notes directory not found at {REFERENCE_NOTES_DIR}")
        return
    
    # Load images from both flat structure and hierarchical folders
    allowed_ext = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # Method 1: Load from flat structure (backward compatibility)
    _load_images_from_directory(REFERENCE_NOTES_DIR, allowed_ext, "")
    
    # Method 2: Load from hierarchical folder structure
    _load_images_from_hierarchical_structure(REFERENCE_NOTES_DIR, allowed_ext)
    
    logger.info(f"Initialized {len(_reference_features)} reference note features")


def _load_images_from_directory(directory: Path, allowed_ext: set, prefix: str = ""):
    """Load images from a specific directory."""
    global _reference_features
    
    if not directory.exists():
        return
    
    for image_file in directory.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in allowed_ext:
            try:
                # Generate note_id based on structure
                if prefix:
                    # Hierarchical: prefix + filename (e.g., "INR_100" + "variant1")
                    note_id = f"{prefix}_{image_file.stem}"
                else:
                    # Flat: just filename (e.g., "INR_100_1")
                    note_id = image_file.stem
                
                # Skip if already loaded (flat structure takes precedence)
                if note_id in _reference_features:
                    continue
                
                ref_img_color = cv2.imread(str(image_file), cv2.IMREAD_COLOR)
                if ref_img_color is None:
                    continue
                
                # Enhance reference image quality
                ref_img_enhanced = enhance_image_quality(ref_img_color)
                ref_img_gray = cv2.cvtColor(ref_img_enhanced, cv2.COLOR_BGR2GRAY)
                
                # Extract features using multiple algorithms
                features_data = extract_multi_algorithm_features(ref_img_gray)
                
                if features_data['orb_desc'] is not None or features_data['sift_desc'] is not None:
                    _reference_features[note_id] = features_data
                    orb_count = len(features_data['orb_kp']) if features_data['orb_kp'] is not None else 0
                    sift_count = len(features_data['sift_kp']) if features_data['sift_kp'] is not None else 0
                    logger.info(f"Loaded reference features for {note_id}: ORB={orb_count}, SIFT={sift_count}")
                
            except Exception as e:
                logger.error(f"Error loading reference image {image_file}: {e}")


def _load_images_from_hierarchical_structure(base_dir: Path, allowed_ext: set):
    """Load images from hierarchical folder structure like INR/100/, USD/20/, etc."""
    global _reference_features
    
    if not base_dir.exists():
        return
    
    # Look for currency folders (INR, USD, EUR, etc.)
    for currency_dir in base_dir.iterdir():
        if not currency_dir.is_dir() or currency_dir.name.startswith('.'):
            continue
        
        currency_code = currency_dir.name.upper()
        
        # Skip if not a valid currency code
        if currency_code not in CURRENCY_DENOMINATIONS:
            continue
        
        logger.info(f"Scanning {currency_code} folder: {currency_dir}")
        
        # Look for denomination folders (10, 20, 50, etc.)
        for denom_dir in currency_dir.iterdir():
            if not denom_dir.is_dir():
                continue
            
            try:
                denomination = denom_dir.name
                # Validate denomination
                if int(denomination) not in CURRENCY_DENOMINATIONS[currency_code]:
                    continue
                
                base_note_id = f"{currency_code}_{denomination}"
                logger.info(f"Loading variants from {base_note_id} folder: {denom_dir}")
                
                # Load all images from this denomination folder
                _load_images_from_directory(denom_dir, allowed_ext, base_note_id)
                
            except (ValueError, KeyError):
                # Skip invalid denomination folders
                continue


# Check if Tesseract executable is available for pytesseract
try:
    _ = pytesseract.get_tesseract_version()
    _tesseract_available = True
    logger.info("Tesseract OCR available")
except Exception:
    _tesseract_available = False
    logger.warning("Tesseract not found. OCR will be disabled. Install Tesseract and ensure it's in PATH for OCR verification.")


def enhance_image_quality(img: np.ndarray) -> np.ndarray:
    """
    Enhance image quality using multiple techniques for better feature detection.
    """
    if len(img.shape) == 3:
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    else:
        # Grayscale enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(img)
    
    # Apply slight Gaussian blur to reduce noise
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    
    return enhanced


def extract_multi_algorithm_features(img_gray: np.ndarray) -> Dict:
    """
    Extract features using multiple algorithms for better matching accuracy.
    """
    features = {
        'orb_kp': None, 'orb_desc': None, 'orb_coords': None,
        'sift_kp': None, 'sift_desc': None, 'sift_coords': None
    }
    
    # ORB features
    if _orb_detector is not None:
        kp_orb, desc_orb = _orb_detector.detectAndCompute(img_gray, None)
        if desc_orb is not None and len(kp_orb) > 0:
            features['orb_kp'] = kp_orb
            features['orb_desc'] = desc_orb
            features['orb_coords'] = np.array([k.pt for k in kp_orb], dtype=np.float32)
    
    # SIFT features (if available)
    if _sift_detector is not None:
        try:
            kp_sift, desc_sift = _sift_detector.detectAndCompute(img_gray, None)
            if desc_sift is not None and len(kp_sift) > 0:
                features['sift_kp'] = kp_sift
                features['sift_desc'] = desc_sift
                features['sift_coords'] = np.array([k.pt for k in kp_sift], dtype=np.float32)
        except Exception as e:
            logger.warning(f"SIFT feature extraction failed: {e}")
    
    return features


def assess_image_quality(img: np.ndarray) -> Dict[str, float]:
    """
    Assess image quality metrics that affect detection accuracy.
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # Sharpness (Laplacian variance)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Brightness
    brightness = np.mean(gray)
    
    # Contrast (standard deviation)
    contrast = np.std(gray)
    
    # Noise estimation (using high-frequency components)
    noise = np.std(cv2.GaussianBlur(gray, (5, 5), 0) - gray)
    
    return {
        'sharpness': sharpness,
        'brightness': brightness,
        'contrast': contrast,
        'noise': noise
    }


def identify_currency_by_features(input_img_gray: np.ndarray, reference_features: Dict) -> Tuple[Optional[str], float, Dict]:
    """
    Enhanced currency identification using multiple feature matching algorithms.
    Returns the best match, confidence score, and detailed matching info.
    """
    if not reference_features:
        return None, 0.0, {}
    
    # Extract features from input image using multiple algorithms
    input_features = extract_multi_algorithm_features(input_img_gray)
    
    best_match_id = None
    best_confidence = 0.0
    match_details = {}
    
    for note_id, ref_data in reference_features.items():
        orb_confidence = 0.0
        sift_confidence = 0.0
        
        # ORB matching
        if (input_features['orb_desc'] is not None and 
            ref_data.get('orb_desc') is not None):
            orb_confidence = match_features_orb(
                input_features['orb_desc'], 
                ref_data['orb_desc'],
                input_features['orb_coords'],
                ref_data.get('orb_coords'),
                note_id
            )
        
        # SIFT matching (if available)
        if (input_features['sift_desc'] is not None and 
            ref_data.get('sift_desc') is not None):
            sift_confidence = match_features_sift(
                input_features['sift_desc'],
                ref_data['sift_desc'], 
                input_features['sift_coords'],
                ref_data.get('sift_coords'),
                note_id
            )
        
        # Combined confidence score (weighted average)
        if orb_confidence > 0 and sift_confidence > 0:
            combined_confidence = (orb_confidence * 0.6 + sift_confidence * 0.4)
        elif orb_confidence > 0:
            combined_confidence = orb_confidence * 0.8  # Slight penalty for single algorithm
        elif sift_confidence > 0:
            combined_confidence = sift_confidence * 0.8
        else:
            combined_confidence = 0.0
        
        match_details[note_id] = {
            'orb_confidence': orb_confidence,
            'sift_confidence': sift_confidence,
            'combined_confidence': combined_confidence
        }
        
        logger.info(f"  > {note_id}: ORB={orb_confidence:.3f}, SIFT={sift_confidence:.3f}, Combined={combined_confidence:.3f}")
        
        if combined_confidence > best_confidence:
            best_confidence = combined_confidence
            best_match_id = note_id
    
    return best_match_id, best_confidence, match_details


def match_features_orb(desc_input: np.ndarray, desc_ref: np.ndarray, 
                      coords_input: np.ndarray, coords_ref: np.ndarray, note_id: str) -> float:
    """Match ORB features with geometric verification."""
    try:
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = matcher.knnMatch(desc_input, desc_ref, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        query_idx = []
        train_idx = []
        
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:  # Stricter ratio for better quality
                    good_matches.append(m)
                    query_idx.append(m.queryIdx)
                    train_idx.append(m.trainIdx)
        
        num_good = len(good_matches)
        if num_good < MIN_MATCH_COUNT:
            return 0.0
        
        # Geometric verification with homography
        if coords_input is not None and coords_ref is not None and num_good >= 4:
            src_pts = coords_input[query_idx]
            dst_pts = coords_ref[train_idx]
            
            H, mask = cv2.findHomography(src_pts, dst_pts, 
                                       cv2.RANSAC, 3.0, maxIters=2000)
            if mask is not None:
                inliers = int(mask.sum())
                inlier_ratio = inliers / num_good
                
                # Enhanced confidence calculation
                if inlier_ratio >= GEOMETRIC_VERIFICATION_THRESHOLD:
                    confidence = min(1.0, (inliers / 50.0) * inlier_ratio)
                    return confidence
        
        # Fallback confidence based on match count
        return min(0.5, num_good / 100.0)
        
    except Exception as e:
        logger.warning(f"ORB matching failed for {note_id}: {e}")
        return 0.0


def match_features_sift(desc_input: np.ndarray, desc_ref: np.ndarray,
                       coords_input: np.ndarray, coords_ref: np.ndarray, note_id: str) -> float:
    """Match SIFT features with geometric verification."""
    try:
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        matches = matcher.knnMatch(desc_input, desc_ref, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        query_idx = []
        train_idx = []
        
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.6 * n.distance:  # Stricter for SIFT
                    good_matches.append(m)
                    query_idx.append(m.queryIdx)
                    train_idx.append(m.trainIdx)
        
        num_good = len(good_matches)
        if num_good < MIN_MATCH_COUNT:
            return 0.0
        
        # Geometric verification
        if coords_input is not None and coords_ref is not None and num_good >= 4:
            src_pts = coords_input[query_idx]
            dst_pts = coords_ref[train_idx]
            
            H, mask = cv2.findHomography(src_pts, dst_pts, 
                                       cv2.RANSAC, 2.0, maxIters=2000)
            if mask is not None:
                inliers = int(mask.sum())
                inlier_ratio = inliers / num_good
                
                if inlier_ratio >= GEOMETRIC_VERIFICATION_THRESHOLD:
                    confidence = min(1.0, (inliers / 40.0) * inlier_ratio)
                    return confidence
        
        return min(0.5, num_good / 80.0)
        
    except Exception as e:
        logger.warning(f"SIFT matching failed for {note_id}: {e}")
        return 0.0


def get_roi_for_note(note_id: str) -> Optional[Tuple[float, float, float, float]]:
    """
    Get ROI coordinates for a note, handling variants.
    For variants like 'INR_200_1', falls back to base 'INR_200' ROI.
    """
    # Try exact match first
    if note_id in NOTE_ROIS:
        return NOTE_ROIS[note_id]
    
    # Try base denomination (remove variant suffix)
    parts = note_id.split('_')
    if len(parts) >= 2:
        base_id = f"{parts[0]}_{parts[1]}"  # e.g., "INR_200" from "INR_200_1"
        if base_id in NOTE_ROIS:
            return NOTE_ROIS[base_id]
    
    return None


def verify_denomination_with_ocr(input_img_color: np.ndarray, note_id: str) -> Tuple[Optional[str], float]:
    """
    Enhanced OCR verification with multiple preprocessing techniques and confidence scoring.
    Returns detected value and confidence score.
    """
    if not _tesseract_available:
        return None, 0.0
    
    roi_coords = get_roi_for_note(note_id)
    if roi_coords is None:
        return None, 0.0
    
    try:
        rel_x, rel_y, rel_w, rel_h = roi_coords
        h, w = input_img_color.shape[:2]
        x, y, roi_w, roi_h = int(rel_x * w), int(rel_y * h), int(rel_w * w), int(rel_h * h)
        
        # Extract ROI with padding
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        roi_w = min(w - x, roi_w + 2 * padding)
        roi_h = min(h - y, roi_h + 2 * padding)
        
        roi = input_img_color[y:y+roi_h, x:x+roi_w]
        if roi.size == 0:
            return None, 0.0
        
        # Try multiple OCR preprocessing techniques
        ocr_results = []
        
        # Method 1: Standard grayscale + OTSU
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        result1 = try_ocr_with_preprocessing(roi_gray, "standard", note_id)
        if result1[0]:
            ocr_results.append(result1)
        
        # Method 2: Enhanced contrast + adaptive threshold
        enhanced = cv2.convertScaleAbs(roi_gray, alpha=1.5, beta=10)
        adaptive_thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
        result2 = try_ocr_with_preprocessing(adaptive_thresh, "adaptive", note_id)
        if result2[0]:
            ocr_results.append(result2)
        
        # Method 3: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(roi_gray, cv2.MORPH_CLOSE, kernel)
        _, morph_thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        result3 = try_ocr_with_preprocessing(morph_thresh, "morphological", note_id)
        if result3[0]:
            ocr_results.append(result3)
        
        # Select best result based on confidence
        if ocr_results:
            best_result = max(ocr_results, key=lambda x: x[1])
            logger.info(f"OCR best result for {note_id}: '{best_result[0]}' (confidence: {best_result[1]:.2f})")
            return best_result[0], best_result[1]
        
        return None, 0.0
        
    except Exception as e:
        logger.error(f"Error in OCR verification for {note_id}: {e}")
        return None, 0.0


def try_ocr_with_preprocessing(roi_processed: np.ndarray, method: str, note_id: str) -> Tuple[Optional[str], float]:
    """Try OCR with specific preprocessing method."""
    try:
        # Upscale for better OCR
        scale = 3
        h, w = roi_processed.shape
        roi_resized = cv2.resize(roi_processed, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        
        # Multiple OCR configurations to try
        configs = [
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',  # Single word
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',  # Single text line
            r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789', # Raw line
        ]
        
        best_confidence = 0.0
        best_value = None
        
        for config in configs:
            try:
                # Get OCR result with confidence data
                data = pytesseract.image_to_data(roi_resized, config=config, output_type=pytesseract.Output.DICT)
                
                # Extract text and confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                texts = [text.strip() for text in data['text'] if text.strip()]
                
                if confidences and texts:
                    avg_confidence = np.mean(confidences) / 100.0  # Convert to 0-1 range
                    combined_text = ''.join(texts)
                    
                    # Extract digits
                    digits = re.findall(r'\d+', combined_text)
                    if digits and avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_value = digits[0]
                        
            except Exception as e:
                continue
        
        if best_value and best_confidence > 0.3:  # Minimum confidence threshold
            logger.debug(f"OCR {method} for {note_id}: '{best_value}' (conf: {best_confidence:.2f})")
            return best_value, best_confidence
            
        return None, 0.0
        
    except Exception as e:
        logger.warning(f"OCR preprocessing {method} failed: {e}")
        return None, 0.0


def extract_currency_and_value_from_note_id(note_id: str) -> Tuple[str, str]:
    """
    Extracts currency and value from a note_id string.
    Supports formats like:
    - 'INR_500' -> ('INR', '500')
    - 'INR_200_1' -> ('INR', '200')
    - 'USD_20_old' -> ('USD', '20')
    - 'EUR_50_v2' -> ('EUR', '50')
    """
    parts = note_id.split('_')
    if len(parts) >= 2:
        currency = parts[0]
        denomination = parts[1]
        # Variant info is in parts[2:] but we only need currency and denomination
        return (currency, denomination)
    else:
        return ("Unknown", "0")


def determine_country_from_currency(currency_code: str) -> str:
    """Maps a currency code to a country name."""
    mapping = {
        'INR': 'India',
        'USD': 'United States', 
        'EUR': 'European Union',
        'GBP': 'United Kingdom',
        'CAD': 'Canada',
        'AUD': 'Australia',
        'JPY': 'Japan',
        'CNY': 'China',
        'CHF': 'Switzerland',
        'SEK': 'Sweden'
    }
    return mapping.get(currency_code, 'Unknown')


def analyze_image_authenticity(image_content: bytes) -> Dict[str, str]:
    """
    Enhanced main analysis function with multi-layered validation.
    """
    try:
        # Decode image
        nparr = np.frombuffer(image_content, np.uint8)
        img_color = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_color is None:
            logger.error("Failed to decode image")
            return {"authenticity": "false", "value": "0", "country": "Unknown"}
        
        logger.info(f"Processing image: {img_color.shape}")
        
        # Step 1: Image quality assessment
        quality_metrics = assess_image_quality(img_color)
        logger.info(f"Image quality: sharpness={quality_metrics['sharpness']:.1f}, "
                   f"brightness={quality_metrics['brightness']:.1f}, "
                   f"contrast={quality_metrics['contrast']:.1f}")
        
        # Reject very poor quality images
        if quality_metrics['sharpness'] < 50:
            logger.warning("Image too blurry for reliable analysis")
            return {"authenticity": "false", "value": "0", "country": "Unknown"}
        
        # Step 2: Image enhancement and orientation handling
        img_enhanced = enhance_image_quality(img_color)
        
        # Auto-handle orientation - try multiple orientations
        orientations = [
            ("original", img_enhanced),
            ("rotated_90", cv2.rotate(img_enhanced, cv2.ROTATE_90_COUNTERCLOCKWISE)),
            ("rotated_180", cv2.rotate(img_enhanced, cv2.ROTATE_180)),
            ("rotated_270", cv2.rotate(img_enhanced, cv2.ROTATE_90_CLOCKWISE))
        ]
        
        best_result = None
        best_overall_confidence = 0.0
        
        # Try each orientation
        for orientation_name, img_oriented in orientations:
            logger.info(f"Trying orientation: {orientation_name}")
            
            img_gray = cv2.cvtColor(img_oriented, cv2.COLOR_BGR2GRAY)
            
            # Step 3: Feature Matching
            best_match_note, feature_confidence, match_details = identify_currency_by_features(
                img_gray, _reference_features)
            
            if not best_match_note or feature_confidence < FEATURE_MATCH_CONFIDENCE_THRESHOLD:
                logger.info(f"Feature matching failed for {orientation_name}. "
                           f"Best confidence: {feature_confidence:.3f}")
                continue
            
            logger.info(f"Feature matching result for {orientation_name}: "
                       f"{best_match_note} (confidence: {feature_confidence:.3f})")
            
            currency_code, expected_value = extract_currency_and_value_from_note_id(best_match_note)
            
            # Step 4: OCR Verification
            detected_value, ocr_confidence = verify_denomination_with_ocr(img_oriented, best_match_note)
            
            # Step 5: Combined confidence calculation
            overall_confidence = calculate_overall_confidence(
                feature_confidence, ocr_confidence, detected_value, expected_value)
            
            logger.info(f"Overall confidence for {orientation_name}: {overall_confidence:.3f}")
            
            if overall_confidence > best_overall_confidence:
                best_overall_confidence = overall_confidence
                best_result = {
                    'note_id': best_match_note,
                    'currency_code': currency_code,
                    'expected_value': expected_value,
                    'detected_value': detected_value,
                    'feature_confidence': feature_confidence,
                    'ocr_confidence': ocr_confidence,
                    'overall_confidence': overall_confidence,
                    'orientation': orientation_name
                }
        
        # Step 6: Final decision making
        if best_result is None:
            logger.warning("No valid matches found in any orientation")
            return {"authenticity": "false", "value": "0", "country": "Unknown"}
        
        is_authentic, final_value = make_authenticity_decision(best_result)
        country = determine_country_from_currency(best_result['currency_code'])
        
        logger.info(f"Final result: authentic={is_authentic}, value={final_value}, "
                   f"country={country}, confidence={best_result['overall_confidence']:.3f}")
        
        return {
            "authenticity": str(is_authentic).lower(),
            "value": final_value,
            "country": country
        }
        
    except Exception as e:
        logger.error(f"Critical error in currency analysis: {str(e)}")
        return {"authenticity": "false", "value": "0", "country": "Unknown"}


def calculate_overall_confidence(feature_conf: float, ocr_conf: float, 
                               detected_value: Optional[str], expected_value: str) -> float:
    """Calculate overall confidence score combining feature matching and OCR."""
    if detected_value and detected_value == expected_value:
        # Perfect match - high confidence
        return min(1.0, feature_conf * 0.7 + ocr_conf * 0.3 + 0.2)
    elif detected_value and detected_value != expected_value:
        # OCR mismatch - penalize heavily
        return feature_conf * 0.3
    else:
        # No OCR result - rely on feature matching with penalty
        return feature_conf * 0.8


def make_authenticity_decision(result: Dict) -> Tuple[bool, str]:
    """Make final authenticity decision based on all available evidence."""
    feature_conf = result['feature_confidence']
    ocr_conf = result['ocr_confidence']
    detected_value = result['detected_value']
    expected_value = result['expected_value']
    overall_conf = result['overall_confidence']
    
    # High confidence threshold for authenticity
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    MEDIUM_CONFIDENCE_THRESHOLD = 0.4
    
    if overall_conf >= HIGH_CONFIDENCE_THRESHOLD:
        # High confidence - trust the result
        final_value = detected_value if detected_value else expected_value
        return True, final_value
    elif overall_conf >= MEDIUM_CONFIDENCE_THRESHOLD:
        # Medium confidence - additional checks
        if detected_value and detected_value == expected_value:
            return True, detected_value
        elif feature_conf > 0.6 and not _tesseract_available:
            # No OCR available but good feature match
            return True, expected_value
        else:
            return False, "0"
    else:
        # Low confidence - reject
        return False, "0"

# Initialize features when module is imported
initialize_reference_features()