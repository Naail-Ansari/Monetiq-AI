from transformers import pipeline

# Create a zero-shot classifier
classifier = pipeline("zero-shot-classification")

def classify_text(text: str) -> str:
    candidate_labels = ["Food", "Groceries", "Other", "Entertainment", "Healthcare"]
    result = classifier(text, candidate_labels)
    return result["labels"][0]  # Best matching label
