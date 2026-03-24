FROM python:3.13-alpine

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for psycopg)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libpq-dev

# Set working directory
WORKDIR /app

# Install dependencies (cache optimized)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8001

# Run FastAPI
CMD ["uvicorn", "launch:app", "--host", "0.0.0.0", "--port", "8001"]