import easyocr
import json
import re
from pathlib import Path
import argparse

def clean_text(text):
    """Clean text by removing special characters and extra spaces"""
    cleaned = ' '.join(text.split())
    return cleaned

def is_valid_pan(text):
    """Check if text matches PAN card number pattern"""
    # Remove spaces and convert to uppercase
    text = text.replace(" ", "").upper()
    
    # Basic length check (should be 10 characters)
    if len(text) != 10:
        return False
        
    # Check if first 5 are letters, middle 4 are numbers, last is letter
    # More lenient check to handle OCR misreads (like 'I' for '1' or 'O' for '0')
    return bool(re.match(r'^[A-Z0-9]{5}[A-Z0-9]{4}[A-Z0-9]$', text))

def is_valid_date(text):
    """Check if text matches date pattern"""
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    return bool(re.search(date_pattern, text))

def is_header_text(text):
    """Check if text is part of the header"""
    header_texts = [
        "income tax department",
        "govt of india",
        "permanent account number",
        "आयकर विभाग",
        "भारत सरकार"
    ]
    return any(header in text.lower() for header in header_texts)

def extract_pan_data(image_path, debug=True):
    """
    Extract PAN card data from the given image
    
    Args:
        image_path (str): Path to the image file
        debug (bool): Whether to print debug information
    
    Returns:
        dict: Dictionary containing extracted PAN card data
    """
    try:
        # Check if file exists
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Read text
        results = reader.readtext(image_path)
        
        if debug:
            print("\nDetected text blocks:")
            print("-" * 50)
            for i, (bbox, text, prob) in enumerate(results):
                print(f"Block {i+1}: '{text}' (Confidence: {prob:.2f})")
            print("-" * 50)
        
        # Initialize data dictionary
        pan_data = {
            "Name": "",
            "Father_Name": "",
            "DOB": "",
            "PAN_Number": ""
        }
        
        # Store all text blocks for analysis
        text_blocks = [(bbox, clean_text(text.strip()), prob) for bbox, text, prob in results]
        
        # Find header position
        header_index = -1
        for i, (bbox, text, prob) in enumerate(text_blocks):
            if is_header_text(text):
                header_index = i
                break
        
        # Process each text block
        name_found = False
        father_name_found = False
        
        for i, (bbox, text, prob) in enumerate(text_blocks):
            # Skip header texts
            if is_header_text(text):
                continue
                
            # Extract PAN number - look for 10-character string
            if len(text.replace(" ", "")) == 10 and is_valid_pan(text):
                pan_data["PAN_Number"] = text.replace(" ", "").upper()
                continue
                
            # Extract DOB
            if is_valid_date(text):
                pan_data["DOB"] = re.search(r'\d{2}/\d{2}/\d{4}', text).group()
                continue
            
            # Extract name and father's name based on position and content
            if not name_found and header_index != -1 and i > header_index:
                if len(text.split()) >= 2 and prob > 0.2:  # Minimum confidence threshold
                    pan_data["Name"] = text
                    name_found = True
                    continue
            
            # After finding name, next valid text block could be father's name
            if name_found and not father_name_found:
                if len(text.split()) >= 2 and prob > 0.2:  # Minimum confidence threshold
                    pan_data["Father_Name"] = text
                    father_name_found = True
        
        # If PAN number wasn't found with strict validation, try to find a 10-character string
        if not pan_data["PAN_Number"]:
            for _, text, _ in text_blocks:
                text = text.replace(" ", "").upper()
                if len(text) == 10 and re.match(r'^[A-Z0-9]{10}$', text):
                    pan_data["PAN_Number"] = text
                    break
        
        # Format output
        formatted_output = {
            "Name": pan_data["Name"],
            "Father Name": pan_data["Father_Name"],
            "DOB": pan_data["DOB"],
            "PAN Number": pan_data["PAN_Number"]
        }
        
        return formatted_output
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract PAN card data from images')
    parser.add_argument('image_path', type=str, help='Path to the PAN card image')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug output')
    
    args = parser.parse_args()
    
    # Extract PAN data
    pan_data = extract_pan_data(args.image_path, debug=not args.no_debug)
    
    if pan_data:
        print("\nExtracted Data:")
        print("-" * 50)
        for key, value in pan_data.items():
            print(f"{key}: {value}")
    else:
        print("Failed to extract PAN card data")

if __name__ == "__main__":
    main() 