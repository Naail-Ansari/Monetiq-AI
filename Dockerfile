FROM python:3.10-slim

# Install OS packages required for OCR
RUN apt-get update && apt-get install -y \
	tesseract-ocr \
	libglib2.0-0 \
	libsm6 \
	libxext6 \
	libxrender-dev \
	&& rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project
COPY . .

# Install Python dependencies with retry and timeout handling
RUN pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

# Expose the FastAPI port
EXPOSE 10000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
