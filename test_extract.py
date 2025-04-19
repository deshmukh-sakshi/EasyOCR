import easyocr
import time

def main():
    print("Initializing EasyOCR...")
    # Initialize the reader with English language
    reader = easyocr.Reader(['en'])
    
    image_path = r'D:\06_projects\16_EasyOCR\EasyOCR\examples\6.jpg'
    print(f"Reading text from {image_path}...")
    
    start_time = time.time()
    # Perform OCR on the image
    result = reader.readtext(image_path)
    end_time = time.time()
    
    print("\nResults:")
    for detection in result:
        bbox, text, confidence = detection
        print(f"Text: {text}")
        print(f"Confidence: {confidence:.2f}")
        print("-" * 30)
    
    print(f"\nProcessing time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 