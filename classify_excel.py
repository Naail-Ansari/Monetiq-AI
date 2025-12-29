import pandas as pd
from train_model import classify_text

# Update this to your actual Excel filename and column name
EXCEL_FILE = 'monetiq_training_dataset_from_bank.csv'  # Change to .xlsx if needed
TEXT_COLUMN = 'ocr_text'  # Change to the actual column name with OCR text
OUTPUT_FILE = 'classified_output.csv'

def main():
    # Read the Excel/CSV file
    df = pd.read_csv(EXCEL_FILE)
    
    # Apply classification to each row in the OCR text column
    df['classification'] = df[TEXT_COLUMN].apply(classify_text)
    
    # Save the results to a new CSV file
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Classification complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
