import easyocr
import time

def main():
    print("Initializing EasyOCR...")
    reader = easyocr.Reader(['en'])
    
    print("Reading text from image...")
    start_time = time.time()
    result = reader.readtext('D:/06_projects/16_EasyOCR/EasyOCR/examples/6.jpg')
    end_time = time.time()
    
    print("\nRessults:")
    for detection in result:
        bbox, text, confidence = detection
        print(f"Text: {text}")
        print(f"Confidence: {confidence:.2f}")
        print("-" * 30)
    
    print(f"\nProcessing time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 