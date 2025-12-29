from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import io
import os 
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import httpx
import json
app = FastAPI()

GROQ_API_KEY = "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"

# Define your prompt template
def build_prompt(expenses):
    return f"""
Given the following expense(s), analyze each for:
- tag (Positive/Neutral/Negative)
- is_essential (true/false)
- can_cut (float, how much can be cut)
- note (short advice)

Then, provide a summary with:
- total_spend
- total_savings_found
- verdict (brief advice on overall spending)

Respond ONLY in this JSON format:
{{
  "expenses": [{{ "title": "...", "tag": "...", "is_essential": ..., "can_cut": ..., "note": "..." }}],
  "summary": {{
    "total_spend": ...,
    "total_savings_found": ...,
    "verdict": "..."
  }}
}}

Expenses input (as list of dicts):
{json.dumps(expenses, ensure_ascii=False, indent=2)}
"""

async def call_groq_api(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",  # You can use other models supported by Groq
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        try:
            result = response.json()
        except Exception as e:
            raise Exception(f"Failed to parse JSON from Groq API: {e}\nRaw response: {response.text}")
        # Check for error in response
        if "error" in result:
            raise Exception(f"Groq API error: {result['error']}")
        # Check for expected structure
        if "choices" not in result or not result["choices"]:
            raise Exception(f"Unexpected Groq API response structure: {result}")
        llm_content = result["choices"][0]["message"]["content"]
        return json.loads(llm_content)

# Dummy classifier (replace with your fine-tuned model)
def classify_text(text: str) -> str:
    if "invoice" in text.lower():
        return "Invoice"
    elif "prescription" in text.lower():
        return "Prescription"
    else:
        return "Unknown"

def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text

@app.post("/classify-image/")
async def classify_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    # Step 1: OCR
    extracted_text = extract_text_from_image(image_bytes)
    
    # Step 2: Classify
    classification = classify_text(extracted_text)
    
    # Step 3: Return JSON
    return JSONResponse(content={
        "extracted_text": extracted_text,
        "classification": classification
    })


# @app.post("/analyze-expense/")
# async def analyze_expense(expense: Expense):
#     analysis = analyze_expense_with_llm(expense)
#     return JSONResponse(content=analysis) 


@app.post("/analyze-expenses/")
async def analyze_expenses(request: Request):
    input_data = await request.json()
    # Accept both list and single dict
    expenses = input_data if isinstance(input_data, list) else [input_data]
    try:
        analysis = await call_groq_api(build_prompt(expenses))
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    return JSONResponse(content=analysis)    