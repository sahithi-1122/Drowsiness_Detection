"""
Test CV Features Integration
"""
from app.services.cv_features import extract_all_cv_features, validate_cv_features
import numpy as np

# Create test image
print("Testing CV Features Integration...")
img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

# Extract features
features = extract_all_cv_features(img)

# Validate
validation = validate_cv_features(features)

print("\n✅ CV Features Test Results:")
print(f"HOG: {features['hog']}")
print(f"Sobel: {features['sobel']}")
print(f"Morphology: {features['morphology']}")
print(f"Optical Flow: {features['optical_flow']}")
print(f"\nValidation: {validation}")

if validation['all_valid']:
    print("\n✅ All CV features are working correctly!")
else:
    print("\n⚠️ Some CV features failed validation")
