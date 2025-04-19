import easyocr
import json
import re
from pathlib import Path
import argparse

def clean_text(text):
    """Clean text by removing special characters and extra spaces"""
    cleaned = ' '.join(text.split())
    return cleaned

def is_valid_name(text):
    """Check if the text could be a valid name"""
    # Skip if contains numbers
    if re.search(r'\d', text):
        return False
        
    # Skip common non-name words
    common_words = {
        'male', 'female', 'address', 'aadhaar', 'birth', 'dob', 'year',
        'government', 'india', 'unique', 'identification', 'authority',
        'पता', 'पुरुष', 'महिला', 'जन्म', 'सरकार', 'भारत',
        'address', 'address:', 'पता:', 'वर्ष', 'year'
    }
    
    words = text.lower().split()
    if any(word in common_words for word in words):
        return False
        
    # Check length (2-4 words is typical for Indian names)
    if not (1 <= len(words) <= 4):
        return False
        
    return True

def extract_aadhaar_data(image_path, debug=True):
    """
    Extract Aadhaar card data from the given image
    
    Args:
        image_path (str): Path to the image file
        debug (bool): Whether to print debug information
    
    Returns:
        dict: Dictionary containing extracted Aadhaar card data
    """
    try:
        # Check if file exists
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Initialize EasyOCR reader for multiple languages
        reader = easyocr.Reader(['en', 'hi', 'mr'])
        
        # Read text
        results = reader.readtext(image_path)
        
        if debug:
            print("\nDetected text blocks:")
            print("-" * 50)
            for i, (bbox, text, prob) in enumerate(results):
                print(f"Block {i+1}: '{text}' (Confidence: {prob:.2f})")
            print("-" * 50)
        
        # Initialize data dictionary
        aadhaar_data = {
            "Name": "",
            "DOB": "",
            "Gender": "",
            "Aadhaar_Number": ""
        }
        
        # Store all text blocks for analysis
        text_blocks = [(bbox, clean_text(text.strip()), prob) for bbox, text, prob in results]
        
        # Find the header text (Government of India)
        header_index = -1
        for i, (bbox, text, prob) in enumerate(text_blocks):
            if "Government of India" in text or "भारत सरकार" in text:
                header_index = i
                break
        
        if header_index != -1:
            # Get the Y-coordinate of the header
            header_y = text_blocks[header_index][0][0][1]  # Y-coordinate of top-left corner
            
            # Look for potential name blocks below the header
            potential_names = []
            for i, (bbox, text, prob) in enumerate(text_blocks):
                # Check if text is below the header and within reasonable distance
                if bbox[0][1] > header_y and bbox[0][1] < header_y + 150:  # Adjust 150 based on image scale
                    if is_valid_name(text):
                        potential_names.append((i, text, prob))
            
            if debug and potential_names:
                print("\nPotential names found:")
                for idx, name, prob in potential_names:
                    print(f"Position {idx}: '{name}' (Confidence: {prob:.2f})")
            
            # Select the name with highest confidence
            if potential_names:
                # Sort by confidence and position (prefer earlier positions)
                potential_names.sort(key=lambda x: (-x[2], x[0]))
                aadhaar_data["Name"] = potential_names[0][1]
                if debug:
                    print(f"\nSelected name: {aadhaar_data['Name']}")
        
        # Process other fields
        for bbox, text, prob in text_blocks:
            text_lower = text.lower()
            
            # Extract DOB (look for date pattern)
            dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
            if dob_match:
                aadhaar_data["DOB"] = dob_match.group()
            
            # Extract Gender (support for multiple languages)
            if any(gender in text_lower for gender in ["female", "स्त्री", "महिला"]):
                aadhaar_data["Gender"] = "Female"
            elif any(gender in text_lower for gender in ["male", "पुरुष", "नर"]):
                aadhaar_data["Gender"] = "Male"
            
            # Extract Aadhaar Number (12-digit number)
            aadhaar_match = re.search(r'\d{4}\s?\d{4}\s?\d{4}', text)
            if aadhaar_match:
                aadhaar_data["Aadhaar_Number"] = aadhaar_match.group().replace(" ", "")
        
        # Final name cleaning
        if aadhaar_data["Name"]:
            # Remove any remaining special characters
            aadhaar_data["Name"] = re.sub(r'[^a-zA-Z\s\u0900-\u097F]', '', aadhaar_data["Name"])
            aadhaar_data["Name"] = ' '.join(aadhaar_data["Name"].split())
        
        return aadhaar_data
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract Aadhaar card data from images')
    parser.add_argument('image_path', type=str, help='Path to the Aadhaar card image')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug output')
    
    args = parser.parse_args()
    
    # Extract Aadhaar data
    aadhaar_data = extract_aadhaar_data(args.image_path, debug=not args.no_debug)
    
    if aadhaar_data:
        print("\nExtracted Data:")
        print("-" * 50)
        print(json.dumps(aadhaar_data, indent=2))
    else:
        print("Failed to extract Aadhaar data")

if __name__ == "__main__":
    main() 