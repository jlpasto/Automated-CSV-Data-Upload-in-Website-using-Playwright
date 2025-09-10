# Use a lightweight base image with Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libcups2 \
    libxkbcommon0 \
    libxcb1 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg-turbo8 \
    libpng16-16 \
    libwebp6 \
    libwebpdemux2 \
    libwebp-dev \
    libwoff1 \
    libharfbuzz0b \
    libvulkan1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their dependencies
RUN playwright install --with-deps

# Copy the rest of the application code
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Command to run your application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]