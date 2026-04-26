# Base image
FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Working directory
WORKDIR /app

# Install system dependencies (only if really needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Install Python dependencies
# -------------------------------
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# -------------------------------
# Copy ONLY required project files
# -------------------------------

# App layer
COPY app/ app/

# Graph & nodes
COPY graph/ graph/
COPY nodes/ nodes/
COPY llm/ llm/

# Utils
COPY utils/ utils/

# Frontend (if serving UI)
COPY frontend/ frontend/

# Config (optional)
COPY .env .env

# -------------------------------
# Runtime folders
# -------------------------------
RUN mkdir -p logs exports temp

# -------------------------------
# Expose port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Run app
# -------------------------------
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]